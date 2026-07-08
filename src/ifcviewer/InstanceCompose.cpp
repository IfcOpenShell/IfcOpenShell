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

#include "InstanceCompose.h"

#include <cstring>
#include <limits>

namespace InstanceCompose {

void worldAabbFromLocal(const float local_min[3], const float local_max[3],
                        const float M[16],
                        float world_min_out[3], float world_max_out[3]) {
    world_min_out[0] = world_min_out[1] = world_min_out[2] =
         std::numeric_limits<float>::max();
    world_max_out[0] = world_max_out[1] = world_max_out[2] =
        -std::numeric_limits<float>::max();
    for (int c = 0; c < 8; ++c) {
        const float x = (c & 1) ? local_max[0] : local_min[0];
        const float y = (c & 2) ? local_max[1] : local_min[1];
        const float z = (c & 4) ? local_max[2] : local_min[2];
        const float wx = M[0]*x + M[4]*y + M[8] *z + M[12];
        const float wy = M[1]*x + M[5]*y + M[9] *z + M[13];
        const float wz = M[2]*x + M[6]*y + M[10]*z + M[14];
        if (wx < world_min_out[0]) world_min_out[0] = wx;
        if (wx > world_max_out[0]) world_max_out[0] = wx;
        if (wy < world_min_out[1]) world_min_out[1] = wy;
        if (wy > world_max_out[1]) world_max_out[1] = wy;
        if (wz < world_min_out[2]) world_min_out[2] = wz;
        if (wz > world_max_out[2]) world_max_out[2] = wz;
    }
}

void composeInstance(
        const double placement_col_major[16],
        const Eigen::Matrix4d& federated_false_origin,
        const Eigen::Matrix4d& model_transformation,
        const Eigen::Matrix4d& coordinate_operation,
        const float local_aabb_min[3], const float local_aabb_max[3],
        float transform_col_major_out[16],
        float world_aabb_min_out[3], float world_aabb_max_out[3]) {
    using Mat4dCol = Eigen::Matrix<double, 4, 4, Eigen::ColMajor>;
    using Mat4fCol = Eigen::Matrix<float,  4, 4, Eigen::ColMajor>;

    const Eigen::Matrix4d P =
        Eigen::Map<const Mat4dCol>(placement_col_major);
    const Eigen::Matrix4d composed =
        federated_false_origin *
        model_transformation *
        coordinate_operation *
        P;

    Eigen::Map<Mat4fCol> T_f(transform_col_major_out);
    T_f = composed.cast<float>();

    worldAabbFromLocal(local_aabb_min, local_aabb_max,
                       transform_col_major_out,
                       world_aabb_min_out, world_aabb_max_out);
}

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

} // namespace InstanceCompose
