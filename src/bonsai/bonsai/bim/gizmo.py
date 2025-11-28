# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

"""
Shared gizmo components for reuse across modules.
"""

__all__ = [
    # Dataclasses
    "GizmoPropConfig",
    # Functions
    "set_snap_point",
    "clear_snap_point",
    "snap_to_mesh",
    "generate_circle_vertices",
    "create_circle_arc",
    # Gizmo classes
    "GizmoMovable",
    "GizmoLock",
    "GizmoArc",
    "GizmoPen",
    "GizmoValidate",
    "GizmoCancel",
    "GizmoPlus",
    "GizmoMinus",
    "GizmoCycle",
    "GizmoArrow",
    "GizmoCone",
    # Mixin classes
    "BaseParametricGizmoGroup",
]

from typing import Any

import bpy
import math
from dataclasses import dataclass
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_line_line
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
import gpu
from gpu_extras.batch import batch_for_shader
import bonsai.tool as tool


SNAP_POINT_SIZE = 10.0
SNAP_POINT_COLOR = (1.0, 0.5, 0.0, 1.0)
SNAP_MAX_RADIUS = 5.0
SNAP_SCREEN_DISTANCE = 30  # Maximum screen-space distance for snapping (in pixels)
SNAP_WORLD_DISTANCE = 0.2  # Maximum world-space distance for snapping (in meters)

ARROW_SHAFT_LENGTH = 0.8
ARROW_HEAD_LENGTH = 0.2
ARROW_WIDTH = 0.015
ARROW_HEAD_WIDTH_MULTIPLIER = 10
ARROW_CIRCLE_SEGMENTS = 8

CONE_LENGTH = 1.0
CONE_RADIUS = 0.35
CONE_SEGMENTS = 16

ARC_SEGMENTS = 24
ARC_LINE_WIDTH = 0.015

PRECISION_MODE_MULTIPLIER = 0.1

RAY_CAST_DISTANCE = 1000  # Distance to extend rays for intersection calculations
DEFAULT_POINT_SIZE = 1.0  # Default GPU point size


@dataclass
class GizmoPropConfig:
    """Configuration for a gizmo property.

    Attributes:
        attr_name: Name of the property attribute on the element's props
        axis: Direction axis as (x, y, z) tuple, determines gizmo color and direction.
            Color convention follows Blender's standard axis colors:
            - X axis (1, 0, 0) or (-1, 0, 0) -> Red
            - Y axis (0, 1, 0) or (0, -1, 0) -> Green
            - Z axis (0, 0, 1) or (0, 0, -1) -> Blue
        invert_delta: If True, inverts the drag direction for this gizmo
    """

    attr_name: str
    axis: tuple[int, int, int]
    invert_delta: bool = False


class SnapManager:
    """Manages snap point visualization and mesh snapping."""

    def __init__(self):
        self._snap_point: tuple[float, float, float] | Vector | None = None
        self._draw_handler = None
        self._shader = None

    def set_snap_point(self, point: tuple[float, float, float] | Vector | None) -> None:
        """Set snap point and register draw handler if needed."""
        self._snap_point = point
        if self._draw_handler is None and point is not None:
            self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(self._draw, (), "WINDOW", "POST_VIEW")
            self._redraw_viewport()

    def clear(self) -> None:
        """Clear snap point and unregister handler."""
        self._snap_point = None
        if self._draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, "WINDOW")
            self._draw_handler = None
            self._redraw_viewport()

    def _draw(self) -> None:
        """Draw snap point as a dot."""
        if self._snap_point is None:
            return

        if self._shader is None:
            self._shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        self._shader.bind()
        self._shader.uniform_float("color", SNAP_POINT_COLOR)
        gpu.state.point_size_set(SNAP_POINT_SIZE)

        batch = batch_for_shader(self._shader, "POINTS", {"pos": [self._snap_point]})
        batch.draw(self._shader)

        gpu.state.point_size_set(DEFAULT_POINT_SIZE)

    @staticmethod
    def _redraw_viewport() -> None:
        """Force 3D viewport redraw."""
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()

    @staticmethod
    def _calc_snap_distance(
        point_3d: Vector,
        location: Vector,
        mouse_coords: tuple[float, float] | None,
        region: bpy.types.Region | None,
        rv3d: bpy.types.RegionView3D | None,
    ) -> float:
        """Calculate distance - screen-space if mouse coords available, else world-space."""
        if mouse_coords is not None and region is not None and rv3d is not None:
            point_2d = location_3d_to_region_2d(region, rv3d, point_3d)
            if point_2d is not None:
                return (Vector(mouse_coords) - point_2d).length
            return float("inf")
        return (point_3d - location).length

    @staticmethod
    def _find_closest_vertex(
        world_vertices: list[Vector],
        location: Vector,
        mouse_coords: tuple[float, float] | None,
        region: bpy.types.Region | None,
        rv3d: bpy.types.RegionView3D | None,
        closest_point: Vector | None,
        closest_distance: float,
    ) -> tuple[Vector | None, float]:
        """Find the closest vertex to snap to."""
        for v_co in world_vertices:
            dist = SnapManager._calc_snap_distance(v_co, location, mouse_coords, region, rv3d)
            if dist < closest_distance:
                closest_distance = dist
                closest_point = v_co
        return closest_point, closest_distance

    @staticmethod
    def _find_closest_edge_point(
        mesh: bpy.types.Mesh,
        world_vertices: list[Vector],
        location: Vector,
        mouse_coords: tuple[float, float] | None,
        region: bpy.types.Region | None,
        rv3d: bpy.types.RegionView3D | None,
        closest_point: Vector | None,
        closest_distance: float,
    ) -> tuple[Vector | None, float]:
        """Find the closest point on an edge to snap to."""
        for edge in mesh.edges:
            v1 = world_vertices[edge.vertices[0]]
            v2 = world_vertices[edge.vertices[1]]

            edge_vec = v2 - v1
            edge_len_sq = edge_vec.length_squared

            if edge_len_sq > 0:
                t = max(0, min(1, (location - v1).dot(edge_vec) / edge_len_sq))
                closest_on_edge = v1 + t * edge_vec
                dist = SnapManager._calc_snap_distance(closest_on_edge, location, mouse_coords, region, rv3d)

                if dist < closest_distance:
                    closest_distance = dist
                    closest_point = closest_on_edge
        return closest_point, closest_distance

    @staticmethod
    def _find_closest_face_point(
        mesh: bpy.types.Mesh,
        world_vertices: list[Vector],
        location: Vector,
        mouse_coords: tuple[float, float] | None,
        region: bpy.types.Region | None,
        rv3d: bpy.types.RegionView3D | None,
        closest_point: Vector | None,
        closest_distance: float,
    ) -> tuple[Vector | None, float]:
        """Find the closest point on a face to snap to."""
        bvh = BVHTree.FromPolygons(world_vertices, [p.vertices for p in mesh.polygons])
        nearest_loc, normal, index, dist = bvh.find_nearest(location)

        if nearest_loc:
            screen_dist = SnapManager._calc_snap_distance(nearest_loc, location, mouse_coords, region, rv3d)
            if screen_dist < closest_distance:
                closest_distance = screen_dist
                closest_point = nearest_loc
        return closest_point, closest_distance

    @staticmethod
    def _get_nearby_objects(
        mesh_objects: list[bpy.types.Object],
        location: Vector,
    ) -> list[bpy.types.Object]:
        """Filter objects to those within SNAP_MAX_RADIUS of location."""
        nearby_objects = []
        for obj in mesh_objects:
            bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            for corner in bbox_corners:
                if (corner - location).length <= SNAP_MAX_RADIUS:
                    nearby_objects.append(obj)
                    break
        return nearby_objects

    @staticmethod
    def snap_to_mesh(
        location: Vector,
        context: bpy.types.Context,
        axis_vector: Vector,
        active_obj: bpy.types.Object,
        mouse_coords: tuple[float, float] | None = None,
    ) -> Vector:
        """Snap a location to the nearest mesh element if snapping is enabled.

        Args:
            location: The world space location to snap
            context: The Blender context
            axis_vector: The axis direction of the gizmo
            active_obj: The active object to exclude from snapping
            mouse_coords: Optional (x, y) mouse position in region coordinates for screen-space distance

        Returns:
            The snapped location or original location if snapping is disabled
        """
        tool_settings = context.scene.tool_settings

        if not tool_settings.use_snap:
            return location

        snap_elements = tool_settings.snap_elements_base

        mesh_objects = [
            obj for obj in context.visible_objects if obj.type == "MESH" and obj != active_obj and obj.visible_get()
        ]

        if not mesh_objects:
            return location

        nearby_objects = SnapManager._get_nearby_objects(mesh_objects, location)

        if not nearby_objects:
            return location

        region = context.region
        rv3d = context.region_data
        use_screen_distance = mouse_coords is not None and region is not None and rv3d is not None

        closest_point: Vector | None = None
        closest_distance = float("inf")

        for obj in nearby_objects:
            if not obj.data.vertices:
                continue

            depsgraph = context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)
            mesh = obj_eval.to_mesh()

            if not mesh.vertices:
                obj_eval.to_mesh_clear()
                continue

            world_vertices = [obj.matrix_world @ v.co for v in mesh.vertices]

            if "VERTEX" in snap_elements:
                closest_point, closest_distance = SnapManager._find_closest_vertex(
                    world_vertices, location, mouse_coords, region, rv3d, closest_point, closest_distance
                )

            if "EDGE" in snap_elements:
                closest_point, closest_distance = SnapManager._find_closest_edge_point(
                    mesh, world_vertices, location, mouse_coords, region, rv3d, closest_point, closest_distance
                )

            if "FACE" in snap_elements:
                closest_point, closest_distance = SnapManager._find_closest_face_point(
                    mesh, world_vertices, location, mouse_coords, region, rv3d, closest_point, closest_distance
                )

            obj_eval.to_mesh_clear()

        # Use screen-space threshold (pixels) or fall back to world-space
        max_distance = SNAP_SCREEN_DISTANCE if use_screen_distance else SNAP_WORLD_DISTANCE
        if closest_point and closest_distance < max_distance:
            return closest_point

        return location


_snap_manager = SnapManager()


def set_snap_point(point: tuple[float, float, float] | Vector | None) -> None:
    _snap_manager.set_snap_point(point)


def clear_snap_point() -> None:
    _snap_manager.clear()


def snap_to_mesh(
    location: Vector,
    context: bpy.types.Context,
    axis_vector: Vector,
    active_obj: bpy.types.Object,
    mouse_coords: tuple[float, float] | None = None,
) -> Vector:
    return _snap_manager.snap_to_mesh(location, context, axis_vector, active_obj, mouse_coords)


def generate_circle_vertices(
    center: tuple[float, float, float] | Vector, radius: float, segments: int, plane: str = "XY"
) -> list[tuple[float, float, float]]:
    """Generate circle vertices in specified plane.

    Args:
        center: (x, y, z) tuple for circle center
        radius: Circle radius
        segments: Number of segments
        plane: 'XY', 'XZ', or 'YZ'

    Returns:
        List of (x, y, z) vertices
    """
    vertices = []
    for i in range(segments + 1):
        angle = (2 * math.pi * i) / segments
        cos_a = radius * math.cos(angle)
        sin_a = radius * math.sin(angle)

        if plane == "XY":
            vertices.append((center[0] + cos_a, center[1] + sin_a, center[2]))
        elif plane == "XZ":
            vertices.append((center[0] + cos_a, center[1], center[2] + sin_a))
        else:
            vertices.append((center[0], center[1] + cos_a, center[2] + sin_a))

    return vertices


def create_circle_arc(
    radius: float = 1.0,
    segments: int = ARC_SEGMENTS,
    direction: str = "LEFT",
    line_width: float = ARC_LINE_WIDTH,
    angle_min: float = 0.0,
    angle_max: float = 90.0,
) -> tuple[tuple[float, float, float], ...]:
    """Create a circle arc with cross-section thickness for visibility from all angles.

    Args:
        radius: Radius of the arc
        segments: Number of segments for smoothness
        direction: 'LEFT' for counterclockwise, 'RIGHT' for clockwise (mirrors along X)
        line_width: Width of the arc line in both perpendicular directions
        angle_min: Start angle in degrees (default 0°)
        angle_max: End angle in degrees (default 90°)

    Returns:
        Tuple of arc triangles for drawing geometry visible from all angles
    """
    half_width = line_width / 2
    angle_min_rad = math.radians(angle_min)
    angle_max_rad = math.radians(angle_max)
    angle_range = angle_max_rad - angle_min_rad

    arc_points = []
    if direction == "LEFT":
        for i in range(segments + 1):
            angle = angle_min_rad + angle_range * (i / segments)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            arc_points.append((x, y))
    else:
        for i in range(segments + 1):
            angle = angle_min_rad + angle_range * (i / segments)
            x = -radius * math.cos(angle)
            y = radius * math.sin(angle)
            arc_points.append((x, y))

    arc_triangles = []
    for i in range(len(arc_points) - 1):
        x1, y1 = arc_points[i]
        x2, y2 = arc_points[i + 1]

        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2) ** 0.5
        if length > 0:
            px, py = -dy / length * half_width, dx / length * half_width

            arc_triangles.extend(
                [
                    (x1 + px, y1 + py, 0.0),
                    (x1 - px, y1 - py, 0.0),
                    (x2 + px, y2 + py, 0.0),
                ]
            )
            arc_triangles.extend(
                [
                    (x2 + px, y2 + py, 0.0),
                    (x1 - px, y1 - py, 0.0),
                    (x2 - px, y2 - py, 0.0),
                ]
            )

            arc_triangles.extend(
                [
                    (x1, y1, -half_width),
                    (x2, y2, -half_width),
                    (x1, y1, +half_width),
                ]
            )
            arc_triangles.extend(
                [
                    (x1, y1, +half_width),
                    (x2, y2, -half_width),
                    (x2, y2, +half_width),
                ]
            )

    return tuple(arc_triangles)


class GizmoMovable(bpy.types.Gizmo):
    """Base class for movable gizmos with snapping and precision controls.

    This class provides common functionality for gizmos that can be dragged
    to modify values, including:
    - Snap to mesh support (toggle with Ctrl)
    - Precision mode (hold Shift for 10x slower movement)
    - Header text with value and modifier hints
    - Consistent invoke/exit/modal behavior
    """

    __slots__ = (
        "custom_shape",
        "init_value",
        "move_get_cb",
        "move_set_cb",
        "axis",
        "local_axis",
        "start_location",
        "active_obj",
        "initial_snap_state",
        "invert_delta",
    )

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set:
        self.init_value = self.move_get_cb() if self.move_get_cb else 0.0
        self.start_location = self.matrix_basis.translation.copy()
        self.active_obj = context.active_object
        self.initial_snap_state = context.scene.tool_settings.use_snap
        return {"RUNNING_MODAL"}

    def exit(self, context: bpy.types.Context, cancel: bool) -> None:
        context.area.header_text_set(None)
        if cancel and self.move_set_cb:
            self.move_set_cb(self.init_value)
        if hasattr(self, "initial_snap_state"):
            context.scene.tool_settings.use_snap = self.initial_snap_state
        clear_snap_point()

    def get_axis_direction(self) -> Vector:
        return self.axis

    def modal(self, context: bpy.types.Context, event: bpy.types.Event, tweak) -> set:
        region = context.region
        rv3d = context.region_data
        tool_settings = context.scene.tool_settings

        tool_settings.use_snap = not self.initial_snap_state if event.ctrl else self.initial_snap_state

        current_coord = (event.mouse_region_x, event.mouse_region_y)
        view_origin = region_2d_to_origin_3d(region, rv3d, current_coord)
        view_direction = region_2d_to_vector_3d(region, rv3d, current_coord)

        axis_direction = self.get_axis_direction()

        result = intersect_line_line(
            view_origin,
            view_origin + view_direction * RAY_CAST_DISTANCE,
            self.start_location,
            self.start_location + axis_direction * RAY_CAST_DISTANCE,
        )
        current_3d = result[1] if result else self.start_location

        delta = (current_3d - self.start_location).dot(axis_direction)

        if tool_settings.use_snap and self.active_obj:
            snapped_pos = snap_to_mesh(current_3d, context, axis_direction, self.active_obj, current_coord)
            if snapped_pos != current_3d:
                delta = (snapped_pos - self.start_location).dot(axis_direction)
                set_snap_point(snapped_pos)
            else:
                clear_snap_point()
        else:
            clear_snap_point()

        if event.shift:
            delta *= PRECISION_MODE_MULTIPLIER

        if getattr(self, "invert_delta", False):
            delta = -delta

        if self.move_set_cb:
            self.move_set_cb(self.init_value + delta)

        self._update_header(context, self.init_value + delta, tool_settings.use_snap, event.shift)

        return {"RUNNING_MODAL"}

    def _update_header(self, context: bpy.types.Context, value: float, is_snapping: bool, is_precision: bool) -> None:
        header_text = f"Value: {value:.3f}m"
        hints = []
        if is_snapping:
            hints.append("Snapping: ON")
        if is_precision:
            hints.append("Precision Mode (0.1x)")
        hints.extend(["Ctrl: Toggle Snap", "Shift: Precision"])

        if hints:
            header_text += "  |  " + "  |  ".join(hints)
        context.area.header_text_set(header_text)


class GizmoLock(bpy.types.Gizmo):
    """Reusable lock icon gizmo that switches between closed and open states."""

    bl_idname = "VIEW3D_GT_lock"

    __slots__ = (
        "custom_shape_closed",
        "custom_shape_open",
        "prop_path",
    )

    tris_closed = (
        (-0.12838619947433472, 1.3143587112426758, 0.0),
        (0.025773197412490845, 1.411454677581787, 0.0),
        (-0.0144234299659729, 1.541273593902588, 0.0),
        (-0.0144234299659729, 1.541273593902588, 0.0),
        (0.025773197412490845, 1.411454677581787, 0.0),
        (0.20782703161239624, 1.4184625148773193, 0.0),
        (0.23792517185211182, 1.5509872436523438, 0.0),
        (0.20782703161239624, 1.4184625148773193, 0.0),
        (0.3689943850040436, 1.3335046768188477, 0.0),
        (0.4613226056098938, 1.433225393295288, 0.0),
        (0.3689943850040436, 1.3335046768188477, 0.0),
        (0.4660903215408325, 1.1793451309204102, 0.0),
        (0.5959094166755676, 1.2195416688919067, 0.0),
        (0.4660903215408325, 1.1793451309204102, 0.0),
        (0.47309836745262146, 0.997291088104248, 0.0),
        (0.6056233048439026, 0.9671931266784668, 0.0),
        (0.47309836745262146, 0.997291088104248, 0.0),
        (0.3881405293941498, 0.8361238241195679, 0.0),
        (-0.48786139488220215, 0.7437955141067505, 0.0),
        (0.48786139488220215, 4.5077928945147505e-08, 0.0),
        (0.48786139488220215, 0.7437955141067505, 0.0),
        (-0.12838619947433472, 1.3143587112426758, 0.0),
        (-0.0144234299659729, 1.541273593902588, 0.0),
        (-0.22810709476470947, 1.406686782836914, 0.0),
        (-0.0144234299659729, 1.541273593902588, 0.0),
        (0.20782703161239624, 1.4184625148773193, 0.0),
        (0.23792517185211182, 1.5509872436523438, 0.0),
        (0.23792517185211182, 1.5509872436523438, 0.0),
        (0.3689943850040436, 1.3335046768188477, 0.0),
        (0.4613226056098938, 1.433225393295288, 0.0),
        (0.4613226056098938, 1.433225393295288, 0.0),
        (0.4660903215408325, 1.1793451309204102, 0.0),
        (0.5959094166755676, 1.2195416688919067, 0.0),
        (0.5959094166755676, 1.2195416688919067, 0.0),
        (0.47309836745262146, 0.997291088104248, 0.0),
        (0.6056233048439026, 0.9671931266784668, 0.0),
        (0.6056233048439026, 0.9671931266784668, 0.0),
        (0.3881405293941498, 0.8361238241195679, 0.0),
        (0.48786142468452454, 0.74379563331604, 0.0),
        (-0.48786139488220215, 0.7437955141067505, 0.0),
        (-0.48786139488220215, 4.5077928945147505e-08, 0.0),
        (0.48786139488220215, 4.5077928945147505e-08, 0.0),
    )

    tris_open = (
        (-0.3519617021083832, 0.7437955141067505, 0.0),
        (-0.3048076927661896, 0.9197763204574585, 0.0),
        (-0.4225003123283386, 0.9877263307571411, 0.0),
        (-0.4225003123283386, 0.9877263307571411, 0.0),
        (-0.3048076927661896, 0.9197763204574585, 0.0),
        (-0.1759808510541916, 1.0486031770706177, 0.0),
        (-0.24393069744110107, 1.1662957668304443, 0.0),
        (-0.1759808510541916, 1.0486031770706177, 0.0),
        (2.9078805141580233e-08, 1.0957571268081665, 0.0),
        (2.9078805141580233e-08, 1.2316569089889526, 0.0),
        (2.9078805141580233e-08, 1.0957571268081665, 0.0),
        (0.1759808510541916, 1.0486031770706177, 0.0),
        (0.243930846452713, 1.1662957668304443, 0.0),
        (0.1759808510541916, 1.0486031770706177, 0.0),
        (0.30480796098709106, 0.9197763204574585, 0.0),
        (0.4225005805492401, 0.9877263307571411, 0.0),
        (0.30480796098709106, 0.9197763204574585, 0.0),
        (0.35196200013160706, 0.7437955141067505, 0.0),
        (-0.48786139488220215, 0.7437955141067505, 0.0),
        (0.48786139488220215, 4.5077928945147505e-08, 0.0),
        (0.48786139488220215, 0.7437955141067505, 0.0),
        (-0.3519617021083832, 0.7437955141067505, 0.0),
        (-0.4225003123283386, 0.9877263307571411, 0.0),
        (-0.48786139488220215, 0.7437955141067505, 0.0),
        (-0.4225003123283386, 0.9877263307571411, 0.0),
        (-0.1759808510541916, 1.0486031770706177, 0.0),
        (-0.24393069744110107, 1.1662957668304443, 0.0),
        (-0.24393069744110107, 1.1662957668304443, 0.0),
        (2.9078805141580233e-08, 1.0957571268081665, 0.0),
        (2.9078805141580233e-08, 1.2316569089889526, 0.0),
        (2.9078805141580233e-08, 1.2316569089889526, 0.0),
        (0.1759808510541916, 1.0486031770706177, 0.0),
        (0.243930846452713, 1.1662957668304443, 0.0),
        (0.243930846452713, 1.1662957668304443, 0.0),
        (0.30480796098709106, 0.9197763204574585, 0.0),
        (0.4225005805492401, 0.9877263307571411, 0.0),
        (0.4225005805492401, 0.9877263307571411, 0.0),
        (0.35196200013160706, 0.7437955141067505, 0.0),
        (0.487861692905426, 0.74379563331604, 0.0),
        (-0.48786139488220215, 0.7437955141067505, 0.0),
        (-0.48786139488220215, 4.5077928945147505e-08, 0.0),
        (0.48786139488220215, 4.5077928945147505e-08, 0.0),
    )

    def get_custom_shape(self, context: bpy.types.Context) -> object:
        """Get the appropriate custom shape based on lock state."""
        obj = context.active_object
        if not obj:
            return self.custom_shape_closed

        try:
            is_open = obj.path_resolve(self.prop_path)
            return self.custom_shape_open if is_open else self.custom_shape_closed
        except (ValueError, KeyError, AttributeError):
            return self.custom_shape_closed

    def setup(self) -> None:
        self.custom_shape_closed = self.new_custom_shape("TRIS", self.tris_closed)
        self.custom_shape_open = self.new_custom_shape("TRIS", self.tris_open)

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.get_custom_shape(context))

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.get_custom_shape(context), select_id=select_id)


class GizmoArc(bpy.types.Gizmo):
    """Reusable arc gizmo for door swing visualization."""

    bl_idname = "VIEW3D_GT_arc"

    __slots__ = (
        "custom_shape_left",
        "custom_shape_right",
        "prop_path",
    )

    def setup(self) -> None:
        """Create arc shapes for both LEFT and RIGHT directions."""
        arc_left = create_circle_arc(radius=1.0, direction="LEFT", angle_min=2.0, angle_max=90.0)
        arc_right = create_circle_arc(radius=1.0, direction="RIGHT", angle_min=2.0, angle_max=90.0)

        self.custom_shape_left = self.new_custom_shape(type="TRIS", verts=arc_left)
        self.custom_shape_right = self.new_custom_shape(type="TRIS", verts=arc_right)

    def _get_shape_for_direction(self, context: bpy.types.Context) -> object:
        """Get the appropriate arc shape based on door swing direction."""
        obj = context.active_object
        if not obj:
            return self.custom_shape_left

        try:
            direction_value = obj.path_resolve(self.prop_path)
            if "RIGHT" in str(direction_value):
                return self.custom_shape_right
        except (ValueError, KeyError, AttributeError):
            pass

        return self.custom_shape_left

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self._get_shape_for_direction(context))

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self._get_shape_for_direction(context), select_id=select_id)


class GizmoPen(bpy.types.Gizmo):
    """Reusable pen/edit icon gizmo for entering edit mode."""

    bl_idname = "VIEW3D_GT_pen"

    __slots__ = ("custom_shape",)

    tris = (
        (-0.07595771551132202, -0.2948460578918457, 0.0),
        (0.16886109113693237, 0.23203276097774506, 0.0),
        (0.062240585684776306, 0.28157487511634827, 0.0),
        (0.07201281189918518, 0.30260589718818665, 0.0),
        (0.21042980253696442, 0.321493536233902, 0.0),
        (0.17863331735134125, 0.25306373834609985, 0.0),
        (0.062240585684776306, 0.28157487511634827, 0.0),
        (-0.1825782209634781, -0.2453039139509201, 0.0),
        (-0.07595771551132202, -0.2948460578918457, 0.0),
        (-0.1825782209634781, -0.2453039139509201, 0.0),
        (-0.19114767014980316, -0.4032624065876007, 0.0),
        (-0.07595771551132202, -0.2948460578918457, 0.0),
        (0.07201281189918518, 0.30260589718818665, 0.0),
        (0.10380929708480835, 0.371035635471344, 0.0),
        (0.21042980253696442, 0.321493536233902, 0.0),
    )

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self.tris)

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


class GizmoValidate(bpy.types.Gizmo):
    """Reusable validate/checkmark icon gizmo for confirming edits."""

    bl_idname = "VIEW3D_GT_validate"

    __slots__ = ("custom_shape",)

    tris = (
        (0.36775994300842285, 0.205583393573761, 0.0),
        (0.030080009251832962, -0.1881658434867859, 0.0),
        (0.030080009251832962, -0.3380376696586609, 0.0),
        (-0.22017201781272888, -0.16090886294841766, 0.0),
        (0.030080009251832962, -0.1881658434867859, 0.0),
        (-0.22017201781272888, -0.011037036776542664, 0.0),
        (0.36775994300842285, 0.205583393573761, 0.0),
        (0.36775994300842285, 0.355455219745636, 0.0),
        (0.030080009251832962, -0.1881658434867859, 0.0),
        (-0.22017201781272888, -0.16090886294841766, 0.0),
        (0.030080009251832962, -0.3380376696586609, 0.0),
        (0.030080009251832962, -0.1881658434867859, 0.0),
    )

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self.tris)

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


class GizmoCancel(bpy.types.Gizmo):
    """Reusable cancel/X icon gizmo for canceling edits."""

    bl_idname = "VIEW3D_GT_cancel"

    __slots__ = ("custom_shape",)

    tris = (
        (0.0, 0.048707593232393265, 0.0),
        (0.0, -0.048707593232393265, 0.0),
        (0.048707593232393265, 0.0, 0.0),
        (0.0, 0.048707593232393265, 0.0),
        (-0.21918421983718872, 0.2678918242454529, 0.0),
        (-0.048707593232393265, 0.0, 0.0),
        (-0.21918421983718872, 0.2678918242454529, 0.0),
        (-0.2678918242454529, 0.21918421983718872, 0.0),
        (-0.048707593232393265, 0.0, 0.0),
        (-0.048707593232393265, 0.0, 0.0),
        (-0.2678918242454529, -0.21918421983718872, 0.0),
        (-0.21918421983718872, -0.2678918242454529, 0.0),
        (0.2678918242454529, 0.21918421983718872, 0.0),
        (0.21918421983718872, 0.2678918242454529, 0.0),
        (0.0, 0.048707593232393265, 0.0),
        (0.21918421983718872, -0.2678918242454529, 0.0),
        (0.2678918242454529, -0.21918421983718872, 0.0),
        (0.048707593232393265, 0.0, 0.0),
        (0.048707593232393265, 0.0, 0.0),
        (0.2678918242454529, 0.21918421983718872, 0.0),
        (0.0, 0.048707593232393265, 0.0),
        (0.0, 0.048707593232393265, 0.0),
        (-0.048707593232393265, 0.0, 0.0),
        (0.0, -0.048707593232393265, 0.0),
        (-0.048707593232393265, 0.0, 0.0),
        (-0.21918421983718872, -0.2678918242454529, 0.0),
        (0.0, -0.048707593232393265, 0.0),
        (0.0, -0.048707593232393265, 0.0),
        (0.21918421983718872, -0.2678918242454529, 0.0),
        (0.048707593232393265, 0.0, 0.0),
    )

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self.tris)

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


class GizmoPlus(bpy.types.Gizmo):
    """Reusable plus/+ icon gizmo for incrementing values."""

    bl_idname = "VIEW3D_GT_plus"

    __slots__ = ("custom_shape",)

    # Plus sign triangles (cross shape) - 50% larger
    tris = (
        # Horizontal bar
        (-0.375, -0.075, 0.0),
        (-0.375, 0.075, 0.0),
        (0.375, 0.075, 0.0),
        (-0.375, -0.075, 0.0),
        (0.375, 0.075, 0.0),
        (0.375, -0.075, 0.0),
        # Vertical bar
        (-0.075, -0.375, 0.0),
        (-0.075, 0.375, 0.0),
        (0.075, 0.375, 0.0),
        (-0.075, -0.375, 0.0),
        (0.075, 0.375, 0.0),
        (0.075, -0.375, 0.0),
    )

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self.tris)

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


class GizmoMinus(bpy.types.Gizmo):
    """Reusable minus/- icon gizmo for decrementing values."""

    bl_idname = "VIEW3D_GT_minus"

    __slots__ = ("custom_shape",)

    # Minus sign triangles (horizontal bar) - 50% larger
    tris = (
        (-0.375, -0.075, 0.0),
        (-0.375, 0.075, 0.0),
        (0.375, 0.075, 0.0),
        (-0.375, -0.075, 0.0),
        (0.375, 0.075, 0.0),
        (0.375, -0.075, 0.0),
    )

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self.tris)

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


def _generate_circular_arrow_tris() -> tuple[tuple[float, float, float], ...]:
    """Generate circular arrow geometry (↻ style) covering ~300 degrees."""
    triangles = []
    radius = 0.375  # 50% larger than original 0.25
    line_width = 0.06  # 50% larger than original 0.04
    half_width = line_width / 2

    # Arc from ~30 degrees to ~330 degrees (300 degree arc)
    segments = 20
    start_angle = math.radians(30)
    end_angle = math.radians(330)
    angle_range = end_angle - start_angle

    # Generate arc points
    arc_points = []
    for i in range(segments + 1):
        angle = start_angle + angle_range * (i / segments)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        arc_points.append((x, y))

    # Create triangles for the arc (flat ribbon in XY plane with Z thickness)
    for i in range(len(arc_points) - 1):
        x1, y1 = arc_points[i]
        x2, y2 = arc_points[i + 1]

        # Direction perpendicular to arc segment (for width in XY plane)
        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2) ** 0.5
        if length > 0:
            px, py = -dy / length * half_width, dx / length * half_width

            # XY plane triangles
            triangles.extend([
                (x1 + px, y1 + py, 0.0),
                (x1 - px, y1 - py, 0.0),
                (x2 + px, y2 + py, 0.0),
            ])
            triangles.extend([
                (x2 + px, y2 + py, 0.0),
                (x1 - px, y1 - py, 0.0),
                (x2 - px, y2 - py, 0.0),
            ])

            # XZ plane triangles (for visibility from other angles)
            triangles.extend([
                (x1, y1, -half_width),
                (x2, y2, -half_width),
                (x1, y1, +half_width),
            ])
            triangles.extend([
                (x1, y1, +half_width),
                (x2, y2, -half_width),
                (x2, y2, +half_width),
            ])

    # Arrowhead at the end of the arc (pointing in direction of cycling)
    arrow_size = 0.18  # 50% larger than original 0.12
    end_x, end_y = arc_points[-1]
    # Direction tangent to the arc at the end
    prev_x, prev_y = arc_points[-2]
    tangent_x = end_x - prev_x
    tangent_y = end_y - prev_y
    tangent_len = (tangent_x**2 + tangent_y**2) ** 0.5
    if tangent_len > 0:
        tangent_x /= tangent_len
        tangent_y /= tangent_len

    # Arrow tip extends in the tangent direction
    tip_x = end_x + tangent_x * arrow_size * 0.5
    tip_y = end_y + tangent_y * arrow_size * 0.5

    # Arrow base perpendicular to tangent
    perp_x = -tangent_y * arrow_size
    perp_y = tangent_x * arrow_size

    # Arrowhead triangle (XY plane)
    triangles.extend([
        (tip_x, tip_y, 0.0),
        (end_x - perp_x * 0.5, end_y - perp_y * 0.5, 0.0),
        (end_x + perp_x * 0.5, end_y + perp_y * 0.5, 0.0),
    ])

    # Arrowhead triangle (XZ plane for depth)
    triangles.extend([
        (tip_x, tip_y, 0.0),
        (end_x, end_y, -arrow_size * 0.5),
        (end_x, end_y, +arrow_size * 0.5),
    ])

    return tuple(triangles)


class GizmoCycle(bpy.types.Gizmo):
    """Reusable circular arrow icon gizmo for cycling through enum values."""

    bl_idname = "VIEW3D_GT_cycle"

    __slots__ = ("custom_shape",)

    tris = _generate_circular_arrow_tris()

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self.tris)

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


class GizmoArrow(GizmoMovable):
    """Arrow gizmo for directional value editing."""

    bl_idname = "BIM_GT_gizmo_arrow"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    def _get_arrow_triangles(self) -> tuple[tuple[float, float, float], ...]:
        """Generate arrow geometry along +X axis."""
        triangles = []

        triangles.extend(
            [
                (0, -ARROW_WIDTH, 0),
                (ARROW_SHAFT_LENGTH, -ARROW_WIDTH, 0),
                (0, +ARROW_WIDTH, 0),
            ]
        )
        triangles.extend(
            [
                (0, +ARROW_WIDTH, 0),
                (ARROW_SHAFT_LENGTH, -ARROW_WIDTH, 0),
                (ARROW_SHAFT_LENGTH, +ARROW_WIDTH, 0),
            ]
        )

        triangles.extend(
            [
                (0, 0, -ARROW_WIDTH),
                (ARROW_SHAFT_LENGTH, 0, -ARROW_WIDTH),
                (0, 0, +ARROW_WIDTH),
            ]
        )
        triangles.extend(
            [
                (0, 0, +ARROW_WIDTH),
                (ARROW_SHAFT_LENGTH, 0, -ARROW_WIDTH),
                (ARROW_SHAFT_LENGTH, 0, +ARROW_WIDTH),
            ]
        )

        head_width = ARROW_WIDTH * ARROW_HEAD_WIDTH_MULTIPLIER
        triangles.extend(
            [
                (ARROW_SHAFT_LENGTH, -head_width, 0),
                (ARROW_SHAFT_LENGTH + ARROW_HEAD_LENGTH, 0, 0),
                (ARROW_SHAFT_LENGTH, +head_width, 0),
            ]
        )

        triangles.extend(
            [
                (ARROW_SHAFT_LENGTH, 0, -head_width),
                (ARROW_SHAFT_LENGTH + ARROW_HEAD_LENGTH, 0, 0),
                (ARROW_SHAFT_LENGTH, 0, +head_width),
            ]
        )

        for i in range(ARROW_CIRCLE_SEGMENTS):
            angle1 = (2 * math.pi * i) / ARROW_CIRCLE_SEGMENTS
            angle2 = (2 * math.pi * (i + 1)) / ARROW_CIRCLE_SEGMENTS

            y1 = head_width * math.cos(angle1)
            z1 = head_width * math.sin(angle1)
            y2 = head_width * math.cos(angle2)
            z2 = head_width * math.sin(angle2)

            triangles.extend(
                [
                    (ARROW_SHAFT_LENGTH, 0, 0),
                    (ARROW_SHAFT_LENGTH, y1, z1),
                    (ARROW_SHAFT_LENGTH, y2, z2),
                ]
            )

        return tuple(triangles)

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self._get_arrow_triangles())

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


class GizmoCone(GizmoMovable):
    """Cone gizmo for directional value editing with local axis support."""

    bl_idname = "BIM_GT_gizmo_cone"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    def get_axis_direction(self) -> Vector:
        if hasattr(self, "local_axis") and self.active_obj:
            obj_rotation = self.active_obj.matrix_world.to_3x3()
            axis_direction = obj_rotation @ self.local_axis
            axis_direction.normalize()
            return axis_direction
        return self.axis

    def _get_cone_triangles(self) -> tuple[tuple[float, float, float], ...]:
        """Generate cone geometry along +X axis."""
        triangles = []
        cone_tip_x = CONE_LENGTH

        for i in range(CONE_SEGMENTS):
            angle1 = (2 * math.pi * i) / CONE_SEGMENTS
            angle2 = (2 * math.pi * (i + 1)) / CONE_SEGMENTS

            y1 = CONE_RADIUS * math.cos(angle1)
            z1 = CONE_RADIUS * math.sin(angle1)
            y2 = CONE_RADIUS * math.cos(angle2)
            z2 = CONE_RADIUS * math.sin(angle2)

            triangles.extend(
                [
                    (cone_tip_x, 0, 0),
                    (0, y1, z1),
                    (0, y2, z2),
                ]
            )

            triangles.extend(
                [
                    (0, 0, 0),
                    (0, y2, z2),
                    (0, y1, z1),
                ]
            )

        return tuple(triangles)

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self._get_cone_triangles())

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


class BaseParametricGizmoGroup:
    """Base mixin class for parametric element gizmo groups (doors, windows, etc.).

    This class provides shared functionality for gizmo groups that edit
    parametric BIM elements. Subclasses should define:
    - gizmo_props: list of property configurations
    - get_props(obj): method to get the element's properties
    - get_gizmo_prefs(): method to get gizmo preferences
    - element_type_check(element): method to check if element is the right type
    - Operator bl_idnames for enable_editing, finish_editing, cancel_editing

    Example subclass:
        class GizmoDoorEdition(bpy.types.GizmoGroup, BaseParametricGizmoGroup):
            bl_idname = "OBJECT_GGT_bim_door_edition"
            ...
    """

    COLOR_RED = (1.0, 0.2, 0.2)
    COLOR_GREEN = (0.1, 0.8, 0.1)
    COLOR_BLUE = (0.2, 0.2, 1.0)
    ARROW_SCALE = 0.25

    # Subclasses must define these
    gizmo_props: list[GizmoPropConfig] = []
    enable_editing_operator: str = ""
    finish_editing_operator: str = ""
    cancel_editing_operator: str = ""

    @classmethod
    def get_arrow_color_from_axis(cls, axis: tuple[int, int, int]) -> tuple[float, float, float]:
        """Get arrow color based on axis direction (X=red, Y=green, Z=blue)."""
        if axis[0] != 0:
            return cls.COLOR_RED
        elif axis[1] != 0:
            return cls.COLOR_GREEN
        return cls.COLOR_BLUE

    def get_axis_rotation_matrix(self, axis: tuple[int, int, int]) -> Matrix:
        """Get rotation matrix to align arrow with the given axis."""
        axis_vec = Vector(axis).normalized()
        default_dir = Vector((1, 0, 0))
        return default_dir.rotation_difference(axis_vec).to_matrix().to_4x4()

    @classmethod
    def is_element_type(cls, element) -> bool:
        """Check if the element is of the correct type. Must be overridden by subclass."""
        raise NotImplementedError("Subclass must implement is_element_type()")

    @classmethod
    def poll(cls, context) -> bool:
        """Show gizmo only when a single element of the correct type is selected and active."""
        prefs = tool.Blender.get_addon_preferences()
        if not prefs.gizmos.draw_gizmos_in_3d_viewport:
            return False

        obj = tool.Blender.get_active_object(is_selected=True)
        if not obj:
            return False

        if len(tool.Blender.get_selected_objects()) != 1:
            return False

        element = tool.Ifc.get_entity(obj)
        if not element or not cls.is_element_type(element):
            return False
        return True

    def get_props(self, obj: bpy.types.Object) -> Any:
        """Get properties for the element. Must be overridden by subclass."""
        raise NotImplementedError("Subclass must implement get_props()")

    def get_gizmo_prefs(self) -> Any:
        """Get gizmo preferences for this element type. Must be overridden by subclass."""
        raise NotImplementedError("Subclass must implement get_gizmo_prefs()")

    def get_prop_min_value(self, attr_name: str) -> float:
        """Get minimum value for a property. Override to customize."""
        return 0.0

    def should_hide_gizmo(self, attr_name: str, props) -> bool:
        """Check if a specific gizmo should be hidden. Override to add visibility rules."""
        return not props.is_editing

    def get_element_height(self, props) -> float:
        """Get the element height for icon positioning. Override if property name differs."""
        return getattr(props, "overall_height", getattr(props, "height", 1.0))

    def setup_property_gizmos(self, context: bpy.types.Context) -> None:
        """Set up gizmos for all properties in gizmo_props."""
        prefs = tool.Blender.get_addon_preferences()
        highlight_color = prefs.decorator_color_selected[:3]

        for prop_config in self.gizmo_props:
            attr_name = prop_config.attr_name
            invert_delta = prop_config.invert_delta
            gizmo = self.gizmos.new("BIM_GT_gizmo_cone")

            # Create closures that capture attr_name
            def make_move_get(name):
                def move_get():
                    obj = bpy.context.active_object
                    if not obj:
                        return 0.0
                    props = self.get_props(obj)
                    return getattr(props, name)

                return move_get

            def make_move_set(name):
                def move_set(value):
                    obj = bpy.context.active_object
                    if not obj:
                        return
                    props = self.get_props(obj)
                    min_val = self.get_prop_min_value(name)
                    setattr(props, name, max(min_val, value))

                return move_set

            gizmo.move_get_cb = make_move_get(attr_name)
            gizmo.move_set_cb = make_move_set(attr_name)
            gizmo.axis = Vector(prop_config.axis)
            gizmo.local_axis = Vector(prop_config.axis)
            gizmo.invert_delta = invert_delta

            gizmo.color = self.get_arrow_color_from_axis(prop_config.axis)
            gizmo.color_highlight = highlight_color
            gizmo.alpha = 0.99
            gizmo.use_draw_modal = True
            gizmo.use_draw_scale = True

            setattr(self, f"gizmo_{attr_name}", gizmo)

    def setup_editing_gizmos(self, context: bpy.types.Context) -> None:
        """Set up pen, validate, and cancel gizmos for editing mode."""
        prefs = tool.Blender.get_addon_preferences()
        default_color = prefs.decorations_colour[:3]
        highlight_color = prefs.decorator_color_selected[:3]

        self.pen_gizmo = self.gizmos.new("VIEW3D_GT_pen")
        self.pen_gizmo.use_draw_scale = False
        self.pen_gizmo.color = default_color
        self.pen_gizmo.color_highlight = highlight_color
        self.pen_gizmo.alpha = 0.8
        self.pen_gizmo.target_set_operator(self.enable_editing_operator)

        self.validate_gizmo = self.gizmos.new("VIEW3D_GT_validate")
        self.validate_gizmo.use_draw_scale = False
        self.validate_gizmo.color = self.COLOR_GREEN
        self.validate_gizmo.color_highlight = highlight_color
        self.validate_gizmo.alpha = 0.8
        self.validate_gizmo.target_set_operator(self.finish_editing_operator)

        self.cancel_gizmo = self.gizmos.new("VIEW3D_GT_cancel")
        self.cancel_gizmo.use_draw_scale = False
        self.cancel_gizmo.color = self.COLOR_RED
        self.cancel_gizmo.color_highlight = highlight_color
        self.cancel_gizmo.alpha = 0.8
        self.cancel_gizmo.target_set_operator(self.cancel_editing_operator)

    def update_property_gizmos(self, mw, props) -> None:
        """Update arrow gizmos position and visibility based on editing state."""
        gizmo_prefs = self.get_gizmo_prefs()

        for prop_config in self.gizmo_props:
            attr_name = prop_config.attr_name
            gizmo = getattr(self, f"gizmo_{attr_name}", None)
            if gizmo is None:
                continue

            # Check preferences
            if not getattr(gizmo_prefs, attr_name, True):
                gizmo.hide = True
                continue

            # Check visibility rules
            if self.should_hide_gizmo(attr_name, props):
                gizmo.hide = True
                continue

            # Update position and show arrow
            gizmo.hide = False
            matrix_method = getattr(self, f"get_gizmo_matrix_{attr_name}", None)
            if matrix_method:
                gizmo.matrix_basis = mw @ matrix_method(props)
            gizmo.matrix_offset = Matrix.Scale(self.ARROW_SCALE, 4)

    def update_editing_gizmos(self, mw, props) -> None:
        """Update editing control gizmos (pen/validate/cancel) visibility and position."""
        icon_z = self.get_element_height(props) + 0.5
        local_transform = (
            Matrix.Translation(Vector((0, 0.0, icon_z)))
            @ Matrix.Rotation(math.radians(90), 4, (1.0, 0.0, 0.0))
            @ Matrix.Scale(0.5, 4)
        )
        icon_matrix_base = mw @ local_transform

        if props.is_editing:
            self.pen_gizmo.hide = True
            self.validate_gizmo.hide = False
            self.validate_gizmo.matrix_basis = icon_matrix_base
            self.cancel_gizmo.hide = False
            cancel_local = Matrix.Translation(Vector((0.5, 0.0, 0.0))) @ local_transform
            self.cancel_gizmo.matrix_basis = mw @ cancel_local
        else:
            self.pen_gizmo.hide = False
            self.pen_gizmo.matrix_basis = icon_matrix_base
            self.validate_gizmo.hide = True
            self.cancel_gizmo.hide = True
