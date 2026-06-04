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

// Tier-1 coverage of ChunkPlanner. Both passes are pure CPU bookkeeping:
// the Morton sort orders mesh ids by Z-order code over centroids, and the
// greedy pack stamps the sorted sequence into chunks ≤ a bytes-budget.
// Tests use small, hand-checkable inputs so each assertion pins one
// invariant (locality, permutation closure, monotonic codes, packing
// monotonicity, single-mesh overflow, empty edge cases).

#include "ChunkPlanner.h"

#include <catch2/catch_all.hpp>

#include <algorithm>
#include <cstdint>
#include <set>
#include <vector>

// -----------------------------------------------------------------------------
// mortonSplit21 / mortonCode3D — primitive invariants
// -----------------------------------------------------------------------------

TEST_CASE("mortonSplit21 leaves zero bits between original bits", "[chunk_planner][morton]") {
    REQUIRE(ChunkPlanner::mortonSplit21(0u) == 0ull);

    // Every original 1-bit lands at position 3*k; the bits in between
    // stay zero. v=0b111 → 0b1001001 = 0x49.
    REQUIRE(ChunkPlanner::mortonSplit21(0b111u) == 0x49ull);

    // The high 11 bits above bit 20 must be discarded (mask 0x1FFFFF).
    REQUIRE(ChunkPlanner::mortonSplit21(1u << 21) == 0ull);
    REQUIRE(ChunkPlanner::mortonSplit21(0xFFFFFFFFu) ==
            ChunkPlanner::mortonSplit21(0x1FFFFFu));
}

TEST_CASE("mortonCode3D interleaves x and y and z onto bits 0/1/2 mod 3", "[chunk_planner][morton]") {
    REQUIRE(ChunkPlanner::mortonCode3D(0, 0, 0) == 0ull);

    // x = 1, y = 0, z = 0 → bit 0 set only.
    REQUIRE(ChunkPlanner::mortonCode3D(1, 0, 0) == 1ull);
    REQUIRE(ChunkPlanner::mortonCode3D(0, 1, 0) == 2ull);
    REQUIRE(ChunkPlanner::mortonCode3D(0, 0, 1) == 4ull);

    // All three set → 0b111.
    REQUIRE(ChunkPlanner::mortonCode3D(1, 1, 1) == 7ull);
}

TEST_CASE("mortonCode3D is monotone along each axis with others fixed", "[chunk_planner][morton]") {
    // Walking one axis up monotonically should make the code monotone in
    // that axis when the other two are zero (no carry from interleaving).
    for (uint32_t a = 0; a < 8; ++a) {
        REQUIRE(ChunkPlanner::mortonCode3D(a, 0, 0)
              < ChunkPlanner::mortonCode3D(a + 1, 0, 0));
        REQUIRE(ChunkPlanner::mortonCode3D(0, a, 0)
              < ChunkPlanner::mortonCode3D(0, a + 1, 0));
        REQUIRE(ChunkPlanner::mortonCode3D(0, 0, a)
              < ChunkPlanner::mortonCode3D(0, 0, a + 1));
    }
}

// -----------------------------------------------------------------------------
// sortMeshIdsByMorton — permutation + locality
// -----------------------------------------------------------------------------

TEST_CASE("Morton sort returns a permutation of all input ids", "[chunk_planner][sort]") {
    const std::size_t N = 32;
    std::vector<float> cx(N), cy(N), cz(N);
    std::vector<uint32_t> inst(N, 1);

    // Sprinkle centroids over a 1m grid.
    for (std::size_t i = 0; i < N; ++i) {
        cx[i] = float((i      ) & 0x3);
        cy[i] = float((i >> 2 ) & 0x3);
        cz[i] = float((i >> 4 ) & 0x1);
    }

    auto sorted = ChunkPlanner::sortMeshIdsByMorton(N, cx, cy, cz, inst);
    REQUIRE(sorted.size() == N);

    // Every input id appears exactly once.
    std::set<uint32_t> seen(sorted.begin(), sorted.end());
    REQUIRE(seen.size() == N);
    REQUIRE(*seen.begin()  == 0u);
    REQUIRE(*seen.rbegin() == uint32_t(N - 1));
}

TEST_CASE("Morton sort puts spatial neighbours close in the sequence", "[chunk_planner][sort]") {
    // Four corners of a unit square in the XY plane. We expect (0,0)
    // and (1,0) to appear adjacent in the sorted order, ditto (0,1)
    // and (1,1) — never (0,0) then (1,1) with a corner in between,
    // which is what the previous (z, y, x) lex sort would produce.
    //
    // mortonCode3D({0,1,0}, {0,0,1}, 0) over the quad:
    //   (0,0,0) → 0
    //   (1,0,0) → 1
    //   (0,1,0) → 2
    //   (1,1,0) → 3
    // So expected order: 0, 1, 2, 3 → ids that map to those codes.
    std::vector<float>    cx   = {0.f, 1.f, 0.f, 1.f};
    std::vector<float>    cy   = {0.f, 0.f, 1.f, 1.f};
    std::vector<float>    cz   = {0.f, 0.f, 0.f, 0.f};
    std::vector<uint32_t> inst = {1, 1, 1, 1};

    auto sorted = ChunkPlanner::sortMeshIdsByMorton(4, cx, cy, cz, inst);
    REQUIRE(sorted == std::vector<uint32_t>{0, 1, 2, 3});
}

TEST_CASE("Morton sort is stable on tied codes", "[chunk_planner][sort]") {
    // All four meshes share the same centroid → identical Morton
    // codes. stable_sort preserves their original id order.
    std::vector<float>    cx   = {0.f, 0.f, 0.f, 0.f};
    std::vector<float>    cy   = {0.f, 0.f, 0.f, 0.f};
    std::vector<float>    cz   = {0.f, 0.f, 0.f, 0.f};
    std::vector<uint32_t> inst = {1, 1, 1, 1};

    auto sorted = ChunkPlanner::sortMeshIdsByMorton(4, cx, cy, cz, inst);
    REQUIRE(sorted == std::vector<uint32_t>{0, 1, 2, 3});
}

// -----------------------------------------------------------------------------
// greedyPackChunks — packing rules
// -----------------------------------------------------------------------------

TEST_CASE("Empty input produces an empty chunk plan", "[chunk_planner][pack]") {
    auto chunks = ChunkPlanner::greedyPackChunks({}, {}, 12, 1024);
    REQUIRE(chunks.empty());
}

TEST_CASE("All meshes fit in one chunk under the bytes ceiling", "[chunk_planner][pack]") {
    // 4 meshes × 100 vertices × 12 B/v = 4800 B << 1 MB ceiling.
    std::vector<uint32_t> sorted    = {0, 1, 2, 3};
    std::vector<uint32_t> v_counts  = {100, 100, 100, 100};

    auto chunks = ChunkPlanner::greedyPackChunks(sorted, v_counts, 12, 1024 * 1024);
    REQUIRE(chunks.size() == 1);
    REQUIRE(chunks[0] == std::vector<uint32_t>{0, 1, 2, 3});
}

TEST_CASE("Greedy pack splits at the bytes ceiling while preserving order", "[chunk_planner][pack]") {
    // ceiling = 500 B; stride = 10 B. Each mesh: 200 B. Two fit (400 B),
    // a third doesn't (would exceed), so it starts a new chunk.
    std::vector<uint32_t> sorted   = {10, 20, 30, 40, 50};
    std::vector<uint32_t> v_counts(60, 0);
    for (uint32_t mi : sorted) v_counts[mi] = 20;   // 20 v × 10 B = 200 B

    auto chunks = ChunkPlanner::greedyPackChunks(sorted, v_counts, 10, 500);
    REQUIRE(chunks.size() == 3);
    REQUIRE(chunks[0] == std::vector<uint32_t>{10, 20});
    REQUIRE(chunks[1] == std::vector<uint32_t>{30, 40});
    REQUIRE(chunks[2] == std::vector<uint32_t>{50});
}

TEST_CASE("A mesh larger than the chunk ceiling gets its own oversized chunk", "[chunk_planner][pack]") {
    // First chunk holds the small mesh (200 B). The huge mesh (10_000 B)
    // alone exceeds the 500 B ceiling but still goes in one chunk —
    // the planner never splits a mesh across chunks.
    std::vector<uint32_t> sorted   = {0, 1, 2};
    std::vector<uint32_t> v_counts = {20, 1000, 20};   // 200 B, 10_000 B, 200 B

    auto chunks = ChunkPlanner::greedyPackChunks(sorted, v_counts, 10, 500);
    REQUIRE(chunks.size() == 3);
    REQUIRE(chunks[0] == std::vector<uint32_t>{0});
    REQUIRE(chunks[1] == std::vector<uint32_t>{1});   // oversized; alone
    REQUIRE(chunks[2] == std::vector<uint32_t>{2});
}

TEST_CASE("Every input mesh lands in exactly one chunk", "[chunk_planner][pack]") {
    // Heterogeneous sizes — confirm the planner is a partition: every
    // mesh id from `sorted` appears in some chunk exactly once, and
    // the per-chunk byte sums obey the ceiling (subject to the
    // single-mesh-oversize exception).
    std::vector<uint32_t> sorted   = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5};
    std::vector<uint32_t> v_counts(16, 0);
    v_counts[1] = 10; v_counts[2] = 20; v_counts[3] = 30; v_counts[4] = 50;
    v_counts[5] = 5;  v_counts[6] = 80; v_counts[9] = 15;

    const uint64_t stride = 12;
    const uint64_t ceil   = 500;
    auto chunks = ChunkPlanner::greedyPackChunks(sorted, v_counts, stride, ceil);

    std::vector<uint32_t> flat;
    for (const auto& c : chunks) {
        REQUIRE_FALSE(c.empty());
        for (auto mi : c) flat.push_back(mi);

        // Per-chunk byte tally check: either ≤ ceiling, or chunk has
        // exactly one mesh that singly exceeds it.
        uint64_t bytes = 0;
        for (auto mi : c) bytes += uint64_t(v_counts[mi]) * stride;
        if (bytes > ceil) {
            REQUIRE(c.size() == 1);
        }
    }
    // Multiset equality: same mesh ids, same multiplicity, same order.
    REQUIRE(flat == sorted);
}

TEST_CASE("Zero-size meshes don't create new chunks unnecessarily", "[chunk_planner][pack]") {
    // A mesh with vertex_count = 0 contributes 0 bytes; it should pack
    // into whatever the current chunk is without triggering a flush.
    std::vector<uint32_t> sorted   = {0, 1, 2, 3};
    std::vector<uint32_t> v_counts = {10, 0, 10, 0};

    auto chunks = ChunkPlanner::greedyPackChunks(sorted, v_counts, 10, 1000);
    REQUIRE(chunks.size() == 1);
    REQUIRE(chunks[0] == std::vector<uint32_t>{0, 1, 2, 3});
}
