#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#include "../profile_helper.h"

taxonomy::item* mapping::map_impl(const IfcSchema::IfcPolyline* inst) {
	IfcSchema::IfcCartesianPoint::list::ptr points = inst->Points();

	// @todo
	const double precision_ = 1.e-5;

	// Parse and store the points in a sequence
	std::vector<taxonomy::point3> polygon;
	polygon.reserve(points->size());
	std::transform(points->begin(), points->end(), std::back_inserter(polygon), [this](const IfcSchema::IfcCartesianPoint* p) {
		return as<taxonomy::point3>(map(p));
	});

	const double eps = precision_ * 10;
	const bool closed_by_proximity = polygon.size() >= 3 && (*polygon.front().components_ - *polygon.back().components_).norm() < eps;
	
	// @todo this removes the end point, since it's identical to the beginning. 
	if (closed_by_proximity) {
		// polygon.resize(polygon.size() - 1);
	}

	// Remove points that are too close to one another
	// remove_duplicate_points_from_loop(polygon, closed_by_proximity, eps);

	if (polygon.size() < 2) {
		return nullptr;
	}

	return polygon_from_points(polygon);
}
