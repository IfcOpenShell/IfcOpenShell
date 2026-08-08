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

#include "document_serializer_plugin.h"

#include <boost/algorithm/string/case_conv.hpp>

#include "../ifcparse/logger.h"

#include <mutex>
#include <set>

namespace ifcopenshell {
namespace plugin {
PLUGIN_API std::filesystem::path add_search_paths_or_default(manager& manager, std::filesystem::path (*default_search_path)());
}
}

namespace {

std::string document_serializer_key(const std::string& format) {
	if (format.empty()) {
		return format;
	}

	auto key = boost::to_lower_copy(format);
	if (key.front() == '.') {
		key.erase(key.begin());
	}
	return key;
}

std::string document_serializer_schema_key(const std::string& schema_name) {
	return boost::to_upper_copy(schema_name);
}

std::string document_serializer_plugin_prefix(const std::string& format = std::string()) {
	const auto format_key = document_serializer_key(format);
	return format_key.empty() ? "document." : "document." + format_key;
}

void add_document_serializer_search_paths(ifcopenshell::plugin::manager& manager) {
	const auto directory = ifcopenshell::plugin::add_search_paths_or_default(
		manager, &ifcopenshell::serializers::document_serializer_plugin_directory);
	if (directory.empty()) {
		return;
	}

	const auto sibling_directory = directory.parent_path().parent_path() / "serializers" / directory.filename();
	if (sibling_directory != directory && std::filesystem::exists(sibling_directory)) {
		manager.add_search_path(sibling_directory);
	}
}

}

void ifcopenshell::serializers::document_serializer_registry::bind(const document_serializer_info& info, create_fn create, const plugin::module& module) {
	entry entry;
	entry.info_ = info;
	entry.info_.format = document_serializer_key(entry.info_.format);
	if (entry.info_.name.empty() && !entry.info_.format.empty()) {
		entry.info_.name = boost::to_upper_copy(entry.info_.format);
	}
	if (entry.info_.description.empty()) {
		entry.info_.description = entry.info_.name;
	}
	entry.info_.schema_name = document_serializer_schema_key(entry.info_.schema_name);
	entry.create_ = create;
	entry.module_ = module.meta().id.empty() ? plugin::module(document_serializer_plugin_metadata(entry.info_.format, entry.info_.schema_name)) : module;

	entries_[entry.info_.format].push_back(entry);
}

const ifcopenshell::serializers::document_serializer_registry::entry* ifcopenshell::serializers::document_serializer_registry::find_entry_(const std::string& format, const std::string& schema_name) const {
	const auto format_key = document_serializer_key(format);
	const auto iter = entries_.find(format_key);
	if (iter == entries_.end()) {
		return nullptr;
	}

	const auto schema_key = document_serializer_schema_key(schema_name);
	const entry* fallback = nullptr;

	for (const auto& candidate : iter->second) {
		if (candidate.info_.schema_name.empty()) {
			if (!fallback) {
				fallback = &candidate;
			}
			continue;
		}
		if (!schema_key.empty() && candidate.info_.schema_name == schema_key) {
			return &candidate;
		}
		if (schema_key.empty() && !fallback) {
			fallback = &candidate;
		}
	}

	return fallback;
}

const ifcopenshell::serializers::document_serializer_info* ifcopenshell::serializers::document_serializer_registry::find(const std::string& format, const std::string& schema_name) const {
	auto* registry = const_cast<document_serializer_registry*>(this);
	const auto* entry = find_entry_(format, schema_name);
	if (!entry) {
		load_document_serializer_plugin(*registry, format, schema_name);
		entry = find_entry_(format, schema_name);
	}
	return entry ? &entry->info_ : nullptr;
}

boost::shared_ptr<serializer> ifcopenshell::serializers::document_serializer_registry::create(const std::string& format, const document_serializer_context& context) const {
	const auto schema_name = !context.schema_name.empty() ? context.schema_name :
		(context.file ? context.file->schema()->name() : std::string());
	auto* registry = const_cast<document_serializer_registry*>(this);
	const auto* entry = find_entry_(format, schema_name);
	if (!entry) {
		load_document_serializer_plugin(*registry, format, schema_name);
		entry = find_entry_(format, schema_name);
	}
	if (!entry) {
		throw ifcopenshell::exception("No document serializer registered for " + format + (schema_name.empty() ? std::string() : " and schema " + schema_name));
	}
	return entry->create_(context);
}

std::vector<ifcopenshell::serializers::document_serializer_info> ifcopenshell::serializers::document_serializer_registry::serializers() const {
	std::vector<document_serializer_info> result;
	std::set<std::string> seen;

	for (const auto& pair : entries_) {
		for (const auto& entry : pair.second) {
			const auto key = entry.info_.format + "|" + entry.info_.schema_name;
			if (!seen.insert(key).second) {
				continue;
			}
			result.push_back(entry.info_);
		}
	}

	ifcopenshell::plugin::manager manager;
	add_document_serializer_search_paths(manager);
	for (const auto& path : manager.discover(document_serializer_plugin_prefix())) {
		ifcopenshell::plugin::module module;
		try {
			module = manager.load(path);
		} catch (const std::exception& e) {
			::logger::root().error(e);
			continue;
		}
		if (module.meta().kind_ != ifcopenshell::plugin::kind::document_serializer) {
			continue;
		}

		document_serializer_registry plugin_registry;
		auto register_plugin = module.get_alias<register_document_serializer_plugin_fn>(document_serializer_plugin_registration_symbol());
		register_plugin(plugin_registry, module);
		for (const auto& pair : plugin_registry.entries_) {
			for (const auto& entry : pair.second) {
				const auto key = entry.info_.format + "|" + entry.info_.schema_name;
				if (!seen.insert(key).second) {
					continue;
				}
				result.push_back(entry.info_);
			}
		}
	}

	return result;
}

const char* ifcopenshell::serializers::document_serializer_plugin_registration_symbol() {
	return "ifcopenshell_register_document_serializer_plugin_v1";
}

ifcopenshell::plugin::metadata ifcopenshell::serializers::document_serializer_plugin_metadata(const std::string& format, const std::string& schema_name) {
	plugin::metadata metadata;
	metadata.kind_ = plugin::kind::document_serializer;
	metadata.id = document_serializer_plugin_prefix(format);
	if (!schema_name.empty()) {
		metadata.id += "." + boost::to_lower_copy(schema_name);
	}
	metadata.schema = document_serializer_schema_key(schema_name);
	metadata.format = document_serializer_key(format);
	return metadata;
}

std::filesystem::path ifcopenshell::serializers::document_serializer_plugin_directory() {
	return plugin::module_directory(reinterpret_cast<const void*>(&ifcopenshell::serializers::document_serializer_plugin_directory));
}

void ifcopenshell::serializers::load_document_serializer_plugins(document_serializer_registry& registry) {
	ifcopenshell::plugin::manager manager;
	add_document_serializer_search_paths(manager);

	for (const auto& path : manager.discover(document_serializer_plugin_prefix())) {
		ifcopenshell::plugin::module module;
		try {
			module = manager.load(path);
		} catch (const std::exception& e) {
			::logger::root().error(e);
			continue;
		}
		if (module.meta().kind_ != ifcopenshell::plugin::kind::document_serializer) {
			continue;
		}

		auto register_plugin = module.get_alias<register_document_serializer_plugin_fn>(document_serializer_plugin_registration_symbol());
		register_plugin(registry, module);
	}
}

bool ifcopenshell::serializers::load_document_serializer_plugin(document_serializer_registry& registry, const std::string& format, const std::string& schema_name) {
	const auto format_key = document_serializer_key(format);
	if (format_key.empty()) {
		return false;
	}

	const auto schema_key = document_serializer_schema_key(schema_name);
	auto basename = document_serializer_plugin_prefix(format_key);
	if (!schema_key.empty()) {
		basename += "." + boost::to_lower_copy(schema_key);
	}

	ifcopenshell::plugin::manager manager;
	add_document_serializer_search_paths(manager);

	for (const auto& path : manager.discover_exact(basename)) {
		ifcopenshell::plugin::module module;
		try {
			module = manager.load(path);
		} catch (const std::exception& e) {
			::logger::root().error(e);
			continue;
		}
		if (module.meta().kind_ != ifcopenshell::plugin::kind::document_serializer ||
			module.meta().format != format_key ||
			document_serializer_schema_key(module.meta().schema) != schema_key) {
			continue;
		}

		auto register_plugin = module.get_alias<register_document_serializer_plugin_fn>(document_serializer_plugin_registration_symbol());
		register_plugin(registry, module);
		return registry.find_entry_(format_key, schema_key) != nullptr;
	}

	return false;
}

ifcopenshell::serializers::document_serializer_registry& ifcopenshell::serializers::document_serializer_registry_instance() {
	static document_serializer_registry registry;
	return registry;
}
