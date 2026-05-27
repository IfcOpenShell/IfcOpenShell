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

#ifndef WGPUMODELGPUDATA_H
#define WGPUMODELGPUDATA_H

#include <webgpu/webgpu.h>

#include <cstddef>
#include <cstdint>
#include <vector>

#include "BvhAccel.h"
#include "InstancedGeometry.h"

// Per-model wgpu state. Mirrors the GL backend's ModelGpuData but with
// wgpu handles. Stage 2 only allocates and uploads the four core buffers;
// bind groups, pipelines, BVH and cull scratch land in later stages.
//
// All vertex/index/mesh/instance bytes are uploaded once at load time via
// wgpuQueueWriteBuffer. The vertex storage buffer is read by the vertex
// shader (vertex pulling), not used as a classic vertex buffer — there is
// no input-assembler vertex layout to match.
// Web (WebGPU) mandates `maxStorageBufferBindingSize` ≥ 128 MB; some browsers
// grant more, but we plan for the floor. Applied identically on desktop —
// the cost is a few extra draws per frame (1 per chunk; typical models =
// 1–3 chunks), which is invisible compared to per-frame GPU work.
//
// At INSTANCED_VERTEX_STRIDE_BYTES = 12 B/vertex this caps a chunk at
// 11.18 M vertices. A mesh whose vertex range is bigger than this can't fit
// in any chunk and would need splitting — typical IFC meshes are nowhere
// near (hundreds of verts), and applyCachedModel asserts loudly if it ever
// happens.
static constexpr uint64_t WGPU_CHUNK_VERTEX_BYTES_LIMIT = 128ull * 1024 * 1024;

struct WgpuModelGpuData {
    // std430 layout: 16 bytes per entry, naturally aligned. base_vertex is
    // CHUNK-LOCAL — the bound vertex_storage on that chunk's bind group
    // gives the right slice when the shader indexes vertices[].
    struct alignas(16) VisibleDrawGpu {
        uint32_t mesh_id;        // -> meshes[] for quantisation basis
        uint32_t instance_idx;   // -> instances[] for transform + ids
        uint32_t ebo_first_u32;  // start of this entry's slice in indices[] (global)
        uint32_t base_vertex;    // chunk-local start of this mesh's slice in vertex_storage
    };
    static_assert(sizeof(VisibleDrawGpu) == 16, "VisibleDrawGpu must be 16 bytes");

    // Per-chunk state. Each chunk owns its vertex_storage (sized ≤ 128 MB)
    // plus a small set of per-frame buffers (visible_draws, prefix_sums,
    // uniform) and a bind group that pulls in the chunk's vertex_storage
    // alongside the model-shared index/mesh/instance buffers. Rendering
    // issues one drawcall per non-empty chunk.
    struct Chunk {
        WGPUBuffer    vertex_storage          = nullptr;
        WGPUBuffer    visible_draws_buffer    = nullptr;
        WGPUBuffer    prefix_sums_buffer      = nullptr;
        WGPUBuffer    per_chunk_uniform       = nullptr;
        WGPUBindGroup bind_group              = nullptr;

        uint32_t      vertex_count            = 0;   // chunk capacity (vertices)
        size_t        visible_draws_capacity  = 0;
        size_t        prefix_sums_capacity    = 0;

        // Per-frame, populated by cullModelCpuCompute and consumed by render().
        uint32_t      total_visible_vertices  = 0;
        uint32_t      total_visible_draws     = 0;

        std::vector<VisibleDrawGpu> visible_draws_scratch;
        std::vector<uint32_t>       prefix_sums_scratch;
    };
    std::vector<Chunk> chunks;

    // For each mesh in meshes[], the chunk it lives in plus the chunk-local
    // vertex offset (where its vertex range starts in chunk's vertex_storage).
    // Populated at applyCachedModel time.
    std::vector<uint32_t> mesh_chunk_idx;
    std::vector<uint32_t> mesh_chunk_local_base_vertex;

    // Model-shared buffers (NOT chunked — sizes safely under 128 MB on real
    // scenes: index buffer up to ~76 MB on a 19 M-index model; instance and
    // mesh storage are far smaller).
    WGPUBuffer index_buffer     = nullptr;   // u32 mesh-local indices (read as storage)
    WGPUBuffer mesh_storage     = nullptr;   // MeshGpu[]: aabb_min/max
    WGPUBuffer instance_storage = nullptr;   // InstanceGpu[]: transform + ids

    // Size mirrors for stats / range checks. vertex_bytes is the sum across
    // all chunks; index_count / mesh_count / instance_count are unchanged.
    size_t   vertex_bytes   = 0;
    uint32_t index_count    = 0;
    uint32_t mesh_count     = 0;
    uint32_t instance_count = 0;

    // CPU side, kept for cull / picking / federation recompose.
    std::vector<MeshInfo>    meshes;
    std::vector<InstanceCpu> instances;

    // Per-model BVH over the instances' world AABBs. Built once at
    // applyCachedModel; consumed by cullModelCpuCompute to reject whole
    // subtrees against frustum + HiZ without descending. Critical for
    // 100+ model / 1M+ instance scenes — turns O(N) per-instance cull
    // into ~O(visible_count + log N).
    ModelBvh bvh;

    bool hidden = false;
};

// Release every wgpu handle in `m` and clear its size mirrors. Safe to call
// repeatedly; idempotent on already-released entries.
void releaseWgpuModelGpuData(WgpuModelGpuData& m);

#endif // WGPUMODELGPUDATA_H
