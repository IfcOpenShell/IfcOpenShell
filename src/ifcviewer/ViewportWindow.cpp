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

#include <QMouseEvent>
#include <QWheelEvent>
#include <QSurfaceFormat>
#include <QtMath>
#include <QtOpenGL/QOpenGLVersionFunctionsFactory>

#include <cstring>
#include <cmath>
#include <algorithm>
#include <limits>

static const size_t INITIAL_VBO_SIZE = 64 * 1024 * 1024;   // 64 MB
static const size_t INITIAL_EBO_SIZE = 32 * 1024 * 1024;   // 32 MB
static const size_t MAX_BUFFER_SIZE  = 4ull * 1024 * 1024 * 1024;  // 4 GB

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

uniform mat4 u_view_projection;
uniform uint u_instance_offset;
uniform uint u_selected_id;

out vec3 v_normal;
out vec4 v_color;
flat out uint v_object_id;
flat out uint v_selected;

void main() {
    InstanceRecord inst = instances[u_instance_offset + uint(gl_InstanceID)];
    vec4 world = inst.transform * vec4(a_position, 1.0);
    gl_Position = u_view_projection * world;

    // Rotate the normal by the upper-3x3 of the transform. For the vast
    // majority of BIM placements this is a rigid rotation (+ uniform scale),
    // so we skip the inverse-transpose.
    v_normal = normalize(mat3(inst.transform) * a_normal);

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
    vec3 n = normalize(v_normal);
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

uniform mat4 u_view_projection;
uniform uint u_instance_offset;

flat out uint v_object_id;

void main() {
    InstanceRecord inst = instances[u_instance_offset + uint(gl_InstanceID)];
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
    // We don't need a GL context here since we're only touching CPU state,
    // but the signal may fire on the render thread so keep it simple.
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
    if (m.instances.empty()) { m.finalized = true; return; }

    // Sort instances by mesh_id (stable for deterministic ordering).
    std::stable_sort(m.instances.begin(), m.instances.end(),
        [](const InstanceCpu& a, const InstanceCpu& b) {
            return a.mesh_id < b.mesh_id;
        });

    // Assign per-mesh contiguous range.
    for (auto& mesh : m.meshes) { mesh.first_instance = 0; mesh.instance_count = 0; }
    uint32_t current = UINT32_MAX;
    uint32_t run_start = 0;
    for (uint32_t i = 0; i < m.instances.size(); ++i) {
        uint32_t mid = m.instances[i].mesh_id;
        if (mid != current) {
            if (current != UINT32_MAX && current < m.meshes.size()) {
                m.meshes[current].first_instance = run_start;
                m.meshes[current].instance_count = i - run_start;
            }
            current = mid;
            run_start = i;
        }
    }
    if (current != UINT32_MAX && current < m.meshes.size()) {
        m.meshes[current].first_instance = run_start;
        m.meshes[current].instance_count = static_cast<uint32_t>(m.instances.size()) - run_start;
    }

    // Build GPU-layout array.
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

    // Allocate and upload SSBO.
    if (m.ssbo) gl_->glDeleteBuffers(1, &m.ssbo);
    gl_->glCreateBuffers(1, &m.ssbo);
    const size_t ssbo_bytes = gpu.size() * sizeof(InstanceGpu);
    gl_->glNamedBufferStorage(m.ssbo, ssbo_bytes, gpu.data(), 0);
    m.ssbo_instance_count = static_cast<uint32_t>(gpu.size());

    m.finalized = true;

    qDebug("Model %u finalized: %zu verts, %zu meshes, %zu instances, %.1f MB vram "
           "(vbo %.1f + ebo %.1f + ssbo %.1f)",
           model_id, size_t(m.vertex_count), m.meshes.size(), m.instances.size(),
           (m.vbo_capacity + m.ebo_capacity + ssbo_bytes) / (1024.0*1024.0),
           m.vbo_capacity / (1024.0*1024.0),
           m.ebo_capacity / (1024.0*1024.0),
           ssbo_bytes / (1024.0*1024.0));
}

void ViewportWindow::resetScene() {
    if (!gl_initialized_) return;
    context_->makeCurrent(this);
    for (auto& [mid, m] : models_gpu_) {
        if (m.vao)  gl_->glDeleteVertexArrays(1, &m.vao);
        if (m.vbo)  gl_->glDeleteBuffers(1, &m.vbo);
        if (m.ebo)  gl_->glDeleteBuffers(1, &m.ebo);
        if (m.ssbo) gl_->glDeleteBuffers(1, &m.ssbo);
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

void ViewportWindow::updateCamera() {
    float yaw_rad = qDegreesToRadians(camera_yaw_);
    float pitch_rad = qDegreesToRadians(camera_pitch_);
    QVector3D eye;
    eye.setX(camera_target_.x() + camera_distance_ * cosf(pitch_rad) * cosf(yaw_rad));
    eye.setY(camera_target_.y() + camera_distance_ * cosf(pitch_rad) * sinf(yaw_rad));
    eye.setZ(camera_target_.z() + camera_distance_ * sinf(pitch_rad));
    view_matrix_.setToIdentity();
    view_matrix_.lookAt(eye, camera_target_, QVector3D(0, 0, 1));
    proj_matrix_.setToIdentity();
    float aspect = width() > 0 ? float(width()) / float(height()) : 1.0f;
    proj_matrix_.perspective(45.0f, aspect, 0.1f, camera_distance_ * 10.0f);
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

    gl_->glUseProgram(main_program_);
    GLint u_vp        = gl_->glGetUniformLocation(main_program_, "u_view_projection");
    GLint u_light     = gl_->glGetUniformLocation(main_program_, "u_light_dir");
    GLint u_sel       = gl_->glGetUniformLocation(main_program_, "u_selected_id");
    GLint u_inst_off  = gl_->glGetUniformLocation(main_program_, "u_instance_offset");
    gl_->glUniformMatrix4fv(u_vp, 1, GL_FALSE, vp.constData());
    gl_->glUniform3f(u_light, 0.3f, 0.5f, 0.8f);
    gl_->glUniform1ui(u_sel, selected_object_id_);

    visible_triangles_ = 0;
    visible_objects_ = 0;
    instanced_draws_ = 0;

    for (auto& [model_id, m] : models_gpu_) {
        if (m.hidden || !m.finalized || !m.ssbo) continue;
        gl_->glBindVertexArray(m.vao);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, m.ssbo);

        for (const auto& mesh : m.meshes) {
            if (mesh.instance_count == 0 || mesh.index_count == 0) continue;
            gl_->glUniform1ui(u_inst_off, mesh.first_instance);
            gl_->glDrawElementsInstancedBaseVertex(
                GL_TRIANGLES,
                static_cast<GLsizei>(mesh.index_count),
                GL_UNSIGNED_INT,
                reinterpret_cast<const void*>(static_cast<uintptr_t>(mesh.ebo_byte_offset)),
                static_cast<GLsizei>(mesh.instance_count),
                static_cast<GLint>(mesh.vbo_byte_offset / INSTANCED_VERTEX_STRIDE_BYTES));
            visible_triangles_ += (mesh.index_count / 3) * mesh.instance_count;
            visible_objects_   += mesh.instance_count;
            ++instanced_draws_;
        }
    }

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
            if (mm.hidden || !mm.finalized) { num_hidden++; continue; }
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
        stats.instanced_draws = instanced_draws_;
        emit frameStatsUpdated(stats);

        qDebug("[frame] %.1f fps  %.2f ms  obj %u/%u  tri %u/%u  "
               "meshes %u  inst_draws %u  "
               "vram %.1f MB (vbo %.1f + ebo %.1f + ssbo %.1f)  models %zu (%zu hidden)",
               last_fps_, 1000.0f / last_fps_,
               visible_objects_, total_obj,
               visible_triangles_, total_tri,
               total_meshes, instanced_draws_,
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
    gl_->glUseProgram(pick_program_);
    GLint u_vp       = gl_->glGetUniformLocation(pick_program_, "u_view_projection");
    GLint u_inst_off = gl_->glGetUniformLocation(pick_program_, "u_instance_offset");
    gl_->glUniformMatrix4fv(u_vp, 1, GL_FALSE, vp.constData());

    for (auto& [model_id, m] : models_gpu_) {
        if (m.hidden || !m.finalized || !m.ssbo) continue;
        gl_->glBindVertexArray(m.vao);
        gl_->glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, m.ssbo);
        for (const auto& mesh : m.meshes) {
            if (mesh.instance_count == 0 || mesh.index_count == 0) continue;
            gl_->glUniform1ui(u_inst_off, mesh.first_instance);
            gl_->glDrawElementsInstancedBaseVertex(
                GL_TRIANGLES,
                static_cast<GLsizei>(mesh.index_count),
                GL_UNSIGNED_INT,
                reinterpret_cast<const void*>(static_cast<uintptr_t>(mesh.ebo_byte_offset)),
                static_cast<GLsizei>(mesh.instance_count),
                static_cast<GLint>(mesh.vbo_byte_offset / INSTANCED_VERTEX_STRIDE_BYTES));
        }
    }
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
