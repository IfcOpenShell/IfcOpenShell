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
SpacingScope = Literal["SEGMENT", "PATH"]
Bound = Union[Literal["BASE", "TOP"], float, dict[str, str]]


class FramingError(ValueError):
    pass


@dataclass(frozen=True)
class Spacing:
    mode: SpacingMode
    value: float

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
        return cls(mode, float(value))


@dataclass(frozen=True)
class VerticalEntry:
    name: str
    spacing: Optional[Spacing]
    bottom: Bound
    top: Bound
    at_ends: bool = False
    at_corners: bool = False
    within: Optional[str] = None


@dataclass(frozen=True)
class HorizontalEntry:
    name: str
    # A single level, or a repeat between two bounds.
    v: Optional[Bound] = None
    spacing: Optional[Spacing] = None
    bottom: Optional[Bound] = None
    top: Optional[Bound] = None
    breaks_at: tuple[str, ...] = ()


@dataclass(frozen=True)
class InfillEntry:
    name: str
    bottom: Bound
    top: Bound
    between: Optional[str] = None
    gap: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)  # left, right, bottom, top
    max_width: Optional[float] = None
    joint: float = 0.0


Entry = Union[VerticalEntry, HorizontalEntry, InfillEntry]


@dataclass(frozen=True)
class VerticalMember:
    entry: str
    u: float
    v_start: float
    v_end: float
    # (segment, bay, index): bay is the parent bay for ``within`` arrays, else 0.
    address: tuple[int, int, int]


@dataclass(frozen=True)
class HorizontalMember:
    entry: str
    v: float
    u_start: float
    u_end: float
    # (row, interval): row counts repeats upward, interval counts breaks along the path.
    address: tuple[int, int]


@dataclass(frozen=True)
class InfillPanel:
    entry: str
    u_start: float
    u_end: float
    v_start: float
    v_end: float
    # (segment, bay, panel): panel counts max_width splits within a bay.
    address: tuple[int, int, int]


@dataclass
class FramingLayout:
    verticals: list[VerticalMember] = field(default_factory=list)
    horizontals: list[HorizontalMember] = field(default_factory=list)
    infills: list[InfillPanel] = field(default_factory=list)

    def by_entry(self, name: str) -> list[Union[VerticalMember, HorizontalMember, InfillPanel]]:
        return [i for i in (*self.verticals, *self.horizontals, *self.infills) if i.entry == name]


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
            within=item.get("within"),
        )
    elif kind == "H":
        if "v" in item:
            if spacing is not None:
                raise FramingError(f"Horizontal {name!r} has both 'v' and 'spacing'.")
            return HorizontalEntry(
                name=name, v=_parse_bound(item["v"], name), breaks_at=tuple(item.get("breaks_at", ()))
            )
        if spacing is None:
            raise FramingError(f"Horizontal {name!r} needs either 'v' or 'spacing'.")
        return HorizontalEntry(
            name=name,
            spacing=spacing,
            bottom=_parse_bound(item.get("bottom", "BASE"), name),
            top=_parse_bound(item.get("top", "TOP"), name),
            breaks_at=tuple(item.get("breaks_at", ())),
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
        )
    raise FramingError(f"Entry {name!r} has unknown kind {kind!r}.")


def _parse_bound(value: Any, name: str) -> Bound:
    if value in ("BASE", "TOP"):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, dict) and isinstance(value.get("member"), str):
        return {"member": value["member"]}
    raise FramingError(f"Entry {name!r} has an invalid bound {value!r}.")


def _parse_gap(value: Any, name: str) -> tuple[float, float, float, float]:
    if isinstance(value, (int, float)):
        return (float(value),) * 4
    if isinstance(value, dict):
        return tuple(float(value.get(side, 0.0)) for side in ("left", "right", "bottom", "top"))  # type: ignore
    raise FramingError(f"Infill {name!r} has an invalid gap {value!r}.")


def _validate_references(entries: list[Entry]) -> None:
    by_name = {e.name: e for e in entries}

    def expect(ref: Optional[str], kind: type, owner: str, role: str) -> None:
        if ref is None:
            return
        target = by_name.get(ref)
        if target is None:
            raise FramingError(f"Entry {owner!r} refers to unknown entry {ref!r} as {role}.")
        if not isinstance(target, kind):
            raise FramingError(f"Entry {owner!r} needs {role} {ref!r} to be a {_KIND_NAMES[kind]}.")
        if kind is HorizontalEntry and target.v is None:
            raise FramingError(f"Entry {owner!r} cannot use repeating horizontal {ref!r} as {role}.")

    def bound_ref(bound: Optional[Bound]) -> Optional[str]:
        return bound["member"] if isinstance(bound, dict) else None

    for e in entries:
        if isinstance(e, VerticalEntry):
            expect(e.within, VerticalEntry, e.name, "'within'")
            expect(bound_ref(e.bottom), HorizontalEntry, e.name, "bottom bound")
            expect(bound_ref(e.top), HorizontalEntry, e.name, "top bound")
        elif isinstance(e, HorizontalEntry):
            for ref in e.breaks_at:
                expect(ref, VerticalEntry, e.name, "'breaks_at'")
            expect(bound_ref(e.v), HorizontalEntry, e.name, "level")
            expect(bound_ref(e.bottom), HorizontalEntry, e.name, "bottom bound")
            expect(bound_ref(e.top), HorizontalEntry, e.name, "top bound")
        elif isinstance(e, InfillEntry):
            expect(e.between, VerticalEntry, e.name, "'between'")
            expect(bound_ref(e.bottom), HorizontalEntry, e.name, "bottom bound")
            expect(bound_ref(e.top), HorizontalEntry, e.name, "top bound")

    # Verticals depend on verticals through 'within', horizontals on horizontals through
    # their bounds. Nothing else can form a cycle, see solve().
    _topological_order([e for e in entries if isinstance(e, VerticalEntry)], lambda e: [e.within])
    _topological_order(
        [e for e in entries if isinstance(e, HorizontalEntry)],
        lambda e: [bound_ref(e.v), bound_ref(e.bottom), bound_ref(e.top)],
    )


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
    """
    if not segment_lengths or any(length <= TOLERANCE for length in segment_lengths):
        raise FramingError("The guide path needs segments of non-zero length.")
    if height <= TOLERANCE:
        raise FramingError("The framing height must be greater than zero.")
    extents = extents or {}
    guide = _Guide(segment_lengths, closed)
    layout = FramingLayout()

    # Order matters: horizontal levels depend only on other horizontals; verticals need
    # those levels for their bounds; horizontal intervals need the verticals they break
    # at; infill needs both.
    horizontals = [e for e in entries if isinstance(e, HorizontalEntry)]
    levels = _solve_levels(_topological_order(horizontals, _horizontal_deps), height, extents)

    vertical_positions: dict[str, list[tuple[float, tuple[int, int, int]]]] = {}
    verticals = [e for e in entries if isinstance(e, VerticalEntry)]
    for entry in _topological_order(verticals, lambda e: [e.within]):
        positions = _solve_vertical_positions(entry, guide, scope, vertical_positions, extents)
        vertical_positions[entry.name] = positions
        v_start = _resolve_bound(entry.bottom, height, levels, extents, side="bottom")
        v_end = _resolve_bound(entry.top, height, levels, extents, side="top")
        if v_end - v_start <= TOLERANCE:
            raise FramingError(f"Vertical {entry.name!r} has no height between its bounds.")
        for u, address in positions:
            layout.verticals.append(VerticalMember(entry.name, u, v_start, v_end, address))

    for entry in horizontals:
        breakers = [m for m in layout.verticals if m.entry in entry.breaks_at]
        lo, hi = extents.get(entry.name, (0.0, 0.0))
        for row, v in enumerate(levels[entry.name]):
            # Only verticals that actually pass through this horizontal break it, so a
            # rail sitting on top of its posts stays continuous.
            row_cuts = []
            for m in breakers:
                if m.v_start < v + hi - TOLERANCE and m.v_end > v + lo + TOLERANCE:
                    m_lo, m_hi = extents.get(m.entry, (0.0, 0.0))
                    row_cuts.append((m.u + m_lo, m.u + m_hi))
            for interval, (u_start, u_end) in enumerate(_subtract_intervals(0.0, guide.length, row_cuts)):
                layout.horizontals.append(HorizontalMember(entry.name, v, u_start, u_end, (row, interval)))

    for entry in entries:
        if isinstance(entry, InfillEntry):
            layout.infills.extend(_solve_infill(entry, guide, height, levels, vertical_positions, extents))
    return layout


class _Guide:
    def __init__(self, segment_lengths: list[float], closed: bool):
        self.closed = closed
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
    return [b["member"] if isinstance(b, dict) else None for b in (e.v, e.bottom, e.top)]


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


def _solve_levels(
    horizontals: list[HorizontalEntry], height: float, extents: dict[str, tuple[float, float]]
) -> dict[str, list[float]]:
    levels: dict[str, list[float]] = {}
    for entry in horizontals:
        if entry.v is not None:
            levels[entry.name] = [_resolve_bound(entry.v, height, levels, extents, side="level")]
            continue
        assert entry.spacing and entry.bottom is not None and entry.top is not None
        start = _resolve_bound(entry.bottom, height, levels, extents, side="bottom")
        end = _resolve_bound(entry.top, height, levels, extents, side="top")
        if end - start <= TOLERANCE:
            raise FramingError(f"Horizontal {entry.name!r} has no room between its bounds.")
        levels[entry.name] = _interior_positions(start, end, entry.spacing)
    return levels


def _interior_positions(start: float, end: float, spacing: Spacing) -> list[float]:
    """Positions strictly inside ``(start, end)``, evenly spread by ``spacing``."""
    length = end - start
    if spacing.mode == "COUNT":
        n = int(spacing.value)
        return [start + length * i / (n + 1) for i in range(1, n + 1)]
    if spacing.mode == "MAX":
        n_bays = max(1, math.ceil(length / spacing.value - TOLERANCE))
        return [start + length * i / n_bays for i in range(1, n_bays)]
    # FIXED: exact spacing, with the remainder split evenly between both ends.
    n = int(math.floor(length / spacing.value + TOLERANCE))
    offset = (length - n * spacing.value) / 2
    positions = [start + offset + i * spacing.value for i in range(n + 1)]
    return [p for p in positions if start + TOLERANCE < p < end - TOLERANCE]


def _solve_vertical_positions(
    entry: VerticalEntry,
    guide: _Guide,
    scope: SpacingScope,
    solved: dict[str, list[tuple[float, tuple[int, int, int]]]],
    extents: dict[str, tuple[float, float]],
) -> list[tuple[float, tuple[int, int, int]]]:
    fixed: list[float] = []
    if entry.at_ends and not guide.closed:
        fixed += [0.0, guide.length]
    if entry.at_corners:
        fixed += guide.corners()

    # Each range is (u_start, u_end, segment, bay) that spacing fills.
    ranges: list[tuple[float, float, int, int]] = []
    if entry.within:
        parents = [u for u, _ in solved[entry.within]]
        lo, hi = extents.get(entry.within, (0.0, 0.0))
        # Bays run face to face between parent members and never across a path vertex.
        breaks = sorted(set(parents + guide.starts + [guide.length]))
        bay_counts: dict[int, int] = {}
        for a, b in zip(breaks, breaks[1:]):
            if b - a <= TOLERANCE:
                continue
            start = a + hi if _near(a, parents) else a
            end = b + lo if _near(b, parents) else b
            segment = guide.segment_at(a)
            bay = bay_counts.get(segment, 0)
            bay_counts[segment] = bay + 1
            if end - start > TOLERANCE:
                ranges.append((start, end, segment, bay))
    elif scope == "PATH":
        ranges.append((0.0, guide.length, 0, 0))
    else:
        ranges = [(s, e, i, 0) for i, (s, e) in enumerate(zip(guide.starts, guide.ends))]

    found: list[tuple[float, int, int]] = []  # (u, segment, bay)
    for u in fixed:
        found.append((u, guide.segment_at(u), 0))
    if entry.spacing:
        for start, end, segment, bay in ranges:
            for u in _interior_positions(start, end, entry.spacing):
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


def _solve_infill(
    entry: InfillEntry,
    guide: _Guide,
    height: float,
    levels: dict[str, list[float]],
    vertical_positions: dict[str, list[tuple[float, tuple[int, int, int]]]],
    extents: dict[str, tuple[float, float]],
) -> list[InfillPanel]:
    gap_left, gap_right, gap_bottom, gap_top = entry.gap
    v_start = _resolve_bound(entry.bottom, height, levels, extents, side="bottom") + gap_bottom
    v_end = _resolve_bound(entry.top, height, levels, extents, side="top") - gap_top
    if v_end - v_start <= TOLERANCE:
        raise FramingError(f"Infill {entry.name!r} has no height between its bounds.")

    members = [u for u, _ in vertical_positions.get(entry.between, [])] if entry.between else []
    lo, hi = extents.get(entry.between, (0.0, 0.0)) if entry.between else (0.0, 0.0)
    # Panels are planar, so cells always split at path vertices as well as at members.
    breaks = sorted(set(members + guide.starts + [guide.length]))
    panels: list[InfillPanel] = []
    bay_counts: dict[int, int] = {}
    for a, b in zip(breaks, breaks[1:]):
        if b - a <= TOLERANCE:
            continue
        segment = guide.segment_at(a)
        bay = bay_counts.get(segment, 0)
        bay_counts[segment] = bay + 1
        start = (a + hi if _near(a, members) else a) + gap_left
        end = (b + lo if _near(b, members) else b) - gap_right
        width = end - start
        if width <= TOLERANCE:
            continue
        n = 1
        if entry.max_width:
            n = max(1, math.ceil((width + entry.joint) / (entry.max_width + entry.joint) - TOLERANCE))
        panel_width = (width - (n - 1) * entry.joint) / n
        if panel_width <= TOLERANCE:
            raise FramingError(f"Infill {entry.name!r} joints leave no room for panels.")
        for i in range(n):
            u0 = start + i * (panel_width + entry.joint)
            panels.append(InfillPanel(entry.name, u0, u0 + panel_width, v_start, v_end, (segment, bay, i)))
    return panels
