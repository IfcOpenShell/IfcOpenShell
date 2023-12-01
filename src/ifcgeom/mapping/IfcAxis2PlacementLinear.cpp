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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#if defined SCHEMA_HAS_IfcAxis2PlacementLinear

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcAxis2PlacementLinear* inst) {

	if (!inst->Location()->as<IfcSchema::IfcPointByDistanceExpression>())
         Logger::Error(std::runtime_error("Location must be IfcPointByDistanceExpression for IfcAxis2PlacementLinear"));

	Eigen::Vector3d o, axis(0, 0, 1), refDirection;

	taxonomy::matrix4::ptr m = taxonomy::cast<taxonomy::matrix4>(map(inst->Location()));
    o = m->components().col(3).head<3>();

   const bool hasAxis = !!inst->Axis();
	const bool hasRef = !!inst->RefDirection();

	if (hasAxis != hasRef) {
		Logger::Warning("Axis and RefDirection should be specified together", inst);
	}

	if (hasAxis) {
		taxonomy::direction3::ptr v = taxonomy::cast<taxonomy::direction3>(map(inst->Axis()));
		axis = *v->components_;
    } else { 
		// 8.9.3.4 IfcAxis2LinearPlacement does not specify the default when Axis is omitted
		// When RefDirection is omitted, see comment below, it is taken to be tangent to the curve.
		// To be consistent, Axis is taken to be orthogonal to RefDirection
        axis = m->components().col(2).head<3>();
    }

	if (hasRef) {
		taxonomy::direction3::ptr v = taxonomy::cast<taxonomy::direction3>(map(inst->RefDirection()));
		refDirection = *v->components_;
	} else {
		// 8.9.3.4 IfcAxis2LinearPlacement 
		// https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcAxis2PlacementLinear.htm
      // "If RefDirection is omitted, the direction is taken from the curve tangent at Location"
		//
		// When the PointByDistanceExpression Location is evaluated, it is evaluating the basis curve and returning
		// the matrix of orthogonal vectors that define the coordinate system at the point on curve as well as the point on curve
		// In other words, the m matrix has everything needed

		refDirection = m->components().col(0).head<3>();

    }
	return taxonomy::make<taxonomy::matrix4>(o, axis, refDirection);
}

#endif
