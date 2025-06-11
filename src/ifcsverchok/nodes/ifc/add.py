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
import ifcsverchok.helper as helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcAdd(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcAdd"
    bl_label = "IFC Add"
    bl_description = "Add an entity to the provided IFC file."
    file: StringProperty(name="file", update=updateNode)
    entity: StringProperty(name="entity", update=updateNode)

    def sv_init(self, context):
        helper.create_socket(
            self.inputs,
            "file",
            description="File to add entity to.",
            data_type="list[list[ifcopenshell.file]]",
            prop_name="file",
        )
        helper.create_socket(
            self.inputs,
            "entity",
            description="Entity to add to file.",
            data_type="list[list[ifcopenshell.entity_instance]]",
            prop_name="entity",
        )
        helper.create_socket(
            self.outputs, "file", description="File with added entity.", data_type="list[list[ifcopenshell.file]]"
        )
        helper.create_socket(
            self.outputs, "entity", description="Added entity.", data_type="list[list[ifcopenshell.entity_instance]]"
        )

    def process(self):
        self.sv_input_names = ["file", "entity"]
        self.file_out: list[ifcopenshell.file] = []
        self.entity_out: list[ifcopenshell.entity_instance] = []
        super().process()
        self.outputs["file"].sv_set([self.file_out])
        self.outputs["entity"].sv_set([self.entity_out])

    def process_ifc(self, file: ifcopenshell.file, entity: ifcopenshell.entity_instance) -> None:
        self.entity_out.append(file.add(entity))
        self.file_out.append(file)


def register():
    bpy.utils.register_class(SvIfcAdd)


def unregister():
    bpy.utils.unregister_class(SvIfcAdd)
