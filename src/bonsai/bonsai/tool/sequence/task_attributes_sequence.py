# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021-2023 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net>
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
from typing import Any, Union, Literal, TYPE_CHECKING
import ifcopenshell
import bonsai.bim.helper
import bonsai.tool as tool
from .props_sequence import PropsSequence

if TYPE_CHECKING:
    from bonsai.bim.prop import Attribute

class TaskAttributesSequence:
    """Mixin class for managing attributes of individual IfcTask and IfcTaskTime entities."""


    @classmethod
    def get_task_attribute_value(cls, attribute_name: str) -> Any:
        props = tool.Sequence.get_work_schedule_props()
        return props.task_attributes[attribute_name].get_value()

    @classmethod
    def get_active_task(cls) -> ifcopenshell.entity_instance:
        props = tool.Sequence.get_work_schedule_props()
        return tool.Ifc.get().by_id(props.active_task_id)

    @classmethod
    def get_task_time(cls, task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return task.TaskTime or None

    @classmethod
    def load_task_attributes(cls, task: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.task_attributes.clear()
        bonsai.bim.helper.import_attributes(task, props.task_attributes)

    @classmethod
    def enable_editing_task_attributes(cls, task: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.active_task_id = task.id()
        props.editing_task_type = "ATTRIBUTES"

    @classmethod
    def get_task_attributes(cls) -> dict[str, Any]:
        props = tool.Sequence.get_work_schedule_props()
        return bonsai.bim.helper.export_attributes(props.task_attributes)

    @classmethod
    def load_task_time_attributes(cls, task_time: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        schema = tool.Ifc.schema()
        entity = schema.declaration_by_name("IfcTaskTime").as_entity()
        assert entity

        def callback(name: str, prop: Union[Attribute, None], data: dict[str, Any]) -> Union[bool, None]:
            attr = entity.attribute_by_index(entity.attribute_index(name))
            if attr.type_of_attribute()._is("IfcDuration"):
                assert prop
                cls.add_duration_prop(prop, data[name])
            if isinstance(data[name], datetime):
                assert prop
                prop.string_value = "" if prop.is_null else data[name].isoformat()
                return True

        props.task_time_attributes.clear()
        props.durations_attributes.clear()
        bonsai.bim.helper.import_attributes(task_time, props.task_time_attributes, callback)

    @classmethod
    def enable_editing_task_time(cls, task: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.active_task_id = task.id()
        props.active_task_time_id = task.TaskTime.id()
        props.editing_task_type = "TASKTIME"

    @classmethod
    def disable_editing_task(cls) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.active_task_id = 0
        props.active_task_time_id = 0
        props.editing_task_type = ""

    @classmethod
    def get_task_time_attributes(cls) -> dict[str, Any]:
        import bonsai.bim.module.sequence.utils.helper_utils as helper

        def callback(attributes: dict[str, Any], prop: Attribute) -> bool:
            if "Start" in prop.name or "Finish" in prop.name or prop.name == "StatusTime":
                if prop.is_null:
                    attributes[prop.name] = None
                    return True
                attributes[prop.name] = helper.parse_datetime(prop.string_value)
                return True
            elif prop.special_type == "DURATION":
                return cls.export_duration_prop(prop, attributes)
            return False

        props = tool.Sequence.get_work_schedule_props()
        return bonsai.bim.helper.export_attributes(props.task_time_attributes, callback)


    @classmethod
    def add_duration_prop(cls, prop: Attribute, duration_value: Union[str, None]) -> None:
        import bonsai.bim.module.sequence.utils.helper_utils as helper

        props = tool.Sequence.get_work_schedule_props()
        prop.special_type = "DURATION"
        duration_props = props.durations_attributes.add()
        duration_props.name = prop.name
        if duration_value is None:
            return
        for key, value in helper.parse_duration_as_blender_props(duration_value).items():
            setattr(duration_props, key, value)

    @classmethod
    def export_duration_prop(cls, prop: Attribute, out_attributes: dict[str, Any]) -> Literal[True]:
        import bonsai.bim.module.sequence.utils.helper_utils as helper

        props = tool.Sequence.get_work_schedule_props()
        if prop.is_null:
            out_attributes[prop.name] = None
        else:
            duration_type = out_attributes["DurationType"] if "DurationType" in out_attributes else None
            time_split_iso_duration = helper.blender_props_to_iso_duration(
                props.durations_attributes, duration_type, prop.name
            )
            out_attributes[prop.name] = time_split_iso_duration
        return True
