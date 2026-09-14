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

"""Regression test for #9270: saving only the .blend file silently drops
unsaved IFC edits the next time the file is reopened, because Bonsai keeps
IFC edits in memory until "Save IFC Project" runs explicitly. This pins
``handler.has_unsaved_ifc_changes`` (the condition ``handler.save_pre``
warns on) and the popup-vs-no-popup behaviour of ``handler.save_pre``
itself."""

from unittest import mock

import pytest

pytestmark = pytest.mark.misc


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    import bpy

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def test_no_warning_when_no_ifc_loaded():
    """No IFC project open: nothing to lose, no warning."""
    from bonsai.bim import handler

    with mock.patch("bonsai.bim.handler.tool.Ifc.get", return_value=None):
        assert handler.has_unsaved_ifc_changes() is False


def test_no_warning_when_ifc_loaded_and_clean():
    """IFC loaded but nothing changed since the last "Save IFC Project"."""
    from bonsai.bim import handler

    with mock.patch("bonsai.bim.handler.tool.Ifc.get", return_value=mock.Mock()), mock.patch(
        "bonsai.bim.handler.tool.Blender.get_bim_props", return_value=mock.Mock(is_dirty=False)
    ):
        assert handler.has_unsaved_ifc_changes() is False


def test_warns_when_ifc_loaded_and_dirty():
    """The #9270 scenario: an IFC element was created/edited, and that
    edit only lives in memory. This is exactly what silently vanishes if
    the user saves the .blend and reopens without an explicit IFC save."""
    from bonsai.bim import handler

    with mock.patch("bonsai.bim.handler.tool.Ifc.get", return_value=mock.Mock()), mock.patch(
        "bonsai.bim.handler.tool.Blender.get_bim_props", return_value=mock.Mock(is_dirty=True)
    ):
        assert handler.has_unsaved_ifc_changes() is True


def test_save_pre_pops_up_warning_when_dirty():
    """``save_pre`` is the ``bpy.app.handlers.save_pre`` hook: it must pop
    up a warning when there are unsaved IFC changes and a window exists
    (interactive Ctrl+S), so the user is not silently left to lose data."""
    from bonsai.bim import handler

    fake_window_manager = mock.Mock()
    with mock.patch("bonsai.bim.handler.has_unsaved_ifc_changes", return_value=True), mock.patch(
        "bonsai.bim.handler.bpy.context", window=mock.Mock(), window_manager=fake_window_manager
    ):
        handler.save_pre(None)

    assert fake_window_manager.popup_menu.call_count == 1
    _, kwargs = fake_window_manager.popup_menu.call_args
    assert kwargs.get("icon") == "ERROR"


def test_save_pre_does_not_pop_up_when_clean():
    """Symmetric case: nothing unsaved, no popup."""
    from bonsai.bim import handler

    fake_window_manager = mock.Mock()
    with mock.patch("bonsai.bim.handler.has_unsaved_ifc_changes", return_value=False), mock.patch(
        "bonsai.bim.handler.bpy.context", window=mock.Mock(), window_manager=fake_window_manager
    ):
        handler.save_pre(None)

    assert fake_window_manager.popup_menu.call_count == 0


def test_save_pre_skips_popup_without_a_window():
    """Background/headless saves (no window) must not try to pop up UI."""
    from bonsai.bim import handler

    fake_window_manager = mock.Mock()
    with mock.patch("bonsai.bim.handler.has_unsaved_ifc_changes", return_value=True), mock.patch(
        "bonsai.bim.handler.bpy.context", window=None, window_manager=fake_window_manager
    ):
        handler.save_pre(None)

    assert fake_window_manager.popup_menu.call_count == 0
