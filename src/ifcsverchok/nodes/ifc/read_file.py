import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcReadFile(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcReadFile"
    bl_label = "IFC Read File"
    path: StringProperty(name="path", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "path").prop_name = "path"
        self.outputs.new("SvVerticesSocket", "file")

    def process(self):
        self.sv_input_names = ["path"]
        super().process()

    def process_ifc(self, path):
        guid = ifcopenshell.guid.new()
        ifcsverchok.helper.ifc_files[guid] = ifcopenshell.open(path)
        self.outputs["file"].sv_set([[ifcsverchok.helper.ifc_files[guid]]])


def register():
    bpy.utils.register_class(SvIfcReadFile)


def unregister():
    bpy.utils.unregister_class(SvIfcReadFile)
