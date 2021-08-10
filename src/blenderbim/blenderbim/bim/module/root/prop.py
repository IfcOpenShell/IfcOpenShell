import bpy
import ifcopenshell
import ifcopenshell.util.schema
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

products_enum = []
classes_enum = []
types_enum = []


def purge():
    global products_enum
    global classes_enum
    global types_enum
    products_enum = []
    classes_enum = []
    types_enum = []


def getIfcPredefinedTypes(self, context):
    global types_enum
    file = IfcStore.get_file()
    if len(types_enum) < 1 and file:
        declaration = IfcStore.get_schema().declaration_by_name(self.ifc_class)
        for attribute in declaration.attributes():
            if attribute.name() == "PredefinedType":
                types_enum.extend(
                    [(e, e, "") for e in attribute.type_of_attribute().declared_type().enumeration_items()]
                )
                break
    return types_enum


def refreshClasses(self, context):
    global classes_enum
    classes_enum.clear()
    enum = getIfcClasses(self, context)
    context.scene.BIMRootProperties.ifc_class = enum[0][0]


def refreshPredefinedTypes(self, context):
    global types_enum
    types_enum.clear()
    enum = getIfcPredefinedTypes(self, context)
    context.scene.BIMRootProperties.ifc_predefined_type = enum[0][0]


def getIfcProducts(self, context):
    global products_enum
    file = IfcStore.get_file()
    if len(products_enum) < 1:
        products_enum.extend(
            [
                (e, e, "")
                for e in [
                    "IfcElement",
                    "IfcElementType",
                    "IfcSpatialElement",
                    "IfcGroup",
                    "IfcStructuralItem",
                    "IfcContext",
                    "IfcAnnotation",
                ]
            ]
        )
        if file.schema == "IFC2X3":
            products_enum[2] = ("IfcSpatialStructureElement", "IfcSpatialStructureElement", "")
    return products_enum


def getIfcClasses(self, context):
    global classes_enum
    file = IfcStore.get_file()
    if len(classes_enum) < 1 and file:
        declaration = IfcStore.get_schema().declaration_by_name(context.scene.BIMRootProperties.ifc_product)
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        classes_enum.extend([(c, c, "") for c in sorted([d.name() for d in declarations])])
    return classes_enum


class BIMRootProperties(PropertyGroup):
    ifc_product: EnumProperty(items=getIfcProducts, name="Products", update=refreshClasses)
    ifc_class: EnumProperty(items=getIfcClasses, name="Class", update=refreshPredefinedTypes)
    ifc_predefined_type: EnumProperty(items=getIfcPredefinedTypes, name="Predefined Type", default=None)
    ifc_userdefined_type: StringProperty(name="Userdefined Type")
