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

#ifndef WGPUSTREAMINGLOADER_H
#define WGPUSTREAMINGLOADER_H

#include "SidecarCache.h"

#include <cstdint>
#include <optional>
#include <string>
#include <vector>

// Metadata-only sidecar load — the foundation for streaming. Reads the v13
// header + mesh dict + instance dict + georef + element table from disk but
// *skips* the bulky vertex and index byte sections, leaving file offsets +
// sizes for later random-access reads.
//
// On a typical real-scene sidecar this returns in milliseconds even when the
// full readSidecar would block on hundreds of MB of vertex bytes. Lets the
// renderer set up cull / instance state immediately and load vertex chunks
// on demand as they become frustum-visible.
//
// Backwards-compatible with v13 sidecars on disk (the format isn't changing
// in this step — we're just reading less of it). v14 with an explicit
// per-chunk TOC arrives in a follow-up; this layer abstracts the chunk
// boundaries so the upgrade is internal.
struct StreamingSidecar {
    // Everything except vertices + indices — same shape as SidecarData but
    // with empty vertices / indices vectors. The renderer uses meshes /
    // instances / georef / elements immediately.
    SidecarData meta;

    // Byte offsets in the on-disk file where the vertex and index sections
    // start (after their 4-byte count headers). Pair with vertex_total_bytes
    // / index_total_bytes for the section length; per-chunk reads slice
    // arbitrary ranges within these.
    uint64_t vertex_section_offset = 0;
    uint64_t vertex_total_bytes    = 0;
    uint64_t index_section_offset  = 0;
    uint64_t index_total_count     = 0;  // u32 indices, NOT bytes

    // Resolved on-disk path so subsequent chunk reads can re-open / seek.
    std::string file_path;
};

// Read just the metadata + section offsets. Returns nullopt on any I/O or
// version error (same failure modes as readSidecar). The file is closed
// before return — callers re-open for per-chunk reads.
std::optional<StreamingSidecar> readSidecarMetadataOnly(const std::string& ifc_path);

// Read a byte range from a sidecar's vertex section. `chunk_byte_offset` is
// RELATIVE to vertex_section_offset (i.e. 0 = first vertex byte). Returns
// false on I/O error or out-of-range request.
//
// Synchronous; intended to be called from a worker thread for async
// streaming or from the main thread for stage-1 on-demand load.
bool readSidecarVertexChunk(const std::string& ifc_path,
                            uint64_t vertex_section_offset,
                            uint64_t chunk_byte_offset,
                            uint64_t chunk_byte_size,
                            std::vector<uint8_t>& out_bytes);

// Read a u32-index range. `chunk_first_index` is RELATIVE to the start of
// the index section (i.e. 0 = first u32 index). `chunk_index_count` is in
// indices (multiply by 4 internally).
bool readSidecarIndexChunk(const std::string& ifc_path,
                           uint64_t index_section_offset,
                           uint64_t chunk_first_index,
                           uint64_t chunk_index_count,
                           std::vector<uint32_t>& out_indices);

#endif // WGPUSTREAMINGLOADER_H
