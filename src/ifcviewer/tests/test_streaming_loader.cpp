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

#include "SidecarCache.h"
#include "SidecarCompress.h"
#include "StreamingLoader.h"

#include <catch2/catch_test_macros.hpp>

#include <atomic>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {

fs::path makeScratchDir(const char* tag) {
    fs::path base = fs::temp_directory_path() / "ifcviewer_test_streaming";
    fs::create_directories(base);
    static std::atomic<uint64_t> counter{0};
    fs::path dir = base / (std::to_string(counter.fetch_add(1)) + "_" + tag);
    fs::create_directories(dir);
    return dir;
}

// Minimal but representative fixture: two meshes sharing one VBO, a non-default
// georef block, and a string table with embedded NULs (so the byte-exact tail
// parse is actually exercised).
SidecarData buildFixture() {
    SidecarData sd;

    sd.vertices.resize(4 * INSTANCED_VERTEX_STRIDE_BYTES);
    for (size_t i = 0; i < sd.vertices.size(); ++i) sd.vertices[i] = uint8_t(i * 7 + 1);

    sd.indices = {0, 1, 2, 1, 2, 3};

    MeshInfo m1{};
    m1.vbo_byte_offset = 0;
    m1.vertex_count = 2;
    m1.ebo_byte_offset = 0;
    m1.index_count = 3;
    MeshInfo m2{};
    m2.vbo_byte_offset = 2 * INSTANCED_VERTEX_STRIDE_BYTES;
    m2.vertex_count = 2;
    m2.ebo_byte_offset = 3 * sizeof(uint32_t);
    m2.index_count = 3;
    sd.meshes = {m1, m2};

    sd.instances.resize(3);
    for (size_t i = 0; i < sd.instances.size(); ++i) {
        sd.instances[i].mesh_id   = (i < 2) ? 0u : 1u;
        sd.instances[i].object_id = uint32_t(100 + i);
        sd.instances[i].model_id  = 1;
    }

    sd.has_coordinate_operation = 1;
    for (int k = 0; k < 16; ++k) sd.coordinate_operation_meters[k] = 0.5 + 0.1 * k;
    sd.project_length_to_meters = 0.001;
    sd.map_unit_to_meters       = 1.0;

    sd.string_table = std::string("\0Wall\0Slab\0", 11);
    sd.elements.resize(2);
    for (size_t i = 0; i < sd.elements.size(); ++i) {
        sd.elements[i].object_id = uint32_t(100 + i);
        sd.elements[i].model_id  = 1;
        sd.elements[i].ifc_id    = int32_t(1000 + i);
    }
    // v16 stores geometry per-chunk (compressed); a fixture with geometry needs
    // a chunk TOC covering its meshes (one chunk per mesh here).
    sd.chunks = { {0, 1}, {1, 1} };
    return sd;
}

}  // namespace

TEST_CASE("readSidecarMetadataOnly returns metadata, skips bulk geometry",
          "[streaming]") {
    fs::path dir = makeScratchDir("metaonly");
    fs::path ifc = dir / "model.ifc";
    SidecarData sd = buildFixture();
    REQUIRE(writeSidecar(ifc.string(), sd));

    auto meta = readSidecarMetadataOnly(ifc.string());
    REQUIRE(meta.has_value());

    // Bulk geometry is skipped, not loaded.
    REQUIRE(meta->meta.vertices.empty());
    REQUIRE(meta->meta.indices.empty());

    // v16: the compressed geometry section starts right after the 20-byte head.
    REQUIRE(meta->geometry_section_offset == SIDECAR_HEAD_BYTES);
    // Chunk TOC carries compressed blob locators for each chunk.
    REQUIRE(meta->meta.chunks.size() == sd.chunks.size());
    REQUIRE(meta->meta.chunks[0].v_comp_size > 0);
    // The element metadata block locator is recorded for on-demand fetch.
    REQUIRE(meta->element_metadata_comp_size > 0);

    // Metadata round-trips.
    REQUIRE(meta->meta.meshes.size() == sd.meshes.size());
    REQUIRE(meta->meta.instances.size() == sd.instances.size());
    REQUIRE(meta->meta.elements.size() == sd.elements.size());
    REQUIRE(meta->meta.string_table == sd.string_table);
    REQUIRE(meta->meta.has_coordinate_operation == 1);
    REQUIRE(meta->meta.project_length_to_meters == 0.001);
    for (int k = 0; k < 16; ++k)
        REQUIRE(meta->meta.coordinate_operation_meters[k] == 0.5 + 0.1 * k);
    REQUIRE(std::memcmp(&meta->meta.meshes[1], &sd.meshes[1], sizeof(MeshInfo)) == 0);
}

TEST_CASE("readSidecarMetadataOnly rejects missing / corrupt files", "[streaming]") {
    fs::path dir = makeScratchDir("reject");
    REQUIRE_FALSE(readSidecarMetadataOnly((dir / "absent.ifc").string()).has_value());

    // Truncated head (under 16 bytes).
    fs::path bad = dir / "bad.ifc";
    {
        FILE* f = std::fopen((dir / "bad.ifcview").string().c_str(), "wb");
        REQUIRE(f);
        const char junk[] = "XYZ";
        std::fwrite(junk, 1, sizeof(junk), f);
        std::fclose(f);
    }
    REQUIRE_FALSE(readSidecarMetadataOnly(bad.string()).has_value());
}

TEST_CASE("readChunkGeometryCompressed decompresses a chunk's blobs", "[streaming]") {
    fs::path dir = makeScratchDir("chunkgeom");
    fs::path ifc = dir / "model.ifc";
    SidecarData sd = buildFixture();
    REQUIRE(writeSidecar(ifc.string(), sd));
    auto meta = readSidecarMetadataOnly(ifc.string());
    REQUIRE(meta.has_value());
    REQUIRE(meta->meta.chunks.size() == 2);

    // Chunk 0 = mesh 0: vertices [0, 2*stride), indices {0,1,2}.
    const auto& c0 = meta->meta.chunks[0];
    const uint64_t stride = INSTANCED_VERTEX_STRIDE_BYTES;
    std::vector<uint8_t>  vbytes;
    std::vector<uint32_t> idx;
    REQUIRE(readChunkGeometryCompressed(
        ifc.string(), meta->geometry_section_offset,
        c0.v_comp_off, c0.v_comp_size, c0.v_raw_size,
        c0.i_comp_off, c0.i_comp_size, c0.i_raw_size, vbytes, idx));
    REQUIRE(vbytes.size() == 2 * stride);
    REQUIRE(std::memcmp(vbytes.data(), sd.vertices.data(), 2 * stride) == 0);
    REQUIRE(idx == std::vector<uint32_t>({0, 1, 2}));

    // Chunk 1 = mesh 1: indices {1,2,3}.
    const auto& c1 = meta->meta.chunks[1];
    REQUIRE(readChunkGeometryCompressed(
        ifc.string(), meta->geometry_section_offset,
        c1.v_comp_off, c1.v_comp_size, c1.v_raw_size,
        c1.i_comp_off, c1.i_comp_size, c1.i_raw_size, vbytes, idx));
    REQUIRE(idx == std::vector<uint32_t>({1, 2, 3}));
    REQUIRE(std::memcmp(vbytes.data(), sd.vertices.data() + 2 * stride, 2 * stride) == 0);
}

TEST_CASE("parseSidecarHead validates magic / version, reads geom length", "[streaming]") {
    uint8_t head[SIDECAR_HEAD_BYTES] = {};
    uint32_t magic = SIDECAR_MAGIC, version = SIDECAR_VERSION, endian = SIDECAR_ENDIAN;
    uint64_t geom = 123456;
    std::memcpy(head + 0, &magic, 4);
    std::memcpy(head + 4, &version, 4);
    std::memcpy(head + 8, &endian, 4);
    std::memcpy(head + 12, &geom, 8);

    uint64_t got = 0;
    REQUIRE(parseSidecarHead(head, sizeof(head), got));
    REQUIRE(got == 123456);

    REQUIRE_FALSE(parseSidecarHead(head, SIDECAR_HEAD_BYTES - 1, got));

    uint8_t bad[SIDECAR_HEAD_BYTES];
    std::memcpy(bad, head, sizeof(bad));
    bad[0] ^= 0xFF;
    REQUIRE_FALSE(parseSidecarHead(bad, sizeof(bad), got));
}

TEST_CASE("v16 element metadata block: fetch via locator, decompress, parse", "[streaming]") {
    fs::path dir = makeScratchDir("v16element");
    fs::path ifc = dir / "model.ifc";
    SidecarData sd = buildFixture();
    REQUIRE(writeSidecar(ifc.string(), sd));

    auto meta = readSidecarMetadataOnly(ifc.string());
    REQUIRE(meta.has_value());
    REQUIRE(meta->meta.meshes.size()   == sd.meshes.size());   // geometry metadata
    REQUIRE(meta->meta.chunks.size()   == sd.chunks.size());
    REQUIRE(meta->meta.elements.size() == sd.elements.size()); // desktop reads element metadata too
    REQUIRE(meta->element_metadata_comp_size > 0);

    // The on-demand path (web) fetches the compressed element metadata frame via the
    // recorded locator and decompresses it — verify that round-trips.
    FILE* f = std::fopen((dir / "model.ifcview").string().c_str(), "rb");
    REQUIRE(f);
    std::vector<uint8_t> cz(size_t(meta->element_metadata_comp_size));
    std::fseek(f, long(meta->element_metadata_comp_offset), SEEK_SET);
    REQUIRE(std::fread(cz.data(), 1, cz.size(), f) == cz.size());
    std::fclose(f);

    std::vector<uint8_t> raw(size_t(meta->element_metadata_raw_size));
    REQUIRE(SidecarCompress::decompress(cz.data(), cz.size(), raw.data(), raw.size()));
    SidecarData d;
    REQUIRE(parseSidecarElementMetadata(raw.data(), raw.size(), d));
    REQUIRE(d.elements.size()  == sd.elements.size());
    REQUIRE(d.string_table     == sd.string_table);

    SidecarData chopped;
    REQUIRE_FALSE(parseSidecarElementMetadata(raw.data(), raw.size() - 1, chopped));
}

TEST_CASE("planSidecarReadRanges coalesces adjacent ranges, keeps far ones split",
          "[streaming]") {
    const uint64_t base = 1000;

    SECTION("adjacent ranges merge into one read") {
        // Two ranges that touch (0..16, 16..48) plus a gap small enough to
        // bridge (gap of 8 within a 64-byte tolerance).
        std::vector<std::pair<uint64_t, uint64_t>> ranges = {{0, 16}, {24, 24}};
        auto plans = planSidecarReadRanges(base, ranges, 64);
        REQUIRE(plans.size() == 1);
        REQUIRE(plans[0].file_offset == base + 0);
        REQUIRE(plans[0].read_size == 48);  // 0 .. 24+24
        REQUIRE(plans[0].slices.size() == 2);
    }

    SECTION("far-apart ranges stay separate") {
        std::vector<std::pair<uint64_t, uint64_t>> ranges = {{0, 16}, {1024, 16}};
        auto plans = planSidecarReadRanges(base, ranges, 64);
        REQUIRE(plans.size() == 2);
    }

    SECTION("input order preserved in destination offsets") {
        // Ranges given high-offset-first; dst offsets must follow input order
        // (range 0 -> dst 0, range 1 -> dst 16) regardless of file order.
        std::vector<std::pair<uint64_t, uint64_t>> ranges = {{2048, 16}, {0, 16}};
        auto plans = planSidecarReadRanges(base, ranges, 64);
        REQUIRE(plans.size() == 2);
        uint64_t total_bytes = 0;
        for (const auto& p : plans)
            for (const auto& s : p.slices) total_bytes += s.bytes;
        REQUIRE(total_bytes == 32);
        // The range at file offset 0 (input index 1) lands at dst 16.
        bool found_dst16 = false;
        for (const auto& p : plans)
            for (const auto& s : p.slices)
                if (p.file_offset == base + 0 && s.dst_offset == 16) found_dst16 = true;
        REQUIRE(found_dst16);
    }
}
