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
from typing import Union
import ifcopenshell
import ifcopenshell.util.sequence
import bonsai.tool as tool
from .props_sequence import PropsSequence

class TaskIcomSequence:
    """Mixin class for managing task Inputs, Outputs, and Resources."""

    @classmethod
    def update_task_ICOM(cls, task: Union[ifcopenshell.entity_instance, None]) -> None:
        """Refreshes the ICOM data (Outputs, Inputs, Resources) for the active task panel.
        If there is no task, it clears the lists to avoid showing data from a previous task."""
        props = tool.Sequence.get_work_schedule_props()
        if task:
            # Outputs
            outputs = tool.Sequence.get_task_outputs(task) or []
            cls.load_task_outputs(outputs)
            # Inputs
            inputs = tool.Sequence.get_task_inputs(task) or []
            cls.load_task_inputs(inputs)
            # Resources
            cls.load_task_resources(task)
        else:
            props.task_outputs.clear()
            props.task_inputs.clear()
            props.task_resources.clear()

    @classmethod
    def load_task_resources(cls, task: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        rprops = tool.Resource.get_resource_props()
        props.task_resources.clear()
        rprops.is_resource_update_enabled = False
        for resource in cls.get_task_resources(task) or []:
            new = props.task_resources.add()
            new.ifc_definition_id = resource.id()
            new.name = resource.Name or "Unnamed"
            new.schedule_usage = resource.Usage.ScheduleUsage or 0 if resource.Usage else 0
        rprops.is_resource_update_enabled = True

    @classmethod
    def get_task_outputs(cls, task: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        props = tool.Sequence.get_work_schedule_props()
        is_deep = props.show_nested_outputs
        return ifcopenshell.util.sequence.get_task_outputs(task, is_deep)


    @classmethod
    def get_task_resources(
        cls, task: Union[ifcopenshell.entity_instance, None]
    ) -> Union[list[ifcopenshell.entity_instance], None]:
        if not task:
            return
        props = tool.Sequence.get_work_schedule_props()
        is_deep = props.show_nested_resources
        return ifcopenshell.util.sequence.get_task_resources(task, is_deep)

    @classmethod
    def load_task_inputs(cls, inputs: list[ifcopenshell.entity_instance]) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.task_inputs.clear()
        for input in inputs:
            new = props.task_inputs.add()
            new.ifc_definition_id = input.id()
            new.name = input.Name or "Unnamed"

    @classmethod
    def load_task_outputs(cls, outputs: list[ifcopenshell.entity_instance]) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.task_outputs.clear()
        if outputs:
            for output in outputs:
                new = props.task_outputs.add()
                new.ifc_definition_id = output.id()
                new.name = output.Name or "Unnamed"

    @classmethod
    def get_task_inputs(cls, task: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        props = tool.Sequence.get_work_schedule_props()
        is_deep = props.show_nested_inputs
        return ifcopenshell.util.sequence.get_task_inputs(task, is_deep)
