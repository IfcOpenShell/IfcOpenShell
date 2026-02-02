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
import bonsai.tool as tool
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

        Uses the proven IfcOpenShell geometry engine to evaluate points along
        the segment, supporting all segment types (LINE, CIRCULARARC, CLOTHOID,
        spirals, etc.).

        Args:
            segment: The IfcAlignmentSegment entity
            distance_interval: Distance between sample points (default 1.0 units)

        Returns:
            List of (x, y, z) tuples representing vertices along the segment,
            or None if geometry cannot be generated
        """
        import ifcopenshell.api.alignment as align_api
        from ifcopenshell.api.alignment import util as align_util
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

            # Get segment length
            try:
                seg_length = abs(curve_segment.SegmentLength.wrappedValue)
            except (AttributeError, TypeError):
                try:
                    seg_length = abs(float(curve_segment.SegmentLength))
                except:
                    continue

            if seg_length < 1e-6:
                continue

            # Calculate number of sample points
            num_points = max(int(seg_length / distance_interval) + 1, 2)

            # Sample points along the segment using IfcOpenShell's geometry engine
            for i in range(num_points):
                # Calculate distance along segment (don't exceed segment length)
                if num_points > 1:
                    dist_along = min(i * distance_interval, seg_length)
                    # Ensure we get the last point exactly at segment end
                    if i == num_points - 1:
                        dist_along = seg_length
                else:
                    dist_along = 0.0

                try:
                    # Use IfcOpenShell's evaluate_segment to get transform matrix
                    transform_matrix = align_util.evaluate_segment(curve_segment, dist_along)

                    # Extract position from 4x4 matrix
                    # Matrix is transposed by util.py, so translation is in row 3
                    x = float(transform_matrix[3, 0]) / unit_scale
                    y = float(transform_matrix[3, 1]) / unit_scale
                    z = float(transform_matrix[3, 2]) / unit_scale

                    all_vertices.append((x, y, z))

                except Exception as e:
                    # If evaluation fails at this point, skip it
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
        try:
            vertices = align_util.generate_vertices(rep_curve, distance_interval=1.0)
        except (ValueError, NotImplementedError, RuntimeError) as e:
            # RuntimeError can occur if IfcOpenShell version doesn't support certain settings
            print(f"[Alignment] generate_vertices failed: {e}")
            return None

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
        vertices = cls.get_segment_vertices(segment, distance_interval=1.0)
        if not vertices or len(vertices) < 2:
            # Fall back to empty if geometry fails
            obj = bpy.data.objects.new(name, None)
            obj.empty_display_type = "PLAIN_AXES"
            obj.empty_display_size = 0.5
        else:
            # Transform vertices from IFC to Blender coordinates
            blender_vertices = [cls.ifc_to_blender_coordinates(v[0], v[1], v[2]) for v in vertices]

            # Create Blender curve from vertices
            curve_data = bpy.data.curves.new(name, type="CURVE")
            curve_data.dimensions = "3D"

            spline = curve_data.splines.new("POLY")
            spline.points.add(len(blender_vertices) - 1)

            for i, vert in enumerate(blender_vertices):
                spline.points[i].co = (vert[0], vert[1], vert[2], 1.0)

            obj = bpy.data.objects.new(name, curve_data)
            obj.show_in_front = True
            curve_data.bevel_depth = 0.0

        # Link to IFC element
        tool.Ifc.link(segment, obj)

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
                    # Skip zero-length segments (they are invisible terminators)
                    if cls.is_zero_length_segment(segment):
                        continue
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
    # Coordinate Transformation Methods
    # =========================================================================

    @classmethod
    def blender_to_ifc_coordinates(cls, x: float, y: float, z: float = 0.0) -> Tuple[float, float, float]:
        """Convert Blender local coordinates to IFC global/map coordinates.

        When a Blender offset is configured (for handling large geospatial coordinates),
        this transforms from Blender's local coordinate system (near origin) to
        the IFC global coordinate system (large geospatial values).

        Args:
            x: X coordinate in Blender space
            y: Y coordinate in Blender space
            z: Z coordinate in Blender space (default 0.0)

        Returns:
            Tuple of (x, y, z) in IFC global coordinates
        """
        import ifcopenshell.util.geolocation
        import ifcopenshell.util.unit

        gprops = tool.Georeference.get_georeference_props()
        ifc_file = tool.Ifc.get()

        if not gprops.has_blender_offset or ifc_file is None:
            # No transformation needed
            return (x, y, z)

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        offset_x = float(gprops.blender_offset_x) * unit_scale
        offset_y = float(gprops.blender_offset_y) * unit_scale
        offset_z = float(gprops.blender_offset_z) * unit_scale
        x_axis_abscissa = float(gprops.blender_x_axis_abscissa)
        x_axis_ordinate = float(gprops.blender_x_axis_ordinate)

        # Create a 4x4 identity matrix with translation set to position
        import numpy as np
        matrix = np.eye(4)
        matrix[0, 3] = x
        matrix[1, 3] = y
        matrix[2, 3] = z

        # Apply local2global transformation (inverse of global2local)
        global_matrix = ifcopenshell.util.geolocation.local2global(
            matrix, offset_x, offset_y, offset_z, x_axis_abscissa, x_axis_ordinate
        )

        return (global_matrix[0, 3], global_matrix[1, 3], global_matrix[2, 3])

    @classmethod
    def ifc_to_blender_coordinates(cls, x: float, y: float, z: float = 0.0) -> Tuple[float, float, float]:
        """Convert IFC global/map coordinates to Blender local coordinates.

        When a Blender offset is configured (for handling large geospatial coordinates),
        this transforms from the IFC global coordinate system (large geospatial values)
        to Blender's local coordinate system (near origin).

        Args:
            x: X coordinate in IFC global space
            y: Y coordinate in IFC global space
            z: Z coordinate in IFC global space (default 0.0)

        Returns:
            Tuple of (x, y, z) in Blender local coordinates
        """
        import ifcopenshell.util.geolocation
        import ifcopenshell.util.unit

        gprops = tool.Georeference.get_georeference_props()
        ifc_file = tool.Ifc.get()

        if not gprops.has_blender_offset or ifc_file is None:
            # No transformation needed
            return (x, y, z)

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        offset_x = float(gprops.blender_offset_x) * unit_scale
        offset_y = float(gprops.blender_offset_y) * unit_scale
        offset_z = float(gprops.blender_offset_z) * unit_scale
        x_axis_abscissa = float(gprops.blender_x_axis_abscissa)
        x_axis_ordinate = float(gprops.blender_x_axis_ordinate)

        # Create a 4x4 identity matrix with translation set to position
        import numpy as np
        matrix = np.eye(4)
        matrix[0, 3] = x
        matrix[1, 3] = y
        matrix[2, 3] = z

        # Apply global2local transformation
        local_matrix = ifcopenshell.util.geolocation.global2local(
            matrix, offset_x, offset_y, offset_z, x_axis_abscissa, x_axis_ordinate
        )

        return (local_matrix[0, 3], local_matrix[1, 3], local_matrix[2, 3])
