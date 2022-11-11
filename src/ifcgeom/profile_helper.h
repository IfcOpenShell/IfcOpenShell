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
			taxonomy::edge *previous, *next;
		};

		taxonomy::loop* polygon_from_points(const std::vector<taxonomy::point3>& ps, bool external = true);

		taxonomy::loop* profile_helper(Eigen::Matrix4d& m4, const std::vector<profile_point>& points);

	}

}