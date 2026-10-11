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

#ifndef IFCVIEWREADER_H
#define IFCVIEWREADER_H

// Loading a .ifcview (format in IfcViewFormat.h).  Two kinds of entry point:
//
//   * File readers for the desktop (readIfcViewMetadata, then
//     readChunkGeometryCompressed per chunk), which open the file with stdio.
//   * Pure, buffer-based parsers (parseIfcViewHead / GeometryMetadata /
//     ElementMetadata, planIfcViewReadRanges) that both the desktop readers
//     and the web loader (Blob.slice / fetch Range) feed with bytes they
//     sliced themselves, so the wire-format knowledge lives in one place and
//     is unit-testable without touching a file.
//
// Compiled on every platform.  The web build links a decompress-only zstd, so
// nothing here compresses; that is IfcViewWriter's job.

#include "IfcViewFormat.h"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <utility>
#include <vector>

// Decompress a zstd frame in [src, src+src_size) into dst, which must have room
// for exactly raw_size bytes. Returns false on any zstd error or if the frame
// doesn't expand to exactly raw_size.
bool decompressIfcViewFrame(const std::uint8_t* src, std::size_t src_size,
                            std::uint8_t* dst, std::size_t raw_size);

// Metadata-only .ifcview load — the foundation for streaming.  Reads the header,
// mesh dict, instance dict, georef, chunk TOC and element table but skips the
// geometry section, leaving the locators needed for later per-chunk reads.
// On a typical real-scene .ifcview this returns in milliseconds while the
// geometry is hundreds of MB, so the renderer can set up cull / instance state
// immediately and load chunks on demand as they become frustum-visible.
struct StreamingIfcView {
    // Everything except vertices + indices — same shape as IfcViewData but
    // with empty vertices / indices vectors. The renderer uses meshes /
    // instances / georef / chunks immediately (elements/strings are element metadata).
    IfcViewData meta;

    // The compressed geometry section starts here. Each chunk's two zstd
    // blobs live at geometry_section_offset + IfcViewChunk.{v_comp_off,i_comp_off};
    // a per-chunk load fetches [that, +*_comp_size) and decompresses to *_raw_size.
    uint64_t geometry_section_offset = 0;

    // Element metadata block locator: a single zstd frame at
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
// version error. The file is closed before return — callers re-open for
// per-chunk reads.
std::optional<StreamingIfcView> readIfcViewMetadata(const std::string& ifc_path);

// Read + decompress one chunk's geometry from disk: the vertex zstd frame at
// [geometry_section_offset + v_comp_off, +v_comp_size) → out_vbytes (v_raw
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

// Parse the IFCVIEW_HEAD_BYTES-byte head. Validates magic / version / endian
// and, on success, writes the compressed-geometry-section byte length (the
// metadata blocks follow at IFCVIEW_HEAD_BYTES + out_geom_bytes). Returns false
// if `n` is short or the header is wrong. `data` must point at the start of
// the file.
bool parseIfcViewHead(const std::uint8_t* data, std::size_t n,
                      std::uint64_t& out_geom_bytes);

// Parse the decompressed geometry metadata block (mesh dict, instance dict,
// georef, chunk TOC) — everything needed to set up + draw the scene. `data`
// points at the first byte of the block; `n` is its raw length. Returns false
// on any bounds overrun, leaving out_meta partially filled.
bool parseIfcViewGeometryMetadata(const std::uint8_t* data, std::size_t n,
                                  IfcViewData& out_meta);

// Parse the decompressed element metadata block (element table + string table
// — used for UI/picking, never for rendering). Fetched on demand. `data`
// points at the first byte of the block; `n` is its raw length.
bool parseIfcViewElementMetadata(const std::uint8_t* data, std::size_t n,
                                 IfcViewData& out_meta);

// Parse a count-prefixed run of instance records from
// [cursor, cursor + remaining), advancing both, and expand them into
// InstanceInfo with transform and world AABB derived from `meshes` under
// identity stage matrices.  False when the data is truncated.
bool readInstanceInfos(const uint8_t*& cursor, std::size_t& remaining,
                       const std::vector<MeshInfo>& meshes,
                       std::vector<InstanceInfo>& out);

// A coalesced read plan: a single contiguous source read whose bytes are
// scattered into the destination at the recorded offsets. Merging adjacent
// (or near-adjacent, within max_gap_bytes) ranges into one read amortises seek
// cost on disk and request count over the network / Blob boundary.
struct IfcViewReadPlan {
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
std::vector<IfcViewReadPlan> planIfcViewReadRanges(
        std::uint64_t section_offset,
        const std::vector<std::pair<std::uint64_t, std::uint64_t>>& ranges,
        std::uint64_t max_gap_bytes);

#endif // IFCVIEWREADER_H
