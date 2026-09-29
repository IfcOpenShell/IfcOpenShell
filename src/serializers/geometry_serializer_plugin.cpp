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

#include "geometry_serializer_plugin.h"

#include <boost/algorithm/string/case_conv.hpp>

#include <mutex>
#include <set>

namespace ifcopenshell {
namespace plugin {
PLUGIN_API std::filesystem::path add_search_paths_or_default(manager& manager, std::filesystem::path (*default_search_path)());
}
}

namespace {

std::string geometry_serializer_plugin_prefix(const std::string& format = std::string()) {
	const auto format_lower = boost::to_lower_copy(format);
	return format_lower.empty() ? "geometry_" : "geometry_" + format_lower;
}

std::string geometry_serializer_key(const std::string& extension) {
	if (extension.empty()) {
		return extension;
	}

	auto key = boost::to_lower_copy(extension);
	if (key.front() != '.') {
		key.insert(key.begin(), '.');
	}
	return key;
}

std::string geometry_serializer_format_from_extension(const std::string& extension) {
	auto key = geometry_serializer_key(extension);
	if (!key.empty() && key.front() == '.') {
		key.erase(key.begin());
	}
	return key;
}

void add_geometry_serializer_search_paths(ifcopenshell::plugin::manager& manager) {
	const auto directory = ifcopenshell::plugin::add_search_paths_or_default(
		manager, &ifcopenshell::serializers::geometry_serializer_plugin_directory);
	if (directory.empty()) {
		return;
	}

	const auto sibling_directory = directory.parent_path().parent_path() / "serializers" / directory.filename();
	if (sibling_directory != directory && std::filesystem::exists(sibling_directory)) {
		manager.add_search_path(sibling_directory);
	}
}

}

void ifcopenshell::serializers::geometry_serializer_registry::bind(const geometry_serializer_info& info, create_fn create, configure_fn configure, const plugin::module& module) {
	entry entry;
	entry.info_ = info;
	entry.info_.format = boost::to_lower_copy(entry.info_.format);
	if (entry.info_.name.empty() && !entry.info_.format.empty()) {
		entry.info_.name = boost::to_upper_copy(entry.info_.format);
	}
	if (entry.info_.description.empty()) {
		entry.info_.description = entry.info_.name;
	}
	entry.create_ = create;
	entry.configure_ = configure;
	entry.module_ = module.meta().id.empty() ? plugin::module(geometry_serializer_plugin_metadata(entry.info_.format)) : module;

	if (entry.info_.extensions.empty() && !entry.info_.format.empty()) {
		entry.info_.extensions.push_back("." + entry.info_.format);
	}

	for (auto& extension : entry.info_.extensions) {
		extension = geometry_serializer_key(extension);
		entries_[extension] = entry;
	}
}

bool ifcopenshell::serializers::geometry_serializer_registry::has(const std::string& extension) const {
	const auto key = geometry_serializer_key(extension);
	if (entries_.find(key) == entries_.end()) {
		load_geometry_serializer_plugin(const_cast<geometry_serializer_registry&>(*this), extension);
	}
	return entries_.find(key) != entries_.end();
}

const ifcopenshell::serializers::geometry_serializer_info* ifcopenshell::serializers::geometry_serializer_registry::find(const std::string& extension) const {
	const auto key = geometry_serializer_key(extension);
	if (entries_.find(key) == entries_.end()) {
		load_geometry_serializer_plugin(const_cast<geometry_serializer_registry&>(*this), extension);
	}
	const auto iter = entries_.find(key);
	if (iter == entries_.end()) {
		return nullptr;
	}
	return &iter->second.info_;
}

void ifcopenshell::serializers::geometry_serializer_registry::configure(const std::string& extension, geometry_serializer_context& context) const {
	const auto key = geometry_serializer_key(extension);
	if (entries_.find(key) == entries_.end()) {
		load_geometry_serializer_plugin(const_cast<geometry_serializer_registry&>(*this), extension);
	}
	const auto iter = entries_.find(key);
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No geometry serializer registered for " + extension);
	}
	if (iter->second.configure_) {
		iter->second.configure_(context);
	}
}

std::shared_ptr<ifcopenshell::geom::geometry_serializer> ifcopenshell::serializers::geometry_serializer_registry::create(const std::string& extension, const geometry_serializer_context& context) const {
	const auto key = geometry_serializer_key(extension);
	if (entries_.find(key) == entries_.end()) {
		load_geometry_serializer_plugin(const_cast<geometry_serializer_registry&>(*this), extension);
	}
	const auto iter = entries_.find(key);
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No geometry serializer registered for " + extension);
	}
	return iter->second.create_(context);
}

std::vector<ifcopenshell::serializers::geometry_serializer_info> ifcopenshell::serializers::geometry_serializer_registry::serializers() const {
	std::vector<geometry_serializer_info> result;
	std::set<std::string> seen_formats;
	for (const auto& pair : entries_) {
		if (!seen_formats.insert(pair.second.info_.format).second) {
			continue;
		}
		result.push_back(pair.second.info_);
	}

	ifcopenshell::plugin::manager manager;
	add_geometry_serializer_search_paths(manager);
	for (const auto& path : manager.discover(geometry_serializer_plugin_prefix())) {
		ifcopenshell::plugin::module module;
		try {
			module = manager.load(path);
		} catch (const std::exception& e) {
			ifcopenshell::logger::root().error(e);
			continue;
		}
		if (module.meta().kind_ != ifcopenshell::plugin::kind::geometry_serializer) {
			continue;
		}

		geometry_serializer_registry plugin_registry;
		auto register_plugin = module.get_alias<register_geometry_serializer_plugin_fn>(geometry_serializer_plugin_registration_symbol());
		register_plugin(plugin_registry, module);
		for (const auto& pair : plugin_registry.entries_) {
			if (!seen_formats.insert(pair.second.info_.format).second) {
				continue;
			}
			result.push_back(pair.second.info_);
		}
	}
	return result;
}

const char* ifcopenshell::serializers::geometry_serializer_plugin_registration_symbol() {
	return "ifcopenshell_register_geometry_serializer_plugin_v1";
}

ifcopenshell::plugin::metadata ifcopenshell::serializers::geometry_serializer_plugin_metadata(const std::string& format) {
	plugin::metadata metadata;
	metadata.kind_ = plugin::kind::geometry_serializer;
	metadata.id = geometry_serializer_plugin_prefix(format);
	metadata.format = boost::to_lower_copy(format);
	return metadata;
}

std::filesystem::path ifcopenshell::serializers::geometry_serializer_plugin_directory() {
	return plugin::module_directory(reinterpret_cast<const void*>(&ifcopenshell::serializers::geometry_serializer_plugin_directory));
}

void ifcopenshell::serializers::load_geometry_serializer_plugins(geometry_serializer_registry& registry) {
	ifcopenshell::plugin::manager manager;
	add_geometry_serializer_search_paths(manager);

	for (const auto& path : manager.discover(geometry_serializer_plugin_prefix())) {
        ifcopenshell::plugin::module module;
        try {
			module = manager.load(path);
		} catch (const std::exception& e) {
            ifcopenshell::logger::root().error(e);
			continue;
		}
		if (module.meta().kind_ != ifcopenshell::plugin::kind::geometry_serializer) {
			continue;
		}

		auto register_plugin = module.get_alias<register_geometry_serializer_plugin_fn>(geometry_serializer_plugin_registration_symbol());
		register_plugin(registry, module);
	}
}

bool ifcopenshell::serializers::load_geometry_serializer_plugin(geometry_serializer_registry& registry, const std::string& extension) {
	const auto format = geometry_serializer_format_from_extension(extension);
	if (format.empty()) {
		return false;
	}

	ifcopenshell::plugin::manager manager;
	add_geometry_serializer_search_paths(manager);

	for (const auto& path : manager.discover_exact(geometry_serializer_plugin_prefix(format))) {
		ifcopenshell::plugin::module module;
		try {
			module = manager.load(path);
		} catch (const std::exception& e) {
			ifcopenshell::logger::root().error(e);
			continue;
		}
		if (module.meta().kind_ != ifcopenshell::plugin::kind::geometry_serializer ||
			module.meta().format != format) {
			continue;
		}

		auto register_plugin = module.get_alias<register_geometry_serializer_plugin_fn>(geometry_serializer_plugin_registration_symbol());
		register_plugin(registry, module);
		return registry.entries_.find(geometry_serializer_key(extension)) != registry.entries_.end();
	}

	return false;
}

ifcopenshell::serializers::geometry_serializer_registry& ifcopenshell::serializers::geometry_serializer_registry_instance() {
	static geometry_serializer_registry registry;
	return registry;
}
