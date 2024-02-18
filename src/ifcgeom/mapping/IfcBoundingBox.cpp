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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcBoundingBox* inst) {
	if (!settings_.get<settings::KeepBoundingBoxes>().get()) {
		// @todo make sure it doesn't log.
		return nullptr;
	}

	const double dx = inst->XDim() * length_unit_;
	const double dy = inst->YDim() * length_unit_;
	const double dz = inst->ZDim() * length_unit_;

	taxonomy::point3::ptr corner = taxonomy::cast<taxonomy::point3>(map(inst->Corner()));
	auto solid = create_box(corner->ccomponents().x(), corner->ccomponents().y(), corner->ccomponents().z(), dx, dy, dz);

	return solid;
}
