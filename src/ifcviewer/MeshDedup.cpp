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

#include "MeshDedup.h"

#include <cmath>
#include <cstring>

namespace {

// FNV-1a over raw bytes.  Indices and packed colours are integers, so an
// exact byte hash is the right equality test for them.
uint64_t hashBytes(const void* data, std::size_t byte_count) {
    const auto* p = static_cast<const unsigned char*>(data);
    uint64_t h = 0xcbf29ce484222325ull;
    for (std::size_t i = 0; i < byte_count; ++i) {
        h ^= p[i];
        h *= 0x100000001b3ull;
    }
    return h;
}

// Relative float precision: positions arrive as float32, so two copies of
// one shape can differ by this fraction of their coordinate magnitude.
constexpr double kFloatRelativeError = 2.0e-7;

}  // namespace

MeshDedup::MeshDedup(double tolerance_meters)
    : tolerance_meters_(tolerance_meters)
{
}

MeshDedup::Key MeshDedup::getMeshKey(const StreamedMesh& mesh) {
    Key key;

    const std::size_t vertex_count = mesh.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS;

    key.vertex_count = static_cast<uint32_t>(vertex_count);
    key.index_count = static_cast<uint32_t>(mesh.indices.size());

    std::vector<uint32_t> colors(vertex_count);
    for (std::size_t i = 0; i < vertex_count; ++i) {
        std::memcpy(&colors[i],
                    mesh.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS + 6,
                    sizeof(uint32_t));
    }
    key.color_hash = hashBytes(colors.data(), colors.size() * sizeof(uint32_t));
    return key;
}

MeshDedup::CanonicalMesh MeshDedup::canonicaliseMesh(const StreamedMesh& mesh) {
    const std::size_t vertex_count = mesh.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS;

    CanonicalMesh canonical_mesh;
    Eigen::Vector3d sum = Eigen::Vector3d::Zero();
    for (std::size_t i = 0; i < vertex_count; ++i) {
        const float* v = mesh.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS;
        sum += Eigen::Vector3d(v[0], v[1], v[2]);
        canonical_mesh.max_abs_coordinate = std::max({canonical_mesh.max_abs_coordinate,
                                         double(std::fabs(v[0])),
                                         double(std::fabs(v[1])),
                                         double(std::fabs(v[2]))});
    }
    if (vertex_count > 0) canonical_mesh.centroid = sum / double(vertex_count);

    canonical_mesh.centered_positions.resize(vertex_count * 3);
    canonical_mesh.centroid_distances.resize(vertex_count);
    double sq = 0.0;
    for (std::size_t i = 0; i < vertex_count; ++i) {
        const float* v = mesh.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS;
        const Eigen::Vector3d c = Eigen::Vector3d(v[0], v[1], v[2]) - canonical_mesh.centroid;
        canonical_mesh.centered_positions[i * 3 + 0] = static_cast<float>(c.x());
        canonical_mesh.centered_positions[i * 3 + 1] = static_cast<float>(c.y());
        canonical_mesh.centered_positions[i * 3 + 2] = static_cast<float>(c.z());
        canonical_mesh.centroid_distances[i] = static_cast<float>(c.norm());
        sq += c.squaredNorm();
    }
    if (vertex_count > 0) canonical_mesh.radius_of_gyration = std::sqrt(sq / double(vertex_count));
    return canonical_mesh;
}

bool MeshDedup::rigidFit(const CanonicalMesh& registered, const CanonicalMesh& candidate,
                         Eigen::Matrix4d& canonical_to_instance_matrix) const {
    const double tol = tolerance_meters_
        + kFloatRelativeError * std::max(registered.max_abs_coordinate,
                                         candidate.max_abs_coordinate);
    if (std::fabs(registered.radius_of_gyration - candidate.radius_of_gyration) > tol) {
        return false;
    }
    // Rotation-invariant and order-dependent: a necessary condition for the
    // fit below, at a fraction of its cost.
    for (std::size_t i = 0; i < registered.centroid_distances.size(); ++i) {
        if (std::fabs(registered.centroid_distances[i] - candidate.centroid_distances[i]) > tol) {
            return false;
        }
    }

    const Eigen::Index n = static_cast<Eigen::Index>(registered.centered_positions.size() / 3);
    const Eigen::Matrix3Xd a =
        Eigen::Map<const Eigen::Matrix3Xf>(registered.centered_positions.data(), 3, n).cast<double>();
    const Eigen::Matrix3Xd b =
        Eigen::Map<const Eigen::Matrix3Xf>(candidate.centered_positions.data(), 3, n).cast<double>();

    // Umeyama without scaling is the Kabsch fit: the proper rotation R
    // minimising sum |R a_i - b_i|^2.  Both clouds are already centred, so
    // only the rotation block is used; the translation is rebuilt from the
    // centroids below.
    const Eigen::Matrix3d r =
        Eigen::umeyama(a, b, /*with_scaling=*/false).topLeftCorner<3, 3>();

    if ((r * a - b).cwiseAbs().maxCoeff() > tol) return false;

    // x_candidate = R (x_registered - c_registered) + c_candidate
    canonical_to_instance_matrix = Eigen::Matrix4d::Identity();
    canonical_to_instance_matrix.block<3, 3>(0, 0) = r;
    canonical_to_instance_matrix.block<3, 1>(0, 3) = candidate.centroid - r * registered.centroid;
    return true;
}

std::optional<CongruentMatch> MeshDedup::findCongruentMesh(const StreamedMesh& mesh) const {
    if (mesh.vertices.empty() || mesh.indices.empty()) return std::nullopt;
    auto it = registered_meshes_.find(getMeshKey(mesh));
    if (it == registered_meshes_.end()) return std::nullopt;
    const CanonicalMesh canonical_mesh = canonicaliseMesh(mesh);
    for (const CanonicalMesh& registered_mesh : it->second) {
        CongruentMatch match;
        if (rigidFit(registered_mesh, canonical_mesh, match.canonical_to_instance_matrix)) {
            match.mesh_id = registered_mesh.mesh_id;
            return match;
        }
    }
    return std::nullopt;
}

void MeshDedup::registerMesh(uint32_t mesh_id, const StreamedMesh& mesh) {
    if (mesh.vertices.empty() || mesh.indices.empty()) return;
    CanonicalMesh canonical_mesh = canonicaliseMesh(mesh);
    canonical_mesh.mesh_id = mesh_id;
    registered_meshes_[getMeshKey(mesh)].push_back(std::move(canonical_mesh));
}
