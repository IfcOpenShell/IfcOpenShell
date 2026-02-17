"""Property Groups for 4D BIM scheduling - Modular Organization.

This package contains PropertyGroup classes organized thematically:
- animation.py: Animation, colors, and colortype management
- camera_hud.py: Camera, orbit, and HUD properties
- task.py: Core Task properties, resources, and products
- schedule.py: WorkSchedules and WorkPlans
- filter.py: Task filtering logic
- calendar.py: Calendar properties and date picker
- misc.py: Miscellaneous properties

All PropertyGroups maintain full compatibility with the original prop.py implementation.
"""



import bpy
from bpy.props import PointerProperty

# --- 1. Import everything from each module to make it accessible from 'prop' ---
# We use 'import *' to put all classes and functions directly
# into the 'prop' namespace, which resolves circular import issues.

from .color_manager_prop import *
from .callbacks_prop import *
from .enums_prop import *
from .task_prop import *
from .schedule_prop import *
from .animation_prop import *
from .camera_prop import *
from .ui_helpers_prop import *


# --- 2. Create a tuple with all the classes to be registered ---
classes = (
    # From task_prop.py
    TaskFilterRule, BIMTaskFilterProperties, SavedFilterSet,
    TaskcolortypeGroupChoice, Task, TaskResource, TaskProduct,
    BIMTaskTreeProperties,
    
    # From schedule_prop.py
    WorkPlan, BIMWorkPlanProperties, BIMWorkScheduleProperties,
    WorkCalendar, RecurrenceComponent, BIMWorkCalendarProperties,
    
    # From animation_prop.py
    BIMTaskTypeColor, AnimationColorSchemes, AnimationColorTypeGroupItem,
    BIMAnimationProperties,
    
    # From camera_prop.py
    BIMCameraOrbitProperties,
    
    # From ui_helpers_prop.py
    IFCStatus, BIMStatusProperties, DatePickerProperties, BIMDateTextProperties,
)

# --- 3. Registration and unregistration functions for the entire package ---
def register():
    """Registers all property classes in this package."""
    for cls in classes:
        bpy.utils.register_class(cls)

    BIMWorkScheduleProperties.filters = PointerProperty(type=BIMTaskFilterProperties)
    BIMAnimationProperties.camera_orbit = PointerProperty(type=BIMCameraOrbitProperties)

def unregister():
    """Unregisters all classes in reverse order."""
    if hasattr(BIMWorkScheduleProperties, 'filters'):
        del BIMWorkScheduleProperties.filters
    if hasattr(BIMAnimationProperties, 'camera_orbit'):
        del BIMAnimationProperties.camera_orbit

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
