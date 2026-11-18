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


// This file was generated with the assistance of an AI coding tool.

#include "SectionCapRenderer.h"

#include <algorithm>
#include <cstdint>
#include <cstring>

namespace {

constexpr int kMaxPlanes = 6;  // matches kMaxSectionPlanes

WGPUStringView svFromCStr(const char* s) {
    WGPUStringView v;
    v.data   = s;
    v.length = s ? std::strlen(s) : 0;
    return v;
}

// Mirrors `CapUniforms` in the shader below.
struct CapUniforms {
    float view_proj[16];
    float inv_view_proj[16];
    float clip_planes[kMaxPlanes][4];
    float hatch_color[4];
    float fill_color[4];
    float spacing_px;      // physical pixels
    float line_width_px;   // physical pixels
    std::uint32_t hatch;
    std::uint32_t clip_count;
};

const char* SECTION_CAP_WGSL = R"WGSL(
struct CapUniforms {
    view_proj:     mat4x4<f32>,
    inv_view_proj: mat4x4<f32>,
    clip_planes:   array<vec4<f32>, 6>,
    hatch_color:   vec4<f32>,
    fill_color:    vec4<f32>,
    spacing_px:    f32,
    line_width_px: f32,
    hatch:         u32,
    clip_count:    u32,
};

@group(0) @binding(0) var accum: texture_2d<f32>;
@group(0) @binding(1) var<uniform> u: CapUniforms;

@vertex
fn vs_main(@builtin(vertex_index) vid: u32) -> @builtin(position) vec4<f32> {
    // One triangle covering the viewport.
    let p = vec2<f32>(f32((vid << 1u) & 2u), f32(vid & 2u));
    return vec4<f32>(p * 2.0 - 1.0, 0.0, 1.0);
}

fn srgbToLinear(s: vec3<f32>) -> vec3<f32> {
    let lo = s / 12.92;
    let hi = pow((s + 0.055) / 1.055, vec3<f32>(2.4));
    return select(hi, lo, s <= vec3<f32>(0.04045));
}

// Coverage of a family of parallel lines `spacing_px` apart, `along` being the
// pixel's coordinate across them.
fn hatchLines(along: f32) -> f32 {
    let m    = along - floor(along / u.spacing_px) * u.spacing_px;
    let dist = min(m, u.spacing_px - m);
    let half = u.line_width_px * 0.5;
    return 1.0 - smoothstep(half - 0.5, half + 0.5, dist);
}

struct FsOut {
    @location(0) color: vec4<f32>,
    @builtin(frag_depth) depth: f32,
};

@fragment
fn fs_main(@builtin(position) pos: vec4<f32>) -> FsOut {
    let acc = textureLoad(accum, vec2<i32>(pos.xy), 0);
    // The winding of a mirrored instance is reversed, which only flips the
    // sign of everything it accumulates.
    if (abs(acc.a) < 0.5) { discard; }

    // The pixel's view ray, from the near plane (t = 0) to the far (t = 1).
    let size = vec2<f32>(textureDimensions(accum));
    let ndc  = vec2<f32>(pos.x / size.x * 2.0 - 1.0, 1.0 - pos.y / size.y * 2.0);
    let o4   = u.inv_view_proj * vec4<f32>(ndc, 0.0, 1.0);
    let f4   = u.inv_view_proj * vec4<f32>(ndc, 1.0, 1.0);
    let o    = o4.xyz / o4.w;
    let dir  = f4.xyz / f4.w - o;

    // Where the ray enters the kept region, the intersection of the planes'
    // negative half-spaces. No cap unless it enters through a plane: a ray
    // that starts inside is looking at the model from within the cut.
    // SectionCapRenderer::rayEntry is the CPU copy of this.
    var t_enter = 0.0;
    var t_exit  = 1.0;
    for (var i = 0u; i < u.clip_count; i = i + 1u) {
        let p  = u.clip_planes[i];
        let f0 = dot(p.xyz, o) + p.w;
        let fd = dot(p.xyz, dir);
        if (fd < 0.0) {
            t_enter = max(t_enter, -f0 / fd);
        } else if (fd > 0.0) {
            t_exit = min(t_exit, -f0 / fd);
        } else if (f0 > 0.0) {
            discard;
        }
    }
    if (t_enter <= 0.0 || t_enter >= t_exit) { discard; }

    var color = acc.rgb / acc.a;
    color = mix(color, u.fill_color.rgb, u.fill_color.a);

    // 0.7071 turns x + y into a distance across 45-degree lines.
    var lines = 0.0;
    if (u.hatch >= 1u) { lines = hatchLines((pos.x + pos.y) * 0.70710678); }
    if (u.hatch >= 2u) { lines = max(lines, hatchLines((pos.x - pos.y) * 0.70710678)); }
    color = mix(color, u.hatch_color.rgb, u.hatch_color.a * lines);

    // A hair behind the plane, so the section gizmo lying in it still passes
    // its depth test.
    let clip = u.view_proj * vec4<f32>(o + dir * (t_enter * 1.001), 1.0);

    var out: FsOut;
    out.color = vec4<f32>(srgbToLinear(color), 1.0);
    out.depth = clamp(clip.z / clip.w, 0.0, 1.0);
    return out;
}
)WGSL";

} // namespace

SectionCapRenderer::~SectionCapRenderer() { destroy(); }

bool SectionCapRenderer::init(WGPUDevice device, WGPUQueue queue,
                              WGPUTextureFormat color_format, int sample_count) {
    device_ = device;
    queue_  = queue;
    if (!device_ || !queue_) return false;

    WGPUBufferDescriptor ub = {};
    ub.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    ub.size  = sizeof(CapUniforms);
    ub.label = svFromCStr("ifcviewer-wgpu.section_cap_uniforms");
    uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &ub);

    WGPUBindGroupLayoutEntry entries[2] = {};
    entries[0].binding               = 0;
    entries[0].visibility            = WGPUShaderStage_Fragment;
    entries[0].texture.sampleType    = WGPUTextureSampleType_UnfilterableFloat;
    entries[0].texture.viewDimension = WGPUTextureViewDimension_2D;
    entries[1].binding               = 1;
    entries[1].visibility            = WGPUShaderStage_Fragment;
    entries[1].buffer.type           = WGPUBufferBindingType_Uniform;
    entries[1].buffer.minBindingSize = sizeof(CapUniforms);
    WGPUBindGroupLayoutDescriptor bgl_desc = {};
    bgl_desc.entryCount = 2;
    bgl_desc.entries    = entries;
    bgl_desc.label      = svFromCStr("ifcviewer-wgpu.section_cap_bgl");
    bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);

    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 1;
    pl_desc.bindGroupLayouts     = &bgl_;
    layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    WGPUShaderSourceWGSL wgsl = {};
    wgsl.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl.code        = svFromCStr(SECTION_CAP_WGSL);
    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl.chain;
    sm_desc.label       = svFromCStr("ifcviewer-wgpu.section_cap_wgsl");
    shader_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    WGPUColorTargetState ct = {};
    ct.format    = color_format;
    ct.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = shader_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &ct;

    // Always passes: a cap is in front of everything the clip left standing.
    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_True;
    depth.depthCompare         = WGPUCompareFunction_Always;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp = {};
    rp.layout             = layout_;
    rp.label              = svFromCStr("ifcviewer-wgpu.section_cap_pipeline");
    rp.vertex.module      = shader_;
    rp.vertex.entryPoint  = svFromCStr("vs_main");
    rp.vertex.bufferCount = 0;
    rp.fragment           = &frag;
    rp.depthStencil       = &depth;
    rp.primitive.topology = WGPUPrimitiveTopology_TriangleList;
    rp.primitive.cullMode = WGPUCullMode_None;
    rp.multisample.count  = uint32_t(sample_count);
    rp.multisample.mask   = 0xFFFFFFFFu;
    pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp);
    return pipeline_ != nullptr;
}

void SectionCapRenderer::ensureTarget(int w, int h) {
    if (w == accum_w_ && h == accum_h_ && accum_view_) return;
    releaseTarget();
    if (!device_) return;

    WGPUTextureDescriptor desc = {};
    desc.dimension     = WGPUTextureDimension_2D;
    desc.size.width    = std::uint32_t(w);
    desc.size.height   = std::uint32_t(h);
    desc.size.depthOrArrayLayers = 1;
    desc.mipLevelCount = 1;
    desc.sampleCount   = 1;
    desc.format        = kAccumFormat;
    desc.usage         = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_TextureBinding;
    desc.label         = svFromCStr("ifcviewer-wgpu.section_cap_accum");
    accum_texture_ = wgpuDeviceCreateTexture(device_, &desc);
    accum_view_    = wgpuTextureCreateView(accum_texture_, nullptr);
    accum_w_ = w;
    accum_h_ = h;
}

void SectionCapRenderer::releaseTarget() {
    // The bind group names the view.
    if (bind_group_)    { wgpuBindGroupRelease(bind_group_);     bind_group_ = nullptr; }
    if (accum_view_)    { wgpuTextureViewRelease(accum_view_);   accum_view_ = nullptr; }
    if (accum_texture_) { wgpuTextureRelease(accum_texture_);    accum_texture_ = nullptr; }
    accum_w_ = accum_h_ = 0;
}

void SectionCapRenderer::encodeComposite(WGPURenderPassEncoder pass,
                                         const Eigen::Matrix4f& view_proj,
                                         const std::vector<SectionPlane>& planes,
                                         float device_pixel_ratio,
                                         const SectionCapStyle& style) {
    if (!ready() || planes.empty()) return;

    CapUniforms u = {};
    const Eigen::Matrix4f inv = view_proj.inverse();
    std::memcpy(u.view_proj, view_proj.data(), sizeof(u.view_proj));
    std::memcpy(u.inv_view_proj, inv.data(), sizeof(u.inv_view_proj));
    u.clip_count = std::uint32_t(std::min<int>(int(planes.size()), kMaxPlanes));
    for (std::uint32_t i = 0; i < u.clip_count; ++i) {
        const SectionPlane& p = planes[i];
        u.clip_planes[i][0] = p.n.x();
        u.clip_planes[i][1] = p.n.y();
        u.clip_planes[i][2] = p.n.z();
        u.clip_planes[i][3] = p.d;
    }
    std::memcpy(u.hatch_color, style.hatch_color, sizeof(u.hatch_color));
    std::memcpy(u.fill_color, style.fill_color, sizeof(u.fill_color));
    // A spacing under a pixel would divide by nearly nothing in the shader.
    u.spacing_px    = std::max(1.0f, style.spacing_px * device_pixel_ratio);
    u.line_width_px = style.line_width_px * device_pixel_ratio;
    u.hatch         = std::uint32_t(style.hatch);
    wgpuQueueWriteBuffer(queue_, uniform_buffer_, 0, &u, sizeof(u));

    if (!bind_group_) {
        WGPUBindGroupEntry e[2] = {};
        e[0].binding     = 0;
        e[0].textureView = accum_view_;
        e[1].binding     = 1;
        e[1].buffer      = uniform_buffer_;
        e[1].size        = sizeof(CapUniforms);
        WGPUBindGroupDescriptor bg = {};
        bg.layout     = bgl_;
        bg.entryCount = 2;
        bg.entries    = e;
        bg.label      = svFromCStr("ifcviewer-wgpu.section_cap_bind_group");
        bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg);
    }

    wgpuRenderPassEncoderSetPipeline(pass, pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, bind_group_, 0, nullptr);
    wgpuRenderPassEncoderDraw(pass, 3, 1, 0, 0);
}

bool SectionCapRenderer::rayEntry(const Eigen::Matrix4f& view_proj,
                                  const std::vector<SectionPlane>& planes,
                                  float ndc_x, float ndc_y,
                                  Eigen::Vector3f& point_out, Eigen::Vector3f& normal_out) {
    const Eigen::Matrix4f inv = view_proj.inverse();
    const Eigen::Vector4f o4 = inv * Eigen::Vector4f(ndc_x, ndc_y, 0.0f, 1.0f);
    const Eigen::Vector4f f4 = inv * Eigen::Vector4f(ndc_x, ndc_y, 1.0f, 1.0f);
    const Eigen::Vector3f o   = o4.head<3>() / o4.w();
    const Eigen::Vector3f dir = f4.head<3>() / f4.w() - o;

    float t_enter = 0.0f;
    float t_exit  = 1.0f;
    int   entered = -1;
    const int n = std::min<int>(int(planes.size()), kMaxPlanes);
    for (int i = 0; i < n; ++i) {
        const float f0 = planes[i].n.dot(o) + planes[i].d;
        const float fd = planes[i].n.dot(dir);
        if (fd < 0.0f) {
            const float t = -f0 / fd;
            if (t > t_enter) { t_enter = t; entered = i; }
        } else if (fd > 0.0f) {
            t_exit = std::min(t_exit, -f0 / fd);
        } else if (f0 > 0.0f) {
            return false;
        }
    }
    if (entered < 0 || t_enter >= t_exit) return false;
    point_out  = o + dir * t_enter;
    normal_out = planes[entered].n;
    return true;
}

void SectionCapRenderer::destroy() {
    releaseTarget();
    if (pipeline_)       { wgpuRenderPipelineRelease(pipeline_);     pipeline_ = nullptr; }
    if (layout_)         { wgpuPipelineLayoutRelease(layout_);       layout_ = nullptr; }
    if (bgl_)            { wgpuBindGroupLayoutRelease(bgl_);         bgl_ = nullptr; }
    if (uniform_buffer_) { wgpuBufferRelease(uniform_buffer_);       uniform_buffer_ = nullptr; }
    if (shader_)         { wgpuShaderModuleRelease(shader_);         shader_ = nullptr; }
}
