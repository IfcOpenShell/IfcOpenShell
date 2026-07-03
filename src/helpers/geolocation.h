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
// auto_local_to_global, which builds a 4x4 matrix that lifts an element's local
// transform into the model's global (georeferenced) frame.  The python utils
// are expected to be ported to C++ in their own module later; this file is
// the temporary home until that lands.

#ifndef GEOLOCATION_H
#define GEOLOCATION_H

#include "../ifcparse/express.h"

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
get_helmert_transformation_parameters(ifcopenshell::file* ifc_file);

// Read the IfcGeometricRepresentationContext.WorldCoordinateSystem (preferring
// the "Model" context) as a 4x4 matrix.  Returns nullopt when the model has
// no parseable WCS.
std::optional<Eigen::Matrix4d> get_wcs(ifcopenshell::file* ifc_file);

// Apply a Helmert transformation to a 4x4 local matrix.
Eigen::Matrix4d local_to_global(const Eigen::Matrix4d& matrix,
                                const HelmertTransformation& params);

// Lift a 4x4 local matrix into global (map) coordinates using the IFC model's
// georeferencing data.  When no map conversion is present the matrix is
// returned unchanged.  When should_return_in_map_units is false, the
// translation column is divided by the map scale so the result is expressed
// in project length units.
Eigen::Matrix4d auto_local_to_global(ifcopenshell::file* ifc_file,
                                     const Eigen::Matrix4d& matrix,
                                     bool should_return_in_map_units = true);

// Build the Helmert transformation as a meter-input / meter-output 4x4 matrix
// directly from parsed parameters, bypassing auto_local_to_global's normalisation
// step.  Used by callers that want a single per-model georef matrix to compose
// with placement matrices at upload time.
//
// Result has shape:
//     [ R_z(theta) · diag(fx, fy, fz)  | (e, n, h) · u_m ]
//     [ 0                               | 1               ]
//
// `map_unit_to_meters` is derived by the caller from the IFC project length
// unit and the authoritative IfcMapConversion.Scale.  Since this matrix takes
// meter inputs from the geometry iterator, Scale is represented by that unit
// conversion and is not applied again in the linear block.  The caller composes
// any IfcGeometricRepresentationContext WCS on the right:
//     G = helmert_meters_from_parameters(...) · inv(wcs_meters)
// (where wcs_meters has its translation column converted from project units
// to meters via calculate_unit_scale).
//
// Unlike auto_local_to_global, this preserves IfcMapConversionScaled.FactorX/Y/Z
// in the rotation block, so they apply correctly to placement translations
// when composing per-model.
Eigen::Matrix4d helmert_meters_from_parameters(const HelmertTransformation& params,
                                               double map_unit_to_meters);

// IfcCoordinateOperation.TargetCRS.MapUnit (the IfcNamedUnit), if present.
// Returns nullopt for IFC2X3, models without an IfcCoordinateOperation, or
// when MapUnit is absent on the IfcProjectedCRS.  This is retained for UI /
// metadata inspection; transform composition derives map unit scale from
// IfcMapConversion.Scale instead.
std::optional<express::Base> get_map_unit(ifcopenshell::file* ifc_file);

// "How do I rotate project east to get to grid east?" — i.e. -atan2(xao, xaa)
// converted to degrees, anticlockwise positive.  Mirrors
// ifcopenshell.util.geolocation.xaxis2angle.
double x_axis_to_angle_deg(double xaa, double xao);

#endif // GEOLOCATION_H
