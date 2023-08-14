# IfcFM - IFC for facility management
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import datetime
import ifcopenshell
import ifcopenshell.util.fm
import ifcopenshell.util.selector
import ifcopenshell.util.date
import ifcopenshell.util.schema
import ifcopenshell.util.system
import ifcopenshell.util.placement
import ifcopenshell.util.classification


class Parser2:
    def __init__(self, preset="BASIC"):
        self.file = None
        self.categories = {}
        self.get_category_elements = {}
        self.get_element_data = {}
        self.get_custom_element_data = {}
        self.duplicate_keys = []

        if preset == "BASIC":
            self.get_category_elements = {
                "actors": get_actors,
                "facilities": get_facilities,
                "storeys": get_storeys,
                "spaces": get_spaces,
                "zones": get_zones,
                "types": get_types,
                "elements": get_elements,
                "systems": get_systems,
            }
            self.get_element_data = {
                "actors": get_actor_data,
                "facilities": get_facility_data,
                "storeys": get_storey_data,
                "spaces": get_space_data,
                "zones": get_zone_data,
                "types": get_type_data,
                "elements": get_element_data,
                "systems": get_system_data,
            }

    def parse(self, ifc_file):
        for category_name, get_category_elements in self.get_category_elements.items():
            self.categories.setdefault(category_name, {})
            for element in get_category_elements(ifc_file):
                data = self.get_element_data[category_name](ifc_file, element) or {}
                custom_data = (
                    self.get_custom_element_data.get(category_name, lambda x, y: None)(ifc_file, element) or {}
                )
                data.update(custom_data)

                if data:
                    if data["key"] in self.categories[category_name]:
                        self.duplicate_keys.append((self.categories[category_name][data["key"]], data))
                    self.categories[category_name][data["key"]] = data


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
        "Address1": get_actor_address(element, "AddressLines"),
        "Address2": get_actor_address(element, "Town"),
        "StateRegion": get_actor_address(element, "Region"),
        "PostalCode": get_actor_address(element, "PostalCode"),
        "Country": get_actor_address(element, "Country"),
    }


def get_facility_data(ifc_file, element):
    return {
        "key": element.Name,
        "Name": element.Name,
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(ifc_file.by_type("IfcProject")[0]),
        "Category": get_classification(element),
        "ProjectName": ifc_file.by_type("IfcProject")[0].Name,
        "SiteName": getattr(get_facility_parent(element, "IfcSite"), "Name", None),
        "LinearUnits": "millimeters",
        "AreaUnits": "square meters",
        "AreaMeasurement": "BIM Software",
        "Phase": ifc_file.by_type("IfcProject")[0].Phase,
        "ModelSoftware": get_owner_application(element),
        "ModelProjectID": ifc_file.by_type("IfcProject")[0].GlobalId,
        "ModelSiteID": getattr(get_facility_parent(element, "IfcSite"), "GlobalId", None),
        "ModelBuildingID": element.GlobalId,
    }


def get_storey_data(ifc_file, element):
    return {
        "key": element.Name,
        "Name": element.Name,
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "Category": "Level",
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
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "Category": get_classification(element),
        "LevelName": getattr(get_facility_parent(element, "IfcBuildingStorey"), "Name", None),
        "Description": element.LongName,
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
        "AuthorOrganizationName": get_owner_name(zone),
        "AuthorDate": get_owner_creation_date(zone),
        "SpaceName": space.Name,
        "ModelSoftware": get_owner_application(zone),
        "ModelID": zone.GlobalId,
    }


def get_type_data(ifc_file, element):
    return {
        "key": element.Name,
        "Name": element.Name,
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "Category": get_classification(element),
        "Description": element.Description,
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
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "TypeName": ifcopenshell.util.element.get_type(element).Name,
        "SpaceName": space_name,
        "SystemName": system,
        "ModelSoftware": get_owner_application(element),
        "ModelObject": "{}[{}]".format(element.is_a(), ifcopenshell.util.element.get_predefined_type(element)),
        "ModelID": element.GlobalId,
    }


def get_system_data(ifc_file, element):
    return {
        "key": element.Name,
        "Name": element.Name,
        "Description": element.Description,
        "AuthorOrganizationName": get_owner_name(element),
        "AuthorDate": get_owner_creation_date(element),
        "Category": get_classification(element),
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
    for address in element.TheActor.Addresses or []:
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


class Parser:
    def __init__(self, logger):
        self.logger = logger
        self.file = None
        self.categories = {
            "actors": self.get_actors,
            "facilities": self.get_facilities,
            "floors": self.get_floors,
            "spaces": self.get_spaces,
            "zones": self.get_zones,
            "types": self.get_types,
            "components": self.get_components,
            "systems": self.get_systems,
            # "assemblies",
            # "connections",
            # "spares",
            # "resources",
            # "jobs",
            # "impacts",
            "documents": self.get_documents,
            # "attributes",
            # "coordinates",
            # "issues",
        }
        # COBie
        self.custom_parameters = {
            "types": {
                "AssetType": lambda e, p: None,
                "ManufacturerOrganizationName": lambda e, p: None,
                "ModelNumber": lambda e, p: None,
                "WarrantyGuarantorParts": lambda e, p: None,
                "WarrantyDurationParts": lambda e, p: None,
                "WarrantyGuarantorLabour": lambda e, p: None,
                "WarrantyDurationLabour": lambda e, p: None,
                "DurationUnit": lambda e, p: "months",
                "WarrantyDescription": lambda e, p: None,
                "ReplacementCost": lambda e, p: None,
                "ExpectedLife": lambda e, p: None,
                "NominalLength": lambda e, p: None,
                "NominalWidth": lambda e, p: None,
                "NominalHeight": lambda e, p: None,
            },
            "components": {
                "SerialNumber": lambda e, p: None,
                "InstallationDate": lambda e, p: None,
                "WarrantyStartDate": lambda e, p: None,
                "TagNumber": lambda e, p: None,
                "BarCode": lambda e, p: None,
                "AssetIdentifier": lambda e, p: None,
            }
        }
        # AOH-BEM
        self.custom_parameters = {
            "types": {
                "ProcurementMethod": lambda e, p: None,
                "ManufacturerOrganizationName": lambda e, p: None,
                "SupplierOrganizationName": lambda e, p: None,
                "ModelNumber": lambda e, p: None,
                "WarrantyOrganizationName": lambda e, p: None,
                "WarrantyDuration": lambda e, p: None,
                "SpecificationSection": lambda e, p: None,
                "SubmittalID": lambda e, p: None,
                "ProductURL": lambda e, p: None,
            },
            "components": {
                "InstallationDate": lambda e, p: None,
                "WarrantyStartDate": lambda e, p: None,
                "InstalledModelNumber": lambda e, p: None,
                "SerialNumber": lambda e, p: None,
                "BarCode": lambda e, p: None,
                "TagNumber": lambda e, p: None,
                "OwnerAssetID": lambda e, p: None,
                "FluidHotFeedName": lambda e, p: None,
                "FluidColdFeedName": lambda e, p: None,
                "ElectricPanelName": lambda e, p: None,
                "ElectricCircuitName": lambda e, p: None,
                "ControlledByName": lambda e, p: None,
                "InterlockedWithName": lambda e, p: None,
                "PartOfAssemblyName": lambda e, p: None,
            }
        }
        self.picklists = {
            "Category-Role": [],
            "Category-Facility": [],
            "FloorType": [],
            "Category-Space": [],
            "ZoneType": [],
            "Category-Product": [],
            "AssetType": [],
            "DurationUnit": ["day"],  # See note about hardcoded day below
            "Category-Element": [],
            "SpareType": [],
            "ApprovalBy": [],
            "StageType": [],
            "objType": [],
        }
        self.default_date = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=-2177452801)).isoformat()

    def parse(self, files):
        self.files = files
        for category, get_category in self.categories.items():
            setattr(self, category, {})
            get_category()

    def get_actors(self):
        for ifc in self.files.values():
            for element in ifc.by_type("IfcActor"):
                name = element.TheActor.Name
                self.actors[name] = self.get_actor(element)

    def get_actor(self, element):
        psets = ifcopenshell.util.element.get_psets(element)
        return {
            "Name": element.TheActor.Name,
            "Category": self.get_classification(element),
            "Email": self.get_actor_address(element, "ElectronicMailAddresses"),
            "Phone": self.get_actor_address(element, "TelephoneNumbers"),
            "CompanyURL": self.get_actor_address(element, "WWWHomePageURL"),
            "Department": self.get_actor_address(element, "InternalLocation"),
            "Address1": self.get_actor_address(element, "AddressLines"),
            "Address2": self.get_actor_address(element, "Town"),
            "StateRegion": self.get_actor_address(element, "Region"),
            "PostalCode": self.get_actor_address(element, "PostalCode"),
            "Country": self.get_actor_address(element, "Country"),
        }

    def get_actor_address(self, element, name):
        for address in element.TheActor.Addresses or []:
            if hasattr(address, name) and getattr(address, name, None):
                result = getattr(address, name)
                if isinstance(result, tuple):
                    return result[0]
                return result

    def get_facilities(self):
        for key, ifc in self.files.items():
            if "arch" not in key:
                continue
            element = ifc.by_type("IfcBuilding")[0]
            self.facilities[element.Name] = {
                "Name": element.Name,
                "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                "AuthorDate": ifcopenshell.util.date.ifc2datetime(
                    ifc.by_type("IfcProject")[0].OwnerHistory.CreationDate
                ).isoformat(),
                "Category": self.get_classification(element),
                "ProjectName": element.Decomposes[0].RelatingObject.Decomposes[0].RelatingObject.Name,
                "SiteName": element.Decomposes[0].RelatingObject.Name,
                "LinearUnits": "millimeters",
                "AreaUnits": "square meters",
                "AreaMeasurement": "Revit",
                "Phase": element.Decomposes[0].RelatingObject.Decomposes[0].RelatingObject.Phase,
                "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                "ModelProjectID": ifc.by_type("IfcProject")[0].GlobalId,
                "ModelSiteID": element.Decomposes[0].RelatingObject.GlobalId,
                "ModelBuildingID": element.GlobalId,
            }

    def get_classification(self, element):
        references = list(ifcopenshell.util.classification.get_references(element))
        if references:
            if hasattr(references[0], "Identification"):
                return "{}:{}".format(references[0].Identification, references[0].Name)
            return "{}:{}".format(references[0].ItemReference, references[0].Name)

    def get_floors(self):
        for key, ifc in self.files.items():
            if "arch" not in key:
                continue
            storeys = ifc.by_type("IfcBuildingStorey")
            for element in storeys:
                self.get_floor(element)

    def get_floor(self, element):
        name = element.Name
        elevation = element.ObjectPlacement.RelativePlacement.Location.Coordinates[2]
        self.floors[name] = {
            "Name": name,
            "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
            "AuthorDate": ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat(),
            "Category": "Level",
            "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
            "ModelObject": element.is_a(),
            "ModelID": element.GlobalId,
            "Elevation": elevation,
        }

    def get_property(self, psets, pset_name, prop_name, decimals=None):
        if pset_name in psets:
            result = psets[pset_name].get(prop_name, None)
            if decimals is None or result is None:
                return result
            return round(result, decimals)

    def get_custom_parameters(self, category, data, element, psets):
        for parameter, get_parameter in self.custom_parameters.get(category, {}).items():
            data[parameter] = get_parameter(element, psets)

    def get_spaces(self):
        for key, ifc in self.files.items():
            if "arch" not in key:
                continue
            primary_keys = []
            for element in ifc.by_type("IfcSpace"):
                name = element.Name
                primary_keys.append(name)
                # TODO: not correct mapping
                psets = ifcopenshell.util.element.get_psets(element)
                data = {
                    "Name": name,
                    "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                    "AuthorDate": ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat(),
                    "Category": self.get_classification(element),
                    "LevelName": element.Decomposes[0].RelatingObject.Name,
                    "Description": element.LongName,
                    "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                    "ModelID": element.GlobalId,
                    "BuildingRoomNumber": None,
                    "UsableHeight": self.get_property(psets, "Data", "COBie.Space.UsableHeight", decimals=0),
                    "AreaGross": self.get_property(psets, "Qto_SpaceBaseQuantities", "GrossFloorArea", decimals=2),
                    "AreaNet": self.get_property(psets, "Qto_SpaceBaseQuantities", "NetFloorArea", decimals=2),
                }
                self.get_custom_parameters("spaces", data, element, psets)
                self.spaces[name] = data

    def get_zones(self):
        for ifc in self.files.values():
            for element in ifc.by_type("IfcZone"):
                for rel in element.IsGroupedBy:
                    for space in rel.RelatedObjects:
                        if not space.is_a("IfcSpace"):
                            continue
                        self.zones[(element.Name or "Unnamed") + (space.Name or "Unnamed")] = {
                            "Name": element.Name,
                            "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                            "AuthorDate": ifcopenshell.util.date.ifc2datetime(
                                element.OwnerHistory.CreationDate
                            ).isoformat(),
                            "Category": "Occupancy",
                            "SpaceName": space.Name,
                            "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                            "ModelID": element.GlobalId,
                            "ParentZoneName": None,
                        }

    def get_systems(self):
        for discipline, ifc in self.files.items():
            for element in ifc.by_type("IfcSystem"):
                name = element.Name
                self.systems[name] = {
                    "Name": name,
                    "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                    "AuthorDate": ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat(),
                    "Category": None,
                    "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                    "ModelID": element.GlobalId,
                    "ParentSystemName": None,
                }

    def get_types(self):
        for discipline, ifc in self.files.items():
            self.get_types_from_file(discipline)

    def get_types_from_file(self, ifc_file):
        primary_keys = []
        for element in ifcopenshell.util.fm.get_fmhem_types(self.files[ifc_file]):
            name = element.Name
            primary_keys.append(name)
            psets = ifcopenshell.util.element.get_psets(element)
            data = {
                "Name": name,
                "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                "AuthorDate": ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat(),
                "Category": self.get_classification(element),
                "Description": element.Description,
                "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                "ModelObject": "{}[{}]".format(element.is_a(), ifcopenshell.util.element.get_predefined_type(element)),
                "ModelID": element.GlobalId,
            }
            self.get_custom_parameters("types", data, element, psets)
            self.types[name] = data

    def get_components(self):
        for discipline, ifc in self.files.items():
            self.get_components_from_file(discipline)

    def get_components_from_file(self, ifc_file):
        for element_type in ifcopenshell.util.fm.get_fmhem_types(self.files[ifc_file]):
            elements = ifcopenshell.util.element.get_types(element_type)
            if not elements:
                self.logger.warning("The type has no occurrences %s", element_type)
                continue
            for element in elements:
                name = element.Name

                system = None
                for rel in element.HasAssignments:
                    if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.is_a("IfcSystem"):
                        system = rel.RelatingGroup.Name

                space = ifcopenshell.util.element.get_container(element)
                space_name = space.Name if space.is_a("IfcSpace") else None

                psets = ifcopenshell.util.element.get_psets(element)

                data = {
                    "Name": name,
                    "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                    "AuthorDate": ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat(),
                    "TypeName": element_type.Name,
                    "SpaceName": space_name,
                    "SystemName": system,
                    "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                    "ModelObject": "{}[{}]".format(
                        element.is_a(), ifcopenshell.util.element.get_predefined_type(element)
                    ),
                    "ModelID": element.GlobalId,
                }
                self.get_custom_parameters("components", data, element, psets)
                self.components[name] = data

    def get_documents(self):
        for ifc in self.files.values():
            for rel in ifc.by_type("IfcRelAssociatesDocument"):
                element = rel.RelatingDocument
                if element.is_a("IfcDocumentInformation"):
                    continue
                for related_object in rel.RelatedObjects:
                    worksheet_row = related_object.Name
                    if ifc.schema == "IFC2X3":
                        referenced_document = element.ReferenceToDocument[0]
                        identification = referenced_document.ItemReference
                        author_date = None
                        if referenced_document.CreationTime:
                            author_date = ifcopenshell.util.date.ifc2datetime(
                                referenced_document.CreationTime
                            ).isoformat()
                    else:
                        referenced_document = element.ReferencedDocument
                        identification = referenced_document.Identification
                        author_date = referenced_document.CreationTime

                    worksheet_name = None
                    if related_object.is_a("IfcSpace"):
                        worksheet_name = "Space"
                    elif related_object.is_a("IfcTypeObject"):
                        worksheet_name = "Type"

                    self.documents[identification + worksheet_name + worksheet_row] = {
                        "Name": identification,
                        "AuthorOrganizationName": referenced_document.DocumentOwner.Name,
                        "AuthorDate": author_date,
                        "Category": referenced_document.Purpose,
                        "WorksheetName": worksheet_name,
                        "WorksheetRow": worksheet_row,
                        "Revision": referenced_document.Revision,
                        "Location": referenced_document.Location,
                        "Description": referenced_document.Name,
                        "SpecificationSection": None,
                        "SubmittalID": None,
                        "SourceURL": None,
                    }
