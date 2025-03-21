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

import itertools

import bpy
import ifcopenshell
import ifcsverchok.helper
import ifcsverchok.helper as helper
from ifcsverchok.ifcstore import SvIfcStore
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data


class SvIfcByGuid(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcByGuid"
    bl_label = "IFC By Guid"
    bl_description = "Get IFC elements by guid from the transient IFC file."
    n_id: StringProperty(default="")
    guid: StringProperty(name="Guid(s)", update=updateNode)
    id_iter = itertools.count()
    guids: list[str]

    def sv_init(self, context):
        helper.create_socket(
            self.inputs, "guid", description="Entities guids.", data_type="list[list[str]]", prop_name="guid"
        )
        helper.create_socket(
            self.outputs, "Entities", description="Entities", data_type="list[list[ifcopenshell.entity_instance]]"
        )

    def draw_buttons(self, context, layout):
        layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = (
            "Get IFC element by guid. Takes one or multiple guids."
        )

    def process(self):
        self.guids = flatten_data(self.inputs["guid"].sv_get(), target_level=1)
        if not self.guids[0]:
            return
        self.file = SvIfcStore.get_file()
        self.entities = [self.file.by_guid(guid) for guid in self.guids]
        self.outputs["Entities"].sv_set(self.entities)


def register():
    bpy.utils.register_class(SvIfcByGuid)


def unregister():
    bpy.utils.unregister_class(SvIfcByGuid)
