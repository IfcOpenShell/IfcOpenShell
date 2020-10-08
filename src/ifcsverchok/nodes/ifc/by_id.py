import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcById(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = 'SvIfcById'
    bl_label = 'IFC By Id'
    file: StringProperty(name='file', update=updateNode)
    id: StringProperty(name='id', update=updateNode)

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', 'file').prop_name = 'file'
        self.inputs.new('SvStringsSocket', 'id').prop_name = 'id'
        self.outputs.new('SvStringsSocket', 'entity')

    def process(self):
        self.sv_input_names = ['file', 'id']
        super().process()

    def process_ifc(self, file, id):
        self.outputs['entity'].sv_set([[file.by_id(int(id))]])

def register():
    bpy.utils.register_class(SvIfcById)

def unregister():
    bpy.utils.unregister_class(SvIfcById)
