# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import test.bootstrap
import ifcopenshell.api.cost
import ifcopenshell.api.control


class TestAssignControl(test.bootstrap.IFC4):
    def test_run(self):
        wall = self.file.createIfcWall()
        control = ifcopenshell.api.cost.add_cost_schedule(self.file)

        # simple assignment
        relation = ifcopenshell.api.control.assign_control(self.file, relating_control=control, related_object=wall)
        assert len(self.file.by_type("IfcRelAssignsToControl")) == 1
        assert relation.RelatingControl == control
        assert relation.RelatedObjects == (wall,)

        # trying to establish existing relationship
        relation = ifcopenshell.api.control.assign_control(self.file, relating_control=control, related_object=wall)
        assert relation is None

        # assigning same control to another object
        wall1 = self.file.createIfcWall()
        relation = ifcopenshell.api.control.assign_control(self.file, relating_control=control, related_object=wall1)
        assert relation is not None
        assert len(self.file.by_type("IfcRelAssignsToControl")) == 1
        assert relation.RelatingControl == control
        assert set(relation.RelatedObjects) == set((wall, wall1))


class TestAssignControlIFC2X3(test.bootstrap.IFC2X3, TestAssignControl):
    pass
