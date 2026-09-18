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

"""Guard against a zero drawing camera Width/Height (seen while triaging #9031).

``BIMCameraProperties.get_scale_and_aspect_ratio`` divides by ``self.height``,
and that division is reachable both from ``width``/``height``'s own ``update=``
callback and from ``depsgraph_update_pre_handler`` (drawing/handler.py). Those
fields had no ``min``, so a stored zero raised an unhandled
``ZeroDivisionError`` on the value change and then again on every depsgraph
update for the rest of the session.

``min=0.01`` makes Blender's RNA layer clamp the value before it is stored,
whether it comes from a UI drag, a redo, or a direct ``props.width = 0``.

This is not the cause of the native EXCEPTION_ACCESS_VIOLATION reported in
#9031. That crash is a use after free of the Camera data-block that this
property group lives on: ``bim.update_representation`` on a drawing camera
replaces ``obj.data`` (``tool/geometry.py`` ``change_data`` ->
``delete_data`` -> ``bpy.data.cameras.remove``). Adding ``min=`` does not
change that, and measurement confirms it does not change the crash rate.
"""

import types
from types import SimpleNamespace

import bpy
import pytest

from bonsai.bim.module.drawing.prop import BIMCameraProperties

pytestmark = pytest.mark.drawing


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def test_zero_height_breaks_the_aspect_ratio_division():
    """Documents the underlying hazard: the division itself has no guard,
    so it is load-bearing that width/height can never reach zero."""
    fake_self = SimpleNamespace(width=50.0, height=0.0)
    with pytest.raises(ZeroDivisionError):
        BIMCameraProperties.get_scale_and_aspect_ratio(fake_self)


def test_camera_width_property_has_positive_min():
    keywords = BIMCameraProperties.__annotations__["width"].keywords
    assert keywords.get("min", 0) > 0


def test_camera_height_property_has_positive_min():
    keywords = BIMCameraProperties.__annotations__["height"].keywords
    assert keywords.get("min", 0) > 0


def test_dragging_height_to_zero_clamps_instead_of_dividing_by_zero():
    """End-to-end: register the real property definitions and simulate the
    UI drag (a direct RNA assignment of 0.0, exactly like ``apply_but_funcs_after``
    applies a dragged value) and prove the stored value never reaches zero,
    so the update callback's division never sees a zero denominator."""

    class _CameraPropsHarness(bpy.types.PropertyGroup):
        __annotations__ = {
            "width": BIMCameraProperties.__annotations__["width"],
            "height": BIMCameraProperties.__annotations__["height"],
        }

    bpy.utils.register_class(_CameraPropsHarness)
    bpy.types.Scene.bimvoice_test_9031_camera_props = bpy.props.PointerProperty(type=_CameraPropsHarness)
    try:
        scene = bpy.context.scene
        props = scene.bimvoice_test_9031_camera_props
        props.width = 50.0
        props.height = 50.0

        # Simulate dragging Height down to (and through) zero.
        props.height = 0.0
        assert props.height > 0, "height reached zero despite the RNA min= clamp"

        # Simulate dragging Width to a negative value.
        props.width = -100.0
        assert props.width > 0, "width went negative despite the RNA min= clamp"

        # With both clamped, the division that used to crash is now always safe.
        BIMCameraProperties.get_scale_and_aspect_ratio(props)
    finally:
        del bpy.types.Scene.bimvoice_test_9031_camera_props
        bpy.utils.unregister_class(_CameraPropsHarness)
