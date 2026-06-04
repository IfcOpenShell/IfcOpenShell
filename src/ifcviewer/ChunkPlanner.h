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

#ifndef CHUNKPLANNER_H
#define CHUNKPLANNER_H

// Chunk-planning helpers for the wgpu viewport. Replaces a previous
// lexicographic (z, y, x) sort with a 3D Morton (Z-order) sort over mesh
// centroids, then greedy-packs the resulting order into chunks bounded by
// a vertex-bytes ceiling. The two passes are split so each is unit-
// testable in isolation (no Qt / no wgpu).

#include <cstddef>
#include <cstdint>
#include <vector>

namespace ChunkPlanner {

// Interleave the low 21 bits of v with two zero bits between each,
// returning bits at positions 0, 3, 6, ..., 60 — one axis of a
// standard 21-bit-per-axis 3D Morton code. ORing three of these
// shifted by 0, 1, 2 gives a 63-bit (x, y, z)-interleaved code; the
// resulting integer ordering puts spatially-close points close in
// the sorted sequence (the classic Z-order curve).
uint64_t mortonSplit21(uint32_t v);

uint64_t mortonCode3D(uint32_t x, uint32_t y, uint32_t z);

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
std::vector<uint32_t> sortMeshIdsByMorton(
    std::size_t n_meshes,
    const std::vector<float>& mesh_cx,
    const std::vector<float>& mesh_cy,
    const std::vector<float>& mesh_cz,
    const std::vector<uint32_t>& mesh_inst_count);

// Greedy-pack a pre-sorted mesh-id sequence into chunks bounded by
// `chunk_vertex_bytes_limit`. Each mesh is placed in the current
// chunk; if adding it would push the running byte count over the
// limit (and the chunk is non-empty), a new chunk is started.
//
// A mesh whose own vertex bytes already exceed the limit lands alone
// in its own (over-sized) chunk — the planner never splits a mesh
// across chunks, because the mega-draw bookkeeping is per-mesh
// chunk-local-offset.
//
// `sorted_mesh_ids` is the order produced by sortMeshIdsByMorton.
// `mesh_vertex_count[mesh_id]` gives the vertex count per mesh.
// `vertex_stride_bytes` is the per-vertex byte size on the GPU.
std::vector<std::vector<uint32_t>> greedyPackChunks(
    const std::vector<uint32_t>& sorted_mesh_ids,
    const std::vector<uint32_t>& mesh_vertex_count,
    uint64_t vertex_stride_bytes,
    uint64_t chunk_vertex_bytes_limit);

} // namespace ChunkPlanner

#endif  // CHUNKPLANNER_H
