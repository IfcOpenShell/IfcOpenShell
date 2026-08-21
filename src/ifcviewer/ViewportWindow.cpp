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

#include "ViewportWindow.h"
#include "AreaMeasurement.h"
#include "CameraMath.h"
#include "ChunkPlanner.h"
#include "InstanceCompose.h"
#include "LengthMeasurement.h"
#include "Log.h"
#include "LogQt.h"
#include "StreamingLoader.h"
#include "VertexQuantization.h"

#include <QCoreApplication>
#include <QGuiApplication>
#include <QResizeEvent>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QtMath>

#include <webgpu/wgpu.h>  // wgpu-native extensions (logging, MULTI_DRAW_INDIRECT, …)

#if defined(Q_OS_WIN)
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#define NOGDI
#define NOMCX
#define NOSERVICE
#include <Windows.h>
#elif defined(Q_OS_MAC)
// Cocoa bridge declared here, implemented in the adjacent .mm file. Must be
// visible before createWgpuSurface() below calls wgpu_macos_attach_metal_layer.
#include "MetalSurface_mac.h"
#endif

#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <future>
#include <limits>
#include <set>
#include <utility>

// -----------------------------------------------------------------------------
// Frame uniforms (CPU mirror of group=0 binding=0 in the WGSL).
// std140-ish layout: every member naturally 16-aligned, struct stride = 96.
// -----------------------------------------------------------------------------

// kMaxSectionPlanes + FrameUniforms moved to ViewportCore.h (#84-k).
// Keep this assert so OverlayRenderer's kMaxSectionPlanes (the section
// visualizer's per-plane uniform slot count) stays in sync with the
// WGSL clip array size.
static_assert(kMaxSectionPlanes == OverlayRenderer::kMaxSectionPlanes,
              "section-plane cap must match OverlayRenderer's");

// Inverse of sRGB encoding. wgpu-native's Vulkan swap chain on X11 treats
// BGRA8Unorm as sRGB-output (encodes shader output linear→sRGB on write,
// despite caps reporting plain Unorm). Pre-applying srgbToLinear here on
// any value we pass to the swap chain — clearValue, etc. — makes the
// implicit encode round-trip and the final bytes match the GL backend.
static inline float srgbToLinear(float s) {
    if (s <= 0.04045f) return s / 12.92f;
    return std::pow((s + 0.055f) / 1.055f, 2.4f);
}

// WebGPU texture<->buffer copies require bytes-per-row to be a multiple of
// this. RGBA8 (4 B/pixel) at 1280 wide produces 5120 — already a multiple,
// but at e.g. 1281 wide we round up to 5376. Tracked as the padded row
// stride in the capture path.
static constexpr uint64_t WGPU_BYTES_PER_ROW_ALIGN = 256;



// computeMeshLocalVolumeQuantised moved to ViewportCore.cpp anon
// namespace (#84-n).

// Ray-AABB (slab) + ray-triangle (Möller-Trumbore). Used by raycast()
// AND by pickMeshLocalAt to refine the AABB-coarse surface hit into a
// real triangle hit — see pickMeshLocalAt's refinement block.

// Convert Qt's pixel-coord QPoint (event payload) to the Eigen::Vector2i
// we store in member fields. The cast is mechanical but isolating it as
// a helper keeps every event-handler site one line shorter.
#include <QPoint>
static inline Eigen::Vector2i toV2i(const QPoint& p) {
    return Eigen::Vector2i(p.x(), p.y());
}

// Slab method ray-AABB. inv_d is precomputed 1/dir per axis.

// rayAabbSlab moved to ViewportCore.cpp anon namespace (#84-t).

// Möller-Trumbore. Returns true on hit; t is in dir-units.
// rayTriMT moved to ViewportCore.cpp anon namespace (#84-t).

// -----------------------------------------------------------------------------
// Small helpers
// -----------------------------------------------------------------------------

static QString sv(WGPUStringView s) {
    if (!s.data) return QString();
    // WGPU_STRLEN sentinel == SIZE_MAX -> nul-terminated.
    const int len = (s.length == WGPU_STRLEN)
                        ? int(std::strlen(s.data))
                        : int(s.length);
    return QString::fromUtf8(s.data, len);
}

// createBufferWithData moved to ViewportCore (anon namespace) (#84-q).

// releaseWgpuModelGpuData moved to ViewportCore.cpp (IfcViewerCore now needs it).

// -----------------------------------------------------------------------------
// WGSL main pipeline — cross-mesh vertex pulling.
//
// We issue ONE draw() call per model per frame. The vertex shader binary-
// searches the prefix-sum table to find which visible-draw entry the current
// @builtin(vertex_index) belongs to, then manually fetches the index and the
// 12-byte packed vertex from storage buffers. This avoids the N-drawcalls-per-
// frame CPU overhead of per-mesh draws (which dominated on scenes with many
// unique meshes — wgpu-native overhead is ~5 µs/draw, so 27k draws = 135ms).
//
// Binary search cost is O(log N) per vertex, with N up to a few hundred
// thousand on dense scenes. Adjacent vertices in the same draw entry share
// the search result inside a warp, so memory-coherence keeps this cheap on
// GPU.
// -----------------------------------------------------------------------------

// MAIN_WGSL moved to ViewportCore.cpp (#84-k).

// Helper: build a WGPUStringView from a null-terminated C string literal.
static WGPUStringView svFromCStr(const char* s) {
    WGPUStringView v{};
    v.data   = s;
    v.length = std::strlen(s);
    return v;
}

// -----------------------------------------------------------------------------
// Construction / destruction
// -----------------------------------------------------------------------------

ViewportWindow::ViewportWindow(QWindow* parent)
    : QWindow(parent),
      core_(this),
      // Bind reference aliases to ViewportCore's storage so the
      // existing `device_` / `queue_` / … sites in this TU keep
      // working unchanged. Each reference goes away as its owning
      // render method moves into ViewportCore.
      instance_          (core_.instance_),
      adapter_           (core_.adapter_),
      device_            (core_.device_),
      queue_             (core_.queue_),
      surface_           (core_.surface_),
      surface_format_    (core_.surface_format_),
      surface_configured_(core_.surface_configured_),
      main_shader_module_       (core_.main_shader_module_),
      frame_bgl_                (core_.frame_bgl_),
      model_bgl_                (core_.model_bgl_),
      pipeline_layout_          (core_.pipeline_layout_),
      main_pipeline_            (core_.main_pipeline_),
      main_pipeline_transparent_(core_.main_pipeline_transparent_),
      depth_texture_      (core_.depth_texture_),
      depth_view_         (core_.depth_view_),
      depth_w_            (core_.depth_w_),
      depth_h_            (core_.depth_h_),
      msaa_color_texture_ (core_.msaa_color_texture_),
      msaa_color_view_    (core_.msaa_color_view_),
      msaa_w_             (core_.msaa_w_),
      msaa_h_             (core_.msaa_h_),
      hiz_shader_module_   (core_.hiz_shader_module_),
      hiz_bgl_             (core_.hiz_bgl_),
      hiz_pipeline_layout_ (core_.hiz_pipeline_layout_),
      hiz_pipeline_        (core_.hiz_pipeline_),
      hiz_uniform_buffer_  (core_.hiz_uniform_buffer_),
      hiz_bind_group_      (core_.hiz_bind_group_),
      hiz_resolve_texture_ (core_.hiz_resolve_texture_),
      hiz_resolve_view_    (core_.hiz_resolve_view_),
      hiz_resolve_w_       (core_.hiz_resolve_w_),
      hiz_resolve_h_       (core_.hiz_resolve_h_),
      hiz_padded_bpr_      (core_.hiz_padded_bpr_),
      hiz_pyramid_         (core_.hiz_pyramid_),
      hiz_mip_offset_      (core_.hiz_mip_offset_),
      hiz_mip_w_           (core_.hiz_mip_w_),
      hiz_mip_h_           (core_.hiz_mip_h_),
      hiz_vp_              (core_.hiz_vp_),
      hiz_valid_           (core_.hiz_valid_),
      hiz_reject_count_    (core_.hiz_reject_count_),
      hiz_trace_budget_    (core_.hiz_trace_budget_),
      hiz_enabled_         (core_.hiz_enabled_),
      edge_shader_module_   (core_.edge_shader_module_),
      edge_bgl_             (core_.edge_bgl_),
      edge_pipeline_layout_ (core_.edge_pipeline_layout_),
      edge_pipeline_        (core_.edge_pipeline_),
      edge_bind_group_      (core_.edge_bind_group_),
      edges_enabled_        (core_.edges_enabled_),
      pick_pipeline_(core_.pick_pipeline_),
      pool_           (core_.pool_),
      streaming_thread_(core_.streaming_thread_),
      streaming_frame_idx_(core_.streaming_frame_idx_),
      models_gpu_     (core_.models_gpu_),
      next_session_model_id_  (core_.next_session_model_id_),
      next_object_id_ (core_.next_object_id_),
      federated_false_origin_meters_(core_.federated_false_origin_meters_),
      wgpu_initialized_(core_.wgpu_initialized_),
      configured_w_   (core_.configured_w_),
      configured_h_   (core_.configured_h_),
      camera_target_  (core_.camera_target_),
      camera_distance_(core_.camera_distance_),
      projection_ortho_(core_.projection_ortho_),
      camera_yaw_deg_ (core_.camera_yaw_deg_),
      camera_pitch_deg_(core_.camera_pitch_deg_),
      camera_fov_y_deg_(core_.camera_fov_y_deg_),
      camera_near_    (core_.camera_near_),
      camera_far_     (core_.camera_far_),
      frame_uniform_buffer_(core_.frame_uniform_buffer_),
      frame_bind_group_    (core_.frame_bind_group_),
      selection_flags_buffer_  (core_.selection_flags_buffer_),
      selection_flags_capacity_(core_.selection_flags_capacity_),
      selection_flags_scratch_ (core_.selection_flags_scratch_),
      section_planes_  (core_.section_planes_),
      xray_alpha_cap_  (core_.xray_alpha_cap_),
      selection_  (core_.selection_),
      visibility_ (core_.visibility_),
      tracked_object_id_    (core_.tracked_object_id_),
      tracked_chunk_mid_    (core_.tracked_chunk_mid_),
      tracked_chunk_idx_    (core_.tracked_chunk_idx_),
      tracked_was_resident_ (core_.tracked_was_resident_),
      streaming_loads_this_frame_      (core_.streaming_loads_this_frame_),
      streaming_more_pending_          (core_.streaming_more_pending_),
      streaming_candidates_this_frame_ (core_.streaming_candidates_this_frame_),
      streaming_evictions_lru_this_frame_(core_.streaming_evictions_lru_this_frame_),
      streaming_evictions_pri_this_frame_(core_.streaming_evictions_pri_this_frame_),
      streaming_drained_this_frame_    (core_.streaming_drained_this_frame_),
      streaming_blocked_oom_this_frame_(core_.streaming_blocked_oom_this_frame_),
      streaming_debug_                 (core_.streaming_debug_),
      pending_screenshot_path_(core_.pending_screenshot_path_),
      pending_screenshot_quit_(core_.pending_screenshot_quit_),
      lod1_dbg_count_         (core_.lod1_dbg_count_),
      lod0_dbg_eligible_count_(core_.lod0_dbg_eligible_count_),
      lod0_dbg_no_lod1_count_ (core_.lod0_dbg_no_lod1_count_),
      lod1_dbg_tris_saved_    (core_.lod1_dbg_tris_saved_),
      initial_view_applied_   (core_.initial_view_applied_),
      min_pixel_radius_        (core_.min_pixel_radius_),
      motion_min_pixel_radius_ (core_.motion_min_pixel_radius_),
      lod1_pixel_threshold_    (core_.lod1_pixel_threshold_),
      cull_threads_enabled_    (core_.cull_threads_enabled_),
      prev_camera_target_      (core_.prev_camera_target_),
      prev_camera_distance_    (core_.prev_camera_distance_),
      prev_camera_yaw_deg_     (core_.prev_camera_yaw_deg_),
      prev_camera_pitch_deg_   (core_.prev_camera_pitch_deg_),
      has_prev_camera_         (core_.has_prev_camera_),
      last_cull_was_motion_    (core_.last_cull_was_motion_),
      bench_warm_streak_       (core_.bench_warm_streak_),
      bench_warm_frames_total_ (core_.bench_warm_frames_total_),
      bench_warm_done_         (core_.bench_warm_done_),
      bench_total_             (core_.bench_total_),
      bench_count_             (core_.bench_count_),
      bench_warmup_            (core_.bench_warmup_),
      bench_yaw_start_         (core_.bench_yaw_start_),
      bench_yaw_speed_         (core_.bench_yaw_speed_),
      bench_frame_ms_          (core_.bench_frame_ms_),
      last_visible_objects_    (core_.last_visible_objects_),
      last_visible_triangles_  (core_.last_visible_triangles_),
      last_sub_draws_          (core_.last_sub_draws_),
      bench_cull_ms_total_     (core_.bench_cull_ms_total_),
      bench_stream_ms_total_   (core_.bench_stream_ms_total_),
      bench_hiz_readback_ms_total_(core_.bench_hiz_readback_ms_total_),
      last_cull_ms_            (core_.last_cull_ms_),
      last_cull_compute_ms_    (core_.last_cull_compute_ms_),
      last_cull_upload_ms_     (core_.last_cull_upload_ms_),
      last_stream_ms_          (core_.last_stream_ms_),
      interactive_frame_count_ (core_.interactive_frame_count_) {
    // wgpu doesn't need a GL context; we just need a real native window
    // whose backing layer matches the GPU API wgpu will drive.
    //
    // - All platforms: OpenGLSurface gives us a hardware-rendering-ready
    //   native window (XCB/HWND/NSView). We never bind a GL context on
    //   top.
    //
    // - macOS specifically: we *don't* use QSurface::MetalSurface even
    //   though it'd be the "obvious" choice. Doing so makes Qt install
    //   its own CAMetalLayer subclass (QMetalLayer) on the NSView and
    //   keep an internal reference to it. Once wgpu-native (Rust) bridge-
    //   retains that layer and re-publishes its drawable pool in
    //   configureSurface, Qt's QMetalLayer winds up deallocated while
    //   Qt's internal reference still points at it, and the next Qt
    //   expose event aborts with:
    //     *** -[QMetalLayer displayLock]:
    //         message sent to deallocated instance ...
    //   With OpenGLSurface (which on macOS still gives us a layer-backed
    //   NSView), Qt doesn't install QMetalLayer; the
    //   MetalSurface_mac.mm bridge attaches a vanilla CAMetalLayer
    //   we fully own, and wgpu-native can do its lifetime gymnastics
    //   without stepping on Qt's bookkeeping.
    setSurfaceType(QSurface::OpenGLSurface);

    // Tool-refresh callback. Fires from core_'s applyStreamedChunk when a
    // freshly-arrived chunk filled in a mesh-local volume. The Volume
    // tool's HUD is the only consumer today; updateVolumeReadout is a
    // cheap no-op outside Volume mode.
    core_.on_volume_dirty_ = [this]() { updateVolumeReadout(); };
}

ViewportWindow::~ViewportWindow() {
    shutdown();
}

// ---- ViewportHost overrides ------------------------------------------------
//
// Scaffolding for Path-A. ViewportCore is empty today, so these don't
// yet have callers; the abstract methods exist only to define the
// boundary that subsequent commits will rely on. Each notification
// forwards to the existing Q_SIGNAL so bonsai-side consumers see no
// change.

// Platform-specific WGPUSurface creation. Called by ViewportCore::initWgpu
// (#84-l) once the wgpu instance is up. The platform branches reach into
// Qt's QNativeInterface to fish out the native window handle (X11
// Display + Window, Win32 HWND, or NSView wrapped in CAMetalLayer) and
// wrap each in the corresponding WGPUSurfaceSource* descriptor. The
// returned WGPUSurface is owned by the caller (ViewportCore stores it
// on `core_.surface_`).
WGPUSurface ViewportWindow::createSurface(WGPUInstance instance) {
    WGPUSurfaceDescriptor surface_desc = {};

#if defined(Q_OS_LINUX)
    const QString platform = QGuiApplication::platformName();
    if (platform == "xcb") {
#  if __has_include(<X11/Xlib.h>)
        auto* x11 = qApp->nativeInterface<QNativeInterface::QX11Application>();
        if (!x11 || !x11->display()) {
            Log::warn() << "Could not get X11 Display* from Qt";
            return nullptr;
        }
        WGPUSurfaceSourceXlibWindow xlib = {};
        xlib.chain.sType = WGPUSType_SurfaceSourceXlibWindow;
        xlib.display = x11->display();
        xlib.window  = static_cast<uint64_t>(winId());
        surface_desc.nextInChain = &xlib.chain;
        return wgpuInstanceCreateSurface(instance, &surface_desc);
#  else
        Log::warn() << "Built without Xlib headers; cannot create X11 surface";
        return nullptr;
#  endif
    } else if (platform == "wayland") {
        Log::warn() << "Wayland wgpu surface creation not yet wired (stage 1.5)";
        return nullptr;
    } else {
        Log::warn().noquote() << "Unsupported Qt platform for wgpu surface:" << platform;
        return nullptr;
    }
#elif defined(Q_OS_WIN)
    WGPUSurfaceSourceWindowsHWND hwndsrc = {};
    hwndsrc.chain.sType = WGPUSType_SurfaceSourceWindowsHWND;
    hwndsrc.hinstance = ::GetModuleHandleW(nullptr);
    hwndsrc.hwnd      = reinterpret_cast<void*>(static_cast<uintptr_t>(winId()));
    surface_desc.nextInChain = &hwndsrc.chain;
    return wgpuInstanceCreateSurface(instance, &surface_desc);
#elif defined(Q_OS_MAC)
    void* nsview = reinterpret_cast<void*>(static_cast<uintptr_t>(winId()));
    void* layer  = wgpu_macos_attach_metal_layer(nsview);
    if (!layer) {
        Log::warn() << "Could not attach CAMetalLayer to the Qt NSView";
        return nullptr;
    }
    WGPUSurfaceSourceMetalLayer metalsrc = {};
    metalsrc.chain.sType = WGPUSType_SurfaceSourceMetalLayer;
    metalsrc.layer = layer;
    surface_desc.nextInChain = &metalsrc.chain;
    return wgpuInstanceCreateSurface(instance, &surface_desc);
#else
    Log::warn() << "wgpu surface creation not yet wired for this platform";
    return nullptr;
#endif
}

void ViewportWindow::framebufferSize(int& width_px, int& height_px) const {
    const float r = float(QWindow::devicePixelRatio());
    width_px  = int(QWindow::width()  * r);
    height_px = int(QWindow::height() * r);
}

float ViewportWindow::dpr() const {
    return float(QWindow::devicePixelRatio());
}

void ViewportWindow::requestFrame() {
    requestUpdate();
}

void ViewportWindow::quit() {
    QCoreApplication::quit();
}

void ViewportWindow::onObjectPicked(uint32_t object_id) {
    emit objectPicked(object_id);
}

void ViewportWindow::onSurfacePickedInTool(int x_px, int y_px, int modifiers) {
    emit surfacePickedInTool(x_px, y_px, modifiers);
}

void ViewportWindow::onToolModeChanged(int tool_mode) {
    emit toolModeChanged(static_cast<ToolMode>(tool_mode));
}

void ViewportWindow::onToolBackspacePressed() {
    emit toolBackspacePressed();
}

void ViewportWindow::onFrameStats(const FrameStats& stats) {
    emit frameStatsUpdated(stats);
}

void ViewportWindow::encodeOverlaysInMainPass(WGPURenderPassEncoder pass,
                                              const OverlayFrame& frame) {
    // Highlight triangles + overlay lines / points — drawn inside the MSAA
    // pass so depth-test correctly hides them behind closer geometry.
    // (Marquee / labels run on the resolved surface; see
    // encodeOverlaysPostMain.)
    // NB: section-plane gizmos and the pivot indicator now draw from
    // ViewportCore::render via their shared renderers (desktop + web), so
    // they are NOT drawn here.
    overlays_.encodeHighlightTriangles(pass, frame);
    overlays_.encodeOverlayLines(pass, frame);
    overlays_.encodeOverlayPoints(pass, frame);
}

void ViewportWindow::encodeOverlaysPostMain(WGPUCommandEncoder enc,
                                            WGPUTextureView surface_view,
                                            const OverlayFrame& frame) {
    // NB: the corner axis gizmo draws from ViewportCore::render (shared
    // AxisIndicatorRenderer), just before this hook.
    overlays_.encodeMarquee(enc, surface_view, frame,
                            box_select_start_pos_,
                            box_select_current_pos_,
                            box_select_active_);
    overlays_.encodeLabels(enc, surface_view, frame);
}

void ViewportWindow::saveScreenshotRgba8(const std::string& path,
                                         const std::uint8_t* rgba,
                                         int w, int h) {
    // QImage takes a stride argument so it doesn't try to read past the
    // last row — wgpu's staging buffer was BGRA8 padded; core already
    // packed the rows tightly into rgba.
    //
    // Premultiplied, matching what the render pass leaves in the buffer: the
    // main blend accumulates alpha as One/OneMinusSrcAlpha, so colour there is
    // already scaled by coverage. Tagging it straight would wash out a
    // screenshot taken over a translucent background; at the default opaque
    // alpha the two formats describe the same bytes.
    QImage img(rgba, w, h, w * 4, QImage::Format_RGBA8888_Premultiplied);
    const QString qpath = QString::fromStdString(path);
    if (img.save(qpath, "PNG")) {
        Log::info() << "[wgpu] saved screenshot: "
                    << path << " (" << w << "x" << h << ")";
    } else {
        Log::warn() << "[wgpu] QImage::save failed for " << path;
    }
}

void ViewportWindow::setBackgroundColor(float r, float g, float b, float a) {
    core_.setBackgroundColor(r, g, b, a);
}

// -----------------------------------------------------------------------------
// Sidecar load + GPU upload
// -----------------------------------------------------------------------------

void ViewportWindow::queueLoadSidecar(const std::string& path) {
    if (wgpu_initialized_) {
        loadSidecar(path);
    } else {
        pending_sidecars_.push_back(path);
    }
}

uint32_t ViewportWindow::loadSidecar(const std::string& path_std) {
    // Internal implementation still uses Qt's path helpers (QDir tilde
    // expansion, QFile readability checks, QFileInfo for absolute resolve).
    // Bridging at the entry boundary keeps the public API Qt-free without
    // a full internal rewrite — those will move to std::filesystem when
    // ViewportCore lands (#84).
    const QString path = QString::fromStdString(path_std);
    if (!wgpu_initialized_) {
        Log::warn().noquote() << "loadSidecar called before wgpu init:" << path;
        return 0;
    }

    // Tilde expansion — shells handle this inside double-quoted args, but a
    // literal "~/..." from a launcher / command-line wouldn't. Cheap to do
    // here so the failure mode isn't "fopen returned ENOENT".
    QString resolved = path;
    if (resolved.startsWith("~/")) {
        resolved = QDir::homePath() + resolved.mid(1);
    }

    // Metadata-only read: mesh dict + instance dict + georef. Per-chunk
    // vertex/index bytes are deferred to the per-frame loader as chunks
    // become frustum-visible.
    auto meta_opt = readSidecarMetadata(resolved.toStdString());
    if (!meta_opt) {
        // Triage: distinguish missing file from magic/version mismatch by
        // peeking the header ourselves, so users know which to fix.
        QFile f(resolved);
        if (!f.exists()) {
            Log::warn().noquote() << "Sidecar not found:" << resolved;
        } else if (!f.open(QIODevice::ReadOnly)) {
            Log::warn().noquote() << "Sidecar unreadable:" << resolved
                                 << "(" << f.errorString() << ")";
        } else {
            uint32_t header[3] = { 0, 0, 0 };
            const qint64 got = f.read(reinterpret_cast<char*>(header), sizeof(header));
            if (got < qint64(sizeof(header))) {
                Log::warn().noquote() << "Sidecar truncated:" << resolved
                                     << "(only" << got << "bytes — expected ≥ 12)";
            } else if (header[0] != SIDECAR_MAGIC) {
                Log::warn().noquote().nospace()
                    << "Sidecar magic mismatch: " << resolved
                    << " — got 0x" << QString::number(header[0], 16)
                    << ", expected 0x" << QString::number(SIDECAR_MAGIC, 16)
                    << " (\"IFVW\")";
            } else if (header[1] != SIDECAR_VERSION) {
                Log::warn().noquote().nospace()
                    << "Sidecar schema mismatch: " << resolved
                    << " — file is v" << header[1]
                    << ", this build expects v" << SIDECAR_VERSION
                    << ". Re-bake the .ifc with a viewer at the matching schema.";
            } else if (header[2] != SIDECAR_ENDIAN) {
                Log::warn().noquote() << "Sidecar endianness mismatch:" << resolved
                                     << "(cross-platform load not supported)";
            } else {
                Log::warn().noquote() << "Sidecar metadata read failed past the header:" << resolved;
            }
        }
        return 0;
    }

    const uint32_t session_model_id = next_session_model_id_++;
    applyCachedModel(session_model_id, std::move(*meta_opt));
    return session_model_id;
}

void ViewportWindow::applyCachedModel(uint32_t session_model_id, StreamingSidecar metadata) {
    core_.applyCachedModel(session_model_id, std::move(metadata));
}

// -----------------------------------------------------------------------------
// Direct-IFC ingestion (mirrors GL ViewportWindow::uploadStreamedMesh /
// uploadStreamedInstance / finalizeModel). Streamer pushes transfer records; we stage
// them into a SidecarData-shaped buffer and commit at finalize via the
// same chunk planner the sidecar load uses.
// -----------------------------------------------------------------------------

// getOrCreateDirectStaging moved to ViewportCore (anon namespace) (#84-q).

void ViewportWindow::uploadStreamedMesh(const StreamedMesh& mesh) { core_.uploadStreamedMesh(mesh); }

void ViewportWindow::uploadStreamedInstance(const StreamedInstance& instance_record) {
    core_.uploadStreamedInstance(instance_record);
}

void ViewportWindow::finalizeModel(uint32_t session_model_id) { core_.finalizeModel(session_model_id); }

// removeModel / resetScene / hideModel / showModel /
// setFederatedFalseOrigin / setModelCoordinateOperation /
// setModelTransformation / recomposeAndUploadModel moved into
// ViewportCore (#84-f). The public-API entry points below forward
// so existing bonsai-side callers don't have to change.

void ViewportWindow::removeModel(uint32_t session_model_id)   { core_.removeModel(session_model_id); }
void ViewportWindow::resetScene()                     { core_.resetScene(); }
void ViewportWindow::hideModel(uint32_t session_model_id)     { core_.hideModel(session_model_id); }
void ViewportWindow::showModel(uint32_t session_model_id)     { core_.showModel(session_model_id); }

void ViewportWindow::setFederatedFalseOrigin(const Eigen::Matrix4d& m) {
    core_.setFederatedFalseOrigin(m);
}
void ViewportWindow::setModelCoordinateOperation(uint32_t session_model_id,
                                                 const Eigen::Matrix4d& m) {
    core_.setModelCoordinateOperation(session_model_id, m);
}
void ViewportWindow::setModelTransformation(uint32_t session_model_id,
                                            const Eigen::Matrix4d& m) {
    core_.setModelTransformation(session_model_id, m);
}
void ViewportWindow::recomposeAndUploadModel(uint32_t session_model_id) {
    core_.recomposeAndUploadModel(session_model_id);
}

bool ViewportWindow::findInstance(uint32_t object_id, InstanceLookup& out) const {
    return core_.findInstance(object_id, out);
}

bool ViewportWindow::firstGeometryPointWorldM(uint32_t session_model_id,
                                              Eigen::Vector3d& out) const {
    return core_.firstGeometryPointWorldM(session_model_id, out);
}

uint32_t ViewportWindow::modelObjectIdBase(uint32_t session_model_id) const {
    return core_.modelObjectIdBase(session_model_id);
}

void ViewportWindow::frameOnFederatedOrigin(uint32_t session_model_id,
                                                float max_distance_m) {
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end()) return;
    const ModelGpuData& model = it->second;
    if (model.instances.empty()) return;

    float mn[3] = {  std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity() };
    float mx[3] = { -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity() };
    for (const auto& inst : model.instances) {
        for (int a = 0; a < 3; ++a) {
            mn[a] = std::min(mn[a], inst.world_aabb_min[a]);
            mx[a] = std::max(mx[a], inst.world_aabb_max[a]);
        }
    }

    // The federated false origin sits at (0,0,0) in post-shift space
    // by construction (federated_false_origin_meters_ inverts it into
    // the instance compose); target it directly so the anchor point
    // we used in the guess is dead-centre in the view.
    camera_target_[0] = 0.0f;
    camera_target_[1] = 0.0f;
    camera_target_[2] = 0.0f;

    // Distance: same viewAll() fit math (bounding sphere radius pulled
    // just inside the tighter FOV with 1.10 padding), then clamped so
    // a model with one crazy-coord outlier vertex doesn't pull the
    // camera back so far that the real geometry becomes a pixel.
    const float dx = mx[0] - mn[0];
    const float dy = mx[1] - mn[1];
    const float dz = mx[2] - mn[2];
    const float radius = 0.5f * std::sqrt(dx * dx + dy * dy + dz * dz);
    if (radius > 1e-4f) {
        const float fovy_rad = qDegreesToRadians(camera_fov_y_deg_);
        const float tan_half = std::tan(fovy_rad * 0.5f);
        if (tan_half > 1e-6f) {
            const int   h          = std::max(configured_h_, 1);
            const float aspect     = float(std::max(configured_w_, 1)) / float(h);
            const float min_aspect = aspect < 1.0f ? aspect : 1.0f;
            const float fit_dist   = (radius / (tan_half * min_aspect)) * 1.10f;
            camera_distance_ = std::clamp(fit_dist, 0.1f, max_distance_m);
        }
    }

    Log::info().noquote().nospace()
        << "[wgpu] frameOnFederatedOrigin model=" << session_model_id
        << " distance=" << camera_distance_
        << " (cap=" << max_distance_m << "m, model radius=" << radius << ")";

    if (isExposed()) requestUpdate();
}

void ViewportWindow::flushPendingSidecarQueue() {
    while (!pending_sidecars_.empty()) {
        const std::string p = pending_sidecars_.front();
        pending_sidecars_.pop_front();
        loadSidecar(p);
    }
}

// -----------------------------------------------------------------------------
// Lifecycle
// -----------------------------------------------------------------------------

void ViewportWindow::exposeEvent(QExposeEvent* /*event*/) {
    if (!isExposed()) return;

    if (!wgpu_initialized_) {
        if (!initWgpu()) {
            Log::warn() << "wgpu init failed; viewport will not render";
            return;
        }
        wgpu_initialized_ = true;
        // Drain any sidecar paths queued before init; uploads run on the
        // now-valid device.
        flushPendingSidecarQueue();
    }

    const int w = int(width()  * devicePixelRatio());
    const int h = int(height() * devicePixelRatio());
    if (w > 0 && h > 0 && (w != configured_w_ || h != configured_h_)) {
        core_.configureSurface(w, h);
    }
    requestUpdate();
}

void ViewportWindow::resizeEvent(QResizeEvent* /*event*/) {
    if (!wgpu_initialized_ || !isExposed()) return;
    const int w = int(width()  * devicePixelRatio());
    const int h = int(height() * devicePixelRatio());
    if (w > 0 && h > 0) {
        core_.configureSurface(w, h);
        requestUpdate();
    }
}

bool ViewportWindow::event(QEvent* event) {
    if (event->type() == QEvent::UpdateRequest) {
        if (wgpu_initialized_ && surface_configured_) {
            render();
        }
        return true;
    }
    return QWindow::event(event);
}

// -----------------------------------------------------------------------------
// wgpu init: instance, surface, adapter, device, queue
// -----------------------------------------------------------------------------

bool ViewportWindow::initWgpu() {
    // ---- Env-var tuning + nav binding setup -----------------------------
    //
    // These mutate VW-side state (cull thresholds, hiz_enabled_, nav
    // button bindings) so they stay in the Qt-bound shell. ViewportCore
    // doesn't know about Qt::MouseButton enums or the still-in-VW cull
    // tuning fields. Once those move (later #84 steps + #85 for input)
    // this whole prologue migrates with them.
    if (const char* s = std::getenv("WGPU_MIN_PX")) {
        const float v = float(std::atof(s));
        if (v >= 0.0f) min_pixel_radius_ = v;
        Log::info().noquote().nospace()
            << "[wgpu cull] WGPU_MIN_PX=" << min_pixel_radius_;
    }
    if (const char* s = std::getenv("WGPU_MIN_PX_MOTION")) {
        const float v = float(std::atof(s));
        if (v >= 0.0f) motion_min_pixel_radius_ = v;
        Log::info().noquote().nospace()
            << "[wgpu cull] WGPU_MIN_PX_MOTION=" << motion_min_pixel_radius_;
    }
    if (const char* s = std::getenv("WGPU_STREAM_DEBUG")) {
        streaming_debug_ = (s[0] == '1');
        if (streaming_debug_) {
            Log::info().noquote() << "[wgpu stream] WGPU_STREAM_DEBUG=1 — per-frame "
                                 "[stream-debug] log enabled";
        }
    }
    if (const char* s = std::getenv("WGPU_HIZ")) {
        if (s[0] == '1') {
            hiz_enabled_ = true;
            Log::info() << "[wgpu] WGPU_HIZ=1 — HiZ occlusion culling enabled "
                       "(disabled by default; see task #58)";
        }
    }
    if (const char* s = std::getenv("WGPU_CULL_THREADS")) {
        cull_threads_enabled_ = (s[0] != '0');
        Log::info().noquote().nospace()
            << "[wgpu cull] WGPU_CULL_THREADS=" << s
            << " (parallelism " << (cull_threads_enabled_ ? "ON" : "OFF") << ")";
    }
    if (const char* s = std::getenv("WGPU_FLY_DEBUG")) {
        fly_debug_ = (s[0] == '1');
        if (fly_debug_) {
            Log::info() << "[wgpu fly] WGPU_FLY_DEBUG=1 — per-frame [fly] dt log enabled";
        }
    }
    // WGPU_NAV_PRESET is a dev override; apply it here. Otherwise leave the
    // preset alone — MainWindow applies the persisted Settings choice before the
    // window is exposed (initWgpu runs on the first expose), so forcing a
    // default here would clobber it and desync the applied preset from Settings.
    if (const char* nav_env = std::getenv("WGPU_NAV_PRESET")) {
        applyNavPreset(nav_env);
    }
    Log::info().noquote().nospace()
        << "[wgpu nav] orbit "
        << (orbit_button_ == Qt::RightButton ? "RMB" : "MMB")
        << (orbit_mods_ & Qt::ShiftModifier ? "+Shift" : "")
        << ", pan "
        << (pan_button_ == Qt::RightButton ? "RMB" : "MMB")
        << (pan_mods_ & Qt::ShiftModifier ? "+Shift" : "");

    // ---- ViewportCore handles instance/adapter/device/queue/pool/format -
    if (!core_.initWgpu(web_limits_)) return false;

    // ---- Pipelines + overlays (still VW-side; HiZ/edge/pick + overlay
    //      init haven't migrated yet) -------------------------------------
    if (!buildPipelines()) return false;
    if (!core_.buildHizPipeline()) return false;
    if (!core_.buildEdgePipeline()) return false;
    if (!overlays_.init(instance_, device_, queue_, surface_format_, SAMPLE_COUNT)) {
        Log::warn() << "OverlayRenderer init failed";
        return false;
    }
    if (!core_.buildPickPipeline()) return false;
    return true;
}

// -----------------------------------------------------------------------------
// Surface creation — platform-specific native handle plumbing.
// -----------------------------------------------------------------------------

#if defined(Q_OS_LINUX)
// QNativeInterface::QX11Application::display() returns Display*; pulling
// Xlib.h is fine on any system that has Qt6Gui built with xcb support
// (which already depends on libX11). We never look inside Display* — we
// only forward the pointer to wgpu as opaque.
#  if __has_include(<X11/Xlib.h>)
#    include <X11/Xlib.h>
#  endif
// QWaylandApplication::display() and ::surface() return wl_display* and
// wl_surface* (wayland-client-core.h). Same story.
#  if __has_include(<wayland-client-core.h>)
#    include <wayland-client-core.h>
#  endif
#elif defined(Q_OS_WIN)
// HINSTANCE for the surface descriptor. NOMINMAX + LEAN_AND_MEAN keep
// <windows.h>'s preprocessor pollution out of Eigen / std::min,max.
#  ifndef NOMINMAX
#    define NOMINMAX
#  endif
#  ifndef WIN32_LEAN_AND_MEAN
#    define WIN32_LEAN_AND_MEAN
#  endif
#  include <windows.h>
#endif

// Private bool createSurface() removed in #84-l — its body is now
// inside the public ViewportHost override createSurface(WGPUInstance).

// -----------------------------------------------------------------------------
// Surface (re)configure + render
// -----------------------------------------------------------------------------

// configureSurface moved to ViewportCore (#84-u).

// -----------------------------------------------------------------------------
// CPU frustum cull + per-mesh compaction
// -----------------------------------------------------------------------------
//
// Plane extraction follows the standard "rows of the VP matrix" derivation,
// adjusted for WebGPU's [0, 1] clip-space z (near plane = row 2, not row 3
// + row 2 as in GL). Planes are stored as (a, b, c, d) with the convention
// a*x + b*y + c*z + d >= 0 meaning the point is inside.
//
// VP is column-major float[16] (Qt convention): element [c*4 + r] is column
// c, row r. row(i) = (vp[0*4+i], vp[1*4+i], vp[2*4+i], vp[3*4+i]).

// extractFrustumPlanes + aabbInFrustum moved to CameraMath.h so
// both VW and ViewportCore can share without one #including the other.

// -----------------------------------------------------------------------------
// HiZ occlusion culling — depth resolve + downsample + readback + mip pyramid
// -----------------------------------------------------------------------------
//
// Single fragment shader does both the MSAA→single-sample resolve and the
// downsample to HiZ_BASE_W × hiz_resolve_h_ in one pass. For each output
// texel it loops over the corresponding source rect and takes max depth
// (= farthest projected z, conservative for occlusion). Sample 0 of the
// MSAA depth is used — slightly less conservative than max-of-samples but
// simpler and good enough for HiZ.
//
// The mip pyramid is max-reduced on CPU. Per-frame readback is small
// (256 × ~160 × 4 = ~160 KB) so the synchronous wgpuInstanceProcessEvents
// stall is well under a millisecond on every backend we care about.

// HIZ_WGSL moved to ViewportCore.cpp anon namespace (#84-r).

// -----------------------------------------------------------------------------
// Edge silhouette post-process (stage 9)
// -----------------------------------------------------------------------------
//
// Ports the GL renderEdgePass algorithm:
//   1. Sample MSAA depth (sample 0) at centre + 4 cardinal neighbours.
//   2. Linearise depth to view-space metres so the Laplacian is meaningful
//      across the entire depth range (raw [0,1] z is heavily non-linear —
//      a fixed threshold would only catch near-camera edges).
//   3. Threshold scales with depth (`u_threshold * c`) so a 4 mm gap reads
//      the same whether it's 0.5 m or 50 m away.
//   4. Multiplicative blend (Dst·src) with src = vec3(1 - edge). Strictly
//      darkens; never brightens.
//
// Constants u_scale=6.0 and u_threshold=0.004 are GL's tuned values;
// camera near/far are hard-coded to the viewport defaults (0.1 / 10000).
// They'll move to a small uniform when AppSettings ports over.

// EDGE_WGSL moved to ViewportCore.cpp anon namespace (#84-s).

// buildEdgePipeline moved to ViewportCore (#84-s).

// encodeEdgePass moved to ViewportCore (#84-s).

// setPivotIndicatorVisible moved to ViewportCore (drawn by the shared
// AxisIndicatorRenderer, so the visibility gate lives there too).
// releaseEdgeResources moved to ViewportCore (#84-s).

// -----------------------------------------------------------------------------
// Pick pipeline (stage 4)
// -----------------------------------------------------------------------------
//
// Same vertex pulling architecture as the main pipeline; reuses
// pipeline_layout_ so per-frame and per-model bind groups stay shared with
// the main draw. Differences are in the fragment (one R32UInt output) and
// the render target attachments (single-sample, surface-sized pick FBO).

// Pick + raycast forwarders. Bodies live in ViewportCore (#84-t); the
// public ViewportWindow API stays so bonsai's input + tool layer keeps
// linking unchanged.
uint32_t ViewportWindow::pickObjectAt(int x_pixels, int y_pixels,
                                      Eigen::Vector3f* normal_out) {
    return core_.pickObjectAt(x_pixels, y_pixels, normal_out);
}
bool ViewportWindow::pickSurfaceAt(int x_pixels, int y_pixels,
                                   uint32_t& object_id_out,
                                   Eigen::Vector3f& world_pos_out,
                                   Eigen::Vector3f& world_normal_out,
                                   float* aabb_radius_out) {
    return core_.pickSurfaceAt(x_pixels, y_pixels, object_id_out,
                               world_pos_out, world_normal_out, aabb_radius_out);
}
std::vector<uint32_t> ViewportWindow::picksInRect(int x, int y, int w, int h) {
    return core_.picksInRect(x, y, w, h);
}
bool ViewportWindow::pickMeshLocalAt(int x, int y, MeshLocalPick& out) {
    return core_.pickMeshLocalAt(x, y, out);
}
bool ViewportWindow::raycast(const float origin[3], const float dir[3],
                             RaycastHit& out) const {
    return core_.raycast(origin, dir, out);
}

// Slab-method ray-AABB intersection. Returns t_enter (the ray parameter at
// the first hit, clamped to >= 0 so origins inside the box land at t = 0)
// and the axis-aligned face normal at the entry: ±X / ±Y / ±Z depending on
// which slab dominated t_min. The face normal is what the section tool
// uses for surface-perpendicular cuts — for BIM geometry that's almost
// always axis-aligned (walls, slabs, columns) this matches the user's
// expectation; for diagonal or curved geometry it falls back to the
// closest of {±X, ±Y, ±Z}, which is still a usable cut direction.
// rayAABBHit moved to ViewportCore.cpp anon namespace (#84-t).

// picksInRect moved to ViewportCore (#84-t).

// pickSurfaceAt moved to ViewportCore (#84-t).

// -----------------------------------------------------------------------------
// Section cutting state
// -----------------------------------------------------------------------------

void ViewportWindow::toggleSectionTool() {
    section_tool_active_ = !section_tool_active_;
    Log::info().noquote() << "[wgpu section] tool"
                      << (section_tool_active_ ? "active" : "off");
    if (isExposed()) requestUpdate();
}

bool ViewportWindow::addSectionPlaneAtSurface(const Eigen::Vector3f& point, const Eigen::Vector3f& normal, float visual_radius) {
    return core_.addSectionPlaneAtSurface(point, normal, visual_radius);
}

void ViewportWindow::removeSectionPlane(int index) { core_.removeSectionPlane(index); }

void ViewportWindow::clearSectionPlanes() { core_.clearSectionPlanes(); }

void ViewportWindow::setOverlayLines(
        const std::vector<OverlayRenderer::LineGroup>& groups) {
    overlays_.setOverlayLines(groups);
    if (isExposed()) requestUpdate();
}

void ViewportWindow::setOverlayPoints(const std::vector<float>& world_xyz,
                                          float r, float g, float b, float a,
                                          float pixel_size,
                                          float stroke_r, float stroke_g,
                                          float stroke_b, float stroke_a,
                                          float stroke_extra) {
    overlays_.setOverlayPoints(world_xyz, r, g, b, a, pixel_size,
                               stroke_r, stroke_g, stroke_b, stroke_a,
                               stroke_extra);
    if (isExposed()) requestUpdate();
}

void ViewportWindow::setOverlayLabels(
        const std::vector<OverlayRenderer::Label>& labels) {
    overlays_.setOverlayLabels(labels);
    if (isExposed()) requestUpdate();
}

void ViewportWindow::setHudText(const std::string& text) {
    // OverlayRenderer still uses QString internally (Qt's QImage/QPainter
    // rasterizes the HUD text). Conversion at the boundary keeps the
    // public API Qt-free; OverlayRenderer's de-Qt comes later.
    overlays_.setHudText(QString::fromStdString(text));
    if (isExposed()) requestUpdate();
}

void ViewportWindow::setHighlightTriangles(const std::vector<float>& world_xyz,
                                               float r, float g, float b, float a) {
    overlays_.setHighlightTriangles(world_xyz, r, g, b, a);
    if (isExposed()) requestUpdate();
}

bool ViewportWindow::readbackMeshTriangles(uint32_t session_model_id, uint32_t mesh_id,
                                               MeshTriangles& out) const {
    auto mit = models_gpu_.find(session_model_id);
    if (mit == models_gpu_.end()) return false;
    const ModelGpuData& model = mit->second;
    if (mesh_id >= model.mesh_triangles_cache.size()) return false;
    const auto& src = model.mesh_triangles_cache[mesh_id];
    if (src.indices.empty() || src.positions.empty()) return false;
    // Copy out — callers iterate freely without worrying about lifetime
    // (streaming may evict a chunk and rebuild the shadow on next load).
    out = src;
    return true;
}

// pickMeshLocalAt moved to ViewportCore (#84-t).

void ViewportWindow::onAreaPick(int x_phys, int y_phys, bool alt) {
    if (!area_tool_) return;
    area_tool_->onPick(*this, x_phys, y_phys, alt);
    updateAreaHud();
}

bool ViewportWindow::meshLocalToGlobal(uint32_t object_id,
                                           const float mesh_local[3],
                                           double global_out[3]) const {
    // Find the instance via the per-model object_id_to_instance map.
    // Use the live map key (`session_model_id`) — see pickMeshLocalAt comment about
    // stale InstanceInfo::session_model_id from sidecar writes.
    for (const auto& [session_model_id, model] : models_gpu_) {
        auto it = model.object_id_to_instance.find(object_id);
        if (it == model.object_id_to_instance.end()) continue;
        const InstanceInfo& inst = model.instances[it->second];
        // CoordinateOperation · placement · local — gives the IFC's own
        // georeferenced world frame (ENH). Excludes FederatedFalseOrigin
        // and ModelTransformation, matching the GL meshLocalToGlobal
        // contract. Runs in double so large IFC placements don't lose
        // precision before the CoordinateOperation cancels them.
        using Mat4dCol = Eigen::Matrix<double, 4, 4, Eigen::ColMajor>;
        const Eigen::Matrix4d P =
            Eigen::Map<const Mat4dCol>(inst.placement_transformation);
        // static_cast (not `double(...)`) to dodge GCC 11's most-vexing-parse:
        // `Vector4d local(double(mesh_local[0]),…)` is otherwise read as a
        // function declaration of `local` whose parameter is `double mesh_local[0]`,
        // shadowing the outer `mesh_local` parameter.
        const Eigen::Vector4d local(static_cast<double>(mesh_local[0]),
                                    static_cast<double>(mesh_local[1]),
                                    static_cast<double>(mesh_local[2]),
                                    1.0);
        const Eigen::Vector3d global =
            (model.coordinate_operation_meters * P * local).head<3>();
        global_out[0] = global.x();
        global_out[1] = global.y();
        global_out[2] = global.z();
        return true;
    }
    return false;
}

// raycast moved to ViewportCore (#84-t).

void ViewportWindow::onLengthPick(int x_phys, int y_phys, bool alt) {
    if (!length_tool_) return;
    length_tool_->onPick(*this, x_phys, y_phys, alt);
}

void ViewportWindow::onLengthBackspace() {
    if (length_tool_) length_tool_->removeLastPoint(*this);
    // External listeners (bonsai's tool router) also want to know — the
    // GL viewport emits this on the same key path.
    emit toolBackspacePressed();
}

void ViewportWindow::updateAreaHud() {
    if (tool_mode_ != ToolMode::Area || !area_tool_) return;
    overlays_.setHudText(
        QStringLiteral("Area: %1 m²  (%2 tris)")
            .arg(area_tool_->totalArea(), 0, 'f', 4)
            .arg(area_tool_->triangleCount()));
    if (isExposed()) requestUpdate();
}

// |det(upper-left 3×3)| of a column-major 4×4 placement. Picks up
// mapped-item scale / mirror so a uniformly-scaled clone of a 1 m³ mesh
// reports its actual volume.
static double det3OfPlacement(const double M[16]) {
    const double m00 = M[0],  m10 = M[1],  m20 = M[2];
    const double m01 = M[4],  m11 = M[5],  m21 = M[6];
    const double m02 = M[8],  m12 = M[9],  m22 = M[10];
    return m00 * (m11 * m22 - m12 * m21)
         - m01 * (m10 * m22 - m12 * m20)
         + m02 * (m10 * m21 - m11 * m20);
}

// computeMeshLocalVolumeQuantised moved to ViewportCore.cpp anon namespace (#84-n).

void ViewportWindow::toggleAreaTool() {
    setToolMode(tool_mode_ == ToolMode::Area ? ToolMode::NoTool : ToolMode::Area);
}

void ViewportWindow::toggleLengthTool() {
    setToolMode(tool_mode_ == ToolMode::Length ? ToolMode::NoTool : ToolMode::Length);
}

void ViewportWindow::toggleVolumeTool() {
    setToolMode(tool_mode_ == ToolMode::Volume ? ToolMode::NoTool : ToolMode::Volume);
}

void ViewportWindow::setSelectedObjectId(uint32_t id) {
    if (id == 0) selection_.clear();
    else         selection_.replace(id);
    if (isExposed()) requestUpdate();
}

// Visibility ops now live in ViewportCore (shared with web); these stay as thin
// Qt-facing wrappers for the menu actions.
void ViewportWindow::hideSelectedElements()    { core_.hideSelected(); }
void ViewportWindow::isolateSelectedElements() { core_.isolateSelected(); }
void ViewportWindow::showAllElements()         { core_.showAll(); }

void ViewportWindow::invertElementVisibility() {
    // Compute the new hidden set: every live object_id in a visible model
    // that ISN'T currently hidden. Then swap. Done in two passes so we
    // don't mutate the set we're iterating over.
    std::vector<uint32_t> to_hide;
    to_hide.reserve(1024);
    for (const auto& [session_model_id, model] : models_gpu_) {
        if (model.hidden) continue;
        for (const InstanceInfo& inst : model.instances) {
            if (inst.object_id == 0) continue;
            if (!visibility_.isHidden(inst.object_id)) {
                to_hide.push_back(inst.object_id);
            }
        }
    }
    visibility_.clear();
    for (uint32_t id : to_hide) visibility_.hide(id);
    if (isExposed()) requestUpdate();
}

// cameraState moved to ViewportCore (#84-i).
ViewportWindow::CameraState ViewportWindow::cameraState() const {
    return core_.cameraState();
}

void ViewportWindow::setToolMode(ToolMode m) {
    if (tool_mode_ == m) return;
    tool_mode_ = m;
    emit toolModeChanged(m);
    // Always tear down the previous tool's overlay artefacts before
    // switching — easier than per-from-state branching, and the new
    // tool re-primes whatever it owns on its first update.
    if (area_tool_)   area_tool_->clear(*this);
    if (length_tool_) length_tool_->clear(*this);
    overlays_.setHudText(QString());
    overlays_.setOverlayLabels({});
    overlays_.setOverlayLines({});
    overlays_.setOverlayPoints({}, 0,0,0,0, 0, 0,0,0,0, 0);
    overlays_.setHighlightTriangles({}, 0, 0, 0, 0);

    switch (tool_mode_) {
    case ToolMode::NoTool:
        Log::info() << "[wgpu measure] tool off";
        break;
    case ToolMode::Volume:
        Log::info() << "[wgpu measure] volume tool — pick / marquee objects, Esc to exit";
        overlays_.setHudText(QStringLiteral("Volume: 0.0000 m³  (0 objects)"));
        updateVolumeReadout();
        break;
    case ToolMode::Area:
        if (!area_tool_) area_tool_ = std::make_unique<AreaMeasurement>();
        Log::info() << "[wgpu measure] area tool — LMB pick coplanar patch, Alt+LMB single tri, click again to remove, Esc exits";
        overlays_.setHudText(QStringLiteral("Area: 0.0000 m²  (0 tris)"));
        break;
    case ToolMode::Length:
        if (!length_tool_) length_tool_ = std::make_unique<LengthMeasurement>();
        Log::info() << "[wgpu measure] length tool — LMB add point, Backspace remove last, Esc exits";
        overlays_.setHudText(QStringLiteral("Length tool: click first point"));
        break;
    }
    if (isExposed()) requestUpdate();
}

// volumeOfObjects / volumesPerObject moved to ViewportCore (#84-j).
double ViewportWindow::volumeOfObjects(
        const std::vector<uint32_t>& object_ids) const {
    return core_.volumeOfObjects(object_ids);
}
std::vector<std::pair<uint32_t, double>>
ViewportWindow::volumesPerObject(
        const std::vector<uint32_t>& object_ids) const {
    return core_.volumesPerObject(object_ids);
}

void ViewportWindow::updateVolumeReadout() {
    if (tool_mode_ != ToolMode::Volume) return;

    const auto& sel = selection_.selectionIds();
    if (sel.empty()) {
        overlays_.setHudText(QString());
        overlays_.setOverlayLabels({});
        return;
    }

    const std::vector<uint32_t> ids(sel.begin(), sel.end());
    const auto per_obj = volumesPerObject(ids);

    // Per-object label cap. Each label allocates one wgpu texture +
    // bind group on first sight; rendering thousands of unique
    // "X.XXXX m³" strings drives the label-texture cache off a cliff
    // and the QPainter rasterise per label dominates the click cost.
    // The HUD total stays correct above the cap — only the per-object
    // overlay labels are suppressed. 200 fits a normal multi-object
    // selection and keeps both memory and per-frame draw count bounded.
    static constexpr size_t kMaxPerObjectLabels = 200;
    const bool show_labels = per_obj.size() <= kMaxPerObjectLabels;

    double total = 0.0;
    std::vector<OverlayRenderer::Label> labels;
    if (show_labels) labels.reserve(per_obj.size());
    for (const auto& [oid, v] : per_obj) {
        total += v;
        if (!show_labels) continue;
        // O(1) instance lookup via object_id_to_instance, then read the
        // world AABB from the cached InstanceInfo directly — same data
        // computeObjectAabb's linear scan would have produced for the
        // first matching instance. For label placement at the AABB
        // centre this is identical-looking; only the rare multi-
        // representation object_id sees a slightly smaller union.
        for (const auto& [session_model_id, model] : models_gpu_) {
            auto it = model.object_id_to_instance.find(oid);
            if (it == model.object_id_to_instance.end()) continue;
            const InstanceInfo& inst = model.instances[it->second];
            OverlayRenderer::Label lbl;
            lbl.world_pos[0] = (inst.world_aabb_min[0] + inst.world_aabb_max[0]) * 0.5f;
            lbl.world_pos[1] = (inst.world_aabb_min[1] + inst.world_aabb_max[1]) * 0.5f;
            lbl.world_pos[2] = (inst.world_aabb_min[2] + inst.world_aabb_max[2]) * 0.5f;
            lbl.text = QString::number(v, 'f', 4) + QStringLiteral(" m³");
            labels.push_back(std::move(lbl));
            break;
        }
    }

    QString hud = QStringLiteral("Volume: %1 m³  (%2 object%3)")
        .arg(total, 0, 'f', 4)
        .arg(per_obj.size())
        .arg(per_obj.size() == 1 ? "" : "s");
    if (!show_labels) {
        hud += QStringLiteral("\n(per-object labels hidden above %1)")
            .arg(kMaxPerObjectLabels);
    }
    overlays_.setHudText(hud);
    overlays_.setOverlayLabels(labels);
}

// projectWorldToLogicalScreen moved to SectionGizmoRenderer (its only users,
// the section hit-test + drag, now live in ViewportCore).

// Section-gizmo hit-test + drag-to-move now live in ViewportCore (shared with
// web, using SectionGizmoRenderer::hitTest). The mouse handlers call
// core_.hitTestSectionGizmo / beginSectionDrag / updateSectionDrag / endSectionDrag.

// buildHizPipeline moved to ViewportCore (#84-r).

// ensureHizTextures moved to ViewportCore (#84-r).

// releaseHizResources moved to ViewportCore (#84-r).

// encodeHizResolve moved to ViewportCore (#84-r).

// startHizMap moved to ViewportCore (#84-r).

// drainHizReadbacks moved to ViewportCore (#84-r).

// aabbOccludedByHiz moved to ViewportCore (#84-r).

void ViewportWindow::setBenchmarkFrames(int frames) {
    bench_total_    = std::max(0, frames);
    bench_count_    = 0;
    bench_yaw_start_ = camera_yaw_deg_;
    bench_warm_streak_       = 0;
    bench_warm_frames_total_ = 0;
    bench_frame_ms_.clear();
    bench_frame_ms_.reserve(size_t(bench_total_));
    if (isExposed() && bench_total_ > 0) requestUpdate();
}

// cullModelCpuCompute moved to ViewportCore (#84-p).

// cullModelCpuUpload moved to ViewportCore (#84-p).

void ViewportWindow::render() {
    // The Qt-side prelude that has to run before each frame: fpsIntegrate
    // (fly-mode WASD camera step) and the isExposed() guard. After that,
    // the wgpu work is all in core_.render().
    if (!isExposed()) return;
    fpsIntegrate();
    core_.render();
}

// -----------------------------------------------------------------------------
// Pipeline + bind-group layouts (built once after init)
// -----------------------------------------------------------------------------

// buildPipelines moved to ViewportCore (#84-k).
bool ViewportWindow::buildPipelines() { return core_.buildPipelines(); }

// ensureSelectionFlagsBuffer moved to ViewportCore (#84-k).
void ViewportWindow::ensureSelectionFlagsBuffer() { core_.ensureSelectionFlagsBuffer(); }

// uploadSelectionFlagsIfDirty moved to ViewportCore (#84-k).
void ViewportWindow::uploadSelectionFlagsIfDirty() { core_.uploadSelectionFlagsIfDirty(); }

void ViewportWindow::buildModelBindGroup(ModelGpuData& model) { core_.buildModelBindGroup(model); }

// buildChunkBindGroup moved to ViewportCore (#84-n).

// makeChunkRequest moved to ViewportCore (folded into loadChunkBytesAndUploadGpu) (#84-n).

// applyStreamedChunk moved to ViewportCore (#84-n).

// loadChunkBytesAndUploadGpu moved to ViewportCore (#84-n).

// unloadChunk moved to ViewportCore (#84-n).

void ViewportWindow::driveStreamingLoads() { core_.driveStreamingLoads(); }

// -----------------------------------------------------------------------------
// Depth attachment
// -----------------------------------------------------------------------------

// ensureDepthTexture moved to ViewportCore (#84-r).

// releaseDepthTexture moved to ViewportCore (#84-r).

// ensureMsaaColorTexture moved to ViewportCore (#84-r).

// releaseMsaaColorTexture moved to ViewportCore (#84-r).

// -----------------------------------------------------------------------------
// Camera + frame uniforms
// -----------------------------------------------------------------------------
//
// Orbit camera around `camera_target_`. World +Z up (BIM convention). Yaw is
// rotation about Z (positive = anticlockwise looking down +Z); pitch is
// elevation above the XY plane.

// orbitEye moved to ViewportCore (its last ViewportWindow uses — fly-mode step
// + mouse-look — now go through ViewportCore::flyMove / flyLook).

// Shared camera-math helper. Every site that needs (view, proj) for cull,
// streaming projection, pick, or render uniforms calls this so the
// projection_ortho_ toggle and the near-vertical up-vector switch land
// identically everywhere.
// buildViewProj moved to ViewportCore (#84-h).

// updateFrameUniforms moved to ViewportCore (#84-m).

// computeSceneAabb moved to ViewportCore (#84-h).

// setCamera body moved to ViewportCore (#84-i). VW keeps the wrapper
// because the auto-viewAll suppression flag (initial_view_applied_)
// still lives on the Qt-bound side — it's the first-model-loaded
// hook that ViewportCore doesn't own yet.
void ViewportWindow::setCamera(float tx, float ty, float tz,
                               float dist, float yaw_deg, float pitch_deg) {
    core_.setCamera(tx, ty, tz, dist, yaw_deg, pitch_deg);
    initial_view_applied_ = true;
}

// viewAll / frameAabb / computeObjectAabb moved to ViewportCore (#84-i).

void ViewportWindow::viewAll() { core_.viewAll(); }
bool ViewportWindow::viewModels(const std::vector<uint32_t>& session_model_ids) {
    return core_.viewModels(session_model_ids);
}
void ViewportWindow::frameAabb(const float mn[3], const float mx[3], float padding) {
    core_.frameAabb(mn, mx, padding);
}
bool ViewportWindow::computeObjectAabb(uint32_t id, float mn[3], float mx[3]) const {
    return core_.computeObjectAabb(id, mn, mx);
}
bool ViewportWindow::computeObjectAabb(uint32_t id,
                                       Eigen::Vector3f& mn, Eigen::Vector3f& mx) const {
    return core_.computeObjectAabb(id, mn, mx);
}

void ViewportWindow::focusOnSelectedObject() {
    if (fps_mode_) return;
    // Shared math lives in ViewportCore::frameSelection (also the web path).
    if (!core_.frameSelection()) {
        Log::info() << "[wgpu] focus: no object selected / no AABB available";
    }
}

// setStandardView / toggleProjection / cameraString moved to ViewportCore (#84-i).
void ViewportWindow::setStandardView(float yaw_deg, float pitch_deg) {
    core_.setStandardView(yaw_deg, pitch_deg);
}
void ViewportWindow::toggleProjection()        { core_.toggleProjection(); }
std::string ViewportWindow::cameraString() const { return core_.cameraString(); }

void ViewportWindow::enterFpsMode() {
    if (fps_mode_) return;
    fps_mode_ = true;
    fps_keys_held_.clear();
    fps_press_center_ = Eigen::Vector2i(width() / 2, height() / 2);
    fps_ignore_next_mouse_move_ = true;
    fps_last_tick_.start();
    setCursor(Qt::BlankCursor);
    QCursor::setPos(mapToGlobal(QPoint(fps_press_center_.x(), fps_press_center_.y())));
    Log::info() << "[wgpu] fly mode active — WASD/QE to move, Shift to boost, Esc to exit";
    if (isExposed()) requestUpdate();
}

void ViewportWindow::exitFpsMode() {
    if (!fps_mode_) return;
    fps_mode_ = false;
    fps_keys_held_.clear();
    setCursor(Qt::ArrowCursor);
    Log::info() << "[wgpu] fly mode off";
    if (isExposed()) requestUpdate();
}

void ViewportWindow::fpsIntegrate() {
    if (!fps_mode_ || fps_keys_held_.empty()) return;

    const qint64 elapsed_ns = fps_last_tick_.nsecsElapsed();
    fps_last_tick_.restart();
    if (elapsed_ns <= 0) return;
    // Clamp dt ceiling so a long stall doesn't warp the camera by a frame's
    // worth of speed (matches GL fps_move_speed_'s 0.1s clamp).
    float dt = float(double(elapsed_ns) / 1e9);
    if (dt > 0.1f) dt = 0.1f;

    // Fly-camera math lives in ViewportCore (shared with the web path).
    core_.flyMove(
        fps_keys_held_.count(Qt::Key_W) != 0, fps_keys_held_.count(Qt::Key_S) != 0,
        fps_keys_held_.count(Qt::Key_D) != 0, fps_keys_held_.count(Qt::Key_A) != 0,
        fps_keys_held_.count(Qt::Key_E) != 0, fps_keys_held_.count(Qt::Key_Q) != 0,
        fps_keys_held_.count(Qt::Key_Shift) != 0, dt);
}

// chunkScreenAreaPx moved to ViewportCore (#84-h).

static Qt::MouseButton toQtBtn(ViewportCore::MouseBtn b) {
    switch (b) {
        case ViewportCore::MouseBtn::Left:   return Qt::LeftButton;
        case ViewportCore::MouseBtn::Middle: return Qt::MiddleButton;
        case ViewportCore::MouseBtn::Right:  return Qt::RightButton;
    }
    return Qt::LeftButton;
}
static Qt::KeyboardModifiers toQtMod(ViewportCore::NavMod m) {
    switch (m) {
        case ViewportCore::NavMod::Plain:  return Qt::NoModifier;
        case ViewportCore::NavMod::Shift: return Qt::ShiftModifier;
        case ViewportCore::NavMod::Ctrl:  return Qt::ControlModifier;
        case ViewportCore::NavMod::Alt:   return Qt::AltModifier;
    }
    return Qt::NoModifier;
}

void ViewportWindow::applyNavPreset(const char* name) {
    // The preset table lives in ViewportCore (shared with web). Map its bindings
    // to the Qt types the mouse handlers compare against.
    core_.setNavPreset(name);
    const auto& b = core_.navBindings();
    orbit_button_  = toQtBtn(b.orbit);   orbit_mods_  = toQtMod(b.orbit_mod);
    pan_button_    = toQtBtn(b.pan);      pan_mods_    = toQtMod(b.pan_mod);
    select_button_ = toQtBtn(b.select);  select_mods_ = toQtMod(b.select_mod);
}

void ViewportWindow::setBackfaceCulling(bool enabled) {
    core_.setBackfaceCulling(enabled);
}

// -----------------------------------------------------------------------------
// One-shot framebuffer capture → PNG
// -----------------------------------------------------------------------------
//
// WebGPU's buffer<->texture copies require bytes-per-row to be a multiple of
// 256. For an RGBA8 (or BGRA8) source the natural row stride width*4 rarely
// satisfies that, so we round up and strip the padding when assembling the
// QImage.
//
// Capture flow:
//   1. After the render pass + before present, encode a copyTextureToBuffer
//      into a CPU-mappable buffer.
//   2. Submit, then wgpuBufferMapAsync (CallbackMode_AllowProcessEvents) and
//      spin wgpuInstanceProcessEvents until the callback signals completion.
//   3. Strip per-row padding into a QImage; convert BGRA↔RGBA if needed;
//      save PNG; optionally quit the app.

#include <QImage>
#include <QCoreApplication>

void ViewportWindow::captureNextFrameToPng(const std::string& path, bool quit_after) { core_.captureNextFrameToPng(path, quit_after); }

// -----------------------------------------------------------------------------
// Mouse navigation — orbit, pan, zoom
// -----------------------------------------------------------------------------
//
// LMB drag → orbit (yaw/pitch). MMB drag → pan (target moves in the camera's
// screen-space plane). Wheel → zoom (camera_distance_ multiplies). Pitch is
// clamped just shy of ±90° to avoid the gimbal-flip at the poles.
//
// No nav-preset awareness yet (Blender/Rhino/Revit bindings come later); we
// don't have selection bound, so LMB is free to orbit.

#include <QMouseEvent>
#include <QWheelEvent>

void ViewportWindow::mousePressEvent(QMouseEvent* event) {
    // In fly mode mouse-look is the only nav; clicking exits fly to match
    // Blender behaviour, then the click also acts as the orbit-mode click.
    if (fps_mode_) {
        exitFpsMode();
        // fall through to normal handling
    }

    nav_active_button_ = event->button();
    nav_last_pos_      = toV2i(event->position().toPoint());
    nav_press_pos_     = nav_last_pos_;
    nav_dragged_       = false;

    // Section tool: claim a plain-LMB press if it lands on one of the
    // plane gizmos' arrows. Suppresses nav classification so the drag
    // doesn't also rotate the camera.
    if (section_tool_active_
        && event->button() == Qt::LeftButton
        && event->modifiers() == Qt::NoModifier) {
        const Eigen::Vector2i lp = toV2i(event->position().toPoint());
        const int hit = core_.hitTestSectionGizmo(lp.x(), lp.y());
        if (hit >= 0 && core_.beginSectionDrag(hit, lp.x(), lp.y())) {
            core_.setSelectedSectionPlane(hit);  // clicking a gizmo selects it
            nav_drag_kind_ = NavDrag::Inactive;
            Log::info().noquote().nospace()
                << "[wgpu section] drag start: plane=" << hit;
            return;
        }
    }

    // Classify the drag against the active nav preset. LMB stays free for
    // selection in every preset (pick on release-without-drag). The modifier
    // is captured at press time so a mid-drag Shift release doesn't switch
    // axes (matches GL ViewportWindow behaviour).
    nav_drag_kind_ = NavDrag::Inactive;
    const auto mods = event->modifiers();
    if (event->button() == orbit_button_
        && (mods & Qt::KeyboardModifierMask) == orbit_mods_) {
        nav_drag_kind_ = NavDrag::Orbit;
        core_.setPivotIndicatorVisible(true);  // hidden again on release
    } else if (event->button() == pan_button_
            && (mods & Qt::KeyboardModifierMask) == pan_mods_) {
        nav_drag_kind_ = NavDrag::Pan;
        core_.setPivotIndicatorVisible(true);
    } else if (event->button() == select_button_
            && !section_tool_active_
            && tool_mode_ != ToolMode::Area
            && tool_mode_ != ToolMode::Length
            && nav_drag_kind_ == NavDrag::Inactive) {
        // Arm marquee box-select. Plain / Shift / Ctrl on the select button
        // (Shift/Ctrl = add/remove) without a tool intercepting the click; if
        // the cursor never moves past the threshold this stays armed-only and
        // the release falls through to single-pick.
        box_select_armed_      = true;
        box_select_active_     = false;
        box_select_start_pos_  = nav_press_pos_;
        box_select_current_pos_ = nav_press_pos_;
        box_select_press_mods_ = mods;
    }
}

void ViewportWindow::mouseReleaseEvent(QMouseEvent* event) {
    if (core_.sectionDragActive() && event->button() == Qt::LeftButton) {
        core_.endSectionDrag();
        nav_active_button_   = Qt::NoButton;
        return;
    }
    // Marquee finalisation: only commit when the drag actually became
    // active (cursor moved past threshold). Press-time mods decide the
    // set op so a mid-drag Shift release doesn't flip the behaviour.
    if (box_select_armed_ && event->button() == select_button_) {
        const bool was_active = box_select_active_;
        box_select_armed_  = false;
        box_select_active_ = false;
        if (was_active) {
            const float dpr = float(devicePixelRatio());
            const int x0 = int(std::min(box_select_start_pos_.x(),
                                        box_select_current_pos_.x()) * dpr);
            const int y0 = int(std::min(box_select_start_pos_.y(),
                                        box_select_current_pos_.y()) * dpr);
            const int x1 = int(std::max(box_select_start_pos_.x(),
                                        box_select_current_pos_.x()) * dpr);
            const int y1 = int(std::max(box_select_start_pos_.y(),
                                        box_select_current_pos_.y()) * dpr);
            const auto ids = picksInRect(x0, y0, x1 - x0, y1 - y0);
            const auto mods = box_select_press_mods_;
            if (mods & Qt::ShiftModifier) {
                for (uint32_t id : ids) selection_.add(id);
                Log::info().noquote().nospace()
                    << "[wgpu marquee] +add " << ids.size() << " object_ids";
            } else if (mods & Qt::ControlModifier) {
                for (uint32_t id : ids) selection_.remove(id);
                Log::info().noquote().nospace()
                    << "[wgpu marquee] -remove " << ids.size() << " object_ids";
            } else {
                selection_.clear();
                for (uint32_t id : ids) selection_.add(id);
                Log::info().noquote().nospace()
                    << "[wgpu marquee] replace " << ids.size() << " object_ids";
            }
            nav_active_button_ = Qt::NoButton;
            nav_drag_kind_     = NavDrag::Inactive;
            updateVolumeReadout();
            requestUpdate();
            return;
        }
        // armed but not active → fall through to single-click pick below.
    }
    if (event->button() == nav_active_button_) {
        // LMB-click without drag → pick the object under the cursor and
        // route through the selection state. Shift = add, Ctrl = remove,
        // no modifier = replace. Empty-space click clears.
        if (event->button() == select_button_ && !nav_dragged_) {
            const Eigen::Vector2i pos = toV2i(event->position().toPoint());
            const int px = int(pos.x() * devicePixelRatio());
            const int py = int(pos.y() * devicePixelRatio());

            // Section tool intercepts plain LMB clicks (with no modifier)
            // to drop a plane at the picked surface. Shift/Ctrl still go
            // through selection so the user can manipulate the existing
            // set while the tool is open.
            if (section_tool_active_
                && event->modifiers() == Qt::NoModifier) {
                uint32_t hit_id = 0;
                Eigen::Vector3f hit_pos, hit_normal;
                float hit_radius = 0.0f;
                if (pickSurfaceAt(px, py, hit_id, hit_pos, hit_normal,
                                  &hit_radius)) {
                    // Pad the gizmo a bit beyond the AABB so the cut reads
                    // as a "cap" rather than ending right at the boundary.
                    addSectionPlaneAtSurface(hit_pos, hit_normal,
                                             hit_radius * 1.5f);
                } else {
                    Log::info().noquote() << "[wgpu section] click missed (no surface)";
                }
                nav_active_button_ = Qt::NoButton;
                nav_drag_kind_     = NavDrag::Inactive;
                core_.setPivotIndicatorVisible(false);
                return;
            }

            // Area tool: plain LMB resolves to (instance, triangle) and
            // accumulates the coplanar patch; Alt+LMB skips BFS for a
            // single-triangle accumulate. Re-clicking inside a previously
            // accumulated patch removes it. Shift/Ctrl fall through to
            // selection so the user can still manage selection state.
            if (tool_mode_ == ToolMode::Area
                && (event->modifiers() == Qt::NoModifier
                 || event->modifiers() == Qt::AltModifier)) {
                const bool alt = (event->modifiers() & Qt::AltModifier) != 0;
                onAreaPick(px, py, alt);
                emit surfacePickedInTool(px, py, int(event->modifiers()));
                nav_active_button_ = Qt::NoButton;
                nav_drag_kind_     = NavDrag::Inactive;
                core_.setPivotIndicatorVisible(false);
                return;
            }

            // Length tool: plain LMB appends a world-space pick point;
            // the readout adapts to the running count (laser / distance
            // / angle / polygon). Shift/Ctrl fall through to selection.
            if (tool_mode_ == ToolMode::Length
                && (event->modifiers() == Qt::NoModifier
                 || event->modifiers() == Qt::AltModifier)) {
                const bool alt = (event->modifiers() & Qt::AltModifier) != 0;
                onLengthPick(px, py, alt);
                emit surfacePickedInTool(px, py, int(event->modifiers()));
                nav_active_button_ = Qt::NoButton;
                nav_drag_kind_     = NavDrag::Inactive;
                core_.setPivotIndicatorVisible(false);
                return;
            }

            const uint32_t id = pickObjectAt(px, py);
            const auto mods = event->modifiers();
            if (id == 0) {
                if (!(mods & (Qt::ShiftModifier | Qt::ControlModifier))) {
                    selection_.clear();
                }
                Log::info().noquote() << "[wgpu pick] miss";
            } else if (mods & Qt::ControlModifier) {
                selection_.remove(id);
                Log::info().noquote().nospace()
                    << "[wgpu pick] -remove object_id=" << id;
            } else if (mods & Qt::ShiftModifier) {
                selection_.add(id);
                Log::info().noquote().nospace()
                    << "[wgpu pick] +add object_id=" << id;
            } else {
                selection_.replace(id);
                Log::info().noquote().nospace()
                    << "[wgpu pick] replace object_id=" << id;
            }
            // Notify external listeners (bonsai mirrors picks into
            // SessionState). Emit even on miss (id == 0) so a clear
            // round-trips, matching the GL backend's emit-active-id
            // semantics.
            emit objectPicked(id);
            // Track this object's chunk for the disappear-diagnostic.
            // Enumerate EVERY (model, chunk) the object's instances land in:
            // an IFC object can have multiple representations (visual,
            // structural, MEP …) which can split across chunks. Tracking
            // only the first found leads to confused diagnostics when the
            // visual you SEE disappear lives in a chunk we never tracked.
            if (id != 0) {
                tracked_object_id_ = id;
                tracked_chunk_idx_ = SIZE_MAX;  // legacy "primary" slot
                tracked_chunk_mid_ = 0;
                std::set<std::pair<uint32_t, size_t>> seen;
                Log::info().noquote().nospace()
                    << "[track] object " << id << " — enumerating chunks:";
                for (auto& [session_model_id, model] : models_gpu_) {
                    for (const auto& inst : model.instances) {
                        if (inst.object_id != id) continue;
                        if (inst.mesh_id >= model.mesh_chunk_idx.size()) continue;
                        const size_t ci = model.mesh_chunk_idx[inst.mesh_id];
                        if (!seen.insert({session_model_id, ci}).second) continue;
                        const auto& chunk = model.chunks[ci];
                        Log::info().noquote().nospace()
                            << "  model " << session_model_id << " chunk " << ci
                            << "  inst_aabb "
                            << QString::number(inst.world_aabb_max[0] - inst.world_aabb_min[0], 'f', 1)
                            << "×"
                            << QString::number(inst.world_aabb_max[1] - inst.world_aabb_min[1], 'f', 1)
                            << "×"
                            << QString::number(inst.world_aabb_max[2] - inst.world_aabb_min[2], 'f', 1) << "m"
                            << "  chunk_aabb "
                            << QString::number(chunk.aabb_max[0] - chunk.aabb_min[0], 'f', 1) << "×"
                            << QString::number(chunk.aabb_max[1] - chunk.aabb_min[1], 'f', 1) << "×"
                            << QString::number(chunk.aabb_max[2] - chunk.aabb_min[2], 'f', 1) << "m"
                            << "  resident=" << (chunk.is_resident ? "Y" : "N");
                        // First hit becomes the "primary" slot the
                        // eviction watcher uses. Good enough until we wire
                        // a multi-chunk watcher.
                        if (tracked_chunk_idx_ == SIZE_MAX) {
                            tracked_chunk_mid_    = session_model_id;
                            tracked_chunk_idx_    = ci;
                            tracked_was_resident_ = chunk.is_resident;
                        }
                    }
                }
                if (tracked_chunk_idx_ == SIZE_MAX) {
                    Log::info() << "  (object_id not matched to any instance)";
                }
            } else {
                tracked_object_id_ = 0;
                tracked_chunk_idx_ = SIZE_MAX;
            }
            updateVolumeReadout();
            requestUpdate();
        }
        nav_active_button_ = Qt::NoButton;
        nav_drag_kind_     = NavDrag::Inactive;
        // Drag is over — hide the pivot indicator without afterglow.
        core_.setPivotIndicatorVisible(false);
    }
}

void ViewportWindow::mouseMoveEvent(QMouseEvent* event) {
    // Section drag intercepts the move handler entirely: the orbit/pan
    // classification already declined this drag in mousePressEvent, so all
    // we have to do is slide the plane along its normal.
    if (core_.sectionDragActive()) {
        const Eigen::Vector2i pos = toV2i(event->position().toPoint());
        core_.updateSectionDrag(pos.x(), pos.y());
        return;
    }

    // Marquee box-select: track the current cursor and promote to active
    // once the press has moved past the manhattan threshold. Active
    // marquee triggers requestUpdate every frame the cursor moves so the
    // rect re-renders.
    if (box_select_armed_) {
        const Eigen::Vector2i pos = toV2i(event->position().toPoint());
        box_select_current_pos_ = pos;
        if (!box_select_active_) {
            const Eigen::Vector2i diff = pos - box_select_start_pos_;
            if (std::abs(diff.x()) + std::abs(diff.y())
                >= kBoxSelectThresholdPx) {
                box_select_active_ = true;
            }
        }
        if (box_select_active_) requestUpdate();
        return;
    }

    // Fly-mode mouse-look: turn the camera in place (eye stays put).
    // The orbit fields (camera_target_/distance/yaw/pitch) are still our
    // single source of truth — but to interpret yaw/pitch as the camera's
    // *look* direction (FPS-style, not orbit-style) we have to snap
    // camera_target_ to a new position whenever yaw/pitch change so
    // orbitEye() resolves to the same eye we had before. Otherwise eye
    // orbits the (unchanged) target and the camera circles the room.
    if (fps_mode_) {
        if (fps_ignore_next_mouse_move_) {
            fps_ignore_next_mouse_move_ = false;
            return;
        }
        const Eigen::Vector2i pos = toV2i(event->position().toPoint());
        const int dx = pos.x() - fps_press_center_.x();
        const int dy = pos.y() - fps_press_center_.y();

        // Mouse-look math (turn-in-place) lives in ViewportCore, shared with
        // the web pointer-lock path.
        core_.flyLook(float(dx), float(dy));

        fps_ignore_next_mouse_move_ = true;
        QCursor::setPos(mapToGlobal(QPoint(fps_press_center_.x(), fps_press_center_.y())));
        requestUpdate();
        return;
    }

    if (nav_active_button_ == Qt::NoButton) return;

    const Eigen::Vector2i pos = toV2i(event->position().toPoint());
    const int dx = pos.x() - nav_last_pos_.x();
    const int dy = pos.y() - nav_last_pos_.y();
    nav_last_pos_ = pos;

    // Promote to drag past 3 px so a wobbly click doesn't get reclassified
    // (otherwise an LMB click drifts a few pixels and never registers as a
    // pick on release).
    if (!nav_dragged_) {
        const int adx = std::abs(pos.x() - nav_press_pos_.x());
        const int ady = std::abs(pos.y() - nav_press_pos_.y());
        if (adx + ady > 3) nav_dragged_ = true;
    }

    if (nav_drag_kind_ == NavDrag::Orbit) {
        // Orbit math lives in ViewportCore so desktop + web can't drift.
        core_.orbitBy(float(dx), float(dy));
    } else if (nav_drag_kind_ == NavDrag::Pan) {
        // Pan needs the viewport height to size world-units-per-pixel.
        core_.panBy(float(dx), float(dy), height());
    }
}

void ViewportWindow::keyPressEvent(QKeyEvent* event) {
    const auto mods = event->modifiers();
    const int  key  = event->key();

    // Fly-mode keys come first so WASD/QE/Shift don't leak to shortcuts.
    if (fps_mode_) {
        if (key == Qt::Key_Escape && !event->isAutoRepeat()) {
            exitFpsMode();
            return;
        }
        switch (key) {
        case Qt::Key_W: case Qt::Key_A: case Qt::Key_S: case Qt::Key_D:
        case Qt::Key_Q: case Qt::Key_E: case Qt::Key_Shift:
            if (!event->isAutoRepeat()) {
                const bool was_empty = fps_keys_held_.empty();
                fps_keys_held_.insert(key);
                if (was_empty) fps_last_tick_.restart();
                // ALWAYS kick the render loop, not just on first key.
                // If Shift was pressed first (Shift-alone doesn't move →
                // fpsIntegrate exits early without requesting another
                // frame, so the loop dies), and Q is pressed next, the
                // old "only on was_empty" trigger missed it and Q never
                // integrated. Re-arming requestUpdate per keypress is
                // free (Qt coalesces) and resolves the deadlock.
                requestUpdate();
            }
            return;
        default: break;
        }
    }

    // Bonsai shortcuts (mirror MainWindow.cpp bind_shortcut table):
    //   H        — hide selected
    //   Shift+H  — isolate selected
    //   Alt+H    — show all (clear hidden set)
    //   Shift+F  — enter fly mode (Esc exits)
    // Visibility + X-ray math lives in ViewportCore (shared with web).
    if (key == Qt::Key_H && mods == Qt::AltModifier) { core_.showAll();        return; }
    if (key == Qt::Key_X && mods == Qt::AltModifier && !event->isAutoRepeat()) {
        core_.toggleXray(); return;
    }
    if (key == Qt::Key_H && mods == Qt::ShiftModifier) { core_.isolateSelected(); return; }
    if (key == Qt::Key_H && mods == Qt::NoModifier)    { core_.hideSelected();    return; }
    if (key == Qt::Key_F && mods == Qt::ShiftModifier && !event->isAutoRepeat()) {
        enterFpsMode();
        return;
    }

    // Section tool. K toggles the tool; Shift+K clears all planes. When
    // the tool is active, click adds a plane at the surface (handled in
    // mouseReleaseEvent) or selects the gizmo under the cursor, Esc
    // deactivates, Del/Backspace removes the selected plane (or the most
    // recent one when nothing is selected). Mirrors GL ViewportWindow +
    // Bonsai's bind_shortcut(K / Shift+K) bindings.
    if (key == Qt::Key_K && !event->isAutoRepeat()) {
        if (mods == Qt::ShiftModifier) {
            clearSectionPlanes();
        } else if (mods == Qt::NoModifier) {
            toggleSectionTool();
        }
        return;
    }
    if (section_tool_active_ && !event->isAutoRepeat()) {
        if (key == Qt::Key_Escape) {
            toggleSectionTool();
            return;
        }
        if ((key == Qt::Key_Delete || key == Qt::Key_Backspace)
            && !section_planes_.empty()) {
            // Delete the selected plane; fall back to the most recent one when
            // nothing is selected.
            const int selected = core_.selectedSectionPlane();
            removeSectionPlane(selected >= 0 ? selected
                                             : int(section_planes_.size()) - 1);
            return;
        }
    }

    // Measurement tools. V toggles Volume, A toggles Area; Esc exits
    // whichever tool is active. Mirrors GL ViewportWindow + Bonsai's
    // bind_shortcut(V) / bind_shortcut(A).
    if (key == Qt::Key_V && mods == Qt::NoModifier && !event->isAutoRepeat()) {
        setToolMode(tool_mode_ == ToolMode::Volume ? ToolMode::NoTool
                                                   : ToolMode::Volume);
        return;
    }
    if (key == Qt::Key_A && mods == Qt::NoModifier && !event->isAutoRepeat()) {
        setToolMode(tool_mode_ == ToolMode::Area ? ToolMode::NoTool
                                                 : ToolMode::Area);
        return;
    }
    if (key == Qt::Key_L && mods == Qt::NoModifier && !event->isAutoRepeat()) {
        setToolMode(tool_mode_ == ToolMode::Length ? ToolMode::NoTool
                                                   : ToolMode::Length);
        return;
    }
    if (tool_mode_ == ToolMode::Length
        && (key == Qt::Key_Backspace || key == Qt::Key_Delete)
        && !event->isAutoRepeat()) {
        onLengthBackspace();
        return;
    }
    if (tool_mode_ != ToolMode::NoTool && key == Qt::Key_Escape
        && !event->isAutoRepeat()) {
        setToolMode(ToolMode::NoTool);
        return;
    }

    // GL-parity viewport hotkeys.
    if (key == Qt::Key_F && mods == Qt::NoModifier && !event->isAutoRepeat()) {
        focusOnSelectedObject();
        return;
    }
    if (key == Qt::Key_Home && !event->isAutoRepeat()) {
        viewAll();
        return;
    }
    if (key == Qt::Key_P && mods == Qt::NoModifier && !event->isAutoRepeat()) {
        toggleProjection();
        return;
    }
    if (key == Qt::Key_C && !(mods & Qt::ControlModifier)) {
        Log::info() << "--camera " << cameraString();
        return;
    }
    // Standard axis-aligned views: X/Y/Z look from +axis, Shift+X/Y/Z from
    // negative side. Top/bottom use pitch ±90°; buildViewProj's up-vector
    // switch keeps lookAt non-degenerate at the poles.
    if ((key == Qt::Key_X || key == Qt::Key_Y || key == Qt::Key_Z)
        && (mods == Qt::NoModifier || mods == Qt::ShiftModifier)
        && !event->isAutoRepeat()) {
        const bool neg = (mods & Qt::ShiftModifier);
        using SV = ViewportCore::StandardView;
        switch (key) {
        case Qt::Key_X: core_.setStandardView(neg ? SV::Back   : SV::Front); break;
        case Qt::Key_Y: core_.setStandardView(neg ? SV::Left   : SV::Right); break;
        case Qt::Key_Z: core_.setStandardView(neg ? SV::Bottom : SV::Top);   break;
        }
        return;
    }

    QWindow::keyPressEvent(event);
}

void ViewportWindow::keyReleaseEvent(QKeyEvent* event) {
    if (fps_mode_ && !event->isAutoRepeat()) {
        fps_keys_held_.erase(event->key());
    }
    QWindow::keyReleaseEvent(event);
}

void ViewportWindow::wheelEvent(QWheelEvent* event) {
    const float notches = float(event->angleDelta().y()) / 120.0f;
    // In fly mode, the wheel adjusts fps_move_speed_ (Blender / GL
    // convention). Up = faster (×1.25 per notch), down = slower (×0.8).
    // Zooming would re-aim the orbit pivot and yank speed (if it were
    // distance-scaled) — neither belongs in a free-fly camera.
    if (fps_mode_) {
        core_.flyAdjustSpeed(notches);  // shared: x1.25/notch, clamped
        Log::info().noquote().nospace()
            << "[wgpu] fly speed: " << QString::number(core_.flySpeed(), 'f', 2) << " m/s";
        return;
    }
    // Orbit mode: zoom in/out around the pivot (math in ViewportCore).
    core_.dollyBy(notches);
    // Pivot afterglow on wheel — visible for 600 ms so the user can see
    // what they're zooming around without holding a drag.
    core_.setPivotIndicatorVisible(true, 600);
}

void ViewportWindow::shutdown() {
    // VW-only resources first — these depend on core_'s device_ being
    // alive, so they must be released before core_.shutdown() releases it.
    core_.releaseDepthTexture();
    core_.releaseMsaaColorTexture();
    core_.releaseHizResources();
    core_.releaseEdgeResources();
    overlays_.destroy();
    core_.releasePickResources();

    // Core owns the rest: streaming thread, models, pool, frame/selection
    // buffers, pipelines/shaders/layouts, queue/device/adapter/surface/
    // instance.
    core_.shutdown();
}
