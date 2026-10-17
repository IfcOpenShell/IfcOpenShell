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

"""Regression tests for #9006's second traceback: the ``exit_edit_mode_callback``
functions wired into ``ProfileDecorator.install()`` crashed when the decorator
invoked them with no active object.

``ProfileDecorator.__call__`` (``bonsai/bim/module/model/decorator.py``) is a
per-frame ``SpaceView3D`` draw handler. Since commit ``1961cd905ee`` (2026-05-28,
"Fix parametric framework live-session regressions"), it treats
``context.active_object is None`` the same as "no longer in edit mode": it
uninstalls itself and fires ``exit_edit_mode_callback()`` -- see decorator.py:167.

That guard was only added to the decorator's own ``obj.mode`` read (which
used to crash outright on ``None``). The four callbacks it can invoke were
never updated to expect ``obj`` to be ``None``:

- ``slab.disable_editing_extrusion_profile``
- ``profile.disable_editing_extrusion_axis``

Both called ``bpy.ops.object.mode_set(mode="OBJECT")`` unconditionally before
even reading ``context.active_object``. ``mode_set``'s poll() requires an
active object, so this raised ``RuntimeError: ... Context missing active
object`` -- the exact second traceback attached to #9006 (from
``slab.disable_editing_extrusion_profile``, reached via the door-type-with-no-profile
repro: the polyline draw operator has no active object at all, so the decorator's
guard fires the callback with ``obj=None``).

- ``railing.cancel_editing_railing_path``
- ``roof.cancel_editing_roof_path``

Both instead ``assert obj`` before doing anything else, so they crashed with
``AssertionError`` in the same scenario -- less alarming in the log than an
operator RuntimeError, but still an unhandled exception raised from a draw
handler.

All four now guard ``obj is None`` and return ``{"CANCELLED"}`` instead of
touching ``bpy.ops.object.mode_set`` or any per-object state."""

import bpy
import pytest

import bonsai.bim.module.model.profile as profile
import bonsai.bim.module.model.railing as railing
import bonsai.bim.module.model.roof as roof
import bonsai.bim.module.model.slab as slab

pytestmark = pytest.mark.model


@pytest.fixture
def no_active_object():
    """Clear Blender's active object for the test body, reproducing the state
    ``ProfileDecorator.__call__`` detects right before it fires
    ``exit_edit_mode_callback()`` with no object to hand it. Restores whatever
    was active afterwards so this doesn't leak into other tests."""
    previous = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = None
    assert bpy.context.active_object is None
    try:
        yield
    finally:
        bpy.context.view_layer.objects.active = previous


def test_disable_editing_extrusion_profile_no_active_object(no_active_object):
    """slab.py -- the exact crash site quoted in #9006's second traceback."""
    assert slab.disable_editing_extrusion_profile(bpy.context) == {"CANCELLED"}


def test_disable_editing_extrusion_axis_no_active_object(no_active_object):
    """profile.py -- identical unguarded mode_set pattern."""
    assert profile.disable_editing_extrusion_axis(bpy.context) == {"CANCELLED"}


def test_cancel_editing_railing_path_no_active_object(no_active_object):
    """railing.py -- crashed with AssertionError instead of RuntimeError."""
    assert railing.cancel_editing_railing_path(bpy.context) == {"CANCELLED"}


def test_cancel_editing_roof_path_no_active_object(no_active_object):
    """roof.py -- crashed with AssertionError instead of RuntimeError."""
    assert roof.cancel_editing_roof_path(bpy.context) == {"CANCELLED"}
