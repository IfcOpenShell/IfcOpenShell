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

#ifndef IFCGEOM_SMLIB_UTILS_H
#define IFCGEOM_SMLIB_UTILS_H

#include "../../../ifcgeom/conversion_settings.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

// Self-contained, so that users of these helpers do not need the kernel headers.
#include <SmApiTessellationParams.h>

#include <Eigen/Dense>

class SmAxis2Placement;
class SmBrep;

namespace ifcopenshell {
namespace geom {

/// SMLib keeps a process global context that has to be created before use and
/// is not safe to create from multiple threads. This is idempotent and
/// thread-safe as long as the caller does not invoke SMLib concurrently.
IFC_GEOMLIBRARY_API void smlib_ensure_context();

constexpr double SMLIB_PI = 3.14159265358979323846;

/// Translates IfcOpenShell deflection settings to SMLib tessellation quality.
IFC_GEOMLIBRARY_API SmTessellationParams smlib_tessellation_params(const ifcopenshell::geom::settings& settings);

/// Converts a 4x4 homogeneous transformation to an SMLib placement.
IFC_GEOMLIBRARY_API void smlib_placement_from_matrix(const Eigen::Matrix4d& matrix, SmAxis2Placement& placement);

/// Applies a boolean operation to two boundary representations. The inputs are
/// left untouched; the result is owned by the caller.
IFC_GEOMLIBRARY_API SmBrep* smlib_brep_boolean(SmBrep* a, SmBrep* b, long operation);

} // namespace geom
} // namespace ifcopenshell

#endif
