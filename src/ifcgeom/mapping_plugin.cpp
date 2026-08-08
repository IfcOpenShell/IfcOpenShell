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

#include "mapping_plugin.h"

#include <boost/algorithm/string/case_conv.hpp>

namespace ifcopenshell {
namespace plugin {
PLUGIN_API std::filesystem::path add_search_paths_or_default(manager& manager, std::filesystem::path (*default_search_path)());
}
}

namespace {
	constexpr const char* mapping_plugin_prefix = "geometry.mapping.";
}

const char* ifcopenshell::geom::impl::mapping_plugin_registration_symbol() {
	return "ifcopenshell_register_mapping_plugin_v1";
}

ifcopenshell::plugin::metadata ifcopenshell::geom::impl::mapping_plugin_metadata(const std::string& schema_name) {
	plugin::metadata metadata;
	metadata.kind_ = plugin::kind::mapping;
	metadata.id = mapping_plugin_prefix + boost::to_lower_copy(schema_name);
	metadata.schema = boost::to_upper_copy(schema_name);
	return metadata;
}

std::filesystem::path ifcopenshell::geom::impl::mapping_plugin_directory() {
	return plugin::module_directory(reinterpret_cast<const void*>(&ifcopenshell::geom::impl::load_mapping_plugins));
}

void ifcopenshell::geom::impl::load_mapping_plugins(mapping_registry& registry) {
	plugin::manager manager;
	plugin::add_search_paths_or_default(manager, &mapping_plugin_directory);

	for (const auto& path : manager.discover(mapping_plugin_prefix)) {
		auto module = manager.load(path);
		if (module.meta().kind_ != plugin::kind::mapping) {
			continue;
		}

		auto register_plugin = module.get_alias<register_mapping_plugin_fn>(mapping_plugin_registration_symbol());
		register_plugin(registry, module);
	}
}

bool ifcopenshell::geom::impl::load_mapping_plugin(mapping_registry& registry, const std::string& schema_name) {
	plugin::manager manager;
	plugin::add_search_paths_or_default(manager, &mapping_plugin_directory);

	const auto expected_schema = boost::to_upper_copy(schema_name);
	const auto basename = std::string(mapping_plugin_prefix) + boost::to_lower_copy(schema_name);

	for (const auto& path : manager.discover_exact(basename)) {
		auto module = manager.load(path);
		if (module.meta().kind_ != plugin::kind::mapping ||
			module.meta().schema != expected_schema) {
			continue;
		}

		auto register_plugin = module.get_alias<register_mapping_plugin_fn>(mapping_plugin_registration_symbol());
		register_plugin(registry, module);
		return true;
	}

	return false;
}
