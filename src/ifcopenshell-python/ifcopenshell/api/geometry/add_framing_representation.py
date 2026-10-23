# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Ryan Schultz
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

from __future__ import annotations

from dataclasses import dataclass, replace
from math import cos, radians, sin
from typing import Any, Optional, Union

import numpy as np
import shapely

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper
import ifcopenshell.util.framing
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.unit
from ifcopenshell.util.framing import TOLERANCE, FramingError, SpacingScope
from ifcopenshell.util.shape_builder import SequenceOfVectors, ShapeBuilder

_Z = np.array((0.0, 0.0, 1.0))


# A clipping plane: a point on it, and its normal pointing away from the solid.
ClipPlane = tuple[np.ndarray, np.ndarray]


@dataclass(frozen=True)
class FramingExtrusion:
    """A vertical member: the entry's profile extruded up from ``origin``.

    The profile's X axis runs along ``ref_direction`` (along the path, rotated by the
    entry's rotation) and its Y axis out of the guide plane, to the path's left.

    On a sloped path the ends are raked to follow it: the member is extended by
    ``bottom_extension`` / ``top_extension`` and cut by every plane in ``bottom_planes`` /
    ``top_planes``. A member standing where the slope changes is cut by both slopes.
    """

    entry: str
    origin: np.ndarray
    ref_direction: np.ndarray
    depth: float
    bottom_planes: tuple[ClipPlane, ...] = ()
    top_planes: tuple[ClipPlane, ...] = ()
    bottom_extension: float = 0.0
    top_extension: float = 0.0


@dataclass(frozen=True)
class FramingRail:
    """A straight piece of a horizontal member: the entry's profile extruded along ``direction``.

    The profile lies in a plumb plane facing along the path in plan (``profile_normal``):
    its X axis is ``x_axis`` (out of the guide plane, to the path's left, rotated by the
    entry's rotation) and its Y axis is up. On a sloped path the extrusion is oblique, so
    the rail's plumb section is the profile, its ends are plumb and it keeps its height
    above the path.

    Where the member turns a corner in plan, the piece is extended by ``start_extension``
    / ``end_extension`` and cut by a plumb mitre plane through ``start_corner`` /
    ``end_corner``, whose normal points away from the piece. A ``None`` mitre is a plumb
    end, which is also how pieces meet where only the slope changes.

    The corner is on the path rather than on the offset axis: the mitre plane bisects the
    corner, so rails offset out of the guide plane still meet on it.
    """

    entry: str
    origin: np.ndarray  # where the piece's axis starts, before any extension
    direction: np.ndarray  # unit extrusion direction, sloped with the path
    x_axis: np.ndarray
    length: float  # along ``direction``
    start_mitre: Optional[np.ndarray] = None
    end_mitre: Optional[np.ndarray] = None
    start_extension: float = 0.0
    end_extension: float = 0.0
    start_corner: Optional[np.ndarray] = None
    end_corner: Optional[np.ndarray] = None
    profile_normal: Optional[np.ndarray] = None  # the path's plan direction

    @property
    def plane_normal(self) -> np.ndarray:
        return self.direction if self.profile_normal is None else self.profile_normal


@dataclass(frozen=True)
class FramingPanel:
    """An infill panel in the guide plane, ``thickness`` thick.

    ``width`` is measured in plan and ``height`` plumb. On a sloped path the panel is a
    parallelogram: plumb sides, with its bottom and top rising ``slope`` per unit width.
    """

    entry: str
    origin: np.ndarray  # bottom left corner, on the panel's centre plane
    direction: np.ndarray  # along the path, in plan
    normal: np.ndarray  # out of the guide plane, to the path's left
    width: float
    height: float
    thickness: float
    slope: float = 0.0

    def outline(self) -> np.ndarray:
        """The panel's corners in its own plane: x along the path, y up."""
        w, h, rise = self.width, self.height, self.width * self.slope
        return np.array(((0.0, 0.0), (w, rise), (w, rise + h), (0.0, h)))


FramingItem = Union[FramingExtrusion, FramingRail, FramingPanel]


@dataclass
class FramingMesh:
    """A closed triangle-and-quad mesh of framing items, for viewport previews."""

    vertices: np.ndarray  # shape (N, 3)
    faces: list[tuple[int, ...]]
    face_entries: list[str]  # the entry each face belongs to


class _GuideMap:
    """Maps the solver's ``(u, v)`` onto a polyline guide path in 3D."""

    def __init__(self, points: SequenceOfVectors, closed: bool):
        pts = np.array(points, dtype=float)
        if pts.ndim != 2 or len(pts) < 2:
            raise FramingError("The guide path needs at least two points.")
        if pts.shape[1] == 2:
            pts = np.hstack((pts, np.zeros((len(pts), 1))))
        if closed:
            pts = np.vstack((pts, pts[:1]))
        self.closed = closed
        self.points = pts
        # u is measured in plan, so spacing and member widths are horizontal, as
        # baluster spacing rules are. Members stay plumb, and v is measured plumb.
        steps = np.diff(pts, axis=0)
        self.lengths = np.linalg.norm(steps[:, :2], axis=1)
        self.rises = steps[:, 2]
        self.starts = np.concatenate(([0.0], np.cumsum(self.lengths)[:-1]))
        self.length = float(self.lengths.sum())

    def segment_at(self, u: float) -> int:
        for i, length in enumerate(self.lengths):
            if u < self.starts[i] + length - TOLERANCE:
                return i
        return len(self.lengths) - 1

    def point_at(self, u: float, segment: Optional[int] = None) -> np.ndarray:
        i = self.segment_at(u) if segment is None else segment
        t = (u - self.starts[i]) / self.lengths[i]
        return self.points[i] + (self.points[i + 1] - self.points[i]) * t

    def direction(self, segment: int) -> np.ndarray:
        """The segment's direction in plan. Members stay plumb, so only plan matters."""
        d = self.points[segment + 1] - self.points[segment]
        d = np.array((d[0], d[1], 0.0))
        length = np.linalg.norm(d)
        if length <= TOLERANCE:
            raise FramingError(f"Guide path segment {segment} is vertical.")
        return d / length

    def slope(self, segment: int) -> float:
        """Rise per unit of plan length."""
        return float(self.rises[segment] / self.lengths[segment]) if self.lengths[segment] > TOLERANCE else 0.0

    def segments_at(self, u: float) -> list[int]:
        """The segment at ``u``, or both segments when ``u`` is on a path vertex."""
        result = [
            i
            for i, (start, length) in enumerate(zip(self.starts, self.lengths))
            if start - TOLERANCE <= u <= start + length + TOLERANCE
        ]
        if self.closed and (u <= TOLERANCE or u >= self.length - TOLERANCE):
            result = sorted({0, len(self.lengths) - 1})
        return result

    def normal(self, segment: int) -> np.ndarray:
        return np.cross(_Z, self.direction(segment))

    def pieces(self, u_start: float, u_end: float) -> list[tuple[int, float, float]]:
        """Split ``[u_start, u_end]`` at path vertices into ``(segment, u_start, u_end)`` pieces."""
        result = []
        last = len(self.lengths) - 1
        for i, (start, length) in enumerate(zip(self.starts, self.lengths)):
            # A run may overhang the ends of an open path, e.g. a top rail covering its end
            # posts, so the first and last segments carry on past them.
            low = -np.inf if i == 0 and not self.closed else start
            high = np.inf if i == last and not self.closed else start + length
            a, b = max(u_start, low), min(u_end, high)
            if b - a > TOLERANCE:
                result.append((i, float(a), float(b)))
        return result


def _rotate_2d(points: np.ndarray, angle: float) -> np.ndarray:
    c, s = cos(angle), sin(angle)
    return points @ np.array(((c, s), (-s, c)))


def get_profile_points(profile: ifcopenshell.entity_instance, unit_scale: float) -> np.ndarray:
    """2D vertices of a tessellated profile, in project units, for measuring its extents."""
    settings = ifcopenshell.geom.settings()
    settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
    shape = ifcopenshell.geom.create_shape(settings, profile)
    vertices = ifcopenshell.util.shape.get_vertices(shape)
    if vertices.size == 0:
        raise FramingError(f"Profile {profile.ProfileName!r} has no geometry.")
    return vertices[:, :2] / unit_scale


def get_profile_mesh(profile: ifcopenshell.entity_instance, unit_scale: float) -> tuple[np.ndarray, np.ndarray]:
    """A profile's triangulated area, in project units: 2D points and counter-clockwise triangles."""
    settings = ifcopenshell.geom.settings()
    settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
    shape = ifcopenshell.geom.create_shape(settings, profile)
    vertices = ifcopenshell.util.shape.get_vertices(shape)[:, :2] / unit_scale
    edges = np.asarray(ifcopenshell.util.shape.get_edges(shape)).reshape(-1, 2)
    # The kernel returns faces for some profiles (circles, hollow sections) but only the
    # outline for others (rectangles, I-shapes), so the area is always rebuilt from the
    # outline. build_area nests the loops, so holes stay holes.
    area = shapely.build_area(shapely.MultiLineString([vertices[[a, b]] for a, b in edges.tolist()]))
    triangles_2d = shapely.get_parts(shapely.constrained_delaunay_triangles(area)) if not area.is_empty else []
    if not len(triangles_2d):
        raise FramingError(f"Profile {profile.ProfileName!r} has no area.")
    corners = np.array([np.asarray(t.exterior.coords)[:3] for t in triangles_2d])
    # Weld coincident points, so edges shared by two triangles can be recognised.
    _, index, inverse = np.unique(np.round(corners.reshape(-1, 2), 9), axis=0, return_index=True, return_inverse=True)
    points = corners.reshape(-1, 2)[index]
    triangles = inverse.reshape(-1, 3)
    a, b, c = points[triangles[:, 0]], points[triangles[:, 1]], points[triangles[:, 2]]
    area = (b - a)[:, 0] * (c - a)[:, 1] - (b - a)[:, 1] * (c - a)[:, 0]
    triangles = np.where(area[:, None] < 0, triangles[:, ::-1], triangles)
    return points, triangles[np.abs(area) > TOLERANCE**2]


def _boundary_edges(triangles: np.ndarray) -> list[tuple[int, int]]:
    """Edges used by one triangle only, in their triangle's winding (outer loops CCW, holes CW)."""
    directed: dict[tuple[int, int], tuple[int, int]] = {}
    counts: dict[tuple[int, int], int] = {}
    for triangle in triangles.tolist():
        for a, b in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
            key = (min(a, b), max(a, b))
            counts[key] = counts.get(key, 0) + 1
            directed[key] = (a, b)
    return [directed[key] for key, count in counts.items() if count == 1]


def compute_framing_mesh(
    items: list[FramingItem], profile_meshes: dict[str, tuple[np.ndarray, np.ndarray]]
) -> FramingMesh:
    """Turn framing items into one mesh, matching the solids the IFC writer creates.

    Mitres are exact without booleans: a rail's end vertices slide along its axis onto
    the mitre plane.

    :param items: See :func:`compute_framing_geometry`.
    :param profile_meshes: Per vertical or horizontal entry name, see :func:`get_profile_mesh`.
    """
    vertices: list[np.ndarray] = []
    faces: list[tuple[int, ...]] = []
    face_entries: list[str] = []
    count = 0
    edges_by_entry = {name: _boundary_edges(t) for name, (_, t) in profile_meshes.items()}
    rectangle_triangles = np.array(((0, 1, 2), (0, 2, 3)))
    rectangle_edges = _boundary_edges(rectangle_triangles)

    def clip(ring: np.ndarray, planes, z_axis: np.ndarray, is_start: bool) -> np.ndarray:
        """Slide a ring of vertices along the axis onto its clipping planes.

        With several planes, each vertex stops at the first plane it meets coming from
        inside the solid, which is the intersection of the kept half-spaces."""
        if not planes:
            return ring
        ts = np.array([-((ring - point) @ normal) / float(z_axis @ normal) for point, normal in planes])
        t = ts.max(axis=0) if is_start else ts.min(axis=0)
        return ring + np.outer(t, z_axis)

    def add_prism(entry, points, triangles, edges, origin, x_axis, y_axis, z_axis, length, start=(), end=()):
        nonlocal count
        base = origin + np.outer(points[:, 0], x_axis) + np.outer(points[:, 1], y_axis)
        bottom = clip(base, start, z_axis, True)
        top = clip(base + z_axis * length, end, z_axis, False)
        n = len(points)
        vertices.extend((bottom, top))
        new_faces = [tuple(int(count + i) for i in tri[::-1]) for tri in triangles]
        new_faces += [tuple(int(count + n + i) for i in tri) for tri in triangles]
        new_faces += [(count + a, count + b, count + n + b, count + n + a) for a, b in edges]
        faces.extend(new_faces)
        face_entries.extend([entry] * len(new_faces))
        count += 2 * n

    for item in items:
        if isinstance(item, FramingExtrusion):
            points, triangles = profile_meshes[item.entry]
            y_axis = np.cross(_Z, item.ref_direction)
            add_prism(
                item.entry,
                points,
                triangles,
                edges_by_entry[item.entry],
                item.origin - _Z * item.bottom_extension,
                item.ref_direction,
                y_axis,
                _Z,
                item.depth + item.bottom_extension + item.top_extension,
                item.bottom_planes,
                item.top_planes,
            )
        elif isinstance(item, FramingRail):
            points, triangles = profile_meshes[item.entry]
            y_axis = np.cross(item.plane_normal, item.x_axis)
            start = ((item.start_corner, item.start_mitre),) if item.start_mitre is not None else ()
            end = ((item.end_corner, item.end_mitre),) if item.end_mitre is not None else ()
            add_prism(
                item.entry,
                points,
                triangles,
                edges_by_entry[item.entry],
                item.origin - item.direction * item.start_extension,
                item.x_axis,
                y_axis,
                item.direction,
                item.length + item.start_extension + item.end_extension,
                start,
                end,
            )
        else:
            up = np.cross(-item.normal, item.direction)
            origin = item.origin + item.normal * item.thickness / 2
            add_prism(
                item.entry,
                item.outline(),
                rectangle_triangles,
                rectangle_edges,
                origin,
                item.direction,
                up,
                -item.normal,
                item.thickness,
            )
    return FramingMesh(np.vstack(vertices) if vertices else np.zeros((0, 3)), faces, face_entries)


def _member_extent(points: np.ndarray, kind: str, rotation: float) -> tuple[float, float]:
    """A profile's extent across a member's axis: along u for a vertical, along v for a horizontal."""
    rotated = _rotate_2d(points, rotation)
    axis = rotated[:, 0] if kind == "V" else rotated[:, 1]
    return float(axis.min()), float(axis.max())


def _mitre_extension(
    corner: np.ndarray, axis_point: np.ndarray, direction: np.ndarray, mitre: np.ndarray, section: np.ndarray
) -> float:
    """How far a piece must run past ``axis_point`` for its whole section to reach the mitre plane.

    :param section: The profile's points in world space, relative to the piece's axis.
    """
    along = float(direction @ mitre)
    shortfall = float(np.max(-((axis_point - corner) + section) @ mitre))
    # A little extra so the clip always cuts through solid material.
    return max(0.0, shortfall / along) * 1.05 + TOLERANCE


def _rail_pieces(
    entry: str,
    u_start: float,
    u_end: float,
    v: float,
    guide: _GuideMap,
    rotation: float,
    offset: float,
    profile_points: np.ndarray,
) -> list[FramingRail]:
    pieces = guide.pieces(u_start, u_end)
    whole_loop = guide.closed and u_start <= TOLERANCE and u_end >= guide.length - TOLERANCE
    frames = []
    for segment, a, b in pieces:
        plan = guide.direction(segment)
        n = guide.normal(segment)
        x_axis = n * cos(rotation) + _Z * sin(rotation)
        y_axis = np.cross(plan, x_axis)
        section = np.outer(profile_points[:, 0], x_axis) + np.outer(profile_points[:, 1], y_axis)
        stretch = float(np.hypot(1.0, guide.slope(segment)))
        d = (plan + _Z * guide.slope(segment)) / stretch
        frames.append((segment, a, b, d, n, x_axis, section, plan, stretch))

    def mitre_between(i: int, j: int) -> Optional[np.ndarray]:
        # Plumb mitres bisect the corner in plan. Pieces that only change slope meet on
        # their plumb ends without one, as do pieces that double back on themselves.
        m = frames[i][7] + frames[j][7]
        length = np.linalg.norm(m)
        if length <= TOLERANCE or float(frames[i][7] @ frames[j][7]) > 1 - TOLERANCE:
            return None
        return m / length

    result = []
    for k, (segment, a, b, d, n, x_axis, section, plan, stretch) in enumerate(frames):
        start = guide.point_at(a, segment) + _Z * v + n * offset
        end = start + d * (b - a) * stretch
        start_mitre = end_mitre = start_corner = end_corner = None
        start_extension = end_extension = 0.0
        prev_k = k - 1 if k > 0 else (len(frames) - 1 if whole_loop and len(frames) > 1 else None)
        next_k = k + 1 if k < len(frames) - 1 else (0 if whole_loop and len(frames) > 1 else None)
        if prev_k is not None and (m := mitre_between(prev_k, k)) is not None:
            start_mitre = -m
            start_corner = guide.point_at(a, segment) + _Z * v
            start_extension = _mitre_extension(start_corner, start, -d, start_mitre, section)
        if next_k is not None and (m := mitre_between(k, next_k)) is not None:
            end_mitre = m
            end_corner = guide.point_at(b, segment) + _Z * v
            end_extension = _mitre_extension(end_corner, end, d, end_mitre, section)
        result.append(
            FramingRail(
                entry,
                start,
                d,
                x_axis,
                (b - a) * stretch,
                start_mitre,
                end_mitre,
                start_extension,
                end_extension,
                start_corner,
                end_corner,
                plan,
            )
        )
    pairs = [(k, k + 1) for k in range(len(result) - 1)]
    if whole_loop and len(result) > 1:
        pairs.append((len(result) - 1, 0))
    return _ease_corners(result, frames, guide, pairs)


def _ease_corners(
    rails: list[FramingRail], frames: list, guide: _GuideMap, pairs: list[tuple[int, int]]
) -> list[FramingRail]:
    """Join offset rails smoothly where the path turns a corner and changes slope.

    Offset to one side, the two legs reach the rail's own corner at different heights.
    So one leg's slope carries on around the corner until the other leg's line meets
    it: on the outside of a rising turn, a short level return along the outgoing leg;
    on the inside, the climb starts a little before the corner on the incoming leg. The
    plan corner is then a mitre between two pieces of the same slope, and the slope
    change a plumb joint between pieces in line.
    """
    after: dict[int, FramingRail] = {}
    for i, j in pairs:
        incoming, outgoing = rails[i], rails[j]
        if incoming.end_mitre is None or outgoing.start_mitre is None:
            continue
        s_in, s_out = guide.slope(frames[i][0]), guide.slope(frames[j][0])
        if abs(s_in - s_out) <= TOLERANCE:
            continue
        p_in, p_out = frames[i][7], frames[j][7]
        # Where the two offset lines cross in plan: the rail's own corner.
        matrix = np.array(((p_in[0], -p_out[0]), (p_in[1], -p_out[1])))
        if abs(np.linalg.det(matrix)) <= TOLERANCE:
            continue
        t_in, t_out = np.linalg.solve(matrix, (outgoing.origin - incoming.origin)[:2])
        corner = incoming.origin[:2] + p_in[:2] * t_in
        z_in = incoming.origin[2] + s_in * t_in
        z_out = outgoing.origin[2] + s_out * t_out
        rise = z_out - z_in
        if abs(rise) <= TOLERANCE:
            continue
        run = rise / (s_out - s_in)
        if run < 0:
            # The outgoing leg is lower: carry the incoming slope along the outgoing leg.
            run = -run
            outgoing_end = outgoing.origin + outgoing.direction * outgoing.length
            if run >= float((outgoing_end[:2] - corner) @ p_out[:2]) - TOLERANCE:
                continue
            stretch = float(np.hypot(1.0, s_in))
            d = (p_out + _Z * s_in) / stretch
            origin = np.array((corner[0], corner[1], z_in))
            transition = replace(
                outgoing,
                origin=origin,
                direction=d,
                length=run * stretch,
                end_mitre=None,
                end_extension=0.0,
                end_corner=None,
                start_extension=_mitre_extension(outgoing.start_corner, origin, -d, outgoing.start_mitre, frames[j][6]),
            )
            joint = origin + d * run * stretch
            rails[j] = replace(
                outgoing,
                origin=joint,
                length=float((outgoing_end - joint) @ outgoing.direction),
                start_mitre=None,
                start_extension=0.0,
                start_corner=None,
            )
            after[i] = transition
        else:
            # The outgoing leg is higher: start its slope early, along the incoming leg.
            if run >= float((corner - incoming.origin[:2]) @ p_in[:2]) - TOLERANCE:
                continue
            stretch = float(np.hypot(1.0, s_out))
            d = (p_in + _Z * s_out) / stretch
            joint = np.array((corner[0] - p_in[0] * run, corner[1] - p_in[1] * run, z_in - s_in * run))
            end = joint + d * run * stretch
            transition = replace(
                incoming,
                origin=joint,
                direction=d,
                length=run * stretch,
                start_mitre=None,
                start_extension=0.0,
                start_corner=None,
                end_extension=_mitre_extension(incoming.end_corner, end, d, incoming.end_mitre, frames[i][6]),
            )
            rails[i] = replace(
                incoming,
                length=float((joint - incoming.origin) @ incoming.direction),
                end_mitre=None,
                end_extension=0.0,
                end_corner=None,
            )
            after[i] = transition
    result = []
    for k, rail in enumerate(rails):
        result.append(rail)
        if k in after:
            result.append(after[k])
    return result


def _raked_vertical(
    entry: str,
    origin: np.ndarray,
    ref_direction: np.ndarray,
    member: ifcopenshell.util.framing.VerticalMember,
    guide: _GuideMap,
    profile_points: np.ndarray,
    square: bool,
) -> FramingExtrusion:
    """A plumb member whose ends follow the slope of the path where it stands."""
    depth = member.v_end - member.v_start
    slopes = {guide.slope(i): i for i in guide.segments_at(member.u)}
    if square or all(abs(s) <= TOLERANCE for s in slopes):
        return FramingExtrusion(entry, origin, ref_direction, depth)
    y_axis = np.cross(_Z, ref_direction)
    section = np.outer(profile_points[:, 0], ref_direction) + np.outer(profile_points[:, 1], y_axis)
    bottom_planes, top_planes = [], []
    extension = 0.0
    for slope, segment in slopes.items():
        plan = guide.direction(segment)
        up = _Z - plan * slope
        up /= np.linalg.norm(up)
        top_planes.append((origin + _Z * depth, up))
        bottom_planes.append((origin, -up))
        extension = max(extension, float(np.max(np.abs(section @ plan))) * abs(slope))
    # A little extra so the clip always cuts through solid material.
    extension = extension * 1.05 + TOLERANCE
    return FramingExtrusion(
        entry, origin, ref_direction, depth, tuple(bottom_planes), tuple(top_planes), extension, extension
    )


def compute_framing_geometry(
    *,
    system: dict[str, Any],
    guide: SequenceOfVectors,
    height: float,
    profile_points: dict[str, np.ndarray],
    closed: bool = False,
    scope: SpacingScope = "SEGMENT",
) -> list[FramingItem]:
    """Lay out a framing system and place each member and panel in 3D.

    Pure geometry, so it can drive a viewport preview as well as the IFC writer. All
    values are in project units.

    :param system: The framing system's JSON data, with a ``members`` list.
    :param guide: The guide path's points. Members are laid out along it, and ``v`` is
        measured up from it.
    :param height: The occurrence's height, which ``"TOP"`` bounds resolve to.
    :param profile_points: Per vertical or horizontal entry name, the 2D points of its
        profile, see :func:`get_profile_points`.
    :param closed: Whether the guide path loops back to its first point.
    :param scope: See :func:`ifcopenshell.util.framing.solve`.
    :return: Items in the order of the system's entries.
    """
    entries = ifcopenshell.util.framing.parse_system(system)
    data = {m["name"]: m for m in system["members"]}
    guide_map = _GuideMap(guide, closed)

    extents: dict[str, tuple[float, float]] = {}
    lateral: dict[str, tuple[float, float]] = {}
    for entry in entries:
        if isinstance(entry, ifcopenshell.util.framing.InfillEntry):
            continue
        if entry.name not in profile_points:
            raise FramingError(f"Entry {entry.name!r} needs a profile.")
        kind = data[entry.name]["kind"]
        rotation = radians(data[entry.name].get("rotation", 0.0))
        extents[entry.name] = _member_extent(profile_points[entry.name], kind, rotation)
        # Out of the guide plane the axes swap: a vertical's profile Y, a horizontal's X.
        across = _member_extent(profile_points[entry.name], "H" if kind == "V" else "V", rotation)
        offset = float(data[entry.name].get("offset", 0.0))
        lateral[entry.name] = (across[0] + offset, across[1] + offset)

    layout = ifcopenshell.util.framing.solve(
        entries,
        guide_map.lengths.tolist(),
        height,
        closed=closed,
        scope=scope,
        extents=extents,
        lateral=lateral,
    )

    items: list[FramingItem] = []
    for entry in entries:
        entry_data = data[entry.name]
        offset = float(entry_data.get("offset", 0.0))
        rotation = radians(entry_data.get("rotation", 0.0))
        if isinstance(entry, ifcopenshell.util.framing.VerticalEntry):
            for member in layout.verticals:
                if member.entry != entry.name:
                    continue
                segment = member.address[0]
                d, n = guide_map.direction(segment), guide_map.normal(segment)
                origin = guide_map.point_at(member.u) + _Z * member.v_start + n * offset
                ref_direction = d * cos(rotation) + n * sin(rotation)
                items.append(
                    _raked_vertical(
                        entry.name,
                        origin,
                        ref_direction,
                        member,
                        guide_map,
                        profile_points[entry.name],
                        square=bool(entry_data.get("square_cut")),
                    )
                )
        elif isinstance(entry, ifcopenshell.util.framing.HorizontalEntry):
            for member in layout.horizontals:
                if member.entry == entry.name:
                    items.extend(
                        _rail_pieces(
                            entry.name,
                            member.u_start,
                            member.u_end,
                            member.v,
                            guide_map,
                            rotation,
                            offset,
                            profile_points[entry.name],
                        )
                    )
        else:
            thickness = float(entry_data.get("thickness", 0.0))
            if thickness <= TOLERANCE:
                raise FramingError(f"Infill {entry.name!r} needs a thickness.")
            for panel in layout.infills:
                if panel.entry != entry.name:
                    continue
                segment = panel.address[0]
                d, n = guide_map.direction(segment), guide_map.normal(segment)
                origin = guide_map.point_at(panel.u_start, segment) + _Z * panel.v_start + n * offset
                items.append(
                    FramingPanel(
                        entry.name,
                        origin,
                        d,
                        n,
                        panel.u_end - panel.u_start,
                        panel.v_end - panel.v_start,
                        thickness,
                        guide_map.slope(segment),
                    )
                )
    return items


def add_framing_representation(
    file: ifcopenshell.file,
    *,  # keywords only as this API implementation is probably not final
    # IfcGeometricRepresentationContext
    context: ifcopenshell.entity_instance,
    system: dict[str, Any],
    guide: SequenceOfVectors,
    height: float,
    closed: bool = False,
    scope: SpacingScope = "SEGMENT",
    part_of_product: Optional[ifcopenshell.entity_instance] = None,
    constituent_set: Optional[ifcopenshell.entity_instance] = None,
    unit_scale: Optional[float] = None,
) -> ifcopenshell.entity_instance:
    """Create a body representation for a framing system laid along a guide path.

    A framing system is a list of entries (posts, rails, mullions, transoms, infill
    panels) described in :mod:`ifcopenshell.util.framing`. Vertical and horizontal
    entries reference an IfcProfileDef by ``{"id": ..., "name": ...}``. Optional entry
    keys used here are ``rotation`` (degrees, in the profile's plane), ``offset`` (out
    of the guide plane, to the path's left) and, for infill, ``thickness``.

    Vertical members and panels are extrusions. Horizontal members are one extrusion per
    straight piece, mitred where they turn a corner.

    Units are expected to be in IFC project units.

    :param context: IfcGeometricRepresentationContext for the representation.
    :param system: The framing system's JSON data, with a ``members`` list.
    :param guide: The guide path's points, in the element's object coordinates.
    :param height: The occurrence's height, which ``"TOP"`` bounds resolve to.
    :param closed: Whether the guide path loops back to its first point.
    :param scope: ``"SEGMENT"`` restarts vertical spacing at every path vertex,
        ``"PATH"`` spaces along the whole path.
    :param part_of_product: The element's IfcProductDefinitionShape (or a type's
        IfcRepresentationMap). If given, each entry's items are grouped in an
        IfcShapeAspect named after the entry, replacing any previous items of that
        aspect.
    :param constituent_set: The element's IfcMaterialConstituentSet. If given,
        each entry's items are styled with the surface style of the material of
        the constituent named after the entry. The geometry kernel does not
        resolve constituents through shape aspects, so without item styles
        viewers show every entry in one colour.
    :param unit_scale: The unit scale as calculated by
        ifcopenshell.util.unit.calculate_unit_scale. If not provided, it
        will be automatically calculated for you.
    :return: IfcShapeRepresentation for the framing system.
    """
    if unit_scale is None:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

    profiles: dict[str, ifcopenshell.entity_instance] = {}
    unresolved: list[str] = []
    for member in system.get("members", []):
        if member.get("kind") not in ("V", "H"):
            continue
        profile = ifcopenshell.util.framing.resolve_profile(file, member.get("profile"))
        if profile is None:
            unresolved.append(member.get("name", "?"))
        else:
            profiles[member["name"]] = profile
    if unresolved:
        raise FramingError(f"No profile found for: {', '.join(unresolved)}.")

    items = compute_framing_geometry(
        system=system,
        guide=guide,
        height=height,
        profile_points={name: get_profile_points(p, unit_scale) for name, p in profiles.items()},
        closed=closed,
        scope=scope,
    )

    builder = ShapeBuilder(file)
    ifc_items: list[ifcopenshell.entity_instance] = []
    items_by_entry: dict[str, list[ifcopenshell.entity_instance]] = {}
    for item in items:
        if isinstance(item, FramingExtrusion):
            ifc_item = builder.extrude(
                profiles[item.entry],
                item.depth + item.bottom_extension + item.top_extension,
                position=item.origin - _Z * item.bottom_extension,
                position_x_axis=item.ref_direction,
                position_z_axis=_Z,
            )
            ifc_item = _clip(builder, ifc_item, (*item.bottom_planes, *item.top_planes))
        elif isinstance(item, FramingRail):
            ifc_item = _rail_solid(builder, profiles[item.entry], item)
        else:
            ifc_item = _panel_solid(file, item)
        ifc_items.append(ifc_item)
        items_by_entry.setdefault(item.entry, []).append(ifc_item)

    representation = builder.get_representation(context, ifc_items)
    if constituent_set is not None:
        _style_items(file, context, constituent_set, items_by_entry)
    if part_of_product is not None:
        for name, entry_items in items_by_entry.items():
            _set_shape_aspect(file, name, entry_items, representation, part_of_product)
    return representation


def _rail_solid(
    builder: ShapeBuilder, profile: ifcopenshell.entity_instance, rail: FramingRail
) -> ifcopenshell.entity_instance:
    z_axis = rail.plane_normal
    y_axis = np.cross(z_axis, rail.x_axis)
    # In the profile's own frame, an oblique direction for a sloped rail, else (0, 0, 1).
    local_direction = (
        float(rail.direction @ rail.x_axis),
        float(rail.direction @ y_axis),
        float(rail.direction @ z_axis),
    )
    solid = builder.extrude(
        profile,
        rail.length + rail.start_extension + rail.end_extension,
        position=rail.origin - rail.direction * rail.start_extension,
        extrusion_vector=local_direction,
        position_x_axis=rail.x_axis,
        position_z_axis=z_axis,
    )
    planes = [
        (c, m) for c, m in ((rail.start_corner, rail.start_mitre), (rail.end_corner, rail.end_mitre)) if m is not None
    ]
    return _clip(builder, solid, planes)


def _clip(builder: ShapeBuilder, solid: ifcopenshell.entity_instance, planes) -> ifcopenshell.entity_instance:
    """Cut a solid by half-spaces whose normals point away from the kept material."""
    if not planes:
        return solid
    for point, normal in planes:
        # Not ShapeBuilder.plane: its reference axis degenerates for a downward normal.
        reference = np.array((1.0, 0.0, 0.0)) if abs(float(normal @ _Z)) > 0.9 else _Z
        x_axis = np.cross(normal, reference)
        x_axis /= np.linalg.norm(x_axis)
        plane = builder.file.createIfcPlane(builder.create_axis2_placement_3d(point, normal, x_axis))
        half_space = builder.half_space_solid(plane)
        solid = builder.file.createIfcBooleanClippingResult("DIFFERENCE", solid, half_space)
    # Wrapped as a solid model, so it can share a SolidModel representation with plain extrusions.
    return builder.file.createIfcCsgSolid(solid)


def _panel_solid(file: ifcopenshell.file, panel: FramingPanel) -> ifcopenshell.entity_instance:
    # Local X runs along the path and local Y up, which needs the local Z pointing to the
    # path's right. The extrusion then runs from the left face to the right face.
    if abs(panel.slope) > TOLERANCE:
        outline = [file.createIfcCartesianPoint(p) for p in panel.outline().tolist()]
        rectangle = file.createIfcArbitraryClosedProfileDef("AREA", None, file.createIfcPolyline(outline + outline[:1]))
    else:
        rectangle = file.createIfcRectangleProfileDef(
            "AREA",
            None,
            file.createIfcAxis2Placement2D(file.createIfcCartesianPoint((panel.width / 2, panel.height / 2))),
            panel.width,
            panel.height,
        )
    position = file.createIfcAxis2Placement3D(
        file.createIfcCartesianPoint((panel.origin + panel.normal * panel.thickness / 2).tolist()),
        file.createIfcDirection((-panel.normal).tolist()),
        file.createIfcDirection(panel.direction.tolist()),
    )
    return file.createIfcExtrudedAreaSolid(
        rectangle, position, file.createIfcDirection((0.0, 0.0, 1.0)), panel.thickness
    )


def _style_items(
    file: ifcopenshell.file,
    context: ifcopenshell.entity_instance,
    constituent_set: ifcopenshell.entity_instance,
    items_by_entry: dict[str, list[ifcopenshell.entity_instance]],
) -> None:
    # Material styles may be assigned to the Body context or to its parent.
    contexts = [context]
    if parent := getattr(context, "ParentContext", None):
        contexts.append(parent)
    for constituent in constituent_set.MaterialConstituents or []:
        items = items_by_entry.get(constituent.Name)
        if not items or not constituent.Material:
            continue
        style = next(
            (
                s
                for c in contexts
                if (s := ifcopenshell.util.representation.get_material_style(constituent.Material, c))
            ),
            None,
        )
        if style is None:
            continue
        for item in items:
            file.createIfcStyledItem(item, (style,), None)


def _set_shape_aspect(
    file: ifcopenshell.file,
    name: str,
    items: list[ifcopenshell.entity_instance],
    representation: ifcopenshell.entity_instance,
    part_of_product: ifcopenshell.entity_instance,
) -> None:
    for aspect in part_of_product.HasShapeAspects or []:
        if aspect.Name != name:
            continue
        for aspect_rep in aspect.ShapeRepresentations:
            if aspect_rep.ContextOfItems == representation.ContextOfItems:
                aspect_rep.Items = items
                aspect_rep.RepresentationType = representation.RepresentationType
                return
    ifcopenshell.api.geometry.add_shape_aspect(
        file, name=name, items=items, representation=representation, part_of_product=part_of_product
    )
