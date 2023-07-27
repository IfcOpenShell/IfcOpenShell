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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcAxis1Placement* inst) {
	Eigen::Vector3d P, axis(0, 0, 1), ref;
	{
		taxonomy::point3::ptr v = taxonomy::cast<taxonomy::point3>(map(inst->Location()));
		P = *v->components_;
	}
	const bool hasAxis = inst->Axis();
	if (hasAxis) {
		taxonomy::direction3::ptr v = taxonomy::cast<taxonomy::direction3>(map(inst->Axis()));
		axis = *v->components_;
	}
	
	// @todo not sure what to do with ref, we're probably never reading it,
	// because we just created an Axis1 again from it in the kernel, but
	// to this constructor we need to supply something valid.
	if (std::abs(axis.x()) > std::abs(axis.z())) {
		ref = Eigen::Vector3d(0, 0, 1).cross(axis).normalized();
	} else {
		ref = Eigen::Vector3d(1, 0, 0).cross(axis).normalized();
	}

	return taxonomy::make<taxonomy::matrix4>(P, axis, ref);
}
