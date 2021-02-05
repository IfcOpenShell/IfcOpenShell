import bpy
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.module.owner.data import Data
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


def getPersons(self, context):
    if not Data.is_loaded:
        Data.load()
    results = []
    for ifc_id, person in Data.people.items():
        if "Id" in person:
            identifier = person["Id"] or ""
        else:
            identifier = person["Identification"] or ""
        results.append((str(ifc_id), identifier, ""))
    return results


def getOrganisations(self, context):
    if not Data.is_loaded:
        Data.load()
    results = []
    for ifc_id, organisation in Data.organisations.items():
        results.append((str(ifc_id), organisation["Name"], ""))
    return results


class Address(PropertyGroup):
    name: StringProperty(name="Name", default="IfcPostalAddress")  # Stores IfcPostalAddress or IfcTelecomAddress
    purpose: EnumProperty(
        items=[
            ("None", "None", ""),
            ("OFFICE", "OFFICE", "An office address."),
            ("SITE", "SITE", "A site address."),
            ("HOME", "HOME", "A home address."),
            ("DISTRIBUTIONPOINT", "DISTRIBUTIONPOINT", "A postal distribution point address."),
            ("USERDEFINED", "USERDEFINED", "A user defined address type to be provided."),
        ],
        name="Purpose",
    )
    description: StringProperty(name="Description")
    user_defined_purpose: StringProperty(name="Custom Purpose")

    internal_location: StringProperty(name="Internal Location")
    address_lines: StringProperty(name="Address")
    postal_box: StringProperty(name="Postal Box")
    town: StringProperty(name="Town")
    region: StringProperty(name="Region")
    postal_code: StringProperty(name="Postal Code")
    country: StringProperty(name="Country")

    telephone_numbers: StringProperty(name="Telephone Numbers")
    facsimile_numbers: StringProperty(name="Facsimile Numbers")
    pager_number: StringProperty(name="Pager Number")
    electronic_mail_addresses: StringProperty(name="Emails")
    www_home_page_url: StringProperty(name="Websites")
    messaging_ids: StringProperty(name="IMs")


class Role(PropertyGroup):
    name: EnumProperty(
        items=[
            ("SUPPLIER", "SUPPLIER", ""),
            ("MANUFACTURER", "MANUFACTURER", ""),
            ("CONTRACTOR", "CONTRACTOR", ""),
            ("SUBCONTRACTOR", "SUBCONTRACTOR", ""),
            ("ARCHITECT", "ARCHITECT", ""),
            ("STRUCTURALENGINEER", "STRUCTURALENGINEER", ""),
            ("COSTENGINEER", "COSTENGINEER", ""),
            ("CLIENT", "CLIENT", ""),
            ("BUILDINGOWNER", "BUILDINGOWNER", ""),
            ("BUILDINGOPERATOR", "BUILDINGOPERATOR", ""),
            ("MECHANICALENGINEER", "MECHANICALENGINEER", ""),
            ("ELECTRICALENGINEER", "ELECTRICALENGINEER", ""),
            ("PROJECTMANAGER", "PROJECTMANAGER", ""),
            ("FACILITIESMANAGER", "FACILITIESMANAGER", ""),
            ("CIVILENGINEER", "CIVILENGINEER", ""),
            ("COMMISSIONINGENGINEER", "COMMISSIONINGENGINEER", ""),
            ("ENGINEER", "ENGINEER", ""),
            ("OWNER", "OWNER", ""),
            ("CONSULTANT", "CONSULTANT", ""),
            ("CONSTRUCTIONMANAGER", "CONSTRUCTIONMANAGER", ""),
            ("FIELDCONSTRUCTIONMANAGER", "FIELDCONSTRUCTIONMANAGER", ""),
            ("RESELLER", "RESELLER", ""),
            ("USERDEFINED", "USERDEFINED", ""),
        ],
        name="Name",
    )
    user_defined_role: StringProperty(name="Custom Role")
    description: StringProperty(name="Description")


class Organisation(PropertyGroup):
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")


class Person(PropertyGroup):
    name: StringProperty(name="Identification")
    family_name: StringProperty(name="Family Name")
    given_name: StringProperty(name="Given Name")
    middle_names: StringProperty(name="Middle Names")
    prefix_titles: StringProperty(name="Prefixes")
    suffix_titles: StringProperty(name="Suffixes")


class BIMOwnerProperties(PropertyGroup):
    person: PointerProperty(type=Person)
    active_person_id: IntProperty(name="Active Person Id")
    organisation: PointerProperty(type=Organisation)
    active_organisation_id: IntProperty(name="Active Organisation Id")
    role: PointerProperty(type=Role)
    active_role_id: IntProperty(name="Active Role Id")
    address: PointerProperty(type=Address)
    active_address_id: IntProperty(name="Active Address Id")
    user_person: EnumProperty(items=getPersons, name="Person")
    user_organisation: EnumProperty(items=getOrganisations, name="Organisation")
