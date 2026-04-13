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
#include <QWheelEvent>
#include <QSurfaceFormat>
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
// Vertex layout (GL side, 28 bytes):
//   location 0: vec3 a_position     (local coords)
//   location 1: vec3 a_normal       (local)
//   location 2: vec4 a_color        (GL_UNSIGNED_BYTE * 4 normalized)
//
// Per-instance record in SSBO std430 (80 bytes):
//   mat4 transform
//   uint object_id
//   uint color_override_rgba8     -- 0 => use baked a_color
//   uint _pad0, _pad1
//
// The draw calls pass `u_instance_offset = mesh.first_instance`; the shader
// reads `instances[u_instance_offset + gl_InstanceID]`.

static const char* MAIN_VERTEX_SHADER = R"(
#version 450 core
#extension GL_ARB_shader_draw_parameters : require
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec4 a_color;

struct InstanceRecord {
    mat4 transform;
    uint object_id;
    uint color_override;
    uint _pad0;
    uint _pad1;
};
layout(std430, binding = 0) readonly buffer Instances {
    InstanceRecord instances[];
};
layout(std430, binding = 1) readonly buffer VisibleIndices {
    uint visible[];
};

uniform mat4 u_view_projection;
uniform uint u_selected_id;

out vec3 v_normal;
out vec4 v_color;
flat out uint v_object_id;
flat out uint v_selected;

void main() {
    uint slot = uint(gl_BaseInstanceARB) + uint(gl_InstanceID);
    uint iid = visible[slot];
    InstanceRecord inst = instances[iid];
    vec4 world = inst.transform * vec4(a_position, 1.0);
    gl_Position = u_view_projection * world;

    // Rotate the normal by the upper-3x3 of the transform.  BIM placements
    // are overwhelmingly rigid rotations (+ optional uniform scale +
    // optional reflection), so we skip the full inverse-transpose but do
    // need to flip the normal when the transform contains a reflection,
    // otherwise mirrored instances shade as if inside-out.  The same
    // determinant sign is what GL_CULL_FACE uses to decide winding, so
    // keeping them in agreement means backface culling is safe to enable.
    mat3 rot = mat3(inst.transform);
    vec3 n = rot * a_normal;
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
layout(location = 0) in vec3 a_position;

struct InstanceRecord {
    mat4 transform;
    uint object_id;
    uint color_override;
    uint _pad0;
    uint _pad1;
};
layout(std430, binding = 0) readonly buffer Instances {
    InstanceRecord instances[];
};
layout(std430, binding = 1) readonly buffer VisibleIndices {
    uint visible[];
};

uniform mat4 u_view_projection;

flat out uint v_object_id;

void main() {
    uint slot = uint(gl_BaseInstanceARB) + uint(gl_InstanceID);
    uint iid = visible[slot];
    InstanceRecord inst = instances[iid];
    gl_Position = u_view_projection * inst.transform * vec4(a_position, 1.0);
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

    connect(&render_timer_, &QTimer::timeout, this, [this]() {
        if (isExposed()) render();
    });
    render_timer_.setInterval(16);
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
            });

    gl_initialized_ = true;
    frame_clock_.start();
    render_timer_.start();

    emit initialized();
}

void ViewportWindow::setupVaoLayout(GLuint vao, GLuint vbo, GLuint ebo) {
    gl_->glVertexArrayVertexBuffer(vao, 0, vbo, 0, INSTANCED_VERTEX_STRIDE_BYTES);
    gl_->glVertexArrayElementBuffer(vao, ebo);

    // position (3 float @ 0)
    gl_->glEnableVertexArrayAttrib(vao, 0);
    gl_->glVertexArrayAttribFormat(vao, 0, 3, GL_FLOAT, GL_FALSE, 0);
    gl_->glVertexArrayAttribBinding(vao, 0, 0);

    // normal (3 float @ 12)
    gl_->glEnableVertexArrayAttrib(vao, 1);
    gl_->glVertexArrayAttribFormat(vao, 1, 3, GL_FLOAT, GL_FALSE, 12);
    gl_->glVertexArrayAttribBinding(vao, 1, 0);

    // color (4 ubyte @ 24, normalized)
    gl_->glEnableVertexArrayAttrib(vao, 2);
    gl_->glVertexArrayAttribFormat(vao, 2, 4, GL_UNSIGNED_BYTE, GL_TRUE, 24);
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

    const size_t vb_size = chunk.vertices.size() * sizeof(float);
    const size_t ib_size = chunk.indices.size()  * sizeof(uint32_t);

    if (m.vbo_used + vb_size > m.vbo_capacity) {
        if (!growModelVbo(m, m.vbo_used + vb_size)) return;
    }
    if (m.ebo_used + ib_size > m.ebo_capacity) {
        if (!growModelEbo(m, m.ebo_used + ib_size)) return;
    }

    MeshInfo info;
    info.vbo_byte_offset = static_cast<uint32_t>(m.vbo_used);
    info.vertex_count    = static_cast<uint32_t>(
        chunk.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS);
    info.ebo_byte_offset = static_cast<uint32_t>(m.ebo_used);
    info.index_count     = static_cast<uint32_t>(chunk.indices.size());
    for (int a = 0; a < 3; ++a) {
        info.local_aabb_min[a] = chunk.local_aabb_min[a];
        info.local_aabb_max[a] = chunk.local_aabb_max[a];
    }
    info.first_instance = 0;
    info.instance_count = 0;

    gl_->glNamedBufferSubData(m.vbo, m.vbo_used, vb_size, chunk.vertices.data());
    gl_->glNamedBufferSubData(m.ebo, m.ebo_used, ib_size, chunk.indices.data());
    m.vbo_used += vb_size;
    m.ebo_used += ib_size;
    m.vertex_count += info.vertex_count;

    if (m.meshes.size() <= chunk.local_mesh_id) m.meshes.resize(chunk.local_mesh_id + 1);
    m.meshes[chunk.local_mesh_id] = info;
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

    // Append the GPU record to the instance SSBO so the model is drawable
    // immediately, without waiting for finalizeModel.  The visible-list
    // architecture means SSBO order is irrelevant to correctness.
    InstanceGpu gpu;
    std::memcpy(gpu.transform, inst.transform, sizeof(gpu.transform));
    gpu.object_id = inst.object_id;
    gpu.color_override_rgba8 = inst.color_override_rgba8;
    gpu._pad0 = 0;
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

    // GPU readback of the packed VBO/EBO ranges actually in use.
    if (m.vbo_used > 0) {
        out.vertices.resize(m.vbo_used / sizeof(float));
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
        if (existing->second.visible_ssbo) gl_->glDeleteBuffers(1, &existing->second.visible_ssbo);
        if (existing->second.indirect_buffer) gl_->glDeleteBuffers(1, &existing->second.indirect_buffer);
        models_gpu_.erase(existing);
    }

    ModelGpuData m;
    gl_->glCreateVertexArrays(1, &m.vao);
    gl_->glCreateBuffers(1, &m.vbo);
    gl_->glCreateBuffers(1, &m.ebo);

    const size_t vb_bytes = data.vertices.size() * sizeof(float);
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
    m.vertex_count = static_cast<uint32_t>(
        data.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS);
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
        dst._pad0 = 0;
        dst._pad1 = 0;
    }
    gl_->glCreateBuffers(1, &m.ssbo);
    const size_t ssbo_bytes = gpu.size() * sizeof(InstanceGpu);
    if (ssbo_bytes > 0) {
        gl_->glNamedBufferStorage(m.ssbo, ssbo_bytes, gpu.data(), 0);
    }
    m.ssbo_instance_count = static_cast<uint32_t>(gpu.size());

    // Recompute the reflection flag from each instance's transform — the
    // sidecar only caches InstanceCpu, not the parallel reflection flags.
    m.instance_reflected.resize(m.instances.size());
    for (size_t i = 0; i < m.instances.size(); ++i) {
        m.instance_reflected[i] = transformIsReflected(m.instances[i].transform) ? 1 : 0;
    }

    buildBvhForModel(m, model_id);

    m.finalized = true;
    models_gpu_.emplace(model_id, std::move(m));

    qDebug("Sidecar apply: model %u  %zu verts, %zu meshes, %zu instances  "
           "%.1f MB vram (vbo %.1f + ebo %.1f + ssbo %.1f)",
           model_id, data.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS,
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
}

void ViewportWindow::resetScene() {
    if (!gl_initialized_) return;
    context_->makeCurrent(this);
    for (auto& [mid, m] : models_gpu_) {
        if (m.vao)  gl_->glDeleteVertexArrays(1, &m.vao);
        if (m.vbo)  gl_->glDeleteBuffers(1, &m.vbo);
        if (m.ebo)  gl_->glDeleteBuffers(1, &m.ebo);
        if (m.ssbo) gl_->glDeleteBuffers(1, &m.ssbo);
        if (m.visible_ssbo) gl_->glDeleteBuffers(1, &m.visible_ssbo);
        if (m.indirect_buffer) gl_->glDeleteBuffers(1, &m.indirect_buffer);
    }
    models_gpu_.clear();
    selected_object_id_ = 0;
}

void ViewportWindow::hideModel(uint32_t model_id) {
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) it->second.hidden = true;
}

void ViewportWindow::showModel(uint32_t model_id) {
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) it->second.hidden = false;
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
        if (it->second.visible_ssbo) gl_->glDeleteBuffers(1, &it->second.visible_ssbo);
        if (it->second.indirect_buffer) gl_->glDeleteBuffers(1, &it->second.indirect_buffer);
        models_gpu_.erase(it);
    }
}

void ViewportWindow::setSelectedObjectId(uint32_t id) { selected_object_id_ = id; }

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

    int px = x * devicePixelRatio();
    int py = (height() - y) * devicePixelRatio();
    uint32_t pixel = 0;
    gl_->glGetTextureSubImage(pick_color_tex_, 0, px, py, 0, 1, 1, 1,
                              GL_RED_INTEGER, GL_UNSIGNED_INT, sizeof(pixel), &pixel);
    return pixel;
}

void ViewportWindow::cullAndUploadVisible(ModelGpuData& m, const float planes[6][4],
                                          float focal_px, float min_pixel_radius) {
    // Per-mesh scratch, split by winding × LOD.  Winding split lets the draw
    // pass toggle glFrontFace once between two MDI calls so GL_CULL_FACE does
    // the right thing for both.  LOD split means instances that want the
    // decimated mesh go into a different bucket that emits against
    // mesh.lod1_ebo_byte_offset / lod1_index_count.
    auto resize_if = [&](std::vector<std::vector<uint32_t>>& v) {
        if (v.size() < m.meshes.size()) v.resize(m.meshes.size());
    };
    resize_if(visible_by_mesh_fwd_lod0_);
    resize_if(visible_by_mesh_fwd_lod1_);
    resize_if(visible_by_mesh_rev_lod0_);
    resize_if(visible_by_mesh_rev_lod1_);
    for (size_t i = 0; i < m.meshes.size(); ++i) {
        visible_by_mesh_fwd_lod0_[i].clear();
        visible_by_mesh_fwd_lod1_[i].clear();
        visible_by_mesh_rev_lod0_[i].clear();
        visible_by_mesh_rev_lod1_[i].clear();
    }

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

    auto test_and_push = [&](uint32_t inst_idx) {
        const InstanceCpu& inst = m.instances[inst_idx];
        if (!aabbInFrustum(inst.world_aabb_min, inst.world_aabb_max, planes)) return;
        if (!contributionPasses(inst.world_aabb_min, inst.world_aabb_max)) return;
        if (inst.mesh_id >= m.meshes.size()) return;
        const MeshInfo& mesh = m.meshes[inst.mesh_id];
        const bool want_lod1 = mesh.lod1_index_count > 0 &&
            lod1_px_threshold > 0.0f &&
            pixelRadius(inst.world_aabb_min, inst.world_aabb_max) < lod1_px_threshold;
        const bool reflected = inst_idx < m.instance_reflected.size()
            && m.instance_reflected[inst_idx] != 0;
        auto& bucket =
            reflected ? (want_lod1 ? visible_by_mesh_rev_lod1_
                                   : visible_by_mesh_rev_lod0_)
                      : (want_lod1 ? visible_by_mesh_fwd_lod1_
                                   : visible_by_mesh_fwd_lod0_);
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

    // Flatten fwd-slice first (LOD0 then LOD1), then rev-slice (ditto), into
    // visible_flat_.  Commands for the fwd slice fill [0, indirect_forward_count),
    // rev fills [indirect_forward_count, end).  LOD0/LOD1 within a winding
    // slice are contiguous — winding is what requires glFrontFace to flip
    // between MDI calls, LOD is not.
    visible_flat_.clear();
    indirect_scratch_.clear();

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
            cmd.baseInstance  = static_cast<uint32_t>(visible_flat_.size());
            indirect_scratch_.push_back(cmd);

            visible_flat_.insert(visible_flat_.end(),
                                 by_mesh[mi].begin(), by_mesh[mi].end());
        }
    };

    emit_slice(visible_by_mesh_fwd_lod0_, 0);
    emit_slice(visible_by_mesh_fwd_lod1_, 1);
    m.indirect_forward_count = static_cast<uint32_t>(indirect_scratch_.size());
    emit_slice(visible_by_mesh_rev_lod0_, 0);
    emit_slice(visible_by_mesh_rev_lod1_, 1);
    m.indirect_command_count = static_cast<uint32_t>(indirect_scratch_.size());

    // Upload visible list (keep binding alive even when empty).
    size_t vis_bytes = std::max<size_t>(visible_flat_.size() * sizeof(uint32_t),
                                        sizeof(uint32_t));
    if (m.visible_ssbo == 0 || m.visible_ssbo_capacity < vis_bytes) {
        if (m.visible_ssbo) gl_->glDeleteBuffers(1, &m.visible_ssbo);
        size_t new_cap = m.visible_ssbo_capacity ? m.visible_ssbo_capacity : 4096;
        while (new_cap < vis_bytes) new_cap *= 2;
        gl_->glCreateBuffers(1, &m.visible_ssbo);
        gl_->glNamedBufferStorage(m.visible_ssbo, new_cap, nullptr, GL_DYNAMIC_STORAGE_BIT);
        m.visible_ssbo_capacity = new_cap;
    }
    if (!visible_flat_.empty()) {
        gl_->glNamedBufferSubData(m.visible_ssbo, 0,
            visible_flat_.size() * sizeof(uint32_t), visible_flat_.data());
    }

    // Upload indirect command buffer.
    size_t ind_bytes = indirect_scratch_.size() * sizeof(DrawElementsIndirectCommand);
    if (ind_bytes == 0) return;
    if (m.indirect_buffer == 0 || m.indirect_capacity < ind_bytes) {
        if (m.indirect_buffer) gl_->glDeleteBuffers(1, &m.indirect_buffer);
        size_t new_cap = m.indirect_capacity ? m.indirect_capacity : 4096;
        while (new_cap < ind_bytes) new_cap *= 2;
        gl_->glCreateBuffers(1, &m.indirect_buffer);
        gl_->glNamedBufferStorage(m.indirect_buffer, new_cap, nullptr, GL_DYNAMIC_STORAGE_BIT);
        m.indirect_capacity = new_cap;
    }
    gl_->glNamedBufferSubData(m.indirect_buffer, 0, ind_bytes, indirect_scratch_.data());
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
    // Drop frustum-visible objects smaller than this many pixels.  Override
    // with IFC_MIN_PX (0 = disabled).  2 px radius = ~4x4 pixels, well below
    // what's meaningful at normal viewing distances and eliminates the long
    // tail of distant MEP/fixings that dominate BIM triangle counts.
    static const float min_pixel_radius = []{
        const char* e = std::getenv("IFC_MIN_PX");
        return (e && *e) ? static_cast<float>(std::atof(e)) : 2.0f;
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

    // Start each frame with CCW-is-front; the two-pass draw below flips
    // back and forth.  Harmless when culling is off.
    gl_->glFrontFace(GL_CCW);

    for (auto& [model_id, m] : models_gpu_) {
        if (m.hidden || !m.ssbo || m.ssbo_instance_count == 0) continue;

        cullAndUploadVisible(m, planes, focal_px, min_pixel_radius);
        if (m.indirect_command_count == 0) continue;

        gl_->glBindVertexArray(m.vao);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, m.ssbo);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, m.visible_ssbo);
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

        for (const auto& cmd : indirect_scratch_) {
            visible_triangles_ += (cmd.count / 3) * cmd.instanceCount;
            visible_objects_   += cmd.instanceCount;
        }
        indirect_sub_draws_ += m.indirect_command_count;
    }
    gl_->glBindBuffer(GL_DRAW_INDIRECT_BUFFER, 0);

    renderAxisGizmo();

    context_->swapBuffers(this);

    float dt = frame_clock_.restart() / 1000.0f;
    accumulated_time_ += dt;
    frame_count_++;
    if (accumulated_time_ >= 1.0f) {
        last_fps_ = static_cast<float>(frame_count_) / accumulated_time_;
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

        qDebug("[frame] %.1f fps  %.2f ms  obj %u/%u  tri %u/%u  "
               "meshes %u  gl_draws %u  sub_draws %u  "
               "vram %.1f MB (vbo %.1f + ebo %.1f + ssbo %.1f)  models %zu (%zu hidden)",
               last_fps_, 1000.0f / last_fps_,
               visible_objects_, total_obj,
               visible_triangles_, total_tri,
               total_meshes, gl_draw_calls_, indirect_sub_draws_,
               (total_vbo + total_ebo + total_ssbo) / (1024.0*1024.0),
               total_vbo / (1024.0*1024.0),
               total_ebo / (1024.0*1024.0),
               total_ssbo / (1024.0*1024.0),
               num_models, num_hidden);
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
    if (isExposed() && !gl_initialized_) initGL();
}
void ViewportWindow::resizeEvent(QResizeEvent*) {
    if (gl_initialized_) render();
}
bool ViewportWindow::event(QEvent* e) {
    switch (e->type()) {
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
    }
}
void ViewportWindow::handleWheel(QWheelEvent* e) {
    float factor = e->angleDelta().y() > 0 ? 0.9f : 1.1f;
    camera_distance_ *= factor;
    camera_distance_ = qMax(0.1f, camera_distance_);
}
