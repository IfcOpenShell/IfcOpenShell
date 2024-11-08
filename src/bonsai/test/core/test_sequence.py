# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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


import bonsai.core.sequence as subject
from test.core.bootstrap import ifc, sequence


class TestAddWorkPlan:
    def test_run(self, ifc):
        ifc.run("sequence.add_work_plan").should_be_called().will_return("work_plan")
        assert subject.add_work_plan(ifc) == "work_plan"


class TestRemoveWorkPlan:
    def test_run(self, ifc):
        ifc.run("sequence.remove_work_plan", work_plan="work_plan").should_be_called()
        subject.remove_work_plan(ifc, work_plan="work_plan")


class TestEnableEditingWorkPlan:
    def test_run(self, sequence):
        sequence.load_work_plan_attributes("work_plan").should_be_called()
        sequence.enable_editing_work_plan("work_plan").should_be_called()
        subject.enable_editing_work_plan(sequence, work_plan="work_plan")


class TestDisableEditingWorkPlan:
    def test_run(self, sequence):
        sequence.disable_editing_work_plan().should_be_called()
        subject.disable_editing_work_plan(sequence)


class TestEditWorkPlan:
    def test_run(self, ifc, sequence):
        sequence.get_work_plan_attributes().should_be_called().will_return("attributes")
        ifc.run("sequence.edit_work_plan", work_plan="work_plan", attributes="attributes").should_be_called()
        sequence.disable_editing_work_plan().should_be_called()
        subject.edit_work_plan(ifc, sequence, work_plan="work_plan")


# TODO continue writing tests
