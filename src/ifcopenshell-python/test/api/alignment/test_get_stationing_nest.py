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

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.nest
import ifcopenshell.api.unit
import ifcopenshell.util.element


def _new_file():
    file = ifcopenshell.file(schema="IFC4X3")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    return file


def _add_real_segment_without_geometry(file, horizontal, design_parameters):
    # Equivalent to ifcopenshell.api.alignment.create_layout_segment(), minus the geometric
    # end-point calculation performed by _add_segment_to_layout()/_get_segment_endpoint() (which
    # requires a registered geometry mapping for the schema). include_geometry=False alignments
    # have no representation to keep in sync anyway, so this reproduces exactly what the real
    # code path does to the layout's segment nest: append the segment, then swap it in front of
    # the mandatory zero-length terminal segment.
    segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters)
    ifcopenshell.api.nest.assign_object(file, related_objects=[segment], relating_object=horizontal)
    ifcopenshell.api.nest.reorder_nesting(file, segment, -1, -1)
    return segment


def test_get_stationing_nest_returns_the_station_nest_even_after_key_point_nest_created():
    # create() establishes the stationing IfcRelNests (one IfcReferent, PredefinedType="STATION")
    # first. update_key_point_referents() then creates a second, separate IfcRelNests of
    # PredefinedType="POSITION" referents. get_stationing_nest() must keep finding the STATION
    # nest regardless of which nest happens to come first in alignment.IsNestedBy.
    file = _new_file()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_geometry=False, start_station=100.0)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )
    _add_real_segment_without_geometry(file, horizontal, design_parameters)

    station_nest_before = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    assert station_nest_before is not None
    assert all(r.PredefinedType == "STATION" for r in station_nest_before.RelatedObjects)

    key_point_nest = ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)
    assert all(r.PredefinedType == "POSITION" for r in key_point_nest.RelatedObjects)
    assert key_point_nest.id() != station_nest_before.id()

    station_nest_after = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    assert station_nest_after is not None
    assert station_nest_after.id() == station_nest_before.id()
    assert all(r.PredefinedType == "STATION" for r in station_nest_after.RelatedObjects)
    assert (
        ifcopenshell.util.element.get_pset(station_nest_after.RelatedObjects[0], name="Pset_Stationing", prop="Station")
        == 100.0
    )


def test_get_stationing_nest_returns_none_when_only_key_point_nest_exists():
    # A mixed or key-point-only nest must never be mistaken for the stationing nest.
    file = _new_file()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_geometry=False)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )
    _add_real_segment_without_geometry(file, horizontal, design_parameters)

    # remove the stationing nest that create() made, leaving only key-point referents behind
    stationing_nest = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    file.remove(stationing_nest.RelatedObjects[0])
    file.remove(stationing_nest)

    ifcopenshell.api.alignment.update_key_point_referents(file, horizontal)

    assert ifcopenshell.api.alignment.get_stationing_nest(file, alignment) is None


test_get_stationing_nest_returns_the_station_nest_even_after_key_point_nest_created()
test_get_stationing_nest_returns_none_when_only_key_point_nest_exists()
