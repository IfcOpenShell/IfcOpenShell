# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bonsai.bim.module.qto.data import QtoData


class BIM_PT_qto(bpy.types.Panel):
    bl_idname = "BIM_PT_qto"
    bl_label = "Quantity Take-off"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_qto"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMQtoProperties

        row = layout.row()
        if context.selected_objects:
            row.label(text=f"Quantifying {len(context.selected_objects)} Selected Objects", icon="MOD_EDGESPLIT")
        else:
            row.label(text="Quantifying All Objects", icon="MOD_EDGESPLIT")
        row = layout.row()
        row.prop(props, "qto_rule", text="")
        row = layout.row()
        row.operator("bim.perform_quantity_take_off")


class BIM_PT_qto_manual(bpy.types.Panel):
    bl_idname = "BIM_PT_qto_manual"
    bl_label = "Manual Quantification"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_qto"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMQtoProperties

        row = layout.row()
        row.prop(props, "calculator")
        row = layout.row()
        row.prop(props, "calculator_function", text="Function")

        row = layout.row(align=True)
        row.prop(props, "qto_name", text="")
        row.prop(props, "prop_name", text="")

        row = layout.row()
        row.operator("bim.calculate_single_quantity")


class BIM_PT_qto_simple(bpy.types.Panel):
    bl_idname = "BIM_PT_qto_simple"
    bl_label = "Simple Quantity Calculator"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_qto"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMQtoProperties

        row = layout.row()
        row.prop(props, "qto_result", text="Results")

        row = layout.row()
        row.operator("bim.calculate_circle_radius")
        row = layout.row()
        row.operator("bim.calculate_edge_lengths")
        row = layout.row()
        row.operator("bim.calculate_face_areas")
        row = layout.row()
        row.operator("bim.calculate_object_volumes")
        row = layout.row()
        row.operator("bim.calculate_formwork_area")


class BIM_PT_qto_cost(bpy.types.Panel):
    bl_idname = "BIM_PT_qto_cost"
    bl_label = "Parametric Cost Relationships"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_qto"

    def draw(self, context):
        if not QtoData.is_loaded:
            QtoData.load()

        if not context.selected_objects:
            row = self.layout.row()
            row.label(text="No Selected Object")
            return

        if not QtoData.data["has_cost_item"]:
            row = self.layout.row()
            row.label(text="No Related Cost Item")
            return

        row = self.layout.row(align=True)
        row.label(text="Relating Cost Item:")
        for relating_cost_item in QtoData.data["relating_cost_items"]:
            row.label(text="\n")
            row = self.layout.row(align=True)
            row.label(text="Cost item name:")
            row.label(text=f"{relating_cost_item['cost_item_name']}")
            row = self.layout.row(align=True)
            row.label(text="Quantity name:")
            row.label(text=f"{relating_cost_item['quantity_name']}")
            row = self.layout.row(align=True)
            row.label(text="Quantity value:")
            row.label(text=f"{relating_cost_item['quantity_value']}")
            row = self.layout.row(align=True)
            row.label(text="Quantity type:")
            row.label(text=f"{relating_cost_item['quantity_type']}")
            row = self.layout.row(align=True)
