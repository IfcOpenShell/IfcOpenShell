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
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty, StringProperty, EnumProperty,
    BoolProperty, IntProperty, FloatProperty, CollectionProperty
)
from typing import TYPE_CHECKING, Literal
from . import callbacks_prop as callbacks, enums_prop as enums, filter


class TaskFilterRule(PropertyGroup):
    """Defines a filter rule with support for multiple data types."""
    is_active: BoolProperty(name="Active", default=True, description="Enable or disable this filter rule")

    column: EnumProperty(
        name="Column",
        description="The column to apply the filter on",
        items=enums.get_all_task_columns_enum,
        update=filter.update_filter_column
    )
    
    operator: EnumProperty(
        name="Operator",
        description="The comparison operation to perform",
        items=enums.get_operator_items
    )
    
    # Internal property to store the current data type
    data_type: StringProperty(name="Data Type", default='string')

    # Specific value fields for each data type
    value_string: StringProperty(name="Value", description="Value for text or date filters")
    value_integer: IntProperty(name="Value", description="Value for integer number filters")
    value_float: FloatProperty(name="Value", description="Value for decimal number filters")
    value_boolean: BoolProperty(name="Value", description="Value for true/false filters")


class BIMTaskFilterProperties(PropertyGroup):
    """Stores the complete configuration of the filter system."""
    rules: CollectionProperty(
        name="Filter Rules",
        type=TaskFilterRule,
    )
    active_rule_index: IntProperty(
        name="Active Filter Rule Index",
    )
    logic: EnumProperty(
        name="Filter Logic",
        description="How multiple filter rules are combined",
        items=[
            ('AND', "Match All (AND)", "Show tasks that meet ALL active rules"),
            ('OR', "Match Any (OR)", "Show tasks that meet AT LEAST ONE active rule"),
        ],
        default='AND',
    )
    show_filters: BoolProperty(
        name="Show Filters",
        description="Shows or hides the filter configuration panel",
        default=False,
    )
    # --- ADDED PROPERTY ---
    show_saved_filters: BoolProperty(
        name="Show Saved Filters",
        description="Shows or hides the saved filters panel",
        default=False,
    )

    def to_json_data(self):
        """Serializes the filter state to a Python dictionary."""
        rules_data = []
        for rule in self.rules:
            rules_data.append({
                "is_active": rule.is_active,
                "column": rule.column,
                "operator": rule.operator,
                "data_type": rule.data_type,
                "value_string": rule.value_string,
                "value_integer": rule.value_integer,
                "value_float": rule.value_float,
                "value_boolean": rule.value_boolean,
            })
        return {
            "rules": rules_data,
            "logic": self.logic,
            "show_filters": self.show_filters,
            "show_saved_filters": self.show_saved_filters,
            "active_rule_index": self.active_rule_index,
        }

    def from_json_data(self, data):
        """Restores the filter state from a Python dictionary."""
        self.rules.clear()
        self.logic = data.get("logic", "AND")
        self.show_filters = data.get("show_filters", False)
        self.show_saved_filters = data.get("show_saved_filters", False)
        for rule_data in data.get("rules", []):
            new_rule = self.rules.add()
            for key, value in rule_data.items():
                if hasattr(new_rule, key):
                    setattr(new_rule, key, value)
        self.active_rule_index = data.get("active_rule_index", 0)


class SavedFilterSet(PropertyGroup):
    """Stores a set of filter rules with a name."""
    name: StringProperty(name="Set Name")
    rules: CollectionProperty(type=TaskFilterRule)


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
        update=callbacks.update_use_active_colortype_group
    )
    selected_colortype_in_active_group: EnumProperty(
        name="colortype in Active Group",
        description="Select colortype within the active custom group (excludes DEFAULT)",
        items=enums.get_custom_group_colortype_items, # <-- CRITICAL CHANGE HERE
        update=callbacks.update_selected_colortype_in_active_group
    )
    
    # Basic task properties
    animation_color_schemes: EnumProperty(name="Animation Color Scheme", items=enums.get_animation_color_schemes_items)
    name: StringProperty(name="Name", update=callbacks.updateTaskName)
    identification: StringProperty(name="Identification", update=callbacks.updateTaskIdentification)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_selected: BoolProperty(
        name="Is Selected",
        update=callbacks.update_task_checkbox_selection
    )
    is_expanded: BoolProperty(name="Is Expanded")
    has_bar_visual: BoolProperty(name="Show Task Bar Animation", default=False, update=callbacks.update_task_bar_list)
    level_index: IntProperty(name="Level Index")
    
    # Times
    duration: StringProperty(name="Duration", update=callbacks.updateTaskDuration)
    start: StringProperty(name="Start", update=callbacks.updateTaskTimeStart)
    finish: StringProperty(name="Finish", update=callbacks.updateTaskTimeFinish)
    actual_start: StringProperty(name="Actual Start", update=callbacks.updateTaskTimeActualStart)
    actual_finish: StringProperty(name="Actual Finish", update=callbacks.updateTaskTimeActualFinish)
    early_start: StringProperty(name="Early Start", update=callbacks.updateTaskTimeEarlyStart)
    early_finish: StringProperty(name="Early Finish", update=callbacks.updateTaskTimeEarlyFinish)
    late_start: StringProperty(name="Late Start", update=callbacks.updateTaskTimeLateStart)
    late_finish: StringProperty(name="Late Finish", update=callbacks.updateTaskTimeLateFinish)
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
    # --- START: Variance Analysis Properties ---
    variance_status: StringProperty(
        name="Variance Status",
        description="Shows if the task is Ahead, Delayed, or On Time based on the last variance calculation"
    )
    variance_days: IntProperty(
        name="Variance (Days)",
        description="The difference in days between the two compared date sets (positive for delayed, negative for ahead)"
    )
    outputs_count: IntProperty(name="Element 3D Count", description="Total number of 3D elements assigned to task (inputs + outputs)")
    inputs_count: IntProperty(name="Inputs Count", description="Number of elements assigned as task inputs")
    
    # Variance color mode checkbox
    is_variance_color_selected: BoolProperty(
        name="Variance Color Mode",
        description="Select this task for variance color mode visualization",
        default=False,
        update=lambda self, context: callbacks.update_variance_color_mode(self, context)
    )
    
    
    if TYPE_CHECKING:
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


class TaskResource(PropertyGroup):
    name: StringProperty(name="Name", update=callbacks.updateAssignedResourceName)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    schedule_usage: FloatProperty(name="Schedule Usage", update=callbacks.updateAssignedResourceUsage)
    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int
        schedule_usage: float


class TaskProduct(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int


WorkPlanEditingType = Literal["-", "ATTRIBUTES", "SCHEDULES", "WORK_SCHEDULE", "TASKS", "WORKTIMES"]


class BIMTaskTreeProperties(PropertyGroup):
    # This belongs by itself for performance reasons. https://developer.blender.org/T87737
    tasks: CollectionProperty(name="Tasks", type=Task)
    if TYPE_CHECKING:
        tasks: bpy.types.bpy_prop_collection_idprop[Task]