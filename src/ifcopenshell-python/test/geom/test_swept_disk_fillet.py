# This file was generated with the assistance of an AI coding tool.

"""IfcSweptDiskSolidPolygonal.FilletRadius on the mapped directrix.

Each case maps a swept disk with ``map_shape`` and reads the directrix loop back. A filleted corner is a
circular edge of the FilletRadius in SI units whose tangent points lie ``r / tan(angle / 2)`` from the
corner on both legs, with the circle centre at the fillet radius from both. The JSON log reports how many
corners were skipped because the radius exceeds what their legs can take: the full length of an end leg
and half the length of an inner leg.
"""

import json
import math

import numpy as np
import pytest

import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
from ifcopenshell import ifcopenshell_wrapper

DISK_RADIUS = 0.05
SKIPPED_CODE = "GEO330"


def swept_disk(points, fillet, unit="METERS", closed=False):
    """The file is returned too: the item dies with it."""
    f = ifcopenshell.api.project.create_file(version="IFC4")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(f, length={"is_metric": True, "raw": unit})
    pts = [f.createIfcCartesianPoint([float(c) for c in p] + [0.0] * (3 - len(p))) for p in points]
    if closed:
        pts.append(pts[0])
    item = f.createIfcSweptDiskSolidPolygonal(f.createIfcPolyline(pts), DISK_RADIUS, None, None, None, fillet)
    return f, item


def map_directrix(disk):
    f, item = disk
    """The mapped directrix loop and the number of corners the log says were skipped."""
    ifcopenshell_wrapper.set_log_format_json()
    try:
        sweep = ifcopenshell_wrapper.map_shape(ifcopenshell.geom.settings(), item)
        messages = [json.loads(line) for line in ifcopenshell_wrapper.get_log().splitlines() if line.strip()]
    finally:
        ifcopenshell_wrapper.set_log_format_text()
    skipped = sum(int(m["message"].split()[1]) for m in messages if m.get("code") == SKIPPED_CODE)
    return sweep.curve, skipped


def arcs(loop):
    return [e for e in loop.children if isinstance(e.basis, ifcopenshell_wrapper.circle)]


def point(vertex):
    return np.array(vertex.components)


def assert_fillet(previous, arc, following, corner, radius):
    """``previous`` and ``following`` are the straight legs meeting at ``corner`` before the fillet."""
    corner = np.array(corner, dtype=float)
    leg_in = point(previous.start) - corner
    leg_out = point(following.end) - corner
    angle = math.acos(np.dot(leg_in, leg_out) / np.linalg.norm(leg_in) / np.linalg.norm(leg_out))
    inset = radius / math.tan(angle / 2.0)
    t0 = corner + leg_in / np.linalg.norm(leg_in) * inset
    t1 = corner + leg_out / np.linalg.norm(leg_out) * inset
    assert point(previous.end) == pytest.approx(t0)
    assert point(arc.start) == pytest.approx(t0)
    assert point(arc.end) == pytest.approx(t1)
    assert point(following.start) == pytest.approx(t1)
    assert arc.basis.radius == pytest.approx(radius)
    centre = np.array(arc.basis.matrix.components)[:3, 3]
    assert np.linalg.norm(centre - t0) == pytest.approx(radius)
    assert np.linalg.norm(centre - t1) == pytest.approx(radius)
    normal = np.array(arc.basis.matrix.components)[:3, 2]
    assert np.dot(normal, leg_in) == pytest.approx(0.0, abs=1e-9)
    assert np.dot(normal, leg_out) == pytest.approx(0.0, abs=1e-9)


def test_right_angle_corner():
    loop, skipped = map_directrix(swept_disk([(0, 0), (1, 0), (1, 1)], 0.2))
    assert skipped == 0
    assert len(loop.children) == 3
    first, arc, last = loop.children
    assert len(arcs(loop)) == 1
    assert isinstance(arc.basis, ifcopenshell_wrapper.circle)
    assert_fillet(first, arc, last, (1, 0, 0), 0.2)
    # a right angle insets the tangent points by the radius
    assert point(first.end) == pytest.approx((0.8, 0, 0))
    assert point(last.start) == pytest.approx((1, 0.2, 0))


def test_oblique_corner_out_of_plane():
    loop, skipped = map_directrix(swept_disk([(0, 0, 0), (1, 0, 0), (2, 1, 1)], 0.1))
    assert skipped == 0
    first, arc, last = loop.children
    assert_fillet(first, arc, last, (1, 0, 0), 0.1)


def test_ends_of_an_open_directrix_are_not_filleted():
    loop, skipped = map_directrix(swept_disk([(0, 0), (1, 0), (1, 1), (2, 1)], 0.1))
    assert skipped == 0
    assert len(arcs(loop)) == 2
    assert len(loop.children) == 5
    assert point(loop.children[0].start) == pytest.approx((0, 0, 0))
    assert point(loop.children[-1].end) == pytest.approx((2, 1, 0))


def test_closed_directrix_fillets_every_corner():
    loop, skipped = map_directrix(swept_disk([(0, 0), (1, 0), (1, 1), (0, 1)], 0.1, closed=True))
    assert skipped == 0
    assert len(arcs(loop)) == 4
    assert len(loop.children) == 8
    assert point(loop.children[0].start) == pytest.approx(point(loop.children[-1].end))


def test_radius_exceeding_both_legs_is_skipped():
    loop, skipped = map_directrix(swept_disk([(0, 0), (1, 0), (1, 1)], 1.5))
    assert skipped == 1
    assert arcs(loop) == []
    assert len(loop.children) == 2


def test_radius_up_to_an_end_leg_and_half_an_inner_leg():
    # end legs allow the full length, inner legs half of it
    points = [(0, 0), (1, 0), (1, 1), (2, 1), (2, 1.1)]
    loop, skipped = map_directrix(swept_disk(points, 0.2))
    assert skipped == 1
    assert len(arcs(loop)) == 2
    loop, skipped = map_directrix(swept_disk(points, 0.5))
    assert skipped == 1
    assert len(arcs(loop)) == 2
    loop, skipped = map_directrix(swept_disk(points, 0.6))
    assert skipped == 3
    assert arcs(loop) == []


def test_straight_corner_is_left_alone_without_a_warning():
    loop, skipped = map_directrix(swept_disk([(0, 0), (1, 0), (2, 0), (2, 1)], 0.1))
    assert skipped == 0
    assert len(arcs(loop)) == 1
    assert len(loop.children) == 4


def test_fillet_radius_in_project_units():
    loop, skipped = map_directrix(swept_disk([(0, 0), (1000, 0), (1000, 1000)], 200.0, unit="MILLIMETERS"))
    assert skipped == 0
    first, arc, last = loop.children
    assert_fillet(first, arc, last, (1, 0, 0), 0.2)


def test_fillet_below_precision_is_ignored():
    loop, skipped = map_directrix(swept_disk([(0, 0), (1, 0), (1, 1)], 1e-6))
    assert skipped == 0
    assert arcs(loop) == []


def test_filleted_sweep_volume():
    f, item = swept_disk([(0, 0), (1, 0), (1, 1)], 0.2)
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, item)
    verts = np.array(shape.verts).reshape(-1, 3)
    faces = np.array(shape.faces).reshape(-1, 3)
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    volume = np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0
    # two legs insets by the radius plus a quarter turn of the fillet
    path_length = 2.0 - 2 * 0.2 + 0.2 * math.pi / 2
    assert volume == pytest.approx(math.pi * DISK_RADIUS**2 * path_length, rel=0.02)
