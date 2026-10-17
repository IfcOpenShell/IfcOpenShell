# This file was generated with the assistance of an AI coding tool.
import re

import pytest

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W

pytestmark = pytest.mark.skipif(
    not hasattr(ifcopenshell.geom.serializers, "svg"),
    reason="SVG serializer is unavailable",
)


def round_column(radius: float) -> ifcopenshell.file:
    f = ifcopenshell.file(schema="IFC4")
    project = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcProject", name="Project")
    ifcopenshell.api.run("unit.assign_unit", f)
    model = ifcopenshell.api.run("context.add_context", f, context_type="Model")
    body = ifcopenshell.api.run(
        "context.add_context",
        f,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model,
    )
    site = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="Storey")
    storey.Elevation = 0.0
    ifcopenshell.api.run("aggregate.assign_object", f, products=[site], relating_object=project)
    ifcopenshell.api.run("aggregate.assign_object", f, products=[building], relating_object=site)
    ifcopenshell.api.run("aggregate.assign_object", f, products=[storey], relating_object=building)

    profile = f.createIfcCircleProfileDef("AREA", None, None, radius)
    origin = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    solid = f.createIfcExtrudedAreaSolid(profile, origin, f.createIfcDirection((0.0, 0.0, 1.0)), 3.0)
    column = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcColumn", name="Column")
    representation = f.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid])
    column.Representation = f.createIfcProductDefinitionShape(None, None, [representation])
    column.ObjectPlacement = f.createIfcLocalPlacement(None, origin)
    ifcopenshell.api.run("spatial.assign_container", f, products=[column], relating_structure=storey)
    return f


def plan_boundary_points(f: ifcopenshell.file, linear_deflection: float) -> int:
    settings = ifcopenshell.geom.settings(ELEMENT_HIERARCHY=True)
    settings.set("dimensionality", W.SURFACES_AND_SOLIDS)
    settings.set("iterator-output", W.NATIVE)
    settings.set("svg-write-poly", True)
    settings.set("svg-xmlns", True)
    settings.set("svg-project", True)
    settings.set("svg-poly", True)
    settings.set("svg-prefilter", True)
    settings.set("section-height-from-storeys", True)
    settings.set("mesher-linear-deflection", linear_deflection)
    buf = ifcopenshell.geom.serializers.buffer()
    serializer = ifcopenshell.geom.serializers.svg(buf, settings)
    serializer.setFile(f)
    for element in ifcopenshell.geom.iterator(settings, f, exclude=["IfcOpeningElement", "IfcSpace"]):
        serializer.write(element)
    serializer.finalize()
    paths = re.findall(r'<path[^>]* d="([^"]*)"', buf.get_value())
    return sum(len(re.findall(r"[ML]", d)) for d in paths)


class TestSvgPolyHlrDeflection:
    def test_finer_linear_deflection_gives_a_smoother_round_column_in_plan(self):
        f = round_column(1.0)
        coarse = plan_boundary_points(f, 0.1)
        fine = plan_boundary_points(f, 0.001)
        assert fine > coarse
