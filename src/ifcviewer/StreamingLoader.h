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

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <utility>
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
    // instances / georef / chunks immediately (elements/strings are element metadata).
    SidecarData meta;

    // v16: the compressed geometry section starts here. Each chunk's two zstd
    // blobs live at geometry_section_offset + SidecarChunk.{v_comp_off,i_comp_off};
    // a per-chunk load fetches [that, +*_comp_size) and decompresses to *_raw_size.
    uint64_t geometry_section_offset = 0;

    // v16 element metadata block locator: a single zstd frame at
    // element_metadata_comp_offset of element_metadata_comp_size bytes →
    // element_metadata_raw_size. The web loader fetches it on demand
    // (elements/strings); desktop reads it up front.
    uint64_t element_metadata_comp_offset = 0;
    uint64_t element_metadata_comp_size   = 0;
    uint64_t element_metadata_raw_size    = 0;

    // Resolved on-disk path so subsequent chunk reads can re-open / seek.
    std::string file_path;
};

// Read just the metadata + section offsets. Returns nullopt on any I/O or
// version error (same failure modes as readSidecar). The file is closed
// before return — callers re-open for per-chunk reads.
std::optional<StreamingSidecar> readSidecarMetadata(const std::string& ifc_path);

// Read + decompress one chunk's geometry (v16) from disk: the vertex zstd frame
// at [geometry_section_offset + v_comp_off, +v_comp_size) → out_vbytes (v_raw
// bytes) and the index frame → out_idx (i_raw/4 u32s). Returns false on I/O or
// decompress failure. Used by the desktop StreamingThread worker + the sync
// first-frame fallback; the web path decompresses in beginWebChunkLoad instead.
bool readChunkGeometryCompressed(const std::string& ifc_path,
                                 std::uint64_t geometry_section_offset,
                                 std::uint64_t v_comp_off, std::uint64_t v_comp_size,
                                 std::uint64_t v_raw_size,
                                 std::uint64_t i_comp_off, std::uint64_t i_comp_size,
                                 std::uint64_t i_raw_size,
                                 std::vector<std::uint8_t>&  out_vbytes,
                                 std::vector<std::uint32_t>& out_idx);

// --- Pure, buffer-based building blocks ------------------------------------
//
// The metadata lives in two disjoint regions of the file: a small fixed
// "head" (12-byte header + the 4-byte vertex-byte count) that precedes the
// bulk vertex/index sections, and a "tail" (mesh dict, instance dict, georef,
// element table, string table) that follows them. Both desktop (FILE*) and
// web (Blob.slice / fetch Range) readers slice those two regions out of the
// source and hand the bytes to these parsers, so the wire-format knowledge
// lives in exactly one place and is unit-testable without touching a file.

// Bytes the head spans: SidecarHeader (12) + uint64 geometry-section length (8).
inline constexpr std::size_t SIDECAR_HEAD_BYTES = 20;

// Parse the 20-byte head (v16). Validates magic / version / endian and, on
// success, writes the compressed-geometry-section byte length (the metadata
// blocks follow at SIDECAR_HEAD_BYTES + out_geom_bytes). Returns false if `n`
// is short or the header is wrong. `data` must point at the start of the file.
bool parseSidecarHead(const std::uint8_t* data, std::size_t n,
                      std::uint64_t& out_geom_bytes);

// Parse the v15 geometry metadata block (mesh dict, instance dict,
// georef, chunk TOC) — everything needed to set up + draw the scene. `data`
// points at the first geometry metadata byte; `n` is geometry_metadata_bytes. Returns false
// on any bounds overrun, leaving out_meta partially filled.
bool parseSidecarGeometryMetadata(const std::uint8_t* data, std::size_t n,
                                  SidecarData& out_meta);

// Parse the v15 element metadata block (element table + string table — the
// IFC property tree, used for UI/picking, never for rendering). Fetched on
// demand. `data` points at the first element metadata byte; `n` is its length.
bool parseSidecarElementMetadata(const std::uint8_t* data, std::size_t n,
                                 SidecarData& out_meta);

// A coalesced read plan: a single contiguous source read whose bytes are
// scattered into the destination at the recorded offsets. Merging adjacent
// (or near-adjacent, within max_gap_bytes) ranges into one read amortises seek
// cost on disk and request count over the network / Blob boundary.
struct SidecarReadPlan {
    std::uint64_t file_offset;   // absolute source offset of this read
    std::uint64_t read_size;     // bytes to read
    struct Slice {
        std::uint64_t src_offset;   // offset within the read buffer
        std::uint64_t dst_offset;   // offset within the destination buffer
        std::uint64_t bytes;
    };
    std::vector<Slice> slices;
};

// Build read plans for `ranges` (section-relative (offset, size) pairs) that
// land in a destination laid out in input order. `section_offset` is added to
// turn section-relative offsets into absolute source offsets. Pure — no I/O.
std::vector<SidecarReadPlan> planSidecarReadRanges(
        std::uint64_t section_offset,
        const std::vector<std::pair<std::uint64_t, std::uint64_t>>& ranges,
        std::uint64_t max_gap_bytes);

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

// Multi-range vertex read. `ranges` is a list of (section-relative
// byte_offset, byte_size) tuples; their contents are concatenated into
// out_bytes in input order. Single fopen across all ranges, so it's
// far cheaper than calling readSidecarVertexChunk N times when a
// spatially-grouped chunk needs to scatter-gather meshes that aren't
// adjacent in the sidecar. out_bytes is resized to the total size.
bool readSidecarVertexRanges(const std::string& ifc_path,
                             uint64_t vertex_section_offset,
                             const std::vector<std::pair<uint64_t, uint64_t>>& ranges,
                             std::vector<uint8_t>& out_bytes);

// Same for the index section. Ranges are (first_u32, count_u32);
// concatenated into out_indices in input order.
bool readSidecarIndexRanges(const std::string& ifc_path,
                            uint64_t index_section_offset,
                            const std::vector<std::pair<uint64_t, uint64_t>>& ranges,
                            std::vector<uint32_t>& out_indices);

#endif // WGPUSTREAMINGLOADER_H
