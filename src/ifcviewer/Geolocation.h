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

// Port of selected helpers from
// src/ifcopenshell-python/ifcopenshell/util/geolocation.py — primarily
// auto_local2global, which builds a 4x4 matrix that lifts an element's local
// transform into the model's global (georeferenced) frame.  The python utils
// are expected to be ported to C++ in their own module later; this file is
// the temporary home until that lands.

#ifndef GEOLOCATION_H
#define GEOLOCATION_H

#include <Eigen/Dense>

#include <optional>

namespace ifcopenshell { class file; }

struct HelmertTransformation {
    double e        = 0.0;  // eastings offset
    double n        = 0.0;  // northings offset
    double h        = 0.0;  // orthogonal-height offset
    double xaa      = 1.0;  // X-axis abscissa  (cos of grid-rotation angle)
    double xao      = 0.0;  // X-axis ordinate  (sin of grid-rotation angle)
    double scale    = 1.0;  // unit scale (project unit -> map unit)
    double factor_x = 1.0;  // combined scale factor along X
    double factor_y = 1.0;  // combined scale factor along Y
    double factor_z = 1.0;  // combined scale factor along Z
};

// Detect a Helmert transformation in the IFC model.  Reads IfcMapConversion /
// IfcMapConversionScaled / IfcRigidOperation in IFC4+, or the
// IfcProject.ePSet_MapConversion property set in IFC2X3.  Returns nullopt
// when the model has no map conversion.
std::optional<HelmertTransformation>
getHelmertTransformationParameters(ifcopenshell::file* ifc_file);

// Read the IfcGeometricRepresentationContext.WorldCoordinateSystem (preferring
// the "Model" context) as a 4x4 matrix.  Returns nullopt when the model has
// no parseable WCS.
std::optional<Eigen::Matrix4d> getWcs(ifcopenshell::file* ifc_file);

// Apply a Helmert transformation to a 4x4 local matrix.
Eigen::Matrix4d local2global(const Eigen::Matrix4d& matrix,
                             const HelmertTransformation& params);

// Lift a 4x4 local matrix into global (map) coordinates using the IFC model's
// georeferencing data.  When no map conversion is present the matrix is
// returned unchanged.  When should_return_in_map_units is false, the
// translation column is divided by the map scale so the result is expressed
// in project length units.
Eigen::Matrix4d autoLocal2Global(ifcopenshell::file* ifc_file,
                                 const Eigen::Matrix4d& matrix,
                                 bool should_return_in_map_units = true);

#endif // GEOLOCATION_H
