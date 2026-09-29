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

// This file was generated with the assistance of an AI coding tool.

// Prototype for issue #5218: maps a "PointCloud" IfcCartesianPointList3D item
// to a taxonomy::collection of point3, read straight from CoordList (see
// kernels/opencascade/point.cpp for the bulk conversion fast path).

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#ifdef SCHEMA_HAS_IfcCartesianPointList3D

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCartesianPointList3D* inst) {
	auto coord_list = inst->CoordList();
	if (coord_list.empty()) {
		return nullptr;
	}

	auto c = taxonomy::make<taxonomy::collection>();
	c->children.reserve(coord_list.size());
	for (auto& coords : coord_list) {
		auto p = taxonomy::make<taxonomy::point3>(
			coords.size() < 1 ? 0. : coords[0] * length_unit_,
			coords.size() < 2 ? 0. : coords[1] * length_unit_,
			coords.size() < 3 ? 0. : coords[2] * length_unit_);
		// No entity per point, so id() lookups in the per-child fallback path
		// stay safe by sharing the list's own instance.
		p->instance = inst;
		c->children.push_back(p);
	}
	return c;
}

#endif
