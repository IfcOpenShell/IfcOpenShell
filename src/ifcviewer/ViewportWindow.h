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

#include <string>
#include <unordered_set>

#include "Stopwatch.h"

#include <webgpu/webgpu.h>

#include <Eigen/Dense>

#include <atomic>
#include <cstdint>
#include <deque>
#include <memory>
#include <unordered_map>
#include <unordered_set>

#include "FrameStats.h"
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
    void  onFrameStats(const FrameStats& stats) override;
    void  encodeOverlaysInMainPass(WGPURenderPassEncoder pass,
                                   const OverlayFrame& frame) override;
    void  encodeOverlaysPostMain(WGPUCommandEncoder enc,
                                 WGPUTextureView surface_view,
                                 const OverlayFrame& frame) override;
    void  saveScreenshotRgba8(const std::string& path, const std::uint8_t* rgba,
                              int w, int h) override;

    void setBackgroundColor(float r, float g, float b, float a = 1.0f);

    // Queue a sidecar path to be loaded after wgpu init completes. Safe to
    // call before the window is exposed. The path is resolved against the
    // working directory and read via SidecarCache::readSidecar (which
    // normalises stem → .ifcview).
    void queueLoadSidecar(const std::string& path);

    // Synchronous metadata load + GPU upload. Requires wgpu init to have
    // completed (i.e. the window has been exposed at least once). Returns
    // the assigned session_model_id, or 0 on failure. Reads metadata only (mesh
    // dict + instance dict + georef); per-chunk vertex / index bytes are
    // read on demand by the per-frame loader as chunks become visible.
    uint32_t loadSidecar(const std::string& path);

    // Allocates per-chunk small buffers and the model-shared mesh /
    // instance storage upfront, but leaves each chunk's pool ranges
    // unclaimed and is_resident=false. The per-frame loader
    // (driveStreamingLoads) sub-allocates the chunk's vertex + index
    // ranges from pool_ on demand as cull flags them visible.
    void applyCachedModel(uint32_t session_model_id,
                          struct StreamingSidecar metadata);

    // Direct-IFC ingestion (mirrors GL ViewportWindow). The host (typically
    // a GeometryStreamer running on a worker) calls uploadStreamedMesh +
    // uploadStreamedInstance once per representation / placement as the IFC
    // triangulates; finalizeModel commits when the iterator finishes.
    // Staged in CPU memory; finalizeModel runs the chunk planner over the
    // staged data, allocates pool slices, and uploads — same render path
    // as a sidecar load. Bytes are gathered from memory (no disk I/O), so
    // every chunk lands `is_resident=true` immediately. The streamer's
    // session_model_id is passed through unchanged; the viewport's globally-unique
    // object_id rebasing happens at finalize time.
    void uploadStreamedMesh(const struct StreamedMesh& mesh);
    void uploadStreamedInstance(const struct StreamedInstance& instance_record);
    void finalizeModel(uint32_t session_model_id);

    void removeModel(uint32_t session_model_id);
    void resetScene();

    // Model-level visibility. Mirrors the GL ViewportWindow API — flips
    // ModelGpuData::hidden, which every render/pick/cull pass already
    // consults. requestUpdate() so the change is visible immediately.
    void hideModel(uint32_t session_model_id);
    void showModel(uint32_t session_model_id);

    // Federation pipeline: composed instance transform =
    //   FederatedFalseOrigin · ModelTransformation · CoordinateOperation
    //                                              · placement_transformation
    // Wgpu does not yet recompose instances against these matrices —
    // composeInstanceFromPlacement is still placement-only — so the
    // setters store the input and post requestUpdate(). Bonsai-side
    // integration compiles against these signatures; visual georef parity
    // arrives with the recompose+SSBO-rewrite work tracked separately.
    void setFederatedFalseOrigin(const Eigen::Matrix4d& matrix_meters);
    void setModelCoordinateOperation(uint32_t session_model_id,
                                     const Eigen::Matrix4d& matrix_meters);
    void setModelTransformation(uint32_t session_model_id,
                                const Eigen::Matrix4d& matrix_meters);

    size_t modelCount() const { return models_gpu_.size(); }

    // Frame the union of all loaded models' world AABBs. No-op on empty
    // scenes. Called automatically after the first model loads (unless
    // setCamera was already invoked); clients can re-invoke to re-frame.
    void viewAll();

    // viewAll scoped to specific models — "view selected model" in a federation
    // browser. Returns whether it framed anything (unloaded / empty models
    // leave the camera where it was).
    bool viewModels(const std::vector<uint32_t>& session_model_ids);

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
    std::string cameraString() const;

    // Snapshot of the orbit camera. Canonical struct now lives in
    // ViewportCore so the camera-mutator path stays Qt-free (#84-i);
    // the alias keeps bonsai's "save view" / "restore view" callers
    // working unchanged.
    using CameraState = ViewportCore::CameraState;
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
    // buildViewProj moved to ViewportCore (#84-h).
    // Per-frame WASD integration when fps_mode_ is true. Called near the
    // top of render() so the displayed frame already reflects movement.
    void fpsIntegrate();
    // Build the camera AABB for a single object across all loaded models.
    bool computeObjectAabb(uint32_t object_id,
                           float mn[3], float mx[3]) const;
public:
    // Eigen::Vector3f overload — matches GL ViewportWindow::computeObjectAabb so
    // bonsai's volume readout / focus callers compile unchanged. Just a
    // thin wrapper around the float[3] version.
    bool computeObjectAabb(uint32_t object_id,
                           Eigen::Vector3f& mn, Eigen::Vector3f& mx) const;
private:
    // Re-aim the orbit camera so the bounding sphere of [mn, mx] fits.
    void frameAabb(const float mn[3], const float mx[3], float padding);

    // chunkScreenAreaPx moved to ViewportCore (#84-h).

public:
    // Apply a nav mouse preset by name ("blender"|"rhino"|"revit"|"web").
    // Sources the shared binding table from ViewportCore; called from init
    // (env / persisted setting) and live from the Settings dialog.
    void applyNavPreset(const char* name);
    void setBackfaceCulling(bool enabled);


    // Queue a one-shot framebuffer capture: the next rendered frame is
    // copied back to host memory and saved to `path` as PNG. If
    // `quit_after` is true, QCoreApplication::quit() is called once the
    // PNG is written. Use this for headless verification and pixel-diff
    // parity testing against the GL backend.
    void captureNextFrameToPng(const std::string& path, bool quit_after = true);

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
    // configureSurface moved to ViewportCore (#84-u).
    void render();
    void shutdown();

    bool  buildPipelines();
    void  buildModelBindGroup(ModelGpuData& m);
    // buildChunkBindGroup / applyStreamedChunk / loadChunkBytesAndUploadGpu
    // / unloadChunk moved to ViewportCore (#84-n). Call them via core_.
    //
    // Called from render() after cull: find non-resident chunks with
    // current visible draw counts > 0 and bring them resident. When the
    // pool is full, evicts LRU non-visible chunks first, then falls back
    // to evicting the farthest-from-camera visible chunks if a closer
    // candidate needs the space. Triggers requestUpdate() if more remain.
    void  driveStreamingLoads();

    void  ensureDepthTexture(int w, int h);
    void  releaseDepthTexture();
    void  ensureMsaaColorTexture(int w, int h);
    void  releaseMsaaColorTexture();

    bool  buildHizPipeline();
    bool  buildEdgePipeline();
    void  encodeEdgePass(WGPUCommandEncoder enc, WGPUTextureView surface_view);
    // setPivotIndicatorVisible moved to ViewportCore — the indicator is drawn
    // by the shared AxisIndicatorRenderer now, so its visibility (afterglow
    // included) lives next to the drawing for desktop + web alike.
    // releaseEdgeResources / buildPickPipeline / ensurePickAttachments /
    // releasePickResources moved to ViewportCore (#84-s, #84-t).

    // Make sure selection_flags_buffer_ is large enough to address every
    // object_id in next_object_id_. Recreates (and rebuilds frame_bind_group_)
    // if it grew. Safe to call every frame; idempotent when already sized.
    void  ensureSelectionFlagsBuffer();
    // Repack the CPU selection into bit-flags and wgpuQueueWriteBuffer to
    // the GPU. Called from render() when selection_.dirty().
    void  uploadSelectionFlagsIfDirty();
    // Synchronous pick: encodes a one-shot R32UInt render of the current
    // visible_draws against the click pixel, copies the single texel back,
    // waits, and returns the object_id (0 if nothing was hit). Call from
    // the main thread between renders. When `normal_out` is non-null, the
    // pick pass's RGBA16F normal MRT is also sampled at the same pixel
    // (decoded from ×0.5+0.5 packing) so the section tool can drop
    // perpendicular cuts.
    uint32_t pickObjectAt(int x_pixels, int y_pixels,
                          Eigen::Vector3f* normal_out = nullptr);
    // Pick + ray-cast — returns the object's id, the world-space point
    // where the pick-pixel pillar enters that instance's AABB, and a
    // camera-facing normal. Returns false on a background miss. We do
    // CPU ray-AABB rather than reading per-pixel depth because WebGPU's
    // copyTextureToBuffer for Depth32Float requires copying the whole
    // mip extent — wasteful per click — and ray-vs-AABB lands close
    // enough to the click for the section tool's "drop a plane here" UX.
    bool pickSurfaceAt(int x_pixels, int y_pixels,
                       uint32_t& object_id_out,
                       Eigen::Vector3f& world_pos_out,
                       Eigen::Vector3f& world_normal_out,
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
    bool  addSectionPlaneAtSurface(const Eigen::Vector3f& point,
                                   const Eigen::Vector3f& normal,
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
    void  setHudText(const std::string& text);
    // Translucent world-space triangle overlay (Area-tool patch shading).
    // Empty list disables; color is RGBA in [0, 1].
    void  setHighlightTriangles(const std::vector<float>& world_xyz,
                                float r, float g, float b, float a);

    // CPU mesh shadow: positions (3 floats/vert, mesh-local) + indices
    // (LOD0). Populated at applyCachedModel / applyStreamedChunk —
    // returns false if the mesh isn't loaded yet (streaming) or the
    // (session_model_id, mesh_id) pair doesn't resolve. Matches the GL
    // ViewportWindow::MeshTriangles + readbackMeshTriangles shape so
    // the measure tools port verbatim.
    using MeshTriangles = ModelGpuData::MeshTriangles;
    bool  readbackMeshTriangles(uint32_t session_model_id, uint32_t mesh_id,
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
    // viewport already keeps the CPU-side MeshInfo + InstanceInfo around
    // for picking / measurement; the federation false-origin guess
    // (ViewportView::guessFederatedFalseOriginFromFirstModel) consumes
    // this lazily on modelGeometryReady. Returns false when the model
    // is unknown or has no instances.
    uint32_t modelObjectIdBase(uint32_t session_model_id) const;
    bool firstGeometryPointWorldM(uint32_t session_model_id,
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
    void frameOnFederatedOrigin(uint32_t session_model_id, float max_distance_m);

    // Selection accessor. Exposed for callers (bonsai's volume readout)
    // that need to read selectionIds() / activeObjectId(). Mutation goes
    // through the existing setSelection / pick paths.
    SelectionState&       selection()       { return selection_; }
    const SelectionState& selection() const { return selection_; }

    // Pick + resolve to mesh-local space. MeshLocalPick lives in
    // ViewportCore (#84-t); re-exported here so existing bonsai
    // callers keep referring to ViewportWindow::MeshLocalPick.
    using MeshLocalPick = ViewportCore::MeshLocalPick;
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
    // RaycastHit moved to ViewportCore (#84-t); re-exported here.
    using RaycastHit = ViewportCore::RaycastHit;
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
    // ViewportWindow::FrameStats is a using-alias for ::FrameStats (moved
    // to its own Qt-free header so ViewportHost::onFrameStats can carry
    // it without dragging Qt into core). Existing bonsai signal binding
    // (frameStatsUpdated) keeps using the qualified name.
    using FrameStats = ::FrameStats;

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
    void  startHizMap(int slot, const Eigen::Matrix4f& vp_used);
    // Drains pending mapAsync callbacks (via processEvents — does NOT
    // block on GPU work). For any slot that just signalled Mapped, reads
    // it, unmaps it, max-reduces the mip pyramid, and updates hiz_vp_.
    void  drainHizReadbacks();
    // Project AABB through hiz_vp_ and test against the pyramid. False
    // (keep) if HiZ isn't valid yet, AABB straddles the near plane, or
    // any projection is unreliable. True (cull) when AABB is provably
    // behind every relevant pyramid cell.
    bool  aabbOccludedByHiz(const float mn[3], const float mx[3]) const;
    void  flushPendingSidecarQueue();
    // computeSceneAabb moved to ViewportCore (#84-h).

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
    // cullModelCpuCompute / cullModelCpuUpload moved to ViewportCore
    // (#84-p). The render path calls core_.cullModelCpuCompute with a
    // ViewportCore::HizOccludedFn that wraps aabbOccludedByHiz when
    // HiZ is enabled (the pyramid + readback orchestration is still
    // here), or null otherwise.

    // Compose one instance's `transform` (float[16] column-major) from
    //   FederatedFalseOrigin · ModelTransformation · CoordinateOperation
    //                                              · placement_transformation
    // and recompute its world AABB from the mesh's local AABB. Maths runs
    // in double; the cast to float happens last so large IFC placements
    // get cancelled by the federation false origin before precision is
    // narrowed. Mirrors GL ViewportWindow::composeInstanceFromPlacement.
    // Implementation lives in ViewportCore now (#84-d); this declaration
    // stayed during the move and forwards to core_ — once every internal
    // caller routes through ViewportCore directly the forwarder goes away.

    // Walk every instance of `session_model_id`, recompose its transform from the
    // current federation matrices, refresh per-chunk world AABBs, and
    // re-upload InstanceGpu[] into m.instance_storage. No-op if the model
    // is unknown, has no instances, or wgpu init hasn't completed.
    void recomposeAndUploadModel(uint32_t session_model_id);

    bool& wgpu_initialized_;
    int& configured_w_;
    int& configured_h_;

    // ---- wgpu lifecycle state aliases ----------------------------------
    //
    // Actual storage lives in core_ (declared below; ViewportWindow is a
    // friend of ViewportCore so these references can bind). Existing
    // member-access sites in ViewportWindow.cpp keep working unchanged —
    // they just resolve to core_.device_ etc. through these references.
    // Each one is removed when its owning render method moves into
    // ViewportCore (#84-b onwards).
    ViewportCore core_;
    WGPUInstance&      instance_;
    WGPUAdapter&       adapter_;
    WGPUDevice&        device_;
    WGPUQueue&         queue_;
    WGPUSurface&       surface_;
    WGPUTextureFormat& surface_format_;
    bool&              surface_configured_;

    // Pipeline + bind-group-layout alias references — actual storage
    // lives in core_ (see ViewportCore.h). Each goes away as the
    // building method (buildPipelines / buildEdgePipeline /
    // buildPickPipeline) migrates into ViewportCore.
    WGPUShaderModule&    main_shader_module_;
    WGPUBindGroupLayout& frame_bgl_;          // group 0
    WGPUBindGroupLayout& model_bgl_;          // group 1
    WGPUPipelineLayout&  pipeline_layout_;
    WGPURenderPipeline&  main_pipeline_;
    WGPURenderPipeline&  main_pipeline_transparent_;

    // Frame uniforms + selection flags aliases (storage in core_).
    WGPUBuffer&    frame_uniform_buffer_;
    WGPUBindGroup& frame_bind_group_;
    WGPUBuffer&    selection_flags_buffer_;
    uint32_t&      selection_flags_capacity_;
    std::vector<uint32_t>& selection_flags_scratch_;
    SelectionState&  selection_;
    VisibilityState& visibility_;

    // Depth + MSAA attachment aliases (storage in core_, #84-r).
    WGPUTexture&     depth_texture_;
    WGPUTextureView& depth_view_;
    int&             depth_w_;
    int&             depth_h_;
    WGPUTexture&     msaa_color_texture_;
    WGPUTextureView& msaa_color_view_;
    int&             msaa_w_;
    int&             msaa_h_;
    // SAMPLE_COUNT moved to ViewportCore.h as kViewportSampleCount (#84-k).
    static constexpr uint32_t SAMPLE_COUNT = kViewportSampleCount;

    // HiZ aliases (storage in core_, #84-r). The render path still
    // drives the per-frame HiZ submit/drain orchestration, but the
    // pipeline + pyramid + slot state all live in ViewportCore now.
    WGPUShaderModule&    hiz_shader_module_;
    WGPUBindGroupLayout& hiz_bgl_;
    WGPUPipelineLayout&  hiz_pipeline_layout_;
    WGPURenderPipeline&  hiz_pipeline_;
    WGPUBuffer&          hiz_uniform_buffer_;
    WGPUBindGroup&       hiz_bind_group_;
    WGPUTexture&         hiz_resolve_texture_;
    WGPUTextureView&     hiz_resolve_view_;
    uint32_t&            hiz_resolve_w_;
    uint32_t&            hiz_resolve_h_;
    uint32_t&            hiz_padded_bpr_;
    // Edge silhouette post-process (stage 9). Samples the MSAA depth
    // texture in a fullscreen pass, computes a depth Laplacian, blends
    // dark lines into the resolved surface colour. Matches GL's
    // renderEdgePass() visually.
    // Edge silhouette pipeline aliases (storage in core_).
    WGPUShaderModule&    edge_shader_module_;
    WGPUBindGroupLayout& edge_bgl_;
    WGPUPipelineLayout&  edge_pipeline_layout_;
    WGPURenderPipeline&  edge_pipeline_;
    WGPUBindGroup&      edge_bind_group_;
    bool&               edges_enabled_;

    // The Qt-coupled viewport overlays (marquee rect, measure lines /
    // points / labels, highlight triangles) — pipelines + shaders +
    // buffers + encoders. The viewport builds a OverlayFrame each frame
    // and asks the renderer to encode each overlay; see OverlayRenderer.h.
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
    // Pick pipeline + targets + staging all moved to ViewportCore (#84-t).
    // No remaining VW callers need the textures/buffers by name, so no
    // aliases here.
    WGPURenderPipeline& pick_pipeline_;

    // Section-cutting state aliases (storage in core_). The section tool
    // mutates section_planes_ through addSectionPlaneAtSurface /
    // removeSectionPlane; the per-frame uniform packs the same vector
    // for the WGSL fragment-side clip gate.
    std::vector<SectionPlane>& section_planes_;
    bool                          section_tool_active_  = false;

    // X-ray cap alias (storage in core_). Default 1.0 = no effect
    // (fragment shader clamps alpha = min(in.color.a, xray_alpha_cap_),
    // which returns in.color.a when the cap is 1). Alt+X drops it to
    // 0.3 to translucent the whole scene; pressing again restores 1.0.
    // When < 1.0, the cull classifier (also in core) routes every
    // instance into the transparent pass so the blend stage actually
    // fires (an opaque-pass fragment with capped alpha would still
    // overwrite the back buffer).
    float& xray_alpha_cap_;

    // Marquee box-select. Armed on LMB press (when no other tool consumes
    // the click), becomes active after the cursor moves past
    // kBoxSelectThresholdPx — until then a release still routes through
    // the single-pick path. Press-time modifiers decide the set op at
    // release: plain → replace, Shift → add, Ctrl → remove.
    bool                       box_select_armed_      = false;
    bool                       box_select_active_     = false;
    Eigen::Vector2i                     box_select_start_pos_;     // logical px
    Eigen::Vector2i                     box_select_current_pos_;   // logical px
    Qt::KeyboardModifiers      box_select_press_mods_ = Qt::NoModifier;
    static constexpr int       kBoxSelectThresholdPx  = 5;
    // box_pick_staging_buffer_/_capacity_ moved to ViewportCore (#84-t).
    // Section-gizmo drag state + hit-test/drag math moved to ViewportCore
    // (shared with web; the mouse handlers call core_.begin/update/endSectionDrag
    // and core_.hitTestSectionGizmo).

    // HiZ slot + pyramid aliases (storage in core_, #84-r). VW's render
    // loop reads hiz_valid_ / hiz_vp_ to gate the HizOccludedFn, and
    // resets hiz_trace_budget_ once per frame; everything else moved.
    std::vector<float>&         hiz_pyramid_;
    std::vector<uint32_t>&      hiz_mip_offset_;
    std::vector<uint32_t>&      hiz_mip_w_;
    std::vector<uint32_t>&      hiz_mip_h_;
    Eigen::Matrix4f&            hiz_vp_;
    bool&                       hiz_valid_;
    uint32_t&                   hiz_reject_count_;
    std::atomic<int>&           hiz_trace_budget_;

    // Camera state aliases (storage in core_).
    float (&camera_target_)[3];
    float& camera_distance_;
    bool&  projection_ortho_;

    // Fly / FPS-mode state. Mirrors GL ViewportWindow::CameraMode::Fps.
    // While fps_mode_ is true: cursor is hidden, mouse-look uses raw
    // deltas, fps_keys_held_ accumulates pressed W/A/S/D/Q/E/Shift, and
    // render() integrates a movement step each frame from those keys.
    // exit via Esc (also any unrelated key click) — recenter the cursor
    // back at fps_press_center_ so the orbit camera resumes cleanly.
    bool         fps_mode_                    = false;
    std::unordered_set<int> fps_keys_held_;
    Stopwatch    fps_last_tick_;
    Eigen::Vector2i       fps_press_center_;
    bool         fps_ignore_next_mouse_move_  = false;
    // Fly base speed (m/s) + wheel adjustment now live in ViewportCore
    // (fly_move_speed_ / flyAdjustSpeed), shared with the web fly path.
    // Per-frame [fly] dt log when WGPU_FLY_DEBUG=1. Diagnoses stutter:
    // print dt of each fpsIntegrate call and the prior render's elapsed
    // ms. Off by default (env-gated) so the normal log stays clean.
    bool         fly_debug_                   = false;
    Stopwatch    fly_render_clock_;

    // Click-and-track aliases (storage in core_). The pick handler still
    // lives in VW so it touches these by name; driveStreamingLoads in
    // core dumps the priority / pool stats at eviction.
    uint32_t&    tracked_object_id_;
    uint32_t&    tracked_chunk_mid_;
    size_t&      tracked_chunk_idx_;
    bool&        tracked_was_resident_;

    // Mouse-navigation bindings — mirrors GL's NavBindings + currentNavBindings().
    // Selection stays on LMB for every preset (none of the presets steal it),
    // so the click-vs-drag distinction at mouseReleaseEvent's pick path keeps
    // working. Set at init from WGPU_NAV_PRESET=blender|rhino|revit (default
    // blender, matching GL's AppSettings::NavPreset::Blender default).
    // Mirror of ViewportCore's preset bindings, mapped to Qt types by
    // applyNavPreset (the core owns the preset table; these are the Qt-side
    // cache the mouse handlers compare against).
    Qt::MouseButton       orbit_button_  = Qt::MiddleButton;
    Qt::KeyboardModifiers orbit_mods_    = Qt::NoModifier;
    Qt::MouseButton       pan_button_    = Qt::MiddleButton;
    Qt::KeyboardModifiers pan_mods_      = Qt::ShiftModifier;
    Qt::MouseButton       select_button_ = Qt::LeftButton;
    Qt::KeyboardModifiers select_mods_   = Qt::NoModifier;
    // Set by mousePressEvent based on which binding matched; consumed by
    // mouseMoveEvent so mid-drag modifier changes don't switch axes.
    enum class NavDrag : uint8_t { Inactive, Orbit, Pan };
    NavDrag nav_drag_kind_ = NavDrag::Inactive;
    float& camera_yaw_deg_;
    float& camera_pitch_deg_;
    float& camera_fov_y_deg_;
    float& camera_near_;
    float& camera_far_;

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
    // Cull-tuning aliases (storage in core_, #84-x). VW's env-var prelude
    // still mutates these through the alias.
    float& min_pixel_radius_;
    float& motion_min_pixel_radius_;

    // Whether driveCull dispatches per-model work via std::async. ON by
    // default; setting WGPU_CULL_THREADS=0 forces sequential cull for
    // measurement (does std::async actually parallelize on this libstdc++?
    // and is per-model the right granularity?).
    bool&  cull_threads_enabled_;

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
    // Opt-in via WGPU_HIZ=1. Storage in core_; aliased here so the
    // env-var setup + render() gating keep compiling.
    bool& hiz_enabled_;

    // When true, initWgpu requests the WebGPU mandatory floor limits
    // (maxStorageBufferBindingSize=128MB, maxBufferSize=256MB) instead of
    // the adapter's actual maximum. Use this to verify on desktop that a
    // scene fits through the constraints a browser will impose.
    bool web_limits_ = false;

    // Monotonic frame counter alias (storage in core_). Bumped at the
    // top of driveStreamingLoads; used as the LRU key for chunk
    // eviction.
    uint64_t& streaming_frame_idx_;

    // Sub-allocator for all chunk vertex + index bytes. Sized at startup
    // by probeAndCreatePool() — the runtime tells us how big a single
    // buffer it can actually deliver, eliminating the per-machine OOM
    // ceiling that one-WGPUBuffer-per-chunk would otherwise hit. All
    // chunk allocations land here; nothing else uses the pool. Replaces
    // the old hand-picked streaming_vram_budget_bytes_ knob entirely.
    // Scene-state aliases (storage in core_).
    BufferPool&      pool_;
    StreamingThread& streaming_thread_;

    // Per-frame streaming activity aliases (storage in core_). Written
    // by driveStreamingLoads; consumed by the still-in-VW benchmark
    // harness.
    int&  streaming_loads_this_frame_;
    bool& streaming_more_pending_;

    // Per-frame streaming counters (storage in core_). Consumed by the
    // bench-warm timeout dump in render() (still VW-side).
    int&  streaming_candidates_this_frame_;
    int&  streaming_evictions_lru_this_frame_;
    int&  streaming_evictions_pri_this_frame_;
    int&  streaming_drained_this_frame_;
    int&  streaming_blocked_oom_this_frame_;
    bool& streaming_debug_;

    // Bench warm-phase counters. We wait until N consecutive frames with
    // 0 loads (convergence) before starting the orbit sweep, capped by
    // MAX_WARM_FRAMES so chronically thrashing scenes still produce
    // numbers. Both reset implicitly per bench run via setBenchmarkFrames.
    int&  bench_warm_streak_;
    int&  bench_warm_frames_total_;
    bool& bench_warm_done_;

private:

    // LOD1 pixel threshold alias (storage in core_, #84-x).
    float& lod1_pixel_threshold_;

    // Per-model state aliases (storage in core_).
    std::unordered_map<uint32_t, ModelGpuData>& models_gpu_;
    uint32_t& next_session_model_id_;
    uint32_t& next_object_id_;

    // Sidecar paths queued before init completes.
    std::deque<std::string> pending_sidecars_;

    // pending_direct_loads_ + initial_view_applied_ moved to ViewportCore
    // (#84-q). initial_view_applied_ stays accessible here as a reference
    // alias so VW::setCamera can flip it without poking through core_.
    bool& initial_view_applied_;

    // Camera-state aliases for motion detection (storage in core_, #84-x).
    float (&prev_camera_target_)[3];
    float& prev_camera_distance_;
    float& prev_camera_yaw_deg_;
    float& prev_camera_pitch_deg_;
    bool&  has_prev_camera_;
    bool&  last_cull_was_motion_;

    // Pending one-shot screenshot path alias (storage in core_).
    // Captured at the end of the next render(); driveStreamingLoads
    // observes the non-empty value to switch into the sync chunk-load
    // fallback so the first-frame capture isn't an empty buffer.
    std::string& pending_screenshot_path_;
    bool&        pending_screenshot_quit_;

    // Mouse navigation state. LMB drag orbits, MMB drag pans, wheel zooms.
    // LMB-click-without-drag picks the object under the cursor. No
    // Blender/Maya preset awareness yet — that arrives with AppSettings.
    Qt::MouseButton nav_active_button_ = Qt::NoButton;
    Eigen::Vector2i          nav_last_pos_;
    Eigen::Vector2i          nav_press_pos_;
    bool            nav_dragged_       = false;

    // Benchmark + frame-stats aliases (storage in core_, #84-x).
    // setBenchmarkFrames(N) writes the bench_* fields through these
    // aliases; the heartbeat / FrameStats path in core_.render reads
    // and resets them.
    int&   bench_total_;
    int&   bench_count_;
    int&   bench_warmup_;
    float& bench_yaw_start_;
    float& bench_yaw_speed_;
    std::vector<float>& bench_frame_ms_;
    uint32_t& last_visible_objects_;
    uint32_t& last_visible_triangles_;
    uint32_t& last_sub_draws_;
    double&   bench_cull_ms_total_;
    double&   bench_stream_ms_total_;
    double&   bench_hiz_readback_ms_total_;
    double&   last_cull_ms_;
    double&   last_cull_compute_ms_;
    double&   last_cull_upload_ms_;
    double&   last_stream_ms_;
    int&      interactive_frame_count_;

    // FederatedFalseOrigin matrix, in metres. Default identity. Stored
    // but not yet applied to per-instance composed transforms — the
    // recompose pass arrives with the federation-load OOM work.
    // Federation false-origin alias (storage in core_).
    Eigen::Matrix4d& federated_false_origin_meters_;

    // Per-frame LOD selection counts (storage in core_, mutated from
    // core_.cullModelCpuCompute). The [frame] heartbeat in VW's render()
    // still reads + resets them.
    uint32_t& lod1_dbg_count_;
    uint32_t& lod0_dbg_eligible_count_;
    uint32_t& lod0_dbg_no_lod1_count_;
    uint64_t& lod1_dbg_tris_saved_;
};

#endif // WGPUVIEWPORTWINDOW_H
