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

// Georeferencing matrix math over plain numbers: no IFC file, no schema
// dispatch, no Qt.
//
// Split out of geolocation.h/geolocation.cpp for the same reason as
// unit_convert: those pull in ../ifcparse/express.h to read an
// IfcMapConversion out of a model, but IfcViewerCore — and through it the
// Emscripten build — needs to compose the resulting matrices without
// linking IfcParse.  Reading the parameters out of an IFC stays in
// geolocation.h; turning them into matrices lives here.

#ifndef GEOLOCATION_TRANSFORM_H
#define GEOLOCATION_TRANSFORM_H

#include <Eigen/Dense>

struct HelmertTransformation {
    double e = 0.0;        // eastings offset
    double n = 0.0;        // northings offset
    double h = 0.0;        // orthogonal-height offset
    double xaa = 1.0;      // X-axis abscissa  (cos of grid-rotation angle)
    double xao = 0.0;      // X-axis ordinate  (sin of grid-rotation angle)
    double scale = 1.0;    // unit scale (project unit -> map unit)
    double factor_x = 1.0; // combined scale factor along X
    double factor_y = 1.0; // combined scale factor along Y
    double factor_z = 1.0; // combined scale factor along Z
};

// Apply a Helmert transformation to a 4x4 local matrix.
Eigen::Matrix4d local_to_global(const Eigen::Matrix4d& matrix,
                                const HelmertTransformation& params);

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

// "How do I rotate project east to get to grid east?" — i.e. -atan2(xao, xaa)
// converted to degrees, anticlockwise positive.  Mirrors
// ifcopenshell.util.geolocation.xaxis2angle.
double x_axis_to_angle_deg(double xaa, double xao);

#endif // GEOLOCATION_TRANSFORM_H
