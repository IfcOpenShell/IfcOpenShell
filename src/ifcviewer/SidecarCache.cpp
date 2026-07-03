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
//   InstanceInfo[num_instances]   (already sorted by mesh_id; v13 layout)
//
//   uint32_t  has_coordinate_operation              (v11+)
//   double[16] coordinate_operation_meters          (v11+; column-major)
//   double    project_length_to_meters              (v11+)
//   double    map_unit_to_meters                    (v11+)
//
//   uint32_t  num_elements
//   ElementTableRecord[num_elements]
//   uint32_t  string_table_bytes
//   char[string_table_bytes]

#include "SidecarCache.h"
#include "SidecarCompress.h"

#include <cstdio>
#include <cstring>

// The baker (writeSidecar) compresses — desktop only; the web build never bakes
// and links a decompress-only zstd. Everything from here to writeSidecar's end
// is guarded off under Emscripten.
#if !defined(__EMSCRIPTEN__)

// zstd level for baking. 19 is near-max ratio; decode speed is level-
// independent and the bake is offline, so favour ratio.
static constexpr int kSidecarZstdLevel = 19;

// --- In-memory serialisation (a block is built in RAM, then compressed) ------
template<typename T>
static void appendVec(std::vector<std::uint8_t>& buffer, const std::vector<T>& values) {
    std::uint32_t count = static_cast<std::uint32_t>(values.size());
    const auto* count_bytes = reinterpret_cast<const std::uint8_t*>(&count);
    buffer.insert(buffer.end(), count_bytes, count_bytes + 4);
    if (count > 0) {
        const auto* value_bytes = reinterpret_cast<const std::uint8_t*>(values.data());
        buffer.insert(buffer.end(), value_bytes, value_bytes + std::size_t(sizeof(T)) * count);
    }
}
static void appendBytes(std::vector<std::uint8_t>& buffer, const void* data, std::size_t byte_count) {
    const auto* bytes = static_cast<const std::uint8_t*>(data);
    buffer.insert(buffer.end(), bytes, bytes + byte_count);
}

// Pull one chunk's geometry out of the whole-model vertex/index arrays into the
// chunk-LOCAL layout applyStreamedChunk expects: vertices of its meshes in chunk
// order, then indices as LOD0 (per mesh) followed by LOD1 (per mesh).
static void extractChunkGeometry(const SidecarData& sidecar_data, const SidecarChunk& sidecar_chunk,
                                 std::vector<std::uint8_t>& vbytes,
                                 std::vector<std::uint8_t>& ibytes) {
    vbytes.clear();
    ibytes.clear();
    const std::uint32_t end = sidecar_chunk.first_mesh + sidecar_chunk.mesh_count;
    for (std::uint32_t mesh_index = sidecar_chunk.first_mesh;
         mesh_index < end && mesh_index < sidecar_data.meshes.size();
         ++mesh_index) {
        const MeshInfo& mesh_info = sidecar_data.meshes[mesh_index];
        const std::size_t vertex_offset = mesh_info.vbo_byte_offset;
        const std::size_t vertex_byte_count =
            std::size_t(mesh_info.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        if (vertex_offset + vertex_byte_count <= sidecar_data.vertices.size())
            vbytes.insert(vbytes.end(), sidecar_data.vertices.begin() + vertex_offset,
                          sidecar_data.vertices.begin() + vertex_offset + vertex_byte_count);
    }
    auto appendIdx = [&](std::size_t first_u32, std::size_t count) {
        if (first_u32 + count > sidecar_data.indices.size()) return;
        const auto* index_bytes =
            reinterpret_cast<const std::uint8_t*>(sidecar_data.indices.data() + first_u32);
        ibytes.insert(ibytes.end(), index_bytes, index_bytes + count * sizeof(std::uint32_t));
    };
    for (std::uint32_t mesh_index = sidecar_chunk.first_mesh;
         mesh_index < end && mesh_index < sidecar_data.meshes.size();
         ++mesh_index) {
        const MeshInfo& mesh_info = sidecar_data.meshes[mesh_index];
        if (mesh_info.index_count) {
            appendIdx(mesh_info.ebo_byte_offset / sizeof(std::uint32_t), mesh_info.index_count);
        }
    }
    for (std::uint32_t mesh_index = sidecar_chunk.first_mesh;
         mesh_index < end && mesh_index < sidecar_data.meshes.size();
         ++mesh_index) {
        const MeshInfo& mesh_info = sidecar_data.meshes[mesh_index];
        if (mesh_info.lod1_index_count) {
            appendIdx(mesh_info.lod1_ebo_byte_offset / sizeof(std::uint32_t), mesh_info.lod1_index_count);
        }
    }
}
#endif  // !__EMSCRIPTEN__ (bake-only serialisation helpers)

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
    std::string path = ifc_path;
    while (!path.empty() && (path.back() == '/' || path.back() == '\\')) path.pop_back();
    auto slash = path.find_last_of("/\\");
    auto dot   = path.find_last_of('.');
    std::string stem = (dot != std::string::npos &&
                        (slash == std::string::npos || dot > slash))
                           ? path.substr(0, dot)
                           : path;
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

#if !defined(__EMSCRIPTEN__)  // bake path — compresses, desktop only
bool writeSidecar(const std::string& ifc_path, const SidecarData& data) {
    std::string path = sidecarPath(ifc_path);
    FILE* f = fopen(path.c_str(), "wb");
    if (!f) return false;

    auto write_bytes = [&](const void* data, std::size_t byte_count) {
        return fwrite(data, 1, byte_count, f) == byte_count;
    };
    auto wrU64 = [&](std::uint64_t v) { return write_bytes(&v, sizeof(v)); };
    auto wrBlock = [&](const std::vector<std::uint8_t>& raw) -> bool {
        auto z = SidecarCompress::compress(raw.data(), raw.size(), kSidecarZstdLevel);
        if (raw.size() > 0 && z.empty()) return false;  // compress failed
        return wrU64(z.size()) && wrU64(raw.size()) && (z.empty() || write_bytes(z.data(), z.size()));
    };

    SidecarHeader hdr = { SIDECAR_MAGIC, SIDECAR_VERSION, SIDECAR_ENDIAN };
    if (!write_bytes(&hdr, sizeof(hdr))) { fclose(f); return false; }

    // --- Geometry section: per-chunk zstd(vertex) + zstd(index) frames -------
    // Offsets in the chunk TOC are relative to the geometry section start, so
    // the loader range-fetches exactly one chunk without reading anything else.
    const long geom_len_pos = ftell(f);
    if (!wrU64(0)) { fclose(f); return false; }  // geom_bytes placeholder
    const long geom_start = ftell(f);

    std::vector<SidecarChunk> chunks = data.chunks;  // fill blob offsets below
    std::vector<std::uint8_t> vraw, iraw;
    for (auto& sidecar_chunk : chunks) {
        extractChunkGeometry(data, sidecar_chunk, vraw, iraw);
        auto vz = SidecarCompress::compress(vraw.data(), vraw.size(), kSidecarZstdLevel);
        auto iz = SidecarCompress::compress(iraw.data(), iraw.size(), kSidecarZstdLevel);
        if ((vraw.size() && vz.empty()) || (iraw.size() && iz.empty())) { fclose(f); return false; }
        sidecar_chunk.v_comp_off  = std::uint64_t(ftell(f) - geom_start);
        sidecar_chunk.v_comp_size = vz.size();
        sidecar_chunk.v_raw_size  = vraw.size();
        if (!vz.empty() && !write_bytes(vz.data(), vz.size())) { fclose(f); return false; }
        sidecar_chunk.i_comp_off  = std::uint64_t(ftell(f) - geom_start);
        sidecar_chunk.i_comp_size = iz.size();
        sidecar_chunk.i_raw_size  = iraw.size();
        if (!iz.empty() && !write_bytes(iz.data(), iz.size())) { fclose(f); return false; }
    }
    const long geom_end = ftell(f);
    if (geom_start < 0 || geom_end < 0) { fclose(f); return false; }
    if (fseek(f, geom_len_pos, SEEK_SET) != 0) { fclose(f); return false; }
    if (!wrU64(std::uint64_t(geom_end - geom_start))) { fclose(f); return false; }
    if (fseek(f, geom_end, SEEK_SET) != 0) { fclose(f); return false; }

    // --- Geometry metadata block (zstd): meshes, instances, georef, chunk TOC
    std::vector<std::uint8_t> geometry_metadata;
    appendVec(geometry_metadata, data.meshes);
    appendVec(geometry_metadata, data.instances);
    appendBytes(geometry_metadata, &data.has_coordinate_operation, 4);
    appendBytes(geometry_metadata, data.coordinate_operation_meters, sizeof(double) * 16);
    appendBytes(geometry_metadata, &data.project_length_to_meters, sizeof(double));
    appendBytes(geometry_metadata, &data.map_unit_to_meters, sizeof(double));
    appendVec(geometry_metadata, chunks);
    if (!wrBlock(geometry_metadata)) { fclose(f); return false; }

    // --- Element metadata block (zstd): elements + string table --------------
    std::vector<std::uint8_t> element_metadata;
    appendVec(element_metadata, data.elements);
    std::uint32_t stbl_len = static_cast<std::uint32_t>(data.string_table.size());
    appendBytes(element_metadata, &stbl_len, 4);
    appendBytes(element_metadata, data.string_table.data(), stbl_len);
    if (!wrBlock(element_metadata)) { fclose(f); return false; }

    fclose(f);
    return true;
}
#endif  // !__EMSCRIPTEN__

// Cursor over an in-memory (decompressed) metadata block.
namespace {
struct BufReader {
    const std::uint8_t* p;
    std::size_t n;
    std::size_t pos = 0;
    bool take(void* dst, std::size_t k) {
        if (pos + k > n) return false;
        std::memcpy(dst, p + pos, k);
        pos += k;
        return true;
    }
    template <typename T>
    bool takeVec(std::vector<T>& v) {
        std::uint32_t c = 0;
        if (!take(&c, 4)) return false;
        if (pos + std::size_t(c) * sizeof(T) > n) return false;
        v.resize(c);
        if (c) { std::memcpy(v.data(), p + pos, std::size_t(c) * sizeof(T)); pos += std::size_t(c) * sizeof(T); }
        return true;
    }
};
}  // namespace

// Full read: reconstruct the whole SidecarData (test/tooling path — the runtime
// streams via readSidecarMetadataOnly + per-chunk loads and never calls this).
// Decompresses the metadata blocks, then scatters each chunk's decompressed
// geometry back into the whole-model vertex/index arrays using the mesh offsets.
std::optional<SidecarData> readSidecar(const std::string& ifc_path) {
    std::string path = sidecarPath(ifc_path);
    FILE* f = fopen(path.c_str(), "rb");
    if (!f) return std::nullopt;
    auto fail = [&]() -> std::optional<SidecarData> { fclose(f); return std::nullopt; };

    SidecarHeader hdr;
    if (fread(&hdr, sizeof(hdr), 1, f) != 1) return fail();
    if (hdr.magic != SIDECAR_MAGIC || hdr.version != SIDECAR_VERSION ||
        hdr.endian != SIDECAR_ENDIAN) return fail();

    auto read_bytes = [&](void* data, std::size_t byte_count) {
        return fread(data, 1, byte_count, f) == byte_count;
    };
    auto rdU64 = [&](std::uint64_t& v) { return read_bytes(&v, sizeof(v)); };

    std::uint64_t geom_bytes = 0;
    if (!rdU64(geom_bytes)) return fail();
    std::vector<std::uint8_t> geom(static_cast<std::size_t>(geom_bytes));
    if (geom_bytes && !read_bytes(geom.data(), geom.size())) return fail();

    auto readBlock = [&](std::vector<std::uint8_t>& out) -> bool {
        std::uint64_t comp = 0, raw = 0;
        if (!rdU64(comp) || !rdU64(raw)) return false;
        std::vector<std::uint8_t> z(static_cast<std::size_t>(comp));
        if (comp && !read_bytes(z.data(), z.size())) return false;
        out.assign(std::size_t(raw), 0);
        return SidecarCompress::decompress(z.data(), z.size(), out.data(), out.size());
    };
    std::vector<std::uint8_t> geometry_metadata, element_metadata;
    if (!readBlock(geometry_metadata) || !readBlock(element_metadata)) return fail();
    fclose(f);

    SidecarData data;
    BufReader cr{ geometry_metadata.data(), geometry_metadata.size() };
    if (!cr.takeVec(data.meshes))    return std::nullopt;
    if (!cr.takeVec(data.instances)) return std::nullopt;
    if (!cr.take(&data.has_coordinate_operation, 4))                    return std::nullopt;
    if (!cr.take(data.coordinate_operation_meters, sizeof(double) * 16)) return std::nullopt;
    if (!cr.take(&data.project_length_to_meters, sizeof(double)))       return std::nullopt;
    if (!cr.take(&data.map_unit_to_meters, sizeof(double)))             return std::nullopt;
    if (!cr.takeVec(data.chunks))    return std::nullopt;

    BufReader dr{ element_metadata.data(), element_metadata.size() };
    if (!dr.takeVec(data.elements)) return std::nullopt;
    std::uint32_t stbl_len = 0;
    if (!dr.take(&stbl_len, 4)) return std::nullopt;
    data.string_table.resize(stbl_len);
    if (stbl_len && !dr.take(data.string_table.data(), stbl_len)) return std::nullopt;

    // Reconstruct the whole-model vertex/index arrays from the per-chunk blobs.
    std::size_t vsize = 0, isize = 0;
    for (const auto& mesh_info : data.meshes) {
        vsize = std::max<std::size_t>(vsize,
            std::size_t(mesh_info.vbo_byte_offset) +
            std::size_t(mesh_info.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES);
        isize = std::max<std::size_t>(
            isize, mesh_info.ebo_byte_offset / sizeof(std::uint32_t) + mesh_info.index_count);
        if (mesh_info.lod1_index_count) {
            isize = std::max<std::size_t>(
                isize,
                mesh_info.lod1_ebo_byte_offset / sizeof(std::uint32_t) + mesh_info.lod1_index_count);
        }
    }
    data.vertices.assign(vsize, 0);
    data.indices.assign(isize, 0);
    for (const auto& sidecar_chunk : data.chunks) {
        if (sidecar_chunk.v_comp_off + sidecar_chunk.v_comp_size > geom.size() ||
            sidecar_chunk.i_comp_off + sidecar_chunk.i_comp_size > geom.size()) return std::nullopt;
        std::vector<std::uint8_t> vraw(static_cast<std::size_t>(sidecar_chunk.v_raw_size));
        std::vector<std::uint8_t> iraw(static_cast<std::size_t>(sidecar_chunk.i_raw_size));
        if (!SidecarCompress::decompress(
                geom.data() + sidecar_chunk.v_comp_off, sidecar_chunk.v_comp_size, vraw.data(), vraw.size()) ||
            !SidecarCompress::decompress(
                geom.data() + sidecar_chunk.i_comp_off, sidecar_chunk.i_comp_size, iraw.data(), iraw.size()))
            return std::nullopt;
        const auto* iu = reinterpret_cast<const std::uint32_t*>(iraw.data());
        std::size_t vcur = 0, icur = 0;
        const std::uint32_t end = sidecar_chunk.first_mesh + sidecar_chunk.mesh_count;
        for (std::uint32_t mesh_index = sidecar_chunk.first_mesh;
             mesh_index < end && mesh_index < data.meshes.size();
             ++mesh_index) {
            const MeshInfo& mesh_info = data.meshes[mesh_index];
            const std::size_t vertex_byte_count =
                std::size_t(mesh_info.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            if (vcur + vertex_byte_count <= vraw.size() &&
                mesh_info.vbo_byte_offset + vertex_byte_count <= data.vertices.size()) {
                std::memcpy(&data.vertices[mesh_info.vbo_byte_offset], vraw.data() + vcur, vertex_byte_count);
            }
            vcur += vertex_byte_count;
        }
        for (std::uint32_t mesh_index = sidecar_chunk.first_mesh;
             mesh_index < end && mesh_index < data.meshes.size();
             ++mesh_index) {
            const MeshInfo& mesh_info = data.meshes[mesh_index];
            if (!mesh_info.index_count) continue;
            if (icur + mesh_info.index_count <= iraw.size() / 4) {
                std::memcpy(&data.indices[mesh_info.ebo_byte_offset / sizeof(std::uint32_t)],
                            iu + icur,
                            mesh_info.index_count * 4);
            }
            icur += mesh_info.index_count;
        }
        for (std::uint32_t mesh_index = sidecar_chunk.first_mesh;
             mesh_index < end && mesh_index < data.meshes.size();
             ++mesh_index) {
            const MeshInfo& mesh_info = data.meshes[mesh_index];
            if (!mesh_info.lod1_index_count) continue;
            if (icur + mesh_info.lod1_index_count <= iraw.size() / 4) {
                std::memcpy(&data.indices[mesh_info.lod1_ebo_byte_offset / sizeof(std::uint32_t)],
                            iu + icur,
                            mesh_info.lod1_index_count * 4);
            }
            icur += mesh_info.lod1_index_count;
        }
    }
    return data;
}
