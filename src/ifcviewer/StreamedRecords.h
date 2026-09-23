// This file was generated with the assistance of an AI coding tool.
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

#ifndef STREAMEDRECORDS_H
#define STREAMEDRECORDS_H

#include "InstancedGeometry.h"

#include <Eigen/Dense>

namespace ifcopenshell::geom { class triangulation_element; }

// Per-unique-mesh state shared across the instances that reference it.
// `offset` is the vertex-rebase applied to the emitted verts (zero when the
// mesh's first vertex is near the origin and rebasing wasn't worth it);
// `has_offset` tells makeStreamedInstance to compensate the placement.
struct MeshAabb {
    float  lmin[3];
    float  lmax[3];
    double offset[3] = {0.0, 0.0, 0.0};
    bool   has_offset = false;
};

// Record builders shared by the live streamer (GeometryStreamer::run) and the
// ifcconvert bake (IfcViewSerializer), so both produce the same vertex and
// placement encoding.  Pure conversions: no Qt, no I/O.

// One interleaved transfer mesh (7 floats/vertex) from a triangulation
// element, in mesh-local coords.  When `offset` is non-zero every vertex
// position is emitted relative to it; the caller compensates by post-
// multiplying each instance's placement by T(+offset).
StreamedMesh buildStreamedMesh(uint32_t session_model_id,
                               uint32_t local_mesh_id,
                               const ifcopenshell::geom::triangulation_element* elem,
                               const Eigen::Vector3d& offset);

// One instance record for a triangulation element.  The placement is kept in
// double; a mesh-rebase offset (if any) is folded into it so world position is
// preserved.
StreamedInstance makeStreamedInstance(uint32_t session_model_id,
                                      uint32_t local_mesh_id,
                                      uint32_t object_id,
                                      const ifcopenshell::geom::triangulation_element& elem,
                                      const MeshAabb& mesh_aabb);

#endif // STREAMEDRECORDS_H
