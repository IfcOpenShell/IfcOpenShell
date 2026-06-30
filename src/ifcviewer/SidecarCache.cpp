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

// v13 layout (all multi-byte fields native-endian; endianness marker in header).
//
//   SidecarHeader (12 bytes)
//
//   uint32_t  num_vertex_bytes
//   uint8_t[] vertex data (12 B/vertex: pos u16x3 + oct-normal i8x2 + rgba8)
//   uint32_t  num_indices
//   uint32_t[] index data (mesh-local indices; base_vertex applied at draw time)
//
//   uint32_t  num_meshes
//   MeshInfo[num_meshes]
//
//   uint32_t  num_instances
//   InstanceCpu[num_instances]   (already sorted by mesh_id; v13 layout)
//
//   uint32_t  has_coordinate_operation              (v11+)
//   double[16] coordinate_operation_meters          (v11+; column-major)
//   double    project_length_to_meters              (v11+)
//   double    map_unit_to_meters                    (v11+)
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
};

// foo.ifc       -> foo.ifcview
// foo.ifcdb/    -> foo.ifcview
// foo.ifcdb     -> foo.ifcview
// foo (no ext)  -> foo.ifcview
static std::string sidecarPath(const std::string& ifc_path) {
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

bool writeSidecar(const std::string& ifc_path, const SidecarData& data) {
    std::string path = sidecarPath(ifc_path);
    FILE* f = fopen(path.c_str(), "wb");
    if (!f) return false;

    SidecarHeader hdr = { SIDECAR_MAGIC, SIDECAR_VERSION, SIDECAR_ENDIAN };
    if (fwrite(&hdr, sizeof(hdr), 1, f) != 1)    { fclose(f); return false; }

    if (!writeVec(f, data.vertices))  { fclose(f); return false; }
    if (!writeVec(f, data.indices))   { fclose(f); return false; }

    // v15: a render-critical metadata block (meshes, instances, georef, chunk
    // TOC) preceded by its byte length, then a deferred block (elements +
    // string_table). The length lets the web loader read just the critical
    // block before painting and fetch the property data lazily / not at all.
    const long crit_len_pos = ftell(f);
    uint64_t crit_bytes = 0;
    if (fwrite(&crit_bytes, sizeof(crit_bytes), 1, f) != 1) { fclose(f); return false; }
    const long crit_start = ftell(f);

    if (!writeVec(f, data.meshes))    { fclose(f); return false; }
    if (!writeVec(f, data.instances)) { fclose(f); return false; }
    // v11 georef block (148 B).
    if (fwrite(&data.has_coordinate_operation, 4, 1, f) != 1) { fclose(f); return false; }
    if (fwrite(data.coordinate_operation_meters,
               sizeof(double), 16, f) != 16)               { fclose(f); return false; }
    if (fwrite(&data.project_length_to_meters,
               sizeof(double), 1, f)  != 1)                { fclose(f); return false; }
    if (fwrite(&data.map_unit_to_meters,
               sizeof(double), 1, f)  != 1)                { fclose(f); return false; }
    if (!writeVec(f, data.chunks))    { fclose(f); return false; }

    // Backpatch the critical-block length.
    const long crit_end = ftell(f);
    if (crit_start < 0 || crit_end < 0) { fclose(f); return false; }
    crit_bytes = uint64_t(crit_end - crit_start);
    if (fseek(f, crit_len_pos, SEEK_SET) != 0) { fclose(f); return false; }
    if (fwrite(&crit_bytes, sizeof(crit_bytes), 1, f) != 1) { fclose(f); return false; }
    if (fseek(f, crit_end, SEEK_SET) != 0) { fclose(f); return false; }

    // Deferred block: element tree + string table (UI/picking, never rendered).
    if (!writeVec(f, data.elements))  { fclose(f); return false; }
    uint32_t stbl_len = static_cast<uint32_t>(data.string_table.size());
    if (fwrite(&stbl_len, 4, 1, f) != 1) { fclose(f); return false; }
    if (stbl_len > 0 && fwrite(data.string_table.data(), 1, stbl_len, f) != stbl_len) {
        fclose(f); return false;
    }

    fclose(f);
    return true;
}

std::optional<SidecarData> readSidecar(const std::string& ifc_path) {
    std::string path = sidecarPath(ifc_path);
    FILE* f = fopen(path.c_str(), "rb");
    if (!f) return std::nullopt;

    auto fail = [&]() -> std::optional<SidecarData> { fclose(f); return std::nullopt; };

    SidecarHeader hdr;
    if (fread(&hdr, sizeof(hdr), 1, f) != 1) return fail();
    if (hdr.magic  != SIDECAR_MAGIC   ||
        hdr.version != SIDECAR_VERSION ||
        hdr.endian != SIDECAR_ENDIAN) return fail();

    SidecarData data;
    if (!readVec(f, data.vertices))  return fail();
    if (!readVec(f, data.indices))   return fail();

    // v15 critical-block length (consumed; only the streaming/web readers need
    // it for a one-shot range read — here we read sequentially).
    uint64_t crit_bytes = 0;
    if (fread(&crit_bytes, sizeof(crit_bytes), 1, f) != 1) return fail();

    // Critical block: meshes, instances, georef, chunk TOC.
    if (!readVec(f, data.meshes))    return fail();
    if (!readVec(f, data.instances)) return fail();
    if (fread(&data.has_coordinate_operation, 4, 1, f) != 1) return fail();
    if (fread(data.coordinate_operation_meters,
              sizeof(double), 16, f) != 16)                  return fail();
    if (fread(&data.project_length_to_meters,
              sizeof(double), 1, f)  != 1)                   return fail();
    if (fread(&data.map_unit_to_meters,
              sizeof(double), 1, f)  != 1)                   return fail();
    if (!readVec(f, data.chunks))    return fail();

    // Deferred block: element tree + string table.
    if (!readVec(f, data.elements))  return fail();
    uint32_t stbl_len;
    if (fread(&stbl_len, 4, 1, f) != 1) return fail();
    data.string_table.resize(stbl_len);
    if (stbl_len > 0 && fread(data.string_table.data(), 1, stbl_len, f) != stbl_len)
        return fail();

    fclose(f);
    return data;
}
