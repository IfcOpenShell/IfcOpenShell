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
#include "InstancedGeometry.h"
#include "SidecarCache.h"
#include "SidecarLayout.h"

#include <catch2/catch_test_macros.hpp>

#include <cstdint>
#include <map>
#include <vector>

namespace {

constexpr int STRIDE = INSTANCED_VERTEX_STRIDE_BYTES;

// A fixture with N meshes, each with a unique vertex/index pattern + LOD1 on
// some, and instances spread across 3D space so the Morton sort actually
// permutes (not already sorted). Geometry is stored in mesh-id order (as a
// fresh bake produces it).
SidecarData buildFixture() {
    SidecarData sd;
    const int N = 6;

    // Per-mesh: vertex_count = i+2, index_count = i+2 (mesh-local 0..vc-1),
    // lod1 on even meshes (lod1_count = 1). Vertices encode (mesh, vert).
    std::vector<MeshInfo> meshes(N);
    for (int i = 0; i < N; ++i) {
        MeshInfo& m = meshes[i];
        const uint32_t vc = uint32_t(i + 2);
        m.vbo_byte_offset = uint32_t(sd.vertices.size());
        m.vertex_count    = vc;
        for (uint32_t v = 0; v < vc; ++v)
            for (int b = 0; b < STRIDE; ++b)
                sd.vertices.push_back(uint8_t((i * 37 + v * 7 + b) & 0xFF));

        m.ebo_byte_offset = uint32_t(sd.indices.size() * sizeof(uint32_t));
        m.index_count     = vc;
        for (uint32_t k = 0; k < vc; ++k) sd.indices.push_back(k);  // mesh-local

        m.local_aabb_min[0] = float(-i); m.local_aabb_max[0] = float(i + 1);
        m.local_aabb_min[1] = 0;         m.local_aabb_max[1] = 2;
        m.local_aabb_min[2] = 0;         m.local_aabb_max[2] = 3;
    }
    // LOD1 slices appended after all LOD0 (matches the baker's global layout).
    for (int i = 0; i < N; ++i) {
        if (i % 2 != 0) { meshes[i].lod1_index_count = 0; continue; }
        meshes[i].lod1_ebo_byte_offset = uint32_t(sd.indices.size() * sizeof(uint32_t));
        meshes[i].lod1_index_count     = 1;
        sd.indices.push_back(uint32_t(i));  // distinctive lod1 index
    }

    // Instances: deliberately UNGROUPED (round-robin across meshes) with
    // first_instance left at 0 — mimicking the real baker, which never sets
    // first_instance and stores instances in stream order. A reorder that
    // trusts first_instance instead of per-instance mesh_id scrambles them.
    auto ninst = [](int i) { return uint32_t((i % 3) + 1); };
    for (int i = 0; i < N; ++i) {
        meshes[i].first_instance = 0;          // as the baker leaves it
        meshes[i].instance_count = ninst(i);   // baker sets the count
    }
    uint32_t obj = 100;
    for (uint32_t k = 0; k < 3; ++k) {         // outer loop = interleave
        for (int i = 0; i < N; ++i) {
            if (k >= ninst(i)) continue;
            InstanceCpu ic;
            ic.mesh_id   = uint32_t(i);        // authoritative
            ic.object_id = obj++;
            ic.model_id  = 1;
            const float x = float((i * 13 + k * 5) % 11);
            const float y = float((i * 7  + k * 3) % 9);
            const float z = float((i * 5  + k * 2) % 7);
            ic.world_aabb_min[0] = x;     ic.world_aabb_max[0] = x + 1;
            ic.world_aabb_min[1] = y;     ic.world_aabb_max[1] = y + 1;
            ic.world_aabb_min[2] = z;     ic.world_aabb_max[2] = z + 1;
            for (int t = 0; t < 16; ++t) ic.transform[t] = float(ic.object_id) + 0.1f * t;
            sd.instances.push_back(ic);
        }
    }
    sd.meshes = meshes;
    return sd;
}

// Everything an instance "draws", independent of storage order: its mesh's
// vertex bytes, LOD0 + LOD1 index VALUES, local AABB, and its own transform.
struct InstSig {
    std::vector<uint8_t>  verts;
    std::vector<uint32_t> idx0, idx1;
    float aabb[6];
    float xf[16];
    bool operator==(const InstSig& o) const {
        if (verts != o.verts || idx0 != o.idx0 || idx1 != o.idx1) return false;
        for (int i = 0; i < 6;  ++i) if (aabb[i] != o.aabb[i]) return false;
        for (int i = 0; i < 16; ++i) if (xf[i]   != o.xf[i])   return false;
        return true;
    }
};

InstSig sigFor(const SidecarData& sd, const InstanceCpu& inst) {
    const MeshInfo& m = sd.meshes.at(inst.mesh_id);
    InstSig s{};
    s.verts.assign(sd.vertices.begin() + m.vbo_byte_offset,
                   sd.vertices.begin() + m.vbo_byte_offset
                       + std::size_t(m.vertex_count) * STRIDE);
    const std::size_t i0 = m.ebo_byte_offset / sizeof(uint32_t);
    s.idx0.assign(sd.indices.begin() + i0, sd.indices.begin() + i0 + m.index_count);
    if (m.lod1_index_count > 0) {
        const std::size_t l0 = m.lod1_ebo_byte_offset / sizeof(uint32_t);
        s.idx1.assign(sd.indices.begin() + l0, sd.indices.begin() + l0 + m.lod1_index_count);
    }
    s.aabb[0]=m.local_aabb_min[0]; s.aabb[1]=m.local_aabb_min[1]; s.aabb[2]=m.local_aabb_min[2];
    s.aabb[3]=m.local_aabb_max[0]; s.aabb[4]=m.local_aabb_max[1]; s.aabb[5]=m.local_aabb_max[2];
    for (int t = 0; t < 16; ++t) s.xf[t] = inst.transform[t];
    return s;
}

std::map<uint32_t, InstSig> sigMap(const SidecarData& sd) {
    std::map<uint32_t, InstSig> m;
    for (const auto& inst : sd.instances) m[inst.object_id] = sigFor(sd, inst);
    return m;
}

}  // namespace

TEST_CASE("reorderSidecarByMorton preserves every instance's drawn geometry", "[layout]") {
    SidecarData before = buildFixture();
    const auto sig_before = sigMap(before);

    SidecarData after = before;
    reorderSidecarByMorton(after);

    // Same counts.
    REQUIRE(after.meshes.size()    == before.meshes.size());
    REQUIRE(after.instances.size() == before.instances.size());
    REQUIRE(after.vertices.size()  == before.vertices.size());
    REQUIRE(after.indices.size()   == before.indices.size());

    // The geometry each object draws is byte-for-byte identical — only the
    // storage order changed.
    REQUIRE(sigMap(after) == sig_before);

    // first_instance / instance_count now correctly describe contiguous,
    // mesh-grouped instance ranges (the baker left first_instance = 0, so a
    // reorder must rebuild them from per-instance mesh_id — getting this wrong
    // scrambles every transform and collapses geometry to the origin).
    for (uint32_t mi = 0; mi < after.meshes.size(); ++mi) {
        const auto& m = after.meshes[mi];
        for (uint32_t k = 0; k < m.instance_count; ++k)
            REQUIRE(after.instances.at(m.first_instance + k).mesh_id == mi);
    }

    // It actually permuted (the fixture isn't already Morton-sorted).
    bool moved = false;
    for (std::size_t i = 0; i < after.meshes.size(); ++i)
        if (after.meshes[i].vbo_byte_offset != before.meshes[i].vbo_byte_offset ||
            after.meshes[i].vertex_count    != before.meshes[i].vertex_count) moved = true;
    REQUIRE(moved);
}

TEST_CASE("reorderSidecarByMorton lays meshes out contiguously per the loader", "[layout]") {
    SidecarData sd = buildFixture();
    reorderSidecarByMorton(sd);

    // Meshes' vertex + LOD0-index slices are laid down back-to-back in array
    // order (so consecutive meshes — i.e. a chunk — form one contiguous range).
    std::uint32_t v_cursor = 0, i_cursor = 0;
    for (const auto& m : sd.meshes) {
        REQUIRE(m.vbo_byte_offset == v_cursor);
        v_cursor += m.vertex_count * STRIDE;
        REQUIRE(m.ebo_byte_offset == i_cursor * sizeof(std::uint32_t));
        i_cursor += m.index_count;
    }

    // Re-running the loader's Morton sort on the laid-out data yields the
    // identity permutation — which is exactly what makes the greedy-packed
    // chunks consecutive (hence contiguous) byte ranges at load time.
    const std::size_t n = sd.meshes.size();
    std::vector<float> cx(n,0), cy(n,0), cz(n,0); std::vector<std::uint32_t> cnt(n,0);
    for (const auto& inst : sd.instances) {
        cx[inst.mesh_id] += 0.5f*(inst.world_aabb_min[0]+inst.world_aabb_max[0]);
        cy[inst.mesh_id] += 0.5f*(inst.world_aabb_min[1]+inst.world_aabb_max[1]);
        cz[inst.mesh_id] += 0.5f*(inst.world_aabb_min[2]+inst.world_aabb_max[2]);
        ++cnt[inst.mesh_id];
    }
    for (std::size_t i=0;i<n;++i) if (cnt[i]>0){float inv=1.0f/cnt[i]; cx[i]*=inv;cy[i]*=inv;cz[i]*=inv;}
    const auto order = ChunkPlanner::sortMeshIdsByMorton(n, cx, cy, cz, cnt);
    for (std::uint32_t i = 0; i < n; ++i) REQUIRE(order[i] == i);
}

TEST_CASE("reorderSidecarByMorton is a no-op for trivial inputs", "[layout]") {
    SidecarData empty;
    reorderSidecarByMorton(empty);
    REQUIRE(empty.meshes.empty());

    SidecarData one = buildFixture();
    one.meshes.resize(1);
    const auto v = one.vertices;
    reorderSidecarByMorton(one);  // n < 2 path doesn't touch anything
    REQUIRE(one.vertices == v);
}
