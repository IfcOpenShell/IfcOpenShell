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


def cube_faces(f: ifcopenshell.file, origin: tuple[float, float, float], size: float) -> list:
    x, y, z = origin
    points = [
        f.create_entity("IfcCartesianPoint", Coordinates=(x + dx * size, y + dy * size, z + dz * size))
        for dz in (0, 1)
        for dy in (0, 1)
        for dx in (0, 1)
    ]
    quads = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    return [
        f.create_entity(
            "IfcFace",
            Bounds=[
                f.create_entity(
                    "IfcFaceOuterBound",
                    Bound=f.create_entity("IfcPolyLoop", Polygon=[points[i] for i in quad]),
                    Orientation=True,
                )
            ],
        )
        for quad in quads
    ]


def difference_with_self_intersecting_base() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")
    base = f.create_entity(
        "IfcFacetedBrep",
        Outer=f.create_entity(
            "IfcClosedShell",
            CfsFaces=cube_faces(f, (0.0, 0.0, 0.0), 2.0) + cube_faces(f, (1.0, 1.0, 1.0), 2.0),
        ),
    )
    cutter = f.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=0.4, YDim=0.4),
        Position=f.create_entity(
            "IfcAxis2Placement3D",
            Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.5, 0.5, 0.0)),
        ),
        ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        Depth=0.4,
    )
    result = f.create_entity("IfcBooleanResult", Operator="DIFFERENCE", FirstOperand=base, SecondOperand=cutter)
    representation = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="CSG",
        Items=[result],
    )
    element = f.create_entity(
        "IfcBuildingElementProxy",
        GlobalId=ifcopenshell.guid.new(),
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
    )
    return f, element


@pytest.mark.parametrize("kernel", kernels)
def test_unprocessable_base_operand_fails_the_boolean(kernel: str) -> None:
    _, element = difference_with_self_intersecting_base()
    with pytest.raises(RuntimeError):
        ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), element, geometry_library=kernel)
