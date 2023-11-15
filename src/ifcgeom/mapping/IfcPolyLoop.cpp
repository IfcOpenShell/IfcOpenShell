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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcPolyLoop* inst) {
	IfcSchema::IfcCartesianPoint::list::ptr points = inst->Polygon();

	// Parse and store the points in a sequence
	std::vector<taxonomy::point3::ptr> polygon;
	polygon.reserve(points->size());
	std::transform(points->begin(), points->end(), std::back_inserter(polygon), [this](const IfcSchema::IfcCartesianPoint* p) {
		return taxonomy::cast<taxonomy::point3>(map(p));
	});

	// A loop should consist of at least three vertices
	int original_count = polygon.size();
	if (original_count < 3) {
		Logger::Message(Logger::LOG_WARNING, "Not enough edges for:", inst);
		return nullptr;
	}

	// @todo Remove points that are too close to one another
	const double eps = settings_.get<settings::Precision>().get();
	// util::remove_duplicate_points_from_loop(polygon, true, eps);

	int count = polygon.size();
	if (original_count - count != 0) {
		std::stringstream ss; ss << (original_count - count) << " edges removed for:"; 
		Logger::Message(Logger::LOG_WARNING, ss.str(), inst);
	}

	if (count < 3) {
		Logger::Message(Logger::LOG_WARNING, "Not enough edges for:", inst);
		return nullptr;
	}

	// Contrary to polyline the loop is implicitly closed
	polygon.push_back(polygon.front());

	return polygon_from_points(polygon);

	// @todo make sure wire intersection check happens

	/*
	BRepBuilderAPI_MakePolygon w;
	for (int i = 1; i <= polygon.Length(); ++i) {
		w.Add(polygon.Value(i));
	}
	w.Close();

	result = w.Wire();

	TopTools_ListOfShape results;
	if (getValue(GV_NO_WIRE_INTERSECTION_CHECK) < 0. && util::wire_intersections(result, results, {getValue(GV_NO_WIRE_INTERSECTION_CHECK) < 0., getValue(GV_NO_WIRE_INTERSECTION_TOLERANCE) < 0., 0., getValue(GV_PRECISION)})) {
		Logger::Error("Self-intersections with " + boost::lexical_cast<std::string>(results.Extent()) + " cycles detected", l);
		util::select_largest(results, result);
	}

	return true;
	*/
}
