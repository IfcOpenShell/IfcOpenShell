# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""Geometry helpers for routing distribution elements (ducts, pipes, cables).

This is deliberately standalone (no IFC reads, no authoring side effects) so
it is easy to unit test and reuse from either a Bonsai operator or a script,
per https://github.com/IfcOpenShell/IfcOpenShell/issues/6100.
"""

Point = tuple[float, float, float]

_EPSILON = 1e-6
_AXIS_NAMES = ("X", "Y", "Z")


def _axis_and_sign(direction: Point) -> tuple[int, int]:
    """Resolve a direction vector to a single axis index and its sign.

    Only axis-aligned directions are supported, matching orthogonal routing
    where a connection point only faces along +/-X, +/-Y or +/-Z.
    """
    nonzero = [i for i, v in enumerate(direction) if abs(v) > _EPSILON]
    if len(nonzero) != 1:
        raise ValueError(f"direction {direction!r} is not axis-aligned (expected exactly one non-zero component)")
    axis = nonzero[0]
    return axis, (1 if direction[axis] > 0 else -1)


def calculate_orthogonal_path(
    start: Point,
    end: Point,
    start_direction: Point | None = None,
    end_direction: Point | None = None,
) -> list[Point]:
    """Calculate an axis-aligned (Manhattan) path between two points.

    `start_direction` and `end_direction` are optional axis-aligned vectors
    constraining which way the path must leave `start` and which way it must
    be travelling when it arrives at `end`, e.g. the outward flow direction
    of a duct or pipe connection port. When omitted, axes are traversed in
    a fixed X, then Y, then Z order.

    Returns the ordered list of waypoints, including `start` and `end`. Two
    consecutive waypoints always share two of their three coordinates, so
    consecutive segments are always axis-aligned. A coincident start and end
    returns a single point. A `ValueError` is raised if a direction
    constraint cannot be satisfied by a direct orthogonal path (for example,
    it requires travel along an axis the two points already share, or
    against the only available direction on that axis), since resolving that
    needs a minimum run length that this function does not have.
    """
    delta = (end[0] - start[0], end[1] - start[1], end[2] - start[2])
    active_axes = [i for i in range(3) if abs(delta[i]) > _EPSILON]

    if not active_axes:
        return [tuple(start)]

    def _require_axis(direction: Point, role: str) -> int:
        axis, sign = _axis_and_sign(direction)
        if axis not in active_axes:
            raise ValueError(
                f"{role} direction is along {_AXIS_NAMES[axis]}, but start and end "
                f"already share that coordinate, so it cannot be honoured without a detour"
            )
        if sign != (1 if delta[axis] > 0 else -1):
            raise ValueError(
                f"{role} direction points away from the target along {_AXIS_NAMES[axis]}, "
                f"so it cannot be honoured without a detour"
            )
        return axis

    first_axis = _require_axis(start_direction, "start") if start_direction is not None else None
    last_axis = _require_axis(end_direction, "end") if end_direction is not None else None

    if first_axis is not None and last_axis is not None and first_axis == last_axis and len(active_axes) > 1:
        raise ValueError("start and end directions both resolve to the same axis, which is contradictory here")

    order = [axis for axis in active_axes if axis not in (first_axis, last_axis)]
    order.sort()
    if last_axis is not None:
        order = ([first_axis] if first_axis is not None else []) + order + [last_axis]
    elif first_axis is not None:
        order = [first_axis] + order
    else:
        order = list(active_axes)

    path = [tuple(start)]
    point = list(start)
    for axis in order:
        point[axis] = end[axis]
        path.append(tuple(point))
    # the last waypoint is `end` by construction, but rebuild it explicitly
    # in case of floating point drift across the intermediate assignments.
    path[-1] = tuple(end)
    return path
