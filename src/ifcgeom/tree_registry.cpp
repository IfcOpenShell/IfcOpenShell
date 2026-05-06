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

#include "tree_registry.h"

#include "tree_plugin.h"
#include "../ifcparse/exception.h"

#include <boost/algorithm/string.hpp>

namespace {
	std::string tree_key(const std::string& backend_id) {
		return boost::to_lower_copy(backend_id);
	}

	[[noreturn]] void unsupported_tree_operation(const std::string& backend_id, const std::string& operation) {
		throw ifcopenshell::exception("Tree backend '" + backend_id + "' does not support " + operation);
	}
}

ifcopenshell::geometry::trees::abstract_tree::~abstract_tree() = default;

void ifcopenshell::geometry::trees::abstract_tree::add_file(ifcopenshell::file&, const ifcopenshell::geometry::Settings&) {
	unsupported_tree_operation(std::string(backend_id()), "add_file()");
}

void ifcopenshell::geometry::trees::abstract_tree::add_element(IfcGeom::Element*) {
	unsupported_tree_operation(std::string(backend_id()), "add_element()");
}

std::vector<express::Entity> ifcopenshell::geometry::trees::abstract_tree::select_box(const express::Entity&, bool, double) const {
	unsupported_tree_operation(std::string(backend_id()), "select_box(entity)");
}

std::vector<express::Entity> ifcopenshell::geometry::trees::abstract_tree::select_box(const IfcGeom::tree_point&) const {
	unsupported_tree_operation(std::string(backend_id()), "select_box(point)");
}

std::vector<express::Entity> ifcopenshell::geometry::trees::abstract_tree::select_box(const IfcGeom::tree_box&, bool) const {
	unsupported_tree_operation(std::string(backend_id()), "select_box(bounds)");
}

std::vector<express::Entity> ifcopenshell::geometry::trees::abstract_tree::select(const express::Entity&, bool, double) const {
	unsupported_tree_operation(std::string(backend_id()), "select(entity)");
}

std::vector<express::Entity> ifcopenshell::geometry::trees::abstract_tree::select(const IfcGeom::Element*, bool, double) const {
	unsupported_tree_operation(std::string(backend_id()), "select(element)");
}

std::vector<express::Entity> ifcopenshell::geometry::trees::abstract_tree::select(const IfcGeom::tree_point&, double) const {
	unsupported_tree_operation(std::string(backend_id()), "select(point)");
}

std::vector<IfcGeom::ray_intersection_result> ifcopenshell::geometry::trees::abstract_tree::select_ray(const IfcGeom::tree_point&, const IfcGeom::tree_point&, double) const {
	unsupported_tree_operation(std::string(backend_id()), "select_ray()");
}

std::vector<IfcGeom::clash> ifcopenshell::geometry::trees::abstract_tree::clash_intersection_many(const std::vector<express::Entity>&, const std::vector<express::Entity>&, double, bool) const {
	unsupported_tree_operation(std::string(backend_id()), "clash_intersection_many()");
}

std::vector<IfcGeom::clash> ifcopenshell::geometry::trees::abstract_tree::clash_collision_many(const std::vector<express::Entity>&, const std::vector<express::Entity>&, bool) const {
	unsupported_tree_operation(std::string(backend_id()), "clash_collision_many()");
}

std::vector<IfcGeom::clash> ifcopenshell::geometry::trees::abstract_tree::clash_clearance_many(const std::vector<express::Entity>&, const std::vector<express::Entity>&, double, bool) const {
	unsupported_tree_operation(std::string(backend_id()), "clash_clearance_many()");
}

const std::vector<double>& ifcopenshell::geometry::trees::abstract_tree::distances() const {
	unsupported_tree_operation(std::string(backend_id()), "distances()");
}

const std::vector<double>& ifcopenshell::geometry::trees::abstract_tree::protrusion_distances() const {
	unsupported_tree_operation(std::string(backend_id()), "protrusion_distances()");
}

bool ifcopenshell::geometry::trees::abstract_tree::enable_face_styles() const {
	unsupported_tree_operation(std::string(backend_id()), "enable_face_styles()");
}

void ifcopenshell::geometry::trees::abstract_tree::enable_face_styles(bool) {
	unsupported_tree_operation(std::string(backend_id()), "enable_face_styles(bool)");
}

const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& ifcopenshell::geometry::trees::abstract_tree::styles() const {
	unsupported_tree_operation(std::string(backend_id()), "styles()");
}

#ifdef WITH_HDF5
void ifcopenshell::geometry::trees::abstract_tree::write_h5() {
	unsupported_tree_operation(std::string(backend_id()), "write_h5()");
}
#endif

void ifcopenshell::geometry::trees::tree_registry::bind(const tree_info& info, create_fn create, const plugin::module& module) {
	entry entry;
	entry.info_ = info;
	entry.create_ = create;
	entry.module_ = module;
	entries_[tree_key(info.backend_id)] = entry;
}

bool ifcopenshell::geometry::trees::tree_registry::has(const std::string& backend_id) const {
	return entries_.find(tree_key(backend_id)) != entries_.end();
}

std::unique_ptr<ifcopenshell::geometry::trees::abstract_tree> ifcopenshell::geometry::trees::tree_registry::create(const std::string& backend_id) const {
	const auto iter = entries_.find(tree_key(backend_id));
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No geometry tree registered for " + backend_id);
	}
	return std::unique_ptr<abstract_tree>(iter->second.create_());
}

ifcopenshell::geometry::trees::tree_registry& ifcopenshell::geometry::trees::tree_registry_instance() {
	static tree_registry registry;
	return registry;
}

std::unique_ptr<ifcopenshell::geometry::trees::abstract_tree> ifcopenshell::geometry::trees::construct(const std::string& backend_id) {
	auto& registry = tree_registry_instance();
	if (!registry.has(backend_id)) {
		load_tree_plugin(registry, backend_id);
	}
	return registry.create(backend_id);
}
