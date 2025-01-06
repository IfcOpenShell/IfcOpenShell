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


class TestUnassignControl(test.bootstrap.IFC4):
    def test_run(self):
        wall = self.file.createIfcWall()
        control = ifcopenshell.api.cost.add_cost_schedule(self.file)

        # assign and unassign
        relation = ifcopenshell.api.control.assign_control(self.file, relating_control=control, related_object=wall)
        ifcopenshell.api.control.unassign_control(self.file, relating_control=control, related_object=wall)
        assert len(self.file.by_type("IfcRelAssignsToControl")) == 0

        # 1 control 2 related objects
        wall1 = self.file.createIfcWall()
        relation = ifcopenshell.api.control.assign_control(self.file, relating_control=control, related_object=wall)
        ifcopenshell.api.control.assign_control(self.file, relating_control=control, related_object=wall1)
        ifcopenshell.api.control.unassign_control(self.file, relating_control=control, related_object=wall1)
        assert len(self.file.by_type("IfcRelAssignsToControl")) == 1
        assert relation.RelatedObjects == (wall,)


class TestUnassignControlIFC2X3(test.bootstrap.IFC2X3, TestUnassignControl):
    pass
