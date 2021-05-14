import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcGenerateGuid(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcGenerateGuid"
    bl_label = "IFC Generate Guid"

    def sv_init(self, context):
        self.outputs.new("SvStringsSocket", "guid")

    def process(self):
        self.outputs["guid"].sv_set([[ifcopenshell.guid.new()]])


def register():
    bpy.utils.register_class(SvIfcGenerateGuid)


def unregister():
    bpy.utils.unregister_class(SvIfcGenerateGuid)
