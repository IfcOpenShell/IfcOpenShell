import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcWriteFile(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcWriteFile"
    bl_label = "IFC Write File"
    file: StringProperty(name="file", update=updateNode)
    path: StringProperty(name="path", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "path").prop_name = "path"

    def process(self):
        self.sv_input_names = ["file", "path"]
        super().process()

    def process_ifc(self, file, path):
        file.write(path)


def register():
    bpy.utils.register_class(SvIfcWriteFile)


def unregister():
    bpy.utils.unregister_class(SvIfcWriteFile)
