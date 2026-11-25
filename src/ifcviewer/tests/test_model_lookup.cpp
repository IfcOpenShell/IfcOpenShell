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

// Tier-1 coverage of ModelLookup: findInstanceInModels walks a model map and
// resolves an object id; sceneWorldAabb / modelsWorldAabb fold instance boxes.
// Tests stay in-memory: ModelGpuData carries WGPUBuffer pointers that
// default to nullptr and are never released by anything in this test
// (releaseWgpuModelGpuData is only called from ViewportWindow).

#include "ModelLookup.h"
#include "ModelGpuData.h"

#include <catch2/catch_all.hpp>

#include <cstdint>

// -----------------------------------------------------------------------------
// findInstanceInModels — lookup correctness
// -----------------------------------------------------------------------------

namespace {

// Build a ModelGpuData with one instance carrying object_id and mesh_id.
// All wgpu pointers stay nullptr; nothing in the test exercises them.
ModelGpuData make_model_with_one_instance(uint32_t object_id, uint32_t mesh_id,
                                          double placement_tx) {
    ModelGpuData m;
    InstanceInfo inst{};
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

TEST_CASE("findInstanceInModels returns false for object_id == 0", "[model_lookup][lookup]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_with_one_instance(7u, 3u, 0.0));

    ModelLookup::InstanceLookup out;
    REQUIRE_FALSE(ModelLookup::findInstanceInModels(0, models, out));
}

TEST_CASE("findInstanceInModels returns false when no model owns the id", "[model_lookup][lookup]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_with_one_instance(7u, 3u, 0.0));
    models.emplace(2u, make_model_with_one_instance(8u, 4u, 0.0));

    ModelLookup::InstanceLookup out;
    REQUIRE_FALSE(ModelLookup::findInstanceInModels(999, models, out));
}

TEST_CASE("findInstanceInModels fills the correct lookup for an owned id", "[model_lookup][lookup]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_with_one_instance(7u, 3u, 11.0));
    models.emplace(2u, make_model_with_one_instance(8u, 4u, 22.0));

    ModelLookup::InstanceLookup out;
    REQUIRE(ModelLookup::findInstanceInModels(8u, models, out));
    REQUIRE(out.session_model_id == 2u);
    REQUIRE(out.mesh_id  == 4u);
    REQUIRE(out.placement_transformation[12] == 22.0);
    REQUIRE(out.placement_transformation[0]  == 1.0);
    REQUIRE(out.placement_transformation[15] == 1.0);
}

TEST_CASE("findInstanceInModels skips a corrupt instance-index entry", "[model_lookup][lookup]") {
    // Map points at an index that doesn't exist in the instances
    // vector — the lookup should treat that as "not found here"
    // rather than reading past the array.
    ModelGpuData m;
    m.object_id_to_instance[42u] = 99u;  // empty instances vector
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, std::move(m));

    ModelLookup::InstanceLookup out;
    REQUIRE_FALSE(ModelLookup::findInstanceInModels(42u, models, out));
}

// ---------------------------------------------------------------------------
// sceneWorldAabb / modelsWorldAabb — the boxes viewAll and "View Selected
// Model" frame. Both fold per-instance world AABBs; the difference is which
// models they fold, and that difference is exactly what these pin down.
// ---------------------------------------------------------------------------

namespace {

// A model holding one instance whose world AABB is the unit box translated to
// (tx, 0, 0), so each model occupies a distinct, easily-checked slab of space.
ModelGpuData make_model_at(float tx, bool hidden = false) {
    ModelGpuData m;
    m.hidden = hidden;
    InstanceInfo inst;
    inst.world_aabb_min[0] = tx - 1.0f;
    inst.world_aabb_min[1] = -1.0f;
    inst.world_aabb_min[2] = -1.0f;
    inst.world_aabb_max[0] = tx + 1.0f;
    inst.world_aabb_max[1] = 1.0f;
    inst.world_aabb_max[2] = 1.0f;
    m.instances.push_back(inst);
    return m;
}

} // namespace

TEST_CASE("sceneWorldAabb unions every visible model", "[model_lookup][aabb]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_at(0.0f));
    models.emplace(2u, make_model_at(10.0f));

    float mn[3], mx[3];
    REQUIRE(ModelLookup::sceneWorldAabb(models, mn, mx));
    REQUIRE(mn[0] == -1.0f);   // model 1's left face
    REQUIRE(mx[0] == 11.0f);   // model 2's right face
}

TEST_CASE("sceneWorldAabb skips hidden models", "[model_lookup][aabb]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_at(0.0f));
    models.emplace(2u, make_model_at(10.0f, /*hidden*/true));

    float mn[3], mx[3];
    REQUIRE(ModelLookup::sceneWorldAabb(models, mn, mx));
    REQUIRE(mx[0] == 1.0f);    // the hidden model at x=10 contributed nothing
}

TEST_CASE("sceneWorldAabb reports empty for a scene with no geometry",
          "[model_lookup][aabb]") {
    const std::unordered_map<uint32_t, ModelGpuData> empty;
    float mn[3], mx[3];
    REQUIRE_FALSE(ModelLookup::sceneWorldAabb(empty, mn, mx));

    // A model whose metadata is up but whose instances haven't landed yet is
    // just as empty — the caller must not frame it.
    std::unordered_map<uint32_t, ModelGpuData> no_instances;
    no_instances.emplace(1u, ModelGpuData{});
    REQUIRE_FALSE(ModelLookup::sceneWorldAabb(no_instances, mn, mx));
}

TEST_CASE("modelsWorldAabb folds only the named models", "[model_lookup][aabb]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_at(0.0f));
    models.emplace(2u, make_model_at(10.0f));
    models.emplace(3u, make_model_at(20.0f));

    float mn[3], mx[3];
    REQUIRE(ModelLookup::modelsWorldAabb(models, {2u}, mn, mx));
    REQUIRE(mn[0] == 9.0f);
    REQUIRE(mx[0] == 11.0f);   // model 2 alone — not the whole scene

    // Several at once unions just those.
    REQUIRE(ModelLookup::modelsWorldAabb(models, {1u, 3u}, mn, mx));
    REQUIRE(mn[0] == -1.0f);
    REQUIRE(mx[0] == 21.0f);
}

TEST_CASE("modelsWorldAabb honours a hidden model the caller named",
          "[model_lookup][aabb]") {
    // Unlike sceneWorldAabb: "view this model" was asked for explicitly, so a
    // hidden model still frames rather than silently reporting nothing.
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_at(10.0f, /*hidden*/true));

    float mn[3], mx[3];
    REQUIRE(ModelLookup::modelsWorldAabb(models, {1u}, mn, mx));
    REQUIRE(mx[0] == 11.0f);
}

TEST_CASE("modelsWorldAabb reports empty for unloaded / unnamed models",
          "[model_lookup][aabb]") {
    std::unordered_map<uint32_t, ModelGpuData> models;
    models.emplace(1u, make_model_at(0.0f));

    float mn[3], mx[3];
    REQUIRE_FALSE(ModelLookup::modelsWorldAabb(models, {}, mn, mx));      // nothing named
    REQUIRE_FALSE(ModelLookup::modelsWorldAabb(models, {99u}, mn, mx));   // not loaded

    // A partially-resolvable list still frames what it can.
    REQUIRE(ModelLookup::modelsWorldAabb(models, {99u, 1u}, mn, mx));
    REQUIRE(mx[0] == 1.0f);
}
