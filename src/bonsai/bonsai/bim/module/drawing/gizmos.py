# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
# Copyright (C) 2020, 2021 Maxim Vasilyev <qwiglydee@gmail.com>
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
Gizmo infrastructure for parametric BIM element editing.

This module provides a framework for interactive 3D gizmos that allow users to
manipulate parametric properties of BIM elements (doors, windows, stairs) directly
in the viewport.

Architecture Overview
=====================

The gizmo system follows a configuration-driven approach where element-specific
gizmo groups (e.g., GizmoDoorEdition) inherit from BaseParametricGizmoGroup and
declare their gizmos via configuration dataclasses:

    class GizmoDoorEdition(bpy.types.GizmoGroup, BaseParametricGizmoGroup):
        dimension_gizmo_props = [
            DimensionGizmoConfig("overall_width", axis=(1, 0, 0)),
            DimensionGizmoConfig("overall_height", axis=(0, 0, 1)),
        ]

Key Components
==============

Configuration Classes:
    - DimensionGizmoConfig: Configures dimension line gizmos with text display

Base Gizmo Classes:
    - GizmoMovable: Base for draggable gizmos with keyboard input support
    - GizmoDimension: Dimension line gizmo with arrows and text labels
    - GizmoArrow2D: 2D arrow gizmo for property manipulation

Mixin Classes:
    - BaseParametricGizmoGroup: Provides common setup/update methods for gizmo groups

Utility Classes:
    - GPUStateScope: Context manager for GPU state save/restore
    - NumericInputState: Tracks keyboard numeric input during modal operations

Global State:
    - _gizmo_modal_context: Module-level dataclass instance for modal operator communication
      (workaround for Blender's ID property limitations)

Data Flow
=========

1. User selects a parametric element (door, window, stair)
2. GizmoGroup.poll() checks if gizmos should be shown
3. GizmoGroup.setup() creates gizmos based on configs
4. GizmoGroup.refresh() updates gizmo positions from element properties
5. User interacts with gizmo -> invoke() -> modal() -> exit()
6. Property changes are written back via move_set_cb callbacks
7. Element mesh is regenerated via operators (e.g., bim.finish_editing_door)

Snapping System
===============

The module includes a mesh vertex snapping system:
    - build_snap_cache(): Builds KD-tree from nearby object vertices
    - snap_to_mesh(): Snaps 3D position to nearest vertex within threshold
    - Uses screen-space distance filtering for accurate snapping

View-Dependent Positioning
==========================

Dimension gizmos automatically reposition based on camera view direction to avoid
overlapping with geometry. The get_local_view_direction() helper determines if the
camera is viewing from the positive or negative side of each axis.
"""

__all__ = [
    "DimensionGizmoConfig",
    "NumericInputState",
    "GPUStateScope",
    "set_snap_point",
    "clear_snap_point",
    "snap_to_mesh",
    "build_snap_cache",
    "clear_snap_cache",
    "get_billboard_rotation",
    "get_camera_direction",
    "generate_circle_vertices",
    "create_circle_arc",
    "BIM_OT_gizmo_value_input",
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
    "GizmoDimension",
    "DimensionRenderer",
    "BaseParametricGizmoGroup",
    "UglyDotGizmo",
    "ExtrusionGuidesGizmo",
    "ExtrusionWidget",
]

from typing import Any, Callable, Iterator

import blf
import bpy
import gpu
import math
import numpy as np
from bpy import types
from dataclasses import dataclass
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_line_line
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
import bonsai.tool as tool
from bonsai.tool.unit import parse_distance_string
from bonsai.bim.module.drawing.shaders import ExtrusionGuidesShader
from ifcopenshell.util.unit import si_conversions


SNAP_POINT_SIZE = 10.0
SNAP_POINT_COLOR = (1.0, 0.5, 0.0, 1.0)
SNAP_MAX_RADIUS = 50.0
SNAP_SCREEN_DISTANCE = 15
SNAP_WORLD_DISTANCE = 0.2
# Query multiple 3D-nearest candidates because screen-nearest may differ from 3D-nearest
SNAP_KD_CANDIDATES = 64

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

RAY_CAST_DISTANCE = 1000
DEFAULT_POINT_SIZE = 1.0

# Characters allowed for keyboard numeric input (supports units and formulas)
_DIGITS = set("0123456789")
_OPERATORS = {".", "-", "+", "*", "/"}
_METRIC_UNITS = {"m", "c", "d"}  # m, cm, dm, mm
_IMPERIAL_UNITS = {"f", "t", "i", "n", "'", '"'}  # ft, in, ', "
_SPECIAL = {"=", " "}  # Formula prefix, spaces

NUMERIC_INPUT_CHARS = _DIGITS | _OPERATORS | _METRIC_UNITS | _IMPERIAL_UNITS | _SPECIAL


@dataclass
class GizmoModalContext:
    """Typed context for modal gizmo operations.

    This replaces the untyped dict pattern for passing state between gizmos
    and the BIM_OT_gizmo_value_input modal operator. Blender ID properties
    don't support function callbacks, so we use this module-level instance.

    Attributes:
        move_set_cb: Callback to set the property value
        active_gizmo: The gizmo currently being manipulated
        gizmo_group: The gizmo group containing the active gizmo
        start_location: World-space position where interaction started
        axis_direction: Direction vector for the gizmo axis
        active_obj: The Blender object being edited
        delta_scale: Multiplier for delta values (e.g., 2.0 for symmetric properties)
        click_offset: Offset from click position to gizmo tip
        hidden_gizmos: Set of gizmos hidden during modal operation
    """

    move_set_cb: Callable[[float], None] | None = None
    active_gizmo: bpy.types.Gizmo | None = None
    gizmo_group: bpy.types.GizmoGroup | None = None
    start_location: Vector | None = None
    axis_direction: Vector | None = None
    active_obj: bpy.types.Object | None = None
    delta_scale: float = 1.0
    click_offset: float = 0.0
    hidden_gizmos: set[bpy.types.Gizmo] | None = None

    def clear(self) -> None:
        """Reset all fields to default values."""
        self.move_set_cb = None
        self.active_gizmo = None
        self.gizmo_group = None
        self.start_location = None
        self.axis_direction = None
        self.active_obj = None
        self.delta_scale = 1.0
        self.click_offset = 0.0
        self.hidden_gizmos = None


# Module-level instance for modal gizmo context
_gizmo_modal_context = GizmoModalContext()


class GPUStateScope:
    """Context manager for saving and restoring GPU state.

    Automatically saves GPU state on entry and restores it on exit,
    ensuring proper cleanup even if an exception occurs.

    Usage:
        with GPUStateScope(depth_test='NONE', blend='ALPHA'):
            ...

        with GPUStateScope(depth_test='NONE', blend='ALPHA', ortho_2d=(width, height)):
            # 2D screen-space drawing
            ...
    """

    __slots__ = (
        "_saved_depth_test",
        "_saved_blend",
        "_saved_projection",
        "_saved_modelview",
        "_depth_test",
        "_blend",
        "_ortho_2d",
    )

    def __init__(
        self,
        depth_test: str | None = None,
        blend: str | None = None,
        ortho_2d: tuple[float, float] | None = None,
    ):
        """Initialize with optional state overrides.

        Args:
            depth_test: Depth test mode ('NONE', 'LESS', 'LESS_EQUAL', etc.) or None to keep current
            blend: Blend mode ('NONE', 'ALPHA', 'ALPHA_PREMULT', etc.) or None to keep current
            ortho_2d: If provided, set up 2D orthographic projection with (width, height)
        """
        self._depth_test = depth_test
        self._blend = blend
        self._ortho_2d = ortho_2d
        self._saved_depth_test: str = ""
        self._saved_blend: str = ""
        self._saved_projection: Matrix | None = None
        self._saved_modelview: Matrix | None = None

    def __enter__(self) -> "GPUStateScope":
        self._saved_depth_test = gpu.state.depth_test_get()
        self._saved_blend = gpu.state.blend_get()

        if self._depth_test is not None:
            gpu.state.depth_test_set(self._depth_test)
        if self._blend is not None:
            gpu.state.blend_set(self._blend)

        if self._ortho_2d is not None:
            self._saved_projection = gpu.matrix.get_projection_matrix()
            self._saved_modelview = gpu.matrix.get_model_view_matrix()

            width, height = self._ortho_2d
            ortho = Matrix.Identity(4)
            ortho[0][0] = 2.0 / width
            ortho[0][3] = -1.0
            ortho[1][1] = 2.0 / height
            ortho[1][3] = -1.0
            ortho[2][2] = -1.0

            gpu.matrix.load_matrix(Matrix.Identity(4))
            gpu.matrix.load_projection_matrix(ortho)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._saved_projection is not None:
            gpu.matrix.load_projection_matrix(self._saved_projection)
        if self._saved_modelview is not None:
            gpu.matrix.load_matrix(self._saved_modelview)

        gpu.state.depth_test_set(self._saved_depth_test)
        gpu.state.blend_set(self._saved_blend)
        return None


class DimensionTextRenderer:
    """Handles text rendering for dimension gizmos.

    Extracted from GizmoDimension to follow Single Responsibility Principle.
    This class manages all text drawing operations including value text,
    property tooltips, and text backgrounds.

    Usage:
        renderer = DimensionTextRenderer.get_instance()
        renderer.draw_value_text(context, screen_pos, perpendicular, value, color)
        renderer.draw_property_tooltip(context, screen_pos, prop_name, color)
    """

    _instance: "DimensionTextRenderer | None" = None
    _tri_shader = None

    # Text rendering parameters
    VALUE_FONT_SIZE = 11
    TOOLTIP_FONT_SIZE = 10
    TEXT_PADDING = 3
    TOOLTIP_OFFSET = 15
    BACKGROUND_ALPHA = 0.7

    @classmethod
    def get_instance(cls) -> "DimensionTextRenderer":
        """Get singleton instance of the text renderer."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _get_tri_shader(cls):
        """Get cached UNIFORM_COLOR shader for triangles."""
        if cls._tri_shader is None:
            cls._tri_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        return cls._tri_shader

    def draw_value_text(
        self,
        context: bpy.types.Context,
        screen_pos: tuple[float, float],
        perpendicular: Vector,
        value: float,
        color: tuple[float, float, float],
        offset_sign: int = 1,
        alignment: str = "center",
    ) -> None:
        """Draw formatted dimension value text at the given screen position.

        Args:
            context: Blender context
            screen_pos: Screen-space position (x, y)
            perpendicular: Perpendicular direction vector for offset
            value: Dimension value to format and display
            color: Text color (r, g, b)
            offset_sign: 1 for above/right, -1 for below/left
            alignment: "center" or "start"
        """
        text = tool.Unit.format_distance(value)

        font_id = 0
        font_size = tool.Blender.scale_font_size(self.VALUE_FONT_SIZE)
        blf.size(font_id, font_size)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)

        text_width, text_height = blf.dimensions(font_id, text)
        offset_distance = (text_height + 4) * offset_sign

        if alignment == "start":
            text_x = screen_pos[0] + perpendicular[0] * offset_distance
            text_y = screen_pos[1] - text_height / 2 + perpendicular[1] * offset_distance
        else:
            text_x = screen_pos[0] - text_width / 2 + perpendicular[0] * offset_distance
            text_y = screen_pos[1] - text_height / 2 + perpendicular[1] * offset_distance

        self._draw_text_background(context, text_x, text_y, text_width, text_height)

        blf.color(font_id, *color, 1.0)
        blf.position(font_id, text_x, text_y, 0)
        blf.draw(font_id, text)
        blf.disable(font_id, blf.SHADOW)

    def draw_property_tooltip(
        self,
        context: bpy.types.Context,
        screen_pos: tuple[float, float],
        prop_name: str,
        color: tuple[float, float, float],
    ) -> None:
        """Draw a tooltip showing the property name near the given screen position.

        Args:
            context: Blender context
            screen_pos: Screen-space position (x, y)
            prop_name: Property name to display (will be converted to Title Case)
            color: Text color (r, g, b)
        """
        prop_display = prop_name.replace("_", " ").title()

        font_id = 0
        font_size = tool.Blender.scale_font_size(self.TOOLTIP_FONT_SIZE)
        blf.size(font_id, font_size)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)

        text_width, text_height = blf.dimensions(font_id, prop_display)

        tooltip_x = screen_pos[0] + self.TOOLTIP_OFFSET
        tooltip_y = screen_pos[1] + self.TOOLTIP_OFFSET

        self._draw_text_background(context, tooltip_x, tooltip_y, text_width, text_height)

        blf.color(font_id, *color, 1.0)
        blf.position(font_id, tooltip_x, tooltip_y, 0)
        blf.draw(font_id, prop_display)
        blf.disable(font_id, blf.SHADOW)

    def _draw_text_background(
        self,
        context: bpy.types.Context,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        """Draw a semi-transparent background behind text."""
        padding = self.TEXT_PADDING
        theme = context.preferences.themes.items()[0][1]
        bg_color = (*theme.user_interface.wcol_menu_back.inner[:3], self.BACKGROUND_ALPHA)

        vertices = [
            (x - padding, y - padding),
            (x + width + padding, y - padding),
            (x + width + padding, y + height + padding),
            (x - padding, y + height + padding),
        ]
        indices = [(0, 1, 2), (0, 2, 3)]

        shader = self._get_tri_shader()
        shader.bind()
        batch = batch_for_shader(shader, "TRIS", {"pos": vertices}, indices=indices)
        shader.uniform_float("color", bg_color)
        batch.draw(shader)


class DimensionRenderer:
    """Handles rendering of dimension line graphics.

    Extracted from GizmoDimension to follow Single Responsibility Principle.
    This class manages all dimension drawing operations including lines,
    arrows, and extension lines in screen space.

    Usage:
        renderer = DimensionRenderer.get_instance()
        renderer.draw(context, start_world, end_world, ...)
    """

    _instance: "DimensionRenderer | None" = None
    _line_shader = None
    _tri_shader = None

    # Visual parameters (in pixels)
    ARROW_SIZE = 10
    EXTENSION_LENGTH = 4
    LINE_WIDTH = 2.0
    MIN_PIXELS_FOR_DETAILS = 35

    @classmethod
    def get_instance(cls) -> "DimensionRenderer":
        """Get singleton instance of the dimension renderer."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _get_line_shader(cls):
        """Get cached POLYLINE_UNIFORM_COLOR shader."""
        if cls._line_shader is None:
            cls._line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        return cls._line_shader

    @classmethod
    def _get_tri_shader(cls):
        """Get cached UNIFORM_COLOR shader for triangles."""
        if cls._tri_shader is None:
            cls._tri_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        return cls._tri_shader

    def draw(
        self,
        context: bpy.types.Context,
        start_world: Vector,
        end_world: Vector,
        axis_world: Vector,
        dimension_length: float,
        color: tuple[float, float, float],
        alpha: float,
        is_highlight: bool,
        highlight_color: tuple[float, float, float],
        highlight_alpha: float,
        show_start_arrow: bool = False,
        show_end_arrow: bool = True,
        show_extension_lines: bool = True,
        text_offset_sign: int = 1,
        text_alignment: str = "center",
        prop_name: str | None = None,
    ) -> None:
        """Draw complete dimension graphics in screen space.

        Args:
            context: Blender context
            start_world: World-space start position
            end_world: World-space end position
            axis_world: Normalized axis direction in world space
            dimension_length: Length of the dimension (for text display)
            color: Base color (r, g, b)
            alpha: Base alpha
            is_highlight: Whether gizmo is highlighted/hovered
            highlight_color: Highlight color (r, g, b)
            highlight_alpha: Highlight alpha
            show_start_arrow: Whether to show arrow at start
            show_end_arrow: Whether to show arrow at end
            show_extension_lines: Whether to show extension lines
            text_offset_sign: 1 for above/right, -1 for below/left
            text_alignment: "center" or "start"
            prop_name: Property name for tooltip (shown when highlighted)
        """
        if dimension_length < 0:
            return

        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        start_screen = location_3d_to_region_2d(region, rv3d, start_world)
        end_screen = location_3d_to_region_2d(region, rv3d, end_world)

        if not start_screen or not end_screen:
            return

        direction = Vector((end_screen[0] - start_screen[0], end_screen[1] - start_screen[1]))
        length_screen = direction.length

        actual_value_is_zero = dimension_length <= 0.001

        # When screen length is zero due to viewing angle (not actual value), skip drawing
        if length_screen < 1 and not actual_value_is_zero:
            return

        # When actual value is zero, determine direction from 3D axis projection
        if length_screen < 1 and actual_value_is_zero:
            test_world = start_world + axis_world * 0.1
            test_screen = location_3d_to_region_2d(region, rv3d, test_world)
            if test_screen:
                direction = Vector((test_screen[0] - start_screen[0], test_screen[1] - start_screen[1]))
                if direction.length > 0.001:
                    direction.normalize()
                else:
                    direction = Vector((1, 0))
            else:
                direction = Vector((1, 0))
        else:
            direction.normalize()

        perpendicular = Vector((-direction[1], direction[0]))

        vertices = []
        indices = []

        line_start = (start_screen[0], start_screen[1])
        line_end = (end_screen[0], end_screen[1])

        if show_start_arrow:
            line_start = (
                start_screen[0] + direction[0] * self.ARROW_SIZE,
                start_screen[1] + direction[1] * self.ARROW_SIZE,
            )
        if show_end_arrow:
            line_end = (
                end_screen[0] - direction[0] * self.ARROW_SIZE,
                end_screen[1] - direction[1] * self.ARROW_SIZE,
            )

        vertices.append(line_start)
        vertices.append(line_end)
        indices.append((0, 1))

        arrow_triangles = []

        if show_start_arrow:
            arrow_triangles.extend(
                self._build_arrow_triangle(start_screen, direction, perpendicular, pointing_backward=False)
            )

        if show_end_arrow:
            arrow_triangles.extend(
                self._build_arrow_triangle(end_screen, direction, perpendicular, pointing_backward=True)
            )

        if show_extension_lines and length_screen >= self.MIN_PIXELS_FOR_DETAILS:
            idx = len(vertices)
            ext_start_top, ext_start_bottom = self._build_extension_line_vertices(start_screen, perpendicular)
            vertices.append(ext_start_top)
            vertices.append(ext_start_bottom)
            indices.append((idx, idx + 1))

            idx = len(vertices)
            ext_end_top, ext_end_bottom = self._build_extension_line_vertices(end_screen, perpendicular)
            vertices.append(ext_end_top)
            vertices.append(ext_end_bottom)
            indices.append((idx, idx + 1))

        if is_highlight:
            draw_color = (*highlight_color, highlight_alpha)
        else:
            draw_color = (*color, alpha)

        with GPUStateScope(depth_test="NONE", blend="ALPHA", ortho_2d=(region.width, region.height)):
            shader = self._get_line_shader()
            shader.bind()
            shader.uniform_float("viewportSize", (region.width, region.height))
            shader.uniform_float("lineWidth", self.LINE_WIDTH)
            shader.uniform_float("color", draw_color)

            line_batch = batch_for_shader(shader, "LINES", {"pos": vertices}, indices=indices)
            line_batch.draw(shader)

            if arrow_triangles:
                tri_shader = self._get_tri_shader()
                tri_shader.bind()
                tri_shader.uniform_float("color", draw_color)
                tri_batch = batch_for_shader(tri_shader, "TRIS", {"pos": arrow_triangles})
                tri_batch.draw(tri_shader)

            if length_screen >= self.MIN_PIXELS_FOR_DETAILS:
                center_screen = (
                    (start_screen[0] + end_screen[0]) / 2,
                    (start_screen[1] + end_screen[1]) / 2,
                )
                text_color = highlight_color if is_highlight else color
                DimensionTextRenderer.get_instance().draw_value_text(
                    context, center_screen, perpendicular, dimension_length, text_color, text_offset_sign, text_alignment
                )

            if is_highlight and prop_name:
                tooltip_color = highlight_color
                DimensionTextRenderer.get_instance().draw_property_tooltip(
                    context, (end_screen[0], end_screen[1]), prop_name, tooltip_color
                )

    def _build_arrow_triangle(
        self, position: Vector, direction: Vector, perpendicular: Vector, pointing_backward: bool
    ) -> list[tuple[float, float]]:
        """Build triangle vertices for an arrow head."""
        sign = -1 if pointing_backward else 1
        arrow_tip = (position[0], position[1])
        arrow_back_left = (
            position[0] + sign * direction[0] * self.ARROW_SIZE + perpendicular[0] * self.ARROW_SIZE * 0.5,
            position[1] + sign * direction[1] * self.ARROW_SIZE + perpendicular[1] * self.ARROW_SIZE * 0.5,
        )
        arrow_back_right = (
            position[0] + sign * direction[0] * self.ARROW_SIZE - perpendicular[0] * self.ARROW_SIZE * 0.5,
            position[1] + sign * direction[1] * self.ARROW_SIZE - perpendicular[1] * self.ARROW_SIZE * 0.5,
        )
        return [arrow_tip, arrow_back_left, arrow_back_right]

    def _build_extension_line_vertices(
        self, position: Vector, perpendicular: Vector
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """Build extension line endpoints perpendicular to the dimension."""
        top = (
            position[0] + perpendicular[0] * self.EXTENSION_LENGTH,
            position[1] + perpendicular[1] * self.EXTENSION_LENGTH,
        )
        bottom = (
            position[0] - perpendicular[0] * self.EXTENSION_LENGTH,
            position[1] - perpendicular[1] * self.EXTENSION_LENGTH,
        )
        return (top, bottom)


@dataclass
class SnapCache:
    """Unified snap cache with combined KD-tree for vertex snapping."""

    # Combined KD-tree with all world vertices from all objects
    kd_tree: KDTree
    # All world vertices indexed by global vertex index (tuples for memory efficiency)
    all_vertices: list[tuple[float, float, float]]


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
class DimensionGizmoConfig:
    """Configuration for a dimension gizmo.

    Used to declaratively configure dimension line gizmos in BaseParametricGizmoGroup subclasses.
    This enables a data-driven approach that reduces boilerplate code for setting up
    dimension gizmos with consistent behavior.

    Color and prop_name are auto-derived if not specified:
        - axis (1,0,0) or (-1,0,0) -> RED
        - axis (0,1,0) or (0,-1,0) -> GREEN
        - axis (0,0,1) or (0,0,-1) -> BLUE
        - prop_name: "attr_name" -> "Attr Name" (underscores to spaces, title case)

    Examples:
        # Basic dimension - uses attr_name to read/write property
        DimensionGizmoConfig(
            attr_name="overall_width",
            axis=(1, 0, 0),
            min_value=0.01,
        )

        # Custom value calculation - for computed properties
        DimensionGizmoConfig(
            attr_name="total_length",
            axis=(1, 0, 0),
            compute_value=lambda props: props.tread_run * props.num_treads,
            apply_value=lambda props, val: setattr(props, "target_length", val),
        )

        # Conditional visibility - hide when not applicable
        DimensionGizmoConfig(
            attr_name="nosing_length",
            axis=(-1, 0, 0),
            visibility_condition=lambda props: props.nosing_length > 0,
        )

    Attributes:
        attr_name: Property name to bind to (e.g., "overall_width"). Used to generate
            gizmo attribute name as f"dimension_{attr_name}_gizmo".
        axis: Direction tuple (x, y, z) for the dimension line. Determines color if not
            specified and defines drag direction. Use negative values for reversed directions.
        color: Optional override. One of "RED", "GREEN", "BLUE". Auto-derived from axis.
        prop_name: Display name for tooltips. Defaults to attr_name with underscores
            replaced by spaces and title-cased.
        min_value: Minimum allowed value when dragging (default 0.0).
        invert_delta: If True, reverses the drag direction effect.
        delta_scale: Multiplier for drag delta (default 1.0). Use <1 for fine control.
        text_offset_sign: 1 or -1 to position text above/below dimension line.
        text_alignment: "start", "center", or "end" for text positioning along line.
        show_start_arrow: Whether to show arrow at start point (default False).
        show_end_arrow: Whether to show arrow at end point (default True).
        compute_value: Optional function(props) -> float for computed dimension values.
            If None, reads directly from getattr(props, attr_name).
        apply_value: Optional function(props, value) to apply new values after drag.
            If None, uses setattr(props, attr_name, value).
        visibility_condition: Optional function(props) -> bool. If returns False,
            the gizmo is hidden. Used for conditional gizmos.
    """

    attr_name: str
    axis: tuple[int, int, int]
    color: str | None = None
    prop_name: str | None = None
    min_value: float = 0.0
    invert_delta: bool = False
    delta_scale: float = 1.0
    text_offset_sign: int = 1
    text_alignment: str = "center"
    show_start_arrow: bool = False
    show_end_arrow: bool = True
    compute_value: Callable[[Any], float] | None = None
    apply_value: Callable[[Any, float], None] | None = None
    visibility_condition: Callable[[Any], bool] | None = None

    def __post_init__(self):
        if self.color is None:
            if self.axis[0] != 0:
                self.color = "RED"
            elif self.axis[1] != 0:
                self.color = "GREEN"
            else:
                self.color = "BLUE"

        if self.prop_name is None:
            self.prop_name = self.attr_name.replace("_", " ").title()


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

    def build_snap_cache(
        self, context: bpy.types.Context, active_obj: bpy.types.Object, include_active: bool = False
    ) -> None:
        """Build unified cache with combined KD-tree for vertex snapping.

        Uses foreach_get for fast vertex data extraction and NumPy for
        batch matrix transformation.

        Args:
            context: The current Blender context.
            active_obj: The active object being edited.
            include_active: If True, include the active object's vertices in snapping targets.
        """
        self._snap_cache = None

        mesh_objects = [obj for obj in context.visible_objects if obj.type == "MESH" and obj.visible_get()]

        if not include_active:
            mesh_objects = [obj for obj in mesh_objects if obj != active_obj]

        if not mesh_objects:
            return

        depsgraph = context.evaluated_depsgraph_get()
        all_vertices: list[tuple[float, float, float]] = []

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

                all_vertices.extend(tuple(co) for co in world_coords)
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

            bbox_min = Vector(
                (
                    min(c.x for c in bbox_corners),
                    min(c.y for c in bbox_corners),
                    min(c.z for c in bbox_corners),
                )
            )
            bbox_max = Vector(
                (
                    max(c.x for c in bbox_corners),
                    max(c.y for c in bbox_corners),
                    max(c.z for c in bbox_corners),
                )
            )

            closest = Vector(
                (
                    max(bbox_min.x, min(location.x, bbox_max.x)),
                    max(bbox_min.y, min(location.y, bbox_max.y)),
                    max(bbox_min.z, min(location.z, bbox_max.z)),
                )
            )

            if (location - closest).length_squared <= radius_sq:
                nearby_objects.append(obj)

        return nearby_objects

    def snap_to_mesh(
        self,
        location: Vector,
        context: bpy.types.Context,
        active_obj: bpy.types.Object,
        mouse_coords: tuple[float, float] | None = None,
        include_active: bool = False,
    ) -> Vector:
        """Snap a location to the nearest vertex if snapping is enabled.

        Only vertex snapping is supported. Returns the original location if
        snapping is disabled or VERTEX is not in the snap elements.

        Args:
            location: The 3D location to snap from.
            context: The current Blender context.
            active_obj: The active object being edited.
            mouse_coords: Optional mouse coordinates for screen-space distance.
            include_active: If True, include the active object's vertices in snapping targets.
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
            closest_point, closest_dist_sq = self._snap_from_cache(location, mouse_vec, region, rv3d)
        else:
            closest_point, closest_dist_sq = self._snap_without_cache(
                location, context, active_obj, mouse_vec, region, rv3d, include_active
            )

        max_dist_sq = SNAP_SCREEN_DISTANCE**2 if use_screen_distance else SNAP_WORLD_DISTANCE**2
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
        """Find closest vertex using cached KD-tree.

        Searches from both the target location AND a secondary location derived from
        the mouse position to handle cases where click offset causes the mouse to be
        far from the target location on screen.
        """
        if self._snap_cache is None:
            return None, float("inf")

        cache = self._snap_cache

        closest_point, closest_dist_sq = SnapManager._find_closest_vertex(
            cache.all_vertices, location, mouse_vec, region, rv3d, None, float("inf"), cache.kd_tree
        )

        # Also search from mouse's 3D position to handle click offset cases
        if mouse_vec is not None and region is not None and rv3d is not None:
            mouse_origin = region_2d_to_origin_3d(region, rv3d, mouse_vec)
            mouse_direction = region_2d_to_vector_3d(region, rv3d, mouse_vec)
            view_distance = (location - mouse_origin).length
            mouse_3d = mouse_origin + mouse_direction * view_distance

            closest_point, closest_dist_sq = SnapManager._find_closest_vertex(
                cache.all_vertices, mouse_3d, mouse_vec, region, rv3d, closest_point, closest_dist_sq, cache.kd_tree
            )

        return closest_point, closest_dist_sq

    def _snap_without_cache(
        self,
        location: Vector,
        context: bpy.types.Context,
        active_obj: bpy.types.Object,
        mouse_vec: Vector | None,
        region: bpy.types.Region | None,
        rv3d: bpy.types.RegionView3D | None,
        include_active: bool = False,
    ) -> tuple[Vector | None, float]:
        """Find closest vertex without cache (fallback path)."""
        mesh_objects = [obj for obj in context.visible_objects if obj.type == "MESH" and obj.visible_get()]

        if not include_active:
            mesh_objects = [obj for obj in mesh_objects if obj != active_obj]

        if not mesh_objects:
            return None, float("inf")

        nearby_objects = set(SnapManager._get_nearby_objects(mesh_objects, location))

        if mouse_vec is not None and region is not None and rv3d is not None:
            mouse_origin = region_2d_to_origin_3d(region, rv3d, mouse_vec)
            mouse_direction = region_2d_to_vector_3d(region, rv3d, mouse_vec)
            view_distance = (location - mouse_origin).length
            mouse_3d = mouse_origin + mouse_direction * view_distance
            nearby_objects.update(SnapManager._get_nearby_objects(mesh_objects, mouse_3d))

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
                    world_vertices, location, mouse_vec, region, rv3d, closest_point, closest_dist_sq
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
    include_active: bool = False,
) -> Vector:
    return _snap_manager.snap_to_mesh(location, context, active_obj, mouse_coords, include_active)


def build_snap_cache(
    context: bpy.types.Context, active_obj: bpy.types.Object, include_active: bool = False
) -> None:
    _snap_manager.build_snap_cache(context, active_obj, include_active)


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


# ============================================================================
# Gizmos under the hood
# ============================================================================
#
# ## Transforms:
#
# source/blender/windowmanager/gizmo/WM_gizmo_types.h
# matrix_basis -- "Transformation of this gizmo." = placement in scene
# matrix_offset -- "Custom offset from origin." = local transforms according to state/value
# matrix_space -- "The space this gizmo is being modified in." used by some gizmos for undefined purposes
# matrix_world -- final matrix, scaled according to viewport zoom and custom scale_basis
#
# source/blender/windowmanager/gizmo/intern/wm_gizmo.c:WM_gizmo_calc_matrix_final_params
# final = space @ (autoscale * (basis @ offset))
# final = space @ (basis @ offset) -- if gizmo.use_draw_scale == False
# final = space @ ((autoscale * basis) @ offset) -- if gizmo.use_draw_offset_scale
#
# source/blender/windowmanager/gizmo/intern/wm_gizmo.c:wm_gizmo_calculate_scale
# autoscale = gizmo.scale_basis * magic(preferences, matrix_space, matrix_basis, context.region_data)
# magic -- making 1.0 to match preferences.view.gizmo_size pixels (75 by default)
#
#
# ## Selection
#
# select_id -- apparently, id of a selectable part
# test_select -- expected to return id of selection, doesn't seem to work
# draw_select -- fake-draw of selection geometry for gpu-side cursor tracking
# ============================================================================


# Some geometries for Gizmo.custom_shape shaders

CUBE = (
    (+1, +1, +1),
    (-1, +1, +1),
    (+1, -1, +1),  # top
    (+1, -1, +1),
    (-1, +1, +1),
    (-1, -1, +1),
    (+1, +1, +1),
    (+1, -1, +1),
    (+1, +1, -1),  # right
    (+1, +1, -1),
    (+1, -1, +1),
    (+1, -1, -1),
    (+1, +1, +1),
    (+1, +1, -1),
    (-1, +1, +1),  # back
    (-1, +1, +1),
    (+1, +1, -1),
    (-1, +1, -1),
    (-1, -1, -1),
    (-1, +1, -1),
    (+1, -1, -1),  # bot
    (+1, -1, -1),
    (-1, +1, -1),
    (+1, +1, -1),
    (-1, -1, -1),
    (-1, -1, +1),
    (-1, +1, -1),  # left
    (-1, +1, -1),
    (-1, -1, +1),
    (-1, +1, +1),
    (-1, -1, -1),
    (+1, -1, -1),
    (-1, -1, +1),  # front
    (-1, -1, +1),
    (+1, -1, -1),
    (+1, -1, +1),
)

DISC = (
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0),
    (0.8660254037844387, 0.49999999999999994, 0),
    (0.0, 0.0, 0.0),
    (0.8660254037844387, 0.49999999999999994, 0),
    (0.5000000000000001, 0.8660254037844386, 0),
    (0.0, 0.0, 0.0),
    (0.5000000000000001, 0.8660254037844386, 0),
    (6.123233995736766e-17, 1.0, 0),
    (0.0, 0.0, 0.0),
    (6.123233995736766e-17, 1.0, 0),
    (-0.4999999999999998, 0.8660254037844387, 0),
    (0.0, 0.0, 0.0),
    (-0.4999999999999998, 0.8660254037844387, 0),
    (-0.8660254037844385, 0.5000000000000003, 0),
    (0.0, 0.0, 0.0),
    (-0.8660254037844385, 0.5000000000000003, 0),
    (-1.0, 1.2246467991473532e-16, 0),
    (0.0, 0.0, 0.0),
    (-1.0, 1.2246467991473532e-16, 0),
    (-0.8660254037844388, -0.4999999999999997, 0),
    (0.0, 0.0, 0.0),
    (-0.8660254037844388, -0.4999999999999997, 0),
    (-0.5000000000000004, -0.8660254037844384, 0),
    (0.0, 0.0, 0.0),
    (-0.5000000000000004, -0.8660254037844384, 0),
    (-1.8369701987210297e-16, -1.0, 0),
    (0.0, 0.0, 0.0),
    (-1.8369701987210297e-16, -1.0, 0),
    (0.49999999999999933, -0.866025403784439, 0),
    (0.0, 0.0, 0.0),
    (0.49999999999999933, -0.866025403784439, 0),
    (0.8660254037844384, -0.5000000000000004, 0),
    (0.0, 0.0, 0.0),
    (0.8660254037844384, -0.5000000000000004, 0),
    (1.0, 0.0, 0),
)

X3DISC = (
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0),
    (0.8660254037844387, 0.49999999999999994, 0),
    (0.0, 0.0, 0.0),
    (0.8660254037844387, 0.49999999999999994, 0),
    (0.5000000000000001, 0.8660254037844386, 0),
    (0.0, 0.0, 0.0),
    (0.5000000000000001, 0.8660254037844386, 0),
    (6.123233995736766e-17, 1.0, 0),
    (0.0, 0.0, 0.0),
    (6.123233995736766e-17, 1.0, 0),
    (-0.4999999999999998, 0.8660254037844387, 0),
    (0.0, 0.0, 0.0),
    (-0.4999999999999998, 0.8660254037844387, 0),
    (-0.8660254037844385, 0.5000000000000003, 0),
    (0.0, 0.0, 0.0),
    (-0.8660254037844385, 0.5000000000000003, 0),
    (-1.0, 1.2246467991473532e-16, 0),
    (0.0, 0.0, 0.0),
    (-1.0, 1.2246467991473532e-16, 0),
    (-0.8660254037844388, -0.4999999999999997, 0),
    (0.0, 0.0, 0.0),
    (-0.8660254037844388, -0.4999999999999997, 0),
    (-0.5000000000000004, -0.8660254037844384, 0),
    (0.0, 0.0, 0.0),
    (-0.5000000000000004, -0.8660254037844384, 0),
    (-1.8369701987210297e-16, -1.0, 0),
    (0.0, 0.0, 0.0),
    (-1.8369701987210297e-16, -1.0, 0),
    (0.49999999999999933, -0.866025403784439, 0),
    (0.0, 0.0, 0.0),
    (0.49999999999999933, -0.866025403784439, 0),
    (0.8660254037844384, -0.5000000000000004, 0),
    (0.0, 0.0, 0.0),
    (0.8660254037844384, -0.5000000000000004, 0),
    (1.0, 0.0, 0),
    (0.0, 0.0, 0.0),
    (0, 1.0, 0.0),
    (0, 0.8660254037844387, 0.49999999999999994),
    (0.0, 0.0, 0.0),
    (0, 0.8660254037844387, 0.49999999999999994),
    (0, 0.5000000000000001, 0.8660254037844386),
    (0.0, 0.0, 0.0),
    (0, 0.5000000000000001, 0.8660254037844386),
    (0, 6.123233995736766e-17, 1.0),
    (0.0, 0.0, 0.0),
    (0, 6.123233995736766e-17, 1.0),
    (0, -0.4999999999999998, 0.8660254037844387),
    (0.0, 0.0, 0.0),
    (0, -0.4999999999999998, 0.8660254037844387),
    (0, -0.8660254037844385, 0.5000000000000003),
    (0.0, 0.0, 0.0),
    (0, -0.8660254037844385, 0.5000000000000003),
    (0, -1.0, 1.2246467991473532e-16),
    (0.0, 0.0, 0.0),
    (0, -1.0, 1.2246467991473532e-16),
    (0, -0.8660254037844388, -0.4999999999999997),
    (0.0, 0.0, 0.0),
    (0, -0.8660254037844388, -0.4999999999999997),
    (0, -0.5000000000000004, -0.8660254037844384),
    (0.0, 0.0, 0.0),
    (0, -0.5000000000000004, -0.8660254037844384),
    (0, -1.8369701987210297e-16, -1.0),
    (0.0, 0.0, 0.0),
    (0, -1.8369701987210297e-16, -1.0),
    (0, 0.49999999999999933, -0.866025403784439),
    (0.0, 0.0, 0.0),
    (0, 0.49999999999999933, -0.866025403784439),
    (0, 0.8660254037844384, -0.5000000000000004),
    (0.0, 0.0, 0.0),
    (0, 0.8660254037844384, -0.5000000000000004),
    (0, 1.0, 0.0),
    (0.0, 0.0, 0.0),
    (0.0, 0, 1.0),
    (0.49999999999999994, 0, 0.8660254037844387),
    (0.0, 0.0, 0.0),
    (0.49999999999999994, 0, 0.8660254037844387),
    (0.8660254037844386, 0, 0.5000000000000001),
    (0.0, 0.0, 0.0),
    (0.8660254037844386, 0, 0.5000000000000001),
    (1.0, 0, 6.123233995736766e-17),
    (0.0, 0.0, 0.0),
    (1.0, 0, 6.123233995736766e-17),
    (0.8660254037844387, 0, -0.4999999999999998),
    (0.0, 0.0, 0.0),
    (0.8660254037844387, 0, -0.4999999999999998),
    (0.5000000000000003, 0, -0.8660254037844385),
    (0.0, 0.0, 0.0),
    (0.5000000000000003, 0, -0.8660254037844385),
    (1.2246467991473532e-16, 0, -1.0),
    (0.0, 0.0, 0.0),
    (1.2246467991473532e-16, 0, -1.0),
    (-0.4999999999999997, 0, -0.8660254037844388),
    (0.0, 0.0, 0.0),
    (-0.4999999999999997, 0, -0.8660254037844388),
    (-0.8660254037844384, 0, -0.5000000000000004),
    (0.0, 0.0, 0.0),
    (-0.8660254037844384, 0, -0.5000000000000004),
    (-1.0, 0, -1.8369701987210297e-16),
    (0.0, 0.0, 0.0),
    (-1.0, 0, -1.8369701987210297e-16),
    (-0.866025403784439, 0, 0.49999999999999933),
    (0.0, 0.0, 0.0),
    (-0.866025403784439, 0, 0.49999999999999933),
    (-0.5000000000000004, 0, 0.8660254037844384),
    (0.0, 0.0, 0.0),
    (-0.5000000000000004, 0, 0.8660254037844384),
    (0.0, 0, 1.0),
)


class CustomGizmo:
    # FIXME: highlighting/selection doesn't work
    def draw_very_custom_shape(self, ctx, custom_shape, select_id=None):
        shader_wrapper, batch = custom_shape
        shader = shader_wrapper.get_shader()

        shader.bind()
        if select_id is not None:
            gpu.select.load_id(select_id)
        else:
            if self.is_highlight:
                color = (*self.color_highlight, self.alpha_highlight)
            else:
                color = (*self.color, self.alpha)
            shader.uniform_float("color", color)
            shader_wrapper.glenable()
        shader_wrapper.uniform_region(ctx)

        with gpu.matrix.push_pop():
            # matrix_world is unaffected by matrix_offset, so use basis @ offset
            matrix = self.matrix_basis @ self.matrix_offset
            gpu.matrix.multiply_matrix(matrix)
            batch.draw(shader)

        gpu.state.blend_set("NONE")


class OffsetHandle:
    """Handling mouse to offset gizmo from base along Z axis"""

    # FIXME: works a bit weird for rotated objects

    def invoke(self, ctx, event):
        self.init_value = self.target_get_value("offset") / self.scale_value
        coordz = self.project_mouse(ctx, event)
        if coordz is None:
            return {"CANCELLED"}
        self.init_coordz = coordz
        return {"RUNNING_MODAL"}

    def modal(self, ctx, event, tweak):
        coordz = self.project_mouse(ctx, event)
        if coordz is None:
            return {"CANCELLED"}
        delta = coordz - self.init_coordz
        if "PRECISE" in tweak:
            delta /= 10.0
        value = max(0, self.init_value + delta)
        value *= self.scale_value
        # ctx.area.header_text_set(f"coords: {self.init_coordz} - {coordz}, delta: {delta}, value: {value}")
        ctx.area.header_text_set(f"Depth: {value}")
        self.target_set_value("offset", value)
        return {"RUNNING_MODAL"}

    def project_mouse(self, ctx, event):
        """Projecting mouse coords to local axis Z"""
        # logic from source/blender/editors/gizmo_library/gizmo_types/arrow3d_gizmo.c:gizmo_arrow_modal

        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        region = ctx.region
        region3d = ctx.region_data
        ray_orig = view3d_utils.region_2d_to_origin_3d(region, region3d, mouse)
        ray_norm = view3d_utils.region_2d_to_vector_3d(region, region3d, mouse)

        # 'arrow' origin and direction
        base = Vector((0, 0, 0))
        axis = Vector((0, 0, 1))

        # projection of the arrow to a plane, perpendicular to view ray
        axis_proj = axis - ray_norm * axis.dot(ray_norm)

        # intersection of the axis with the plane through view origin perpendicular to the arrow projection
        coords = geometry.intersect_line_plane(base, axis, ray_orig, axis_proj)

        return coords.z

    def exit(self, ctx, cancel):
        if cancel:
            self.target_set_value("offset", self.init_value)
        else:
            self.group.update(ctx)


class UglyDotGizmo(OffsetHandle, types.Gizmo):
    """three orthogonal circles"""

    bl_idname = "BIM_GT_uglydot_3d"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    __slots__ = (
        "scale_value",
        "custom_shape",
        "init_value",
        "init_coordz",
    )

    def setup(self):
        self.custom_shape = self.new_custom_shape(type="TRIS", verts=X3DISC)

    def refresh(self):
        offset = self.target_get_value("offset") / self.scale_value
        self.matrix_offset.translation.z = offset

    def draw(self, ctx):
        self.refresh()
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, ctx, select_id):
        self.refresh()
        self.draw_custom_shape(self.custom_shape, select_id=select_id)



class ExtrusionGuidesGizmo(CustomGizmo, types.Gizmo):
    """Extrusion guides

    Noninteractive gizmo to indicate extrusion depth and planes.
    Draws main segment and orthogonal cross at endpoints.
    """

    bl_idname = "BIM_GT_extrusion_guides"
    bl_target_properties = ({"id": "depth", "type": "FLOAT", "array_length": 1},)

    __slots__ = ("scale_value", "custom_shape")

    def setup(self):
        """setup `custom_shape`"""
        shader_wrapper = ExtrusionGuidesShader()
        verts = [Vector((0, 0, 0)), Vector((0, 0, 1))]
        verts, edges = shader_wrapper.process_geometry(verts)
        if not tool.Blender.validate_shader_batch_data(verts, edges):
            verts, edges = [], []
        self.custom_shape = shader_wrapper, shader_wrapper.batch(
            pos=verts,
            indices=edges,
        )

    def draw(self, ctx):
        self.refresh()
        self.draw_very_custom_shape(ctx, self.custom_shape)

    def refresh(self):
        depth = self.target_get_value("depth") / self.scale_value
        self.matrix_offset.col[2][2] = depth  # z-scaled



class ExtrusionWidget(types.GizmoGroup):
    bl_idname = "bim.extrusion_widget"
    bl_label = "Extrusion Gizmos"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT", "SHOW_MODAL_ALL"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj
            and (data := obj.data)
            and isinstance(data, bpy.types.Mesh)
            and tool.Geometry.get_mesh_props(data).ifc_parameters.get("IfcExtrudedAreaSolid/Depth") is not None
        )

    def setup(self, context: bpy.types.Context) -> None:
        target = context.object
        if not target:
            return
        mesh = target.data
        if not isinstance(mesh, bpy.types.Mesh):
            return
        prop = tool.Geometry.get_mesh_props(mesh).ifc_parameters.get("IfcExtrudedAreaSolid/Depth")

        basis = target.matrix_world.normalized()
        theme = context.preferences.themes[0].user_interface
        scale_value = self.get_scale_value(context.scene.unit_settings.system, context.scene.unit_settings.length_unit)

        # setup handle
        gz = self.handle = self.gizmos.new("BIM_GT_uglydot_3d")
        gz.matrix_basis = basis
        gz.scale_basis = 0.1
        gz.color = gz.color_highlight = tuple(theme.gizmo_primary)
        gz.alpha = 0.5
        gz.alpha_highlight = 1.0
        gz.use_draw_modal = True
        gz.target_set_prop("offset", prop, "value")
        gz.scale_value = scale_value

        # setup guides
        gz = self.guides = self.gizmos.new("BIM_GT_extrusion_guides")
        gz.matrix_basis = basis
        gz.color = gz.color_highlight = tuple(theme.gizmo_secondary)
        gz.alpha = gz.alpha_highlight = 0.75
        gz.use_draw_modal = True
        gz.target_set_prop("depth", prop, "value")
        gz.scale_value = scale_value


    def refresh(self, context: bpy.types.Context) -> None:
        """updating gizmos"""
        target = context.active_object
        if not target:
            return
        basis = target.matrix_world.normalized()
        self.handle.matrix_basis = basis
        self.guides.matrix_basis = basis

    def update(self, context: bpy.types.Context) -> None:
        """updating object"""
        bpy.ops.bim.update_parametric_representation()
        target = context.active_object
        if not target:
            return
        mesh = target.data
        if not isinstance(mesh, bpy.types.Mesh):
            return
        prop = tool.Geometry.get_mesh_props(mesh).ifc_parameters.get("IfcExtrudedAreaSolid/Depth")
        if prop is None:
            return
        self.handle.target_set_prop("offset", prop, "value")
        self.guides.target_set_prop("depth", prop, "value")

    @staticmethod
    def get_scale_value(system: str, length_unit: str) -> float:
        scale_value = 1
        if system == "METRIC":
            if length_unit == "KILOMETERS":
                scale_value /= 1000
            elif length_unit == "CENTIMETERS":
                scale_value *= 100
            elif length_unit == "MILLIMETERS":
                scale_value *= 1000
            elif length_unit == "MICROMETERS":
                scale_value *= 1000000
        elif system == "IMPERIAL":
            if length_unit == "MILES":
                scale_value /= si_conversions["mile"]
            elif length_unit == "FEET":
                scale_value /= si_conversions["foot"]
            elif length_unit == "INCHES":
                scale_value /= si_conversions["inch"]
            elif length_unit == "THOU":
                scale_value /= si_conversions["thou"]
        return scale_value

# ============================================================================
# Core Gizmo Classes
# ============================================================================

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
        self._move_set_cb = _gizmo_modal_context.move_set_cb
        self._active_gizmo = _gizmo_modal_context.active_gizmo
        self._gizmo_group = _gizmo_modal_context.gizmo_group
        self._hidden_gizmos: list[bpy.types.Gizmo] = []
        self._original_color: tuple[float, float, float] | None = None

        self._start_location: Vector = _gizmo_modal_context.start_location or Vector()
        self._axis_direction: Vector = _gizmo_modal_context.axis_direction or Vector((0, 0, 1))
        self._active_obj: bpy.types.Object | None = _gizmo_modal_context.active_obj
        self._delta_scale: float = _gizmo_modal_context.delta_scale
        self._click_offset: float = _gizmo_modal_context.click_offset
        self._mouse_delta: float = 0.0

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

        hidden_set: set[bpy.types.Gizmo] = set()
        for gizmo in self._gizmo_group.gizmos:
            if gizmo != self._active_gizmo:
                gizmo.hide = True
                hidden_set.add(gizmo)
                self._hidden_gizmos.append(gizmo)

        _gizmo_modal_context.hidden_gizmos = hidden_set

    def _restore_gizmo_visibility(self) -> None:
        _gizmo_modal_context.hidden_gizmos = None
        for gizmo in self._hidden_gizmos:
            gizmo.hide = False
        self._hidden_gizmos.clear()

    def modal(self, context, event):
        kb = self._keyboard_input

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

        self._is_snapping = not self._initial_snap_state if event.ctrl else self._initial_snap_state

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

        # Snap the dimension tip (not mouse position) to nearby vertices
        if self._is_snapping and self._active_obj:
            tip_3d = current_3d - self._axis_direction * self._click_offset

            original_snap = tool_settings.use_snap
            tool_settings.use_snap = True
            snapped_tip = snap_to_mesh(tip_3d, context, self._active_obj, current_coord)
            tool_settings.use_snap = original_snap

            if snapped_tip != tip_3d:
                # snap_to_mesh may return a tuple from the cache, ensure it's a Vector
                snapped_tip_vec = Vector(snapped_tip) if not isinstance(snapped_tip, Vector) else snapped_tip
                delta = (snapped_tip_vec - self._start_location).dot(self._axis_direction) + self._click_offset
                set_snap_point(snapped_tip)
            else:
                clear_snap_point()
        else:
            clear_snap_point()

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
            input_str = kb.get_input_string()
            preview = kb.calculate_final_value(self.init_value, self.invert_delta)
            validity = "" if kb.is_valid else " [invalid]"
            header = f"{self.prop_name}: {preview:.3f}m  |  Input: {input_str}_{validity}"
            header += "  |  Click/Enter: Confirm  |  ESC: Cancel"
        else:
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
                    if self._gizmo_group and hasattr(self._gizmo_group, "refresh"):
                        self._gizmo_group.refresh(context)
                    if context.area:
                        context.area.tag_redraw()
                finally:
                    clear_snap_point()
                    clear_snap_cache()
                    _gizmo_modal_context.clear()


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

    # Class-level cached shader (created once, reused across all instances)
    _cached_tri_shader = None

    @classmethod
    def _get_tri_shader(cls):
        """Get cached UNIFORM_COLOR shader for triangles."""
        if cls._cached_tri_shader is None:
            cls._cached_tri_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        return cls._cached_tri_shader

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
        prop_name = getattr(self, "prop_name", "Value")
        bpy.ops.ed.undo_push(message=f"Gizmo: {prop_name}")
        if self.initial_snap_state and self.active_obj:
            build_snap_cache(context, self.active_obj)
            self._snap_cache_built = True

        self._hide_other_gizmos()

        return {"RUNNING_MODAL"}

    def _hide_other_gizmos(self) -> None:
        """Hide all other gizmos in the group during interaction."""
        gizmo_group = getattr(self, "gizmo_group", None)
        if not gizmo_group:
            return

        hidden_set: set[bpy.types.Gizmo] = set()
        for gizmo in gizmo_group.gizmos:
            if gizmo != self:
                gizmo.hide = True
                hidden_set.add(gizmo)

        _gizmo_modal_context.hidden_gizmos = hidden_set

    def _restore_gizmo_visibility(self) -> None:
        """Restore visibility of gizmos hidden during interaction."""
        _gizmo_modal_context.hidden_gizmos = None

    def exit(self, context: bpy.types.Context, cancel: bool) -> None:
        if context.area:
            context.area.header_text_set(None)
        if hasattr(self, "keyboard_input"):
            self.keyboard_input.reset()

        should_invoke_keyboard = (
            not cancel
            and hasattr(self, "_has_dragged")
            and not self._has_dragged
            and self.move_set_cb is not None
        )

        if should_invoke_keyboard:
            _gizmo_modal_context.move_set_cb = self.move_set_cb
            _gizmo_modal_context.active_gizmo = self
            _gizmo_modal_context.gizmo_group = getattr(self, "gizmo_group", None)
            _gizmo_modal_context.start_location = self.start_location.copy()
            _gizmo_modal_context.axis_direction = self.get_axis_direction()
            _gizmo_modal_context.active_obj = self.active_obj
            _gizmo_modal_context.delta_scale = getattr(self, "delta_scale", 1.0)
            bpy.ops.bim.gizmo_value_input(
                "INVOKE_DEFAULT",
                prop_name=getattr(self, "prop_name", "Value"),
                init_value=self.init_value,
                invert_delta=getattr(self, "invert_delta", False),
            )
        elif cancel and self.move_set_cb:
            self.move_set_cb(self.init_value)

        if not should_invoke_keyboard:
            self._restore_gizmo_visibility()

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

        if tool_settings.use_snap and not self._snap_cache_built and self.active_obj:
            build_snap_cache(context, self.active_obj)
            self._snap_cache_built = True

        current_coord = (event.mouse_region_x, event.mouse_region_y)

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
                # snap_to_mesh may return a tuple from the cache, ensure it's a Vector
                snapped_pos_vec = Vector(snapped_pos) if not isinstance(snapped_pos, Vector) else snapped_pos
                delta = (snapped_pos_vec - self.start_location).dot(axis_direction)
                set_snap_point(snapped_pos)
            else:
                clear_snap_point()
        else:
            clear_snap_point()

        if event.shift:
            delta *= PRECISION_MODE_MULTIPLIER

        if getattr(self, "invert_delta", False):
            delta = -delta

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

    def draw_property_tooltip(self, context: bpy.types.Context) -> None:
        """Draw a tooltip showing the property name near the gizmo when highlighted."""
        if not self.is_highlight:
            return
        if not hasattr(self, "prop_name") or not self.prop_name:
            return

        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        gizmo_pos = self.matrix_basis.translation
        screen_pos = location_3d_to_region_2d(region, rv3d, gizmo_pos)
        if not screen_pos:
            return

        prop_display = self.prop_name.replace("_", " ").title()

        font_id = 0
        font_size = tool.Blender.scale_font_size(10)
        blf.size(font_id, font_size)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)

        text_width, text_height = blf.dimensions(font_id, prop_display)

        tooltip_x = screen_pos[0] + 15
        tooltip_y = screen_pos[1] + 15

        with GPUStateScope(depth_test="NONE", blend="ALPHA", ortho_2d=(region.width, region.height)):
            padding = 3
            theme = context.preferences.themes.items()[0][1]
            bg_color = (*theme.user_interface.wcol_menu_back.inner[:3], 0.7)

            vertices = [
                (tooltip_x - padding, tooltip_y - padding),
                (tooltip_x + text_width + padding, tooltip_y - padding),
                (tooltip_x + text_width + padding, tooltip_y + text_height + padding),
                (tooltip_x - padding, tooltip_y + text_height + padding),
            ]
            indices = [(0, 1, 2), (0, 2, 3)]

            shader = self._get_tri_shader()
            shader.bind()
            batch = batch_for_shader(shader, "TRIS", {"pos": vertices}, indices=indices)
            shader.uniform_float("color", bg_color)
            batch.draw(shader)

            blf.color(font_id, self.color_highlight[0], self.color_highlight[1], self.color_highlight[2], 1.0)
            blf.position(font_id, tooltip_x, tooltip_y, 0)
            blf.draw(font_id, prop_display)

        blf.disable(font_id, blf.SHADOW)


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
        self.draw_property_tooltip(context)

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
        self.draw_property_tooltip(context)

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


class GizmoDimension(GizmoMovable):
    """Dimension line gizmo that displays a measurement with extension lines and text.

    The dimension line is drawn from (0, 0, 0) to (length, 0, 0) in local space,
    with extension lines at both ends and a text label showing the formatted value.
    Clicking on the dimension line allows editing the value similar to arrow gizmos.

    The arrows, extension lines, and text are drawn in screen space for constant size,
    while the main dimension line spans the actual world-space distance.
    """

    bl_idname = "BIM_GT_gizmo_dimension"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    # Class-level cached shaders (created once, reused across all instances)
    _cached_line_shader = None
    _cached_tri_shader = None

    @classmethod
    def _get_line_shader(cls):
        """Get cached POLYLINE_UNIFORM_COLOR shader."""
        if cls._cached_line_shader is None:
            cls._cached_line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        return cls._cached_line_shader

    @classmethod
    def _get_tri_shader(cls):
        """Get cached UNIFORM_COLOR shader for triangles."""
        if cls._cached_tri_shader is None:
            cls._cached_tri_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        return cls._cached_tri_shader

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
        "_dimension_length",
        "text_offset_sign",  # -1 to offset text below/left, +1 for above/right (default)
        "show_start_arrow",  # Whether to show arrow at start (origin) of dimension
        "show_end_arrow",  # Whether to show arrow at end of dimension
        "text_alignment",  # "center" (default) or "start" (left-aligned at offset from line)
        "_original_value",  # Original property value before interaction
        "_click_offset",  # Offset from dimension tip to click position (for snap correction)
        "show_extension_lines",  # Whether to show extension lines at dimension endpoints
    )

    ARROW_SIZE = 10
    EXTENSION_LENGTH = 4
    LINE_WIDTH = 2.0
    MIN_PIXELS_FOR_DETAILS = 35
    HIT_WIDTH = 0.03
    MIN_HIT_LENGTH = 0.05

    def _get_clickable_shape(self) -> tuple[tuple[float, float, float], ...]:
        """Generate a simple clickable bar shape (unit length along X)."""
        hw = self.HIT_WIDTH / 2
        return (
            (0, -hw, -hw), (1, -hw, -hw), (0, hw, -hw),
            (0, hw, -hw), (1, -hw, -hw), (1, hw, -hw),
            (0, -hw, hw), (0, hw, hw), (1, -hw, hw),
            (1, -hw, hw), (0, hw, hw), (1, hw, hw),
            (0, -hw, -hw), (0, -hw, hw), (1, -hw, -hw),
            (1, -hw, -hw), (0, -hw, hw), (1, -hw, hw),
            (0, hw, -hw), (1, hw, -hw), (0, hw, hw),
            (0, hw, hw), (1, hw, -hw), (1, hw, hw),
        )

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self._get_clickable_shape())
        self._dimension_length = 1.0
        self.text_offset_sign = 1
        self.show_start_arrow = False
        self.show_end_arrow = True
        self.text_alignment = "center"
        self.show_extension_lines = True

    def draw(self, context: bpy.types.Context) -> None:
        """Draw dimension graphics using the DimensionRenderer singleton."""
        if not hasattr(self, "_dimension_length") or self._dimension_length < 0:
            return

        axis_world = Vector(self.matrix_basis.col[0][:3]).normalized()
        start_world = self.matrix_basis.translation.copy()
        end_world = start_world + axis_world * self._dimension_length

        DimensionRenderer.get_instance().draw(
            context=context,
            start_world=start_world,
            end_world=end_world,
            axis_world=axis_world,
            dimension_length=self._dimension_length,
            color=(self.color[0], self.color[1], self.color[2]),
            alpha=self.alpha,
            is_highlight=self.is_highlight,
            highlight_color=(self.color_highlight[0], self.color_highlight[1], self.color_highlight[2]),
            highlight_alpha=self.alpha_highlight,
            show_start_arrow=getattr(self, "show_start_arrow", False),
            show_end_arrow=getattr(self, "show_end_arrow", True),
            show_extension_lines=getattr(self, "show_extension_lines", True),
            text_offset_sign=getattr(self, "text_offset_sign", 1),
            text_alignment=getattr(self, "text_alignment", "center"),
            prop_name=getattr(self, "prop_name", None),
        )

    def _calculate_screen_endpoints(
        self, context: bpy.types.Context
    ) -> tuple[Vector, Vector, Vector, float] | None:
        """Calculate screen-space endpoints and direction for the dimension line.

        Returns:
            Tuple of (start_screen, end_screen, direction, length_screen) or None if off-screen
        """
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return None

        axis_world = Vector(self.matrix_basis.col[0][:3]).normalized()
        start_world = self.matrix_basis.translation.copy()
        end_world = start_world + axis_world * self._dimension_length

        start_screen = location_3d_to_region_2d(region, rv3d, start_world)
        end_screen = location_3d_to_region_2d(region, rv3d, end_world)

        if not start_screen or not end_screen:
            return None

        direction = Vector((end_screen[0] - start_screen[0], end_screen[1] - start_screen[1]))
        length_screen = direction.length

        actual_value_is_zero = self._dimension_length <= 0.001

        # When screen length is zero due to viewing angle (not actual value being 0), skip drawing
        if length_screen < 1 and not actual_value_is_zero:
            return None

        # When actual value is zero, determine direction from 3D axis projection
        if length_screen < 1 and actual_value_is_zero:
            test_world = start_world + axis_world * 0.1
            test_screen = location_3d_to_region_2d(region, rv3d, test_world)
            if test_screen:
                direction = Vector((test_screen[0] - start_screen[0], test_screen[1] - start_screen[1]))
                if direction.length > 0.001:
                    direction.normalize()
                else:
                    direction = Vector((1, 0))
            else:
                direction = Vector((1, 0))
        else:
            direction.normalize()

        return (Vector(start_screen), Vector(end_screen), direction, length_screen)

    def _build_arrow_triangle(
        self, position: Vector, direction: Vector, perpendicular: Vector, pointing_backward: bool
    ) -> list[tuple[float, float]]:
        """Build triangle vertices for an arrow head.

        Args:
            position: Screen position of the arrow tip
            direction: Normalized direction vector of the dimension line
            perpendicular: Perpendicular vector for arrow width
            pointing_backward: If True, arrow points opposite to direction (for end arrow)

        Returns:
            List of 3 vertex tuples forming the arrow triangle
        """
        sign = -1 if pointing_backward else 1
        arrow_tip = (position[0], position[1])
        arrow_back_left = (
            position[0] + sign * direction[0] * self.ARROW_SIZE + perpendicular[0] * self.ARROW_SIZE * 0.5,
            position[1] + sign * direction[1] * self.ARROW_SIZE + perpendicular[1] * self.ARROW_SIZE * 0.5,
        )
        arrow_back_right = (
            position[0] + sign * direction[0] * self.ARROW_SIZE - perpendicular[0] * self.ARROW_SIZE * 0.5,
            position[1] + sign * direction[1] * self.ARROW_SIZE - perpendicular[1] * self.ARROW_SIZE * 0.5,
        )
        return [arrow_tip, arrow_back_left, arrow_back_right]

    def _build_extension_line_vertices(
        self, position: Vector, perpendicular: Vector
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """Build extension line endpoints perpendicular to the dimension at given position.

        Returns:
            Tuple of (top_vertex, bottom_vertex)
        """
        top = (
            position[0] + perpendicular[0] * self.EXTENSION_LENGTH,
            position[1] + perpendicular[1] * self.EXTENSION_LENGTH,
        )
        bottom = (
            position[0] - perpendicular[0] * self.EXTENSION_LENGTH,
            position[1] - perpendicular[1] * self.EXTENSION_LENGTH,
        )
        return (top, bottom)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        # Scale the clickable shape to match the dimension length
        # The custom_shape is unit length (0 to 1), so we need to scale by _dimension_length
        # Use MIN_HIT_LENGTH to ensure small dimensions are still clickable
        length = getattr(self, "_dimension_length", 1.0)
        hit_length = max(length, self.MIN_HIT_LENGTH)

        # Save original matrix_offset and apply length scaling along local X axis
        # Use matrix_offset for local transforms as per Blender gizmo conventions
        original_offset = self.matrix_offset.copy() if self.matrix_offset else Matrix.Identity(4)
        self.matrix_offset = Matrix.Diagonal((hit_length, 1.0, 1.0, 1.0))

        self.draw_custom_shape(self.custom_shape, select_id=select_id)

        self.matrix_offset = original_offset

    def set_dimension_length(self, length: float) -> None:
        """Set the length of the dimension line with validation."""
        # Validate input: reject NaN, Inf, and non-numeric values
        if not isinstance(length, (int, float)) or math.isnan(length) or math.isinf(length):
            length = 0.0
        # Clamp to valid range (0 to 10000 meters is reasonable for BIM)
        self._dimension_length = max(0.0, min(length, 10000.0))

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set:
        """Initialize dimension gizmo interaction with click-position tracking.

        Click-position tracking prevents jarring value jumps when clicking:

        1. Calculate where user clicked on the dimension axis (click_distance)
        2. Set start_location at the click position so delta=0 there
        3. Store _original_value for cancel/restore functionality
        4. Set init_value = click_distance for direct position mapping

        Result: When dragging, value = click_distance + mouse_delta, giving
        intuitive "drag to position" behavior without any initial jump.
        The value only changes when the user actually drags.
        """
        self.init_value = self.move_get_cb() if self.move_get_cb else 0.0
        self.active_obj = context.active_object
        self.initial_snap_state = context.scene.tool_settings.use_snap
        self.keyboard_input = NumericInputState.create_default()
        self._snap_cache_built = False
        self._has_dragged = False
        self._start_mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        if not hasattr(self, "prop_name") or self.prop_name is None:
            self.prop_name = "Value"

        # Push undo step before making changes so Ctrl+Z can restore original state
        prop_name = getattr(self, "prop_name", "Value")
        bpy.ops.ed.undo_push(message=f"Gizmo: {prop_name}")

        axis_world = Vector(self.matrix_basis.col[0][:3]).normalized()
        gizmo_origin = self.matrix_basis.translation.copy()

        # Calculate where user clicked on the axis
        region = context.region
        rv3d = context.region_data
        click_distance = self.init_value  # Default: assume click at current value endpoint

        if region and rv3d:
            click_coord = (event.mouse_region_x, event.mouse_region_y)
            view_origin = region_2d_to_origin_3d(region, rv3d, click_coord)
            view_direction = region_2d_to_vector_3d(region, rv3d, click_coord)

            result = intersect_line_line(
                view_origin,
                view_origin + view_direction * RAY_CAST_DISTANCE,
                gizmo_origin,
                gizmo_origin + axis_world * RAY_CAST_DISTANCE,
            )

            if result:
                click_on_axis = result[1]
                click_distance = (click_on_axis - gizmo_origin).dot(axis_world)

        # Set start_location at the click position on the axis
        # This makes delta=0 when mouse is at click position
        self.start_location = gizmo_origin + axis_world * click_distance

        # With start_location at click point and init_value = click_distance:
        # - When mouse moves to position p: delta = p - click_distance
        # - final_value = click_distance + (p - click_distance) = p
        # This gives us direct "position = value" behavior.
        # The modal only updates after user has dragged, preserving original value until then.
        self._original_value = self.init_value

        # Why _click_offset: Users rarely click exactly on the dimension tip. Without this
        # correction, the value would jump to match cursor position. By storing the offset
        # between click position and actual tip, we can subtract it during modal updates
        # so the dimension "sticks" to the cursor naturally without initial jumps.
        self._click_offset = click_distance - self._original_value

        self.init_value = click_distance

        if self.initial_snap_state and self.active_obj:
            build_snap_cache(context, self.active_obj)
            self._snap_cache_built = True

        self._hide_other_gizmos()

        return {"RUNNING_MODAL"}

    def _hide_other_gizmos(self) -> None:
        """Hide all other gizmos in the group during interaction."""
        gizmo_group = getattr(self, "gizmo_group", None)
        if not gizmo_group:
            return

        hidden_set: set[bpy.types.Gizmo] = set()
        for gizmo in gizmo_group.gizmos:
            if gizmo != self:
                gizmo.hide = True
                hidden_set.add(gizmo)

        _gizmo_modal_context.hidden_gizmos = hidden_set

    def _restore_gizmo_visibility(self) -> None:
        """Restore visibility of gizmos hidden during interaction."""
        _gizmo_modal_context.hidden_gizmos = None

    def modal(self, context: bpy.types.Context, event: bpy.types.Event, tweak) -> set:
        """Override modal to apply click offset and prevent value jumps."""
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

        if tool_settings.use_snap and not self._snap_cache_built and self.active_obj:
            build_snap_cache(context, self.active_obj)
            self._snap_cache_built = True

        current_coord = (event.mouse_region_x, event.mouse_region_y)

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
            # Snap the dimension tip (not mouse position) to target
            # Calculate where the dimension tip would be with current delta
            # The tip is at: gizmo_origin + axis * (init_value + delta)
            # Since start_location = gizmo_origin + axis * click_offset (where user clicked),
            # the tip is at: current_3d - axis * click_offset
            click_offset = getattr(self, "_click_offset", 0.0)
            tip_3d = current_3d - axis_direction * click_offset

            # Snap the tip position
            snapped_tip = snap_to_mesh(tip_3d, context, self.active_obj, current_coord)
            if snapped_tip != tip_3d:
                # Adjust delta so the dimension tip lands on the snapped position
                # snap_to_mesh may return a tuple from the cache, ensure it's a Vector
                snapped_tip_vec = Vector(snapped_tip) if not isinstance(snapped_tip, Vector) else snapped_tip
                delta = (snapped_tip_vec - self.start_location).dot(axis_direction) + click_offset
                set_snap_point(snapped_tip)
            else:
                clear_snap_point()
        else:
            clear_snap_point()

        if event.shift:
            delta *= PRECISION_MODE_MULTIPLIER

        if getattr(self, "invert_delta", False):
            delta = -delta

        delta_scale = getattr(self, "delta_scale", 1.0)
        delta *= delta_scale

        kb = self.keyboard_input
        final_delta = kb.parsed_value if kb.parsed_value != 0.0 else delta

        # Use original value (before click offset) for relative dragging behavior
        # This ensures no value jump - the value only changes by the drag delta
        original_value = getattr(self, "_original_value", self.init_value)

        # Only update the value if user has dragged or is typing
        # This prevents value jumps when just clicking without dragging
        if self._has_dragged or kb.is_active:
            if self.move_set_cb:
                self.move_set_cb(original_value + final_delta)
            self._update_header(context, original_value + final_delta, tool_settings.use_snap, event.shift)
        else:
            # Show original value in header until user drags
            self._update_header(context, original_value, tool_settings.use_snap, event.shift)

        return {"RUNNING_MODAL"}

    # Minimum clickable length (in world units) when dimension is at 0
    MIN_CLICKABLE_LENGTH = 0.05

    def draw_prepare(self, context: bpy.types.Context) -> None:
        """Update the clickable shape to match dimension length."""
        if not hasattr(self, "_dimension_length"):
            self._dimension_length = 1.0

        # Scale the clickable shape to match the dimension length
        # Use minimum length to ensure there's always a clickable area (for the arrow tip)
        scale_x = max(self._dimension_length, self.MIN_CLICKABLE_LENGTH)
        self.matrix_offset = Matrix.Scale(scale_x, 4, Vector((1, 0, 0)))

    def exit(self, context: bpy.types.Context, cancel: bool) -> None:
        """Handle gizmo exit - restore original value if cancelled."""
        # Clear header text
        if context.area:
            context.area.header_text_set(None)
        if hasattr(self, "keyboard_input"):
            self.keyboard_input.reset()

        should_invoke_keyboard = (
            not cancel
            and hasattr(self, "_has_dragged")
            and not self._has_dragged
            and self.move_set_cb is not None
        )

        if should_invoke_keyboard:
            _gizmo_modal_context.move_set_cb = self.move_set_cb
            _gizmo_modal_context.active_gizmo = self
            _gizmo_modal_context.gizmo_group = getattr(self, "gizmo_group", None)
            # Use click position as start_location so delta=0 at current mouse position
            # This prevents value jump when modal starts
            _gizmo_modal_context.start_location = self.start_location.copy()
            _gizmo_modal_context.axis_direction = self.get_axis_direction()
            _gizmo_modal_context.active_obj = self.active_obj
            _gizmo_modal_context.delta_scale = getattr(self, "delta_scale", 1.0)
            # Pass click offset so modal can snap the dimension tip (not mouse position)
            _gizmo_modal_context.click_offset = getattr(self, "_click_offset", 0.0)
            # Use original value (before click offset adjustment) for the input modal
            original_value = getattr(self, "_original_value", self.init_value)
            bpy.ops.bim.gizmo_value_input(
                "INVOKE_DEFAULT",
                prop_name=getattr(self, "prop_name", "Value"),
                init_value=original_value,
                invert_delta=getattr(self, "invert_delta", False),
            )
        elif cancel and hasattr(self, "_original_value") and self.move_set_cb:
            self.move_set_cb(self._original_value)

        # (keyboard input modal handles its own visibility restoration)
        if not should_invoke_keyboard:
            self._restore_gizmo_visibility()

        if hasattr(self, "initial_snap_state"):
            context.scene.tool_settings.use_snap = self.initial_snap_state
        clear_snap_point()
        clear_snap_cache()


class BaseParametricGizmoGroup:
    """Base mixin for parametric element gizmo groups (doors, windows, stairs, etc.).

    Coordinate System
    =================

    All parametric elements use IFC/Blender coordinate conventions:

    Door/Window local space (looking from interior toward exterior):
    ::

              +Z (up)
               |
               |
               |_______ +X (width)
              /
             /
           +Y (depth, toward exterior)

        - X: Width direction (0 at left edge, positive toward right)
        - Y: Depth direction (0 at interior face, positive toward exterior)
        - Z: Height direction (0 at floor level, positive upward)
        - Origin: Bottom-left corner at interior face

    Stair local space (viewed from above, looking down):
    ::

             +Z (up)
              |   +Y (run/travel)
              |  /
              | /
              |/_______ +X (width)

        - X: Width direction (perpendicular to travel)
        - Y: Run direction (direction of travel up the stair)
        - Z: Height direction (0 at base, positive upward)
        - Origin: Bottom of first riser, left edge

    Gizmo Positioning Strategy
    ==========================

    Gizmos are positioned to avoid overlapping with geometry by using view-dependent
    offsets. The `get_local_view_direction()` method determines which side of the
    element the camera is viewing from, and gizmos are placed on the visible side.

    - Dimension gizmos: Positioned with GIZMO_OFFSET from geometry edges
    - Icon gizmos: Positioned above element using ICON_Z_OFFSET, laid out horizontally
    """

    # === Gizmo Colors ===
    # Match Blender axis convention: X=red, Y=green, Z=blue
    COLOR_RED = (1.0, 0.2, 0.2)
    COLOR_GREEN = (0.1, 0.8, 0.1)
    COLOR_BLUE = (0.3, 0.3, 1.0)

    # === Dimension Gizmo Layout (meters) ===
    ARROW_SCALE = 0.25  # Scale factor for arrow gizmos
    GIZMO_OFFSET = 0.15  # Distance from geometry edge to dimension line

    # === Icon Gizmo Layout (meters) ===
    # Icons are positioned in a horizontal row above the element:
    #   [Validate] [Cancel] [Cycle]
    #      0.0       0.5     0.87   <- X positions (ICON_VALIDATE_X + offset)
    EDITING_ICON_SCALE = 0.2  # Scale for editing icon gizmos (validate, cancel, cycle)
    ICON_VALIDATE_X = 0.0  # X position of validate (checkmark) icon
    ICON_CANCEL_X = 0.5  # X offset from validate for cancel (X) icon
    ICON_CYCLE_X = 0.87  # X offset from validate for cycle (arrow) icon
    ICON_Z_OFFSET = 0.5  # Height above element for icons
    ICON_Y_OFFSET = GIZMO_OFFSET * 2  # Y offset to keep icons clear of geometry

    dimension_gizmo_props: list[DimensionGizmoConfig] = []
    enable_editing_operator: str = ""
    finish_editing_operator: str = ""
    cancel_editing_operator: str = ""
    cycle_type_operator: str = ""

    @classmethod
    def get_color_from_name(cls, color_name: str) -> tuple[float, float, float]:
        """Get color tuple from color name string."""
        colors = {"RED": cls.COLOR_RED, "GREEN": cls.COLOR_GREEN, "BLUE": cls.COLOR_BLUE}
        return colors.get(color_name.upper(), cls.COLOR_RED)

    @classmethod
    def get_arrow_color_from_axis(cls, axis: tuple[int, int, int]) -> tuple[float, float, float]:
        if axis[0] != 0:
            return cls.COLOR_RED
        elif axis[1] != 0:
            return cls.COLOR_GREEN
        return cls.COLOR_BLUE

    def get_axis_rotation_matrix(self, axis: tuple[int, int, int]) -> Matrix:
        """Get a rotation matrix that aligns the X-axis with the given axis direction."""
        axis_vec = Vector(axis).normalized()
        default_dir = Vector((1, 0, 0))
        return default_dir.rotation_difference(axis_vec).to_matrix().to_4x4()

    @staticmethod
    def get_local_view_direction(context: bpy.types.Context, world_matrix: Matrix) -> tuple[bool, bool]:
        """Calculate view direction in element's local space.

        Returns:
            tuple of (viewing_from_negative_y, viewing_from_negative_x)
            - viewing_from_negative_y: True if camera is on the -Y side of the element
            - viewing_from_negative_x: True if camera is on the -X side of the element

        Returns (False, False) if region data is unavailable.
        """
        rv3d = context.region_data
        if not rv3d:
            return False, False

        view_direction = Vector(rv3d.view_rotation @ Vector((0, 0, -1)))
        local_view_dir = world_matrix.inverted().to_3x3() @ view_direction

        viewing_from_negative_y = local_view_dir.y < 0
        viewing_from_negative_x = local_view_dir.x < 0

        return viewing_from_negative_y, viewing_from_negative_x

    def get_y_position_for_view(
        self, props, viewing_from_negative_y: bool, width_attr: str = "width", use_offset: bool = False
    ) -> float:
        """Get Y position based on view direction.

        Common helper for view-dependent gizmo positioning. Elements are positioned
        at Y=0 or Y=width depending on which side the camera is viewing from.

        Args:
            props: Element properties object
            viewing_from_negative_y: True if viewing from -Y side
            width_attr: Property name for element width (default "width", door/window use implicit overall_width logic)
            use_offset: If True, adds/subtracts GIZMO_OFFSET from the position

        Returns:
            Y position: width + offset when viewing from -Y, 0 - offset otherwise
        """
        width = getattr(props, width_attr, 0)
        if viewing_from_negative_y:
            return width + (self.GIZMO_OFFSET if use_offset else 0)
        return -self.GIZMO_OFFSET if use_offset else 0

    def compose_gizmo_matrix(self, translation: Vector, axis: tuple[int, int, int]) -> Matrix:
        """Compose a gizmo transformation matrix from translation and axis.

        This is the standard pattern used for positioning gizmos:
        translation @ rotation where rotation aligns X-axis with the given axis.

        Args:
            translation: Position vector for the gizmo
            axis: Direction axis tuple, e.g., (1, 0, 0) for X-axis

        Returns:
            Combined transformation matrix (translation @ rotation)
        """
        return Matrix.Translation(translation) @ self.get_axis_rotation_matrix(axis)

    def get_lining_y_position_for_view(
        self, props, viewing_from_negative_y: bool, use_offset: bool = True
    ) -> float:
        """Get Y position for lining-based elements (doors, windows) based on view direction.

        For elements with lining_offset property, this calculates the Y position
        relative to lining_offset, flipping sides based on camera view direction.

        Args:
            props: Element properties object (must have lining_offset attribute)
            viewing_from_negative_y: True if viewing from -Y side
            use_offset: If True, adds/subtracts GIZMO_OFFSET (default True)

        Returns:
            Y position: lining_offset + GIZMO_OFFSET when viewing from -Y,
                       lining_offset - GIZMO_OFFSET otherwise
        """
        lining_offset = getattr(props, "lining_offset", 0)
        if viewing_from_negative_y:
            return lining_offset + (self.GIZMO_OFFSET if use_offset else 0)
        return lining_offset - (self.GIZMO_OFFSET if use_offset else 0)

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

    def is_setup_complete(self) -> bool:
        """Check if gizmo setup has been completed.

        Returns True if essential gizmos have been created. This guard
        prevents errors when refresh() is called before setup() completes.

        Subclasses can override to add additional checks.
        """
        return hasattr(self, "validate_gizmo")

    def get_prop_min_value(self, attr_name: str) -> float:
        return 0.0

    def should_hide_gizmo(self, attr_name: str, props) -> bool:
        return not props.is_editing

    def get_element_height(self, props) -> float:
        return getattr(props, "overall_height", getattr(props, "height", 1.0))

    def is_gizmo_hidden_by_modal(self, gizmo: bpy.types.Gizmo) -> bool:
        """Check if a gizmo should be hidden because a modal operator is active.

        This is used to hide all gizmos except the active one during modal
        operations like keyboard value input or mouse dragging.
        """
        hidden_by_modal = _gizmo_modal_context.hidden_gizmos or set()
        return gizmo in hidden_by_modal

    def iter_visible_dimension_gizmos(self) -> Iterator[tuple["DimensionGizmoConfig", bpy.types.Gizmo]]:
        """Iterate over visible dimension gizmos with their configs.

        Yields:
            Tuples of (config, gizmo) for each dimension gizmo that exists and is not hidden.

        Example:
            for config, gizmo in self.iter_visible_dimension_gizmos():
                gizmo.draw_prepare(context)
        """
        for config in getattr(self, "dimension_gizmo_props", []):
            gizmo = getattr(self, f"dimension_{config.attr_name}_gizmo", None)
            if gizmo and not gizmo.hide:
                yield config, gizmo

    def get_dimension_gizmo_if_visible(self, attr_name: str) -> bpy.types.Gizmo | None:
        """Get a dimension gizmo by attribute name if it exists and is visible.

        Simplifies the common pattern:
            if hasattr(self, "dimension_X_gizmo") and not self.dimension_X_gizmo.hide:
        to:
            if gizmo := self.get_dimension_gizmo_if_visible("X"):

        Args:
            attr_name: The dimension attribute name (without "dimension_" prefix and "_gizmo" suffix)

        Returns:
            The gizmo if it exists and is not hidden, None otherwise.
        """
        gizmo = getattr(self, f"dimension_{attr_name}_gizmo", None)
        if gizmo and not gizmo.hide:
            return gizmo
        return None

    def get_gizmo_if_visible(self, gizmo_name: str) -> bpy.types.Gizmo | None:
        """Get a gizmo by attribute name if it exists and is visible.

        Args:
            gizmo_name: The full gizmo attribute name (e.g., "validate_gizmo", "lock_gizmo")

        Returns:
            The gizmo if it exists and is not hidden, None otherwise.
        """
        gizmo = getattr(self, gizmo_name, None)
        if gizmo and not gizmo.hide:
            return gizmo
        return None

    def set_icon_gizmo_position(
        self,
        gizmo_name: str,
        mw: Matrix,
        x: float,
        y: float,
        z: float,
        billboard_rot: Matrix,
        scale: float = 0.5,
    ) -> None:
        """Set an icon gizmo's position with billboard rotation.

        Args:
            gizmo_name: The gizmo attribute name (e.g., "validate_gizmo")
            mw: Object's world matrix
            x, y, z: Local position coordinates
            billboard_rot: Billboard rotation matrix to face camera
            scale: Gizmo scale factor (default 0.5)
        """
        if gz := self.get_gizmo_if_visible(gizmo_name):
            local_transform = Matrix.Translation(Vector((x, y, z))) @ billboard_rot @ Matrix.Scale(scale, 4)
            gz.matrix_basis = mw @ local_transform

    def set_dimension_gizmo_position(
        self,
        attr_name: str,
        mw: Matrix,
        position: Vector,
        axis: tuple[int, int, int],
    ) -> None:
        """Set a dimension gizmo's position if visible.

        Args:
            attr_name: The dimension attribute name (e.g., "overall_width")
            mw: Object's world matrix
            position: Local position as Vector or tuple (x, y, z)
            axis: Direction axis tuple (e.g., (1, 0, 0) for X)
        """
        if gz := self.get_dimension_gizmo_if_visible(attr_name):
            gz.matrix_basis = mw @ self.compose_gizmo_matrix(position, axis)

    def should_hide_dimension_gizmo(
        self, gizmo: bpy.types.Gizmo, config: "DimensionGizmoConfig", props, gizmo_prefs
    ) -> bool:
        """Unified visibility check for dimension gizmos.

        Checks all hide conditions in priority order:
        1. Modal operator hiding
        2. User preference visibility toggle
        3. Editing state
        4. Custom visibility condition from config

        Args:
            gizmo: The gizmo to check
            config: Dimension gizmo configuration
            props: Element properties object
            gizmo_prefs: Gizmo visibility preferences

        Returns:
            True if gizmo should be hidden, False otherwise
        """
        if self.is_gizmo_hidden_by_modal(gizmo):
            return True
        if not getattr(gizmo_prefs, config.attr_name, True):
            return True
        if self.should_hide_gizmo(config.attr_name, props):
            return True
        if config.visibility_condition and not config.visibility_condition(props):
            return True
        return False

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

    def _make_dimension_getter(self, config: DimensionGizmoConfig):
        """Create getter closure for dimension gizmo."""
        if config.compute_value:
            compute_fn = config.compute_value

            def move_get():
                obj = bpy.context.active_object
                if not obj:
                    return 0.0
                return compute_fn(self.get_props(obj))

            return move_get

        attr_name = config.attr_name

        def move_get():
            obj = bpy.context.active_object
            if not obj:
                return 0.0
            return getattr(self.get_props(obj), attr_name, 0.0)

        return move_get

    def _make_dimension_setter(self, config: DimensionGizmoConfig):
        """Create setter closure for dimension gizmo."""
        if config.apply_value:
            apply_fn, min_val = config.apply_value, config.min_value

            def move_set(value):
                obj = bpy.context.active_object
                if not obj:
                    return
                apply_fn(self.get_props(obj), max(min_val, value))

            return move_set

        attr_name, min_val = config.attr_name, config.min_value

        def move_set(value):
            obj = bpy.context.active_object
            if not obj:
                return
            setattr(self.get_props(obj), attr_name, max(min_val, value))

        return move_set

    def setup_dimension_gizmos(self, context: bpy.types.Context) -> None:
        """Set up dimension gizmos from dimension_gizmo_props configuration."""
        prefs = tool.Blender.get_addon_preferences()
        highlight_color = prefs.decorator_color_selected[:3]

        for config in getattr(self, "dimension_gizmo_props", []):
            gizmo = self.gizmos.new("BIM_GT_gizmo_dimension")
            gizmo.move_get_cb = self._make_dimension_getter(config)
            gizmo.move_set_cb = self._make_dimension_setter(config)
            gizmo.axis = Vector(config.axis)
            gizmo.local_axis = Vector(config.axis)
            gizmo.invert_delta = config.invert_delta
            gizmo.delta_scale = config.delta_scale
            gizmo.prop_name = config.prop_name  # Auto-derived in __post_init__
            gizmo.gizmo_group = self
            gizmo.color = self.get_color_from_name(config.color)
            gizmo.color_highlight = highlight_color
            gizmo.alpha = 1.0
            gizmo.use_draw_modal = True
            gizmo.use_draw_scale = False
            gizmo.text_offset_sign = config.text_offset_sign
            gizmo.text_alignment = config.text_alignment
            gizmo.show_start_arrow = config.show_start_arrow
            gizmo.show_end_arrow = config.show_end_arrow
            setattr(self, f"dimension_{config.attr_name}_gizmo", gizmo)

    def update_dimension_gizmos(self, mw: Matrix, props) -> None:
        """Update dimension gizmos from dimension_gizmo_props configuration."""
        gizmo_prefs = self.get_gizmo_prefs()

        for config in getattr(self, "dimension_gizmo_props", []):
            gizmo = getattr(self, f"dimension_{config.attr_name}_gizmo", None)
            if gizmo is None:
                continue

            # Use unified visibility checker
            if self.should_hide_dimension_gizmo(gizmo, config, props, gizmo_prefs):
                gizmo.hide = True
                continue

            gizmo.hide = False

            matrix_method = getattr(self, f"get_dimension_matrix_{config.attr_name}", None)
            base_matrix = matrix_method(props) if matrix_method else Matrix.Identity(4)

            if config.compute_value:
                value = config.compute_value(props)
            else:
                value = getattr(props, config.attr_name, 0.0)

            # Handle negative values by flipping the gizmo direction
            if value < 0:
                # Flip the X axis (dimension direction) for negative values
                flip_matrix = Matrix.Scale(-1, 4, Vector((1, 0, 0)))
                gizmo.matrix_basis = mw @ base_matrix @ flip_matrix
                gizmo.set_dimension_length(abs(value))
            else:
                gizmo.matrix_basis = mw @ base_matrix
                gizmo.set_dimension_length(value)

    def get_icon_y_offset(self, context: bpy.types.Context, mw: Matrix) -> float:
        """Get Y offset for icons based on view direction.

        Returns negative offset when viewing from -Y side (icons move to -Y),
        positive offset when viewing from +Y side (icons move to +Y).
        Subclasses can override to customize behavior.
        """
        return 0.0

    def update_editing_gizmos(self, context: bpy.types.Context, mw: Matrix, props) -> None:
        """Update editing icon gizmo positions to billboard toward camera."""
        icon_z = self.get_element_height(props) + self.ICON_Z_OFFSET
        icon_y = self.get_icon_y_offset(context, mw)
        billboard_rot = get_billboard_rotation(context)

        # This ensures icons face camera regardless of object rotation
        local_pos_validate = Vector((self.ICON_VALIDATE_X, icon_y, icon_z))
        world_pos_validate = mw @ local_pos_validate

        icon_matrix_base = Matrix.Translation(world_pos_validate) @ billboard_rot @ Matrix.Scale(0.5, 4)

        if props.is_editing:
            self.pen_gizmo.hide = True
            self.validate_gizmo.hide = self.is_gizmo_hidden_by_modal(self.validate_gizmo)
            self.validate_gizmo.matrix_basis = icon_matrix_base

            self.cancel_gizmo.hide = self.is_gizmo_hidden_by_modal(self.cancel_gizmo)
            local_pos_cancel = Vector((self.ICON_VALIDATE_X + self.ICON_CANCEL_X, icon_y, icon_z))
            world_pos_cancel = mw @ local_pos_cancel
            self.cancel_gizmo.matrix_basis = Matrix.Translation(world_pos_cancel) @ billboard_rot @ Matrix.Scale(0.5, 4)

            if self.cycle_type_operator:
                self.cycle_gizmo.hide = self.is_gizmo_hidden_by_modal(self.cycle_gizmo)
                local_pos_cycle = Vector((self.ICON_VALIDATE_X + self.ICON_CYCLE_X, icon_y, icon_z))
                world_pos_cycle = mw @ local_pos_cycle
                self.cycle_gizmo.matrix_basis = Matrix.Translation(world_pos_cycle) @ billboard_rot @ Matrix.Scale(0.30, 4)
        else:
            self.pen_gizmo.hide = self.is_gizmo_hidden_by_modal(self.pen_gizmo)
            self.pen_gizmo.matrix_basis = icon_matrix_base
            self.validate_gizmo.hide = True
            self.cancel_gizmo.hide = True
            if self.cycle_type_operator:
                self.cycle_gizmo.hide = True

    def draw_prepare(self, context: bpy.types.Context) -> None:
        """Called before drawing - updates gizmos to face camera.

        This method updates editing gizmos and dimension gizmos.
        Subclasses can override _update_dimension_gizmo_positions() to customize
        dimension gizmo positioning based on view direction.
        """
        obj = context.active_object
        if not obj:
            return
        props = self.get_props(obj)
        mw = obj.matrix_world
        self.update_editing_gizmos(context, mw, props)

        self._update_dimension_gizmo_positions(context, mw, props)

        # Prepare dimension gizmos for drawing
        for _, gizmo in self.iter_visible_dimension_gizmos():
            gizmo.draw_prepare(context)

    def _update_dimension_gizmo_positions(
        self, context: bpy.types.Context, mw: "Matrix", props  # noqa: ARG002
    ) -> None:
        """Update dimension gizmo positions based on view direction.

        Override this method in subclasses to implement view-dependent
        positioning for dimension gizmos.

        Args:
            context: Blender context
            mw: Object's world matrix
            props: Element properties object
        """
