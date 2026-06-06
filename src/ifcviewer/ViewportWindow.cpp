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


// Forward declaration — defined below alongside updateFrameUniforms. Used
// by render() to extract camera/frustum state without duplicating the math.
static Eigen::Vector3f orbitEye(const float target[3], float dist,
                          float yaw_deg, float pitch_deg);

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

static bool rayAabbSlab(const float ro[3], const float inv_d[3],
                        const float bmin[3], const float bmax[3]) {
    float tmin = 0.0f, tmax = std::numeric_limits<float>::infinity();
    for (int i = 0; i < 3; ++i) {
        const float t1 = (bmin[i] - ro[i]) * inv_d[i];
        const float t2 = (bmax[i] - ro[i]) * inv_d[i];
        tmin = std::max(tmin, std::min(t1, t2));
        tmax = std::min(tmax, std::max(t1, t2));
    }
    return tmax >= tmin && tmax >= 0.0f;
}

// Möller-Trumbore. Returns true on hit; t is in dir-units.
static bool rayTriMT(const float ro[3], const float rd[3],
                     const float v0[3], const float v1[3], const float v2[3],
                     float& t_out) {
    constexpr float EPS = 1e-7f;
    const float e1[3] = {v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]};
    const float e2[3] = {v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]};
    const float h[3]  = {
        rd[1]*e2[2] - rd[2]*e2[1],
        rd[2]*e2[0] - rd[0]*e2[2],
        rd[0]*e2[1] - rd[1]*e2[0]
    };
    const float a = e1[0]*h[0] + e1[1]*h[1] + e1[2]*h[2];
    if (a > -EPS && a < EPS) return false;
    const float f = 1.0f / a;
    const float s[3] = {ro[0]-v0[0], ro[1]-v0[1], ro[2]-v0[2]};
    const float u = f * (s[0]*h[0] + s[1]*h[1] + s[2]*h[2]);
    if (u < 0.0f || u > 1.0f) return false;
    const float q[3] = {
        s[1]*e1[2] - s[2]*e1[1],
        s[2]*e1[0] - s[0]*e1[2],
        s[0]*e1[1] - s[1]*e1[0]
    };
    const float v = f * (rd[0]*q[0] + rd[1]*q[1] + rd[2]*q[2]);
    if (v < 0.0f || u + v > 1.0f) return false;
    const float t = f * (e2[0]*q[0] + e2[1]*q[1] + e2[2]*q[2]);
    if (t <= EPS) return false;
    t_out = t;
    return true;
}

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

// Allocate a wgpu buffer of `size_bytes` with the given usage, and upload
// `data` into it via the queue. Returns nullptr when size_bytes == 0 (wgpu
// rejects zero-sized buffer creation). `label` is informational; it shows up
// in validation messages when something goes wrong.
static WGPUBuffer createBufferWithData(WGPUDevice device, WGPUQueue queue,
                                       const void* data, size_t size_bytes,
                                       WGPUBufferUsage usage,
                                       const char* label) {
    if (size_bytes == 0) return nullptr;

    WGPUBufferDescriptor desc = {};
    desc.size  = uint64_t(size_bytes);
    desc.usage = usage | WGPUBufferUsage_CopyDst;
    if (label) {
        desc.label.data   = label;
        desc.label.length = std::strlen(label);
    }
    WGPUBuffer buf = wgpuDeviceCreateBuffer(device, &desc);
    if (buf && data) {
        wgpuQueueWriteBuffer(queue, buf, 0, data, size_bytes);
    }
    return buf;
}

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
      hiz_shader_module_   (core_.hiz_shader_module_),
      hiz_bgl_             (core_.hiz_bgl_),
      hiz_pipeline_layout_ (core_.hiz_pipeline_layout_),
      hiz_pipeline_        (core_.hiz_pipeline_),
      edge_shader_module_   (core_.edge_shader_module_),
      edge_bgl_             (core_.edge_bgl_),
      edge_pipeline_layout_ (core_.edge_pipeline_layout_),
      edge_pipeline_        (core_.edge_pipeline_),
      pick_pipeline_(core_.pick_pipeline_),
      pool_           (core_.pool_),
      streaming_thread_(core_.streaming_thread_),
      streaming_frame_idx_(core_.streaming_frame_idx_),
      models_gpu_     (core_.models_gpu_),
      next_model_id_  (core_.next_model_id_),
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
      background_color_(core_.background_color_),
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
      lod1_dbg_count_         (core_.lod1_dbg_count_),
      lod0_dbg_eligible_count_(core_.lod0_dbg_eligible_count_),
      lod0_dbg_no_lod1_count_ (core_.lod0_dbg_no_lod1_count_),
      lod1_dbg_tris_saved_    (core_.lod1_dbg_tris_saved_) {
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

void ViewportWindow::setBackgroundColor(float r, float g, float b, float a) {
    background_color_ = {r, g, b, a};
    if (isExposed()) requestUpdate();
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
    auto meta_opt = readSidecarMetadataOnly(resolved.toStdString());
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

    const uint32_t mid = next_model_id_++;
    applyCachedModel(mid, std::move(*meta_opt));
    return mid;
}

void ViewportWindow::applyCachedModel(uint32_t model_id,
                                          StreamingSidecar metadata) {
    if (!device_ || !queue_) {
        Log::warn() << "applyCachedModel without an initialised device";
        return;
    }

    // Replace any existing state for this id.
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        releaseWgpuModelGpuData(it->second, pool_);
        models_gpu_.erase(it);
    }

    ModelGpuData m;
    m.vertex_bytes   = metadata.vertex_total_bytes;
    m.index_count    = uint32_t(metadata.index_total_count);
    m.mesh_count     = uint32_t(metadata.meta.meshes.size());
    m.instance_count = uint32_t(metadata.meta.instances.size());
    m.streaming_file_path             = metadata.file_path;
    m.streaming_vertex_section_offset = metadata.vertex_section_offset;
    m.streaming_index_section_offset  = metadata.index_section_offset;

    // ---- Spatial chunk plan ----------------------------------------------
    // Sort meshes by world-space centroid (mean of their instances' AABB
    // centres), then greedy-pack into chunks ≤ WGPU_CHUNK_VERTEX_BYTES_LIMIT.
    // Each chunk's AABB ends up tight rather than spanning the whole model,
    // so the distance-based streaming evictor can meaningfully distinguish
    // chunks. Per-mesh layout within a chunk is the spatial-sort order;
    // the loader scatter-gathers from each mesh's sidecar offsets.
    const size_t n_meshes = metadata.meta.meshes.size();
    m.mesh_chunk_idx.assign(n_meshes, 0);
    m.mesh_chunk_local_base_vertex.assign(n_meshes, 0);
    m.mesh_chunk_local_ebo_first_u32.assign(n_meshes, 0);
    m.mesh_chunk_local_lod1_first_u32.assign(n_meshes, 0);

    // Per-mesh centroid = mean of its instances' world AABB centres.
    // Meshes with no instances stay at (0,0,0) — they're dead weight but
    // still need a chunk slot for layout consistency.
    std::vector<float>    mesh_cx(n_meshes, 0.0f),
                          mesh_cy(n_meshes, 0.0f),
                          mesh_cz(n_meshes, 0.0f);
    std::vector<uint32_t> mesh_inst_count(n_meshes, 0);
    for (const auto& inst : metadata.meta.instances) {
        if (inst.mesh_id >= n_meshes) continue;
        mesh_cx[inst.mesh_id] += 0.5f * (inst.world_aabb_min[0] + inst.world_aabb_max[0]);
        mesh_cy[inst.mesh_id] += 0.5f * (inst.world_aabb_min[1] + inst.world_aabb_max[1]);
        mesh_cz[inst.mesh_id] += 0.5f * (inst.world_aabb_min[2] + inst.world_aabb_max[2]);
        ++mesh_inst_count[inst.mesh_id];
    }
    for (size_t i = 0; i < n_meshes; ++i) {
        if (mesh_inst_count[i] > 0) {
            const float inv = 1.0f / float(mesh_inst_count[i]);
            mesh_cx[i] *= inv; mesh_cy[i] *= inv; mesh_cz[i] *= inv;
        }
    }

    // Chunk planning: sort meshes by 3D Morton code over centroids, then
    // greedy-pack into chunks ≤ WGPU_CHUNK_VERTEX_BYTES_LIMIT. Each mesh
    // ends up in exactly one chunk.
    std::vector<std::vector<uint32_t>> chunk_mesh_ids;
    std::vector<uint32_t>              instance_to_chunk;
    instance_to_chunk.assign(metadata.meta.instances.size(), 0);
    {
        std::vector<uint32_t> sorted_mesh_ids = ChunkPlanner::sortMeshIdsByMorton(
            n_meshes, mesh_cx, mesh_cy, mesh_cz, mesh_inst_count);
        std::vector<uint32_t> mesh_vertex_count;
        mesh_vertex_count.reserve(n_meshes);
        for (size_t i = 0; i < n_meshes; ++i) {
            mesh_vertex_count.push_back(metadata.meta.meshes[i].vertex_count);
        }
        chunk_mesh_ids = ChunkPlanner::greedyPackChunks(
            sorted_mesh_ids, mesh_vertex_count,
            INSTANCED_VERTEX_STRIDE_BYTES,
            WGPU_CHUNK_VERTEX_BYTES_LIMIT);
        // Derive instance_to_chunk via mesh_id → chunk lookup table.
        std::vector<uint32_t> mesh_to_chunk(n_meshes, 0);
        for (size_t ci = 0; ci < chunk_mesh_ids.size(); ++ci) {
            for (uint32_t mi : chunk_mesh_ids[ci]) mesh_to_chunk[mi] = uint32_t(ci);
        }
        for (size_t i = 0; i < metadata.meta.instances.size(); ++i) {
            const uint32_t mi = metadata.meta.instances[i].mesh_id;
            if (mi < n_meshes) instance_to_chunk[i] = mesh_to_chunk[mi];
        }
    }

    std::vector<uint32_t> chunk_instance_count(chunk_mesh_ids.size(), 0);
    for (size_t i = 0; i < instance_to_chunk.size(); ++i) {
        const uint32_t ci = instance_to_chunk[i];
        if (ci < chunk_instance_count.size()) ++chunk_instance_count[ci];
    }

    // ---- Allocate per-chunk state. NO pool slices yet (chunks are
    // non-resident); the per-frame loader brings them in as cull marks
    // them visible.
    m.chunks.resize(chunk_mesh_ids.size());
    // Per-chunk per-mesh chunk-local offsets. Built during the chunk
    // construction loop, consumed by the post-loop per-instance array
    // population. Under spatial bucketing the same mesh_id can land in
    // multiple chunks at different offsets, so this can't be a per-mesh
    // global — it has to be per-(chunk, mesh).
    struct MeshLocal { uint32_t base_vertex; uint32_t ebo_first; uint32_t lod1_first; };
    std::vector<std::unordered_map<uint32_t, MeshLocal>>
        chunk_mesh_offsets(chunk_mesh_ids.size());
    for (size_t ci = 0; ci < chunk_mesh_ids.size(); ++ci) {
        ModelGpuData::Chunk& c = m.chunks[ci];
        c.mesh_ids    = std::move(chunk_mesh_ids[ci]);
        c.is_resident = false;                              // streaming

        // Walk this chunk's meshes in chunk-local layout order, computing
        // each mesh's chunk-local base_vertex / ebo_first_u32 and the
        // chunk's aggregate vertex/index totals. LOD1 indices (if any
        // mesh has them baked) get a second pass and pack AFTER all the
        // LOD0 indices in the chunk's index slice — so a single slice
        // carries both LODs and cull picks per-instance by chunk-local
        // u32 offset.
        uint32_t chunk_local_v = 0;
        uint32_t chunk_local_i = 0;
        for (uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = metadata.meta.meshes[mi];
            m.mesh_chunk_idx[mi]                 = uint32_t(ci);
            m.mesh_chunk_local_base_vertex[mi]   = chunk_local_v;
            m.mesh_chunk_local_ebo_first_u32[mi] = chunk_local_i;
            chunk_mesh_offsets[ci][mi] = MeshLocal{chunk_local_v, chunk_local_i, 0};
            chunk_local_v += mesh.vertex_count;
            chunk_local_i += mesh.index_count;
        }
        uint32_t chunk_local_lod1 = 0;
        for (uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = metadata.meta.meshes[mi];
            if (mesh.lod1_index_count == 0) continue;
            m.mesh_chunk_local_lod1_first_u32[mi] = chunk_local_i + chunk_local_lod1;
            chunk_mesh_offsets[ci][mi].lod1_first = chunk_local_i + chunk_local_lod1;
            chunk_local_lod1 += mesh.lod1_index_count;
        }
        c.vertex_count     = chunk_local_v;
        c.vertex_byte_size = uint64_t(chunk_local_v) * INSTANCED_VERTEX_STRIDE_BYTES;
        c.index_count      = chunk_local_i + chunk_local_lod1;
        c.lod1_index_count = chunk_local_lod1;

        // Small per-chunk buffers, allocated upfront so cull can write into
        // them. visible_draws_buffer cap = chunk's instance count (worst-
        // case all visible, one entry each — LOD doesn't double-count).
        const size_t chunk_inst = std::max<size_t>(chunk_instance_count[ci], 1);
        const size_t draws_bytes = chunk_inst * sizeof(ModelGpuData::VisibleDrawGpu);
        const size_t ps_bytes    = (chunk_inst + 1) * sizeof(uint32_t);

        WGPUBufferDescriptor vd_desc = {};
        vd_desc.size  = std::max<uint64_t>(draws_bytes, 16);
        vd_desc.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        vd_desc.label = svFromCStr("model.chunk.visible_draws");
        c.visible_draws_buffer   = wgpuDeviceCreateBuffer(device_, &vd_desc);
        c.visible_draws_capacity = chunk_inst;
        m.vram_bytes_ssbo += vd_desc.size;

        WGPUBufferDescriptor ps_desc = {};
        ps_desc.size  = std::max<uint64_t>(ps_bytes, 16);
        ps_desc.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        ps_desc.label = svFromCStr("model.chunk.prefix_sums");
        c.prefix_sums_buffer   = wgpuDeviceCreateBuffer(device_, &ps_desc);
        c.prefix_sums_capacity = chunk_inst + 1;
        m.vram_bytes_ssbo += ps_desc.size;

        WGPUBufferDescriptor mu_desc = {};
        mu_desc.size  = 16;
        mu_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        mu_desc.label = svFromCStr("model.chunk.uniform");
        c.per_chunk_uniform = wgpuDeviceCreateBuffer(device_, &mu_desc);
        m.vram_bytes_ssbo += 16;

        c.visible_draws_scratch.reserve(chunk_inst);
        c.prefix_sums_scratch.reserve(chunk_inst + 1);
    }

    // Index section is NOT loaded upfront. Each chunk's index slice will
    // be range-read alongside its vertex bytes in loadChunkBytesAndUploadGpu.
    // Eliminates the 1.5+ GB upfront index VRAM cost that was the binding
    // OOM constraint on real scenes.

    // MeshGpu storage (per-mesh quant basis).
    std::vector<MeshGpu> mesh_gpu;
    mesh_gpu.reserve(metadata.meta.meshes.size());
    for (const auto& mi : metadata.meta.meshes) {
        MeshGpu mg = {};
        mg.aabb_min[0] = mi.local_aabb_min[0];
        mg.aabb_min[1] = mi.local_aabb_min[1];
        mg.aabb_min[2] = mi.local_aabb_min[2];
        mg.aabb_max[0] = mi.local_aabb_max[0];
        mg.aabb_max[1] = mi.local_aabb_max[1];
        mg.aabb_max[2] = mi.local_aabb_max[2];
        mesh_gpu.push_back(mg);
    }
    const size_t mesh_storage_bytes = mesh_gpu.size() * sizeof(MeshGpu);
    m.mesh_storage = createBufferWithData(
        device_, queue_,
        mesh_gpu.data(), mesh_storage_bytes,
        WGPUBufferUsage_Storage,
        "model.mesh_storage");
    m.vram_bytes_ssbo += mesh_storage_bytes;

    // InstanceGpu storage. Rebase object_ids globally (same as non-streaming).
    const uint32_t object_id_base = next_object_id_;
    uint32_t max_local_id = 0;
    std::vector<InstanceGpu> inst_gpu;
    inst_gpu.reserve(metadata.meta.instances.size());
    for (auto& ic : metadata.meta.instances) {
        if (ic.object_id > max_local_id) max_local_id = ic.object_id;
        ic.object_id = object_id_base + ic.object_id;
        InstanceGpu ig = {};
        std::memcpy(ig.transform, ic.transform, sizeof(ig.transform));
        ig.object_id            = ic.object_id;
        ig.color_override_rgba8 = ic.color_override_rgba8;
        ig.mesh_id              = ic.mesh_id;
        inst_gpu.push_back(ig);
    }
    next_object_id_ = object_id_base + max_local_id + 1;
    const size_t inst_storage_bytes = inst_gpu.size() * sizeof(InstanceGpu);
    m.instance_storage = createBufferWithData(
        device_, queue_,
        inst_gpu.data(), inst_storage_bytes,
        WGPUBufferUsage_Storage,
        "model.instance_storage");
    m.vram_bytes_ssbo += inst_storage_bytes;

    // Hand off CPU mirrors.
    m.meshes    = std::move(metadata.meta.meshes);
    m.instances = std::move(metadata.meta.instances);

    // Streaming defers per-mesh vertex data until the owning chunk is
    // loaded, so mesh-local volumes + the Area-tool CPU shadow can't
    // be precomputed here. Both fill in per-chunk inside
    // applyStreamedChunk as the bytes arrive.
    m.mesh_local_volumes.assign(m.meshes.size(), 0.0);
    m.mesh_triangles_cache.assign(m.meshes.size(), ModelGpuData::MeshTriangles{});
    // Default: assume opaque. applyStreamedChunk flips entries to 1 as
    // their bytes arrive and a vertex-alpha-byte < 255 is observed.
    m.mesh_has_alpha.assign(m.meshes.size(), uint8_t(0));

    // object_id → instance index lookup. Volume tool reads it on every
    // selection mutation; per-pick latency stays O(K) instead of O(K*N).
    m.object_id_to_instance.clear();
    m.object_id_to_instance.reserve(m.instances.size());
    for (uint32_t i = 0; i < uint32_t(m.instances.size()); ++i) {
        m.object_id_to_instance.emplace(m.instances[i].object_id, i);
    }

    // Compute per-chunk world AABBs + instance-id lists from the
    // instance_to_chunk mapping. Under spatial bucketing this captures
    // each bucket's actual instance extent; under mesh-keyed it's
    // equivalent to the old mesh_chunk_idx lookup since one mesh → one
    // chunk → instances all land identically.
    for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
        m.chunks[ci].instance_ids.reserve(m.instances.size() / m.chunks.size() + 4);
    }
    for (uint32_t inst_idx = 0; inst_idx < uint32_t(m.instances.size()); ++inst_idx) {
        const auto& inst = m.instances[inst_idx];
        const uint32_t ci = instance_to_chunk[inst_idx];
        if (ci >= m.chunks.size()) continue;
        auto& c = m.chunks[ci];
        for (int a = 0; a < 3; ++a) {
            c.aabb_min[a] = std::min(c.aabb_min[a], inst.world_aabb_min[a]);
            c.aabb_max[a] = std::max(c.aabb_max[a], inst.world_aabb_max[a]);
        }
        c.instance_ids.push_back(inst_idx);
    }

    // Populate per-instance arrays from the per-chunk per-mesh offsets
    // computed during chunk construction. Works for both planners:
    //   - mesh-keyed: each mesh in one chunk, offsets match the old
    //     per-mesh-array translation exactly (pixel-identical)
    //   - spatial: the same mesh_id may appear in different chunks at
    //     different offsets; the per-chunk table holds each chunk's own
    //     local offsets, so instance_*[i] reflects the chunk that
    //     instance i's bucket landed in
    {
        const size_t n_inst = m.instances.size();
        m.instance_chunk_idx.assign(n_inst, 0);
        m.instance_base_vertex.assign(n_inst, 0);
        m.instance_ebo_first_u32.assign(n_inst, 0);
        m.instance_lod1_first_u32.assign(n_inst, 0);
        for (size_t i = 0; i < n_inst; ++i) {
            const uint32_t ci = instance_to_chunk[i];
            const uint32_t mi = m.instances[i].mesh_id;
            if (ci >= chunk_mesh_offsets.size()) continue;
            auto it = chunk_mesh_offsets[ci].find(mi);
            if (it == chunk_mesh_offsets[ci].end()) continue;
            m.instance_chunk_idx[i]      = ci;
            m.instance_base_vertex[i]    = it->second.base_vertex;
            m.instance_ebo_first_u32[i]  = it->second.ebo_first;
            m.instance_lod1_first_u32[i] = it->second.lod1_first;
        }
    }

    auto [inserted, _] = models_gpu_.emplace(model_id, std::move(m));
    ModelGpuData& mref = inserted->second;

    // Bind groups can't be built yet — they need vertex_storage from each
    // chunk's load. The per-frame loader (commit 4) will buildModelBindGroup
    // after a chunk becomes resident.

    Log::info().noquote().nospace()
        << "[wgpu stream] applyCachedModel mid=" << model_id
        << " verts=" << mref.vertex_bytes << "B (deferred)"
        << " idx="   << mref.index_count
        << " meshes=" << mref.mesh_count
        << " instances=" << mref.instance_count
        << " chunks=" << mref.chunks.size();

    if (!initial_view_applied_) {
        viewAll();
        initial_view_applied_ = true;
    }
    ensureSelectionFlagsBuffer();
    if (isExposed()) requestUpdate();
}

// -----------------------------------------------------------------------------
// Direct-IFC ingestion (mirrors GL ViewportWindow::uploadMeshChunk /
// uploadInstanceChunk / finalizeModel). Streamer pushes chunks; we stage
// them into a SidecarData-shaped buffer and commit at finalize via the
// same chunk planner the sidecar load uses.
// -----------------------------------------------------------------------------

static SidecarData& getOrCreateDirectStaging(
        std::unordered_map<uint32_t, std::unique_ptr<SidecarData>>& staging,
        uint32_t model_id) {
    auto it = staging.find(model_id);
    if (it == staging.end()) {
        auto [it_new, _] = staging.emplace(
            model_id, std::make_unique<SidecarData>());
        return *it_new->second;
    }
    return *it->second;
}

void ViewportWindow::uploadMeshChunk(const MeshChunk& chunk) {
    if (chunk.vertices.empty() || chunk.indices.empty()) return;
    SidecarData& s = getOrCreateDirectStaging(pending_direct_loads_, chunk.model_id);

    // Streamer format: 7 floats / vertex (pos3 + normal3 + color-as-float).
    // Same quantisation as SidecarBuilder::onMeshReady so direct-load and
    // sidecar-load produce byte-identical GPU buffers.
    const size_t n_verts = chunk.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS;

    float bmin[3] = {  std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity() };
    float bmax[3] = { -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity() };
    for (size_t i = 0; i < n_verts; ++i) {
        const float* v = chunk.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS;
        for (int a = 0; a < 3; ++a) {
            if (v[a] < bmin[a]) bmin[a] = v[a];
            if (v[a] > bmax[a]) bmax[a] = v[a];
        }
    }
    float extent_recip[3];
    for (int a = 0; a < 3; ++a) {
        const float ext = bmax[a] - bmin[a];
        extent_recip[a] = ext > 0.0f ? 1.0f / ext : 0.0f;
    }

    const size_t vb_offset = s.vertices.size();
    s.vertices.resize(vb_offset + n_verts * INSTANCED_VERTEX_STRIDE_BYTES);
    for (size_t i = 0; i < n_verts; ++i) {
        quantizeVertex(chunk.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS,
                       bmin, extent_recip,
                       s.vertices.data() + vb_offset
                           + i * INSTANCED_VERTEX_STRIDE_BYTES);
    }

    const size_t ib_offset = s.indices.size();
    s.indices.insert(s.indices.end(),
                     chunk.indices.begin(), chunk.indices.end());

    MeshInfo info{};
    info.vbo_byte_offset = uint32_t(vb_offset);
    info.vertex_count    = uint32_t(n_verts);
    info.ebo_byte_offset = uint32_t(ib_offset * sizeof(uint32_t));
    info.index_count     = uint32_t(chunk.indices.size());
    for (int a = 0; a < 3; ++a) {
        info.local_aabb_min[a] = bmin[a];
        info.local_aabb_max[a] = bmax[a];
    }
    info.first_instance       = 0;
    info.instance_count       = 0;
    info.lod1_ebo_byte_offset = 0;
    info.lod1_index_count     = 0;

    if (s.meshes.size() <= chunk.local_mesh_id) {
        s.meshes.resize(chunk.local_mesh_id + 1);
    }
    s.meshes[chunk.local_mesh_id] = info;
}

void ViewportWindow::uploadInstanceChunk(const InstanceChunk& chunk) {
    SidecarData& s = getOrCreateDirectStaging(pending_direct_loads_, chunk.model_id);

    InstanceCpu inst{};
    inst.mesh_id              = chunk.local_mesh_id;
    inst.object_id            = chunk.object_id;
    inst.color_override_rgba8 = chunk.color_override_rgba8;
    inst.model_id             = chunk.model_id;
    std::memcpy(inst.placement_transformation, chunk.transform,
                sizeof(inst.placement_transformation));
    for (int i = 0; i < 16; ++i) {
        inst.transform[i] = float(chunk.transform[i]);
    }
    std::memcpy(inst.world_aabb_min, chunk.world_aabb_min, sizeof(inst.world_aabb_min));
    std::memcpy(inst.world_aabb_max, chunk.world_aabb_max, sizeof(inst.world_aabb_max));

    s.instances.push_back(inst);
}

void ViewportWindow::finalizeModel(uint32_t model_id) {
    auto it = pending_direct_loads_.find(model_id);
    if (it == pending_direct_loads_.end()) {
        Log::warn().nospace()
            << "[wgpu direct] finalizeModel(" << model_id
            << ") with no staged data; skipping";
        return;
    }
    // Move the staging out so the apply path can std::move from it without
    // leaving a half-moved entry in the map mid-call.
    std::unique_ptr<SidecarData> staging_ptr = std::move(it->second);
    pending_direct_loads_.erase(it);
    SidecarData& s = *staging_ptr;

    if (!device_ || !queue_) {
        Log::warn() << "[wgpu direct] finalizeModel without an initialised device";
        return;
    }
    if (s.meshes.empty() || s.instances.empty()) {
        Log::info().nospace() << "[wgpu direct] finalizeModel(" << model_id
                          << "): empty staging (meshes=" << s.meshes.size()
                          << " instances=" << s.instances.size() << ")";
        return;
    }

    // Build a StreamingSidecar around the staging so applyCachedModel can
    // run its chunk planner over the same shape it expects from on-disk
    // metadata. file_path is left empty — the streaming worker key off
    // that to skip these chunks (they're already resident after the
    // applyStreamedChunk loop below).
    StreamingSidecar metadata;
    metadata.meta = std::move(s);
    metadata.vertex_section_offset = 0;
    metadata.vertex_total_bytes    = metadata.meta.vertices.size();
    metadata.index_section_offset  = 0;
    metadata.index_total_count     = metadata.meta.indices.size();
    metadata.file_path.clear();

    // applyCachedModel consumes meta.meshes / meta.instances (via std::move
    // inside). The raw vertex / index bytes stay on `metadata.meta` until
    // we gather them per-chunk below.
    std::vector<uint8_t>  raw_vertices = std::move(metadata.meta.vertices);
    std::vector<uint32_t> raw_indices  = std::move(metadata.meta.indices);

    applyCachedModel(model_id, std::move(metadata));

    auto model_it = models_gpu_.find(model_id);
    if (model_it == models_gpu_.end()) {
        Log::warn().nospace()
            << "[wgpu direct] finalizeModel(" << model_id
            << "): applyCachedModel produced no model entry";
        return;
    }
    ModelGpuData& m = model_it->second;

    // Gather each chunk's vertex + index bytes from the staged buffers
    // using the per-mesh chunk-local offsets the planner just produced.
    // Same layout as makeChunkRequest's v_ranges/i_ranges, but the source
    // is memory not a sidecar file.
    size_t chunks_uploaded = 0;
    for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
        auto& c = m.chunks[ci];
        if (c.mesh_ids.empty()) continue;

        std::vector<uint8_t>  vbytes(c.vertex_byte_size);
        std::vector<uint32_t> idx;
        idx.reserve(c.index_count);

        for (uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = m.meshes[mi];
            const size_t vsz = size_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            if (vsz > 0) {
                const size_t dst_off = size_t(m.mesh_chunk_local_base_vertex[mi])
                                     * INSTANCED_VERTEX_STRIDE_BYTES;
                std::memcpy(vbytes.data() + dst_off,
                            raw_vertices.data() + mesh.vbo_byte_offset, vsz);
            }
            if (mesh.index_count > 0) {
                const uint32_t* src = raw_indices.data()
                                    + (mesh.ebo_byte_offset / sizeof(uint32_t));
                idx.insert(idx.end(), src, src + mesh.index_count);
            }
        }
        // LOD1 indices: streamer doesn't emit them, but the planner reserves
        // space for them in the chunk's index slice when m.meshes[mi]
        // .lod1_index_count > 0. Direct-load never has LOD1, so this is a
        // no-op walk; left here so the layout stays parallel to the
        // sidecar gather.

        if (!core_.applyStreamedChunk(m, ci, vbytes, idx)) {
            Log::warn().nospace()
                << "[wgpu direct] finalizeModel(" << model_id
                << "): applyStreamedChunk failed on chunk " << ci
                << " (pool OOM?)";
            continue;
        }
        ++chunks_uploaded;
    }

    Log::info().nospace()
        << "[wgpu direct] finalizeModel mid=" << model_id
        << " meshes=" << m.meshes.size()
        << " instances=" << m.instances.size()
        << " chunks=" << chunks_uploaded << "/" << m.chunks.size()
        << " verts=" << raw_vertices.size() << "B"
        << " idx=" << raw_indices.size();
}

// removeModel / resetScene / hideModel / showModel /
// setFederatedFalseOrigin / setModelCoordinateOperation /
// setModelTransformation / recomposeAndUploadModel moved into
// ViewportCore (#84-f). The public-API entry points below forward
// so existing bonsai-side callers don't have to change.

void ViewportWindow::removeModel(uint32_t model_id)   { core_.removeModel(model_id); }
void ViewportWindow::resetScene()                     { core_.resetScene(); }
void ViewportWindow::hideModel(uint32_t model_id)     { core_.hideModel(model_id); }
void ViewportWindow::showModel(uint32_t model_id)     { core_.showModel(model_id); }

void ViewportWindow::setFederatedFalseOrigin(const Eigen::Matrix4d& m) {
    core_.setFederatedFalseOrigin(m);
}
void ViewportWindow::setModelCoordinateOperation(uint32_t mid,
                                                 const Eigen::Matrix4d& m) {
    core_.setModelCoordinateOperation(mid, m);
}
void ViewportWindow::setModelTransformation(uint32_t mid,
                                            const Eigen::Matrix4d& m) {
    core_.setModelTransformation(mid, m);
}
void ViewportWindow::recomposeAndUploadModel(uint32_t mid) {
    core_.recomposeAndUploadModel(mid);
}

bool ViewportWindow::findInstance(uint32_t object_id, InstanceLookup& out) const {
    return core_.findInstance(object_id, out);
}

bool ViewportWindow::firstGeometryPointWorldM(uint32_t model_id,
                                              Eigen::Vector3d& out) const {
    return core_.firstGeometryPointWorldM(model_id, out);
}

void ViewportWindow::frameOnFederatedOrigin(uint32_t model_id,
                                                float max_distance_m) {
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return;
    const ModelGpuData& m = it->second;
    if (m.instances.empty()) return;

    float mn[3] = {  std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity() };
    float mx[3] = { -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity() };
    for (const auto& inst : m.instances) {
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
        << "[wgpu] frameOnFederatedOrigin model=" << model_id
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
        configureSurface(w, h);
    }
    requestUpdate();
}

void ViewportWindow::resizeEvent(QResizeEvent* /*event*/) {
    if (!wgpu_initialized_ || !isExposed()) return;
    const int w = int(width()  * devicePixelRatio());
    const int h = int(height() * devicePixelRatio());
    if (w > 0 && h > 0) {
        configureSurface(w, h);
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
    const char* nav_env = std::getenv("WGPU_NAV_PRESET");
    applyNavPreset(nav_env ? nav_env : "blender");
    Log::info().noquote().nospace()
        << "[wgpu nav] preset=" << (nav_env ? nav_env : "blender")
        << " (orbit "
        << (orbit_button_ == Qt::RightButton ? "RMB" : "MMB")
        << (orbit_mods_ & Qt::ShiftModifier ? "+Shift" : "")
        << ", pan "
        << (pan_button_ == Qt::RightButton ? "RMB" : "MMB")
        << (pan_mods_ & Qt::ShiftModifier ? "+Shift" : "")
        << ")";

    // ---- ViewportCore handles instance/adapter/device/queue/pool/format -
    if (!core_.initWgpu(web_limits_)) return false;

    // ---- Pipelines + overlays (still VW-side; HiZ/edge/pick + overlay
    //      init haven't migrated yet) -------------------------------------
    if (!buildPipelines()) return false;
    if (!buildHizPipeline()) return false;
    if (!buildEdgePipeline()) return false;
    if (!overlays_.init(instance_, device_, queue_, surface_format_, SAMPLE_COUNT)) {
        Log::warn() << "OverlayRenderer init failed";
        return false;
    }
    if (!buildPickPipeline()) return false;
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
#elif defined(Q_OS_MAC)
// Cocoa bridge declared in MetalSurface_mac.h, implemented in the
// adjacent .mm file. Keeps Objective-C out of this pure-C++ TU.
#  include "MetalSurface_mac.h"
#endif

// Private bool createSurface() removed in #84-l — its body is now
// inside the public ViewportHost override createSurface(WGPUInstance).

// -----------------------------------------------------------------------------
// Surface (re)configure + render
// -----------------------------------------------------------------------------

void ViewportWindow::configureSurface(int width_px, int height_px) {
    WGPUSurfaceConfiguration cfg = {};
    cfg.device      = device_;
    cfg.format      = surface_format_;
    // CopySrc lets captureNextFrameToPng copy the surface texture back to
    // host memory. Trivial cost on all known backends.
    cfg.usage       = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_CopySrc;
    cfg.width       = uint32_t(width_px);
    cfg.height      = uint32_t(height_px);
    // Present mode. WGPU_PRESENT_MODE=fifo|fifo_relaxed|mailbox|immediate
    // overrides; default is mailbox.
    //   mailbox       — DEFAULT. Vsync-aligned (no tearing), one-frame
    //                   queue (last-frame-wins). ~16ms input→display
    //                   latency. wgpu-native falls back to fifo
    //                   automatically on backends that don't implement
    //                   it (Vulkan + NVIDIA on Linux is the historical
    //                   one).
    //   fifo          — strict vsync, 2–3 frame DXGI/swapchain queue
    //                   (~50ms latency). Most power-efficient, but
    //                   visibly laggy for cursor-bound interactions
    //                   (marquee, pivot, orbit). Was the stage-1 default
    //                   because Fifo is the only mode the WebGPU spec
    //                   *requires* backends to support.
    //   fifo_relaxed  — adaptive vsync. Tears when a frame misses the
    //                   refresh deadline, smooth otherwise. Useful in
    //                   the fly-mode-jitter case where Fifo would
    //                   double-frame on a missed vsync.
    //   immediate     — no vsync at all. Frames presented as soon as
    //                   ready, may tear on motion. Useful for raw
    //                   throughput benchmarking.
    // Preference order. Override with WGPU_PRESENT_MODE=...; otherwise we
    // try Mailbox → Immediate → FifoRelaxed → Fifo and pick the first
    // mode actually advertised by the surface. Asking for a mode that
    // the backend doesn't list aborts the process (wgpu-native panics
    // from Rust at wgpuSurfaceConfigure). On Metal in particular only
    // Fifo + Immediate are exposed today, so a static Mailbox default
    // crashes there.
    //
    // Why Immediate sits above FifoRelaxed: Mailbox is the right answer
    // for an interactive viewer (vsync-aligned, no tearing, 1-frame
    // queue) but a meaningful subset of Linux Vulkan stacks (some
    // compositors, some driver/WSI combinations) silently don't expose
    // it — see the "[wgpu] surface advertises present modes:" startup
    // log. On those stacks, Fifo's 2-3 frame queue doubles input-to-
    // photon latency the moment WASD activates, which on a 60 Hz
    // display reads as judder during fly-mode mouse-look. Immediate
    // can tear but keeps latency at one render-body, which preserves
    // the responsive-feel that's the main reason to use a wgpu viewer.
    // FifoRelaxed is the middle option — better latency than Fifo at
    // the edge, can tear when over budget — kept as the next fallback.
    WGPUPresentMode preferred[4] = {
        WGPUPresentMode_Mailbox,
        WGPUPresentMode_Immediate,
        WGPUPresentMode_FifoRelaxed,
        WGPUPresentMode_Fifo,
    };
    const char* pm_name = "mailbox";
    if (const char* s = std::getenv("WGPU_PRESENT_MODE")) {
        WGPUPresentMode override_pm = WGPUPresentMode_Fifo;
        bool known = true;
        if      (std::strcmp(s, "fifo") == 0)         { override_pm = WGPUPresentMode_Fifo;        pm_name = "fifo"; }
        else if (std::strcmp(s, "fifo_relaxed") == 0) { override_pm = WGPUPresentMode_FifoRelaxed; pm_name = "fifo_relaxed"; }
        else if (std::strcmp(s, "mailbox") == 0)      { override_pm = WGPUPresentMode_Mailbox;     pm_name = "mailbox"; }
        else if (std::strcmp(s, "immediate") == 0)    { override_pm = WGPUPresentMode_Immediate;   pm_name = "immediate"; }
        else {
            known = false;
            Log::warn().noquote().nospace()
                << "[wgpu] unknown WGPU_PRESENT_MODE=" << s
                << " (expected fifo|fifo_relaxed|mailbox|immediate); falling back to preference order";
        }
        if (known) {
            preferred[0] = override_pm;
            preferred[1] = WGPUPresentMode_Fifo; // Fifo is the only guaranteed-supported mode
            preferred[2] = preferred[3] = WGPUPresentMode_Fifo;
        }
    }

    WGPUSurfaceCapabilities caps = {};
    wgpuSurfaceGetCapabilities(surface_, adapter_, &caps);
    auto supports = [&](WGPUPresentMode mode) {
        for (size_t i = 0; i < caps.presentModeCount; ++i) {
            if (caps.presentModes[i] == mode) return true;
        }
        return false;
    };

    // Log the full advertised set on first configure. Diagnostic for
    // "WGPU_PRESENT_MODE=mailbox falls back to fifo" — if Mailbox is
    // missing here, the driver/compositor doesn't expose it (drives the
    // input-latency question; see WGPU_PRESENT_MODE notes above). If
    // Mailbox is listed but we still pick Fifo, the preference order
    // has a bug.
    if (!surface_configured_) {
        QString advertised;
        for (size_t i = 0; i < caps.presentModeCount; ++i) {
            const char* name = "?";
            switch (caps.presentModes[i]) {
                case WGPUPresentMode_Fifo:        name = "fifo";         break;
                case WGPUPresentMode_FifoRelaxed: name = "fifo_relaxed"; break;
                case WGPUPresentMode_Mailbox:     name = "mailbox";      break;
                case WGPUPresentMode_Immediate:   name = "immediate";    break;
                default: break;
            }
            if (i > 0) advertised += ", ";
            advertised += QString::fromLatin1(name);
        }
        Log::info().noquote().nospace()
            << "[wgpu] surface advertises present modes: " << advertised;
    }
    WGPUPresentMode pm = WGPUPresentMode_Fifo; // spec-guaranteed fallback
    for (WGPUPresentMode candidate : preferred) {
        if (supports(candidate)) { pm = candidate; break; }
    }
    switch (pm) {
        case WGPUPresentMode_Mailbox:      pm_name = "mailbox";      break;
        case WGPUPresentMode_FifoRelaxed:  pm_name = "fifo_relaxed"; break;
        case WGPUPresentMode_Immediate:    pm_name = "immediate";    break;
        case WGPUPresentMode_Fifo:         pm_name = "fifo";         break;
        default: break;
    }
    wgpuSurfaceCapabilitiesFreeMembers(caps);
    cfg.presentMode = pm;
    if (!surface_configured_) {
        const char* note = "";
        switch (pm) {
            case WGPUPresentMode_Mailbox:
                note = " (vsync-aligned, no queue lag — default)"; break;
            case WGPUPresentMode_Fifo:
                note = " (strict vsync, may queue 2–3 frames)";    break;
            case WGPUPresentMode_FifoRelaxed:
                note = " (adaptive vsync — sync if in budget, tear if not)"; break;
            case WGPUPresentMode_Immediate:
                note = " (vsync OFF — framerate uncapped, may tear)";        break;
            default: break;
        }
        Log::info().noquote().nospace() << "[wgpu] present mode = " << pm_name << note;
    }
    cfg.alphaMode   = WGPUCompositeAlphaMode_Auto;

    wgpuSurfaceConfigure(surface_, &cfg);
    configured_w_       = width_px;
    configured_h_       = height_px;
    surface_configured_ = true;
    ensureDepthTexture(width_px, height_px);
    ensureMsaaColorTexture(width_px, height_px);
    ensureHizTextures(width_px, height_px);
    // depth_view_ was just replaced; force the HiZ + edge bind groups to
    // rebuild against the new view on next encode.
    if (hiz_bind_group_) {
        wgpuBindGroupRelease(hiz_bind_group_);
        hiz_bind_group_ = nullptr;
    }
    if (edge_bind_group_) {
        wgpuBindGroupRelease(edge_bind_group_);
        edge_bind_group_ = nullptr;
    }
}

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

static const char* HIZ_WGSL = R"(
struct HizUniforms {
    src_w: u32,
    src_h: u32,
    dst_w: u32,
    dst_h: u32,
};

@group(0) @binding(0) var src_depth: texture_depth_multisampled_2d;
@group(0) @binding(1) var<uniform> u_hiz: HizUniforms;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
};

@vertex
fn vs_main(@builtin(vertex_index) vid: u32) -> VsOut {
    // Fullscreen triangle from a 3-vertex draw, no IA bindings.
    let x = f32((vid << 1u) & 2u) * 2.0 - 1.0;
    let y = f32(vid & 2u) * 2.0 - 1.0;
    var out: VsOut;
    out.clip_pos = vec4<f32>(x, -y, 0.0, 1.0);
    return out;
}

@fragment
fn fs_main(in: VsOut) -> @builtin(frag_depth) f32 {
    let dst_x = u32(in.clip_pos.x);
    let dst_y = u32(in.clip_pos.y);
    let sx0 = (dst_x * u_hiz.src_w) / u_hiz.dst_w;
    let sx1 = ((dst_x + 1u) * u_hiz.src_w) / u_hiz.dst_w;
    let sy0 = (dst_y * u_hiz.src_h) / u_hiz.dst_h;
    let sy1 = ((dst_y + 1u) * u_hiz.src_h) / u_hiz.dst_h;

    var max_d: f32 = 0.0;
    for (var y: u32 = sy0; y < sy1; y = y + 1u) {
        for (var x: u32 = sx0; x < sx1; x = x + 1u) {
            let d = textureLoad(src_depth, vec2<i32>(i32(x), i32(y)), 0);
            max_d = max(max_d, d);
        }
    }
    return max_d;
}
)";

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

static const char* EDGE_WGSL = R"(
@group(0) @binding(0) var src_depth: texture_depth_multisampled_2d;

const NEAR: f32 = 0.1;
const FAR:  f32 = 10000.0;
const EDGE_SCALE:     f32 = 6.0;
const EDGE_THRESHOLD: f32 = 0.004;

// Depth texture stores [0,1] z (we pre-multiply a z-remap onto Qt's GL-style
// projection in the main pipeline). Convert back to GL-NDC then reverse-
// project to view-space distance.
fn linearise(z: f32) -> f32 {
    let ndc = z * 2.0 - 1.0;
    return (2.0 * NEAR * FAR) / (FAR + NEAR - ndc * (FAR - NEAR));
}

@vertex
fn vs_main(@builtin(vertex_index) vid: u32) -> @builtin(position) vec4<f32> {
    let x = f32((vid << 1u) & 2u) * 2.0 - 1.0;
    let y = f32(vid & 2u) * 2.0 - 1.0;
    return vec4<f32>(x, y, 0.0, 1.0);
}

@fragment
fn fs_main(@builtin(position) frag: vec4<f32>) -> @location(0) vec4<f32> {
    let p   = vec2<i32>(i32(frag.x), i32(frag.y));
    let dim = vec2<i32>(textureDimensions(src_depth));

    let dc_raw = textureLoad(src_depth, p, 0);
    // Background pixels: nothing was drawn here. Skip so we don't draw
    // edges on the void / sky.
    if (dc_raw >= 0.99999) { discard; }

    let c = linearise(dc_raw);
    let n = linearise(textureLoad(src_depth, vec2<i32>(p.x,                     max(p.y - 1, 0)),     0));
    let s = linearise(textureLoad(src_depth, vec2<i32>(p.x,                     min(p.y + 1, dim.y - 1)), 0));
    let e = linearise(textureLoad(src_depth, vec2<i32>(min(p.x + 1, dim.x - 1), p.y),                 0));
    let w = linearise(textureLoad(src_depth, vec2<i32>(max(p.x - 1, 0),         p.y),                 0));

    let lap   = abs(4.0 * c - n - s - e - w);
    let t     = EDGE_THRESHOLD * c;
    let edge  = clamp((lap - t) * EDGE_SCALE, 0.0, 0.6);

    // Multiplicative blend (Dst, Zero): output rgb = (1 - edge), so the
    // existing surface colour is multiplied by (1 - edge) per channel.
    return vec4<f32>(vec3<f32>(1.0 - edge), 1.0);
}
)";

bool ViewportWindow::buildEdgePipeline() {
    WGPUBindGroupLayoutEntry entries[1] = {};
    entries[0].binding = 0;
    entries[0].visibility = WGPUShaderStage_Fragment;
    entries[0].texture.sampleType    = WGPUTextureSampleType_Depth;
    entries[0].texture.viewDimension = WGPUTextureViewDimension_2D;
    entries[0].texture.multisampled  = 1;

    WGPUBindGroupLayoutDescriptor bgl_desc = {};
    bgl_desc.entryCount = 1;
    bgl_desc.entries    = entries;
    bgl_desc.label      = svFromCStr("ifcviewer-wgpu.edge_bgl");
    edge_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);

    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 1;
    pl_desc.bindGroupLayouts     = &edge_bgl_;
    pl_desc.label                = svFromCStr("ifcviewer-wgpu.edge_pipeline_layout");
    edge_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    WGPUShaderSourceWGSL wgsl_src = {};
    wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl_src.code        = svFromCStr(EDGE_WGSL);
    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl_src.chain;
    sm_desc.label       = svFromCStr("ifcviewer-wgpu.edge_wgsl");
    edge_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    // Multiplicative blend (Dst, Zero): out.rgb = src.rgb * dst.rgb.
    // Fragment outputs (1 - edge, 1 - edge, 1 - edge) so the existing
    // surface colour is scaled per-channel — strictly darkens, never
    // brightens. Matches GL's renderEdgePass (GL_DST_COLOR, GL_ZERO).
    WGPUBlendState blend = {};
    blend.color.srcFactor = WGPUBlendFactor_Dst;
    blend.color.dstFactor = WGPUBlendFactor_Zero;
    blend.color.operation = WGPUBlendOperation_Add;
    blend.alpha.srcFactor = WGPUBlendFactor_Zero;
    blend.alpha.dstFactor = WGPUBlendFactor_One;
    blend.alpha.operation = WGPUBlendOperation_Add;

    WGPUColorTargetState target = {};
    target.format    = surface_format_;
    target.blend     = &blend;
    target.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = edge_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &target;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = edge_pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.edge_pipeline");
    rp_desc.vertex.module       = edge_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 0;
    rp_desc.fragment            = &frag;
    rp_desc.depthStencil        = nullptr;            // no depth attachment
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode  = WGPUCullMode_None;
    rp_desc.multisample.count   = 1;
    rp_desc.multisample.mask    = 0xFFFFFFFFu;

    edge_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!edge_pipeline_) {
        Log::warn() << "wgpu edge pipeline creation failed";
        return false;
    }
    return true;
}

void ViewportWindow::encodeEdgePass(WGPUCommandEncoder enc,
                                        WGPUTextureView surface_view) {
    if (!edges_enabled_ || !edge_pipeline_ || !depth_view_ || !surface_view) return;

    // Rebuild lazily when the underlying depth view was replaced (on resize
    // we proactively null this out alongside the HiZ bind group).
    if (!edge_bind_group_) {
        WGPUBindGroupEntry entry = {};
        entry.binding     = 0;
        entry.textureView = depth_view_;
        WGPUBindGroupDescriptor bg = {};
        bg.layout     = edge_bgl_;
        bg.entryCount = 1;
        bg.entries    = &entry;
        bg.label      = svFromCStr("ifcviewer-wgpu.edge_bind_group");
        edge_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg);
    }

    WGPURenderPassColorAttachment color = {};
    color.view       = surface_view;
    color.loadOp     = WGPULoadOp_Load;      // preserve resolved main-pass colour
    color.storeOp    = WGPUStoreOp_Store;
    color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 1;
    pass_desc.colorAttachments       = &color;
    pass_desc.depthStencilAttachment = nullptr;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.edge_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetPipeline(pass, edge_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, edge_bind_group_, 0, nullptr);
    wgpuRenderPassEncoderDraw(pass, 3, 1, 0, 0);
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);
}

// -----------------------------------------------------------------------------
void ViewportWindow::setPivotIndicatorVisible(bool visible, int hide_after_ms) {
    if (!pivot_indicator_hide_timer_) {
        pivot_indicator_hide_timer_ = new QTimer(this);
        pivot_indicator_hide_timer_->setSingleShot(true);
        QObject::connect(pivot_indicator_hide_timer_, &QTimer::timeout, this,
                         [this]() {
                             pivot_indicator_visible_ = false;
                             requestUpdate();
                         });
    }
    pivot_indicator_visible_ = visible;
    if (visible && hide_after_ms > 0) {
        pivot_indicator_hide_timer_->start(hide_after_ms);
    } else {
        pivot_indicator_hide_timer_->stop();
    }
    requestUpdate();
}
void ViewportWindow::releaseEdgeResources() {
    if (edge_bind_group_)      { wgpuBindGroupRelease(edge_bind_group_);      edge_bind_group_ = nullptr; }
    if (edge_pipeline_)        { wgpuRenderPipelineRelease(edge_pipeline_);   edge_pipeline_ = nullptr; }
    if (edge_shader_module_)   { wgpuShaderModuleRelease(edge_shader_module_);edge_shader_module_ = nullptr; }
    if (edge_pipeline_layout_) { wgpuPipelineLayoutRelease(edge_pipeline_layout_); edge_pipeline_layout_ = nullptr; }
    if (edge_bgl_)             { wgpuBindGroupLayoutRelease(edge_bgl_);       edge_bgl_ = nullptr; }
}

// -----------------------------------------------------------------------------
// Pick pipeline (stage 4)
// -----------------------------------------------------------------------------
//
// Same vertex pulling architecture as the main pipeline; reuses
// pipeline_layout_ so per-frame and per-model bind groups stay shared with
// the main draw. Differences are in the fragment (one R32UInt output) and
// the render target attachments (single-sample, surface-sized pick FBO).

bool ViewportWindow::buildPickPipeline() {
    // Two color attachments: R32UInt for object_id, RGBA16F for the
    // packed world-space normal so the section tool can drop perpendicular
    // cuts at the picked pixel.
    WGPUColorTargetState color_targets[2] = {};
    color_targets[0].format    = WGPUTextureFormat_R32Uint;
    color_targets[0].writeMask = WGPUColorWriteMask_All;
    color_targets[1].format    = WGPUTextureFormat_RGBA16Float;
    color_targets[1].writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = main_shader_module_;
    frag.entryPoint  = svFromCStr("fs_pick");
    frag.targetCount = 2;
    frag.targets     = color_targets;

    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_True;
    depth.depthCompare         = WGPUCompareFunction_Less;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.pick_pipeline");
    rp_desc.vertex.module       = main_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_pick");
    rp_desc.vertex.bufferCount  = 0;
    rp_desc.fragment            = &frag;
    rp_desc.depthStencil        = &depth;
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode  = WGPUCullMode_Back;
    rp_desc.primitive.frontFace = WGPUFrontFace_CCW;
    rp_desc.multisample.count   = 1;
    rp_desc.multisample.mask    = 0xFFFFFFFFu;

    pick_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!pick_pipeline_) {
        Log::warn() << "wgpu pick pipeline creation failed";
        return false;
    }
    return true;
}

void ViewportWindow::ensurePickAttachments(int w, int h) {
    if (w <= 0 || h <= 0) return;
    if (w == pick_w_ && h == pick_h_ && pick_color_view_) return;

    if (pick_color_view_)     { wgpuTextureViewRelease(pick_color_view_); pick_color_view_ = nullptr; }
    if (pick_color_texture_)  { wgpuTextureRelease(pick_color_texture_);  pick_color_texture_ = nullptr; }
    if (pick_normal_view_)    { wgpuTextureViewRelease(pick_normal_view_); pick_normal_view_ = nullptr; }
    if (pick_normal_texture_) { wgpuTextureRelease(pick_normal_texture_); pick_normal_texture_ = nullptr; }
    if (pick_depth_view_)     { wgpuTextureViewRelease(pick_depth_view_); pick_depth_view_ = nullptr; }
    if (pick_depth_texture_)  { wgpuTextureRelease(pick_depth_texture_);  pick_depth_texture_ = nullptr; }

    WGPUTextureDescriptor cdesc = {};
    cdesc.usage         = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_CopySrc;
    cdesc.dimension     = WGPUTextureDimension_2D;
    cdesc.size.width    = uint32_t(w);
    cdesc.size.height   = uint32_t(h);
    cdesc.size.depthOrArrayLayers = 1;
    cdesc.format        = WGPUTextureFormat_R32Uint;
    cdesc.mipLevelCount = 1;
    cdesc.sampleCount   = 1;
    cdesc.label         = svFromCStr("ifcviewer-wgpu.pick_color");
    pick_color_texture_ = wgpuDeviceCreateTexture(device_, &cdesc);
    pick_color_view_    = wgpuTextureCreateView(pick_color_texture_, nullptr);

    WGPUTextureDescriptor ndesc = cdesc;
    ndesc.format = WGPUTextureFormat_RGBA16Float;
    ndesc.label  = svFromCStr("ifcviewer-wgpu.pick_normal");
    pick_normal_texture_ = wgpuDeviceCreateTexture(device_, &ndesc);
    pick_normal_view_    = wgpuTextureCreateView(pick_normal_texture_, nullptr);

    WGPUTextureDescriptor ddesc = {};
    ddesc.usage         = WGPUTextureUsage_RenderAttachment;
    ddesc.dimension     = WGPUTextureDimension_2D;
    ddesc.size.width    = uint32_t(w);
    ddesc.size.height   = uint32_t(h);
    ddesc.size.depthOrArrayLayers = 1;
    ddesc.format        = WGPUTextureFormat_Depth32Float;
    ddesc.mipLevelCount = 1;
    ddesc.sampleCount   = 1;
    ddesc.label         = svFromCStr("ifcviewer-wgpu.pick_depth");
    pick_depth_texture_ = wgpuDeviceCreateTexture(device_, &ddesc);
    WGPUTextureViewDescriptor dvdesc = {};
    dvdesc.format          = WGPUTextureFormat_Depth32Float;
    dvdesc.dimension       = WGPUTextureViewDimension_2D;
    dvdesc.mipLevelCount   = 1;
    dvdesc.arrayLayerCount = 1;
    dvdesc.aspect          = WGPUTextureAspect_DepthOnly;
    pick_depth_view_ = wgpuTextureCreateView(pick_depth_texture_, &dvdesc);

    if (!pick_staging_buffer_) {
        // 256 B is the smallest aligned staging buffer that satisfies
        // WGPU_BYTES_PER_ROW_ALIGN for a single-row copy.
        WGPUBufferDescriptor sb = {};
        sb.size  = 256;
        sb.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        sb.label = svFromCStr("ifcviewer-wgpu.pick_staging");
        pick_staging_buffer_ = wgpuDeviceCreateBuffer(device_, &sb);
    }
    if (!pick_normal_staging_buffer_) {
        WGPUBufferDescriptor sb = {};
        sb.size  = 256;
        sb.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        sb.label = svFromCStr("ifcviewer-wgpu.pick_normal_staging");
        pick_normal_staging_buffer_ = wgpuDeviceCreateBuffer(device_, &sb);
    }
    pick_w_ = w;
    pick_h_ = h;
}

void ViewportWindow::releasePickResources() {
    if (pick_color_view_)     { wgpuTextureViewRelease(pick_color_view_); pick_color_view_ = nullptr; }
    if (pick_color_texture_)  { wgpuTextureRelease(pick_color_texture_);  pick_color_texture_ = nullptr; }
    if (pick_normal_view_)    { wgpuTextureViewRelease(pick_normal_view_); pick_normal_view_ = nullptr; }
    if (pick_normal_texture_) { wgpuTextureRelease(pick_normal_texture_); pick_normal_texture_ = nullptr; }
    if (pick_depth_view_)     { wgpuTextureViewRelease(pick_depth_view_); pick_depth_view_ = nullptr; }
    if (pick_depth_texture_)  { wgpuTextureRelease(pick_depth_texture_);  pick_depth_texture_ = nullptr; }
    if (pick_staging_buffer_) { wgpuBufferRelease(pick_staging_buffer_);  pick_staging_buffer_ = nullptr; }
    if (pick_normal_staging_buffer_) { wgpuBufferRelease(pick_normal_staging_buffer_); pick_normal_staging_buffer_ = nullptr; }
    if (pick_pipeline_)       { wgpuRenderPipelineRelease(pick_pipeline_); pick_pipeline_ = nullptr; }
    pick_w_ = pick_h_ = 0;
}

uint32_t ViewportWindow::pickObjectAt(int x_pixels, int y_pixels,
                                          Eigen::Vector3f* normal_out) {
    if (normal_out) *normal_out = Eigen::Vector3f(0, 0, 1);
    if (!pick_pipeline_ || !device_ || !queue_ || models_gpu_.empty()) return 0;
    if (configured_w_ <= 0 || configured_h_ <= 0) return 0;
    if (x_pixels < 0 || y_pixels < 0 ||
        x_pixels >= configured_w_ || y_pixels >= configured_h_) return 0;

    ensurePickAttachments(configured_w_, configured_h_);
    if (!pick_color_view_ || !pick_depth_view_ || !pick_staging_buffer_) return 0;
    if (normal_out && !pick_normal_staging_buffer_) return 0;

    // The current frame's visible_draws are already on the GPU (uploaded
    // by the last render's cullModelCpuUpload), and the per-model bind
    // groups + frame uniform are valid. Just encode a one-shot pick pass.

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    WGPURenderPassColorAttachment color[2] = {};
    color[0].view       = pick_color_view_;
    color[0].loadOp     = WGPULoadOp_Clear;
    color[0].storeOp    = WGPUStoreOp_Store;
    color[0].clearValue = { 0.0, 0.0, 0.0, 0.0 };  // object_id == 0 means miss
    color[0].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;
    color[1].view       = pick_normal_view_;
    color[1].loadOp     = WGPULoadOp_Clear;
    color[1].storeOp    = WGPUStoreOp_Store;
    color[1].clearValue = { 0.5, 0.5, 0.5, 0.0 };  // packed-zero normal at miss
    color[1].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDepthStencilAttachment depth = {};
    depth.view              = pick_depth_view_;
    depth.depthLoadOp       = WGPULoadOp_Clear;
    depth.depthStoreOp      = WGPUStoreOp_Store;
    depth.depthClearValue   = 1.0f;
    depth.stencilLoadOp     = WGPULoadOp_Undefined;
    depth.stencilStoreOp    = WGPUStoreOp_Undefined;
    depth.stencilReadOnly   = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 2;
    pass_desc.colorAttachments       = color;
    pass_desc.depthStencilAttachment = &depth;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.pick_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetPipeline(pass, pick_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, frame_bind_group_, 0, nullptr);
    for (const auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& c : m.chunks) {
            if (!c.bind_group || c.total_visible_vertices == 0) continue;
            wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
            wgpuRenderPassEncoderDraw(pass, c.total_visible_vertices, 1, 0, 0);
        }
    }
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    // Copy the single texel at (x, y) into the staging buffer's first 4 B.
    WGPUTexelCopyTextureInfo src = {};
    src.texture  = pick_color_texture_;
    src.aspect   = WGPUTextureAspect_All;
    src.origin.x = uint32_t(x_pixels);
    src.origin.y = uint32_t(y_pixels);

    WGPUTexelCopyBufferInfo dst = {};
    dst.buffer              = pick_staging_buffer_;
    dst.layout.bytesPerRow  = 256;
    dst.layout.rowsPerImage = 1;

    WGPUExtent3D extent = {};
    extent.width  = 1;
    extent.height = 1;
    extent.depthOrArrayLayers = 1;

    wgpuCommandEncoderCopyTextureToBuffer(enc, &src, &dst, &extent);

    // Optionally copy the normal texel too. RGBA16F is a color format (no
    // full-mip-extent restriction) so a 1×1 copy is fine.
    if (normal_out) {
        WGPUTexelCopyTextureInfo nsrc = {};
        nsrc.texture  = pick_normal_texture_;
        nsrc.aspect   = WGPUTextureAspect_All;
        nsrc.origin.x = uint32_t(x_pixels);
        nsrc.origin.y = uint32_t(y_pixels);

        WGPUTexelCopyBufferInfo ndst = {};
        ndst.buffer              = pick_normal_staging_buffer_;
        ndst.layout.bytesPerRow  = 256;
        ndst.layout.rowsPerImage = 1;

        wgpuCommandEncoderCopyTextureToBuffer(enc, &nsrc, &ndst, &extent);
    }

    WGPUCommandBuffer cmd = wgpuCommandEncoderFinish(enc, nullptr);
    wgpuQueueSubmit(queue_, 1, &cmd);
    wgpuCommandBufferRelease(cmd);
    wgpuCommandEncoderRelease(enc);

    // Sync wait for the readback — pick is interactive (click) and rare,
    // so the GPU stall here is fine.
    struct MapReq { bool done = false; bool ok = false; };
    MapReq req;
    WGPUBufferMapCallbackInfo mcb = {};
    mcb.mode = WGPUCallbackMode_AllowProcessEvents;
    mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                      void* ud1, void* /*ud2*/) {
        auto* r = static_cast<MapReq*>(ud1);
        r->done = true;
        r->ok   = (status == WGPUMapAsyncStatus_Success);
    };
    mcb.userdata1 = &req;

    wgpuBufferMapAsync(pick_staging_buffer_, WGPUMapMode_Read, 0, 256, mcb);
    while (!req.done) wgpuInstanceProcessEvents(instance_);
    if (!req.ok) return 0;

    const uint32_t* mapped = static_cast<const uint32_t*>(
        wgpuBufferGetConstMappedRange(pick_staging_buffer_, 0, 256));
    const uint32_t object_id = mapped ? mapped[0] : 0u;
    wgpuBufferUnmap(pick_staging_buffer_);

    if (normal_out && object_id != 0) {
        MapReq nreq;
        WGPUBufferMapCallbackInfo ncb = mcb;
        ncb.userdata1 = &nreq;
        wgpuBufferMapAsync(pick_normal_staging_buffer_, WGPUMapMode_Read, 0, 256, ncb);
        while (!nreq.done) wgpuInstanceProcessEvents(instance_);
        if (nreq.ok) {
            // RGBA16F = 4 × half-floats per texel = 8 bytes. Decode the
            // first texel (xyz channels) and undo the ×0.5+0.5 sign pack
            // from fs_pick.
            const uint16_t* halves = static_cast<const uint16_t*>(
                wgpuBufferGetConstMappedRange(pick_normal_staging_buffer_, 0, 256));
            if (halves) {
                auto h2f = [](uint16_t h) -> float {
                    // IEEE 754 half → float. Standard bit-fiddle, no STL
                    // helper in pre-C++23.
                    const uint32_t sign     = uint32_t(h & 0x8000u) << 16;
                    uint32_t       exponent = uint32_t(h & 0x7C00u) >> 10;
                    uint32_t       mantissa = uint32_t(h & 0x03FFu);
                    if (exponent == 0) {
                        if (mantissa == 0) {
                            union { uint32_t u; float f; } v{ sign };
                            return v.f;
                        }
                        while ((mantissa & 0x0400u) == 0) {
                            mantissa <<= 1;
                            --exponent;
                        }
                        ++exponent;
                        mantissa &= 0x03FFu;
                    } else if (exponent == 0x1Fu) {
                        exponent = 0xFFu;
                    } else {
                        exponent += (127u - 15u);
                    }
                    const uint32_t bits = sign | (exponent << 23) | (mantissa << 13);
                    union { uint32_t u; float f; } v{ bits };
                    return v.f;
                };
                const float nx = h2f(halves[0]) * 2.0f - 1.0f;
                const float ny = h2f(halves[1]) * 2.0f - 1.0f;
                const float nz = h2f(halves[2]) * 2.0f - 1.0f;
                Eigen::Vector3f n(nx, ny, nz);
                if (n.squaredNorm() > 1e-6f) *normal_out = n.normalized();
            }
            wgpuBufferUnmap(pick_normal_staging_buffer_);
        }
    }

    return object_id;
}

// Slab-method ray-AABB intersection. Returns t_enter (the ray parameter at
// the first hit, clamped to >= 0 so origins inside the box land at t = 0)
// and the axis-aligned face normal at the entry: ±X / ±Y / ±Z depending on
// which slab dominated t_min. The face normal is what the section tool
// uses for surface-perpendicular cuts — for BIM geometry that's almost
// always axis-aligned (walls, slabs, columns) this matches the user's
// expectation; for diagonal or curved geometry it falls back to the
// closest of {±X, ±Y, ±Z}, which is still a usable cut direction.
static bool rayAABBHit(const Eigen::Vector3f& origin, const Eigen::Vector3f& dir,
                       const float mn[3], const float mx[3],
                       float& t_enter, Eigen::Vector3f& face_normal) {
    float t_min = -std::numeric_limits<float>::infinity();
    float t_max =  std::numeric_limits<float>::infinity();
    const float o[3] = { origin.x(), origin.y(), origin.z() };
    const float d[3] = { dir.x(),    dir.y(),    dir.z()    };
    int   hit_axis = -1;
    float hit_sign = 0.0f;  // +1 = ray entered through min-side of slab → outward normal is -axis
    for (int i = 0; i < 3; ++i) {
        if (std::abs(d[i]) < 1e-8f) {
            if (o[i] < mn[i] || o[i] > mx[i]) return false;
            continue;
        }
        float t1 = (mn[i] - o[i]) / d[i];
        float t2 = (mx[i] - o[i]) / d[i];
        float sign_for_t1 = -1.0f;  // ray hits min slab → outward normal points along -axis
        if (t1 > t2) { std::swap(t1, t2); sign_for_t1 = +1.0f; }
        if (t1 > t_min) {
            t_min    = t1;
            hit_axis = i;
            hit_sign = sign_for_t1;
        }
        t_max = std::min(t_max, t2);
        if (t_min > t_max) return false;
    }
    if (t_max < 0.0f) return false;
    t_enter = std::max(t_min, 0.0f);

    if (hit_axis < 0) {
        face_normal = -dir;  // ray origin inside the box on all axes — fallback
    } else {
        Eigen::Vector3f n(0, 0, 0);
        n[hit_axis] = hit_sign;
        face_normal = n;
    }
    return true;
}

std::vector<uint32_t> ViewportWindow::picksInRect(int x, int y, int w, int h) {
    std::vector<uint32_t> out;
    if (w <= 0 || h <= 0) return out;
    if (!pick_pipeline_ || !device_ || !queue_ || models_gpu_.empty()) return out;
    if (configured_w_ <= 0 || configured_h_ <= 0) return out;
    // Clip to framebuffer.
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > configured_w_) w = configured_w_ - x;
    if (y + h > configured_h_) h = configured_h_ - y;
    if (w <= 0 || h <= 0) return out;

    ensurePickAttachments(configured_w_, configured_h_);
    if (!pick_color_view_ || !pick_depth_view_) return out;

    // Padded bytes-per-row for the rect region. R32UInt = 4 B/texel.
    const uint64_t unpadded_bpr = uint64_t(w) * 4;
    const uint64_t padded_bpr   = (unpadded_bpr + WGPU_BYTES_PER_ROW_ALIGN - 1)
                                  / WGPU_BYTES_PER_ROW_ALIGN
                                  * WGPU_BYTES_PER_ROW_ALIGN;
    const uint64_t needed_bytes = padded_bpr * uint64_t(h);
    if (needed_bytes > box_pick_staging_capacity_) {
        if (box_pick_staging_buffer_) {
            wgpuBufferRelease(box_pick_staging_buffer_);
            box_pick_staging_buffer_ = nullptr;
        }
        // 2× grow heuristic — rectangle picks are rare so the slight
        // overshoot on the first grow doesn't matter.
        const uint64_t cap = std::max<uint64_t>(needed_bytes * 2, 64 * 1024);
        WGPUBufferDescriptor sb = {};
        sb.size  = cap;
        sb.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        sb.label = svFromCStr("ifcviewer-wgpu.box_pick_staging");
        box_pick_staging_buffer_ = wgpuDeviceCreateBuffer(device_, &sb);
        box_pick_staging_capacity_ = cap;
    }
    if (!box_pick_staging_buffer_) return out;

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    // Same pick pass setup as pickObjectAt, but with two color targets
    // (R32UInt object_id + RGBA16F normal — we discard the normal here).
    WGPURenderPassColorAttachment color[2] = {};
    color[0].view       = pick_color_view_;
    color[0].loadOp     = WGPULoadOp_Clear;
    color[0].storeOp    = WGPUStoreOp_Store;
    color[0].clearValue = { 0, 0, 0, 0 };
    color[0].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;
    color[1].view       = pick_normal_view_;
    color[1].loadOp     = WGPULoadOp_Clear;
    color[1].storeOp    = WGPUStoreOp_Store;
    color[1].clearValue = { 0.5, 0.5, 0.5, 0 };
    color[1].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDepthStencilAttachment depth = {};
    depth.view            = pick_depth_view_;
    depth.depthLoadOp     = WGPULoadOp_Clear;
    depth.depthStoreOp    = WGPUStoreOp_Store;
    depth.depthClearValue = 1.0f;
    depth.stencilLoadOp   = WGPULoadOp_Undefined;
    depth.stencilStoreOp  = WGPUStoreOp_Undefined;
    depth.stencilReadOnly = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 2;
    pass_desc.colorAttachments       = color;
    pass_desc.depthStencilAttachment = &depth;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.box_pick_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetPipeline(pass, pick_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, frame_bind_group_, 0, nullptr);
    for (const auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& c : m.chunks) {
            if (!c.bind_group || c.total_visible_vertices == 0) continue;
            wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
            wgpuRenderPassEncoderDraw(pass, c.total_visible_vertices, 1, 0, 0);
        }
    }
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    // Copy the rect region of the color attachment to the staging buffer.
    // Color formats allow arbitrary subrect copies (unlike Depth32Float).
    WGPUTexelCopyTextureInfo src = {};
    src.texture  = pick_color_texture_;
    src.aspect   = WGPUTextureAspect_All;
    src.origin.x = uint32_t(x);
    src.origin.y = uint32_t(y);

    WGPUTexelCopyBufferInfo dst = {};
    dst.buffer              = box_pick_staging_buffer_;
    dst.layout.bytesPerRow  = uint32_t(padded_bpr);
    dst.layout.rowsPerImage = uint32_t(h);

    WGPUExtent3D extent = {};
    extent.width  = uint32_t(w);
    extent.height = uint32_t(h);
    extent.depthOrArrayLayers = 1;

    wgpuCommandEncoderCopyTextureToBuffer(enc, &src, &dst, &extent);

    WGPUCommandBuffer cmd = wgpuCommandEncoderFinish(enc, nullptr);
    wgpuQueueSubmit(queue_, 1, &cmd);
    wgpuCommandBufferRelease(cmd);
    wgpuCommandEncoderRelease(enc);

    struct MapReq { bool done = false; bool ok = false; };
    MapReq req;
    WGPUBufferMapCallbackInfo mcb = {};
    mcb.mode = WGPUCallbackMode_AllowProcessEvents;
    mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                      void* ud1, void* /*ud2*/) {
        auto* r = static_cast<MapReq*>(ud1);
        r->done = true;
        r->ok   = (status == WGPUMapAsyncStatus_Success);
    };
    mcb.userdata1 = &req;
    wgpuBufferMapAsync(box_pick_staging_buffer_, WGPUMapMode_Read,
                       0, needed_bytes, mcb);
    while (!req.done) wgpuInstanceProcessEvents(instance_);
    if (!req.ok) return out;

    const uint8_t* mapped = static_cast<const uint8_t*>(
        wgpuBufferGetConstMappedRange(box_pick_staging_buffer_, 0, needed_bytes));
    std::unordered_set<uint32_t> seen;
    if (mapped) {
        for (int row = 0; row < h; ++row) {
            const uint32_t* line = reinterpret_cast<const uint32_t*>(
                mapped + size_t(row) * size_t(padded_bpr));
            for (int col = 0; col < w; ++col) {
                const uint32_t id = line[col];
                if (id != 0) seen.insert(id);
            }
        }
    }
    wgpuBufferUnmap(box_pick_staging_buffer_);

    out.reserve(seen.size());
    for (uint32_t id : seen) out.push_back(id);
    return out;
}

bool ViewportWindow::pickSurfaceAt(int x_pixels, int y_pixels,
                                       uint32_t& object_id_out,
                                       Eigen::Vector3f& world_pos_out,
                                       Eigen::Vector3f& world_normal_out,
                                       float* aabb_radius_out) {
    if (aabb_radius_out) *aabb_radius_out = 0.0f;
    Eigen::Vector3f picked_normal(0, 0, 1);
    const uint32_t id = pickObjectAt(x_pixels, y_pixels, &picked_normal);
    if (id == 0) return false;

    // Build the ray through the clicked pixel: shoot from the camera eye
    // toward the unprojected far-plane point. WebGPU forbids partial copies
    // of Depth32Float (must cover the full mip extent), so reading per-pixel
    // depth would cost a per-click full-texture readback — instead we
    // ray-cast against the AABB of every instance carrying the picked
    // object_id and take the closest hit. Equally accurate for the section
    // tool's "drop a plane where I clicked" UX, no readback at all.
    Eigen::Matrix4f view, proj;
    core_.buildViewProj(view, proj);
    Eigen::Matrix4f inv_vp;
    if (!tryInvert4f(proj * view, inv_vp)) return false;

    const float ndc_x = (2.0f * float(x_pixels) / float(configured_w_)) - 1.0f;
    const float ndc_y = 1.0f - (2.0f * float(y_pixels) / float(configured_h_));
    // Unproject the far-plane corner (NDC z = 1 for WebGPU) of the
    // pick-pixel pillar to get a point on the ray.
    const Eigen::Vector4f far_clip(ndc_x, ndc_y, 1.0f, 1.0f);
    const Eigen::Vector4f far_w   = inv_vp * far_clip;
    if (std::abs(far_w.w()) < 1e-6f) return false;
    const Eigen::Vector3f far_world = far_w.head<3>() / far_w.w();

    const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                   camera_yaw_deg_, camera_pitch_deg_);
    Eigen::Vector3f ray_dir = far_world - eye;
    if (ray_dir.squaredNorm() < 1e-8f) return false;
    ray_dir.normalize();

    float best_t = std::numeric_limits<float>::infinity();
    Eigen::Vector3f best_point;
    Eigen::Vector3f best_normal;
    float     best_radius = 0.0f;
    bool found = false;
    for (const auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& inst : m.instances) {
            if (inst.object_id != id) continue;
            float t = 0.0f;
            Eigen::Vector3f n;
            if (!rayAABBHit(eye, ray_dir,
                            inst.world_aabb_min, inst.world_aabb_max,
                            t, n)) continue;
            if (t < best_t) {
                best_t      = t;
                best_point  = eye + ray_dir * t;
                best_normal = n;
                const float dx = inst.world_aabb_max[0] - inst.world_aabb_min[0];
                const float dy = inst.world_aabb_max[1] - inst.world_aabb_min[1];
                const float dz = inst.world_aabb_max[2] - inst.world_aabb_min[2];
                best_radius = 0.5f * std::sqrt(dx * dx + dy * dy + dz * dz);
                found       = true;
            }
        }
    }
    if (!found) return false;

    if (aabb_radius_out) *aabb_radius_out = best_radius;

    world_pos_out    = best_point;
    // Prefer the per-fragment normal from the pick MRT (matches the actual
    // picked triangle), fall back to the AABB-face normal if the pick pass
    // returned a degenerate vector (e.g. background sliver). The auto-flip
    // in addSectionPlaneAtSurface re-orients toward the camera.
    world_normal_out = (picked_normal.squaredNorm() > 1e-3f)
                         ? picked_normal : best_normal;
    object_id_out    = id;
    return true;
}

// -----------------------------------------------------------------------------
// Section cutting state
// -----------------------------------------------------------------------------

void ViewportWindow::toggleSectionTool() {
    section_tool_active_ = !section_tool_active_;
    Log::info().noquote() << "[wgpu section] tool"
                      << (section_tool_active_ ? "active" : "off");
    if (isExposed()) requestUpdate();
}

bool ViewportWindow::addSectionPlaneAtSurface(const Eigen::Vector3f& point,
                                                  const Eigen::Vector3f& normal,
                                                  float visual_radius) {
    if (int(section_planes_.size()) >= kMaxSectionPlanes) {
        std::fprintf(stderr, "[warn] [wgpu section] cap reached (%d planes)\n",
                     kMaxSectionPlanes);
        return false;
    }
    Eigen::Vector3f n = normal;
    if (n.squaredNorm() < 1e-8f) return false;
    n.normalize();
    // Auto-flip the normal so the camera-facing half gets cut away — that
    // way the first click always reveals the surface the user just clicked.
    const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                   camera_yaw_deg_, camera_pitch_deg_);
    const Eigen::Vector3f eye_dir = eye - point;
    if (n.dot(eye_dir) < 0.0f) n = -n;

    SectionPlane p;
    p.n             = n;
    p.origin        = point;
    p.d             = -n.dot(point);
    p.visual_radius = (visual_radius > 0.0f) ? visual_radius : 1.0f;
    section_planes_.push_back(p);
    Log::info().noquote().nospace()
        << "[wgpu section] added plane #" << section_planes_.size() - 1
        << " origin=(" << point.x() << "," << point.y() << "," << point.z() << ")"
        << " normal=(" << n.x() << "," << n.y() << "," << n.z() << ")";
    if (isExposed()) requestUpdate();
    return true;
}

void ViewportWindow::removeSectionPlane(int index) {
    if (index < 0 || index >= int(section_planes_.size())) return;
    section_planes_.erase(section_planes_.begin() + index);
    Log::info().noquote() << "[wgpu section] removed plane" << index;
    if (isExposed()) requestUpdate();
}

void ViewportWindow::clearSectionPlanes() {
    if (section_planes_.empty()) return;
    section_planes_.clear();
    Log::info() << "[wgpu section] cleared all planes";
    if (isExposed()) requestUpdate();
}

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

bool ViewportWindow::readbackMeshTriangles(uint32_t model_id, uint32_t mesh_id,
                                               MeshTriangles& out) const {
    auto mit = models_gpu_.find(model_id);
    if (mit == models_gpu_.end()) return false;
    const ModelGpuData& m = mit->second;
    if (mesh_id >= m.mesh_triangles_cache.size()) return false;
    const auto& src = m.mesh_triangles_cache[mesh_id];
    if (src.indices.empty() || src.positions.empty()) return false;
    // Copy out — callers iterate freely without worrying about lifetime
    // (streaming may evict a chunk and rebuild the shadow on next load).
    out = src;
    return true;
}

bool ViewportWindow::pickMeshLocalAt(int x, int y, MeshLocalPick& out) {
    uint32_t obj_id = 0;
    Eigen::Vector3f world_pos, world_normal;
    if (!pickSurfaceAt(x, y, obj_id, world_pos, world_normal)) return false;

    // O(1) instance lookup via object_id_to_instance — see also the
    // Volume tool. composed_transform is the float `inst.transform`,
    // already the per-frame world placement.
    //
    // Use the OUTER mid (the live map key) rather than inst.model_id —
    // the InstanceCpu's model_id field is whatever the GL streamer
    // wrote at sidecar-write time, which is stale across sessions and
    // doesn't match the current load's globally-rebased model id.
    for (const auto& [mid, m] : models_gpu_) {
        auto it = m.object_id_to_instance.find(obj_id);
        if (it == m.object_id_to_instance.end()) continue;
        const InstanceCpu& inst = m.instances[it->second];

        // inst.transform is column-major float[16] — the GPU upload
        // layout. Eigen::Matrix4f is also column-major by default, so
        // a Map reads it directly with no element swizzling.
        const Eigen::Matrix4f T = Eigen::Map<const Eigen::Matrix4f>(inst.transform);
        Eigen::Matrix4f Ti;
        if (!tryInvert4f(T, Ti)) return false;

        if (inst.mesh_id >= m.meshes.size()) return false;

        // pickSurfaceAt returns a bounding-box hit (WebGPU bans the
        // depth readback that would give us a real surface point), so
        // world_pos sits on the AABB face — not on any triangle of the
        // mesh. Refine against the picked instance's CPU mesh shadow:
        // re-project the click into a world ray and Möller-Trumbore it
        // against every triangle of this mesh. On a hit, replace
        // world_pos with the real surface point and world_normal with
        // the transformed face normal. Without this, the Area/Length
        // BFS seeds with whatever triangle is closest to the AABB
        // corner — often a perpendicular face, which produces
        // bounding-box-shaped patches instead of surface patches.
        Eigen::Vector3f refined_world_pos    = world_pos;
        Eigen::Vector3f refined_world_normal = world_normal;
        if (inst.mesh_id < m.mesh_triangles_cache.size()) {
            const auto& tris = m.mesh_triangles_cache[inst.mesh_id];
            if (!tris.indices.empty() && configured_w_ > 0 && configured_h_ > 0) {
                Eigen::Matrix4f view, proj;
                core_.buildViewProj(view, proj);
                Eigen::Matrix4f inv_vp;
                if (tryInvert4f(proj * view, inv_vp)) {
                    const float ndc_x = (2.0f * float(x) / float(configured_w_)) - 1.0f;
                    const float ndc_y = 1.0f - (2.0f * float(y) / float(configured_h_));
                    const Eigen::Vector4f far_clip(ndc_x, ndc_y, 1.0f, 1.0f);
                    const Eigen::Vector4f far_w = inv_vp * far_clip;
                    if (std::abs(far_w.w()) >= 1e-6f) {
                        const Eigen::Vector3f far_world = far_w.head<3>() / far_w.w();
                        const Eigen::Vector3f eye = orbitEye(
                            camera_target_, camera_distance_,
                            camera_yaw_deg_, camera_pitch_deg_);
                        Eigen::Vector3f ray_dir = far_world - eye;
                        if (ray_dir.squaredNorm() > 1e-8f) {
                            ray_dir.normalize();
                            // Inverse-transform the world ray into mesh-local.
                            const Eigen::Vector4f ro_l4 = Ti * Eigen::Vector4f(eye.x(),     eye.y(),     eye.z(),     1.0f);
                            const Eigen::Vector4f rd_l4 = Ti * Eigen::Vector4f(ray_dir.x(), ray_dir.y(), ray_dir.z(), 0.0f);
                            const float ro_l[3] = { ro_l4.x(), ro_l4.y(), ro_l4.z() };
                            const float rd_l[3] = { rd_l4.x(), rd_l4.y(), rd_l4.z() };
                            const float ldn = std::sqrt(
                                rd_l[0]*rd_l[0] + rd_l[1]*rd_l[1] + rd_l[2]*rd_l[2]);
                            if (ldn > 0.0f) {
                                float best_t_world = std::numeric_limits<float>::infinity();
                                uint32_t best_tri = UINT32_MAX;
                                const size_t n_tris = tris.indices.size() / 3;
                                for (size_t t = 0; t < n_tris; ++t) {
                                    const uint32_t ia = tris.indices[3 * t + 0];
                                    const uint32_t ib = tris.indices[3 * t + 1];
                                    const uint32_t ic = tris.indices[3 * t + 2];
                                    if (3 * ia + 2 >= tris.positions.size()
                                     || 3 * ib + 2 >= tris.positions.size()
                                     || 3 * ic + 2 >= tris.positions.size()) continue;
                                    const float* va = &tris.positions[3 * ia];
                                    const float* vb = &tris.positions[3 * ib];
                                    const float* vc = &tris.positions[3 * ic];
                                    float t_local = 0.0f;
                                    if (!rayTriMT(ro_l, rd_l, va, vb, vc, t_local)) continue;
                                    const float t_world = t_local / ldn;
                                    if (t_world < best_t_world) {
                                        best_t_world = t_world;
                                        best_tri     = uint32_t(t);
                                    }
                                }
                                if (best_tri != UINT32_MAX) {
                                    refined_world_pos = eye + ray_dir * best_t_world;
                                    // Face normal of the chosen tri,
                                    // transformed back to world.
                                    const uint32_t ia = tris.indices[3 * best_tri + 0];
                                    const uint32_t ib = tris.indices[3 * best_tri + 1];
                                    const uint32_t ic = tris.indices[3 * best_tri + 2];
                                    const float* va = &tris.positions[3 * ia];
                                    const float* vb = &tris.positions[3 * ib];
                                    const float* vc = &tris.positions[3 * ic];
                                    const float bax = vb[0]-va[0], bay = vb[1]-va[1], baz = vb[2]-va[2];
                                    const float cax = vc[0]-va[0], cay = vc[1]-va[1], caz = vc[2]-va[2];
                                    float n_local[3] = {
                                        bay*caz - baz*cay,
                                        baz*cax - bax*caz,
                                        bax*cay - bay*cax,
                                    };
                                    const float nl = std::sqrt(
                                        n_local[0]*n_local[0]
                                      + n_local[1]*n_local[1]
                                      + n_local[2]*n_local[2]);
                                    if (nl > 0.0f) {
                                        n_local[0] /= nl;
                                        n_local[1] /= nl;
                                        n_local[2] /= nl;
                                    }
                                    const float* M = inst.transform;
                                    Eigen::Vector3f n_world(
                                        M[0]*n_local[0] + M[4]*n_local[1] + M[8] *n_local[2],
                                        M[1]*n_local[0] + M[5]*n_local[1] + M[9] *n_local[2],
                                        M[2]*n_local[0] + M[6]*n_local[1] + M[10]*n_local[2]);
                                    if (n_world.squaredNorm() > 1e-12f) {
                                        n_world.normalize();
                                        refined_world_normal = n_world;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        const Eigen::Vector4f mp = Ti * Eigen::Vector4f(refined_world_pos.x(),
                                            refined_world_pos.y(),
                                            refined_world_pos.z(), 1.0f);

        out.object_id     = obj_id;
        out.model_id      = mid;
        out.mesh_id       = inst.mesh_id;
        out.mesh_local[0] = mp.x();
        out.mesh_local[1] = mp.y();
        out.mesh_local[2] = mp.z();
        out.world_pos [0] = refined_world_pos.x();
        out.world_pos [1] = refined_world_pos.y();
        out.world_pos [2] = refined_world_pos.z();
        out.world_normal[0] = refined_world_normal.x();
        out.world_normal[1] = refined_world_normal.y();
        out.world_normal[2] = refined_world_normal.z();
        std::memcpy(out.composed_transform, inst.transform,
                    sizeof(out.composed_transform));
        return true;
    }
    return false;
}

void ViewportWindow::onAreaPick(int x_phys, int y_phys, bool alt) {
    if (!area_tool_) return;
    area_tool_->onPick(*this, x_phys, y_phys, alt);
    updateAreaHud();
}

bool ViewportWindow::meshLocalToGlobal(uint32_t object_id,
                                           const float mesh_local[3],
                                           double global_out[3]) const {
    // Find the instance via the per-model object_id_to_instance map.
    // Use the live map key (`mid`) — see pickMeshLocalAt comment about
    // stale InstanceCpu::model_id from sidecar writes.
    for (const auto& [mid, m] : models_gpu_) {
        auto it = m.object_id_to_instance.find(object_id);
        if (it == m.object_id_to_instance.end()) continue;
        const InstanceCpu& inst = m.instances[it->second];
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
            (m.coordinate_operation_meters * P * local).head<3>();
        global_out[0] = global.x();
        global_out[1] = global.y();
        global_out[2] = global.z();
        return true;
    }
    return false;
}

bool ViewportWindow::raycast(const float origin[3], const float dir[3],
                                 RaycastHit& out) const {
    // World-AABB cull per instance, then transform the ray into the
    // mesh's local frame and intersect every triangle. No BVH — typical
    // BIM scenes have enough AABB-cull to make this acceptable (~ms);
    // a per-model BVH would be the next optimisation.
    float inv_d[3] = {
        std::abs(dir[0]) > 1e-20f ? 1.0f / dir[0] : std::numeric_limits<float>::infinity(),
        std::abs(dir[1]) > 1e-20f ? 1.0f / dir[1] : std::numeric_limits<float>::infinity(),
        std::abs(dir[2]) > 1e-20f ? 1.0f / dir[2] : std::numeric_limits<float>::infinity(),
    };

    float best_t = std::numeric_limits<float>::infinity();
    uint32_t best_oid = 0;
    float    best_normal[3] = {0, 0, 0};

    for (const auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (uint32_t inst_idx = 0; inst_idx < uint32_t(m.instances.size()); ++inst_idx) {
            const InstanceCpu& inst = m.instances[inst_idx];
            if (!rayAabbSlab(origin, inv_d, inst.world_aabb_min, inst.world_aabb_max)) {
                continue;
            }
            if (inst.mesh_id >= m.mesh_triangles_cache.size()) continue;
            const auto& tris = m.mesh_triangles_cache[inst.mesh_id];
            if (tris.indices.empty()) continue;

            // Transform ray into mesh-local frame. We need both a point
            // (origin) and a direction (dir) inverse-transformed; dir is
            // a vector so the translation drops out.
            const Eigen::Matrix4f T = Eigen::Map<const Eigen::Matrix4f>(inst.transform);
            Eigen::Matrix4f Ti;
            if (!tryInvert4f(T, Ti)) continue;
            const Eigen::Vector4f ro_local4 = Ti * Eigen::Vector4f(origin[0], origin[1], origin[2], 1.0f);
            const Eigen::Vector4f rd_local4 = Ti * Eigen::Vector4f(dir[0],    dir[1],    dir[2],    0.0f);
            const float ro_local[3] = { ro_local4.x(), ro_local4.y(), ro_local4.z() };
            const float rd_local[3] = { rd_local4.x(), rd_local4.y(), rd_local4.z() };

            const size_t n_tris = tris.indices.size() / 3;
            for (size_t t = 0; t < n_tris; ++t) {
                const uint32_t ia = tris.indices[3 * t + 0];
                const uint32_t ib = tris.indices[3 * t + 1];
                const uint32_t ic = tris.indices[3 * t + 2];
                if (3 * ia + 2 >= tris.positions.size()
                 || 3 * ib + 2 >= tris.positions.size()
                 || 3 * ic + 2 >= tris.positions.size()) continue;
                const float* va = &tris.positions[3 * ia];
                const float* vb = &tris.positions[3 * ib];
                const float* vc = &tris.positions[3 * ic];
                float t_local = 0.0f;
                if (!rayTriMT(ro_local, rd_local, va, vb, vc, t_local)) continue;
                // Convert t_local into world units. Because we
                // inverse-transformed dir without normalising, world-t =
                // local-t × (|world-dir| / |local-dir|). The caller
                // guarantees world-dir is unit; we compute local-dir
                // length here.
                const float ldn = std::sqrt(rd_local[0]*rd_local[0]
                                          + rd_local[1]*rd_local[1]
                                          + rd_local[2]*rd_local[2]);
                if (ldn <= 0.0f) continue;
                const float t_world = t_local / ldn;
                if (t_world >= best_t) continue;
                best_t   = t_world;
                best_oid = inst.object_id;

                // Mesh-local triangle normal → world via the transform's
                // rotation block. Same column-major math as
                // applyCachedModel uses for AABB normals.
                const float bax = vb[0]-va[0], bay = vb[1]-va[1], baz = vb[2]-va[2];
                const float cax = vc[0]-va[0], cay = vc[1]-va[1], caz = vc[2]-va[2];
                float n_local[3] = {
                    bay * caz - baz * cay,
                    baz * cax - bax * caz,
                    bax * cay - bay * cax,
                };
                const float nl = std::sqrt(n_local[0]*n_local[0]
                                         + n_local[1]*n_local[1]
                                         + n_local[2]*n_local[2]);
                if (nl > 0.0f) { n_local[0] /= nl; n_local[1] /= nl; n_local[2] /= nl; }
                // Normal transform = inverse-transpose; for a rigid +
                // uniform-scale transform the upper-left 3×3 is fine.
                const float* M = inst.transform;
                best_normal[0] = M[0]*n_local[0] + M[4]*n_local[1] + M[8]*n_local[2];
                best_normal[1] = M[1]*n_local[0] + M[5]*n_local[1] + M[9]*n_local[2];
                best_normal[2] = M[2]*n_local[0] + M[6]*n_local[1] + M[10]*n_local[2];
                const float wnl = std::sqrt(best_normal[0]*best_normal[0]
                                          + best_normal[1]*best_normal[1]
                                          + best_normal[2]*best_normal[2]);
                if (wnl > 0.0f) {
                    best_normal[0] /= wnl;
                    best_normal[1] /= wnl;
                    best_normal[2] /= wnl;
                }
            }
        }
    }
    if (!std::isfinite(best_t)) return false;
    out.object_id    = best_oid;
    out.distance     = best_t;
    out.world_pos[0] = origin[0] + best_t * dir[0];
    out.world_pos[1] = origin[1] + best_t * dir[1];
    out.world_pos[2] = origin[2] + best_t * dir[2];
    out.world_normal[0] = best_normal[0];
    out.world_normal[1] = best_normal[1];
    out.world_normal[2] = best_normal[2];
    return true;
}

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

void ViewportWindow::hideSelectedElements() {
    if (selection_.count() == 0) return;
    for (uint32_t id : selection_.selectionIds()) visibility_.hide(id);
    selection_.clear();
    if (isExposed()) requestUpdate();
}

void ViewportWindow::isolateSelectedElements() {
    if (selection_.count() == 0) return;
    // Hide every object in a visible model that isn't in the selection.
    // Model-hidden objects stay model-hidden — element-level hiding on
    // top of that is redundant and just bloats hidden_ids_.
    const auto& sel_ids = selection_.selectionIds();
    for (const auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const InstanceCpu& inst : m.instances) {
            if (inst.object_id == 0) continue;
            if (sel_ids.find(inst.object_id) == sel_ids.end()) {
                visibility_.hide(inst.object_id);
            }
        }
    }
    if (isExposed()) requestUpdate();
}

void ViewportWindow::showAllElements() {
    if (visibility_.hiddenCount() == 0) return;
    visibility_.clear();
    if (isExposed()) requestUpdate();
}

void ViewportWindow::invertElementVisibility() {
    // Compute the new hidden set: every live object_id in a visible model
    // that ISN'T currently hidden. Then swap. Done in two passes so we
    // don't mutate the set we're iterating over.
    std::vector<uint32_t> to_hide;
    to_hide.reserve(1024);
    for (const auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const InstanceCpu& inst : m.instances) {
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
        // world AABB from the cached InstanceCpu directly — same data
        // computeObjectAabb's linear scan would have produced for the
        // first matching instance. For label placement at the AABB
        // centre this is identical-looking; only the rare multi-
        // representation object_id sees a slightly smaller union.
        for (const auto& [mid, m] : models_gpu_) {
            auto it = m.object_id_to_instance.find(oid);
            if (it == m.object_id_to_instance.end()) continue;
            const InstanceCpu& inst = m.instances[it->second];
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

// Project a world point to LOGICAL pixel coords (Qt's mouse-event units).
// Returns false if behind the camera.
static bool projectWorldToLogicalScreen(const Eigen::Matrix4f& vp,
                                        const Eigen::Vector3f& world,
                                        int win_w, int win_h,
                                        Eigen::Vector2f& out) {
    const Eigen::Vector4f clip = vp * Eigen::Vector4f(world.x(), world.y(), world.z(), 1.0f);
    if (clip.w() <= 0.0f) return false;
    const float invw = 1.0f / clip.w();
    out = Eigen::Vector2f(
        (clip.x() * invw * 0.5f + 0.5f) * float(win_w),
        (1.0f - (clip.y() * invw * 0.5f + 0.5f)) * float(win_h));
    return true;
}

int ViewportWindow::hitTestSectionGizmo(int x, int y) const {
    if (section_planes_.empty()) return -1;
    const int w = width();
    const int h = height();
    if (w <= 0 || h <= 0) return -1;
    Eigen::Matrix4f view, proj;
    core_.buildViewProj(view, proj);
    const Eigen::Matrix4f vp = proj * view;
    const float grab_px = 12.0f;
    int   best    = -1;
    float best_d2 = grab_px * grab_px;
    for (int i = 0; i < int(section_planes_.size()); ++i) {
        const SectionPlane& p = section_planes_[i];
        Eigen::Vector2f s_origin, s_tip;
        if (!projectWorldToLogicalScreen(vp, p.origin,
                                         w, h, s_origin)) continue;
        // The gizmo's arrow extends along +n by exactly 1 m in world
        // space — OverlayRenderer::encodeSectionGizmos uses
        // half_size = 1.0 to scale a plane-local arrow tip at z = 1.
        // Mirror that here.
        if (!projectWorldToLogicalScreen(vp, p.origin + p.n * 1.0f,
                                         w, h, s_tip)) continue;
        const Eigen::Vector2f q{float(x), float(y)};
        const Eigen::Vector2f ab = s_tip - s_origin;
        const float ab_len2 = ab.squaredNorm();
        if (ab_len2 < 1e-3f) continue;
        float t = (q - s_origin).dot(ab) / ab_len2;
        t = std::clamp(t, 0.0f, 1.0f);
        const Eigen::Vector2f proj_pt = s_origin + ab * t;
        const float d2 = (q - proj_pt).squaredNorm();
        if (d2 < best_d2) { best_d2 = d2; best = i; }
    }
    return best;
}

void ViewportWindow::updateSectionDrag(int x, int y) {
    if (!section_drag_active_) return;
    if (section_drag_index_ < 0
        || section_drag_index_ >= int(section_planes_.size())) return;
    SectionPlane& p = section_planes_[section_drag_index_];

    const int w = width();
    const int h = height();
    if (w <= 0 || h <= 0) return;
    Eigen::Matrix4f view, proj;
    core_.buildViewProj(view, proj);
    const Eigen::Matrix4f vp = proj * view;

    // Re-project the press-time origin and origin + n to screen space.
    // The press-time origin is what `start` should be relative to — so the
    // plane slides smoothly even as the camera moves (we re-project every
    // frame to handle mid-drag camera rotation cleanly).
    Eigen::Vector2f s_origin, s_n;
    if (!projectWorldToLogicalScreen(vp, section_drag_start_origin_,
                                     w, h, s_origin)) return;
    if (!projectWorldToLogicalScreen(vp, section_drag_start_origin_ + p.n,
                                     w, h, s_n)) return;
    const Eigen::Vector2f screen_axis = s_n - s_origin;
    const float screen_axis_len2 = screen_axis.squaredNorm();
    if (screen_axis_len2 < 1e-3f) return;  // arrow is edge-on

    // Project pixel delta onto the screen-space axis; convert to metres
    // via (delta · axis) / |axis|² (axis is 1 m long in world space).
    const Eigen::Vector2f delta_px(float(x - section_drag_start_mouse_.x()),
                             float(y - section_drag_start_mouse_.y()));
    const float meters = delta_px.dot(screen_axis)
                         / screen_axis_len2;

    p.origin = section_drag_start_origin_ + p.n * meters;
    p.d      = -p.n.dot(p.origin);
    requestUpdate();
}

bool ViewportWindow::buildHizPipeline() {
    // Bind group layout: MSAA depth texture + small uniform.
    WGPUBindGroupLayoutEntry entries[2] = {};
    entries[0].binding = 0;
    entries[0].visibility = WGPUShaderStage_Fragment;
    entries[0].texture.sampleType = WGPUTextureSampleType_Depth;
    entries[0].texture.viewDimension = WGPUTextureViewDimension_2D;
    entries[0].texture.multisampled = 1;
    entries[1].binding = 1;
    entries[1].visibility = WGPUShaderStage_Fragment;
    entries[1].buffer.type = WGPUBufferBindingType_Uniform;
    entries[1].buffer.minBindingSize = 16;  // 4 u32s

    WGPUBindGroupLayoutDescriptor bgl_desc = {};
    bgl_desc.entryCount = 2;
    bgl_desc.entries    = entries;
    bgl_desc.label      = svFromCStr("ifcviewer-wgpu.hiz_bgl");
    hiz_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);

    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 1;
    pl_desc.bindGroupLayouts     = &hiz_bgl_;
    pl_desc.label                = svFromCStr("ifcviewer-wgpu.hiz_pipeline_layout");
    hiz_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    WGPUShaderSourceWGSL wgsl_src = {};
    wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl_src.code        = svFromCStr(HIZ_WGSL);
    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl_src.chain;
    sm_desc.label       = svFromCStr("ifcviewer-wgpu.hiz_wgsl");
    hiz_shader_module_  = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    // Depth-only output, no colour target, no fragment writeout besides
    // frag_depth. Single-sample.
    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_True;
    depth.depthCompare         = WGPUCompareFunction_Always;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = hiz_pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.hiz_pipeline");
    rp_desc.vertex.module       = hiz_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 0;

    WGPUFragmentState frag = {};
    frag.module      = hiz_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 0;  // depth-only
    rp_desc.fragment = &frag;

    rp_desc.depthStencil       = &depth;
    rp_desc.primitive.topology = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode = WGPUCullMode_None;
    rp_desc.multisample.count  = 1;
    rp_desc.multisample.mask   = 0xFFFFFFFFu;

    hiz_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!hiz_pipeline_) {
        Log::warn() << "wgpu hiz pipeline creation failed";
        return false;
    }

    WGPUBufferDescriptor ub_desc = {};
    ub_desc.size  = 16;
    ub_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    ub_desc.label = svFromCStr("ifcviewer-wgpu.hiz_uniform");
    hiz_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &ub_desc);

    return true;
}

void ViewportWindow::ensureHizTextures(int viewport_w, int viewport_h) {
    if (viewport_w <= 0 || viewport_h <= 0) return;

    const uint32_t dst_w = HIZ_BASE_W;
    const uint32_t dst_h = std::max<uint32_t>(
        1, (uint32_t(viewport_h) * dst_w + uint32_t(viewport_w) / 2) / uint32_t(viewport_w));

    if (dst_w == hiz_resolve_w_ && dst_h == hiz_resolve_h_ && hiz_resolve_view_) return;

    if (hiz_resolve_view_)    { wgpuTextureViewRelease(hiz_resolve_view_); hiz_resolve_view_ = nullptr; }
    if (hiz_resolve_texture_) { wgpuTextureRelease(hiz_resolve_texture_);  hiz_resolve_texture_ = nullptr; }
    for (int s = 0; s < HIZ_SLOTS; ++s) {
        if (hiz_staging_buffers_[s]) {
            // Force any pending map to finish before release (defensive: shouldn't happen on resize).
            if (hiz_slot_state_[s] == HizSlotState::Mapped) {
                wgpuBufferUnmap(hiz_staging_buffers_[s]);
            }
            wgpuBufferRelease(hiz_staging_buffers_[s]);
            hiz_staging_buffers_[s] = nullptr;
        }
        hiz_slot_state_[s] = HizSlotState::Idle;
    }
    hiz_write_idx_ = 0;
    hiz_valid_     = false;
    if (hiz_bind_group_)      { wgpuBindGroupRelease(hiz_bind_group_);     hiz_bind_group_ = nullptr; }

    WGPUTextureDescriptor desc = {};
    desc.usage         = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_CopySrc;
    desc.dimension     = WGPUTextureDimension_2D;
    desc.size.width    = dst_w;
    desc.size.height   = dst_h;
    desc.size.depthOrArrayLayers = 1;
    desc.format        = WGPUTextureFormat_Depth32Float;
    desc.mipLevelCount = 1;
    desc.sampleCount   = 1;
    desc.label         = svFromCStr("ifcviewer-wgpu.hiz_resolve");
    hiz_resolve_texture_ = wgpuDeviceCreateTexture(device_, &desc);

    WGPUTextureViewDescriptor vdesc = {};
    vdesc.format          = WGPUTextureFormat_Depth32Float;
    vdesc.dimension       = WGPUTextureViewDimension_2D;
    vdesc.mipLevelCount   = 1;
    vdesc.arrayLayerCount = 1;
    vdesc.aspect          = WGPUTextureAspect_DepthOnly;
    hiz_resolve_view_ = wgpuTextureCreateView(hiz_resolve_texture_, &vdesc);

    // Staging buffers: pad each row to 256-byte alignment. Two slots
    // ping-pong so GPU fill of slot N overlaps CPU read of slot N-1.
    hiz_padded_bpr_ = uint32_t(
        (dst_w * sizeof(float) + WGPU_BYTES_PER_ROW_ALIGN - 1)
        / WGPU_BYTES_PER_ROW_ALIGN * WGPU_BYTES_PER_ROW_ALIGN);
    for (int s = 0; s < HIZ_SLOTS; ++s) {
        WGPUBufferDescriptor bdesc = {};
        bdesc.size  = uint64_t(hiz_padded_bpr_) * uint64_t(dst_h);
        bdesc.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        bdesc.label = svFromCStr(s == 0 ? "ifcviewer-wgpu.hiz_staging[0]"
                                        : "ifcviewer-wgpu.hiz_staging[1]");
        hiz_staging_buffers_[s] = wgpuDeviceCreateBuffer(device_, &bdesc);
    }

    hiz_resolve_w_ = dst_w;
    hiz_resolve_h_ = dst_h;
    hiz_valid_     = false;  // pyramid stale until next readback
}

void ViewportWindow::releaseHizResources() {
    if (hiz_bind_group_)      { wgpuBindGroupRelease(hiz_bind_group_);     hiz_bind_group_ = nullptr; }
    if (hiz_uniform_buffer_)  { wgpuBufferRelease(hiz_uniform_buffer_);    hiz_uniform_buffer_ = nullptr; }
    if (hiz_resolve_view_)    { wgpuTextureViewRelease(hiz_resolve_view_); hiz_resolve_view_ = nullptr; }
    if (hiz_resolve_texture_) { wgpuTextureRelease(hiz_resolve_texture_);  hiz_resolve_texture_ = nullptr; }
    for (int s = 0; s < HIZ_SLOTS; ++s) {
        if (hiz_staging_buffers_[s]) {
            if (hiz_slot_state_[s] == HizSlotState::Mapped) {
                wgpuBufferUnmap(hiz_staging_buffers_[s]);
            }
            wgpuBufferRelease(hiz_staging_buffers_[s]);
            hiz_staging_buffers_[s] = nullptr;
        }
        hiz_slot_state_[s] = HizSlotState::Idle;
    }
    hiz_write_idx_ = 0;
    if (hiz_pipeline_)        { wgpuRenderPipelineRelease(hiz_pipeline_);  hiz_pipeline_ = nullptr; }
    if (hiz_shader_module_)   { wgpuShaderModuleRelease(hiz_shader_module_); hiz_shader_module_ = nullptr; }
    if (hiz_pipeline_layout_) { wgpuPipelineLayoutRelease(hiz_pipeline_layout_); hiz_pipeline_layout_ = nullptr; }
    if (hiz_bgl_)             { wgpuBindGroupLayoutRelease(hiz_bgl_);      hiz_bgl_ = nullptr; }
    hiz_resolve_w_ = hiz_resolve_h_ = hiz_padded_bpr_ = 0;
    hiz_valid_ = false;
    hiz_pyramid_.clear();
    hiz_mip_offset_.clear();
    hiz_mip_w_.clear();
    hiz_mip_h_.clear();
}

int ViewportWindow::encodeHizResolve(WGPUCommandEncoder enc) {
    if (!hiz_enabled_ || !hiz_pipeline_ || !hiz_resolve_view_ || !depth_view_) return -1;

    // Pick an idle ping-pong slot. If both slots are in flight, skip the
    // resolve for this frame — the cull keeps using whatever pyramid we
    // already built (slightly more stale than usual, but never blocks).
    int slot = -1;
    for (int s = 0; s < HIZ_SLOTS; ++s) {
        const int idx = (hiz_write_idx_ + s) % HIZ_SLOTS;
        if (hiz_slot_state_[idx] == HizSlotState::Idle) { slot = idx; break; }
    }
    if (slot < 0) return -1;
    hiz_write_idx_ = (slot + 1) % HIZ_SLOTS;

    // (Re)build the bind group every frame is wasteful; only rebuild when the
    // depth view itself was replaced (driven by surface resize). For now we
    // recreate lazily — fine for the per-frame cost (couple of µs).
    if (!hiz_bind_group_) {
        WGPUBindGroupEntry entries[2] = {};
        entries[0].binding     = 0;
        entries[0].textureView = depth_view_;
        entries[1].binding     = 1;
        entries[1].buffer      = hiz_uniform_buffer_;
        entries[1].size        = 16;
        WGPUBindGroupDescriptor bg = {};
        bg.layout     = hiz_bgl_;
        bg.entryCount = 2;
        bg.entries    = entries;
        bg.label      = svFromCStr("ifcviewer-wgpu.hiz_bind_group");
        hiz_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg);
    }

    const uint32_t uniforms[4] = {
        uint32_t(depth_w_), uint32_t(depth_h_),
        hiz_resolve_w_, hiz_resolve_h_,
    };
    wgpuQueueWriteBuffer(queue_, hiz_uniform_buffer_, 0, uniforms, sizeof(uniforms));

    WGPURenderPassDepthStencilAttachment depth_att = {};
    depth_att.view              = hiz_resolve_view_;
    depth_att.depthLoadOp       = WGPULoadOp_Clear;
    depth_att.depthStoreOp      = WGPUStoreOp_Store;
    depth_att.depthClearValue   = 0.0f;  // start at "nearest"; shader writes max
    depth_att.stencilLoadOp     = WGPULoadOp_Undefined;
    depth_att.stencilStoreOp    = WGPUStoreOp_Undefined;
    depth_att.depthReadOnly     = false;
    depth_att.stencilReadOnly   = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 0;
    pass_desc.depthStencilAttachment = &depth_att;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.hiz_resolve_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetPipeline(pass, hiz_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, hiz_bind_group_, 0, nullptr);
    wgpuRenderPassEncoderDraw(pass, 3, 1, 0, 0);
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    // Copy the small resolved depth texture into the chosen staging slot.
    WGPUTexelCopyTextureInfo src = {};
    src.texture = hiz_resolve_texture_;
    src.aspect  = WGPUTextureAspect_DepthOnly;

    WGPUTexelCopyBufferInfo dst = {};
    dst.buffer              = hiz_staging_buffers_[slot];
    dst.layout.bytesPerRow  = hiz_padded_bpr_;
    dst.layout.rowsPerImage = hiz_resolve_h_;

    WGPUExtent3D extent = {};
    extent.width  = hiz_resolve_w_;
    extent.height = hiz_resolve_h_;
    extent.depthOrArrayLayers = 1;

    wgpuCommandEncoderCopyTextureToBuffer(enc, &src, &dst, &extent);
    return slot;
}

void ViewportWindow::startHizMap(int slot, const Eigen::Matrix4f& vp_used) {
    if (slot < 0 || slot >= HIZ_SLOTS) return;
    if (!hiz_staging_buffers_[slot] || hiz_resolve_w_ == 0) return;

    hiz_slot_vp_[slot]   = vp_used;
    hiz_slot_state_[slot] = HizSlotState::Mapping;

    struct MapCtx { ViewportWindow* self; int slot; };
    auto* ctx = new MapCtx{ this, slot };

    WGPUBufferMapCallbackInfo mcb = {};
    mcb.mode = WGPUCallbackMode_AllowProcessEvents;
    mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                      void* ud1, void* /*ud2*/) {
        auto* c = static_cast<MapCtx*>(ud1);
        if (status == WGPUMapAsyncStatus_Success) {
            c->self->hiz_slot_state_[c->slot] = HizSlotState::Mapped;
        } else {
            c->self->hiz_slot_state_[c->slot] = HizSlotState::Idle;
        }
        delete c;
    };
    mcb.userdata1 = ctx;

    const size_t map_size = size_t(hiz_padded_bpr_) * size_t(hiz_resolve_h_);
    wgpuBufferMapAsync(hiz_staging_buffers_[slot], WGPUMapMode_Read,
                       0, map_size, mcb);
}

void ViewportWindow::drainHizReadbacks() {
    if (!hiz_enabled_ || hiz_resolve_w_ == 0) return;
    // Process any callbacks that have fired since last frame. Does NOT block:
    // wgpuInstanceProcessEvents returns immediately after running ready
    // callbacks. The mapAsync mode is AllowProcessEvents, so this is the
    // correct drainage point.
    wgpuInstanceProcessEvents(instance_);

    for (int slot = 0; slot < HIZ_SLOTS; ++slot) {
        if (hiz_slot_state_[slot] != HizSlotState::Mapped) continue;

        const size_t map_size = size_t(hiz_padded_bpr_) * size_t(hiz_resolve_h_);
        const uint8_t* mapped = static_cast<const uint8_t*>(
            wgpuBufferGetConstMappedRange(hiz_staging_buffers_[slot], 0, map_size));

        const uint32_t W0 = hiz_resolve_w_;
        const uint32_t H0 = hiz_resolve_h_;

        // (Re)build mip pyramid metadata if dimensions changed.
        if (hiz_mip_offset_.empty()
            || hiz_mip_w_.empty() || hiz_mip_w_[0] != W0
            || hiz_mip_h_.empty() || hiz_mip_h_[0] != H0) {
            hiz_mip_offset_.clear();
            hiz_mip_w_.clear();
            hiz_mip_h_.clear();
            uint32_t total = 0;
            uint32_t w = W0, h = H0;
            while (true) {
                hiz_mip_offset_.push_back(total);
                hiz_mip_w_.push_back(w);
                hiz_mip_h_.push_back(h);
                total += w * h;
                if (w == 1 && h == 1) break;
                // Ceil rather than floor when halving. With floor a mip-0
                // row of H0-1 maps to ly = (H0-1)>>level which can land
                // outside floor(H0/2^level) entirely — the bottom (and
                // right) rows of mip 0 then never propagate into coarse
                // mips, so lookups for AABBs near those edges land in an
                // empty sample range with the initial max_d=0 and reject
                // everything. Ceil gives every parent row a child texel.
                w = std::max(1u, (w + 1u) / 2u);
                h = std::max(1u, (h + 1u) / 2u);
            }
            hiz_pyramid_.assign(total, 0.0f);
        }

        // Mip 0: strip per-row padding.
        for (uint32_t y = 0; y < H0; ++y) {
            std::memcpy(&hiz_pyramid_[y * W0],
                        mapped + size_t(y) * hiz_padded_bpr_,
                        W0 * sizeof(float));
        }
        wgpuBufferUnmap(hiz_staging_buffers_[slot]);
        hiz_slot_state_[slot] = HizSlotState::Idle;

        // Higher mips: max-reduce 2×2 children.
        for (size_t L = 1; L < hiz_mip_offset_.size(); ++L) {
            const uint32_t prev_w = hiz_mip_w_[L - 1];
            const uint32_t prev_h = hiz_mip_h_[L - 1];
            const uint32_t this_w = hiz_mip_w_[L];
            const uint32_t this_h = hiz_mip_h_[L];
            const float* src = &hiz_pyramid_[hiz_mip_offset_[L - 1]];
            float*       dst = &hiz_pyramid_[hiz_mip_offset_[L]];
            for (uint32_t y = 0; y < this_h; ++y) {
                for (uint32_t x = 0; x < this_w; ++x) {
                    const uint32_t x0 = std::min(prev_w - 1, x * 2u);
                    const uint32_t y0 = std::min(prev_h - 1, y * 2u);
                    const uint32_t x1 = std::min(prev_w - 1, x0 + 1u);
                    const uint32_t y1 = std::min(prev_h - 1, y0 + 1u);
                    const float a = src[y0 * prev_w + x0];
                    const float b = src[y0 * prev_w + x1];
                    const float c = src[y1 * prev_w + x0];
                    const float d = src[y1 * prev_w + x1];
                    dst[y * this_w + x] = std::max(std::max(a, b), std::max(c, d));
                }
            }
        }

        hiz_vp_    = hiz_slot_vp_[slot];
        hiz_valid_ = true;
    }
}

bool ViewportWindow::aabbOccludedByHiz(const float mn[3], const float mx[3]) const {
    if (!hiz_valid_ || hiz_mip_offset_.empty()) return false;

    // Project the 8 corners of the AABB. Track:
    //   - min/max NDC x,y (screen-space bounds)
    //   - min projected z (nearest point of the AABB to the camera)
    //   - whether any corner has clip.w <= 0 (AABB straddles near plane)
    const float* m = hiz_vp_.data();  // column-major
    auto applyVp = [m](float x, float y, float z, float out[4]) {
        out[0] = m[0]*x + m[4]*y + m[8] *z + m[12];
        out[1] = m[1]*x + m[5]*y + m[9] *z + m[13];
        out[2] = m[2]*x + m[6]*y + m[10]*z + m[14];
        out[3] = m[3]*x + m[7]*y + m[11]*z + m[15];
    };

    float nx_lo =  std::numeric_limits<float>::infinity();
    float ny_lo =  std::numeric_limits<float>::infinity();
    float nx_hi = -std::numeric_limits<float>::infinity();
    float ny_hi = -std::numeric_limits<float>::infinity();
    float min_z =  std::numeric_limits<float>::infinity();
    for (int i = 0; i < 8; ++i) {
        const float x = (i & 1) ? mx[0] : mn[0];
        const float y = (i & 2) ? mx[1] : mn[1];
        const float z = (i & 4) ? mx[2] : mn[2];
        float c[4]; applyVp(x, y, z, c);
        if (c[3] <= 1e-4f) return false;       // straddles or behind near
        const float inv_w = 1.0f / c[3];
        const float ndc_x = c[0] * inv_w;
        const float ndc_y = c[1] * inv_w;
        const float ndc_z = c[2] * inv_w;
        nx_lo = std::min(nx_lo, ndc_x);
        ny_lo = std::min(ny_lo, ndc_y);
        nx_hi = std::max(nx_hi, ndc_x);
        ny_hi = std::max(ny_hi, ndc_y);
        min_z = std::min(min_z, ndc_z);
    }

    // Outside NDC entirely → frustum cull already handled this, but be safe.
    if (nx_hi < -1.0f || nx_lo > 1.0f || ny_hi < -1.0f || ny_lo > 1.0f) return false;
    if (min_z < 0.0f) return false;  // crosses near plane

    // Convert NDC AABB to pyramid-pixel AABB at mip 0.
    // NDC y is +up; HiZ-texture y is +down (the resolve shader's
    // builtin-position fragment coords are framebuffer-space which
    // is +Y-down). v = 0.5 * (1 - ny) gives the mapping.
    const uint32_t W0 = hiz_mip_w_[0];
    const uint32_t H0 = hiz_mip_h_[0];
    const float u_lo =  0.5f * (nx_lo + 1.0f);
    const float u_hi =  0.5f * (nx_hi + 1.0f);
    const float v_lo =  0.5f * (1.0f - ny_hi);
    const float v_hi =  0.5f * (1.0f - ny_lo);
    int x0 = std::max(0, int(std::floor(u_lo * float(W0))));
    int x1 = std::min(int(W0) - 1, int(std::ceil (u_hi * float(W0))));
    int y0 = std::max(0, int(std::floor(v_lo * float(H0))));
    int y1 = std::min(int(H0) - 1, int(std::ceil (v_hi * float(H0))));
    if (x1 < x0 || y1 < y0) return false;

    // Pick the smallest mip level where the AABB covers ≤ 2 texels per axis.
    // Stops at the coarsest level so 1×1 always works.
    const int side = std::max(x1 - x0 + 1, y1 - y0 + 1);
    int level = 0;
    while (level + 1 < int(hiz_mip_offset_.size()) && (1 << level) < side) ++level;

    const uint32_t lw = hiz_mip_w_[level];
    const uint32_t lh = hiz_mip_h_[level];
    // Clamp BOTH endpoints to the mip's valid range. ly0 / lx0 also need
    // to be clamped on the upper end — without that, an AABB whose
    // bottom touches NDC y = -1 (or right touches +1) shifts to a child
    // texel index that exceeds the mip's dimensions, the loop never
    // iterates, and max_d stays at its 0.0 initial value → false reject.
    // The ceil-mip construction above prevents this in the common case,
    // but this guard makes the lookup robust to any future mip-sizing
    // change too.
    const int lx0 = std::clamp(int(x0) >> level, 0, int(lw) - 1);
    const int ly0 = std::clamp(int(y0) >> level, 0, int(lh) - 1);
    const int lx1 = std::clamp(int(x1) >> level, 0, int(lw) - 1);
    const int ly1 = std::clamp(int(y1) >> level, 0, int(lh) - 1);
    if (lx0 > lx1 || ly0 > ly1) return false;  // empty sample range

    const float* level_data = &hiz_pyramid_[hiz_mip_offset_[level]];
    float max_d = 0.0f;
    for (int y = ly0; y <= ly1; ++y) {
        for (int x = lx0; x <= lx1; ++x) {
            max_d = std::max(max_d, level_data[y * int(lw) + x]);
        }
    }

    // AABB occluded iff its nearest projected z is BEHIND the depth pyramid's
    // coverage (greater in WebGPU's [0,1] z, where 0 is near, 1 is far).
    // No epsilon: min_z is a strict lower bound on the AABB's actual mesh
    // depth (it's the closest corner of the conservative bounding box), so
    // min_z > max_d implies actual_mesh_depth > max_d.
    const bool rejected = (min_z > max_d);

    // WGPU_HIZ_TRACE diagnostic. Decrement the shared budget atomically
    // and log when this rejection got a slot. Logs target the post-stop
    // false-rejection class of bug — fields are everything needed to
    // reconstruct the decision: AABB world bounds, screen NDC bounds,
    // mip level and sample rect, max_d sampled, min_z computed, gap.
    if (rejected && hiz_trace_budget_.load(std::memory_order_relaxed) > 0) {
        int prev = hiz_trace_budget_.fetch_sub(1, std::memory_order_relaxed);
        if (prev > 0) {
            Log::info().noquote().nospace()
                << "[hiz reject] aabb_min=(" << mn[0] << "," << mn[1] << "," << mn[2] << ")"
                << " aabb_max=(" << mx[0] << "," << mx[1] << "," << mx[2] << ")"
                << " ndc_x=[" << nx_lo << "," << nx_hi << "]"
                << " ndc_y=[" << ny_lo << "," << ny_hi << "]"
                << " min_z=" << min_z << " max_d=" << max_d
                << " gap=" << (min_z - max_d)
                << " level=" << level
                << " sample=(" << lx0 << "," << ly0 << ")-(" << lx1 << "," << ly1 << ")"
                << " mip=" << lw << "x" << lh;
        }
    }
    return rejected;
}

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
    // Time the whole render() body (cull + encode + present) for the
    // benchmark stats. Started before any wgpu work so cull is included.
    Stopwatch frame_timer;
    frame_timer.start();

    // Advance fly-mode camera by wall-clock dt since the last frame so the
    // frame we're about to render already reflects the move. Driving this
    // from render() (rather than a QTimer) means a long frame costs one
    // missed step, not a backlog.
    fpsIntegrate();

    // Drain any HiZ async readbacks that completed since last frame so the
    // pyramid is as fresh as it can be before cull runs.
    if (hiz_enabled_) drainHizReadbacks();

    // Flush any pending selection changes to GPU.
    uploadSelectionFlagsIfDirty();

    WGPUSurfaceTexture surf_tex = {};
    wgpuSurfaceGetCurrentTexture(surface_, &surf_tex);

    switch (surf_tex.status) {
        case WGPUSurfaceGetCurrentTextureStatus_SuccessOptimal:
        case WGPUSurfaceGetCurrentTextureStatus_SuccessSuboptimal:
            break;  // proceed
        case WGPUSurfaceGetCurrentTextureStatus_Timeout:
        case WGPUSurfaceGetCurrentTextureStatus_Outdated:
        case WGPUSurfaceGetCurrentTextureStatus_Lost: {
            // Reconfigure and try again next frame.
            const int w = int(width()  * devicePixelRatio());
            const int h = int(height() * devicePixelRatio());
            if (w > 0 && h > 0) configureSurface(w, h);
            requestUpdate();
            return;
        }
        default:
            Log::warn() << "GetCurrentTexture status" << int(surf_tex.status);
            return;
    }

    WGPUTextureView view = wgpuTextureCreateView(surf_tex.texture, nullptr);

    core_.updateFrameUniforms();

    // Per-frame cull: extract frustum planes from the same VP we just wrote
    // into the uniform, then run cullModelCpu on every visible model. The
    // cull writes its results directly into each model's visible_buffer via
    // wgpuQueueWriteBuffer — these writes are sequenced before the draw
    // commands we encode next.
    last_visible_objects_   = 0;
    last_visible_triangles_ = 0;
    last_sub_draws_         = 0;
    hiz_reject_count_       = 0;
    Stopwatch cull_timer;
    cull_timer.start();
    Eigen::Matrix4f vp_this_frame;
    {
        const Eigen::Vector3f target(camera_target_[0], camera_target_[1], camera_target_[2]);
        const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                       camera_yaw_deg_, camera_pitch_deg_);
        Eigen::Matrix4f v, p;
        core_.buildViewProj(v, p);
        const Eigen::Matrix4f vp = p * v;
        vp_this_frame = vp;
        float planes[6][4];
        extractFrustumPlanes(vp.data(), planes);

        // LOD pick inputs: world-space eye, unit forward, vertical focal in
        // pixels. focal_px maps view-space depth to projected radius:
        //   projected_px = world_radius * focal_px / view_z.
        const Eigen::Vector3f fwd_q = (target - eye).normalized();
        // World-up convention: Z-up. Near the poles lookAt degenerates,
        // so swap to Y-up — mirrors buildViewProj's pitch gate at line
        // 4701 so cull's camera basis matches the actual view matrix.
        const Eigen::Vector3f world_up = (std::abs(camera_pitch_deg_) >= 89.0f)
                                     ? Eigen::Vector3f(0.0f, 1.0f, 0.0f)
                                     : Eigen::Vector3f(0.0f, 0.0f, 1.0f);
        const Eigen::Vector3f right_q  = fwd_q.cross(world_up).normalized();
        const Eigen::Vector3f up_q     = right_q.cross(fwd_q).normalized();
        const float eye_a[3]   = { eye.x(),     eye.y(),     eye.z()    };
        const float fwd_a[3]   = { fwd_q.x(),   fwd_q.y(),   fwd_q.z()  };
        const float right_a[3] = { right_q.x(), right_q.y(), right_q.z() };
        const float up_a[3]    = { up_q.x(),    up_q.y(),    up_q.z()    };
        const float focal_px = (configured_h_ > 0)
            ? (0.5f * float(configured_h_)
                / std::tan(qDegreesToRadians(camera_fov_y_deg_) * 0.5f))
            : 0.0f;

        // Motion detection: any change in camera state since last frame
        // bumps the contribution threshold to motion_min_pixel_radius_
        // (mirrors GL's NavPreset behaviour, drops more sub-pixel work
        // during orbit/pan/zoom).
        const bool camera_moved = has_prev_camera_
            && (camera_target_[0] != prev_camera_target_[0]
             || camera_target_[1] != prev_camera_target_[1]
             || camera_target_[2] != prev_camera_target_[2]
             || camera_distance_  != prev_camera_distance_
             || camera_yaw_deg_   != prev_camera_yaw_deg_
             || camera_pitch_deg_ != prev_camera_pitch_deg_);
        const bool use_motion_threshold =
            camera_moved && motion_min_pixel_radius_ > min_pixel_radius_;
        const float effective_min_px =
            use_motion_threshold ? motion_min_pixel_radius_ : min_pixel_radius_;
        last_cull_was_motion_ = use_motion_threshold;

        // HiZ stale-VP gate. The depth pyramid is async — the pyramid
        // resident in hiz_pyramid_ was captured one or more frames ago
        // at hiz_vp_. If the current VP differs, AABBs project through
        // a stale matrix to wrong screen-space positions and sample
        // depth captured for what was at THOSE positions in the old
        // view — incorrect rejections. Strict by default: HiZ on only
        // when current VP exactly matches the pyramid's. WGPU_HIZ_MOTION=1
        // trusts the stale pyramid across motion (matches GL's default
        // behaviour; the env var name mirrors GL's IFC_HIZ_MOTION knob
        // but the wgpu default is inverted toward strictness).
        static const bool hiz_trust_stale = []{
            const char* e = std::getenv("WGPU_HIZ_MOTION");
            return e && e[0] == '1';
        }();
        const bool hiz_vp_matches = hiz_valid_
            && (hiz_trust_stale || hiz_vp_ == vp_this_frame);
        const bool hiz_for_this_frame = hiz_enabled_ && hiz_vp_matches;

        // WGPU_HIZ_TRACE: arm rejection logging when HiZ is about to
        // fire post-settle. Reports per-frame budget, dumps a snapshot
        // of the pyramid's bottom rows (the band the post-stop bug
        // manifests in), and the per-rejection details land via the
        // hiz_trace_budget_ atomic checked inside aabbOccludedByHiz.
        static const bool hiz_trace_on = []{
            const char* e = std::getenv("WGPU_HIZ_TRACE");
            return e && e[0] == '1';
        }();
        if (hiz_trace_on && hiz_for_this_frame) {
            constexpr int kHizTracePerFrame = 12;
            hiz_trace_budget_.store(kHizTracePerFrame, std::memory_order_relaxed);
            // One-shot per-frame log so the user can correlate rejections
            // with what they were looking at.
            Log::info().noquote().nospace()
                << "[hiz trace] frame: vp_match="
                << (hiz_vp_ == vp_this_frame ? "exact" : "loose")
                << " pyramid_mip0=" << hiz_mip_w_[0] << "x" << hiz_mip_h_[0]
                << " budget=" << kHizTracePerFrame;
            // Dump the bottom 3 rows of mip 0, evenly sampled across width.
            // If the bug is "pyramid bottom rows hold near-zero depth"
            // these values will be visibly small.
            const uint32_t W0 = hiz_mip_w_[0];
            const uint32_t H0 = hiz_mip_h_[0];
            const float* L0 = &hiz_pyramid_[hiz_mip_offset_[0]];
            for (int dy = 2; dy >= 0; --dy) {
                const uint32_t y = H0 - 1 - uint32_t(dy);
                QString row;
                for (int s = 0; s < 8; ++s) {
                    const uint32_t x = (s * (W0 - 1)) / 7;
                    row += QString::asprintf("%.4f ", L0[y * W0 + x]);
                }
                Log::info().noquote().nospace()
                    << "[hiz trace] pyramid row " << y << " (8 samples): " << row;
            }
        } else if (hiz_trace_on) {
            hiz_trace_budget_.store(0, std::memory_order_relaxed);
        }

        // HiZ occlusion callback. Null when HiZ is disabled or its VP is
        // stale; otherwise wraps aabbOccludedByHiz (still VW-side because
        // the HiZ pyramid + readback orchestration hasn't migrated yet).
        // The pyramid's reads are atomic-friendly, so the parallel cull
        // workers can share this callback safely.
        ViewportCore::HizOccludedFn hiz_occluded;
        if (hiz_for_this_frame) {
            hiz_occluded = [this](const float mn[3], const float mx[3]) {
                return aabbOccludedByHiz(mn, mx);
            };
        }

        // Cull each model on its own worker thread. wgpu queue writes are
        // serialised on the main thread after the parallel compute joins —
        // wgpu-native doesn't guarantee thread-safety on queue ops.
        // WGPU_CULL_THREADS=0 forces the sequential path for measurement.
        if (cull_threads_enabled_) {
            std::vector<std::pair<uint32_t, std::future<uint32_t>>> futures;
            futures.reserve(models_gpu_.size());
            for (auto& [mid, m] : models_gpu_) {
                if (m.hidden) continue;
                auto& m_ref = m;
                futures.emplace_back(mid, std::async(std::launch::async,
                    [this, &m_ref, &planes, &eye_a, &fwd_a, &right_a, &up_a,
                     focal_px, effective_min_px, &hiz_occluded]() {
                        return core_.cullModelCpuCompute(
                            m_ref, planes, eye_a, fwd_a, right_a, up_a,
                            focal_px,
                            effective_min_px, lod1_pixel_threshold_,
                            hiz_occluded);
                    }));
            }
            for (auto& [mid, fut] : futures) {
                hiz_reject_count_ += fut.get();
            }
        } else {
            for (auto& [mid, m] : models_gpu_) {
                if (m.hidden) continue;
                hiz_reject_count_ += core_.cullModelCpuCompute(
                    m, planes, eye_a, fwd_a, right_a, up_a, focal_px,
                    effective_min_px, lod1_pixel_threshold_,
                    hiz_occluded);
            }
        }

        // Split timer: how much of the "cull" cost is the upload phase
        // (sequential queueWriteBuffer × 3 per resident chunk × ~120
        // chunks ≈ 360 wgpu calls/frame). If upload >> compute the parallel
        // cull is doing its job and the bottleneck is somewhere else.
        const double cull_compute_ms = double(cull_timer.nsecsElapsed()) / 1e6;
        Stopwatch upload_timer;
        upload_timer.start();
        for (auto& [mid, m] : models_gpu_) {
            if (m.hidden) continue;
            core_.cullModelCpuUpload(m);
            for (const auto& c : m.chunks) {
                last_visible_objects_   += c.total_visible_draws;
                last_visible_triangles_ += c.total_visible_vertices / 3u;
                // One CPU drawcall per non-empty chunk.
                if (c.total_visible_draws > 0) last_sub_draws_ += 1;
            }
        }
        last_cull_compute_ms_ = cull_compute_ms;
        last_cull_upload_ms_  = double(upload_timer.nsecsElapsed()) / 1e6;
    }

    // Stop the cull-only timer before streaming, so the benchmark
    // attribution doesn't lump disk I/O into "cull".
    const double cull_only_ms = double(cull_timer.nsecsElapsed()) / 1e6;
    last_cull_ms_ = cull_only_ms;

    // Streaming: bring non-resident chunks that the cull just flagged
    // visible into residency. Runs before draw encoding so newly-loaded
    // chunks render the same frame. Timed separately because synchronous
    // disk reads here can dwarf the cull itself on big scenes.
    Stopwatch stream_timer;
    stream_timer.start();
    driveStreamingLoads();
    const double stream_ms = double(stream_timer.nsecsElapsed()) / 1e6;
    last_stream_ms_ = stream_ms;

    // Snapshot camera state for next frame's motion detection.
    prev_camera_target_[0] = camera_target_[0];
    prev_camera_target_[1] = camera_target_[1];
    prev_camera_target_[2] = camera_target_[2];
    prev_camera_distance_  = camera_distance_;
    prev_camera_yaw_deg_   = camera_yaw_deg_;
    prev_camera_pitch_deg_ = camera_pitch_deg_;
    has_prev_camera_       = true;
    if (bench_total_ > 0 && bench_count_ >= bench_warmup_) {
        bench_cull_ms_total_   += cull_only_ms;
        bench_stream_ms_total_ += stream_ms;
    }

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    WGPURenderPassColorAttachment color = {};
    color.view          = msaa_color_view_;  // render into 4× MSAA target
    color.resolveTarget = view;              // resolve to surface texture
    color.loadOp        = WGPULoadOp_Clear;
    color.storeOp       = WGPUStoreOp_Store;
    color.clearValue    = {
        srgbToLinear(background_color_[0]),
        srgbToLinear(background_color_[1]),
        srgbToLinear(background_color_[2]),
        1.0,
    };
    color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDepthStencilAttachment depth = {};
    depth.view              = depth_view_;
    depth.depthLoadOp       = WGPULoadOp_Clear;
    depth.depthStoreOp      = WGPUStoreOp_Store;
    depth.depthClearValue   = 1.0f;
    depth.stencilLoadOp     = WGPULoadOp_Undefined;
    depth.stencilStoreOp    = WGPUStoreOp_Undefined;
    depth.depthReadOnly     = false;
    depth.stencilReadOnly   = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount = 1;
    pass_desc.colorAttachments     = &color;
    pass_desc.depthStencilAttachment = depth_view_ ? &depth : nullptr;

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);

    // Two-pass main render: opaque first (depth write on, no blend), then
    // transparent (depth write off, alpha blend on). Each chunk's
    // visible_draws_scratch is laid out as [opaque][transparent]; the
    // draw calls slice into the same shared buffer via firstVertex +
    // vertexCount. Skip a half when it's empty.
    if (main_pipeline_ && main_pipeline_transparent_
        && frame_bind_group_ && !models_gpu_.empty()) {
        // ---- Opaque pass ------------------------------------------------
        wgpuRenderPassEncoderSetPipeline(pass, main_pipeline_);
        wgpuRenderPassEncoderSetBindGroup(pass, 0, frame_bind_group_, 0, nullptr);

        for (const auto& [mid, m] : models_gpu_) {
            if (m.hidden) continue;
            for (const auto& c : m.chunks) {
                if (!c.bind_group || c.opaque_visible_vertices == 0) continue;
                wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
                wgpuRenderPassEncoderDraw(pass,
                                          c.opaque_visible_vertices,
                                          1, 0, 0);
            }
        }

        // ---- Transparent pass ------------------------------------------
        // Same bind groups, different pipeline. Each chunk's transparent
        // range starts at firstVertex = opaque_visible_vertices and runs
        // for (total - opaque) vertices.
        wgpuRenderPassEncoderSetPipeline(pass, main_pipeline_transparent_);
        // Frame bind group is already set; bind group 0 layout is identical.

        for (const auto& [mid, m] : models_gpu_) {
            if (m.hidden) continue;
            for (const auto& c : m.chunks) {
                if (!c.bind_group) continue;
                const uint32_t transparent_verts =
                    c.total_visible_vertices - c.opaque_visible_vertices;
                if (transparent_verts == 0) continue;
                wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
                wgpuRenderPassEncoderDraw(pass,
                                          transparent_verts, 1,
                                          c.opaque_visible_vertices, 0);
            }
        }
    }

    // Snapshot the per-frame inputs every overlay needs. Built once and
    // passed by const-ref so OverlayRenderer never reaches back into
    // this viewport.
    OverlayFrame overlay_frame;
    overlay_frame.view_proj          = vp_this_frame;
    overlay_frame.camera_target      = Eigen::Vector3f(camera_target_[0],
                                                 camera_target_[1],
                                                 camera_target_[2]);
    overlay_frame.camera_distance    = camera_distance_;
    overlay_frame.camera_yaw_deg     = camera_yaw_deg_;
    overlay_frame.camera_pitch_deg   = camera_pitch_deg_;
    overlay_frame.camera_fov_y_deg   = camera_fov_y_deg_;
    overlay_frame.viewport_w_px      = int(width()  * devicePixelRatio());
    overlay_frame.viewport_h_px      = int(height() * devicePixelRatio());
    overlay_frame.device_pixel_ratio = int(devicePixelRatio());

    // Section planes — translucent overlay quads showing where each
    // active clip plane cuts. Drawn inside the main MSAA pass.
    overlays_.encodeSectionGizmos(pass, overlay_frame, section_planes_);

    // Highlight triangles (Area-tool patch shading). Drawn inside the
    // main MSAA pass so depth-test correctly hides patches behind closer
    // geometry; depth-write off so the corner gizmo / labels still render
    // on top.
    overlays_.encodeHighlightTriangles(pass, overlay_frame);

    // Pivot indicator. Encoded inside the main MSAA pass after geometry so
    // depth interaction is correct — the indicator vanishes behind closer
    // surfaces. Visibility is driven by orbit/wheel UI handlers.
    overlays_.encodePivot(pass, overlay_frame, pivot_indicator_visible_);

    // Overlay line groups (measurement / dimension annotation lines).
    // Depth-tested against geometry so they hide behind closer surfaces;
    // depth-write off so the corner gizmo + marquee can still draw over
    // them on the resolved surface afterwards.
    overlays_.encodeOverlayLines(pass, overlay_frame);

    // Overlay point sprites (measurement endpoints, snap candidates).
    // Drawn after lines so the sprite halo correctly covers any line
    // ends at the same world position.
    overlays_.encodeOverlayPoints(pass, overlay_frame);

    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    // ---- Edge silhouette post-process — reads MSAA depth, blends dark
    // lines onto the resolved surface colour. Encoded before HiZ resolve
    // so HiZ uses the same MSAA depth that produced the edges.
    if (edges_enabled_) {
        encodeEdgePass(enc, view);
    }

    // Corner axis gizmo. Encoded after the edge pass on the resolved
    // surface, so the laplacian can't darken its lines or its background.
    overlays_.encodeCornerAxis(enc, view, overlay_frame);

    // Marquee box-select drag rect (visible only while a drag is active).
    // Drawn on the resolved surface so the rect outline isn't affected by
    // the edge silhouette pass.
    overlays_.encodeMarquee(enc, view, overlay_frame,
                            box_select_start_pos_,
                            box_select_current_pos_,
                            box_select_active_);

    // Labels + HUD text. Drawn last so they stack on top of every other
    // overlay (no depth test, alpha-blended on the resolved surface).
    overlays_.encodeLabels(enc, view, overlay_frame);

    // ---- HiZ: resolve MSAA depth → small single-sample → ping-pong slot
    int hiz_submitted_slot = -1;
    if (hiz_enabled_) {
        hiz_submitted_slot = encodeHizResolve(enc);
    }

    // ---- Optional capture: encode copy on the same command buffer -------
    WGPUBuffer    capture_buffer    = nullptr;
    uint32_t      capture_padded_bpr = 0;
    const bool    want_capture       = !pending_screenshot_path_.empty();
    if (want_capture) {
        const uint32_t row_bytes_unpadded = uint32_t(configured_w_) * 4u;
        capture_padded_bpr = uint32_t(
            (row_bytes_unpadded + WGPU_BYTES_PER_ROW_ALIGN - 1)
            / WGPU_BYTES_PER_ROW_ALIGN * WGPU_BYTES_PER_ROW_ALIGN);
        const uint64_t total_bytes = uint64_t(capture_padded_bpr) * uint64_t(configured_h_);

        WGPUBufferDescriptor bdesc = {};
        bdesc.size  = total_bytes;
        bdesc.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        bdesc.label = svFromCStr("ifcviewer-wgpu.capture");
        capture_buffer = wgpuDeviceCreateBuffer(device_, &bdesc);

        WGPUTexelCopyTextureInfo src = {};
        src.texture = surf_tex.texture;
        src.aspect  = WGPUTextureAspect_All;

        WGPUTexelCopyBufferInfo dst = {};
        dst.buffer              = capture_buffer;
        dst.layout.bytesPerRow  = capture_padded_bpr;
        dst.layout.rowsPerImage = uint32_t(configured_h_);

        WGPUExtent3D extent = {};
        extent.width  = uint32_t(configured_w_);
        extent.height = uint32_t(configured_h_);
        extent.depthOrArrayLayers = 1;

        wgpuCommandEncoderCopyTextureToBuffer(enc, &src, &dst, &extent);
    }

    WGPUCommandBuffer cmd = wgpuCommandEncoderFinish(enc, nullptr);
    wgpuQueueSubmit(queue_, 1, &cmd);

    wgpuCommandBufferRelease(cmd);
    wgpuCommandEncoderRelease(enc);
    wgpuTextureViewRelease(view);

    // ---- Optional capture: map + save PNG -------------------------------
    if (want_capture && capture_buffer) {
        struct MapReq { bool done = false; bool ok = false; };
        MapReq req;

        WGPUBufferMapCallbackInfo mcb = {};
        mcb.mode = WGPUCallbackMode_AllowProcessEvents;
        mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView message,
                          void* ud1, void* /*ud2*/) {
            auto* r = static_cast<MapReq*>(ud1);
            r->done = true;
            r->ok   = (status == WGPUMapAsyncStatus_Success);
            if (!r->ok) {
                Log::warn().noquote() << "wgpu MapAsync failed:" << sv(message);
            }
        };
        mcb.userdata1 = &req;

        const uint64_t total_bytes = uint64_t(capture_padded_bpr) * uint64_t(configured_h_);
        wgpuBufferMapAsync(capture_buffer, WGPUMapMode_Read, 0, size_t(total_bytes), mcb);
        while (!req.done) wgpuInstanceProcessEvents(instance_);

        if (req.ok) {
            const uint8_t* mapped = static_cast<const uint8_t*>(
                wgpuBufferGetConstMappedRange(capture_buffer, 0, size_t(total_bytes)));

            // Assemble tightly-packed RGBA8 image. Surface is BGRA8 on most
            // backends (we saw format=28 = BGRA8Unorm), so swap R/B on the
            // fly. If a future surface_format_ is RGBA8, just memcpy.
            const bool is_bgra =
                surface_format_ == WGPUTextureFormat_BGRA8Unorm ||
                surface_format_ == WGPUTextureFormat_BGRA8UnormSrgb;
            const uint32_t w = uint32_t(configured_w_);
            const uint32_t h = uint32_t(configured_h_);
            QImage img(int(w), int(h), QImage::Format_RGBA8888);
            for (uint32_t y = 0; y < h; ++y) {
                const uint8_t* src_row = mapped + size_t(y) * capture_padded_bpr;
                uint8_t*       dst_row = img.scanLine(int(y));
                if (is_bgra) {
                    for (uint32_t x = 0; x < w; ++x) {
                        dst_row[x * 4 + 0] = src_row[x * 4 + 2];  // R <- B
                        dst_row[x * 4 + 1] = src_row[x * 4 + 1];  // G
                        dst_row[x * 4 + 2] = src_row[x * 4 + 0];  // B <- R
                        dst_row[x * 4 + 3] = src_row[x * 4 + 3];  // A
                    }
                } else {
                    std::memcpy(dst_row, src_row, size_t(w) * 4);
                }
            }
            wgpuBufferUnmap(capture_buffer);

            const QString qpath = QString::fromStdString(pending_screenshot_path_);
            if (img.save(qpath, "PNG")) {
                Log::info().noquote() << "[wgpu] saved screenshot: "
                                  << pending_screenshot_path_ << " (" << w << "x" << h << ")";
            } else {
                Log::warn().noquote() << "[wgpu] QImage::save failed for "
                                     << pending_screenshot_path_;
            }
        }
        wgpuBufferRelease(capture_buffer);

        const bool quit_after = pending_screenshot_quit_;
        pending_screenshot_path_.clear();
        pending_screenshot_quit_ = false;
        if (quit_after) QCoreApplication::quit();
    }

    // Emit per-frame stats before present so external listeners (bonsai's
    // status bar) see fresh numbers in the same UI tick. fps is a
    // rolling 60-sample average; the first window after startup is
    // computed against the partial sample count so the readout settles
    // immediately rather than starting at 0.
    {
        const double this_frame_ms =
            double(frame_timer.nsecsElapsed()) / 1e6;
        frame_time_ms_sum_ -= frame_time_ms_window_[frame_time_ms_head_];
        frame_time_ms_window_[frame_time_ms_head_] = this_frame_ms;
        frame_time_ms_sum_ += this_frame_ms;
        frame_time_ms_head_ = (frame_time_ms_head_ + 1) % FRAME_TIME_WINDOW;
        if (frame_time_ms_count_ < FRAME_TIME_WINDOW) ++frame_time_ms_count_;
        const double avg_ms = frame_time_ms_count_ > 0
            ? frame_time_ms_sum_ / double(frame_time_ms_count_)
            : 0.0;

        uint32_t total_obj = 0, total_tri = 0, total_meshes = 0;
        for (const auto& [mid, mm] : models_gpu_) {
            total_obj    += uint32_t(mm.instances.size());
            total_tri    += mm.index_count / 3;
            total_meshes += uint32_t(mm.meshes.size());
        }

        FrameStats stats;
        stats.fps               = avg_ms > 0.0 ? float(1000.0 / avg_ms) : 0.0f;
        stats.frame_time_ms     = float(avg_ms);
        stats.total_objects     = total_obj;
        stats.visible_objects   = last_visible_objects_;
        stats.total_triangles   = total_tri;
        stats.visible_triangles = last_visible_triangles_;
        stats.unique_meshes     = total_meshes;
        // Wgpu does one indirect dispatch per resident chunk; mirror that
        // into the GL-named field bonsai's status string consumes.
        uint32_t draw_calls = 0;
        for (const auto& [mid, mm] : models_gpu_) {
            if (mm.hidden) continue;
            for (const auto& c : mm.chunks) {
                if (c.is_resident && c.total_visible_draws > 0) ++draw_calls;
            }
        }
        stats.gl_draw_calls      = draw_calls;
        stats.indirect_sub_draws = last_sub_draws_;
        emit frameStatsUpdated(stats);
    }

    wgpuSurfacePresent(surface_);
    wgpuTextureRelease(surf_tex.texture);

    // Settle frame: if this frame applied the motion contribution threshold,
    // schedule one more frame so the camera-now-stopped state recomputes
    // the cull at the still threshold and the previously dropped sub-pixel
    // instances pop back in. Matches GL's behaviour.
    if (last_cull_was_motion_) requestUpdate();

    // ---- HiZ async readback handoff -------------------------------------
    // Don't block — just kick off the mapAsync for the slot we filled this
    // frame. Drainage happens at the top of the *next* frame via
    // drainHizReadbacks(), giving the GPU at least one frame of headroom.
    if (hiz_enabled_ && hiz_submitted_slot >= 0) {
        Stopwatch hiz_timer;
        if (bench_total_ > 0) hiz_timer.start();
        startHizMap(hiz_submitted_slot, vp_this_frame);
        if (bench_total_ > 0 && bench_count_ >= bench_warmup_) {
            bench_hiz_readback_ms_total_ += double(hiz_timer.nsecsElapsed()) / 1e6;
        }
    }

    // ---- Interactive heartbeat log -------------------------------------
    // Prints a per-frame stats line every 30 frames when not in
    // benchmark mode, so the user can diagnose performance and
    // visibility issues at runtime without firing up --benchmark.
    // Includes "missing" (chunks the cull marked frustum-visible but
    // are not resident this frame) — that's the diagnostic for "things
    // I expected to see aren't showing up." Healthy steady state has
    // missing == 0; pool-bound scenes will show missing > 0 for the
    // chunks that don't fit.
    if (bench_total_ == 0) {
        ++interactive_frame_count_;
        // Log every render (frames in interactive mode only fire on
        // actual activity — camera motion, model load, streaming loads
        // in flight — so this is naturally rate-limited and shows the
        // user what's happening as they interact).
        {
            const float ms = float(frame_timer.nsecsElapsed()) / 1e6f;
            uint64_t total_vbo = 0, total_ebo = 0, total_ssbo = 0;
            uint32_t total_instances = 0, total_meshes = 0;
            size_t chunks_total = 0, chunks_resident = 0;
            size_t chunks_frustum_vis = 0, chunks_missing = 0;
            for (const auto& [mid, mo] : models_gpu_) {
                total_vbo  += mo.vram_bytes_vbo;
                total_ebo  += mo.vram_bytes_ebo;
                total_ssbo += mo.vram_bytes_ssbo;
                total_instances += mo.instance_count;
                total_meshes    += mo.mesh_count;
                for (const auto& c : mo.chunks) {
                    ++chunks_total;
                    if (c.is_resident) ++chunks_resident;
                    if (c.frustum_visible_count > 0) {
                        ++chunks_frustum_vis;
                        if (!c.is_resident) ++chunks_missing;
                    }
                }
            }
            const double mb = 1.0 / (1024.0 * 1024.0);
            Log::info().noquote().nospace()
                << "[frame] " << QString::number(ms > 0 ? 1000.0f / ms : 0.0f, 'f', 1) << " fps"
                << "  " << QString::number(ms, 'f', 2) << " ms"
                << "  obj " << last_visible_objects_ << "/" << total_instances
                << "  tri " << last_visible_triangles_
                << "  sub_draws " << last_sub_draws_
                << "  hiz_rej " << hiz_reject_count_
                << "  cull " << QString::number(last_cull_ms_, 'f', 2) << "ms"
                << "  stream " << QString::number(last_stream_ms_, 'f', 2) << "ms"
                << "  chunks " << chunks_resident << "/" << chunks_frustum_vis
                << "/" << chunks_total << " (missing " << chunks_missing << ")"
                << "  vram " << QString::number(double(total_vbo + total_ebo + total_ssbo) * mb, 'f', 1) << "MB"
                << "  models " << models_gpu_.size()
                << "  lod1 " << lod1_dbg_count_ << "/" << (lod1_dbg_count_ + lod0_dbg_eligible_count_)
                << " (saved " << lod1_dbg_tris_saved_ << " tris, "
                << lod0_dbg_no_lod1_count_ << " no-lod1)";
            lod1_dbg_count_ = 0;
            lod0_dbg_eligible_count_ = 0;
            lod0_dbg_no_lod1_count_ = 0;
            lod1_dbg_tris_saved_ = 0;

            // Lightweight stream-health summary, every ~5s (300 frames at
            // 60 fps / 5s at 60), only when there's something missing AND
            // something cycling. Single line — no multi-line spew. Tells
            // the user "working set > pool, this many chunks thrashing"
            // without the deep-dump volume.
            if (chunks_missing > 0
                && (interactive_frame_count_ % 300) == 0) {
                size_t cycled = 0;
                uint32_t max_load = 0;
                for (const auto& [mid, mo] : models_gpu_) {
                    for (const auto& c : mo.chunks) {
                        if (c.load_count > 1) ++cycled;
                        if (c.load_count > max_load) max_load = c.load_count;
                    }
                }
                if (cycled > 0 || max_load > 1) {
                    const char* diag = (cycled > 10)
                        ? "thrashing — working set > pool"
                        : (max_load > 5)
                            ? "few chunks cycling (hysteresis boundary)"
                            : "loading";
                    Log::info().noquote().nospace()
                        << "[stream] " << chunks_resident << " resident, "
                        << chunks_missing << " missing, " << cycled
                        << " cycled (max load=" << max_load << ")"
                        << " — " << diag;
                }
            }
            // Verbose investigation dump — top-8 models by missing-count,
            // top 20 missing chunks by priority, bottom 5 residents by
            // effective priority, every chunk of a tracked model. Volume
            // is too high for steady-state console; gated behind
            // WGPU_STREAM_DEEP_DEBUG so it stays available when something
            // needs investigating but doesn't drown the normal log.
            if (chunks_missing > 0
                && std::getenv("WGPU_STREAM_DEEP_DEBUG") != nullptr
                && (interactive_frame_count_ % 120) == 0) {
                // Build the camera VP matrix and project AABB corners
                // — same metric driveStreamingLoads uses for priority,
                // duplicated here so the heartbeat dump can show what
                // the loader is actually scoring chunks at.
                Eigen::Matrix4f v_dbg, p_dbg;
                core_.buildViewProj(v_dbg, p_dbg);
                const Eigen::Matrix4f vp_dbg = p_dbg * v_dbg;
                auto chunk_priority_px2 = [&](const ModelGpuData::Chunk& c) -> float {
                    if (configured_w_ <= 0 || configured_h_ <= 0 ||
                        c.aabb_min[0] > c.aabb_max[0]) return 0.0f;
                    float xmin =  std::numeric_limits<float>::infinity();
                    float ymin =  std::numeric_limits<float>::infinity();
                    float xmax = -std::numeric_limits<float>::infinity();
                    float ymax = -std::numeric_limits<float>::infinity();
                    int   cif  = 0;
                    for (int i = 0; i < 8; ++i) {
                        const Eigen::Vector4f corner(
                            (i & 1) ? c.aabb_max[0] : c.aabb_min[0],
                            (i & 2) ? c.aabb_max[1] : c.aabb_min[1],
                            (i & 4) ? c.aabb_max[2] : c.aabb_min[2],
                            1.0f);
                        const Eigen::Vector4f clip = vp_dbg * corner;
                        if (clip.w() <= 1e-3f) continue;
                        ++cif;
                        const float px_x = (clip.x() / clip.w() * 0.5f + 0.5f) * float(configured_w_);
                        const float px_y = (clip.y() / clip.w() * 0.5f + 0.5f) * float(configured_h_);
                        xmin = std::min(xmin, px_x); ymin = std::min(ymin, px_y);
                        xmax = std::max(xmax, px_x); ymax = std::max(ymax, px_y);
                    }
                    if (cif == 0) return 0.0f;
                    xmin = std::max(xmin, 0.0f); ymin = std::max(ymin, 0.0f);
                    xmax = std::min(xmax, float(configured_w_));
                    ymax = std::min(ymax, float(configured_h_));
                    if (xmax <= xmin || ymax <= ymin) return 0.0f;
                    return (xmax - xmin) * (ymax - ymin);
                };
                struct Probe {
                    QString name;
                    float   priority;
                    float   ex, ey, ez;
                    float   history;
                };
                std::vector<Probe> missing_set, resident_set;
                missing_set.reserve(64);
                resident_set.reserve(256);
                for (const auto& [mid, mo] : models_gpu_) {
                    QFileInfo fi(QString::fromStdString(mo.streaming_file_path));
                    const QString base = fi.completeBaseName();
                    for (const auto& c : mo.chunks) {
                        Probe p;
                        p.name = base;
                        p.priority = chunk_priority_px2(c);
                        p.ex = c.aabb_max[0] - c.aabb_min[0];
                        p.ey = c.aabb_max[1] - c.aabb_min[1];
                        p.ez = c.aabb_max[2] - c.aabb_min[2];
                        p.history = c.visibility_history;
                        if (c.is_resident) {
                            resident_set.push_back(p);
                        } else if (c.frustum_visible_count > 0) {
                            missing_set.push_back(p);
                        }
                    }
                }
                // Top 20 missing by priority. 20 (not 5) because the
                // chunks the user actually cares about — e.g. brace
                // model chunks — may be ranked below the absolute top
                // but well above the bottom residents. We need to see
                // them to evaluate whether the metric is right.
                std::partial_sort(missing_set.begin(),
                                  missing_set.begin() + std::min<size_t>(20, missing_set.size()),
                                  missing_set.end(),
                                  [](const Probe& a, const Probe& b) {
                                      return a.priority > b.priority;
                                  });
                // Bottom 5 residents by EFFECTIVE priority (× history) —
                // these are the chunks a candidate would need to beat
                // to swap in.
                std::partial_sort(resident_set.begin(),
                                  resident_set.begin() + std::min<size_t>(5, resident_set.size()),
                                  resident_set.end(),
                                  [](const Probe& a, const Probe& b) {
                                      const float ha = std::max(a.history, 0.05f);
                                      const float hb = std::max(b.history, 0.05f);
                                      return a.priority * ha < b.priority * hb;
                                  });
                Log::info().noquote() << "  [missing per model — top 8 by missing-count]";
                struct Row {
                    QString name;
                    size_t  resident = 0;
                    size_t  frustum  = 0;
                    size_t  missing  = 0;
                };
                std::vector<Row> rows;
                rows.reserve(models_gpu_.size());
                for (const auto& [mid, mo] : models_gpu_) {
                    Row r;
                    QFileInfo fi(QString::fromStdString(mo.streaming_file_path));
                    r.name = fi.completeBaseName();
                    for (const auto& c : mo.chunks) {
                        if (c.is_resident) ++r.resident;
                        if (c.frustum_visible_count > 0) {
                            ++r.frustum;
                            if (!c.is_resident) ++r.missing;
                        }
                    }
                    if (r.missing > 0) rows.push_back(std::move(r));
                }
                std::sort(rows.begin(), rows.end(),
                          [](const Row& a, const Row& b) {
                              return a.missing > b.missing;
                          });
                const size_t cap = std::min<size_t>(rows.size(), 8);
                for (size_t i = 0; i < cap; ++i) {
                    const Row& r = rows[i];
                    Log::info().noquote().nospace()
                        << "    " << r.name
                        << "  resident=" << r.resident
                        << "  frustum=" << r.frustum
                        << "  missing=" << r.missing;
                }
                Log::info().noquote() << "  [top 20 MISSING chunks by priority (px², want these loaded)]";
                for (size_t i = 0; i < std::min<size_t>(20, missing_set.size()); ++i) {
                    const Probe& p = missing_set[i];
                    Log::info().noquote().nospace()
                        << "    pri=" << QString::number(p.priority, 'f', 0)
                        << "  aabb=" << QString::number(p.ex, 'f', 1) << "x"
                        << QString::number(p.ey, 'f', 1) << "x"
                        << QString::number(p.ez, 'f', 1) << "m"
                        << "  in " << p.name;
                }
                Log::info().noquote() << "  [bottom 5 RESIDENT chunks by effective priority (must beat with 2× hysteresis)]";
                for (size_t i = 0; i < std::min<size_t>(5, resident_set.size()); ++i) {
                    const Probe& p = resident_set[i];
                    const float eff = p.priority * std::max(p.history, 0.05f);
                    Log::info().noquote().nospace()
                        << "    pri=" << QString::number(p.priority, 'f', 0)
                        << " hist=" << QString::number(p.history, 'f', 2)
                        << " eff=" << QString::number(eff, 'f', 0)
                        << "  aabb=" << QString::number(p.ex, 'f', 1) << "x"
                        << QString::number(p.ey, 'f', 1) << "x"
                        << QString::number(p.ez, 'f', 1) << "m"
                        << "  in " << p.name;
                }
            }
        }
    }

    // ---- Benchmark integration + auto-quit -------------------------------
    if (bench_total_ > 0) {
        // Cold-load gate: don't start the orbit sweep until streaming has
        // converged for a few consecutive frames. Converged = 0 loads.
        // bench_warm_done_ latches on first satisfaction so the gate is
        // evaluated only during warmup, not every frame after.
        if (!bench_warm_done_) {
            constexpr int CONVERGE_FRAMES_REQUIRED = 5;
            constexpr int MAX_WARM_FRAMES          = 600;
            // With async I/O, "no main-thread work this frame" isn't
            // enough — a worker thread might still be reading. The
            // streaming is truly settled only when the worker queue is
            // empty AND no chunks are awaiting drain.
            const bool worker_idle =
                streaming_thread_.inFlightApprox() == 0;
            if (streaming_loads_this_frame_ > 0 || !worker_idle) {
                bench_warm_streak_ = 0;
            } else {
                ++bench_warm_streak_;
            }
            ++bench_warm_frames_total_;
            const bool converged = bench_warm_streak_ >= CONVERGE_FRAMES_REQUIRED;
            const bool timed_out = bench_warm_frames_total_ >= MAX_WARM_FRAMES;
            if (converged) {
                Log::info().noquote().nospace()
                    << "[bench warm] converged after "
                    << bench_warm_frames_total_ << " frames";
                bench_warm_done_ = true;
            } else if (timed_out) {
                // Walk every chunk in every model to summarise the steady-
                // state shape: how many frustum-visible chunks are missing,
                // how many residents have load_count > 1 (cycled), the
                // chunk that's been re-loaded the most times, total pool
                // usage. This is the smoking gun for working-set > pool:
                // high "missing" with high "cycled" means we're stuck in
                // an evict-reload loop. Low "missing" with low "cycled"
                // means convergence just needs more frames.
                size_t total_chunks = 0;
                size_t resident = 0;
                size_t missing_visible = 0;
                size_t cycled = 0;
                uint32_t max_load = 0;
                for (const auto& [mid, m] : models_gpu_) {
                    for (const auto& c : m.chunks) {
                        ++total_chunks;
                        if (c.is_resident) ++resident;
                        else if (c.frustum_visible_count > 0) ++missing_visible;
                        if (c.load_count > 1) ++cycled;
                        if (c.load_count > max_load) max_load = c.load_count;
                    }
                }
                const double mb = 1.0 / (1024.0 * 1024.0);
                // Estimate the typical "would fit" pressure: avg byte size
                // of the missing-visible chunks. If that's much larger than
                // largest_free_run, fragmentation is the smoking gun even
                // when total_free would be enough.
                uint64_t missing_bytes_total = 0;
                uint32_t missing_count_for_avg = 0;
                for (const auto& [mid, m] : models_gpu_) {
                    for (const auto& c : m.chunks) {
                        if (!c.is_resident && c.frustum_visible_count > 0) {
                            missing_bytes_total += c.vertex_byte_size
                                                 + c.index_count * sizeof(uint32_t);
                            ++missing_count_for_avg;
                        }
                    }
                }
                const uint64_t avg_missing_bytes = missing_count_for_avg > 0
                    ? missing_bytes_total / missing_count_for_avg : 0;
                const uint64_t largest_free = pool_.largest_free_run_bytes();
                const bool fragmented = missing_visible > 0
                                      && avg_missing_bytes > largest_free
                                      && pool_.total_free_bytes() > avg_missing_bytes;

                const char* diag;
                if (fragmented) {
                    diag = "POOL FRAGMENTED (total free OK but no contiguous run big enough)";
                } else if (missing_visible > 0 && cycled > 10) {
                    diag = "WORKING SET > POOL (thrashing — many chunks cycling)";
                } else if (missing_visible > 0 && max_load > 5) {
                    diag = "FEW-CHUNK CYCLE (one+ chunks keep reloading, likely hysteresis-boundary)";
                } else if (missing_visible > 0) {
                    diag = "still loading (try MAX_WARM_FRAMES↑)";
                } else {
                    diag = "converged, just below the gate's 5-frame streak";
                }
                Log::warn().noquote().nospace()
                    << "[bench warm] timed out after " << bench_warm_frames_total_
                    << " frames without convergence (last loads="
                    << streaming_loads_this_frame_ << ")\n"
                    << "  chunks: " << resident << " resident, "
                    << missing_visible << " visible-but-missing, "
                    << total_chunks << " total\n"
                    << "  cycled (loaded >1×): " << cycled
                    << ", max load_count: " << max_load << "\n"
                    << "  pool: "
                    << QString::number(double(pool_.total_used_bytes()) * mb, 'f', 0)
                    << " / "
                    << QString::number(double(pool_.total_capacity_bytes()) * mb, 'f', 0)
                    << " MB used, "
                    << QString::number(double(largest_free) * mb, 'f', 0)
                    << " MB largest free run, "
                    << QString::number(double(pool_.total_free_bytes()) * mb, 'f', 0)
                    << " MB total free\n"
                    << "  avg missing chunk: "
                    << QString::number(double(avg_missing_bytes) * mb, 'f', 1) << " MB\n"
                    << "  diagnosis: " << diag
                    << "; starting bench anyway";
                bench_warm_done_ = true;
            } else {
                requestUpdate();
                return;
            }
        }

        const float ms = float(frame_timer.nsecsElapsed()) / 1e6f;

        // Warm-up frames are dropped from the sample. The yaw advance starts
        // immediately so the warmup frames already exercise different views.
        if (bench_count_ >= bench_warmup_) {
            bench_frame_ms_.push_back(ms);
        }

        // Per-frame line (every 50 frames so the log stays readable). Format
        // approximates GL's per-frame stats so a side-by-side script can
        // diff them. cull is the wall-clock cull cost from the timer above.
        if ((bench_count_ % 50) == 0) {
            uint64_t total_vbo = 0, total_ebo = 0, total_ssbo = 0;
            uint32_t total_instances = 0, total_meshes = 0;
            for (const auto& [mid, mo] : models_gpu_) {
                total_vbo += mo.vram_bytes_vbo;
                total_ebo += mo.vram_bytes_ebo;
                total_ssbo += mo.vram_bytes_ssbo;
                total_instances += mo.instance_count;
                total_meshes    += mo.mesh_count;
            }
            const double mb = 1.0 / (1024.0 * 1024.0);
            const double avg_n  = double(std::max(1, bench_count_ - bench_warmup_ + 1));
            const double cull_ms   = bench_cull_ms_total_   / avg_n;
            const double stream_ms = bench_stream_ms_total_ / avg_n;
            Log::info().noquote().nospace()
                << "[frame] " << QString::number(ms > 0 ? 1000.0f / ms : 0.0f, 'f', 1) << " fps"
                << "  " << QString::number(ms, 'f', 2) << " ms"
                << "  obj " << last_visible_objects_ << "/" << total_instances
                << "  tri " << last_visible_triangles_
                << "  meshes " << total_meshes
                << "  sub_draws " << last_sub_draws_
                << "  hiz_rej " << hiz_reject_count_
                << "  cull[wall " << QString::number(cull_ms, 'f', 2)
                << " | compute " << QString::number(last_cull_compute_ms_, 'f', 2)
                << " upload " << QString::number(last_cull_upload_ms_, 'f', 2) << "]ms"
                << "  stream[" << QString::number(stream_ms, 'f', 2) << "]ms"
                << "  vram " << QString::number(double(total_vbo + total_ebo + total_ssbo) * mb, 'f', 1) << "MB"
                << " (vbo " << QString::number(double(total_vbo) * mb, 'f', 1)
                << " + ebo " << QString::number(double(total_ebo) * mb, 'f', 1)
                << " + ssbo " << QString::number(double(total_ssbo) * mb, 'f', 1) << ")"
                << "  models " << models_gpu_.size()
                << "  lod1 " << lod1_dbg_count_ << "/" << (lod1_dbg_count_ + lod0_dbg_eligible_count_)
                << " (saved " << lod1_dbg_tris_saved_ << " tris, "
                << lod0_dbg_no_lod1_count_ << " no-lod1)";
            lod1_dbg_count_ = 0;
            lod0_dbg_eligible_count_ = 0;
            lod0_dbg_no_lod1_count_ = 0;
            lod1_dbg_tris_saved_ = 0;
        }
        camera_yaw_deg_ = bench_yaw_start_
                        + bench_yaw_speed_ * float(bench_count_ + 1);
        ++bench_count_;

        if (bench_count_ >= bench_warmup_ + bench_total_) {
            // Final frame — assemble stats and emit. Format mirrors the GL
            // minimal so output is line-diffable across backends.
            std::vector<float> times = bench_frame_ms_;
            std::sort(times.begin(), times.end());
            auto pct = [&times](double p) -> float {
                if (times.empty()) return 0.0f;
                const size_t idx = std::min(times.size() - 1,
                    size_t(p * double(times.size() - 1)));
                return times[idx];
            };
            float sum = 0.0f;
            for (float f : times) sum += f;
            const float avg    = times.empty() ? 0.0f : sum / float(times.size());
            const float median = pct(0.5);
            const float p1     = pct(0.01);
            const float p99    = pct(0.99);

            const float total_sweep = bench_yaw_speed_ * float(bench_total_);
            Log::info().noquote().nospace()
                << "\n=== BENCHMARK (" << bench_total_ << " frames, orbit "
                << total_sweep << "° at " << bench_yaw_speed_ << "°/frame) ===";
            Log::info().noquote().nospace()
                << "  avg: "    << avg    << " ms (" << (avg    > 0 ? 1000.0f/avg    : 0.0f) << " fps)";
            Log::info().noquote().nospace()
                << "  median: " << median << " ms (" << (median > 0 ? 1000.0f/median : 0.0f) << " fps)";
            Log::info().noquote().nospace()
                << "  p1: "  << p1  << " ms  p99: " << p99 << " ms";
            Log::info().noquote().nospace()
                << "  last frame: obj " << last_visible_objects_
                << "  tri " << last_visible_triangles_
                << "  sub_draws " << last_sub_draws_
                << "  hiz_rej " << hiz_reject_count_;
            const double n = double(std::max(1, bench_total_));
            Log::info().noquote().nospace()
                << "  per-frame avg ms: cull=" << bench_cull_ms_total_ / n
                << "  stream=" << bench_stream_ms_total_ / n
                << "  hiz_readback=" << bench_hiz_readback_ms_total_ / n
                << "  hiz=" << (hiz_enabled_ ? "on" : "off");
            Log::info().noquote() << "=== END BENCHMARK ===\n";

            bench_total_ = 0;
            QCoreApplication::quit();
        } else {
            requestUpdate();
        }
    }
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

void ViewportWindow::buildModelBindGroup(ModelGpuData& m) {
    if (!m.mesh_storage || !m.instance_storage) {
        // Empty model — no chunks, no bind groups; the draw loop will skip.
        return;
    }
    for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
        core_.buildChunkBindGroup(m, ci);
    }
}

// buildChunkBindGroup moved to ViewportCore (#84-n).

// makeChunkRequest moved to ViewportCore (folded into loadChunkBytesAndUploadGpu) (#84-n).

// applyStreamedChunk moved to ViewportCore (#84-n).

// loadChunkBytesAndUploadGpu moved to ViewportCore (#84-n).

// unloadChunk moved to ViewportCore (#84-n).

void ViewportWindow::driveStreamingLoads() { core_.driveStreamingLoads(); }

// -----------------------------------------------------------------------------
// Depth attachment
// -----------------------------------------------------------------------------

void ViewportWindow::ensureDepthTexture(int w, int h) {
    if (w == depth_w_ && h == depth_h_ && depth_view_) return;
    releaseDepthTexture();

    WGPUTextureDescriptor desc = {};
    // TextureBinding is needed so the HiZ resolve pass can sample this as
    // a texture_depth_multisampled_2d in its fragment shader.
    desc.usage         = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_TextureBinding;
    desc.dimension     = WGPUTextureDimension_2D;
    desc.size.width    = uint32_t(w);
    desc.size.height   = uint32_t(h);
    desc.size.depthOrArrayLayers = 1;
    desc.format        = WGPUTextureFormat_Depth32Float;
    desc.mipLevelCount = 1;
    desc.sampleCount   = SAMPLE_COUNT;  // matches MSAA color target
    desc.label         = svFromCStr("ifcviewer-wgpu.depth");
    depth_texture_ = wgpuDeviceCreateTexture(device_, &desc);

    WGPUTextureViewDescriptor vdesc = {};
    vdesc.format          = WGPUTextureFormat_Depth32Float;
    vdesc.dimension       = WGPUTextureViewDimension_2D;
    vdesc.mipLevelCount   = 1;
    vdesc.arrayLayerCount = 1;
    vdesc.aspect          = WGPUTextureAspect_DepthOnly;
    depth_view_ = wgpuTextureCreateView(depth_texture_, &vdesc);

    depth_w_ = w;
    depth_h_ = h;
}

void ViewportWindow::releaseDepthTexture() {
    if (depth_view_)    { wgpuTextureViewRelease(depth_view_); depth_view_ = nullptr; }
    if (depth_texture_) { wgpuTextureRelease(depth_texture_);  depth_texture_ = nullptr; }
    depth_w_ = depth_h_ = 0;
}

void ViewportWindow::ensureMsaaColorTexture(int w, int h) {
    if (w == msaa_w_ && h == msaa_h_ && msaa_color_view_) return;
    releaseMsaaColorTexture();

    WGPUTextureDescriptor desc = {};
    desc.usage         = WGPUTextureUsage_RenderAttachment;
    desc.dimension     = WGPUTextureDimension_2D;
    desc.size.width    = uint32_t(w);
    desc.size.height   = uint32_t(h);
    desc.size.depthOrArrayLayers = 1;
    desc.format        = surface_format_;
    desc.mipLevelCount = 1;
    desc.sampleCount   = SAMPLE_COUNT;
    desc.label         = svFromCStr("ifcviewer-wgpu.msaa_color");
    msaa_color_texture_ = wgpuDeviceCreateTexture(device_, &desc);

    msaa_color_view_ = wgpuTextureCreateView(msaa_color_texture_, nullptr);
    msaa_w_ = w;
    msaa_h_ = h;
}

void ViewportWindow::releaseMsaaColorTexture() {
    if (msaa_color_view_)    { wgpuTextureViewRelease(msaa_color_view_); msaa_color_view_ = nullptr; }
    if (msaa_color_texture_) { wgpuTextureRelease(msaa_color_texture_);  msaa_color_texture_ = nullptr; }
    msaa_w_ = msaa_h_ = 0;
}

// -----------------------------------------------------------------------------
// Camera + frame uniforms
// -----------------------------------------------------------------------------
//
// Orbit camera around `camera_target_`. World +Z up (BIM convention). Yaw is
// rotation about Z (positive = anticlockwise looking down +Z); pitch is
// elevation above the XY plane.

static Eigen::Vector3f orbitEye(const float target[3], float dist,
                          float yaw_deg, float pitch_deg) {
    // Matches the GL ViewportWindow::updateCamera convention exactly so the
    // orbit pivot, framing, and benchmark camera path align between backends.
    //   eye.x = target.x + dist * cos(pitch) * cos(yaw)
    //   eye.y = target.y + dist * cos(pitch) * sin(yaw)
    //   eye.z = target.z + dist * sin(pitch)
    const float yaw = qDegreesToRadians(yaw_deg);
    const float pit = qDegreesToRadians(pitch_deg);
    const float cp = std::cos(pit), sp = std::sin(pit);
    const float cy = std::cos(yaw), sy = std::sin(yaw);
    return Eigen::Vector3f(target[0] + dist * cp * cy,
                     target[1] + dist * cp * sy,
                     target[2] + dist * sp);
}

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
    if (selection_.count() == 0) {
        Log::info() << "[wgpu] focus: no object selected";
        return;
    }
    float lo[3] = {  std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity() };
    float hi[3] = { -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity() };
    bool any = false;
    for (uint32_t id : selection_.selectionIds()) {
        float mn[3], mx[3];
        if (!computeObjectAabb(id, mn, mx)) continue;
        for (int i = 0; i < 3; ++i) {
            lo[i] = std::min(lo[i], mn[i]);
            hi[i] = std::max(hi[i], mx[i]);
        }
        any = true;
    }
    if (!any) {
        Log::info() << "[wgpu] focus: no AABB available";
        return;
    }
    frameAabb(lo, hi, 1.30f);
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

    // Forward = orbit eye -> target, kept as the camera's view direction in
    // fly mode too so a Shift+F right after orbiting doesn't snap to a new
    // heading. WASD moves in the screen plane; QE rises/falls along world +Z.
    const Eigen::Vector3f target(camera_target_[0], camera_target_[1], camera_target_[2]);
    const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                   camera_yaw_deg_, camera_pitch_deg_);
    Eigen::Vector3f forward = (target - eye); forward.normalize();
    // When looking straight up/down, cross(forward, worldZ) degenerates;
    // fall back to worldY so right doesn't go NaN and WASD still works.
    const Eigen::Vector3f world_up(0.0f, 0.0f, 1.0f);
    const Eigen::Vector3f right_basis = (std::abs(camera_pitch_deg_) >= 89.0f)
                                ? Eigen::Vector3f(0.0f, 1.0f, 0.0f)
                                : world_up;
    Eigen::Vector3f right = forward.cross(right_basis);
    right.normalize();

    Eigen::Vector3f move(0, 0, 0);
    if (fps_keys_held_.count(Qt::Key_W)) move += forward;
    if (fps_keys_held_.count(Qt::Key_S)) move -= forward;
    if (fps_keys_held_.count(Qt::Key_D)) move += right;
    if (fps_keys_held_.count(Qt::Key_A)) move -= right;
    if (fps_keys_held_.count(Qt::Key_E)) move += world_up;
    if (fps_keys_held_.count(Qt::Key_Q)) move -= world_up;
    if (move.isZero()) return;
    move.normalize();

    // Absolute m/s, scrollwheel-adjustable (Blender / GL convention).
    // Scaling with camera_distance_ produced "stuttery" speed on big scenes
    // because distance varies frame-to-frame (and worse, wheel zoom kept
    // changing it underneath fly mode).
    const float speed = fps_move_speed_
                      * (fps_keys_held_.count(Qt::Key_Shift) ? 5.0f : 1.0f);
    const Eigen::Vector3f delta = move * (speed * dt);

    camera_target_[0] += delta.x();
    camera_target_[1] += delta.y();
    camera_target_[2] += delta.z();
    requestUpdate();

    if (fly_debug_) {
        // dt timeline: see if values jitter (under/over-integration symptoms).
        // Show in ms with 2dp so small jumps are visible.
        const qint64 since_render_ns = fly_render_clock_.isValid()
                                     ? fly_render_clock_.nsecsElapsed() : 0;
        fly_render_clock_.restart();
        Log::info().noquote().nospace()
            << "[fly] dt=" << QString::number(dt * 1000.0f, 'f', 2) << "ms"
            << " render_gap=" << QString::number(double(since_render_ns) / 1e6, 'f', 2) << "ms"
            << " keys=" << fps_keys_held_.size()
            << " speed=" << QString::number(speed, 'f', 2) << "m/s"
            << " delta=" << QString::number(delta.norm(), 'f', 4) << "m";
    }
}

// chunkScreenAreaPx moved to ViewportCore (#84-h).

void ViewportWindow::applyNavPreset(const char* name) {
    // Matches GL AppSettings::NavPreset semantics exactly.
    //   blender — Orbit MMB,        Pan Shift+MMB   (default)
    //   rhino   — Orbit RMB,        Pan Shift+RMB
    //   revit   — Orbit Shift+MMB,  Pan MMB
    if (name && std::strcmp(name, "rhino") == 0) {
        orbit_button_ = Qt::RightButton;  orbit_mods_ = Qt::NoModifier;
        pan_button_   = Qt::RightButton;  pan_mods_   = Qt::ShiftModifier;
    } else if (name && std::strcmp(name, "revit") == 0) {
        orbit_button_ = Qt::MiddleButton; orbit_mods_ = Qt::ShiftModifier;
        pan_button_   = Qt::MiddleButton; pan_mods_   = Qt::NoModifier;
    } else {
        orbit_button_ = Qt::MiddleButton; orbit_mods_ = Qt::NoModifier;
        pan_button_   = Qt::MiddleButton; pan_mods_   = Qt::ShiftModifier;
    }
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

void ViewportWindow::captureNextFrameToPng(const std::string& path, bool quit_after) {
    pending_screenshot_path_ = path;
    pending_screenshot_quit_ = quit_after;
    if (isExposed()) requestUpdate();
}

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
        const int hit = hitTestSectionGizmo(lp.x(), lp.y());
        if (hit >= 0) {
            section_drag_active_       = true;
            section_drag_index_        = hit;
            section_drag_start_mouse_  = lp;
            section_drag_start_origin_ = section_planes_[hit].origin;
            nav_drag_kind_             = NavDrag::Inactive;
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
        setPivotIndicatorVisible(true);  // hidden again on release
    } else if (event->button() == pan_button_
            && (mods & Qt::KeyboardModifierMask) == pan_mods_) {
        nav_drag_kind_ = NavDrag::Pan;
        setPivotIndicatorVisible(true);
    } else if (event->button() == Qt::LeftButton
            && !section_tool_active_
            && tool_mode_ != ToolMode::Area
            && tool_mode_ != ToolMode::Length
            && nav_drag_kind_ == NavDrag::Inactive) {
        // Arm marquee box-select. Plain / Shift / Ctrl LMB without a tool
        // intercepting the click; if the cursor never moves past the
        // threshold this stays armed-only and the release falls through
        // to single-pick.
        box_select_armed_      = true;
        box_select_active_     = false;
        box_select_start_pos_  = nav_press_pos_;
        box_select_current_pos_ = nav_press_pos_;
        box_select_press_mods_ = mods;
    }
}

void ViewportWindow::mouseReleaseEvent(QMouseEvent* event) {
    if (section_drag_active_ && event->button() == Qt::LeftButton) {
        section_drag_active_ = false;
        section_drag_index_  = -1;
        nav_active_button_   = Qt::NoButton;
        return;
    }
    // Marquee finalisation: only commit when the drag actually became
    // active (cursor moved past threshold). Press-time mods decide the
    // set op so a mid-drag Shift release doesn't flip the behaviour.
    if (box_select_armed_ && event->button() == Qt::LeftButton) {
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
        if (event->button() == Qt::LeftButton && !nav_dragged_) {
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
                setPivotIndicatorVisible(false);
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
                setPivotIndicatorVisible(false);
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
                setPivotIndicatorVisible(false);
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
                for (auto& [mid, m] : models_gpu_) {
                    for (const auto& inst : m.instances) {
                        if (inst.object_id != id) continue;
                        if (inst.mesh_id >= m.mesh_chunk_idx.size()) continue;
                        const size_t ci = m.mesh_chunk_idx[inst.mesh_id];
                        if (!seen.insert({mid, ci}).second) continue;
                        const auto& c = m.chunks[ci];
                        Log::info().noquote().nospace()
                            << "  model " << mid << " chunk " << ci
                            << "  inst_aabb "
                            << QString::number(inst.world_aabb_max[0] - inst.world_aabb_min[0], 'f', 1)
                            << "×"
                            << QString::number(inst.world_aabb_max[1] - inst.world_aabb_min[1], 'f', 1)
                            << "×"
                            << QString::number(inst.world_aabb_max[2] - inst.world_aabb_min[2], 'f', 1) << "m"
                            << "  chunk_aabb "
                            << QString::number(c.aabb_max[0] - c.aabb_min[0], 'f', 1) << "×"
                            << QString::number(c.aabb_max[1] - c.aabb_min[1], 'f', 1) << "×"
                            << QString::number(c.aabb_max[2] - c.aabb_min[2], 'f', 1) << "m"
                            << "  resident=" << (c.is_resident ? "Y" : "N");
                        // First hit becomes the "primary" slot the
                        // eviction watcher uses. Good enough until we wire
                        // a multi-chunk watcher.
                        if (tracked_chunk_idx_ == SIZE_MAX) {
                            tracked_chunk_mid_    = mid;
                            tracked_chunk_idx_    = ci;
                            tracked_was_resident_ = c.is_resident;
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
        setPivotIndicatorVisible(false);
    }
}

void ViewportWindow::mouseMoveEvent(QMouseEvent* event) {
    // Section drag intercepts the move handler entirely: the orbit/pan
    // classification already declined this drag in mousePressEvent, so all
    // we have to do is slide the plane along its normal.
    if (section_drag_active_) {
        const Eigen::Vector2i pos = toV2i(event->position().toPoint());
        updateSectionDrag(pos.x(), pos.y());
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

        // Save eye BEFORE rotating so we can pin it after.
        const Eigen::Vector3f pinned_eye = orbitEye(camera_target_, camera_distance_,
                                              camera_yaw_deg_, camera_pitch_deg_);

        // Convention: mouse-up looks up, mouse-down looks down (non-inverted).
        // orbitEye stores pitch with sin(pitch) controlling eye.z relative to
        // target → larger pitch = eye higher = looking down. To make mouse-up
        // (dy<0) look up (i.e. raise pitch in our stored convention so the
        // camera tilts down toward the target… wait, with eye pinned in FPS
        // mode the relationship inverts: increasing pitch pulls *target* up,
        // which means forward tilts down). Net: dy>0 (down) increases pitch
        // → forward tilts down → looking down. `+=` is correct here even
        // though orbit-mode also uses `+=` for the opposite visual reason.
        camera_yaw_deg_   -= float(dx) * 0.2f;
        camera_pitch_deg_ += float(dy) * 0.2f;
        camera_pitch_deg_ = std::clamp(camera_pitch_deg_, -89.9f, 89.9f);

        // Re-derive target so orbitEye(target, dist, new_yaw, new_pitch) ==
        // pinned_eye. eye = target + dist*(cp*cy, cp*sy, sp) → invert.
        const float yaw = qDegreesToRadians(camera_yaw_deg_);
        const float pit = qDegreesToRadians(camera_pitch_deg_);
        const float cp = std::cos(pit), sp = std::sin(pit);
        const float cy = std::cos(yaw), sy = std::sin(yaw);
        camera_target_[0] = pinned_eye.x() - camera_distance_ * cp * cy;
        camera_target_[1] = pinned_eye.y() - camera_distance_ * cp * sy;
        camera_target_[2] = pinned_eye.z() - camera_distance_ * sp;

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
        // Drag-right rotates the world right (yaw -= dx), drag-down tilts
        // the camera up so we see more of the object's top (pitch += dy).
        // 0.4 deg/px matches GL ViewportWindow.
        camera_yaw_deg_   -= float(dx) * 0.4f;
        camera_pitch_deg_ += float(dy) * 0.4f;
        camera_pitch_deg_ = std::clamp(camera_pitch_deg_, -89.9f, 89.9f);
        requestUpdate();
    } else if (nav_drag_kind_ == NavDrag::Pan) {
        // Pan in the camera's screen-space plane. World units per pixel
        // tracks the view-frustum width at the pivot's depth so panning
        // feels constant regardless of zoom. Within 1° of straight up/down
        // the world-Z up-reference degenerates (cross with forward is the
        // zero vector → NaN), so switch to world-Y up — matches the
        // up-vector switch in buildViewProj so top/bottom views still pan.
        const Eigen::Vector3f target(camera_target_[0], camera_target_[1], camera_target_[2]);
        const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                       camera_yaw_deg_, camera_pitch_deg_);
        const Eigen::Vector3f fwd   = (target - eye).normalized();
        const Eigen::Vector3f world_up = (std::abs(camera_pitch_deg_) >= 89.0f)
                                 ? Eigen::Vector3f(0.0f, 1.0f, 0.0f)
                                 : Eigen::Vector3f(0.0f, 0.0f, 1.0f);
        const Eigen::Vector3f right = fwd.cross(world_up).normalized();
        const Eigen::Vector3f up    = right.cross(fwd).normalized();

        const float half_h_world = camera_distance_
            * std::tan(qDegreesToRadians(camera_fov_y_deg_) * 0.5f);
        const float pan_per_pixel = (height() > 0)
            ? (2.0f * half_h_world / float(height()))
            : 0.0f;

        const Eigen::Vector3f shift = -right * (float(dx) * pan_per_pixel)
                              +  up    * (float(dy) * pan_per_pixel);
        camera_target_[0] += shift.x();
        camera_target_[1] += shift.y();
        camera_target_[2] += shift.z();
        requestUpdate();
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
    if (key == Qt::Key_H && mods == Qt::AltModifier) {
        if (visibility_.hiddenCount() == 0) return;
        visibility_.clear();
        Log::info() << "[wgpu] show all";
        requestUpdate();
        return;
    }
    // Alt+X — toggle global X-ray (translucent everything). The frame
    // uniform `xray_alpha_cap` clamps `fs_main`'s output alpha; the cull
    // classifier sees `xray_alpha_cap_ < 1` and routes every instance
    // through the transparent pass so the blend actually fires.
    if (key == Qt::Key_X && mods == Qt::AltModifier && !event->isAutoRepeat()) {
        constexpr float kXrayOnCap = 0.3f;
        xray_alpha_cap_ = (xray_alpha_cap_ < 1.0f) ? 1.0f : kXrayOnCap;
        Log::info().noquote().nospace()
            << "[wgpu] x-ray "
            << (xray_alpha_cap_ < 1.0f ? "ON"  : "OFF")
            << " (cap=" << xray_alpha_cap_ << ")";
        requestUpdate();
        return;
    }
    if (key == Qt::Key_H && mods == Qt::ShiftModifier) {
        if (selection_.count() == 0) return;
        size_t hidden_now = 0;
        for (auto& [mid, m] : models_gpu_) {
            for (const auto& inst : m.instances) {
                if (selection_.contains(inst.object_id)) continue;
                if (!visibility_.isHidden(inst.object_id)) {
                    visibility_.hide(inst.object_id);
                    ++hidden_now;
                }
            }
        }
        Log::info().noquote().nospace() << "[wgpu] isolated " << selection_.count()
                                    << " (hid " << hidden_now << " others)";
        requestUpdate();
        return;
    }
    if (key == Qt::Key_H && mods == Qt::NoModifier) {
        if (selection_.count() == 0) return;
        for (uint32_t id : selection_.selectionIds()) visibility_.hide(id);
        const size_t n = selection_.count();
        selection_.clear();   // hiding deselects, matching GL behaviour
        Log::info().noquote().nospace() << "[wgpu] hid " << n << " selected";
        requestUpdate();
        return;
    }
    if (key == Qt::Key_F && mods == Qt::ShiftModifier && !event->isAutoRepeat()) {
        enterFpsMode();
        return;
    }

    // Section tool. K toggles the tool; Shift+K clears all planes. When
    // the tool is active, click adds a plane at the surface (handled in
    // mouseReleaseEvent), Esc deactivates, Del/Backspace removes the
    // most recently added plane. Mirrors GL ViewportWindow + Bonsai's
    // bind_shortcut(K / Shift+K) bindings.
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
            removeSectionPlane(int(section_planes_.size()) - 1);
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
        switch (key) {
        case Qt::Key_X: setStandardView(neg ? 180.0f : 0.0f,   0.0f); break;
        case Qt::Key_Y: setStandardView(neg ? 270.0f : 90.0f,  0.0f); break;
        case Qt::Key_Z: setStandardView(camera_yaw_deg_, neg ? -90.0f : 90.0f); break;
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
        const float factor = std::pow(1.25f, notches);
        fps_move_speed_ = std::clamp(fps_move_speed_ * factor, 0.05f, 1000.0f);
        Log::info().noquote().nospace()
            << "[wgpu] fly speed: " << QString::number(fps_move_speed_, 'f', 2) << " m/s";
        return;
    }
    // Orbit mode: each notch zooms ~10% in/out; sign matches "wheel up = in".
    const float factor = std::pow(0.9f, notches);
    camera_distance_   = std::max(0.01f, camera_distance_ * factor);
    // Pivot afterglow on wheel — visible for 600 ms so the user can see
    // what they're zooming around without holding a drag.
    setPivotIndicatorVisible(true, 600);
    requestUpdate();
}

void ViewportWindow::shutdown() {
    // VW-only resources first — these depend on core_'s device_ being
    // alive, so they must be released before core_.shutdown() releases it.
    releaseDepthTexture();
    releaseMsaaColorTexture();
    releaseHizResources();
    releaseEdgeResources();
    overlays_.destroy();
    releasePickResources();

    // Core owns the rest: streaming thread, models, pool, frame/selection
    // buffers, pipelines/shaders/layouts, queue/device/adapter/surface/
    // instance.
    core_.shutdown();
}
