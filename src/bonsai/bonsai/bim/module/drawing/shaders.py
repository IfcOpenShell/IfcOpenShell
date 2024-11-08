# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Maxim Vasilyev <qwiglydee@gmail.com>
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

from gpu_extras.batch import batch_for_shader
import gpu
from mathutils import Vector


# NOTES:
# Since Metal doesn't support geometry shaders we stick to builtin shaders
# and generate all geometry data in python before passing it to the shader.
# This way was considered to be the most reliable atm.
# More: https://blender.stackexchange.com/questions/291674/migrating-geometry-shaders-to-metal
#
# BGL deprecation:
# since `bgl` is deprecated, creating smoothing lines became tricky
# Notes for creating shaders with smoothed lines:
# in geom shader - use triangle_strip, DEFAULT_SETUP, do_edge_verts or do_vertex to emit vertices
# in frag shader - use lineWidth uniform, smoothline flaot in, smoothing shader code from base shader
# mind the vertex limit since emitting vertices for smoothed lines produces twice as much vertices


BASE_DEF_GLSL = """
#define PI 3.141592653589793
#define MAX_POINTS 64
#define CIRCLE_SEGS 12
#define SMOOTH_WIDTH 1.0
#define lineSmooth true
"""

BASE_LIB_GLSL = """
// TODO: redefine as macor instead
uniform vec2 winsize;
uniform float lineWidth;
#define half_winsize (winsize / 2)
// convert camera to window
#define C2W(v) vec4(v.x * half_winsize.x / v.w, v.y * half_winsize.y / v.w, v.z / v.w, 1)
// convert window to camera
#define W2C(v) vec4(v.x * v.w / half_winsize.x, v.y * v.w / half_winsize.y, v.z * v.w, 1)

void emitSegment(vec4 p0, vec4 p1) {
    gl_Position = p0;
    EmitVertex();
    gl_Position = p1;
    EmitVertex();
    EndPrimitive();
}

void emitTriangle(vec4 p1, vec4 p2, vec4 p3) {
    gl_Position = p1;
    EmitVertex();
    gl_Position = p2;
    EmitVertex();
    gl_Position = p3;
    EmitVertex();
    EndPrimitive();
}

#define matCLIP2WIN() vec4(winsize.x/2, winsize.y/2, 1, 1)
#define CLIP2WIN(v) (clip2win * (v) / (v).w)
#define matWIN2CLIP() vec4(2/winsize.x, 2/winsize.y, 1, 1)
#define WIN2CLIP(v) (win2clip * (v) * (v).w)
#define DEFAULT_SETUP() vec4 clip2win = matCLIP2WIN(), win2clip = matWIN2CLIP(); vec2 EDGE_DIR

out float smoothline;

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

bool check_counterclockwise(in vec4 A, in vec4 B, in vec4 C) {
    return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x);
}

void angle_circle_head(
    in vec4 circle_start, in float circle_angle,
    in bool counterclockwise,
    out vec4 head[CIRCLE_SEGS+1], out float angle_segs) {
    
    // 1 added to CIRCLE_SEGS because we're number of vertices
    // for n segments is n+1
    
    float angle_d;
    angle_d = PI * 2 / CIRCLE_SEGS; // 30d
    // need to bottom clamp it to 1, otherwise it causes Blender crash at extruding the curve
    angle_segs = max(1, ceil(circle_angle / angle_d));
    angle_d = circle_angle / angle_segs;
    
    for(int i = 0; i < (angle_segs + 1); i++) {
        float angle = angle_d * i;
        if (counterclockwise) {
            head[i] = vec4(
                circle_start.x *  cos(-angle) + circle_start.y * sin(-angle),
                circle_start.x * -sin(-angle) + circle_start.y * cos(-angle),
                0, 0
            );
        } else {
                head[i] = vec4(
                circle_start.x *  cos(angle) + circle_start.y * sin(angle),
                circle_start.x * -sin(angle) + circle_start.y * cos(angle),
                0, 0
            );
        }
    }
}

void cross_head(in vec4 dir, in float size, out vec4 head[3]) {
    vec4 nose = dir * size;
    float c = cos(PI/2), s = sin(PI/2);
    head[0] = nose;
    head[1] = vec4(mat2(c, -s, +s, c) * nose.xy, 0, 0);
    head[2] = vec4(mat2(c, +s, -s, c) * nose.xy, 0, 0);
}

// do_vertex_util is custom EmitVertex method to support line smoothing
// `e`   - edge xy direction in win/clip space (directions are invariant in both spaces)
#define do_vertex(pos, e) (do_vertex_util(pos, vec2(-(e).y, (e).x) / winsize.xy))
#define do_vertex_win(pos, e) ( do_vertex( WIN2CLIP( pos ), e ) )

// if vertex is shared by two segments of the line still need to emit it twice 
// to avoid smoothing artifacts
// don't forget to initialize `vec2 EDGE_DIR` for macro to work
// `pos0` / `pos1` - vertex position in clip space
#define do_edge_verts(pos0, pos1) ( EDGE_DIR = normalize( ( (pos1) - (pos0) ).xy ), do_vertex( pos0, EDGE_DIR ), do_vertex( pos1, EDGE_DIR) )
#define do_edge_verts_win(pos0, pos1) ( do_edge_verts( WIN2CLIP(pos0), WIN2CLIP(pos1) ) )
void do_vertex_util(vec4 pos, vec2 ofs)
{
    float final_line_width = lineWidth + SMOOTH_WIDTH * float(lineSmooth);
    ofs *= final_line_width;

    smoothline = final_line_width * 0.5;
    gl_Position = pos;
    gl_Position.xy += ofs * pos.w;
    EmitVertex();

    smoothline = -final_line_width * 0.5;
    gl_Position = pos;
    gl_Position.xy -= ofs * pos.w;
    EmitVertex();
}

// geometry utils
void triangle_head(in vec4 side, in vec4 dir, in float length, in float width, in float radius, out vec4 head[5]) {
    // TODO: radius is unnecessary?
    head[0] = side * -radius;
    head[1] = side * length * -.5;
    head[2] = dir * width;
    head[3] = side * length * .5;
    head[4] = side * radius;
}

void do_triangle_head(vec4 pos_w, vec4 head[5]) {
    DEFAULT_SETUP();
    do_edge_verts_win(pos_w + head[0], pos_w + head[1]);
    do_edge_verts_win(pos_w + head[1], pos_w + head[2]);
    do_edge_verts_win(pos_w + head[2], pos_w + head[3]);
    do_edge_verts_win(pos_w + head[3], pos_w + head[4]);
}

void do_circle_head(vec4 pos_w, vec4 head[CIRCLE_SEGS]) {
    DEFAULT_SETUP();
    for(int i=0; i<CIRCLE_SEGS-1; i++) {
        do_edge_verts_win(pos_w + head[i], pos_w + head[i+1]);
        EmitVertex();
    }
    do_edge_verts_win( pos_w + head[CIRCLE_SEGS-1], pos_w + head[0] );
}

"""


def add_verts_sequence(verts, start_i, output_verts, output_edges, closed=False):
    """Add sequence of verts to output lists, returns next vertex index"""
    for i, v in enumerate(verts[:-1], start_i):
        output_verts.append(v)
        output_edges.append((i, i + 1))
    output_verts.append(verts[-1])
    if closed:
        output_edges.append((i + 1, start_i))
    return i + 2


def add_offsets(v, offsets):
    """returns list of verts with offsets added"""
    return [v + offset for offset in offsets]


class BaseShader:
    """Wrapper for GPUShader
    To use for viewport decorations with geometry generated on GPU side.

    The Geometry shader works in clipping coords (aftre projecting before division and window scaling).
    To make window-scale geometry, vectors should be calculated in window space and than back-projected to clipping spae.
    Provide `half_winsize` uniform vector with halfsize of window, and use W2C and C2W macros.

    Replace glsl code in derived classes.
    Beware of unused attributes and uniforms: glsl compiler will optimize them out and blender fail with an exception.


    Vertex topology attribute to use with line segments:
    - 0 = inner
    - 1 = starting
    - 2 = ending
    - 3 = isolated
    """

    TYPE = None  # should be LINES|POINTS|etc

    DEF_GLSL = BASE_DEF_GLSL

    VERT_GLSL = """
    uniform mat4 viewMatrix;
    uniform mat4 modelMatrix;

    in vec3 pos;
    in uint topology;
    out vec4 gl_Position;
    out uint topo;

    void main() {
        gl_Position = viewMatrix * modelMatrix * vec4(pos, 1.0);
        topo = topology;
    }
    """

    # prepended to geom_glsl
    LIB_GLSL = BASE_LIB_GLSL

    GEOM_GLSL = """
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices = 4) out;

    void main() {
        // default setup for macro to work
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();
        vec2 EDGE_DIR;

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        do_edge_verts(p0, p1);
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    uniform float lineWidth;
    
    in float smoothline;
    out vec4 fragColor;
    void main() {
        vec2 co = gl_FragCoord.xy;

        fragColor = color;
        if (lineSmooth) {
            fragColor.a *= clamp((lineWidth + SMOOTH_WIDTH) * 0.5 - abs(smoothline), 0.0, 1.0);
        }
    }
    """

    def __init__(self):
        # POLYLINE_UNIFORM_COLOR is good for smoothed lines since `bgl.enable(GL_LINE_SMOOTH)` is deprecated
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.base_shader = gpu.shader.from_builtin("UNIFORM_COLOR")

    def get_shader(self):
        """Returns shader for this type"""
        return self.line_shader if self.TYPE == "LINES" else self.base_shader

    def batch(self, indices=None, **data):
        """Returns automatic GPUBatch filled with provided parameters"""
        shader = self.get_shader()
        batch = batch_for_shader(shader, self.TYPE, data, indices=indices)
        return batch

    def bind(self):
        """need to bind shader before changing it's uniforms"""
        shader = self.get_shader()
        shader.bind()
        return shader

    def glenable(self):
        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("LESS_EQUAL")

    def uniform_region(self, ctx):
        shader = self.bind()

        region = ctx.region
        region3d = ctx.region_data

        uniform_floats = {
            "ModelViewProjectionMatrix": region3d.perspective_matrix,
            # POLYLINE_UNIFORM_COLOR specific uniforms
            "viewportSize": (region.width, region.height),
            "lineWidth": 2.5,
        }

        for name, value in uniform_floats.items():
            shader.uniform_float(name, value)


# TODO: add smoothing if this shader is going to be used
# TODO: dead code?
class BaseLinesShader(BaseShader):
    """Draws line segments with gaps around vertices at endpoints"""

    TYPE = "LINES"

    DEF_GLSL = (
        BaseShader.DEF_GLSL
        + """
    #define GAP_SIZE {gap_size}
    """
    )

    GEOM_GLSL = """
    layout(lines) in;
    in uint topo[];
    layout(line_strip, max_vertices=2) out;

    void main() {
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = topo[0], t1 = topo[1];

        vec4 p0w = C2W(p0), p1w = C2W(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * GAP_SIZE;

        vec4 p0_ = p0w, p1_ = p1w;

        if (t0 == 1u) {
            p0_ += gap;
        }

        if (t1 == 2u) {
            p1_ -= gap;
        }

        emitSegment(W2C(p0_), W2C(p1_));
    }
    """

    def __init__(self, gap_size=16):
        super().__init__(gap_size=gap_size)

    def glenable(self):
        super().glenable()


class GizmoShader(BaseShader):
    """Gizmo 2D shader

    Scaling to match viewport is partially controlled by user preferences and gizmo code.
    """

    # TODO: add some magic to respect gizmo settings/params

    VERT_GLSL = """
    uniform mat4 ModelViewProjectionMatrix;

    in vec3 pos;

    void main() {
        gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0);
    }
    """


# TODO: add smoothing if this shader is going to be used
class DotsGizmoShader(GizmoShader):
    """Draws circles of radius 1 around points"""

    TYPE = "POINTS"

    DEF_GLSL = (
        BaseShader.DEF_GLSL
        + """
    #define CIRCLE_SEGMENTS 12
    #define CIRCLE_RADIUS 8
    """
    )

    GEOM_GLSL = """
    layout(points) in;
    layout(triangle_strip, max_vertices=36) out;

    // apparently can be precalculated
    void makeCircle(out vec4 circle[CIRCLE_SEGMENTS+1]) {
        float angle_d = PI * 2 / CIRCLE_SEGMENTS;
        for(int i = 0; i<=CIRCLE_SEGMENTS; i++) {
            float angle = angle_d * i;
            circle[i] = vec4(cos(angle), sin(angle), 0, 0) * CIRCLE_RADIUS;
        }
    }

    void main() {
        vec4 p0 = gl_in[0].gl_Position;
        vec4 p0w = C2W(p0);

        vec4 circle[CIRCLE_SEGMENTS+1];
        makeCircle(circle);

        vec4 p1w, p2w;

        for(int i = 0; i<=CIRCLE_SEGMENTS; i++) {
            p1w = p0w + circle[i];
            p2w = p0w + circle[i+1];
            emitTriangle(p0, W2C(p1w), W2C(p2w));
        }
/*
        for(int i = 0; i<=CIRCLE_SEGMENTS; i++) {
            p1w = p0 + circle[i];
            p2w = p0 + circle[i+1];
            emitTriangle(p0, p1w, p2w);
        }
*/
    }
    """


class ExtrusionGuidesShader(GizmoShader):
    """Draws lines and add cross in XY plane at endpoints"""

    TYPE = "LINES"

    def process_geometry(self, verts):
        CROSS_SIZE = 0.5

        p0, p1 = verts
        bx = Vector((1, 0, 0)) * CROSS_SIZE
        by = Vector((0, 1, 0)) * CROSS_SIZE

        output_verts = []
        output_edges = []
        out_kwargs = {
            "output_verts": output_verts,
            "output_edges": output_edges,
        }

        start_i = 0
        start_i = add_verts_sequence(add_offsets(p0, [-bx, bx]), start_i, **out_kwargs)
        start_i = add_verts_sequence(add_offsets(p0, [-by, by]), start_i, **out_kwargs)
        start_i = add_verts_sequence(add_offsets(p1, [-bx, bx]), start_i, **out_kwargs)
        start_i = add_verts_sequence(add_offsets(p1, [-by, by]), start_i, **out_kwargs)

        return output_verts, output_edges
