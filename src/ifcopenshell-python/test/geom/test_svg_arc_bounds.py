# This file was generated with the assistance of an AI coding tool.

import re

import pytest

import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.geom


def _create_model_with_shallow_arc_column():
    model = ifcopenshell.api.project.create_file()
    project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    body = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=ifcopenshell.api.context.add_context(model, context_type="Model"),
    )
    building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding")
    storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey")
    storey.Elevation = 0.0
    ifcopenshell.api.aggregate.assign_object(model, products=[building], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(model, products=[storey], relating_object=building)
    points = model.createIfcCartesianPointList2D([(-1.0, 0.0), (0.0, 0.1), (1.0, 0.0)])
    curve = model.createIfcIndexedPolyCurve(
        points, [model.createIfcArcIndex((1, 2, 3)), model.createIfcLineIndex((3, 1))], False
    )
    profile = model.createIfcArbitraryClosedProfileDef("AREA", None, curve)
    column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcColumn", name="Column")
    representation = ifcopenshell.api.geometry.add_profile_representation(
        model, context=body, profile=profile, depth=3.0
    )
    ifcopenshell.api.geometry.assign_representation(model, product=column, representation=representation)
    ifcopenshell.api.spatial.assign_container(model, products=[column], relating_structure=storey)
    return model


def test_svg_bounds_follow_the_drawn_arc(tmp_path):
    model = _create_model_with_shallow_arc_column()
    settings = ifcopenshell.geom.settings()
    settings.set("section-height-from-storeys", True)
    settings.set("bounds", "512x512")
    path = tmp_path / "plan.svg"
    serializer = ifcopenshell.geom.serializers.svg(str(path), settings)
    serializer.setFile(model)
    serializer.writeHeader()
    for shape in ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(settings, model, 1)):
        serializer.write(shape)
    serializer.finalize()
    del serializer

    d = re.search(r'<path d="([^"]*)"', path.read_text()).group(1)
    number = r"(-?[\d.]+(?:e-?\d+)?)"
    match = re.fullmatch(rf"M{number},{number} A\S+ \S+ \S+ {number},{number} L{number},{number}", d)
    xs = [float(match.group(i)) for i in (1, 3, 5)]
    assert max(xs) - min(xs) == pytest.approx(512, rel=0.05)
