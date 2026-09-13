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
#
# This file was generated with the assistance of an AI coding tool.

"""Post-processing pass that removes/trims same-class duplicate or overlapping
edge strokes from an already-generated drawing SVG tree (known-issues item 21).

Deliberately has no bpy/ifcopenshell dependency -- it operates purely on the
lxml tree merge_linework_and_add_metadata() has already finalised, which makes
it testable without Blender (see test/bim/module/drawing/test_svg_dedup.py).

Duplicate/overlap detection is done with plain parametric line-segment math,
not shapely boolean ops: two edges drawn by different products for the same
physical location are collinear only up to floating-point noise (each side
computes its own copy via an independent geometry path), not bit-identical.
shapely.LineString.intersection() treats two such almost-but-not-quite-
parallel segments as crossing at a single point rather than overlapping,
which silently misses real duplicates -- confirmed against a real fixture
where an earlier shapely-intersection-based version of this pass found only
2 of 20 known duplicate/overlap groups. A tolerant perpendicular-distance +
parameter-overlap test (the same approach already validated for this exact
item during its own measurement phase) does not have that failure mode.
"""

from typing import Optional

from lxml import etree

SVG_NS = "{http://www.w3.org/2000/svg}"
IFC_NS = "{http://www.ifcopenshell.org/ns}"

Point = tuple[float, float]
Segment = tuple[Point, Point]

# Collinearity/overlap tolerances, in SVG units. PARALLEL_TOL is a unitless
# cross-product-of-unit-vectors threshold (~0.06 degrees); the rest scale off
# the caller's own distance tolerance, matching the constants this session
# already validated against real drawings while quantifying this issue.
PARALLEL_TOL = 1e-3

# Safety cap on merge_duplicate_edges()'s fixed-point loop. Real drawings
# converge within 1-2 passes (verified against a real multi-thousand-edge
# fixture); this only guards against a pathological input never settling.
MAX_PASSES = 5


def merge_duplicate_edges(root, tolerance: float = 1e-3) -> None:
    """Two different elements can each independently draw their own copy of the
    same physical edge (e.g. a shared 'cross-coplanar' boundary) -- both copies
    are individually correct, but drawing both is visibly wrong once stroke
    opacity drops below 100%. Unlike merge_linework_and_add_metadata()'s own
    polygon-merge phase (which intentionally discards per-product identity for
    wall/slab cut-fill regions where the seam has no meaningful "which product"
    answer), this never builds synthetic merged geometry or touches any <g>'s
    own ifc:guid/product class -- every surviving path stays exactly where it
    was, under its own real product's own <g>, either untouched, trimmed to its
    own non-overlapping remainder, or removed outright if fully redundant. Must
    run after merge_linework_and_add_metadata(), which is what finalises each
    <g>'s own "cut"/"projection" class labelling.

    Trimming one cluster can occasionally reveal a *new* overlap between two
    other members' own leftover remainders (each was only tested against its
    original, untrimmed extent) -- so this iterates to a fixed point rather
    than doing a single pass, capped defensively since real drawings converge
    within one or two passes in practice.

    Known-issues item 55: passes a "dirty" set of (class, cut-or-projection)
    bucket keys from each pass into the next, so later passes only re-parse
    and re-cluster buckets that actually changed -- a bucket's own trimming
    can only ever reveal a new overlap within that SAME bucket (buckets are
    entirely disjoint by class/group), never in a different one, so an
    unchanged bucket is guaranteed identical on every later pass regardless.
    """
    dirty_keys = None  # None means "examine every bucket" -- only true on pass 1.
    for _ in range(MAX_PASSES):
        dirty_keys = _run_one_pass(root, tolerance, dirty_keys)
        if not dirty_keys:
            return


def _cut_or_projection(path: "etree._Element") -> Optional[str]:
    """Which of the two `<g>` group kinds `merge_linework_and_add_metadata()`
    labels a product's own linework with (known-issues item 52) `path`'s
    parent belongs to, if either. `operator.py`'s SHAPELY fill-boundary scan
    only ever looks at `"projection"`-classed groups, so a duplicate pair
    spanning one product's `"cut"` copy and another's `"projection"` copy of
    the same boundary edge must never let the cut-side copy (kept as
    survivor purely because it happens to be longer) delete the
    projection-side copy that scan actually depends on. Returns `None` for
    anything not carrying either label -- such paths keep clustering
    together as before, this distinction only matters between the two.
    """
    parent = path.getparent()
    if parent is None:
        return None
    classes = parent.get("class", "").split()
    if "cut" in classes:
        return "cut"
    if "projection" in classes:
        return "projection"
    return None


def _run_one_pass(
    root, tolerance: float, only_keys: Optional[set[tuple[str, Optional[str]]]] = None
) -> set[tuple[str, Optional[str]]]:
    """Runs one class-grouped cluster/trim pass, restricted to `only_keys`'s
    (class, cut-or-projection) buckets when given (`None` = every bucket).
    Returns the set of bucket keys that actually changed, so the caller can
    restrict the next pass to just those (known-issues item 55)."""
    paths_by_class: dict[tuple[str, Optional[str]], list[tuple[etree._Element, Segment]]] = {}
    for path in root.findall(f".//{SVG_NS}g[@{IFC_NS}guid]/{SVG_NS}path"):
        cls = path.get("class")
        d = path.get("d")
        if not cls or not d:
            continue
        # Known-issues item 52: scoped to (class, cut-or-projection) rather than
        # class alone, so a "cut"-side and "projection"-side copy of what looks
        # like the same edge never cluster together and risk the wrong one
        # surviving -- see _cut_or_projection()'s own comment.
        key = (cls, _cut_or_projection(path))
        if only_keys is not None and key not in only_keys:
            continue
        seg = _edge_path_d_to_segment(d)
        if seg is None or _length(seg) < tolerance:
            continue
        paths_by_class.setdefault(key, []).append((path, seg))

    changed_keys: set[tuple[str, Optional[str]]] = set()

    for key, entries in paths_by_class.items():
        n = len(entries)
        if n < 2:
            continue

        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for i in range(n):
            for j in range(i + 1, n):
                if _collinear_overlap(entries[i][1], entries[j][1], tolerance) is not None:
                    ri, rj = find(i), find(j)
                    if ri != rj:
                        parent[ri] = rj

        clusters: dict[int, list[int]] = {}
        for i in range(n):
            clusters.setdefault(find(i), []).append(i)

        for members in clusters.values():
            if len(members) < 2:
                continue
            _resolve_cluster([entries[i] for i in members], tolerance)
            changed_keys.add(key)

    return changed_keys


def _resolve_cluster(members: list[tuple["etree._Element", Segment]], tolerance: float) -> None:
    """Keeps the longest member's own <path> whole as the survivor; every other
    member is trimmed down to whatever portion of its own extent (projected
    onto the survivor's own direction) isn't already covered by the survivor
    or an earlier-processed member -- so overlaps spanning more than two paths
    still converge to a minimal, non-overlapping cover.
    """
    members = sorted(members, key=lambda m: _length(m[1]), reverse=True)
    survivor_path, survivor_seg = members[0]
    origin, direction, survivor_len = _origin_direction_length(survivor_seg)

    covered = _merge_intervals([(0.0, survivor_len)])

    for path, seg in members[1:]:
        t0 = _project(seg[0], origin, direction)
        t1 = _project(seg[1], origin, direction)
        lo, hi = (t0, t1) if t0 <= t1 else (t1, t0)

        remainder_intervals = _subtract_intervals(lo, hi, covered, tolerance)
        _set_or_split_edge_path(path, origin, direction, remainder_intervals)
        covered = _merge_intervals(covered + [(lo, hi)])


def _edge_path_d_to_segment(d: str) -> Optional[Segment]:
    """Parses this pipeline's own simple "M x,y L x,y" edge-path convention (the
    only shape a classified edge <path> takes -- unlike the closed multi-subpath
    polygons merge_linework_and_add_metadata()'s own polygon phase parses).
    Returns None for anything else, conservatively.
    """
    tokens = d.replace("M", "").replace("L", "").strip().split()
    if len(tokens) != 2:
        return None
    try:
        p0 = tuple(float(v) for v in tokens[0].split(","))
        p1 = tuple(float(v) for v in tokens[1].split(","))
    except ValueError:
        return None
    if len(p0) != 2 or len(p1) != 2:
        return None
    return (p0, p1)


def _length(seg: Segment) -> float:
    (x0, y0), (x1, y1) = seg
    return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5


def _origin_direction_length(seg: Segment) -> tuple[Point, Point, float]:
    (x0, y0), (x1, y1) = seg
    length = _length(seg)
    return (x0, y0), ((x1 - x0) / length, (y1 - y0) / length), length


def _project(p: Point, origin: Point, direction: Point) -> float:
    return (p[0] - origin[0]) * direction[0] + (p[1] - origin[1]) * direction[1]


def _collinear_overlap(seg_a: Segment, seg_b: Segment, tolerance: float) -> Optional[tuple[float, float]]:
    """Returns seg_b's overlapping parameter interval in seg_a's own frame if
    the two segments are collinear (within PARALLEL_TOL) and their extents
    genuinely overlap; None otherwise (including for lines that merely cross,
    which intersect at a single point/zero-length overlap, not a shared run).

    Two independently-computed copies of the same physical edge are collinear
    only up to floating-point noise from each side's own geometry path, not
    bit-identical -- confirmed against a real fixture to differ by several
    thousandths of an SVG unit even for edges that are visually and
    semantically exact duplicates. The perpendicular-distance and overlap-
    length bands are widened to 5x the base tolerance (matching this same
    item's own already-validated measurement methodology) so genuine
    duplicates aren't missed just because `tolerance` itself is drawn tight
    enough to matter for the *trimmed remainder* geometry this function's
    caller goes on to emit.
    """
    band = tolerance * 5
    len_a = _length(seg_a)
    len_b = _length(seg_b)
    if len_a < tolerance or len_b < tolerance:
        return None

    origin, direction, _ = _origin_direction_length(seg_a)
    _, direction_b, _ = _origin_direction_length(seg_b)

    cross = direction[0] * direction_b[1] - direction[1] * direction_b[0]
    if abs(cross) > PARALLEL_TOL:
        return None

    to_b0 = (seg_b[0][0] - origin[0], seg_b[0][1] - origin[1])
    perp_dist = abs(to_b0[0] * direction[1] - to_b0[1] * direction[0])
    if perp_dist > band:
        return None

    t0 = _project(seg_b[0], origin, direction)
    t1 = _project(seg_b[1], origin, direction)
    lo, hi = (t0, t1) if t0 <= t1 else (t1, t0)

    overlap_lo = max(lo, 0.0)
    overlap_hi = min(hi, len_a)
    if overlap_hi - overlap_lo <= band:
        return None
    return (overlap_lo, overlap_hi)


def _merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    merged: list[tuple[float, float]] = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged


def _subtract_intervals(
    lo: float, hi: float, covered: list[tuple[float, float]], tolerance: float
) -> list[tuple[float, float]]:
    remaining = [(lo, hi)]
    for clo, chi in covered:
        next_remaining = []
        for rlo, rhi in remaining:
            if chi <= rlo or clo >= rhi:
                next_remaining.append((rlo, rhi))
                continue
            if clo > rlo:
                next_remaining.append((rlo, clo))
            if chi < rhi:
                next_remaining.append((chi, rhi))
        remaining = next_remaining
    return [(a, b) for a, b in remaining if (b - a) > tolerance]


def _set_or_split_edge_path(
    path: "etree._Element", origin: Point, direction: Point, remainder_intervals: list[tuple[float, float]]
) -> None:
    """Replaces a classified edge <path>'s geometry with its (possibly
    discontinuous) remainder after trimming away a duplicate/overlapping
    portion. Removes the <path> outright if nothing of meaningful length
    survives. A remainder split into multiple disjoint pieces becomes multiple
    sibling <path> elements (same class, same parent <g>) rather than one
    multi-subpath path, keeping the "one path = one simple line segment"
    invariant the rest of this pipeline relies on.
    """
    if not remainder_intervals:
        path.getparent().remove(path)
        return

    def point_at(t: float) -> Point:
        return (origin[0] + direction[0] * t, origin[1] + direction[1] * t)

    (first_lo, first_hi), *rest = remainder_intervals
    p0, p1 = point_at(first_lo), point_at(first_hi)
    path.set("d", f"M{p0[0]},{p0[1]} L{p1[0]},{p1[1]}")

    parent = path.getparent()
    index = list(parent).index(path)
    for offset, (lo, hi) in enumerate(rest, start=1):
        p0, p1 = point_at(lo), point_at(hi)
        # Known-issues item 53: namespaced, matching every other <path> this pipeline
        # writes/reads (e.g. this module's own root.findall(f".//{SVG_NS}g[...]/{SVG_NS}path")
        # above) -- an unnamespaced element is invisible to that same query on the same
        # in-memory tree, defeating both this loop's own fixed-point convergence and the
        # SHAPELY boundary scan (item 52) if either ever walks past a sibling created here.
        sibling = etree.Element(f"{SVG_NS}path")
        sibling.set("class", path.get("class"))
        sibling.set("d", f"M{p0[0]},{p0[1]} L{p1[0]},{p1[1]}")
        parent.insert(index + offset, sibling)
