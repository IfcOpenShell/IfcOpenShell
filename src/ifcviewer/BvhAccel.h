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

struct ObjectDrawInfo {
    uint32_t index_offset;  // byte offset into EBO
    uint32_t index_count;   // number of indices
    uint32_t model_id;      // which model this object belongs to
    float aabb_min[3];      // world-space AABB
    float aabb_max[3];
};

static constexpr uint32_t BVH_MAX_LEAF_SIZE = 8;
static constexpr uint32_t BVH_MIN_OBJECTS = 32;

struct BvhNode {
    float aabb_min[3];
    float aabb_max[3];
    uint32_t right_or_first; // interior: right child index (left is always this_index+1); leaf: first object index
    uint16_t count;           // 0 = interior; >0 = leaf with this many objects
    uint16_t axis;            // split axis (0/1/2) for interior; unused for leaf
};
static_assert(sizeof(BvhNode) == 32, "BvhNode must be 32 bytes for cache alignment and sidecar format");

struct ModelBvh {
    uint32_t model_id = 0;
    std::vector<BvhNode> nodes;
    std::vector<uint32_t> object_indices;  // indices into object_draw_info_
};

struct BvhSet {
    std::unordered_map<uint32_t, ModelBvh> models;
    std::unordered_set<uint32_t> bvh_model_ids;
};

struct EboReorderResult {
    std::vector<uint32_t> reordered_ebo;
    std::vector<ObjectDrawInfo> reordered_draw_info;
};

// Build BVH trees for all models in the given draw info snapshot.
// Only builds the tree structure; does not touch EBO data.
std::shared_ptr<BvhSet> buildBvhSet(const std::vector<ObjectDrawInfo>& draw_info);

// Reorder the EBO so objects within each BVH leaf are contiguous.
// Must be called with the CURRENT run's EBO and draw_info (not cached).
EboReorderResult reorderEbo(const BvhSet& bvh_set,
                            const std::vector<ObjectDrawInfo>& draw_info,
                            const std::vector<uint32_t>& original_ebo);

#endif // BVHACCEL_H
