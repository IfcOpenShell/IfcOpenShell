import bpy

import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore

import bpy
import json
import ifcopenshell

from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcAddPset(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcAddPset"
    bl_label = "IFC Add Pset"
    Name: StringProperty(name="Name", update=updateNode, default="My_Pset")
    Properties: StringProperty(name="Properties", update=updateNode, default="{\"Foo\":\"Bar\"}")
    Elements: StringProperty(name="Elements", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Name").prop_name = "Name"
        self.inputs.new("SvTextSocket", "Properties").prop_name = "Properties"
        self.inputs.new("SvStringsSocket", "Elements").prop_name = "Elements"
        self.outputs.new("SvStringsSocket", "entity")
        self.outputs.new("SvStringsSocket", "file")

    def process(self):
        if not any(socket.is_linked for socket in self.outputs):
            return

        name = self.inputs["Name"].sv_get()[0][0]
        properties = self.inputs["Properties"].sv_get()[0][0]
        elements = self.inputs["Elements"].sv_get()[0]

        if SvIfcStore.file is None:
            SvIfcStore.file = SvIfcStore.create_boilerplate()
        self.file = SvIfcStore.get_file()

        if self.node_id not in SvIfcStore.id_map.values():
            element = self.create(name, properties, elements)
        else:
            element = self.edit(name, properties, elements)

        self.outputs["entity"].sv_set([[element]])
        self.outputs["file"].sv_set([[self.file]])

    def create(self, name, properties, elements):
        results = []
        for element in elements:
            result = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name=name)
            ifcopenshell.api.run("pset.edit_pset", self.file, pset=result, properties=json.loads(properties))
            SvIfcStore.id_map[result.id()] = self.node_id
            results.append(result)
        return result

    def edit(self, name, properties, elements):
        result = self.get_existing_element()
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=result, name=name, properties=json.loads(properties))
        return result

    def get_existing_element(self):
        entity_id = list(SvIfcStore.id_map.keys())[list(SvIfcStore.id_map.values()).index(self.node_id)]
        return self.file.by_id(entity_id)


def register():
    bpy.utils.register_class(SvIfcAddPset)


def unregister():
    bpy.utils.unregister_class(SvIfcAddPset)
    SvIfcStore.purge()
