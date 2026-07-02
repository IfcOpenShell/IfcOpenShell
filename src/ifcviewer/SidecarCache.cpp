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
static void appendVec(std::vector<std::uint8_t>& b, const std::vector<T>& v) {
    std::uint32_t n = static_cast<std::uint32_t>(v.size());
    const auto* np = reinterpret_cast<const std::uint8_t*>(&n);
    b.insert(b.end(), np, np + 4);
    if (n > 0) {
        const auto* p = reinterpret_cast<const std::uint8_t*>(v.data());
        b.insert(b.end(), p, p + std::size_t(sizeof(T)) * n);
    }
}
static void appendBytes(std::vector<std::uint8_t>& b, const void* p, std::size_t n) {
    const auto* c = static_cast<const std::uint8_t*>(p);
    b.insert(b.end(), c, c + n);
}

// Pull one chunk's geometry out of the whole-model vertex/index arrays into the
// chunk-LOCAL layout applyStreamedChunk expects: vertices of its meshes in chunk
// order, then indices as LOD0 (per mesh) followed by LOD1 (per mesh).
static void extractChunkGeometry(const SidecarData& d, const SidecarChunk& c,
                                 std::vector<std::uint8_t>& vbytes,
                                 std::vector<std::uint8_t>& ibytes) {
    vbytes.clear();
    ibytes.clear();
    const std::uint32_t end = c.first_mesh + c.mesh_count;
    for (std::uint32_t mi = c.first_mesh; mi < end && mi < d.meshes.size(); ++mi) {
        const MeshInfo& m = d.meshes[mi];
        const std::size_t voff = m.vbo_byte_offset;
        const std::size_t vn = std::size_t(m.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        if (voff + vn <= d.vertices.size())
            vbytes.insert(vbytes.end(), d.vertices.begin() + voff,
                          d.vertices.begin() + voff + vn);
    }
    auto appendIdx = [&](std::size_t first_u32, std::size_t count) {
        if (first_u32 + count > d.indices.size()) return;
        const auto* p = reinterpret_cast<const std::uint8_t*>(d.indices.data() + first_u32);
        ibytes.insert(ibytes.end(), p, p + count * sizeof(std::uint32_t));
    };
    for (std::uint32_t mi = c.first_mesh; mi < end && mi < d.meshes.size(); ++mi) {
        const MeshInfo& m = d.meshes[mi];
        if (m.index_count) appendIdx(m.ebo_byte_offset / sizeof(std::uint32_t), m.index_count);
    }
    for (std::uint32_t mi = c.first_mesh; mi < end && mi < d.meshes.size(); ++mi) {
        const MeshInfo& m = d.meshes[mi];
        if (m.lod1_index_count)
            appendIdx(m.lod1_ebo_byte_offset / sizeof(std::uint32_t), m.lod1_index_count);
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

#if !defined(__EMSCRIPTEN__)  // bake path — compresses, desktop only
bool writeSidecar(const std::string& ifc_path, const SidecarData& data) {
    std::string path = sidecarPath(ifc_path);
    FILE* f = fopen(path.c_str(), "wb");
    if (!f) return false;

    auto wr = [&](const void* p, std::size_t n) {
        return fwrite(p, 1, n, f) == n;
    };
    auto wrU64 = [&](std::uint64_t v) { return wr(&v, sizeof(v)); };
    auto wrBlock = [&](const std::vector<std::uint8_t>& raw) -> bool {
        auto z = SidecarCompress::compress(raw.data(), raw.size(), kSidecarZstdLevel);
        if (raw.size() > 0 && z.empty()) return false;  // compress failed
        return wrU64(z.size()) && wrU64(raw.size()) && (z.empty() || wr(z.data(), z.size()));
    };

    SidecarHeader hdr = { SIDECAR_MAGIC, SIDECAR_VERSION, SIDECAR_ENDIAN };
    if (!wr(&hdr, sizeof(hdr))) { fclose(f); return false; }

    // --- Geometry section: per-chunk zstd(vertex) + zstd(index) frames -------
    // Offsets in the chunk TOC are relative to the geometry section start, so
    // the loader range-fetches exactly one chunk without reading anything else.
    const long geom_len_pos = ftell(f);
    if (!wrU64(0)) { fclose(f); return false; }  // geom_bytes placeholder
    const long geom_start = ftell(f);

    std::vector<SidecarChunk> chunks = data.chunks;  // fill blob offsets below
    std::vector<std::uint8_t> vraw, iraw;
    for (auto& c : chunks) {
        extractChunkGeometry(data, c, vraw, iraw);
        auto vz = SidecarCompress::compress(vraw.data(), vraw.size(), kSidecarZstdLevel);
        auto iz = SidecarCompress::compress(iraw.data(), iraw.size(), kSidecarZstdLevel);
        if ((vraw.size() && vz.empty()) || (iraw.size() && iz.empty())) { fclose(f); return false; }
        c.v_comp_off  = std::uint64_t(ftell(f) - geom_start);
        c.v_comp_size = vz.size();
        c.v_raw_size  = vraw.size();
        if (!vz.empty() && !wr(vz.data(), vz.size())) { fclose(f); return false; }
        c.i_comp_off  = std::uint64_t(ftell(f) - geom_start);
        c.i_comp_size = iz.size();
        c.i_raw_size  = iraw.size();
        if (!iz.empty() && !wr(iz.data(), iz.size())) { fclose(f); return false; }
    }
    const long geom_end = ftell(f);
    if (geom_start < 0 || geom_end < 0) { fclose(f); return false; }
    if (fseek(f, geom_len_pos, SEEK_SET) != 0) { fclose(f); return false; }
    if (!wrU64(std::uint64_t(geom_end - geom_start))) { fclose(f); return false; }
    if (fseek(f, geom_end, SEEK_SET) != 0) { fclose(f); return false; }

    // --- Critical metadata block (zstd): meshes, instances, georef, chunk TOC
    std::vector<std::uint8_t> crit;
    appendVec(crit, data.meshes);
    appendVec(crit, data.instances);
    appendBytes(crit, &data.has_coordinate_operation, 4);
    appendBytes(crit, data.coordinate_operation_meters, sizeof(double) * 16);
    appendBytes(crit, &data.project_length_to_meters, sizeof(double));
    appendBytes(crit, &data.map_unit_to_meters, sizeof(double));
    appendVec(crit, chunks);
    if (!wrBlock(crit)) { fclose(f); return false; }

    // --- Deferred metadata block (zstd): element tree + string table ---------
    std::vector<std::uint8_t> def;
    appendVec(def, data.elements);
    std::uint32_t stbl_len = static_cast<std::uint32_t>(data.string_table.size());
    appendBytes(def, &stbl_len, 4);
    appendBytes(def, data.string_table.data(), stbl_len);
    if (!wrBlock(def)) { fclose(f); return false; }

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

    auto rd = [&](void* p, std::size_t k) { return fread(p, 1, k, f) == k; };
    auto rdU64 = [&](std::uint64_t& v) { return rd(&v, sizeof(v)); };

    std::uint64_t geom_bytes = 0;
    if (!rdU64(geom_bytes)) return fail();
    std::vector<std::uint8_t> geom(static_cast<std::size_t>(geom_bytes));
    if (geom_bytes && !rd(geom.data(), geom.size())) return fail();

    auto readBlock = [&](std::vector<std::uint8_t>& out) -> bool {
        std::uint64_t comp = 0, raw = 0;
        if (!rdU64(comp) || !rdU64(raw)) return false;
        std::vector<std::uint8_t> z(static_cast<std::size_t>(comp));
        if (comp && !rd(z.data(), z.size())) return false;
        out.assign(std::size_t(raw), 0);
        return SidecarCompress::decompress(z.data(), z.size(), out.data(), out.size());
    };
    std::vector<std::uint8_t> crit, def;
    if (!readBlock(crit) || !readBlock(def)) return fail();
    fclose(f);

    SidecarData data;
    BufReader cr{ crit.data(), crit.size() };
    if (!cr.takeVec(data.meshes))    return std::nullopt;
    if (!cr.takeVec(data.instances)) return std::nullopt;
    if (!cr.take(&data.has_coordinate_operation, 4))                    return std::nullopt;
    if (!cr.take(data.coordinate_operation_meters, sizeof(double) * 16)) return std::nullopt;
    if (!cr.take(&data.project_length_to_meters, sizeof(double)))       return std::nullopt;
    if (!cr.take(&data.map_unit_to_meters, sizeof(double)))             return std::nullopt;
    if (!cr.takeVec(data.chunks))    return std::nullopt;

    BufReader dr{ def.data(), def.size() };
    if (!dr.takeVec(data.elements)) return std::nullopt;
    std::uint32_t stbl_len = 0;
    if (!dr.take(&stbl_len, 4)) return std::nullopt;
    data.string_table.resize(stbl_len);
    if (stbl_len && !dr.take(data.string_table.data(), stbl_len)) return std::nullopt;

    // Reconstruct the whole-model vertex/index arrays from the per-chunk blobs.
    std::size_t vsize = 0, isize = 0;
    for (const auto& m : data.meshes) {
        vsize = std::max<std::size_t>(vsize,
            std::size_t(m.vbo_byte_offset) + std::size_t(m.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES);
        isize = std::max<std::size_t>(isize, m.ebo_byte_offset / sizeof(std::uint32_t) + m.index_count);
        if (m.lod1_index_count)
            isize = std::max<std::size_t>(isize, m.lod1_ebo_byte_offset / sizeof(std::uint32_t) + m.lod1_index_count);
    }
    data.vertices.assign(vsize, 0);
    data.indices.assign(isize, 0);
    for (const auto& c : data.chunks) {
        if (c.v_comp_off + c.v_comp_size > geom.size() ||
            c.i_comp_off + c.i_comp_size > geom.size()) return std::nullopt;
        std::vector<std::uint8_t> vraw(static_cast<std::size_t>(c.v_raw_size));
        std::vector<std::uint8_t> iraw(static_cast<std::size_t>(c.i_raw_size));
        if (!SidecarCompress::decompress(geom.data() + c.v_comp_off, c.v_comp_size, vraw.data(), vraw.size()) ||
            !SidecarCompress::decompress(geom.data() + c.i_comp_off, c.i_comp_size, iraw.data(), iraw.size()))
            return std::nullopt;
        const auto* iu = reinterpret_cast<const std::uint32_t*>(iraw.data());
        std::size_t vcur = 0, icur = 0;
        const std::uint32_t end = c.first_mesh + c.mesh_count;
        for (std::uint32_t mi = c.first_mesh; mi < end && mi < data.meshes.size(); ++mi) {
            const MeshInfo& m = data.meshes[mi];
            const std::size_t vn = std::size_t(m.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            if (vcur + vn <= vraw.size() && m.vbo_byte_offset + vn <= data.vertices.size())
                std::memcpy(&data.vertices[m.vbo_byte_offset], vraw.data() + vcur, vn);
            vcur += vn;
        }
        for (std::uint32_t mi = c.first_mesh; mi < end && mi < data.meshes.size(); ++mi) {
            const MeshInfo& m = data.meshes[mi];
            if (!m.index_count) continue;
            if (icur + m.index_count <= iraw.size() / 4)
                std::memcpy(&data.indices[m.ebo_byte_offset / sizeof(std::uint32_t)], iu + icur, m.index_count * 4);
            icur += m.index_count;
        }
        for (std::uint32_t mi = c.first_mesh; mi < end && mi < data.meshes.size(); ++mi) {
            const MeshInfo& m = data.meshes[mi];
            if (!m.lod1_index_count) continue;
            if (icur + m.lod1_index_count <= iraw.size() / 4)
                std::memcpy(&data.indices[m.lod1_ebo_byte_offset / sizeof(std::uint32_t)], iu + icur, m.lod1_index_count * 4);
            icur += m.lod1_index_count;
        }
    }
    return data;
}
