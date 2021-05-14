from mathutils import Matrix
import bgl
from gpu.types import GPUShader
from gpu_extras.batch import batch_for_shader


class BaseShader():
    """Wrapepr for GPUShader
    To use for viewport decorations with geometry generated on GPU side.

    The Geometry shader works in clipping coords (aftre projecting before division and window scaling).
    To make window-scale geometry, vectors should be calculated in window space and than back-projected to clipping spae.
    Provide `winSize` uniform vector with halfsize of window, and use W2C and C2W macros.

    Replace glsl code in derived classes.
    Beware of unused attributes and uniforms: glsl compiler will optimize them out and blender fail with an exception.


    Vertex topology attribute to use with line segments:
    - 0 = inner
    - 1 = starting
    - 2 = ending
    - 3 = isolated
    """

    TYPE = None  # should be LINES|POINTS|etc

    DEF_GLSL = """
    #define PI 3.141592653589793
    """

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
    LIB_GLSL = """
    uniform vec2 winSize;
    // convert camera to window
    #define C2W(v) vec4(v.x * winSize.x / v.w, v.y * winSize.y / v.w, v.z / v.w, 1)
    // convert window to camera
    #define W2C(v) vec4(v.x * v.w / winSize.x, v.y * v.w / winSize.y, v.z * v.w, 1)

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
    """

    GEOM_GLSL = """
    """

    FRAG_GLSL = """
    uniform vec4 color;
    out vec4 fragColor;

    void main() {
        fragColor = color;
    }
    """

    def __init__(self):
        # NB: libcode arg doesn't work
        self.prog = GPUShader(vertexcode=self.VERT_GLSL,
                              fragcode=self.FRAG_GLSL,
                              geocode=self.LIB_GLSL + self.GEOM_GLSL,
                              defines=self.DEF_GLSL)

    def batch(self, indices=None, **data):
        """Returns automatic GPUBatch filled with provided parameters
        """
        batch = batch_for_shader(self.prog, self.TYPE, data, indices=indices)
        batch.program_set(self.prog)
        return batch

    def bind(self):
        self.prog.bind()

    def glenable(self):
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
        bgl.glBlendEquation(bgl.GL_FUNC_ADD)

        # bgl.glEnable(bgl.GL_DEPTH_TEST)
        # bgl.glDepthFunc(bgl.GL_LEQUAL)
        # bgl.glDepthMask(True)

    def uniform_region(self, ctx):
        region = ctx.region
        region3d = ctx.region_data
        try:
            self.prog.uniform_float('viewMatrix', region3d.perspective_matrix)
        except ValueError:  # unused uniform
            pass
        try:
            self.prog.uniform_float('winSize', (region.width / 2, region.height / 2))
        except ValueError:  # unused uniform
            pass


class BaseLinesShader(BaseShader):
    """Draws line segments with gaps around vertices at endpoints
    """
    TYPE = 'LINES'

    DEF_GLSL = BaseShader.DEF_GLSL + """
    #define GAP_SIZE {gap_size}
    """

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
        bgl.glEnable(bgl.GL_LINE_SMOOTH)


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


class DotsGizmoShader(GizmoShader):
    """Draws circles of radius 1 around points"""

    TYPE = 'POINTS'

    DEF_GLSL = BaseShader.DEF_GLSL + """
    #define CIRCLE_SEGMENTS 12
    #define CIRCLE_RADIUS 8
    """

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

    TYPE = 'LINES'

    DEF_GLSL = BaseShader.DEF_GLSL + """
    #define CROSS_SIZE .5
    """

    GEOM_GLSL = """
    uniform mat4 ModelViewProjectionMatrix;

    layout(lines) in;
    layout(line_strip, max_vertices=10) out;

    void main() {
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        vec4 p0w = C2W(p0), p1w = C2W(p1);

        emitSegment(p0, p1);

        vec4 bx = ModelViewProjectionMatrix[0] * CROSS_SIZE;
        vec4 by = ModelViewProjectionMatrix[1] * CROSS_SIZE;

        emitSegment(p0 - bx, p0 + bx);
        emitSegment(p0 - by, p0 + by);
        emitSegment(p1 - bx, p1 + bx);
        emitSegment(p1 - by, p1 + by);
    }
    """

    def glenable(self):
        super().glenable()
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
