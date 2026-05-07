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

#ifndef IFCVIEWER_FULL_MEASUREMENT_H
#define IFCVIEWER_FULL_MEASUREMENT_H

#include <cstdint>
#include <vector>

class ViewportWindow;

// Sum of mesh-local volumes (m³) of every instance whose object_id is in
// `object_ids`.  Groups by (model, mesh) so each unique mesh is read back
// from the GPU at most once per call; instances of the same mesh are scaled
// by |det(placement_3x3)| to pick up mapped-item scale/mirror.  Volume is
// taken as the absolute value of the signed-tetrahedra sum, so winding
// convention does not matter.  Returns 0.0 for empty input or when nothing
// resolves.  Recomputes from scratch on every call — no cache.
double volumeOfObjects(ViewportWindow& vp,
                       const std::vector<uint32_t>& object_ids);

#endif // IFCVIEWER_FULL_MEASUREMENT_H
