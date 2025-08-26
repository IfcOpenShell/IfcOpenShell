# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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


import os
import bpy
import bonsai.tool as tool
from bpy.types import WorkSpaceTool
from functools import partial

from bonsai.bim.module.numbering.data import NumberingData

from bonsai.bim.module.numbering.util import NumberFormatting

class NumberingTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.numbering_tool"
    bl_label = "Numbering Tool"
    bl_description = "Gives you Numbering related superpowers"
    # TODO: replace with numbering icon
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.numbering")
    bl_widget = None

    def draw_settings(context, layout, ws_tool):
        # Unlike operators, Blender doesn't treat workspace tools as a class, so we'll create our own.
        NumberingToolUI.draw(context, layout)

class NumberingToolUI:

    @classmethod
    def draw(cls, context, layout):
        cls.layout = layout
        cls.props = tool.Numbering.get_numbering_props()

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        if not NumberingData.is_loaded:
            NumberingData.load()

        cls.draw_interface()

    @classmethod
    def draw_interface(cls):
        
        assert (layout := cls.layout)
        
        props = tool.Numbering.get_numbering_props()

        cls.draw_settings(layout, props)
        cls.draw_selection(layout, props)
        cls.draw_numbering_order(layout, props)
        cls.draw_numbering_systems(layout, props)
        cls.draw_numbering_format(layout, props)
        cls.draw_storage_options(layout, props)

        # Actions
        box = layout.box()
        row = box.row(align=True)
        row.operator("bim.assign_numbers", icon="TAG", text="Assign Numbers")
        row = box.row(align=True)
        row.operator("bim.remove_numbers", icon="X", text="Remove Numbers")

    def draw_settings(layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Settings")
        grid = box.grid_flow(row_major=True, align=True, columns=4, even_columns=True)
        grid.prop(props, "settings_name", text="Name")
        grid.operator("bim.save_settings", icon="FILE_TICK", text="Save")
        grid.operator("bim.clear_settings", icon="CANCEL", text="Clear")
        grid.operator("bim.export_settings", icon="EXPORT", text="Export")

        grid.prop(props, "saved_settings", text="")
        grid.operator("bim.load_settings", icon="FILE_REFRESH", text="Load")
        grid.operator("bim.delete_settings", icon="TRASH", text="Delete")
        grid.operator("bim.import_settings", icon="IMPORT", text="Import")

    def draw_selection(layout, props):  
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Elements to number")
        grid = box.grid_flow(row_major=True, align=True, columns=4, even_columns=True)
        grid.prop(props, "selected_toggle")
        grid.prop(props, "visible_toggle")
        grid.prop(props, "parent_type", text="")
        if props.parent_type == "Other":
            grid.prop(props, "parent_type_other", text="")
        else:
            grid.label(text="")

        grid = box.grid_flow(row_major=True, align=True, columns=4, even_columns=True)
        grid.prop(props, "selected_types", expand=True)

    def draw_numbering_order(layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Numbering order")
        # Create a grid for direction and precision
        grid = box.grid_flow(row_major=True, align=True, columns=4, even_columns=True)
        grid.label(text="Direction: ")
        grid.prop(props, "x_direction", text="X")
        grid.prop(props, "y_direction", text="Y")
        grid.prop(props, "z_direction", text="Z")
        grid.label(text="Precision: ")
        grid.prop(props, "precision", index=0, text="X")
        grid.prop(props, "precision", index=1, text="Y")
        grid.prop(props, "precision", index=2, text="Z")

        # Axis order and reference point 
        grid = box.grid_flow(row_major=True, align=True, columns=4)
        grid.label(text="Order:")
        grid.prop(props, "axis_order", text="")
        grid.label(text="Reference point:")
        grid.prop(props, "location_type", text="")

    def draw_numbering_systems(layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Numbering of elements {E}, within type {T} and storeys {S}")
        grid = box.grid_flow(row_major=True, align=True, columns=4, even_columns=True)
        grid.label(text="Start at:")
        grid.prop(props, "initial_element_number", text="{E}")
        grid.prop(props, "initial_type_number", text="{T}")
        grid.prop(props, "initial_storey_number", text="{S}")
        grid.label(text="System:")
        grid.prop(props, "element_numbering", text="{E}")
        grid.prop(props, "type_numbering", text="{T}")
        grid.prop(props, "storey_numbering", text="{S}")

        # Custom storey number
        if props.storey_numbering == "custom":
            box = box.box()
            row = box.row(align=True)
            row.prop(props, "custom_storey", text="Storey")
            row.prop(props, "custom_storey_number", text="Number")

    def draw_numbering_format(layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Numbering format")
        grid = box.grid_flow(align=True, columns=4, even_columns=True)
        grid.label(text="Format:")
        grid.prop(props, "format", text="")
        # Show preview in a textbox style (non-editable)
        grid.label(text="Preview:")
        preview_box = grid.box()
        preview_box.label(text=NumberFormatting.format_preview)

    def draw_storage_options(layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Store number in")
        
        grid = box.grid_flow(align=True, columns=4, even_columns=True)
        grid.prop(props, "save_type", text="")
        if props.save_type == "Attribute":
            grid.prop(props, "attribute_name", text="")
            if props.attribute_name == "Other":
                grid.prop(props, "attribute_name_other", text="")
        if props.save_type == "Pset":
            grid.prop(props, "pset_name", text="")
            if props.pset_name == "Custom Pset":
                grid.prop(props, "custom_pset_name", text="")
            grid.prop(props, "property_name", text="")

        box.prop(props, "remove_toggle")
        box.prop(props, "check_duplicates_toggle")


