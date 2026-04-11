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
#include "SidecarCache.h"

#include <QMouseEvent>
#include <QWheelEvent>
#include <QSurfaceFormat>
#include <QtMath>
#include <QtOpenGL/QOpenGLVersionFunctionsFactory>

#include <cstring>
#include <cmath>
#include <algorithm>
#include <limits>

static const size_t INITIAL_VBO_SIZE = 64 * 1024 * 1024;  // 64 MB
static const size_t INITIAL_EBO_SIZE = 32 * 1024 * 1024;  // 32 MB
static const size_t MAX_BUFFER_SIZE = 4ull * 1024 * 1024 * 1024;  // 4 GB
static const int VERTEX_STRIDE = 8;  // pos(3) + normal(3) + object_id(1) + color(1 packed)

static const char* MAIN_VERTEX_SHADER = R"(
#version 450 core
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in float a_object_id;
layout(location = 3) in vec4 a_color;

uniform mat4 u_view_projection;
uniform uint u_selected_id;

out vec3 v_normal;
out vec3 v_position;
out vec4 v_color;
flat out uint v_object_id;
flat out uint v_selected;

void main() {
    gl_Position = u_view_projection * vec4(a_position, 1.0);
    v_normal = a_normal;
    v_position = a_position;
    v_color = a_color;
    v_object_id = floatBitsToUint(a_object_id);
    v_selected = (v_object_id == u_selected_id) ? 1u : 0u;
}
)";

static const char* MAIN_FRAGMENT_SHADER = R"(
#version 450 core
in vec3 v_normal;
in vec3 v_position;
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

    if (v_selected == 1u) {
        color = mix(color, vec3(0.2, 0.6, 1.0), 0.5);
    }

    frag_color = vec4(color, v_color.a);
}
)";

static const char* PICK_VERTEX_SHADER = R"(
#version 450 core
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in float a_object_id;

uniform mat4 u_view_projection;

flat out uint v_object_id;

void main() {
    gl_Position = u_view_projection * vec4(a_position, 1.0);
    v_object_id = floatBitsToUint(a_object_id);
}
)";

static const char* PICK_FRAGMENT_SHADER = R"(
#version 450 core
flat in uint v_object_id;

out uint frag_id;

void main() {
    frag_id = v_object_id;
}
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

void main() {
    frag_color = vec4(v_color, 1.0);
}
)";

static GLuint compileShader(QOpenGLFunctions_4_5_Core* gl, GLenum type, const char* source) {
    GLuint shader = gl->glCreateShader(type);
    gl->glShaderSource(shader, 1, &source, nullptr);
    gl->glCompileShader(shader);
    GLint ok = 0;
    gl->glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[1024];
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
        char log[1024];
        gl->glGetProgramInfoLog(prog, sizeof(log), nullptr, log);
        qWarning("Program link error: %s", log);
    }
    gl->glDeleteShader(vert);
    gl->glDeleteShader(frag);
    return prog;
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
    render_timer_.setInterval(16); // ~60 fps
}

ViewportWindow::~ViewportWindow() {
    if (bvh_build_thread_.joinable())
        bvh_build_thread_.join();
    if (context_) {
        context_->makeCurrent(this);
        if (gl_) {
            for (auto& [mid, m] : models_gpu_) {
                if (m.vao) gl_->glDeleteVertexArrays(1, &m.vao);
                if (m.vbo) gl_->glDeleteBuffers(1, &m.vbo);
                if (m.ebo) gl_->glDeleteBuffers(1, &m.ebo);
            }
            if (axis_vao_) gl_->glDeleteVertexArrays(1, &axis_vao_);
            if (axis_vbo_) gl_->glDeleteBuffers(1, &axis_vbo_);
            if (main_program_) gl_->glDeleteProgram(main_program_);
            if (pick_program_) gl_->glDeleteProgram(pick_program_);
            if (axis_program_) gl_->glDeleteProgram(axis_program_);
            if (pick_fbo_) gl_->glDeleteFramebuffers(1, &pick_fbo_);
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
    if (!context_->create()) {
        qFatal("Failed to create OpenGL context");
        return;
    }
    context_->makeCurrent(this);

    gl_ = QOpenGLVersionFunctionsFactory::get<QOpenGLFunctions_4_5_Core>(context_);
    if (!gl_) {
        qWarning("OpenGL 4.5 not available, falling back");
        return;
    }

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
    gl_->glVertexArrayVertexBuffer(vao, 0, vbo, 0, VERTEX_STRIDE * sizeof(float));
    gl_->glVertexArrayElementBuffer(vao, ebo);

    // position
    gl_->glEnableVertexArrayAttrib(vao, 0);
    gl_->glVertexArrayAttribFormat(vao, 0, 3, GL_FLOAT, GL_FALSE, 0);
    gl_->glVertexArrayAttribBinding(vao, 0, 0);

    // normal
    gl_->glEnableVertexArrayAttrib(vao, 1);
    gl_->glVertexArrayAttribFormat(vao, 1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float));
    gl_->glVertexArrayAttribBinding(vao, 1, 0);

    // object_id (passed as float, decoded in shader via floatBitsToUint)
    gl_->glEnableVertexArrayAttrib(vao, 2);
    gl_->glVertexArrayAttribFormat(vao, 2, 1, GL_FLOAT, GL_FALSE, 6 * sizeof(float));
    gl_->glVertexArrayAttribBinding(vao, 2, 0);

    // color (RGBA8 packed into the 4 bytes at offset 28; normalized to vec4)
    gl_->glEnableVertexArrayAttrib(vao, 3);
    gl_->glVertexArrayAttribFormat(vao, 3, 4, GL_UNSIGNED_BYTE, GL_TRUE, 7 * sizeof(float));
    gl_->glVertexArrayAttribBinding(vao, 3, 0);
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
        0.0f, 0.0f, 0.0f,   1.0f, 0.25f, 0.25f,
        1.0f, 0.0f, 0.0f,   1.0f, 0.25f, 0.25f,
        0.0f, 0.0f, 0.0f,   0.30f, 0.95f, 0.30f,
        0.0f, 1.0f, 0.0f,   0.30f, 0.95f, 0.30f,
        0.0f, 0.0f, 0.0f,   0.30f, 0.55f, 1.0f,
        0.0f, 0.0f, 1.0f,   0.30f, 0.55f, 1.0f,
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
        qWarning("VBO grow request (%zu MB) exceeds cap", new_capacity / (1024 * 1024));
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

    gl_->glVertexArrayVertexBuffer(m.vao, 0, m.vbo, 0, VERTEX_STRIDE * sizeof(float));

    qInfo("Model VBO grew to %zu MB", m.vbo_capacity / (1024 * 1024));
    return true;
}

bool ViewportWindow::growModelEbo(ModelGpuData& m, size_t needed_total) {
    size_t new_capacity = m.ebo_capacity;
    while (new_capacity < needed_total) new_capacity *= 2;
    if (new_capacity > MAX_BUFFER_SIZE) {
        qWarning("EBO grow request (%zu MB) exceeds cap", new_capacity / (1024 * 1024));
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

    qInfo("Model EBO grew to %zu MB", m.ebo_capacity / (1024 * 1024));
    return true;
}

void ViewportWindow::uploadChunk(const UploadChunk& chunk) {
    if (!gl_initialized_) return;
    if (chunk.vertices.empty() || chunk.indices.empty()) return;

    context_->makeCurrent(this);

    // Get or create per-model GPU data.
    auto it = models_gpu_.find(chunk.model_id);
    if (it == models_gpu_.end()) {
        ModelGpuData m;
        gl_->glCreateVertexArrays(1, &m.vao);
        gl_->glCreateBuffers(1, &m.vbo);
        gl_->glCreateBuffers(1, &m.ebo);

        m.vbo_capacity = INITIAL_VBO_SIZE;
        m.ebo_capacity = INITIAL_EBO_SIZE;
        gl_->glNamedBufferStorage(m.vbo, m.vbo_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);
        gl_->glNamedBufferStorage(m.ebo, m.ebo_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);

        setupVaoLayout(m.vao, m.vbo, m.ebo);
        it = models_gpu_.emplace(chunk.model_id, std::move(m)).first;
    }

    auto& mgpu = it->second;

    size_t vb_size = chunk.vertices.size() * sizeof(float);
    size_t ib_size = chunk.indices.size() * sizeof(uint32_t);

    if (mgpu.vbo_used + vb_size > mgpu.vbo_capacity) {
        if (!growModelVbo(mgpu, mgpu.vbo_used + vb_size)) {
            qWarning("VBO at cap, skipping chunk");
            return;
        }
    }
    if (mgpu.ebo_used + ib_size > mgpu.ebo_capacity) {
        if (!growModelEbo(mgpu, mgpu.ebo_used + ib_size)) {
            qWarning("EBO at cap, skipping chunk");
            return;
        }
    }

    uint32_t base_vertex = mgpu.vertex_count;

    gl_->glNamedBufferSubData(mgpu.vbo, mgpu.vbo_used, vb_size, chunk.vertices.data());

    // Remap chunk-local indices into model-local global indices.
    std::vector<uint32_t> global_indices(chunk.indices.size());
    for (size_t i = 0; i < chunk.indices.size(); ++i) {
        global_indices[i] = chunk.indices[i] + base_vertex;
    }
    gl_->glNamedBufferSubData(mgpu.ebo, mgpu.ebo_used, ib_size, global_indices.data());

    // Compute AABB from vertex positions in this chunk.
    ObjectDrawInfo info;
    info.index_offset = static_cast<uint32_t>(mgpu.ebo_used);
    info.index_count = static_cast<uint32_t>(chunk.indices.size());
    info.model_id = chunk.model_id;

    const size_t num_verts = chunk.vertices.size() / VERTEX_STRIDE;
    if (num_verts > 0) {
        info.aabb_min[0] = info.aabb_min[1] = info.aabb_min[2] =  std::numeric_limits<float>::max();
        info.aabb_max[0] = info.aabb_max[1] = info.aabb_max[2] = -std::numeric_limits<float>::max();
        for (size_t v = 0; v < num_verts; ++v) {
            const float* pos = &chunk.vertices[v * VERTEX_STRIDE];
            for (int a = 0; a < 3; ++a) {
                if (pos[a] < info.aabb_min[a]) info.aabb_min[a] = pos[a];
                if (pos[a] > info.aabb_max[a]) info.aabb_max[a] = pos[a];
            }
        }
    } else {
        info.aabb_min[0] = info.aabb_min[1] = info.aabb_min[2] = 0.0f;
        info.aabb_max[0] = info.aabb_max[1] = info.aabb_max[2] = 0.0f;
    }

    mgpu.draw_info.push_back(info);
    mgpu.active_draw_count = static_cast<uint32_t>(mgpu.draw_info.size()); // immediately drawable
    mgpu.vbo_used += vb_size;
    mgpu.ebo_used += ib_size;
    mgpu.vertex_count += static_cast<uint32_t>(num_verts);
    mgpu.total_triangles += static_cast<uint32_t>(chunk.indices.size() / 3);
}

void ViewportWindow::uploadBulk(uint32_t model_id,
                                std::vector<float> vertices,
                                std::vector<uint32_t> indices,
                                const std::vector<ObjectDrawInfo>& draw_info,
                                std::shared_ptr<BvhSet> bvh_set) {
    if (!gl_initialized_) return;
    if (vertices.empty() || indices.empty()) return;

    context_->makeCurrent(this);

    size_t vb_size = vertices.size() * sizeof(float);
    size_t ib_size = indices.size() * sizeof(uint32_t);

    // Allocate empty buffers at exact size — no data uploaded yet.
    ModelGpuData m;
    gl_->glCreateVertexArrays(1, &m.vao);
    gl_->glCreateBuffers(1, &m.vbo);
    gl_->glCreateBuffers(1, &m.ebo);

    m.vbo_capacity = vb_size;
    m.ebo_capacity = ib_size;
    gl_->glNamedBufferStorage(m.vbo, vb_size, nullptr, GL_DYNAMIC_STORAGE_BIT);
    gl_->glNamedBufferStorage(m.ebo, ib_size, nullptr, GL_DYNAMIC_STORAGE_BIT);

    setupVaoLayout(m.vao, m.vbo, m.ebo);

    m.vbo_used = vb_size;
    m.ebo_used = ib_size;
    m.vertex_count = static_cast<uint32_t>(vertices.size() / VERTEX_STRIDE);
    m.draw_info = draw_info;
    m.active_draw_count = 0;  // nothing drawable yet

    uint32_t total_tri = 0;
    for (const auto& di : draw_info) total_tri += di.index_count / 3;
    m.total_triangles = total_tri;

    // Delete old model data if re-uploading.
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        gl_->glDeleteVertexArrays(1, &it->second.vao);
        gl_->glDeleteBuffers(1, &it->second.vbo);
        gl_->glDeleteBuffers(1, &it->second.ebo);
    }
    models_gpu_[model_id] = std::move(m);

    // Queue progressive upload — data will stream in over subsequent frames.
    PendingUpload pu;
    pu.model_id = model_id;
    pu.vertices = std::move(vertices);
    pu.indices = std::move(indices);
    pu.bvh_set = std::move(bvh_set);
    pending_uploads_.push_back(std::move(pu));

    qDebug("Bulk upload queued: model %u, %zu vertices, %zu indices, %zu objects",
           model_id, vertices.size() / VERTEX_STRIDE, indices.size(), draw_info.size());
}

void ViewportWindow::resetScene() {
    if (!gl_initialized_) return;

    if (bvh_build_thread_.joinable())
        bvh_build_thread_.join();

    context_->makeCurrent(this);
    for (auto& [mid, m] : models_gpu_) {
        if (m.vao) gl_->glDeleteVertexArrays(1, &m.vao);
        if (m.vbo) gl_->glDeleteBuffers(1, &m.vbo);
        if (m.ebo) gl_->glDeleteBuffers(1, &m.ebo);
    }
    models_gpu_.clear();
    model_bvhs_.clear();
    pending_uploads_.clear();
    selected_object_id_ = 0;
    {
        std::lock_guard<std::mutex> bvh_lock(bvh_result_mutex_);
        pending_bvh_.reset();
    }
}

static const size_t UPLOAD_CHUNK_BYTES = 48 * 1024 * 1024;  // 48 MB per frame

void ViewportWindow::processPendingUploads() {
    if (pending_uploads_.empty()) return;

    auto& pu = pending_uploads_.front();
    auto it = models_gpu_.find(pu.model_id);
    if (it == models_gpu_.end()) {
        pending_uploads_.pop_front();
        return;
    }
    auto& mgpu = it->second;

    size_t vbo_total = pu.vertices.size() * sizeof(float);
    size_t ebo_total = pu.indices.size() * sizeof(uint32_t);

    // Phase 1: Upload VBO in chunks.
    if (pu.vbo_uploaded < vbo_total) {
        size_t remaining = vbo_total - pu.vbo_uploaded;
        size_t chunk = std::min(remaining, UPLOAD_CHUNK_BYTES);
        gl_->glNamedBufferSubData(mgpu.vbo, pu.vbo_uploaded, chunk,
                                  reinterpret_cast<const char*>(pu.vertices.data()) + pu.vbo_uploaded);
        pu.vbo_uploaded += chunk;

        if (pu.vbo_uploaded >= vbo_total) {
            // VBO done — free CPU memory.
            pu.vertices.clear();
            pu.vertices.shrink_to_fit();
        }
        return;  // yield to render loop
    }

    // Phase 2: Upload EBO in chunks. Objects become drawable as their range lands.
    if (pu.ebo_uploaded < ebo_total) {
        size_t remaining = ebo_total - pu.ebo_uploaded;
        size_t chunk = std::min(remaining, UPLOAD_CHUNK_BYTES);
        gl_->glNamedBufferSubData(mgpu.ebo, pu.ebo_uploaded, chunk,
                                  reinterpret_cast<const char*>(pu.indices.data()) + pu.ebo_uploaded);
        pu.ebo_uploaded += chunk;

        // Advance active_draw_count: activate objects whose EBO range is fully uploaded.
        while (mgpu.active_draw_count < mgpu.draw_info.size()) {
            const auto& obj = mgpu.draw_info[mgpu.active_draw_count];
            size_t obj_end = obj.index_offset + obj.index_count * sizeof(uint32_t);
            if (obj_end <= pu.ebo_uploaded)
                mgpu.active_draw_count++;
            else
                break;
        }

        if (pu.ebo_uploaded >= ebo_total) {
            // EBO done — free CPU memory.
            pu.indices.clear();
            pu.indices.shrink_to_fit();
        } else {
            return;  // yield to render loop
        }
    }

    // Fully uploaded — activate BVH if present.
    mgpu.active_draw_count = static_cast<uint32_t>(mgpu.draw_info.size());
    if (pu.bvh_set) {
        model_bvhs_[pu.model_id] = std::move(pu.bvh_set);
    }

    qDebug("Progressive upload complete: model %u", pu.model_id);
    pending_uploads_.pop_front();
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

    // Cancel any pending upload for this model.
    pending_uploads_.erase(
        std::remove_if(pending_uploads_.begin(), pending_uploads_.end(),
                        [model_id](const PendingUpload& pu) { return pu.model_id == model_id; }),
        pending_uploads_.end());

    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        gl_->glDeleteVertexArrays(1, &it->second.vao);
        gl_->glDeleteBuffers(1, &it->second.vbo);
        gl_->glDeleteBuffers(1, &it->second.ebo);
        models_gpu_.erase(it);
    }
    model_bvhs_.erase(model_id);
}

std::vector<uint32_t> ViewportWindow::readbackEbo(uint32_t model_id) const {
    std::vector<uint32_t> ebo_data;
    auto it = models_gpu_.find(model_id);
    if (!gl_ || it == models_gpu_.end() || it->second.ebo_used == 0) return ebo_data;

    const auto& m = it->second;
    size_t num_indices = m.ebo_used / sizeof(uint32_t);
    ebo_data.resize(num_indices);
    gl_->glGetNamedBufferSubData(m.ebo, 0, m.ebo_used, ebo_data.data());
    return ebo_data;
}

std::vector<float> ViewportWindow::readbackVbo(uint32_t model_id) const {
    std::vector<float> vbo_data;
    auto it = models_gpu_.find(model_id);
    if (!gl_ || it == models_gpu_.end() || it->second.vbo_used == 0) return vbo_data;

    const auto& m = it->second;
    size_t num_floats = m.vbo_used / sizeof(float);
    vbo_data.resize(num_floats);
    gl_->glGetNamedBufferSubData(m.vbo, 0, m.vbo_used, vbo_data.data());
    return vbo_data;
}

void ViewportWindow::buildBvhAsync(uint32_t model_id,
                                   const std::string& ifc_path,
                                   uint64_t ifc_file_size,
                                   std::vector<PackedElementInfo> sidecar_elements,
                                   std::string sidecar_string_table) {
    if (bvh_build_thread_.joinable())
        bvh_build_thread_.join();

    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return;

    // Snapshot draw info; read back EBO + VBO on GL thread.
    std::vector<ObjectDrawInfo> draw_snapshot = it->second.draw_info;
    std::vector<uint32_t> ebo_snapshot = readbackEbo(model_id);
    std::vector<float> vbo_snapshot;
    if (!ifc_path.empty() && !sidecar_elements.empty()) {
        vbo_snapshot = readbackVbo(model_id);
    }

    if (draw_snapshot.empty() || ebo_snapshot.empty()) return;

    bvh_build_thread_ = std::thread([this,
                                     model_id,
                                     draw_info = std::move(draw_snapshot),
                                     ebo_data = std::move(ebo_snapshot),
                                     vbo_data = std::move(vbo_snapshot),
                                     elements = std::move(sidecar_elements),
                                     string_table = std::move(sidecar_string_table),
                                     ifc_path, ifc_file_size]() {
        auto bvh_set = buildBvhSet(draw_info);

        EboReorderResult ebo_result = reorderEbo(*bvh_set, draw_info, ebo_data);

        // Write full sidecar if requested.
        if (!ifc_path.empty() && !elements.empty() && !vbo_data.empty()) {
            SidecarData sd;
            sd.vertices = vbo_data;
            sd.indices = ebo_result.reordered_ebo;
            sd.draw_info = ebo_result.reordered_draw_info;
            sd.elements = std::move(elements);
            sd.string_table = std::move(string_table);
            sd.bvh_set = bvh_set;
            writeSidecar(ifc_path, sd, ifc_file_size);
        }

        {
            std::lock_guard<std::mutex> lock(bvh_result_mutex_);
            pending_bvh_ = std::make_unique<PendingBvh>();
            pending_bvh_->model_id = model_id;
            pending_bvh_->bvh_set = std::move(bvh_set);
            pending_bvh_->ebo_reorder = std::move(ebo_result);
        }
    });
}

void ViewportWindow::applyBvhResult() {
    std::unique_ptr<PendingBvh> result;
    {
        std::lock_guard<std::mutex> lock(bvh_result_mutex_);
        result = std::move(pending_bvh_);
    }
    if (!result) return;

    auto it = models_gpu_.find(result->model_id);
    if (it == models_gpu_.end()) return;

    auto& mgpu = it->second;

    // Re-upload the reordered EBO into this model's buffer.
    if (!result->ebo_reorder.reordered_ebo.empty()) {
        size_t ebo_bytes = result->ebo_reorder.reordered_ebo.size() * sizeof(uint32_t);
        if (ebo_bytes <= mgpu.ebo_capacity) {
            gl_->glNamedBufferSubData(mgpu.ebo, 0, ebo_bytes,
                                      result->ebo_reorder.reordered_ebo.data());
        }
    }

    // Swap draw info.
    if (result->ebo_reorder.reordered_draw_info.size() == mgpu.draw_info.size()) {
        mgpu.draw_info = std::move(result->ebo_reorder.reordered_draw_info);
    }

    model_bvhs_[result->model_id] = std::move(result->bvh_set);

    qDebug("BVH activated for model %u", result->model_id);
}

void ViewportWindow::setSelectedObjectId(uint32_t id) {
    selected_object_id_ = id;
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

    int px = x * devicePixelRatio();
    int py = (height() - y) * devicePixelRatio();
    uint32_t pixel = 0;
    gl_->glGetTextureSubImage(pick_color_tex_, 0, px, py, 0, 1, 1, 1, GL_RED_INTEGER, GL_UNSIGNED_INT, sizeof(pixel), &pixel);

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

bool ViewportWindow::aabbInFrustum(const float aabb_min[3], const float aabb_max[3],
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

void ViewportWindow::traverseBvh(const ModelBvh& mbvh, const ModelGpuData& mgpu,
                                 const float planes[6][4]) {
    if (mbvh.nodes.empty()) return;

    uint32_t stack[64];
    int sp = 0;
    stack[sp++] = 0;  // root

    // Get the current model's draw command being built.
    auto& cmd = frame_draw_cmds_.back();

    while (sp > 0) {
        uint32_t ni = stack[--sp];
        const BvhNode& node = mbvh.nodes[ni];

        if (!aabbInFrustum(node.aabb_min, node.aabb_max, planes))
            continue;

        if (node.count > 0) {
            for (uint32_t i = 0; i < node.count; ++i) {
                uint32_t oi = mbvh.object_indices[node.right_or_first + i];
                const auto& obj = mgpu.draw_info[oi];
                if (aabbInFrustum(obj.aabb_min, obj.aabb_max, planes)) {
                    cmd.counts.push_back(static_cast<GLsizei>(obj.index_count));
                    cmd.offsets.push_back(reinterpret_cast<const void*>(
                        static_cast<uintptr_t>(obj.index_offset)));
                    visible_triangles_ += obj.index_count / 3;
                }
            }
        } else {
            if (sp < 63) {
                stack[sp++] = node.right_or_first;
                stack[sp++] = ni + 1;
            }
        }
    }
}

void ViewportWindow::buildVisibleList(const QMatrix4x4& vp) {
    frame_draw_cmds_.clear();
    visible_triangles_ = 0;

    // Extract 6 frustum planes from the view-projection matrix.
    float planes[6][4];
    for (int i = 0; i < 4; ++i) {
        planes[0][i] = vp(3, i) + vp(0, i);  // left
        planes[1][i] = vp(3, i) - vp(0, i);  // right
        planes[2][i] = vp(3, i) + vp(1, i);  // bottom
        planes[3][i] = vp(3, i) - vp(1, i);  // top
        planes[4][i] = vp(3, i) + vp(2, i);  // near
        planes[5][i] = vp(3, i) - vp(2, i);  // far
    }
    for (int p = 0; p < 6; ++p) {
        float len = std::sqrt(planes[p][0] * planes[p][0] +
                              planes[p][1] * planes[p][1] +
                              planes[p][2] * planes[p][2]);
        if (len > 0.0f) {
            float inv = 1.0f / len;
            planes[p][0] *= inv;
            planes[p][1] *= inv;
            planes[p][2] *= inv;
            planes[p][3] *= inv;
        }
    }

    for (auto& [model_id, mgpu] : models_gpu_) {
        if (mgpu.hidden || mgpu.active_draw_count == 0) continue;

        frame_draw_cmds_.push_back({mgpu.vao, {}, {}});
        auto& cmd = frame_draw_cmds_.back();
        cmd.counts.reserve(mgpu.active_draw_count);
        cmd.offsets.reserve(mgpu.active_draw_count);

        bool fully_loaded = (mgpu.active_draw_count == mgpu.draw_info.size());
        auto bvh_it = model_bvhs_.find(model_id);

        // Only use BVH if model is fully uploaded; during progressive upload,
        // fall back to linear scan of active objects.
        if (fully_loaded && bvh_it != model_bvhs_.end() && bvh_it->second) {
            const auto& bvh_set = *bvh_it->second;
            auto mbvh_it = bvh_set.models.find(model_id);
            if (mbvh_it != bvh_set.models.end()) {
                traverseBvh(mbvh_it->second, mgpu, planes);
            }
        } else {
            // Linear scan of active objects only.
            for (uint32_t i = 0; i < mgpu.active_draw_count; ++i) {
                const auto& obj = mgpu.draw_info[i];
                if (aabbInFrustum(obj.aabb_min, obj.aabb_max, planes)) {
                    cmd.counts.push_back(static_cast<GLsizei>(obj.index_count));
                    cmd.offsets.push_back(reinterpret_cast<const void*>(
                        static_cast<uintptr_t>(obj.index_offset)));
                    visible_triangles_ += obj.index_count / 3;
                }
            }
        }

        if (cmd.counts.empty()) {
            frame_draw_cmds_.pop_back();
        }
    }
}

void ViewportWindow::render() {
    if (!gl_initialized_ || !isExposed()) return;

    context_->makeCurrent(this);
    applyBvhResult();
    processPendingUploads();
    updateCamera();

    int w = width() * devicePixelRatio();
    int h = height() * devicePixelRatio();
    gl_->glViewport(0, 0, w, h);
    gl_->glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    QMatrix4x4 vp = proj_matrix_ * view_matrix_;

    gl_->glUseProgram(main_program_);
    gl_->glUniformMatrix4fv(gl_->glGetUniformLocation(main_program_, "u_view_projection"), 1, GL_FALSE, vp.constData());
    gl_->glUniform3f(gl_->glGetUniformLocation(main_program_, "u_light_dir"), 0.3f, 0.5f, 0.8f);
    gl_->glUniform1ui(gl_->glGetUniformLocation(main_program_, "u_selected_id"), selected_object_id_);

    buildVisibleList(vp);
    for (const auto& cmd : frame_draw_cmds_) {
        gl_->glBindVertexArray(cmd.vao);
        gl_->glMultiDrawElements(GL_TRIANGLES,
            cmd.counts.data(), GL_UNSIGNED_INT,
            cmd.offsets.data(),
            static_cast<GLsizei>(cmd.counts.size()));
    }

    renderAxisGizmo();

    context_->swapBuffers(this);

    // Compute FPS.
    float dt = frame_clock_.restart() / 1000.0f;
    accumulated_time_ += dt;
    frame_count_++;
    if (accumulated_time_ >= 1.0f) {
        last_fps_ = static_cast<float>(frame_count_) / accumulated_time_;
        frame_count_ = 0;
        accumulated_time_ = 0.0f;

        uint32_t total_obj = 0, total_tri = 0, vis_obj = 0;
        for (const auto& [mid, m] : models_gpu_) {
            if (!m.hidden) {
                total_obj += static_cast<uint32_t>(m.draw_info.size());
                total_tri += m.total_triangles;
            }
        }
        for (const auto& cmd : frame_draw_cmds_) {
            vis_obj += static_cast<uint32_t>(cmd.counts.size());
        }

        FrameStats stats;
        stats.fps = last_fps_;
        stats.frame_time_ms = 1000.0f / last_fps_;
        stats.total_objects = total_obj;
        stats.visible_objects = vis_obj;
        stats.total_triangles = total_tri;
        stats.visible_triangles = visible_triangles_;
        emit frameStatsUpdated(stats);
    }
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

    QVector3D eye_dir;
    eye_dir.setX(cosf(pitch_rad) * cosf(yaw_rad));
    eye_dir.setY(cosf(pitch_rad) * sinf(yaw_rad));
    eye_dir.setZ(sinf(pitch_rad));

    QMatrix4x4 gizmo_view;
    gizmo_view.lookAt(eye_dir * 3.0f, QVector3D(0, 0, 0), QVector3D(0, 0, 1));

    QMatrix4x4 gizmo_proj;
    gizmo_proj.ortho(-1.4f, 1.4f, -1.4f, 1.4f, 0.1f, 10.0f);

    QMatrix4x4 mvp = gizmo_proj * gizmo_view;

    gl_->glUseProgram(axis_program_);
    gl_->glUniformMatrix4fv(gl_->glGetUniformLocation(axis_program_, "u_mvp"), 1, GL_FALSE, mvp.constData());

    gl_->glLineWidth(2.5f);
    gl_->glBindVertexArray(axis_vao_);
    gl_->glDrawArrays(GL_LINES, 0, 6);

    gl_->glEnable(GL_DEPTH_TEST);
}

void ViewportWindow::renderPickPass() {
    gl_->glBindFramebuffer(GL_FRAMEBUFFER, pick_fbo_);
    gl_->glViewport(0, 0, pick_width_, pick_height_);

    GLuint clear_val = 0;
    gl_->glClearBufferuiv(GL_COLOR, 0, &clear_val);
    gl_->glClear(GL_DEPTH_BUFFER_BIT);

    QMatrix4x4 vp = proj_matrix_ * view_matrix_;
    gl_->glUseProgram(pick_program_);
    gl_->glUniformMatrix4fv(gl_->glGetUniformLocation(pick_program_, "u_view_projection"), 1, GL_FALSE, vp.constData());

    // Reuse the visible list from the most recent render() call.
    for (const auto& cmd : frame_draw_cmds_) {
        gl_->glBindVertexArray(cmd.vao);
        gl_->glMultiDrawElements(GL_TRIANGLES,
            cmd.counts.data(), GL_UNSIGNED_INT,
            cmd.offsets.data(),
            static_cast<GLsizei>(cmd.counts.size()));
    }

    gl_->glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void ViewportWindow::exposeEvent(QExposeEvent*) {
    if (isExposed() && !gl_initialized_) {
        initGL();
    }
}

void ViewportWindow::resizeEvent(QResizeEvent*) {
    if (gl_initialized_) render();
}

bool ViewportWindow::event(QEvent* e) {
    switch (e->type()) {
    case QEvent::MouseButtonPress:
        handleMousePress(static_cast<QMouseEvent*>(e));
        return true;
    case QEvent::MouseButtonRelease:
        handleMouseRelease(static_cast<QMouseEvent*>(e));
        return true;
    case QEvent::MouseMove:
        handleMouseMove(static_cast<QMouseEvent*>(e));
        return true;
    case QEvent::Wheel:
        handleWheel(static_cast<QWheelEvent*>(e));
        return true;
    default:
        return QWindow::event(e);
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
            QVector3D up(
                -sinf(pitch_rad) * cosf(yaw_rad),
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
