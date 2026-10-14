// This file was generated with the assistance of an AI coding tool.
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

#ifndef STREAMEDRECORDS_H
#define STREAMEDRECORDS_H

#include "InstancedGeometry.h"
#include "MeshDedup.h"

#include <Eigen/Dense>

#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace ifcopenshell::geom { class triangulation_element; }

// Per-unique-mesh local box, for the instance world box.
struct MeshAabb {
    float lmin[3];
    float lmax[3];
};

// How a geometry is placed onto the mesh it is drawn with.
// `canonical_to_instance_matrix` is non-identity when MeshDedup folded the
// geometry onto an earlier, congruent mesh.
struct UniqueMesh {
    uint32_t        mesh_id = 0;
    Eigen::Matrix4d canonical_to_instance_matrix = Eigen::Matrix4d::Identity();
};

// Record builders shared by the live streamer (GeometryStreamer::run) and the
// ifcconvert bake (src/serializers/ifcview_serializer), so both produce the same vertex and
// placement encoding.  Pure conversions: no Qt, no I/O.

// One interleaved transfer mesh (7 floats/vertex) from a triangulation
// element, in mesh-local coords.  Far-from-origin vertices are expected to
// have been rebased by the iterator (vertex-rebase-distance), which keeps the
// float32 positions precise and folds the shift into the placement itself.
StreamedMesh buildStreamedMesh(uint32_t session_model_id,
                               uint32_t mesh_id,
                               const ifcopenshell::geom::triangulation_element* elem);

// One instance record for a triangulation element.  The placement is kept in
// double, post-multiplied by the dedup transform so world position is
// preserved.
StreamedInstance makeStreamedInstance(uint32_t session_model_id,
                                      uint32_t object_id,
                                      const ifcopenshell::geom::triangulation_element& elem,
                                      const UniqueMesh& unique_mesh,
                                      const MeshAabb& mesh_aabb);

// Resolves every geometry to the mesh it is drawn with.  Geometries with the
// same id (mapped items) share a mesh, and MeshDedup folds a mesh that is a
// rigid-motion copy of an earlier one onto it.
class MeshRegistry {
public:
    // The placement of `elem`'s geometry.  When the geometry needs a mesh of
    // its own it is returned in `new_mesh` for the caller to emit.
    UniqueMesh resolve(uint32_t session_model_id,
                       const ifcopenshell::geom::triangulation_element& elem,
                       std::optional<StreamedMesh>& new_mesh);

    const MeshAabb& aabb(uint32_t mesh_id) const { return mesh_aabbs_[mesh_id]; }
    uint32_t meshCount() const { return static_cast<uint32_t>(mesh_aabbs_.size()); }
    uint32_t congruentMeshCount() const { return congruent_mesh_count_; }

private:
    std::unordered_map<std::string, UniqueMesh> geom_id_to_unique_mesh_;
    MeshDedup mesh_dedup_;
    std::vector<MeshAabb> mesh_aabbs_;
    uint32_t congruent_mesh_count_ = 0;
};

#endif // STREAMEDRECORDS_H
