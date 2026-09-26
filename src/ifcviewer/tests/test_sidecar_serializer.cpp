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

#include "SidecarSerializer.h"
#include "SidecarCache.h"

#include <catch2/catch_test_macros.hpp>

#include <atomic>
#include <cstring>
#include <filesystem>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {

// Unit quad at z, in the streamer's 7-floats/vertex transfer layout.
StreamedMesh makeQuadMesh(uint32_t local_mesh_id, float z) {
    StreamedMesh mesh;
    mesh.session_model_id = 1;
    mesh.local_mesh_id = local_mesh_id;

    const float corner_x[4] = {0.0f, 1.0f, 1.0f, 0.0f};
    const float corner_y[4] = {0.0f, 0.0f, 1.0f, 1.0f};
    uint32_t packed_color = 0xFFFFFFFFu;  // opaque white
    float color_as_float;
    std::memcpy(&color_as_float, &packed_color, sizeof(float));

    for (int i = 0; i < 4; ++i) {
        mesh.vertices.push_back(corner_x[i]);
        mesh.vertices.push_back(corner_y[i]);
        mesh.vertices.push_back(z);
        mesh.vertices.push_back(0.0f);
        mesh.vertices.push_back(0.0f);
        mesh.vertices.push_back(1.0f);
        mesh.vertices.push_back(color_as_float);
    }
    mesh.indices = {0, 1, 2, 0, 2, 3};

    mesh.local_aabb_min[0] = 0.0f; mesh.local_aabb_min[1] = 0.0f; mesh.local_aabb_min[2] = z;
    mesh.local_aabb_max[0] = 1.0f; mesh.local_aabb_max[1] = 1.0f; mesh.local_aabb_max[2] = z;
    return mesh;
}

StreamedInstance makeInstance(uint32_t local_mesh_id, uint32_t object_id, float x) {
    StreamedInstance inst;
    inst.session_model_id = 1;
    inst.local_mesh_id = local_mesh_id;
    inst.object_id = object_id;
    for (int i = 0; i < 16; ++i) inst.transform[i] = (i % 5 == 0) ? 1.0 : 0.0;
    inst.transform[12] = x;  // column-major translation x
    inst.world_aabb_min[0] = x;     inst.world_aabb_min[1] = 0.0f; inst.world_aabb_min[2] = 0.0f;
    inst.world_aabb_max[0] = x + 1; inst.world_aabb_max[1] = 1.0f; inst.world_aabb_max[2] = 1.0f;
    return inst;
}

ElementInfo makeElement(uint32_t object_id, std::string guid, std::string name, std::string type) {
    ElementInfo info;
    info.object_id = object_id;
    info.session_model_id = 1;
    info.ifc_id = static_cast<int>(object_id);
    info.guid = std::move(guid);
    info.name = std::move(name);
    info.type = std::move(type);
    return info;
}

std::string stringSlice(const SidecarData& data, uint32_t offset, uint32_t length) {
    return data.string_table.substr(offset, length);
}

// Each test creates its own scratch directory under the OS tmp root so they
// can run in parallel without colliding on file paths.
fs::path makeScratchDir(const char* tag) {
    fs::path base = fs::temp_directory_path() / "ifcviewer_test_sidecar";
    fs::create_directories(base);
    static std::atomic<uint64_t> counter{0};
    auto unique = std::to_string(counter.fetch_add(1)) + "_" + tag;
    fs::path dir = base / unique;
    fs::create_directories(dir);
    return dir;
}

}  // namespace

TEST_CASE("SidecarSerializer accumulates meshes, instances and elements", "[sidecar]") {
    SidecarSerializer serializer;
    serializer.onMeshReady(makeQuadMesh(0, 0.0f));
    serializer.onMeshReady(makeQuadMesh(1, 5.0f));
    serializer.onInstanceReady(makeInstance(0, 1, 0.0f));
    serializer.onInstanceReady(makeInstance(0, 2, 3.0f));
    serializer.onInstanceReady(makeInstance(1, 3, 9.0f));

    std::vector<ElementInfo> elements;
    elements.push_back(makeElement(1, "guid-1", "Wall A", "IfcWall"));
    elements.push_back(makeElement(2, "guid-2", "Slab B", "IfcSlab"));

    SidecarData data = serializer.finalize(ModelGeoref{}, elements);

    REQUIRE(data.meshes.size() == 2);
    REQUIRE(data.instances.size() == 3);
    REQUIRE(data.vertices.size() == 2 * 4 * INSTANCED_VERTEX_STRIDE_BYTES);
    REQUIRE(data.indices.size() >= 12);
    REQUIRE(!data.chunks.empty());  // finalize bakes the v14 chunk TOC

    // Instances stay grouped per mesh and instance_count follows; meshes are
    // distinguished by the z of their local AABB after the Morton pass.
    uint32_t count_at_z0 = 0;
    uint32_t count_at_z5 = 0;
    for (const MeshInfo& mesh : data.meshes) {
        REQUIRE(mesh.vertex_count == 4);
        REQUIRE(mesh.first_instance + mesh.instance_count <= data.instances.size());
        if (mesh.local_aabb_min[2] == 0.0f) count_at_z0 = mesh.instance_count;
        if (mesh.local_aabb_min[2] == 5.0f) count_at_z5 = mesh.instance_count;
    }
    REQUIRE(count_at_z0 == 2);
    REQUIRE(count_at_z5 == 1);

    // Element table round-trips guid / name / type through the string table.
    REQUIRE(data.elements.size() == 2);
    REQUIRE(stringSlice(data, data.elements[0].guid_offset, data.elements[0].guid_length) == "guid-1");
    REQUIRE(stringSlice(data, data.elements[0].name_offset, data.elements[0].name_length) == "Wall A");
    REQUIRE(stringSlice(data, data.elements[0].type_offset, data.elements[0].type_length) == "IfcWall");
    REQUIRE(stringSlice(data, data.elements[1].guid_offset, data.elements[1].guid_length) == "guid-2");
    REQUIRE(stringSlice(data, data.elements[1].name_offset, data.elements[1].name_length) == "Slab B");
    REQUIRE(stringSlice(data, data.elements[1].type_offset, data.elements[1].type_length) == "IfcSlab");
}

TEST_CASE("SidecarSerializer output round-trips through the on-disk cache", "[sidecar]") {
    SidecarSerializer serializer;
    serializer.onMeshReady(makeQuadMesh(0, 0.0f));
    serializer.onMeshReady(makeQuadMesh(1, 5.0f));
    serializer.onInstanceReady(makeInstance(0, 1, 0.0f));
    serializer.onInstanceReady(makeInstance(1, 2, 9.0f));

    SidecarData data = serializer.finalize(ModelGeoref{}, {});

    const fs::path dir = makeScratchDir("roundtrip");
    const fs::path ifc_path = dir / "model.ifc";
    REQUIRE(writeSidecar(ifc_path.string(), data));

    auto loaded = readSidecar(ifc_path.string());
    REQUIRE(loaded.has_value());
    REQUIRE(loaded->meshes.size() == data.meshes.size());
    REQUIRE(loaded->instances.size() == data.instances.size());
    REQUIRE(loaded->vertices == data.vertices);
    REQUIRE(loaded->indices == data.indices);
    REQUIRE(loaded->chunks.size() == data.chunks.size());

    fs::remove_all(dir);
}

TEST_CASE("SidecarSerializer can be reused after finalize", "[sidecar]") {
    SidecarSerializer serializer;
    serializer.onMeshReady(makeQuadMesh(0, 0.0f));
    serializer.onInstanceReady(makeInstance(0, 1, 0.0f));
    (void)serializer.finalize(ModelGeoref{}, {});

    serializer.onMeshReady(makeQuadMesh(0, 1.0f));
    SidecarData data = serializer.finalize(ModelGeoref{}, {});

    REQUIRE(data.meshes.size() == 1);
    REQUIRE(data.instances.empty());
    REQUIRE(data.elements.empty());
    REQUIRE(data.vertices.size() == 4 * INSTANCED_VERTEX_STRIDE_BYTES);
}
