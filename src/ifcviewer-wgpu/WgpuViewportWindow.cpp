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
#include "WgpuStreamingLoader.h"

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

// Section-cutting cap. Single source of truth lives in WgpuOverlayRenderer
// so the visualizer and the WGSL clip array agree by construction.
static constexpr int kMaxSectionPlanes = WgpuOverlayRenderer::kMaxSectionPlanes;

struct FrameUniforms {
    float view_proj[16];
    float light_dir[4];     // xyz = unit dir toward light, w unused
    float fill_dir[4];      // xyz = secondary fill dir
    float sky_color[4];     // xyz = sky-tint ambient, w unused
    float ground_color[4];  // xyz = ground-tint ambient, w unused
    int   clip_count;       // active section-plane count (≤ kMaxSectionPlanes)
    int   _pad_clip[3];     // pad to 16-byte alignment for the array below
    float clip_planes[kMaxSectionPlanes][4]; // xyz = world-space unit normal, w = plane offset
};
static_assert(sizeof(FrameUniforms)
                  == 16 * sizeof(float)
                   + 4 * 4 * sizeof(float)
                   + 4 * sizeof(int)
                   + kMaxSectionPlanes * 4 * sizeof(float),
              "FrameUniforms must match WGSL layout");

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

// Interleave the low 21 bits of v with two zero bits between each,
// returning bits at positions 0, 3, 6, ..., 60 — one axis of a
// standard 21-bit-per-axis 3D Morton code. ORing three of these
// shifted by 0, 1, 2 gives a 63-bit (x, y, z)-interleaved code; the
// resulting integer ordering puts spatially-close points close in
// the sorted sequence (the classic Z-order curve).
static uint64_t mortonSplit21(uint32_t v) {
    uint64_t r = v & 0x1FFFFFu;
    r = (r | r << 32) & 0x001F00000000FFFFULL;
    r = (r | r << 16) & 0x001F0000FF0000FFULL;
    r = (r | r << 8)  & 0x100F00F00F00F00FULL;
    r = (r | r << 4)  & 0x10C30C30C30C30C3ULL;
    r = (r | r << 2)  & 0x1249249249249249ULL;
    return r;
}

static uint64_t mortonCode3D(uint32_t x, uint32_t y, uint32_t z) {
    return mortonSplit21(x) | (mortonSplit21(y) << 1) | (mortonSplit21(z) << 2);
}

// Return a mesh-id permutation sorted by 3D Morton (Z-order) code over
// the meshes' centroids. Replaces a lexicographic (z, y, x) sort,
// which was effectively a 1D Z-slab traversal — chunks ended up
// spanning the whole XY extent of the model, ~50m × 50m × 0.5m for a
// typical building. Morton clusters spatially in all 3 axes, so each
// chunk's AABB becomes a tight 3D voxel — small enough that
// per-chunk frustum / contribution / HiZ rejection becomes meaningful
// (a 1km-wide AABB never gets occluded; a 10m voxel often does).
//
// Meshes with no instances get a Morton code of 0 and sink to the
// front; they contribute no geometry / AABBs so where they land in
// the chunk plan doesn't matter.
static std::vector<uint32_t> sortMeshIdsByMorton(
        std::size_t n_meshes,
        const std::vector<float>&    mesh_cx,
        const std::vector<float>&    mesh_cy,
        const std::vector<float>&    mesh_cz,
        const std::vector<uint32_t>& mesh_inst_count) {
    // Per-model bounds over centroids. Quantising relative to these
    // gives the Morton code its full 21-bit-per-axis resolution
    // (~2 M bins per axis = sub-millimetre on a kilometre-scale scene,
    // way more than we need; the cost is the same regardless).
    float bmin[3] = {  std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity() };
    float bmax[3] = { -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity() };
    for (std::size_t i = 0; i < n_meshes; ++i) {
        if (mesh_inst_count[i] == 0) continue;
        bmin[0] = std::min(bmin[0], mesh_cx[i]); bmax[0] = std::max(bmax[0], mesh_cx[i]);
        bmin[1] = std::min(bmin[1], mesh_cy[i]); bmax[1] = std::max(bmax[1], mesh_cy[i]);
        bmin[2] = std::min(bmin[2], mesh_cz[i]); bmax[2] = std::max(bmax[2], mesh_cz[i]);
    }
    const float ext[3] = {
        std::max(bmax[0] - bmin[0], 1e-3f),
        std::max(bmax[1] - bmin[1], 1e-3f),
        std::max(bmax[2] - bmin[2], 1e-3f),
    };
    constexpr uint32_t MORTON_BITS = 21;
    constexpr uint32_t MORTON_MAX  = (1u << MORTON_BITS) - 1u;

    std::vector<uint64_t> codes(n_meshes, 0);
    for (uint32_t i = 0; i < uint32_t(n_meshes); ++i) {
        if (mesh_inst_count[i] == 0) continue;
        const float nx = (mesh_cx[i] - bmin[0]) / ext[0];
        const float ny = (mesh_cy[i] - bmin[1]) / ext[1];
        const float nz = (mesh_cz[i] - bmin[2]) / ext[2];
        const uint32_t qx = std::min(uint32_t(nx * float(MORTON_MAX + 1u)), MORTON_MAX);
        const uint32_t qy = std::min(uint32_t(ny * float(MORTON_MAX + 1u)), MORTON_MAX);
        const uint32_t qz = std::min(uint32_t(nz * float(MORTON_MAX + 1u)), MORTON_MAX);
        codes[i] = mortonCode3D(qx, qy, qz);
    }

    std::vector<uint32_t> sorted(n_meshes);
    std::iota(sorted.begin(), sorted.end(), 0u);
    std::stable_sort(sorted.begin(), sorted.end(),
        [&](uint32_t a, uint32_t b) { return codes[a] < codes[b]; });
    return sorted;
}

void releaseWgpuModelGpuData(WgpuModelGpuData& m, WgpuBufferPool& pool) {
    for (auto& c : m.chunks) {
        if (c.bind_group)           { wgpuBindGroupRelease(c.bind_group);          c.bind_group = nullptr; }
        if (c.vertex_slice.valid()) {
            pool.free(c.vertex_slice);
            c.vertex_slice = {};
        }
        if (c.index_slice.valid()) {
            pool.free(c.index_slice);
            c.index_slice = {};
        }
        if (c.visible_draws_buffer) { wgpuBufferRelease(c.visible_draws_buffer);   c.visible_draws_buffer = nullptr; }
        if (c.prefix_sums_buffer)   { wgpuBufferRelease(c.prefix_sums_buffer);     c.prefix_sums_buffer = nullptr; }
        if (c.per_chunk_uniform)    { wgpuBufferRelease(c.per_chunk_uniform);      c.per_chunk_uniform = nullptr; }
    }
    m.chunks.clear();
    m.mesh_chunk_idx.clear();
    m.mesh_chunk_local_base_vertex.clear();
    m.mesh_chunk_local_ebo_first_u32.clear();
    m.mesh_chunk_local_lod1_first_u32.clear();
    m.instance_chunk_idx.clear();
    m.instance_base_vertex.clear();
    m.instance_ebo_first_u32.clear();
    m.instance_lod1_first_u32.clear();
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
    clip_count:   i32,
    // Three scalar i32 pads instead of vec3<i32>: vec3 has 16-byte
    // alignment so it would also pad the SUBSEQUENT clip_planes start
    // up to offset 160. Three i32s pad to 144 with no further nudge,
    // matching the tightly-packed C++ FrameUniforms (240 B).
    _pad_clip_0:  i32,
    _pad_clip_1:  i32,
    _pad_clip_2:  i32,
    clip_planes:  array<vec4<f32>, 6>,
};

// Returns true if `world` lies on the positive (clipped-away) side of any
// active section plane. Each plane is (n.xyz, d) and clips where
// dot(n, world) + d > 0. Both the main and pick fragments discard with
// this predicate so cuts are visible AND consistent with selection.
fn is_section_clipped(world: vec3<f32>) -> bool {
    let n = u_frame.clip_count;
    if (n == 0) { return false; }
    for (var i = 0; i < n; i = i + 1) {
        let p = u_frame.clip_planes[i];
        if (dot(p.xyz, world) + p.w > 0.0) { return true; }
    }
    return false;
}

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
    if (is_section_clipped(in.world_pos)) { discard; }

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
    @location(1) world_pos: vec3<f32>,
    @location(2) normal:    vec3<f32>,
};

// Section tool needs the actual per-fragment normal (the AABB face was
// too coarse for diagonal geometry). Two color attachments — R32UInt
// object_id at @location(0), RGBA16F packed normal at @location(1).
// We multiply-by-0.5+0.5 so unsigned half-floats keep the sign without
// extra channel allocation.
struct FsOutPick {
    @location(0) object_id: u32,
    @location(1) normal:    vec4<f32>,
};

@vertex
fn vs_pick(@builtin(vertex_index) vid: u32) -> VsOutPick {
    var out: VsOutPick;
    if (vid >= u_model.total_vertex_count) {
        out.clip_pos  = vec4<f32>(0.0, 0.0, 0.0, 0.0);
        out.object_id = 0u;
        out.world_pos = vec3<f32>(0.0, 0.0, 0.0);
        out.normal    = vec3<f32>(0.0, 0.0, 1.0);
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

    // Decode the same octahedral normal as vs_main — pick needs it so
    // the section tool can drop perpendicular cuts.
    let nx = f32(extractI8(w1, 2u)) / 127.0;
    let ny = f32(extractI8(w1, 3u)) / 127.0;
    let n_local = octDecode(vec2<f32>(nx, ny));
    let rot = mat3x3<f32>(inst.transform[0].xyz,
                          inst.transform[1].xyz,
                          inst.transform[2].xyz);
    let n_world = normalize(rot * n_local);
    let det = determinant(rot);
    let n_final = select(n_world, -n_world, det < 0.0);

    out.clip_pos  = u_frame.view_proj * world4;
    out.object_id = inst.object_id;
    out.world_pos = world4.xyz;
    out.normal    = n_final;
    return out;
}

@fragment
fn fs_pick(in: VsOutPick) -> FsOutPick {
    if (is_section_clipped(in.world_pos)) { discard; }
    var out: FsOutPick;
    out.object_id = in.object_id;
    // Pack signed normal into RGBA16F (unsigned-ish half range) as ×0.5+0.5.
    out.normal = vec4<f32>(normalize(in.normal) * 0.5 + vec3<f32>(0.5), 1.0);
    return out;
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

    // Streaming path: load metadata only, chunks stay non-resident until
    // the per-frame loader brings them in. Falls back to legacy full-load
    // when streaming_enabled_ is off (default).
    if (streaming_enabled_) {
        auto meta_opt = readSidecarMetadataOnly(resolved.toStdString());
        if (!meta_opt) {
            qWarning().noquote() << "Failed to stream-read sidecar metadata:" << resolved;
            return 0;
        }
        const uint32_t mid = next_model_id_++;
        applyCachedModelStreaming(mid, std::move(*meta_opt));
        return mid;
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

void WgpuViewportWindow::applyCachedModelStreaming(uint32_t model_id,
                                                   StreamingSidecar metadata) {
    if (!device_ || !queue_) {
        qWarning() << "applyCachedModelStreaming without an initialised device";
        return;
    }

    // Replace any existing state for this id.
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        releaseWgpuModelGpuData(it->second, pool_);
        models_gpu_.erase(it);
    }

    WgpuModelGpuData m;
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
        std::vector<uint32_t> sorted_mesh_ids =
            sortMeshIdsByMorton(n_meshes, mesh_cx, mesh_cy, mesh_cz, mesh_inst_count);
        chunk_mesh_ids.push_back({});
        uint64_t current_chunk_bytes = 0;
        for (uint32_t mi : sorted_mesh_ids) {
            const MeshInfo& mesh = metadata.meta.meshes[mi];
            const uint64_t mesh_bytes = uint64_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            if (current_chunk_bytes > 0
                && current_chunk_bytes + mesh_bytes > WGPU_CHUNK_VERTEX_BYTES_LIMIT) {
                chunk_mesh_ids.push_back({});
                current_chunk_bytes = 0;
            }
            chunk_mesh_ids.back().push_back(mi);
            current_chunk_bytes += mesh_bytes;
        }
        if (chunk_mesh_ids.back().empty()) chunk_mesh_ids.pop_back();
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
        WgpuModelGpuData::Chunk& c = m.chunks[ci];
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
        const size_t draws_bytes = chunk_inst * sizeof(WgpuModelGpuData::VisibleDrawGpu);
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
    WgpuModelGpuData& mref = inserted->second;

    // Bind groups can't be built yet — they need vertex_storage from each
    // chunk's load. The per-frame loader (commit 4) will buildModelBindGroup
    // after a chunk becomes resident.

    qInfo().noquote().nospace()
        << "[wgpu stream] applyCachedModelStreaming mid=" << model_id
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

void WgpuViewportWindow::applyCachedModel(uint32_t model_id, SidecarData data) {
    if (!device_ || !queue_) {
        qWarning() << "applyCachedModel without an initialised device";
        return;
    }

    // Replace any existing state for this id.
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        releaseWgpuModelGpuData(it->second, pool_);
        models_gpu_.erase(it);
    }

    WgpuModelGpuData m;
    m.vertex_bytes   = data.vertices.size();
    m.index_count    = uint32_t(data.indices.size());
    m.mesh_count     = uint32_t(data.meshes.size());
    m.instance_count = uint32_t(data.instances.size());

    // ---- Spatial chunk plan ----------------------------------------------
    // Identical algorithm to applyCachedModelStreaming: sort meshes by
    // world-space centroid, then greedy-pack into chunks of
    // ≤WGPU_CHUNK_VERTEX_BYTES_LIMIT. Each chunk's mesh_ids list defines
    // the chunk-local layout order. Non-streaming differs only in that
    // vertex+index bytes are already in memory (data.vertices,
    // data.indices), so we gather them with per-mesh queueWriteBuffer
    // calls instead of scatter-gather disk reads.
    const size_t n_meshes = data.meshes.size();
    m.mesh_chunk_idx.assign(n_meshes, 0);
    m.mesh_chunk_local_base_vertex.assign(n_meshes, 0);
    m.mesh_chunk_local_ebo_first_u32.assign(n_meshes, 0);
    m.mesh_chunk_local_lod1_first_u32.assign(n_meshes, 0);

    std::vector<float>    mesh_cx(n_meshes, 0.0f),
                          mesh_cy(n_meshes, 0.0f),
                          mesh_cz(n_meshes, 0.0f);
    std::vector<uint32_t> mesh_inst_count(n_meshes, 0);
    for (const auto& inst : data.instances) {
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

    // Morton sort (see sortMeshIdsByMorton above) — same logic as the
    // streaming path; gives tight 3D voxel chunks instead of XY slabs.
    std::vector<uint32_t> sorted_mesh_ids =
        sortMeshIdsByMorton(n_meshes, mesh_cx, mesh_cy, mesh_cz, mesh_inst_count);

    std::vector<std::vector<uint32_t>> chunk_mesh_ids;
    chunk_mesh_ids.push_back({});
    uint64_t current_chunk_bytes = 0;
    for (uint32_t mi : sorted_mesh_ids) {
        const MeshInfo& mesh = data.meshes[mi];
        const uint64_t mesh_vertex_bytes = uint64_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        if (mesh_vertex_bytes > WGPU_CHUNK_VERTEX_BYTES_LIMIT) {
            qWarning().noquote().nospace()
                << "Mesh #" << mi << " has " << mesh_vertex_bytes
                << " B — exceeds chunk limit " << WGPU_CHUNK_VERTEX_BYTES_LIMIT
                << ". Mesh-splitting is not implemented.";
        }
        if (current_chunk_bytes > 0
            && current_chunk_bytes + mesh_vertex_bytes > WGPU_CHUNK_VERTEX_BYTES_LIMIT) {
            chunk_mesh_ids.push_back({});
            current_chunk_bytes = 0;
        }
        chunk_mesh_ids.back().push_back(mi);
        current_chunk_bytes += mesh_vertex_bytes;
    }
    if (chunk_mesh_ids.back().empty()) chunk_mesh_ids.pop_back();

    std::vector<uint32_t> mesh_to_chunk(n_meshes, 0);
    for (size_t ci = 0; ci < chunk_mesh_ids.size(); ++ci) {
        for (uint32_t mi : chunk_mesh_ids[ci]) mesh_to_chunk[mi] = uint32_t(ci);
    }
    std::vector<uint32_t> chunk_instance_count(chunk_mesh_ids.size(), 0);
    for (const auto& inst : data.instances) {
        if (inst.mesh_id < n_meshes) ++chunk_instance_count[mesh_to_chunk[inst.mesh_id]];
    }

    // ---- Allocate per-chunk pool ranges and upload per-mesh slices ------
    m.chunks.resize(chunk_mesh_ids.size());
    for (size_t ci = 0; ci < chunk_mesh_ids.size(); ++ci) {
        WgpuModelGpuData::Chunk& c = m.chunks[ci];
        c.mesh_ids = std::move(chunk_mesh_ids[ci]);

        // Walk meshes in chunk-local layout order, computing each mesh's
        // chunk-local offsets and the chunk's aggregate vertex/index totals.
        // LOD1 indices (if any mesh has them baked) pack AFTER all the
        // LOD0 indices in the chunk's index slice — single slice carries
        // both LODs, cull picks per-instance by chunk-local u32 offset.
        uint32_t chunk_local_v = 0;
        uint32_t chunk_local_i = 0;
        for (uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = data.meshes[mi];
            m.mesh_chunk_idx[mi]                 = uint32_t(ci);
            m.mesh_chunk_local_base_vertex[mi]   = chunk_local_v;
            m.mesh_chunk_local_ebo_first_u32[mi] = chunk_local_i;
            chunk_local_v += mesh.vertex_count;
            chunk_local_i += mesh.index_count;
        }
        uint32_t chunk_local_lod1 = 0;
        for (uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = data.meshes[mi];
            if (mesh.lod1_index_count == 0) continue;
            m.mesh_chunk_local_lod1_first_u32[mi] = chunk_local_i + chunk_local_lod1;
            chunk_local_lod1 += mesh.lod1_index_count;
        }
        c.vertex_count     = chunk_local_v;
        c.vertex_byte_size = uint64_t(chunk_local_v) * INSTANCED_VERTEX_STRIDE_BYTES;
        c.index_count      = chunk_local_i + chunk_local_lod1;
        c.lod1_index_count = chunk_local_lod1;

        c.vertex_slice = pool_.alloc(c.vertex_byte_size, 256);
        if (!c.vertex_slice.valid()) {
            qWarning().noquote().nospace()
                << "[wgpu] pool OOM: chunk " << ci << " needed "
                << c.vertex_byte_size << " B for vertices, pool free="
                << pool_.total_free_bytes() << " B across "
                << pool_.sub_buffer_count() << " sub-buffer(s); aborting model load";
            releaseWgpuModelGpuData(m, pool_);
            return;
        }
        if (c.index_count > 0) {
            c.index_slice = pool_.alloc(c.index_count * sizeof(uint32_t), 256);
            if (!c.index_slice.valid()) {
                qWarning().noquote().nospace()
                    << "[wgpu] pool OOM: chunk " << ci << " needed "
                    << (c.index_count * sizeof(uint32_t))
                    << " B for indices, pool free=" << pool_.total_free_bytes()
                    << " B across " << pool_.sub_buffer_count()
                    << " sub-buffer(s); aborting model load";
                releaseWgpuModelGpuData(m, pool_);
                return;
            }
        }

        // Gather each mesh's bytes from data.vertices / data.indices and
        // write into the pool at chunk-local offsets. Multiple small
        // queueWriteBuffer calls per chunk; wgpu batches them efficiently.
        uint64_t v_off = 0;
        uint64_t i_off = 0;
        for (uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = data.meshes[mi];
            const size_t v_bytes = size_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            if (v_bytes > 0) {
                wgpuQueueWriteBuffer(queue_, c.vertex_slice.buffer,
                                     c.vertex_slice.offset + v_off,
                                     data.vertices.data() + mesh.vbo_byte_offset,
                                     v_bytes);
                v_off += v_bytes;
            }
            const size_t i_bytes = size_t(mesh.index_count) * sizeof(uint32_t);
            if (i_bytes > 0) {
                wgpuQueueWriteBuffer(queue_, c.index_slice.buffer,
                                     c.index_slice.offset + i_off,
                                     data.indices.data() + (mesh.ebo_byte_offset / sizeof(uint32_t)),
                                     i_bytes);
                i_off += i_bytes;
            }
        }
        // LOD1 indices second, packed after all LOD0 indices in the slice.
        // mesh_chunk_local_lod1_first_u32[mi] already encodes this layout —
        // we just have to copy in the same order it was assigned.
        for (uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = data.meshes[mi];
            if (mesh.lod1_index_count == 0) continue;
            const size_t l1_bytes = size_t(mesh.lod1_index_count) * sizeof(uint32_t);
            wgpuQueueWriteBuffer(queue_, c.index_slice.buffer,
                                 c.index_slice.offset + i_off,
                                 data.indices.data() + (mesh.lod1_ebo_byte_offset / sizeof(uint32_t)),
                                 l1_bytes);
            i_off += l1_bytes;
        }
        m.vram_bytes_vbo += c.vertex_byte_size;
        m.vram_bytes_ebo += c.index_count * sizeof(uint32_t);
    }

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
    const size_t mesh_storage_bytes = mesh_gpu.size() * sizeof(MeshGpu);
    m.mesh_storage = createBufferWithData(
        device_, queue_,
        mesh_gpu.data(), mesh_storage_bytes,
        WGPUBufferUsage_Storage,
        "model.mesh_storage");
    m.vram_bytes_ssbo += mesh_storage_bytes;

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
    const size_t inst_storage_bytes = inst_gpu.size() * sizeof(InstanceGpu);
    m.instance_storage = createBufferWithData(
        device_, queue_,
        inst_gpu.data(), inst_storage_bytes,
        WGPUBufferUsage_Storage,
        "model.instance_storage");
    m.vram_bytes_ssbo += inst_storage_bytes;

    // Per-chunk buffers for cross-mesh vertex pulling. Each chunk is sized
    // to its own worst case (instances whose mesh lives in that chunk) —
    // each visible instance only ever contributes ONE VisibleDraw entry
    // (LOD0 OR LOD1), so the previous instance_count × 2 cap was a 4×
    // over-allocation on multi-chunk models. Tight sizing also keeps total
    // VRAM down on dense scenes.
    for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
        WgpuModelGpuData::Chunk& c = m.chunks[ci];

        const size_t chunk_inst = std::max<size_t>(chunk_instance_count[ci], 1);
        const size_t draws_bytes = chunk_inst * sizeof(WgpuModelGpuData::VisibleDrawGpu);
        const size_t ps_cap      = chunk_inst + 1;
        const size_t ps_bytes    = ps_cap * sizeof(uint32_t);

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
        c.prefix_sums_capacity = ps_cap;
        m.vram_bytes_ssbo += ps_desc.size;

        WGPUBufferDescriptor mu_desc = {};
        mu_desc.size  = 16;
        mu_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        mu_desc.label = svFromCStr("model.chunk.uniform");
        c.per_chunk_uniform = wgpuDeviceCreateBuffer(device_, &mu_desc);
        m.vram_bytes_ssbo += 16;

        c.visible_draws_scratch.reserve(chunk_inst);
        c.prefix_sums_scratch.reserve(ps_cap);
    }

    // Hand off CPU mirrors (cull / picking will need them later).
    m.meshes    = std::move(data.meshes);
    m.instances = std::move(data.instances);

    // Per-chunk world AABB + instance-id list. Same logic as the
    // streaming path. Lets cull frustum-test each chunk's AABB once
    // and skip every instance inside in one shot when the chunk is
    // off-screen.
    for (auto& c : m.chunks) {
        c.instance_ids.reserve(m.instances.size() / m.chunks.size() + 4);
    }
    for (uint32_t inst_idx = 0; inst_idx < uint32_t(m.instances.size()); ++inst_idx) {
        const auto& inst = m.instances[inst_idx];
        if (inst.mesh_id >= m.mesh_chunk_idx.size()) continue;
        const uint32_t ci = m.mesh_chunk_idx[inst.mesh_id];
        if (ci >= m.chunks.size()) continue;
        auto& c = m.chunks[ci];
        for (int a = 0; a < 3; ++a) {
            c.aabb_min[a] = std::min(c.aabb_min[a], inst.world_aabb_min[a]);
            c.aabb_max[a] = std::max(c.aabb_max[a], inst.world_aabb_max[a]);
        }
        c.instance_ids.push_back(inst_idx);
    }

    // Resolve per-instance chunk lookups by translating from the per-mesh
    // arrays. Cull reads these directly, so the spatial-bucket planner
    // (which can place the same mesh in multiple chunks under #55) will
    // populate them without going through mesh_chunk_idx[].
    {
        const size_t n_inst = m.instances.size();
        m.instance_chunk_idx.assign(n_inst, 0);
        m.instance_base_vertex.assign(n_inst, 0);
        m.instance_ebo_first_u32.assign(n_inst, 0);
        m.instance_lod1_first_u32.assign(n_inst, 0);
        for (size_t i = 0; i < n_inst; ++i) {
            const uint32_t mi = m.instances[i].mesh_id;
            if (mi >= m.mesh_chunk_idx.size()) continue;
            m.instance_chunk_idx[i]      = m.mesh_chunk_idx[mi];
            m.instance_base_vertex[i]    = m.mesh_chunk_local_base_vertex[mi];
            m.instance_ebo_first_u32[i]  = m.mesh_chunk_local_ebo_first_u32[mi];
            m.instance_lod1_first_u32[i] = m.mesh_chunk_local_lod1_first_u32[mi];
        }
    }

    auto [inserted, _] = models_gpu_.emplace(model_id, std::move(m));
    WgpuModelGpuData& mref = inserted->second;
    buildModelBindGroup(mref);

    // Cumulative VRAM across all loaded models so the user can see where
    // the wall is hit when streaming into a multi-GB scene.
    uint64_t total_vbo = 0, total_ebo = 0, total_ssbo = 0;
    for (const auto& [mid_other, mo] : models_gpu_) {
        total_vbo  += mo.vram_bytes_vbo;
        total_ebo  += mo.vram_bytes_ebo;
        total_ssbo += mo.vram_bytes_ssbo;
    }
    const double mb = 1.0 / (1024.0 * 1024.0);
    qInfo().noquote().nospace()
        << "[wgpu] applyCachedModel mid=" << model_id
        << " verts=" << mref.vertex_bytes << "B"
        << " idx="   << mref.index_count
        << " meshes=" << mref.mesh_count
        << " instances=" << mref.instance_count
        << " chunks=" << mref.chunks.size()
        << " | model vram=" << QString::number(double(mref.vram_bytes_vbo
                                                  + mref.vram_bytes_ebo
                                                  + mref.vram_bytes_ssbo) * mb, 'f', 1) << "MB"
        << "  total vram="  << QString::number(double(total_vbo + total_ebo + total_ssbo) * mb, 'f', 1) << "MB"
        << " (vbo "  << QString::number(double(total_vbo)  * mb, 'f', 1)
        << " + ebo " << QString::number(double(total_ebo)  * mb, 'f', 1)
        << " + ssbo "<< QString::number(double(total_ssbo) * mb, 'f', 1) << ")";

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
    releaseWgpuModelGpuData(it->second, pool_);
    models_gpu_.erase(it);
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::resetScene() {
    for (auto& [mid, m] : models_gpu_) releaseWgpuModelGpuData(m, pool_);
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

    // Env-var overrides for contribution-cull thresholds. wgpu uses
    // view-Z (perspective-divide-correct) for projected_px, whereas the
    // GL backend uses euclidean distance — so for off-axis instances
    // wgpu computes a larger projected_px and is less aggressive at the
    // same numeric threshold. These knobs exist to let us sweep matching
    // values during the perf-parity push without rebuilding.
    if (const char* s = std::getenv("WGPU_MIN_PX")) {
        const float v = float(std::atof(s));
        if (v >= 0.0f) min_pixel_radius_ = v;
        qInfo().noquote().nospace()
            << "[wgpu cull] WGPU_MIN_PX=" << min_pixel_radius_;
    }
    if (const char* s = std::getenv("WGPU_MIN_PX_MOTION")) {
        const float v = float(std::atof(s));
        if (v >= 0.0f) motion_min_pixel_radius_ = v;
        qInfo().noquote().nospace()
            << "[wgpu cull] WGPU_MIN_PX_MOTION=" << motion_min_pixel_radius_;
    }
    if (const char* s = std::getenv("WGPU_STREAM_DEBUG")) {
        streaming_debug_ = (s[0] == '1');
        if (streaming_debug_) {
            qInfo().noquote() << "[wgpu stream] WGPU_STREAM_DEBUG=1 — per-frame "
                                 "[stream-debug] log enabled";
        }
    }
    if (const char* s = std::getenv("WGPU_HIZ")) {
        if (s[0] == '1') {
            hiz_enabled_ = true;
            qInfo() << "[wgpu] WGPU_HIZ=1 — HiZ occlusion culling enabled "
                       "(disabled by default; see task #58)";
        }
    }
    if (const char* s = std::getenv("WGPU_CULL_THREADS")) {
        // "0" disables std::async dispatch — every model is culled on the
        // main thread, sequentially. Used to measure speedup vs the
        // parallel-per-model path. Any non-"0" value keeps parallelism on.
        cull_threads_enabled_ = (s[0] != '0');
        qInfo().noquote().nospace()
            << "[wgpu cull] WGPU_CULL_THREADS=" << s
            << " (parallelism " << (cull_threads_enabled_ ? "ON" : "OFF") << ")";
    }
    if (const char* s = std::getenv("WGPU_FLY_DEBUG")) {
        fly_debug_ = (s[0] == '1');
        if (fly_debug_) {
            qInfo() << "[wgpu fly] WGPU_FLY_DEBUG=1 — per-frame [fly] dt log enabled";
        }
    }
    // Mouse-nav preset (matches GL AppSettings::NavPreset). blender default,
    // rhino or revit as alternatives. Selection always stays on LMB.
    const char* nav_env = std::getenv("WGPU_NAV_PRESET");
    applyNavPreset(nav_env ? nav_env : "blender");
    qInfo().noquote().nospace()
        << "[wgpu nav] preset=" << (nav_env ? nav_env : "blender")
        << " (orbit "
        << (orbit_button_ == Qt::RightButton ? "RMB" : "MMB")
        << (orbit_mods_ & Qt::ShiftModifier ? "+Shift" : "")
        << ", pan "
        << (pan_button_ == Qt::RightButton ? "RMB" : "MMB")
        << (pan_mods_ & Qt::ShiftModifier ? "+Shift" : "")
        << ")";

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

    // ---- Probe streaming pool capacity ----------------------------------
    // Ask the device for the largest single buffer it'll actually give us.
    // Replaces the per-machine "guess the OOM ceiling" knob: now the
    // runtime answers the question. Failure here is fatal — without any
    // pool we can't load chunks.
    if (!probeAndCreatePool()) {
        qWarning() << "wgpu: streaming pool probe failed; cannot start";
        return false;
    }

    // Background loader for streaming reads — must outlive any
    // applyCachedModelStreaming call so we can drain results into the
    // pool. Stopped in shutdown() before pool_.destroy().
    streaming_thread_.start();

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
    if (!overlays_.init(instance_, device_, queue_, surface_format_, SAMPLE_COUNT)) {
        qWarning() << "WgpuOverlayRenderer init failed";
        return false;
    }
    if (!buildPickPipeline()) return false;

    qInfo() << "wgpu init OK; surface format =" << int(surface_format_);
    return true;
}

bool WgpuViewportWindow::probeAndCreatePool() {
    // Discover the largest single buffer the runtime will grant. We
    // descend from the device's advertised maxBufferSize because the
    // adapter promises that much per binding, but the underlying
    // allocator (gpu-alloc-rs on Vulkan, Metal heap manager, browser
    // internals) may refuse anything above an undocumented per-system
    // ceiling. The probe answers the question honestly.
    //
    // Each attempt is wrapped in an OOM error scope so a failed
    // allocation doesn't surface to onUncapturedError as a noisy
    // validation warning — the scope captures the OOM cleanly and we
    // simply halve and retry.

    WGPULimits device_limits = {};
    wgpuDeviceGetLimits(device_, &device_limits);

    // 64 MB lower bound: below this the viewer is unusable for any real
    // dataset, so we'd rather fail init than limp along.
    constexpr uint64_t MIN_POOL_CAPACITY = 64ull * 1024 * 1024;
    // 4 GB starting cap: this is the largest single buffer the WebGPU
    // ecosystem realistically supports today (browsers stay well below;
    // desktop drivers vary). Asking for the device's full advertised
    // maxBufferSize first is wasteful — on wgpu-native it can be 1 TB
    // (a sentinel meaning "no spec floor"), which always fails and
    // forces ~10 halving steps before we land somewhere sensible.
    constexpr uint64_t MAX_PROBE_START   = 4ull * 1024 * 1024 * 1024;
    uint64_t try_size = std::min<uint64_t>(device_limits.maxBufferSize,
                                           MAX_PROBE_START);
    if (try_size < MIN_POOL_CAPACITY) try_size = MIN_POOL_CAPACITY;

    const WGPUBufferUsage pool_usage = WGPUBufferUsage_Storage
                                     | WGPUBufferUsage_CopyDst;

    while (try_size >= MIN_POOL_CAPACITY) {
        // wgpu-native classifies "Not enough memory left" as Validation,
        // not OutOfMemory — so we need both filters. Nested scopes: OOM
        // inner (matches first), Validation outer (catches the rest).
        wgpuDevicePushErrorScope(device_, WGPUErrorFilter_Validation);
        wgpuDevicePushErrorScope(device_, WGPUErrorFilter_OutOfMemory);

        // Test allocation. If it survives both scopes, this size works
        // and becomes the pool's per-sub-buffer capacity.
        WGPUBufferDescriptor desc = {};
        desc.usage             = pool_usage;
        desc.size              = try_size;
        desc.label.data        = "ifcviewer-wgpu.pool_probe";
        desc.label.length      = std::strlen("ifcviewer-wgpu.pool_probe");
        WGPUBuffer probe_buf   = wgpuDeviceCreateBuffer(device_, &desc);

        struct PopResult { bool done = false; bool error = false; };
        auto pop = [&](PopResult& pr) {
            WGPUPopErrorScopeCallbackInfo pcb = {};
            pcb.mode = WGPUCallbackMode_AllowProcessEvents;
            pcb.callback = [](WGPUPopErrorScopeStatus, WGPUErrorType type,
                              WGPUStringView, void* ud1, void* /*ud2*/) {
                auto* p = static_cast<PopResult*>(ud1);
                p->done = true;
                p->error = (type != WGPUErrorType_NoError);
            };
            pcb.userdata1 = &pr;
            wgpuDevicePopErrorScope(device_, pcb);
            while (!pr.done) wgpuInstanceProcessEvents(instance_);
        };
        PopResult oom_pop, validation_pop;
        pop(oom_pop);
        pop(validation_pop);

        if (probe_buf) wgpuBufferRelease(probe_buf);
        if (probe_buf && !oom_pop.error && !validation_pop.error) {
            // Per-sub-buffer capacity locked in; the pool can grow
            // beyond this by allocating more sub-buffers of the same
            // size on demand (up to whatever the driver lets us total).
            pool_.configure(instance_, device_, pool_usage, try_size,
                            "ifcviewer-wgpu.pool");
            qInfo().noquote()
                << "wgpu: pool per-sub-buffer capacity ="
                << (try_size / (1024 * 1024)) << "MB"
                << "(device maxBufferSize ="
                << (device_limits.maxBufferSize / (1024 * 1024))
                << "MB); pool will grow on demand";
            return true;
        }
        try_size /= 2;
    }

    qWarning() << "wgpu: pool probe found no allocatable size >="
               << (MIN_POOL_CAPACITY / (1024 * 1024)) << "MB";
    return false;
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
    // Present mode. WGPU_PRESENT_MODE=fifo|fifo_relaxed|mailbox|immediate
    // (default fifo). Recommended for fly-mode stutter: fifo_relaxed.
    //   fifo          — strict vsync. Frame waiting > display refresh
    //                   pushes the present to the NEXT refresh, producing
    //                   the visible "double-frame" jump when cull or
    //                   chunk-apply briefly exceeds budget.
    //   fifo_relaxed  — adaptive vsync. Syncs to display when frame hits
    //                   the budget; allows tear when it doesn't. Removes
    //                   the missed-vsync stutter while keeping smooth
    //                   presentation when we're under budget. Best
    //                   compromise for the fly-mode jitter case.
    //   mailbox       — uncapped, last-frame-wins, no tearing. Not
    //                   supported on Vulkan + NVIDIA on Linux (falls
    //                   back to Fifo); use fifo_relaxed instead there.
    //   immediate     — uncapped, frames presented as soon as ready,
    //                   may tear. Useful for raw-throughput benchmarking.
    WGPUPresentMode pm = WGPUPresentMode_Fifo;
    const char* pm_name = "fifo";
    if (const char* s = std::getenv("WGPU_PRESENT_MODE")) {
        if (std::strcmp(s, "fifo_relaxed") == 0) {
            pm = WGPUPresentMode_FifoRelaxed; pm_name = "fifo_relaxed";
        } else if (std::strcmp(s, "mailbox") == 0) {
            pm = WGPUPresentMode_Mailbox;     pm_name = "mailbox";
        } else if (std::strcmp(s, "immediate") == 0) {
            pm = WGPUPresentMode_Immediate;   pm_name = "immediate";
        } else if (std::strcmp(s, "fifo") != 0) {
            qWarning().noquote().nospace()
                << "[wgpu] unknown WGPU_PRESENT_MODE=" << s
                << " (expected fifo|fifo_relaxed|mailbox|immediate); using fifo";
        }
    }
    cfg.presentMode = pm;
    if (pm != WGPUPresentMode_Fifo && !surface_configured_) {
        qInfo().noquote().nospace()
            << "[wgpu] present mode = " << pm_name
            << (pm == WGPUPresentMode_FifoRelaxed
                  ? " (adaptive vsync — sync if in budget, tear if not)"
                  : " (vsync OFF — framerate uncapped)");
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

// -----------------------------------------------------------------------------
void WgpuViewportWindow::setPivotIndicatorVisible(bool visible, int hide_after_ms) {
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
        qWarning() << "wgpu pick pipeline creation failed";
        return false;
    }
    return true;
}

void WgpuViewportWindow::ensurePickAttachments(int w, int h) {
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

void WgpuViewportWindow::releasePickResources() {
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

uint32_t WgpuViewportWindow::pickObjectAt(int x_pixels, int y_pixels,
                                          QVector3D* normal_out) {
    if (normal_out) *normal_out = QVector3D(0, 0, 1);
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
                QVector3D n(nx, ny, nz);
                if (n.lengthSquared() > 1e-6f) *normal_out = n.normalized();
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
static bool rayAABBHit(const QVector3D& origin, const QVector3D& dir,
                       const float mn[3], const float mx[3],
                       float& t_enter, QVector3D& face_normal) {
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
        QVector3D n(0, 0, 0);
        n[hit_axis] = hit_sign;
        face_normal = n;
    }
    return true;
}

std::vector<uint32_t> WgpuViewportWindow::picksInRect(int x, int y, int w, int h) {
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

bool WgpuViewportWindow::pickSurfaceAt(int x_pixels, int y_pixels,
                                       uint32_t& object_id_out,
                                       QVector3D& world_pos_out,
                                       QVector3D& world_normal_out,
                                       float* aabb_radius_out) {
    if (aabb_radius_out) *aabb_radius_out = 0.0f;
    QVector3D picked_normal(0, 0, 1);
    const uint32_t id = pickObjectAt(x_pixels, y_pixels, &picked_normal);
    if (id == 0) return false;

    // Build the ray through the clicked pixel: shoot from the camera eye
    // toward the unprojected far-plane point. WebGPU forbids partial copies
    // of Depth32Float (must cover the full mip extent), so reading per-pixel
    // depth would cost a per-click full-texture readback — instead we
    // ray-cast against the AABB of every instance carrying the picked
    // object_id and take the closest hit. Equally accurate for the section
    // tool's "drop a plane where I clicked" UX, no readback at all.
    QMatrix4x4 view, proj;
    buildViewProj(view, proj);
    bool ok = false;
    const QMatrix4x4 inv_vp = (proj * view).inverted(&ok);
    if (!ok) return false;

    const float ndc_x = (2.0f * float(x_pixels) / float(configured_w_)) - 1.0f;
    const float ndc_y = 1.0f - (2.0f * float(y_pixels) / float(configured_h_));
    // Unproject the far-plane corner (NDC z = 1 for WebGPU) of the
    // pick-pixel pillar to get a point on the ray.
    const QVector4D far_clip(ndc_x, ndc_y, 1.0f, 1.0f);
    const QVector4D far_w   = inv_vp * far_clip;
    if (std::abs(far_w.w()) < 1e-6f) return false;
    const QVector3D far_world = far_w.toVector3D() / far_w.w();

    const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                   camera_yaw_deg_, camera_pitch_deg_);
    QVector3D ray_dir = far_world - eye;
    if (ray_dir.lengthSquared() < 1e-8f) return false;
    ray_dir.normalize();

    float best_t = std::numeric_limits<float>::infinity();
    QVector3D best_point;
    QVector3D best_normal;
    float     best_radius = 0.0f;
    bool found = false;
    for (const auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& inst : m.instances) {
            if (inst.object_id != id) continue;
            float t = 0.0f;
            QVector3D n;
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
    world_normal_out = (picked_normal.lengthSquared() > 1e-3f)
                         ? picked_normal : best_normal;
    object_id_out    = id;
    return true;
}

// -----------------------------------------------------------------------------
// Section cutting state
// -----------------------------------------------------------------------------

void WgpuViewportWindow::toggleSectionTool() {
    section_tool_active_ = !section_tool_active_;
    qInfo().noquote() << "[wgpu section] tool"
                      << (section_tool_active_ ? "active" : "off");
    if (isExposed()) requestUpdate();
}

bool WgpuViewportWindow::addSectionPlaneAtSurface(const QVector3D& point,
                                                  const QVector3D& normal,
                                                  float visual_radius) {
    if (int(section_planes_.size()) >= kMaxSectionPlanes) {
        qWarning("[wgpu section] cap reached (%d planes)", kMaxSectionPlanes);
        return false;
    }
    QVector3D n = normal;
    if (n.lengthSquared() < 1e-8f) return false;
    n.normalize();
    // Auto-flip the normal so the camera-facing half gets cut away — that
    // way the first click always reveals the surface the user just clicked.
    const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                   camera_yaw_deg_, camera_pitch_deg_);
    const QVector3D eye_dir = eye - point;
    if (QVector3D::dotProduct(n, eye_dir) < 0.0f) n = -n;

    WgpuSectionPlane p;
    p.n             = n;
    p.origin        = point;
    p.d             = -QVector3D::dotProduct(n, point);
    p.visual_radius = (visual_radius > 0.0f) ? visual_radius : 1.0f;
    section_planes_.push_back(p);
    qInfo().noquote().nospace()
        << "[wgpu section] added plane #" << section_planes_.size() - 1
        << " origin=(" << point.x() << "," << point.y() << "," << point.z() << ")"
        << " normal=(" << n.x() << "," << n.y() << "," << n.z() << ")";
    if (isExposed()) requestUpdate();
    return true;
}

void WgpuViewportWindow::removeSectionPlane(int index) {
    if (index < 0 || index >= int(section_planes_.size())) return;
    section_planes_.erase(section_planes_.begin() + index);
    qInfo().noquote() << "[wgpu section] removed plane" << index;
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::clearSectionPlanes() {
    if (section_planes_.empty()) return;
    section_planes_.clear();
    qInfo() << "[wgpu section] cleared all planes";
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::setOverlayLines(
        const std::vector<WgpuOverlayRenderer::LineGroup>& groups) {
    overlays_.setOverlayLines(groups);
    if (isExposed()) requestUpdate();
}

// Project a world point to LOGICAL pixel coords (Qt's mouse-event units).
// Returns false if behind the camera.
static bool projectWorldToLogicalScreen(const QMatrix4x4& vp,
                                        const QVector3D& world,
                                        int win_w, int win_h,
                                        QVector2D& out) {
    const QVector4D clip = vp * QVector4D(world, 1.0f);
    if (clip.w() <= 0.0f) return false;
    const float invw = 1.0f / clip.w();
    out = QVector2D(
        (clip.x() * invw * 0.5f + 0.5f) * float(win_w),
        (1.0f - (clip.y() * invw * 0.5f + 0.5f)) * float(win_h));
    return true;
}

int WgpuViewportWindow::hitTestSectionGizmo(int x, int y) const {
    if (section_planes_.empty()) return -1;
    const int w = width();
    const int h = height();
    if (w <= 0 || h <= 0) return -1;
    QMatrix4x4 view, proj;
    buildViewProj(view, proj);
    const QMatrix4x4 vp = proj * view;
    const float grab_px = 12.0f;
    int   best    = -1;
    float best_d2 = grab_px * grab_px;
    for (int i = 0; i < int(section_planes_.size()); ++i) {
        const WgpuSectionPlane& p = section_planes_[i];
        QVector2D s_origin, s_tip;
        if (!projectWorldToLogicalScreen(vp, p.origin,
                                         w, h, s_origin)) continue;
        // The gizmo's arrow extends along +n by exactly 1 m in world
        // space — WgpuOverlayRenderer::encodeSectionGizmos uses
        // half_size = 1.0 to scale a plane-local arrow tip at z = 1.
        // Mirror that here.
        if (!projectWorldToLogicalScreen(vp, p.origin + p.n * 1.0f,
                                         w, h, s_tip)) continue;
        const QVector2D q{float(x), float(y)};
        const QVector2D ab = s_tip - s_origin;
        const float ab_len2 = ab.lengthSquared();
        if (ab_len2 < 1e-3f) continue;
        float t = QVector2D::dotProduct(q - s_origin, ab) / ab_len2;
        t = std::clamp(t, 0.0f, 1.0f);
        const QVector2D proj_pt = s_origin + ab * t;
        const float d2 = (q - proj_pt).lengthSquared();
        if (d2 < best_d2) { best_d2 = d2; best = i; }
    }
    return best;
}

void WgpuViewportWindow::updateSectionDrag(int x, int y) {
    if (!section_drag_active_) return;
    if (section_drag_index_ < 0
        || section_drag_index_ >= int(section_planes_.size())) return;
    WgpuSectionPlane& p = section_planes_[section_drag_index_];

    const int w = width();
    const int h = height();
    if (w <= 0 || h <= 0) return;
    QMatrix4x4 view, proj;
    buildViewProj(view, proj);
    const QMatrix4x4 vp = proj * view;

    // Re-project the press-time origin and origin + n to screen space.
    // The press-time origin is what `start` should be relative to — so the
    // plane slides smoothly even as the camera moves (we re-project every
    // frame to handle mid-drag camera rotation cleanly).
    QVector2D s_origin, s_n;
    if (!projectWorldToLogicalScreen(vp, section_drag_start_origin_,
                                     w, h, s_origin)) return;
    if (!projectWorldToLogicalScreen(vp, section_drag_start_origin_ + p.n,
                                     w, h, s_n)) return;
    const QVector2D screen_axis = s_n - s_origin;
    const float screen_axis_len2 = screen_axis.lengthSquared();
    if (screen_axis_len2 < 1e-3f) return;  // arrow is edge-on

    // Project pixel delta onto the screen-space axis; convert to metres
    // via (delta · axis) / |axis|² (axis is 1 m long in world space).
    const QVector2D delta_px(float(x - section_drag_start_mouse_.x()),
                             float(y - section_drag_start_mouse_.y()));
    const float meters = QVector2D::dotProduct(delta_px, screen_axis)
                         / screen_axis_len2;

    p.origin = section_drag_start_origin_ + p.n * meters;
    p.d      = -QVector3D::dotProduct(p.n, p.origin);
    requestUpdate();
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
            qInfo().noquote().nospace()
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

void WgpuViewportWindow::setBenchmarkFrames(int frames) {
    bench_total_    = std::max(0, frames);
    bench_count_    = 0;
    bench_yaw_start_ = camera_yaw_deg_;
    bench_warm_streak_       = 0;
    bench_warm_frames_total_ = 0;
    bench_frame_ms_.clear();
    bench_frame_ms_.reserve(size_t(bench_total_));
    if (isExposed() && bench_total_ > 0) requestUpdate();
}

uint32_t WgpuViewportWindow::cullModelCpuCompute(WgpuModelGpuData& m,
                                                 const float planes[6][4],
                                                 const float eye[3],
                                                 const float forward[3],
                                                 const float right[3],
                                                 const float up[3],
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
        c.frustum_visible_count  = 0;
        c.current_priority       = 0.0f;
    }

    // Per-chunk running vertex count (used to populate that chunk's prefix
    // sums incrementally). Kept on the stack to avoid heap churn for small
    // chunk counts.
    std::vector<uint32_t> running_vertex_count(m.chunks.size(), 0);

    // Per-instance work as a lambda — same logic regardless of how we
    // reached the instance (BVH walk leaf vs. flat linear scan). Keeps the
    // BVH path single-pass (no scratch buffer / no second iteration).
    auto process_instance = [&](uint32_t i) {
        const auto& inst = m.instances[i];
        if (inst.mesh_id >= m.meshes.size()) return;
        if (visibility_.isHidden(inst.object_id)) return;
        // Per-instance frustum still needed: a partially-covered subtree
        // descended this far means *some* leaves are visible, but not
        // necessarily this one.
        if (!aabbInFrustum(inst.world_aabb_min, inst.world_aabb_max, planes)) return;

        const uint32_t chunk_idx = m.instance_chunk_idx[i];
        WgpuModelGpuData::Chunk& c = m.chunks[chunk_idx];

        // Bump the chunk's frustum-only counter before contribution / HiZ.
        // Stable across frames when the camera doesn't move, so the
        // streaming loader doesn't thrash on HiZ visibility flicker.
        ++c.frustum_visible_count;

        const MeshInfo& mesh = m.meshes[inst.mesh_id];

        // Two screen-space metrics computed per instance:
        //
        //   projected_px  — sphere-radius projection. Cheap, conservative
        //                   (over-estimates). Used by the contribution
        //                   gate (`projected_px < min_radius_px`) and
        //                   LOD pick. Conservative-over is the right
        //                   failure mode there: we'd rather draw a tiny
        //                   sub-pixel sliver than wrongly skip it.
        //   box_area_px2  — AABB-rectangle projection. Tight. Used only
        //                   by the streaming priority accumulator. BIM
        //                   geometry is thin-in-one-axis (slabs, pipes,
        //                   columns, windows); a sphere bounding a flat
        //                   ocean plane over-states screen footprint by
        //                   100×+ when viewed edge-on, which made occluded
        //                   far geometry steal residency from close,
        //                   visible structural elements (e.g. bracing).
        //
        // We accumulate BEFORE contribution / HiZ rejection because
        // streaming asks "do we want this chunk's bytes resident", not
        // "do we draw it this frame".
        float projected_px = std::numeric_limits<float>::infinity();
        {
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

                // World-AABB half-extents projected onto camera right/up.
                // Each |basis · world_axis| term is the contribution of
                // that world axis to that screen axis (e.g. a horizontal
                // ocean plane's Z extent collapses to ~0 in screen-x when
                // viewed edge-on).
                const float hex = 0.5f * ex;
                const float hey = 0.5f * ey;
                const float hez = 0.5f * ez;
                const float view_he_x = std::fabs(right[0]) * hex
                                      + std::fabs(right[1]) * hey
                                      + std::fabs(right[2]) * hez;
                const float view_he_y = std::fabs(up[0])    * hex
                                      + std::fabs(up[1])    * hey
                                      + std::fabs(up[2])    * hez;
                const float inv_z = focal_px / view_z;
                const float box_area_px2 = 4.0f
                                         * view_he_x * inv_z
                                         * view_he_y * inv_z;
                c.current_priority += box_area_px2;
            }
        }

        // Contribution cull before HiZ: HiZ is by far the most expensive
        // per-instance test (8-corner projection + mip pyramid sample), so
        // letting cheap contribution drops happen first cuts the HiZ-tested
        // population by ~5× on real scenes.
        if (contrib_enabled && projected_px < min_radius_px) return;

        if (hiz_enabled
            && aabbOccludedByHiz(inst.world_aabb_min, inst.world_aabb_max)) {
            ++hiz_rejects;
            return;
        }

        const bool use_lod1 = lod_enabled
                            && mesh.lod1_index_count > 0
                            && projected_px < lod1_threshold_px;

        // Emit one VisibleDraw entry into the chunk that owns this
        // instance's vertex range. base_vertex AND ebo_first_u32 are both
        // CHUNK-LOCAL — the chunk's bind group points at its own
        // vertex_storage and index_buffer slices so the shader indexes
        // them directly. When use_lod1, ebo_first_u32 routes into the LOD1
        // section of the chunk's index slice (which is packed after the
        // LOD0 section at chunk-build time); the shader is oblivious to
        // the LOD split. (chunk_idx and c were resolved at the top of
        // process_instance so the priority accumulator could reach the
        // chunk before contribution / HiZ rejected this instance.)
        WgpuModelGpuData::VisibleDrawGpu d;
        d.mesh_id       = inst.mesh_id;
        d.instance_idx  = i;
        d.ebo_first_u32 = use_lod1 ? m.instance_lod1_first_u32[i]
                                   : m.instance_ebo_first_u32[i];
        d.base_vertex   = m.instance_base_vertex[i];
        c.visible_draws_scratch.push_back(d);

        const uint32_t entry_vert_count = use_lod1 ? mesh.lod1_index_count
                                                   : mesh.index_count;
        running_vertex_count[chunk_idx] += entry_vert_count;
        c.prefix_sums_scratch.push_back(running_vertex_count[chunk_idx]);
        if (use_lod1) {
            ++lod1_dbg_count_;
            lod1_dbg_tris_saved_ += (mesh.index_count > mesh.lod1_index_count
                                     ? (mesh.index_count - mesh.lod1_index_count) / 3
                                     : 0);
        } else if (mesh.lod1_index_count > 0) {
            ++lod0_dbg_eligible_count_;
        } else {
            ++lod0_dbg_no_lod1_count_;
        }
    };

    // Chunk-driven walk: frustum-test each chunk's AABB once, and skip
    // every instance inside in one shot when the chunk is off-screen.
    // With spatial chunk planning (~hundreds of tight per-chunk AABBs
    // per scene) this rejects most instances without ever touching them
    // individually — a strict superset of the previous BVH walk's win,
    // because the chunk partition is already a one-level spatial BVH
    // with zero traversal overhead. The per-model BVH built at load
    // time is now unused by cull; it stays around as dead weight until
    // the cleanup pass removes it.
    for (auto& c : m.chunks) {
        if (c.instance_ids.empty()) continue;
        if (!aabbInFrustum(c.aabb_min, c.aabb_max, planes)) continue;
        for (uint32_t i : c.instance_ids) process_instance(i);
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
    cull_timer.start();
    QMatrix4x4 vp_this_frame;
    {
        const QVector3D target(camera_target_[0], camera_target_[1], camera_target_[2]);
        const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                       camera_yaw_deg_, camera_pitch_deg_);
        QMatrix4x4 v, p;
        buildViewProj(v, p);
        const QMatrix4x4 vp = p * v;
        vp_this_frame = vp;
        float planes[6][4];
        extractFrustumPlanes(vp.constData(), planes);

        // LOD pick inputs: world-space eye, unit forward, vertical focal in
        // pixels. focal_px maps view-space depth to projected radius:
        //   projected_px = world_radius * focal_px / view_z.
        const QVector3D fwd_q = (target - eye).normalized();
        // World-up convention: Z-up. Near the poles lookAt degenerates,
        // so swap to Y-up — mirrors buildViewProj's pitch gate at line
        // 4701 so cull's camera basis matches the actual view matrix.
        const QVector3D world_up = (std::abs(camera_pitch_deg_) >= 89.0f)
                                     ? QVector3D(0.0f, 1.0f, 0.0f)
                                     : QVector3D(0.0f, 0.0f, 1.0f);
        const QVector3D right_q  = QVector3D::crossProduct(fwd_q, world_up).normalized();
        const QVector3D up_q     = QVector3D::crossProduct(right_q, fwd_q).normalized();
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
            qInfo().noquote().nospace()
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
                qInfo().noquote().nospace()
                    << "[hiz trace] pyramid row " << y << " (8 samples): " << row;
            }
        } else if (hiz_trace_on) {
            hiz_trace_budget_.store(0, std::memory_order_relaxed);
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
                     focal_px, effective_min_px, hiz_for_this_frame]() {
                        return cullModelCpuCompute(
                            m_ref, planes, eye_a, fwd_a, right_a, up_a,
                            focal_px,
                            effective_min_px, lod1_pixel_threshold_,
                            hiz_for_this_frame);
                    }));
            }
            for (auto& [mid, fut] : futures) {
                hiz_reject_count_ += fut.get();
            }
        } else {
            for (auto& [mid, m] : models_gpu_) {
                if (m.hidden) continue;
                hiz_reject_count_ += cullModelCpuCompute(
                    m, planes, eye_a, fwd_a, right_a, up_a, focal_px,
                    effective_min_px, lod1_pixel_threshold_,
                    hiz_for_this_frame);
            }
        }

        // Split timer: how much of the "cull" cost is the upload phase
        // (sequential queueWriteBuffer × 3 per resident chunk × ~120
        // chunks ≈ 360 wgpu calls/frame). If upload >> compute the parallel
        // cull is doing its job and the bottleneck is somewhere else.
        const double cull_compute_ms = double(cull_timer.nsecsElapsed()) / 1e6;
        QElapsedTimer upload_timer;
        upload_timer.start();
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
    QElapsedTimer stream_timer;
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

    // Snapshot the per-frame inputs every overlay needs. Built once and
    // passed by const-ref so WgpuOverlayRenderer never reaches back into
    // this viewport.
    WgpuOverlayFrame overlay_frame;
    overlay_frame.view_proj          = vp_this_frame;
    overlay_frame.camera_target      = QVector3D(camera_target_[0],
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

    // Pivot indicator. Encoded inside the main MSAA pass after geometry so
    // depth interaction is correct — the indicator vanishes behind closer
    // surfaces. Visibility is driven by orbit/wheel UI handlers.
    overlays_.encodePivot(pass, overlay_frame, pivot_indicator_visible_);

    // Overlay line groups (measurement / dimension annotation lines).
    // Depth-tested against geometry so they hide behind closer surfaces;
    // depth-write off so the corner gizmo + marquee can still draw over
    // them on the resolved surface afterwards.
    overlays_.encodeOverlayLines(pass, overlay_frame);

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
            qInfo().noquote().nospace()
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

            // Every ~120 frames, when something's missing, dump the
            // top-8 models by missing-chunk count + top/bottom chunks
            // by priority. The priorities settle the question: is the
            // metric correctly scoring the missing chunks lower than
            // residents, or is something else (bug, hysteresis, etc.)
            // preventing valid swaps?
            if (chunks_missing > 0 && (interactive_frame_count_ % 30) == 0) {
                // Build the camera VP matrix and project AABB corners
                // — same metric driveStreamingLoads uses for priority,
                // duplicated here so the heartbeat dump can show what
                // the loader is actually scoring chunks at.
                QMatrix4x4 v_dbg, p_dbg;
                buildViewProj(v_dbg, p_dbg);
                const QMatrix4x4 vp_dbg = p_dbg * v_dbg;
                auto chunk_priority_px2 = [&](const WgpuModelGpuData::Chunk& c) -> float {
                    if (configured_w_ <= 0 || configured_h_ <= 0 ||
                        c.aabb_min[0] > c.aabb_max[0]) return 0.0f;
                    float xmin =  std::numeric_limits<float>::infinity();
                    float ymin =  std::numeric_limits<float>::infinity();
                    float xmax = -std::numeric_limits<float>::infinity();
                    float ymax = -std::numeric_limits<float>::infinity();
                    int   cif  = 0;
                    for (int i = 0; i < 8; ++i) {
                        const QVector4D corner(
                            (i & 1) ? c.aabb_max[0] : c.aabb_min[0],
                            (i & 2) ? c.aabb_max[1] : c.aabb_min[1],
                            (i & 4) ? c.aabb_max[2] : c.aabb_min[2],
                            1.0f);
                        const QVector4D clip = vp_dbg * corner;
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
                qInfo().noquote() << "  [missing per model — top 8 by missing-count]";
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
                    qInfo().noquote().nospace()
                        << "    " << r.name
                        << "  resident=" << r.resident
                        << "  frustum=" << r.frustum
                        << "  missing=" << r.missing;
                }
                qInfo().noquote() << "  [top 20 MISSING chunks by priority (px², want these loaded)]";
                for (size_t i = 0; i < std::min<size_t>(20, missing_set.size()); ++i) {
                    const Probe& p = missing_set[i];
                    qInfo().noquote().nospace()
                        << "    pri=" << QString::number(p.priority, 'f', 0)
                        << "  aabb=" << QString::number(p.ex, 'f', 1) << "x"
                        << QString::number(p.ey, 'f', 1) << "x"
                        << QString::number(p.ez, 'f', 1) << "m"
                        << "  in " << p.name;
                }
                qInfo().noquote() << "  [bottom 5 RESIDENT chunks by effective priority (must beat with 2× hysteresis)]";
                for (size_t i = 0; i < std::min<size_t>(5, resident_set.size()); ++i) {
                    const Probe& p = resident_set[i];
                    const float eff = p.priority * std::max(p.history, 0.05f);
                    qInfo().noquote().nospace()
                        << "    pri=" << QString::number(p.priority, 'f', 0)
                        << " hist=" << QString::number(p.history, 'f', 2)
                        << " eff=" << QString::number(eff, 'f', 0)
                        << "  aabb=" << QString::number(p.ex, 'f', 1) << "x"
                        << QString::number(p.ey, 'f', 1) << "x"
                        << QString::number(p.ez, 'f', 1) << "m"
                        << "  in " << p.name;
                }
                // Dump every chunk of the bracing model so we can see
                // whether its priority is genuinely low (metric faithful)
                // or unexpectedly high (metric broken). Hardcoded model
                // name match is fine for this one-off investigation.
                qInfo().noquote() << "  [brace.ifc (bracing) all chunks]";
                for (const auto& [mid, mo] : models_gpu_) {
                    QFileInfo fi(QString::fromStdString(mo.streaming_file_path));
                    if (!fi.completeBaseName().contains(QStringLiteral("brace.ifc"))) continue;
                    for (size_t ci = 0; ci < mo.chunks.size(); ++ci) {
                        const auto& c = mo.chunks[ci];
                        const float pri = chunk_priority_px2(c);
                        qInfo().noquote().nospace()
                            << "    chunk " << ci
                            << "  pri=" << QString::number(pri, 'f', 0) << "px²"
                            << "  resident=" << (c.is_resident ? "Y" : "N")
                            << "  loading=" << (c.is_loading  ? "Y" : "N")
                            << "  frustum=" << c.frustum_visible_count
                            << "  hist=" << QString::number(c.visibility_history, 'f', 2)
                            << "  aabb=" << QString::number(c.aabb_max[0]-c.aabb_min[0], 'f', 1) << "x"
                            << QString::number(c.aabb_max[1]-c.aabb_min[1], 'f', 1) << "x"
                            << QString::number(c.aabb_max[2]-c.aabb_min[2], 'f', 1) << "m"
                            << "  centre=("
                            << QString::number(0.5f*(c.aabb_min[0]+c.aabb_max[0]), 'f', 1) << ","
                            << QString::number(0.5f*(c.aabb_min[1]+c.aabb_max[1]), 'f', 1) << ","
                            << QString::number(0.5f*(c.aabb_min[2]+c.aabb_max[2]), 'f', 1) << ")";
                    }
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
                qInfo().noquote().nospace()
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
                qWarning().noquote().nospace()
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
            qInfo().noquote().nospace()
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
                << "  stream=" << bench_stream_ms_total_ / n
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
    if (!m.mesh_storage || !m.instance_storage) {
        // Empty model — no chunks, no bind groups; the draw loop will skip.
        return;
    }
    for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
        buildChunkBindGroup(m, ci);
    }
}

void WgpuViewportWindow::buildChunkBindGroup(WgpuModelGpuData& m, size_t chunk_idx) {
    if (chunk_idx >= m.chunks.size()) return;
    auto& c = m.chunks[chunk_idx];
    if (c.bind_group) {
        wgpuBindGroupRelease(c.bind_group);
        c.bind_group = nullptr;
    }
    if (!c.vertex_slice.valid() || !c.index_slice.valid()
        || !c.visible_draws_buffer || !c.prefix_sums_buffer || !c.per_chunk_uniform
        || !m.mesh_storage || !m.instance_storage) {
        return;
    }

    WGPUBindGroupEntry entries[7] = {};
    // vertices and indices live in the shared pool. Each slice carries
    // the specific sub-buffer it landed in (the pool may span several
    // when scenes exceed wgpu's single-buffer cap). The other entries
    // are still per-chunk small buffers (visible_draws/prefix_sums/uniform)
    // or per-model (mesh/instance).
    entries[0].binding = 0;
    entries[0].buffer  = c.vertex_slice.buffer;
    entries[0].offset  = c.vertex_slice.offset;
    entries[0].size    = c.vertex_slice.size;
    entries[1].binding = 1;
    entries[1].buffer  = m.mesh_storage;
    entries[1].size    = WGPU_WHOLE_SIZE;
    entries[2].binding = 2;
    entries[2].buffer  = m.instance_storage;
    entries[2].size    = WGPU_WHOLE_SIZE;
    entries[3].binding = 3;
    entries[3].buffer  = c.index_slice.buffer;
    entries[3].offset  = c.index_slice.offset;
    entries[3].size    = c.index_slice.size;
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

// Build the worker request for a chunk. Walks the chunk's mesh_ids and
// derives scatter-gather byte/index ranges from each mesh's sidecar
// offsets. Pure function of model + chunk metadata; safe to call from
// the main thread.
static WgpuStreamingThread::Request makeChunkRequest(
        const WgpuModelGpuData& m, size_t chunk_idx, uint32_t model_id) {
    const auto& c = m.chunks[chunk_idx];
    WgpuStreamingThread::Request req;
    req.model_id              = model_id;
    req.chunk_idx             = chunk_idx;
    req.file_path             = m.streaming_file_path;
    req.vertex_section_offset = m.streaming_vertex_section_offset;
    req.index_section_offset  = m.streaming_index_section_offset;
    req.v_ranges.reserve(c.mesh_ids.size());
    req.i_ranges.reserve(c.mesh_ids.size());
    for (uint32_t mi : c.mesh_ids) {
        const MeshInfo& mesh = m.meshes[mi];
        const uint64_t v_bytes = uint64_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        if (v_bytes > 0) {
            req.v_ranges.emplace_back(uint64_t(mesh.vbo_byte_offset), v_bytes);
        }
        if (mesh.index_count > 0) {
            req.i_ranges.emplace_back(
                uint64_t(mesh.ebo_byte_offset / sizeof(uint32_t)),
                uint64_t(mesh.index_count));
        }
    }
    // LOD1 indices second pass — matches the chunk-local packing order
    // (all LOD0 first, then LOD1) so the worker's concatenated index
    // result lands at the offsets recorded in
    // m.mesh_chunk_local_lod1_first_u32.
    for (uint32_t mi : c.mesh_ids) {
        const MeshInfo& mesh = m.meshes[mi];
        if (mesh.lod1_index_count == 0) continue;
        req.i_ranges.emplace_back(
            uint64_t(mesh.lod1_ebo_byte_offset / sizeof(uint32_t)),
            uint64_t(mesh.lod1_index_count));
    }
    return req;
}

// Apply a streamed chunk's bytes to the GPU: pool-allocate vertex +
// index slices, queueWriteBuffer the bytes, build the bind group, flip
// is_resident=true. Returns false on pool OOM (caller should have made
// room first); on failure, no slices are claimed and is_resident
// stays false. Called both from the worker-result drain (async) and
// from loadChunkBytesAndUploadGpu (sync first-frame fallback).
bool WgpuViewportWindow::applyStreamedChunk(
        WgpuModelGpuData& m, size_t chunk_idx,
        const std::vector<uint8_t>& vbytes,
        const std::vector<uint32_t>& idx) {
    auto& c = m.chunks[chunk_idx];

    c.vertex_slice = pool_.alloc(vbytes.size(), 256);
    if (!c.vertex_slice.valid()) return false;
    wgpuQueueWriteBuffer(queue_, c.vertex_slice.buffer,
                         c.vertex_slice.offset,
                         vbytes.data(), vbytes.size());
    m.vram_bytes_vbo += vbytes.size();

    if (!idx.empty()) {
        const size_t ibytes = idx.size() * sizeof(uint32_t);
        c.index_slice = pool_.alloc(ibytes, 256);
        if (!c.index_slice.valid()) {
            pool_.free(c.vertex_slice);
            m.vram_bytes_vbo -= c.vertex_slice.size;
            c.vertex_slice = {};
            return false;
        }
        wgpuQueueWriteBuffer(queue_, c.index_slice.buffer,
                             c.index_slice.offset,
                             idx.data(), ibytes);
        m.vram_bytes_ebo += ibytes;
    }

    buildChunkBindGroup(m, chunk_idx);
    c.is_resident      = true;
    c.is_loading       = false;
    c.loaded_frame_idx = streaming_frame_idx_;
    return true;
}

bool WgpuViewportWindow::loadChunkBytesAndUploadGpu(WgpuModelGpuData& m, size_t chunk_idx) {
    if (chunk_idx >= m.chunks.size()) return false;
    auto& c = m.chunks[chunk_idx];
    if (c.is_resident) return true;
    if (m.streaming_file_path.empty()) return false;

    // Synchronous fallback: build the request, do the disk read inline,
    // apply. Used only when the async path can't be — i.e. by the
    // screenshot test on first frame. Normal streaming goes through
    // driveStreamingLoads → streaming_thread_.
    WgpuStreamingThread::Request req = makeChunkRequest(m, chunk_idx, /*mid*/ 0);
    std::vector<uint8_t>  vbytes;
    std::vector<uint32_t> idx;
    if (!req.v_ranges.empty()) {
        if (!readSidecarVertexRanges(req.file_path,
                                     req.vertex_section_offset,
                                     req.v_ranges, vbytes)) {
            qWarning().noquote().nospace()
                << "[wgpu stream] failed to read vertex chunk " << chunk_idx
                << " (" << req.v_ranges.size() << " ranges, total "
                << c.vertex_byte_size << " B)";
            return false;
        }
    }
    if (!req.i_ranges.empty()) {
        if (!readSidecarIndexRanges(req.file_path,
                                    req.index_section_offset,
                                    req.i_ranges, idx)) {
            qWarning().noquote().nospace()
                << "[wgpu stream] failed to read index chunk " << chunk_idx
                << " (" << req.i_ranges.size() << " ranges, total "
                << c.index_count << " indices)";
            return false;
        }
    }
    return applyStreamedChunk(m, chunk_idx, vbytes, idx);
}

void WgpuViewportWindow::unloadChunk(WgpuModelGpuData& m, size_t chunk_idx) {
    if (chunk_idx >= m.chunks.size()) return;
    auto& c = m.chunks[chunk_idx];
    if (!c.is_resident) return;

    if (c.bind_group) {
        wgpuBindGroupRelease(c.bind_group);
        c.bind_group = nullptr;
    }
    if (c.vertex_slice.valid()) {
        m.vram_bytes_vbo -= c.vertex_slice.size;
        pool_.free(c.vertex_slice);
        c.vertex_slice = {};
    }
    if (c.index_slice.valid()) {
        m.vram_bytes_ebo -= c.index_slice.size;
        pool_.free(c.index_slice);
        c.index_slice = {};
    }
    // Clear per-frame visibility so the chunk doesn't get re-rendered or
    // re-evicted on the same frame; cull will set it again next time
    // the chunk falls in the frustum.
    c.total_visible_draws    = 0;
    c.total_visible_vertices = 0;
    c.is_resident = false;
}

void WgpuViewportWindow::driveStreamingLoads() {
    // Bump LRU clock once per call. Resident-and-visible chunks get
    // stamped with this value below; the evictor uses it to find the
    // least-recently-visible non-visible resident chunk.
    ++streaming_frame_idx_;

    // Refresh per-chunk frame state. (a) LRU stamp on frustum-visible
    // residents (HiZ flicker can't un-stamp them; cull-with-HiZ would
    // thrash the LRU). (b) EMA-smoothed visibility_history: how often
    // the chunk has *actually* contributed pixels (post-HiZ) over the
    // last ~30 frames. The two metrics serve different jobs — LRU
    // distinguishes "out of view" from "in view", history distinguishes
    // "in view AND not occluded" from "in view BUT mostly occluded".
    constexpr float HISTORY_ALPHA = 1.0f / 30.0f;
    for (auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (auto& c : m.chunks) {
            if (c.is_resident && c.frustum_visible_count > 0) {
                c.last_visible_frame_idx = streaming_frame_idx_;
            }
            const float current = (c.total_visible_draws > 0) ? 1.0f : 0.0f;
            c.visibility_history =
                c.visibility_history * (1.0f - HISTORY_ALPHA)
              + current * HISTORY_ALPHA;
        }
    }

    // Build the camera's view-projection (still needed for the AABB-based
    // diagnostic dump in the tracking output below). Cull/render use the
    // same helper.
    QMatrix4x4 v_mat, p_mat;
    buildViewProj(v_mat, p_mat);
    const QMatrix4x4 vp_mat = p_mat * v_mat;

    // chunk.current_priority was accumulated during cullModelCpuCompute
    // (one add per frustum-passing instance). No standalone walk needed
    // here; the candidate/resident priority lambdas just read it.
    auto chunk_screen_area_px = [&](const WgpuModelGpuData::Chunk& c) -> float {
        return c.current_priority;
    };

    // Resident chunks: contribution × visibility_history (floored), so
    // chunks that don't actually render lose priority over time and
    // become evictable. Candidates: pure contribution — best-case
    // estimate. Asymmetry lets new high-contribution chunks displace
    // long-resident-but-occluded ones.
    //
    // CRITICAL: newly-loaded chunks get a "grace period" of GRACE_FRAMES
    // at the full max-history factor. Without it, a freshly-loaded
    // chunk's effective priority crashes to contribution × 0.05 next
    // frame (history hasn't had time to develop), and the chunk it
    // displaced — back as a candidate at full priority — re-displaces
    // it. Infinite reverse-swap between equal-priority chunks. The
    // cycle starves the per-frame load budget (MAX_STREAMING_LOADS = 4)
    // so candidates ranked below the cyclers (e.g. brace chunks at
    // priority position 20) never get attempted. Grace period gives
    // visibility_history time to settle and breaks the cycle.
    constexpr float    HISTORY_FLOOR = 0.05f;
    constexpr uint64_t GRACE_FRAMES  = 30;
    auto resident_priority = [&](const WgpuModelGpuData::Chunk& c) -> float {
        const uint64_t age = streaming_frame_idx_ - c.loaded_frame_idx;
        const float vis = (age < GRACE_FRAMES)
            ? 1.0f
            : std::max(c.visibility_history, HISTORY_FLOOR);
        return chunk_screen_area_px(c) * vis;
    };
    auto candidate_priority = [&](const WgpuModelGpuData::Chunk& c) -> float {
        return chunk_screen_area_px(c);
    };

    // Per-frame load budget. Caps first-frame stall on a fresh load — at
    // 4 chunks/frame × 60fps we ingest 240 chunks/sec, fast enough that
    // a 100-model scene fully resides in ~1s. The hard ceiling on total
    // residency is the pool capacity (probed at startup); when the pool
    // can't fit a candidate, the evictors below free closer-fitting
    // ranges until it does.
    constexpr int MAX_STREAMING_LOADS_PER_FRAME = 4;
    int loads = 0;
    bool more_pending = false;

    // Reset per-frame counters used by WGPU_STREAM_DEBUG output.
    streaming_candidates_this_frame_    = 0;
    streaming_evictions_lru_this_frame_ = 0;
    streaming_evictions_pri_this_frame_ = 0;
    streaming_drained_this_frame_       = 0;
    streaming_blocked_oom_this_frame_   = 0;

    // The pool needs `need` contiguous bytes free for both the vertex and
    // index allocations a load requires. Fragmentation matters: a chunk
    // may fit total-free-bytes but not largest_free_run_bytes(). With
    // multi-sub-buffer pools, an alloc can also succeed by growing the
    // pool (adding a new sub-buffer at per_sub_buffer_capacity_bytes()),
    // so a chunk also "fits" if it's smaller than one fresh sub-buffer.
    // The actual alloc handles the growth attempt; this predicate only
    // avoids wasted evict-then-fail loops.
    auto pool_can_fit = [&](uint64_t bytes) -> bool {
        if (pool_.largest_free_run_bytes() >= bytes) return true;
        // Growth might still rescue us. Use next_growth_size_bytes()
        // rather than per_sub_buffer_capacity_bytes() — after a refusal
        // at e.g. 2 GB, halve-on-failure pushes the next achievable
        // sub-buffer down to 1 GB; saying "fits if ≤2 GB" would lie.
        if (pool_.can_grow() && pool_.next_growth_size_bytes() >= bytes) return true;
        return false;
    };

    // Phase-1 evictor: drop the LRU non-visible resident chunk. Skips
    // chunks stamped on streaming_frame_idx_ to avoid yanking what cull
    // just marked visible. Returns true iff a chunk was evicted.
    auto evict_one_lru = [&]() -> bool {
        WgpuModelGpuData* victim_m = nullptr;
        size_t            victim_ci = 0;
        uint64_t          victim_lru = std::numeric_limits<uint64_t>::max();
        for (auto& [mid, m] : models_gpu_) {
            for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
                auto& c = m.chunks[ci];
                if (!c.is_resident) continue;
                if (c.last_visible_frame_idx == streaming_frame_idx_) continue;
                if (c.last_visible_frame_idx < victim_lru) {
                    victim_lru = c.last_visible_frame_idx;
                    victim_m   = &m;
                    victim_ci  = ci;
                }
            }
        }
        if (!victim_m) return false;
        unloadChunk(*victim_m, victim_ci);
        ++streaming_evictions_lru_this_frame_;
        return true;
    };

    // Phase-2 evictor: when every resident chunk is visible-this-frame
    // but we still need room for a higher-priority candidate, drop the
    // resident with the lowest priority (contribution × history) —
    // provided the candidate's contribution is meaningfully bigger.
    // 2.0× hysteresis: candidate must have 2× more pixel area than the
    // victim's effective priority. In linear-radius terms that's a
    // ~41% gap, which is what stops 5 m vs 7 m chunks from oscillating.
    // Area metric is much more discriminating than radius, so we can
    // afford a bigger gap and still leave room for genuine swaps.
    constexpr float EVICT_PRIORITY_RATIO = 2.0f;
    auto evict_lowest_priority_than = [&](float cand_priority) -> bool {
        const float threshold = cand_priority / EVICT_PRIORITY_RATIO;
        WgpuModelGpuData* victim_m = nullptr;
        size_t            victim_ci = 0;
        float             victim_priority = threshold;
        for (auto& [mid, m] : models_gpu_) {
            for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
                auto& c = m.chunks[ci];
                if (!c.is_resident) continue;
                const float p = resident_priority(c);
                if (p < victim_priority) {
                    victim_priority = p;
                    victim_m        = &m;
                    victim_ci       = ci;
                }
            }
        }
        if (!victim_m) return false;
        unloadChunk(*victim_m, victim_ci);
        ++streaming_evictions_pri_this_frame_;
        return true;
    };

    // ---- Drain worker results -------------------------------------------
    // Apply any chunk reads that the streaming thread finished since
    // last frame. Each apply does pool.alloc + queueWriteBuffer + bind
    // group build — strictly main-thread work because wgpu queue ops
    // are not thread-safe. Counts toward loads_this_frame for the
    // bench warm gate's "settled" check.
    {
        auto results = streaming_thread_.drainResults();
        for (auto& res : results) {
            auto it = models_gpu_.find(res.model_id);
            if (it == models_gpu_.end()) continue;  // model unloaded
            auto& m = it->second;
            if (res.chunk_idx >= m.chunks.size()) continue;
            auto& c = m.chunks[res.chunk_idx];
            // The chunk may have been "unloaded" mid-flight (it wasn't
            // resident yet — eviction only acts on residents — but the
            // loader could have re-enqueued or the model could have
            // been hidden). Clear the loading flag regardless.
            c.is_loading = false;
            if (!res.success) {
                qWarning().noquote().nospace()
                    << "[wgpu stream] worker read failed for model "
                    << res.model_id << " chunk " << res.chunk_idx;
                continue;
            }
            if (!applyStreamedChunk(m, res.chunk_idx, res.vbytes, res.idx)) {
                // Pool OOM at apply time — eviction had freed less than
                // we needed by the time the result returned. Next frame's
                // loader will re-enqueue if still wanted.
                continue;
            }
            ++loads;
            ++streaming_drained_this_frame_;
            ++c.load_count;
            c.last_visible_frame_idx = streaming_frame_idx_;
        }
    }

    // ---- Enqueue new requests -------------------------------------------
    // Gather non-resident, !is_loading, frustum-visible chunks; sort by
    // candidate priority (contribution_px) DESCENDING so the biggest
    // screen-coverage chunks load first. Each enqueue makes room in
    // the pool by evicting low-priority residents (contribution ×
    // visibility_history); apply's alloc is best-effort.
    struct Candidate { WgpuModelGpuData* m; size_t ci; uint32_t mid; float priority; };
    std::vector<Candidate> candidates;
    candidates.reserve(64);
    for (auto& [mid, m] : models_gpu_) {
        if (m.streaming_file_path.empty() || m.hidden) continue;
        for (size_t ci = 0; ci < m.chunks.size(); ++ci) {
            auto& c = m.chunks[ci];
            if (c.is_resident)                       continue;
            if (c.is_loading)                        continue;
            if (c.frustum_visible_count == 0)        continue;
            candidates.push_back({&m, ci, mid, candidate_priority(c)});
        }
    }
    streaming_candidates_this_frame_ = int(candidates.size());
    std::sort(candidates.begin(), candidates.end(),
              [](const Candidate& a, const Candidate& b) {
                  return a.priority > b.priority;  // biggest first
              });

    int enqueued = 0;
    for (const Candidate& cand : candidates) {
        if (enqueued >= MAX_STREAMING_LOADS_PER_FRAME) {
            more_pending = true;
            break;
        }
        auto& c = cand.m->chunks[cand.ci];

        const uint64_t need = c.vertex_byte_size
                            + c.index_count * sizeof(uint32_t);
        while (!pool_can_fit(c.vertex_byte_size)
               || (c.index_count > 0
                   && !pool_can_fit(c.index_count * sizeof(uint32_t)))
               || pool_.total_free_bytes() < need) {
            if (evict_one_lru())                                       continue;
            if (evict_lowest_priority_than(cand.priority))             continue;
            break;
        }
        if (!pool_can_fit(c.vertex_byte_size)
            || (c.index_count > 0
                && !pool_can_fit(c.index_count * sizeof(uint32_t)))) {
            // Sorted-by-priority: every remaining candidate has equal
            // or lower priority, so eviction won't succeed for them either.
            ++streaming_blocked_oom_this_frame_;
            more_pending = true;
            break;
        }

        // Sync fallback when a screenshot is pending: the deferred-capture
        // wait would let the window manager re-layout the window while we
        // wait, capturing at the wrong size. With sync loads the chunk
        // appears in the same frame we enqueue, no deferred-state to manage.
        if (!pending_screenshot_path_.isEmpty()) {
            if (loadChunkBytesAndUploadGpu(*cand.m, cand.ci)) {
                ++enqueued;
                c.last_visible_frame_idx = streaming_frame_idx_;
            }
            continue;
        }

        if (streaming_thread_.enqueue(makeChunkRequest(*cand.m, cand.ci, cand.mid))) {
            c.is_loading = true;
            ++enqueued;
        }
    }
    loads += enqueued;
    // Keep the frame loop running while we're making progress or there
    // are worker reads still in flight. When everything's quiet
    // (no main-thread work this frame AND worker queue empty) we let
    // the renderer idle until the camera moves or a model loads.
    // Spinning otherwise would burn CPU forever on visible-set >
    // pool-capacity scenes.
    if (loads > 0 || streaming_thread_.inFlightApprox() > 0) requestUpdate();

    // Surface per-frame activity for the bench harness to gate the
    // orbit sweep against cold-load. We only export loads — more_pending
    // can stay true forever in the can't-fit case and is not a "done"
    // signal.
    streaming_loads_this_frame_ = loads;
    streaming_more_pending_     = more_pending;

    // Click-and-track diagnostic. When the user picked an object, we noted
    // which chunk holds it. If that chunk has just transitioned resident
    // → evicted, dump the priority + pool state at the moment of loss so
    // we can see WHY it lost (was the new candidate higher priority? did
    // the pool fail to fit anyone? did frustum visibility just go to 0?).
    if (tracked_chunk_idx_ != SIZE_MAX) {
        auto it = models_gpu_.find(tracked_chunk_mid_);
        if (it != models_gpu_.end()
            && tracked_chunk_idx_ < it->second.chunks.size()) {
            const auto& m = it->second;
            const auto& c = m.chunks[tracked_chunk_idx_];
            if (tracked_was_resident_ && !c.is_resident) {
                const double mb = 1.0 / (1024.0 * 1024.0);
                const float my_area  = chunkScreenAreaPx(c, vp_mat);
                const uint64_t my_bytes = c.vertex_byte_size
                                        + c.index_count * sizeof(uint32_t);
                qInfo().noquote().nospace()
                    << "[track] chunk " << tracked_chunk_idx_
                    << " (object " << tracked_object_id_
                    << ", model " << tracked_chunk_mid_
                    << ") EVICTED this frame";
                qInfo().noquote().nospace()
                    << "  area=" << QString::number(my_area, 'f', 0) << "px²"
                    << " frustum_vis=" << c.frustum_visible_count
                    << " hist=" << QString::number(c.visibility_history, 'f', 2)
                    << " load_count=" << c.load_count
                    << " size=" << QString::number(double(my_bytes) * mb, 'f', 1) << "MB";
                qInfo().noquote().nospace()
                    << "  chunk aabb "
                    << QString::number(c.aabb_max[0] - c.aabb_min[0], 'f', 1) << "×"
                    << QString::number(c.aabb_max[1] - c.aabb_min[1], 'f', 1) << "×"
                    << QString::number(c.aabb_max[2] - c.aabb_min[2], 'f', 1) << "m"
                    << " centre=("
                    << QString::number(0.5f * (c.aabb_min[0] + c.aabb_max[0]), 'f', 1) << ","
                    << QString::number(0.5f * (c.aabb_min[1] + c.aabb_max[1]), 'f', 1) << ","
                    << QString::number(0.5f * (c.aabb_min[2] + c.aabb_max[2]), 'f', 1) << ")";
                qInfo().noquote().nospace()
                    << "  pool used="
                    << QString::number(double(pool_.total_used_bytes()) * mb, 'f', 0)
                    << "/"
                    << QString::number(double(pool_.total_capacity_bytes()) * mb, 'f', 0)
                    << "MB largest_free="
                    << QString::number(double(pool_.largest_free_run_bytes()) * mb, 'f', 1) << "MB";
                qInfo().noquote().nospace()
                    << "  this-frame: cands=" << streaming_candidates_this_frame_
                    << " enq=" << enqueued
                    << " ev_lru=" << streaming_evictions_lru_this_frame_
                    << " ev_pri=" << streaming_evictions_pri_this_frame_
                    << " blocked=" << streaming_blocked_oom_this_frame_;

                // Top 5 candidates by priority — see which chunk(s) outscored ours.
                struct Stat { uint32_t mid; size_t ci; float area; };
                std::vector<Stat> all;
                all.reserve(64);
                for (const auto& [mid2, m2] : models_gpu_) {
                    for (size_t ci2 = 0; ci2 < m2.chunks.size(); ++ci2) {
                        const auto& cc = m2.chunks[ci2];
                        if (cc.is_resident)                continue;
                        if (cc.frustum_visible_count == 0) continue;
                        all.push_back({mid2, ci2, chunkScreenAreaPx(cc, vp_mat)});
                    }
                }
                std::sort(all.begin(), all.end(),
                          [](const Stat& a, const Stat& b){ return a.area > b.area; });
                const size_t n = std::min<size_t>(5, all.size());
                for (size_t i = 0; i < n; ++i) {
                    qInfo().noquote().nospace()
                        << "  top cand #" << i << ": model " << all[i].mid
                        << " chunk " << all[i].ci
                        << " area=" << QString::number(all[i].area, 'f', 0) << "px²";
                }
            }
            tracked_was_resident_ = c.is_resident;
        }
    }

    if (streaming_debug_) {
        // Cheap per-frame breakdown so a thrash cycle's shape becomes
        // visible — high candidates + high evictions + low net loads is
        // the smoking gun for "working set > pool".
        size_t resident = 0;
        uint32_t max_load_count = 0;
        size_t   cycled = 0;          // chunks loaded > 1 time this session
        for (const auto& [mid, m] : models_gpu_) {
            for (const auto& c : m.chunks) {
                if (c.is_resident) ++resident;
                if (c.load_count > max_load_count) max_load_count = c.load_count;
                if (c.load_count > 1) ++cycled;
            }
        }
        qInfo().noquote().nospace()
            << "[stream-debug] f" << streaming_frame_idx_
            << " cands=" << streaming_candidates_this_frame_
            << " enq=" << enqueued
            << " drained=" << streaming_drained_this_frame_
            << " ev_lru=" << streaming_evictions_lru_this_frame_
            << " ev_pri=" << streaming_evictions_pri_this_frame_
            << " blocked=" << streaming_blocked_oom_this_frame_
            << " resident=" << resident
            << " cycled=" << cycled
            << " max_load=" << max_load_count;
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

// Shared camera-math helper. Every site that needs (view, proj) for cull,
// streaming projection, pick, or render uniforms calls this so the
// projection_ortho_ toggle and the near-vertical up-vector switch land
// identically everywhere.
void WgpuViewportWindow::buildViewProj(QMatrix4x4& view_out,
                                        QMatrix4x4& proj_out) const {
    const QVector3D target(camera_target_[0], camera_target_[1], camera_target_[2]);
    const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                   camera_yaw_deg_, camera_pitch_deg_);
    // Within 1° of straight-up/down, switch up from world +Z to world +Y
    // so lookAt's side vector doesn't degenerate (forward × up → 0). Mirrors
    // GL ViewportWindow::updateCamera; the standard-view top/bottom hotkeys
    // land at pitch = ±90° exactly so this is the path that keeps them
    // well-conditioned.
    const QVector3D up = (std::abs(camera_pitch_deg_) >= 89.0f)
                       ? QVector3D(0.0f, 1.0f, 0.0f)
                       : QVector3D(0.0f, 0.0f, 1.0f);
    view_out.setToIdentity();
    view_out.lookAt(eye, target, up);

    const float aspect = (configured_h_ > 0)
                            ? float(configured_w_) / float(configured_h_)
                            : 1.0f;
    QMatrix4x4 p;
    if (projection_ortho_) {
        // Size the ortho box so the same world rectangle fills the view as
        // the perspective camera at the pivot's distance. Toggling at any
        // zoom keeps framing identical. Mirrors GL.
        const float half_h = camera_distance_
            * std::tan(qDegreesToRadians(camera_fov_y_deg_ * 0.5f));
        const float half_w = half_h * aspect;
        const float depth  = camera_distance_ * 10.0f;
        p.ortho(-half_w, half_w, -half_h, half_h, -depth, depth);
    } else {
        p.perspective(camera_fov_y_deg_, aspect, camera_near_, camera_far_);
    }
    // Qt builds a GL-style projection (clip-z in [-1, 1]); WebGPU expects
    // clip-z in [0, 1]. Pre-multiply by a remap matrix that maps [-1,1] → [0,1].
    QMatrix4x4 z_remap;
    z_remap(2, 2) = 0.5f;
    z_remap(2, 3) = 0.5f;
    proj_out = z_remap * p;
}

void WgpuViewportWindow::updateFrameUniforms() {
    QMatrix4x4 view, proj;
    buildViewProj(view, proj);

    const QMatrix4x4 view_proj = proj * view;

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

    // Pack active section planes. `is_section_clipped` (WGSL) reads
    // u.clip_count and u.clip_planes[0..clip_count) and discards
    // fragments on the positive side.
    const int n = std::min<int>(int(section_planes_.size()), kMaxSectionPlanes);
    u.clip_count = n;
    for (int i = 0; i < n; ++i) {
        const WgpuSectionPlane& p = section_planes_[i];
        u.clip_planes[i][0] = p.n.x();
        u.clip_planes[i][1] = p.n.y();
        u.clip_planes[i][2] = p.n.z();
        u.clip_planes[i][3] = p.d;
    }

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

void WgpuViewportWindow::frameAabb(const float mn[3], const float mx[3],
                                    float padding) {
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
            camera_distance_ = std::max(0.1f, (radius / (tan_half * min_aspect)) * padding);
        }
    }
    if (isExposed()) requestUpdate();
}

bool WgpuViewportWindow::computeObjectAabb(uint32_t object_id,
                                            float mn[3], float mx[3]) const {
    bool any = false;
    for (int i = 0; i < 3; ++i) {
        mn[i] =  std::numeric_limits<float>::infinity();
        mx[i] = -std::numeric_limits<float>::infinity();
    }
    for (const auto& [mid, m] : models_gpu_) {
        for (const auto& inst : m.instances) {
            if (inst.object_id != object_id) continue;
            for (int i = 0; i < 3; ++i) {
                mn[i] = std::min(mn[i], inst.world_aabb_min[i]);
                mx[i] = std::max(mx[i], inst.world_aabb_max[i]);
            }
            any = true;
        }
    }
    return any;
}

void WgpuViewportWindow::focusOnSelectedObject() {
    if (fps_mode_) return;
    if (selection_.count() == 0) {
        qInfo() << "[wgpu] focus: no object selected";
        return;
    }
    float lo[3] = {  std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity() };
    float hi[3] = { -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity() };
    bool any = false;
    for (uint32_t id : selection_.ids()) {
        float mn[3], mx[3];
        if (!computeObjectAabb(id, mn, mx)) continue;
        for (int i = 0; i < 3; ++i) {
            lo[i] = std::min(lo[i], mn[i]);
            hi[i] = std::max(hi[i], mx[i]);
        }
        any = true;
    }
    if (!any) {
        qInfo() << "[wgpu] focus: no AABB available";
        return;
    }
    frameAabb(lo, hi, 1.30f);
}

void WgpuViewportWindow::setStandardView(float yaw_deg, float pitch_deg) {
    // Bypasses the orbit-pitch clamp so top/bottom land exactly at ±90°.
    // buildViewProj() picks the up vector based on |pitch| so lookAt stays
    // well-conditioned at the poles.
    camera_yaw_deg_   = yaw_deg;
    camera_pitch_deg_ = pitch_deg;
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::toggleProjection() {
    projection_ortho_ = !projection_ortho_;
    qInfo() << "[wgpu] projection:" << (projection_ortho_ ? "ortho" : "perspective");
    if (isExposed()) requestUpdate();
}

QString WgpuViewportWindow::cameraString() const {
    return QString("%1,%2,%3,%4,%5,%6")
        .arg(camera_target_[0], 0, 'f', 4)
        .arg(camera_target_[1], 0, 'f', 4)
        .arg(camera_target_[2], 0, 'f', 4)
        .arg(camera_distance_,  0, 'f', 4)
        .arg(camera_yaw_deg_,   0, 'f', 2)
        .arg(camera_pitch_deg_, 0, 'f', 2);
}

void WgpuViewportWindow::enterFpsMode() {
    if (fps_mode_) return;
    fps_mode_ = true;
    fps_keys_held_.clear();
    fps_press_center_ = QPoint(width() / 2, height() / 2);
    fps_ignore_next_mouse_move_ = true;
    fps_last_tick_.start();
    setCursor(Qt::BlankCursor);
    QCursor::setPos(mapToGlobal(fps_press_center_));
    qInfo() << "[wgpu] fly mode active — WASD/QE to move, Shift to boost, Esc to exit";
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::exitFpsMode() {
    if (!fps_mode_) return;
    fps_mode_ = false;
    fps_keys_held_.clear();
    setCursor(Qt::ArrowCursor);
    qInfo() << "[wgpu] fly mode off";
    if (isExposed()) requestUpdate();
}

void WgpuViewportWindow::fpsIntegrate() {
    if (!fps_mode_ || fps_keys_held_.isEmpty()) return;

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
    const QVector3D target(camera_target_[0], camera_target_[1], camera_target_[2]);
    const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                   camera_yaw_deg_, camera_pitch_deg_);
    QVector3D forward = (target - eye); forward.normalize();
    // When looking straight up/down, cross(forward, worldZ) degenerates;
    // fall back to worldY so right doesn't go NaN and WASD still works.
    const QVector3D world_up(0.0f, 0.0f, 1.0f);
    const QVector3D right_basis = (std::abs(camera_pitch_deg_) >= 89.0f)
                                ? QVector3D(0.0f, 1.0f, 0.0f)
                                : world_up;
    QVector3D right = QVector3D::crossProduct(forward, right_basis);
    right.normalize();

    QVector3D move(0, 0, 0);
    if (fps_keys_held_.contains(Qt::Key_W)) move += forward;
    if (fps_keys_held_.contains(Qt::Key_S)) move -= forward;
    if (fps_keys_held_.contains(Qt::Key_D)) move += right;
    if (fps_keys_held_.contains(Qt::Key_A)) move -= right;
    if (fps_keys_held_.contains(Qt::Key_E)) move += world_up;
    if (fps_keys_held_.contains(Qt::Key_Q)) move -= world_up;
    if (move.isNull()) return;
    move.normalize();

    // Absolute m/s, scrollwheel-adjustable (Blender / GL convention).
    // Scaling with camera_distance_ produced "stuttery" speed on big scenes
    // because distance varies frame-to-frame (and worse, wheel zoom kept
    // changing it underneath fly mode).
    const float speed = fps_move_speed_
                      * (fps_keys_held_.contains(Qt::Key_Shift) ? 5.0f : 1.0f);
    const QVector3D delta = move * (speed * dt);

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
        qInfo().noquote().nospace()
            << "[fly] dt=" << QString::number(dt * 1000.0f, 'f', 2) << "ms"
            << " render_gap=" << QString::number(double(since_render_ns) / 1e6, 'f', 2) << "ms"
            << " keys=" << fps_keys_held_.size()
            << " speed=" << QString::number(speed, 'f', 2) << "m/s"
            << " delta=" << QString::number(delta.length(), 'f', 4) << "m";
    }
}

float WgpuViewportWindow::chunkScreenAreaPx(const WgpuModelGpuData::Chunk& c,
                                             const QMatrix4x4& vp_mat) const {
    if (configured_w_ <= 0 || configured_h_ <= 0)   return 0.0f;
    if (c.aabb_min[0] > c.aabb_max[0])              return 0.0f;
    const float full_area = float(configured_w_) * float(configured_h_);

    // A chunk's AABB is the UNION of every instance's world AABB it
    // contains — typically much bigger than any single instance. On a
    // BIM floor plate it's commonly 200-400m on a side. With the camera
    // standing inside a building, that AABB straddles the near plane:
    // most corners sit behind the camera, the loop below silently drops
    // them, and the projected bbox of the surviving in-front corners is
    // a tiny fraction of what the chunk's actual on-screen geometry
    // covers. The chunk then loses every eviction fight against smaller
    // chunks whose AABBs sit entirely in front of the camera. Result:
    // big floor/slab chunks pop in/out as the camera tilts a few degrees.
    //
    // Two short-circuits stop that. Eye-inside-AABB → assume full
    // viewport (mirrors GL's contribution-cull short-circuit). Any
    // corner behind near plane (AABB straddles) → also full viewport;
    // the chunk's true on-screen extent is unmeasurable from 8 corners
    // alone once any are behind, so over-prioritise rather than
    // under-prioritise.
    const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                   camera_yaw_deg_, camera_pitch_deg_);
    if (eye.x() >= c.aabb_min[0] && eye.x() <= c.aabb_max[0] &&
        eye.y() >= c.aabb_min[1] && eye.y() <= c.aabb_max[1] &&
        eye.z() >= c.aabb_min[2] && eye.z() <= c.aabb_max[2]) {
        return full_area;
    }

    float xmin = std::numeric_limits<float>::infinity();
    float ymin = std::numeric_limits<float>::infinity();
    float xmax = -std::numeric_limits<float>::infinity();
    float ymax = -std::numeric_limits<float>::infinity();
    int corners_in_front = 0;
    int corners_behind   = 0;
    for (int i = 0; i < 8; ++i) {
        const QVector4D corner_world(
            (i & 1) ? c.aabb_max[0] : c.aabb_min[0],
            (i & 2) ? c.aabb_max[1] : c.aabb_min[1],
            (i & 4) ? c.aabb_max[2] : c.aabb_min[2],
            1.0f);
        const QVector4D clip = vp_mat * corner_world;
        if (clip.w() <= 1e-3f) { ++corners_behind; continue; }
        ++corners_in_front;
        const float ndc_x = clip.x() / clip.w();
        const float ndc_y = clip.y() / clip.w();
        const float px_x  = (ndc_x * 0.5f + 0.5f) * float(configured_w_);
        const float px_y  = (ndc_y * 0.5f + 0.5f) * float(configured_h_);
        xmin = std::min(xmin, px_x);
        ymin = std::min(ymin, px_y);
        xmax = std::max(xmax, px_x);
        ymax = std::max(ymax, px_y);
    }
    if (corners_in_front == 0) return 0.0f;
    if (corners_behind > 0)    return full_area;

    xmin = std::max(xmin, 0.0f);
    ymin = std::max(ymin, 0.0f);
    xmax = std::min(xmax, float(configured_w_));
    ymax = std::min(ymax, float(configured_h_));
    if (xmax <= xmin || ymax <= ymin) return 0.0f;
    return (xmax - xmin) * (ymax - ymin);
}

void WgpuViewportWindow::applyNavPreset(const char* name) {
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
    // In fly mode mouse-look is the only nav; clicking exits fly to match
    // Blender behaviour, then the click also acts as the orbit-mode click.
    if (fps_mode_) {
        exitFpsMode();
        // fall through to normal handling
    }

    nav_active_button_ = event->button();
    nav_last_pos_      = event->position().toPoint();
    nav_press_pos_     = nav_last_pos_;
    nav_dragged_       = false;

    // Section tool: claim a plain-LMB press if it lands on one of the
    // plane gizmos' arrows. Suppresses nav classification so the drag
    // doesn't also rotate the camera.
    if (section_tool_active_
        && event->button() == Qt::LeftButton
        && event->modifiers() == Qt::NoModifier) {
        const QPoint lp = event->position().toPoint();
        const int hit = hitTestSectionGizmo(lp.x(), lp.y());
        if (hit >= 0) {
            section_drag_active_       = true;
            section_drag_index_        = hit;
            section_drag_start_mouse_  = lp;
            section_drag_start_origin_ = section_planes_[hit].origin;
            nav_drag_kind_             = NavDrag::Inactive;
            qInfo().noquote().nospace()
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

void WgpuViewportWindow::mouseReleaseEvent(QMouseEvent* event) {
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
                qInfo().noquote().nospace()
                    << "[wgpu marquee] +add " << ids.size() << " object_ids";
            } else if (mods & Qt::ControlModifier) {
                for (uint32_t id : ids) selection_.remove(id);
                qInfo().noquote().nospace()
                    << "[wgpu marquee] -remove " << ids.size() << " object_ids";
            } else {
                selection_.clear();
                for (uint32_t id : ids) selection_.add(id);
                qInfo().noquote().nospace()
                    << "[wgpu marquee] replace " << ids.size() << " object_ids";
            }
            nav_active_button_ = Qt::NoButton;
            nav_drag_kind_     = NavDrag::Inactive;
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
            const QPoint pos = event->position().toPoint();
            const int px = int(pos.x() * devicePixelRatio());
            const int py = int(pos.y() * devicePixelRatio());

            // Section tool intercepts plain LMB clicks (with no modifier)
            // to drop a plane at the picked surface. Shift/Ctrl still go
            // through selection so the user can manipulate the existing
            // set while the tool is open.
            if (section_tool_active_
                && event->modifiers() == Qt::NoModifier) {
                uint32_t hit_id = 0;
                QVector3D hit_pos, hit_normal;
                float hit_radius = 0.0f;
                if (pickSurfaceAt(px, py, hit_id, hit_pos, hit_normal,
                                  &hit_radius)) {
                    // Pad the gizmo a bit beyond the AABB so the cut reads
                    // as a "cap" rather than ending right at the boundary.
                    addSectionPlaneAtSurface(hit_pos, hit_normal,
                                             hit_radius * 1.5f);
                } else {
                    qInfo().noquote() << "[wgpu section] click missed (no surface)";
                }
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
                qInfo().noquote().nospace()
                    << "[track] object " << id << " — enumerating chunks:";
                for (auto& [mid, m] : models_gpu_) {
                    for (const auto& inst : m.instances) {
                        if (inst.object_id != id) continue;
                        if (inst.mesh_id >= m.mesh_chunk_idx.size()) continue;
                        const size_t ci = m.mesh_chunk_idx[inst.mesh_id];
                        if (!seen.insert({mid, ci}).second) continue;
                        const auto& c = m.chunks[ci];
                        qInfo().noquote().nospace()
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
                    qInfo() << "  (object_id not matched to any instance)";
                }
            } else {
                tracked_object_id_ = 0;
                tracked_chunk_idx_ = SIZE_MAX;
            }
            requestUpdate();
        }
        nav_active_button_ = Qt::NoButton;
        nav_drag_kind_     = NavDrag::Inactive;
        // Drag is over — hide the pivot indicator without afterglow.
        setPivotIndicatorVisible(false);
    }
}

void WgpuViewportWindow::mouseMoveEvent(QMouseEvent* event) {
    // Section drag intercepts the move handler entirely: the orbit/pan
    // classification already declined this drag in mousePressEvent, so all
    // we have to do is slide the plane along its normal.
    if (section_drag_active_) {
        const QPoint pos = event->position().toPoint();
        updateSectionDrag(pos.x(), pos.y());
        return;
    }

    // Marquee box-select: track the current cursor and promote to active
    // once the press has moved past the manhattan threshold. Active
    // marquee triggers requestUpdate every frame the cursor moves so the
    // rect re-renders.
    if (box_select_armed_) {
        const QPoint pos = event->position().toPoint();
        box_select_current_pos_ = pos;
        if (!box_select_active_) {
            if ((pos - box_select_start_pos_).manhattanLength()
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
        const QPoint pos = event->position().toPoint();
        const int dx = pos.x() - fps_press_center_.x();
        const int dy = pos.y() - fps_press_center_.y();

        // Save eye BEFORE rotating so we can pin it after.
        const QVector3D pinned_eye = orbitEye(camera_target_, camera_distance_,
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
        QCursor::setPos(mapToGlobal(fps_press_center_));
        requestUpdate();
        return;
    }

    if (nav_active_button_ == Qt::NoButton) return;

    const QPoint pos = event->position().toPoint();
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
        const QVector3D target(camera_target_[0], camera_target_[1], camera_target_[2]);
        const QVector3D eye = orbitEye(camera_target_, camera_distance_,
                                       camera_yaw_deg_, camera_pitch_deg_);
        const QVector3D fwd   = (target - eye).normalized();
        const QVector3D world_up = (std::abs(camera_pitch_deg_) >= 89.0f)
                                 ? QVector3D(0.0f, 1.0f, 0.0f)
                                 : QVector3D(0.0f, 0.0f, 1.0f);
        const QVector3D right = QVector3D::crossProduct(fwd, world_up).normalized();
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
                const bool was_empty = fps_keys_held_.isEmpty();
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
        qInfo() << "[wgpu] show all";
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
        qInfo().noquote().nospace() << "[wgpu] isolated " << selection_.count()
                                    << " (hid " << hidden_now << " others)";
        requestUpdate();
        return;
    }
    if (key == Qt::Key_H && mods == Qt::NoModifier) {
        if (selection_.count() == 0) return;
        for (uint32_t id : selection_.ids()) visibility_.hide(id);
        const size_t n = selection_.count();
        selection_.clear();   // hiding deselects, matching GL behaviour
        qInfo().noquote().nospace() << "[wgpu] hid " << n << " selected";
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
        qInfo("--camera %s", qPrintable(cameraString()));
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

void WgpuViewportWindow::keyReleaseEvent(QKeyEvent* event) {
    if (fps_mode_ && !event->isAutoRepeat()) {
        fps_keys_held_.remove(event->key());
    }
    QWindow::keyReleaseEvent(event);
}

void WgpuViewportWindow::wheelEvent(QWheelEvent* event) {
    const float notches = float(event->angleDelta().y()) / 120.0f;
    // In fly mode, the wheel adjusts fps_move_speed_ (Blender / GL
    // convention). Up = faster (×1.25 per notch), down = slower (×0.8).
    // Zooming would re-aim the orbit pivot and yank speed (if it were
    // distance-scaled) — neither belongs in a free-fly camera.
    if (fps_mode_) {
        const float factor = std::pow(1.25f, notches);
        fps_move_speed_ = std::clamp(fps_move_speed_ * factor, 0.05f, 1000.0f);
        qInfo().noquote().nospace()
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

void WgpuViewportWindow::shutdown() {
    // Stop the streaming worker first so no late results land in the
    // pool after we've torn down the model state. Pending in-flight
    // reads are completed (worker drains its queue) then thread joins.
    streaming_thread_.stop();

    // Release per-model buffers before the device they were created from.
    for (auto& [mid, m] : models_gpu_) releaseWgpuModelGpuData(m, pool_);
    models_gpu_.clear();

    releaseDepthTexture();
    releaseMsaaColorTexture();
    releaseHizResources();
    releaseEdgeResources();
    overlays_.destroy();
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

    // Destroy the streaming pool while device_ is still alive (it owns
    // the underlying WGPUBuffer). All chunks have already returned their
    // ranges via releaseWgpuModelGpuData above; pool's free-list count
    // should equal capacity at this point.
    pool_.destroy();

    if (queue_)    { wgpuQueueRelease(queue_);       queue_    = nullptr; }
    if (device_)   { wgpuDeviceRelease(device_);     device_   = nullptr; }
    if (adapter_)  { wgpuAdapterRelease(adapter_);   adapter_  = nullptr; }
    if (surface_)  { wgpuSurfaceRelease(surface_);   surface_  = nullptr; }
    if (instance_) { wgpuInstanceRelease(instance_); instance_ = nullptr; }
    wgpu_initialized_   = false;
    surface_configured_ = false;
}
