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
    not ifcopenshell.geom.has_geometry_library("manifold"), reason="manifold geometry kernel is unavailable"
)


def extruded_volume(make_profile):
    model = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )
    origin = model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((0.0, 0.0)))
    solid = model.createIfcExtrudedAreaSolid(
        make_profile(model, origin),
        model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0))),
        model.createIfcDirection((0.0, 0.0, 1.0)),
        1.0,
    )
    representation = model.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid])
    column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcColumn")
    column.Representation = model.createIfcProductDefinitionShape(None, None, [representation])
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), column, geometry_library="manifold")
    return ifcopenshell.util.shape.get_volume(shape.geometry)


def test_circle_profile_converts_with_default_circle_segments():
    volume = extruded_volume(lambda model, origin: model.createIfcCircleProfileDef("AREA", None, origin, 0.2))
    assert volume == pytest.approx(math.pi * 0.2**2, rel=0.02)


def test_rounded_rectangle_corners_are_not_reduced_to_chords():
    volume = extruded_volume(
        lambda model, origin: model.createIfcRoundedRectangleProfileDef("AREA", None, origin, 0.4, 0.4, 0.05)
    )
    assert volume == pytest.approx(0.16 - (4 - math.pi) * 0.05**2, rel=5e-3)


def test_i_shape_fillets_are_not_reduced_to_chords():
    volume = extruded_volume(
        lambda model, origin: model.createIfcIShapeProfileDef("AREA", None, origin, 0.2, 0.4, 0.008, 0.013, 0.016)
    )
    expected = 2 * 0.2 * 0.013 + (0.4 - 2 * 0.013) * 0.008 + (4 - math.pi) * 0.016**2
    assert volume == pytest.approx(expected, rel=1e-2)
