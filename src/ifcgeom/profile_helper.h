#ifndef PROFILE_HELPER_H
#define PROFILE_HELPER_H

#include "taxonomy.h"

namespace ifcopenshell {

	namespace geometry {
		struct profile_point {
			std::array<double, 2> xy;
			boost::optional<double> radius;
		};

		struct profile_point_with_edges {
			Eigen::Vector2d xy;
			boost::optional<double> radius;
			taxonomy::edge::ptr previous, next;
		};

		struct profile_point_with_edges_3d {
			Eigen::Vector3d xy;
			boost::optional<double> radius;
			taxonomy::edge::ptr previous, next;
		};

		taxonomy::loop::ptr polygon_from_points(const std::vector<taxonomy::point3::ptr>& ps, bool external = true);

		taxonomy::loop::ptr profile_helper(const taxonomy::matrix4::ptr& m4, const std::vector<profile_point>& points);

		taxonomy::loop::ptr fillet_loop(taxonomy::loop::ptr lp, double radius);
	}

}

#endif