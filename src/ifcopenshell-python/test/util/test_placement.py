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

import ifcopenshell.util.placement as subject
import test.bootstrap


class TestGetStoreyElevationIFC4(test.bootstrap.IFC4):
    def test_run(self):
        storey = self.file.createIfcBuildingStorey()
        placement = self.file.createIfcLocalPlacement()
        placement.RelativePlacement = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 3.0))
        )
        storey.ObjectPlacement = placement
        assert subject.get_storey_elevation(storey) == 3.0

    def test_getting_the_elevation_if_no_z_location(self):
        storey = self.file.createIfcBuildingStorey()
        storey.Elevation = 3.0
        assert subject.get_storey_elevation(storey) == 3.0

    def test_returning_0_as_a_fallback(self):
        storey = self.file.createIfcBuildingStorey()
        assert subject.get_storey_elevation(storey) == 0.0
        building = self.file.createIfcBuilding()
        assert subject.get_storey_elevation(building) == 0.0


def assert_orthonormal(matrix):
    rotation = matrix[:3, :3]
    assert not np.any(np.isnan(matrix)), f"matrix contains NaN:\n{matrix}"
    assert np.allclose(rotation.T @ rotation, np.eye(3)), f"matrix is not orthonormal:\n{matrix}"
    assert np.isclose(np.linalg.det(rotation), 1.0), f"determinant is not 1:\n{matrix}"


class TestA2P(test.bootstrap.IFC4):
    def test_deriving_the_x_axis_by_projection_when_it_is_not_perpendicular_to_z(self):
        # IfcBuildAxes derives the X axis by projecting RefDirection onto the
        # plane normal to Axis, so (1, 0, 1) against Z becomes (1, 0, 0).
        matrix = subject.a2p((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 1.0))
        assert np.allclose(matrix[:3, 0], (1.0, 0.0, 0.0))
        assert np.allclose(matrix[:3, 1], (0.0, 1.0, 0.0))
        assert np.allclose(matrix[:3, 2], (0.0, 0.0, 1.0))
        assert_orthonormal(matrix)

    def test_keeping_an_already_perpendicular_x_axis_unchanged(self):
        matrix = subject.a2p((1.0, 2.0, 3.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))
        assert np.allclose(matrix[:3, 0], (0.0, 1.0, 0.0))
        assert np.allclose(matrix[:3, 1], (-1.0, 0.0, 0.0))
        assert np.allclose(matrix[:3, 2], (0.0, 0.0, 1.0))
        assert np.allclose(matrix[:3, 3], (1.0, 2.0, 3.0))
        assert_orthonormal(matrix)


class TestGetAxis2PlacementOrthonormalityIFC4(test.bootstrap.IFC4):
    def placement_3d(self, axis, ref_direction=None):
        return self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection(axis) if axis else None,
            self.file.createIfcDirection(ref_direction) if ref_direction else None,
        )

    def test_axis2placement3d_with_a_non_perpendicular_ref_direction(self):
        matrix = subject.get_axis2placement(self.placement_3d((0.0, 0.0, 1.0), (1.0, 0.0, 1.0)))
        assert np.allclose(matrix[:3, 0], (1.0, 0.0, 0.0))
        assert_orthonormal(matrix)

    def test_axis2placement3d_along_x_without_a_ref_direction(self):
        # A valid file: RefDirection is optional, so the X axis is ours to pick
        # and it must not be parallel to Axis.
        for axis in ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)):
            matrix = subject.get_axis2placement(self.placement_3d(axis))
            assert np.allclose(matrix[:3, 2], axis)
            assert_orthonormal(matrix)

    def test_axis2placement3d_along_the_other_axes_without_a_ref_direction(self):
        for axis in ((0.0, 0.0, 1.0), (0.0, 1.0, 0.0), (0.0, 0.0, -1.0)):
            matrix = subject.get_axis2placement(self.placement_3d(axis))
            assert np.allclose(matrix[:3, 2], axis)
            assert_orthonormal(matrix)

    def test_axis1placement_along_x(self):
        # IfcAxis1Placement has no RefDirection attribute at all, so an axis of
        # (1, 0, 0) is perfectly valid and must not produce NaN.
        placement = self.file.createIfcAxis1Placement(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )
        matrix = subject.get_axis2placement(placement)
        assert np.allclose(matrix[:3, 2], (1.0, 0.0, 0.0))
        assert_orthonormal(matrix)
