# This file was generated with the assistance of an AI coding tool.
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

import bpy

import bonsai.bim.module.drawing.prop as drawing_prop
import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestUpdateWidthHeight(NewFile):
    def test_persists_a_camera_size_edit_through_a_deferred_timer(self):
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_drawing()
        camera = next(o for o in bpy.data.objects if o.type == "CAMERA")
        bpy.context.scene.camera = camera

        def get_block():
            return tool.Ifc.get_entity(camera).Representation.Representations[0].Items[0].TreeRootExpression

        width = get_block().XLength

        camera.data.BIMCameraProperties.width = width * 2

        assert get_block().XLength == width
        assert drawing_prop._pending_camera_representation_persist
        drawing_prop._pending_camera_representation_persist()
        assert get_block().XLength == width * 2
