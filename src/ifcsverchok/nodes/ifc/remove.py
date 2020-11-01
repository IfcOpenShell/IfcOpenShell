import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcRemove(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcRemove"
    bl_label = "IFC Remove"
    file: StringProperty(name="file", update=updateNode)
    entity: StringProperty(name="entity", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "entity").prop_name = "entity"
        self.outputs.new("SvStringsSocket", "file")

    def process(self):
        file = self.inputs["file"].sv_get()[0][0]
        self.new_file = ifcopenshell.file.from_string(file.wrapped_data.to_string())
        self.remove_entity(self.inputs["entity"].sv_get())
        self.outputs["file"].sv_set([[self.new_file]])

    def remove_entity(self, entity):
        if isinstance(entity, (tuple, list)):
            for e in entity:
                self.remove_entity(e)
        else:
            self.new_file.remove(self.new_file.by_id(entity.id()))


def register():
    bpy.utils.register_class(SvIfcRemove)


def unregister():
    bpy.utils.unregister_class(SvIfcRemove)
