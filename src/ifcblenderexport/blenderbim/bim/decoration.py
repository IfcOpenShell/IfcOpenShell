"""Viewport decorations"""
import math
from bpy.types import SpaceView3D
from mathutils import Vector
import bpy
import blf
from bpy_extras.view3d_utils import location_3d_to_region_2d


class ViewDecorator(object):
    # class var for single handler
    installed = None

    @classmethod
    def install(cls, *args, **kwargs):
        handler = cls(*args, **kwargs)
        cls.installed = SpaceView3D.draw_handler_add(handler, (), 'WINDOW', 'POST_PIXEL')

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, 'WINDOW')
        except ValueError:
            pass
        cls.installed = None


class DimensionDecorator(ViewDecorator):
    """Decorates dimension curves
    - outlines each segment with an arrow
    - puts metric text next to each segment
    """

    def __init__(self, props, context):
        self.context = context
        self.props = props
        self.font_id = 0  # TODO: take font from styles
        self.dpi = context.preferences.system.dpi

    def __call__(self):
        # get active drawing, if any
        if self.props.active_drawing_index is None or len(self.props.drawings) == 0:
            return
        drawing = self.props.drawings[self.props.active_drawing_index]
        collection = bpy.data.collections.get("IfcGroup/" + drawing.name)
        # get curve object
        if 'IfcAnnotation/Dimension' not in collection.all_objects:
            return
        curve = collection.all_objects['IfcAnnotation/Dimension']

        for segm in self.iter_segments(curve):
            self.draw_label(segm)
            self.draw_arrow(segm)

    def iter_segments(self, curve):
        """Yields each segment converted to world coords
        (v0, v1, length)
        """
        for spline in curve.data.splines:
            points = [curve.matrix_world @ p.co for p in spline.points]
            for i in range(len(points)-1):
                p0 = points[i]
                p1 = points[i+1]
                length = (p1 - p0).length
                yield (p0, p1, length)

    def draw_label(self, segm):
        """Draw text of segment length
        aligned and centered at segment middle
        """
        p0, p1, length = segm

        # convert to view coords
        region = self.context.region
        region3d = self.context.region_data
        p0 = location_3d_to_region_2d(region, region3d, p0)
        p1 = location_3d_to_region_2d(region, region3d, p1)

        text = f"{length:.2f}"

        ang = -Vector((1, 0)).angle_signed(p1 - p0)
        cos = math.cos(ang)
        sin = math.sin(ang)

        # midpoint
        pos = p0 + (p1 - p0) * .5

        # TODO: take font size from styles
        blf.size(self.font_id, 16, self.dpi)
        w, h = blf.dimensions(self.font_id, text)

        # align centered
        pos -= Vector((cos, sin)) * w * 0.5

        # add padding
        # TODO: take padding from styles and adjust to line width
        pos += Vector((-sin, cos)) * 4

        # TODO: handle overlapping of text with arrows for narrow segments

        blf.enable(self.font_id, blf.ROTATION)
        blf.position(self.font_id, pos.x, pos.y, 0)

        blf.rotation(self.font_id, ang)
        blf.draw(self.font_id, text)
        blf.disable(self.font_id, blf.ROTATION)

    def draw_arrow(self, segm):
        pass