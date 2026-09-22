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

#ifndef IFCOPENSHELL_OPENCASCADE_TREE_BREP_H
#define IFCOPENSHELL_OPENCASCADE_TREE_BREP_H

#include "../../kernel_registry.h"
#include "../../tree_registry.h"
#include "../../../ifcparse/exception.h"
#include "tree.h"

namespace ifcopenshell {
	namespace geom {
		namespace trees {
			namespace opencascade_tree_backends {

				inline gp_Pnt make_point(const ifcopenshell::geom::tree_point& point) {
					return gp_Pnt(point[0], point[1], point[2]);
				}

				inline Bnd_Box make_box(const ifcopenshell::geom::tree_box& bounds) {
					Bnd_Box box;
					box.Add(make_point(bounds[0]));
					box.Add(make_point(bounds[1]));
					return box;
				}

				inline express::entity to_product_entity(const express::base& instance) {
					if (!instance) {
						throw ifcopenshell::exception("Instance should be an IfcProduct");
					}

					auto entity = instance.as<express::entity>();
					if (!entity || !instance.declaration().is("IfcProduct")) {
						throw ifcopenshell::exception("Instance should be an IfcProduct");
					}

					return entity;
				}

				inline std::vector<express::base> to_base_vector(const std::vector<express::entity>& entities) {
					return std::vector<express::base>(entities.begin(), entities.end());
				}

				class brep_tree : public ifcopenshell::geom::tree {
				public:
					std::string backend_id() const override {
						return "opencascade.brep";
					}

					void add_file(ifcopenshell::file& file, const ifcopenshell::geom::settings& settings) override {
						auto settings_ = settings;
						settings_.get<ifcopenshell::geom::settings::IteratorOutput>().value = ifcopenshell::geom::settings::NATIVE;
						settings_.get<ifcopenshell::geom::settings::UseWorldCoords>().value = true;
						settings_.get<ifcopenshell::geom::settings::ReorientShells>().value = true;

						ifcopenshell::geom::iterator iterator(ifcopenshell::geom::kernels::construct(&file, "opencascade", settings_), settings_, &file, {}, 1);
						if (iterator.initialize()) {
							do {
								auto element = iterator.get();
								add_element(element.get());
							} while (iterator.next());
						}
					}

					void add_element(ifcopenshell::geom::element* element) override {
						auto* brep = dynamic_cast<ifcopenshell::geom::native_element*>(element);
						if (!brep) {
							throw ifcopenshell::exception("Tree backend 'opencascade.brep' requires native brep elements");
						}
						tree_.add_element(brep);
					}

					std::vector<express::base> select_box(const express::base& entity, bool completely_within, double extend) const override {
						return to_base_vector(tree_.select_box(to_product_entity(entity), completely_within, extend));
					}

					std::vector<express::base> select_box(const ifcopenshell::geom::tree_point& point) const override {
						return to_base_vector(tree_.select_box(make_point(point)));
					}

					std::vector<express::base> select_box(const ifcopenshell::geom::tree_box& bounds, bool completely_within) const override {
						return to_base_vector(tree_.select_box(make_box(bounds), completely_within));
					}

					std::vector<express::base> select(const express::base& entity, bool completely_within, double extend) const override {
						return to_base_vector(tree_.select(to_product_entity(entity), completely_within, extend));
					}

					std::vector<express::base> select(const ifcopenshell::geom::element* element, bool completely_within, double extend) const override {
						auto* brep = dynamic_cast<const ifcopenshell::geom::native_element*>(element);
						if (!brep) {
							throw ifcopenshell::exception("Tree backend 'opencascade.brep' requires brep elements for select()");
						}
						return to_base_vector(tree_.select(brep, completely_within, extend));
					}

					std::vector<express::base> select(const ifcopenshell::geom::tree_point& point, double extend) const override {
						return to_base_vector(tree_.select(make_point(point), extend));
					}

					std::vector<ifcopenshell::geom::ray_intersection_result> select_ray(const ifcopenshell::geom::tree_point& origin, const ifcopenshell::geom::tree_point& direction, double length) const override {
						return tree_.select_ray(make_point(origin), gp_Dir(direction[0], direction[1], direction[2]), length);
					}

					const std::vector<double>& distances() const override {
						return tree_.distances();
					}

					const std::vector<double>& protrusion_distances() const override {
						return tree_.protrusion_distances();
					}

					bool enable_face_styles() const override {
						return tree_.enable_face_styles();
					}

					void enable_face_styles(bool enable) override {
						tree_.enable_face_styles(enable);
					}

					const std::vector<ifcopenshell::geom::taxonomy::style::ptr>& styles() const override {
						return tree_.styles();
					}

				private:
					ifcopenshell::geom::opencascade_tree tree_;
				};

			}
		}
	}
}

#endif
