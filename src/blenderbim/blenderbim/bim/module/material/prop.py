import bpy
import blenderbim.bim.schema  # refactor
from ifcopenshell.api.material.data import Data
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

materials_enum = []
materialtypes_enum = []
profileclasses_enum = []
parameterizedprofileclasses_enum = []


def getProfileClasses(self, context):
    global profileclasses_enum
    if len(profileclasses_enum) == 0 and IfcStore.get_schema():
        profileclasses_enum.clear()
        profileclasses_enum = [
            (t.name(), t.name(), "") for t in IfcStore.get_schema().declaration_by_name("IfcProfileDef").subtypes()
        ]
    return profileclasses_enum


def getParameterizedProfileClasses(self, context):
    global parameterizedprofileclasses_enum
    if len(parameterizedprofileclasses_enum) == 0 and IfcStore.get_schema():
        parameterizedprofileclasses_enum.clear()
        parameterizedprofileclasses_enum = [
            (t.name(), t.name(), "")
            for t in IfcStore.get_schema().declaration_by_name("IfcParameterizedProfileDef").subtypes()
        ]
    return parameterizedprofileclasses_enum


def getMaterials(self, context):
    global materials_enum
    if len(materials_enum) == 0 and IfcStore.get_file():
        materials_enum.clear()
        materials_enum = [(str(m_id), m["Name"], "") for m_id, m in Data.materials.items()]
    return materials_enum


def getMaterialTypes(self, context):
    global materialtypes_enum
    if len(materialtypes_enum) == 0 and IfcStore.get_file():
        material_types = [
            "IfcMaterial",
            "IfcMaterialConstituentSet",
            "IfcMaterialLayerSet",
            "IfcMaterialLayerSetUsage",
            "IfcMaterialProfileSet",
            "IfcMaterialList",
        ]
        if IfcStore.get_file().schema == "IFC2X3":
            material_types = ["IfcMaterial", "IfcMaterialLayerSet", "IfcMaterialLayerSetUsage", "IfcMaterialList"]
        materialtypes_enum.clear()
        materialtypes_enum = [(m, m, "") for m in material_types]
    return materialtypes_enum


class BIMObjectMaterialProperties(PropertyGroup):
    material_type: EnumProperty(items=getMaterialTypes, name="Material Type")
    material: EnumProperty(items=getMaterials, name="Material")
    is_editing: BoolProperty(name="Is Editing", default=False)
    material_set_attributes: CollectionProperty(name="Material Set Attributes", type=Attribute)
    active_material_set_item_id: IntProperty(name="Active Material Set ID")
    material_set_item_attributes: CollectionProperty(name="Material Set Item Attributes", type=Attribute)
    material_set_item_profile_attributes: CollectionProperty(name="Material Set Item Profile Attributes", type=Attribute)
    material_set_item_material: EnumProperty(items=getMaterials, name="Material")
    profile_classes: EnumProperty(items=getProfileClasses, name="Profile Classes")
    parameterized_profile_classes: EnumProperty(
        items=getParameterizedProfileClasses, name="Parameterized Profile Classes"
    )
