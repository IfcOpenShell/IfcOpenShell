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
import ifcopenshell.util.selector
from bpy.props import StringProperty
from sverchok.data_structure import updateNode
from sverchok.node_tree import SverchCustomTreeNode

import ifcsverchok.helper as helper
from ifcsverchok.ifcstore import SvIfcStore


class SvIfcByQuery(bpy.types.Node, SverchCustomTreeNode, helper.SvIfcCore):
    bl_idname = "SvIfcByQuery"
    bl_label = "IFC By Query"
    query: StringProperty(name="Query", update=updateNode)

    def sv_init(self, context) -> None:
        helper.create_socket(
            self.inputs,
            "query",
            description="IFC Query string.",
            data_type="list[list[str]]",
            prop_name="query",
        )
        helper.create_socket(
            self.outputs,
            "Entity",
            description="IFC Entities found by the query.",
            data_type="set[ifcopenshell.entity_instance]",
            prop_name="Entity",
        )

    def process(self):
        if not self.inputs["query"].sv_get()[0][0]:
            return
        self.file = SvIfcStore.get_file()
        self.sv_input_names = ["query"]
        super().process()

    def process_ifc(self, query: str) -> None:
        elements = ifcopenshell.util.selector.filter_elements(self.file, query)
        self.outputs["Entity"].sv_set(elements)


def register():
    bpy.utils.register_class(SvIfcByQuery)


def unregister():
    bpy.utils.unregister_class(SvIfcByQuery)
