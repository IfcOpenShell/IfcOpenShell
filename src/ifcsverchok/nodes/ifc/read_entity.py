import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcReadEntity(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = 'SvIfcReadEntity'
    bl_label = 'IFC Read Entity'
    file: StringProperty(name='file', update=updateNode)
    entity: StringProperty(name='entity', update=updateNode)
    current_ifc_class: StringProperty(name='current_ifc_class')

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', 'file').prop_name = 'file'
        self.inputs.new('SvStringsSocket', 'entity').prop_name = 'entity'
        self.outputs.new('SvStringsSocket', 'id')
        self.outputs.new('SvStringsSocket', 'is_a')

    def process(self):
        self.sv_input_names = ['file', 'entity']
        ifc_class = self.inputs['entity'].sv_get()[0][0]
        if ifc_class:
            ifc_class = ifc_class.is_a()
            file = self.inputs['file'].sv_get()[0][0]
            if file:
                schema_name = file.wrapped_data.schema
            else:
                schema_name = 'IFC4'
            self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name)
            self.entity_schema = self.schema.declaration_by_name(ifc_class)

            if ifc_class != self.current_ifc_class:
                self.generate_outputs(ifc_class)
        super().process()

    def generate_outputs(self, ifc_class):
        while len(self.outputs) > 2:
            self.outputs.remove(self.outputs[-1])
        for i in range(0, self.entity_schema.attribute_count()):
            name = self.entity_schema.attribute_by_index(i).name()
            self.outputs.new('SvStringsSocket', name).prop_name = name
        self.current_ifc_class = ifc_class

    def process_ifc(self, file, entity):
        self.outputs['id'].sv_set([[entity.id()]])
        self.outputs['is_a'].sv_set([[entity.is_a()]])
        for i in range(0, self.entity_schema.attribute_count()):
            name = self.entity_schema.attribute_by_index(i).name()
            self.outputs[name].sv_set([[entity[i]]])


def register():
    bpy.utils.register_class(SvIfcReadEntity)

def unregister():
    bpy.utils.unregister_class(SvIfcReadEntity)
