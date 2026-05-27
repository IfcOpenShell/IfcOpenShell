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

#include "WgpuStreamingLoader.h"

#include <cstdio>

namespace {

struct SidecarHeaderRaw {
    uint32_t magic;
    uint32_t version;
    uint32_t endian;
};

template<typename T>
bool readVec(FILE* f, std::vector<T>& v) {
    uint32_t n;
    if (std::fread(&n, 4, 1, f) != 1) return false;
    v.resize(n);
    if (n > 0 && std::fread(v.data(), sizeof(T), n, f) != n) return false;
    return true;
}

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

std::optional<StreamingSidecar> readSidecarMetadataOnly(const std::string& ifc_path) {
    const std::string path = sidecarPath(ifc_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return std::nullopt;

    auto fail = [&]() -> std::optional<StreamingSidecar> {
        std::fclose(f);
        return std::nullopt;
    };

    SidecarHeaderRaw hdr;
    if (std::fread(&hdr, sizeof(hdr), 1, f) != 1)      return fail();
    if (hdr.magic   != SIDECAR_MAGIC)                  return fail();
    if (hdr.version != SIDECAR_VERSION)                return fail();
    if (hdr.endian  != SIDECAR_ENDIAN)                 return fail();

    StreamingSidecar out;
    out.file_path = path;

    // Vertex section: read count, record offset of data, seek past.
    uint32_t num_vertex_bytes = 0;
    if (std::fread(&num_vertex_bytes, 4, 1, f) != 1)   return fail();
    out.vertex_section_offset = uint64_t(std::ftell(f));
    out.vertex_total_bytes    = num_vertex_bytes;
    if (std::fseek(f, long(num_vertex_bytes), SEEK_CUR) != 0) return fail();

    // Index section: same dance, in u32 units.
    uint32_t num_indices = 0;
    if (std::fread(&num_indices, 4, 1, f) != 1)        return fail();
    out.index_section_offset = uint64_t(std::ftell(f));
    out.index_total_count    = num_indices;
    if (std::fseek(f, long(num_indices) * 4, SEEK_CUR) != 0) return fail();

    // Mesh dict + instance dict — small, load into meta.
    if (!readVec(f, out.meta.meshes))    return fail();
    if (!readVec(f, out.meta.instances)) return fail();

    // v11 georef block (148 bytes total).
    if (std::fread(&out.meta.has_coordinate_operation, 4, 1, f) != 1) return fail();
    if (std::fread(out.meta.coordinate_operation_meters,
                   sizeof(double), 16, f) != 16)                      return fail();
    if (std::fread(&out.meta.project_length_to_meters,
                   sizeof(double), 1, f) != 1)                        return fail();
    if (std::fread(&out.meta.map_unit_to_meters,
                   sizeof(double), 1, f) != 1)                        return fail();

    // Element table + string table.
    if (!readVec(f, out.meta.elements))                return fail();
    uint32_t stbl_len = 0;
    if (std::fread(&stbl_len, 4, 1, f) != 1)           return fail();
    out.meta.string_table.resize(stbl_len);
    if (stbl_len > 0 &&
        std::fread(out.meta.string_table.data(), 1, stbl_len, f) != stbl_len)
        return fail();

    std::fclose(f);
    return out;
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
