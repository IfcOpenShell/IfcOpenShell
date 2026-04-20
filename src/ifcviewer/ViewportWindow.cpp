/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "ViewportWindow.h"

#include "AppSettings.h"

#include <QMouseEvent>
#include <QKeyEvent>
#include <QWheelEvent>
#include <QSurfaceFormat>
#include <QCoreApplication>
#include <QtMath>
#include <QtOpenGL/QOpenGLVersionFunctionsFactory>

#include <cstring>
#include <cstdlib>
#include <cmath>
#include <algorithm>
#include <limits>

static const size_t INITIAL_VBO_SIZE  = 64 * 1024 * 1024;   // 64 MB
static const size_t INITIAL_EBO_SIZE  = 32 * 1024 * 1024;   // 32 MB
static const size_t INITIAL_SSBO_SIZE = 4  * 1024 * 1024;   // 4 MB (~52k instances)
static const size_t MAX_BUFFER_SIZE   = 4ull * 1024 * 1024 * 1024;  // 4 GB

static_assert(sizeof(DrawElementsIndirectCommand) == 20, "indirect cmd must be 20 bytes");

// -----------------------------------------------------------------------------
// Shaders
// -----------------------------------------------------------------------------
//
// Vertex layout (GL side, 12 bytes — quantized; see InstancedGeometry.h):
//   location 0: vec3 a_position_q   (u16x3 normalized, per-mesh AABB basis)
//   location 1: vec2 a_normal_oct   (i8x2 normalized, octahedral)
//   location 2: vec4 a_color        (u8x4 normalized)
//
// Per-instance record in SSBO std430 (80 bytes):
//   mat4 transform
//   uint object_id
//   uint color_override_rgba8     -- 0 => use baked a_color
//   uint mesh_id                  -- index into per-model MeshGpu[]
//   uint _pad1
//
// The draw calls pass `u_instance_offset = mesh.first_instance`; the shader
// reads `instances[u_instance_offset + gl_InstanceID]`.

static const char* MAIN_VERTEX_SHADER = R"(
#version 450 core
#extension GL_ARB_shader_draw_parameters : require
// Quantized vertex inputs — see InstancedGeometry.h for layout.
layout(location = 0) in vec3 a_position_q;  // u16x3 normalized -> [0,1]
layout(location = 1) in vec2 a_normal_oct;  // i8x2 normalized -> [-1,1]
layout(location = 2) in vec4 a_color;

struct InstanceRecord {
    mat4 transform;
    uint object_id;
    uint color_override;
    uint mesh_id;
    uint _pad1;
};
layout(std430, binding = 0) readonly buffer Instances {
    InstanceRecord instances[];
};
layout(std430, binding = 1) readonly buffer VisibleIndices {
    uint visible[];
};
struct MeshQuant { vec4 aabb_min; vec4 aabb_max; };
layout(std430, binding = 2) readonly buffer Meshes {
    MeshQuant meshes[];
};

uniform mat4 u_view_projection;
uniform uint u_selected_id;

out vec3 v_normal;
out vec4 v_color;
flat out uint v_object_id;
flat out uint v_selected;

// Meyer et al. octahedral normal decode.  Input is in [-1,1]^2.
vec3 octDecode(vec2 e) {
    vec3 n = vec3(e.xy, 1.0 - abs(e.x) - abs(e.y));
    if (n.z < 0.0) n.xy = (1.0 - abs(n.yx)) * vec2(n.x >= 0.0 ? 1.0 : -1.0,
                                                    n.y >= 0.0 ? 1.0 : -1.0);
    return normalize(n);
}

void main() {
    uint slot = uint(gl_BaseInstanceARB) + uint(gl_InstanceID);
    uint iid = visible[slot];
    InstanceRecord inst = instances[iid];
    MeshQuant mq = meshes[inst.mesh_id];

    // Dequantize local position against this mesh's AABB.
    vec3 pos_local = mix(mq.aabb_min.xyz, mq.aabb_max.xyz, a_position_q);

    vec4 world = inst.transform * vec4(pos_local, 1.0);
    gl_Position = u_view_projection * world;

    // Rotate the normal by the upper-3x3 of the transform.  BIM placements
    // are overwhelmingly rigid rotations (+ optional uniform scale +
    // optional reflection), so we skip the full inverse-transpose but do
    // need to flip the normal when the transform contains a reflection,
    // otherwise mirrored instances shade as if inside-out.  The same
    // determinant sign is what GL_CULL_FACE uses to decide winding, so
    // keeping them in agreement means backface culling is safe to enable.
    vec3 n_local = octDecode(a_normal_oct);
    mat3 rot = mat3(inst.transform);
    vec3 n = rot * n_local;
    if (determinant(rot) < 0.0) n = -n;
    v_normal = normalize(n);

    vec4 baked = a_color;
    if (inst.color_override != 0u) {
        float r = float((inst.color_override      ) & 0xFFu) / 255.0;
        float g = float((inst.color_override >>  8) & 0xFFu) / 255.0;
        float b = float((inst.color_override >> 16) & 0xFFu) / 255.0;
        float a = float((inst.color_override >> 24) & 0xFFu) / 255.0;
        if (a > 0.0) baked = vec4(r, g, b, a);
    }
    v_color = baked;

    v_object_id = inst.object_id;
    v_selected = (v_object_id == u_selected_id) ? 1u : 0u;
}
)";

static const char* MAIN_FRAGMENT_SHADER = R"(
#version 450 core
in vec3 v_normal;
in vec4 v_color;
flat in uint v_object_id;
flat in uint v_selected;

uniform vec3 u_light_dir;

out vec4 frag_color;

void main() {
    // v_normal already has the reflection flip applied in the vertex
    // shader.  When backface culling is off, open shells let us see the
    // "wrong" side of a face — flip based on gl_FrontFacing so both
    // sides light correctly.  When culling is on this branch is always
    // true and has no effect.
    vec3 n = normalize(v_normal);
    if (!gl_FrontFacing) n = -n;
    float ndotl = max(dot(n, u_light_dir), 0.0);
    float ambient = 0.25;
    float diffuse = 0.75 * ndotl;
    vec3 color = v_color.rgb * (ambient + diffuse);
    if (v_selected == 1u) color = mix(color, vec3(0.2, 0.6, 1.0), 0.5);
    frag_color = vec4(color, v_color.a);
}
)";

static const char* PICK_VERTEX_SHADER = R"(
#version 450 core
#extension GL_ARB_shader_draw_parameters : require
layout(location = 0) in vec3 a_position_q;

struct InstanceRecord {
    mat4 transform;
    uint object_id;
    uint color_override;
    uint mesh_id;
    uint _pad1;
};
layout(std430, binding = 0) readonly buffer Instances {
    InstanceRecord instances[];
};
layout(std430, binding = 1) readonly buffer VisibleIndices {
    uint visible[];
};
struct MeshQuant { vec4 aabb_min; vec4 aabb_max; };
layout(std430, binding = 2) readonly buffer Meshes {
    MeshQuant meshes[];
};

uniform mat4 u_view_projection;

flat out uint v_object_id;

void main() {
    uint slot = uint(gl_BaseInstanceARB) + uint(gl_InstanceID);
    uint iid = visible[slot];
    InstanceRecord inst = instances[iid];
    MeshQuant mq = meshes[inst.mesh_id];
    vec3 pos_local = mix(mq.aabb_min.xyz, mq.aabb_max.xyz, a_position_q);
    gl_Position = u_view_projection * inst.transform * vec4(pos_local, 1.0);
    v_object_id = inst.object_id;
}
)";

static const char* PICK_FRAGMENT_SHADER = R"(
#version 450 core
flat in uint v_object_id;
out uint frag_id;
void main() { frag_id = v_object_id; }
)";

static const char* AXIS_VERTEX_SHADER = R"(
#version 450 core
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;
uniform mat4 u_mvp;
out vec3 v_color;
void main() {
    gl_Position = u_mvp * vec4(a_position, 1.0);
    v_color = a_color;
}
)";

static const char* AXIS_FRAGMENT_SHADER = R"(
#version 450 core
in vec3 v_color;
out vec4 frag_color;
void main() { frag_color = vec4(v_color, 1.0); }
)";

static GLuint compileShader(QOpenGLFunctions_4_5_Core* gl, GLenum type, const char* source) {
    GLuint shader = gl->glCreateShader(type);
    gl->glShaderSource(shader, 1, &source, nullptr);
    gl->glCompileShader(shader);
    GLint ok = 0;
    gl->glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[2048];
        gl->glGetShaderInfoLog(shader, sizeof(log), nullptr, log);
        qWarning("Shader compile error: %s", log);
    }
    return shader;
}

static const char* HIZ_DOWNSAMPLE_VS = R"(
#version 450 core
void main() {
    vec2 pos = vec2((gl_VertexID & 1) * 4.0 - 1.0,
                    (gl_VertexID & 2) * 2.0 - 1.0);
    gl_Position = vec4(pos, 0.0, 1.0);
}
)";

static const char* HIZ_DOWNSAMPLE_FS = R"(
#version 450 core
uniform sampler2D u_depth;
uniform vec2 u_inv_dest_size;
void main() {
    vec2 uv = gl_FragCoord.xy * u_inv_dest_size;
    gl_FragDepth = texture(u_depth, uv).r;
}
)";


static GLuint linkProgram(QOpenGLFunctions_4_5_Core* gl, GLuint vert, GLuint frag) {
    GLuint prog = gl->glCreateProgram();
    gl->glAttachShader(prog, vert);
    gl->glAttachShader(prog, frag);
    gl->glLinkProgram(prog);
    GLint ok = 0;
    gl->glGetProgramiv(prog, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[2048];
        gl->glGetProgramInfoLog(prog, sizeof(log), nullptr, log);
        qWarning("Program link error: %s", log);
    }
    gl->glDeleteShader(vert);
    gl->glDeleteShader(frag);
    return prog;
}

// -----------------------------------------------------------------------------

// Meyer et al. octahedral normal encode.  Input unit vector -> [-1,1]^2.
static void octEncode(const float n[3], float out[2]) {
    float ax = std::fabs(n[0]), ay = std::fabs(n[1]), az = std::fabs(n[2]);
    float denom = ax + ay + az;
    if (denom < 1e-12f) { out[0] = 0.0f; out[1] = 0.0f; return; }
    float px = n[0] / denom;
    float py = n[1] / denom;
    if (n[2] < 0.0f) {
        float sx = px >= 0.0f ? 1.0f : -1.0f;
        float sy = py >= 0.0f ? 1.0f : -1.0f;
        float nx = (1.0f - std::fabs(py)) * sx;
        float ny = (1.0f - std::fabs(px)) * sy;
        px = nx; py = ny;
    }
    out[0] = px;
    out[1] = py;
}

// Quantize a streamer-format vertex (pos3 + normal3 + color-as-float) into
// the 12 B VBO record, given the mesh's tight local AABB.  `extent_recip`
// is 1/(max-min) per axis, or 0 for degenerate axes (quantum becomes 0).
static void quantizeVertex(const float src[7],
                           const float aabb_min[3],
                           const float extent_recip[3],
                           uint8_t dst[INSTANCED_VERTEX_STRIDE_BYTES]) {
    // Position -> u16 normalized.
    uint16_t* p = reinterpret_cast<uint16_t*>(dst + INSTANCED_VERTEX_POS_OFFSET);
    for (int a = 0; a < 3; ++a) {
        float t = (src[a] - aabb_min[a]) * extent_recip[a];
        if (t < 0.0f) t = 0.0f; else if (t > 1.0f) t = 1.0f;
        p[a] = static_cast<uint16_t>(t * 65535.0f + 0.5f);
    }
    // Normal -> oct i8x2.  int8 gives ~1.4° worst-case error — fine for BIM.
    float oct[2];
    octEncode(src + 3, oct);
    int8_t* n = reinterpret_cast<int8_t*>(dst + INSTANCED_VERTEX_NORMAL_OFFSET);
    for (int a = 0; a < 2; ++a) {
        float v = oct[a];
        if (v < -1.0f) v = -1.0f; else if (v > 1.0f) v = 1.0f;
        n[a] = static_cast<int8_t>(std::lrintf(v * 127.0f));
    }
    // Color passes through — streamer packs 4 bytes into the 7th float slot.
    std::memcpy(dst + INSTANCED_VERTEX_COLOR_OFFSET, src + 6, 4);
}

// Determinant of the upper-left 3x3 of a column-major mat4 stored as 16 floats.
// Sign tells us whether the transform contains a reflection, which is what
// decides which glFrontFace winding to draw the instance with.
static bool transformIsReflected(const float t[16]) {
    const float det =
        t[0] * (t[5] * t[10] - t[9] * t[6])
      - t[4] * (t[1] * t[10] - t[9] * t[2])
      + t[8] * (t[1] * t[6]  - t[5] * t[2]);
    return det < 0.0f;
}

static bool aabbInFrustum(const float aabb_min[3], const float aabb_max[3],
                          const float planes[6][4]) {
    for (int p = 0; p < 6; ++p) {
        float px = planes[p][0] >= 0.0f ? aabb_max[0] : aabb_min[0];
        float py = planes[p][1] >= 0.0f ? aabb_max[1] : aabb_min[1];
        float pz = planes[p][2] >= 0.0f ? aabb_max[2] : aabb_min[2];
        float dist = planes[p][0] * px + planes[p][1] * py + planes[p][2] * pz + planes[p][3];
        if (dist < 0.0f) return false;
    }
    return true;
}

static void extractFrustumPlanes(const QMatrix4x4& vp, float planes[6][4]) {
    for (int i = 0; i < 4; ++i) {
        planes[0][i] = vp(3, i) + vp(0, i);
        planes[1][i] = vp(3, i) - vp(0, i);
        planes[2][i] = vp(3, i) + vp(1, i);
        planes[3][i] = vp(3, i) - vp(1, i);
        planes[4][i] = vp(3, i) + vp(2, i);
        planes[5][i] = vp(3, i) - vp(2, i);
    }
    for (int p = 0; p < 6; ++p) {
        float len = std::sqrt(planes[p][0]*planes[p][0] +
                              planes[p][1]*planes[p][1] +
                              planes[p][2]*planes[p][2]);
        if (len > 0.0f) {
            float inv = 1.0f / len;
            planes[p][0] *= inv; planes[p][1] *= inv;
            planes[p][2] *= inv; planes[p][3] *= inv;
        }
    }
}

// Build bvh_items (one per instance, 1:1 ordering) and a per-model BVH.
// Items with instances.size() < BVH_MIN_OBJECTS leave bvh empty — the
// render path falls back to drawing every instance.
static void buildBvhForModel(ModelGpuData& m, uint32_t model_id) {
    m.bvh_items.clear();
    m.bvh_items.reserve(m.instances.size());
    for (const auto& inst : m.instances) {
        BvhItem it;
        std::memcpy(it.aabb_min, inst.world_aabb_min, sizeof(it.aabb_min));
        std::memcpy(it.aabb_max, inst.world_aabb_max, sizeof(it.aabb_max));
        it.model_id = inst.model_id;
        m.bvh_items.push_back(it);
    }
    if (m.bvh_items.size() >= BVH_MIN_OBJECTS) {
        m.bvh = buildModelBvhOne(m.bvh_items, model_id);
    } else {
        m.bvh = ModelBvh{};
    }
}

ViewportWindow::ViewportWindow(QWindow* parent)
    : QWindow(parent)
{
    setSurfaceType(QWindow::OpenGLSurface);

    QSurfaceFormat fmt;
    fmt.setVersion(4, 5);
    fmt.setProfile(QSurfaceFormat::CoreProfile);
    fmt.setDepthBufferSize(24);
    fmt.setSwapBehavior(QSurfaceFormat::DoubleBuffer);
    fmt.setSamples(4);
    setFormat(fmt);

    // Redraw is driven by QEvent::UpdateRequest.  We post one via
    // requestUpdate() from every function that mutates visible state
    // (mouse/wheel, model lifecycle, selection, resize).  When nothing
    // changes — the common case for a static BIM model — we don't burn
    // CPU/GPU redrawing the same frame.  Qt coalesces multiple
    // requestUpdate() calls inside a single vblank.
}

ViewportWindow::~ViewportWindow() {
    if (context_) {
        context_->makeCurrent(this);
        if (gl_) {
            for (auto& [mid, m] : models_gpu_) {
                if (m.vao)  gl_->glDeleteVertexArrays(1, &m.vao);
                if (m.vbo)  gl_->glDeleteBuffers(1, &m.vbo);
                if (m.ebo)  gl_->glDeleteBuffers(1, &m.ebo);
                if (m.ssbo) gl_->glDeleteBuffers(1, &m.ssbo);
                if (m.mesh_info_ssbo) gl_->glDeleteBuffers(1, &m.mesh_info_ssbo);
                if (m.visible_ssbo) gl_->glDeleteBuffers(1, &m.visible_ssbo);
                if (m.indirect_buffer) gl_->glDeleteBuffers(1, &m.indirect_buffer);
            }
            if (axis_vao_)      gl_->glDeleteVertexArrays(1, &axis_vao_);
            if (axis_vbo_)      gl_->glDeleteBuffers(1, &axis_vbo_);
            if (main_program_)  gl_->glDeleteProgram(main_program_);
            if (pick_program_)  gl_->glDeleteProgram(pick_program_);
            if (axis_program_)  gl_->glDeleteProgram(axis_program_);
            if (pick_fbo_)      gl_->glDeleteFramebuffers(1, &pick_fbo_);
            if (pick_color_tex_) gl_->glDeleteTextures(1, &pick_color_tex_);
            if (pick_depth_rbo_) gl_->glDeleteRenderbuffers(1, &pick_depth_rbo_);
            if (hiz_fbo_)         gl_->glDeleteFramebuffers(1, &hiz_fbo_);
            if (hiz_depth_tex_)   gl_->glDeleteTextures(1, &hiz_depth_tex_);
            if (hiz_resolve_fbo_) gl_->glDeleteFramebuffers(1, &hiz_resolve_fbo_);
            if (hiz_resolve_depth_tex_) gl_->glDeleteTextures(1, &hiz_resolve_depth_tex_);
            if (hiz_downsample_program_) gl_->glDeleteProgram(hiz_downsample_program_);
            if (hiz_downsample_vao_) gl_->glDeleteVertexArrays(1, &hiz_downsample_vao_);
        }
        context_->doneCurrent();
    }
}

void ViewportWindow::initGL() {
    if (gl_initialized_) return;

    context_ = new QOpenGLContext(this);
    context_->setFormat(requestedFormat());
    if (!context_->create()) { qFatal("Failed to create OpenGL context"); return; }
    context_->makeCurrent(this);

    gl_ = QOpenGLVersionFunctionsFactory::get<QOpenGLFunctions_4_5_Core>(context_);
    if (!gl_) { qWarning("OpenGL 4.5 not available"); return; }

    buildShaders();
    buildAxisGizmo();

    gl_->glEnable(GL_DEPTH_TEST);
    gl_->glEnable(GL_MULTISAMPLE);
    gl_->glClearColor(0.18f, 0.20f, 0.22f, 1.0f);
    gl_->glCullFace(GL_BACK);
    if (AppSettings::instance().backfaceCulling()) gl_->glEnable(GL_CULL_FACE);
    else                                            gl_->glDisable(GL_CULL_FACE);

    // Hot-toggle cull state when the setting changes.  Queued so we touch GL
    // state only when render() is about to run.
    connect(&AppSettings::instance(), &AppSettings::backfaceCullingChanged,
            this, [this](bool on) {
                if (!gl_initialized_ || !gl_) return;
                context_->makeCurrent(this);
                if (on) gl_->glEnable(GL_CULL_FACE);
                else    gl_->glDisable(GL_CULL_FACE);
                requestUpdate();
            });

    gl_initialized_ = true;
    requestUpdate();

    emit initialized();
}

void ViewportWindow::setupVaoLayout(GLuint vao, GLuint vbo, GLuint ebo) {
    gl_->glVertexArrayVertexBuffer(vao, 0, vbo, 0, INSTANCED_VERTEX_STRIDE_BYTES);
    gl_->glVertexArrayElementBuffer(vao, ebo);

    // position (3 x u16 normalized @ 0)
    gl_->glEnableVertexArrayAttrib(vao, 0);
    gl_->glVertexArrayAttribFormat(vao, 0, 3, GL_UNSIGNED_SHORT, GL_TRUE,
                                   INSTANCED_VERTEX_POS_OFFSET);
    gl_->glVertexArrayAttribBinding(vao, 0, 0);

    // normal oct-encoded (2 x i8 normalized @ 6)
    gl_->glEnableVertexArrayAttrib(vao, 1);
    gl_->glVertexArrayAttribFormat(vao, 1, 2, GL_BYTE, GL_TRUE,
                                   INSTANCED_VERTEX_NORMAL_OFFSET);
    gl_->glVertexArrayAttribBinding(vao, 1, 0);

    // color (4 x u8 normalized @ 8)
    gl_->glEnableVertexArrayAttrib(vao, 2);
    gl_->glVertexArrayAttribFormat(vao, 2, 4, GL_UNSIGNED_BYTE, GL_TRUE,
                                   INSTANCED_VERTEX_COLOR_OFFSET);
    gl_->glVertexArrayAttribBinding(vao, 2, 0);
}

void ViewportWindow::buildShaders() {
    {
        GLuint vs = compileShader(gl_, GL_VERTEX_SHADER, MAIN_VERTEX_SHADER);
        GLuint fs = compileShader(gl_, GL_FRAGMENT_SHADER, MAIN_FRAGMENT_SHADER);
        main_program_ = linkProgram(gl_, vs, fs);
    }
    {
        GLuint vs = compileShader(gl_, GL_VERTEX_SHADER, PICK_VERTEX_SHADER);
        GLuint fs = compileShader(gl_, GL_FRAGMENT_SHADER, PICK_FRAGMENT_SHADER);
        pick_program_ = linkProgram(gl_, vs, fs);
    }
    {
        GLuint vs = compileShader(gl_, GL_VERTEX_SHADER, AXIS_VERTEX_SHADER);
        GLuint fs = compileShader(gl_, GL_FRAGMENT_SHADER, AXIS_FRAGMENT_SHADER);
        axis_program_ = linkProgram(gl_, vs, fs);
    }
    {
        GLuint vs = compileShader(gl_, GL_VERTEX_SHADER, HIZ_DOWNSAMPLE_VS);
        GLuint fs = compileShader(gl_, GL_FRAGMENT_SHADER, HIZ_DOWNSAMPLE_FS);
        hiz_downsample_program_ = linkProgram(gl_, vs, fs);
        gl_->glCreateVertexArrays(1, &hiz_downsample_vao_);
    }
}

void ViewportWindow::buildAxisGizmo() {
    static const float axis_data[] = {
        0,0,0,  1.0f,0.25f,0.25f,
        1,0,0,  1.0f,0.25f,0.25f,
        0,0,0,  0.30f,0.95f,0.30f,
        0,1,0,  0.30f,0.95f,0.30f,
        0,0,0,  0.30f,0.55f,1.0f,
        0,0,1,  0.30f,0.55f,1.0f,
    };
    gl_->glCreateVertexArrays(1, &axis_vao_);
    gl_->glCreateBuffers(1, &axis_vbo_);
    gl_->glNamedBufferStorage(axis_vbo_, sizeof(axis_data), axis_data, 0);
    gl_->glVertexArrayVertexBuffer(axis_vao_, 0, axis_vbo_, 0, 6 * sizeof(float));
    gl_->glEnableVertexArrayAttrib(axis_vao_, 0);
    gl_->glVertexArrayAttribFormat(axis_vao_, 0, 3, GL_FLOAT, GL_FALSE, 0);
    gl_->glVertexArrayAttribBinding(axis_vao_, 0, 0);
    gl_->glEnableVertexArrayAttrib(axis_vao_, 1);
    gl_->glVertexArrayAttribFormat(axis_vao_, 1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float));
    gl_->glVertexArrayAttribBinding(axis_vao_, 1, 0);
}

bool ViewportWindow::growModelVbo(ModelGpuData& m, size_t needed_total) {
    size_t new_capacity = m.vbo_capacity;
    while (new_capacity < needed_total) new_capacity *= 2;
    if (new_capacity > MAX_BUFFER_SIZE) {
        qWarning("VBO grow request (%zu MB) exceeds cap", new_capacity / (1024*1024));
        return false;
    }
    GLuint new_vbo = 0;
    gl_->glCreateBuffers(1, &new_vbo);
    gl_->glNamedBufferStorage(new_vbo, new_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);
    if (m.vbo_used > 0) {
        gl_->glCopyNamedBufferSubData(m.vbo, new_vbo, 0, 0, m.vbo_used);
    }
    gl_->glDeleteBuffers(1, &m.vbo);
    m.vbo = new_vbo;
    m.vbo_capacity = new_capacity;
    gl_->glVertexArrayVertexBuffer(m.vao, 0, m.vbo, 0, INSTANCED_VERTEX_STRIDE_BYTES);
    qInfo("Model VBO grew to %zu MB", m.vbo_capacity / (1024*1024));
    return true;
}

bool ViewportWindow::growModelSsbo(ModelGpuData& m, size_t needed_total) {
    size_t new_capacity = m.ssbo_capacity ? m.ssbo_capacity : INITIAL_SSBO_SIZE;
    while (new_capacity < needed_total) new_capacity *= 2;
    if (new_capacity > MAX_BUFFER_SIZE) {
        qWarning("Instance SSBO grow request (%zu MB) exceeds cap", new_capacity / (1024*1024));
        return false;
    }
    GLuint new_ssbo = 0;
    gl_->glCreateBuffers(1, &new_ssbo);
    gl_->glNamedBufferStorage(new_ssbo, new_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);
    const size_t used = m.ssbo_instance_count * sizeof(InstanceGpu);
    if (m.ssbo && used > 0) {
        gl_->glCopyNamedBufferSubData(m.ssbo, new_ssbo, 0, 0, used);
    }
    if (m.ssbo) gl_->glDeleteBuffers(1, &m.ssbo);
    m.ssbo = new_ssbo;
    m.ssbo_capacity = new_capacity;
    qInfo("Model instance SSBO grew to %zu MB", m.ssbo_capacity / (1024*1024));
    return true;
}

bool ViewportWindow::growModelEbo(ModelGpuData& m, size_t needed_total) {
    size_t new_capacity = m.ebo_capacity;
    while (new_capacity < needed_total) new_capacity *= 2;
    if (new_capacity > MAX_BUFFER_SIZE) {
        qWarning("EBO grow request (%zu MB) exceeds cap", new_capacity / (1024*1024));
        return false;
    }
    GLuint new_ebo = 0;
    gl_->glCreateBuffers(1, &new_ebo);
    gl_->glNamedBufferStorage(new_ebo, new_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);
    if (m.ebo_used > 0) {
        gl_->glCopyNamedBufferSubData(m.ebo, new_ebo, 0, 0, m.ebo_used);
    }
    gl_->glDeleteBuffers(1, &m.ebo);
    m.ebo = new_ebo;
    m.ebo_capacity = new_capacity;
    gl_->glVertexArrayElementBuffer(m.vao, m.ebo);
    qInfo("Model EBO grew to %zu MB", m.ebo_capacity / (1024*1024));
    return true;
}

ModelGpuData& ViewportWindow::getOrCreateModel(uint32_t model_id) {
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) return it->second;

    ModelGpuData m;
    gl_->glCreateVertexArrays(1, &m.vao);
    gl_->glCreateBuffers(1, &m.vbo);
    gl_->glCreateBuffers(1, &m.ebo);

    m.vbo_capacity = INITIAL_VBO_SIZE;
    m.ebo_capacity = INITIAL_EBO_SIZE;
    gl_->glNamedBufferStorage(m.vbo, m.vbo_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);
    gl_->glNamedBufferStorage(m.ebo, m.ebo_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);
    setupVaoLayout(m.vao, m.vbo, m.ebo);

    // Pre-allocate instance SSBO so we can append during streaming.
    gl_->glCreateBuffers(1, &m.ssbo);
    m.ssbo_capacity = INITIAL_SSBO_SIZE;
    gl_->glNamedBufferStorage(m.ssbo, m.ssbo_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);

    return models_gpu_.emplace(model_id, std::move(m)).first->second;
}

void ViewportWindow::uploadMeshChunk(const MeshChunk& chunk) {
    if (!gl_initialized_) return;
    if (chunk.vertices.empty() || chunk.indices.empty()) return;
    context_->makeCurrent(this);

    ModelGpuData& m = getOrCreateModel(chunk.model_id);

    // Streamer format: 7 floats/vertex (pos3 + normal3 + color-as-float).
    const size_t src_stride_floats = 7;
    const size_t n_verts = chunk.vertices.size() / src_stride_floats;

    // Recompute a tight local AABB from the actual vertex positions — the
    // chunk-provided AABB can be slightly loose, which wastes quantization
    // precision.  Also derives the dequant basis we'll ship to the GPU.
    float bmin[3] = {  std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity() };
    float bmax[3] = { -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity() };
    for (size_t i = 0; i < n_verts; ++i) {
        const float* v = chunk.vertices.data() + i * src_stride_floats;
        for (int a = 0; a < 3; ++a) {
            if (v[a] < bmin[a]) bmin[a] = v[a];
            if (v[a] > bmax[a]) bmax[a] = v[a];
        }
    }
    // Degenerate / zero-extent axis: collapse to a single quantum.  The
    // dequant shader will output bmin[a] for every vertex, which is correct.
    float extent_recip[3];
    for (int a = 0; a < 3; ++a) {
        float ext = bmax[a] - bmin[a];
        extent_recip[a] = ext > 0.0f ? 1.0f / ext : 0.0f;
    }

    // Quantize into a scratch buffer sized to the destination layout.
    std::vector<uint8_t> quant(n_verts * INSTANCED_VERTEX_STRIDE_BYTES);
    for (size_t i = 0; i < n_verts; ++i) {
        quantizeVertex(chunk.vertices.data() + i * src_stride_floats,
                       bmin, extent_recip,
                       quant.data() + i * INSTANCED_VERTEX_STRIDE_BYTES);
    }

    const size_t vb_size = quant.size();
    const size_t ib_size = chunk.indices.size() * sizeof(uint32_t);

    if (m.vbo_used + vb_size > m.vbo_capacity) {
        if (!growModelVbo(m, m.vbo_used + vb_size)) return;
    }
    if (m.ebo_used + ib_size > m.ebo_capacity) {
        if (!growModelEbo(m, m.ebo_used + ib_size)) return;
    }

    MeshInfo info;
    info.vbo_byte_offset = static_cast<uint32_t>(m.vbo_used);
    info.vertex_count    = static_cast<uint32_t>(n_verts);
    info.ebo_byte_offset = static_cast<uint32_t>(m.ebo_used);
    info.index_count     = static_cast<uint32_t>(chunk.indices.size());
    for (int a = 0; a < 3; ++a) {
        info.local_aabb_min[a] = bmin[a];
        info.local_aabb_max[a] = bmax[a];
    }
    info.first_instance = 0;
    info.instance_count = 0;

    gl_->glNamedBufferSubData(m.vbo, m.vbo_used, vb_size, quant.data());
    gl_->glNamedBufferSubData(m.ebo, m.ebo_used, ib_size, chunk.indices.data());
    m.vbo_used += vb_size;
    m.ebo_used += ib_size;
    m.vertex_count += info.vertex_count;

    if (m.meshes.size() <= chunk.local_mesh_id) m.meshes.resize(chunk.local_mesh_id + 1);
    m.meshes[chunk.local_mesh_id] = info;

    // Write the matching dequant basis into the MeshGpu SSBO.  Grow on
    // demand; geometrically doubling keeps this amortized O(1) over streaming.
    MeshGpu mg{};
    for (int a = 0; a < 3; ++a) {
        mg.aabb_min[a] = bmin[a];
        mg.aabb_max[a] = bmax[a];
    }
    mg.aabb_min[3] = 0.0f;
    mg.aabb_max[3] = 0.0f;

    const size_t mg_offset = chunk.local_mesh_id * sizeof(MeshGpu);
    if (mg_offset + sizeof(MeshGpu) > m.mesh_info_capacity) {
        size_t new_cap = m.mesh_info_capacity ? m.mesh_info_capacity : 32 * sizeof(MeshGpu);
        while (new_cap < mg_offset + sizeof(MeshGpu)) new_cap *= 2;
        GLuint new_ssbo = 0;
        gl_->glCreateBuffers(1, &new_ssbo);
        gl_->glNamedBufferStorage(new_ssbo, new_cap, nullptr, GL_DYNAMIC_STORAGE_BIT);
        if (m.mesh_info_ssbo && m.mesh_info_capacity > 0) {
            gl_->glCopyNamedBufferSubData(m.mesh_info_ssbo, new_ssbo, 0, 0,
                                          m.mesh_info_capacity);
            gl_->glDeleteBuffers(1, &m.mesh_info_ssbo);
        }
        m.mesh_info_ssbo = new_ssbo;
        m.mesh_info_capacity = new_cap;
    }
    gl_->glNamedBufferSubData(m.mesh_info_ssbo, mg_offset, sizeof(MeshGpu), &mg);
}

void ViewportWindow::uploadInstanceChunk(const InstanceChunk& chunk) {
    if (!gl_initialized_) return;
    context_->makeCurrent(this);

    ModelGpuData& m = getOrCreateModel(chunk.model_id);

    InstanceCpu inst;
    inst.mesh_id  = chunk.local_mesh_id;
    inst.object_id = chunk.object_id;
    inst.color_override_rgba8 = chunk.color_override_rgba8;
    inst.model_id = chunk.model_id;
    std::memcpy(inst.transform,      chunk.transform,      sizeof(inst.transform));
    std::memcpy(inst.world_aabb_min, chunk.world_aabb_min, sizeof(inst.world_aabb_min));
    std::memcpy(inst.world_aabb_max, chunk.world_aabb_max, sizeof(inst.world_aabb_max));
    m.instances.push_back(inst);
    m.instance_reflected.push_back(transformIsReflected(inst.transform) ? 1 : 0);

    // Mirror into bvh_items so the hot cull path (which reads AABBs out of
    // bvh_items even when no BVH has been built yet) stays correct during
    // streaming.  finalizeModel rebuilds the real BVH over these items.
    BvhItem bi;
    std::memcpy(bi.aabb_min, inst.world_aabb_min, sizeof(bi.aabb_min));
    std::memcpy(bi.aabb_max, inst.world_aabb_max, sizeof(bi.aabb_max));
    bi.model_id = inst.model_id;
    m.bvh_items.push_back(bi);

    // Append the GPU record to the instance SSBO so the model is drawable
    // immediately, without waiting for finalizeModel.  The visible-list
    // architecture means SSBO order is irrelevant to correctness.
    InstanceGpu gpu;
    std::memcpy(gpu.transform, inst.transform, sizeof(gpu.transform));
    gpu.object_id = inst.object_id;
    gpu.color_override_rgba8 = inst.color_override_rgba8;
    gpu.mesh_id = inst.mesh_id;
    gpu._pad1 = 0;

    const size_t offset = m.ssbo_instance_count * sizeof(InstanceGpu);
    if (offset + sizeof(InstanceGpu) > m.ssbo_capacity) {
        if (!growModelSsbo(m, offset + sizeof(InstanceGpu))) return;
    }
    gl_->glNamedBufferSubData(m.ssbo, offset, sizeof(InstanceGpu), &gpu);
    m.ssbo_instance_count++;

    if (chunk.local_mesh_id < m.meshes.size()) {
        m.total_triangles += m.meshes[chunk.local_mesh_id].index_count / 3;
    }
    have_cached_cull_ = false;
    requestUpdate();
}

void ViewportWindow::finalizeModel(uint32_t model_id) {
    if (!gl_initialized_) return;
    context_->makeCurrent(this);

    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return;
    ModelGpuData& m = it->second;

    // Instance SSBO has been populated incrementally during streaming, so
    // we don't re-upload here.  What finalize still does:
    //   (1) compute per-mesh instance counts — used by stats and the sidecar
    //       round-trip (first_instance is unused by the visible-list renderer),
    //   (2) build the per-model BVH over instance world AABBs.
    for (auto& mesh : m.meshes) { mesh.first_instance = 0; mesh.instance_count = 0; }
    for (const auto& inst : m.instances) {
        if (inst.mesh_id < m.meshes.size()) ++m.meshes[inst.mesh_id].instance_count;
    }

    buildBvhForModel(m, model_id);

    m.finalized = true;
    have_cached_cull_ = false;
    requestUpdate();

    const size_t ssbo_bytes = m.ssbo_instance_count * sizeof(InstanceGpu);
    qDebug("Model %u finalized: %zu verts, %zu meshes, %zu instances, %.1f MB vram "
           "(vbo %.1f + ebo %.1f + ssbo-used %.1f / %.1f cap)",
           model_id, size_t(m.vertex_count), m.meshes.size(), m.instances.size(),
           (m.vbo_capacity + m.ebo_capacity + m.ssbo_capacity) / (1024.0*1024.0),
           m.vbo_capacity / (1024.0*1024.0),
           m.ebo_capacity / (1024.0*1024.0),
           ssbo_bytes / (1024.0*1024.0),
           m.ssbo_capacity / (1024.0*1024.0));
}

bool ViewportWindow::snapshotModel(uint32_t model_id, SidecarData& out) const {
    auto it = models_gpu_.find(model_id);
    if (!gl_ || it == models_gpu_.end()) return false;
    const auto& m = it->second;
    if (!m.finalized) return false;

    // GPU readback of the packed VBO/EBO ranges actually in use.  VBO is
    // raw bytes at the quantized layout.
    if (m.vbo_used > 0) {
        out.vertices.resize(m.vbo_used);
        gl_->glGetNamedBufferSubData(m.vbo, 0, m.vbo_used, out.vertices.data());
    }
    if (m.ebo_used > 0) {
        out.indices.resize(m.ebo_used / sizeof(uint32_t));
        gl_->glGetNamedBufferSubData(m.ebo, 0, m.ebo_used, out.indices.data());
    }

    out.meshes    = m.meshes;
    out.instances = m.instances;
    return true;
}

void ViewportWindow::applyCachedModel(uint32_t model_id, SidecarData data) {
    if (!gl_initialized_) return;
    context_->makeCurrent(this);

    // Drop any existing state for this model_id.
    auto existing = models_gpu_.find(model_id);
    if (existing != models_gpu_.end()) {
        if (existing->second.vao)  gl_->glDeleteVertexArrays(1, &existing->second.vao);
        if (existing->second.vbo)  gl_->glDeleteBuffers(1, &existing->second.vbo);
        if (existing->second.ebo)  gl_->glDeleteBuffers(1, &existing->second.ebo);
        if (existing->second.ssbo) gl_->glDeleteBuffers(1, &existing->second.ssbo);
        if (existing->second.mesh_info_ssbo) gl_->glDeleteBuffers(1, &existing->second.mesh_info_ssbo);
        if (existing->second.visible_ssbo) gl_->glDeleteBuffers(1, &existing->second.visible_ssbo);
        if (existing->second.indirect_buffer) gl_->glDeleteBuffers(1, &existing->second.indirect_buffer);
        models_gpu_.erase(existing);
    }

    ModelGpuData m;
    gl_->glCreateVertexArrays(1, &m.vao);
    gl_->glCreateBuffers(1, &m.vbo);
    gl_->glCreateBuffers(1, &m.ebo);

    const size_t vb_bytes = data.vertices.size();
    const size_t ib_bytes = data.indices.size()  * sizeof(uint32_t);
    m.vbo_capacity = std::max<size_t>(vb_bytes, 1);
    m.ebo_capacity = std::max<size_t>(ib_bytes, 1);
    gl_->glNamedBufferStorage(m.vbo, m.vbo_capacity,
                              vb_bytes ? data.vertices.data() : nullptr,
                              GL_DYNAMIC_STORAGE_BIT);
    gl_->glNamedBufferStorage(m.ebo, m.ebo_capacity,
                              ib_bytes ? data.indices.data() : nullptr,
                              GL_DYNAMIC_STORAGE_BIT);
    setupVaoLayout(m.vao, m.vbo, m.ebo);

    m.vbo_used = vb_bytes;
    m.ebo_used = ib_bytes;
    m.vertex_count = static_cast<uint32_t>(vb_bytes / INSTANCED_VERTEX_STRIDE_BYTES);
    m.meshes = std::move(data.meshes);
    m.instances = std::move(data.instances);

    uint32_t total_tri = 0;
    for (const auto& mesh : m.meshes) {
        total_tri += (mesh.index_count / 3) * mesh.instance_count;
    }
    m.total_triangles = total_tri;

    // Build and upload the instance SSBO.
    std::vector<InstanceGpu> gpu(m.instances.size());
    for (size_t i = 0; i < m.instances.size(); ++i) {
        const InstanceCpu& src = m.instances[i];
        InstanceGpu& dst = gpu[i];
        std::memcpy(dst.transform, src.transform, sizeof(dst.transform));
        dst.object_id = src.object_id;
        dst.color_override_rgba8 = src.color_override_rgba8;
        dst.mesh_id = src.mesh_id;
        dst._pad1 = 0;
    }
    gl_->glCreateBuffers(1, &m.ssbo);
    const size_t ssbo_bytes = gpu.size() * sizeof(InstanceGpu);
    if (ssbo_bytes > 0) {
        gl_->glNamedBufferStorage(m.ssbo, ssbo_bytes, gpu.data(), 0);
    }
    m.ssbo_instance_count = static_cast<uint32_t>(gpu.size());

    // Build and upload the per-mesh quantization SSBO from cached meshes.
    {
        std::vector<MeshGpu> mesh_gpu(m.meshes.size());
        for (size_t i = 0; i < m.meshes.size(); ++i) {
            for (int a = 0; a < 3; ++a) {
                mesh_gpu[i].aabb_min[a] = m.meshes[i].local_aabb_min[a];
                mesh_gpu[i].aabb_max[a] = m.meshes[i].local_aabb_max[a];
            }
            mesh_gpu[i].aabb_min[3] = 0.0f;
            mesh_gpu[i].aabb_max[3] = 0.0f;
        }
        const size_t mg_bytes = mesh_gpu.size() * sizeof(MeshGpu);
        gl_->glCreateBuffers(1, &m.mesh_info_ssbo);
        if (mg_bytes > 0) {
            gl_->glNamedBufferStorage(m.mesh_info_ssbo, mg_bytes,
                                      mesh_gpu.data(), GL_DYNAMIC_STORAGE_BIT);
            m.mesh_info_capacity = mg_bytes;
        } else {
            gl_->glNamedBufferStorage(m.mesh_info_ssbo, sizeof(MeshGpu),
                                      nullptr, GL_DYNAMIC_STORAGE_BIT);
            m.mesh_info_capacity = sizeof(MeshGpu);
        }
    }

    // Recompute the reflection flag from each instance's transform — the
    // sidecar only caches InstanceCpu, not the parallel reflection flags.
    m.instance_reflected.resize(m.instances.size());
    for (size_t i = 0; i < m.instances.size(); ++i) {
        m.instance_reflected[i] = transformIsReflected(m.instances[i].transform) ? 1 : 0;
    }

    buildBvhForModel(m, model_id);

    m.finalized = true;
    models_gpu_.emplace(model_id, std::move(m));
    have_cached_cull_ = false;
    requestUpdate();

    qDebug("Sidecar apply: model %u  %zu verts, %zu meshes, %zu instances  "
           "%.1f MB vram (vbo %.1f + ebo %.1f + ssbo %.1f)",
           model_id, vb_bytes / INSTANCED_VERTEX_STRIDE_BYTES,
           models_gpu_[model_id].meshes.size(),
           models_gpu_[model_id].instances.size(),
           (vb_bytes + ib_bytes + ssbo_bytes) / (1024.0*1024.0),
           vb_bytes / (1024.0*1024.0),
           ib_bytes / (1024.0*1024.0),
           ssbo_bytes / (1024.0*1024.0));
}

void ViewportWindow::applyLodExtension(uint32_t model_id, const SidecarData& sd) {
    if (!gl_initialized_) return;
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end() || !it->second.finalized) return;
    ModelGpuData& m = it->second;

    const size_t total_ib_bytes = sd.indices.size() * sizeof(uint32_t);
    if (total_ib_bytes <= m.ebo_used) {
        // buildLods didn't add anything; just refresh the meshes vector in
        // case lod1_* fields were touched.
        m.meshes = sd.meshes;
        have_cached_cull_ = false;
        requestUpdate();
        return;
    }

    context_->makeCurrent(this);
    if (total_ib_bytes > m.ebo_capacity) {
        if (!growModelEbo(m, total_ib_bytes)) return;
    }
    const size_t append_bytes = total_ib_bytes - m.ebo_used;
    const uint32_t* appended_src =
        sd.indices.data() + (m.ebo_used / sizeof(uint32_t));
    gl_->glNamedBufferSubData(m.ebo, m.ebo_used, append_bytes, appended_src);
    m.ebo_used = total_ib_bytes;

    // Replace mesh metadata so cullAndUploadVisible sees the new lod1_ fields.
    m.meshes = sd.meshes;
    have_cached_cull_ = false;
    requestUpdate();
}

void ViewportWindow::resetScene() {
    if (!gl_initialized_) return;
    context_->makeCurrent(this);
    for (auto& [mid, m] : models_gpu_) {
        if (m.vao)  gl_->glDeleteVertexArrays(1, &m.vao);
        if (m.vbo)  gl_->glDeleteBuffers(1, &m.vbo);
        if (m.ebo)  gl_->glDeleteBuffers(1, &m.ebo);
        if (m.ssbo) gl_->glDeleteBuffers(1, &m.ssbo);
        if (m.mesh_info_ssbo) gl_->glDeleteBuffers(1, &m.mesh_info_ssbo);
        if (m.visible_ssbo) gl_->glDeleteBuffers(1, &m.visible_ssbo);
        if (m.indirect_buffer) gl_->glDeleteBuffers(1, &m.indirect_buffer);
    }
    models_gpu_.clear();
    selected_object_id_ = 0;
    have_cached_cull_ = false;
    requestUpdate();
}

void ViewportWindow::hideModel(uint32_t model_id) {
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        it->second.hidden = true;
        have_cached_cull_ = false;
        requestUpdate();
    }
}

void ViewportWindow::showModel(uint32_t model_id) {
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        it->second.hidden = false;
        have_cached_cull_ = false;
        requestUpdate();
    }
}

void ViewportWindow::removeModel(uint32_t model_id) {
    if (!gl_initialized_) return;
    context_->makeCurrent(this);
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        if (it->second.vao)  gl_->glDeleteVertexArrays(1, &it->second.vao);
        if (it->second.vbo)  gl_->glDeleteBuffers(1, &it->second.vbo);
        if (it->second.ebo)  gl_->glDeleteBuffers(1, &it->second.ebo);
        if (it->second.ssbo) gl_->glDeleteBuffers(1, &it->second.ssbo);
        if (it->second.mesh_info_ssbo) gl_->glDeleteBuffers(1, &it->second.mesh_info_ssbo);
        if (it->second.visible_ssbo) gl_->glDeleteBuffers(1, &it->second.visible_ssbo);
        if (it->second.indirect_buffer) gl_->glDeleteBuffers(1, &it->second.indirect_buffer);
        models_gpu_.erase(it);
        have_cached_cull_ = false;
        requestUpdate();
    }
}

void ViewportWindow::setSelectedObjectId(uint32_t id) {
    selected_object_id_ = id;
    requestUpdate();
}

void ViewportWindow::setCamera(float tx, float ty, float tz,
                                float dist, float yaw, float pitch) {
    camera_target_ = QVector3D(tx, ty, tz);
    camera_distance_ = dist;
    camera_yaw_ = yaw;
    camera_pitch_ = pitch;
    have_cached_cull_ = false;
    requestUpdate();
}

void ViewportWindow::setBenchmarkFrames(int n) {
    benchmark_total_ = n;
    benchmark_count_ = 0;
    benchmark_warmup_ = 5;
    benchmark_yaw_start_ = camera_yaw_;
    benchmark_frame_times_.clear();
    benchmark_frame_times_.reserve(n);
    requestUpdate();
}

QString ViewportWindow::cameraString() const {
    return QString("%1,%2,%3,%4,%5,%6")
        .arg(camera_target_.x(), 0, 'f', 4)
        .arg(camera_target_.y(), 0, 'f', 4)
        .arg(camera_target_.z(), 0, 'f', 4)
        .arg(camera_distance_, 0, 'f', 4)
        .arg(camera_yaw_, 0, 'f', 2)
        .arg(camera_pitch_, 0, 'f', 2);
}

void ViewportWindow::keyPressEvent(QKeyEvent* event) {
    if (event->key() == Qt::Key_C && !(event->modifiers() & Qt::ControlModifier)) {
        qDebug("--camera %s", qPrintable(cameraString()));
        return;
    }
    QWindow::keyPressEvent(event);
}

// --- HiZ occlusion culling (Phase 3C) -----------------------------------

// Baseline HiZ resolution.  256x128 is enough to cull big occluders
// (walls, slabs) reliably; finer detail doesn't help much because we're
// sampling the pyramid at the mip level where the AABB's rect is ~2
// texels anyway.  Readback cost is ~128 KB/frame ≈ negligible.
// IFC_HIZ_SIZE=<N> overrides the width; height tracks aspect.
static int hizBaseWidth() {
    static const int w = []{
        const char* e = std::getenv("IFC_HIZ_SIZE");
        return (e && *e) ? std::max(64, std::atoi(e)) : 256;
    }();
    return w;
}

static bool hizEnabled() {
    static const bool disabled = []{
        const char* e = std::getenv("IFC_NO_HIZ");
        return e && e[0] == '1';
    }();
    return !disabled;
}

void ViewportWindow::buildHizPyramid() {
    if (!gl_initialized_) return;

    const int win_w = width()  * devicePixelRatio();
    const int win_h = height() * devicePixelRatio();
    if (win_w <= 0 || win_h <= 0) return;

    const int base_w = hizBaseWidth();
    const int base_h = std::max(1, (base_w * win_h) / win_w);

    // Resolve target (full window size, single sample, D24S8 to match Qt's
    // default FBO which uses depth+stencil even when only depth is requested).
    if (win_w != hiz_resolve_w_ || win_h != hiz_resolve_h_) {
        if (hiz_resolve_fbo_)        gl_->glDeleteFramebuffers(1, &hiz_resolve_fbo_);
        if (hiz_resolve_depth_tex_)  gl_->glDeleteTextures(1, &hiz_resolve_depth_tex_);
        gl_->glCreateTextures(GL_TEXTURE_2D, 1, &hiz_resolve_depth_tex_);
        gl_->glTextureStorage2D(hiz_resolve_depth_tex_, 1,
                                GL_DEPTH24_STENCIL8, win_w, win_h);
        gl_->glCreateFramebuffers(1, &hiz_resolve_fbo_);
        gl_->glNamedFramebufferTexture(hiz_resolve_fbo_, GL_DEPTH_STENCIL_ATTACHMENT,
                                       hiz_resolve_depth_tex_, 0);
        hiz_resolve_w_ = win_w;
        hiz_resolve_h_ = win_h;
    }

    if (base_w != hiz_base_w_ || base_h != hiz_base_h_) {
        if (hiz_fbo_)       gl_->glDeleteFramebuffers(1, &hiz_fbo_);
        if (hiz_depth_tex_) gl_->glDeleteTextures(1, &hiz_depth_tex_);
        gl_->glCreateTextures(GL_TEXTURE_2D, 1, &hiz_depth_tex_);
        gl_->glTextureStorage2D(hiz_depth_tex_, 1, GL_DEPTH_COMPONENT24,
                                base_w, base_h);
        gl_->glCreateFramebuffers(1, &hiz_fbo_);
        gl_->glNamedFramebufferTexture(hiz_fbo_, GL_DEPTH_ATTACHMENT,
                                       hiz_depth_tex_, 0);
        gl_->glNamedFramebufferDrawBuffer(hiz_fbo_, GL_NONE);
        gl_->glNamedFramebufferReadBuffer(hiz_fbo_, GL_NONE);
        {
            GLenum s = gl_->glCheckNamedFramebufferStatus(hiz_fbo_, GL_FRAMEBUFFER);
            if (s != GL_FRAMEBUFFER_COMPLETE)
                qWarning("HiZ FBO incomplete: 0x%04x", s);
        }

        hiz_base_w_ = base_w;
        hiz_base_h_ = base_h;
        hiz_depth_readback_.assign(base_w * base_h, 1.0f);

        // Build the mip-offset table.  Level 0 = base_w x base_h.
        hiz_mip_offset_.clear();
        hiz_mip_w_.clear();
        hiz_mip_h_.clear();
        uint32_t off = 0;
        int mw = base_w, mh = base_h;
        while (mw >= 1 && mh >= 1) {
            hiz_mip_offset_.push_back(off);
            hiz_mip_w_.push_back(static_cast<uint32_t>(mw));
            hiz_mip_h_.push_back(static_cast<uint32_t>(mh));
            off += static_cast<uint32_t>(mw) * static_cast<uint32_t>(mh);
            if (mw == 1 && mh == 1) break;
            mw = std::max(1, mw / 2);
            mh = std::max(1, mh / 2);
        }
        hiz_pyramid_.assign(off, 1.0f);
    }

    // Drain stale GL errors before HiZ pipeline.
    while (gl_->glGetError() != GL_NO_ERROR) {}

    // Step 1: MSAA default-fb → full-size SS resolve (same-size blit).
    gl_->glBindFramebuffer(GL_READ_FRAMEBUFFER, 0);
    gl_->glBindFramebuffer(GL_DRAW_FRAMEBUFFER, hiz_resolve_fbo_);
    gl_->glBlitFramebuffer(0, 0, win_w, win_h,
                           0, 0, win_w, win_h,
                           GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT, GL_NEAREST);

    // Step 2: downsample resolved depth to HiZ base via fullscreen-triangle.
    // glBlitFramebuffer with depth + scaling produces GL_INVALID_VALUE on
    // some drivers, so we sample the resolve texture and write gl_FragDepth.
    gl_->glBindFramebuffer(GL_FRAMEBUFFER, hiz_fbo_);
    gl_->glViewport(0, 0, hiz_base_w_, hiz_base_h_);
    gl_->glEnable(GL_DEPTH_TEST);
    gl_->glDepthFunc(GL_ALWAYS);
    gl_->glDepthMask(GL_TRUE);
    gl_->glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE);
    gl_->glUseProgram(hiz_downsample_program_);
    gl_->glTextureParameteri(hiz_resolve_depth_tex_, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    gl_->glTextureParameteri(hiz_resolve_depth_tex_, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    gl_->glTextureParameteri(hiz_resolve_depth_tex_, GL_TEXTURE_COMPARE_MODE, GL_NONE);
    gl_->glBindTextureUnit(0, hiz_resolve_depth_tex_);
    gl_->glUniform1i(gl_->glGetUniformLocation(hiz_downsample_program_, "u_depth"), 0);
    gl_->glUniform2f(gl_->glGetUniformLocation(hiz_downsample_program_, "u_inv_dest_size"),
                     1.0f / static_cast<float>(hiz_base_w_),
                     1.0f / static_cast<float>(hiz_base_h_));
    gl_->glBindVertexArray(hiz_downsample_vao_);
    gl_->glDrawArrays(GL_TRIANGLES, 0, 3);
    gl_->glBindVertexArray(0);
    gl_->glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);
    gl_->glDepthFunc(GL_LESS);
    gl_->glBindFramebuffer(GL_FRAMEBUFFER, 0);
    gl_->glViewport(0, 0, win_w, win_h);

    // Synchronous readback into level 0 of the pyramid.  At 256x128 this
    // is ~128 KB and the driver copy is fast enough not to matter in
    // practice; PBO-ring async was tried and made orbiting flicker worse
    // (2-frame-stale depth vs 1-frame).
    gl_->glGetTextureImage(hiz_depth_tex_, 0, GL_DEPTH_COMPONENT, GL_FLOAT,
                           static_cast<GLsizei>(hiz_depth_readback_.size() * sizeof(float)),
                           hiz_depth_readback_.data());

    {
        static int diag = 5;
        static int skip = 60;
        if (skip > 0) { --skip; }
        else if (diag > 0) {
            --diag;
            float mn = 1.0f, mx = 0.0f;
            int zeros = 0, ones = 0;
            for (size_t i = 0; i < hiz_depth_readback_.size(); ++i) {
                float v = hiz_depth_readback_[i];
                if (v < mn) mn = v;
                if (v > mx) mx = v;
                if (v == 0.0f) ++zeros;
                if (v == 1.0f) ++ones;
            }
            int geom = (int)hiz_depth_readback_.size() - zeros - ones;
            qWarning("HiZ readback %dx%d: min=%.6f max=%.6f zeros=%d ones=%d geom=%d total=%d",
                     hiz_base_w_, hiz_base_h_, mn, mx, zeros, ones, geom,
                     (int)hiz_depth_readback_.size());
        }
    }

    // Copy level 0 into the pyramid, then max-reduce subsequent levels.
    std::memcpy(hiz_pyramid_.data() + hiz_mip_offset_[0],
                hiz_depth_readback_.data(),
                hiz_depth_readback_.size() * sizeof(float));
    for (size_t lvl = 1; lvl < hiz_mip_offset_.size(); ++lvl) {
        const uint32_t pw = hiz_mip_w_[lvl - 1];
        const uint32_t ph = hiz_mip_h_[lvl - 1];
        const uint32_t cw = hiz_mip_w_[lvl];
        const uint32_t ch = hiz_mip_h_[lvl];
        const float* parent = hiz_pyramid_.data() + hiz_mip_offset_[lvl - 1];
        float* child  = hiz_pyramid_.data() + hiz_mip_offset_[lvl];
        for (uint32_t y = 0; y < ch; ++y) {
            const uint32_t py0 = std::min(2 * y,     ph - 1);
            const uint32_t py1 = std::min(2 * y + 1, ph - 1);
            for (uint32_t x = 0; x < cw; ++x) {
                const uint32_t px0 = std::min(2 * x,     pw - 1);
                const uint32_t px1 = std::min(2 * x + 1, pw - 1);
                const float a = parent[py0 * pw + px0];
                const float b = parent[py0 * pw + px1];
                const float c = parent[py1 * pw + px0];
                const float d = parent[py1 * pw + px1];
                child[y * cw + x] = std::max(std::max(a, b), std::max(c, d));
            }
        }
    }

    hiz_vp_ = proj_matrix_ * view_matrix_;
    hiz_vp_valid_ = true;
}

bool ViewportWindow::aabbOccludedByHiz(const float mn[3], const float mx[3]) const {
    if (!hiz_vp_valid_ || hiz_pyramid_.empty()) return false;

    // Project all 8 corners through the HiZ frame's VP (stored last frame).
    // Track NDC min/max over x, y, z.  If any corner has w <= 0, the AABB
    // straddles the near plane and we skip (behaves like "not occluded").
    float sx_min =  std::numeric_limits<float>::infinity();
    float sx_max = -std::numeric_limits<float>::infinity();
    float sy_min =  std::numeric_limits<float>::infinity();
    float sy_max = -std::numeric_limits<float>::infinity();
    float sz_min =  std::numeric_limits<float>::infinity();
    const float* vp = hiz_vp_.constData();  // column-major
    for (int c = 0; c < 8; ++c) {
        const float x = (c & 1) ? mx[0] : mn[0];
        const float y = (c & 2) ? mx[1] : mn[1];
        const float z = (c & 4) ? mx[2] : mn[2];
        const float cx = vp[0]*x + vp[4]*y + vp[8]*z  + vp[12];
        const float cy = vp[1]*x + vp[5]*y + vp[9]*z  + vp[13];
        const float cz = vp[2]*x + vp[6]*y + vp[10]*z + vp[14];
        const float cw = vp[3]*x + vp[7]*y + vp[11]*z + vp[15];
        if (cw <= 1e-4f) return false;  // near-plane straddle
        const float inv = 1.0f / cw;
        const float nx = cx * inv;
        const float ny = cy * inv;
        const float nz = cz * inv;
        if (nx < sx_min) sx_min = nx;  if (nx > sx_max) sx_max = nx;
        if (ny < sy_min) sy_min = ny;  if (ny > sy_max) sy_max = ny;
        if (nz < sz_min) sz_min = nz;
    }

    if (sx_max < -1.0f || sx_min > 1.0f ||
        sy_max < -1.0f || sy_min > 1.0f) return false;
    if (sz_min < -1.0f) return false;

    sx_min = std::max(sx_min, -1.0f);
    sx_max = std::min(sx_max,  1.0f);
    sy_min = std::max(sy_min, -1.0f);
    sy_max = std::min(sy_max,  1.0f);

    const float u_min = 0.5f * (sx_min + 1.0f);
    const float u_max = 0.5f * (sx_max + 1.0f);
    const float v_min = 0.5f * (sy_min + 1.0f);
    const float v_max = 0.5f * (sy_max + 1.0f);
    const float aabb_near_depth = 0.5f * (sz_min + 1.0f);

    // Sample at a fine mip and reject ONLY if every texel agrees the AABB
    // is behind it.  One non-occluding texel → visible, early-out.  Cap
    // iteration to avoid slow queries on large projected rects.
    const int mip = std::min(1, (int)hiz_mip_offset_.size() - 1);
    const uint32_t mw = hiz_mip_w_[mip];
    const uint32_t mh = hiz_mip_h_[mip];
    int x0 = static_cast<int>(std::floor(u_min * mw));
    int x1 = static_cast<int>(std::ceil (u_max * mw));
    int y0 = static_cast<int>(std::floor(v_min * mh));
    int y1 = static_cast<int>(std::ceil (v_max * mh));
    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 > (int)mw) x1 = mw;
    if (y1 > (int)mh) y1 = mh;
    if (x1 <= x0 || y1 <= y0) return false;

    static constexpr int MAX_HIZ_SAMPLES = 64;
    if ((x1 - x0) * (y1 - y0) > MAX_HIZ_SAMPLES) return false;

    const float* level = hiz_pyramid_.data() + hiz_mip_offset_[mip];
    for (int y = y0; y < y1; ++y) {
        const float* row = level + static_cast<size_t>(y) * mw;
        for (int x = x0; x < x1; ++x) {
            if (aabb_near_depth <= row[x]) return false;
        }
    }
    return true;
}

uint32_t ViewportWindow::pickObjectAt(int x, int y) {
    if (!gl_initialized_) return 0;
    context_->makeCurrent(this);

    int w = width() * devicePixelRatio();
    int h = height() * devicePixelRatio();
    if (pick_width_ != w || pick_height_ != h) {
        if (pick_fbo_) gl_->glDeleteFramebuffers(1, &pick_fbo_);
        if (pick_color_tex_) gl_->glDeleteTextures(1, &pick_color_tex_);
        if (pick_depth_rbo_) gl_->glDeleteRenderbuffers(1, &pick_depth_rbo_);
        gl_->glCreateFramebuffers(1, &pick_fbo_);
        gl_->glCreateTextures(GL_TEXTURE_2D, 1, &pick_color_tex_);
        gl_->glTextureStorage2D(pick_color_tex_, 1, GL_R32UI, w, h);
        gl_->glNamedFramebufferTexture(pick_fbo_, GL_COLOR_ATTACHMENT0, pick_color_tex_, 0);
        gl_->glCreateRenderbuffers(1, &pick_depth_rbo_);
        gl_->glNamedRenderbufferStorage(pick_depth_rbo_, GL_DEPTH_COMPONENT24, w, h);
        gl_->glNamedFramebufferRenderbuffer(pick_fbo_, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, pick_depth_rbo_);
        pick_width_ = w;
        pick_height_ = h;
    }

    renderPickPass();

    // The pick pass overwrote each model's visible_ssbo / indirect_buffer with
    // pick-specific cull params (no contribution cull, no HiZ).  Invalidate
    // the cached cull so the next render() rebuilds them with main-render
    // params; otherwise the viewport draws with stale pick-pass buffers and
    // shading looks wrong until the camera moves.
    have_cached_cull_ = false;

    int px = x * devicePixelRatio();
    int py = (height() - y) * devicePixelRatio();
    uint32_t pixel = 0;
    gl_->glGetTextureSubImage(pick_color_tex_, 0, px, py, 0, 1, 1, 1,
                              GL_RED_INTEGER, GL_UNSIGNED_INT, sizeof(pixel), &pixel);
    return pixel;
}

void ViewportWindow::cullAndUploadVisible(ModelGpuData& m, const float planes[6][4],
                                          float focal_px, float min_pixel_radius) {
    cullModelCpu(m, planes, focal_px, min_pixel_radius);
    uploadCullResults(m);
}

void ViewportWindow::cullModelCpu(ModelGpuData& m, const float planes[6][4],
                                  float focal_px, float min_pixel_radius) {
    // Per-mesh scratch, split by winding × LOD.  Winding split lets the draw
    // pass toggle glFrontFace once between two MDI calls so GL_CULL_FACE does
    // the right thing for both.  LOD split means instances that want the
    // decimated mesh go into a different bucket that emits against
    // mesh.lod1_ebo_byte_offset / lod1_index_count.
    QElapsedTimer phase_timer;
    phase_timer.start();

    auto resize_if = [&](std::vector<std::vector<uint32_t>>& v) {
        if (v.size() < m.meshes.size()) v.resize(m.meshes.size());
    };
    resize_if(m.vis_fwd_lod0);
    resize_if(m.vis_fwd_lod1);
    resize_if(m.vis_rev_lod0);
    resize_if(m.vis_rev_lod1);
    for (size_t i = 0; i < m.meshes.size(); ++i) {
        m.vis_fwd_lod0[i].clear();
        m.vis_fwd_lod1[i].clear();
        m.vis_rev_lod0[i].clear();
        m.vis_rev_lod1[i].clear();
    }
    cull_clear_ns_ += phase_timer.nsecsElapsed();
    phase_timer.restart();

    // LOD1 switches in when projected sphere radius (in pixels) drops below
    // this threshold.  Overridable for tuning.  Set to 0 to disable LOD1
    // entirely (always draw LOD0).
    static const float lod1_px_threshold = []{
        const char* e = std::getenv("IFC_LOD1_PX");
        return (e && *e) ? static_cast<float>(std::atof(e)) : 30.0f;
    }();

    // Bounding-sphere contribution test: approximate an AABB by its enclosing
    // sphere (centre = midpoint, radius = half-diagonal).  Project radius to
    // pixels as r_px = focal_px * r / distance (perspective).  Reject if
    // smaller than the threshold.  Returns true when the node/instance
    // should be kept.
    //
    // If the camera is inside the AABB the sphere-radius test would reject
    // by distance going to zero / negative — we handle that by skipping the
    // test whenever the camera lies within an inflated AABB.  Cheap and
    // conservative: never drops things you're standing next to.
    const float cx = camera_eye_.x();
    const float cy = camera_eye_.y();
    const float cz = camera_eye_.z();
    auto contributionPasses = [&](const float mn[3], const float mx[3]) -> bool {
        if (min_pixel_radius <= 0.0f) return true;
        // Camera inside AABB? Always keep.
        if (cx >= mn[0] && cx <= mx[0] &&
            cy >= mn[1] && cy <= mx[1] &&
            cz >= mn[2] && cz <= mx[2]) {
            return true;
        }
        float ex = 0.5f * (mx[0] - mn[0]);
        float ey = 0.5f * (mx[1] - mn[1]);
        float ez = 0.5f * (mx[2] - mn[2]);
        float radius = std::sqrt(ex*ex + ey*ey + ez*ez);
        float dx = 0.5f * (mx[0] + mn[0]) - cx;
        float dy = 0.5f * (mx[1] + mn[1]) - cy;
        float dz = 0.5f * (mx[2] + mn[2]) - cz;
        float dist = std::sqrt(dx*dx + dy*dy + dz*dz);
        // r_px = focal_px * radius / dist; compare r_px >= min_pixel_radius,
        // rearranged to avoid the divide.
        return focal_px * radius >= min_pixel_radius * dist;
    };

    // Returns projected sphere radius in pixels (or +inf when camera is
    // inside the AABB).  Shares the geometry with contributionPasses; this
    // version returns the value so we can also use it for LOD selection.
    auto pixelRadius = [&](const float mn[3], const float mx[3]) -> float {
        if (cx >= mn[0] && cx <= mx[0] &&
            cy >= mn[1] && cy <= mx[1] &&
            cz >= mn[2] && cz <= mx[2]) {
            return std::numeric_limits<float>::infinity();
        }
        float ex = 0.5f * (mx[0] - mn[0]);
        float ey = 0.5f * (mx[1] - mn[1]);
        float ez = 0.5f * (mx[2] - mn[2]);
        float radius = std::sqrt(ex*ex + ey*ey + ez*ez);
        float dx = 0.5f * (mx[0] + mn[0]) - cx;
        float dy = 0.5f * (mx[1] + mn[1]) - cy;
        float dz = 0.5f * (mx[2] + mn[2]) - cz;
        float dist = std::sqrt(dx*dx + dy*dy + dz*dz);
        return dist > 0.0f ? focal_px * radius / dist
                           : std::numeric_limits<float>::infinity();
    };

    // HiZ occlusion is skipped entirely when the pick pass runs
    // (min_pixel_radius == 0 on that path), when the user disables it via
    // env var, or before the first pyramid has been built.
    //
    // Crucially, HiZ is also skipped when the stored VP (hiz_vp_, captured at
    // the end of the previous frame) differs from this frame's VP — i.e.
    // whenever the camera has moved.  The stored depth buffer encodes what
    // was visible from hiz_vp_'s viewpoint; projecting a current-frame AABB
    // through that VP answers "was this occluded LAST frame?", which is only
    // a correct proxy for "is this occluded NOW?" when the camera is static.
    // Orbiting past a wall would otherwise leave objects persistently culled
    // because prior frames' depth buffers only ever contained the wall (the
    // objects behind it were themselves HiZ-culled, never drawn, so never in
    // the buffer — a self-reinforcing feedback loop).  On static views HiZ
    // kicks in after a single frame of lag.
    const QMatrix4x4 current_vp = proj_matrix_ * view_matrix_;
    static const bool hiz_force_motion = []{
        const char* e = std::getenv("IFC_HIZ_MOTION");
        return e && *e && std::atoi(e) != 0;
    }();
    const bool hiz_vp_matches = hiz_vp_valid_
        && (hiz_force_motion || hiz_vp_ == current_vp);
    const bool hiz_on = hizEnabled() && min_pixel_radius > 0.0f && hiz_vp_matches;

    // Hot path: read the AABB from the compact bvh_items array (28 B stride)
    // rather than the wide InstanceCpu (104 B stride).  Most instances fail
    // frustum or contribution, so we want to avoid touching the wider struct
    // until a survivor needs its mesh_id.  This alone turns the cull from
    // cache-miss-per-instance into stream-friendly linear reads.
    auto test_and_push = [&](uint32_t inst_idx) {
        const BvhItem& item = m.bvh_items[inst_idx];
        if (!aabbInFrustum(item.aabb_min, item.aabb_max, planes)) return;
        if (!contributionPasses(item.aabb_min, item.aabb_max)) return;
        if (hiz_on && aabbOccludedByHiz(item.aabb_min, item.aabb_max)) {
            hiz_reject_count_.fetch_add(1, std::memory_order_relaxed);
            return;
        }
        // Survivor — now pay the wide-struct fetch for mesh_id.
        const InstanceCpu& inst = m.instances[inst_idx];
        if (inst.mesh_id >= m.meshes.size()) return;
        const MeshInfo& mesh = m.meshes[inst.mesh_id];
        const bool want_lod1 = mesh.lod1_index_count > 0 &&
            lod1_px_threshold > 0.0f &&
            pixelRadius(item.aabb_min, item.aabb_max) < lod1_px_threshold;
        const bool reflected = inst_idx < m.instance_reflected.size()
            && m.instance_reflected[inst_idx] != 0;
        auto& bucket =
            reflected ? (want_lod1 ? m.vis_rev_lod1
                                   : m.vis_rev_lod0)
                      : (want_lod1 ? m.vis_fwd_lod1
                                   : m.vis_fwd_lod0);
        bucket[inst.mesh_id].push_back(inst_idx);
    };

    if (!m.bvh.nodes.empty()) {
        uint32_t stack[64];
        int sp = 0;
        stack[sp++] = 0;
        while (sp > 0) {
            uint32_t ni = stack[--sp];
            const BvhNode& n = m.bvh.nodes[ni];
            if (!aabbInFrustum(n.aabb_min, n.aabb_max, planes)) continue;
            // Contribution cull the whole subtree: if the node's enclosing
            // sphere is below threshold, every child is too.
            if (!contributionPasses(n.aabb_min, n.aabb_max)) continue;
            // HiZ cull the whole subtree: if the node AABB is fully
            // occluded, every leaf is too.  The conservative test (AABB
            // near-depth vs max pyramid depth) never rejects a visible
            // parent wrongly even when some children could have peeked
            // through.
            if (hiz_on && aabbOccludedByHiz(n.aabb_min, n.aabb_max)) continue;
            if (n.count > 0) {
                for (uint32_t k = 0; k < n.count; ++k) {
                    uint32_t item_idx = m.bvh.item_indices[n.right_or_first + k];
                    test_and_push(item_idx);
                }
            } else {
                // Left child = ni + 1, right child = n.right_or_first.
                // Push right first so left is popped next (DFS order).
                if (sp + 2 <= 64) {
                    stack[sp++] = n.right_or_first;
                    stack[sp++] = ni + 1;
                }
            }
        }
    } else {
        for (uint32_t i = 0; i < m.instances.size(); ++i) test_and_push(i);
    }
    cull_traverse_ns_ += phase_timer.nsecsElapsed();
    phase_timer.restart();

    // Flatten fwd-slice first (LOD0 then LOD1), then rev-slice (ditto), into
    // visible_flat_.  Commands for the fwd slice fill [0, indirect_forward_count),
    // rev fills [indirect_forward_count, end).  LOD0/LOD1 within a winding
    // slice are contiguous — winding is what requires glFrontFace to flip
    // between MDI calls, LOD is not.
    m.visible_flat.clear();
    m.indirect_scratch.clear();

    auto emit_slice = [&](std::vector<std::vector<uint32_t>>& by_mesh, int lod) {
        for (size_t mi = 0; mi < m.meshes.size(); ++mi) {
            const auto& mesh = m.meshes[mi];
            const uint32_t vis_count = static_cast<uint32_t>(by_mesh[mi].size());
            const uint32_t idx_count =
                (lod == 1) ? mesh.lod1_index_count : mesh.index_count;
            const uint32_t ebo_off =
                (lod == 1) ? mesh.lod1_ebo_byte_offset : mesh.ebo_byte_offset;
            if (vis_count == 0 || idx_count == 0) continue;

            DrawElementsIndirectCommand cmd;
            cmd.count         = idx_count;
            cmd.instanceCount = vis_count;
            cmd.firstIndex    = ebo_off / sizeof(uint32_t);
            cmd.baseVertex    = mesh.vbo_byte_offset / INSTANCED_VERTEX_STRIDE_BYTES;
            cmd.baseInstance  = static_cast<uint32_t>(m.visible_flat.size());
            m.indirect_scratch.push_back(cmd);

            m.visible_flat.insert(m.visible_flat.end(),
                                  by_mesh[mi].begin(), by_mesh[mi].end());
        }
    };

    emit_slice(m.vis_fwd_lod0, 0);
    emit_slice(m.vis_fwd_lod1, 1);
    m.indirect_forward_count = static_cast<uint32_t>(m.indirect_scratch.size());
    emit_slice(m.vis_rev_lod0, 0);
    emit_slice(m.vis_rev_lod1, 1);
    m.indirect_command_count = static_cast<uint32_t>(m.indirect_scratch.size());

    // Per-model stats snapshot — summed into the frame counters regardless
    // of whether this frame ran a full cull or reused the cached one.
    uint32_t model_vis_obj = 0, model_vis_tri = 0;
    for (const auto& cmd : m.indirect_scratch) {
        model_vis_tri += (cmd.count / 3) * cmd.instanceCount;
        model_vis_obj += cmd.instanceCount;
    }
    m.cached_visible_objects   = model_vis_obj;
    m.cached_visible_triangles = model_vis_tri;

    cull_emit_ns_ += phase_timer.nsecsElapsed();
}

void ViewportWindow::uploadCullResults(ModelGpuData& m) {
    QElapsedTimer phase_timer;
    phase_timer.start();

    // Upload visible list (keep binding alive even when empty).
    size_t vis_bytes = std::max<size_t>(m.visible_flat.size() * sizeof(uint32_t),
                                        sizeof(uint32_t));
    if (m.visible_ssbo == 0 || m.visible_ssbo_capacity < vis_bytes) {
        if (m.visible_ssbo) gl_->glDeleteBuffers(1, &m.visible_ssbo);
        size_t new_cap = m.visible_ssbo_capacity ? m.visible_ssbo_capacity : 4096;
        while (new_cap < vis_bytes) new_cap *= 2;
        gl_->glCreateBuffers(1, &m.visible_ssbo);
        gl_->glNamedBufferStorage(m.visible_ssbo, new_cap, nullptr, GL_DYNAMIC_STORAGE_BIT);
        m.visible_ssbo_capacity = new_cap;
    }
    if (!m.visible_flat.empty()) {
        gl_->glNamedBufferSubData(m.visible_ssbo, 0,
            m.visible_flat.size() * sizeof(uint32_t), m.visible_flat.data());
    }

    // Upload indirect command buffer.
    size_t ind_bytes = m.indirect_scratch.size() * sizeof(DrawElementsIndirectCommand);
    if (ind_bytes == 0) {
        cull_upload_ns_ += phase_timer.nsecsElapsed();
        return;
    }
    if (m.indirect_buffer == 0 || m.indirect_capacity < ind_bytes) {
        if (m.indirect_buffer) gl_->glDeleteBuffers(1, &m.indirect_buffer);
        size_t new_cap = m.indirect_capacity ? m.indirect_capacity : 4096;
        while (new_cap < ind_bytes) new_cap *= 2;
        gl_->glCreateBuffers(1, &m.indirect_buffer);
        gl_->glNamedBufferStorage(m.indirect_buffer, new_cap, nullptr, GL_DYNAMIC_STORAGE_BIT);
        m.indirect_capacity = new_cap;
    }
    gl_->glNamedBufferSubData(m.indirect_buffer, 0, ind_bytes, m.indirect_scratch.data());
    cull_upload_ns_ += phase_timer.nsecsElapsed();
}

void ViewportWindow::updateCamera() {
    float yaw_rad = qDegreesToRadians(camera_yaw_);
    float pitch_rad = qDegreesToRadians(camera_pitch_);
    QVector3D eye;
    eye.setX(camera_target_.x() + camera_distance_ * cosf(pitch_rad) * cosf(yaw_rad));
    eye.setY(camera_target_.y() + camera_distance_ * cosf(pitch_rad) * sinf(yaw_rad));
    eye.setZ(camera_target_.z() + camera_distance_ * sinf(pitch_rad));
    camera_eye_ = eye;
    view_matrix_.setToIdentity();
    view_matrix_.lookAt(eye, camera_target_, QVector3D(0, 0, 1));
    proj_matrix_.setToIdentity();
    float aspect = width() > 0 ? float(width()) / float(height()) : 1.0f;
    proj_matrix_.perspective(camera_fov_y_deg_, aspect, 0.1f, camera_distance_ * 10.0f);
}

void ViewportWindow::render() {
    if (!gl_initialized_ || !isExposed()) return;

    QElapsedTimer frame_cost_clock;
    frame_cost_clock.start();

    context_->makeCurrent(this);
    updateCamera();

    int w = width()  * devicePixelRatio();
    int h = height() * devicePixelRatio();
    gl_->glViewport(0, 0, w, h);
    gl_->glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    QMatrix4x4 vp = proj_matrix_ * view_matrix_;
    float planes[6][4];
    extractFrustumPlanes(vp, planes);

    // Pixels-per-radian vertical focal length.  Combined with per-instance
    // world-space radius this gives screen-space pixel size for contribution
    // culling below.
    const float focal_px = 0.5f * static_cast<float>(h) /
        std::tan(qDegreesToRadians(0.5f * camera_fov_y_deg_));
    static const float base_min_pixel_radius = []{
        const char* e = std::getenv("IFC_MIN_PX");
        return (e && *e) ? static_cast<float>(std::atof(e)) : 2.0f;
    }();
    static const float motion_min_pixel_radius = []{
        const char* e = std::getenv("IFC_MIN_PX_MOTION");
        return (e && *e) ? static_cast<float>(std::atof(e))
                         : 0.0f;  // 0 = disabled (no motion boost)
    }();

    gl_->glUseProgram(main_program_);
    GLint u_vp        = gl_->glGetUniformLocation(main_program_, "u_view_projection");
    GLint u_light     = gl_->glGetUniformLocation(main_program_, "u_light_dir");
    GLint u_sel       = gl_->glGetUniformLocation(main_program_, "u_selected_id");
    gl_->glUniformMatrix4fv(u_vp, 1, GL_FALSE, vp.constData());
    gl_->glUniform3f(u_light, 0.3f, 0.5f, 0.8f);
    gl_->glUniform1ui(u_sel, selected_object_id_);

    visible_triangles_ = 0;
    visible_objects_ = 0;
    gl_draw_calls_ = 0;
    indirect_sub_draws_ = 0;
    // Only reset hiz_reject_count_ on frames where we actually re-cull;
    // otherwise we'd wipe the previous cull's number and print 0 every
    // still frame.  See the cull_this_frame branch below.

    // Decide whether this frame's view+scene is identical to the last
    // successful cull.  If so the per-model indirect buffers / visible
    // SSBOs are still valid — we just re-issue the draws from them and
    // skip the expensive cull traversal entirely.
    const bool camera_unchanged = have_cached_cull_
        && last_cull_view_ == view_matrix_
        && last_cull_proj_ == proj_matrix_;
    const bool camera_moving = !camera_unchanged;
    const bool use_motion_threshold = camera_moving
        && motion_min_pixel_radius > base_min_pixel_radius;
    // Force a re-cull on the first still frame after motion so we
    // restore the base contribution threshold and clear stale HiZ.
    const bool needs_settle_recull = !camera_moving
        && last_cull_was_motion_;
    const bool cull_this_frame = camera_moving || needs_settle_recull;
    // Invalidate HiZ on the settle frame: the pyramid was built from the
    // motion frame's sparse depth (aggressive threshold hid objects whose
    // depth would normally populate the pyramid), causing false occlusion.
    if (needs_settle_recull)
        hiz_vp_valid_ = false;
    const float min_pixel_radius = use_motion_threshold
        ? motion_min_pixel_radius : base_min_pixel_radius;
    if (cull_this_frame) {
        hiz_reject_count_.store(0, std::memory_order_relaxed);
        last_cull_was_motion_ = camera_moving;
    } else {
        ++cull_skipped_frames_;
    }

    // Start each frame with CCW-is-front; the two-pass draw below flips
    // back and forth.  Harmless when culling is off.
    gl_->glFrontFace(GL_CCW);

    static const bool mt_cull_enabled = []{
        const char* e = std::getenv("IFC_CULL_THREADS");
        return !(e && e[0] == '0');
    }();

    QElapsedTimer cull_wall_timer;
    if (cull_this_frame) {
        cull_wall_timer.start();
        std::vector<ModelGpuData*> cull_targets;
        cull_targets.reserve(models_gpu_.size());
        for (auto& [mid, m] : models_gpu_) {
            if (m.hidden || !m.ssbo || m.ssbo_instance_count == 0) continue;
            cull_targets.push_back(&m);
        }

        if (mt_cull_enabled && cull_targets.size() > 1) {
            std::vector<std::future<void>> futs;
            futs.reserve(cull_targets.size());
            for (ModelGpuData* mp : cull_targets) {
                const float mpr = min_pixel_radius;
                futs.emplace_back(std::async(std::launch::async,
                    [this, mp, &planes, focal_px, mpr]() {
                        cullModelCpu(*mp, planes, focal_px, mpr);
                    }));
            }
            for (auto& f : futs) f.get();
        } else {
            for (ModelGpuData* mp : cull_targets) {
                cullModelCpu(*mp, planes, focal_px, min_pixel_radius);
            }
        }

        cull_wall_ns_ += cull_wall_timer.nsecsElapsed();
    }

    for (auto& [model_id, m] : models_gpu_) {
        if (m.hidden || !m.ssbo || m.ssbo_instance_count == 0) continue;

        if (cull_this_frame) {
            uploadCullResults(m);
        }
        if (m.indirect_command_count == 0) continue;

        gl_->glBindVertexArray(m.vao);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, m.ssbo);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, m.visible_ssbo);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, m.mesh_info_ssbo);
        gl_->glBindBuffer(GL_DRAW_INDIRECT_BUFFER, m.indirect_buffer);

        uint32_t fwd = m.indirect_forward_count;
        uint32_t rev = m.indirect_command_count - fwd;
        // Perf diagnostics (confirmed 2026-04 on GTX 1650 @ 128M tris:
        // draw-bound, not upload-bound — see README Phase 3):
        //   IFC_SKIP_MDI=1         skip the actual MDI draws (keeps cull +
        //                          upload + binds).  FPS jump == draw-bound.
        //   IFC_MAX_SUBDRAWS=N     truncate drawcount to N per MDI.  Lets
        //                          you distinguish per-subdraw command-
        //                          processor overhead from raw tri work.
        static const bool skip_mdi = []{
            const char* e = std::getenv("IFC_SKIP_MDI");
            return e && e[0] == '1';
        }();
        static const uint32_t max_subdraws = []{
            const char* e = std::getenv("IFC_MAX_SUBDRAWS");
            return (e && *e) ? static_cast<uint32_t>(std::atoi(e))
                             : std::numeric_limits<uint32_t>::max();
        }();
        if (max_subdraws < m.indirect_command_count) {
            // Keep the fwd/rev ratio so the workload mix is preserved.
            const uint32_t total = m.indirect_command_count;
            fwd = static_cast<uint32_t>((uint64_t)fwd * max_subdraws / total);
            rev = max_subdraws - fwd;
        }
        // Forward pass: non-reflected instances, standard CCW winding.
        if (fwd > 0 && !skip_mdi) {
            gl_->glFrontFace(GL_CCW);
            gl_->glMultiDrawElementsIndirect(
                GL_TRIANGLES, GL_UNSIGNED_INT, nullptr,
                static_cast<GLsizei>(fwd), 0);
            ++gl_draw_calls_;
        }
        // Reverse pass: reflected instances — their world-space winding is
        // flipped, so telling GL the front is CW keeps cull-back working.
        if (rev > 0 && !skip_mdi) {
            gl_->glFrontFace(GL_CW);
            gl_->glMultiDrawElementsIndirect(
                GL_TRIANGLES, GL_UNSIGNED_INT,
                reinterpret_cast<const void*>(m.indirect_forward_count * sizeof(DrawElementsIndirectCommand)),
                static_cast<GLsizei>(rev), 0);
            ++gl_draw_calls_;
            gl_->glFrontFace(GL_CCW);
        }

        visible_triangles_  += m.cached_visible_triangles;
        visible_objects_    += m.cached_visible_objects;
        indirect_sub_draws_ += m.indirect_command_count;
    }
    if (cull_this_frame) {
        last_cull_view_     = view_matrix_;
        last_cull_proj_     = proj_matrix_;
        have_cached_cull_   = true;
    }
    if (needs_settle_recull)
        qDebug("[motion-cull] settle result: obj=%u sub_draws=%u hiz_rej=%u",
               visible_objects_, indirect_sub_draws_,
               hiz_reject_count_.load());
    gl_->glBindBuffer(GL_DRAW_INDIRECT_BUFFER, 0);

    renderAxisGizmo();

    // Build HiZ from this frame's resolved depth for next frame's cull.
    // Synchronous glReadPixels inside — cost ~0.5 ms at 256x128 on a
    // mid-range dGPU.  Skippable via IFC_NO_HIZ=1.  Also skipped on
    // still frames: if we didn't re-cull, the depth buffer is
    // bit-identical to the one we already turned into a pyramid.
    if (hizEnabled() && cull_this_frame) {
        buildHizPyramid();
    }

    context_->swapBuffers(this);

    // Ensure one more frame runs after the last motion frame so the
    // settle recull can detect the camera has stopped and restore the
    // base contribution threshold.
    if (last_cull_was_motion_)
        requestUpdate();

    // Measure frame *cost* (time spent inside render()) rather than the
    // wall-clock gap between frames.  With event-driven rendering, idle gaps
    // between requestUpdate() calls would otherwise pollute the FPS window.
    // Reported fps = "if I rendered continuously, this is the rate I'd hit",
    // which is what profiling actually wants.
    const float frame_cost_s = frame_cost_clock.nsecsElapsed() * 1e-9f;

    if (benchmark_total_ > 0) {
        camera_yaw_ += benchmark_yaw_speed_;
        have_cached_cull_ = false;

        if (benchmark_warmup_ > 0) {
            --benchmark_warmup_;
        } else {
            benchmark_frame_times_.push_back(frame_cost_s * 1000.0f);
            ++benchmark_count_;
        }
        if (benchmark_count_ >= benchmark_total_) {
            std::sort(benchmark_frame_times_.begin(), benchmark_frame_times_.end());
            float sum = 0.0f;
            for (float t : benchmark_frame_times_) sum += t;
            float avg = sum / benchmark_frame_times_.size();
            float median = benchmark_frame_times_[benchmark_frame_times_.size() / 2];
            float p1  = benchmark_frame_times_[(size_t)(benchmark_frame_times_.size() * 0.01f)];
            float p99 = benchmark_frame_times_[(size_t)(benchmark_frame_times_.size() * 0.99f)];
            float total_arc = benchmark_yaw_speed_ * (benchmark_total_ + 5);
            qDebug("\n=== BENCHMARK (%d frames, orbit %.0f° at %.1f°/frame) ===",
                   benchmark_total_, total_arc, benchmark_yaw_speed_);
            qDebug("  avg: %.2f ms (%.1f fps)", avg, 1000.0f / avg);
            qDebug("  median: %.2f ms (%.1f fps)", median, 1000.0f / median);
            qDebug("  p1: %.2f ms  p99: %.2f ms", p1, p99);
            qDebug("  last frame: obj %u  tri %u  sub_draws %u  hiz_rej %u",
                   visible_objects_, visible_triangles_,
                   indirect_sub_draws_,
                   hiz_reject_count_.load());
            qDebug("=== END BENCHMARK ===\n");
            QCoreApplication::quit();
            return;
        }
        requestUpdate();
    }

    accumulated_time_ += frame_cost_s;
    frame_count_++;
    if (accumulated_time_ >= 1.0f) {
        last_fps_ = static_cast<float>(frame_count_) / accumulated_time_;
        const uint32_t frames_in_window = static_cast<uint32_t>(frame_count_);
        frame_count_ = 0;
        accumulated_time_ = 0.0f;

        uint32_t total_obj = 0, total_tri = 0, total_meshes = 0;
        size_t total_vbo = 0, total_ebo = 0, total_ssbo = 0;
        size_t num_models = 0, num_hidden = 0;
        for (const auto& [mid, mm] : models_gpu_) {
            num_models++;
            if (mm.hidden) { num_hidden++; continue; }
            total_obj += static_cast<uint32_t>(mm.instances.size());
            total_tri += mm.total_triangles;
            total_meshes += static_cast<uint32_t>(mm.meshes.size());
            total_vbo += mm.vbo_capacity;
            total_ebo += mm.ebo_capacity;
            total_ssbo += mm.ssbo_instance_count * sizeof(InstanceGpu);
        }

        FrameStats stats;
        stats.fps = last_fps_;
        stats.frame_time_ms = 1000.0f / last_fps_;
        stats.total_objects = total_obj;
        stats.visible_objects = visible_objects_;
        stats.total_triangles = total_tri;
        stats.visible_triangles = visible_triangles_;
        stats.unique_meshes = total_meshes;
        stats.gl_draw_calls = gl_draw_calls_;
        stats.indirect_sub_draws = indirect_sub_draws_;
        emit frameStatsUpdated(stats);

        const double inv_frames = frames_in_window > 0
            ? 1.0 / static_cast<double>(frames_in_window) : 0.0;
        const double clr_ms = cull_clear_ns_.load()    * 1e-6 * inv_frames;
        const double trv_ms = cull_traverse_ns_.load() * 1e-6 * inv_frames;
        const double emt_ms = cull_emit_ns_.load()     * 1e-6 * inv_frames;
        const double upl_ms = cull_upload_ns_.load()   * 1e-6 * inv_frames;
        const double wall_ms = cull_wall_ns_           * 1e-6 * inv_frames;
        cull_clear_ns_.store(0);
        cull_traverse_ns_.store(0);
        cull_emit_ns_.store(0);
        cull_upload_ns_.store(0);
        cull_wall_ns_ = 0;
        const uint32_t skipped = cull_skipped_frames_;
        cull_skipped_frames_ = 0;

        qDebug("[frame] %.1f fps  %.2f ms  obj %u/%u  tri %u/%u  "
               "meshes %u  gl_draws %u  sub_draws %u  hiz_rej %u  "
               "cull[wall %.2f | work: clr %.2f trv %.2f emt %.2f upl %.2f]ms  skipped %u/%u  "
               "vram %.1f MB (vbo %.1f + ebo %.1f + ssbo %.1f)  models %zu (%zu hidden)",
               last_fps_, 1000.0f / last_fps_,
               visible_objects_, total_obj,
               visible_triangles_, total_tri,
               total_meshes, gl_draw_calls_, indirect_sub_draws_,
               hiz_reject_count_.load(),
               wall_ms, clr_ms, trv_ms, emt_ms, upl_ms,
               skipped, frames_in_window,
               (total_vbo + total_ebo + total_ssbo) / (1024.0*1024.0),
               total_vbo / (1024.0*1024.0),
               total_ebo / (1024.0*1024.0),
               total_ssbo / (1024.0*1024.0),
               num_models, num_hidden);

        // One-shot sub_draw composition diagnostic.
        static const bool subdraw_diag = std::getenv("IFC_SUBDRAW_DIAG") != nullptr;
        if (subdraw_diag) {
            uint32_t total_subdraws = 0;
            uint32_t hist[8] = {};
            uint32_t instances_in_bucket[8] = {};
            uint32_t tris_in_bucket[8] = {};

            struct ModelStats {
                uint32_t model_id;
                uint32_t subdraws;
                uint32_t single_instance;
                uint32_t total_meshes;
                uint32_t total_instances;
            };
            std::vector<ModelStats> per_model;

            auto bucket_idx = [](uint32_t ic) -> int {
                if (ic <= 1) return 0;
                if (ic <= 2) return 1;
                if (ic <= 4) return 2;
                if (ic <= 8) return 3;
                if (ic <= 16) return 4;
                if (ic <= 64) return 5;
                if (ic <= 256) return 6;
                return 7;
            };

            // --- Mesh-level consolidation analysis ---
            // Per mesh_id, count visible instances across all 4 buckets.
            // Also count how many buckets each mesh_id appears in.
            uint32_t unique_visible_meshes = 0;
            uint32_t meshes_truly_single = 0;   // 1 instance total, 1 bucket
            uint32_t meshes_split_by_state = 0; // >1 bucket but each has 1 instance
            uint32_t subdraws_if_merged_buckets = 0; // sub_draws if winding+LOD ignored
            uint32_t mesh_vis_hist[8] = {};     // histogram of per-mesh visible instance counts

            for (const auto& [mid, mm] : models_gpu_) {
                if (mm.hidden) continue;
                ModelStats ms{mid, mm.indirect_command_count, 0,
                              static_cast<uint32_t>(mm.meshes.size()),
                              static_cast<uint32_t>(mm.instances.size())};
                for (const auto& cmd : mm.indirect_scratch) {
                    int b = bucket_idx(cmd.instanceCount);
                    hist[b]++;
                    instances_in_bucket[b] += cmd.instanceCount;
                    tris_in_bucket[b] += (cmd.count / 3) * cmd.instanceCount;
                    if (cmd.instanceCount == 1) ms.single_instance++;
                    total_subdraws++;
                }
                per_model.push_back(ms);

                const size_t nm = mm.meshes.size();
                for (size_t mi = 0; mi < nm; ++mi) {
                    uint32_t total_vis = 0;
                    uint32_t buckets_present = 0;
                    auto count_bucket = [&](const std::vector<std::vector<uint32_t>>& v) {
                        if (mi < v.size() && !v[mi].empty()) {
                            total_vis += static_cast<uint32_t>(v[mi].size());
                            buckets_present++;
                        }
                    };
                    count_bucket(mm.vis_fwd_lod0);
                    count_bucket(mm.vis_fwd_lod1);
                    count_bucket(mm.vis_rev_lod0);
                    count_bucket(mm.vis_rev_lod1);
                    if (total_vis == 0) continue;

                    unique_visible_meshes++;
                    mesh_vis_hist[bucket_idx(total_vis)]++;
                    if (total_vis > 0) subdraws_if_merged_buckets++;

                    if (total_vis == 1 && buckets_present == 1)
                        meshes_truly_single++;
                    else if (buckets_present > 1) {
                        bool all_single = true;
                        auto check = [&](const std::vector<std::vector<uint32_t>>& v) {
                            if (mi < v.size() && v[mi].size() > 1) all_single = false;
                        };
                        check(mm.vis_fwd_lod0); check(mm.vis_fwd_lod1);
                        check(mm.vis_rev_lod0); check(mm.vis_rev_lod1);
                        if (all_single) meshes_split_by_state++;
                    }
                }
            }

            qDebug("\n=== SUB_DRAW COMPOSITION (this frame) ===");
            qDebug("Total sub_draws: %u", total_subdraws);
            const char* labels[] = {"    1", "    2", "  3-4", "  5-8",
                                    " 9-16", "17-64", "65-256", " 257+"};
            qDebug("instanceCount histogram:");
            qDebug("  range     | sub_draws | instances  | triangles");
            for (int i = 0; i < 8; ++i) {
                if (hist[i] == 0) continue;
                qDebug("  %s   | %7u   | %9u  | %10u",
                       labels[i], hist[i], instances_in_bucket[i], tris_in_bucket[i]);
            }

            uint32_t single = hist[0], small = hist[0] + hist[1] + hist[2];
            qDebug("Single-instance sub_draws: %u (%.1f%%)",
                   single, total_subdraws ? 100.0 * single / total_subdraws : 0.0);
            qDebug("Small (<=4) sub_draws:     %u (%.1f%%)",
                   small, total_subdraws ? 100.0 * small / total_subdraws : 0.0);

            qDebug("\n--- MESH-LEVEL CONSOLIDATION ---");
            qDebug("Unique visible mesh IDs: %u", unique_visible_meshes);
            qDebug("Visible instance count per mesh_id:");
            qDebug("  range     | mesh_ids");
            for (int i = 0; i < 8; ++i) {
                if (mesh_vis_hist[i] == 0) continue;
                qDebug("  %s   | %7u", labels[i], mesh_vis_hist[i]);
            }

            qDebug("\nAmong single-instance sub_draws (%u):", single);
            qDebug("  Truly unique (1 inst, 1 bucket):     %u", meshes_truly_single);
            qDebug("  Split by state (>1 bucket, each =1): %u  (saves %u sub_draws if merged)",
                   meshes_split_by_state, meshes_split_by_state);

            qDebug("\nEstimated sub_draws by grouping strategy:");
            qDebug("  Current (mesh_id x winding x LOD):   %u", total_subdraws);
            qDebug("  Merged buckets (mesh_id only):        %u  (%.0f%% reduction)",
                   subdraws_if_merged_buckets,
                   total_subdraws ? 100.0 * (1.0 - (double)subdraws_if_merged_buckets / total_subdraws) : 0.0);

            std::sort(per_model.begin(), per_model.end(),
                      [](const ModelStats& a, const ModelStats& b) {
                          return a.subdraws > b.subdraws;
                      });
            qDebug("\nTop 15 models by sub_draw count:");
            qDebug("  model_id | sub_draws | single_inst | meshes   | instances");
            for (size_t i = 0; i < std::min<size_t>(15, per_model.size()); ++i) {
                const auto& ms = per_model[i];
                qDebug("  %7u  | %7u   | %7u     | %7u  | %7u",
                       ms.model_id, ms.subdraws, ms.single_instance,
                       ms.total_meshes, ms.total_instances);
            }
            qDebug("=== END SUB_DRAW COMPOSITION ===\n");
        }
    }
}

void ViewportWindow::renderPickPass() {
    gl_->glBindFramebuffer(GL_FRAMEBUFFER, pick_fbo_);
    gl_->glViewport(0, 0, pick_width_, pick_height_);
    GLuint clear_val = 0;
    gl_->glClearBufferuiv(GL_COLOR, 0, &clear_val);
    gl_->glClear(GL_DEPTH_BUFFER_BIT);

    QMatrix4x4 vp = proj_matrix_ * view_matrix_;
    float planes[6][4];
    extractFrustumPlanes(vp, planes);

    gl_->glUseProgram(pick_program_);
    GLint u_vp       = gl_->glGetUniformLocation(pick_program_, "u_view_projection");
    gl_->glUniformMatrix4fv(u_vp, 1, GL_FALSE, vp.constData());

    gl_->glFrontFace(GL_CCW);

    for (auto& [model_id, m] : models_gpu_) {
        if (m.hidden || !m.ssbo || m.ssbo_instance_count == 0) continue;

        // Pick pass: contribution-cull disabled (0.0 threshold) so every
        // frustum-visible object is clickable, even sub-pixel ones.
        cullAndUploadVisible(m, planes, 1.0f, 0.0f);
        if (m.indirect_command_count == 0) continue;

        gl_->glBindVertexArray(m.vao);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, m.ssbo);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, m.visible_ssbo);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, m.mesh_info_ssbo);
        gl_->glBindBuffer(GL_DRAW_INDIRECT_BUFFER, m.indirect_buffer);

        const uint32_t fwd = m.indirect_forward_count;
        const uint32_t rev = m.indirect_command_count - fwd;
        if (fwd > 0) {
            gl_->glFrontFace(GL_CCW);
            gl_->glMultiDrawElementsIndirect(
                GL_TRIANGLES, GL_UNSIGNED_INT, nullptr,
                static_cast<GLsizei>(fwd), 0);
        }
        if (rev > 0) {
            gl_->glFrontFace(GL_CW);
            gl_->glMultiDrawElementsIndirect(
                GL_TRIANGLES, GL_UNSIGNED_INT,
                reinterpret_cast<const void*>(fwd * sizeof(DrawElementsIndirectCommand)),
                static_cast<GLsizei>(rev), 0);
            gl_->glFrontFace(GL_CCW);
        }
    }
    gl_->glBindBuffer(GL_DRAW_INDIRECT_BUFFER, 0);
    gl_->glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void ViewportWindow::renderAxisGizmo() {
    if (!axis_program_ || !axis_vao_) return;
    const int dpr = devicePixelRatio();
    const int gizmo_size = 110 * dpr;
    const int margin = 10 * dpr;
    gl_->glViewport(margin, margin, gizmo_size, gizmo_size);
    gl_->glDisable(GL_DEPTH_TEST);

    float yaw_rad = qDegreesToRadians(camera_yaw_);
    float pitch_rad = qDegreesToRadians(camera_pitch_);
    QVector3D eye_dir(cosf(pitch_rad) * cosf(yaw_rad),
                      cosf(pitch_rad) * sinf(yaw_rad),
                      sinf(pitch_rad));
    QMatrix4x4 gv; gv.lookAt(eye_dir * 3.0f, QVector3D(0,0,0), QVector3D(0,0,1));
    QMatrix4x4 gp; gp.ortho(-1.4f, 1.4f, -1.4f, 1.4f, 0.1f, 10.0f);
    QMatrix4x4 mvp = gp * gv;

    gl_->glUseProgram(axis_program_);
    gl_->glUniformMatrix4fv(gl_->glGetUniformLocation(axis_program_, "u_mvp"), 1, GL_FALSE, mvp.constData());
    gl_->glLineWidth(2.5f);
    gl_->glBindVertexArray(axis_vao_);
    gl_->glDrawArrays(GL_LINES, 0, 6);
    gl_->glEnable(GL_DEPTH_TEST);
}

void ViewportWindow::exposeEvent(QExposeEvent*) {
    if (isExposed()) {
        if (!gl_initialized_) initGL();
        else                  requestUpdate();
    }
}
void ViewportWindow::resizeEvent(QResizeEvent*) {
    if (gl_initialized_) requestUpdate();
}
bool ViewportWindow::event(QEvent* e) {
    switch (e->type()) {
    case QEvent::UpdateRequest:
        if (isExposed() && gl_initialized_) render();
        return true;
    case QEvent::MouseButtonPress:   handleMousePress(static_cast<QMouseEvent*>(e));   return true;
    case QEvent::MouseButtonRelease: handleMouseRelease(static_cast<QMouseEvent*>(e)); return true;
    case QEvent::MouseMove:          handleMouseMove(static_cast<QMouseEvent*>(e));    return true;
    case QEvent::Wheel:              handleWheel(static_cast<QWheelEvent*>(e));        return true;
    default: return QWindow::event(e);
    }
}

void ViewportWindow::handleMousePress(QMouseEvent* e) {
    active_button_ = e->button();
    last_mouse_pos_ = e->pos();
}
void ViewportWindow::handleMouseRelease(QMouseEvent* e) {
    if (active_button_ == Qt::LeftButton && (e->pos() - last_mouse_pos_).manhattanLength() < 5) {
        uint32_t id = pickObjectAt(e->pos().x(), e->pos().y());
        selected_object_id_ = id;
        emit objectPicked(id);
        requestUpdate();  // selection highlight changed
    }
    active_button_ = Qt::NoButton;
}
void ViewportWindow::handleMouseMove(QMouseEvent* e) {
    QPoint delta = e->pos() - last_mouse_pos_;
    last_mouse_pos_ = e->pos();
    if (active_button_ == Qt::MiddleButton) {
        if (e->modifiers() & Qt::ShiftModifier) {
            float pan_speed = camera_distance_ * 0.002f;
            float yaw_rad = qDegreesToRadians(camera_yaw_);
            float pitch_rad = qDegreesToRadians(camera_pitch_);
            QVector3D right(-sinf(yaw_rad), cosf(yaw_rad), 0.0f);
            QVector3D up(-sinf(pitch_rad) * cosf(yaw_rad),
                         -sinf(pitch_rad) * sinf(yaw_rad),
                          cosf(pitch_rad));
            camera_target_ -= right * delta.x() * pan_speed;
            camera_target_ += up * delta.y() * pan_speed;
        } else {
            camera_yaw_ -= delta.x() * 0.3f;
            camera_pitch_ += delta.y() * 0.3f;
            camera_pitch_ = qBound(-89.0f, camera_pitch_, 89.0f);
        }
        requestUpdate();
    }
}
void ViewportWindow::handleWheel(QWheelEvent* e) {
    float factor = e->angleDelta().y() > 0 ? 0.9f : 1.1f;
    camera_distance_ *= factor;
    camera_distance_ = qMax(0.1f, camera_distance_);
    requestUpdate();
}
