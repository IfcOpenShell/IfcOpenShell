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

import test.bootstrap
import ifcopenshell.api.drawing


class TestUnassignProduct(test.bootstrap.IFC4):
    def test_unassigning_a_product(self):
        wall = self.file.createIfcWall()
        label = self.file.createIfcAnnotation()
        ifcopenshell.api.drawing.assign_product(self.file, relating_product=wall, related_object=label)
        ifcopenshell.api.drawing.unassign_product(self.file, relating_product=wall, related_object=label)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 0

    def test_unassigning_a_grid_axis(self):
        axis = self.file.createIfcGridAxis(AxisTag="A")
        grid = self.file.createIfcGrid(UAxes=[axis])
        line = self.file.createIfcAnnotation()
        ifcopenshell.api.drawing.assign_product(self.file, relating_product=axis, related_object=line)
        ifcopenshell.api.drawing.unassign_product(self.file, relating_product=axis, related_object=line)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 0


class TestUnassignProductIFC2X3(test.bootstrap.IFC2X3, TestUnassignProduct):
    pass
