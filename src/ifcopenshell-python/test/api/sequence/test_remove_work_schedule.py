# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.api.sequence


def declared_objects(ifc_file: ifcopenshell.file) -> set[ifcopenshell.entity_instance]:
    project = ifc_file.by_type("IfcProject")[0]
    declared = {obj for rel in project.Declares for obj in rel.RelatedDefinitions}
    return declared


# NOTE: sequence module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestRemoveWorkSchedule(test.bootstrap.IFC4):
    def test_remove_work_schedule(self):
        self.file.create_entity("IfcProject")
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(self.file)

        work_plan = ifcopenshell.api.sequence.add_work_plan(self.file)
        ifcopenshell.api.sequence.assign_work_plan(self.file, work_schedule, work_plan)

        work_schedule1 = ifcopenshell.api.sequence.add_work_schedule(self.file)
        rel = self.file.create_entity("IfcRelDefinesByObject")
        rel.RelatingObject = work_schedule
        rel.RelatedObjects = [work_schedule1]

        ifcopenshell.api.sequence.add_task(self.file, work_schedule=work_schedule)

        ifcopenshell.api.sequence.remove_work_schedule(self.file, work_schedule=work_schedule)
        # Remove workschedule and subschedules.
        assert len(self.file.by_type("IfcWorkSchedule")) == 0
        assert len(self.file.by_type("IfcRelDefinesByObject")) == 0
        # Unassign from a work plan.
        assert len(self.file.by_type("IfcRelAggregates")) == 0
        # Remove related IfcTasks.
        assert len(self.file.by_type("IfcTask")) == 0
        assert len(self.file.by_type("IfcRelAssignsToControl")) == 0
        # Unassign from a project.
        assert declared_objects(self.file) == {work_plan}


class TestRemoveWorkScheduleIFC4X3(test.bootstrap.IFC4X3, TestRemoveWorkSchedule):
    pass
