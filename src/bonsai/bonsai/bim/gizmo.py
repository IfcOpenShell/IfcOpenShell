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

import bpy
import math
from typing import Optional, Tuple, List
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_line_line
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
import gpu
from gpu_extras.batch import batch_for_shader


SNAP_CIRCLE_SEGMENTS = 16
SNAP_CIRCLE_RADIUS = 0.1
SNAP_CIRCLE_COLOR = (1.0, 0.5, 0.0, 1.0)
SNAP_LINE_WIDTH = 3.0
SNAP_MAX_RADIUS = 10.0

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

class SnapManager:
    """Manages snap point visualization and mesh snapping."""

    def __init__(self):
        self._snap_point: Optional[Tuple[float, float, float]] = None
        self._draw_handler = None
        self._shader = None

    def set_snap_point(self, point: Optional[Tuple[float, float, float]]) -> None:
        """Set snap point and register draw handler if needed."""
        self._snap_point = point
        if self._draw_handler is None and point is not None:
            self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(
                self._draw, (), 'WINDOW', 'POST_VIEW'
            )
            self._redraw_viewport()

    def clear(self) -> None:
        """Clear snap point and unregister handler."""
        self._snap_point = None
        if self._draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, 'WINDOW')
            self._draw_handler = None
            self._redraw_viewport()

    def _draw(self) -> None:
        """Draw snap point circles."""
        if self._snap_point is None:
            return

        if self._shader is None:
            self._shader = gpu.shader.from_builtin('UNIFORM_COLOR')

        self._shader.bind()
        self._shader.uniform_float("color", SNAP_CIRCLE_COLOR)
        gpu.state.line_width_set(SNAP_LINE_WIDTH)

        for plane in ('XY', 'XZ', 'YZ'):
            vertices = generate_circle_vertices(
                self._snap_point, SNAP_CIRCLE_RADIUS, SNAP_CIRCLE_SEGMENTS, plane
            )
            batch = batch_for_shader(self._shader, 'LINE_STRIP', {"pos": vertices})
            batch.draw(self._shader)

        gpu.state.line_width_set(1.0)

    @staticmethod
    def _redraw_viewport() -> None:
        """Force 3D viewport redraw."""
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

    @staticmethod
    def snap_to_mesh(
        location: Vector,
        context: bpy.types.Context,
        axis_vector: Vector,
        active_obj: bpy.types.Object
    ) -> Vector:
        """Snap a location to the nearest mesh element if snapping is enabled.

        Args:
            location: The world space location to snap
            context: The Blender context
            axis_vector: The axis direction of the gizmo
            active_obj: The active object to exclude from snapping

        Returns:
            The snapped location or original location if snapping is disabled
        """
        tool_settings = context.scene.tool_settings

        if not tool_settings.use_snap:
            return location

        snap_elements = tool_settings.snap_elements_base

        mesh_objects = [
            obj
            for obj in context.visible_objects
            if obj.type == "MESH" and obj != active_obj and obj.visible_get()
        ]

        if not mesh_objects:
            return location

        nearby_objects = []
        for obj in mesh_objects:
            bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

            for corner in bbox_corners:
                if (corner - location).length <= SNAP_MAX_RADIUS:
                    nearby_objects.append(obj)
                    break

        if not nearby_objects:
            return location

        closest_point = None
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

            if 'VERTEX' in snap_elements:
                for v_co in world_vertices:
                    dist = (v_co - location).length
                    if dist < closest_distance:
                        closest_distance = dist
                        closest_point = v_co

            if 'EDGE' in snap_elements:
                for edge in mesh.edges:
                    v1 = world_vertices[edge.vertices[0]]
                    v2 = world_vertices[edge.vertices[1]]

                    edge_vec = v2 - v1
                    edge_len_sq = edge_vec.length_squared

                    if edge_len_sq > 0:
                        t = max(0, min(1, (location - v1).dot(edge_vec) / edge_len_sq))
                        closest_on_edge = v1 + t * edge_vec
                        dist = (closest_on_edge - location).length

                        if dist < closest_distance:
                            closest_distance = dist
                            closest_point = closest_on_edge

            if 'FACE' in snap_elements:
                bvh = BVHTree.FromPolygons(
                    world_vertices, [p.vertices for p in mesh.polygons]
                )

                nearest_loc, normal, index, dist = bvh.find_nearest(location)

                if nearest_loc and dist < closest_distance:
                    closest_distance = dist
                    closest_point = nearest_loc

            obj_eval.to_mesh_clear()

        if closest_point and closest_distance < SNAP_MAX_RADIUS:
            return closest_point

        return location


_snap_manager = SnapManager()


def set_snap_point(point: Optional[Tuple[float, float, float]]) -> None:
    _snap_manager.set_snap_point(point)


def clear_snap_point() -> None:
    _snap_manager.clear()


def snap_to_mesh(
    location: Vector,
    context: bpy.types.Context,
    axis_vector: Vector,
    active_obj: bpy.types.Object
) -> Vector:
    return _snap_manager.snap_to_mesh(location, context, axis_vector, active_obj)


def generate_circle_vertices(
    center: Tuple[float, float, float],
    radius: float,
    segments: int,
    plane: str = 'XY'
) -> List[Tuple[float, float, float]]:
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

        if plane == 'XY':
            vertices.append((center[0] + cos_a, center[1] + sin_a, center[2]))
        elif plane == 'XZ':
            vertices.append((center[0] + cos_a, center[1], center[2] + sin_a))
        else:
            vertices.append((center[0], center[1] + cos_a, center[2] + sin_a))

    return vertices


def create_quarter_circle_arc(
    radius: float = 1.0,
    segments: int = ARC_SEGMENTS,
    direction: str = "LEFT",
    line_width: float = ARC_LINE_WIDTH
) -> Tuple[Tuple[float, float, float], ...]:
    """Create a quarter circle arc with cross-section thickness for visibility from all angles.

    Args:
        radius: Radius of the arc
        segments: Number of segments for smoothness
        direction: 'LEFT' for counterclockwise (0 to 90°), 'RIGHT' for clockwise (0 to -90°)
        line_width: Width of the arc line in both perpendicular directions

    Returns:
        Tuple of arc triangles for drawing geometry visible from all angles
    """
    half_width = line_width / 2

    arc_points = []
    if direction == "LEFT":
        for i in range(segments + 1):
            angle = (math.pi / 2) * (i / segments)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            arc_points.append((x, y))
    else:
        for i in range(segments + 1):
            angle = (math.pi / 2) * (i / segments)
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

            arc_triangles.extend([
                (x1 + px, y1 + py, 0.0),
                (x1 - px, y1 - py, 0.0),
                (x2 + px, y2 + py, 0.0),
            ])
            arc_triangles.extend([
                (x2 + px, y2 + py, 0.0),
                (x1 - px, y1 - py, 0.0),
                (x2 - px, y2 - py, 0.0),
            ])

            arc_triangles.extend([
                (x1, y1, -half_width),
                (x2, y2, -half_width),
                (x1, y1, +half_width),
            ])
            arc_triangles.extend([
                (x1, y1, +half_width),
                (x2, y2, -half_width),
                (x2, y2, +half_width),
            ])

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
            view_origin, view_origin + view_direction * 1000,
            self.start_location, self.start_location + axis_direction * 1000
        )
        current_3d = result[1] if result else self.start_location

        delta = (current_3d - self.start_location).dot(axis_direction)

        if tool_settings.use_snap and self.active_obj:
            snapped_pos = snap_to_mesh(current_3d, context, axis_direction, self.active_obj)
            if snapped_pos != current_3d:
                delta = (snapped_pos - self.start_location).dot(axis_direction)
                set_snap_point(snapped_pos)
            else:
                clear_snap_point()
        else:
            clear_snap_point()

        if event.shift:
            delta *= PRECISION_MODE_MULTIPLIER

        if self.move_set_cb:
            self.move_set_cb(self.init_value + delta)

        self._update_header(context, self.init_value + delta, tool_settings.use_snap, event.shift)

        return {"RUNNING_MODAL"}

    def _update_header(
        self,
        context: bpy.types.Context,
        value: float,
        is_snapping: bool,
        is_precision: bool
    ) -> None:
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
        (0.16803650558, 0.18791499734, 0.0), (-0.07805634290, 0.18791499734, 0.0), (0.16803650558, 0.44701099396, 0.0),
        (0.16803650558, 0.44701099396, 0.0), (-0.07805634290, 0.18791499734, 0.0), (-0.07805634290, 0.44701099396, 0.0),
        (0.20165449381, 0.13603900373, 0.0), (-0.11167433113, 0.13603900373, 0.0), (0.20165449381, -0.44701099396, 0.0),
        (0.20165449381, -0.44701099396, 0.0), (-0.11167433113, 0.13603900373, 0.0), (-0.11167433113, -0.44701099396, 0.0),
        (-0.07805634290, 0.18791499734, 0.0), (-0.39353451133, 0.18791499734, 0.0), (-0.07805634290, 0.44701099396, 0.0),
        (-0.07805634290, 0.44701099396, 0.0), (-0.39353451133, 0.18791499734, 0.0), (-0.39353451133, 0.30746498704, 0.0),
        (-0.44701099396, 0.18791499734, 0.0), (-0.44701099396, -0.04477182776, 0.0), (-0.39353451133, 0.18791499734, 0.0),
        (-0.39353451133, 0.18791499734, 0.0), (-0.44701099396, -0.04477182776, 0.0), (-0.39353451133, -0.04477182776, 0.0),
    )

    tris_open = (
        (0.16803650558, 0.18791499734, 0.0), (-0.07805634290, 0.18791499734, 0.0), (0.16803650558, 0.44701099396, 0.0),
        (0.16803650558, 0.44701099396, 0.0), (-0.07805634290, 0.18791499734, 0.0), (-0.07805634290, 0.44701099396, 0.0),
        (0.20165449381, 0.13603900373, 0.0), (-0.11167433113, 0.13603900373, 0.0), (0.20165449381, -0.44701099396, 0.0),
        (0.20165449381, -0.44701099396, 0.0), (-0.11167433113, 0.13603900373, 0.0), (-0.11167433113, -0.44701099396, 0.0),
        (0.16803650558, 0.44701099396, 0.0), (-0.07805634290, 0.44701099396, 0.0), (0.16803650558, 0.70610702038, 0.0),
        (0.16803650558, 0.70610702038, 0.0), (-0.07805634290, 0.44701099396, 0.0), (-0.07805634290, 0.58656096458, 0.0),
        (-0.11167433113, 0.44701099396, 0.0), (-0.11167433113, 0.73432201147, 0.0), (-0.07805634290, 0.44701099396, 0.0),
        (-0.07805634290, 0.44701099396, 0.0), (-0.11167433113, 0.73432201147, 0.0), (-0.07805634290, 0.73432201147, 0.0),
    )

    def get_custom_shape(self, context: bpy.types.Context):
        obj = context.active_object
        if not obj:
            return self.custom_shape_closed

        try:
            is_open = obj.path_resolve(self.prop_path)
            return self.custom_shape_open if is_open else self.custom_shape_closed
        except:
            return self.custom_shape_closed

    def setup(self) -> None:
        self.custom_shape_closed = self.new_custom_shape("TRIS", self.tris_closed)
        self.custom_shape_open = self.new_custom_shape("TRIS", self.tris_open)

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.get_custom_shape(context))

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.get_custom_shape(context), select_id=select_id)


class GizmoArc(bpy.types.Gizmo):
    """Reusable quarter circle arc gizmo."""

    bl_idname = "VIEW3D_GT_arc"

    __slots__ = (
        "custom_shape_left",
        "custom_shape_right",
        "prop_path",
    )

    def setup(self) -> None:
        """Create quarter circle shapes for both LEFT and RIGHT directions."""
        arc_left = create_quarter_circle_arc(radius=1.0, direction="LEFT")
        arc_right = create_quarter_circle_arc(radius=1.0, direction="RIGHT")

        self.custom_shape_left = self.new_custom_shape(type="TRIS", verts=arc_left)
        self.custom_shape_right = self.new_custom_shape(type="TRIS", verts=arc_right)

    def _get_shape_for_direction(self, context: bpy.types.Context):
        obj = context.active_object
        if not obj:
            return self.custom_shape_left

        try:
            direction_value = obj.path_resolve(self.prop_path)
            if "RIGHT" in str(direction_value):
                return self.custom_shape_right
        except:
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


class GizmoArrow(GizmoMovable):
    """Arrow gizmo for directional value editing."""

    bl_idname = "BIM_GT_gizmo_arrow"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    def _get_arrow_triangles(self) -> Tuple[Tuple[float, float, float], ...]:
        """Generate arrow geometry along +X axis."""
        triangles = []

        triangles.extend([
            (0, -ARROW_WIDTH, 0),
            (ARROW_SHAFT_LENGTH, -ARROW_WIDTH, 0),
            (0, +ARROW_WIDTH, 0),
        ])
        triangles.extend([
            (0, +ARROW_WIDTH, 0),
            (ARROW_SHAFT_LENGTH, -ARROW_WIDTH, 0),
            (ARROW_SHAFT_LENGTH, +ARROW_WIDTH, 0),
        ])

        triangles.extend([
            (0, 0, -ARROW_WIDTH),
            (ARROW_SHAFT_LENGTH, 0, -ARROW_WIDTH),
            (0, 0, +ARROW_WIDTH),
        ])
        triangles.extend([
            (0, 0, +ARROW_WIDTH),
            (ARROW_SHAFT_LENGTH, 0, -ARROW_WIDTH),
            (ARROW_SHAFT_LENGTH, 0, +ARROW_WIDTH),
        ])

        head_width = ARROW_WIDTH * ARROW_HEAD_WIDTH_MULTIPLIER
        triangles.extend([
            (ARROW_SHAFT_LENGTH, -head_width, 0),
            (ARROW_SHAFT_LENGTH + ARROW_HEAD_LENGTH, 0, 0),
            (ARROW_SHAFT_LENGTH, +head_width, 0),
        ])

        triangles.extend([
            (ARROW_SHAFT_LENGTH, 0, -head_width),
            (ARROW_SHAFT_LENGTH + ARROW_HEAD_LENGTH, 0, 0),
            (ARROW_SHAFT_LENGTH, 0, +head_width),
        ])

        for i in range(ARROW_CIRCLE_SEGMENTS):
            angle1 = (2 * math.pi * i) / ARROW_CIRCLE_SEGMENTS
            angle2 = (2 * math.pi * (i + 1)) / ARROW_CIRCLE_SEGMENTS

            y1 = head_width * math.cos(angle1)
            z1 = head_width * math.sin(angle1)
            y2 = head_width * math.cos(angle2)
            z2 = head_width * math.sin(angle2)

            triangles.extend([
                (ARROW_SHAFT_LENGTH, 0, 0),
                (ARROW_SHAFT_LENGTH, y1, z1),
                (ARROW_SHAFT_LENGTH, y2, z2),
            ])

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

    def _get_cone_triangles(self) -> Tuple[Tuple[float, float, float], ...]:
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

            triangles.extend([
                (cone_tip_x, 0, 0),
                (0, y1, z1),
                (0, y2, z2),
            ])

            triangles.extend([
                (0, 0, 0),
                (0, y2, z2),
                (0, y1, z1),
            ])

        return tuple(triangles)

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self._get_cone_triangles())

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)
