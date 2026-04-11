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

#ifndef SIDECARCACHE_H
#define SIDECARCACHE_H

#include "BvhAccel.h"

#include <cstdint>
#include <optional>
#include <string>
#include <vector>

static constexpr uint32_t SIDECAR_MAGIC   = 0x49465657;  // "IFVW"
static constexpr uint32_t SIDECAR_VERSION = 3;
static constexpr uint32_t SIDECAR_ENDIAN  = 0x01020304;

// Fixed-size element record for the sidecar.  Strings are stored as
// (offset, length) pairs into a separate string table.
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

// Everything the viewer needs to display a model without tessellating.
struct SidecarData {
    // GPU geometry (ready to upload as-is)
    std::vector<float>    vertices;      // interleaved, 8 floats per vertex
    std::vector<uint32_t> indices;       // global (already remapped)

    // Per-object metadata
    std::vector<ObjectDrawInfo> draw_info;

    // Element tree metadata
    std::vector<PackedElementInfo> elements;
    std::string string_table;            // concatenated UTF-8

    // BVH acceleration
    std::shared_ptr<BvhSet> bvh_set;
};

// Write a full sidecar next to the IFC file.
// Returns true on success.
bool writeSidecar(const std::string& ifc_path,
                  const SidecarData& data,
                  uint64_t ifc_file_size);

// Read a sidecar.  Returns nullopt on any failure (missing, stale, corrupt).
std::optional<SidecarData> readSidecar(const std::string& ifc_path,
                                       uint64_t ifc_file_size);

#endif // SIDECARCACHE_H
