# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

from bpy.types import Panel
import bonsai.tool as tool
from bonsai.core.numbering import NumberFormatting
from bonsai.bim.module.numbering.data import NumberingData

class BIM_PT_Numbering(Panel):
    bl_label = "Numbering settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return context.workspace.tools.from_space_view3d_mode(context.mode).idname == "bim.numbering_tool"

    def draw(cls,  context):
        assert (layout := cls.layout)

        if not NumberingData.is_loaded:
            NumberingData.load()
        
        props = tool.Numbering.get_numbering_props()
        
        cls.draw_selection(layout, props)
        cls.draw_numbering_order(layout, props)
        cls.draw_numbering_systems(layout, props)
        cls.draw_numbering_format(layout, props)
        cls.draw_storage_options(layout, props)
        cls.draw_settings(layout, props)

    @classmethod
    def draw_selection(cls, layout, props):  
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

    @classmethod
    def draw_numbering_order(cls, layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Numbering Order")
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
        grid.label(text="Reference Point:")
        grid.prop(props, "location_type", text="")

    @classmethod
    def draw_numbering_systems(cls, layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Numbering of Elements {E}, Within Type {T} and Storeys {S}")
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

    @classmethod
    def draw_numbering_format(cls, layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Numbering Format")
        grid = box.grid_flow(align=True, columns=4, even_columns=True)
        grid.label(text="Format:")
        grid.prop(props, "format", text="")
        # Show preview in a textbox style (non-editable)
        grid.label(text="Preview:")
        preview_box = grid.box()
        preview_box.label(text=NumberFormatting.format_preview)

    @classmethod
    def draw_storage_options(cls, layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Store Number in")

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

    @classmethod   
    def draw_settings(cls, layout, props):
        box = layout.box()
        box.alignment = "EXPAND"
        box.label(text="Manage Settings")
        grid = box.grid_flow(row_major=True, align=True, columns=4, even_columns=True)
        grid.prop(props, "settings_name", text="Name")
        grid.operator("bim.save_settings", icon="FILE_TICK", text="Save")
        grid.operator("bim.clear_settings", icon="CANCEL", text="Clear")
        grid.operator("bim.export_settings", icon="EXPORT", text="Export")

        grid.prop(props, "saved_settings", text="")
        grid.operator("bim.load_settings", icon="FILE_REFRESH", text="Load")
        grid.operator("bim.delete_settings", icon="TRASH", text="Delete")
        grid.operator("bim.import_settings", icon="IMPORT", text="Import")
