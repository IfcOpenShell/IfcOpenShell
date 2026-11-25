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

import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.guid
import ifcopenshell.util.placement as subject
import test.bootstrap


class TestA2P(test.bootstrap.IFC4):
    def test_projecting_a_non_perpendicular_x_axis_onto_the_plane_normal_to_z(self):
        matrix = subject.a2p((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 1.0))
        assert np.allclose(matrix, np.eye(4))

    def test_keeping_an_already_perpendicular_x_axis_unchanged(self):
        matrix = subject.a2p((1.0, 2.0, 3.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))
        assert np.allclose(matrix[:3, 0], (0.0, 1.0, 0.0))
        assert np.allclose(matrix[:3, 1], (-1.0, 0.0, 0.0))
        assert np.allclose(matrix[:3, 2], (0.0, 0.0, 1.0))
        assert np.allclose(matrix[:3, 3], (1.0, 2.0, 3.0))


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


def create_placement(file, location, x_axis=None, relative_to=None):
    return file.createIfcLocalPlacement(
        relative_to,
        file.createIfcAxis2Placement3D(
            file.createIfcCartesianPoint(location),
            None,
            file.createIfcDirection(x_axis) if x_axis else None,
        ),
    )


def create_polyline(file, points):
    return file.createIfcPolyline([file.createIfcCartesianPoint(p) for p in points])


def create_grid_axis(file, axes="UAxes", curve=None, object_placement=None):
    axis = file.createIfcGridAxis("A", curve, True)
    grid = file.createIfcGrid(ifcopenshell.guid.new(), ObjectPlacement=object_placement)
    setattr(grid, axes, [axis])
    return axis


class TestGetGridAxisCoordinatesIFC4(test.bootstrap.IFC4):
    def test_getting_the_points_of_a_polyline_axis(self):
        axis = create_grid_axis(self.file, curve=create_polyline(self.file, ((0.0, 0.0), (10.0, 0.0))))
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])

    def test_applying_the_grid_placement(self):
        axis = create_grid_axis(
            self.file,
            curve=create_polyline(self.file, ((0.0, 0.0), (10.0, 0.0))),
            object_placement=create_placement(self.file, (5.0, 5.0, 1.0), x_axis=(0.0, 1.0, 0.0)),
        )
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[5.0, 5.0, 1.0], [5.0, 15.0, 1.0]])

    def test_applying_a_placement_relative_to_another(self):
        site = create_placement(self.file, (100.0, 0.0, 0.0))
        axis = create_grid_axis(
            self.file,
            curve=create_polyline(self.file, ((0.0, 0.0), (0.0, 10.0))),
            object_placement=create_placement(self.file, (0.0, 50.0, 0.0), relative_to=site),
        )
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[100.0, 50.0, 0.0], [100.0, 60.0, 0.0]])

    def test_keeping_the_z_of_3d_points(self):
        axis = create_grid_axis(self.file, curve=create_polyline(self.file, ((0.0, 0.0, 2.0), (10.0, 0.0, 2.0))))
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[0.0, 0.0, 2.0], [10.0, 0.0, 2.0]])

    @pytest.mark.parametrize("axes", ("UAxes", "VAxes", "WAxes"))
    def test_finding_the_grid_from_any_axis_list(self, axes):
        axis = create_grid_axis(
            self.file,
            axes=axes,
            curve=create_polyline(self.file, ((0.0, 0.0), (1.0, 0.0))),
            object_placement=create_placement(self.file, (0.0, 0.0, 3.0)),
        )
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[0.0, 0.0, 3.0], [1.0, 0.0, 3.0]])

    def test_getting_the_points_of_an_indexed_poly_curve_without_segments(self):
        points = self.file.createIfcCartesianPointList2D(((0.0, 0.0), (5.0, 0.0), (10.0, 0.0)))
        axis = create_grid_axis(self.file, curve=self.file.createIfcIndexedPolyCurve(points))
        assert np.allclose(
            subject.get_grid_axis_coordinates(axis), [[0.0, 0.0, 0.0], [5.0, 0.0, 0.0], [10.0, 0.0, 0.0]]
        )

    def test_walking_the_line_segments_of_an_indexed_poly_curve(self):
        points = self.file.createIfcCartesianPointList2D(((0.0, 0.0), (5.0, 0.0), (10.0, 0.0)))
        segments = [self.file.createIfcLineIndex((3, 2)), self.file.createIfcLineIndex((2, 1))]
        axis = create_grid_axis(self.file, curve=self.file.createIfcIndexedPolyCurve(points, segments))
        assert np.allclose(
            subject.get_grid_axis_coordinates(axis), [[10.0, 0.0, 0.0], [5.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        )

    def test_subdividing_the_arc_of_an_indexed_poly_curve(self):
        points = self.file.createIfcCartesianPointList2D(((0.0, 0.0), (4.0, 0.0), (5.0, 1.0), (4.0, 2.0)))
        segments = [self.file.createIfcLineIndex((1, 2)), self.file.createIfcArcIndex((2, 3, 4))]
        axis = create_grid_axis(
            self.file,
            curve=self.file.createIfcIndexedPolyCurve(points, segments),
            object_placement=create_placement(self.file, (10.0, 0.0, 0.0)),
        )
        coordinates = subject.get_grid_axis_coordinates(axis)
        assert len(coordinates) > 3
        assert np.allclose(coordinates[:2], [[10.0, 0.0, 0.0], [14.0, 0.0, 0.0]])
        assert np.allclose(coordinates[-1], [14.0, 2.0, 0.0])
        assert np.allclose(np.linalg.norm(coordinates[1:] - (14.0, 1.0, 0.0), axis=1), 1.0)
        assert np.all(coordinates[1:, 0] >= 14.0 - 1e-9)

    def test_walking_a_circle_axis(self):
        circle = self.file.createIfcCircle(
            self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint((1.0, 2.0))), 5.0
        )
        axis = create_grid_axis(self.file, curve=circle)
        coordinates = subject.get_grid_axis_coordinates(axis)
        assert len(coordinates) > 4
        assert np.allclose(coordinates[0], [6.0, 2.0, 0.0])
        assert np.allclose(coordinates[-1], coordinates[0])
        assert np.allclose(np.linalg.norm(coordinates - (1.0, 2.0, 0.0), axis=1), 5.0)

    def test_walking_a_trimmed_circle_axis(self):
        circle = self.file.createIfcCircle(
            self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint((0.0, 0.0))), 5.0
        )
        curve = self.file.createIfcTrimmedCurve(
            circle,
            [self.file.createIfcCartesianPoint((5.0, 0.0))],
            [self.file.createIfcCartesianPoint((0.0, 5.0))],
            True,
            "CARTESIAN",
        )
        coordinates = subject.get_grid_axis_coordinates(create_grid_axis(self.file, curve=curve))
        assert len(coordinates) > 2
        assert np.allclose(coordinates[0], [5.0, 0.0, 0.0])
        assert np.allclose(coordinates[-1], [0.0, 5.0, 0.0])
        assert np.allclose(np.linalg.norm(coordinates, axis=1), 5.0)
        assert np.all(coordinates[:, :2] >= -1e-9)

    def test_walking_a_composite_curve_axis(self):
        segments = [
            self.file.createIfcCompositeCurveSegment(
                "CONTINUOUS", True, create_polyline(self.file, ((0.0, 0.0), (4.0, 0.0)))
            ),
            self.file.createIfcCompositeCurveSegment(
                "CONTINUOUS", False, create_polyline(self.file, ((4.0, 3.0), (4.0, 0.0)))
            ),
        ]
        axis = create_grid_axis(self.file, curve=self.file.createIfcCompositeCurve(segments, False))
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[0.0, 0.0, 0.0], [4.0, 0.0, 0.0], [4.0, 3.0, 0.0]])

    def test_keeping_discontinuous_composite_vertices(self):
        segments = [
            self.file.createIfcCompositeCurveSegment(
                "DISCONTINUOUS", True, create_polyline(self.file, ((0.0, 0.0), (4.0, 0.0)))
            ),
            self.file.createIfcCompositeCurveSegment(
                "DISCONTINUOUS", False, create_polyline(self.file, ((8.0, 3.0), (6.0, 1.0)))
            ),
        ]
        curve = self.file.createIfcCompositeCurve(segments, False)
        axis = create_grid_axis(self.file, curve=curve, object_placement=create_placement(self.file, (10.0, 20.0, 2.0)))
        expected = np.array(((0.0, 0.0, 0.0), (4.0, 0.0, 0.0), (6.0, 1.0, 0.0), (8.0, 3.0, 0.0)))
        coordinates = subject.get_grid_axis_coordinates(axis)
        assert coordinates.shape == (4, 3)
        assert np.allclose(coordinates, expected + (10.0, 20.0, 2.0))

    def test_chaining_geometry_failures_as_axis_value_errors(self):
        spline = self.file.createIfcBSplineCurveWithKnots(
            2,
            [self.file.createIfcCartesianPoint(p) for p in ((0.0, 0.0), (1.0, 2.0), (3.0, 0.0))],
            "UNSPECIFIED",
            False,
            False,
            (3, 3),
            (0.0, 1.0),
            "UNSPECIFIED",
        )
        curve = self.file.createIfcTrimmedCurve(
            spline,
            [self.file.createIfcParameterValue(0.0)],
            [self.file.createIfcParameterValue(1.0)],
            True,
            "PARAMETER",
        )
        axis = create_grid_axis(self.file, curve=curve)
        with pytest.raises(ValueError, match=rf"IfcGridAxis #{axis.id()} 'A'.*can not be interpreted") as error:
            subject.get_grid_axis_coordinates(axis)
        assert isinstance(error.value.__cause__, RuntimeError)
        assert str(error.value.__cause__) in str(error.value)

    def test_returning_project_length_units(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        axis = create_grid_axis(
            self.file,
            curve=create_polyline(self.file, ((0.0, 0.0), (10000.0, 0.0))),
            object_placement=create_placement(self.file, (5000.0, 0.0, 0.0)),
        )
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[5000.0, 0.0, 0.0], [15000.0, 0.0, 0.0]])

    def test_raising_for_an_unbounded_axis(self):
        line = self.file.createIfcLine(
            self.file.createIfcCartesianPoint((0.0, 0.0)),
            self.file.createIfcVector(self.file.createIfcDirection((1.0, 0.0)), 1.0),
        )
        axis = create_grid_axis(self.file, curve=line)
        with pytest.raises(ValueError, match=rf"#{axis.id()} 'A' has an unbounded IfcLine as AxisCurve"):
            subject.get_grid_axis_coordinates(axis)

    def test_raising_for_an_axis_without_a_curve(self):
        file = ifcopenshell.file.from_string(
            "ISO-10303-21;HEADER;FILE_DESCRIPTION((''),'2;1');"
            "FILE_NAME('','',(''),(''),'','','');FILE_SCHEMA(('IFC4'));ENDSEC;DATA;"
            "#1=IFCGRIDAXIS('A',$,.T.);"
            "#2=IFCGRID('0YvctVUKr0kugbFTf53O9L',$,$,$,$,$,$,(#1),(),$,$);"
            "ENDSEC;END-ISO-10303-21;"
        )
        with pytest.raises(ValueError, match="#1 'A' has no AxisCurve"):
            subject.get_grid_axis_coordinates(file.by_id(1))

    def test_raising_for_an_axis_outside_a_grid(self):
        axis = self.file.createIfcGridAxis("B", create_polyline(self.file, ((0.0, 0.0), (1.0, 0.0))), True)
        with pytest.raises(ValueError, match=rf"#{axis.id()} 'B' belongs to no IfcGrid"):
            subject.get_grid_axis_coordinates(axis)


class TestGetGridAxisCoordinatesIFC4X3(test.bootstrap.IFC4X3):
    def test_sampling_an_alignment_curve_axis(self):
        segment = self.file.createIfcCurveSegment(
            Transition="CONTINUOUS",
            Placement=self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint((1.0, 2.0))),
            SegmentStart=self.file.createIfcLengthMeasure(0.0),
            SegmentLength=self.file.createIfcLengthMeasure(10.0),
            ParentCurve=self.file.createIfcLine(
                self.file.createIfcCartesianPoint((0.0, 0.0)),
                self.file.createIfcVector(self.file.createIfcDirection((1.0, 0.0)), 1.0),
            ),
        )
        axis = create_grid_axis(
            self.file,
            curve=self.file.createIfcCompositeCurve([segment], False),
            object_placement=create_placement(self.file, (0.0, 0.0, 4.0)),
        )
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[1.0, 2.0, 4.0], [11.0, 2.0, 4.0]])

    def test_applying_the_grid_placement(self):
        axis = create_grid_axis(
            self.file,
            curve=create_polyline(self.file, ((0.0, 0.0), (10.0, 0.0))),
            object_placement=create_placement(self.file, (2.0, 3.0, 4.0), x_axis=(0.0, 1.0, 0.0)),
        )
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[2.0, 3.0, 4.0], [2.0, 13.0, 4.0]])


class TestGetGridAxisCoordinatesIFC2X3(test.bootstrap.IFC2X3):
    def test_applying_the_grid_placement(self):
        axis = create_grid_axis(
            self.file,
            axes="VAxes",
            curve=create_polyline(self.file, ((0.0, 0.0), (10.0, 0.0))),
            object_placement=create_placement(self.file, (1.0, 2.0, 0.0)),
        )
        assert np.allclose(subject.get_grid_axis_coordinates(axis), [[1.0, 2.0, 0.0], [11.0, 2.0, 0.0]])
