# This file was generated with the assistance of an AI coding tool.
import math

import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.shape

pytestmark = pytest.mark.skipif(
    not ifcopenshell.geom.has_geometry_library("opencascade"), reason="opencascade geometry kernel is unavailable"
)


def box_with_concave_corner_volume() -> float:
    model = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )

    def line(start, end):
        polyline = model.createIfcPolyline([model.createIfcCartesianPoint(start), model.createIfcCartesianPoint(end)])
        return model.createIfcCompositeCurveSegment("CONTINUOUS", True, polyline)

    circle = model.createIfcCircle(model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((1.0, 1.0))), 0.2)
    arc = model.createIfcTrimmedCurve(
        circle,
        [model.createIfcParameterValue(math.pi)],
        [model.createIfcParameterValue(1.5 * math.pi)],
        True,
        "PARAMETER",
    )
    segments = [
        line((0.0, 0.0), (1.0, 0.0)),
        line((1.0, 0.0), (1.0, 0.8)),
        model.createIfcCompositeCurveSegment("CONTINUOUS", False, arc),
        line((0.8, 1.0), (0.0, 1.0)),
        line((0.0, 1.0), (0.0, 0.0)),
    ]
    profile = model.createIfcArbitraryClosedProfileDef("AREA", None, model.createIfcCompositeCurve(segments, False))
    solid = model.createIfcExtrudedAreaSolid(
        profile,
        model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0))),
        model.createIfcDirection((0.0, 0.0, 1.0)),
        1.0,
    )
    representation = model.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid])
    column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcColumn")
    column.Representation = model.createIfcProductDefinitionShape(None, None, [representation])
    assert not [u for u in model.by_type("IfcNamedUnit") if u.UnitType == "PLANEANGLEUNIT"]
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), column, geometry_library="opencascade")
    return ifcopenshell.util.shape.get_volume(shape.geometry)


def test_parameter_value_trims_without_a_plane_angle_unit_are_radians():
    assert box_with_concave_corner_volume() == pytest.approx(1.0 - math.pi * 0.2**2 / 4, abs=1e-2)
