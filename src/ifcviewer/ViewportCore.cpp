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

#include "ViewportCore.h"

#include "InstanceCompose.h"

ViewportCore::ViewportCore(ViewportHost* host) : host_(host) {}
ViewportCore::~ViewportCore() = default;

bool ViewportCore::findInstance(uint32_t object_id,
                                InstanceCompose::InstanceLookup& out) const {
    return InstanceCompose::findInstanceInModels(object_id, models_gpu_, out);
}

bool ViewportCore::firstGeometryPointWorldM(uint32_t model_id,
                                            Eigen::Vector3d& out) const {
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return false;
    const ModelGpuData& m = it->second;
    if (m.instances.empty()) return false;

    const InstanceCpu& inst0 = m.instances[0];
    if (inst0.mesh_id >= m.meshes.size()) return false;
    const MeshInfo& mesh0 = m.meshes[inst0.mesh_id];

    // Mesh-local AABB centre — a point that's actually on the geometry.
    // Using AABB centre (vs. literal vertex 0) gives a centroid-like
    // anchor rather than a corner, which is more representative of where
    // the mesh "is" for the false-origin guess.
    const Eigen::Vector3d local_center_m(
        0.5 * (double(mesh0.local_aabb_min[0]) + double(mesh0.local_aabb_max[0])),
        0.5 * (double(mesh0.local_aabb_min[1]) + double(mesh0.local_aabb_max[1])),
        0.5 * (double(mesh0.local_aabb_min[2]) + double(mesh0.local_aabb_max[2])));

    // placement_transformation is double[16] column-major in metres,
    // pre-CoordinateOperation / FederatedFalseOrigin / ModelTransformation
    // (same convention as InstanceLookup above).
    using Mat4dCol = Eigen::Matrix<double, 4, 4, Eigen::ColMajor>;
    const Eigen::Matrix4d P =
        Eigen::Map<const Mat4dCol>(inst0.placement_transformation);
    out = (P * local_center_m.homogeneous()).head<3>();
    return true;
}

void ViewportCore::composeInstanceFromPlacement(InstanceCpu& inst,
                                                const ModelGpuData& m) const {
    if (inst.mesh_id < m.meshes.size()) {
        const MeshInfo& mi = m.meshes[inst.mesh_id];
        InstanceCompose::composeInstance(
            inst.placement_transformation,
            federated_false_origin_meters_,
            m.model_transformation_meters,
            m.coordinate_operation_meters,
            mi.local_aabb_min, mi.local_aabb_max,
            inst.transform,
            inst.world_aabb_min, inst.world_aabb_max);
    } else {
        // Unknown mesh id: still compose the transform (downstream may
        // use it for picking / readback even without geometry), but
        // emit a degenerate world AABB so cull doesn't pick this up.
        const float zero[3] = {0.0f, 0.0f, 0.0f};
        InstanceCompose::composeInstance(
            inst.placement_transformation,
            federated_false_origin_meters_,
            m.model_transformation_meters,
            m.coordinate_operation_meters,
            zero, zero,
            inst.transform,
            inst.world_aabb_min, inst.world_aabb_max);
        for (int a = 0; a < 3; ++a) {
            inst.world_aabb_min[a] = 0.0f;
            inst.world_aabb_max[a] = 0.0f;
        }
    }
}
