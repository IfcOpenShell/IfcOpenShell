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


class FramingError(ValueError):
    pass


@dataclass(frozen=True)
class Spacing:
    mode: SpacingMode
    value: float
    # Where FIXED spacing is measured from: the start of each range, its end, or
    # centred with the remainder split between both ends.
    align: SpacingAlign = "CENTER"

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
        align = data.get("align", "CENTER")
        if align not in ("START", "CENTER", "END"):
            raise FramingError(f"Entry {entry_name!r} has unknown spacing alignment {align!r}.")
        return cls(mode, float(value), align)


@dataclass(frozen=True)
class VerticalEntry:
    name: str
    spacing: Optional[Spacing]
    bottom: Bound
    top: Bound
    at_ends: bool = False
    at_corners: bool = False
    within: Optional[str] = None
    # Which of the bays to fill, counted from 1 along the path; negatives count from
    # the end. Empty means all.
    bays: tuple[int, ...] = ()
    # Cut into pieces at the faces of these horizontal entries' rows, where they cross.
    breaks_at: tuple[str, ...] = ()


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


Entry = Union[VerticalEntry, HorizontalEntry, InfillEntry]


@dataclass(frozen=True)
class VerticalMember:
    entry: str
    u: float
    v_start: float
    v_end: float
    # (segment, bay, index): bay is the parent bay for ``within`` arrays, else 0.
    address: tuple[int, int, int]
    # Counts the pieces upward when the member breaks at horizontals.
    piece: int = 0


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
    # (segment, bay, row, panel): row counts gaps upwards, panel counts max_width splits.
    address: tuple[int, int, int, int]


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
            bays=_parse_selection(item.get("bays"), name, "bays"),
            breaks_at=tuple(item.get("breaks_at", ())),
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
        if kind is HorizontalEntry and target.v is None and not allow_repeating:
            raise FramingError(f"Entry {owner!r} cannot use repeating horizontal {ref!r} as {role}.")

    def bound_ref(bound: Optional[Bound]) -> Optional[str]:
        return bound["member"] if isinstance(bound, dict) else None

    for e in entries:
        if isinstance(e, VerticalEntry):
            expect(e.within, VerticalEntry, e.name, "'within'")
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
    _topological_order([e for e in entries if isinstance(e, VerticalEntry)], lambda e: [e.within])
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
    for name in vertical_positions:
        kept = {m.u for m in layout.verticals if m.entry == name}
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

    # Verticals that break at horizontals are cut at the faces of the rows that cross
    # them, where those rows actually run.
    breaks_by_entry = {e.name: e.breaks_at for e in verticals if e.breaks_at}
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

    for entry in entries:
        if isinstance(entry, InfillEntry):
            layout.infills.extend(
                _solve_infill(
                    entry, guide, height, levels, vertical_positions, layout.verticals, layout.horizontals, extents
                )
            )
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
        if entry.v is not None:
            levels[entry.name] = [_resolve_bound(entry.v, height, levels, extents, side="level")]
            continue
        assert entry.spacing and entry.bottom is not None and entry.top is not None
        start, end = _resolve_bounds(entry.name, entry.bottom, entry.top, height, levels, extents)
        if end - start <= TOLERANCE:
            raise FramingError(f"Horizontal {entry.name!r} has no room between its bounds.")
        gaps = [(start, end)]
        if entry.within:
            lo, hi = extents.get(entry.within, (0.0, 0.0))
            gaps = _subtract_intervals(start, end, [(v + lo, v + hi) for v in levels[entry.within]])
        levels[entry.name] = [v for a, b in _select(gaps, entry.rows) for v in _interior_positions(a, b, entry.spacing)]
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
    # FIXED: exact spacing, measured from the start, the end, or with the remainder
    # split evenly between both ends.
    n = int(math.floor(length / spacing.value + TOLERANCE))
    remainder = length - n * spacing.value
    offset = {"START": 0.0, "CENTER": remainder / 2, "END": remainder}[spacing.align]
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
    ranges = _select(ranges, entry.bays)

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
