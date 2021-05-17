import bpy
import blenderbim.bim.module.drawing.decoration as decoration
from bpy.app.handlers import persistent


@persistent
def toggleDecorationsOnLoad(*args):
    toggle = bpy.context.scene.DocProperties.should_draw_decorations
    if toggle:
        decoration.DecorationsHandler.install(bpy.context)
    else:
        decoration.DecorationsHandler.uninstall()


@persistent
def depsgraph_update_pre_handler(scene):
    set_active_camera_resolution(scene)


def set_active_camera_resolution(scene):
    if not scene.camera or "/" not in scene.camera.name or not scene.DocProperties.drawings:
        return
    if (
        scene.render.resolution_x != scene.camera.data.BIMCameraProperties.raster_x
        or scene.render.resolution_y != scene.camera.data.BIMCameraProperties.raster_y
    ):
        scene.render.resolution_x = scene.camera.data.BIMCameraProperties.raster_x
        scene.render.resolution_y = scene.camera.data.BIMCameraProperties.raster_y
    current_drawing = scene.DocProperties.drawings[scene.DocProperties.current_drawing_index]
    if scene.camera != current_drawing.camera:
        scene.DocProperties.current_drawing_index = scene.DocProperties.drawings.find(scene.camera.name.split("/")[1])
        bpy.ops.bim.activate_view(drawing_index=scene.DocProperties.current_drawing_index)
