import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty, EnumProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from blenderbim.bim.module.root.prop import getIfcClasses, getIfcProducts, refreshClasses, refreshPredefinedTypes


class SvIfcByType(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcByType"
    bl_label = "IFC By Type"
    file: StringProperty(name="file", update=updateNode)
    ifc_product: EnumProperty(items=getIfcProducts, name="Products", update=refreshClasses)
    ifc_class: EnumProperty(items=getIfcClasses, name="Class", update=refreshPredefinedTypes)
    custom_ifc_class: StringProperty(name="Custom Ifc Class", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "ifc_product").prop_name = "ifc_product"
        self.inputs.new("SvStringsSocket", "ifc_class").prop_name = "ifc_class"
        self.inputs.new("SvStringsSocket", "custom_ifc_class").prop_name = "custom_ifc_class"
        self.outputs.new("SvStringsSocket", "entity")

    def process(self):
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
