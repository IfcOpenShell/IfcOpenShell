# This file was generated with the assistance of an AI coding tool.

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


@pytest.mark.parametrize("kernel", ["opencascade", "cgal", "cgal-simple", "manifold"])
@pytest.mark.parametrize("kind", ["horizontal", "surface", "fixed_reference"])
def test_alignment_lofts_across_kernels(kernel, kind):
    if not ifcopenshell.geom.has_geometry_library(kernel):
        pytest.skip(f"{kernel} geometry kernel is unavailable")
    model = ifcopenshell.file(schema="IFC4X3_ADD2")
    origin = model.createIfcCartesianPoint((0.0, 0.0, 0.0))
    context = model.createIfcGeometricRepresentationContext(
        None, "Model", 3, 1e-5, model.createIfcAxis2Placement3D(origin), None
    )
    placement = model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((0.0, 0.0)))
    parent = model.createIfcLine(
        model.createIfcCartesianPoint((0.0, 0.0)),
        model.createIfcVector(model.createIfcDirection((1.0, 0.0)), 1.0),
    )
    segment = model.createIfcCurveSegment(
        Transition="CONTINUOUS",
        Placement=placement,
        SegmentStart=model.createIfcLengthMeasure(0.0),
        SegmentLength=model.createIfcLengthMeasure(10.0),
        ParentCurve=parent,
    )
    directrix = model.createIfcCompositeCurve(Segments=[segment], SelfIntersect=False)

    def station(distance):
        return model.createIfcAxis2PlacementLinear(
            Location=model.createIfcPointByDistanceExpression(
                DistanceAlong=model.createIfcLengthMeasure(distance), BasisCurve=directrix
            )
        )

    rectangle = model.createIfcRectangleProfileDef(ProfileType="AREA", XDim=2.0, YDim=1.0)
    if kind == "horizontal":
        solid = model.createIfcSectionedSolidHorizontal(
            Directrix=directrix,
            CrossSections=[rectangle, rectangle],
            CrossSectionPositions=[station(0.0), station(10.0)],
        )
    elif kind == "surface":
        profiles = [
            model.createIfcOpenCrossProfileDef(
                ProfileType="CURVE",
                HorizontalWidths=True,
                Widths=widths,
                Slopes=(0.0, 0.0, 0.0),
                Tags=("a", "b", "c", "d"),
            )
            for widths in [(1.0, 0.0, 1.0), (1.0, 0.5, 0.5)]
        ]
        solid = model.createIfcSectionedSurface(
            Directrix=directrix,
            CrossSections=profiles,
            CrossSectionPositions=[station(0.0), station(10.0)],
        )
    else:
        solid = model.createIfcFixedReferenceSweptAreaSolid(
            SweptArea=rectangle,
            Directrix=directrix,
            FixedReference=model.createIfcDirection((0.0, 1.0, 0.0)),
        )
    representation = model.createIfcShapeRepresentation(context, "Body", "AdvancedSweptSolid", [solid])
    settings = ifcopenshell.geom.settings()
    settings.set("reorient-shells", True)
    geometry = ifcopenshell.geom.create_shape(settings, representation, geometry_library=kernel)
    vertices = ifcopenshell.util.shape.get_vertices(geometry)
    assert np.ptp(vertices, axis=0) == pytest.approx((10.0, 2.0, 0.0 if kind == "surface" else 1.0))
    assert ifcopenshell.util.shape.get_area(geometry) == pytest.approx(20.0 if kind == "surface" else 64.0)
    if kind != "surface":
        assert ifcopenshell.util.shape.get_volume(geometry) == pytest.approx(20.0)
