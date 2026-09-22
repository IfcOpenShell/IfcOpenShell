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
}

void ifcopenshell::geom::trees::tree_registry::bind(const tree_info& info, create_fn create, const plugin::module& module) {
	entry entry;
	entry.info_ = info;
	entry.create_ = create;
	entry.module_ = module;
	entries_[tree_key(info.backend_id)] = entry;
}

bool ifcopenshell::geom::trees::tree_registry::has(const std::string& backend_id) const {
	return entries_.find(tree_key(backend_id)) != entries_.end();
}

std::unique_ptr<ifcopenshell::geom::tree> ifcopenshell::geom::trees::tree_registry::create(const std::string& backend_id) const {
	const auto iter = entries_.find(tree_key(backend_id));
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No geometry tree registered for " + backend_id);
	}
	return std::unique_ptr<ifcopenshell::geom::tree>(iter->second.create_());
}

ifcopenshell::geom::trees::tree_registry& ifcopenshell::geom::trees::tree_registry_instance() {
	static tree_registry registry;
	return registry;
}

std::unique_ptr<ifcopenshell::geom::tree> ifcopenshell::geom::trees::construct(const std::string& backend_id) {
	auto& registry = tree_registry_instance();
	if (!registry.has(backend_id)) {
		load_tree_plugin(registry, backend_id);
	}
	return registry.create(backend_id);
}
