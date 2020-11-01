import bpy
import ifcopenshell
import ifcopenshell.util.element
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcGetProperty(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcGetProperty"
    bl_label = "IFC Get Property"
    entity: StringProperty(name="entity", update=updateNode)
    pset_name: StringProperty(name="pset_name", update=updateNode)
    prop_name: StringProperty(name="prop_name", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "entity").prop_name = "entity"
        self.inputs.new("SvStringsSocket", "pset_name").prop_name = "pset_name"
        self.inputs.new("SvStringsSocket", "prop_name").prop_name = "prop_name"
        self.outputs.new("SvStringsSocket", "value")

    def process(self):
        self.sv_input_names = ["entity", "pset_name", "prop_name"]
        self.value_out = []
        super().process()
        self.outputs["value"].sv_set(self.value_out)

    def process_ifc(self, entity, pset_name, prop_name):
        try:
            self.value_out.append(ifcopenshell.util.element.get_psets(entity)[pset_name][prop_name])
        except:
            pass


def register():
    bpy.utils.register_class(SvIfcGetProperty)


def unregister():
    bpy.utils.unregister_class(SvIfcGetProperty)
