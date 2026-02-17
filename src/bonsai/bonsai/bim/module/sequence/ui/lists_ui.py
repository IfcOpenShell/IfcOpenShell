# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net
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

# Toggle to show/hide saved ColorTypes section
import bpy
import re
from bpy.types import UIList
import bonsai.tool as tool
from bonsai.bim.module.sequence.data import SequenceData
from typing import Any, Optional



class BIM_UL_animation_group_stack(UIList):
    bl_idname = "BIM_UL_animation_group_stack"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0):
        row = layout.row(align=True)
        row.prop(item, "enabled", text="")
        row.label(text=item.group)

    def invoke(self, context, event):
        pass

class BIM_UL_task_columns(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: "BIMWorkScheduleProperties",
        item: "Attribute",
        icon,
        active_data,
        active_propname,
    ):
        props = tool.Sequence.get_work_schedule_props()
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", emboss=False, text="")
            if props.sort_column == item.name:
                row.label(text="", icon="SORTALPHA")
            row.operator("bim.remove_task_column", text="", icon="X").name = item.name


class BIM_UL_task_filters(UIList):
    """Draws the list of filter rules."""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0):
        # 'item' is an instance of TaskFilterRule
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # The data type is now read directly from the rule's property
            data_type = getattr(item, 'data_type', 'string')

            row = layout.row(align=True)

            # Common controls (checkbox, column, operator)
            row.prop(item, "is_active", text="")
            row.prop(item, "column", text="")
            row.prop(item, "operator", text="")

            # The value field is only enabled if the operator requires it
            value_row = row.row(align=True)
            value_row.enabled = item.operator not in {'EMPTY', 'NOT_EMPTY'}

            # Conditional logic to draw the correct value widget
            if data_type == 'integer':
                value_row.prop(item, "value_integer", text="")
            elif data_type in ('float', 'real'):
                value_row.prop(item, "value_float", text="")
            elif data_type == 'boolean':
                value_row.prop(item, "value_boolean", text="")
            elif data_type == 'date':
                # For dates, we show the text and a button that opens the calendar
                value_row.prop(item, "value_string", text="")
                # [DEBUG] CORRECTED CALENDAR BUTTON
                op = value_row.operator("bim.filter_datepicker", text="", icon="OUTLINER_DATA_CAMERA")
                op.rule_index = index  # [DEBUG] THIS IS CRUCIAL - pass the index
            else:  # By default, use string (for text, enums, etc.)
                value_row.prop(item, "value_string", text="")

class BIM_UL_saved_filter_sets(UIList):

    """Draws the list of saved filter sets."""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # 'item' es una instancia de SavedFilterSet
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(text=item.name, icon='FILTER')

class BIM_UL_task_inputs(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.select_product", text="", icon="RESTRICT_SELECT_OFF")
            op.product = item.ifc_definition_id
            row.prop(item, "name", emboss=False, text="")
            # row.operator("bim.remove_task_column", text="", icon="X").name = item.name

class BIM_UL_task_resources(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.operator("bim.go_to_resource", text="", icon="STYLUS_PRESSURE").resource = item.ifc_definition_id
            row.prop(item, "name", emboss=False, text="")
            row.prop(item, "schedule_usage", emboss=False, text="")

class BIM_UL_animation_colors(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row()
            row.prop(item, "color", text="")
            row.prop(item, "name", text="")

class BIM_UL_task_outputs(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.select_product", text="", icon="RESTRICT_SELECT_OFF")
            op.product = item.ifc_definition_id
            row.prop(item, "name", emboss=False, text="")

class BIM_UL_product_input_tasks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.go_to_task", text="", icon="STYLUS_PRESSURE")
            op.task = item.ifc_definition_id
            row.split(factor=0.8)
            row.prop(item, "name", text="")

class BIM_UL_product_output_tasks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.go_to_task", text="", icon="STYLUS_PRESSURE")
            op.task = item.ifc_definition_id
            row.split(factor=0.8)
            row.prop(item, "name", text="")

class BIM_UL_tasks(UIList):
    @classmethod
    def draw_header(cls, layout: bpy.types.UILayout):
        props = tool.Sequence.get_work_schedule_props()
        row = layout.row(align=True)

        # Apply original COPIA alignment system with virtual columns support
        split1 = row.split(factor=0.1)
        # Header "ID" + quick sort-by-ID button (with spacing)
        hdr = split1.row(align=False)  # Changed to False to avoid tight alignment
        hdr.label(text="ID", icon="BLANK1")
        hdr.operator("bim.sort_schedule_by_id_asc", text="", icon="SORTALPHA")
        
        # Calculate split factor accounting for 2 virtual columns (Element 3D + Variance)
        # Drastically reduced to compensate for 18+ spaces in virtual columns manual spacing
        split2 = split1.split(factor=0.4 - min(0.2, 0.1 * len(props.columns)))
        split2.label(text="Name", icon="BLANK1")
        
        # Use same split2 for custom columns to ensure perfect alignment
        split3 = cls.draw_custom_columns(props, split2, header=True)
        
        # Virtual columns headers using the returned split from draw_custom_columns
        split3.label(text="  Element 3D  ")  # Add manual spacing
        split3.label(text="Variance")


    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: "BIMTaskTreeProperties",
        item: "Task",
        icon,
        active_data,
        active_propname,
    ):
        if item:
            self.props = tool.Sequence.get_work_schedule_props()
            task = SequenceData.data["tasks"][item.ifc_definition_id]
            row = layout.row(align=True)
            
            self.draw_hierarchy(row, item)

            # Apply original COPIA alignment system with virtual columns support
            split1 = row.split(factor=0.1)
            split1.prop(item, "identification", emboss=False, text="")
            
            # Use SAME split calculation as header for perfect alignment
            # Drastically reduced to compensate for 18+ spaces in virtual columns manual spacing
            split2 = split1.split(factor=0.4 - min(0.2, 0.1 * len(self.props.columns)))
            # Align Name values to start at beginning of "Name" title - remove icon and add left alignment
            name_row = split2.row(align=False)
            name_row.alignment = 'LEFT'
            name_row.label(text=item.name or "Unnamed")  # No padding, no icon - pure left align

            # Use same split2 for custom columns to ensure perfect alignment
            split3 = BIM_UL_tasks.draw_custom_columns(self.props, split2, item, task)

            # Virtual columns data using the returned split from draw_custom_columns
            split3.label(text=f"                  {item.outputs_count}    ")  # Move back left - better center for 3D Outputs

            # Variance column with status and colored background
            variance_status_text = item.variance_status or ""
            icon = 'BLANK1'
            
            # Status field display based on variance result
            if "Delayed" in variance_status_text:
                icon = 'TIME'
                red_box = split3.box()
                red_box.alert = True
                red_row = red_box.row()
                red_row.scale_y = 0.9
                red_row.label(text=variance_status_text, icon=icon)
                
            elif "Ahead" in variance_status_text:
                # GREEN: Use box with active = True for green
                icon = 'TIME'
                green_box = split3.box()
                green_box.active = True
                green_row = green_box.row()
                green_row.scale_y = 0.9
                # Use a label so it's not a button
                green_row.label(text=variance_status_text, icon=icon)
            elif "On Time" in variance_status_text:
                # BLUE: Use box with active = False for blue
                icon = 'TIME'
                blue_box = split3.box()
                blue_box.active = False
                blue_box.enabled = True
                blue_row = blue_box.row()
                blue_row.scale_y = 0.9
                # Use a label so it's not a button
                blue_row.label(text=variance_status_text, icon=icon)
            else:
                # Default
                icon = 'BLANK1'
                split3.label(text=variance_status_text, icon=icon)

            # Add variance color mode checkbox - ALL FUNCTIONAL
            if variance_status_text:
                checkbox_container = row.row(align=True)
                checkbox_container.scale_x = 0.8
                
                # CONDITIONAL based on variance result - ALL use real prop()
                if "Delayed" in variance_status_text:
                    # RED: alert works perfectly
                    checkbox_container.alert = True
                    
                elif "Ahead" in variance_status_text:
                    # GREEN: box with active = True
                    checkbox_box = checkbox_container.box()
                    checkbox_box.active = True
                    checkbox_box.scale_y = 0.9
                    checkbox_container = checkbox_box.row()
                    
                elif "On Time" in variance_status_text:
                    # BLUE: box with active = False
                    checkbox_box = checkbox_container.box() 
                    checkbox_box.active = False
                    checkbox_box.enabled = True
                    checkbox_box.scale_y = 0.9
                    checkbox_container = checkbox_box.row()
                
                # ALL use the real prop() to function
                checkbox_container.prop(
                    item,
                    "is_variance_color_selected",
                    text="",
                    icon="CHECKBOX_HLT" if item.is_variance_color_selected else "CHECKBOX_DEHLT",
                )

            if self.props.active_task_id and self.props.editing_task_type == "ATTRIBUTES":
                row.prop(
                    item,
                    "is_selected",
                    icon="CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT",
                    text="",
                    emboss=False,
                )
            if self.props.should_show_task_bar_selection:
                row.prop(
                    item,
                    "has_bar_visual",
                    icon="COLLECTION_COLOR_04" if item.has_bar_visual else "OUTLINER_COLLECTION",
                    text="",
                    emboss=False,
                )
            if self.props.enable_reorder:
                self.draw_order_operator(row, item.ifc_definition_id)
            if self.props.editing_task_type == "SEQUENCE" and self.props.highlighted_task_id != item.ifc_definition_id:
                if item.is_predecessor:
                    op = row.operator("bim.unassign_predecessor", text="", icon="BACK", emboss=False)
                else:
                    op = row.operator("bim.assign_predecessor", text="", icon="TRACKING_BACKWARDS", emboss=False)
                op.task = item.ifc_definition_id

                if item.is_successor:
                    op = row.operator("bim.unassign_successor", text="", icon="FORWARD", emboss=False)
                else:
                    op = row.operator("bim.assign_successor", text="", icon="TRACKING_FORWARDS", emboss=False)
                op.task = item.ifc_definition_id

    def draw_order_operator(self, row: bpy.types.UILayout, ifc_definition_id: int) -> None:
        task = SequenceData.data["tasks"][ifc_definition_id]
        if task["NestingIndex"] is not None:
            if task["NestingIndex"] == 0:
                op = row.operator("bim.reorder_task_nesting", icon="TRIA_DOWN", text="")
                op.task = ifc_definition_id
                op.new_index = task["NestingIndex"] + 1
            elif task["NestingIndex"] > 0:
                op = row.operator("bim.reorder_task_nesting", icon="TRIA_UP", text="")
                op.task = ifc_definition_id
                op.new_index = task["NestingIndex"] - 1

    def draw_hierarchy(self, row: bpy.types.UILayout, item: bpy.types.PropertyGroup) -> None:
        for i in range(0, item.level_index):
            row.label(text="", icon="BLANK1")
        if item.has_children:
            if item.is_expanded:
                row.operator("bim.contract_task", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN").task = (
                    item.ifc_definition_id
                )
            else:
                row.operator("bim.expand_task", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT").task = (
                    item.ifc_definition_id
                )
        else:
            row.label(text="", icon="DOT")

    @classmethod
    def draw_custom_columns(
        cls,
        props: bpy.types.PropertyGroup,
        row: bpy.types.UILayout,
        item: Optional[bpy.types.PropertyGroup] = None,
        task: Optional[dict[str, Any]] = None,
        *,
        header: bool = False,
    ) -> bpy.types.UILayout:
        """Original COPIA alignment system: simple and perfect alignment"""
        if not header:
            assert item and task, "Item and task must be provided when not drawing a header"

        # Apply original COPIA system: simple iteration through all columns
        # This ensures perfect alignment between headers and data
        for column in props.columns:
            column_name = column.name
            
            # --- Generalized handling for all date columns ---
            date_match = re.match(r"IfcTaskTime\.(Schedule|Actual|Early|Late)(Start|Finish)", column_name)
            if date_match:
                date_type = date_match.group(1).lower()
                date_part = date_match.group(2)

                prop_name = f"{date_type.lower()}_{date_part.lower()}"
                if date_type == "schedule":
                    prop_name = date_part.lower()

                derived_prop_name = f"derived_{prop_name}"

                if header:
                    # Show full names: Schedule Start, Actual Start, Late Start, etc.
                    full_name = f"{date_type.title()} {date_part}"
                    # Create sub-split for Schedule columns to reduce spacing
                    if date_type == "schedule":
                        subsplit = row.split(factor=0.6)  # Reduce space for Schedule columns
                        subsplit.label(text=full_name)
                    else:
                        row.label(text=full_name)
                else:
                    derived_value = getattr(item, derived_prop_name, "")
                    if derived_value:
                        # Add manual spacing to move Finish dates right - adjusted only for Schedule columns
                        if date_part == "Finish" and date_type == "schedule":
                            subsplit = row.split(factor=0.6)  # Reduce space for Schedule columns
                            subsplit.label(text=f"     {derived_value}*")  # 5 spaces - Schedule Finish (reduced from 10)
                        elif date_part == "Start" and date_type == "schedule":
                            subsplit = row.split(factor=0.6)  # Reduce space for Schedule columns  
                            subsplit.label(text=f"     {derived_value}*")  # 5 spaces - Schedule Start (corrected from 10)
                        elif date_part == "Finish" and date_type == "actual":
                            row.label(text=f"          {derived_value}*")  # 10 spaces - Actual Finish (original)
                        elif date_part == "Start" and date_type == "actual":
                            row.label(text=f"     {derived_value}*")  # 5 spaces - Actual Start (original)
                        elif date_part == "Finish" and date_type == "early":
                            row.label(text=f"          {derived_value}*")  # 10 spaces - Early Finish (original)
                        elif date_part == "Start" and date_type == "early":
                            row.label(text=f"     {derived_value}*")  # 5 spaces - Early Start (original)
                        elif date_part == "Finish" and date_type == "late":
                            row.label(text=f"          {derived_value}*")  # 10 spaces - Late Finish (original)
                        elif date_part == "Start" and date_type == "late":
                            row.label(text=f"     {derived_value}*")  # 5 spaces - Late Start (original)
                        else:
                            row.label(text=derived_value + "*")
                    else:
                        # Apply same alignment logic when there's no derived_value
                        if date_part in ["Finish", "Start"] and date_type in ["schedule", "actual", "early", "late"]:
                            # Get the actual value and apply the same spacing as derived_value
                            actual_value = getattr(item, prop_name, "")
                            if actual_value:
                                if date_type == "schedule":
                                    subsplit = row.split(factor=0.6)  # Reduce space for Schedule columns
                                    if date_part == "Start":
                                        subsplit.label(text=f"     {actual_value}")  # 5 spaces - Schedule Start
                                    else:  # Finish
                                        subsplit.label(text=f"     {actual_value}")  # 5 spaces - Schedule Finish
                                else:
                                    if date_part == "Start":
                                        row.label(text=f"     {actual_value}")  # 5 spaces - Other Start columns (original)
                                    else:  # Finish
                                        row.label(text=f"          {actual_value}")  # 10 spaces - Other Finish columns (original)
                            else:
                                row.prop(item, prop_name, emboss=False, text="")
                        else:
                            row.prop(item, prop_name, emboss=False, text="")
                continue

            if column_name == "IfcTaskTime.ScheduleDuration":
                if header:
                    row.label(text="Duration")
                else:
                    if item.derived_duration:
                        row.label(text=f"     {item.derived_duration}*")  # 5 spaces - Duration
                    else:
                        # Apply same 15-space alignment for editable fields
                        duration_value = getattr(item, "duration", "")
                        if duration_value:
                            row.label(text=f"       {duration_value}")  # 10 spaces - Duration
                        else:
                            row.prop(item, "duration", emboss=False, text="")
            elif column_name == "Controls.Calendar":
                if header:
                    row.label(text="Calendar")
                else:
                    if item.derived_calendar:
                        row.label(text=f"               {item.derived_calendar}*")  # 15 spaces - Calendar
                    else:
                        calendar_value = item.calendar or "-"
                        row.label(text=f"               {calendar_value}")  # 15 spaces - Calendar
            else:
                ifc_class, name = column_name.split(".")
                if header:
                    row.label(text=name)
                else:
                    if ifc_class == "IfcTask":
                        value = task[name]
                    elif ifc_class == "IfcTaskTime":
                        if (task_time_id := task["TaskTime"]) is None:
                            value = None
                        else:
                            value = SequenceData.data["task_times"][task_time_id][name]
                    else:
                        assert False, f"Unexpected ifc_class '{ifc_class}'."
                    if value is None:
                        row.label(text=f"               -")  # 15 spaces - NULL value
                    else:
                        row.label(text=f"               {str(value)}")  # 15 spaces - All other columns
        
        # Return the row for virtual columns to use
        return row
