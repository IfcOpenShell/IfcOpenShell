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

#include <boost/algorithm/string/case_conv.hpp>

#ifdef __EMSCRIPTEN__
#include <dlfcn.h>
#endif

#include <algorithm>
#include <stdexcept>

namespace ifcopenshell {
namespace plugin {
PLUGIN_API std::filesystem::path add_search_paths_or_default(manager& manager, std::filesystem::path (*default_search_path)());
}
}

namespace {
	constexpr const char* kernel_plugin_prefix = "geometry_kernel_";

	std::string kernel_plugin_name(const std::string& backend_id) {
		auto name = boost::to_lower_copy(backend_id);
		name.erase(std::remove(name.begin(), name.end(), '-'), name.end());
		return name;
	}
}

const char* ifcopenshell::geom::kernels::kernel_plugin_registration_symbol() {
	return "ifcopenshell_register_kernel_plugin_v1";
}

ifcopenshell::plugin::metadata ifcopenshell::geom::kernels::kernel_plugin_metadata(const std::string& plugin_name) {
	plugin::metadata metadata;
	metadata.kind_ = plugin::kind::kernel;
	metadata.id = kernel_plugin_prefix + plugin_name;
	return metadata;
}

std::filesystem::path ifcopenshell::geom::kernels::kernel_plugin_directory() {
	return plugin::module_directory(reinterpret_cast<const void*>(&ifcopenshell::geom::kernels::load_kernel_plugins));
}

void ifcopenshell::geom::kernels::load_kernel_plugins(kernel_registry& registry) {
	plugin::manager manager;
	plugin::add_search_paths_or_default(manager, &kernel_plugin_directory);

	for (const auto& path : manager.discover(kernel_plugin_prefix)) {
		auto module = manager.load(path);
		if (module.meta().kind_ != plugin::kind::kernel) {
			continue;
		}

		auto register_plugin = module.get_alias<register_kernel_plugin_fn>(kernel_plugin_registration_symbol());
		register_plugin(registry, module);
	}
}

bool ifcopenshell::geom::kernels::load_kernel_plugin(kernel_registry& registry, const std::string& backend_id) {
	plugin::manager manager;
	plugin::add_search_paths_or_default(manager, &kernel_plugin_directory);

	const auto plugin_name = kernel_plugin_name(backend_id);
	const auto basename = std::string(kernel_plugin_prefix) + plugin_name;

#ifdef __EMSCRIPTEN__
	using emscripten_register_fn = void (*)(kernel_registry*);
	const auto emscripten_symbol = std::string("ifcopenshell_emscripten_register_kernel_") + plugin_name;
	if (auto* register_ptr = dlsym(RTLD_DEFAULT, emscripten_symbol.c_str())) {
		union {
			void* ptr;
			emscripten_register_fn fn;
		} register_symbol;
		register_symbol.ptr = register_ptr;
		if (register_symbol.fn) {
			register_symbol.fn(&registry);
			return registry.has(backend_id);
		}
	}
#endif

	for (const auto& path : manager.discover_exact(basename)) {
		auto module = manager.load(path);
		if (module.meta().kind_ != plugin::kind::kernel ||
			module.meta().id != basename) {
			continue;
		}

		auto register_plugin = module.get_alias<register_kernel_plugin_fn>(kernel_plugin_registration_symbol());
		register_plugin(registry, module);
		return registry.has(backend_id);
	}

	return false;
}
