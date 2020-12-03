import bpy
import ifcopenshell
import ifcopenshell.util.selector
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcByQuery(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcByQuery"
    bl_label = "IFC By Query"
    file: StringProperty(name="file", update=updateNode)
    query: StringProperty(name="query", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "query").prop_name = "query"
        self.outputs.new("SvStringsSocket", "entity")

    def process(self):
        self.sv_input_names = ["file", "query"]
        super().process()

    def process_ifc(self, file, query):
        selector = ifcopenshell.util.selector.Selector()
        self.outputs["entity"].sv_set([selector.parse(file, query)])


def register():
    bpy.utils.register_class(SvIfcByQuery)


def unregister():
    bpy.utils.unregister_class(SvIfcByQuery)
