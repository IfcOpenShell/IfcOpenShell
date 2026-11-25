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

#include "IfcViewWriter.h"

#include <zstd.h>

#include <algorithm>
#include <atomic>
#include <cstdio>
#include <cstring>
#include <thread>

namespace {

// zstd level for baking. 19 is near-max ratio; decode speed is level-
// independent and the bake is offline, so favour ratio.
constexpr int kIfcViewZstdLevel = 19;

// --- In-memory serialisation (a block is built in RAM, then compressed) ------
template<typename T>
void appendVec(std::vector<std::uint8_t>& buffer, const std::vector<T>& values) {
    std::uint32_t count = static_cast<std::uint32_t>(values.size());
    const auto* count_bytes = reinterpret_cast<const std::uint8_t*>(&count);
    buffer.insert(buffer.end(), count_bytes, count_bytes + 4);
    if (count > 0) {
        const auto* value_bytes = reinterpret_cast<const std::uint8_t*>(values.data());
        buffer.insert(buffer.end(), value_bytes, value_bytes + std::size_t(sizeof(T)) * count);
    }
}
void appendBytes(std::vector<std::uint8_t>& buffer, const void* data, std::size_t byte_count) {
    const auto* bytes = static_cast<const std::uint8_t*>(data);
    buffer.insert(buffer.end(), bytes, bytes + byte_count);
}

// Pull one chunk's geometry out of the whole-model vertex/index arrays into the
// chunk-LOCAL layout applyStreamedChunk expects: vertices of its meshes in chunk
// order, then indices as LOD0 (per mesh) followed by LOD1 (per mesh).
void extractChunkGeometry(const IfcViewData& ifcview_data, const IfcViewChunk& ifcview_chunk,
                          std::vector<std::uint8_t>& vbytes,
                          std::vector<std::uint8_t>& ibytes) {
    vbytes.clear();
    ibytes.clear();
    const std::uint32_t end = ifcview_chunk.first_mesh + ifcview_chunk.mesh_count;
    for (std::uint32_t mesh_index = ifcview_chunk.first_mesh;
         mesh_index < end && mesh_index < ifcview_data.meshes.size();
         ++mesh_index) {
        const MeshInfo& mesh_info = ifcview_data.meshes[mesh_index];
        const std::size_t vertex_offset = mesh_info.vbo_byte_offset;
        const std::size_t vertex_byte_count =
            std::size_t(mesh_info.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        if (vertex_offset + vertex_byte_count <= ifcview_data.vertices.size())
            vbytes.insert(vbytes.end(), ifcview_data.vertices.begin() + vertex_offset,
                          ifcview_data.vertices.begin() + vertex_offset + vertex_byte_count);
    }
    auto appendIdx = [&](std::size_t first_u32, std::size_t count) {
        if (first_u32 + count > ifcview_data.indices.size()) return;
        const auto* index_bytes =
            reinterpret_cast<const std::uint8_t*>(ifcview_data.indices.data() + first_u32);
        ibytes.insert(ibytes.end(), index_bytes, index_bytes + count * sizeof(std::uint32_t));
    };
    for (std::uint32_t mesh_index = ifcview_chunk.first_mesh;
         mesh_index < end && mesh_index < ifcview_data.meshes.size();
         ++mesh_index) {
        const MeshInfo& mesh_info = ifcview_data.meshes[mesh_index];
        if (mesh_info.index_count) {
            appendIdx(mesh_info.ebo_byte_offset / sizeof(std::uint32_t), mesh_info.index_count);
        }
    }
    for (std::uint32_t mesh_index = ifcview_chunk.first_mesh;
         mesh_index < end && mesh_index < ifcview_data.meshes.size();
         ++mesh_index) {
        const MeshInfo& mesh_info = ifcview_data.meshes[mesh_index];
        if (mesh_info.lod1_index_count) {
            appendIdx(mesh_info.lod1_ebo_byte_offset / sizeof(std::uint32_t), mesh_info.lod1_index_count);
        }
    }
}

void appendInstanceInfos(std::vector<std::uint8_t>& buffer,
                         const std::vector<InstanceInfo>& instances) {
    const std::uint32_t count = static_cast<std::uint32_t>(instances.size());
    appendBytes(buffer, &count, 4);
    buffer.reserve(buffer.size() + instances.size() * IFCVIEW_INSTANCE_RECORD_BYTES);
    for (const InstanceInfo& inst : instances) {
        const double* p = inst.placement_transformation;  // column-major
        const double translation[3] = { p[12], p[13], p[14] };
        const float linear[9] = {
            float(p[0]), float(p[1]), float(p[2]),
            float(p[4]), float(p[5]), float(p[6]),
            float(p[8]), float(p[9]), float(p[10]),
        };
        appendBytes(buffer, &inst.mesh_id, 4);
        appendBytes(buffer, &inst.object_id, 4);
        appendBytes(buffer, translation, sizeof(translation));
        appendBytes(buffer, linear, sizeof(linear));
    }
}

}  // namespace

std::vector<std::uint8_t> compressIfcViewFrame(const std::uint8_t* src, std::size_t n,
                                               int level) {
    if (n == 0) return {};
    std::vector<std::uint8_t> out(ZSTD_compressBound(n));
    const size_t got = ZSTD_compress(out.data(), out.size(), src, n, level);
    if (ZSTD_isError(got)) return {};
    out.resize(got);
    return out;
}

bool writeIfcView(const std::string& ifc_path, const IfcViewData& data) {
    std::string path = ifcViewPathFor(ifc_path);
    FILE* f = fopen(path.c_str(), "wb");
    if (!f) return false;

    auto write_bytes = [&](const void* data, std::size_t byte_count) {
        return fwrite(data, 1, byte_count, f) == byte_count;
    };
    auto wrU64 = [&](std::uint64_t v) { return write_bytes(&v, sizeof(v)); };
    auto wrBlock = [&](const std::vector<std::uint8_t>& raw) -> bool {
        auto z = compressIfcViewFrame(raw.data(), raw.size(), kIfcViewZstdLevel);
        if (raw.size() > 0 && z.empty()) return false;  // compress failed
        return wrU64(z.size()) && wrU64(raw.size()) && (z.empty() || write_bytes(z.data(), z.size()));
    };

    IfcViewHeader hdr = { IFCVIEW_MAGIC, IFCVIEW_VERSION, IFCVIEW_ENDIAN };
    if (!write_bytes(&hdr, sizeof(hdr))) { fclose(f); return false; }

    // --- Geometry section: per-chunk zstd(vertex) + zstd(index) frames -------
    // Offsets in the chunk TOC are relative to the geometry section start, so
    // the loader range-fetches exactly one chunk without reading anything else.
    const long geom_len_pos = ftell(f);
    if (!wrU64(0)) { fclose(f); return false; }  // geom_bytes placeholder
    const long geom_start = ftell(f);

    std::vector<IfcViewChunk> chunks = data.chunks;  // fill blob offsets below

    // Compress every chunk's geometry in parallel — zstd is the bulk of the bake
    // cost — then write the frames serially so their offsets stay contiguous.
    struct ChunkBlob {
        std::vector<std::uint8_t> vz, iz;
        std::size_t v_raw = 0, i_raw = 0;
    };
    std::vector<ChunkBlob> blobs(chunks.size());
    std::atomic<bool> compress_ok{true};
    {
        const unsigned hw = std::max(1u, std::thread::hardware_concurrency());
        const std::size_t worker_count =
            std::min<std::size_t>(hw, std::max<std::size_t>(std::size_t(1), chunks.size()));
        std::atomic<std::size_t> next{0};
        auto worker = [&]() {
            std::vector<std::uint8_t> vraw, iraw;
            for (std::size_t idx = next.fetch_add(1); idx < chunks.size();
                 idx = next.fetch_add(1)) {
                extractChunkGeometry(data, chunks[idx], vraw, iraw);
                blobs[idx].v_raw = vraw.size();
                blobs[idx].i_raw = iraw.size();
                blobs[idx].vz = compressIfcViewFrame(vraw.data(), vraw.size(), kIfcViewZstdLevel);
                blobs[idx].iz = compressIfcViewFrame(iraw.data(), iraw.size(), kIfcViewZstdLevel);
                if ((vraw.size() && blobs[idx].vz.empty()) ||
                    (iraw.size() && blobs[idx].iz.empty())) {
                    compress_ok.store(false, std::memory_order_relaxed);
                }
            }
        };
        std::vector<std::thread> pool;
        pool.reserve(worker_count > 0 ? worker_count - 1 : 0);
        for (std::size_t i = 1; i < worker_count; ++i) pool.emplace_back(worker);
        worker();  // the calling thread participates too
        for (auto& th : pool) th.join();
    }
    if (!compress_ok.load()) { fclose(f); return false; }

    for (std::size_t idx = 0; idx < chunks.size(); ++idx) {
        auto& ifcview_chunk = chunks[idx];
        const ChunkBlob& blob = blobs[idx];
        ifcview_chunk.v_comp_off  = std::uint64_t(ftell(f) - geom_start);
        ifcview_chunk.v_comp_size = blob.vz.size();
        ifcview_chunk.v_raw_size  = blob.v_raw;
        if (!blob.vz.empty() && !write_bytes(blob.vz.data(), blob.vz.size())) { fclose(f); return false; }
        ifcview_chunk.i_comp_off  = std::uint64_t(ftell(f) - geom_start);
        ifcview_chunk.i_comp_size = blob.iz.size();
        ifcview_chunk.i_raw_size  = blob.i_raw;
        if (!blob.iz.empty() && !write_bytes(blob.iz.data(), blob.iz.size())) { fclose(f); return false; }
    }
    const long geom_end = ftell(f);
    if (geom_start < 0 || geom_end < 0) { fclose(f); return false; }
    if (fseek(f, geom_len_pos, SEEK_SET) != 0) { fclose(f); return false; }
    if (!wrU64(std::uint64_t(geom_end - geom_start))) { fclose(f); return false; }
    if (fseek(f, geom_end, SEEK_SET) != 0) { fclose(f); return false; }

    // --- Geometry metadata block (zstd): meshes, instances, georef, chunk TOC
    std::vector<std::uint8_t> geometry_metadata;
    appendVec(geometry_metadata, data.meshes);
    appendInstanceInfos(geometry_metadata, data.instances);
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
