"""User Interface (UI) Panels for 4D BIM Scheduling - Modular Organization.

This package contains the Panel (bpy.types.Panel) and UIList (bpy.types.UIList)
classes, thematically organized to build the addon's interface in Blender.

The structure is as follows:
- panels_schedule.py: Panels for managing schedules, tasks, variance analysis, and ICOM.
- panels_animation.py: Panels dedicated to 4D animation configuration, color schemes, camera control, orbit, and HUD settings.
- panels_workplan.py: Panels for managing Work Plans and Calendars.
- lists_ui.py: Contains reusable UI elements, primarily the UIList classes that display data lists.

The __init__.py file acts as an orchestrator, importing all components and managing
their centralized registration and unregistration within Blender.
"""


import bpy

# 1. Import all classes from the new UI modules
from .animation_ui import (
    BIM_PT_animation_tools,
    BIM_PT_animation_color_schemes,
)
from .lists_ui import (
    BIM_UL_animation_group_stack,
    BIM_UL_task_columns,
    BIM_UL_task_filters,
    BIM_UL_saved_filter_sets,
    BIM_UL_task_inputs,
    BIM_UL_task_resources,
    BIM_UL_animation_colors,
    BIM_UL_task_outputs,
    BIM_UL_product_input_tasks,
    BIM_UL_product_output_tasks,
    BIM_UL_tasks,
)
from .management_ui import (
    BIM_PT_work_plans,
    BIM_PT_work_calendars,
    BIM_PT_4D_Tools,
)
from .panels_schedule import (
    BIM_PT_status,
    BIM_PT_work_schedules,
    BIM_PT_task_icom,
    BIM_PT_variance_analysis,
)

# 2. Group all classes into a single tuple for easy registration
classes = (
    # Animation Panels
    BIM_PT_animation_tools,
    BIM_PT_animation_color_schemes,
    # UIList Classes
    BIM_UL_animation_group_stack,
    BIM_UL_task_columns,
    BIM_UL_task_filters,
    BIM_UL_saved_filter_sets,
    BIM_UL_task_inputs,
    BIM_UL_task_resources,
    BIM_UL_animation_colors,
    BIM_UL_task_outputs,
    BIM_UL_product_input_tasks,
    BIM_UL_product_output_tasks,
    BIM_UL_tasks,
    # Management Panels
    BIM_PT_work_plans,
    BIM_PT_work_calendars,
    BIM_PT_4D_Tools,
    # Schedule Panels
    BIM_PT_status,
    BIM_PT_work_schedules,
    BIM_PT_task_icom,
    BIM_PT_variance_analysis,
)

# 3. Registration and unregistration functions for this UI package
def register():
    """Registers all UI classes from this module."""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregisters all UI classes in reverse order."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)