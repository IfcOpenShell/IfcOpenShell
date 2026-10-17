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

#include "GridHelperRenderer.h"
#include "ViewportFogWgsl.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <string>
#include <vector>

namespace {

static WGPUStringView svFromCStr(const char* s) {
    WGPUStringView v{};
    v.data   = s;
    v.length = std::strlen(s);
    return v;
}

// Native 1 px line-list grid — avoids thick-line quads that overlap on dense spacing.
static const char* GRID_LINE_WGSL = R"(
struct GridUniforms {
    mvp: mat4x4<f32>,
)"
VIEWPORT_FOG_WGSL_UNIFORM_FIELDS
R"(};

@group(0) @binding(0) var<uniform> u: GridUniforms;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) color: vec4<f32>,
    @location(1) world_pos: vec3<f32>,
};

@vertex
fn vs_main(@location(0) pos: vec3<f32>, @location(1) color: vec4<f32>) -> VsOut {
    var out: VsOut;
    out.clip_pos = u.mvp * vec4(pos, 1.0);
    out.color = color;
    out.world_pos = pos;
    return out;
}

)"
VIEWPORT_FOG_WGSL_SRGB_TO_LINEAR
VIEWPORT_FOG_WGSL_LINEAR_TO_SRGB
VIEWPORT_FOG_WGSL_APPLY_FN
R"(
@fragment
fn fs_main(in: VsOut) -> @location(0) vec4<f32> {
    var rgb = in.color.xyz;
    let alpha = in.color.a;
    if (u.fog_params.w > 0.5) {
        rgb = viewport_apply_distance_fog(
            rgb,
            in.world_pos,
            u.camera_pos.xyz,
            u.view_forward.xyz,
            u.fog_color.xyz,
            u.fog_params);
    }
    return vec4<f32>(srgbToLinear(rgb), alpha);
}
)";

constexpr int kFloatsPerVertex = 7;  // xyz + rgba

// `a` and `b` are world coordinates. They go through `world_to_viewer` in
// double, so a grid far out at survey coordinates is still exact near the
// false origin, where it is drawn.
void pushLine(std::vector<float>& verts,
              const Eigen::Matrix4d& world_to_viewer,
              const Eigen::Vector3d& a,
              const Eigen::Vector3d& b,
              const Eigen::Vector3f& color,
              float opacity) {
    const float alpha = std::clamp(opacity, 0.0f, 1.0f);
    auto push_v = [&](const Eigen::Vector3d& w) {
        const Eigen::Vector3d p = (world_to_viewer * w.homogeneous()).head<3>();
        verts.push_back(float(p.x()));
        verts.push_back(float(p.y()));
        verts.push_back(float(p.z()));
        verts.push_back(color.x());
        verts.push_back(color.y());
        verts.push_back(color.z());
        verts.push_back(alpha);
    };
    push_v(a);
    push_v(b);
}

void appendGridLines(std::vector<float>& verts, const ViewportGridSpec& spec,
                     const Eigen::Matrix4d& M) {
    if (!spec.visible || spec.divisions <= 0 || spec.spacing <= 0.0f) {
        return;
    }

    const double extent = double(spec.spacing) * double(spec.divisions);
    const Eigen::Vector3d o = spec.origin;
    const float opacity = std::clamp(spec.opacity, 0.0f, 1.0f);
    // Every 10th step is the primary grid. The lines between are secondary:
    // the same grey pulled toward white, at a lower opacity, so they read lighter.
    constexpr int kMajorEvery = 10;
    constexpr float kSecondaryOpacity = 0.35f;

    for (int i = -spec.divisions; i <= spec.divisions; ++i) {
        const bool major = (i % kMajorEvery) == 0;
        const float line_opacity = major ? opacity : opacity * kSecondaryOpacity;
        const Eigen::Vector3f color_u = major
            ? spec.color_u
            : spec.color_u * 0.45f + Eigen::Vector3f(0.55f, 0.55f, 0.55f);
        const Eigen::Vector3f color_v = major
            ? spec.color_v
            : spec.color_v * 0.45f + Eigen::Vector3f(0.55f, 0.55f, 0.55f);
        const double offset = double(i) * double(spec.spacing);
        switch (spec.plane) {
            case ViewportGridSpec::Plane::XY: {
                const double y = o.y() + offset;
                pushLine(verts, M,
                         Eigen::Vector3d(o.x() - extent, y, o.z()),
                         Eigen::Vector3d(o.x() + extent, y, o.z()),
                         color_u, line_opacity);
                const double x = o.x() + offset;
                pushLine(verts, M,
                         Eigen::Vector3d(x, o.y() - extent, o.z()),
                         Eigen::Vector3d(x, o.y() + extent, o.z()),
                         color_v, line_opacity);
                break;
            }
            case ViewportGridSpec::Plane::XZ: {
                const double z = o.z() + offset;
                pushLine(verts, M,
                         Eigen::Vector3d(o.x() - extent, o.y(), z),
                         Eigen::Vector3d(o.x() + extent, o.y(), z),
                         color_u, line_opacity);
                const double x = o.x() + offset;
                pushLine(verts, M,
                         Eigen::Vector3d(x, o.y(), o.z() - extent),
                         Eigen::Vector3d(x, o.y(), o.z() + extent),
                         color_v, line_opacity);
                break;
            }
            case ViewportGridSpec::Plane::YZ: {
                const double z = o.z() + offset;
                pushLine(verts, M,
                         Eigen::Vector3d(o.x(), o.y() - extent, z),
                         Eigen::Vector3d(o.x(), o.y() + extent, z),
                         color_u, line_opacity);
                const double y = o.y() + offset;
                pushLine(verts, M,
                         Eigen::Vector3d(o.x(), y, o.z() - extent),
                         Eigen::Vector3d(o.x(), y, o.z() + extent),
                         color_v, line_opacity);
                break;
            }
        }
    }
}

}  // namespace

GridHelperRenderer::~GridHelperRenderer() { destroy(); }

bool GridHelperRenderer::init(WGPUDevice device, WGPUQueue queue,
                              WGPUTextureFormat color_format, int sample_count) {
    device_ = device;
    queue_  = queue;
    if (!device_ || !queue_) return false;

    if (grids_.empty()) {
        grids_.push_back(ViewportGridSpec::defaultBaseGrid());
    }

    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = 4096 * kFloatsPerVertex * sizeof(float);
        bdesc.label = svFromCStr("ifcviewer-wgpu.grid_vbo");
        vertex_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
    }
    {
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        bdesc.size  = kUniformSlotSize;
        bdesc.label = svFromCStr("ifcviewer-wgpu.grid_uniforms");
        uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
    }
    {
        WGPUBindGroupLayoutEntry entry = {};
        entry.binding    = 0;
        entry.visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
        entry.buffer.type             = WGPUBufferBindingType_Uniform;
        entry.buffer.minBindingSize   = 128;
        WGPUBindGroupLayoutDescriptor bgl_desc = {};
        bgl_desc.entryCount = 1;
        bgl_desc.entries    = &entry;
        bgl_desc.label      = svFromCStr("ifcviewer-wgpu.grid_bgl");
        bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);
    }
    {
        WGPUPipelineLayoutDescriptor pl_desc = {};
        pl_desc.bindGroupLayoutCount = 1;
        pl_desc.bindGroupLayouts     = &bgl_;
        pl_desc.label                = svFromCStr("ifcviewer-wgpu.grid_pl");
        pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);
    }
    {
        WGPUBindGroupEntry entry = {};
        entry.binding = 0;
        entry.buffer  = uniform_buffer_;
        entry.offset  = 0;
        entry.size    = kUniformSlotSize;
        WGPUBindGroupDescriptor bg_desc = {};
        bg_desc.layout     = bgl_;
        bg_desc.entryCount = 1;
        bg_desc.entries    = &entry;
        bg_desc.label      = svFromCStr("ifcviewer-wgpu.grid_bg");
        bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg_desc);
    }
    {
        WGPUShaderSourceWGSL wgsl_src = {};
        wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
        wgsl_src.code        = svFromCStr(GRID_LINE_WGSL);
        WGPUShaderModuleDescriptor sm_desc = {};
        sm_desc.nextInChain = &wgsl_src.chain;
        sm_desc.label       = svFromCStr("ifcviewer-wgpu.grid_wgsl");
        shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);
    }

    WGPUVertexAttribute attribs[2] = {};
    attribs[0].format = WGPUVertexFormat_Float32x3;
    attribs[0].offset = 0;
    attribs[0].shaderLocation = 0;
    attribs[1].format = WGPUVertexFormat_Float32x4;
    attribs[1].offset = 12;
    attribs[1].shaderLocation = 1;

    WGPUVertexBufferLayout vbl = {};
    vbl.arrayStride    = kFloatsPerVertex * sizeof(float);
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
    ct.format    = color_format;
    ct.blend     = &blend;
    ct.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = shader_module_;
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
    rp_desc.layout              = pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.grid_pipeline");
    rp_desc.vertex.module       = shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 1;
    rp_desc.vertex.buffers      = &vbl;
    rp_desc.fragment            = &frag;
    rp_desc.depthStencil        = &depth;
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_LineList;
    rp_desc.primitive.cullMode  = WGPUCullMode_None;
    rp_desc.multisample.count   = uint32_t(sample_count);
    rp_desc.multisample.mask    = 0xFFFFFFFFu;
    pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);

    rebuildVertices();
    return pipeline_ != nullptr;
}

void GridHelperRenderer::destroy() {
    if (bind_group_)      { wgpuBindGroupRelease(bind_group_);      bind_group_ = nullptr; }
    if (pipeline_)        { wgpuRenderPipelineRelease(pipeline_);  pipeline_ = nullptr; }
    if (shader_module_)   { wgpuShaderModuleRelease(shader_module_); shader_module_ = nullptr; }
    if (pipeline_layout_) { wgpuPipelineLayoutRelease(pipeline_layout_); pipeline_layout_ = nullptr; }
    if (bgl_)             { wgpuBindGroupLayoutRelease(bgl_);        bgl_ = nullptr; }
    if (uniform_buffer_)  { wgpuBufferRelease(uniform_buffer_);      uniform_buffer_ = nullptr; }
    if (vertex_buffer_)   { wgpuBufferRelease(vertex_buffer_);       vertex_buffer_ = nullptr; }
    vertex_count_ = 0;
    device_ = nullptr;
    queue_  = nullptr;
}

bool GridHelperRenderer::hasVisibleGrid() const {
    for (const ViewportGridSpec& spec : grids_) {
        if (spec.visible) return true;
    }
    return false;
}

void GridHelperRenderer::rebuildVertices() {
    if (!queue_ || !vertex_buffer_) return;

    std::vector<float> verts;
    verts.reserve(8192);
    for (const ViewportGridSpec& spec : grids_) {
        appendGridLines(verts, spec, world_to_viewer_);
    }

    vertex_count_ = int(verts.size() / kFloatsPerVertex);
    if (verts.empty()) {
        return;
    }

    const size_t byte_size = verts.size() * sizeof(float);
    if (byte_size > 4096 * kFloatsPerVertex * sizeof(float)) {
        if (vertex_buffer_) {
            wgpuBufferRelease(vertex_buffer_);
            vertex_buffer_ = nullptr;
        }
        WGPUBufferDescriptor bdesc = {};
        bdesc.usage = WGPUBufferUsage_Vertex | WGPUBufferUsage_CopyDst;
        bdesc.size  = byte_size;
        bdesc.label = svFromCStr("ifcviewer-wgpu.grid_vbo");
        vertex_buffer_ = wgpuDeviceCreateBuffer(device_, &bdesc);
    }

    wgpuQueueWriteBuffer(queue_, vertex_buffer_, 0, verts.data(), byte_size);
}

void GridHelperRenderer::setWorldToViewer(const Eigen::Matrix4d& world_to_viewer) {
    if (world_to_viewer_ == world_to_viewer) return;
    world_to_viewer_ = world_to_viewer;
    rebuildVertices();
}

void GridHelperRenderer::upsertGrid(const ViewportGridSpec& spec) {
    if (spec.id.empty()) return;

    ViewportGridSpec copy = spec;

    auto it = std::find_if(grids_.begin(), grids_.end(),
                           [&](const ViewportGridSpec& g) { return g.id == copy.id; });
    if (it != grids_.end()) {
        *it = copy;
    } else {
        grids_.push_back(copy);
    }
    rebuildVertices();
}

bool GridHelperRenderer::removeGrid(const std::string& id) {
    const auto it = std::find_if(grids_.begin(), grids_.end(),
                                 [&](const ViewportGridSpec& g) { return g.id == id; });
    if (it == grids_.end()) return false;
    grids_.erase(it);
    rebuildVertices();
    return true;
}

void GridHelperRenderer::clearGrids() {
    grids_.clear();
    rebuildVertices();
}

void GridHelperRenderer::encode(WGPURenderPassEncoder pass,
                                const Eigen::Matrix4f& view_proj,
                                const ViewportFog& fog,
                                const Eigen::Vector3f& eye,
                                const Eigen::Vector3f& forward,
                                int viewport_w_px, int viewport_h_px,
                                int device_pixel_ratio) {
    (void)viewport_w_px;
    (void)device_pixel_ratio;
    if (!master_visible_ || !hasVisibleGrid() || !pipeline_ || vertex_count_ <= 0 || viewport_h_px <= 0) {
        return;
    }

    uint8_t slot[kUniformSlotSize];
    std::memset(slot, 0, sizeof(slot));
    std::memcpy(slot, view_proj.data(), 16 * sizeof(float));
    float camera_pos[4];
    float view_forward[4];
    float fog_color[4];
    float fog_params[4];
    fog.writeUniformTail(camera_pos, view_forward, fog_color, fog_params, eye, forward);
    std::memcpy(slot + 64, camera_pos, 16);
    std::memcpy(slot + 80, view_forward, 16);
    std::memcpy(slot + 96, fog_color, 16);
    std::memcpy(slot + 112, fog_params, 16);
    wgpuQueueWriteBuffer(queue_, uniform_buffer_, 0, slot, sizeof(slot));

    wgpuRenderPassEncoderSetPipeline(pass, pipeline_);
    wgpuRenderPassEncoderSetVertexBuffer(pass, 0, vertex_buffer_, 0, WGPU_WHOLE_SIZE);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, bind_group_, 0, nullptr);
    wgpuRenderPassEncoderDraw(pass, uint32_t(vertex_count_), 1, 0, 0);
}
