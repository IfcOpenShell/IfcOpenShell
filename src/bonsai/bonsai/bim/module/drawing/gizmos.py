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
#
# This file was modified with the assistance of an AI coding tool.

"""Viewport gizmos for parametric BIM element editing.

Feature gizmo groups (one per parametric type) declare their gizmos via
``DimensionGizmoConfig`` and inherit shared setup / refresh / snapping
machinery from ``BaseParametricGizmoGroup``. Single-click icons bind to
operators via ``target_set_operator``; drag handles inherit modal state
from ``GizmoMovable``.
"""

__all__ = [  # noqa: RUF022 (unsorted `__all__`)
    "GizmoColor",
    "GizmoAxis",
    "TextAlignment",
    "CoordinateSpace",
    "ModalState",
    "DimensionGizmoConfig",
    "SwingArcConfig",
    "ViewDirection",
    "GizmoModalContext",
    "get_modal_context",
    "get_validated_modal_context",
    "ParametricProps",
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
    "GizmoLockOpen",
    "GizmoLockClosed",
    "GizmoArc",
    "GizmoPen",
    "GizmoValidate",
    "GizmoCancel",
    "GizmoPlus",
    "GizmoMinus",
    "GizmoArrayParent",
    "GizmoArrayAll",
    "GizmoArrayLayerIndicator",
    "GizmoCycle",
    "GizmoMenu",
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

import math
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Literal,
    Optional,
    Protocol,
    runtime_checkable,
)

import blf
import bpy
import gpu
import ifcopenshell.util.element
import numpy as np
from bpy import types
from bpy_extras import view3d_utils
from bpy_extras.view3d_utils import (
    location_3d_to_region_2d,
    region_2d_to_origin_3d,
    region_2d_to_vector_3d,
)
from gpu_extras.batch import batch_for_shader
from ifcopenshell.util.unit import si_conversions
from mathutils import Matrix, Vector, geometry
from mathutils.geometry import intersect_line_line
from mathutils.kdtree import KDTree

import bonsai.tool as tool
from bonsai.bim.module.drawing.shaders import ExtrusionGuidesShader

if TYPE_CHECKING:
    import bmesh

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

# Door-swing arc: start a couple of degrees off the jamb so the arc tip stays
# visible; full quarter-turn for the standard 90-degree swing.
DOOR_SWING_ANGLE_MIN = 2.0
DOOR_SWING_ANGLE_MAX = 90.0

# Default scale factor for billboarded icons (Blender-unit visual size).
DEFAULT_BILLBOARD_SCALE = 0.5

# Shared gizmo color constants. Re-exported as class attributes on
# BaseParametricGizmoGroup so callers can use either ``self.COLOR_GREEN``
# from inside a gizmo group or the module-level constant from a class body
# (e.g. IconSlot declarations) without a forward-reference issue. Match
# Blender's axis convention: X=red, Y=green, Z=blue.
COLOR_RED = (1.0, 0.2, 0.2)
COLOR_GREEN = (0.1, 0.8, 0.1)
COLOR_BLUE = (0.3, 0.3, 1.0)
COLOR_NEUTRAL = (1.0, 1.0, 1.0)

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


def _is_transform_modal_active(context) -> bool:
    """Module-local alias for ``tool.Blender.is_transform_modal_active``.

    Preserved as a name so AST scans and call sites in this file stay
    decoupled from the helper's home module.
    """
    return tool.Blender.is_transform_modal_active(context)


def _hide_all_non_modal_gizmos(group) -> None:
    """Set ``hide = True`` on every gizmo in ``group`` whose own ``is_modal``
    is False. Used by parametric ``draw_prepare`` to suppress visible
    re-positioning while a transform modal is dragging ``matrix_world``."""
    for gz in group.gizmos:
        if not getattr(gz, "is_modal", False):
            gz.hide = True


def apply_transform_modal_draw_gate(group, context) -> bool:
    """Combined gate for ``draw_prepare`` overrides: hide non-modal gizmos and
    return ``True`` when a Blender transform modal is dragging matrix_world.

    Returns ``False`` when no transform modal is active so callers can fall
    through to their normal positioning logic. ``True`` means the caller must
    early-return without touching matrix_basis — the hidden gizmos will be
    re-shown on the next idle frame once the modal exits."""
    if not _is_transform_modal_active(context):
        return False
    _hide_all_non_modal_gizmos(group)
    return True


class GizmoColor(Enum):
    """Color identifiers for dimension gizmos.

    Maps axis directions to colors following BIM/CAD conventions:
    - RED: X-axis (width)
    - GREEN: Y-axis (depth)
    - BLUE: Z-axis (height)

    Use GizmoColor.from_axis() to auto-derive color from axis direction.
    """

    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"

    @classmethod
    def from_axis(cls, axis: tuple[int, int, int]) -> "GizmoColor":
        """Derive color from axis direction.

        Args:
            axis: Direction tuple (x, y, z) with at least one non-zero component.

        Returns:
            GizmoColor based on the first non-zero axis component.
        """
        if axis[0] != 0:
            return cls.RED
        elif axis[1] != 0:
            return cls.GREEN
        return cls.BLUE


class TextAlignment(Enum):
    """Text alignment options for dimension gizmo labels.

    Controls where the dimension value text is positioned along the dimension line.
    """

    START = "start"  # Align text to the start of the dimension line
    CENTER = "center"  # Center text on the dimension line (default)
    END = "end"  # Align text to the end of the dimension line


# Type alias for gizmo axis direction tuples
# Each component must be -1, 0, or 1 to indicate direction along that axis
GizmoAxis = tuple[Literal[-1, 0, 1], Literal[-1, 0, 1], Literal[-1, 0, 1]]


class CoordinateSpace(Enum):
    """Coordinate space identifiers for gizmo positioning.

    Clarifies which space a position or direction is expressed in:
    - LOCAL: Object-local coordinates (relative to element origin)
    - WORLD: World/scene coordinates (absolute position)
    - SCREEN: 2D screen-space coordinates (pixels)

    Usage:
        # Document coordinate space in function signatures
        def get_position(self, space: CoordinateSpace = CoordinateSpace.LOCAL) -> Vector:
            ...

        # Or use as documentation in comments
        local_pos = Vector((0, 0, 1))  # CoordinateSpace.LOCAL
        world_pos = matrix_world @ local_pos  # CoordinateSpace.WORLD
    """

    LOCAL = "local"  # Object-local space (relative to element matrix_world)
    WORLD = "world"  # World/scene space (absolute coordinates)
    SCREEN = "screen"  # 2D screen space (pixel coordinates)


class ModalState(Enum):
    """State machine states for modal gizmo operations.

    Used to track the current interaction mode during gizmo manipulation.
    Helps organize modal operator logic and determine valid state transitions.

    States:
        IDLE: No interaction active, waiting for user input
        DRAGGING: User is dragging the gizmo with the mouse
        KEYBOARD_INPUT: User is typing a numeric value
        SNAPPING: Dragging with snap enabled (Ctrl held)
        PRECISION: Dragging with precision mode (Shift held)

    State transitions:
        IDLE -> DRAGGING: Mouse press on gizmo
        IDLE -> KEYBOARD_INPUT: Numeric key press
        DRAGGING -> SNAPPING: Ctrl pressed during drag
        DRAGGING -> PRECISION: Shift pressed during drag
        SNAPPING -> DRAGGING: Ctrl released
        PRECISION -> DRAGGING: Shift released
        * -> IDLE: Mouse release, Enter, Escape
    """

    IDLE = "idle"
    DRAGGING = "dragging"
    KEYBOARD_INPUT = "keyboard_input"
    SNAPPING = "snapping"
    PRECISION = "precision"

    def is_active(self) -> bool:
        """Check if this state represents an active interaction."""
        return self != ModalState.IDLE

    def allows_keyboard_input(self) -> bool:
        """Check if this state allows transitioning to keyboard input."""
        return self in (ModalState.IDLE, ModalState.DRAGGING)


@dataclass(slots=True)
class GizmoModalContext:
    """Typed context for modal gizmo operations.

    Passes state between a gizmo and the BIM_OT_gizmo_value_input modal operator.
    Blender ID properties cannot carry function callbacks, so a module-level
    instance carries them out-of-band.

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


def get_modal_context() -> GizmoModalContext:
    """Get the global modal gizmo context.

    Provides access to the module-level context without exposing the private variable.
    Use this when reading context values that may be None.

    Returns:
        The global GizmoModalContext instance.
    """
    return _gizmo_modal_context


def get_validated_modal_context() -> GizmoModalContext:
    """Get the modal context, validating that essential fields are set.

    Use this when the context is expected to be fully initialized (e.g., during
    modal operator execution). Raises RuntimeError if the context is incomplete.

    Returns:
        The global GizmoModalContext instance with essential fields validated.

    Raises:
        RuntimeError: If active_gizmo or gizmo_group is None.
    """
    ctx = _gizmo_modal_context
    if ctx.active_gizmo is None:
        raise RuntimeError("Modal context not initialized: active_gizmo is None")
    if ctx.gizmo_group is None:
        raise RuntimeError("Modal context not initialized: gizmo_group is None")
    return ctx


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

    Manages text drawing operations including value text, property
    tooltips, and text backgrounds.

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
        alignment: TextAlignment | str = TextAlignment.CENTER,
        display_text: str | None = None,
    ) -> None:
        """Draw formatted dimension value text at the given screen position.

        Args:
            context: Blender context
            screen_pos: Screen-space position (x, y)
            perpendicular: Perpendicular direction vector for offset
            value: Dimension value to format and display
            color: Text color (r, g, b)
            offset_sign: 1 for above/right, -1 for below/left
            alignment: TextAlignment enum value
            display_text: Pre-formatted label. If provided, used verbatim instead of
                formatting `value`.
        """
        # Normalize string to enum for comparison
        if isinstance(alignment, str):
            alignment = TextAlignment(alignment)

        if display_text is not None:
            text = display_text
        else:
            is_negative = value < 0
            text = tool.Unit.format_distance(abs(value))
            if is_negative:
                text = "-" + text

        font_id = 0
        font_size = tool.Blender.scale_font_size(self.VALUE_FONT_SIZE)
        blf.size(font_id, font_size)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)

        text_width, text_height = blf.dimensions(font_id, text)
        offset_distance = (text_height + 4) * offset_sign

        if alignment == TextAlignment.START:
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


@dataclass(slots=True, frozen=True)
class ViewDirection:
    """Immutable representation of camera view direction relative to an element's local space.

    Provides a cleaner API than tuple unpacking for view-dependent gizmo positioning.

    With:
        view = self.get_view_direction(context, mw)
        if view.from_back: ...

    Attributes:
        from_negative_y: True if camera is on the -Y side (viewing from "back")
        from_negative_x: True if camera is on the -X side (viewing from "left")

    Properties:
        from_back: Alias for from_negative_y (more intuitive for doors/windows)
        from_front: Inverse of from_back
        from_left: Alias for from_negative_x
        from_right: Inverse of from_left
    """

    from_negative_y: bool = False
    from_negative_x: bool = False

    @property
    def from_back(self) -> bool:
        """True if viewing from the back (-Y) side of the element."""
        return self.from_negative_y

    @property
    def from_front(self) -> bool:
        """True if viewing from the front (+Y) side of the element."""
        return not self.from_negative_y

    @property
    def from_left(self) -> bool:
        """True if viewing from the left (-X) side of the element."""
        return self.from_negative_x

    @property
    def from_right(self) -> bool:
        """True if viewing from the right (+X) side of the element."""
        return not self.from_negative_x

    @classmethod
    def from_context(cls, context: bpy.types.Context, world_matrix: Matrix) -> "ViewDirection":
        """Create ViewDirection from Blender context and object world matrix.

        Args:
            context: Blender context with region_data
            world_matrix: Object's world transformation matrix

        Returns:
            ViewDirection instance, defaults to (False, False) if region data unavailable.
        """
        rv3d = context.region_data
        if not rv3d:
            return cls()

        view_direction = Vector(rv3d.view_rotation @ Vector((0, 0, -1)))
        local_view_dir = world_matrix.inverted().to_3x3() @ view_direction

        return cls(
            from_negative_y=local_view_dir.y < 0,
            from_negative_x=local_view_dir.x < 0,
        )


# Eight unit-length directions for the multi-pass outline shared by every
# icon-class gizmo and by ``DimensionRenderer``'s arrowhead halo. The
# silhouette is rendered once per direction, offset by an outline width
# along that direction; the union approximates a circular dilation —
# a uniform halo on every side. Cardinals are length 1; diagonals use
# sqrt(0.5) components so every direction is at the same Euclidean
# distance from the origin. Uniform scaling around the local origin
# can't replace this: for asymmetric / multi-part geometry it just pushes
# parts further from the origin, which reads as a directional shift
# rather than an outline.
_OUTLINE_DIRECTIONS_8 = (
    (1.0, 0.0),
    (-1.0, 0.0),
    (0.0, 1.0),
    (0.0, -1.0),
    (0.7071067811865476, 0.7071067811865476),
    (-0.7071067811865476, 0.7071067811865476),
    (0.7071067811865476, -0.7071067811865476),
    (-0.7071067811865476, -0.7071067811865476),
)


class DimensionRenderer:
    """Singleton renderer for dimension line graphics. Draws the dimension
    line, end arrows, and extension lines in screen space."""

    _instance: "DimensionRenderer | None" = None
    _line_shader = None
    _tri_shader = None

    # Visual parameters (in pixels)
    ARROW_SIZE = 10
    EXTENSION_LENGTH = 4
    LINE_WIDTH = 2.0
    MIN_PIXELS_FOR_DETAILS = 35
    # Outline underlay so the dimension stays legible against same-color
    # backgrounds (white line on white wall). The line uses a single wider
    # dark pass (one extra pixel on each side); the arrowheads use the same
    # 8-direction halo technique as icon-class gizmos because a uniform
    # widening of a triangle is shape-dependent, not a uniform halo.
    OUTLINE_LINE_WIDTH_INCREASE = 2.0
    OUTLINE_LINE_ALPHA = 0.7
    OUTLINE_ARROW_PX = 1.5
    OUTLINE_ARROW_ALPHA = 0.4

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
        text_alignment: TextAlignment = TextAlignment.CENTER,
        prop_name: str | None = None,
        display_value: float | None = None,
        display_text: str | None = None,
    ) -> None:
        """Draw complete dimension graphics in screen space.

        Args:
            context: Blender context
            start_world: World-space start position
            end_world: World-space end position
            axis_world: Normalized axis direction in world space
            dimension_length: Length of the dimension (for drawing the line)
            color: Base color (r, g, b)
            alpha: Base alpha
            is_highlight: Whether gizmo is highlighted/hovered
            highlight_color: Highlight color (r, g, b)
            highlight_alpha: Highlight alpha
            show_start_arrow: Whether to show arrow at start
            show_end_arrow: Whether to show arrow at end
            show_extension_lines: Whether to show extension lines
            text_offset_sign: 1 for above/right, -1 for below/left
            text_alignment: TextAlignment enum for text positioning
            prop_name: Property name for tooltip (shown when highlighted)
            display_value: Value to display as text (can be negative); uses dimension_length if None
            display_text: Pre-formatted label string. If provided, used verbatim instead of
                formatting `display_value` via tool.Unit.format_distance.
        """
        if dimension_length < 0:
            return

        # Use display_value for text if provided, otherwise use dimension_length
        text_value = display_value if display_value is not None else dimension_length

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

        # Force the main pass fully opaque so the dark outline underlay
        # doesn't bleed through and grey out the line/arrows.
        if is_highlight:
            draw_color = (*highlight_color, 1.0)
        else:
            draw_color = (*color, 1.0)

        with GPUStateScope(depth_test="NONE", blend="ALPHA", ortho_2d=(region.width, region.height)):
            shader = self._get_line_shader()
            shader.bind()
            shader.uniform_float("viewportSize", (region.width, region.height))

            line_batch = batch_for_shader(shader, "LINES", {"pos": vertices}, indices=indices)
            # Underlay for legibility against same-colour backgrounds.
            shader.uniform_float("lineWidth", self.LINE_WIDTH + self.OUTLINE_LINE_WIDTH_INCREASE)
            shader.uniform_float("color", (0.0, 0.0, 0.0, self.OUTLINE_LINE_ALPHA))
            line_batch.draw(shader)
            shader.uniform_float("lineWidth", self.LINE_WIDTH)
            shader.uniform_float("color", draw_color)
            line_batch.draw(shader)

            if arrow_triangles:
                tri_shader = self._get_tri_shader()
                tri_shader.bind()
                tri_batch = batch_for_shader(tri_shader, "TRIS", {"pos": arrow_triangles})
                # Same eight-direction halo as the icon mixin, in screen-pixel units.
                tri_shader.uniform_float("color", (0.0, 0.0, 0.0, self.OUTLINE_ARROW_ALPHA))
                for dx, dy in _OUTLINE_DIRECTIONS_8:
                    with gpu.matrix.push_pop():
                        gpu.matrix.multiply_matrix(
                            Matrix.Translation((dx * self.OUTLINE_ARROW_PX, dy * self.OUTLINE_ARROW_PX, 0.0))
                        )
                        tri_batch.draw(tri_shader)
                tri_shader.uniform_float("color", draw_color)
                tri_batch.draw(tri_shader)

            if length_screen >= self.MIN_PIXELS_FOR_DETAILS:
                center_screen = (
                    (start_screen[0] + end_screen[0]) / 2,
                    (start_screen[1] + end_screen[1]) / 2,
                )
                text_color = highlight_color if is_highlight else color
                DimensionTextRenderer.get_instance().draw_value_text(
                    context,
                    center_screen,
                    perpendicular,
                    text_value,
                    text_color,
                    text_offset_sign,
                    text_alignment,
                    display_text,
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


@dataclass(slots=True, frozen=True)
class SnapCache:
    """Immutable snap cache with combined KD-tree for vertex snapping."""

    # Combined KD-tree with all world vertices from all objects
    kd_tree: KDTree
    # All world vertices indexed by global vertex index (tuples for memory efficiency)
    all_vertices: list[tuple[float, float, float]]


@dataclass(slots=True)
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
        is_valid, value = tool.Unit.parse_distance_string(input_str)

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


@runtime_checkable
class ParametricProps(Protocol):
    """Protocol defining the common interface for parametric element properties.

    All parametric property classes (BIMDoorProperties, BIMWindowProperties,
    BIMStairProperties, etc.) should implement this interface. This enables
    type-safe code in BaseParametricGizmoGroup without importing concrete classes.

    Example:
        def update_gizmos(self, props: ParametricProps) -> None:
            if props.is_editing:
                # Safe to access common properties
                ...
    """

    is_editing: bool


@dataclass(slots=True)
class BaseValueGizmoConfig:
    """Shared scaffolding for every parametric value gizmo (dimensions, counts, …).

    Holds the attribute binding, axis/placement hints, color, and read/write hooks
    that any value-driven gizmo declared on a ``BaseParametricGizmoGroup`` needs.
    Continuous-distance specifics (arrows, text alignment, snap scaling) belong on
    ``DimensionGizmoConfig``; integer-stepper specifics belong on the future
    ``CountGizmoConfig`` sibling.

    Color and prop_name are auto-derived if not specified:
        - axis (1,0,0) or (-1,0,0) -> RED
        - axis (0,1,0) or (0,-1,0) -> GREEN
        - axis (0,0,1) or (0,0,-1) -> BLUE
        - prop_name: "attr_name" -> "Attr Name" (underscores to spaces, title case)

    Attributes:
        attr_name: Property name to bind to (e.g., "overall_width"). Used to generate
            the per-gizmo attribute on the gizmo group.
        axis: Direction tuple (x, y, z). Determines color if not specified and defines
            the drag/orientation direction. Use negative values for reversed directions.
        color: Optional override. One of "RED", "GREEN", "BLUE". Auto-derived from axis.
        prop_name: Display name for tooltips. Defaults to attr_name with underscores
            replaced by spaces and title-cased.
        compute_value: Optional function(props) -> value for computed values.
            If None, reads directly from getattr(props, attr_name).
        apply_value: Optional function(props, value) to apply new values after edit.
            If None, uses setattr(props, attr_name, value).
        visibility_condition: Optional function(props) -> bool. If returns False,
            the gizmo is hidden. Used for conditional gizmos.
        matrix_position: Optional function(props) -> Vector for gizmo position.
            The returned Vector is the local-space position where the gizmo origin
            will be placed. Combined with axis to create the full transformation matrix.
    """

    attr_name: str
    axis: GizmoAxis
    color: GizmoColor | str | None = None  # GizmoColor enum, string ("RED"/"GREEN"/"BLUE"), or None for auto
    prop_name: str | None = None
    compute_value: Callable[[Any], Any] | None = None
    apply_value: Callable[[Any, Any], None] | None = None
    visibility_condition: Callable[[Any], bool] | None = None
    # Optional: function(props) -> Vector position.
    #
    # SUBTLE: presence of this callable doubles as a *trigger* in
    # ``BaseParametricGizmoGroup.update_dimension_gizmos`` — when set, the
    # gizmo's per-frame matrix is composed via ``compose_gizmo_matrix``,
    # which calls ``get_axis_rotation_matrix(self.axis)`` to align the
    # gizmo's intrinsic +X direction with ``self.axis`` in object-local
    # space. When this is None, the framework falls back to
    # ``base_matrix = Identity`` (no axis rotation), and the dimension's
    # visual line renders along the object's local +X regardless of
    # ``self.axis``. If your dimension's axis is not local +X, you MUST
    # pass a ``matrix_position`` callable — even ``lambda _props: Vector((0, 0, 0))``
    # is enough to flip the branch. The wall pattern uses
    # ``set_dimension_gizmo_position`` for this; the declarative pattern
    # uses ``matrix_position`` for the same effect.
    matrix_position: Callable[[Any], "Vector"] | None = None

    def __post_init__(self):
        # Validate attr_name
        if not self.attr_name or not isinstance(self.attr_name, str):
            raise ValueError("attr_name must be a non-empty string")

        # Validate axis
        if len(self.axis) != 3:
            raise ValueError(f"axis must be a 3-tuple, got {len(self.axis)} elements")
        if not any(self.axis):
            raise ValueError("axis must have at least one non-zero component")

        # Normalize and validate color
        if self.color is None:
            # Auto-derive from axis direction
            self.color = GizmoColor.from_axis(self.axis)
        elif isinstance(self.color, str):
            # Convert string to enum
            try:
                self.color = GizmoColor(self.color)
            except ValueError:
                raise ValueError(f"color must be 'RED', 'GREEN', or 'BLUE', got '{self.color}'")
        elif not isinstance(self.color, GizmoColor):
            raise ValueError(f"color must be GizmoColor enum, string, or None, got {type(self.color)}")

        # Auto-derive prop_name from attr_name if not specified
        if self.prop_name is None:
            self.prop_name = self.attr_name.replace("_", " ").title()


@dataclass(slots=True)
class CountGizmoConfig(BaseValueGizmoConfig):
    """Configuration for an integer-stepper gizmo (drag-snap-to-int handle).

    Renders as a fixed-size bar (no arrows, no extension lines) with the integer
    value as text. Built on top of ``BIM_GT_gizmo_dimension`` — the underlying
    gizmo type is reused; only the configuration differs (arrows/extension
    lines off, fixed visual length, ``move_set_cb`` wrapped to snap-to-int and
    clamp to [min_count, max_count]).

    Examples:
        # Basic count - simple integer stepper bound to props.count
        CountGizmoConfig(
            attr_name="count",
            axis=(1, 0, 0),
            min_count=1,
            max_count=999,
        )

        # With keyboard sensitivity tuning - drag 1m → count += 5
        CountGizmoConfig(
            attr_name="count",
            axis=(1, 0, 0),
            delta_scale=5.0,
        )

    See ``BaseValueGizmoConfig`` for the shared attributes (attr_name, axis,
    color, prop_name, compute_value, apply_value, visibility_condition,
    matrix_position).

    Count-specific attributes:
        min_count: Minimum allowed value when dragging (default 1).
        max_count: Maximum allowed value when dragging (default 999).
        step: Integer step size; drag values round to nearest multiple of step.
        delta_scale: Drag-to-count multiplier. Higher = more counts per meter
            of drag. Default 2.0 = roughly half a count per metre, tuned so a
            short flick covers small counts without overshoot.
        count_formatter: Optional function(props, value) -> str for the count
            label. If None, falls back to ``str(int(value))``.
    """

    min_count: int = 1
    max_count: int = 999
    step: int = 1
    delta_scale: float = 2.0
    count_formatter: Callable[[Any, int], str] | None = None

    def __post_init__(self):
        BaseValueGizmoConfig.__post_init__(self)
        if self.min_count > self.max_count:
            raise ValueError(f"min_count {self.min_count} must be <= max_count {self.max_count}")
        if self.step < 1:
            raise ValueError(f"step must be >= 1, got {self.step}")


@dataclass(slots=True)
class DimensionGizmoConfig(BaseValueGizmoConfig):
    """Configuration for a continuous-float dimension line gizmo.

    Used to declaratively configure dimension line gizmos in BaseParametricGizmoGroup subclasses.
    This enables a data-driven approach that reduces boilerplate code for setting up
    dimension gizmos with consistent behavior.

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

    See ``BaseValueGizmoConfig`` for the shared attributes (attr_name, axis, color,
    prop_name, compute_value, apply_value, visibility_condition, matrix_position).

    Dimension-specific attributes:
        min_value: Lower bound the default ``attr_name`` setter clamps to
            before writing (default 0.0 — the floor for natural non-negative
            dimensions like ``wall_thickness``, ``casing_thickness``,
            ``overall_width``). Only consulted when ``apply_value`` is None;
            when a custom ``apply_value`` is supplied, the callback owns any
            bounding (it can pass through, absolutise, or reproject the sign
            as needed).
        invert_delta: If True, reverses the drag direction effect.
        delta_scale: Multiplier for drag delta (default 1.0). Use <1 for fine control.
        text_offset_sign: 1 or -1 to position text above/below dimension line.
        text_alignment: "start", "center", or "end" for text positioning along line.
        show_start_arrow: Whether to show arrow at start point (default False).
        show_end_arrow: Whether to show arrow at end point (default True).
        text_formatter: Optional function(props, value) -> str for the dimension label.
            Receives the props bag and the post-`compute_value` display value
            (i.e. the same number `apply_value` consumes during drag — for the
            wall slope gizmo this is the displacement, NOT the underlying
            `x_angle`). The raw underlying attribute is accessible as
            `getattr(props, attr_name)`. If None, falls back to the default
            `tool.Unit.format_distance(abs(value))` with negative-sign handling.
    """

    min_value: float = 0.0
    invert_delta: bool = False
    delta_scale: float = 1.0
    text_offset_sign: Literal[-1, 1] = 1
    text_alignment: TextAlignment | str = TextAlignment.CENTER
    show_start_arrow: bool = False
    show_end_arrow: bool = True
    text_formatter: Callable[[Any, float], str] | None = None  # Optional: function(props, value) -> label text
    schematic_visible_length: float | None = None  # Override the schematic group's default tag length for this dim.
    # In-place dimensions ignore this — it only affects schematic-group rendering.

    def __post_init__(self):
        # @dataclass(slots=True) rebinds the class in module namespace, leaving super()'s
        # implicit __class__ cell pointing at the pre-decorator class. Call the parent
        # __post_init__ directly to avoid the resulting TypeError.
        BaseValueGizmoConfig.__post_init__(self)

        # Normalize and validate text_alignment
        if isinstance(self.text_alignment, str):
            try:
                self.text_alignment = TextAlignment(self.text_alignment)
            except ValueError:
                valid = [e.value for e in TextAlignment]
                raise ValueError(f"text_alignment must be one of {valid}, got '{self.text_alignment}'")
        elif not isinstance(self.text_alignment, TextAlignment):
            raise ValueError(f"text_alignment must be TextAlignment enum or string, got {type(self.text_alignment)}")

        # Validate text_offset_sign
        if self.text_offset_sign not in (1, -1):
            raise ValueError(f"text_offset_sign must be 1 or -1, got {self.text_offset_sign}")

    def __repr__(self) -> str:
        """Concise representation showing key configuration values."""
        parts = [f"attr_name={self.attr_name!r}", f"axis={self.axis}"]
        if self.color:
            parts.append(f"color={self.color.name}")
        if self.visibility_condition:
            parts.append("visibility_condition=<fn>")
        if self.matrix_position:
            parts.append("matrix_position=<fn>")
        if self.compute_value:
            parts.append("compute_value=<fn>")
        if self.min_value != 0.0:
            parts.append(f"min_value={self.min_value}")
        if self.invert_delta:
            parts.append("invert_delta=True")
        return f"DimensionGizmoConfig({', '.join(parts)})"


@dataclass(slots=True)
class IconActionConfig:
    """Declarative config for a single icon-action gizmo (one-shot click,
    no value, no drag state).

    ``visibility_condition``: optional ``(obj) -> bool`` predicate hiding
    this one icon. ``None`` means always visible while the group is polled."""

    name: str
    icon: str
    operator: str
    visibility_condition: Callable[[Any], bool] | None = None


@dataclass(slots=True)
class SwingArcConfig:
    """Declarative config for one swing-arc panel — a pair of ``GizmoArc``
    instances representing a single hinged panel's two possible open sides.

    Each entry produces two gizmos at setup time:
      - ``self.gizmo_swing_arc_<name>``: main arc on the active swing side
      - ``self.gizmo_swing_arc_<name>_flip``: Y-mirror of the main, on the
        opposite side of the hinge line

    Both gizmos hide together when ``visibility_condition(props)`` is False.
    When visible, each arc's ``matrix_basis`` is:

        Translation(hinge_x(props), hinge_y(props), 0)
            @ Scale(panel_width(props), 4)
            @ (Scale(-1, X) if x_mirror(props) else Identity)
            @ (Scale(-1, Y) if this is the flip arc else Identity)

    The arc geometry (``GizmoArc.tris``) is a unit quarter-arc sweeping
    counterclockwise from +X to +Y with its hinge at the origin, so the
    transforms above translate the hinge into world position, scale to
    panel size, and mirror across the hinge line as needed.
    """

    name: str
    visibility_condition: Callable[[Any], bool]
    hinge_x: Callable[[Any], float]
    hinge_y: Callable[[Any], float]
    panel_width: Callable[[Any], float]
    x_mirror: Callable[[Any], bool]


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
        tool.Blender.update_all_viewports()

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
                mesh.vertices.foreach_get("co", coords)
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
            if not obj.bound_box:
                continue
            bbox = tool.Blender.get_object_world_bounding_box(obj)
            bbox_min = bbox["min_point"]
            bbox_max = bbox["max_point"]

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


def build_snap_cache(context: bpy.types.Context, active_obj: bpy.types.Object, include_active: bool = False) -> None:
    _snap_manager.build_snap_cache(context, active_obj, include_active)


def clear_snap_cache() -> None:
    _snap_manager.clear_snap_cache()


def get_billboard_rotation(context: bpy.types.Context) -> Matrix:
    """Get rotation matrix that makes an object face the camera."""
    rv3d = context.region_data
    if rv3d is None:
        return Matrix.Identity(4)
    return rv3d.view_matrix.to_3x3().transposed().to_4x4()


def billboarded_at(world_pos: Vector, billboard_rot: Matrix, scale: float = DEFAULT_BILLBOARD_SCALE) -> Matrix:
    """Compose the standard icon matrix_basis: translate to ``world_pos``, billboard to the camera,
    then uniformly scale."""
    return Matrix.Translation(world_pos) @ billboard_rot @ Matrix.Scale(scale, 4)


def billboarded_along_axis(
    world_pos: Vector,
    billboard_rot: Matrix,
    axis_world: Vector,
    scale: float = DEFAULT_BILLBOARD_SCALE,
) -> Matrix:
    """Composed matrix_basis like ``billboarded_at`` but with local +X
    rotated about the camera-forward axis to align with ``axis_world``
    projected onto the screen plane.

    The gizmo still faces the camera (local +Z stays along camera-forward),
    only its in-plane orientation changes. Falls back to plain
    ``billboarded_at`` when the axis is near-parallel to the view direction
    (no usable screen projection)."""
    camera_forward = billboard_rot @ Vector((0.0, 0.0, 1.0))
    projected = axis_world - camera_forward * axis_world.dot(camera_forward)
    if projected.length < 1e-4:
        return billboarded_at(world_pos, billboard_rot, scale)
    projected.normalize()
    y_axis = camera_forward.cross(projected).normalized()
    rot = Matrix.Identity(4)
    rot[0][:3] = (projected.x, y_axis.x, camera_forward.x)
    rot[1][:3] = (projected.y, y_axis.y, camera_forward.y)
    rot[2][:3] = (projected.z, y_axis.z, camera_forward.z)
    return Matrix.Translation(world_pos) @ rot @ Matrix.Scale(scale, 4)


def get_screen_up(billboard_rot: Matrix) -> Vector:
    """Camera's screen-up direction in world space — local +Y of the billboard
    rotation. Use to lift a gizmo above an anchor in a way that stays
    perpendicular to the view plane (world +Z collapses to zero on-screen in
    top-down view and lands lifted gizmos on top of their anchors)."""
    return billboard_rot @ Vector((0.0, 1.0, 0.0))


# Screen-up distance lifted off floor-plane gizmo anchors in plan view. Matches
# the inter-icon stack spacing used by wall-corner stacks so single icons and
# stack bases sit at consistent screen-up positions when multiple groups render
# around the same wall endpoint.
DEFAULT_TOP_DOWN_CLEARANCE = 0.4


def top_down_clearance(
    context: bpy.types.Context,
    billboard_rot: Matrix,
    distance: float = DEFAULT_TOP_DOWN_CLEARANCE,
) -> Vector:
    """Screen-up offset that keeps a floor-plane gizmo anchor visible in plan view.

    In a top-down view the world-Z axis projects to ~zero on screen, so any
    icon anchored on the floor (wall endpoints, corners, connection points,
    the projected 3D cursor) sits directly on the click target it represents.
    Adding this offset before ``billboarded_at`` shifts the icon along the
    camera's up axis without changing the operator's world-space target.

    Returns a zero vector outside the top-down cone so callers can apply it
    unconditionally."""
    if not tool.Blender.is_view_top_down(context):
        return Vector((0.0, 0.0, 0.0))
    return get_screen_up(billboard_rot) * distance


# Dead-band on the screen-X delta — prevents flicker when the gizmo sits on the
# element origin.
EXTEND_FLIP_EPSILON = 1e-4

# Post-multipliers that mirror a billboarded matrix about its local X / Y axis.
EXTEND_FLIP_MIRROR_X = Matrix.Diagonal(Vector((-1.0, 1.0, 1.0, 1.0)))
EXTEND_FLIP_MIRROR_Y = Matrix.Diagonal(Vector((1.0, -1.0, 1.0, 1.0)))


def should_flip_extend_arrow(
    gizmo_world: Vector,
    reference_world: Vector,
    billboard_rot: Matrix,
) -> bool:
    """True when ``reference_world`` projects to screen-right of ``gizmo_world`` —
    mirror the extend arrow's local X so it points away from the reference in screen space."""
    screen_delta = billboard_rot.transposed() @ (reference_world - gizmo_world)
    return screen_delta.x > EXTEND_FLIP_EPSILON


def setup_icon_gizmo(
    gizmo_group: bpy.types.GizmoGroup,
    gizmo_type: str,
    color: tuple[float, float, float],
    highlight_color: tuple[float, float, float],
    operator: str,
    alpha: float = 0.8,
) -> bpy.types.Gizmo:
    """Create an icon gizmo with the Bonsai defaults (no draw-scale, fixed
    alpha, click-to-operator)."""
    gizmo = gizmo_group.gizmos.new(gizmo_type)
    gizmo.use_draw_scale = False
    gizmo.color = color
    gizmo.color_highlight = highlight_color
    gizmo.alpha = alpha
    gizmo.target_set_operator(operator)
    return gizmo


def get_warning_color_from_prefs(prefs) -> tuple[float, float, float]:
    """Hover color for destructive gizmo icons (split, unjoin, delete)."""
    return prefs.decorator_color_error[:3]


# --- Tris geometry helpers ----------------------------------------------------
# Shared by the icon ``bpy.types.Gizmo`` subclasses defined later in this module.
# Each gizmo declares a flat ``tris`` tuple of (x, y, z) vertices grouped into
# triangles of 3; these helpers compose tris from primitives so the per-gizmo
# definitions stay small and visually readable.


def rect_tris(x0: float, y0: float, x1: float, y1: float) -> tuple[tuple[float, float, float], ...]:
    """Two triangles forming an axis-aligned rectangle from ``(x0, y0)`` to ``(x1, y1)``,
    in the Z=0 plane (the convention for icon gizmos)."""
    return (
        (x0, y0, 0.0),
        (x0, y1, 0.0),
        (x1, y1, 0.0),
        (x0, y0, 0.0),
        (x1, y1, 0.0),
        (x1, y0, 0.0),
    )


def swap_xy_tris(
    tris: tuple[tuple[float, float, float], ...],
) -> tuple[tuple[float, float, float], ...]:
    """Reflect a ``tris`` tuple across the Y=X diagonal — useful when a "vertical"
    sibling of a "horizontal" icon should otherwise be a literal copy."""
    return tuple((y, x, z) for x, y, z in tris)


# Module-level GPU caches for StaticTrisGizmoMixin. Batches are keyed by
# concrete subclass (each has its own ``tris``); the shader is a single
# UNIFORM_COLOR instance shared across all icon-class gizmos. Both must be
# cleared on addon unregister + ``load_post`` because GPUBatch / GPUShader
# references hold GPU resources that go stale across blend-file reloads.
_static_tris_batches: dict[type, "gpu.types.GPUBatch"] = {}
_static_tris_shader = None


def _get_static_tris_shader():
    global _static_tris_shader
    if _static_tris_shader is None:
        _static_tris_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    return _static_tris_shader


def _get_static_tris_batch(cls):
    batch = _static_tris_batches.get(cls)
    if batch is None:
        batch = batch_for_shader(_get_static_tris_shader(), "TRIS", {"pos": cls.tris})
        _static_tris_batches[cls] = batch
    return batch


def clear_static_tris_cache() -> None:
    """Drops the cached per-class TRIS batches and shader. Wired into addon
    teardown + ``load_post`` so GPU resources don't outlive their context."""
    global _static_tris_shader
    _static_tris_batches.clear()
    _static_tris_shader = None


# Single source of truth for icon-class outline defaults. Referenced from
# both ``StaticTrisGizmoMixin`` (class-attribute defaults a concrete gizmo
# can override per-class) and ``draw_tris_with_outline`` (helper called
# from dynamic-tris gizmos that don't inherit the mixin). ``_OUTLINE_DIRECTIONS_8``
# lives near ``DimensionRenderer`` because both consumers reference it.
_OUTLINE_DEFAULT_WIDTH = 0.03
_OUTLINE_DEFAULT_ALPHA = 0.4


def _draw_outline_and_body(
    shader: "gpu.types.GPUShader",
    batch: "gpu.types.GPUBatch",
    base_matrix: Matrix,
    color: tuple[float, float, float, float],
    outline_width: float,
    outline_alpha: float,
) -> None:
    """Renders 8 outline passes (semi-transparent black, offset by
    ``outline_width`` in the cardinal + diagonal unit directions) followed
    by the body pass at ``color``, wrapped in ALPHA blend state.

    Caller must bind the shader and configure any sampler / texture
    uniforms before calling. The ``color`` uniform is set internally for
    each pass — caller's ``color`` uniform is overwritten."""
    with GPUStateScope(blend="ALPHA"):
        if outline_alpha > 0.0 and outline_width > 0.0:
            shader.uniform_float("color", (0.0, 0.0, 0.0, outline_alpha))
            for dx, dy in _OUTLINE_DIRECTIONS_8:
                offset_matrix = base_matrix @ Matrix.Translation((dx * outline_width, dy * outline_width, 0.0))
                with gpu.matrix.push_pop():
                    gpu.matrix.multiply_matrix(offset_matrix)
                    batch.draw(shader)
        shader.uniform_float("color", color)
        with gpu.matrix.push_pop():
            gpu.matrix.multiply_matrix(base_matrix)
            batch.draw(shader)


def draw_tris_with_outline(
    batch: "gpu.types.GPUBatch",
    base_matrix: Matrix,
    color: tuple[float, float, float, float],
    outline_width: float = _OUTLINE_DEFAULT_WIDTH,
    outline_alpha: float = _OUTLINE_DEFAULT_ALPHA,
) -> None:
    """Renders ``batch`` as an opaque tris body with an 8-way dark halo behind.

    Shared between StaticTrisGizmoMixin and custom-draw gizmos with dynamic
    tris. The caller supplies the per-frame matrix and the icon color; this
    routine handles shader binding, the eight outline passes, the body
    pass, and the surrounding GPU blend state."""
    shader = _get_static_tris_shader()
    shader.bind()
    _draw_outline_and_body(shader, batch, base_matrix, color, outline_width, outline_alpha)


class StaticTrisGizmoMixin:
    """Mixin for gizmos drawing a static class-level ``tris`` tuple.

    Renders the icon nine times: eight outline passes (the silhouette in
    semi-transparent black, offset by ``outline_width`` in eight unit-length
    directions), then the icon itself at its normal color. The union of the
    eight offset silhouettes approximates a circular dilation of the icon,
    producing a uniform dark halo on every side — keeps glyphs legible on
    any background (white walls, white mesh, dark theme, dark mesh).
    Disable per-class with ``outline_alpha = 0.0`` or ``outline_width = 0``."""

    # Outline ring width in local tris coordinates. The existing tris span
    # roughly ±0.3 to ±0.45 in local XY; 0.03 produces a ~6–10% halo on
    # every side, readable on any background without crowding the glyph.
    outline_width: float = _OUTLINE_DEFAULT_WIDTH
    # Per-pass alpha. Eight overlapping passes accumulate where they meet,
    # so 0.4 per pass produces a near-opaque inner ring (~0.98 cumulative)
    # and a clearly visible outer fade (single-pass 0.4 at the dilation edge).
    outline_alpha: float = _OUTLINE_DEFAULT_ALPHA
    # When True, hit shape is the glyph's 2D bounding box (plus ``outline_width``
    # padding) — clickable surface matches the visible tile, no dead zones.
    # Subclasses used in tight stacks (where adjacent icons sit closer than the
    # bbox extent) should set this False so each icon's hit area stays inside
    # its glyph and adjacent icons don't steal each other's clicks.
    hit_uses_bbox: bool = True

    def setup(self) -> None:
        if self.hit_uses_bbox:
            xs = [v[0] for v in self.tris]
            ys = [v[1] for v in self.tris]
            pad = self.outline_width
            hit_tris = rect_tris(min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)
        else:
            hit_tris = self.tris
        self.custom_shape = self.new_custom_shape("TRIS", hit_tris)

    def draw(self, context: bpy.types.Context) -> None:
        # Icon body is forced fully opaque: any ``self.alpha`` < 1.0 would
        # let the dark outline behind bleed through and grey out the glyph.
        # Hover-vs-default is conveyed by RGB only.
        if self.is_highlight:
            color = (*self.color_highlight, 1.0)
        else:
            color = (*self.color, 1.0)
        draw_tris_with_outline(
            _get_static_tris_batch(type(self)),
            self.matrix_basis @ self.matrix_offset,
            color,
            self.outline_width,
            self.outline_alpha,
        )

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


# Unit quad in the Z=0 plane — same local space as icon-class ``tris`` tuples,
# so ``matrix_basis`` / ``scale_basis`` position it identically.
_TEXTURED_QUAD_POSITIONS = (
    (-0.5, -0.5, 0.0),
    (0.5, -0.5, 0.0),
    (0.5, 0.5, 0.0),
    (-0.5, 0.5, 0.0),
)
_TEXTURED_QUAD_TEX_COORDS = (
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
)


class TexturedQuadGizmoMixin(StaticTrisGizmoMixin):
    """Renders a billboarded textured quad from ``bim/data/icons/<icon_name>.png``.

    Inherits ``StaticTrisGizmoMixin`` on purpose: ``draw_select`` and the
    tris fallback stay available. Any texture failure (missing PNG, GPU
    init error, mid-reload race) falls through to ``super().draw`` so the
    gizmo never disappears. ``outline_scale`` / ``outline_alpha`` are
    inherited from the parent and apply identically — IMAGE_COLOR multiplies
    the sampled texel by the uniform color, so a black-tinted scaled-up pass
    produces a dark halo around the PNG silhouette."""

    icon_name: str = ""

    def setup(self) -> None:
        super().setup()
        from bonsai.bim.module.drawing import (
            gizmo_textures,  # ty: ignore[unresolved-import]
        )

        self._quad_batch = batch_for_shader(
            gizmo_textures.get_shader(),
            "TRI_FAN",
            {"pos": _TEXTURED_QUAD_POSITIONS, "texCoord": _TEXTURED_QUAD_TEX_COORDS},
        )

    def draw(self, context: bpy.types.Context) -> None:
        from bonsai.bim.module.drawing import (
            gizmo_textures,  # ty: ignore[unresolved-import]
        )

        texture = gizmo_textures.get_icon_texture(self.icon_name)
        if texture is None:
            super().draw(context)
            return
        shader = gizmo_textures.get_shader()
        # Icon body forced fully opaque so the dark outline behind doesn't
        # bleed through the texture and grey out the glyph.
        if self.is_highlight:
            color = (*self.color_highlight, 1.0)
        else:
            color = (*self.color, 1.0)
        shader.bind()
        shader.uniform_sampler("image", texture)
        _draw_outline_and_body(
            shader,
            self._quad_batch,
            self.matrix_basis @ self.matrix_offset,
            color,
            self.outline_width,
            self.outline_alpha,
        )


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
            delta *= PRECISION_MODE_MULTIPLIER
        value = max(0, self.init_value + delta)
        value *= self.scale_value
        ctx.area.header_text_set(f"Depth: {value}")
        self.target_set_value("offset", value)
        return {"RUNNING_MODAL"}

    def project_mouse(self, ctx, event):
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
        target = context.active_object
        if not target:
            return
        basis = target.matrix_world.normalized()
        self.handle.matrix_basis = basis
        self.guides.matrix_basis = basis

    def update(self, context: bpy.types.Context) -> None:
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

    def _get_triangles(self) -> tuple[tuple[float, float, float], ...]:
        """Subclasses must return TRIS-mode geometry for the custom shape."""
        raise NotImplementedError(f"{type(self).__name__} must define _get_triangles()")

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self._get_triangles())

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

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
            not cancel and hasattr(self, "_has_dragged") and not self._has_dragged and self.move_set_cb is not None
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
            if (dx * dx + dy * dy) > (self.DRAG_THRESHOLD**2):
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

    def _handle_keyboard_input(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str] | None:
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


LOCK_TRIS_OPEN = (
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

LOCK_TRIS_CLOSED = (
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


class GizmoLockOpen(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Static open-padlock glyph."""

    bl_idname = "VIEW3D_GT_lock_open"
    __slots__ = ("custom_shape",)
    tris = LOCK_TRIS_OPEN


class GizmoLockClosed(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Static closed-padlock glyph."""

    bl_idname = "VIEW3D_GT_lock_closed"
    __slots__ = ("custom_shape",)
    tris = LOCK_TRIS_CLOSED


ARC_TRIS_DEFAULT = create_circle_arc(
    radius=1.0, direction="LEFT", angle_min=DOOR_SWING_ANGLE_MIN, angle_max=DOOR_SWING_ANGLE_MAX
)


class GizmoArc(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Static quarter-arc glyph for swing visualisation.

    Consumers needing the mirrored (RIGHT) visual apply a flip-X matrix to
    ``matrix_basis``. ``outline_alpha = 0.0`` suppresses the inherited 8-pass
    dark halo: an open curve has no enclosed silhouette for the dilation to
    ring, so the offset passes read as ghost arcs rather than a uniform
    outline. The arc's own cross-section thickness keeps it legible without
    the halo."""

    bl_idname = "VIEW3D_GT_arc"
    __slots__ = ("custom_shape",)
    tris = ARC_TRIS_DEFAULT
    outline_alpha = 0.0


def _link_toggle_icon_tris(broken: bool) -> tuple[tuple[float, float, float], ...]:
    """Two filled dots joined by a horizontal connector. ``broken=False``
    draws a single continuous bar between the dots' inner edges;
    ``broken=True`` shears the two halves vertically — the left dot AND
    its stub slip down as a unit, the right dot AND its stub slip up,
    with a horizontal gap at the centre.

    Each half moves as a cohesive piece so the stub stays attached to its
    dot at the same y, reading as a snapped link whose two halves slid
    apart rather than as bent stubs jutting out of stationary dots."""
    dot_cx = 0.30
    dot_r = 0.10
    bar_half_thickness = 0.04
    # Inner edge of each dot — the intact bar joins the dot edges, not the
    # centres, so the dot + bar reads as one continuous shape.
    bar_inner_x = dot_cx - dot_r
    segments = 12
    # Vertical shear applied to each half when broken. Zero in the intact
    # form keeps both halves on the centerline.
    half_offset_y = 0.08 if broken else 0.0

    tris: list[tuple[float, float, float]] = []
    for sign in (-1, 1):
        cx = sign * dot_cx
        cy = sign * half_offset_y
        for i in range(segments):
            a1 = (2.0 * math.pi) * (i / segments)
            a2 = (2.0 * math.pi) * ((i + 1) / segments)
            p1 = (cx + dot_r * math.cos(a1), cy + dot_r * math.sin(a1))
            p2 = (cx + dot_r * math.cos(a2), cy + dot_r * math.sin(a2))
            tris.append((cx, cy, 0.0))
            tris.append((p1[0], p1[1], 0.0))
            tris.append((p2[0], p2[1], 0.0))

    if broken:
        # Stubs reach inward into the dot's interior so they read as rooted
        # in the dot rather than floating off its edge after the slip.
        stub_outer_x = 0.27
        stub_inner_x = 0.06
        tris.extend(
            rect_tris(
                -stub_outer_x,
                -half_offset_y - bar_half_thickness,
                -stub_inner_x,
                -half_offset_y + bar_half_thickness,
            )
        )
        tris.extend(
            rect_tris(
                stub_inner_x,
                half_offset_y - bar_half_thickness,
                stub_outer_x,
                half_offset_y + bar_half_thickness,
            )
        )
    else:
        tris.extend(rect_tris(-bar_inner_x, -bar_half_thickness, bar_inner_x, bar_half_thickness))

    return tuple(tris)


LINK_TRIS_INTACT = _link_toggle_icon_tris(broken=False)
LINK_TRIS_BROKEN = _link_toggle_icon_tris(broken=True)


class GizmoLinkToggle(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Two-state link glyph: default reads as a connected link (two dots +
    intact connector); hover swaps to a broken link (same dots + severed
    connector) to signal that a click will sever the underlying connection.

    Single-click gizmo — the target operator is bound via
    ``target_set_operator`` by the owning group. The hover swap is purely
    visual; the click target is the same in both states. The glyph is
    feature-agnostic — any path / link / pair-of-connected-items context can
    reuse it for a sever-this-connection affordance."""

    bl_idname = "VIEW3D_GT_link_toggle"
    __slots__ = ("custom_shape",)
    # Bbox source for the hit shape. The broken form's vertically-sheared
    # halves give it the larger bbox of the two states, so using it as the
    # hit-shape source guarantees the clickable area covers either form —
    # the cursor doesn't lose hover at the offset dots' outer edges.
    tris = LINK_TRIS_BROKEN

    # Per-class batch cache: one entry per highlight state. The mixin parent
    # caches one batch per class via ``_get_static_tris_batch``; the per-state
    # swap needs a second batch, so this class keeps its own cache.
    _batch_cache: ClassVar[dict[bool, "gpu.types.GPUBatch"]] = {}

    def draw(self, context: bpy.types.Context) -> None:
        broken = bool(self.is_highlight)
        batch = type(self)._batch_cache.get(broken)
        if batch is None:
            tris = LINK_TRIS_BROKEN if broken else LINK_TRIS_INTACT
            batch = batch_for_shader(_get_static_tris_shader(), "TRIS", {"pos": tris})
            type(self)._batch_cache[broken] = batch
        # Icon body forced fully opaque so the dark outline behind doesn't
        # bleed through and grey out the glyph.
        color = (*self.color_highlight, 1.0) if broken else (*self.color, 1.0)
        draw_tris_with_outline(
            batch,
            self.matrix_basis @ self.matrix_offset,
            color,
            self.outline_width,
            self.outline_alpha,
        )


def _fillet_icon_tris() -> tuple[tuple[float, float, float], ...]:
    """Filled L-glyph with a smoothly rounded corner — two perpendicular
    wall bars joined by a constant-thickness arc band."""
    arc_center_x = 0.0
    arc_center_y = 0.0
    r_outer = 0.28
    r_inner = 0.18  # thickness = 0.10
    arc_segments = 8

    # Banana sweeps from 270° (downward radial) to 360° = 0° (rightward
    # radial). The bars extend the wall material outward from the banana's
    # two end caps along the tangent direction.
    outer_at_start = (arc_center_x, arc_center_y - r_outer)  # 270°, outer
    inner_at_start = (arc_center_x, arc_center_y - r_inner)  # 270°, inner
    outer_at_end = (arc_center_x + r_outer, arc_center_y)  # 0°, outer
    inner_at_end = (arc_center_x + r_inner, arc_center_y)  # 0°, inner

    bar_a_left = -0.45  # horizontal bar extends from banana cap LEFTWARD
    bar_b_top = 0.45  # vertical bar extends from banana cap UPWARD

    tris: list[tuple[float, float, float]] = []
    # Horizontal bar: tangent at 270° (downward radial), tangent direction is +X.
    # The bar lies along +X with cross-section in radial direction (y).
    tris.extend(rect_tris(bar_a_left, outer_at_start[1], outer_at_start[0], inner_at_start[1]))
    # Vertical bar: tangent at 0° (rightward radial), tangent direction is +Y.
    # The bar lies along +Y with cross-section in radial direction (x).
    tris.extend(rect_tris(inner_at_end[0], outer_at_end[1], outer_at_end[0], bar_b_top))

    # Quarter-banana sector: each angular slice → trapezoid → two CCW triangles.
    angle_start = 3.0 * math.pi / 2.0  # 270°
    angle_end = 2.0 * math.pi  # 360° / 0°
    for i in range(arc_segments):
        a1 = angle_start + (angle_end - angle_start) * (i / arc_segments)
        a2 = angle_start + (angle_end - angle_start) * ((i + 1) / arc_segments)
        outer1 = (arc_center_x + r_outer * math.cos(a1), arc_center_y + r_outer * math.sin(a1))
        outer2 = (arc_center_x + r_outer * math.cos(a2), arc_center_y + r_outer * math.sin(a2))
        inner1 = (arc_center_x + r_inner * math.cos(a1), arc_center_y + r_inner * math.sin(a1))
        inner2 = (arc_center_x + r_inner * math.cos(a2), arc_center_y + r_inner * math.sin(a2))
        tris.append((outer1[0], outer1[1], 0.0))
        tris.append((outer2[0], outer2[1], 0.0))
        tris.append((inner2[0], inner2[1], 0.0))
        tris.append((outer1[0], outer1[1], 0.0))
        tris.append((inner2[0], inner2[1], 0.0))
        tris.append((inner1[0], inner1[1], 0.0))
    return tuple(tris)


FILLET_TRIS_DEFAULT = _fillet_icon_tris()


class GizmoFillet(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Filled fillet glyph for wall-corner rounding."""

    bl_idname = "VIEW3D_GT_fillet"
    __slots__ = ("custom_shape",)
    tris = FILLET_TRIS_DEFAULT
    # Stacked at ICON_STACK_OFFSET_Y above the join icon in the wall-join
    # gizmo group; full-bbox hit overlaps the sibling icons' bboxes and
    # steals their clicks.
    hit_uses_bbox = False


def _wall_corner_icon_tris() -> tuple[tuple[float, float, float], ...]:
    """Filled L-glyph with a sharp 90° inner corner."""
    # Match the fillet icon's bar thickness so the row reads at one visual weight.
    outer_y = -0.28
    inner_y = -0.18
    outer_x = 0.28
    inner_x = 0.18
    bar_a_left = -0.45
    bar_b_top = 0.45

    tris: list[tuple[float, float, float]] = []
    # Bars overlap at the corner square so the L renders as one continuous material.
    tris.extend(rect_tris(bar_a_left, outer_y, outer_x, inner_y))
    tris.extend(rect_tris(inner_x, outer_y, outer_x, bar_b_top))
    return tuple(tris)


WALL_CORNER_TRIS_DEFAULT = _wall_corner_icon_tris()


class GizmoWallCornerIcon(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Filled L-shape glyph (sharp 90° corner) for joining two walls."""

    bl_idname = "VIEW3D_GT_wall_corner"
    __slots__ = ("custom_shape",)
    tris = WALL_CORNER_TRIS_DEFAULT
    hit_uses_bbox = False  # tight stack in GizmoWallJoinIntersection — see GizmoFillet


def _wall_tee_icon_tris() -> tuple[tuple[float, float, float], ...]:
    """Filled side-T glyph (⊣ orientation) for extending one wall into
    another's side. The through wall (vertical bar, right edge) carries a
    branching wall (horizontal bar) butting into its midline — visually
    distinguishes 'extend wall to wall' from the L-corner 'join' glyph by
    *where* the bars meet (middle vs corner)."""
    # Match the wall-corner bbox + bar thickness so the icon row reads at
    # one visual weight.
    bar_lo_y = -0.28
    bar_top = 0.45
    through_inner_x = 0.18
    through_outer_x = 0.28
    branch_left = -0.45
    # Branching bar centered on the through-bar's midline so the vertical
    # extends equally above and below — reads as a balanced ⊣.
    branch_mid_y = (bar_lo_y + bar_top) / 2
    branch_half_thickness = 0.05

    tris: list[tuple[float, float, float]] = []
    tris.extend(rect_tris(through_inner_x, bar_lo_y, through_outer_x, bar_top))
    # Branching bar's right edge stops at the through-bar's inner edge so the
    # bars touch without overlapping.
    tris.extend(
        rect_tris(
            branch_left,
            branch_mid_y - branch_half_thickness,
            through_inner_x,
            branch_mid_y + branch_half_thickness,
        )
    )
    return tuple(tris)


WALL_TEE_TRIS_DEFAULT = _wall_tee_icon_tris()


class GizmoWallTeeIcon(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Filled T-junction glyph for extending one wall into another's side."""

    bl_idname = "VIEW3D_GT_wall_tee"
    __slots__ = ("custom_shape",)
    tris = WALL_TEE_TRIS_DEFAULT
    hit_uses_bbox = False  # tight stack in GizmoWallJoinIntersection — see GizmoFillet


class GizmoPen(StaticTrisGizmoMixin, bpy.types.Gizmo):
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


class GizmoValidate(StaticTrisGizmoMixin, bpy.types.Gizmo):
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


class GizmoCancel(StaticTrisGizmoMixin, bpy.types.Gizmo):
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


class GizmoPlus(StaticTrisGizmoMixin, bpy.types.Gizmo):
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


class GizmoMinus(StaticTrisGizmoMixin, bpy.types.Gizmo):
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


class GizmoTrash(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Wastebasket icon for destructive delete actions — body + lid + handle."""

    bl_idname = "VIEW3D_GT_trash"

    __slots__ = ("custom_shape",)

    # Trash-can profile within the conventional ±0.375 icon bounding box.
    # Sized ~15% larger than the baseline 3-rect icon design so the
    # destructive button reads as the visual end-stop of the row. Solid
    # fills match the Bonsai gizmo-icon convention (Plus / Minus / Cancel).
    tris = (
        # Body — slightly narrower than the lid for the classic bin shape.
        *rect_tris(-0.23, -0.345, 0.23, 0.207),
        # Lid — extends wider on both sides so it sits "over" the body.
        *rect_tris(-0.31, 0.207, 0.31, 0.30),
        # Handle — small bar centered on top of the lid.
        *rect_tris(-0.09, 0.30, 0.09, 0.39),
    )


class GizmoArrayParent(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Hierarchy tree glyph — one top node connected to three bottom nodes
    by short lines. Fires the operator that selects the parent object of an
    array given a child is currently active."""

    bl_idname = "VIEW3D_GT_array_parent"

    __slots__ = ("custom_shape",)

    # Hierarchy tree: one top node + three bottom nodes wired by trunk +
    # crossbar + drop legs. Conventional ±0.375 icon bounding box.
    tris = (
        # Top (parent) node.
        *rect_tris(-0.075, 0.195, 0.075, 0.345),
        # Three child nodes along the bottom row.
        *rect_tris(-0.335, -0.335, -0.205, -0.205),
        *rect_tris(-0.065, -0.335, 0.065, -0.205),
        *rect_tris(0.205, -0.335, 0.335, -0.205),
        # Vertical trunk: top node down through the crossbar to the centre child.
        *rect_tris(-0.02, -0.205, 0.02, 0.195),
        # Horizontal crossbar joining the trunk's midpoint to left/right legs.
        *rect_tris(-0.27, -0.07, 0.27, -0.03),
        # Drop legs from crossbar to the left and right children.
        *rect_tris(-0.29, -0.205, -0.25, -0.07),
        *rect_tris(0.25, -0.205, 0.29, -0.07),
    )


def _quad_tris(x0: float, y0: float, x1: float, y1: float) -> tuple:
    """Two CCW triangles covering rectangle ``(x0,y0)-(x1,y1)`` in Z=0."""
    return (
        (x0, y0, 0.0), (x1, y0, 0.0), (x1, y1, 0.0),
        (x0, y0, 0.0), (x1, y1, 0.0), (x0, y1, 0.0),
    )  # fmt: skip


# 7-segment digit definitions for world-space integer-label gizmos. Each digit's
# strokes fit inside a unit-cell (width 0.22, height 0.40) centred on (0, 0); the
# label builder translates the cell into the final position. Composed of seven
# rectangle "segments" — top, mid, bot horizontals + upper-left/right and
# lower-left/right verticals — so the count gizmo can render any integer 0-9999
# without an external font.
_DIGIT_STROKES = {
    "top": (-0.10, 0.18, 0.10, 0.20),
    "mid": (-0.10, -0.02, 0.10, 0.02),
    "bot": (-0.10, -0.20, 0.10, -0.18),
    "ul":  (-0.10, 0.00, -0.07, 0.20),
    "ur":  (0.07, 0.00, 0.10, 0.20),
    "ll":  (-0.10, -0.20, -0.07, 0.00),
    "lr":  (0.07, -0.20, 0.10, 0.00),
}  # fmt: skip
_DIGIT_SEGMENTS = {
    "0": ("top", "ul", "ur", "ll", "lr", "bot"),
    "1": ("ur", "lr"),
    "2": ("top", "ur", "mid", "ll", "bot"),
    "3": ("top", "ur", "mid", "lr", "bot"),
    "4": ("ul", "ur", "mid", "lr"),
    "5": ("top", "ul", "mid", "lr", "bot"),
    "6": ("top", "ul", "mid", "ll", "lr", "bot"),
    "7": ("top", "ur", "lr"),
    "8": ("top", "ul", "ur", "mid", "ll", "lr", "bot"),
    "9": ("top", "ul", "ur", "mid", "lr", "bot"),
}
# Width of one digit cell including its trailing kerning gap. ``x`` prefix is
# rendered as two crossed diagonals across one cell of the same width.
_DIGIT_CELL_W = 0.26


def _digit_tris(digit: str, cx: float, cy: float) -> tuple:
    """Triangles for one ``"0"``..``"9"`` digit centred on ``(cx, cy)``."""
    tris: list[tuple[float, float, float]] = []
    for seg in _DIGIT_SEGMENTS[digit]:
        x0, y0, x1, y1 = _DIGIT_STROKES[seg]
        tris.extend(_quad_tris(x0 + cx, y0 + cy, x1 + cx, y1 + cy))
    return tuple(tris)


def _x_prefix_tris(cx: float, cy: float) -> tuple:
    """Triangles for an ``x`` glyph centred on ``(cx, cy)`` — two crossed
    diagonals roughly matching a digit's height for the count label."""
    # Each leg is a thin rectangle rotated 45° from the cell centre. Vertex
    # coords are precomputed: half-length 0.13 along the rotated axis, half
    # width 0.025 perpendicular. Using two quads keeps it TRIS-only.
    leg = 0.13
    w = 0.025
    # Leg 1 (top-left → bottom-right).
    p1 = (cx - leg - w, cy + leg - w, 0.0)
    p2 = (cx - leg + w, cy + leg + w, 0.0)
    p3 = (cx + leg + w, cy - leg + w, 0.0)
    p4 = (cx + leg - w, cy - leg - w, 0.0)
    # Leg 2 (top-right → bottom-left).
    q1 = (cx + leg - w, cy + leg + w, 0.0)
    q2 = (cx + leg + w, cy + leg - w, 0.0)
    q3 = (cx - leg + w, cy - leg - w, 0.0)
    q4 = (cx - leg - w, cy - leg + w, 0.0)
    return (
        p1, p2, p3, p1, p3, p4,
        q1, q2, q3, q1, q3, q4,
    )  # fmt: skip


def _count_label_tris(count: int, cx: float, cy: float) -> tuple:
    """Triangles for an ``xN`` label centred on ``(cx, cy)``. Composes the
    ``x`` prefix and each base-10 digit horizontally."""
    digits = str(max(0, int(count)))
    total_w = _DIGIT_CELL_W * (1 + len(digits))
    start_x = cx - total_w / 2 + _DIGIT_CELL_W / 2
    tris: list[tuple[float, float, float]] = []
    tris.extend(_x_prefix_tris(start_x, cy))
    for i, d in enumerate(digits):
        tris.extend(_digit_tris(d, start_x + (i + 1) * _DIGIT_CELL_W, cy))
    return tuple(tris)


class GizmoArrayAll(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """2×2 grid of small filled squares — multi-select for an array
    (parent + all children).

    On hover from an array child, paints a wireframe bbox around every
    sibling in the same array layer."""

    bl_idname = "VIEW3D_GT_array_all"

    __slots__ = ("custom_shape",)

    # Four small filled squares in a 2x2 grid, each 0.2 wide with a 0.15 gap
    # between rows / columns so the grid reads as discrete cells rather than a
    # solid block. All within the ±0.375 icon bounding-box convention.
    tris = (
        *_quad_tris(-0.275, 0.075, -0.075, 0.275),  # top-left
        *_quad_tris(0.075, 0.075, 0.275, 0.275),  # top-right
        *_quad_tris(-0.275, -0.275, -0.075, -0.075),  # bottom-left
        *_quad_tris(0.075, -0.275, 0.275, -0.075),  # bottom-right
    )

    def draw(self, context: bpy.types.Context) -> None:
        super().draw(context)
        if self.is_highlight:
            self._draw_containing_array_bbox(context)

    def _draw_containing_array_bbox(self, context: bpy.types.Context) -> None:
        """Outline every sibling of the active child in the array layer that
        produced it. No-op when no resolvable parent / layer."""
        obj = context.active_object
        if obj is None:
            return
        child_element = tool.Ifc.get_entity(obj)
        if child_element is None:
            return
        layer_index = tool.Array.get_child_layer_index(child_element)
        if layer_index is None:
            return
        pset = ifcopenshell.util.element.get_pset(child_element, "BBIM_Array")
        if not pset:
            return
        parent_guid = pset.get("Parent")
        if not parent_guid:
            return
        try:
            parent_element = tool.Ifc.get().by_guid(parent_guid)
        except RuntimeError:
            return
        from bonsai.bim.module.model.array import draw_array_layer_children_bbox

        draw_array_layer_children_bbox(context, parent_element, layer_index)


class GizmoArrayLayerIndicator(bpy.types.Gizmo):
    """ARRAY layer entry icon with a world-space ``xN`` count rendered above.

    The 2×2-grid glyph sits in the bottom half of the local frame; the
    ``xN`` count is composed of 7-segment digit triangles in the top half.
    Both are part of the gizmo's custom shape so the entire glyph is a
    single click target.

    On hover, ``draw()`` paints a wireframe bbox around every child of this
    layer in the same 3D pass — drawing inline keeps the bbox in lockstep
    with the highlight."""

    bl_idname = "BIM_GT_array_layer_indicator"

    __slots__ = ("custom_shape", "_count", "_built_count", "_layer_index", "_outlined_batch")

    # Icon glyph (2×2 grid) translated down so the upper half stays free for
    # the count label. Centred so the gizmo's world anchor falls between the
    # icon and the label.
    _ICON_TRIS = (
        *_quad_tris(-0.275, -0.475, -0.075, -0.275),
        *_quad_tris(0.075, -0.475, 0.275, -0.275),
        *_quad_tris(-0.275, -0.225, -0.075, -0.025),
        *_quad_tris(0.075, -0.225, 0.275, -0.025),
    )
    # Vertical centre of the count label in the gizmo's local frame.
    _LABEL_Y = 0.22

    def setup(self) -> None:
        self._count = 0
        self._built_count = -1
        # ``-1`` until the gizmo group calls ``set_layer_index``. The bbox
        # highlight no-ops while the index is unassigned.
        self._layer_index = -1
        tris = self._build_tris()
        self.custom_shape = self.new_custom_shape("TRIS", tris)
        self._outlined_batch = batch_for_shader(_get_static_tris_shader(), "TRIS", {"pos": tris})
        self._built_count = 0

    def set_count(self, count: int) -> None:
        self._count = int(count)

    def set_layer_index(self, layer_index: int) -> None:
        self._layer_index = int(layer_index)

    def _build_tris(self) -> tuple:
        return self._ICON_TRIS + _count_label_tris(self._count, 0.0, self._LABEL_Y)

    def _ensure_shape(self) -> None:
        if self._built_count != self._count:
            tris = self._build_tris()
            self.custom_shape = self.new_custom_shape("TRIS", tris)
            self._outlined_batch = batch_for_shader(_get_static_tris_shader(), "TRIS", {"pos": tris})
            self._built_count = self._count

    def draw(self, context: bpy.types.Context) -> None:
        self._ensure_shape()
        if self.is_highlight:
            color = (*self.color_highlight, 1.0)
        else:
            color = (*self.color, 1.0)
        draw_tris_with_outline(self._outlined_batch, self.matrix_basis @ self.matrix_offset, color)
        if self.is_highlight:
            self._draw_layer_children_bbox(context)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self._ensure_shape()
        self.draw_custom_shape(self.custom_shape, select_id=select_id)

    def _draw_layer_children_bbox(self, context: bpy.types.Context) -> None:
        """Outline this layer's children inline so the bbox stays in lockstep
        with the gizmo highlight."""
        if self._layer_index < 0:
            return
        obj = context.active_object
        if obj is None:
            return
        parent_element = tool.Ifc.get_entity(obj)
        if parent_element is None:
            return
        from bonsai.bim.module.model.array import draw_array_layer_children_bbox

        draw_array_layer_children_bbox(context, parent_element, self._layer_index)


class GizmoCountLabel(bpy.types.Gizmo):
    """``xN`` text label rendered from 7-segment digit triangles.

    Mirrors a caller-supplied integer into a live count badge. No icon
    glyph; the gizmo is the number alone."""

    bl_idname = "BIM_GT_count_label"

    __slots__ = ("custom_shape", "_count", "_built_count", "_outlined_batch")

    def setup(self) -> None:
        self._count = 0
        self._built_count = -1
        tris = _count_label_tris(self._count, 0.0, 0.0)
        self.custom_shape = self.new_custom_shape("TRIS", tris)
        self._outlined_batch = batch_for_shader(_get_static_tris_shader(), "TRIS", {"pos": tris})
        self._built_count = 0

    def set_count(self, count: int) -> None:
        self._count = int(count)

    def _ensure_shape(self) -> None:
        if self._built_count != self._count:
            tris = _count_label_tris(self._count, 0.0, 0.0)
            self.custom_shape = self.new_custom_shape("TRIS", tris)
            self._outlined_batch = batch_for_shader(_get_static_tris_shader(), "TRIS", {"pos": tris})
            self._built_count = self._count

    def draw(self, context: bpy.types.Context) -> None:
        self._ensure_shape()
        color = (*self.color_highlight, 1.0) if self.is_highlight else (*self.color, 1.0)
        draw_tris_with_outline(self._outlined_batch, self.matrix_basis @ self.matrix_offset, color)

    def draw_select(self, context: bpy.types.Context, select_id: int) -> None:
        self._ensure_shape()
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


class GizmoMerge(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Two arrows pointing inward toward each other — conveys joining/merging elements."""

    bl_idname = "VIEW3D_GT_merge"

    __slots__ = ("custom_shape",)

    # Two solid triangles pointing toward the center on the horizontal axis,
    # plus two thin tails behind each tip to make them read as arrows rather than
    # standalone triangles.
    tris = (
        # Left arrowhead pointing right (tip at x≈-0.05).
        (-0.35, -0.20, 0.0),
        (-0.35, 0.20, 0.0),
        (-0.05, 0.0, 0.0),
        # Left tail behind the arrowhead.
        *rect_tris(-0.45, -0.06, -0.30, 0.06),
        # Right arrowhead pointing left (tip at x≈0.05).
        (0.35, -0.20, 0.0),
        (0.35, 0.20, 0.0),
        (0.05, 0.0, 0.0),
        # Right tail behind the arrowhead.
        *rect_tris(0.30, -0.06, 0.45, 0.06),
    )


class GizmoSplit(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Two arrows pointing outward away from each other — conveys splitting/cutting
    one element into two. Visual inverse of `GizmoMerge`."""

    bl_idname = "VIEW3D_GT_split"

    __slots__ = ("custom_shape",)

    # Two solid triangles pointing OUTWARD on the horizontal axis (tips at x=±0.35),
    # with tails extending toward the centerline. The tails meet at center to form a
    # short horizontal bar, suggesting the split point itself.
    tris = (
        # Left arrowhead pointing left (tip at x=-0.35).
        (-0.05, -0.20, 0.0),
        (-0.05, 0.20, 0.0),
        (-0.35, 0.0, 0.0),
        # Left tail extending toward the right (away from the tip, toward center).
        *rect_tris(-0.05, -0.06, 0.10, 0.06),
        # Right arrowhead pointing right (tip at x=0.35).
        (0.05, -0.20, 0.0),
        (0.05, 0.20, 0.0),
        (0.35, 0.0, 0.0),
        # Right tail extending toward the left.
        *rect_tris(-0.10, -0.06, 0.05, 0.06),
    )


class GizmoUnjoin(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Two C-shaped hooks facing each other across a clear gap — conveys
    severing a relationship between two elements (e.g. an
    ``IfcRelConnectsPathElements`` between two walls). The "two linked
    things pulled apart" silhouette reads as relationship-cut rather than
    geometry-cut."""

    bl_idname = "VIEW3D_GT_unjoin"

    __slots__ = ("custom_shape",)

    # Each hook is three solid bars composing a C: top, bottom, and back
    # wall. The two C's face inward across a clear gap so the silhouette
    # reads as "two interlocking links pulled apart".
    tris = (
        # Left hook — C opening to the right.
        *rect_tris(-0.30, 0.11, -0.08, 0.17),
        *rect_tris(-0.30, -0.17, -0.08, -0.11),
        *rect_tris(-0.30, -0.17, -0.24, 0.17),
        # Right hook — mirror, C opening to the left.
        *rect_tris(0.08, 0.11, 0.30, 0.17),
        *rect_tris(0.08, -0.17, 0.30, -0.11),
        *rect_tris(0.24, -0.17, 0.30, 0.17),
    )


class GizmoExtend(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """An arrow pointing into a vertical bar — conveys extending an element to a target
    line (e.g. extending a wall to the 3D cursor)."""

    bl_idname = "VIEW3D_GT_extend"

    __slots__ = ("custom_shape",)

    # Layout: thick vertical bar at the right edge (the "target") with a horizontal
    # arrow pointing into it from the left.
    tris = (
        # Vertical target bar (x = 0.25 to 0.35, full height).
        *rect_tris(0.25, -0.30, 0.35, 0.30),
        # Arrowhead pointing right toward the bar (tip at x=0.20).
        (-0.05, -0.18, 0.0),
        (-0.05, 0.18, 0.0),
        (0.20, 0.0, 0.0),
        # Tail extending leftward from the arrowhead base.
        *rect_tris(-0.35, -0.06, -0.05, 0.06),
    )


class GizmoExtendVertical(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Vertical sibling of `GizmoExtend` — arrow pointing UP into a horizontal
    bar. Conveys extending an element's height to a target Z."""

    bl_idname = "VIEW3D_GT_extend_vertical"

    __slots__ = ("custom_shape",)

    # Mechanically derived from GizmoExtend by reflecting across Y=X.
    tris = swap_xy_tris(GizmoExtend.tris)


def _offset_baseline_tris(mark_x: float) -> tuple[tuple[float, float, float], ...]:
    """Shared geometry for the three offset-baseline icons: a horizontal "wall
    section" bar with a vertical mark at ``mark_x`` indicating where the reference
    axis sits within the wall thickness. Matches the visual convention used in the
    Bonsai N-panel's wall Align row."""
    return rect_tris(-0.25, -0.07, 0.25, 0.07) + rect_tris(mark_x - 0.04, -0.22, mark_x + 0.04, 0.22)


class GizmoOffsetExterior(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Wall offset baseline indicator — reference axis at the exterior face (left mark)."""

    bl_idname = "VIEW3D_GT_offset_exterior"
    __slots__ = ("custom_shape",)
    tris = _offset_baseline_tris(-0.24)


class GizmoOffsetCenter(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Wall offset baseline indicator — reference axis at the centreline (middle mark)."""

    bl_idname = "VIEW3D_GT_offset_center"
    __slots__ = ("custom_shape",)
    tris = _offset_baseline_tris(0.0)


class GizmoOffsetInterior(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Wall offset baseline indicator — reference axis at the interior face (right mark)."""

    bl_idname = "VIEW3D_GT_offset_interior"
    __slots__ = ("custom_shape",)
    tris = _offset_baseline_tris(0.24)


class GizmoAddOpening(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """A rectangular frame (square outline with a hole in the middle) — conveys adding an
    opening (window/door/void) to a wall."""

    bl_idname = "VIEW3D_GT_add_opening"

    __slots__ = ("custom_shape",)

    # Outer 0.40 × 0.40 square with a 0.25 × 0.25 inner hole, drawn as four bars
    # forming a frame, plus a small "+" in the inner hole to convey "add".
    tris = (
        *rect_tris(-0.20, 0.125, 0.20, 0.20),  # Top bar
        *rect_tris(-0.20, -0.20, 0.20, -0.125),  # Bottom bar
        *rect_tris(-0.20, -0.125, -0.125, 0.125),  # Left bar
        *rect_tris(0.125, -0.125, 0.20, 0.125),  # Right bar
        *rect_tris(-0.07, -0.015, 0.07, 0.015),  # "+" horizontal stroke
        *rect_tris(-0.015, -0.07, 0.015, 0.07),  # "+" vertical stroke
    )


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


class GizmoCycle(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Circular arrow icon gizmo for cycling through enum values."""

    bl_idname = "VIEW3D_GT_cycle"

    __slots__ = ("custom_shape",)

    tris = _generate_circular_arrow_tris()


def _generate_menu_tris() -> tuple[tuple[float, float, float], ...]:
    """Three stacked horizontal bars — universal "menu / pick from list" glyph."""
    # Sized ~30% larger than the validate / cancel icon family so the picker
    # affordance reads more strongly — picking a type is a higher-stakes click
    # than the surrounding edit-mode toggles.
    bar_half_thickness = 0.046
    bar_half_width = 0.26
    vertical_spacing = 0.182
    return (
        *rect_tris(
            -bar_half_width,
            +vertical_spacing - bar_half_thickness,
            +bar_half_width,
            +vertical_spacing + bar_half_thickness,
        ),
        *rect_tris(-bar_half_width, -bar_half_thickness, +bar_half_width, +bar_half_thickness),
        *rect_tris(
            -bar_half_width,
            -vertical_spacing - bar_half_thickness,
            +bar_half_width,
            -vertical_spacing + bar_half_thickness,
        ),
    )


class GizmoMenu(StaticTrisGizmoMixin, bpy.types.Gizmo):
    """Hamburger-stack menu icon — 'open a picker to choose from many options'.

    For enums with 3+ values; use ``GizmoCycle`` for exactly 2 (where the
    advance-one-per-click semantic stays predictable)."""

    bl_idname = "VIEW3D_GT_menu"

    __slots__ = ("custom_shape",)

    tris = _generate_menu_tris()


class GizmoArrow(GizmoMovable):
    """Arrow gizmo for directional value editing."""

    bl_idname = "BIM_GT_gizmo_arrow"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    def _get_triangles(self) -> tuple[tuple[float, float, float], ...]:
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

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)
        self.draw_property_tooltip(context)


class GizmoArrow2D(GizmoMovable):
    """Flat 2D arrow that rotates around its axis to face the camera."""

    bl_idname = "BIM_GT_gizmo_arrow_2d"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    ARROW_2D_SHAFT_LENGTH = 0.5
    ARROW_2D_HEAD_LENGTH = 0.5
    ARROW_2D_WIDTH = 0.25
    ARROW_2D_HEAD_WIDTH = 0.75

    def _get_triangles(self) -> tuple[tuple[float, float, float], ...]:
        """Generate flat arrow geometry in XY plane, pointing along +X."""
        shaft = self.ARROW_2D_SHAFT_LENGTH
        head = self.ARROW_2D_HEAD_LENGTH
        w = self.ARROW_2D_WIDTH / 2
        hw = self.ARROW_2D_HEAD_WIDTH / 2

        return (
            # Shaft
            (0, -w, 0),
            (shaft, -w, 0),
            (0, w, 0),
            (0, w, 0),
            (shaft, -w, 0),
            (shaft, w, 0),
            # Head
            (shaft, -hw, 0),
            (shaft + head, 0, 0),
            (shaft, hw, 0),
        )

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)
        self.draw_property_tooltip(context)

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

    def _get_triangles(self) -> tuple[tuple[float, float, float], ...]:
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

    def draw(self, context: bpy.types.Context) -> None:
        self.draw_custom_shape(self.custom_shape)


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
        "_display_value",  # Actual value for display (can be negative)
        "text_offset_sign",  # -1 to offset text below/left, +1 for above/right (default)
        "show_start_arrow",  # Whether to show arrow at start (origin) of dimension
        "show_end_arrow",  # Whether to show arrow at end of dimension
        "text_alignment",  # TextAlignment enum: CENTER (default) or START (left-aligned at offset from line)
        "_original_value",  # Original property value before interaction
        "_click_offset",  # Offset from dimension tip to click position (for snap correction)
        "show_extension_lines",  # Whether to show extension lines at dimension endpoints
        "text_formatter",  # Optional (props, value) -> str to override the default dimension label
        "schematic_attr_name",  # Set by BaseSchematicGizmoGroup: attr_name of the bound config, read by hover-highlight
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
            (0, -hw, -hw),
            (1, -hw, -hw),
            (0, hw, -hw),
            (0, hw, -hw),
            (1, -hw, -hw),
            (1, hw, -hw),
            (0, -hw, hw),
            (0, hw, hw),
            (1, -hw, hw),
            (1, -hw, hw),
            (0, hw, hw),
            (1, hw, hw),
            (0, -hw, -hw),
            (0, -hw, hw),
            (1, -hw, -hw),
            (1, -hw, -hw),
            (0, -hw, hw),
            (1, -hw, hw),
            (0, hw, -hw),
            (1, hw, -hw),
            (0, hw, hw),
            (0, hw, hw),
            (1, hw, -hw),
            (1, hw, hw),
        )

    def setup(self) -> None:
        self.custom_shape = self.new_custom_shape("TRIS", self._get_clickable_shape())
        self._dimension_length = 1.0
        self._display_value = 1.0
        self.text_offset_sign = 1
        self.show_start_arrow = False
        self.show_end_arrow = True
        self.text_alignment = TextAlignment.CENTER
        self.show_extension_lines = True

    def draw(self, context: bpy.types.Context) -> None:
        """Draw dimension graphics using the DimensionRenderer singleton."""
        if not hasattr(self, "_dimension_length") or self._dimension_length < 0:
            return

        axis_world = Vector(self.matrix_basis.col[0][:3]).normalized()
        start_world = self.matrix_basis.translation.copy()
        end_world = start_world + axis_world * self._dimension_length

        display_value = getattr(self, "_display_value", self._dimension_length)
        text_formatter = getattr(self, "text_formatter", None)
        gizmo_group = getattr(self, "gizmo_group", None)
        display_text: str | None = None
        if text_formatter is not None and gizmo_group is not None:
            obj = bpy.context.active_object
            props = gizmo_group.get_props(obj) if obj is not None else None
            if props is not None:
                display_text = text_formatter(props, display_value)

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
            text_alignment=getattr(self, "text_alignment", TextAlignment.CENTER),
            prop_name=getattr(self, "prop_name", None),
            display_value=display_value,
            display_text=display_text,
        )

    def _calculate_screen_endpoints(self, context: bpy.types.Context) -> tuple[Vector, Vector, Vector, float] | None:
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
        # Store the actual value for display (can be negative)
        self._display_value = max(-10000.0, min(length, 10000.0))
        # Clamp to valid range (0 to 10000 meters is reasonable for BIM) for drawing
        self._dimension_length = max(0.0, min(abs(length), 10000.0))
        # Smaller dimensions win selection when hit regions overlap: a long gizmo's
        # hit box fully contains a nested short one's, so without a bias the long
        # one wins and the short one is unreachable. The long one stays clickable
        # at its exposed ends regardless of bias.
        self.select_bias = -self._dimension_length

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

        # Schematic gizmos opt out of dimension snap. Force the header
        # indicator to ``off`` for the drag's duration so the user sees the
        # state matches behaviour; ``exit`` restores ``initial_snap_state``.
        # Skipping the snap cache here also avoids the per-drag mesh probe.
        snap_supported = getattr(self.gizmo_group, "snap_enabled_on_dimensions", True)
        if not snap_supported:
            context.scene.tool_settings.use_snap = False
        elif self.initial_snap_state and self.active_obj:
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

        # Group-level opt-out: schematic gizmos float in viewport space, so
        # global-snap-to-scene-vertices would produce spurious value jumps.
        # The fallback (``True``) covers any gizmo whose group is not a
        # ``BaseParametricGizmoGroup``.
        snap_supported = getattr(self.gizmo_group, "snap_enabled_on_dimensions", True)

        if snap_supported:
            tool_settings.use_snap = not self.initial_snap_state if event.ctrl else self.initial_snap_state

            if tool_settings.use_snap and not self._snap_cache_built and self.active_obj:
                build_snap_cache(context, self.active_obj)
                self._snap_cache_built = True

        current_coord = (event.mouse_region_x, event.mouse_region_y)

        if not self._has_dragged and hasattr(self, "_start_mouse_pos"):
            dx = current_coord[0] - self._start_mouse_pos[0]
            dy = current_coord[1] - self._start_mouse_pos[1]
            if (dx * dx + dy * dy) > (self.DRAG_THRESHOLD**2):
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

        if snap_supported and tool_settings.use_snap and self.active_obj:
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
            not cancel and hasattr(self, "_has_dragged") and not self._has_dragged and self.move_set_cb is not None
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


class BillboardingGizmoGroupMixin:
    """Mixin for standalone ``bpy.types.GizmoGroup`` classes whose icons must billboard
    (face the camera) and re-position every frame.

    Blender calls ``GizmoGroup.refresh()`` only on state-change events (selection,
    property change, dependency update) — not on camera rotation. A gizmo group that
    only sets ``matrix_basis`` in ``refresh()`` will appear to "freeze" its rotation
    at the camera angle in effect when it was last refreshed; orbiting the camera
    leaves the icon facing the wrong way.

    ``draw_prepare()`` *is* called every redraw, so the fix is to run the same
    positioning code from both events. Rather than overriding ``refresh()`` and
    ``draw_prepare()`` in every gizmo group that has this need, subclass this mixin
    and implement a single ``position_gizmos(context)`` method.

    Usage::

        class MyGizmoGroup(bpy.types.GizmoGroup, BillboardingGizmoGroupMixin):
            bl_idname = "..."
            ...
            def setup(self, context):
                ...
            def position_gizmos(self, context):
                # set matrix_basis on every gizmo here, using get_billboard_rotation
                # for any icon that should face the camera.
                ...

    ``position_gizmos`` should be idempotent — it's called twice when a state change
    coincides with a redraw (once via ``refresh``, once via ``draw_prepare``)."""

    def refresh(self, context: bpy.types.Context) -> None:
        self.position_gizmos(context)

    def draw_prepare(self, context: bpy.types.Context) -> None:
        if apply_transform_modal_draw_gate(self, context):
            return
        self.position_gizmos(context)

    def setup_icon_gizmo(
        self,
        gizmo_type: str,
        color: tuple[float, float, float],
        highlight_color: tuple[float, float, float],
        operator: str,
        alpha: float = 0.8,
    ) -> bpy.types.Gizmo:
        """Convenience wrapper over `setup_icon_gizmo` for subclasses."""
        return setup_icon_gizmo(self, gizmo_type, color, highlight_color, operator, alpha)

    def get_decoration_colors(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        """Standard (default, highlight) color pair for active-state gizmos.
        Pulls from the addon preferences — same source consumed by every
        Bonsai decorator. Hover-class gizmos that should not pull focus
        should use ``get_unselected_decoration_colors`` instead."""
        prefs = tool.Blender.get_addon_preferences()
        return prefs.decorations_colour[:3], prefs.decorator_color_selected[:3]

    def get_unselected_decoration_colors(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        """Lower-priority (unselected default, highlight) pair for gizmos
        that surface on already-selected geometry and shouldn't compete
        visually with the selection outline (e.g. array-child navigation)."""
        prefs = tool.Blender.get_addon_preferences()
        return prefs.decorator_color_unselected[:3], prefs.decorator_color_selected[:3]

    def position_gizmos(self, context: bpy.types.Context) -> None:
        raise NotImplementedError(
            f"{type(self).__name__} must implement position_gizmos(context) when using BillboardingGizmoGroupMixin."
        )


@dataclass(frozen=True)
class IconSlot:
    """One slot in a parametric edit gizmo's icon toolbar row.

    The slot's X coordinate is COMPUTED from its index in ``feature_slots`` —
    never set explicitly. Adding an icon is a one-line append; the layout
    manager resolves the X. Hidden slots STILL CONSUME their X position so
    toggling a visibility preference doesn't shift the row.

    Fields:

    - ``gizmo_idname`` — for single-icon slots, the full Blender gizmo
      idname. For multi-variant slots, EITHER a string PREFIX that auto-
      suffixes ``_<variant>`` per member (the common case — e.g.
      ``"VIEW3D_GT_lock"`` + variants ``("open", "closed")`` becomes
      ``VIEW3D_GT_lock_open`` / ``VIEW3D_GT_lock_closed``) OR a tuple of
      explicit idnames matching the variant count when the variants
      don't share a prefix. Attributes created on the gizmo group are
      ``self.<name>_gizmo`` for single slots, ``self.<name>_<variant>_gizmo``
      for each variant in multi-variant slots.
    - ``variants`` — variant suffixes, e.g. ``("open", "closed")`` for a
      lock pair, ``("exterior", "center", "interior")`` for a baseline
      cycle. Empty tuple = single icon.
    - ``color`` — RGB tuple. ``None`` falls back to the gizmo group's default
      decoration color. Use the group's ``COLOR_RED`` / ``COLOR_GREEN`` /
      ``COLOR_BLUE`` literals for state-coded icons.
    - ``extra_gap_before`` — extra spacing past the default uniform gap, in
      meters. Use sparingly — e.g. to visually separate a destructive
      action (trash) from the routine edit controls.
    - ``operator_props`` — tuple of (key, value) pairs forwarded to
      ``target_set_operator``'s return value (e.g. ``increment=1`` for a
      +/- adjuster, ``property_name="..."`` for a generic toggle).
    - ``placeholder`` — when ``True``, the slot reserves an X position in
      the row but no auto-managed gizmo is created. Subclasses look the X
      up via ``_slot_x_positions()[name]`` to place their own dynamically-
      built gizmos (e.g. a live count label). ``gizmo_idname`` / ``operator``
      are unused for placeholders."""

    name: str
    gizmo_idname: str | tuple[str, ...] = ""
    operator: str = ""
    # Matches DEFAULT_BILLBOARD_SCALE — the scale validate/cancel render at,
    # so slots that don't override land at the same visual size by default.
    # Helper icons (+/- count adjusters, lock pairs, delete) override with
    # smaller values (0.20 - 0.35) to signal secondary affordance.
    scale: float = DEFAULT_BILLBOARD_SCALE
    color: tuple[float, float, float] | None = None
    variants: tuple[str, ...] = ()
    extra_gap_before: float = 0.0
    operator_props: tuple[tuple[str, Any], ...] = ()
    placeholder: bool = False
    # Optional per-frame visibility predicate. Called with the gizmo group
    # instance as the sole argument; returning False hides this slot's gizmo
    # while still reserving its X position so the row layout doesn't shift.
    # Used for idle-row icons whose relevance depends on element state (e.g.
    # toggle_openings only when the host has openings).
    visible_when: Optional[Callable[[Any], bool]] = None

    def __post_init__(self) -> None:
        # Validate shape at class-definition time so a typo doesn't surface
        # as a runtime error in the gizmo group's setup() three layers deep.
        if self.placeholder:
            return
        if self.variants:
            if isinstance(self.gizmo_idname, str):
                pass  # prefix form — idname auto-suffixed per variant
            elif isinstance(self.gizmo_idname, tuple) and len(self.gizmo_idname) == len(self.variants):
                pass  # explicit-tuple form
            else:
                raise TypeError(
                    f"IconSlot({self.name!r}): variants={self.variants} requires gizmo_idname "
                    f"to be either a string prefix (auto-suffixed as <prefix>_<variant>) or a "
                    f"tuple of {len(self.variants)} explicit idnames, got {self.gizmo_idname!r}"
                )
        elif not isinstance(self.gizmo_idname, str) or not self.gizmo_idname:
            raise TypeError(
                f"IconSlot({self.name!r}): single-icon slot requires gizmo_idname str, "
                f"got {self.gizmo_idname!r} (set variants=(...) if you want a multi-variant "
                f"slot, or placeholder=True for a reserved-position slot)"
            )

    def variant_idnames(self) -> tuple[str, ...]:
        """Resolve per-variant gizmo idnames. For prefix form, suffix each
        variant onto the prefix; for tuple form, return as is. Single-icon
        slots return a one-element tuple containing the idname."""
        if not self.variants:
            assert isinstance(self.gizmo_idname, str)
            return (self.gizmo_idname,)
        if isinstance(self.gizmo_idname, str):
            return tuple(f"{self.gizmo_idname}_{variant}" for variant in self.variants)
        return self.gizmo_idname

    def gizmo_attrs(self) -> tuple[str, ...]:
        """Names of every ``self.*`` attribute this slot writes during setup.
        Returns one for a single slot, N for an N-variant slot, and an empty
        tuple for placeholder slots (which reserve X without an auto-gizmo)."""
        if self.placeholder:
            return ()
        if self.variants:
            return tuple(f"{self.name}_{variant}_gizmo" for variant in self.variants)
        return (f"{self.name}_gizmo",)


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

    Color Convention
    ================

    Gizmo colors follow Blender's axis convention:
    - RED: X-axis dimensions (width)
    - GREEN: Y-axis dimensions (depth)
    - BLUE: Z-axis dimensions (height)

    View Direction API
    ==================

    Use ``ViewDirection.from_context(context, mw)`` to determine camera position::

        view = ViewDirection.from_context(context, obj.matrix_world)
        if view.from_back:  # Camera behind element (interior for doors)
            y_pos = props.depth
        if view.from_left:  # Camera on left side
            x_pos = -offset

    Negative Value Handling
    =======================

    Some dimensions support negative values (e.g., lining_offset). When negative,
    the gizmo is flipped 180° using FLIP_MATRIX so the arrow points opposite.
    """

    # === Gizmo Colors ===
    # Aliased to the module-level constants so subclass class bodies can
    # reference either spelling. Match Blender's axis convention:
    # X=red, Y=green, Z=blue.
    COLOR_RED = COLOR_RED
    COLOR_GREEN = COLOR_GREEN
    COLOR_BLUE = COLOR_BLUE
    COLOR_NEUTRAL = COLOR_NEUTRAL

    # === Dimension Gizmo Layout (meters) ===
    ARROW_SCALE = 0.25  # Scale factor for arrow gizmos
    GIZMO_OFFSET = 0.15  # Distance from geometry edge to dimension line
    GIZMO_STACK_OFFSET = 0.1  # Offset increment for stacking multiple gizmos to avoid overlap
    GIZMO_CLAMP_MAX = 10000.0  # Maximum value for dimension clamping (meters)

    # Pre-computed flip matrix for negative value handling (180° rotation around Z)
    FLIP_MATRIX = Matrix.Rotation(math.pi, 4, "Z")

    # Default: dimension drags respect Blender's global snap (Ctrl-toggleable
    # during drag). Subclasses whose dimensions float in viewport space rather
    # than aligning to real-world geometry should override to ``False`` —
    # snapping to scene vertices in that case produces spurious value jumps
    # as the mouse crosses unrelated meshes.
    snap_enabled_on_dimensions: bool = True

    # === Icon Gizmo Layout (meters) ===
    # Icons are positioned in a horizontal row above the element:
    #   [Validate] [Cancel] [Cycle]
    #      0.0       0.5     0.87   <- X positions (ICON_VALIDATE_X + offset)
    EDITING_ICON_SCALE = 0.2  # Scale for editing icon gizmos (validate, cancel, cycle)
    ICON_VALIDATE_X = 0.0  # X position of validate (checkmark) icon
    ICON_CANCEL_X = 0.5  # X offset from validate for cancel (X) icon
    ICON_CYCLE_X = 0.87  # X offset from validate for cycle (arrow) icon
    # Subclasses append to declare feature icons in the edit-mode toolbar row.
    # The layout manager assigns each slot an X position from its tuple
    # index — adding a new icon is a one-line append, no hardcoded X
    # constant, no "remember to bump the right edge" rule. The trailing
    # ARRAY button is positioned past the last slot automatically.
    feature_slots: ClassVar[tuple[IconSlot, ...]] = ()
    # Idle-mode pen-row extras (e.g. wall's toggle_openings). Each slot is
    # placed past the pen at uniform ``ICON_ARRAY_GAP`` spacing. Hidden during
    # edit — the validate/cancel row owns the X positions there. Peer gizmo
    # groups (e.g. ``GizmoArrayEdition``'s per-layer ARRAY icons) query
    # ``_idle_row_right_edge()`` to position past these without a hardcoded
    # per-feature table.
    idle_slots: ClassVar[tuple[IconSlot, ...]] = ()
    # Gap between adjacent slots past the leading validate/cancel/cycle
    # triplet, AND between the last slot and the ARRAY button.
    ICON_ARRAY_GAP: float = 0.37
    ICON_Z_OFFSET = 0.5  # Height above element for icons
    ICON_Y_OFFSET = GIZMO_OFFSET * 2  # Y offset to keep icons clear of geometry
    # Offset (meters in world units) used along the screen-up direction when
    # world-Z stacking would project to zero on screen (plan / top-down views).
    SCREEN_STACK_OFFSET = 0.5

    dimension_gizmo_props: list[DimensionGizmoConfig] = []
    enable_editing_operator: str = ""
    finish_editing_operator: str = ""
    cancel_editing_operator: str = ""
    # Mutually exclusive; cycle for 2-4 values, pick for 5+.
    cycle_type_operator: str = ""
    pick_type_operator: str = ""

    REGISTRY: list[type] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseParametricGizmoGroup.REGISTRY.append(cls)

    @classmethod
    def _slot_x_positions(cls) -> dict[str, float]:
        """Map each ``feature_slot`` name to its X coordinate in the row.

        Slots are laid out from the cycle position onward at uniform
        ``ICON_ARRAY_GAP`` spacing, plus any per-slot ``extra_gap_before``.
        When the cycle slot is unused (no ``cycle_type_operator`` /
        ``pick_type_operator``), the first feature slot collapses into the
        cycle position so the row stays tight — that's how wall's baseline
        triplet ends up at X=0.87 without a gap before it. Tuple order is
        the only thing that controls X; rearranging the tuple rearranges
        the row."""
        positions: dict[str, float] = {}
        has_cycle = bool(cls.cycle_type_operator) or bool(cls.pick_type_operator)
        next_x = (cls.ICON_CYCLE_X + cls.ICON_ARRAY_GAP) if has_cycle else cls.ICON_CYCLE_X
        for slot in cls.feature_slots:
            next_x += slot.extra_gap_before
            positions[slot.name] = next_x
            next_x += cls.ICON_ARRAY_GAP
        return positions

    @classmethod
    def _feature_row_right_edge(cls) -> float:
        """Right edge of the feature icon row, fed to the trailing ARRAY
        button's X. Computed strictly from slot order + gaps; empty
        ``feature_slots`` collapses to the cycle position."""
        positions = cls._slot_x_positions()
        if not positions:
            return cls.ICON_CYCLE_X
        return max(positions.values())

    @classmethod
    def _idle_slot_x_positions(cls) -> dict[str, float]:
        """Map each ``idle_slot`` name to its X coordinate past the pen.

        First idle slot lands at ``ICON_CANCEL_X`` (the cancel-slot position,
        unused in idle since validate/cancel are edit-only). Successive slots
        are spaced by ``ICON_ARRAY_GAP``, plus any per-slot ``extra_gap_before``."""
        positions: dict[str, float] = {}
        next_x = cls.ICON_CANCEL_X
        for slot in cls.idle_slots:
            next_x += slot.extra_gap_before
            positions[slot.name] = next_x
            next_x += cls.ICON_ARRAY_GAP
        return positions

    @classmethod
    def _idle_row_right_edge(cls) -> float:
        """Rightmost local-X reserved by this group's idle row. Returns the
        pen position (``ICON_VALIDATE_X``) when no idle slots are declared
        so peer queries always get a meaningful number."""
        positions = cls._idle_slot_x_positions()
        if not positions:
            return cls.ICON_VALIDATE_X
        return max(positions.values())

    @classmethod
    def pick_visible_anchor(cls, context: bpy.types.Context, world_base: Vector, world_top: Vector) -> Vector:
        """Choose between two anchor candidates so vertical separation stays
        visible regardless of view orientation.

        In 3D views the world-Z gap between base and top reads cleanly on
        screen, so return ``world_top``. In plan / top-down views that gap
        projects to zero and the icons stack on each other; return
        ``world_base`` lifted along screen-up by ``SCREEN_STACK_OFFSET`` so
        the icons stay individually visible and clickable."""
        if tool.Blender.is_view_top_down(context):
            return world_base + tool.Blender.get_screen_up_world(context) * cls.SCREEN_STACK_OFFSET
        return world_top

    @classmethod
    def get_color_from_name(cls, color: GizmoColor | str) -> tuple[float, float, float]:
        """Get color tuple from GizmoColor enum or color name string."""
        colors = {
            GizmoColor.RED: cls.COLOR_RED,
            GizmoColor.GREEN: cls.COLOR_GREEN,
            GizmoColor.BLUE: cls.COLOR_BLUE,
        }
        if isinstance(color, GizmoColor):
            return colors.get(color, cls.COLOR_RED)
        # Handle legacy string input
        return colors.get(GizmoColor(color.upper()), cls.COLOR_RED)

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

        Note: Consider using ViewDirection.from_context() for a cleaner API.
        """
        rv3d = context.region_data
        if not rv3d:
            return False, False

        view_direction = Vector(rv3d.view_rotation @ Vector((0, 0, -1)))
        local_view_dir = world_matrix.inverted().to_3x3() @ view_direction

        viewing_from_negative_y = local_view_dir.y < 0
        viewing_from_negative_x = local_view_dir.x < 0

        return viewing_from_negative_y, viewing_from_negative_x

    def get_view_direction(self, context: bpy.types.Context, world_matrix: Matrix) -> "ViewDirection":
        """Get view direction as a ViewDirection object for cleaner API.

        Example:
            view = self.get_view_direction(context, mw)
            if view.from_back:
                y_pos = props.depth
            else:
                y_pos = 0
        """
        from_neg_y, from_neg_x = self.get_local_view_direction(context, world_matrix)
        return ViewDirection(from_negative_y=from_neg_y, from_negative_x=from_neg_x)

    def update_gizmo_visibility(self, gizmo: bpy.types.Gizmo, is_editing: bool) -> bool:
        """Hide ``gizmo`` when not editing or when a modal owns the viewport.
        Returns True if the gizmo is now visible."""
        if self.is_gizmo_hidden_by_modal(gizmo):
            gizmo.hide = True
            return False
        gizmo.hide = not is_editing
        return not gizmo.hide

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

    @staticmethod
    def get_camera_facing_outer_y(
        viewing_from_negative_y: bool,
        near_y: float,
        far_y: float,
        gizmo_offset: float = 0.0,
    ) -> float:
        """Y coordinate just outside the camera-facing face of an element.

        Generalises `get_y_position_for_view` for elements whose near face
        isn't at the local origin. ``near_y`` is the local-Y of the -Y face;
        ``far_y`` is the local-Y of the +Y face. Returns the Y just *outside* the
        face the camera is currently looking at, pushed by ``gizmo_offset`` (use
        ``cls.GIZMO_OFFSET`` for the standard handle gap).

        Suits walls (``near_y = props.offset``, ``far_y = props.offset + props.thickness``)
        and any other element whose section sits inside a non-zero Y band. Stair /
        door / window can also call this once their callers pass explicit near/far
        instead of the implicit ``width_attr`` pattern, eliminating
        ``get_y_position_for_view``, ``get_lining_y_position_for_view`` etc. as
        wrappers around the same shape — but they're left intact for now to avoid
        churning code paths that already work."""
        if viewing_from_negative_y:
            return near_y - gizmo_offset
        return far_y + gizmo_offset

    def get_icon_y_for_view(self, props, viewing_from_negative_y: bool) -> float:
        """Get Y position for editing icons based on view direction.

        Similar to get_y_position_for_view but always includes offset and
        uses the element's furthest Y extent for positioning.

        Args:
            props: Element properties object
            viewing_from_negative_y: True if viewing from -Y side

        Returns:
            Y position for icon row: -GIZMO_OFFSET when viewing from -Y,
                                     width + GIZMO_OFFSET otherwise
        """
        width = getattr(props, "width", 0)
        if viewing_from_negative_y:
            return -self.GIZMO_OFFSET
        return width + self.GIZMO_OFFSET

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

    def get_lining_y_position_for_view(self, props, viewing_from_negative_y: bool, use_offset: bool = True) -> float:
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

    def get_x_positions_for_view(
        self, width: float, offset: float, viewing_from_negative_x: bool
    ) -> tuple[float, float]:
        """Get X positions for height and lining gizmos based on view direction.

        When viewing from -X side, height goes to -X and lining goes to +X.
        When viewing from +X side, height goes to +X and lining goes to -X.

        Args:
            width: Element width (e.g., overall_width)
            offset: Additional offset (e.g., casing_thickness)
            viewing_from_negative_x: True if viewing from -X side

        Returns:
            Tuple of (x_pos_height, x_pos_lining)
        """
        if viewing_from_negative_x:
            x_pos_height = -offset - self.GIZMO_OFFSET
            x_pos_lining = width + offset + self.GIZMO_OFFSET
        else:
            x_pos_height = width + offset + self.GIZMO_OFFSET
            x_pos_lining = -offset - self.GIZMO_OFFSET
        return x_pos_height, x_pos_lining

    def get_dimension_matrix_lining_offset_default(self, props) -> Matrix:
        """Default lining offset matrix for door/window elements.

        Position at element width + offset, at Y=0, below the element.
        Override in subclass if different positioning is needed.
        """
        width = getattr(props, "overall_width", 0)
        return self.compose_gizmo_matrix(Vector((width + self.GIZMO_OFFSET, 0, -self.GIZMO_OFFSET)), (0, 1, 0))

    def get_casing_offset(self, props) -> float:
        """Get casing offset for view-dependent dimension positioning.

        Override in door to return casing_thickness when lining_offset is 0.
        Default returns 0 (no casing offset).
        """
        return 0.0

    def _update_view_dependent_dimensions(self, context: bpy.types.Context, mw: Matrix, props) -> None:  # noqa: ARG002
        """Update overall_width, overall_height, and lining_offset based on view direction.

        This base implementation handles the common pattern for door/window gizmos.
        Subclasses can override get_casing_offset() to customize behavior.
        """
        viewing_from_negative_y, viewing_from_negative_x = self._frame_view_dir
        y_pos = self.get_lining_y_position_for_view(props, viewing_from_negative_y)

        self.set_dimension_gizmo_position("overall_width", mw, Vector((0, y_pos, -self.GIZMO_OFFSET)), (1, 0, 0))

        casing_offset = self.get_casing_offset(props)
        x_pos_height, x_pos_lining = self.get_x_positions_for_view(
            props.overall_width, casing_offset, viewing_from_negative_x
        )
        self.set_dimension_gizmo_position("overall_height", mw, Vector((x_pos_height, y_pos, 0)), (0, 0, 1))
        self.set_dimension_gizmo_position(
            "lining_offset", mw, Vector((x_pos_lining, 0, -self.GIZMO_OFFSET)), (0, 1, 0), props.lining_offset
        )

    def create_icon_gizmo(
        self,
        gizmo_type: str,
        color: tuple[float, float, float],
        operator: str,
        alpha: float = 0.8,
        **operator_props,
    ) -> bpy.types.Gizmo:
        """Create an icon gizmo with common settings.

        State-aware icons must use a static pair (open/closed) and have the
        consumer pick which one to show.
        """
        prefs = tool.Blender.get_addon_preferences()
        highlight_color = prefs.decorator_color_selected[:3]

        gz = self.gizmos.new(gizmo_type)
        gz.use_draw_scale = False
        gz.color = color
        gz.color_highlight = highlight_color
        gz.alpha = alpha
        op = gz.target_set_operator(operator)
        for key, value in operator_props.items():
            setattr(op, key, value)
        return gz

    def create_arc_gizmo(
        self,
        color: tuple[float, float, float],
        operator: str,
        alpha: float = 0.5,
        **operator_props,
    ) -> bpy.types.Gizmo:
        return self.create_icon_gizmo("VIEW3D_GT_arc", color, operator, alpha, **operator_props)

    def create_icon_gizmo_lock_pair(
        self,
        operator: str,
        open_color: tuple[float, float, float],
        closed_color: tuple[float, float, float] | None = None,
        alpha: float = 0.8,
        **operator_props,
    ) -> tuple[bpy.types.Gizmo, bpy.types.Gizmo]:
        """Create an open/closed padlock gizmo pair sharing one operator binding.

        ``closed_color`` defaults to ``open_color`` for neutral pairs. Caller
        hides whichever member is inappropriate for the current state, then
        positions both together via ``set_icon_gizmo_pair_position`` so a
        state flip can't reveal a stale pose."""
        if closed_color is None:
            closed_color = open_color
        open_gz = self.create_icon_gizmo("VIEW3D_GT_lock_open", open_color, operator, alpha, **operator_props)
        closed_gz = self.create_icon_gizmo("VIEW3D_GT_lock_closed", closed_color, operator, alpha, **operator_props)
        return open_gz, closed_gz

    @classmethod
    def is_element_type(cls, element) -> bool:
        raise NotImplementedError("Subclass must implement is_element_type()")

    @classmethod
    def poll(cls, context) -> bool:
        obj = tool.Blender.get_active_object(is_selected=True)
        if obj is None:
            return False
        if not tool.Blender.are_viewport_gizmos_enabled():
            return False
        # Hide every parametric gizmo while any preview is open — the preview
        # is the only interactive surface in that mode, sister gizmos would
        # compete for screen space and let the user trigger mutations that
        # would race the preview's in-progress draft.
        from bonsai.bim.module.model import preview_base

        if preview_base.any_preview_active(context):
            return False
        if _is_transform_modal_active(context):
            return False
        if cls.gizmo_pref_name:
            prefs = tool.Blender.get_addon_preferences()
            if not getattr(prefs.gizmos, cls.gizmo_pref_name, True):
                return False
        if len(tool.Blender.get_selected_objects()) != 1:
            return False
        element = tool.Ifc.get_entity(obj)
        if not element:
            return False
        # Array children are managed replicas — their parametric attributes get
        # overwritten on the next ``regenerate_array``, so editing them via the
        # parametric gizmos would be silently undone. Skip across every gizmo
        # group (door/window/stair/wall/roof/railing/array all inherit this poll).
        if tool.Blender.Modifier.is_array_child(element):
            return False
        if not cls.is_element_type(element):
            return False
        # Mutual exclusion between parametric and array edit lifecycles — running two
        # finish operators against the same object would race, and the doubled
        # validate/cancel icon stack reads as a UI bug. Hide this gizmo group
        # while a different parametric type is in an active edit lifecycle on obj.
        if cls._other_parametric_edit_active(obj):
            return False
        return True

    @classmethod
    def _other_parametric_edit_active(cls, obj: bpy.types.Object) -> bool:
        """True if any parametric type OTHER than this group's own is in an
        active edit lifecycle on ``obj``."""
        return tool.Parametric.is_object_editing(obj, skip_name=getattr(cls, "gizmo_pref_name", None)) is not None

    def setup(self, context: bpy.types.Context) -> None:
        """Template method for gizmo setup.

        Subclasses should override setup_element_specific_gizmos() to add
        element-specific gizmos (e.g., door swing arcs, stair lock icons).
        """
        self.setup_editing_gizmos(context)
        self.setup_dimension_gizmos(context)
        self.setup_element_specific_gizmos(context)

    def setup_element_specific_gizmos(self, context: bpy.types.Context) -> None:
        """Override to add element-specific gizmos.

        Called after setup_editing_gizmos and setup_dimension_gizmos.
        Examples: door swing arcs, stair lock/plus/minus icons.
        """
        pass

    # Frame-scoped caches primed at the top of ``refresh()`` and ``draw_prepare()``.
    # Every per-frame helper — preferences access, view-direction lookup, billboard
    # rotation — reads these instead of re-deriving the same values, since each
    # gizmo group ends up needing them 2–5× per frame across its position helpers.
    _frame_prefs: Any = None
    _frame_view_dir: tuple[bool, bool] | None = None
    _frame_billboard_rot: "Matrix | None" = None

    def _prime_frame_caches(self, context: bpy.types.Context, mw: "Matrix") -> None:
        self._frame_prefs = tool.Blender.get_addon_preferences()
        self._frame_view_dir = self.get_local_view_direction(context, mw)
        self._frame_billboard_rot = get_billboard_rotation(context)

    def refresh(self, context: bpy.types.Context) -> None:
        """Template method for gizmo refresh.

        Subclasses should override _refresh_element_specific() for element-specific updates
        (e.g., door swing arcs, stair lock icons).
        """
        if not self.is_setup_complete():
            return
        obj = context.active_object
        if not obj:
            return

        props = self.get_props(obj)
        mw = obj.matrix_world
        self._prime_frame_caches(context, mw)
        self.update_editing_gizmos(context, mw, props)
        self.update_dimension_gizmos(mw, props)
        self._refresh_element_specific(context, mw, props)

    def _refresh_element_specific(self, context: bpy.types.Context, mw: "Matrix", props) -> None:  # noqa: ARG002
        """Override for element-specific refresh logic.

        Called from both refresh() (on state change) and draw_prepare() (per frame),
        so any override must be idempotent and cheap. Use this to re-position or
        re-billboard element-specific gizmos (door swing arcs, stair lock/+/- icons,
        wall cursor icons, etc.).
        """
        pass

    # Subclass should define these class attributes for metadata-driven dispatch.
    # ``gizmo_pref_name`` matches a flat BoolProperty field on
    # ``GizmoPreferences`` and gates the whole gizmo group's poll.
    props_getter: Callable[[bpy.types.Object], bpy.types.PropertyGroup] | None = None
    gizmo_pref_name: str | None = None  # e.g., "door"

    def get_props(self, obj: bpy.types.Object) -> Any:
        """Get properties for the element.

        Subclass can either:
        1. Define class attribute `props_getter` (e.g., tool.Model.get_door_props)
        2. Override this method directly

        The ``props_getter`` reference is captured at class-definition time
        (early binding), so tests cannot redirect it via
        ``patch.object(tool.Model, "get_X_props", ...)``. Inject a stub
        callable directly when exercising dispatch in tests.
        """
        if self.props_getter:
            return self.props_getter(obj)
        raise NotImplementedError("Subclass must define props_getter or override get_props()")

    def get_addon_prefs(self):
        """Return the addon preferences struct. Inside ``refresh`` / ``draw_prepare``
        the frame cache is hit; outside (e.g. ``setup``) we fall through to a fresh
        lookup so callers don't have to know which call path they're on."""
        return self._frame_prefs if self._frame_prefs is not None else tool.Blender.get_addon_preferences()

    def get_decoration_colors(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        """Get default and highlight colors from preferences.

        Returns:
            Tuple of (default_color, highlight_color) as RGB tuples.
        """
        prefs = self.get_addon_prefs()
        return prefs.decorations_colour[:3], prefs.decorator_color_selected[:3]

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
        scale: float = DEFAULT_BILLBOARD_SCALE,
    ) -> None:
        if gz := self.get_gizmo_if_visible(gizmo_name):
            world_pos = mw @ Vector((x, y, z))
            gz.matrix_basis = billboarded_at(world_pos, billboard_rot, scale)

    def set_icon_gizmo_pair_position(
        self,
        open_name: str,
        closed_name: str,
        mw: Matrix,
        x: float,
        y: float,
        z: float,
        billboard_rot: Matrix,
        scale: float = DEFAULT_BILLBOARD_SCALE,
    ) -> None:
        """Position both members of an open/closed pair at the same anchor;
        write the matrix on both so a state flip can't reveal a stale pose."""
        open_gz = getattr(self, open_name, None)
        closed_gz = getattr(self, closed_name, None)
        if not open_gz or not closed_gz:
            return
        world_pos = mw @ Vector((x, y, z))
        matrix = billboarded_at(world_pos, billboard_rot, scale)
        open_gz.matrix_basis = matrix
        closed_gz.matrix_basis = matrix

    def set_dimension_gizmo_position(
        self,
        attr_name: str,
        mw: Matrix,
        position: Vector,
        axis: tuple[int, int, int],
        value: float | None = None,
    ) -> None:
        """Set a dimension gizmo's position if visible.

        Args:
            attr_name: The dimension attribute name (e.g., "overall_width")
            mw: Object's world matrix
            position: Local position as Vector or tuple (x, y, z)
            axis: Direction axis tuple (e.g., (1, 0, 0) for X)
            value: Optional value to check for negative flip. If None, no flip is applied.
        """
        if gz := self.get_dimension_gizmo_if_visible(attr_name):
            self._apply_dimension_matrix(gz, mw, self.compose_gizmo_matrix(position, axis), value)

    def _apply_dimension_matrix(
        self,
        gizmo: bpy.types.Gizmo,
        mw: Matrix,
        base_matrix: Matrix,
        value: float | None = None,
    ) -> None:
        """Apply matrix to dimension gizmo, flipping for negative values.

        Consolidates negative value handling in one place. For negative values,
        the gizmo is rotated 180° around Z so the dimension arrow points in the
        opposite direction while keeping the origin at the same position.

        Args:
            gizmo: The dimension gizmo to update
            mw: Object's world matrix
            base_matrix: Local transformation matrix
            value: If negative, applies FLIP_MATRIX rotation
        """
        if value is not None and value < 0:
            gizmo.matrix_basis = mw @ base_matrix @ self.FLIP_MATRIX
        else:
            gizmo.matrix_basis = mw @ base_matrix

    def should_hide_dimension_gizmo(self, gizmo: bpy.types.Gizmo, config: "DimensionGizmoConfig", props) -> bool:
        """Hide a dimension gizmo when its modal owner is active, when the
        element isn't in edit state for this attribute, or when the config
        carries a custom visibility predicate that rejects ``props``. The
        per-feature enable toggle is gated upstream by ``poll()``."""
        if self.is_gizmo_hidden_by_modal(gizmo):
            return True
        if self.should_hide_gizmo(config.attr_name, props):
            return True
        if config.visibility_condition and not config.visibility_condition(props):
            return True
        return False

    def _setup_icon_gizmo(
        self,
        gizmo_type: str,
        color: tuple[float, float, float],
        operator: str,
        highlight_color: tuple[float, float, float] | None = None,
        alpha: float = 0.8,
    ) -> bpy.types.Gizmo:
        """Create and configure an icon gizmo with standard settings.

        Thin wrapper over `setup_icon_gizmo` that defaults ``highlight_color``
        to the addon-prefs selection color via ``get_decoration_colors``.
        """
        if highlight_color is None:
            _, highlight_color = self.get_decoration_colors()
        return setup_icon_gizmo(self, gizmo_type, color, highlight_color, operator, alpha)

    def setup_editing_gizmos(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()

        # Pen icon is bound to ``bim.enable_editing_parametric`` (a universal dispatcher)
        # rather than the gizmo group's own enable op directly. The dispatcher receives
        # this group's ``enable_editing_operator`` as ``feature_enable_op`` and:
        #   - plain click → fires the per-feature enable (this group's operator)
        #   - Shift+click → fires ``bim.enable_editing_array`` if the active element is
        #     an array parent (one pen icon, two behaviours; no second pen needed for arrays).
        self.pen_gizmo = self.gizmos.new("VIEW3D_GT_pen")
        self.pen_gizmo.use_draw_scale = False
        self.pen_gizmo.color = default_color
        self.pen_gizmo.color_highlight = highlight_color
        self.pen_gizmo.alpha = 0.8
        pen_op = self.pen_gizmo.target_set_operator("bim.enable_editing_parametric")
        pen_op.feature_enable_op = self.enable_editing_operator

        self.validate_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_validate", self.COLOR_GREEN, self.finish_editing_operator, highlight_color
        )
        self.cancel_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_cancel", self.COLOR_RED, self.cancel_editing_operator, highlight_color
        )

        # Type-selector slot: cycle (one click advances) or pick (popup menu).
        # ``self.cycle_gizmo`` is the shared instance name regardless of icon —
        # consumers reposition / hide it via that attribute. ``cycle_type_operator``
        # wins if both are set (consumers shouldn't set both).
        if self.cycle_type_operator:
            self.cycle_gizmo = self._setup_icon_gizmo(
                "VIEW3D_GT_cycle", default_color, self.cycle_type_operator, highlight_color
            )
        elif self.pick_type_operator:
            self.cycle_gizmo = self._setup_icon_gizmo(
                "VIEW3D_GT_menu", default_color, self.pick_type_operator, highlight_color
            )

        # Feature-specific edit-row icons. Subclasses declare them via
        # ``feature_slots``; multi-variant slots create one gizmo per
        # variant at the same X (e.g. a lock pair, a baseline triplet) and
        # the subclass picks which is visible per frame. Placeholder slots
        # only reserve an X position — the subclass creates its own gizmo
        # there in ``setup_element_specific_gizmos``.
        for slot in self.feature_slots:
            if slot.placeholder:
                continue
            slot_color = slot.color if slot.color is not None else default_color
            kwargs = dict(slot.operator_props)
            for attr, idname in zip(slot.gizmo_attrs(), slot.variant_idnames()):
                gz = self.create_icon_gizmo(idname, slot_color, slot.operator, **kwargs)
                setattr(self, attr, gz)

        # Idle-mode pen-row extras. Same creation path as feature_slots; the
        # IDLE branch of ``update_editing_gizmos`` positions and visibility-
        # gates them, the EDIT branch hides them so the validate/cancel row
        # owns the X positions.
        for slot in self.idle_slots:
            if slot.placeholder:
                continue
            slot_color = slot.color if slot.color is not None else default_color
            kwargs = dict(slot.operator_props)
            for attr, idname in zip(slot.gizmo_attrs(), slot.variant_idnames()):
                gz = self.create_icon_gizmo(idname, slot_color, slot.operator, **kwargs)
                setattr(self, attr, gz)

        # ARRAY button — visible during the feature edit lifecycle only (positioned by
        # ``update_editing_gizmos``). Click commits the current edit and adds a
        # Blender-vanilla-defaulted array (count=2, X-offset = bbox extent). The
        # array gizmo group opts out via ``hide_array_button = True`` since
        # adding an array to an array layer is the panel's job, not a gizmo's.
        if not getattr(self, "hide_array_button", False):
            self.array_gizmo = self._setup_icon_gizmo(
                "VIEW3D_GT_array_all",
                default_color,
                "bim.add_array_from_feature_edit",
                highlight_color,
            )

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
        """Setter closure. ``min_value`` clamps only on the default
        ``attr_name`` path; a custom ``apply_value`` owns its own bounding."""
        if config.apply_value:
            apply_fn = config.apply_value

            def move_set(value):
                obj = bpy.context.active_object
                if not obj:
                    return
                apply_fn(self.get_props(obj), value)

            return move_set

        attr_name, min_val = config.attr_name, config.min_value

        def move_set(value):
            obj = bpy.context.active_object
            if not obj:
                return
            setattr(self.get_props(obj), attr_name, max(min_val, value))

        return move_set

    # Fixed visual length (world units) for count gizmos. Decoupled from the
    # underlying integer value so a count of 99 doesn't render as a 99-metre bar.
    COUNT_GIZMO_VISUAL_LENGTH = 0.3

    def _make_count_setter(self, config: "CountGizmoConfig"):
        """Create setter closure for count gizmo. Snaps to integer step and
        clamps to [min_count, max_count] before applying."""
        min_count, max_count, step = config.min_count, config.max_count, config.step

        if config.apply_value:
            apply_fn = config.apply_value

            def move_set(value):
                obj = bpy.context.active_object
                if not obj:
                    return
                snapped = max(min_count, min(max_count, int(round(value / step)) * step))
                apply_fn(self.get_props(obj), snapped)

            return move_set

        attr_name = config.attr_name

        def move_set(value):
            obj = bpy.context.active_object
            if not obj:
                return
            snapped = max(min_count, min(max_count, int(round(value / step)) * step))
            setattr(self.get_props(obj), attr_name, snapped)

        return move_set

    def _setup_count_gizmo(self, config: "CountGizmoConfig", highlight_color: tuple[float, float, float]) -> None:
        """Configure a BIM_GT_gizmo_dimension instance to behave as an integer stepper.

        Reuses the dimension gizmo type — only configuration differs (no arrows,
        no extension lines, int-snapped setter, count_formatter as text_formatter,
        fixed visual length applied per-frame in ``update_dimension_gizmos``)."""
        gizmo = self.gizmos.new("BIM_GT_gizmo_dimension")
        gizmo.move_get_cb = self._make_dimension_getter(config)
        gizmo.move_set_cb = self._make_count_setter(config)
        gizmo.axis = Vector(config.axis)
        gizmo.local_axis = Vector(config.axis)
        gizmo.invert_delta = False
        gizmo.delta_scale = config.delta_scale
        gizmo.prop_name = config.prop_name
        gizmo.gizmo_group = self
        # Count formatter receives (props, value) like text_formatter; the
        # dimension gizmo's draw path calls it once per frame.
        gizmo.text_formatter = config.count_formatter or (lambda props, value: str(int(value)))
        gizmo.color = self.get_color_from_name(config.color)
        gizmo.color_highlight = highlight_color
        gizmo.alpha = 1.0
        gizmo.use_draw_modal = True
        gizmo.use_draw_scale = False
        gizmo.text_offset_sign = 1
        gizmo.text_alignment = TextAlignment.CENTER
        # Count visual is a plain bar — no arrows, no extension lines.
        gizmo.show_start_arrow = False
        gizmo.show_end_arrow = False
        gizmo.show_extension_lines = False
        setattr(self, f"dimension_{config.attr_name}_gizmo", gizmo)

    def setup_dimension_gizmos(self, context: bpy.types.Context) -> None:
        """Set up value gizmos (dimensions and counts) from dimension_gizmo_props."""
        prefs = tool.Blender.get_addon_preferences()
        highlight_color = prefs.decorator_color_selected[:3]

        for config in getattr(self, "dimension_gizmo_props", []):
            if isinstance(config, CountGizmoConfig):
                self._setup_count_gizmo(config, highlight_color)
                continue
            gizmo = self.gizmos.new("BIM_GT_gizmo_dimension")
            gizmo.move_get_cb = self._make_dimension_getter(config)
            gizmo.move_set_cb = self._make_dimension_setter(config)
            gizmo.axis = Vector(config.axis)
            gizmo.local_axis = Vector(config.axis)
            gizmo.invert_delta = config.invert_delta
            gizmo.delta_scale = config.delta_scale
            gizmo.prop_name = config.prop_name  # Auto-derived in __post_init__
            gizmo.gizmo_group = self
            gizmo.text_formatter = config.text_formatter
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
        """Update value gizmos (dimensions and counts) from dimension_gizmo_props."""
        for config in getattr(self, "dimension_gizmo_props", []):
            gizmo = getattr(self, f"dimension_{config.attr_name}_gizmo", None)
            if gizmo is None:
                continue

            if self.should_hide_dimension_gizmo(gizmo, config, props):
                gizmo.hide = True
                continue

            gizmo.hide = False

            # Priority: config.matrix_position > get_dimension_matrix_* method > Identity.
            if config.matrix_position:
                base_matrix = self.compose_gizmo_matrix(config.matrix_position(props), config.axis)
            else:
                matrix_method = getattr(self, f"get_dimension_matrix_{config.attr_name}", None)
                base_matrix = matrix_method(props) if matrix_method else Matrix.Identity(4)

            if config.compute_value:
                value = config.compute_value(props)
            else:
                value = getattr(props, config.attr_name, 0.0)

            if isinstance(config, CountGizmoConfig):
                # Visual length is decoupled from the integer count — the bar
                # stays at a constant world size while the label tracks ``value``.
                gizmo.matrix_basis = mw @ base_matrix
                gizmo._dimension_length = self.COUNT_GIZMO_VISUAL_LENGTH
                gizmo._display_value = value
                gizmo.select_bias = -self.COUNT_GIZMO_VISUAL_LENGTH
                continue

            # Use consolidated negative value handling
            self._apply_dimension_matrix(gizmo, mw, base_matrix, value)
            gizmo.show_start_arrow = config.show_start_arrow
            gizmo.show_end_arrow = config.show_end_arrow
            gizmo.set_dimension_length(value)

    def get_icon_y_extent(self, props) -> tuple[float, float]:
        """Get Y extents for icon positioning based on element geometry.

        Subclasses should override this to return the furthest geometry extents
        in the +Y and -Y directions from the element origin.

        Returns:
            Tuple of (positive_y_extent, negative_y_extent).
            Both values should be positive (absolute distances).
            The base implementation returns (0, 0).

        Example for a door:
            return (lining_offset + lining_depth + 2*OFFSET, 2*OFFSET)
        """
        return (0.0, 0.0)

    def get_icon_y_offset(self, context: bpy.types.Context, mw: Matrix) -> float:  # noqa: ARG002
        """Get Y offset for icons based on view direction.

        Uses get_icon_y_extent() to determine how far to offset icons based on
        the camera viewing direction. Icons are positioned beyond the geometry
        on the side the camera is viewing from.

        Subclasses typically only need to override get_icon_y_extent().
        """
        obj = context.active_object
        if not obj:
            return self.ICON_Y_OFFSET

        props = self.get_props(obj)
        positive_extent, negative_extent = self.get_icon_y_extent(props)

        if self._frame_view_dir[0]:
            return -negative_extent
        return positive_extent

    def update_editing_gizmos(self, context: bpy.types.Context, mw: Matrix, props) -> None:
        """Update editing icon gizmo positions to billboard toward camera."""
        icon_z = self.get_element_height(props) + self.ICON_Z_OFFSET
        icon_y = self.get_icon_y_offset(context, mw)
        billboard_rot = self._frame_billboard_rot
        # set_icon_gizmo_position no-ops on hidden gizmos (via get_gizmo_if_visible),
        # so the hide flag must be set first; that gates whether the matrix is written.
        if props.is_editing:
            self.pen_gizmo.hide = True
            self.validate_gizmo.hide = self.is_gizmo_hidden_by_modal(self.validate_gizmo)
            self.set_icon_gizmo_position(
                "validate_gizmo", mw=mw, x=self.ICON_VALIDATE_X, y=icon_y, z=icon_z, billboard_rot=billboard_rot
            )
            self.cancel_gizmo.hide = self.is_gizmo_hidden_by_modal(self.cancel_gizmo)
            self.set_icon_gizmo_position(
                "cancel_gizmo",
                mw=mw,
                x=self.ICON_VALIDATE_X + self.ICON_CANCEL_X,
                y=icon_y,
                z=icon_z,
                billboard_rot=billboard_rot,
            )
            if self.cycle_type_operator or self.pick_type_operator:
                self.cycle_gizmo.hide = self.is_gizmo_hidden_by_modal(self.cycle_gizmo)
                self.set_icon_gizmo_position(
                    "cycle_gizmo",
                    mw=mw,
                    x=self.ICON_VALIDATE_X + self.ICON_CYCLE_X,
                    y=icon_y,
                    z=icon_z,
                    billboard_rot=billboard_rot,
                    scale=0.30,
                )
            # Feature slots: per-class IconSlot tuples driven by tuple order.
            # Whole-feature visibility is gated upstream by ``poll()`` against
            # ``prefs.gizmos.<feature>``; positioning happens unconditionally
            # whenever the gizmo group polls visible.
            slot_positions = self._slot_x_positions()
            for slot in self.feature_slots:
                if slot.placeholder:
                    continue
                slot_x = self.ICON_VALIDATE_X + slot_positions[slot.name]
                attrs = slot.gizmo_attrs()
                if slot.variants:
                    # Multi-variant slot: write matrix on every variant member
                    # at the same anchor so a state flip never reveals a stale
                    # pose. The subclass's per-frame hook picks which member
                    # is visible — this loop doesn't toggle hide flags.
                    world_pos = mw @ Vector((slot_x, icon_y, icon_z))
                    matrix = billboarded_at(world_pos, billboard_rot, scale=slot.scale)
                    for attr in attrs:
                        gz = getattr(self, attr, None)
                        if gz is not None:
                            gz.matrix_basis = matrix
                    continue
                gz = getattr(self, attrs[0], None)
                if gz is None:
                    continue
                gz.hide = self.is_gizmo_hidden_by_modal(gz)
                self.set_icon_gizmo_position(
                    attrs[0],
                    mw=mw,
                    x=slot_x,
                    y=icon_y,
                    z=icon_z,
                    billboard_rot=billboard_rot,
                    scale=slot.scale,
                )
            # ARRAY button sits past the last feature-specific icon. Slot-based
            # subclasses derive the right edge from the slot count.
            if hasattr(self, "array_gizmo"):
                self.array_gizmo.hide = self.is_gizmo_hidden_by_modal(self.array_gizmo)
                # 30% smaller than the editing-icon-row default (0.50 → 0.35):
                # the array button is a tertiary affordance compared to the
                # primary pen / validate / cancel triad, and the smaller
                # footprint keeps the edit-mode row from sprawling.
                self.set_icon_gizmo_position(
                    "array_gizmo",
                    mw=mw,
                    x=self.ICON_VALIDATE_X + self._feature_row_right_edge() + self.ICON_ARRAY_GAP,
                    y=icon_y,
                    z=icon_z,
                    billboard_rot=billboard_rot,
                    scale=0.35,
                )
            # Idle-row icons are hidden in edit — validate / cancel sit at
            # the same X positions, so showing both would stack icons.
            for slot in self.idle_slots:
                for attr in slot.gizmo_attrs():
                    gz = getattr(self, attr, None)
                    if gz is not None:
                        gz.hide = True
        else:
            # ``hide_pen_button = True`` keeps the pen permanently hidden — for
            # groups whose edit-mode entry is already provided by another widget
            # in the same viewport region. ``GizmoArrayEdition`` opts in because
            # its clickable ``xN`` count label (``GizmoArrayCount``) is the
            # canonical entry point; surfacing a second pen next to it is the
            # redundant icon the user saw in the array gizmo viewport.
            if getattr(self, "hide_pen_button", False):
                self.pen_gizmo.hide = True
            else:
                self.pen_gizmo.hide = self.is_gizmo_hidden_by_modal(self.pen_gizmo)
                self.set_icon_gizmo_position(
                    "pen_gizmo", mw=mw, x=self.ICON_VALIDATE_X, y=icon_y, z=icon_z, billboard_rot=billboard_rot
                )
            self.validate_gizmo.hide = True
            self.cancel_gizmo.hide = True
            if self.cycle_type_operator or self.pick_type_operator:
                self.cycle_gizmo.hide = True
            for slot in self.feature_slots:
                for attr in slot.gizmo_attrs():
                    gz = getattr(self, attr, None)
                    if gz is not None:
                        gz.hide = True
            if hasattr(self, "array_gizmo"):
                self.array_gizmo.hide = True
            # Idle slots: position past the pen, apply per-slot visible_when
            # so state-dependent icons (e.g. toggle_openings) only render
            # when relevant. Hidden slots STILL consume their X position so
            # the row layout doesn't shift when state flips.
            idle_positions = self._idle_slot_x_positions()
            for slot in self.idle_slots:
                if slot.placeholder:
                    continue
                slot_x = self.ICON_VALIDATE_X + idle_positions[slot.name]
                gate = slot.visible_when
                visible = True if gate is None else bool(gate(self))
                for attr in slot.gizmo_attrs():
                    gz = getattr(self, attr, None)
                    if gz is None:
                        continue
                    if not visible:
                        gz.hide = True
                        continue
                    gz.hide = self.is_gizmo_hidden_by_modal(gz)
                    self.set_icon_gizmo_position(
                        attr,
                        mw=mw,
                        x=slot_x,
                        y=icon_y,
                        z=icon_z,
                        billboard_rot=billboard_rot,
                        scale=slot.scale,
                    )

    def draw_prepare(self, context: bpy.types.Context) -> None:
        """Called before drawing - updates gizmos to face camera.

        This method updates editing gizmos, dimension gizmos, and element-specific
        gizmos. Subclasses can override _update_dimension_gizmo_positions() to
        customize dimension gizmo positioning, and _refresh_element_specific() to
        re-billboard element-specific gizmos per frame.
        """
        if not self.is_setup_complete():
            return
        if apply_transform_modal_draw_gate(self, context):
            return
        obj = context.active_object
        if not obj:
            return
        props = self.get_props(obj)
        mw = obj.matrix_world
        self._prime_frame_caches(context, mw)
        self.update_editing_gizmos(context, mw, props)
        # `update_dimension_gizmos` flips the dimension gizmos' `hide` flag
        # based on `props.is_editing` + per-config visibility conditions.
        # `refresh()` already calls it, but `refresh()` only fires on depsgraph
        # events — a `finish_editing_*` operator that toggles `is_editing` to
        # False without mutating IFC (e.g. wall no-op commit, cancel) does not
        # trigger a depsgraph update, so without this call the dimension gizmos
        # would stay visible until the next user input.
        self.update_dimension_gizmos(mw, props)

        self._update_dimension_gizmo_positions(context, mw, props)

        # Prepare dimension gizmos for drawing
        for _, gizmo in self.iter_visible_dimension_gizmos():
            gizmo.draw_prepare(context)

        self._refresh_element_specific(context, mw, props)

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


class BaseSchematicGizmoGroup(BaseParametricGizmoGroup):
    """Base for parametric gizmo groups that drive a billboarded schematic preview.

    Provides:

    - Schematic-anchored ``BIM_GT_gizmo_dimension`` instances declared via
      ``schematic_dimension_props``. Each dimension is laid out in
      schematic-local coordinates around the schematic anchor and
      billboarded to the camera, so the labelled tag reads the same size
      regardless of the bound value and the camera angle.
    - A GPU draw handler that renders a live mini preview of the element's
      geometry near the icon row. Subclasses build the bmesh in
      ``build_schematic_mesh(props)`` and the handler reuses a cached
      list of local-coordinate edge pairs across redraws.

    Subclasses leave ``dimension_gizmo_props = []`` (the default here) and
    populate ``schematic_dimension_props`` instead. The pen / validate /
    cancel / cycle icon row inherited from the parametric base still applies.

    Decoration-only: the preview mesh is not hit-testable; clicks land on
    the labelled dimensions, which carry the parametric edit semantics.
    """

    # Schematic groups don't draw in-place dimension lines; the parent's
    # setup_dimension_gizmos / update_dimension_gizmos iterate this empty
    # list and become no-ops. The schematic equivalents below take their place.
    dimension_gizmo_props: list[DimensionGizmoConfig] = []

    # Schematic dimensions float in billboarded viewport space, not aligned to
    # real-world geometry. Snapping the dragged tip to scene vertices would
    # produce nonsensical value jumps as the mouse crosses unrelated meshes.
    snap_enabled_on_dimensions: bool = False

    # Declarative dimension configuration consumed by ``setup_schematic_dimensions``
    # and ``update_schematic_dimensions``. Each config produces one
    # ``BIM_GT_gizmo_dimension`` instance positioned at a schematic-local
    # location and billboarded to the camera. The dimension's *visual* length
    # is the actual value rescaled into schematic units via
    # ``_compute_schematic_scale`` and floored at a minimum visible length,
    # so tiny dimensions stay grabable; the *displayed* numeric label still
    # shows the real value via ``text_formatter``.
    schematic_dimension_props: list[DimensionGizmoConfig] = []

    # World-unit half-extent of the schematic decoration box anchored at the
    # icon row. Sliders' ``slider_position`` values are interpreted inside
    # this box; subclasses scale ``build_schematic_mesh`` output to fit it.
    schematic_box_size: float = 0.3

    # Offset from the icon-row anchor (object origin + element height +
    # ICON_Z_OFFSET) to the bottom-centre of the schematic, applied as
    # ``billboard_rot @ schematic_anchor_offset``. The coordinate convention
    # matches ``billboard_rot``: schematic-local +X → screen RIGHT, +Y → screen
    # UP, +Z → toward the viewer. The default ``(0, 0.9, 0)`` lifts the
    # schematic by 0.9 world-units in screen UP so it clears the validate /
    # cancel icons (which sit at the icon-row anchor with scale 0.2).
    schematic_anchor_offset: Vector = Vector((0.0, 0.9, 0.0))

    # Fixed rotation applied to the schematic frame *before* billboarding,
    # so the schematic appears at the same tilt regardless of camera angle.
    # Default identity ⇒ flat front view. Subclasses can set a small
    # rotation (e.g. ~25° around Y) to expose the depth axis, so dimensions
    # along schematic-local Z have a visible on-screen extent. Useful when
    # one of the bound properties is a depth/thickness whose true geometric
    # direction is otherwise invisible from a flat front-facing schematic.
    schematic_view_rotation: "Matrix" = Matrix.Identity(4)

    # Per-concrete-subclass draw-handler singleton. Python writes via
    # ``cls._draw_handler_installed = ...`` land on the concrete class
    # (not on this base), so two consumer subclasses do not collide.
    _draw_handler_installed: object | None = None

    # Per-concrete-subclass cache of (schematic_cache_key → list[(Vector,
    # Vector, tag)]) — schematic-local edge endpoints + feature tag,
    # pre-computed once per distinct geometry shape (typically per
    # ``railing_type``-like enum). The draw handler transforms the cached
    # local coords with the current frame's billboard + view rotation
    # rather than re-running the bmesh build pipeline; this is the
    # standard Blender practice of keeping allocations out of draw
    # callbacks. The cache is lazily initialised per subclass via
    # ``_get_schematic_geometry_cache`` so concurrent consumers don't
    # share entries.
    _schematic_geometry_cache: dict | None = None

    # Maps a dimension's ``attr_name`` (e.g. "railing_diameter") to a
    # feature tag carried on the schematic mesh's edges (e.g. "rail_tube").
    # When the user hovers a dimension whose ``attr_name`` is in this map,
    # all edges tagged with the corresponding feature are drawn in
    # ``SCHEMATIC_HIGHLIGHT_COLOR`` so the geometric part being measured
    # is visually called out. Subclasses opt in by populating this dict;
    # the default empty dict gives no highlight (graceful no-op).
    schematic_attr_to_feature: dict[str, str] = {}

    # Per-concrete-subclass cache of the feature tag currently hovered.
    # Written by ``_update_hovered_feature`` (instance-side, runs in
    # ``draw_prepare``) and read by the class-level draw handler. ``None``
    # means "no dimension hovered" (default-coloured pass only).
    _hovered_feature: str | None = None

    # Name of the bmesh edge string layer used to tag edges with a feature
    # name. Builders write ``edge[layer] = b"rail_tube"``; the cache reads
    # the same layer back on extraction. The string layer is preferred
    # over an int layer + lookup table because each builder declares its
    # tags in plain Python and the extraction path is symmetric.
    SCHEMATIC_FEATURE_LAYER_NAME: str = "schematic_feature"

    # ── Abstract hooks ────────────────────────────────────────────────────

    @classmethod
    def build_schematic_mesh(cls, props) -> "bmesh.types.BMesh":
        """Return a transient bmesh of the mini preview in schematic-local coordinates.

        Subclasses MUST implement. The returned bmesh's edges are extracted
        into a cached list of local-coord ``(Vector, Vector)`` pairs by
        ``_get_schematic_local_edges`` and the bmesh is freed immediately
        afterward. The draw handler then transforms the cached pairs per
        frame — so the bmesh is built once per distinct
        ``schematic_cache_key`` value, not once per draw call.
        """
        raise NotImplementedError(f"{cls.__name__} must implement build_schematic_mesh(props) -> bmesh.BMesh")

    @classmethod
    def schematic_cache_key(cls, props):
        """Hashable key identifying the schematic's geometry shape, or ``None`` to disable caching.

        Subclasses whose schematic depends only on a small set of discrete
        (e.g. enum-like) props should return a tuple of those — the bmesh
        then rebuilds only when the key changes. Returning ``None`` rebuilds
        on every draw, appropriate for schematics whose proportions vary
        continuously with the bound properties.

        The cached form lives in ``_schematic_geometry_cache`` and is
        camera-independent: only schematic-local edge endpoints are stored,
        so the cache survives camera moves and only invalidates on key
        change.
        """
        return None

    # ── Optional hooks ────────────────────────────────────────────────────

    def schematic_should_show(self, props) -> bool:
        """Whether the schematic preview and sliders should be visible this frame.

        Default: tied to ``props.is_editing``. Subclasses can override to
        add additional gating (e.g. hide when a sibling edit mode is open).
        """
        return bool(getattr(props, "is_editing", False))

    # ── Lifecycle (overrides ``BaseParametricGizmoGroup``) ────────────────

    def setup(self, context: bpy.types.Context) -> None:
        self.setup_editing_gizmos(context)
        self.setup_schematic_dimensions(context)
        self.setup_element_specific_gizmos(context)

    def refresh(self, context: bpy.types.Context) -> None:
        if not self.is_setup_complete():
            return
        obj = context.active_object
        if not obj:
            return
        props = self.get_props(obj)
        mw = obj.matrix_world
        self._prime_frame_caches(context, mw)
        self.update_editing_gizmos(context, mw, props)
        self.update_schematic_dimensions(context, mw, props)
        self._reconcile_draw_handler(props)
        self._refresh_element_specific(context, mw, props)
        self._update_hovered_feature()

    def draw_prepare(self, context: bpy.types.Context) -> None:
        if not self.is_setup_complete():
            return
        if apply_transform_modal_draw_gate(self, context):
            return
        obj = context.active_object
        if not obj:
            return
        props = self.get_props(obj)
        mw = obj.matrix_world
        self._prime_frame_caches(context, mw)
        self.update_editing_gizmos(context, mw, props)
        self.update_schematic_dimensions(context, mw, props)
        self._reconcile_draw_handler(props)
        self._refresh_element_specific(context, mw, props)
        self._update_hovered_feature()

    def _update_hovered_feature(self) -> None:
        """Record which feature tag the user is currently hovering on.

        Walks the group's gizmos for the first ``is_highlight=True``
        dimension whose ``schematic_attr_name`` maps into
        ``schematic_attr_to_feature``, and writes the corresponding tag
        onto the concrete class (so the class-level draw handler can
        pick it up). ``None`` is written when nothing eligible is
        hovered. Cheap walk — runs once per frame, no allocations.
        """
        cls = type(self)
        attr_to_feature = cls.schematic_attr_to_feature
        if not attr_to_feature:
            cls._hovered_feature = None
            return
        for gz in self.gizmos:
            if not getattr(gz, "is_highlight", False):
                continue
            attr_name = getattr(gz, "schematic_attr_name", None)
            if attr_name is None:
                continue
            feature = attr_to_feature.get(attr_name)
            if feature is not None:
                cls._hovered_feature = feature
                return
        cls._hovered_feature = None

    # ── Dimension wiring (schematic-anchored ``BIM_GT_gizmo_dimension`` lines) ──

    # Fixed visual length (as a fraction of ``schematic_box_size``) for every
    # Schematic dimension bars render as constant-width labelled tags; the
    # value reads from the text label, not bar length. Decouples readability
    # from value magnitude — a 5mm thickness and a 5m height are equally
    # clickable. Drag distance still maps 1:1 to the property's world units.
    SCHEMATIC_DIM_VISIBLE_LENGTH_RATIO: float = 0.6

    def setup_schematic_dimensions(self, context: bpy.types.Context) -> None:
        """Create one ``BIM_GT_gizmo_dimension`` per ``DimensionGizmoConfig``."""
        prefs = tool.Blender.get_addon_preferences()
        highlight_color = prefs.decorator_color_selected[:3]

        for config in self.schematic_dimension_props:
            gizmo = self.gizmos.new("BIM_GT_gizmo_dimension")
            gizmo.move_get_cb = self._make_dimension_getter(config)
            gizmo.move_set_cb = self._make_dimension_setter(config)
            # Non-zero initial axis; per-frame refresh overwrites with the
            # billboarded direction.
            gizmo.axis = Vector(config.axis)
            # No ``local_axis``: schematic drags must follow the billboarded
            # bar (screen-up for a vertical bar), not the object-local axis.
            gizmo.invert_delta = config.invert_delta
            gizmo.delta_scale = config.delta_scale
            gizmo.prop_name = config.prop_name
            gizmo.gizmo_group = self
            gizmo.text_formatter = config.text_formatter
            gizmo.color = self.get_color_from_name(config.color)
            gizmo.color_highlight = highlight_color
            gizmo.alpha = 1.0
            gizmo.use_draw_modal = True
            gizmo.use_draw_scale = False
            gizmo.text_offset_sign = config.text_offset_sign
            gizmo.text_alignment = config.text_alignment
            gizmo.show_start_arrow = config.show_start_arrow
            gizmo.show_end_arrow = config.show_end_arrow
            gizmo.schematic_attr_name = config.attr_name
            setattr(self, f"schematic_dim_{config.attr_name}_gizmo", gizmo)

    def update_schematic_dimensions(self, context: bpy.types.Context, mw: Matrix, props) -> None:
        """Position and size each schematic-anchored dimension gizmo."""
        billboard_rot = self._frame_billboard_rot
        view_rotation = self.schematic_view_rotation
        anchor = self._compute_schematic_anchor(props, mw, billboard_rot)
        should_show = self.schematic_should_show(props)
        default_length = self.schematic_box_size * self.SCHEMATIC_DIM_VISIBLE_LENGTH_RATIO

        for config in self.schematic_dimension_props:
            gizmo = getattr(self, f"schematic_dim_{config.attr_name}_gizmo", None)
            if gizmo is None:
                continue

            if not should_show:
                gizmo.hide = True
                continue
            if config.visibility_condition is not None and not config.visibility_condition(props):
                gizmo.hide = True
                continue
            if self.is_gizmo_hidden_by_modal(gizmo):
                gizmo.hide = True
                continue
            gizmo.hide = False

            # Freeze geometry transforms while a modal is active so an
            # orbit-during-drag can't shift the drag direction under the
            # user's hand.
            if getattr(gizmo, "is_modal", False):
                continue

            local_offset = Vector()
            if config.matrix_position is not None:
                local_offset = Vector(config.matrix_position(props))
            gizmo.matrix_basis = self._schematic_world_matrix(
                anchor, billboard_rot, config.axis, local_offset, view_rotation
            )

            # Drag axis = visual bar direction; keep aligned with the on-screen
            # bar even when it points partly into screen depth.
            gizmo.axis = (billboard_rot @ view_rotation @ Vector(config.axis)).normalized()

            visible_length = (
                config.schematic_visible_length if config.schematic_visible_length is not None else default_length
            )
            gizmo.set_dimension_length(visible_length)
            gizmo.show_start_arrow = config.show_start_arrow
            gizmo.show_end_arrow = config.show_end_arrow

    # ── Schematic anchor + draw handler lifecycle ─────────────────────────

    def _compute_schematic_anchor(self, props, mw: Matrix, billboard_rot: Matrix) -> Vector:
        """World-space anchor of the schematic decoration box (instance entry point)."""
        return self.compute_schematic_anchor(
            mw,
            self.get_element_height(props),
            self.ICON_VALIDATE_X,
            self.ICON_Z_OFFSET,
            billboard_rot,
            self.schematic_anchor_offset,
        )

    @staticmethod
    def compute_schematic_anchor(
        mw: Matrix,
        element_height: float,
        icon_x: float,
        icon_z_offset: float,
        billboard_rot: Matrix,
        schematic_offset: Vector,
    ) -> Vector:
        """Schematic-anchor world position: icon-row origin + the schematic
        offset rotated into the screen frame.

        The anchor itself stays billboard-aligned regardless of
        ``schematic_view_rotation``; tilts are applied to the contents
        downstream so the anchored frame stays stable on screen."""
        icon_world = mw @ Vector((icon_x, 0.0, element_height + icon_z_offset))
        return icon_world + billboard_rot @ Vector(schematic_offset)

    @staticmethod
    def _schematic_world_matrix(
        anchor: Vector,
        billboard_rot: Matrix,
        axis: tuple[float, float, float],
        local_position: tuple[float, float, float] | Vector,
        view_rotation: Matrix | None = None,
    ) -> Matrix:
        """``matrix_basis`` for a schematic-anchored gizmo.

        Translates to ``anchor + billboard_rot @ view_rotation @ local_position``
        and rotates +X to the schematic-local ``axis``."""
        if view_rotation is None:
            view_rotation = Matrix.Identity(4)
        local_offset = view_rotation @ Vector(local_position)
        world_pos = anchor + billboard_rot @ local_offset
        axis_world = (billboard_rot @ view_rotation @ Vector(axis)).normalized()
        x_to_axis = Vector((1, 0, 0)).rotation_difference(axis_world).to_matrix().to_4x4()
        return Matrix.Translation(world_pos) @ x_to_axis

    def _reconcile_draw_handler(self, props) -> None:
        """Install or remove the GPU draw handler to match ``schematic_should_show``."""
        if self.schematic_should_show(props):
            self._install_draw_handler()
        else:
            self._uninstall_draw_handler()

    @classmethod
    def _get_schematic_geometry_cache(cls) -> dict:
        """Return the per-concrete-subclass schematic-geometry cache, creating it on first access.

        Subclass attribute writes via ``cls._schematic_geometry_cache = ...``
        land on the concrete class (not on this base), so two consumer
        subclasses keep independent caches. The lazy ``__dict__`` check
        ensures each subclass starts with its own empty dict rather than
        inheriting (and mutating) the base's.
        """
        if "_schematic_geometry_cache" not in cls.__dict__ or cls._schematic_geometry_cache is None:
            cls._schematic_geometry_cache = {}
        return cls._schematic_geometry_cache

    @classmethod
    def _get_schematic_local_edges(cls, props) -> "list[tuple[Vector, Vector, str | None]]":
        """Return the schematic's edges as schematic-local ``(v0, v1, tag)`` triples.

        ``tag`` is the feature tag stored on the bmesh edge string layer
        named by ``SCHEMATIC_FEATURE_LAYER_NAME`` (empty bytes → ``None``).
        Builders that don't tag any edges produce all-``None`` tags; the
        draw handler then takes the default-only path.

        Hits the per-subclass cache when ``schematic_cache_key(props)`` is
        not ``None`` — the bmesh is built only on cache miss. The cached
        list contains only local coordinates + tag strings, so it stays
        valid across camera moves; the draw handler applies per-frame
        transforms (anchor, billboard rotation, view rotation) at render
        time.

        Keeping the bmesh allocation off the draw path is the standard
        Blender practice — see the ``ProfileDecorator`` pattern, which
        likewise caches its shader and rebuilds geometry only on
        state-change rather than per draw call.
        """
        key = cls.schematic_cache_key(props)
        cache = cls._get_schematic_geometry_cache()
        if key is not None and key in cache:
            return cache[key]
        bm = cls.build_schematic_mesh(props)
        try:
            feat_layer = bm.edges.layers.string.get(cls.SCHEMATIC_FEATURE_LAYER_NAME)
            edges: list[tuple[Vector, Vector, str | None]] = []
            for e in bm.edges:
                v0 = Vector(e.verts[0].co)
                v1 = Vector(e.verts[1].co)
                if feat_layer is None:
                    tag: str | None = None
                else:
                    raw = e[feat_layer]
                    tag = raw.decode("utf-8") if raw else None
                edges.append((v0, v1, tag))
        finally:
            bm.free()
        if key is not None:
            cache[key] = edges
        return edges

    @classmethod
    def _install_draw_handler(cls) -> None:
        """Register a class-level ``POST_VIEW`` handler on ``SpaceView3D``.

        Idempotent. The class attribute write lands on the concrete subclass
        (not on this base), so two schematic consumers (railing, roof, …)
        keep independent handles.
        """
        if cls._draw_handler_installed is not None:
            return
        cls._draw_handler_installed = bpy.types.SpaceView3D.draw_handler_add(
            cls._schematic_draw_callback, (cls,), "WINDOW", "POST_VIEW"
        )

    @classmethod
    def _uninstall_draw_handler(cls) -> None:
        """Remove the schematic draw handler if installed. Idempotent."""
        if cls._draw_handler_installed is None:
            return
        bpy.types.SpaceView3D.draw_handler_remove(cls._draw_handler_installed, "WINDOW")
        cls._draw_handler_installed = None

    @classmethod
    def _props_for_active(cls):
        """``(obj, props)`` for the active+selected object, or ``(None, None)``."""
        obj = tool.Blender.get_active_object(is_selected=True)
        if obj is None or not cls.props_getter:
            return None, None
        props = cls.props_getter(obj)
        return obj, props

    @classmethod
    def _schematic_draw_callback(cls, owner_cls) -> None:
        """GPU callback that renders the schematic mesh as wireframe.

        Self-uninstalls when the active object has no editable schematic props.
        Per-frame: rebuilds the bmesh from props, transforms verts into the
        schematic frame, batches as line segments via ``POLYLINE_UNIFORM_COLOR``.
        """
        obj, props = owner_cls._props_for_active()
        if obj is None or props is None or not owner_cls.schematic_should_show_class(props):
            owner_cls._uninstall_draw_handler()
            return

        context = bpy.context
        region = getattr(context, "region", None)
        rv3d = getattr(context, "region_data", None)
        if region is None or rv3d is None:
            return

        try:
            local_edges = owner_cls._get_schematic_local_edges(props)
        except Exception:
            # A subclass build that raises would otherwise crash the viewport
            # on every redraw. Drop the handler so the user sees a missing
            # schematic instead of a broken Blender; the next refresh will
            # try again if conditions allow.
            owner_cls._uninstall_draw_handler()
            return

        if not local_edges:
            return

        mw = obj.matrix_world
        billboard_rot = get_billboard_rotation(context)
        anchor = owner_cls.compute_schematic_anchor(
            mw,
            owner_cls._get_element_height_class(props),
            owner_cls.ICON_VALIDATE_X,
            owner_cls.ICON_Z_OFFSET,
            billboard_rot,
            owner_cls.schematic_anchor_offset,
        )

        view_rotation = owner_cls.schematic_view_rotation
        hovered = getattr(owner_cls, "_hovered_feature", None)
        default_segments: list[tuple[float, float, float]] = []
        highlight_segments: list[tuple[float, float, float]] = []
        for v0_local, v1_local, tag in local_edges:
            a = tuple(anchor + billboard_rot @ view_rotation @ v0_local)
            b = tuple(anchor + billboard_rot @ view_rotation @ v1_local)
            if hovered is not None and tag == hovered:
                highlight_segments.append(a)
                highlight_segments.append(b)
            else:
                default_segments.append(a)
                default_segments.append(b)

        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        shader.bind()
        shader.uniform_float("lineWidth", owner_cls.SCHEMATIC_LINE_WIDTH)
        shader.uniform_float("viewportSize", (region.width, region.height))
        if default_segments:
            shader.uniform_float("color", owner_cls.SCHEMATIC_LINE_COLOR)
            batch_for_shader(shader, "LINES", {"pos": default_segments}).draw(shader)
        if highlight_segments:
            shader.uniform_float("color", owner_cls.SCHEMATIC_HIGHLIGHT_COLOR)
            batch_for_shader(shader, "LINES", {"pos": highlight_segments}).draw(shader)

    @classmethod
    def schematic_should_show_class(cls, props) -> bool:
        """Class-level visibility gate. Mirror any override of the instance form."""
        return bool(getattr(props, "is_editing", False))

    @classmethod
    def _get_element_height_class(cls, props) -> float:
        return getattr(props, "overall_height", getattr(props, "height", 1.0))

    # ── Visual constants ─────────────────────────────────────────────────

    SCHEMATIC_LINE_COLOR: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.85)
    # Warm amber, opaque, distinguishable against the default white line
    # colour and against most Blender themes. Used to overdraw the subset
    # of edges tagged with the hovered dimension's feature.
    SCHEMATIC_HIGHLIGHT_COLOR: tuple[float, float, float, float] = (1.0, 0.7, 0.2, 0.95)
    SCHEMATIC_LINE_WIDTH: float = 1.5


class BaseIconActionGroup(BillboardingGizmoGroupMixin):
    """Base for gizmo groups that emit clickable icon-action gizmos.

    Action gizmos invoke an operator on click and have no associated state —
    copy Z rotation, snap to host, align to grid, etc. Each subclass declares
    ``action_configs: list[IconActionConfig]`` and one icon is emitted per
    config, stacked horizontally and billboarded above the active object's
    bounding box.

    Override ``is_eligible_object`` to gate when the group polls in. The
    default eligibility is "active object is an IFC element"; subclasses
    typically also require a selection cardinality.

    The pen / validate / cancel icon row from ``BaseParametricGizmoGroup``
    polls when **exactly one** object is selected, so action gizmos that
    require ``len >= 2`` are mutually exclusive with parametric editing —
    there is no icon-row overlap in practice.
    """

    action_configs: ClassVar[list[IconActionConfig]] = []

    # Layout constants. Icons appear above the active object's bounding box,
    # billboarded toward the camera. Tweak per-subclass if a feature needs a
    # different anchor. ICON_SCALE matches the validate/cancel cycle scale
    # used by BaseParametricGizmoGroup at ICON_VALIDATE_X (0.375 ≈ 75% of
    # the default gizmo size) so the action icons sit at the same visual
    # weight as the parametric-edit icon row.
    ICON_ROW_Z_OFFSET = 0.5
    ICON_SPACING_X = 0.4
    ICON_SCALE = 0.375

    @classmethod
    def is_eligible_object(cls, obj: bpy.types.Object) -> bool:
        """Subclass override. Default: any IFC element.

        Subclasses commonly add selection-count or IFC-class filters."""
        return tool.Ifc.get_entity(obj) is not None

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        obj = tool.Blender.get_active_object(is_selected=True)
        if obj is None:
            return False
        if not tool.Blender.are_viewport_gizmos_enabled():
            return False
        if _is_transform_modal_active(context):
            return False
        return cls.is_eligible_object(obj)

    def setup(self, context: bpy.types.Context) -> None:
        prefs = tool.Blender.get_addon_preferences()
        default_color = tuple(prefs.decorations_colour[:3])
        highlight_color = tuple(prefs.decorator_color_selected[:3])
        for config in self.action_configs:
            gizmo = self.setup_icon_gizmo(config.icon, default_color, highlight_color, config.operator)
            setattr(self, f"action_{config.name}_gizmo", gizmo)

    def get_icon_anchor(self, context: bpy.types.Context) -> Vector | None:
        obj = context.active_object
        if obj is None:
            return None
        z_top = max((c[2] for c in obj.bound_box), default=0.0)
        return obj.matrix_world @ Vector((0.0, 0.0, z_top + self.ICON_ROW_Z_OFFSET))

    def position_gizmos(self, context: bpy.types.Context) -> None:
        obj = context.active_object
        if obj is None:
            return
        anchor = self.get_icon_anchor(context)
        if anchor is None:
            return
        billboard_rot = get_billboard_rotation(context)
        # World-X spacing keeps a billboarded icon row coherent regardless
        # of anchor object rotation.
        for i, config in enumerate(self.action_configs):
            gizmo = getattr(self, f"action_{config.name}_gizmo", None)
            if gizmo is None:
                continue
            if config.visibility_condition is not None and not config.visibility_condition(obj):
                gizmo.hide = True
                continue
            gizmo.hide = False
            pos = anchor + Vector((i * self.ICON_SPACING_X, 0.0, 0.0))
            gizmo.matrix_basis = billboarded_at(pos, billboard_rot, scale=self.ICON_SCALE)
