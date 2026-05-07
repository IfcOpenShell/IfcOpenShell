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

#include "tree_plugin.h"

#include <boost/algorithm/string/case_conv.hpp>

namespace ifcopenshell {
namespace plugin {
PLUGIN_API std::filesystem::path add_search_paths_or_default(manager& manager, std::filesystem::path (*default_search_path)());
}
}

namespace {
	constexpr const char* tree_plugin_prefix = "geometry.tree.";
}

const char* ifcopenshell::geometry::trees::tree_plugin_registration_symbol() {
	return "ifcopenshell_register_tree_plugin_v1";
}

ifcopenshell::plugin::metadata ifcopenshell::geometry::trees::tree_plugin_metadata(const std::string& plugin_name) {
	plugin::metadata metadata;
	metadata.kind_ = plugin::kind::tree;
	metadata.id = std::string(tree_plugin_prefix) + plugin_name;
	return metadata;
}

std::filesystem::path ifcopenshell::geometry::trees::tree_plugin_directory() {
	return plugin::module_directory(reinterpret_cast<const void*>(&ifcopenshell::geometry::trees::load_tree_plugins));
}

void ifcopenshell::geometry::trees::load_tree_plugins(tree_registry& registry) {
	plugin::manager manager;
	plugin::add_search_paths_or_default(manager, &tree_plugin_directory);

	for (const auto& path : manager.discover(tree_plugin_prefix)) {
		auto module = manager.load(path);
		if (module.meta().kind_ != plugin::kind::tree) {
			continue;
		}

		auto register_plugin = module.get_alias<register_tree_plugin_fn>(tree_plugin_registration_symbol());
		register_plugin(registry, module);
	}
}

bool ifcopenshell::geometry::trees::load_tree_plugin(tree_registry& registry, const std::string& backend_id) {
	plugin::manager manager;
	plugin::add_search_paths_or_default(manager, &tree_plugin_directory);

	const auto plugin_name = boost::to_lower_copy(backend_id);
	const auto basename = std::string(tree_plugin_prefix) + plugin_name;

	for (const auto& path : manager.discover_exact(basename)) {
		auto module = manager.load(path);
		if (module.meta().kind_ != plugin::kind::tree ||
			module.meta().id != basename) {
			continue;
		}

		auto register_plugin = module.get_alias<register_tree_plugin_fn>(tree_plugin_registration_symbol());
		register_plugin(registry, module);
		return registry.has(backend_id);
	}

	return false;
}
