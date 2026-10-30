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

import types

import bpy
import pytest

from bonsai.bim.module.drawing.prop import BIMCameraProperties

pytestmark = pytest.mark.drawing


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def test_dragging_height_to_zero_clamps_instead_of_dividing_by_zero():
    class _CameraPropsHarness(bpy.types.PropertyGroup):
        __annotations__ = {
            "width": BIMCameraProperties.__annotations__["width"],
            "height": BIMCameraProperties.__annotations__["height"],
        }

    bpy.utils.register_class(_CameraPropsHarness)
    bpy.types.Scene.bimvoice_test_9031_camera_props = bpy.props.PointerProperty(type=_CameraPropsHarness)
    try:
        props = bpy.context.scene.bimvoice_test_9031_camera_props
        props.width = 50.0
        props.height = 50.0
        props.height = 0.0
        assert props.height > 0
        props.width = -100.0
        assert props.width > 0
        BIMCameraProperties.get_scale_and_aspect_ratio(props)
    finally:
        del bpy.types.Scene.bimvoice_test_9031_camera_props
        bpy.utils.unregister_class(_CameraPropsHarness)
