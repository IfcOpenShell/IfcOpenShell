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

#ifndef IFCOPENSHELL_OPENCASCADE_TREE_BACKENDS_H
#define IFCOPENSHELL_OPENCASCADE_TREE_BACKENDS_H

#include "../../kernel_registry.h"
#include "../../tree_registry.h"
#include "../../../ifcparse/exception.h"
#include "IfcGeomTree.h"

namespace ifcopenshell {
	namespace geometry {
		namespace trees {
			namespace opencascade_tree_backends {

				inline gp_Pnt make_point(const IfcGeom::tree_point& point) {
					return gp_Pnt(point[0], point[1], point[2]);
				}

				inline Bnd_Box make_box(const IfcGeom::tree_box& bounds) {
					Bnd_Box box;
					box.Add(make_point(bounds[0]));
					box.Add(make_point(bounds[1]));
					return box;
				}

				class brep_tree : public abstract_tree {
				public:
					std::string_view backend_id() const override {
						return "opencascade.brep";
					}

					void add_file(ifcopenshell::file& file, const ifcopenshell::geometry::Settings& settings) override {
						auto settings_ = settings;
						settings_.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;
						settings_.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = true;
						settings_.get<ifcopenshell::geometry::settings::ReorientShells>().value = true;

						IfcGeom::Iterator iterator(ifcopenshell::geometry::kernels::construct(&file, "opencascade", settings_), settings_, &file, {}, 1);
						if (iterator.initialize()) {
							do {
								add_element(iterator.get());
							} while (iterator.next());
						}
					}

					void add_element(IfcGeom::Element* element) override {
						auto* brep = dynamic_cast<IfcGeom::BRepElement*>(element);
						if (!brep) {
							throw ifcopenshell::exception("Tree backend 'opencascade.brep' requires native BRep elements");
						}
						tree_.add_element(brep);
					}

					std::vector<express::Entity> select_box(const express::Entity& entity, bool completely_within, double extend) const override {
						return tree_.select_box(entity, completely_within, extend);
					}

					std::vector<express::Entity> select_box(const IfcGeom::tree_point& point) const override {
						return tree_.select_box(make_point(point));
					}

					std::vector<express::Entity> select_box(const IfcGeom::tree_box& bounds, bool completely_within) const override {
						return tree_.select_box(make_box(bounds), completely_within);
					}

					std::vector<express::Entity> select(const express::Entity& entity, bool completely_within, double extend) const override {
						return tree_.select(entity, completely_within, extend);
					}

					std::vector<express::Entity> select(const IfcGeom::Element* element, bool completely_within, double extend) const override {
						auto* brep = dynamic_cast<const IfcGeom::BRepElement*>(element);
						if (!brep) {
							throw ifcopenshell::exception("Tree backend 'opencascade.brep' requires BRep elements for select()");
						}
						return tree_.select(brep, completely_within, extend);
					}

					std::vector<express::Entity> select(const IfcGeom::tree_point& point, double extend) const override {
						return tree_.select(make_point(point), extend);
					}

					std::vector<IfcGeom::ray_intersection_result> select_ray(const IfcGeom::tree_point& origin, const IfcGeom::tree_point& direction, double length) const override {
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

					const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& styles() const override {
						return tree_.styles();
					}

				private:
					IfcGeom::opencascade_tree tree_;
				};

				class trianglebvh_tree : public abstract_tree {
				public:
					std::string_view backend_id() const override {
						return "opencascade.trianglebvh";
					}

					void add_file(ifcopenshell::file& file, const ifcopenshell::geometry::Settings& settings) override {
						auto settings_ = settings;
						settings_.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::TRIANGULATED;
						settings_.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = true;

						IfcGeom::Iterator iterator(ifcopenshell::geometry::kernels::construct(&file, "opencascade", settings_), settings_, &file, {}, 1);
						if (iterator.initialize()) {
							do {
								add_element(iterator.get());
							} while (iterator.next());
						}
					}

					void add_element(IfcGeom::Element* element) override {
						auto* triangulation = dynamic_cast<IfcGeom::TriangulationElement*>(element);
						if (!triangulation) {
							throw ifcopenshell::exception("Tree backend 'opencascade.trianglebvh' requires triangulation elements");
						}
						tree_.add_element(triangulation);
					}

					std::vector<IfcGeom::clash> clash_intersection_many(const std::vector<express::Entity>& set_a, const std::vector<express::Entity>& set_b, double tolerance, bool check_all) const override {
						return tree_.clash_intersection_many(set_a, set_b, tolerance, check_all);
					}

					std::vector<IfcGeom::clash> clash_collision_many(const std::vector<express::Entity>& set_a, const std::vector<express::Entity>& set_b, bool allow_touching) const override {
						return tree_.clash_collision_many(set_a, set_b, allow_touching);
					}

					std::vector<IfcGeom::clash> clash_clearance_many(const std::vector<express::Entity>& set_a, const std::vector<express::Entity>& set_b, double clearance, bool check_all) const override {
						return tree_.clash_clearance_many(set_a, set_b, clearance, check_all);
					}

				private:
					IfcGeom::opencascade_tree tree_;
				};

			}
		}
	}
}

#endif
