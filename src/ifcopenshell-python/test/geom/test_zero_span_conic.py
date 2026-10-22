# This file was generated with the assistance of an AI coding tool.

import numpy as np

import ifcopenshell
import ifcopenshell.geom


def profile_with_trimmed_circle(start: float, end: float) -> ifcopenshell.file:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")

    def point(x, y):
        return f.create_entity("IfcCartesianPoint", Coordinates=(float(x), float(y)))

    def segment(curve):
        return f.create_entity("IfcCompositeCurveSegment", Transition="CONTINUOUS", SameSense=True, ParentCurve=curve)

    def line(a, b):
        return segment(f.create_entity("IfcPolyline", Points=[point(*a), point(*b)]))

    circle = f.create_entity(
        "IfcCircle",
        Position=f.create_entity("IfcAxis2Placement2D", Location=point(2, 1)),
        Radius=1.0,
    )
    trimmed = f.create_entity(
        "IfcTrimmedCurve",
        BasisCurve=circle,
        Trim1=[f.create_entity("IfcParameterValue", wrappedValue=start)],
        Trim2=[f.create_entity("IfcParameterValue", wrappedValue=end)],
        SenseAgreement=True,
        MasterRepresentation="PARAMETER",
    )
    outline = f.create_entity(
        "IfcCompositeCurve",
        Segments=[
            line((0, 0), (3, 0)),
            line((3, 0), (3, 1)),
            segment(trimmed),
            line((3, 1), (0, 1)),
            line((0, 1), (0, 0)),
        ],
        SelfIntersect=False,
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
    representation = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid],
    )
    f.create_entity(
        "IfcBuildingElementProxy",
        GlobalId=ifcopenshell.guid.new(),
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
    )
    return f


def vertices(f: ifcopenshell.file) -> np.ndarray:
    element = f.by_type("IfcBuildingElementProxy")[0]
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), element)
    return np.array(shape.geometry.verts).reshape(-1, 3)


class TestZeroSpanTrimmedCircle:
    def test_zero_span_segment_is_skipped(self):
        verts = vertices(profile_with_trimmed_circle(0.0, 0.0))
        assert np.allclose(verts.min(axis=0), (0.0, 0.0, 0.0), atol=1e-6)
        assert np.allclose(verts.max(axis=0), (3.0, 1.0, 1.0), atol=1e-6)
