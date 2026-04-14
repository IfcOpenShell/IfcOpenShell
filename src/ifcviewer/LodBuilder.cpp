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

#include "LodBuilder.h"

#include <meshoptimizer.h>

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

void buildLods(SidecarData& sd,
               int min_triangles,
               float target_ratio,
               float target_error) {
    if (sd.meshes.empty() || sd.vertices.empty() || sd.indices.empty()) return;

    const size_t vtx_stride_bytes   = INSTANCED_VERTEX_STRIDE_BYTES;
    const size_t total_vertex_count = sd.vertices.size() / vtx_stride_bytes;

    // Env var knobs so we can tune without rebuilding.
    //   IFC_LOD_LOCK_BORDER=1      re-enable LockBorder (off by default: BIM
    //                              geometry is often non-manifold so locking
    //                              borders prevents any collapse).
    //   IFC_LOD_ERROR=<float>      override target_error (default 0.05 → 0.2).
    //   IFC_LOD_RATIO=<float>      override target_ratio.
    //   IFC_LOD_MIN_SAVINGS=<0..1> minimum fraction of tris saved to accept
    //                              (default 0.25).
    //   IFC_LOD_DEBUG=1            print per-mesh diagnostics for the first
    //                              few meshes of each call.
    //   IFC_LOD_SLOPPY=0           disable sloppy (clustering) decimator.
    //                              Default ON: BIM brep output is usually
    //                              non-manifold, so edge-collapse simplify
    //                              returns the input unchanged.
    const char* env_lock    = std::getenv("IFC_LOD_LOCK_BORDER");
    const char* env_err     = std::getenv("IFC_LOD_ERROR");
    const char* env_ratio   = std::getenv("IFC_LOD_RATIO");
    const char* env_savings = std::getenv("IFC_LOD_MIN_SAVINGS");
    const char* env_debug   = std::getenv("IFC_LOD_DEBUG");
    const char* env_sloppy  = std::getenv("IFC_LOD_SLOPPY");

    const bool lock_border = env_lock && env_lock[0] == '1';
    const bool use_sloppy  = !(env_sloppy && env_sloppy[0] == '0');
    if (env_err)   target_error = static_cast<float>(std::atof(env_err));
    if (env_ratio) target_ratio = static_cast<float>(std::atof(env_ratio));
    float min_savings = 0.25f;
    if (env_savings) min_savings = static_cast<float>(std::atof(env_savings));
    const bool debug = env_debug && env_debug[0] == '1';

    // Loosened defaults: BIM meshes are non-manifold; LockBorder ≈ zero
    // collapses. A 0.2 error budget still looks fine at sub-4px.
    if (target_error < 0.2f) target_error = 0.2f;

    // Scratch buffers reused across meshes so we only allocate once.
    std::vector<uint32_t> simplified;
    std::vector<uint32_t> shadow;
    std::vector<float>    dequant_pos;   // 3 floats/vertex, dequantized
    simplified.reserve(1024);
    shadow.reserve(1024);
    dequant_pos.reserve(1024 * 3);

    int dbg_printed = 0;
    int dbg_rejected_savings = 0;
    int dbg_rejected_noreduce = 0;
    int dbg_accepted = 0;

    for (auto& mesh : sd.meshes) {
        mesh.lod1_ebo_byte_offset = 0;
        mesh.lod1_index_count     = 0;

        const uint32_t tri_count = mesh.index_count / 3;
        if (static_cast<int>(tri_count) < min_triangles) continue;
        if (mesh.vertex_count == 0) continue;

        // meshopt wants a pointer to the *first position* and a vertex_count
        // equal to the number of referenced vertices (i.e. the absolute upper
        // bound on indices we might see).  Indices in `sd.indices` for this
        // mesh are mesh-local (0..mesh.vertex_count).  Pass the base-vertex
        // as an offset into sd.vertices so meshopt reads positions at the
        // right place.
        const uint32_t base_vertex = mesh.vbo_byte_offset / vtx_stride_bytes;
        if (base_vertex + mesh.vertex_count > total_vertex_count) continue;

        const uint32_t first_index = mesh.ebo_byte_offset / sizeof(uint32_t);
        if (first_index + mesh.index_count > sd.indices.size()) continue;

        // Dequantize positions for this mesh into a temp float array.
        // meshopt needs contiguous float3 positions with a known stride;
        // quantized bytes aren't directly usable.
        const uint8_t* quant_base =
            sd.vertices.data() + base_vertex * vtx_stride_bytes;
        dequant_pos.resize(static_cast<size_t>(mesh.vertex_count) * 3);
        const float extent[3] = {
            mesh.local_aabb_max[0] - mesh.local_aabb_min[0],
            mesh.local_aabb_max[1] - mesh.local_aabb_min[1],
            mesh.local_aabb_max[2] - mesh.local_aabb_min[2],
        };
        for (uint32_t v = 0; v < mesh.vertex_count; ++v) {
            const uint16_t* p = reinterpret_cast<const uint16_t*>(
                quant_base + v * vtx_stride_bytes);
            for (int a = 0; a < 3; ++a) {
                float t = p[a] / 65535.0f;
                dequant_pos[v * 3 + a] = mesh.local_aabb_min[a] + t * extent[a];
            }
        }
        const float* positions = dequant_pos.data();
        const size_t local_pos_stride = sizeof(float) * 3;
        const uint32_t* indices = sd.indices.data() + first_index;

        const size_t target_index_count = std::max<size_t>(
            3, static_cast<size_t>(mesh.index_count * target_ratio) / 3 * 3);

        // The instanced VBO stores each triangle's vertices separately, so the
        // mesh's index buffer is topologically disconnected — every edge is
        // boundary, every vertex is unique, and meshopt_simplify can't collapse
        // anything.  Build a shadow index buffer that welds by position, so
        // shared-position vertices share an ID; then simplify on that.  Output
        // indices are still valid mesh-local IDs (canonical representatives),
        // usable directly as LOD1 indices against the same VBO.
        shadow.resize(mesh.index_count);
        meshopt_generateShadowIndexBuffer(
            shadow.data(),
            indices, mesh.index_count,
            positions, mesh.vertex_count,
            sizeof(float) * 3,       // compare only xyz
            local_pos_stride);

        simplified.resize(mesh.index_count);
        float result_error = 0.0f;
        size_t new_index_count = 0;

        if (use_sloppy) {
            // Cluster-based decimator.  Ignores topology entirely; great for
            // BIM brep output which is usually non-manifold / has T-junctions.
            // Operates directly on the original indices — welding isn't
            // needed since it quantises positions into voxel cells.
            new_index_count = meshopt_simplifySloppy(
                simplified.data(),
                indices, mesh.index_count,
                positions, mesh.vertex_count, local_pos_stride,
                target_index_count, target_error,
                &result_error);
        } else {
            const unsigned int options =
                lock_border ? static_cast<unsigned int>(meshopt_SimplifyLockBorder) : 0u;
            new_index_count = meshopt_simplify(
                simplified.data(),
                shadow.data(), mesh.index_count,
                positions, mesh.vertex_count, local_pos_stride,
                target_index_count, target_error,
                options, &result_error);
        }

        if (debug && dbg_printed < 8) {
            std::fprintf(stderr,
                "  [lod] mesh tris=%u target=%zu got=%zu err=%.4f\n",
                tri_count, target_index_count / 3,
                new_index_count / 3, result_error);
            ++dbg_printed;
        }

        // Accept only if we actually saved a meaningful chunk of tris.
        if (new_index_count == 0 || new_index_count >= mesh.index_count) {
            ++dbg_rejected_noreduce;
            continue;
        }

        const uint32_t saved = mesh.index_count - static_cast<uint32_t>(new_index_count);
        if (static_cast<float>(saved) < min_savings * static_cast<float>(mesh.index_count)) {
            ++dbg_rejected_savings;
            continue;
        }
        ++dbg_accepted;

        // Append the surviving indices to sd.indices; record the offset.
        const size_t append_offset_bytes = sd.indices.size() * sizeof(uint32_t);
        sd.indices.insert(sd.indices.end(),
                          simplified.begin(),
                          simplified.begin() + new_index_count);
        mesh.lod1_ebo_byte_offset = static_cast<uint32_t>(append_offset_bytes);
        mesh.lod1_index_count     = static_cast<uint32_t>(new_index_count);
    }

    if (debug) {
        std::fprintf(stderr,
            "  [lod] summary: accepted=%d rejected_noreduce=%d rejected_savings=%d "
            "(lock_border=%d target_error=%.3f target_ratio=%.3f min_savings=%.3f)\n",
            dbg_accepted, dbg_rejected_noreduce, dbg_rejected_savings,
            lock_border ? 1 : 0, target_error, target_ratio, min_savings);
    }
}

LodStats summariseLods(const SidecarData& sd) {
    LodStats s;
    s.meshes_total = static_cast<uint32_t>(sd.meshes.size());
    for (const auto& m : sd.meshes) {
        s.tris_lod0 += m.index_count / 3;
        if (m.lod1_index_count > 0) {
            ++s.meshes_with_lod1;
            s.tris_lod1          += m.lod1_index_count / 3;
            s.tris_lod0_for_lod1 += m.index_count / 3;
        }
    }
    return s;
}
