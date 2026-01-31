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

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal, etc.)
            parent_obj: The parent Blender object (alignment object)

        Returns:
            The created Blender curve object, or None if no representation
        """
        import ifcopenshell.api.alignment as align_api
        from ifcopenshell.api.alignment import util as align_util

        # Get the layout's curve representation
        try:
            rep_curve = align_api.get_layout_curve(layout)
        except Exception:
            rep_curve = None

        if rep_curve is None:
            return None

        # Generate vertices using IfcOpenShell's geometry engine
        try:
            vertices = align_util.generate_vertices(rep_curve, distance_interval=1.0)
        except (ValueError, NotImplementedError):
            return None

        if len(vertices) < 2:
            return None

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
    def _create_segment_empty(
        cls, segment: "ifcopenshell.entity_instance", index: int, parent_obj: Optional[bpy.types.Object] = None
    ) -> Optional[bpy.types.Object]:
        """Create an empty Blender object linked to an IFC segment.

        Creates an empty (no geometry) for segment selection/editing.
        The layout curve handles visualization.

        Args:
            segment: The IfcAlignmentSegment entity
            index: The segment index (for naming)
            parent_obj: The parent Blender object (layout object)

        Returns:
            The created Blender object, or existing one if already linked
        """
        # Check if a Blender object already exists for this IFC element
        existing_obj = tool.Ifc.get_object(segment)
        if existing_obj:
            return existing_obj

        # Get segment parameters for naming and positioning
        if not hasattr(segment, "DesignParameters") or not segment.DesignParameters:
            return None

        dp = segment.DesignParameters
        seg_type = getattr(dp, "PredefinedType", "UNKNOWN") or "UNKNOWN"
        name = f"Segment {index + 1} ({seg_type})"

        # Create empty (no geometry - the layout curve handles visualization)
        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = "PLAIN_AXES"
        obj.empty_display_size = 0.5

        # Position at segment start point
        if hasattr(dp, "StartPoint") and dp.StartPoint:
            coords = dp.StartPoint.Coordinates
            if len(coords) >= 2:
                obj.location = (coords[0], coords[1], 0.0)

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
        """Create Blender objects for all segments in a layout.

        Creates a single curve from the IFC representation for visualization,
        plus empty objects for each segment (for selection/editing).

        Args:
            layout: The IFC layout entity (IfcAlignmentHorizontal, etc.)
            layout_obj: The parent Blender object for the layout

        Returns:
            List of created Blender objects (curve + segment empties)
        """
        result_objs = []

        # Create layout curve from IFC representation (for visualization)
        # This uses IfcOpenShell's geometry engine which supports all segment types
        curve_obj = cls.create_curve_from_representation(layout, layout_obj)
        if curve_obj:
            result_objs.append(curve_obj)

        # Create empty objects for each segment (for selection/editing)
        for rel in getattr(layout, "IsNestedBy", []) or []:
            for i, segment in enumerate(rel.RelatedObjects or []):
                if segment.is_a() == "IfcAlignmentSegment":
                    seg_obj = cls._create_segment_empty(segment, i, layout_obj)
                    if seg_obj:
                        result_objs.append(seg_obj)

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
