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

// Tier-1 coverage of InstanceCompose. Both helpers are pure CPU:
//   - composeInstance does the federation × placement matrix chain plus
//     a corner-AABB transform.
//   - findInstanceInModels walks a model map and resolves an object id.
// Tests stay in-memory: ModelGpuData carries WGPUBuffer pointers that
// default to nullptr and are never released by anything in this test
// (releaseWgpuModelGpuData is only called from ViewportWindow).

#include "InstanceCompose.h"
#include "ModelGpuData.h"

#include <catch2/catch_all.hpp>

#include <array>
#include <cmath>
#include <cstring>

namespace {

// Build a 4x4 identity in column-major double[16] order.
std::array<double, 16> identity_dcm() {
    std::array<double, 16> M{};
    M[0] = M[5] = M[10] = M[15] = 1.0;
    return M;
}

// Build a 4x4 column-major double[16] translation matrix.
std::array<double, 16> translation_dcm(double tx, double ty, double tz) {
    auto M = identity_dcm();
    M[12] = tx; M[13] = ty; M[14] = tz;
    return M;
}

// Build a 4x4 column-major double[16] scale matrix.
std::array<double, 16> scale_dcm(double s) {
    std::array<double, 16> M{};
    M[0] = M[5] = M[10] = s;
    M[15] = 1.0;
    return M;
}

bool nearly_equal(float a, float b, float eps = 1e-5f) {
    return std::fabs(a - b) <= eps;
}

} // namespace

// -----------------------------------------------------------------------------
// worldAabbFromLocal — corner walk
// -----------------------------------------------------------------------------

TEST_CASE("worldAabbFromLocal identity-matrix copies the local AABB", "[instance_compose][aabb]") {
    const float lmin[3] = {-1.0f, -2.0f, -3.0f};
    const float lmax[3] = { 4.0f,  5.0f,  6.0f};
    const float Mid[16] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    };
    float omin[3], omax[3];
    InstanceCompose::worldAabbFromLocal(lmin, lmax, Mid, omin, omax);

    REQUIRE(nearly_equal(omin[0], lmin[0]));
    REQUIRE(nearly_equal(omin[1], lmin[1]));
    REQUIRE(nearly_equal(omin[2], lmin[2]));
    REQUIRE(nearly_equal(omax[0], lmax[0]));
    REQUIRE(nearly_equal(omax[1], lmax[1]));
    REQUIRE(nearly_equal(omax[2], lmax[2]));
}

TEST_CASE("worldAabbFromLocal translation shifts every axis", "[instance_compose][aabb]") {
    const float lmin[3] = {0.0f, 0.0f, 0.0f};
    const float lmax[3] = {1.0f, 1.0f, 1.0f};
    // Column-major translation by (10, 20, 30).
    const float Mt[16] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        10, 20, 30, 1
    };
    float omin[3], omax[3];
    InstanceCompose::worldAabbFromLocal(lmin, lmax, Mt, omin, omax);

    REQUIRE(nearly_equal(omin[0], 10.0f));
    REQUIRE(nearly_equal(omin[1], 20.0f));
    REQUIRE(nearly_equal(omin[2], 30.0f));
    REQUIRE(nearly_equal(omax[0], 11.0f));
    REQUIRE(nearly_equal(omax[1], 21.0f));
    REQUIRE(nearly_equal(omax[2], 31.0f));
}

TEST_CASE("worldAabbFromLocal 90° z-rotation swaps x/y and keeps extent", "[instance_compose][aabb]") {
    // Column-major rotation by 90° around z. Pre-rotation AABB is
    // [(0..2) × (0..1) × (0..1)]; post-rotation the x-extent becomes
    // -1..0 and y becomes 0..2.
    const float lmin[3] = {0.0f, 0.0f, 0.0f};
    const float lmax[3] = {2.0f, 1.0f, 1.0f};
    const float Mr[16] = {
        0,  1, 0, 0,
       -1,  0, 0, 0,
        0,  0, 1, 0,
        0,  0, 0, 1
    };
    float omin[3], omax[3];
    InstanceCompose::worldAabbFromLocal(lmin, lmax, Mr, omin, omax);

    REQUIRE(nearly_equal(omin[0], -1.0f));
    REQUIRE(nearly_equal(omax[0],  0.0f));
    REQUIRE(nearly_equal(omin[1],  0.0f));
    REQUIRE(nearly_equal(omax[1],  2.0f));
    REQUIRE(nearly_equal(omin[2],  0.0f));
    REQUIRE(nearly_equal(omax[2],  1.0f));
}

// -----------------------------------------------------------------------------
// composeInstance — matrix product correctness
// -----------------------------------------------------------------------------

TEST_CASE("composeInstance with all-identity matrices returns placement", "[instance_compose][matrix]") {
    auto P = translation_dcm(7.0, 8.0, 9.0);

    const float lmin[3] = {-1, -1, -1};
    const float lmax[3] = { 1,  1,  1};
    float T[16];
    float omin[3], omax[3];
    InstanceCompose::composeInstance(
        P.data(),
        Eigen::Matrix4d::Identity(),
        Eigen::Matrix4d::Identity(),
        Eigen::Matrix4d::Identity(),
        lmin, lmax,
        T, omin, omax);

    REQUIRE(nearly_equal(T[12], 7.0f));
    REQUIRE(nearly_equal(T[13], 8.0f));
    REQUIRE(nearly_equal(T[14], 9.0f));

    // Local AABB shifted by P's translation.
    REQUIRE(nearly_equal(omin[0], 6.0f));
    REQUIRE(nearly_equal(omax[0], 8.0f));
    REQUIRE(nearly_equal(omin[1], 7.0f));
    REQUIRE(nearly_equal(omax[1], 9.0f));
}

TEST_CASE("composeInstance applies federation × model × coordop × placement in order", "[instance_compose][matrix]") {
    // Each matrix translates by a distinct vector along one axis so
    // their composition is unambiguous and the order is detectable.
    //
    //   placement       : t = (1, 0, 0)
    //   coordop         : t = (0, 2, 0)
    //   model_transform : t = (0, 0, 4)
    //   federation      : t = (8, 0, 0)
    //
    // composed = fed * model * coordop * placement
    // Translation composition for pure translations is just sum:
    // (8+0+0+1, 0+0+2+0, 0+4+0+0) = (9, 2, 4).
    auto P = translation_dcm(1.0, 0.0, 0.0);
    Eigen::Matrix4d coordop = Eigen::Matrix4d::Identity();
    coordop(1, 3) = 2.0;
    Eigen::Matrix4d mt = Eigen::Matrix4d::Identity();
    mt(2, 3) = 4.0;
    Eigen::Matrix4d fed = Eigen::Matrix4d::Identity();
    fed(0, 3) = 8.0;

    const float lmin[3] = {0, 0, 0};
    const float lmax[3] = {0, 0, 0};
    float T[16];
    float omin[3], omax[3];
    InstanceCompose::composeInstance(
        P.data(), fed, mt, coordop, lmin, lmax,
        T, omin, omax);

    REQUIRE(nearly_equal(T[12], 9.0f));
    REQUIRE(nearly_equal(T[13], 2.0f));
    REQUIRE(nearly_equal(T[14], 4.0f));
}

TEST_CASE("composeInstance cancels large placement against federation false origin", "[instance_compose][matrix]") {
    // Real-world federated case: IFC placement at 10 km off origin
    // gets cancelled by an opposite federation false origin. After
    // composition the rendered geometry should sit near the origin
    // with float32-clean precision.
    auto P = translation_dcm(1e7, 1e7, 1e7);
    Eigen::Matrix4d fed = Eigen::Matrix4d::Identity();
    fed(0, 3) = -1e7;
    fed(1, 3) = -1e7;
    fed(2, 3) = -1e7;

    const float lmin[3] = {0, 0, 0};
    const float lmax[3] = {0, 0, 0};
    float T[16];
    float omin[3], omax[3];
    InstanceCompose::composeInstance(
        P.data(), fed,
        Eigen::Matrix4d::Identity(),
        Eigen::Matrix4d::Identity(),
        lmin, lmax, T, omin, omax);

    // After the double-precision cancellation we get exact 0. A naive
    // float-precision implementation would lose meters of accuracy at
    // 10 km from origin (float32 ULP at 1e7 is ~1.0).
    REQUIRE(nearly_equal(T[12], 0.0f, 1e-2f));
    REQUIRE(nearly_equal(T[13], 0.0f, 1e-2f));
    REQUIRE(nearly_equal(T[14], 0.0f, 1e-2f));
}

TEST_CASE("composeInstance writes column-major float[16]", "[instance_compose][matrix]") {
    // Compose with an identity rotation/translation chain and check
    // that the matrix lands in column-major order (T[12,13,14] = tx,ty,tz
    // — not row-major T[3,7,11]).
    auto P = translation_dcm(5.0, 6.0, 7.0);

    const float lmin[3] = {0, 0, 0};
    const float lmax[3] = {0, 0, 0};
    float T[16];
    float omin[3], omax[3];
    InstanceCompose::composeInstance(
        P.data(),
        Eigen::Matrix4d::Identity(),
        Eigen::Matrix4d::Identity(),
        Eigen::Matrix4d::Identity(),
        lmin, lmax, T, omin, omax);

    REQUIRE(nearly_equal(T[12], 5.0f));
    REQUIRE(nearly_equal(T[13], 6.0f));
    REQUIRE(nearly_equal(T[14], 7.0f));
    REQUIRE(nearly_equal(T[15], 1.0f));
    // Row-major positions stay zero.
    REQUIRE(nearly_equal(T[3], 0.0f));
    REQUIRE(nearly_equal(T[7], 0.0f));
    REQUIRE(nearly_equal(T[11], 0.0f));
}

TEST_CASE("composeInstance scales the world AABB by the placement scale", "[instance_compose][aabb]") {
    auto P = scale_dcm(2.0);
    const float lmin[3] = {-1, -1, -1};
    const float lmax[3] = { 1,  1,  1};
    float T[16];
    float omin[3], omax[3];
    InstanceCompose::composeInstance(
        P.data(),
        Eigen::Matrix4d::Identity(),
        Eigen::Matrix4d::Identity(),
        Eigen::Matrix4d::Identity(),
        lmin, lmax, T, omin, omax);

    REQUIRE(nearly_equal(omin[0], -2.0f));
    REQUIRE(nearly_equal(omax[0],  2.0f));
    REQUIRE(nearly_equal(omin[1], -2.0f));
    REQUIRE(nearly_equal(omax[1],  2.0f));
    REQUIRE(nearly_equal(omin[2], -2.0f));
    REQUIRE(nearly_equal(omax[2],  2.0f));
}

// -----------------------------------------------------------------------------
// findInstanceInModels — lookup correctness
// -----------------------------------------------------------------------------

namespace {

// Build a ModelGpuData with one instance carrying object_id and mesh_id.
// All wgpu pointers stay nullptr; nothing in the test exercises them.
ModelGpuData make_model_with_one_instance(uint32_t object_id, uint32_t mesh_id,
                                          double placement_tx) {
    ModelGpuData m;
    InstanceCpu inst{};
    inst.mesh_id   = mesh_id;
    inst.object_id = object_id;
    // Column-major identity with a tx for verification.
    inst.placement_transformation[0]  = 1.0;
    inst.placement_transformation[5]  = 1.0;
    inst.placement_transformation[10] = 1.0;
    inst.placement_transformation[15] = 1.0;
    inst.placement_transformation[12] = placement_tx;
    m.instances.push_back(inst);
    m.object_id_to_instance[object_id] = 0;
    return m;
}

} // namespace

TEST_CASE("findInstanceInModels returns false for object_id == 0", "[instance_compose][lookup]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_with_one_instance(7u, 3u, 0.0));

    InstanceCompose::InstanceLookup out;
    REQUIRE_FALSE(InstanceCompose::findInstanceInModels(0, models, out));
}

TEST_CASE("findInstanceInModels returns false when no model owns the id", "[instance_compose][lookup]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_with_one_instance(7u, 3u, 0.0));
    models.emplace(2u, make_model_with_one_instance(8u, 4u, 0.0));

    InstanceCompose::InstanceLookup out;
    REQUIRE_FALSE(InstanceCompose::findInstanceInModels(999, models, out));
}

TEST_CASE("findInstanceInModels fills the correct lookup for an owned id", "[instance_compose][lookup]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_with_one_instance(7u, 3u, 11.0));
    models.emplace(2u, make_model_with_one_instance(8u, 4u, 22.0));

    InstanceCompose::InstanceLookup out;
    REQUIRE(InstanceCompose::findInstanceInModels(8u, models, out));
    REQUIRE(out.model_id == 2u);
    REQUIRE(out.mesh_id  == 4u);
    REQUIRE(out.placement_transformation[12] == 22.0);
    REQUIRE(out.placement_transformation[0]  == 1.0);
    REQUIRE(out.placement_transformation[15] == 1.0);
}

TEST_CASE("findInstanceInModels skips a corrupt instance-index entry", "[instance_compose][lookup]") {
    // Map points at an index that doesn't exist in the instances
    // vector — the lookup should treat that as "not found here"
    // rather than reading past the array.
    ModelGpuData m;
    m.object_id_to_instance[42u] = 99u;  // empty instances vector
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, std::move(m));

    InstanceCompose::InstanceLookup out;
    REQUIRE_FALSE(InstanceCompose::findInstanceInModels(42u, models, out));
}
