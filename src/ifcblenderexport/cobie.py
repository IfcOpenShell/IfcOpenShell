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
        self.picklists = {
            'Category-Role': [],
            'Category-Facility': [],
            'objType': []
            }

    def convert(self):
        self.file = ifcopenshell.open('C:/cygwin64/home/moud308/Projects/ifc2cobie/input.ifc')
        self.get_contacts()
        self.get_facilities()

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
            building_name = self.get_building_name(building)
            units = self.get_units_from_building(building)
            self.facilities[building_name] = {
                'CreatedBy': self.get_email_from_history(building.OwnerHistory),
                'CreatedOn': datetime.datetime.fromtimestamp(building.OwnerHistory.CreationDate).isoformat() if building.OwnerHistory.CreationDate else date.datetime.fromtimestamp(-2177452801).isoformat(),
                'Category': self.get_category_from_building(building),
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
                'Description': self.get_object_attribte(building, 'Description'),
                'ProjectDescription': self.get_object_attribte(self.get_parent_spatial_element(building, 'IfcProject'), 'Description'),
                'SiteDescription': self.get_object_attribte(self.get_parent_spatial_element(building, 'IfcSite'), 'Description'),
                'Phase': self.get_object_attribte(self.get_parent_spatial_element(building, 'IfcProject'), 'Phase')
                }

    def get_object_attribte(self, object, attribute):
        result = getattr(object, attribute)
        if result:
            return result
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

    def get_building_name(self, building):
        if not building.Name:
            logging.error('A building name was not found for {}'.format(building))
            return 'Building{}'.format(building.id())
        return building.Name

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

    def get_category_from_building(self, building):
        class_identification = None
        class_name = None
        for association in building.HasAssociations:
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
            logging.error('The classification has invalid identification and name for {}'.format(building))
        result = '{}:{}'.format(class_identification, class_name)
        self.picklists['Category-Facility'].append(result)
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
print('# Finished conversion in {}s'.format(time.time() - start))
