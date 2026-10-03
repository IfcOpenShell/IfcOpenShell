# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom


def red_box(side: str) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
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
    rendering = f.create_entity(
        "IfcSurfaceStyleRendering",
        SurfaceColour=f.create_entity("IfcColourRgb", Red=1.0, Green=0.0, Blue=0.0),
        ReflectanceMethod="FLAT",
    )
    style = f.create_entity("IfcSurfaceStyle", Side=side, Styles=[rendering])
    f.create_entity("IfcStyledItem", Item=solid, Styles=[style])
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


@pytest.mark.parametrize("side", ["POSITIVE", "NEGATIVE", "BOTH"])
def test_surface_style_is_used_for_any_side(side: str) -> None:
    _, element = red_box(side)
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), element)
    assert [tuple(m.diffuse.components) for m in shape.geometry.materials] == [(1.0, 0.0, 0.0)]
