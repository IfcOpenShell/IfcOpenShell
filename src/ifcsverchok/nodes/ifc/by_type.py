import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcByType(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcByType"
    bl_label = "IFC By Type"
    file: StringProperty(name="file", update=updateNode)
    type: StringProperty(name="type", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "type").prop_name = "type"
        self.outputs.new("SvStringsSocket", "entity")

    def process(self):
        self.sv_input_names = ["file", "type"]
        super().process()

    def process_ifc(self, file, type):
        self.outputs["entity"].sv_set([file.by_type(type)])


def register():
    bpy.utils.register_class(SvIfcByType)


def unregister():
    bpy.utils.unregister_class(SvIfcByType)
