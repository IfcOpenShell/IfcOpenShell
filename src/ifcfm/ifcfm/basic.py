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
import ifcopenshell.util.classification
import ifcopenshell.util.date
import ifcopenshell.util.element
import ifcopenshell.util.fm
import ifcopenshell.util.placement
import ifcopenshell.util.system
from typing import Any, Union, Optional


def get_facilities(ifc_file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    return ifc_file.by_type("IfcBuilding")


def get_storeys(ifc_file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    return ifc_file.by_type("IfcBuildingStorey")


def get_spaces(ifc_file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    return ifc_file.by_type("IfcSpace")


def get_zones(ifc_file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    zones = []
    for zone in ifc_file.by_type("IfcZone"):
        for rel in zone.IsGroupedBy:
            zones.extend([(zone, space) for space in rel.RelatedObjects])
    return zones


def get_element_types(ifc_file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    return ifcopenshell.util.fm.get_fmhem_types(ifc_file)


def get_elements(ifc_file: ifcopenshell.file) -> set[ifcopenshell.entity_instance]:
    elements = set()
    for element_type in get_element_types(ifc_file):
        elements.update(ifcopenshell.util.element.get_types(element_type))
    return elements


def get_systems(ifc_file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    return ifc_file.by_type("IfcSystem")


def get_facility_data(ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> dict[str, Any]:
    return {
        "Name": element.Name,
        "ProjectName": ifc_file.by_type("IfcProject")[0].Name,
        "SiteName": getattr(get_facility_parent(element, "IfcSite"), "Name", None),
        "ClassificationIdentification": get_classification_identification(element),
        "ClassificationName": get_classification_name(element),
        "OrganizationName": get_owner_name(element),
        "CreationDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
        "ModelProjectID": ifc_file.by_type("IfcProject")[0].GlobalId,
        "ModelSiteID": getattr(get_facility_parent(element, "IfcSite"), "GlobalId", None),
        "ModelBuildingID": element.GlobalId,
        "LengthUnit": "millimeters",
        "AreaUnit": "square meters",
        "Phase": ifc_file.by_type("IfcProject")[0].Phase,
    }


def get_storey_data(ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> dict[str, Any]:
    return {
        "Name": element.Name,
        "ClassificationIdentification": "Level",
        "ClassificationName": get_classification_name(element),
        "OrganizationName": get_owner_name(element),
        "CreationDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
        "ModelObject": element.is_a(),
        "ModelID": element.GlobalId,
        "Elevation": ifcopenshell.util.placement.get_storey_elevation(element),
    }


def get_space_data(ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> dict[str, Any]:
    psets = ifcopenshell.util.element.get_psets(element)
    return {
        "Name": element.Name,
        "Description": element.LongName,
        "ClassificationIdentification": get_classification_identification(element),
        "ClassificationName": get_classification_name(element),
        "StoreyName": getattr(get_facility_parent(element, "IfcBuildingStorey"), "Name", None),
        "OrganizationName": get_owner_name(element),
        "CreationDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
        "ModelID": element.GlobalId,
        "FinishCeilingHeight": get_property(psets, "Qto_SpaceBaseQuantities", "FinishCeilingHeight", decimals=2),
        "GrossFloorArea": get_property(psets, "Qto_SpaceBaseQuantities", "GrossFloorArea", decimals=2),
        "NetFloorArea": get_property(psets, "Qto_SpaceBaseQuantities", "NetFloorArea", decimals=2),
    }


def get_zone_data(ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> dict[str, Any]:
    zone, space = element
    return {
        "Name": zone.Name,
        "SpaceName": space.Name,
        "OrganizationName": get_owner_name(zone),
        "CreationDate": get_owner_creation_date(zone),
        "ModelSoftware": get_owner_application(zone),
        "ModelID": zone.GlobalId,
    }


def get_element_type_data(ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> dict[str, Any]:
    psets = ifcopenshell.util.element.get_psets(element)
    return {
        "Name": element.Name,
        "Description": element.Description,
        "ClassificationIdentification": get_classification_identification(element),
        "ClassificationName": get_classification_name(element),
        "OrganizationName": get_owner_name(element),
        "CreationDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
        "ModelObject": "{}[{}]".format(element.is_a(), ifcopenshell.util.element.get_predefined_type(element)),
        "ModelID": element.GlobalId,
        "ModelTag": element.Tag,
        "Manufacturer": get_property(psets, "Pset_ManufacturerTypeInformation", "Manufacturer"),
        "ModelReference": get_property(psets, "Pset_ManufacturerTypeInformation", "ModelReference"),
        "ModelLabel": get_property(psets, "Pset_ManufacturerTypeInformation", "ModelLabel"),
        "PointOfContact": get_property(psets, "Pset_Warranty", "PointOfContact"),
        "WarrantyPeriod": get_property(psets, "Pset_Warranty", "WarrantyPeriod"),
    }


def get_element_data(ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> dict[str, Any]:
    space = ifcopenshell.util.element.get_container(element)
    space_name = space.Name if space.is_a("IfcSpace") else None
    systems = ifcopenshell.util.system.get_element_systems(element)
    system = systems[0].Name if systems else None
    psets = ifcopenshell.util.element.get_psets(element)
    return {
        "Name": element.Name,
        "TypeName": ifcopenshell.util.element.get_type(element).Name,
        "SpaceName": space_name,
        "SystemName": system,
        "OrganizationName": get_owner_name(element),
        "CreationDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
        "ModelObject": "{}[{}]".format(element.is_a(), ifcopenshell.util.element.get_predefined_type(element)),
        "ModelID": element.GlobalId,
        "ModelTag": element.Tag,
        "SerialNumber": get_property(psets, "Pset_ManufacturerOccurrence", "SerialNumber"),
        "BarCode": get_property(psets, "Pset_ManufacturerOccurrence", "BarCode"),
        "BatchReference": get_property(psets, "Pset_ManufacturerOccurrence", "BatchReference"),
        "TagNumber": get_property(psets, "Pset_ConstructionOccurrence", "TagNumber"),
        "AssetIdentifier": get_property(psets, "Pset_ConstructionOccurrence", "AssetIdentifier"),
        "InstallationDate": get_property(psets, "Pset_ConstructionOccurrence", "InstallationDate"),
        "WarrantyStartDate": get_property(psets, "Pset_Warranty", "WarrantyStartDate"),
    }


def get_system_data(ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> dict[str, Any]:
    return {
        "Name": element.Name,
        "Description": element.Description,
        "ClassificationIdentification": get_classification_identification(element),
        "ClassificationName": get_classification_name(element),
        "OrganizationName": get_owner_name(element),
        "CreationDate": get_owner_creation_date(element),
        "ModelSoftware": get_owner_application(element),
        "ModelID": element.GlobalId,
    }


def get_owner_name(element: ifcopenshell.entity_instance) -> Union[str, None]:
    if not getattr(element, "OwnerHistory", None):
        return
    return element.OwnerHistory.OwningUser.TheOrganization.Name


def get_owner_creation_date(element: ifcopenshell.entity_instance) -> Union[str, None]:
    if not getattr(element, "OwnerHistory", None):
        return
    return ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat()


def get_owner_application(element: ifcopenshell.entity_instance) -> Union[str, None]:
    if not getattr(element, "OwnerHistory", None):
        return
    return element.OwnerHistory.OwningApplication.ApplicationFullName


def get_facility_parent(
    element: ifcopenshell.entity_instance, ifc_class: str
) -> Union[ifcopenshell.entity_instance, None]:
    parent = ifcopenshell.util.element.get_aggregate(element)
    while parent:
        if parent.is_a(ifc_class):
            return parent
        if parent.is_a("IfcProject"):
            return
        parent = ifcopenshell.util.element.get_aggregate(parent)


def get_classification_identification(element: ifcopenshell.entity_instance) -> Union[str, None]:
    references = list(ifcopenshell.util.classification.get_references(element))
    if references:
        if hasattr(references[0], "Identification"):
            return references[0].Identification
        return references[0].ItemReference


def get_classification_name(element: ifcopenshell.entity_instance) -> Union[str, None]:
    references = list(ifcopenshell.util.classification.get_references(element))
    if references:
        return references[0].Name


def get_property(
    psets: dict[str, Any], pset_name: str, prop_name: str, decimals: Optional[int] = None
) -> Union[Any, None, float]:
    if pset_name in psets:
        result = psets[pset_name].get(prop_name, None)
        if decimals is None or result is None:
            return result
        return round(result, decimals)


config = {
    "name": "IFC Basic",
    "description": "buildingSMART standardised properties related to asset management and handover",
    "colours": {
        "h": "dddddd",  # Header data
        "p": "dc8774",  # Primary identification data
        "s": "b8dd73",  # Secondary asset data
        "r": "eda786",  # Internal reference
        "e": "96c7d0",  # External / autogenerated data
        "o": "ddb873",  # Conditional / optional data
        "n": "eeeeee",  # Other data
        "b": "000000",  # Not in scope
    },
    "categories": {
        "Facilities": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "ProjectName",
                "SiteName",
                "ClassificationIdentification",
                "ClassificationName",
                "OrganizationName",
                "CreationDate",
                "ModelSoftware",
                "ModelProjectID",
                "ModelSiteID",
                "ModelBuildingID",
                "LengthUnit",
                "AreaUnit",
                "Phase",
            ],
            "colours": "ppprrreeeeesss",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_facilities,
            "get_element_data": get_facility_data,
        },
        "Storeys": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "ClassificationIdentification",
                "ClassificationName",
                "OrganizationName",
                "CreationDate",
                "ModelSoftware",
                "ModelObject",
                "ModelID",
                "Elevation",
            ],
            "colours": "prrreeees",
            "sort": [{"name": "Elevation", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
            "get_category_elements": get_storeys,
            "get_element_data": get_storey_data,
        },
        "Spaces": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "Description",
                "ClassificationIdentification",
                "ClassificationName",
                "StoreyName",
                "OrganizationName",
                "CreationDate",
                "ModelSoftware",
                "ModelID",
                "FinishCeilingHeight",
                "GrossFloorArea",
                "NetFloorArea",
            ],
            "colours": "pprrrreeesss",
            "sort": [{"name": "StoreyName", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
            "get_category_elements": get_spaces,
            "get_element_data": get_space_data,
        },
        "Zones": {
            "keys": ["Name", "SpaceName"],
            "headers": ["Name", "SpaceName", "OrganizationName", "CreationDate", "ModelSoftware", "ModelID"],
            "colours": "prreee",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_zones,
            "get_element_data": get_zone_data,
        },
        "ElementTypes": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "Description",
                "ClassificationIdentification",
                "ClassificationName",
                "OrganizationName",
                "CreationDate",
                "ModelSoftware",
                "ModelObject",
                "ModelID",
                "ModelTag",
                "Manufacturer",
                "ModelReference",
                "ModelLabel",
                "PointOfContact",
                "WarrantyPeriod",
            ],
            "colours": "pprrreeeeesssss",
            "sort": [{"name": "ModelObject", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
            "get_category_elements": get_element_types,
            "get_element_data": get_element_type_data,
        },
        "Elements": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "TypeName",
                "SpaceName",
                "SystemName",
                "OrganizationName",
                "CreationDate",
                "ModelSoftware",
                "ModelObject",
                "ModelID",
                "ModelTag",
                "SerialNumber",
                "BarCode",
                "BatchReference",
                "TagNumber",
                "AssetIdentifier",
                "InstallationDate",
                "WarrantyStartDate",
            ],
            "colours": "prrrreeeeesssssss",
            "sort": [{"name": "TypeName", "order": "ASC"}, {"name": "Name", "order": "ASC"}],
            "get_category_elements": get_elements,
            "get_element_data": get_element_data,
        },
        "Systems": {
            "keys": ["Name"],
            "headers": [
                "Name",
                "Description",
                "ClassificationIdentification",
                "ClassificationName",
                "OrganizationName",
                "CreationDate",
                "ModelSoftware",
                "ModelID",
            ],
            "colours": "pprrreee",
            "sort": [{"name": "Name", "order": "ASC"}],
            "get_category_elements": get_systems,
            "get_element_data": get_system_data,
        },
    },
}
