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

namespace {

struct Centroid {
    float x, y, z;
};

Centroid computeCentroid(const BvhItem& it) {
    return {
        (it.aabb_min[0] + it.aabb_max[0]) * 0.5f,
        (it.aabb_min[1] + it.aabb_max[1]) * 0.5f,
        (it.aabb_min[2] + it.aabb_max[2]) * 0.5f
    };
}

void computeAABB(const std::vector<BvhItem>& items,
                 const uint32_t* indices, uint32_t count,
                 float out_min[3], float out_max[3]) {
    out_min[0] = out_min[1] = out_min[2] = std::numeric_limits<float>::max();
    out_max[0] = out_max[1] = out_max[2] = -std::numeric_limits<float>::max();
    for (uint32_t i = 0; i < count; ++i) {
        const auto& it = items[indices[i]];
        for (int a = 0; a < 3; ++a) {
            if (it.aabb_min[a] < out_min[a]) out_min[a] = it.aabb_min[a];
            if (it.aabb_max[a] > out_max[a]) out_max[a] = it.aabb_max[a];
        }
    }
}

void buildRecursive(ModelBvh& mbvh,
                    const std::vector<BvhItem>& items,
                    uint32_t start, uint32_t count) {
    uint32_t node_idx = static_cast<uint32_t>(mbvh.nodes.size());
    mbvh.nodes.emplace_back();
    BvhNode& node = mbvh.nodes[node_idx];

    computeAABB(items, &mbvh.item_indices[start], count,
                node.aabb_min, node.aabb_max);

    if (count <= BVH_MAX_LEAF_SIZE) {
        node.right_or_first = start;
        node.count = static_cast<uint16_t>(count);
        node.axis = 0;
        return;
    }

    float extent[3] = {
        node.aabb_max[0] - node.aabb_min[0],
        node.aabb_max[1] - node.aabb_min[1],
        node.aabb_max[2] - node.aabb_min[2]
    };
    int axis = 0;
    if (extent[1] > extent[axis]) axis = 1;
    if (extent[2] > extent[axis]) axis = 2;

    uint32_t mid = count / 2;
    std::nth_element(
        mbvh.item_indices.begin() + start,
        mbvh.item_indices.begin() + start + mid,
        mbvh.item_indices.begin() + start + count,
        [&](uint32_t a, uint32_t b) {
            Centroid ca = computeCentroid(items[a]);
            Centroid cb = computeCentroid(items[b]);
            return (&ca.x)[axis] < (&cb.x)[axis];
        });

    node.count = 0;
    node.axis = static_cast<uint16_t>(axis);

    buildRecursive(mbvh, items, start, mid);

    uint32_t right_child_idx = static_cast<uint32_t>(mbvh.nodes.size());
    buildRecursive(mbvh, items, start + mid, count - mid);

    mbvh.nodes[node_idx].right_or_first = right_child_idx;
}

ModelBvh buildModelBvh(const std::vector<BvhItem>& items,
                       const std::vector<uint32_t>& model_item_indices,
                       uint32_t model_id) {
    ModelBvh mbvh;
    mbvh.model_id = model_id;
    mbvh.item_indices = model_item_indices;

    uint32_t count = static_cast<uint32_t>(model_item_indices.size());
    if (count == 0) return mbvh;

    mbvh.nodes.reserve(count * 2);
    buildRecursive(mbvh, items, 0, count);

    assert(!mbvh.nodes.empty());
    return mbvh;
}

} // anonymous namespace

ModelBvh buildModelBvhOne(const std::vector<BvhItem>& items, uint32_t model_id) {
    std::vector<uint32_t> idxs(items.size());
    for (uint32_t i = 0; i < items.size(); ++i) idxs[i] = i;
    return buildModelBvh(items, idxs, model_id);
}

std::shared_ptr<BvhSet> buildBvhSet(const std::vector<BvhItem>& items) {
    auto bvh_set = std::make_shared<BvhSet>();

    std::unordered_map<uint32_t, std::vector<uint32_t>> model_items;
    for (uint32_t i = 0; i < static_cast<uint32_t>(items.size()); ++i) {
        model_items[items[i].model_id].push_back(i);
    }

    for (auto& [model_id, idxs] : model_items) {
        if (idxs.size() < BVH_MIN_OBJECTS) continue;

        ModelBvh mbvh = buildModelBvh(items, idxs, model_id);
        bvh_set->bvh_model_ids.insert(model_id);
        bvh_set->models[model_id] = std::move(mbvh);
    }

    return bvh_set;
}
