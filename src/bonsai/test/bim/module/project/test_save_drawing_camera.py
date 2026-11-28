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

import bpy

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc


class TestSaveProjectKeepsDrawingCamera(NewIfc):
    def test_zoom_survives_saving_and_reopening(self):
        tool.Project.save_test_project()
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        drawing = tool.Ifc.get().by_type("IfcAnnotation")[0]
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        props = tool.Drawing.get_camera_props(bpy.context.scene.camera.data)
        props.width = 20.0
        props.height = 10.0
        bpy.context.view_layer.update()
        bpy.ops.bim.save_project(filepath=str(tool.Project.TEMP_PROJECT_PATH), should_save_as=True)

        bpy.ops.bim.load_project(filepath=str(tool.Project.TEMP_PROJECT_PATH))
        bpy.ops.bim.load_drawings()
        drawing = tool.Ifc.get().by_type("IfcAnnotation")[0]
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        props = tool.Drawing.get_camera_props(bpy.context.scene.camera.data)
        assert (props.width, props.height) == (20.0, 10.0)
