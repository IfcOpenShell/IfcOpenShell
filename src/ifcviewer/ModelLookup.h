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

#ifndef MODELLOOKUP_H
#define MODELLOOKUP_H

// Queries over the map of loaded models: the cross-model object-id ->
// (model, mesh, placement) lookup and the scene / per-model world AABBs.
// Pulled out of ViewportWindow as a free-function module so they can be
// unit-tested without spinning up a Qt window or a wgpu device.

#include <cstdint>
#include <unordered_map>
#include <vector>

#include "ModelGpuData.h"

namespace ModelLookup {

// Result of a successful findInstance lookup. The placement_transformation
// is double[16] column-major (pre-CoordinateOperation / FederatedFalseOrigin
// / ModelTransformation) — the same convention as InstanceInfo so the
// measurement / picking tools can re-compose at need.
struct InstanceLookup {
    uint32_t session_model_id = 0;
    uint32_t mesh_id  = 0;
    double   placement_transformation[16]{};
};

// Walk a map of models looking for the one that owns `object_id`,
// fill `out` with that instance's (session_model_id, mesh_id, placement) and
// return true. Returns false for object_id == 0 (the sentinel for
// "no object") or when no model owns the id. Defensive: skips
// instances whose stored index is out-of-range for the model's
// instance array.
bool findInstanceInModels(
    uint32_t object_id,
    const std::unordered_map<uint32_t, ModelGpuData>& models,
    InstanceLookup& out);

// Union of every instance's world AABB across every VISIBLE model — the box
// viewAll frames. Model-hidden models are excluded (framing them would fly the
// camera at geometry you cannot see).
//
// Returns false when nothing contributed, in which case [mn, mx] is left as the
// empty box (min = +inf, max = -inf) and the caller must not use it.
bool sceneWorldAabb(const std::unordered_map<uint32_t, ModelGpuData>& models,
                    float world_min_out[3], float world_max_out[3]);

// The same union restricted to the named models — the box "view selected model"
// frames. Ids naming a model that isn't loaded contribute nothing. Hidden
// models are NOT skipped here: the caller named these specifically, so honour
// the request rather than second-guessing it.
bool modelsWorldAabb(const std::unordered_map<uint32_t, ModelGpuData>& models,
                     const std::vector<uint32_t>& session_model_ids,
                     float world_min_out[3], float world_max_out[3]);

} // namespace ModelLookup

#endif  // MODELLOOKUP_H
