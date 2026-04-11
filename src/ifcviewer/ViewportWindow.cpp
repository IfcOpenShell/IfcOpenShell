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

static const size_t INITIAL_VBO_SIZE = 64 * 1024 * 1024;  // 64 MB
static const size_t INITIAL_EBO_SIZE = 32 * 1024 * 1024;  // 32 MB
// Cap buffer growth so a runaway upload can't try to allocate the world.
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
    if (context_) {
        context_->makeCurrent(this);
        if (gl_) {
            if (vao_) gl_->glDeleteVertexArrays(1, &vao_);
            if (vbo_) gl_->glDeleteBuffers(1, &vbo_);
            if (ebo_) gl_->glDeleteBuffers(1, &ebo_);
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

    // Create VAO
    gl_->glCreateVertexArrays(1, &vao_);

    // Create VBO with initial capacity
    vbo_capacity_ = INITIAL_VBO_SIZE;
    gl_->glCreateBuffers(1, &vbo_);
    gl_->glNamedBufferStorage(vbo_, vbo_capacity_, nullptr,
        GL_DYNAMIC_STORAGE_BIT);

    // Create EBO with initial capacity
    ebo_capacity_ = INITIAL_EBO_SIZE;
    gl_->glCreateBuffers(1, &ebo_);
    gl_->glNamedBufferStorage(ebo_, ebo_capacity_, nullptr,
        GL_DYNAMIC_STORAGE_BIT);

    // Vertex layout: pos(3f) + normal(3f) + object_id(1f) + color(4 unorm bytes)
    // = 8 floats = 32 bytes per vertex.
    gl_->glVertexArrayVertexBuffer(vao_, 0, vbo_, 0, VERTEX_STRIDE * sizeof(float));
    gl_->glVertexArrayElementBuffer(vao_, ebo_);

    // position
    gl_->glEnableVertexArrayAttrib(vao_, 0);
    gl_->glVertexArrayAttribFormat(vao_, 0, 3, GL_FLOAT, GL_FALSE, 0);
    gl_->glVertexArrayAttribBinding(vao_, 0, 0);

    // normal
    gl_->glEnableVertexArrayAttrib(vao_, 1);
    gl_->glVertexArrayAttribFormat(vao_, 1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float));
    gl_->glVertexArrayAttribBinding(vao_, 1, 0);

    // object_id (passed as float, decoded in shader via floatBitsToUint)
    gl_->glEnableVertexArrayAttrib(vao_, 2);
    gl_->glVertexArrayAttribFormat(vao_, 2, 1, GL_FLOAT, GL_FALSE, 6 * sizeof(float));
    gl_->glVertexArrayAttribBinding(vao_, 2, 0);

    // color (RGBA8 packed into the 4 bytes at offset 28; normalized to vec4)
    gl_->glEnableVertexArrayAttrib(vao_, 3);
    gl_->glVertexArrayAttribFormat(vao_, 3, 4, GL_UNSIGNED_BYTE, GL_TRUE, 7 * sizeof(float));
    gl_->glVertexArrayAttribBinding(vao_, 3, 0);

    gl_->glEnable(GL_DEPTH_TEST);
    gl_->glEnable(GL_MULTISAMPLE);
    gl_->glClearColor(0.18f, 0.20f, 0.22f, 1.0f);

    gl_initialized_ = true;
    frame_clock_.start();
    render_timer_.start();

    emit initialized();
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
    // 3 line segments (X red, Y green, Z blue), 6 vertices, pos(3) + color(3).
    static const float axis_data[] = {
        // X axis - red
        0.0f, 0.0f, 0.0f,   1.0f, 0.25f, 0.25f,
        1.0f, 0.0f, 0.0f,   1.0f, 0.25f, 0.25f,
        // Y axis - green
        0.0f, 0.0f, 0.0f,   0.30f, 0.95f, 0.30f,
        0.0f, 1.0f, 0.0f,   0.30f, 0.95f, 0.30f,
        // Z axis - blue
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

bool ViewportWindow::growVbo(size_t needed_total) {
    // Double until it fits, but don't blow past the cap.
    size_t new_capacity = vbo_capacity_;
    while (new_capacity < needed_total) {
        new_capacity *= 2;
    }
    if (new_capacity > MAX_BUFFER_SIZE) {
        qWarning("VBO grow request (%zu MB) exceeds cap (%zu MB)",
            new_capacity / (1024 * 1024), MAX_BUFFER_SIZE / (1024 * 1024));
        return false;
    }

    GLuint new_vbo = 0;
    gl_->glCreateBuffers(1, &new_vbo);
    gl_->glNamedBufferStorage(new_vbo, new_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);

    if (vbo_used_ > 0) {
        gl_->glCopyNamedBufferSubData(vbo_, new_vbo, 0, 0, vbo_used_);
    }

    gl_->glDeleteBuffers(1, &vbo_);
    vbo_ = new_vbo;
    vbo_capacity_ = new_capacity;

    // Rebind on the VAO so subsequent draws see the new buffer.
    gl_->glVertexArrayVertexBuffer(vao_, 0, vbo_, 0, VERTEX_STRIDE * sizeof(float));

    qInfo("VBO grew to %zu MB", vbo_capacity_ / (1024 * 1024));
    return true;
}

bool ViewportWindow::growEbo(size_t needed_total) {
    size_t new_capacity = ebo_capacity_;
    while (new_capacity < needed_total) {
        new_capacity *= 2;
    }
    if (new_capacity > MAX_BUFFER_SIZE) {
        qWarning("EBO grow request (%zu MB) exceeds cap (%zu MB)",
            new_capacity / (1024 * 1024), MAX_BUFFER_SIZE / (1024 * 1024));
        return false;
    }

    GLuint new_ebo = 0;
    gl_->glCreateBuffers(1, &new_ebo);
    gl_->glNamedBufferStorage(new_ebo, new_capacity, nullptr, GL_DYNAMIC_STORAGE_BIT);

    if (ebo_used_ > 0) {
        gl_->glCopyNamedBufferSubData(ebo_, new_ebo, 0, 0, ebo_used_);
    }

    gl_->glDeleteBuffers(1, &ebo_);
    ebo_ = new_ebo;
    ebo_capacity_ = new_capacity;

    gl_->glVertexArrayElementBuffer(vao_, ebo_);

    qInfo("EBO grew to %zu MB", ebo_capacity_ / (1024 * 1024));
    return true;
}

void ViewportWindow::uploadChunk(const UploadChunk& chunk) {
    if (!gl_initialized_) return;
    if (chunk.vertices.empty() || chunk.indices.empty()) return;

    context_->makeCurrent(this);

    size_t vb_size = chunk.vertices.size() * sizeof(float);
    size_t ib_size = chunk.indices.size() * sizeof(uint32_t);

    if (vbo_used_ + vb_size > vbo_capacity_) {
        if (!growVbo(vbo_used_ + vb_size)) {
            qWarning("VBO at cap, skipping chunk");
            return;
        }
    }
    if (ebo_used_ + ib_size > ebo_capacity_) {
        if (!growEbo(ebo_used_ + ib_size)) {
            qWarning("EBO at cap, skipping chunk");
            return;
        }
    }

    uint32_t base_vertex = vertex_count_;

    gl_->glNamedBufferSubData(vbo_, vbo_used_, vb_size, chunk.vertices.data());

    // Remap chunk-local indices into global indices so the whole EBO can be
    // drawn with a single glDrawElements call.
    std::vector<uint32_t> global_indices(chunk.indices.size());
    for (size_t i = 0; i < chunk.indices.size(); ++i) {
        global_indices[i] = chunk.indices[i] + base_vertex;
    }
    gl_->glNamedBufferSubData(ebo_, ebo_used_, ib_size, global_indices.data());

    // Compute AABB from vertex positions in this chunk.
    ObjectDrawInfo info;
    info.index_offset = static_cast<uint32_t>(ebo_used_);
    info.index_count = static_cast<uint32_t>(chunk.indices.size());

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

    {
        std::lock_guard<std::mutex> lock(upload_mutex_);
        total_index_count_ += static_cast<uint32_t>(chunk.indices.size());
        object_draw_info_.push_back(info);
    }

    vbo_used_ += vb_size;
    ebo_used_ += ib_size;
    vertex_count_ += static_cast<uint32_t>(chunk.vertices.size() / VERTEX_STRIDE);
    total_triangles_ += static_cast<uint32_t>(chunk.indices.size() / 3);
}

void ViewportWindow::resetScene() {
    if (!gl_initialized_) return;

    std::lock_guard<std::mutex> lock(upload_mutex_);
    total_index_count_ = 0;
    vbo_used_ = 0;
    ebo_used_ = 0;
    vertex_count_ = 0;
    total_triangles_ = 0;
    selected_object_id_ = 0;
    object_draw_info_.clear();
}

void ViewportWindow::setSelectedObjectId(uint32_t id) {
    selected_object_id_ = id;
}

uint32_t ViewportWindow::pickObjectAt(int x, int y) {
    if (!gl_initialized_) return 0;

    context_->makeCurrent(this);

    int w = width() * devicePixelRatio();
    int h = height() * devicePixelRatio();

    // Create/resize pick FBO if needed
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

    // IFC / Blender convention: X right, Y forward, Z up.
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

void ViewportWindow::buildVisibleList(const QMatrix4x4& vp) {
    visible_counts_.clear();
    visible_offsets_.clear();
    visible_triangles_ = 0;

    std::lock_guard<std::mutex> lock(upload_mutex_);
    if (object_draw_info_.empty()) return;

    // Extract 6 frustum planes from the view-projection matrix.
    // Each plane is (a, b, c, d) where ax + by + cz + d >= 0 is inside.
    // QMatrix4x4 is stored column-major; operator(row, col) gives element.
    float planes[6][4];
    for (int i = 0; i < 4; ++i) {
        planes[0][i] = vp(3, i) + vp(0, i);  // left
        planes[1][i] = vp(3, i) - vp(0, i);  // right
        planes[2][i] = vp(3, i) + vp(1, i);  // bottom
        planes[3][i] = vp(3, i) - vp(1, i);  // top
        planes[4][i] = vp(3, i) + vp(2, i);  // near
        planes[5][i] = vp(3, i) - vp(2, i);  // far
    }
    // Normalize planes.
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

    visible_counts_.reserve(object_draw_info_.size());
    visible_offsets_.reserve(object_draw_info_.size());

    for (const auto& obj : object_draw_info_) {
        bool visible = true;
        for (int p = 0; p < 6; ++p) {
            // p-vertex: the AABB corner most in the direction of the plane normal.
            float px = planes[p][0] >= 0.0f ? obj.aabb_max[0] : obj.aabb_min[0];
            float py = planes[p][1] >= 0.0f ? obj.aabb_max[1] : obj.aabb_min[1];
            float pz = planes[p][2] >= 0.0f ? obj.aabb_max[2] : obj.aabb_min[2];
            float dist = planes[p][0] * px + planes[p][1] * py + planes[p][2] * pz + planes[p][3];
            if (dist < 0.0f) {
                visible = false;
                break;
            }
        }
        if (visible) {
            visible_counts_.push_back(static_cast<GLsizei>(obj.index_count));
            visible_offsets_.push_back(reinterpret_cast<const void*>(
                static_cast<uintptr_t>(obj.index_offset)));
            visible_triangles_ += obj.index_count / 3;
        }
    }
}

void ViewportWindow::render() {
    if (!gl_initialized_ || !isExposed()) return;

    context_->makeCurrent(this);
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

    gl_->glBindVertexArray(vao_);

    buildVisibleList(vp);
    if (!visible_counts_.empty()) {
        gl_->glMultiDrawElements(GL_TRIANGLES,
            visible_counts_.data(), GL_UNSIGNED_INT,
            visible_offsets_.data(),
            static_cast<GLsizei>(visible_counts_.size()));
    }

    renderAxisGizmo();

    context_->swapBuffers(this);

    // Compute FPS (updated once per second to avoid flicker).
    float dt = frame_clock_.restart() / 1000.0f;
    accumulated_time_ += dt;
    frame_count_++;
    if (accumulated_time_ >= 1.0f) {
        last_fps_ = static_cast<float>(frame_count_) / accumulated_time_;
        frame_count_ = 0;
        accumulated_time_ = 0.0f;

        FrameStats stats;
        stats.fps = last_fps_;
        stats.frame_time_ms = 1000.0f / last_fps_;
        stats.total_objects = static_cast<uint32_t>(object_draw_info_.size());
        stats.visible_objects = static_cast<uint32_t>(visible_counts_.size());
        stats.total_triangles = total_triangles_;
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

    // Build a view matrix from the same camera orientation but with a fixed
    // close-up distance, so the gizmo rotates with the scene camera. Z-up.
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

    gl_->glLineWidth(2.5f);  // ignored on some core-profile drivers, that's OK
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

    gl_->glBindVertexArray(vao_);

    // Reuse the visible list from the most recent render() call.
    if (!visible_counts_.empty()) {
        gl_->glMultiDrawElements(GL_TRIANGLES,
            visible_counts_.data(), GL_UNSIGNED_INT,
            visible_offsets_.data(),
            static_cast<GLsizei>(visible_counts_.size()));
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
            // Pan in screen space, derived from the Z-up camera basis.
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
            // Orbit
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
