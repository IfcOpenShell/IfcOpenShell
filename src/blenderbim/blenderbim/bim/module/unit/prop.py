import bpy
import ifcopenshell
import ifcopenshell.util.schema
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.prop import StrProperty, Attribute
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


unitclasses_enum = []


def purge():
    global unitclasses_enum
    unitclasses_enum = []


def getUnitClasses(self, context):
    global unitclasses_enum
    if not len(unitclasses_enum) and IfcStore.get_file():
        declarations = ifcopenshell.util.schema.get_subtypes(IfcStore.get_schema().declaration_by_name("IfcNamedUnit"))
        unitclasses_enum.extend([(c, c, "") for c in sorted([d.name() for d in declarations])])
        unitclasses_enum.extend([("IfcDerivedUnit", "IfcDerivedUnit", ""), ("IfcMonetaryUnit", "IfcMonetaryUnit", "")])
    return unitclasses_enum


class Unit(PropertyGroup):
    name: StringProperty(name="Name")
    unit_type: StringProperty(name="Unit Type")
    is_assigned: BoolProperty(name="Is Assigned")
    icon: StringProperty(name="Icon")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMUnitProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    units: CollectionProperty(name="Units", type=Unit)
    active_unit_index: IntProperty(name="Active Unit Index")
    active_unit_id: IntProperty(name="Active Unit Id")
    unit_classes: EnumProperty(items=getUnitClasses, name="Unit Classes")
    unit_attributes: CollectionProperty(name="Unit Attributes", type=Attribute)
