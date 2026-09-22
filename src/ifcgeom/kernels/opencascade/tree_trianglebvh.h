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

#ifndef IFCOPENSHELL_OPENCASCADE_TREE_TRIANGLEBVH_H
#define IFCOPENSHELL_OPENCASCADE_TREE_TRIANGLEBVH_H

#include "../../kernel_registry.h"
#include "../../tree_registry.h"
#include "../../../ifcparse/exception.h"
#include "tree.h"

namespace ifcopenshell {
	namespace geom {
		namespace trees {
			namespace opencascade_tree_backends {

				class trianglebvh_tree : public abstract_tree {
				public:
					std::string_view backend_id() const override {
						return "opencascade.trianglebvh";
					}

					void add_file(ifcopenshell::file& file, const ifcopenshell::geom::settings& settings) override {
						auto settings_ = settings;
						settings_.get<ifcopenshell::geom::settings::IteratorOutput>().value = ifcopenshell::geom::settings::TRIANGULATED;
						settings_.get<ifcopenshell::geom::settings::UseWorldCoords>().value = true;

						ifcopenshell::geom::iterator iterator(ifcopenshell::geom::kernels::construct(&file, "opencascade", settings_), settings_, &file, {}, 1);
						if (iterator.initialize()) {
							do {
								auto element = iterator.get();
								add_element(element.get());
							} while (iterator.next());
						}
					}

					void add_element(ifcopenshell::geom::element* element) override {
						auto* triangulation = dynamic_cast<ifcopenshell::geom::triangulation_element*>(element);
						if (!triangulation) {
							throw ifcopenshell::exception("Tree backend 'opencascade.trianglebvh' requires triangulation elements");
						}
						tree_.add_element(triangulation);
					}

					std::vector<ifcopenshell::geom::clash> clash_intersection_many(const std::vector<express::entity>& set_a, const std::vector<express::entity>& set_b, double tolerance, bool check_all) const override {
						return tree_.clash_intersection_many(set_a, set_b, tolerance, check_all);
					}

					std::vector<ifcopenshell::geom::clash> clash_collision_many(const std::vector<express::entity>& set_a, const std::vector<express::entity>& set_b, bool allow_touching) const override {
						return tree_.clash_collision_many(set_a, set_b, allow_touching);
					}

					std::vector<ifcopenshell::geom::clash> clash_clearance_many(const std::vector<express::entity>& set_a, const std::vector<express::entity>& set_b, double clearance, bool check_all) const override {
						return tree_.clash_clearance_many(set_a, set_b, clearance, check_all);
					}

				private:
					ifcopenshell::geom::opencascade_tree tree_;
				};

			}
		}
	}
}

#endif
