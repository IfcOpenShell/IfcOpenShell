# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

"""Pins the ``include_linked_ifc`` toggle contract.

The toggle extends the cap pipeline to also bisect meshes living inside
Project ▸ Links collection-instance empties — without it those meshes
are clipped by Blender's native viewport clip but never get
cross-section caps drawn at the cut.
"""

import bpy
import pytest
from mathutils import Matrix

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.clip_box


def _make_synthetic_linked_collection(
    inner_location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    instance_location: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> tuple[bpy.types.Object, bpy.types.Object, bpy.types.Collection]:
    """Build a synthetic link: a collection with one mesh + an instance empty.

    Mirrors the structural shape of a real loaded link without driving
    the multi-process .ifc.cache.blend pipeline. Returns
    ``(instance_empty, inner_mesh, collection)`` so tests can assert
    against the exact objects they created.
    """
    collection = bpy.data.collections.new("LinkedIFC")
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=inner_location)
    inner = bpy.context.active_object
    for c in list(inner.users_collection):
        c.objects.unlink(inner)
    collection.objects.link(inner)

    empty = bpy.data.objects.new("LinkedIFC.001", None)
    empty.instance_type = "COLLECTION"
    empty.instance_collection = collection
    bpy.context.scene.collection.objects.link(empty)
    # matrix_world (not .location) so the test reads a fresh value without
    # needing a depsgraph tick to propagate matrix_local → matrix_world.
    empty.matrix_world = Matrix.Translation(instance_location)

    return empty, inner, collection


def _register_synthetic_link(empty: bpy.types.Object) -> None:
    """Add a Project ▸ Links entry pointing at ``empty``.

    No IFC is set in the bootstrap fixture, so
    ``tool.Project.get_link_empty_handle`` resolves via the link's
    ``empty_handle`` PointerProperty rather than the IfcStore.
    """
    project_props = tool.Project.get_project_props()
    link = project_props.links.add()
    link.name = "synthetic"
    link.is_loaded = True
    link.empty_handle = empty


class TestDefaultIsOff(NewFile):
    def test_include_linked_ifc_defaults_to_false(self):
        scene_props = tool.ClipBox.get_scene_props()
        assert scene_props.include_linked_ifc is False


class TestIteratorGating(NewFile):
    def test_iterator_returns_nothing_when_toggle_off(self):
        empty, _inner, _col = _make_synthetic_linked_collection()
        _register_synthetic_link(empty)
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.include_linked_ifc = False

        yielded = list(tool.ClipBox._iter_linked_ifc_capable_meshes(bpy.context.scene))

        assert yielded == []

    def test_iterator_yields_inner_mesh_when_toggle_on(self):
        empty, inner, _col = _make_synthetic_linked_collection()
        _register_synthetic_link(empty)
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.include_linked_ifc = True

        yielded = list(tool.ClipBox._iter_linked_ifc_capable_meshes(bpy.context.scene))

        assert len(yielded) == 1
        instance, mesh_obj, _world_matrix = yielded[0]
        assert instance is empty
        assert mesh_obj is inner

    def test_iterator_composes_instance_and_inner_matrix(self):
        # The inner mesh's matrix_world is library-local (cube at origin
        # inside the collection). The instance empty is offset by 5m on X.
        # The effective world matrix must combine the two so the cap lands
        # in the active scene, not at the inner mesh's library origin.
        empty, inner, _col = _make_synthetic_linked_collection(
            inner_location=(0.0, 0.0, 0.0),
            instance_location=(5.0, 0.0, 0.0),
        )
        _register_synthetic_link(empty)
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.include_linked_ifc = True

        _instance, _mesh_obj, world_matrix = next(iter(tool.ClipBox._iter_linked_ifc_capable_meshes(bpy.context.scene)))

        expected = empty.matrix_world @ inner.matrix_world
        assert (world_matrix.translation - expected.translation).length < 1e-6
        # And the composition picks up the empty's offset.
        assert world_matrix.translation.x == pytest.approx(5.0)

    def test_iterator_skips_links_with_no_instance_collection(self):
        # A link whose empty_handle was created but never linked to a
        # collection (e.g. half-initialised link) must not yield anything.
        empty = bpy.data.objects.new("LinkedIFC.broken", None)
        empty.instance_type = "COLLECTION"
        bpy.context.scene.collection.objects.link(empty)
        _register_synthetic_link(empty)
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.include_linked_ifc = True

        yielded = list(tool.ClipBox._iter_linked_ifc_capable_meshes(bpy.context.scene))

        assert yielded == []

    def test_iterator_skips_unloaded_links(self):
        empty, _inner, _col = _make_synthetic_linked_collection()
        project_props = tool.Project.get_project_props()
        link = project_props.links.add()
        link.name = "unloaded"
        link.is_loaded = False
        link.empty_handle = empty
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.include_linked_ifc = True

        yielded = list(tool.ClipBox._iter_linked_ifc_capable_meshes(bpy.context.scene))

        assert yielded == []


class TestUpdateCallbackInvalidatesCache(NewFile):
    def test_toggling_include_linked_ifc_clears_cap_cache(self):
        # Seed the cache with a sentinel so we can detect invalidation.
        tool.ClipBox._cap_cache["sentinel"] = (object(), None)
        scene_props = tool.ClipBox.get_scene_props()

        scene_props.include_linked_ifc = True

        assert "sentinel" not in tool.ClipBox._cap_cache
        tool.ClipBox._cancel_pending_cap_rebuild()


class TestRebuildCachesLinkedMesh(NewFile):
    def test_rebuild_adds_link_prefixed_entry_when_toggle_on(self):
        # The default clip box spawns a 20m cube around the cursor, so a
        # 2m cube at the origin sits fully inside both the box and the
        # instance's translation — guaranteeing the AABB-vs-planes check
        # passes and a (cache_key, batch) entry lands in _cap_cache.
        empty, _inner, _col = _make_synthetic_linked_collection()
        _register_synthetic_link(empty)
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.include_linked_ifc = True

        tool.ClipBox.rebuild_caps_now()

        link_keys = [name for name in tool.ClipBox._cap_cache if name.startswith("link:")]
        assert link_keys, f"expected a link: cache entry, got {list(tool.ClipBox._cap_cache)}"

    def test_rebuild_drops_link_entry_when_toggle_off(self):
        empty, _inner, _col = _make_synthetic_linked_collection()
        _register_synthetic_link(empty)
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.include_linked_ifc = True
        tool.ClipBox.rebuild_caps_now()
        assert any(name.startswith("link:") for name in tool.ClipBox._cap_cache)

        scene_props.include_linked_ifc = False
        tool.ClipBox.rebuild_caps_now()

        assert not any(name.startswith("link:") for name in tool.ClipBox._cap_cache)
