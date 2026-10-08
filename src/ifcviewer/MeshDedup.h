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

#ifndef MESHDEDUP_H
#define MESHDEDUP_H

#include "InstancedGeometry.h"

#include <Eigen/Dense>

#include <cstddef>
#include <cstdint>
#include <optional>
#include <unordered_map>
#include <vector>

// Finds duplicate (congruent) meshes from a list of registered meshes.
//
// The iterator already identifies mapped representations via the geometry id.
// This handles identical meshes that have a different geometry id.
//
// Matching is order-dependent (Procrustes): vertex i of the candidate must
// correspond to vertex i of the registered mesh. A mesh matches a prior
// registered mesh when:
//   * cheap filter: vertex count, index list and vertex colours are identical;
//   * the radius of gyration agrees within the tolerance;
//   * the best-fit proper rotation + translation (Kabsch) carries every
//     registered vertex onto the candidate vertex within the tolerance.
// Mirror images will not match.
//
// The tolerance is absolute (metres) plus a float-precision allowance that
// grows with the coordinate magnitude, so meshes far from the origin still
// match while a genuinely different shape never does.
struct CongruentMatch {
    uint32_t mesh_id = 0;
    // Maps the registered (canonical) mesh's local coordinates onto the
    // candidate's: x_candidate = canonical_to_instance_matrix * x_canonical.
    Eigen::Matrix4d canonical_to_instance_matrix = Eigen::Matrix4d::Identity();
};

class MeshDedup {
public:
    explicit MeshDedup(double tolerance_meters = 1e-4);
    std::optional<CongruentMatch> findCongruentMesh(const StreamedMesh& mesh) const;
    void registerMesh(uint32_t mesh_id, const StreamedMesh& mesh);

private:
    struct Key {
        uint32_t vertex_count = 0;
        uint64_t index_hash = 0;
        uint64_t color_hash = 0;
        bool operator==(const Key& o) const {
            return vertex_count == o.vertex_count && index_hash == o.index_hash
                && color_hash == o.color_hash;
        }
    };
    struct KeyHash {
        std::size_t operator()(const Key& k) const {
            return std::size_t(k.index_hash ^ (k.color_hash * 0x9E3779B97F4A7C15ull)
                               ^ (uint64_t(k.vertex_count) << 32));
        }
    };
    struct CanonicalMesh {
        uint32_t mesh_id = 0;
        double radius_of_gyration = 0.0;
        double max_abs_coordinate = 0.0;
        Eigen::Vector3d centroid = Eigen::Vector3d::Zero();
        std::vector<float> centered_positions;  // xyz per vertex, relative to centroid
    };

    static Key getMeshKey(const StreamedMesh& mesh);
    static CanonicalMesh canonicaliseMesh(const StreamedMesh& mesh);
    bool rigidFit(const CanonicalMesh& registered, const CanonicalMesh& candidate,
                  Eigen::Matrix4d& canonical_to_instance_matrix) const;

    double tolerance_meters_;
    std::unordered_map<Key, std::vector<CanonicalMesh>, KeyHash> registered_meshes_;
};

#endif  // MESHDEDUP_H
