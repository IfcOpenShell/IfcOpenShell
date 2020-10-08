import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcByGuid(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = 'SvIfcByGuid'
    bl_label = 'IFC By Guid'
    file: StringProperty(name='file', update=updateNode)
    guid: StringProperty(name='guid', update=updateNode)

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', 'file').prop_name = 'file'
        self.inputs.new('SvStringsSocket', 'guid').prop_name = 'guid'
        self.outputs.new('SvStringsSocket', 'entity')

    def process(self):
        self.sv_input_names = ['file', 'guid']
        super().process()

    def process_ifc(self, file, guid):
        self.outputs['entity'].sv_set([[file.by_guid(guid)]])

def register():
    bpy.utils.register_class(SvIfcByGuid)

def unregister():
    bpy.utils.unregister_class(SvIfcByGuid)
