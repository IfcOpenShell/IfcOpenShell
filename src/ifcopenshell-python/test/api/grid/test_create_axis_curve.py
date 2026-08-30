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

import numpy as np

import ifcopenshell.api.grid
import test.bootstrap


class TestCreateAxisCurve(test.bootstrap.IFC4):
    def make_grid_with_axis(self, axis_tag="A"):
        grid = self.file.createIfcGrid()
        grid.ObjectPlacement = self.file.createIfcLocalPlacement(
            RelativePlacement=self.file.createIfcAxis2Placement3D(
                Location=self.file.createIfcCartesianPoint([0.0, 0.0, 0.0])
            )
        )
        axis = ifcopenshell.api.grid.create_grid_axis(
            self.file, axis_tag=axis_tag, same_sense=True, uvw_axes="UAxes", grid=grid
        )
        return grid, axis

    def test_creates_a_polyline_axis_curve(self):
        _, axis = self.make_grid_with_axis()
        ifcopenshell.api.grid.create_axis_curve(
            self.file, p1=np.array([0.0, 0.0, 0.0]), p2=np.array([10.0, 0.0, 0.0]), grid_axis=axis
        )
        assert axis.AxisCurve is not None
        assert axis.AxisCurve.is_a("IfcPolyline")
        assert len(axis.AxisCurve.Points) == 2

    def test_replaces_existing_curve_when_unshared(self):
        """Calling create_axis_curve again on the same axis replaces the old curve
        and removes the old curve from the file when nothing else references it."""
        _, axis = self.make_grid_with_axis()
        ifcopenshell.api.grid.create_axis_curve(
            self.file, p1=np.array([0.0, 0.0, 0.0]), p2=np.array([10.0, 0.0, 0.0]), grid_axis=axis
        )
        old_curve_id = axis.AxisCurve.id()
        ifcopenshell.api.grid.create_axis_curve(
            self.file, p1=np.array([1.0, 0.0, 0.0]), p2=np.array([11.0, 0.0, 0.0]), grid_axis=axis
        )
        assert axis.AxisCurve.id() != old_curve_id
        assert self.file.by_id(old_curve_id) is None

    def test_does_not_remove_shared_curve(self):
        """When two axes share the same AxisCurve (e.g. after a shallow copy during
        duplication), updating one axis must not destroy the curve still referenced
        by the other axis."""
        grid, axis = self.make_grid_with_axis()
        axis2 = ifcopenshell.api.grid.create_grid_axis(
            self.file, axis_tag="B", same_sense=True, uvw_axes="UAxes", grid=grid
        )
        ifcopenshell.api.grid.create_axis_curve(
            self.file, p1=np.array([0.0, 0.0, 0.0]), p2=np.array([10.0, 0.0, 0.0]), grid_axis=axis
        )
        shared_curve = axis.AxisCurve
        shared_curve_id = shared_curve.id()
        # Simulate what copy_class produces: a duplicate axis that shares the
        # source's AxisCurve rather than having its own copy.
        axis2.AxisCurve = shared_curve
        assert self.file.get_total_inverses(shared_curve) == 2

        # Updating axis1's curve must not remove the curve that axis2 still needs.
        ifcopenshell.api.grid.create_axis_curve(
            self.file, p1=np.array([1.0, 0.0, 0.0]), p2=np.array([11.0, 0.0, 0.0]), grid_axis=axis
        )
        assert axis2.AxisCurve.id() == shared_curve_id
        assert self.file.by_id(shared_curve_id) is not None


class TestCreateAxisCurveIFC2X3(test.bootstrap.IFC2X3, TestCreateAxisCurve):
    pass
