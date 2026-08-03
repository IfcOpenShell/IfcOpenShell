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

from typing import Optional

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.pset
import ifcopenshell.guid
import ifcopenshell.util.alignment
import ifcopenshell.util.element
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._get_segment_start_point_label import (
    _get_segment_start_point_label,
)
from ifcopenshell.api.alignment._sort_nest import _sort_nest
from ifcopenshell.api.alignment.update_fallback_position import update_fallback_position


def _get_key_point_referent_nest(layout: entity_instance) -> Optional[entity_instance]:
    """
    Searches layout.IsNestedBy for the IfcRelNests whose RelatedObjects are IfcReferent.

    This is distinct from both get_stationing_nest (scoped to the parent IfcAlignment, and
    specifically the STATION/station-equation nest) and get_alignment_segment_nest (the *segment*
    nest that also lives on layout.IsNestedBy, holding IfcAlignmentSegment, never IfcReferent).
    """
    for nest in layout.IsNestedBy:
        for related_object in nest.RelatedObjects:
            if related_object.is_a("IfcReferent"):
                return nest
    return None


def _remove_referent(file: ifcopenshell.file, referent: entity_instance) -> None:
    """Cleanly deletes a key-point IfcReferent: its Pset_Stationing, its ObjectPlacement (if
    exclusively owned by it), and finally the referent itself."""
    for inverse in list(file.get_inverse(referent)):
        if inverse.is_a("IfcRelDefinesByProperties"):
            ifcopenshell.api.pset.remove_pset(file, product=referent, pset=inverse.RelatingPropertyDefinition)

    object_placement = referent.ObjectPlacement
    if object_placement and file.get_total_inverses(object_placement) == 1:
        referent.ObjectPlacement = None
        ifcopenshell.util.element.remove_deep2(file, object_placement)

    file.remove(referent)  # also strips referent out of any IfcRelNests.RelatedObjects referencing it


def _create_key_point_referent(
    file: ifcopenshell.file,
    alignment: entity_instance,
    curve: Optional[entity_instance],
    label: str,
    distance_along: float,
    station: float,
) -> entity_instance:
    if curve and curve.is_a("IfcCompositeCurve") and 0 < len(curve.Segments):
        object_placement = file.createIfcLinearPlacement(
            RelativePlacement=file.createIfcAxis2PlacementLinear(
                Location=file.createIfcPointByDistanceExpression(
                    DistanceAlong=file.createIfcLengthMeasure(distance_along),
                    OffsetLateral=None,
                    OffsetVertical=None,
                    OffsetLongitudinal=None,
                    BasisCurve=curve,
                )
            ),
        )
        update_fallback_position(file, object_placement)
    else:
        object_placement = file.createIfcLocalPlacement(
            PlacementRelTo=None,
            RelativePlacement=file.createIfcAxis2Placement2D(
                Location=file.createIfcCartesianPoint(alignment.ObjectPlacement.RelativePlacement.Location.Coordinates)
            ),
        )

    name = f"{label} ({ifcopenshell.util.alignment.station_as_string(file, station)})"

    referent = file.createIfcReferent(
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=name,
        Description=None,
        ObjectType=None,
        ObjectPlacement=object_placement,
        Representation=None,
        PredefinedType="POSITION",
    )

    pset_stationing = ifcopenshell.api.pset.add_pset(file, product=referent, name="Pset_Stationing")
    ifcopenshell.api.pset.edit_pset(file, pset=pset_stationing, properties={"Station": station})

    return referent


def update_key_point_referents(
    file: ifcopenshell.file,
    layout: entity_instance,
    rel_nests: Optional[entity_instance] = None,
    clear: bool = False,
) -> entity_instance:
    """
    Creates IfcReferent key-point markers for every segment transition in an alignment layout.

    Labels are derived from _get_segment_start_point_label (e.g. "P.C.", "P.T.", "P.O.B.",
    "P.V.C.", ...), with the station appended, e.g. "P.C. (145+98.32)". Different jurisdictions use
    different naming systems for these key points -- register_referent_name_callback() lets a
    caller override the default horizontal/vertical/cant labeling before calling this function; if
    a callback is registered, its output is used here instead of the built-in labels. Referents are
    nested to `rel_nests`, an IfcRelNests distinct from the layout's segment nest (found via
    get_alignment_segment_nest) and from the alignment's stationing nest (found via
    get_stationing_nest) -- key-point referents never belong in either of those.

    :param layout: IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant
    :param rel_nests: an existing IfcRelNests to (re)populate. May live anywhere (e.g. the parent
        IfcAlignment, the layout, or elsewhere) -- the caller decides. If omitted, an existing
        referent-nest already on `layout` is reused, or a new one is created and related to `layout`.
    :param clear: if True, deletes all IfcReferent currently in rel_nests.RelatedObjects (and their
        Pset_Stationing) before regenerating. If False (default), new referents are appended to
        whatever already exists -- no deduplication.
    :return: the IfcRelNests, with RelatedObjects sorted ascending by Pset_Stationing.Station

    Example:

    .. code:: python

        horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        nest = ifcopenshell.api.alignment.update_key_point_referents(model, horizontal)

    Example, with custom labels for a jurisdiction that doesn't use the built-in abbreviations:

    .. code:: python

        def my_horizontal_labels(prev_segment, segment):
            if prev_segment is None:
                return "Start"
            if segment is None:
                return "End"
            return "Curve Point"  # a name representative of the prev_segment -> segment transition

        ifcopenshell.api.alignment.register_referent_name_callback(horizontal=my_horizontal_labels)
        horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        nest = ifcopenshell.api.alignment.update_key_point_referents(model, horizontal)
        # nest.RelatedObjects[0].Name starts with "Start (" instead of the default "P.O.B. ("
    """

    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received {layout.is_a()}"
        )

    if rel_nests is None:
        rel_nests = _get_key_point_referent_nest(layout)
        if rel_nests is None:
            rel_nests = file.createIfcRelNests(
                GlobalId=ifcopenshell.guid.new(), RelatingObject=layout, RelatedObjects=()
            )

    if clear:
        for referent in list(rel_nests.RelatedObjects):
            _remove_referent(file, referent)
        rel_nests.RelatedObjects = ()

    segments = list(ifcopenshell.api.alignment.get_layout_segments(layout))
    if segments and ifcopenshell.api.alignment.has_zero_length_segment(layout):
        segments = segments[:-1]

    if not segments:
        _sort_nest(
            rel_nests, key=lambda x: ifcopenshell.util.element.get_pset(x, name="Pset_Stationing", prop="Station")
        )
        return rel_nests

    alignment = ifcopenshell.api.alignment.get_alignment(layout)
    start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment)
    curve = ifcopenshell.api.alignment.get_layout_curve(layout)
    is_horizontal = layout.is_a("IfcAlignmentHorizontal")

    new_referents = []
    distance_along = 0.0
    prev_segment = None
    for segment in segments:
        dp = segment.DesignParameters
        seg_distance_along = distance_along if is_horizontal else dp.StartDistAlong

        label = _get_segment_start_point_label(prev_segment, segment)
        station = start_station + seg_distance_along
        new_referents.append(_create_key_point_referent(file, alignment, curve, label, seg_distance_along, station))

        if is_horizontal:
            distance_along += dp.SegmentLength
        else:
            distance_along = dp.StartDistAlong + dp.HorizontalLength

        prev_segment = segment

    label = _get_segment_start_point_label(prev_segment, None)
    station = start_station + distance_along
    new_referents.append(_create_key_point_referent(file, alignment, curve, label, distance_along, station))

    rel_nests.RelatedObjects = tuple(rel_nests.RelatedObjects) + tuple(new_referents)
    _sort_nest(rel_nests, key=lambda x: ifcopenshell.util.element.get_pset(x, name="Pset_Stationing", prop="Station"))

    return rel_nests
