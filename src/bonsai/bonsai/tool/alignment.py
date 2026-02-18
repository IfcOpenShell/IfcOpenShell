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
import bonsai.tool as tool
import bonsai.bim.import_ifc
import ifcopenshell.api.alignment
from typing import TYPE_CHECKING, Optional, List, Tuple
from dataclasses import dataclass

if TYPE_CHECKING:
    import ifcopenshell


# =============================================================================
# Data Classes for PI Geometry Results
# =============================================================================


@dataclass
class PIGeometryResult:
    """Result of PI geometry calculation."""

    stations: List[float]
    lengths: List[float]
    directions: List[float]
    total_length: float


class Alignment:
    """Tool class for alignment-related Blender operations.

    Following Bonsai's tool pattern, all methods are classmethods
    that can be called without instantiation.
    """

    # =========================================================================
    # Geometry Calculation Methods
    # =========================================================================

    @classmethod
    def calculate_pi_geometry(
        cls, pis: List[Tuple[float, float]], start_station: float = 0.0
    ) -> PIGeometryResult:
        """Calculate lengths, stations, and directions for a list of PI points.

        Args:
            pis: List of (x, y) coordinate tuples for each PI
            start_station: Starting station value

        Returns:
            PIGeometryResult containing calculated values
        """
        if len(pis) < 2:
            return PIGeometryResult(
                stations=[start_station] if pis else [],
                lengths=[0.0] if pis else [],
                directions=[0.0] if pis else [],
                total_length=0.0,
            )

        stations = []
        lengths = []
        directions = []
        cumulative_length = start_station

        for i, pi in enumerate(pis):
            stations.append(cumulative_length)

            if i < len(pis) - 1:
                next_pi = pis[i + 1]
                dx = next_pi[0] - pi[0]
                dy = next_pi[1] - pi[1]
                length = math.sqrt(dx * dx + dy * dy)
                direction = math.atan2(dy, dx)
                lengths.append(length)
                directions.append(direction)
                cumulative_length += length
            else:
                lengths.append(0.0)
                directions.append(0.0)

        total_length = cumulative_length - start_station

        return PIGeometryResult(
            stations=stations, lengths=lengths, directions=directions, total_length=total_length
        )

    @classmethod
    def calculate_deflection_angle(cls, incoming_direction: float, outgoing_direction: float) -> float:
        """Calculate the deflection angle between two tangent directions.

        Args:
            incoming_direction: Direction angle of incoming tangent (radians)
            outgoing_direction: Direction angle of outgoing tangent (radians)

        Returns:
            Deflection angle in radians (always positive)
        """
        delta = outgoing_direction - incoming_direction
        # Normalize to -pi to pi
        while delta > math.pi:
            delta -= 2 * math.pi
        while delta < -math.pi:
            delta += 2 * math.pi
        return abs(delta)

    @classmethod
    def calculate_tangent_length(cls, radius: float, deflection_angle: float) -> float:
        """Calculate tangent length for a circular curve.

        T = R * tan(Δ/2)

        Args:
            radius: Curve radius
            deflection_angle: Deflection angle in radians

        Returns:
            Tangent length
        """
        if deflection_angle == 0 or radius == 0:
            return 0.0
        return radius * math.tan(deflection_angle / 2)

    @classmethod
    def calculate_arc_length(cls, radius: float, deflection_angle: float) -> float:
        """Calculate arc length for a circular curve.

        L = R * Δ

        Args:
            radius: Curve radius
            deflection_angle: Deflection angle in radians

        Returns:
            Arc length
        """
        return radius * deflection_angle

    @classmethod
    def calculate_bc_ec_points(
        cls,
        pi_x: float,
        pi_y: float,
        incoming_direction: float,
        outgoing_direction: float,
        tangent_length: float,
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Calculate Begin Curve (BC) and End Curve (EC) points.

        BC = PI - incoming_tangent_vector * T
        EC = PI + outgoing_tangent_vector * T

        Args:
            pi_x: PI X coordinate
            pi_y: PI Y coordinate
            incoming_direction: Direction of incoming tangent (radians)
            outgoing_direction: Direction of outgoing tangent (radians)
            tangent_length: Calculated tangent length

        Returns:
            Tuple of (BC point, EC point) as (x, y) tuples
        """
        # BC is along the incoming tangent, before the PI
        bc_x = pi_x - tangent_length * math.cos(incoming_direction)
        bc_y = pi_y - tangent_length * math.sin(incoming_direction)

        # EC is along the outgoing tangent, after the PI
        ec_x = pi_x + tangent_length * math.cos(outgoing_direction)
        ec_y = pi_y + tangent_length * math.sin(outgoing_direction)

        return ((bc_x, bc_y), (ec_x, ec_y))

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
    def layout_has_real_segments(cls, layout: "ifcopenshell.entity_instance") -> bool:
        """Check if a layout has any real (non-zero-length) segments.

        An empty layout only has the mandatory zero-length terminator segment.

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal, etc.)

        Returns:
            True if the layout has at least one real segment
        """
        for rel in getattr(layout, "IsNestedBy", []) or []:
            for segment in rel.RelatedObjects or []:
                if segment.is_a("IfcAlignmentSegment"):
                    if not cls.is_zero_length_segment(segment):
                        return True
        return False

    # =========================================================================
    # Segment Geometry Utilities
    # =========================================================================

    @classmethod
    def get_segment_vertices(
        cls, segment: "ifcopenshell.entity_instance", distance_interval: float = 1.0
    ) -> Optional[List[Tuple[float, float, float]]]:
        """Get vertices for a single alignment segment using IfcOpenShell's geometry engine.

        Uses the proven IfcOpenShell C++ geometry engine (create_shape) to generate
        vertices, supporting all segment types (LINE, CIRCULARARC, CLOTHOID,
        spirals, etc.) including negative-length curve segments.

        Args:
            segment: The IfcAlignmentSegment entity
            distance_interval: Distance between sample points (default 1.0 units)

        Returns:
            List of (x, y, z) tuples representing vertices along the segment,
            or None if geometry cannot be generated
        """
        import ifcopenshell.api.alignment as align_api
        import ifcopenshell.geom
        import ifcopenshell.util.unit
        import numpy as np

        # Skip zero-length segments
        if cls.is_zero_length_segment(segment):
            return None

        # Get the mapped curve segment(s) for this alignment segment
        try:
            mapped_segments = align_api.get_mapped_segments(segment)
        except Exception as e:
            print(f"[Alignment] get_mapped_segments failed: {e}")
            return None

        if not mapped_segments:
            return None

        # Get IFC file for unit scale
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            return None

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

        all_vertices = []

        # Process each curve segment (usually 1, but HELMERTCURVE has 2)
        for curve_segment in mapped_segments:
            if curve_segment is None:
                continue

            # Use create_shape to generate vertices - the same proven approach as generate_vertices()
            # This handles negative-length curve segments correctly at the C++ level
            try:
                s = ifcopenshell.geom.settings()

                shape = ifcopenshell.geom.create_shape(s, curve_segment)
                verts = shape.verts

                if len(verts) == 0:
                    continue

                # Reshape to (N, 3) array and apply unit scale
                vertices_array = np.array(verts).reshape((-1, 3))
                for v in vertices_array:
                    # create_shape returns values already in file units, apply scale
                    x = float(v[0]) / unit_scale
                    y = float(v[1]) / unit_scale
                    z = float(v[2]) / unit_scale
                    all_vertices.append((x, y, z))

            except Exception as e:
                print(f"[Alignment] create_shape failed for curve segment: {e}")
                continue

        if len(all_vertices) < 2:
            return None

        return all_vertices

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
    def create_curve_from_representation(
        cls,
        layout: "ifcopenshell.entity_instance",
        parent_obj: Optional[bpy.types.Object] = None,
    ) -> Optional[bpy.types.Object]:
        """Create a Blender curve from an alignment layout's IFC representation.

        Uses IfcOpenShell's geometry engine to generate vertices, supporting
        all segment types (LINE, CIRCULARARC, CLOTHOID, spirals, etc.).

        The vertices from IFC are in global/map coordinates. If a Blender offset
        is configured (for handling large geospatial coordinates), the vertices
        are transformed to Blender local coordinates.

        Empty alignments (only zero-length terminator segment) are silently skipped.

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal, etc.)
            parent_obj: The parent Blender object (alignment object)

        Returns:
            The created Blender curve object, or None if no representation or empty
        """
        import ifcopenshell.api.alignment as align_api
        from ifcopenshell.api.alignment import util as align_util
        import ifcopenshell.util.geolocation
        import ifcopenshell.util.unit

        # Skip empty layouts (only zero-length terminator) - no error message needed
        if not cls.layout_has_real_segments(layout):
            return None

        # Get the layout's curve representation
        try:
            rep_curve = align_api.get_layout_curve(layout)
        except Exception as e:
            print(f"[Alignment] get_layout_curve failed: {e}")
            rep_curve = None

        if rep_curve is None:
            return None

        # Generate vertices using IfcOpenShell's geometry engine
        vertices = align_util.generate_vertices(rep_curve, distance_interval=1.0)

        if len(vertices) < 2:
            print(f"[Alignment] Not enough vertices ({len(vertices)}), need at least 2")
            return None

        # Check if we need to apply Blender offset transformation
        # IFC vertices are in global/map coordinates, we need to convert to Blender local
        gprops = tool.Georeference.get_georeference_props()
        ifc_file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file) if ifc_file else 1.0

        if gprops.has_blender_offset:
            offset_x = float(gprops.blender_offset_x) * unit_scale
            offset_y = float(gprops.blender_offset_y) * unit_scale
            offset_z = float(gprops.blender_offset_z) * unit_scale
            x_axis_abscissa = float(gprops.blender_x_axis_abscissa)
            x_axis_ordinate = float(gprops.blender_x_axis_ordinate)

            # Transform each vertex from IFC global to Blender local
            transformed_vertices = []
            for vert in vertices:
                # Create a 4x4 identity matrix with translation set to vertex position
                import numpy as np
                matrix = np.eye(4)
                matrix[0, 3] = vert[0]
                matrix[1, 3] = vert[1]
                matrix[2, 3] = vert[2]

                # Apply global2local transformation
                local_matrix = ifcopenshell.util.geolocation.global2local(
                    matrix, offset_x, offset_y, offset_z, x_axis_abscissa, x_axis_ordinate
                )

                # Extract transformed position
                transformed_vertices.append((local_matrix[0, 3], local_matrix[1, 3], local_matrix[2, 3]))

            vertices = transformed_vertices

        # Create Blender curve from vertices
        layout_type = layout.is_a().replace("IfcAlignment", "")  # "Horizontal", "Vertical", etc.
        name = f"{layout_type}Curve"
        curve_data = bpy.data.curves.new(name, type="CURVE")
        curve_data.dimensions = "3D"

        spline = curve_data.splines.new("POLY")
        spline.points.add(len(vertices) - 1)

        for i, vert in enumerate(vertices):
            spline.points[i].co = (vert[0], vert[1], vert[2], 1.0)

        obj = bpy.data.objects.new(name, curve_data)
        obj.show_in_front = True
        curve_data.bevel_depth = 0.0

        # Set a visible color for the curve (black, like construction lines)
        obj.color = (0.0, 0.0, 0.0, 1.0)  # Black color

        # Set parent relationship
        if parent_obj:
            obj.parent = parent_obj

        # Assign to same collection as parent
        if parent_obj and parent_obj.users_collection:
            parent_obj.users_collection[0].objects.link(obj)
        else:
            tool.Collector.assign(obj)

        return obj

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

        mapped_segments = ifcopenshell.api.alignment.get_mapped_segments(segment)
        tool.Loader.load_settings()
        for curve_segment in mapped_segments:
            if curve_segment is not None:
                geometry = tool.Loader.create_generic_shape(curve_segment)
                # Currently, there may be potentially two IfcCurveSegments, for Helmert
                mesh = ifc_importer.create_mesh(curve_segment, geometry)
                obj = bpy.data.objects.new(tool.Loader.get_name(curve_segment), mesh)
                tool.Ifc.link(curve_segment, obj)
                tool.Collector.assign(obj)
        return obj

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
    def update_pi_properties(cls, props, geometry_result) -> None:
        """Update Blender PropertyGroup with calculated geometry.

        This bridges the pure Python calculation results back to
        the Blender UI properties.

        Args:
            props: The SaikeiAlignmentProperties PropertyGroup
            geometry_result: PIGeometryResult from core.alignment
        """
        pis = props.pis
        for i, pi in enumerate(pis):
            if i < len(geometry_result.stations):
                pi.station = geometry_result.stations[i]
            if i < len(geometry_result.lengths):
                pi.length_to_next = geometry_result.lengths[i]
            if i < len(geometry_result.directions):
                pi.direction_to_next = geometry_result.directions[i]

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

        # Get segments via IfcRelNests
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

        # Get nested layouts via IfcRelNests
        for rel in getattr(alignment, "IsNestedBy", []) or []:
            for layout in rel.RelatedObjects or []:
                if layout.is_a() in ("IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"):
                    # Remove segment objects first
                    removed_count += cls.remove_layout_segment_objects(layout)

                    # Remove layout object
                    layout_obj = tool.Ifc.get_object(layout)
                    if layout_obj and cls._remove_blender_object(layout_obj):
                        removed_count += 1

        # Remove alignment object
        alignment_obj = tool.Ifc.get_object(alignment)
        if alignment_obj and cls._remove_blender_object(alignment_obj):
            removed_count += 1

        return removed_count

    @classmethod
    def refresh_layout_visualization(
        cls, layout: ifcopenshell.entity_instance, layout_obj: Optional[bpy.types.Object] = None
    ) -> List[bpy.types.Object]:
        """Refresh the visualization for a layout by removing and recreating segment objects.

        Args:
            layout: The IFC layout entity
            layout_obj: Optional parent Blender object (will be looked up if not provided)

        Returns:
            List of newly created segment objects
        """
        # Get or find the layout object
        if layout_obj is None:
            layout_obj = tool.Ifc.get_object(layout)

        if layout_obj is None:
            return []

        # Remove existing segment objects
        cls.remove_layout_segment_objects(layout)

        # Create new segment objects
        return cls.create_objects_for_layout_segments(layout, layout_obj)

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
        try:
            import ifcopenshell.api.alignment as align_api

            return align_api.get_alignment(layout)
        except Exception:
            return None

    @classmethod
    def get_alignment_for_layout(
        cls, layout: "ifcopenshell.entity_instance"
    ) -> Optional["ifcopenshell.entity_instance"]:
        """Get the parent IfcAlignment for a layout entity.

        This is an alias for validate_layout_has_parent_alignment that
        makes the intent clearer when you need the alignment itself.

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal, etc.)

        Returns:
            The parent IfcAlignment if found, None otherwise
        """
        return cls.validate_layout_has_parent_alignment(layout)

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
    def safe_create_alignment_by_pi_method(
        cls, ifc_file: "ifcopenshell.file", name: str, hpoints: list, radii: list, start_station: float = 0.0
    ) -> "ifcopenshell.entity_instance":
        """Safely create a new alignment using PI method.

        When creating a new alignment, we don't need validation since
        we're creating the alignment itself - stationing will be
        properly associated with it.

        Args:
            ifc_file: The IFC file
            name: Alignment name
            hpoints: List of (X, Y) coordinate pairs for PIs
            radii: List of curve radii
            start_station: Starting station value

        Returns:
            The created IfcAlignment entity
        """
        import ifcopenshell.api.alignment as align_api

        # Create the alignment - this creates a new alignment so stationing
        # will be properly associated with it
        alignment = align_api.create_by_pi_method(
            ifc_file, name=name, hpoints=hpoints, radii=radii, start_station=start_station
        )

        return alignment

    # =========================================================================
    # PI Edit Mode Methods
    # =========================================================================
    # These methods support the PI Edit Mode feature, which allows users to
    # move alignment PIs (Points of Intersection) using Blender's standard
    # transform tools (G key). The workflow is:
    # 1. Back-calculate PI positions from existing IFC segments
    # 2. Create temporary EMPTY objects at each PI location
    # 3. User moves empties with standard Blender tools
    # 4. Collect new positions and regenerate alignment segments

    @classmethod
    def back_calculate_pis_from_alignment(
        cls, alignment: "ifcopenshell.entity_instance"
    ) -> List[dict]:
        """Reverse-engineer PI positions from IFC alignment segments.

        This function analyzes the alignment's horizontal segments and
        reconstructs the original PI (Point of Intersection) positions
        that were used to create the alignment.

        Algorithm:
        1. Get horizontal layout and segments
        2. First PI = start point of first segment
        3. For each CIRCULARARC segment:
           - Extract BC (begin curve) from StartPoint
           - Calculate deflection: Δ = arc_length / radius
           - Calculate tangent length: T = R × tan(Δ/2)
           - PI position = BC + T × direction_vector
           - Store radius
        4. For LINE-only transitions (radius=0):
           - PI = endpoint of LINE segment (becomes a tangent PI)
        5. Last PI = end point of last real segment

        Args:
            alignment: The IfcAlignment entity

        Returns:
            List of dicts, each containing:
            - "x": float - X coordinate in IFC space
            - "y": float - Y coordinate in IFC space
            - "radius": float - Curve radius (0 for endpoints/tangent PIs)
            - "type": str - "ENDPOINT", "CURVE", or "TANGENT"

        Raises:
            ValueError: If alignment has no horizontal layout or segments
        """
        import ifcopenshell.api.alignment as align_api

        # Get horizontal layout
        h_layout = align_api.get_horizontal_layout(alignment)
        if h_layout is None:
            raise ValueError(f"Alignment #{alignment.id()} has no horizontal layout")

        # Get all segments
        segments = []
        for rel in getattr(h_layout, "IsNestedBy", []) or []:
            for segment in rel.RelatedObjects or []:
                if segment.is_a("IfcAlignmentSegment"):
                    segments.append(segment)

        if not segments:
            raise ValueError(f"Alignment #{alignment.id()} has no segments")

        # Filter out zero-length terminator segments
        real_segments = []
        for seg in segments:
            if not cls.is_zero_length_segment(seg):
                real_segments.append(seg)

        if not real_segments:
            raise ValueError(f"Alignment #{alignment.id()} has no real segments (only terminator)")

        pis = []

        # First PI: start point of first segment
        first_dp = real_segments[0].DesignParameters
        first_x = float(first_dp.StartPoint.Coordinates[0])
        first_y = float(first_dp.StartPoint.Coordinates[1])
        pis.append({
            "x": first_x,
            "y": first_y,
            "radius": 0.0,
            "type": "ENDPOINT"
        })

        # Track current position and direction for LINE segments
        # This helps us identify tangent PIs (where LINE meets LINE)
        prev_seg_type = first_dp.PredefinedType

        # Process each segment
        for i, seg in enumerate(real_segments):
            dp = seg.DesignParameters
            seg_type = dp.PredefinedType

            if seg_type == "CIRCULARARC":
                # Reconstruct PI from arc segment
                bc_x = float(dp.StartPoint.Coordinates[0])
                bc_y = float(dp.StartPoint.Coordinates[1])
                angle_in = float(dp.StartDirection)
                radius = abs(float(dp.StartRadiusOfCurvature))
                arc_length = float(dp.SegmentLength)

                # Deflection angle: Δ = L / R
                deflection = arc_length / radius

                # Tangent length: T = R × tan(Δ/2)
                tangent_length = radius * math.tan(deflection / 2)

                # PI position: BC + T × direction_vector
                pi_x = bc_x + tangent_length * math.cos(angle_in)
                pi_y = bc_y + tangent_length * math.sin(angle_in)

                pis.append({
                    "x": pi_x,
                    "y": pi_y,
                    "radius": radius,
                    "type": "CURVE"
                })

            elif seg_type == "LINE":
                # For LINE segments, check if this is a transition point
                # If the previous segment was also LINE and this isn't the first,
                # we may have a tangent PI at the connection point
                if i > 0 and prev_seg_type == "LINE":
                    # There's a tangent PI at the start of this LINE
                    # (end of previous LINE)
                    start_x = float(dp.StartPoint.Coordinates[0])
                    start_y = float(dp.StartPoint.Coordinates[1])
                    pis.append({
                        "x": start_x,
                        "y": start_y,
                        "radius": 0.0,
                        "type": "TANGENT"
                    })

            prev_seg_type = seg_type

        # Last PI: end point of last segment
        last_dp = real_segments[-1].DesignParameters
        last_seg_type = last_dp.PredefinedType
        last_length = float(last_dp.SegmentLength)
        last_direction = float(last_dp.StartDirection)
        last_start_x = float(last_dp.StartPoint.Coordinates[0])
        last_start_y = float(last_dp.StartPoint.Coordinates[1])

        if last_seg_type == "LINE":
            # End of LINE: simple projection
            end_x = last_start_x + last_length * math.cos(last_direction)
            end_y = last_start_y + last_length * math.sin(last_direction)
        elif last_seg_type == "CIRCULARARC":
            # End of ARC: use geometry engine or calculate
            last_radius = abs(float(last_dp.StartRadiusOfCurvature))
            deflection = last_length / last_radius

            # Determine curve direction (positive radius = counterclockwise)
            is_ccw = float(last_dp.StartRadiusOfCurvature) > 0
            if is_ccw:
                end_direction = last_direction + deflection
            else:
                end_direction = last_direction - deflection

            # Calculate EC (end curve) position
            # For an arc, EC is at BC + arc travel
            # We need to use the center calculation
            center_offset_angle = last_direction + (math.pi / 2 if is_ccw else -math.pi / 2)
            center_x = last_start_x + last_radius * math.cos(center_offset_angle)
            center_y = last_start_y + last_radius * math.sin(center_offset_angle)

            # EC is at the end of the arc
            ec_angle = center_offset_angle + math.pi + (deflection if is_ccw else -deflection)
            end_x = center_x + last_radius * math.cos(ec_angle)
            end_y = center_y + last_radius * math.sin(ec_angle)
        else:
            # For other segment types (CLOTHOID, etc.), use start point as fallback
            # TODO: Support spiral transitions
            end_x = last_start_x
            end_y = last_start_y

        pis.append({
            "x": end_x,
            "y": end_y,
            "radius": 0.0,
            "type": "ENDPOINT"
        })

        return pis

    @classmethod
    def create_pi_edit_empties(
        cls,
        alignment: "ifcopenshell.entity_instance",
        pis: List[dict],
    ) -> List[bpy.types.Object]:
        """Create EMPTY objects at PI locations for editing.

        Creates temporary Blender EMPTY objects at each PI position,
        allowing users to move them with standard Blender tools (G key).

        The empties are:
        - Parented to the alignment object
        - Tagged with custom properties for identification
        - Named sequentially (PI.001, PI.002, etc.)

        Args:
            alignment: The IfcAlignment entity
            pis: List of PI dicts from back_calculate_pis_from_alignment()

        Returns:
            List of created Blender EMPTY objects, sorted by index
        """
        alignment_obj = tool.Ifc.get_object(alignment)
        if alignment_obj is None:
            return []

        # Get the collection to add objects to
        collection = None
        if alignment_obj.users_collection:
            collection = alignment_obj.users_collection[0]
        else:
            collection = bpy.context.scene.collection

        alignment_id = alignment.id()
        empties = []

        for i, pi in enumerate(pis):
            # Convert IFC coordinates to Blender coordinates
            blender_pos = tool.Georeference.enh2xyz((float(pi["e"]), float(pi["n"]), 0.0))

            # Create EMPTY object
            name = f"PI.{i + 1:03d}"
            empty = bpy.data.objects.new(name, None)
            empty.empty_display_type = "SPHERE"
            empty.empty_display_size = 2.0
            empty.location = blender_pos

            # Tag with custom properties for identification
            empty["saikei_is_pi_empty"] = True
            empty["saikei_pi_index"] = i
            empty["saikei_pi_radius"] = pi["radius"]
            empty["saikei_alignment_id"] = alignment_id
            empty["saikei_pi_type"] = pi["type"]

            # Parent to alignment object
            empty.parent = alignment_obj

            # Link to collection
            collection.objects.link(empty)

            empties.append(empty)

        return empties

    @classmethod
    def get_pi_edit_empties(cls, alignment_id: int) -> List[bpy.types.Object]:
        """Find all PI EMPTY objects for a given alignment.

        Searches all objects in the scene for empties tagged with
        the PI edit mode custom properties.

        Args:
            alignment_id: The IFC ID of the alignment being edited

        Returns:
            List of PI EMPTY objects, sorted by pi_index
        """
        empties = []

        for obj in bpy.data.objects:
            if obj.get("saikei_is_pi_empty") and obj.get("saikei_alignment_id") == alignment_id:
                empties.append(obj)

        # Sort by PI index
        empties.sort(key=lambda e: e.get("saikei_pi_index", 0))

        return empties

    @classmethod
    def remove_pi_edit_empties(cls, alignment_id: int) -> int:
        """Remove all PI EMPTY objects for a given alignment.

        Args:
            alignment_id: The IFC ID of the alignment being edited

        Returns:
            Number of objects removed
        """
        empties = cls.get_pi_edit_empties(alignment_id)
        removed_count = 0

        for empty in empties:
            bpy.data.objects.remove(empty, do_unlink=True)
            removed_count += 1

        return removed_count

    @classmethod
    def collect_pis_from_empties(
        cls, alignment_id: int
    ) -> Tuple[List[Tuple[float, float]], List[float]]:
        """Gather current PI positions from EMPTY objects.

        Reads the current positions of PI empties and converts them
        back to IFC coordinates for regenerating the alignment.

        Args:
            alignment_id: The IFC ID of the alignment being edited

        Returns:
            Tuple of:
            - hpoints: List of (x, y) tuples in IFC coordinates
            - radii: List of radii for interior PIs only (not first/last)
        """
        empties = cls.get_pi_edit_empties(alignment_id)

        if len(empties) < 2:
            return ([], [])

        hpoints = []
        radii = []

        for i, empty in enumerate(empties):
            # Convert Blender position to IFC coordinates
            ifc_pos = tool.Georeference.xyz2enh(tuple(empty.matrix_world.translation))
            hpoints.append((ifc_pos[0], ifc_pos[1]))

            # Collect radii for interior PIs only (not first or last)
            if 0 < i < len(empties) - 1:
                radius = empty.get("saikei_pi_radius", 0.0)
                radii.append(radius)

        return (hpoints, radii)
