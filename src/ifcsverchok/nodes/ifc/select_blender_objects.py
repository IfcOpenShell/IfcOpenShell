import bpy
import ifcopenshell
import ifcopenshell.util.selector
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcSelectBlenderObjects(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = 'SvIfcSelectBlenderObjects'
    bl_label = 'IFC Select Blender Objects'
    file: StringProperty(name='file', update=updateNode)
    query: StringProperty(name='query', update=updateNode)

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', 'entities').prop_name = 'entities'

    def process(self):
        self.sv_input_names = ['entities']
        self.guids = []
        super().process()
        for obj in bpy.context.visible_objects:
            index = obj.BIMObjectProperties.attributes.find('GlobalId')
            if index != -1 \
                    and obj.BIMObjectProperties.attributes[index].string_value in self.guids:
                obj.select_set(True)

    def process_ifc(self, entities):
        self.guids.append(entities.GlobalId)


def register():
    bpy.utils.register_class(SvIfcSelectBlenderObjects)

def unregister():
    bpy.utils.unregister_class(SvIfcSelectBlenderObjects)
