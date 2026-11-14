# This file was generated with the assistance of an AI coding tool.
"""Hybrid kernel fallback in the multithreaded iterator.

A representation with one item the first kernel cannot convert next to one it
can must fall back to the next kernel, whatever the number of threads.
"""

import math

import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom

HYBRID = "hybrid-cgal-simple-opencascade"
REFERENCE = "opencascade"

BEND_RADIUS = 1.0
PIPE_RADIUS = 0.2
STUB_LENGTH = 0.1

# The stub alone spans STUB_LENGTH along X, the bend spans more than BEND_RADIUS,
# so a quarter of the pipe radius separates the two without depending on the mesher.
TOLERANCE = PIPE_RADIUS / 4

pytestmark = pytest.mark.skipif(
    not all(ifcopenshell.geom.has_geometry_library(library) for library in ("cgal-simple", REFERENCE)),
    reason=f"cgal-simple or {REFERENCE} geometry kernel is unavailable",
)


def pipe_bend() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    """A swept disk on a quarter arc (no cgal-simple support) with a straight extruded stub at its start."""
    f = ifcopenshell.api.project.create_file(version="IFC4")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(f, length={"is_metric": True, "raw": "METERS"})
    model = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )

    middle = (BEND_RADIUS * math.sin(math.pi / 4), BEND_RADIUS * (1 - math.cos(math.pi / 4)), 0.0)
    points = f.createIfcCartesianPointList3D(((0.0, 0.0, 0.0), middle, (BEND_RADIUS, BEND_RADIUS, 0.0)))
    arc = f.createIfcIndexedPolyCurve(points, [f.createIfcArcIndex((1, 2, 3))], False)
    swept_disk = f.createIfcSweptDiskSolid(arc, PIPE_RADIUS)

    profile = f.createIfcCircleProfileDef("AREA", None, None, PIPE_RADIUS)
    position = f.createIfcAxis2Placement3D(
        f.createIfcCartesianPoint((0.0, 0.0, 0.0)),
        f.createIfcDirection((-1.0, 0.0, 0.0)),
        f.createIfcDirection((0.0, 1.0, 0.0)),
    )
    stub = f.createIfcExtrudedAreaSolid(profile, position, f.createIfcDirection((0.0, 0.0, 1.0)), STUB_LENGTH)

    fitting = ifcopenshell.api.root.create_entity(f, ifc_class="IfcPipeFitting", predefined_type="BEND")
    representation = f.createIfcShapeRepresentation(body, "Body", "SolidModel", [swept_disk, stub])
    ifcopenshell.api.geometry.assign_representation(f, product=fitting, representation=representation)
    return f, fitting


def extents(library: str, num_threads: int) -> tuple[float, float, float]:
    f, fitting = pipe_bend()
    iterator = ifcopenshell.geom.iterator(
        ifcopenshell.geom.settings(), f, num_threads, include=[fitting], geometry_library=library
    )
    assert iterator.initialize()
    verts = iterator.get().geometry.verts
    return tuple(max(verts[axis::3]) - min(verts[axis::3]) for axis in range(3))


@pytest.mark.parametrize("num_threads", [1, 2])
def test_bend_spans_the_arc(num_threads: int) -> None:
    """The swept disk is not dropped: the bend is as large as the one OpenCASCADE gives."""
    assert extents(HYBRID, num_threads) == pytest.approx(extents(REFERENCE, num_threads), abs=TOLERANCE)


def test_bend_is_the_same_on_one_and_two_threads() -> None:
    assert extents(HYBRID, 2) == pytest.approx(extents(HYBRID, 1), abs=TOLERANCE)
