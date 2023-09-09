# IfcFM - IFC for facility management
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcFM.
#
# IfcFM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcFM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcFM.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.fm
import ifcopenshell.util.date
import ifcopenshell.util.system
import ifcopenshell.util.placement
import ifcopenshell.util.classification


# The original BIMServer plugin has a function called ifcToCOBie:
# https://github.com/opensourceBIM/COBie-plugins/blob/master/COBieShared/src/org/bimserver/cobie/shared/serialization/COBieTabSerializer.java#L54
# This calls various serialisers here:
# https://github.com/opensourceBIM/COBie-plugins/tree/master/COBieShared/src/org/bimserver/cobie/shared/serialization/util
# Some settings are also defined here:
# https://github.com/opensourceBIM/COBie-plugins/blob/master/COBiePlugins/lib/IfcToCobieConfig.xml


def get_contacts(ifc_file):
    return ifc_file.by_type("IfcPersonAndOrganization")


def get_facilities(ifc_file):
    return ifc_file.by_type("IfcBuilding")


def get_floors(ifc_file):
    return [
        e
        for e in ifc_file.by_type("IfcBuildingStorey")
        if ifcopenshell.util.element.get_aggregate(e).is_a("IfcBuilding")
    ]


def get_spaces(ifc_file):
    return ifc_file.by_type("IfcSpace")


def get_zones(ifc_file):
    results = []
    zones = ifc_file.by_type("IfcZone")
    for zone in zones or []:
        has_space = False
        for rel in zone.IsGroupedBy:
            items = [(zone, space) for space in rel.RelatedObjects if space.is_a("IfcSpace") and val(space.Name)]
            if items:
                results.extend(items)
                has_space = True
        if not has_space:
            results.append((zone, None))
    if zones:
        return results

    zone_spaces = {}
    for space in ifc_file.by_type("IfcSpace"):
        for _, props in ifcopenshell.util.element.get_psets(space).items():
            for name, value in props.items():
                if "ZoneName" in name:
                    zone_name = val(value)
                    space_name = val(space.Name)
                    category = name
                    zone_key = str(name) + "," + str(category)
                    zone_spaces.setdefault(zone_key, [])
                    if space_name not in zone_spaces[zone_key]:
                        zone_spaces[zone_key].append(space_name)
                        results.append(((zone_name, category), space_name))
    return results


def get_types(ifc_file):
    return ifcopenshell.util.fm.get_cobie_types(ifc_file)


def get_components(ifc_file):
    elements = set()
    for element_type in ifcopenshell.util.fm.get_cobie_types(ifc_file):
        elements.update(ifcopenshell.util.element.get_types(element_type))
    return elements


def get_systems(ifc_file):
    return ifc_file.by_type("IfcSystem")


def get_contact_data(ifc_file, element):
    email = get_email_from_pao(element)

    history = get_history(ifc_file)
    created_by = None
    created_on = None

    roles = []
    for actor in [element, element.ThePerson, element.TheOrganization]:
        for role in actor.Roles or []:
            if role.Role == "USERDEFINED":
                if role.UserDefinedRole:
                    roles.append(role.UserDefinedRole)
            else:
                roles.append(role.Role)

    organization = element.TheOrganization
    person = element.ThePerson

    department = get_pao_address(element, "InternalLocation")
    if not department:
        for rel in organization.Relates:
            for org in rel.RelatedOrganizations:
                if val(org.Name):
                    department = org.Name

    return {
        "key": email,
        "Email": email,
        "CreatedBy": get_email_from_history(history) if history else None,
        "CreatedOn": ifcopenshell.util.date.ifc2datetime(history.CreationDate).isoformat() if history else None,
        "Category": ",".join(roles),
        "Company": getattr(organization, "Name", None),
        "Phone": get_pao_address(element, "TelephoneNumbers"),
        "ExternalSystem": history.OwningApplication.ApplicationFullName if history else None,
        "ExternalObject": element.is_a(),
        "ExternalIdentifier": email,
        "Department": department,
        "OrganizationCode": getattr(organization, "Id", getattr(organization, "Identification", None))
        or organization.Name,
        "GivenName": getattr(person, "GivenName", None),
        "FamilyName": getattr(person, "FamilyName", None),
        "Street": get_pao_address(element, "AddressLines"),
        "PostalBox": get_pao_address(element, "PostalBox"),
        "Town": get_pao_address(element, "Town"),
        "StateRegion": get_pao_address(element, "Region"),
        "PostalCode": get_pao_address(element, "PostalCode"),
        "Country": get_pao_address(element, "Country"),
    }


def get_facility_data(ifc_file, element):
    site = get_facility_parent(element, "IfcSite")
    site_name = None
    site_description = None
    if site:
        site_name = val(site.Name) or val(site.LongName) or site.GlobalId
        site_description = val(site.Description) or val(site.LongName) or val(site.Name)

    project = None
    project_name = None
    project_description = None
    try:
        project = ifc_file.by_type("IfcProject")[0]
        project_name = val(project.Name) or val(project.LongName) or project.GlobalId
        project_description = val(project.Description) or val(project.LongName) or val(project.Name)
    except:
        pass

    name = val(element.Name) or val(element.LongName)
    if not name:
        name = val(project.Name) or val(project.LongName)
    if not name and site:
        name = val(site.Name) or val(site.LongName)

    return {
        "key": name,
        "Name": name,
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "Category": get_category(element),
        "ProjectName": project_name,
        "SiteName": site_name,
        "LinearUnits": get_unit_name(ifc_file, "LENGTHUNIT"),
        "AreaUnits": get_unit_name(ifc_file, "AREAUNIT"),
        "VolumeUnits": get_unit_name(ifc_file, "VOLUMEUNIT"),
        "CurrencyUnit": get_unit_name(ifc_file, "IfcMonetaryUnit"),
        "AreaMeasurement": get_area_measurement(element),
        "ExternalSystem": get_external_system(element),
        "ExternalProjectObject": "IfcProject",
        "ExternalProjectIdentifier": project.GlobalId if project else ifcopenshell.guid.new(),
        "ExternalSiteObject": "IfcSite",
        "ExternalSiteIdentifier": site.GlobalId if site else ifcopenshell.guid.new(),
        "ExternalFacilityObject": "IfcBuilding",
        "ExternalFacilityIdentifier": element.GlobalId,
        "Description": val(element.Description) or val(element.LongName) or val(element.Name),
        "ProjectDescription": project_description,
        "SiteDescription": site_description,
        "Phase": val(project.Phase) if project else None,
    }


def get_floor_data(ifc_file, element):
    external_object = element.is_a()
    if external_object.ObjectType and external_object.ObjectType.lower() in ("site", "ifcsite"):
        external_object = "IfcSite"

    height_names = {
        "Height",
        "NetHeight",
        "GrossHeight",
        "Net Height",
        "Gross Height",
        "StoreyHeight",
        "Storey Height",
        "FloorHeight",
        "Floor Height",
    }

    height = None
    for _, props in ifcopenshell.util.element.get_psets(element):
        if height is not None:
            break
        for name, value in props.items():
            if name in height_names and val(value):
                height = str(value)
                break

    return {
        "key": var(element.Name),
        "Name": var(element.Name),
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "Category": get_category(element),
        "ExternalSystem": get_external_system(element),
        "ExternalObject": external_object,
        "ExternalIdentifier": element.GlobalId,
        "Description": val(element.Description) or val(element.LongName) or val(element.Name),
        "Elevation": val(str(getattr(element, "Elevation", ""))),
        "Height": height,
    }


def get_space_data(ifc_file, element):
    floor_name = None
    floor = ifcopenshell.util.element.get_aggregate(element)
    if floor and floor.is_a("IfcBuildingStorey"):
        floor_name = val(floor.Name)

    room_tag = None
    room_tag_names = {"RoomTag", "Tag", "Room Tag"}
    usable_height = None
    usable_height_names = {"FinishCeilingHeight", "Height", "UsableHeight"}
    gross_area = None
    gross_area_names = {"GrossFloorArea", "GSA"}
    net_area = None
    net_area_names = {"NetFloorArea", "GSA"}
    for _, props in ifcopenshell.util.element.get_psets(element):
        for name, value in props.items():
            if not room_tag and name in room_tag_names and val(value):
                room_tag = str(value)
            if not usable_height and name in usable_height_names and val(value):
                usable_height = str(value)
            if not gross_area and name in gross_area_names and val(value):
                gross_area = str(value)
            if not net_area and name in net_area_names and val(value):
                net_area = str(value)

    return {
        "key": val(element.Name),
        "Name": val(element.Name),
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "Category": get_category(element),
        "FloorName": floor_name,
        "Description": val(element.Description) or val(element.LongName) or val(element.Name),
        "ExternalSystem": get_external_system(element),
        "ExternalObject": element.is_a(),
        "ExternalIdentifier": element.GlobalId,
        "RoomTag": room_tag,
        "UsableHeight": usable_height,
        "GrossArea": gross_area,
        "NetArea": net_area,
    }


def get_zone_data(ifc_file, element):
    zone, space = element

    if isinstance(zone, tuple):
        name, category = zone
        history = get_history(ifc_file)
        return {
            "key": "-".join([str(name), str(category), str(space)]),
            "Name": name,
            "CreatedBy": get_email_from_history(history) if history else None,
            "CreatedOn": ifcopenshell.util.date.ifc2datetime(history.CreationDate).isoformat() if history else None,
            "Category": category,
            "SpaceNames": space,
            "ExternalSystem": history.OwningApplication.ApplicationFullName if history else None,
            "ExternalObject": "IfcPropertySingleValue",
            "ExternalIdentifier": None,
            "Description": val(name) or val(category),
        }

    name = zone.Name
    parent = ifcopenshell.util.element.get_aggregate(zone)
    if parent and val(parent.Name):
        name = parent.Name + "-" + name

    category = get_category(zone)
    space_name = val(space.Name) if space else None

    return {
        "key": "-".join([str(name), str(category), str(space_name)]),
        "Name": name,
        "CreatedBy": get_created_by(zone),
        "CreatedOn": get_created_on(zone),
        "Category": category,
        "SpaceNames": space_name,
        "ExternalSystem": get_external_system(zone),
        "ExternalObject": zone.is_a(),
        "ExternalIdentifier": zone.GlobalId,
        "Description": val(zone.Description) or zone.Name,
    }


def get_type_data(ifc_file, element):
    return {
        "key": element.Name,
        "Name": element.Name,
        "Description": element.Description,
        "Category": get_classification(element),
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "ModelSoftware": get_external_system(element),
        "ModelObject": "{}[{}]".format(element.is_a(), ifcopenshell.util.element.get_predefined_type(element)),
        "ModelTag": element.Tag,
        "ModelID": element.GlobalId,
    }


def get_element_data(ifc_file, element):
    space = ifcopenshell.util.element.get_container(element)
    space_name = space.Name if space.is_a("IfcSpace") else None
    systems = ifcopenshell.util.system.get_element_systems(element)
    system = systems[0].Name if systems else None
    return {
        "key": element.Name,
        "Name": element.Name,
        "TypeName": ifcopenshell.util.element.get_type(element).Name,
        "SpaceName": space_name,
        "SystemName": system,
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "ModelSoftware": get_external_system(element),
        "ModelObject": "{}[{}]".format(element.is_a(), ifcopenshell.util.element.get_predefined_type(element)),
        "ModelID": element.GlobalId,
    }


def get_system_data(ifc_file, element):
    return {
        "key": element.Name,
        "Name": element.Name,
        "Description": element.Description,
        "Category": get_classification(element),
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "ModelSoftware": get_external_system(element),
        "ModelID": element.GlobalId,
    }


def get_unit_name(ifc_file, unit_type):
    for unit in ifc_file.by_type("IfcUnitAssignment")[0].Units:
        if unit.is_a("IfcNamedUnit") and unit.UnitType == unit_type:
            if unit.is_a("IfcSIUnit"):
                prefix = (unit.Prefix or "").lower()
                if unit_type == "LENGTHUNIT":
                    return f"{prefix}meters"
                elif unit_type == "AREAUNIT":
                    return f"square {prefix}meters"
                elif unit_type == "VOLUMEUNIT":
                    return f"cubic {prefix}meters"
            else:
                return val(unit.Name)
        elif unit.is_a("IfcMonetaryUnit") and unit_type == "IfcMonetaryUnit":
            return val(unit.Currency)


def get_created_by(element):
    if getattr(element, "OwnerHistory", None):
        return get_email_from_history(element.OwnerHistory)


def get_email_from_history(element):
    pao = element.OwningUser
    if pao.is_a("IfcPersonAndOrganization"):
        return get_email_from_pao(pao)


def get_email_from_pao(pao):
    for address in pao.ThePerson.Addresses or []:
        if address.is_a("IfcTelecomAddress") and address.ElectronicMailAddresses:
            return address.ElectronicMailAddresses[0]

    for address in pao.TheOrganization.Addresses or []:
        if address.is_a("IfcTelecomAddress") and address.ElectronicMailAddresses:
            return address.ElectronicMailAddresses[0]

    person_id = getattr(pao.ThePerson, "Identification", getattr(pao.ThePerson, "Id", None))
    if person_id:
        return person_id

    organization_id = getattr(pao.TheOrganization, "Identification", getattr(pao.TheOrganization, "Id", None))
    if organization_id:
        return organization_id

    if pao.ThePerson.GivenName and pao.ThePerson.FamilyName and pao.TheOrganization.Name:
        return pao.ThePerson.GivenName + pao.ThePerson.FamilyName + "@" + pao.TheOrganization.Name + ".com"


def get_owner_name(element):
    if getattr(element, "OwnerHistory", None):
        return element.OwnerHistory.OwningUser.TheOrganization.Name


def get_created_on(element):
    if getattr(element, "OwnerHistory", None):
        return ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat()


def get_external_system(element):
    if getattr(element, "OwnerHistory", None):
        return val(element.OwnerHistory.OwningApplication.ApplicationFullName)


def get_facility_parent(element, ifc_class):
    parent = ifcopenshell.util.element.get_aggregate(element)
    while parent:
        if parent.is_a(ifc_class):
            return parent
        if parent.is_a("IfcProject"):
            return
        parent = ifcopenshell.util.element.get_aggregate(parent)


def val(x):
    return x if x not in ("", "n/a") else None


def get_area_measurement(element):
    for relationship in getattr(element, "IsDefinedBy", []) or []:
        if relationship.is_a("IfcRelDefinesByProperties"):
            definition = relationship.RelatingPropertyDefinition
            if definition.is_a("IfcElementQuantity") and val(definition.MethodOfMeasurement):
                return definition.MethodOfMeasurement
    for rel in getattr(element, "IsDecomposedBy", []):
        for related_object in rel.RelatedObjects:
            result = get_area_measurement(related_object)
            if result:
                return result


def get_category(element):
    references = list(ifcopenshell.util.classification.get_references(element))
    results = []
    for reference in references:
        if reference.is_a("IfcClassification"):
            results.append(reference.Name)
        elif reference.is_a("IfcClassificationReference"):
            identification = val(getattr(reference, "Identification", getattr(reference, "ItemReference", None)))
            if val(reference.Name) and identification and val(reference.Name) != identification:
                results.append(identification + " : " + val(reference.Name))
            elif val(reference.Name):
                results.append(reference.Name)
            elif identification:
                results.append(identification)
            elif reference.ReferencedSource and val(reference.ReferencedSource.Name):
                results.append(reference.ReferencedSource.Name)
            elif val(reference.Location):
                results.append(reference.Location)
    if results:
        return ",".join(results)

    category_props = [
        ("Assembly Code", "Assembly Description"),
        ("Category Code", "Category Description"),
        ("Classification Code", "Classification Description"),
        ("OmniClass Number", "OmniClass Title"),
        ("Uniclass Code", "Uniclass Description"),
    ]

    psets = ifcopenshell.util.element.get_psets(element)
    properties = {}
    if psets:
        for _, props in psets.items():
            properties.update(props)

    for code, description in category_props:
        code = val(properties.get(code, None))
        if code:
            description = val(properties.get(description, None))
            if code and description:
                results.append(code + " : " + description)
            else:
                results.append(code)
    if results:
        return ",".join(results)

    return val(getattr(element, "ObjectType", None))


def get_pao_address(element, name):
    for actor in [element.TheActor.ThePerson, element.TheActor.TheOrganization]:
        for address in actor.Addresses or []:
            if hasattr(address, name) and getattr(address, name, None):
                result = getattr(address, name)
                if isinstance(result, tuple):
                    if name == "AddressLines":
                        return " ".join(result)
                    return result[0]
                return result


def get_property(psets, pset_name, prop_name, decimals=None):
    if pset_name in psets:
        result = psets[pset_name].get(prop_name, None)
        if decimals is None or result is None:
            return result
        return round(result, decimals)


def get_history(ifc_file):
    histories = ifc_file.by_type("IfcOwnerHistory")
    if histories:
        return sorted(histories, key=lambda x: x.id())[-1]


get_category_elements = {
    "Contact": get_contacts,
    "Facility": get_facilities,
    "Floor": get_floors,
    "Space": get_spaces,
    "Zone": get_zones,
    "Type": get_types,
    "Component": get_components,
    "System": get_systems,
}

get_element_data = {
    "Contact": get_contact_data,
    "Facility": get_facility_data,
    "Floor": get_floor_data,
    "Space": get_space_data,
    "Zone": get_zone_data,
    "Type": get_type_data,
    "Component": get_component_data,
    "System": get_system_data,
}

config = {
    "Actors": {
        "headers": [
            "Name",
            "Category",
            "Email",
            "Phone",
            "CompanyURL",
            "Department",
            "Address1",
            "Address2",
            "StateRegion",
            "PostalCode",
            "Country",
        ],
        "colours": "ppssssssss",
        "sort": [{"name": "Name", "order": "ASC"}],
    },
    "Facilities": {
        "headers": [
            "Name",
            "ProjectName",
            "SiteName",
            "Category",
            "AuthorOrganizationName",
            "AuthorDate",
            "ModelSoftware",
            "ModelProjectID",
            "ModelSiteID",
            "ModelBuildingID",
            "LinearUnits",
            "AreaUnits",
            "AreaMeasurement",
            "Phase",
        ],
        "colours": "ppppreeeeessss",
        "sort": [{"name": "Name", "order": "ASC"}],
    },
    "Storeys": {
        "headers": [
            "Name",
            "Category",
            "AuthorOrganizationName",
            "AuthorDate",
            "ModelSoftware",
            "ModelObject",
            "ModelID",
            "Elevation",
        ],
        "colours": "ppreeees",
        "sort": [{"name": "Elevation", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
    },
    "Spaces": {
        "headers": [
            "Name",
            "Description",
            "Category",
            "LevelName",
            "AuthorOrganizationName",
            "AuthorDate",
            "ModelSoftware",
            "ModelID",
            "AreaGross",
            "AreaNet",
        ],
        "colours": "ppprreeess",
        "sort": [{"name": "LevelName", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
    },
    "Zones": {
        "headers": ["Name", "SpaceName", "AuthorOrganizationName", "AuthorDate", "ModelSoftware", "ModelID"],
        "colours": "prreee",
        "sort": [{"name": "Name", "order": "ASC"}],
    },
    "Types": {
        "headers": [
            "Name",
            "Description",
            "Category",
            "AuthorOrganizationName",
            "AuthorDate",
            "ModelSoftware",
            "ModelObject",
            "ModelTag",
            "ModelID",
        ],
        "colours": "pppreeeee",
        "sort": [{"name": "ModelObject", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
    },
    "Elements": {
        "headers": [
            "Name",
            "TypeName",
            "SpaceName",
            "SystemName",
            "AuthorOrganizationName",
            "AuthorDate",
            "ModelSoftware",
            "ModelObject",
            "ModelID",
        ],
        "colours": "prrrreeee",
        "sort": [{"name": "TypeName", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
    },
    "Systems": {
        "headers": [
            "Name",
            "Description",
            "Category",
            "AuthorOrganizationName",
            "AuthorDate",
            "ModelSoftware",
            "ModelID",
        ],
        "colours": "pppreee",
        "sort": [{"name": "Name", "order": "ASC"}],
    },
}
