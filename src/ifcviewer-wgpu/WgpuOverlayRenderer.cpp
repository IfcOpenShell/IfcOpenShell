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

#include "WgpuOverlayRenderer.h"

#include <QFont>
#include <QFontMetrics>
#include <QImage>
#include <QPainter>
#include <QStringList>
#include <QtMath>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <vector>

// -----------------------------------------------------------------------------
// Local helpers
// -----------------------------------------------------------------------------

namespace {

WGPUStringView svFromCStr(const char* s) {
    WGPUStringView v{};
    v.data   = s;
    v.length = std::strlen(s);
    return v;
}

// Populate `attribs[5]` with the standard thick-line vertex layout:
//   loc 0: start (vec3 @ 0)   loc 1: end   (vec3 @ 12)
//   loc 2: col   (vec3 @ 24)  loc 3: t     (f32  @ 36)
//   loc 4: side  (f32  @ 40)
// Returns a WGPUVertexBufferLayout aliasing the caller-owned `attribs`.
WGPUVertexBufferLayout thickLineVertexLayout(WGPUVertexAttribute attribs[5]) {
    attribs[0].format = WGPUVertexFormat_Float32x3; attribs[0].offset = 0;  attribs[0].shaderLocation = 0;
    attribs[1].format = WGPUVertexFormat_Float32x3; attribs[1].offset = 12; attribs[1].shaderLocation = 1;
    attribs[2].format = WGPUVertexFormat_Float32x3; attribs[2].offset = 24; attribs[2].shaderLocation = 2;
    attribs[3].format = WGPUVertexFormat_Float32;   attribs[3].offset = 36; attribs[3].shaderLocation = 3;
    attribs[4].format = WGPUVertexFormat_Float32;   attribs[4].offset = 40; attribs[4].shaderLocation = 4;
    WGPUVertexBufferLayout vbl = {};
    vbl.arrayStride    = 44;
    vbl.stepMode       = WGPUVertexStepMode_Vertex;
    vbl.attributeCount = 5;
    vbl.attributes     = attribs;
    return vbl;
}

// Pack the axis uniform's 256-byte slot. Layout matches WGSL AxisUniforms:
// mat4 + vec3 + f32 + f32 + f32 + vec2 = 96 B used, padded to 256.
void packAxisUniform(uint8_t* dst,
                     const QMatrix4x4& mvp, const QVector3D& origin,
                     float arm, float alpha, float line_width_px,
                     float viewport_w, float viewport_h) {
    std::memset(dst, 0, 256);
    std::memcpy(dst, mvp.constData(), 16 * sizeof(float));
    float ox = origin.x(), oy = origin.y(), oz = origin.z();
    std::memcpy(dst + 64, &ox, sizeof(float));
    std::memcpy(dst + 68, &oy, sizeof(float));
    std::memcpy(dst + 72, &oz, sizeof(float));
    std::memcpy(dst + 76, &arm,           sizeof(float));
    std::memcpy(dst + 80, &alpha,         sizeof(float));
    std::memcpy(dst + 84, &line_width_px, sizeof(float));
    std::memcpy(dst + 88, &viewport_w,    sizeof(float));
    std::memcpy(dst + 92, &viewport_h,    sizeof(float));
}

// Pack the section uniform's 256-byte slot. Layout matches WGSL
// SectionUniforms: mat4 + 4×(vec3 + scalar pad) + vec4 + vec2 + 8 B pad
// = 160 B used, padded to 256.
void packSectionUniform(uint8_t* dst,
                        const QMatrix4x4& mvp,
                        const QVector3D& origin, float half_size,
                        const QVector3D& tangent, float line_width_px,
                        const QVector3D& bitangent,
                        const QVector3D& normal,
                        float r, float g, float b, float a,
                        float viewport_w, float viewport_h) {
    std::memset(dst, 0, 256);
    std::memcpy(dst, mvp.constData(), 16 * sizeof(float));
    auto put_vec3_pad = [&](size_t off, const QVector3D& v, float pad_val) {
        float vx = v.x(), vy = v.y(), vz = v.z();
        std::memcpy(dst + off + 0,  &vx, sizeof(float));
        std::memcpy(dst + off + 4,  &vy, sizeof(float));
        std::memcpy(dst + off + 8,  &vz, sizeof(float));
        std::memcpy(dst + off + 12, &pad_val, sizeof(float));
    };
    put_vec3_pad(64,  origin,    half_size);
    put_vec3_pad(80,  tangent,   line_width_px);
    put_vec3_pad(96,  bitangent, 0.0f);
    put_vec3_pad(112, normal,    0.0f);
    float tint[4] = { r, g, b, a };
    std::memcpy(dst + 128, tint, sizeof(tint));
    std::memcpy(dst + 144, &viewport_w, sizeof(float));
    std::memcpy(dst + 148, &viewport_h, sizeof(float));
}

}  // namespace

// -----------------------------------------------------------------------------
// Shared WGSL — VsOut + thick_line_clip helper + fs_main AA fragment
// -----------------------------------------------------------------------------

#define THICK_LINE_HELPERS_WGSL R"WGSL(
struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) color:  vec4<f32>,
    @location(1) side_t: f32,
};

fn thick_line_clip(p_start: vec4<f32>, p_end: vec4<f32>,
                   t: f32, side: f32,
                   viewport_size: vec2<f32>,
                   line_width_px: f32) -> vec4<f32> {
    let p_here = mix(p_start, p_end, t);
    let s_start = (p_start.xy / p_start.w) * viewport_size * 0.5;
    let s_end   = (p_end.xy   / p_end.w  ) * viewport_size * 0.5;
    let dir  = normalize(s_end - s_start);
    let perp = vec2<f32>(-dir.y, dir.x);
    let off_pixels = perp * (line_width_px * 0.5) * side;
    let off_ndc    = off_pixels * 2.0 / viewport_size;
    return vec4<f32>(p_here.xy + off_ndc * p_here.w, p_here.zw);
}

@fragment
fn fs_main(in: VsOut) -> @location(0) vec4<f32> {
    let d  = abs(in.side_t);
    let aa = fwidth(in.side_t);
    let coverage = 1.0 - smoothstep(1.0 - aa, 1.0, d);
    return vec4<f32>(in.color.xyz, in.color.w * coverage);
}
)WGSL"

static const char* AXIS_WGSL = THICK_LINE_HELPERS_WGSL R"WGSL(
struct AxisUniforms {
    mvp:           mat4x4<f32>,
    origin:        vec3<f32>,
    arm:           f32,
    alpha:         f32,
    line_width_px: f32,
    viewport_size: vec2<f32>,
};

@group(0) @binding(0) var<uniform> u: AxisUniforms;

@vertex
fn vs_main(@location(0) start: vec3<f32>,
           @location(1) end:   vec3<f32>,
           @location(2) col:   vec3<f32>,
           @location(3) t:     f32,
           @location(4) side:  f32) -> VsOut {
    let p_start = u.mvp * vec4<f32>(u.origin + start * u.arm, 1.0);
    let p_end   = u.mvp * vec4<f32>(u.origin + end   * u.arm, 1.0);
    var out: VsOut;
    out.clip_pos = thick_line_clip(p_start, p_end, t, side,
                                    u.viewport_size, u.line_width_px);
    out.color  = vec4<f32>(col, u.alpha);
    out.side_t = side;
    return out;
}
)WGSL";

static const char* SECTION_WGSL = THICK_LINE_HELPERS_WGSL R"WGSL(
struct SectionUniforms {
    mvp:           mat4x4<f32>,
    origin:        vec3<f32>,
    half_size:     f32,
    tangent:       vec3<f32>,
    line_width_px: f32,
    bitangent:     vec3<f32>,
    _pad1:         f32,
    normal:        vec3<f32>,
    _pad2:         f32,
    tint:          vec4<f32>,
    viewport_size: vec2<f32>,
    _pad3:         vec2<f32>,
};

@group(0) @binding(0) var<uniform> u: SectionUniforms;

fn plane_to_world(p: vec3<f32>) -> vec3<f32> {
    return u.origin + (u.tangent * p.x + u.bitangent * p.y + u.normal * p.z)
                      * u.half_size;
}

@vertex
fn vs_main(@location(0) start_local: vec3<f32>,
           @location(1) end_local:   vec3<f32>,
           @location(2) col:         vec3<f32>,
           @location(3) t:           f32,
           @location(4) side:        f32) -> VsOut {
    let p_start = u.mvp * vec4<f32>(plane_to_world(start_local), 1.0);
    let p_end   = u.mvp * vec4<f32>(plane_to_world(end_local),   1.0);
    var out: VsOut;
    out.clip_pos = thick_line_clip(p_start, p_end, t, side,
                                    u.viewport_size, u.line_width_px);
    out.color    = vec4<f32>(col * u.tint.xyz, u.tint.w);
    out.side_t   = side;
    return out;
}
)WGSL";

static const char* MARQUEE_WGSL = THICK_LINE_HELPERS_WGSL R"WGSL(
struct MarqueeUniforms {
    rect_min:      vec2<f32>,
    rect_max:      vec2<f32>,
    color:         vec4<f32>,
    viewport_size: vec2<f32>,
    line_width_px: f32,
    fill_alpha:    f32,
};

@group(0) @binding(0) var<uniform> u: MarqueeUniforms;

@vertex
fn vs_main(@location(0) start_uv: vec2<f32>,
           @location(1) end_uv:   vec2<f32>,
           @location(2) t:        f32,
           @location(3) side:     f32) -> VsOut {
    let p_start = vec4<f32>(mix(u.rect_min, u.rect_max, start_uv), 0.0, 1.0);
    let p_end   = vec4<f32>(mix(u.rect_min, u.rect_max, end_uv),   0.0, 1.0);
    var out: VsOut;
    out.clip_pos = thick_line_clip(p_start, p_end, t, side,
                                    u.viewport_size, u.line_width_px);
    out.color    = u.color;
    out.side_t   = side;
    return out;
}

struct VsFillOut {
    @builtin(position) clip_pos: vec4<f32>,
};

@vertex
fn vs_fill(@location(0) pos_uv: vec2<f32>) -> VsFillOut {
    var out: VsFillOut;
    let p = mix(u.rect_min, u.rect_max, pos_uv);
    out.clip_pos = vec4<f32>(p, 0.0, 1.0);
    return out;
}

@fragment
fn fs_fill() -> @location(0) vec4<f32> {
    return vec4<f32>(u.color.xyz, u.color.w * u.fill_alpha);
}
)WGSL";

// Overlay-line shader: world-space segments expanded into screen-space
// quads. Same expansion strategy as the GL OverlayRenderer LINE_VS/FS pair —
// per-vertex (a, b, side, along), per-fragment signed-perpendicular distance
// for stroke pick and arc length for dash. Lives in its own module because
// the FS needs the dash/stroke logic that the shared thick-line helper
// doesn't carry (axis / section / marquee never dash).
static const char* OVERLAY_LINES_WGSL = R"WGSL(
struct LineUniforms {
    view_proj:      mat4x4<f32>,
    inner_color:    vec4<f32>,
    stroke_color:   vec4<f32>,
    viewport_size:  vec2<f32>,
    line_width_px:  f32,    // inner full-width (px)
    stroke_extra:   f32,    // halo per side (px)
    dash_period_px: f32,    // 0 = solid
    dash_on_ratio:  f32,
};
@group(0) @binding(0) var<uniform> u: LineUniforms;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) dist_px:  f32,    // signed perpendicular distance (px)
    @location(1) along_px: f32,    // arc length from segment start (px)
};

@vertex
fn vs_main(@location(0) a:     vec3<f32>,
           @location(1) b:     vec3<f32>,
           @location(2) side:  f32,
           @location(3) along: f32) -> VsOut {
    let clip_a = u.view_proj * vec4<f32>(a, 1.0);
    let clip_b = u.view_proj * vec4<f32>(b, 1.0);
    let s_a = (clip_a.xy / clip_a.w) * 0.5 * u.viewport_size;
    let s_b = (clip_b.xy / clip_b.w) * 0.5 * u.viewport_size;
    let delta = s_b - s_a;
    let len   = length(delta);
    var dir   = vec2<f32>(1.0, 0.0);
    if (len > 1e-6) { dir = delta / len; }
    let perp = vec2<f32>(-dir.y, dir.x);

    let clip_self = mix(clip_a, clip_b, along);
    var s_self    = (clip_self.xy / clip_self.w) * 0.5 * u.viewport_size;
    let half_total = u.line_width_px * 0.5 + u.stroke_extra;
    s_self = s_self + perp * side * half_total;

    let ndc_out = s_self / (u.viewport_size * 0.5);
    var out: VsOut;
    out.clip_pos = vec4<f32>(ndc_out * clip_self.w, clip_self.z, clip_self.w);
    out.dist_px  = side * half_total;
    out.along_px = along * len;
    return out;
}

@fragment
fn fs_main(in: VsOut) -> @location(0) vec4<f32> {
    if (u.dash_period_px > 0.0) {
        let t = in.along_px - floor(in.along_px / u.dash_period_px) * u.dash_period_px;
        if (t > u.dash_period_px * u.dash_on_ratio) { discard; }
    }
    let ad         = abs(in.dist_px);
    let half_inner = u.line_width_px * 0.5;
    let total      = half_inner + u.stroke_extra;
    if (ad > total) { discard; }
    var col = u.inner_color;
    if (ad > half_inner) { col = u.stroke_color; }
    let outer_a = smoothstep(total, total - 1.0, ad);
    return vec4<f32>(col.xyz, col.w * outer_a);
}
)WGSL";

// Overlay-point shader: world-space positions expanded into screen-space
// quads (sprite size = inner_diameter + 2*stroke_extra). The FS does the
// sprite-distance pick + AA — same shape as GL OverlayRenderer's POINT_FS
// but reads `corner` from a vertex varying instead of gl_PointCoord
// because WebGPU has no point primitive with a sized sprite.
static const char* OVERLAY_POINTS_WGSL = R"WGSL(
struct PointUniforms {
    view_proj:         mat4x4<f32>,
    inner_color:       vec4<f32>,
    stroke_color:      vec4<f32>,
    viewport_size:     vec2<f32>,
    total_half_px:     f32,   // (inner_diameter + 2*stroke_extra) * 0.5
    inner_radius_norm: f32,   // inner_radius / total_half  ∈ (0, 1]
};
@group(0) @binding(0) var<uniform> u: PointUniforms;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) corner: vec2<f32>,
};

@vertex
fn vs_main(@location(0) world_pos: vec3<f32>,
           @location(1) corner:    vec2<f32>) -> VsOut {
    let clip = u.view_proj * vec4<f32>(world_pos, 1.0);
    let ndc  = clip.xy / clip.w;
    let s    = ndc * 0.5 * u.viewport_size;
    let s_off = s + corner * u.total_half_px;
    let ndc_out = s_off / (u.viewport_size * 0.5);
    var out: VsOut;
    out.clip_pos = vec4<f32>(ndc_out * clip.w, clip.z, clip.w);
    out.corner   = corner;
    return out;
}

@fragment
fn fs_main(in: VsOut) -> @location(0) vec4<f32> {
    let d = length(in.corner);
    if (d > 1.0) { discard; }
    var col = u.inner_color;
    if (d > u.inner_radius_norm) { col = u.stroke_color; }
    let aa    = fwidth(d);
    let outer = 1.0 - smoothstep(1.0 - aa, 1.0, d);
    return vec4<f32>(col.xyz, col.w * outer);
}
)WGSL";

// Label shader: textured quads in screen space. Each visible label/HUD
// item contributes 6 vertices (NDC position + uv); a pre-rasterised
// QImage carrying both the dark-grey background fill and the white
// text occupies the bound texture. Standard alpha blend.
static const char* LABELS_WGSL = R"WGSL(
@group(0) @binding(0) var samp: sampler;
@group(0) @binding(1) var tex:  texture_2d<f32>;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) uv: vec2<f32>,
};

@vertex
fn vs_main(@location(0) ndc: vec2<f32>,
           @location(1) uv:  vec2<f32>) -> VsOut {
    var out: VsOut;
    out.clip_pos = vec4<f32>(ndc, 0.0, 1.0);
    out.uv       = uv;
    return out;
}

@fragment
fn fs_main(in: VsOut) -> @location(0) vec4<f32> {
    return textureSample(tex, samp, in.uv);
}
)WGSL";

// -----------------------------------------------------------------------------
// Construction / destruction
// -----------------------------------------------------------------------------

WgpuOverlayRenderer::~WgpuOverlayRenderer() {
    destroy();
}

bool WgpuOverlayRenderer::init(WGPUInstance instance, WGPUDevice device,
                               WGPUQueue queue, WGPUTextureFormat surface_format,
                               int sample_count) {
    instance_       = instance;
    device_         = device;
    queue_          = queue;
    surface_format_ = surface_format;
    sample_count_   = sample_count;
    if (!buildAxisIndicator())     return false;
    if (!buildSectionVisualizer()) return false;
    if (!buildMarquee())           return false;
    if (!buildOverlayLines())      return false;
    if (!buildOverlayPoints())     return false;
    if (!buildLabels())            return false;
    return true;
}

void WgpuOverlayRenderer::destroy() {
    // Axis indicator
    if (axis_bind_group_)         { wgpuBindGroupRelease(axis_bind_group_);              axis_bind_group_ = nullptr; }
    if (axis_pivot_pipeline_)     { wgpuRenderPipelineRelease(axis_pivot_pipeline_);     axis_pivot_pipeline_ = nullptr; }
    if (axis_pivot_xray_pipeline_){ wgpuRenderPipelineRelease(axis_pivot_xray_pipeline_); axis_pivot_xray_pipeline_ = nullptr; }
    if (axis_corner_pipeline_)    { wgpuRenderPipelineRelease(axis_corner_pipeline_);    axis_corner_pipeline_ = nullptr; }
    if (axis_shader_module_)      { wgpuShaderModuleRelease(axis_shader_module_);        axis_shader_module_ = nullptr; }
    if (axis_pipeline_layout_)    { wgpuPipelineLayoutRelease(axis_pipeline_layout_);    axis_pipeline_layout_ = nullptr; }
    if (axis_bgl_)                { wgpuBindGroupLayoutRelease(axis_bgl_);               axis_bgl_ = nullptr; }
    if (axis_uniform_buffer_)     { wgpuBufferRelease(axis_uniform_buffer_);             axis_uniform_buffer_ = nullptr; }
    if (axis_vertex_buffer_)      { wgpuBufferRelease(axis_vertex_buffer_);              axis_vertex_buffer_ = nullptr; }

    // Section visualizer
    if (section_bind_group_)      { wgpuBindGroupRelease(section_bind_group_);          section_bind_group_ = nullptr; }
    if (section_pipeline_)        { wgpuRenderPipelineRelease(section_pipeline_);       section_pipeline_ = nullptr; }
    if (section_shader_module_)   { wgpuShaderModuleRelease(section_shader_module_);    section_shader_module_ = nullptr; }
    if (section_pipeline_layout_) { wgpuPipelineLayoutRelease(section_pipeline_layout_); section_pipeline_layout_ = nullptr; }
    if (section_bgl_)             { wgpuBindGroupLayoutRelease(section_bgl_);           section_bgl_ = nullptr; }
    if (section_uniform_buffer_)  { wgpuBufferRelease(section_uniform_buffer_);         section_uniform_buffer_ = nullptr; }
    if (section_vertex_buffer_)   { wgpuBufferRelease(section_vertex_buffer_);          section_vertex_buffer_ = nullptr; }

    // Marquee
    if (marquee_bind_group_)         { wgpuBindGroupRelease(marquee_bind_group_);              marquee_bind_group_ = nullptr; }
    if (marquee_pipeline_)           { wgpuRenderPipelineRelease(marquee_pipeline_);           marquee_pipeline_ = nullptr; }
    if (marquee_fill_pipeline_)      { wgpuRenderPipelineRelease(marquee_fill_pipeline_);      marquee_fill_pipeline_ = nullptr; }
    if (marquee_shader_module_)      { wgpuShaderModuleRelease(marquee_shader_module_);        marquee_shader_module_ = nullptr; }
    if (marquee_pipeline_layout_)    { wgpuPipelineLayoutRelease(marquee_pipeline_layout_);    marquee_pipeline_layout_ = nullptr; }
    if (marquee_bgl_)                { wgpuBindGroupLayoutRelease(marquee_bgl_);               marquee_bgl_ = nullptr; }
    if (marquee_uniform_buffer_)     { wgpuBufferRelease(marquee_uniform_buffer_);             marquee_uniform_buffer_ = nullptr; }
    if (marquee_vertex_buffer_)      { wgpuBufferRelease(marquee_vertex_buffer_);              marquee_vertex_buffer_ = nullptr; }
    if (marquee_fill_vertex_buffer_) { wgpuBufferRelease(marquee_fill_vertex_buffer_);         marquee_fill_vertex_buffer_ = nullptr; }

    // Overlay lines
    if (overlay_line_bind_group_)      { wgpuBindGroupRelease(overlay_line_bind_group_);          overlay_line_bind_group_ = nullptr; }
    if (overlay_line_pipeline_)        { wgpuRenderPipelineRelease(overlay_line_pipeline_);       overlay_line_pipeline_ = nullptr; }
    if (overlay_line_shader_module_)   { wgpuShaderModuleRelease(overlay_line_shader_module_);    overlay_line_shader_module_ = nullptr; }
    if (overlay_line_pipeline_layout_) { wgpuPipelineLayoutRelease(overlay_line_pipeline_layout_); overlay_line_pipeline_layout_ = nullptr; }
    if (overlay_line_bgl_)             { wgpuBindGroupLayoutRelease(overlay_line_bgl_);           overlay_line_bgl_ = nullptr; }
    if (overlay_line_uniform_buffer_)  { wgpuBufferRelease(overlay_line_uniform_buffer_);         overlay_line_uniform_buffer_ = nullptr; }
    if (overlay_line_vertex_buffer_)   { wgpuBufferRelease(overlay_line_vertex_buffer_);          overlay_line_vertex_buffer_ = nullptr; }
    overlay_line_vertex_capacity_ = 0;
    overlay_line_uniform_slots_   = 0;
    overlay_line_draws_.clear();

    // Overlay points
    if (overlay_point_bind_group_)      { wgpuBindGroupRelease(overlay_point_bind_group_);          overlay_point_bind_group_ = nullptr; }
    if (overlay_point_pipeline_)        { wgpuRenderPipelineRelease(overlay_point_pipeline_);       overlay_point_pipeline_ = nullptr; }
    if (overlay_point_shader_module_)   { wgpuShaderModuleRelease(overlay_point_shader_module_);    overlay_point_shader_module_ = nullptr; }
    if (overlay_point_pipeline_layout_) { wgpuPipelineLayoutRelease(overlay_point_pipeline_layout_); overlay_point_pipeline_layout_ = nullptr; }
    if (overlay_point_bgl_)             { wgpuBindGroupLayoutRelease(overlay_point_bgl_);           overlay_point_bgl_ = nullptr; }
    if (overlay_point_uniform_buffer_)  { wgpuBufferRelease(overlay_point_uniform_buffer_);         overlay_point_uniform_buffer_ = nullptr; }
    if (overlay_point_vertex_buffer_)   { wgpuBufferRelease(overlay_point_vertex_buffer_);          overlay_point_vertex_buffer_ = nullptr; }
    overlay_point_vertex_capacity_ = 0;
    overlay_point_vertex_count_    = 0;

    // Labels + HUD
    releaseLabelTextures();
    if (label_sampler_)          { wgpuSamplerRelease(label_sampler_);                 label_sampler_ = nullptr; }
    if (label_pipeline_)         { wgpuRenderPipelineRelease(label_pipeline_);         label_pipeline_ = nullptr; }
    if (label_shader_module_)    { wgpuShaderModuleRelease(label_shader_module_);      label_shader_module_ = nullptr; }
    if (label_pipeline_layout_)  { wgpuPipelineLayoutRelease(label_pipeline_layout_);  label_pipeline_layout_ = nullptr; }
    if (label_bgl_)              { wgpuBindGroupLayoutRelease(label_bgl_);             label_bgl_ = nullptr; }
    if (label_vertex_buffer_)    { wgpuBufferRelease(label_vertex_buffer_);            label_vertex_buffer_ = nullptr; }
    label_vertex_capacity_ = 0;
    labels_.clear();
    hud_text_.clear();
}

// -----------------------------------------------------------------------------
// Axis indicator
// -----------------------------------------------------------------------------

bool WgpuOverlayRenderer::buildAxisIndicator() {
    // Bonsai decorator palette (src/bonsai/bonsai/bim/ui.py:593+):
    //   decorator_color_error    = (1.000, 0.200, 0.322) — red    → +X
    //   decorator_color_selected = (0.545, 0.863, 0.000) — green  → +Y
    //   decorator_color_special  = (0.157, 0.565, 1.000) — blue   → +Z
    // Same palette is reused for the section gizmo + marquee so all overlay
    // colours come from one canonical source.
    static const float axis_verts[] = {
        //  start         end           color (RGB — Bonsai decorators)  t    side
        // ---- +X red ----
         0,0,0,         1,0,0,        1.000f, 0.200f, 0.322f,  0.f,  -1.f,
         0,0,0,         1,0,0,        1.000f, 0.200f, 0.322f,  0.f,  +1.f,
         0,0,0,         1,0,0,        1.000f, 0.200f, 0.322f,  1.f,  -1.f,
         0,0,0,         1,0,0,        1.000f, 0.200f, 0.322f,  1.f,  -1.f,
         0,0,0,         1,0,0,        1.000f, 0.200f, 0.322f,  0.f,  +1.f,
         0,0,0,         1,0,0,        1.000f, 0.200f, 0.322f,  1.f,  +1.f,
        // ---- +Y green ----
         0,0,0,         0,1,0,        0.545f, 0.863f, 0.000f,  0.f,  -1.f,
         0,0,0,         0,1,0,        0.545f, 0.863f, 0.000f,  0.f,  +1.f,
         0,0,0,         0,1,0,        0.545f, 0.863f, 0.000f,  1.f,  -1.f,
         0,0,0,         0,1,0,        0.545f, 0.863f, 0.000f,  1.f,  -1.f,
         0,0,0,         0,1,0,        0.545f, 0.863f, 0.000f,  0.f,  +1.f,
         0,0,0,         0,1,0,        0.545f, 0.863f, 0.000f,  1.f,  +1.f,
        // ---- +Z blue ----
         0,0,0,         0,0,1,        0.157f, 0.565f, 1.000f,  0.f,  -1.f,
         0,0,0,         0,0,1,        0.157f, 0.565f, 1.000f,  0.f,  +1.f,
         0,0,0,         0,0,1,        0.157f, 0.565f, 1.000f,  1.f,  -1.f,
         0,0,0,         0,0,1,        0.157f, 0.565f, 1.000f,  1.f,  -1.f,
         0,0,0,         0,0,1,        0.157f, 0.565f, 1.000f,  0.f,  +1.f,
         0,0,0,         0,0,1,        0.157f, 0.565f, 1.000f,  1.f,  +1.f,
    };
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = sizeof(axis_verts);
        bdesc.label = svFromCStr("ifcviewer-wgpu.axis_vbo");
        axis_vertex_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
        wgpuQueueWriteBuffer(queue_, axis_vertex_buffer_, 0, axis_verts, sizeof(axis_verts));
    }
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        bdesc.size  = 3u * kAxisUniformSlotSize;
        bdesc.label = svFromCStr("ifcviewer-wgpu.axis_uniforms");
        axis_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
    }
    {
        WGPUBindGroupLayoutEntry entry = {};
        entry.binding    = 0;
        entry.visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
        entry.buffer.type             = WGPUBufferBindingType_Uniform;
        entry.buffer.hasDynamicOffset = 1;
        entry.buffer.minBindingSize   = 96;
        WGPUBindGroupLayoutDescriptor bgl_desc = {};
        bgl_desc.entryCount = 1;
        bgl_desc.entries    = &entry;
        bgl_desc.label      = svFromCStr("ifcviewer-wgpu.axis_bgl");
        axis_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);
    }
    {
        WGPUPipelineLayoutDescriptor pl_desc = {};
        pl_desc.bindGroupLayoutCount = 1;
        pl_desc.bindGroupLayouts     = &axis_bgl_;
        pl_desc.label                = svFromCStr("ifcviewer-wgpu.axis_pipeline_layout");
        axis_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);
    }
    {
        WGPUBindGroupEntry entry = {};
        entry.binding = 0;
        entry.buffer  = axis_uniform_buffer_;
        entry.offset  = 0;
        entry.size    = kAxisUniformSlotSize;
        WGPUBindGroupDescriptor bg_desc = {};
        bg_desc.layout     = axis_bgl_;
        bg_desc.entryCount = 1;
        bg_desc.entries    = &entry;
        bg_desc.label      = svFromCStr("ifcviewer-wgpu.axis_bind_group");
        axis_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg_desc);
    }
    {
        WGPUShaderSourceWGSL wgsl_src = {};
        wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
        wgsl_src.code        = svFromCStr(AXIS_WGSL);
        WGPUShaderModuleDescriptor sm_desc = {};
        sm_desc.nextInChain = &wgsl_src.chain;
        sm_desc.label       = svFromCStr("ifcviewer-wgpu.axis_wgsl");
        axis_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);
    }

    WGPUVertexAttribute attribs[5] = {};
    WGPUVertexBufferLayout vbl = thickLineVertexLayout(attribs);

    WGPUBlendState blend = {};
    blend.color.srcFactor = WGPUBlendFactor_SrcAlpha;
    blend.color.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.color.operation = WGPUBlendOperation_Add;
    blend.alpha.srcFactor = WGPUBlendFactor_One;
    blend.alpha.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.alpha.operation = WGPUBlendOperation_Add;

    auto build_pivot = [&](WGPUCompareFunction cmp, const char* label,
                           WGPURenderPipeline& out) {
        WGPUColorTargetState ct = {};
        ct.format    = surface_format_;
        ct.blend     = &blend;
        ct.writeMask = WGPUColorWriteMask_All;

        WGPUFragmentState frag = {};
        frag.module      = axis_shader_module_;
        frag.entryPoint  = svFromCStr("fs_main");
        frag.targetCount = 1;
        frag.targets     = &ct;

        WGPUDepthStencilState depth = {};
        depth.format               = WGPUTextureFormat_Depth32Float;
        depth.depthWriteEnabled    = WGPUOptionalBool_False;
        depth.depthCompare         = cmp;
        depth.stencilFront.compare = WGPUCompareFunction_Always;
        depth.stencilBack.compare  = WGPUCompareFunction_Always;

        WGPURenderPipelineDescriptor rp_desc = {};
        rp_desc.layout              = axis_pipeline_layout_;
        rp_desc.label               = svFromCStr(label);
        rp_desc.vertex.module       = axis_shader_module_;
        rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
        rp_desc.vertex.bufferCount  = 1;
        rp_desc.vertex.buffers      = &vbl;
        rp_desc.fragment            = &frag;
        rp_desc.depthStencil        = &depth;
        rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
        rp_desc.primitive.cullMode  = WGPUCullMode_None;
        rp_desc.multisample.count   = uint32_t(sample_count_);
        rp_desc.multisample.mask    = 0xFFFFFFFFu;
        out = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    };
    build_pivot(WGPUCompareFunction_LessEqual,
                "ifcviewer-wgpu.axis_pivot_pipeline",
                axis_pivot_pipeline_);
    build_pivot(WGPUCompareFunction_GreaterEqual,
                "ifcviewer-wgpu.axis_pivot_xray_pipeline",
                axis_pivot_xray_pipeline_);

    // Corner: resolved surface, no depth, sampleCount=1.
    {
        WGPUColorTargetState ct = {};
        ct.format    = surface_format_;
        ct.blend     = &blend;
        ct.writeMask = WGPUColorWriteMask_All;

        WGPUFragmentState frag = {};
        frag.module      = axis_shader_module_;
        frag.entryPoint  = svFromCStr("fs_main");
        frag.targetCount = 1;
        frag.targets     = &ct;

        WGPURenderPipelineDescriptor rp_desc = {};
        rp_desc.layout              = axis_pipeline_layout_;
        rp_desc.label               = svFromCStr("ifcviewer-wgpu.axis_corner_pipeline");
        rp_desc.vertex.module       = axis_shader_module_;
        rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
        rp_desc.vertex.bufferCount  = 1;
        rp_desc.vertex.buffers      = &vbl;
        rp_desc.fragment            = &frag;
        rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
        rp_desc.primitive.cullMode  = WGPUCullMode_None;
        rp_desc.multisample.count   = 1;
        rp_desc.multisample.mask    = 0xFFFFFFFFu;
        axis_corner_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    }

    return axis_pivot_pipeline_ && axis_pivot_xray_pipeline_
        && axis_corner_pipeline_;
}

void WgpuOverlayRenderer::encodePivot(WGPURenderPassEncoder pass,
                                      const WgpuOverlayFrame& f,
                                      bool visible) {
    if (!visible || !axis_pivot_pipeline_ || !axis_pivot_xray_pipeline_) return;
    if (f.viewport_h_px <= 0) return;

    // Arm length = 30 logical px projected into world at the pivot's distance.
    const float fovy_rad        = qDegreesToRadians(f.camera_fov_y_deg);
    const float world_per_pixel = f.camera_distance * std::tan(fovy_rad * 0.5f)
                                  * 2.0f / float(f.viewport_h_px);
    const float arm_pixels = 30.0f * float(f.device_pixel_ratio);
    const float arm_world  = arm_pixels * world_per_pixel;

    const float dpr     = float(f.device_pixel_ratio);
    const float line_w  = 2.5f * dpr;
    const float vw      = float(f.viewport_w_px);
    const float vh      = float(f.viewport_h_px);

    uint8_t slot_visible[256];
    uint8_t slot_xray[256];
    packAxisUniform(slot_visible, f.view_proj, f.camera_target, arm_world,
                    1.00f, line_w, vw, vh);
    packAxisUniform(slot_xray,    f.view_proj, f.camera_target, arm_world,
                    0.30f, line_w, vw, vh);
    const uint32_t visible_off = 1u * kAxisUniformSlotSize;
    const uint32_t xray_off    = 2u * kAxisUniformSlotSize;
    wgpuQueueWriteBuffer(queue_, axis_uniform_buffer_, visible_off,
                         slot_visible, sizeof(slot_visible));
    wgpuQueueWriteBuffer(queue_, axis_uniform_buffer_, xray_off,
                         slot_xray, sizeof(slot_xray));

    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, axis_vertex_buffer_, 0,
                                         WGPU_WHOLE_SIZE);
    wgpuRenderPassEncoderSetPipeline(pass, axis_pivot_xray_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, axis_bind_group_, 1, &xray_off);
    wgpuRenderPassEncoderDraw(pass, 18, 1, 0, 0);
    wgpuRenderPassEncoderSetPipeline(pass, axis_pivot_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, axis_bind_group_, 1, &visible_off);
    wgpuRenderPassEncoderDraw(pass, 18, 1, 0, 0);
}

void WgpuOverlayRenderer::encodeCornerAxis(WGPUCommandEncoder enc,
                                           WGPUTextureView surface_view,
                                           const WgpuOverlayFrame& f) {
    if (!axis_corner_pipeline_ || !surface_view) return;
    const int dpr = std::max(1, f.device_pixel_ratio);
    const uint32_t gizmo_size = uint32_t(110 * dpr);
    const uint32_t margin     = uint32_t(10 * dpr);
    if (gizmo_size == 0 || f.viewport_w_px <= 0 || f.viewport_h_px <= 0) return;
    // Bottom-left in WebGPU framebuffer space (y down).
    const uint32_t fb_h = uint32_t(f.viewport_h_px);
    if (gizmo_size + margin > fb_h) return;
    const uint32_t y = fb_h - margin - gizmo_size;

    // Independent ortho projection from the camera's direction. Near the
    // poles the up axis collapses against the look direction, so swap to
    // Y-up there — mirrors buildViewProj's identical fix on the viewport.
    const float yaw_rad   = qDegreesToRadians(f.camera_yaw_deg);
    const float pitch_rad = qDegreesToRadians(f.camera_pitch_deg);
    const QVector3D eye_dir(std::cos(pitch_rad) * std::cos(yaw_rad),
                            std::cos(pitch_rad) * std::sin(yaw_rad),
                            std::sin(pitch_rad));
    const QVector3D world_up = (std::abs(f.camera_pitch_deg) >= 89.0f)
                                 ? QVector3D(0.0f, 1.0f, 0.0f)
                                 : QVector3D(0.0f, 0.0f, 1.0f);
    QMatrix4x4 gv;
    gv.lookAt(eye_dir * 3.0f, QVector3D(0, 0, 0), world_up);
    QMatrix4x4 gp;
    gp.ortho(-1.4f, 1.4f, -1.4f, 1.4f, 0.1f, 10.0f);
    QMatrix4x4 z_remap;
    z_remap(2, 2) = 0.5f;
    z_remap(2, 3) = 0.5f;
    const QMatrix4x4 mvp = z_remap * gp * gv;

    uint8_t slot[256];
    const float line_w = 2.5f * float(dpr);
    packAxisUniform(slot, mvp, QVector3D(0, 0, 0), 1.0f, 1.0f, line_w,
                    float(gizmo_size), float(gizmo_size));
    const uint32_t slot_offset = 0u;
    wgpuQueueWriteBuffer(queue_, axis_uniform_buffer_, slot_offset, slot, sizeof(slot));

    WGPURenderPassColorAttachment color = {};
    color.view       = surface_view;
    color.loadOp     = WGPULoadOp_Load;
    color.storeOp    = WGPUStoreOp_Store;
    color.clearValue = { 0.0, 0.0, 0.0, 1.0 };
    color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount = 1;
    pass_desc.colorAttachments     = &color;
    pass_desc.label                = svFromCStr("ifcviewer-wgpu.corner_axis_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetViewport(pass, float(margin), float(y),
                                     float(gizmo_size), float(gizmo_size),
                                     0.0f, 1.0f);
    wgpuRenderPassEncoderSetPipeline(pass, axis_corner_pipeline_);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, axis_vertex_buffer_, 0,
                                         WGPU_WHOLE_SIZE);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, axis_bind_group_, 1, &slot_offset);
    wgpuRenderPassEncoderDraw(pass, 18, 1, 0, 0);
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);
}

// -----------------------------------------------------------------------------
// Section plane visualizer
// -----------------------------------------------------------------------------

bool WgpuOverlayRenderer::buildSectionVisualizer() {
    struct Seg {
        std::array<float, 3> s, e;
        std::array<float, 3> c;
    };
    static constexpr std::array<float, 3> kSectionRed = {1.000f, 0.200f, 0.322f};
    static const Seg segs[] = {
        // ---- quad outline ----
        { {-1, -1, 0}, { 1, -1, 0}, kSectionRed },
        { { 1, -1, 0}, { 1,  1, 0}, kSectionRed },
        { { 1,  1, 0}, {-1,  1, 0}, kSectionRed },
        { {-1,  1, 0}, {-1, -1, 0}, kSectionRed },
        // ---- arrow shaft along +n ----
        { { 0, 0, 0}, { 0, 0, 1}, kSectionRed },
        // ---- arrow head: 4 diagonals from tip to ring at z = 0.78 ----
        { { 0, 0, 1}, {-0.18f,  0,     0.78f}, kSectionRed },
        { { 0, 0, 1}, { 0.18f,  0,     0.78f}, kSectionRed },
        { { 0, 0, 1}, { 0,     -0.18f, 0.78f}, kSectionRed },
        { { 0, 0, 1}, { 0,      0.18f, 0.78f}, kSectionRed },
    };
    std::vector<float> verts;
    verts.reserve(std::size(segs) * 6 * 11);
    auto push_v = [&](const Seg& s, float t, float side) {
        verts.insert(verts.end(), { s.s[0], s.s[1], s.s[2],
                                     s.e[0], s.e[1], s.e[2],
                                     s.c[0], s.c[1], s.c[2],
                                     t, side });
    };
    for (const auto& s : segs) {
        push_v(s, 0.f, -1.f); push_v(s, 0.f, +1.f); push_v(s, 1.f, -1.f);
        push_v(s, 1.f, -1.f); push_v(s, 0.f, +1.f); push_v(s, 1.f, +1.f);
    }
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = verts.size() * sizeof(float);
        bdesc.label = svFromCStr("ifcviewer-wgpu.section_gizmo_vbo");
        section_vertex_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
        wgpuQueueWriteBuffer(queue_, section_vertex_buffer_, 0,
                             verts.data(), verts.size() * sizeof(float));
    }
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        bdesc.size  = uint64_t(kMaxSectionPlanes) * kSectionUniformSlotSize;
        bdesc.label = svFromCStr("ifcviewer-wgpu.section_uniforms");
        section_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
    }
    {
        WGPUBindGroupLayoutEntry entry = {};
        entry.binding    = 0;
        entry.visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
        entry.buffer.type             = WGPUBufferBindingType_Uniform;
        entry.buffer.hasDynamicOffset = 1;
        entry.buffer.minBindingSize   = 160;
        WGPUBindGroupLayoutDescriptor bgl_desc = {};
        bgl_desc.entryCount = 1;
        bgl_desc.entries    = &entry;
        bgl_desc.label      = svFromCStr("ifcviewer-wgpu.section_bgl");
        section_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);
    }
    {
        WGPUPipelineLayoutDescriptor pl_desc = {};
        pl_desc.bindGroupLayoutCount = 1;
        pl_desc.bindGroupLayouts     = &section_bgl_;
        pl_desc.label                = svFromCStr("ifcviewer-wgpu.section_pipeline_layout");
        section_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);
    }
    {
        WGPUBindGroupEntry entry = {};
        entry.binding = 0;
        entry.buffer  = section_uniform_buffer_;
        entry.offset  = 0;
        entry.size    = kSectionUniformSlotSize;
        WGPUBindGroupDescriptor bg_desc = {};
        bg_desc.layout     = section_bgl_;
        bg_desc.entryCount = 1;
        bg_desc.entries    = &entry;
        bg_desc.label      = svFromCStr("ifcviewer-wgpu.section_bind_group");
        section_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg_desc);
    }
    {
        WGPUShaderSourceWGSL wgsl_src = {};
        wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
        wgsl_src.code        = svFromCStr(SECTION_WGSL);
        WGPUShaderModuleDescriptor sm_desc = {};
        sm_desc.nextInChain = &wgsl_src.chain;
        sm_desc.label       = svFromCStr("ifcviewer-wgpu.section_wgsl");
        section_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);
    }

    WGPUVertexAttribute attribs[5] = {};
    WGPUVertexBufferLayout vbl = thickLineVertexLayout(attribs);

    WGPUBlendState blend = {};
    blend.color.srcFactor = WGPUBlendFactor_SrcAlpha;
    blend.color.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.color.operation = WGPUBlendOperation_Add;
    blend.alpha.srcFactor = WGPUBlendFactor_One;
    blend.alpha.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.alpha.operation = WGPUBlendOperation_Add;

    WGPUColorTargetState ct = {};
    ct.format    = surface_format_;
    ct.blend     = &blend;
    ct.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = section_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &ct;

    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_False;
    depth.depthCompare         = WGPUCompareFunction_LessEqual;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = section_pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.section_pipeline");
    rp_desc.vertex.module       = section_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 1;
    rp_desc.vertex.buffers      = &vbl;
    rp_desc.fragment            = &frag;
    rp_desc.depthStencil        = &depth;
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode  = WGPUCullMode_None;
    rp_desc.multisample.count   = uint32_t(sample_count_);
    rp_desc.multisample.mask    = 0xFFFFFFFFu;
    section_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);

    return section_pipeline_ != nullptr;
}

void WgpuOverlayRenderer::encodeSectionGizmos(WGPURenderPassEncoder pass,
                                              const WgpuOverlayFrame& f,
                                              const std::vector<WgpuSectionPlane>& planes) {
    if (!section_pipeline_ || planes.empty()) return;

    wgpuRenderPassEncoderSetPipeline(pass, section_pipeline_);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, section_vertex_buffer_, 0,
                                         WGPU_WHOLE_SIZE);

    const int n = std::min<int>(int(planes.size()), kMaxSectionPlanes);
    for (int i = 0; i < n; ++i) {
        const WgpuSectionPlane& p = planes[i];

        // Stable in-plane basis: pick the world axis least parallel to n
        // so the cross-product stays well-conditioned at any orientation.
        QVector3D nn = p.n.normalized();
        const float ax = std::abs(nn.x()), ay = std::abs(nn.y()), az = std::abs(nn.z());
        QVector3D seed = (ax < ay && ax < az) ? QVector3D(1, 0, 0)
                       : (ay < az)             ? QVector3D(0, 1, 0)
                                               : QVector3D(0, 0, 1);
        QVector3D tangent = QVector3D::crossProduct(nn, seed);
        if (tangent.lengthSquared() < 1e-12f) tangent = QVector3D(1, 0, 0);
        tangent.normalize();
        QVector3D bitangent = QVector3D::crossProduct(nn, tangent).normalized();

        // Fixed 1 m half-size matches GL's renderSectionPlanes constant.
        const float half_size = 1.0f;
        const float dpr       = float(std::max(1, f.device_pixel_ratio));
        const float line_w    = 5.0f * dpr;
        const float vw        = float(f.viewport_w_px);
        const float vh        = float(f.viewport_h_px);

        uint8_t slot[256];
        // Neutral tint — actual colours come from the per-vertex VBO
        // (red quad outline + red arrow). Tint stays available for a
        // future "selected" multiplier.
        packSectionUniform(slot, f.view_proj, p.origin, half_size,
                           tangent, line_w, bitangent, nn,
                           1.0f, 1.0f, 1.0f, 1.0f,
                           vw, vh);
        const uint32_t slot_offset = uint32_t(i) * kSectionUniformSlotSize;
        wgpuQueueWriteBuffer(queue_, section_uniform_buffer_,
                             slot_offset, slot, sizeof(slot));

        wgpuRenderPassEncoderSetBindGroup(pass, 0, section_bind_group_,
                                          1, &slot_offset);
        wgpuRenderPassEncoderDraw(pass, 54, 1, 0, 0);
    }
}

// -----------------------------------------------------------------------------
// Marquee
// -----------------------------------------------------------------------------

bool WgpuOverlayRenderer::buildMarquee() {
    struct Seg { std::array<float, 2> s, e; };
    static const Seg segs[] = {
        { {0, 0}, {1, 0} },
        { {1, 0}, {1, 1} },
        { {1, 1}, {0, 1} },
        { {0, 1}, {0, 0} },
    };
    std::vector<float> verts;
    verts.reserve(std::size(segs) * 6 * 6);
    auto push_v = [&](const Seg& s, float t, float side) {
        verts.insert(verts.end(), { s.s[0], s.s[1], s.e[0], s.e[1], t, side });
    };
    for (const auto& s : segs) {
        push_v(s, 0.f, -1.f); push_v(s, 0.f, +1.f); push_v(s, 1.f, -1.f);
        push_v(s, 1.f, -1.f); push_v(s, 0.f, +1.f); push_v(s, 1.f, +1.f);
    }
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = verts.size() * sizeof(float);
        bdesc.label = svFromCStr("ifcviewer-wgpu.marquee_vbo");
        marquee_vertex_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
        wgpuQueueWriteBuffer(queue_, marquee_vertex_buffer_, 0,
                             verts.data(), verts.size() * sizeof(float));
    }
    static const float fill_verts[] = {
        0, 0,   1, 0,   1, 1,
        0, 0,   1, 1,   0, 1,
    };
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = sizeof(fill_verts);
        bdesc.label = svFromCStr("ifcviewer-wgpu.marquee_fill_vbo");
        marquee_fill_vertex_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
        wgpuQueueWriteBuffer(queue_, marquee_fill_vertex_buffer_, 0,
                             fill_verts, sizeof(fill_verts));
    }
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        bdesc.size  = 64;
        bdesc.label = svFromCStr("ifcviewer-wgpu.marquee_uniforms");
        marquee_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
    }
    {
        WGPUBindGroupLayoutEntry entry = {};
        entry.binding    = 0;
        entry.visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
        entry.buffer.type             = WGPUBufferBindingType_Uniform;
        entry.buffer.hasDynamicOffset = 0;
        entry.buffer.minBindingSize   = 48;
        WGPUBindGroupLayoutDescriptor bgl_desc = {};
        bgl_desc.entryCount = 1;
        bgl_desc.entries    = &entry;
        bgl_desc.label      = svFromCStr("ifcviewer-wgpu.marquee_bgl");
        marquee_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);
    }
    {
        WGPUPipelineLayoutDescriptor pl_desc = {};
        pl_desc.bindGroupLayoutCount = 1;
        pl_desc.bindGroupLayouts     = &marquee_bgl_;
        pl_desc.label                = svFromCStr("ifcviewer-wgpu.marquee_pipeline_layout");
        marquee_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);
    }
    {
        WGPUBindGroupEntry entry = {};
        entry.binding = 0;
        entry.buffer  = marquee_uniform_buffer_;
        entry.offset  = 0;
        entry.size    = 64;
        WGPUBindGroupDescriptor bg_desc = {};
        bg_desc.layout     = marquee_bgl_;
        bg_desc.entryCount = 1;
        bg_desc.entries    = &entry;
        bg_desc.label      = svFromCStr("ifcviewer-wgpu.marquee_bind_group");
        marquee_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg_desc);
    }
    {
        WGPUShaderSourceWGSL wgsl_src = {};
        wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
        wgsl_src.code        = svFromCStr(MARQUEE_WGSL);
        WGPUShaderModuleDescriptor sm_desc = {};
        sm_desc.nextInChain = &wgsl_src.chain;
        sm_desc.label       = svFromCStr("ifcviewer-wgpu.marquee_wgsl");
        marquee_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);
    }

    // Vertex layout: start_uv(vec2) + end_uv(vec2) + t(f32) + side(f32),
    // stride 24.
    WGPUVertexAttribute attribs[4] = {};
    attribs[0].format = WGPUVertexFormat_Float32x2; attribs[0].offset = 0;  attribs[0].shaderLocation = 0;
    attribs[1].format = WGPUVertexFormat_Float32x2; attribs[1].offset = 8;  attribs[1].shaderLocation = 1;
    attribs[2].format = WGPUVertexFormat_Float32;   attribs[2].offset = 16; attribs[2].shaderLocation = 2;
    attribs[3].format = WGPUVertexFormat_Float32;   attribs[3].offset = 20; attribs[3].shaderLocation = 3;
    WGPUVertexBufferLayout vbl = {};
    vbl.arrayStride    = 24;
    vbl.stepMode       = WGPUVertexStepMode_Vertex;
    vbl.attributeCount = 4;
    vbl.attributes     = attribs;

    WGPUBlendState blend = {};
    blend.color.srcFactor = WGPUBlendFactor_SrcAlpha;
    blend.color.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.color.operation = WGPUBlendOperation_Add;
    blend.alpha.srcFactor = WGPUBlendFactor_One;
    blend.alpha.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.alpha.operation = WGPUBlendOperation_Add;

    WGPUColorTargetState ct = {};
    ct.format    = surface_format_;
    ct.blend     = &blend;
    ct.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = marquee_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &ct;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = marquee_pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.marquee_pipeline");
    rp_desc.vertex.module       = marquee_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 1;
    rp_desc.vertex.buffers      = &vbl;
    rp_desc.fragment            = &frag;
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode  = WGPUCullMode_None;
    rp_desc.multisample.count   = 1;
    rp_desc.multisample.mask    = 0xFFFFFFFFu;
    marquee_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);

    WGPUVertexAttribute fill_attribs[1] = {};
    fill_attribs[0].format = WGPUVertexFormat_Float32x2;
    fill_attribs[0].offset = 0;
    fill_attribs[0].shaderLocation = 0;
    WGPUVertexBufferLayout fill_vbl = {};
    fill_vbl.arrayStride    = 8;
    fill_vbl.stepMode       = WGPUVertexStepMode_Vertex;
    fill_vbl.attributeCount = 1;
    fill_vbl.attributes     = fill_attribs;

    WGPUFragmentState fill_frag = {};
    fill_frag.module      = marquee_shader_module_;
    fill_frag.entryPoint  = svFromCStr("fs_fill");
    fill_frag.targetCount = 1;
    fill_frag.targets     = &ct;

    WGPURenderPipelineDescriptor fill_rp_desc = rp_desc;
    fill_rp_desc.label              = svFromCStr("ifcviewer-wgpu.marquee_fill_pipeline");
    fill_rp_desc.vertex.entryPoint  = svFromCStr("vs_fill");
    fill_rp_desc.vertex.bufferCount = 1;
    fill_rp_desc.vertex.buffers     = &fill_vbl;
    fill_rp_desc.fragment           = &fill_frag;
    marquee_fill_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &fill_rp_desc);

    return marquee_pipeline_ != nullptr && marquee_fill_pipeline_ != nullptr;
}

void WgpuOverlayRenderer::encodeMarquee(WGPUCommandEncoder enc,
                                        WGPUTextureView surface_view,
                                        const WgpuOverlayFrame& f,
                                        QPoint start_logical_px,
                                        QPoint current_logical_px,
                                        bool active) {
    if (!marquee_pipeline_ || !surface_view) return;
    if (!active) return;
    if (f.viewport_w_px <= 0 || f.viewport_h_px <= 0) return;

    const float w = float(f.viewport_w_px);
    const float h = float(f.viewport_h_px);
    const float dpr = float(std::max(1, f.device_pixel_ratio));
    const float lx0 = float(std::min(start_logical_px.x(),
                                     current_logical_px.x())) * dpr;
    const float ly0 = float(std::min(start_logical_px.y(),
                                     current_logical_px.y())) * dpr;
    const float lx1 = float(std::max(start_logical_px.x(),
                                     current_logical_px.x())) * dpr;
    const float ly1 = float(std::max(start_logical_px.y(),
                                     current_logical_px.y())) * dpr;
    if (lx1 <= lx0 || ly1 <= ly0) return;

    const float nx0 = (lx0 / w) * 2.0f - 1.0f;
    const float nx1 = (lx1 / w) * 2.0f - 1.0f;
    const float ny_top    = 1.0f - 2.0f * ly0 / h;
    const float ny_bottom = 1.0f - 2.0f * ly1 / h;

    // Bonsai decorator_color_special (axis +Z blue): 0.157, 0.565, 1.000.
    // Outline alpha 0.95; fill_alpha (multiplied onto that) gives ~0.19
    // alpha for the translucent fill.
    float uniforms[16] = {};
    uniforms[0]  = nx0;       uniforms[1]  = ny_top;
    uniforms[2]  = nx1;       uniforms[3]  = ny_bottom;
    uniforms[4]  = 0.157f;    uniforms[5]  = 0.565f;
    uniforms[6]  = 1.000f;    uniforms[7]  = 0.95f;
    uniforms[8]  = w;         uniforms[9]  = h;
    uniforms[10] = 3.0f * dpr;
    uniforms[11] = 0.20f;
    wgpuQueueWriteBuffer(queue_, marquee_uniform_buffer_, 0,
                         uniforms, 12 * sizeof(float));

    WGPURenderPassColorAttachment color = {};
    color.view       = surface_view;
    color.loadOp     = WGPULoadOp_Load;
    color.storeOp    = WGPUStoreOp_Store;
    color.clearValue = { 0, 0, 0, 1 };
    color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount = 1;
    pass_desc.colorAttachments     = &color;
    pass_desc.label                = svFromCStr("ifcviewer-wgpu.marquee_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, marquee_bind_group_, 0, nullptr);

    wgpuRenderPassEncoderSetPipeline(pass, marquee_fill_pipeline_);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, marquee_fill_vertex_buffer_,
                                         0, WGPU_WHOLE_SIZE);
    wgpuRenderPassEncoderDraw(pass, 6, 1, 0, 0);

    wgpuRenderPassEncoderSetPipeline(pass, marquee_pipeline_);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, marquee_vertex_buffer_, 0,
                                         WGPU_WHOLE_SIZE);
    wgpuRenderPassEncoderDraw(pass, 24, 1, 0, 0);

    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);
}

// -----------------------------------------------------------------------------
// Overlay lines
// -----------------------------------------------------------------------------

bool WgpuOverlayRenderer::buildOverlayLines() {
    // Empty initial buffers — both grow on demand inside setOverlayLines.
    // Use a tiny starter capacity so the very first set call doesn't have
    // to special-case "buffer is null."
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = 256;
        bdesc.label = svFromCStr("ifcviewer-wgpu.overlay_line_vbo");
        overlay_line_vertex_buffer_   = wgpuDeviceCreateBuffer(device_, &bdesc);
        overlay_line_vertex_capacity_ = 256;
    }
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        bdesc.size  = kOverlayLineUniformSlotSize;
        bdesc.label = svFromCStr("ifcviewer-wgpu.overlay_line_uniforms");
        overlay_line_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
        overlay_line_uniform_slots_  = 1;
    }
    {
        WGPUBindGroupLayoutEntry entry = {};
        entry.binding    = 0;
        entry.visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
        entry.buffer.type             = WGPUBufferBindingType_Uniform;
        entry.buffer.hasDynamicOffset = 1;
        entry.buffer.minBindingSize   = 128;
        WGPUBindGroupLayoutDescriptor bgl_desc = {};
        bgl_desc.entryCount = 1;
        bgl_desc.entries    = &entry;
        bgl_desc.label      = svFromCStr("ifcviewer-wgpu.overlay_line_bgl");
        overlay_line_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);
    }
    {
        WGPUPipelineLayoutDescriptor pl_desc = {};
        pl_desc.bindGroupLayoutCount = 1;
        pl_desc.bindGroupLayouts     = &overlay_line_bgl_;
        pl_desc.label                = svFromCStr("ifcviewer-wgpu.overlay_line_pipeline_layout");
        overlay_line_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);
    }
    {
        WGPUBindGroupEntry entry = {};
        entry.binding = 0;
        entry.buffer  = overlay_line_uniform_buffer_;
        entry.offset  = 0;
        entry.size    = 128;
        WGPUBindGroupDescriptor bg_desc = {};
        bg_desc.layout     = overlay_line_bgl_;
        bg_desc.entryCount = 1;
        bg_desc.entries    = &entry;
        bg_desc.label      = svFromCStr("ifcviewer-wgpu.overlay_line_bind_group");
        overlay_line_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg_desc);
    }
    {
        WGPUShaderSourceWGSL wgsl_src = {};
        wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
        wgsl_src.code        = svFromCStr(OVERLAY_LINES_WGSL);
        WGPUShaderModuleDescriptor sm_desc = {};
        sm_desc.nextInChain = &wgsl_src.chain;
        sm_desc.label       = svFromCStr("ifcviewer-wgpu.overlay_line_wgsl");
        overlay_line_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);
    }

    // Per-vertex layout: (a.xyz, b.xyz, side, along) = 8 floats = 32 bytes.
    WGPUVertexAttribute attribs[4] = {};
    attribs[0].format = WGPUVertexFormat_Float32x3; attribs[0].offset = 0;  attribs[0].shaderLocation = 0;
    attribs[1].format = WGPUVertexFormat_Float32x3; attribs[1].offset = 12; attribs[1].shaderLocation = 1;
    attribs[2].format = WGPUVertexFormat_Float32;   attribs[2].offset = 24; attribs[2].shaderLocation = 2;
    attribs[3].format = WGPUVertexFormat_Float32;   attribs[3].offset = 28; attribs[3].shaderLocation = 3;
    WGPUVertexBufferLayout vbl = {};
    vbl.arrayStride    = 32;
    vbl.stepMode       = WGPUVertexStepMode_Vertex;
    vbl.attributeCount = 4;
    vbl.attributes     = attribs;

    WGPUBlendState blend = {};
    blend.color.srcFactor = WGPUBlendFactor_SrcAlpha;
    blend.color.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.color.operation = WGPUBlendOperation_Add;
    blend.alpha.srcFactor = WGPUBlendFactor_One;
    blend.alpha.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.alpha.operation = WGPUBlendOperation_Add;

    WGPUColorTargetState ct = {};
    ct.format    = surface_format_;
    ct.blend     = &blend;
    ct.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = overlay_line_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &ct;

    // Depth-tested against the main MSAA depth so lines correctly hide
    // behind geometry; depth-write off so they don't occlude later
    // overlays.
    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_False;
    depth.depthCompare         = WGPUCompareFunction_LessEqual;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = overlay_line_pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.overlay_line_pipeline");
    rp_desc.vertex.module       = overlay_line_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 1;
    rp_desc.vertex.buffers      = &vbl;
    rp_desc.fragment            = &frag;
    rp_desc.depthStencil        = &depth;
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode  = WGPUCullMode_None;
    rp_desc.multisample.count   = uint32_t(sample_count_);
    rp_desc.multisample.mask    = 0xFFFFFFFFu;
    overlay_line_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    return overlay_line_pipeline_ != nullptr;
}

void WgpuOverlayRenderer::setOverlayLines(const std::vector<LineGroup>& groups) {
    overlay_line_draws_.clear();
    if (groups.empty()) return;

    // Per-segment expansion: 6 vertices × 8 floats = 48 floats per segment.
    // Each vertex carries (a.xyz, b.xyz, side, along) where (side, along)
    // selects one of six fixed corners of the screen-space quad.
    static const float CORNERS[6][2] = {
        {-1.0f, 0.0f}, {+1.0f, 0.0f}, {-1.0f, 1.0f},
        {-1.0f, 1.0f}, {+1.0f, 0.0f}, {+1.0f, 1.0f},
    };

    std::vector<float> verts;
    uint32_t first_vertex = 0;
    overlay_line_draws_.reserve(groups.size());
    for (const auto& g : groups) {
        if (g.world_xyz.size() < 6) {
            overlay_line_draws_.push_back({first_vertex, 0});
            continue;
        }
        const size_t n_segs = g.world_xyz.size() / 6;
        const uint32_t group_vcount = uint32_t(n_segs) * 6;
        verts.reserve(verts.size() + size_t(group_vcount) * 8);
        for (size_t s = 0; s < n_segs; ++s) {
            const float* a = &g.world_xyz[s * 6 + 0];
            const float* b = &g.world_xyz[s * 6 + 3];
            for (int c = 0; c < 6; ++c) {
                verts.push_back(a[0]); verts.push_back(a[1]); verts.push_back(a[2]);
                verts.push_back(b[0]); verts.push_back(b[1]); verts.push_back(b[2]);
                verts.push_back(CORNERS[c][0]);
                verts.push_back(CORNERS[c][1]);
            }
        }
        overlay_line_draws_.push_back({first_vertex, group_vcount});
        first_vertex += group_vcount;
    }

    // Grow vertex buffer if needed (1.5× headroom so steady-state setters
    // don't re-allocate every frame).
    const uint64_t bytes = uint64_t(verts.size()) * sizeof(float);
    if (bytes > overlay_line_vertex_capacity_) {
        const uint64_t new_cap = bytes + bytes / 2;
        if (overlay_line_vertex_buffer_) {
            wgpuBufferRelease(overlay_line_vertex_buffer_);
        }
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = new_cap;
        bdesc.label = svFromCStr("ifcviewer-wgpu.overlay_line_vbo");
        overlay_line_vertex_buffer_   = wgpuDeviceCreateBuffer(device_, &bdesc);
        overlay_line_vertex_capacity_ = new_cap;
    }
    if (bytes > 0) {
        wgpuQueueWriteBuffer(queue_, overlay_line_vertex_buffer_, 0,
                             verts.data(), size_t(bytes));
    }

    // Grow uniform buffer to one 256-byte slot per group; re-create the
    // bind group on each grow so the dynamic-offset stride still binds
    // exactly 128 bytes per group (the WGSL struct size).
    if (uint32_t(groups.size()) > overlay_line_uniform_slots_) {
        const uint32_t new_slots = uint32_t(groups.size());
        if (overlay_line_uniform_buffer_) {
            wgpuBufferRelease(overlay_line_uniform_buffer_);
        }
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        bdesc.size  = uint64_t(new_slots) * kOverlayLineUniformSlotSize;
        bdesc.label = svFromCStr("ifcviewer-wgpu.overlay_line_uniforms");
        overlay_line_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
        overlay_line_uniform_slots_  = new_slots;

        if (overlay_line_bind_group_) {
            wgpuBindGroupRelease(overlay_line_bind_group_);
        }
        WGPUBindGroupEntry entry = {};
        entry.binding = 0;
        entry.buffer  = overlay_line_uniform_buffer_;
        entry.offset  = 0;
        entry.size    = 128;
        WGPUBindGroupDescriptor bg_desc = {};
        bg_desc.layout     = overlay_line_bgl_;
        bg_desc.entryCount = 1;
        bg_desc.entries    = &entry;
        bg_desc.label      = svFromCStr("ifcviewer-wgpu.overlay_line_bind_group");
        overlay_line_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg_desc);
    }

    // Pack each group's static slot tail (everything after the per-frame
    // view_proj). Layout matches WGSL LineUniforms (see OVERLAY_LINES_WGSL):
    //   [  0..64) view_proj      (written per-frame)
    //   [ 64..80) inner_color
    //   [ 80..96) stroke_color
    //   [ 96..104) viewport_size (written per-frame)
    //   [104..108) line_width_px
    //   [108..112) stroke_extra
    //   [112..116) dash_period_px
    //   [116..120) dash_on_ratio
    for (size_t i = 0; i < groups.size(); ++i) {
        const auto& g = groups[i];
        const uint64_t slot_off = uint64_t(i) * kOverlayLineUniformSlotSize;
        uint8_t slot_tail[56] = {};  // bytes [64..120)
        std::memcpy(slot_tail + 0,  g.color,        16);  //  64.. 80
        std::memcpy(slot_tail + 16, g.stroke_color, 16);  //  80.. 96
        // viewport_size occupies [96..104) — written per-frame.
        std::memcpy(slot_tail + 40, &g.line_width,     4);  // 104..108
        std::memcpy(slot_tail + 44, &g.stroke_extra,   4);  // 108..112
        std::memcpy(slot_tail + 48, &g.dash_period_px, 4);  // 112..116
        std::memcpy(slot_tail + 52, &g.dash_on_ratio,  4);  // 116..120
        wgpuQueueWriteBuffer(queue_, overlay_line_uniform_buffer_,
                             slot_off + 64, slot_tail, sizeof(slot_tail));
    }
}

void WgpuOverlayRenderer::encodeOverlayLines(WGPURenderPassEncoder pass,
                                             const WgpuOverlayFrame& f) {
    if (!overlay_line_pipeline_ || overlay_line_draws_.empty()) return;
    if (f.viewport_w_px <= 0 || f.viewport_h_px <= 0) return;

    // Per-frame slot prefix: view_proj (64 B) into [0..64), viewport_size
    // (8 B) into [96..104). The static [64..96) and [104..120) ranges were
    // filled by setOverlayLines so we don't touch them again.
    float vp[16];
    std::memcpy(vp, f.view_proj.constData(), sizeof(vp));
    const float viewport[2] = { float(f.viewport_w_px),
                                float(f.viewport_h_px) };

    wgpuRenderPassEncoderSetPipeline(pass, overlay_line_pipeline_);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, overlay_line_vertex_buffer_,
                                         0, WGPU_WHOLE_SIZE);

    for (size_t i = 0; i < overlay_line_draws_.size(); ++i) {
        const auto& d = overlay_line_draws_[i];
        if (d.vertex_count == 0) continue;
        const uint64_t slot_off = uint64_t(i) * kOverlayLineUniformSlotSize;
        wgpuQueueWriteBuffer(queue_, overlay_line_uniform_buffer_,
                             slot_off + 0, vp, sizeof(vp));
        wgpuQueueWriteBuffer(queue_, overlay_line_uniform_buffer_,
                             slot_off + 96, viewport, sizeof(viewport));
        const uint32_t dynamic_offsets[1] = { uint32_t(slot_off) };
        wgpuRenderPassEncoderSetBindGroup(pass, 0, overlay_line_bind_group_,
                                          1, dynamic_offsets);
        wgpuRenderPassEncoderDraw(pass, d.vertex_count, 1, d.first_vertex, 0);
    }
}

// -----------------------------------------------------------------------------
// Overlay points
// -----------------------------------------------------------------------------

bool WgpuOverlayRenderer::buildOverlayPoints() {
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = 256;
        bdesc.label = svFromCStr("ifcviewer-wgpu.overlay_point_vbo");
        overlay_point_vertex_buffer_   = wgpuDeviceCreateBuffer(device_, &bdesc);
        overlay_point_vertex_capacity_ = 256;
    }
    {
        // WGSL PointUniforms struct size: mat4(64) + 2×vec4(32) + vec2(8) +
        // 2×f32(8) = 112 B; struct rounds up to 128 (alignOf == 16).
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        bdesc.size  = 128;
        bdesc.label = svFromCStr("ifcviewer-wgpu.overlay_point_uniforms");
        overlay_point_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
    }
    {
        WGPUBindGroupLayoutEntry entry = {};
        entry.binding    = 0;
        entry.visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
        entry.buffer.type           = WGPUBufferBindingType_Uniform;
        entry.buffer.minBindingSize = 128;
        WGPUBindGroupLayoutDescriptor bgl_desc = {};
        bgl_desc.entryCount = 1;
        bgl_desc.entries    = &entry;
        bgl_desc.label      = svFromCStr("ifcviewer-wgpu.overlay_point_bgl");
        overlay_point_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);
    }
    {
        WGPUPipelineLayoutDescriptor pl_desc = {};
        pl_desc.bindGroupLayoutCount = 1;
        pl_desc.bindGroupLayouts     = &overlay_point_bgl_;
        pl_desc.label                = svFromCStr("ifcviewer-wgpu.overlay_point_pipeline_layout");
        overlay_point_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);
    }
    {
        WGPUBindGroupEntry entry = {};
        entry.binding = 0;
        entry.buffer  = overlay_point_uniform_buffer_;
        entry.offset  = 0;
        entry.size    = 128;
        WGPUBindGroupDescriptor bg_desc = {};
        bg_desc.layout     = overlay_point_bgl_;
        bg_desc.entryCount = 1;
        bg_desc.entries    = &entry;
        bg_desc.label      = svFromCStr("ifcviewer-wgpu.overlay_point_bind_group");
        overlay_point_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg_desc);
    }
    {
        WGPUShaderSourceWGSL wgsl_src = {};
        wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
        wgsl_src.code        = svFromCStr(OVERLAY_POINTS_WGSL);
        WGPUShaderModuleDescriptor sm_desc = {};
        sm_desc.nextInChain = &wgsl_src.chain;
        sm_desc.label       = svFromCStr("ifcviewer-wgpu.overlay_point_wgsl");
        overlay_point_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);
    }

    // Per-vertex layout: (world_pos.xyz, corner.xy) = 5 floats = 20 bytes.
    WGPUVertexAttribute attribs[2] = {};
    attribs[0].format = WGPUVertexFormat_Float32x3; attribs[0].offset = 0;  attribs[0].shaderLocation = 0;
    attribs[1].format = WGPUVertexFormat_Float32x2; attribs[1].offset = 12; attribs[1].shaderLocation = 1;
    WGPUVertexBufferLayout vbl = {};
    vbl.arrayStride    = 20;
    vbl.stepMode       = WGPUVertexStepMode_Vertex;
    vbl.attributeCount = 2;
    vbl.attributes     = attribs;

    WGPUBlendState blend = {};
    blend.color.srcFactor = WGPUBlendFactor_SrcAlpha;
    blend.color.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.color.operation = WGPUBlendOperation_Add;
    blend.alpha.srcFactor = WGPUBlendFactor_One;
    blend.alpha.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.alpha.operation = WGPUBlendOperation_Add;

    WGPUColorTargetState ct = {};
    ct.format    = surface_format_;
    ct.blend     = &blend;
    ct.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = overlay_point_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &ct;

    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_False;
    depth.depthCompare         = WGPUCompareFunction_LessEqual;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = overlay_point_pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.overlay_point_pipeline");
    rp_desc.vertex.module       = overlay_point_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 1;
    rp_desc.vertex.buffers      = &vbl;
    rp_desc.fragment            = &frag;
    rp_desc.depthStencil        = &depth;
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode  = WGPUCullMode_None;
    rp_desc.multisample.count   = uint32_t(sample_count_);
    rp_desc.multisample.mask    = 0xFFFFFFFFu;
    overlay_point_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    return overlay_point_pipeline_ != nullptr;
}

void WgpuOverlayRenderer::setOverlayPoints(const std::vector<float>& world_xyz,
                                           float r, float g, float b, float a,
                                           float pixel_size,
                                           float stroke_r, float stroke_g,
                                           float stroke_b, float stroke_a,
                                           float stroke_extra) {
    overlay_point_vertex_count_ = 0;
    if (world_xyz.size() < 3 || pixel_size <= 0.0f) return;

    const size_t n_pts = world_xyz.size() / 3;
    // Six vertices per point (two triangles), 5 floats each.
    static const float CORNERS[6][2] = {
        {-1.0f, -1.0f}, {+1.0f, -1.0f}, {-1.0f, +1.0f},
        {-1.0f, +1.0f}, {+1.0f, -1.0f}, {+1.0f, +1.0f},
    };
    std::vector<float> verts;
    verts.reserve(n_pts * 6 * 5);
    for (size_t p = 0; p < n_pts; ++p) {
        const float* w = &world_xyz[p * 3];
        for (int c = 0; c < 6; ++c) {
            verts.push_back(w[0]); verts.push_back(w[1]); verts.push_back(w[2]);
            verts.push_back(CORNERS[c][0]);
            verts.push_back(CORNERS[c][1]);
        }
    }
    overlay_point_vertex_count_ = uint32_t(n_pts) * 6;

    const uint64_t bytes = uint64_t(verts.size()) * sizeof(float);
    if (bytes > overlay_point_vertex_capacity_) {
        const uint64_t new_cap = bytes + bytes / 2;
        if (overlay_point_vertex_buffer_) {
            wgpuBufferRelease(overlay_point_vertex_buffer_);
        }
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = new_cap;
        bdesc.label = svFromCStr("ifcviewer-wgpu.overlay_point_vbo");
        overlay_point_vertex_buffer_   = wgpuDeviceCreateBuffer(device_, &bdesc);
        overlay_point_vertex_capacity_ = new_cap;
    }
    wgpuQueueWriteBuffer(queue_, overlay_point_vertex_buffer_, 0,
                         verts.data(), size_t(bytes));

    // Pack the [64..120) tail of the uniform slot (inner/stroke + sprite
    // geometry — view_proj and viewport_size are written per-frame in
    // encodeOverlayPoints). Slot layout matches WGSL PointUniforms:
    //   [  0..64) view_proj         (per-frame)
    //   [ 64..80) inner_color
    //   [ 80..96) stroke_color
    //   [ 96..104) viewport_size    (per-frame)
    //   [104..108) total_half_px
    //   [108..112) inner_radius_norm
    // pixel_size is the inner full diameter; total diameter = pixel_size
    // + 2*stroke_extra; inner_radius_norm = inner_radius / total_half.
    const float total_diam   = pixel_size + 2.0f * stroke_extra;
    const float total_half   = total_diam * 0.5f;
    const float inner_radius = pixel_size * 0.5f;
    const float inner_norm   = (total_half > 1e-6f) ? (inner_radius / total_half)
                                                    : 1.0f;
    uint8_t slot_tail[44] = {};
    const float inner_rgba [4] = { r, g, b, a };
    const float stroke_rgba[4] = { stroke_r, stroke_g, stroke_b, stroke_a };
    std::memcpy(slot_tail + 0,  inner_rgba,  16);
    std::memcpy(slot_tail + 16, stroke_rgba, 16);
    std::memcpy(slot_tail + 40, &total_half, 4);
    // inner_radius_norm sits at slot offset 108 → tail offset 44, but the
    // tail above only spans [64..108). The norm goes in its own write.
    wgpuQueueWriteBuffer(queue_, overlay_point_uniform_buffer_, 64,
                         slot_tail, sizeof(slot_tail));
    wgpuQueueWriteBuffer(queue_, overlay_point_uniform_buffer_, 108,
                         &inner_norm, sizeof(inner_norm));
}

void WgpuOverlayRenderer::encodeOverlayPoints(WGPURenderPassEncoder pass,
                                              const WgpuOverlayFrame& f) {
    if (!overlay_point_pipeline_ || overlay_point_vertex_count_ == 0) return;
    if (f.viewport_w_px <= 0 || f.viewport_h_px <= 0) return;

    float vp[16];
    std::memcpy(vp, f.view_proj.constData(), sizeof(vp));
    const float viewport[2] = { float(f.viewport_w_px),
                                float(f.viewport_h_px) };
    wgpuQueueWriteBuffer(queue_, overlay_point_uniform_buffer_, 0,  vp, sizeof(vp));
    wgpuQueueWriteBuffer(queue_, overlay_point_uniform_buffer_, 96, viewport, sizeof(viewport));

    wgpuRenderPassEncoderSetPipeline(pass, overlay_point_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, overlay_point_bind_group_, 0, nullptr);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, overlay_point_vertex_buffer_,
                                         0, WGPU_WHOLE_SIZE);
    wgpuRenderPassEncoderDraw(pass, overlay_point_vertex_count_, 1, 0, 0);
}

// -----------------------------------------------------------------------------
// Labels + HUD text (textured quads, content-cached)
// -----------------------------------------------------------------------------

bool WgpuOverlayRenderer::buildLabels() {
    {
        WGPUSamplerDescriptor sd = {};
        sd.minFilter    = WGPUFilterMode_Linear;
        sd.magFilter    = WGPUFilterMode_Linear;
        sd.mipmapFilter = WGPUMipmapFilterMode_Nearest;
        sd.addressModeU = WGPUAddressMode_ClampToEdge;
        sd.addressModeV = WGPUAddressMode_ClampToEdge;
        sd.addressModeW = WGPUAddressMode_ClampToEdge;
        sd.lodMinClamp  = 0.0f;
        sd.lodMaxClamp  = 0.0f;
        sd.maxAnisotropy = 1;
        sd.label = svFromCStr("ifcviewer-wgpu.label_sampler");
        label_sampler_ = wgpuDeviceCreateSampler(device_, &sd);
    }
    {
        WGPUBindGroupLayoutEntry entries[2] = {};
        entries[0].binding    = 0;
        entries[0].visibility = WGPUShaderStage_Fragment;
        entries[0].sampler.type = WGPUSamplerBindingType_Filtering;
        entries[1].binding    = 1;
        entries[1].visibility = WGPUShaderStage_Fragment;
        entries[1].texture.sampleType    = WGPUTextureSampleType_Float;
        entries[1].texture.viewDimension = WGPUTextureViewDimension_2D;
        WGPUBindGroupLayoutDescriptor bgl_desc = {};
        bgl_desc.entryCount = 2;
        bgl_desc.entries    = entries;
        bgl_desc.label      = svFromCStr("ifcviewer-wgpu.label_bgl");
        label_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);
    }
    {
        WGPUPipelineLayoutDescriptor pl_desc = {};
        pl_desc.bindGroupLayoutCount = 1;
        pl_desc.bindGroupLayouts     = &label_bgl_;
        pl_desc.label                = svFromCStr("ifcviewer-wgpu.label_pipeline_layout");
        label_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);
    }
    {
        WGPUShaderSourceWGSL wgsl_src = {};
        wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
        wgsl_src.code        = svFromCStr(LABELS_WGSL);
        WGPUShaderModuleDescriptor sm_desc = {};
        sm_desc.nextInChain = &wgsl_src.chain;
        sm_desc.label       = svFromCStr("ifcviewer-wgpu.label_wgsl");
        label_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);
    }
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = 256;
        bdesc.label = svFromCStr("ifcviewer-wgpu.label_vbo");
        label_vertex_buffer_   = wgpuDeviceCreateBuffer(device_, &bdesc);
        label_vertex_capacity_ = 256;
    }

    // Per-vertex: vec2 NDC + vec2 uv = 16 B stride.
    WGPUVertexAttribute attribs[2] = {};
    attribs[0].format = WGPUVertexFormat_Float32x2; attribs[0].offset = 0; attribs[0].shaderLocation = 0;
    attribs[1].format = WGPUVertexFormat_Float32x2; attribs[1].offset = 8; attribs[1].shaderLocation = 1;
    WGPUVertexBufferLayout vbl = {};
    vbl.arrayStride    = 16;
    vbl.stepMode       = WGPUVertexStepMode_Vertex;
    vbl.attributeCount = 2;
    vbl.attributes     = attribs;

    WGPUBlendState blend = {};
    blend.color.srcFactor = WGPUBlendFactor_SrcAlpha;
    blend.color.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.color.operation = WGPUBlendOperation_Add;
    blend.alpha.srcFactor = WGPUBlendFactor_One;
    blend.alpha.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.alpha.operation = WGPUBlendOperation_Add;

    WGPUColorTargetState ct = {};
    ct.format    = surface_format_;
    ct.blend     = &blend;
    ct.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = label_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &ct;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = label_pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.label_pipeline");
    rp_desc.vertex.module       = label_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 1;
    rp_desc.vertex.buffers      = &vbl;
    rp_desc.fragment            = &frag;
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode  = WGPUCullMode_None;
    rp_desc.multisample.count   = 1;
    rp_desc.multisample.mask    = 0xFFFFFFFFu;
    label_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    return label_pipeline_ != nullptr;
}

void WgpuOverlayRenderer::releaseLabelTextures() {
    for (auto it = label_tex_cache_.begin(); it != label_tex_cache_.end(); ++it) {
        if (it.value().bind_group) wgpuBindGroupRelease(it.value().bind_group);
        if (it.value().view)       wgpuTextureViewRelease(it.value().view);
        if (it.value().texture)    wgpuTextureRelease(it.value().texture);
    }
    label_tex_cache_.clear();
}

void WgpuOverlayRenderer::setOverlayLabels(const std::vector<Label>& labels) {
    labels_ = labels;
}

void WgpuOverlayRenderer::setHudText(const QString& text) {
    hud_text_ = text;
}

WgpuOverlayRenderer::LabelTexture*
WgpuOverlayRenderer::getOrCreateLabelTexture(const QString& cache_key,
                                             const QString& text,
                                             int font_pt,
                                             int dpr) {
    auto it = label_tex_cache_.find(cache_key);
    if (it != label_tex_cache_.end()) return &it.value();

    // Rasterise: dark-grey rounded background (matches GL's #141414) +
    // white antialiased text. Pixel-size everything by `dpr` so the
    // texture is sharp on HiDPI surfaces.
    QFont font;
    font.setPointSize(font_pt);
    font.setStyleHint(QFont::SansSerif);
    QFontMetrics fm(font);
    const QStringList lines = text.split('\n');
    int text_w_logical = 0;
    for (const auto& ln : lines) {
        text_w_logical = std::max(text_w_logical, fm.horizontalAdvance(ln));
    }
    const int line_h_logical = fm.height();
    const int text_h_logical = line_h_logical * lines.size();
    const int pad_x_logical  = 6;
    const int pad_y_logical  = 3;
    const int w_logical = text_w_logical + 2 * pad_x_logical;
    const int h_logical = text_h_logical + 2 * pad_y_logical;
    const int w_px = std::max(1, w_logical * dpr);
    const int h_px = std::max(1, h_logical * dpr);

    QImage img(w_px, h_px, QImage::Format_RGBA8888_Premultiplied);
    img.setDevicePixelRatio(dpr);
    img.fill(Qt::transparent);
    {
        QPainter painter(&img);
        painter.setRenderHint(QPainter::Antialiasing, true);
        painter.setRenderHint(QPainter::TextAntialiasing, true);
        // Background: opaque dark-grey, no border.
        painter.setPen(Qt::NoPen);
        painter.setBrush(QColor(20, 20, 20, 235));
        painter.drawRoundedRect(QRect(0, 0, w_logical, h_logical), 3, 3);
        // Text: white.
        painter.setPen(Qt::white);
        painter.setFont(font);
        painter.drawText(QRect(pad_x_logical, pad_y_logical,
                               text_w_logical, text_h_logical),
                         Qt::AlignLeft | Qt::AlignTop, text);
    }

    // Convert QImage's row layout (BGRA in Premultiplied? actually RGBA8888
    // is byte-order RGBA, so safe) into a wgpu-friendly tightly-packed
    // buffer with bytesPerRow padded to a 256-byte multiple (wgpu copy
    // alignment requirement only for B2T, but Queue.writeTexture has the
    // same constraint via bytesPerRow alignment to 256 when used with
    // wgpuQueueWriteTexture? — actually wgpuQueueWriteTexture has NO 256
    // alignment requirement, only buffer-based copies do). So we can pass
    // img.bits() directly with bytesPerRow = w_px * 4.

    LabelTexture entry;
    entry.width_px  = w_px;
    entry.height_px = h_px;

    WGPUTextureDescriptor td = {};
    td.usage         = WGPUTextureUsage_TextureBinding | WGPUTextureUsage_CopyDst;
    td.dimension     = WGPUTextureDimension_2D;
    td.format        = WGPUTextureFormat_RGBA8Unorm;
    td.size.width    = uint32_t(w_px);
    td.size.height   = uint32_t(h_px);
    td.size.depthOrArrayLayers = 1;
    td.mipLevelCount = 1;
    td.sampleCount   = 1;
    td.label         = svFromCStr("ifcviewer-wgpu.label_texture");
    entry.texture = wgpuDeviceCreateTexture(device_, &td);

    WGPUTexelCopyTextureInfo dst = {};
    dst.texture  = entry.texture;
    dst.aspect   = WGPUTextureAspect_All;
    WGPUTexelCopyBufferLayout layout = {};
    layout.bytesPerRow  = uint32_t(w_px) * 4;
    layout.rowsPerImage = uint32_t(h_px);
    WGPUExtent3D extent = { uint32_t(w_px), uint32_t(h_px), 1 };
    wgpuQueueWriteTexture(queue_, &dst, img.constBits(),
                          size_t(w_px) * size_t(h_px) * 4,
                          &layout, &extent);

    WGPUTextureViewDescriptor tvd = {};
    tvd.format      = WGPUTextureFormat_RGBA8Unorm;
    tvd.dimension   = WGPUTextureViewDimension_2D;
    tvd.baseMipLevel = 0;
    tvd.mipLevelCount = 1;
    tvd.baseArrayLayer = 0;
    tvd.arrayLayerCount = 1;
    tvd.aspect = WGPUTextureAspect_All;
    tvd.label  = svFromCStr("ifcviewer-wgpu.label_view");
    entry.view = wgpuTextureCreateView(entry.texture, &tvd);

    WGPUBindGroupEntry bge[2] = {};
    bge[0].binding = 0;
    bge[0].sampler = label_sampler_;
    bge[1].binding = 1;
    bge[1].textureView = entry.view;
    WGPUBindGroupDescriptor bgd = {};
    bgd.layout     = label_bgl_;
    bgd.entryCount = 2;
    bgd.entries    = bge;
    bgd.label      = svFromCStr("ifcviewer-wgpu.label_bind_group");
    entry.bind_group = wgpuDeviceCreateBindGroup(device_, &bgd);

    auto inserted = label_tex_cache_.insert(cache_key, entry);
    return &inserted.value();
}

void WgpuOverlayRenderer::encodeLabels(WGPUCommandEncoder enc,
                                       WGPUTextureView surface_view,
                                       const WgpuOverlayFrame& f) {
    if (!label_pipeline_ || !surface_view) return;
    if (labels_.empty() && hud_text_.isEmpty()) return;
    if (f.viewport_w_px <= 0 || f.viewport_h_px <= 0) return;

    const int   dpr   = std::max(1, f.device_pixel_ratio);
    const float w_phys = float(f.viewport_w_px);
    const float h_phys = float(f.viewport_h_px);

    // Resolve each label/HUD to (texture, NDC quad), expanding into the
    // per-frame vertex buffer.
    struct DrawRec { LabelTexture* tex; uint32_t first_vertex; };
    std::vector<DrawRec> draws;
    std::vector<float>   verts;
    draws.reserve(labels_.size() + 1);
    verts.reserve((labels_.size() + 1) * 6 * 4);

    auto push_quad = [&](LabelTexture* tex, float nx0, float ny0,
                                            float nx1, float ny1) {
        // Two triangles, top-left at (nx0, ny0) (NDC Y up).
        // UV layout: (0,0) at top-left of image → flip Y because NDC Y
        // increases upward but image V increases downward.
        const float u0 = 0.0f, u1 = 1.0f, v0 = 0.0f, v1 = 1.0f;
        draws.push_back({tex, uint32_t(verts.size() / 4)});
        const float quad[24] = {
            nx0, ny0, u0, v0,   nx1, ny0, u1, v0,   nx0, ny1, u0, v1,
            nx0, ny1, u0, v1,   nx1, ny0, u1, v0,   nx1, ny1, u1, v1,
        };
        verts.insert(verts.end(), quad, quad + 24);
    };

    // World-anchored labels at point size 9 (matches GL OverlayRenderer).
    for (const auto& lbl : labels_) {
        const float* p = lbl.world_pos;
        const float* m = f.view_proj.constData();
        // Column-major: M[col*4 + row].
        const float wx = m[0]*p[0] + m[4]*p[1] + m[8]*p[2]  + m[12];
        const float wy = m[1]*p[0] + m[5]*p[1] + m[9]*p[2]  + m[13];
        const float ww = m[3]*p[0] + m[7]*p[1] + m[11]*p[2] + m[15];
        if (ww <= 0.0f) continue;
        const float ndc_x = wx / ww;
        const float ndc_y = wy / ww;
        if (ndc_x < -1.0f || ndc_x > 1.0f
         || ndc_y < -1.0f || ndc_y > 1.0f) continue;
        const float sx_phys = (ndc_x * 0.5f + 0.5f) * w_phys;
        const float sy_phys = (1.0f - (ndc_y * 0.5f + 0.5f)) * h_phys;
        const QString key = QStringLiteral("L9:") + lbl.text;
        LabelTexture* tex = getOrCreateLabelTexture(key, lbl.text, 9, dpr);
        if (!tex) continue;
        const float wq = float(tex->width_px);
        const float hq = float(tex->height_px);
        const float lx_phys = sx_phys - wq * 0.5f;
        const float ly_phys = sy_phys - hq * 0.5f;
        const float nx0 = (lx_phys / w_phys) * 2.0f - 1.0f;
        const float nx1 = ((lx_phys + wq) / w_phys) * 2.0f - 1.0f;
        const float ny0 = 1.0f - 2.0f * ly_phys / h_phys;          // top
        const float ny1 = 1.0f - 2.0f * (ly_phys + hq) / h_phys;   // bottom
        push_quad(tex, nx0, ny0, nx1, ny1);
    }

    // HUD: top-left, point size 11 (matches GL OverlayRenderer).
    if (!hud_text_.isEmpty()) {
        const QString key = QStringLiteral("H11:") + hud_text_;
        LabelTexture* tex = getOrCreateLabelTexture(key, hud_text_, 11, dpr);
        if (tex) {
            const float margin_phys = 12.0f * float(dpr);
            const float lx_phys = margin_phys;
            const float ly_phys = margin_phys;
            const float wq = float(tex->width_px);
            const float hq = float(tex->height_px);
            const float nx0 = (lx_phys / w_phys) * 2.0f - 1.0f;
            const float nx1 = ((lx_phys + wq) / w_phys) * 2.0f - 1.0f;
            const float ny0 = 1.0f - 2.0f * ly_phys / h_phys;
            const float ny1 = 1.0f - 2.0f * (ly_phys + hq) / h_phys;
            push_quad(tex, nx0, ny0, nx1, ny1);
        }
    }

    if (draws.empty()) return;

    // Grow + upload the per-frame vertex buffer.
    const uint64_t bytes = uint64_t(verts.size()) * sizeof(float);
    if (bytes > label_vertex_capacity_) {
        const uint64_t new_cap = bytes + bytes / 2;
        if (label_vertex_buffer_) wgpuBufferRelease(label_vertex_buffer_);
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = new_cap;
        bdesc.label = svFromCStr("ifcviewer-wgpu.label_vbo");
        label_vertex_buffer_   = wgpuDeviceCreateBuffer(device_, &bdesc);
        label_vertex_capacity_ = new_cap;
    }
    wgpuQueueWriteBuffer(queue_, label_vertex_buffer_, 0,
                         verts.data(), size_t(bytes));

    WGPURenderPassColorAttachment color = {};
    color.view       = surface_view;
    color.loadOp     = WGPULoadOp_Load;
    color.storeOp    = WGPUStoreOp_Store;
    color.clearValue = { 0, 0, 0, 1 };
    color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount = 1;
    pass_desc.colorAttachments     = &color;
    pass_desc.label                = svFromCStr("ifcviewer-wgpu.label_pass");
    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);

    wgpuRenderPassEncoderSetPipeline(pass, label_pipeline_);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, label_vertex_buffer_,
                                         0, WGPU_WHOLE_SIZE);
    for (const auto& d : draws) {
        wgpuRenderPassEncoderSetBindGroup(pass, 0, d.tex->bind_group, 0, nullptr);
        wgpuRenderPassEncoderDraw(pass, 6, 1, d.first_vertex, 0);
    }
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);
}
