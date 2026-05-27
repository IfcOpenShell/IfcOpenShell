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

"""Unit coverage for the shared parametric-edit lifecycle mixins.

``bonsai.bim.parametric_lifecycle`` is the load-bearing path for 4 of 6
parametric features (door, window, railing, roof). The registry smoke test
elsewhere verifies operators are wired up; the mixins' own state-transition
contracts are tested here.

The mixins are exercised through minimal in-test subclasses that supply the
abstract hooks (``_is_element_type``, ``_get_props``, etc.). All ``tool.*`` and
``ifcopenshell.*`` references at the module top of ``parametric_lifecycle`` are
patched at the module attribute (not the source module) so each test sees
isolated mock state."""

import json
from typing import ClassVar
from unittest import mock

import pytest

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    import bpy

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


class _FakeProps:
    """Stand-in for ``BIM<Name>Properties`` — records what was set so tests can
    assert state transitions without instantiating real PropertyGroups."""

    def __init__(self):
        self.is_editing = False
        self.last_kwargs = None
        self.general = {"width": 1000}
        self.lining = {"thickness": 50}
        self.panel = {"material": "wood"}

    def set_props_kwargs_from_ifc_data(self, data):
        self.last_kwargs = dict(data)

    def get_general_kwargs(self, convert_to_project_units=True):
        return dict(self.general)

    def get_lining_kwargs(self, convert_to_project_units=True):
        return dict(self.lining)

    def get_panel_kwargs(self, convert_to_project_units=True):
        return dict(self.panel)


def _make_obj(props):
    obj = mock.Mock()
    obj.props = props
    obj.name = "TestObj"
    return obj


def _make_pset_text(general, lining, panel):
    payload = {"lining_properties": lining, "panel_properties": panel, **general}
    return json.dumps(payload)


# ----------------------------------------------------------------------
# FeatureModifierEditMixin (door/window pattern)
# ----------------------------------------------------------------------


def _door_mixin_cls(match=True, raise_on_update=False):
    from bonsai.bim.parametric_lifecycle import FeatureModifierEditMixin

    raised = raise_on_update

    class _TestDoorMixin(FeatureModifierEditMixin):
        pset_name: ClassVar[str] = "BBIM_Door"
        representations_called: ClassVar[list] = []

        @classmethod
        def _is_element_type(cls, element):
            return match

        @classmethod
        def _get_props(cls, obj):
            return obj.props

        @classmethod
        def _update_modifier_representation(cls, obj, context):
            cls.representations_called.append(obj)
            if raised:
                raise RuntimeError("simulated representation failure")

    return _TestDoorMixin


@pytest.fixture
def patched_tool_and_ifc():
    """Patch ``tool`` and ``ifcopenshell.*`` references on the lifecycle module.

    Yields ``(mock_tool, mock_ifc_util_element, mock_ifc_api_pset,
    mock_ifc_util_rep, mock_core_geometry)`` so tests can configure return
    values and assert call args."""
    target = "bonsai.bim.parametric_lifecycle"
    with mock.patch(f"{target}.tool") as mock_tool, mock.patch(f"{target}.ifcopenshell") as mock_ifc, mock.patch(
        f"{target}.bonsai"
    ) as mock_bonsai:
        # Element returned by tool.Ifc.get_entity is reused across mocks.
        element = mock.Mock(name="entity")
        mock_tool.Ifc.get_entity.return_value = element
        mock_tool.Ifc.get.return_value = mock.Mock(name="ifc_file")
        mock_tool.Model.get_constituents_props_data.return_value = {"materials": []}
        mock_tool.Pset.get_element_pset.return_value = mock.Mock(name="pset")
        mock_ifc.util.element.get_type.return_value = None  # skip thumbnail mark
        yield {
            "tool": mock_tool,
            "ifc": mock_ifc,
            "bonsai": mock_bonsai,
            "element": element,
        }


def test_feature_modifier_enable_one_sets_is_editing_and_loads_kwargs(patched_tool_and_ifc):
    props = _FakeProps()
    obj = _make_obj(props)
    patched_tool_and_ifc["ifc"].util.element.get_pset.return_value = _make_pset_text(
        {"width": 1234}, {"thickness": 50}, {"material": "wood"}
    )

    cls = _door_mixin_cls(match=True)
    cls._enable_one(obj)

    assert props.is_editing is True
    assert props.last_kwargs is not None
    assert props.last_kwargs["width"] == 1234
    assert props.last_kwargs["thickness"] == 50
    assert props.last_kwargs["material"] == "wood"
    assert "materials" in props.last_kwargs  # from get_constituents_props_data


def test_feature_modifier_enable_one_noop_when_element_not_match(patched_tool_and_ifc):
    props = _FakeProps()
    obj = _make_obj(props)

    cls = _door_mixin_cls(match=False)
    cls._enable_one(obj)

    assert props.is_editing is False
    assert props.last_kwargs is None
    # get_pset must not be called when _is_element_type returns False — the
    # _resolve guard short-circuits before reading pset data.
    patched_tool_and_ifc["ifc"].util.element.get_pset.assert_not_called()


def test_feature_modifier_enable_one_noop_when_no_entity(patched_tool_and_ifc):
    """tool.Ifc.get_entity returning None must short-circuit before predicate runs."""
    props = _FakeProps()
    obj = _make_obj(props)
    patched_tool_and_ifc["tool"].Ifc.get_entity.return_value = None

    cls = _door_mixin_cls(match=True)
    cls._enable_one(obj)

    assert props.is_editing is False


def test_feature_modifier_finish_one_clears_is_editing_and_writes_pset(patched_tool_and_ifc):
    props = _FakeProps()
    props.is_editing = True
    obj = _make_obj(props)
    ctx = mock.Mock(name="context")

    cls = _door_mixin_cls(match=True)
    cls._finish_one(obj, ctx)

    assert props.is_editing is False
    assert obj in cls.representations_called
    # tool.Pset.write_bbim_data is called exactly once with the merged dict.
    patched_tool_and_ifc["tool"].Pset.write_bbim_data.assert_called_once()
    call_args = patched_tool_and_ifc["tool"].Pset.write_bbim_data.call_args
    assert call_args.args[1] == "BBIM_Door"  # pset_name positional arg
    written_data = call_args.args[2]
    assert "lining_properties" in written_data and "panel_properties" in written_data


def test_feature_modifier_finish_one_exception_leaves_draft_in_progress(patched_tool_and_ifc):
    """If _update_modifier_representation raises, is_editing must stay True
    so the user's draft survives for retry. This is the contract called out
    in parametric_lifecycle.py:161 — set is_editing=False only on success."""
    props = _FakeProps()
    props.is_editing = True
    obj = _make_obj(props)
    ctx = mock.Mock(name="context")

    cls = _door_mixin_cls(match=True, raise_on_update=True)
    with pytest.raises(RuntimeError, match="simulated representation failure"):
        cls._finish_one(obj, ctx)

    assert props.is_editing is True  # draft survives


def test_feature_modifier_cancel_one_restores_and_clears_is_editing(patched_tool_and_ifc):
    props = _FakeProps()
    props.is_editing = True
    obj = _make_obj(props)
    patched_tool_and_ifc["ifc"].util.element.get_pset.return_value = _make_pset_text(
        {"width": 900}, {"thickness": 60}, {"material": "steel"}
    )

    cls = _door_mixin_cls(match=True)
    cls._cancel_one(obj)

    assert props.is_editing is False
    assert props.last_kwargs is not None and props.last_kwargs["width"] == 900
    # switch_representation must be called via bonsai.core.geometry.
    patched_tool_and_ifc["bonsai"].core.geometry.switch_representation.assert_called_once()


def test_feature_modifier_targets_loop_uses_iter_targets(patched_tool_and_ifc):
    """_enable_targets / _finish_targets / _cancel_targets iterate
    _iter_targets — default is [active_object]; subclasses can override."""
    props_a, props_b = _FakeProps(), _FakeProps()
    obj_a, obj_b = _make_obj(props_a), _make_obj(props_b)
    patched_tool_and_ifc["ifc"].util.element.get_pset.return_value = _make_pset_text(
        {"width": 1000}, {"thickness": 50}, {"material": "wood"}
    )

    cls = _door_mixin_cls(match=True)
    cls._iter_targets = classmethod(lambda c, ctx: [obj_a, obj_b])

    result = cls()._enable_targets(mock.Mock())

    assert result == {"FINISHED"}
    assert props_a.is_editing is True
    assert props_b.is_editing is True


# ----------------------------------------------------------------------
# PathPreservingEditMixin (railing/roof pattern)
# ----------------------------------------------------------------------


class _FakePathProps:
    """Stand-in for railing/roof properties — get_general_kwargs only (no lining/panel)."""

    def __init__(self):
        self.is_editing = False
        self.last_kwargs = None
        self.general = {"width": 200, "thickness": 10}

    def set_props_kwargs_from_ifc_data(self, data):
        self.last_kwargs = dict(data)

    def get_general_kwargs(self, convert_to_project_units=True):
        return dict(self.general)


def _path_mixin_cls(match=True):
    from bonsai.bim.parametric_lifecycle import PathPreservingEditMixin

    class _TestPathMixin(PathPreservingEditMixin):
        pset_name: ClassVar[str] = "BBIM_Railing"
        pset_updates: ClassVar[list] = []
        ifc_data_updates: ClassVar[list] = []
        bmesh_updates: ClassVar[list] = []

        @classmethod
        def _is_element_type(cls, element):
            return match

        @classmethod
        def _get_props(cls, obj):
            return obj.props

        @classmethod
        def _update_pset(cls, element, data):
            cls.pset_updates.append((element, data))

        @classmethod
        def _update_modifier_ifc_data(cls, obj, context):
            cls.ifc_data_updates.append(obj)

        @classmethod
        def _restore_viewport_after_cancel(cls, obj, context):
            cls.bmesh_updates.append(obj)

    return _TestPathMixin


def test_path_preserving_enable_one_sets_is_editing(patched_tool_and_ifc):
    props = _FakePathProps()
    obj = _make_obj(props)
    patched_tool_and_ifc["tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {"width": 250, "path_data": {"points": [[0, 0], [1, 0]]}}
    }

    cls = _path_mixin_cls(match=True)
    cls._enable_one(obj)

    assert props.is_editing is True
    assert props.last_kwargs is not None
    assert props.last_kwargs["width"] == 250
    # path_data passes through (default _post_load_data is pass-through)
    assert props.last_kwargs["path_data"] == {"points": [[0, 0], [1, 0]]}


def test_path_preserving_finish_one_preserves_path_data_and_clears_is_editing(patched_tool_and_ifc):
    props = _FakePathProps()
    props.is_editing = True
    obj = _make_obj(props)
    ctx = mock.Mock(name="context")
    sentinel_path = {"points": [[5, 5], [9, 9]], "edges": [[0, 1]]}
    patched_tool_and_ifc["tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {"path_data": sentinel_path}
    }

    cls = _path_mixin_cls(match=True)
    cls._finish_one(obj, ctx)

    assert props.is_editing is False
    assert cls.pset_updates, "_update_pset must be called on Finish"
    assert cls.pset_updates[-1][1]["path_data"] is sentinel_path  # preserved by reference
    assert obj in cls.ifc_data_updates


def test_path_preserving_cancel_one_calls_restore_viewport_after_cancel(patched_tool_and_ifc):
    props = _FakePathProps()
    props.is_editing = True
    obj = _make_obj(props)
    ctx = mock.Mock(name="context")
    patched_tool_and_ifc["tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {"width": 250, "path_data": {"points": []}}
    }

    cls = _path_mixin_cls(match=True)
    cls._cancel_one(obj, ctx)

    assert props.is_editing is False
    assert obj in cls.bmesh_updates


def test_path_preserving_enable_one_post_load_data_hook_runs(patched_tool_and_ifc):
    """Railing overrides _post_load_data to JSON-serialise path_data —
    confirm the hook is honoured (here we drop a sentinel key)."""
    props = _FakePathProps()
    obj = _make_obj(props)
    patched_tool_and_ifc["tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {"width": 250, "extra": "drop_me"}
    }

    cls = _path_mixin_cls(match=True)
    cls._post_load_data = classmethod(lambda c, data: {k: v for k, v in data.items() if k != "extra"})
    cls._enable_one(obj)

    assert "extra" not in props.last_kwargs


# ----------------------------------------------------------------------
# _ParametricEditMixinBase._resolve guard
# ----------------------------------------------------------------------


def test_resolve_returns_none_when_obj_has_no_entity(patched_tool_and_ifc):
    cls = _door_mixin_cls(match=True)
    patched_tool_and_ifc["tool"].Ifc.get_entity.return_value = None
    obj = _make_obj(_FakeProps())

    assert cls._resolve(obj) is None


def test_resolve_returns_none_when_element_type_mismatch(patched_tool_and_ifc):
    cls = _door_mixin_cls(match=False)
    obj = _make_obj(_FakeProps())

    assert cls._resolve(obj) is None


def test_resolve_returns_tuple_when_match(patched_tool_and_ifc):
    cls = _door_mixin_cls(match=True)
    props = _FakeProps()
    obj = _make_obj(props)

    resolved = cls._resolve(obj)

    assert resolved is not None
    element, returned_props = resolved
    assert element is patched_tool_and_ifc["element"]
    assert returned_props is props
