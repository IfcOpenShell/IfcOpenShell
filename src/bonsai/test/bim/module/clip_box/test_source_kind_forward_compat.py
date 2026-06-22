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

"""Forward-compat guards for the source-based clip-box wiring.

Adding a new source kind requires matching entries across four sites — the
label dict, the dispatch table, a callback in ``data.py``, and the menu entry.
Missing one path silently degrades the dialog to "No options" with no error.
These tests pin the four-way integrity.
"""

import pytest

from bonsai.bim.module.clip_box import data, operator, ui

pytestmark = pytest.mark.clip_box


def test_every_label_has_a_dispatch_entry():
    missing = set(operator.SOURCE_KIND_LABELS) - set(operator._SOURCE_ID_DISPATCH)
    assert not missing, f"Kinds missing from dispatch: {sorted(missing)}"


def test_every_dispatch_value_is_callable():
    for kind, fn in operator._SOURCE_ID_DISPATCH.items():
        assert callable(fn), f"Dispatch entry for {kind} is not callable"


def test_every_dispatch_target_lives_in_data_module():
    # Each callback must be a real attribute of the data module; protects
    # against typos in the dispatch table that would otherwise only surface
    # at the first dialog open.
    for kind, fn in operator._SOURCE_ID_DISPATCH.items():
        assert (
            getattr(data, fn.__name__, None) is fn
        ), f"Dispatch target for {kind} ({fn.__name__}) is not exported from data.py"


def test_every_menu_entry_is_a_known_kind():
    for kind, label, icon in ui._SOURCE_MENU_ENTRIES:
        assert kind in operator.SOURCE_KIND_LABELS, f"Menu kind {kind!r} (label={label!r}) is not in SOURCE_KIND_LABELS"


def test_every_label_has_a_menu_entry():
    menu_kinds = {kind for kind, _label, _icon in ui._SOURCE_MENU_ENTRIES}
    missing = set(operator.SOURCE_KIND_LABELS) - menu_kinds
    assert not missing, f"Kinds missing from menu: {sorted(missing)}"


def test_status_values_match_between_tool_and_data():
    # The status picker labels in data.STATUS_LABELS and the tool-layer
    # validation list must agree — the dispatcher rejects any status value
    # missing from the latter.
    from bonsai.tool.clip_box import SOURCE_STATUS_VALUES

    data_values = tuple(value for value, _label in data.STATUS_LABELS)
    assert data_values == SOURCE_STATUS_VALUES
