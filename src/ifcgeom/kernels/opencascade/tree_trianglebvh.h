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

				inline std::vector<express::entity> to_product_entities(const std::vector<express::base>& instances) {
					std::vector<express::entity> entities;
					entities.reserve(instances.size());

					for (const auto& instance : instances) {
						if (!instance) {
							throw ifcopenshell::exception("All instances should be of type IfcProduct");
						}

						auto entity = instance.as<express::entity>();
						if (!entity || !instance.declaration().is("IfcProduct")) {
							throw ifcopenshell::exception("All instances should be of type IfcProduct");
						}
						entities.push_back(entity);
					}

					return entities;
				}

				class trianglebvh_tree : public ifcopenshell::geom::tree {
				public:
					std::string backend_id() const override {
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

					std::vector<ifcopenshell::geom::clash> clash_intersection_many(const std::vector<express::base>& set_a, const std::vector<express::base>& set_b, double tolerance, bool check_all) const override {
						return tree_.clash_intersection_many(to_product_entities(set_a), to_product_entities(set_b), tolerance, check_all);
					}

					std::vector<ifcopenshell::geom::clash> clash_collision_many(const std::vector<express::base>& set_a, const std::vector<express::base>& set_b, bool allow_touching) const override {
						return tree_.clash_collision_many(to_product_entities(set_a), to_product_entities(set_b), allow_touching);
					}

					std::vector<ifcopenshell::geom::clash> clash_clearance_many(const std::vector<express::base>& set_a, const std::vector<express::base>& set_b, double clearance, bool check_all) const override {
						return tree_.clash_clearance_many(to_product_entities(set_a), to_product_entities(set_b), clearance, check_all);
					}

				private:
					ifcopenshell::geom::opencascade_tree tree_;
				};

			}
		}
	}
}

#endif
