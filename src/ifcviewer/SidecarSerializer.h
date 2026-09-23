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

#ifndef SIDECARSERIALIZER_H
#define SIDECARSERIALIZER_H

#include "FederationMath.h"
#include "InstancedGeometry.h"
#include "SidecarCache.h"

#include <vector>

// Assembles a .ifcview SidecarData from streamer output and finalizes it
// (LOD build, element packing, Morton chunk layout + chunk TOC).
//
// Deliberately Qt-free: SidecarBuilder (the QObject that drives a live
// GeometryStreamer) and the IfcConvert .ifcview serializer plugin both wrap
// this class instead of each carrying its own copy of the assembly logic.
class SidecarSerializer {
public:
    // Accumulator interface. Safe to call repeatedly from a single thread.
    void onMeshReady(const StreamedMesh& mesh);
    void onInstanceReady(const StreamedInstance& instance_record);

    // Finishes assembly using the georef + element batch the caller collected
    // during streaming. Returns the assembled SidecarData by move; the
    // serializer's internal state is left empty so the same instance can be
    // reused for another load. The returned data is laid out in streaming
    // chunk order (SidecarLayout) so it is ready for writeSidecar() as-is.
    SidecarData finalize(const ModelGeoref& georef,
                         const std::vector<ElementInfo>& elements);

private:
    SidecarData sidecar_data_;
};

#endif // SIDECARSERIALIZER_H
