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

#include "WgpuViewportWindow.h"

#include <QGuiApplication>
#include <QResizeEvent>
#include <QDebug>
#include <QDir>
#include <QElapsedTimer>
#include <QFile>
#include <QFileInfo>
#include <QMatrix4x4>
#include <QVector3D>
#include <QtMath>

#include <webgpu/wgpu.h>  // wgpu-native extensions (logging, MULTI_DRAW_INDIRECT, …)

#include <algorithm>
#include <cmath>
#include <cstring>
#include <limits>
#include <utility>

// -----------------------------------------------------------------------------
// Frame uniforms (CPU mirror of group=0 binding=0 in the WGSL).
// std140-ish layout: every member naturally 16-aligned, struct stride = 96.
// -----------------------------------------------------------------------------

struct FrameUniforms {
    float view_proj[16];
    float light_dir[4];     // xyz = unit dir toward light, w unused
    float fill_dir[4];      // xyz = secondary fill dir
    float sky_color[4];     // xyz = sky-tint ambient, w unused
    float ground_color[4];  // xyz = ground-tint ambient, w unused
};
static_assert(sizeof(FrameUniforms) == 16 * sizeof(float) + 4 * 4 * sizeof(float),
              "FrameUniforms must match WGSL layout (mat4 + 4xvec4)");

// WebGPU texture<->buffer copies require bytes-per-row to be a multiple of
// this. RGBA8 (4 B/pixel) at 1280 wide produces 5120 — already a multiple,
// but at e.g. 1281 wide we round up to 5376. Tracked as the padded row
// stride in the capture path.
static constexpr uint64_t WGPU_BYTES_PER_ROW_ALIGN = 256;

// Forward declaration — defined below alongside updateFrameUniforms. Used
// by render() to extract camera/frustum state without duplicating the math.
static QVector3D orbitEye(const float target[3], float dist,
                          float yaw_deg, float pitch_deg);

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

static void onWgpuLog(WGPULogLevel level, WGPUStringView message, void* /*userdata*/) {
    const QString m = sv(message);
    switch (level) {
        case WGPULogLevel_Error: qWarning().noquote() << "[wgpu err]"   << m; break;
        case WGPULogLevel_Warn:  qWarning().noquote() << "[wgpu warn]"  << m; break;
        case WGPULogLevel_Info:  qInfo   ().noquote() << "[wgpu info]"  << m; break;
        case WGPULogLevel_Debug: qDebug  ().noquote() << "[wgpu dbg]"   << m; break;
        case WGPULogLevel_Trace: qDebug  ().noquote() << "[wgpu trace]" << m; break;
        default: break;
    }
}

static void onUncapturedError(WGPUDevice const* /*device*/,
                              WGPUErrorType type, WGPUStringView message,
                              void* /*ud1*/, void* /*ud2*/) {
    qWarning().noquote() << "[wgpu device error" << int(type) << "]" << sv(message);
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

void releaseWgpuModelGpuData(WgpuModelGpuData& m) {
    if (m.bind_group)       { wgpuBindGroupRelease(m.bind_group);    m.bind_group = nullptr; }
    if (m.vertex_storage)   { wgpuBufferRelease(m.vertex_storage);   m.vertex_storage = nullptr; }
    if (m.index_buffer)     { wgpuBufferRelease(m.index_buffer);     m.index_buffer = nullptr; }
    if (m.mesh_storage)     { wgpuBufferRelease(m.mesh_storage);     m.mesh_storage = nullptr; }
    if (m.instance_storage) { wgpuBufferRelease(m.instance_storage); m.instance_storage = nullptr; }
    if (m.visible_buffer)   { wgpuBufferRelease(m.visible_buffer);   m.visible_buffer = nullptr; }
    m.vertex_bytes   = 0;
    m.index_count    = 0;
    m.mesh_count     = 0;
    m.instance_count = 0;
    m.visible_buffer_capacity = 0;
    m.meshes.clear();
    m.instances.clear();
    m.mesh_draws.clear();
    m.visible_flat_scratch.clear();
}

// -----------------------------------------------------------------------------
// WGSL main pipeline — vertex pulling.
//
// Vertex bytes are read manually from a u32 storage buffer (3 u32 per vertex,
// matching INSTANCED_VERTEX_STRIDE_BYTES=12). gl_BaseVertex is folded into
// vertex_index by the WebGPU IA, so per-mesh draws set baseVertex =
// mesh.vbo_byte_offset / 12 and the shader indexes the global storage array
// directly. firstInstance carries the global instance slot, fetched as
// @builtin(instance_index).
// -----------------------------------------------------------------------------

static const char* MAIN_WGSL = R"(
struct InstanceRecord {
    transform: mat4x4<f32>,
    object_id: u32,
    color_override: u32,
    mesh_id: u32,
    _pad1: u32,
};

struct MeshQuant {
    aabb_min: vec4<f32>,
    aabb_max: vec4<f32>,
};

struct FrameUniforms {
    view_proj:    mat4x4<f32>,
    light_dir:    vec4<f32>,
    fill_dir:     vec4<f32>,
    sky_color:    vec4<f32>,
    ground_color: vec4<f32>,
};

@group(0) @binding(0) var<uniform> u_frame: FrameUniforms;

@group(1) @binding(0) var<storage, read> vertices:  array<u32>;
@group(1) @binding(1) var<storage, read> meshes:    array<MeshQuant>;
@group(1) @binding(2) var<storage, read> instances: array<InstanceRecord>;
// Per-frame compacted visible list: visible[firstInstance + i] picks the
// real instance for this draw slot. firstInstance is set per drawIndexed
// call so each mesh reads its own contiguous slice of `visible`.
@group(1) @binding(3) var<storage, read> visible:   array<u32>;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) normal:    vec3<f32>,
    @location(1) color:     vec4<f32>,
    @location(2) world_pos: vec3<f32>,
};

// Sign-extend an i8 packed into the byte_idx'th byte of `packed`.
fn extractI8(packed: u32, byte_idx: u32) -> i32 {
    let raw = i32((packed >> (byte_idx * 8u)) & 0xFFu);
    return select(raw, raw - 256, raw >= 128);
}

// Meyer et al. octahedral normal decode. Input in [-1,1]^2.
fn octDecode(e: vec2<f32>) -> vec3<f32> {
    var n = vec3<f32>(e.x, e.y, 1.0 - abs(e.x) - abs(e.y));
    if (n.z < 0.0) {
        let tx = select(-1.0, 1.0, n.x >= 0.0);
        let ty = select(-1.0, 1.0, n.y >= 0.0);
        n = vec3<f32>((1.0 - abs(n.y)) * tx, (1.0 - abs(n.x)) * ty, n.z);
    }
    return normalize(n);
}

@vertex
fn vs_main(@builtin(vertex_index)   vid: u32,
           @builtin(instance_index) iid: u32) -> VsOut {
    let inst_idx = visible[iid];
    let inst = instances[inst_idx];
    let mq   = meshes[inst.mesh_id];

    let w0 = vertices[vid * 3u + 0u];
    let w1 = vertices[vid * 3u + 1u];
    let w2 = vertices[vid * 3u + 2u];

    let px = f32(w0 & 0xFFFFu)         / 65535.0;
    let py = f32((w0 >> 16u) & 0xFFFFu) / 65535.0;
    let pz = f32(w1 & 0xFFFFu)         / 65535.0;
    let pos_local = mix(mq.aabb_min.xyz, mq.aabb_max.xyz, vec3<f32>(px, py, pz));

    let nx = f32(extractI8(w1, 2u)) / 127.0;
    let ny = f32(extractI8(w1, 3u)) / 127.0;
    let n_local = octDecode(vec2<f32>(nx, ny));

    let r = f32(w2 & 0xFFu)          / 255.0;
    let g = f32((w2 >>  8u) & 0xFFu) / 255.0;
    let b = f32((w2 >> 16u) & 0xFFu) / 255.0;
    let a = f32((w2 >> 24u) & 0xFFu) / 255.0;

    let world4 = inst.transform * vec4<f32>(pos_local, 1.0);
    let rot = mat3x3<f32>(inst.transform[0].xyz,
                          inst.transform[1].xyz,
                          inst.transform[2].xyz);
    let n_world = normalize(rot * n_local);
    let det = determinant(rot);
    let n_final = select(n_world, -n_world, det < 0.0);

    var color = vec4<f32>(r, g, b, a);
    if (inst.color_override != 0u) {
        let cr = f32(inst.color_override         & 0xFFu) / 255.0;
        let cg = f32((inst.color_override >>  8u) & 0xFFu) / 255.0;
        let cb = f32((inst.color_override >> 16u) & 0xFFu) / 255.0;
        let ca = f32((inst.color_override >> 24u) & 0xFFu) / 255.0;
        if (ca > 0.0) { color = vec4<f32>(cr, cg, cb, ca); }
    }

    var out: VsOut;
    out.clip_pos  = u_frame.view_proj * world4;
    out.normal    = n_final;
    out.color     = color;
    out.world_pos = world4.xyz;
    return out;
}

@fragment
fn fs_main(in: VsOut) -> @location(0) vec4<f32> {
    var n = normalize(in.normal);

    // World +Z is up (BIM convention). Hemisphere ambient: faces pointing
    // up read sky, faces pointing down read ground, lerp by n.z.
    let hemi_t  = 0.5 + 0.5 * n.z;
    let ambient = mix(u_frame.ground_color.xyz, u_frame.sky_color.xyz, hemi_t);

    let key  = max(dot(n, u_frame.light_dir.xyz), 0.0);
    let fill = max(dot(n, u_frame.fill_dir.xyz),  0.0) * 0.35;

    let color = in.color.xyz * (ambient + (key + fill) * 0.7);
    return vec4<f32>(color, in.color.a);
}
)";

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

WgpuViewportWindow::WgpuViewportWindow(QWindow* parent)
    : QWindow(parent) {
    // wgpu doesn't need a GL context; we just need a real native window that
    // the platform window manager has actually created. OpenGLSurface is the
    // most portable way to ask Qt for a hardware-rendering-ready native
    // window — we never bind a GL context on top of it.
    setSurfaceType(QSurface::OpenGLSurface);
}

WgpuViewportWindow::~WgpuViewportWindow() {
    shutdown();
}

void WgpuViewportWindow::setBackgroundColor(const QColor& color) {
    background_color_ = color;
    if (isExposed()) requestUpdate();
}

// -----------------------------------------------------------------------------
// Sidecar load + GPU upload
// -----------------------------------------------------------------------------

void WgpuViewportWindow::queueLoadSidecar(const QString& path) {
    if (wgpu_initialized_) {
        loadSidecar(path);
    } else {
        pending_sidecars_.push_back(path);
    }
}

uint32_t WgpuViewportWindow::loadSidecar(const QString& path) {
    if (!wgpu_initialized_) {
        qWarning().noquote() << "loadSidecar called before wgpu init:" << path;
        return 0;
    }

    // Tilde expansion — shells handle this inside double-quoted args, but a
    // literal "~/..." from a launcher / command-line wouldn't. Cheap to do
    // here so the failure mode isn't "fopen returned ENOENT".
    QString resolved = path;
    if (resolved.startsWith("~/")) {
        resolved = QDir::homePath() + resolved.mid(1);
    }

    auto data_opt = readSidecar(resolved.toStdString());
    if (!data_opt) {
        // Triage: distinguish missing file from magic/version mismatch by
        // peeking the header ourselves, so users know which to fix.
        QFile f(resolved);
        if (!f.exists()) {
            qWarning().noquote() << "Sidecar not found:" << resolved;
        } else if (!f.open(QIODevice::ReadOnly)) {
            qWarning().noquote() << "Sidecar unreadable:" << resolved
                                 << "(" << f.errorString() << ")";
        } else {
            uint32_t header[3] = { 0, 0, 0 };
            const qint64 got = f.read(reinterpret_cast<char*>(header), sizeof(header));
            if (got < qint64(sizeof(header))) {
                qWarning().noquote() << "Sidecar truncated:" << resolved
                                     << "(only" << got << "bytes — expected ≥ 12)";
            } else if (header[0] != SIDECAR_MAGIC) {
                qWarning().noquote().nospace()
                    << "Sidecar magic mismatch: " << resolved
                    << " — got 0x" << QString::number(header[0], 16)
                    << ", expected 0x" << QString::number(SIDECAR_MAGIC, 16)
                    << " (\"IFVW\")";
            } else if (header[1] != SIDECAR_VERSION) {
                qWarning().noquote().nospace()
                    << "Sidecar schema mismatch: " << resolved
                    << " — file is v" << header[1]
                    << ", this build expects v" << SIDECAR_VERSION
                    << ". Re-bake the .ifc with a viewer at the matching schema.";
            } else if (header[2] != SIDECAR_ENDIAN) {
                qWarning().noquote() << "Sidecar endianness mismatch:" << resolved
                                     << "(cross-platform load not supported)";
            } else {
                qWarning().noquote() << "Sidecar read failed past the header:" << resolved;
            }
        }
        return 0;
    }

    const uint32_t mid = next_model_id_++;
    applyCachedModel(mid, std::move(*data_opt));
    return mid;
}

void WgpuViewportWindow::applyCachedModel(uint32_t model_id, SidecarData data) {
    if (!device_ || !queue_) {
        qWarning() << "applyCachedModel without an initialised device";
        return;
    }

    // Replace any existing state for this id.
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        releaseWgpuModelGpuData(it->second);
        models_gpu_.erase(it);
    }

    WgpuModelGpuData m;
    m.vertex_bytes   = data.vertices.size();
    m.index_count    = uint32_t(data.indices.size());
    m.mesh_count     = uint32_t(data.meshes.size());
    m.instance_count = uint32_t(data.instances.size());

    // Vertex storage — raw bytes at INSTANCED_VERTEX_STRIDE_BYTES layout. The
    // vertex shader will read this as a u8 storage buffer in stage 3.
    m.vertex_storage = createBufferWithData(
        device_, queue_,
        data.vertices.data(), data.vertices.size(),
        WGPUBufferUsage_Storage,
        "model.vertex_storage");

    // Index buffer — mesh-local u32 indices; baseVertex applied per-draw.
    m.index_buffer = createBufferWithData(
        device_, queue_,
        data.indices.data(), data.indices.size() * sizeof(uint32_t),
        WGPUBufferUsage_Index,
        "model.index_buffer");

    // Derive MeshGpu[] (vec4 aabb_min + vec4 aabb_max) from MeshInfo's
    // local_aabb_*. Mirrors the GL backend's mesh_info_ssbo population.
    std::vector<MeshGpu> mesh_gpu;
    mesh_gpu.reserve(data.meshes.size());
    for (const auto& mi : data.meshes) {
        MeshGpu mg = {};
        mg.aabb_min[0] = mi.local_aabb_min[0];
        mg.aabb_min[1] = mi.local_aabb_min[1];
        mg.aabb_min[2] = mi.local_aabb_min[2];
        mg.aabb_min[3] = 0.0f;
        mg.aabb_max[0] = mi.local_aabb_max[0];
        mg.aabb_max[1] = mi.local_aabb_max[1];
        mg.aabb_max[2] = mi.local_aabb_max[2];
        mg.aabb_max[3] = 0.0f;
        mesh_gpu.push_back(mg);
    }
    m.mesh_storage = createBufferWithData(
        device_, queue_,
        mesh_gpu.data(), mesh_gpu.size() * sizeof(MeshGpu),
        WGPUBufferUsage_Storage,
        "model.mesh_storage");

    // Derive InstanceGpu[] from InstanceCpu[]. Stage 2 uses the cached
    // `transform` directly (stage matrices are identity until stage 5+
    // adds federation composition).
    std::vector<InstanceGpu> inst_gpu;
    inst_gpu.reserve(data.instances.size());
    for (const auto& ic : data.instances) {
        InstanceGpu ig = {};
        std::memcpy(ig.transform, ic.transform, sizeof(ig.transform));
        ig.object_id            = ic.object_id;
        ig.color_override_rgba8 = ic.color_override_rgba8;
        ig.mesh_id              = ic.mesh_id;
        inst_gpu.push_back(ig);
    }
    m.instance_storage = createBufferWithData(
        device_, queue_,
        inst_gpu.data(), inst_gpu.size() * sizeof(InstanceGpu),
        WGPUBufferUsage_Storage,
        "model.instance_storage");

    // Pre-size the visible buffer for the worst case (every instance visible).
    // Per-frame cull writes a u32 list into it via wgpuQueueWriteBuffer; we
    // never grow it so the bind group reference stays valid for the model's
    // lifetime. Minimum size 4 bytes — wgpu rejects zero-sized buffers.
    const size_t visible_bytes = std::max<size_t>(
        size_t(data.instances.size()) * sizeof(uint32_t), 4u);
    WGPUBufferDescriptor vb_desc = {};
    vb_desc.size  = visible_bytes;
    vb_desc.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
    vb_desc.label = svFromCStr("model.visible_buffer");
    m.visible_buffer          = wgpuDeviceCreateBuffer(device_, &vb_desc);
    m.visible_buffer_capacity = std::max<size_t>(data.instances.size(), 1u);

    // Hand off CPU mirrors (cull / picking will need them later).
    m.meshes    = std::move(data.meshes);
    m.instances = std::move(data.instances);
    m.mesh_draws.assign(m.meshes.size(), WgpuModelGpuData::MeshDraw{});
    m.visible_flat_scratch.reserve(m.instances.size());

    auto [inserted, _] = models_gpu_.emplace(model_id, std::move(m));
    WgpuModelGpuData& mref = inserted->second;
    buildModelBindGroup(mref);

    qInfo().noquote().nospace()
        << "[wgpu] applyCachedModel mid=" << model_id
        << " verts=" << mref.vertex_bytes << "B"
        << " idx="   << mref.index_count
        << " meshes=" << mref.mesh_count
        << " instances=" << mref.instance_count;

    if (!initial_view_applied_) {
        viewAll();
        initial_view_applied_ = true;
    }
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::removeModel(uint32_t model_id) {
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return;
    releaseWgpuModelGpuData(it->second);
    models_gpu_.erase(it);
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::resetScene() {
    for (auto& [mid, m] : models_gpu_) releaseWgpuModelGpuData(m);
    models_gpu_.clear();
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::flushPendingSidecarQueue() {
    while (!pending_sidecars_.empty()) {
        const QString p = pending_sidecars_.front();
        pending_sidecars_.pop_front();
        loadSidecar(p);
    }
}

// -----------------------------------------------------------------------------
// Lifecycle
// -----------------------------------------------------------------------------

void WgpuViewportWindow::exposeEvent(QExposeEvent* /*event*/) {
    if (!isExposed()) return;

    if (!wgpu_initialized_) {
        if (!initWgpu()) {
            qWarning() << "wgpu init failed; viewport will not render";
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

void WgpuViewportWindow::resizeEvent(QResizeEvent* /*event*/) {
    if (!wgpu_initialized_ || !isExposed()) return;
    const int w = int(width()  * devicePixelRatio());
    const int h = int(height() * devicePixelRatio());
    if (w > 0 && h > 0) {
        configureSurface(w, h);
        requestUpdate();
    }
}

bool WgpuViewportWindow::event(QEvent* event) {
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

bool WgpuViewportWindow::initWgpu() {
    // Optional: log everything wgpu-native says at warn+ so backend init
    // problems surface in the console rather than being swallowed.
    wgpuSetLogCallback(onWgpuLog, nullptr);
    wgpuSetLogLevel(WGPULogLevel_Warn);

    instance_ = wgpuCreateInstance(nullptr);
    if (!instance_) {
        qWarning() << "wgpuCreateInstance returned null";
        return false;
    }

    if (!createSurface()) return false;

    // ---- Async request adapter -------------------------------------------
    struct AdapterReq { WGPUAdapter adapter = nullptr; bool done = false; bool ok = false; };
    AdapterReq areq;

    WGPURequestAdapterOptions adapter_opts = {};
    adapter_opts.compatibleSurface = surface_;
    adapter_opts.powerPreference   = WGPUPowerPreference_HighPerformance;

    WGPURequestAdapterCallbackInfo acb = {};
    acb.mode      = WGPUCallbackMode_AllowProcessEvents;
    acb.callback  = [](WGPURequestAdapterStatus status, WGPUAdapter adapter,
                       WGPUStringView message, void* ud1, void* /*ud2*/) {
        auto* r = static_cast<AdapterReq*>(ud1);
        r->done = true;
        if (status == WGPURequestAdapterStatus_Success) {
            r->adapter = adapter;
            r->ok = true;
        } else {
            qWarning().noquote() << "RequestAdapter failed:" << sv(message);
        }
    };
    acb.userdata1 = &areq;

    wgpuInstanceRequestAdapter(instance_, &adapter_opts, acb);
    while (!areq.done) wgpuInstanceProcessEvents(instance_);
    if (!areq.ok) return false;
    adapter_ = areq.adapter;

    // ---- Async request device --------------------------------------------
    struct DeviceReq { WGPUDevice device = nullptr; bool done = false; bool ok = false; };
    DeviceReq dreq;

    WGPUDeviceDescriptor dev_desc = {};
    // Surface uncaptured errors (validation failures etc.) into qWarning so
    // they're attributable rather than silently swallowed.
    dev_desc.uncapturedErrorCallbackInfo.callback = onUncapturedError;

    WGPURequestDeviceCallbackInfo dcb = {};
    dcb.mode     = WGPUCallbackMode_AllowProcessEvents;
    dcb.callback = [](WGPURequestDeviceStatus status, WGPUDevice device,
                      WGPUStringView message, void* ud1, void* /*ud2*/) {
        auto* r = static_cast<DeviceReq*>(ud1);
        r->done = true;
        if (status == WGPURequestDeviceStatus_Success) {
            r->device = device;
            r->ok = true;
        } else {
            qWarning().noquote() << "RequestDevice failed:" << sv(message);
        }
    };
    dcb.userdata1 = &dreq;

    wgpuAdapterRequestDevice(adapter_, &dev_desc, dcb);
    while (!dreq.done) wgpuInstanceProcessEvents(instance_);
    if (!dreq.ok) return false;
    device_ = dreq.device;
    queue_  = wgpuDeviceGetQueue(device_);

    // ---- Pick a surface format -------------------------------------------
    WGPUSurfaceCapabilities caps = {};
    if (wgpuSurfaceGetCapabilities(surface_, adapter_, &caps) != WGPUStatus_Success
        || caps.formatCount == 0) {
        qWarning() << "wgpuSurfaceGetCapabilities returned no formats";
        return false;
    }
    surface_format_ = caps.formats[0];  // preferred format per wgpu docs
    wgpuSurfaceCapabilitiesFreeMembers(caps);

    if (!buildPipelines()) return false;

    qInfo() << "wgpu init OK; surface format =" << int(surface_format_);
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
#endif

bool WgpuViewportWindow::createSurface() {
    WGPUSurfaceDescriptor surface_desc = {};

#if defined(Q_OS_LINUX)
    const QString platform = QGuiApplication::platformName();
    if (platform == "xcb") {
#  if __has_include(<X11/Xlib.h>)
        auto* x11 = qApp->nativeInterface<QNativeInterface::QX11Application>();
        if (!x11 || !x11->display()) {
            qWarning() << "Could not get X11 Display* from Qt";
            return false;
        }
        WGPUSurfaceSourceXlibWindow xlib = {};
        xlib.chain.sType = WGPUSType_SurfaceSourceXlibWindow;
        xlib.display = x11->display();
        xlib.window  = static_cast<uint64_t>(winId());
        surface_desc.nextInChain = &xlib.chain;
        surface_ = wgpuInstanceCreateSurface(instance_, &surface_desc);
#  else
        qWarning() << "Built without Xlib headers; cannot create X11 surface";
        return false;
#  endif
    } else if (platform == "wayland") {
#  if __has_include(<wayland-client-core.h>)
        auto* wl = qApp->nativeInterface<QNativeInterface::QWaylandApplication>();
        if (!wl || !wl->display()) {
            qWarning() << "Could not get Wayland wl_display* from Qt";
            return false;
        }
        // The wl_surface for a window is exposed via the QPA window-handle
        // accessor on the native interface (not the application-wide one).
        // For stage 1 we fail loud; stage-1.5 fills this in.
        qWarning() << "Wayland wgpu surface creation not yet wired (stage 1.5)";
        return false;
#  else
        qWarning() << "Built without Wayland headers; cannot create Wayland surface";
        return false;
#  endif
    } else {
        qWarning().noquote() << "Unsupported Qt platform for wgpu surface:" << platform;
        return false;
    }
#else
    // macOS / Windows native-handle wiring lands when those targets become
    // active. Stage-1 development happens on Linux.
    qWarning() << "wgpu surface creation not yet wired for this platform";
    return false;
#endif

    if (!surface_) {
        qWarning() << "wgpuInstanceCreateSurface returned null";
        return false;
    }
    return true;
}

// -----------------------------------------------------------------------------
// Surface (re)configure + render
// -----------------------------------------------------------------------------

void WgpuViewportWindow::configureSurface(int width_px, int height_px) {
    WGPUSurfaceConfiguration cfg = {};
    cfg.device      = device_;
    cfg.format      = surface_format_;
    // CopySrc lets captureNextFrameToPng copy the surface texture back to
    // host memory. Trivial cost on all known backends.
    cfg.usage       = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_CopySrc;
    cfg.width       = uint32_t(width_px);
    cfg.height      = uint32_t(height_px);
    cfg.presentMode = WGPUPresentMode_Fifo;
    cfg.alphaMode   = WGPUCompositeAlphaMode_Auto;

    wgpuSurfaceConfigure(surface_, &cfg);
    configured_w_       = width_px;
    configured_h_       = height_px;
    surface_configured_ = true;
    ensureDepthTexture(width_px, height_px);
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

static inline void rowVec(const float vp[16], int row, float out[4]) {
    out[0] = vp[0 * 4 + row];
    out[1] = vp[1 * 4 + row];
    out[2] = vp[2 * 4 + row];
    out[3] = vp[3 * 4 + row];
}

static inline void planeNormalize(float p[4]) {
    const float len = std::sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]);
    if (len > 0.0f) {
        const float inv = 1.0f / len;
        p[0] *= inv; p[1] *= inv; p[2] *= inv; p[3] *= inv;
    }
}

static void extractFrustumPlanes(const float vp[16], float planes[6][4]) {
    float r0[4], r1[4], r2[4], r3[4];
    rowVec(vp, 0, r0);
    rowVec(vp, 1, r1);
    rowVec(vp, 2, r2);
    rowVec(vp, 3, r3);

    // left   = r3 + r0
    // right  = r3 - r0
    // bottom = r3 + r1
    // top    = r3 - r1
    // near   = r2          (WebGPU clip z >= 0)
    // far    = r3 - r2
    for (int i = 0; i < 4; ++i) {
        planes[0][i] = r3[i] + r0[i];
        planes[1][i] = r3[i] - r0[i];
        planes[2][i] = r3[i] + r1[i];
        planes[3][i] = r3[i] - r1[i];
        planes[4][i] = r2[i];
        planes[5][i] = r3[i] - r2[i];
    }
    for (int p = 0; p < 6; ++p) planeNormalize(planes[p]);
}

// Returns false iff the AABB is fully outside any one plane (early-rejects
// trivially-invisible instances). May return true for boxes that straddle
// the frustum — that's fine, those still need to draw.
static bool aabbInFrustum(const float mn[3], const float mx[3],
                          const float planes[6][4]) {
    for (int p = 0; p < 6; ++p) {
        const float a = planes[p][0], b = planes[p][1], c = planes[p][2], d = planes[p][3];
        // p-vertex: the AABB corner furthest along the plane normal.
        const float px = (a >= 0.0f) ? mx[0] : mn[0];
        const float py = (b >= 0.0f) ? mx[1] : mn[1];
        const float pz = (c >= 0.0f) ? mx[2] : mn[2];
        if (a * px + b * py + c * pz + d < 0.0f) return false;
    }
    return true;
}

void WgpuViewportWindow::setBenchmarkFrames(int frames) {
    bench_total_    = std::max(0, frames);
    bench_count_    = 0;
    bench_yaw_start_ = camera_yaw_deg_;
    bench_frame_ms_.clear();
    bench_frame_ms_.reserve(size_t(bench_total_));
    if (isExposed() && bench_total_ > 0) requestUpdate();
}

void WgpuViewportWindow::cullModelCpu(WgpuModelGpuData& m, const float planes[6][4]) {
    if (m.instances.empty() || m.meshes.empty() || !m.visible_buffer) {
        for (auto& d : m.mesh_draws) d.instance_count = 0;
        return;
    }

    // Per-mesh visible-instance buckets. Allocated once per cull from scratch
    // vectors held on the model (no fresh heap on the per-frame path).
    static thread_local std::vector<std::vector<uint32_t>> per_mesh_visible;
    if (per_mesh_visible.size() < m.meshes.size()) per_mesh_visible.resize(m.meshes.size());
    for (size_t mi = 0; mi < m.meshes.size(); ++mi) per_mesh_visible[mi].clear();

    for (uint32_t i = 0; i < uint32_t(m.instances.size()); ++i) {
        const auto& inst = m.instances[i];
        if (inst.mesh_id >= m.meshes.size()) continue;
        if (!aabbInFrustum(inst.world_aabb_min, inst.world_aabb_max, planes)) continue;
        per_mesh_visible[inst.mesh_id].push_back(i);
    }

    // Flatten into m.visible_flat_scratch and populate per-mesh draws.
    m.visible_flat_scratch.clear();
    m.mesh_draws.assign(m.meshes.size(), WgpuModelGpuData::MeshDraw{});
    for (uint32_t mi = 0; mi < m.meshes.size(); ++mi) {
        const MeshInfo& mesh = m.meshes[mi];
        WgpuModelGpuData::MeshDraw& d = m.mesh_draws[mi];
        d.first_instance = uint32_t(m.visible_flat_scratch.size());
        d.instance_count = uint32_t(per_mesh_visible[mi].size());
        d.first_index    = mesh.ebo_byte_offset / uint32_t(sizeof(uint32_t));
        d.base_vertex    = int32_t(mesh.vbo_byte_offset / INSTANCED_VERTEX_STRIDE_BYTES);
        d.index_count    = mesh.index_count;
        for (uint32_t inst_idx : per_mesh_visible[mi]) {
            m.visible_flat_scratch.push_back(inst_idx);
        }
    }

    // Upload the visible list. Round up to 4-byte multiple (always true for
    // u32 arrays). Empty visible list still uploads one zero so the bind
    // group has something well-defined; the per-mesh loop will skip the draw.
    const size_t bytes_to_upload = std::max<size_t>(
        m.visible_flat_scratch.size() * sizeof(uint32_t), sizeof(uint32_t));
    static const uint32_t zero = 0;
    const void*  src  = m.visible_flat_scratch.empty()
                          ? static_cast<const void*>(&zero)
                          : static_cast<const void*>(m.visible_flat_scratch.data());
    wgpuQueueWriteBuffer(queue_, m.visible_buffer, 0, src, bytes_to_upload);
}

void WgpuViewportWindow::render() {
    // Time the whole render() body (cull + encode + present) for the
    // benchmark stats. Started before any wgpu work so cull is included.
    QElapsedTimer frame_timer;
    if (bench_total_ > 0) frame_timer.start();

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
            qWarning() << "GetCurrentTexture status" << int(surf_tex.status);
            return;
    }

    WGPUTextureView view = wgpuTextureCreateView(surf_tex.texture, nullptr);

    updateFrameUniforms();

    // Per-frame cull: extract frustum planes from the same VP we just wrote
    // into the uniform, then run cullModelCpu on every visible model. The
    // cull writes its results directly into each model's visible_buffer via
    // wgpuQueueWriteBuffer — these writes are sequenced before the draw
    // commands we encode next.
    last_visible_objects_   = 0;
    last_visible_triangles_ = 0;
    last_sub_draws_         = 0;
    {
        const QVector3D target(camera_target_[0], camera_target_[1], camera_target_[2]);
        const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                       camera_yaw_deg_, camera_pitch_deg_);
        QMatrix4x4 v; v.lookAt(eye, target, QVector3D(0.0f, 0.0f, 1.0f));
        const float aspect = (configured_h_ > 0)
                                ? float(configured_w_) / float(configured_h_) : 1.0f;
        QMatrix4x4 p; p.perspective(camera_fov_y_deg_, aspect, camera_near_, camera_far_);
        QMatrix4x4 z; z(2, 2) = 0.5f; z(2, 3) = 0.5f;
        const QMatrix4x4 vp = z * p * v;
        float planes[6][4];
        extractFrustumPlanes(vp.constData(), planes);
        for (auto& [mid, m] : models_gpu_) {
            if (m.hidden) continue;
            cullModelCpu(m, planes);
            for (const auto& d : m.mesh_draws) {
                if (d.instance_count == 0 || d.index_count == 0) continue;
                last_visible_objects_   += d.instance_count;
                last_visible_triangles_ += (d.index_count / 3u) * d.instance_count;
                last_sub_draws_         += 1;
            }
        }
    }

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    WGPURenderPassColorAttachment color = {};
    color.view       = view;
    color.loadOp     = WGPULoadOp_Clear;
    color.storeOp    = WGPUStoreOp_Store;
    color.clearValue = {
        background_color_.redF(),
        background_color_.greenF(),
        background_color_.blueF(),
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

    if (main_pipeline_ && frame_bind_group_ && !models_gpu_.empty()) {
        wgpuRenderPassEncoderSetPipeline(pass, main_pipeline_);
        wgpuRenderPassEncoderSetBindGroup(pass, 0, frame_bind_group_, 0, nullptr);

        for (const auto& [mid, m] : models_gpu_) {
            if (m.hidden || !m.bind_group || !m.index_buffer || m.index_count == 0) continue;

            wgpuRenderPassEncoderSetBindGroup(pass, 1, m.bind_group, 0, nullptr);
            wgpuRenderPassEncoderSetIndexBuffer(pass, m.index_buffer,
                                                WGPUIndexFormat_Uint32,
                                                0, WGPU_WHOLE_SIZE);

            // One drawIndexed per non-empty mesh. instanceCount is the number
            // of frustum-surviving instances of this mesh; firstInstance is
            // their offset into m.visible_buffer (consumed by the WGSL
            // `visible[iid]` indirection). All-instances-culled meshes are
            // skipped — no draw call issued at all.
            for (const auto& d : m.mesh_draws) {
                if (d.instance_count == 0 || d.index_count == 0) continue;
                wgpuRenderPassEncoderDrawIndexed(
                    pass,
                    d.index_count,
                    d.instance_count,
                    d.first_index,
                    d.base_vertex,
                    d.first_instance);
            }
        }
    }

    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    // ---- Optional capture: encode copy on the same command buffer -------
    WGPUBuffer    capture_buffer    = nullptr;
    uint32_t      capture_padded_bpr = 0;
    const bool    want_capture       = !pending_screenshot_path_.isEmpty();
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
                qWarning().noquote() << "wgpu MapAsync failed:" << sv(message);
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

            if (img.save(pending_screenshot_path_, "PNG")) {
                qInfo().noquote() << "[wgpu] saved screenshot:"
                                  << pending_screenshot_path_ << "(" << w << "x" << h << ")";
            } else {
                qWarning().noquote() << "[wgpu] QImage::save failed for"
                                     << pending_screenshot_path_;
            }
        }
        wgpuBufferRelease(capture_buffer);

        const bool quit_after = pending_screenshot_quit_;
        pending_screenshot_path_.clear();
        pending_screenshot_quit_ = false;
        if (quit_after) QCoreApplication::quit();
    }

    wgpuSurfacePresent(surface_);
    wgpuTextureRelease(surf_tex.texture);

    // ---- Benchmark integration + auto-quit -------------------------------
    if (bench_total_ > 0) {
        const float ms = float(frame_timer.nsecsElapsed()) / 1e6f;

        // Warm-up frames are dropped from the sample. The yaw advance starts
        // immediately so the warmup frames already exercise different views.
        if (bench_count_ >= bench_warmup_) {
            bench_frame_ms_.push_back(ms);
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
            qInfo().noquote().nospace()
                << "\n=== BENCHMARK (" << bench_total_ << " frames, orbit "
                << total_sweep << "° at " << bench_yaw_speed_ << "°/frame) ===";
            qInfo().noquote().nospace()
                << "  avg: "    << avg    << " ms (" << (avg    > 0 ? 1000.0f/avg    : 0.0f) << " fps)";
            qInfo().noquote().nospace()
                << "  median: " << median << " ms (" << (median > 0 ? 1000.0f/median : 0.0f) << " fps)";
            qInfo().noquote().nospace()
                << "  p1: "  << p1  << " ms  p99: " << p99 << " ms";
            qInfo().noquote().nospace()
                << "  last frame: obj " << last_visible_objects_
                << "  tri " << last_visible_triangles_
                << "  sub_draws " << last_sub_draws_
                << "  hiz_rej 0";  // HiZ lands in stage 7
            qInfo().noquote() << "=== END BENCHMARK ===\n";

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

bool WgpuViewportWindow::buildPipelines() {
    // ---- Bind group layouts ----------------------------------------------
    WGPUBindGroupLayoutEntry frame_entries[1] = {};
    frame_entries[0].binding = 0;
    frame_entries[0].visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
    frame_entries[0].buffer.type = WGPUBufferBindingType_Uniform;
    frame_entries[0].buffer.minBindingSize = sizeof(FrameUniforms);

    WGPUBindGroupLayoutDescriptor frame_bgl_desc = {};
    frame_bgl_desc.entryCount = 1;
    frame_bgl_desc.entries    = frame_entries;
    frame_bgl_desc.label      = svFromCStr("ifcviewer-wgpu.frame_bgl");
    frame_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &frame_bgl_desc);

    WGPUBindGroupLayoutEntry model_entries[4] = {};
    for (int i = 0; i < 4; ++i) {
        model_entries[i].binding     = uint32_t(i);
        model_entries[i].visibility  = WGPUShaderStage_Vertex;
        model_entries[i].buffer.type = WGPUBufferBindingType_ReadOnlyStorage;
    }
    WGPUBindGroupLayoutDescriptor model_bgl_desc = {};
    model_bgl_desc.entryCount = 4;
    model_bgl_desc.entries    = model_entries;
    model_bgl_desc.label      = svFromCStr("ifcviewer-wgpu.model_bgl");
    model_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &model_bgl_desc);

    // ---- Pipeline layout -------------------------------------------------
    WGPUBindGroupLayout bgls[2] = { frame_bgl_, model_bgl_ };
    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 2;
    pl_desc.bindGroupLayouts     = bgls;
    pl_desc.label                = svFromCStr("ifcviewer-wgpu.pipeline_layout");
    pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    // ---- Shader module ---------------------------------------------------
    WGPUShaderSourceWGSL wgsl_src = {};
    wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl_src.code        = svFromCStr(MAIN_WGSL);

    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl_src.chain;
    sm_desc.label       = svFromCStr("ifcviewer-wgpu.main_wgsl");
    main_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    // ---- Render pipeline -------------------------------------------------
    WGPUColorTargetState color_target = {};
    color_target.format    = surface_format_;
    color_target.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = main_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &color_target;

    WGPUDepthStencilState depth = {};
    depth.format              = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled   = WGPUOptionalBool_True;
    depth.depthCompare        = WGPUCompareFunction_Less;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout            = pipeline_layout_;
    rp_desc.label             = svFromCStr("ifcviewer-wgpu.main_pipeline");
    rp_desc.vertex.module     = main_shader_module_;
    rp_desc.vertex.entryPoint = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount = 0;       // vertex pulling: no IA bindings
    rp_desc.fragment          = &frag;
    rp_desc.depthStencil      = &depth;
    rp_desc.primitive.topology = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode = WGPUCullMode_Back;
    rp_desc.primitive.frontFace = WGPUFrontFace_CCW;
    rp_desc.multisample.count = 1;
    rp_desc.multisample.mask  = 0xFFFFFFFFu;

    main_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!main_pipeline_) {
        qWarning() << "wgpu main render pipeline creation failed";
        return false;
    }

    // ---- Per-frame uniform buffer + bind group ---------------------------
    WGPUBufferDescriptor fb_desc = {};
    fb_desc.size  = sizeof(FrameUniforms);
    fb_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    fb_desc.label = svFromCStr("ifcviewer-wgpu.frame_uniform");
    frame_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &fb_desc);

    WGPUBindGroupEntry fbg_entries[1] = {};
    fbg_entries[0].binding = 0;
    fbg_entries[0].buffer  = frame_uniform_buffer_;
    fbg_entries[0].offset  = 0;
    fbg_entries[0].size    = sizeof(FrameUniforms);
    WGPUBindGroupDescriptor fbg_desc = {};
    fbg_desc.layout     = frame_bgl_;
    fbg_desc.entryCount = 1;
    fbg_desc.entries    = fbg_entries;
    fbg_desc.label      = svFromCStr("ifcviewer-wgpu.frame_bind_group");
    frame_bind_group_ = wgpuDeviceCreateBindGroup(device_, &fbg_desc);

    return true;
}

void WgpuViewportWindow::buildModelBindGroup(WgpuModelGpuData& m) {
    if (m.bind_group) {
        wgpuBindGroupRelease(m.bind_group);
        m.bind_group = nullptr;
    }
    if (!m.vertex_storage || !m.mesh_storage || !m.instance_storage || !m.visible_buffer) {
        // Empty model — no bind group needed; the draw loop will skip it.
        return;
    }

    WGPUBindGroupEntry entries[4] = {};
    entries[0].binding = 0;
    entries[0].buffer  = m.vertex_storage;
    entries[0].size    = WGPU_WHOLE_SIZE;
    entries[1].binding = 1;
    entries[1].buffer  = m.mesh_storage;
    entries[1].size    = WGPU_WHOLE_SIZE;
    entries[2].binding = 2;
    entries[2].buffer  = m.instance_storage;
    entries[2].size    = WGPU_WHOLE_SIZE;
    entries[3].binding = 3;
    entries[3].buffer  = m.visible_buffer;
    entries[3].size    = WGPU_WHOLE_SIZE;

    WGPUBindGroupDescriptor desc = {};
    desc.layout     = model_bgl_;
    desc.entryCount = 4;
    desc.entries    = entries;
    desc.label      = svFromCStr("ifcviewer-wgpu.model_bind_group");
    m.bind_group = wgpuDeviceCreateBindGroup(device_, &desc);
}

// -----------------------------------------------------------------------------
// Depth attachment
// -----------------------------------------------------------------------------

void WgpuViewportWindow::ensureDepthTexture(int w, int h) {
    if (w == depth_w_ && h == depth_h_ && depth_view_) return;
    releaseDepthTexture();

    WGPUTextureDescriptor desc = {};
    desc.usage         = WGPUTextureUsage_RenderAttachment;
    desc.dimension     = WGPUTextureDimension_2D;
    desc.size.width    = uint32_t(w);
    desc.size.height   = uint32_t(h);
    desc.size.depthOrArrayLayers = 1;
    desc.format        = WGPUTextureFormat_Depth32Float;
    desc.mipLevelCount = 1;
    desc.sampleCount   = 1;
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

void WgpuViewportWindow::releaseDepthTexture() {
    if (depth_view_)    { wgpuTextureViewRelease(depth_view_); depth_view_ = nullptr; }
    if (depth_texture_) { wgpuTextureRelease(depth_texture_);  depth_texture_ = nullptr; }
    depth_w_ = depth_h_ = 0;
}

// -----------------------------------------------------------------------------
// Camera + frame uniforms
// -----------------------------------------------------------------------------
//
// Orbit camera around `camera_target_`. World +Z up (BIM convention). Yaw is
// rotation about Z (positive = anticlockwise looking down +Z); pitch is
// elevation above the XY plane.

static QVector3D orbitEye(const float target[3], float dist,
                          float yaw_deg, float pitch_deg) {
    const float yaw = qDegreesToRadians(yaw_deg);
    const float pit = qDegreesToRadians(pitch_deg);
    const float cp = std::cos(pit), sp = std::sin(pit);
    const float cy = std::cos(yaw), sy = std::sin(yaw);
    return QVector3D(target[0] + dist * cp * sy,
                     target[1] - dist * cp * cy,
                     target[2] + dist * sp);
}

void WgpuViewportWindow::updateFrameUniforms() {
    const QVector3D target(camera_target_[0], camera_target_[1], camera_target_[2]);
    const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                   camera_yaw_deg_, camera_pitch_deg_);

    QMatrix4x4 view;
    view.lookAt(eye, target, QVector3D(0.0f, 0.0f, 1.0f));

    const float aspect = (configured_h_ > 0)
                            ? float(configured_w_) / float(configured_h_)
                            : 1.0f;
    QMatrix4x4 proj;
    proj.perspective(camera_fov_y_deg_, aspect, camera_near_, camera_far_);

    // Qt builds a GL-style projection (clip-z in [-1, 1]); WebGPU expects
    // clip-z in [0, 1]. Pre-multiply by a remap matrix that maps [-1,1] → [0,1].
    QMatrix4x4 z_remap;  // identity
    z_remap(2, 2) = 0.5f;
    z_remap(2, 3) = 0.5f;

    const QMatrix4x4 view_proj = z_remap * proj * view;

    FrameUniforms u = {};
    std::memcpy(u.view_proj, view_proj.constData(), 16 * sizeof(float));

    QVector3D L(0.4f, -0.6f, 0.9f); L.normalize();
    QVector3D F(-0.3f,  0.5f, 0.4f); F.normalize();
    u.light_dir[0] = L.x(); u.light_dir[1] = L.y(); u.light_dir[2] = L.z(); u.light_dir[3] = 0;
    u.fill_dir [0] = F.x(); u.fill_dir [1] = F.y(); u.fill_dir [2] = F.z(); u.fill_dir [3] = 0;
    u.sky_color   [0] = 0.85f; u.sky_color   [1] = 0.88f; u.sky_color   [2] = 0.95f;
    u.ground_color[0] = 0.35f; u.ground_color[1] = 0.32f; u.ground_color[2] = 0.30f;

    wgpuQueueWriteBuffer(queue_, frame_uniform_buffer_, 0, &u, sizeof(u));
}

bool WgpuViewportWindow::computeSceneAabb(float mn[3], float mx[3]) const {
    bool any = false;
    for (int i = 0; i < 3; ++i) {
        mn[i] =  std::numeric_limits<float>::infinity();
        mx[i] = -std::numeric_limits<float>::infinity();
    }
    for (const auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& inst : m.instances) {
            for (int i = 0; i < 3; ++i) {
                mn[i] = std::min(mn[i], inst.world_aabb_min[i]);
                mx[i] = std::max(mx[i], inst.world_aabb_max[i]);
            }
            any = true;
        }
    }
    return any;
}

void WgpuViewportWindow::viewAll() {
    float mn[3], mx[3];
    if (!computeSceneAabb(mn, mx)) return;
    camera_target_[0] = 0.5f * (mn[0] + mx[0]);
    camera_target_[1] = 0.5f * (mn[1] + mx[1]);
    camera_target_[2] = 0.5f * (mn[2] + mx[2]);
    const float diag = std::sqrt(
        (mx[0] - mn[0]) * (mx[0] - mn[0]) +
        (mx[1] - mn[1]) * (mx[1] - mn[1]) +
        (mx[2] - mn[2]) * (mx[2] - mn[2]));
    // Pull back enough so the bounding sphere fits at half-FOV.
    const float half_fov = qDegreesToRadians(camera_fov_y_deg_) * 0.5f;
    camera_distance_ = std::max(1.0f, 0.6f * diag / std::tan(half_fov));
    if (isExposed()) requestUpdate();
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

void WgpuViewportWindow::captureNextFrameToPng(const QString& path, bool quit_after) {
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

void WgpuViewportWindow::mousePressEvent(QMouseEvent* event) {
    nav_active_button_ = event->button();
    nav_last_pos_      = event->position().toPoint();
}

void WgpuViewportWindow::mouseReleaseEvent(QMouseEvent* event) {
    if (event->button() == nav_active_button_) {
        nav_active_button_ = Qt::NoButton;
    }
}

void WgpuViewportWindow::mouseMoveEvent(QMouseEvent* event) {
    if (nav_active_button_ == Qt::NoButton) return;

    const QPoint pos = event->position().toPoint();
    const int dx = pos.x() - nav_last_pos_.x();
    const int dy = pos.y() - nav_last_pos_.y();
    nav_last_pos_ = pos;

    if (nav_active_button_ == Qt::LeftButton) {
        // Orbit. 0.4 deg/px feels right for a 1280-wide window.
        camera_yaw_deg_   += float(dx) * -0.4f;
        camera_pitch_deg_ += float(dy) * -0.4f;
        camera_pitch_deg_ = std::clamp(camera_pitch_deg_, -89.9f, 89.9f);
        requestUpdate();
    } else if (nav_active_button_ == Qt::MiddleButton) {
        // Pan in the camera's screen-space plane. World units per pixel
        // tracks the view-frustum width at the pivot's depth so panning
        // feels constant regardless of zoom.
        const QVector3D target(camera_target_[0], camera_target_[1], camera_target_[2]);
        const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                       camera_yaw_deg_, camera_pitch_deg_);
        const QVector3D fwd   = (target - eye).normalized();
        const QVector3D right = QVector3D::crossProduct(fwd, QVector3D(0, 0, 1)).normalized();
        const QVector3D up    = QVector3D::crossProduct(right, fwd).normalized();

        const float half_h_world = camera_distance_
            * std::tan(qDegreesToRadians(camera_fov_y_deg_) * 0.5f);
        const float pan_per_pixel = (height() > 0)
            ? (2.0f * half_h_world / float(height()))
            : 0.0f;

        const QVector3D shift = -right * (float(dx) * pan_per_pixel)
                              +  up    * (float(dy) * pan_per_pixel);
        camera_target_[0] += shift.x();
        camera_target_[1] += shift.y();
        camera_target_[2] += shift.z();
        requestUpdate();
    }
}

void WgpuViewportWindow::wheelEvent(QWheelEvent* event) {
    // 120 = one notch on a typical mouse. Each notch zooms ~12% in/out;
    // sign matches conventional "wheel up = zoom in".
    const float notches = float(event->angleDelta().y()) / 120.0f;
    const float factor  = std::pow(0.9f, notches);
    camera_distance_ = std::max(0.01f, camera_distance_ * factor);
    requestUpdate();
}

void WgpuViewportWindow::shutdown() {
    // Release per-model buffers before the device they were created from.
    for (auto& [mid, m] : models_gpu_) releaseWgpuModelGpuData(m);
    models_gpu_.clear();

    releaseDepthTexture();

    if (frame_bind_group_)     { wgpuBindGroupRelease(frame_bind_group_);         frame_bind_group_ = nullptr; }
    if (frame_uniform_buffer_) { wgpuBufferRelease(frame_uniform_buffer_);        frame_uniform_buffer_ = nullptr; }
    if (main_pipeline_)        { wgpuRenderPipelineRelease(main_pipeline_);       main_pipeline_ = nullptr; }
    if (main_shader_module_)   { wgpuShaderModuleRelease(main_shader_module_);    main_shader_module_ = nullptr; }
    if (pipeline_layout_)      { wgpuPipelineLayoutRelease(pipeline_layout_);     pipeline_layout_ = nullptr; }
    if (model_bgl_)            { wgpuBindGroupLayoutRelease(model_bgl_);          model_bgl_ = nullptr; }
    if (frame_bgl_)            { wgpuBindGroupLayoutRelease(frame_bgl_);          frame_bgl_ = nullptr; }

    if (queue_)    { wgpuQueueRelease(queue_);       queue_    = nullptr; }
    if (device_)   { wgpuDeviceRelease(device_);     device_   = nullptr; }
    if (adapter_)  { wgpuAdapterRelease(adapter_);   adapter_  = nullptr; }
    if (surface_)  { wgpuSurfaceRelease(surface_);   surface_  = nullptr; }
    if (instance_) { wgpuInstanceRelease(instance_); instance_ = nullptr; }
    wgpu_initialized_   = false;
    surface_configured_ = false;
}
