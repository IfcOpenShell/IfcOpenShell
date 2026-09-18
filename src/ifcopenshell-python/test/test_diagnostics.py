# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

import ifcopenshell
import ifcopenshell.diagnostics
import ifcopenshell.guid
import ifcopenshell.util.placement
import pytest


def _mapped_item_without_source() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    """Reproduce issue #7170: an IfcMappedItem whose required MappingSource is unset."""
    f = ifcopenshell.file(schema="IFC4")
    item = f.create_entity("IfcMappedItem")
    item.MappingTarget = f.create_entity(
        "IfcCartesianTransformationOperator3D",
        LocalOrigin=f.create_entity("IfcCartesianPoint", (0.0, 0.0, 0.0)),
    )
    return f, item


def _placement_with_null_direction() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    """Reproduce issue #5113: an IfcDirection with null DirectionRatios.

    The bad direction is created inline and never bound to a name, so a caller
    that only holds the placement can reach it only by following references,
    which is how it appears during a real file load.
    """
    f = ifcopenshell.file(schema="IFC4")
    placement = f.create_entity(
        "IfcAxis2Placement3D",
        Location=f.create_entity("IfcCartesianPoint", (0.0, 0.0, 0.0)),
        Axis=f.create_entity("IfcDirection"),
        RefDirection=f.create_entity("IfcDirection", (1.0, 0.0, 0.0)),
    )
    return f, placement


def test_mapped_item_missing_source_is_named_with_high_confidence():
    f, item = _mapped_item_without_source()
    try:
        ifcopenshell.util.placement.get_mappeditem_transformation(item)
    except Exception as e:
        report = ifcopenshell.diagnostics.diagnose(e)
    else:
        pytest.fail("expected the invalid file to raise")

    assert report.likely_cause == item
    top = report.candidates[0]
    assert top.instance == item
    assert top.confidence == "high"
    assert top.in_frame
    assert any("MappingSource" in msg for msg in top.errors)


def test_null_direction_in_caller_frame_is_named():
    f, placement = _placement_with_null_direction()
    try:
        ifcopenshell.util.placement.get_axis2placement(placement)
    except Exception as e:
        report = ifcopenshell.diagnostics.diagnose(e)
    else:
        pytest.fail("expected the invalid file to raise")

    cause = report.likely_cause
    assert cause is not None
    assert cause.is_a() == "IfcDirection"
    assert cause.DirectionRatios is None
    assert any("DirectionRatios" in msg for msg in report.candidates[0].errors)


def test_null_direction_reachable_only_by_reference_is_named_with_medium_confidence():
    f, placement = _placement_with_null_direction()
    try:
        # Only the placement is a local here. The invalid direction is reached
        # by following IfcAxis2Placement3D.Axis, so it is a referenced suspect.
        ifcopenshell.util.placement.get_axis2placement(placement)
    except Exception as e:
        report = ifcopenshell.diagnostics.diagnose(e)
    else:
        pytest.fail("expected the invalid file to raise")

    cause = report.likely_cause
    assert cause is not None
    assert cause.is_a() == "IfcDirection"
    top = report.candidates[0]
    assert top.instance == cause
    assert top.confidence == "medium"
    assert not top.in_frame


def test_valid_entities_are_not_blamed():
    f = ifcopenshell.file(schema="IFC4")
    wall = f.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new())

    def crash(element):
        raise KeyError("something unrelated to the file")

    try:
        crash(wall)
    except Exception as e:
        report = ifcopenshell.diagnostics.diagnose(e)

    # The wall is a valid entity, so it must not be reported as the cause.
    assert report.likely_cause is None
    assert report.candidates
    assert all(c.confidence == "low" for c in report.candidates)


def test_no_entities_in_traceback():
    try:
        raise ValueError("no ifc here")
    except Exception as e:
        report = ifcopenshell.diagnostics.diagnose(e)

    assert report.likely_cause is None
    assert report.candidates == []
    assert "No IFC entities" in str(report)


def test_diagnose_defaults_to_current_exception():
    f, item = _mapped_item_without_source()
    try:
        ifcopenshell.util.placement.get_mappeditem_transformation(item)
    except Exception:
        report = ifcopenshell.diagnostics.diagnose()

    assert report.likely_cause == item


if __name__ == "__main__":
    pytest.main(["-sv", __file__])
