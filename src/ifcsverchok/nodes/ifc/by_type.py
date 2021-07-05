import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty, EnumProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


def get_ifc_products(self, context):
    ifc_products = getattr(self, "ifc_products", [])
    file = self.inputs["file"].sv_get()[0][0]
    if not file:
        return []
    if ifc_products and file:
        return ifc_products
    ifc_products = []
    ifc_products.extend(
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
        ifc_products[2] = ("IfcSpatialStructureElement", "IfcSpatialStructureElement", "")
    return ifc_products


def update_ifc_products(self, context):
    if hasattr(self, "ifc_classes"):
        self.ifc_classes.clear()


def get_ifc_classes(self, context):
    ifc_classes = getattr(self, "ifc_classes", [])
    if ifc_classes:
        return self.ifc_classes
    file = self.inputs["file"].sv_get()[0][0]
    if not file:
        return []
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(file.schema)
    declaration = schema.declaration_by_name(self.ifc_product)

    def get_classes(declaration):
        results = []
        if not declaration.is_abstract():
            results.append(declaration.name())
        for subtype in declaration.subtypes():
            results.extend(get_classes(subtype))
        return results

    classes = get_classes(declaration)
    ifc_classes.extend([(c, c, "") for c in sorted(classes)])
    return ifc_classes


class SvIfcByType(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcByType"
    bl_label = "IFC By Type"
    file: StringProperty(name="file", update=updateNode)
    ifc_product: EnumProperty(items=get_ifc_products, name="Products", update=update_ifc_products)
    ifc_class: EnumProperty(items=get_ifc_classes, name="Class", update=updateNode)
    custom_ifc_class: StringProperty(name="Custom Ifc Class", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "ifc_product").prop_name = "ifc_product"
        self.inputs.new("SvStringsSocket", "ifc_class").prop_name = "ifc_class"
        self.inputs.new("SvStringsSocket", "custom_ifc_class").prop_name = "custom_ifc_class"
        self.outputs.new("SvStringsSocket", "entity")

    def process(self):
        file = self.inputs["file"].sv_get()[0][0]
        if file:
            self.ifc_products = get_ifc_products(self, bpy.context)
            self.ifc_classes = get_ifc_classes(self, bpy.context)
        self.sv_input_names = ["file", "ifc_product", "ifc_class", "custom_ifc_class"]
        super().process()

    def process_ifc(self, file, ifc_product, ifc_class, custom_ifc_class):
        if custom_ifc_class:
            self.outputs["entity"].sv_set([file.by_type(custom_ifc_class)])
        else:
            self.outputs["entity"].sv_set([file.by_type(ifc_class)])


def register():
    bpy.utils.register_class(SvIfcByType)


def unregister():
    bpy.utils.unregister_class(SvIfcByType)
