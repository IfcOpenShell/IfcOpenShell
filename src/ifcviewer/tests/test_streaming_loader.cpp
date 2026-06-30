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
        sd.elements[i].parent_id = (i == 0) ? -1 : int32_t(100);
    }
    return sd;
}

}  // namespace

TEST_CASE("readSidecarMetadataOnly returns metadata + section offsets, skips bulk",
          "[streaming]") {
    fs::path dir = makeScratchDir("metaonly");
    fs::path ifc = dir / "model.ifc";
    SidecarData sd = buildFixture();
    REQUIRE(writeSidecar(ifc.string(), sd));

    auto meta = readSidecarMetadataOnly(ifc.string());
    REQUIRE(meta.has_value());

    // Bulk sections are skipped, not loaded.
    REQUIRE(meta->meta.vertices.empty());
    REQUIRE(meta->meta.indices.empty());

    // Offsets locate the two skipped sections. The vertex section starts
    // right after the 16-byte head.
    REQUIRE(meta->vertex_section_offset == SIDECAR_HEAD_BYTES);
    REQUIRE(meta->vertex_total_bytes == sd.vertices.size());
    REQUIRE(meta->index_total_count == sd.indices.size());
    REQUIRE(meta->index_section_offset ==
            SIDECAR_HEAD_BYTES + sd.vertices.size() + 4);

    // Tail metadata round-trips.
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

TEST_CASE("readSidecarVertexRanges scatters byte ranges in input order", "[streaming]") {
    fs::path dir = makeScratchDir("vranges");
    fs::path ifc = dir / "model.ifc";
    SidecarData sd = buildFixture();
    REQUIRE(writeSidecar(ifc.string(), sd));
    auto meta = readSidecarMetadataOnly(ifc.string());
    REQUIRE(meta.has_value());

    // Two section-relative ranges given out of file order; the destination
    // must preserve input order (second mesh's bytes first, then first).
    const uint64_t stride = INSTANCED_VERTEX_STRIDE_BYTES;
    std::vector<std::pair<uint64_t, uint64_t>> ranges = {
        {2 * stride, 2 * stride},  // last 2 vertices
        {0, 2 * stride},           // first 2 vertices
    };
    std::vector<uint8_t> out;
    REQUIRE(readSidecarVertexRanges(ifc.string(), meta->vertex_section_offset,
                                    ranges, out));
    REQUIRE(out.size() == 4 * stride);
    REQUIRE(std::memcmp(out.data(), sd.vertices.data() + 2 * stride, 2 * stride) == 0);
    REQUIRE(std::memcmp(out.data() + 2 * stride, sd.vertices.data(), 2 * stride) == 0);
}

TEST_CASE("readSidecarIndexRanges reads u32 index ranges", "[streaming]") {
    fs::path dir = makeScratchDir("iranges");
    fs::path ifc = dir / "model.ifc";
    SidecarData sd = buildFixture();
    REQUIRE(writeSidecar(ifc.string(), sd));
    auto meta = readSidecarMetadataOnly(ifc.string());
    REQUIRE(meta.has_value());

    std::vector<std::pair<uint64_t, uint64_t>> ranges = {{3, 3}};  // indices[3..6)
    std::vector<uint32_t> out;
    REQUIRE(readSidecarIndexRanges(ifc.string(), meta->index_section_offset,
                                   ranges, out));
    REQUIRE(out == std::vector<uint32_t>({1, 2, 3}));
}

TEST_CASE("parseSidecarHead validates magic / version / length", "[streaming]") {
    uint8_t head[SIDECAR_HEAD_BYTES] = {};
    uint32_t magic = SIDECAR_MAGIC, version = SIDECAR_VERSION, endian = SIDECAR_ENDIAN;
    uint32_t nvb = 4096;
    std::memcpy(head + 0, &magic, 4);
    std::memcpy(head + 4, &version, 4);
    std::memcpy(head + 8, &endian, 4);
    std::memcpy(head + 12, &nvb, 4);

    uint32_t got = 0;
    REQUIRE(parseSidecarHead(head, sizeof(head), got));
    REQUIRE(got == 4096);

    // Short buffer.
    REQUIRE_FALSE(parseSidecarHead(head, SIDECAR_HEAD_BYTES - 1, got));

    // Wrong magic.
    uint8_t bad[SIDECAR_HEAD_BYTES];
    std::memcpy(bad, head, sizeof(bad));
    bad[0] ^= 0xFF;
    REQUIRE_FALSE(parseSidecarHead(bad, sizeof(bad), got));
}

TEST_CASE("v15 critical/deferred metadata split round-trips + rejects truncation",
          "[streaming]") {
    fs::path dir = makeScratchDir("v15split");
    fs::path ifc = dir / "model.ifc";
    SidecarData sd = buildFixture();
    sd.chunks = { {0, 1}, {1, 1} };  // a TOC, so the critical block carries chunks
    REQUIRE(writeSidecar(ifc.string(), sd));

    // readSidecarMetadataOnly (desktop) reads BOTH blocks + records the locator.
    auto meta = readSidecarMetadataOnly(ifc.string());
    REQUIRE(meta.has_value());
    REQUIRE(meta->meta.meshes.size()      == sd.meshes.size());   // critical
    REQUIRE(meta->meta.chunks.size()      == sd.chunks.size());   // critical
    REQUIRE(meta->meta.elements.size()    == sd.elements.size()); // deferred
    REQUIRE(meta->meta.string_table       == sd.string_table);    // deferred
    REQUIRE(meta->critical_meta_bytes > 0);

    // Pull the raw critical block via the recorded locator and parse it alone —
    // exactly what the web loader does before painting.
    FILE* f = std::fopen((dir / "model.ifcview").string().c_str(), "rb");
    REQUIRE(f);
    std::vector<uint8_t> crit(size_t(meta->critical_meta_bytes));
    std::fseek(f, long(meta->critical_meta_offset), SEEK_SET);
    REQUIRE(std::fread(crit.data(), 1, crit.size(), f) == crit.size());
    std::fclose(f);

    SidecarData c;
    REQUIRE(parseSidecarCritical(crit.data(), crit.size(), c));
    REQUIRE(c.meshes.size()    == sd.meshes.size());
    REQUIRE(c.chunks.size()    == sd.chunks.size());
    REQUIRE(c.elements.empty());  // the critical block has no property data
    SidecarData chopped;
    REQUIRE_FALSE(parseSidecarCritical(crit.data(), crit.size() - 1, chopped));
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
