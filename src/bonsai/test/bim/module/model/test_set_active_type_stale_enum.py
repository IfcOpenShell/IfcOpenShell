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
live items, and a plain assignment raises
``TypeError: bpy_struct: item.attr = val: enum "<id>" not found in (...)``,
aborting the whole IFC operator.

The fix must not just avoid the crash: it must resolve the clicked id
against the live IFC model, refresh the stale cache (switching
``ifc_class`` first if the id belongs to a different class), and *complete*
the user's click. Only a genuinely deleted type should be left unapplied,
and even then the user must be told via ``self.report(...)`` rather than
the operator silently doing nothing.
"""

from unittest import mock

import pytest

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    import bpy

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


class _FakeEntity:
    """Stand-in for an ``ifcopenshell.entity_instance`` IFC type element."""

    def __init__(self, id_: int, ifc_class: str, name: str):
        self._id = id_
        self._class = ifc_class
        self.Name = name

    def id(self) -> int:
        return self._id

    def is_a(self) -> str:
        return self._class


class _FakeIfcFile:
    """Stand-in for ``ifcopenshell.file``: ``by_id`` on a missing id raises
    ``RuntimeError``, exactly like the real API when the entity was
    deleted."""

    def __init__(self, entities: list[_FakeEntity]):
        self._entities = {e.id(): e for e in entities}

    def by_id(self, id_: int) -> _FakeEntity:
        try:
            return self._entities[id_]
        except KeyError:
            raise RuntimeError(f"Instance not found: #{id_}")


class _FakeModelProps:
    """Stand-in for ``BIMModelProperties`` that reproduces Blender's dynamic
    ``EnumProperty`` contract for ``relating_type_id`` *and* ``ifc_class``:
    assigning a value outside the current valid set raises ``TypeError``,
    exactly like the real ``enum "<id>" not found in (...)`` error reported
    in #8850. ``class_to_ids`` mirrors what ``update_ifc_class`` does for
    real - switching ``ifc_class`` to a *different* value rebuilds the
    valid ``relating_type_id`` set for that class. Blender does not fire an
    ``EnumProperty``'s update callback when the value doesn't change, so
    reassigning the *same* ``ifc_class`` deliberately leaves
    ``relating_type_id``'s valid set untouched here too."""

    def __init__(
        self,
        valid_ids: set[str],
        initial_relating_type_id: str,
        valid_classes: set[str],
        initial_ifc_class: str,
        class_to_ids: dict[str, set[str]],
    ):
        object.__setattr__(self, "_valid_ids", set(valid_ids))
        object.__setattr__(self, "_valid_classes", set(valid_classes))
        object.__setattr__(self, "_class_to_ids", class_to_ids)
        object.__setattr__(self, "relating_type_id", initial_relating_type_id)
        object.__setattr__(self, "ifc_class", initial_ifc_class)

    def __setattr__(self, name, value):
        if name == "relating_type_id":
            if value not in self._valid_ids:
                raise TypeError(f'bpy_struct: item.attr = val: enum "{value}" not found in {tuple(self._valid_ids)}')
            object.__setattr__(self, name, value)
        elif name == "ifc_class":
            if value not in self._valid_classes:
                raise TypeError(
                    f'bpy_struct: item.attr = val: enum "{value}" not found in {tuple(self._valid_classes)}'
                )
            changed = value != self.ifc_class
            object.__setattr__(self, name, value)
            if changed:
                object.__setattr__(self, "_valid_ids", set(self._class_to_ids.get(value, ())))
        else:
            object.__setattr__(self, name, value)


def _set_active_type(relating_type: int, props: _FakeModelProps, ifc_file: _FakeIfcFile):
    """Drive ``SetActiveType._execute`` against fakes, patching
    ``AuthoringData.refresh_relating_type_id`` to mirror its real effect:
    rebuild ``relating_type_id``'s valid set from whatever ``ifc_class`` is
    currently active in ``props``. Returns the fake operator so tests can
    assert on ``op.report``."""
    import bonsai.bim.module.model.product as product

    def _refresh():
        object.__setattr__(props, "_valid_ids", set(props._class_to_ids.get(props.ifc_class, ())))

    op = mock.Mock()
    op.relating_type = relating_type

    with (
        mock.patch.object(product.tool.Model, "get_model_props", return_value=props),
        mock.patch.object(product.tool.Ifc, "get", return_value=ifc_file),
        mock.patch.object(product.AuthoringData, "refresh_relating_type_id", side_effect=_refresh),
    ):
        product.SetActiveType._execute(op, context=mock.Mock())
    return op


def test_stale_same_class_refreshes_cache_and_completes_the_click():
    """A type was created in the currently-active class after the panel
    last drew (e.g. via Duplicate Type), so its id isn't in the cached
    relating_type_id items yet, but ``ifc_class`` hasn't changed. The
    operator must refresh the cache and land on the requested type -
    not just avoid crashing."""
    ifc_file = _FakeIfcFile(
        [
            _FakeEntity(63, "IfcDoorType", "Door A"),
            _FakeEntity(64, "IfcDoorType", "Door B (just created)"),
        ]
    )
    props = _FakeModelProps(
        valid_ids={"63"},  # 64 missing: stale same-class cache
        initial_relating_type_id="63",
        valid_classes={"IfcDoorType", "IfcWindowType"},
        initial_ifc_class="IfcDoorType",
        class_to_ids={"IfcDoorType": {"63", "64"}},
    )

    _set_active_type(64, props, ifc_file)

    assert props.relating_type_id == "64"


def test_stale_different_class_switches_class_and_completes_the_click():
    """The class tab moved on (Door -> Window) before the click landed:
    the door id is no longer a member of the enum. The operator must
    switch back to the clicked type's own class and land on it - not
    just avoid crashing and leave the click un-actioned."""
    ifc_file = _FakeIfcFile(
        [
            _FakeEntity(63, "IfcDoorType", "Door A"),
            _FakeEntity(70, "IfcWindowType", "Window A"),
        ]
    )
    props = _FakeModelProps(
        valid_ids={"63"},
        initial_relating_type_id="63",
        valid_classes={"IfcDoorType", "IfcWindowType"},
        initial_ifc_class="IfcDoorType",
        class_to_ids={"IfcDoorType": {"63"}, "IfcWindowType": {"70"}},
    )

    _set_active_type(70, props, ifc_file)

    assert props.ifc_class == "IfcWindowType"
    assert props.relating_type_id == "70"


def test_valid_id_is_still_assigned():
    """The common case - no staleness at all - must keep working."""
    ifc_file = _FakeIfcFile([_FakeEntity(63, "IfcDoorType", "Door A"), _FakeEntity(64, "IfcDoorType", "Door B")])
    props = _FakeModelProps(
        valid_ids={"63", "64"},
        initial_relating_type_id="63",
        valid_classes={"IfcDoorType"},
        initial_ifc_class="IfcDoorType",
        class_to_ids={"IfcDoorType": {"63", "64"}},
    )

    _set_active_type(64, props, ifc_file)

    assert props.relating_type_id == "64"


def test_deleted_type_reports_warning_and_leaves_props_untouched():
    """The type was deleted between draw and click (id no longer resolves
    at all, in any class). The operator must not crash, must leave
    relating_type_id at whatever valid value it had, AND must tell the
    user via self.report - not fail silently."""
    ifc_file = _FakeIfcFile([_FakeEntity(63, "IfcDoorType", "Door A")])  # 999 does not exist
    props = _FakeModelProps(
        valid_ids={"63"},
        initial_relating_type_id="63",
        valid_classes={"IfcDoorType"},
        initial_ifc_class="IfcDoorType",
        class_to_ids={"IfcDoorType": {"63"}},
    )

    op = _set_active_type(999, props, ifc_file)

    assert props.relating_type_id == "63"
    op.report.assert_called_once()
    (report_level, _message), _kwargs = op.report.call_args
    assert report_level == {"WARNING"}
