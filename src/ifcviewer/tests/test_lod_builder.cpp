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

#include "InstancedGeometry.h"
#include "LodBuilder.h"
#include "SidecarCache.h"

#include <catch2/catch_test_macros.hpp>

#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace {

// Wipes LOD env-var knobs so tests run against the documented defaults
// regardless of the host shell.
struct ScopedEnvIsolate {
    ScopedEnvIsolate() {
#ifdef _WIN32
        _putenv_s("IFC_LOD_ERROR", "");
        _putenv_s("IFC_LOD_RATIO", "");
        _putenv_s("IFC_LOD_MIN_SAVINGS", "");
        _putenv_s("IFC_LOD_DEBUG", "");
#else
        unsetenv("IFC_LOD_ERROR");
        unsetenv("IFC_LOD_RATIO");
        unsetenv("IFC_LOD_MIN_SAVINGS");
        unsetenv("IFC_LOD_DEBUG");
#endif
    }
};

// Append one quantized vertex (positions only — normal/color zeroed) to the
// vertex byte buffer.  Quantization basis is the mesh's local AABB.
void appendQuantizedVertex(std::vector<uint8_t>& bytes,
                           const float pos[3],
                           const float aabb_min[3],
                           const float aabb_max[3]) {
    uint16_t qpos[3];
    for (int a = 0; a < 3; ++a) {
        float extent = aabb_max[a] - aabb_min[a];
        float t = extent > 0.0f ? (pos[a] - aabb_min[a]) / extent : 0.0f;
        if (t < 0.0f) t = 0.0f;
        if (t > 1.0f) t = 1.0f;
        qpos[a] = static_cast<uint16_t>(t * 65535.0f + 0.5f);
    }
    size_t before = bytes.size();
    bytes.resize(before + INSTANCED_VERTEX_STRIDE_BYTES, 0);
    std::memcpy(bytes.data() + before + INSTANCED_VERTEX_POS_OFFSET, qpos, sizeof(qpos));
}

// Build a planar NxN grid mesh: (N-1)^2 quads = 2*(N-1)^2 triangles.  Returns
// a single-mesh SidecarData with quantized vertex bytes and uint32 indices.
SidecarData makeGridMesh(int N) {
    SidecarData sd;
    MeshInfo mesh{};
    mesh.local_aabb_min[0] = 0.0f; mesh.local_aabb_min[1] = 0.0f; mesh.local_aabb_min[2] = 0.0f;
    mesh.local_aabb_max[0] = 1.0f; mesh.local_aabb_max[1] = 1.0f; mesh.local_aabb_max[2] = 0.0f;
    mesh.vbo_byte_offset = 0;
    mesh.ebo_byte_offset = 0;
    mesh.vertex_count = uint32_t(N * N);

    for (int j = 0; j < N; ++j) {
        for (int i = 0; i < N; ++i) {
            float pos[3] = {
                float(i) / float(N - 1),
                float(j) / float(N - 1),
                0.0f
            };
            appendQuantizedVertex(sd.vertices, pos,
                                  mesh.local_aabb_min, mesh.local_aabb_max);
        }
    }

    for (int j = 0; j < N - 1; ++j) {
        for (int i = 0; i < N - 1; ++i) {
            uint32_t v00 = uint32_t(j * N + i);
            uint32_t v10 = v00 + 1;
            uint32_t v01 = v00 + uint32_t(N);
            uint32_t v11 = v01 + 1;
            sd.indices.push_back(v00); sd.indices.push_back(v10); sd.indices.push_back(v11);
            sd.indices.push_back(v00); sd.indices.push_back(v11); sd.indices.push_back(v01);
        }
    }
    mesh.index_count = uint32_t(sd.indices.size());
    sd.meshes.push_back(mesh);
    return sd;
}

} // namespace

TEST_CASE("buildLods skips meshes below min_triangles", "[lod]") {
    ScopedEnvIsolate guard;
    // 9x9 grid -> 128 triangles. Default min_triangles is 500.
    SidecarData sd = makeGridMesh(9);
    REQUIRE(sd.meshes[0].index_count / 3 == 128u);

    size_t indices_before = sd.indices.size();
    buildLods(sd);

    REQUIRE(sd.meshes[0].lod1_index_count == 0);
    REQUIRE(sd.meshes[0].lod1_ebo_byte_offset == 0);
    REQUIRE(sd.indices.size() == indices_before);  // nothing appended
}

TEST_CASE("buildLods produces a valid LOD1 slice for a high-tri mesh", "[lod]") {
    ScopedEnvIsolate guard;
    // 30x30 grid -> 1682 triangles. Comfortably above min_triangles.
    SidecarData sd = makeGridMesh(30);
    const uint32_t lod0_indices = sd.meshes[0].index_count;
    const size_t indices_before = sd.indices.size();
    REQUIRE(lod0_indices / 3 >= 500u);

    buildLods(sd);

    const auto& m = sd.meshes[0];
    REQUIRE(m.lod1_index_count > 0);
    REQUIRE(m.lod1_index_count % 3 == 0);
    REQUIRE(m.lod1_index_count < lod0_indices);  // actually decimated
    REQUIRE(m.lod1_ebo_byte_offset == indices_before * sizeof(uint32_t));
    REQUIRE(sd.indices.size() == indices_before + m.lod1_index_count);

    // LOD1 indices live in the appended slice and must reference real vertices
    // within this mesh.
    const uint32_t first = m.lod1_ebo_byte_offset / uint32_t(sizeof(uint32_t));
    for (uint32_t k = 0; k < m.lod1_index_count; ++k) {
        REQUIRE(sd.indices[first + k] < m.vertex_count);
    }
}

TEST_CASE("buildLods is deterministic for the same input", "[lod]") {
    ScopedEnvIsolate guard;
    SidecarData a = makeGridMesh(30);
    SidecarData b = makeGridMesh(30);

    buildLods(a);
    buildLods(b);

    REQUIRE(a.meshes[0].lod1_index_count == b.meshes[0].lod1_index_count);
    REQUIRE(a.meshes[0].lod1_ebo_byte_offset == b.meshes[0].lod1_ebo_byte_offset);
    REQUIRE(a.indices == b.indices);
}

TEST_CASE("buildLods is a no-op when sd is empty", "[lod]") {
    ScopedEnvIsolate guard;
    SidecarData sd;
    buildLods(sd);
    REQUIRE(sd.meshes.empty());
    REQUIRE(sd.vertices.empty());
    REQUIRE(sd.indices.empty());
}

TEST_CASE("summariseLods is consistent before and after buildLods", "[lod]") {
    ScopedEnvIsolate guard;
    SidecarData sd = makeGridMesh(30);

    LodStats before = summariseLods(sd);
    REQUIRE(before.meshes_total == 1);
    REQUIRE(before.meshes_with_lod1 == 0);
    REQUIRE(before.tris_lod0 == sd.meshes[0].index_count / 3);
    REQUIRE(before.tris_lod1 == 0);
    REQUIRE(before.tris_lod0_for_lod1 == 0);

    buildLods(sd);
    LodStats after = summariseLods(sd);

    REQUIRE(after.meshes_total == before.meshes_total);
    REQUIRE(after.tris_lod0 == before.tris_lod0);  // LOD0 untouched
    REQUIRE(after.meshes_with_lod1 == 1);
    REQUIRE(after.tris_lod0_for_lod1 == before.tris_lod0);
    REQUIRE(after.tris_lod1 == sd.meshes[0].lod1_index_count / 3);
    REQUIRE(after.tris_lod1 < after.tris_lod0_for_lod1);
}
