"""Viewport decorations"""
from bpy.types import SpaceView3D
import bpy
import blf


class ViewDecorator(object):
    # class var for single handler
    installed = None

    @classmethod
    def install(cls, *args, **kwargs):
        handler = cls(*args, **kwargs)
        cls.installed = SpaceView3D.draw_handler_add(handler, (), 'WINDOW', 'POST_PIXEL')

    @classmethod
    def uninstall(cls):
        SpaceView3D.draw_handler_remove(cls.installed, 'WINDOW')
        cls.installed = None


class DimensionDecorator(ViewDecorator):
    """Decorates dimension curves
    - outlines each segment with an arrow
    - puts metric text next to each segment
    """

    def __init__(self, scene, context):
        self.scene = scene
        self.context = context
        self.font_id = 0
        self.dpi = context.preferences.system.dpi
        print("Created decorator", scene)

    def __call__(self):
        # get active drawing, if any
        if self.scene.active_drawing_index is None or len(self.scene.drawings) == 0:
            return
        drawing = self.scene.drawings[self.scene.active_drawing_index]
        collection = bpy.data.collections.get("IfcGroup/" + drawing.name)
        if 'IfcAnnotation/Dimension' not in collection.all_objects:
            return
        curve = collection.all_objects['IfcAnnotation/Dimension'].data
        text = repr(curve)
        blf.position(self.font_id, 100, 100, 0)
        blf.size(self.font_id, 10, self.dpi)
        blf.draw(self.font_id, text)
