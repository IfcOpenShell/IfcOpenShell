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

#ifndef WGPUVIEWPORTWINDOW_H
#define WGPUVIEWPORTWINDOW_H

#include <QWindow>
#include <QColor>
#include <QElapsedTimer>
#include <QMatrix4x4>
#include <QPoint>
#include <QSet>
#include <QString>
#include <QTimer>

#include <webgpu/webgpu.h>

#include <Eigen/Dense>

#include <atomic>
#include <cstdint>
#include <deque>
#include <memory>
#include <unordered_map>
#include <unordered_set>

#include "SidecarCache.h"
#include "BufferPool.h"
#include "InstanceCompose.h"
#include "ModelGpuData.h"
#include "OverlayRenderer.h"
#include "SelectionState.h"
#include "StreamingThread.h"
#include "ViewportCore.h"
#include "ViewportHost.h"
#include "VisibilityState.h"

// Stage-2 wgpu viewport: opens a native QWindow, brings up a wgpu instance/
// adapter/device, configures a surface against the platform-native window
// handle, and clears to background_color_ on every UpdateRequest. Models
// loaded from `.ifcview` sidecars are uploaded as wgpu buffers (no draw
// path yet — that's stage 3).
//
// Mirrors the lifecycle shape of the GL ViewportWindow so subsequent stages
// can grow this into a full IFC renderer without restructuring the host.
//
// Also implements ViewportHost: as the Path-A refactor moves rendering
// state out into ViewportCore, this class plays the embedder role
// (provides the wgpu surface, schedules frames, forwards notifications
// to Q_SIGNALS). The web target's host is the analog on the Emscripten
// side. Today most state still lives here; the override implementations
// at the bottom of the class are the bridge for whatever has already
// moved.
class ViewportWindow : public QWindow, public ViewportHost {
    Q_OBJECT
public:
    explicit ViewportWindow(QWindow* parent = nullptr);
    ~ViewportWindow();

    // --- ViewportHost ----------------------------------------------------
    //
    // Implementations live in ViewportWindow.cpp alongside the
    // platform-specific surface code so the Qt + native window-handle
    // bits stay co-located. Notification overrides (onObjectPicked
    // etc.) forward to the existing Q_SIGNALS so bonsai-side consumers
    // see no change.
    WGPUSurface createSurface(WGPUInstance instance) override;
    void  framebufferSize(int& width_px, int& height_px) const override;
    float dpr() const override;
    void  requestFrame() override;
    void  quit() override;
    void  onObjectPicked(uint32_t object_id) override;
    void  onSurfacePickedInTool(int x_px, int y_px, int modifiers) override;
    void  onToolModeChanged(int tool_mode) override;
    void  onToolBackspacePressed() override;

    void setBackgroundColor(const QColor& color);

    // Queue a sidecar path to be loaded after wgpu init completes. Safe to
    // call before the window is exposed. The path is resolved against the
    // working directory and read via SidecarCache::readSidecar (which
    // normalises stem → .ifcview).
    void queueLoadSidecar(const QString& path);

    // Synchronous metadata load + GPU upload. Requires wgpu init to have
    // completed (i.e. the window has been exposed at least once). Returns
    // the assigned model_id, or 0 on failure. Reads metadata only (mesh
    // dict + instance dict + georef); per-chunk vertex / index bytes are
    // read on demand by the per-frame loader as chunks become visible.
    uint32_t loadSidecar(const QString& path);

    // Allocates per-chunk small buffers and the model-shared mesh /
    // instance storage upfront, but leaves each chunk's pool ranges
    // unclaimed and is_resident=false. The per-frame loader
    // (driveStreamingLoads) sub-allocates the chunk's vertex + index
    // ranges from pool_ on demand as cull flags them visible.
    void applyCachedModel(uint32_t model_id,
                          struct StreamingSidecar metadata);

    // Direct-IFC ingestion (mirrors GL ViewportWindow). The host (typically
    // a GeometryStreamer running on a worker) calls uploadMeshChunk +
    // uploadInstanceChunk once per representation / placement as the IFC
    // triangulates; finalizeModel commits when the iterator finishes.
    // Staged in CPU memory; finalizeModel runs the chunk planner over the
    // staged data, allocates pool slices, and uploads — same render path
    // as a sidecar load. Bytes are gathered from memory (no disk I/O), so
    // every chunk lands `is_resident=true` immediately. The streamer's
    // model_id is passed through unchanged; the viewport's globally-unique
    // object_id rebasing happens at finalize time.
    void uploadMeshChunk(const struct MeshChunk& chunk);
    void uploadInstanceChunk(const struct InstanceChunk& chunk);
    void finalizeModel(uint32_t model_id);

    void removeModel(uint32_t model_id);
    void resetScene();

    // Model-level visibility. Mirrors the GL ViewportWindow API — flips
    // ModelGpuData::hidden, which every render/pick/cull pass already
    // consults. requestUpdate() so the change is visible immediately.
    void hideModel(uint32_t model_id);
    void showModel(uint32_t model_id);

    // Federation pipeline: composed instance transform =
    //   FederatedFalseOrigin · ModelTransformation · CoordinateOperation
    //                                              · placement_transformation
    // Wgpu does not yet recompose instances against these matrices —
    // composeInstanceFromPlacement is still placement-only — so the
    // setters store the input and post requestUpdate(). Bonsai-side
    // integration compiles against these signatures; visual georef parity
    // arrives with the recompose+SSBO-rewrite work tracked separately.
    void setFederatedFalseOrigin(const Eigen::Matrix4d& matrix_meters);
    void setModelCoordinateOperation(uint32_t model_id,
                                     const Eigen::Matrix4d& matrix_meters);
    void setModelTransformation(uint32_t model_id,
                                const Eigen::Matrix4d& matrix_meters);

    size_t modelCount() const { return models_gpu_.size(); }

    // Frame the union of all loaded models' world AABBs. No-op on empty
    // scenes. Called automatically after the first model loads (unless
    // setCamera was already invoked); clients can re-invoke to re-frame.
    void viewAll();

    // Explicit camera state, mirroring the GL ViewportWindow API. Suppresses
    // the auto-viewAll on first load so a script-driven camera survives
    // model loading. Parameters match the GL --camera tx,ty,tz,dist,yaw,pitch
    // order so a pasted camera string lands the same view in both backends.
    void setCamera(float tx, float ty, float tz,
                   float dist, float yaw_deg, float pitch_deg);

    // GL-parity camera helpers. setStandardView snaps to an axis-aligned
    // angle without re-framing (used by X/Y/Z keys). focusOnSelectedObject
    // frames the union AABB of the current selection. toggleProjection
    // flips perspective <-> orthographic. cameraString formats the current
    // state for a --camera CLI arg.
    void    setStandardView(float yaw_deg, float pitch_deg);
    void    focusOnSelectedObject();
    void    toggleProjection();
    bool    projectionOrtho() const { return projection_ortho_; }
    QString cameraString() const;

    // Snapshot of the orbit camera. Mirrors GL ViewportWindow::CameraState
    // so bonsai's "save view" / "restore view" commands port unchanged.
    struct CameraState {
        QVector3D target;
        float distance;
        float yaw;    // degrees
        float pitch;  // degrees
    };
    CameraState cameraState() const;

    // Tool toggles: flip between NoTool and the named tool. Wrappers
    // around setToolMode so bonsai's verb actions stay terse.
    void toggleAreaTool();
    void toggleLengthTool();
    void toggleVolumeTool();

    // Element-level visibility verbs. The fine-grained per-id mutations
    // go through visibility_; these high-level methods are what bonsai's
    // Commands.cpp calls. Hidden elements are dropped from cull (no draw,
    // no depth, no pick).
    void hideSelectedElements();
    void isolateSelectedElements();
    void showAllElements();
    void invertElementVisibility();

    // Replace the selection with {id} (or clear if id == 0). Used by
    // SessionState mirroring and by project commands that drop selection
    // on model removal. Wrapper around selection_.replace / clear.
    void setSelectedObjectId(uint32_t id);

    // FPS / fly mode. enterFpsMode swaps the orbit camera for a WASD/QE
    // free-fly camera (hotkey: Shift+F). exitFpsMode restores the orbit
    // pivot and reveals the cursor. Mouse-look uses raw deltas (cursor is
    // hidden and recentered each frame).
    void enterFpsMode();
    void exitFpsMode();
    bool fpsMode() const { return fps_mode_; }

private:
    // Common camera math used by render, cull, streaming, and pick. Produces
    // the view matrix and a WebGPU-correct projection (z mapped to [0, 1]).
    // Single helper so projection_ortho_ and the up-vector switch at near-
    // vertical pitch land identically everywhere.
    void buildViewProj(QMatrix4x4& view_out, QMatrix4x4& proj_out) const;
    // Per-frame WASD integration when fps_mode_ is true. Called near the
    // top of render() so the displayed frame already reflects movement.
    void fpsIntegrate();
    // Build the camera AABB for a single object across all loaded models.
    bool computeObjectAabb(uint32_t object_id,
                           float mn[3], float mx[3]) const;
public:
    // QVector3D overload — matches GL ViewportWindow::computeObjectAabb so
    // bonsai's volume readout / focus callers compile unchanged. Just a
    // thin wrapper around the float[3] version.
    bool computeObjectAabb(uint32_t object_id,
                           QVector3D& mn, QVector3D& mx) const;
private:
    // Re-aim the orbit camera so the bounding sphere of [mn, mx] fits.
    void frameAabb(const float mn[3], const float mx[3], float padding);
    // Resolve nav_preset_ env var to orbit/pan bindings.
    void applyNavPreset(const char* name);

    // Project the chunk's world-space AABB through `vp_mat` and return the
    // 2D pixel area covered on screen. This is the streaming loader's
    // chunk-priority metric — extracted from driveStreamingLoads as a
    // member so the click-and-track diagnostic can compare scores.
    float chunkScreenAreaPx(const ModelGpuData::Chunk& c,
                            const QMatrix4x4& vp_mat) const;

public:

    // Queue a one-shot framebuffer capture: the next rendered frame is
    // copied back to host memory and saved to `path` as PNG. If
    // `quit_after` is true, QCoreApplication::quit() is called once the
    // PNG is written. Use this for headless verification and pixel-diff
    // parity testing against the GL backend.
    void captureNextFrameToPng(const QString& path, bool quit_after = true);

    // Benchmark mode: render N timed frames (after a small warmup), yaw-
    // sweeping the camera at 0.5°/frame, then print a stats block on
    // stderr and QCoreApplication::quit(). Mirrors the GL minimal's
    // --benchmark output format so a script can diff them line for line.
    void setBenchmarkFrames(int frames);

protected:
    void exposeEvent(QExposeEvent* event) override;
    void resizeEvent(QResizeEvent* event) override;
    bool event(QEvent* event) override;
    void mousePressEvent(QMouseEvent* event) override;
    void mouseReleaseEvent(QMouseEvent* event) override;
    void mouseMoveEvent(QMouseEvent* event) override;
    void wheelEvent(QWheelEvent* event) override;
    void keyPressEvent(QKeyEvent* event) override;
    void keyReleaseEvent(QKeyEvent* event) override;

private:
    bool initWgpu();
    bool createSurface();
    void configureSurface(int width_px, int height_px);
    void render();
    void shutdown();

    bool  buildPipelines();
    void  buildModelBindGroup(ModelGpuData& m);
    void  buildChunkBindGroup(ModelGpuData& m, size_t chunk_idx);
    // Streaming: read the chunk's vertex + index bytes from disk,
    // sub-allocate ranges in pool_, queueWriteBuffer them in, build the
    // chunk's bind group, flip is_resident=true. Returns true on success;
    // false if either the disk read or a pool alloc fails (caller is
    // expected to have already evicted enough). No-op (returns true)
    // when already resident.
    bool  loadChunkBytesAndUploadGpu(ModelGpuData& m, size_t chunk_idx);
    // Pool-allocate + queueWriteBuffer + build bind group for a chunk
    // whose vbytes/idx have already been read (by either the worker
    // thread's drained result or the sync fallback). Returns false on
    // pool OOM. Toggles is_resident=true / is_loading=false on success.
    bool  applyStreamedChunk(ModelGpuData& m, size_t chunk_idx,
                             const std::vector<uint8_t>& vbytes,
                             const std::vector<uint32_t>& idx);
    // Release a resident chunk's pool ranges + bind group; flip
    // is_resident=false. The chunk's CPU metadata (offsets, AABB,
    // visible-draw scratch) is retained so a subsequent
    // loadChunkBytesAndUploadGpu can bring it back without re-planning.
    void  unloadChunk(ModelGpuData& m, size_t chunk_idx);
    // Called from render() after cull: find non-resident chunks with
    // current visible draw counts > 0 and bring them resident. When the
    // pool is full, evicts LRU non-visible chunks first, then falls back
    // to evicting the farthest-from-camera visible chunks if a closer
    // candidate needs the space. Triggers requestUpdate() if more remain.
    void  driveStreamingLoads();

    // Discover the largest single buffer wgpu will give us by descending
    // from the device's limits.maxBufferSize through OOM error scopes.
    // Allocates pool_ at the discovered size. Returns false only when
    // even a tiny pool can't be created (i.e. the device is unusable).
    bool  probeAndCreatePool();
    void  ensureDepthTexture(int w, int h);
    void  releaseDepthTexture();
    void  ensureMsaaColorTexture(int w, int h);
    void  releaseMsaaColorTexture();

    bool  buildHizPipeline();
    bool  buildEdgePipeline();
    void  encodeEdgePass(WGPUCommandEncoder enc, WGPUTextureView surface_view);
    // Show/hide the pivot indicator. hide_after_ms > 0 starts the
    // single-shot auto-hide timer used by the wheel-zoom afterglow;
    // drag callers pass 0 and toggle manually on press/release. The
    // actual gizmo rendering lives in OverlayRenderer — this just
    // manages the UI-side visibility timer.
    void  setPivotIndicatorVisible(bool visible, int hide_after_ms = 0);
    void  releaseEdgeResources();

    bool  buildPickPipeline();

    // Make sure selection_flags_buffer_ is large enough to address every
    // object_id in next_object_id_. Recreates (and rebuilds frame_bind_group_)
    // if it grew. Safe to call every frame; idempotent when already sized.
    void  ensureSelectionFlagsBuffer();
    // Repack the CPU selection into bit-flags and wgpuQueueWriteBuffer to
    // the GPU. Called from render() when selection_.dirty().
    void  uploadSelectionFlagsIfDirty();
    void  ensurePickAttachments(int w, int h);
    void  releasePickResources();
    // Synchronous pick: encodes a one-shot R32UInt render of the current
    // visible_draws against the click pixel, copies the single texel back,
    // waits, and returns the object_id (0 if nothing was hit). Call from
    // the main thread between renders. When `normal_out` is non-null, the
    // pick pass's RGBA16F normal MRT is also sampled at the same pixel
    // (decoded from ×0.5+0.5 packing) so the section tool can drop
    // perpendicular cuts.
    uint32_t pickObjectAt(int x_pixels, int y_pixels,
                          QVector3D* normal_out = nullptr);
    // Pick + ray-cast — returns the object's id, the world-space point
    // where the pick-pixel pillar enters that instance's AABB, and a
    // camera-facing normal. Returns false on a background miss. We do
    // CPU ray-AABB rather than reading per-pixel depth because WebGPU's
    // copyTextureToBuffer for Depth32Float requires copying the whole
    // mip extent — wasteful per click — and ray-vs-AABB lands close
    // enough to the click for the section tool's "drop a plane here" UX.
    bool pickSurfaceAt(int x_pixels, int y_pixels,
                       uint32_t& object_id_out,
                       QVector3D& world_pos_out,
                       QVector3D& world_normal_out,
                       float* aabb_radius_out = nullptr);
    // Rectangle pick: render the pick pass, copy the rect region of the
    // R32UInt color attachment, and return every unique non-zero
    // object_id covered. `rect` is in physical pixels (post-DPR), already
    // clipped to the framebuffer by the caller.
    std::vector<uint32_t> picksInRect(int x, int y, int w, int h);

public:
    // Section-cutting tool. Mirrors the GL ViewportWindow API:
    //   K           toggle (sectionToolActive / toggleSectionTool)
    //   Shift+K     clearSectionPlanes
    //   click       addSectionPlaneAtSurface (when tool active)
    //   Del/Backspace removeSectionPlane (most recent, when tool active)
    //   Esc         deactivate tool
    bool  sectionToolActive() const { return section_tool_active_; }
    void  toggleSectionTool();
    bool  addSectionPlaneAtSurface(const QVector3D& point,
                                   const QVector3D& normal,
                                   float visual_radius = 0.0f);
    void  removeSectionPlane(int index);
    void  clearSectionPlanes();
    int   sectionPlaneCount() const { return int(section_planes_.size()); }
    // Overlay primitives. Mirror GL ViewportWindow so the Measurement +
    // dimension tools can target either backend through one API.
    // Empty inputs clears the corresponding set.
    void  setOverlayLines(const std::vector<OverlayRenderer::LineGroup>& groups);
    void  setOverlayPoints(const std::vector<float>& world_xyz,
                           float r, float g, float b, float a,
                           float pixel_size,
                           float stroke_r, float stroke_g,
                           float stroke_b, float stroke_a,
                           float stroke_extra);
    void  setOverlayLabels(const std::vector<OverlayRenderer::Label>& labels);
    void  setHudText(const QString& text);
    // Translucent world-space triangle overlay (Area-tool patch shading).
    // Empty list disables; color is RGBA in [0, 1].
    void  setHighlightTriangles(const std::vector<float>& world_xyz,
                                float r, float g, float b, float a);

    // CPU mesh shadow: positions (3 floats/vert, mesh-local) + indices
    // (LOD0). Populated at applyCachedModel / applyStreamedChunk —
    // returns false if the mesh isn't loaded yet (streaming) or the
    // (model_id, mesh_id) pair doesn't resolve. Matches the GL
    // ViewportWindow::MeshTriangles + readbackMeshTriangles shape so
    // the measure tools port verbatim.
    using MeshTriangles = ModelGpuData::MeshTriangles;
    bool  readbackMeshTriangles(uint32_t model_id, uint32_t mesh_id,
                                MeshTriangles& out) const;

    // Pure CPU lookup: object_id → owning model + mesh + raw placement
    // matrix (column-major, pre-CoordinateOperation / FederatedFalseOrigin
    // / ModelTransformation). Mirrors GL ViewportWindow::InstanceLookup
    // so Measurement.cpp ports unchanged. The canonical struct lives in
    // InstanceCompose so the lookup can be unit-tested without Qt.
    using InstanceLookup = InstanceCompose::InstanceLookup;
    bool findInstance(uint32_t object_id, InstanceLookup& out) const;

    // A point that actually lies on the model's first instance — the
    // first instance's mesh AABB centre transformed by that instance's
    // placement, in metres, pre-CoordinateOperation. Lookup only — the
    // viewport already keeps the CPU-side MeshInfo + InstanceCpu around
    // for picking / measurement; the federation false-origin guess
    // (ViewportView::guessFederatedFalseOriginFromFirstModel) consumes
    // this lazily on modelGeometryReady. Returns false when the model
    // is unknown or has no instances.
    bool firstGeometryPointWorldM(uint32_t model_id,
                                  Eigen::Vector3d& out) const;

    // Re-frame the camera onto the federated false origin in post-shift
    // space. After ViewportView's first-model false-origin guess sets a
    // federation origin and the resulting recomposeAndUploadModel runs,
    // the federation false origin (in world coords) maps to (0,0,0) in
    // render coords — so we target (0,0,0) and the first model's
    // anchor point sits dead-centre.
    //
    // Distance comes from the model's post-shift AABB diagonal with the
    // same padding math as viewAll(), but clamped to `max_distance_m`
    // so a model with one crazy-coord outlier vertex (16 km AABB
    // diagonal because of one bad triangle) can't pull the camera so
    // far back that the bulk of the geometry becomes a single pixel.
    // Yaw/pitch unchanged — preserves the user's current look direction.
    //
    // Unlike viewAll() this *never* iterates all loaded models — it
    // frames around the specific model the guess fired for, ignoring
    // models with bad coordinates elsewhere in the session.
    void frameOnFederatedOrigin(uint32_t model_id, float max_distance_m);

    // Selection accessor. Exposed for callers (bonsai's volume readout)
    // that need to read selectionIds() / activeObjectId(). Mutation goes
    // through the existing setSelection / pick paths.
    SelectionState&       selection()       { return selection_; }
    const SelectionState& selection() const { return selection_; }

    // Pick + resolve to mesh-local space. Runs pickSurfaceAt to get the
    // world-space hit, then inverts the instance's composed transform
    // to express the hit in the mesh's own coordinates — what
    // readbackMeshTriangles returns. Returns false on miss.
    struct MeshLocalPick {
        uint32_t object_id = 0;
        uint32_t model_id  = 0;
        uint32_t mesh_id   = 0;
        float    mesh_local [3] = {0, 0, 0};
        float    world_pos  [3] = {0, 0, 0};
        float    world_normal[3] = {0, 0, 0};
        float    composed_transform[16] = {1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1};
    };
    bool pickMeshLocalAt(int x, int y, MeshLocalPick& out);

    // Resolve a mesh-local point to a (placement-applied) global frame.
    // Matches GL ViewportWindow::meshLocalToGlobal's shape so the Length
    // tool's ENH readout ports unchanged. The wgpu viewer doesn't carry
    // per-model CoordinateOperation yet, so this currently outputs
    // placement_transformation · mesh_local (i.e. the IFC's own world
    // coords pre-georeferencing); ENH and IFC-world coincide for the
    // non-federated case the minimal viewer handles today.
    bool meshLocalToGlobal(uint32_t object_id, const float mesh_local[3],
                           double global_out[3]) const;

    // CPU world-space raycast. Brute-force: per-instance world-AABB
    // reject, then ray-into-mesh-local + Möller-Trumbore against the
    // CPU mesh shadow. `dir` must be a unit vector — distance is the
    // ray's t parameter, which equals world distance only at |dir|=1.
    // Used by the Length tool's 1-point laser-measure overlay to find
    // the ceiling/floor counterpart of a horizontal-surface click.
    struct RaycastHit {
        uint32_t object_id      = 0;
        float    distance       = 0.0f;
        float    world_pos[3]   = {0, 0, 0};
        float    world_normal[3]= {0, 0, 0};
    };
    bool raycast(const float origin[3], const float dir[3], RaycastHit& out) const;

    // Measurement tools. Mirrors GL ViewportWindow::ToolMode. Volume is
    // selection-driven (LMB / marquee). Area is click-to-accumulate:
    // each LMB picks a triangle and either adds or removes its
    // coplanar patch via BFS over shared edges; Alt+LMB skips the BFS.
    // V/A/L toggle, Esc exits. Length consumes Backspace too for
    // remove-last-point semantics.
    // NoTool (not None) because X11/X.h #define's None as 0L; including
    // it transitively via Qt's xcb back-end breaks any enum named None.
    enum class ToolMode { NoTool, Volume, Area, Length };
    Q_ENUM(ToolMode)
    ToolMode toolMode() const { return tool_mode_; }
    void     setToolMode(ToolMode m);

    // Per-frame snapshot of cull / scene stats, emitted via
    // frameStatsUpdated at the end of each render(). Mirrors GL
    // ViewportWindow::FrameStats so bonsai's status bar binding ports
    // unchanged. gl_draw_calls is the wgpu draw-call count (named for
    // continuity with the GL field bonsai's status format string uses).
    struct FrameStats {
        float    fps;
        float    frame_time_ms;
        uint32_t total_objects;
        uint32_t visible_objects;
        uint32_t total_triangles;
        uint32_t visible_triangles;
        uint32_t unique_meshes;
        uint32_t gl_draw_calls;        // wgpu draw-call count; name kept for bonsai parity
        uint32_t indirect_sub_draws;   // sub-draws packed into the chunk-indirect lists
    };

signals:
    // Selection moved by a pick / marquee. Emitted with the active id
    // (0 = miss). Bonsai mirrors this into SessionState.
    void objectPicked(uint32_t object_id);
    void frameStatsUpdated(const ViewportWindow::FrameStats& stats);
    // Emitted instead of objectPicked when an Area / Length tool is
    // active. The host branches on toolMode() and calls
    // pickMeshLocalAt(x, y, ...) for hit details. Coordinates are in
    // physical pixels (post-DPR).
    void surfacePickedInTool(int x, int y, int modifiers);
    // Emitted whenever the active tool changes (incl. on→off).
    void toolModeChanged(ViewportWindow::ToolMode mode);
    // Backspace/Delete pressed while a tool is active. Length tool's
    // remove-last-point; other tools may ignore.
    void toolBackspacePressed();

public:

    // Sum of mesh-local volumes (m³) of every instance whose object_id
    // is in `object_ids`. Each instance is scaled by |det(placement_3x3)|
    // to pick up mapped-item scale/mirror; signed-tetrahedra absolute
    // value means winding is ignored. Volumes are precomputed at
    // applyCachedModel — this call is just lookups + multiplies.
    double volumeOfObjects(const std::vector<uint32_t>& object_ids) const;
private:
    // Per-object variant. Used by the Volume tool to drive both the
    // total HUD and the per-object overlay labels at AABB centres.
    std::vector<std::pair<uint32_t, double>>
        volumesPerObject(const std::vector<uint32_t>& object_ids) const;

    void  ensureHizTextures(int viewport_w, int viewport_h);
    void  releaseHizResources();
    // Resolves the just-rendered MSAA depth into the small single-sample
    // HiZ texture and copies it to whichever staging slot is currently
    // idle. Returns the slot index used, or -1 if both slots are still
    // in flight (resolve is skipped this frame — fine, we already have
    // a recent pyramid). Encoded onto `enc` so it ships in the same
    // command buffer as the main draw.
    int   encodeHizResolve(WGPUCommandEncoder enc);
    // Issues a non-blocking mapAsync on `slot` after submit, so the
    // callback can fire whenever the GPU has actually finished writing.
    void  startHizMap(int slot, const QMatrix4x4& vp_used);
    // Drains pending mapAsync callbacks (via processEvents — does NOT
    // block on GPU work). For any slot that just signalled Mapped, reads
    // it, unmaps it, max-reduces the mip pyramid, and updates hiz_vp_.
    void  drainHizReadbacks();
    // Project AABB through hiz_vp_ and test against the pyramid. False
    // (keep) if HiZ isn't valid yet, AABB straddles the near plane, or
    // any projection is unreliable. True (cull) when AABB is provably
    // behind every relevant pyramid cell.
    bool  aabbOccludedByHiz(const float mn[3], const float mx[3]) const;
    void  updateFrameUniforms();
    void  flushPendingSidecarQueue();
    bool  computeSceneAabb(float mn[3], float mx[3]) const;

    // Cull `m`'s instances against the supplied frustum planes (world-space,
    // ax+by+cz+d >= 0 means inside), bucket survivors by (mesh_id, lod), and
    // write the flat visible-index list into m.visible_buffer via
    // wgpuQueueWriteBuffer. After return, m.mesh_draws is the per-mesh,
    // per-LOD draw schedule for the frame.
    //
    // `eye` and `forward` (forward = unit (target - eye)) are used to compute
    // each instance's view-space depth for the projected-radius formula.
    // `focal_px` = viewport_height / (2 * tan(fov_y / 2)).
    //
    // Two pixel-radius thresholds:
    //   `min_radius_px`  — instances projected below this are dropped
    //                       entirely (contribution culling).
    //   `lod1_threshold_px` — survivors projected below this get the mesh's
    //                       LOD1 index slice when one was baked.
    // min_radius_px == 0 disables contribution culling.
    // CPU-only phase of cull: produces m.visible_draws_scratch /
    // prefix_sums_scratch and sets total_visible_draws / total_visible_
    // vertices. Touches no wgpu state, so this can run on a worker thread
    // (multiple models culled in parallel). Returns the number of HiZ
    // rejections accumulated (caller adds to the per-frame stat).
    // right/up are world-space camera basis vectors (orthonormal with
    // forward). Used by the streaming priority accumulator to project
    // each instance's world AABB to a screen-space rectangle — far
    // tighter than a bounding-sphere projection for BIM geometry, which
    // is overwhelmingly thin-in-one-axis (pipes, columns, slabs,
    // windows). Sphere projection is kept for contribution / LOD picks
    // because conservative-over is the right failure mode there.
    uint32_t cullModelCpuCompute(ModelGpuData& m,
                                 const float planes[6][4],
                                 const float eye[3],
                                 const float forward[3],
                                 const float right[3],
                                 const float up[3],
                                 float focal_px,
                                 float min_radius_px,
                                 float lod1_threshold_px,
                                 bool  hiz_enabled) const;
    // Upload phase: wgpuQueueWriteBuffer for visible_draws / prefix_sums /
    // per-model uniform. Main-thread only (wgpu queue ops are not all
    // thread-safe).
    void     cullModelCpuUpload(ModelGpuData& m);

    // Compose one instance's `transform` (float[16] column-major) from
    //   FederatedFalseOrigin · ModelTransformation · CoordinateOperation
    //                                              · placement_transformation
    // and recompute its world AABB from the mesh's local AABB. Maths runs
    // in double; the cast to float happens last so large IFC placements
    // get cancelled by the federation false origin before precision is
    // narrowed. Mirrors GL ViewportWindow::composeInstanceFromPlacement.
    void composeInstanceFromPlacement(InstanceCpu& inst,
                                      const ModelGpuData& m) const;

    // Walk every instance of `model_id`, recompose its transform from the
    // current federation matrices, refresh per-chunk world AABBs, and
    // re-upload InstanceGpu[] into m.instance_storage. No-op if the model
    // is unknown, has no instances, or wgpu init hasn't completed.
    void recomposeAndUploadModel(uint32_t model_id);

    bool wgpu_initialized_ = false;
    bool surface_configured_ = false;
    int  configured_w_ = 0;
    int  configured_h_ = 0;

    WGPUInstance      instance_       = nullptr;
    WGPUAdapter       adapter_        = nullptr;
    WGPUDevice        device_         = nullptr;
    WGPUQueue         queue_          = nullptr;
    WGPUSurface       surface_        = nullptr;
    WGPUTextureFormat surface_format_ = WGPUTextureFormat_Undefined;

    // Render pipeline + bind group layouts (built once after init).
    WGPUShaderModule       main_shader_module_ = nullptr;
    WGPUBindGroupLayout    frame_bgl_          = nullptr;  // group 0
    WGPUBindGroupLayout    model_bgl_          = nullptr;  // group 1
    WGPUPipelineLayout     pipeline_layout_    = nullptr;
    WGPURenderPipeline     main_pipeline_      = nullptr;
    // Transparent-pass pipeline. Same shader / layout / vertex-pulling as
    // main_pipeline_; differs only in depthWriteEnabled=False and a
    // SrcAlpha / OneMinusSrcAlpha blend on the color target. render()
    // does the opaque pass with main_pipeline_ first, then this one
    // over the transparent partition of each chunk's visible_draws.
    WGPURenderPipeline     main_pipeline_transparent_ = nullptr;

    // Per-frame uniform (view-proj + lighting), bound at group 0.
    WGPUBuffer    frame_uniform_buffer_ = nullptr;
    WGPUBindGroup frame_bind_group_     = nullptr;

    // Selection flags storage buffer at group=0 binding=1. u32-per-object_id,
    // bit 0 = selected, bit 1 = active. Sized to next_object_id_ rounded up;
    // grows when a load pushes past the current capacity. Bound in the
    // frame bind group because object_ids are globally unique across models.
    WGPUBuffer         selection_flags_buffer_   = nullptr;
    uint32_t           selection_flags_capacity_ = 0;  // number of u32 entries
    SelectionState selection_;
    std::vector<uint32_t> selection_flags_scratch_;

    // Per-element visibility. Consulted in cullModelCpuCompute to drop
    // hidden instances before they're added to visible_draws — keeps
    // hidden geometry out of cost on every axis (no draw, no depth, no
    // pick). Mutated on the main thread between renders; cull workers
    // read concurrently which is safe as long as no concurrent writes.
    VisibilityState visibility_;

    // Depth attachment (4× MSAA), recreated on surface resize.
    WGPUTexture     depth_texture_ = nullptr;
    WGPUTextureView depth_view_    = nullptr;
    int             depth_w_       = 0;
    int             depth_h_       = 0;

    // 4× MSAA color target. Surface format-matched, recreated on resize.
    // The render pass writes here, then resolves into the surface texture.
    WGPUTexture     msaa_color_texture_ = nullptr;
    WGPUTextureView msaa_color_view_    = nullptr;
    int             msaa_w_             = 0;
    int             msaa_h_             = 0;
    static constexpr uint32_t SAMPLE_COUNT = 4;

    // HiZ occlusion culling. After each frame's main render pass we
    // downsample MSAA depth into a small single-sample Depth32Float texture
    // (hiz_resolve_texture_), copy it into a CPU-mappable staging buffer,
    // wait for the map via processEvents, and max-reduce a mip pyramid on
    // CPU. The cull pass in the *next* frame projects each instance's AABB
    // through hiz_vp_ (the VP used to fill the pyramid) and rejects when
    // the AABB's nearest projected z is behind the pyramid's coverage.
    //
    // GL's HiZ default is 256 wide; we match. Height tracks viewport aspect.
    static constexpr uint32_t HIZ_BASE_W = 256;

    WGPUShaderModule    hiz_shader_module_   = nullptr;
    WGPUBindGroupLayout hiz_bgl_             = nullptr;
    WGPUPipelineLayout  hiz_pipeline_layout_ = nullptr;
    WGPURenderPipeline  hiz_pipeline_        = nullptr;
    WGPUBuffer          hiz_uniform_buffer_  = nullptr;
    WGPUBindGroup       hiz_bind_group_      = nullptr;

    WGPUTexture     hiz_resolve_texture_ = nullptr;
    WGPUTextureView hiz_resolve_view_    = nullptr;
    uint32_t        hiz_resolve_w_       = 0;
    uint32_t        hiz_resolve_h_       = 0;
    uint32_t        hiz_padded_bpr_      = 0;  // bytes per row in the staging buffer

    // Ping-pong async readback. Frame N submits a copy into slot
    // hiz_write_idx_ and calls mapAsync (non-blocking) on that slot. Frame
    // N+K (K ≥ 1) calls processEvents to drain callbacks; whichever slot
    // signalled completion is mapped, read into hiz_pyramid_, and unmapped
    // — making the pyramid 1+ frames stale, which is fine ("slightly-stale
    // depth" pattern the GL backend already documents). Two slots overlap
    // GPU write with CPU read; we never block on the readback.
    // Edge silhouette post-process (stage 9). Samples the MSAA depth
    // texture in a fullscreen pass, computes a depth Laplacian, blends
    // dark lines into the resolved surface colour. Matches GL's
    // renderEdgePass() visually.
    WGPUShaderModule    edge_shader_module_   = nullptr;
    WGPUBindGroupLayout edge_bgl_             = nullptr;
    WGPUPipelineLayout  edge_pipeline_layout_ = nullptr;
    WGPURenderPipeline  edge_pipeline_        = nullptr;
    WGPUBindGroup       edge_bind_group_      = nullptr;
    bool                edges_enabled_        = true;

    // Pivot visibility state — the gizmo itself lives in overlays_.
    // The timer auto-hides the pivot after a wheel-zoom afterglow.
    bool                pivot_indicator_visible_    = false;
    QTimer*             pivot_indicator_hide_timer_ = nullptr;

    // All viewport overlays (axis indicator, section gizmos, marquee
    // rect) — pipelines + shaders + buffers + encoders. The viewport
    // builds a OverlayFrame each frame and asks the renderer to
    // encode each overlay; see OverlayRenderer.h.
    OverlayRenderer overlays_;

    // Active measurement tool. setToolMode() / setSelection mutations
    // both funnel into updateVolumeReadout() which pushes the HUD +
    // per-object labels into overlays_.
    ToolMode tool_mode_ = ToolMode::NoTool;
    // Recompute the volume HUD + per-object labels from the current
    // selection. No-op unless tool_mode_ == Volume; on the first call
    // after entering Volume mode this primes the overlay.
    void updateVolumeReadout();

    // Area tool state lives in AreaMeasurement (header below). The
    // viewport owns it for the session and routes LMB picks in Area
    // mode through onAreaPick.
    std::unique_ptr<class AreaMeasurement> area_tool_;
    void onAreaPick(int x_phys, int y_phys, bool alt);
    void updateAreaHud();

    // Length tool state lives in LengthMeasurement. Same lifecycle
    // pattern: lazily constructed on first L press, cleared on tool
    // exit, click handler routes LMB through onLengthPick + Backspace
    // through onLengthBackspace.
    std::unique_ptr<class LengthMeasurement> length_tool_;
    void onLengthPick(int x_phys, int y_phys, bool alt);
    void onLengthBackspace();

    // Pick pass (stage 4). Single-sample R32UInt target + depth, vertex-
    // pulled from the same visible_draws / instances buffers as the main
    // pass — pick fragment outputs the instance's object_id. The pick
    // pipeline reuses pipeline_layout_ because it needs the same set of
    // bindings (frame uniform at group=0, per-model storages at group=1).
    WGPURenderPipeline pick_pipeline_       = nullptr;
    WGPUTexture        pick_color_texture_  = nullptr;
    WGPUTextureView    pick_color_view_     = nullptr;
    // Second pick MRT: RGBA16F packed world-space normal. Sampled by
    // pickSurfaceAt so section cuts are perpendicular to the actual
    // picked triangle (rather than the AABB face that contains it).
    WGPUTexture        pick_normal_texture_         = nullptr;
    WGPUTextureView    pick_normal_view_            = nullptr;
    WGPUBuffer         pick_normal_staging_buffer_  = nullptr;  // 256 B (one RGBA16F texel padded)
    WGPUTexture        pick_depth_texture_  = nullptr;
    WGPUTextureView    pick_depth_view_     = nullptr;
    WGPUBuffer         pick_staging_buffer_ = nullptr;  // 256 B (single texel + bytes-per-row pad)
    int                pick_w_              = 0;
    int                pick_h_              = 0;

    // Section-cutting state. SectionPlane lives in OverlayRenderer.h
    // because the visualiser reads it; the viewport owns the authoritative
    // vector that the section tool mutates.
    std::vector<SectionPlane> section_planes_;
    bool                          section_tool_active_  = false;

    // X-ray mode. Default 1.0 = no effect (fragment shader clamps
    // alpha = min(in.color.a, xray_alpha_cap_), which returns in.color.a
    // when the cap is 1). Alt+X drops it to 0.3 to translucent the whole
    // scene; pressing again restores 1.0. When < 1.0, the cull
    // classifier also routes every instance into the transparent pass
    // so the blend stage actually fires (an opaque-pass fragment with
    // capped alpha would still overwrite the back buffer).
    float                         xray_alpha_cap_       = 1.0f;

    // Marquee box-select. Armed on LMB press (when no other tool consumes
    // the click), becomes active after the cursor moves past
    // kBoxSelectThresholdPx — until then a release still routes through
    // the single-pick path. Press-time modifiers decide the set op at
    // release: plain → replace, Shift → add, Ctrl → remove.
    bool                       box_select_armed_      = false;
    bool                       box_select_active_     = false;
    QPoint                     box_select_start_pos_;     // logical px
    QPoint                     box_select_current_pos_;   // logical px
    Qt::KeyboardModifiers      box_select_press_mods_ = Qt::NoModifier;
    static constexpr int       kBoxSelectThresholdPx  = 5;
    // R32UInt staging for the rect-pick. Sized to the largest rect we've
    // seen so far (padded to 256 bpr), regrown if a bigger rect arrives.
    WGPUBuffer                 box_pick_staging_buffer_   = nullptr;
    uint64_t                   box_pick_staging_capacity_ = 0;
    // Drag-to-move state for the arrow gizmo. While `section_drag_active_`
    // is true, mouseMoveEvent calls updateSectionDrag instead of letting
    // the press fall through to the orbit/pan handlers.
    bool                      section_drag_active_  = false;
    int                       section_drag_index_   = -1;
    QPoint                    section_drag_start_mouse_;
    QVector3D                 section_drag_start_origin_;
    // Mirrors GL ViewportWindow::hitTestSectionGizmo: returns the index of
    // the plane whose arrow gizmo is within grab_px of (x, y), or -1.
    int   hitTestSectionGizmo(int x, int y) const;
    // Mirrors GL ViewportWindow::updateSectionDrag: projects the cursor
    // delta onto the plane's normal in screen space and slides the plane
    // along that direction.
    void  updateSectionDrag(int x, int y);

    enum class HizSlotState : uint8_t { Idle, Mapping, Mapped };
    static constexpr int HIZ_SLOTS = 2;
    WGPUBuffer    hiz_staging_buffers_[HIZ_SLOTS] = { nullptr, nullptr };
    QMatrix4x4    hiz_slot_vp_       [HIZ_SLOTS];
    HizSlotState  hiz_slot_state_    [HIZ_SLOTS] = { HizSlotState::Idle,
                                                     HizSlotState::Idle };
    int           hiz_write_idx_                  = 0;

    // CPU mip pyramid (max-reduce). hiz_pyramid_[hiz_mip_offset_[L] + y*W + x].
    std::vector<float>    hiz_pyramid_;
    std::vector<uint32_t> hiz_mip_offset_;
    std::vector<uint32_t> hiz_mip_w_;
    std::vector<uint32_t> hiz_mip_h_;
    QMatrix4x4            hiz_vp_;
    bool                  hiz_valid_         = false;
    uint32_t              hiz_reject_count_  = 0;  // per-frame stat

    // WGPU_HIZ_TRACE=1 — diagnostic logging budget shared across the
    // parallel cull threads. Set to a non-zero count at start of cull
    // when tracing is on; each rejection in aabbOccludedByHiz atomically
    // decrements and logs while >0. Atomic because cull dispatches one
    // thread per model.
    mutable std::atomic<int> hiz_trace_budget_{0};

    QColor background_color_ = QColor("#202329");

    // Camera (orbit, right-handed Y-up world → wait, BIM is +Z up).
    // Mirrors the GL viewport's defaults; mouse navigation lands later.
    float camera_target_[3] = { 0.0f, 0.0f, 0.0f };
    float camera_distance_  = 50.0f;

    // Perspective by default; toggleProjection() (P key) flips this. When
    // true, the per-frame projection builder uses an orthographic matrix
    // sized by camera_distance_ × tan(fov/2) so toggling looks like a
    // smooth swap rather than a jump in apparent size.
    bool  projection_ortho_ = false;

    // Fly / FPS-mode state. Mirrors GL ViewportWindow::CameraMode::Fps.
    // While fps_mode_ is true: cursor is hidden, mouse-look uses raw
    // deltas, fps_keys_held_ accumulates pressed W/A/S/D/Q/E/Shift, and
    // render() integrates a movement step each frame from those keys.
    // exit via Esc (also any unrelated key click) — recenter the cursor
    // back at fps_press_center_ so the orbit camera resumes cleanly.
    bool         fps_mode_                    = false;
    QSet<int>    fps_keys_held_;
    QElapsedTimer fps_last_tick_;
    QPoint       fps_press_center_;
    bool         fps_ignore_next_mouse_move_  = false;
    // Fly base speed in m/s at no-modifier (Shift gives a 5× boost). Default
    // 5.0 matches GL fps_move_speed_. Scrollwheel in fly mode adjusts this
    // by ×1.25 / ×0.8 per notch, Blender-style — wheel does NOT zoom while
    // in fly mode (which would change camera_distance_ underneath us and
    // make speed jitter if speed were distance-scaled).
    float        fps_move_speed_              = 5.0f;
    // Per-frame [fly] dt log when WGPU_FLY_DEBUG=1. Diagnoses stutter:
    // print dt of each fpsIntegrate call and the prior render's elapsed
    // ms. Off by default (env-gated) so the normal log stays clean.
    bool         fly_debug_                   = false;
    QElapsedTimer fly_render_clock_;

    // Click-and-track diagnostic: when a pick lands, stash the chunk
    // that holds the picked object. driveStreamingLoads watches for that
    // chunk's `is_resident` flipping true→false and dumps the priority
    // / pool stats at the moment of eviction so we can see why it lost.
    uint32_t     tracked_object_id_           = 0;
    uint32_t     tracked_chunk_mid_           = 0;
    size_t       tracked_chunk_idx_           = SIZE_MAX;
    bool         tracked_was_resident_        = false;

    // Mouse-navigation bindings — mirrors GL's NavBindings + currentNavBindings().
    // Selection stays on LMB for every preset (none of the presets steal it),
    // so the click-vs-drag distinction at mouseReleaseEvent's pick path keeps
    // working. Set at init from WGPU_NAV_PRESET=blender|rhino|revit (default
    // blender, matching GL's AppSettings::NavPreset::Blender default).
    Qt::MouseButton       orbit_button_ = Qt::MiddleButton;
    Qt::KeyboardModifiers orbit_mods_   = Qt::NoModifier;
    Qt::MouseButton       pan_button_   = Qt::MiddleButton;
    Qt::KeyboardModifiers pan_mods_     = Qt::ShiftModifier;
    // Set by mousePressEvent based on which binding matched; consumed by
    // mouseMoveEvent so mid-drag modifier changes don't switch axes.
    enum class NavDrag : uint8_t { Inactive, Orbit, Pan };
    NavDrag nav_drag_kind_ = NavDrag::Inactive;
    float camera_yaw_deg_   = 45.0f;
    float camera_pitch_deg_ = 30.0f;
    float camera_fov_y_deg_ = 45.0f;
    float camera_near_      = 0.1f;
    float camera_far_       = 10000.0f;

    // Contribution-cull thresholds. Still-frame uses min_pixel_radius_;
    // when the camera changed since last frame, the bigger motion threshold
    // kicks in to drop more sub-pixel detail (and slash per-frame cull cost).
    //
    // GL ships 2.0 / 10.0, but uses euclidean distance for projected_px
    // (sqrt(dx² + dy² + dz²)) while wgpu uses view-Z distance (the
    // perspective-divide-correct denominator). For off-axis instances
    // view_z < euclidean, so wgpu's projected_px is larger than GL's at
    // the same numeric threshold — i.e. wgpu is structurally less
    // aggressive. Bumping to 3.0 / 15.0 compensates so the effective drop
    // rate matches GL's; on the federation scene this lands obj/tri
    // counts within ~10% of GL's across an orbit (vs ~3× without the
    // bump). Override at runtime via WGPU_MIN_PX / WGPU_MIN_PX_MOTION.
    float min_pixel_radius_        = 3.0f;
    float motion_min_pixel_radius_ = 15.0f;

    // Whether driveCull dispatches per-model work via std::async. ON by
    // default; setting WGPU_CULL_THREADS=0 forces sequential cull for
    // measurement (does std::async actually parallelize on this libstdc++?
    // and is per-model the right granularity?).
    bool  cull_threads_enabled_     = true;

public:
    // Master switch for HiZ occlusion. OFF by default — has two issues vs
    // the GL backend on this codepath (see task #58):
    //   (1) Correctness: bottom-edge AABBs get falsely rejected as the
    //       camera rotates. Math review didn't pin it down; root cause
    //       likely needs RenderDoc capture of the pyramid.
    //   (2) Perf: HiZ ON costs ~2.5 ms more cull time than HiZ OFF on
    //       the federation bench but only saves ~1 ms of raster work
    //       because our indirect-draw iterates the visible_draws buffer
    //       regardless. Net 9% slower (49.7 vs 54.2 fps).
    // Opt-in via WGPU_HIZ=1.
    bool hiz_enabled_ = false;

    // When true, initWgpu requests the WebGPU mandatory floor limits
    // (maxStorageBufferBindingSize=128MB, maxBufferSize=256MB) instead of
    // the adapter's actual maximum. Use this to verify on desktop that a
    // scene fits through the constraints a browser will impose.
    bool web_limits_ = false;

    // Monotonic frame counter, bumped at the top of driveStreamingLoads.
    // Used as the LRU key for chunk eviction.
    uint64_t streaming_frame_idx_           = 0;

    // Sub-allocator for all chunk vertex + index bytes. Sized at startup
    // by probeAndCreatePool() — the runtime tells us how big a single
    // buffer it can actually deliver, eliminating the per-machine OOM
    // ceiling that one-WGPUBuffer-per-chunk would otherwise hit. All
    // chunk allocations land here; nothing else uses the pool. Replaces
    // the old hand-picked streaming_vram_budget_bytes_ knob entirely.
    BufferPool pool_;

    // Background worker that does scatter-gather chunk reads off the
    // render thread. driveStreamingLoads enqueues requests for visible
    // non-resident chunks and drains completed results into the pool
    // on subsequent frames. Kills the 100-300 ms per-frame stutters
    // that synchronous disk reads caused during orbit.
    StreamingThread streaming_thread_;

    // Per-frame streaming activity, written by driveStreamingLoads,
    // consumed by the benchmark harness to delay the orbit sweep until
    // the initial cold-load settles. `loads` = chunks brought resident
    // this frame; `more_pending` = the loader wants to keep going.
    int  streaming_loads_this_frame_ = 0;
    bool streaming_more_pending_     = false;

    // Per-frame streaming counters for WGPU_STREAM_DEBUG. Mutated inside
    // driveStreamingLoads, consumed by the per-frame debug print and the
    // bench-warm timeout dump.
    int  streaming_candidates_this_frame_      = 0;
    int  streaming_evictions_lru_this_frame_   = 0;
    int  streaming_evictions_pri_this_frame_   = 0;
    int  streaming_drained_this_frame_         = 0;
    int  streaming_blocked_oom_this_frame_     = 0;
    bool streaming_debug_                      = false;  // WGPU_STREAM_DEBUG=1

    // Bench warm-phase counters. We wait until N consecutive frames with
    // 0 loads (convergence) before starting the orbit sweep, capped by
    // MAX_WARM_FRAMES so chronically thrashing scenes still produce
    // numbers. Both reset implicitly per bench run via setBenchmarkFrames.
    int  bench_warm_streak_          = 0;
    int  bench_warm_frames_total_    = 0;
    bool bench_warm_done_            = false;  // latch: once true, gate is open for this run

private:

    // Switch to LOD1 when an instance's projected bounding-sphere radius
    // drops below this many pixels. 0 disables (always LOD0). Defaults
    // mirror AppSettings::lod1PixelThreshold() in the GL backend.
    float lod1_pixel_threshold_ = 30.0f;

    // Per-model state, keyed by viewport-assigned model_id.
    std::unordered_map<uint32_t, ModelGpuData> models_gpu_;
    uint32_t next_model_id_  = 1;
    // Globally-unique object_id allocator. Each applyCachedModel rebases
    // the sidecar's local object_ids by base_object_id_so_far so picks
    // are unambiguous across models. Selection flags index this range.
    uint32_t next_object_id_ = 1;

    // Sidecar paths queued before init completes.
    std::deque<QString> pending_sidecars_;

    // Direct-IFC staging buffers, keyed by streamer model_id. Populated
    // by uploadMeshChunk / uploadInstanceChunk; consumed and cleared by
    // finalizeModel. Shape matches SidecarData so the same chunk-planner
    // + apply flow services both sidecar and direct-IFC loads. Held by
    // unique_ptr so emplace / erase don't copy the (potentially huge)
    // vertex byte vector when the map rehashes.
    std::unordered_map<uint32_t, std::unique_ptr<SidecarData>>
        pending_direct_loads_;

    // Set after the first model load triggers a viewAll(); prevents
    // subsequent loads from snapping the camera away from where the
    // user pointed it.
    bool initial_view_applied_ = false;

    // Camera state at the previous render() for motion detection. Any
    // change means we apply the motion contribution threshold this frame
    // (drops more sub-pixel work mid-orbit; matches GL behaviour).
    float prev_camera_target_[3]   = { 0, 0, 0 };
    float prev_camera_distance_    = 0.0f;
    float prev_camera_yaw_deg_     = 0.0f;
    float prev_camera_pitch_deg_   = 0.0f;
    bool  has_prev_camera_         = false;

    // True iff the last cull used the motion threshold. Render schedules a
    // single settle frame after motion stops so the previously dropped
    // sub-pixel instances reappear at the still threshold. Without this,
    // event-driven rendering would leave those instances missing forever
    // because no further frame is requested after the user releases the
    // mouse. Matches GL's last_cull_was_motion_ behaviour.
    bool  last_cull_was_motion_    = false;

    // Pending one-shot screenshot, captured at the end of the next render().
    QString pending_screenshot_path_;
    bool    pending_screenshot_quit_ = false;

    // Mouse navigation state. LMB drag orbits, MMB drag pans, wheel zooms.
    // LMB-click-without-drag picks the object under the cursor. No
    // Blender/Maya preset awareness yet — that arrives with AppSettings.
    Qt::MouseButton nav_active_button_ = Qt::NoButton;
    QPoint          nav_last_pos_;
    QPoint          nav_press_pos_;
    bool            nav_dragged_       = false;

    // Benchmark mode. setBenchmarkFrames(N) arms it; render() integrates the
    // yaw, captures per-frame ms after warmup, and prints + quits when the
    // target frame count is hit.
    int   bench_total_    = 0;
    int   bench_count_    = 0;
    int   bench_warmup_   = 5;
    float bench_yaw_start_ = 0.0f;
    float bench_yaw_speed_ = 0.5f;  // degrees per frame
    std::vector<float> bench_frame_ms_;

    // Per-frame stat snapshot from the last cull. Sum of m.mesh_draws across
    // visible models. Exposed via the benchmark summary; will grow into a
    // proper FrameStats signal when stage 11's host integration arrives.
    uint32_t last_visible_objects_   = 0;
    uint32_t last_visible_triangles_ = 0;
    uint32_t last_sub_draws_         = 0;

    // Phase-time accumulators for benchmark mode. Each window measures a
    // distinct slice of render() so we can attribute frame cost. Totals
    // across the timed window are divided by bench_total_ on print.
    double   bench_cull_ms_total_     = 0.0;
    double   bench_stream_ms_total_   = 0.0;  // driveStreamingLoads only
    double   bench_hiz_readback_ms_total_ = 0.0;
    double   bench_submit_ms_total_   = 0.0;

    // Last-frame per-phase times. Available in interactive mode (no
    // bench) so the periodic [frame] heartbeat log can show cull /
    // stream cost without needing the bench averaging machinery.
    double   last_cull_ms_            = 0.0;
    double   last_cull_compute_ms_    = 0.0;  // parallel per-model cull
    double   last_cull_upload_ms_     = 0.0;  // sequential queueWriteBuffer pass
    double   last_stream_ms_          = 0.0;

    // Tick count for the interactive (non-bench) [frame] heartbeat log.
    // Increments every render() and prints stats every N frames.
    int      interactive_frame_count_ = 0;

    // Rolling 60-sample frame-time window for the smoothed fps emitted
    // via frameStatsUpdated. Index wraps; sum kept incrementally to
    // avoid a per-frame reduction.
    static constexpr int FRAME_TIME_WINDOW = 60;
    double   frame_time_ms_window_[FRAME_TIME_WINDOW] = {};
    int      frame_time_ms_count_  = 0;
    int      frame_time_ms_head_   = 0;
    double   frame_time_ms_sum_    = 0.0;

    // FederatedFalseOrigin matrix, in metres. Default identity. Stored
    // but not yet applied to per-instance composed transforms — the
    // recompose pass arrives with the federation-load OOM work.
    Eigen::Matrix4d federated_false_origin_meters_ = Eigen::Matrix4d::Identity();

    // Per-frame LOD selection counts, mutated from cullModelCpuCompute
    // and reset after the [frame] heartbeat prints them. Keeps an eye
    // on whether LOD1 is actually firing on real scenes — early-days
    // diagnostic while we trust the new code path.
    mutable uint32_t lod1_dbg_count_              = 0;
    mutable uint32_t lod0_dbg_eligible_count_     = 0;
    mutable uint32_t lod0_dbg_no_lod1_count_      = 0;
    mutable uint64_t lod1_dbg_tris_saved_         = 0;
};

#endif // WGPUVIEWPORTWINDOW_H
