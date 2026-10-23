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

from dataclasses import dataclass
from math import cos, radians, sin
from typing import Any, Optional, Union

import numpy as np

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper
import ifcopenshell.util.framing
import ifcopenshell.util.shape
import ifcopenshell.util.unit
from ifcopenshell.util.framing import TOLERANCE, FramingError, SpacingScope
from ifcopenshell.util.shape_builder import SequenceOfVectors, ShapeBuilder

_Z = np.array((0.0, 0.0, 1.0))


@dataclass(frozen=True)
class FramingExtrusion:
    """A vertical member: the entry's profile extruded up from ``origin``.

    The profile's X axis runs along ``ref_direction`` (along the path, rotated by the
    entry's rotation) and its Y axis out of the guide plane, to the path's left.
    """

    entry: str
    origin: np.ndarray
    ref_direction: np.ndarray
    depth: float


@dataclass(frozen=True)
class FramingRail:
    """A straight piece of a horizontal member: the entry's profile extruded along ``direction``.

    The profile's X axis is ``x_axis`` (out of the guide plane, to the path's left,
    rotated by the entry's rotation) and its Y axis is up. Where the member turns a
    corner, the piece is extended by ``start_extension`` / ``end_extension`` and cut by a
    mitre plane through ``start_corner`` / ``end_corner``, whose normal points away from
    the piece. A ``None`` mitre is a square end.

    The corner is on the path rather than on the offset axis: the mitre plane bisects the
    corner, so rails offset out of the guide plane still meet on it.
    """

    entry: str
    origin: np.ndarray  # where the piece's axis starts, before any extension
    direction: np.ndarray
    x_axis: np.ndarray
    length: float
    start_mitre: Optional[np.ndarray] = None
    end_mitre: Optional[np.ndarray] = None
    start_extension: float = 0.0
    end_extension: float = 0.0
    start_corner: Optional[np.ndarray] = None
    end_corner: Optional[np.ndarray] = None


@dataclass(frozen=True)
class FramingPanel:
    """An infill panel: a ``width`` x ``height`` rectangle in the guide plane, ``thickness`` thick."""

    entry: str
    origin: np.ndarray  # bottom left corner, on the panel's centre plane
    direction: np.ndarray  # along the path
    normal: np.ndarray  # out of the guide plane, to the path's left
    width: float
    height: float
    thickness: float


FramingItem = Union[FramingExtrusion, FramingRail, FramingPanel]


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
        self.lengths = np.linalg.norm(np.diff(pts, axis=0), axis=1)
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

    def direction_3d(self, segment: int) -> np.ndarray:
        return (self.points[segment + 1] - self.points[segment]) / self.lengths[segment]

    def normal(self, segment: int) -> np.ndarray:
        return np.cross(_Z, self.direction(segment))

    def pieces(self, u_start: float, u_end: float) -> list[tuple[int, float, float]]:
        """Split ``[u_start, u_end]`` at path vertices into ``(segment, u_start, u_end)`` pieces."""
        result = []
        for i, (start, length) in enumerate(zip(self.starts, self.lengths)):
            a, b = max(u_start, start), min(u_end, start + length)
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
        d = guide.direction_3d(segment)
        n = guide.normal(segment)
        up = np.cross(d, n)
        x_axis = n * cos(rotation) + up * sin(rotation)
        y_axis = np.cross(d, x_axis)
        section = np.outer(profile_points[:, 0], x_axis) + np.outer(profile_points[:, 1], y_axis)
        frames.append((segment, a, b, d, n, x_axis, section))

    def mitre_between(i: int, j: int) -> Optional[np.ndarray]:
        m = frames[i][3] + frames[j][3]
        length = np.linalg.norm(m)
        # A path that doubles back on itself has no usable mitre, so it gets square ends.
        return m / length if length > TOLERANCE else None

    result = []
    for k, (segment, a, b, d, n, x_axis, section) in enumerate(frames):
        start = guide.point_at(a, segment) + _Z * v + n * offset
        end = start + d * (b - a)
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
                b - a,
                start_mitre,
                end_mitre,
                start_extension,
                end_extension,
                start_corner,
                end_corner,
            )
        )
    return result


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
    for entry in entries:
        if isinstance(entry, ifcopenshell.util.framing.InfillEntry):
            continue
        if entry.name not in profile_points:
            raise FramingError(f"Entry {entry.name!r} needs a profile.")
        kind = data[entry.name]["kind"]
        extents[entry.name] = _member_extent(
            profile_points[entry.name], kind, radians(data[entry.name].get("rotation", 0.0))
        )

    layout = ifcopenshell.util.framing.solve(
        entries, guide_map.lengths.tolist(), height, closed=closed, scope=scope, extents=extents
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
                items.append(
                    FramingExtrusion(
                        entry.name, origin, d * cos(rotation) + n * sin(rotation), member.v_end - member.v_start
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
                item.depth,
                position=item.origin,
                position_x_axis=item.ref_direction,
                position_z_axis=_Z,
            )
        elif isinstance(item, FramingRail):
            ifc_item = _rail_solid(builder, profiles[item.entry], item)
        else:
            ifc_item = _panel_solid(file, item)
        ifc_items.append(ifc_item)
        items_by_entry.setdefault(item.entry, []).append(ifc_item)

    representation = builder.get_representation(context, ifc_items)
    if part_of_product is not None:
        for name, entry_items in items_by_entry.items():
            _set_shape_aspect(file, name, entry_items, representation, part_of_product)
    return representation


def _rail_solid(
    builder: ShapeBuilder, profile: ifcopenshell.entity_instance, rail: FramingRail
) -> ifcopenshell.entity_instance:
    solid = builder.extrude(
        profile,
        rail.length + rail.start_extension + rail.end_extension,
        position=rail.origin - rail.direction * rail.start_extension,
        position_x_axis=rail.x_axis,
        position_z_axis=rail.direction,
    )
    if rail.start_mitre is None and rail.end_mitre is None:
        return solid
    for corner, mitre in ((rail.start_corner, rail.start_mitre), (rail.end_corner, rail.end_mitre)):
        if mitre is None:
            continue
        half_space = builder.half_space_solid(builder.plane(corner, mitre))
        solid = builder.file.createIfcBooleanClippingResult("DIFFERENCE", solid, half_space)
    # Wrapped as a solid model, so it can share a SolidModel representation with plain extrusions.
    return builder.file.createIfcCsgSolid(solid)


def _panel_solid(file: ifcopenshell.file, panel: FramingPanel) -> ifcopenshell.entity_instance:
    # Local X runs along the path and local Y up, which needs the local Z pointing to the
    # path's right. The extrusion then runs from the left face to the right face.
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
