"""Package tests that fail when OpenCASCADE is duplicated across plug-ins.

Release packages once statically linked a private OCCT copy into every geometry
plug-in.  Each copy owns its own Standard_Type registry, typeinfo and allocator, so
a TopoDS_Shape created by the OpenCASCADE kernel plug-in and consumed by another
plug-in (the brep tree backend, the SVG serializer) is misread: tree.select()
returns nothing or raises SWIG's "An unknown error occurred", the SVG serializer
raises the same or aborts, and Bonsai drawings come out blank.  Geometry conversion
alone stays bit-identical, so no existing test noticed.

These tests exercise exactly those cross-plug-in hand-offs.  They are meant to run
against the *packaged* binaries in the release build workflows (see
run_against_package.py), where CI's source build against one shared system OCCT
can never reproduce the problem.
"""

import os

import ifcopenshell
import ifcopenshell.geom
import pytest

W = ifcopenshell.ifcopenshell_wrapper
HERE = os.path.dirname(os.path.abspath(__file__))
# A fixture from the main tree, not from the `test/input` submodule, so a bare checkout works.
FIXTURE = os.environ.get("IFCOPENSHELL_PACKAGE_TEST_FIXTURE") or os.path.join(
    HERE, "..", "..", "src", "ifcopenshell-python", "test", "fixtures", "ColumnPSetsOfSets.ifc"
)


@pytest.fixture(scope="module")
def model():
    return ifcopenshell.open(FIXTURE)


@pytest.fixture(scope="module")
def column(model):
    return model.by_type("IfcColumn")[0]


@pytest.fixture(scope="module")
def column_centre(column):
    """A point inside the column, computed from triangulated output that never leaves the kernel plug-in."""
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), column)
    verts = shape.geometry.verts
    n = len(verts) // 3
    cx, cy, cz = (sum(verts[i::3]) / n for i in range(3))
    m = shape.transformation.matrix  # 16 values; translation in the last column when row-major
    if abs(m[15] - 1) < 1e-12 and all(abs(m[12 + c]) < 1e-12 for c in range(3)):
        return tuple(float(m[r * 4 + 0] * cx + m[r * 4 + 1] * cy + m[r * 4 + 2] * cz + m[r * 4 + 3]) for r in range(3))
    return tuple(float(m[0 + r] * cx + m[4 + r] * cy + m[8 + r] * cz + m[12 + r]) for r in range(3))


def native_settings():
    s = ifcopenshell.geom.settings()
    s.set("iterator-output", W.NATIVE)  # brep elements select the opencascade.brep tree backend
    return s


def test_brep_tree_add_element_then_select(model, column, column_centre):
    """Kernel plug-in creates the TopoDS_Shape; the brep tree plug-in reads it."""
    tree = ifcopenshell.geom.tree()
    it = ifcopenshell.geom.iterator(native_settings(), model)
    assert it.initialize()
    while True:
        elem = it.get()
        assert type(elem).__name__ == "native_element", type(elem).__name__
        tree.add_element(elem)
        if not it.next():
            break

    # On a duplicated-OCCT package this raises RuntimeError("An unknown error occurred") or returns ().
    hits = tree.select(column_centre)
    assert column in hits, hits
    assert column in tree.select(column), "an element must select itself"


def test_brep_tree_add_file_then_select(model, column, column_centre):
    """Same hand-off through the tree's own iterator (tree(file, settings))."""
    tree = ifcopenshell.geom.tree(model, native_settings())
    assert column in tree.select(column_centre)


def test_svg_serializer(model, column, column_centre):
    """Mirror Bonsai's drawing generator: NATIVE elements into the SVG serializer plug-in."""
    s = native_settings()
    s.set("dimensionality", W.CURVES_SURFACES_AND_SOLIDS)
    s.set("section-height", column_centre[2])
    for key, value in [
        ("svg-without-storeys", True),
        ("svg-write-poly", True),
        ("svg-poly", True),
        ("svg-xmlns", True),
        ("svg-project", True),
        ("auto-elevation", False),
        ("auto-section", False),
    ]:
        s.set(key, value)
    buf = ifcopenshell.geom.serializers.buffer()
    ser = ifcopenshell.geom.serializers.svg(buf, s)
    ser.setFile(model)
    ser.writeHeader()
    it = ifcopenshell.geom.iterator(s, model)
    assert it.initialize()
    while True:
        ser.write(it.get())  # raises "An unknown error occurred" on a duplicated-OCCT package
        if not it.next():
            break
    ser.finalize()
    svg = buf.get_value()
    assert "<svg" in svg
    assert "<path" in svg or "<polyline" in svg or "<polygon" in svg, svg
