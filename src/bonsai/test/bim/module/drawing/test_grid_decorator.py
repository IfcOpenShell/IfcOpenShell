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

"""Regression tests for #9232: the viewport GridDecorator truncated
IfcGridAxis.AxisTag at the first dot (e.g. "a.1" -> "a"), because it derived
the label text by splitting the Blender object's display name instead of
reading AxisTag from the linked IFC entity.

``GridDecorator`` is built with ``__new__`` (skipping ``BaseDecorator.__init__``)
so these tests never touch ``gpu.shader.from_builtin``, which requires a
live GPU context that isn't guaranteed under every Blender test runner.
``draw_label`` and the region-projection helper are stubbed so only the
text-derivation logic under test executes."""

import types
from unittest.mock import Mock

import bpy
import pytest

pytestmark = pytest.mark.drawing


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def _rendered_text(obj, monkeypatch, element=None):
    """Call the real (patched) GridDecorator.draw_labels and return the
    text it asked draw_label to render (both endpoints always get the
    same text, so a single string is returned)."""
    from mathutils import Vector

    import bonsai.bim.module.drawing.decoration as decoration
    import bonsai.tool as tool

    monkeypatch.setattr(decoration, "location_3d_to_region_2d", lambda region, region3d, v: Vector((0.0, 0.0)))
    monkeypatch.setattr(tool.Ifc, "get_entity", lambda o: element)

    captured = []
    decorator = decoration.GridDecorator.__new__(decoration.GridDecorator)
    decorator.draw_label = lambda context, text, *a, **kw: captured.append(text)

    context = Mock(region=object(), region_data=object())
    verts = [Vector((0, 0, 0)), Vector((1, 0, 0))]
    decorator.draw_labels(context, obj, verts)

    assert len(captured) == 2
    assert captured[0] == captured[1]
    return captured[0]


def _fake_obj(name):
    # Mock's constructor special-cases the ``name`` kwarg for its own repr,
    # so the ``.name`` attribute has to be assigned after construction.
    obj = Mock(spec=["name"])
    obj.name = name
    return obj


def test_dotted_axis_tag_renders_in_full_from_the_ifc_entity(monkeypatch):
    element = Mock(AxisTag="a.1")
    text = _rendered_text(_fake_obj("IfcGridAxis/a.1"), monkeypatch, element=element)
    assert text == "a.1"


@pytest.mark.parametrize("tag", ["a.A", "a.B", "a.C", "b.1", "b.C"])
def test_letter_and_numeric_suffixes_render_in_full(monkeypatch, tag):
    element = Mock(AxisTag=tag)
    text = _rendered_text(_fake_obj(f"IfcGridAxis/{tag}"), monkeypatch, element=element)
    assert text == tag


def test_object_name_is_never_consulted_when_the_entity_is_reachable(monkeypatch):
    # The Blender object name is a red herring here (looks pre-truncated);
    # the element's AxisTag must still win.
    element = Mock(AxisTag="a.1")
    text = _rendered_text(_fake_obj("IfcGridAxis/a"), monkeypatch, element=element)
    assert text == "a.1"


def test_missing_element_falls_back_to_object_name_untouched(monkeypatch):
    # No linked IFC entity: fall back to the object name. A dotted tag with
    # no real Blender duplicate suffix must be left exactly as-is.
    text = _rendered_text(_fake_obj("IfcGridAxis/a.1"), monkeypatch, element=None)
    assert text == "a.1"


def test_missing_element_fallback_strips_only_a_real_blender_suffix(monkeypatch):
    # Blender appended ".001" for a name collision; the fallback must strip
    # only that trailing suffix, not the axis tag's own dot.
    text = _rendered_text(_fake_obj("IfcGridAxis/a.1.001"), monkeypatch, element=None)
    assert text == "a.1"


def test_missing_element_fallback_does_not_strip_a_single_digit_suffix(monkeypatch):
    # A single trailing digit is legitimate axis-tag content, not a
    # Blender-generated ".001"-style duplicate suffix.
    text = _rendered_text(_fake_obj("IfcGridAxis/a.5"), monkeypatch, element=None)
    assert text == "a.5"


def test_element_with_falsy_axis_tag_falls_back_to_object_name(monkeypatch):
    element = Mock(AxisTag=None)
    text = _rendered_text(_fake_obj("IfcGridAxis/a.1"), monkeypatch, element=element)
    assert text == "a.1"
