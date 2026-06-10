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

"""Cache-invalidation tests for ``tool.Blender.Modifier.any_selected_is_array_child``.

The wall-topology gizmo gate calls this on every viewport input event. The
underlying ``is_array_child`` check is a BBIM_Array pset lookup per selected
object; without memoisation that runs N_selected times per event. These
tests pin that the cache reuses results across identical (selection, IFC
generation) pairs and invalidates on either change."""

from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _reset_memo():
    from bonsai import tool

    saved = getattr(tool.Blender.Modifier, "_any_selected_array_child_memo", None)
    tool.Blender.Modifier._any_selected_array_child_memo = None
    yield
    tool.Blender.Modifier._any_selected_array_child_memo = saved


def _mock_obj(name: str) -> Mock:
    obj = Mock()
    obj.name = name
    return obj


def test_repeat_call_within_generation_reuses_cache():
    from bonsai import tool

    obj_a = _mock_obj("Wall.001")
    obj_b = _mock_obj("Wall.002")

    is_array_child_calls = {"n": 0}

    def counting_is_array_child(elem):
        is_array_child_calls["n"] += 1
        return False

    with patch("bonsai.tool.blender.tool.Blender.get_selected_objects", return_value=[obj_a, obj_b]), patch(
        "bonsai.tool.blender.tool.Parametric.get_geom_generation", return_value=5
    ), patch("bonsai.tool.blender.tool.Ifc.get_entity", return_value=Mock()), patch.object(
        tool.Blender.Modifier, "is_array_child", side_effect=counting_is_array_child
    ):
        first = tool.Blender.Modifier.any_selected_is_array_child()
        second = tool.Blender.Modifier.any_selected_is_array_child()

    assert first is False
    assert second is False
    assert is_array_child_calls["n"] == 2, "First call walks N_selected; second call must reuse cached result"


def test_generation_advance_invalidates_cache():
    from bonsai import tool

    obj = _mock_obj("Wall.001")
    gen_state = {"gen": 1}

    call_count = {"n": 0}

    def counting_is_array_child(elem):
        call_count["n"] += 1
        return False

    with patch("bonsai.tool.blender.tool.Blender.get_selected_objects", return_value=[obj]), patch(
        "bonsai.tool.blender.tool.Parametric.get_geom_generation", side_effect=lambda: gen_state["gen"]
    ), patch("bonsai.tool.blender.tool.Ifc.get_entity", return_value=Mock()), patch.object(
        tool.Blender.Modifier, "is_array_child", side_effect=counting_is_array_child
    ):
        tool.Blender.Modifier.any_selected_is_array_child()
        first = call_count["n"]
        gen_state["gen"] = 2
        tool.Blender.Modifier.any_selected_is_array_child()

    assert call_count["n"] > first


def test_selection_change_invalidates_cache():
    from bonsai import tool

    obj_a = _mock_obj("Wall.001")
    obj_b = _mock_obj("Wall.002")
    selection = {"sel": [obj_a]}

    call_count = {"n": 0}

    def counting_is_array_child(elem):
        call_count["n"] += 1
        return False

    with patch("bonsai.tool.blender.tool.Blender.get_selected_objects", side_effect=lambda: selection["sel"]), patch(
        "bonsai.tool.blender.tool.Parametric.get_geom_generation", return_value=1
    ), patch("bonsai.tool.blender.tool.Ifc.get_entity", return_value=Mock()), patch.object(
        tool.Blender.Modifier, "is_array_child", side_effect=counting_is_array_child
    ):
        tool.Blender.Modifier.any_selected_is_array_child()
        first = call_count["n"]
        selection["sel"] = [obj_a, obj_b]
        tool.Blender.Modifier.any_selected_is_array_child()

    assert call_count["n"] > first


def test_short_circuits_on_first_hit():
    """``is_array_child`` returning True for the first selected object must
    short-circuit; the rest of the selection isn't walked. Belt-and-suspenders
    test — the early-return existed before the cache wrap and must survive it."""
    from bonsai import tool

    obj_a = _mock_obj("Wall.001")
    obj_b = _mock_obj("Wall.002")
    obj_c = _mock_obj("Wall.003")

    call_count = {"n": 0}

    def counting_is_array_child(elem):
        call_count["n"] += 1
        return True

    with patch("bonsai.tool.blender.tool.Blender.get_selected_objects", return_value=[obj_a, obj_b, obj_c]), patch(
        "bonsai.tool.blender.tool.Parametric.get_geom_generation", return_value=1
    ), patch("bonsai.tool.blender.tool.Ifc.get_entity", return_value=Mock()), patch.object(
        tool.Blender.Modifier, "is_array_child", side_effect=counting_is_array_child
    ):
        result = tool.Blender.Modifier.any_selected_is_array_child()

    assert result is True
    assert call_count["n"] == 1
