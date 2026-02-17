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
from typing import Any, Union, Literal, TYPE_CHECKING
import ifcopenshell
import ifcopenshell.util.date
import bonsai.bim.helper
import bonsai.tool as tool
from .props_sequence import PropsSequence

if TYPE_CHECKING:
    from bonsai.bim.prop import Attribute

class SequenceRelationsSequence:
    """Mixin class for managing IfcRelSequence relationships between tasks."""

    @classmethod
    def enable_editing_task_sequence(cls) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.editing_task_type = "SEQUENCE"

    @classmethod
    def load_rel_sequence_attributes(cls, rel_sequence: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.sequence_attributes.clear()
        bonsai.bim.helper.import_attributes(rel_sequence, props.sequence_attributes)
    
    @classmethod
    def enable_editing_rel_sequence_attributes(cls, rel_sequence: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.active_sequence_id = rel_sequence.id()
        props.editing_sequence_type = "ATTRIBUTES"

    @classmethod
    def load_lag_time_attributes(cls, lag_time: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()

    def callback(name: str, prop: Union[Attribute, None], data: dict[str, Any]) -> None | Literal[True]:
        if name == "LagValue":
            prop = props.lag_time_attributes.add()
            prop.name = name
            prop.is_null = data[name] is None
            prop.is_optional = False
            prop.data_type = "string"
            prop.string_value = (
                "" if prop.is_null else ifcopenshell.util.date.datetime2ifc(data[name].wrappedValue, "IfcDuration")
            )
            return True

        props.lag_time_attributes.clear()
        bonsai.bim.helper.import_attributes(lag_time, props.lag_time_attributes, callback)

    @classmethod
    def enable_editing_sequence_lag_time(cls, rel_sequence: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.active_sequence_id = rel_sequence.id()
        props.editing_sequence_type = "LAG_TIME"

    @classmethod
    def get_rel_sequence_attributes(cls) -> dict[str, Any]:
        props = tool.Sequence.get_work_schedule_props()
        return bonsai.bim.helper.export_attributes(props.sequence_attributes)

    @classmethod
    def disable_editing_rel_sequence(cls) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.active_sequence_id = 0

    @classmethod
    def get_lag_time_attributes(cls) -> dict[str, Any]:
        props = tool.Sequence.get_work_schedule_props()
        return bonsai.bim.helper.export_attributes(props.lag_time_attributes)



