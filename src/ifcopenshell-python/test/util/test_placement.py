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
import pytest

import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.placement as subject
import test.bootstrap


class TestGetAxis2PlacementIFC4(test.bootstrap.IFC4):
    def test_2d_placement(self):
        placement = self.file.createIfcAxis2Placement2D(
            self.file.createIfcCartesianPoint((1.0, 2.0)), self.file.createIfcDirection((0.0, 1.0))
        )
        matrix = subject.get_placement(placement)
        assert np.allclose(matrix[:, 3], (1.0, 2.0, 0.0, 1.0))
        assert np.allclose(matrix[:3, 0], (0.0, 1.0, 0.0))
        assert np.allclose(matrix[:3, 2], (0.0, 0.0, 1.0))

    def test_axis1_placement_along_negative_x(self):
        placement = self.file.createIfcAxis1Placement(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)), self.file.createIfcDirection((-1.0, 0.0, 0.0))
        )
        rotation = subject.get_placement(placement)[:3, :3]
        assert np.allclose(rotation @ rotation.T, np.eye(3))
        assert np.allclose(rotation[:, 2], (-1.0, 0.0, 0.0))


class TestGetLocalPlacementIFC4(test.bootstrap.IFC4):
    def test_composing_parent_placements(self):
        parent = self.file.createIfcLocalPlacement(
            RelativePlacement=self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((1.0, 2.0, 3.0)))
        )
        child = self.file.createIfcLocalPlacement(
            parent, self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((10.0, 0.0, 0.0)))
        )
        assert np.allclose(subject.get_placement(child)[:, 3], (11.0, 2.0, 3.0, 1.0))

    def test_returning_identity_without_a_placement(self):
        assert np.array_equal(subject.get_placement(None), np.eye(4))

    def test_returning_file_units_or_si(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        placement = self.file.createIfcLocalPlacement(
            RelativePlacement=self.file.createIfcAxis2Placement3D(
                self.file.createIfcCartesianPoint((1000.0, 2000.0, 3000.0))
            )
        )
        assert np.allclose(subject.get_placement(placement)[:3, 3], (1000.0, 2000.0, 3000.0))
        assert np.allclose(subject.get_placement(placement, should_return_si=True)[:3, 3], (1.0, 2.0, 3.0))


class TestGetPlacementForTransformationOperatorIFC4(test.bootstrap.IFC4):
    def test_non_uniform_scaling_along_rotated_axes(self):
        operator = self.file.createIfcCartesianTransformationOperator3DnonUniform(
            Axis1=self.file.createIfcDirection((0.0, 0.0, 1.0)),
            Axis3=self.file.createIfcDirection((1.0, 0.0, 0.0)),
            LocalOrigin=self.file.createIfcCartesianPoint((5.0, 6.0, 7.0)),
            Scale=2.0,
            Scale2=3.0,
            Scale3=4.0,
        )
        matrix = subject.get_placement(operator)
        assert np.allclose(matrix[:3, 0], (0.0, 0.0, 2.0))
        assert np.allclose(matrix[:3, 1], (0.0, 3.0, 0.0))
        assert np.allclose(matrix[:3, 2], (4.0, 0.0, 0.0))
        assert np.allclose(matrix[:3, 3], (5.0, 6.0, 7.0))

    def test_mirroring_when_axis2_opposes_the_right_handed_y(self):
        operator = self.file.createIfcCartesianTransformationOperator3D(
            Axis1=self.file.createIfcDirection((1.0, 0.0, 0.0)),
            Axis2=self.file.createIfcDirection((0.0, -1.0, 0.0)),
            LocalOrigin=self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
        )
        matrix = subject.get_placement(operator)
        assert np.allclose(matrix[:3, 1], (0.0, -1.0, 0.0))
        assert np.linalg.det(matrix[:3, :3]) == pytest.approx(-1.0)

    def test_2d_operator(self):
        operator = self.file.createIfcCartesianTransformationOperator2D(
            Axis1=self.file.createIfcDirection((0.0, 1.0)),
            LocalOrigin=self.file.createIfcCartesianPoint((1.0, 2.0)),
            Scale=3.0,
        )
        matrix = subject.get_placement(operator)
        assert np.allclose(matrix[:3, 0], (0.0, 3.0, 0.0))
        assert np.allclose(matrix[:3, 1], (-3.0, 0.0, 0.0))
        assert np.allclose(matrix[:3, 2], (0.0, 0.0, 1.0))
        assert np.allclose(matrix[:3, 3], (1.0, 2.0, 0.0))


class TestGetMappedItemTransformationIFC4(test.bootstrap.IFC4):
    def test_composing_the_mapping_origin_and_target(self):
        source = self.file.createIfcRepresentationMap(
            MappingOrigin=self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((1.0, 0.0, 0.0)))
        )
        target = self.file.createIfcCartesianTransformationOperator3D(
            LocalOrigin=self.file.createIfcCartesianPoint((0.0, 0.0, 10.0)), Scale=2.0
        )
        item = self.file.createIfcMappedItem(MappingSource=source, MappingTarget=target)
        matrix = subject.get_mappeditem_transformation(item)
        assert np.allclose(matrix @ np.array((0.0, 0.0, 0.0, 1.0)), (2.0, 0.0, 10.0, 1.0))


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
