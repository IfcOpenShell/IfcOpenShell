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
import ifcopenshell.util.element
from ifcopenshell import entity_instance


def _is_zero_length_segment(segment: entity_instance) -> bool:
    """Check if segment is a zero-length terminator."""
    dp = segment.DesignParameters
    if dp.is_a("IfcAlignmentHorizontalSegment"):
        return dp.SegmentLength == 0.0
    elif dp.is_a("IfcAlignmentVerticalSegment"):
        return dp.HorizontalLength == 0.0
    elif dp.is_a("IfcAlignmentCantSegment"):
        return dp.HorizontalLength == 0.0
    return False


def clear_layout_segments(file: ifcopenshell.file, layout: entity_instance) -> None:
    """
    Clear all segments from a layout while preserving the layout entity
    and zero-length terminator.

    This function removes:
    - All real (non-zero-length) IfcAlignmentSegment entities from the layout
    - Their associated IfcCurveSegment entities from the geometric representation
    - Referents positioned on the removed segments

    It preserves:
    - The layout entity (IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant)
    - The zero-length terminator segment (required by IFC spec)
    - The alignment's main stationing referent

    :param file: The IFC file
    :param layout: An IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant

    Example:

    .. code:: python

        alignment = model.by_type("IfcAlignment")[0]
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

        # Clear existing segments
        ifcopenshell.api.alignment.clear_layout_segments(model, h_layout)

        # Add new segments with updated PI positions
        ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(
            model, h_layout, new_hpoints, new_radii
        )
    """
    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if layout.is_a() not in expected_types:
        raise TypeError(f"Expected entity type to be one of {expected_types}, instead received {layout.is_a()}")

    # Get the geometric curve for this layout
    curve = ifcopenshell.api.alignment.get_layout_curve(layout)

    # Get all segments from the layout
    segments = ifcopenshell.api.alignment.get_layout_segments(layout)

    if not segments:
        return  # Nothing to clear

    # Identify segments to remove (all except zero-length terminator)
    zero_length_segment = None
    segments_to_remove = []

    for segment in segments:
        if _is_zero_length_segment(segment):
            zero_length_segment = segment
        else:
            segments_to_remove.append(segment)

    if not segments_to_remove:
        return  # Only zero-length terminator exists, nothing to clear

    # Collect curve segments to remove before removing alignment segments
    # (we need the nesting relationship to find mapped segments)
    curve_segments_to_remove = []
    for segment in segments_to_remove:
        try:
            mapped = ifcopenshell.api.alignment.get_mapped_segments(segment)
            for cs in mapped:
                if cs is not None:
                    curve_segments_to_remove.append(cs)
        except (IndexError, AttributeError):
            # Segment might not have curve representation yet
            pass

    # Remove referents positioned on segments being removed
    for segment in segments_to_remove:
        # Check for referents positioned relative to this segment
        if hasattr(segment, "PositionedRelativeTo") and segment.PositionedRelativeTo:
            for rel_pos in segment.PositionedRelativeTo:
                referent = rel_pos.RelatingPositioningElement
                if referent and referent.is_a("IfcReferent"):
                    # Remove the referent
                    ifcopenshell.api.run("root.remove_product", file, product=referent)

    # Remove segments from nesting relationship
    ifcopenshell.api.nest.unassign_object(file, related_objects=segments_to_remove)

    # Remove segment entities
    for segment in segments_to_remove:
        # Remove design parameters
        dp = segment.DesignParameters
        if dp:
            # Remove StartPoint if it exists
            if hasattr(dp, "StartPoint") and dp.StartPoint:
                file.remove(dp.StartPoint)
            file.remove(dp)

        # Remove the segment entity itself
        file.remove(segment)

    # Clear curve segments from the geometric representation
    if curve and curve.Segments:
        # Keep only the zero-length curve segment (last one)
        if ifcopenshell.api.alignment.has_zero_length_segment(curve):
            zero_length_curve_seg = curve.Segments[-1]
            # Update curve to only contain zero-length segment
            curve.Segments = (zero_length_curve_seg,)
        else:
            # No zero-length segment in curve, clear all
            curve.Segments = ()

        # Clean up removed curve segment entities
        for cs in curve_segments_to_remove:
            try:
                # Remove the curve segment's parent curve and placement
                if hasattr(cs, "ParentCurve") and cs.ParentCurve:
                    parent_curve = cs.ParentCurve
                    # Check if parent curve is used elsewhere
                    if file.get_total_inverses(parent_curve) <= 1:
                        # Remove placement if exists
                        if hasattr(parent_curve, "Position") and parent_curve.Position:
                            pos = parent_curve.Position
                            if hasattr(pos, "Location") and pos.Location:
                                if file.get_total_inverses(pos.Location) <= 1:
                                    file.remove(pos.Location)
                            if hasattr(pos, "RefDirection") and pos.RefDirection:
                                if file.get_total_inverses(pos.RefDirection) <= 1:
                                    file.remove(pos.RefDirection)
                            if file.get_total_inverses(pos) <= 1:
                                file.remove(pos)
                        file.remove(parent_curve)

                # Remove placement on curve segment
                if hasattr(cs, "Placement") and cs.Placement:
                    placement = cs.Placement
                    if hasattr(placement, "Location") and placement.Location:
                        if file.get_total_inverses(placement.Location) <= 1:
                            file.remove(placement.Location)
                    if hasattr(placement, "RefDirection") and placement.RefDirection:
                        if file.get_total_inverses(placement.RefDirection) <= 1:
                            file.remove(placement.RefDirection)
                    if file.get_total_inverses(placement) <= 1:
                        file.remove(placement)

                # Remove the curve segment itself
                file.remove(cs)
            except Exception:
                # Entity may have already been removed
                pass

    # Reset zero-length terminator to origin position
    if zero_length_segment:
        dp = zero_length_segment.DesignParameters
        if dp.is_a("IfcAlignmentHorizontalSegment"):
            # Reset StartPoint to origin
            if dp.StartPoint:
                dp.StartPoint.Coordinates = (0.0, 0.0)
            dp.StartDirection = 0.0
        elif dp.is_a("IfcAlignmentVerticalSegment"):
            dp.StartDistAlong = 0.0
            dp.StartHeight = 0.0
            dp.StartGradient = 0.0
            dp.EndGradient = 0.0
        elif dp.is_a("IfcAlignmentCantSegment"):
            dp.StartDistAlong = 0.0
            dp.StartCantLeft = 0.0
            dp.StartCantRight = 0.0

        # Update the zero-length segment's referent
        if hasattr(zero_length_segment, "PositionedRelativeTo") and zero_length_segment.PositionedRelativeTo:
            for rel_pos in zero_length_segment.PositionedRelativeTo:
                referent = rel_pos.RelatingPositioningElement
                if referent and referent.is_a("IfcReferent"):
                    # Update referent position to origin
                    if hasattr(referent, "ObjectPlacement") and referent.ObjectPlacement:
                        placement = referent.ObjectPlacement
                        if hasattr(placement, "RelativePlacement") and placement.RelativePlacement:
                            rel_place = placement.RelativePlacement
                            if hasattr(rel_place, "Location") and rel_place.Location:
                                if hasattr(rel_place.Location, "DistanceAlong"):
                                    rel_place.Location.DistanceAlong.wrappedValue = 0.0
                        if hasattr(placement, "CartesianPosition") and placement.CartesianPosition:
                            cart_pos = placement.CartesianPosition
                            if hasattr(cart_pos, "Location") and cart_pos.Location:
                                cart_pos.Location.Coordinates = (0.0, 0.0, 0.0)
