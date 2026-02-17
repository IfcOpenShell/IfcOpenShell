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
from typing import TYPE_CHECKING
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.sequence.prop import (
        BIMAnimationProperties,
        BIMStatusProperties,
        BIMTaskTreeProperties,
        BIMWorkCalendarProperties,
        BIMWorkPlanProperties,
        BIMWorkScheduleProperties,
    )

class PropsSequence:
    """Mixin class for accessing BIM sequence properties from the Blender scene."""

    @classmethod
    def get_work_schedule_props(cls) -> BIMWorkScheduleProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMWorkScheduleProperties

    @classmethod
    def get_task_tree_props(cls) -> BIMTaskTreeProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMTaskTreeProperties  

    @classmethod
    def get_animation_props(cls) -> BIMAnimationProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMAnimationProperties

    @classmethod
    def get_status_props(cls) -> BIMStatusProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMStatusProperties

    @classmethod
    def get_work_plan_props(cls) -> BIMWorkPlanProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMWorkPlanProperties

    @classmethod
    def get_work_calendar_props(cls) -> BIMWorkCalendarProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMWorkCalendarProperties 







