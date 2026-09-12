"""Segment counts for conics in the CGAL kernel.

Guards against small radii collapsing to a triangle when circle-segments is 0
and the segment count is derived from the deflection settings.
"""

import math

import pytest

import ifcopenshell
import ifcopenshell.geom

# Values Bonsai passes for interactive viewport quality.
BONSAI_LINEAR_DEFLECTION = 0.05
BONSAI_ANGULAR_DEFLECTION = 0.5

kernels = [
    pytest.param(
        kernel,
        marks=pytest.mark.skipif(
            not ifcopenshell.geom.has_geometry_library(kernel),
            reason=f"{kernel} geometry kernel is unavailable",
        ),
    )
    for kernel in ("cgal", "cgal-simple")
]


def circular_extrusion(radius: float) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")
    solid = f.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=f.create_entity("IfcCircleProfileDef", ProfileType="AREA", Radius=radius),
        Position=f.create_entity(
            "IfcAxis2Placement3D",
            Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
        ),
        ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        Depth=1.0,
    )
    representation = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid],
    )
    element = f.create_entity(
        "IfcBuildingElementProxy",
        GlobalId=ifcopenshell.guid.new(),
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
    )
    return f, element


def segments_per_section(radius: float, kernel: str, circle_segments: int = 0) -> int:
    _, element = circular_extrusion(radius)
    settings = ifcopenshell.geom.settings()
    settings.set("mesher-linear-deflection", BONSAI_LINEAR_DEFLECTION)
    settings.set("mesher-angular-deflection", BONSAI_ANGULAR_DEFLECTION)
    settings.set("circle-segments", circle_segments)
    settings.set("weld-vertices", True)
    shape = ifcopenshell.geom.create_shape(settings, element, geometry_library=kernel)
    verts = shape.geometry.verts
    return sum(1 for i in range(len(verts) // 3) if round(verts[i * 3 + 2], 6) == 0.0)


@pytest.mark.parametrize("kernel", kernels)
@pytest.mark.parametrize("radius", [0.05, 0.1, 0.5, 1.0, 5.0])
def test_angular_deflection_bounds_small_radii(kernel: str, radius: float) -> None:
    """A full circle never turns more than mesher-angular-deflection per chord."""
    segments = segments_per_section(radius, kernel)
    assert segments >= math.ceil(2 * math.pi / BONSAI_ANGULAR_DEFLECTION)


@pytest.mark.parametrize("kernel", kernels)
def test_linear_deflection_still_drives_large_radii(kernel: str) -> None:
    """Large radii keep the finer, linear deflection driven count (issue #8051)."""
    assert segments_per_section(5.0, kernel) > segments_per_section(0.5, kernel)


@pytest.mark.parametrize("kernel", kernels)
def test_explicit_circle_segments_is_radius_independent(kernel: str) -> None:
    """A non zero circle-segments is used verbatim, whatever the radius."""
    for radius in (0.05, 0.5, 5.0):
        assert segments_per_section(radius, kernel, circle_segments=16) == 16
