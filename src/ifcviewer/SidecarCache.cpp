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

// Commit A: sidecar cache is temporarily disabled.  The on-disk format is
// being rewritten from v3 (monolithic world-coord geometry) to v4 (instanced
// meshes + per-instance records).  Until v4 is finalised, loads always go
// through the streaming path and writes are no-ops.

#include "SidecarCache.h"

bool writeSidecar(const std::string& /*ifc_path*/,
                  const SidecarData& /*data*/,
                  uint64_t /*ifc_file_size*/) {
    return true;
}

std::optional<SidecarData> readSidecar(const std::string& /*ifc_path*/,
                                       uint64_t /*ifc_file_size*/) {
    return std::nullopt;
}
