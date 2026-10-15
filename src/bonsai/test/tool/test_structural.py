# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import math

import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.structural
import numpy as np

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.structural import Structural as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Structural)


class TestGetInPlaneComponents(NewFile):
    def test_an_angle_above_the_horizontal(self):
        x, z = subject.get_in_plane_components("ANGLE", magnitude=10, angle=30)
        assert math.isclose(x, 10 * math.cos(math.radians(30)))
        assert math.isclose(z, 5)

    def test_a_slope(self):
        x, z = subject.get_in_plane_components("SLOPE", magnitude=10, rise=5, run=12)
        assert math.isclose(x, 120 / 13)
        assert math.isclose(z, 50 / 13)

    def test_angles_measure_from_the_axis_of_their_eighth(self):
        x, z = subject.get_in_plane_components("ANGLE", magnitude=100, angle=40, direction="Q4")
        assert math.isclose(x, -100 * math.cos(math.radians(40)))
        assert math.isclose(z, 100 * math.sin(math.radians(40)))
        # Q6 is measured from -Z, turning left.
        x, z = subject.get_in_plane_components("ANGLE", magnitude=100, angle=25, direction="Q6")
        assert math.isclose(x, -100 * math.sin(math.radians(25)))
        assert math.isclose(z, -100 * math.cos(math.radians(25)))

    def test_slopes_rise_vertically_in_any_eighth_of_their_quadrant(self):
        for direction in ("Q5", "Q6"):
            x, z = subject.get_in_plane_components("SLOPE", magnitude=200, rise=3, run=4, direction=direction)
            assert math.isclose(x, -160)
            assert math.isclose(z, -120)

    def test_an_axis_direction_has_no_rounding_noise(self):
        assert subject.get_in_plane_components("ANGLE", magnitude=50, angle=0, direction="Q7") == (0.0, -50.0)

    def test_a_zero_slope_gives_no_force(self):
        assert subject.get_in_plane_components("SLOPE", magnitude=10, rise=0, run=0) == (0.0, 0.0)


class TestGetEighth(NewFile):
    def test_the_eighth_and_angle_from_its_axis(self):
        eighth, angle, along, across = subject.get_eighth(-30, 40)
        assert eighth == "Q3"
        assert math.isclose(angle, math.degrees(math.atan2(30, 40)))
        assert math.isclose(along, 40) and math.isclose(across, 30)

    def test_a_diagonal_measures_from_the_horizontal(self):
        assert subject.get_eighth(-1, -1)[0] == "Q5"

    def test_a_preferred_eighth_on_its_boundary(self):
        assert subject.get_eighth(1, 1, "Q2")[0] == "Q2"
        assert subject.get_eighth(1, 2, "Q8")[0] == "Q2"  # Not in Q8, so not taken.


class TestGetSimpleSlope(NewFile):
    def test_reducing_to_small_whole_numbers(self):
        assert subject.get_simple_slope(-160, -120) == (-3, -4)
        assert subject.get_simple_slope(134.16407864998737, -268.3281572999747) == (-2, 1)

    def test_axis_aligned_components(self):
        assert subject.get_simple_slope(5, 0) == (0.0, 1.0)
        assert subject.get_simple_slope(0, -5) == (-1.0, 0.0)

    def test_falling_back_to_a_unit_slope(self):
        rise, run = subject.get_simple_slope(3, 7.1)
        assert math.isclose(math.hypot(rise, run), 1)
        assert math.isclose(rise / run, 7.1 / 3)


class TestSolveTwoForceMagnitudes(NewFile):
    def test_two_pulls_making_a_resultant(self):
        # Two pulls at 20 degrees up and 30 degrees down from a horizontal 120.
        first = (math.cos(math.radians(20)), 0, math.sin(math.radians(20)))
        second = (math.cos(math.radians(30)), 0, -math.sin(math.radians(30)))
        a, b = subject.solve_two_force_magnitudes((120, 0, 0), first, second)
        assert math.isclose(a, 120 * math.sin(math.radians(30)) / math.sin(math.radians(130)))
        assert math.isclose(b, 120 * math.sin(math.radians(20)) / math.sin(math.radians(130)))

    def test_a_negative_magnitude_reverses_a_force(self):
        a, b = subject.solve_two_force_magnitudes((-1, 0, 0), (1, 0, 0), (0, 0, 1))
        assert math.isclose(a, -1)
        assert math.isclose(b, 0, abs_tol=1e-12)

    def test_parallel_directions_have_no_solution(self):
        assert subject.solve_two_force_magnitudes((1, 0, 1), (1, 0, 0), (-1, 0, 0)) is None

    def test_a_target_out_of_their_plane_has_no_solution(self):
        assert subject.solve_two_force_magnitudes((0, 10, 0), (1, 0, 0), (0, 0, 1)) is None


class TestSolveUnknowns(NewFile):
    def test_two_force_magnitudes_for_a_known_resultant(self):
        forces, resultant, error = subject.solve_unknowns(
            [(10, 0, 0), (0, 0, 10), (5, 0, 5)], [(False, True), (False, True), (True, True)], (35, 0, 45), (True, True)
        )
        assert not error
        assert math.isclose(forces[0][0], 30) and math.isclose(forces[1][2], 40)
        assert forces[2] == (5, 0, 5) and resultant == (35, 0, 45)

    def test_a_force_magnitude_and_the_resultant_along_its_direction(self):
        # A known pull down and right, and a pull down and left of unknown size, whose sum acts straight down.
        forces, resultant, error = subject.solve_unknowns(
            [(30, 0, -40), (-1, 0, -1)], [(True, True), (False, True)], (0, 0, -1), (False, True)
        )
        assert not error
        assert math.isclose(forces[1][0], -30) and math.isclose(forces[1][2], -30)
        assert math.isclose(resultant[0], 0, abs_tol=1e-9) and math.isclose(resultant[2], -70)

    def test_a_whole_force_making_up_a_known_resultant(self):
        forces, resultant, error = subject.solve_unknowns(
            [(20, 0, 0), (1, 0, 1)], [(True, True), (False, False)], (5, 0, 12), (True, True)
        )
        assert not error and forces[1] == (-15, 0, 12)

    def test_the_sum_when_only_the_resultant_is_unknown(self):
        forces, resultant, error = subject.solve_unknowns(
            [(3, 0, 4), (1, 0, -1)], [(True, True), (True, True)], (0, 0, 0), (False, False)
        )
        assert not error and resultant == (4, 0, 3)

    def test_naming_the_unknowns_when_there_are_not_two(self):
        error = subject.solve_unknowns([(1, 0, 0)], [(False, True)], (0, 0, 1), (False, False))[2]
        assert error.startswith("Unlocked: F₁ magnitude, R magnitude, R direction")
        assert subject.solve_unknowns([(1, 0, 0)], [(True, True)], (1, 0, 0), (True, True))[2].startswith("Nothing")

    def test_a_direction_with_another_unknown_is_not_solved(self):
        error = subject.solve_unknowns([(1, 0, 0), (0, 0, 1)], [(True, False), (False, True)], (1, 0, 1), (True, True))[
            2
        ]
        assert "not supported" in error


class TestGetAxesTilt(NewFile):
    def test_a_point_without_axes_of_its_own(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        point = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection")
        assert subject.get_axes_tilt(point) == 0.0

    def test_axes_tilted_in_the_x_z_plane(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        point = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection")
        for tilt in (25, -60, 135):
            angle = math.radians(tilt)
            ifcopenshell.api.structural.edit_structural_connection_cs(
                ifc_file,
                structural_item=point,
                axis=(-math.sin(angle), 0, math.cos(angle)),
                ref_direction=(math.cos(angle), 0, math.sin(angle)),
            )
            assert math.isclose(subject.get_axes_tilt(point), tilt)

    def test_axes_turned_out_of_the_x_z_plane(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        point = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection")
        ifcopenshell.api.structural.edit_structural_connection_cs(
            ifc_file, structural_item=point, axis=(0, 0, 1), ref_direction=(0.6, 0.8, 0)
        )
        assert subject.get_axes_tilt(point) is None


def new_point() -> ifcopenshell.entity_instance:
    ifc_file = ifcopenshell.file(schema="IFC4")
    tool.Ifc.set(ifc_file)
    return ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection")


def tilt_axes(point: ifcopenshell.entity_instance, tilt: float) -> None:
    angle = math.radians(tilt)
    ifcopenshell.api.structural.edit_structural_connection_cs(
        tool.Ifc.get(),
        structural_item=point,
        axis=(-math.sin(angle), 0, math.cos(angle)),
        ref_direction=(math.cos(angle), 0, math.sin(angle)),
    )


class TestGetAxesRotation(NewFile):
    def test_global_axes_for_a_point_without_its_own(self):
        assert (subject.get_axes_rotation(new_point()) == np.eye(3)).all()

    def test_x_and_z_as_columns(self):
        point = new_point()
        tilt_axes(point, 30)
        rotation = subject.get_axes_rotation(point)
        assert np.allclose(rotation[:, 0], (math.cos(math.radians(30)), 0, 0.5))
        assert np.allclose(rotation[:, 2], (-0.5, 0, math.cos(math.radians(30))))


class TestAxesSlope(NewFile):
    def test_a_slope_matching_the_tilt(self):
        point = new_point()
        tilt_axes(point, math.degrees(math.atan2(4, 12)))
        subject.set_axes_slope(point, (4.0, 12.0))
        assert subject.get_axes_slope(point) == (4.0, 12.0)

    def test_a_slope_falling_to_the_right(self):
        point = new_point()
        tilt_axes(point, -math.degrees(math.atan2(4, 12)))
        subject.set_axes_slope(point, (4.0, 12.0))
        assert subject.get_axes_slope(point) == (4.0, 12.0)

    def test_a_slope_gone_stale_is_not_given(self):
        point = new_point()
        tilt_axes(point, 30)
        subject.set_axes_slope(point, (4.0, 12.0))
        assert subject.get_axes_slope(point) is None

    def test_forgetting_a_slope(self):
        point = new_point()
        tilt_axes(point, math.degrees(math.atan2(4, 12)))
        subject.set_axes_slope(point, (4.0, 12.0))
        subject.set_axes_slope(point, None)
        assert subject.get_axes_slope(point) is None


class TestGetAxesTerms(NewFile):
    def test_global_axes(self):
        assert subject.get_axes_terms(new_point()) == ("ANGLE", "Q1", 0.0, None)

    def test_axes_set_by_an_angle(self):
        point = new_point()
        tilt_axes(point, -25)
        mode, eighth, angle, slope = subject.get_axes_terms(point)
        assert (mode, eighth, slope) == ("ANGLE", "Q8", None)
        assert math.isclose(angle, 25)

    def test_axes_set_by_a_slope(self):
        point = new_point()
        tilt_axes(point, math.degrees(math.atan2(4, 12)))
        subject.set_axes_slope(point, (4.0, 12.0))
        mode, eighth, angle, slope = subject.get_axes_terms(point)
        assert (mode, eighth, slope) == ("SLOPE", "Q1", (4.0, 12.0))
        assert math.isclose(angle, math.degrees(math.atan2(4, 12)))

    def test_axes_turned_in_3d(self):
        point = new_point()
        ifcopenshell.api.structural.edit_structural_connection_cs(
            tool.Ifc.get(), structural_item=point, axis=(0, 0, 1), ref_direction=(0.6, 0.8, 0)
        )
        assert subject.get_axes_terms(point) == ("THREE_D", None, 0.0, None)


class TestPushAndKnownComponent(NewFile):
    def test_a_push(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        activity = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointAction")
        assert not subject.get_push(activity)
        subject.set_push(activity, True)
        assert subject.get_push(activity)
        subject.set_push(activity, False)
        assert not subject.get_push(activity)

    def test_a_known_component(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        activity = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointAction")
        assert subject.get_known_component(activity) is None
        subject.set_known_component(activity, "Z")
        assert subject.get_known_component(activity) == "Z"
        subject.set_known_component(activity, None)
        assert subject.get_known_component(activity) is None
