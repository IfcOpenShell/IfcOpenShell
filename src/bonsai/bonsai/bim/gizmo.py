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
    "NumericInputState",
    # Functions
    "set_snap_point",
    "clear_snap_point",
    "snap_to_mesh",
    "build_snap_cache",
    "clear_snap_cache",
    "get_billboard_rotation",
    "get_camera_direction",
    "generate_circle_vertices",
    "create_circle_arc",
    # Operators
    "BIM_OT_gizmo_value_input",
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
    "GizmoArrow2D",
    "GizmoCone",
    # Mixin classes
    "BaseParametricGizmoGroup",
]

from typing import Any

import bpy
import math
import numpy as np
from dataclasses import dataclass
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_line_line
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
import gpu
from gpu_extras.batch import batch_for_shader
import bonsai.tool as tool
from bonsai.tool.unit import parse_distance_string


SNAP_POINT_SIZE = 10.0
SNAP_POINT_COLOR = (1.0, 0.5, 0.0, 1.0)
SNAP_MAX_RADIUS = 5.0
SNAP_SCREEN_DISTANCE = 15  # Maximum screen-space distance for snapping (in pixels)
SNAP_WORLD_DISTANCE = 0.2  # Maximum world-space distance for snapping (in meters)
SNAP_KD_CANDIDATES = 16  # Number of KD-tree candidates (3D nearest may differ from screen nearest)

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

# Characters allowed for keyboard numeric input (supports units and formulas)
_DIGITS = set("0123456789")
_OPERATORS = {".", "-", "+", "*", "/"}
_METRIC_UNITS = {"m", "c", "d"}  # m, cm, dm, mm
_IMPERIAL_UNITS = {"f", "t", "i", "n", "'", '"'}  # ft, in, ', "
_SPECIAL = {"=", " "}  # Formula prefix, spaces

NUMERIC_INPUT_CHARS = _DIGITS | _OPERATORS | _METRIC_UNITS | _IMPERIAL_UNITS | _SPECIAL

# Module-level storage for gizmo callback (Blender ID properties don't support functions)
_gizmo_value_input_callback: dict[str, Any] = {}


@dataclass
class SnapCache:
    """Unified snap cache with combined KD-tree for vertex snapping."""

    # Combined KD-tree with all world vertices from all objects
    kd_tree: KDTree
    # All world vertices indexed by global vertex index
    all_vertices: list[Vector]


@dataclass
class NumericInputState:
    """State for keyboard numeric input during gizmo operations."""

    characters: list[str]
    parsed_value: float
    is_active: bool
    is_valid: bool

    @classmethod
    def create_default(cls) -> "NumericInputState":
        return cls(characters=[], parsed_value=0.0, is_active=False, is_valid=True)

    def reset(self) -> None:
        self.characters.clear()
        self.parsed_value = 0.0
        self.is_active = False
        self.is_valid = True

    def get_input_string(self) -> str:
        return "".join(self.characters)

    def is_relative_mode(self) -> bool:
        input_str = self.get_input_string()
        return input_str.startswith("+") or input_str.startswith("-")

    def calculate_final_value(self, init_value: float, invert_delta: bool = False) -> float:
        if self.is_relative_mode():
            delta = self.parsed_value
            if invert_delta:
                delta = -delta
            return init_value + delta
        return self.parsed_value

    def parse(self) -> None:
        """Parse the current input string and update parsed_value and is_valid."""
        if not self.characters:
            self.parsed_value = 0.0
            self.is_valid = True
            return

        input_str = self.get_input_string()
        is_valid, value = parse_distance_string(input_str)

        if is_valid:
            self.parsed_value = value
            self.is_valid = True
        else:
            try:
                self.parsed_value = float(input_str)
                self.is_valid = True
            except ValueError:
                self.parsed_value = 0.0
                self.is_valid = False


@dataclass
class GizmoPropConfig:
    """Configuration for a gizmo property."""

    attr_name: str
    axis: tuple[int, int, int]
    invert_delta: bool = False
    delta_scale: float = 1.0  # Multiplier for the delta (e.g., 2.0 for symmetric thickness properties)


class SnapManager:
    """Manages snap point visualization and mesh snapping with caching."""

    def __init__(self):
        self._snap_point: tuple[float, float, float] | Vector | None = None
        self._draw_handler = None
        self._shader = None
        self._snap_cache: SnapCache | None = None

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

    def build_snap_cache(self, context: bpy.types.Context, active_obj: bpy.types.Object) -> None:
        """Build unified cache with combined KD-tree for vertex snapping.

        Uses foreach_get for fast vertex data extraction and NumPy for
        batch matrix transformation.
        """
        self._snap_cache = None

        mesh_objects = [
            obj for obj in context.visible_objects
            if obj.type == "MESH" and obj != active_obj and obj.visible_get()
        ]

        if not mesh_objects:
            return

        depsgraph = context.evaluated_depsgraph_get()
        all_vertices: list[Vector] = []

        for obj in mesh_objects:
            mesh_data = obj.data
            if not hasattr(mesh_data, "vertices") or not mesh_data.vertices:
                continue

            obj_eval = obj.evaluated_get(depsgraph)
            mesh = obj_eval.to_mesh()

            try:
                vertex_count = len(mesh.vertices)
                if vertex_count == 0:
                    continue

                coords = np.empty(vertex_count * 3, dtype=np.float32)
                mesh.vertices.foreach_get("co", coords)  # type: ignore[arg-type]
                coords = coords.reshape(-1, 3)

                matrix = np.array(obj_eval.matrix_world, dtype=np.float32)
                ones = np.ones((vertex_count, 1), dtype=np.float32)
                coords_h = np.hstack([coords, ones])
                world_coords = (coords_h @ matrix.T)[:, :3]

                all_vertices.extend(Vector(co) for co in world_coords)
            finally:
                obj_eval.to_mesh_clear()

        if not all_vertices:
            return

        kd_tree = KDTree(len(all_vertices))
        for i, v in enumerate(all_vertices):
            kd_tree.insert(v, i)
        kd_tree.balance()

        self._snap_cache = SnapCache(
            kd_tree=kd_tree,
            all_vertices=all_vertices,
        )

    def clear_snap_cache(self) -> None:
        self._snap_cache = None

    @staticmethod
    def _calc_snap_distance_sq(
        point_3d: Vector,
        location: Vector,
        mouse_vec: Vector | None,
        region: bpy.types.Region | None,
        rv3d: bpy.types.RegionView3D | None,
    ) -> float:
        """Calculate squared distance - screen-space if mouse coords available, else world-space."""
        if mouse_vec is not None and region is not None and rv3d is not None:
            point_2d = location_3d_to_region_2d(region, rv3d, point_3d)
            if point_2d is not None:
                return (mouse_vec - point_2d).length_squared
            return float("inf")
        return (point_3d - location).length_squared

    @staticmethod
    def _find_closest_vertex(
        world_vertices: list[Vector],
        location: Vector,
        mouse_vec: Vector | None,
        region: bpy.types.Region | None,
        rv3d: bpy.types.RegionView3D | None,
        closest_point: Vector | None,
        closest_dist_sq: float,
        kd_tree: KDTree | None = None,
    ) -> tuple[Vector | None, float]:
        """Find the closest vertex to snap to using KD-tree if available."""
        if kd_tree is not None:
            for _, idx, _ in kd_tree.find_n(location, SNAP_KD_CANDIDATES):
                v_co = world_vertices[idx]
                dist_sq = SnapManager._calc_snap_distance_sq(v_co, location, mouse_vec, region, rv3d)
                if dist_sq < closest_dist_sq:
                    closest_dist_sq = dist_sq
                    closest_point = v_co
        else:
            for v_co in world_vertices:
                dist_sq = SnapManager._calc_snap_distance_sq(v_co, location, mouse_vec, region, rv3d)
                if dist_sq < closest_dist_sq:
                    closest_dist_sq = dist_sq
                    closest_point = v_co
        return closest_point, closest_dist_sq

    @staticmethod
    def _get_nearby_objects(
        mesh_objects: list[bpy.types.Object],
        location: Vector,
    ) -> list[bpy.types.Object]:
        """Filter objects to those within SNAP_MAX_RADIUS of location."""
        radius_sq = SNAP_MAX_RADIUS * SNAP_MAX_RADIUS
        nearby_objects = []

        for obj in mesh_objects:
            bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            if not bbox_corners:
                continue

            bbox_min = Vector((
                min(c.x for c in bbox_corners),
                min(c.y for c in bbox_corners),
                min(c.z for c in bbox_corners),
            ))
            bbox_max = Vector((
                max(c.x for c in bbox_corners),
                max(c.y for c in bbox_corners),
                max(c.z for c in bbox_corners),
            ))

            closest = Vector((
                max(bbox_min.x, min(location.x, bbox_max.x)),
                max(bbox_min.y, min(location.y, bbox_max.y)),
                max(bbox_min.z, min(location.z, bbox_max.z)),
            ))

            if (location - closest).length_squared <= radius_sq:
                nearby_objects.append(obj)

        return nearby_objects

    def snap_to_mesh(
        self,
        location: Vector,
        context: bpy.types.Context,
        active_obj: bpy.types.Object,
        mouse_coords: tuple[float, float] | None = None,
    ) -> Vector:
        """Snap a location to the nearest vertex if snapping is enabled.

        Only vertex snapping is supported. Returns the original location if
        snapping is disabled or VERTEX is not in the snap elements.
        """
        tool_settings = context.scene.tool_settings

        if not tool_settings.use_snap:
            return location

        if "VERTEX" not in tool_settings.snap_elements_base:
            return location

        region = context.region
        rv3d = context.region_data
        use_screen_distance = mouse_coords is not None and region is not None and rv3d is not None
        mouse_vec = Vector(mouse_coords) if mouse_coords is not None else None

        closest_point: Vector | None = None
        closest_dist_sq = float("inf")

        if self._snap_cache is not None:
            closest_point, closest_dist_sq = self._snap_from_cache(
                location, mouse_vec, region, rv3d
            )
        else:
            closest_point, closest_dist_sq = self._snap_without_cache(
                location, context, active_obj, mouse_vec, region, rv3d
            )

        max_dist_sq = SNAP_SCREEN_DISTANCE ** 2 if use_screen_distance else SNAP_WORLD_DISTANCE ** 2
        if closest_point and closest_dist_sq < max_dist_sq:
            return closest_point

        return location

    def _snap_from_cache(
        self,
        location: Vector,
        mouse_vec: Vector | None,
        region: bpy.types.Region | None,
        rv3d: bpy.types.RegionView3D | None,
    ) -> tuple[Vector | None, float]:
        """Find closest vertex using cached KD-tree."""
        if self._snap_cache is None:
            return None, float("inf")

        cache = self._snap_cache
        return SnapManager._find_closest_vertex(
            cache.all_vertices, location, mouse_vec, region, rv3d,
            None, float("inf"), cache.kd_tree
        )

    def _snap_without_cache(
        self,
        location: Vector,
        context: bpy.types.Context,
        active_obj: bpy.types.Object,
        mouse_vec: Vector | None,
        region: bpy.types.Region | None,
        rv3d: bpy.types.RegionView3D | None,
    ) -> tuple[Vector | None, float]:
        """Find closest vertex without cache (fallback path)."""
        mesh_objects = [
            obj for obj in context.visible_objects
            if obj.type == "MESH" and obj != active_obj and obj.visible_get()
        ]

        if not mesh_objects:
            return None, float("inf")

        nearby_objects = SnapManager._get_nearby_objects(mesh_objects, location)
        if not nearby_objects:
            return None, float("inf")

        closest_point: Vector | None = None
        closest_dist_sq = float("inf")
        depsgraph = context.evaluated_depsgraph_get()

        for obj in nearby_objects:
            mesh_data = obj.data
            if not hasattr(mesh_data, "vertices") or not mesh_data.vertices:
                continue

            obj_eval = obj.evaluated_get(depsgraph)
            mesh = obj_eval.to_mesh()

            try:
                if not mesh or not mesh.vertices:
                    continue

                world_vertices = [obj_eval.matrix_world @ v.co for v in mesh.vertices]
                closest_point, closest_dist_sq = SnapManager._find_closest_vertex(
                    world_vertices, location, mouse_vec, region, rv3d,
                    closest_point, closest_dist_sq
                )
            finally:
                obj_eval.to_mesh_clear()

        return closest_point, closest_dist_sq


_snap_manager = SnapManager()


def set_snap_point(point: tuple[float, float, float] | Vector | None) -> None:
    _snap_manager.set_snap_point(point)


def clear_snap_point() -> None:
    _snap_manager.clear()


def snap_to_mesh(
    location: Vector,
    context: bpy.types.Context,
    active_obj: bpy.types.Object,
    mouse_coords: tuple[float, float] | None = None,
) -> Vector:
    return _snap_manager.snap_to_mesh(location, context, active_obj, mouse_coords)


def build_snap_cache(context: bpy.types.Context, active_obj: bpy.types.Object) -> None:
    _snap_manager.build_snap_cache(context, active_obj)


def clear_snap_cache() -> None:
    _snap_manager.clear_snap_cache()


def get_billboard_rotation(context: bpy.types.Context) -> Matrix:
    """Get rotation matrix that makes an object face the camera."""
    rv3d = context.region_data
    if rv3d is None:
        return Matrix.Identity(4)
    return rv3d.view_matrix.to_3x3().transposed().to_4x4()


def get_camera_direction(context: bpy.types.Context, position: Vector) -> Vector | None:
    """Get normalized direction from position towards camera."""
    rv3d = context.region_data
    if rv3d is None:
        return None

    if rv3d.is_perspective:
        view_origin = rv3d.view_matrix.inverted().translation
        return (view_origin - position).normalized()
    return Vector(rv3d.view_matrix.inverted().col[2][:3]).normalized()


def generate_circle_vertices(
    center: tuple[float, float, float] | Vector, radius: float, segments: int, plane: str = "XY"
) -> list[tuple[float, float, float]]:
    """Generate circle vertices in specified plane ('XY', 'XZ', or 'YZ')."""
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
    """Create a circle arc with cross-section thickness for visibility from all angles."""
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


class BIM_OT_gizmo_value_input(bpy.types.Operator):
    """Enter a numeric value for a gizmo property. Click or Enter to confirm, ESC to cancel."""

    bl_idname = "bim.gizmo_value_input"
    bl_label = "Gizmo Value Input"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    prop_name: bpy.props.StringProperty(name="Property Name", default="Value")
    init_value: bpy.props.FloatProperty(name="Initial Value", default=0.0)
    invert_delta: bpy.props.BoolProperty(name="Invert Delta", default=False)

    def invoke(self, context, event):
        self._keyboard_input = NumericInputState.create_default()
        self._move_set_cb = _gizmo_value_input_callback.get("move_set_cb")
        self._active_gizmo = _gizmo_value_input_callback.get("active_gizmo")
        self._gizmo_group = _gizmo_value_input_callback.get("gizmo_group")
        self._hidden_gizmos: list[bpy.types.Gizmo] = []
        self._original_color: tuple[float, float, float] | None = None

        # Mouse movement context
        self._start_location: Vector = _gizmo_value_input_callback.get("start_location", Vector())
        self._axis_direction: Vector = _gizmo_value_input_callback.get("axis_direction", Vector((0, 0, 1)))
        self._active_obj: bpy.types.Object | None = _gizmo_value_input_callback.get("active_obj")
        self._delta_scale: float = _gizmo_value_input_callback.get("delta_scale", 1.0)
        self._mouse_delta: float = 0.0

        # Snapping state
        self._initial_snap_state: bool = context.scene.tool_settings.use_snap
        self._snap_cache_built: bool = False
        self._is_snapping: bool = False

        self._hide_other_gizmos()
        self._set_highlight_color()

        context.window_manager.modal_handler_add(self)
        self._update_header(context)
        return {"RUNNING_MODAL"}

    def _set_highlight_color(self) -> None:
        if not self._active_gizmo:
            return
        self._original_color = tuple(self._active_gizmo.color)
        self._active_gizmo.color = self._active_gizmo.color_highlight

    def _restore_color(self) -> None:
        if self._active_gizmo and self._original_color:
            self._active_gizmo.color = self._original_color

    def _hide_other_gizmos(self) -> None:
        if not self._gizmo_group or not self._active_gizmo:
            return

        # Store hidden gizmos so update_property_gizmos respects it.
        hidden_set: set[bpy.types.Gizmo] = set()
        for gizmo in self._gizmo_group.gizmos:
            if gizmo != self._active_gizmo:
                gizmo.hide = True
                hidden_set.add(gizmo)
                self._hidden_gizmos.append(gizmo)

        # Store in module-level dict so gizmo group methods can check it
        _gizmo_value_input_callback["hidden_gizmos"] = hidden_set

    def _restore_gizmo_visibility(self) -> None:
        # Clear the hidden set first so refresh doesn't re-hide.
        _gizmo_value_input_callback.pop("hidden_gizmos", None)
        for gizmo in self._hidden_gizmos:
            gizmo.hide = False
        self._hidden_gizmos.clear()

    def modal(self, context, event):
        kb = self._keyboard_input

        # Character input
        if event.value == "PRESS" and event.ascii and event.ascii.lower() in NUMERIC_INPUT_CHARS:
            kb.characters.append(event.ascii)
            kb.is_active = True
            kb.parse()
            self._apply_value()
            self._update_header(context)
            return {"RUNNING_MODAL"}

        if event.type == "BACK_SPACE" and event.value == "PRESS":
            if kb.characters:
                kb.characters.pop()
                kb.parse()
                self._apply_value()
                self._update_header(context)
            return {"RUNNING_MODAL"}

        if event.type in {"RET", "NUMPAD_ENTER"} and event.value == "PRESS":
            if kb.is_valid:
                self._apply_value()
            self._cleanup(context)
            return {"FINISHED"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            if kb.characters:
                if kb.is_valid:
                    self._apply_value()
                self._cleanup(context)
                return {"FINISHED"}
            self._cleanup(context)
            return {"CANCELLED"}

        if event.type == "ESC" and event.value == "PRESS":
            if self._move_set_cb:
                self._move_set_cb(self.init_value)
            self._cleanup(context)
            return {"CANCELLED"}

        if event.type == "RIGHTMOUSE" and event.value == "PRESS":
            if self._move_set_cb:
                self._move_set_cb(self.init_value)
            self._cleanup(context)
            return {"CANCELLED"}

        # Mouse movement - only when not typing
        if event.type == "MOUSEMOVE" and not kb.characters:
            self._handle_mouse_move(context, event)
            return {"RUNNING_MODAL"}

        return {"RUNNING_MODAL"}

    def _handle_mouse_move(self, context, event) -> None:
        region = context.region
        rv3d = context.region_data
        tool_settings = context.scene.tool_settings
        if not region or not rv3d:
            return

        # Ctrl toggles snapping
        self._is_snapping = not self._initial_snap_state if event.ctrl else self._initial_snap_state

        # Build snap cache lazily on first Ctrl press
        if self._is_snapping and not self._snap_cache_built and self._active_obj:
            build_snap_cache(context, self._active_obj)
            self._snap_cache_built = True

        current_coord = (event.mouse_region_x, event.mouse_region_y)
        view_origin = region_2d_to_origin_3d(region, rv3d, current_coord)
        view_direction = region_2d_to_vector_3d(region, rv3d, current_coord)

        result = intersect_line_line(
            view_origin,
            view_origin + view_direction * RAY_CAST_DISTANCE,
            self._start_location,
            self._start_location + self._axis_direction * RAY_CAST_DISTANCE,
        )
        current_3d = result[1] if result else self._start_location

        delta = (current_3d - self._start_location).dot(self._axis_direction)

        # Snapping
        if self._is_snapping and self._active_obj:
            # Temporarily set tool_settings for snap_to_mesh
            original_snap = tool_settings.use_snap
            tool_settings.use_snap = True
            snapped_pos = snap_to_mesh(current_3d, context, self._active_obj, current_coord)
            tool_settings.use_snap = original_snap
            if snapped_pos != current_3d:
                delta = (snapped_pos - self._start_location).dot(self._axis_direction)
                set_snap_point(snapped_pos)
            else:
                clear_snap_point()
        else:
            clear_snap_point()

        # Precision mode with Shift
        if event.shift:
            delta *= PRECISION_MODE_MULTIPLIER

        if self.invert_delta:
            delta = -delta

        delta *= self._delta_scale
        self._mouse_delta = delta

        if self._move_set_cb:
            self._move_set_cb(self.init_value + delta)

        self._update_header(context)

    def _apply_value(self) -> None:
        if not self._move_set_cb or not self._keyboard_input.is_valid:
            return
        final_value = self._keyboard_input.calculate_final_value(self.init_value, self.invert_delta)
        self._move_set_cb(final_value)

    def _update_header(self, context) -> None:
        if not context.area:
            return
        kb = self._keyboard_input

        if kb.characters:
            # Typing mode - show keyboard input
            input_str = kb.get_input_string()
            preview = kb.calculate_final_value(self.init_value, self.invert_delta)
            validity = "" if kb.is_valid else " [invalid]"
            header = f"{self.prop_name}: {preview:.3f}m  |  Input: {input_str}_{validity}"
            header += "  |  Click/Enter: Confirm  |  ESC: Cancel"
        else:
            # Mouse mode - show current value from mouse delta
            current_value = self.init_value + self._mouse_delta
            header = f"{self.prop_name}: {current_value:.3f}m"
            hints = []
            if self._is_snapping:
                hints.append("Snapping: ON")
            hints.extend(["Ctrl: Snap", "Shift: Precision", "Type: Enter Value"])
            header += "  |  " + "  |  ".join(hints)
            header += "  |  Click/Enter: Confirm  |  ESC: Cancel"

        context.area.header_text_set(header)

    def _cleanup(self, context) -> None:
        try:
            if context.area:
                context.area.header_text_set(None)
        finally:
            try:
                self._restore_color()
            finally:
                try:
                    self._restore_gizmo_visibility()
                    # Trigger gizmo group refresh to recalculate positions based on new values
                    if self._gizmo_group and hasattr(self._gizmo_group, "refresh"):
                        self._gizmo_group.refresh(context)
                    # Force viewport redraw to update gizmo display
                    if context.area:
                        context.area.tag_redraw()
                finally:
                    clear_snap_point()
                    clear_snap_cache()
                    _gizmo_value_input_callback.clear()


class GizmoMovable(bpy.types.Gizmo):
    """Base class for draggable gizmos. Ctrl: snap, Shift: precision, Keyboard: direct input.

    Click without dragging enters a keyboard-only input mode for accessibility.
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
        "delta_scale",
        "prop_name",
        "keyboard_input",
        "gizmo_group",
        "_snap_cache_built",
        "_start_mouse_pos",
        "_has_dragged",
    )

    # Threshold in pixels for considering mouse movement as a drag
    DRAG_THRESHOLD = 5

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set:
        self.init_value = self.move_get_cb() if self.move_get_cb else 0.0
        self.start_location = self.matrix_basis.translation.copy()
        self.active_obj = context.active_object
        self.initial_snap_state = context.scene.tool_settings.use_snap
        self.keyboard_input = NumericInputState.create_default()
        self._snap_cache_built = False
        self._start_mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self._has_dragged = False
        if not hasattr(self, "prop_name") or self.prop_name is None:
            self.prop_name = "Value"
        # Build cache immediately only if snap is already enabled
        if self.initial_snap_state and self.active_obj:
            build_snap_cache(context, self.active_obj)
            self._snap_cache_built = True
        return {"RUNNING_MODAL"}

    def exit(self, context: bpy.types.Context, cancel: bool) -> None:
        if context.area:
            context.area.header_text_set(None)
        if hasattr(self, "keyboard_input"):
            self.keyboard_input.reset()

        # Check for click-without-drag: invoke keyboard input operator for accessibility
        should_invoke_keyboard = (
            not cancel
            and hasattr(self, "_has_dragged")
            and not self._has_dragged
            and self.move_set_cb is not None
        )

        if should_invoke_keyboard:
            # Store callback and gizmo references in module-level dict
            _gizmo_value_input_callback["move_set_cb"] = self.move_set_cb
            _gizmo_value_input_callback["active_gizmo"] = self
            _gizmo_value_input_callback["gizmo_group"] = getattr(self, "gizmo_group", None)
            # Store context for mouse movement support
            _gizmo_value_input_callback["start_location"] = self.start_location.copy()
            _gizmo_value_input_callback["axis_direction"] = self.get_axis_direction()
            _gizmo_value_input_callback["active_obj"] = self.active_obj
            _gizmo_value_input_callback["delta_scale"] = getattr(self, "delta_scale", 1.0)
            bpy.ops.bim.gizmo_value_input(
                "INVOKE_DEFAULT",
                prop_name=getattr(self, "prop_name", "Value"),
                init_value=self.init_value,
                invert_delta=getattr(self, "invert_delta", False),
            )
        elif cancel and self.move_set_cb:
            self.move_set_cb(self.init_value)

        if hasattr(self, "initial_snap_state"):
            context.scene.tool_settings.use_snap = self.initial_snap_state
        clear_snap_point()
        clear_snap_cache()

    def get_axis_direction(self) -> Vector:
        """Get the world-space axis direction, transforming local_axis if set."""
        if hasattr(self, "local_axis") and self.active_obj:
            obj_rotation = self.active_obj.matrix_world.to_3x3()
            axis_direction: Vector = obj_rotation @ self.local_axis
            axis_direction.normalize()
            return axis_direction
        return self.axis

    def modal(self, context: bpy.types.Context, event: bpy.types.Event, tweak) -> set:
        region = context.region
        rv3d = context.region_data
        tool_settings = context.scene.tool_settings

        keyboard_result = self._handle_keyboard_input(context, event)
        if keyboard_result is not None:
            return keyboard_result

        if self.keyboard_input.is_active:
            return {"RUNNING_MODAL"}

        if not region or not rv3d:
            return {"RUNNING_MODAL"}

        tool_settings.use_snap = not self.initial_snap_state if event.ctrl else self.initial_snap_state

        # Build snap cache lazily on first Ctrl press if not already built
        if tool_settings.use_snap and not self._snap_cache_built and self.active_obj:
            build_snap_cache(context, self.active_obj)
            self._snap_cache_built = True

        current_coord = (event.mouse_region_x, event.mouse_region_y)

        # Detect if user has dragged beyond threshold
        if not self._has_dragged and hasattr(self, "_start_mouse_pos"):
            dx = current_coord[0] - self._start_mouse_pos[0]
            dy = current_coord[1] - self._start_mouse_pos[1]
            if (dx * dx + dy * dy) > (self.DRAG_THRESHOLD ** 2):
                self._has_dragged = True
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
            snapped_pos = snap_to_mesh(current_3d, context, self.active_obj, current_coord)
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

        # Apply delta scale (e.g., 2.0 for symmetric thickness properties)
        delta_scale = getattr(self, "delta_scale", 1.0)
        delta *= delta_scale

        kb = self.keyboard_input
        final_delta = kb.parsed_value if kb.parsed_value != 0.0 else delta

        if self.move_set_cb:
            self.move_set_cb(self.init_value + final_delta)

        self._update_header(context, self.init_value + final_delta, tool_settings.use_snap, event.shift)

        return {"RUNNING_MODAL"}

    def _handle_keyboard_input(
        self, context: bpy.types.Context, event: bpy.types.Event
    ) -> set[str] | None:
        """Handle keyboard numeric input."""
        kb = self.keyboard_input

        if event.value == "PRESS" and event.ascii and event.ascii.lower() in NUMERIC_INPUT_CHARS:
            kb.characters.append(event.ascii)
            kb.is_active = True
            kb.parse()
            self._apply_keyboard_value()
            self._update_header_typing(context)
            return {"RUNNING_MODAL"}

        if event.type == "BACK_SPACE" and event.value == "PRESS":
            if kb.characters:
                kb.characters.pop()
                kb.parse()
                self._apply_keyboard_value()
                self._update_header_typing(context)
            elif kb.is_active:
                kb.reset()
                if self.move_set_cb:
                    self.move_set_cb(self.init_value)
            return {"RUNNING_MODAL"}

        if event.type in {"RET", "NUMPAD_ENTER"} and event.value == "PRESS":
            if kb.is_active and kb.is_valid:
                final_value = kb.calculate_final_value(self.init_value, getattr(self, "invert_delta", False))
                kb.characters.clear()
                kb.is_active = False
                self._update_header(context, final_value, False, False)
            return {"RUNNING_MODAL"}

        if event.type == "ESC" and event.value == "PRESS" and kb.is_active:
            kb.reset()
            if self.move_set_cb:
                self.move_set_cb(self.init_value)
            return {"RUNNING_MODAL"}

        return None

    def _apply_keyboard_value(self) -> None:
        kb = self.keyboard_input
        if self.move_set_cb and kb.is_valid:
            final_value = kb.calculate_final_value(self.init_value, getattr(self, "invert_delta", False))
            self.move_set_cb(final_value)

    def _update_header_typing(self, context: bpy.types.Context) -> None:
        if not context.area:
            return
        kb = self.keyboard_input
        input_str = kb.get_input_string()
        preview = kb.calculate_final_value(self.init_value, getattr(self, "invert_delta", False))

        validity = "" if kb.is_valid else " [invalid]"
        prop_display = getattr(self, "prop_name", "Value")

        header = f"{prop_display}: {preview:.3f}m  |  Input: {input_str}_{validity}"
        header += "  |  Enter: Confirm  |  Backspace: Delete  |  ESC: Cancel"
        context.area.header_text_set(header)

    def _update_header(self, context: bpy.types.Context, value: float, is_snapping: bool, is_precision: bool) -> None:
        if not context.area:
            return
        prop_display = getattr(self, "prop_name", "Value")
        hints = []
        if is_snapping:
            hints.append("Snapping: ON")
        if is_precision:
            hints.append("Precision (0.1x)")
        hints.extend(["Ctrl: Snap", "Shift: Precision", "Type: Enter Value"])

        header_text = f"{prop_display}: {value:.3f}m  |  " + "  |  ".join(hints)
        context.area.header_text_set(header_text)


class GizmoLock(bpy.types.Gizmo):
    """Lock icon gizmo that switches between closed and open states."""

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
    """Arc gizmo for door swing visualization."""

    bl_idname = "VIEW3D_GT_arc"

    __slots__ = (
        "custom_shape_left",
        "custom_shape_right",
        "prop_path",
    )

    def setup(self) -> None:
        """Create arc shapes for LEFT and RIGHT directions."""
        arc_left = create_circle_arc(radius=1.0, direction="LEFT", angle_min=2.0, angle_max=90.0)
        arc_right = create_circle_arc(radius=1.0, direction="RIGHT", angle_min=2.0, angle_max=90.0)

        self.custom_shape_left = self.new_custom_shape(type="TRIS", verts=arc_left)
        self.custom_shape_right = self.new_custom_shape(type="TRIS", verts=arc_right)

    def _get_shape_for_direction(self, context: bpy.types.Context) -> object:
        """Get arc shape based on door swing direction."""
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
    """Pen/edit icon gizmo for entering edit mode."""

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
    """Validate/checkmark icon gizmo for confirming edits."""

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
    """Cancel/X icon gizmo for canceling edits."""

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
    """Plus icon gizmo for incrementing values."""

    bl_idname = "VIEW3D_GT_plus"

    __slots__ = ("custom_shape",)

    tris = (
        (-0.375, -0.075, 0.0),
        (-0.375, 0.075, 0.0),
        (0.375, 0.075, 0.0),
        (-0.375, -0.075, 0.0),
        (0.375, 0.075, 0.0),
        (0.375, -0.075, 0.0),
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
    """Minus icon gizmo for decrementing values."""

    bl_idname = "VIEW3D_GT_minus"

    __slots__ = ("custom_shape",)

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
    """Generate circular arrow geometry covering ~300 degrees."""
    triangles = []
    radius = 0.375
    line_width = 0.10
    half_width = line_width / 2

    segments = 20
    start_angle = math.radians(30)
    end_angle = math.radians(330)
    angle_range = end_angle - start_angle

    arc_points = []
    for i in range(segments + 1):
        angle = start_angle + angle_range * (i / segments)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        arc_points.append((x, y))

    for i in range(len(arc_points) - 1):
        x1, y1 = arc_points[i]
        x2, y2 = arc_points[i + 1]

        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2) ** 0.5
        if length > 0:
            px, py = -dy / length * half_width, dx / length * half_width

            triangles.extend(
                [
                    (x1 + px, y1 + py, 0.0),
                    (x1 - px, y1 - py, 0.0),
                    (x2 + px, y2 + py, 0.0),
                ]
            )
            triangles.extend(
                [
                    (x2 + px, y2 + py, 0.0),
                    (x1 - px, y1 - py, 0.0),
                    (x2 - px, y2 - py, 0.0),
                ]
            )

            triangles.extend(
                [
                    (x1, y1, -half_width),
                    (x2, y2, -half_width),
                    (x1, y1, +half_width),
                ]
            )
            triangles.extend(
                [
                    (x1, y1, +half_width),
                    (x2, y2, -half_width),
                    (x2, y2, +half_width),
                ]
            )

    arrow_size = 0.30
    end_x, end_y = arc_points[-1]
    prev_x, prev_y = arc_points[-2]
    tangent_x = end_x - prev_x
    tangent_y = end_y - prev_y
    tangent_len = (tangent_x**2 + tangent_y**2) ** 0.5
    if tangent_len > 0:
        tangent_x /= tangent_len
        tangent_y /= tangent_len

    tip_x = end_x + tangent_x * arrow_size * 0.5
    tip_y = end_y + tangent_y * arrow_size * 0.5

    perp_x = -tangent_y * arrow_size
    perp_y = tangent_x * arrow_size

    triangles.extend(
        [
            (tip_x, tip_y, 0.0),
            (end_x - perp_x * 0.5, end_y - perp_y * 0.5, 0.0),
            (end_x + perp_x * 0.5, end_y + perp_y * 0.5, 0.0),
        ]
    )

    triangles.extend(
        [
            (tip_x, tip_y, 0.0),
            (end_x, end_y, -arrow_size * 0.5),
            (end_x, end_y, +arrow_size * 0.5),
        ]
    )

    return tuple(triangles)


class GizmoCycle(bpy.types.Gizmo):
    """Circular arrow icon gizmo for cycling through enum values."""

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


class GizmoArrow2D(GizmoMovable):
    """Flat 2D arrow that rotates around its axis to face the camera."""

    bl_idname = "BIM_GT_gizmo_arrow_2d"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    ARROW_2D_SHAFT_LENGTH = 0.5
    ARROW_2D_HEAD_LENGTH = 0.5
    ARROW_2D_WIDTH = 0.25
    ARROW_2D_HEAD_WIDTH = 0.75

    def _get_arrow_2d_triangles(self) -> tuple[tuple[float, float, float], ...]:
        """Generate flat arrow geometry in XY plane, pointing along +X."""
        shaft = self.ARROW_2D_SHAFT_LENGTH
        head = self.ARROW_2D_HEAD_LENGTH
        w = self.ARROW_2D_WIDTH / 2
        hw = self.ARROW_2D_HEAD_WIDTH / 2

        return (
            # Shaft
            (0, -w, 0), (shaft, -w, 0), (0, w, 0),
            (0, w, 0), (shaft, -w, 0), (shaft, w, 0),
            # Head
            (shaft, -hw, 0), (shaft + head, 0, 0), (shaft, hw, 0),
        )

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self._get_arrow_2d_triangles())

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def draw_prepare(self, context: bpy.types.Context) -> None:
        """Rotate around arrow axis to face camera."""
        position = self.matrix_basis.translation
        to_camera = get_camera_direction(context, position)
        if to_camera is None:
            return

        axis_world = Vector(self.matrix_basis.col[0][:3]).normalized()
        to_camera_projected = to_camera - axis_world * to_camera.dot(axis_world)

        if to_camera_projected.length_squared < 1e-6:
            return

        to_camera_projected.normalize()

        local_z_world = Vector(self.matrix_basis.col[2][:3]).normalized()
        local_z_projected = local_z_world - axis_world * local_z_world.dot(axis_world)

        if local_z_projected.length_squared < 1e-6:
            return

        local_z_projected.normalize()

        cross = local_z_projected.cross(to_camera_projected)
        dot = local_z_projected.dot(to_camera_projected)
        sign = 1.0 if cross.dot(axis_world) >= 0 else -1.0
        angle = sign * math.acos(max(-1.0, min(1.0, dot)))

        axis_rot = Matrix.Rotation(angle, 4, "X")
        current_scale = self.matrix_offset.to_scale() if self.matrix_offset else Vector((1, 1, 1))
        self.matrix_offset = axis_rot @ Matrix.Scale(current_scale[0], 4)


class GizmoCone(GizmoMovable):
    """Cone gizmo for directional value editing."""

    bl_idname = "BIM_GT_gizmo_cone"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    def _get_cone_triangles(self) -> tuple[tuple[float, float, float], ...]:
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
    """Base mixin for parametric element gizmo groups (doors, windows, etc.)."""

    COLOR_RED = (1.0, 0.2, 0.2)
    COLOR_GREEN = (0.1, 0.8, 0.1)
    COLOR_BLUE = (0.3, 0.3, 1.0)
    ARROW_SCALE = 0.25

    # Subclasses must define these
    gizmo_props: list[GizmoPropConfig] = []
    enable_editing_operator: str = ""
    finish_editing_operator: str = ""
    cancel_editing_operator: str = ""
    cycle_type_operator: str = ""

    @classmethod
    def get_arrow_color_from_axis(cls, axis: tuple[int, int, int]) -> tuple[float, float, float]:
        if axis[0] != 0:
            return cls.COLOR_RED
        elif axis[1] != 0:
            return cls.COLOR_GREEN
        return cls.COLOR_BLUE

    def get_axis_rotation_matrix(self, axis: tuple[int, int, int]) -> Matrix:
        axis_vec = Vector(axis).normalized()
        default_dir = Vector((1, 0, 0))
        return default_dir.rotation_difference(axis_vec).to_matrix().to_4x4()

    @classmethod
    def is_element_type(cls, element) -> bool:
        raise NotImplementedError("Subclass must implement is_element_type()")

    @classmethod
    def poll(cls, context) -> bool:
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
        raise NotImplementedError("Subclass must implement get_props()")

    def get_gizmo_prefs(self) -> Any:
        raise NotImplementedError("Subclass must implement get_gizmo_prefs()")

    def get_prop_min_value(self, attr_name: str) -> float:
        return 0.0

    def should_hide_gizmo(self, attr_name: str, props) -> bool:
        return not props.is_editing

    def get_element_height(self, props) -> float:
        return getattr(props, "overall_height", getattr(props, "height", 1.0))

    def setup_property_gizmos(self, context: bpy.types.Context) -> None:
        prefs = tool.Blender.get_addon_preferences()
        highlight_color = prefs.decorator_color_selected[:3]

        for prop_config in self.gizmo_props:
            attr_name = prop_config.attr_name
            invert_delta = prop_config.invert_delta
            gizmo = self.gizmos.new("BIM_GT_gizmo_arrow_2d")

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
            gizmo.delta_scale = prop_config.delta_scale

            gizmo.prop_name = attr_name.replace("_", " ").title()
            gizmo.gizmo_group = self

            gizmo.color = self.get_arrow_color_from_axis(prop_config.axis)
            gizmo.color_highlight = highlight_color
            gizmo.alpha = 0.99
            gizmo.use_draw_modal = True
            gizmo.use_draw_scale = True

            setattr(self, f"gizmo_{attr_name}", gizmo)

    def setup_editing_gizmos(self, context: bpy.types.Context) -> None:
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

        if self.cycle_type_operator:
            self.cycle_gizmo = self.gizmos.new("VIEW3D_GT_cycle")
            self.cycle_gizmo.use_draw_scale = False
            self.cycle_gizmo.color = default_color
            self.cycle_gizmo.color_highlight = highlight_color
            self.cycle_gizmo.alpha = 0.8
            self.cycle_gizmo.target_set_operator(self.cycle_type_operator)

    def update_property_gizmos(self, mw, props) -> None:
        gizmo_prefs = self.get_gizmo_prefs()
        # Check if keyboard input modal is hiding gizmos
        hidden_by_modal = _gizmo_value_input_callback.get("hidden_gizmos", set())

        for prop_config in self.gizmo_props:
            attr_name = prop_config.attr_name
            gizmo = getattr(self, f"gizmo_{attr_name}", None)
            if gizmo is None:
                continue

            # Respect gizmos hidden by keyboard input modal
            if gizmo in hidden_by_modal:
                gizmo.hide = True
                continue

            if not getattr(gizmo_prefs, attr_name, True):
                gizmo.hide = True
                continue

            if self.should_hide_gizmo(attr_name, props):
                gizmo.hide = True
                continue

            gizmo.hide = False
            matrix_method = getattr(self, f"get_gizmo_matrix_{attr_name}", None)
            if matrix_method:
                gizmo.matrix_basis = mw @ matrix_method(props)
            gizmo.matrix_offset = Matrix.Scale(self.ARROW_SCALE, 4)

    def update_editing_gizmos(self, context: bpy.types.Context, mw, props) -> None:
        icon_z = self.get_element_height(props) + 0.5
        billboard_rot = get_billboard_rotation(context)
        # Check if keyboard input modal is hiding gizmos
        hidden_by_modal = _gizmo_value_input_callback.get("hidden_gizmos", set())

        local_transform = (
            Matrix.Translation(Vector((0, 0.0, icon_z)))
            @ billboard_rot
            @ Matrix.Scale(0.5, 4)
        )
        icon_matrix_base = mw @ local_transform

        if props.is_editing:
            self.pen_gizmo.hide = True
            self.validate_gizmo.hide = self.validate_gizmo in hidden_by_modal
            self.validate_gizmo.matrix_basis = icon_matrix_base
            self.cancel_gizmo.hide = self.cancel_gizmo in hidden_by_modal
            cancel_local = Matrix.Translation(Vector((0.5, 0.0, 0.0))) @ local_transform
            self.cancel_gizmo.matrix_basis = mw @ cancel_local
            if self.cycle_type_operator:
                self.cycle_gizmo.hide = self.cycle_gizmo in hidden_by_modal
                cycle_transform = (
                    Matrix.Translation(Vector((0, 0.0, icon_z)))
                    @ billboard_rot
                    @ Matrix.Scale(0.30, 4)
                )
                cycle_local = Matrix.Translation(Vector((0.87, 0.0, 0.0))) @ cycle_transform
                self.cycle_gizmo.matrix_basis = mw @ cycle_local
        else:
            self.pen_gizmo.hide = self.pen_gizmo in hidden_by_modal
            self.pen_gizmo.matrix_basis = icon_matrix_base
            self.validate_gizmo.hide = True
            self.cancel_gizmo.hide = True
            if self.cycle_type_operator:
                self.cycle_gizmo.hide = True

    def draw_prepare(self, context: bpy.types.Context) -> None:
        """Called before drawing - updates gizmos to face camera."""
        obj = context.active_object
        if not obj:
            return
        props = self.get_props(obj)
        mw = obj.matrix_world
        self.update_editing_gizmos(context, mw, props)

        for prop_config in self.gizmo_props:
            gizmo = getattr(self, f"gizmo_{prop_config.attr_name}", None)
            if gizmo and hasattr(gizmo, "draw_prepare") and not gizmo.hide:
                gizmo.draw_prepare(context)
