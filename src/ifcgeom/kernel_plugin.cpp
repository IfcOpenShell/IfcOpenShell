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

#include "kernel_plugin.h"

#include <stdexcept>

namespace {
	constexpr const char* kernel_plugin_prefix = "geometry.kernel.";
}

const char* ifcopenshell::geometry::kernels::kernel_plugin_registration_symbol() {
	return "ifcopenshell_register_kernel_plugin_v1";
}

ifcopenshell::plugin::metadata ifcopenshell::geometry::kernels::kernel_plugin_metadata(const std::string& plugin_name) {
	plugin::metadata metadata;
	metadata.kind_ = plugin::kind::kernel;
	metadata.id = kernel_plugin_prefix + plugin_name;
	return metadata;
}

std::filesystem::path ifcopenshell::geometry::kernels::kernel_plugin_directory() {
	return plugin::module_directory(reinterpret_cast<const void*>(&ifcopenshell::geometry::kernels::load_kernel_plugins));
}

void ifcopenshell::geometry::kernels::load_kernel_plugins(kernel_registry& registry) {
	plugin::manager manager;
	manager.add_search_path(kernel_plugin_directory());

	for (const auto& path : manager.discover(kernel_plugin_prefix)) {
		auto module = manager.load(path);
		if (module.meta().kind_ != plugin::kind::kernel) {
			continue;
		}

		auto register_plugin = module.get_alias<register_kernel_plugin_fn>(kernel_plugin_registration_symbol());
		register_plugin(registry, module);
	}
}
