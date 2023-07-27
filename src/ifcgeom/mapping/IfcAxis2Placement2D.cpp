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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcAxis2Placement2D* inst) {
	Eigen::Vector3d P, axis(0, 0, 1), V(1, 0, 0);
	{
		taxonomy::point3::ptr v = taxonomy::cast<taxonomy::point3>(map(inst->Location()));
		P = *v->components_;
	}
	const bool hasRef = !!inst->RefDirection();
	if (hasRef) {
		taxonomy::direction3::ptr v = taxonomy::cast<taxonomy::direction3>(map(inst->RefDirection()));
		V = *v->components_;
	}
	return taxonomy::make<taxonomy::matrix4>(P, axis, V);
}
