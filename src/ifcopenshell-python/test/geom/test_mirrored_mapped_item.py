# This file was generated with the assistance of an AI coding tool.

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom


def mapped_l_shape(mirror: bool) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")

    def point(x, y):
        return f.create_entity("IfcCartesianPoint", Coordinates=(float(x), float(y)))

    outline = f.create_entity(
        "IfcPolyline",
        Points=[point(0, 0), point(3, 0), point(3, 1), point(1, 1), point(1, 2), point(0, 2), point(0, 0)],
    )
    solid = f.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=f.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA", OuterCurve=outline),
        Position=f.create_entity(
            "IfcAxis2Placement3D",
            Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
        ),
        ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        Depth=1.0,
    )
    source = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid],
    )
    representation_map = f.create_entity(
        "IfcRepresentationMap",
        MappingOrigin=f.create_entity(
            "IfcAxis2Placement3D",
            Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
        ),
        MappedRepresentation=source,
    )
    target = f.create_entity(
        "IfcCartesianTransformationOperator3D",
        Axis1=f.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0)),
        Axis2=f.create_entity("IfcDirection", DirectionRatios=(0.0, -1.0 if mirror else 1.0, 0.0)),
        LocalOrigin=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
        Scale=1.0,
        Axis3=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
    )
    representation = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="MappedRepresentation",
        Items=[f.create_entity("IfcMappedItem", MappingSource=representation_map, MappingTarget=target)],
    )
    element = f.create_entity(
        "IfcBuildingElementProxy",
        GlobalId=ifcopenshell.guid.new(),
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
    )
    return f, element


def triangles_agreeing_with_normals(mirror: bool) -> tuple[int, int]:
    _, element = mapped_l_shape(mirror)
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", False)
    geometry = ifcopenshell.geom.create_shape(settings, element).geometry
    verts = np.array(geometry.verts).reshape(-1, 3)
    normals = np.array(geometry.normals).reshape(-1, 3)
    faces = np.array(geometry.faces).reshape(-1, 3)
    agreeing = 0
    for a, b, c in faces:
        winding_normal = np.cross(verts[b] - verts[a], verts[c] - verts[a])
        if np.dot(winding_normal, normals[a]) > 0:
            agreeing += 1
    return agreeing, len(faces)


@pytest.mark.parametrize("mirror", [False, True])
def test_winding_matches_vertex_normals(mirror: bool) -> None:
    agreeing, total = triangles_agreeing_with_normals(mirror)
    assert total > 0
    assert agreeing == total
