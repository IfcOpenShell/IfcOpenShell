import datetime
import ifcopenshell
import ifcopenshell.util.fm
import ifcopenshell.util.selector
import ifcopenshell.util.date
import ifcopenshell.util.schema


class Parser:
    def __init__(self, logger):
        self.logger = logger
        self.file = None
        self.sheets = [
            "contacts",
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
        # self.file = ifcopenshell.open(file)
        # self.type_assets = self.selector.parse(self.file, type_query)
        # self.component_assets = self.selector.parse(self.file, component_query)

        self.get_contacts()
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

    def get_contacts(self):
        for element in self.files["arch"].by_type("IfcOrganization"):
            if "IfcApplication" in [e.is_a() for e in self.files["arch"].get_inverse(element)]:
                continue
            name = element.Name
            self.contacts[name] = self.get_organisation(element)

    def get_organisation(self, element):
        return {
            "Name": element.Name,
            "Category": self.get_organisation_category(element),
            "Email": self.get_organisation_address(element, "ElectronicMailAddresses"),
            "Phone": self.get_organisation_address(element, "TelephoneNumbers"),
            "Department": self.get_organisation_address(element, "InternalLocation"),
            "Street": self.get_organisation_address(element, "AddressLines"),
            "PostalBox": self.get_organisation_address(element, "PostalBox"),
            "Town": self.get_organisation_address(element, "Town"),
            "StateRegion": self.get_organisation_address(element, "Region"),
            "PostalCode": self.get_organisation_address(element, "PostalCode"),
            "Country": self.get_organisation_address(element, "Country"),
            "CompanyURL": self.get_organisation_address(element, "WWWHomePageURL"),
        }

    def get_organisation_category(self, element):
        for role in element.Roles or []:
            if role.UserDefinedRole:
                return role.UserDefinedRole

    def get_organisation_address(self, element, name):
        for address in element.Addresses or []:
            if hasattr(address, name) and getattr(address, name, None):
                result = getattr(address, name)
                if isinstance(result, tuple):
                    return result[0]
                return result

    def get_facilities(self):
        element = self.files["arch"].by_type("IfcBuilding")[0]
        self.facilities[element.Name] = {
            "Name": element.Name,
            "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
            "AuthorDate": ifcopenshell.util.date.ifc2datetime(
                self.files["arch"].by_type("IfcProject")[0].OwnerHistory.CreationDate
            ).isoformat(),
            "Category": self.get_classification(element),
            "ProjectName": element.Decomposes[0].RelatingObject.Decomposes[0].RelatingObject.Name,
            "SiteName": element.Decomposes[0].RelatingObject.Name,
            "LinearUnits": "millimeters",
            "AreaUnits": "square meters",
            "AreaMeasurement": "TODO",
            "Phase": element.Decomposes[0].RelatingObject.Decomposes[0].RelatingObject.Phase,
            "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
            "ModelProjectID": self.files["arch"].by_type("IfcProject")[0].GlobalId,
            "ModelSiteID": element.Decomposes[0].RelatingObject.GlobalId,
            "ModelBuildingID": element.GlobalId,
        }

    def get_classification(self, element):
        rel = [r for r in element.HasAssociations or [] if r.is_a("IfcRelAssociatesClassification")]
        if rel:
            classification = rel[0].RelatingClassification
            if getattr(classification, "Identification", None) and getattr(classification, "Name", None):
                return "{}:{}".format(classification.Identification, classification.Name)
            elif getattr(classification, "ItemReference", None) and getattr(classification, "Name", None):
                return "{}:{}".format(classification.ItemReference, classification.Name)

    def get_floors(self):
        storeys = self.files["arch"].by_type("IfcBuildingStorey")
        self.floors["Site"] = {
            "Name": "Site",
            "AuthorOrganizationName": storeys[0].OwnerHistory.OwningUser.TheOrganization.Name,
            "AuthorDate": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "Category": "Site",
            "ModelSoftware": "IfcFM",
            "ModelObject": "IfcExternalSpatialElement",
            "ModelID": ifcopenshell.guid.new(),  # TODO
            "Elevation": None,
        }
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

    def get_spaces(self):
        primary_keys = []
        for element in self.files["arch"].by_type("IfcSpace"):
            name = element.Name
            primary_keys.append(name)
            # TODO: not correct mapping
            psets = ifcopenshell.util.element.get_psets(element)

            category = None
            if "Data" in psets and "COBie.Space.Category" in psets["Data"]:
                category = psets["Data"]["COBie.Space.Category"].replace(" : ", ":")

            usable_height = None
            if "Data" in psets and "COBie.Space.Category" in psets["Data"]:
                usable_height = round(psets["Data"]["COBie.Space.UsableHeight"], 2) or None

            area_gross = None
            if "Data" in psets and "COBie.Space.GrossArea" in psets["Data"]:
                area_gross = round(psets["Data"]["COBie.Space.GrossArea"], 2) or None

            area_net = None
            if "Data" in psets and "COBie.Space.NetArea" in psets["Data"]:
                area_net = round(psets["Data"]["COBie.Space.NetArea"], 2) or None

            self.spaces[name] = {
                "Name": name,
                "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                "AuthorDate": ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat(),
                "Category": category,
                "LevelName": element.Decomposes[0].RelatingObject.Name,
                "Description": element.LongName,
                "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                "ModelID": element.GlobalId,
                "BuildingRoomNumber": None,
                "UsableHeight": usable_height,
                "AreaGross": area_gross,
                "AreaNet": area_net,
            }

    def get_zones(self):
        for element in self.files["arch"].by_type("IfcZone"):
            for rel in element.IsGroupedBy:
                for space in rel.RelatedObjects:
                    if not space.is_a("IfcSpace"):
                        continue
                    self.zones[element.Name + space.Name] = {
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
            # if discipline == "arch":
            #    continue
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

            # Hack
            category = None
            if ifc_file == "arch":
                #if "Data" in psets and "COBie.Type.Category" in psets["Data"]:
                #    if ":" in psets["Data"]["COBie.Type.Category"]:
                #        category = psets["Data"]["COBie.Type.Category"].replace(" : ", ":")
                if "Data" in psets and "Classification.Uniclass.Pr.Number" in psets["Data"]:
                    category = f"{psets['Data']['Classification.Uniclass.Pr.Number']}:{psets['Data']['Classification.Uniclass.Pr.Description']}"
            elif ifc_file == "hyd":
                if "Data" in psets and "Classification.Uniclass.Pr.Number" in psets["Data"]:
                    category = f"{psets['Data']['Classification.Uniclass.Pr.Number']}:{psets['Data']['Classification.Uniclass.Pr.Description']}"

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
                "ModelObject": element.is_a(),
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
            for element in element_type.ObjectTypeOf[0].RelatedObjects:
                name = element.Name

                system = None
                for rel in element.HasAssignments:
                    if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.is_a("IfcSystem"):
                        system = rel.RelatingGroup.Name

                space_name = None

                # Nasty hack
                if ifc_file == "arch":
                    psets = ifcopenshell.util.element.get_psets(element)
                    if "Data" in psets and "COBie.Component.Space" in psets["Data"]:
                        space_name = psets["Data"]["COBie.Component.Space"]
                        if space_name not in self.spaces:
                            space_name = None
                else:
                    space = element.ContainedInStructure[0].RelatingStructure
                    if space.is_a("IfcSpace"):
                       space_name = space.Name

                self.components[name] = {
                    "Name": name,
                    "AuthorOrganizationName": element.OwnerHistory.OwningUser.TheOrganization.Name,
                    "AuthorDate": ifcopenshell.util.date.ifc2datetime(element.OwnerHistory.CreationDate).isoformat(),
                    "TypeName": element_type.Name,
                    "SpaceName": space_name,
                    "InstallationDate": None,
                    "WarrantyStartDate": None,
                    "ModelSoftware": element.OwnerHistory.OwningApplication.ApplicationFullName,
                    "ModelObject": element.is_a(),
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
        for rel in self.files["arch"].by_type("IfcRelAssociatesDocument"):
            element = rel.RelatingDocument
            for related_object in rel.RelatedObjects:
                name = element.Name
                worksheet_row = related_object.Name
                if self.files["arch"].schema == "IFC2X3":
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
