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
static constexpr uint32_t SIDECAR_VERSION = 9;
static constexpr uint32_t SIDECAR_ENDIAN  = 0x01020304;

// Fixed-size element record.  Strings are stored as (offset, length) pairs
// into a separate string table.
struct PackedElementInfo {
    uint32_t object_id;
    uint32_t model_id;
    int32_t  ifc_id;
    int32_t  parent_id;
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
    std::vector<MeshInfo>     meshes;        // indexed by local_mesh_id
    std::vector<InstanceCpu>  instances;     // sorted by mesh_id

    // Element tree metadata.
    std::vector<PackedElementInfo> elements;
    std::string               string_table;
};

// Sidecar is keyed on the path stem: foo.ifc and foo.ifcdb/ both resolve to
// foo.ifcview alongside the source.  No staleness check — callers delete the
// file to invalidate.
bool writeSidecar(const std::string& ifc_path, const SidecarData& data);

std::optional<SidecarData> readSidecar(const std::string& ifc_path);

#endif // SIDECARCACHE_H
