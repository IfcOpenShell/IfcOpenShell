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

// v13 sidecar layout (matched against SidecarCache.cpp):
//
//   SidecarHeader (12 bytes)
//   uint32 num_vertex_bytes
//   uint8[num_vertex_bytes] vertex data            <-- streaming skips
//   uint32 num_indices
//   uint32[num_indices] index data                  <-- streaming skips
//   uint32 num_meshes + MeshInfo[]                  <-- streaming reads
//   uint32 num_instances + InstanceCpu[]            <-- streaming reads
//   uint32 has_coord_op + double[16] + 2× double    <-- streaming reads
//   uint32 num_elements + PackedElementInfo[]       <-- streaming reads
//   uint32 string_table_bytes + char[]              <-- streaming reads
//
// Streaming reader returns offsets to the two skipped sections so chunks
// can be range-read on demand. File handle is closed before return.

#include "StreamingLoader.h"
#include "SidecarCompress.h"

#include <algorithm>
#include <cstdio>
#include <cstring>

namespace {

struct SidecarHeaderRaw {
    uint32_t magic;
    uint32_t version;
    uint32_t endian;
};

// Bounds-checked forward cursor over an in-memory buffer. parseSidecarTail
// walks the metadata tail through one of these so a truncated buffer fails
// cleanly (return false) instead of reading out of bounds.
struct BufCursor {
    const uint8_t* p;
    size_t remaining;

    bool take(void* dst, size_t bytes) {
        if (bytes > remaining) return false;
        std::memcpy(dst, p, bytes);
        p += bytes;
        remaining -= bytes;
        return true;
    }

    // Read a uint32 length prefix followed by length*sizeof(T) elements.
    template<typename T>
    bool takeVec(std::vector<T>& v) {
        uint32_t n;
        if (!take(&n, 4)) return false;
        if (uint64_t(n) * sizeof(T) > remaining) return false;
        v.resize(n);
        if (n > 0 && !take(v.data(), size_t(n) * sizeof(T))) return false;
        return true;
    }
};

std::string sidecarPath(const std::string& ifc_path) {
    std::string p = ifc_path;
    while (!p.empty() && (p.back() == '/' || p.back() == '\\')) p.pop_back();
    auto slash = p.find_last_of("/\\");
    auto dot   = p.find_last_of('.');
    std::string stem = (dot != std::string::npos &&
                        (slash == std::string::npos || dot > slash))
                           ? p.substr(0, dot)
                           : p;
    return stem + ".ifcview";
}

}  // namespace

bool parseSidecarHead(const uint8_t* data, size_t n, uint64_t& out_geom_bytes) {
    if (n < SIDECAR_HEAD_BYTES) return false;
    SidecarHeaderRaw hdr;
    std::memcpy(&hdr, data, sizeof(hdr));
    if (hdr.magic   != SIDECAR_MAGIC)  return false;
    if (hdr.version != SIDECAR_VERSION) return false;
    if (hdr.endian  != SIDECAR_ENDIAN) return false;
    std::memcpy(&out_geom_bytes, data + sizeof(hdr), 8);
    return true;
}

bool parseSidecarCritical(const uint8_t* data, size_t n, SidecarData& out) {
    // v15 render-critical block: meshes, instances, georef, chunk TOC.
    BufCursor c{data, n};
    if (!c.takeVec(out.meshes))    return false;
    if (!c.takeVec(out.instances)) return false;
    if (!c.take(&out.has_coordinate_operation, 4))                  return false;
    if (!c.take(out.coordinate_operation_meters, sizeof(double) * 16)) return false;
    if (!c.take(&out.project_length_to_meters, sizeof(double)))     return false;
    if (!c.take(&out.map_unit_to_meters, sizeof(double)))          return false;
    if (!c.takeVec(out.chunks)) return false;
    return true;
}

bool parseSidecarDeferred(const uint8_t* data, size_t n, SidecarData& out) {
    // v15 deferred block: element tree + string table (UI/picking, not rendered).
    BufCursor c{data, n};
    if (!c.takeVec(out.elements)) return false;
    uint32_t stbl_len = 0;
    if (!c.take(&stbl_len, 4))       return false;
    if (stbl_len > c.remaining)      return false;
    out.string_table.resize(stbl_len);
    if (stbl_len > 0 && !c.take(out.string_table.data(), stbl_len)) return false;
    return true;
}

std::optional<StreamingSidecar> readSidecarMetadataOnly(const std::string& ifc_path) {
    const std::string path = sidecarPath(ifc_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return std::nullopt;

    auto fail = [&]() -> std::optional<StreamingSidecar> {
        std::fclose(f);
        return std::nullopt;
    };

    // Head (v16): 12-byte header + the compressed-geometry-section length. The
    // metadata blocks follow the geometry at SIDECAR_HEAD_BYTES + geom_bytes.
    uint8_t head[SIDECAR_HEAD_BYTES];
    if (std::fread(head, 1, SIDECAR_HEAD_BYTES, f) != SIDECAR_HEAD_BYTES) return fail();
    uint64_t geom_bytes = 0;
    if (!parseSidecarHead(head, SIDECAR_HEAD_BYTES, geom_bytes)) return fail();

    StreamingSidecar out;
    out.file_path                = path;
    out.geometry_section_offset  = SIDECAR_HEAD_BYTES;

    // Skip the geometry section; the two compressed metadata blocks follow.
    if (std::fseek(f, long(SIDECAR_HEAD_BYTES) + long(geom_bytes), SEEK_SET) != 0)
        return fail();

    // Each metadata block on disk is [comp u64][raw u64][zstd frame].
    auto readBlock = [&](std::vector<uint8_t>& raw,
                         uint64_t* comp_off = nullptr, uint64_t* comp_sz = nullptr,
                         uint64_t* raw_sz = nullptr) -> bool {
        uint64_t comp = 0, rawn = 0;
        if (std::fread(&comp, 8, 1, f) != 1 || std::fread(&rawn, 8, 1, f) != 1) return false;
        const long here = std::ftell(f);
        std::vector<uint8_t> z(static_cast<size_t>(comp));
        if (comp && std::fread(z.data(), 1, z.size(), f) != z.size()) return false;
        raw.assign(size_t(rawn), 0);
        if (comp_off) *comp_off = uint64_t(here);
        if (comp_sz)  *comp_sz  = comp;
        if (raw_sz)   *raw_sz   = rawn;
        return SidecarCompress::decompress(z.data(), z.size(), raw.data(), raw.size());
    };

    std::vector<uint8_t> crit, def;
    if (!readBlock(crit)) return fail();
    if (!readBlock(def, &out.deferred_comp_offset, &out.deferred_comp_size,
                   &out.deferred_raw_size)) return fail();
    std::fclose(f);

    // Desktop reads both blocks up front; the web path reads only critical
    // before painting and fetches the deferred block on demand.
    if (!parseSidecarCritical(crit.data(), crit.size(), out.meta)) return std::nullopt;
    if (!parseSidecarDeferred(def.data(), def.size(), out.meta))   return std::nullopt;
    return out;
}

bool readChunkGeometryCompressed(const std::string& ifc_path,
                                 std::uint64_t geometry_section_offset,
                                 std::uint64_t v_comp_off, std::uint64_t v_comp_size,
                                 std::uint64_t v_raw_size,
                                 std::uint64_t i_comp_off, std::uint64_t i_comp_size,
                                 std::uint64_t i_raw_size,
                                 std::vector<std::uint8_t>&  out_vbytes,
                                 std::vector<std::uint32_t>& out_idx) {
    const std::string path = sidecarPath(ifc_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    auto readFrame = [&](std::uint64_t off, std::uint64_t comp, std::uint64_t raw,
                         std::uint8_t* dst) -> bool {
        if (raw == 0) return comp == 0;
        std::vector<std::uint8_t> z(static_cast<size_t>(comp));
        if (std::fseek(f, long(geometry_section_offset + off), SEEK_SET) != 0) return false;
        if (comp && std::fread(z.data(), 1, z.size(), f) != z.size()) return false;
        return SidecarCompress::decompress(z.data(), z.size(), dst, size_t(raw));
    };
    out_vbytes.assign(size_t(v_raw_size), 0);
    out_idx.assign(size_t(i_raw_size / sizeof(std::uint32_t)), 0);
    const bool ok =
        readFrame(v_comp_off, v_comp_size, v_raw_size, out_vbytes.data()) &&
        readFrame(i_comp_off, i_comp_size, i_raw_size,
                  reinterpret_cast<std::uint8_t*>(out_idx.data()));
    std::fclose(f);
    return ok;
}

bool readSidecarVertexChunk(const std::string& ifc_path,
                            uint64_t vertex_section_offset,
                            uint64_t chunk_byte_offset,
                            uint64_t chunk_byte_size,
                            std::vector<uint8_t>& out_bytes) {
    if (chunk_byte_size == 0) { out_bytes.clear(); return true; }

    const std::string path = sidecarPath(ifc_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    if (std::fseek(f, long(vertex_section_offset + chunk_byte_offset), SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    out_bytes.resize(size_t(chunk_byte_size));
    const size_t got = std::fread(out_bytes.data(), 1, size_t(chunk_byte_size), f);
    std::fclose(f);
    return got == size_t(chunk_byte_size);
}

bool readSidecarIndexChunk(const std::string& ifc_path,
                           uint64_t index_section_offset,
                           uint64_t chunk_first_index,
                           uint64_t chunk_index_count,
                           std::vector<uint32_t>& out_indices) {
    if (chunk_index_count == 0) { out_indices.clear(); return true; }

    const std::string path = sidecarPath(ifc_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    const uint64_t byte_offset = index_section_offset + chunk_first_index * 4u;
    if (std::fseek(f, long(byte_offset), SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    out_indices.resize(size_t(chunk_index_count));
    const size_t got = std::fread(out_indices.data(), sizeof(uint32_t),
                                  size_t(chunk_index_count), f);
    std::fclose(f);
    return got == size_t(chunk_index_count);
}

// Coalesce ranges that are close in file order into single reads. The input
// order is preserved in the destination buffer; we just merge reads on the
// source side. A `max_gap_bytes` tolerance lets us swallow small gaps when one
// read is cheaper than a seek + fresh read.
//
// Callers must lay out the destination in INPUT order; the reader scatters
// bytes via per-input-range dst offsets after a single coalesced read.
std::vector<SidecarReadPlan> planSidecarReadRanges(
        uint64_t section_offset,
        const std::vector<std::pair<uint64_t, uint64_t>>& ranges,
        uint64_t max_gap_bytes) {
    // Sort by file offset, remembering original order so we can scatter
    // to the destination correctly.
    struct Indexed { uint64_t off, size, dst; };
    std::vector<Indexed> sorted;
    sorted.reserve(ranges.size());
    uint64_t dst_cursor = 0;
    for (const auto& [off, sz] : ranges) {
        sorted.push_back({off, sz, dst_cursor});
        dst_cursor += sz;
    }
    std::sort(sorted.begin(), sorted.end(),
              [](const Indexed& a, const Indexed& b) { return a.off < b.off; });

    std::vector<SidecarReadPlan> plans;
    for (const auto& r : sorted) {
        if (r.size == 0) continue;
        if (!plans.empty()) {
            SidecarReadPlan& back = plans.back();
            const uint64_t end_of_back = back.file_offset + back.read_size;
            const uint64_t r_file = section_offset + r.off;
            if (r_file >= end_of_back && r_file - end_of_back <= max_gap_bytes) {
                // Merge: extend the read to include r (plus any gap).
                const uint64_t new_size = (r_file + r.size) - back.file_offset;
                back.slices.push_back({
                    r_file - back.file_offset,  // src within read
                    r.dst,
                    r.size,
                });
                back.read_size = new_size;
                continue;
            }
        }
        SidecarReadPlan np;
        np.file_offset = section_offset + r.off;
        np.read_size   = r.size;
        np.slices.push_back({0, r.dst, r.size});
        plans.push_back(std::move(np));
    }
    return plans;
}

bool readSidecarVertexRanges(const std::string& ifc_path,
                             uint64_t vertex_section_offset,
                             const std::vector<std::pair<uint64_t, uint64_t>>& ranges,
                             std::vector<uint8_t>& out_bytes) {
    uint64_t total = 0;
    for (const auto& r : ranges) total += r.second;
    out_bytes.resize(size_t(total));
    if (total == 0) return true;

    // 64 KB max gap: on SSDs a small contiguous read is much cheaper
    // than a seek + fresh read, even if some bytes are discarded.
    auto plans = planSidecarReadRanges(vertex_section_offset, ranges, 64 * 1024);

    const std::string path = sidecarPath(ifc_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;

    std::vector<uint8_t> scratch;
    for (const auto& p : plans) {
        scratch.resize(size_t(p.read_size));
        if (std::fseek(f, long(p.file_offset), SEEK_SET) != 0) { std::fclose(f); return false; }
        if (std::fread(scratch.data(), 1, scratch.size(), f) != scratch.size()) {
            std::fclose(f); return false;
        }
        for (const auto& s : p.slices) {
            std::memcpy(out_bytes.data() + s.dst_offset,
                        scratch.data() + s.src_offset, size_t(s.bytes));
        }
    }
    std::fclose(f);
    return true;
}

bool readSidecarIndexRanges(const std::string& ifc_path,
                            uint64_t index_section_offset,
                            const std::vector<std::pair<uint64_t, uint64_t>>& ranges,
                            std::vector<uint32_t>& out_indices) {
    uint64_t total = 0;
    for (const auto& r : ranges) total += r.second;
    out_indices.resize(size_t(total));
    if (total == 0) return true;

    // Convert u32-range (first_u32, count_u32) to byte-range
    // (file_offset, byte_size). Then coalesce + read.
    std::vector<std::pair<uint64_t, uint64_t>> byte_ranges;
    byte_ranges.reserve(ranges.size());
    uint64_t out_byte_cursor = 0;
    for (const auto& [first_u32, count] : ranges) {
        // Store byte offsets relative to the index section.
        byte_ranges.emplace_back(first_u32 * 4u, count * 4u);
        out_byte_cursor += count * 4u;
    }
    auto plans = planSidecarReadRanges(index_section_offset, byte_ranges, 64 * 1024);

    const std::string path = sidecarPath(ifc_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;

    std::vector<uint8_t> scratch;
    uint8_t* out_bytes = reinterpret_cast<uint8_t*>(out_indices.data());
    for (const auto& p : plans) {
        scratch.resize(size_t(p.read_size));
        if (std::fseek(f, long(p.file_offset), SEEK_SET) != 0) { std::fclose(f); return false; }
        if (std::fread(scratch.data(), 1, scratch.size(), f) != scratch.size()) {
            std::fclose(f); return false;
        }
        for (const auto& s : p.slices) {
            std::memcpy(out_bytes + s.dst_offset,
                        scratch.data() + s.src_offset, size_t(s.bytes));
        }
    }
    std::fclose(f);
    return true;
}
