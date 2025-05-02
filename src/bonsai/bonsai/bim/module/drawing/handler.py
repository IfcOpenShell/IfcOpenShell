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
    props = tool.Drawing.get_document_props()
    if props.should_draw_decorations:
        decoration.DecorationsHandler.install(bpy.context)
    else:
        decoration.DecorationsHandler.uninstall()


@persistent
def depsgraph_update_pre_handler(scene):
    set_active_camera_resolution(scene)


def set_active_camera_resolution(scene: bpy.types.Scene) -> None:
    """Sync scene render resolution with the active drawing
    and prevent user from manually changing ``ortho_scale`` on IFC camera."""
    props = tool.Drawing.get_document_props()
    camera_obj = scene.camera
    if not camera_obj or "/" not in camera_obj.name or not props.drawings:
        return
    assert isinstance((camera := camera_obj.data), bpy.types.Camera)
    props = tool.Drawing.get_camera_props(camera)
    ortho_scale, aspect_ratio = props.get_scale_and_aspect_ratio()
    scene_render = scene.render
    if (camera.ortho_scale != ortho_scale) or not tool.Cad.is_x(
        scene_render.resolution_x / scene_render.resolution_y, aspect_ratio
    ):
        raster_x, raster_y = props.update_camera_resolution()
        scene_render.resolution_x = raster_x
        scene_render.resolution_y = raster_y
