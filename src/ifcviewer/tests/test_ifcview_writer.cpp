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

#include "InstanceCompose.h"
#include "InstancedGeometry.h"
#include "IfcViewFormat.h"
#include "IfcViewReader.h"
#include "IfcViewWriter.h"

#include <catch2/catch_test_macros.hpp>

#include <algorithm>
#include <atomic>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <optional>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {

// Each test creates its own scratch directory under the OS tmp root so they
// can run in parallel without colliding on file paths.
fs::path makeScratchDir(const char* tag) {
    fs::path base = fs::temp_directory_path() / "ifcviewer_test_ifcview";
    fs::create_directories(base);
    static std::atomic<uint64_t> counter{0};
    auto unique = std::to_string(counter.fetch_add(1)) + "_" + tag;
    fs::path dir = base / unique;
    fs::create_directories(dir);
    return dir;
}

IfcViewData buildFixture() {
    IfcViewData sd;

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
        InstanceInfo& inst = sd.instances[i];
        inst.mesh_id   = (i < 3) ? 0u : 1u;
        inst.object_id = uint32_t(100 + i);
        // An affine placement (bottom row 0 0 0 1, as every IFC placement is)
        // whose entries are exact in float, so the v19 record round-trips it.
        for (int k = 0; k < 16; ++k) {
            inst.placement_transformation[k] = double(i) * 0.25 + double(k);
        }
        inst.placement_transformation[3] = inst.placement_transformation[7] =
            inst.placement_transformation[11] = 0.0;
        inst.placement_transformation[15] = 1.0;
        // Not stored: the session id is the loader's, and transform +
        // world AABB come back derived from the placement and the mesh AABB.
        inst.session_model_id = 0;
        const MeshInfo& mesh = sd.meshes[inst.mesh_id];
        const Eigen::Matrix4d identity = Eigen::Matrix4d::Identity();
        InstanceCompose::composeInstance(inst.placement_transformation, identity, identity, identity,
                                      mesh.local_aabb_min, mesh.local_aabb_max,
                                      inst.transform, inst.world_aabb_min, inst.world_aabb_max);
    }

    // Non-default georef block.
    sd.has_coordinate_operation = 1;
    for (int k = 0; k < 16; ++k) sd.coordinate_operation_meters[k] = 0.5 + 0.1 * k;
    sd.project_length_to_meters = 0.001;  // mm project
    sd.map_unit_to_meters       = 1.0;    // metres map

    sd.string_table = std::string("\0Wall\0Slab\0", 11);  // includes embedded NULs
    sd.elements.resize(3);
    for (size_t i = 0; i < sd.elements.size(); ++i) {
        ElementTableRecord& e = sd.elements[i];
        e.object_id = uint32_t(100 + i);
        e.session_model_id  = 1;
        e.ifc_id    = int32_t(1000 + i);
        e.guid_offset = 0;  e.guid_length = 0;
        e.name_offset = 1;  e.name_length = 4;   // "Wall"
        e.type_offset = 6;  e.type_length = 4;   // "Slab"
    }
    // v16 stores geometry per-chunk (compressed), so a fixture with geometry
    // needs a chunk TOC covering its meshes for write/read to round-trip.
    sd.chunks = { {0, 2} };
    return sd;
}

bool ifcViewDataEqual(const IfcViewData& a, const IfcViewData& b) {
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
        if (std::memcmp(&a.instances[i], &b.instances[i], sizeof(InstanceInfo)) != 0) return false;
    }
    for (size_t i = 0; i < a.elements.size(); ++i) {
        if (std::memcmp(&a.elements[i], &b.elements[i], sizeof(ElementTableRecord)) != 0) return false;
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

// The viewer never loads a .ifcview whole: it reads the metadata, then fetches
// and decompresses chunks on demand.  Do the same here and scatter each
// chunk's geometry back by the mesh offsets, so a round trip is checked
// through the production reader.
std::optional<IfcViewData> readWholeIfcView(const std::string& ifc_path) {
    auto meta = readIfcViewMetadata(ifc_path);
    if (!meta) return std::nullopt;
    IfcViewData data = meta->meta;

    size_t vertex_bytes = 0, index_count = 0;
    for (const MeshInfo& m : data.meshes) {
        vertex_bytes = std::max(vertex_bytes,
            size_t(m.vbo_byte_offset) + size_t(m.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES);
        index_count = std::max(index_count, size_t(m.ebo_byte_offset / 4) + m.index_count);
        index_count = std::max(index_count, size_t(m.lod1_ebo_byte_offset / 4) + m.lod1_index_count);
    }
    data.vertices.assign(vertex_bytes, 0);
    data.indices.assign(index_count, 0);

    std::vector<uint8_t>  vbytes;
    std::vector<uint32_t> idx;
    for (const IfcViewChunk& c : data.chunks) {
        if (!readChunkGeometryCompressed(ifc_path, meta->geometry_section_offset,
                                         c.v_comp_off, c.v_comp_size, c.v_raw_size,
                                         c.i_comp_off, c.i_comp_size, c.i_raw_size, vbytes, idx)) {
            return std::nullopt;
        }
        // Chunk-local layout: the vertices of its meshes in order, then LOD0
        // indices per mesh, then LOD1 indices per mesh.
        size_t vcur = 0, icur = 0;
        const uint32_t end = c.first_mesh + c.mesh_count;
        for (uint32_t m = c.first_mesh; m < end; ++m) {
            const MeshInfo& mi = data.meshes[m];
            const size_t n = size_t(mi.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            std::memcpy(data.vertices.data() + mi.vbo_byte_offset, vbytes.data() + vcur, n);
            vcur += n;
        }
        for (uint32_t m = c.first_mesh; m < end; ++m) {
            const MeshInfo& mi = data.meshes[m];
            std::copy_n(idx.data() + icur, mi.index_count, data.indices.data() + mi.ebo_byte_offset / 4);
            icur += mi.index_count;
        }
        for (uint32_t m = c.first_mesh; m < end; ++m) {
            const MeshInfo& mi = data.meshes[m];
            std::copy_n(idx.data() + icur, mi.lod1_index_count,
                        data.indices.data() + mi.lod1_ebo_byte_offset / 4);
            icur += mi.lod1_index_count;
        }
    }
    return data;
}

} // namespace

TEST_CASE("MeshInfo and the instance record have stable layouts (.ifcview wire format)", "[ifcview]") {
    REQUIRE(sizeof(MeshInfo) == 56);
    REQUIRE(IFCVIEW_INSTANCE_RECORD_BYTES == 68);
    REQUIRE(sizeof(InstanceGpu) == 80);
    REQUIRE(sizeof(ElementTableRecord) == 36);
    REQUIRE(IFCVIEW_VERSION == 19);
    REQUIRE(sizeof(IfcViewChunk) == 56);
    REQUIRE(IFCVIEW_MAGIC == 0x49465657u);
}

TEST_CASE("writeIfcView round-trips the v14 chunk TOC", "[ifcview]") {
    fs::path dir = makeScratchDir("chunks");
    fs::path ifc = dir / "model.ifc";
    IfcViewData sd = buildFixture();
    sd.chunks = { {0, 1}, {1, 1} };  // two chunks over the two meshes
    REQUIRE(writeIfcView(ifc.string(), sd));
    auto loaded = readWholeIfcView(ifc.string());
    REQUIRE(loaded.has_value());
    REQUIRE(loaded->chunks.size() == 2);
    REQUIRE(loaded->chunks[0].first_mesh == 0);
    REQUIRE(loaded->chunks[0].mesh_count == 1);
    REQUIRE(loaded->chunks[1].first_mesh == 1);
    REQUIRE(loaded->chunks[1].mesh_count == 1);
}

TEST_CASE("writeIfcView round-trips the full fixture through the reader", "[ifcview]") {
    fs::path dir = makeScratchDir("roundtrip");
    fs::path ifc = dir / "model.ifc";
    fs::path expected = dir / "model.ifcview";

    IfcViewData original = buildFixture();
    REQUIRE(writeIfcView(ifc.string(), original));
    REQUIRE(fs::exists(expected));

    auto loaded = readWholeIfcView(ifc.string());
    REQUIRE(loaded.has_value());
    REQUIRE(ifcViewDataEqual(original, *loaded));
}

TEST_CASE("Empty IfcViewData round-trips cleanly", "[ifcview]") {
    fs::path dir = makeScratchDir("empty");
    fs::path ifc = dir / "empty.ifc";
    IfcViewData empty;
    REQUIRE(writeIfcView(ifc.string(), empty));
    auto loaded = readWholeIfcView(ifc.string());
    REQUIRE(loaded.has_value());
    REQUIRE(loaded->vertices.empty());
    REQUIRE(loaded->indices.empty());
    REQUIRE(loaded->meshes.empty());
    REQUIRE(loaded->instances.empty());
    REQUIRE(loaded->elements.empty());
    REQUIRE(loaded->string_table.empty());
}

// ViewportCore::applyCachedModel seeds ModelGpuData::coordinate_operation_meters
// straight from these fields, which is what puts a georeferenced model into
// global coordinates without a host having to push the matrix. That only works
// if the matrix survives the write/read round-trip in the same storage order it
// went in — a silent transpose would misplace every georeferenced model rather
// than fail loudly.
TEST_CASE("CoordinateOperation + unit scales round-trip through the .ifcview", "[ifcview]") {
    fs::path dir = makeScratchDir("georef");
    fs::path ifc = dir / "georef.ifc";

    IfcViewData sd = buildFixture();
    sd.has_coordinate_operation = 1;
    sd.project_length_to_meters = 0.001;   // model authored in millimetres
    sd.map_unit_to_meters       = 1.0;
    // Asymmetric on purpose: a transpose would still pass a symmetric matrix.
    // Translation lives in the last column under column-major storage, i.e.
    // elements [12], [13], [14].
    for (int i = 0; i < 16; ++i) sd.coordinate_operation_meters[i] = 0.0;
    sd.coordinate_operation_meters[0]  =  0.5;   // (0,0)
    sd.coordinate_operation_meters[1]  =  0.25;  // (1,0)
    sd.coordinate_operation_meters[5]  =  2.0;   // (1,1)
    sd.coordinate_operation_meters[10] =  1.0;   // (2,2)
    sd.coordinate_operation_meters[12] = -2523.02945910871;  // eastings
    sd.coordinate_operation_meters[13] = -4962.73759029173;  // northings
    sd.coordinate_operation_meters[14] =  1580.0;            // orthogonal height
    sd.coordinate_operation_meters[15] =  1.0;

    REQUIRE(writeIfcView(ifc.string(), sd));
    auto loaded = readWholeIfcView(ifc.string());
    REQUIRE(loaded.has_value());

    REQUIRE(loaded->has_coordinate_operation == 1);
    REQUIRE(loaded->project_length_to_meters == 0.001);
    REQUIRE(loaded->map_unit_to_meters == 1.0);
    for (int i = 0; i < 16; ++i) {
        REQUIRE(loaded->coordinate_operation_meters[i] ==
                sd.coordinate_operation_meters[i]);
    }
}

// A model with no IfcMapConversion must come back with the flag clear, so the
// seeding leaves the identity placeholder alone rather than baking in a
// half-populated matrix.
TEST_CASE(".ifcview without a CoordinateOperation reports none", "[ifcview]") {
    fs::path dir = makeScratchDir("nogeoref");
    fs::path ifc = dir / "nogeoref.ifc";
    // buildFixture() populates the georef block, so clear it back to what a
    // model with no IfcMapConversion bakes: flag down, identity placeholder.
    IfcViewData sd = buildFixture();
    sd.has_coordinate_operation = 0;
    for (int i = 0; i < 16; ++i) sd.coordinate_operation_meters[i] = (i % 5 == 0) ? 1.0 : 0.0;

    REQUIRE(writeIfcView(ifc.string(), sd));
    auto loaded = readWholeIfcView(ifc.string());
    REQUIRE(loaded.has_value());
    REQUIRE(loaded->has_coordinate_operation == 0);
    for (int i = 0; i < 16; ++i) {
        REQUIRE(loaded->coordinate_operation_meters[i] == ((i % 5 == 0) ? 1.0 : 0.0));
    }
}

TEST_CASE(".ifcview path stem maps .ifc / .ifcdb / extensionless to .ifcview", "[ifcview]") {
    // The mapping is internal but observable: writing under one source name
    // must be readable under any other name that maps to the same stem.
    fs::path dir = makeScratchDir("stems");
    IfcViewData sd = buildFixture();

    fs::path ifc_path    = dir / "shared.ifc";
    fs::path ifcdb_path  = dir / "shared.ifcdb";
    fs::path ifcdb_slash = dir / "shared.ifcdb/";
    fs::path noext_path  = dir / "shared";

    REQUIRE(writeIfcView(ifc_path.string(), sd));
    REQUIRE(fs::exists(dir / "shared.ifcview"));

    auto a = readWholeIfcView(ifcdb_path.string());
    auto b = readWholeIfcView(ifcdb_slash.string());
    auto c = readWholeIfcView(noext_path.string());
    REQUIRE(a.has_value());
    REQUIRE(b.has_value());
    REQUIRE(c.has_value());
    REQUIRE(ifcViewDataEqual(sd, *a));
    REQUIRE(ifcViewDataEqual(sd, *b));
    REQUIRE(ifcViewDataEqual(sd, *c));
}

// --- zstd frames -------------------------------------------------------------

TEST_CASE("a zstd frame round-trips and shrinks structured bytes", "[ifcview]") {
    // Structured data like the .ifcview carries (repeated matrices, patterned
    // indices) — should both round-trip AND actually shrink.
    std::vector<uint8_t> raw;
    for (int i = 0; i < 20000; ++i) {
        raw.push_back(uint8_t(i & 0xFF));
        raw.push_back(uint8_t((i >> 8) & 0x07));  // low-entropy high byte
        raw.push_back(0);
        raw.push_back(0xAA);
    }

    auto packed = compressIfcViewFrame(raw.data(), raw.size(), 19);
    REQUIRE_FALSE(packed.empty());
    REQUIRE(packed.size() < raw.size());  // it compressed

    std::vector<uint8_t> out(raw.size());
    REQUIRE(decompressIfcViewFrame(packed.data(), packed.size(), out.data(), out.size()));
    REQUIRE(out == raw);
}

TEST_CASE("decompressIfcViewFrame rejects a wrong raw size and garbage", "[ifcview]") {
    std::vector<uint8_t> raw(1024, 0x42);
    auto packed = compressIfcViewFrame(raw.data(), raw.size(), 3);
    REQUIRE_FALSE(packed.empty());

    // Wrong declared raw size must fail, not silently truncate.
    std::vector<uint8_t> too_small(512);
    REQUIRE_FALSE(decompressIfcViewFrame(packed.data(), packed.size(),
                                         too_small.data(), too_small.size()));

    // Garbage input fails cleanly.
    std::vector<uint8_t> junk = { 1, 2, 3, 4, 5, 6, 7, 8 };
    std::vector<uint8_t> dst(1024);
    REQUIRE_FALSE(decompressIfcViewFrame(junk.data(), junk.size(), dst.data(), dst.size()));
}

TEST_CASE("an empty zstd frame round-trips to empty", "[ifcview]") {
    std::vector<uint8_t> dst;
    REQUIRE(decompressIfcViewFrame(nullptr, 0, dst.data(), 0));
}
