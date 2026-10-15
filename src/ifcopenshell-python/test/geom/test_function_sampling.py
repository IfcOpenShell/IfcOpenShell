# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Thomas Krijnen <thomas@aecgeeks.com>
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

"""Tests for how alignment curves, and the sweeps and lofts along them, are sampled (IfcOpenShell#5360).

Curves are sampled at every segment boundary and between them within mesher-linear-deflection and
mesher-angular-deflection, so straights need only their ends. Sweeps and lofts place sections the
same way, keeping their profiles within the deflection of the true surface.

The fixture has alignments with arcs, clothoid spirals, a gradient curve, cant, a polyline, an offset
curve, a tight (R 10) and a gentle (R 5000) arc, Viennese bends, a tight vertical curve, and a straight
with a linear cant transition. Along them: a swept solid; sectioned solids with a constant profile, a
taper and a sideways shift; a sectioned surface of tagged open profiles; a sweep that rolls with cant;
and a sweep and a loft around the tight arc. True section positions are computed here from the
directrix frame and the rectangle profiles.

Run this file directly to print point and section counts, errors and timings.
"""

import time
from pathlib import Path

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.geom
import ifcopenshell.util.shape
from ifcopenshell import ifcopenshell_wrapper

FIXTURE = Path(__file__).parent.parent / "fixtures/geom/function_sampling.ifc"
CURVES = [
    "H arcs",
    "H spirals",
    "Gradient",
    "Cant",
    "Polyline",
    "Offset",
    "Tight",
    "Gentle",
    "Viennese",
    "Tight vertical",
    "Canted",
]
STRAIGHT_AXES = ["Polyline", "Canted"]  # no curvature: only their boundaries at any deflection
SWEEPS = ["Swept", "Constant", "Taper", "Shifted", "Rolling sweep", "Tight sweep", "Tight loft"]
LINEAR = 0.001  # the default mesher-linear-deflection
ANGULAR = 0.5  # the default mesher-angular-deflection
SLACK = 1.05  # errors are measured at sample points, not exactly at their maximum
# The fixture's geometric segments agree with its layouts' design parameters to about 2e-6, so
# positions taken from the layouts are compared with this tolerance
TOLERANCE = 1e-5
REFERENCE_STEP = 0.05  # spacing of the dense evaluation used as the true curve


@pytest.fixture(scope="module")
def ifc_file():
    return ifcopenshell.open(FIXTURE)


def settings(linear=LINEAR, angular=ANGULAR) -> ifcopenshell.geom.settings:
    s = ifcopenshell.geom.settings()
    s.set("mesher-linear-deflection", linear)
    s.set("mesher-angular-deflection", angular)
    return s


def unit(v):
    return v / np.linalg.norm(v)


# Curves and their layouts


def get_alignment(ifc_file, name):
    return next(a for a in ifc_file.by_type("IfcAlignment") if a.Name == name)


def get_curve(alignment):
    if alignment.Name in ("Polyline", "Offset"):
        return alignment.Representation.Representations[0].Items[0]
    return ifcopenshell.api.alignment.get_curve(alignment)


def get_evaluator(curve, s=None):
    s = s or settings()
    fn = ifcopenshell_wrapper.map_shape(s, curve)
    if isinstance(fn, ifcopenshell_wrapper.loop):
        fn = ifcopenshell_wrapper.convert_loop_to_function_item(fn)
    return ifcopenshell_wrapper.function_item_evaluator(s, fn)


def layout_segments(layout):
    return [s.DesignParameters for s in layout.IsNestedBy[0].RelatedObjects] if layout else []


def horizontal_spans(alignment):
    """(start, end, is_straight) for each horizontal segment, in distance along"""
    spans, start = [], 0.0
    for p in layout_segments(ifcopenshell.api.alignment.get_horizontal_layout(alignment)):
        spans.append((start, start + p.SegmentLength, p.PredefinedType == "LINE"))
        start += p.SegmentLength
    return spans


def vertical_spans(alignment):
    return [
        (p.StartDistAlong, p.StartDistAlong + p.HorizontalLength, p.PredefinedType == "CONSTANTGRADIENT")
        for p in layout_segments(ifcopenshell.api.alignment.get_vertical_layout(alignment))
    ]


def cant_spans(alignment):
    def is_constant(p):
        left = p.EndCantLeft if p.EndCantLeft is not None else p.StartCantLeft
        right = p.EndCantRight if p.EndCantRight is not None else p.StartCantRight
        return p.PredefinedType == "CONSTANTCANT" and left == p.StartCantLeft and right == p.StartCantRight

    return [
        (p.StartDistAlong, p.StartDistAlong + p.HorizontalLength, is_constant(p))
        for p in layout_segments(ifcopenshell.api.alignment.get_cant_layout(alignment))
    ]


def polyline_spans(polyline):
    points = np.array([p.Coordinates for p in polyline.Points])
    lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
    starts = np.concatenate([[0.0], np.cumsum(lengths)])
    return [(starts[i], starts[i + 1], True) for i in range(len(lengths))]


def offset_spans(offset_curve, end):
    distances = [v.DistanceAlong.wrappedValue for v in offset_curve.OffsetValues]
    # offsets are interpolated linearly, then held constant to the end of the basis curve, so they
    # never make a straight basis curve bend
    return [(a, b, True) for a, b in zip(distances, distances[1:] + [end]) if b > a]


def component_spans(ifc_file, alignment) -> list[list[tuple[float, float, bool]]]:
    """Span lists of every function that makes up the alignment's curve"""
    if alignment.Name == "Polyline":
        return [polyline_spans(get_curve(alignment))]
    if alignment.Name == "Offset":
        basis = component_spans(ifc_file, get_alignment(ifc_file, "Gradient"))
        return basis + [offset_spans(get_curve(alignment), basis[0][-1][1])]
    spans = [horizontal_spans(alignment)]
    if ifcopenshell.api.alignment.get_vertical_layout(alignment):
        spans.append(vertical_spans(alignment))
    if ifcopenshell.api.alignment.get_cant_layout(alignment):
        spans.append(cant_spans(alignment))
    return [s for s in spans if s]


def segment_boundaries(ifc_file, alignment) -> list[float]:
    return sorted({b for spans in component_spans(ifc_file, alignment) for s in spans for b in s[:2]})


def is_straight(ifc_file, alignment, u0: float, u1: float) -> bool:
    """True when u0..u1 lies, for every component, within one straight span"""
    for spans in component_spans(ifc_file, alignment):
        if not any(s - TOLERANCE <= u0 and u1 <= e + TOLERANCE and straight for s, e, straight in spans):
            return False
    return True


def position(evaluator, u):
    return np.array(evaluator.evaluate(u))[:3, 3]


def chord_error(evaluator, points) -> float:
    """Largest distance between the curve and the polyline through its evaluated points"""
    vertices = np.array([position(evaluator, u) for u in points])
    reference_u = np.arange(points[0], points[-1], REFERENCE_STEP)
    reference = np.array([position(evaluator, u) for u in reference_u])
    index = np.clip(np.searchsorted(points, reference_u, side="right") - 1, 0, len(points) - 2)
    a, b = vertices[index], vertices[index + 1]
    ab = b - a
    t = np.clip(np.einsum("ij,ij->i", reference - a, ab) / np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-24), 0, 1)
    return float(np.max(np.linalg.norm(reference - (a + t[:, None] * ab), axis=1)))


def turning_angles(evaluator, points):
    """How far the curve turns within each interval between points, measured just inside its ends
    so that a kink at a point (a polyline corner) doesn't count"""
    angles = []
    for u0, u1 in zip(points, points[1:]):
        e = min(1e-3, (u1 - u0) / 4)
        t0 = unit(position(evaluator, u0 + e) - position(evaluator, u0))
        t1 = unit(position(evaluator, u1) - position(evaluator, u1 - e))
        angles.append(np.arccos(np.clip(np.dot(t0, t1), -1, 1)))
    return np.array(angles)


# Sweeps, lofts and the surface


def get_item(ifc_file, name):
    proxy = next(p for p in ifc_file.by_type("IfcBuildingElementProxy") if p.Name == name)
    return proxy.Representation.Representations[0].Items[0]


def stations(item) -> list[tuple[float, float, ifcopenshell.entity_instance]]:
    """(distance along, lateral offset, profile) of each authored cross section"""
    return [
        (p.Location.DistanceAlong.wrappedValue, p.Location.OffsetLateral or 0.0, profile)
        for p, profile in zip(item.CrossSectionPositions, item.CrossSections)
    ]


def section_origins(item, s=None) -> np.ndarray:
    s = s or settings()
    if item.is_a("IfcSectionedSurface"):
        # The wrapper doesn't expose the matrix of a loop. The "Tagged" surface lies on the first
        # straight, along the X axis, with its "C" tag on the directrix, so its sections are the
        # mesh vertices with y = 0.
        verts = np.array(ifcopenshell.geom.create_shape(s, item).verts).reshape(-1, 3)
        on_directrix = verts[np.abs(verts[:, 1]) < 1e-6]
        return on_directrix[np.unique(np.round(on_directrix[:, 0], 6), return_index=True)[1]]
    loft = ifcopenshell_wrapper.map_shape(s, item)
    return np.array([np.array(child.matrix.components)[:3, 3] for child in loft.children])


class CurveLocator:
    """Finds the distance along the directrix of points on it"""

    def __init__(self, item):
        self.evaluator = get_evaluator(item.Directrix)
        points = self.evaluator.evaluation_points()
        self.u = np.arange(points[0], points[-1], REFERENCE_STEP)
        self.positions = np.array([position(self.evaluator, u) for u in self.u])

    def locate(self, point) -> float:
        u = self.u[np.argmin(np.linalg.norm(self.positions - point, axis=1))]
        for _ in range(3):
            d = position(self.evaluator, u + 1e-3) - position(self.evaluator, u)
            u += float(np.dot(point - position(self.evaluator, u), d) / np.dot(d, d)) * 1e-3
        return u

    def section_u(self, item, s=None) -> list[float]:
        return sorted(self.locate(p) for p in section_origins(item, s))


def is_constant_straight(ifc_file, item, u0, u1) -> bool:
    """True when u0..u1 is on a straight, non-rotating part of the directrix and between two authored
    cross sections that differ at most by their offset, so the loft is exact without sections between"""
    authored = stations(item)
    for (a, _, profile_a), (b, _, profile_b) in zip(authored, authored[1:]):
        if a - TOLERANCE <= u0 and u1 <= b + TOLERANCE:
            return profile_a == profile_b and is_straight(ifc_file, get_alignment(ifc_file, "Gradient"), u0, u1)
    return False


def true_corners(item, locator, u):
    """World positions of the rectangle profile's corners where the section at u should be"""
    m = np.array(locator.evaluator.evaluate(u))
    origin, tangent, lateral, up = m[:3, 3], unit(m[:3, 0]), unit(m[:3, 1]), unit(m[:3, 2])
    offset = 0.0
    if item.is_a("IfcSectionedSolidHorizontal"):
        authored = stations(item)
        distances = [a[0] for a in authored]
        width = np.interp(u, distances, [a[2].XDim for a in authored])
        height = authored[0][2].YDim
        offset = np.interp(u, distances, [a[1] for a in authored])
        x_axis, y_axis = lateral, up
    else:
        width, height = item.SweptArea.XDim, item.SweptArea.YDim
        if item.is_a("IfcDirectrixDerivedReferenceSweptAreaSolid"):
            x_axis, y_axis = lateral, unit(np.cross(tangent, lateral))
        else:
            reference = np.array(item.FixedReference.DirectionRatios)
            x_axis = unit(reference - tangent * np.dot(tangent, reference))
            y_axis = np.cross(x_axis, tangent)
    corners = [(-width / 2, -height / 2), (width / 2, -height / 2), (width / 2, height / 2), (-width / 2, height / 2)]
    return np.array([origin + x_axis * (x + offset) + y_axis * y for x, y in corners])


def section_errors(item):
    """Largest corner path deviation and face twist between consecutive sections, and their count"""
    locator = CurveLocator(item)
    section_u = locator.section_u(item)
    path, twist = 0.0, 0.0
    for u0, u1 in zip(section_u, section_u[1:]):
        a, b = true_corners(item, locator, u0), true_corners(item, locator, u1)
        for t in (0.25, 0.5, 0.75):
            p = true_corners(item, locator, u0 + t * (u1 - u0))
            ab = b - a
            k = np.clip(np.einsum("ij,ij->i", p - a, ab) / np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-24), 0, 1)
            path = max(path, float(np.max(np.linalg.norm(p - (a + k[:, None] * ab), axis=1))))
        for i in range(4):
            j = (i + 1) % 4
            normal = np.cross(a[j] - a[i], b[i] - a[i])
            if np.linalg.norm(normal) > 1e-12:
                twist = max(twist, abs(np.dot(a[i] - a[j] - b[i] + b[j], unit(normal))) / 4)
    return path, twist, len(section_u)


def expected_measure(item, locator) -> float:
    """Volume of a rectangle sweep, or area of a flat open profile sweep, by integrating the
    (interpolated) cross section along the directrix"""
    if item.is_a("IfcSweptAreaSolid"):
        points = locator.evaluator.evaluation_points()
        distances, measures = [points[0], points[-1]], [item.SweptArea.XDim * item.SweptArea.YDim] * 2
    else:
        authored = stations(item)
        distances = [a[0] for a in authored]
        if item.is_a("IfcSectionedSurface"):
            measures = [sum(profile.Widths) for _, _, profile in authored]
        else:
            measures = [profile.XDim * profile.YDim for _, _, profile in authored]
    u = np.append(np.arange(distances[0], distances[-1], REFERENCE_STEP), distances[-1])
    measure = np.interp(u, distances, measures)
    p = np.array([position(locator.evaluator, x) for x in u])
    dl = np.linalg.norm(np.diff(p, axis=0), axis=1)
    return float(np.sum(dl * (measure[:-1] + measure[1:]) / 2))


# Curve tests


@pytest.mark.parametrize("name", CURVES)
def test_curve_ends_are_evaluated(ifc_file, name):
    alignment = get_alignment(ifc_file, name)
    points = get_evaluator(get_curve(alignment)).evaluation_points()
    boundaries = segment_boundaries(ifc_file, alignment)
    assert points[0] == pytest.approx(boundaries[0], abs=TOLERANCE)
    assert points[-1] == pytest.approx(boundaries[-1], abs=TOLERANCE)


@pytest.mark.parametrize("name", CURVES)
def test_curve_points_increase(ifc_file, name):
    points = get_evaluator(get_curve(get_alignment(ifc_file, name))).evaluation_points()
    assert all(b > a for a, b in zip(points, points[1:]))


@pytest.mark.parametrize("name", CURVES)
def test_segment_boundaries_are_evaluated(ifc_file, name):
    alignment = get_alignment(ifc_file, name)
    points = np.array(get_evaluator(get_curve(alignment)).evaluation_points())
    missing = [b for b in segment_boundaries(ifc_file, alignment) if np.min(np.abs(points - b)) > TOLERANCE]
    assert not missing, f"boundaries not evaluated: {missing}"


@pytest.mark.parametrize("name", CURVES)
def test_straights_are_only_evaluated_at_their_ends(ifc_file, name):
    alignment = get_alignment(ifc_file, name)
    points = get_evaluator(get_curve(alignment)).evaluation_points()
    boundaries = np.array(segment_boundaries(ifc_file, alignment))
    for u in points[1:-1]:
        if np.min(np.abs(boundaries - u)) > TOLERANCE:
            assert not is_straight(ifc_file, alignment, u - 1e-3, u + 1e-3), f"{u:.3f} is inside a straight"


@pytest.mark.parametrize("name", CURVES)
def test_curve_within_linear_deflection(ifc_file, name):
    evaluator = get_evaluator(get_curve(get_alignment(ifc_file, name)))
    assert chord_error(evaluator, evaluator.evaluation_points()) <= LINEAR * SLACK


@pytest.mark.parametrize("name", CURVES)
def test_curve_within_angular_deflection(ifc_file, name):
    evaluator = get_evaluator(get_curve(get_alignment(ifc_file, name)))
    assert np.max(turning_angles(evaluator, evaluator.evaluation_points())) <= ANGULAR * SLACK


@pytest.mark.parametrize("name", [n for n in CURVES if n not in STRAIGHT_AXES])
def test_coarser_deflection_gives_fewer_points_within_it(ifc_file, name):
    curve = get_curve(get_alignment(ifc_file, name))
    fine = get_evaluator(curve, settings(linear=0.001))
    coarse = get_evaluator(curve, settings(linear=0.01))
    assert len(coarse.evaluation_points()) < len(fine.evaluation_points())
    assert chord_error(coarse, coarse.evaluation_points()) <= 0.01 * SLACK


@pytest.mark.parametrize("name,radius", [("Tight", 10.0), ("Gentle", 5000.0)])
def test_steps_follow_the_radius(ifc_file, name, radius):
    # A chord of length s on radius R deviates s^2 / (8 R), so the arc needs at least L / sqrt(8 R d)
    # steps. Bisection can halve a step more than strictly needed, so allow up to twice that, plus the
    # straights.
    alignment = get_alignment(ifc_file, name)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    arc = next(p.SegmentLength for p in layout_segments(horizontal) if p.PredefinedType == "CIRCULARARC")
    ideal = arc / np.sqrt(8 * radius * LINEAR)
    assert ideal <= len(get_evaluator(get_curve(alignment)).evaluation_points()) <= 2 * ideal + 4


# Sweep, loft and surface tests


# Every point of the surface is within the linear deflection of the true surface, so the volume (or,
# for a surface, the area) is within that times the surface area. The path and face tests below are
# the strict checks; these ones catch sections that are missing or misplaced altogether.


@pytest.mark.parametrize("name", SWEEPS)
def test_volume(ifc_file, name):
    item = get_item(ifc_file, name)
    shape = ifcopenshell.geom.create_shape(settings(), item)
    error = ifcopenshell.util.shape.get_volume(shape) - expected_measure(item, CurveLocator(item))
    assert abs(error) <= LINEAR * ifcopenshell.util.shape.get_area(shape)


def test_surface_area(ifc_file):
    item = get_item(ifc_file, "Tagged")
    shape = ifcopenshell.geom.create_shape(settings(), item)
    # flat profiles on a straight: the surface is exact
    assert ifcopenshell.util.shape.get_area(shape) == pytest.approx(
        expected_measure(item, CurveLocator(item)), rel=1e-9
    )


@pytest.mark.parametrize("name", ["Taper", "Tagged"])  # the others have authored sections only at their ends
def test_authored_sections_are_placed(ifc_file, name):
    item = get_item(ifc_file, name)
    locator = CurveLocator(item)
    origins = section_origins(item)
    missing = [
        d
        for d, _, _ in stations(item)
        if np.min(np.linalg.norm(origins - position(locator.evaluator, d), axis=1)) > TOLERANCE
    ]
    assert not missing, f"authored stations without a section: {missing}"


@pytest.mark.parametrize("name", ["Constant", "Taper", "Shifted", "Tagged"])
def test_constant_straights_are_lofted_from_their_ends(ifc_file, name):
    item = get_item(ifc_file, name)
    for u in CurveLocator(item).section_u(item):
        assert not is_constant_straight(ifc_file, item, u - 1e-2, u + 1e-2), f"section at {u:.3f}"


@pytest.mark.parametrize("name", SWEEPS)
def test_section_paths_within_linear_deflection(ifc_file, name):
    path, _, _ = section_errors(get_item(ifc_file, name))
    assert path <= LINEAR * SLACK


@pytest.mark.parametrize("name", SWEEPS)
def test_section_faces_within_linear_deflection_of_flat(ifc_file, name):
    _, twist, _ = section_errors(get_item(ifc_file, name))
    assert twist <= LINEAR * SLACK


if __name__ == "__main__":
    f = ifcopenshell.open(FIXTURE)
    print(f"{'curve':16s} {'points':>7s} {'chord err':>10s} {'max turn':>9s} {'time ms':>8s}")
    for name in CURVES:
        start = time.perf_counter()
        evaluator = get_evaluator(get_curve(get_alignment(f, name)))
        points = evaluator.evaluation_points()
        elapsed = (time.perf_counter() - start) * 1000
        print(
            f"{name:16s} {len(points):7d} {chord_error(evaluator, points):10.2e} "
            f"{np.max(turning_angles(evaluator, points)):9.4f} {elapsed:8.0f}"
        )
    print(
        f"\n{'item':16s} {'sections':>8s} {'path err':>10s} {'twist':>10s} {'measure':>12s} {'expected':>12s} {'time ms':>8s}"
    )
    for name in SWEEPS + ["Tagged"]:
        item = get_item(f, name)
        start = time.perf_counter()
        shape = ifcopenshell.geom.create_shape(settings(), item)
        elapsed = (time.perf_counter() - start) * 1000
        locator = CurveLocator(item)
        if item.is_a("IfcSectionedSurface"):
            path, twist, count = float("nan"), float("nan"), len(section_origins(item))
            measure = ifcopenshell.util.shape.get_area(shape)
        else:
            path, twist, count = section_errors(item)
            measure = ifcopenshell.util.shape.get_volume(shape)
        print(
            f"{name:16s} {count:8d} {path:10.2e} {twist:10.2e} {measure:12.4f} "
            f"{expected_measure(item, locator):12.4f} {elapsed:8.0f}"
        )
