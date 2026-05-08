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

#ifndef IFCOPENSHELL_TREE_REGISTRY_H
#define IFCOPENSHELL_TREE_REGISTRY_H

#include "tree.h"
#include "../plugin/plugin.h"

#include <boost/function.hpp>

#include <map>
#include <memory>
#include <string>
#include <string_view>

namespace ifcopenshell {
	class file;

	namespace geometry {
		class Settings;

		namespace trees {

			struct IFC_GEOM_API tree_info {
				std::string backend_id;
			};

			class IFC_GEOM_API abstract_tree {
			public:
				virtual ~abstract_tree();

				virtual std::string_view backend_id() const = 0;

				virtual void add_file(ifcopenshell::file& file, const ifcopenshell::geometry::Settings& settings);
				virtual void add_element(IfcGeom::Element* element);

				virtual std::vector<express::Entity> select_box(const express::Entity& entity, bool completely_within, double extend) const;
				virtual std::vector<express::Entity> select_box(const IfcGeom::tree_point& point) const;
				virtual std::vector<express::Entity> select_box(const IfcGeom::tree_box& bounds, bool completely_within) const;

				virtual std::vector<express::Entity> select(const express::Entity& entity, bool completely_within, double extend) const;
				virtual std::vector<express::Entity> select(const IfcGeom::Element* element, bool completely_within, double extend) const;
				virtual std::vector<express::Entity> select(const IfcGeom::tree_point& point, double extend) const;
				virtual std::vector<IfcGeom::ray_intersection_result> select_ray(const IfcGeom::tree_point& origin, const IfcGeom::tree_point& direction, double length) const;

				virtual std::vector<IfcGeom::clash> clash_intersection_many(const std::vector<express::Entity>& set_a, const std::vector<express::Entity>& set_b, double tolerance, bool check_all) const;
				virtual std::vector<IfcGeom::clash> clash_collision_many(const std::vector<express::Entity>& set_a, const std::vector<express::Entity>& set_b, bool allow_touching) const;
				virtual std::vector<IfcGeom::clash> clash_clearance_many(const std::vector<express::Entity>& set_a, const std::vector<express::Entity>& set_b, double clearance, bool check_all) const;

				virtual const std::vector<double>& distances() const;
				virtual const std::vector<double>& protrusion_distances() const;
				virtual bool enable_face_styles() const;
				virtual void enable_face_styles(bool enable);
				virtual const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& styles() const;

			};

			class IFC_GEOM_API tree_registry {
			public:
				typedef boost::function0<abstract_tree*> create_fn;

				void bind(const tree_info& info, create_fn create, const ifcopenshell::plugin::module& module = ifcopenshell::plugin::module());
				bool has(const std::string& backend_id) const;
				std::unique_ptr<abstract_tree> create(const std::string& backend_id) const;

			private:
				struct entry {
					tree_info info_;
					create_fn create_;
					ifcopenshell::plugin::module module_;
				};

				std::map<std::string, entry> entries_;
			};

			IFC_GEOM_API tree_registry& tree_registry_instance();
			IFC_GEOM_API std::unique_ptr<abstract_tree> construct(const std::string& backend_id);

		}
	}
}

#endif
