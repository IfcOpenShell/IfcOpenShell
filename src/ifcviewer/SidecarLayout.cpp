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
    const std::size_t mesh_count = sd.meshes.size();
    if (mesh_count < 2) return;

    // Per-mesh centroid + instance count, exactly as the loader computes them
    // before chunk planning (average of instance world-AABB centres).
    std::vector<float>         mesh_centroid_x(mesh_count, 0.0f),
                               mesh_centroid_y(mesh_count, 0.0f),
                               mesh_centroid_z(mesh_count, 0.0f);
    std::vector<std::uint32_t> mesh_instance_count(mesh_count, 0);
    for (const auto& inst : sd.instances) {
        if (inst.mesh_id >= mesh_count) continue;
        mesh_centroid_x[inst.mesh_id] += 0.5f * (inst.world_aabb_min[0] + inst.world_aabb_max[0]);
        mesh_centroid_y[inst.mesh_id] += 0.5f * (inst.world_aabb_min[1] + inst.world_aabb_max[1]);
        mesh_centroid_z[inst.mesh_id] += 0.5f * (inst.world_aabb_min[2] + inst.world_aabb_max[2]);
        ++mesh_instance_count[inst.mesh_id];
    }
    for (std::size_t i = 0; i < mesh_count; ++i) {
        if (mesh_instance_count[i] > 0) {
            const float inv = 1.0f / float(mesh_instance_count[i]);
            mesh_centroid_x[i] *= inv;
            mesh_centroid_y[i] *= inv;
            mesh_centroid_z[i] *= inv;
        }
    }

    // order[new_id] = old mesh id, in the loader's Morton order.
    const std::vector<std::uint32_t> order =
        ChunkPlanner::sortMeshIdsByMorton(
            mesh_count, mesh_centroid_x, mesh_centroid_y, mesh_centroid_z, mesh_instance_count);

    // Greedy-pack the sorted order into chunks (the same plan the loader used
    // to derive). Each chunk is a CONSECUTIVE run of `order`, so once we lay
    // meshes out in `order` the chunk is a contiguous mesh range — recorded in
    // the TOC as {first_mesh, mesh_count}.
    std::vector<std::uint32_t> mesh_vertex_count(mesh_count, 0);
    for (std::size_t i = 0; i < mesh_count; ++i) mesh_vertex_count[i] = sd.meshes[i].vertex_count;
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
    std::vector<std::vector<std::uint32_t>> insts_by_mesh(mesh_count);
    for (std::uint32_t instance_index = 0; instance_index < sd.instances.size(); ++instance_index) {
        const std::uint32_t mesh_id = sd.instances[instance_index].mesh_id;
        if (mesh_id < mesh_count) insts_by_mesh[mesh_id].push_back(instance_index);
    }

    std::vector<std::uint8_t>   new_vertices;  new_vertices.reserve(sd.vertices.size());
    std::vector<std::uint32_t>  new_indices;   new_indices.reserve(sd.indices.size());
    std::vector<MeshInfo>       new_meshes(mesh_count);
    std::vector<InstanceCpu>    new_instances; new_instances.reserve(sd.instances.size());

    // Pass A: vertices + LOD0 indices + instances, mesh-by-mesh in the new
    // order, recording the new offsets on each MeshInfo.
    for (std::uint32_t new_mesh_index = 0; new_mesh_index < mesh_count; ++new_mesh_index) {
        const std::uint32_t old = order[new_mesh_index];
        const MeshInfo& old_mesh_info = sd.meshes[old];
        MeshInfo new_mesh_info = old_mesh_info;  // carries AABB; offsets/instance fields overwritten below

        new_mesh_info.vbo_byte_offset = std::uint32_t(new_vertices.size());
        const std::size_t vbytes = std::size_t(old_mesh_info.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        new_vertices.insert(new_vertices.end(),
                            sd.vertices.begin() + old_mesh_info.vbo_byte_offset,
                            sd.vertices.begin() + old_mesh_info.vbo_byte_offset + vbytes);

        new_mesh_info.ebo_byte_offset = std::uint32_t(new_indices.size() * sizeof(std::uint32_t));
        const std::size_t i0 = old_mesh_info.ebo_byte_offset / sizeof(std::uint32_t);
        new_indices.insert(new_indices.end(),
                           sd.indices.begin() + i0,
                           sd.indices.begin() + i0 + old_mesh_info.index_count);

        new_mesh_info.first_instance = std::uint32_t(new_instances.size());
        new_mesh_info.instance_count = std::uint32_t(insts_by_mesh[old].size());
        for (std::uint32_t instance_index : insts_by_mesh[old]) {
            InstanceCpu instance = sd.instances[instance_index];
            instance.mesh_id = new_mesh_index;
            new_instances.push_back(instance);
        }

        new_meshes[new_mesh_index] = new_mesh_info;
    }

    // Pass B: LOD1 indices appended after all LOD0 (same global layout as the
    // baker), in the new order, so a chunk's LOD1 slice is contiguous too.
    for (std::uint32_t new_mesh_index = 0; new_mesh_index < mesh_count; ++new_mesh_index) {
        const MeshInfo& old_mesh_info = sd.meshes[order[new_mesh_index]];
        MeshInfo& new_mesh_info = new_meshes[new_mesh_index];
        if (old_mesh_info.lod1_index_count == 0) {
            new_mesh_info.lod1_ebo_byte_offset = 0;
            continue;
        }
        new_mesh_info.lod1_ebo_byte_offset = std::uint32_t(new_indices.size() * sizeof(std::uint32_t));
        const std::size_t l0 = old_mesh_info.lod1_ebo_byte_offset / sizeof(std::uint32_t);
        new_indices.insert(new_indices.end(),
                           sd.indices.begin() + l0,
                           sd.indices.begin() + l0 + old_mesh_info.lod1_index_count);
    }

    sd.vertices  = std::move(new_vertices);
    sd.indices   = std::move(new_indices);
    sd.meshes    = std::move(new_meshes);
    sd.instances = std::move(new_instances);
}
