# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import bonsai.bim.module.drawing.decoration as decoration
import bonsai.tool as tool
from bpy.app.handlers import persistent


@persistent
def load_post(*args):
    if bpy.context.scene.DocProperties.should_draw_decorations:
        decoration.DecorationsHandler.install(bpy.context)
    else:
        decoration.DecorationsHandler.uninstall()


@persistent
def depsgraph_update_pre_handler(scene):
    set_active_camera_resolution(scene)


def set_active_camera_resolution(scene):
    if not scene.camera or "/" not in scene.camera.name or not scene.DocProperties.drawings:
        return
    props = scene.camera.data.BIMCameraProperties
    ortho_scale = max((props.width, props.height))
    aspect_ratio = props.width / props.height
    if (scene.camera.data.ortho_scale != ortho_scale) or (
        scene.render.resolution_x / scene.render.resolution_y != aspect_ratio
    ):
        scene.camera.data.ortho_scale = ortho_scale

        diagram_scale = tool.Drawing.get_diagram_scale(scene.camera)
        scale_ratio = tool.Drawing.get_scale_ratio(diagram_scale["Scale"])

        if props.width > props.height:
            aspect_ratio = props.height / props.width
            raster_x = ortho_scale * scale_ratio * props.dpi / 0.0254
            raster_y = ortho_scale * aspect_ratio * scale_ratio * props.dpi / 0.0254
        else:
            aspect_ratio = props.width / props.height
            raster_x = ortho_scale * aspect_ratio * scale_ratio * props.dpi / 0.0254
            raster_y = ortho_scale * scale_ratio * props.dpi / 0.0254

        scene.render.resolution_x = scene.camera.data.BIMCameraProperties.raster_x = int(raster_x)
        scene.render.resolution_y = scene.camera.data.BIMCameraProperties.raster_y = int(raster_y)

    current_drawing = scene.DocProperties.drawings[scene.DocProperties.current_drawing_index]
