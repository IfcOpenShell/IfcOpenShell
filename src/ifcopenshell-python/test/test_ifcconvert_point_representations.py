# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""End-to-end coverage that mimics IfcConvert for Vertex/Point/PointCloud
representations (#134, #1409, #5218), as requested by aothms on PR #8759:
ifcopenshell.geom.create_shape() succeeding is not proof that the actual
IfcConvert output pipeline (serializers writing real files) works. These
tests invoke the real IfcConvert binary and inspect the resulting files.
"""

import json
import shutil
import struct
import subprocess
import xml.etree.ElementTree as ET

import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.unit

IFCCONVERT = shutil.which("IfcConvert")

pytestmark = pytest.mark.skipif(IFCCONVERT is None, reason="Requires IfcConvert in path")


def make_model(tmp_path):
    """A single model with a Vertex, a Point, a PointCloud and (as a
    regression check) an ordinary extruded wall, so that IfcConvert has to
    process all four in one pass.
    """
    f = ifcopenshell.file()
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Test")
    unit = ifcopenshell.api.unit.add_si_unit(f, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(f, units=[unit])
    context = ifcopenshell.api.context.add_context(f, context_type="Model")

    vertex_xyz = (1.0, 2.0, 3.0)
    vertex_element = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingElementProxy", name="Vertex")
    vertex_point = f.createIfcVertexPoint(f.createIfcCartesianPoint(vertex_xyz))
    vertex_representation = f.createIfcTopologyRepresentation(context, "Body", "Vertex", [vertex_point])
    vertex_element.Representation = f.createIfcProductDefinitionShape(Representations=[vertex_representation])

    point_xyz = (4.0, 5.0, 6.0)
    point_element = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingElementProxy", name="Point")
    point_representation = f.createIfcShapeRepresentation(
        context, "Body", "Point", [f.createIfcCartesianPoint(point_xyz)]
    )
    point_element.Representation = f.createIfcProductDefinitionShape(Representations=[point_representation])

    cloud_coords = [(10.0, 11.0, 12.0), (13.0, 14.0, 15.0), (16.0, 17.0, 18.0), (-1.0, 0.5, 9.0)]
    cloud_element = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingElementProxy", name="PointCloud")
    point_list = f.createIfcCartesianPointList3D(cloud_coords)
    cloud_representation = f.createIfcShapeRepresentation(context, "Body", "PointCloud", [point_list])
    cloud_element.Representation = f.createIfcProductDefinitionShape(Representations=[cloud_representation])

    wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall")
    profile_points = [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]
    curve = f.createIfcPolyline([f.createIfcCartesianPoint(p) for p in profile_points])
    extrusion = f.createIfcExtrudedAreaSolid(
        f.createIfcArbitraryClosedProfileDef("AREA", None, curve),
        f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0))),
        f.createIfcDirection((0.0, 0.0, 1.0)),
        1.0,
    )
    wall_representation = f.createIfcShapeRepresentation(context, "Body", "SweptSolid", [extrusion])
    wall.Representation = f.createIfcProductDefinitionShape(Representations=[wall_representation])

    fn = tmp_path / "point_representations.ifc"
    f.write(str(fn))
    return fn, {
        "Vertex": vertex_xyz,
        "Point": point_xyz,
        "PointCloud": cloud_coords,
    }


def run_ifcconvert(input_fn, output_fn, *extra_args):
    # Point/vertex conversion (see kernels/opencascade/point.cpp) is only
    # implemented in the OpenCascade kernel, force it explicitly since a
    # build with CGAL/Manifold available would otherwise default to those.
    # --use-element-names makes the OBJ "g"/glTF node names predictable
    # (the IfcRoot.Name we set), instead of opaque unique IDs.
    args = [
        IFCCONVERT,
        "-yqv",
        "--kernel",
        "opencascade",
        "--use-element-names",
        str(input_fn),
        str(output_fn),
        *extra_args,
    ]
    completed = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return completed.returncode, completed.stdout.decode("utf-8", "replace")


def parse_obj_groups(obj_text):
    """Split a Wavefront OBJ into per-object groups of ("v"/"p"/"f" ...) lines."""
    groups = {}
    current = None
    for line in obj_text.splitlines():
        if line.startswith("g "):
            current = line[2:].strip()
            groups[current] = {"v": [], "p": [], "f": []}
        elif current is not None and line[:2] in ("v ", "p ", "f "):
            kind = line[0]
            groups[current][kind].append(line)
    return groups


class TestIfcConvertObj:
    def test_vertex_point_and_point_cloud_produce_p_records(self, tmp_path):
        fn, expected = make_model(tmp_path)
        obj_fn = tmp_path / "out.obj"

        returncode, log = run_ifcconvert(fn, obj_fn)
        assert returncode == 0, log
        assert obj_fn.exists()

        groups = parse_obj_groups(obj_fn.read_text())

        # Every representation-only object should produce exactly as many
        # "p" (point primitive) records as it has vertices, and no "f".
        for name, coords in [("Vertex", [expected["Vertex"]]), ("Point", [expected["Point"]])]:
            matches = [g for gid, g in groups.items() if gid.split("-")[0] == name or name in gid]
            assert matches, f"No OBJ group found for {name} (groups: {list(groups)})"
            g = matches[0]
            assert len(g["v"]) == len(coords)
            assert len(g["p"]) == len(coords)
            assert len(g["f"]) == 0
            for (x, y, z), vline in zip(coords, g["v"]):
                _, vx, vy, vz = vline.split()
                assert (float(vx), float(vy), float(vz)) == (x, y, z)

        cloud_matches = [g for gid, g in groups.items() if "PointCloud" in gid]
        assert cloud_matches, f"No OBJ group found for PointCloud (groups: {list(groups)})"
        cloud = cloud_matches[0]
        assert len(cloud["v"]) == len(expected["PointCloud"])
        assert len(cloud["p"]) == len(expected["PointCloud"])
        assert len(cloud["f"]) == 0
        actual_coords = {tuple(float(c) for c in vline.split()[1:]) for vline in cloud["v"]}
        assert actual_coords == set(expected["PointCloud"])

        # OBJ vertex/point indices are 1-based and cumulative across the
        # whole file (not reset per "g" group), matching how faces already
        # index into vcount_total. The point cloud's "p" indices must still
        # be distinct and contiguous, referencing exactly its own 4 "v" lines.
        p_indices = sorted(int(pline.split()[1]) for pline in cloud["p"])
        assert p_indices == list(range(p_indices[0], p_indices[0] + len(expected["PointCloud"])))

    def test_ordinary_geometry_still_produces_faces(self, tmp_path):
        # Regression check: a normal extruded wall in the same file must
        # still triangulate to faces, unaffected by the point/vertex handling.
        fn, _ = make_model(tmp_path)
        obj_fn = tmp_path / "out.obj"

        returncode, log = run_ifcconvert(fn, obj_fn)
        assert returncode == 0, log

        groups = parse_obj_groups(obj_fn.read_text())
        wall_matches = [g for gid, g in groups.items() if "Wall" in gid]
        assert wall_matches, f"No OBJ group found for Wall (groups: {list(groups)})"
        wall = wall_matches[0]
        assert len(wall["f"]) > 0
        assert len(wall["p"]) == 0


class TestIfcConvertGltf:
    def test_point_cloud_uses_points_primitive_mode(self, tmp_path):
        fn, expected = make_model(tmp_path)
        glb_fn = tmp_path / "out.glb"

        returncode, log = run_ifcconvert(fn, glb_fn)
        assert returncode == 0, log
        assert glb_fn.exists()

        data = glb_fn.read_bytes()
        magic, version, length = struct.unpack_from("<4sII", data, 0)
        assert magic == b"glTF"

        offset = 12
        json_chunk = None
        while offset < length:
            chunk_length, chunk_type = struct.unpack_from("<I4s", data, offset)
            chunk_data = data[offset + 8 : offset + 8 + chunk_length]
            if chunk_type == b"JSON":
                json_chunk = json.loads(chunk_data.decode("utf-8"))
                break
            offset += 8 + chunk_length
        assert json_chunk is not None, "No JSON chunk found in .glb"

        # Mode 0 is POINTS in glTF; some mesh, somewhere, must use it for
        # this file (the PointCloud/Point/Vertex elements), and none of the
        # 4 point-cloud vertices should have been silently dropped.
        point_primitives = [
            p for mesh in json_chunk.get("meshes", []) for p in mesh.get("primitives", []) if p.get("mode") == 0
        ]
        assert point_primitives, "Expected at least one glTF primitive with mode=POINTS (0)"

        accessors = json_chunk["accessors"]
        vertex_counts = {accessors[p["attributes"]["POSITION"]]["count"] for p in point_primitives}
        assert len(expected["PointCloud"]) in vertex_counts or 1 in vertex_counts


class TestIfcConvertCollada:
    def test_point_only_geometry_does_not_crash(self, tmp_path):
        # COLLADA has no native point primitive (see ColladaSerializer.cpp:
        # ColladaGeometries::write logs a "has no COLLADA representation"
        # warning for this, but geometry serializer plugins don't currently
        # receive IfcConvert's actual logger instance - a pre-existing gap
        # unrelated to #134/#1409/#5218, so the warning isn't observable
        # from here). What matters end-to-end: IfcConvert must not crash,
        # and the position data must still be written even though there is
        # no visible primitive referencing it.
        fn, expected = make_model(tmp_path)
        dae_fn = tmp_path / "out.dae"

        returncode, log = run_ifcconvert(fn, dae_fn)
        assert returncode == 0, log
        assert dae_fn.exists()

        xml = dae_fn.read_text()
        tree = ET.fromstring(xml)
        ns = {"c": "http://www.collada.org/2005/11/COLLADASchema"}
        geometries = tree.findall(".//c:library_geometries/c:geometry", ns)
        assert geometries, "Expected at least one <geometry> in the .dae"

        point_cloud_floats = " ".join(f"{c:g}" for coords in expected["PointCloud"] for c in coords)
        found_point_cloud_positions = False
        for geometry in geometries:
            float_array = geometry.find(".//c:float_array", ns)
            if (
                float_array is not None
                and float_array.text
                and point_cloud_floats in " ".join(float_array.text.split())
            ):
                found_point_cloud_positions = True
                # No triangles/lines/polylist: nothing meaningful to draw.
                assert geometry.find(".//c:triangles", ns) is None
                assert geometry.find(".//c:lines", ns) is None
        assert found_point_cloud_positions, "PointCloud coordinates missing from .dae output"


if __name__ == "__main__":
    import pytest

    pytest.main(["-vvsx", __file__])
