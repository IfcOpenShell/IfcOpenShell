# This file was generated with the assistance of an AI coding tool.

import numpy as np

import ifcopenshell
import ifcopenshell.geom


def test_advanced_brep_with_spherical_surface_converts_to_sphere():
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")

    def point(*coordinates):
        return f.create_entity("IfcCartesianPoint", Coordinates=tuple(float(c) for c in coordinates))

    radius = 2.0
    vertex = f.create_entity("IfcVertexPoint", VertexGeometry=point(radius, 0, 0))
    circle = f.create_entity(
        "IfcCircle",
        Position=f.create_entity("IfcAxis2Placement3D", Location=point(0, 0, 0)),
        Radius=radius,
    )
    edge = f.create_entity("IfcEdgeCurve", EdgeStart=vertex, EdgeEnd=vertex, EdgeGeometry=circle, SameSense=True)
    loop = f.create_entity(
        "IfcEdgeLoop", EdgeList=[f.create_entity("IfcOrientedEdge", EdgeElement=edge, Orientation=True)]
    )
    face = f.create_entity(
        "IfcAdvancedFace",
        Bounds=[f.create_entity("IfcFaceOuterBound", Bound=loop, Orientation=True)],
        FaceSurface=f.create_entity(
            "IfcSphericalSurface",
            Position=f.create_entity("IfcAxis2Placement3D", Location=point(1, 2, 3)),
            Radius=radius,
        ),
        SameSense=True,
    )
    brep = f.create_entity("IfcAdvancedBrep", Outer=f.create_entity("IfcClosedShell", CfsFaces=[face]))
    representation = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="AdvancedBrep",
        Items=[brep],
    )
    element = f.create_entity(
        "IfcBuildingElementProxy",
        GlobalId=ifcopenshell.guid.new(),
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
    )
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), element)
    verts = np.array(shape.geometry.verts).reshape(-1, 3)
    assert np.allclose(verts.max(axis=0) - verts.min(axis=0), 2 * radius, atol=1e-2)
    assert np.allclose((verts.max(axis=0) + verts.min(axis=0)) / 2, (1, 2, 3), atol=1e-2)
