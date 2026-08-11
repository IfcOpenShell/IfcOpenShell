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
// src/ifcopenshell-python/ifcopenshell/util/geolocation.py.

#ifndef GEOLOCATION_H
#define GEOLOCATION_H

#include "../ifcparse/express.h"
#include "geolocation_transform.h"

#include <Eigen/Dense>
#include <optional>

namespace ifcopenshell {
class file;
}

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

// Lift a 4x4 local matrix into global (map) coordinates using the IFC model's
// georeferencing data.  When no map conversion is present the matrix is
// returned unchanged.  When should_return_in_map_units is false, the
// translation column is divided by the map scale so the result is expressed
// in project length units.
Eigen::Matrix4d auto_local_to_global(ifcopenshell::file* ifc_file,
                                     const Eigen::Matrix4d& matrix,
                                     bool should_return_in_map_units = true);

// IfcCoordinateOperation.TargetCRS.MapUnit (the IfcNamedUnit), if present.
// Returns nullopt for IFC2X3, models without an IfcCoordinateOperation, or
// when MapUnit is absent on the IfcProjectedCRS.  This is retained for UI /
// metadata inspection; transform composition derives map unit scale from
// IfcMapConversion.Scale instead.
std::optional<express::base> get_map_unit(ifcopenshell::file* ifc_file);

#endif // GEOLOCATION_H
