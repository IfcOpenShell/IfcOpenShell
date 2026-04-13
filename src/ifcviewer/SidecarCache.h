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
static constexpr uint32_t SIDECAR_VERSION = 5;
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
// re-running the iterator.  v4 schema: instanced geometry.
struct SidecarData {
    // Per-model GPU geometry (local coords).  28 bytes/vertex.
    std::vector<float>        vertices;
    std::vector<uint32_t>     indices;

    // Mesh dictionary and per-instance data.
    std::vector<MeshInfo>     meshes;        // indexed by local_mesh_id
    std::vector<InstanceCpu>  instances;     // sorted by mesh_id

    // Element tree metadata.
    std::vector<PackedElementInfo> elements;
    std::string               string_table;
};

// v4 writer/reader are stubbed for Commit A — no disk I/O happens.
bool writeSidecar(const std::string& ifc_path,
                  const SidecarData& data,
                  uint64_t ifc_file_size);

std::optional<SidecarData> readSidecar(const std::string& ifc_path,
                                       uint64_t ifc_file_size);

#endif // SIDECARCACHE_H
