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

# This file was generated with the assistance of an AI coding tool.

from collections.abc import Sequence
from typing import Optional

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.util.element
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._add_segment_to_curve import _add_segment_to_curve
from ifcopenshell.api.alignment._get_segment_endpoint import _get_segment_endpoint
from ifcopenshell.api.alignment._update_zero_length_segment_placement import _update_zero_length_segment_placement
from ifcopenshell.api.alignment.clear_layout_segments import _is_zero_length_segment


def _remove_design_parameters(file: ifcopenshell.file, design_parameters: entity_instance) -> None:
    start_point = getattr(design_parameters, "StartPoint", None)
    file.remove(design_parameters)
    if start_point is not None and file.get_total_inverses(start_point) == 0:
        file.remove(start_point)


def _remove_segment_representation(file: ifcopenshell.file, segment: entity_instance) -> bool:
    """Drop an IfcAlignmentSegment's own per-segment representation (see
    create_segment_representations), which points at an IfcCurveSegment about to be rebuilt.
    Returns whether it had one."""
    product = segment.Representation
    if product is None:
        return False
    segment.Representation = None
    for representation in product.Representations:
        representation.Items = ()
        if file.get_total_inverses(representation) <= 1:
            file.remove(representation)
    if file.get_total_inverses(product) == 0:
        file.remove(product)
    return True


def _remove_curve_segment(file: ifcopenshell.file, curve_segment: entity_instance) -> None:
    """Remove an IfcCurveSegment no longer used by its composite curve, with its placement and parent
    curve when nothing else uses them."""
    if file.get_total_inverses(curve_segment) > 0:
        return
    parts = [curve_segment.Placement, curve_segment.ParentCurve]
    file.remove(curve_segment)
    for part in parts:
        if part is not None and file.get_total_inverses(part) == 0:
            ifcopenshell.util.element.remove_deep2(file, part)


def update_layout_segments(
    file: ifcopenshell.file,
    layout: entity_instance,
    segments: Sequence[tuple[Optional[entity_instance], entity_instance]],
) -> list[entity_instance]:
    """
    Replaces the real (non-zero-length) segments of a layout with a new sequence, *keeping* existing
    IfcAlignmentSegment entities (and so their GlobalIds) wherever the caller says a new segment
    corresponds to an existing one.

    This is the alternative to clear_layout_segments followed by create_layout_segment for every
    segment, which gives every segment a new GlobalId even when the edit only changed a radius, a
    spiral length, or a PI position -- breaking anything that refers to a segment by identity.

    Each element of ``segments`` is ``(existing, design_parameters)``:

    - ``existing`` is an IfcAlignmentSegment already nested in ``layout`` that the new segment
      corresponds to -- it keeps its GlobalId and gets ``design_parameters`` in place of its old ones
      -- or None for a segment that's genuinely new (a new IfcAlignmentSegment is created).
    - ``design_parameters`` is a new IfcAlignmentHorizontalSegment / IfcAlignmentVerticalSegment /
      IfcAlignmentCantSegment matching the layout.

    Existing segments not referenced are removed (a deleted PI's curve, say). The segments end up
    nested in the given order, before the layout's zero-length terminator, which is kept and moved to
    the new end. The layout's representation curve (if any) is rebuilt to match: IfcCurveSegments
    carry no identity, so they are simply regenerated from the design parameters in order, on the
    same curve entity -- anything referring to the curve itself (an IfcOffsetCurveByDistances, a
    linear placement) stays attached. Per-segment representations (see
    create_segment_representations) are regenerated if the layout had them.

    :param layout: An IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant
    :param segments: The new sequence of (existing IfcAlignmentSegment or None, design parameters)
    :return: The layout's real IfcAlignmentSegments, in their new order

    Example:

    .. code:: python

        existing = ifcopenshell.api.alignment.get_layout_segments(layout)[:-1]  # without the terminator
        # same segments, a longer first one: every GlobalId is kept
        new_parameters = [...]  # an IfcAlignmentHorizontalSegment per segment
        ifcopenshell.api.alignment.update_layout_segments(model, layout, list(zip(existing, new_parameters)))
    """
    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if layout.is_a() not in expected_types:
        raise TypeError(f"Expected entity type to be one of {expected_types}, instead received {layout.is_a()}")

    current = list(ifcopenshell.api.alignment.get_layout_segments(layout) or [])
    terminator = next((s for s in current if _is_zero_length_segment(s)), None)
    real = [s for s in current if s is not terminator]
    kept = [existing for existing, _ in segments if existing is not None]
    if any(existing not in real for existing in kept):
        raise ValueError("Every existing segment given must be a real segment of this layout")
    if len({s.id() for s in kept}) != len(kept):
        raise ValueError("An existing segment can only be kept once")

    # 1. Take the curve apart first -- while the nest still describes it (get_mapped_segments is
    #    positional) -- and drop per-segment representations, which point at those curve segments.
    curve = ifcopenshell.api.alignment.get_layout_curve(layout)
    old_curve_segments = []
    had_segment_representations = False
    for segment in real:
        if curve is not None:
            try:
                old_curve_segments.extend(cs for cs in ifcopenshell.api.alignment.get_mapped_segments(segment) if cs)
            except (IndexError, AttributeError):
                pass
        had_segment_representations |= _remove_segment_representation(file, segment)
    if curve is not None and curve.Segments:
        keep_terminal = ifcopenshell.api.alignment.has_zero_length_segment(curve)
        curve.Segments = (curve.Segments[-1],) if keep_terminal else ()
    for curve_segment in old_curve_segments:
        _remove_curve_segment(file, curve_segment)

    # 2. Remove the segments that aren't kept.
    removed = [s for s in real if s not in kept]
    if removed:
        for segment in removed:
            for rel in list(segment.PositionedRelativeTo or []):
                referent = rel.RelatingPositioningElement
                if referent is not None and referent.is_a("IfcReferent"):
                    ifcopenshell.api.run("root.remove_product", file, product=referent)
        ifcopenshell.api.nest.unassign_object(file, related_objects=removed)
        for segment in removed:
            if segment.DesignParameters is not None:
                _remove_design_parameters(file, segment.DesignParameters)
            file.remove(segment)

    # 3. Kept segments get their new design parameters; new ones are created.
    ordered = []
    for existing, design_parameters in segments:
        if existing is not None:
            old = existing.DesignParameters
            existing.DesignParameters = design_parameters
            if old is not None and old != design_parameters:
                _remove_design_parameters(file, old)
            ordered.append(existing)
        else:
            segment = file.createIfcAlignmentSegment(
                GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
            )
            ifcopenshell.api.nest.assign_object(file, related_objects=[segment], relating_object=layout)
            ordered.append(segment)

    # 4. Nest them in the new order, the terminator last.
    nest = ifcopenshell.api.alignment.get_alignment_segment_nest(layout)
    if nest is not None:
        nest.RelatedObjects = tuple(ordered) + ((terminator,) if terminator is not None else ())

    # 5. Rebuild the curve from the new order, and move the terminator to the new end.
    end_point = None
    for segment in ordered:
        end_point = _get_segment_endpoint(file, segment)
        if curve is not None:
            _add_segment_to_curve(file, segment, curve)
    if terminator is not None and end_point is not None:
        _update_zero_length_segment_placement(file, terminator, end_point)

    if had_segment_representations:
        alignment = ifcopenshell.api.alignment.get_alignment(layout)
        if alignment is not None:
            ifcopenshell.api.alignment.create_segment_representations(file, alignment)

    return ordered
