# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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

from collections import Counter

import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit
import ifcopenshell.util.alignment
import ifcopenshell.util.element

COORDINATES = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
RADII = [1000.0, 1250.0, 950.0]
VPOINTS = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
LENGTHS = [1600.0, 1200.0, 2000.0, 800.0]


def _new_file():
    file = ifcopenshell.file(schema="IFC4X3")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )
    return file


def _new_file_no_context():
    file = ifcopenshell.file(schema="IFC4X3")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    return file


def _build_alignment(file, start_station=0.0):
    return ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", COORDINATES, RADII, VPOINTS, LENGTHS, start_station
    )


def _pset_station(referent):
    return ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="Station")


def _label(name):
    return name.rsplit("(", 1)[1].rstrip(")")


def test_wrong_layout_type_raises_type_error():
    file = _new_file()
    alignment = _build_alignment(file)
    with pytest.raises(TypeError):
        ifcopenshell.api.alignment.update_key_point_referents(file, alignment)


def test_default_rel_nests_created_when_none_provided():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)

    assert nest.is_a("IfcRelNests")
    assert nest.RelatingObject == alignment
    assert nest.id() != segment_nest.id()
    assert len(nest.RelatedObjects) == 8
    assert all(r.is_a("IfcReferent") for r in nest.RelatedObjects)


def test_second_call_without_rel_nests_creates_separate_nest():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment_count_before = len(ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal).RelatedObjects)

    nest1 = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    nest2 = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)

    assert nest1.id() != nest2.id()
    assert len(nest1.RelatedObjects) == 8
    assert len(nest2.RelatedObjects) == 8
    segment_count_after = len(ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal).RelatedObjects)
    assert segment_count_after == segment_count_before


def test_passing_previous_nest_back_in_accumulates():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    nest1 = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    nest2 = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal, rel_nests=nest1)

    assert nest1.id() == nest2.id()
    assert len(nest2.RelatedObjects) == 16


def test_provided_rel_nests_is_used_as_is():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    # rel_nests.RelatingObject must be the IfcAlignment that nests `layout`
    rel_nests = file.createIfcRelNests(GlobalId=ifcopenshell.guid.new(), RelatingObject=alignment, RelatedObjects=())

    result = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal, rel_nests=rel_nests)

    assert result.id() == rel_nests.id()
    assert result.RelatingObject == alignment
    assert len(result.RelatedObjects) == 8


def test_provided_rel_nests_with_wrong_relating_object_raises_type_error():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    rel_nests = file.createIfcRelNests(GlobalId=ifcopenshell.guid.new(), RelatingObject=horizontal, RelatedObjects=())

    with pytest.raises(TypeError):
        ifcopenshell.api.alignment.update_key_point_referents(file, horizontal, rel_nests=rel_nests)


def test_clear_true_removes_old_referents_and_psets():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    old_referent_ids = [r.id() for r in nest.RelatedObjects]
    old_pset_ids = [r.IsDefinedBy[0].RelatingPropertyDefinition.id() for r in nest.RelatedObjects]

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal, rel_nests=nest, clear=True)

    assert len(nest.RelatedObjects) == 8
    for old_id in old_referent_ids + old_pset_ids:
        with pytest.raises(RuntimeError):
            file.by_id(old_id)


def test_clear_false_appends_without_dedup():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    ifcopenshell.api.alignment.update_key_point_referents(file, horizontal, rel_nests=nest, clear=False)

    assert len(nest.RelatedObjects) == 16
    counts = Counter(r.Name for r in nest.RelatedObjects)
    assert len(counts) == 8
    assert all(count == 2 for count in counts.values())


def test_default_horizontal_labels_and_order():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)

    expected = ["P.O.B.", "P.C.", "P.T.", "P.C.", "P.T.", "P.C.", "P.T.", "P.O.E."]
    assert [_label(r.Name) for r in nest.RelatedObjects] == expected

    stations = [_pset_station(r) for r in nest.RelatedObjects]
    assert stations == sorted(stations)
    assert stations[0] == 0.0


def test_default_vertical_labels_and_order():
    file = _new_file()
    alignment = _build_alignment(file)
    vertical = ifcopenshell.api.alignment.get_vertical_layout(alignment)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, vertical)

    expected = [
        "V.P.O.B.",
        "P.V.C.",
        "P.V.T.",
        "P.V.C.",
        "P.V.T.",
        "P.V.C.",
        "P.V.T.",
        "P.V.C.",
        "P.V.T.",
        "V.P.O.E.",
    ]
    assert [_label(r.Name) for r in nest.RelatedObjects] == expected

    segments = ifcopenshell.api.alignment.get_layout_segments(vertical)
    real_segments = segments[:-1] if ifcopenshell.api.alignment.has_zero_length_segment(vertical) else segments
    # spot check the interior referents' stations against the segments' StartDistAlong directly
    for referent, segment in zip(nest.RelatedObjects[1:-1], real_segments[1:]):
        assert _pset_station(referent) == pytest.approx(segment.DesignParameters.StartDistAlong)


def test_name_format():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    referent = nest.RelatedObjects[0]
    station = _pset_station(referent)
    assert referent.Name == f"{alignment.Name} {ifcopenshell.util.alignment.station_as_string(file, station)} (P.O.B.)"


def test_geometric_placement_when_layout_has_representation():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    curve = ifcopenshell.api.alignment.get_layout_curve(horizontal)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)

    for referent in nest.RelatedObjects:
        assert referent.ObjectPlacement.is_a("IfcLinearPlacement")
        location = referent.ObjectPlacement.RelativePlacement.Location
        assert location.is_a("IfcPointByDistanceExpression")
        assert location.BasisCurve == curve
        assert referent.ObjectPlacement.CartesianPosition is not None

    first, last = nest.RelatedObjects[0], nest.RelatedObjects[-1]
    assert first.ObjectPlacement.RelativePlacement.Location.DistanceAlong.wrappedValue == pytest.approx(0.0)
    assert last.ObjectPlacement.RelativePlacement.Location.DistanceAlong.wrappedValue == pytest.approx(
        _pset_station(last)
    )


def test_fallback_placement_when_layout_has_no_geometry():
    file = _new_file_no_context()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_geometry=False)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(file, horizontal, COORDINATES, RADII)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)

    expected_coordinates = alignment.ObjectPlacement.RelativePlacement.Location.Coordinates
    for referent in nest.RelatedObjects:
        assert referent.ObjectPlacement.is_a("IfcLocalPlacement")
        assert referent.ObjectPlacement.RelativePlacement.Location.Coordinates == expected_coordinates


def test_cant_layout_boundary_labels():
    file = _new_file_no_context()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_cant=True, include_geometry=False)
    cant = ifcopenshell.api.alignment.get_cant_layout(alignment)

    dp1 = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, cant, dp1)

    dp2 = file.createIfcAlignmentCantSegment(
        StartDistAlong=100.0,
        HorizontalLength=50.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, cant, dp2)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, cant)

    labels = [_label(r.Name) for r in nest.RelatedObjects]
    assert labels[0] == "C.P.O.B."
    assert labels[-1] == "C.P.O.E."
    # CONSTANTCANT -> CONSTANTCANT is currently an unfilled "xx" placeholder in the cant lookup
    # table (_get_segment_start_point_label.py) -- out of scope to fill in here.
    assert labels[1] == "xx"

    stations = [_pset_station(r) for r in nest.RelatedObjects]
    assert stations == [0.0, 100.0, 150.0]


def test_no_real_segments_produces_no_referents():
    file = _new_file_no_context()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_geometry=False)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    assert nest.RelatedObjects == ()


def test_single_real_segment_produces_only_boundary_labels():
    file = _new_file_no_context()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_geometry=False)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartTag=None,
        EndTag=None,
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, horizontal, design_parameters)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    labels = [_label(r.Name) for r in nest.RelatedObjects]
    assert labels == ["P.O.B.", "P.O.E."]


def test_start_station_composes_for_child_alignment():
    file = _new_file()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_vertical=False, start_station=100.0)
    ifcopenshell.api.alignment.add_vertical_layout(file, alignment)
    ifcopenshell.api.alignment.add_vertical_layout(file, alignment)  # forces the child-alignment split

    child_alignment = alignment.IsDecomposedBy[0].RelatedObjects[-1]
    child_vertical = ifcopenshell.api.alignment.get_vertical_layout(child_alignment)

    dp1 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=500.0,
        StartHeight=10.0,
        StartGradient=0.01,
        EndGradient=0.01,
        PredefinedType="CONSTANTGRADIENT",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, child_vertical, dp1)

    dp2 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=500.0,
        HorizontalLength=300.0,
        StartHeight=15.0,
        StartGradient=0.01,
        EndGradient=0.01,
        PredefinedType="CONSTANTGRADIENT",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, child_vertical, dp2)

    nest = ifcopenshell.api.alignment.update_key_point_referents(file, child_vertical)
    stations = [_pset_station(r) for r in nest.RelatedObjects]
    assert stations == pytest.approx([100.0, 600.0, 900.0])


def test_rel_nests_from_ancestor_used_for_naming_and_nesting():
    """A vertical layout living under a child alignment (once a second vertical layout is
    added, per CT 4.1.4.4.1.2) can still have its key-point referents named after and nested
    to an ancestor alignment's own rel_nests -- e.g. the same one already holding that
    ancestor's horizontal key points -- rather than the child's generic "Child of X" name."""
    file = _new_file()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_vertical=False, start_station=100.0)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    horizontal_nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    horizontal_count = len(horizontal_nest.RelatedObjects)

    ifcopenshell.api.alignment.add_vertical_layout(file, alignment)
    ifcopenshell.api.alignment.add_vertical_layout(file, alignment)  # forces the child-alignment split
    child_alignment = alignment.IsDecomposedBy[0].RelatedObjects[-1]
    child_vertical = ifcopenshell.api.alignment.get_vertical_layout(child_alignment)

    dp = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=500.0,
        StartHeight=10.0,
        StartGradient=0.01,
        EndGradient=0.01,
        PredefinedType="CONSTANTGRADIENT",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, child_vertical, dp)

    result = ifcopenshell.api.alignment.update_key_point_referents(file, child_vertical, rel_nests=horizontal_nest)

    assert result == horizontal_nest
    assert result.RelatingObject == alignment
    assert len(result.RelatedObjects) == horizontal_count + 2
    assert all(r.Name.startswith("A1 ") for r in result.RelatedObjects)
    assert not any("Child of" in r.Name for r in result.RelatedObjects)


def test_returns_ifc_rel_nests():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    result = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    assert result.is_a("IfcRelNests")


test_wrong_layout_type_raises_type_error()
test_default_rel_nests_created_when_none_provided()
test_second_call_without_rel_nests_creates_separate_nest()
test_passing_previous_nest_back_in_accumulates()
test_provided_rel_nests_is_used_as_is()
test_provided_rel_nests_with_wrong_relating_object_raises_type_error()
test_clear_true_removes_old_referents_and_psets()
test_clear_false_appends_without_dedup()
test_default_horizontal_labels_and_order()
test_default_vertical_labels_and_order()
test_name_format()
test_geometric_placement_when_layout_has_representation()
test_fallback_placement_when_layout_has_no_geometry()
test_cant_layout_boundary_labels()
test_no_real_segments_produces_no_referents()
test_single_real_segment_produces_only_boundary_labels()
test_start_station_composes_for_child_alignment()
test_rel_nests_from_ancestor_used_for_naming_and_nesting()
test_returns_ifc_rel_nests()
