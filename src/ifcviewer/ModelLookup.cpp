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

#include "ModelLookup.h"

#include <cstring>
#include <limits>

namespace ModelLookup {

bool findInstanceInModels(
        uint32_t object_id,
        const std::unordered_map<uint32_t, ModelGpuData>& models,
        InstanceLookup& out) {
    if (object_id == 0) return false;
    for (const auto& [session_model_id, model_data] : models) {
        auto it = model_data.object_id_to_instance.find(object_id);
        if (it == model_data.object_id_to_instance.end()) continue;
        const uint32_t instance_index = it->second;
        if (instance_index >= model_data.instances.size()) continue;
        const InstanceInfo& instance = model_data.instances[instance_index];
        out.session_model_id = session_model_id;
        out.mesh_id  = instance.mesh_id;
        std::memcpy(out.placement_transformation,
                    instance.placement_transformation,
                    sizeof(out.placement_transformation));
        return true;
    }
    return false;
}

namespace {

// Start an AABB accumulator empty, so the first fold sets both corners.
void resetAabb(float mn[3], float mx[3]) {
    for (int i = 0; i < 3; ++i) {
        mn[i] =  std::numeric_limits<float>::infinity();
        mx[i] = -std::numeric_limits<float>::infinity();
    }
}

// Fold one model's instance world AABBs into an accumulator already reset.
// Returns whether the model contributed anything (an instance-less model — one
// whose metadata is up but whose geometry has not landed — contributes nothing).
bool foldModelAabb(const ModelGpuData& model_data, float mn[3], float mx[3]) {
    bool any = false;
    for (const InstanceInfo& instance : model_data.instances) {
        for (int i = 0; i < 3; ++i) {
            mn[i] = std::min(mn[i], instance.world_aabb_min[i]);
            mx[i] = std::max(mx[i], instance.world_aabb_max[i]);
        }
        any = true;
    }
    return any;
}

}  // namespace

bool sceneWorldAabb(const std::unordered_map<uint32_t, ModelGpuData>& models,
                    float world_min_out[3], float world_max_out[3]) {
    resetAabb(world_min_out, world_max_out);
    bool any = false;
    for (const auto& [session_model_id, model_data] : models) {
        if (model_data.hidden) continue;
        any |= foldModelAabb(model_data, world_min_out, world_max_out);
    }
    return any;
}

bool modelsWorldAabb(const std::unordered_map<uint32_t, ModelGpuData>& models,
                     const std::vector<uint32_t>& session_model_ids,
                     float world_min_out[3], float world_max_out[3]) {
    resetAabb(world_min_out, world_max_out);
    bool any = false;
    for (uint32_t session_model_id : session_model_ids) {
        auto it = models.find(session_model_id);
        if (it == models.end()) continue;
        any |= foldModelAabb(it->second, world_min_out, world_max_out);
    }
    return any;
}

} // namespace ModelLookup
