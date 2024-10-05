import collections

import numpy as np
import ifcopenshell
import ifcopenshell.geom

import pytest

from test.bootstrap import file


@pytest.mark.parametrize("file", ["geom/polygonal-face-tessellation.ifc"], indirect=True)
def test_polyhedral_setting(file):
    s = ifcopenshell.geom.settings()
    # default is triangle mesh
    assert s.get("triangulation-type") == ifcopenshell.ifcopenshell_wrapper.TRIANGLE_MESH
    s = ifcopenshell.geom.settings(TRIANGULATION_TYPE=ifcopenshell.ifcopenshell_wrapper.POLYHEDRON_WITHOUT_HOLES)
    obj = ifcopenshell.geom.create_shape(s, file[30])
    # outer:
    #   - top
    #   - left
    #   - bottom
    #   - right
    #   - back;
    # inner:
    #   - top
    #   - left
    #   - bottom
    #   - right
    #   - back;
    # front:
    #   - 8 triangles
    # --------------------- +
    #     18 facets
    assert len(obj.geometry.faces) == 18
    s = ifcopenshell.geom.settings(TRIANGULATION_TYPE=ifcopenshell.ifcopenshell_wrapper.POLYHEDRON_WITH_HOLES)
    obj = ifcopenshell.geom.create_shape(s, file[30])
    # outer:
    #   - top
    #   - left
    #   - bottom
    #   - right
    #   - back;
    # inner:
    #   - top
    #   - left
    #   - bottom
    #   - right
    #   - back;
    # front:
    #   - single facet with 2 bounds
    # --------------------- +
    #     11 facets
    assert len(obj.geometry.faces) == 11
    # 10 facets with 1 bound, 1 facet with 2 bounds
    assert sorted(collections.Counter(map(len, obj.geometry.faces)).items()) == [(1, 10), (2, 1)]


def get_edges(inst):
    coords = inst.Coordinates.CoordList
    for f in inst.Faces:

        def emit(loop):
            fcoords = list(map(lambda i: coords[i - 1], loop))
            shifted = fcoords[1:] + [fcoords[0]]
            return map(frozenset, zip(fcoords, shifted))

        yield from emit(f.CoordIndex)

        if f.is_a("IfcIndexedPolygonalFaceWithVoids"):
            for inner in f.InnerCoordIndices:
                yield from emit(inner)


@pytest.mark.parametrize("file", ["geom/polygonal-face-tessellation.ifc"], indirect=True)
@pytest.mark.parametrize("geometry_library", ["opencascade", "cgal", "cgal-simple"])
def test_correct_edges(file, geometry_library):
    s = ifcopenshell.geom.settings()
    obj = ifcopenshell.geom.create_shape(s, file[30], geometry_library=geometry_library)
    vs = np.array(obj.geometry.verts).reshape((-1, 3))
    eds = np.array(obj.geometry.edges).reshape((-1, 2))
    edge_collection_1 = set(map(lambda t: frozenset(map(tuple, t)), (vs[eds] * 1000).tolist()))
    rep = file[30].Representation.Representations[0].Items[0]
    edge_collection_2 = set(get_edges(rep))
    assert edge_collection_1 == edge_collection_2
