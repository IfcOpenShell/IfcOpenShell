"""Package tests that fail when a packaged shared library can't be loaded.

Plug-ins are loaded at runtime, so a missing library only shows up when its plug-in
is loaded, and often as a "missing plug-in" error.  These tests load every plug-in.

Not covered currently - local dependencies, e.g.:
- locally installed dependencies (system copies of libraries missing from the package)
- dependencies on build artifacts (absolute install names or rpaths into the build tree)
"""

from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import pytest

PACKAGE_DIR = Path(ifcopenshell.__file__).parent


@pytest.mark.parametrize(
    "schema",
    [
        pytest.param("IFC2X3", id="ifcopenshell_parse_schema_ifc2x3"),
        pytest.param("IFC4", id="ifcopenshell_parse_schema_ifc4"),
        pytest.param("IFC4X3_ADD2", id="ifcopenshell_parse_schema_ifc4x3_add2"),
    ],
)
def test_schema_loads(schema: str):
    ifcopenshell.schema_by_name(schema)


@pytest.mark.parametrize(
    "schema",
    [
        pytest.param("IFC2X3", id="ifcopenshell_geometry_mapping_ifc2x3"),
        pytest.param("IFC4", id="ifcopenshell_geometry_mapping_ifc4"),
        pytest.param("IFC4X3_ADD2", id="ifcopenshell_geometry_mapping_ifc4x3_add2"),
    ],
)
def test_geometry_mapping_loads(schema: str):
    ifcopenshell.geom.kernel(ifcopenshell.geom.settings(), ifcopenshell.file(schema=schema), "passthrough")


@pytest.mark.parametrize(
    "kernel",
    [
        pytest.param("opencascade", id="ifcopenshell_geometry_kernel_opencascade"),
        pytest.param("cgal", id="ifcopenshell_geometry_kernel_cgal"),
        pytest.param("cgal-simple", id="ifcopenshell_geometry_kernel_cgalsimple"),
        pytest.param("manifold", id="ifcopenshell_geometry_kernel_manifold"),
        pytest.param("passthrough", id="ifcopenshell_geometry_kernel_passthrough"),
    ],
)
def test_geometry_kernel_loads(kernel: str):
    assert ifcopenshell.geom.has_geometry_library(kernel)


@pytest.mark.parametrize(
    "extension",
    [
        pytest.param("dae", id="ifcopenshell_geometry_dae"),
        pytest.param("glb", id="ifcopenshell_geometry_glb"),
        pytest.param("igs", id="ifcopenshell_geometry_igs"),
        pytest.param("obj", id="ifcopenshell_geometry_obj"),
        pytest.param("stp", id="ifcopenshell_geometry_stp"),
        pytest.param("svg", id="ifcopenshell_geometry_svg"),
        pytest.param("ttl", id="ifcopenshell_geometry_ttl"),
    ],
)
def test_geometry_serializer_loads(extension: str, tmp_path: Path):
    serializer = getattr(ifcopenshell.geom.serializers, extension)
    serializer(str(tmp_path / f"model.{extension}"), ifcopenshell.geom.settings())


@pytest.mark.parametrize([], [pytest.param(id="ifcopenshell_geometry_svgfill")])
def test_svgfill_loads():
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><g class="projection"><path d="M 0,0 L 1,0"/></g></svg>'
    assert ifcopenshell.ifcopenshell_wrapper.svg_to_line_segments(svg, "projection")


@pytest.mark.parametrize(
    "backend",
    [
        pytest.param("opencascade.brep", id="ifcopenshell_geometry_tree_opencascade_brep"),
        pytest.param("opencascade.trianglebvh", id="ifcopenshell_geometry_tree_opencascade_trianglebvh"),
    ],
)
def test_geometry_tree_loads(backend: str):
    ifcopenshell.geom.tree(backend=backend)


@pytest.mark.parametrize([], [pytest.param(id="ifcopenshell_document_rdb")])
def test_document_rdb_loads(tmp_path: Path):
    ifc_path = tmp_path / "model.ifc"
    ifcopenshell.file().write(ifc_path)
    rdb_path = tmp_path / "model.rdb"
    ifcopenshell.convert_path_to_rocksdb(ifc_path, rdb_path)
    assert rdb_path.exists()


def test_every_plugin_is_tested():
    tested = {
        param.id
        for test in list(globals().values())
        for mark in getattr(test, "pytestmark", [])
        if mark.name == "parametrize"
        for param in mark.args[1]
    }
    packaged = {
        path.name.split(".")[0]
        for path in PACKAGE_DIR.iterdir()
        if path.name.startswith("ifcopenshell_") and path.suffix in (".so", ".dylib", ".dll")
    }
    assert packaged == tested
