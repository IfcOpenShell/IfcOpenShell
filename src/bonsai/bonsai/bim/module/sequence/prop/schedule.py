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
import bonsai.tool as tool
import bonsai.core.sequence as core
from bonsai.bim.module.sequence.data import SequenceData
from bonsai.bim.prop import Attribute, ISODuration
from . import callbacks_prop
from . import enums_prop

# Import snapshot functions
try:
    from ..operators.operator import snapshot_all_ui_state
    from ..operators.schedule_task_operators import restore_all_ui_state
except ImportError:
    # Fallback functions if imports fail
    def snapshot_all_ui_state(context):
        pass
    def restore_all_ui_state(context):
        pass

# Global flag to prevent recursive callback execution during restore
_CALLBACK_LOCK = False
from dateutil import parser
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    CollectionProperty,
)
from typing import TYPE_CHECKING, Literal

# Import from other modules
try:
    from .task import TaskResource, TaskProduct, get_date_source_items
    from .filter import BIMTaskFilterProperties, SavedFilterSet
except ImportError:
    # Fallback for when running from the original location
    from .task import TaskResource, TaskProduct, get_date_source_items
    from .filter import BIMTaskFilterProperties, SavedFilterSet

# ============================================================================
# SCHEDULE CALLBACK FUNCTIONS
# ============================================================================

def update_variance_calculation(self, context):
    """Callback when chronogram types change - does NOT automatically calculate variance."""
    # FIXED: Remove automatic calculation when changing chronogram type
    # User must press Calculate button to calculate variance
    pass

def update_active_work_schedule_id(self, context):
    """
    Callback que se ejecuta cuando cambia el schedule activo.
    Guarda automáticamente los perfiles del schedule anterior y carga los del nuevo.
    """
    try:
        import bonsai.tool as tool
        # DEBUG: Check that the callback is running
        current_ws_id = getattr(self, 'active_work_schedule_id', 0)
        previous_ws_id = getattr(context.scene, '_previous_work_schedule_id', 0)
        print(f"🔄 DEBUG: Callback ejecutado - Cambio de WS {previous_ws_id} → {current_ws_id}")
        
        # Skip if it's the same schedule or invalid
        if current_ws_id == previous_ws_id or current_ws_id <= 0:
            return
        
        # Save current state
        context.scene['_previous_work_schedule_id'] = current_ws_id
        print(f"[DEBUG] DEBUG: _previous_work_schedule_id guardado: {current_ws_id}")
        
        # Defer the heavy loading operations
        def deferred_load():
            try:
                print(f"🔄 Loading tasks for work schedule: {current_ws_id}")
                core.load_task_tree(tool.Sequence, work_schedule=tool.Ifc.get().by_id(current_ws_id))
                print(f"[DEBUG] Tasks loaded for work schedule: {current_ws_id}")
            except Exception as e:
                print(f"[ERROR] Error loading tasks for work schedule {current_ws_id}: {e}")
            return None
        
        bpy.app.timers.register(deferred_load, first_interval=0.1)
        
    except Exception as e:
        print(f"[ERROR] Error in update_active_work_schedule_id: {e}")

def update_active_task_index(self, context):
    """
    Updates active task index, synchronizes colortypes,
    and selects associated 3D objects in the viewport (for single click).
    """
    task_ifc = tool.Sequence.get_highlighted_task()
    self.highlighted_task_id = task_ifc.id() if task_ifc else 0
    tool.Sequence.update_task_ICOM(task_ifc)
    
    # Import pset data module 
    import bonsai.bim.module.pset.data
    bonsai.bim.module.pset.data.refresh()

    if self.editing_task_type == "SEQUENCE":
        return

    tprops = tool.Sequence.get_task_tree_props()
    if not tprops.tasks or self.active_task_index >= len(tprops.tasks):
        return

    task = tprops.tasks[self.active_task_index]

    # --- START: Automatic synchronization ---
    try:
        # Import UnifiedColorTypeManager from animation module
        from .animation import UnifiedColorTypeManager
        
        # Sync DEFAULT group (only if no custom groups exist)
        user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
        if not user_groups:
            UnifiedColorTypeManager.sync_default_group_to_predefinedtype(context, task)
            print(f"[DEBUG] Task {task.ifc_definition_id}: DEFAULT group synchronized")
        
        # Load active animation colortype group colortypes (only if selected)
        anim_props = tool.Sequence.get_animation_props()
        selected_group = getattr(anim_props, "task_colortype_group_selector", "")
        if selected_group and selected_group != "DEFAULT":
            UnifiedColorTypeManager.load_colortypes_into_collection(anim_props, context, selected_group)
            print(f"[DEBUG] Animation colortypes loaded for group: {selected_group}")
    except Exception as e:
        print(f"[WARNING] Error in automatic colortype synchronization: {e}")
    
    # --- 3D SELECTION LOGIC FOR SINGLE CLICK ---
    props = tool.Sequence.get_work_schedule_props()
    if props.should_select_3d_on_task_click:
        if not task_ifc:
            try:
                import bpy
                bpy.ops.object.select_all(action='DESELECT')
            except RuntimeError:
                # Occurs if we're not in object mode, safe to ignore
                pass
            return
        
        try:
            import bpy
            outputs = tool.Sequence.get_task_outputs(task_ifc)
            
            # Deselect everything first
            if bpy.context.view_layer.objects.active:
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            
            if outputs:
                objects_to_select = [tool.Ifc.get_object(p) for p in outputs if tool.Ifc.get_object(p)]
                
                if objects_to_select:
                    for obj in objects_to_select:
                        # Make sure object is visible and selectable
                        obj.hide_set(False)
                        obj.hide_select = False
                        obj.select_set(True)
                    
                    # Set the first object as active
                    bpy.context.view_layer.objects.active = objects_to_select[0]
                    print(f"🎯 3D Task: Selected {len(objects_to_select)} objects for task '{task_ifc.Name or task_ifc.id()}'")
        except Exception as e:
            print(f"[WARNING] Error in 3D selection: {e}")


def update_work_schedule_predefined_type(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    """Se ejecuta cuando cambia el tipo de schedule - NO limpiar automáticamente"""
    try:
        print(f"🔄 Work schedule predefined type changed to: {self.work_schedule_predefined_types}")
        print("ℹ️ Variance colors will remain active - use Clear Variance button to reset")
            
    except Exception as e:
        print(f"[WARNING] Error in update_work_schedule_predefined_type: {e}")

def update_visualisation_start(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    update_visualisation_start_finish(self, context, "visualisation_start")

def update_visualisation_finish(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    update_visualisation_start_finish(self, context, "visualisation_finish")

def update_visualisation_start_finish(
    self: "BIMWorkScheduleProperties",
    context: bpy.types.Context,
    startfinish: Literal["visualisation_start", "visualisation_finish"],
) -> None:
    startfinish_value = getattr(self, startfinish)
    try:
        startfinish_datetime = parser.isoparse(startfinish_value)
    except Exception:
        try:
            startfinish_datetime = parser.parse(startfinish_value, dayfirst=True, fuzzy=True)
        except Exception:
            # If parsing fails, don't crash - just return
            return
    
    # Store the parsed datetime back as ISO format
    setattr(self, startfinish, startfinish_datetime.isoformat())
    
    # Update frame range when dates change
    if self.visualisation_start and self.visualisation_finish:
        try:
            start_datetime = parser.isoparse(self.visualisation_start)
            finish_datetime = parser.isoparse(self.visualisation_finish)
            
            # Calculate duration and frame range
            duration_days = (finish_datetime - start_datetime).days
            if duration_days > 0:
                # Set reasonable frame range based on duration
                frame_end = max(250, min(duration_days * 10, 10000))
                context.scene.frame_end = frame_end
                print(f"[DEBUG] Updated frame range to {frame_end} frames for {duration_days} day duration")
        except Exception as e:
            print(f"[WARNING] Error updating frame range: {e}")

def update_sort_reversed(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    print(f"[DEBUG CALLBACK] *** SCHEDULE.PY update_sort_reversed CALLED (THIS SHOULD NOT BE USED) ***")
    global _CALLBACK_LOCK

    # Prevent recursive execution during restore operations
    if _CALLBACK_LOCK:
        print(f"[DEBUG] schedule.py update_sort_reversed: SKIPPED - callback locked during restore")
        return

    if self.active_work_schedule_id:
        try:
            _CALLBACK_LOCK = True
            print(f"[DEBUG] schedule.py update_sort_reversed: Starting - taking snapshot")
            snapshot_all_ui_state(context)
            print(f"[DEBUG] schedule.py update_sort_reversed: Loading task tree")
            core.load_task_tree(
                tool.Sequence,
                work_schedule=tool.Ifc.get().by_id(self.active_work_schedule_id),
            )
            # MISSING: load_task_properties() - this might be the key difference!
            tool.Sequence.load_task_properties()
            print(f"[DEBUG] schedule.py update_sort_reversed: Restoring snapshot")
            restore_all_ui_state(context)

            # FORCE a delayed restore to ensure it sticks
            def delayed_restore():
                print(f"[DEBUG] schedule.py update_sort_reversed: DELAYED restore attempt")
                restore_all_ui_state(context)
                global _CALLBACK_LOCK
                _CALLBACK_LOCK = False  # Unlock after delayed restore
                return None

            import bpy
            bpy.app.timers.register(delayed_restore, first_interval=0.1)
            print(f"[DEBUG] schedule.py update_sort_reversed: Completed")
        except Exception as e:
            _CALLBACK_LOCK = False  # Unlock on error
            print(f"[ERROR] schedule.py update_sort_reversed failed: {e}")
            raise

def update_filter_by_active_schedule(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    if obj := context.active_object:
        product = tool.Ifc.get_entity(obj)
        assert product
        core.load_product_related_tasks(tool.Sequence, product=product)


def update_date_source_type(self, context):
    """
    Simple callback when the user changes schedule type.
    Only updates date range using Guess functionality.
    """
    try:
        print(f"📅 Date source changed to: {self.date_source_type}")
        
        # Store previous dates for sync animation
        previous_start = self.visualisation_start
        previous_finish = self.visualisation_finish

        # Update date range for the new schedule type using Guess
        bpy.ops.bim.guess_date_range('INVOKE_DEFAULT', work_schedule=self.active_work_schedule_id)
        
        # Call sync animation if it exists
        try:
            bpy.ops.bim.sync_animation_by_date(
                'INVOKE_DEFAULT',
                previous_start_date=previous_start,
                previous_finish_date=previous_finish
            )
        except Exception as e:
            print(f"[WARNING] Animation sync failed: {e}")
                
    except Exception as e:
        print(f"[ERROR] update_date_source_type: Error: {e}")
        import traceback
        traceback.print_exc()

# Helper functions for enums



def update_active_task_outputs(self, context):
    """Update callback for nested task outputs"""
    task_ifc = tool.Sequence.get_highlighted_task()
    if task_ifc:
        tool.Sequence.update_task_outputs(task_ifc, show_nested=self.show_nested_outputs)

def update_active_task_resources(self, context):
    """Update callback for nested task resources"""
    task_ifc = tool.Sequence.get_highlighted_task()
    if task_ifc:
        tool.Sequence.update_task_resources(task_ifc, show_nested=self.show_nested_resources)

def update_active_task_inputs(self, context):
    """Update callback for nested task inputs"""
    task_ifc = tool.Sequence.get_highlighted_task()
    if task_ifc:
        tool.Sequence.update_task_inputs(task_ifc, show_nested=self.show_nested_inputs)

# ============================================================================
# SCHEDULE PROPERTY GROUP CLASSES
# ============================================================================

class WorkPlan(PropertyGroup):
    """Work plan properties"""
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    
    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int

class BIMWorkPlanProperties(PropertyGroup):
    """Work plan management properties"""
    work_plan_attributes: CollectionProperty(name="Work Plan Attributes", type=Attribute)
    editing_type: EnumProperty(
        items=[("WORK_PLAN", "Work Plan", ""), ("WORK_SCHEDULE", "Work Schedule", "")],
        name="Editing Type"
    )
    work_plans: CollectionProperty(name="Work Plans", type=WorkPlan)
    active_work_plan_index: IntProperty(name="Active Work Plan Index")
    active_work_plan_id: IntProperty(name="Active Work Plan Id")
    work_schedules: EnumProperty(items=enums_prop.getWorkSchedules, name="Work Schedules")
    
    if TYPE_CHECKING:
        work_plan_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        editing_type: str
        work_plans: bpy.types.bpy_prop_collection_idprop[WorkPlan]
        active_work_plan_index: int
        active_work_plan_id: int
        work_schedules: str

class BIMWorkScheduleProperties(PropertyGroup):
    """Main work schedule properties with comprehensive task and animation management"""
    
    # Basic schedule properties
    work_schedule_predefined_types: EnumProperty(
        items=enums_prop.get_schedule_predefined_types, 
        name="Predefined Type", 
        default=None, 
        update=update_work_schedule_predefined_type
    )
    object_type: StringProperty(name="Object Type")
    durations_attributes: CollectionProperty(name="Durations Attributes", type=ISODuration)
    work_calendars: EnumProperty(items=lambda self, context: [], name="Work Calendars")  # Will be populated
    work_schedule_attributes: CollectionProperty(name="Work Schedule Attributes", type=Attribute)
    editing_type: StringProperty(name="Editing Type")
    editing_task_type: StringProperty(name="Editing Task Type")
    
    # Active schedule and task management
    active_work_schedule_index: IntProperty(name="Active Work Schedules Index")
    active_work_schedule_id: IntProperty(name="Active Work Schedules Id", update=update_active_work_schedule_id)
    active_task_index: IntProperty(name="Active Task Index", update=update_active_task_index)
    active_task_id: IntProperty(name="Active Task Id")
    highlighted_task_id: IntProperty(name="Highlighted Task Id")
    
    # Task attributes and editing
    task_attributes: CollectionProperty(name="Task Attributes", type=Attribute)
    is_task_update_enabled: BoolProperty(name="Is Task Update Enabled", default=True)
    
    # UI toggles and options
    should_show_visualisation_ui: BoolProperty(name="Should Show Visualisation UI", default=True, update=callbacks_prop.switch_options)
    should_show_task_bar_selection: BoolProperty(name="Add to task bar", default=False)
    should_show_snapshot_ui: BoolProperty(name="Should Show Snapshot UI", default=False, update=callbacks_prop.switch_options2)
    should_show_column_ui: BoolProperty(name="Should Show Column UI", default=False)
    should_show_schedule_baseline_ui: BoolProperty(name="Baselines", default=False)
    should_select_3d_on_task_click: BoolProperty(
        name="Select 3D on Task Click",
        description="Automatically select 3D elements when a task is selected in the list",
        default=True
    )
    
    # Column management
    columns: CollectionProperty(name="Columns", type=Attribute)
    active_column_index: IntProperty(name="Active Column Index")
    sort_column: StringProperty(name="Sort Column")
    is_sort_reversed: BoolProperty(name="Is Sort Reversed", update=update_sort_reversed)
    column_types: EnumProperty(
        items=[
            ("IfcTask", "IfcTask", ""),
            ("IfcTaskTime", "IfcTaskTime", ""),
            ("Special", "Special", ""),
        ],
        name="Column Types",
    )
    task_columns: EnumProperty(items=enums_prop.getTaskColumns, name="Task Columns")
    task_time_columns: EnumProperty(items=enums_prop.getTaskTimeColumns, name="Task Time Columns")
    other_columns: EnumProperty(
        items=[
            ("Controls.Calendar", "Calendar", ""),
        ],
        name="Special Columns",
    )
    
    # Column navigation properties
    column_start_index: IntProperty(
        name="Column Start Index",
        description="Starting index for visible columns",
        default=0,
        min=0
    )
    columns_per_view: IntProperty(
        name="Columns Per View", 
        description="Maximum number of columns to display at once",
        default=5,
        min=1,
        max=20
    )
    
    # Task time and sequence management
    active_task_time_id: IntProperty(name="Active Task Time Id")
    task_time_attributes: CollectionProperty(name="Task Time Attributes", type=Attribute)
    contracted_tasks: StringProperty(name="Contracted Task Items", default="[]")
    task_bars: StringProperty(name="Checked Task Items", default="[]")
    editing_sequence_type: StringProperty(name="Editing Sequence Type")
    active_sequence_id: IntProperty(name="Active Sequence Id")
    sequence_attributes: CollectionProperty(name="Sequence Attributes", type=Attribute)
    lag_time_attributes: CollectionProperty(name="Time Lag Attributes", type=Attribute)
    
    # Date source and visualization
    date_source_type: EnumProperty(
        name="Date Source",
        description="Choose which set of dates to use for animation and snapshots",
        items=[
            ('SCHEDULE', "Schedule", "Use ScheduleStart and ScheduleFinish dates"),
            ('ACTUAL', "Actual", "Use ActualStart and ActualFinish dates"),
            ('EARLY', "Early", "Use EarlyStart and EarlyFinish dates"),
            ('LATE', "Late", "Use LateStart and LateFinish dates"),
        ],
        default='SCHEDULE',
        update=update_date_source_type
    )
    visualisation_start: StringProperty(name="Visualisation Start", update=update_visualisation_start)
    visualisation_finish: StringProperty(name="Visualisation Finish", update=update_visualisation_finish)
    
    # Animation speed and timing
    speed_multiplier: FloatProperty(name="Speed Multiplier", default=10000)
    speed_animation_duration: StringProperty(name="Speed Animation Duration", default="1 s")
    speed_animation_frames: IntProperty(name="Speed Animation Frames", default=24)
    speed_real_duration: StringProperty(name="Speed Real Duration", default="1 w")
    speed_types: EnumProperty(
        items=[
            ("FRAME_SPEED", "Frame-based", "e.g. 25 frames = 1 real week"),
            ("DURATION_SPEED", "Duration-based", "e.g. 1 video second = 1 real week"),
            ("MULTIPLIER_SPEED", "Multiplier", "e.g. 1000 x real life speed"),
        ],
        name="Speed Type",
        default="FRAME_SPEED",
    )
    
    # Task resources and products
    task_resources: CollectionProperty(name="Task Resources", type=TaskResource)
    active_task_resource_index: IntProperty(name="Active Task Resource Index")
    task_inputs: CollectionProperty(name="Task Inputs", type=TaskProduct)
    active_task_input_index: IntProperty(name="Active Task Input Index")
    task_outputs: CollectionProperty(name="Task Outputs", type=TaskProduct)
    active_task_output_index: IntProperty(name="Active Task Output Index")
    product_input_tasks: CollectionProperty(name="Product Task Inputs", type=TaskProduct)
    product_output_tasks: CollectionProperty(name="Product Task Outputs", type=TaskProduct)
    active_product_output_task_index: IntProperty(name="Active Product Output Task Index")
    active_product_input_task_index: IntProperty(name="Active Product Input Task Index")
    
    # Display options for nested items
    show_saved_colortypes_section: BoolProperty(name="Show Saved colortypes", default=True)
    show_nested_outputs: BoolProperty(name="Show Nested Tasks", default=False, update=update_active_task_outputs)
    show_nested_resources: BoolProperty(name="Show Nested Tasks", default=False, update=update_active_task_resources)
    show_nested_inputs: BoolProperty(name="Show Nested Tasks", default=False, update=update_active_task_inputs)
    
    # Task management options
    enable_reorder: BoolProperty(name="Enable Reorder", default=False)
    show_task_operators: BoolProperty(name="Show Task Options", default=True)
    filter_by_active_schedule: BoolProperty(
        name="Filter By Active Schedule", 
        default=False, 
        update=update_filter_by_active_schedule
    )
    selected_tasks_count: IntProperty(name="Selected Tasks Count", default=0)
    
    # Lookahead analysis
    last_lookahead_window: StringProperty(
        name="Last Lookahead Window",
        description="Stores the last selected lookahead time window to allow re-applying it automatically.",
        default=""
    )
    
    # Filtering and saved filter sets
    filters: PointerProperty(type=BIMTaskFilterProperties)
    saved_filter_sets: CollectionProperty(type=SavedFilterSet)
    active_saved_filter_set_index: IntProperty()
    
    # Variance analysis
    variance_source_a: EnumProperty(
        name="Compare",
        items=get_date_source_items,
        default=0,
        description="The baseline date set for comparison",
        update=update_variance_calculation,
    )
    variance_source_b: EnumProperty(
        name="With",
        items=get_date_source_items,
        default=1,
        description="The date set to compare against the baseline",
        update=update_variance_calculation,
    )
    
    if TYPE_CHECKING:
        saved_filter_sets: bpy.types.bpy_prop_collection_idprop[SavedFilterSet]
        active_saved_filter_set_index: int
        work_schedule_predefined_types: str
        object_type: str
        durations_attributes: bpy.types.bpy_prop_collection_idprop[ISODuration]
        work_calendars: str
        work_schedule_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        editing_type: str
        editing_task_type: str
        active_work_schedule_index: int
        active_work_schedule_id: int
        active_task_index: int
        active_task_id: int
        last_lookahead_window: str
        date_source_type: str
        highlighted_task_id: int
        task_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        should_show_visualisation_ui: bool
        should_show_task_bar_selection: bool
        should_show_snapshot_ui: bool
        should_show_column_ui: bool
        should_show_schedule_baseline_ui: bool
        should_select_3d_on_task_click: bool
        columns: bpy.types.bpy_prop_collection_idprop[Attribute]
        active_column_index: int
        sort_column: str
        is_sort_reversed: bool
        column_types: str
        task_columns: str
        task_time_columns: str
        other_columns: str
        column_start_index: int
        columns_per_view: int
        active_task_time_id: int
        task_time_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        contracted_tasks: str
        task_bars: str
        is_task_update_enabled: bool
        editing_sequence_type: str
        active_sequence_id: int
        sequence_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        lag_time_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        visualisation_start: str
        visualisation_finish: str
        speed_multiplier: float
        speed_animation_duration: str
        speed_animation_frames: int
        speed_real_duration: str
        speed_types: str
        task_resources: bpy.types.bpy_prop_collection_idprop[TaskResource]
        active_task_resource_index: int
        task_inputs: bpy.types.bpy_prop_collection_idprop[TaskProduct]
        active_task_input_index: int
        task_outputs: bpy.types.bpy_prop_collection_idprop[TaskProduct]
        active_task_output_index: int
        product_input_tasks: bpy.types.bpy_prop_collection_idprop[TaskProduct]
        product_output_tasks: bpy.types.bpy_prop_collection_idprop[TaskProduct]
        active_product_output_task_index: int
        active_product_input_task_index: int
        show_saved_colortypes_section: bool
        show_nested_outputs: bool
        show_nested_resources: bool
        show_nested_inputs: bool
        enable_reorder: bool
        show_task_operators: bool
        filter_by_active_schedule: bool
        selected_tasks_count: int
        variance_source_a: str
        variance_source_b: str

# ============================================================================
# ADDITIONAL SCHEDULE HELPER FUNCTIONS
# ============================================================================


def getWorkCalendars(self, context):
    """Work calendars enum function"""
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["work_calendars_enum"]



