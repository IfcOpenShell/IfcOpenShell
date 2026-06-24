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

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

import bonsai.tool as tool
from bonsai.bim.helper import draw_attributes, prop_with_search

if TYPE_CHECKING:
    from bonsai.bim.prop import Attribute


class BIM_MT_ifc_patch_presets(bpy.types.Menu):
    """Lists ifc-patch presets for the currently selected recipe.

    ``preset_subdir`` is resolved per draw so switching recipes swaps the
    preset list without re-registering the menu."""

    bl_label = "IFC Patch Presets"
    preset_operator = "script.execute_preset"

    def draw(self, context: bpy.types.Context) -> None:
        self.preset_subdir = tool.Patch.get_preset_subdir()
        bpy.types.Menu.draw_preset(self, context)


class BIM_PT_patch(bpy.types.Panel):
    bl_label = "Patch"
    bl_idname = "BIM_PT_patch"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_quality_control"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        props = tool.Patch.get_patch_props()
        row = layout.row()
        prop_with_search(row, props, "ifc_patch_recipes")

        if tool.Ifc.get():
            row = self.layout.row()
            row.prop(props, "should_load_from_memory")

        if not tool.Ifc.get() or not props.should_load_from_memory:
            row = layout.row(align=True)
            row.prop(props, "ifc_patch_input")
            row.operator("bim.select_ifc_patch_input", icon="FILE_FOLDER", text="")

        if tool.Patch.does_patch_has_output(props.ifc_patch_recipes):
            row = layout.row(align=True)
            row.prop(props, "ifc_patch_output")
            row.operator("bim.select_ifc_patch_output", icon="FILE_FOLDER", text="")

        def draw_callback_(attribute: Attribute, row: bpy.types.UILayout) -> None:
            if props.ifc_patch_recipes == "ExtractElements" and attribute.name == "Query":
                row.operator("bim.patch_query_from_selected", text="", icon="EYEDROPPER")

        if props.ifc_patch_args_attr:
            preset_row = layout.row(heading="Preset", align=True)
            preset_row.menu("BIM_MT_ifc_patch_presets", text=BIM_MT_ifc_patch_presets.bl_label)
            preset_row.operator("bim.add_ifc_patch_preset", text="", icon="ADD")
            preset_row.operator("bim.add_ifc_patch_preset", text="", icon="REMOVE").remove_active = True

            draw_callback = draw_callback_ if props.ifc_patch_recipes == "ExtractElements" else None
            draw_attributes(props.ifc_patch_args_attr, layout, callback=draw_callback)

        op = layout.operator("bim.execute_ifc_patch")
