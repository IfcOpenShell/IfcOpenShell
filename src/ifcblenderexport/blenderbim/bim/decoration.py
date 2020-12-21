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
    in uint style;
    out vec4 gl_Position;
    out uint vstyle;

    void main() {
        gl_Position = viewMatrix * vec4(pos, 1.0);
        vstyle = style;
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
    out vec4 fragColor;

    void main() {
        fragColor = vec4(1.0, 1.0, 1.0, 1.0);
    }
    """

    LIB_GLSL = """
    void arrow_head(in vec2 p0, in vec2 p1, out vec2 head[3]) {
        vec2 nose = normalize(p1 - p0) * ARROW_SIZE;
        float c = cos(ARROW_ANGLE), s = sin(ARROW_ANGLE);
        head[0] = nose;
        head[1] = mat2(c, -s, +s, c) * nose;
        head[2] = mat2(c, +s, -s, c) * nose;
    }

    void circle_head(in vec2 p0, in vec2 p1, out vec2 head[CIRCLE_SEGS]) {
        float angle_d = PI * 2 / CIRCLE_SEGS;
        for(int i = 0; i<CIRCLE_SEGS; i++) {
            float angle = angle_d * i;
            head[i] = vec2(cos(angle), sin(angle)) * CIRCLE_SIZE;
        }
    }
    """

    DEF_GLSL = """
        #define PI 3.141592653589793
        #define CIRCLE_SEGS 24
        // max points = SEGS (circle) + 2 (stem) + 3 (arrow)
        #define MAX_POINTS 29
        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 16.0
        #define CIRCLE_SIZE 8.0
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
        # NB: libcode param doesn't work
        return GPUShader(vertexcode=cls.VERT_GLSL,
                         fragcode=cls.FRAG_GLSL,
                         geocode=cls.LIB_GLSL + cls.GEOM_GLSL,
                         defines=cls.DEF_GLSL)

    def __call__(self):
        if self.props.active_drawing_index is None or len(self.props.drawings) == 0:
            return

        for obj in self.get_objects():
            self.decorate(obj)

    def get_objects(self):
        """find relevant objects
        using class.basename

        returns: iterable of blender objects
        """
        drawing = self.props.drawings[self.props.active_drawing_index]
        collection = bpy.data.collections.get("IfcGroup/" + drawing.name)
        return filter(lambda o: self.basename in o.name, collection.objects)

    def get_path_geom(self, obj):
        """parse path geometry into line segments
        returns:
        - vertices: 3-tuples of coords
        - indices: 2-tuples of each segment verices' indices
        - styles: 0=internal, 1=beginning, 2=ending
        """
        vertices = []
        indices = []
        styles = []

        idx = 0
        for spline in obj.data.splines:
            spline_points = spline.bezier_points if spline.bezier_points else spline.points
            points = [obj.matrix_world @ p.co for p in spline_points]
            cnt = len(points)
            vertices.extend(p[:3] for p in points)
            styles.append(1)
            styles.extend([0] * max(0, cnt - 2))
            styles.append(2)
            indices.extend((idx+i, idx+i+1) for i in range(cnt-1))
            idx += cnt

        return vertices, indices, styles

    def get_mesh_geom(self, obj):
        """parse mesh geometry into line segments
        returns:
        - vertices: 3-tuples of coords
        - indices: 2-tuples of each segment verices' indices
        - styles: 0=internal, 1=beginning, 2=ending
        """
        pass

    def decorate(self, object):
        """perform actuall drawing stuff"""
        raise NotImplementedError()

    def draw_lines(self, obj, geom):
        region = self.context.region
        region3d = self.context.region_data

        vertices, indices, styles = geom

        fmt = GPUVertFormat()
        fmt.attr_add(id="pos", comp_type='F32', len=3, fetch_mode='FLOAT')

        vbo = GPUVertBuf(len=len(vertices), format=fmt)
        vbo.attr_fill(id="pos", data=vertices)

        ibo = GPUIndexBuf(type='LINES', seq=indices)

        batch = GPUBatch(type='LINES', buf=vbo, elem=ibo)

        self.shader.bind()
        self.shader.uniform_float
        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float("windowW", region.width)
        self.shader.uniform_float("windowH", region.height)
        batch.draw(self.shader)

    def draw_lines_styled(self, obj, geom):
        region = self.context.region
        region3d = self.context.region_data

        vertices, indices, styles = geom

        fmt = GPUVertFormat()
        fmt.attr_add(id="pos", comp_type='F32', len=3, fetch_mode='FLOAT')
        fmt.attr_add(id="style", comp_type='U8', len=1, fetch_mode='INT')

        vbo = GPUVertBuf(len=len(vertices), format=fmt)
        vbo.attr_fill(id="pos", data=vertices)
        vbo.attr_fill(id="style", data=styles)

        ibo = GPUIndexBuf(type='LINES', seq=indices)

        batch = GPUBatch(type='LINES', buf=vbo, elem=ibo)

        self.shader.bind()
        self.shader.uniform_float
        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float("windowW", region.width)
        self.shader.uniform_float("windowH", region.height)
        batch.draw(self.shader)


class DimensionDecorator(BaseDecorator):
    """Decorator for dimension objects
    - each edge of a segment with arrow
    - puts metric text next to each segment
    """
    basename = "IfcAnnotation/Dimension"
    installed = None
    GEOM_GLSL = """
    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    uniform float windowW;
    uniform float windowH;

    void main() {
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        // converting NDC to/from window coords
        float hw = windowW/2, hh= windowH/2;
        mat4 windowMatrix = mat4(hw, 0, 0, 0,   0, hh, 0, 0,   0, 0, 1, 0,   0, 0, 0, 1);
        mat4 unwindowMatrix = inverse(windowMatrix);
        vec2 p0w = (windowMatrix * (p0 / p0.w)).xy, p1w = (windowMatrix * (p1 / p1.w)).xy;

        vec2 head[3];
        vec4 head_ndc[3];
        arrow_head(p0w, p1w, head);
        for(int i=0; i<3; i++) head_ndc[i] = unwindowMatrix * vec4(head[i], 0, 0) * p1.w;
        vec4 nose = head_ndc[0];

        gl_Position = p0;
        EmitVertex();
        gl_Position = p0 + head_ndc[1];
        EmitVertex();
        gl_Position = p0 + head_ndc[2];
        EmitVertex();
        gl_Position = p0;
        EmitVertex();
        EndPrimitive();

        gl_Position = p1;
        EmitVertex();
        gl_Position = p1 - head_ndc[1];
        EmitVertex();
        gl_Position = p1 - head_ndc[2];
        EmitVertex();
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();

        gl_Position = p0 + nose;
        EmitVertex();
        gl_Position = p1 - nose;
        EmitVertex();
        EndPrimitive();
    }
    """

    def __init__(self, props, context):
        super().__init__(props, context)
        self.font_id = 0
        self.dpi = context.preferences.system.dpi

    def decorate(self, obj):
        geom = self.get_path_geom(obj)
        self.draw_lines(obj, geom)
        self.draw_labels(obj, geom)

    def draw_labels(self, obj, geom):
        region = self.context.region
        region3d = self.context.region_data
        vertices, indices, _ = geom
        for i0, i1 in indices:
            v0 = Vector(vertices[i0])
            v1 = Vector(vertices[i1])
            length = (v1 - v0).length
            text = f"{length:.2f}"
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            self.draw_label(p0, p1, text)

    def draw_label(self, p0, p1, text):
        """Draw text of segment length
        aligned and centered at segment middle
        """
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

        blf.enable(self.font_id, blf.ROTATION)
        blf.position(self.font_id, pos.x, pos.y, 0)

        blf.rotation(self.font_id, ang)
        blf.draw(self.font_id, text)
        blf.disable(self.font_id, blf.ROTATION)


class EqualityDecorator(DimensionDecorator):
    """Decorator for equality objects
    - outlines each segment
    - augments with arrows on both sides
    - puts 'EQ' label
    """
    basename = "IfcAnnotation/Equal"
    installed = None

    def draw_labels(self, obj, geom):
        region = self.context.region
        region3d = self.context.region_data
        vertices, indices, _ = geom
        for i0, i1 in indices:
            v0 = Vector(vertices[i0])
            v1 = Vector(vertices[i1])
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            self.draw_label(p0, p1, "EQ")


class LeaderDecorator(BaseDecorator):
    """Decorating stairs
    - head point with arrow
    - middle points w/out decorations
    """
    basename = "IfcAnnotation/Leader"
    installed = None

    GEOM_GLSL = """
    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint vstyle[];

    uniform float windowW;
    uniform float windowH;

    void main() {
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint s0 = vstyle[0], s1 = vstyle[1];

        // converting NDC to/from window coords
        float hw = windowW/2, hh= windowH/2;
        mat4 windowMatrix = mat4(hw, 0, 0, 0,   0, hh, 0, 0,   0, 0, 1, 0,   0, 0, 0, 1);
        mat4 unwindowMatrix = inverse(windowMatrix);
        vec2 p0w = (windowMatrix * (p0 / p0.w)).xy, p1w = (windowMatrix * (p1 / p1.w)).xy;

        vec4 nose1 = vec4(0);

        vec2 head[3];
        vec4 head_ndc[3];
        arrow_head(p0w, p1w, head);
        for(int i=0; i<3; i++) head_ndc[i] = unwindowMatrix * vec4(head[i], 0, 0) * p1.w;

        if (s1 == 2u) {
            gl_Position = p1;
            EmitVertex();
            gl_Position = p1 - head_ndc[1];
            EmitVertex();
            gl_Position = p1 - head_ndc[2];
            EmitVertex();
            gl_Position = p1;
            EmitVertex();
            EndPrimitive();

            vec2 nose = normalize(p1w - p0w) * ARROW_SIZE;
            nose1 = unwindowMatrix * vec4(nose, 0, 0) * p1.w;
        }

        gl_Position = p0;
        EmitVertex();
        gl_Position = p1 - nose1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, obj):
        geom = self.get_path_geom(obj)
        self.draw_lines_styled(obj, geom)


class StairDecorator(BaseDecorator):
    """Decorating stairs
    - head point with arrow
    - tail point with circle
    - middle points w/out decorations
    """
    basename = "IfcAnnotation/Stair"
    installed = None

    GEOM_GLSL = """
    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint vstyle[];

    uniform float windowW;
    uniform float windowH;

    void main() {
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint s0 = vstyle[0], s1 = vstyle[1];

        // converting NDC to/from window coords
        float hw = windowW/2, hh= windowH/2;
        mat4 windowMatrix = mat4(hw, 0, 0, 0,   0, hh, 0, 0,   0, 0, 1, 0,   0, 0, 0, 1);
        mat4 unwindowMatrix = inverse(windowMatrix);
        vec2 p0w = (windowMatrix * (p0 / p0.w)).xy, p1w = (windowMatrix * (p1 / p1.w)).xy;

        vec4 nose0 = vec4(0), nose1 = vec4(0);

        if (s0 == 1u) {
            vec2 head[CIRCLE_SEGS];
            circle_head(p0w, p1w, head);
            for(int i=0; i<CIRCLE_SEGS; i++) {
                gl_Position = p0 + unwindowMatrix * vec4(head[i], 0, 0) * p0.w;
                EmitVertex();
            }
            gl_Position = p0 + unwindowMatrix * vec4(head[0], 0, 0) * p0.w;
            EmitVertex();
            EndPrimitive();

            vec2 nose = normalize(p1w - p0w) * CIRCLE_SIZE;
            nose0 = unwindowMatrix * vec4(nose, 0, 0) * p0.w;
        }

        if (s1 == 2u) {
            vec2 head[3];
            vec4 head_ndc[3];
            arrow_head(p0w, p1w, head);
            for(int i=0; i<3; i++) head_ndc[i] = unwindowMatrix * vec4(head[i], 0, 0) * p1.w;

            gl_Position = p1;
            EmitVertex();
            gl_Position = p1 - head_ndc[1];
            EmitVertex();
            gl_Position = p1 - head_ndc[2];
            EmitVertex();
            gl_Position = p1;
            EmitVertex();
            EndPrimitive();

            vec2 nose = normalize(p1w - p0w) * ARROW_SIZE;
            nose1 = unwindowMatrix * vec4(nose, 0, 0) * p1.w;
        }

        gl_Position = p0 + nose0;
        EmitVertex();
        gl_Position = p1 - nose1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, obj):
        geom = self.get_path_geom(obj)
        self.draw_lines_styled(obj, geom)


class HiddenDecorator(BaseDecorator):
    basename = "IfcAnnotation/Hidden"
    installed = None

    def decorate(self, obj):
        geom = self.get_mesh_geom(obj)
        self.draw_lines(obj, geom)
