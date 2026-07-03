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

// Tier-1 coverage of the instanced-geometry GPU/sidecar layout and the
// vertex quantization used to fill it.
//
// quantizeVertex / octEncodeNormal (VertexQuantization.h) are the shared
// production helpers: ViewportWindow::uploadStreamedMesh and SidecarBuilder both
// route through them so the rendered VBO and the on-disk .ifcview record are
// byte-identical.  The tests exercise that real implementation directly:
//   - runtime size/alignment assertions (defense in depth for the static_asserts)
//   - documented INSTANCED_VERTEX_* constants form a self-consistent layout
//   - position quantization round-trips within the u16-grid error bound
//   - octahedral normal encode/decode round-trips, and the i8-packed normal
//     written by quantizeVertex stays within its documented angular error

#include "InstancedGeometry.h"
#include "VertexQuantization.h"

#include <catch2/catch_test_macros.hpp>

#include <cmath>
#include <cstdint>
#include <cstring>

namespace {

// Inverse of octEncodeNormal: square [-1,1]^2 -> unit sphere.  The test owns
// the decode (the production header only ships the encoder, since the GPU
// shader does the decode); it is the standard Meyer et al. octahedral unfold.
void octDecodeNormal(const float e[2], float out[3]) {
    float x = e[0];
    float y = e[1];
    float z = 1.0f - std::fabs(x) - std::fabs(y);
    if (z < 0.0f) {
        float ox = (1.0f - std::fabs(y)) * (x >= 0.0f ? 1.0f : -1.0f);
        float oy = (1.0f - std::fabs(x)) * (y >= 0.0f ? 1.0f : -1.0f);
        x = ox;
        y = oy;
    }
    float len = std::sqrt(x * x + y * y + z * z);
    out[0] = x / len;
    out[1] = y / len;
    out[2] = z / len;
}

// Angle (degrees) between two unit-ish vectors.
float angleDeg(const float a[3], const float b[3]) {
    float dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    if (dot > 1.0f) dot = 1.0f;
    if (dot < -1.0f) dot = -1.0f;
    return std::acos(dot) * (180.0f / 3.14159265358979323846f);
}

} // namespace

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

TEST_CASE("quantizeVertex round-trips position within the documented error bound",
          "[instgeom]") {
    // The quantization basis is per-mesh: t = (p - min) / (max - min) packed
    // into u16, dequantized as p' = min + (q / 65535) * (max - min).  The
    // round-trip error per axis is at most (max - min) / 65535 (one ulp of the
    // u16 grid).
    const float aabb_min[3]     = {-3.5f, 100.25f, -1000.0f};
    const float aabb_max[3]     = { 7.5f, 200.25f,  1000.0f};
    const float extent[3]       = {
        aabb_max[0] - aabb_min[0],
        aabb_max[1] - aabb_min[1],
        aabb_max[2] - aabb_min[2],
    };
    const float extent_recip[3] = {
        1.0f / extent[0], 1.0f / extent[1], 1.0f / extent[2],
    };

    constexpr int kSamples = 65;
    float worst_err = 0.0f;
    for (int s = 0; s <= kSamples; ++s) {
        float t = float(s) / float(kSamples);

        // A streamer-format vertex: pos3 + normal3 + color-as-float.
        float src[INSTANCED_VERTEX_STRIDE_FLOATS] = {0};
        for (int a = 0; a < 3; ++a) src[a] = aabb_min[a] + t * extent[a];
        src[5] = 1.0f;  // arbitrary valid normal (0,0,1)

        uint8_t dst[INSTANCED_VERTEX_STRIDE_BYTES];
        quantizeVertex(src, aabb_min, extent_recip, dst);

        const uint16_t* q =
            reinterpret_cast<const uint16_t*>(dst + INSTANCED_VERTEX_POS_OFFSET);
        for (int a = 0; a < 3; ++a) {
            float pp = aabb_min[a] + (q[a] / 65535.0f) * extent[a];
            float err = std::fabs(pp - src[a]);
            if (err > worst_err) worst_err = err;
        }
    }

    // Worst error must stay within one u16 ulp of the largest extent, with a
    // small float-rounding margin.
    float ulp = 0.0f;
    for (int a = 0; a < 3; ++a) {
        ulp = std::max(ulp, extent[a] / 65535.0f);
    }
    REQUIRE(worst_err <= ulp * 1.01f);
}

TEST_CASE("quantizeVertex handles a degenerate (zero-extent) axis", "[instgeom]") {
    // A planar mesh has a flat axis: extent_recip is 0 there (see the header
    // contract).  Every vertex on that axis must quantize to 0, not NaN.
    const float aabb_min[3]     = {0.0f, 0.0f, 5.0f};
    const float extent_recip[3] = {1.0f, 1.0f, 0.0f};  // Z is degenerate

    float src[INSTANCED_VERTEX_STRIDE_FLOATS] = {0};
    src[0] = 0.5f; src[1] = 0.25f; src[2] = 5.0f;
    src[5] = 1.0f;

    uint8_t dst[INSTANCED_VERTEX_STRIDE_BYTES];
    quantizeVertex(src, aabb_min, extent_recip, dst);

    const uint16_t* q =
        reinterpret_cast<const uint16_t*>(dst + INSTANCED_VERTEX_POS_OFFSET);
    REQUIRE(q[2] == 0);  // degenerate axis collapses to the grid origin
}

TEST_CASE("octEncodeNormal / octDecodeNormal round-trip unit normals", "[instgeom]") {
    // The float-precision oct map is a bijection on the sphere — encode then
    // decode must recover the original direction tightly (the i8 packing,
    // which adds the real error, is covered separately below).
    const float normals[][3] = {
        { 1, 0, 0}, {-1, 0, 0}, {0,  1, 0}, {0, -1, 0},
        { 0, 0, 1}, { 0, 0,-1},                       // axis-aligned
        { 0.5773503f,  0.5773503f,  0.5773503f},      // +++ diagonal
        {-0.5773503f, -0.5773503f, -0.5773503f},      // --- diagonal (z < 0 fold)
        { 0.7071068f,  0.0f,       -0.7071068f},      // z < 0 fold
        { 0.2672612f,  0.5345225f,  0.8017837f},      // arbitrary
    };

    for (const auto& n : normals) {
        float e[2];
        octEncodeNormal(n, e);
        REQUIRE(e[0] >= -1.0f);
        REQUIRE(e[0] <=  1.0f);
        REQUIRE(e[1] >= -1.0f);
        REQUIRE(e[1] <=  1.0f);

        float decoded[3];
        octDecodeNormal(e, decoded);
        INFO("normal (" << n[0] << ", " << n[1] << ", " << n[2] << ")");
        REQUIRE(angleDeg(n, decoded) < 0.01f);
    }
}

TEST_CASE("quantizeVertex packs the normal within its documented i8 error bound",
          "[instgeom]") {
    // quantizeVertex stores the octahedral normal as i8 x 2.  The header
    // documents "~1.4 deg worst-case error" for that packing; sweep a dense
    // set of directions and pin the worst observed error well below a 3 deg
    // regression ceiling (a broken encoder is off by tens of degrees).
    const float aabb_min[3]     = {0, 0, 0};
    const float extent_recip[3] = {1, 1, 1};

    float worst_err = 0.0f;
    constexpr int kSteps = 40;
    for (int i = 0; i <= kSteps; ++i) {
        for (int j = 0; j <= kSteps; ++j) {
            // Spherical sweep over the full sphere.
            float theta = 3.14159265f * float(i) / float(kSteps);          // polar
            float phi   = 2.0f * 3.14159265f * float(j) / float(kSteps);   // azimuth
            float n[3] = {
                std::sin(theta) * std::cos(phi),
                std::sin(theta) * std::sin(phi),
                std::cos(theta),
            };

            float src[INSTANCED_VERTEX_STRIDE_FLOATS] = {0};
            src[3] = n[0]; src[4] = n[1]; src[5] = n[2];

            uint8_t dst[INSTANCED_VERTEX_STRIDE_BYTES];
            quantizeVertex(src, aabb_min, extent_recip, dst);

            // Decode the stored i8 oct pair back to a direction.
            const int8_t* packed =
                reinterpret_cast<const int8_t*>(dst + INSTANCED_VERTEX_NORMAL_OFFSET);
            float e[2] = {packed[0] / 127.0f, packed[1] / 127.0f};
            float decoded[3];
            octDecodeNormal(e, decoded);

            worst_err = std::max(worst_err, angleDeg(n, decoded));
        }
    }

    INFO("worst i8 octahedral normal error: " << worst_err << " deg");
    REQUIRE(worst_err > 0.0f);   // sanity: quantization is actually lossy
    REQUIRE(worst_err < 3.0f);   // regression ceiling around the documented ~1.4 deg
}

TEST_CASE("quantizeVertex passes the packed color through unchanged", "[instgeom]") {
    // The streamer packs an rgba8 into the 7th float slot; quantizeVertex
    // memcpy's those 4 bytes straight into the VBO color field.
    const uint8_t rgba[4] = {0x11, 0x22, 0x33, 0x44};
    float color_as_float;
    std::memcpy(&color_as_float, rgba, 4);

    const float aabb_min[3]     = {0, 0, 0};
    const float extent_recip[3] = {1, 1, 1};
    float src[INSTANCED_VERTEX_STRIDE_FLOATS] = {0};
    src[5] = 1.0f;            // valid normal
    src[6] = color_as_float;  // color slot

    uint8_t dst[INSTANCED_VERTEX_STRIDE_BYTES];
    quantizeVertex(src, aabb_min, extent_recip, dst);

    REQUIRE(std::memcmp(dst + INSTANCED_VERTEX_COLOR_OFFSET, rgba, 4) == 0);
}

TEST_CASE("StreamedMesh and StreamedInstance default-init to zeroed metadata", "[instgeom]") {
    StreamedMesh mc;
    REQUIRE(mc.model_id == 0);
    REQUIRE(mc.local_mesh_id == 0);
    REQUIRE(mc.vertices.empty());
    REQUIRE(mc.indices.empty());

    StreamedInstance ic;
    REQUIRE(ic.model_id == 0);
    REQUIRE(ic.local_mesh_id == 0);
    REQUIRE(ic.object_id == 0);
    REQUIRE(ic.color_override_rgba8 == 0);
}
