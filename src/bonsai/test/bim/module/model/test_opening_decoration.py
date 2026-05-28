# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Tests for tool.Geometry.get_dissolved_edges and the opening-decoration cache
layers. The dissolve helper's contract:

- Read-only on the input mesh.
- Returns (verts_local, edge_indices) indexed into the dissolved bmesh.
- Material seams survive (delimit=MATERIAL).
- Default angle threshold is 1°."""

from math import radians

import bmesh
import bpy
import pytest
from mathutils import Matrix, Vector

import bonsai.tool as tool
from bonsai.bim import decorator_cache
from bonsai.bim.module.model import opening as opening_module

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _reset_decoration_caches():
    # Tests share module-global state (dissolve cache + token, world-draw-data
    # cache, batch cache, per-object epochs). Reset every layer so a previous
    # test can't poison hit/miss assertions.
    decorator_cache.reset_for_test()
    opening_module._dissolved_edges_cache.clear()
    opening_module._dissolved_edges_cache_token = -1
    opening_module._world_draw_data_cache.clear()
    opening_module._batch_cache.clear()
    opening_module._object_epochs.clear()
    yield
    decorator_cache.reset_for_test()
    opening_module._dissolved_edges_cache.clear()
    opening_module._world_draw_data_cache.clear()
    opening_module._batch_cache.clear()
    opening_module._object_epochs.clear()


def _make_mesh(name: str, verts: list[tuple[float, float, float]], faces: list[tuple[int, ...]]) -> bpy.types.Mesh:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def _edge_count(mesh: bpy.types.Mesh) -> int:
    bm = bmesh.new()
    bm.from_mesh(mesh)
    n = len(bm.edges)
    bm.free()
    return n


def test_collapses_coplanar_diagonal_on_triangulated_quad():
    # Triangulated unit quad in the XY plane: 4 verts, 2 tris share a diagonal.
    # Raw bmesh has 5 edges (4 quad sides + 1 diagonal). Dissolve must drop the
    # diagonal because both triangles are perfectly coplanar.
    mesh = _make_mesh(
        "quad_tri",
        verts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )
    assert _edge_count(mesh) == 5

    verts, edges = tool.Geometry.get_dissolved_edges(mesh)

    assert len(verts) == 4
    assert len(edges) == 4
    # Every returned edge index must point into the returned verts list.
    for a, b in edges:
        assert 0 <= a < len(verts)
        assert 0 <= b < len(verts)
        assert a != b


def test_preserves_real_edges_on_cube():
    # Default cube has 8 verts / 12 edges / 6 quad faces. There are no coplanar
    # internal splits to dissolve, so the helper must return the cube intact.
    mesh = bpy.data.meshes.new("cube")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()

    verts, edges = tool.Geometry.get_dissolved_edges(mesh)

    assert len(verts) == 8
    assert len(edges) == 12


def test_preserves_material_seam_on_coplanar_split():
    # Two coplanar triangles sharing an edge but each with a different
    # material_index. delimit=MATERIAL must keep the shared edge alive.
    mesh = _make_mesh(
        "split_mat",
        verts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )
    mat_a = bpy.data.materials.new("mat_a")
    mat_b = bpy.data.materials.new("mat_b")
    mesh.materials.append(mat_a)
    mesh.materials.append(mat_b)
    mesh.polygons[0].material_index = 0
    mesh.polygons[1].material_index = 1
    mesh.update()

    verts, edges = tool.Geometry.get_dissolved_edges(mesh)

    # The 4 perimeter edges plus the shared diagonal: 5 total survive.
    assert len(verts) == 4
    assert len(edges) == 5

    bpy.data.materials.remove(mat_a)
    bpy.data.materials.remove(mat_b)


def test_does_not_mutate_input_mesh():
    # The helper must be read-only: viewport draw handlers call it every frame
    # and any obj.data mutation would race the depsgraph and trigger redraws.
    mesh = _make_mesh(
        "ro_quad",
        verts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )
    edges_before = _edge_count(mesh)
    verts_before = len(mesh.vertices)

    tool.Geometry.get_dissolved_edges(mesh)

    assert _edge_count(mesh) == edges_before
    assert len(mesh.vertices) == verts_before


def test_accepts_explicit_angle_limit():
    # Smoke: the angle_limit kwarg must be honored end-to-end (not silently
    # ignored). With a near-zero threshold, even sub-degree coplanar splits
    # survive; with a generous threshold, they collapse.
    mesh = _make_mesh(
        "quad_tri",
        verts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )

    _, edges_zero = tool.Geometry.get_dissolved_edges(mesh, angle_limit=0.0)
    _, edges_default = tool.Geometry.get_dissolved_edges(mesh)

    assert len(edges_zero) > len(edges_default), "angle_limit=0 must preserve more edges than the default 1° dissolve"


def test_cache_serves_identical_object_on_repeat_call():
    # Without caching, the helper rebuilds verts/edges every viewport redraw.
    # Identity (`is`) — not equality — proves the second call hit the cache
    # rather than recomputing identical content.
    mesh = _make_mesh(
        "cached",
        verts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )
    first = opening_module._get_cached_dissolved_edges(mesh)
    second = opening_module._get_cached_dissolved_edges(mesh)

    assert first is second


def test_cache_invalidates_on_decorator_token_bump():
    # depsgraph_update_post / undo / redo / load all bump the shared decorator
    # token; this cache must clear when the token changes so a downstream
    # depsgraph edit (mesh content changed) is reflected on the next call.
    mesh = _make_mesh(
        "bumped",
        verts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )
    first = opening_module._get_cached_dissolved_edges(mesh)
    decorator_cache._DECORATOR_CACHE_TOKEN += 1
    second = opening_module._get_cached_dissolved_edges(mesh)

    assert first is not second, "token bump must invalidate the cache entry"
    assert len(first[0]) == len(second[0])
    assert len(first[1]) == len(second[1])


def test_cache_partitions_entries_by_mesh_identity():
    # Two distinct meshes share the same epoch; both must coexist in the cache
    # so multi-opening frames don't thrash.
    mesh_a = _make_mesh(
        "a",
        verts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )
    mesh_b = _make_mesh(
        "b",
        verts=[(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )

    a_first = opening_module._get_cached_dissolved_edges(mesh_a)
    b_first = opening_module._get_cached_dissolved_edges(mesh_b)
    a_second = opening_module._get_cached_dissolved_edges(mesh_a)

    assert a_first is a_second, "mesh_a entry must survive an interleaved mesh_b call"
    assert a_first is not b_first


def test_cache_partitions_entries_by_angle_limit():
    # Same mesh, different angle_limit → different cached results. Hardens
    # against a future caller introducing a per-opening threshold override.
    mesh = _make_mesh(
        "partitioned",
        verts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )
    tight = opening_module._get_cached_dissolved_edges(mesh, angle_limit=0.0)
    loose = opening_module._get_cached_dissolved_edges(mesh, angle_limit=radians(1.0))
    tight_again = opening_module._get_cached_dissolved_edges(mesh, angle_limit=0.0)

    assert tight is tight_again
    assert tight is not loose


# --- world-data cache (_get_cached_world_draw_data) ---------------------------


def _make_object(name: str, mesh: bpy.types.Mesh) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _make_triangulated_quad_obj(name: str) -> bpy.types.Object:
    mesh = _make_mesh(
        name,
        verts=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        faces=[(0, 1, 2), (0, 2, 3)],
    )
    return _make_object(name, mesh)


def test_world_data_cache_returns_four_tuple_with_expected_shapes():
    obj = _make_triangulated_quad_obj("shape")
    line_verts, verts, edges_indices, tris = opening_module._get_cached_world_draw_data(obj)

    assert len(verts) == 4  # full mesh vert count
    assert len(line_verts) == 4  # dissolved (diagonal collapsed → 4 surviving verts)
    assert len(edges_indices) == 4  # quad outline, no diagonal
    assert len(tris) == 2  # two triangles
    assert all(len(t) == 3 for t in tris)


def test_world_data_cache_hit_returns_identical_tuple_on_repeat_call():
    obj = _make_triangulated_quad_obj("hit")
    first = opening_module._get_cached_world_draw_data(obj)
    second = opening_module._get_cached_world_draw_data(obj)

    assert first is second


def test_world_data_cache_invalidates_on_object_epoch_bump():
    # depsgraph_update_post bumps per-object epochs (one per Object whose
    # transform or geometry changed). After bumping this object's epoch the
    # next lookup must miss and recompute.
    obj = _make_triangulated_quad_obj("bumped")
    first = opening_module._get_cached_world_draw_data(obj)
    opening_module._object_epochs[obj.session_uid] = opening_module._object_epochs.get(obj.session_uid, 0) + 1
    second = opening_module._get_cached_world_draw_data(obj)

    assert first is not second


def test_world_data_cache_partitions_entries_by_object_identity():
    a = _make_triangulated_quad_obj("a")
    b = _make_triangulated_quad_obj("b")

    a_first = opening_module._get_cached_world_draw_data(a)
    b_first = opening_module._get_cached_world_draw_data(b)
    a_second = opening_module._get_cached_world_draw_data(a)

    assert a_first is a_second
    assert a_first is not b_first


def test_world_data_cache_reflects_new_matrix_after_epoch_bump():
    # The cache stores world-space verts. A transform without an epoch bump
    # would serve stale coordinates — but transform updates bump the object's
    # epoch via the depsgraph handler, so after bump + recompute the new
    # matrix must be reflected.
    obj = _make_triangulated_quad_obj("moved")
    before = opening_module._get_cached_world_draw_data(obj)
    obj.matrix_world = obj.matrix_world @ Matrix.Translation((5.0, 0.0, 0.0))
    opening_module._object_epochs[obj.session_uid] = opening_module._object_epochs.get(obj.session_uid, 0) + 1
    after = opening_module._get_cached_world_draw_data(obj)

    # Each vert in `after` is 5 units shifted on X relative to `before`.
    for a_co, b_co in zip(after[1], before[1]):
        assert a_co[0] - b_co[0] == pytest.approx(5.0)
        assert a_co[1] == pytest.approx(b_co[1])
        assert a_co[2] == pytest.approx(b_co[2])


def test_world_data_cache_ios_edges_path_returns_curated_edges():
    # When the mesh has an ios_edges attribute, line_verts must equal the full
    # verts (no dissolve), and edges_indices must include only entries where
    # the attribute is True.
    obj = _make_triangulated_quad_obj("curated")
    attr = obj.data.attributes.new(name="ios_edges", type="BOOLEAN", domain="EDGE")
    # 5 edges total (quad + diagonal). Mark only the 4 quad sides as real.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    real_edges_count = 0
    for i, edge in enumerate(bm.edges):
        is_diagonal = (
            abs(edge.verts[0].co[0] - edge.verts[1].co[0]) > 0 and abs(edge.verts[0].co[1] - edge.verts[1].co[1]) > 0
        )
        attr.data[i].value = not is_diagonal
        if not is_diagonal:
            real_edges_count += 1
    bm.free()
    obj.data.update()

    line_verts, verts, edges_indices, _ = opening_module._get_cached_world_draw_data(obj)

    assert line_verts is verts, "ios_edges path must reuse the full-verts list as line_verts"
    assert len(edges_indices) == real_edges_count


def test_world_data_cache_dissolve_path_drops_diagonal():
    # Without ios_edges, the cache falls through to dissolve. The 5th edge
    # (diagonal) must be gone from edges_indices.
    obj = _make_triangulated_quad_obj("dissolved")
    line_verts, verts, edges_indices, _ = opening_module._get_cached_world_draw_data(obj)

    assert len(edges_indices) == 4
    assert len(line_verts) == 4
    assert len(verts) == 4


# --- batch cache (_get_cached_batch_or_none / _store_batch_in_cache) ---------


def test_batch_cache_returns_none_on_cold_lookup():
    assert opening_module._get_cached_batch_or_none((123, "lines")) is None


def test_batch_cache_returns_stored_batch_on_hit():
    # Sentinel stands in for a GPUBatch — the cache treats it opaquely, so
    # this test pins lookup/store correctness without needing a real shader.
    sentinel = object()
    opening_module._store_batch_in_cache((42, "lines"), sentinel)

    assert opening_module._get_cached_batch_or_none((42, "lines")) is sentinel


def test_batch_cache_invalidates_on_object_epoch_bump():
    sentinel = object()
    opening_module._store_batch_in_cache((42, "lines"), sentinel)
    opening_module._object_epochs[42] = opening_module._object_epochs.get(42, 0) + 1

    assert opening_module._get_cached_batch_or_none((42, "lines")) is None


def test_batch_cache_partitions_entries_by_kind():
    # Same object, different batch kinds (LINES vs TRIS vs arrow) coexist —
    # required so the same opening's three batches don't evict each other.
    lines_batch = object()
    tris_batch = object()
    opening_module._store_batch_in_cache((42, "lines"), lines_batch)
    opening_module._store_batch_in_cache((42, "tris"), tris_batch)

    assert opening_module._get_cached_batch_or_none((42, "lines")) is lines_batch
    assert opening_module._get_cached_batch_or_none((42, "tris")) is tris_batch


def test_batch_cache_partitions_entries_by_object_uid():
    a_batch = object()
    b_batch = object()
    opening_module._store_batch_in_cache((1, "lines"), a_batch)
    opening_module._store_batch_in_cache((2, "lines"), b_batch)

    assert opening_module._get_cached_batch_or_none((1, "lines")) is a_batch
    assert opening_module._get_cached_batch_or_none((2, "lines")) is b_batch


# --- per-object epoch invalidation (granularity contract) --------------------


def test_world_data_cache_per_object_epoch_invalidates_only_target():
    # Core contract for the granular-invalidation feature: bumping one object's
    # epoch must not evict another object's cached payload. This is what makes
    # dragging a single object in a 50-opening scene affordable.
    a = _make_triangulated_quad_obj("granular_a")
    b = _make_triangulated_quad_obj("granular_b")

    a_first = opening_module._get_cached_world_draw_data(a)
    b_first = opening_module._get_cached_world_draw_data(b)

    opening_module._object_epochs[a.session_uid] = opening_module._object_epochs.get(a.session_uid, 0) + 1

    a_second = opening_module._get_cached_world_draw_data(a)
    b_second = opening_module._get_cached_world_draw_data(b)

    assert a_first is not a_second, "a's epoch bump must invalidate a's entry"
    assert b_first is b_second, "a's epoch bump must NOT touch b's entry"


def test_batch_cache_per_object_epoch_invalidates_only_target():
    a_lines = object()
    b_lines = object()
    opening_module._store_batch_in_cache((1, "lines"), a_lines)
    opening_module._store_batch_in_cache((2, "lines"), b_lines)

    opening_module._object_epochs[1] = opening_module._object_epochs.get(1, 0) + 1

    assert opening_module._get_cached_batch_or_none((1, "lines")) is None
    assert opening_module._get_cached_batch_or_none((2, "lines")) is b_lines


def test_global_clear_handler_wipes_everything():
    # undo/redo/load can't be modeled as per-object deltas — the global handler
    # must wipe every layer (epochs + both caches) so we can never serve state
    # that pre-dates the undo/load.
    a = _make_triangulated_quad_obj("wipe_a")
    opening_module._get_cached_world_draw_data(a)
    opening_module._store_batch_in_cache((a.session_uid, "lines"), object())
    assert a.session_uid in opening_module._world_draw_data_cache
    assert (a.session_uid, "lines") in opening_module._batch_cache

    opening_module._clear_decoration_caches_globally()

    assert opening_module._world_draw_data_cache == {}
    assert opening_module._batch_cache == {}
    assert opening_module._object_epochs == {}


class _FakeDepsgraphUpdate:
    def __init__(self, id_, transform: bool = False, geometry: bool = False):
        self.id = id_
        self.is_updated_transform = transform
        self.is_updated_geometry = geometry


class _FakeDepsgraph:
    def __init__(self, updates):
        self.updates = updates


def test_depsgraph_handler_bumps_epoch_for_updated_object():
    # Synthesised depsgraph delta: one Object with a transform update. The
    # handler must increment that object's epoch.
    obj = _make_triangulated_quad_obj("bumped_via_handler")
    before = opening_module._object_epochs.get(obj.session_uid, 0)

    deps = _FakeDepsgraph([_FakeDepsgraphUpdate(obj, transform=True)])
    opening_module._bump_object_epochs_for_decoration(None, deps)

    assert opening_module._object_epochs[obj.session_uid] == before + 1


def test_depsgraph_handler_ignores_non_object_updates():
    # Updates whose .id isn't a bpy.types.Object (Mesh, Material, NodeTree…)
    # must not affect any object's epoch.
    obj = _make_triangulated_quad_obj("untouched")
    deps = _FakeDepsgraph([_FakeDepsgraphUpdate(obj.data, geometry=True)])
    opening_module._bump_object_epochs_for_decoration(None, deps)

    assert obj.session_uid not in opening_module._object_epochs


def test_depsgraph_handler_ignores_updates_without_transform_or_geometry():
    # An Object update flagged only for shading must not bump the epoch —
    # shading changes don't move the wire overlay.
    obj = _make_triangulated_quad_obj("shading_only")
    deps = _FakeDepsgraph([_FakeDepsgraphUpdate(obj)])
    opening_module._bump_object_epochs_for_decoration(None, deps)

    assert obj.session_uid not in opening_module._object_epochs


def test_depsgraph_handler_resolves_cow_original():
    # For non-evaluated Blender objects, obj.original returns obj itself, so
    # the .original-resolution path keys the SAME uid the draw handler reads.
    # Pinning this prevents a future refactor that drops the .original lookup
    # from silently regressing the COW-boundary case (the decorator failing to
    # follow a moved object).
    obj = _make_triangulated_quad_obj("cow")
    deps = _FakeDepsgraph([_FakeDepsgraphUpdate(obj, transform=True)])
    opening_module._bump_object_epochs_for_decoration(None, deps)

    assert obj.original.session_uid in opening_module._object_epochs


def test_depsgraph_handler_tolerates_missing_depsgraph():
    # Some Blender event paths may call the handler without a depsgraph; the
    # handler must short-circuit instead of raising AttributeError.
    opening_module._bump_object_epochs_for_decoration()
    opening_module._bump_object_epochs_for_decoration(None)
    opening_module._bump_object_epochs_for_decoration(None, None)

    assert opening_module._object_epochs == {}
