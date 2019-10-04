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
                'CreatedOn': datetime.datetime.fromtimestamp(history.CreationDate).isoformat(),
                'Category': self.get_category_from_history(history),
                'Company': history.OwningUser.TheOrganization.Name or 'n/a',
                'Phone': self.get_phone_from_history(history),
                'ExtSystem': history.OwningApplication.ApplicationFullName,
                'ExtObject': self.get_ext_object_from_history(history),
                'ExtIdentifier': history.OwningUser.ThePerson.Id if self.file.schema == 'IFC2X3' else history.OwningUser.ThePerson.Identification,
                'Department': self.get_department_from_history(history),
                'OrganizationCode': (history.OwningUser.TheOrganization.Id or 'n/a') if self.file.schema == 'IFC2X3' else (history.OwningUser.TheOrganization.Identification or 'n/a'),
                'GivenName': history.OwningUser.ThePerson.GivenName or 'n/a',
                'FamilyName': history.OwningUser.ThePerson.FamilyName or 'n/a',
                'Street': postal_address.AddressLines or 'n/a',
                'PostalBox': postal_address.PostalBox or 'n/a',
                'Town': postal_address.Town or 'n/a',
                'StateRegion': postal_address.Region or 'n/a',
                'PostalCode': postal_address.PostalCode or 'n/a',
                'Country': postal_address.Country or 'n/a'
                }

    def get_facilities(self):
        buildings = self.file.by_type('IfcBuilding')
        for building in buildings:
            if not building.Name:
                logging.error('A building name was not found for {}'.format(building))
                continue

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
            logging.warning('No roles could be found for {}'.format(history))
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
