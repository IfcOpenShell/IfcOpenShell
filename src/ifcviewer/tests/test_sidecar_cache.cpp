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

#include "InstancedGeometry.h"
#include "SidecarCache.h"

#include <catch2/catch_test_macros.hpp>

#include <atomic>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <random>
#include <string>

namespace fs = std::filesystem;

namespace {

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

SidecarData buildFixture() {
    SidecarData sd;

    // 4 vertices worth of arbitrary bytes (12 B/vertex).
    sd.vertices.resize(4 * INSTANCED_VERTEX_STRIDE_BYTES);
    for (size_t i = 0; i < sd.vertices.size(); ++i) sd.vertices[i] = uint8_t(i * 7);

    // Two meshes share the VBO — second mesh starts at vertex 2.
    sd.indices = {0, 1, 2, 1, 2, 3};

    MeshInfo m1{};
    m1.vbo_byte_offset = 0;
    m1.vertex_count = 2;
    m1.ebo_byte_offset = 0;
    m1.index_count = 3;
    m1.local_aabb_min[0] = -1; m1.local_aabb_min[1] = -2; m1.local_aabb_min[2] = -3;
    m1.local_aabb_max[0] =  4; m1.local_aabb_max[1] =  5; m1.local_aabb_max[2] =  6;
    m1.first_instance = 0;
    m1.instance_count = 3;
    m1.lod1_ebo_byte_offset = 0;
    m1.lod1_index_count = 0;

    MeshInfo m2{};
    m2.vbo_byte_offset = 2 * INSTANCED_VERTEX_STRIDE_BYTES;
    m2.vertex_count = 2;
    m2.ebo_byte_offset = 3 * sizeof(uint32_t);
    m2.index_count = 3;
    m2.local_aabb_min[0] = 10; m2.local_aabb_min[1] = 11; m2.local_aabb_min[2] = 12;
    m2.local_aabb_max[0] = 13; m2.local_aabb_max[1] = 14; m2.local_aabb_max[2] = 15;
    m2.first_instance = 3;
    m2.instance_count = 2;
    m2.lod1_ebo_byte_offset = 0;
    m2.lod1_index_count = 0;

    sd.meshes = {m1, m2};

    sd.instances.resize(5);
    for (size_t i = 0; i < sd.instances.size(); ++i) {
        InstanceCpu& inst = sd.instances[i];
        inst.mesh_id   = (i < 3) ? 0u : 1u;
        inst.object_id = uint32_t(100 + i);
        inst.color_override_rgba8 = uint32_t(0xAA000000u | (i * 0x010203u));
        inst.model_id  = 1;
        for (int k = 0; k < 16; ++k) {
            inst.placement_transformation[k] = double(i) * 0.25 + double(k);
            inst.transform[k]                = float(i) * 0.5f  + float(k);
        }
        inst.world_aabb_min[0] = float(i);
        inst.world_aabb_min[1] = float(i + 1);
        inst.world_aabb_min[2] = float(i + 2);
        inst.world_aabb_max[0] = float(i) + 10.0f;
        inst.world_aabb_max[1] = float(i + 1) + 10.0f;
        inst.world_aabb_max[2] = float(i + 2) + 10.0f;
    }

    // Non-default georef block.
    sd.has_coordinate_operation = 1;
    for (int k = 0; k < 16; ++k) sd.coordinate_operation_meters[k] = 0.5 + 0.1 * k;
    sd.project_length_to_meters = 0.001;  // mm project
    sd.map_unit_to_meters       = 1.0;    // metres map

    sd.string_table = std::string("\0Wall\0Slab\0", 11);  // includes embedded NULs
    sd.elements.resize(3);
    for (size_t i = 0; i < sd.elements.size(); ++i) {
        PackedElementInfo& e = sd.elements[i];
        e.object_id = uint32_t(100 + i);
        e.model_id  = 1;
        e.ifc_id    = int32_t(1000 + i);
        e.parent_id = (i == 0) ? -1 : int32_t(100);
        e.guid_offset = 0;  e.guid_length = 0;
        e.name_offset = 1;  e.name_length = 4;   // "Wall"
        e.type_offset = 6;  e.type_length = 4;   // "Slab"
    }
    return sd;
}

bool sidecarDataEqual(const SidecarData& a, const SidecarData& b) {
    if (a.vertices != b.vertices) return false;
    if (a.indices  != b.indices)  return false;
    if (a.meshes.size()    != b.meshes.size())    return false;
    if (a.instances.size() != b.instances.size()) return false;
    if (a.elements.size()  != b.elements.size())  return false;
    if (a.string_table     != b.string_table)     return false;

    for (size_t i = 0; i < a.meshes.size(); ++i) {
        if (std::memcmp(&a.meshes[i], &b.meshes[i], sizeof(MeshInfo)) != 0) return false;
    }
    for (size_t i = 0; i < a.instances.size(); ++i) {
        if (std::memcmp(&a.instances[i], &b.instances[i], sizeof(InstanceCpu)) != 0) return false;
    }
    for (size_t i = 0; i < a.elements.size(); ++i) {
        if (std::memcmp(&a.elements[i], &b.elements[i], sizeof(PackedElementInfo)) != 0) return false;
    }

    // v11 georef block.
    if (a.has_coordinate_operation != b.has_coordinate_operation) return false;
    if (a.project_length_to_meters != b.project_length_to_meters) return false;
    if (a.map_unit_to_meters       != b.map_unit_to_meters)       return false;
    for (int i = 0; i < 16; ++i) {
        if (a.coordinate_operation_meters[i] != b.coordinate_operation_meters[i])
            return false;
    }
    return true;
}

} // namespace

TEST_CASE("MeshInfo and InstanceCpu have stable layouts (sidecar wire format)", "[sidecar]") {
    REQUIRE(sizeof(MeshInfo) == 56);
    REQUIRE(sizeof(InstanceGpu) == 80);
    REQUIRE(SIDECAR_VERSION == 14);
    REQUIRE(sizeof(SidecarChunk) == 8);
    REQUIRE(SIDECAR_MAGIC == 0x49465657u);
}

TEST_CASE("writeSidecar/readSidecar round-trip the v14 chunk TOC", "[sidecar]") {
    fs::path dir = makeScratchDir("chunks");
    fs::path ifc = dir / "model.ifc";
    SidecarData sd = buildFixture();
    sd.chunks = { {0, 1}, {1, 1} };  // two chunks over the two meshes
    REQUIRE(writeSidecar(ifc.string(), sd));
    auto loaded = readSidecar(ifc.string());
    REQUIRE(loaded.has_value());
    REQUIRE(loaded->chunks.size() == 2);
    REQUIRE(loaded->chunks[0].first_mesh == 0);
    REQUIRE(loaded->chunks[0].mesh_count == 1);
    REQUIRE(loaded->chunks[1].first_mesh == 1);
    REQUIRE(loaded->chunks[1].mesh_count == 1);
}

TEST_CASE("writeSidecar then readSidecar round-trips the full fixture", "[sidecar]") {
    fs::path dir = makeScratchDir("roundtrip");
    fs::path ifc = dir / "model.ifc";
    fs::path expected = dir / "model.ifcview";

    SidecarData original = buildFixture();
    REQUIRE(writeSidecar(ifc.string(), original));
    REQUIRE(fs::exists(expected));

    auto loaded = readSidecar(ifc.string());
    REQUIRE(loaded.has_value());
    REQUIRE(sidecarDataEqual(original, *loaded));
}

TEST_CASE("readSidecar returns nullopt when the sidecar is missing", "[sidecar]") {
    fs::path dir = makeScratchDir("missing");
    fs::path ifc = dir / "absent.ifc";
    auto loaded = readSidecar(ifc.string());
    REQUIRE_FALSE(loaded.has_value());
}

TEST_CASE("readSidecar rejects a truncated header", "[sidecar]") {
    fs::path dir = makeScratchDir("truncated");
    fs::path ifc = dir / "bad.ifc";
    fs::path bad = dir / "bad.ifcview";
    {
        FILE* f = std::fopen(bad.string().c_str(), "wb");
        REQUIRE(f);
        const char junk[] = "X";
        std::fwrite(junk, 1, sizeof(junk), f);
        std::fclose(f);
    }
    auto loaded = readSidecar(ifc.string());
    REQUIRE_FALSE(loaded.has_value());
}

TEST_CASE("readSidecar rejects a wrong magic / version", "[sidecar]") {
    fs::path dir = makeScratchDir("wrongver");
    fs::path ifc = dir / "old.ifc";
    fs::path old = dir / "old.ifcview";
    struct Hdr { uint32_t magic, version, endian; } h{
        SIDECAR_MAGIC, SIDECAR_VERSION - 1, SIDECAR_ENDIAN
    };
    {
        FILE* f = std::fopen(old.string().c_str(), "wb");
        REQUIRE(f);
        std::fwrite(&h, sizeof(h), 1, f);
        // Write zeroed payload so the failure must come from the header check.
        uint32_t zero = 0;
        for (int i = 0; i < 6; ++i) std::fwrite(&zero, 4, 1, f);
        std::fclose(f);
    }
    auto loaded = readSidecar(ifc.string());
    REQUIRE_FALSE(loaded.has_value());
}

TEST_CASE("Empty SidecarData round-trips cleanly", "[sidecar]") {
    fs::path dir = makeScratchDir("empty");
    fs::path ifc = dir / "empty.ifc";
    SidecarData empty;
    REQUIRE(writeSidecar(ifc.string(), empty));
    auto loaded = readSidecar(ifc.string());
    REQUIRE(loaded.has_value());
    REQUIRE(loaded->vertices.empty());
    REQUIRE(loaded->indices.empty());
    REQUIRE(loaded->meshes.empty());
    REQUIRE(loaded->instances.empty());
    REQUIRE(loaded->elements.empty());
    REQUIRE(loaded->string_table.empty());
}

TEST_CASE("Sidecar path stem maps .ifc / .ifcdb / extensionless to .ifcview", "[sidecar]") {
    // The mapping is internal but observable: writing under one source name
    // must be readable under any other name that maps to the same stem.
    fs::path dir = makeScratchDir("stems");
    SidecarData sd = buildFixture();

    fs::path ifc_path    = dir / "shared.ifc";
    fs::path ifcdb_path  = dir / "shared.ifcdb";
    fs::path ifcdb_slash = dir / "shared.ifcdb/";
    fs::path noext_path  = dir / "shared";

    REQUIRE(writeSidecar(ifc_path.string(), sd));
    REQUIRE(fs::exists(dir / "shared.ifcview"));

    auto a = readSidecar(ifcdb_path.string());
    auto b = readSidecar(ifcdb_slash.string());
    auto c = readSidecar(noext_path.string());
    REQUIRE(a.has_value());
    REQUIRE(b.has_value());
    REQUIRE(c.has_value());
    REQUIRE(sidecarDataEqual(sd, *a));
    REQUIRE(sidecarDataEqual(sd, *b));
    REQUIRE(sidecarDataEqual(sd, *c));
}
