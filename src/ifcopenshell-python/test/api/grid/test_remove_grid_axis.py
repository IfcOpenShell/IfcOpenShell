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

import ifcopenshell.api.grid
import test.bootstrap


class TestRemoveGridAxis(test.bootstrap.IFC4):
    def test_removing_an_axis_removes_its_curve(self):
        grid = self.file.createIfcGrid()
        axis = ifcopenshell.api.grid.create_grid_axis(
            self.file, axis_tag="A", same_sense=True, uvw_axes="UAxes", grid=grid
        )
        axis.AxisCurve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))])
        axis2 = ifcopenshell.api.grid.create_grid_axis(
            self.file, axis_tag="B", same_sense=True, uvw_axes="UAxes", grid=grid
        )
        axis2.AxisCurve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint((1.0, 0.0, 0.0))])
        ifcopenshell.api.grid.remove_grid_axis(self.file, axis=axis2)
        assert grid.UAxes == (axis,)
        assert len(self.file.by_type("IfcGridAxis")) == 1
        # The curve should be removed since it was only used by the removed axis.
        assert len(self.file.by_type("IfcPolyline")) == 1

    def test_removing_an_axis_preserves_shared_curve(self):
        grid = self.file.createIfcGrid()
        shared_curve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))])
        axis = ifcopenshell.api.grid.create_grid_axis(
            self.file, axis_tag="A", same_sense=True, uvw_axes="UAxes", grid=grid
        )
        axis.AxisCurve = shared_curve
        axis2 = ifcopenshell.api.grid.create_grid_axis(
            self.file, axis_tag="B", same_sense=True, uvw_axes="UAxes", grid=grid
        )
        axis2.AxisCurve = shared_curve
        ifcopenshell.api.grid.remove_grid_axis(self.file, axis=axis2)
        assert grid.UAxes == (axis,)
        # The shared curve should be preserved since it's still used by axis.
        assert shared_curve in self.file
        assert axis.AxisCurve == shared_curve


class TestRemoveGridAxisIFC2X3(test.bootstrap.IFC2X3, TestRemoveGridAxis):
    pass
