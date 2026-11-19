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

import types
from unittest.mock import MagicMock, patch

import bpy
import ifcopenshell
import pytest

import bonsai.tool as tool
from bonsai.bim.module.drawing.operator import ActivateDrawingStyle
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.drawing


class TestActivateDrawingStyle(NewFile):
    def test_poll_returns_false_without_active_drawing(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        cam_data = bpy.data.cameras.new("TestCam")
        cam_obj = bpy.data.objects.new("TestCam", cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        bpy.context.scene.camera = cam_obj

        assert tool.Drawing.get_document_props().get_active_drawing() is None
        assert ActivateDrawingStyle.poll(bpy.context) is False

    def test_execute_cancels_gracefully_without_active_drawing(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        cam_data = bpy.data.cameras.new("TestCam")
        cam_obj = bpy.data.objects.new("TestCam", cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        bpy.context.scene.camera = cam_obj

        op = ActivateDrawingStyle()
        op.report = MagicMock()
        dummy_style = types.SimpleNamespace(name="Default", raster_style="{}")

        with (
            patch.object(
                tool.Drawing,
                "get_camera_props",
                return_value=types.SimpleNamespace(get_active_drawing_style=lambda: dummy_style),
            ),
            patch.object(
                tool.Drawing,
                "get_document_props",
                return_value=types.SimpleNamespace(get_active_drawing=lambda: None),
            ),
            patch.object(op, "set_raster_style") as mock_set_raster,
        ):
            result = op._execute(bpy.context)

        assert result == {"CANCELLED"}
        mock_set_raster.assert_not_called()
        op.report.assert_called_once()
