# This file was generated with the assistance of an AI coding tool.

import math

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid


def build_model():
    model = ifcopenshell.file(schema="IFC4")
    origin = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, origin, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    placement = model.createIfcLocalPlacement(None, origin)
    helix = [(math.cos(i / 10.0), math.sin(i / 10.0), i / 100.0) for i in range(300)]
    heavy = model.createIfcSweptDiskSolid(
        model.createIfcPolyline([model.createIfcCartesianPoint(p) for p in helix]), 0.01, None, None, None
    )
    profile = model.createIfcRectangleProfileDef("AREA", None, None, 1.0, 1.0)
    light = model.createIfcExtrudedAreaSolid(profile, None, model.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
    for i in range(24):
        item = heavy if i % 8 == 0 else light
        representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [item])
        model.createIfcBuildingElementProxy(
            ifcopenshell.guid.new(),
            None,
            str(i),
            None,
            None,
            placement,
            model.createIfcProductDefinitionShape(None, None, [representation]),
        )
    return model


def iterate(model, threads):
    settings = ifcopenshell.geom.settings()
    iterator = ifcopenshell.geom.iterator(settings, model, threads, geometry_library="opencascade")
    ids = []
    if iterator.initialize():
        while True:
            ids.append(iterator.get().id)
            if not iterator.next():
                break
    return ids


def test_multithreaded_output_order_matches_single_threaded_3904():
    model = build_model()
    expected = iterate(model, 1)
    assert len(expected) == 24
    for _ in range(3):
        assert iterate(model, 8) == expected
