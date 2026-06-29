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

#include <atomic>
#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "BufferPool.h"
#include "InstanceCompose.h"
#include "InstancedGeometry.h"
#include "ModelGpuData.h"
#include "SectionPlane.h"
#include "SelectionState.h"
#include "SidecarCache.h"
#include "StreamingLoader.h"
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

    // ---- Incremental orbit navigation ---------------------------------------
    //
    // Pixel-delta camera moves, shared by every host (Qt desktop + web).
    // Hosts translate raw pointer/wheel events into these calls and own
    // their own UI concerns (drag promotion, pivot indicator, cursor
    // capture); the orbit math lives here so it can't drift between
    // platforms. Each schedules a frame via the host.
    //
    // orbitBy:  drag-right yaws the world right (yaw -= dx), drag-down
    //           tilts the camera up (pitch += dy). 0.4 deg/px matches GL.
    // panBy:    shifts the target in the camera's screen plane; world
    //           units/pixel track the frustum height at the pivot so the
    //           feel is zoom-independent. Needs the viewport height.
    // dollyBy:  each wheel notch zooms ~10% (distance *= 0.9^notches);
    //           positive notches zoom in.
    void orbitBy(float dx_px, float dy_px);
    void panBy(float dx_px, float dy_px, int viewport_height_px);
    void dollyBy(float notches);

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

    // Build the FrameUniforms struct (view-proj + lighting + section
    // planes + xray cap) from current camera + section_planes_ +
    // xray_alpha_cap_ and upload it via the queue. Called once per
    // render() at frame start, before any draw encode.
    void updateFrameUniforms();

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

#if defined(__EMSCRIPTEN__)
    // Async-init driver for the web. The spin-wait pattern in initWgpu()
    // doesn't work on Dawn-web — RequestDevice's callback never fires
    // when the caller is parked inside an Asyncify spin loop, even with
    // AllowSpontaneous + emscripten_sleep yields. The fix is to mirror
    // the original main_web.cpp spike: nested callbacks, no spin.
    // Fires `on_complete(true)` once instance + adapter + device + queue
    // + pool + surface_format_ are all in place; on any failure, fires
    // on_complete(false). Caller is responsible for calling
    // buildPipelines + buildHiz/Edge/Pick + scene-load after on_complete.
    void initWgpuAsyncWeb(std::function<void(bool ok)> on_complete);
#endif

    // ---- Chunk residency (#84-n) ------------------------------------------
    //
    // Build the per-chunk WGPUBindGroup over its current pool slices +
    // shared model storage. Idempotent — releases any previous bind group
    // first. Called after a slice's bytes have been written via
    // applyStreamedChunk, and from buildModelBindGroup for every chunk
    // at model-load time.
    void buildChunkBindGroup(ModelGpuData& m, std::size_t chunk_idx);

    // Pool-allocate vertex + index slices for the chunk, queueWriteBuffer
    // the bytes, build the bind group, flip is_resident=true. Returns
    // false on pool OOM (caller should have made room first); on
    // failure, no slices are claimed and is_resident stays false.
    // Called from the worker-result drain (async) and from
    // loadChunkBytesAndUploadGpu (sync first-frame fallback). Fires
    // on_volume_dirty_ when this chunk filled in any mesh-local volume
    // so consumers (the Volume tool's HUD) can refresh.
    bool applyStreamedChunk(ModelGpuData& m, std::size_t chunk_idx,
                            const std::vector<std::uint8_t>& vbytes,
                            const std::vector<std::uint32_t>& idx);

    // Synchronous-fallback path: read this chunk's byte ranges from
    // the sidecar file directly (no worker thread) and apply. Used by
    // the screenshot test on first frame, and any caller that needs a
    // chunk resident inside the same call (no deferred-state to
    // manage). Returns true on success.
    bool loadChunkBytesAndUploadGpu(ModelGpuData& m, std::size_t chunk_idx);

    // Release the chunk's pool slices + bind group, clear residency.
    // No-op if !c.is_resident.
    void unloadChunk(ModelGpuData& m, std::size_t chunk_idx);

    // Build the worker request for a chunk. Walks the chunk's mesh_ids
    // and derives scatter-gather byte/index ranges from each mesh's
    // sidecar offsets. Pure function of model + chunk metadata; safe to
    // call from the main thread.
    static StreamingThread::Request makeChunkRequest(
        const ModelGpuData& m, std::size_t chunk_idx, std::uint32_t model_id);

    // Per-frame streaming driver. Called from render() after cull. Walks
    // every model's chunks once for residency bookkeeping, drains the
    // worker's completed results into the pool, then enqueues new
    // requests for visible non-resident chunks (LRU + priority eviction
    // when the pool can't fit). Triggers host_->requestFrame() while
    // residency is still settling so the render loop keeps ticking.
    void driveStreamingLoads();

    // ---- Sidecar / direct load (#84-q) -----------------------------------
    //
    // Apply a parsed sidecar's metadata + planned chunk layout to
    // models_gpu_[model_id]. Builds the per-chunk small buffers
    // (visible_draws / prefix_sums / per_chunk_uniform), the per-model
    // mesh + instance storage SSBOs, and the spatial chunk plan; chunk
    // vertex/index slices stay non-resident until the streaming loader
    // brings them in. Triggers an auto-viewAll on the first model (so a
    // freshly-loaded scene frames itself).
    void applyCachedModel(std::uint32_t model_id, StreamingSidecar metadata);

    // Qt-free sidecar load: readSidecarMetadataOnly + applyCachedModel.
    // Used by the web build (and any other non-Qt embedder) so the
    // public ViewportWindow::loadSidecar's QString + QFile triage
    // tilde-expansion doesn't have to be replicated. Returns 0 on
    // any failure (device not ready, file missing, magic / version
    // mismatch) and the freshly-assigned model_id on success.
    std::uint32_t loadSidecarFromPath(const std::string& path);

#if defined(__EMSCRIPTEN__)
    // Web byte-range load (#88). Loads a sidecar from the JS-registered
    // File (Module.__ifcvFile) WITHOUT copying the whole file into the
    // wasm heap: the head + tail metadata are read via Blob.slice, the
    // streaming model is built, and it is tagged blob-sourced so each
    // chunk's vertex/index byte ranges are pulled lazily through the async
    // path. Asynchronous — returns immediately and frames the model from
    // the JS completion callback. resetScene() first to replace.
    void loadSidecarFromBlobWeb();

    // Kick off the async blob read of one chunk's vertex + index byte
    // ranges. applyStreamedChunk runs in the JS completion callback;
    // c.is_loading is held until then. No-op if the model/chunk vanished
    // mid-flight (e.g. a resetScene landed between issue and completion).
    void beginWebChunkLoad(std::uint32_t model_id, std::size_t chunk_idx);
#endif

    // Direct-load (bonsai-side) entry points. Bonsai's SceneLoader feeds
    // the viewer one mesh + one instance at a time, then calls
    // finalizeModel once everything's staged. The staging map lives on
    // ViewportCore so both halves can share it.
    void uploadMeshChunk(const MeshChunk& chunk);
    void uploadInstanceChunk(const InstanceChunk& chunk);
    void finalizeModel(std::uint32_t model_id);

    // ---- Cross-chunk + screenshot capture (#84-v) -------------------------
    //
    // Rebuild every chunk's bind group for the supplied model. No-op
    // when the model has no GPU storage yet (empty load — the chunk
    // draw loop skips it anyway).
    void buildModelBindGroup(ModelGpuData& m);

    // Arm a one-shot screenshot capture. The next render() encodes a
    // surface-to-buffer copy alongside the main pass, maps it back to
    // RGBA8, and saves a PNG at `path`. `quit_after` requests host
    // shutdown once the capture writes — the host's quit() decides
    // when (synchronously or queued).
    void captureNextFrameToPng(const std::string& path, bool quit_after);
    bool pending_screenshot_quit_ = false;

    // Encode a surface-to-buffer copy of the swapchain texture into the
    // supplied encoder. Returns the allocated readback buffer (caller
    // releases) and writes the row-aligned bytes-per-row through
    // `padded_bpr_out`. The caller is expected to wait for queue submit
    // before calling finalizeScreenshotCapture below.
    WGPUBuffer encodeScreenshotCapture(WGPUCommandEncoder enc,
                                       WGPUTexture surface_texture,
                                       std::uint32_t& padded_bpr_out);

    // After queue submit, map the staging buffer back to host memory,
    // BGRA→RGBA-swap into a tightly-packed RGBA8 image, hand it to
    // host_->saveScreenshotRgba8, then release the staging buffer.
    // Clears pending_screenshot_path_ and (when pending_screenshot_quit_
    // was set) invokes host_->quit().
    void finalizeScreenshotCapture(WGPUBuffer capture_buffer,
                                   std::uint32_t padded_bpr);

    // ---- Section planes (#84-y) -------------------------------------------
    //
    // Append a section plane at the supplied surface hit, with a normal
    // auto-flipped toward the camera so the first click reveals the
    // surface the user just clicked. `visual_radius` controls the
    // overlay gizmo size; <= 0 falls back to 1 m. Returns false when
    // the kMaxSectionPlanes cap is already reached.
    bool addSectionPlaneAtSurface(const Eigen::Vector3f& point,
                                  const Eigen::Vector3f& normal,
                                  float visual_radius);

    // Remove a single section plane by index (no-op when out of range).
    void removeSectionPlane(int index);

    // Drop every section plane. No-op when none are active.
    void clearSectionPlanes();

    // ---- Render loop (#84-x) ----------------------------------------------
    //
    // Encode one frame: acquire the swapchain texture, run cull (parallel
    // when WGPU_CULL_THREADS!=0), drive streaming residency, encode the
    // two-pass main draw, edge pass, HiZ resolve, and (optionally) the
    // screenshot capture. Calls host_->encodeOverlaysInMainPass and
    // host_->encodeOverlaysPostMain for the overlay layers (still
    // Qt-bound), and host_->onFrameStats for the bench / status bar
    // listeners. Idempotent re: framebuffer size — reconfigures the
    // surface on Outdated/Lost. Returns early when the surface query
    // fails so the next frame retries cleanly.
    void render();

    // ---- Surface configuration (#84-u) ------------------------------------
    //
    // Configure the swapchain at the given physical size. Picks a present
    // mode from caps + preference order (Mailbox → Immediate → FifoRelaxed
    // → Fifo, overridable via WGPU_PRESENT_MODE), reconfigures the
    // surface, then (re)allocates the depth + MSAA color + HiZ resolve
    // textures and invalidates the HiZ + edge bind groups so they
    // rebuild against the new depth view on next encode.
    void configureSurface(int width_px, int height_px);

    // ---- HiZ + framebuffer attachments (#84-r) ----------------------------
    //
    // Build the HiZ resolve pipeline (and shader module + BGL + uniform
    // buffer). Run once during init, after buildPipelines but before the
    // first render. Returns false on pipeline creation failure.
    bool buildHizPipeline();

    // (Re)allocate the resolve depth texture + ping-pong staging buffers
    // to match a viewport_w x viewport_h surface. Idempotent when
    // dimensions match. Resets ping-pong state so any in-flight map is
    // dropped (caller already ensured the surface resize blocked).
    void ensureHizTextures(int viewport_w, int viewport_h);

    // Tear down every HiZ-owned wgpu resource (pipeline + textures +
    // staging buffers + pyramid). Called from shutdown() before
    // device_ is released.
    void releaseHizResources();

    // Encode the per-frame resolve pass + texture-to-buffer copy into
    // the supplied command encoder. Picks an idle ping-pong slot (or
    // returns -1 when both slots are still in flight). Returns the
    // chosen slot so the caller can later call startHizMap on it.
    int encodeHizResolve(WGPUCommandEncoder enc);

    // Queue the async map for the given slot. Records the VP the
    // resolve was rendered with so the eventual readback knows which
    // matrix produced the depth.
    void startHizMap(int slot, const Eigen::Matrix4f& vp_used);

    // Drain any mapAsync completions that fired since last frame,
    // rebuild the CPU mip pyramid from the freshly-mapped data, swap
    // it into hiz_pyramid_. Non-blocking — frames where no slot has
    // completed just leave the pyramid untouched.
    void drainHizReadbacks();

    // Per-instance HiZ occlusion test. Projects the AABB through
    // hiz_vp_ (the matrix the pyramid was rendered with), maps to mip
    // pixel coords, max-reduces across the covered area, rejects when
    // the AABB's nearest projected z is behind the pyramid coverage.
    bool aabbOccludedByHiz(const float mn[3], const float mx[3]) const;

    // Ensure the main render-pass depth attachment matches the current
    // surface size. Created with MSAA + TextureBinding usage so the HiZ
    // resolve can sample it. Idempotent when dimensions match.
    void ensureDepthTexture(int w, int h);
    void releaseDepthTexture();

    // MSAA color attachment for the main pass. Same lifecycle pattern
    // as the depth texture above.
    void ensureMsaaColorTexture(int w, int h);
    void releaseMsaaColorTexture();

    // ---- Edge silhouette post-process (#84-s) -----------------------------
    //
    // Build the edge pipeline + shader + BGL. Run after initWgpu's
    // device is up. Returns false on pipeline creation failure.
    bool buildEdgePipeline();

    // Encode the edge silhouette fullscreen pass into the supplied
    // command encoder. No-op when edges_enabled_ is false or the
    // pipeline / depth view / surface view is null. Lazily builds the
    // bind group on first call after a surface resize.
    void encodeEdgePass(WGPUCommandEncoder enc, WGPUTextureView surface_view);

    // Tear down the edge pipeline + bind group + supporting state.
    // Called from shutdown() before the device dies.
    void releaseEdgeResources();

    // ---- Pick + raycast (#84-t) -------------------------------------------
    //
    // Build the pick pipeline. Reuses the main shader module's
    // vs_pick / fs_pick entry points + pipeline_layout_ (same bindings
    // as the main draw). Single-sample target. Returns false on
    // pipeline creation failure.
    bool buildPickPipeline();

    // (Re)allocate the pick MRT attachments + readback staging buffers
    // to the supplied size. Idempotent when dimensions match.
    void ensurePickAttachments(int w, int h);

    // Encode the one-shot pick pass + copy the (x, y) texel into the pick
    // staging buffer(s) and submit. Shared by the sync (pickObjectAt) and
    // async (pickObjectAtAsync) readbacks. Caller validates bounds/attachments.
    void encodePickReadbackToStaging(int x_pixels, int y_pixels, bool want_normal);

    // Tear down every pick-owned wgpu resource (pipeline + MRTs +
    // staging buffers). Called from shutdown() before device_ dies.
    void releasePickResources();

    // Encode + readback the single-pixel object_id + normal at (x, y).
    // Returns 0 on miss (or any guard failure). When `normal_out` is
    // non-null, decodes the RGBA16F normal MRT's first texel into a
    // unit world-space normal. Synchronous (interactive click path).
    std::uint32_t pickObjectAt(int x_pixels, int y_pixels,
                               Eigen::Vector3f* normal_out = nullptr);

    // Route a pick result into the selection state machine (replace / add /
    // remove / empty-click-clear), mirroring the desktop click semantics.
    // Marks selection_ dirty for the next render's flush.
    void applyPickToSelection(std::uint32_t object_id, bool add, bool remove);

#if defined(__EMSCRIPTEN__)
    // Async object pick for the web build: encodes the same pick pass as
    // pickObjectAt but reads the staging buffer back via a spontaneous map
    // callback (no blocking spin, which would hang the JS event loop) and
    // delivers object_id to `cb`. Object-id only; one pick in flight at a
    // time (a pick issued while another is mapping is dropped → cb(0)).
    void pickObjectAtAsync(int x_pixels, int y_pixels,
                           std::function<void(std::uint32_t)> cb);
#endif

    // Marquee box select: encode the pick pass, copy the (x, y, w, h)
    // sub-rect of the object_id MRT back, return the set of unique
    // non-zero ids. Synchronous (rare interaction).
    std::vector<std::uint32_t> picksInRect(int x, int y, int w, int h);

    // Run pickObjectAt + raycast against every instance carrying the
    // hit object_id, then return the closest hit's world position,
    // world normal, and (optionally) the bounding-sphere radius. The
    // normal preference goes to the pick MRT's per-fragment value; the
    // AABB-face normal is a fallback.
    bool pickSurfaceAt(int x_pixels, int y_pixels,
                       std::uint32_t& object_id_out,
                       Eigen::Vector3f& world_pos_out,
                       Eigen::Vector3f& world_normal_out,
                       float* aabb_radius_out = nullptr);

    // Per-pick result for the Area / Length / Volume tools. The
    // composed_transform mirrors InstanceCpu::transform so callers can
    // round-trip from mesh-local back to world without re-deriving it.
    struct MeshLocalPick {
        std::uint32_t object_id   = 0;
        std::uint32_t model_id    = 0;
        std::uint32_t mesh_id     = 0;
        float    mesh_local  [3]  = {0, 0, 0};
        float    world_pos   [3]  = {0, 0, 0};
        float    world_normal[3]  = {0, 0, 0};
        float    composed_transform[16] = {1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1};
    };

    // pickSurfaceAt + transform back into the picked instance's mesh-
    // local space, refined against the cached CPU mesh shadow when
    // available (Möller-Trumbore per-triangle). Output sits on a real
    // triangle, not the AABB face. Returns false on miss.
    bool pickMeshLocalAt(int x, int y, MeshLocalPick& out);

    // Bonsai-side raycast helper. Walks every visible instance's
    // world-AABB, then Möller-Trumbore against the cached mesh
    // triangles. `dir` must be a unit vector — distance is the ray's
    // t parameter (= world distance only at |dir|=1).
    struct RaycastHit {
        std::uint32_t object_id    = 0;
        float         distance     = 0.0f;
        float         world_pos[3] = {0, 0, 0};
        float         world_normal[3] = {0, 0, 0};
    };
    bool raycast(const float origin[3], const float dir[3], RaycastHit& out) const;

    // ---- Cull (#84-p) -----------------------------------------------------
    //
    // Per-instance occlusion test, supplied by the caller. Wired by
    // ViewportWindow to its HiZ pyramid (still VW-side) — when the
    // function is null, occlusion is implicitly "miss" and only
    // frustum + contribution culling apply.
    using HizOccludedFn = std::function<bool(const float mn[3], const float mx[3])>;

    // Walk every instance in `m`, frustum-test, contribution-test, and
    // (when `hiz_occluded` is non-null) HiZ-test. Populates each
    // chunk's visible_draws_scratch + prefix_sums_scratch with the
    // partition the render pass will issue. Returns the number of
    // instances HiZ rejected so render() can aggregate the counter.
    // `const` because cull doesn't touch wgpu state — pure CPU work
    // over ModelGpuData scratch fields.
    std::uint32_t cullModelCpuCompute(
        ModelGpuData& m,
        const float planes[6][4],
        const float eye[3],
        const float forward[3],
        const float right[3],
        const float up[3],
        float focal_px,
        float min_radius_px,
        float lod1_threshold_px,
        const HizOccludedFn& hiz_occluded) const;

    // Upload the per-chunk visible-draw + prefix-sum partitions + the
    // per-chunk uniform (counts + the opaque/transparent split point)
    // for every chunk in `m`. Called once per visible model after
    // cullModelCpuCompute fills the scratch.
    void cullModelCpuUpload(ModelGpuData& m);

    // ---- Per-frame cull-cycle debug counters -----------------------------
    //
    // Tally how often the LOD1 pick triggered, how many triangles it
    // saved, and how many instances either had no LOD1 to pick or sat
    // above the threshold. Reset at the end of every render() cycle by
    // the bench / frame-stats path in VW. Mutable so cullModelCpuCompute
    // can stay const for the rest of its data flow.
    mutable std::uint32_t lod1_dbg_count_           = 0;
    mutable std::uint32_t lod0_dbg_eligible_count_  = 0;
    mutable std::uint32_t lod0_dbg_no_lod1_count_   = 0;
    mutable std::uint64_t lod1_dbg_tris_saved_      = 0;

private:
    bool createPool();

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
    WGPUBuffer          hiz_uniform_buffer_  = nullptr;
    WGPUBindGroup       hiz_bind_group_      = nullptr;

    // Downsampled HiZ depth target (single-sampled, 256-wide-by-aspect).
    // The resolve pass writes max-reduced depth into this; one frame later
    // we copy it into a CPU-mappable staging buffer and rebuild the mip
    // pyramid.
    WGPUTexture     hiz_resolve_texture_ = nullptr;
    WGPUTextureView hiz_resolve_view_    = nullptr;
    std::uint32_t   hiz_resolve_w_       = 0;
    std::uint32_t   hiz_resolve_h_       = 0;
    std::uint32_t   hiz_padded_bpr_      = 0;  // bytes per row in the staging buffer

    // Ping-pong async readback. Frame N submits a copy into slot
    // hiz_write_idx_ and calls mapAsync. Frame N+K (K >= 1) calls
    // processEvents to drain; whichever slot signalled completion is
    // mapped, read into hiz_pyramid_, and unmapped — making the pyramid
    // 1+ frames stale (the "slightly-stale depth" pattern). Two slots
    // overlap GPU write with CPU read; we never block on the readback.
    enum class HizSlotState : std::uint8_t { Idle, Mapping, Mapped };
    static constexpr int HIZ_SLOTS = 2;
    WGPUBuffer       hiz_staging_buffers_[HIZ_SLOTS] = { nullptr, nullptr };
    Eigen::Matrix4f  hiz_slot_vp_       [HIZ_SLOTS];
    HizSlotState     hiz_slot_state_    [HIZ_SLOTS] = { HizSlotState::Idle,
                                                        HizSlotState::Idle };
    int              hiz_write_idx_      = 0;

    // CPU mip pyramid (max-reduce). hiz_pyramid_[hiz_mip_offset_[L] + y*W + x].
    std::vector<float>          hiz_pyramid_;
    std::vector<std::uint32_t>  hiz_mip_offset_;
    std::vector<std::uint32_t>  hiz_mip_w_;
    std::vector<std::uint32_t>  hiz_mip_h_;
    Eigen::Matrix4f             hiz_vp_           = Eigen::Matrix4f::Identity();
    bool                        hiz_valid_        = false;
    bool                        hiz_enabled_      = false;
    std::uint32_t               hiz_reject_count_ = 0;  // per-frame stat

    // Per-frame trace budget for WGPU_HIZ_TRACE. The render() loop
    // resets it to kHizTracePerFrame at the start of each frame; the
    // parallel cull workers atomically decrement when logging a
    // rejection.
    mutable std::atomic<int> hiz_trace_budget_{0};

    // GL's HiZ default is 256 wide; we match. Height tracks viewport aspect.
    static constexpr std::uint32_t HIZ_BASE_W = 256;

    // ---- Depth + MSAA color attachments -----------------------------------
    //
    // Owned by core because both the main render pass (still VW-side) and
    // the HiZ resolve pass (now core-side) bind these. Reallocated on
    // surface resize via ensureDepthTexture / ensureMsaaColorTexture.
    WGPUTexture     depth_texture_      = nullptr;
    WGPUTextureView depth_view_         = nullptr;
    int             depth_w_            = 0;
    int             depth_h_            = 0;
    WGPUTexture     msaa_color_texture_ = nullptr;
    WGPUTextureView msaa_color_view_    = nullptr;
    int             msaa_w_             = 0;
    int             msaa_h_             = 0;

    // Edge-silhouette pipeline group. Drawn after the main pass; reads
    // the depth/normal attachments to emit dark outlines.
    WGPUShaderModule    edge_shader_module_   = nullptr;
    WGPUBindGroupLayout edge_bgl_             = nullptr;
    WGPUPipelineLayout  edge_pipeline_layout_ = nullptr;
    WGPURenderPipeline  edge_pipeline_        = nullptr;
    WGPUBindGroup       edge_bind_group_      = nullptr;
    bool                edges_enabled_        = true;

    // Pick pass. Reuses pipeline_layout_ — same set of bindings as the
    // main pass since the pick fragment also vertex-pulls instance data.
    WGPURenderPipeline  pick_pipeline_ = nullptr;

    // Pick render targets + readback staging. Single-sample, surface-
    // sized R32UInt for object_id + RGBA16F for the packed world-space
    // normal (the section tool drops perpendicular cuts at the picked
    // pixel). picksInRect grows box_pick_staging_buffer_ on demand for
    // marquee selection.
    WGPUTexture        pick_color_texture_         = nullptr;
    WGPUTextureView    pick_color_view_            = nullptr;
    WGPUTexture        pick_normal_texture_        = nullptr;
    WGPUTextureView    pick_normal_view_           = nullptr;
    WGPUTexture        pick_depth_texture_         = nullptr;
    WGPUTextureView    pick_depth_view_            = nullptr;
    WGPUBuffer         pick_staging_buffer_        = nullptr;
    WGPUBuffer         pick_normal_staging_buffer_ = nullptr;
    int                pick_w_                     = 0;
    int                pick_h_                     = 0;
    WGPUBuffer         box_pick_staging_buffer_    = nullptr;
    std::uint64_t      box_pick_staging_capacity_  = 0;
#if defined(__EMSCRIPTEN__)
    // Async object-pick state (web). Held while the staging map is in flight;
    // pick_async_cb_ fires with object_id when the spontaneous map resolves.
    bool                              pick_async_in_flight_ = false;
    std::function<void(std::uint32_t)> pick_async_cb_;
#endif

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

    // Active world-space section planes (up to kMaxSectionPlanes); packed
    // into the per-frame uniform every render and consumed by the WGSL
    // is_section_clipped fragment gate. The section tool in
    // ViewportWindow mutates this through addSectionPlaneAtSurface /
    // removeSectionPlane (still Qt-bound — they wire into the input
    // path). Reading happens here.
    std::vector<SectionPlane> section_planes_;

    // X-ray mode alpha clamp: when < 1.0 every instance routes through
    // the transparent pass with fragment.a clamped to min(in.color.a, cap).
    // Toggled by ViewportWindow::toggleXray; consumed by cull
    // (transparent-pass classifier) and updateFrameUniforms.
    float xray_alpha_cap_ = 1.0f;

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

    // Monotonic streaming-residency clock. Bumped at the top of
    // driveStreamingLoads; applyStreamedChunk stamps loaded_frame_idx
    // with it for the new-chunk grace period; the LRU evictor reads
    // last_visible_frame_idx against it. Lifetime matches models_gpu_
    // (resets only at shutdown).
    std::uint64_t streaming_frame_idx_ = 0;

    // Per-frame streaming activity. Written by driveStreamingLoads,
    // consumed by the benchmark warm-gate (`loads_this_frame == 0 AND
    // worker idle == settled`). `more_pending` is a soft hint — true
    // means residency hasn't converged and the loop should keep ticking.
    int  streaming_loads_this_frame_ = 0;
    bool streaming_more_pending_     = false;

    // Per-frame breakdown counters consumed by the WGPU_STREAM_DEBUG
    // log. All reset at the top of driveStreamingLoads.
    int  streaming_candidates_this_frame_      = 0;
    int  streaming_evictions_lru_this_frame_   = 0;
    int  streaming_evictions_pri_this_frame_   = 0;
    int  streaming_drained_this_frame_         = 0;
    int  streaming_blocked_oom_this_frame_     = 0;
    bool streaming_debug_                      = false;  // WGPU_STREAM_DEBUG=1

    // Click-and-track diagnostic. Set by the pick handler when an
    // object is selected; driveStreamingLoads dumps priority + pool
    // state every time that chunk transitions resident→evicted so
    // we can pinpoint WHY a piece of geometry disappeared.
    std::uint32_t tracked_object_id_  = 0;
    std::uint32_t tracked_chunk_mid_  = 0;
    std::size_t   tracked_chunk_idx_  = SIZE_MAX;
    bool          tracked_was_resident_ = false;

    // When non-empty, a screenshot capture is pending and the streaming
    // loader switches to the synchronous-fetch fallback so the
    // first-frame capture isn't an empty buffer. Cleared after capture
    // completes.
    std::string pending_screenshot_path_;

    // Bonsai direct-load staging map. uploadMeshChunk +
    // uploadInstanceChunk append into entries keyed by model_id; the
    // finalizeModel call moves the entry out, hands it to
    // applyCachedModel, and uploads the chunk slices synchronously.
    std::unordered_map<std::uint32_t, std::unique_ptr<SidecarData>>
        pending_direct_loads_;

    // ---- Render-loop state (#84-x) ---------------------------------------

    // Contribution-cull thresholds. min_pixel_radius_ is the still-frame
    // floor; motion_min_pixel_radius_ kicks in during orbit/pan/zoom to
    // drop more sub-pixel work. lod1_pixel_threshold_ chooses LOD1 over
    // LOD0 when an instance projects below that radius.
    float min_pixel_radius_        = 3.0f;
    float motion_min_pixel_radius_ = 15.0f;
    float lod1_pixel_threshold_    = 30.0f;
    // WGPU_CULL_THREADS=0 forces sequential cull (one model after another)
    // for parallel-vs-serial benchmarking. Default ON.
    bool  cull_threads_enabled_    = true;

    // Per-frame stats latched by render() for FrameStats emission +
    // the interactive heartbeat / bench per-frame line.
    std::uint32_t last_visible_objects_   = 0;
    std::uint32_t last_visible_triangles_ = 0;
    std::uint32_t last_sub_draws_         = 0;
    double last_cull_ms_                  = 0.0;
    double last_cull_compute_ms_          = 0.0;
    double last_cull_upload_ms_           = 0.0;
    double last_stream_ms_                = 0.0;
    // True when the cull just used motion_min_pixel_radius_ — render()
    // schedules one more frame so the camera-now-stopped state recomputes
    // the cull at the still threshold and previously dropped sub-pixel
    // instances pop back in.
    bool   last_cull_was_motion_          = false;

    // Previous frame's camera state for the motion-vs-still decision.
    float prev_camera_target_[3] = { 0, 0, 0 };
    float prev_camera_distance_  = 0.0f;
    float prev_camera_yaw_deg_   = 0.0f;
    float prev_camera_pitch_deg_ = 0.0f;
    bool  has_prev_camera_       = false;

    // Rolling-average FPS readout (60-frame window). frame_time_ms_sum_
    // tracks the running sum so FrameStats can divide-by-count without
    // re-summing.
    static constexpr int FRAME_TIME_WINDOW = 60;
    double frame_time_ms_window_[FRAME_TIME_WINDOW] = {};
    int    frame_time_ms_count_ = 0;
    int    frame_time_ms_head_  = 0;
    double frame_time_ms_sum_   = 0.0;

    // Benchmark-mode state. Activated by setBenchmarkFrames(n); render()
    // orbits the camera at bench_yaw_speed_ deg/frame for bench_total_
    // frames after a bench_warmup_ settle period, collects per-frame ms,
    // emits a percentile summary, and calls host_->quit().
    int   bench_total_         = 0;
    int   bench_count_         = 0;
    int   bench_warmup_        = 5;
    float bench_yaw_start_     = 0.0f;
    float bench_yaw_speed_     = 0.5f;  // degrees per frame
    std::vector<float> bench_frame_ms_;

    // Cold-load warmup gate counters. The orbit sweep waits until
    // streaming has converged for CONVERGE_FRAMES_REQUIRED consecutive
    // frames before starting the sample collection.
    int  bench_warm_streak_          = 0;
    int  bench_warm_frames_total_    = 0;
    bool bench_warm_done_            = false;

    // Per-frame timing accumulators for the bench summary. Each
    // accumulator is divided by bench_total_ when the run finishes.
    double bench_cull_ms_total_         = 0.0;
    double bench_stream_ms_total_       = 0.0;
    double bench_hiz_readback_ms_total_ = 0.0;

    // Interactive [frame] heartbeat counter. Used to rate-limit the
    // stream-health summary + WGPU_STREAM_DEEP_DEBUG dump.
    int interactive_frame_count_ = 0;

    // Auto-viewAll suppression. Flipped true by the first applyCachedModel
    // (so a fresh scene frames itself) or by any explicit setCamera (so a
    // user/bonsai-side camera write isn't overridden by the next model
    // load). Lives here so applyCachedModel can read + write it.
    bool initial_view_applied_ = false;

    // Tool-refresh callback: fired by applyStreamedChunk when a newly-
    // arrived chunk filled in a mesh-local volume. ViewportWindow wires
    // this to its Volume-tool HUD refresh in the ctor. Null by default
    // (no-op) so headless and non-Qt hosts pay nothing.
    std::function<void()> on_volume_dirty_;

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
