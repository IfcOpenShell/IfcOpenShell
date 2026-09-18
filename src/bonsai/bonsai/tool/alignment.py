# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025, 2026 Michael Yoder <myoder@desertspringscivil.com>
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


"""Alignment Tool - Blender implementations for alignment visualization.

This module contains Blender-specific code for creating and managing
alignment objects in the 3D view. It bridges the core business logic
to the Blender environment.

All methods are classmethods following Bonsai's tool pattern.
"""

from __future__ import annotations
import bpy
import math
import logging
import numpy as np
import bonsai.tool as tool
import bonsai.bim.import_ifc
import ifcopenshell.api.alignment
import ifcopenshell.api.aggregate
import ifcopenshell.api.geometry
import ifcopenshell.api.nest
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.unit
from typing import TYPE_CHECKING, Optional, List, Tuple

if TYPE_CHECKING:
    import ifcopenshell


class Alignment:
    """Tool class for alignment-related Blender operations.

    Following Bonsai's tool pattern, all methods are classmethods
    that can be called without instantiation.
    """

    # =========================================================================
    # IFC API Wrappers (for core layer delegation)
    # =========================================================================

    @classmethod
    def get_horizontal_layout(cls, alignment: "ifcopenshell.entity_instance"):
        """Get the IfcAlignmentHorizontal layout from an alignment.

        Args:
            alignment: The IfcAlignment entity

        Returns:
            The IfcAlignmentHorizontal entity, or None
        """
        import ifcopenshell.api.alignment as align_api

        return align_api.get_horizontal_layout(alignment)

    @classmethod
    def create_alignment(
        cls, name: str, start_station: float = 0.0, define_stationing: bool = True
    ) -> "ifcopenshell.entity_instance":
        """Create a full IfcAlignment with horizontal layout via the alignment API.

        Creates the complete IFC structure: IfcAlignment, IfcAlignmentHorizontal,
        stationing referent (unless define_stationing is False), geometric
        representation, and zero-length terminal. Also creates the Blender
        object for the alignment itself — but not for its (still segment-less)
        horizontal layout: create_hierarchy_for_alignment() would create that
        eagerly, leaving a stray "Layout" object with no segments in the scene
        before anything has actually been drawn, unlike a loaded file which
        never has one until it's meaningful. The Alignments tab's draw tool
        creates the layout object lazily, once there's something to show.

        Args:
            name: The alignment name
            start_station: Starting station value (default 0.0), ignored
                when define_stationing is False
            define_stationing: Whether to add a start-station referent at
                all. False leaves the alignment with no stationing defined
                yet — a state this codebase already handles gracefully
                elsewhere (e.g. ALIGN_OT_set_start_station's own "no
                stationing at all yet" branch) — for a user who doesn't
                want/need stationing, or wants to define it later.

        Returns:
            The created IfcAlignment entity
        """
        import ifcopenshell.api.alignment as align_api
        import ifcopenshell.util.alignment

        ifc_file = tool.Ifc.get()
        # align_api.create() no longer takes start_station (it doesn't define
        # stationing at all — see its docstring) — add the starting referent
        # ourselves, same as add_horizontal_layout_to_alignment() does for the
        # bare/Add-Element bootstrap path below.
        alignment = align_api.create(ifc_file, name=name)
        if define_stationing:
            station_string = ifcopenshell.util.alignment.station_as_string(ifc_file, start_station)
            referent_name = f"{alignment.Name or 'Alignment'} {station_string}"
            align_api.add_stationing_referent(ifc_file, referent_name, alignment, 0.0, start_station)
        cls.create_object_for_alignment(alignment)
        return alignment

    @classmethod
    def add_horizontal_layout_to_alignment(
        cls, alignment: "ifcopenshell.entity_instance"
    ) -> "ifcopenshell.entity_instance":
        """Add an IfcAlignmentHorizontal layout to a bare IfcAlignment.

        Creates the nested horizontal layout, zero-length terminal segment,
        and geometric representation using the alignment API. Use this to
        bootstrap an alignment created via Add Element (which has no layouts).

        Args:
            alignment: A bare IfcAlignment entity with no horizontal layout.

        Returns:
            The newly created IfcAlignmentHorizontal entity.
        """
        import ifcopenshell.api.aggregate
        import ifcopenshell.api.alignment as align_api
        import ifcopenshell.api.nest
        import ifcopenshell.util.alignment
        from ifcopenshell.api.alignment._add_zero_length_segment import (
            _add_zero_length_segment,
        )
        from ifcopenshell.api.alignment._create_geometric_representation import (
            _create_geometric_representation,
        )

        ifc_file = tool.Ifc.get()

        # Mirrors align_api.create()'s sequence for an alignment entity that
        # already exists (Add Element creates the bare IfcAlignment first).

        # create() gives the alignment an origin local placement; a bare
        # Add Element entity may not have one yet.
        if alignment.ObjectPlacement is None:
            alignment.ObjectPlacement = ifc_file.createIfcLocalPlacement(
                PlacementRelTo=None,
                RelativePlacement=ifc_file.createIfcAxis2Placement2D(
                    Location=ifc_file.createIfcCartesianPoint(Coordinates=(0.0, 0.0))
                ),
            )

        # Create and nest the horizontal layout
        h_layout = ifc_file.createIfcAlignmentHorizontal(GlobalId=ifcopenshell.guid.new())
        ifcopenshell.api.nest.assign_object(ifc_file, related_objects=[h_layout], relating_object=alignment)

        # Create geometric representation (curves) for the alignment
        _create_geometric_representation(ifc_file, alignment)

        # Zero-length terminal segment (semantic + geometric) -- must come before
        # add_stationing_referent() below: add_stationing_referent() only gives the
        # referent an IfcLinearPlacement (tracking the curve) when the curve already
        # has at least one segment; otherwise it falls back to a plain IfcLocalPlacement
        # at the origin, which then never gets "restated" onto the curve later, because
        # create_representation() (called after every real draw/Apply) only does that
        # restating once, guarded by "if alignment.Representation: return" -- and
        # _create_geometric_representation() above already set alignment.Representation,
        # making that restate unreachable for good. align_api.create() (the other
        # alignment-creation path, used by the Alignments tab's own Add Alignment
        # button) avoids this by adding its zero-length segments before returning, i.e.
        # before any caller can add a stationing referent -- mirror that ordering here.
        _add_zero_length_segment(ifc_file, h_layout)

        # Stationing referent (required by the segment-creation API), using
        # the upstream "<alignment name> <station>" naming convention.
        start_station = 0.0
        station_string = ifcopenshell.util.alignment.station_as_string(ifc_file, start_station)
        referent_name = f"{alignment.Name or 'Alignment'} {station_string}"
        align_api.add_stationing_referent(ifc_file, referent_name, alignment, 0.0, start_station)

        # IFC 4.1.4.1.1 Alignment Aggregation To Project
        project = next(iter(ifc_file.by_type("IfcProject")), None)
        if project is not None:
            ifcopenshell.api.aggregate.assign_object(ifc_file, products=[alignment], relating_object=project)

        return h_layout

    @classmethod
    def clear_layout_segments(cls, layout: "ifcopenshell.entity_instance"):
        """Clear the real (non-terminator) segments from a layout.

        The alignment API's PI/PVI layout functions *append* segments and
        expose no clear/remove helper, so editing a layout (PI/PVI recalc, edit
        mode) requires removing the previous segments first. This removes both
        halves of each real segment — the geometric IfcCurveSegment in the
        layout's representation curve and the semantic IfcAlignmentSegment —
        while preserving the layout entity and its mandatory zero-length
        terminator (which the layout functions then update in place).

        NOTE: this duplicates `ifcopenshell.api.alignment.clear_layout_segments`,
        which does the same thing natively. New call sites (e.g. the segment
        table's Apply operators) should prefer the native function directly;
        this copy is kept only because the existing PI/PVI draw-tool call
        sites already depend on its exact behavior and haven't been migrated.

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal/Vertical/Cant)
        """
        import ifcopenshell.api.alignment as align_api
        import ifcopenshell.api.root
        import ifcopenshell.util.element

        ifc_file = tool.Ifc.get()

        # 1) Remove the geometric curve segments (keep the zero-length terminator).
        curve = align_api.get_layout_curve(layout)
        if curve is not None and getattr(curve, "Segments", None):
            kept_curve_segments = []
            dropped_curve_segments = []
            for curve_segment in curve.Segments:
                segment_length = curve_segment.SegmentLength
                value = float(getattr(segment_length, "wrappedValue", segment_length))
                (kept_curve_segments if abs(value) < 1e-6 else dropped_curve_segments).append(curve_segment)
            curve.Segments = kept_curve_segments
            for curve_segment in dropped_curve_segments:
                ifcopenshell.util.element.remove_deep2(ifc_file, curve_segment)

        # 2) Remove the semantic IfcAlignmentSegments (keep the terminator).
        dropped_segments = []
        for rel in getattr(layout, "IsNestedBy", []) or []:
            kept_related = []
            for segment in rel.RelatedObjects or []:
                if segment.is_a("IfcAlignmentSegment") and not cls.is_zero_length_segment(segment):
                    dropped_segments.append(segment)
                else:
                    kept_related.append(segment)
            rel.RelatedObjects = kept_related
        for segment in dropped_segments:
            ifcopenshell.api.root.remove_product(ifc_file, product=segment)

    # =========================================================================
    # Zero-Length Segment Utilities
    # =========================================================================

    @classmethod
    def is_zero_length_segment(cls, segment: "ifcopenshell.entity_instance") -> bool:
        """Check if a segment is a zero-length terminator segment.

        Zero-length segments are required by IFC to mark the end of an alignment
        but should be invisible to users in the UI.

        Args:
            segment: The IfcAlignmentSegment entity

        Returns:
            True if this is a zero-length segment
        """
        if not hasattr(segment, "DesignParameters") or not segment.DesignParameters:
            return False

        dp = segment.DesignParameters

        # Check based on segment type
        if dp.is_a("IfcAlignmentHorizontalSegment"):
            return abs(dp.SegmentLength) < 1e-6
        elif dp.is_a("IfcAlignmentVerticalSegment"):
            return abs(dp.HorizontalLength) < 1e-6
        elif dp.is_a("IfcAlignmentCantSegment"):
            return abs(dp.HorizontalLength) < 1e-6

        return False

    @classmethod
    def get_real_layout_segments(cls, layout: "ifcopenshell.entity_instance") -> list:
        """All of `layout`'s real (non-terminator) IfcAlignmentSegments, in order.

        Centralizes the "skip the mandatory zero-length terminator" filter
        (via is_zero_length_segment) that both the read-only segment panel and
        the segment-table editing feature's "populate from IFC" step need to
        agree on identically.

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal/Vertical/Cant)
        """
        segments = []
        for rel in getattr(layout, "IsNestedBy", []) or []:
            for obj in rel.RelatedObjects or []:
                if obj.is_a("IfcAlignmentSegment") and not cls.is_zero_length_segment(obj):
                    segments.append(obj)
        return segments

    # =========================================================================
    # Cant — generate from horizontal, keep curve types in sync
    # =========================================================================

    #: Cant PredefinedType for each horizontal spiral-family PredefinedType --
    #: _map_alignment_cant_segment (ifcopenshell) implements HELMERTCURVE/
    #: BLOSSCURVE/COSINECURVE/SINECURVE/VIENNESEBEND as direct 1:1 matches, so
    #: those map to themselves; CLOTHOID and CUBIC have no cant-side
    #: equivalent in the IFC schema, so both fall back to LINEARTRANSITION
    #: (a plain linear cant ramp -- the conventional real-world pairing for a
    #: clothoid transition anyway). LINE/CIRCULARARC both become CONSTANTCANT
    #: (0 on tangents, the design value on arcs). Used by both
    #: generate_cant_layout() and sync_cant_segment_types() so the two always
    #: agree on the mapping.
    CANT_TYPE_FOR_HORIZONTAL_TYPE = {
        "LINE": "CONSTANTCANT",
        "CIRCULARARC": "CONSTANTCANT",
        "CLOTHOID": "LINEARTRANSITION",
        "CUBIC": "LINEARTRANSITION",
        "HELMERTCURVE": "HELMERTCURVE",
        "BLOSSCURVE": "BLOSSCURVE",
        "COSINECURVE": "COSINECURVE",
        "SINECURVE": "SINECURVE",
        "VIENNESEBEND": "VIENNESEBEND",
    }

    @classmethod
    def has_real_vertical_segments(cls, alignment: "ifcopenshell.entity_instance") -> bool:
        """Whether ``alignment`` has any drawn vertical geometry yet, across
        all of its vertical layouts (direct, or under child alignments per
        IFC CT 4.1.4.4.1.2). Used to gate deleting the horizontal layout: per
        the user (2026-09-16), horizontal can't be deleted while a vertical
        exists (it's defined against the horizontal's distance-along range) --
        delete the vertical(s) first, or the whole alignment to start over.
        """
        return any(cls.get_real_layout_segments(v) for v in cls.get_all_vertical_layouts(alignment))

    @classmethod
    def get_all_cant_layouts(cls, alignment: "ifcopenshell.entity_instance") -> list:
        """Return all IfcAlignmentCant layouts for ``alignment``.

        Mirrors get_all_vertical_layouts(): a cant layout nests onto whichever
        alignment entity (top-level, or a child per IFC CT 4.1.4.4.1.2) also
        nests the vertical it pairs with -- get_cant_layout() (ifcopenshell)
        only ever checks one alignment's own direct IsNestedBy, so with
        multiple verticals (hence multiple children, each with its own cant
        or none) this is the only way to find all of them.
        """
        cants = []
        for rel in getattr(alignment, "IsNestedBy", []) or []:
            for obj in rel.RelatedObjects or []:
                if obj.is_a("IfcAlignmentCant"):
                    cants.append(obj)
        for child in cls.get_child_alignments(alignment):
            for rel in getattr(child, "IsNestedBy", []) or []:
                for obj in rel.RelatedObjects or []:
                    if obj.is_a("IfcAlignmentCant"):
                        cants.append(obj)
        return cants

    @classmethod
    def has_real_cant_segments(cls, alignment: "ifcopenshell.entity_instance") -> bool:
        """Whether ``alignment`` has a cant layout with real segments yet, on
        the top-level alignment or any child (see get_all_cant_layouts).

        Used to gate deleting a vertical layout the same way
        has_real_vertical_segments() gates deleting horizontal: cant is
        generated from (and station-matched to) a specific horizontal/vertical
        pair, so deleting that vertical while its cant still exists would
        leave the cant layout referencing a basis curve that's gone.
        """
        return any(cls.get_real_layout_segments(c) for c in cls.get_all_cant_layouts(alignment))

    @classmethod
    def get_or_create_cant_layout(cls, alignment: "ifcopenshell.entity_instance") -> "ifcopenshell.entity_instance":
        """The alignment's IfcAlignmentCant layout, creating one (with its
        mandatory zero-length terminator) if it doesn't have one yet.

        Mirrors the cant half of ifcopenshell.api.alignment.create() -- the
        only existing reference for constructing a fresh IfcAlignmentCant --
        rather than the fuller ifcopenshell.api.alignment.add_vertical_layout()
        pattern: cant doesn't have vertical's child-alignment-on-second-layout
        complexity (an alignment has at most one cant layout).

        Also upgrades the alignment's Axis/Curve3D representation from
        IfcGradientCurve to IfcSegmentedReferenceCurve if it isn't already
        (confirmed empirically, 2026-09-16: create_layout_segment's cant path
        -- _add_segment_to_curve -- raises TypeError otherwise, since it
        requires the alignment's curve to already be an
        IfcSegmentedReferenceCurve). _create_geometric_representation
        (ifcopenshell) only builds that wrapping when an alignment is
        created with horizontal+vertical+cant from the start (its own case
        3, IFC CT 4.1.7.1.1.3); there's no existing ifcopenshell.api.alignment
        function that performs this specific upgrade for an alignment that
        already has real horizontal+vertical geometry, which is the only
        path this project's own workflow ever takes (cant is always added
        after horizontal+vertical already exist, never all three at once).
        """
        existing = ifcopenshell.api.alignment.get_cant_layout(alignment)
        if existing:
            return existing

        from ifcopenshell.api.alignment._add_zero_length_segment import _add_zero_length_segment

        file = tool.Ifc.get()

        for representation in ifcopenshell.util.representation.get_representations_iter(alignment):
            if representation.RepresentationIdentifier == "Axis" and representation.RepresentationType == "Curve3D":
                base_curve = representation.Items[0]
                if not base_curve.is_a("IfcSegmentedReferenceCurve"):
                    segmented_reference_curve = file.createIfcSegmentedReferenceCurve(
                        Segments=[], BaseCurve=base_curve, SelfIntersect=False
                    )
                    representation.Items = (segmented_reference_curve,)
                break

        cant_layout = file.createIfcAlignmentCant(GlobalId=ifcopenshell.guid.new(), RailHeadDistance=1.0)
        ifcopenshell.api.nest.assign_object(file, related_objects=[cant_layout], relating_object=alignment)
        _add_zero_length_segment(file, cant_layout)
        return cant_layout

    @classmethod
    def build_cant_specs_from_horizontal(
        cls, h_segments: list, cant_value: float
    ) -> list[tuple[str, float, float, float, Optional[float], Optional[float]]]:
        """One cant segment spec per real horizontal segment, mirroring its
        station range and curve family (see CANT_TYPE_FOR_HORIZONTAL_TYPE).

        cant_value is the full left/right rail height difference on a curve;
        the OUTER rail (opposite the direction of turn -- positive
        StartRadiusOfCurvature is a left/CCW turn per this project's
        convention, so the outer rail is on the right) is raised by the full
        value, the inner rail stays at 0 -- rather than splitting the value
        symmetrically about the centerline, which would leave both rails
        offset from datum for no reason a caller asked for. A transition
        segment ramps between whatever the alignment's cant already is
        entering it and the adjacent arc's target left/right values, working
        out entry vs. exit by which neighbour (next or previous) is the
        CIRCULARARC.

        Only handles the tangent-spiral-arc-spiral-tangent pattern the
        PI-method solver already produces; raises ValueError for any
        horizontal segment type with no CANT_TYPE_FOR_HORIZONTAL_TYPE entry.

        :return: (predefined_type, length, start_left, start_right, end_left,
            end_right) tuples, in station order. end_left/end_right are None
            for CONSTANTCANT (matches how ALIGN_OT_apply_cant_segments already
            leaves End* unset for a non-transition row).
        """

        def _outer_left_right(radius: float) -> tuple[float, float]:
            if radius > 0.0:
                return 0.0, cant_value
            if radius < 0.0:
                return cant_value, 0.0
            return 0.0, 0.0

        specs = []
        cur_left, cur_right = 0.0, 0.0
        n = len(h_segments)
        for i, seg in enumerate(h_segments):
            dp = seg.DesignParameters
            h_type = dp.PredefinedType
            length = dp.SegmentLength or 0.0
            if length <= 0.0:
                continue
            cant_type = cls.CANT_TYPE_FOR_HORIZONTAL_TYPE.get(h_type)
            if cant_type is None:
                raise ValueError(f"Horizontal segment type {h_type!r} has no cant equivalent")

            if h_type == "LINE":
                specs.append((cant_type, length, cur_left, cur_right, None, None))
                continue

            if h_type == "CIRCULARARC":
                cur_left, cur_right = _outer_left_right(dp.StartRadiusOfCurvature or 0.0)
                specs.append((cant_type, length, cur_left, cur_right, None, None))
                continue

            # Transition segment: ramp between the current cant and whichever
            # adjacent arc this transition borders (entering it if the arc
            # comes next, leaving it if the arc came just before).
            next_dp = h_segments[i + 1].DesignParameters if i + 1 < n else None
            prev_dp = h_segments[i - 1].DesignParameters if i > 0 else None
            if next_dp is not None and next_dp.PredefinedType == "CIRCULARARC":
                target = _outer_left_right(next_dp.StartRadiusOfCurvature or 0.0)
                start_left, start_right = cur_left, cur_right
                end_left, end_right = target
            elif prev_dp is not None and prev_dp.PredefinedType == "CIRCULARARC":
                start_left, start_right = cur_left, cur_right
                end_left, end_right = 0.0, 0.0
            else:
                start_left, start_right = cur_left, cur_right
                end_left, end_right = cur_left, cur_right

            specs.append((cant_type, length, start_left, start_right, end_left, end_right))
            cur_left, cur_right = end_left, end_right

        return specs

    @classmethod
    def sync_cant_segment_types(cls, alignment: "ifcopenshell.entity_instance") -> int:
        """Keep an already-generated cant layout's curve *types* in step with
        the horizontal layout's own, after a horizontal edit (Apply Curve,
        Apply Horizontal Curves, or the raw segment table's Apply) changes
        which spiral family a transition uses -- e.g. BLOSSCURVE to
        COSINECURVE (per the user, 2026-09-16: "When editing horizontal curve
        types update the cant layout to keep them in sync").

        Matches cant segments to horizontal segments by position (the i-th
        real cant segment corresponds to the i-th real horizontal segment) --
        exactly how generate_cant_layout() built them in the first place, so
        this holds as long as neither layout's segment *count* has drifted
        independently (e.g. the raw segment table adding/removing rows on one
        side only) since the last (re)generation. Silently does nothing if
        there's no cant layout yet, or if the segment counts no longer match
        -- forcing a positional correspondence that's gone stale would silently
        retype the wrong segments, worse than leaving cant untouched until the
        user regenerates it.

        Only the PredefinedType changes here, in place -- start/end cant
        values are left exactly as they are (this is a curve-family swap, not
        a re-generation; see generate_cant_layout() for that). Returns the
        number of cant segments actually retyped.
        """
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        cant_layouts = cls.get_all_cant_layouts(alignment)
        if not h_layout or not cant_layouts:
            return 0

        h_segments = cls.get_real_layout_segments(h_layout)

        changed = 0
        for cant_layout in cant_layouts:
            cant_segments = cls.get_real_layout_segments(cant_layout)
            if len(h_segments) != len(cant_segments):
                # Horizontal is shared across every vertical/cant pairing --
                # a count mismatch here means THIS cant is stale relative to
                # the (just-changed) horizontal, not that the mapping is
                # wrong in general. Skip it, same reasoning as the module
                # docstring above.
                continue
            for h_seg, cant_seg in zip(h_segments, cant_segments):
                h_type = h_seg.DesignParameters.PredefinedType
                expected = cls.CANT_TYPE_FOR_HORIZONTAL_TYPE.get(h_type)
                if expected is None:
                    continue
                cant_dp = cant_seg.DesignParameters
                if cant_dp.PredefinedType != expected:
                    cant_dp.PredefinedType = expected
                    changed += 1

        if changed:
            file = tool.Ifc.get()
            ifcopenshell.api.alignment.create_representation(file, alignment)

        return changed

    @classmethod
    def remove_cant_layout(cls, cant_layout: "ifcopenshell.entity_instance") -> None:
        """Remove one cant layout entirely: its segments, the layout entity,
        its nesting under whichever alignment owns it, and (if present) the
        IfcSegmentedReferenceCurve wrapping that alignment's own Axis/Curve3D
        curve -- reverting that representation back to the plain
        IfcGradientCurve it wrapped (the reverse of get_or_create_cant_layout's
        own upgrade). Always safe to call regardless of how many verticals
        exist -- a cant layout only ever nests alongside the one vertical it
        pairs with, never spanning several.
        """
        file = tool.Ifc.get()
        owning_alignment = ifcopenshell.api.alignment.get_alignment(cant_layout)

        for representation in ifcopenshell.util.representation.get_representations_iter(owning_alignment):
            if representation.RepresentationIdentifier == "Axis" and representation.RepresentationType == "Curve3D":
                item = representation.Items[0]
                if item.is_a("IfcSegmentedReferenceCurve"):
                    representation.Items = (item.BaseCurve,)
                    file.remove(item)
                break

        ifcopenshell.api.nest.unassign_object(file, related_objects=[cant_layout])
        ifcopenshell.util.element.remove_deep2(file, cant_layout)

    @classmethod
    def remove_vertical_layout(cls, vertical_layout: "ifcopenshell.entity_instance") -> None:
        """Remove one vertical layout entirely: its segments, the layout
        entity, and whatever geometric representation existed only for it.
        Caller's responsibility to have already removed its cant layout
        first, if it had one (has_real_cant_segments gates this at the poll
        level -- see ALIGN_OT_remove_vertical_layout).

        Two structurally different cases, both handled here:

        - The only vertical, nested directly on the top-level alignment:
          reverts the representation back to horizontal-only (IFC CT
          4.1.7.1.1.1) -- removing the Axis/Curve3D IfcGradientCurve
          representation and renaming the FootPrint/Curve2D one back to
          Axis/Curve2D, the reverse of what _create_geometric_representation
          itself builds for its "Horizontal and Vertical" case.
        - One of several verticals (IFC CT 4.1.4.4.1.2): per
          add_vertical_layout's own docstring, every vertical beyond the
          first ends up on its own, independent child alignment (siblings,
          not nested within each other) -- so removing any one of them, once
          2+ exist, never affects the others, and the owning child alignment
          (with everything exclusively nested under it -- this vertical, its
          own Representation) is simply removed outright.
        """
        file = tool.Ifc.get()
        owning_alignment = ifcopenshell.api.alignment.get_alignment(vertical_layout)
        top_level = cls._get_top_level_alignment(owning_alignment)

        if owning_alignment.id() == top_level.id():
            for representation in list(ifcopenshell.util.representation.get_representations_iter(owning_alignment)):
                if (
                    representation.RepresentationIdentifier == "Axis"
                    and representation.RepresentationType == "Curve3D"
                ):
                    ifcopenshell.api.geometry.unassign_representation(file, owning_alignment, representation)
                    ifcopenshell.util.element.remove_deep2(file, representation)
                    break
            for representation in ifcopenshell.util.representation.get_representations_iter(owning_alignment):
                if (
                    representation.RepresentationIdentifier == "FootPrint"
                    and representation.RepresentationType == "Curve2D"
                ):
                    representation.RepresentationIdentifier = "Axis"
                    break

            ifcopenshell.api.nest.unassign_object(file, related_objects=[vertical_layout])
            ifcopenshell.util.element.remove_deep2(file, vertical_layout)
        else:
            ifcopenshell.api.aggregate.unassign_object(file, products=[owning_alignment])
            ifcopenshell.util.element.remove_deep2(file, owning_alignment)

    @classmethod
    def remove_horizontal_layout(cls, alignment: "ifcopenshell.entity_instance") -> None:
        """Remove the alignment's horizontal layout entirely -- its segments,
        the layout entity, its whole geometric representation (there's
        nothing left to represent once horizontal, the foundation every
        other layout is defined against, is gone), and its stationing
        referents (their IfcLinearPlacement references the now-gone basis
        curve). Caller's responsibility to have already removed every
        vertical (hence every cant) first -- has_real_vertical_segments
        gates this at the poll level (see ALIGN_OT_remove_horizontal_layout).

        Leaves the bare IfcAlignment entity itself in place, exactly the
        state ALIGN_OT_add_alignment produces -- ready to draw again.

        TODO once key-point referents (REQUIREMENTS.md future work) are
        generated by this project's own workflow: remove those here too, the
        same reason stationing referents already are -- their placements
        reference this same now-gone basis curve.
        """
        file = tool.Ifc.get()
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        if not h_layout:
            return

        for referent, *_ in cls.get_stationing_referents(alignment):
            referent_obj = tool.Ifc.get_object(referent)
            if referent_obj:
                bpy.data.objects.remove(referent_obj, do_unlink=True)
        stationing_nest = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
        if stationing_nest:
            for referent in list(stationing_nest.RelatedObjects):
                ifcopenshell.util.element.remove_deep2(file, referent)
            ifcopenshell.util.element.remove_deep2(file, stationing_nest)

        if alignment.Representation:
            representation = alignment.Representation
            alignment.Representation = None
            ifcopenshell.util.element.remove_deep2(file, representation)

        ifcopenshell.api.nest.unassign_object(file, related_objects=[h_layout])
        ifcopenshell.util.element.remove_deep2(file, h_layout)

        obj = tool.Ifc.get_object(alignment)
        if obj is not None and obj.type == "MESH":
            cls._remove_blender_object(obj)
            cls.create_object_for_alignment(alignment)

    # =========================================================================
    # Segment Table Editing — Validation
    # =========================================================================

    @classmethod
    def validate_horizontal_segment_rows(cls, rows) -> list[str]:
        """Checks staged HorizontalSegmentRow entries before an Apply commits
        them to IFC. Returns a list of human-readable error strings; empty
        means the rows are safe to rebuild from.

        Deliberately does NOT guard against a spiral-family row (CLOTHOID/
        CUBIC/HELMERTCURVE/BLOSSCURVE/COSINECURVE/SINECURVE) with
        start_radius == end_radius, even though that reliably crashes the
        geometry kernel ("Only finite values are allowed" -- it divides by a
        curvature-change factor that's exactly zero in that case). Per the
        user (2026-09-14): the kernel bug should be left to crash rather than
        silently avoided here, so it stays visible as a reminder to fix it at
        the source instead of being masked by a UI-side workaround.
        """
        errors = []
        if len(rows) == 0:
            errors.append("Add at least one segment before applying.")
        for i, row in enumerate(rows):
            label = f"Segment {i + 1}"
            if row.predefined_type == "UNSUPPORTED":
                errors.append(f"{label}: unsupported type ({row.original_predefined_type}) — remove or fix it.")
                continue
            if row.length <= 0.0:
                errors.append(f"{label}: length must be greater than zero.")
            if row.predefined_type == "CIRCULARARC" and row.start_radius == 0.0:
                errors.append(f"{label}: a circular arc needs a non-zero radius.")
        return errors

    @classmethod
    def validate_vertical_segment_rows(cls, rows) -> list[str]:
        """Checks staged VerticalSegmentRow entries before an Apply commits
        them to IFC. Returns a list of human-readable error strings; empty
        means the rows are safe to rebuild from."""
        errors = []
        if len(rows) == 0:
            errors.append("Add at least one segment before applying.")
        for i, row in enumerate(rows):
            label = f"Segment {i + 1}"
            if row.predefined_type == "UNSUPPORTED":
                errors.append(f"{label}: unsupported type ({row.original_predefined_type}) — remove or fix it.")
                continue
            if row.h_length <= 0.0:
                errors.append(f"{label}: length must be greater than zero.")
        return errors

    @classmethod
    def validate_cant_segment_rows(cls, rows) -> list[str]:
        """Checks staged CantSegmentRow entries before an Apply commits them
        to IFC. Returns a list of human-readable error strings; empty means
        the rows are safe to rebuild from."""
        errors = []
        if len(rows) == 0:
            errors.append("Add at least one segment before applying.")
        for i, row in enumerate(rows):
            label = f"Segment {i + 1}"
            if row.predefined_type == "UNSUPPORTED":
                errors.append(f"{label}: unsupported type ({row.original_predefined_type}) — remove or fix it.")
                continue
            if row.h_length <= 0.0:
                errors.append(f"{label}: length must be greater than zero.")
        return errors

    # =========================================================================
    # Blender Object Creation
    # =========================================================================

    @classmethod
    def create_object_for_alignment(cls, alignment: ifcopenshell.entity_instance) -> Optional[bpy.types.Object]:
        """Create a Blender object for an IFC alignment and link it properly.

        This follows Bonsai's pattern for creating Blender representations:
        1. Create a Blender Empty object
        2. Link it to the IFC element via tool.Ifc.link()
        3. Assign it to the appropriate collection via tool.Collector.assign()

        Args:
            alignment: The IFC alignment entity

        Returns:
            The created Blender object, or existing one if already linked
        """
        # Check if a Blender object already exists for this IFC element
        existing_obj = tool.Ifc.get_object(alignment)
        if existing_obj:
            return existing_obj

        # Create Blender Empty object with naming pattern "IfcClass/Name"
        name = f"IfcAlignment/{alignment.Name or 'Unnamed'}"
        obj = bpy.data.objects.new(name, None)  # None = Empty object
        obj.empty_display_type = "ARROWS"
        obj.empty_display_size = 1.0

        # Link the Blender object to the IFC element (creates bidirectional mapping)
        tool.Ifc.link(alignment, obj)

        # Assign to appropriate collection (Bonsai handles collection hierarchy)
        tool.Collector.assign(obj)

        return obj

    @classmethod
    def refresh_alignment_representation_object(
        cls, alignment: ifcopenshell.entity_instance
    ) -> Optional[bpy.types.Object]:
        """Create or refresh the single mesh object for `alignment`'s own geometry.

        `alignment` (IfcAlignment) carries its own Axis representation (the
        whole composite curve — see create_representation()), so it gets
        exactly one Blender mesh object, tessellated the same way any other
        IFC product's representation is: this is what loading an alignment
        from a file produces. It deliberately does NOT create separate
        objects for the nested IfcAlignmentHorizontal/Vertical/Cant layouts
        or their IfcAlignmentSegments, unlike create_object_for_layout /
        create_objects_for_layout_segments (still used by CSV import's
        hierarchy build), which would leave the scene collection looking
        different from a loaded file for no IFC-side reason. This one is
        for the Alignments tab's authoring workflow, which shows segments
        via ALIGN_PT_alignment_segments instead of individual viewport
        objects.

        Args:
            alignment: The IFC alignment entity, with a representation already
                created (see ifcopenshell.api.alignment.create_representation).

        Returns:
            The alignment's Blender object (existing, reloaded, or newly
            created), or None if it has no representation to build a mesh
            from yet.
        """
        obj = tool.Ifc.get_object(alignment)
        if obj is not None and obj.type != "MESH":
            # A bare Empty from before any geometry existed (Object.type
            # can't be changed in place) — replace it.
            cls._remove_blender_object(obj)
            obj = None

        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        ifc_importer = bonsai.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()

        tool.Loader.load_settings()
        geometry = tool.Loader.create_generic_shape(alignment)
        if geometry is None:
            return obj

        # Force the same "recenter mesh vertices around the first vertex, and
        # carry that as the object's own matrix_world offset" treatment
        # create_mesh() normally only applies once tool.Loader.is_point_far_away()'s
        # magnitude threshold is crossed (see that function and
        # apply_blender_offset_to_matrix_world's CARTESIAN_POINT branch). An
        # interactively-drawn alignment's own start point is exactly where its
        # object's own origin -- what a click-to-select highlight dot uses --
        # is expected to sit, regardless of whether that point happens to be
        # "far" from Blender's (0,0,0) in the far-away-detector's sense. Without
        # forcing it, a small/local-coordinate alignment (e.g. starting at
        # (0, 100)) never crosses that threshold, so the object is left at
        # identity with its geometry baked in as absolute vertex coordinates
        # instead: visibly correct in the viewport, but the object's own
        # origin stays stuck at (0, 0, 0) regardless of where the alignment
        # actually starts.
        #
        # Recomputed on *every* call, not just when the object is first
        # created (per the user, 2026-09-17: "the dot is annoying and we
        # didn't have it before" — the object-origin dot silently fell behind
        # the curve's real start after a later PI edit). The offset gets
        # baked into a persisted `cartesian_point_offset` mesh property, and
        # tool.Geometry.reload_representation()'s generic reload path (used
        # here previously) reuses that *stored* value rather than
        # recomputing it — correct for rendering (mesh verts and matrix_world
        # both still use the same, if stale, anchor consistently) but it
        # means the object's own origin stays wherever the curve's start was
        # on the last full rebuild, silently drifting from the curve as PIs
        # get edited afterward. Rebuilding the mesh fresh here every time
        # (rather than reloading) keeps the origin — and the click-to-select
        # dot — anchored to the curve's *current* start point on every Apply,
        # not just the first draw.
        inner_geometry = geometry.geometry if hasattr(geometry, "geometry") else geometry
        verts = ifcopenshell.util.shape.get_vertices(inner_geometry)
        cartesian_point_offset = verts[0] if verts.size else False

        mesh = ifc_importer.create_mesh(alignment, geometry, cartesian_point_offset=cartesian_point_offset)
        if mesh is None:
            return obj
        # Without this, the mesh has no record of which IfcRepresentation it
        # came from, so a later reload_representation() elsewhere silently
        # finds nothing to update — the IFC segments are correct (the segment
        # listing panel reads them directly) but the viewport mesh never changes.
        tool.Loader.link_mesh(geometry, mesh)

        if hasattr(geometry, "transformation_buffer"):
            mat = ifcopenshell.util.shape.get_shape_matrix(geometry)
        else:
            mat = np.eye(4)

        if obj is not None:
            old_mesh = obj.data
            obj.data = mesh
            if old_mesh and old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)
        else:
            name = f"IfcAlignment/{alignment.Name or 'Unnamed'}"
            obj = bpy.data.objects.new(name, mesh)
            tool.Ifc.link(alignment, obj)
            tool.Collector.assign(obj)

        # apply_blender_offset_to_matrix_world reads the offset back off
        # obj.data — must run after obj.data is reassigned above.
        obj.matrix_world = tool.Loader.apply_blender_offset_to_matrix_world(obj, mat)
        tool.Geometry.record_object_position(obj)

        return obj

    @classmethod
    def get_alignment_start_end_points(
        cls, alignment: ifcopenshell.entity_instance
    ) -> Tuple[List[float], List[float]]:
        """The horizontal alignment's start and end points, in local IFC coords.

        Read directly from the current segments rather than tracked
        separately: the first real segment's StartPoint is the start, and the
        mandatory zero-length terminator's StartPoint sits exactly at the
        end. Unlike an interior PI, neither point moves when a curve is
        applied at some other PI, so there's no need to track them via a
        marker object the way ALIGN_OT_apply_pi_curve's interior PI markers
        do.
        """
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        segments = list(ifcopenshell.api.alignment.get_layout_segments(h_layout)) if h_layout else []
        if not segments:
            raise ValueError(f"Alignment #{alignment.id()} has no horizontal segments yet")
        start = list(segments[0].DesignParameters.StartPoint.Coordinates)
        end = list(segments[-1].DesignParameters.StartPoint.Coordinates)
        return start, end

    @classmethod
    def get_vertical_alignment_start_end_points(
        cls, alignment: ifcopenshell.entity_instance
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """The vertical alignment's start and end (distance_along, elevation) points.

        Mirrors get_alignment_start_end_points() for the vertical layout: the
        first real segment's (StartDistAlong, StartHeight) is the start. The
        end is evaluated at the last real segment's own end — exact for both
        CONSTANTGRADIENT and PARABOLICARC, since a parabola's average
        gradient over its length is exactly (StartGradient + EndGradient) / 2.
        """
        v_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
        segments = list(ifcopenshell.api.alignment.get_layout_segments(v_layout)) if v_layout else []
        real_segments = [s for s in segments if not cls.is_zero_length_segment(s)]
        if not real_segments:
            raise ValueError(f"Alignment #{alignment.id()} has no vertical segments yet")
        first_dp = real_segments[0].DesignParameters
        start = (first_dp.StartDistAlong, first_dp.StartHeight)
        last_dp = real_segments[-1].DesignParameters
        end_dist = last_dp.StartDistAlong + last_dp.HorizontalLength
        end_elev = last_dp.StartHeight + 0.5 * (last_dp.StartGradient + last_dp.EndGradient) * last_dp.HorizontalLength
        return start, (end_dist, end_elev)

    @classmethod
    def remove_layout_and_child_layout_objects(cls, alignment: ifcopenshell.entity_instance) -> int:
        """Remove any layout/segment objects left from the old per-segment
        object pipeline (create_object_for_layout / create_objects_for_layout_segments)
        so redrawing via the Alignments tab converges on the single-mesh
        representation refresh_alignment_representation_object() produces —
        matching a loaded file — even for alignments first drawn before this
        cleanup existed.
        """
        removed = 0
        for rel in getattr(alignment, "IsNestedBy", []) or []:
            for layout in rel.RelatedObjects or []:
                if layout.is_a() not in ("IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"):
                    continue
                removed += cls.remove_layout_segment_objects(layout)
                layout_obj = tool.Ifc.get_object(layout)
                if layout_obj and cls._remove_blender_object(layout_obj):
                    removed += 1
        return removed

    @classmethod
    def create_object_for_layout(
        cls, layout_entity: ifcopenshell.entity_instance, parent_obj: Optional[bpy.types.Object] = None
    ) -> Optional[bpy.types.Object]:
        """Create a Blender object for an IFC alignment layout.

        Args:
            layout_entity: The IFC layout entity (IfcAlignmentHorizontal, etc.)
            parent_obj: The parent Blender object (IfcAlignment object)

        Returns:
            The created Blender object, or existing one if already linked
        """
        # Check if a Blender object already exists for this IFC element
        existing_obj = tool.Ifc.get_object(layout_entity)
        if existing_obj:
            return existing_obj

        # Determine the layout type from the IFC class
        ifc_class = layout_entity.is_a()
        name = f"{ifc_class}"

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = "PLAIN_AXES"
        obj.empty_display_size = 0.5

        # Link to IFC element
        tool.Ifc.link(layout_entity, obj)

        # Set parent relationship in Blender (mirrors IFC nesting)
        if parent_obj:
            obj.parent = parent_obj

        # Assign to same collection as parent (avoid "Unsorted")
        if parent_obj and parent_obj.users_collection:
            parent_obj.users_collection[0].objects.link(obj)
        else:
            tool.Collector.assign(obj)

        return obj

    @classmethod
    def _find_layout_curve(cls, layout: "ifcopenshell.entity_instance") -> Optional["ifcopenshell.entity_instance"]:
        """Return the composite/gradient/reference curve for a layout.

        Extends get_layout_curve with a fallback for horizontal-only alignments
        (e.g. "reusing horizontal" parents per IFC CT 4.1.4.4.1.2) that carry
        only a FootPrint representation rather than an Axis one.
        """
        curve = ifcopenshell.api.alignment.get_layout_curve(layout)
        if curve is not None:
            return curve

        if not layout.is_a("IfcAlignmentHorizontal"):
            return None

        alignment = ifcopenshell.api.alignment.get_alignment(layout)
        if alignment is None:
            return None

        # Try FootPrint representation on the parent alignment
        if alignment.Representation:
            for rep in alignment.Representation.Representations:
                if rep.RepresentationIdentifier == "FootPrint" and rep.Items:
                    item = rep.Items[0]
                    if item.is_a("IfcCompositeCurve"):
                        return item

        # Try BaseCurve of any child alignment's IfcGradientCurve
        for rel in alignment.IsDecomposedBy or []:
            for child in rel.RelatedObjects or []:
                child_curve = ifcopenshell.api.alignment.get_curve(child)
                if child_curve and child_curve.is_a("IfcGradientCurve"):
                    return child_curve.BaseCurve

        return None

    @classmethod
    def _map_alignment_segment_to_curve_segments(
        cls,
        segment: "ifcopenshell.entity_instance",
        layout: "ifcopenshell.entity_instance",
        curve: "ifcopenshell.entity_instance",
    ) -> tuple:
        """Map an IfcAlignmentSegment to its IfcCurveSegment(s) in the given curve.

        Mirrors the logic of ifcopenshell.api.alignment.get_mapped_segments but
        uses the caller-supplied curve so that FootPrint-derived curves work too.
        """
        def _count(seg: "ifcopenshell.entity_instance") -> int:
            dp = seg.DesignParameters
            if dp.is_a("IfcAlignmentHorizontalSegment") or dp.is_a("IfcAlignmentCantSegment"):
                return 2 if getattr(dp, "PredefinedType", None) == "HELMERTCURVE" else 1
            return 1

        index = 0
        for seg in layout.IsNestedBy[0].RelatedObjects:
            index += _count(seg)
            if seg == segment:
                break

        n = _count(segment)
        if n == 1:
            return (curve.Segments[index - 1], None)
        return (curve.Segments[index - 2], curve.Segments[index - 1])

    @classmethod
    def _create_segment_curve(
        cls, segment: "ifcopenshell.entity_instance", index: int, parent_obj: Optional[bpy.types.Object] = None
    ) -> Optional[bpy.types.Object]:
        """Create a Blender curve object for an IFC alignment segment.

        Creates actual curve geometry using IfcOpenShell's geometry engine,
        so the segment can be selected and highlighted in the viewport.

        Zero-length segments (required terminators) are skipped as they should
        be invisible to users.

        Args:
            segment: The IfcAlignmentSegment entity
            index: The segment index (for naming)
            parent_obj: The parent Blender object (layout object)

        Returns:
            The created Blender curve object, or existing one if already linked,
            or None for zero-length segments or geometry failures
        """
        # Skip zero-length segments - they are required terminators but should be invisible
        if cls.is_zero_length_segment(segment):
            return None

        # Check if a Blender object already exists for this IFC element
        existing_obj = tool.Ifc.get_object(segment)
        if existing_obj:
            return existing_obj

        # Get segment parameters for naming
        if not hasattr(segment, "DesignParameters") or not segment.DesignParameters:
            return None

        dp = segment.DesignParameters
        seg_type = getattr(dp, "PredefinedType", "UNKNOWN") or "UNKNOWN"
        name = f"Segment {index + 1} ({seg_type})"

        # Get vertices for this segment using IfcOpenShell's geometry engine
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        ifc_importer = bonsai.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()

        # Resolve the IfcCurveSegment(s) for this layout segment.
        # Use _find_layout_curve instead of get_layout_curve because horizontal-only
        # alignments (e.g. IFC CT 4.1.4.4.1.2 "reusing horizontal" parents) may only
        # have a FootPrint representation rather than an Axis one, causing the standard
        # get_layout_curve / get_mapped_segments to return None and crash.
        layout = segment.Nests[0].RelatingObject if segment.Nests else None
        if not layout:
            return None

        layout_curve = cls._find_layout_curve(layout)
        if not layout_curve:
            return None

        mapped_segments = cls._map_alignment_segment_to_curve_segments(segment, layout, layout_curve)
        tool.Loader.load_settings()
        obj = None
        for curve_segment in mapped_segments:
            if curve_segment is not None:
                geometry = tool.Loader.create_generic_shape(curve_segment)
                # Currently, there may be potentially two IfcCurveSegments, for Helmert
                mesh = ifc_importer.create_mesh(curve_segment, geometry)
                obj = bpy.data.objects.new(f"IfcAlignmentSegment/{name}", mesh)

                if geometry:
                    # create_generic_shape on a non-product entity (IfcCurveSegment) returns
                    # a raw triangulation without transformation_buffer; only ShapeElements
                    # (IfcProducts) carry the placement matrix in transformation_buffer.
                    if hasattr(geometry, "transformation_buffer"):
                        mat = ifcopenshell.util.shape.get_shape_matrix(geometry)
                    else:
                        # Vertices are already in plan-space coordinates; use identity so
                        # apply_blender_offset_to_matrix_world can apply any cartesian_point_offset
                        # that create_mesh stored (for far-away coordinate handling).
                        mat = np.eye(4)
                    obj.matrix_world = tool.Loader.apply_blender_offset_to_matrix_world(obj, mat)
                    tool.Geometry.record_object_position(obj)

                # Parent to layout object and assign to same collection
                if parent_obj:
                    obj.parent = parent_obj
                    if parent_obj.users_collection:
                        parent_obj.users_collection[0].objects.link(obj)
                    else:
                        tool.Collector.assign(obj)
                else:
                    tool.Collector.assign(obj)

        # Link the Blender object to the IfcAlignmentSegment (the IfcProduct),
        # not the IfcCurveSegment (geometry). This follows Bonsai's convention
        # of one Blender object per IfcProduct and ensures correct cleanup.
        if obj:
            tool.Ifc.link(segment, obj)

        return obj

    @classmethod
    def create_alignment_from_csv(cls, filepath: str) -> "ifcopenshell.entity_instance":
        """Create alignment(s) from a CSV file via the alignment API.

        The CSV format (see ifcopenshell.api.alignment.create_from_csv) is one
        horizontal row (X,Y,R triples) followed by any number of vertical rows
        (D,Z,L triples) — extra verticals become aggregated child alignments.
        Per IFC 4.1.5.1 alignments cannot be contained in spatial structures,
        so the imported alignment is referenced into every IfcSite instead.
        """
        import ifcopenshell.api.alignment as align_api
        import ifcopenshell.api.spatial

        ifc_file = tool.Ifc.get()
        # start_station=0.0 is required since upstream b5670c4fc (2026-08-31):
        # create_from_csv no longer adds stationing when start_station is None,
        # and the import path below materializes the referents it creates.
        alignment = align_api.create_from_csv(ifc_file, filepath, start_station=0.0)
        for site in ifc_file.by_type("IfcSite"):
            ifcopenshell.api.spatial.reference_structure(
                ifc_file, products=[alignment], relating_structure=site
            )
        return alignment

    @classmethod
    def get_child_alignments(cls, alignment: "ifcopenshell.entity_instance") -> list:
        """Return child IfcAlignments aggregated under ``alignment``.

        Per IFC CT 4.1.4.4.1.2, an alignment reusing one horizontal for
        several verticals aggregates a child IfcAlignment per extra vertical.
        Returns [] for the common single-vertical case.
        """
        children = []
        for rel in alignment.IsDecomposedBy or []:
            for related in rel.RelatedObjects:
                if related.is_a("IfcAlignment"):
                    children.append(related)
        return children

    @classmethod
    def create_child_vertical_hierarchy(
        cls,
        child_alignment: "ifcopenshell.entity_instance",
        parent_obj: bpy.types.Object,
    ) -> None:
        """Create vertical layout objects for a child alignment under the parent object.

        In the IFC CT 4.1.4.4.1.2 multiple-vertical template, each child
        IfcAlignment is only a structural wrapper around one IfcAlignmentVertical.
        We skip creating a Blender empty for the child alignment itself so that
        the scene collection stays uncluttered — only the top-level IfcAlignment
        appears there.  The vertical layout object (and its segment curves) are
        parented directly to the top-level alignment object.
        """
        for rel in getattr(child_alignment, "IsNestedBy", []) or []:
            for layout in rel.RelatedObjects or []:
                if layout.is_a("IfcAlignmentVertical"):
                    layout_obj = cls.create_object_for_layout(layout, parent_obj)
                    if layout_obj:
                        cls.create_objects_for_layout_segments(layout, layout_obj)

    @classmethod
    def _get_top_level_alignment(
        cls, alignment: "ifcopenshell.entity_instance"
    ) -> "ifcopenshell.entity_instance":
        """Walk up IfcRelAggregates to the top-level parent IfcAlignment."""
        for rel in getattr(alignment, "Decomposes", []) or []:
            parent = rel.RelatingObject
            if parent.is_a("IfcAlignment"):
                return cls._get_top_level_alignment(parent)
        return alignment

    @classmethod
    def get_all_vertical_layouts(cls, alignment: "ifcopenshell.entity_instance") -> list:
        """Return all IfcAlignmentVertical layouts for ``alignment``.

        Collects verticals nested directly under the alignment AND verticals
        nested under child alignments (IFC CT 4.1.4.4.1.2 multiple-vertical
        template).
        """
        verticals = []
        for rel in getattr(alignment, "IsNestedBy", []) or []:
            for obj in rel.RelatedObjects or []:
                if obj.is_a("IfcAlignmentVertical"):
                    verticals.append(obj)
        for child in cls.get_child_alignments(alignment):
            for rel in getattr(child, "IsNestedBy", []) or []:
                for obj in rel.RelatedObjects or []:
                    if obj.is_a("IfcAlignmentVertical"):
                        verticals.append(obj)
        return verticals

    @classmethod
    def create_object_for_referent(cls, referent: "ifcopenshell.entity_instance") -> Optional[bpy.types.Object]:
        """Create a Blender empty for one IfcReferent (get-or-create).

        Matches what loading a file does for referents (e.g. stationing
        referents from add_stationing_referent) — without this, an alignment
        built interactively has no viewport object for its referents at all,
        unlike one loaded from a file.
        """
        existing_obj = tool.Ifc.get_object(referent)
        if existing_obj:
            return existing_obj
        referent_obj = bpy.data.objects.new(tool.Loader.get_name(referent), None)
        tool.Geometry.link(referent, referent_obj)
        tool.Collector.assign(referent_obj, should_clean_users_collection=False)
        cls.sync_referent_object_placement(referent)
        return referent_obj

    @classmethod
    def create_objects_for_referents(cls, alignment: "ifcopenshell.entity_instance") -> int:
        """Create empty objects for every IfcReferent nested on ``alignment``
        that doesn't already have one.

        Returns the number of referent objects created.
        """
        count = 0
        for rel in alignment.IsNestedBy or []:
            for referent in rel.RelatedObjects:
                if referent.is_a("IfcReferent") and not tool.Ifc.get_object(referent):
                    cls.create_object_for_referent(referent)
                    count += 1
        return count

    @classmethod
    def sync_referent_object_placement(cls, referent: "ifcopenshell.entity_instance") -> None:
        """Move one IfcReferent's Blender object to match its current ObjectPlacement.

        add_stationing_referent()'s own docstring spells out why this is needed: with
        no basis curve yet (a brand-new alignment with no horizontal geometry drawn),
        a stationing referent is placed with an IfcLocalPlacement at the global origin;
        once the curve has real segments, create_representation() "restates" it onto the
        curve with a proper IfcLinearPlacement -- at the IFC level. Nothing previously
        re-read that restated placement back into the Blender object, so it stayed
        sitting at the origin forever, regardless of where the real alignment ended up.

        Resolving an IfcLinearPlacement (its Location is an IfcPointByDistanceExpression,
        not a plain IfcCartesianPoint) requires evaluating the referenced curve, which
        ifcopenshell.util.placement.get_axis2placement already does via the geometry
        kernel — the same ifcopenshell.util.placement.get_local_placement() call the
        standard IFC-import pipeline uses for any placement-only product (see
        ImportIfc.get_element_matrix). No-op if there's no Blender object for this
        referent, or if its placement still can't be resolved (e.g. still no real
        geometry -- get_axis2placement's geometry-kernel fallback then legitimately has
        nothing to evaluate).
        """
        referent_obj = tool.Ifc.get_object(referent)
        if not referent_obj or not referent.ObjectPlacement:
            return

        ifc = tool.Ifc.get()
        try:
            matrix = ifcopenshell.util.placement.get_local_placement(referent.ObjectPlacement)
        except Exception:
            return

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)
        matrix[0][3] *= unit_scale
        matrix[1][3] *= unit_scale
        matrix[2][3] *= unit_scale

        referent_obj.matrix_world = tool.Loader.apply_blender_offset_to_matrix_world(referent_obj, matrix)
        tool.Geometry.record_object_position(referent_obj)

    @classmethod
    def sync_stationing_referent_placements(cls, alignment: "ifcopenshell.entity_instance") -> None:
        """Refresh every stationing referent's Blender object position for ``alignment``.

        Call this after (re)generating real horizontal geometry (see
        sync_referent_object_placement for why) -- ALIGN_OT_draw_horizontal_alignment
        and ALIGN_OT_apply_pi_curve both do, via _generate_alignment_segments().
        """
        for referent, *_ in cls.get_stationing_referents(alignment):
            cls.sync_referent_object_placement(referent)

    # =========================================================================
    # Stationing
    # =========================================================================

    @classmethod
    def find_stationing_referent_at(
        cls, alignment: "ifcopenshell.entity_instance", distance_along: float, tol: float = 1e-6
    ) -> Optional["ifcopenshell.entity_instance"]:
        """The stationing referent at a given distance along ``alignment``, or None."""
        import ifcopenshell.api.alignment as align_api
        from ifcopenshell.api.alignment._referent_distance_along import _referent_distance_along

        nest = align_api.get_stationing_nest(tool.Ifc.get(), alignment)
        if nest is None:
            return None
        for referent in nest.RelatedObjects:
            if abs(_referent_distance_along(referent) - distance_along) < tol:
                return referent
        return None

    @classmethod
    def get_stationing_referents(
        cls, alignment: "ifcopenshell.entity_instance"
    ) -> List[Tuple["ifcopenshell.entity_instance", float, float, Optional[float], Optional[bool]]]:
        """All stationing referents on ``alignment``, sorted by distance along.

        Returns (referent, distance_along, station, incoming_station,
        has_increasing_station) tuples.
        """
        import ifcopenshell.api.alignment as align_api
        import ifcopenshell.util.element
        from ifcopenshell.api.alignment._referent_distance_along import _referent_distance_along

        nest = align_api.get_stationing_nest(tool.Ifc.get(), alignment)
        if nest is None:
            return []
        rows = []
        for referent in nest.RelatedObjects:
            rows.append(
                (
                    referent,
                    _referent_distance_along(referent),
                    ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="Station"),
                    ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="IncomingStation"),
                    ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="HasIncreasingStation"),
                )
            )
        rows.sort(key=lambda r: r[1])
        return rows

    @classmethod
    def set_stationing_referent_station(cls, referent: "ifcopenshell.entity_instance", station: float) -> None:
        """Change a stationing referent's outgoing Station value in place.

        Used to edit the alignment's start station (the referent at distance
        along 0) without removing/re-adding it. Renames the referent and its
        Blender object to match, same naming convention add_stationing_referent
        uses.
        """
        import ifcopenshell.api.pset
        import ifcopenshell.util.element

        ifc_file = tool.Ifc.get()
        pset_data = ifcopenshell.util.element.get_pset(
            referent, name="Pset_Stationing", should_inherit=False, verbose=True
        )
        if not pset_data or "id" not in pset_data:
            raise ValueError(f"Referent #{referent.id()} has no Pset_Stationing to edit")
        pset = ifc_file.by_id(pset_data["id"])
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Station": station})

        # "<Alignment name> <station>", matching add_stationing_referent()'s
        # own convention (e.g. create_alignment()'s start referent).
        alignment_name = None
        for rel in getattr(referent, "Nests", []) or []:
            if rel.RelatingObject.is_a("IfcAlignment"):
                alignment_name = rel.RelatingObject.Name
                break
        prefix = f"{alignment_name} " if alignment_name else ""
        name = f"{prefix}{cls.format_station(station)}"
        referent.Name = name
        if obj := tool.Ifc.get_object(referent):
            obj.name = tool.Loader.get_name(referent)

    @classmethod
    def create_hierarchy_for_alignment(cls, alignment: "ifcopenshell.entity_instance") -> Optional[bpy.types.Object]:
        """Create the full Blender object hierarchy for an alignment.

        Creates:
        - IfcAlignment object (root)
        - IfcAlignmentHorizontal object (child)
        - IfcAlignmentVertical object (child, if present)
        - IfcAlignmentCant object (child, if present)
        - Segment objects under each layout

        Args:
            alignment: The IFC alignment entity

        Returns:
            The root alignment Blender object
        """
        # Create the alignment object
        alignment_obj = cls.create_object_for_alignment(alignment)
        if not alignment_obj:
            return None

        # Get nested layouts via IfcRelNests
        layouts = []
        for rel in getattr(alignment, "IsNestedBy", []) or []:
            for obj in rel.RelatedObjects or []:
                if obj.is_a() in ("IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"):
                    layouts.append(obj)

        # Create Blender objects for each layout and its segments
        for layout in layouts:
            layout_obj = cls.create_object_for_layout(layout, alignment_obj)
            if layout_obj:
                cls.create_objects_for_layout_segments(layout, layout_obj)

        return alignment_obj

    @classmethod
    def create_objects_for_layout_segments(
        cls, layout: "ifcopenshell.entity_instance", layout_obj: bpy.types.Object
    ) -> List[bpy.types.Object]:
        """Create Blender curve objects for all segments in a layout.

        Each segment becomes its own selectable curve object, using IfcOpenShell's
        geometry engine to generate accurate geometry for all segment types
        (LINE, CIRCULARARC, CLOTHOID, spirals, etc.).

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal, etc.)
            layout_obj: The parent Blender object for the layout

        Returns:
            List of created Blender curve objects for each segment
        """
        result_objs = []

        # Create individual curve objects for each segment
        # Each segment is its own selectable object with actual geometry
        visible_index = 0
        for rel in getattr(layout, "IsNestedBy", []) or []:
            for segment in rel.RelatedObjects or []:
                if segment.is_a() == "IfcAlignmentSegment":
                    seg_obj = cls._create_segment_curve(segment, visible_index, layout_obj)
                    if seg_obj:
                        result_objs.append(seg_obj)
                    visible_index += 1  # Always increment for consistent numbering

        return result_objs

    @classmethod
    def format_station(cls, station: float) -> str:
        """Format a station (project units) in project stationing notation.

        Delegates to ifcopenshell.util.alignment.station_as_string, which
        derives the notation from the project LENGTHUNIT: imperial projects
        read ``100+50.00``, metric projects ``10+050.000``. Falls back to a
        plain number when no IFC file is open (e.g. dialog previews before a
        project exists).
        """
        import ifcopenshell.util.alignment

        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return f"{float(station):.2f}"
        return ifcopenshell.util.alignment.station_as_string(ifc_file, float(station))

    @classmethod
    def parse_station(cls, text: str) -> float:
        """Parse a station typed by the user into a float (project units).

        Accepts either a plain number (``"1000"``) or stationing notation —
        the inverse of format_station() — such as ``"10+00"`` (Imperial) or
        ``"1+000"`` (SI); either notation is accepted regardless of the
        project's own unit system. Falls back to a plain float parse when no
        IFC file is open (e.g. dialog previews before a project exists).

        Raises:
            ValueError: If ``text`` is neither a plain number nor valid
                stationing notation.
        """
        import ifcopenshell.util.alignment

        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return float(text)
        return ifcopenshell.util.alignment.station_from_string(ifc_file, text)

    @classmethod
    def _remove_blender_object(cls, obj: bpy.types.Object) -> bool:
        """Safely remove a Blender object and its data.

        Args:
            obj: The Blender object to remove

        Returns:
            True if removed successfully
        """
        # Unlink from IFC if linked
        try:
            tool.Ifc.unlink(obj=obj)
        except Exception:
            pass  # Object might not be linked

        # Store data reference before removing object
        data = obj.data

        # Remove the object
        bpy.data.objects.remove(obj, do_unlink=True)

        # Clean up orphan curve/mesh data
        if data and data.users == 0:
            if isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)
            elif isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)

        return True

    @classmethod
    def remove_layout_segment_objects(cls, layout: ifcopenshell.entity_instance) -> int:
        """Remove all Blender objects for segments in a layout.

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal, etc.)

        Returns:
            Number of objects removed
        """
        removed_count = 0

        for rel in getattr(layout, "IsNestedBy", []) or []:
            for segment in rel.RelatedObjects or []:
                if segment.is_a() == "IfcAlignmentSegment":
                    obj = tool.Ifc.get_object(segment)
                    if obj and cls._remove_blender_object(obj):
                        removed_count += 1

        return removed_count

    @classmethod
    def remove_alignment_hierarchy(cls, alignment: ifcopenshell.entity_instance) -> int:
        """Remove all Blender objects for an alignment and its children.

        Args:
            alignment: The IFC alignment entity

        Returns:
            Number of objects removed
        """
        removed_count = 0

        # Get nested layouts (and referents) via IfcRelNests
        for rel in getattr(alignment, "IsNestedBy", []) or []:
            for related in rel.RelatedObjects or []:
                if related.is_a() in ("IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"):
                    # Remove segment objects first
                    removed_count += cls.remove_layout_segment_objects(related)

                    # Remove layout object
                    layout_obj = tool.Ifc.get_object(related)
                    if layout_obj and cls._remove_blender_object(layout_obj):
                        removed_count += 1
                elif related.is_a("IfcReferent"):
                    referent_obj = tool.Ifc.get_object(related)
                    if referent_obj and cls._remove_blender_object(referent_obj):
                        removed_count += 1

        # Remove alignment object
        alignment_obj = tool.Ifc.get_object(alignment)
        if alignment_obj and cls._remove_blender_object(alignment_obj):
            removed_count += 1

        return removed_count

    # =========================================================================
    # Validation and Safe Wrappers
    # =========================================================================
    # These methods provide pre-validation before calling IfcOpenShell alignment
    # API functions. This prevents issues like orphan layouts (from undo/redo)
    # causing invalid IFC entities (e.g., IfcRelPositions with empty RelatedProducts).
    #
    # The key principle: validate BEFORE operations to prevent invalid data,
    # rather than cleaning up after the fact.

    @classmethod
    def validate_layout_has_parent_alignment(
        cls, layout: "ifcopenshell.entity_instance"
    ) -> Optional["ifcopenshell.entity_instance"]:
        """Check if a layout entity has a valid parent IfcAlignment.

        Orphan layouts (e.g., from undo/redo operations) can cause issues
        when the alignment API tries to create referents, as the code
        expects a parent alignment to exist.

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal, etc.)

        Returns:
            The parent IfcAlignment if found, None otherwise
        """
        import ifcopenshell.api.alignment as align_api

        return align_api.get_alignment(layout)

    @classmethod
    def safe_layout_horizontal_by_pi_method(
        cls, ifc_file: "ifcopenshell.file", layout: "ifcopenshell.entity_instance", hpoints: list, radii: list
    ) -> bool:
        """Safely add segments to a horizontal layout using PI method.

        This wrapper validates that the layout has a valid parent alignment
        before calling the IfcOpenShell API. This prevents the creation of
        invalid IfcRelPositions entities.

        Args:
            ifc_file: The IFC file
            layout: The IfcAlignmentHorizontal layout
            hpoints: List of (X, Y) coordinate pairs for PIs
            radii: List of curve radii

        Returns:
            True if successful

        Raises:
            ValueError: If layout has no parent alignment
        """
        import ifcopenshell.api.alignment as align_api

        # Validate layout has a parent alignment - this is the key check
        # that prevents orphan stationing from being created
        alignment = cls.validate_layout_has_parent_alignment(layout)
        if alignment is None:
            raise ValueError(
                f"Layout #{layout.id()} ({layout.is_a()}) has no parent IfcAlignment. "
                "This may be an orphan layout from undo/redo. "
                "Cannot add segments without a valid parent alignment."
            )

        # Now safe to call the API - stationing will be associated with alignment
        align_api.layout_horizontal_alignment_by_pi_method(ifc_file, layout, hpoints, radii)

        return True

    @classmethod
    def safe_layout_vertical_by_pi_method(
        cls, ifc_file: "ifcopenshell.file", layout: "ifcopenshell.entity_instance", vpoints: list, lengths: list
    ) -> bool:
        """Safely add segments to a vertical layout using the PI method.

        Mirrors safe_layout_horizontal_by_pi_method — validates the layout has
        a valid parent alignment before calling the IfcOpenShell API.

        Args:
            ifc_file: The IFC file
            layout: The IfcAlignmentVertical layout
            vpoints: List of (distance_along, elevation) pairs for PIs, including start/end
            lengths: Horizontal length of the parabolic curve at each interior PI (0.0 = sharp)

        Returns:
            True if successful

        Raises:
            ValueError: If layout has no parent alignment
        """
        import ifcopenshell.api.alignment as align_api

        alignment = cls.validate_layout_has_parent_alignment(layout)
        if alignment is None:
            raise ValueError(
                f"Layout #{layout.id()} ({layout.is_a()}) has no parent IfcAlignment. "
                "This may be an orphan layout from undo/redo. "
                "Cannot add segments without a valid parent alignment."
            )

        align_api.layout_vertical_alignment_by_pi_method(ifc_file, layout, vpoints, lengths)

        return True

    @classmethod
    def get_horizontal_alignment_length(cls, h_layout: "ifcopenshell.entity_instance") -> float:
        """Total plan length of a horizontal layout's real (non-zero-length) segments.

        Used to seed the vertical profile view's distance-along range before
        any vertical layout exists yet — the vertical PI drawing tool needs a
        sensible canvas width spanning the whole horizontal alignment.
        """
        import ifcopenshell.api.alignment as align_api

        total = 0.0
        for segment in align_api.get_layout_segments(h_layout) or []:
            dp = segment.DesignParameters
            if not dp:
                continue
            total += abs(getattr(dp, "SegmentLength", 0.0) or 0.0)
        return total

    @classmethod
    def get_active_alignment(cls) -> ifcopenshell.entity_instance | None:
        if obj := tool.Blender.get_active_object():
            # PI curve marker empties (see PICurveMarkerProperties) are never
            # IFC-linked — they're transient viewport helpers — so they need
            # their own lookup via the alignment_id they were tagged with,
            # rather than falling through to tool.Ifc.get_entity() below.
            # Without this, selecting a marker to press Apply Curve leaves
            # this returning None, and the Alignments tab's dropdown/segment
            # table (which sync from this) revert to "select an alignment".
            marker = obj.bonsai_pi_curve_marker
            if marker.is_pi_marker:
                ifc_file = tool.Ifc.get()
                if not ifc_file:
                    return None
                try:
                    alignment = ifc_file.by_id(marker.alignment_id)
                except RuntimeError:
                    return None
                return cls._get_top_level_alignment(alignment) if alignment.is_a("IfcAlignment") else None
            element = tool.Ifc.get_entity(obj)
            if not element:
                return None
            if element.is_a("IfcAlignment"):
                return cls._get_top_level_alignment(element)
            # Walk up: segment → layout → alignment → top-level alignment
            if element.is_a("IfcAlignmentSegment"):
                for rel in getattr(element, "Nests", []) or []:
                    layout = rel.RelatingObject
                    for rel2 in getattr(layout, "Nests", []) or []:
                        if rel2.RelatingObject.is_a("IfcAlignment"):
                            return cls._get_top_level_alignment(rel2.RelatingObject)
            if element.is_a("IfcAlignmentHorizontal") or element.is_a("IfcAlignmentVertical") or element.is_a("IfcAlignmentCant"):
                for rel in getattr(element, "Nests", []) or []:
                    if rel.RelatingObject.is_a("IfcAlignment"):
                        return cls._get_top_level_alignment(rel.RelatingObject)
        return None
