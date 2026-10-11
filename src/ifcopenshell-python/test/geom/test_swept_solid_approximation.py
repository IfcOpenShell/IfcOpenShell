# This file was generated with the assistance of an AI coding tool.
"""Swept disks and lofts on kernels without a native sweep or loft (#8106)."""

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid

TOL = 0.02

kernels = [
    pytest.param(
        kernel,
        marks=pytest.mark.skipif(
            not ifcopenshell.geom.has_geometry_library(kernel),
            reason=f"{kernel} geometry kernel is unavailable",
        ),
    )
    for kernel in ("manifold", "cgal", "cgal-simple")
]


def point(f: ifcopenshell.file, *coordinates: float) -> ifcopenshell.entity_instance:
    return f.create_entity("IfcCartesianPoint", Coordinates=tuple(float(c) for c in coordinates))


def proxy(f: ifcopenshell.file, solid: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    context = f.create_entity("IfcGeometricRepresentationContext")
    representation = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid],
    )
    return f.create_entity(
        "IfcBuildingElementProxy",
        GlobalId=ifcopenshell.guid.new(),
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
    )


def swept_disk() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    directrix = f.create_entity("IfcPolyline", Points=[point(f, 0, 0, 0), point(f, 1, 0, 0), point(f, 1, 1, 0)])
    return f, proxy(f, f.create_entity("IfcSweptDiskSolid", Directrix=directrix, Radius=0.1))


def tapered_extrusion(z: float) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")

    def profile(size: float) -> ifcopenshell.entity_instance:
        return f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=size, YDim=size)

    solid = f.create_entity(
        "IfcExtrudedAreaSolidTapered",
        SweptArea=profile(1.0),
        Position=f.create_entity("IfcAxis2Placement3D", Location=point(f, 0, 0, z)),
        ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        Depth=1.0,
        EndSweptArea=profile(0.5),
    )
    return f, proxy(f, solid)


def bounds(element: ifcopenshell.entity_instance, kernel: str, **options) -> tuple[list[float], list[float]]:
    settings = ifcopenshell.geom.settings()
    for key, value in options.items():
        settings.set(key, value)
    shape = ifcopenshell.geom.create_shape(settings, element, geometry_library=kernel)
    verts = shape.geometry.verts
    assert len(verts) > 0
    xyz = [verts[i::3] for i in range(3)]
    return [min(c) for c in xyz], [max(c) for c in xyz]


@pytest.mark.parametrize("kernel", kernels)
def test_swept_disk_is_not_dropped(kernel: str) -> None:
    _, element = swept_disk()
    lo, hi = bounds(element, kernel)
    assert lo[0] == pytest.approx(0.0, abs=TOL)
    assert hi[0] == pytest.approx(1.1, abs=TOL)
    assert hi[1] == pytest.approx(1.0, abs=TOL)
    assert lo[2] == pytest.approx(-0.1, abs=TOL)
    assert hi[2] == pytest.approx(0.1, abs=TOL)


@pytest.mark.parametrize("kernel", kernels)
def test_tapered_extrusion_is_not_dropped(kernel: str) -> None:
    _, element = tapered_extrusion(0.0)
    lo, hi = bounds(element, kernel)
    assert lo == pytest.approx([-0.5, -0.5, 0.0], abs=TOL)
    assert hi == pytest.approx([0.5, 0.5, 1.0], abs=TOL)


@pytest.mark.parametrize("kernel", kernels)
def test_tapered_extrusion_keeps_its_placement(kernel: str) -> None:
    _, element = tapered_extrusion(5.0)
    lo, hi = bounds(element, kernel)
    assert lo[2] == pytest.approx(5.0, abs=TOL)
    assert hi[2] == pytest.approx(6.0, abs=TOL)


@pytest.mark.skipif(
    not ifcopenshell.geom.has_geometry_library("opencascade"),
    reason="opencascade geometry kernel is unavailable",
)
def test_forced_approximation_matches_native_sweep() -> None:
    _, element = swept_disk()
    native = bounds(element, "opencascade")
    approximated = bounds(element, "opencascade", **{"approximate-swept-solids": True})
    assert approximated[0] == pytest.approx(native[0], abs=TOL)
    assert approximated[1] == pytest.approx(native[1], abs=TOL)
