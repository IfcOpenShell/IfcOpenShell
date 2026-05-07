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

// Tier-1 coverage of the instanced-geometry GPU/sidecar layout.
//
// The production quantization helpers currently live inside
// ViewportWindow.cpp (see uploadMeshChunk).  Once they're factored out into a
// reusable header (planned tier-3 prerequisite) this test will exercise the
// real implementation directly.  For now we cover:
//   - runtime size/alignment assertions (defense in depth for the static_asserts)
//   - documented constants form a self-consistent layout
//   - a reference position-quantization round-trip that pins the error bound
//     declared in InstancedGeometry.h ("dequant to mix(aabb_min, aabb_max, t)")

#include "InstancedGeometry.h"

#include <catch2/catch_test_macros.hpp>

#include <cmath>
#include <cstdint>

TEST_CASE("Instanced GPU/CPU struct sizes match the wire format", "[instgeom]") {
    REQUIRE(sizeof(MeshGpu) == 32);
    REQUIRE(sizeof(MeshInfo) == 56);
    REQUIRE(sizeof(InstanceGpu) == 80);
    REQUIRE(alignof(MeshGpu) == 16);
    REQUIRE(alignof(InstanceGpu) == 16);
}

TEST_CASE("INSTANCED_VERTEX_* constants are self-consistent", "[instgeom]") {
    // Position (u16 x 3 = 6 B) + normal (i8 x 2 = 2 B) + color (u8 x 4 = 4 B)
    // packed contiguously with no implicit padding.
    REQUIRE(INSTANCED_VERTEX_POS_OFFSET == 0);
    REQUIRE(INSTANCED_VERTEX_NORMAL_OFFSET == 6);
    REQUIRE(INSTANCED_VERTEX_COLOR_OFFSET == 8);
    REQUIRE(INSTANCED_VERTEX_STRIDE_BYTES == 12);
    REQUIRE(INSTANCED_VERTEX_STRIDE_FLOATS == 7);
}

TEST_CASE("Position quantization round-trips within the documented error bound", "[instgeom]") {
    // The quantization basis is per-mesh: t = (p - min) / (max - min) packed
    // into u16, and dequantized as p' = min + t * (max - min).  The round-trip
    // error per axis is at most (max - min) / 65535 (one ulp of the u16 grid).
    const float aabb_min[3] = {-3.5f, 100.25f, -1000.0f};
    const float aabb_max[3] = { 7.5f, 200.25f,  1000.0f};
    const float extent[3] = {
        aabb_max[0] - aabb_min[0],
        aabb_max[1] - aabb_min[1],
        aabb_max[2] - aabb_min[2],
    };

    constexpr int kSamples = 65;
    float worst_err = 0.0f;
    for (int s = 0; s <= kSamples; ++s) {
        float t = float(s) / float(kSamples);
        for (int a = 0; a < 3; ++a) {
            float p = aabb_min[a] + t * extent[a];

            // Pack (the same formula buildLods/the streamer use against an AABB).
            float tt = (p - aabb_min[a]) / extent[a];
            if (tt < 0.0f) tt = 0.0f;
            if (tt > 1.0f) tt = 1.0f;
            uint16_t q = uint16_t(tt * 65535.0f + 0.5f);

            // Unpack (matches the dequant in LodBuilder.cpp).
            float pp = aabb_min[a] + (q / 65535.0f) * extent[a];

            float err = std::fabs(pp - p);
            if (err > worst_err) worst_err = err;
        }
    }

    // The round-trip error must stay within one u16 ulp of the largest extent,
    // with a small float-rounding margin.
    float ulp = 0.0f;
    for (int a = 0; a < 3; ++a) {
        ulp = std::max(ulp, extent[a] / 65535.0f);
    }
    REQUIRE(worst_err <= ulp * 1.01f);
}

TEST_CASE("MeshChunk and InstanceChunk default-init to zeroed metadata", "[instgeom]") {
    MeshChunk mc;
    REQUIRE(mc.model_id == 0);
    REQUIRE(mc.local_mesh_id == 0);
    REQUIRE(mc.vertices.empty());
    REQUIRE(mc.indices.empty());

    InstanceChunk ic;
    REQUIRE(ic.model_id == 0);
    REQUIRE(ic.local_mesh_id == 0);
    REQUIRE(ic.object_id == 0);
    REQUIRE(ic.color_override_rgba8 == 0);
}
