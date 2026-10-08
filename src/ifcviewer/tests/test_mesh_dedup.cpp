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

// Tier-1 coverage of MeshDedup: rigid-motion copies of a registered mesh
// are recognised and the returned transform reproduces the copy; anything
// that is not a rigid copy (scaled, mirrored, re-indexed, recoloured) is not.

#include "MeshDedup.h"

#include <catch2/catch_all.hpp>

#include <Eigen/Dense>

#include <cmath>
#include <cstring>
#include <vector>

namespace {

// An irregular tetrahedron: no symmetry, so a mirror image is never a
// rotation of it and a wrong correspondence cannot fit by accident.
StreamedMesh tetrahedron(uint32_t color = 0xFF336699u) {
    const float pos[4][3] = {{0.0f, 0.0f, 0.0f},
                             {1.0f, 0.0f, 0.0f},
                             {0.3f, 0.8f, 0.0f},
                             {0.2f, 0.3f, 0.6f}};
    StreamedMesh m;
    float color_as_float;
    std::memcpy(&color_as_float, &color, sizeof(float));
    for (const auto& p : pos) {
        m.vertices.insert(m.vertices.end(), {p[0], p[1], p[2], 0.0f, 0.0f, 1.0f, color_as_float});
    }
    m.indices = {0, 1, 2, 0, 3, 1, 1, 3, 2, 2, 3, 0};
    return m;
}

StreamedMesh transformed(const StreamedMesh& src, const Eigen::Matrix4d& t) {
    StreamedMesh out = src;
    const std::size_t n = src.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS;
    for (std::size_t i = 0; i < n; ++i) {
        float* v = out.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS;
        const Eigen::Vector4d p = t * Eigen::Vector4d(v[0], v[1], v[2], 1.0);
        v[0] = static_cast<float>(p.x());
        v[1] = static_cast<float>(p.y());
        v[2] = static_cast<float>(p.z());
    }
    return out;
}

Eigen::Matrix4d rigid(double angle_z, const Eigen::Vector3d& translation) {
    Eigen::Matrix4d t = Eigen::Matrix4d::Identity();
    t.block<3, 3>(0, 0) = Eigen::AngleAxisd(angle_z, Eigen::Vector3d::UnitZ()).toRotationMatrix();
    t.block<3, 1>(0, 3) = translation;
    return t;
}

// Largest distance between the match transform applied to the registered
// mesh and the candidate's actual vertices.
double reproductionError(const StreamedMesh& registered, const StreamedMesh& candidate,
                         const Eigen::Matrix4d& canonical_to_instance_matrix) {
    const StreamedMesh rebuilt = transformed(registered, canonical_to_instance_matrix);
    double worst = 0.0;
    for (std::size_t i = 0; i < candidate.vertices.size(); i += INSTANCED_VERTEX_STRIDE_FLOATS) {
        for (int a = 0; a < 3; ++a) {
            worst = std::max(worst, double(std::fabs(rebuilt.vertices[i + a] - candidate.vertices[i + a])));
        }
    }
    return worst;
}

}  // namespace

TEST_CASE("a translated copy matches and the transform reproduces it", "[mesh_dedup]") {
    MeshDedup dedup;
    const StreamedMesh base = tetrahedron();
    dedup.registerMesh(7, base);

    const StreamedMesh copy = transformed(base, rigid(0.0, {12.5, -3.0, 40.0}));
    const auto match = dedup.findCongruentMesh(copy);
    REQUIRE(match.has_value());
    CHECK(match->mesh_id == 7);
    CHECK(reproductionError(base, copy, match->canonical_to_instance_matrix) < 1e-5);
}

TEST_CASE("a rotated and translated copy matches with a proper rotation", "[mesh_dedup]") {
    MeshDedup dedup;
    const StreamedMesh base = tetrahedron();
    dedup.registerMesh(3, base);

    const StreamedMesh copy = transformed(base, rigid(1.1, {-2.0, 5.0, 0.25}));
    const auto match = dedup.findCongruentMesh(copy);
    REQUIRE(match.has_value());
    CHECK(match->mesh_id == 3);
    CHECK(reproductionError(base, copy, match->canonical_to_instance_matrix) < 1e-5);
    CHECK(match->canonical_to_instance_matrix.block<3, 3>(0, 0).determinant() == Catch::Approx(1.0));
}

TEST_CASE("the first registered copy wins when several are registered", "[mesh_dedup]") {
    MeshDedup dedup;
    const StreamedMesh base = tetrahedron();
    dedup.registerMesh(1, base);
    dedup.registerMesh(2, transformed(base, rigid(0.0, {1.0, 0.0, 0.0})));

    const auto match = dedup.findCongruentMesh(transformed(base, rigid(0.3, {9.0, 9.0, 9.0})));
    REQUIRE(match.has_value());
    CHECK(match->mesh_id == 1);
}

TEST_CASE("a copy beyond the tolerance does not match", "[mesh_dedup]") {
    MeshDedup dedup(1e-4);
    const StreamedMesh base = tetrahedron();
    dedup.registerMesh(0, base);

    StreamedMesh nudged = base;
    nudged.vertices[2 * INSTANCED_VERTEX_STRIDE_FLOATS + 1] += 0.01f;  // move one vertex 1 cm
    CHECK_FALSE(dedup.findCongruentMesh(nudged).has_value());

    StreamedMesh scaled = base;
    for (std::size_t i = 0; i < scaled.vertices.size(); i += INSTANCED_VERTEX_STRIDE_FLOATS) {
        for (int a = 0; a < 3; ++a) scaled.vertices[i + a] *= 1.01f;
    }
    CHECK_FALSE(dedup.findCongruentMesh(scaled).has_value());
}

TEST_CASE("a mirror image does not match", "[mesh_dedup]") {
    MeshDedup dedup;
    const StreamedMesh base = tetrahedron();
    dedup.registerMesh(0, base);

    Eigen::Matrix4d mirror = Eigen::Matrix4d::Identity();
    mirror(0, 0) = -1.0;
    CHECK_FALSE(dedup.findCongruentMesh(transformed(base, mirror)).has_value());
}

TEST_CASE("different triangles or colours over the same points do not match", "[mesh_dedup]") {
    MeshDedup dedup;
    const StreamedMesh base = tetrahedron();
    dedup.registerMesh(0, base);

    StreamedMesh reindexed = base;
    std::swap(reindexed.indices[0], reindexed.indices[1]);
    CHECK_FALSE(dedup.findCongruentMesh(reindexed).has_value());

    CHECK_FALSE(dedup.findCongruentMesh(tetrahedron(0xFF112233u)).has_value());
}

TEST_CASE("an empty mesh never matches, even after one was registered", "[mesh_dedup]") {
    MeshDedup dedup;
    dedup.registerMesh(0, StreamedMesh{});
    CHECK_FALSE(dedup.findCongruentMesh(StreamedMesh{}).has_value());
}
