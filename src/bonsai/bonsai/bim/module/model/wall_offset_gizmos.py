# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
# This file was generated with the assistance of an AI coding tool.

"""Four wall-offset dimension gizmos (left / right / top / bottom) shared by door and
window edit gizmo groups — both fillings sit in a LAYER2 wall and the offset math is
identical.

The compute side returns a *signed* value on the X axis (negative when the filling
is 180°-flipped onto the wall's opposite face) so the gizmo framework auto-flips
the rendered arrow; the apply side takes ``abs(value)`` because the user-facing
offset is always positive. Z-axis values are unsigned in both directions.

Fillings are assumed to align with the wall's local X axis to within ±90° — the
parametric door/window construction path enforces this, and the X-sign math
falls back to +1 if ``col[0].x`` lands on the ambiguous zero (filling rotated
exactly 90° in the wall plane).

Every public entry point falls back to a safe no-op when the host-wall chain
cannot be resolved: reads return 0.0, writes do nothing, and gizmo anchors
return a filling-relative position. This keeps the gizmos non-crashing when a
filling momentarily loses its host (e.g. mid-edit, partially-loaded files).

``_GEOM_CACHE`` is module-scoped and persists across tests — tests must call
``clear_caches()`` between cases."""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Protocol

from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.drawing.gizmos import DimensionGizmoConfig

if TYPE_CHECKING:
    import bpy


class FillingProps(Protocol):
    """Structural subset of door/window props this module touches."""

    id_data: bpy.types.Object
    overall_width: float
    overall_height: float


# Wall-local frame axis indices. Y (depth) is unused — fillings sit on the wall's centreline.
_AXIS_X = 0
_AXIS_Z = 2


class _HostWallGeom(NamedTuple):
    """Cached host-wall geometry in SI metres, wall-local frame. ``height`` is
    the vertical projection (already accounts for slanted extrusions)."""

    wall_obj: bpy.types.Object
    height: float
    axis_min_x: float
    axis_max_x: float


class _AxisExtent(NamedTuple):
    """``[low, high]`` interval on one wall-local axis; low = near end.

    ``x_sign`` is +1 / -1 for an X-axis filling extent only (carries the
    180° auto-flip); always 1.0 elsewhere."""

    low: float
    high: float
    x_sign: float = 1.0


class _Edge(NamedTuple):
    """Wall edge a gizmo measures to. ``is_max_end=True`` picks right/top, else left/bottom."""

    axis_index: int
    is_max_end: bool


_LEFT = _Edge(axis_index=_AXIS_X, is_max_end=False)
_RIGHT = _Edge(axis_index=_AXIS_X, is_max_end=True)
_BOTTOM = _Edge(axis_index=_AXIS_Z, is_max_end=False)
_TOP = _Edge(axis_index=_AXIS_Z, is_max_end=True)


# Avoids repeating the host-wall chain walk + LAYER2 geometry read per gizmo per frame.
_GEOM_CACHE = tool.Parametric.GenerationKeyedCache()


def clear_caches() -> None:
    _GEOM_CACHE.clear()


def _host_wall_geom(filling_obj: bpy.types.Object) -> _HostWallGeom | None:
    """Cached host-wall geometry for a filling, or ``None`` if any link in
    filling → opening → wall → LAYER2 extrusion → scene-object resolution breaks."""
    return _GEOM_CACHE.get_or_compute(filling_obj.name, lambda: _compute_host_wall_geom(filling_obj))


def _compute_host_wall_geom(filling_obj: bpy.types.Object) -> _HostWallGeom | None:
    element = tool.Ifc.get_entity(filling_obj)
    if not element:
        return None
    host_wall = tool.Spatial.get_host_wall(element)
    if not host_wall:
        return None
    wall_obj = tool.Ifc.get_object(host_wall)
    length_height = tool.Wall.get_length_and_height(host_wall)
    axis_extent = tool.Wall.get_axis_local_extent(host_wall)
    # x_angle is None for non-LAYER2 walls — gates entry; the value itself is unused.
    if not (wall_obj and length_height and axis_extent and tool.Wall.get_x_angle(host_wall) is not None):
        return None
    _, height = length_height
    axis_min_x, axis_max_x = axis_extent
    return _HostWallGeom(wall_obj=wall_obj, height=height, axis_min_x=axis_min_x, axis_max_x=axis_max_x)


def _filling_axis_extent(props: FillingProps, host_wall_obj: bpy.types.Object, axis_index: int) -> _AxisExtent:
    """Filling footprint on the wall's local axis.

    X-axis extent carries the filling's orientation sign (180° flip onto
    the opposite face) in ``x_sign``."""
    filling_in_wall = host_wall_obj.matrix_world.inverted() @ props.id_data.matrix_world
    origin = filling_in_wall.translation[axis_index]
    if axis_index == _AXIS_X:
        # col[0].x is the X-component of the filling's local X axis in the wall-local frame:
        # +1 when filling's +X aligns with wall's +X, -1 after a 180° Z-flip.
        x_sign = 1.0 if filling_in_wall.col[0].x >= 0.0 else -1.0
        signed_width = x_sign * props.overall_width
        return _AxisExtent(origin + min(0.0, signed_width), origin + max(0.0, signed_width), x_sign)
    return _AxisExtent(origin, origin + props.overall_height)


def _wall_axis_extent(geom: _HostWallGeom, axis_index: int) -> _AxisExtent:
    """Wall span on one local axis: X = IFC axis-line endpoints (not mesh bound-box,
    which drifts on trimmed walls); Z = 0 → wall height."""
    if axis_index == _AXIS_X:
        return _AxisExtent(geom.axis_min_x, geom.axis_max_x)
    return _AxisExtent(0.0, geom.height)


def _offset_from_extents(filling: _AxisExtent, wall: _AxisExtent, is_max_end: bool) -> float:
    """Distance from the wall edge to the filling's matching edge on the same axis."""
    if is_max_end:
        return wall.high - filling.high
    return filling.low - wall.low


def _translate_along_wall_axis(
    props: FillingProps, host_wall_obj: bpy.types.Object, delta: float, axis_index: int
) -> None:
    """Shift the filling by ``delta`` SI metres along the wall's local axis. Drag
    operates in the filling's intent frame, not Blender's world frame, so a rotated
    host wall still tracks correctly."""
    if delta == 0.0:
        return
    direction_world = host_wall_obj.matrix_world.to_3x3().col[axis_index].normalized()
    props.id_data.matrix_world.translation = props.id_data.matrix_world.translation + direction_world * delta


def _get_offset(props: FillingProps, edge: _Edge) -> float:
    """SI distance from the wall edge to the filling's matching edge on the same axis."""
    geom = _host_wall_geom(props.id_data)
    if not geom:
        return 0.0
    filling = _filling_axis_extent(props, geom.wall_obj, edge.axis_index)
    wall = _wall_axis_extent(geom, edge.axis_index)
    return _offset_from_extents(filling, wall, edge.is_max_end)


def _set_offset(props: FillingProps, edge: _Edge, value: float) -> None:
    """Translate the filling so its offset to ``edge`` becomes ``max(0, value)`` SI metres.
    Max-end edges (right/top) translate in the opposite direction of near-end edges."""
    geom = _host_wall_geom(props.id_data)
    if not geom:
        return
    current = _get_offset(props, edge)
    target = max(0.0, value)
    delta = (current - target) if edge.is_max_end else (target - current)
    _translate_along_wall_axis(props, geom.wall_obj, delta, edge.axis_index)


def has_host_wall(props: FillingProps) -> bool:
    """True when the filling resolves to a LAYER2 host wall present in the scene."""
    return _host_wall_geom(props.id_data) is not None


def _edge_position(props: FillingProps, edge: _Edge) -> Vector:
    """Gizmo anchor in filling-local space, at the wall edge, pointing toward the filling."""
    geom = _host_wall_geom(props.id_data)
    if not geom:
        if edge.axis_index == _AXIS_X:
            return Vector((0.0, 0.0, props.overall_height / 2))
        return Vector((props.overall_width / 2, 0.0, props.overall_height if edge.is_max_end else 0.0))
    wall = _wall_axis_extent(geom, edge.axis_index)
    edge_value = wall.high if edge.is_max_end else wall.low
    if edge.axis_index == _AXIS_X:
        wall_edge_world = geom.wall_obj.matrix_world @ Vector((edge_value, 0.0, 0.0))
        pos = props.id_data.matrix_world.inverted() @ wall_edge_world
        return Vector((pos.x, 0.0, props.overall_height / 2))
    # LAYER2 wall matrix_world is upright, so wall-local Z and filling-local Z differ
    # only by the filling's Z origin in the wall frame.
    filling_z_in_wall = _filling_axis_extent(props, geom.wall_obj, axis_index=_AXIS_Z).low
    return Vector((props.overall_width / 2, 0.0, edge_value - filling_z_in_wall))


def _compute_value(props: FillingProps, edge: _Edge) -> float:
    """Renderer-side value. X-axis edges return a signed value so the gizmo's
    auto-flip kicks in for fillings on the wall's opposite face; Z-axis returns unsigned."""
    geom = _host_wall_geom(props.id_data)
    if not geom:
        return 0.0
    filling = _filling_axis_extent(props, geom.wall_obj, edge.axis_index)
    wall = _wall_axis_extent(geom, edge.axis_index)
    return filling.x_sign * _offset_from_extents(filling, wall, edge.is_max_end)


def _apply_value(props: FillingProps, edge: _Edge, value: float) -> None:
    """Drag-end commit; X-axis takes ``abs(value)`` since the negative sign in compute
    is a rendering hint only (user-facing offset is always positive)."""
    if edge.axis_index == _AXIS_X:
        _set_offset(props, edge, abs(value))
    else:
        _set_offset(props, edge, value)


# attr_name identifies the gizmo within its group; values flow through
# compute/apply, not via a registered property.
WALL_OFFSET_GIZMO_CONFIGS: list[DimensionGizmoConfig] = [
    DimensionGizmoConfig(
        attr_name="host_wall_offset_left",
        axis=(1, 0, 0),
        visibility_condition=has_host_wall,
        compute_value=lambda p: _compute_value(p, _LEFT),
        apply_value=lambda p, v: _apply_value(p, _LEFT, v),
        matrix_position=lambda p: _edge_position(p, _LEFT),
    ),
    DimensionGizmoConfig(
        attr_name="host_wall_offset_right",
        axis=(-1, 0, 0),
        visibility_condition=has_host_wall,
        compute_value=lambda p: _compute_value(p, _RIGHT),
        apply_value=lambda p, v: _apply_value(p, _RIGHT, v),
        matrix_position=lambda p: _edge_position(p, _RIGHT),
    ),
    DimensionGizmoConfig(
        attr_name="host_wall_offset_bottom",
        axis=(0, 0, 1),
        visibility_condition=has_host_wall,
        compute_value=lambda p: _compute_value(p, _BOTTOM),
        apply_value=lambda p, v: _apply_value(p, _BOTTOM, v),
        matrix_position=lambda p: _edge_position(p, _BOTTOM),
    ),
    DimensionGizmoConfig(
        attr_name="host_wall_offset_top",
        axis=(0, 0, -1),
        visibility_condition=has_host_wall,
        compute_value=lambda p: _compute_value(p, _TOP),
        apply_value=lambda p, v: _apply_value(p, _TOP, v),
        matrix_position=lambda p: _edge_position(p, _TOP),
    ),
]
