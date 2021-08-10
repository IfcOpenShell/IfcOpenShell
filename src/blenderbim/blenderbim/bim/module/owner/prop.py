import bpy
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.owner.data import Data
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

_persons_enum = []
_organisations_enum = []

def purge():
    global _persons_enum
    global _organisations_enum
    _persons_enum.clear()
    _organisations_enum.clear()

def getPersons(self, context):
    global _persons_enum
    if not Data.is_loaded:
        Data.load(IfcStore.get_file())
    _persons_enum.clear()
    for ifc_id, person in Data.people.items():
        if "Id" in person:
            identifier = person["Id"] or ""
        else:
            identifier = person["Identification"] or ""
        _persons_enum.append((str(ifc_id), identifier, ""))
    return _persons_enum


def getOrganisations(self, context):
    global _organisations_enum
    if not Data.is_loaded:
        Data.load(IfcStore.get_file())
    _organisations_enum.clear()
    for ifc_id, organisation in Data.organisations.items():
        _organisations_enum.append((str(ifc_id), organisation["Name"], ""))
    return _organisations_enum


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
    address_lines: CollectionProperty(type=StrProperty, name="Address")
    postal_box: StringProperty(name="Postal Box")
    town: StringProperty(name="Town")
    region: StringProperty(name="Region")
    postal_code: StringProperty(name="Postal Code")
    country: StringProperty(name="Country")

    telephone_numbers: CollectionProperty(type=StrProperty, name="Telephone Numbers")
    facsimile_numbers: CollectionProperty(type=StrProperty, name="Facsimile Numbers")
    pager_number: StringProperty(name="Pager Number")
    electronic_mail_addresses: CollectionProperty(type=StrProperty, name="Emails")
    www_home_page_url: StringProperty(name="Website")
    messaging_ids: CollectionProperty(type=StrProperty, name="IMs")


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
    middle_names: CollectionProperty(type=StrProperty, name="Middle Names")
    prefix_titles: CollectionProperty(type=StrProperty, name="Prefixes")
    suffix_titles: CollectionProperty(type=StrProperty, name="Suffixes")


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
