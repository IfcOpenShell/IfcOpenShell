# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom

pytestmark = pytest.mark.skipif(
    not ifcopenshell.geom.has_geometry_library("cgal"), reason="cgal geometry kernel is unavailable"
)


def box(x: float) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")
    solid = f.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=2.0, YDim=1.0),
        Position=f.create_entity(
            "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
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
    placement = f.create_entity(
        "IfcLocalPlacement",
        RelativePlacement=f.create_entity(
            "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(x, 0.0, 0.0))
        ),
    )
    element = f.create_entity(
        "IfcBuildingElementProxy",
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=placement,
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
    )
    return f, element


@pytest.mark.parametrize("x", [0.0, 10.0])
def test_original_edges_of_placed_element(x: float) -> None:
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    settings.set("cgal-original-edges", True)
    _, element = box(x)
    shape = ifcopenshell.geom.create_shape(settings, element, geometry_library="cgal")
    assert len(shape.geometry.edges) // 2 == 12
