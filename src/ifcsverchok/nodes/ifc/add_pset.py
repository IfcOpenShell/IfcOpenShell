# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2022 Martina Jakubowska <martina@jakubowska.dk>
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

import bpy
import json
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.pset

from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data


class SvIfcAddPset(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcAddPset"
    bl_label = "IFC Add Pset"
    Name: StringProperty(
        name="Name",
        description="Name of the property set. Eg. Pset_WallCommon.",
        update=updateNode,
        default="My_Pset",
    )
    Properties: StringProperty(
        name="Properties",
        description='Propertied in a JSON key:value format.Eg. {"IsExternal":"True"}',
        update=updateNode,
        default='{"Foo":"Bar"}',
    )
    Elements: StringProperty(name="Element Ids", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Name").prop_name = "Name"
        self.inputs.new("SvTextSocket", "Properties").prop_name = "Properties"
        self.inputs.new("SvStringsSocket", "Elements").prop_name = "Elements"
        self.outputs.new("SvStringsSocket", "Entity")

    def draw_buttons(self, context, layout):
        layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = (
            "Add a property set and corresponding properties to IfcElements."
        )

    def process(self):
        if not any(socket.is_linked for socket in self.outputs):
            return

        name = self.inputs["Name"].sv_get()[0][0]
        properties = self.inputs["Properties"].sv_get()[0][0]
        element_ids = flatten_data(self.inputs["Elements"].sv_get(), target_level=1)

        self.file = SvIfcStore.get_file()
        try:
            elements = [self.file.by_id(int(step_id)) for step_id in element_ids]
        except Exception as e:
            raise Exception("Instance ID not found", e)

        if self.node_id not in SvIfcStore.id_map:
            element = self.create(name, properties, elements)
        else:
            element = self.edit(name, properties, elements)

        self.outputs["Entity"].sv_set([element])

    def create(
        self, name: str, properties: str, elements: list[ifcopenshell.entity_instance]
    ) -> list[ifcopenshell.entity_instance]:
        results = []
        for element in elements:
            result = ifcopenshell.api.pset.add_pset(self.file, product=element, name=name)
            ifcopenshell.api.pset.edit_pset(
                self.file,
                pset=result,
                properties=json.loads(properties),
            )
            SvIfcStore.id_map.setdefault(self.node_id, []).append(result.id())
            results.append(result)
        return results

    def edit(
        self, name: str, properties: str, elements: list[ifcopenshell.entity_instance]
    ) -> list[ifcopenshell.entity_instance]:
        result_ids = SvIfcStore.id_map[self.node_id]
        results: list[ifcopenshell.entity_instance] = []
        for result_id in result_ids:
            result = self.file.by_id(result_id)
            ifcopenshell.api.pset.edit_pset(
                self.file,
                pset=result,
                name=name,
                properties=json.loads(properties),
            )
            results.append(result)
        return results


def register():
    bpy.utils.register_class(SvIfcAddPset)


def unregister():
    bpy.utils.unregister_class(SvIfcAddPset)
    SvIfcStore.purge()
