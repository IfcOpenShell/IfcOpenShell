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
# Note that the following categories are not implemented in the BIMServer COBie-Plugins:
# Impact, Coordinate, Issue, Picklist


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
    for element_type in get_types(ifc_file):
        elements.update(ifcopenshell.util.element.get_types(element_type))
    return elements


def get_systems(ifc_file):
    results = []
    components = get_components(ifc_file)
    if ifc_file.schema == "IFC2X3":
        systems = ifc_file.by_type("IfcSystem", include_subtypes=False)
    else:
        systems = ifc_file.by_type("IfcSystem", include_subtypes=False) + ifc_file.by_type("IfcDistributionSystem")
    for system in systems:
        for element in ifcopenshell.util.system.get_system_elements(system):
            if element in components:
                results.append((system, element))
    return results


def get_assemblies(ifc_file):
    results = []
    layer_sets = ifc_file.by_type("IfcMaterialLayerSet")
    layer_sets = []  # This is temporarily overridden because it is unclear exactly how this is stored in Type.
    for layer_set in layer_sets:
        for layer in layer_set.MaterialLayers:
            results.append((None, layer_set, layer.Material))
    rels = ifc_file.by_type("IfcRelAggregates") + ifc_file.by_type("IfcRelNests")
    types = get_types(ifc_file)
    components = get_components(ifc_file)
    for rel in rels:
        if rel.RelatingObject.is_a("IfcSpace"):
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcSpace"):
                    results.append((rel, rel.RelatingObject, related_object))
        elif rel.RelatingObject.is_a("IfcZone"):
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcZone"):
                    results.append((rel, rel.RelatingObject, related_object))
        elif rel.RelatingObject in types:
            for related_object in rel.RelatedObjects:
                if related_object in types:
                    results.append((rel, rel.RelatingObject, related_object))
        elif rel.RelatingObject in components:
            for related_object in rel.RelatedObjects:
                if related_object in components:
                    results.append((rel, rel.RelatingObject, related_object))
        elif rel.RelatingObject.is_a() in ("IfcSystem", "IfcDistributionSystem"):
            for related_object in rel.RelatedObjects:
                if related_object.is_a() in ("IfcSystem", "IfcDistributionSystem"):
                    results.append((rel, rel.RelatingObject, related_object))
    return results


def get_connections(ifc_file):
    return ifc_file.by_type("IfcRelConnectsPorts")


def get_spares(ifc_file):
    return ifc_file.by_type("IfcConstructionProductResource")


def get_resources(ifc_file):
    return ifc_file.by_type("IfcConstructionEquipmentResource")


def get_jobs(ifc_file):
    return ifc_file.by_type("IfcTask")


def get_documents(ifc_file):
    # The original COBie-Plugins assumes a single related object per rel. I think this was wrong.
    results = []
    for rel in ifc_file.by_type("IfcRelAssociatesDocument"):
        doc = rel.RelatingDocument
        if doc.is_a("IfcDocumentInformation"):
            for related_object in rel.RelatedObjects:
                results.append((rel, doc, related_object))
        elif doc.is_a("IfcDocumentReference") and doc.ReferencedDocument:
            for related_object in rel.RelatedObjects:
                results.append((rel, doc.ReferencedDocument, related_object))
    return results


def get_attributes(ifc_file):
    results = []
    history = get_history(ifc_file)
    created_by = get_email_from_history(history) if history else None
    created_on = ifcopenshell.util.date.ifc2datetime(history.CreationDate).isoformat() if history else None
    external_system = history.OwningApplication.ApplicationFullName if history else None
    get_sheets = {
        "Facility": get_facilities,
        "Floor": get_floors,
        "Space": get_spaces,
        "Type": get_types,
        "Component": get_components,
    }

    # COBie-Plugins includes what seems like a whole bunch of arbitrary "at the
    # time it seemed to help" exclusion names. I don't like that strategy. If
    # you've got garbage in your model, clean it out first.

    # fmt: off
    excluded_names = {
        "Manufacturer",
        "ModelNumber", "ArticleNumber", "ModelLabel",
        "WarrantyGuarantorParts", "PointOfContact",
        "WarrantyGuarantorLabor", "PointOfContact",
        "WarrantyDescription", "WarrantyIdentifier",
        "ReplacementCost", "Replacement Cost", "Replacement", "Cost",
        "NominalLength", "OverallLength",
        "NominalWidth", "Width",
        "NominalHeight", "Height",
        "ModelReference", "Reference",
        "Shape",
        "Size",
        "Color", "Colour",
        "Finish",
        "Grade",
        "Material",
        "Constituents", "Parts",
        "Features",
        "AccessibilityPerformance", "Access",
        "CodePerformance", "Regulation",
        "SustainabilityPerformance", "Environmental",
        "SerialNumber", "InstallationDate", "WarrantyStartDate", "TagNumber", "BarCode", "AssetIdentifier"
    }
    # fmt: on

    for sheet_name, get_sheet in get_sheets.items():
        for element in get_sheet(ifc_file):
            for pset_name, props in ifcopenshell.util.element.get_psets(element).items():
                pset = ifc_file.by_id(props["id"])
                pset_created_by = get_created_by(pset) or created_by
                pset_created_on = get_created_on(pset) or created_on
                pset_external_system = get_external_system(element) or external_system
                pset_description = val(pset.Description) or pset_name
                category = get_category(pset)
                for name, value in props.items():
                    if value == "default" or not val(value):
                        continue
                    elif name in excluded_names:
                        continue
                    elif name == "id":
                        continue

                    unit = None
                    if isinstance(value, (int, float)):
                        unit = get_property_unit(props["id"], name)

                    allowed_values = None
                    if isinstance(value, (tuple, list)):
                        allowed_values = get_property_unit(props["id"], name)

                    data = {
                        "key": str(val(name)) + str(sheet_name) + str(val(element.Name)),
                        "Name": val(name),
                        "CreatedBy": pset_created_by,
                        "CreatedOn": pset_created_on,
                        "Category": category,
                        "SheetName": sheet_name,
                        "RowName": val(element.Name),
                        "Value": value,
                        "Unit": unit,
                        "ExternalSystem": pset_external_system,
                        "ExternalObject": pset_name,
                        "ExternalIdentifier": pset.GlobalId,
                        "Description": pset_description,
                        "AllowedValues": allowed_values,
                    }
                    results.append(data)
    return results


def get_contact_data(ifc_file, element):
    email = get_email_from_pao(element)

    history = get_history(ifc_file)

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
        "LinearUnits": get_unit_type_name(ifc_file, "LENGTHUNIT"),
        "AreaUnits": get_unit_type_name(ifc_file, "AREAUNIT"),
        "VolumeUnits": get_unit_type_name(ifc_file, "VOLUMEUNIT"),
        "CurrencyUnit": get_unit_type_name(ifc_file, "IfcMonetaryUnit"),
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
    if element.ObjectType and element.ObjectType.lower() in ("site", "ifcsite"):
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
    for _, props in ifcopenshell.util.element.get_psets(element).items():
        if height is not None:
            break
        for name, value in props.items():
            if name in height_names and val(value):
                height = str(value)
                break

    elevation = getattr(element, "Elevation", "")
    elevation = "" if elevation is None else str(elevation)

    return {
        "key": val(element.Name),
        "Name": val(element.Name),
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "Category": get_category(element),
        "ExternalSystem": get_external_system(element),
        "ExternalObject": external_object,
        "ExternalIdentifier": element.GlobalId,
        "Description": val(element.Description) or val(element.LongName) or val(element.Name),
        "Elevation": val(elevation),
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
    for _, props in ifcopenshell.util.element.get_psets(element).items():
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
    pset_metadata = {}
    pset_mapping = {
        "manufacturer": {"Manufacturer"},
        "model_number": {"ModelNumber", "ArticleNumber", "ModelLabel"},
        "warranty_guarantor_parts": {"WarrantyGuarantorParts", "PointOfContact"},
        "warranty_guarantor_labor": {"WarrantyGuarantorLabor", "PointOfContact"},
        "warranty_description": {"WarrantyDescription", "WarrantyIdentifier"},
        "replacement_cost": {"ReplacementCost", "Replacement Cost", "Replacement", "Cost"},
        "nominal_length": {"NominalLength", "OverallLength", "Length"},
        "nominal_width": {"NominalWidth", "OverallWidth", "Width"},
        # https://github.com/opensourceBIM/COBie-plugins/blob/master/COBiePlugins/lib/IfcToCobieConfig.xml#L104
        "nominal_height": {"NominalHeight", "Height"},  # Original has a typo "Heght"
        "model_reference": {"ModelReference"},
        "shape": {"Shape"},
        "size": {"Size"},
        "color": {"Color", "Colour"},
        "finish": {"Finish"},
        "grade": {"Grade"},
        "material": {"Material"},
        "constituents": {"Constituents", "Parts"},
        "features": {"Features"},
        "accessibility_performance": {"AccessibilityPerformance", "Access"},
        "code_performance": {"CodePerformance", "Regulation"},
        "sustainability_performance": {"SustainabilityPerformance", "Environmental"},
    }
    asset_type = None
    asset_type_names = {"AssetType", "AssetAccountingType"}
    warranty_duration_parts = None
    warranty_duration_parts_names = {"WarrantyDurationParts", "WarrantyPeriod"}
    warranty_duration_labor = None
    warranty_duration_labor_names = {"WarrantyDurationLabor", "WarrantyPeriod"}
    warranty_duration_unit = None
    expected_life = None
    expected_life_names = {"ExpectedLife", "Expected Life", "ServiceLifeDuration", "Expected"}
    duration_unit = None

    for pset_name, props in ifcopenshell.util.element.get_psets(element).items():
        pset_warranty_type = None
        if pset_name == "Pset_Warranty":
            if "parts" in (props.get("WarrantyIdentifier", "") or "").lower():
                pset_warranty_type = "parts"
            elif "labor" in (props.get("WarrantyIdentifier", "") or "").lower():
                pset_warranty_type = "labor"

        pset = ifc_file.by_id(props["id"])

        for name, value in props.items():
            for key, prop_names in pset_mapping.items():
                if not pset_metadata.get(key, None) and name in prop_names and val(value):
                    pset_metadata[key] = str(value)

            if not asset_type and name in asset_type_names and val(value):
                value = value.strip().lower()
                if value in ("moveable", "nonfixed"):
                    asset_type = "Moveable"
                elif value == "fixed":
                    asset_type = "Fixed"
            if not warranty_duration_parts and name in warranty_duration_parts_names and val(value):
                warranty_duration_parts = str(value)
                if not warranty_duration_unit:
                    warranty_duration_unit = get_property_unit(pset, name)
            if not warranty_duration_labor and name in warranty_duration_labor_names and val(value):
                warranty_duration_labor = str(value)
                if not warranty_duration_unit:
                    warranty_duration_unit = get_property_unit(pset, name)
            if not expected_life and name in expected_life_names and val(value):
                expected_life = str(value)
                if not duration_unit:
                    duration_unit = get_property_unit(pset, name)

            if pset_warranty_type == "parts" and val(value):
                if name == "PointOfContact":
                    # https://github.com/buildingSMART/IFC4.3.x-development/issues/698
                    warranty_guarantor_parts = str(value)
                elif name == "WarrantyPeriod":
                    warranty_duration_parts = str(value)
                    unit = get_property_unit(pset, name)
                    warranty_duration_unit = unit or warranty_duration_unit
            elif pset_warranty_type == "labor" and val(value):
                if name == "PointOfContact":
                    # https://github.com/buildingSMART/IFC4.3.x-development/issues/698
                    warranty_guarantor_labor = str(value)
                elif name == "WarrantyPeriod":
                    warranty_duration_labor = str(value)
                    unit = get_property_unit(pset, name)
                    warranty_duration_unit = unit or warranty_duration_unit

    if warranty_duration_parts or warranty_duration_labor:
        if not warranty_duration_unit:
            warranty_duration_unit = get_unit_type_name(ifc_file, "TIMEUNIT")

    if not asset_type and element.is_a("IfcFurnitureType"):
        asset_type = "Moveable"

    return {
        "key": val(element.Name),
        "Name": val(element.Name),
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "Category": get_category(element),
        "Description": val(element.Description) or val(element.Name),
        "AssetType": asset_type,
        "Manufacturer": pset_metadata.get("manufacturer", None),
        "ModelNumber": pset_metadata.get("model_number", None),
        "WarrantyGuarantorParts": pset_metadata.get("warranty_guarantor_parts", None),
        "WarrantyDurationParts": warranty_duration_parts,
        "WarrantyGuarantorLabor": pset_metadata.get("warranty_guarantor_labor", None),
        "WarrantyDurationLabor": warranty_duration_labor,
        "WarrantyDurationUnit": warranty_duration_unit,
        "ExternalSystem": get_external_system(element),
        "ExternalObject": element.is_a(),
        "ExternalIdentifier": element.GlobalId,
        "ReplacementCost": pset_metadata.get("replacement_cost", None),
        "ExpectedLife": expected_life,
        "DurationUnit": duration_unit,
        "WarrantyDescription": pset_metadata.get("warranty_description", None),
        "NominalLength": pset_metadata.get("nominal_length", None),
        "NominalWidth": pset_metadata.get("nominal_width", None),
        "NominalHeight": pset_metadata.get("nominal_height", None),
        "ModelReference": pset_metadata.get("model_reference", None),
        "Shape": pset_metadata.get("shape", None),
        "Size": pset_metadata.get("size", None),
        "Color": pset_metadata.get("color", None),
        "Finish": pset_metadata.get("finish", None),
        "Grade": pset_metadata.get("grade", None),
        "Material": pset_metadata.get("material", None),
        "Constituents": pset_metadata.get("constituents", None),
        "Features": pset_metadata.get("features", None),
        "AccessibilityPerformance": pset_metadata.get("accessibility_performance", None),
        "CodePerformance": pset_metadata.get("code_performance", None),
        "SustainabilityPerformance": pset_metadata.get("sustainability_performance", None),
    }


def get_component_data(ifc_file, element):
    space = ifcopenshell.util.element.get_container(element)
    space_name = space.Name if space.is_a("IfcSpace") else None
    systems = ifcopenshell.util.system.get_element_systems(element)
    system = systems[0].Name if systems else None

    type_name = None
    relating_type = ifcopenshell.util.element.get_type(element)
    if relating_type and val(relating_type.Name):
        type_name = relating_type.Name
    else:
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        type_name = getattr(material, "Name", None) or getattr(material, "LayerSetName", None)

    serial_number = None
    installation_date = None
    warranty_start_date = None
    tag_number = None
    bar_code = None
    asset_identifier = None

    for _, props in ifcopenshell.util.element.get_psets(element).items():
        for name, value in props.items():
            if not serial_number and name == "SerialNumber" and val(value):
                serial_number = str(value)
            if not installation_date and name == "InstallationDate" and val(value):
                installation_date = str(value)
            if not warranty_start_date and name == "WarrantyStartDate" and val(value):
                warranty_start_date = str(value)
            if not tag_number and name == "TagNumber" and val(value):
                tag_number = str(value)
            if not bar_code and name == "BarCode" and val(value):
                bar_code = str(value)
            if not asset_identifier and name == "AssetIdentifier" and val(value):
                asset_identifier = str(value)

    return {
        "key": element.Name,
        "Name": element.Name,
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "TypeName": type_name,
        "Space": space_name,
        "Description": val(element.Description) or val(element.Name),
        "ExternalSystem": get_external_system(element),
        "ExternalObject": element.is_a(),
        "ExternalIdentifier": element.GlobalId,
        "SerialNumber": serial_number,
        "InstallationDate": installation_date,
        "WarrantyStartDate": warranty_start_date,
        "TagNumber": tag_number,
        "BarCode": bar_code,
        "AssetIdentifier": asset_identifier,
    }


def get_system_data(ifc_file, element):
    system, component = element
    category = get_category(system)
    component_name = val(component.Name)
    return {
        "key": str(val(system.Name)) + str(category) + str(component_name),
        "Name": val(system.Name),
        "CreatedBy": get_created_by(system),
        "CreatedOn": get_created_on(system),
        "Category": get_category(system),
        "ComponentNames": component_name,
        "ExternalSystem": get_external_system(system),
        "ExternalObject": system.is_a(),
        "ExternalIdentifier": system.GlobalId,
        "Description": val(system.Description) or val(system.Name),
    }


def get_assembly_data(ifc_file, element):
    rel, relating_object, related_object = element

    if relating_object.is_a("IfcMaterialLayerSet"):
        name = val(relating_object.LayerSetName)
        parent_name = name
        if name:
            name += " assembly"
        assembly_type = "Layer"
        sheet_name = "Type"
        description = val(relating_object.LayerSetName)
    else:
        name = val(relating_object.Name)
        parent_name = name
        assembly_type = "Fixed"
        sheet_name = get_sheet_name(relating_object)
        description = val(rel.Description) or val(rel.Name)

    child_name = val(related_object.Name)
    history = get_history(ifc_file)

    return {
        "key": str(name) + str(sheet_name) + str(parent_name),
        "Name": name,
        "CreatedBy": get_email_from_history(history) if history else None,
        "CreatedOn": ifcopenshell.util.date.ifc2datetime(history.CreationDate).isoformat() if history else None,
        "SheetName": sheet_name,
        "ParentName": parent_name,
        "ChildNames": child_name,
        "AssemblyType": assembly_type,
        "ExternalSystem": history.OwningApplication.ApplicationFullName if history else None,
        "ExternalObject": rel.is_a() if rel else relating_object.is_a(),
        "ExternalIdentifier": rel.GlobalId if rel else None,
        "Description": description,
    }


def get_connection_data(ifc_file, element):
    connection_type = (
        val(element.RelatingPort.ObjectType)
        or val(element.RelatedPort.ObjectType)
        or val(element.Description)
        or val(element.Name)
    )
    name = val(element.Name)
    row_name1 = val(ifcopenshell.util.system.get_port_element(element.RelatingPort).Name)
    row_name2 = val(ifcopenshell.util.system.get_port_element(element.RelatedPort).Name)
    return {
        "key": str(name) + str(connection_type) + str(row_name1) + str(row_name2),
        "Name": name,
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "ConnectionType": connection_type,
        "SheetName": "Component",
        "RowName1": row_name1,
        "RowName2": row_name2,
        "RealizingElement": val(element.RealizingElement.Name) if element.RealizingElement else None,
        "PortName1": val(element.RelatingPort.Name),
        "PortName2": val(element.RelatedPort.Name),
        "ExternalSystem": get_external_system(element),
        "ExternalObject": element.is_a(),
        "ExternalIdentifier": element.GlobalId,
        "Description": val(element.Description) or val(element.Name),
    }


def get_spare_data(ifc_file, element):
    type_name = None
    for rel in element.ResourceOf or []:
        for related_object in rel.RelatedObjects or []:
            if val(related_object.Name):
                type_name = val(related_object.Name)

    suppliers = None
    set_number = None
    part_number = None
    for _, props in ifcopenshell.util.element.get_psets(element).items():
        for name, value in props.items():
            if name == "Suppliers" and val(value):
                suppliers = str(value)
            if name == "SetNumber" and val(value):
                set_number = str(value)
            if name == "PartNumber" and val(value):
                part_number = str(value)

    return {
        "key": val(element),
        "Name": val(element.Name),
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "Category": get_category(element),
        "TypeName": type_name,
        "Suppliers": suppliers,
        "ExternalSystem": get_external_system(element),
        "ExternalObject": element.is_a(),
        "ExternalIdentifier": element.GlobalId,
        "Description": val(element.Description) or val(element.Name),
        "SetNumber": set_number,
        "PartNumber": part_number,
    }


def get_resource_data(ifc_file, element):
    return {
        "key": val(element.Name),
        "Name": val(element.Name),
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "Category": val(element.ObjectType),
        "ExternalSystem": get_external_system(element),
        "ExternalObject": element.is_a(),
        "ExternalIdentifier": element.GlobalId,
        "Description": val(element.Description) or val(element.Name),
    }


def get_job_data(ifc_file, element):
    type_names = []
    resource_names = []
    for rel in element.OperatesOn or []:
        for related_object in rel.RelatedObjects or []:
            if not val(related_object.Name):
                continue
            if related_object.is_a("IfcTypeObject"):
                type_names.append(related_object.Name)
            elif related_object.is_a("IfcConstructionEquipmentResource"):
                resource_names.append(related_object.Name)
    type_name = ",".join(type_names) if type_names else None
    resource_names = ",".join(resource_names) if resource_names else None

    duration = None
    duration_unit = None
    start = None
    task_start_unit = None
    frequency = None
    frequency_unit = None

    for _, props in ifcopenshell.util.element.get_psets(element).items():
        pset = ifc_file.by_id(props["id"])
        for name, value in props.items():
            if not duration and name == "TaskDuration" and val(value):
                duration = str(value)
                if not duration_unit:
                    duration_unit = get_property_unit(pset, name)
            if not start and name == "TaskStartDate" and val(value):
                start = str(value)
                if not task_start_unit:
                    task_start_unit = get_property_unit(pset, name)
            if not frequency and name == "TaskInterval" and val(value):
                frequency = str(value)
                if not frequency_unit:
                    frequency_unit = get_property_unit(pset, name)

    task_number = val(getattr(element, "Id", None)) or val(getattr(element, "Identification", None))

    priors = []
    for rel in element.IsSuccessorFrom or []:
        if rel.RelatedProcess.is_a("IfcTask"):
            prior_task = rel.RelatedProcess
            prior_id = val(getattr(prior_task, "Id", None)) or val(getattr(prior_task, "Identification", None))
            if prior_id:
                priors.append(prior_id)
    priors = ",".join(priors) if priors else task_number

    return {
        "key": str(val(element.Name)) + str(type_name) + str(task_number),
        "Name": val(element.Name),
        "CreatedBy": get_created_by(element),
        "CreatedOn": get_created_on(element),
        "Category": val(element.ObjectType),
        "Status": val(element.Status),
        "TypeName": type_name,
        "Description": val(element.Description) or val(element.Name),
        "Duration": duration,
        "DurationUnit": duration_unit,
        "Start": start,
        "TaskStartUnit": task_start_unit,
        "Frequency": frequency,
        "FrequencyUnit": frequency_unit,
        "ExternalSystem": get_external_system(element),
        "ExternalObject": element.is_a(),
        "ExternalIdentifier": element.GlobalId,
        "TaskNumber": task_number,
        "Priors": priors,
        "ResourceNames": resource_names,
    }


def get_document_data(ifc_file, element):
    rel, doc, related_object = element
    directory = getattr(doc, "Location", None)
    file = None
    if not directory:
        references = getattr(doc, "DocumentReferences", []) or getattr(doc, "HasDocumentReferences", [])
        for reference in references or []:
            if val(reference.Location):
                directory = reference.Location
            identification = getattr(reference, "ItemReference", None) or getattr(reference, "Identification", None)
            if val(reference.Name) and doc.Name != reference.Name:
                file = reference.Name
            elif val(identification):
                file = identification
    name = val(doc.Name)
    stage = val(doc.Scope) or "Requirement"
    sheet_name = get_sheet_name(related_object)
    row_name = val(related_object.Name)
    return {
        "key": str(name) + str(stage) + str(sheet_name) + str(row_name),
        "Name": name,
        "CreatedBy": get_created_by(rel),
        "CreatedOn": get_created_on(rel),
        "Category": val(doc.Purpose),
        "ApprovalBy": val(doc.IntendedUse) or "Information Only",
        "Stage": stage,
        "SheetName": sheet_name,
        "RowName": row_name,
        "Directory": directory,
        "File": file,
        "ExternalSystem": get_external_system(rel),
        "ExternalObject": rel.is_a(),
        "ExternalIdentifier": rel.GlobalId,
        "Description": val(doc.Description),
        "Reference": val(doc.Description) or val(doc.Name),
    }


def get_attribute_data(ifc_file, element):
    return element


def get_unit_type_name(ifc_file, unit_type):
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


def get_unit_name(ifc_file, unit):
    if unit.is_a("IfcNamedUnit"):
        return val(unit.Name)


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
    return "1900-12-31T23:59:59"  # Yes, really


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
    for actor in [element.ThePerson, element.TheOrganization]:
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


def get_property_unit(pset, prop_name):
    for prop in getattr(pset, "HasProperties", []) or []:
        if prop.Name == prop_name:
            unit = getattr(prop, "Unit", None)
            if unit:
                return get_unit_name(unit)


def get_allowed_values(pset_id, prop_name):
    pset = ifc_file.by_id(pset_id)
    for prop in getattr(pset, "HasProperties", []) or []:
        if prop.Name == prop_name:
            if prop.is_a("IfcPropertyEnumeratedValue") and prop.EnumerationValues:
                return ",".join([v.wrappedValue for v in prop.EnumerationValues])


def get_sheet_name(element):
    if element.is_a("IfcBuilding"):
        return "Facility"
    elif element.is_a("IfcBuildingStorey"):
        return "Floor"
    elif element.is_a("IfcSpace"):
        return "Space"
    elif element.is_a("IfcZone"):
        return "Zone"
    elif element.is_a("IfcSystem"):
        return "System"
    elif element.is_a("IfcElementType"):
        return "Type"
    elif element.is_a("IfcElement"):
        return "Component"
    elif element.is_a("IfcTask"):
        return "Job"
    elif element.is_a("IfcConstructionProductResource"):
        return "Spare"
    elif element.is_a("IfcConstructionEquipmentResource"):
        return "Resource"


config = {
    "colours": {
        "h": "c0c0c0",  # Header data
        "r": "ffff99",  # Required
        "i": "ffcc99",  # Internal reference
        "e": "cc99ff",  # External reference
        "o": "ccffcc",  # Optionally specified
        "s": "c0c0c0",  # Secondary product data
        "b": "99ccff",  # Bespoke data
        "x": "000000",  # Not in scope
    },
    "null": "n/a",
    "empty": "n/a",
    "bool_true": "Yes",
    "bool_false": "No",
    "categories": {
        "Contact": {
            "keys": ["Email"],
            "headers": [
                "Email",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "Company",
                "Phone",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Department",
                "OrganizationCode",
                "GivenName",
                "FamilyName",
                "Street",
                "PostalBox",
                "Town",
                "StateRegion",
                "PostalCode",
                "Country",
            ],
            "colours": "rrrrrreeeoooooooooo",
            "sort": [{"name": "Email", "order": "ASC"}],
            "get_category_elements": get_contacts,
            "get_element_data": get_contact_data,
        },
        "Facility": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "ProjectName",
                "SiteName",
                "LinearUnits",
                "AreaUnits",
                "VolumeUnits",
                "CurrencyUnit",
                "AreaMeasurement",
                "ExternalSystem",
                "ExternalProjectObject",
                "ExternalProjectIdentifier",
                "ExternalSiteObject",
                "ExternalSiteIdentifier",
                "ExternalFacilityObject",
                "ExternalFacilityIdentifier",
                "Description",
                "ProjectDescription",
                "SiteDescription",
                "Phase",
            ],
            "colours": "ririrriiiireeeeeeeoooo",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_facilities,
            "get_element_data": get_facility_data,
        },
        "Floor": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Description",
                "Elevation",
                "Height",
            ],
            "colours": "ririeeeooo",
            "sort": [{"name": "Elevation", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
            "get_category_elements": get_floors,
            "get_element_data": get_floor_data,
        },
        "Space": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "FloorName",
                "Description",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "RoomTag",
                "UsableHeight",
                "GrossArea",
                "NetArea",
            ],
            "colours": "ririrreeeoooo",
            "sort": [{"name": "FloorName", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
            "get_category_elements": get_spaces,
            "get_element_data": get_space_data,
        },
        "Zone": {
            "keys": ["Name", "Category", "SpaceNames"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "SpaceNames",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Description",
            ],
            "colours": "ririreeeo",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_zones,
            "get_element_data": get_zone_data,
        },
        "Type": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "Description",
                "AssetType",
                "Manufacturer",
                "ModelNumber",
                "WarrantyGuarantorParts",
                "WarrantyDurationParts",
                "WarrantyGuarantorLabor",
                "WarrantyDurationLabor",
                "WarrantyDurationUnit",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "ReplacementCost",
                "ExpectedLife",
                "DurationUnit",
                "WarrantyDescription",
                "NominalLength",
                "NominalWidth",
                "NominalHeight",
                "ModelReference",
                "Shape",
                "Size",
                "Color",
                "Finish",
                "Grade",
                "Material",
                "Constituents",
                "Features",
                "AccessibilityPerformance",
                "CodePerformance",
                "SustainabilityPerformance",
            ],
            "colours": "riririiriririeeeooiorrroooooooooooo",
            "sort": [{"name": "ExternalObject", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
            "get_category_elements": get_types,
            "get_element_data": get_type_data,
        },
        "Component": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "TypeName",
                "Space",
                "Description",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "SerialNumber",
                "InstallationDate",
                "WarrantyStartDate",
                "TagNumber",
                "BarCode",
                "AssetIdentifier",
            ],
            "colours": "ririireeeoooooo",
            "sort": [
                {"name": "ExternalObject", "order": "ASC"},
                {"name": "TypeName", "order": "ASC"},
                {"name": "Name", "order": "ASC"},
            ],
            "get_category_elements": get_components,
            "get_element_data": get_component_data,
        },
        "System": {
            "keys": ["Name", "Category", "ComponentNames"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "ComponentNames",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Description",
            ],
            "colours": "ririieeeo",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_systems,
            "get_element_data": get_system_data,
        },
        "Assembly": {  # Note that this is technically "not required"
            "keys": ["Name", "SheetName", "ParentName"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "SheetName",
                "ParentName",
                "ChildNames",
                "AssemblyType",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Description",
            ],
            "colours": "ririiiieeeo",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_assemblies,
            "get_element_data": get_assembly_data,
        },
        "Connection": {  # Note that this is technically "not required"
            "keys": ["Name", "ConnectionType", "RowName1", "RowName2"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "ConnectionType",
                "SheetName",
                "RowName1",
                "RowName2",
                "RealizingElement",
                "PortName1",
                "PortName2",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Description",
            ],
            "colours": "ririiiiiiieeeo",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_connections,
            "get_element_data": get_connection_data,
        },
        "Spare": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "TypeName",
                "Suppliers",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Description",
                "SetNumber",
                "PartNumber",
            ],
            "colours": "ririiieeeooo",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_spares,
            "get_element_data": get_spare_data,
        },
        "Resource": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Description",
            ],
            "colours": "ririeeeo",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_resources,
            "get_element_data": get_resource_data,
        },
        "Job": {
            "keys": ["Name", "TypeName", "TaskNumber"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "Status",
                "TypeName",
                "Description",
                "Duration",
                "DurationUnit",
                "Start",
                "TaskStartUnit",
                "Frequency",
                "FrequencyUnit",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "TaskNumber",
                "Priors",
                "ResourceNames",
            ],
            "colours": "ririiirriririeeeoii",
            "sort": [{"name": "TypeName", "order": "ASC"}, {"name": "TaskNumber", "order": "ASC"}],
            "get_category_elements": get_jobs,
            "get_element_data": get_job_data,
        },
        "Document": {
            "keys": ["Name", "Stage", "SheetName", "RowName"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "ApprovalBy",
                "Stage",
                "SheetName",
                "RowName",
                "Directory",
                "File",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Description",
                "Reference",
            ],
            "colours": "ririiiiirreeeoo",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_documents,
            "get_element_data": get_document_data,
        },
        "Attribute": {
            "keys": ["Name", "SheetName", "RowName"],
            "headers": [
                "Name",
                "CreatedBy",
                "CreatedOn",
                "Category",
                "SheetName",
                "RowName",
                "Value",
                "Unit",
                "ExternalSystem",
                "ExternalObject",
                "ExternalIdentifier",
                "Description",
                "AllowedValues",
            ],
            "colours": "ririiirreeeoo",
            "sort": [{"name": "Category", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
            "get_category_elements": get_attributes,
            "get_element_data": get_attribute_data,
        },
    },
}
