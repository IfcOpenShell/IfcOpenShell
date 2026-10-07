# This file was generated with the assistance of an AI coding tool.

import re

import pytest

import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom


def _write_space_plan(tmp_path, use_namespace):
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
    space = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSpace", name="Room")
    representation = ifcopenshell.api.geometry.add_wall_representation(
        model, context=body, length=4, height=3, thickness=5
    )
    ifcopenshell.api.geometry.assign_representation(model, product=space, representation=representation)
    ifcopenshell.api.aggregate.assign_object(model, products=[space], relating_object=storey)

    settings = ifcopenshell.geom.settings()
    settings.set("section-height-from-storeys", True)
    settings.set("print-space-areas", True)
    settings.set("svg-xmlns", use_namespace)
    path = tmp_path / "plan.svg"
    serializer = ifcopenshell.geom.serializers.svg(str(path), settings)
    serializer.setFile(model)
    serializer.writeHeader()
    for shape in ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(settings, model, 1)):
        serializer.write(shape)
    serializer.finalize()
    del serializer
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("use_namespace, attribute", [(False, "data-area"), (True, "ifc:area")])
def test_svg_space_group_carries_its_area(tmp_path, use_namespace, attribute):
    svg = _write_space_plan(tmp_path, use_namespace)
    group = re.search(r"<g [^>]*IfcSpace[^>]*>", svg).group(0)
    areas = [float(area) for area in re.findall(rf'{attribute}="([^"]*)"', group)]
    assert areas == [pytest.approx(20.0, abs=0.005)]


def test_svg_space_area_label_is_not_double_escaped(tmp_path):
    svg = _write_space_plan(tmp_path, False)
    assert "20.00m²</tspan>" in svg
