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
import ifcsverchok.helper
import ifcsverchok.helper as helper
from ifcsverchok.ifcstore import SvIfcStore
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data


class SvIfcById(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcById"
    bl_label = "IFC By Id"
    bl_description = "Get IFC elements by step id from the transient IFC file."
    id: StringProperty(
        name="Id(s)",
        update=updateNode,
    )

    def sv_init(self, context):
        helper.create_socket(self.inputs, "id", description="Step ids.", data_type="list[list[str]]", prop_name="id")
        helper.create_socket(
            self.outputs,
            "Entities",
            description="Entities.",
            data_type="list[ifcopenshell.entity_instance]",
            prop_name="Entities",
        )

    def draw_buttons(self, context, layout):
        layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = (
            "Get IFC element by step id. Takes one or multiple step ids."
        )

    def process(self):
        self.ids = flatten_data(self.inputs["id"].sv_get(), target_level=1)
        if not self.ids[0]:
            return
        self.file = SvIfcStore.get_file()
        self.entities = [self.file.by_id(int(step_id)) for step_id in self.ids]
        self.outputs["Entities"].sv_set(self.entities)


def register():
    bpy.utils.register_class(SvIfcById)


def unregister():
    bpy.utils.unregister_class(SvIfcById)
