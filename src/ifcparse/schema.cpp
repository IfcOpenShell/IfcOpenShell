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

#include "schema.h"

#include "express.h"

#include <map>
#include <mutex>
#include <set>

#include "schemas/Header_section_schema.h"

namespace ifcopenshell {
namespace plugin {
PLUGIN_API std::filesystem::path add_search_paths_or_default(manager& manager, std::filesystem::path (*default_search_path)());
}
}

bool ifcopenshell::declaration::is(const std::string& name) const {
    const std::string* name_ptr = &name;
    if (std::any_of(name.begin(), name.end(), [](char character) { return std::islower(character); })) {
        temp_string_() = name;
        boost::to_upper(temp_string_());
        name_ptr = &temp_string_();
    }

    if (name_upper_ == *name_ptr) {
        return true;
    }

    if ((this->as_entity() != nullptr) && (this->as_entity()->supertype() != nullptr)) {
        return this->as_entity()->supertype()->is(name);
    }
    if (this->as_type_declaration() != nullptr) {
        const ifcopenshell::named_type* named_type = this->as_type_declaration()->declared_type()->as_named_type();
        if (named_type != nullptr) {
            return named_type->is(name);
        }
    }

    return false;
}

bool ifcopenshell::declaration::is(const ifcopenshell::declaration& decl) const {
    if (this == &decl) {
        return true;
    }

    if (decl.as_select_type() != nullptr) {
        const auto& li = decl.as_select_type()->select_list();
        for (const auto* selected_decl : li) {
            if (is(*selected_decl)) {
                return true;
            }
        }
    }
    if ((this->as_entity() != nullptr) && (this->as_entity()->supertype() != nullptr)) {
        return this->as_entity()->supertype()->is(decl);
    }
    if (this->as_type_declaration() != nullptr) {
        const ifcopenshell::named_type* named_type = this->as_type_declaration()->declared_type()->as_named_type();
        if (named_type != nullptr) {
            return named_type->is(decl);
        }
    }

    return false;
}

bool ifcopenshell::named_type::is(const std::string& name) const {
    return declared_type()->is(name);
}

bool ifcopenshell::named_type::is(const ifcopenshell::declaration& decl) const {
    return declared_type()->is(decl);
}

ifcopenshell::entity::~entity() {
    for (const auto* attribute : attributes_) {
        delete attribute;
    }
    for (const auto* inverse_attribute : inverse_attributes_) {
        delete inverse_attribute;
    }
}
namespace {
	constexpr const char* schema_plugin_prefix = "parse.schema.";

	std::string schema_key(const std::string& schema_name) {
		return boost::to_upper_copy(schema_name);
	}

	ifcopenshell::plugin::module builtin_schema_module(const std::string& schema_name) {
		ifcopenshell::plugin::metadata metadata;
		metadata.kind_ = ifcopenshell::plugin::kind::parse_schema;
		metadata.id = "parse.schema." + boost::to_lower_copy(schema_name);
		metadata.schema = schema_name;
		return ifcopenshell::plugin::module::builtin(metadata);
	}

	void register_builtin_schemas(ifcopenshell::schema_registry& registry) {
		registry.bind("HEADER_SECTION_SCHEMA", &Header_section_schema::get_schema, &Header_section_schema::clear_schema, builtin_schema_module("HEADER_SECTION_SCHEMA"));
	}

	bool load_schema_plugin(ifcopenshell::schema_registry& registry, const std::string& schema_name) {
		ifcopenshell::plugin::manager manager;
		ifcopenshell::plugin::add_search_paths_or_default(manager, &ifcopenshell::schema_plugin_directory);

		const auto expected_key = schema_key(schema_name);
		const auto basename = std::string(schema_plugin_prefix) + boost::to_lower_copy(schema_name);

		for (const auto& path : manager.discover_exact(basename)) {
			auto module = manager.load(path);
			if (module.meta().kind_ != ifcopenshell::plugin::kind::parse_schema ||
				schema_key(module.meta().schema) != expected_key) {
				continue;
			}

			auto register_plugin = module.get_alias<ifcopenshell::schema_registry::register_schema_plugin_fn>(ifcopenshell::schema_plugin_registration_symbol());
			register_plugin(registry, module);
			return true;
		}

		return false;
	}

}

ifcopenshell::schema_definition::schema_definition(const std::string& name, const std::vector<const declaration*>& declarations)
    : name_(name)
    , declarations_(declarations)
{
    std::sort(declarations_.begin(), declarations_.end(), declaration_by_index_sort());
    for (std::vector<const declaration*>::iterator it = declarations_.begin(); it != declarations_.end(); ++it) {
        (**it).schema_ = this;

        if ((**it).as_type_declaration() != nullptr) {
            type_declarations_.push_back((**it).as_type_declaration());
        }
        if ((**it).as_select_type() != nullptr) {
            select_types_.push_back((**it).as_select_type());
        }
        if ((**it).as_enumeration_type() != nullptr) {
            enumeration_types_.push_back((**it).as_enumeration_type());
        }
        if ((**it).as_entity() != nullptr) {
            entities_.push_back((**it).as_entity());
        }
    }

    // Force each entity's lazy all_attributes_ cache now, while construction
    // is still single-threaded. The schema is a process-wide singleton shared
    // read-only across concurrent parsing threads; letting all_attributes()
    // populate the cache lazily on first parse would be a data race.
    for (const entity* ent : entities_) {
        ent->all_attributes();
    }

    register_schema(this);
}

ifcopenshell::schema_definition::~schema_definition() {
    for (std::vector<const declaration*>::const_iterator it = declarations_.begin(); it != declarations_.end(); ++it) {
        delete *it;
    }
}

void ifcopenshell::register_schema(schema_definition* schema) {
    schema_registry_instance().bind(schema);
}

ifcopenshell::schema_registry& ifcopenshell::schema_registry_instance() {
	static schema_registry registry;
	static std::once_flag once;
	std::call_once(once, register_builtin_schemas, std::ref(registry));
	return registry;
}

const char* ifcopenshell::schema_plugin_registration_symbol() {
	return "ifcopenshell_register_schema_plugin_v1";
}

ifcopenshell::plugin::metadata ifcopenshell::schema_plugin_metadata(const std::string& schema_name) {
	plugin::metadata metadata;
	metadata.kind_ = plugin::kind::parse_schema;
	metadata.id = schema_plugin_prefix + boost::to_lower_copy(schema_name);
	metadata.schema = boost::to_upper_copy(schema_name);
	return metadata;
}

// Stable anchor symbol inside libIfcParse for plugin::module_directory()'s
// dladdr/GetModuleHandleEx lookup. A variable (vs. a function pointer) has
// exactly one canonical address inside its defining module — function
// pointers can resolve to a PLT/stub copy in the consumer binary on some
// toolchains (observed on macOS arm64: `&load_schema_plugins` resolved
// inside BonsaiViewer.exe instead of libIfcParse.dylib, so dladdr returned
// the exe's directory and the plugin search path ended up at
// BonsaiViewer.app/Contents/MacOS/ instead of wherever libIfcParse — and
// therefore the schema plug-ins — actually lived).
extern "C" IFC_PARSE_API char ifcopenshell_libifcparse_anchor;
IFC_PARSE_API char ifcopenshell_libifcparse_anchor = 0;

std::filesystem::path ifcopenshell::schema_plugin_directory() {
	return plugin::module_directory(&ifcopenshell_libifcparse_anchor);
}

void ifcopenshell::load_schema_plugins(schema_registry& registry) {
	plugin::manager manager;
	plugin::add_search_paths_or_default(manager, &schema_plugin_directory);

	for (const auto& path : manager.discover(schema_plugin_prefix)) {
		auto module = manager.load(path);
		if (module.meta().kind_ != plugin::kind::parse_schema) {
			continue;
		}

		auto register_plugin = module.get_alias<schema_registry::register_schema_plugin_fn>(schema_plugin_registration_symbol());
		register_plugin(registry, module);
	}
}

void ifcopenshell::schema_registry::bind(const std::string& schema_name, get_schema_fn get, clear_schema_fn clear, const plugin::module& module) {
	std::lock_guard<std::recursive_mutex> lock(mutex_);
	auto& entry = entries_[schema_key(schema_name)];
	entry.get_ = get;
	entry.clear_ = clear;
	entry.module_ = module;
}

void ifcopenshell::schema_registry::bind(schema_definition* schema) {
	std::lock_guard<std::recursive_mutex> lock(mutex_);
	auto& entry = entries_[schema_key(schema->name())];
	entry.schema_ = schema;
}

const ifcopenshell::schema_definition* ifcopenshell::schema_registry::get(const std::string& schema_name) {
	std::lock_guard<std::recursive_mutex> lock(mutex_);
	const auto key = schema_key(schema_name);
	auto iter = entries_.find(key);
	if (iter == entries_.end()) {
		load_schema_plugin(*this, schema_name);
		iter = entries_.find(key);
	}
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No schema named " + schema_name);
	}
	if (!iter->second.schema_ && iter->second.get_) {
		iter->second.schema_ = &iter->second.get_();
	}
	if (!iter->second.schema_) {
		throw ifcopenshell::exception("No schema named " + schema_name);
	}
	return iter->second.schema_;
}

std::vector<std::string> ifcopenshell::schema_registry::names() {
	std::lock_guard<std::recursive_mutex> lock(mutex_);
	std::set<std::string> seen;
	for (const auto& pair : entries_) {
		seen.insert(pair.first);
	}

	plugin::manager manager;
	plugin::add_search_paths_or_default(manager, &schema_plugin_directory);
	for (const auto& path : manager.discover(schema_plugin_prefix)) {
		auto module = manager.load(path);
		if (module.meta().kind_ == plugin::kind::parse_schema && !module.meta().schema.empty()) {
			seen.insert(schema_key(module.meta().schema));
		}
	}

	std::vector<std::string> names(seen.begin(), seen.end());
	return names;
}

void ifcopenshell::schema_registry::clear() {
	std::lock_guard<std::recursive_mutex> lock(mutex_);
	for (auto& pair : entries_) {
		if (pair.second.clear_) {
			pair.second.clear_();
		}
		pair.second.schema_ = nullptr;
	}
}

const ifcopenshell::schema_definition* ifcopenshell::schema_by_name(const std::string& name) {
	return schema_registry_instance().get(name);
}

std::vector<std::string> ifcopenshell::schema_names() {
    return schema_registry_instance().names();
}

void ifcopenshell::clear_schemas() {
    schema_registry_instance().clear();
}
