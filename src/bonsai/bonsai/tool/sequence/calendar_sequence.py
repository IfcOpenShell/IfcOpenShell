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

from __future__ import annotations
import bpy
from datetime import datetime
from typing import Any, Union
from dateutil import parser
import ifcopenshell
import bonsai.bim.helper
import bonsai.tool as tool
from .props_sequence import PropsSequence

class CalendarSequence:
    """Mixin class for managing IfcWorkCalendar, IfcWorkTime, and IfcRecurrencePattern."""

    @classmethod
    def get_active_work_time(cls) -> ifcopenshell.entity_instance:
        props = tool.Sequence.get_work_calendar_props()
        return tool.Ifc.get().by_id(props.active_work_time_id)

    @classmethod
    def enable_editing_work_calendar_times(cls, work_calendar: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_calendar_props()
        props.active_work_calendar_id = work_calendar.id()
        props.editing_type = "WORKTIMES"

    @classmethod
    def load_work_calendar_attributes(cls, work_calendar: ifcopenshell.entity_instance) -> dict[str, Any]:
        props = tool.Sequence.get_work_calendar_props()
        props.work_calendar_attributes.clear()
        return bonsai.bim.helper.import_attributes(work_calendar, props.work_calendar_attributes)

    @classmethod
    def enable_editing_work_calendar(cls, work_calendar: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_calendar_props()
        props.active_work_calendar_id = work_calendar.id()
        props.editing_type = "ATTRIBUTES"

    @classmethod
    def disable_editing_work_calendar(cls) -> None:
        props = tool.Sequence.get_work_calendar_props()
        props.active_work_calendar_id = 0

    @classmethod
    def get_work_calendar_attributes(cls) -> dict[str, Any]:
        props = tool.Sequence.get_work_calendar_props()
        return bonsai.bim.helper.export_attributes(props.work_calendar_attributes)

    @classmethod
    def load_work_time_attributes(cls, work_time: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_calendar_props()
        props.work_time_attributes.clear()

        bonsai.bim.helper.import_attributes(work_time, props.work_time_attributes)

    @classmethod
    def enable_editing_work_time(cls, work_time: ifcopenshell.entity_instance) -> None:
        def initialise_recurrence_components(props):
            if len(props.day_components) == 0:
                for i in range(0, 31):
                    new = props.day_components.add()
                    new.name = str(i + 1)
            if len(props.weekday_components) == 0:
                for d in ["M", "T", "W", "T", "F", "S", "S"]:
                    new = props.weekday_components.add()
                    new.name = d
            if len(props.month_components) == 0:
                for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                    new = props.month_components.add()
                    new.name = m

        def load_recurrence_pattern_data(work_time, props):
            props.position = 0
            props.interval = 0
            props.occurrences = 0
            props.start_time = ""
            props.end_time = ""
            for component in props.day_components:
                component.is_specified = False
            for component in props.weekday_components:
                component.is_specified = False
            for component in props.month_components:
                component.is_specified = False
            if not work_time.RecurrencePattern:
                return
            recurrence_pattern = work_time.RecurrencePattern
            for attribute in ["Position", "Interval", "Occurrences"]:
                if getattr(recurrence_pattern, attribute):
                    setattr(props, attribute.lower(), getattr(recurrence_pattern, attribute))
            for component in recurrence_pattern.DayComponent or []:
                props.day_components[component - 1].is_specified = True
            for component in recurrence_pattern.WeekdayComponent or []:
                props.weekday_components[component - 1].is_specified = True
            for component in recurrence_pattern.MonthComponent or []:
                props.month_components[component - 1].is_specified = True

        props = tool.Sequence.get_work_calendar_props()
        initialise_recurrence_components(props)
        load_recurrence_pattern_data(work_time, props)
        props.active_work_time_id = work_time.id()
        props.editing_type = "WORKTIMES"

    @classmethod
    def get_work_time_attributes(cls) -> dict[str, Any]:
        import bonsai.bim.module.sequence.utils.helper_utils as helper

        def callback(attributes: dict[str, Any], prop: Attribute) -> bool:
            if "Start" in prop.name or "Finish" in prop.name:
                if prop.is_null:
                    attributes[prop.name] = None
                    return True
                attributes[prop.name] = helper.parse_datetime(prop.string_value)
                return True
            return False

        props = tool.Sequence.get_work_calendar_props()
        return bonsai.bim.helper.export_attributes(props.work_time_attributes, callback)

    @classmethod
    def get_recurrence_pattern_attributes(cls, recurrence_pattern):
        props = tool.Sequence.get_work_calendar_props()
        attributes = {
            "Interval": props.interval if props.interval > 0 else None,
            "Occurrences": props.occurrences if props.occurrences > 0 else None,
        }
        applicable_data = {
            "DAILY": ["Interval", "Occurrences"],
            "WEEKLY": ["WeekdayComponent", "Interval", "Occurrences"],
            "MONTHLY_BY_DAY_OF_MONTH": ["DayComponent", "Interval", "Occurrences"],
            "MONTHLY_BY_POSITION": ["WeekdayComponent", "Position", "Interval", "Occurrences"],
            "BY_DAY_COUNT": ["Interval", "Occurrences"],
            "BY_WEEKDAY_COUNT": ["WeekdayComponent", "Interval", "Occurrences"],
            "YEARLY_BY_DAY_OF_MONTH": ["DayComponent", "MonthComponent", "Interval", "Occurrences"],
            "YEARLY_BY_POSITION": ["WeekdayComponent", "MonthComponent", "Position", "Interval", "Occurrences"],
        }
        if "Position" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["Position"] = props.position if props.position != 0 else None
        if "DayComponent" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["DayComponent"] = [i + 1 for i, c in enumerate(props.day_components) if c.is_specified]
        if "WeekdayComponent" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["WeekdayComponent"] = [i + 1 for i, c in enumerate(props.weekday_components) if c.is_specified]
        if "MonthComponent" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["MonthComponent"] = [i + 1 for i, c in enumerate(props.month_components) if c.is_specified]
        return attributes

    @classmethod
    def disable_editing_work_time(cls) -> None:
        props = tool.Sequence.get_work_calendar_props()
        props.active_work_time_id = 0


    @classmethod
    def get_recurrence_pattern_times(cls) -> Union[tuple[datetime, datetime], None]:
        props = tool.Sequence.get_work_calendar_props()
        try:
            start_time = parser.parse(props.start_time)
            end_time = parser.parse(props.end_time)
            return start_time, end_time
        except parser.ParserError:
            return None  # improve UI / refactor to add user hints
    
    @classmethod
    def reset_time_period(cls) -> None:
        props = tool.Sequence.get_work_calendar_props()
        props.start_time = ""
        props.end_time = ""

    @classmethod
    def disable_editing_task_time(cls) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.active_task_id = 0
        props.active_task_time_id = 0
