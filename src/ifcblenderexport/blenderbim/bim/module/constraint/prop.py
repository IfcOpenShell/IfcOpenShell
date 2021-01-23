import bpy
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


class Constraint(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMConstraintProperties(PropertyGroup):
    constraint_attributes: CollectionProperty(name="Constraint Attributes", type=Attribute)
    active_constraint_id: IntProperty(name="Active Constraint Id")
    constraints: CollectionProperty(name="Constraints", type=Constraint)
    active_constraint_index: IntProperty(name="Active Constraint Index")
    is_editing: StringProperty(name="Is Editing")


class BIMObjectConstraintProperties(PropertyGroup):
    is_adding: StringProperty(name="Is Adding")
    available_constraint_types: EnumProperty(
        items=[(c, c, "") for c in ["IfcObjective"]], name="Available Constraint Types"
    )
