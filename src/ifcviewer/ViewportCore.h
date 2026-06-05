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

#ifndef VIEWPORTCORE_H
#define VIEWPORTCORE_H

// Platform-agnostic render core. Owns the wgpu lifecycle state +
// (eventually) scene state + per-frame render path. Talks to its
// embedder through ViewportHost (window/canvas surface, scheduling,
// notifications) — has no Qt or browser dependencies of its own.
//
// First migration target (#84-a): wgpu instance/adapter/device/queue/
// surface ownership. The next subsystems (pipelines, models, render
// path) move incrementally across subsequent commits — each leaving
// the desktop build green. ViewportWindow currently holds reference
// members pointing back at ViewportCore's storage so its body doesn't
// have to acquire a `core_.` prefix on every wgpu touch. Those
// references shrink as render methods themselves move over.

#include <webgpu/webgpu.h>

#include <Eigen/Dense>

#include <cstdint>
#include <unordered_map>

#include "BufferPool.h"
#include "InstancedGeometry.h"
#include "ModelGpuData.h"
#include "StreamingThread.h"
#include "ViewportHost.h"

class ViewportCore {
public:
    explicit ViewportCore(ViewportHost* host);
    ~ViewportCore();

    ViewportCore(const ViewportCore&)            = delete;
    ViewportCore& operator=(const ViewportCore&) = delete;

    ViewportHost* host() const { return host_; }

    // ---- Scene-mutation methods --------------------------------------------
    //
    // composeInstanceFromPlacement composes the per-instance
    //   transform = federated_false_origin × model_transformation
    //             × coordinate_operation × placement
    // (all in metres, double precision) and rebakes the world AABB
    // from the mesh-local one. Used by the per-model recompose path
    // after any of the four federation matrices change. Pure scene
    // math — no GPU touch.
    void composeInstanceFromPlacement(InstanceCpu& inst,
                                      const ModelGpuData& m) const;

    // Friend access for ViewportWindow's reference proxies. As each
    // render method moves into ViewportCore it stops needing these
    // (it touches the fields directly); once everything has migrated
    // the friend declaration goes away.
    friend class ViewportWindow;

private:
    ViewportHost* host_;

    // ---- wgpu lifecycle state ------------------------------------------------
    //
    // Plain pointers (wgpu C handles); zero-init means "not yet
    // initialised". Owned by ViewportCore now; reference members in
    // ViewportWindow alias these so the existing call sites don't
    // need to change to use a `core_.` prefix.
    WGPUInstance      instance_           = nullptr;
    WGPUAdapter       adapter_            = nullptr;
    WGPUDevice        device_             = nullptr;
    WGPUQueue         queue_              = nullptr;
    WGPUSurface       surface_            = nullptr;
    WGPUTextureFormat surface_format_     = WGPUTextureFormat_Undefined;
    bool              surface_configured_ = false;

    // ---- Pipelines + bind-group layouts (built once after init) -------------
    //
    // Main render pipeline group: one shader module + two bind group
    // layouts (frame uniforms at group=0, per-model storages at
    // group=1) feeding both the opaque-pass pipeline and the
    // transparent-pass variant. The transparent pipeline shares the
    // shader and layout; it differs only in depthWriteEnabled=False
    // and the SrcAlpha / OneMinusSrcAlpha blend on the color target.
    WGPUShaderModule    main_shader_module_       = nullptr;
    WGPUBindGroupLayout frame_bgl_                = nullptr;  // group 0
    WGPUBindGroupLayout model_bgl_                = nullptr;  // group 1
    WGPUPipelineLayout  pipeline_layout_          = nullptr;
    WGPURenderPipeline  main_pipeline_            = nullptr;
    WGPURenderPipeline  main_pipeline_transparent_ = nullptr;

    // HiZ occlusion-cull pipeline group. Downsamples MSAA depth into a
    // mip pyramid; consumed by next-frame cull.
    WGPUShaderModule    hiz_shader_module_   = nullptr;
    WGPUBindGroupLayout hiz_bgl_             = nullptr;
    WGPUPipelineLayout  hiz_pipeline_layout_ = nullptr;
    WGPURenderPipeline  hiz_pipeline_        = nullptr;

    // Edge-silhouette pipeline group. Drawn after the main pass; reads
    // the depth/normal attachments to emit dark outlines.
    WGPUShaderModule    edge_shader_module_   = nullptr;
    WGPUBindGroupLayout edge_bgl_             = nullptr;
    WGPUPipelineLayout  edge_pipeline_layout_ = nullptr;
    WGPURenderPipeline  edge_pipeline_        = nullptr;

    // Pick pass. Reuses pipeline_layout_ — same set of bindings as the
    // main pass since the pick fragment also vertex-pulls instance data.
    WGPURenderPipeline  pick_pipeline_ = nullptr;

    // ---- Scene state ---------------------------------------------------------
    //
    // Sub-allocator for chunk vertex + index buffers. All per-chunk
    // pool slices come from here; nothing else uses it. Replaces the
    // old hand-picked streaming_vram_budget_bytes_ knob entirely.
    BufferPool pool_;

    // Background worker that does scatter-gather chunk reads off the
    // render thread. driveStreamingLoads enqueues requests for visible
    // non-resident chunks and drains completed results into the pool
    // on subsequent frames.
    StreamingThread streaming_thread_;

    // Per-model GPU + CPU state, keyed by viewport-assigned model_id.
    std::unordered_map<uint32_t, ModelGpuData> models_gpu_;
    uint32_t next_model_id_  = 1;
    // Globally-unique object_id allocator. Each applyCachedModel rebases
    // the sidecar's local object_ids by base_object_id_so_far so picks
    // are unambiguous across models.
    uint32_t next_object_id_ = 1;

    // Federation false origin (metres, double precision). Applied to
    // every instance composition so geometry rebased through a large
    // model offset doesn't lose float32 precision near the GPU origin.
    Eigen::Matrix4d federated_false_origin_meters_ = Eigen::Matrix4d::Identity();
};

#endif  // VIEWPORTCORE_H
