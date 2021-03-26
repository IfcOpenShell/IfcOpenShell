import bpy
import ifcopenshell.util.type
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.ifc import IfcStore
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

applicable_types_enum = []
relating_types_enum = []
type_classes_enum = []
available_types_enum = []


def getIfcTypes(self, context):
    global type_classes_enum
    file = IfcStore.get_file()
    if len(type_classes_enum) < 1 and file:
        declaration = IfcStore.get_schema().declaration_by_name("IfcElementType")

        def get_classes(declaration):
            results = []
            if not declaration.is_abstract():
                results.append(declaration.name())
            for subtype in declaration.subtypes():
                results.extend(get_classes(subtype))
            return results

        classes = get_classes(declaration)
        type_classes_enum.extend([(c, c, "") for c in sorted(classes)])
    return type_classes_enum


def getAvailableTypes(self, context):
    global available_types_enum
    if len(available_types_enum) < 1:
        elements = IfcStore.get_file().by_type(self.ifc_class)
        available_types_enum.extend((str(e.id()), e.Name, "") for e in elements)
    return available_types_enum


def updateTypeInstanceIfcClass(self, context):
    global available_types_enum
    available_types_enum.clear()


def getApplicableTypes(self, context):
    global applicable_types_enum
    if len(applicable_types_enum) < 1:
        element = IfcStore.get_file().by_id(context.active_object.BIMObjectProperties.ifc_definition_id)
        types = ifcopenshell.util.type.get_applicable_types(element.is_a(), schema=IfcStore.get_file().schema)
        applicable_types_enum.extend((t, t, "") for t in types)
    return applicable_types_enum


def getRelatingTypes(self, context):
    global relating_types_enum
    if len(relating_types_enum) < 1:
        elements = IfcStore.get_file().by_type(context.active_object.BIMTypeProperties.relating_type_class)
        relating_types_enum.extend((str(e.id()), e.Name, "") for e in elements)
    return relating_types_enum


def updateTypeDropdowns(self, context):
    global applicable_types_enum
    global relating_types_enum
    applicable_types_enum.clear()
    relating_types_enum.clear()


class BIMTypeProperties(PropertyGroup):
    is_editing_type: BoolProperty(name="Is Editing Type", update=updateTypeDropdowns)
    relating_type_class: EnumProperty(items=getApplicableTypes, name="Relating Type Class")
    relating_type: EnumProperty(items=getRelatingTypes, name="Relating Type")
    # This is purely a UX thing
    blank_relating_type: EnumProperty(items=[("None", "No Types Found", "")], name="Relating Type")
