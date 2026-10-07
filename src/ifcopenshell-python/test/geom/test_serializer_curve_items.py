# This file was generated with the assistance of an AI coding tool.

import subprocess
import sys
import xml.etree.ElementTree as ET

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.shape

CURVE_POINTS = [(5.0, 0.0, 0.0), (6.0, 0.0, 0.0), (6.0, 1.0, 0.0)]

WRITE_SCRIPT = """
import sys
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W

settings = ifcopenshell.geom.settings()
settings.set("dimensionality", W.CURVES_SURFACES_AND_SOLIDS)
settings.set("weld-vertices", False)
settings.set("apply-default-materials", True)
model = ifcopenshell.open(sys.argv[1])
if sys.argv[2].endswith(".obj"):
    serializer = ifcopenshell.geom.serializers.obj(sys.argv[2], sys.argv[2][:-4] + ".mtl", settings)
else:
    serializer = ifcopenshell.geom.serializers.collada(sys.argv[2], settings)
serializer.setFile(model)
serializer.writeHeader()
for shape in ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(settings, model, 1)):
    serializer.write(shape)
serializer.finalize()
"""

models = pytest.mark.parametrize(
    "schema,curve_first",
    [("IFC4", False), ("IFC4", True), ("IFC2X3", False), ("IFC2X3", True)],
    ids=["ifc4-solid-first", "ifc4-curve-first", "ifc2x3-solid-first", "ifc2x3-curve-first"],
)


def _create_model(schema, curve_first):
    model = ifcopenshell.file(schema=schema)
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Project", None, None, None, None, [context], units)
    curve = model.createIfcPolyline([model.createIfcCartesianPoint(point) for point in CURVE_POINTS])
    position = model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((0.0, 0.0)), None)
    profile = model.createIfcRectangleProfileDef("AREA", None, position, 1.0, 1.0)
    solid = model.createIfcExtrudedAreaSolid(profile, placement, model.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
    items = [curve, solid] if curve_first else [solid, curve]
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


def _write(tmp_path, schema, curve_first, extension):
    ifc_path = tmp_path / "model.ifc"
    out_path = tmp_path / f"model.{extension}"
    _create_model(schema, curve_first).write(str(ifc_path))
    result = subprocess.run([sys.executable, "-c", WRITE_SCRIPT, str(ifc_path), str(out_path)])
    assert result.returncode == 0
    return out_path


def _assert_corner_normals_match_triangles(corners):
    assert corners
    for positions, normals in corners:
        expected = np.cross(positions[1] - positions[0], positions[2] - positions[0])
        expected /= np.linalg.norm(expected)
        for normal in normals:
            assert normal == pytest.approx(expected, abs=1e-6)


def _assert_lines_follow_curve(segments):
    expected = {frozenset(CURVE_POINTS[0:2]), frozenset(CURVE_POINTS[1:3])}
    assert {frozenset(tuple(float(c) for c in np.round(p, 6)) for p in segment) for segment in segments} == expected


@models
def test_triangulation_normals_stay_with_their_vertices(schema, curve_first):
    settings = ifcopenshell.geom.settings()
    settings.set("dimensionality", W.CURVES_SURFACES_AND_SOLIDS)
    settings.set("weld-vertices", False)
    model = _create_model(schema, curve_first)
    geometry = ifcopenshell.geom.create_shape(settings, model.by_type("IfcBuildingElementProxy")[0]).geometry
    verts = ifcopenshell.util.shape.get_vertices(geometry)
    normals = ifcopenshell.util.shape.get_normals(geometry)
    faces = ifcopenshell.util.shape.get_faces(geometry)
    _assert_corner_normals_match_triangles([(verts[face], normals[face]) for face in faces])


@models
def test_obj_normal_indices_with_curve_item(tmp_path, schema, curve_first):
    lines = [line.split() for line in _write(tmp_path, schema, curve_first, "obj").read_text().splitlines()]
    positions = np.array([line[1:] for line in lines if line[0] == "v"], dtype=float)
    normals = np.array([line[1:] for line in lines if line[0] == "vn"], dtype=float)
    corners = []
    for line in lines:
        if line[0] == "f":
            indices = np.array([corner.split("/") for corner in line[1:]])
            corners.append((positions[indices[:, 0].astype(int) - 1], normals[indices[:, 2].astype(int) - 1]))
    _assert_corner_normals_match_triangles(corners)
    _assert_lines_follow_curve([positions[np.array(line[1:], dtype=int) - 1] for line in lines if line[0] == "l"])


@models
def test_collada_with_curve_item(tmp_path, schema, curve_first):
    root = ET.parse(_write(tmp_path, schema, curve_first, "dae")).getroot()
    ns = {"c": root.tag[1:].split("}")[0]}
    mesh = root.find(".//c:mesh", ns)
    sources = {
        source.get("id").rsplit("-", 1)[-1]: np.array(source.find("c:float_array", ns).text.split(), dtype=float)
        for source in mesh.iterfind("c:source", ns)
    }
    positions = sources["positions"].reshape(-1, 3)
    normals = sources["normals"].reshape(-1, 3)
    corners = []
    for triangles in mesh.iterfind("c:triangles", ns):
        indices = np.array(triangles.find("c:p", ns).text.split(), dtype=int).reshape(-1, 3, 2)
        corners.extend((positions[triangle[:, 0]], normals[triangle[:, 1]]) for triangle in indices)
    _assert_corner_normals_match_triangles(corners)
    segments = []
    for lines in mesh.iterfind("c:lines", ns):
        segments.extend(positions[np.array(lines.find("c:p", ns).text.split(), dtype=int).reshape(-1, 2)])
    _assert_lines_follow_curve(segments)
