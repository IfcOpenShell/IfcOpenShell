# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>, 2021-2022 Yassine Oualid <yassine@sigmadimensions.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool


def refresh():
    SequenceData.is_loaded = False


class SequenceData:
    is_loaded = False
    number_of_work_plans_loaded = 0
    number_of_work_schedules_loaded = 0
    number_of_tasks_loaded = 0
    tasks = {}

    @classmethod
    def load(cls):
        cls.load_work_plans()
        cls.is_loaded = True

    @classmethod
    def load_work_plans(cls):
        cls.work_plans = {}
        cls.number_of_work_plans_loaded = len(tool.Ifc.get().by_type("IfcWorkPlan"))
        for work_plan in tool.Ifc.get().by_type("IfcWorkPlan"):
            cls.work_plans[work_plan.id()] = {"Name": work_plan.Name}
