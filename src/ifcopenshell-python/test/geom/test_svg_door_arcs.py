# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import ifcopenshell.api.unit
import ifcopenshell.geom


def _create_model_with_door_on_lower_storey():
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
    ifcopenshell.api.aggregate.assign_object(model, products=[building], relating_object=project)

    def local_placement(relative_to, z):
        point = model.createIfcCartesianPoint((0.0, 0.0, z))
        return model.createIfcLocalPlacement(relative_to, model.createIfcAxis2Placement3D(point))

    storeys = []
    for elevation in (0.0, 3.0):
        storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey")
        storey.Elevation = elevation
        storey.ObjectPlacement = local_placement(None, elevation)
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        representation = ifcopenshell.api.geometry.add_wall_representation(
            model, context=body, length=4, height=3, thickness=0.2
        )
        ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=representation)
        ifcopenshell.api.spatial.assign_container(model, products=[wall], relating_structure=storey)
        wall.ObjectPlacement = local_placement(storey.ObjectPlacement, 0.0)
        storeys.append(storey)
    ifcopenshell.api.aggregate.assign_object(model, products=storeys, relating_object=building)

    door = ifcopenshell.api.root.create_entity(model, ifc_class="IfcDoor")
    door_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcDoorType")
    door_type.OperationType = "SINGLE_SWING_LEFT"
    ifcopenshell.api.type.assign_type(model, related_objects=[door], relating_type=door_type)
    representation = ifcopenshell.api.geometry.add_wall_representation(
        model, context=body, length=0.9, height=2.1, thickness=0.05
    )
    ifcopenshell.api.geometry.assign_representation(model, product=door, representation=representation)
    ifcopenshell.api.spatial.assign_container(model, products=[door], relating_structure=storeys[0])
    door.ObjectPlacement = local_placement(storeys[0].ObjectPlacement, 0.0)
    return model, door


def test_svg_door_arc_only_on_the_storey_that_cuts_the_door(tmp_path):
    model, door = _create_model_with_door_on_lower_storey()
    settings = ifcopenshell.geom.settings()
    settings.set("section-height-from-storeys", True)
    settings.set("door-arcs", True)
    path = tmp_path / "plan.svg"
    serializer = ifcopenshell.geom.serializers.svg(str(path), settings)
    serializer.setFile(model)
    serializer.writeHeader()
    for shape in ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(settings, model, 1)):
        serializer.write(shape)
    serializer.finalize()
    del serializer

    svg = path.read_text()
    assert svg.count("IfcBuildingStorey") == 2
    assert svg.count(door.GlobalId) == 1
