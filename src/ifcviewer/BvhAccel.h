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

#ifndef BVHACCEL_H
#define BVHACCEL_H

#include <cstdint>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>

// Generic BVH item — anything with a world AABB and a model_id.
// For the instanced renderer each item represents one InstanceCpu.
struct BvhItem {
    float    aabb_min[3];
    float    aabb_max[3];
    uint32_t model_id;
};

static constexpr uint32_t BVH_MAX_LEAF_SIZE = 8;
static constexpr uint32_t BVH_MIN_OBJECTS   = 32;

struct BvhNode {
    float    aabb_min[3];
    float    aabb_max[3];
    uint32_t right_or_first; // interior: right child index (left is always this_index+1); leaf: first item index
    uint16_t count;           // 0 = interior; >0 = leaf with this many items
    uint16_t axis;            // split axis (0/1/2) for interior; unused for leaf
};
static_assert(sizeof(BvhNode) == 32, "BvhNode must be 32 bytes for cache alignment and sidecar format");

struct ModelBvh {
    uint32_t model_id = 0;
    std::vector<BvhNode> nodes;
    std::vector<uint32_t> item_indices;  // indices into the model's InstanceCpu array
};

struct BvhSet {
    std::unordered_map<uint32_t, ModelBvh> models;
    std::unordered_set<uint32_t> bvh_model_ids;
};

// Build BVH trees for all models in the given item snapshot.
// Items are expected to already be grouped/filtered by caller if needed.
// item_indices in the result reference positions within the full `items`
// vector — callers providing a single model's items will see 0..N-1.
std::shared_ptr<BvhSet> buildBvhSet(const std::vector<BvhItem>& items);

#endif // BVHACCEL_H
