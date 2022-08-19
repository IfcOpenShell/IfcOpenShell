# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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


def add_work_plan(ifc, sequence):
    ifc.run("sequence.add_work_plan")
    sequence.load_work_plans()


def remove_work_plan(ifc, sequence, work_plan=None):
    ifc.run("sequence.remove_work_plan", work_plan=work_plan)
    sequence.load_work_plans()


def enable_editing_work_plan(sequence, work_plan=None):
    sequence.load_work_plan_attributes(work_plan)
    sequence.enable_editing_work_plan(work_plan)


def disable_editing_work_plan(sequence):
    sequence.disable_editing_work_plan()


def edit_work_plan(ifc, sequence):
    work_plan = sequence.get_current_ifc_work_plan()
    attributes = sequence.get_work_plan_attributes()
    ifc.run("sequence.edit_work_plan", work_plan=work_plan, attributes=attributes)
    sequence.disable_editing_work_plan()
    sequence.load_work_plans()
