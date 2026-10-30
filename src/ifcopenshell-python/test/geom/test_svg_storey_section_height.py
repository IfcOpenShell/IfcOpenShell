# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.geom


def _create_model(building_elevation):
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

    def local_placement(relative_to, z):
        point = model.createIfcCartesianPoint((0.0, 0.0, z))
        return model.createIfcLocalPlacement(relative_to, model.createIfcAxis2Placement3D(point))

    building.ObjectPlacement = local_placement(None, building_elevation)
    storey.ObjectPlacement = local_placement(building.ObjectPlacement, 0.0)
    wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall", name="Wall")
    representation = ifcopenshell.api.geometry.add_wall_representation(
        model, context=body, length=4, height=3, thickness=0.2
    )
    ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=representation)
    ifcopenshell.api.spatial.assign_container(model, products=[wall], relating_structure=storey)
    wall.ObjectPlacement = local_placement(storey.ObjectPlacement, 0.0)
    return model


@pytest.mark.parametrize("building_elevation", [0.0, 10.0], ids=["ground", "raised_building"])
def test_svg_section_height_from_storeys_uses_global_placement(tmp_path, building_elevation):
    model = _create_model(building_elevation)
    settings = ifcopenshell.geom.settings()
    settings.set("section-height-from-storeys", True)
    path = tmp_path / "plan.svg"
    serializer = ifcopenshell.geom.serializers.svg(str(path), settings)
    serializer.setFile(model)
    serializer.writeHeader()
    for shape in ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(settings, model, 1)):
        serializer.write(shape)
    serializer.finalize()
    del serializer

    assert 'class="IfcWall"' in path.read_text()
