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

import math
from unittest.mock import patch

import bpy
import pytest
from mathutils import Matrix, Vector

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.clip_box


class TestAddClipBox(NewFile):
    def test_creates_empty_and_registers_entry(self):
        result = bpy.ops.bim.add_clip_box()
        assert result == {"FINISHED"}
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 1
        host = scene_props.clip_boxes[0].obj
        assert host is not None
        assert host.empty_display_type == "CUBE"
        obj_props = tool.ClipBox.get_object_props(host)
        assert obj_props.is_clip_box is True

    def test_spawns_at_3d_cursor(self):
        bpy.context.scene.cursor.location = (4.0, 0.0, 2.0)
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        assert host is not None
        assert host.matrix_world.translation.x == pytest.approx(4.0)
        assert host.matrix_world.translation.z == pytest.approx(2.0)

    def test_spawns_in_clip_boxes_collection(self):
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        collection_names = [c.name for c in host.users_collection]
        assert "BBIM_ClipBoxes" in collection_names


class TestActiveClipBoxResolution(NewFile):
    def test_no_box_returns_none(self):
        assert tool.ClipBox.get_active_clip_box() is None

    def test_active_index_out_of_range_returns_none(self):
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.active_clip_box_index = 99
        assert tool.ClipBox.get_active_clip_box() is None


class TestComputePlanes(NewFile):
    def test_planes_match_unit_box_at_origin(self):
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host.matrix_world = Matrix.Identity(4)

        planes = tool.ClipBox.compute_planes(host)
        assert tool.Cad.point_is_inside_clip_planes(planes, Vector((0, 0, 0)))
        assert not tool.Cad.point_is_inside_clip_planes(planes, Vector((2, 0, 0)))
        assert not tool.Cad.point_is_inside_clip_planes(planes, Vector((0, 0, -2)))

    def test_scaled_host_grows_clip_region(self):
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host.matrix_world = Matrix.Diagonal((3.0, 1.0, 1.0, 1.0))

        # Test points well clear of any reasonable expand margin so the
        # assertion pins the OBB scaling behaviour, not the margin value.
        planes = tool.ClipBox.compute_planes(host)
        assert tool.Cad.point_is_inside_clip_planes(planes, Vector((2.5, 0, 0)))
        assert not tool.Cad.point_is_inside_clip_planes(planes, Vector((4.0, 0, 0)))

    def test_rotated_host_rotates_clip_region(self):
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host.matrix_world = Matrix.Rotation(math.radians(45), 4, "Z")

        # Test points well clear of the expand margin so the assertion
        # pins rotation, not the margin value.
        planes = tool.ClipBox.compute_planes(host)
        assert tool.Cad.point_is_inside_clip_planes(planes, Vector((0.5, 0, 0)))
        assert not tool.Cad.point_is_inside_clip_planes(planes, Vector((2.0, 0, 0)))

    def test_translated_and_rotated_host_keeps_centre_inside(self):
        bpy.context.scene.cursor.location = (5.0, 7.0, 0.0)
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host.matrix_world = Matrix.Translation((5.0, 7.0, 0.0)) @ Matrix.Rotation(math.radians(30), 4, "Z")

        planes = tool.ClipBox.compute_planes(host)
        assert tool.Cad.point_is_inside_clip_planes(planes, Vector((5, 7, 0)))

    def test_margin_grows_with_scale(self):
        # The empty's CUBE display lives at local +-1; the GPU dot
        # product that tests each wireframe vertex against the clip
        # planes has float error that scales with the axis's world
        # half-extent. A fixed absolute margin gets eaten by that drift
        # once the box is spawned at non-trivial scale, so the half-
        # extent the planes encode must include a relative term — the
        # margin between the wireframe edge and the plane must grow
        # with the scale.
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()

        host.matrix_world = Matrix.Identity(4)
        planes_unit = tool.ClipBox.compute_planes(host)
        # +X plane: normal (-1, 0, 0), d = half_x. Read half from d.
        half_unit = planes_unit[0][3]
        margin_unit = half_unit - 1.0

        host.matrix_world = Matrix.Diagonal((100.0, 100.0, 100.0, 1.0))
        planes_scaled = tool.ClipBox.compute_planes(host)
        half_scaled = planes_scaled[0][3]
        margin_scaled = half_scaled - 100.0

        assert margin_scaled > margin_unit * 10, (
            f"margin must scale with extent: unit={margin_unit:g}, " f"scale-100={margin_scaled:g}"
        )


class TestToggleEnabled(NewFile):
    def test_flips_scene_enabled_flag(self):
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        original = scene_props.enabled
        bpy.ops.bim.toggle_clip_box_enabled()
        assert scene_props.enabled is (not original)


class TestSetActiveClipBox(NewFile):
    def test_switches_active_index(self):
        bpy.ops.bim.add_clip_box()
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        assert scene_props.active_clip_box_index == 1
        bpy.ops.bim.set_active_clip_box(index=0)
        assert scene_props.active_clip_box_index == 0

    def test_invalid_index_cancels(self):
        bpy.ops.bim.add_clip_box()
        result = bpy.ops.bim.set_active_clip_box(index=99)
        assert result == {"CANCELLED"}


class TestRemoveClipBox(NewFile):
    def test_drops_active_entry_when_no_index(self):
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host_name = host.name
        bpy.ops.bim.remove_clip_box(delete_object=True)
        assert host_name not in bpy.data.objects
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 0

    def test_drops_specified_index(self):
        # Per-row UIList button passes index explicitly; the user can
        # click X on any row without first selecting it as active.
        bpy.ops.bim.add_clip_box()
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        first_name = scene_props.clip_boxes[0].obj.name
        bpy.ops.bim.remove_clip_box(index=0)
        assert first_name not in bpy.data.objects
        assert len(scene_props.clip_boxes) == 1

    def test_no_active_box_cancels(self):
        result = bpy.ops.bim.remove_clip_box()
        assert result == {"CANCELLED"}

    def test_out_of_range_index_cancels(self):
        bpy.ops.bim.add_clip_box()
        result = bpy.ops.bim.remove_clip_box(index=99)
        assert result == {"CANCELLED"}


class TestPsetPersistence(NewFile):
    def test_add_clip_box_writes_project_pset(self):
        import ifcopenshell.util.element

        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()
        project = tool.Ifc.get().by_type("IfcProject")[0]
        psets = ifcopenshell.util.element.get_psets(project)
        assert tool.ClipBox.PSET_NAME in psets
        assert psets[tool.ClipBox.PSET_NAME]["Count"] == 1

    def test_round_trip_via_pset_restores_matrix(self):
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host.matrix_world = Matrix.Translation((5.0, 7.0, 3.0)) @ Matrix.Diagonal((2.0, 1.5, 0.5, 1.0))
        tool.ClipBox.save_to_project_pset()

        # Simulate a fresh-load state: clear scene list AND delete the
        # Blender empty so load has to recreate it.
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.clip_boxes.clear()
        bpy.data.objects.remove(host, do_unlink=True)

        tool.ClipBox.load_from_project_pset()
        assert len(scene_props.clip_boxes) == 1
        rehydrated = scene_props.clip_boxes[0].obj
        assert rehydrated is not None
        for r in range(4):
            for c in range(4):
                expected = (Matrix.Translation((5.0, 7.0, 3.0)) @ Matrix.Diagonal((2.0, 1.5, 0.5, 1.0)))[r][c]
                assert rehydrated.matrix_world[r][c] == pytest.approx(expected, abs=1e-6)

    def test_load_from_pset_is_idempotent(self):
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()
        tool.ClipBox.load_from_project_pset()
        tool.ClipBox.load_from_project_pset()
        assert len(tool.ClipBox.get_scene_props().clip_boxes) == 1

    def test_load_from_pset_does_not_touch_enabled(self):
        # ``enabled`` is intentionally not persisted to the pset — the
        # default is False (fresh .blend) and Blender's own .blend
        # session save carries the user's saved value through reload.
        # ``load_from_project_pset`` must not stomp either.
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.enabled = True
        tool.ClipBox.save_to_project_pset()

        # Simulate the depsgraph IFC-reload branch: load runs without
        # touching enabled; the prior True value must survive.
        tool.ClipBox.load_from_project_pset()
        assert scene_props.enabled is True

        # And the opposite: load when False must not flip it True.
        scene_props.enabled = False
        tool.ClipBox.load_from_project_pset()
        assert scene_props.enabled is False

    def test_add_clip_box_creates_no_ifc_entity(self):
        # The clip box is project-pset persisted; there must be no
        # IfcRoot entity attached to the empty (which would lock its
        # scale and strip it on export).
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        assert tool.Ifc.get_entity(host) is None

    def test_show_caps_round_trips_via_pset(self):
        # show_caps is a scene-level toggle persisted in the project pset.
        # Per-mesh cap cost dominates the bisect, which doesn't scale with
        # clip-box extent, so the toggle applies file-wide.
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.show_caps = False
        tool.ClipBox.save_to_project_pset()

        scene_props.clip_boxes.clear()
        scene_props.show_caps = True  # default; load_from_project_pset must flip back to False
        bpy.data.objects.remove(host, do_unlink=True)

        tool.ClipBox.load_from_project_pset()
        assert scene_props.show_caps is False


class TestCapGeneration(NewFile):
    def test_cap_for_box_straddling_clip_plane_produces_triangles(self):
        # A 2x2x2 cube centred at the origin, clipped by a unit-radius clip
        # box also at the origin: the four faces of the cube that pierce
        # the +/- x box faces should yield cap polygons on the two faces.
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host.matrix_world = Matrix.Identity(4)  # unit box at origin

        bpy.ops.mesh.primitive_cube_add(size=4.0, location=(0.0, 0.0, 0.0))
        cube = bpy.context.active_object

        world_planes = tool.Cad.obb_clip_planes_from_matrix(host.matrix_world)
        verts = tool.ClipBox._compute_caps_for_object(cube, world_planes)

        # Every cap is at least one triangle (3 verts each), and we expect
        # 6 cap polygons (one per box face) → at minimum 18 verts.
        assert len(verts) >= 18
        assert len(verts) % 3 == 0

    def test_cap_for_mesh_entirely_outside_box_produces_nothing(self):
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host.matrix_world = Matrix.Identity(4)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(10.0, 0.0, 0.0))
        cube = bpy.context.active_object

        world_planes = tool.Cad.obb_clip_planes_from_matrix(host.matrix_world)
        verts = tool.ClipBox._compute_caps_for_object(cube, world_planes)
        assert verts == []

    def test_cap_for_mesh_entirely_inside_box_produces_nothing(self):
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host.matrix_world = Matrix.Identity(4)

        bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0.0, 0.0, 0.0))
        cube = bpy.context.active_object

        world_planes = tool.Cad.obb_clip_planes_from_matrix(host.matrix_world)
        verts = tool.ClipBox._compute_caps_for_object(cube, world_planes)
        assert verts == []

    def test_non_watertight_mesh_does_not_crash(self):
        # The cap pipeline assumes watertight input; non-watertight
        # meshes (terrain, single-shell surfaces) may produce degenerate
        # caps but must not raise. The user is responsible for input
        # quality.
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        host.matrix_world = Matrix.Identity(4)

        bpy.ops.mesh.primitive_grid_add(size=4.0, location=(0.0, 0.0, 0.0))
        grid = bpy.context.active_object

        world_planes = tool.Cad.obb_clip_planes_from_matrix(host.matrix_world)
        verts = tool.ClipBox._compute_caps_for_object(grid, world_planes)
        assert isinstance(verts, list)

    def test_show_caps_defaults_on_and_toggles(self):
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        assert scene_props.show_caps is True
        scene_props.show_caps = False
        assert scene_props.show_caps is False


class TestCapEligibility(NewFile):
    def test_ifc_space_is_not_capped(self):
        # IfcSpace is an IfcProduct (spatial structure) but should never
        # cap — spaces are non-physical containers; capping them sprouts
        # solid fills where the room boundary crosses the clip plane.
        tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()

        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        space_obj = bpy.context.active_object
        tool.Root.get_root_props().ifc_product = "IfcSpatialElement"
        bpy.ops.bim.assign_class(ifc_class="IfcSpace")

        capable = list(tool.ClipBox._iter_capable_objects(bpy.context.scene))
        assert space_obj not in capable

    def test_ifc_wall_is_capped(self):
        tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()

        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        wall_obj = bpy.context.active_object
        tool.Root.get_root_props().ifc_product = "IfcElement"
        bpy.ops.bim.assign_class(ifc_class="IfcWall")

        capable = list(tool.ClipBox._iter_capable_objects(bpy.context.scene))
        assert wall_obj in capable

    def test_pure_blender_mesh_is_not_capped(self):
        tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()

        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        cube = bpy.context.active_object
        # No assign_class — pure Blender mesh, no IFC entity attached.
        capable = list(tool.ClipBox._iter_capable_objects(bpy.context.scene))
        assert cube not in capable


class TestDuplicateClipBox(NewFile):
    def test_duplicates_active_when_no_index(self):
        bpy.ops.bim.add_clip_box()
        source = tool.ClipBox.get_active_clip_box()
        source.matrix_world = Matrix.Translation((3.0, 4.0, 5.0)) @ Matrix.Diagonal((2.0, 1.0, 1.0, 1.0))

        bpy.ops.bim.duplicate_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 2
        copy = tool.ClipBox.get_active_clip_box()
        assert copy is not source
        for r in range(4):
            for c in range(4):
                assert copy.matrix_world[r][c] == pytest.approx(source.matrix_world[r][c])
        assert tool.ClipBox.get_object_props(copy).is_clip_box is True

    def test_duplicates_specified_index(self):
        bpy.ops.bim.add_clip_box()
        first = tool.ClipBox.get_active_clip_box()
        bpy.ops.bim.add_clip_box()
        # Active is now index 1; duplicate index 0 explicitly.
        bpy.ops.bim.duplicate_clip_box(index=0)
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 3
        copy = tool.ClipBox.get_active_clip_box()
        for r in range(4):
            for c in range(4):
                assert copy.matrix_world[r][c] == pytest.approx(first.matrix_world[r][c])

    def test_no_active_box_cancels(self):
        result = bpy.ops.bim.duplicate_clip_box()
        assert result == {"CANCELLED"}

    def test_out_of_range_index_cancels(self):
        bpy.ops.bim.add_clip_box()
        result = bpy.ops.bim.duplicate_clip_box(index=99)
        assert result == {"CANCELLED"}

    def test_duplicate_arms_clipping(self):
        bpy.ops.bim.add_clip_box()  # arms
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.enabled = False  # user disables
        bpy.ops.bim.duplicate_clip_box()  # re-arms
        assert scene_props.enabled is True


class TestCollectionSync(NewFile):
    def test_sync_adopts_orphan_clip_box_empty(self):
        # Simulates Bonsai's Shift+D duplicate: an empty with is_clip_box=True
        # exists in the BBIM_ClipBoxes collection but no scene-list entry
        # points at it. The sync must adopt it as a first-class clip box.
        bpy.ops.bim.add_clip_box()
        source = tool.ClipBox.get_active_clip_box()

        orphan = bpy.data.objects.new(source.name, None)
        orphan.empty_display_type = "CUBE"
        orphan.empty_display_size = 1.0
        orphan.matrix_world = source.matrix_world.copy()
        tool.ClipBox.get_object_props(orphan).is_clip_box = True
        collection = bpy.data.collections.get("BBIM_ClipBoxes")
        collection.objects.link(orphan)

        tool.ClipBox._sync_collection_to_list(bpy.context.scene)
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 2
        assert scene_props.clip_boxes[-1].obj is orphan
        assert scene_props.active_clip_box_index == 1

    def test_sync_skips_unflagged_empties(self):
        bpy.ops.bim.add_clip_box()
        collection = bpy.data.collections.get("BBIM_ClipBoxes")
        decoy = bpy.data.objects.new("Decoy", None)
        collection.objects.link(decoy)

        tool.ClipBox._sync_collection_to_list(bpy.context.scene)
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 1


class TestEnabledIsSceneLevel(NewFile):
    def test_default_is_false(self):
        scene_props = tool.ClipBox.get_scene_props()
        assert scene_props.enabled is False

    def test_add_arms_clipping(self):
        # Adding any clip box flips enabled True so the user
        # immediately sees the cut and discovers the panel toggle
        # by association.
        scene_props = tool.ClipBox.get_scene_props()
        assert scene_props.enabled is False
        bpy.ops.bim.add_clip_box()
        assert scene_props.enabled is True

    def test_subsequent_adds_re_arm_after_user_disables(self):
        bpy.ops.bim.add_clip_box()  # arms
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.enabled = False  # user disables
        bpy.ops.bim.add_clip_box()  # second add re-arms
        assert scene_props.enabled is True

    def test_selecting_clip_box_does_not_arm(self):
        # Per design, selecting a clip box empty must NOT toggle the
        # scene-level enabled — activation is panel-only. Otherwise a
        # casual click in the outliner would silently hide geometry
        # with no obvious unarm path for a user who hasn't found the
        # panel yet.
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.enabled = False  # disable after first-add auto-arm

        host = tool.ClipBox.get_active_clip_box()
        bpy.context.view_layer.objects.active = host
        tool.ClipBox.on_depsgraph_update(bpy.context.scene, None)
        assert scene_props.enabled is False

    def test_toggle_operator_flips_scene_enabled(self):
        bpy.ops.bim.add_clip_box()  # first-add arms it
        scene_props = tool.ClipBox.get_scene_props()
        assert scene_props.enabled is True
        bpy.ops.bim.toggle_clip_box_enabled()
        assert scene_props.enabled is False
        bpy.ops.bim.toggle_clip_box_enabled()
        assert scene_props.enabled is True


class TestSpawnScale(NewFile):
    def test_default_scale_is_ten(self):
        # Default spawn scale is 10 (=20m cube) to cover a typical
        # storey, not the meaningless 1m unit cube.
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        assert tuple(host.scale) == pytest.approx((10.0, 10.0, 10.0))


class TestCapRebuildDebounce(NewFile):
    """The depsgraph handler debounces cap rebuilds so a burst of
    updates (e.g. an external-addon gizmo drag) collapses to one
    rebuild ~250 ms after the storm subsides. Bonsai's own transform
    modals get a fast path: an immediate rebuild on the True→False
    transition of ``is_transform_modal_active``.
    """

    def setup_method(self):
        bpy.ops.bim.add_clip_box()
        tool.ClipBox._cancel_pending_cap_rebuild()
        tool.ClipBox._last_modal_state = False
        tool.ClipBox._last_seen_object_matrices.clear()

    def teardown_method(self):
        tool.ClipBox._cancel_pending_cap_rebuild()
        tool.ClipBox._last_modal_state = False
        tool.ClipBox._last_seen_object_matrices.clear()

    def test_modal_end_triggers_immediate_rebuild(self):
        # Prime "previous tick had a modal active" then run a tick with
        # no modal → fast path fires rebuild_cap_cache synchronously,
        # bypassing the timer. Targets _handle_cap_tick directly to
        # bypass the screen guard that aborts in headless test runs.
        tool.ClipBox._last_modal_state = True
        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
            patch.object(tool.ClipBox, "rebuild_cap_cache") as mock_rebuild,
            patch.object(tool.ClipBox, "_schedule_cap_rebuild") as mock_schedule,
        ):
            tool.ClipBox._handle_cap_tick(bpy.context.scene, None)
        mock_rebuild.assert_called_once()
        mock_schedule.assert_not_called()

    def test_burst_collapses_to_one_pending_timer(self):
        # 5 ticks with no modal active → schedule called 5 times; each
        # call cancels the previous pending timer and registers a fresh
        # one, so exactly one timer is pending at the end.
        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
            patch.object(tool.ClipBox, "rebuild_cap_cache"),
        ):
            for _ in range(5):
                tool.ClipBox._handle_cap_tick(bpy.context.scene, None)
        pending = tool.ClipBox._pending_cap_rebuild
        assert pending is not None
        assert bpy.app.timers.is_registered(pending)
        tool.ClipBox._cancel_pending_cap_rebuild()

    def test_pending_rebuild_hides_caps(self):
        # While a debounce is in flight, on_post_view_caps must not
        # draw — the cached batches reflect an earlier frame and would
        # look stale against the geometry being mutated.
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.enabled = True
        scene_props.show_caps = True

        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
            patch.object(tool.ClipBox, "rebuild_cap_cache"),
        ):
            tool.ClipBox._handle_cap_tick(bpy.context.scene, None)
        assert tool.ClipBox._pending_cap_rebuild is not None

        # Populate cap_cache to non-empty so the first-line gate
        # "if not cls._cap_cache: return" doesn't fire — the contract
        # we're pinning is the pending-rebuild gate specifically.
        tool.ClipBox._cap_cache["sentinel"] = ((), None)
        try:
            # If pending-rebuild gate works, on_post_view_caps exits
            # before importing gpu / building a shader. Patch
            # gpu.shader.from_builtin to fail loudly if drawing happens.
            with (
                patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
                patch("gpu.shader.from_builtin", side_effect=AssertionError("should be hidden")),
            ):
                tool.ClipBox.on_post_view_caps()
        finally:
            tool.ClipBox._cap_cache.pop("sentinel", None)
            tool.ClipBox._cancel_pending_cap_rebuild()

    def test_cancel_pending_drops_timer(self):
        with patch.object(tool.Blender, "is_transform_modal_active", return_value=False):
            tool.ClipBox._schedule_cap_rebuild()
        pending = tool.ClipBox._pending_cap_rebuild
        assert pending is not None and bpy.app.timers.is_registered(pending)
        tool.ClipBox._cancel_pending_cap_rebuild()
        assert tool.ClipBox._pending_cap_rebuild is None
        assert not bpy.app.timers.is_registered(pending)

    def test_unregister_handler_cancels_pending(self):
        # The module's unregister() must drop any pending rebuild so a
        # timer can't fire against a freed addon. Exercise the helper
        # directly — full addon unregister would tear down too much for
        # a unit test.
        with patch.object(tool.Blender, "is_transform_modal_active", return_value=False):
            tool.ClipBox._schedule_cap_rebuild()
        assert tool.ClipBox._pending_cap_rebuild is not None
        tool.ClipBox._cancel_pending_cap_rebuild()
        assert tool.ClipBox._pending_cap_rebuild is None

    def test_selection_only_tick_does_not_schedule(self):
        # Selecting an Object raises is_updated_transform=True on the
        # Object itself even though no actual matrix delta occurred
        # (Blender quirk). The matrix-hash baseline must filter that
        # out so the cache and hide-while-pending gate don't flash on
        # every click. Also covers the Scene/ViewLayer noise.
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object

        # Prime the baseline so cube's current matrix hash is "seen".
        tool.ClipBox._last_seen_object_matrices[cube.name] = tool.Blender.hash_matrix(cube.matrix_world)

        class _SceneUpdate:
            id = bpy.context.scene
            is_updated_geometry = False
            is_updated_transform = True

        class _CubeSelectionUpdate:
            id = cube
            is_updated_geometry = False
            is_updated_transform = True  # quirk: matrix unchanged

        class _FakeDepsgraph:
            updates = (_SceneUpdate(), _CubeSelectionUpdate())

        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
            patch.object(tool.ClipBox, "_schedule_cap_rebuild") as mock_schedule,
        ):
            tool.ClipBox._handle_cap_tick(bpy.context.scene, _FakeDepsgraph())
        mock_schedule.assert_not_called()
        assert tool.ClipBox._pending_cap_rebuild is None

    def test_real_transform_tick_does_schedule(self):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        # Baseline hash, then mutate the matrix so the filter sees a
        # true delta on the next tick.
        tool.ClipBox._last_seen_object_matrices[cube.name] = tool.Blender.hash_matrix(cube.matrix_world)
        cube.matrix_world = cube.matrix_world @ Matrix.Translation((1.0, 0, 0))

        class _TransformUpdate:
            id = cube
            is_updated_geometry = False
            is_updated_transform = True

        class _FakeDepsgraph:
            updates = (_TransformUpdate(),)

        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
            patch.object(tool.ClipBox, "_schedule_cap_rebuild") as mock_schedule,
        ):
            tool.ClipBox._handle_cap_tick(bpy.context.scene, _FakeDepsgraph())
        mock_schedule.assert_called_once()

    def test_geometry_update_tick_does_schedule(self):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object

        class _GeometryUpdate:
            id = cube
            is_updated_geometry = True
            is_updated_transform = False

        class _FakeDepsgraph:
            updates = (_GeometryUpdate(),)

        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
            patch.object(tool.ClipBox, "_schedule_cap_rebuild") as mock_schedule,
        ):
            tool.ClipBox._handle_cap_tick(bpy.context.scene, _FakeDepsgraph())
        mock_schedule.assert_called_once()

    def test_edit_mode_skips_scheduling(self):
        # In any EDIT_* mode the depsgraph fires per vert/edge nudge;
        # the cap view isn't the focus and would flash off on every
        # tick. The entry-point gate must short-circuit before the
        # debounce scheduler runs.
        with (
            patch.object(tool.Blender, "is_in_edit_mode", return_value=True),
            patch.object(tool.ClipBox, "_handle_cap_tick") as mock_handle,
        ):
            tool.ClipBox.on_depsgraph_update_caps(bpy.context.scene, None)
        mock_handle.assert_not_called()


class TestClipBbReArmTriggers(NewFile):
    """The C-side clip_bb captured by view3d.clip_border for edit-mode
    click-select is view-aligned and tied to the box pose at arm time,
    so it goes stale on either a clip-box transform commit, an external
    matrix mutation, or an IFC reload that rehydrates from pset. The
    depsgraph handler schedules a full re-arm at those events; the
    modal gate suppresses per-tick re-arms during a live drag.
    """

    @pytest.fixture(autouse=True)
    def reset_clipbox_state_after_newfile(self, setup):
        # ``setup`` is NewFile's autouse fixture; declaring it as a parameter
        # forces this fixture to run AFTER it. NewFile.setup calls
        # wm.read_homefile, which fires our load_pre handler and leaves the
        # _file_loading gate True — tests below exercise on_depsgraph_update
        # in the normal (post-load) state, so the gate must be open here.
        tool.ClipBox._file_loading = False
        tool.ClipBox._post_load_paint_pending = False
        tool.ClipBox._persisted_matrices.clear()
        tool.ClipBox._last_seen_ifc_id = 0
        tool.ClipBox._cancel_pending_refresh()

    def teardown_method(self):
        tool.ClipBox._persisted_matrices.clear()
        tool.ClipBox._last_seen_ifc_id = 0
        tool.ClipBox._cancel_pending_refresh()

    def test_matrix_change_outside_modal_re_arms(self):
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        # Seed a stale baseline so prev_matrix != current_matrix.
        stale = tuple(tuple(row) for row in Matrix.Translation((-99.0, 0.0, 0.0)))
        tool.ClipBox._persisted_matrices[host.name] = stale

        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
            patch.object(tool.ClipBox, "schedule_refresh") as mock_refresh,
        ):
            tool.ClipBox.on_depsgraph_update(bpy.context.scene, bpy.context.evaluated_depsgraph_get())
        mock_refresh.assert_called_once()

    def test_matrix_change_during_modal_skips_re_arm(self):
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        stale = tuple(tuple(row) for row in Matrix.Translation((-99.0, 0.0, 0.0)))
        tool.ClipBox._persisted_matrices[host.name] = stale

        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=True),
            patch.object(tool.ClipBox, "schedule_refresh") as mock_refresh,
        ):
            tool.ClipBox.on_depsgraph_update(bpy.context.scene, bpy.context.evaluated_depsgraph_get())
        mock_refresh.assert_not_called()

    def test_first_matrix_sighting_does_not_re_arm(self):
        # No prior persisted-matrix entry: the branch records the
        # baseline and exits without re-arming. The add path already
        # armed once; a per-tick re-arm on first sight would double-arm.
        bpy.ops.bim.add_clip_box()
        host = tool.ClipBox.get_active_clip_box()
        tool.ClipBox._persisted_matrices.pop(host.name, None)

        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
            patch.object(tool.ClipBox, "schedule_refresh") as mock_refresh,
        ):
            tool.ClipBox.on_depsgraph_update(bpy.context.scene, bpy.context.evaluated_depsgraph_get())
        mock_refresh.assert_not_called()

    def test_ifc_reload_re_arms(self):
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_clip_box()
        # Force an ifc-id mismatch so the rehydrate-from-pset branch
        # fires. The .blend carries the prior session's clip_bb forward;
        # the picker is armed for the OLD view until this re-arms.
        tool.ClipBox._last_seen_ifc_id = 0

        with (
            patch.object(tool.Blender, "is_transform_modal_active", return_value=False),
            patch.object(tool.ClipBox, "schedule_refresh") as mock_refresh,
        ):
            tool.ClipBox.on_depsgraph_update(bpy.context.scene, bpy.context.evaluated_depsgraph_get())
        # IFC-load triggers a re-arm. (Reading the show_caps pset entry
        # writes scene_props.show_caps via its update callback, which
        # is a separate pre-existing re-arm path; the test pins the
        # invariant "ifc-load arms at least once".)
        assert mock_refresh.call_count >= 1


class TestRefreshTimerLifecycle(NewFile):
    """The refresh timer must not survive file-load teardown AND must not
    re-fire until the new file's GPU contexts are wired. A timer that
    arms against pre-init regions CTDs Blender inside GPU_matrix_ortho_set.
    The gate spans load_pre → first on_pre_view tick (first paint = GPU
    ready); load_post fires too early and intentionally does not clear it."""

    @pytest.fixture(autouse=True)
    def reset_clipbox_state_after_newfile(self, setup):
        # ``setup`` is NewFile's autouse fixture; declaring it as a parameter
        # forces this fixture to run AFTER it, so the file-load gate that
        # NewFile.setup's wm.read_homefile leaves True is reset here.
        tool.ClipBox._file_loading = False
        tool.ClipBox._post_load_paint_pending = False
        tool.ClipBox._cancel_pending_refresh()
        tool.ClipBox._cancel_pending_cap_rebuild()

    def teardown_method(self):
        tool.ClipBox._file_loading = False
        tool.ClipBox._post_load_paint_pending = False
        tool.ClipBox._cancel_pending_refresh()
        tool.ClipBox._cancel_pending_cap_rebuild()

    def test_load_pre_cancels_pending_refresh(self):
        from bonsai.bim.module.clip_box import _on_load_pre

        tool.ClipBox.schedule_refresh()
        pending = tool.ClipBox._pending_refresh
        assert pending is not None
        assert bpy.app.timers.is_registered(pending)

        _on_load_pre("ignored.blend")

        assert tool.ClipBox._pending_refresh is None
        assert not bpy.app.timers.is_registered(pending)
        assert tool.ClipBox._file_loading is True
        assert tool.ClipBox._post_load_paint_pending is True

    def test_load_pre_cancels_pending_cap_rebuild(self):
        from bonsai.bim.module.clip_box import _on_load_pre

        tool.ClipBox._schedule_cap_rebuild(interval=10.0)
        pending = tool.ClipBox._pending_cap_rebuild
        assert pending is not None
        assert bpy.app.timers.is_registered(pending)

        _on_load_pre("ignored.blend")

        assert tool.ClipBox._pending_cap_rebuild is None
        assert not bpy.app.timers.is_registered(pending)

    def test_schedule_refresh_no_op_while_loading(self):
        tool.ClipBox._file_loading = True
        tool.ClipBox.schedule_refresh()
        assert tool.ClipBox._pending_refresh is None

    def test_load_post_does_not_clear_file_loading_gate(self):
        from bonsai.bim.module.clip_box import _on_load_post

        tool.ClipBox._file_loading = True
        tool.ClipBox._post_load_paint_pending = True

        _on_load_post("ignored.blend")

        assert tool.ClipBox._file_loading is True
        assert tool.ClipBox._post_load_paint_pending is True

    def test_first_pre_view_clears_gate_and_kicks_refresh(self):
        tool.ClipBox._file_loading = True
        tool.ClipBox._post_load_paint_pending = True

        with patch.object(tool.ClipBox, "schedule_refresh") as mock_refresh:
            tool.ClipBox.on_pre_view()

        assert tool.ClipBox._file_loading is False
        assert tool.ClipBox._post_load_paint_pending is False
        mock_refresh.assert_called_once()

    def test_subsequent_pre_view_does_not_re_kick(self):
        with patch.object(tool.ClipBox, "schedule_refresh") as mock_refresh:
            tool.ClipBox.on_pre_view()

        mock_refresh.assert_not_called()

    def test_depsgraph_update_no_op_while_loading(self):
        tool.ClipBox._file_loading = True

        with patch.object(tool.ClipBox, "_active_scene_props") as mock_props:
            tool.ClipBox.on_depsgraph_update(bpy.context.scene, bpy.context.evaluated_depsgraph_get())

        mock_props.assert_not_called()
