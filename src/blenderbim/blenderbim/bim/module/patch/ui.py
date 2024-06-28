# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool
from blenderbim.bim.helper import prop_with_search
from blenderbim.bim.helper import draw_attributes


def has_digits(text):
    """Checks if a string contains no digits (0-9) and float decimal."""
    if "," in text:
        return False
    return any(char.isdigit() or char == "." for char in text)


def draw_ResetAbsoluteCoordinates(props, layout):
    col = layout.column(align=True)
    col.prop(props, "ifc_patch_reset_absolute_coordinates_mode")
    col.separator(factor=0.5)
    col.prop(props, "ifc_patch_reset_absolute_coordinates_offset")

    col_digit = layout.column(align=True)

    if props.ifc_patch_reset_absolute_coordinates_offset == "auto":
        col_digit.alert = not has_digits(
            props.ifc_patch_reset_absolute_coordinates_threshold
        )
        col_digit.prop(
            props,
            "ifc_patch_reset_absolute_coordinates_threshold",
            text="Threshold",
        )
    elif props.ifc_patch_reset_absolute_coordinates_offset == "manual":
        col_digit.alert = not has_digits(
            props.ifc_patch_reset_absolute_coordinates_threshold
        )
        col_digit.prop(
            props,
            "ifc_patch_reset_absolute_coordinates_threshold",
            text="Threshold",
        )
        row = col_digit.row(align=True)
        row_x = row.row()
        row_x.alert = not has_digits(
            props.ifc_patch_reset_absolute_coordinates_offset_x
        )
        row_x.prop(props, "ifc_patch_reset_absolute_coordinates_offset_x", text="")

        row_y = row.row()
        row_y.alert = not has_digits(
            props.ifc_patch_reset_absolute_coordinates_offset_y
        )
        row_y.prop(props, "ifc_patch_reset_absolute_coordinates_offset_y", text="")

        row_z = row.row()
        row_z.alert = not has_digits(
            props.ifc_patch_reset_absolute_coordinates_offset_z
        )
        row_z.prop(props, "ifc_patch_reset_absolute_coordinates_offset_z", text="")


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

        scene = context.scene
        props = scene.BIMPatchProperties
        row = layout.row()
        prop_with_search(row, props, "ifc_patch_recipes")

        if tool.Ifc.get():
            row = self.layout.row()
            row.prop(props, "should_load_from_memory")

        if not tool.Ifc.get() or not props.should_load_from_memory:
            row = layout.row(align=True)
            row.prop(props, "ifc_patch_input")
            row.operator("bim.select_ifc_patch_input", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(props, "ifc_patch_output")
        row.operator("bim.select_ifc_patch_output", icon="FILE_FOLDER", text="")

        if props.ifc_patch_recipes == "ResetAbsoluteCoordinates":
            draw_ResetAbsoluteCoordinates(props, layout)

        elif props.ifc_patch_args_attr:
            draw_attributes(props.ifc_patch_args_attr, layout)

        else:
            layout.row().prop(props, "ifc_patch_args")

        op = layout.operator("bim.execute_ifc_patch")
        op.use_json_for_args = len(props.ifc_patch_args_attr) == 0
