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

#include "SectionGizmoRenderer.h"

#include <algorithm>
#include <array>
#include <cstring>
#include <string>

namespace {

constexpr int      kMaxPlanes            = 6;    // matches kMaxSectionPlanes
constexpr uint32_t kSectionUniformSlot   = 256;  // dynamic-offset slot stride

WGPUStringView svFromCStr(const char* s) {
    WGPUStringView v;
    v.data   = s;
    v.length = s ? std::strlen(s) : 0;
    return v;
}

// Thick-line rendering helper (shared shape with OverlayRenderer's other
// overlays) + the section-gizmo vertex/fragment shaders. Each line segment is
// expanded to a screen-space-thick, anti-aliased quad.
static const std::string SECTION_GIZMO_WGSL = std::string(R"WGSL(
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
)WGSL");

// Pack the 256-byte dynamic-offset slot. Layout matches SectionUniforms above:
// mat4 + 4×(vec3 + scalar) + vec4 + vec2 + pad = 160 B used, padded to 256.
void packSectionUniform(uint8_t* dst,
                        const Eigen::Matrix4f& mvp,
                        const Eigen::Vector3f& origin, float half_size,
                        const Eigen::Vector3f& tangent, float line_width_px,
                        const Eigen::Vector3f& bitangent,
                        const Eigen::Vector3f& normal,
                        float r, float g, float b, float a,
                        float viewport_w, float viewport_h) {
    std::memset(dst, 0, 256);
    std::memcpy(dst, mvp.data(), 16 * sizeof(float));
    auto put_vec3_pad = [&](size_t off, const Eigen::Vector3f& v, float pad_val) {
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

// Stable in-plane basis: pick the world axis least parallel to n so the
// cross-product stays well-conditioned at any orientation.
void planeBasis(const Eigen::Vector3f& n_in,
                Eigen::Vector3f& nn, Eigen::Vector3f& tangent, Eigen::Vector3f& bitangent) {
    nn = n_in.normalized();
    const float ax = std::abs(nn.x()), ay = std::abs(nn.y()), az = std::abs(nn.z());
    Eigen::Vector3f seed = (ax < ay && ax < az) ? Eigen::Vector3f(1, 0, 0)
                         : (ay < az)             ? Eigen::Vector3f(0, 1, 0)
                                                 : Eigen::Vector3f(0, 0, 1);
    tangent = nn.cross(seed);
    if (tangent.squaredNorm() < 1e-12f) tangent = Eigen::Vector3f(1, 0, 0);
    tangent.normalize();
    bitangent = nn.cross(tangent).normalized();
}

bool projectWorldToLogicalScreen(const Eigen::Matrix4f& vp, const Eigen::Vector3f& world,
                                 int win_w, int win_h, Eigen::Vector2f& out) {
    const Eigen::Vector4f clip = vp * Eigen::Vector4f(world.x(), world.y(), world.z(), 1.0f);
    if (clip.w() <= 0.0f) return false;
    const float invw = 1.0f / clip.w();
    out = Eigen::Vector2f((clip.x() * invw * 0.5f + 0.5f) * float(win_w),
                          (1.0f - (clip.y() * invw * 0.5f + 0.5f)) * float(win_h));
    return true;
}

}  // namespace

SectionGizmoRenderer::~SectionGizmoRenderer() { destroy(); }

bool SectionGizmoRenderer::init(WGPUDevice device, WGPUQueue queue,
                                WGPUTextureFormat color_format, int sample_count) {
    device_ = device;
    queue_  = queue;
    if (!device_ || !queue_) return false;

    // ---- Gizmo geometry: 9 line segments (quad outline + normal arrow) ----
    struct Seg { std::array<float, 3> s, e, c; };
    static constexpr std::array<float, 3> kRed = { 1.000f, 0.200f, 0.322f };
    static const Seg segs[] = {
        { {-1, -1, 0}, { 1, -1, 0}, kRed },   // quad outline
        { { 1, -1, 0}, { 1,  1, 0}, kRed },
        { { 1,  1, 0}, {-1,  1, 0}, kRed },
        { {-1,  1, 0}, {-1, -1, 0}, kRed },
        { { 0,  0, 0}, { 0,  0, 1}, kRed },   // arrow shaft along +n
        { { 0,  0, 1}, {-0.18f, 0,      0.78f}, kRed },  // arrow head
        { { 0,  0, 1}, { 0.18f, 0,      0.78f}, kRed },
        { { 0,  0, 1}, { 0,    -0.18f,  0.78f}, kRed },
        { { 0,  0, 1}, { 0,     0.18f,  0.78f}, kRed },
    };
    std::vector<float> verts;
    verts.reserve(std::size(segs) * 6 * 11);
    auto push_v = [&](const Seg& s, float t, float side) {
        verts.insert(verts.end(), { s.s[0], s.s[1], s.s[2], s.e[0], s.e[1], s.e[2],
                                    s.c[0], s.c[1], s.c[2], t, side });
    };
    for (const auto& s : segs) {
        push_v(s, 0.f, -1.f); push_v(s, 0.f, +1.f); push_v(s, 1.f, -1.f);
        push_v(s, 1.f, -1.f); push_v(s, 0.f, +1.f); push_v(s, 1.f, +1.f);
    }
    vertex_count_ = int(std::size(segs)) * 6;

    WGPUBufferDescriptor vb = {};
    vb.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
    vb.size  = verts.size() * sizeof(float);
    vb.label = svFromCStr("ifcviewer-wgpu.section_gizmo_vbo");
    vertex_buffer_ = wgpuDeviceCreateBuffer(device_, &vb);
    wgpuQueueWriteBuffer(queue_, vertex_buffer_, 0, verts.data(), verts.size() * sizeof(float));

    WGPUBufferDescriptor ub = {};
    ub.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    ub.size  = uint64_t(kMaxPlanes) * kSectionUniformSlot;
    ub.label = svFromCStr("ifcviewer-wgpu.section_gizmo_uniforms");
    uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &ub);

    WGPUBindGroupLayoutEntry ble = {};
    ble.binding                 = 0;
    ble.visibility              = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
    ble.buffer.type             = WGPUBufferBindingType_Uniform;
    ble.buffer.hasDynamicOffset = 1;
    ble.buffer.minBindingSize   = 160;
    WGPUBindGroupLayoutDescriptor bgl_desc = {};
    bgl_desc.entryCount = 1;
    bgl_desc.entries    = &ble;
    bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);

    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 1;
    pl_desc.bindGroupLayouts     = &bgl_;
    layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    WGPUBindGroupEntry bge = {};
    bge.binding = 0;
    bge.buffer  = uniform_buffer_;
    bge.offset  = 0;
    bge.size    = kSectionUniformSlot;
    WGPUBindGroupDescriptor bg_desc = {};
    bg_desc.layout     = bgl_;
    bg_desc.entryCount = 1;
    bg_desc.entries    = &bge;
    bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg_desc);

    WGPUShaderSourceWGSL wgsl = {};
    wgsl.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl.code        = svFromCStr(SECTION_GIZMO_WGSL.c_str());
    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl.chain;
    shader_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    // Vertex layout: start_local vec3, end_local vec3, col vec3, t f32, side f32.
    WGPUVertexAttribute attribs[5] = {};
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

    WGPUBlendState blend = {};
    blend.color.srcFactor = WGPUBlendFactor_SrcAlpha;
    blend.color.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.color.operation = WGPUBlendOperation_Add;
    blend.alpha.srcFactor = WGPUBlendFactor_One;
    blend.alpha.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    blend.alpha.operation = WGPUBlendOperation_Add;
    WGPUColorTargetState ct = {};
    ct.format    = color_format;
    ct.blend     = &blend;
    ct.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = shader_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &ct;

    // Depth-test against geometry (LessEqual) but don't write depth.
    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_False;
    depth.depthCompare         = WGPUCompareFunction_LessEqual;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp = {};
    rp.layout              = layout_;
    rp.label               = svFromCStr("ifcviewer-wgpu.section_gizmo_pipeline");
    rp.vertex.module       = shader_;
    rp.vertex.entryPoint   = svFromCStr("vs_main");
    rp.vertex.bufferCount  = 1;
    rp.vertex.buffers      = &vbl;
    rp.fragment            = &frag;
    rp.depthStencil        = &depth;
    rp.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp.primitive.cullMode  = WGPUCullMode_None;
    rp.multisample.count    = uint32_t(sample_count);
    rp.multisample.mask     = 0xFFFFFFFFu;
    pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp);
    return pipeline_ != nullptr;
}

void SectionGizmoRenderer::encode(WGPURenderPassEncoder pass, const Eigen::Matrix4f& view_proj,
                                  const std::vector<SectionPlane>& planes,
                                  int viewport_w_px, int viewport_h_px, int device_pixel_ratio) {
    if (!pipeline_ || planes.empty()) return;
    wgpuRenderPassEncoderSetPipeline(pass, pipeline_);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, vertex_buffer_, 0, WGPU_WHOLE_SIZE);

    const float dpr    = float(std::max(1, device_pixel_ratio));
    const float line_w = 5.0f * dpr;
    const float vw     = float(viewport_w_px);
    const float vh     = float(viewport_h_px);
    const int   n      = std::min<int>(int(planes.size()), kMaxPlanes);
    for (int i = 0; i < n; ++i) {
        const SectionPlane& p = planes[i];
        Eigen::Vector3f nn, tangent, bitangent;
        planeBasis(p.n, nn, tangent, bitangent);
        // Fixed 1 m gizmo (matches the desktop OverlayRenderer / GL constant).
        // NOT visual_radius: the normal is flipped toward the camera, so a large
        // arrow would shoot past the eye (clip.w<0) and vanish.
        const float half = 1.0f;

        uint8_t slot[256];
        packSectionUniform(slot, view_proj, p.origin, half, tangent, line_w,
                           bitangent, nn, 1.0f, 1.0f, 1.0f, 1.0f, vw, vh);
        const uint32_t slot_offset = uint32_t(i) * kSectionUniformSlot;
        wgpuQueueWriteBuffer(queue_, uniform_buffer_, slot_offset, slot, sizeof(slot));
        wgpuRenderPassEncoderSetBindGroup(pass, 0, bind_group_, 1, &slot_offset);
        wgpuRenderPassEncoderDraw(pass, uint32_t(vertex_count_), 1, 0, 0);
    }
}

int SectionGizmoRenderer::hitTest(int x, int y, const std::vector<SectionPlane>& planes,
                                  const Eigen::Matrix4f& view, const Eigen::Matrix4f& proj,
                                  int viewport_w_px, int viewport_h_px, float tolerance_px) {
    const Eigen::Matrix4f vp = proj * view;
    const Eigen::Vector2f q{ float(x), float(y) };
    int   best_i = -1;
    float best_d = tolerance_px;
    const int n = std::min<int>(int(planes.size()), kMaxPlanes);
    for (int i = 0; i < n; ++i) {
        const SectionPlane& p = planes[i];
        // The arrow runs origin → origin + n * 1 m (visual radius scales the
        // gizmo, but hit-test the unit arrow to mirror the desktop).
        Eigen::Vector2f s_origin, s_tip;
        if (!projectWorldToLogicalScreen(vp, p.origin, viewport_w_px, viewport_h_px, s_origin)) continue;
        if (!projectWorldToLogicalScreen(vp, p.origin + p.n * 1.0f, viewport_w_px, viewport_h_px, s_tip)) continue;
        const Eigen::Vector2f ab = s_tip - s_origin;
        const float ab_len2 = ab.squaredNorm();
        if (ab_len2 < 1e-3f) continue;
        float t = (q - s_origin).dot(ab) / ab_len2;
        t = std::clamp(t, 0.0f, 1.0f);
        const Eigen::Vector2f proj_pt = s_origin + ab * t;
        const float d = (q - proj_pt).norm();
        if (d < best_d) { best_d = d; best_i = i; }
    }
    return best_i;
}

void SectionGizmoRenderer::destroy() {
    if (pipeline_)       { wgpuRenderPipelineRelease(pipeline_);       pipeline_ = nullptr; }
    if (layout_)         { wgpuPipelineLayoutRelease(layout_);         layout_ = nullptr; }
    if (bgl_)            { wgpuBindGroupLayoutRelease(bgl_);           bgl_ = nullptr; }
    if (bind_group_)     { wgpuBindGroupRelease(bind_group_);          bind_group_ = nullptr; }
    if (vertex_buffer_)  { wgpuBufferRelease(vertex_buffer_);          vertex_buffer_ = nullptr; }
    if (uniform_buffer_) { wgpuBufferRelease(uniform_buffer_);         uniform_buffer_ = nullptr; }
    if (shader_)         { wgpuShaderModuleRelease(shader_);           shader_ = nullptr; }
}
