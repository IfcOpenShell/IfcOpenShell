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

#include "SidecarLayout.h"

#include "ChunkPlanner.h"
#include "InstancedGeometry.h"

#include <cstdint>
#include <vector>

void reorderSidecarByMorton(SidecarData& sd) {
    const std::size_t n = sd.meshes.size();
    if (n < 2) return;

    // Per-mesh centroid + instance count, exactly as the loader computes them
    // before chunk planning (average of instance world-AABB centres).
    std::vector<float>         cx(n, 0.0f), cy(n, 0.0f), cz(n, 0.0f);
    std::vector<std::uint32_t> cnt(n, 0);
    for (const auto& inst : sd.instances) {
        if (inst.mesh_id >= n) continue;
        cx[inst.mesh_id] += 0.5f * (inst.world_aabb_min[0] + inst.world_aabb_max[0]);
        cy[inst.mesh_id] += 0.5f * (inst.world_aabb_min[1] + inst.world_aabb_max[1]);
        cz[inst.mesh_id] += 0.5f * (inst.world_aabb_min[2] + inst.world_aabb_max[2]);
        ++cnt[inst.mesh_id];
    }
    for (std::size_t i = 0; i < n; ++i) {
        if (cnt[i] > 0) {
            const float inv = 1.0f / float(cnt[i]);
            cx[i] *= inv; cy[i] *= inv; cz[i] *= inv;
        }
    }

    // order[new_id] = old mesh id, in the loader's Morton order.
    const std::vector<std::uint32_t> order =
        ChunkPlanner::sortMeshIdsByMorton(n, cx, cy, cz, cnt);

    // Greedy-pack the sorted order into chunks (the same plan the loader used
    // to derive). Each chunk is a CONSECUTIVE run of `order`, so once we lay
    // meshes out in `order` the chunk is a contiguous mesh range — recorded in
    // the TOC as {first_mesh, mesh_count}.
    std::vector<std::uint32_t> mesh_vertex_count(n, 0);
    for (std::size_t i = 0; i < n; ++i) mesh_vertex_count[i] = sd.meshes[i].vertex_count;
    const std::vector<std::vector<std::uint32_t>> packed = ChunkPlanner::greedyPackChunks(
        order, mesh_vertex_count, INSTANCED_VERTEX_STRIDE_BYTES,
        WGPU_CHUNK_VERTEX_BYTES_LIMIT);
    sd.chunks.clear();
    sd.chunks.reserve(packed.size());
    {
        std::uint32_t first = 0;
        for (const auto& chunk : packed) {
            sd.chunks.push_back({first, std::uint32_t(chunk.size())});
            first += std::uint32_t(chunk.size());
        }
    }

    // Bucket instances by their (authoritative) mesh_id. We must NOT rely on
    // MeshInfo.first_instance: the baker leaves it 0 for every mesh and stores
    // instances ungrouped, so first_instance describes nothing. Grouping here
    // by mesh_id both reorders instances correctly AND fixes first_instance.
    std::vector<std::vector<std::uint32_t>> insts_by_mesh(n);
    for (std::uint32_t ii = 0; ii < sd.instances.size(); ++ii) {
        const std::uint32_t mid = sd.instances[ii].mesh_id;
        if (mid < n) insts_by_mesh[mid].push_back(ii);
    }

    std::vector<std::uint8_t>   new_vertices;  new_vertices.reserve(sd.vertices.size());
    std::vector<std::uint32_t>  new_indices;   new_indices.reserve(sd.indices.size());
    std::vector<MeshInfo>       new_meshes(n);
    std::vector<InstanceCpu>    new_instances; new_instances.reserve(sd.instances.size());

    // Pass A: vertices + LOD0 indices + instances, mesh-by-mesh in the new
    // order, recording the new offsets on each MeshInfo.
    for (std::uint32_t ni = 0; ni < n; ++ni) {
        const std::uint32_t old = order[ni];
        const MeshInfo& om = sd.meshes[old];
        MeshInfo nm = om;  // carries AABB; offsets/instance fields overwritten below

        nm.vbo_byte_offset = std::uint32_t(new_vertices.size());
        const std::size_t vbytes = std::size_t(om.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        new_vertices.insert(new_vertices.end(),
                            sd.vertices.begin() + om.vbo_byte_offset,
                            sd.vertices.begin() + om.vbo_byte_offset + vbytes);

        nm.ebo_byte_offset = std::uint32_t(new_indices.size() * sizeof(std::uint32_t));
        const std::size_t i0 = om.ebo_byte_offset / sizeof(std::uint32_t);
        new_indices.insert(new_indices.end(),
                           sd.indices.begin() + i0,
                           sd.indices.begin() + i0 + om.index_count);

        nm.first_instance = std::uint32_t(new_instances.size());
        nm.instance_count = std::uint32_t(insts_by_mesh[old].size());
        for (std::uint32_t ii : insts_by_mesh[old]) {
            InstanceCpu ic = sd.instances[ii];
            ic.mesh_id = ni;
            new_instances.push_back(ic);
        }

        new_meshes[ni] = nm;
    }

    // Pass B: LOD1 indices appended after all LOD0 (same global layout as the
    // baker), in the new order, so a chunk's LOD1 slice is contiguous too.
    for (std::uint32_t ni = 0; ni < n; ++ni) {
        const MeshInfo& om = sd.meshes[order[ni]];
        MeshInfo& nm = new_meshes[ni];
        if (om.lod1_index_count == 0) { nm.lod1_ebo_byte_offset = 0; continue; }
        nm.lod1_ebo_byte_offset = std::uint32_t(new_indices.size() * sizeof(std::uint32_t));
        const std::size_t l0 = om.lod1_ebo_byte_offset / sizeof(std::uint32_t);
        new_indices.insert(new_indices.end(),
                           sd.indices.begin() + l0,
                           sd.indices.begin() + l0 + om.lod1_index_count);
    }

    sd.vertices  = std::move(new_vertices);
    sd.indices   = std::move(new_indices);
    sd.meshes    = std::move(new_meshes);
    sd.instances = std::move(new_instances);
}
