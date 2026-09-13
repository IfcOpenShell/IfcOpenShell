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
import ifcopenshell.util.shape
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
    def create_alignment(cls, name: str, start_station: float = 0.0) -> "ifcopenshell.entity_instance":
        """Create a full IfcAlignment with horizontal layout via the alignment API.

        Creates the complete IFC structure: IfcAlignment, IfcAlignmentHorizontal,
        stationing referent, geometric representation, and zero-length terminal.
        Also creates the Blender object for the alignment itself — but not for
        its (still segment-less) horizontal layout: create_hierarchy_for_alignment()
        would create that eagerly, leaving a stray "Layout" object with no
        segments in the scene before anything has actually been drawn, unlike
        a loaded file which never has one until it's meaningful. The
        Alignments tab's draw tool creates the layout object lazily, once
        there's something to show.

        Args:
            name: The alignment name
            start_station: Starting station value (default 0.0)

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

        # Stationing referent (required by the segment-creation API), using
        # the upstream "<alignment name> <station>" naming convention.
        start_station = 0.0
        station_string = ifcopenshell.util.alignment.station_as_string(ifc_file, start_station)
        referent_name = f"{alignment.Name or 'Alignment'} {station_string}"
        align_api.add_stationing_referent(ifc_file, referent_name, alignment, 0.0, start_station)

        # Zero-length terminal segment (semantic + geometric)
        _add_zero_length_segment(ifc_file, h_layout)

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
        if obj is not None and obj.type == "MESH":
            tool.Geometry.reload_representation(obj)
            return obj

        # No object yet, or it's a bare Empty from before any geometry
        # existed (Object.type can't be changed in place) — replace it.
        if obj is not None:
            cls._remove_blender_object(obj)

        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        ifc_importer = bonsai.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()

        tool.Loader.load_settings()
        geometry = tool.Loader.create_generic_shape(alignment)
        if geometry is None:
            return None

        mesh = ifc_importer.create_mesh(alignment, geometry)
        if mesh is not None:
            # Without this, the mesh has no record of which IfcRepresentation
            # it came from, so a later reload_representation() (the branch
            # above, once this object already exists) silently finds nothing
            # to update — the IFC segments are correct (the segment listing
            # panel reads them directly) but the viewport mesh never changes.
            tool.Loader.link_mesh(geometry, mesh)
        name = f"IfcAlignment/{alignment.Name or 'Unnamed'}"
        new_obj = bpy.data.objects.new(name, mesh)

        if hasattr(geometry, "transformation_buffer"):
            mat = ifcopenshell.util.shape.get_shape_matrix(geometry)
        else:
            mat = np.eye(4)
        new_obj.matrix_world = tool.Loader.apply_blender_offset_to_matrix_world(new_obj, mat)
        tool.Geometry.record_object_position(new_obj)

        tool.Ifc.link(alignment, new_obj)
        tool.Collector.assign(new_obj)

        return new_obj

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
