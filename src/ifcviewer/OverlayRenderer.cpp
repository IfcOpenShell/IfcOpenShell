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

#include "OverlayRenderer.h"

#include <QFont>
#include <QFontMetrics>
#include <QPainter>
#include <QtGlobal>
#include <QtOpenGL/QOpenGLPaintDevice>

namespace {

GLuint compile(QOpenGLFunctions_4_5_Core* gl, GLenum type, const char* src) {
    GLuint s = gl->glCreateShader(type);
    gl->glShaderSource(s, 1, &src, nullptr);
    gl->glCompileShader(s);
    GLint ok = 0;
    gl->glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[2048];
        gl->glGetShaderInfoLog(s, sizeof(log), nullptr, log);
        qWarning("OverlayRenderer shader compile error: %s", log);
    }
    return s;
}

GLuint link(QOpenGLFunctions_4_5_Core* gl, GLuint vs, GLuint fs) {
    GLuint p = gl->glCreateProgram();
    gl->glAttachShader(p, vs);
    gl->glAttachShader(p, fs);
    gl->glLinkProgram(p);
    GLint ok = 0;
    gl->glGetProgramiv(p, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[2048];
        gl->glGetProgramInfoLog(p, sizeof(log), nullptr, log);
        qWarning("OverlayRenderer program link error: %s", log);
    }
    gl->glDeleteShader(vs);
    gl->glDeleteShader(fs);
    return p;
}

const char* VERT_SRC = R"(
#version 450 core
layout(location = 0) in vec3 in_pos;
uniform mat4 u_view_proj;
void main() {
    gl_Position = u_view_proj * vec4(in_pos, 1.0);
}
)";

const char* FRAG_SRC = R"(
#version 450 core
uniform vec4 u_color;
out vec4 frag_color;
void main() {
    frag_color = u_color;
}
)";

} // namespace

void OverlayRenderer::initialize(QOpenGLFunctions_4_5_Core* gl) {
    if (gl_) return;
    gl_ = gl;

    GLuint vs = compile(gl_, GL_VERTEX_SHADER,   VERT_SRC);
    GLuint fs = compile(gl_, GL_FRAGMENT_SHADER, FRAG_SRC);
    program_  = link(gl_, vs, fs);
    u_view_proj_ = gl_->glGetUniformLocation(program_, "u_view_proj");
    u_color_     = gl_->glGetUniformLocation(program_, "u_color");

    gl_->glCreateVertexArrays(1, &vao_);
    gl_->glCreateBuffers(1, &vbo_);
    gl_->glEnableVertexArrayAttrib(vao_, 0);
    gl_->glVertexArrayAttribFormat(vao_, 0, 3, GL_FLOAT, GL_FALSE, 0);
    gl_->glVertexArrayAttribBinding(vao_, 0, 0);
    gl_->glVertexArrayVertexBuffer(vao_, 0, vbo_, 0, 3 * sizeof(float));
}

void OverlayRenderer::release() {
    if (!gl_) return;
    if (vbo_)     gl_->glDeleteBuffers(1, &vbo_);
    if (vao_)     gl_->glDeleteVertexArrays(1, &vao_);
    if (program_) gl_->glDeleteProgram(program_);
    program_ = vao_ = vbo_ = 0;
    vbo_capacity_ = 0;
    vertex_count_ = 0;
    gl_ = nullptr;
}

void OverlayRenderer::setHudText(const QString& text) {
    hud_text_ = text;
}

void OverlayRenderer::setHighlightTriangles(const std::vector<float>& world_xyz,
                                             float r, float g, float b, float a) {
    if (!gl_) return;
    color_[0] = r; color_[1] = g; color_[2] = b; color_[3] = a;
    vertex_count_ = GLsizei(world_xyz.size() / 3);
    if (vertex_count_ == 0) return;

    const size_t bytes = world_xyz.size() * sizeof(float);
    if (bytes > vbo_capacity_) {
        // Grow with a little headroom so frequent appends don't realloc.
        const size_t new_cap = bytes + bytes / 2;
        gl_->glNamedBufferData(vbo_, GLsizeiptr(new_cap),
                               nullptr, GL_DYNAMIC_DRAW);
        vbo_capacity_ = new_cap;
    }
    gl_->glNamedBufferSubData(vbo_, 0, GLsizeiptr(bytes), world_xyz.data());
}

void OverlayRenderer::render(const float view_proj[16],
                              int pixel_w, int pixel_h, qreal dpr) {
    if (!gl_) return;

    // GL pass: tinted highlight triangles.
    if (program_ && vertex_count_ > 0 && color_[3] > 0.0f) {
        gl_->glUseProgram(program_);
        gl_->glUniformMatrix4fv(u_view_proj_, 1, GL_FALSE, view_proj);
        gl_->glUniform4fv(u_color_, 1, color_);

        // Save the GL state we touch and restore at the end so the rest of
        // the render pass keeps seeing what it expects.
        GLboolean prev_blend     = gl_->glIsEnabled(GL_BLEND);
        GLboolean prev_cull      = gl_->glIsEnabled(GL_CULL_FACE);
        GLboolean prev_depth_msk = GL_TRUE;
        gl_->glGetBooleanv(GL_DEPTH_WRITEMASK, &prev_depth_msk);
        GLint prev_depth_func = GL_LESS;
        gl_->glGetIntegerv(GL_DEPTH_FUNC, &prev_depth_func);
        GLint prev_blend_src = GL_ONE, prev_blend_dst = GL_ZERO;
        gl_->glGetIntegerv(GL_BLEND_SRC_ALPHA, &prev_blend_src);
        gl_->glGetIntegerv(GL_BLEND_DST_ALPHA, &prev_blend_dst);

        gl_->glEnable(GL_BLEND);
        gl_->glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        gl_->glDisable(GL_CULL_FACE);            // both sides tinted
        gl_->glDepthMask(GL_FALSE);              // tint, don't occlude
        gl_->glDepthFunc(GL_LEQUAL);             // win the coplanar fight

        gl_->glBindVertexArray(vao_);
        gl_->glDrawArrays(GL_TRIANGLES, 0, vertex_count_);
        gl_->glBindVertexArray(0);

        if (!prev_blend) gl_->glDisable(GL_BLEND);
        gl_->glBlendFunc(prev_blend_src, prev_blend_dst);
        if (prev_cull) gl_->glEnable(GL_CULL_FACE);
        gl_->glDepthMask(prev_depth_msk);
        gl_->glDepthFunc(prev_depth_func);
    }

    // QPainter pass: HUD text.  This rebinds programs/VAOs internally, so
    // it has to come after every other GL primitive in the overlay.
    if (!hud_text_.isEmpty() && pixel_w > 0 && pixel_h > 0) {
        QOpenGLPaintDevice device(QSize(pixel_w, pixel_h));
        device.setDevicePixelRatio(dpr);
        QPainter painter(&device);
        painter.setRenderHint(QPainter::Antialiasing);
        painter.setRenderHint(QPainter::TextAntialiasing);

        QFont font("monospace", 11);
        font.setStyleHint(QFont::TypeWriter);
        painter.setFont(font);
        const QFontMetrics fm(font);
        const int pad_x = 10, pad_y = 6, margin = 12;
        const int text_w = fm.horizontalAdvance(hud_text_);
        const int text_h = fm.height();
        const QRect bg(margin, margin,
                       text_w + 2 * pad_x,
                       text_h + 2 * pad_y);

        painter.setPen(Qt::NoPen);
        painter.setBrush(QColor(0, 0, 0, 160));
        painter.drawRoundedRect(bg, 4, 4);
        painter.setPen(Qt::white);
        painter.drawText(bg.adjusted(pad_x, pad_y, -pad_x, -pad_y),
                         Qt::AlignLeft | Qt::AlignVCenter,
                         hud_text_);
    }
}
