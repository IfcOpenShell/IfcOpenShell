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
// src/ifcopenshell-python/ifcopenshell/util/placement.py — entity-instance
// placement chains -> 4x4 matrices, used by callers that need to read
// IfcLocalPlacement / IfcAxis2Placement* outside of the geometry kernel.

#ifndef PLACEMENT_H
#define PLACEMENT_H

#include "../ifcparse/express.h"

#include <Eigen/Dense>

// Build a 4x4 placement matrix from an origin + Z + X axis triple, mirroring
// ifcopenshell.util.placement.a2p.  The Y axis is derived as Z × X.  Inputs
// don't need to be unit; vectors are renormalised internally.
Eigen::Matrix4d axes_to_placement(const Eigen::Vector3d& origin,
                                  const Eigen::Vector3d& z,
                                  const Eigen::Vector3d& x);

// IfcAxis2Placement{2D,3D,Linear} / IfcAxis1Placement -> 4x4 matrix.  Mirrors
// ifcopenshell.util.placement.get_axis2placement.  Returns identity for null
// or unparseable inputs.  Translation is in the IFC's project length unit.
Eigen::Matrix4d get_axis2_placement(const express::Base& placement);

// Resolve an IfcLocalPlacement (or an IfcAxis2Placement* directly) into a
// 4x4 matrix in the IFC project's length unit, walking the PlacementRelTo
// chain.  Mirrors ifcopenshell.util.placement.get_local_placement.  Returns
// identity for a null input.
Eigen::Matrix4d get_local_placement(const express::Base& placement);

#endif // PLACEMENT_H
