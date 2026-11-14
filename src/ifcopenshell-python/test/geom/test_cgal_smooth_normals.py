# This file was generated with the assistance of an AI coding tool.

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom

pytestmark = pytest.mark.skipif(
    not ifcopenshell.geom.has_geometry_library("cgal"), reason="cgal geometry kernel is unavailable"
)


def cylinder() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")
    solid = f.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=f.create_entity("IfcCircleProfileDef", ProfileType="AREA", Radius=1.0),
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
    element = f.create_entity(
        "IfcBuildingElementProxy",
        GlobalId=ifcopenshell.guid.new(),
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
    )
    return f, element


def side_normals_alignment(smooth_angle: float) -> float:
    settings = ifcopenshell.geom.settings()
    settings.set("cgal-smooth-angle-degrees", smooth_angle)
    settings.set("circle-segments", 8)
    settings.set("weld-vertices", False)
    _, element = cylinder()
    geometry = ifcopenshell.geom.create_shape(settings, element, geometry_library="cgal").geometry
    verts = np.array(geometry.verts).reshape(-1, 3)
    normals = np.array(geometry.normals).reshape(-1, 3)
    assert np.allclose(np.linalg.norm(normals, axis=1), 1.0)
    side = np.abs(normals[:, 2]) < 1e-6
    radial = verts[side][:, :2] / np.linalg.norm(verts[side][:, :2], axis=1)[:, None]
    return float(np.min((normals[side][:, :2] * radial).sum(axis=1) / np.linalg.norm(normals[side][:, :2], axis=1)))


def test_smoothing_angle_changes_emitted_normals() -> None:
    assert side_normals_alignment(60.0) > side_normals_alignment(-1.0) + 0.05
