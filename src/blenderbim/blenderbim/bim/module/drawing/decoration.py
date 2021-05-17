"""Viewport decorations"""
import math
from functools import reduce
from itertools import chain

from bpy.types import SpaceView3D
from mathutils import Vector, Matrix
import bpy
import bmesh
import blf
from bpy_extras.view3d_utils import location_3d_to_region_2d
import gpu
import bgl
from gpu.types import GPUShader, GPUBatch, GPUIndexBuf, GPUVertBuf, GPUVertFormat
from gpu_extras.batch import batch_for_shader
import blenderbim.bim.module.drawing.helper as helper


class BaseDecorator():
    # base name of objects to decorate
    basename = "IfcAnnotation/Something"

    DEF_GLSL = """
        #define PI 3.141592653589793
        #define MAX_POINTS 64
        #define CIRCLE_SEGS 24
    """

    LIB_GLSL = """
    #define matCLIP2WIN() vec4(winsize.x/2, winsize.y/2, 1, 1)
    #define matWIN2CLIP() vec4(2/winsize.x, 2/winsize.y, 1, 1)
    #define CLIP2WIN(v) (clip2win * v / v.w)
    #define WIN2CLIP(v) (win2clip * v * v.w)

    void arrow_head(in vec4 dir, in float size, in float angle, out vec4 head[3]) {
        vec4 nose = dir * size;
        float c = cos(angle), s = sin(angle);
        head[0] = nose;
        head[1] = vec4(mat2(c, -s, +s, c) * nose.xy, 0, 0);
        head[2] = vec4(mat2(c, +s, -s, c) * nose.xy, 0, 0);
    }

    void circle_head(in float size, out vec4 head[CIRCLE_SEGS]) {
        float angle_d = PI * 2 / CIRCLE_SEGS;
        for(int i = 0; i<CIRCLE_SEGS; i++) {
            float angle = angle_d * i;
            head[i] = vec4(cos(angle), sin(angle), 0, 0) * size;
        }
    }

    void cross_head(in vec4 dir, in float size, out vec4 head[3]) {
        vec4 nose = dir * size;
        float c = cos(PI/2), s = sin(PI/2);
        head[0] = nose;
        head[1] = vec4(mat2(c, -s, +s, c) * nose.xy, 0, 0);
        head[2] = vec4(mat2(c, +s, -s, c) * nose.xy, 0, 0);
    }
    """

    VERT_GLSL = """
    uniform mat4 viewMatrix;
    in vec3 pos;
    in uint topo;
    out vec4 gl_Position;
    out uint type;

    void main() {
        gl_Position = viewMatrix * vec4(pos, 1.0);
        type = topo;
    }
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=2) out;

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 16.0;

        vec4 p;

        p = p0w + gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w - gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    out vec4 fragColor;

    void main() {
        fragColor = color;
    }
    """

    def __init__(self):
        # NB: libcode param doesn't work
        self.shader = GPUShader(vertexcode=self.VERT_GLSL,
                                fragcode=self.FRAG_GLSL,
                                geocode=self.LIB_GLSL + self.GEOM_GLSL,
                                defines=self.DEF_GLSL)

    def get_objects(self, collection):
        """find relevant objects
        using class.basename

        returns: iterable of blender objects
        """
        return filter(lambda o: self.basename in o.name, collection.all_objects)

    def get_path_geom(self, obj, topo=True):
        """Parses path geometry into line segments

        Args:
          obj: Blender object with data of type Curve
          topo: bool; if types of vertices are needed

        Returns:
          vertices: 3-tuples of coords
          indices: 2-tuples of each segment verices' indices
          topology: types of vertices
            0: internal
            1: beginning
            2: ending
        """
        vertices = []
        indices = []
        topology = []

        idx = 0
        for spline in obj.data.splines:
            spline_points = spline.bezier_points if spline.bezier_points else spline.points
            if len(spline_points) < 2:
                continue
            points = [obj.matrix_world @ p.co for p in spline_points]
            cnt = len(points)
            vertices.extend(p[:3] for p in points)
            if topo:
                topology.append(1)
                topology.extend([0] * max(0, cnt - 2))
                topology.append(2)
            indices.extend((idx+i, idx+i+1) for i in range(cnt-1))
            idx += cnt

        return vertices, indices, topology

    def get_mesh_geom(self, obj):
        """Parses mesh geometry into line segments

        Args:
          obj: Blender object with data of type Mesh

        Returns:
          vertices: 3-tuples of coords
          indices: 2-tuples of each segment verices' indices
        """
        vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
        indices = [e.vertices for e in obj.data.edges]
        return vertices, indices

    def get_editmesh_geom(self, obj):
        """Parses editmode mesh geometry into line segments
        """
        mesh = bmesh.from_edit_mesh(obj.data)
        vertices = []
        indices = []
        idx = 0

        for edge in mesh.edges:
            vertices.extend(edge.verts)
            indices.append((idx, idx+1))
            idx += 2
        vertices = [obj.matrix_world @ v.co for v in vertices]

        return vertices, indices

    def decorate(self, context, object):
        """perform actuall drawing stuff"""
        raise NotImplementedError()

    def draw_lines(self, context, obj, vertices, indices, topology=None):
        region = context.region
        region3d = context.region_data
        color = context.scene.DocProperties.decorations_colour

        fmt = GPUVertFormat()
        fmt.attr_add(id="pos", comp_type='F32', len=3, fetch_mode='FLOAT')
        if topology:
            fmt.attr_add(id="topo", comp_type='U8', len=1, fetch_mode='INT')

        vbo = GPUVertBuf(len=len(vertices), format=fmt)
        vbo.attr_fill(id="pos", data=vertices)
        if topology:
            vbo.attr_fill(id="topo", data=topology)

        ibo = GPUIndexBuf(type='LINES', seq=indices)

        batch = GPUBatch(type='LINES', buf=vbo, elem=ibo)

        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glHint(bgl.GL_LINE_SMOOTH_HINT, bgl.GL_NICEST)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

        self.shader.bind()
        self.shader.uniform_float
        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float("winsize", (region.width, region.height))
        self.shader.uniform_float("color", color)

        batch.draw(self.shader)

    def draw_label(self, context, text, pos, dir, gap=4, center=True, vcenter=False):
        """Draw text label

        Args:
          pos: bottom-center

        aligned and centered at segment middle
        """
        font_id = 0
        font_size = 16
        dpi = context.preferences.system.dpi

        color = context.scene.DocProperties.decorations_colour

        ang = -Vector((1, 0)).angle_signed(dir)
        cos = math.cos(ang)
        sin = math.sin(ang)

        blf.size(font_id, font_size, dpi)

        w, h = 0, 0
        if center or vcenter:
            w, h = blf.dimensions(font_id, text)

        if center:
            # horizontal centering
            pos -= Vector((cos, sin)) * w * 0.5

        if vcenter:
            # vertical centering
            pos -= Vector((-sin, cos)) * h * 0.5

        if gap:
            # side-shifting
            pos += Vector((-sin, cos)) * gap

        blf.enable(font_id, blf.ROTATION)
        blf.position(font_id, pos.x, pos.y, 0)

        blf.rotation(font_id, ang)
        blf.color(font_id, *color)
        blf.draw(font_id, text)
        blf.disable(font_id, blf.ROTATION)

    def format_value(self, context, value):
        unit_system = context.scene.unit_settings.system
        if unit_system == 'IMPERIAL':
            precision = context.scene.BIMProperties.imperial_precision
            if precision == "NONE":
                precision = 256
            elif precision == "1":
                precision = 1
            elif "/" in precision:
                precision = int(precision.split("/")[1])
        elif unit_system == 'METRIC':
            precision = 3
        else:
            return

        return bpy.utils.units.to_string(unit_system, 'LENGTH', value, precision, split_unit=True)


class DimensionDecorator(BaseDecorator):
    """Decorator for dimension objects
    - each edge of a segment with arrow
    - puts metric text next to each segment
    """
    basename = "IfcAnnotation/Dimension"

    DEF_GLSL = BaseDecorator.DEF_GLSL + """
        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 16.0
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);

        vec4 p;

        vec4 head[3];
        arrow_head(dir, ARROW_SIZE, ARROW_ANGLE, head);

        // start edge arrow
        gl_Position = p0;
        EmitVertex();
        p = p0w + head[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        gl_Position = p0;
        EmitVertex();
        EndPrimitive();

        // end edge arrow
        gl_Position = p1;
        EmitVertex();
        p = p1w - head[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w - head[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();

        // stem, with gaps for arrows
        p = p0w + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w - head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        verts, idxs, _ = self.get_path_geom(obj, topo=False)
        self.draw_lines(context, obj, verts, idxs)
        self.draw_labels(context, obj, verts, idxs)

    def draw_labels(self, context, obj, vertices, indices):
        region = context.region
        region3d = context.region_data
        for i0, i1 in indices:
            v0 = Vector(vertices[i0])
            v1 = Vector(vertices[i1])
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            dir = p1 - p0
            if dir.length < 1:
                continue
            length = (v1 - v0).length
            text = self.format_value(context, length)
            self.draw_label(context, text, p0 + (dir) * .5, dir)


class EqualityDecorator(DimensionDecorator):
    """Decorator for equality objects
    - outlines each segment
    - augments with arrows on both sides
    - puts 'EQ' label
    """
    basename = "IfcAnnotation/Equal"

    def draw_labels(self, context, obj, vertices, indices):
        region = context.region
        region3d = context.region_data
        for i0, i1 in indices:
            v0 = Vector(vertices[i0])
            v1 = Vector(vertices[i1])
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            dir = p1 - p0
            if dir.length < 1:
                continue
            self.draw_label(context, "EQ", p0 + (dir) * .5, dir)


class LeaderDecorator(BaseDecorator):
    """Decorating stairs
    - head point with arrow
    - middle points w/out decorations
    """
    basename = "IfcAnnotation/Leader"

    DEF_GLSL = BaseDecorator.DEF_GLSL + """
        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 16.0
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap1 = vec4(0);

        vec4 p;

        // end edge arrow for last segment
        if (t1 == 2u) {
            vec4 head[3];
            arrow_head(dir, ARROW_SIZE, ARROW_ANGLE, head);

            gl_Position = p1;
            EmitVertex();
            p = p1w - head[1];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            p = p1w - head[2];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            gl_Position = p1;
            EmitVertex();
            EndPrimitive();

            gap1 = dir * ARROW_SIZE;
        }

        // stem, adjusted for and arrow
        gl_Position = p0;
        EmitVertex();
        p = p1w - gap1;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        verts, idxs, topo = self.get_path_geom(obj)
        self.draw_lines(context, obj, verts, idxs, topo)


class StairDecorator(BaseDecorator):
    """Decorating stairs
    - head point with arrow
    - tail point with circle
    - middle points w/out decorations
    """
    basename = "IfcAnnotation/Stair"

    DEF_GLSL = BaseDecorator.DEF_GLSL + """
        #define CIRCLE_SIZE 8.0
        #define ARROW_ANGLE PI / 3.0
        #define ARROW_SIZE 24.0
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap0 = vec4(0), gap1 = vec4(0);

        vec4 p;

        // start edge circle for first segment
        if (t0 == 1u) {
            vec4 head[CIRCLE_SEGS];
            circle_head(CIRCLE_SIZE, head);

            for(int i=0; i<CIRCLE_SEGS; i++) {
                p = p0w + head[i];
                gl_Position = WIN2CLIP(p);
                EmitVertex();
            }
            p = p0w + head[0];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            EndPrimitive();

            gap0 = dir * CIRCLE_SIZE;
        }

        // end edge arrow for last segment
        if (t1 == 2u) {
            vec4 head[3];
            arrow_head(dir, ARROW_SIZE, ARROW_ANGLE, head);

            p = p1w - head[1];
            gl_Position = WIN2CLIP(p);
            EmitVertex();

            gl_Position = p1;
            EmitVertex();

            p = p1w - head[2];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            EndPrimitive();
        }

        // stem, with gaps for edge decoration
        p = p0w + gap0;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        verts, idxs, topo = self.get_path_geom(obj)
        self.draw_lines(context, obj, verts, idxs, topo)


class HiddenDecorator(BaseDecorator):
    basename = "IfcAnnotation/Hidden"

    DEF_GLSL = BaseDecorator.DEF_GLSL + """
        #define DASH_SIZE 16.0
        #define DASH_PATTERN 0x0000FFFFU
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    out float dist; // distance from starging point along segment

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 1;

        vec4 p;

        // NB: something should be used to affect position, otherwise compiler eliminates winsize

        dist = 0;
        p = p0w + gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        dist = length(edge);
        p = p1w - gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    in vec2 gl_FragCoord;
    in float dist;
    out vec4 fragColor;

    void main() {
        uint bit = uint(fract(dist / DASH_SIZE) * 32);
        if ((DASH_PATTERN & (1U<<bit)) == 0U) discard;
        fragColor = color;
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts, idxs = self.get_editmesh_geom(obj)
        else:
            verts, idxs = self.get_mesh_geom(obj)
        self.draw_lines(context, obj, verts, idxs)


class MiscDecorator(HiddenDecorator):
    basename = "IfcAnnotation/Misc"

    FRAG_GLSL = BaseDecorator.FRAG_GLSL


class LevelDecorator(BaseDecorator):

    def get_splines(self, obj):
        """Iterates through splines
        Args:
          obj: Blender object with Curve data

        Yields:
          verts: points of each spline, world coords
        """
        for spline in obj.data.splines:
            spline_points = spline.bezier_points if spline.bezier_points else spline.points
            if len(spline_points) < 2:
                continue
            yield [obj.matrix_world @ p.co for p in spline_points]

    def decorate(self, context, obj):
        verts, idxs, topo = self.get_path_geom(obj)
        self.draw_lines(context, obj, verts, idxs, topo)
        splines = self.get_splines(obj)
        self.draw_labels(context, obj, splines)


class PlanLevelDecorator(LevelDecorator):
    basename = "IfcAnnotation/Plan Level"

    DEF_GLSL = BaseDecorator.DEF_GLSL + """
        #define CIRCLE_SIZE 8.0
        #define CROSS_SIZE 16.0
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap1 = vec4(0);

        vec4 p;

        // end edge cross+circle for last segment
        if (t1 == 2u) {
            vec4 head_o[CIRCLE_SEGS];
            circle_head(CIRCLE_SIZE, head_o);

            for(int i=0; i<CIRCLE_SEGS; i++) {
                p = p1w + head_o[i];
                gl_Position = WIN2CLIP(p);
                EmitVertex();
            }
            p = p1w + head_o[0];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            EndPrimitive();

            vec4 head_x[3];
            cross_head(dir, CROSS_SIZE, head_x);

            p = p1w + head_x[1];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            p = p1w + head_x[2];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            EndPrimitive();

            gap1 = head_x[0];
        }

        // stem, adjusted for and arrow
        gl_Position = p0;
        EmitVertex();
        p = p1w + gap1;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def draw_labels(self, context, obj, splines):
        region = context.region
        region3d = context.region_data
        for verts in splines:
            v0 = verts[0]
            v1 = verts[1]
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            dir = p1 - p0
            if dir.length < 1:
                continue
            text = "RL " + self.format_value(context, verts[-1].z)
            self.draw_label(context, text, p0, dir, gap=8, center=False)


class SectionLevelDecorator(LevelDecorator):
    basename = "IfcAnnotation/Section Level"

    DEF_GLSL = BaseDecorator.DEF_GLSL + """
        #define CALLOUT_GAP 8.0
        #define CALLOUT_SIZE 64.0
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint type[];
    out float dist; // distance from starging point along segment

    void callout_head(in vec4 dir, out vec4 head[4]) {
        vec2 gap = dir.xy * CALLOUT_GAP;
        vec2 tail = dir.xy * -CALLOUT_SIZE;
        vec2 side = cross(vec3(dir.xy, 0), vec3(0, 0, 1)).xy * CALLOUT_GAP;

        head[0] = vec4(tail + side, 0, 0);
        head[1] = vec4(gap * 2 + side, 0, 0);
        head[2] = vec4(gap, 0, 0);
        head[3] = vec4(side, 0, 0);
    }

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 16.0;

        vec4 p;

        // start edge callout
        if (t0 == 1u) {
            vec4 head[4];
            callout_head(dir, head);

            for(int i=0; i<4; i++) {
                p = p0w + head[i];
                gl_Position = WIN2CLIP(p);
                EmitVertex();
            }
            EndPrimitive();
        }

        // stem
        dist = 0;
        gl_Position = p0;
        EmitVertex();
        dist = length(p1w - p0w);
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def draw_labels(self, context, obj, splines):
        region = context.region
        region3d = context.region_data
        for verts in splines:
            v0 = verts[0]
            v1 = verts[1]
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            dir = p1 - p0
            if dir.length < 1:
                continue
            text = "RL " + self.format_value(context, verts[-1].z)
            self.draw_label(context, text, p0 + dir.normalized() * 16, -dir, gap=16, center=False)


class BreakDecorator(BaseDecorator):
    """Decorator for dimension objects
    - first edge of a mesh with zigzag thingy in the middle

    Uses first two vertices in verts list.
    """
    basename = "IfcAnnotation/Break"

    DEF_GLSL = BaseDecorator.DEF_GLSL + """
        #define BREAK_LENGTH 32.0
        #define BREAK_WIDTH 16.0
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1), pmw = (p0w + p1w) * .5;
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 16.0;

        vec4 p;

        vec4 quart = dir * BREAK_LENGTH * .25;
        vec4 side = vec4(cross(vec3(dir.xy, 0), vec3(0, 0, 1)).xy, 0, 0) * BREAK_WIDTH;

        // TODO: check if there's enough length for zigzag

        gl_Position = p0;
        EmitVertex();

        p = pmw;
        gl_Position = WIN2CLIP(p);
        EmitVertex();

        p = pmw + quart - side;
        gl_Position = WIN2CLIP(p);
        EmitVertex();

        p = pmw + quart * 3 + side;
        gl_Position = WIN2CLIP(p);
        EmitVertex();

        p = pmw + quart * 4;
        gl_Position = WIN2CLIP(p);
        EmitVertex();

        gl_Position = p1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts = self.get_editmesh_geom(obj)
        else:
            verts = self.get_mesh_geom(obj)
        self.draw_lines(context, obj, verts, [(0, 1)])

    def get_mesh_geom(self, obj):
        # first vertices only
        vertices = [obj.matrix_world @ obj.data.vertices[i].co for i in (0, 1)]
        return vertices

    def get_editmesh_geom(self, obj):
        # first vertices only
        mesh = bmesh.from_edit_mesh(obj.data)
        vertices = [obj.matrix_world @ v.co for v in mesh.edges[0].verts]
        return vertices


class GridDecorator(BaseDecorator):
    basename = "IfcGridAxis/"

    DEF_GLSL = BaseDecorator.DEF_GLSL + """
        #define CIRCLE_SIZE 16.0
        #define DASH_SIZE 48.0
        #define DASH_PATTERN 0x03C0FFFFU
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    out float dist; // distance from starging point along segment

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * CIRCLE_SIZE;

        vec4 p;

        vec4 head[CIRCLE_SEGS];
        circle_head(CIRCLE_SIZE, head);

        dist = 0;

        // start edge circle
        for(int i=0; i<CIRCLE_SEGS; i++) {
            p = p0w + head[i];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
        }
        p = p0w + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // end edge circle
        for(int i=0; i<CIRCLE_SEGS; i++) {
            p = p1w + head[i];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
        }
        p = p1w + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // stem
        dist = 0;
        p = p0w + gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        dist = length(edge);
        p = p1w - gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    in vec2 gl_FragCoord;
    in float dist;
    out vec4 fragColor;

    void main() {
        uint bit = uint(fract(dist / DASH_SIZE) * 32);
        if ((DASH_PATTERN & (1U<<bit)) == 0U) discard;
        fragColor = color;
    }
    """

    def get_mesh_geom(self, obj):
        # first vertices only
        vertices = [obj.matrix_world @ obj.data.vertices[i].co for i in (0, 1)]
        return vertices

    def get_editmesh_geom(self, obj):
        # first vertices only
        mesh = bmesh.from_edit_mesh(obj.data)
        vertices = [obj.matrix_world @ v.co for v in mesh.edges[0].verts]
        return vertices

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts = self.get_editmesh_geom(obj)
        else:
            verts = self.get_mesh_geom(obj)
        self.draw_lines(context, obj, verts, [(0, 1)])
        self.draw_labels(context, obj, verts)

    def draw_labels(self, context, obj, vertices):
        region = context.region
        region3d = context.region_data
        v0 = Vector(vertices[0])
        v1 = Vector(vertices[1])
        p0 = location_3d_to_region_2d(region, region3d, v0)
        p1 = location_3d_to_region_2d(region, region3d, v1)
        dir = Vector((1, 0))
        text = obj.name.split("/")[1].split(".")[0]
        self.draw_label(context, text, p0, dir, vcenter=True, gap=0)
        self.draw_label(context, text, p1, dir, vcenter=True, gap=0)


class SectionViewDecorator(LevelDecorator):
    basename = "IfcAnnotation/Section"

    DEF_GLSL = BaseDecorator.DEF_GLSL + """
        #define CIRCLE_SIZE 8.0
        #define TRIANGLE_L 32.0
        #define TRIANGLE_W 16.0
    """

    GEOM_GLSL = """
    uniform vec2 winsize;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    void triangle_head(in vec4 dir, in vec4 side, in float length, in float width, out vec4 head[3]) {
        vec4 nose = dir * length;
        vec4 ear = side * width;
        head[0] = vec4(0);
        head[1] = nose * .5 + ear;
        head[2] = nose;
    }

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * TRIANGLE_L * .5;
        vec4 side = vec4(cross(vec3(dir.xy, 0), vec3(0, 0, 1)).xy, 0, 0);
        vec4 p;

        vec4 head[CIRCLE_SEGS];
        circle_head(CIRCLE_SIZE, head);

        vec4 head3[3];

        // start edge circle
        for(int i=0; i<CIRCLE_SEGS; i++) {
            p = p0w + gap + head[i];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
        }
        p = p0w + gap + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // start edge triangle
        triangle_head(dir, -side, TRIANGLE_L, TRIANGLE_W, head3);
        p = p0w + head3[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head3[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head3[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // end edge circle
        for(int i=0; i<CIRCLE_SEGS; i++) {
            p = p1w - gap + head[i];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
        }
        p = p1w - gap + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // end edge triangle
        triangle_head(-dir, -side, TRIANGLE_L, TRIANGLE_W, head3);
        p = p1w + head3[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w + head3[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w + head3[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // stem
        gl_Position = p0;
        EmitVertex();
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        verts, _, _ = self.get_path_geom(obj, topo=False)
        self.draw_lines(context, obj, verts, [(0, 1)])


class DecorationsHandler():
    decorators_classes = [
        DimensionDecorator,
        EqualityDecorator,
        GridDecorator,
        HiddenDecorator,
        LeaderDecorator,
        MiscDecorator,
        PlanLevelDecorator,
        SectionLevelDecorator,
        StairDecorator,
        BreakDecorator,
        SectionViewDecorator
    ]

    installed = None

    @classmethod
    def install(cls, context):
        if cls.installed:
            cls.uninstall()
        handler = cls()
        cls.installed = SpaceView3D.draw_handler_add(handler, (context,), 'WINDOW', 'POST_PIXEL')

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, 'WINDOW')
        except ValueError:
            pass
        cls.installed = None

    def __init__(self):
        self.decorators = [cls() for cls in self.decorators_classes]

    def __call__(self, context):
        collection, _ = helper.get_active_drawing(context.scene)
        if collection is None:
            return

        for decorator in self.decorators:
            for obj in decorator.get_objects(collection):
                decorator.decorate(context, obj)
