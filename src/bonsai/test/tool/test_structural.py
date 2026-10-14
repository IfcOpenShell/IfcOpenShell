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
from bonsai.bim.module.structural.load_decoration_data import box_crosses_segments
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


class TestGetAngleFromEighth(NewFile):
    def test_either_axis_of_a_quadrant(self):
        # Up and to the left, 30 degrees off the vertical.
        x, z = -math.sin(math.radians(30)), math.cos(math.radians(30))
        assert math.isclose(subject.get_angle_from_eighth(x, z, "Q3"), 30)
        assert math.isclose(subject.get_angle_from_eighth(x, z, "Q4"), 60)

    def test_any_eighth_turning_its_way(self):
        # Up and to the left at 45 degrees: from -Z turning left, past -X; from -Z turning right, past +X and +Z.
        assert math.isclose(subject.get_angle_from_eighth(-1, 1, "Q6"), 135)
        assert math.isclose(subject.get_angle_from_eighth(-1, 1, "Q7"), 225)
        assert math.isclose(subject.get_angle_from_eighth(-1, 1, "Q1"), 135)

    def test_along_an_axis(self):
        assert subject.get_angle_from_eighth(0, 1, "Q2") == 0.0
        assert subject.get_angle_from_eighth(0, 1, "Q1") == 90.0

    def test_no_direction(self):
        assert subject.get_angle_from_eighth(0, 0, "Q1") is None


class TestResultantEighth(NewFile):
    def test_choosing_and_forgetting_per_load_case(self):
        point = new_point()
        ifc_file = tool.Ifc.get()
        first = ifcopenshell.api.structural.add_structural_load_case(ifc_file, name="First")
        second = ifcopenshell.api.structural.add_structural_load_case(ifc_file, name="Second")
        assert subject.get_resultant_eighth(point, first) is None
        subject.set_resultant_eighth(point, first, "Q4")
        subject.set_resultant_eighth(point, second, "Q6")
        assert subject.get_resultant_eighth(point, first) == "Q4"
        assert subject.get_resultant_eighth(point, second) == "Q6"
        subject.set_resultant_eighth(point, first, None)
        assert subject.get_resultant_eighth(point, first) is None
        assert subject.get_resultant_eighth(point, second) == "Q6"


class TestBoxCrossesSegments(NewFile):
    # A label's box from (0, 0), 10 wide and 5 high.
    def test_lines_crossing_or_inside(self):
        assert box_crosses_segments(0, 0, 10, 5, [((-5, 2), (15, 2))])
        assert box_crosses_segments(0, 0, 10, 5, [((2, 1), (3, 2))])
        assert box_crosses_segments(0, 0, 10, 5, [((-1, 4), (1, 6))])  # Across a corner.

    def test_lines_clear_of_it(self):
        assert not box_crosses_segments(0, 0, 10, 5, [((-5, 8), (15, 8))])
        assert not box_crosses_segments(0, 0, 10, 5, [((12, 0), (20, 10))])
        assert not box_crosses_segments(0, 0, 10, 5, [])

    def test_any_of_several(self):
        assert box_crosses_segments(0, 0, 10, 5, [((-5, 8), (15, 8)), ((5, -5), (5, 10))])


class TestPointAxesComponents(NewFile):
    def test_global_components_along_tilted_axes(self):
        # Axes tilted 30 degrees: x' up a 30 degree incline, z' square to it.
        x, z = subject.to_axes(math.cos(math.radians(30)), math.sin(math.radians(30)), 30)
        assert math.isclose(x, 1) and math.isclose(z, 0, abs_tol=1e-12)
        x, z = subject.to_axes(0, 1, 30)
        assert math.isclose(x, 0.5) and math.isclose(z, math.cos(math.radians(30)))

    def test_back_to_global(self):
        x, z = subject.from_axes(*subject.to_axes(3.0, -4.0, -25), -25)
        assert math.isclose(x, 3.0) and math.isclose(z, -4.0)


def direction(degrees: float, magnitude: float = 1.0) -> tuple[float, float, float]:
    return (magnitude * math.cos(math.radians(degrees)), 0.0, magnitude * math.sin(math.radians(degrees)))


class TestSolveLinkedUnknowns(NewFile):
    def test_equal_magnitudes_count_as_one_unknown(self):
        # A known pull, and two pulls of unknown but equal magnitude, whose resultant is vertical.
        forces = [direction(-40, 6), direction(200), direction(230)]
        locks = [(True, True), (False, True), (False, True)]
        solved, resultant, error = subject.solve_unknowns(forces, locks, (0, 0, -1), (False, True), [None, "T", "T"])
        expected = 6 * math.cos(math.radians(40)) / (math.cos(math.radians(20)) + math.cos(math.radians(50)))
        assert not error
        assert math.isclose(math.hypot(*solved[1]), expected) and math.isclose(math.hypot(*solved[2]), expected)
        assert math.isclose(sum(f[0] for f in solved), 0, abs_tol=1e-9) and resultant[0] == 0

    def test_without_the_link_there_are_too_many_unknowns(self):
        forces = [direction(-40, 6), direction(200), direction(230)]
        locks = [(True, True), (False, True), (False, True)]
        assert "Two can be found" in subject.solve_unknowns(forces, locks, (0, 0, -1), (False, True))[2]

    def test_a_linked_magnitude_follows_a_known_one(self):
        forces = [direction(-40, 6), direction(200, 3), direction(230), direction(90)]
        locks = [(True, True), (True, True), (False, True), (False, True)]
        solved, _, error = subject.solve_unknowns(forces, locks, (0, 0, 0), (True, True), [None, "T", "T", None])
        assert error.startswith("Unlocked: F")  # Only the fourth is unknown once the third follows the second.
        solved, _, error = subject.solve_unknowns(
            forces, [*locks[:3], (False, False)], (0, 0, 0), (True, True), [None, "T", "T", None]
        )
        assert not error and math.isclose(math.hypot(*solved[2]), 3)

    def test_a_magnitude_a_multiple_of_another(self):
        forces = [direction(-40, 6), direction(200), direction(230)]
        locks = [(True, True), (False, True), (False, True)]
        solved, _, error = subject.solve_unknowns(
            forces, locks, (0, 0, -1), (False, True), [None, "T", "T"], [1.0, 1.0, 0.25]
        )
        expected = 6 * math.cos(math.radians(40)) / (math.cos(math.radians(20)) + 0.25 * math.cos(math.radians(50)))
        assert not error
        assert math.isclose(math.hypot(*solved[1]), expected) and math.isclose(math.hypot(*solved[2]), expected / 4)

    def test_a_multiple_of_a_known_magnitude(self):
        forces = [direction(-40, 6), direction(200, 3), direction(230), direction(90)]
        locks = [(True, True), (True, True), (False, True), (False, False)]
        solved, _, error = subject.solve_unknowns(
            forces, locks, (0, 0, 0), (True, True), [None, "T", "T", None], [1.0, 1.0, 0.5, 1.0]
        )
        assert not error and math.isclose(math.hypot(*solved[2]), 1.5)


class TestMagnitudeGroups(NewFile):
    def test_linked_directly_and_through_another(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        activities = [
            ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointAction") for _ in range(4)
        ]
        subject.set_magnitude_link(activities[1], activities[0])
        subject.set_magnitude_link(activities[2], activities[1])
        groups = subject.get_magnitude_groups(activities)
        assert groups[0] == groups[1] == groups[2] and groups[0] is not None and groups[3] is None
        assert subject.get_magnitude_link(activities[1]) == activities[0].GlobalId

    def test_unlinking_and_overriding(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        first, second = (
            ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointAction") for _ in range(2)
        )
        subject.set_magnitude_link(second, first)
        assert subject.get_magnitude_groups([first, second], {second.GlobalId: None}) == [None, None]
        subject.set_magnitude_link(second, None)
        assert subject.get_magnitude_link(second) is None

    def test_ratios_through_a_chain(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        first, second, third = (
            ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointAction") for _ in range(3)
        )
        subject.set_magnitude_link(second, first, 0.5)
        subject.set_magnitude_link(third, second, 0.25)
        assert subject.get_magnitude_ratio(second) == 0.5
        groups, factors = subject.get_magnitude_links([first, second, third])
        assert groups[0] == groups[1] == groups[2] is not None
        assert [f / factors[0] for f in factors] == [1.0, 0.5, 0.125]
        groups, factors = subject.get_magnitude_links([first, second, third], {third.GlobalId: (first.GlobalId, 2.0)})
        assert [f / factors[0] for f in factors] == [1.0, 0.5, 2.0]


class TestGetResultantFound(NewFile):
    def test_by_how_many_force_values_are_unknown(self):
        known, magnitude_unknown, both_unknown = (True, True), (False, True), (False, False)
        assert subject.get_resultant_found([known, known]) == ["magnitude", "direction"]
        assert subject.get_resultant_found([known, magnitude_unknown]) == ["magnitude"]
        assert subject.get_resultant_found([known, both_unknown]) == []

    def test_linked_magnitudes_count_once(self):
        locks = [(True, True), (False, True), (False, True)]
        assert subject.get_resultant_found(locks) == []
        assert subject.get_resultant_found(locks, [None, "T", "T"]) == ["magnitude"]
        assert subject.get_resultant_found([(True, True), (False, True)], ["T", "T"]) == ["magnitude", "direction"]


class TestGetMoment(NewFile):
    def test_counter_clockwise_positive_seen_from_minus_y(self):
        # A force up, to the right of the centre, turns counter-clockwise.
        moment, arm, foot = subject.get_moment(np.zeros(3), np.array((2.0, 0, 0)), np.array((0, 0, 5.0)))
        assert math.isclose(moment, 10) and math.isclose(arm, 2) and np.allclose(foot, (2, 0, 0))
        moment, _, _ = subject.get_moment(np.zeros(3), np.array((2.0, 0, 0)), np.array((0, 0, -5.0)))
        assert math.isclose(moment, -10)

    def test_the_arm_square_to_an_inclined_line_of_action(self):
        # Along a 3:4 line through (4, 0, 0), from the origin: the arm is 4 sin of its angle from X.
        force = np.array((-30.0, 0, 40.0))
        moment, arm, foot = subject.get_moment(np.zeros(3), np.array((4.0, 0, 0)), force)
        assert math.isclose(arm, 4 * 0.8) and math.isclose(moment, 50 * arm)
        assert math.isclose(float(np.dot(foot, force)), 0, abs_tol=1e-9)  # The arm is square to the force.

    def test_a_line_of_action_through_the_centre(self):
        moment, arm, _ = subject.get_moment(np.zeros(3), np.array((3.0, 0, 4.0)), np.array((6.0, 0, 8.0)))
        assert math.isclose(moment, 0, abs_tol=1e-9) and math.isclose(arm, 0, abs_tol=1e-9)


class TestMomentCentre(NewFile):
    def test_choosing_and_forgetting(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        case = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralLoadCase")
        point = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection")
        assert subject.get_moment_centre(case) is None
        subject.set_moment_centre(case, point)
        assert subject.get_moment_centre(case) == point
        subject.set_moment_centre(case, None)
        assert subject.get_moment_centre(case) is None


class TestSolveMomentUnknown(NewFile):
    def test_a_magnitude_for_the_moment(self):
        # A known 10 down at 2 to the right, and an upward force at 4 found to balance it.
        arms = [np.array((2.0, 0, 0)), np.array((4.0, 0, 0))]
        forces = [np.array((0, 0, -10.0)), np.array((0, 0, 1.0))]
        solved, error = subject.solve_moment_unknown(arms, forces, [(True, True), (False, True)], 0.0)
        assert not error and np.allclose(solved[1], (0, 0, 5))

    def test_a_magnitude_reversed_for_the_moment(self):
        arms = [np.array((2.0, 0, 0))]
        solved, error = subject.solve_moment_unknown(arms, [np.array((0, 0, 1.0))], [(False, True)], -20.0)
        assert not error and np.allclose(solved[0], (0, 0, -10))

    def test_linked_magnitudes_found_together(self):
        arms = [np.array((1.0, 0, 0)), np.array((3.0, 0, 0))]
        forces = [np.array((0, 0, 1.0)), np.array((0, 0, 1.0))]
        locks = [(False, True), (False, True)]
        solved, error = subject.solve_moment_unknown(arms, forces, locks, 30.0, ["T", "T"], [1.0, 2.0])
        # m (1 + 2 * 3) = 30, the second twice the first.
        assert not error and np.allclose(solved[0], (0, 0, 30 / 7)) and np.allclose(solved[1], (0, 0, 60 / 7))

    def test_a_direction_nearest_its_own(self):
        # 10 at 2 to the right makes at most 20; 10 needs the force 30 degrees off its arm.
        arms = [np.array((2.0, 0, 0))]
        start = np.array(direction(100, 10))  # Nearer 150 degrees than 30, of the two directions that make it.
        solved, error = subject.solve_moment_unknown(arms, [start], [(True, False)], 10.0)
        assert not error and math.isclose(math.hypot(solved[0][0], solved[0][2]), 10)
        assert math.isclose(2 * solved[0][2], 10) and solved[0][0] < 0  # 150 degrees from +X, not 30.

    def test_one_unknown_only(self):
        arms = [np.array((2.0, 0, 0))]
        assert "Unlock one" in subject.solve_moment_unknown(arms, [np.array((0, 0, 1.0))], [(True, True)], 5.0)[1]
        error = subject.solve_moment_unknown(arms, [np.array((0, 0, 1.0))], [(False, False)], 5.0)[1]
        assert error.startswith("Unlocked: F1 magnitude, F1 direction")

    def test_no_moment_to_make(self):
        arms = [np.array((2.0, 0, 0))]
        error = subject.solve_moment_unknown(arms, [np.array((1.0, 0, 0))], [(False, True)], 5.0)[1]
        assert "passes through the centre" in error
        error = subject.solve_moment_unknown(arms, [np.array((0, 0, 1.0))], [(True, False)], 5.0)[1]
        assert "at most 2" in error


class TestSolveCentrePosition(NewFile):
    def setup_method(self):
        # 10 down at 4 to the right of the origin; A starts at the origin, 40 clockwise.
        self.points, self.forces = [np.array((4.0, 0, 0))], [np.array((0, 0, -10.0))]

    def moment(self, centre):
        return sum((p[0] - centre[0]) * f[2] - (p[2] - centre[2]) * f[0] for p, f in zip(self.points, self.forces))

    def test_along_the_arm(self):
        centre, error = subject.solve_centre_position(self.points, self.forces, np.zeros(3), -20.0, "ARM", 0)
        assert not error and np.allclose(centre, (2, 0, 0)) and math.isclose(self.moment(centre), -20)

    def test_along_r(self):
        start = np.array((0.0, 0, 3.0))  # 5 from the point, on a 3:4 line.
        centre, error = subject.solve_centre_position(self.points, self.forces, start, -20.0, "REACH", 0)
        assert not error and math.isclose(self.moment(centre), -20)
        assert np.allclose(centre, (2, 0, 1.5))  # 2.5 from the point, on the same line.

    def test_round_the_point(self):
        start = np.array((0.0, 0, 3.0))
        centre, error = subject.solve_centre_position(self.points, self.forces, start, -30.0, "SWING", 0)
        assert not error and math.isclose(self.moment(centre), -30)
        assert math.isclose(math.hypot(centre[0] - 4, centre[2]), 5)  # r kept.
        assert centre[2] > 0  # The nearer of the two places, above as it started.

    def test_several_forces(self):
        self.points.append(np.array((-2.0, 0, 0)))
        self.forces.append(np.array((0, 0, -5.0)))
        centre, error = subject.solve_centre_position(self.points, self.forces, np.zeros(3), 0.0, "ARM", 0)
        assert not error and math.isclose(self.moment(centre), 0, abs_tol=1e-9)  # Their balance point.

    def test_no_place_serves(self):
        start = np.array((0.0, 0, 3.0))
        error = subject.solve_centre_position(self.points, self.forces, start, -100.0, "SWING", 0)[1]
        assert "No angle of r" in error
        error = subject.solve_centre_position(self.points, self.forces, self.points[0], -5.0, "REACH", 0)[1]
        assert "no direction" in error


class TestSolveForcePoint(NewFile):
    def test_where_a_force_balances_another(self):
        # 8 down at 1 to the left of A; 7 down to the right balances it at 8/7.
        points = [np.array((-1.0, 0, 0)), np.array((0.5, 0, 0))]
        forces = [np.array((0, 0, -8.0)), np.array((0, 0, -7.0))]
        point, error = subject.solve_force_point(points, forces, np.zeros(3), 0.0, 1)
        assert not error and np.allclose(point, (8 / 7, 0, 0))

    def test_its_height_kept(self):
        points, forces = [np.array((2.0, 0, 3.0))], [np.array((4.0, 0, -10.0))]
        point, error = subject.solve_force_point(points, forces, np.zeros(3), -50.0, 0)
        # -10 x - 4 * 3 = -50, so x = 3.8, at the same height.
        assert not error and np.allclose(point, (3.8, 0, 3.0))

    def test_a_force_along_x(self):
        points, forces = [np.array((2.0, 0, 3.0))], [np.array((4.0, 0, 0))]
        assert "runs along X" in subject.solve_force_point(points, forces, np.zeros(3), 5.0, 0)[1]

    def test_along_z(self):
        # 6 to the right at 2 above A makes -12; moved to make -30, it acts at 5 above.
        points, forces = [np.array((1.0, 0, 2.0))], [np.array((6.0, 0, 0))]
        point, error = subject.solve_force_point(points, forces, np.zeros(3), -30.0, 0, "Z")
        assert not error and np.allclose(point, (1, 0, 5))
        error = subject.solve_force_point([np.array((1.0, 0, 2.0))], [np.array((0, 0, -6.0))], np.zeros(3), 5.0, 0, "Z")
        assert "runs along Z" in error[1]

    def test_along_the_line_from_the_centre(self):
        # 10 down at (3, 4): -30; along its line from the centre to make -60, at twice the distance.
        points, forces = [np.array((3.0, 0, 4.0))], [np.array((0, 0, -10.0))]
        point, error = subject.solve_force_point(points, forces, np.zeros(3), -60.0, 0, "REACH")
        assert not error and np.allclose(point, (6, 0, 8))

    def test_round_the_centre(self):
        # 10 down at 5 from the centre makes at most 50; -30 at x = 3, nearer where it started above.
        points, forces = [np.array((3.0, 0, 4.0))], [np.array((0, 0, -10.0))]
        point, error = subject.solve_force_point(points, forces, np.zeros(3), -40.0, 0, "SWING")
        assert not error and np.allclose(point, (4, 0, 3)) and math.isclose(math.hypot(point[0], point[2]), 5)
        assert "No angle" in subject.solve_force_point(points, forces, np.zeros(3), -60.0, 0, "SWING")[1]
