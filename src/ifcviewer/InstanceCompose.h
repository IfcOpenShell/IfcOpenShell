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

// Per-instance transform composition and world-AABB derivation: pure matrix
// maths on plain arrays, Eigen only, so the viewport, the .ifcview readers and
// the bake tool can share it.  Queries over loaded models live in ModelLookup.

#include <Eigen/Dense>

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

}  // namespace InstanceCompose

#endif  // INSTANCECOMPOSE_H
