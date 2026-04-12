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

// v4 layout (all multi-byte fields native-endian; endianness marker in header):
//
//   SidecarHeader (16 bytes)
//   uint64_t  source_file_size
//
//   uint32_t  num_vertices_floats
//   float[]   vertex data (28 B/vertex: pos3 + normal3 + color1_packed)
//   uint32_t  num_indices
//   uint32_t[] index data (mesh-local indices; base_vertex applied at draw time)
//
//   uint32_t  num_meshes
//   MeshInfo[num_meshes]
//
//   uint32_t  num_instances
//   InstanceCpu[num_instances]   (already sorted by mesh_id)
//
//   uint32_t  num_elements
//   PackedElementInfo[num_elements]
//   uint32_t  string_table_bytes
//   char[string_table_bytes]

#include "SidecarCache.h"

#include <cstdio>
#include <cstring>

struct SidecarHeader {
    uint32_t magic;
    uint32_t version;
    uint32_t endian;
    uint32_t reserved;
};

static std::string sidecarPath(const std::string& ifc_path) {
    return ifc_path + ".ifcview";
}

template<typename T>
static bool writeVec(FILE* f, const std::vector<T>& v) {
    uint32_t n = static_cast<uint32_t>(v.size());
    if (fwrite(&n, 4, 1, f) != 1) return false;
    if (n > 0 && fwrite(v.data(), sizeof(T), n, f) != n) return false;
    return true;
}

template<typename T>
static bool readVec(FILE* f, std::vector<T>& v) {
    uint32_t n;
    if (fread(&n, 4, 1, f) != 1) return false;
    v.resize(n);
    if (n > 0 && fread(v.data(), sizeof(T), n, f) != n) return false;
    return true;
}

bool writeSidecar(const std::string& ifc_path,
                  const SidecarData& data,
                  uint64_t ifc_file_size) {
    std::string path = sidecarPath(ifc_path);
    FILE* f = fopen(path.c_str(), "wb");
    if (!f) return false;

    SidecarHeader hdr = { SIDECAR_MAGIC, SIDECAR_VERSION, SIDECAR_ENDIAN, 0 };
    if (fwrite(&hdr, sizeof(hdr), 1, f) != 1)    { fclose(f); return false; }
    if (fwrite(&ifc_file_size, 8, 1, f) != 1)    { fclose(f); return false; }

    if (!writeVec(f, data.vertices))  { fclose(f); return false; }
    if (!writeVec(f, data.indices))   { fclose(f); return false; }
    if (!writeVec(f, data.meshes))    { fclose(f); return false; }
    if (!writeVec(f, data.instances)) { fclose(f); return false; }
    if (!writeVec(f, data.elements))  { fclose(f); return false; }

    uint32_t stbl_len = static_cast<uint32_t>(data.string_table.size());
    if (fwrite(&stbl_len, 4, 1, f) != 1) { fclose(f); return false; }
    if (stbl_len > 0 && fwrite(data.string_table.data(), 1, stbl_len, f) != stbl_len) {
        fclose(f); return false;
    }

    fclose(f);
    return true;
}

std::optional<SidecarData> readSidecar(const std::string& ifc_path,
                                       uint64_t ifc_file_size) {
    std::string path = sidecarPath(ifc_path);
    FILE* f = fopen(path.c_str(), "rb");
    if (!f) return std::nullopt;

    auto fail = [&]() -> std::optional<SidecarData> { fclose(f); return std::nullopt; };

    SidecarHeader hdr;
    if (fread(&hdr, sizeof(hdr), 1, f) != 1) return fail();
    if (hdr.magic  != SIDECAR_MAGIC   ||
        hdr.version != SIDECAR_VERSION ||
        hdr.endian != SIDECAR_ENDIAN) return fail();

    uint64_t stored_size;
    if (fread(&stored_size, 8, 1, f) != 1)  return fail();
    if (stored_size != ifc_file_size)       return fail();

    SidecarData data;
    if (!readVec(f, data.vertices))  return fail();
    if (!readVec(f, data.indices))   return fail();
    if (!readVec(f, data.meshes))    return fail();
    if (!readVec(f, data.instances)) return fail();
    if (!readVec(f, data.elements))  return fail();

    uint32_t stbl_len;
    if (fread(&stbl_len, 4, 1, f) != 1) return fail();
    data.string_table.resize(stbl_len);
    if (stbl_len > 0 && fread(data.string_table.data(), 1, stbl_len, f) != stbl_len)
        return fail();

    fclose(f);
    return data;
}
