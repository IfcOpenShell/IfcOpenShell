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

"""Regression test for https://github.com/IfcOpenShell/IfcOpenShell/issues/8850.

``BIM_OT_set_active_type``'s ``relating_type`` id is baked into its button at
draw time from ``AuthoringData.data["paginated_relating_types"]``, filtered by
whatever ``ifc_class`` the Type Manager was showing at that moment. If the
class tab (or the underlying type list) changes before the click lands, the
target id is no longer a member of the ``relating_type_id`` EnumProperty's
live items, and the plain assignment raises
``TypeError: bpy_struct: item.attr = val: enum "<id>" not found in (...)``,
aborting the whole IFC operator. Same race already guarded for the sibling
assignment in ``bim/handler.py:update_bim_tool_props`` (see 233cc344fa).
"""

from types import SimpleNamespace
from unittest import mock

import pytest

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    import bpy

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


class _FakeModelProps:
    """Stand-in for ``BIMModelProperties`` that reproduces Blender's dynamic
    ``EnumProperty`` contract for ``relating_type_id``: assigning a value not
    present in ``valid_ids`` raises ``TypeError``, exactly like the real
    ``enum "<id>" not found in (...)`` error reported in #8850."""

    def __init__(self, valid_ids, initial):
        object.__setattr__(self, "_valid_ids", set(valid_ids))
        object.__setattr__(self, "relating_type_id", initial)

    def __setattr__(self, name, value):
        if name == "relating_type_id" and value not in self._valid_ids:
            raise TypeError(f'bpy_struct: item.attr = val: enum "{value}" not found in {tuple(self._valid_ids)}')
        object.__setattr__(self, name, value)


def _set_active_type(relating_type, props):
    import bonsai.bim.module.model.product as product

    op = SimpleNamespace(relating_type=relating_type)
    with mock.patch.object(product.tool.Model, "get_model_props", return_value=props):
        return product.SetActiveType._execute(op, context=mock.Mock())


def test_stale_id_does_not_raise_and_leaves_props_untouched():
    """The class tab moved on (e.g. Door -> Window) before the click landed:
    the door id is no longer a member of the enum. The operator must not
    crash, and must leave relating_type_id at whatever valid value it had."""
    props = _FakeModelProps(valid_ids={"63", "64"}, initial="64")

    _set_active_type(65, props)  # must not raise TypeError

    assert props.relating_type_id == "64"


def test_valid_id_is_still_assigned():
    """Guarding the stale case must not swallow legitimate assignments."""
    props = _FakeModelProps(valid_ids={"63", "64"}, initial="63")

    _set_active_type(64, props)

    assert props.relating_type_id == "64"
