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
import ifcopenshell.util.classification


class Parser:
    def __init__(self, logger):
        self.logger = logger
        self.file = None
        self.sheets = [
            "actors",
            "facilities",
            "floors",
            "spaces",
            "zones",
            "types",
            "components",
            "systems",
            "assemblies",
            "connections",
            "spares",
            "resources",
            "jobs",
            "impacts",
            "documents",
            "attributes",
            "coordinates",
            "issues",
        ]
        for sheet in self.sheets:
            setattr(self, sheet, {})
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

        self.get_actors()
        self.get_facilities()
        self.get_floors()
        self.get_spaces()
        self.get_zones()
        self.get_types()
        self.get_components()
        self.get_systems()
        # self.get_assemblies()
        # self.get_connections()
        # self.get_spares()
        # self.get_resources()
        # self.get_jobs()
        # self.get_impacts()
        self.get_documents()
        # self.get_attributes()
        # self.get_coordinates()
        # self.get_issues()

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

                self.spaces[name] = {
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
            category = self.get_classification(element)

            self.types[name] = {
                "Name": name,
                "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                "AuthorDate": ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat(),
                "Category": category,
                "ProcurementMethod": None,
                "Description": element.Description,
                "ManufacturerOrganizationName": None,
                "SupplierOrganizationName": None,
                "ModelNumber": None,
                "WarrantyOrganizationName": None,
                "WarrantyDuration": None,
                "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                "ModelObject": "{}[{}]".format(element.is_a(), ifcopenshell.util.element.get_predefined_type(element)),
                "ModelID": element.GlobalId,
                "SpecificationSection": None,
                "SubmittalID": None,
                "ProductURL": None,
            }

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

                self.components[name] = {
                    "Name": name,
                    "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                    "AuthorDate": ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat(),
                    "TypeName": element_type.Name,
                    "SpaceName": space_name,
                    "InstallationDate": None,
                    "WarrantyStartDate": None,
                    "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                    "ModelObject": "{}[{}]".format(element.is_a(), ifcopenshell.util.element.get_predefined_type(element)),
                    "ModelID": element.GlobalId,
                    "InstalledModelNumber": None,
                    "SerialNumber": None,
                    "BarCode": None,
                    "TagNumber": None,
                    "OwnerAssetID": None,
                    "SystemName": system,
                    "FluidHotFeedName": None,
                    "FluidColdFeedName": None,
                    "ElectricPanelName": None,
                    "ElectricCircuitName": None,
                    "ControlledByName": None,
                    "InterlockedWithName": None,
                    "PartOfAssemblyName": None,
                }

    def get_documents(self):
        for ifc in self.files.values():
            for rel in ifc.by_type("IfcRelAssociatesDocument"):
                element = rel.RelatingDocument
                if element.is_a("IfcDocumentInformation"):
                    continue
                for related_object in rel.RelatedObjects:
                    name = element.Name
                    worksheet_row = related_object.Name
                    if ifc.schema == "IFC2X3":
                        submittal_id = element.ItemReference
                        referenced_document = element.ReferenceToDocument[0]
                        author_date = None
                        if referenced_document.CreationTime:
                            author_date = ifcopenshell.util.date.ifc2datetime(referenced_document.CreationTime).isoformat()
                    else:
                        submittal_id = element.Identification
                        referenced_document = element.ReferencedDocument
                        author_date = referenced_document.CreationTime

                    worksheet_name = None
                    if related_object.is_a("IfcSpace"):
                        worksheet_name = "Space"
                    elif related_object.is_a("IfcTypeObject"):
                        worksheet_name = "Type"

                    self.documents[element.Name + worksheet_name + worksheet_row] = {
                        "Name": name,
                        "AuthorOrganizationName": referenced_document.DocumentOwner.Name,
                        "AuthorDate": author_date,
                        "Category": referenced_document.Purpose,
                        "WorksheetName": worksheet_name,
                        "WorksheetRow": worksheet_row,
                        "Revision": referenced_document.Revision,
                        "Location": referenced_document.Name,
                        "Description": referenced_document.Description,
                        "SpecificationSection": None,
                        "SubmittalID": submittal_id,
                        "SourceURL": None,
                    }
