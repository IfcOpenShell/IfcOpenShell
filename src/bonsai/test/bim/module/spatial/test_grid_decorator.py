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

"""Regression tests for #9232: this is the Spatial module's own
``GridDecorator`` (distinct from ``bonsai.bim.module.drawing.decoration``'s
``GridDecorator``), which draws the always-on grid axis labels installed by
``tool.Root.reload_grid_decorator()`` on every project load. It carried the
exact same bug: the label text was split off the Blender object's display
name at the first dot instead of read from the linked IfcGridAxis entity.

``GridDecorator`` is built with ``__new__`` (skipping ``ViewportDecorator``
init) so these tests never touch a live GPU/blf backend."""

import types
from unittest.mock import Mock

import bpy
import pytest

pytestmark = pytest.mark.spatial


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def _fake_obj(name):
    from mathutils import Vector

    obj = Mock(spec=["name", "visible_get", "select_get", "matrix_world", "data"])
    obj.name = name
    obj.visible_get.return_value = True
    obj.select_get.return_value = False
    obj.matrix_world = __import__("mathutils").Matrix.Identity(4)
    obj.data = Mock(vertices=[Mock(co=Vector((0, 0, 0))), Mock(co=Vector((1, 0, 0)))])
    return obj


def _drawn_labels(obj, monkeypatch, element=None):
    from types import SimpleNamespace

    from mathutils import Vector

    import bonsai.bim.module.spatial.decorator as spatial_decoration
    import bonsai.tool as tool

    monkeypatch.setattr(spatial_decoration, "location_3d_to_region_2d", lambda region, region3d, v: Vector((0, 0)))
    monkeypatch.setattr(tool.Ifc, "get_entity", lambda o: element)
    monkeypatch.setattr(
        tool.Blender,
        "get_addon_preferences",
        staticmethod(
            lambda: SimpleNamespace(
                decorator_color_selected=(1, 1, 1, 1),
                decorator_color_unselected=(1, 1, 1, 1),
                decorator_color_special=(1, 1, 1, 1),
            )
        ),
    )
    monkeypatch.setattr(tool.Blender, "is_addon_enabled", staticmethod(lambda: True))
    monkeypatch.setattr(
        tool.Spatial, "get_grid_props", staticmethod(lambda: SimpleNamespace(grid_axes=[SimpleNamespace(obj=obj)]))
    )

    import blf

    drawn = []
    monkeypatch.setattr(blf, "draw", lambda font_id, text: drawn.append(text))
    monkeypatch.setattr(blf, "dimensions", lambda font_id, text: (10.0, 10.0))

    decorator = spatial_decoration.GridDecorator.__new__(spatial_decoration.GridDecorator)
    context = SimpleNamespace(region=object(), region_data=object(), mode="OBJECT")
    decorator.draw_text(context)

    assert len(drawn) == 2
    assert drawn[0] == drawn[1]
    return drawn[0]


def test_dotted_axis_tag_renders_in_full_from_the_ifc_entity(monkeypatch):
    element = Mock(AxisTag="a.1")
    text = _drawn_labels(_fake_obj("IfcGridAxis/a.1"), monkeypatch, element=element)
    assert text == "a.1"


@pytest.mark.parametrize("tag", ["a.A", "b.C", "b.5"])
def test_letter_and_numeric_suffixes_render_in_full(monkeypatch, tag):
    element = Mock(AxisTag=tag)
    text = _drawn_labels(_fake_obj(f"IfcGridAxis/{tag}"), monkeypatch, element=element)
    assert text == tag


def test_missing_element_fallback_strips_only_a_real_blender_suffix(monkeypatch):
    text = _drawn_labels(_fake_obj("IfcGridAxis/a.1.001"), monkeypatch, element=None)
    assert text == "a.1"


def test_missing_element_fallback_does_not_strip_a_single_digit_suffix(monkeypatch):
    text = _drawn_labels(_fake_obj("IfcGridAxis/a.5"), monkeypatch, element=None)
    assert text == "a.5"
