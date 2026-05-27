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

"""Addon-load smoke for ``bonsai``.

Pins the registration/unregistration cycle as a runnable contract. The cycle
exercises every ``register()`` site across ``bim/__init__.py``'s modules dict,
every ``PointerProperty`` attachment, every gizmo-prefs auto-registration, and
every ``bpy.app.handlers`` install. A regression in any of those surfaces here
as an exception with a traceback that points at the failing site, instead of
the silent ``addon failed to enable`` users see in a fresh Blender."""

import types

import bpy
import pytest

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def test_addon_unregister_then_register_does_not_raise():
    """Running the suite has already enabled the addon. Cycle through one
    unregister + register to exercise both halves, then leave the addon
    enabled so downstream tests in the same Blender session keep working."""
    import bonsai

    bonsai.unregister()
    try:
        bonsai.register()
    except Exception:
        # Re-raise after attempting to leave the session in a usable state for
        # any tests that run after this one.
        try:
            bonsai.register()
        except Exception:
            pass
        raise
