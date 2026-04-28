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

#include "BvhAccel.h"

#include <catch2/catch_test_macros.hpp>

#include <random>
#include <vector>

namespace {

BvhItem makeItem(float x, float y, float z, float r, uint32_t model_id = 1) {
    BvhItem it{};
    it.aabb_min[0] = x - r;
    it.aabb_min[1] = y - r;
    it.aabb_min[2] = z - r;
    it.aabb_max[0] = x + r;
    it.aabb_max[1] = y + r;
    it.aabb_max[2] = z + r;
    it.model_id = model_id;
    return it;
}

bool aabbContains(const float outer_min[3], const float outer_max[3],
                  const float inner_min[3], const float inner_max[3]) {
    for (int a = 0; a < 3; ++a) {
        if (inner_min[a] < outer_min[a]) return false;
        if (inner_max[a] > outer_max[a]) return false;
    }
    return true;
}

void verifyNode(const ModelBvh& mbvh,
                const std::vector<BvhItem>& items,
                uint32_t node_idx) {
    REQUIRE(node_idx < mbvh.nodes.size());
    const BvhNode& node = mbvh.nodes[node_idx];

    if (node.count > 0) {
        // Leaf: every item's AABB must be inside the node AABB.
        REQUIRE(node.count <= BVH_MAX_LEAF_SIZE);
        for (uint32_t k = 0; k < node.count; ++k) {
            uint32_t idx = mbvh.item_indices[node.right_or_first + k];
            REQUIRE(idx < items.size());
            REQUIRE(aabbContains(node.aabb_min, node.aabb_max,
                                 items[idx].aabb_min, items[idx].aabb_max));
        }
        return;
    }

    // Interior: left child is at node_idx + 1, right at node.right_or_first.
    uint32_t left_idx  = node_idx + 1;
    uint32_t right_idx = node.right_or_first;
    REQUIRE(left_idx  < mbvh.nodes.size());
    REQUIRE(right_idx < mbvh.nodes.size());
    REQUIRE(left_idx  != right_idx);

    const BvhNode& l = mbvh.nodes[left_idx];
    const BvhNode& r = mbvh.nodes[right_idx];
    REQUIRE(aabbContains(node.aabb_min, node.aabb_max, l.aabb_min, l.aabb_max));
    REQUIRE(aabbContains(node.aabb_min, node.aabb_max, r.aabb_min, r.aabb_max));
    REQUIRE(node.axis < 3);

    verifyNode(mbvh, items, left_idx);
    verifyNode(mbvh, items, right_idx);
}

} // namespace

TEST_CASE("BvhNode is 32 bytes (sidecar/cache layout invariant)", "[bvh]") {
    REQUIRE(sizeof(BvhNode) == 32);
}

TEST_CASE("buildModelBvhOne on empty input produces no nodes", "[bvh]") {
    std::vector<BvhItem> items;
    ModelBvh mbvh = buildModelBvhOne(items, /*model_id=*/42);
    REQUIRE(mbvh.model_id == 42);
    REQUIRE(mbvh.nodes.empty());
    REQUIRE(mbvh.item_indices.empty());
}

TEST_CASE("buildModelBvhOne with <= BVH_MAX_LEAF_SIZE items yields a single leaf", "[bvh]") {
    std::vector<BvhItem> items;
    for (int i = 0; i < 5; ++i) {
        items.push_back(makeItem(float(i), 0.0f, 0.0f, 0.5f));
    }
    ModelBvh mbvh = buildModelBvhOne(items, 1);
    REQUIRE(mbvh.nodes.size() == 1);
    REQUIRE(mbvh.nodes[0].count == 5);
    REQUIRE(mbvh.item_indices.size() == 5);
    verifyNode(mbvh, items, 0);
}

TEST_CASE("buildModelBvhOne with many items splits and respects invariants", "[bvh]") {
    std::mt19937 rng(0xC0FFEE);
    std::uniform_real_distribution<float> coord(-100.0f, 100.0f);
    std::uniform_real_distribution<float> radius(0.1f, 1.0f);

    constexpr int N = 256;
    std::vector<BvhItem> items;
    items.reserve(N);
    for (int i = 0; i < N; ++i) {
        items.push_back(makeItem(coord(rng), coord(rng), coord(rng), radius(rng)));
    }

    ModelBvh mbvh = buildModelBvhOne(items, /*model_id=*/7);
    REQUIRE(mbvh.model_id == 7);
    REQUIRE(!mbvh.nodes.empty());
    REQUIRE(mbvh.item_indices.size() == N);

    // Permutation invariant: each item must appear exactly once.
    std::vector<int> seen(N, 0);
    for (uint32_t idx : mbvh.item_indices) {
        REQUIRE(idx < uint32_t(N));
        seen[idx]++;
    }
    for (int s : seen) REQUIRE(s == 1);

    // Recursive structural invariants.
    verifyNode(mbvh, items, 0);

    // Sum of leaf counts must equal item count.
    uint32_t leaf_total = 0;
    for (const auto& n : mbvh.nodes) {
        if (n.count > 0) leaf_total += n.count;
    }
    REQUIRE(leaf_total == N);
}

TEST_CASE("buildBvhSet partitions by model_id and gates on BVH_MIN_OBJECTS", "[bvh]") {
    // Model 1: well above BVH_MIN_OBJECTS — should get a BVH.
    // Model 2: a single item — below the gate, must be skipped.
    std::vector<BvhItem> items;
    for (uint32_t i = 0; i < BVH_MIN_OBJECTS + 4; ++i) {
        items.push_back(makeItem(float(i), 0.0f, 0.0f, 0.5f, /*model_id=*/1));
    }
    items.push_back(makeItem(0.0f, 0.0f, 0.0f, 0.5f, /*model_id=*/2));

    auto set = buildBvhSet(items);
    REQUIRE(set);
    REQUIRE(set->bvh_model_ids.count(1) == 1);
    REQUIRE(set->bvh_model_ids.count(2) == 0);
    REQUIRE(set->models.count(1) == 1);
    REQUIRE(set->models.count(2) == 0);

    const auto& mbvh = set->models.at(1);
    REQUIRE(mbvh.model_id == 1);
    REQUIRE(mbvh.item_indices.size() == BVH_MIN_OBJECTS + 4);
    // item_indices reference positions in the *full* items array — the model-1
    // items are at indices [0, BVH_MIN_OBJECTS + 4), so every entry must be
    // less than that.
    for (uint32_t idx : mbvh.item_indices) {
        REQUIRE(idx < BVH_MIN_OBJECTS + 4);
    }
    verifyNode(mbvh, items, 0);
}

TEST_CASE("buildBvhSet returns empty set when nothing meets the gate", "[bvh]") {
    std::vector<BvhItem> items;
    for (uint32_t i = 0; i < BVH_MIN_OBJECTS - 1; ++i) {
        items.push_back(makeItem(float(i), 0.0f, 0.0f, 0.5f));
    }
    auto set = buildBvhSet(items);
    REQUIRE(set);
    REQUIRE(set->bvh_model_ids.empty());
    REQUIRE(set->models.empty());
}
