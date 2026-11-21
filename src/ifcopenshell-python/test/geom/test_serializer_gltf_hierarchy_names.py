# This file was generated with the assistance of an AI coding tool.

import json
import struct

import pytest

import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.geom


def _create_model():
    model = ifcopenshell.api.project.create_file()
    project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="Project")
    ifcopenshell.api.unit.assign_unit(model)
    context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )
    site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name="Building")
    ifcopenshell.api.aggregate.assign_object(model, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(model, products=[building], relating_object=site)
    parents = {site: None, building: site}
    for storey_name in ("Lower", "Upper"):
        storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name=storey_name)
        ifcopenshell.api.aggregate.assign_object(model, products=[storey], relating_object=building)
        parents[storey] = building
        for wall_name in ("First", "Second"):
            wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall", name=f"{storey_name} {wall_name}")
            ifcopenshell.api.spatial.assign_container(model, products=[wall], relating_structure=storey)
            representation = ifcopenshell.api.geometry.add_wall_representation(
                model, context=body, length=4, height=3, thickness=0.2
            )
            ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=representation)
            ifcopenshell.api.geometry.edit_object_placement(model, product=wall)
            parents[wall] = storey
    return model, parents


def _write_node_parents(model, path, naming):
    settings = ifcopenshell.geom.settings()
    settings.set("apply-default-materials", True)
    settings.set("element-hierarchy", True)
    settings.set(naming, True)
    serializer = ifcopenshell.geom.serializers.glb(str(path), settings)
    serializer.setFile(model)
    serializer.writeHeader()
    for shape in ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(settings, model, 1)):
        serializer.write(shape)
    serializer.finalize()
    del serializer
    data = path.read_bytes()
    nodes = json.loads(data[20 : 20 + struct.unpack_from("<I", data, 12)[0]])["nodes"]
    parent_names = {}
    for node in nodes:
        for child in node.get("children", []):
            parent_names[child] = node.get("name", "")
    return sorted((node["name"], parent_names.get(index, "")) for index, node in enumerate(nodes) if "name" in node)


@pytest.mark.parametrize(
    "naming,attribute", [("use-element-guids", "GlobalId"), ("use-element-names", "Name")], ids=["guids", "names"]
)
def test_gltf_hierarchy_nodes_are_named_after_their_own_element(tmp_path, naming, attribute):
    model, parents = _create_model()
    expected = sorted(
        (getattr(element, attribute), getattr(parent, attribute) if parent else "")
        for element, parent in parents.items()
    )
    assert _write_node_parents(model, tmp_path / "model.glb", naming) == expected
