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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.resource
import ifcopenshell.api.root
import test.bootstrap


# NOTE: resource module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestEditResourceTimeDurationRoundTrip(test.bootstrap.IFC4):
    """Regression tests for #6964: ScheduleWork is a plain IfcDuration
    attribute write, so it must come back exactly as given, whether the
    value is whole minutes or carries a fractional second."""

    def test_dimitrios_exact_value_is_preserved(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.resource.add_resource_time(self.file, resource=resource)
        ifcopenshell.api.resource.edit_resource_time(
            self.file, resource_time=resource_time, attributes={"ScheduleWork": "PT2H30M"}
        )
        assert resource_time.ScheduleWork == "PT2H30M"

    def test_a_duration_with_a_fractional_second_is_preserved(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.resource.add_resource_time(self.file, resource=resource)
        ifcopenshell.api.resource.edit_resource_time(
            self.file, resource_time=resource_time, attributes={"ScheduleWork": "PT2H29M59.999867S"}
        )
        assert resource_time.ScheduleWork == "PT2H29M59.999867S"
