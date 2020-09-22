import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvCreateIfc(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = 'SvCreateIfc'
    bl_label = 'Create IFC'
    schema: StringProperty(name='schema', update=updateNode, default='IFC4')

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', 'schema').prop_name = 'schema'
        self.outputs.new('SvVerticesSocket', 'file')

    def process(self):
        self.sv_input_names = ['schema']
        super().process()

    def process_ifc(self, schema):
        guid = ifcopenshell.guid.new()
        ifcsverchok.helper.ifc_files[guid] = ifcopenshell.file(schema=schema)
        self.outputs['file'].sv_set([[ifcsverchok.helper.ifc_files[guid]]])

def register():
    bpy.utils.register_class(SvCreateIfc)

def unregister():
    bpy.utils.unregister_class(SvCreateIfc)
