#ifndef PROFILE_HELPER_H
#define PROFILE_HELPER_H

#include "ifc_geom_api.h"
#include "taxonomy.h"

namespace ifcopenshell {

	namespace geometry {
		struct profile_point {
			std::array<double, 2> xy;
			std::optional<double> radius;

			profile_point(const std::array<double, 2>& p, const std::optional<double>& r = std::nullopt)
				: xy(p), radius(r) {
			}

			// Recent Boost makes optional's converting constructor explicit,
			// and an explicit constructor cannot be used in copy-initialization
			// - which is what `{{x, y}, {radius}}` in the profile mappings is.
			// Taking the double directly keeps every call site working.
			profile_point(const std::array<double, 2>& p, double r)
				: xy(p), radius(r) {
			}
		};

		struct profile_point_with_edges {
			Eigen::Vector2d xy;
			std::optional<double> radius;
			taxonomy::edge::ptr previous, next;
		};

		struct profile_point_with_edges_3d {
			Eigen::Vector3d xy;
			std::optional<double> radius;
			taxonomy::edge::ptr previous, next;
		};

		IFC_GEOM_API taxonomy::loop::ptr polygon_from_points(const std::vector<taxonomy::point3::ptr>& ps, bool external = true);

		IFC_GEOM_API taxonomy::loop::ptr profile_helper(const taxonomy::matrix4::ptr& m4, const std::vector<profile_point>& points);

		IFC_GEOM_API taxonomy::loop::ptr fillet_loop(taxonomy::loop::ptr lp, double radius);

		IFC_GEOM_API void remove_duplicate_points_from_loop(std::vector<taxonomy::point3::ptr>& polygon, bool closed, double tol);

		IFC_GEOM_API std::pair<std::vector<taxonomy::point3::ptr>, std::vector<std::set<std::string>>> remove_duplicate_points_from_loop(const std::vector<taxonomy::point3::ptr>& polygon, const std::vector<std::string>& tags);
	}

}

#endif
