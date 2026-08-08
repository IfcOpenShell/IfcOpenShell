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

#include "kernel_registry.h"

#include "../ifcgeom/kernel_plugin.h"
#include "../ifcgeom/hybrid_kernel.h"
#include "../ifcparse/file.h"

#include <boost/algorithm/string.hpp>

#include <algorithm>
#include <cstring>
#include <iostream>
#include <vector>

namespace ifcopenshell {
namespace plugin {
PLUGIN_API std::filesystem::path add_search_paths_or_default(manager& manager, std::filesystem::path (*default_search_path)());
}
}

namespace {
	constexpr const char* kernel_plugin_prefix = "geometry.kernel.";

	std::string kernel_key(const std::string& backend_id) {
		return boost::to_lower_copy(backend_id);
	}

	bool is_prefix(const std::string& text, const std::string& prefix) {
		return !prefix.empty() && text.rfind(prefix, 0) == 0;
	}

	void register_kernel_module(ifcopenshell::geom::kernels::kernel_registry& registry, const ifcopenshell::plugin::module& module) {
		auto register_plugin = module.get_alias<ifcopenshell::geom::kernels::register_kernel_plugin_fn>(
			ifcopenshell::geom::kernels::kernel_plugin_registration_symbol());
		register_plugin(registry, module);
	}

	struct kernel_match {
		std::string backend_id;
		ifcopenshell::plugin::module module;
		bool has_module = false;
	};

	void consider_kernel_info(kernel_match& match, const std::string& geometry_library_lower, const ifcopenshell::geom::kernels::kernel_info& info) {
		const auto backend_id = kernel_key(info.backend_id);
		if (is_prefix(geometry_library_lower, backend_id) && backend_id.size() > match.backend_id.size()) {
			match.backend_id = backend_id;
			match.has_module = false;
		}
	}

	kernel_match find_kernel_match(ifcopenshell::geom::kernels::kernel_registry& registry, const std::string& geometry_library_lower) {
		kernel_match match;

		for (const auto& info : registry.kernels()) {
			consider_kernel_info(match, geometry_library_lower, info);
		}

		ifcopenshell::plugin::manager manager;
		ifcopenshell::plugin::add_search_paths_or_default(manager, &ifcopenshell::geom::kernels::kernel_plugin_directory);
		for (const auto& path : manager.discover(kernel_plugin_prefix)) {
			ifcopenshell::plugin::module module;
			try {
				module = manager.load(path);
			} catch (const std::exception& e) {
#ifdef IFOPSH_PLUGIN_DEBUG
				std::cerr << "[ifcopenshell.plugin] skip kernel plugin " << path << ": " << e.what() << std::endl;
#else
				static_cast<void>(e);
#endif
				continue;
			}
			if (module.meta().kind_ != ifcopenshell::plugin::kind::kernel) {
				continue;
			}

			ifcopenshell::geom::kernels::kernel_registry plugin_registry;
			register_kernel_module(plugin_registry, module);
			for (const auto& info : plugin_registry.kernels()) {
				const auto backend_id = kernel_key(info.backend_id);
				if (is_prefix(geometry_library_lower, backend_id) && backend_id.size() > match.backend_id.size()) {
					match.backend_id = backend_id;
					match.module = module;
					match.has_module = true;
				}
			}
		}

		if (!match.backend_id.empty() && !registry.has(match.backend_id) && match.has_module) {
			register_kernel_module(registry, match.module);
		}

		return match;
	}
}

void ifcopenshell::geom::kernels::kernel_registry::bind(const kernel_info& info, create_fn create, const plugin::module& module) {
	entry entry;
	entry.info_ = info;
	entry.create_ = create;
	entry.module_ = module;
	entries_[kernel_key(info.backend_id)] = entry;
}

bool ifcopenshell::geom::kernels::kernel_registry::has(const std::string& backend_id) const {
	return entries_.find(kernel_key(backend_id)) != entries_.end();
}

std::unique_ptr<ifcopenshell::geom::kernels::abstract_kernel> ifcopenshell::geom::kernels::kernel_registry::create(const std::string& backend_id, ifcopenshell::file* file, ifcopenshell::geom::settings& settings) const {
	const auto iter = entries_.find(kernel_key(backend_id));
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No geometry kernel registered for " + backend_id);
	}
	return std::unique_ptr<abstract_kernel>(iter->second.create_(file, settings));
}

std::vector<ifcopenshell::geom::kernels::kernel_info> ifcopenshell::geom::kernels::kernel_registry::kernels() const {
	std::vector<kernel_info> result;
	for (const auto& pair : entries_) {
		result.push_back(pair.second.info_);
	}
	return result;
}

ifcopenshell::geom::kernels::kernel_registry& ifcopenshell::geom::kernels::kernel_registry_instance() {
	static kernel_registry registry;
	return registry;
}

std::unique_ptr<ifcopenshell::geom::kernels::abstract_kernel> ifcopenshell::geom::kernels::construct(ifcopenshell::file* file, const std::string& geometry_library, ifcopenshell::geom::settings& settings) {
	auto geometry_library_lower = boost::to_lower_copy(geometry_library);
	auto& registry = kernel_registry_instance();

	if (!registry.has(geometry_library_lower)) {
		load_kernel_plugin(registry, geometry_library_lower);
	}
	if (registry.has(geometry_library_lower)) {
		return registry.create(geometry_library_lower, file, settings);
	}

	if (geometry_library_lower.rfind("hybrid-", 0) == 0) {
		geometry_library_lower = geometry_library_lower.substr(strlen("hybrid"));
		std::vector<std::unique_ptr<abstract_kernel>> kernels;
		while (!geometry_library_lower.empty()) {
			if (geometry_library_lower.find("-", 0) == 0) {
				geometry_library_lower = geometry_library_lower.substr(strlen("-"));
			} else {
				throw ifcopenshell::exception("Invalid hybrid kernel " + geometry_library);
			}

			const auto match = find_kernel_match(registry, geometry_library_lower);
			const auto& matched_backend_id = match.backend_id;

			if (matched_backend_id.empty()) {
				throw ifcopenshell::exception("Invalid hybrid kernel; no match for prefix of " + geometry_library_lower);
			}

			kernels.push_back(registry.create(matched_backend_id, file, settings));
			geometry_library_lower = geometry_library_lower.substr(matched_backend_id.size());
		}

		for (auto it = kernels.begin(); it != kernels.end(); ++it) {
			(**it).propagate_exceptions = it == kernels.begin();
			(**it).partial_success_is_success = it == kernels.end() - 1;
		}

		if (!kernels.empty()) {
			return std::make_unique<hybrid_kernel>(geometry_library, file, settings, std::move(kernels));
		}
	}

	throw ifcopenshell::exception("No geometry kernel registered for " + geometry_library);
}
