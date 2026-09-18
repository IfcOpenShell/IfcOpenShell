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

import datetime

import ifcopenshell.api.resource
import ifcopenshell.api.root
import test.bootstrap


# NOTE: resource module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestEditResourceTime(test.bootstrap.IFC4):
    def test_editing_schedule_work_to_a_zero_duration(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.resource.add_resource_time(self.file, resource=resource)

        # A caller may legitimately pass a zero-length timedelta (e.g. "the
        # resource did no work in this period"). A falsy value is not the
        # same as an unset one, and must still go through IfcDuration
        # serialisation instead of being written raw.
        ifcopenshell.api.resource.edit_resource_time(
            self.file, resource_time=resource_time, attributes={"ScheduleWork": datetime.timedelta(0)}
        )
        assert resource_time.ScheduleWork == "P0D"

    def test_editing_actual_work_to_a_zero_duration(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.resource.add_resource_time(self.file, resource=resource)

        ifcopenshell.api.resource.edit_resource_time(
            self.file, resource_time=resource_time, attributes={"ActualWork": datetime.timedelta(0)}
        )
        assert resource_time.ActualWork == "P0D"

    def test_editing_schedule_work_to_none_clears_it(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.resource.add_resource_time(self.file, resource=resource)

        ifcopenshell.api.resource.edit_resource_time(
            self.file, resource_time=resource_time, attributes={"ScheduleWork": "PT8H"}
        )
        assert resource_time.ScheduleWork == "PT8H"

        ifcopenshell.api.resource.edit_resource_time(
            self.file, resource_time=resource_time, attributes={"ScheduleWork": None}
        )
        assert resource_time.ScheduleWork is None
