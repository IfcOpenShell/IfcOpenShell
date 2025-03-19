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
import ifcopenshell.guid
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcCreateFileRefresh(bpy.types.Operator):
    bl_idname = "node.sv_ifc_create_file_refresh"
    bl_label = "LB Out"

    tree_name: StringProperty(default="")
    node_name: StringProperty(default="")
    has_baked: bpy.props.BoolProperty(name="Has Baked", default=False)

    def execute(self, context):
        node: SvIfcCreateFile
        node = bpy.data.node_groups[self.tree_name].nodes[self.node_name]
        node.process()
        return {"FINISHED"}


class SvIfcCreateFile(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcCreateFile"
    bl_label = "IFC Create File"
    schema: StringProperty(name="schema", update=updateNode, default="IFC4")

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "schema").prop_name = "schema"
        self.outputs.new("SvVerticesSocket", "file")

    def draw_buttons(self, context, layout):
        self.wrapper_tracked_ui_draw_op(layout, "node.sv_ifc_create_file_refresh", icon="FILE_REFRESH", text="Refresh")

    def process(self):
        self.sv_input_names = ["schema"]
        super().process()

    def process_ifc(self, schema: str) -> None:
        guid = ifcopenshell.guid.new()
        ifcsverchok.helper.ifc_files[guid] = ifcopenshell.file(schema=schema)
        self.outputs["file"].sv_set([[ifcsverchok.helper.ifc_files[guid]]])


def register():
    bpy.utils.register_class(SvIfcCreateFile)
    bpy.utils.register_class(SvIfcCreateFileRefresh)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateFile)
    bpy.utils.unregister_class(SvIfcCreateFileRefresh)
