"""Viewport decorations"""
import math
from functools import reduce
from itertools import chain

from bpy.types import SpaceView3D
from mathutils import Vector, Matrix
import bpy
import blf
from bpy_extras.view3d_utils import location_3d_to_region_2d
import gpu
import bgl
from gpu.types import GPUShader, GPUBatch, GPUIndexBuf, GPUVertBuf, GPUVertFormat
from gpu_extras.batch import batch_for_shader


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

    VERT_GLSL = """
    uniform mat4 viewMatrix;
    in vec3 pos;
    out vec4 gl_Position;

    void main() {
        gl_Position = viewMatrix * vec4(pos, 1.0);
    }
    """
    GEOM_GLSL = """
    layout(lines) in;
    layout(line_strip, max_vertices=10) out;

    uniform float windowW;
    uniform float windowH;
    uniform float angle;
    uniform float length;
    uniform float aspect;

    void main() {
        /** generates arrows from lines */

        // converting NDC to/from window coords
        float hw = windowW/2, hh= windowH/2;
        mat4 windowMatrix = mat4(hw, 0, 0, 0,   0, hh, 0, 0,   0, 0, 1, 0,   0, 0, 0, 1);
        mat4 unwindowMatrix = inverse(windowMatrix);

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = windowMatrix * (p0 / p0.w), p1w = windowMatrix * (p1 / p1.w);

        // arrow head of specified length in direction of a segment
        // rotating the head left/right to form triangle
        vec4 head = normalize(p1w - p0w) * length;
        float c = cos(angle), s = sin(angle);
        vec4 head_a = mat4( c, -s, 0, 0,  +s, c, 0, 0,  0, 0, 1, 0,  0, 0, 0, 1) * head;
        vec4 head_b = mat4( c, +s, 0, 0,  -s, c, 0, 0,  0, 0, 1, 0,  0, 0, 0, 1) * head;

        // projecting back to NDC
        vec4 head_ndc = unwindowMatrix * head;
        vec4 head_a_ndc = unwindowMatrix * head_a;
        vec4 head_b_ndc = unwindowMatrix * head_b;

        gl_Position = p0 + head_ndc * p0.w;
        EmitVertex();
        gl_Position = p1 - head_ndc * p1.w;
        EmitVertex();
        EndPrimitive();

        gl_Position = p0;
        EmitVertex();
        gl_Position = p0 + head_a_ndc * p0.w;
        EmitVertex();
        gl_Position = p0 + head_b_ndc * p0.w;
        EmitVertex();
        gl_Position = p0;
        EmitVertex();
        EndPrimitive();

        gl_Position = p1;
        EmitVertex();
        gl_Position = p1 - head_b_ndc * p1.w;
        EmitVertex();
        gl_Position = p1 - head_a_ndc * p1.w;
        EmitVertex();
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();
    }
    """
    FRAG_GLSL = """
    uniform vec3 color;
    out vec4 fragColor;

    void main() {
        fragColor = vec4(color, 1.0);
    }
    """

    def __init__(self, props, context):
        self.context = context
        self.props = props
        self.font_id = 0  # TODO: take font from styles
        self.dpi = context.preferences.system.dpi
        self.shader = self.create_shader()

    @classmethod
    def create_shader(cls):
        return GPUShader(vertexcode=cls.VERT_GLSL, fragcode=cls.FRAG_GLSL, geocode=cls.GEOM_GLSL)

    def __call__(self):
        # get active drawing, if any
        if self.props.active_drawing_index is None or len(self.props.drawings) == 0:
            return
        drawing = self.props.drawings[self.props.active_drawing_index]
        collection = bpy.data.collections.get("IfcGroup/" + drawing.name)

        segments = self.get_segments(self.get_curves(collection, "IfcAnnotation/Dimension"))

        self.draw_arrows(segments)
        for segm in segments:
            self.draw_label(segm, f"{segm[2]:.2f}")

        # segments = self.get_segments(self.get_curves(collection, "IfcAnnotation/Equal"))

        # self.draw_arrows(segments)
        # for segm in segments:
        #     self.draw_label(segm, "EQ")

    def get_curves(self, collection, basename):
        return list(filter(lambda o: basename in o.name, collection.objects))

    def get_segments(self, curves):
        return list(chain.from_iterable(self.iter_segments(curve) for curve in curves))

    def iter_segments(self, curve):
        """Yields each segment converted to world coords
        (v0, v1, length)
        """
        for spline in curve.data.splines:
            spline_points = spline.bezier_points if spline.bezier_points else spline.points
            points = [curve.matrix_world @ p.co for p in spline_points]
            for i in range(len(points)-1):
                p0 = points[i]
                p1 = points[i+1]
                length = (p1 - p0).length
                yield (p0, p1, length)

    def draw_label(self, segm, text):
        """Draw text of segment length
        aligned and centered at segment middle
        """
        p0, p1, _ = segm

        # convert to view coords
        region = self.context.region
        region3d = self.context.region_data
        p0 = location_3d_to_region_2d(region, region3d, p0)
        p1 = location_3d_to_region_2d(region, region3d, p1)
        proj = p1 - p0

        if proj.length < 0.001:
            return

        ang = -Vector((1, 0)).angle_signed(proj)
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

    def draw_arrows(self, segments):
        def coords(segm):
            return [(segm[0].x, segm[0].y, segm[0].z),
                    (segm[1].x, segm[1].y, segm[1].z)]
        points = list(reduce(lambda points, segm: points + coords(segm),
                             segments, []))
        batch = batch_for_shader(self.shader, 'LINES', {'pos': points})
        self.shader.bind()

        region = self.context.region
        region3d = self.context.region_data

        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float("windowW", region.width)
        self.shader.uniform_float("windowH", region.height)

        # TODO: get everything from styles
        self.shader.uniform_float('color', (1.0, 1.0, 1.0))
        self.shader.uniform_float('angle', math.pi / 12)
        self.shader.uniform_float('length', 16)
        batch.draw(self.shader)
