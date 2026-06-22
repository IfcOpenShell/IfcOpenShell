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

"""Pins the ``clip_only_ifc_products`` toggle contract.

The toggle gates the cap-eligibility filter (IFC-only vs. all visible meshes)
and lives only on the Blender Scene PG — the project pset must never carry it.
"""

import math

import bpy
import ifcopenshell
import pytest
from mathutils import Matrix, Vector

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.clip_box


def _make_ifc_wall(ifc, location=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=location)
    obj = bpy.context.active_object
    entity = ifc.create_entity("IfcWall")
    tool.Ifc.link(entity, obj)
    return entity, obj


def _make_blender_cube(location=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=location)
    return bpy.context.active_object


class TestDefaultIsTrue(NewFile):
    def test_clip_only_ifc_products_defaults_to_true(self):
        scene_props = tool.ClipBox.get_scene_props()
        assert scene_props.clip_only_ifc_products is True


class TestCapEligibilityHonorsToggle(NewFile):
    def test_only_ifc_true_excludes_non_ifc_mesh(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        _, wall = _make_ifc_wall(ifc, location=(0.0, 0.0, 0.0))
        cube = _make_blender_cube(location=(4.0, 0.0, 0.0))
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.clip_only_ifc_products = True

        eligible = set(tool.ClipBox._iter_capable_objects(bpy.context.scene))

        assert wall in eligible
        assert cube not in eligible

    def test_only_ifc_false_includes_non_ifc_mesh(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        _, wall = _make_ifc_wall(ifc, location=(0.0, 0.0, 0.0))
        cube = _make_blender_cube(location=(4.0, 0.0, 0.0))
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.clip_only_ifc_products = False

        eligible = set(tool.ClipBox._iter_capable_objects(bpy.context.scene))

        assert wall in eligible
        assert cube in eligible

    def test_only_ifc_false_works_without_ifc_file_loaded(self):
        # No IFC at all; eligibility should still yield Blender meshes when
        # the IFC-only filter is off, since there's nothing to filter against.
        cube = _make_blender_cube(location=(0.0, 0.0, 0.0))
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.clip_only_ifc_products = False

        eligible = set(tool.ClipBox._iter_capable_objects(bpy.context.scene))

        assert cube in eligible


class TestShowCapsTriggersRebuild(NewFile):
    def test_show_caps_off_then_on_schedules_cap_rebuild(self):
        # Off → On must schedule a rebuild — without this, caps stay empty
        # until the user nudges geometry to fire the next depsgraph tick.
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.show_caps = False
        tool.ClipBox._cancel_pending_cap_rebuild()
        assert tool.ClipBox._pending_cap_rebuild is None

        scene_props.show_caps = True

        assert tool.ClipBox._pending_cap_rebuild is not None
        tool.ClipBox._cancel_pending_cap_rebuild()


class TestRebuildCapsNow(NewFile):
    def test_rebuild_caps_now_cancels_any_pending_debounce(self):
        # Synchronous path must wipe the debounced timer — otherwise the
        # rebuild fires twice when the gizmo unlock interleaves with a
        # depsgraph tick.
        bpy.ops.bim.add_clip_box()
        tool.ClipBox._schedule_cap_rebuild()
        assert tool.ClipBox._pending_cap_rebuild is not None

        tool.ClipBox.rebuild_caps_now()

        assert tool.ClipBox._pending_cap_rebuild is None


class TestActiveClipBoxIndexRebuildsCaps(NewFile):
    def test_index_change_schedules_cap_rebuild(self):
        # UI-list click changes active_clip_box_index — the cap cache
        # belongs to the previous box's clip volume, so a rebuild must
        # be scheduled so the overlay matches the newly-active box.
        bpy.ops.bim.add_clip_box()
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        tool.ClipBox._cancel_pending_cap_rebuild()
        assert tool.ClipBox._pending_cap_rebuild is None

        scene_props.active_clip_box_index = 0

        assert tool.ClipBox._pending_cap_rebuild is not None
        tool.ClipBox._cancel_pending_cap_rebuild()


def _exec_align_view(axis: int, is_max: bool):
    """Run ``bim.align_view_to_clip_face`` against the first VIEW_3D area
    and return its ``rv3d``. Skips if no viewport is available in the
    test session."""
    for area in bpy.context.window.screen.areas:
        if area.type != "VIEW_3D":
            continue
        region = next((r for r in area.regions if r.type == "WINDOW"), None)
        if region is None:
            continue
        with bpy.context.temp_override(area=area, region=region):
            result = bpy.ops.bim.align_view_to_clip_face("EXEC_DEFAULT", axis=axis, is_max=is_max)
            assert result == {"FINISHED"}
            return bpy.context.space_data.region_3d
    pytest.skip("No VIEW_3D area available")


class TestAlignViewToClipFace(NewFile):
    def test_align_view_sets_rv3d_rotation_to_face_normal(self):
        # The operator must reorient the viewport so its forward axis
        # points AGAINST the picked face's outward normal (so the user
        # sees the face from outside).
        bpy.ops.bim.add_clip_box()
        clip_box = tool.ClipBox.get_active_clip_box()
        # Rotate the empty so the +X face's outward world normal isn't
        # axis-aligned — proves the operator handles arbitrary rotation.
        clip_box.matrix_world = Matrix.Rotation(math.radians(30), 4, "Z") @ clip_box.matrix_world

        rv3d = _exec_align_view(axis=0, is_max=True)

        outward = clip_box.matrix_world.to_3x3().col[0].normalized()
        forward = rv3d.view_rotation @ Vector((0.0, 0.0, -1.0))
        assert (forward - (-outward)).length < 1e-4

    def test_align_view_uses_box_local_z_up_for_side_face(self):
        # Side faces (±X, ±Y local normals) follow Blender's numpad 1 / 3
        # convention but in the BOX'S local frame: local +Z is the
        # screen-up axis, transformed through the empty's rotation.
        bpy.ops.bim.add_clip_box()
        clip_box = tool.ClipBox.get_active_clip_box()
        clip_box.matrix_world = Matrix.Rotation(math.radians(45), 4, "Z") @ clip_box.matrix_world

        rv3d = _exec_align_view(axis=0, is_max=True)

        expected_up = (clip_box.matrix_world.to_quaternion() @ Vector((0.0, 0.0, 1.0))).normalized()
        up_world = rv3d.view_rotation @ Vector((0.0, 1.0, 0.0))
        assert (
            up_world - expected_up
        ).length < 1e-3, (
            f"Side-face view must have box-local +Z as up; expected {tuple(expected_up)}, got {tuple(up_world)}"
        )

    def test_align_view_keeps_box_local_z_up_for_negative_y_face(self):
        # Clicking the -Y face used to put world +Z at the BOTTOM of the
        # screen. With box-local convention it stays at the top.
        bpy.ops.bim.add_clip_box()

        rv3d = _exec_align_view(axis=1, is_max=False)

        up_world = rv3d.view_rotation @ Vector((0.0, 1.0, 0.0))
        assert up_world.z > 0.99, f"-Y face view must keep box-local +Z as up, got {tuple(up_world)}"

    def test_align_view_respects_box_local_axes_when_box_x_rotated(self):
        # Rotating around X moves box-local +Z away from world +Z; the
        # up axis must follow the BOX, otherwise the box edges no longer
        # appear horizontal/vertical when aligned to a face — the bug
        # users hit on rotated boxes.
        bpy.ops.bim.add_clip_box()
        clip_box = tool.ClipBox.get_active_clip_box()
        clip_box.matrix_world = Matrix.Rotation(math.radians(30), 4, "X") @ clip_box.matrix_world

        rv3d = _exec_align_view(axis=0, is_max=True)

        expected_up = (clip_box.matrix_world.to_quaternion() @ Vector((0.0, 0.0, 1.0))).normalized()
        up_world = rv3d.view_rotation @ Vector((0.0, 1.0, 0.0))
        assert (
            up_world - expected_up
        ).length < 1e-3, f"X-rotated box must use box-local Z; expected {tuple(expected_up)}, got {tuple(up_world)}"

    def test_align_view_uses_box_local_y_up_for_top_face(self):
        # Top face (local +Z outward) follows Blender's numpad-7
        # convention applied in the box's local frame: local +Y is up.
        bpy.ops.bim.add_clip_box()

        rv3d = _exec_align_view(axis=2, is_max=True)

        up_world = rv3d.view_rotation @ Vector((0.0, 1.0, 0.0))
        assert up_world.y > 0.99, f"Top-face view must have box-local +Y as up, got {tuple(up_world)}"

    def test_align_view_uses_box_local_negative_y_up_for_bottom_face(self):
        # Bottom face (local -Z outward) follows ctrl-numpad-7: box-local
        # -Y is up.
        bpy.ops.bim.add_clip_box()

        rv3d = _exec_align_view(axis=2, is_max=False)

        up_world = rv3d.view_rotation @ Vector((0.0, 1.0, 0.0))
        assert up_world.y < -0.99, f"Bottom-face view must have box-local -Y as up, got {tuple(up_world)}"


class TestNotPersistedToProjectPset(NewFile):
    def test_pset_does_not_carry_clip_only_ifc_products(self):
        bpy.ops.bim.create_project()
        scene_props = tool.ClipBox.get_scene_props()
        # Flip to a non-default value, then trigger a pset write.
        scene_props.clip_only_ifc_products = False
        bpy.ops.bim.add_clip_box()  # writes the pset

        import ifcopenshell.util.element

        project = tool.Ifc.get().by_type("IfcProject")[0]
        pset = ifcopenshell.util.element.get_psets(project).get(tool.ClipBox.PSET_NAME, {})

        # Whatever the pset stores, it must not carry this scene-only toggle.
        for key in pset:
            assert (
                "clip_only_ifc" not in key.lower()
            ), f"Project pset unexpectedly carries the scene-only toggle (key {key!r})"

    def test_load_from_pset_does_not_touch_clip_only_ifc_products(self):
        # Round-trip: set the toggle on the Scene, simulate a pset load, and
        # confirm the loader didn't overwrite the user's Scene-level choice.
        bpy.ops.bim.create_project()
        scene_props = tool.ClipBox.get_scene_props()
        scene_props.clip_only_ifc_products = False

        tool.ClipBox.load_from_project_pset()

        assert scene_props.clip_only_ifc_products is False
