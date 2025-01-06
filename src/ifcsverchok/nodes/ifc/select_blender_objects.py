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
import ifcopenshell.util.selector
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from bonsai.bim.ifc import IfcStore


class SvIfcSelectBlenderObjectsRefresh(bpy.types.Operator):
    bl_idname = "node.sv_ifc_select_blender_objects_refresh"
    bl_label = "IFC Select Blender Objects Refresh"
    bl_options = {"UNDO"}

    tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node = bpy.data.node_groups[self.tree_name].nodes[self.node_name]
        node.process()
        return {"FINISHED"}


class SvIfcSelectBlenderObjects(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcSelectBlenderObjects"
    bl_label = "IFC Select Blender Objects"
    file: StringProperty(name="file", update=updateNode)
    query: StringProperty(name="query", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "entities").prop_name = "entities"

    def draw_buttons(self, context, layout):
        self.wrapper_tracked_ui_draw_op(
            layout, "node.sv_ifc_select_blender_objects_refresh", icon="FILE_REFRESH", text="Refresh"
        )

    def process(self):
        self.file = IfcStore.get_file()
        self.sv_input_names = ["entities"]
        self.guids = []
        super().process()
        for obj in bpy.context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            if self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId in self.guids:
                obj.select_set(True)

    def process_ifc(self, entities):
        self.guids.append(entities.GlobalId)


def register():
    bpy.utils.register_class(SvIfcSelectBlenderObjectsRefresh)
    bpy.utils.register_class(SvIfcSelectBlenderObjects)


def unregister():
    bpy.utils.unregister_class(SvIfcSelectBlenderObjects)
    bpy.utils.unregister_class(SvIfcSelectBlenderObjectsRefresh)
