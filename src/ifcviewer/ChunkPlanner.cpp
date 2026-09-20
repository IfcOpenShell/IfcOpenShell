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

#include "ChunkPlanner.h"

#include <algorithm>
#include <limits>
#include <numeric>

namespace ChunkPlanner {

uint64_t mortonSplit21(uint32_t v) {
    uint64_t r = v & 0x1FFFFFu;
    r = (r | r << 32) & 0x001F00000000FFFFULL;
    r = (r | r << 16) & 0x001F0000FF0000FFULL;
    r = (r | r << 8)  & 0x100F00F00F00F00FULL;
    r = (r | r << 4)  & 0x10C30C30C30C30C3ULL;
    r = (r | r << 2)  & 0x1249249249249249ULL;
    return r;
}

uint64_t mortonCode3D(uint32_t x, uint32_t y, uint32_t z) {
    return mortonSplit21(x) | (mortonSplit21(y) << 1) | (mortonSplit21(z) << 2);
}

std::vector<uint32_t> sortMeshIdsByMorton(
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

std::vector<std::vector<uint32_t>> greedyPackChunks(
        const std::vector<uint32_t>& sorted_mesh_ids,
        const std::vector<uint32_t>& mesh_vertex_count,
        uint64_t vertex_stride_bytes,
        uint64_t chunk_vertex_bytes_limit) {
    std::vector<std::vector<uint32_t>> chunks;
    if (sorted_mesh_ids.empty()) return chunks;

    chunks.push_back({});
    uint64_t current_chunk_bytes = 0;
    for (uint32_t mi : sorted_mesh_ids) {
        const uint64_t mesh_bytes =
            uint64_t(mesh_vertex_count[mi]) * vertex_stride_bytes;
        if (current_chunk_bytes > 0
            && current_chunk_bytes + mesh_bytes > chunk_vertex_bytes_limit) {
            chunks.push_back({});
            current_chunk_bytes = 0;
        }
        chunks.back().push_back(mi);
        current_chunk_bytes += mesh_bytes;
    }
    if (chunks.back().empty()) chunks.pop_back();
    return chunks;
}

} // namespace ChunkPlanner
