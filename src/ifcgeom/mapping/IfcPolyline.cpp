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

#include "../profile_helper.h"

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcPolyline* inst) {
	IfcSchema::IfcCartesianPoint::list::ptr points = inst->Points();

	// Parse and store the points in a sequence
	std::vector<taxonomy::point3::ptr> polygon;
	polygon.reserve(points->size());
	std::transform(points->begin(), points->end(), std::back_inserter(polygon), [this](const IfcSchema::IfcCartesianPoint* p) {
		return taxonomy::cast<taxonomy::point3>(map(p));
	});

	const bool closed_by_proximity = polygon.size() >= 3 && (*polygon.front()->components_ - *polygon.back()->components_).norm() < settings_.get<settings::Precision>().get();
	if (closed_by_proximity) {
		polygon.resize(polygon.size() - 1);
		polygon.push_back(polygon.front());
	}

	// @todo Remove points that are too close to one another
	// util::remove_duplicate_points_from_loop(polygon, closed_by_proximity, eps);

	if (polygon.size() < 2) {
		// We somehow need to signal we fail this curve on purpose not to trigger an error.
		return nullptr;
	}

	return polygon_from_points(polygon);
}
