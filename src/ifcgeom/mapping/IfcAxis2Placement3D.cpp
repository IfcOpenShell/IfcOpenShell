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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcAxis2Placement3D* inst) {
	Eigen::Vector3d o, axis(0, 0, 1), refDirection, X(1, 0, 0);
	{
		taxonomy::point3::ptr v = taxonomy::cast<taxonomy::point3>(map(inst->Location()));
		o = *v->components_;
	}
	const bool hasAxis = !!inst->Axis();
	const bool hasRef = !!inst->RefDirection();

	if (hasAxis != hasRef) {
		Logger::Warning("Axis and RefDirection should be specified together", inst);
	}

	if (hasAxis) {
		taxonomy::direction3::ptr v = taxonomy::cast<taxonomy::direction3>(map(inst->Axis()));
		axis = *v->components_;
	}

	if (hasRef) {
		taxonomy::direction3::ptr v = taxonomy::cast<taxonomy::direction3>(map(inst->RefDirection()));
		refDirection = *v->components_;
	} else {
		if (acos(axis.dot(X)) > 1.e-5) {
			refDirection = { 1., 0., 0. };
		} else {
			refDirection = { 0., 0., 1. };
		}
		auto Xvec = axis.dot(refDirection) * axis;
		auto Xaxis = refDirection - Xvec;
		refDirection = Xaxis;
	}
	return taxonomy::make<taxonomy::matrix4>(o, axis, refDirection);
}
