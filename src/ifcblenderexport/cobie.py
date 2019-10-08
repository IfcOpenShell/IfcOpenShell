import time
import datetime
import ifcopenshell
import logging
import pprint

class IfcCobieCsv():
    def __init__(self):
        self.file = None
        self.contacts = {}
        self.facilities = {}
        self.floors = {}
        self.spaces = {}
        self.zones = {}
        self.types = {}
        self.components = {}
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
            'objType': []
            }
        self.default_date = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds = -2177452801)).isoformat()

    def convert(self):
        self.file = ifcopenshell.open('C:/cygwin64/home/moud308/Projects/ifc2cobie/input.ifc')
        self.get_contacts()
        self.get_facilities()
        self.get_floors()
        self.get_spaces()
        self.get_zones()
        self.get_types()
        self.get_components()

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
                'Street': self.get_attribute_from_address(postal_address, 'AddressLines'),
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
                'Description': self.get_object_attribute(building, 'Description'),
                'ProjectDescription': self.get_object_attribute(self.get_parent_spatial_element(building, 'IfcProject'), 'Description'),
                'SiteDescription': self.get_object_attribute(self.get_parent_spatial_element(building, 'IfcSite'), 'Description'),
                'Phase': self.get_object_attribute(self.get_parent_spatial_element(building, 'IfcProject'), 'Phase')
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
                'Description': self.get_object_attribute(storey, 'Description'),
                'Elevation': self.get_object_attribute(storey, 'Elevation'),
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
                'FloorName': self.get_object_attribute(self.get_parent_spatial_element(space, 'IfcBuildingStorey'), 'Name', True),
                'Description': self.get_object_attribute(space, 'Description'),
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
                'SpaceNames': self.get_space_names_from_zone(zone),
                'ExtSystem': self.get_ext_system_from_history(zone.OwnerHistory),
                'ExtObject': self.get_ext_object(zone),
                'ExtIdentifier': zone.GlobalId,
                'Description': self.get_object_attribute(zone, 'Description'),
                }

    def get_types(self):
        types = self.file.by_type('IfcTypeObject')
        for type in types:
            is_a_type_asset = False
            for type_asset in self.type_assets:
                if type.is_a(type_asset):
                    is_a_type_asset = True
            if not is_a_type_asset:
                logging.warning('A type which is not an asset was found for {}'.format(type))
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
                'Description': self.get_object_attribute(type, 'Description'),
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
            is_a_component_asset = False
            for asset in self.component_assets:
                if component.is_a(asset):
                    is_a_component_asset = True
            if not is_a_component_asset:
                logging.warning('A component which is not an asset was found for {}'.format(component))
                continue
            component_name = self.get_object_name(component)
            self.components[component_name] = {
                'CreatedBy': self.get_email_from_history(component.OwnerHistory),
                'CreatedOn': self.get_created_on_from_history(component.OwnerHistory),
                'TypeName': self.get_type_name_from_component(component),
                'Space': self.get_space_name_from_component(component),
                'Description': self.get_object_attribute(component, 'Description'),
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

    def get_space_name_from_component(self, component):
        for relationship in component.ContainedInStructure:
            if relationship.RelatingStructure.is_a('IfcSpace') \
                and relationship.RelatingStructure.Name:
                return relationship.RelatingStructure.Name
        logging.error('A related space name could not be determined for {}'.format(component))

    def get_type_name_from_component(self, component):
        if self.file.schema == 'IFC2X3':
            for relationship in component.IsDefinedBy:
                if relationship.is_a('IfcRelDefinesByType') \
                    and relationship.RelatingType.Name:
                    return relationship.RelatingType.Name
        else:
            for relationship in component.IsTypedBy:
                if relationship.RelatingType.Name:
                    return relationship.RelatingType.Name
        logging.error('A related type name could not be determined for {}'.format(component))

    def get_expected_life_from_type(self, type):
        if self.file.schema == 'IFC2X3':
            return self.get_pset_value_from_object(type, 'COBie_ServiceLife', 'ServiceLifeDuration', 'n/a')
        return self.get_pset_value_from_object(type, 'Pset_ServiceLife', 'ServiceLifeDuration', 'n/a')

    def get_contact_pset_value_from_object(self, object, pset_name, property_name):
        result = self.get_pset_value_from_object(object, pset_name, property_name)
        if not result:
            logging.error('No property {} in {} was found for {}'.format(property_name, pset_name, object))
        if result not in self.contacts:
            logging.error('A coresponding {} contact in {} was not found for {}'.format(property_name, pset_name, object))
        return result

    def get_pset_value_from_object(self, object, pset_name, property_name, default=None, picklist=None):
        pset = self.get_pset_from_object(object, pset_name)
        if not pset:
            if picklist:
                self.picklists[picklist].append(default)
            return default
        property = self.get_property_from_pset(pset, property_name, default)
        if picklist:
            self.picklists[picklist].append(property)
        return property

    def get_space_names_from_zone(self, zone):
        spaces = []
        for relationship in zone.IsGroupedBy:
            for space in relationship.RelatedObjects:
                spaces.append(space.Name)
        if spaces:
            return ','.join(spaces)
        logging.error('No spaces were found for {}'.format(zone))

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
            if relationship.RelatingPropertyDefinition.is_a('IfcQuantitySet') \
                and relationship.RelatingPropertyDefinition.Name == name:
                return relationship.RelatingPropertyDefinition
        logging.warning('The qto {} was not found for {}'.format(name, object))

    def get_property_from_qto(self, qto, name, attribute):
        for property in qto.Quantities:
            if property.Name == name:
                return getattr(property, attribute)
        logging.warning('The quantity value {} was not found for {}'.format(name, qto))
        return 'n/a'

    def get_property_from_pset(self, pset, name, default=None):
        for property in pset.HasProperties:
            if property.Name == name:
                return property.NominalValue
        logging.warning('The property {} was not found for {}'.format(name, pset))
        return default

    def get_pset_from_object(self, object, name):
        if object.is_a('IfcTypeObject'):
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
        logging.warning('The pset {} was not found for {}'.format(name, object))

    def get_height_from_storey(self, storey):
        for relationship in storey.IsDefinedBy:
            if not relationship.RelatingPropertyDefinition.is_a('IfcElementQuantity'):
                continue
            for quantity in relationship.RelatingPropertyDefinition.Quantities:
                if quantity.is_a('IfcQuantityLength') \
                    and quantity.LengthValue:
                    return quantity.LengthValue
        logging.warning('A height length value was not found for {}'.format(storey))
        return 'n/a'

    def get_created_on_from_history(self, history):
        if history.CreationDate:
            return datetime.datetime.fromtimestamp(history.CreationDate).isoformat()
        logging.warning('A created on date was not found for {}'.format(history))
        return self.default_date

    def get_object_attribute(self, object, attribute, is_primary_key = False):
        result = getattr(object, attribute)
        if result:
            return result
        if is_primary_key:
            logging.error('The primary key attribute {} was not found for {}'.format(attribute, object))
        else:
            logging.warning('The attribute {} was not found for {}'.format(attribute, object))
        return 'n/a'

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
            logging.error('A primary key name was not found for {}'.format(object))
            return 'Object{}'.format(object.id())
        return object.Name

    def get_area_measurement_from_building(self, building):
        for relationship in building.IsDefinedBy:
            if relationship.RelatingPropertyDefinition.is_a('IfcElementQuantity') \
                and relationship.RelatingPropertyDefinition.MethodOfMeasurement:
                return relationship.RelatingPropertyDefinition.MethodOfMeasurement
        logging.warning('A method of measurement was not defined for {}'.format(building))

    def get_unit_type_from_units(self, units, type):
        for unit in units:
            if unit.UnitType == type:
                if unit.is_a('IfcSIUnit') and unit.Prefix:
                    return '{}{}'.format(unit.Prefix, unit.Name)
                return unit.Name
        logging.error('A unit {} was not defined in this project for {}'.format(type, units))

    def get_monetary_unit_from_units(self, units):
        for unit in units:
            if unit.is_a('IfcMonetaryUnit'):
                return unit.Currency
        logging.error('A monetary unit could not be found for {}'.format(units))

    def get_project_globalid_from_building(self, building):
        return self.get_parent_spatial_element(building, 'IfcProject').GlobalId

    def get_site_globalid_from_building(self, building):
        return self.get_parent_spatial_element(building, 'IfcSite').GlobalId

    def get_project_name_from_building(self, building):
        project = self.get_parent_spatial_element(building, 'IfcProject')
        if project.Name:
            return project.Name
        logging.error('The project name is empty for {}'.format(project))
        return 'n/a'

    def get_site_name_from_building(self, building):
        site = self.get_parent_spatial_element(building, 'IfcSite')
        if site.Name:
            return site.Name
        logging.error('The site name is empty for {}'.format(site))
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
            logging.error('The classification has invalid identification and name for {}'.format(object))
        result = '{}:{}'.format(class_identification, class_name)
        self.picklists[picklist].append(result)
        return result
        # The responsibility matrix lists a fallback, but it is a very
        # cumbersome check, and so it is not implemented here.

    def get_name_from_person(self, person, attribute):
        name = getattr(person, attribute)
        if not name.isalpha():
            logging.warning('The person\'s {} seems to be badly formatted ("{}") for {}'.format(attribute, name, person))
        return name if name else 'n/a'

    def get_attribute_from_address(self, address, attribute):
        result = getattr(address, attribute)
        if not result:
            logging.warning('The address {} seems to not exist for {}'.format(attribute, address))
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

        given_name = person.GivenName if person.GivenName else "uknnown"
        family_name = person.FamilyName if person.FamilyName else "uknnown"
        organisation_name = organisation.Name if organisation.Name else "unknown"

        if given_name == 'unknown' \
            and family_name == 'unknown' \
            and organisation_name == 'unknown':
            logging.error('No primary key could be determined from {}'.format(history))

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
        for role in ((both.Roles or []) + (person.Roles or []) + (organisation.Roles or [])):
            roles.append(self.get_role(role))
        result = ','.join(set(roles))
        if not result:
            logging.error('No roles could be found for {}'.format(history))
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
        logging.warning('An internal location was not found for {}'.format(organisation))

    def get_role(self, role):
        if role.Role == 'USERDEFINED':
            return role.UserDefinedRole
        return role.Role

    def get_phone_from_person_or_organisation(self, person_or_org):
        for address in (person_or_org.Addresses or []):
            if address.is_a('IfcTelecomAddress'):
                return address.TelephoneNumbers[0]
        logging.warning('A phone was not found for {}'.format(person_or_org))

    def get_email_from_person_or_organisation(self, person_or_org):
        for address in (person_or_org.Addresses or []):
            if address.is_a('IfcTelecomAddress'):
                return address.ElectronicMailAddresses[0]
        logging.warning('An email address was not found for {}'.format(person_or_org))

start = time.time()
print('# Starting conversion')
ifc_cobie_csv = IfcCobieCsv()
ifc_cobie_csv.convert()
pprint.pprint(ifc_cobie_csv.contacts)
pprint.pprint(ifc_cobie_csv.facilities)
pprint.pprint(ifc_cobie_csv.floors)
pprint.pprint(ifc_cobie_csv.spaces)
pprint.pprint(ifc_cobie_csv.zones)
pprint.pprint(ifc_cobie_csv.types)
pprint.pprint(ifc_cobie_csv.components)
print('# Finished conversion in {}s'.format(time.time() - start))
