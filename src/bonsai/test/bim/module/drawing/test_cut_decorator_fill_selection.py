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

"""Regression test for #5133: a selected IfcAnnotation whose visible cut is a
solid fill (not just a thin edge) must show a selection cue too.

``CutDecorator.__call__`` groups line/point cut geometry into
``all_vertices``/``selected_vertices`` and draws the latter in the addon's
selection-highlight colour. The polygon fills built from ``fill_cache`` used
to be grouped only by material colour, with no selection split, so a
selected annotation whose surface is a solid fill had no visible cue.

This exercises the real ``CutDecorator.__call__`` end to end (real IFC
project, real geometry bisection, real material colour lookup) and only
stubs the leaf GPU calls, since ``gpu.state``/``gpu.shader`` require an
initialized GPU context that ``--background`` Blender doesn't provide."""

import types
from unittest.mock import MagicMock

import bpy
import pytest

pytestmark = pytest.mark.drawing


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


@pytest.fixture
def two_annotations_crossing_camera_plane():
    """A fresh IFC project with two IfcAnnotation cubes straddling the
    camera's cut plane (world Z=0): one selected, one not."""
    import bonsai.tool as tool

    bpy.ops.bim.create_project()
    scene = bpy.context.scene

    cam_data = bpy.data.cameras.new("cut_decorator_test_cam")
    cam_obj = bpy.data.objects.new("cut_decorator_test_cam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (0, 0, 0)
    cam_obj.rotation_euler = (0, 0, 0)
    scene.camera = cam_obj

    def make_annotation(name, x_offset, select):
        bpy.ops.mesh.primitive_cube_add(size=2.0, location=(x_offset, 0, 0))
        obj = bpy.context.active_object
        obj.name = name
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcAnnotation", predefined_type="NOTE", userdefined_type="")
        obj.select_set(select)
        return obj

    unselected = make_annotation("CutDecoratorTest_Unselected", 0.0, select=False)
    selected = make_annotation("CutDecoratorTest_Selected", 3.0, select=True)
    bpy.context.view_layer.update()

    assert tool.Ifc.get_entity(unselected).is_a("IfcAnnotation")
    assert tool.Ifc.get_entity(selected).is_a("IfcAnnotation")
    assert unselected.select_get() is False
    assert selected.select_get() is True

    yield unselected, selected


def test_selected_annotation_fill_uses_selection_highlight_colour(monkeypatch, two_annotations_crossing_camera_plane):
    from bonsai.bim.module.drawing import decoration
    from bonsai.bim.module.drawing.decoration import CutDecorator, DecoratorData

    # `two_annotations_crossing_camera_plane` already created the objects
    # (one selected, one not) in the current scene; nothing to unpack here.

    # Stub only the leaf GPU calls: gpu.state/gpu.shader need an initialized
    # GPU context, unavailable in --background Blender. Everything else
    # (the fill/selection grouping under test) runs unmodified.
    fake_shader = MagicMock()
    monkeypatch.setattr(decoration.gpu.state, "point_size_set", lambda *a, **k: None)
    monkeypatch.setattr(decoration.gpu.state, "blend_set", lambda *a, **k: None)
    monkeypatch.setattr(decoration.gpu.shader, "from_builtin", lambda *a, **k: fake_shader)

    recorded_tris_colours = []

    def recording_draw_batch(self, shader_type, content_pos, color, indices=None):
        if shader_type == "TRIS":
            recorded_tris_colours.append(tuple(color))
        # Skip the real implementation entirely: batch_for_shader/.draw()
        # also require an initialized GPU context.

    monkeypatch.setattr(CutDecorator, "draw_batch", recording_draw_batch)

    fake_context = types.SimpleNamespace(
        scene=bpy.context.scene,
        screen=types.SimpleNamespace(areas=[]),
        region=types.SimpleNamespace(width=800, height=600),
    )

    DecoratorData.cut_cache.clear()
    DecoratorData.slice_cache.clear()
    DecoratorData.fill_cache.clear()

    handler = CutDecorator()
    handler(fake_context)

    import bonsai.tool as tool

    selected_elements_color = tuple(tool.Blender.get_addon_preferences().decorator_color_selected)

    assert recorded_tris_colours, "no fill (TRIS) batches were drawn for either annotation"
    assert (
        selected_elements_color in recorded_tris_colours
    ), "the selected annotation's fill must be drawn in the selection-highlight colour"
    assert any(
        c != selected_elements_color for c in recorded_tris_colours
    ), "the unselected annotation's fill must keep its own (non-highlight) colour"
