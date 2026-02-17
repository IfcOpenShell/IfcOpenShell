"""Calendar-related PropertyGroups for 4D BIM scheduling.

This module contains all calendar and date-related PropertyGroup classes extracted from prop.py:
- WorkCalendar: Work calendar properties
- RecurrenceComponent: Date recurrence component properties  
- BIMWorkCalendarProperties: Main work calendar management
- DatePickerProperties: Date picker UI properties
- BIMDateTextProperties: Date text animation properties

Each PropertyGroup maintains full compatibility with the original implementation
while being organized thematically for better maintainability.
"""

import bpy
from bpy.props import (
    StringProperty,
    IntProperty, 
    BoolProperty,
    EnumProperty,
    CollectionProperty,
    PointerProperty
)
from bpy.types import PropertyGroup

try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        import bpy.types
        from ..prop_types import Attribute
except ImportError:
    TYPE_CHECKING = False

# Import callback functions and utilities
try:
    import bonsai.tool as tool
    from bonsai.bim.prop import Attribute
except ImportError:
    # Fallback for development/testing
    Attribute = None


def update_selected_date(self: "DatePickerProperties", context: bpy.types.Context) -> None:
    """Update the selected date with time components."""
    include_time = True
    selected_date = tool.Sequence.parse_isodate_datetime(self.selected_date, include_time)
    selected_date = selected_date.replace(hour=self.selected_hour, minute=self.selected_min, second=self.selected_sec)
    self.selected_date = tool.Sequence.isodate_datetime(selected_date, include_time)


class WorkCalendar(PropertyGroup):
    """Work calendar properties for scheduling."""
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    
    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int


class RecurrenceComponent(PropertyGroup):
    """Component for date recurrence patterns."""
    name: StringProperty(name="Name")
    is_specified: BoolProperty(name="Is Specified")
    
    if TYPE_CHECKING:
        name: str
        is_specified: bool


class BIMWorkCalendarProperties(PropertyGroup):
    """Main work calendar properties with comprehensive calendar management."""
    work_calendar_attributes: CollectionProperty(name="Work Calendar Attributes", type=Attribute)
    work_time_attributes: CollectionProperty(name="Work Time Attributes", type=Attribute)
    editing_type: StringProperty(name="Editing Type")
    active_work_calendar_id: IntProperty(name="Active Work Calendar Id")
    active_work_time_id: IntProperty(name="Active Work Time Id")
    
    # Recurrence components
    day_components: CollectionProperty(name="Day Components", type=RecurrenceComponent)
    weekday_components: CollectionProperty(name="Weekday Components", type=RecurrenceComponent)
    month_components: CollectionProperty(name="Month Components", type=RecurrenceComponent)
    
    # Recurrence settings
    position: IntProperty(name="Position")
    interval: IntProperty(name="Recurrence Interval")
    occurrences: IntProperty(name="Occurs N Times")
    recurrence_types: EnumProperty(
        items=[
            ("DAILY", "Daily", "e.g. Every day"),
            ("WEEKLY", "Weekly", "e.g. Every Friday"),
            ("MONTHLY_BY_DAY_OF_MONTH", "Monthly on Specified Date", "e.g. Every 2nd of each Month"),
            ("MONTHLY_BY_POSITION", "Monthly on Specified Weekday", "e.g. Every 1st Friday of each Month"),
            ("YEARLY_BY_DAY_OF_MONTH", "Yearly on Specified Date", "e.g. Every 2nd of October"),
            ("YEARLY_BY_POSITION", "Yearly on Specified Weekday", "e.g. Every 1st Friday of October"),
        ],
        name="Recurrence Types",
    )
    
    # Time settings
    start_time: StringProperty(name="Start Time")
    end_time: StringProperty(name="End Time")
    
    if TYPE_CHECKING:
        work_calendar_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        work_time_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        editing_type: str
        active_work_calendar_id: int
        active_work_time_id: int
        day_components: bpy.types.bpy_prop_collection_idprop[RecurrenceComponent]
        weekday_components: bpy.types.bpy_prop_collection_idprop[RecurrenceComponent]
        month_components: bpy.types.bpy_prop_collection_idprop[RecurrenceComponent]
        position: int
        interval: int
        occurrences: int
        recurrence_types: str
        start_time: str
        end_time: str


class DatePickerProperties(PropertyGroup):
    """Properties for date picker UI components."""
    display_date: StringProperty(
        name="Display Date",
        description="Needed to keep track of what month is currently opened in date picker without affecting the currently selected date.",
    )
    selected_date: StringProperty(name="Selected Date")
    selected_hour: IntProperty(min=0, max=23, update=update_selected_date)
    selected_min: IntProperty(min=0, max=59, update=update_selected_date)
    selected_sec: IntProperty(min=0, max=59, update=update_selected_date)
    
    if TYPE_CHECKING:
        display_date: str
        selected_date: str
        selected_hour: int
        selected_min: int
        selected_sec: int


class BIMDateTextProperties(PropertyGroup):
    """Properties for date text animations in 4D visualizations."""
    start_frame: IntProperty(name="Start Frame")
    total_frames: IntProperty(name="Total Frames")
    start: StringProperty(name="Start")
    finish: StringProperty(name="Finish")
    
    if TYPE_CHECKING:
        start_frame: int
        total_frames: int
        start: str
        finish: str