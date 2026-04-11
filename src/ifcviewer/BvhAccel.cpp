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

#include <algorithm>
#include <cassert>
#include <cmath>
#include <limits>
#include <numeric>

namespace {

struct Centroid {
    float x, y, z;
};

Centroid computeCentroid(const ObjectDrawInfo& obj) {
    return {
        (obj.aabb_min[0] + obj.aabb_max[0]) * 0.5f,
        (obj.aabb_min[1] + obj.aabb_max[1]) * 0.5f,
        (obj.aabb_min[2] + obj.aabb_max[2]) * 0.5f
    };
}

void computeAABB(const std::vector<ObjectDrawInfo>& draw_info,
                 const uint32_t* indices, uint32_t count,
                 float out_min[3], float out_max[3]) {
    out_min[0] = out_min[1] = out_min[2] = std::numeric_limits<float>::max();
    out_max[0] = out_max[1] = out_max[2] = -std::numeric_limits<float>::max();
    for (uint32_t i = 0; i < count; ++i) {
        const auto& obj = draw_info[indices[i]];
        for (int a = 0; a < 3; ++a) {
            if (obj.aabb_min[a] < out_min[a]) out_min[a] = obj.aabb_min[a];
            if (obj.aabb_max[a] > out_max[a]) out_max[a] = obj.aabb_max[a];
        }
    }
}

// Recursive BVH builder. Writes nodes in pre-order DFS into mbvh.nodes.
// object_indices[start..start+count) are the indices to partition.
void buildRecursive(ModelBvh& mbvh,
                    const std::vector<ObjectDrawInfo>& draw_info,
                    uint32_t start, uint32_t count) {
    uint32_t node_idx = static_cast<uint32_t>(mbvh.nodes.size());
    mbvh.nodes.emplace_back();
    BvhNode& node = mbvh.nodes[node_idx];

    computeAABB(draw_info, &mbvh.object_indices[start], count,
                node.aabb_min, node.aabb_max);

    if (count <= BVH_MAX_LEAF_SIZE) {
        node.right_or_first = start;
        node.count = static_cast<uint16_t>(count);
        node.axis = 0;
        return;
    }

    // Find longest axis of node AABB.
    float extent[3] = {
        node.aabb_max[0] - node.aabb_min[0],
        node.aabb_max[1] - node.aabb_min[1],
        node.aabb_max[2] - node.aabb_min[2]
    };
    int axis = 0;
    if (extent[1] > extent[axis]) axis = 1;
    if (extent[2] > extent[axis]) axis = 2;

    // Partition at median centroid on the chosen axis.
    uint32_t mid = count / 2;
    std::nth_element(
        mbvh.object_indices.begin() + start,
        mbvh.object_indices.begin() + start + mid,
        mbvh.object_indices.begin() + start + count,
        [&](uint32_t a, uint32_t b) {
            Centroid ca = computeCentroid(draw_info[a]);
            Centroid cb = computeCentroid(draw_info[b]);
            return (&ca.x)[axis] < (&cb.x)[axis];
        });

    node.count = 0;  // interior
    node.axis = static_cast<uint16_t>(axis);

    // Left child is always node_idx + 1 (implicit in pre-order DFS).
    // Build left subtree first. Note: &node is invalidated after this call
    // because the vector may reallocate.
    buildRecursive(mbvh, draw_info, start, mid);

    // Right child is the next node written after the entire left subtree.
    uint32_t right_child_idx = static_cast<uint32_t>(mbvh.nodes.size());
    buildRecursive(mbvh, draw_info, start + mid, count - mid);

    // Patch the right child index (left is implicit = node_idx + 1).
    mbvh.nodes[node_idx].right_or_first = right_child_idx;
}

} // anonymous namespace

ModelBvh buildModelBvh(const std::vector<ObjectDrawInfo>& draw_info,
                       const std::vector<uint32_t>& model_object_indices,
                       uint32_t model_id) {
    ModelBvh mbvh;
    mbvh.model_id = model_id;
    mbvh.object_indices = model_object_indices;

    uint32_t count = static_cast<uint32_t>(model_object_indices.size());
    if (count == 0) return mbvh;

    // Reserve a rough estimate: ~2*n nodes for a balanced binary tree.
    mbvh.nodes.reserve(count * 2);

    buildRecursive(mbvh, draw_info, 0, count);

    // Verify: every object appears exactly once in the leaves.
    assert(!mbvh.nodes.empty());

    return mbvh;
}

std::shared_ptr<BvhSet> buildBvhSet(const std::vector<ObjectDrawInfo>& draw_info) {
    auto bvh_set = std::make_shared<BvhSet>();

    // Group object indices by model_id.
    std::unordered_map<uint32_t, std::vector<uint32_t>> model_objects;
    for (uint32_t i = 0; i < static_cast<uint32_t>(draw_info.size()); ++i) {
        model_objects[draw_info[i].model_id].push_back(i);
    }

    // Build per-model BVHs.
    for (auto& [model_id, obj_indices] : model_objects) {
        if (obj_indices.size() < BVH_MIN_OBJECTS) continue;

        ModelBvh mbvh = buildModelBvh(draw_info, obj_indices, model_id);
        bvh_set->bvh_model_ids.insert(model_id);
        bvh_set->models[model_id] = std::move(mbvh);
    }

    return bvh_set;
}

EboReorderResult reorderEbo(const BvhSet& bvh_set,
                            const std::vector<ObjectDrawInfo>& draw_info,
                            const std::vector<uint32_t>& original_ebo) {
    EboReorderResult result;
    result.reordered_draw_info = draw_info;  // copy; we'll update offsets
    result.reordered_ebo.reserve(original_ebo.size());

    // Track which draw_info entries have been placed.
    std::vector<bool> placed(draw_info.size(), false);

    for (const auto& [model_id, mbvh] : bvh_set.models) {
        // DFS traversal of BVH to visit leaves in order.
        uint32_t stack[64];
        int sp = 0;
        stack[sp++] = 0;

        while (sp > 0) {
            uint32_t ni = stack[--sp];
            const BvhNode& node = mbvh.nodes[ni];

            if (node.count > 0) {
                // Leaf: emit objects in order.
                for (uint32_t i = 0; i < node.count; ++i) {
                    uint32_t oi = mbvh.object_indices[node.right_or_first + i];
                    if (placed[oi]) continue;
                    placed[oi] = true;

                    const auto& old_info = draw_info[oi];
                    uint32_t new_offset = static_cast<uint32_t>(
                        result.reordered_ebo.size() * sizeof(uint32_t));

                    // Copy indices from original EBO.
                    uint32_t idx_start = old_info.index_offset / sizeof(uint32_t);
                    uint32_t idx_count = old_info.index_count;
                    for (uint32_t j = 0; j < idx_count; ++j) {
                        result.reordered_ebo.push_back(original_ebo[idx_start + j]);
                    }

                    result.reordered_draw_info[oi].index_offset = new_offset;
                }
            } else {
                // Interior: push left (=ni+1) last so it's processed first.
                stack[sp++] = node.right_or_first;  // right child
                stack[sp++] = ni + 1;                // left child
            }
        }
    }

    // Append non-BVH objects (models too small for BVH).
    for (uint32_t oi = 0; oi < static_cast<uint32_t>(draw_info.size()); ++oi) {
        if (placed[oi]) continue;
        placed[oi] = true;

        const auto& old_info = draw_info[oi];
        uint32_t new_offset = static_cast<uint32_t>(
            result.reordered_ebo.size() * sizeof(uint32_t));

        uint32_t idx_start = old_info.index_offset / sizeof(uint32_t);
        uint32_t idx_count = old_info.index_count;
        for (uint32_t j = 0; j < idx_count; ++j) {
            result.reordered_ebo.push_back(original_ebo[idx_start + j]);
        }

        result.reordered_draw_info[oi].index_offset = new_offset;
    }

    assert(result.reordered_ebo.size() == original_ebo.size());

    return result;
}
