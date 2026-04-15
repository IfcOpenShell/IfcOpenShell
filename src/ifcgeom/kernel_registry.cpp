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

#include <cstring>
#include <mutex>

namespace {
	std::string kernel_key(const std::string& backend_id) {
		return boost::to_lower_copy(backend_id);
	}

}

void ifcopenshell::geometry::kernels::kernel_registry::bind(const kernel_info& info, create_fn create, const plugin::module& module) {
	entry entry;
	entry.info_ = info;
	entry.create_ = create;
	entry.module_ = module;
	entries_[kernel_key(info.backend_id)] = entry;
}

bool ifcopenshell::geometry::kernels::kernel_registry::has(const std::string& backend_id) const {
	return entries_.find(kernel_key(backend_id)) != entries_.end();
}

std::unique_ptr<ifcopenshell::geometry::kernels::AbstractKernel> ifcopenshell::geometry::kernels::kernel_registry::create(const std::string& backend_id, ifcopenshell::file* file, Settings& settings) const {
	const auto iter = entries_.find(kernel_key(backend_id));
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No geometry kernel registered for " + backend_id);
	}
	return std::unique_ptr<AbstractKernel>(iter->second.create_(file, settings));
}

std::vector<ifcopenshell::geometry::kernels::kernel_info> ifcopenshell::geometry::kernels::kernel_registry::kernels() const {
	std::vector<kernel_info> result;
	for (const auto& pair : entries_) {
		result.push_back(pair.second.info_);
	}
	return result;
}

ifcopenshell::geometry::kernels::kernel_registry& ifcopenshell::geometry::kernels::kernel_registry_instance() {
	static kernel_registry registry;
	static std::once_flag once;
	std::call_once(once, load_kernel_plugins, std::ref(registry));
	return registry;
}

std::unique_ptr<ifcopenshell::geometry::kernels::AbstractKernel> ifcopenshell::geometry::kernels::construct(ifcopenshell::file* file, const std::string& geometry_library, Settings& settings) {
	auto geometry_library_lower = boost::to_lower_copy(geometry_library);
	auto& registry = kernel_registry_instance();

	if (registry.has(geometry_library_lower)) {
		return registry.create(geometry_library_lower, file, settings);
	}

	if (geometry_library_lower.rfind("hybrid-", 0) == 0) {
		geometry_library_lower = geometry_library_lower.substr(strlen("hybrid"));
		std::vector<std::unique_ptr<AbstractKernel>> kernels;
		while (!geometry_library_lower.empty()) {
			if (geometry_library_lower.find("-", 0) == 0) {
				geometry_library_lower = geometry_library_lower.substr(strlen("-"));
			} else {
				throw ifcopenshell::exception("Invalid hybrid kernel " + geometry_library);
			}

			std::string matched_backend_id;
			for (const auto& info : registry.kernels()) {
				const auto backend_id = kernel_key(info.backend_id);
				if (geometry_library_lower.rfind(backend_id, 0) == 0 && backend_id.size() > matched_backend_id.size()) {
					matched_backend_id = backend_id;
				}
			}

			if (matched_backend_id.empty()) {
				throw ifcopenshell::exception("Invalid hybrid kernel " + geometry_library);
			}

			kernels.push_back(registry.create(matched_backend_id, file, settings));
			geometry_library_lower = geometry_library_lower.substr(matched_backend_id.size());
		}

		for (auto it = kernels.begin(); it != kernels.end(); ++it) {
			(**it).propagate_exceptions = it == kernels.begin();
			(**it).partial_success_is_success = it == kernels.end() - 1;
		}

		if (!kernels.empty()) {
			return std::make_unique<HybridKernel>(geometry_library, file, settings, std::move(kernels));
		}
	}

	throw ifcopenshell::exception("No geometry kernel registered for " + geometry_library);
}
