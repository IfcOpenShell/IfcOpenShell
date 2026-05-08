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

#ifndef IFCOPENSHELL_TREE_H
#define IFCOPENSHELL_TREE_H

#include "IfcGeomElement.h"

#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace ifcopenshell {
	class file;

	namespace geometry {
		class Settings;
	}
}

namespace IfcGeom {
	class Iterator;

	using tree_point = std::array<double, 3>;
	using tree_box = std::array<tree_point, 2>;

	struct IFC_GEOM_API ray_intersection_result {
		double distance;
		int style_index;
		express::Entity instance;
		tree_point position;
		tree_point normal;
		double ray_distance;
		double dot_product;
	};

	struct IFC_GEOM_API clash {
		int clash_type;
		express::Base a;
		express::Base b;
		double distance;
		tree_point p1;
		tree_point p2;
	};

	class IFC_GEOM_API tree {
	public:
		tree();
		explicit tree(const std::string& backend_id);
		explicit tree(ifcopenshell::file& file);
		tree(ifcopenshell::file& file, const ifcopenshell::geometry::Settings& settings);
		explicit tree(IfcGeom::Iterator& iterator);
		~tree();

		tree(tree&& other) noexcept;
		tree& operator=(tree&& other) noexcept;

		tree(const tree& other) = delete;
		tree& operator=(const tree& other) = delete;

		void add_file(ifcopenshell::file& file, const ifcopenshell::geometry::Settings& settings);
		void add_file(IfcGeom::Iterator& iterator);
		void add_element(IfcGeom::Element* element);

		std::vector<express::Entity> select_box(const express::Entity& entity, bool completely_within = false, double extend = -1.e-5) const;
		std::vector<express::Entity> select_box(const tree_point& point) const;
		std::vector<express::Entity> select_box(const tree_box& bounds, bool completely_within = false) const;

		std::vector<express::Entity> select(const express::Entity& entity, bool completely_within = false, double extend = 0.0) const;
		std::vector<express::Entity> select(const IfcGeom::Element* element, bool completely_within = false, double extend = -1.e-5) const;
		std::vector<express::Entity> select(const tree_point& point, double extend = 0.0) const;
		std::vector<ray_intersection_result> select_ray(const tree_point& origin, const tree_point& direction, double length = 1000.) const;

		std::vector<clash> clash_intersection_many(const std::vector<express::Base>& set_a, const std::vector<express::Base>& set_b, double tolerance = 0.002, bool check_all = true) const;
		std::vector<clash> clash_collision_many(const std::vector<express::Base>& set_a, const std::vector<express::Base>& set_b, bool allow_touching = false) const;
		std::vector<clash> clash_clearance_many(const std::vector<express::Base>& set_a, const std::vector<express::Base>& set_b, double clearance = 0.05, bool check_all = false) const;

		const std::vector<double>& distances() const;
		const std::vector<double>& protrusion_distances() const;

		bool enable_face_styles() const;
		void enable_face_styles(bool enable);
		const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& styles() const;

		std::string uint8_to_b64(const std::vector<uint8_t>& uuids_array) const;
		static bool is_manifold(const std::vector<int>& faces);

	private:
		class impl;
		std::unique_ptr<impl> impl_;
	};
}

#endif
