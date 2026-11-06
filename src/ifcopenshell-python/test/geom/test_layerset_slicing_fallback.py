# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom


def wall_with_axis() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")

    def point(*coordinates):
        return f.create_entity("IfcCartesianPoint", Coordinates=tuple(float(c) for c in coordinates))

    solid = f.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=4.0, YDim=0.3),
        Position=f.create_entity("IfcAxis2Placement3D", Location=point(0, 0, 0)),
        ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        Depth=3.0,
    )
    body = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid],
    )
    axis = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Axis",
        RepresentationType="Curve2D",
        Items=[f.create_entity("IfcPolyline", Points=[point(-2, 0), point(2, 0)])],
    )
    wall = f.create_entity(
        "IfcWall",
        GlobalId=ifcopenshell.guid.new(),
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[body, axis]),
    )
    layers = [
        f.create_entity("IfcMaterialLayer", Material=f.create_entity("IfcMaterial", Name=name), LayerThickness=t)
        for name, t in (("a", 0.1), ("b", 0.2))
    ]
    usage = f.create_entity(
        "IfcMaterialLayerSetUsage",
        ForLayerSet=f.create_entity("IfcMaterialLayerSet", MaterialLayers=layers),
        LayerSetDirection="AXIS2",
        DirectionSense="POSITIVE",
        OffsetFromReferenceLine=0.0,
    )
    f.create_entity(
        "IfcRelAssociatesMaterial", GlobalId=ifcopenshell.guid.new(), RelatedObjects=[wall], RelatingMaterial=usage
    )
    return f, wall


@pytest.mark.parametrize("slicing", [False, True])
def test_wall_is_converted_with_layerset_slicing(slicing: bool) -> None:
    settings = ifcopenshell.geom.settings()
    settings.set("enable-layerset-slicing", slicing)
    _, wall = wall_with_axis()
    shape = ifcopenshell.geom.create_shape(settings, wall)
    assert len(shape.geometry.verts) // 3 == 8
