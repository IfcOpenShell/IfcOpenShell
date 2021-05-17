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
