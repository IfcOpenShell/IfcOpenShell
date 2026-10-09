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

// NOTE: Sidecar format v3 is being rewritten to v4 (instanced geometry layout).
// During the instancing rewrite (Commit A) the cache is a no-op: reads always
// miss and writes always succeed without producing a file. Commit B will
// re-introduce the on-disk format with MeshInfo + InstanceGpu sections.

#ifndef SIDECARCACHE_H
#define SIDECARCACHE_H

#include "InstancedGeometry.h"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <vector>
#include <memory>

static constexpr uint32_t SIDECAR_MAGIC   = 0x49465657;  // "IFVW"
// v5 = MeshInfo extended with lod1_ebo_byte_offset + lod1_index_count (56 B).
//      sd.indices may contain an appended LOD1 index slice for each mesh
//      where meshoptimizer decimation produced useful output.
// v6 = VBO vertices quantized to 16 B/vertex (pos u16x3 + normal oct i16x2 +
//      color u8x4).  Dequant basis is per-mesh MeshInfo.local_aabb_min/max.
// v7 = VBO vertices shrunk to 12 B/vertex (normal oct i8x2 replaces i16x2,
//      eliminating 2-byte pad + saving 2 bytes on normal).
// v8 = source_file_size field dropped from header.  Sidecar is keyed purely
//      on path stem (foo.ifc and foo.ifcdb/ both map to foo.ifcview) so the
//      same cache serves either source format.  Staleness is user-managed
//      (delete the sidecar to force a rebuild).
// v9 = unused `reserved` field dropped from header (16 B -> 12 B).
// v10 = InstanceInfo gains placement_transformation[16] alongside transform[16]
//       — record grew from 104 B to 168 B.  placement_transformation is the
//       raw streamer output; transform is the composed FederatedFalseOrigin ·
//       ModelTransformation · CoordinateOperation · placement_transformation
//       result.  Sidecar serialises both; on load the transform is recomputed
//       from placement_transformation + the ViewportWindow's current stage
//       matrices, so v10 sidecars are reusable across .ifcfeds.
// v11 = SidecarData gains a per-model CoordinateOperation cache:
//       coordinate_operation_meters[16] (column-major), unit scales, and a
//       has_coordinate_operation flag.  Lets sidecar-loaded models apply
//       georef without re-parsing the IFC source.  Edits to the IFC's
//       IfcMapConversion do NOT invalidate the sidecar — delete the
//       .ifcview manually if you change the source's georef parameters.
// v12 = InstanceInfo::placement_transformation is double[16], and
//       StreamedInstance carries the streamer placement as double[16].  This keeps
//       large IFC placements exact until CoordinateOperation / FederatedFalseOrigin
//       composition has reduced them to viewport-local float-sized values.
// v13 = Map unit scale in cached ModelGeoref is derived from
//       IfcMapConversion.Scale, not IfcProjectedCRS.MapUnit.
// v14 = Geometry is laid out in streaming-chunk order (SidecarLayout) and a
//       chunk table-of-contents (`chunks`) is appended.  The loader builds its
//       chunks from the TOC instead of re-deriving the Morton/greedy plan, so
//       each chunk is one CONTIGUOUS byte range — fixing network read
//       amplification.  The plan can't be re-derived at load because the float
//       Morton quantisation isn't bit-identical across toolchains (x86 baker vs
//       wasm loader), so it must be baked in.  No back-compat: v13 sidecars are
//       rejected (regenerate them).
// v15 = The post-index metadata is split into a geometry metadata block (meshes,
//       instances, georef, chunk TOC) followed by an element metadata block (elements +
//       string_table — IFC element metadata, used for UI/picking, never for
//       rendering), with the geometry block's byte length written just after
//       the index section.  The web loader reads only the geometry block before
//       painting, so first geometry no longer waits on the property data; the
//       element block is fetched lazily (or skipped where unused).  Desktop
//       reads both.  No back-compat: regenerate sidecars.
// v16 = Geometry + metadata are zstd-COMPRESSED.  Each chunk's vertex bytes and
//       index bytes are stored as two independent zstd frames (so per-chunk
//       Range streaming still works — you fetch + decompress just one chunk),
//       and the geometry + element metadata blocks are single zstd frames.
//       The chunk TOC records each chunk's compressed blob offsets/sizes plus
//       the raw (decompressed) sizes.  ~3-5x fewer bytes over the wire while
//       keeping HTTP Range intact (unlike server Content-Encoding).  No
//       back-compat: regenerate sidecars.
// v17 = Removes unused element hierarchy metadata. No back-compat: regenerate
//       sidecars.
// v18 = InstanceInfo is no longer stored verbatim.  The on-disk instance record
//       is mesh_id, object_id, and the double[16]
//       placement (136 B, down from 232 B).  session_model_id belongs to the
//       session that loads the file, and transform / world AABB are derived
//       from the placement and the mesh's local AABB (identity stage matrices)
//       by the readers, exactly as the baker used to derive them before
//       writing.  No back-compat: regenerate sidecars.
// v19 = The placement is stored as a double[3] translation plus a float[9]
//       column-major linear part (68 B per instance, down from 136).  The
//       bottom row of an IFC placement is always 0 0 0 1, and float holds the
//       rotation to ~1e-7 relative, under a micron over any mesh extent, while
//       the translation keeps the double precision that large placements need
//       until the federation false origin cancels them.  The geometry metadata
//       block is what the web loader must finish reading before it can fetch
//       any chunk, so its size is on the path to first paint.  No back-compat:
//       regenerate sidecars.
static constexpr uint32_t SIDECAR_VERSION = 19;
static constexpr uint32_t SIDECAR_ENDIAN  = 0x01020304;

// On-disk per-instance record (v19): mesh_id, object_id, translation as
// double[3], then the 3x3 linear part of the placement as float[9]
// (column-major), written field by field so there is no alignment padding.
static constexpr std::size_t SIDECAR_INSTANCE_RECORD_BYTES =
    2 * sizeof(uint32_t) + 3 * sizeof(double) + 9 * sizeof(float);

// Parse a count-prefixed run of v19 instance records from
// [cursor, cursor + remaining), advancing both, and expand them into
// InstanceInfo with transform and world AABB derived from `meshes` under
// identity stage matrices.  False when the data is truncated.
bool readInstanceInfos(const uint8_t*& cursor, std::size_t& remaining,
                       const std::vector<MeshInfo>& meshes,
                       std::vector<InstanceInfo>& out);

// Chunk table-of-contents entry (v16).  A chunk is a CONTIGUOUS range of meshes
// [first_mesh, first_mesh + mesh_count).  Its vertex + index bytes are stored as
// two zstd frames in the geometry section; the loader fetches [v_comp_off,
// +v_comp_size) / [i_comp_off, +i_comp_size) (offsets relative to the geometry
// section start) and decompresses them to v_raw_size / i_raw_size bytes — the
// chunk-local (vbytes, idx) applyStreamedChunk consumes.
struct SidecarChunk {
    uint32_t first_mesh;
    uint32_t mesh_count;
    uint64_t v_comp_off;
    uint64_t v_comp_size;
    uint64_t v_raw_size;
    uint64_t i_comp_off;
    uint64_t i_comp_size;
    uint64_t i_raw_size;
};

// Fixed-size element record.  Strings are stored as (offset, length) pairs
// into a separate string table.
struct ElementTableRecord {
    uint32_t object_id;
    uint32_t session_model_id;
    int32_t  ifc_id;
    uint32_t guid_offset;
    uint32_t guid_length;
    uint32_t name_offset;
    uint32_t name_length;
    uint32_t type_offset;
    uint32_t type_length;
};

// Everything needed to display an already-tessellated model without
// re-running the iterator.  v6 schema: instanced + quantized geometry.
struct SidecarData {
    // Per-model GPU geometry (local coords).  Raw VBO bytes at the
    // INSTANCED_VERTEX_STRIDE_BYTES layout (12 B/vertex as of v7).
    std::vector<uint8_t>      vertices;
    std::vector<uint32_t>     indices;

    // Mesh dictionary and per-instance data.
    std::vector<MeshInfo>     meshes;        // indexed by mesh_id
    std::vector<InstanceInfo>  instances;     // sorted by mesh_id

    // CoordinateOperation cache (v11+).  Mirrors ModelGeoref so a sidecar
    // load can apply georef without re-parsing the IFC source.
    // has_coordinate_operation == 0 means the model has no
    // IfcMapConversion; the matrix is then the identity placeholder.
    double   coordinate_operation_meters[16] = {
                 1, 0, 0, 0,
                 0, 1, 0, 0,
                 0, 0, 1, 0,
                 0, 0, 0, 1 };
    double   project_length_to_meters = 1.0;
    double   map_unit_to_meters       = 1.0;
    uint32_t has_coordinate_operation = 0;

    // Element metadata.
    std::vector<ElementTableRecord> elements;
    std::string               string_table;

    // Streaming chunk TOC.  Always written on disk (v14); geometry is laid out
    // in this chunk order (see SidecarLayout) so each chunk is one contiguous
    // range and the loader builds chunks directly from it. Stays empty only for
    // in-memory direct loads (finalizeModel), which don't stream and fall back
    // to deriving the plan.
    std::vector<SidecarChunk> chunks;
};

// Sidecar is keyed on the path stem: foo.ifc and foo.ifcdb/ both resolve to
// foo.ifcview alongside the source.  No staleness check — callers delete the
// file to invalidate.
bool writeSidecar(const std::string& ifc_path, const SidecarData& data);

std::optional<SidecarData> readSidecar(const std::string& ifc_path);

#endif // SIDECARCACHE_H
