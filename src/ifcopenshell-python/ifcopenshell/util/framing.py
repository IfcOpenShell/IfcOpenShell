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

"""Layout solver for framing systems (railings, curtain walls, storefront).

A framing system is a list of entries laid out in a 2D ``(u, v)`` domain:
``u`` is the distance along a guide path and ``v`` the height above it.

- Vertical entries (``"V"``) are lines of constant ``u``: posts, balusters, mullions.
- Horizontal entries (``"H"``) are lines of constant ``v``: rails, cables, transoms.
- Infill entries (``"INFILL"``) are rectangular cells between members: glass, panels.

The solver is pure: no IFC, no Blender. Mapping ``(u, v)`` into 3D is the caller's job,
and so is resolving profiles. The size of a member's profile across its axis is passed
in as an *extent* ``(lo, hi)`` relative to the member's axis line, along ``u`` for a
vertical and along ``v`` for a horizontal.

Every output item carries a grid ``address`` so the same solve can be written as a
single body or as separate parts, and so occurrence overrides can refer to it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Union

TOLERANCE = 1e-6

SpacingMode = Literal["FIXED", "MAX", "COUNT"]
SpacingAlign = Literal["START", "CENTER", "END"]
SpacingScope = Literal["SEGMENT", "PATH"]
Bound = Union[Literal["BASE", "TOP"], float, dict[str, str]]
JambHeight = Literal["FULL", "HEAD", "MITRE"]
# The direction (du, dv) of the line a member's end is cut along.
Cut = tuple[float, float]
Point = tuple[float, float]


class FramingError(ValueError):
    pass


@dataclass(frozen=True)
class Spacing:
    mode: SpacingMode
    value: float
    # FIXED: where spacing is measured from in each range. START and END put the first
    # member ``offset`` in from that end; CENTER splits the remainder between both ends
    # and then slides the pattern ``offset`` along u. The default is CENTER.
    # MAX: None spreads equal bays over the whole range. START, END and CENTER anchor a
    # member ``offset`` in from that end, or ``offset`` along u from the midpoint, and
    # spread equal bays on each side of it.
    align: Optional[SpacingAlign] = None
    offset: float = 0.0
    # MAX and COUNT: make the clear openings between member faces equal, instead of the
    # centre-to-centre bays. With MAX, the value is then the widest clear opening.
    openings: bool = False

    @classmethod
    def from_data(cls, data: dict[str, Any], entry_name: str) -> Spacing:
        mode = data.get("mode")
        value = data.get("value")
        if mode not in ("FIXED", "MAX", "COUNT"):
            raise FramingError(f"Entry {entry_name!r} has unknown spacing mode {mode!r}.")
        if not isinstance(value, (int, float)) or value <= 0:
            raise FramingError(f"Entry {entry_name!r} needs a positive spacing value.")
        if mode == "COUNT" and value != int(value):
            raise FramingError(f"Entry {entry_name!r} needs a whole number for COUNT spacing.")
        align = data.get("align")
        if align not in (None, "START", "CENTER", "END"):
            raise FramingError(f"Entry {entry_name!r} has unknown spacing alignment {align!r}.")
        offset = data.get("offset", 0.0)
        if not isinstance(offset, (int, float)):
            raise FramingError(f"Entry {entry_name!r} needs a number for its spacing offset.")
        if offset and (mode == "COUNT" or (mode == "MAX" and align is None)):
            raise FramingError(f"Entry {entry_name!r} has a spacing offset but nothing to offset from.")
        openings = bool(data.get("openings", False))
        if openings and mode == "FIXED":
            raise FramingError(f"Entry {entry_name!r} cannot have equal openings with FIXED spacing.")
        if openings and mode == "MAX" and align is not None:
            raise FramingError(f"Entry {entry_name!r} cannot have equal openings and an alignment.")
        return cls(mode, float(value), align, float(offset), openings)


@dataclass(frozen=True)
class VerticalEntry:
    name: str
    spacing: Optional[Spacing]
    bottom: Bound
    top: Bound
    at_ends: bool = False
    at_corners: bool = False
    # Space inside the bays between the members of these vertical entries, face to face.
    within: tuple[str, ...] = ()
    # Which of the bays to fill, counted from 1 along the path; negatives count from
    # the end. Empty means all.
    bays: tuple[int, ...] = ()
    # Cut into pieces at the faces of these horizontal entries' rows, where they cross.
    breaks_at: tuple[str, ...] = ()
    # Keep the profile's faces inside the boundary instead of centring it on it: end
    # verticals stop at the path ends, and spacing is measured to the member's faces.
    flush: bool = False
    # At corners, instead of one member centred on the corner: the first leg runs through,
    # its member flush with the second leg's outer face, and the second leg's member stands
    # against the first leg's inner face. Members' depth out of the guide plane sets where.
    butt_corners: bool = False
    # Off, members run straight through openings instead of being cut by them: edge
    # openings reach a side of the framing (a path end, the base or the top), holes do not.
    cut_by_edge_voids: bool = True
    cut_by_hole_voids: bool = True
    # "JAMB" frames the sides of openings instead of being laid out itself. Layer 1 sits
    # against the opening, layer 2 outside it, and so on. FULL runs between the entry's
    # bounds, so the head butts into it; HEAD stops under the opening's head, which sits
    # on it; MITRE mitres with the head and sill. Sloped openings use layer 1 only.
    void_role: Optional[Literal["JAMB"]] = None
    void_layer: int = 1
    jamb_height: JambHeight = "FULL"
    # The IFC classes of the fillings it frames ("IfcOpeningElement" for none). Empty means all.
    void_for: tuple[str, ...] = ()


@dataclass(frozen=True)
class HorizontalEntry:
    name: str
    # A single level, or a repeat between two bounds.
    v: Optional[Bound] = None
    spacing: Optional[Spacing] = None
    bottom: Optional[Bound] = None
    top: Optional[Bound] = None
    breaks_at: tuple[str, ...] = ()
    # A repeat fills each gap between the rows of this horizontal entry.
    within: Optional[str] = None
    # Which of those gaps to fill, counted from 1 upwards; negatives count from the top.
    rows: tuple[int, ...] = ()
    # Run only in some bays along the path: the bays between members of this vertical
    # entry (or the path segments, without one), picked as for verticals.
    between: Optional[str] = None
    bays: tuple[int, ...] = ()
    # How far each run carries on past its start and end, in plan along the path.
    # Negative pulls it back. Breaks within a run are not affected.
    extend_start: float = 0.0
    extend_end: float = 0.0
    # Keep the profile's faces inside the boundary instead of centring it on it: a level
    # at BASE or TOP sits on or under it, and spacing is measured to the member's faces.
    flush: bool = False
    # Up (or, negative, down) from the level ``v`` resolves to, so a member can follow the
    # top of the framing a set distance under it, as a lower top plate.
    level_offset: float = 0.0
    # Where the path turns: "MITRE", or butted with "BUTT_FIRST" (the first leg runs through
    # to the second leg's outer face) or "BUTT_SECOND". Laid out by the geometry writer.
    corner_joint: Literal["MITRE", "BUTT_FIRST", "BUTT_SECOND"] = "MITRE"
    cut_by_edge_voids: bool = True
    cut_by_hole_voids: bool = True
    # "HEAD" spans over openings and "SILL" under raised ones, instead of being laid out itself.
    # Layers stack away from the opening: heads upwards, sills downwards. Entries in the same
    # layer sit side by side, out of the guide plane by their offsets, as sistered members.
    # Sloped openings use layer 1 only.
    void_role: Optional[Literal["HEAD", "SILL"]] = None
    void_layer: int = 1
    void_for: tuple[str, ...] = ()


@dataclass(frozen=True)
class InfillEntry:
    name: str
    bottom: Bound
    top: Bound
    between: Optional[str] = None
    gap: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)  # left, right, bottom, top
    max_width: Optional[float] = None
    joint: float = 0.0
    # Panels stack in each gap between the rows of this horizontal entry.
    within: Optional[str] = None
    # Panels are also cut at the faces of these vertical entries' members.
    breaks_at: tuple[str, ...] = ()
    bays: tuple[int, ...] = ()  # columns along the path, as for verticals
    rows: tuple[int, ...] = ()  # rows upwards, as for horizontals
    cut_by_edge_voids: bool = True
    cut_by_hole_voids: bool = True


Entry = Union[VerticalEntry, HorizontalEntry, InfillEntry]


@dataclass(frozen=True)
class Void:
    """A rough opening in ``(u, v)``: its edges are where the jambs' inner faces, the head's
    underside and the sill's top go. It must not cross a corner of the path.

    The ``u_start`` to ``v_end`` rectangle is the opening, unless an ``outline`` gives its
    shape, for example a sloped one. Edges steeper than 45 degrees are then framed by
    jambs, and others by a head over the opening or a sill under it."""

    u_start: float
    u_end: float
    v_start: float
    v_end: float
    # The IFC class of what fills it, such as "IfcDoor", or None for a bare opening.
    filling: Optional[str] = None
    outline: tuple[Point, ...] = ()


@dataclass(frozen=True)
class VerticalMember:
    entry: str
    u: float
    v_start: float
    v_end: float
    # (segment, bay, index): bay is the parent bay for ``within`` arrays, else 0. Jambs
    # have bay -1 - n for the nth void, and index 2 * layer + side.
    address: tuple[int, int, int]
    # Counts the pieces upward when the member breaks at horizontals.
    piece: int = 0
    # Where a sloped opening edge cuts an end, the line it is cut along. Else square.
    bottom_cut: Optional[Cut] = None
    top_cut: Optional[Cut] = None


@dataclass(frozen=True)
class HorizontalMember:
    entry: str
    v: float
    u_start: float
    u_end: float
    # (row, interval): row counts repeats upward, interval counts breaks along the path.
    # Heads and sills have row -1 - n for the nth void, and count from 0 heads first.
    address: tuple[int, int]
    start_cut: Optional[Cut] = None
    end_cut: Optional[Cut] = None


@dataclass(frozen=True)
class InclinedMember:
    """A member along an edge of a sloped opening, from ``start`` to ``end`` on its axis.

    ``kind`` is how its profile is oriented: "V" as a jamb, "H" as a head or sill. Its
    section is square to its axis, and each end is cut along a line through it."""

    entry: str
    kind: Literal["V", "H"]
    start: Point
    end: Point
    start_cut: Cut
    end_cut: Cut
    # (-1 - n, 100 * edge + 10 * layer + entry in it) for the nth sloped opening.
    address: tuple[int, int]


@dataclass(frozen=True)
class InfillPanel:
    entry: str
    u_start: float
    u_end: float
    v_start: float
    v_end: float
    # (segment, bay, row, panel): row counts gaps upwards, panel counts max_width splits.
    address: tuple[int, int, int, int]
    # Counts the pieces left where voids cut the panel.
    piece: int = 0
    # Where a sloped opening cuts the panel, its shape, counter-clockwise. Else the rectangle.
    outline: tuple[Point, ...] = ()


@dataclass
class FramingLayout:
    verticals: list[VerticalMember] = field(default_factory=list)
    horizontals: list[HorizontalMember] = field(default_factory=list)
    infills: list[InfillPanel] = field(default_factory=list)
    inclined: list[InclinedMember] = field(default_factory=list)

    def by_entry(self, name: str) -> list[Union[VerticalMember, HorizontalMember, InfillPanel, InclinedMember]]:
        return [i for i in (*self.verticals, *self.horizontals, *self.infills, *self.inclined) if i.entry == name]


def resolve_profile(ifc_file: Any, reference: Optional[dict[str, Any]]) -> Optional[Any]:
    """Find the IfcProfileDef an entry's ``profile`` reference points to.

    The step id is tried first, as it is stable within a file. The name is the fallback for
    when the id no longer points to a profile, for example after appending a type into
    another file. If the id points to a profile with a different name, a profile that still
    has the stored name wins (the id came from another file). Otherwise the profile was
    renamed and the id wins. Callers should write the resolved id and name back.

    :param ifc_file: The IFC file holding the profile.
    :param reference: An entry's ``{"id": ..., "name": ...}`` profile reference.
    :return: The IfcProfileDef, or None if neither the id nor the name resolves.
    """
    if not reference:
        return None
    name = reference.get("name")
    by_name = None
    if name:
        by_name = next((p for p in ifc_file.by_type("IfcProfileDef") if p.ProfileName == name), None)
    if isinstance(step_id := reference.get("id"), int) and step_id > 0:
        try:
            by_id = ifc_file.by_id(step_id)
        except RuntimeError:
            by_id = None
        if by_id is not None and by_id.is_a("IfcProfileDef"):
            if not name or by_id.ProfileName == name or by_name is None:
                return by_id
    return by_name


def parse_system(data: dict[str, Any]) -> list[Entry]:
    """Parse and validate the ``members`` list of a framing system's JSON data."""
    members = data.get("members")
    if not isinstance(members, list):
        raise FramingError("Framing data needs a 'members' list.")
    entries: list[Entry] = []
    names: set[str] = set()
    for item in members:
        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise FramingError("Every framing entry needs a name.")
        if name in names:
            raise FramingError(f"Entry name {name!r} is used more than once.")
        names.add(name)
        entries.append(_parse_entry(item, name))
    _validate_references(entries)
    return entries


def _parse_entry(item: dict[str, Any], name: str) -> Entry:
    kind = item.get("kind")
    spacing = Spacing.from_data(item["spacing"], name) if "spacing" in item else None
    both = bool(item.get("cut_by_voids", True))
    cuts = {key: bool(item.get(key, both)) for key in ("cut_by_edge_voids", "cut_by_hole_voids")}
    void_role = item.get("void_role")
    if void_role is not None:
        return _parse_void_framing(item, name, kind, void_role)
    if kind == "V":
        if spacing is None and not item.get("at_ends") and not item.get("at_corners"):
            raise FramingError(f"Vertical {name!r} needs spacing, at_ends or at_corners.")
        return VerticalEntry(
            name=name,
            spacing=spacing,
            bottom=_parse_bound(item.get("bottom", "BASE"), name),
            top=_parse_bound(item.get("top", "TOP"), name),
            at_ends=bool(item.get("at_ends", False)),
            at_corners=bool(item.get("at_corners", False)),
            within=_parse_names(item.get("within"), name, "within"),
            bays=_parse_selection(item.get("bays"), name, "bays"),
            breaks_at=tuple(item.get("breaks_at", ())),
            flush=bool(item.get("flush", False)),
            butt_corners=bool(item.get("butt_corners", False)),
            **cuts,
        )
    elif kind == "H":
        if "v" in item:
            if spacing is not None:
                raise FramingError(f"Horizontal {name!r} has both 'v' and 'spacing'.")
            if item.get("within"):
                raise FramingError(f"Horizontal {name!r} needs spacing to repeat within another entry.")
            return HorizontalEntry(
                name=name,
                v=_parse_bound(item["v"], name),
                breaks_at=tuple(item.get("breaks_at", ())),
                between=item.get("between"),
                bays=_parse_selection(item.get("bays"), name, "bays"),
                extend_start=_parse_length(item.get("extend_start", 0.0), name, "extend_start"),
                extend_end=_parse_length(item.get("extend_end", 0.0), name, "extend_end"),
                flush=bool(item.get("flush", False)),
                level_offset=_parse_length(item.get("level_offset", 0.0), name, "level_offset"),
                corner_joint=_parse_corner_joint(item, name),
                **cuts,
            )
        if spacing is None:
            raise FramingError(f"Horizontal {name!r} needs either 'v' or 'spacing'.")
        return HorizontalEntry(
            name=name,
            spacing=spacing,
            bottom=_parse_bound(item.get("bottom", "BASE"), name),
            top=_parse_bound(item.get("top", "TOP"), name),
            breaks_at=tuple(item.get("breaks_at", ())),
            within=item.get("within"),
            rows=_parse_selection(item.get("rows"), name, "rows"),
            between=item.get("between"),
            bays=_parse_selection(item.get("bays"), name, "bays"),
            extend_start=_parse_length(item.get("extend_start", 0.0), name, "extend_start"),
            extend_end=_parse_length(item.get("extend_end", 0.0), name, "extend_end"),
            flush=bool(item.get("flush", False)),
            corner_joint=_parse_corner_joint(item, name),
            **cuts,
        )
    elif kind == "INFILL":
        max_width = item.get("max_width")
        if max_width is not None and max_width <= 0:
            raise FramingError(f"Infill {name!r} needs a positive max_width.")
        return InfillEntry(
            name=name,
            bottom=_parse_bound(item.get("bottom", "BASE"), name),
            top=_parse_bound(item.get("top", "TOP"), name),
            between=item.get("between"),
            gap=_parse_gap(item.get("gap", 0.0), name),
            max_width=max_width,
            joint=float(item.get("joint", 0.0)),
            within=item.get("within"),
            breaks_at=tuple(item.get("breaks_at", ())),
            bays=_parse_selection(item.get("bays"), name, "bays"),
            rows=_parse_selection(item.get("rows"), name, "rows"),
            **cuts,
        )
    raise FramingError(f"Entry {name!r} has unknown kind {kind!r}.")


def _parse_void_framing(item: dict[str, Any], name: str, kind: Any, void_role: Any) -> Entry:
    """An entry that frames openings: it has no layout of its own, so no spacing or level."""
    void_for = _parse_names(item.get("void_for"), name, "void_for")
    layer = item.get("void_layer", 1)
    if isinstance(layer, bool) or not isinstance(layer, int) or layer < 1:
        raise FramingError(f"Entry {name!r} needs a void layer of 1 or more.")
    if kind == "V":
        if void_role != "JAMB":
            raise FramingError(f"Vertical {name!r} has unknown void role {void_role!r}.")
        for key in ("spacing", "at_ends", "at_corners", "within", "bays"):
            if item.get(key):
                raise FramingError(f"Jamb {name!r} frames openings, so it cannot have {key!r}.")
        jamb_height = item.get("jamb_height", "FULL")
        if jamb_height not in ("FULL", "HEAD", "MITRE"):
            raise FramingError(f"Jamb {name!r} has unknown jamb height {jamb_height!r}.")
        return VerticalEntry(
            name=name,
            spacing=None,
            bottom=_parse_bound(item.get("bottom", "BASE"), name),
            top=_parse_bound(item.get("top", "TOP"), name),
            breaks_at=tuple(item.get("breaks_at", ())),
            void_role="JAMB",
            void_layer=layer,
            jamb_height=jamb_height,
            void_for=void_for,
        )
    if kind == "H":
        if void_role not in ("HEAD", "SILL"):
            raise FramingError(f"Horizontal {name!r} has unknown void role {void_role!r}.")
        for key in ("v", "spacing", "within", "between", "bays"):
            if item.get(key) is not None:
                raise FramingError(f"{void_role.title()} {name!r} frames openings, so it cannot have {key!r}.")
        return HorizontalEntry(name=name, void_role=void_role, void_for=void_for, void_layer=layer)
    raise FramingError(f"Entry {name!r} of kind {kind!r} cannot have a void role.")


def _parse_bound(value: Any, name: str) -> Bound:
    if value in ("BASE", "TOP"):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, dict) and isinstance(value.get("member"), str):
        return {"member": value["member"]}
    raise FramingError(f"Entry {name!r} has an invalid bound {value!r}.")


def _parse_names(value: Any, name: str, key: str) -> tuple[str, ...]:
    """One entry name, or a list of them."""
    if not value:
        return ()
    names = [value] if isinstance(value, str) else value
    if not isinstance(names, list) or not all(isinstance(n, str) and n for n in names):
        raise FramingError(f"Entry {name!r} needs an entry name or a list of them for {key!r}.")
    return tuple(dict.fromkeys(names))


def _parse_corner_joint(item: dict[str, Any], name: str) -> str:
    joint = item.get("corner_joint", "MITRE")
    if joint not in ("MITRE", "BUTT_FIRST", "BUTT_SECOND"):
        raise FramingError(f"Horizontal {name!r} has unknown corner joint {joint!r}.")
    return joint


def _parse_length(value: Any, name: str, key: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FramingError(f"Entry {name!r} needs {key!r} to be a number.")
    return float(value)


def _parse_selection(value: Any, name: str, key: str) -> tuple[int, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(i, int) and not isinstance(i, bool) and i for i in value):
        raise FramingError(f"Entry {name!r} needs {key!r} to be a list of non-zero whole numbers.")
    return tuple(value)


def _select(items: list, selection: tuple[int, ...]) -> list:
    """The items picked by a 1-based selection, where negatives count from the end."""
    if not selection:
        return items
    picked = {i - 1 if i > 0 else len(items) + i for i in selection}
    return [item for i, item in enumerate(items) if i in picked]


def _parse_gap(value: Any, name: str) -> tuple[float, float, float, float]:
    if isinstance(value, (int, float)):
        return (float(value),) * 4
    if isinstance(value, dict):
        return tuple(float(value.get(side, 0.0)) for side in ("left", "right", "bottom", "top"))  # type: ignore
    raise FramingError(f"Infill {name!r} has an invalid gap {value!r}.")


def _validate_references(entries: list[Entry]) -> None:
    by_name = {e.name: e for e in entries}

    def expect(ref: Optional[str], kind: type, owner: str, role: str, allow_repeating: bool = False) -> None:
        if ref is None:
            return
        target = by_name.get(ref)
        if target is None:
            raise FramingError(f"Entry {owner!r} refers to unknown entry {ref!r} as {role}.")
        if not isinstance(target, kind):
            raise FramingError(f"Entry {owner!r} needs {role} {ref!r} to be a {_KIND_NAMES[kind]}.")
        if target.void_role and role != "'breaks_at'":
            raise FramingError(f"Entry {owner!r} cannot use {ref!r} as {role}, as it only frames openings.")
        if kind is HorizontalEntry and target.v is None and not allow_repeating:
            raise FramingError(f"Entry {owner!r} cannot use repeating horizontal {ref!r} as {role}.")

    def bound_ref(bound: Optional[Bound]) -> Optional[str]:
        return bound["member"] if isinstance(bound, dict) else None

    for e in entries:
        if isinstance(e, VerticalEntry):
            for ref in e.within:
                expect(ref, VerticalEntry, e.name, "'within'")
            for ref in e.breaks_at:
                expect(ref, HorizontalEntry, e.name, "'breaks_at'", allow_repeating=True)
                if e.name in getattr(by_name[ref], "breaks_at", ()):
                    raise FramingError(
                        f"Entries {e.name!r} and {ref!r} break at each other. Choose which one is continuous."
                    )
            expect(bound_ref(e.bottom), HorizontalEntry, e.name, "bottom bound", allow_repeating=True)
            expect(bound_ref(e.top), HorizontalEntry, e.name, "top bound", allow_repeating=True)
        elif isinstance(e, HorizontalEntry):
            for ref in e.breaks_at:
                expect(ref, VerticalEntry, e.name, "'breaks_at'")
            expect(e.within, HorizontalEntry, e.name, "'within'", allow_repeating=True)
            expect(e.between, VerticalEntry, e.name, "'between'")
            expect(bound_ref(e.v), HorizontalEntry, e.name, "level")
            expect(bound_ref(e.bottom), HorizontalEntry, e.name, "bottom bound", allow_repeating=True)
            expect(bound_ref(e.top), HorizontalEntry, e.name, "top bound", allow_repeating=True)
        elif isinstance(e, InfillEntry):
            expect(e.between, VerticalEntry, e.name, "'between'")
            expect(e.within, HorizontalEntry, e.name, "'within'", allow_repeating=True)
            for ref in e.breaks_at:
                expect(ref, VerticalEntry, e.name, "'breaks_at'")
            expect(bound_ref(e.bottom), HorizontalEntry, e.name, "bottom bound", allow_repeating=True)
            expect(bound_ref(e.top), HorizontalEntry, e.name, "top bound", allow_repeating=True)

    # Verticals depend on verticals through 'within', horizontals on horizontals through
    # their bounds and 'within'. Nothing else can form a cycle, see solve().
    _topological_order([e for e in entries if isinstance(e, VerticalEntry)], lambda e: list(e.within))
    _topological_order([e for e in entries if isinstance(e, HorizontalEntry)], _horizontal_deps)


_KIND_NAMES = {VerticalEntry: "vertical", HorizontalEntry: "horizontal", InfillEntry: "infill"}


def _topological_order(entries: list, get_deps) -> list:
    by_name = {e.name: e for e in entries}
    ordered: list = []
    state: dict[str, str] = {}

    def visit(e, chain: list[str]) -> None:
        if state.get(e.name) == "done":
            return
        if state.get(e.name) == "visiting":
            raise FramingError(f"Framing entries refer to each other in a loop: {' -> '.join(chain + [e.name])}.")
        state[e.name] = "visiting"
        for dep in get_deps(e):
            if dep in by_name:
                visit(by_name[dep], chain + [e.name])
        state[e.name] = "done"
        ordered.append(e)

    for e in entries:
        visit(e, [])
    return ordered


def solve(
    entries: list[Entry],
    segment_lengths: list[float],
    height: float,
    closed: bool = False,
    scope: SpacingScope = "SEGMENT",
    extents: Optional[dict[str, tuple[float, float]]] = None,
    lateral: Optional[dict[str, tuple[float, float]]] = None,
    voids: tuple[Void, ...] = (),
    turns: Optional[list[float]] = None,
) -> FramingLayout:
    """Lay out a framing system along a guide.

    :param entries: Parsed entries, see :func:`parse_system`.
    :param segment_lengths: Lengths of the guide path's straight segments, in order.
    :param height: The occurrence's height, which is what ``"TOP"`` resolves to.
    :param closed: Whether the guide path is a loop. A loop has no ends, and its
        start is a corner.
    :param scope: ``"SEGMENT"`` restarts vertical spacing at every path vertex,
        ``"PATH"`` spaces along the whole path.
    :param extents: Per entry name, the profile's ``(lo, hi)`` extent across the
        member's axis. Missing entries are treated as lines.
    :param lateral: Per entry name, the member's ``(lo, hi)`` extent out of the guide
        plane, offset included. A run only reaches over an end vertical it overlaps
        this way, so an offset handrail is not stretched over posts it misses. Missing
        entries are assumed to overlap.
    :param voids: Rough openings to frame. Members are cut where they cross an opening or
        its framing, if their entry is cut by that kind of opening (``cut_by_edge_voids``
        for one reaching a side of the framing, else ``cut_by_hole_voids``), and spaced verticals in the
        way of a jamb are left out. Jambs, heads and sills come from the entries with a
        ``void_role``. Without them, jambs default to the end vertical's profile, the
        head to the highest horizontal's and the sill to the lowest one's.
    :param turns: How far the path turns at each vertex between segments, in radians, for
        butt corners. Square corners are assumed without them.
    """
    if not segment_lengths or any(length <= TOLERANCE for length in segment_lengths):
        raise FramingError("The guide path needs segments of non-zero length.")
    if height <= TOLERANCE:
        raise FramingError("The framing height must be greater than zero.")
    extents = extents or {}
    guide = _Guide(segment_lengths, closed, turns)
    layout = FramingLayout()

    # Order matters: horizontal levels depend only on other horizontals; verticals need
    # those levels for their bounds; horizontal intervals need the verticals they break
    # at; infill needs both.
    horizontals = [e for e in entries if isinstance(e, HorizontalEntry) and not e.void_role]
    levels = _solve_levels(_topological_order(horizontals, _horizontal_deps), height, extents)

    vertical_positions: dict[str, list[tuple[float, tuple[int, int, int]]]] = {}
    verticals = [e for e in entries if isinstance(e, VerticalEntry) and not e.void_role]
    for entry in _topological_order(verticals, lambda e: list(e.within)):
        positions = _solve_vertical_positions(
            entry, guide, scope, vertical_positions, extents, lateral or {}, {e.name: e for e in verticals}
        )
        vertical_positions[entry.name] = positions
        v_start, v_end = _resolve_bounds(entry.name, entry.bottom, entry.top, height, levels, extents)
        if v_end - v_start <= TOLERANCE:
            raise FramingError(f"Vertical {entry.name!r} has no height between its bounds.")
        for u, address in positions:
            layout.verticals.append(VerticalMember(entry.name, u, v_start, v_end, address))

    runs: dict[str, list[tuple[float, float]]] = {}
    for entry in horizontals:
        runs[entry.name] = [(0.0, guide.length)]
        if entry.bays:
            # Bays run centre to centre between the members of 'between'; breaks_at still
            # trims the ends back to their faces.
            members = [u for u, _ in vertical_positions.get(entry.between, [])] if entry.between else []
            breaks = sorted(set(members + guide.starts + [guide.length]))
            bays = [(a, b) for a, b in zip(breaks, breaks[1:]) if b - a > TOLERANCE]
            runs[entry.name] = _merge_intervals(_select(bays, entry.bays))

    # A vertical stands only where the members it is bounded by run, so balusters do not
    # float where their rail has been left out. This uses the runs before breaks, as a
    # rail broken at its own balusters still holds them.
    bounds_by_entry = {e.name: [b["member"] for b in (e.bottom, e.top) if isinstance(b, dict)] for e in verticals}
    layout.verticals = [
        m
        for m in layout.verticals
        if all(any(a - TOLERANCE <= m.u <= b + TOLERANCE for a, b in runs[name]) for name in bounds_by_entry[m.entry])
    ]
    by_name = {e.name: e for e in entries}
    # Sloped openings, and openings whose jambs mitre, are framed edge by edge.
    sloped_voids = [(i, v) for i, v in enumerate(voids) if v.outline or _jamb_mode(entries, v.filling) == "MITRE"]
    frames = [
        _frame_void(i, void, entries, verticals, guide, height, levels, layout, extents, lateral or {})
        for i, void in enumerate(voids)
        if (i, void) not in sloped_voids
    ]
    # A corner member that runs through serves as an opening's jamb where it stands. One
    # centred on the corner also runs unbroken from bound to bound; at a butt corner, the
    # member under a sloped opening of its own leg is cut by it, as an end member is.
    corners = {e.name: _corner_positions(e, guide, extents, lateral or {}) for e in verticals if e.at_corners}
    centred = {e.name: guide.corners() for e in verticals if e.at_corners and not e.butt_corners}

    def is_corner(m: VerticalMember) -> bool:
        return m.address[1] >= 0 and _near(m.u, centred.get(m.entry, []))

    beside = {
        e.name: [u for c in guide.corners() for u, _ in _butt_corner(e, c, guide, extents, lateral or {}) or []]
        for e in verticals
        if e.at_corners
    }
    corner_boxes = [
        (*_extent_at(m, extents), m.v_start, m.v_end)
        for m in layout.verticals
        if m.address[1] >= 0 and _near(m.u, corners.get(m.entry, []) + beside.get(m.entry, []))
    ]
    sloped = _frame_sloped_voids(
        sloped_voids, entries, verticals, guide, height, levels, extents, corner_boxes, lateral or {}
    )
    if sloped:
        layout.inclined = sloped.members
    for name in vertical_positions:
        kept = {m.u for m in layout.verticals if m.entry == name and m.address[1] >= 0}
        vertical_positions[name] = [p for p in vertical_positions[name] if p[0] in kept]

    lateral = lateral or {}
    for entry in horizontals:
        breakers = [m for m in layout.verticals if m.entry in entry.breaks_at]
        lo, hi = extents.get(entry.name, (0.0, 0.0))

        def beside(vertical: str, rail: str = entry.name) -> bool:
            if rail not in lateral or vertical not in lateral:
                return True
            (r_lo, r_hi), (m_lo, m_hi) = lateral[rail], lateral[vertical]
            return r_lo < m_hi - TOLERANCE and r_hi > m_lo + TOLERANCE

        for row, v in enumerate(levels[entry.name]):
            # Only verticals that actually pass through this horizontal break it, so a
            # rail sitting on top of its posts stays continuous.
            row_cuts = []
            for m in breakers:
                if m.v_start < v + hi - TOLERANCE and m.v_end > v + lo + TOLERANCE:
                    m_lo, m_hi = extents.get(m.entry, (0.0, 0.0))
                    row_cuts.append((m.u + m_lo, m.u + m_hi))
            # A run ending at a vertical it meets carries on to that vertical's outer
            # face, so a top rail covers its end posts. If it also breaks at them, the
            # cut trims it back to their inner face as before.
            row_runs = []
            for a, b in runs[entry.name]:
                if not (guide.closed and a <= TOLERANCE and b >= guide.length - TOLERANCE):
                    a -= _end_overhang(layout.verticals, a, v + lo, v + hi, extents, side=0, beside=beside)
                    b += _end_overhang(layout.verticals, b, v + lo, v + hi, extents, side=1, beside=beside)
                    a, b = a - entry.extend_start, b + entry.extend_end
                if b - a > TOLERANCE:
                    row_runs.append((a, b))
            intervals = [i for a, b in row_runs for i in _subtract_intervals(a, b, row_cuts)]
            for interval, (u_start, u_end) in enumerate(intervals):
                layout.horizontals.append(HorizontalMember(entry.name, v, u_start, u_end, (row, interval)))

    # Panels follow their rails as laid out, before openings cut them, which cut the panels too.
    uncut_horizontals = list(layout.horizontals)
    if frames:
        for frame in frames:
            frame.place_head_and_sill(layout.horizontals, by_name, extents)
        layout.horizontals = _cut_horizontals(layout.horizontals, frames, by_name, extents)
    for frame in frames:
        layout.horizontals.extend(frame.horizontals)
    # A sloped opening also cuts the framing of rectangular ones, as a rake cuts a window's jambs.
    if sloped:
        layout.horizontals = sloped.cut_horizontals(layout.horizontals, by_name)

    # Verticals that break at horizontals are cut at the faces of the rows that cross
    # them, where those rows actually run.
    breaks_by_entry = {e.name: e.breaks_at for e in entries if isinstance(e, VerticalEntry) and e.breaks_at}
    if breaks_by_entry:
        pieces = []
        for m in layout.verticals:
            names = breaks_by_entry.get(m.entry)
            if not names:
                pieces.append(m)
                continue
            cuts = []
            for h in layout.horizontals:
                if h.entry in names and h.u_start - TOLERANCE <= m.u <= h.u_end + TOLERANCE:
                    lo, hi = extents.get(h.entry, (0.0, 0.0))
                    if h.v + hi > m.v_start + TOLERANCE and h.v + lo < m.v_end - TOLERANCE:
                        cuts.append((h.v + lo, h.v + hi))
            for i, (a, b) in enumerate(_subtract_intervals(m.v_start, m.v_end, cuts)):
                pieces.append(VerticalMember(m.entry, m.u, a, b, m.address, i))
        layout.verticals = pieces
    if frames:
        layout.verticals = _cut_verticals(layout.verticals, frames, by_name, extents, is_corner)
    if sloped:
        layout.verticals = sloped.cut_verticals(layout.verticals, by_name, is_corner)

    for entry in entries:
        if isinstance(entry, InfillEntry):
            panels = _solve_infill(
                entry, guide, height, levels, vertical_positions, layout.verticals, uncut_horizontals, extents
            )
            if cutting := [f for f in frames if _is_cut(entry, f.edge)]:
                panels = _cut_panels(panels, cutting, entry.gap)
            if sloped:
                panels = sloped.cut_panels(panels, entry, entry.gap)
            layout.infills.extend(panels)
    return layout


def _end_overhang(
    verticals: list[VerticalMember],
    u: float,
    v_bottom: float,
    v_top: float,
    extents: dict[str, tuple[float, float]],
    side: int,
    beside=lambda name: True,
) -> float:
    """How far past ``u`` the widest vertical standing there reaches, if it meets the
    horizontal spanning ``v_bottom`` to ``v_top``: through it, or stopping just under or over it.

    :param side: 0 for the start of a run (the vertical's ``lo`` side), 1 for its end.
    :param beside: Whether the horizontal overlaps a vertical entry out of the guide plane.
    """
    overhang = 0.0
    for m in verticals:
        if (
            abs(m.u - u) <= TOLERANCE
            and m.v_start <= v_top + TOLERANCE
            and m.v_end >= v_bottom - TOLERANCE
            and beside(m.entry)
        ):
            lo, hi = extents.get(m.entry, (0.0, 0.0))
            overhang = max(overhang, -lo if side == 0 else hi)
    return overhang


class _Guide:
    def __init__(self, segment_lengths: list[float], closed: bool, turns: Optional[list[float]] = None):
        self.closed = closed
        # At each vertex between segments, how far the path turns. Square if not known.
        self.turns = list(turns) if turns else [math.pi / 2] * (len(segment_lengths) - 1)
        self.starts: list[float] = []
        total = 0.0
        for length in segment_lengths:
            self.starts.append(total)
            total += length
        self.length = total
        self.ends = [s + l for s, l in zip(self.starts, segment_lengths)]

    def segment_at(self, u: float) -> int:
        for i, end in enumerate(self.ends):
            if u < end - TOLERANCE:
                return i
        return len(self.ends) - 1

    def corners(self) -> list[float]:
        corners = self.starts[1:]
        return [0.0] + corners if self.closed else corners


def _horizontal_deps(e: HorizontalEntry) -> list[Optional[str]]:
    return [b["member"] if isinstance(b, dict) else None for b in (e.v, e.bottom, e.top)] + [e.within]


def _resolve_bound(
    bound: Bound,
    height: float,
    levels: dict[str, list[float]],
    extents: dict[str, tuple[float, float]],
    side: Literal["bottom", "top", "level"],
) -> float:
    if bound == "BASE":
        return 0.0
    if bound == "TOP":
        return height
    if isinstance(bound, float):
        return bound
    name = bound["member"]
    lo, hi = extents.get(name, (0.0, 0.0))
    v = levels[name][0]
    # A bottom bound stops on the member's top face, a top bound under its bottom face.
    return v + hi if side == "bottom" else v + lo if side == "top" else v


def _bound_faces(
    bound: Bound,
    height: float,
    levels: dict[str, list[float]],
    extents: dict[str, tuple[float, float]],
    side: Literal["bottom", "top"],
) -> list[float]:
    """Every height a bound can stand for: one, or one per row of a repeating member."""
    if not isinstance(bound, dict):
        return [_resolve_bound(bound, height, levels, extents, side)]
    lo, hi = extents.get(bound["member"], (0.0, 0.0))
    # A bottom bound stops on the member's top face, a top bound under its bottom face.
    return sorted(v + hi if side == "bottom" else v + lo for v in levels[bound["member"]])


def _resolve_bounds(
    name: str,
    bottom: Bound,
    top: Bound,
    height: float,
    levels: dict[str, list[float]],
    extents: dict[str, tuple[float, float]],
) -> tuple[float, float]:
    """Resolve a pair of bounds, picking the nearest rows of repeating members.

    A repeating top bound is its lowest row above the bottom; a repeating bottom bound
    its highest row below the top. With both repeating, the bottom is the first row
    and the top the next row above it. Gaps between further rows are filled with
    ``within`` instead."""
    bottoms = _bound_faces(bottom, height, levels, extents, "bottom")
    tops = _bound_faces(top, height, levels, extents, "top")
    if not bottoms or not tops:
        raise FramingError(f"Entry {name!r} is bounded by a repeating horizontal with no rows.")
    if len(tops) == 1:
        v_top = tops[0]
        below = [b for b in bottoms if b < v_top - TOLERANCE]
        return (below[-1] if below else bottoms[0]), v_top
    v_bottom = bottoms[0]
    above = [t for t in tops if t > v_bottom + TOLERANCE]
    return v_bottom, (above[0] if above else tops[-1])


def _solve_levels(
    horizontals: list[HorizontalEntry], height: float, extents: dict[str, tuple[float, float]]
) -> dict[str, list[float]]:
    levels: dict[str, list[float]] = {}
    for entry in horizontals:
        lo, hi = extents.get(entry.name, (0.0, 0.0)) if entry.flush else (0.0, 0.0)
        if entry.v is not None:
            v = _resolve_bound(entry.v, height, levels, extents, side="level")
            # Flush, the bottom face sits on BASE and the top face under TOP.
            v -= lo if entry.v == "BASE" else hi if entry.v == "TOP" else 0.0
            levels[entry.name] = [v + entry.level_offset]
            continue
        assert entry.spacing and entry.bottom is not None and entry.top is not None
        start, end = _resolve_bounds(entry.name, entry.bottom, entry.top, height, levels, extents)
        if end - start <= TOLERANCE:
            raise FramingError(f"Horizontal {entry.name!r} has no room between its bounds.")
        gaps = [(start, end)]
        if entry.within:
            w_lo, w_hi = extents.get(entry.within, (0.0, 0.0))
            gaps = _subtract_intervals(start, end, [(v + w_lo, v + w_hi) for v in levels[entry.within]])
        levels[entry.name] = [
            v
            for a, b in _select(gaps, entry.rows)
            for v in (
                # Openings run between the bound faces, so flush has nothing to add.
                _interior_positions(a, b, entry.spacing, extent=extents.get(entry.name, (0.0, 0.0)))
                if entry.spacing.openings
                else _interior_positions(
                    a - lo, b - hi, entry.spacing, entry.flush, extents.get(entry.name, (0.0, 0.0))
                )
            )
        ]
    return levels


def _interior_positions(
    start: float,
    end: float,
    spacing: Spacing,
    inclusive: bool = False,
    extent: tuple[float, float] = (0.0, 0.0),
) -> list[float]:
    """Positions strictly inside ``(start, end)``, evenly spread by ``spacing``.

    With ``inclusive``, as for a flush member whose range already stops at its faces, a
    FIXED or anchored MAX member may also sit on either end. ``extent`` is the member's
    own ``(lo, hi)``, which equal openings need."""
    # Positive keeps members off the ends, negative lets them sit on them.
    slack = -TOLERANCE if inclusive else TOLERANCE
    length = end - start
    if spacing.openings:
        width = extent[1] - extent[0]
        if spacing.mode == "COUNT":
            n_openings = int(spacing.value) + 1
        else:
            n_openings = max(1, math.ceil((length + width) / (spacing.value + width) - TOLERANCE))
        return _equal_openings(start, end, n_openings, extent)
    if spacing.mode == "COUNT":
        n = int(spacing.value)
        return [start + length * i / (n + 1) for i in range(1, n + 1)]
    if spacing.mode == "MAX":
        anchor = {
            None: None,
            "START": start + spacing.offset,
            "CENTER": (start + end) / 2 + spacing.offset,
            "END": end - spacing.offset,
        }[spacing.align]
        # An anchor on or past either end leaves nothing to split around.
        if anchor is None or not start + slack < anchor < end - slack:
            return _equal_bays(start, end, spacing.value)
        return _equal_bays(start, anchor, spacing.value) + [anchor] + _equal_bays(anchor, end, spacing.value)
    # FIXED: exact spacing. START and END run from the first member, offset in from
    # that end; CENTER splits the remainder between both ends, then slides the pattern.
    step = spacing.value
    if spacing.align == "START":
        positions = _steps(start + spacing.offset, end, step)
    elif spacing.align == "END":
        positions = [end - (p - start) for p in _steps(start + spacing.offset, end, step)]
    else:
        n = int(math.floor(length / step + TOLERANCE))
        origin = start + (length - n * step) / 2 + spacing.offset
        first = math.ceil((start - origin) / step - TOLERANCE)
        positions = _steps(origin + first * step, end, step)
    return sorted(p for p in positions if start + slack < p < end - slack)


def _equal_bays(start: float, end: float, max_width: float) -> list[float]:
    """Positions strictly inside ``(start, end)`` that split it into equal bays no wider than ``max_width``."""
    n_bays = max(1, math.ceil((end - start) / max_width - TOLERANCE))
    return [start + (end - start) * i / n_bays for i in range(1, n_bays)]


def _equal_openings(start: float, end: float, n_openings: int, extent: tuple[float, float]) -> list[float]:
    """Positions of ``n_openings - 1`` members of ``extent`` that leave equal clear openings in ``(start, end)``."""
    lo, hi = extent
    gap = (end - start - (n_openings - 1) * (hi - lo)) / n_openings
    if gap <= TOLERANCE:
        raise FramingError("The members are too wide to leave openings between them.")
    # Member k's low face is k openings and k - 1 members in.
    return [start + k * gap + (k - 1) * (hi - lo) - lo for k in range(1, n_openings)]


def _steps(first: float, end: float, step: float) -> list[float]:
    """``first``, then every ``step`` after it up to ``end``."""
    n = int(math.floor((end - first) / step + TOLERANCE)) if end >= first else -1
    return [first + i * step for i in range(n + 1)]


def _fixed_positions(
    entry: VerticalEntry,
    guide: _Guide,
    extents: dict[str, tuple[float, float]],
    lateral: Optional[dict[str, tuple[float, float]]] = None,
) -> list[tuple[float, int]]:
    """Where an entry's end and corner members stand, and on which segment."""
    own_lo, own_hi = extents.get(entry.name, (0.0, 0.0)) if entry.flush else (0.0, 0.0)
    fixed: list[tuple[float, int]] = []
    if entry.at_ends and not guide.closed:
        fixed += [(0.0 - own_lo, 0), (guide.length - own_hi, len(guide.starts) - 1)]
    if entry.at_corners:
        for corner in guide.corners():
            fixed += _butt_corner(entry, corner, guide, extents, lateral or {}) or [(corner, guide.segment_at(corner))]
    return fixed


def _corner_positions(
    entry: VerticalEntry,
    guide: _Guide,
    extents: dict[str, tuple[float, float]],
    lateral: dict[str, tuple[float, float]],
) -> list[float]:
    """Where an entry's corner members stand that bound both legs: on each corner, or at a
    butt corner the first leg's, which runs through."""
    positions = []
    for corner in guide.corners():
        positions.append((_butt_corner(entry, corner, guide, extents, lateral) or [(corner, 0)])[0][0])
    return positions


def _butt_corner(
    entry: VerticalEntry,
    corner: float,
    guide: _Guide,
    extents: dict[str, tuple[float, float]],
    lateral: dict[str, tuple[float, float]],
) -> Optional[list[tuple[float, int]]]:
    """An entry's two members at a butt corner: the first leg's, flush with the second leg's
    outer face, and the second leg's, against the first leg's inner face. None for a member
    centred on the corner, or at the start of a loop."""
    if not entry.butt_corners:
        return None
    segment = next((i for i, s in enumerate(guide.starts) if i > 0 and abs(s - corner) <= TOLERANCE), None)
    half = max((abs(x) for x in lateral.get(entry.name, (0.0, 0.0))), default=0.0)
    if segment is None or half <= TOLERANCE:
        return None
    # Along either leg, the other leg's face is this far past the corner.
    reach = half / max(abs(math.sin(guide.turns[segment - 1])), 0.2)
    lo, hi = extents.get(entry.name, (0.0, 0.0))
    # The first leg's member stands past the corner in u, on its own leg extended.
    return [(corner + reach - hi, segment - 1), (corner + reach - lo, segment)]


def _parent_extent(
    name: str, u: float, guide: _Guide, extents: dict[str, tuple[float, float]], lateral: dict[str, tuple[float, float]]
) -> tuple[float, float]:
    """How far a parent member reaches along the path either side of ``u``.

    A member on a corner of the path faces along one leg, so across the other it reaches as
    far as its depth out of the guide plane. Its widest half is kept clear on both legs."""
    lo, hi = extents.get(name, (0.0, 0.0))
    if not _near(u, guide.corners()):
        return lo, hi
    half = max(abs(lo), abs(hi), *(abs(x) for x in lateral.get(name, (0.0, 0.0))))
    return -half, half


def _solve_vertical_positions(
    entry: VerticalEntry,
    guide: _Guide,
    scope: SpacingScope,
    solved: dict[str, list[tuple[float, tuple[int, int, int]]]],
    extents: dict[str, tuple[float, float]],
    lateral: Optional[dict[str, tuple[float, float]]] = None,
    verticals: Optional[dict[str, VerticalEntry]] = None,
) -> list[tuple[float, tuple[int, int, int]]]:
    # Flush, the member's own faces are what reach the path ends and the range ends.
    own_lo, own_hi = extents.get(entry.name, (0.0, 0.0)) if entry.flush else (0.0, 0.0)
    lateral = lateral or {}
    fixed = _fixed_positions(entry, guide, extents, lateral)

    # Each range is (u_start, u_end, segment, bay) that spacing fills.
    ranges: list[tuple[float, float, int, int]] = []
    if entry.within:
        # Every parent member as (u, lo, hi), whichever entry it comes from.
        parents = []
        for name in entry.within:
            # A butt corner's two members bound the legs as one: the first leg's bay runs to
            # its member's inner face, the second leg's from its member's outer face.
            parent = (verticals or {}).get(name)
            pairs = {
                c: pair
                for c in guide.corners()
                if parent and (pair := _butt_corner(parent, c, guide, extents, lateral))
            }
            paired = [u for pair in pairs.values() for u, _ in pair]
            lo, hi = extents.get(name, (0.0, 0.0))
            for u, _ in solved[name]:
                if not _near(u, paired):
                    parents.append((u, *_parent_extent(name, u, guide, extents, lateral)))
            for c, ((first, _), (second, _)) in pairs.items():
                parents.append((c, first + lo - c, second + hi - c))

        def faces(u: float) -> Optional[tuple[float, float]]:
            # Where parents of several entries share a position, the widest one bounds the bay.
            here = [(lo, hi) for p, lo, hi in parents if abs(p - u) <= TOLERANCE]
            return (min(lo for lo, _ in here), max(hi for _, hi in here)) if here else None

        # Bays run face to face between parent members and never across a path vertex.
        breaks = sorted(set([p for p, _, _ in parents] + guide.starts + [guide.length]))
        bay_counts: dict[int, int] = {}
        for a, b in zip(breaks, breaks[1:]):
            if b - a <= TOLERANCE:
                continue
            start = a + face[1] if (face := faces(a)) else a
            end = b + face[0] if (face := faces(b)) else b
            if end - start <= TOLERANCE:
                continue
            segment = guide.segment_at(a)
            bay = bay_counts.get(segment, 0)
            bay_counts[segment] = bay + 1
            ranges.append((start, end, segment, bay))
    elif scope == "PATH":
        ranges.append((0.0, guide.length, 0, 0))
    else:
        ranges = [(s, e, i, 0) for i, (s, e) in enumerate(zip(guide.starts, guide.ends))]
    ranges = _select(ranges, entry.bays)

    found: list[tuple[float, int, int]] = []  # (u, segment, bay)
    for u, segment in fixed:
        found.append((u, segment, 0))
    if entry.spacing:
        for start, end, segment, bay in ranges:
            extent = extents.get(entry.name, (0.0, 0.0))
            if entry.spacing.openings:
                # Openings run between faces: the range's, or those of this entry's own end or
                # corner members standing on its ends, wherever flush has put them.
                lo, hi = extent
                for u, _ in fixed:
                    if u + lo <= start + TOLERANCE and u + hi >= start - TOLERANCE:
                        start = max(start, u + hi)
                    if u + lo <= end + TOLERANCE and u + hi >= end - TOLERANCE:
                        end = min(end, u + lo)
                positions = _interior_positions(start, end, entry.spacing, extent=extent)
            else:
                positions = _interior_positions(start - own_lo, end - own_hi, entry.spacing, entry.flush, extent)
            for u in positions:
                found.append((u, segment if scope == "SEGMENT" or entry.within else guide.segment_at(u), bay))

    found.sort()
    positions: list[tuple[float, tuple[int, int, int]]] = []
    counters: dict[tuple[int, int], int] = {}
    for u, segment, bay in found:
        if positions and abs(positions[-1][0] - u) <= TOLERANCE:
            continue
        index = counters.get((segment, bay), 0)
        counters[(segment, bay)] = index + 1
        positions.append((u, (segment, bay, index)))
    return positions


def _near(u: float, values: list[float]) -> bool:
    return any(abs(u - v) <= TOLERANCE for v in values)


def _merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Join intervals that touch, so a rail over adjacent bays stays one piece."""
    merged: list[tuple[float, float]] = []
    for a, b in sorted(intervals):
        if merged and a <= merged[-1][1] + TOLERANCE:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def _subtract_intervals(start: float, end: float, cuts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    cursor = start
    for cut_start, cut_end in sorted(cuts):
        if cut_start - cursor > TOLERANCE:
            result.append((cursor, min(cut_start, end)))
        cursor = max(cursor, cut_end)
        if cursor >= end - TOLERANCE:
            break
    if end - cursor > TOLERANCE:
        result.append((cursor, end))
    return [(a, b) for a, b in result if b - a > TOLERANCE]


def _coverage(members: list[HorizontalMember], name: str, u_start: float, u_end: float) -> dict[float, float]:
    """For each row of a horizontal entry, how much of ``[u_start, u_end]`` it runs along."""
    covered: dict[float, float] = {}
    for m in members:
        if m.entry == name:
            overlap = min(m.u_end, u_end) - max(m.u_start, u_start)
            if overlap > 0:
                covered[m.v] = covered.get(m.v, 0.0) + overlap
    return covered


def _solve_infill(
    entry: InfillEntry,
    guide: _Guide,
    height: float,
    levels: dict[str, list[float]],
    vertical_positions: dict[str, list[tuple[float, tuple[int, int, int]]]],
    verticals: list[VerticalMember],
    horizontals: list[HorizontalMember],
    extents: dict[str, tuple[float, float]],
) -> list[InfillPanel]:
    gap_left, gap_right, gap_bottom, gap_top = entry.gap
    v_start, v_end = _resolve_bounds(entry.name, entry.bottom, entry.top, height, levels, extents)
    if v_end - v_start - gap_bottom - gap_top <= TOLERANCE:
        raise FramingError(f"Infill {entry.name!r} has no height between its bounds.")

    members = [u for u, _ in vertical_positions.get(entry.between, [])] if entry.between else []
    lo, hi = extents.get(entry.between, (0.0, 0.0)) if entry.between else (0.0, 0.0)
    # Panels are planar, so cells always split at path vertices as well as at members.
    breaks = sorted(set(members + guide.starts + [guide.length]))
    # Like a rail, a panel only breaks at members that pass through its height.
    cuts = [
        (m.u + extents.get(m.entry, (0.0, 0.0))[0], m.u + extents.get(m.entry, (0.0, 0.0))[1])
        for m in verticals
        if m.entry in entry.breaks_at and m.v_start < v_end - TOLERANCE and m.v_end > v_start + TOLERANCE
    ]
    columns: list[tuple[float, float, int, int]] = []
    bay_counts: dict[int, int] = {}
    for a, b in zip(breaks, breaks[1:]):
        if b - a <= TOLERANCE:
            continue
        segment = guide.segment_at(a)
        face_start = a + hi if _near(a, members) else a
        face_end = b + lo if _near(b, members) else b
        for piece_start, piece_end in _subtract_intervals(face_start, face_end, cuts):
            start, end = piece_start + gap_left, piece_end - gap_right
            if end - start > TOLERANCE:
                bay = bay_counts.get(segment, 0)
                bay_counts[segment] = bay + 1
                columns.append((start, end, segment, bay))

    bound_members = [b["member"] for b in (entry.bottom, entry.top) if isinstance(b, dict)]
    panels: list[InfillPanel] = []
    for start, end, segment, bay in _select(columns, entry.bays):
        width = end - start
        # A panel follows the members it is bounded by: where a bounding rail does not
        # run along most of the bay, there is no panel.
        if any(sum(_coverage(horizontals, name, start, end).values()) < width / 2 for name in bound_members):
            continue
        rows = [(v_start, v_end)]
        if entry.within:
            w_lo, w_hi = extents.get(entry.within, (0.0, 0.0))
            covered = _coverage(horizontals, entry.within, start, end)
            cuts = [(v + w_lo, v + w_hi) for v, length in covered.items() if length >= width / 2]
            rows = _subtract_intervals(v_start, v_end, cuts)
        n = 1
        if entry.max_width:
            n = max(1, math.ceil((width + entry.joint) / (entry.max_width + entry.joint) - TOLERANCE))
        panel_width = (width - (n - 1) * entry.joint) / n
        if panel_width <= TOLERANCE:
            raise FramingError(f"Infill {entry.name!r} joints leave no room for panels.")
        for row in _select(list(range(len(rows))), entry.rows):
            a, b = rows[row][0] + gap_bottom, rows[row][1] - gap_top
            if b - a <= TOLERANCE:
                continue
            for i in range(n):
                u0 = start + i * (panel_width + entry.joint)
                panels.append(InfillPanel(entry.name, u0, u0 + panel_width, a, b, (segment, bay, row, i)))
    return panels


Rect = tuple[float, float, float, float]  # u_start, u_end, v_start, v_end


def _overlaps(a_start: float, a_end: float, b_start: float, b_end: float) -> bool:
    return a_start < b_end - TOLERANCE and a_end > b_start + TOLERANCE


def _void_framing(entries: list[Entry], kind: type, role: str, filling: Optional[str]) -> list:
    """The entries with this void role that frame the filling, those naming it first."""
    key = filling or "IfcOpeningElement"
    found = [
        e for e in entries if isinstance(e, kind) and e.void_role == role and (not e.void_for or key in e.void_for)
    ]
    return sorted(found, key=lambda e: not e.void_for)


def _extent_at(
    m: Union[VerticalMember, HorizontalMember], extents: dict[str, tuple[float, float]]
) -> tuple[float, float]:
    """A member's faces across its axis, as (lo, hi) around its position."""
    lo, hi = extents.get(m.entry, (0.0, 0.0))
    at = m.u if isinstance(m, VerticalMember) else m.v
    return at + lo, at + hi


@dataclass
class _VoidFrame:
    index: int
    void: Void
    # Whether the opening reaches a side of the framing, rather than being a hole in it.
    edge: bool
    reaches_top: bool
    # The faces the head spans between, one per side.
    head_span: list[float]
    # Head and sill layers away from the opening, each the entries side by side in it.
    heads: list[list[HorizontalEntry]]
    sills: list[list[HorizontalEntry]]
    # What the jambs, head and sill take up. With the opening, these cut other members.
    rects: list[Rect] = field(default_factory=list)
    horizontals: list[HorizontalMember] = field(default_factory=list)

    def all_rects(self) -> list[Rect]:
        return self.rects + [(self.void.u_start, self.void.u_end, self.void.v_start, self.void.v_end)]

    def place_head_and_sill(
        self,
        horizontals: list[HorizontalMember],
        by_name: dict[str, Entry],
        extents: dict[str, tuple[float, float]],
    ) -> None:
        void = self.void
        plans = []
        # Each layer sits on the one below it, or hangs under the one above for sills.
        face = void.v_end
        for layer in self.heads if not self.reaches_top else ():
            levels = [(e, face - extents.get(e.name, (0.0, 0.0))[0]) for e in layer]
            plans += [(e, v, tuple(self.head_span)) for e, v in levels]
            face = max(v + extents.get(e.name, (0.0, 0.0))[1] for e, v in levels)
        face = void.v_start
        for layer in self.sills if void.v_start > TOLERANCE else ():
            levels = [(e, face - extents.get(e.name, (0.0, 0.0))[1]) for e in layer]
            plans += [(e, v, (void.u_start, void.u_end)) for e, v in levels]
            face = min(v + extents.get(e.name, (0.0, 0.0))[0] for e, v in levels)
        for interval, (entry, v, (a, b)) in enumerate(plans):
            lo, hi = extents.get(entry.name, (0.0, 0.0))
            # A member running through the opening where this one would go serves as it instead.
            if any(
                not _is_cut(by_name[h.entry], self.edge)
                and _overlaps(*_extent_at(h, extents), v + lo, v + hi)
                and min(h.u_end, b) - max(h.u_start, a) >= (b - a) / 2
                for h in horizontals
            ):
                continue
            self.horizontals.append(HorizontalMember(entry.name, v, a, b, (-1 - self.index, interval)))
            self.rects.append((a, b, v + lo, v + hi))


def _frame_void(
    index: int,
    void: Void,
    entries: list[Entry],
    verticals: list[VerticalEntry],
    guide: _Guide,
    height: float,
    levels: dict[str, list[float]],
    layout: FramingLayout,
    extents: dict[str, tuple[float, float]],
    lateral: Optional[dict[str, tuple[float, float]]] = None,
) -> _VoidFrame:
    """Place an opening's jambs, leaving out spaced verticals in their way. The head and
    sill are placed once the horizontals are known, see :meth:`_VoidFrame.place_head_and_sill`."""
    if void.u_end - void.u_start <= TOLERANCE or void.v_end - void.v_start <= TOLERANCE:
        raise FramingError(f"Opening {index + 1} has no size.")
    if any(void.u_start + TOLERANCE < s < void.u_end - TOLERANCE for s in guide.starts[1:]):
        raise FramingError(f"Opening {index + 1} crosses a corner of the path.")
    segment = guide.segment_at((void.u_start + void.u_end) / 2)
    reaches_top = void.v_end >= height - TOLERANCE

    # Jamb layers from the opening outwards. Without jamb entries, the end vertical frames it.
    layers: list[tuple[VerticalEntry, JambHeight]] = []
    if jambs := _void_framing(entries, VerticalEntry, "JAMB", void.filling):
        for layer in sorted({e.void_layer for e in jambs}):
            entry = next(e for e in jambs if e.void_layer == layer)
            layers.append((entry, entry.jamb_height))
    elif default := next((e for e in verticals if e.at_ends), None) or next(
        (e for e in verticals if e.at_corners), None
    ):
        layers.append((default, "FULL"))
    # The head bears on the layers inside the first FULL one and spans between its faces.
    full = next((k for k, (_, mode) in enumerate(layers) if mode == "FULL"), None)

    singles = [e for e in entries if isinstance(e, HorizontalEntry) and not e.void_role and e.v is not None]
    heads = _void_layers(entries, "HEAD", void.filling)
    if not heads and singles:
        heads = [[max(singles, key=lambda e: levels[e.name][0])]]
    sills = _void_layers(entries, "SILL", void.filling)
    if not sills and singles:
        sills = [[min(singles, key=lambda e: levels[e.name][0])]]
    edge = (
        void.u_start <= TOLERANCE or void.u_end >= guide.length - TOLERANCE or void.v_start <= TOLERANCE or reaches_top
    )
    frame = _VoidFrame(index, void, edge, reaches_top, [void.u_start, void.u_end], heads, sills)

    by_name = {e.name: e for e in entries}
    fixed = {e.name: [u for u, _ in _fixed_positions(e, guide, extents, lateral)] for e in verticals}
    dropped: set[int] = set()
    for side, edge in ((0, void.u_start), (1, void.u_end)):
        if edge <= TOLERANCE if side == 0 else edge >= guide.length - TOLERANCE:
            continue  # The opening runs to the path end, so there is nothing to frame it there.
        face, locked = edge, False
        for k, (entry, mode) in enumerate(layers):
            lo, hi = extents.get(entry.name, (0.0, 0.0))
            u = face - hi if side == 0 else face - lo
            v_start, v_end = _resolve_bounds(entry.name, entry.bottom, entry.top, height, levels, extents)
            if mode == "HEAD" and not reaches_top:
                v_end = void.v_end
            in_way = [
                m
                for m in layout.verticals
                if id(m) not in dropped
                and _overlaps(*_extent_at(m, extents), u + lo, u + hi)
                and _overlaps(m.v_start, m.v_end, v_start, v_end)
            ]
            # End and corner members, other jambs and members running through the opening
            # serve as the jamb here. Spaced members make way for it.
            serving = [
                m
                for m in in_way
                if m.address[1] < 0 or _near(m.u, fixed.get(m.entry, [])) or not _is_cut(by_name[m.entry], frame.edge)
            ]
            if serving:
                if not locked:
                    frame.head_span[side] = _extent_at(serving[0], extents)[1 - side]
                break
            dropped.update(id(m) for m in in_way)
            layout.verticals.append(VerticalMember(entry.name, u, v_start, v_end, (segment, -1 - index, 2 * k + side)))
            frame.rects.append((u + lo, u + hi, v_start, v_end))
            outer = u + lo if side == 0 else u + hi
            if not locked:
                frame.head_span[side] = face if k == full else outer
                locked = k == full
            face = outer
    layout.verticals = [m for m in layout.verticals if id(m) not in dropped]
    return frame


def _cut_verticals(
    verticals: list[VerticalMember],
    frames: list[_VoidFrame],
    by_name: dict[str, Entry],
    extents: dict[str, tuple[float, float]],
    keep=lambda m: False,
) -> list[VerticalMember]:
    """Cut the members that cross openings or their framing, renumbering the pieces."""
    result: list[VerticalMember] = []
    counters: dict[tuple, int] = {}
    for m in verticals:
        pieces = [(m.v_start, m.v_end)]
        if m.address[1] >= 0 and not keep(m):
            faces = _extent_at(m, extents)
            cutting = [f for f in frames if _is_cut(by_name[m.entry], f.edge)]
            cuts = [(r[2], r[3]) for f in cutting for r in f.all_rects() if _overlaps(*faces, r[0], r[1])]
            pieces = _subtract_intervals(m.v_start, m.v_end, cuts)
        for a, b in pieces:
            key = (m.entry, m.address)
            counters[key] = counters.get(key, -1) + 1
            result.append(VerticalMember(m.entry, m.u, a, b, m.address, counters[key]))
    return result


def _cut_horizontals(
    horizontals: list[HorizontalMember],
    frames: list[_VoidFrame],
    by_name: dict[str, Entry],
    extents: dict[str, tuple[float, float]],
) -> list[HorizontalMember]:
    """Cut the members that cross openings or their framing, renumbering the intervals."""
    result: list[HorizontalMember] = []
    counters: dict[tuple, int] = {}
    for h in horizontals:
        pieces = [(h.u_start, h.u_end)]
        if cutting := [f for f in frames if _is_cut(by_name[h.entry], f.edge)]:
            faces = _extent_at(h, extents)
            cuts = [(r[0], r[1]) for f in cutting for r in f.all_rects() if _overlaps(*faces, r[2], r[3])]
            pieces = _subtract_intervals(h.u_start, h.u_end, cuts)
        for a, b in pieces:
            key = (h.entry, h.address[0])
            counters[key] = counters.get(key, -1) + 1
            result.append(HorizontalMember(h.entry, h.v, a, b, (h.address[0], counters[key])))
    return result


def _cut_panels(
    panels: list[InfillPanel], frames: list[_VoidFrame], gap: tuple[float, float, float, float]
) -> list[InfillPanel]:
    """Cut panels around openings and their framing, keeping the entry's gap at each cut."""
    gap_left, gap_right, gap_bottom, gap_top = gap
    result: list[InfillPanel] = []
    for panel in panels:
        # Each piece, with which of its left, right, bottom and top sides a cut made.
        pieces: list[tuple[Rect, tuple[bool, bool, bool, bool]]] = [
            ((panel.u_start, panel.u_end, panel.v_start, panel.v_end), (False, False, False, False))
        ]
        for frame in frames:
            for rect in frame.all_rects():
                pieces = [p for box, cut in pieces for p in _subtract_rect(box, cut, rect)]
        n = 0
        for (u0, u1, v0, v1), (left, right, bottom, top) in pieces:
            u0, u1 = u0 + (gap_left if left else 0.0), u1 - (gap_right if right else 0.0)
            v0, v1 = v0 + (gap_bottom if bottom else 0.0), v1 - (gap_top if top else 0.0)
            if u1 - u0 > TOLERANCE and v1 - v0 > TOLERANCE:
                result.append(InfillPanel(panel.entry, u0, u1, v0, v1, panel.address, n))
                n += 1
    return result


def _subtract_rect(
    box: Rect, cut: tuple[bool, bool, bool, bool], rect: Rect
) -> list[tuple[Rect, tuple[bool, bool, bool, bool]]]:
    """What is left of ``box`` around ``rect``: full-width pieces below and above it, then
    the pieces beside it."""
    u0, u1, v0, v1 = box
    a, b, c, d = rect
    if not (_overlaps(u0, u1, a, b) and _overlaps(v0, v1, c, d)):
        return [(box, cut)]
    left, right, bottom, top = cut
    pieces = []
    if c > v0 + TOLERANCE:
        pieces.append(((u0, u1, v0, c), (left, right, bottom, True)))
    if d < v1 - TOLERANCE:
        pieces.append(((u0, u1, d, v1), (left, right, True, top)))
    # Beside the cut, a side against a piece above or below is a seam, not a cut.
    mid_bottom = bottom if c <= v0 + TOLERANCE else False
    mid_top = top if d >= v1 - TOLERANCE else False
    mid_v0, mid_v1 = max(v0, c), min(v1, d)
    if a > u0 + TOLERANCE:
        pieces.append(((u0, a, mid_v0, mid_v1), (left, True, mid_bottom, mid_top)))
    if b < u1 - TOLERANCE:
        pieces.append(((b, u1, mid_v0, mid_v1), (True, right, mid_bottom, mid_top)))
    return pieces


def _void_layers(entries: list[Entry], role: str, filling: Optional[str], kind: type = HorizontalEntry) -> list[list]:
    """The layers of a role framing a filling, from the opening out. In each layer, the
    entries naming the filling are used if there are any, else those for all openings."""
    found = _void_framing(entries, kind, role, filling)
    layers = []
    for layer in sorted({e.void_layer for e in found}):
        here = [e for e in found if e.void_layer == layer]
        layers.append([e for e in here if e.void_for] or here)
    return layers


def _is_cut(entry: Entry, edge: bool) -> bool:
    """Whether an entry's members are cut by an edge opening, or by a hole."""
    return entry.cut_by_edge_voids if edge else entry.cut_by_hole_voids


def _jamb_mode(entries: list[Entry], filling: Optional[str]) -> JambHeight:
    """How the innermost jamb framing this filling meets the head and sill."""
    jambs = _void_framing(entries, VerticalEntry, "JAMB", filling)
    if not jambs:
        return "FULL"
    layer = min(e.void_layer for e in jambs)
    return next(e for e in jambs if e.void_layer == layer).jamb_height


def _sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def _along(a: Point, d: Point, s: float) -> Point:
    return (a[0] + d[0] * s, a[1] + d[1] * s)


def _dot(a: Point, b: Point) -> float:
    return a[0] * b[0] + a[1] * b[1]


def _cross(a: Point, b: Point) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _unit(a: Point) -> Point:
    length = math.hypot(*a)
    return (a[0] / length, a[1] / length)


def _meet(p: Point, d: Point, q: Point, e: Point) -> Optional[float]:
    """How far along ``d`` from ``p`` the line through ``q`` along ``e`` is, or None if parallel."""
    denominator = _cross(d, e)
    if abs(denominator) <= 1e-9:
        return None
    return _cross(_sub(q, p), e) / denominator


@dataclass
class _SlopedEdge:
    """An edge of a sloped opening, and the member framing it from outside the opening."""

    a: Point
    b: Point
    direction: Point  # from a to b
    entry: Optional[Union[VerticalEntry, HorizontalEntry]] = None
    # The framing's layers out from the opening, each the entries side by side in it.
    layers: list[list[Union[VerticalEntry, HorizontalEntry]]] = field(default_factory=list)
    role: str = ""
    kind: Literal["V", "H"] = "V"
    t: Point = (0.0, 1.0)  # the member's axis: upward for "V", along the path for "H"
    p: Point = (1.0, 0.0)  # the direction the profile's (lo, hi) extent is measured in
    out: Point = (1.0, 0.0)  # away from the opening
    depth: float = 0.0  # of all its layers
    mode: JambHeight = "FULL"

    @property
    def far(self) -> Point:
        """A point on the framing's outer face, away from the opening."""
        return _along(self.a, self.out, self.depth)


class _SlopedFrames:
    """Sloped openings and their framing, merged into a zone of edge openings and one of holes."""

    def __init__(self, zones: dict[bool, Any], members: list[InclinedMember]):
        self.zones = zones
        self.members = members
        self._cutters: dict[tuple[bool, ...], _SlopedZone] = {}

    def _cutter(self, entry: Entry) -> Optional[_SlopedZone]:
        """The zone that cuts an entry's members: the kinds of opening it is cut by."""
        import shapely

        key = tuple(edge for edge in (True, False) if edge in self.zones and _is_cut(entry, edge))
        if not key:
            return None
        if key not in self._cutters:
            self._cutters[key] = _SlopedZone(shapely.unary_union([self.zones[edge] for edge in key]))
        return self._cutters[key]

    def cut_verticals(
        self, verticals: list[VerticalMember], by_name: dict[str, Entry], keep=lambda m: False
    ) -> list[VerticalMember]:
        result: list[VerticalMember] = []
        counters: dict[tuple, int] = {}
        for m in verticals:
            pieces = [((m.u, m.v_start), (m.u, m.v_end), None, None)]
            if not keep(m) and (cutter := self._cutter(by_name[m.entry])):
                pieces = cutter.cut_line((m.u, m.v_start), (m.u, m.v_end))
            for (_, v_start), (_, v_end), bottom, top in pieces:
                key = (m.entry, m.address)
                counters[key] = counters.get(key, -1) + 1
                result.append(
                    VerticalMember(
                        m.entry,
                        m.u,
                        v_start,
                        v_end,
                        m.address,
                        counters[key],
                        bottom or (m.bottom_cut if abs(v_start - m.v_start) <= TOLERANCE else None),
                        top or (m.top_cut if abs(v_end - m.v_end) <= TOLERANCE else None),
                    )
                )
        return result

    def cut_horizontals(self, horizontals: list[HorizontalMember], by_name: dict[str, Entry]) -> list[HorizontalMember]:
        result: list[HorizontalMember] = []
        counters: dict[tuple, int] = {}
        for h in horizontals:
            pieces = [((h.u_start, h.v), (h.u_end, h.v), None, None)]
            if cutter := self._cutter(by_name[h.entry]):
                pieces = cutter.cut_line((h.u_start, h.v), (h.u_end, h.v))
            for (u_start, _), (u_end, _), start, end in pieces:
                key = (h.entry, h.address[0])
                counters[key] = counters.get(key, -1) + 1
                result.append(
                    HorizontalMember(
                        h.entry,
                        h.v,
                        u_start,
                        u_end,
                        (h.address[0], counters[key]),
                        start or (h.start_cut if abs(u_start - h.u_start) <= TOLERANCE else None),
                        end or (h.end_cut if abs(u_end - h.u_end) <= TOLERANCE else None),
                    )
                )
        return result

    def cut_panels(
        self, panels: list[InfillPanel], entry: InfillEntry, gap: tuple[float, float, float, float]
    ) -> list[InfillPanel]:
        cutter = self._cutter(entry)
        return cutter.cut_panels(panels, gap) if cutter else panels


class _SlopedZone:
    """Where sloped openings and their framing are, which cuts other members."""

    def __init__(self, zone: Any):
        self.zone = zone
        self.segments: list[tuple[Point, Point]] = []
        for polygon in getattr(zone, "geoms", [zone]):
            for ring in (polygon.exterior, *polygon.interiors):
                coords = list(ring.coords)
                self.segments += [(a, b) for a, b in zip(coords, coords[1:]) if math.dist(a, b) > TOLERANCE]

    def _cut_direction(self, point: Point) -> Cut:
        """The direction of the zone's boundary where a member leaves it."""

        def distance(segment: tuple[Point, Point]) -> float:
            a, b = segment
            d = _sub(b, a)
            s = min(max(_dot(_sub(point, a), d) / _dot(d, d), 0.0), 1.0)
            return math.dist(point, _along(a, d, s))

        a, b = min(self.segments, key=distance)
        return _unit(_sub(b, a))

    def cut_line(self, a: Point, b: Point) -> list[tuple[Point, Point, Optional[Cut], Optional[Cut]]]:
        """What is left of the line from ``a`` to ``b`` outside the zone, with the new cuts."""
        import shapely.geometry

        line = shapely.geometry.LineString([a, b])
        if not line.intersects(self.zone):
            return [(a, b, None, None)]
        rest = line.difference(self.zone)
        length = math.dist(a, b)
        d = _unit(_sub(b, a))
        pieces = []
        for piece in getattr(rest, "geoms", [rest]):
            if piece.is_empty or piece.geom_type != "LineString" or piece.length <= TOLERANCE:
                continue
            start, end = sorted((tuple(piece.coords[0]), tuple(piece.coords[-1])), key=lambda p: _dot(_sub(p, a), d))
            start_cut = None if _dot(_sub(start, a), d) <= TOLERANCE else self._cut_direction(start)
            end_cut = None if _dot(_sub(end, a), d) >= length - TOLERANCE else self._cut_direction(end)
            pieces.append((start, end, start_cut, end_cut))
        return sorted(pieces, key=lambda p: _dot(_sub(p[0], a), d))

    def cut_panels(self, panels: list[InfillPanel], gap: tuple[float, float, float, float]) -> list[InfillPanel]:
        """Cut panels around the zone, keeping the entry's widest gap from it."""
        import shapely.geometry
        import shapely.ops

        cutter = self.zone.buffer(max(gap), join_style=2) if max(gap) > TOLERANCE else self.zone
        result: list[InfillPanel] = []
        for panel in panels:
            if panel.outline:
                box = shapely.geometry.Polygon(panel.outline)
            else:
                box = shapely.geometry.box(panel.u_start, panel.v_start, panel.u_end, panel.v_end)
            if not box.intersects(cutter) or box.intersection(cutter).area <= TOLERANCE:
                result.append(panel)
                continue
            rest = box.difference(cutter)
            pieces = [g for g in getattr(rest, "geoms", [rest]) if g.geom_type == "Polygon"]
            # A panel is one solid without holes, so a hole splits it in two.
            while any(p.interiors for p in pieces):
                p = next(p for p in pieces if p.interiors)
                x = shapely.geometry.Polygon(p.interiors[0]).centroid.x
                knife = shapely.geometry.LineString([(x, p.bounds[1] - 1.0), (x, p.bounds[3] + 1.0)])
                pieces.remove(p)
                pieces += [g for g in shapely.ops.split(p, knife).geoms if g.geom_type == "Polygon"]
            n = 0
            for piece in pieces:
                if piece.area <= TOLERANCE:
                    continue
                u0, v0, u1, v1 = piece.bounds
                rectangle = abs(piece.area - (u1 - u0) * (v1 - v0)) <= TOLERANCE
                ring = shapely.geometry.polygon.orient(piece, 1.0).exterior.coords[:-1]
                outline = () if rectangle else tuple((float(u), float(v)) for u, v in ring)
                result.append(InfillPanel(panel.entry, u0, u1, v0, v1, panel.address, n, outline))
                n += 1
        return result


def _frame_sloped_voids(
    sloped_voids: list[tuple[int, Void]],
    entries: list[Entry],
    verticals: list[VerticalEntry],
    guide: _Guide,
    height: float,
    levels: dict[str, list[float]],
    extents: dict[str, tuple[float, float]],
    corner_boxes: Optional[list[Rect]] = None,
    lateral: Optional[dict[str, tuple[float, float]]] = None,
) -> Optional[_SlopedFrames]:
    """Frame sloped openings edge by edge, from outside them.

    A corner member standing where a jamb would go serves as it instead.

    Openings that overlap are merged, and only edges inside the framing are framed. Where
    two members meet at a corner, the jamb's ``jamb_height`` decides which one runs
    through: FULL the jamb, HEAD the head or sill, MITRE neither. Members framing edges
    of the same kind mitre. A member ending on the framing's boundary stops at its bound,
    as a jamb on the bottom rail, or at the path end, and one reaching a corner of the path
    stops there. Layers stack out from the opening, as for rectangular openings."""
    if not sloped_voids:
        return None
    import shapely
    import shapely.geometry

    def shape(void: Void) -> Any:
        points = void.outline or (
            (void.u_start, void.v_start),
            (void.u_end, void.v_start),
            (void.u_end, void.v_end),
            (void.u_start, void.v_end),
        )
        if len(points) < 3:
            raise FramingError("A sloped opening needs at least three points.")
        return shapely.geometry.Polygon(points).buffer(0)

    butt = next((e for e in verticals if e.at_corners and e.butt_corners), None)

    def corner_bound(segment: int, side: int) -> Optional[float]:
        """Where a member reaching the corner at the start (0) or end (1) of its segment
        ends, or the corner itself if it is not a butt corner, so the writer mitres there.
        On the first leg it runs over the member that runs through, to the other leg's outer
        face; on the second it stops at the first leg's inner face."""
        corner = guide.starts[segment] if side == 0 else guide.ends[segment]
        if corner >= guide.length - TOLERANCE:
            corner = 0.0
        pair = _butt_corner(butt, corner, guide, extents, lateral or {}) if butt else None
        if not pair:
            return guide.starts[segment] if side == 0 else guide.ends[segment]
        (first, _), (second, _) = pair
        lo, hi = extents.get(butt.name, (0.0, 0.0))
        return first + hi if side == 1 else second + lo

    def _depth(entry: Entry) -> float:
        lo, hi = extents.get(entry.name, (0.0, 0.0))
        return hi - lo

    def on_leg(void: Void) -> tuple[Any, int]:
        """An opening on the leg it is measured along: to its corners, or at a butt corner on
        to the other leg's outer face, over the member there. It may reach past the path's ends."""
        polygon = shape(void)
        segment = guide.segment_at(polygon.centroid.x)
        last, far = len(guide.starts) - 1, 1e9
        low = corner_bound(segment, 0) if segment > 0 or guide.closed else -far
        high = corner_bound(segment, 1) if segment < last or guide.closed else far
        return polygon.intersection(shapely.geometry.box(low, -far, high, far)), segment

    domain = shapely.geometry.box(0.0, 0.0, guide.length, height)
    shapes = [(i, void, *on_leg(void)) for i, void in sloped_voids]
    merged = shapely.unary_union([s for _, _, s, _ in shapes]).intersection(domain)
    parts = [g for g in getattr(merged, "geoms", [merged]) if g.geom_type == "Polygon" and g.area > TOLERANCE]
    # The openings and their members' strips, by whether they reach a side of the framing.
    zones: dict[bool, list[Any]] = {}
    members: list[InclinedMember] = []

    def on_boundary(a: Point, b: Point) -> bool:
        # The framing's sides, and the corners of the path, where the other leg frames it.
        lines = [(0, 0.0), (0, guide.length), (1, 0.0), (1, height)] + [(0, s) for s in guide.starts[1:]]
        return any(abs(a[axis] - value) <= TOLERANCE and abs(b[axis] - value) <= TOLERANCE for axis, value in lines)

    for part in parts:
        index, void, part_segment = next(
            ((i, v, seg) for i, v, s, seg in shapes if s.intersects(part)), (*sloped_voids[0], 0)
        )
        u0, v0, u1, v1 = part.bounds
        edge = u0 <= TOLERANCE or u1 >= guide.length - TOLERANCE or v0 <= TOLERANCE or v1 >= height - TOLERANCE
        zone_parts = zones.setdefault(edge, [])
        zone_parts.append(part)

        jambs = _void_layers(entries, "JAMB", void.filling, VerticalEntry)
        if not jambs:
            default = next((e for e in verticals if e.at_ends), None) or next(
                (e for e in verticals if e.at_corners), None
            )
            jambs = [[default]] if default else []
        mode = jambs[0][0].jamb_height if jambs else "FULL"
        singles = [e for e in entries if isinstance(e, HorizontalEntry) and not e.void_role and e.v is not None]
        heads = _void_layers(entries, "HEAD", void.filling)
        if not heads and singles:
            heads = [[max(singles, key=lambda e: levels[e.name][0])]]
        sills = _void_layers(entries, "SILL", void.filling)
        if not sills and singles:
            sills = [[min(singles, key=lambda e: levels[e.name][0])]]

        # Counter-clockwise, so the opening is on each edge's left, without collinear points.
        ring = list(shapely.geometry.polygon.orient(part, 1.0).exterior.coords)[:-1]
        points = [
            p
            for k, p in enumerate(ring)
            if abs(_cross(_sub(p, ring[k - 1]), _sub(ring[(k + 1) % len(ring)], p))) > TOLERANCE**2
        ]
        edges: list[_SlopedEdge] = []
        for k, a in enumerate(points):
            b = points[(k + 1) % len(points)]
            edge = _SlopedEdge(a, b, _unit(_sub(b, a)))
            edges.append(edge)
            if on_boundary(a, b):
                continue
            d = edge.direction
            edge.out = (d[1], -d[0])
            if abs(d[1]) > abs(d[0]):
                edge.role, edge.kind, edge.layers = "JAMB", "V", jambs
                edge.t = d if d[1] > 0 else (-d[0], -d[1])
                edge.p = (edge.t[1], -edge.t[0])
            else:
                edge.role = "HEAD" if edge.out[1] > 0 else "SILL"
                edge.kind, edge.layers = "H", heads if edge.role == "HEAD" else sills
                edge.t = d if d[0] > 0 else (-d[0], -d[1])
                edge.p = (-edge.t[1], edge.t[0])
            if not edge.layers:
                continue
            depth = sum(max(_depth(e) for e in layer) for layer in edge.layers)
            if edge.role == "JAMB" and corner_boxes:
                strip = shapely.geometry.Polygon([a, b, _along(b, edge.out, depth), _along(a, edge.out, depth)])
                if any(
                    strip.intersection(shapely.geometry.box(u0, v0, u1, v1)).area > TOLERANCE
                    for u0, u1, v0, v1 in corner_boxes
                ):
                    continue
            edge.entry = edge.layers[0][0]
            edge.depth = depth
            edge.mode = mode

        def end_of(
            x: _SlopedEdge, origin: Point, entry: Entry, vertex: Point, y: _SlopedEdge, is_end: bool
        ) -> tuple[float, Cut]:
            """Where a member of ``x`` with its axis through ``origin`` ends at ``vertex``, next
            to edge ``y``, and the line it is cut along. Every layer meets ``y``'s framing as a
            whole, so the layers end on the same lines."""
            if y.entry is None:
                line = (vertex, y.direction)
                if on_boundary(y.a, y.b) and x.kind == "V" and abs(y.direction[1]) <= TOLERANCE:
                    # A jamb ending on the framing's base or top stops at its own bound.
                    v_bottom, v_top = _resolve_bounds(entry.name, entry.bottom, entry.top, height, levels, extents)
                    line = ((vertex[0], v_bottom if vertex[1] < height / 2 else v_top), (1.0, 0.0))
                at = _meet(origin, x.t, *line)
                if at is None or abs(_cross(x.t, line[1])) < 0.2:
                    return _dot(_sub(vertex, origin), x.t), x.p
                return at, line[1]
            if x.role == y.role or "JAMB" not in (x.role, y.role) or x.mode == "MITRE":
                far = _meet(x.far, x.t, y.far, y.t)
                corner = _along(x.far, x.t, far) if far is not None else vertex
                cut = _unit(_sub(corner, vertex)) if math.dist(corner, vertex) > TOLERANCE else x.p
                at = _meet(origin, x.t, vertex, cut)
                return (at if at is not None else _dot(_sub(vertex, origin), x.t)), cut
            through = (x.role == "JAMB") == (x.mode == "FULL")
            ats = [at for q in (y.a, y.far) if (at := _meet(origin, x.t, q, y.t)) is not None]
            pick = max if through == is_end else min
            return pick(ats), y.t

        for k, x in enumerate(edges):
            if x.entry is None:
                continue
            # A member stays on its own segment of the path, cut plumb at its ends, and at a
            # butt corner square, see corner_bound.
            segment = part_segment
            segment_ends = (guide.starts[segment], guide.ends[segment])
            outward = 1.0 if _dot(x.out, x.p) > 0 else -1.0
            offset = 0.0  # of this layer's face nearest the opening, from the edge
            for n_layer, layer in enumerate(x.layers):
                for n_entry, entry in enumerate(layer):
                    lo, hi = extents.get(entry.name, (0.0, 0.0))
                    near = _along(x.a, x.out, offset)
                    origin = _along(near, x.p, -lo if outward > 0 else -hi)
                    ends = []
                    for vertex, y in ((x.a, edges[k - 1]), (x.b, edges[(k + 1) % len(edges)])):
                        other = x.b if vertex is x.a else x.a
                        is_end = _dot(_sub(vertex, other), x.t) > 0
                        ends.append((is_end, *end_of(x, origin, entry, vertex, y, is_end)))
                    (_, start_at, start_cut), (_, end_at, end_cut) = sorted(ends, key=lambda e: e[0])
                    clipped = []
                    for at, cut in ((start_at, start_cut), (end_at, end_cut)):
                        u = _along(origin, x.t, at)[0]
                        bound = None
                        if u < segment_ends[0] + TOLERANCE:
                            bound = corner_bound(segment, 0) if segment > 0 or guide.closed else None
                            if bound is None and u < segment_ends[0] - TOLERANCE:
                                bound = segment_ends[0]
                        elif u > segment_ends[1] - TOLERANCE:
                            last = len(guide.starts) - 1
                            bound = corner_bound(segment, 1) if segment < last or guide.closed else None
                            if bound is None and u > segment_ends[1] + TOLERANCE:
                                bound = segment_ends[1]
                        if bound is not None and (plumb := _meet(origin, x.t, (bound, 0.0), (0.0, 1.0))) is not None:
                            at, cut = plumb, (0.0, 1.0)
                        clipped.append((at, cut))
                    (start_at, start_cut), (end_at, end_cut) = clipped
                    if end_at - start_at <= TOLERANCE:
                        continue
                    start, end = _along(origin, x.t, start_at), _along(origin, x.t, end_at)
                    address = (-1 - index, k * 100 + n_layer * 10 + n_entry)
                    members.append(InclinedMember(entry.name, x.kind, start, end, start_cut, end_cut, address))
                    # What the member takes up: between its faces, and between its end cuts.
                    corners = []
                    for line_point in (near, _along(near, x.out, hi - lo)):
                        for point, cut in ((start, start_cut), (end, end_cut)):
                            at = _meet(line_point, x.t, point, cut)
                            corners.append(_along(line_point, x.t, at) if at is not None else point)
                    strip = shapely.geometry.Polygon([corners[0], corners[1], corners[3], corners[2]]).buffer(0)
                    if strip.area > TOLERANCE:
                        zone_parts.append(strip)
                offset += max(_depth(e) for e in layer)

    return _SlopedFrames({edge: shapely.unary_union(p) for edge, p in zones.items()}, members)
