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

#include <cstdio>
#include <cstring>

// Binary layout (all multi-byte fields native-endian):
//
//   SidecarHeader          (16 bytes)
//   uint64_t               source_file_size
//
//   uint32_t               num_vertices  (count of floats)
//   float[num_vertices]    vertex data
//
//   uint32_t               num_indices
//   uint32_t[num_indices]  index data
//
//   uint32_t               num_draw_infos
//   ObjectDrawInfo[N]      draw info array
//
//   uint32_t               num_elements
//   PackedElementInfo[N]   element records
//   uint32_t               string_table_bytes
//   char[string_table_bytes]
//
//   uint32_t               num_bvh_models
//   for each model:
//     uint32_t model_id
//     uint32_t num_nodes
//     BvhNode[num_nodes]
//     uint32_t num_object_indices
//     uint32_t[num_object_indices]

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

    // Header
    SidecarHeader hdr = { SIDECAR_MAGIC, SIDECAR_VERSION, SIDECAR_ENDIAN, 0 };
    fwrite(&hdr, sizeof(hdr), 1, f);
    fwrite(&ifc_file_size, 8, 1, f);

    // Geometry
    if (!writeVec(f, data.vertices)) { fclose(f); return false; }
    if (!writeVec(f, data.indices))  { fclose(f); return false; }

    // Draw info
    if (!writeVec(f, data.draw_info)) { fclose(f); return false; }

    // Elements + string table
    if (!writeVec(f, data.elements)) { fclose(f); return false; }
    uint32_t stbl_len = static_cast<uint32_t>(data.string_table.size());
    fwrite(&stbl_len, 4, 1, f);
    if (stbl_len > 0) fwrite(data.string_table.data(), 1, stbl_len, f);

    // BVH
    uint32_t num_bvh_models = data.bvh_set
        ? static_cast<uint32_t>(data.bvh_set->models.size()) : 0;
    fwrite(&num_bvh_models, 4, 1, f);

    if (data.bvh_set) {
        for (const auto& [model_id, mbvh] : data.bvh_set->models) {
            fwrite(&model_id, 4, 1, f);

            uint32_t nn = static_cast<uint32_t>(mbvh.nodes.size());
            fwrite(&nn, 4, 1, f);
            if (nn > 0) fwrite(mbvh.nodes.data(), sizeof(BvhNode), nn, f);

            uint32_t no = static_cast<uint32_t>(mbvh.object_indices.size());
            fwrite(&no, 4, 1, f);
            if (no > 0) fwrite(mbvh.object_indices.data(), 4, no, f);
        }
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

    // Header
    SidecarHeader hdr;
    if (fread(&hdr, sizeof(hdr), 1, f) != 1) return fail();
    if (hdr.magic != SIDECAR_MAGIC ||
        hdr.version != SIDECAR_VERSION ||
        hdr.endian != SIDECAR_ENDIAN) return fail();

    uint64_t stored_size;
    if (fread(&stored_size, 8, 1, f) != 1) return fail();
    if (stored_size != ifc_file_size) return fail();

    SidecarData data;

    // Geometry
    if (!readVec(f, data.vertices)) return fail();
    if (!readVec(f, data.indices))  return fail();

    // Draw info
    if (!readVec(f, data.draw_info)) return fail();

    // Elements + string table
    if (!readVec(f, data.elements)) return fail();
    uint32_t stbl_len;
    if (fread(&stbl_len, 4, 1, f) != 1) return fail();
    data.string_table.resize(stbl_len);
    if (stbl_len > 0 && fread(data.string_table.data(), 1, stbl_len, f) != stbl_len)
        return fail();

    // BVH
    uint32_t num_bvh_models;
    if (fread(&num_bvh_models, 4, 1, f) != 1) return fail();

    if (num_bvh_models > 0) {
        data.bvh_set = std::make_shared<BvhSet>();
        for (uint32_t m = 0; m < num_bvh_models; ++m) {
            uint32_t model_id;
            if (fread(&model_id, 4, 1, f) != 1) return fail();

            ModelBvh mbvh;
            mbvh.model_id = model_id;

            uint32_t nn;
            if (fread(&nn, 4, 1, f) != 1) return fail();
            mbvh.nodes.resize(nn);
            if (nn > 0 && fread(mbvh.nodes.data(), sizeof(BvhNode), nn, f) != nn)
                return fail();

            uint32_t no;
            if (fread(&no, 4, 1, f) != 1) return fail();
            mbvh.object_indices.resize(no);
            if (no > 0 && fread(mbvh.object_indices.data(), 4, no, f) != no)
                return fail();

            data.bvh_set->bvh_model_ids.insert(model_id);
            data.bvh_set->models[model_id] = std::move(mbvh);
        }
    }

    fclose(f);
    return data;
}
