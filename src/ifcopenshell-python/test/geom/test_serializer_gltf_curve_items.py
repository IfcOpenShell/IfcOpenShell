# This file was generated with the assistance of an AI coding tool.

import json
import struct
import subprocess
import sys

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.guid

LINES = 1
TRIANGLES = 4
SOLID_COLOUR = (1.0, 0.0, 0.0)

WRITE_SCRIPT = """import sys; sys.path[:] = [p for p in sys.path if p]
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W

settings = ifcopenshell.geom.settings()
settings.set("dimensionality", W.CURVES_SURFACES_AND_SOLIDS)
settings.set("weld-vertices", False)
settings.set("apply-default-materials", True)
model = ifcopenshell.open(sys.argv[1])
serializer = ifcopenshell.geom.serializers.glb(sys.argv[2], settings)
serializer.setFile(model)
serializer.writeHeader()
for shape in ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(settings, model, 1)):
    serializer.write(shape)
serializer.finalize()
"""

models = pytest.mark.parametrize(
    "schema,layout",
    [
        ("IFC4", "sc"),
        ("IFC4", "cs"),
        ("IFC4", "cscsc"),
        ("IFC2X3", "sc"),
        ("IFC2X3", "cs"),
        ("IFC2X3", "cscsc"),
    ],
    ids=[
        "ifc4-solid-first",
        "ifc4-curve-first",
        "ifc4-interleaved",
        "ifc2x3-solid-first",
        "ifc2x3-curve-first",
        "ifc2x3-interleaved",
    ],
)


def _curve_points(index):
    x = 5.0 + 3.0 * index
    return [(x, 0.0, 0.0), (x + 1.0, 0.0, 0.0), (x + 1.0, 1.0, 0.0)]


def _create_model(schema, layout):
    model = ifcopenshell.file(schema=schema)
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Project", None, None, None, None, [context], units)

    items = []
    for index, kind in enumerate(layout):
        if kind == "c":
            item = model.createIfcPolyline([model.createIfcCartesianPoint(p) for p in _curve_points(index)])
        else:
            position = model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((3.0 * index, 0.0)), None)
            profile = model.createIfcRectangleProfileDef("AREA", None, position, 1.0, 1.0)
            item = model.createIfcExtrudedAreaSolid(profile, placement, model.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
            rendering = model.createIfcSurfaceStyleRendering(model.createIfcColourRgb(None, *SOLID_COLOUR))
            rendering.ReflectanceMethod = "FLAT"
            style = model.createIfcSurfaceStyle("Solid", "BOTH", [rendering])
            if schema == "IFC2X3":
                style = model.createIfcPresentationStyleAssignment([style])
            model.createIfcStyledItem(item, [style], None)
        items.append(item)
    representation = model.createIfcShapeRepresentation(context, "Body", "GeometricSet", items)
    model.createIfcBuildingElementProxy(
        ifcopenshell.guid.new(),
        None,
        "Proxy",
        None,
        None,
        model.createIfcLocalPlacement(None, placement),
        model.createIfcProductDefinitionShape(None, None, [representation]),
        None,
        None,
    )
    return model


def _read_accessor(document, binary, index):
    accessor = document["accessors"][index]
    view = document["bufferViews"][accessor["bufferView"]]
    width = {"SCALAR": 1, "VEC3": 3}[accessor["type"]]
    dtype = {5125: "<u4", 5126: "<f4"}[accessor["componentType"]]
    assert accessor["count"] * width * 4 <= view["byteLength"]
    assert view["byteOffset"] + view["byteLength"] <= document["buffers"][0]["byteLength"] <= len(binary)
    values = np.frombuffer(binary, dtype=dtype, count=accessor["count"] * width, offset=view["byteOffset"])
    return values.reshape(-1, width)


def _write_primitives(tmp_path, schema, layout):
    ifc_path = tmp_path / "model.ifc"
    glb_path = tmp_path / "model.glb"
    _create_model(schema, layout).write(str(ifc_path))
    result = subprocess.run([sys.executable, "-c", WRITE_SCRIPT, str(ifc_path), str(glb_path)])
    assert result.returncode == 0
    data = glb_path.read_bytes()
    assert struct.unpack_from("<I", data, 8)[0] == len(data)
    json_length = struct.unpack_from("<I", data, 12)[0]
    document = json.loads(data[20 : 20 + json_length])
    binary = data[28 + json_length :]
    (mesh,) = document["meshes"]
    primitives = []
    for primitive in mesh["primitives"]:
        indices = _read_accessor(document, binary, primitive["indices"])[:, 0]
        positions = _read_accessor(document, binary, primitive["attributes"]["POSITION"]).astype(float)
        assert indices.max() < len(positions)
        normals = None
        if "NORMAL" in primitive["attributes"]:
            normals = _read_accessor(document, binary, primitive["attributes"]["NORMAL"]).astype(float)
            assert len(normals) == len(positions)
        material = document["materials"][primitive["material"]]["pbrMetallicRoughness"]["baseColorFactor"]
        primitives.append((primitive["mode"], indices, positions, normals, tuple(material[:3])))
    return primitives


@models
def test_gltf_triangles_of_representation_with_curve_items(tmp_path, schema, layout):
    triangles = [p for p in _write_primitives(tmp_path, schema, layout) if p[0] == TRIANGLES]
    assert triangles
    covered = set()
    for _, indices, positions, normals, colour in triangles:
        assert colour == pytest.approx(SOLID_COLOUR)
        assert len(indices) % 3 == 0
        for triangle in indices.reshape(-1, 3):
            corners = positions[triangle]
            expected = np.cross(corners[1] - corners[0], corners[2] - corners[0])
            expected /= np.linalg.norm(expected)
            for normal in normals[triangle]:
                assert normal == pytest.approx(expected, abs=1e-6)
            covered.add(int(np.floor(corners[:, 0].min() / 3.0 + 0.5)))
    assert covered == {index for index, kind in enumerate(layout) if kind == "s"}


@models
def test_gltf_lines_of_representation_with_curve_items(tmp_path, schema, layout):
    lines = [p for p in _write_primitives(tmp_path, schema, layout) if p[0] == LINES]
    assert lines
    segments = set()
    for _, indices, positions, normals, colour in lines:
        assert colour != pytest.approx(SOLID_COLOUR)
        assert normals is None
        assert len(indices) % 2 == 0
        for segment in indices.reshape(-1, 2):
            segments.add(frozenset(tuple(float(c) for c in np.round(positions[segment[i]], 6)) for i in range(2)))
    expected = set()
    for index, kind in enumerate(layout):
        if kind == "c":
            points = _curve_points(index)
            expected |= {frozenset(points[0:2]), frozenset(points[1:3])}
    assert segments == expected
