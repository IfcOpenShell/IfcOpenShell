# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom

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


def box() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")
    solid = f.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=2.0, YDim=1.0),
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


@pytest.mark.parametrize("kernel", kernels)
@pytest.mark.parametrize("dont_emit_normals", [False, True])
def test_dont_emit_normals(kernel: str, dont_emit_normals: bool) -> None:
    settings = ifcopenshell.geom.settings()
    settings.set("no-normals", dont_emit_normals)
    _, element = box()
    shape = ifcopenshell.geom.create_shape(settings, element, geometry_library=kernel)
    assert (len(shape.geometry.normals) == 0) == dont_emit_normals
