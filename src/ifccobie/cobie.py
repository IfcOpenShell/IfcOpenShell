#!/usr/bin/env python3
# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico bimtester.py`

import os
import time
import argparse
import datetime
import ifcopenshell
import logging

class IfcCobieParser():
    def __init__(self, logger):
        self.logger = logger
        self.file = None
        self.contacts = {}
        self.facilities = {}
        self.floors = {}
        self.spaces = {}
        self.zones = {}
        self.types = {}
        self.components = {}
        self.systems = {}
        self.assemblies = {}
        self.connections = {}
        self.spares = {}
        self.resources = {}
        self.jobs = {}
        self.impacts = {}
        self.documents = {}
        self.attributes = {}
        self.coordinates = {}
        self.issues = {}
        self.type_assets = [
            'IfcDoorStyle',
            'IfcBuildingElementProxyType',
            'IfcChimneyType',
            'IfcCoveringType',
            'IfcDoorType',
            'IfcFootingType',
            'IfcPileType',
            'IfcRoofType',
            'IfcShadingDeviceType',
            'IfcWindowType',
            'IfcDistributionControlElementType',
            'IfcDistributionChamberElementType',
            'IfcEnergyConversionDeviceType',
            'IfcFlowControllerType',
            'IfcFlowMovingDeviceType',
            'IfcFlowStorageDeviceType',
            'IfcFlowTerminalType',
            'IfcFlowTreatmentDeviceType',
            'IfcElementAssemblyType',
            'IfcBuildingElementPartType',
            'IfcDiscreteAccessoryType',
            'IfcMechanicalFastenerType',
            'IfcReinforcingElementType',
            'IfcVibrationIsolatorType',
            'IfcFurnishingElementType',
            'IfcGeographicElementType',
            'IfcTransportElementType',
            'IfcSpatialZoneType',
            'IfcWindowStyle',
            ]
        self.component_assets = [
            'IfcBuildingElementProxy',
            'IfcChimney',
            'IfcCovering',
            'IfcDoor',
            'IfcShadingDevice',
            'IfcWindow',
            'IfcDistributionControlElement',
            'IfcDistributionChamberElement',
            'IfcEnergyConversionDevice',
            'IfcFlowController',
            'IfcFlowMovingDevice',
            'IfcFlowStorageDevice',
            'IfcFlowTerminal',
            'IfcFlowTreatmentDevice',
            'IfcDiscreteAccessory',
            'IfcTendon',
            'IfcTendonAnchor',
            'IfcVibrationIsolator',
            'IfcFurnishingElement',
            'IfcGeographicElement',
            'IfcTransportElement',
            ]
        self.picklists = {
            'Category-Role': [],
            'Category-Facility': [],
            'FloorType': [],
            'Category-Space': [],
            'ZoneType': [],
            'Category-Product': [],
            'AssetType': [],
            'DurationUnit': ['day'], # See note about hardcoded day below
            'Category-Element': [],
            'SpareType': [],
            'ApprovalBy': [],
            'StageType': [],
            'objType': []
            }
        self.default_date = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds = -2177452801)).isoformat()

    def parse(self, filename):
        self.file = ifcopenshell.open(filename)
        self.get_contacts()
        self.get_facilities()
        self.get_floors()
        self.get_spaces()
        self.get_zones()
        self.get_types()
        self.get_components()
        self.get_systems()
        self.get_assemblies()
        self.get_connections()
        self.get_spares()
        self.get_resources()
        self.get_jobs()
        self.get_impacts()
        self.get_documents()
        self.get_attributes()
        self.get_coordinates()
        self.get_issues()

    def get_contacts(self):
        histories = self.file.by_type('IfcOwnerHistory')
        for history in histories:
            email = self.get_email_from_history(history)
            if not email:
                continue
            postal_address = self.get_postal_address_from_history(history)
            self.contacts[email] = {
                'CreatedBy': email,
                'CreatedOn': datetime.datetime.fromtimestamp(history.CreationDate).isoformat() if history.CreationDate else datetime.datetime.now().isoformat(),
                'Category': self.get_category_from_history(history),
                'Company': history.OwningUser.TheOrganization.Name or 'n/a',
                'Phone': self.get_phone_from_history(history),
                'ExtSystem': self.get_ext_system_from_history(history),
                'ExtObject': self.get_ext_object_from_history(history),
                'ExtIdentifier': history.OwningUser.ThePerson.Id if self.file.schema == 'IFC2X3' else history.OwningUser.ThePerson.Identification,
                'Department': self.get_department_from_history(history),
                'OrganizationCode': (history.OwningUser.TheOrganization.Id or 'n/a') if self.file.schema == 'IFC2X3' else (history.OwningUser.TheOrganization.Identification or 'n/a'),
                'GivenName': self.get_name_from_person(history.OwningUser.ThePerson, 'GivenName'),
                'FamilyName': self.get_name_from_person(history.OwningUser.ThePerson, 'FamilyName'),
                'Street': self.get_lines_from_address(postal_address),
                'PostalBox': self.get_attribute_from_address(postal_address, 'PostalBox'),
                'Town': self.get_attribute_from_address(postal_address, 'Town'),
                'StateRegion': self.get_attribute_from_address(postal_address, 'Region'),
                'PostalCode': self.get_attribute_from_address(postal_address, 'PostalCode'),
                'Country': self.get_attribute_from_address(postal_address, 'Country')
                }

    def get_facilities(self):
        buildings = self.file.by_type('IfcBuilding')
        for building in buildings:
            building_name = self.get_object_name(building)
            units = self.get_units_from_building(building)
            self.facilities[building_name] = {
                'CreatedBy': self.get_email_from_history(building.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(building.OwnerHistory),
                'Category': self.get_category_from_object(building, 'Category-Facility'),
                'ProjectName': self.get_project_name_from_building(building),
                'SiteName': self.get_site_name_from_building(building),
                'LinearUnits': self.get_unit_type_from_units(units, 'LENGTHUNIT'),
                'AreaUnits': self.get_unit_type_from_units(units, 'AREAUNIT'),
                'VolumeUnits': self.get_unit_type_from_units(units, 'VOLUMEUNIT'),
                'CostUnit': self.get_monetary_unit_from_units(units),
                'AreaMeasurement': self.get_area_measurement_from_building(building),
                'ExternalSystem': self.get_ext_system_from_history(building.OwnerHistory),
                'ExternalProjectObject': self.get_ext_project_object(),
                'ExternalProjectIdentifier': self.get_project_globalid_from_building(building),
                'ExternalSiteObject': self.get_ext_site_object(),
                'ExternalSiteIdentifier': self.get_site_globalid_from_building(building),
                'ExternalFacilityObject': self.get_ext_object(building),
                'ExternalFacilityIdentifier': building.GlobalId,
                'Description': self.get_object_attribute(building, 'Description', default='n/a'),
                'ProjectDescription': self.get_object_attribute(self.get_parent_spatial_element(building, 'IfcProject'), 'Description', default='n/a'),
                'SiteDescription': self.get_object_attribute(self.get_parent_spatial_element(building, 'IfcSite'), 'Description', default='n/a'),
                'Phase': self.get_object_attribute(self.get_parent_spatial_element(building, 'IfcProject'), 'Phase', default='n/a')
                }

    def get_floors(self):
        storeys = self.file.by_type('IfcBuildingStorey')
        for storey in storeys:
            storey_name = self.get_object_name(storey)
            self.floors[storey_name] = {
                'CreatedBy': self.get_email_from_history(storey.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(storey.OwnerHistory),
                'Category': self.get_category_from_object(storey, 'FloorType'),
                'ExtSystem': self.get_ext_system_from_history(storey.OwnerHistory),
                'ExtObject': self.get_ext_object(storey),
                'ExtIdentifier': storey.GlobalId,
                'Description': self.get_object_attribute(storey, 'Description', default='n/a'),
                'Elevation': self.get_object_attribute(storey, 'Elevation', default='n/a'),
                'Height': self.get_height_from_storey(storey)
                }

    def get_spaces(self):
        spaces = self.file.by_type('IfcSpace')
        for space in spaces:
            space_name = self.get_object_name(space)
            self.spaces[space_name] = {
                'CreatedBy': self.get_email_from_history(space.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(space.OwnerHistory),
                'Category': self.get_category_from_object(space, 'Category-Space'),
                'FloorName': self.get_object_attribute(self.get_parent_spatial_element(space, 'IfcBuildingStorey'), 'Name', is_primary_key=True, default='n/a'),
                'Description': self.get_object_attribute(space, 'Description', default='n/a'),
                'ExtSystem': self.get_ext_system_from_history(space.OwnerHistory),
                'ExtObject': self.get_ext_object(space),
                'ExtIdentifier': space.GlobalId,
                'RoomTag': self.get_pset_value_from_object(space, 'COBie_Space', 'RoomTag', 'n/a'),
                'UsableHeight': self.get_usable_height_from_space(space),
                'GrossArea': self.get_gross_area_from_space(space),
                'NetArea': self.get_net_area_from_space(space),
                }

    def get_zones(self):
        zones = self.file.by_type('IfcZone')
        for zone in zones:
            zone_name = self.get_object_name(zone)
            self.zones[zone_name] = {
                'CreatedBy': self.get_email_from_history(zone.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(zone.OwnerHistory),
                'Category': self.get_category_from_object(zone, 'ZoneType'),
                'SpaceNames': self.get_grouped_product_names_from_object(zone, 'IfcSpace'),
                'ExtSystem': self.get_ext_system_from_history(zone.OwnerHistory),
                'ExtObject': self.get_ext_object(zone),
                'ExtIdentifier': zone.GlobalId,
                'Description': self.get_object_attribute(zone, 'Description', default='n/a'),
                }

    def get_types(self):
        types = self.file.by_type('IfcTypeObject')
        for type in types:
            is_a_type_asset = False
            for type_asset in self.type_assets:
                if type.is_a(type_asset):
                    is_a_type_asset = True
            if not is_a_type_asset:
                self.logger.warning('A type which is not an asset was found for {}'.format(type))
                continue
            # The responsibility matrix states to parse IfcMaterial and
            # IfcMaterialLayerSet too, but it doesn't make much sense, so I
            # don't parse it.
            type_name = self.get_object_name(type)
            self.types[type_name] = {
                'CreatedBy': self.get_email_from_history(type.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(type.OwnerHistory),
                'Category': self.get_category_from_object(type, 'Category-Product'),
                # The responsibility matrix states two possible fallbacks. I
                # choose the 'n/a' option as opposed to repeating the name.
                'Description': self.get_object_attribute(type, 'Description', default='n/a'),
                'AssetType': self.get_pset_value_from_object(type, 'COBie_Asset', 'AssetType', 'n/a', 'AssetType'),
                'Manufacturer': self.get_contact_pset_value_from_object(type, 'Pset_ManufacturerTypeInformation', 'Manufacturer'),
                'ModelNumber': self.get_pset_value_from_object(type, 'Pset_ManufacturerTypeInformation', 'ModelLabel', 'n/a'),
                # The responsibility matrix talks about using the Pset_Warranty
                # values, but Pset_Warranty only applies to objects, not types,
                # and so they are ignored.
                'WarrantyGuarantorParts': self.get_contact_pset_value_from_object(type, 'COBie_Warranty', 'WarrantyGuarantorParts'),
                'WarrantyDurationParts': self.get_pset_value_from_object(type, 'COBie_Warranty', 'WarrantyDurationParts', 0),
                'WarrantyGuarantorLabor': self.get_contact_pset_value_from_object(type, 'COBie_Warranty', 'WarrantyGuarantorLabor'),
                'WarrantyDurationLabor': self.get_pset_value_from_object(type, 'COBie_Warranty', 'WarrantyDurationLabor', 0),
                # TODO: this may be derived from the duration values above, but
                # until it is clarified, it will be hardcoded as 'day'
                'WarrantyDurationUnit': 'day',
                'ExtSystem': self.get_ext_system_from_history(type.OwnerHistory),
                'ExtObject': self.get_ext_object(type),
                'ExtIdentifier': type.GlobalId,
                'ReplacementCost': self.get_pset_value_from_object(type, 'COBie_EconomicImpactValues', 'ReplacementCost', 'n/a'),
                'ExpectedLife': self.get_expected_life_from_type(type),
                # See note about WarrantyDurationUnit above
                'DurationUnit': 'day',
                'NominalLength': self.get_pset_value_from_object(type, 'COBie_Specification', 'NominalLength', 0),
                'NominalWidth': self.get_pset_value_from_object(type, 'COBie_Specification', 'NominalWidth', 0),
                'NominalHeight': self.get_pset_value_from_object(type, 'COBie_Specification', 'NominalHeight', 0),
                'ModelReference': self.get_pset_value_from_object(type, 'Pset_ManufacturerTypeInformation', 'ModelReference', 'n/a'),
                'Shape': self.get_pset_value_from_object(type, 'COBie_Specification', 'Shape', 'n/a'),
                'Size': self.get_pset_value_from_object(type, 'COBie_Specification', 'Size', 'n/a'),
                # The responsbility matrix allows the British spelling of
                # "colour". I, however, do not.
                'Color': self.get_pset_value_from_object(type, 'COBie_Specification', 'Color', 'n/a'),
                'Finish': self.get_pset_value_from_object(type, 'COBie_Specification', 'Finish', 'n/a'),
                'Grade': self.get_pset_value_from_object(type, 'COBie_Specification', 'Grade', 'n/a'),
                'Material': self.get_pset_value_from_object(type, 'COBie_Specification', 'Material', 'n/a'),
                'Constituents': self.get_pset_value_from_object(type, 'COBie_Specification', 'Constituents', 'n/a'),
                'Features': self.get_pset_value_from_object(type, 'COBie_Specification', 'Features', 'n/a'),
                'AccessibilityPerformance': self.get_pset_value_from_object(type, 'COBie_Specification', 'AccessibilityPerformance', 'n/a'),
                'CodePerformance': self.get_pset_value_from_object(type, 'COBie_Specification', 'CodePerformance', 'n/a'),
                'SustainabilityPerformance': self.get_pset_value_from_object(type, 'COBie_Specification', 'SustainabilityPerformance', 'n/a'),
                }

    def get_components(self):
        components = self.file.by_type('IfcElement')
        for component in components:
            if not self.is_object_a_component_asset(component):
                self.logger.warning('A component which is not an asset was found for {}'.format(component))
                continue
            component_name = self.get_object_name(component)
            self.components[component_name] = {
                'CreatedBy': self.get_email_from_history(component.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(component.OwnerHistory),
                'TypeName': self.get_type_name_from_object(component),
                'Space': self.get_space_name_from_component(component),
                'Description': self.get_object_attribute(component, 'Description', default='n/a'),
                'ExtSystem': self.get_ext_system_from_history(component.OwnerHistory),
                'ExtObject': self.get_ext_object(component),
                'ExtIdentifier': component.GlobalId,
                'SerialNumber': self.get_pset_value_from_object(component, 'Pset_ManufacturerOccurence', 'SerialNumber', 'n/a'),
                'InstallationDate': self.get_pset_value_from_object(component, 'COBie_Component', 'InstallationDate', self.default_date),
                'WarrantyStartDate': self.get_pset_value_from_object(component, 'COBie_Component', 'WarrantyStartDate', self.default_date),
                'TagNumber': self.get_pset_value_from_object(component, 'COBie_Component', 'TagNumber', 'n/a'),
                'BarCode': self.get_pset_value_from_object(component, 'Pset_ManufacturerOccurence', 'BarCode', 'n/a'),
                'AssetIdentifier': self.get_pset_value_from_object(component, 'COBie_Component', 'AssetIdentifier', 'n/a'),
                }

    def get_systems(self):
        systems = self.file.by_type('IfcSystem')
        for system in systems:
            system_name = self.get_object_name(system)
            self.systems[system_name] = {
                'CreatedBy': self.get_email_from_history(system.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(system.OwnerHistory),
                'Category': self.get_category_from_object(system, 'Category-Element'),
                'ComponentNames': self.get_grouped_product_names_from_object(system, 'IfcProduct'),
                'ExtSystem': self.get_ext_system_from_history(system.OwnerHistory),
                'ExtObject': self.get_ext_object(system),
                'ExtIdentifier': system.GlobalId,
                'Description': self.get_object_attribute(system, 'Description', default='n/a'),
                }

    def get_assemblies(self):
        assemblies = self.file.by_type('IfcRelAggregates')
        for assembly in assemblies:
            assembly_name = self.get_object_name(assembly)
            if not self.is_object_a_component_asset(assembly.RelatingObject):
                continue
            self.assemblies[assembly_name] = {
                'CreatedBy': self.get_email_from_history(assembly.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(assembly.OwnerHistory),
                'SheetName': 'Assembly',
                'ParentName': self.get_object_name(assembly.RelatingObject),
                'ChildNames': ','.join([o.Name if o.Name else '' for o in assembly.RelatedObjects]),
                'AssemblyType': 'n/a', # I don't understand this field
                'ExtSystem': self.get_ext_system_from_history(assembly.OwnerHistory),
                'ExtObject': self.get_ext_object(assembly),
                'ExtIdentifier': assembly.GlobalId,
                'Description': self.get_object_attribute(assembly, 'Description', default='n/a'),
                }

    def get_connections(self):
        connections = self.file.by_type('IfcRelConnects')
        for connection in connections:
            connection_name = self.get_object_name(connection)
            self.connections[connection_name] = {
                'CreatedBy': self.get_email_from_history(connection.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(connection.OwnerHistory),
                # There is ambiguity for what the ConnectionType mapping should be
                'ConnectionType': self.get_object_attribute(connection, 'Description', default='n/a'),
                'SheetName': 'Connections',
                'RowName1': self.get_row_name_from_connection(connection, 'RelatingElement'),
                'RowName2': self.get_row_name_from_connection(connection, 'RelatedElement'),
                'RealizingElement': self.get_port_name_from_connection(connection, 'RealizingElement'),
                'PortName1': self.get_port_name_from_connection(connection, 'RelatingPort'),
                'PortName2': self.get_port_name_from_connection(connection, 'RelatedPort'),
                'ExtSystem': self.get_ext_system_from_history(connection.OwnerHistory),
                'ExtObject': self.get_ext_object(connection),
                'ExtIdentifier': connection.GlobalId,
                'Description': self.get_object_attribute(connection, 'Description', default='n/a'),
                }

    def get_spares(self):
        spares = self.file.by_type('IfcConstructionProductResource')
        for spare in spares:
            spare_name = self.get_object_name(spare)
            self.spares[spare_name] = {
                'CreatedBy': self.get_email_from_history(spare.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(spare.OwnerHistory),
                'Category': self.get_category_from_object(spare, 'SpareType'),
                'TypeName': self.get_type_name_from_object(spare),
                'Suppliers': self.get_contact_pset_value_from_object(spare, 'COBie_Spare', 'Suppliers'),
                'ExtSystem': self.get_ext_system_from_history(spare.OwnerHistory),
                'ExtObject': self.get_ext_object(spare),
                'ExtIdentifier': spare.GlobalId,
                'Description': self.get_object_attribute(spare, 'Description', default='n/a'),
                'SetNumber': self.get_contact_pset_value_from_object(spare, 'COBie_Spare', 'SetNumber'),
                'PartNumber': self.get_contact_pset_value_from_object(spare, 'COBie_Spare', 'PartNumber'),
                }

    def get_resources(self):
        resources = self.file.by_type('IfcConstructionProductResource')
        for resource in resources:
            resource_name = self.get_object_name(resource)
            self.resources[resource_name] = {
                'CreatedBy': self.get_email_from_history(resource.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(resource.OwnerHistory),
                'Category': self.get_object_attribute(resource, 'ObjectType', picklist='ResourceType', default='n/a'),
                'ExtSystem': self.get_ext_system_from_history(resource.OwnerHistory),
                'ExtObject': self.get_ext_object(resource),
                'ExtIdentifier': resource.GlobalId,
                'Description': self.get_object_attribute(resource, 'Description', default='n/a'),
                }

    def get_jobs(self):
        jobs = self.file.by_type('IfcTask')
        for job in jobs:
            job_name = self.get_object_name(job)
            task_time = job.TaskTime
            self.jobs[job_name] = {
                'CreatedBy': self.get_email_from_history(job.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(job.OwnerHistory),
                'Category': self.get_object_attribute(job, 'ObjectType', picklist='JobType', default='n/a'),
                'Status': self.get_object_attribute(job, 'Status', picklist='JobStatusType', default='n/a'),
                'TypeName': self.get_type_name_from_object(job),
                'Description': self.get_object_attribute(job, 'Description', default='n/a'),
                'Duration': self.get_object_attribute(task_time, 'ScheduleDuration', default=0),
                'DurationUnit': 'day',
                'Start': self.get_object_attribute(task_time, 'ScheduleStart', default=0),
                'TaskStartUnit': 'day',
                'Frequency': self.get_object_attribute(task_time.Recurrence, 'Occurrences', default=0) if hasattr(task_time, 'Recurrence') else 0,
                'FrequencyUnit': 'day',
                'ExtSystem': self.get_ext_system_from_history(job.OwnerHistory),
                'ExtObject': self.get_ext_object(job),
                'ExtIdentifier': job.GlobalId,
                'TaskNumber': self.get_object_attribute(job, 'Identification'),
                'Priors': self.get_priors_from_job(job),
                'ResourceNames': self.get_resource_names_from_job(job),
                }

    # Impacts is not explicitly defined as a mapping in the responsibliity
    # matrix. This is my best guess. This data should not be relied upon until
    # this is clarified.
    def get_impacts(self):
        impacts = self.file.by_type('IfcPropertySet')
        for impact in impacts:
            if impact.Name != 'Pset_EnvironmentalImpactValues' \
                or not impact.HasProperties:
                continue
            for property in impact.HasProperties:
                property_name = '{}-{}'.format(property.id(), self.get_object_name(property))
                self.impacts[property_name] = {
                    'CreatedBy': self.get_email_from_history(impact.OwnerHistory),
                    'CreatedOn': self.get_created_on_from_history(impact.OwnerHistory),
                    'ImpactType': None,
                    'ImpactStage': None,
                    'SheetName': 'Impacts',
                    'RowName': 'n/a',
                    'Value': self.get_property_value(property),
                    'Unit': '{}{}'.format(property.Unit.Prefix, property.Unit.Name) if hasattr(property, 'Unit') and property.Unit else 'n/a',
                    'LeadInTime': self.get_property_value(property, name='LeadInTime'),
                    'Duration': self.get_property_value(property, name='Duration'),
                    'LeadOutTime': self.get_property_value(property, name='LeadOutTime'),
                    'ExtSystem': self.get_ext_system_from_history(impact.OwnerHistory),
                    'ExtObject': self.get_ext_object(impact),
                    'ExtIdentifier': impact.GlobalId,
                    'Description': self.get_object_attribute(impact, 'Description', default='n/a'),
                }

    def get_documents(self):
        documents = self.file.by_type('IfcDocumentInformation')
        for document in documents:
            document_name = self.get_object_name(document)
            self.documents[document_name] = {
                'CreatedBy': self.get_email_from_history(document.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(document.OwnerHistory),
                'Category': 'n/a', # I am not sure what this mapping is meant to be
                'ApprovalBy': self.get_object_attribute(document, 'IntendedUse', picklist='ApprovalBy', default='Information Only'),
                'Stage': self.get_object_attribute(document, 'Scope', picklist='StageType', default='Required'),
                'SheetName': 'Documents',
                'RowName': 'n/a',
                'Directory': self.get_directory_from_document(document),
                'File': self.get_file_from_document(document),
                'ExtSystem': self.get_ext_system_from_history(document.OwnerHistory),
                'ExtObject': self.get_ext_object(document),
                'ExtIdentifier': document.GlobalId,
                'Description': self.get_object_attribute(document, 'Description', default=document_name),
                'Reference': document_name,
                }

    # Attributes is not explicitly defined as a mapping in the responsibliity
    # matrix. This is my best guess. This data should not be relied upon until
    # this is clarified.
    def get_attributes(self):
        attributes = self.file.by_type('IfcPropertySet')
        for attribute in attributes:
            if not attribute.HasProperties:
                continue
            for property in attribute.HasProperties:
                property_name = '{}-{}'.format(property.id(), self.get_object_name(property))
                self.attributes[property_name] = {
                    'CreatedBy': self.get_email_from_history(attribute.OwnerHistory),
                    'CreatedOn': self.get_created_on_from_history(attribute.OwnerHistory),
                    'Category': 'n/a', # I am not sure what this mapping is meant to be
                    'SheetName': 'Attributes',
                    'RowName': 'n/a', # I am not sure what this mapping is meant to be
                    'Value': self.get_property_value(property),
                    'Unit': '{}{}'.format(property.Unit.Prefix if hasattr(property.Unit, 'Prefix') else '', property.Unit.Name if hasattr(property.Unit, 'Name') else 'n/a') if hasattr(property, 'Unit') and property.Unit else 'n/a',
                    'ExtSystem': self.get_ext_system_from_history(attribute.OwnerHistory),
                    'ExtObject': self.get_ext_object(attribute),
                    'ExtIdentifier': attribute.GlobalId,
                    'Description': self.get_object_attribute(attribute, 'Description', default='n/a'),
                    # I'm holding off implementing this until I understand a bit
                    # more about attributes
                    'AllowedValues': 'n/a',
                    }

    def get_coordinates(self):
        coordinates = self.file.by_type('IfcBuildingStorey') \
            + self.file.by_type('IfcSpace') \
            + self.file.by_type('IfcProduct')
        for coordinate in coordinates:
            coordinate_name = '{}/{}'.format(coordinate.is_a(), self.get_object_name(coordinate))
            self.coordinates[coordinate_name] = {
                'CreatedBy': self.get_email_from_history(coordinate.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(coordinate.OwnerHistory),
                'Category': 'Location', # I am not sure what this mapping is meant to be
                'SheetName': 'Coordinates',
                'RowName': 'n/a',
                'CoordinateXAxis': coordinate.ObjectPlacement.RelativePlacement.Location.Coordinates[0],
                'CoordinateYAxis': coordinate.ObjectPlacement.RelativePlacement.Location.Coordinates[1],
                'CoordinateZAxis': coordinate.ObjectPlacement.RelativePlacement.Location.Coordinates[2],
                'ExtSystem': self.get_ext_system_from_history(coordinate.OwnerHistory),
                'ExtObject': self.get_ext_object(coordinate),
                'ExtIdentifier': coordinate.GlobalId,
                # Holding off implementing this, see Bug #688:
                # https://github.com/IfcOpenShell/IfcOpenShell/issues/688
                'ClockwiseRotation': 'n/a', # X axis
                'ElevationalRotation': 'n/a', # Y axis
                'YawRotation': 'n/a', # Z axis
                }

    # I don't fully understand this worksheet. Don't trust this data.
    def get_issues(self):
        issues = self.file.by_type('IfcApproval')
        for issue in issues:
            issue_name = self.get_object_name(issue)
            self.issues[issue_name] = {
                'CreatedBy': self.get_email_from_history(issue.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(issue.OwnerHistory),
                'Type': 'n/a', # How do we get to the Pset_Risk from the IfcApproval?
                'Risk': 'n/a', # How do we get to the Pset_Risk from the IfcApproval?
                'Chance': 'n/a', # How do we get to the Pset_Risk from the IfcApproval?
                'Impact': 'n/a', # How do we get to the Pset_Risk from the IfcApproval?
                'SheetName1': 'n/a',
                'RowName1': 'n/a',
                'SheetName2': 'n/a',
                'RowName2': 'n/a',
                'Description': self.get_object_attribute(issue, 'Description', default='n/a'),
                'Owner': self.get_email_from_history(issue.RequestingApproval), # Is this correct?
                'Mitigation': 'n/a',
                'ExtSystem': self.get_ext_system_from_history(issue.OwnerHistory),
                'ExtObject': self.get_ext_object(issue),
                'ExtIdentifier': issue.GlobalId,
                }

    def get_directory_from_document(self, document):
        if self.file.schema == 'IFC2X3':
            if document.HasDocumentReferences:
                for reference in document.HasDocumentReferences:
                    return self.get_object_attribute(reference, 'Location', default='n/a')
        else:
            return self.get_object_attribute(document, 'Location', default='n/a')

    def get_file_from_document(self, document):
        if self.file.schema == 'IFC2X3':
            if document.HasDocumentReferences:
                for reference in document.HasDocumentReferences:
                    return self.get_object_attribute(reference, 'Name', default='n/a')
        else:
            self.get_object_attribute(document, 'Identification', default='n/a')

    def get_resource_names_from_job(self, job):
        names = []
        if job.OperatesOn \
            and job.OperatesOn.RelatedObjects:
            for object in job.OperatesOn.RelatedObjects:
                names.append(object.Name)
        return ','.join(names)

    def get_priors_from_job(self, job):
        # The responsibility matrix is vague as to whether it expects a task
        # name or a task identification. I chose task name.
        if job.IsSuccessorFrom \
            and job.IsSuccessorFrom.RelatingProcess \
            and job.IsSuccessorFrom.RelatingProcess.is_a('IfcTask'):
                return self.get_object_name(job.IsSuccessorFrom.RelatingProcess)

    def get_row_name_from_connection(self, connection, key):
        if not connection.is_a('IfcRelConnectsElements'):
            return None
        object = getattr(connection, key)
        if self.is_object_a_component_asset(object):
            return object.Name
        self.logger.error('The connected object relationship {} is not a component asset for {}'.format(key, connection))

    def get_port_name_from_connection(self, connection, key):
        if not connection.is_a('IfcRelConnectsPorts'):
            return None
        object = getattr(connection, key)
        if object and self.is_object_a_component_asset(object):
            return object.Name
        self.logger.error('The connected object relationship {} is not a component asset for {}'.format(key, connection))

    def is_object_a_component_asset(self, object):
        is_an_asset = False
        for asset in self.component_assets:
            if object.is_a(asset):
                is_an_asset = True
        return is_an_asset

    def get_space_name_from_component(self, component):
        for relationship in component.ContainedInStructure:
            if relationship.RelatingStructure.is_a('IfcSpace') \
                and relationship.RelatingStructure.Name:
                return relationship.RelatingStructure.Name
        self.logger.error('A related space name could not be determined for {}'.format(component))

    def get_type_name_from_object(self, object):
        if self.file.schema == 'IFC2X3':
            for relationship in object.IsDefinedBy:
                if relationship.is_a('IfcRelDefinesByType') \
                    and relationship.RelatingType.Name:
                    return relationship.RelatingType.Name
        else:
            for relationship in object.IsTypedBy:
                if relationship.RelatingType.Name:
                    return relationship.RelatingType.Name
        self.logger.error('A related type name could not be determined for {}'.format(object))

    def get_expected_life_from_type(self, type):
        if self.file.schema == 'IFC2X3':
            return self.get_pset_value_from_object(type, 'COBie_ServiceLife', 'ServiceLifeDuration', 'n/a')
        return self.get_pset_value_from_object(type, 'Pset_ServiceLife', 'ServiceLifeDuration', 'n/a')

    def get_contact_pset_value_from_object(self, object, pset_name, property_name):
        result = self.get_pset_value_from_object(object, pset_name, property_name)
        if not result:
            self.logger.error('No property {} in {} was found for {}'.format(property_name, pset_name, object))
        if result not in self.contacts:
            self.logger.error('A coresponding {} contact in {} was not found for {}'.format(property_name, pset_name, object))
        return result

    def get_pset_value_from_object(self, object, pset_name, property_name, default=None, picklist=None):
        pset = self.get_pset_from_object(object, pset_name)
        if not pset:
            if picklist:
                self.picklists[picklist].append(default)
            return default
        prop = self.get_property_from_pset(pset, property_name, default)
        if picklist:
            self.picklists[picklist].append(prop)
        return prop

    def get_grouped_product_names_from_object(self, object, type):
        names = []
        for relationship in object.IsGroupedBy:
            for related_object in relationship.RelatedObjects:
                if related_object.is_a(type):
                    names.append(related_object.Name)
        if names:
            return ','.join(names)
        self.logger.error('No related {} were found for {}'.format(type, object))

    def get_net_area_from_space(self, space):
        qto = self.get_qto_from_object(space, 'Qto_SpaceBaseQuantities')
        if not qto:
            return 'n/a'
        return self.get_property_from_qto(qto, 'NetFloorArea', 'AreaValue')

    def get_gross_area_from_space(self, space):
        qto = self.get_qto_from_object(space, 'Qto_SpaceBaseQuantities')
        if not qto:
            return 'n/a'
        return self.get_property_from_qto(qto, 'GrossFloorArea', 'AreaValue')

    def get_usable_height_from_space(self, space):
        qto = self.get_qto_from_object(space, 'Qto_SpaceBaseQuantities')
        if not qto:
            return 'n/a'
        return self.get_property_from_qto(qto, 'FinishCeilingHeight', 'LengthValue')

    def get_qto_from_object(self, object, name):
        for relationship in object.IsDefinedBy:
            if relationship.is_a('IfcRelDefinesByProperties') \
                and relationship.RelatingPropertyDefinition.is_a('IfcQuantitySet') \
                and relationship.RelatingPropertyDefinition.Name == name:
                return relationship.RelatingPropertyDefinition
        self.logger.warning('The qto {} was not found for {}'.format(name, object))

    def get_property_from_qto(self, qto, name, attribute):
        for property in qto.Quantities:
            if property.Name == name:
                return getattr(property, attribute)
        self.logger.warning('The quantity value {} was not found for {}'.format(name, qto))
        return 'n/a'

    def get_property_from_pset(self, pset, name, default=None):
        for prop in pset.HasProperties:
            if prop.Name == name:
                return prop.NominalValue.wrappedValue
        self.logger.warning('The property {} was not found for {}'.format(name, pset))
        return default

    def get_property_value(self, prop, name=None):
        if not prop.is_a('IfcPropertySingleValue'):
            return 'n/a'
        if name is not None and prop.Name != name:
            return 'n/a'
        value = self.get_object_attribute(prop, 'NominalValue', default=None)
        if value:
            return value.wrappedValue
        return 'n/a'

    def get_pset_from_object(self, object, name):
        if object.is_a('IfcTypeObject'):
            if object.HasPropertySets:
                for pset in object.HasPropertySets:
                    if pset.is_a('IfcPropertySet') \
                        and pset.Name == name:
                        return pset
        else:
            for relationship in object.IsDefinedBy:
                if relationship.is_a('IfcRelDefinesByProperties') \
                    and relationship.RelatingPropertyDefinition.is_a('IfcPropertySet') \
                    and relationship.RelatingPropertyDefinition.Name == name:
                    return relationship.RelatingPropertyDefinition
        self.logger.warning('The pset {} was not found for {}'.format(name, object))

    def get_height_from_storey(self, storey):
        for relationship in storey.IsDefinedBy:
            if not relationship.RelatingPropertyDefinition.is_a('IfcElementQuantity'):
                continue
            for quantity in relationship.RelatingPropertyDefinition.Quantities:
                if quantity.is_a('IfcQuantityLength') \
                    and quantity.LengthValue:
                    return quantity.LengthValue
        self.logger.warning('A height length value was not found for {}'.format(storey))
        return 'n/a'

    def get_created_on_from_history(self, history):
        if history.CreationDate:
            return datetime.datetime.fromtimestamp(history.CreationDate).isoformat()
        self.logger.warning('A created on date was not found for {}'.format(history))
        return self.default_date

    def get_object_attribute(self, object, attribute, is_primary_key = False, picklist = None, default=None):
        result = getattr(object, attribute)
        if result:
            if picklist:
                self.picklists[picklist].append(result)
            return result
        if is_primary_key:
            self.logger.error('The primary key attribute {} was not found for {}'.format(attribute, object))
        else:
            self.logger.warning('The attribute {} was not found for {}'.format(attribute, object))
        return default

    def get_ext_project_object(self):
        self.picklists['objType'].append('IfcProject')
        return 'IfcProject'

    def get_ext_site_object(self):
        self.picklists['objType'].append('IfcSite')
        return 'IfcSite'

    def get_ext_object(self, object):
        self.picklists['objType'].append(object.is_a())
        return object.is_a()

    def get_ext_system_from_history(self, history):
        return history.OwningApplication.ApplicationFullName

    def get_object_name(self, object):
        if not object.Name:
            self.logger.error('A primary key name was not found for {}'.format(object))
            return 'Object{}'.format(object.id())
        return object.Name

    def get_area_measurement_from_building(self, building):
        for relationship in building.IsDefinedBy:
            if relationship.RelatingPropertyDefinition.is_a('IfcElementQuantity') \
                and relationship.RelatingPropertyDefinition.MethodOfMeasurement:
                return relationship.RelatingPropertyDefinition.MethodOfMeasurement
        self.logger.warning('A method of measurement was not defined for {}'.format(building))

    def get_unit_type_from_units(self, units, type):
        for unit in units:
            if unit.UnitType == type:
                if unit.is_a('IfcSIUnit') and unit.Prefix:
                    return '{}{}'.format(unit.Prefix, unit.Name)
                return unit.Name
        self.logger.error('A unit {} was not defined in this project for {}'.format(type, units))

    def get_monetary_unit_from_units(self, units):
        for unit in units:
            if unit.is_a('IfcMonetaryUnit'):
                return unit.Currency
        self.logger.error('A monetary unit could not be found for {}'.format(units))

    def get_project_globalid_from_building(self, building):
        return self.get_parent_spatial_element(building, 'IfcProject').GlobalId

    def get_site_globalid_from_building(self, building):
        return self.get_parent_spatial_element(building, 'IfcSite').GlobalId

    def get_project_name_from_building(self, building):
        project = self.get_parent_spatial_element(building, 'IfcProject')
        if project.Name:
            return project.Name
        self.logger.error('The project name is empty for {}'.format(project))
        return 'n/a'

    def get_site_name_from_building(self, building):
        site = self.get_parent_spatial_element(building, 'IfcSite')
        if site.Name:
            return site.Name
        self.logger.error('The site name is empty for {}'.format(site))
        return 'n/a'

    def get_units_from_building(self, building):
        return self.get_parent_spatial_element(building, 'IfcProject').UnitsInContext.Units

    def get_parent_spatial_element(self, child, name):
        for relationship in child.Decomposes:
            if relationship.RelatingObject.is_a(name):
                return relationship.RelatingObject
            return self.get_parent_spatial_element(relationship.RelatingObject, name)
        return None

    def get_category_from_object(self, object, picklist):
        class_identification = None
        class_name = None
        for association in object.HasAssociations:
            if not association.is_a('IfcRelAssociatesClassification'):
                continue
            if not association.RelatingClassification.is_a('IfcClassificationReference'):
                continue
            if self.file.schema == 'IFC2X3':
                class_identification = association.RelatingClassification.ItemReference
            else:
                class_identification = association.RelatingClassification.Identification
            class_name = association.RelatingClassification.Name
            break
        if not class_identification or class_name:
            self.logger.error('The classification has invalid identification and name for {}'.format(object))
        result = '{}:{}'.format(class_identification, class_name)
        self.picklists[picklist].append(result)
        return result
        # The responsibility matrix lists a fallback, but it is a very
        # cumbersome check, and so it is not implemented here.

    def get_name_from_person(self, person, attribute):
        name = getattr(person, attribute)
        if not name or not name.isalpha():
            self.logger.warning('The person\'s {} seems to be badly formatted ("{}") for {}'.format(attribute, name, person))
        return name if name else 'n/a'

    def get_lines_from_address(self, address):
        result = self.get_attribute_from_address(address, 'AddressLines')
        if isinstance(result, tuple):
            return ', '.join(result)
        return result

    def get_attribute_from_address(self, address, attribute):
        result = getattr(address, attribute)
        if not result:
            self.logger.warning('The address {} seems to not exist for {}'.format(attribute, address))
            return 'n/a'
        return result

    def get_email_from_history(self, history):
        person = history.OwningUser.ThePerson
        organisation = history.OwningUser.TheOrganization
        email = self.get_email_from_person_or_organisation(person)
        if email:
            return email

        email = self.get_email_from_person_or_organisation(organisation)
        if email:
            return email

        given_name = person.GivenName if person.GivenName else "unknown"
        family_name = person.FamilyName if person.FamilyName else "unknown"
        organisation_name = organisation.Name if organisation.Name else "unknown"

        if given_name == 'unknown' \
            and family_name == 'unknown' \
            and organisation_name == 'unknown':
            self.logger.error('No primary key could be determined from {}'.format(history))

        return '{}{}@{}'.format(given_name, family_name, organisation_name)

    def get_postal_address_from_history(self, history):
        for address in (history.OwningUser.ThePerson.Addresses or []):
            if address.is_a('IfcPostalAddress'):
                return address
        for address in (history.OwningUser.TheOrganization.Addresses or []):
            if address.is_a('IfcPostalAddress'):
                return address
        return self.file.createIfcPostalAddress()

    def get_category_from_history(self, history):
        roles = []
        both = history.OwningUser
        person = both.ThePerson
        organisation = both.TheOrganization
        both_roles = list(both.Roles) if both.Roles else []
        person_roles = list(person.Roles) if person.Roles else []
        organisation_roles = list(organisation.Roles) if organisation.Roles else []
        for role in (both_roles + person_roles + organisation_roles):
            roles.append(self.get_role(role))
        result = ','.join(set(roles))
        if not result:
            self.logger.error('No roles could be found for {}'.format(history))
            return
        self.picklists['Category-Role'].append(result)
        return result

    def get_phone_from_history(self, history):
        person = history.OwningUser.ThePerson
        organisation = history.OwningUser.TheOrganization
        phone = self.get_phone_from_person_or_organisation(person)
        if phone:
            return phone
        phone = self.get_phone_from_person_or_organisation(organisation)
        if phone:
            return phone
        return 'n/a'

    def get_ext_object_from_history(self, history):
        result = history.OwningUser.is_a()
        self.picklists['objType'].append(result)
        return result

    def get_department_from_history(self, history):
        organisation = history.OwningUser.TheOrganization
        department = self.get_internal_location_from_organisation(organisation)
        if department:
            return department
        last_department = None
        for relationship in organisation.Relates:
            for related_organisation in relationship.RelatedOrganizations:
                department = self.get_internal_location_from_organisation(related_organisation)
                if department:
                    last_department = department
        if last_department:
            return last_department
        return history.OwningUser.TheOrganization.Name or 'n/a'

    def get_internal_location_from_organisation(self, organisation):
        for address in (organisation.Addresses or []):
            if address.is_a('IfcPostalAddress'):
                return address.InternalLocation
        self.logger.warning('An internal location was not found for {}'.format(organisation))

    def get_role(self, role):
        if role.Role == 'USERDEFINED':
            return role.UserDefinedRole
        return role.Role

    def get_phone_from_person_or_organisation(self, person_or_org):
        for address in (person_or_org.Addresses or []):
            if address.is_a('IfcTelecomAddress'):
                return address.TelephoneNumbers[0]
        self.logger.warning('A phone was not found for {}'.format(person_or_org))

    def get_email_from_person_or_organisation(self, person_or_org):
        for address in (person_or_org.Addresses or []):
            if address.is_a('IfcTelecomAddress'):
                return address.ElectronicMailAddresses[0]
        self.logger.warning('An email address was not found for {}'.format(person_or_org))

class CobieWriter():
    def __init__(self, parser, filename=None):
        self.filename = filename
        self.parser = parser
        self.sheets = []
        self.sheet_data = {}
        self.colours = {
            'r': 'fdff8e', # Required
            'i': 'fdcd94', # Internal reference
            'e': 'cd95ff', # External reference
            'o': 'cdffc8', # Optional
            's': 'c0c0c0', # Secondary information
            'p': '9ccaff', # Project specific
            'n': '000000' # Not used
            }

    def write(self):
        self.sheets = ['Contact', 'Facility', 'Floor', 'Space', 'Zone', 'Type',
            'Component', 'System', 'Assembly', 'Connection', 'Spare',
            'Resource', 'Job', 'Impact', 'Document', 'Attribute', 'Coordinate',
            'Issue']
        self.write_data('Contact', self.parser.contacts, 'Email',
            ['Email', 'CreatedBy', 'CreatedOn', 'Category', 'Company',
            'Phone', 'ExtSystem', 'ExtObject', 'ExtIdentifier',
            'Department', 'OrganizationCode', 'GivenName', 'FamilyName',
            'Street', 'PostalBox', 'Town', 'StateRegion', 'PostalCode',
            'Country'], 'ririrreeeoooooooooo')
        self.write_data('Facility', self.parser.facilities, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'ProjectName',
            'SiteName', 'LinearUnits', 'AreaUnits', 'VolumeUnits', 'CostUnit',
            'AreaMeasurement', 'ExternalSystem', 'ExternalProjectObject',
            'ExternalProjectIdentifier', 'ExternalSiteObject',
            'ExternalSiteIdentifier', 'ExternalFacilityObject',
            'ExternalFacilityIdentifier', 'Description', 'ProjectDescription',
            'SiteDescription', 'Phase'], 'ririrriiiireeeeeeeoooo')
        self.write_data('Floor', self.parser.floors, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'ExtSystem',
            'ExtObject', 'ExtIdentifier', 'Description', 'Elevation', 'Height'], 'ririeeeooo')
        self.write_data('Space', self.parser.spaces, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'FloorName',
            'Description', 'ExtSystem', 'ExtObject', 'ExtIdentifier', 'RoomTag',
            'UsableHeight', 'GrossArea', 'NetArea'], 'ririireeeoooo')
        self.write_data('Zone', self.parser.zones, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'SpaceNames',
            'ExtSystem', 'ExtObject', 'ExtIdentifier', 'Description',], 'ririieeeo')
        self.write_data('Type', self.parser.types, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'Description',
            'AssetType', 'Manufacturer', 'ModelNumber',
            'WarrantyGuarantorParts', 'WarrantyDurationParts',
            'WarrantyGuarantorLabor', 'WarrantyDurationLabor',
            'WarrantyDurationUnit', 'ExtSystem', 'ExtObject', 'ExtIdentifier',
            'ReplacementCost', 'ExpectedLife', 'DurationUnit', 'NominalLength',
            'NominalWidth', 'NominalHeight', 'ModelReference', 'Shape', 'Size',
            'Color', 'Finish', 'Grade', 'Material', 'Constituents', 'Features',
            'AccessibilityPerformance', 'CodePerformance',
            'SustainabilityPerformance',], 'riririoooooooeeeooooooooooooooooooo')
        self.write_data('Component', self.parser.components, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'TypeName', 'Space',
            'Description', 'ExtSystem', 'ExtObject', 'ExtIdentifier',
            'SerialNumber', 'InstallationDate', 'WarrantyStartDate',
            'TagNumber', 'BarCode', 'AssetIdentifier',], 'ririireeeoooooo')
        self.write_data('System', self.parser.systems, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'ComponentNames',
            'ExtSystem', 'ExtObject', 'ExtIdentifier', 'Description',], 'ririieeeo')
        self.write_data('Assembly', self.parser.assemblies, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'SheetName', 'ParentName',
            'ChildNames', 'AssemblyType', 'ExtSystem', 'ExtObject',
            'ExtIdentifier', 'Description',], 'rirrrrreeeo')
        self.write_data('Connection', self.parser.connections, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'ConnectionType', 'SheetName',
            'RowName1', 'RowName2', 'RealizingElement', 'PortName1',
            'PortName2', 'ExtSystem', 'ExtObject', 'ExtIdentifier',
            'Description',], 'ririiiiiiieeeo')
        self.write_data('Spare', self.parser.spares, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'TypeName',
            'Suppliers', 'ExtSystem', 'ExtObject', 'ExtIdentifier',
            'Description', 'SetNumber', 'PartNumber',], 'ririiieeeooo')
        self.write_data('Resource', self.parser.resources, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'ExtSystem',
            'ExtObject', 'ExtIdentifier', 'Description',], 'ririeeeo')
        self.write_data('Job', self.parser.jobs, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'Status', 'TypeName',
            'Description', 'Duration', 'DurationUnit', 'Start', 'TaskStartUnit',
            'Frequency', 'FrequencyUnit', 'ExtSystem', 'ExtObject',
            'ExtIdentifier', 'TaskNumber', 'Priors', 'ResourceNames',], 'ririiirriririeeeoii')
        self.write_data('Impact', self.parser.impacts, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'ImpactType', 'ImpactStage',
            'SheetName', 'RowName', 'Value', 'Unit', 'LeadInTime', 'Duration',
            'LeadOutTime', 'ExtSystem', 'ExtObject', 'ExtIdentifier',
            'Description',], 'ririiiirioooeeeo')
        self.write_data('Document', self.parser.documents, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'ApprovalBy',
            'Stage', 'SheetName', 'RowName', 'Directory', 'File', 'ExtSystem',
            'ExtObject', 'ExtIdentifier', 'Description', 'Reference',], 'ririiiiirreeeoo')
        self.write_data('Attribute', self.parser.attributes, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'SheetName',
            'RowName', 'Value', 'Unit', 'ExtSystem', 'ExtObject',
            'ExtIdentifier', 'Description', 'AllowedValues',], 'ririiirreeeoo')
        self.write_data('Coordinate', self.parser.coordinates, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Category', 'SheetName',
            'RowName', 'CoordinateXAxis', 'CoordinateYAxis', 'CoordinateZAxis',
            'ExtSystem', 'ExtObject', 'ExtIdentifier', 'ClockwiseRotation',
            'ElevationalRotation', 'YawRotation',], 'ririiooooeeeooo')
        self.write_data('Issue', self.parser.issues, 'Name',
            ['Name', 'CreatedBy', 'CreatedOn', 'Type', 'Risk', 'Chance',
            'Impact', 'SheetName1', 'RowName1', 'SheetName2', 'RowName2',
            'Description', 'Owner', 'Mitigation', 'ExtSystem', 'ExtObject',
            'ExtIdentifier',], 'ririooooooooooeee')

    def write_data(self, sheet, data, primary_key, fieldnames, colours):
        self.sheet_data[sheet] = {
            'headers': fieldnames,
            'colours': colours,
            'rows': []
        }
        for name, row in data.items():
            row[primary_key] = name
            values = []
            for fieldname in fieldnames:
                values.append(row[fieldname])
            self.sheet_data[sheet]['rows'].append(values)


class CobieCsvWriter(CobieWriter):
    def write(self):
        import csv
        super().write()
        for sheet, data in self.sheet_data.items():
            with open(os.path.join(self.filename, '{}.csv'.format(sheet)), 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(data['headers'])
                for row in data['rows']:
                    writer.writerow(row)


class CobieXlsWriter(CobieWriter):
    def write(self):
        from xlsxwriter import Workbook
        super().write()
        self.workbook = Workbook(self.filename + '.xlsx')

        self.cell_formats = {}
        for key, value in self.colours.items():
            self.cell_formats[key] = self.workbook.add_format()
            self.cell_formats[key].set_bg_color(value)

        for sheet in self.sheets:
            self.write_worksheet(sheet)
        self.workbook.close()

    def write_worksheet(self, name):
        worksheet = self.workbook.add_worksheet(name)
        r = 0
        c = 0
        for header in self.sheet_data[name]['headers']:
            cell = worksheet.write(r, c, header, self.cell_formats['s'])
            c += 1
        c = 0
        r += 1
        for row in self.sheet_data[name]['rows']:
            c = 0
            for col in row:
                cell = worksheet.write(r, c, col, self.cell_formats[self.sheet_data[name]['colours'][c]])
                c += 1
            r += 1


class CobieOdsWriter(CobieWriter):
    def write(self):
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.style import Style, TableCellProperties
        super().write()
        self.doc = OpenDocumentSpreadsheet()

        self.cell_formats = {}
        for key, value in self.colours.items():
            style = Style(name=key, family='table-cell')
            style.addElement(TableCellProperties(backgroundcolor='#' + value))
            self.doc.automaticstyles.addElement(style)
            self.cell_formats[key] = style

        for sheet in self.sheets:
            self.write_table(sheet)
        self.doc.save(self.filename, True)

    def write_table(self, name):
        from odf.table import Table, TableRow, TableCell
        from odf.text import P

        table = Table(name=name)
        tr = TableRow()
        for header in self.sheet_data[name]['headers']:
            tc = TableCell(valuetype='string', stylename='s')
            tc.addElement(P(text=header))
            tr.addElement(tc)
        table.addElement(tr)
        for row in self.sheet_data[name]['rows']:
            tr = TableRow()
            c = 0
            for col in row:
                tc = TableCell(valuetype='string', stylename=self.sheet_data[name]['colours'][c])
                tc.addElement(P(text=col))
                tr.addElement(tc)
                c += 1
            table.addElement(tr)
        self.doc.spreadsheet.addElement(table)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Converts COBie IFC MVD into its spreadsheet equivalent')
    parser.add_argument('input', type=str, help='Specify an IFC file to process')
    parser.add_argument('output', type=str, help='The output directory for CSV or filename for other formats')
    parser.add_argument(
        '-l',
        '--log',
        type=str,
        help='Specify where errors should be logged',
        default='process.log')
    parser.add_argument(
        '-f',
        '--format',
        type=str,
        help='Choose which format to export in (csv/xlsx)',
        default='csv')
    args = vars(parser.parse_args())

    print('Processing IFC file ...')

    start = time.time()
    logging.basicConfig(
        filename=args['log'],
        filemode='a', level=logging.DEBUG)
    logger = logging.getLogger('IFCtoCOBie')
    logger.info('Starting conversion')
    parser = IfcCobieParser(logger)
    parser.parse(args['input'])

    print('Generating reports ...')

    if args['format'] == 'xlsx':
        writer = CobieXlsWriter(parser, args['output'])
    elif args['format'] == 'ods':
        writer = CobieOdsWriter(parser, args['output'])
    else:
        writer = CobieCsvWriter(parser, args['output'])
    writer.write()

    logger.info('Finished conversion in {}s'.format(time.time() - start))
    print('# All reports are complete :-)')
