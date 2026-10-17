# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom


def _create_model_with_boxes(count):
    model = ifcopenshell.api.project.create_file()
    ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    body = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=ifcopenshell.api.context.add_context(model, context_type="Model"),
    )
    for i in range(count):
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        representation = ifcopenshell.api.geometry.add_wall_representation(
            model, context=body, length=4, height=3, thickness=0.2
        )
        ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=representation)
        point = model.createIfcCartesianPoint((0.0, 10.0 * i, 0.0))
        wall.ObjectPlacement = model.createIfcLocalPlacement(None, model.createIfcAxis2Placement3D(point))
    return model


def _write_obj(tmp_path, model, **options):
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", False)
    settings.set("use-world-coords", True)
    for key, value in options.items():
        settings.set(key.replace("_", "-"), value)
    path = tmp_path / "model.obj"
    serializer = ifcopenshell.geom.serializers.obj(str(path), str(tmp_path / "model.mtl"), settings)
    serializer.setFile(model)
    serializer.writeHeader()
    for shape in ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(settings, model, 1)):
        serializer.write(shape)
    serializer.finalize()
    del serializer
    return [line.split() for line in path.read_text().splitlines()]


def _corners(lines):
    positions = [tuple(map(float, line[1:])) for line in lines if line[0] == "v"]
    normals = [tuple(map(float, line[1:])) for line in lines if line[0] == "vn"]
    for line in lines:
        if line[0] == "f":
            for corner in line[1:]:
                indices = corner.split("/")
                yield positions[int(indices[0]) - 1], normals[int(indices[2]) - 1]


@pytest.mark.parametrize("generate_uvs", [False, True], ids=["plain", "uvs"])
def test_obj_box_shares_positions_and_normals_between_corners(tmp_path, generate_uvs):
    lines = _write_obj(tmp_path, _create_model_with_boxes(2), generate_uvs=generate_uvs)
    assert sum(line[0] == "v" for line in lines) == 2 * 8
    assert sum(line[0] == "vn" for line in lines) == 2 * 6
    corners = list(_corners(lines))
    assert len(corners) == 2 * 12 * 3
    for position, normal in corners:
        offset = sum(p * n for p, n in zip(position, normal))
        box = round(position[1] / 10.0)
        expected = max(4 * normal[0], 0.2 * normal[1], 3 * normal[2]) + 10.0 * box * normal[1]
        assert offset == pytest.approx(expected, abs=1e-9)
