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
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "BufferPool.h"
#include "InstanceCompose.h"
#include "InstancedGeometry.h"
#include "ModelGpuData.h"
#include "SelectionState.h"
#include "StreamingThread.h"
#include "ViewportHost.h"
#include "VisibilityState.h"

// Render-loop constants shared between ViewportCore and ViewportWindow.
// Kept here (not in OverlayRenderer.h) so IfcViewerCore stays Qt-free.
// ViewportWindow.cpp asserts the section-plane cap matches
// OverlayRenderer's so the WGSL clip-plane array and the section-tool
// state vector agree by construction.
constexpr int kMaxSectionPlanes = 6;
constexpr uint32_t kViewportSampleCount = 4;

// Per-frame uniform layout. Matches the WGSL struct the main pipeline
// declares (see ViewportCore.cpp MAIN_WGSL). Both buildPipelines (in
// ViewportCore) and updateFrameUniforms (currently in ViewportWindow)
// allocate / write this; keeping the type here makes the layout the
// single source of truth.
struct FrameUniforms {
    float view_proj[16];
    float light_dir[4];     // xyz = unit dir toward light, w unused
    float fill_dir[4];      // xyz = secondary fill dir
    float sky_color[4];     // xyz = sky-tint ambient, w unused
    float ground_color[4];  // xyz = ground-tint ambient, w unused
    int   clip_count;       // active section-plane count (≤ kMaxSectionPlanes)
    int   _pad_clip[3];     // pad to 16-byte alignment for the array below
    float clip_planes[kMaxSectionPlanes][4]; // xyz = world-space unit normal, w = plane offset
    float xray_alpha_cap;   // X-ray mode: fragment alpha clamped to min(in.color.a, cap)
    float _pad_xray[3];     // pad to 16-byte alignment so the struct stays vec4-aligned
};
static_assert(sizeof(FrameUniforms)
                  == 16 * sizeof(float)
                   + 4 * 4 * sizeof(float)
                   + 4 * sizeof(int)
                   + kMaxSectionPlanes * 4 * sizeof(float)
                   + 4 * sizeof(float),
              "FrameUniforms must match WGSL layout");

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

    // Cross-model object_id lookup. Delegates to
    // InstanceCompose::findInstanceInModels; the wrapper exists so
    // callers don't have to know about the underlying map of models.
    bool findInstance(uint32_t object_id,
                      InstanceCompose::InstanceLookup& out) const;

    // A point that actually lies on the model's first instance — used
    // by the federation false-origin guess on first geometry. Pure
    // read of models_gpu_; no GPU touch.
    bool firstGeometryPointWorldM(uint32_t model_id,
                                  Eigen::Vector3d& out) const;

    // ---- Scene mutators -----------------------------------------------------
    //
    // All of these flip scene state (or post a recompose) and ask the
    // host to schedule another frame via host_->requestFrame(). The host
    // is responsible for coalescing those requests (Qt's requestUpdate
    // does it natively; the web host wraps requestAnimationFrame).

    void removeModel(uint32_t model_id);
    void resetScene();
    void hideModel(uint32_t model_id);
    void showModel(uint32_t model_id);

    // Federation matrix setters. Each writes to model state and posts
    // a recompose so per-instance world matrices stay consistent with
    // the configured georef + transformation pipeline.
    void setFederatedFalseOrigin(const Eigen::Matrix4d& matrix_meters);
    void setModelCoordinateOperation(uint32_t model_id,
                                     const Eigen::Matrix4d& matrix_meters);
    void setModelTransformation(uint32_t model_id,
                                const Eigen::Matrix4d& matrix_meters);

    // Walk every instance of `model_id`, recompose its transform from
    // the current federation matrices, refresh per-chunk world AABBs,
    // and re-upload InstanceGpu[] into m.instance_storage. No-op if
    // the model is unknown, has no instances, or wgpu init hasn't
    // completed.
    void recomposeAndUploadModel(uint32_t model_id);

    // ---- Camera math --------------------------------------------------------
    //
    // buildViewProj feeds every cull, streaming, pick and render path
    // — keep it as a single helper so the projection_ortho_ toggle
    // and the near-vertical up-vector switch can't drift between
    // call sites. computeSceneAabb folds every visible model's
    // world AABBs into one — used by viewAll and the bench camera.
    // chunkScreenAreaPx projects one chunk's world AABB through a
    // VP into 2D pixels — the streaming loader's priority signal.
    void buildViewProj(Eigen::Matrix4f& view_out,
                       Eigen::Matrix4f& proj_out) const;
    bool computeSceneAabb(float mn[3], float mx[3]) const;
    float chunkScreenAreaPx(const ModelGpuData::Chunk& c,
                            const Eigen::Matrix4f& vp_mat) const;

    // Camera state snapshot for save-view / restore-view round-trips.
    // Same shape as ViewportWindow::CameraState (kept as a `using` alias
    // there) so bonsai's HomeView code keeps working.
    struct CameraState {
        Eigen::Vector3f target = Eigen::Vector3f::Zero();
        float distance = 50.0f;
        float yaw      = 45.0f;
        float pitch    = 30.0f;
    };

    // ---- Camera mutators / getters ------------------------------------------

    void viewAll();
    void setCamera(float tx, float ty, float tz,
                   float dist, float yaw_deg, float pitch_deg);
    void setStandardView(float yaw_deg, float pitch_deg);
    void toggleProjection();
    bool projectionOrtho() const { return projection_ortho_; }
    std::string cameraString() const;
    CameraState cameraState() const;

    // Re-aim the orbit camera so [mn, mx] fits the view with `padding`
    // headroom (1.10 typical). Used by viewAll and focusOnSelectedObject.
    void frameAabb(const float mn[3], const float mx[3], float padding);

    // Per-object AABB lookup. Aggregates every instance of `object_id`
    // across every loaded model. Two overloads — float[3] for internal
    // callers; the Eigen::Vector3f overload exists so bonsai's volume
    // readout + focus paths compile unchanged.
    bool computeObjectAabb(uint32_t object_id, float mn[3], float mx[3]) const;
    bool computeObjectAabb(uint32_t object_id,
                           Eigen::Vector3f& mn, Eigen::Vector3f& mx) const;

    // Sum of mesh-local volumes (m³) of every instance whose object_id
    // is in `object_ids`. Each instance is scaled by |det(placement_3x3)|
    // to pick up mapped-item scale/mirror; signed-tetrahedra absolute
    // value means winding is ignored. Volumes are precomputed at
    // applyCachedModel — this call is just lookups + multiplies.
    double volumeOfObjects(const std::vector<uint32_t>& object_ids) const;
    // Per-object variant. Used by the Volume tool to drive both the
    // total HUD and the per-object overlay labels at AABB centres.
    std::vector<std::pair<uint32_t, double>>
        volumesPerObject(const std::vector<uint32_t>& object_ids) const;

    // ---- Pipeline construction --------------------------------------------
    //
    // buildPipelines creates the main render pipelines (opaque +
    // transparent variants), bind group layouts, the per-frame UBO,
    // and the WGSL shader module. Called once after the device + queue
    // come up + the surface format is picked.
    //
    // ensureSelectionFlagsBuffer (re)allocates the selection flags
    // storage buffer geometrically as next_object_id_ grows, and
    // (re)builds the frame bind group when its referenced buffers
    // change. uploadSelectionFlagsIfDirty flushes
    // selection_.fillFlagsArray() into the GPU when selection_'s dirty
    // flag is set — called once per frame at render time.
    bool buildPipelines();
    void ensureSelectionFlagsBuffer();
    void uploadSelectionFlagsIfDirty();

    // ---- wgpu lifecycle ----------------------------------------------------
    //
    // initWgpu brings up the wgpu instance, gets the platform surface
    // from host_->createSurface, requests adapter + device + queue,
    // probes the streaming pool capacity, starts the background loader
    // thread, and picks the swap-chain surface format. Does NOT build
    // pipelines — the host runs the pipeline construction after this
    // (so VW can still keep its HiZ / edge / pick / overlay builders
    // co-located).
    //
    // `web_limits` forces the WebGPU spec mandatory floor (128 MB max
    // storage binding, 256 MB max buffer) instead of the adapter's
    // actual maximum — used by --web-limits to verify chunking fits
    // through browser constraints.
    //
    // shutdown tears down everything ViewportCore owns. The host's own
    // teardown (depth/MSAA/HiZ/edge/pick attachments + overlays) must
    // run BEFORE this call so its device-owned resources release
    // against a still-live device.
    bool initWgpu(bool web_limits);
    void shutdown();

private:
    bool probeAndCreatePool();

public:

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

    // ---- Frame uniforms + selection bind ----------------------------------
    //
    // The per-frame UBO (view-proj + lighting + section planes + xray
    // params) and the frame bind group it lives in alongside the
    // selection flags storage buffer at group=0 binding=1.
    // ensureSelectionFlagsBuffer is the only writer for the buffer +
    // bind group; uploadSelectionFlagsIfDirty repopulates the flags
    // from selection_ when it changes.
    WGPUBuffer    frame_uniform_buffer_     = nullptr;
    WGPUBindGroup frame_bind_group_         = nullptr;
    WGPUBuffer    selection_flags_buffer_   = nullptr;
    uint32_t      selection_flags_capacity_ = 0;  // u32 entries
    std::vector<uint32_t> selection_flags_scratch_;

    // Selection + per-element visibility state machines. Pure CPU
    // bookkeeping today (no GPU touch beyond the readback uploaded via
    // selection_flags_buffer_). Mutated on the main thread between
    // renders; cull workers read concurrently which is safe as long
    // as no concurrent writes.
    SelectionState  selection_;
    VisibilityState visibility_;

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

    // Flips true once initWgpu has finished bringing up device + queue
    // (still done on the ViewportWindow side today — moves with #84-i).
    // Any method that uploads or encodes work checks this guard so a
    // queued setter that runs before init becomes a no-op rather than
    // crashing on a null device.
    bool wgpu_initialized_ = false;

    // ---- Surface geometry ----------------------------------------------------
    //
    // configured_w_/h_ track the device-pixel framebuffer size as last
    // requested through host_->framebufferSize(). depth + MSAA attachments
    // are sized against these.
    int configured_w_ = 0;
    int configured_h_ = 0;

    // ---- Orbit / fly camera state -------------------------------------------
    //
    // Mirrors the GL viewport's defaults; the orbit math lives in
    // buildViewProj (also in ViewportCore). BIM scenes are +Z up.
    float camera_target_[3]  = { 0.0f, 0.0f, 0.0f };
    float camera_distance_   = 50.0f;
    float camera_yaw_deg_    = 45.0f;
    float camera_pitch_deg_  = 30.0f;
    float camera_fov_y_deg_  = 45.0f;
    float camera_near_       = 0.1f;
    float camera_far_        = 10000.0f;
    // Perspective by default; toggleProjection (P key) flips this. When
    // true, buildViewProj uses an orthographic matrix sized by
    // camera_distance_ × tan(fov/2) so toggling looks like a smooth
    // swap rather than a jump in apparent size.
    bool  projection_ortho_  = false;

    // RGBA in linear-space [0..1]. The render-pass clear value applies
    // an sRGB-to-linear conversion on top so the on-screen colour
    // matches the hex value passed via setBackgroundColor.
    Eigen::Vector4f background_color_ = {0.125f, 0.137f, 0.161f, 1.0f};
};

#endif  // VIEWPORTCORE_H
