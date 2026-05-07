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

// ---- Triangle program (flat color) ----

const char* TRI_VS = R"(
#version 450 core
layout(location = 0) in vec3 in_pos;
uniform mat4 u_view_proj;
void main() {
    gl_Position = u_view_proj * vec4(in_pos, 1.0);
}
)";

const char* TRI_FS = R"(
#version 450 core
uniform vec4 u_color;
out vec4 frag_color;
void main() {
    frag_color = u_color;
}
)";

// ---- Point sprite program (outlined disc via gl_PointCoord) ----

const char* POINT_VS = R"(
#version 450 core
layout(location = 0) in vec3 in_pos;
uniform mat4  u_view_proj;
uniform float u_point_size;
void main() {
    gl_Position  = u_view_proj * vec4(in_pos, 1.0);
    gl_PointSize = u_point_size;
}
)";

// inner_radius_norm is the inner-disc radius as a fraction of the
// half-sprite (so 1.0 = no stroke, smaller = thicker stroke).  The
// fragment shader reads gl_PointCoord (range [0,1] across the sprite),
// computes the distance from the centre normalised against the half-
// sprite, and picks inner vs stroke from that.  ~1px AA at every band
// boundary using fwidth-style smoothstep with a narrow ramp.
const char* POINT_FS = R"(
#version 450 core
uniform vec4  u_inner_color;
uniform vec4  u_stroke_color;
uniform float u_inner_radius_norm;
out vec4 frag_color;
void main() {
    vec2 c = gl_PointCoord - 0.5;
    float d = length(c) * 2.0;             // 0 at centre, 1 at sprite edge
    if (d > 1.0) discard;
    float aa = fwidth(d) * 1.2;            // ~1px feather
    float t_inner = smoothstep(u_inner_radius_norm - aa,
                               u_inner_radius_norm + aa, d);
    vec4 col = mix(u_inner_color, u_stroke_color, t_inner);
    float outer_alpha = smoothstep(1.0, 1.0 - aa, d);
    frag_color = vec4(col.rgb, col.a * outer_alpha);
}
)";

// ---- Line program (screen-space-expanded quads with outline) ----
//
// Per-vertex layout: (in_a, in_b, in_side, in_along), 8 floats total.
// The vertex shader projects both endpoints to screen pixels, computes
// the screen-space perpendicular, and offsets *this* corner accordingly.
// Output v_dist_px is the signed perpendicular distance from the line
// axis at this corner; linear interpolation across the quad gives the
// per-fragment distance the FS uses to discard / pick inner vs stroke.

const char* LINE_VS = R"(
#version 450 core
layout(location = 0) in vec3  in_a;
layout(location = 1) in vec3  in_b;
layout(location = 2) in float in_side;     // -1 or +1
layout(location = 3) in float in_along;    // 0 (at a) or 1 (at b)
uniform mat4  u_view_proj;
uniform vec2  u_screen_size;               // physical pixels
uniform float u_half_width;                // inner half-width (px)
uniform float u_stroke_extra;              // halo per side (px)
out float v_dist_px;
void main() {
    vec4 clip_a = u_view_proj * vec4(in_a, 1.0);
    vec4 clip_b = u_view_proj * vec4(in_b, 1.0);

    // Project to screen pixels.
    vec2 screen_a = (clip_a.xy / clip_a.w) * 0.5 * u_screen_size;
    vec2 screen_b = (clip_b.xy / clip_b.w) * 0.5 * u_screen_size;

    vec2 delta = screen_b - screen_a;
    float len = length(delta);
    vec2 dir  = (len > 1e-6) ? (delta / len) : vec2(1.0, 0.0);
    vec2 perp = vec2(-dir.y, dir.x);

    // Offset this corner perpendicular to the line.
    vec4 clip_self    = mix(clip_a, clip_b, in_along);
    vec2 screen_self  = (clip_self.xy / clip_self.w) * 0.5 * u_screen_size;
    float total_half  = u_half_width + u_stroke_extra;
    screen_self      += perp * in_side * total_half;

    // Back to NDC, then to clip space (multiply by w to undo the w-divide
    // GL is about to apply).  Depth is preserved from the picked endpoint.
    vec2 ndc_out = screen_self / (u_screen_size * 0.5);
    gl_Position = vec4(ndc_out * clip_self.w, clip_self.z, clip_self.w);

    v_dist_px = in_side * total_half;
}
)";

// ---- Screen-space rect program (label + HUD backgrounds) ----
//
// Skip QPainter::fillRect entirely — on QOpenGLPaintDevice it's
// unreliable across drivers.  Backgrounds are drawn as raw GL quads
// using NDC-space coordinates; QPainter only renders the text on top.

const char* RECT_VS = R"(
#version 450 core
layout(location = 0) in vec2 in_ndc;
void main() {
    gl_Position = vec4(in_ndc, 0.0, 1.0);
}
)";

const char* RECT_FS = R"(
#version 450 core
uniform vec4 u_color;
out vec4 frag_color;
void main() {
    frag_color = u_color;
}
)";

const char* LINE_FS = R"(
#version 450 core
in float v_dist_px;
uniform vec4  u_inner_color;
uniform vec4  u_stroke_color;
uniform float u_half_width;
uniform float u_stroke_extra;
out vec4 frag_color;
void main() {
    float ad = abs(v_dist_px);
    float total = u_half_width + u_stroke_extra;
    if (ad > total) discard;

    // ~1px AA on the inner/stroke boundary and the outer edge.
    float t_stroke = smoothstep(u_half_width - 0.5, u_half_width + 0.5, ad);
    vec4  col      = mix(u_inner_color, u_stroke_color, t_stroke);
    float outer_a  = smoothstep(total, total - 1.0, ad);
    frag_color = vec4(col.rgb, col.a * outer_a);
}
)";

void uploadFloats(QOpenGLFunctions_4_5_Core* gl,
                  GLuint vbo, size_t& capacity_bytes,
                  const std::vector<float>& data) {
    const size_t bytes = data.size() * sizeof(float);
    if (bytes == 0) return;
    if (bytes > capacity_bytes) {
        const size_t new_cap = bytes + bytes / 2;
        gl->glNamedBufferData(vbo, GLsizeiptr(new_cap),
                              nullptr, GL_DYNAMIC_DRAW);
        capacity_bytes = new_cap;
    }
    gl->glNamedBufferSubData(vbo, 0, GLsizeiptr(bytes), data.data());
}

// CPU expansion of N segments (3 floats * 2 verts per segment, packed) into
// 6 vertices per segment, each carrying (a, b, side, along) = 8 floats.
void expandLineSegments(const std::vector<float>& endpoints,
                        std::vector<float>& out) {
    out.clear();
    if (endpoints.size() < 6) return;
    const size_t n_segs = endpoints.size() / 6;
    out.reserve(n_segs * 6 * 8);
    static const float CORNERS[6][2] = {
        {-1.0f, 0.0f}, {+1.0f, 0.0f}, {-1.0f, 1.0f},
        {-1.0f, 1.0f}, {+1.0f, 0.0f}, {+1.0f, 1.0f},
    };
    for (size_t s = 0; s < n_segs; ++s) {
        const float* a = &endpoints[s * 6 + 0];
        const float* b = &endpoints[s * 6 + 3];
        for (int c = 0; c < 6; ++c) {
            out.push_back(a[0]); out.push_back(a[1]); out.push_back(a[2]);
            out.push_back(b[0]); out.push_back(b[1]); out.push_back(b[2]);
            out.push_back(CORNERS[c][0]);
            out.push_back(CORNERS[c][1]);
        }
    }
}

} // namespace

void OverlayRenderer::initialize(QOpenGLFunctions_4_5_Core* gl) {
    if (gl_) return;
    gl_ = gl;

    // Triangle program.
    {
        GLuint vs = compile(gl_, GL_VERTEX_SHADER,   TRI_VS);
        GLuint fs = compile(gl_, GL_FRAGMENT_SHADER, TRI_FS);
        program_tri_     = link(gl_, vs, fs);
        u_tri_view_proj_ = gl_->glGetUniformLocation(program_tri_, "u_view_proj");
        u_tri_color_     = gl_->glGetUniformLocation(program_tri_, "u_color");
    }
    // Point program.
    {
        GLuint vs = compile(gl_, GL_VERTEX_SHADER,   POINT_VS);
        GLuint fs = compile(gl_, GL_FRAGMENT_SHADER, POINT_FS);
        program_pt_           = link(gl_, vs, fs);
        u_pt_view_proj_       = gl_->glGetUniformLocation(program_pt_, "u_view_proj");
        u_pt_point_size_      = gl_->glGetUniformLocation(program_pt_, "u_point_size");
        u_pt_inner_color_     = gl_->glGetUniformLocation(program_pt_, "u_inner_color");
        u_pt_stroke_color_    = gl_->glGetUniformLocation(program_pt_, "u_stroke_color");
        u_pt_inner_radius_    = gl_->glGetUniformLocation(program_pt_, "u_inner_radius_norm");
    }
    // Line program.
    {
        GLuint vs = compile(gl_, GL_VERTEX_SHADER,   LINE_VS);
        GLuint fs = compile(gl_, GL_FRAGMENT_SHADER, LINE_FS);
        program_ln_           = link(gl_, vs, fs);
        u_ln_view_proj_       = gl_->glGetUniformLocation(program_ln_, "u_view_proj");
        u_ln_screen_size_     = gl_->glGetUniformLocation(program_ln_, "u_screen_size");
        u_ln_half_width_      = gl_->glGetUniformLocation(program_ln_, "u_half_width");
        u_ln_stroke_extra_    = gl_->glGetUniformLocation(program_ln_, "u_stroke_extra");
        u_ln_inner_color_     = gl_->glGetUniformLocation(program_ln_, "u_inner_color");
        u_ln_stroke_color_    = gl_->glGetUniformLocation(program_ln_, "u_stroke_color");
    }
    // Screen-space rect program.
    {
        GLuint vs = compile(gl_, GL_VERTEX_SHADER,   RECT_VS);
        GLuint fs = compile(gl_, GL_FRAGMENT_SHADER, RECT_FS);
        program_rect_  = link(gl_, vs, fs);
        u_rect_color_  = gl_->glGetUniformLocation(program_rect_, "u_color");
    }

    // Triangle VAO/VBO: one vec3 attribute.
    gl_->glCreateVertexArrays(1, &triangles_.vao);
    gl_->glCreateBuffers(1, &triangles_.vbo);
    gl_->glEnableVertexArrayAttrib(triangles_.vao, 0);
    gl_->glVertexArrayAttribFormat(triangles_.vao, 0, 3, GL_FLOAT, GL_FALSE, 0);
    gl_->glVertexArrayAttribBinding(triangles_.vao, 0, 0);
    gl_->glVertexArrayVertexBuffer(triangles_.vao, 0, triangles_.vbo,
                                   0, 3 * sizeof(float));

    // Point VAO/VBO: one vec3 attribute.
    gl_->glCreateVertexArrays(1, &points_.vao);
    gl_->glCreateBuffers(1, &points_.vbo);
    gl_->glEnableVertexArrayAttrib(points_.vao, 0);
    gl_->glVertexArrayAttribFormat(points_.vao, 0, 3, GL_FLOAT, GL_FALSE, 0);
    gl_->glVertexArrayAttribBinding(points_.vao, 0, 0);
    gl_->glVertexArrayVertexBuffer(points_.vao, 0, points_.vbo,
                                   0, 3 * sizeof(float));

    // Line VAO/VBO: 8 floats per vertex (a:vec3, b:vec3, side, along).
    gl_->glCreateVertexArrays(1, &lines_.vao);
    gl_->glCreateBuffers(1, &lines_.vbo);
    const GLsizei stride = 8 * sizeof(float);
    gl_->glEnableVertexArrayAttrib(lines_.vao, 0);
    gl_->glVertexArrayAttribFormat(lines_.vao, 0, 3, GL_FLOAT, GL_FALSE, 0);
    gl_->glVertexArrayAttribBinding(lines_.vao, 0, 0);
    gl_->glEnableVertexArrayAttrib(lines_.vao, 1);
    gl_->glVertexArrayAttribFormat(lines_.vao, 1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float));
    gl_->glVertexArrayAttribBinding(lines_.vao, 1, 0);
    gl_->glEnableVertexArrayAttrib(lines_.vao, 2);
    gl_->glVertexArrayAttribFormat(lines_.vao, 2, 1, GL_FLOAT, GL_FALSE, 6 * sizeof(float));
    gl_->glVertexArrayAttribBinding(lines_.vao, 2, 0);
    gl_->glEnableVertexArrayAttrib(lines_.vao, 3);
    gl_->glVertexArrayAttribFormat(lines_.vao, 3, 1, GL_FLOAT, GL_FALSE, 7 * sizeof(float));
    gl_->glVertexArrayAttribBinding(lines_.vao, 3, 0);
    gl_->glVertexArrayVertexBuffer(lines_.vao, 0, lines_.vbo, 0, stride);

    // Screen-rect VAO/VBO: 2 floats per vertex (vec2 NDC).
    gl_->glCreateVertexArrays(1, &vao_rect_);
    gl_->glCreateBuffers(1, &vbo_rect_);
    gl_->glEnableVertexArrayAttrib(vao_rect_, 0);
    gl_->glVertexArrayAttribFormat(vao_rect_, 0, 2, GL_FLOAT, GL_FALSE, 0);
    gl_->glVertexArrayAttribBinding(vao_rect_, 0, 0);
    gl_->glVertexArrayVertexBuffer(vao_rect_, 0, vbo_rect_, 0, 2 * sizeof(float));
}

void OverlayRenderer::release() {
    if (!gl_) return;
    if (triangles_.vbo) gl_->glDeleteBuffers(1, &triangles_.vbo);
    if (triangles_.vao) gl_->glDeleteVertexArrays(1, &triangles_.vao);
    if (points_.vbo)    gl_->glDeleteBuffers(1, &points_.vbo);
    if (points_.vao)    gl_->glDeleteVertexArrays(1, &points_.vao);
    if (lines_.vbo)     gl_->glDeleteBuffers(1, &lines_.vbo);
    if (lines_.vao)     gl_->glDeleteVertexArrays(1, &lines_.vao);
    if (vbo_rect_)      gl_->glDeleteBuffers(1, &vbo_rect_);
    if (vao_rect_)      gl_->glDeleteVertexArrays(1, &vao_rect_);
    if (program_tri_)   gl_->glDeleteProgram(program_tri_);
    if (program_pt_)    gl_->glDeleteProgram(program_pt_);
    if (program_ln_)    gl_->glDeleteProgram(program_ln_);
    if (program_rect_)  gl_->glDeleteProgram(program_rect_);
    triangles_ = {};
    points_    = {};
    lines_     = {};
    vao_rect_  = vbo_rect_ = 0;
    vbo_rect_capacity_ = 0;
    program_tri_ = program_pt_ = program_ln_ = program_rect_ = 0;
    gl_ = nullptr;
}

void OverlayRenderer::setHudText(const QString& text) {
    hud_text_ = text;
}

void OverlayRenderer::setOverlayLabels(const std::vector<Label>& labels) {
    labels_ = labels;
}

void OverlayRenderer::setHighlightTriangles(const std::vector<float>& world_xyz,
                                             float r, float g, float b, float a) {
    if (!gl_) return;
    triangles_.color[0] = r; triangles_.color[1] = g;
    triangles_.color[2] = b; triangles_.color[3] = a;
    triangles_.vertex_count = GLsizei(world_xyz.size() / 3);
    uploadFloats(gl_, triangles_.vbo, triangles_.vbo_capacity, world_xyz);
}

void OverlayRenderer::setOverlayPoints(const std::vector<float>& world_xyz,
                                        float r, float g, float b, float a,
                                        float pixel_size,
                                        float sr, float sg, float sb, float sa,
                                        float stroke_extra) {
    if (!gl_) return;
    points_.inner_color[0]  = r;  points_.inner_color[1]  = g;
    points_.inner_color[2]  = b;  points_.inner_color[3]  = a;
    points_.stroke_color[0] = sr; points_.stroke_color[1] = sg;
    points_.stroke_color[2] = sb; points_.stroke_color[3] = sa;
    points_.pixel_size      = pixel_size;
    points_.stroke_extra    = stroke_extra;
    points_.vertex_count    = GLsizei(world_xyz.size() / 3);
    uploadFloats(gl_, points_.vbo, points_.vbo_capacity, world_xyz);
}

void OverlayRenderer::setOverlayLines(const std::vector<float>& world_xyz,
                                       float r, float g, float b, float a,
                                       float line_width,
                                       float sr, float sg, float sb, float sa,
                                       float stroke_extra) {
    if (!gl_) return;
    lines_.inner_color[0]  = r;  lines_.inner_color[1]  = g;
    lines_.inner_color[2]  = b;  lines_.inner_color[3]  = a;
    lines_.stroke_color[0] = sr; lines_.stroke_color[1] = sg;
    lines_.stroke_color[2] = sb; lines_.stroke_color[3] = sa;
    lines_.line_width      = line_width;
    lines_.stroke_extra    = stroke_extra;

    std::vector<float> expanded;
    expandLineSegments(world_xyz, expanded);
    lines_.vertex_count = GLsizei(expanded.size() / 8);
    uploadFloats(gl_, lines_.vbo, lines_.vbo_capacity, expanded);
}

void OverlayRenderer::render(const float view_proj[16],
                              int pixel_w, int pixel_h, qreal dpr) {
    if (!gl_) return;

    // Save GL state we touch.
    GLboolean prev_blend     = gl_->glIsEnabled(GL_BLEND);
    GLboolean prev_cull      = gl_->glIsEnabled(GL_CULL_FACE);
    GLboolean prev_pt_size   = gl_->glIsEnabled(GL_PROGRAM_POINT_SIZE);
    GLboolean prev_depth_msk = GL_TRUE;
    gl_->glGetBooleanv(GL_DEPTH_WRITEMASK, &prev_depth_msk);
    GLint prev_depth_func = GL_LESS;
    gl_->glGetIntegerv(GL_DEPTH_FUNC, &prev_depth_func);
    GLint prev_blend_src = GL_ONE, prev_blend_dst = GL_ZERO;
    gl_->glGetIntegerv(GL_BLEND_SRC_ALPHA, &prev_blend_src);
    gl_->glGetIntegerv(GL_BLEND_DST_ALPHA, &prev_blend_dst);

    gl_->glEnable(GL_BLEND);
    gl_->glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    gl_->glDisable(GL_CULL_FACE);
    gl_->glDepthMask(GL_FALSE);
    gl_->glDepthFunc(GL_LEQUAL);
    gl_->glEnable(GL_PROGRAM_POINT_SIZE);

    if (triangles_.vertex_count > 0 && triangles_.color[3] > 0.0f) {
        // Highlight triangles stay depth-aware (GL_LEQUAL) so they tint
        // the surface in place rather than poking through walls.
        gl_->glUseProgram(program_tri_);
        gl_->glUniformMatrix4fv(u_tri_view_proj_, 1, GL_FALSE, view_proj);
        gl_->glUniform4fv(u_tri_color_, 1, triangles_.color);
        gl_->glBindVertexArray(triangles_.vao);
        gl_->glDrawArrays(GL_TRIANGLES, 0, triangles_.vertex_count);
    }
    // Measurement annotations (lines + points) draw on top of every other
    // pass — the standard CAD convention.  GL_ALWAYS wins every depth
    // compare; GL_LEQUAL is restored at the end of the function.
    gl_->glDepthFunc(GL_ALWAYS);
    if (lines_.vertex_count > 0 && lines_.inner_color[3] > 0.0f) {
        gl_->glUseProgram(program_ln_);
        gl_->glUniformMatrix4fv(u_ln_view_proj_, 1, GL_FALSE, view_proj);
        gl_->glUniform2f(u_ln_screen_size_, float(pixel_w), float(pixel_h));
        gl_->glUniform1f(u_ln_half_width_,   lines_.line_width * 0.5f);
        gl_->glUniform1f(u_ln_stroke_extra_, lines_.stroke_extra);
        gl_->glUniform4fv(u_ln_inner_color_,  1, lines_.inner_color);
        gl_->glUniform4fv(u_ln_stroke_color_, 1, lines_.stroke_color);
        gl_->glBindVertexArray(lines_.vao);
        gl_->glDrawArrays(GL_TRIANGLES, 0, lines_.vertex_count);
    }
    if (points_.vertex_count > 0 && points_.inner_color[3] > 0.0f) {
        // Inner-radius ratio in [0, 1]: how much of the sprite is the
        // inner colour vs the stroke band.  pixel_size is the inner-disc
        // diameter; the sprite (and gl_PointSize) is enlarged by
        // 2*stroke_extra so the halo has somewhere to draw.
        const float total = points_.pixel_size + 2.0f * points_.stroke_extra;
        const float inner_ratio = (total > 0.0f)
            ? (points_.pixel_size / total) : 1.0f;
        gl_->glUseProgram(program_pt_);
        gl_->glUniformMatrix4fv(u_pt_view_proj_, 1, GL_FALSE, view_proj);
        gl_->glUniform1f(u_pt_point_size_, total);
        gl_->glUniform1f(u_pt_inner_radius_, inner_ratio);
        gl_->glUniform4fv(u_pt_inner_color_,  1, points_.inner_color);
        gl_->glUniform4fv(u_pt_stroke_color_, 1, points_.stroke_color);
        gl_->glBindVertexArray(points_.vao);
        gl_->glDrawArrays(GL_POINTS, 0, points_.vertex_count);
    }
    gl_->glBindVertexArray(0);

    if (!prev_blend)   gl_->glDisable(GL_BLEND);
    gl_->glBlendFunc(prev_blend_src, prev_blend_dst);
    if (prev_cull)     gl_->glEnable(GL_CULL_FACE);
    if (!prev_pt_size) gl_->glDisable(GL_PROGRAM_POINT_SIZE);
    gl_->glDepthMask(prev_depth_msk);
    gl_->glDepthFunc(prev_depth_func);

    // Two-stage HUD/label pass: collect rect bounds (in logical pixels) +
    // text strings, draw all rect backgrounds via GL (screen-space NDC
    // quads, depth test off), then run a QPainter pass that *only* draws
    // text on top.  Side-stepping QPainter::fillRect entirely avoids the
    // QOpenGLPaintDevice quirk where solid fills silently drop while
    // text continues to render.
    const bool any_painter = !hud_text_.isEmpty() || !labels_.empty();
    if (!any_painter || pixel_w <= 0 || pixel_h <= 0) return;

    const float logical_w = float(pixel_w) / float(dpr ? dpr : 1.0);
    const float logical_h = float(pixel_h) / float(dpr ? dpr : 1.0);

    QFont label_font("monospace", 9);
    label_font.setStyleHint(QFont::TypeWriter);
    QFont hud_font("monospace", 11);
    hud_font.setStyleHint(QFont::TypeWriter);
    const QFontMetrics lfm(label_font);
    const QFontMetrics hfm(hud_font);

    const int label_pad_x = 4, label_pad_y = 2;
    const int hud_pad_x   = 10, hud_pad_y = 6;
    const int hud_margin  = 12;

    struct PaintItem { QRect bg; QString text; const QFont* font; int align; };
    std::vector<PaintItem> items;
    items.reserve(labels_.size() + 1);

    // World-anchored label rects.
    for (const auto& lbl : labels_) {
        const float* p = lbl.world_pos;
        // Column-major: M[col*4 + row].
        const float wx = view_proj[0]*p[0] + view_proj[4]*p[1] + view_proj[8]*p[2]  + view_proj[12];
        const float wy = view_proj[1]*p[0] + view_proj[5]*p[1] + view_proj[9]*p[2]  + view_proj[13];
        const float ww = view_proj[3]*p[0] + view_proj[7]*p[1] + view_proj[11]*p[2] + view_proj[15];
        if (ww <= 0.0f) continue;             // behind camera
        const float ndc_x = wx / ww;
        const float ndc_y = wy / ww;
        if (ndc_x < -1.0f || ndc_x > 1.0f
         || ndc_y < -1.0f || ndc_y > 1.0f) continue;
        const float sx = (ndc_x * 0.5f + 0.5f) * logical_w;
        const float sy = (1.0f - (ndc_y * 0.5f + 0.5f)) * logical_h;
        const int tw = lfm.horizontalAdvance(lbl.text);
        const int th = lfm.height();
        QRect bg(int(sx) - tw / 2 - label_pad_x,
                 int(sy) - th / 2 - label_pad_y,
                 tw + 2 * label_pad_x,
                 th + 2 * label_pad_y);
        items.push_back({bg, lbl.text, &label_font, Qt::AlignCenter});
    }
    // HUD rect (always top-left if any text).
    if (!hud_text_.isEmpty()) {
        const QStringList lines = hud_text_.split('\n');
        int tw = 0;
        for (const auto& ln : lines) tw = qMax(tw, hfm.horizontalAdvance(ln));
        const int th = hfm.height() * lines.size();
        QRect bg(hud_margin, hud_margin,
                 tw + 2 * hud_pad_x,
                 th + 2 * hud_pad_y);
        items.push_back({bg, hud_text_, &hud_font, int(Qt::AlignLeft | Qt::AlignTop)});
    }

    // GL pass: draw all background rects as NDC-space triangles.
    if (!items.empty()) {
        std::vector<float> ndc;
        ndc.reserve(items.size() * 12);   // 6 verts * 2 floats per rect
        auto px_to_ndc_x = [logical_w](float px) {
            return (px / logical_w) * 2.0f - 1.0f;
        };
        auto px_to_ndc_y = [logical_h](float px) {
            return 1.0f - (px / logical_h) * 2.0f;
        };
        for (const auto& it : items) {
            const float x0 = px_to_ndc_x(float(it.bg.left()));
            const float x1 = px_to_ndc_x(float(it.bg.right() + 1));
            const float y0 = px_to_ndc_y(float(it.bg.top()));
            const float y1 = px_to_ndc_y(float(it.bg.bottom() + 1));
            ndc.insert(ndc.end(), {
                x0, y0,  x1, y0,  x0, y1,
                x0, y1,  x1, y0,  x1, y1
            });
        }
        const size_t bytes = ndc.size() * sizeof(float);
        if (bytes > vbo_rect_capacity_) {
            const size_t new_cap = bytes + bytes / 2;
            gl_->glNamedBufferData(vbo_rect_, GLsizeiptr(new_cap),
                                   nullptr, GL_DYNAMIC_DRAW);
            vbo_rect_capacity_ = new_cap;
        }
        gl_->glNamedBufferSubData(vbo_rect_, 0, GLsizeiptr(bytes), ndc.data());

        // GL_TRIANGLES respects GL_CULL_FACE; the NDC→window y-flip turns
        // our CCW NDC quads into window-CW which get back-culled if cull
        // is on (which it is by default in this app).  Disable cull for
        // the rect pass — lines+points above were unaffected since
        // GL_LINES / GL_POINTS skip face culling entirely.
        GLboolean prev_depth_test = gl_->glIsEnabled(GL_DEPTH_TEST);
        GLboolean prev_cull_face  = gl_->glIsEnabled(GL_CULL_FACE);
        gl_->glDisable(GL_DEPTH_TEST);
        gl_->glDisable(GL_CULL_FACE);
        gl_->glDisable(GL_BLEND);
        gl_->glUseProgram(program_rect_);
        gl_->glUniform4f(u_rect_color_, 0.08f, 0.08f, 0.08f, 1.0f);
        gl_->glBindVertexArray(vao_rect_);
        gl_->glDrawArrays(GL_TRIANGLES, 0, GLsizei(items.size() * 6));
        gl_->glBindVertexArray(0);
        if (prev_depth_test) gl_->glEnable(GL_DEPTH_TEST);
        if (prev_cull_face)  gl_->glEnable(GL_CULL_FACE);
    }

    // QPainter pass: text only, on top of the GL-drawn backgrounds.
    QOpenGLPaintDevice device(QSize(pixel_w, pixel_h));
    device.setDevicePixelRatio(dpr);
    QPainter painter(&device);
    painter.setRenderHint(QPainter::TextAntialiasing);
    painter.setPen(Qt::white);
    for (const auto& it : items) {
        painter.setFont(*it.font);
        const int px = it.font == &hud_font ? hud_pad_x : label_pad_x;
        const int py = it.font == &hud_font ? hud_pad_y : label_pad_y;
        painter.drawText(it.bg.adjusted(px, py, -px, -py), it.align, it.text);
    }
}
