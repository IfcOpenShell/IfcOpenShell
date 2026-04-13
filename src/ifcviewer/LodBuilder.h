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

#ifndef LODBUILDER_H
#define LODBUILDER_H

#include "SidecarCache.h"

// Build a LOD1 index slice for every mesh in `sd` whose triangle count is
// above `min_triangles`, using meshoptimizer's edge-collapse decimator.  The
// LOD1 indices are appended to `sd.indices`; each MeshInfo's
// lod1_ebo_byte_offset + lod1_index_count are populated to point at the
// appended range.  Meshes that don't qualify (too small) or where the
// decimator couldn't meet the target within the error budget have
// lod1_index_count left at 0 (renderer falls back to LOD0).
//
// Defaults match the Phase 3B first-iteration design:
//   min_triangles = 500     — below this the overhead dominates
//   target_ratio  = 0.25    — aim for 25% of original tris
//   target_error  = 0.05    — stop if relative error exceeds 5%
//
// `sd.vertices` is read (position is the first 3 floats of each
// INSTANCED_VERTEX_STRIDE_FLOATS-wide vertex) but not modified — LOD1
// reuses the same vertex buffer, just with a different index list.
void buildLods(SidecarData& sd,
               int min_triangles = 500,
               float target_ratio = 0.25f,
               float target_error = 0.05f);

// Cheap summary for logging.  Safe to call before or after buildLods.
struct LodStats {
    uint32_t meshes_total       = 0;
    uint32_t meshes_with_lod1   = 0;
    uint32_t tris_lod0          = 0;   // sum across all meshes
    uint32_t tris_lod1          = 0;   // only for meshes that got LOD1
    uint32_t tris_lod0_for_lod1 = 0;   // LOD0 tris of the meshes that got LOD1
};
LodStats summariseLods(const SidecarData& sd);

#endif // LODBUILDER_H
