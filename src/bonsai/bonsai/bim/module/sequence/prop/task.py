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

import bpy
import ifcopenshell.api
import ifcopenshell.api.sequence
import ifcopenshell.util.attribute
import ifcopenshell.util.date
import bonsai.tool as tool
import bonsai.core.sequence as core
from bonsai.bim.module.sequence.data import SequenceData, refresh as refresh_sequence_data
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
from typing import TYPE_CHECKING, Literal

# Import functions from animation module
try:
    from .animation import (
        get_animation_color_schemes_items,
        get_custom_group_colortype_items,
        UnifiedColorTypeManager
    )
except ImportError:
    # Fallback for when running from the original location
    from .animation import (
        get_animation_color_schemes_items,
        get_custom_group_colortype_items,
        UnifiedColorTypeManager
    )

# ============================================================================
# TASK CALLBACK FUNCTIONS
# ============================================================================

def update_task_checkbox_selection(self, context):
    """
    Callback that is executed when checking/unchecking a checkbox.
    Uses a timer to execute the 3D selection logic safely.
    """
    def apply_selection():
        try:
            # Get the properties to check if 3D selection is active
            props = tool.Sequence.get_work_schedule_props()
            if props.should_select_3d_on_task_click:
                # Execute the 3D selection logic
                ids = tool.Sequence.get_selected_task_ids()
                if ids:
                    bpy.ops.bim.select_task_related_products(task_ids=list(ids))
                    print(f"[DEBUG] 3D Selection applied for {len(ids)} tasks")
        except Exception as e:
            print(f"[ERROR] Error in 3D selection: {e}")
        return None
    
    # Use a timer to ensure this runs safely in the next context update
    bpy.app.timers.register(apply_selection, first_interval=0.1)

def updateTaskName(self: "Task", context: bpy.types.Context) -> None:
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled or self.name == "Unnamed":
        return
    ifc_file = tool.Ifc.get()
    ifcopenshell.api.sequence.edit_task(
        ifc_file,
        task=ifc_file.by_id(self.ifc_definition_id),
        attributes={"Name": self.name},
    )
    SequenceData.load()

def updateTaskIdentification(self: "Task", context: bpy.types.Context) -> None:
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled or self.identification == "XXX":
        return
    ifc_file = tool.Ifc.get()
    ifcopenshell.api.sequence.edit_task(
        ifc_file,
        task=ifc_file.by_id(self.ifc_definition_id),
        attributes={"Identification": self.identification},
    )
    SequenceData.load()

def updateTaskTimeStart(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "start", "Schedule")

def updateTaskTimeFinish(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "finish", "Schedule")

def updateTaskTimeActualStart(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "actual_start", "Actual")

def updateTaskTimeActualFinish(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "actual_finish", "Actual")

def updateTaskTimeEarlyStart(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "early_start", "Early")

def updateTaskTimeEarlyFinish(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "early_finish", "Early")

def updateTaskTimeLateStart(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "late_start", "Late")

def updateTaskTimeLateFinish(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "late_finish", "Late")

def updateTaskTimeDateTime(
    self: "Task",
    context: bpy.types.Context,
    prop_name: str,
    ifc_date_type: Literal["Schedule", "Actual", "Early", "Late"],
) -> None:
    props = tool.Sequence.get_work_schedule_props()

    if not props.is_task_update_enabled:
        return

    date_string = getattr(self, prop_name)

    # Handle empty or None values
    if not date_string or date_string in ["-", "null", "NULL", ""]:
        date_value = None
    else:
        try:
            parsed_date = ifcopenshell.util.date.parse_datetime(date_string)
            if parsed_date is None:
                self.setattr(prop_name, "-")
                return
            date_value = parsed_date
        except Exception:
            self.setattr(prop_name, "-")
            return

    # Determine IFC attribute name
    if prop_name.endswith("_start"):
        ifc_prop_name = "ScheduleStart" if "Schedule" in ifc_date_type else f"{ifc_date_type}Start"
    elif prop_name.endswith("_finish"):
        ifc_prop_name = "ScheduleFinish" if "Schedule" in ifc_date_type else f"{ifc_date_type}Finish"
    else:
        # For backward compatibility with "start" and "finish"
        ifc_prop_name = f"Schedule{prop_name.capitalize()}"

    ifc_file = tool.Ifc.get()
    task = ifc_file.by_id(self.ifc_definition_id)
    task_time = ifcopenshell.util.date.get_task_time_by_type(task, ifc_date_type)

    if task_time:
        # Update existing task time
        ifcopenshell.api.sequence.edit_task_time(
            ifc_file,
            task_time=task_time,
            attributes={ifc_prop_name: date_value},
        )
    elif date_value:
        # Create new task time if date value is provided
        ifcopenshell.api.sequence.add_task_time(
            ifc_file,
            task=task,
            attributes={
                "TaskTimeType": ifc_date_type.upper(),
                ifc_prop_name: date_value,
            },
        )
    # If date_value is None and no task_time exists, do nothing
    
    SequenceData.load()

def updateTaskDuration(self: "Task", context: bpy.types.Context) -> None:
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled:
        return

    if self.duration == "-":
        return

    duration = ifcopenshell.util.date.parse_duration(self.duration)
    if not duration:
        self.duration = "-"
        return

    ifc_file = tool.Ifc.get()
    task = ifc_file.by_id(self.ifc_definition_id)
    task_time = task.TaskTime
    if task_time:
        ifcopenshell.api.sequence.edit_task_time(
            ifc_file,
            task_time=task_time,
            attributes={"ScheduleDuration": duration},
        )
    else:
        ifcopenshell.api.sequence.add_task_time(
            ifc_file,
            task=task,
            attributes={"ScheduleDuration": duration},
        )
    SequenceData.load()

def updateTaskPredefinedType(self: "Task", context: bpy.types.Context) -> None:
    """Callback when PredefinedType changes - auto-syncs to DEFAULT group"""
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled:
        return
    try:
        # The IFC attribute editing logic is already handled by the attribute's callback.
        # This callback should only be concerned with UI synchronization.

        # 1. Get the new PredefinedType value directly from the task.
        # This is more reliable than reading from cached data during edit.
        ifc_file = tool.Ifc.get()
        task_ifc = ifc_file.by_id(self.ifc_definition_id)
        current_predefined_type = getattr(task_ifc, 'PredefinedType', 'NOTDEFINED') or 'NOTDEFINED'
        
        print(f"🔄 PredefinedType changed callback: Task {self.ifc_definition_id} → {current_predefined_type}")

        # 2. Sync to DEFAULT group (only if no custom groups exist to avoid confusion)
        user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
        if not user_groups:
            UnifiedColorTypeManager.sync_default_group_to_predefinedtype(context, self)
            print(f"[DEBUG] Task {self.ifc_definition_id} DEFAULT group synced to {current_predefined_type}")
        else:
            print(f"[WARNING] Custom groups detected - DEFAULT sync skipped for task {self.ifc_definition_id}")

        # 3. Force UI refresh to reflect changes
        refresh_sequence_data()

    except Exception as e:
        print(f"[ERROR] Error in updateTaskPredefinedType: {e}")
        import traceback
        traceback.print_exc()

def updateAssignedResourceName(self, context):
    pass

def updateAssignedResourceUsage(self: "TaskResource", context: object) -> None:
    props = tool.Resource.get_resource_props()
    if not props.is_resource_update_enabled:
        return
    if not self.schedule_usage:
        return
    resource = tool.Ifc.get().by_id(self.ifc_definition_id)
    if resource.Usage and resource.Usage.ScheduleUsage == self.schedule_usage:
        return
    tool.Resource.run_edit_resource_time(resource, attributes={"ScheduleUsage": self.schedule_usage})
    tool.Sequence.load_task_properties()

def update_task_bar_list(self: "Task", context: bpy.types.Context) -> None:
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled:
        return
    
    # Add or remove from the list
    if self.has_bar_visual:
        tool.Sequence.add_task_bar(self.ifc_definition_id)
    else:
        tool.Sequence.remove_task_bar(self.ifc_definition_id)
    
    # Force viewport refresh to update bars
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()

def update_use_active_colortype_group(self: "Task", context):
    """Updates usage of the active colortype group"""
    try:
        anim_props = tool.Sequence.get_animation_props()
        selected_group = getattr(anim_props, "task_colortype_group_selector", "")
        
        # CRITICAL: Use the group selected in task_colortype_group_selector, NOT ColorType_groups
        if selected_group and selected_group != "DEFAULT":
            entry = UnifiedColorTypeManager.sync_task_colortypes(context, self, selected_group)
            if entry:
                entry.enabled = bool(self.use_active_colortype_group)
                print(f"[DEBUG] Task {self.ifc_definition_id}: Active group '{selected_group}' enabled = {entry.enabled}")
                
                # NEW FUNCTIONALITY: Auto-sync animation_color_schemes
                if entry.enabled and entry.selected_colortype:
                    from .animation import safe_set_animation_color_schemes
                    safe_set_animation_color_schemes(self, entry.selected_colortype)
                    print(f"🔄 AUTO-SYNC: animation_color_schemes = '{entry.selected_colortype}'")
            else:
                print(f"[ERROR] Could not sync task {self.ifc_definition_id} with group '{selected_group}'")
        else:
            print(f"[WARNING] No valid custom group selected: '{selected_group}'")
    except Exception as e:
        print(f"[ERROR] Error in update_use_active_colortype_group: {e}")

def update_selected_colortype_in_active_group(self: "Task", context):
    """Updates the selected colortype in the active group"""
    try:
        # Validate that the current value is not a numeric string or invalid
        current_value = self.selected_colortype_in_active_group
        
        # Get valid enum items to check against
        valid_items = get_custom_group_colortype_items(self, context)
        valid_values = [item[0] for item in valid_items]
        
        # Check for invalid values
        if current_value and (current_value.isdigit() or current_value not in valid_values):
            print(f"🚫 Invalid colortype value '{current_value}' detected, correcting...")
            # Don't assign anything - let the enum system handle it
            return
        
        # Get animation properties to determine active group
        anim_props = tool.Sequence.get_animation_props()
        selected_group = getattr(anim_props, "task_colortype_group_selector", "")
        
        if not selected_group or selected_group == "DEFAULT":
            print(f"[WARNING] No valid custom group selected for task {self.ifc_definition_id}")
            return
        
        # Update the mapping in the task's colortype_group_choices
        entry = UnifiedColorTypeManager.sync_task_colortypes(context, self, selected_group)
        if entry:
            entry.selected_colortype = current_value
            print(f"[DEBUG] Task {self.ifc_definition_id}: Group '{selected_group}' colortype = '{current_value}'")
            
            # NEW FUNCTIONALITY: Auto-sync with animation_color_schemes if the group is active
            if entry.enabled and current_value:
                from .animation import safe_set_animation_color_schemes
                safe_set_animation_color_schemes(self, current_value)
                print(f"🔄 AUTO-SYNC: animation_color_schemes = '{current_value}'")
                
    except Exception as e:
        print(f"[ERROR] Error in update_selected_colortype_in_active_group: {e}")

def update_variance_color_mode(self, context):
    """Updates variance color mode visualization"""
    try:
        wprops = tool.Sequence.get_work_schedule_props()
        
        if self.is_variance_color_selected:
            # Add task to variance selection if not already present
            if str(self.ifc_definition_id) not in wprops.variance_selected_tasks:
                task_item = wprops.variance_selected_tasks.add()
                task_item.task_id = str(self.ifc_definition_id)
                print(f"[DEBUG] Added task {self.ifc_definition_id} to variance color selection")
        else:
            # Remove task from variance selection
            to_remove = []
            for i, item in enumerate(wprops.variance_selected_tasks):
                if item.task_id == str(self.ifc_definition_id):
                    to_remove.append(i)
            
            for idx in reversed(to_remove):
                wprops.variance_selected_tasks.remove(idx)
                print(f"[DEBUG] Removed task {self.ifc_definition_id} from variance color selection")
        
        # Refresh viewport to update colors
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
                
    except Exception as e:
        print(f"[ERROR] Error in update_variance_color_mode: {e}")

# ============================================================================
# TASK PROPERTY GROUP CLASSES
# ============================================================================

class TaskcolortypeGroupChoice(PropertyGroup):
    """colortype group mapping for each task"""
    group_name: StringProperty(name="Group Name")
    enabled: BoolProperty(name="Enabled")
    selected_colortype: StringProperty(name="Selected colortype")
    
    if TYPE_CHECKING:
        group_name: str
        enabled: bool
        selected_colortype: str

class Task(PropertyGroup):
    """Task properties with improved colortype support"""
    # colortype mapping by group
    colortype_group_choices: CollectionProperty(name="colortype Group Choices", type=TaskcolortypeGroupChoice)
    use_active_colortype_group: BoolProperty(
        name="Use Active Group", 
        default=False, 
        update=update_use_active_colortype_group
    )
    selected_colortype_in_active_group: EnumProperty(
        name="colortype in Active Group",
        description="Select colortype within the active custom group (excludes DEFAULT)",
        items=get_custom_group_colortype_items,
        update=update_selected_colortype_in_active_group
    )
    
    # Basic task properties
    animation_color_schemes: EnumProperty(name="Animation Color Scheme", items=get_animation_color_schemes_items)
    name: StringProperty(name="Name", update=updateTaskName)
    identification: StringProperty(name="Identification", update=updateTaskIdentification)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_selected: BoolProperty(
        name="Is Selected",
        update=update_task_checkbox_selection
    )
    is_expanded: BoolProperty(name="Is Expanded")
    has_bar_visual: BoolProperty(name="Show Task Bar Animation", default=False, update=update_task_bar_list)
    level_index: IntProperty(name="Level Index")
    
    # Times
    duration: StringProperty(name="Duration", update=updateTaskDuration)
    start: StringProperty(name="Start", update=updateTaskTimeStart)
    finish: StringProperty(name="Finish", update=updateTaskTimeFinish)
    actual_start: StringProperty(name="Actual Start", update=updateTaskTimeActualStart)
    actual_finish: StringProperty(name="Actual Finish", update=updateTaskTimeActualFinish)
    early_start: StringProperty(name="Early Start", update=updateTaskTimeEarlyStart)
    early_finish: StringProperty(name="Early Finish", update=updateTaskTimeEarlyFinish)
    late_start: StringProperty(name="Late Start", update=updateTaskTimeLateStart)
    late_finish: StringProperty(name="Late Finish", update=updateTaskTimeLateFinish)
    calendar: StringProperty(name="Calendar")
    derived_start: StringProperty(name="Derived Start")
    derived_finish: StringProperty(name="Derived Finish")
    derived_actual_start: StringProperty(name="Derived Actual Start")
    derived_actual_finish: StringProperty(name="Derived Actual Finish")
    derived_early_start: StringProperty(name="Derived Early Start")
    derived_early_finish: StringProperty(name="Derived Early Finish")
    derived_late_start: StringProperty(name="Derived Late Start")
    derived_late_finish: StringProperty(name="Derived Late Finish")
    derived_duration: StringProperty(name="Derived Duration")
    derived_calendar: StringProperty(name="Derived Calendar")
    
    # Relationships
    is_predecessor: BoolProperty(name="Is Predecessor")
    is_successor: BoolProperty(name="Is Successor")
    
    # Variance Analysis Properties
    variance_status: StringProperty(
        name="Variance Status",
        description="Shows if the task is Ahead, Delayed, or On Time based on the last variance calculation"
    )
    variance_days: IntProperty(
        name="Variance (Days)",
        description="The difference in days between the two compared date sets (positive for delayed, negative for ahead)"
    )
    outputs_count: IntProperty(name="Element 3D Count", description="Total number of 3D elements assigned to task (inputs + outputs)")
    
    # Variance color mode checkbox
    is_variance_color_selected: BoolProperty(
        name="Variance Color Mode",
        description="Select this task for variance color mode visualization",
        default=False,
        update=update_variance_color_mode
    )
    
    if TYPE_CHECKING:
        colortype_group_choices: bpy.types.bpy_prop_collection_idprop[TaskcolortypeGroupChoice]
        use_active_colortype_group: bool
        selected_colortype_in_active_group: str
        animation_color_schemes: str
        name: str
        identification: str
        ifc_definition_id: int
        has_children: bool
        is_selected: bool
        is_expanded: bool
        has_bar_visual: bool
        level_index: int
        duration: str
        start: str
        finish: str
        calendar: str
        derived_start: str
        derived_finish: str
        derived_duration: str
        derived_calendar: str
        actual_start: str
        actual_finish: str
        derived_actual_start: str
        derived_actual_finish: str
        early_start: str
        early_finish: str
        derived_early_start: str
        derived_early_finish: str
        late_start: str
        late_finish: str
        derived_late_start: str
        derived_late_finish: str
        is_predecessor: bool
        is_successor: bool
        outputs_count: int
        variance_status: str
        variance_days: int
        is_variance_color_selected: bool

class TaskResource(PropertyGroup):
    """Task resource properties"""
    name: StringProperty(name="Name", update=updateAssignedResourceName)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    schedule_usage: FloatProperty(name="Schedule Usage", update=updateAssignedResourceUsage)
    
    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int
        schedule_usage: float

class TaskProduct(PropertyGroup):
    """Task product properties"""
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    
    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int

class BIMTaskTreeProperties(PropertyGroup):
    """Task tree collection - separate for performance reasons"""
    # This belongs by itself for performance reasons. https://developer.blender.org/T87737
    tasks: CollectionProperty(name="Tasks", type=Task)
    
    if TYPE_CHECKING:
        tasks: bpy.types.bpy_prop_collection_idprop[Task]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_date_source_items(self, context):
    """Helper for EnumProperty items to select date sources."""
    return [
        ('SCHEDULE', "Schedule", "Use Schedule dates"),
        ('ACTUAL', "Actual", "Use Actual dates"),
        ('EARLY', "Early", "Use Early dates"),
        ('LATE', "Late", "Use Late dates"),
    ]