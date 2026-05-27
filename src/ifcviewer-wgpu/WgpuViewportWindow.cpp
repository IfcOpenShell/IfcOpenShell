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
#include <atomic>
#include <cmath>
#include <cstring>
#include <future>
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
    for (auto& c : m.chunks) {
        if (c.bind_group)           { wgpuBindGroupRelease(c.bind_group);          c.bind_group = nullptr; }
        if (c.vertex_storage)       { wgpuBufferRelease(c.vertex_storage);         c.vertex_storage = nullptr; }
        if (c.visible_draws_buffer) { wgpuBufferRelease(c.visible_draws_buffer);   c.visible_draws_buffer = nullptr; }
        if (c.prefix_sums_buffer)   { wgpuBufferRelease(c.prefix_sums_buffer);     c.prefix_sums_buffer = nullptr; }
        if (c.per_chunk_uniform)    { wgpuBufferRelease(c.per_chunk_uniform);      c.per_chunk_uniform = nullptr; }
    }
    m.chunks.clear();
    m.mesh_chunk_idx.clear();
    m.mesh_chunk_local_base_vertex.clear();
    if (m.index_buffer)         { wgpuBufferRelease(m.index_buffer);          m.index_buffer = nullptr; }
    if (m.mesh_storage)         { wgpuBufferRelease(m.mesh_storage);          m.mesh_storage = nullptr; }
    if (m.instance_storage)     { wgpuBufferRelease(m.instance_storage);      m.instance_storage = nullptr; }
    m.vertex_bytes   = 0;
    m.index_count    = 0;
    m.mesh_count     = 0;
    m.instance_count = 0;
    m.meshes.clear();
    m.instances.clear();
}

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

struct VisibleDraw {
    mesh_id:        u32,
    instance_idx:   u32,
    ebo_first_u32:  u32,
    base_vertex:    u32,
};

struct PerModel {
    draw_count:           u32,
    total_vertex_count:   u32,
    _pad0:                u32,
    _pad1:                u32,
};

@group(0) @binding(0) var<uniform> u_frame: FrameUniforms;
// Selection flags indexed by object_id. bit 0 = in selection, bit 1 = active.
// Sized to next_object_id_ on the CPU side; out-of-range reads can't happen
// because we cap the index by arrayLength before fetching.
@group(0) @binding(1) var<storage, read> sel_flags: array<u32>;

@group(1) @binding(0) var<storage, read> vertices:      array<u32>;
@group(1) @binding(1) var<storage, read> meshes:        array<MeshQuant>;
@group(1) @binding(2) var<storage, read> instances:     array<InstanceRecord>;
@group(1) @binding(3) var<storage, read> indices:       array<u32>;
@group(1) @binding(4) var<storage, read> visible_draws: array<VisibleDraw>;
@group(1) @binding(5) var<storage, read> prefix_sums:   array<u32>;
@group(1) @binding(6) var<uniform>       u_model:       PerModel;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) normal:    vec3<f32>,
    @location(1) color:     vec4<f32>,
    @location(2) world_pos: vec3<f32>,
    @location(3) @interpolate(flat) object_id: u32,
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

// Binary search for the largest i in [0, draw_count) with prefix_sums[i] <= vid.
// prefix_sums is monotonic non-decreasing and contains draw_count+1 entries
// (prefix_sums[draw_count] == total_vertex_count).
fn find_draw(vid: u32) -> u32 {
    var lo: u32 = 0u;
    var hi: u32 = u_model.draw_count;
    while (lo + 1u < hi) {
        let mid = (lo + hi) >> 1u;
        if (prefix_sums[mid] <= vid) {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    return lo;
}

@vertex
fn vs_main(@builtin(vertex_index) vid: u32) -> VsOut {
    // Saturate past the end (shouldn't happen given draw() count, but safe).
    if (vid >= u_model.total_vertex_count) {
        var degen: VsOut;
        degen.clip_pos = vec4<f32>(0.0, 0.0, 0.0, 0.0);
        return degen;
    }

    let draw_idx = find_draw(vid);
    let local_v  = vid - prefix_sums[draw_idx];
    let item     = visible_draws[draw_idx];

    // Fetch the mesh-local index then the global vertex index.
    let mesh_local_index = indices[item.ebo_first_u32 + local_v];
    let v_global         = item.base_vertex + mesh_local_index;

    let inst = instances[item.instance_idx];
    let mq   = meshes[item.mesh_id];

    let w0 = vertices[v_global * 3u + 0u];
    let w1 = vertices[v_global * 3u + 1u];
    let w2 = vertices[v_global * 3u + 2u];

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
    out.object_id = inst.object_id;
    return out;
}

// sRGB decode — used to undo wgpu's automatic linear→sRGB write encoding
// on swap-chain BGRA8Unorm so the final bytes match what the GL backend
// writes directly. The GL pipeline outputs to a non-sRGB FB and treats
// every colour input as already-linear, so its bytes are exactly its
// shader outputs. wgpu on the same swap chain auto-encodes, which makes
// everything appear ~3× brighter unless we pre-decode once.
fn srgbToLinear(s: vec3<f32>) -> vec3<f32> {
    let lo = s / 12.92;
    let hi = pow((s + 0.055) / 1.055, vec3<f32>(2.4));
    return select(hi, lo, s <= vec3<f32>(0.04045));
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

    var color = in.color.xyz * (ambient + (key + fill) * 0.7);

    // Cavity shading: where adjacent fragments have a sharp normal change
    // (concave creases, edges where two faces meet), darken slightly so
    // shape boundaries read on flat-colour models. Matches the GL shader.
    let cavity = clamp(length(fwidth(n)) * 1.5, 0.0, 0.35);
    color = color * (1.0 - cavity);

    // Selection tint. bit 0 = in selection (cool blue mix), bit 1 = active
    // (slightly stronger blue mix). Matches the GL main shader.
    if (in.object_id < arrayLength(&sel_flags)) {
        let flags = sel_flags[in.object_id];
        if ((flags & 1u) != 0u) { color = mix(color, vec3<f32>(0.2, 0.6, 1.0), 0.45); }
        if ((flags & 2u) != 0u) { color = mix(color, vec3<f32>(0.4, 0.8, 1.0), 0.40); }
    }

    // Cancel the swap chain's implicit linear→sRGB encoding so the final
    // bytes match the GL backend (see srgbToLinear above).
    return vec4<f32>(srgbToLinear(color), in.color.a);
}

// --------------------------- Pick pipeline ---------------------------------
// Same vertex pulling as vs_main, but VsOutPick carries only the object_id
// (flat-interpolated). Fragment writes the object_id to an R32UInt target.
// Background (no draw) reads 0 because the pick attachment is cleared to 0.

struct VsOutPick {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) @interpolate(flat) object_id: u32,
};

@vertex
fn vs_pick(@builtin(vertex_index) vid: u32) -> VsOutPick {
    var out: VsOutPick;
    if (vid >= u_model.total_vertex_count) {
        out.clip_pos  = vec4<f32>(0.0, 0.0, 0.0, 0.0);
        out.object_id = 0u;
        return out;
    }

    let draw_idx = find_draw(vid);
    let local_v  = vid - prefix_sums[draw_idx];
    let item     = visible_draws[draw_idx];
    let mesh_local_index = indices[item.ebo_first_u32 + local_v];
    let v_global = item.base_vertex + mesh_local_index;
    let inst = instances[item.instance_idx];
    let mq   = meshes[item.mesh_id];

    let w0 = vertices[v_global * 3u + 0u];
    let w1 = vertices[v_global * 3u + 1u];
    let pos_norm = vec3<f32>(
        f32(w0 & 0xFFFFu)          / 65535.0,
        f32((w0 >> 16u) & 0xFFFFu) / 65535.0,
        f32(w1 & 0xFFFFu)          / 65535.0,
    );
    let pos_local = mix(mq.aabb_min.xyz, mq.aabb_max.xyz, pos_norm);
    let world4    = inst.transform * vec4<f32>(pos_local, 1.0);

    out.clip_pos  = u_frame.view_proj * world4;
    out.object_id = inst.object_id;
    return out;
}

@fragment
fn fs_pick(in: VsOutPick) -> @location(0) u32 {
    return in.object_id;
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

    // ---- Vertex chunking: split data.vertices into ≤128 MB chunks --------
    // Each mesh's vertex range stays in exactly one chunk. We walk meshes in
    // their existing order, accumulating into the current chunk until adding
    // another mesh would overflow the limit; then start a new chunk.
    //
    // After this, mesh_chunk_idx[mi] tells which chunk mesh mi lives in,
    // and mesh_chunk_local_base_vertex[mi] is the chunk-LOCAL vertex offset
    // for that mesh (in vertex units, divide bytes by 12). The shader's
    // vertex_storage binding will be the chunk's vertex_storage so the
    // chunk-local base_vertex indexes correctly.
    m.mesh_chunk_idx.assign(data.meshes.size(), 0);
    m.mesh_chunk_local_base_vertex.assign(data.meshes.size(), 0);

    struct ChunkPlan {
        size_t   source_byte_offset = 0;  // where in data.vertices this chunk's slice starts
        size_t   byte_count         = 0;  // bytes in this chunk
        uint32_t vertex_count       = 0;  // vertex_count = byte_count / 12
    };
    std::vector<ChunkPlan> chunk_plans;
    size_t   current_chunk_bytes  = 0;
    uint32_t current_chunk_idx    = 0;
    size_t   current_chunk_start  = 0;  // byte offset in data.vertices for current chunk's start

    chunk_plans.push_back({});  // chunk 0
    for (uint32_t mi = 0; mi < data.meshes.size(); ++mi) {
        const MeshInfo& mesh = data.meshes[mi];
        const size_t mesh_vertex_bytes = size_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        if (mesh_vertex_bytes > WGPU_CHUNK_VERTEX_BYTES_LIMIT) {
            qWarning().noquote().nospace()
                << "Mesh #" << mi << " has " << mesh_vertex_bytes
                << " B of vertex data — exceeds chunk limit "
                << WGPU_CHUNK_VERTEX_BYTES_LIMIT
                << " B. Mesh-splitting is not implemented; this mesh will be"
                   " in an oversize chunk that won't fit a web browser.";
        }

        // Sanity: mesh.vbo_byte_offset is the GLOBAL byte offset in
        // data.vertices. We use it for chunk bookkeeping; if a sidecar's
        // meshes aren't sorted by vbo_byte_offset things go subtly wrong,
        // but every baker produces them ascending.
        if (current_chunk_bytes > 0
            && current_chunk_bytes + mesh_vertex_bytes > WGPU_CHUNK_VERTEX_BYTES_LIMIT) {
            // Finalise current chunk, start a new one.
            ChunkPlan& done = chunk_plans[current_chunk_idx];
            done.source_byte_offset = current_chunk_start;
            done.byte_count         = current_chunk_bytes;
            done.vertex_count       = uint32_t(current_chunk_bytes / INSTANCED_VERTEX_STRIDE_BYTES);
            ++current_chunk_idx;
            chunk_plans.push_back({});
            current_chunk_bytes = 0;
            current_chunk_start = mesh.vbo_byte_offset;
        } else if (current_chunk_bytes == 0) {
            current_chunk_start = mesh.vbo_byte_offset;
        }

        m.mesh_chunk_idx[mi]             = current_chunk_idx;
        m.mesh_chunk_local_base_vertex[mi]
            = uint32_t(current_chunk_bytes / INSTANCED_VERTEX_STRIDE_BYTES);
        current_chunk_bytes += mesh_vertex_bytes;
    }
    // Finalise the last (possibly first) chunk.
    {
        ChunkPlan& done = chunk_plans[current_chunk_idx];
        done.source_byte_offset = current_chunk_start;
        done.byte_count         = current_chunk_bytes;
        done.vertex_count       = uint32_t(current_chunk_bytes / INSTANCED_VERTEX_STRIDE_BYTES);
    }
    // Drop trailing empty chunk (e.g. on a no-mesh model).
    if (chunk_plans.back().byte_count == 0) chunk_plans.pop_back();

    // ---- Allocate per-chunk buffers + upload vertex slices --------------
    m.chunks.resize(chunk_plans.size());
    for (size_t ci = 0; ci < chunk_plans.size(); ++ci) {
        const ChunkPlan& plan = chunk_plans[ci];
        WgpuModelGpuData::Chunk& c = m.chunks[ci];
        c.vertex_count = plan.vertex_count;

        const char* vs_label = (ci == 0) ? "model.chunk0.vertex_storage"
                                         : "model.chunkN.vertex_storage";
        c.vertex_storage = createBufferWithData(
            device_, queue_,
            data.vertices.data() + plan.source_byte_offset,
            plan.byte_count,
            WGPUBufferUsage_Storage,
            vs_label);
    }

    // Index buffer — single, shared across chunks. Mesh-local u32 indices.
    // Bound as storage in the vertex shader for manual fetch.
    m.index_buffer = createBufferWithData(
        device_, queue_,
        data.indices.data(), data.indices.size() * sizeof(uint32_t),
        WGPUBufferUsage_Storage | WGPUBufferUsage_Index,
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

    // Derive InstanceGpu[] from InstanceCpu[]. Rebase each instance's
    // object_id by next_object_id_ so picks are globally unambiguous
    // across multiple loaded sidecars (each sidecar's local IDs start
    // from 1 and would otherwise collide).
    const uint32_t object_id_base = next_object_id_;
    uint32_t max_local_id = 0;
    std::vector<InstanceGpu> inst_gpu;
    inst_gpu.reserve(data.instances.size());
    for (auto& ic : data.instances) {
        if (ic.object_id > max_local_id) max_local_id = ic.object_id;
        // Rebase in the CPU mirror too so future cull / picks see the
        // global id consistently.
        ic.object_id = object_id_base + ic.object_id;
        InstanceGpu ig = {};
        std::memcpy(ig.transform, ic.transform, sizeof(ig.transform));
        ig.object_id            = ic.object_id;
        ig.color_override_rgba8 = ic.color_override_rgba8;
        ig.mesh_id              = ic.mesh_id;
        inst_gpu.push_back(ig);
    }
    next_object_id_ = object_id_base + max_local_id + 1;
    m.instance_storage = createBufferWithData(
        device_, queue_,
        inst_gpu.data(), inst_gpu.size() * sizeof(InstanceGpu),
        WGPUBufferUsage_Storage,
        "model.instance_storage");

    // Per-chunk buffers for cross-mesh vertex pulling. Pre-sized to the
    // worst case (every visible instance ends up in this one chunk) so
    // wgpuQueueWriteBuffer never has to recreate them mid-frame and the
    // bind group reference stays valid for the model's lifetime.
    //
    // VisibleDraw capacity: up to one entry per (instance × 2 LODs). LOD1
    // only fills when bake produced one, but headroom is cheap (~3 MB
    // worst-case per chunk for a 100k-instance model).
    const size_t draw_cap_per_chunk = std::max<size_t>(size_t(data.instances.size()) * 2u, 1u);
    const size_t draws_bytes_per_chunk = draw_cap_per_chunk * sizeof(WgpuModelGpuData::VisibleDrawGpu);
    const size_t ps_cap_per_chunk = draw_cap_per_chunk + 1;
    for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
        WgpuModelGpuData::Chunk& c = m.chunks[ci];

        WGPUBufferDescriptor vd_desc = {};
        vd_desc.size  = std::max<uint64_t>(draws_bytes_per_chunk, 16);
        vd_desc.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        vd_desc.label = svFromCStr("model.chunk.visible_draws");
        c.visible_draws_buffer   = wgpuDeviceCreateBuffer(device_, &vd_desc);
        c.visible_draws_capacity = draw_cap_per_chunk;

        WGPUBufferDescriptor ps_desc = {};
        ps_desc.size  = std::max<uint64_t>(ps_cap_per_chunk * sizeof(uint32_t), 16);
        ps_desc.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        ps_desc.label = svFromCStr("model.chunk.prefix_sums");
        c.prefix_sums_buffer   = wgpuDeviceCreateBuffer(device_, &ps_desc);
        c.prefix_sums_capacity = ps_cap_per_chunk;

        WGPUBufferDescriptor mu_desc = {};
        mu_desc.size  = 16;
        mu_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        mu_desc.label = svFromCStr("model.chunk.uniform");
        c.per_chunk_uniform = wgpuDeviceCreateBuffer(device_, &mu_desc);

        c.visible_draws_scratch.reserve(draw_cap_per_chunk);
        c.prefix_sums_scratch.reserve(ps_cap_per_chunk);
    }

    // Hand off CPU mirrors (cull / picking will need them later).
    m.meshes    = std::move(data.meshes);
    m.instances = std::move(data.instances);

    auto [inserted, _] = models_gpu_.emplace(model_id, std::move(m));
    WgpuModelGpuData& mref = inserted->second;
    buildModelBindGroup(mref);

    qInfo().noquote().nospace()
        << "[wgpu] applyCachedModel mid=" << model_id
        << " verts=" << mref.vertex_bytes << "B"
        << " idx="   << mref.index_count
        << " meshes=" << mref.mesh_count
        << " instances=" << mref.instance_count
        << " chunks=" << mref.chunks.size();

    if (!initial_view_applied_) {
        viewAll();
        initial_view_applied_ = true;
    }
    // Grow selection_flags_ to cover the new id range.
    ensureSelectionFlagsBuffer();
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

    // Pick the limits to request on the device. Default = the adapter's
    // actual maximum so large native scenes get all the headroom the GPU
    // can give. --web-limits forces the WebGPU spec mandatory floor
    // (128 MB max storage binding, 256 MB max buffer) so we can verify on
    // desktop that the renderer's chunking actually fits through browser
    // constraints — turns "trust me, web will work" into a hard test.
    WGPULimits adapter_limits = {};
    wgpuAdapterGetLimits(adapter_, &adapter_limits);

    WGPULimits web_floor_limits = adapter_limits;
    // Override just the two that BIM scenes typically blow past. Everything
    // else stays at adapter max (no point making the device weaker than it
    // could be on facets we know browsers grant generously, e.g. workgroup
    // sizes — those are texture / compute limits and we don't hit them).
    web_floor_limits.maxStorageBufferBindingSize = 128ull * 1024 * 1024;
    web_floor_limits.maxBufferSize               = 256ull * 1024 * 1024;

    WGPUDeviceDescriptor dev_desc = {};
    dev_desc.requiredLimits = web_limits_ ? &web_floor_limits : &adapter_limits;
    if (web_limits_) {
        qInfo() << "wgpu --web-limits: requesting browser-floor limits"
                << "(maxStorageBufferBindingSize=128MB, maxBufferSize=256MB)";
    }
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
    if (!buildHizPipeline()) return false;
    if (!buildEdgePipeline()) return false;
    if (!buildPickPipeline()) return false;

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

bool WgpuViewportWindow::buildEdgePipeline() {
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
        qWarning() << "wgpu edge pipeline creation failed";
        return false;
    }
    return true;
}

void WgpuViewportWindow::encodeEdgePass(WGPUCommandEncoder enc,
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

void WgpuViewportWindow::releaseEdgeResources() {
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

bool WgpuViewportWindow::buildPickPipeline() {
    WGPUColorTargetState color_target = {};
    color_target.format    = WGPUTextureFormat_R32Uint;
    color_target.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = main_shader_module_;
    frag.entryPoint  = svFromCStr("fs_pick");
    frag.targetCount = 1;
    frag.targets     = &color_target;

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
        qWarning() << "wgpu pick pipeline creation failed";
        return false;
    }
    return true;
}

void WgpuViewportWindow::ensurePickAttachments(int w, int h) {
    if (w <= 0 || h <= 0) return;
    if (w == pick_w_ && h == pick_h_ && pick_color_view_) return;

    if (pick_color_view_)    { wgpuTextureViewRelease(pick_color_view_); pick_color_view_ = nullptr; }
    if (pick_color_texture_) { wgpuTextureRelease(pick_color_texture_);  pick_color_texture_ = nullptr; }
    if (pick_depth_view_)    { wgpuTextureViewRelease(pick_depth_view_); pick_depth_view_ = nullptr; }
    if (pick_depth_texture_) { wgpuTextureRelease(pick_depth_texture_);  pick_depth_texture_ = nullptr; }

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

    pick_w_ = w;
    pick_h_ = h;
}

void WgpuViewportWindow::releasePickResources() {
    if (pick_color_view_)    { wgpuTextureViewRelease(pick_color_view_); pick_color_view_ = nullptr; }
    if (pick_color_texture_) { wgpuTextureRelease(pick_color_texture_);  pick_color_texture_ = nullptr; }
    if (pick_depth_view_)    { wgpuTextureViewRelease(pick_depth_view_); pick_depth_view_ = nullptr; }
    if (pick_depth_texture_) { wgpuTextureRelease(pick_depth_texture_);  pick_depth_texture_ = nullptr; }
    if (pick_staging_buffer_){ wgpuBufferRelease(pick_staging_buffer_);  pick_staging_buffer_ = nullptr; }
    if (pick_pipeline_)      { wgpuRenderPipelineRelease(pick_pipeline_); pick_pipeline_ = nullptr; }
    pick_w_ = pick_h_ = 0;
}

uint32_t WgpuViewportWindow::pickObjectAt(int x_pixels, int y_pixels) {
    if (!pick_pipeline_ || !device_ || !queue_ || models_gpu_.empty()) return 0;
    if (configured_w_ <= 0 || configured_h_ <= 0) return 0;
    if (x_pixels < 0 || y_pixels < 0 ||
        x_pixels >= configured_w_ || y_pixels >= configured_h_) return 0;

    ensurePickAttachments(configured_w_, configured_h_);
    if (!pick_color_view_ || !pick_depth_view_ || !pick_staging_buffer_) return 0;

    // The current frame's visible_draws are already on the GPU (uploaded
    // by the last render's cullModelCpuUpload), and the per-model bind
    // groups + frame uniform are valid. Just encode a one-shot pick pass.

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    WGPURenderPassColorAttachment color = {};
    color.view       = pick_color_view_;
    color.loadOp     = WGPULoadOp_Clear;
    color.storeOp    = WGPUStoreOp_Store;
    color.clearValue = { 0.0, 0.0, 0.0, 0.0 };  // object_id == 0 means miss
    color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDepthStencilAttachment depth = {};
    depth.view              = pick_depth_view_;
    depth.depthLoadOp       = WGPULoadOp_Clear;
    depth.depthStoreOp      = WGPUStoreOp_Store;
    depth.depthClearValue   = 1.0f;
    depth.stencilLoadOp     = WGPULoadOp_Undefined;
    depth.stencilStoreOp    = WGPUStoreOp_Undefined;
    depth.stencilReadOnly   = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 1;
    pass_desc.colorAttachments       = &color;
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

    return object_id;
}

bool WgpuViewportWindow::buildHizPipeline() {
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
        qWarning() << "wgpu hiz pipeline creation failed";
        return false;
    }

    WGPUBufferDescriptor ub_desc = {};
    ub_desc.size  = 16;
    ub_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    ub_desc.label = svFromCStr("ifcviewer-wgpu.hiz_uniform");
    hiz_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &ub_desc);

    return true;
}

void WgpuViewportWindow::ensureHizTextures(int viewport_w, int viewport_h) {
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

void WgpuViewportWindow::releaseHizResources() {
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

int WgpuViewportWindow::encodeHizResolve(WGPUCommandEncoder enc) {
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

void WgpuViewportWindow::startHizMap(int slot, const QMatrix4x4& vp_used) {
    if (slot < 0 || slot >= HIZ_SLOTS) return;
    if (!hiz_staging_buffers_[slot] || hiz_resolve_w_ == 0) return;

    hiz_slot_vp_[slot]   = vp_used;
    hiz_slot_state_[slot] = HizSlotState::Mapping;

    struct MapCtx { WgpuViewportWindow* self; int slot; };
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

void WgpuViewportWindow::drainHizReadbacks() {
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
                w = std::max(1u, w / 2u);
                h = std::max(1u, h / 2u);
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

bool WgpuViewportWindow::aabbOccludedByHiz(const float mn[3], const float mx[3]) const {
    if (!hiz_valid_ || hiz_mip_offset_.empty()) return false;

    // Project the 8 corners of the AABB. Track:
    //   - min/max NDC x,y (screen-space bounds)
    //   - min projected z (nearest point of the AABB to the camera)
    //   - whether any corner has clip.w <= 0 (AABB straddles near plane)
    const float* m = hiz_vp_.constData();  // column-major
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
    // NDC y is +up; texture y is +down (matches our resolve shader's
    // y-flip via clip_pos.y = -y).
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
    const int lx0 = std::max(0, int(x0) >> level);
    const int ly0 = std::max(0, int(y0) >> level);
    const int lx1 = std::min(int(lw) - 1, int(x1) >> level);
    const int ly1 = std::min(int(lh) - 1, int(y1) >> level);

    const float* level_data = &hiz_pyramid_[hiz_mip_offset_[level]];
    float max_d = 0.0f;
    for (int y = ly0; y <= ly1; ++y) {
        for (int x = lx0; x <= lx1; ++x) {
            max_d = std::max(max_d, level_data[y * int(lw) + x]);
        }
    }

    // AABB occluded iff its nearest projected z is BEHIND the depth pyramid's
    // coverage (greater in WebGPU's [0,1] z, where 0 is near, 1 is far).
    return min_z > max_d;
}

void WgpuViewportWindow::setBenchmarkFrames(int frames) {
    bench_total_    = std::max(0, frames);
    bench_count_    = 0;
    bench_yaw_start_ = camera_yaw_deg_;
    bench_frame_ms_.clear();
    bench_frame_ms_.reserve(size_t(bench_total_));
    if (isExposed() && bench_total_ > 0) requestUpdate();
}

uint32_t WgpuViewportWindow::cullModelCpuCompute(WgpuModelGpuData& m,
                                                 const float planes[6][4],
                                                 const float eye[3], const float forward[3],
                                                 float focal_px,
                                                 float min_radius_px,
                                                 float lod1_threshold_px,
                                                 bool  hiz_enabled) const {
    uint32_t hiz_rejects = 0;

    if (m.instances.empty() || m.meshes.empty() || m.chunks.empty()) {
        return 0;
    }

    const bool contrib_enabled = (min_radius_px      > 0.0f);
    const bool lod_enabled     = (lod1_threshold_px  > 0.0f);

    // Reset per-chunk scratch + counters at the start of each cull.
    for (auto& c : m.chunks) {
        c.visible_draws_scratch.clear();
        c.prefix_sums_scratch.clear();
        c.prefix_sums_scratch.push_back(0);
        c.total_visible_vertices = 0;
        c.total_visible_draws    = 0;
    }

    // Per-chunk running vertex count (used to populate that chunk's prefix
    // sums incrementally). Kept on the stack to avoid heap churn for small
    // chunk counts.
    std::vector<uint32_t> running_vertex_count(m.chunks.size(), 0);

    for (uint32_t i = 0; i < uint32_t(m.instances.size()); ++i) {
        const auto& inst = m.instances[i];
        if (inst.mesh_id >= m.meshes.size()) continue;
        // Cheapest possible cull first: explicit user-hidden flag. Skips
        // every downstream cost (frustum / HiZ / draw / pick).
        if (visibility_.isHidden(inst.object_id)) continue;
        if (!aabbInFrustum(inst.world_aabb_min, inst.world_aabb_max, planes)) continue;

        const MeshInfo& mesh = m.meshes[inst.mesh_id];

        // Projected bounding-sphere radius in pixels — shared between the
        // contribution-cull and LOD-pick decisions. Computed before HiZ so
        // contribution can short-circuit the per-instance HiZ projection
        // (which is the bulk of cull cost on dense scenes).
        float projected_px = std::numeric_limits<float>::infinity();
        if (contrib_enabled || (lod_enabled && mesh.lod1_index_count > 0)) {
            const float cx = 0.5f * (inst.world_aabb_min[0] + inst.world_aabb_max[0]);
            const float cy = 0.5f * (inst.world_aabb_min[1] + inst.world_aabb_max[1]);
            const float cz = 0.5f * (inst.world_aabb_min[2] + inst.world_aabb_max[2]);
            const float ex = inst.world_aabb_max[0] - inst.world_aabb_min[0];
            const float ey = inst.world_aabb_max[1] - inst.world_aabb_min[1];
            const float ez = inst.world_aabb_max[2] - inst.world_aabb_min[2];
            const float radius_world = 0.5f * std::sqrt(ex*ex + ey*ey + ez*ez);
            const float view_z = forward[0] * (cx - eye[0])
                               + forward[1] * (cy - eye[1])
                               + forward[2] * (cz - eye[2]);
            if (view_z > 1e-3f) {
                projected_px = radius_world * focal_px / view_z;
            }
        }

        // Contribution cull before HiZ: HiZ is by far the most expensive
        // per-instance test (8-corner projection + mip pyramid sample), so
        // letting cheap contribution drops happen first cuts the HiZ-tested
        // population by ~5× on real scenes.
        if (contrib_enabled && projected_px < min_radius_px) continue;

        if (hiz_enabled
            && aabbOccludedByHiz(inst.world_aabb_min, inst.world_aabb_max)) {
            ++hiz_rejects;
            continue;
        }

        const bool use_lod1 = lod_enabled
                            && mesh.lod1_index_count > 0
                            && projected_px < lod1_threshold_px;

        // Emit one VisibleDraw entry into the chunk that owns this mesh's
        // vertex range. base_vertex is CHUNK-LOCAL; the chunk's bind group
        // points at its own vertex_storage so the shader indexes correctly.
        const uint32_t chunk_idx = m.mesh_chunk_idx[inst.mesh_id];
        WgpuModelGpuData::Chunk& c = m.chunks[chunk_idx];

        WgpuModelGpuData::VisibleDrawGpu d;
        d.mesh_id       = inst.mesh_id;
        d.instance_idx  = i;
        d.ebo_first_u32 = (use_lod1 ? mesh.lod1_ebo_byte_offset : mesh.ebo_byte_offset)
                          / uint32_t(sizeof(uint32_t));
        d.base_vertex   = m.mesh_chunk_local_base_vertex[inst.mesh_id];
        c.visible_draws_scratch.push_back(d);

        const uint32_t entry_vert_count = use_lod1 ? mesh.lod1_index_count
                                                    : mesh.index_count;
        running_vertex_count[chunk_idx] += entry_vert_count;
        c.prefix_sums_scratch.push_back(running_vertex_count[chunk_idx]);
    }

    for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
        auto& c = m.chunks[ci];
        c.total_visible_draws    = uint32_t(c.visible_draws_scratch.size());
        c.total_visible_vertices = running_vertex_count[ci];
    }
    return hiz_rejects;
}

void WgpuViewportWindow::cullModelCpuUpload(WgpuModelGpuData& m) {
    for (auto& c : m.chunks) {
        if (!c.visible_draws_buffer || !c.prefix_sums_buffer || !c.per_chunk_uniform) continue;

        if (c.total_visible_draws == 0) {
            // Render() will skip this chunk; still zero the uniform so any
            // accidental dispatch sees 0 work.
            const uint32_t um[4] = { 0, 0, 0, 0 };
            wgpuQueueWriteBuffer(queue_, c.per_chunk_uniform, 0, um, sizeof(um));
            continue;
        }

        wgpuQueueWriteBuffer(queue_, c.visible_draws_buffer, 0,
                             c.visible_draws_scratch.data(),
                             c.visible_draws_scratch.size()
                                 * sizeof(WgpuModelGpuData::VisibleDrawGpu));
        wgpuQueueWriteBuffer(queue_, c.prefix_sums_buffer, 0,
                             c.prefix_sums_scratch.data(),
                             c.prefix_sums_scratch.size() * sizeof(uint32_t));

        const uint32_t um[4] = {
            c.total_visible_draws,
            c.total_visible_vertices,
            0, 0,
        };
        wgpuQueueWriteBuffer(queue_, c.per_chunk_uniform, 0, um, sizeof(um));
    }
}

void WgpuViewportWindow::render() {
    // Time the whole render() body (cull + encode + present) for the
    // benchmark stats. Started before any wgpu work so cull is included.
    QElapsedTimer frame_timer;
    if (bench_total_ > 0) frame_timer.start();

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
    hiz_reject_count_       = 0;
    QElapsedTimer cull_timer;
    if (bench_total_ > 0) cull_timer.start();
    QMatrix4x4 vp_this_frame;
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
        vp_this_frame = vp;
        float planes[6][4];
        extractFrustumPlanes(vp.constData(), planes);

        // LOD pick inputs: world-space eye, unit forward, vertical focal in
        // pixels. focal_px maps view-space depth to projected radius:
        //   projected_px = world_radius * focal_px / view_z.
        const QVector3D fwd_q = (target - eye).normalized();
        const float eye_a[3] = { eye.x(),  eye.y(),  eye.z()  };
        const float fwd_a[3] = { fwd_q.x(), fwd_q.y(), fwd_q.z() };
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

        // Cull each model on its own worker thread. wgpu queue writes are
        // serialised on the main thread after the parallel compute joins —
        // wgpu-native doesn't guarantee thread-safety on queue ops.
        std::vector<std::pair<uint32_t, std::future<uint32_t>>> futures;
        futures.reserve(models_gpu_.size());
        for (auto& [mid, m] : models_gpu_) {
            if (m.hidden) continue;
            auto& m_ref = m;
            futures.emplace_back(mid, std::async(std::launch::async,
                [this, &m_ref, &planes, &eye_a, &fwd_a,
                 focal_px, effective_min_px]() {
                    return cullModelCpuCompute(
                        m_ref, planes, eye_a, fwd_a, focal_px,
                        effective_min_px, lod1_pixel_threshold_,
                        hiz_enabled_);
                }));
        }
        for (auto& [mid, fut] : futures) {
            hiz_reject_count_ += fut.get();
        }
        for (auto& [mid, m] : models_gpu_) {
            if (m.hidden) continue;
            cullModelCpuUpload(m);
            for (const auto& c : m.chunks) {
                last_visible_objects_   += c.total_visible_draws;
                last_visible_triangles_ += c.total_visible_vertices / 3u;
                // One CPU drawcall per non-empty chunk.
                if (c.total_visible_draws > 0) last_sub_draws_ += 1;
            }
        }
    }

    // Snapshot camera state for next frame's motion detection.
    prev_camera_target_[0] = camera_target_[0];
    prev_camera_target_[1] = camera_target_[1];
    prev_camera_target_[2] = camera_target_[2];
    prev_camera_distance_  = camera_distance_;
    prev_camera_yaw_deg_   = camera_yaw_deg_;
    prev_camera_pitch_deg_ = camera_pitch_deg_;
    has_prev_camera_       = true;
    if (bench_total_ > 0 && bench_count_ >= bench_warmup_) {
        bench_cull_ms_total_ += double(cull_timer.nsecsElapsed()) / 1e6;
    }

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    WGPURenderPassColorAttachment color = {};
    color.view          = msaa_color_view_;  // render into 4× MSAA target
    color.resolveTarget = view;              // resolve to surface texture
    color.loadOp        = WGPULoadOp_Clear;
    color.storeOp       = WGPUStoreOp_Store;
    color.clearValue    = {
        srgbToLinear(background_color_.redF()),
        srgbToLinear(background_color_.greenF()),
        srgbToLinear(background_color_.blueF()),
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
            if (m.hidden) continue;
            // One drawcall per non-empty chunk. Each chunk binds its own
            // vertex_storage + visible_draws + prefix_sums + uniform via
            // its bind_group. The shader is identical across chunks.
            for (const auto& c : m.chunks) {
                if (!c.bind_group || c.total_visible_vertices == 0) continue;
                wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
                wgpuRenderPassEncoderDraw(pass, c.total_visible_vertices, 1, 0, 0);
            }
        }
    }

    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    // ---- Edge silhouette post-process — reads MSAA depth, blends dark
    // lines onto the resolved surface colour. Encoded before HiZ resolve
    // so HiZ uses the same MSAA depth that produced the edges.
    if (edges_enabled_) {
        encodeEdgePass(enc, view);
    }

    // ---- HiZ: resolve MSAA depth → small single-sample → ping-pong slot
    int hiz_submitted_slot = -1;
    if (hiz_enabled_) {
        hiz_submitted_slot = encodeHizResolve(enc);
    }

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
        QElapsedTimer hiz_timer;
        if (bench_total_ > 0) hiz_timer.start();
        startHizMap(hiz_submitted_slot, vp_this_frame);
        if (bench_total_ > 0 && bench_count_ >= bench_warmup_) {
            bench_hiz_readback_ms_total_ += double(hiz_timer.nsecsElapsed()) / 1e6;
        }
    }

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
                << "  hiz_rej " << hiz_reject_count_;
            const double n = double(std::max(1, bench_total_));
            qInfo().noquote().nospace()
                << "  per-frame avg ms: cull=" << bench_cull_ms_total_ / n
                << "  hiz_readback=" << bench_hiz_readback_ms_total_ / n
                << "  hiz=" << (hiz_enabled_ ? "on" : "off");
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
    WGPUBindGroupLayoutEntry frame_entries[2] = {};
    frame_entries[0].binding = 0;
    frame_entries[0].visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
    frame_entries[0].buffer.type = WGPUBufferBindingType_Uniform;
    frame_entries[0].buffer.minBindingSize = sizeof(FrameUniforms);
    frame_entries[1].binding = 1;
    frame_entries[1].visibility = WGPUShaderStage_Fragment;
    frame_entries[1].buffer.type = WGPUBufferBindingType_ReadOnlyStorage;

    WGPUBindGroupLayoutDescriptor frame_bgl_desc = {};
    frame_bgl_desc.entryCount = 2;
    frame_bgl_desc.entries    = frame_entries;
    frame_bgl_desc.label      = svFromCStr("ifcviewer-wgpu.frame_bgl");
    frame_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &frame_bgl_desc);

    // 6 read-only storage buffers (vertices, meshes, instances, indices,
    // visible_draws, prefix_sums) + 1 uniform (per-model count). All read
    // in the vertex shader. WebGPU's mandatory min is 8 storage / 12 uniform
    // per stage, so we're comfortably under the cap.
    WGPUBindGroupLayoutEntry model_entries[7] = {};
    for (int i = 0; i < 6; ++i) {
        model_entries[i].binding     = uint32_t(i);
        model_entries[i].visibility  = WGPUShaderStage_Vertex;
        model_entries[i].buffer.type = WGPUBufferBindingType_ReadOnlyStorage;
    }
    model_entries[6].binding             = 6;
    model_entries[6].visibility          = WGPUShaderStage_Vertex;
    model_entries[6].buffer.type         = WGPUBufferBindingType_Uniform;
    model_entries[6].buffer.minBindingSize = 16;
    WGPUBindGroupLayoutDescriptor model_bgl_desc = {};
    model_bgl_desc.entryCount = 7;
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
    rp_desc.multisample.count = SAMPLE_COUNT;
    rp_desc.multisample.mask  = 0xFFFFFFFFu;

    main_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!main_pipeline_) {
        qWarning() << "wgpu main render pipeline creation failed";
        return false;
    }

    // ---- Per-frame uniform buffer ---------------------------------------
    WGPUBufferDescriptor fb_desc = {};
    fb_desc.size  = sizeof(FrameUniforms);
    fb_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    fb_desc.label = svFromCStr("ifcviewer-wgpu.frame_uniform");
    frame_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &fb_desc);

    // frame_bind_group_ is built lazily once we have a selection_flags_
    // buffer to bind alongside the uniform — ensureSelectionFlagsBuffer
    // handles both the first creation and any subsequent resize.

    return true;
}

void WgpuViewportWindow::ensureSelectionFlagsBuffer() {
    // Round up to at least 64 entries (256 B — minimum useful storage) and
    // grow geometrically when next_object_id_ outruns the current capacity.
    const uint32_t needed = std::max<uint32_t>(next_object_id_, 64);
    if (selection_flags_buffer_ && selection_flags_capacity_ >= needed) {
        if (!frame_bind_group_) {
            // First-time bind group creation after the buffer exists.
            // (Should always be true here.)
        } else {
            return;
        }
    }

    // (Re)allocate. Geometric grow so we don't recreate every frame as a
    // big scene streams in.
    uint32_t new_cap = selection_flags_capacity_;
    if (new_cap < 64) new_cap = 64;
    while (new_cap < needed) new_cap *= 2;

    if (!selection_flags_buffer_ || selection_flags_capacity_ < new_cap) {
        if (selection_flags_buffer_) {
            wgpuBufferRelease(selection_flags_buffer_);
            selection_flags_buffer_ = nullptr;
        }
        WGPUBufferDescriptor sb = {};
        sb.size  = uint64_t(new_cap) * sizeof(uint32_t);
        sb.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        sb.label = svFromCStr("ifcviewer-wgpu.selection_flags");
        selection_flags_buffer_   = wgpuDeviceCreateBuffer(device_, &sb);
        selection_flags_capacity_ = new_cap;
        // Initialise to zero so any unused range reads as "not selected".
        // wgpuQueueWriteBuffer with a small zero block is enough; the rest
        // is created as zero-initialised by wgpu per the spec.
    }

    // Rebuild the frame bind group against the (possibly new) buffer.
    if (frame_bind_group_) {
        wgpuBindGroupRelease(frame_bind_group_);
        frame_bind_group_ = nullptr;
    }
    WGPUBindGroupEntry fbg_entries[2] = {};
    fbg_entries[0].binding = 0;
    fbg_entries[0].buffer  = frame_uniform_buffer_;
    fbg_entries[0].size    = sizeof(FrameUniforms);
    fbg_entries[1].binding = 1;
    fbg_entries[1].buffer  = selection_flags_buffer_;
    fbg_entries[1].size    = WGPU_WHOLE_SIZE;
    WGPUBindGroupDescriptor fbg_desc = {};
    fbg_desc.layout     = frame_bgl_;
    fbg_desc.entryCount = 2;
    fbg_desc.entries    = fbg_entries;
    fbg_desc.label      = svFromCStr("ifcviewer-wgpu.frame_bind_group");
    frame_bind_group_ = wgpuDeviceCreateBindGroup(device_, &fbg_desc);

    // Force a re-upload of the flags into the (possibly new) buffer.
    selection_flags_scratch_.assign(selection_flags_capacity_, 0);
    selection_.fillFlagsArray(selection_flags_scratch_, selection_flags_capacity_);
    wgpuQueueWriteBuffer(queue_, selection_flags_buffer_, 0,
                         selection_flags_scratch_.data(),
                         selection_flags_scratch_.size() * sizeof(uint32_t));
    selection_.markClean();
}

void WgpuViewportWindow::uploadSelectionFlagsIfDirty() {
    if (!selection_.dirty() || !selection_flags_buffer_) return;
    selection_flags_scratch_.assign(selection_flags_capacity_, 0);
    selection_.fillFlagsArray(selection_flags_scratch_, selection_flags_capacity_);
    wgpuQueueWriteBuffer(queue_, selection_flags_buffer_, 0,
                         selection_flags_scratch_.data(),
                         selection_flags_scratch_.size() * sizeof(uint32_t));
    selection_.markClean();
}

void WgpuViewportWindow::buildModelBindGroup(WgpuModelGpuData& m) {
    if (!m.mesh_storage || !m.instance_storage || !m.index_buffer) {
        // Empty model — no chunks, no bind groups; the draw loop will skip.
        return;
    }

    // One bind group per chunk: chunk's vertex_storage, visible_draws,
    // prefix_sums, per_chunk_uniform — plus the shared mesh / instance /
    // index buffers.
    for (auto& c : m.chunks) {
        if (c.bind_group) {
            wgpuBindGroupRelease(c.bind_group);
            c.bind_group = nullptr;
        }
        if (!c.vertex_storage || !c.visible_draws_buffer
            || !c.prefix_sums_buffer || !c.per_chunk_uniform) continue;

        WGPUBindGroupEntry entries[7] = {};
        entries[0].binding = 0;
        entries[0].buffer  = c.vertex_storage;
        entries[0].size    = WGPU_WHOLE_SIZE;
        entries[1].binding = 1;
        entries[1].buffer  = m.mesh_storage;
        entries[1].size    = WGPU_WHOLE_SIZE;
        entries[2].binding = 2;
        entries[2].buffer  = m.instance_storage;
        entries[2].size    = WGPU_WHOLE_SIZE;
        entries[3].binding = 3;
        entries[3].buffer  = m.index_buffer;
        entries[3].size    = WGPU_WHOLE_SIZE;
        entries[4].binding = 4;
        entries[4].buffer  = c.visible_draws_buffer;
        entries[4].size    = WGPU_WHOLE_SIZE;
        entries[5].binding = 5;
        entries[5].buffer  = c.prefix_sums_buffer;
        entries[5].size    = WGPU_WHOLE_SIZE;
        entries[6].binding = 6;
        entries[6].buffer  = c.per_chunk_uniform;
        entries[6].size    = 16;

        WGPUBindGroupDescriptor desc = {};
        desc.layout     = model_bgl_;
        desc.entryCount = 7;
        desc.entries    = entries;
        desc.label      = svFromCStr("ifcviewer-wgpu.chunk_bind_group");
        c.bind_group = wgpuDeviceCreateBindGroup(device_, &desc);
    }
}

// -----------------------------------------------------------------------------
// Depth attachment
// -----------------------------------------------------------------------------

void WgpuViewportWindow::ensureDepthTexture(int w, int h) {
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

void WgpuViewportWindow::releaseDepthTexture() {
    if (depth_view_)    { wgpuTextureViewRelease(depth_view_); depth_view_ = nullptr; }
    if (depth_texture_) { wgpuTextureRelease(depth_texture_);  depth_texture_ = nullptr; }
    depth_w_ = depth_h_ = 0;
}

void WgpuViewportWindow::ensureMsaaColorTexture(int w, int h) {
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

void WgpuViewportWindow::releaseMsaaColorTexture() {
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

static QVector3D orbitEye(const float target[3], float dist,
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
    return QVector3D(target[0] + dist * cp * cy,
                     target[1] + dist * cp * sy,
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

    // Values match the GL viewport's main fragment shader so a side-by-side
    // diff of the two backends only shows what the wgpu pipeline has yet to
    // implement (edge silhouette pass, MSAA polish, etc.) — not lighting
    // model differences. Key + fill are ~unit-length, ~120° apart.
    QVector3D L( 0.3f,  0.5f, 0.8f); L.normalize();
    QVector3D F(-0.3f, -0.5f, 0.8f); F.normalize();
    u.light_dir[0] = L.x(); u.light_dir[1] = L.y(); u.light_dir[2] = L.z(); u.light_dir[3] = 0;
    u.fill_dir [0] = F.x(); u.fill_dir [1] = F.y(); u.fill_dir [2] = F.z(); u.fill_dir [3] = 0;
    u.sky_color   [0] = 0.55f; u.sky_color   [1] = 0.60f; u.sky_color   [2] = 0.70f;
    u.ground_color[0] = 0.35f; u.ground_color[1] = 0.32f; u.ground_color[2] = 0.28f;

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

void WgpuViewportWindow::setCamera(float tx, float ty, float tz,
                                   float dist, float yaw_deg, float pitch_deg) {
    camera_target_[0] = tx;
    camera_target_[1] = ty;
    camera_target_[2] = tz;
    camera_distance_  = std::max(0.01f, dist);
    camera_yaw_deg_   = yaw_deg;
    camera_pitch_deg_ = std::clamp(pitch_deg, -89.9f, 89.9f);
    // Suppress the auto-viewAll on the first model load so the script-set
    // camera survives. Manual viewAll() calls after this still work.
    initial_view_applied_ = true;
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::viewAll() {
    float mn[3], mx[3];
    if (!computeSceneAabb(mn, mx)) return;

    // Frame the union AABB with the same math as GL's frameAabb(mn, mx, 1.10):
    // target at centroid, distance pulls the bounding sphere just inside the
    // tighter of the horizontal/vertical FOV. Padding 1.10 matches GL viewAll.
    const float cx = 0.5f * (mn[0] + mx[0]);
    const float cy = 0.5f * (mn[1] + mx[1]);
    const float cz = 0.5f * (mn[2] + mx[2]);
    camera_target_[0] = cx;
    camera_target_[1] = cy;
    camera_target_[2] = cz;

    const float dx = mx[0] - mn[0];
    const float dy = mx[1] - mn[1];
    const float dz = mx[2] - mn[2];
    const float radius = 0.5f * std::sqrt(dx*dx + dy*dy + dz*dz);

    if (radius > 1e-4f) {
        const float fovy_rad = qDegreesToRadians(camera_fov_y_deg_);
        const float tan_half = std::tan(fovy_rad * 0.5f);
        if (tan_half > 1e-6f) {
            const int   h          = std::max(configured_h_, 1);
            const float aspect     = float(std::max(configured_w_, 1)) / float(h);
            const float min_aspect = aspect < 1.0f ? aspect : 1.0f;
            camera_distance_ = std::max(0.1f, (radius / (tan_half * min_aspect)) * 1.10f);
        }
    }

    qInfo().noquote().nospace()
        << "[wgpu] viewAll target=(" << cx << ", " << cy << ", " << cz << ")"
        << " distance=" << camera_distance_
        << " (scene radius=" << radius << ")";

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
    nav_press_pos_     = nav_last_pos_;
    nav_dragged_       = false;
}

void WgpuViewportWindow::mouseReleaseEvent(QMouseEvent* event) {
    if (event->button() == nav_active_button_) {
        // LMB-click without drag → pick the object under the cursor and
        // route through the selection state. Shift = add, Ctrl = remove,
        // no modifier = replace. Empty-space click clears.
        if (event->button() == Qt::LeftButton && !nav_dragged_) {
            const QPoint pos = event->position().toPoint();
            const int px = int(pos.x() * devicePixelRatio());
            const int py = int(pos.y() * devicePixelRatio());
            const uint32_t id = pickObjectAt(px, py);
            const auto mods = event->modifiers();
            if (id == 0) {
                if (!(mods & (Qt::ShiftModifier | Qt::ControlModifier))) {
                    selection_.clear();
                }
                qInfo().noquote() << "[wgpu pick] miss";
            } else if (mods & Qt::ControlModifier) {
                selection_.remove(id);
                qInfo().noquote().nospace()
                    << "[wgpu pick] -remove object_id=" << id;
            } else if (mods & Qt::ShiftModifier) {
                selection_.add(id);
                qInfo().noquote().nospace()
                    << "[wgpu pick] +add object_id=" << id;
            } else {
                selection_.replace(id);
                qInfo().noquote().nospace()
                    << "[wgpu pick] replace object_id=" << id;
            }
            requestUpdate();
        }
        nav_active_button_ = Qt::NoButton;
    }
}

void WgpuViewportWindow::mouseMoveEvent(QMouseEvent* event) {
    if (nav_active_button_ == Qt::NoButton) return;

    const QPoint pos = event->position().toPoint();
    const int dx = pos.x() - nav_last_pos_.x();
    const int dy = pos.y() - nav_last_pos_.y();
    nav_last_pos_ = pos;

    // Promote to drag past 3 px so a wobbly click doesn't get reclassified.
    if (!nav_dragged_) {
        const int adx = std::abs(pos.x() - nav_press_pos_.x());
        const int ady = std::abs(pos.y() - nav_press_pos_.y());
        if (adx + ady > 3) nav_dragged_ = true;
    }

    if (nav_active_button_ == Qt::LeftButton) {
        // Orbit. Sign convention matches the GL viewport: drag-right rotates
        // the world right (yaw -= dx), drag-down tilts the camera up so we
        // see more of the object's top (pitch += dy). 0.4 deg/px feels right
        // for a 1280-wide window.
        camera_yaw_deg_   -= float(dx) * 0.4f;
        camera_pitch_deg_ += float(dy) * 0.4f;
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

void WgpuViewportWindow::keyPressEvent(QKeyEvent* event) {
    // Visibility shortcuts, modelled on the GL viewer:
    //   H         — hide selected
    //   Shift+H   — show all (clear hidden set)
    //   I         — isolate selected (hide everything not currently selected)
    // None of these are useful without a selection (except show-all), so we
    // skip silently rather than burning a cull on an empty mutation.
    const auto mods = event->modifiers();
    const int key   = event->key();

    if (key == Qt::Key_H && (mods & Qt::ShiftModifier)) {
        if (visibility_.hiddenCount() == 0) return;
        visibility_.clear();
        qInfo() << "[wgpu] show all";
        requestUpdate();
        return;
    }
    if (key == Qt::Key_H) {
        if (selection_.count() == 0) return;
        for (uint32_t id : selection_.ids()) visibility_.hide(id);
        const size_t n = selection_.count();
        selection_.clear();   // hiding deselects, matching GL behaviour
        qInfo().noquote().nospace() << "[wgpu] hid " << n << " selected";
        requestUpdate();
        return;
    }
    if (key == Qt::Key_I) {
        if (selection_.count() == 0) return;
        // Walk every instance across all models; hide those NOT in selection.
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
        qInfo().noquote().nospace() << "[wgpu] isolated " << selection_.count()
                                    << " (hid " << hidden_now << " others)";
        requestUpdate();
        return;
    }

    QWindow::keyPressEvent(event);
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
    releaseMsaaColorTexture();
    releaseHizResources();
    releaseEdgeResources();
    releasePickResources();

    if (frame_bind_group_)        { wgpuBindGroupRelease(frame_bind_group_);          frame_bind_group_ = nullptr; }
    if (frame_uniform_buffer_)    { wgpuBufferRelease(frame_uniform_buffer_);         frame_uniform_buffer_ = nullptr; }
    if (selection_flags_buffer_)  { wgpuBufferRelease(selection_flags_buffer_);       selection_flags_buffer_ = nullptr; }
    selection_flags_capacity_ = 0;
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
