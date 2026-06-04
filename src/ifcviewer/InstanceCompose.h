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

#ifndef INSTANCECOMPOSE_H
#define INSTANCECOMPOSE_H

// Instance-transform composition + per-instance world AABB derivation,
// plus the cross-model object-id → (model, mesh, placement) lookup.
// Pulled out of ViewportWindow as a free-function module so the matrix
// math + lookup logic can be unit-tested without spinning up a Qt window
// or a wgpu device.

#include <Eigen/Dense>

#include <cstdint>
#include <unordered_map>

#include "ModelGpuData.h"

namespace InstanceCompose {

// Transform the 8 corners of [local_min, local_max] through the
// column-major 4x4 matrix M (float[16]) and bound the result in
// world space. Called after every recompose so per-instance world
// AABBs (and the chunk AABBs derived from them) reflect the current
// federation matrices.
void worldAabbFromLocal(const float local_min[3], const float local_max[3],
                        const float M[16],
                        float world_min_out[3], float world_max_out[3]);

// composed = federated_false_origin
//          * model_transformation
//          * coordinate_operation
//          * placement
//
// Maths in double; narrow only at the end. Large IFC placements need
// to be cancelled by federated_false_origin before the float cast or
// precision is lost. The composed float matrix is written into
// transform_col_major_out (column-major, GPU-uploadable), then the
// local AABB is transformed by the same matrix to produce the
// world-space AABB.
void composeInstance(
    const double placement_col_major[16],
    const Eigen::Matrix4d& federated_false_origin,
    const Eigen::Matrix4d& model_transformation,
    const Eigen::Matrix4d& coordinate_operation,
    const float local_aabb_min[3], const float local_aabb_max[3],
    float transform_col_major_out[16],
    float world_aabb_min_out[3], float world_aabb_max_out[3]);

// Result of a successful findInstance lookup. The placement_transformation
// is double[16] column-major (pre-CoordinateOperation / FederatedFalseOrigin
// / ModelTransformation) — the same convention as InstanceCpu so the
// measurement / picking tools can re-compose at need.
struct InstanceLookup {
    uint32_t model_id = 0;
    uint32_t mesh_id  = 0;
    double   placement_transformation[16]{};
};

// Walk a map of models looking for the one that owns `object_id`,
// fill `out` with that instance's (model_id, mesh_id, placement) and
// return true. Returns false for object_id == 0 (the sentinel for
// "no object") or when no model owns the id. Defensive: skips
// instances whose stored index is out-of-range for the model's
// instance array.
bool findInstanceInModels(
    uint32_t object_id,
    const std::unordered_map<uint32_t, ModelGpuData>& models,
    InstanceLookup& out);

} // namespace InstanceCompose

#endif  // INSTANCECOMPOSE_H
