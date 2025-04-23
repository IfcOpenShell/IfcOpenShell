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
import bonsai.tool as tool
import ifcsverchok.helper
import ifcsverchok.helper as helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcSelectBlenderObjectsRefresh(bpy.types.Operator):
    bl_idname = "node.sv_ifc_select_blender_objects_refresh"
    bl_label = "IFC Select Blender Objects Refresh"
    bl_options = {"UNDO"}

    tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node: SvIfcSelectBlenderObjects
        node = bpy.data.node_groups[self.tree_name].nodes[self.node_name]
        node.process()
        return {"FINISHED"}


class SvIfcSelectBlenderObjects(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcSelectBlenderObjects"
    bl_label = "IFC Select Blender Objects"
    bl_description = "Select Blender objects based on IFC entities."
    file: StringProperty(name="file", update=updateNode)
    # TODO: never used.
    query: StringProperty(name="query", update=updateNode)

    def sv_init(self, context):
        helper.create_socket(
            self.inputs,
            "entities",
            description="IFC entities to select Bonsai Blender objects for (selects only objects by matching GlobalId).",
            data_type="list[list[ifcopenshell.entity_instance]]",
            prop_name="entities",
        )

    def draw_buttons(self, context, layout):
        self.wrapper_tracked_ui_draw_op(
            layout, "node.sv_ifc_select_blender_objects_refresh", icon="FILE_REFRESH", text="Refresh"
        )

    def process(self) -> None:
        self.sv_input_names = ["entities"]
        self.guids: list[str] = []
        super().process()
        for obj in bpy.context.visible_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if getattr(element, "GlobalId", None) in self.guids:
                obj.select_set(True)

    def process_ifc(self, entities: ifcopenshell.entity_instance) -> None:
        self.guids.append(entities.GlobalId)


def register():
    bpy.utils.register_class(SvIfcSelectBlenderObjectsRefresh)
    bpy.utils.register_class(SvIfcSelectBlenderObjects)


def unregister():
    bpy.utils.unregister_class(SvIfcSelectBlenderObjects)
    bpy.utils.unregister_class(SvIfcSelectBlenderObjectsRefresh)
