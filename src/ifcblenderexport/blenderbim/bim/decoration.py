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


class Shaders:
    pass


class BaseDecorator():
    # base name of objects to decorate
    basename = "IfcAnnotation/Something"

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
    layout(line_strip, max_vertices=2) out;

    void main() {
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        gl_Position = p0;
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

    def __init__(self, props, context):
        self.context = context
        self.props = props
        self.shader = self.create_shader()

    @classmethod
    def create_shader(cls):
        return GPUShader(vertexcode=cls.VERT_GLSL, fragcode=cls.FRAG_GLSL, geocode=cls.GEOM_GLSL)

    def __call__(self):
        # get active drawing, if any
        if self.props.active_drawing_index is None or len(self.props.drawings) == 0:
            return

        objects = list(self.get_objects())
        if not objects:
            return

        self.decorate(objects)

    def get_objects(self):
        """find relevant objects
        using class.basename

        returns: iterable of blender objects
        """
        drawing = self.props.drawings[self.props.active_drawing_index]
        collection = bpy.data.collections.get("IfcGroup/" + drawing.name)
        return filter(lambda o: self.basename in o.name, collection.objects)

    def decorate(self, objects):
        """perform actuall drawing stuff"""
        raise NotImplementedError()

    def flat_points(self, segments):
        """flatten segments into list of their points
        returns: iterable of points as coords tuples
        """
        def coords(v):
            return tuple(v)[:3]
        return reduce(lambda points, segm: points + [coords(segm[0]), coords(segm[1])], segments, [])


class PathDecorator:
    def get_segments(self, object):
        """extract segments from curve object"""
        for spline in object.data.splines:
            spline_points = spline.bezier_points if spline.bezier_points else spline.points
            points = [object.matrix_world @ p.co for p in spline_points]
            for i in range(len(points)-1):
                p0 = points[i]
                p1 = points[i+1]
                yield (p0, p1)


class MeshDecorator:
    def get_segments(self, object):
        """extract segments from mesh object"""
        for edge in object.data.edges:
            p0 = object.data.vertices[edge.vertices[0]].co
            p1 = object.data.vertices[edge.vertices[1]].co
            yield (p0, p1)


class DimensionDecorator(PathDecorator, BaseDecorator):
    """Decorator for dimension objects
    - outlines each segment
    - augments with arrows on both sides
    - puts metric text next to each segment
    """
    basename = "IfcAnnotation/Dimension"
    installed = None

    GEOM_GLSL = """
    layout(lines) in;
    layout(line_strip, max_vertices=10) out;

    uniform float windowW;
    uniform float windowH;
    uniform float arrow_length;
    uniform float arrow_angle;

    void arrow_head(in vec2 p0, in vec2 p1, out vec2 head[3]) {
        vec2 nose = normalize(p1 - p0) * arrow_length;
        float c = cos(arrow_angle), s = sin(arrow_angle);
        head[0] = nose;
        head[1] = mat2( c, -s, +s, c) * nose;
        head[2] = mat2( c, +s, -s, c) * nose;
    }

    void main() {
        /** generates arrows from lines */
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        // converting NDC to/from window coords
        float hw = windowW/2, hh= windowH/2;
        mat4 windowMatrix = mat4(hw, 0, 0, 0,   0, hh, 0, 0,   0, 0, 1, 0,   0, 0, 0, 1);
        mat4 unwindowMatrix = inverse(windowMatrix);

        vec2 head[3];
        vec4 head_ndc[3];

        vec4 p0w = windowMatrix * (p0 / p0.w), p1w = windowMatrix * (p1 / p1.w);
        arrow_head(p0w.xy, p1w.xy, head);
        for(int i=0; i<3; i++) head_ndc[i] = unwindowMatrix * vec4(head[i], 0, 0);

        gl_Position = p0 + head_ndc[0] * p0.w;
        EmitVertex();
        gl_Position = p1 - head_ndc[0] * p1.w;
        EmitVertex();
        EndPrimitive();

        gl_Position = p0;
        EmitVertex();
        gl_Position = p0 + head_ndc[1] * p0.w;
        EmitVertex();
        gl_Position = p0 + head_ndc[2] * p0.w;
        EmitVertex();
        gl_Position = p0;
        EmitVertex();
        EndPrimitive();

        gl_Position = p1;
        EmitVertex();
        gl_Position = p1 - head_ndc[1] * p1.w;
        EmitVertex();
        gl_Position = p1 - head_ndc[2] * p1.w;
        EmitVertex();
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def __init__(self, props, context):
        super().__init__(props, context)
        self.font_id = 0
        self.dpi = context.preferences.system.dpi

    def decorate(self, objects):
        segments = list(chain.from_iterable(self.get_segments(obj) for obj in objects))
        if not segments:
            return

        for segm in segments:
            length = (segm[1] - segm[0]).length
            text = f"{length:.2f}"
            self.draw_label(segm, text)

        self.draw_arrows(segments)

    def draw_label(self, segm, text):
        """Draw text of segment length
        aligned and centered at segment middle
        """
        p0, p1 = segm

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
        region = self.context.region
        region3d = self.context.region_data
        points = self.flat_points(segments)

        batch = batch_for_shader(self.shader, 'LINES', {'pos': points})
        self.shader.bind()
        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float("windowW", region.width)
        self.shader.uniform_float("windowH", region.height)
        # # TODO: get everything from styles
        self.shader.uniform_float('color', (1.0, 1.0, 1.0))
        self.shader.uniform_float('arrow_angle', math.pi / 12)
        self.shader.uniform_float('arrow_length', 16)
        batch.draw(self.shader)


class EqualityDecorator(DimensionDecorator):
    """Decorator for equality objects
    - outlines each segment
    - augments with arrows on both sides
    - puts 'EQ' label
    """
    basename = "IfcAnnotation/Equal"
    installed = None

    def decorate(self, objects):
        segments = list(chain.from_iterable(self.get_segments(obj) for obj in objects))
        if not segments:
            return

        for segm in segments:
            self.draw_label(segm, 'EQ')

        self.draw_arrows(segments)


class LeaderDecorator(PathDecorator, BaseDecorator):
    basename = "IfcAnnotation/Leader"
    installed = None

    def decorate(self, objects):
        segments = list(chain.from_iterable(self.get_segments(obj) for obj in objects))
        if not segments:
            return

        region3d = self.context.region_data
        points = self.flat_points(segments)
        batch = batch_for_shader(self.shader, 'LINES', {'pos': points})
        self.shader.bind()
        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float('color', (1.0, 1.0, 1.0))
        batch.draw(self.shader)


class StairDecorator(PathDecorator, BaseDecorator):
    basename = "IfcAnnotation/Stair"
    installed = None

    def decorate(self, objects):
        segments = list(chain.from_iterable(self.get_segments(obj) for obj in objects))
        if not segments:
            return

        region3d = self.context.region_data
        points = self.flat_points(segments)
        batch = batch_for_shader(self.shader, 'LINES', {'pos': points})
        self.shader.bind()
        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float('color', (1.0, 1.0, 1.0))
        batch.draw(self.shader)


class HiddenDecorator(MeshDecorator, BaseDecorator):
    basename = "IfcAnnotation/Hidden"
    installed = None

    def decorate(self, objects):
        segments = list(chain.from_iterable(self.get_segments(obj) for obj in objects))
        if not segments:
            return

        region3d = self.context.region_data
        points = self.flat_points(segments)
        batch = batch_for_shader(self.shader, 'LINES', {'pos': points})
        self.shader.bind()
        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float('color', (1.0, 1.0, 1.0))
        batch.draw(self.shader)
