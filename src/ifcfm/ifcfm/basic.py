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


def get_actors(ifc_file):
    return ifc_file.by_type("IfcActor")


def get_facilities(ifc_file):
    return ifc_file.by_type("IfcBuilding")


def get_storeys(ifc_file):
    return ifc_file.by_type("IfcBuildingStorey")


def get_spaces(ifc_file):
    return ifc_file.by_type("IfcSpace")


def get_zones(ifc_file):
    zones = []
    for zone in ifc_file.by_type("IfcZone"):
        for rel in zone.IsGroupedBy:
            zones.extend([(zone, space) for space in rel.RelatedObjects])
    return zones


def get_types(ifc_file):
    return ifcopenshell.util.fm.get_fmhem_types(ifc_file)


def get_elements(ifc_file):
    elements = set()
    for element_type in ifcopenshell.util.fm.get_fmhem_types(ifc_file):
        elements.update(ifcopenshell.util.element.get_types(element_type))
    return elements


def get_systems(ifc_file):
    return ifc_file.by_type("IfcSystem")


def get_actor_data(ifc_file, element):
    return {
        "key": element.TheActor.Name,
        "Name": element.TheActor.Name,
        "Category": get_classification(element),
        "Email": get_actor_address(element, "ElectronicMailAddresses"),
        "Phone": get_actor_address(element, "TelephoneNumbers"),
        "CompanyURL": get_actor_address(element, "WWWHomePageURL"),
        "Department": get_actor_address(element, "InternalLocation"),
        "Address": get_actor_address(element, "AddressLines"),
        "Town": get_actor_address(element, "Town"),
        "Region": get_actor_address(element, "Region"),
        "PostalCode": get_actor_address(element, "PostalCode"),
        "Country": get_actor_address(element, "Country"),
    }


def get_facility_data(ifc_file, element):
    return {
        "key": element.Name,
        "Name": element.Name,
        "ProjectName": ifc_file.by_type("IfcProject")[0].Name,
        "SiteName": getattr(get_facility_parent(element, "IfcSite"), "Name", None),
        "Category": get_classification(element),
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
        "ModelProjectID": ifc_file.by_type("IfcProject")[0].GlobalId,
        "ModelSiteID": getattr(get_facility_parent(element, "IfcSite"), "GlobalId", None),
        "ModelBuildingID": element.GlobalId,
        "LinearUnits": "millimeters",
        "AreaUnits": "square meters",
        "AreaMeasurement": "BIM Software",
        "Phase": ifc_file.by_type("IfcProject")[0].Phase,
    }


def get_storey_data(ifc_file, element):
    return {
        "key": element.Name,
        "Name": element.Name,
        "Category": "Level",
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
        "ModelObject": element.is_a(),
        "ModelID": element.GlobalId,
        "Elevation": ifcopenshell.util.placement.get_storey_elevation(element),
    }


def get_space_data(ifc_file, element):
    psets = ifcopenshell.util.element.get_psets(element)
    return {
        "key": element.Name,
        "Name": element.Name,
        "Description": element.LongName,
        "Category": get_classification(element),
        "LevelName": getattr(get_facility_parent(element, "IfcBuildingStorey"), "Name", None),
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
        "ModelID": element.GlobalId,
        "AreaGross": get_property(psets, "Qto_SpaceBaseQuantities", "GrossFloorArea", decimals=2),
        "AreaNet": get_property(psets, "Qto_SpaceBaseQuantities", "NetFloorArea", decimals=2),
    }


def get_zone_data(ifc_file, element):
    zone, space = element
    return {
        "key": (element.Name or "Unnamed") + (space.Name or "Unnamed"),
        "Name": zone.Name,
        "SpaceName": space.Name,
        "AuthorOrganizationName": get_owner_name(zone),
        "AuthorDate": get_owner_creation_date(zone),
        "ModelSoftware": get_owner_application(zone),
        "ModelID": zone.GlobalId,
    }


def get_type_data(ifc_file, element):
    return {
        "key": element.Name,
        "Name": element.Name,
        "Description": element.Description,
        "Category": get_classification(element),
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
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
        "ModelSoftware": get_owner_application(element),
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
        "ModelSoftware": get_owner_application(element),
        "ModelID": element.GlobalId,
    }


def get_owner_name(element):
    if not getattr(element, "OwnerHistory", None):
        return
    return element.OwnerHistory.OwningUser.TheOrganization.Name


def get_owner_creation_date(element):
    if not getattr(element, "OwnerHistory", None):
        return
    return ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat()


def get_owner_application(element):
    if not getattr(element, "OwnerHistory", None):
        return
    return element.OwnerHistory.OwningApplication.ApplicationFullName


def get_facility_parent(element, ifc_class):
    parent = ifcopenshell.util.element.get_aggregate(element)
    while parent:
        if parent.is_a(ifc_class):
            return parent
        if parent.is_a("IfcProject"):
            return
        parent = ifcopenshell.util.element.get_aggregate(parent)


def get_classification(element):
    references = list(ifcopenshell.util.classification.get_references(element))
    if references:
        if hasattr(references[0], "Identification"):
            return "{}:{}".format(references[0].Identification, references[0].Name)
        return "{}:{}".format(references[0].ItemReference, references[0].Name)


def get_actor_address(element, name):
    actors = []
    if element.TheActor.is_a("IfcOrganization") or element.TheActor.is_a("IfcPerson"):
        actors = [element.TheActor]
    elif element.TheActor.is_a("IfcPersonAndOrganization"):
        actors = [element.TheActor.TheOrganization, element.TheActor.ThePerson]
    for actor in actors:
        for address in actor.Addresses or []:
            if hasattr(address, name) and getattr(address, name, None):
                result = getattr(address, name)
                if isinstance(result, tuple):
                    return result[0]
                return result


def get_property(psets, pset_name, prop_name, decimals=None):
    if pset_name in psets:
        result = psets[pset_name].get(prop_name, None)
        if decimals is None or result is None:
            return result
        return round(result, decimals)


get_category_elements = {
    "Actors": get_actors,
    "Facilities": get_facilities,
    "Storeys": get_storeys,
    "Spaces": get_spaces,
    "Zones": get_zones,
    "Types": get_types,
    "Elements": get_elements,
    "Systems": get_systems,
}

get_element_data = {
    "Actors": get_actor_data,
    "Facilities": get_facility_data,
    "Storeys": get_storey_data,
    "Spaces": get_space_data,
    "Zones": get_zone_data,
    "Types": get_type_data,
    "Elements": get_element_data,
    "Systems": get_system_data,
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
