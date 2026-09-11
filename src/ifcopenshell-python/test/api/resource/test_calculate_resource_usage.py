# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.resource
import ifcopenshell.api.root
import ifcopenshell.api.sequence
import test.bootstrap


# NOTE: resource module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestCalculateResourceUsage(test.bootstrap.IFC4):
    def test_calculating_usage_from_a_scheduled_duration(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")

        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        ifcopenshell.api.resource.add_resource_time(self.file, resource=resource)
        resource.Usage.ScheduleWork = "P2D"

        task = ifcopenshell.api.sequence.add_task(self.file)
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=task)
        ifcopenshell.api.sequence.edit_task_time(self.file, task_time=task_time, attributes={"ScheduleDuration": "P1D"})
        ifcopenshell.api.sequence.assign_process(self.file, relating_process=task, related_object=resource)

        ifcopenshell.api.resource.calculate_resource_usage(self.file, resource=resource)
        assert resource.Usage.ScheduleUsage == 6.0

    def test_no_crash_when_task_time_has_no_scheduled_duration(self):
        # A task time with a start date but no duration is a valid, deliberately
        # supported state (see TestEditTaskTime.
        # test_editing_just_a_start_date_with_no_duration_or_finish).
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")

        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        ifcopenshell.api.resource.add_resource_time(self.file, resource=resource)
        resource.Usage.ScheduleWork = "P2D"

        task = ifcopenshell.api.sequence.add_task(self.file)
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=task)
        ifcopenshell.api.sequence.edit_task_time(
            self.file,
            task_time=task_time,
            attributes={"ScheduleDuration": None, "ScheduleStart": "2000-01-01T09:00:00"},
        )
        ifcopenshell.api.sequence.assign_process(self.file, relating_process=task, related_object=resource)

        ifcopenshell.api.resource.calculate_resource_usage(self.file, resource=resource)
        assert resource.Usage.ScheduleUsage is None
