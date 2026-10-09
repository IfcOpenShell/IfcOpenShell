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

#include "SidecarReader.h"
#include "InstanceCompose.h"

#include <zstd.h>

#include <algorithm>
#include <cstdio>
#include <cstring>

namespace {

// Bounds-checked forward cursor over an in-memory buffer, so a truncated
// block fails cleanly (return false) instead of reading out of bounds.
struct BufCursor {
    const uint8_t* cursor;
    size_t remaining_bytes;

    bool read(void* dst, size_t bytes) {
        if (bytes > remaining_bytes) return false;
        std::memcpy(dst, cursor, bytes);
        cursor += bytes;
        remaining_bytes -= bytes;
        return true;
    }

    // Read a uint32 length prefix followed by length*sizeof(T) elements.
    template<typename T>
    bool readVec(std::vector<T>& values) {
        uint32_t n;
        if (!read(&n, 4)) return false;
        if (uint64_t(n) * sizeof(T) > remaining_bytes) return false;
        values.resize(n);
        if (n > 0 && !read(values.data(), size_t(n) * sizeof(T))) return false;
        return true;
    }
};

}  // namespace

bool decompressSidecarFrame(const std::uint8_t* src, std::size_t src_size,
                            std::uint8_t* dst, std::size_t raw_size) {
    if (raw_size == 0) return src_size == 0;  // empty in ↔ empty out
    if (!src || !dst || src_size == 0) return false;
    const size_t got = ZSTD_decompress(dst, raw_size, src, src_size);
    return !ZSTD_isError(got) && got == raw_size;
}

bool readInstanceInfos(const std::uint8_t*& cursor, std::size_t& remaining,
                       const std::vector<MeshInfo>& meshes,
                       std::vector<InstanceInfo>& out) {
    std::uint32_t count = 0;
    if (remaining < 4) return false;
    std::memcpy(&count, cursor, 4);
    cursor += 4;
    remaining -= 4;
    if (std::uint64_t(count) * SIDECAR_INSTANCE_RECORD_BYTES > remaining) return false;

    const Eigen::Matrix4d identity = Eigen::Matrix4d::Identity();
    const float zero[3] = {0.0f, 0.0f, 0.0f};
    out.assign(count, InstanceInfo{});
    for (InstanceInfo& inst : out) {
        double translation[3];
        float linear[9];
        std::memcpy(&inst.mesh_id, cursor, 4);              cursor += 4;
        std::memcpy(&inst.object_id, cursor, 4);            cursor += 4;
        std::memcpy(translation, cursor, sizeof(translation)); cursor += sizeof(translation);
        std::memcpy(linear, cursor, sizeof(linear));           cursor += sizeof(linear);
        double* p = inst.placement_transformation;  // column-major
        p[0] = linear[0]; p[1] = linear[1]; p[2]  = linear[2]; p[3]  = 0.0;
        p[4] = linear[3]; p[5] = linear[4]; p[6]  = linear[5]; p[7]  = 0.0;
        p[8] = linear[6]; p[9] = linear[7]; p[10] = linear[8]; p[11] = 0.0;
        p[12] = translation[0]; p[13] = translation[1]; p[14] = translation[2]; p[15] = 1.0;

        // An instance naming a mesh the file does not have gets an empty
        // world box, as ViewportCore::composeInstanceFromPlacement does, so
        // it never passes a cull.
        const bool known_mesh = inst.mesh_id < meshes.size();
        InstanceCompose::composeInstance(
            inst.placement_transformation, identity, identity, identity,
            known_mesh ? meshes[inst.mesh_id].local_aabb_min : zero,
            known_mesh ? meshes[inst.mesh_id].local_aabb_max : zero,
            inst.transform, inst.world_aabb_min, inst.world_aabb_max);
        if (!known_mesh) {
            for (int a = 0; a < 3; ++a) inst.world_aabb_min[a] = inst.world_aabb_max[a] = 0.0f;
        }
    }
    remaining -= std::size_t(count) * SIDECAR_INSTANCE_RECORD_BYTES;
    return true;
}

bool parseSidecarHead(const uint8_t* data, size_t n, uint64_t& out_geom_bytes) {
    if (n < SIDECAR_HEAD_BYTES) return false;
    SidecarHeader hdr;
    std::memcpy(&hdr, data, sizeof(hdr));
    if (hdr.magic   != SIDECAR_MAGIC)  return false;
    if (hdr.version != SIDECAR_VERSION) return false;
    if (hdr.endian  != SIDECAR_ENDIAN) return false;
    std::memcpy(&out_geom_bytes, data + sizeof(hdr), sizeof(out_geom_bytes));
    return true;
}

bool parseSidecarGeometryMetadata(const uint8_t* data, size_t n, SidecarData& out) {
    BufCursor c{data, n};
    if (!c.readVec(out.meshes))    return false;
    if (!readInstanceInfos(c.cursor, c.remaining_bytes, out.meshes, out.instances)) return false;
    if (!c.read(&out.has_coordinate_operation, 4))                  return false;
    if (!c.read(out.coordinate_operation_meters, sizeof(double) * 16)) return false;
    if (!c.read(&out.project_length_to_meters, sizeof(double)))     return false;
    if (!c.read(&out.map_unit_to_meters, sizeof(double)))          return false;
    if (!c.readVec(out.chunks)) return false;
    return true;
}

bool parseSidecarElementMetadata(const uint8_t* data, size_t n, SidecarData& out) {
    BufCursor c{data, n};
    if (!c.readVec(out.elements)) return false;
    uint32_t stbl_len = 0;
    if (!c.read(&stbl_len, 4))       return false;
    if (stbl_len > c.remaining_bytes) return false;
    out.string_table.resize(stbl_len);
    if (stbl_len > 0 && !c.read(out.string_table.data(), stbl_len)) return false;
    return true;
}

std::optional<StreamingSidecar> readSidecarMetadata(const std::string& ifc_path) {
    const std::string path = sidecarPathFor(ifc_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return std::nullopt;

    auto fail = [&]() -> std::optional<StreamingSidecar> {
        std::fclose(f);
        return std::nullopt;
    };

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
        return decompressSidecarFrame(z.data(), z.size(), raw.data(), raw.size());
    };

    std::vector<uint8_t> geometry_metadata, element_metadata;
    if (!readBlock(geometry_metadata)) return fail();
    if (!readBlock(element_metadata, &out.element_metadata_comp_offset, &out.element_metadata_comp_size,
                   &out.element_metadata_raw_size)) return fail();
    std::fclose(f);

    // Desktop reads both blocks up front; the web path reads only geometry
    // metadata before painting and fetches the element metadata block on demand.
    if (!parseSidecarGeometryMetadata(geometry_metadata.data(), geometry_metadata.size(), out.meta))
        return std::nullopt;
    if (!parseSidecarElementMetadata(element_metadata.data(), element_metadata.size(), out.meta))
        return std::nullopt;
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
    const std::string path = sidecarPathFor(ifc_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    auto readFrame = [&](std::uint64_t off, std::uint64_t comp, std::uint64_t raw,
                         std::uint8_t* dst) -> bool {
        if (raw == 0) return comp == 0;
        std::vector<std::uint8_t> z(static_cast<size_t>(comp));
        if (std::fseek(f, long(geometry_section_offset + off), SEEK_SET) != 0) return false;
        if (comp && std::fread(z.data(), 1, z.size(), f) != z.size()) return false;
        return decompressSidecarFrame(z.data(), z.size(), dst, size_t(raw));
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
