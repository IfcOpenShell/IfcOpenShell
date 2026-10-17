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

#include "AxisIndicatorRenderer.h"
#include "WgpuDynamicOffsets.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <string>
#include <vector>

#include "CameraMath.h"

namespace {

constexpr uint32_t kAxisUniformSlot = 256;  // dynamic-offset slot stride
constexpr uint32_t kAxisVertexCount = 18;   // 3 arms x 2 triangles x 3 verts

// Uniform slots in the shared buffer.
constexpr uint32_t kSlotCorner     = 0;
constexpr uint32_t kSlotPivot      = 1;
constexpr uint32_t kSlotPivotXray  = 2;
constexpr uint32_t kSlotOrigin     = 3;
constexpr uint32_t kSlotOriginXray = 4;
constexpr uint32_t kSlotSurvey     = 5;
constexpr uint32_t kSlotSurveyXray = 6;
constexpr uint32_t kSlotCount      = 7;

WGPUStringView svFromCStr(const char* s) {
    WGPUStringView v;
    v.data   = s;
    v.length = s ? std::strlen(s) : 0;
    return v;
}

// Thick-line rendering helper (shared shape with the other overlays) + the
// axis vertex shader. Each arm is expanded to a screen-space-thick,
// anti-aliased quad.
static const std::string AXIS_WGSL = std::string(R"WGSL(
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
)WGSL");

// Pack the axis uniform's 256-byte slot. Layout matches WGSL AxisUniforms:
// mat4 + vec3 + f32 + f32 + f32 + vec2 = 96 B used, padded to 256.
void packAxisUniform(uint8_t* dst,
                     const Eigen::Matrix4f& mvp, const Eigen::Vector3f& origin,
                     float arm, float alpha, float line_width_px,
                     float viewport_w, float viewport_h) {
    std::memset(dst, 0, kAxisUniformSlot);
    std::memcpy(dst, mvp.data(), 16 * sizeof(float));
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

}  // namespace

AxisIndicatorRenderer::~AxisIndicatorRenderer() { destroy(); }

bool AxisIndicatorRenderer::init(WGPUDevice device, WGPUQueue queue,
                                 WGPUTextureFormat color_format, int sample_count) {
    device_ = device;
    queue_  = queue;
    if (!device_ || !queue_) return false;

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

    WGPUBufferDescriptor vb = {};
    vb.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
    vb.size  = sizeof(axis_verts);
    vb.label = svFromCStr("ifcviewer-wgpu.axis_vbo");
    vertex_buffer_ = wgpuDeviceCreateBuffer(device_, &vb);
    wgpuQueueWriteBuffer(queue_, vertex_buffer_, 0, axis_verts, sizeof(axis_verts));

    WGPUBufferDescriptor ub = {};
    ub.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    ub.size  = kSlotCount * kAxisUniformSlot;
    ub.label = svFromCStr("ifcviewer-wgpu.axis_uniforms");
    uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &ub);

    WGPUBindGroupLayoutEntry ble = {};
    ble.binding                 = 0;
    ble.visibility              = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
    ble.buffer.type             = WGPUBufferBindingType_Uniform;
    ble.buffer.hasDynamicOffset = 1;
    ble.buffer.minBindingSize   = 192;
    WGPUBindGroupLayoutDescriptor bgl_desc = {};
    bgl_desc.entryCount = 1;
    bgl_desc.entries    = &ble;
    bgl_desc.label      = svFromCStr("ifcviewer-wgpu.axis_bgl");
    bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);

    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 1;
    pl_desc.bindGroupLayouts     = &bgl_;
    pl_desc.label                = svFromCStr("ifcviewer-wgpu.axis_pipeline_layout");
    layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    WGPUBindGroupEntry bge = {};
    bge.binding = 0;
    bge.buffer  = uniform_buffer_;
    bge.offset  = 0;
    bge.size    = kAxisUniformSlot;
    WGPUBindGroupDescriptor bg_desc = {};
    bg_desc.layout     = bgl_;
    bg_desc.entryCount = 1;
    bg_desc.entries    = &bge;
    bg_desc.label      = svFromCStr("ifcviewer-wgpu.axis_bind_group");
    bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg_desc);

    WGPUShaderSourceWGSL wgsl = {};
    wgsl.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl.code        = svFromCStr(AXIS_WGSL.c_str());
    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl.chain;
    sm_desc.label       = svFromCStr("ifcviewer-wgpu.axis_wgsl");
    shader_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    // Vertex layout: start vec3, end vec3, col vec3, t f32, side f32.
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

    // Pivot: inside the main MSAA pass, depth-tested against the scene but
    // never writing depth. Two passes — LessEqual for the visible part,
    // GreaterEqual for the dim x-ray showing through geometry.
    auto build_pivot = [&](WGPUCompareFunction cmp, const char* label,
                           WGPURenderPipeline& out) {
        WGPUColorTargetState ct = {};
        ct.format    = color_format;
        ct.blend     = &blend;
        ct.writeMask = WGPUColorWriteMask_All;

        WGPUFragmentState frag = {};
        frag.module      = shader_;
        frag.entryPoint  = svFromCStr("fs_main");
        frag.targetCount = 1;
        frag.targets     = &ct;

        WGPUDepthStencilState depth = {};
        depth.format               = WGPUTextureFormat_Depth32Float;
        depth.depthWriteEnabled    = WGPUOptionalBool_False;
        depth.depthCompare         = cmp;
        depth.stencilFront.compare = WGPUCompareFunction_Always;
        depth.stencilBack.compare  = WGPUCompareFunction_Always;

        WGPURenderPipelineDescriptor rp = {};
        rp.layout              = layout_;
        rp.label               = svFromCStr(label);
        rp.vertex.module       = shader_;
        rp.vertex.entryPoint   = svFromCStr("vs_main");
        rp.vertex.bufferCount  = 1;
        rp.vertex.buffers      = &vbl;
        rp.fragment            = &frag;
        rp.depthStencil        = &depth;
        rp.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
        rp.primitive.cullMode  = WGPUCullMode_None;
        rp.multisample.count   = uint32_t(sample_count);
        rp.multisample.mask    = 0xFFFFFFFFu;
        out = wgpuDeviceCreateRenderPipeline(device_, &rp);
    };
    build_pivot(WGPUCompareFunction_LessEqual,
                "ifcviewer-wgpu.axis_pivot_pipeline", pivot_pipeline_);
    build_pivot(WGPUCompareFunction_GreaterEqual,
                "ifcviewer-wgpu.axis_pivot_xray_pipeline", pivot_xray_pipeline_);

    // Corner: resolved surface, no depth, sampleCount=1.
    {
        WGPUColorTargetState ct = {};
        ct.format    = color_format;
        ct.blend     = &blend;
        ct.writeMask = WGPUColorWriteMask_All;

        WGPUFragmentState frag = {};
        frag.module      = shader_;
        frag.entryPoint  = svFromCStr("fs_main");
        frag.targetCount = 1;
        frag.targets     = &ct;

        WGPURenderPipelineDescriptor rp = {};
        rp.layout              = layout_;
        rp.label               = svFromCStr("ifcviewer-wgpu.axis_corner_pipeline");
        rp.vertex.module       = shader_;
        rp.vertex.entryPoint   = svFromCStr("vs_main");
        rp.vertex.bufferCount  = 1;
        rp.vertex.buffers      = &vbl;
        rp.fragment            = &frag;
        rp.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
        rp.primitive.cullMode  = WGPUCullMode_None;
        rp.multisample.count   = 1;
        rp.multisample.mask    = 0xFFFFFFFFu;
        corner_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp);
    }

    // Blender floor axes: X and Y only, one colour along each line. Z is not
    // part of the floor. Unit segments, scaled by the uniform arm (metres).
    static const float origin_line_verts[] = {
        //  pos (unit)          rgba   — Blender theme axis X / Y
        -1.f, 0.f, 0.f,        0.902f, 0.271f, 0.322f, 1.f,
         1.f, 0.f, 0.f,        0.902f, 0.271f, 0.322f, 1.f,
         0.f,-1.f, 0.f,        0.545f, 0.863f, 0.000f, 1.f,
         0.f, 1.f, 0.f,        0.545f, 0.863f, 0.000f, 1.f,
    };
    WGPUBufferDescriptor olb = {};
    olb.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
    olb.size  = sizeof(origin_line_verts);
    olb.label = svFromCStr("ifcviewer-wgpu.origin_axis_vbo");
    origin_line_buffer_ = wgpuDeviceCreateBuffer(device_, &olb);
    wgpuQueueWriteBuffer(queue_, origin_line_buffer_, 0,
                         origin_line_verts, sizeof(origin_line_verts));

    static const std::string ORIGIN_LINE_WGSL = std::string(R"AXIS(
struct AxisUniforms {
    mvp:           mat4x4<f32>,
    origin:        vec3<f32>,
    arm:           f32,
    alpha:         f32,
    line_width_px: f32,
    viewport_size: vec2<f32>,
    camera_pos:    vec4<f32>,
    view_forward:  vec4<f32>,
    fog_color:     vec4<f32>,
    fog_params:    vec4<f32>,
    axis_x:        vec4<f32>,
    axis_y:        vec4<f32>,
};
@group(0) @binding(0) var<uniform> u: AxisUniforms;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) color: vec4<f32>,
    @location(1) world_pos: vec3<f32>,
};

@vertex
fn vs_line(@location(0) pos: vec3<f32>,
           @location(1) color: vec4<f32>) -> VsOut {
    var out: VsOut;
    let world = u.origin + (pos.x * u.axis_x.xyz + pos.y * u.axis_y.xyz) * u.arm;
    out.clip_pos = u.mvp * vec4<f32>(world, 1.0);
    out.color = vec4<f32>(color.rgb, color.a * u.alpha);
    out.world_pos = world;
    return out;
}

fn srgbToLinear(s: vec3<f32>) -> vec3<f32> {
    let lo = s / 12.92;
    let hi = pow((s + 0.055) / 1.055, vec3<f32>(2.4));
    return select(hi, lo, s <= vec3<f32>(0.04045));
}

fn viewport_fog_factor(world_pos: vec3<f32>, camera_pos: vec3<f32>,
                       view_forward: vec3<f32>, fog_params: vec4<f32>) -> f32 {
    let fog_mode = fog_params.w;
    if (fog_mode <= 0.5) { return 0.0; }
    let fog_depth = max(dot(world_pos - camera_pos, view_forward), 0.0);
    if (fog_mode < 1.5) {
        return smoothstep(fog_params.x, fog_params.y, fog_depth);
    }
    let d = fog_params.z * fog_depth;
    return 1.0 - exp(-d * d);
}

@fragment
fn fs_line(in: VsOut) -> @location(0) vec4<f32> {
    var rgb = in.color.xyz;
    if (u.fog_params.w > 0.5) {
        let fog_factor = viewport_fog_factor(
            in.world_pos, u.camera_pos.xyz, u.view_forward.xyz, u.fog_params);
        if (fog_factor > 0.0) {
            rgb = mix(rgb, u.fog_color.xyz, fog_factor);
        }
    }
    return vec4<f32>(srgbToLinear(rgb), in.color.a);
}
)AXIS");

    WGPUShaderSourceWGSL line_wgsl = {};
    line_wgsl.chain.sType = WGPUSType_ShaderSourceWGSL;
    line_wgsl.code        = svFromCStr(ORIGIN_LINE_WGSL.c_str());
    WGPUShaderModuleDescriptor line_sm = {};
    line_sm.nextInChain = &line_wgsl.chain;
    line_sm.label       = svFromCStr("ifcviewer-wgpu.origin_axis_wgsl");
    origin_line_shader_ = wgpuDeviceCreateShaderModule(device_, &line_sm);

    WGPUVertexAttribute line_attribs[2] = {};
    line_attribs[0].format = WGPUVertexFormat_Float32x3;
    line_attribs[0].offset = 0;
    line_attribs[0].shaderLocation = 0;
    line_attribs[1].format = WGPUVertexFormat_Float32x4;
    line_attribs[1].offset = 12;
    line_attribs[1].shaderLocation = 1;
    WGPUVertexBufferLayout line_vbl = {};
    line_vbl.arrayStride    = 28;
    line_vbl.stepMode       = WGPUVertexStepMode_Vertex;
    line_vbl.attributeCount = 2;
    line_vbl.attributes     = line_attribs;

    auto build_origin_line = [&](WGPUCompareFunction cmp, const char* label,
                                 WGPURenderPipeline& out) {
        WGPUColorTargetState ct = {};
        ct.format    = color_format;
        ct.blend     = &blend;
        ct.writeMask = WGPUColorWriteMask_All;

        WGPUFragmentState frag = {};
        frag.module      = origin_line_shader_;
        frag.entryPoint  = svFromCStr("fs_line");
        frag.targetCount = 1;
        frag.targets     = &ct;

        WGPUDepthStencilState depth = {};
        depth.format               = WGPUTextureFormat_Depth32Float;
        depth.depthWriteEnabled    = WGPUOptionalBool_False;
        depth.depthCompare         = cmp;
        depth.stencilFront.compare = WGPUCompareFunction_Always;
        depth.stencilBack.compare  = WGPUCompareFunction_Always;

        WGPURenderPipelineDescriptor rp = {};
        rp.layout              = layout_;
        rp.label               = svFromCStr(label);
        rp.vertex.module       = origin_line_shader_;
        rp.vertex.entryPoint   = svFromCStr("vs_line");
        rp.vertex.bufferCount  = 1;
        rp.vertex.buffers      = &line_vbl;
        rp.fragment            = &frag;
        rp.depthStencil        = &depth;
        rp.primitive.topology  = WGPUPrimitiveTopology_LineList;
        rp.primitive.cullMode  = WGPUCullMode_None;
        rp.multisample.count   = uint32_t(sample_count);
        rp.multisample.mask    = 0xFFFFFFFFu;
        out = wgpuDeviceCreateRenderPipeline(device_, &rp);
    };
    build_origin_line(WGPUCompareFunction_LessEqual,
                      "ifcviewer-wgpu.origin_axis_pipeline", origin_line_pipeline_);
    build_origin_line(WGPUCompareFunction_GreaterEqual,
                      "ifcviewer-wgpu.origin_axis_xray_pipeline", origin_line_xray_pipeline_);

    // Survey marker: a screen-facing triangle with a centre cross, the usual
    // survey-point symbol, so it cannot be mistaken for the orbit pivot's
    // RGB triad. Built once in CSS px around the point; each stroke is a
    // quad, drawn first as a dark halo and then in amber so it reads on
    // light and dark surfaces alike.
    {
        struct Seg { float ax, ay, bx, by; };
        constexpr float R = 11.0f;   // triangle circumradius, px
        constexpr float C = 4.0f;    // half-length of the centre cross, px
        const float s3 = std::sqrt(3.0f) * 0.5f;
        const Seg segs[] = {
            { 0.0f,    R,        -R * s3, -R * 0.5f },
            { -R * s3, -R * 0.5f, R * s3, -R * 0.5f },
            { R * s3,  -R * 0.5f, 0.0f,    R        },
            { -C, 0.0f, C, 0.0f },
            { 0.0f, -C, 0.0f, C },
        };
        std::vector<float> verts;
        auto push_layer = [&](float width, float r, float g, float b) {
            for (const Seg& s : segs) {
                float dx = s.bx - s.ax, dy = s.by - s.ay;
                const float len = std::sqrt(dx * dx + dy * dy);
                dx /= len; dy /= len;
                const float h = width * 0.5f;
                const float ax = s.ax - dx * h, ay = s.ay - dy * h;
                const float bx = s.bx + dx * h, by = s.by + dy * h;
                const float nx = -dy * h, ny = dx * h;
                const float quad[6][3] = {
                    { ax - nx, ay - ny, -1.f }, { ax + nx, ay + ny, +1.f },
                    { bx - nx, by - ny, -1.f }, { bx - nx, by - ny, -1.f },
                    { ax + nx, ay + ny, +1.f }, { bx + nx, by + ny, +1.f },
                };
                for (const auto& q : quad) {
                    verts.insert(verts.end(), { q[0], q[1], r, g, b, q[2] });
                }
            }
        };
        push_layer(4.5f, 0.06f, 0.07f, 0.09f);
        push_layer(2.0f, 1.00f, 0.72f, 0.16f);
        survey_vertex_count_ = uint32_t(verts.size() / 6);

        WGPUBufferDescriptor sb = {};
        sb.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        sb.size  = verts.size() * sizeof(float);
        sb.label = svFromCStr("ifcviewer-wgpu.survey_marker_vbo");
        survey_buffer_ = wgpuDeviceCreateBuffer(device_, &sb);
        wgpuQueueWriteBuffer(queue_, survey_buffer_, 0, verts.data(), sb.size);
    }

    static const std::string SURVEY_WGSL = std::string(R"WGSL(
struct AxisUniforms {
    mvp:           mat4x4<f32>,
    origin:        vec3<f32>,
    arm:           f32,
    alpha:         f32,
    line_width_px: f32,
    viewport_size: vec2<f32>,
};
@group(0) @binding(0) var<uniform> u: AxisUniforms;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) color:  vec4<f32>,
    @location(1) side_t: f32,
};

// `offset` is CSS px around the point, y up; `u.arm` is the device pixel
// ratio. The marker keeps the point's depth so the x-ray split still works.
@vertex
fn vs_survey(@location(0) offset: vec2<f32>,
             @location(1) col:    vec3<f32>,
             @location(2) side:   f32) -> VsOut {
    let c = u.mvp * vec4<f32>(u.origin, 1.0);
    let off_ndc = offset * u.arm * 2.0 / u.viewport_size;
    var out: VsOut;
    out.clip_pos = vec4<f32>(c.xy + off_ndc * c.w, c.zw);
    out.color  = vec4<f32>(col, u.alpha);
    out.side_t = side;
    return out;
}

@fragment
fn fs_survey(in: VsOut) -> @location(0) vec4<f32> {
    let d  = abs(in.side_t);
    let aa = fwidth(in.side_t);
    let coverage = 1.0 - smoothstep(1.0 - aa, 1.0, d);
    return vec4<f32>(in.color.xyz, in.color.w * coverage);
}
)WGSL");

    WGPUShaderSourceWGSL survey_wgsl = {};
    survey_wgsl.chain.sType = WGPUSType_ShaderSourceWGSL;
    survey_wgsl.code        = svFromCStr(SURVEY_WGSL.c_str());
    WGPUShaderModuleDescriptor survey_sm = {};
    survey_sm.nextInChain = &survey_wgsl.chain;
    survey_sm.label       = svFromCStr("ifcviewer-wgpu.survey_marker_wgsl");
    survey_shader_ = wgpuDeviceCreateShaderModule(device_, &survey_sm);

    WGPUVertexAttribute survey_attribs[3] = {};
    survey_attribs[0].format = WGPUVertexFormat_Float32x2; survey_attribs[0].offset = 0;  survey_attribs[0].shaderLocation = 0;
    survey_attribs[1].format = WGPUVertexFormat_Float32x3; survey_attribs[1].offset = 8;  survey_attribs[1].shaderLocation = 1;
    survey_attribs[2].format = WGPUVertexFormat_Float32;   survey_attribs[2].offset = 20; survey_attribs[2].shaderLocation = 2;
    WGPUVertexBufferLayout survey_vbl = {};
    survey_vbl.arrayStride    = 24;
    survey_vbl.stepMode       = WGPUVertexStepMode_Vertex;
    survey_vbl.attributeCount = 3;
    survey_vbl.attributes     = survey_attribs;

    auto build_survey = [&](WGPUCompareFunction cmp, const char* label,
                            WGPURenderPipeline& out) {
        WGPUColorTargetState ct = {};
        ct.format    = color_format;
        ct.blend     = &blend;
        ct.writeMask = WGPUColorWriteMask_All;

        WGPUFragmentState frag = {};
        frag.module      = survey_shader_;
        frag.entryPoint  = svFromCStr("fs_survey");
        frag.targetCount = 1;
        frag.targets     = &ct;

        WGPUDepthStencilState depth = {};
        depth.format               = WGPUTextureFormat_Depth32Float;
        depth.depthWriteEnabled    = WGPUOptionalBool_False;
        depth.depthCompare         = cmp;
        depth.stencilFront.compare = WGPUCompareFunction_Always;
        depth.stencilBack.compare  = WGPUCompareFunction_Always;

        WGPURenderPipelineDescriptor rp = {};
        rp.layout              = layout_;
        rp.label               = svFromCStr(label);
        rp.vertex.module       = survey_shader_;
        rp.vertex.entryPoint   = svFromCStr("vs_survey");
        rp.vertex.bufferCount  = 1;
        rp.vertex.buffers      = &survey_vbl;
        rp.fragment            = &frag;
        rp.depthStencil        = &depth;
        rp.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
        rp.primitive.cullMode  = WGPUCullMode_None;
        rp.multisample.count   = uint32_t(sample_count);
        rp.multisample.mask    = 0xFFFFFFFFu;
        out = wgpuDeviceCreateRenderPipeline(device_, &rp);
    };
    build_survey(WGPUCompareFunction_LessEqual,
                 "ifcviewer-wgpu.survey_marker_pipeline", survey_pipeline_);
    build_survey(WGPUCompareFunction_GreaterEqual,
                 "ifcviewer-wgpu.survey_marker_xray_pipeline", survey_xray_pipeline_);

    return pivot_pipeline_ && pivot_xray_pipeline_ && corner_pipeline_
        && origin_line_pipeline_ && origin_line_xray_pipeline_
        && survey_pipeline_ && survey_xray_pipeline_;
}

void AxisIndicatorRenderer::encodeWorldTriad(WGPURenderPassEncoder pass,
                                             const OverlayFrame& f,
                                             const Eigen::Vector3f& origin,
                                             float scale_distance,
                                             bool visible,
                                             float arm_css_px,
                                             uint32_t slot_visible_index,
                                             uint32_t slot_xray_index) {
    if (!visible || !pivot_pipeline_ || !pivot_xray_pipeline_) return;
    if (f.viewport_h_px <= 0) return;
    if (!(scale_distance > 0.0f) || !(arm_css_px > 0.0f)) return;

    // Arm length = `arm_css_px` logical px projected into world at
    // `scale_distance`. Line thickness scales with the arm.
    const float fovy_rad        = f.camera_fov_y_deg * kPiF / 180.0f;
    const float world_per_pixel = scale_distance * std::tan(fovy_rad * 0.5f)
                                  * 2.0f / float(f.viewport_h_px);
    const float dpr        = float(f.device_pixel_ratio);
    const float arm_pixels = arm_css_px * dpr;
    const float arm_world  = arm_pixels * world_per_pixel;
    const float line_w     = (arm_css_px / 30.0f) * 2.5f * dpr;
    const float vw     = float(f.viewport_w_px);
    const float vh     = float(f.viewport_h_px);

    uint8_t slot_visible[kAxisUniformSlot];
    uint8_t slot_xray[kAxisUniformSlot];
    packAxisUniform(slot_visible, f.view_proj, origin, arm_world,
                    1.00f, line_w, vw, vh);
    packAxisUniform(slot_xray,    f.view_proj, origin, arm_world,
                    0.30f, line_w, vw, vh);
    const uint32_t visible_off = slot_visible_index * kAxisUniformSlot;
    const uint32_t xray_off    = slot_xray_index    * kAxisUniformSlot;
    wgpuQueueWriteBuffer(queue_, uniform_buffer_, visible_off,
                         slot_visible, sizeof(slot_visible));
    wgpuQueueWriteBuffer(queue_, uniform_buffer_, xray_off,
                         slot_xray, sizeof(slot_xray));

    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, vertex_buffer_, 0, WGPU_WHOLE_SIZE);
    wgpuRenderPassEncoderSetPipeline(pass, pivot_xray_pipeline_);
    ifcviewer::setBindGroupDynamic(pass, 0, bind_group_, 1, &xray_off);
    wgpuRenderPassEncoderDraw(pass, kAxisVertexCount, 1, 0, 0);
    wgpuRenderPassEncoderSetPipeline(pass, pivot_pipeline_);
    ifcviewer::setBindGroupDynamic(pass, 0, bind_group_, 1, &visible_off);
    wgpuRenderPassEncoderDraw(pass, kAxisVertexCount, 1, 0, 0);
}

void AxisIndicatorRenderer::encodePivot(WGPURenderPassEncoder pass,
                                        const OverlayFrame& f, bool visible) {
    encodeWorldTriad(pass, f, f.camera_target, f.camera_distance, visible,
                     30.0f, kSlotPivot, kSlotPivotXray);
}

void AxisIndicatorRenderer::encodeSurveyPoint(WGPURenderPassEncoder pass,
                                              const OverlayFrame& f,
                                              const Eigen::Vector3f& origin,
                                              bool visible) {
    if (!visible || !survey_pipeline_ || !survey_xray_pipeline_ || !survey_buffer_) return;
    if (f.viewport_w_px <= 0 || f.viewport_h_px <= 0) return;

    // The guessed false origin is the centre of a mesh, so it is usually
    // inside geometry: the x-ray pass stays strong enough to find and click.
    const float dpr = float(std::max(1, f.device_pixel_ratio));
    const float vw  = float(f.viewport_w_px);
    const float vh  = float(f.viewport_h_px);
    uint8_t slot_visible[kAxisUniformSlot];
    uint8_t slot_xray[kAxisUniformSlot];
    packAxisUniform(slot_visible, f.view_proj, origin, dpr, 1.00f, 0.0f, vw, vh);
    packAxisUniform(slot_xray,    f.view_proj, origin, dpr, 0.85f, 0.0f, vw, vh);
    const uint32_t visible_off = kSlotSurvey     * kAxisUniformSlot;
    const uint32_t xray_off    = kSlotSurveyXray * kAxisUniformSlot;
    wgpuQueueWriteBuffer(queue_, uniform_buffer_, visible_off, slot_visible, sizeof(slot_visible));
    wgpuQueueWriteBuffer(queue_, uniform_buffer_, xray_off,    slot_xray,    sizeof(slot_xray));

    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, survey_buffer_, 0, WGPU_WHOLE_SIZE);
    wgpuRenderPassEncoderSetPipeline(pass, survey_xray_pipeline_);
    ifcviewer::setBindGroupDynamic(pass, 0, bind_group_, 1, &xray_off);
    wgpuRenderPassEncoderDraw(pass, survey_vertex_count_, 1, 0, 0);
    wgpuRenderPassEncoderSetPipeline(pass, survey_pipeline_);
    ifcviewer::setBindGroupDynamic(pass, 0, bind_group_, 1, &visible_off);
    wgpuRenderPassEncoderDraw(pass, survey_vertex_count_, 1, 0, 0);
}

void AxisIndicatorRenderer::encodeOrigin(WGPURenderPassEncoder pass,
                                         const OverlayFrame& f,
                                         const Eigen::Vector3f& origin,
                                         const Eigen::Vector3f& x_dir,
                                         const Eigen::Vector3f& y_dir,
                                         float size_metres,
                                         const ViewportFog& fog,
                                         const Eigen::Vector3f& eye,
                                         const Eigen::Vector3f& forward,
                                         bool visible) {
    if (!visible || !origin_line_pipeline_) return;
    if (!(size_metres > 0.0f)) return;

    // `arm` is metres either side. Fog tail matches the grid uniform so the
    // floor axes dissolve into the background with the grid lines.
    uint8_t slot_visible[kAxisUniformSlot];
    packAxisUniform(slot_visible, f.view_proj, origin, size_metres,
                    1.00f, 1.0f, float(f.viewport_w_px), float(f.viewport_h_px));
    float camera_pos[4], view_forward[4], fog_color[4], fog_params[4];
    fog.writeUniformTail(camera_pos, view_forward, fog_color, fog_params, eye, forward);
    std::memcpy(slot_visible + 96, camera_pos, 16);
    std::memcpy(slot_visible + 112, view_forward, 16);
    std::memcpy(slot_visible + 128, fog_color, 16);
    std::memcpy(slot_visible + 144, fog_params, 16);
    const float axis_x[4] = { x_dir.x(), x_dir.y(), x_dir.z(), 0.0f };
    const float axis_y[4] = { y_dir.x(), y_dir.y(), y_dir.z(), 0.0f };
    std::memcpy(slot_visible + 160, axis_x, 16);
    std::memcpy(slot_visible + 176, axis_y, 16);
    const uint32_t visible_off = kSlotOrigin * kAxisUniformSlot;
    wgpuQueueWriteBuffer(queue_, uniform_buffer_, visible_off,
                         slot_visible, sizeof(slot_visible));

    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, origin_line_buffer_, 0, WGPU_WHOLE_SIZE);
    wgpuRenderPassEncoderSetPipeline(pass, origin_line_pipeline_);
    ifcviewer::setBindGroupDynamic(pass, 0, bind_group_, 1, &visible_off);
    wgpuRenderPassEncoderDraw(pass, 4, 1, 0, 0);
}

void AxisIndicatorRenderer::encodeCornerAxis(WGPUCommandEncoder enc,
                                             WGPUTextureView surface_view,
                                             const OverlayFrame& f) {
    if (!corner_pipeline_ || !surface_view) return;
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
    const float yaw_rad   = f.camera_yaw_deg   * kPiF / 180.0f;
    const float pitch_rad = f.camera_pitch_deg * kPiF / 180.0f;
    const Eigen::Vector3f eye_dir(std::cos(pitch_rad) * std::cos(yaw_rad),
                                  std::cos(pitch_rad) * std::sin(yaw_rad),
                                  std::sin(pitch_rad));
    const Eigen::Vector3f world_up = (std::abs(f.camera_pitch_deg) >= 89.0f)
                                   ? Eigen::Vector3f(0.0f, 1.0f, 0.0f)
                                   : Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    const Eigen::Matrix4f gv = lookAtRH(eye_dir * 3.0f, Eigen::Vector3f::Zero(), world_up);
    const Eigen::Matrix4f gp = orthoGL(-1.4f, 1.4f, -1.4f, 1.4f, 0.1f, 10.0f);
    Eigen::Matrix4f z_remap = Eigen::Matrix4f::Identity();
    z_remap(2, 2) = 0.5f;
    z_remap(2, 3) = 0.5f;
    const Eigen::Matrix4f mvp = z_remap * gp * gv;

    uint8_t slot[kAxisUniformSlot];
    const float line_w = 2.5f * float(dpr);
    packAxisUniform(slot, mvp, Eigen::Vector3f(0, 0, 0), 1.0f, 1.0f, line_w,
                    float(gizmo_size), float(gizmo_size));
    const uint32_t slot_offset = kSlotCorner * kAxisUniformSlot;
    wgpuQueueWriteBuffer(queue_, uniform_buffer_, slot_offset, slot, sizeof(slot));

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
    wgpuRenderPassEncoderSetPipeline(pass, corner_pipeline_);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, vertex_buffer_, 0, WGPU_WHOLE_SIZE);
    ifcviewer::setBindGroupDynamic(pass, 0, bind_group_, 1, &slot_offset);
    wgpuRenderPassEncoderDraw(pass, kAxisVertexCount, 1, 0, 0);
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);
}

void AxisIndicatorRenderer::destroy() {
    if (pivot_pipeline_)      { wgpuRenderPipelineRelease(pivot_pipeline_);      pivot_pipeline_ = nullptr; }
    if (pivot_xray_pipeline_) { wgpuRenderPipelineRelease(pivot_xray_pipeline_); pivot_xray_pipeline_ = nullptr; }
    if (corner_pipeline_)     { wgpuRenderPipelineRelease(corner_pipeline_);     corner_pipeline_ = nullptr; }
    if (origin_line_pipeline_)      { wgpuRenderPipelineRelease(origin_line_pipeline_);      origin_line_pipeline_ = nullptr; }
    if (origin_line_xray_pipeline_) { wgpuRenderPipelineRelease(origin_line_xray_pipeline_); origin_line_xray_pipeline_ = nullptr; }
    if (origin_line_buffer_)  { wgpuBufferRelease(origin_line_buffer_);          origin_line_buffer_ = nullptr; }
    if (origin_line_shader_)  { wgpuShaderModuleRelease(origin_line_shader_);    origin_line_shader_ = nullptr; }
    if (survey_pipeline_)      { wgpuRenderPipelineRelease(survey_pipeline_);      survey_pipeline_ = nullptr; }
    if (survey_xray_pipeline_) { wgpuRenderPipelineRelease(survey_xray_pipeline_); survey_xray_pipeline_ = nullptr; }
    if (survey_buffer_)        { wgpuBufferRelease(survey_buffer_);                survey_buffer_ = nullptr; }
    if (survey_shader_)        { wgpuShaderModuleRelease(survey_shader_);          survey_shader_ = nullptr; }
    if (layout_)              { wgpuPipelineLayoutRelease(layout_);              layout_ = nullptr; }
    if (bgl_)                 { wgpuBindGroupLayoutRelease(bgl_);                bgl_ = nullptr; }
    if (bind_group_)          { wgpuBindGroupRelease(bind_group_);               bind_group_ = nullptr; }
    if (vertex_buffer_)       { wgpuBufferRelease(vertex_buffer_);               vertex_buffer_ = nullptr; }
    if (uniform_buffer_)      { wgpuBufferRelease(uniform_buffer_);              uniform_buffer_ = nullptr; }
    if (shader_)              { wgpuShaderModuleRelease(shader_);                shader_ = nullptr; }
}
