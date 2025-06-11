# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcSverchok.
#
# IfcSverchok is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcSverchok is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IfcSverchok.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, ensure_min_nesting, flatten_data


class SvIfcReadEntity(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcReadEntity"
    bl_label = "IFC Read Entity"
    entity: StringProperty(name="Entity Id", update=updateNode)
    current_ifc_class: StringProperty(name="current_ifc_class")

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "entity").prop_name = "entity"
        self.outputs.new("SvStringsSocket", "id")
        self.outputs.new("SvStringsSocket", "is_a")

    def draw_buttons(self, context, layout):
        layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = (
            "Decompose an IfcEntity into its attributes. Takes one entity id as input"
        )

    def process(self):
        self.sv_input_names = ["entity"]
        entity_id = flatten_data(self.inputs["entity"].sv_get(), target_level=1)
        if not entity_id[0]:
            return
        if len(entity_id) > 1:
            raise Exception("Only one entity can be read at a time")
        self.file = SvIfcStore.get_file()
        try:
            entity = self.file.by_id(entity_id[0])
        except Exception as e:
            raise Exception("Instance with id {} not found".format(entity_id), e)

        if entity:
            ifc_class = entity.is_a()
            file = SvIfcStore.get_file()
            if file:
                schema_name = file.schema_identifier
            else:
                schema_name = "IFC4"
            self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name)
            self.entity_schema = self.schema.declaration_by_name(ifc_class)

            if ifc_class != self.current_ifc_class:
                self.generate_outputs(ifc_class)

        self.outputs["id"].sv_set([entity.id()])
        self.outputs["is_a"].sv_set([entity.is_a()])
        for i in range(0, self.entity_schema.attribute_count()):
            name = self.entity_schema.attribute_by_index(i).name()
            self.outputs[name].sv_set([entity[i]])

    def generate_outputs(self, ifc_class):
        while len(self.outputs) > 2:
            self.outputs.remove(self.outputs[-1])
        for i in range(0, self.entity_schema.attribute_count()):
            name = self.entity_schema.attribute_by_index(i).name()
            self.outputs.new("SvStringsSocket", name).prop_name = name
        self.current_ifc_class = ifc_class


def register():
    bpy.utils.register_class(SvIfcReadEntity)


def unregister():
    bpy.utils.unregister_class(SvIfcReadEntity)
