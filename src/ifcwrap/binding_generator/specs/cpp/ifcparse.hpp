// SPDX-License-Identifier: LGPL-3.0-or-later

#ifndef IFCWRAP_BINDING_GENERATOR_IFCPARSE_SPEC_HPP
#define IFCWRAP_BINDING_GENERATOR_IFCPARSE_SPEC_HPP

#include "spec_macros.h"

#include "argument.h"
#include "argument_type.h"
#include "file.h"
#include "parse.h"
#include "schema.h"
#include "plugin.h"
#include "si_prefix.h"
#include "utils.h"

#include <algorithm>
#include <cstdint>
#include <cstddef>
#include <fstream>
#include <iterator>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>

/*
 * Opaque C handles exposed by this spec. Each entry gives the binding name,
 * C++ type, and destruction policy. Optional arguments select value or shared
 * pointer storage and define how an empty value is detected.
 */
IFCAPI_HANDLE(file, ifcopenshell::file, delete)
IFCAPI_HANDLE(instance_streamer, ifcopenshell::instance_streamer<>, delete)
IFCAPI_HANDLE(instance, express::base, none, value, "!static_cast<bool>({value})")
IFCAPI_HANDLE(header, ifcopenshell::spf_header, none)
IFCAPI_HANDLE(file_description, Header_section_schema::file_description, none, value, "!static_cast<bool>({value})")
IFCAPI_HANDLE(file_name, Header_section_schema::file_name, none, value, "!static_cast<bool>({value})")
IFCAPI_HANDLE(file_schema, Header_section_schema::file_schema, none, value, "!static_cast<bool>({value})")
IFCAPI_HANDLE(declaration, ifcopenshell::declaration, none)
IFCAPI_HANDLE(type_declaration, ifcopenshell::type_declaration, none)
IFCAPI_HANDLE(select_type, ifcopenshell::select_type, none)
IFCAPI_HANDLE(schema, ifcopenshell::schema_definition, none)
IFCAPI_HANDLE(enumeration, ifcopenshell::enumeration_type, none)
IFCAPI_HANDLE(parameter_type, ifcopenshell::parameter_type, none)
IFCAPI_HANDLE(named_type, ifcopenshell::named_type, none)
IFCAPI_HANDLE(simple_type, ifcopenshell::simple_type, none)
IFCAPI_HANDLE(aggregation_type, ifcopenshell::aggregation_type, none)
IFCAPI_HANDLE(entity, ifcopenshell::entity, none)
IFCAPI_HANDLE(attribute, ifcopenshell::attribute, none)
IFCAPI_HANDLE(inverse_attribute, ifcopenshell::inverse_attribute, none)
IFCAPI_HANDLE(attribute_value, ifcopenshell::attribute_value, none, value) struct ifcopenshell_parse_attribute_value_t;
IFCAPI_HANDLE(instance_list, std::vector<express::base>, none, value) struct ifcopenshell_parse_instance_list_t;

/*
 * Existing C++ methods included in the C ABI. Entries identify the receiver
 * handle, C++ method, exported name, and exact parameter types when needed to
 * select an overload. Clang supplies the remaining type information.
 */
IFCAPI_DISCOVER_METHOD(file, create, create, const ifcopenshell::declaration*, int)
IFCAPI_DISCOVER_METHOD(file, instances_by_type, by_type, const std::string&)
IFCAPI_DISCOVER_METHOD(file, instances_by_type_excl_subtypes, by_type_excl_subtypes, const std::string&)
IFCAPI_DISCOVER_METHOD(file, add_entity, add, const express::base&, int)
IFCAPI_DISCOVER_METHOD(file, add_type_ref, add_type_ref, const express::base&)
IFCAPI_DISCOVER_METHOD(file, batch, batch)
IFCAPI_DISCOVER_METHOD(file, build_inverses, build_inverses)
IFCAPI_DISCOVER_METHOD(file, build_inverses_, build_inverses_, const express::base&)
IFCAPI_DISCOVER_METHOD(file, bypass_type, bypass_type, const std::string&)
IFCAPI_DISCOVER_METHOD(file, create_timestamp, create_timestamp)
IFCAPI_DISCOVER_METHOD(file, fresh_id, fresh_id)
IFCAPI_DISCOVER_METHOD(file, get_inverse_indices_by_id, get_inverse_indices_by_id, int)
IFCAPI_DISCOVER_METHOD(file, get_max_id, get_max_id)
IFCAPI_DISCOVER_METHOD(file, get_total_inverses, get_total_inverses_by_id, int)
IFCAPI_DISCOVER_METHOD(file, ifcroot_type, ifcroot_type)
IFCAPI_DISCOVER_METHOD(file, initialize, initialize, const std::string&, ifcopenshell::filetype, bool)
IFCAPI_DISCOVER_METHOD(file, instance_by_guid, by_guid, const std::string&)
IFCAPI_DISCOVER_METHOD(file, instance_by_id, by_id, int)
IFCAPI_DISCOVER_METHOD(file, instances_by_reference, instances_by_reference, int)
IFCAPI_DISCOVER_METHOD(file, process_deletion_inverse, process_deletion_inverse, const express::base&)
IFCAPI_DISCOVER_METHOD(file, recalculate_id_counter, recalculate_id_counter)
IFCAPI_DISCOVER_METHOD(file, remove_entity, remove, const express::base&)
IFCAPI_DISCOVER_METHOD(file, remove_type_ref, remove_type_ref, const express::base&)
IFCAPI_DISCOVER_METHOD(file, reset_identity_cache, reset_identity_cache)
IFCAPI_DISCOVER_METHOD(file, schema, schema)
IFCAPI_DISCOVER_METHOD(file, traverse, traverse, const express::base&, int)
IFCAPI_DISCOVER_METHOD(file, traverse_breadth_first, traverse_breadth_first, const express::base&, int)
IFCAPI_DISCOVER_METHOD(file, unbatch, unbatch)
IFCAPI_DISCOVER_METHOD(instance, declaration, declaration)
IFCAPI_DISCOVER_METHOD(instance, file, file)
IFCAPI_DISCOVER_METHOD(instance, get_attribute_value, get_argument, unsigned long)
IFCAPI_DISCOVER_METHOD(instance, id, id)
IFCAPI_DISCOVER_METHOD(instance, identity, identity)
IFCAPI_DISCOVER_METHOD(schema, declaration_by_name, declaration_by_name, const std::string&)
IFCAPI_DISCOVER_METHOD(schema, declaration_by_name, declaration_by_index, unsigned long)
IFCAPI_DISCOVER_METHOD(schema, declarations, declarations)
IFCAPI_DISCOVER_METHOD(schema, entities, entities)
IFCAPI_DISCOVER_METHOD(schema, enumeration_types, enumeration_types)
IFCAPI_DISCOVER_METHOD(schema, name, name)
IFCAPI_DISCOVER_METHOD(schema, select_types, select_types)
IFCAPI_DISCOVER_METHOD(schema, type_declarations, type_declarations)
IFCAPI_DISCOVER_METHOD(declaration, is, is_a, const std::string&)
IFCAPI_DISCOVER_METHOD(declaration, as_entity, as_entity)
IFCAPI_DISCOVER_METHOD(declaration, as_enumeration_type, as_enumeration_type)
IFCAPI_DISCOVER_METHOD(declaration, as_select_type, as_select_type)
IFCAPI_DISCOVER_METHOD(declaration, as_type_declaration, as_type_declaration)
IFCAPI_DISCOVER_METHOD(declaration, index_in_schema, index_in_schema)
IFCAPI_DISCOVER_METHOD(declaration, name, name)
IFCAPI_DISCOVER_METHOD(declaration, name_uc, name_uc)
IFCAPI_DISCOVER_METHOD(declaration, schema, schema)
IFCAPI_DISCOVER_METHOD(declaration, type, type)
IFCAPI_DISCOVER_METHOD(type_declaration, as_type_declaration, as_type_declaration)
IFCAPI_DISCOVER_METHOD(type_declaration, declared_type, declared_type)
IFCAPI_DISCOVER_METHOD(select_type, as_select_type, as_select_type)
IFCAPI_DISCOVER_METHOD(select_type, select_list, select_list)
IFCAPI_DISCOVER_METHOD(enumeration, as_enumeration_type, as_enumeration_type)
IFCAPI_DISCOVER_METHOD(enumeration, enumeration_items, enumeration_items)
IFCAPI_DISCOVER_METHOD(enumeration, lookup_enum_offset, lookup_enum_offset, const std::string&)
IFCAPI_DISCOVER_METHOD(enumeration, lookup_enum_value, lookup_enum_value, unsigned long)
IFCAPI_DISCOVER_METHOD(parameter_type, as_aggregation_type, as_aggregation_type)
IFCAPI_DISCOVER_METHOD(parameter_type, as_named_type, as_named_type)
IFCAPI_DISCOVER_METHOD(parameter_type, as_simple_type, as_simple_type)
IFCAPI_DISCOVER_METHOD(named_type, is, is_a, const std::string&)
IFCAPI_DISCOVER_METHOD(named_type, as_named_type, as_named_type)
IFCAPI_DISCOVER_METHOD(named_type, declared_type, declared_type)
IFCAPI_DISCOVER_METHOD(simple_type, as_simple_type, as_simple_type)
IFCAPI_DISCOVER_METHOD(simple_type, declared_type, declared_type)
IFCAPI_DISCOVER_METHOD(aggregation_type, as_aggregation_type, as_aggregation_type)
IFCAPI_DISCOVER_METHOD(aggregation_type, bound1, bound1)
IFCAPI_DISCOVER_METHOD(aggregation_type, bound2, bound2)
IFCAPI_DISCOVER_METHOD(aggregation_type, type_of_element, type_of_element)
IFCAPI_DISCOVER_METHOD(header, owner_file, file)
IFCAPI_DISCOVER_METHOD(header, file_description, file_description)
IFCAPI_DISCOVER_METHOD(header, file_name, file_name)
IFCAPI_DISCOVER_METHOD(header, file_schema, file_schema)
IFCAPI_DISCOVER_METHOD(file_description, Class, class)
IFCAPI_DISCOVER_METHOD(file_description, description, description)
IFCAPI_DISCOVER_METHOD(file_description, implementation_level, implementation_level)
IFCAPI_DISCOVER_METHOD(file_description, initialize, initialize, std::vector<std::string>, std::string)
IFCAPI_DISCOVER_METHOD(file_description, setdescription, setdescription, const std::vector<std::string>&)
IFCAPI_DISCOVER_METHOD(file_description, setimplementation_level, setimplementation_level, const std::string&)
IFCAPI_DISCOVER_METHOD(file_name, Class, class)
IFCAPI_DISCOVER_METHOD(file_name, author, author)
IFCAPI_DISCOVER_METHOD(file_name, authorization, authorization)
IFCAPI_DISCOVER_METHOD(file_name, initialize, initialize, std::string, std::string, std::vector<std::string>, std::vector<std::string>, std::string, std::string, std::string)
IFCAPI_DISCOVER_METHOD(file_name, name, name)
IFCAPI_DISCOVER_METHOD(file_name, organization, organization)
IFCAPI_DISCOVER_METHOD(file_name, originating_system, originating_system)
IFCAPI_DISCOVER_METHOD(file_name, preprocessor_version, preprocessor_version)
IFCAPI_DISCOVER_METHOD(file_name, setauthor, setauthor, const std::vector<std::string>&)
IFCAPI_DISCOVER_METHOD(file_name, setauthorization, setauthorization, const std::string&)
IFCAPI_DISCOVER_METHOD(file_name, setname, setname, const std::string&)
IFCAPI_DISCOVER_METHOD(file_name, setorganization, setorganization, const std::vector<std::string>&)
IFCAPI_DISCOVER_METHOD(file_name, setoriginating_system, setoriginating_system, const std::string&)
IFCAPI_DISCOVER_METHOD(file_name, setpreprocessor_version, setpreprocessor_version, const std::string&)
IFCAPI_DISCOVER_METHOD(file_name, settime_stamp, settime_stamp, const std::string&)
IFCAPI_DISCOVER_METHOD(file_name, time_stamp, time_stamp)
IFCAPI_DISCOVER_METHOD(file_schema, Class, class)
IFCAPI_DISCOVER_METHOD(file_schema, initialize, initialize, std::vector<std::string>)
IFCAPI_DISCOVER_METHOD(file_schema, schema_identifiers, schema_identifiers)
IFCAPI_DISCOVER_METHOD(file_schema, setschema_identifiers, setschema_identifiers, const std::vector<std::string>&)
IFCAPI_DISCOVER_METHOD(entity, attribute_index, attribute_index, const std::string&)
IFCAPI_DISCOVER_METHOD(entity, all_attributes, all_attributes)
IFCAPI_DISCOVER_METHOD(entity, all_inverse_attributes, all_inverse_attributes)
IFCAPI_DISCOVER_METHOD(entity, as_entity, as_entity)
IFCAPI_DISCOVER_METHOD(entity, attribute_by_index, attribute_by_index, unsigned long)
IFCAPI_DISCOVER_METHOD(entity, attribute_count, attribute_count)
IFCAPI_DISCOVER_METHOD(entity, attributes, attributes)
IFCAPI_DISCOVER_METHOD(entity, derived, derived)
IFCAPI_DISCOVER_METHOD(entity, inverse_attributes, inverse_attributes)
IFCAPI_DISCOVER_METHOD(entity, is_abstract, is_abstract)
IFCAPI_DISCOVER_METHOD(entity, set_attributes, set_attributes, const std::vector<const ifcopenshell::attribute*>&, const std::vector<bool>&)
IFCAPI_DISCOVER_METHOD(entity, set_inverse_attributes, set_inverse_attributes, const std::vector<const ifcopenshell::inverse_attribute*>&)
IFCAPI_DISCOVER_METHOD(entity, set_subtypes, set_subtypes, const std::vector<const ifcopenshell::entity*>&)
IFCAPI_DISCOVER_METHOD(entity, subtypes, subtypes)
IFCAPI_DISCOVER_METHOD(entity, supertype, supertype)
IFCAPI_DISCOVER_METHOD(attribute, name, name)
IFCAPI_DISCOVER_METHOD(attribute, optional, optional)
IFCAPI_DISCOVER_METHOD(attribute, type_of_attribute, type_of_attribute)
IFCAPI_DISCOVER_METHOD(inverse_attribute, attribute_reference, attribute_reference)
IFCAPI_DISCOVER_METHOD(inverse_attribute, bound1, bound1)
IFCAPI_DISCOVER_METHOD(inverse_attribute, bound2, bound2)
IFCAPI_DISCOVER_METHOD(inverse_attribute, entity_reference, entity_reference)
IFCAPI_DISCOVER_METHOD(inverse_attribute, name, name)
IFCAPI_DISCOVER_METHOD(instance_streamer, bypassed_instances, bypassed_instances)
IFCAPI_DISCOVER_METHOD(instance_streamer, has_semicolon, has_semicolon)
IFCAPI_DISCOVER_METHOD(instance_streamer, push_page, push_page, const std::string&)
IFCAPI_DISCOVER_METHOD(instance_streamer, semicolon_count, semicolon_count)

namespace ifcopenshell::capi {

void set_feature(const std::string& name, bool value);
bool get_feature(const std::string& name);
std::string get_log();
void turn_on_detailed_logging();
void turn_off_detailed_logging();
void set_log_format_json();
void set_log_format_text();
std::string get_info_json(const express::base& instance, bool include_identifier);
std::string streamer_references(ifcopenshell::instance_streamer<>* streamer);
std::string streamer_inverses(ifcopenshell::instance_streamer<>* streamer);
std::string streamer_read_instance_json(ifcopenshell::instance_streamer<>* streamer);
void unset_instance_argument_value(express::base& instance, size_t index);
void set_instance_argument_bool(express::base& instance, size_t index, bool value);
void set_instance_argument_int32(express::base& instance, size_t index, int value);
void set_instance_argument_double(express::base& instance, size_t index, double value);
void set_instance_argument_string(express::base& instance, size_t index, const std::string& value);
void set_instance_argument_instance(express::base& instance, size_t index, express::base* value);
void set_instance_argument_instance_list(express::base& instance, size_t index, std::vector<express::base>* value);
void set_instance_argument_int32_list(express::base& instance, size_t index, const std::vector<int>& value);
void set_instance_argument_double_list(express::base& instance, size_t index, const std::vector<double>& value);
void set_instance_argument_string_list(express::base& instance, size_t index, const std::vector<std::string>& value);
void set_instance_argument_int32_list_list(express::base& instance, size_t index, const std::vector<std::vector<int>>& value);
void set_instance_argument_double_list_list(express::base& instance, size_t index, const std::vector<std::vector<double>>& value);
void set_instance_argument_logical(express::base& instance, size_t index, int value);
void set_instance_argument_aggregate_of_aggregate_of_entity_instance(
    express::base& instance,
    size_t index,
    const std::vector<std::vector<int>>& value
);
void set_instance_argument_enumeration(
    express::base& instance,
    size_t index,
    const ifcopenshell::enumeration_type* enumeration,
    size_t enumeration_index
);
bool set_instance_argument_enumeration_by_name(express::base& instance, size_t index, const std::string& value);
void set_instance_attribute_from_attribute_value(express::base& instance, size_t index, const ifcopenshell::attribute_value& value);
void unset_instance_argument(express::base& instance, size_t index);
ifcopenshell::argument_type instance_attribute_type(const express::base& instance, unsigned index);

} // namespace ifcopenshell::capi

namespace ifcparse::bindings {

inline std::vector<express::base> to_base_vector(const std::vector<express::entity>& entities) {
    std::vector<express::base> result;
    result.reserve(entities.size());
    for (const auto& entity : entities) {
        result.push_back(entity);
    }
    return result;
}

inline std::vector<express::base> get_inverses_by_declaration(
    ifcopenshell::file& self,
    int instance_id,
    const ifcopenshell::declaration* declaration,
    int attribute_index
) {
    return to_base_vector(self.get_inverse(instance_id, declaration, attribute_index));
}

inline std::string argument_type_to_string(int type) {
    return ifcopenshell::argument_type_to_string(static_cast<ifcopenshell::argument_type>(type));
}

inline void clear_schemas() {
    ifcopenshell::clear_schemas();
}

inline void escape_xml(std::string text) {
    ifcopenshell::escape_xml(text);
}

inline int from_parameter_type(const ifcopenshell::parameter_type* parameter_type) {
    return static_cast<int>(ifcopenshell::from_parameter_type(parameter_type));
}

inline int guess_file_type(const std::string& path) {
    return static_cast<int>(ifcopenshell::guess_file_type(path));
}

inline int make_aggregate(int element_type) {
    return static_cast<int>(ifcopenshell::make_aggregate(static_cast<ifcopenshell::argument_type>(element_type)));
}

inline void register_schema(ifcopenshell::schema_definition* schema) {
    ifcopenshell::register_schema(*schema);
}

inline void sanitate_material_name(std::string material_name) {
    ifcopenshell::sanitate_material_name(material_name);
}

inline const ifcopenshell::schema_definition* schema_by_name(const std::string& schema_name) {
    return ifcopenshell::schema_by_name(schema_name);
}

inline std::vector<std::string> schema_names() {
    return ifcopenshell::schema_names();
}

inline std::string schema_plugin_registration_symbol() {
    return ifcopenshell::schema_plugin_registration_symbol();
}

inline void set_plugin_search_paths(const std::vector<std::string>& paths) {
    ifcopenshell::plugin::set_search_paths(paths);
}

inline std::vector<std::string> get_plugin_search_paths() {
    return ifcopenshell::plugin::search_paths();
}

inline void clear_plugin_search_paths() {
    ifcopenshell::plugin::clear_search_paths();
}

inline double si_prefix_to_value(const std::string& prefix) {
    return ifcopenshell::si_prefix_to_value(prefix);
}

inline std::vector<express::base> traverse(const express::base& instance, int max_depth) {
    return ifcopenshell::traverse(instance, max_depth);
}

inline std::vector<express::base> traverse_breadth_first(const express::base& instance, int max_depth) {
    return ifcopenshell::traverse_breadth_first(instance, max_depth);
}

inline void unescape_xml(std::string text) {
    ifcopenshell::unescape_xml(text);
}

inline bool valid_binary_string(const std::string& binary_string) {
    return ifcopenshell::valid_binary_string(binary_string);
}

inline std::unique_ptr<ifcopenshell::file> open(const std::string& path, bool readonly) {
    {
        std::ifstream probe(path.c_str());
        if (!probe.good()) {
            throw std::runtime_error(std::string("File does not exist or is not readable: ") + path);
        }
    }
    auto file = std::make_unique<ifcopenshell::file>(path, ifcopenshell::FT_AUTODETECT, readonly);
    if (!file->good()) {
        throw std::runtime_error(std::string("Failed to open IFC file: ") + path);
    }
    return file;
}

inline std::unique_ptr<ifcopenshell::file> open_bypass(
    const std::string& path,
    const std::vector<std::string>& type_names
) {
    auto file = std::make_unique<ifcopenshell::file>(ifcopenshell::uninitialized_tag{});
    for (const auto& type_name : type_names) {
        file->bypass_type(type_name);
    }
    if (!file->initialize(path)) {
        throw std::runtime_error(std::string("Failed to open IFC file: ") + path);
    }
    return file;
}

inline std::unique_ptr<ifcopenshell::file> new_file(
    const std::string& schema_identifier,
    int file_type,
    const std::string& path
) {
    const ifcopenshell::schema_definition* schema = ifcopenshell::schema_by_name(schema_identifier);
    return std::make_unique<ifcopenshell::file>(
        schema, static_cast<ifcopenshell::filetype>(file_type), path);
}

inline std::unique_ptr<ifcopenshell::file> read_memory(const void* data, int length) {
    if (length < 0) {
        throw std::runtime_error("length is negative");
    }
    auto file = std::make_unique<ifcopenshell::file>(const_cast<void*>(data), static_cast<int>(length));
    if (!file->good()) {
        throw std::runtime_error("Failed to parse IFC data from string");
    }
    return file;
}

inline std::unique_ptr<ifcopenshell::instance_streamer<>> stream() {
    return std::make_unique<ifcopenshell::instance_streamer<>>();
}

inline std::unique_ptr<ifcopenshell::instance_streamer<>> stream_from_path(
    const std::string& path,
    bool mmap
) {
#ifdef USE_MMAP
    return std::make_unique<ifcopenshell::instance_streamer<>>(path, mmap);
#else
    (void)mmap;
    return std::make_unique<ifcopenshell::instance_streamer<>>(path, false);
#endif
}

inline std::unique_ptr<ifcopenshell::instance_streamer<>> stream_from_string(const std::string& data) {
    return std::make_unique<ifcopenshell::instance_streamer<>>(
        (void*)data.data(), static_cast<int>(data.size()));
}

inline IFCAPI_STATIC const char* version() {
    return IFCOPENSHELL_VERSION;
}

inline double get_si_equivalent(const express::base& named_unit) {
    if (!named_unit.declaration().is("IfcNamedUnit")) {
        throw ifcopenshell::exception("Instance is not an IfcNamedUnit.");
    }
    double scale = 1.0;
    express::base si_unit;
    if (named_unit.declaration().is("IfcConversionBasedUnit")) {
        auto factor = static_cast<express::base>(named_unit.get_attribute_value(
            named_unit.declaration().as_entity()->attribute_index("ConversionFactor")));
        auto value_component = static_cast<express::base>(factor.get_attribute_value(
            factor.declaration().as_entity()->attribute_index("ValueComponent")));
        auto unit_component = static_cast<express::base>(factor.get_attribute_value(
            factor.declaration().as_entity()->attribute_index("UnitComponent")));
        scale = static_cast<double>(value_component.get_attribute_value(0));
        if (unit_component.declaration().is("IfcSIUnit")) {
            si_unit = unit_component;
        }
    } else if (named_unit.declaration().is("IfcSIUnit")) {
        si_unit = named_unit;
    }
    if (si_unit) {
        ifcopenshell::attribute_value prefix = si_unit.get_attribute_value(
            si_unit.declaration().as_entity()->attribute_index("Prefix"));
        if (!prefix.isNull()) {
            scale *= ifcopenshell::si_prefix_to_value(static_cast<std::string>(prefix));
        }
    } else {
        scale = 0.0;
    }
    return scale;
}

inline void set_feature(const std::string& name, bool value) {
    ifcopenshell::capi::set_feature(name, value);
}

inline bool get_feature(const std::string& name) {
    return ifcopenshell::capi::get_feature(name);
}

inline std::string get_log() {
    return ifcopenshell::capi::get_log();
}

inline void turn_on_detailed_logging() {
    ifcopenshell::capi::turn_on_detailed_logging();
}

inline void turn_off_detailed_logging() {
    ifcopenshell::capi::turn_off_detailed_logging();
}

inline void set_log_format_json() {
    ifcopenshell::capi::set_log_format_json();
}

inline void set_log_format_text() {
    ifcopenshell::capi::set_log_format_text();
}

inline std::string get_info_json(const express::base& instance, bool include_identifier) {
    return ifcopenshell::capi::get_info_json(instance, include_identifier);
}

inline void write(ifcopenshell::file& self, const std::string& path) {
    std::ofstream stream(ifcopenshell::path::from_utf8(path).c_str());
    if (!stream.good()) {
        throw std::runtime_error("Failed to write to path: '" + path + "', check folder and file permissions.");
    }
    stream << self;
}

inline int storage_mode(ifcopenshell::file& self) {
    return std::visit([](auto& storage) -> int {
        using T = std::decay_t<decltype(storage)>;
        if constexpr (std::is_same_v<T, ifcopenshell::impl::in_memory_file_storage>) {
            return 0;
        } else if constexpr (std::is_same_v<T, ifcopenshell::impl::rocks_db_file_storage>) {
            return 1;
        }
        return -1;
    }, self.storage_);
}

inline express::base create_entity_by_name(ifcopenshell::file& self, const std::string& type_name) {
    const auto* schema = self.schema();
    const auto* decl = schema->declaration_by_name(type_name);
    if (!decl || (!decl->as_entity() && !decl->as_type_declaration() && !decl->as_enumeration_type())) {
        throw std::runtime_error("Declaration is not creatable");
    }
    auto entity = self.create(decl);
    if (!entity) {
        throw std::runtime_error("Failed to create entity");
    }
    return entity;
}

inline express::base create_entity_by_name_with_id(
    ifcopenshell::file& self,
    const std::string& type_name,
    std::uint32_t id
) {
    const auto* schema = self.schema();
    const auto* decl = schema->declaration_by_name(type_name);
    if (!decl || !decl->as_entity()) {
        throw std::runtime_error("Type declaration is not an entity");
    }
    auto entity = self.create(decl, static_cast<int>(id));
    if (!entity) {
        throw std::runtime_error("Failed to create entity with id");
    }
    return entity;
}

inline express::base add_entity(
    ifcopenshell::file& self,
    const express::base& instance,
    std::uint32_t id
) {
    auto added = self.add_entity(instance, id == 0 ? -1 : static_cast<int>(id));
    if (!added) {
        throw std::runtime_error("Failed to add entity");
    }
    return added;
}

inline std::string schema_name(ifcopenshell::file& self) {
    if (self.schema() == nullptr) {
        return std::string();
    }
    return self.schema()->name();
}

inline int get_total_inverses(ifcopenshell::file& self, const express::base& instance) {
    auto entity = instance.as<express::entity>();
    if (entity) {
        return self.get_total_inverses(entity.id());
    }
    throw ifcopenshell::exception("Only entities with ids are supported for get_total_inverses.");
}

inline std::vector<std::string> types(ifcopenshell::file& self) {
    const size_t n = std::distance(self.types_begin(), self.types_end());
    std::vector<std::string> type_names;
    type_names.reserve(n);
    std::transform(self.types_begin(), self.types_end(), std::back_inserter(type_names), [](const ifcopenshell::declaration* decl) {
        return decl->name();
    });
    return type_names;
}

inline std::string to_string(ifcopenshell::file& self) {
    std::ostringstream stream;
    stream << self;
    return stream.str();
}

inline std::vector<unsigned int> entity_names(ifcopenshell::file& self) {
    std::vector<unsigned int> ids;
    ids.reserve(std::distance(self.begin(), self.end()));
    for (auto it = self.begin(); it != self.end(); ++it) {
        ids.push_back(it->first);
    }
    return ids;
}

inline std::size_t file_pointer(ifcopenshell::file& self) {
    return reinterpret_cast<std::size_t>(&self);
}

inline std::vector<int> get_inverse_indices(ifcopenshell::file& self, const express::base& instance) {
    auto entity = instance.as<express::entity>();
    if (entity) {
        return self.get_inverse_indices_by_id(entity.id());
    }
    throw ifcopenshell::exception("Only entities with ids are supported for get_inverse_indices.");
}

inline int good(ifcopenshell::file& self) {
    return static_cast<int>(self.good().value());
}

inline double get_unit(ifcopenshell::file& self, const std::string& unit_type) {
    return self.get_unit(unit_type).second;
}

inline std::vector<uint8_t> key_value_store_query(ifcopenshell::file& self, const std::string& key) {
    auto* storage = std::visit([](auto& value) -> const ifcopenshell::impl::rocks_db_file_storage* {
        using T = std::decay_t<decltype(value)>;
        if constexpr (std::is_same_v<T, ifcopenshell::impl::rocks_db_file_storage>) {
            return &value;
        }
        return nullptr;
    }, self.storage_);
    if (!storage) {
        return std::vector<uint8_t>();
    }
#ifdef IFOPSH_WITH_ROCKSDB
    std::string value;
    if (storage->db->Get(storage->ropts, key, &value) != rocksdb::Status::OK()) {
        return std::vector<uint8_t>();
    }
    return std::vector<uint8_t>(value.begin(), value.end());
#else
    (void)key;
    return std::vector<uint8_t>();
#endif
}

inline std::vector<std::string> key_value_store_iter(ifcopenshell::file& self, const std::string& prefix) {
    std::vector<std::string> values;
    auto* storage = std::visit([](auto& value) -> const ifcopenshell::impl::rocks_db_file_storage* {
        using T = std::decay_t<decltype(value)>;
        if constexpr (std::is_same_v<T, ifcopenshell::impl::rocks_db_file_storage>) {
            return &value;
        }
        return nullptr;
    }, self.storage_);
    if (!storage) {
        return values;
    }
#ifdef IFOPSH_WITH_ROCKSDB
    std::unique_ptr<rocksdb::Iterator> iterator(storage->db->NewIterator(storage->ropts));
    const rocksdb::Slice prefix_slice(prefix);
    for (iterator->Seek(prefix); iterator->Valid() && iterator->key().starts_with(prefix_slice); iterator->Next()) {
        values.push_back(iterator->key().ToString());
    }
#else
    (void)prefix;
#endif
    return values;
}

inline int status(ifcopenshell::instance_streamer<>* self) {
    return static_cast<int>(static_cast<ifcopenshell::file_open_status::file_open_enum>(self->status()));
}

inline std::string references(ifcopenshell::instance_streamer<>* self) {
    return ifcopenshell::capi::streamer_references(self);
}

inline std::string inverses(ifcopenshell::instance_streamer<>* self) {
    return ifcopenshell::capi::streamer_inverses(self);
}

inline std::string read_instance_json(ifcopenshell::instance_streamer<>* self) {
    return ifcopenshell::capi::streamer_read_instance_json(self);
}

inline std::size_t file_pointer(const express::base& self) {
    return reinterpret_cast<std::size_t>(self.file());
}

inline unsigned int get_argument_index(const express::base& self, const std::string& name) {
    if (self.declaration().as_entity()) {
        const auto index = self.declaration().as_entity()->attribute_index(name);
        if (index >= 0) {
            return static_cast<unsigned int>(index);
        }
    } else if (name == "wrappedValue") {
        return 0u;
    }
    throw ifcopenshell::exception("Attribute '" + name + "' not found on entity named " + self.declaration().name());
}

inline std::string get_argument_name(const express::base& self, unsigned int index) {
    if (self.declaration().as_entity()) {
        return self.declaration().as_entity()->attribute_by_index(index)->name();
    }
    if (index == 0u) {
        return std::string("wrappedValue");
    }
    throw ifcopenshell::exception(std::to_string(index) + " out of bounds on " + self.declaration().name());
}

inline int get_attribute_category(const express::base& self, const std::string& name) {
    if (!self.declaration().as_entity()) {
        return name == "wrappedValue" ? 1 : 0;
    }
    for (const auto* attr : self.declaration().as_entity()->all_attributes()) {
        if (attr->name() == name) {
            return 1;
        }
    }
    for (const auto* attr : self.declaration().as_entity()->all_inverse_attributes()) {
        if (attr->name() == name) {
            return 2;
        }
    }
    return 0;
}

inline void unset_argument(express::base& self, std::size_t index) {
    ifcopenshell::capi::unset_instance_argument_value(self, index);
}

inline void set_argument_bool(express::base& self, std::size_t index, bool value) {
    ifcopenshell::capi::set_instance_argument_bool(self, index, value);
}

inline void set_argument_int32(express::base& self, std::size_t index, int value) {
    ifcopenshell::capi::set_instance_argument_int32(self, index, value);
}

inline void set_argument_double(express::base& self, std::size_t index, double value) {
    ifcopenshell::capi::set_instance_argument_double(self, index, value);
}

inline void set_argument_string(express::base& self, std::size_t index, const std::string& value) {
    ifcopenshell::capi::set_instance_argument_string(self, index, value);
}

inline void set_argument_instance(express::base& self, std::size_t index, express::base* value) {
    ifcopenshell::capi::set_instance_argument_instance(self, index, value);
}

inline void set_argument_instance_list(
    express::base& self,
    std::size_t index,
    std::vector<express::base>* value
) {
    ifcopenshell::capi::set_instance_argument_instance_list(self, index, value);
}

inline void set_argument_int32_list(
    express::base& self,
    std::size_t index,
    const std::vector<int>& value
) {
    ifcopenshell::capi::set_instance_argument_int32_list(self, index, value);
}

inline void set_argument_double_list(
    express::base& self,
    std::size_t index,
    const std::vector<double>& value
) {
    ifcopenshell::capi::set_instance_argument_double_list(self, index, value);
}

inline void set_argument_string_list(
    express::base& self,
    std::size_t index,
    const std::vector<std::string>& value
) {
    ifcopenshell::capi::set_instance_argument_string_list(self, index, value);
}

inline void set_argument_int32_list_list(
    express::base& self,
    std::size_t index,
    const std::vector<std::vector<int>>& value
) {
    ifcopenshell::capi::set_instance_argument_int32_list_list(self, index, value);
}

inline void set_argument_double_list_list(
    express::base& self,
    std::size_t index,
    const std::vector<std::vector<double>>& value
) {
    ifcopenshell::capi::set_instance_argument_double_list_list(self, index, value);
}

inline void set_argument_logical(express::base& self, std::size_t index, int value) {
    ifcopenshell::capi::set_instance_argument_logical(self, index, value);
}

inline void set_argument_as_aggregate_of_aggregate_of_entity_instance(
    express::base& self,
    std::size_t index,
    const std::vector<std::vector<int>>& value
) {
    ifcopenshell::capi::set_instance_argument_aggregate_of_aggregate_of_entity_instance(self, index, value);
}

inline void set_argument_enumeration(
    express::base& self,
    std::size_t index,
    const ifcopenshell::enumeration_type* enumeration,
    std::size_t enumeration_index
) {
    ifcopenshell::capi::set_instance_argument_enumeration(self, index, enumeration, enumeration_index);
}

inline bool set_argument_enumeration_by_name(
    express::base& self,
    std::size_t index,
    const std::string& value
) {
    return ifcopenshell::capi::set_instance_argument_enumeration_by_name(self, index, value);
}

inline std::vector<express::base> instance_list_create_from_handles(
    const std::vector<express::base>& instances
) {
    std::vector<express::base> agg;
    agg.reserve(instances.size());
    for (const auto& inst : instances) {
        if (inst) {
            agg.push_back(inst);
        }
    }
    return agg;
}

inline std::vector<express::base> get_inverse(
    ifcopenshell::file* self,
    express::base* instance
) {
    auto entity = instance->as<express::entity>();
    if (entity) {
        return to_base_vector(self->get_inverse(entity.id(), 0, -1));
    }
    throw ifcopenshell::exception("Only entities with ids are supported for get_inverse.");
}

inline ifcopenshell::spf_header* header(ifcopenshell::file* self) {
    return &self->header();
}

inline std::optional<express::base> header_file_description(ifcopenshell::file* self) {
    return self->header().file_description();
}

inline std::optional<express::base> header_file_name(ifcopenshell::file* self) {
    return self->header().file_name();
}

inline std::optional<express::base> header_file_schema(ifcopenshell::file* self) {
    return self->header().file_schema();
}

inline void set_attribute_value(
    express::base& self,
    const std::string& name,
    ifcopenshell::attribute_value& value
) {
    if (!self.declaration().as_entity()) {
        if (name != "wrappedValue") {
            throw ifcopenshell::exception(name + " not found on " + self.declaration().name());
        }
        ifcopenshell::capi::set_instance_attribute_from_attribute_value(self, 0u, value);
        return;
    }
    const auto index = self.declaration().as_entity()->attribute_index(name);
    if (index < 0) {
        throw ifcopenshell::exception(name + " not found on " + self.declaration().name());
    }
    ifcopenshell::capi::set_instance_attribute_from_attribute_value(self, static_cast<size_t>(index), value);
}

inline void unset_attribute_value(express::base& self, const std::string& name) {
    if (!self.declaration().as_entity()) {
        if (name != "wrappedValue") {
            throw ifcopenshell::exception(name + " not found on " + self.declaration().name());
        }
        ifcopenshell::capi::unset_instance_argument(self, 0u);
        return;
    }
    const auto index = self.declaration().as_entity()->attribute_index(name);
    if (index < 0) {
        throw ifcopenshell::exception(name + " not found on " + self.declaration().name());
    }
    ifcopenshell::capi::unset_instance_argument(self, static_cast<size_t>(index));
}

inline std::vector<express::base> get_inverse(
    express::base& self,
    const std::string& name
) {
    if (self.declaration().as_entity()) {
        return to_base_vector(self.as<express::entity>().get_inverse(name));
    }
    throw ifcopenshell::exception(name + " not found on " + self.declaration().name());
}

inline ifcopenshell::attribute_value get_attribute_value(
    express::base& self,
    std::size_t index
) {
    return self.get_attribute_value(index);
}

inline ifcopenshell::attribute_value get_argument_by_name(
    express::base& self,
    const std::string& name
) {
    return self.get_attribute_value(get_argument_index(self, name));
}

inline IFCAPI_STATIC const char* get_argument_type(express::base& self, unsigned int index) {
    return ifcopenshell::argument_type_to_string(ifcopenshell::capi::instance_attribute_type(self, index));
}

inline std::string to_string(express::base& self, bool valid_spf) {
    std::ostringstream oss;
    self.to_string(oss, valid_spf);
    return oss.str();
}

inline std::string class_name(express::base& self, bool with_schema) {
    auto name = self.declaration().name();
    if (with_schema) {
        name = self.declaration().schema()->name() + "." + name;
    }
    return name;
}

inline bool is_a(express::base& self, const std::string& declaration_name) {
    return self.declaration().is(declaration_name);
}

inline std::vector<std::string> get_attribute_names(express::base& self) {
    if (!self.declaration().as_entity()) {
        return std::vector<std::string>(1, "wrappedValue");
    }
    const auto attrs = self.declaration().as_entity()->all_attributes();
    std::vector<std::string> names;
    names.reserve(attrs.size());
    for (const auto* attr : attrs) {
        names.push_back(attr->name());
    }
    return names;
}

inline std::vector<std::string> get_inverse_attribute_names(express::base& self) {
    if (!self.declaration().as_entity()) {
        return std::vector<std::string>();
    }
    const auto attrs = self.declaration().as_entity()->all_inverse_attributes();
    std::vector<std::string> names;
    names.reserve(attrs.size());
    for (const auto* attr : attrs) {
        names.push_back(attr->name());
    }
    return names;
}

inline std::vector<express::base> get_inverse_attribute_by_name(
    express::base& self,
    const std::string& name
) {
    auto entity = self.as<express::entity>();
    if (entity) {
        return to_base_vector(entity.get_inverse(name));
    }
    throw ifcopenshell::exception("Only entities with ids are supported for inverse attributes.");
}

inline bool is_null(ifcopenshell::attribute_value& self) {
    return self.isNull();
}

inline IFCAPI_STATIC const char* type(ifcopenshell::attribute_value& self) {
    return ifcopenshell::argument_type_to_string(self.type());
}

inline std::size_t size(ifcopenshell::attribute_value& self) {
    return self.size();
}

inline int as_int32(ifcopenshell::attribute_value& self) {
    return static_cast<int>(self);
}

inline bool as_bool(ifcopenshell::attribute_value& self) {
    return static_cast<bool>(self);
}

inline int as_logical(ifcopenshell::attribute_value& self) {
    const boost::logic::tribool value = self;
    if (boost::logic::indeterminate(value)) {
        return -1;
    }
    return value ? 1 : 0;
}

inline double as_double(ifcopenshell::attribute_value& self) {
    return static_cast<double>(self);
}

inline std::vector<int> as_int32_list(ifcopenshell::attribute_value& self) {
    const auto values = static_cast<std::vector<int64_t>>(self);
    return std::vector<int>(values.begin(), values.end());
}

inline std::vector<double> as_double_list(ifcopenshell::attribute_value& self) {
    return static_cast<std::vector<double>>(self);
}

inline std::vector<std::vector<int>> as_int32_list_list(ifcopenshell::attribute_value& self) {
    const auto values = static_cast<std::vector<std::vector<int64_t>>>(self);
    std::vector<std::vector<int>> result;
    result.reserve(values.size());
    for (const auto& row : values) {
        result.emplace_back(row.begin(), row.end());
    }
    return result;
}

inline std::vector<std::vector<int>> as_instance_id_list_list(ifcopenshell::attribute_value& self) {
    if (self.isNull() || self.type() != ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
        throw ifcopenshell::exception("Attribute is not an aggregate of aggregate of entity instance");
    }
    auto aggregate = static_cast<std::vector<std::vector<express::base>>>(self);
    std::vector<std::vector<int>> result;
    result.reserve(aggregate.size());
    for (const auto& group : aggregate) {
        std::vector<int> row;
        row.reserve(group.size());
        for (const auto& instance : group) {
            if (!instance) {
                throw ifcopenshell::exception("Aggregate contains a null entity instance");
            }
            row.push_back(static_cast<int>(instance.id()));
        }
        result.push_back(std::move(row));
    }
    return result;
}

inline std::vector<std::vector<double>> as_double_list_list(ifcopenshell::attribute_value& self) {
    return static_cast<std::vector<std::vector<double>>>(self);
}

inline std::vector<std::string> as_string_list(ifcopenshell::attribute_value& self) {
    return static_cast<std::vector<std::string>>(self);
}

inline std::string as_string(ifcopenshell::attribute_value& self) {
    return static_cast<std::string>(self);
}

inline std::optional<express::base> as_instance(ifcopenshell::attribute_value& self) {
    return static_cast<express::base>(self);
}

inline std::vector<express::base> as_instance_list(
    ifcopenshell::attribute_value& self
) {
    return static_cast<std::vector<express::base>>(self);
}

inline std::string as_enumeration_value(ifcopenshell::attribute_value& self) {
    return std::string(static_cast<ifcopenshell::enumeration_reference>(self).value());
}

inline std::size_t as_enumeration_index(ifcopenshell::attribute_value& self) {
    return static_cast<ifcopenshell::enumeration_reference>(self).index();
}

inline std::optional<ifcopenshell::enumeration_type*> as_enumeration_type(ifcopenshell::attribute_value& self) {
    return const_cast<ifcopenshell::enumeration_type*>(
        static_cast<ifcopenshell::enumeration_reference>(self).enumeration());
}

inline std::string write(ifcopenshell::spf_header* self) {
    std::ostringstream stream;
    self->write(stream);
    return stream.str();
}

inline std::vector<std::string> select_list_names(ifcopenshell::select_type* self) {
    std::vector<std::string> names;
    names.reserve(self->select_list().size());
    for (const auto* decl : self->select_list()) {
        names.push_back(decl->name());
    }
    return names;
}

inline std::vector<std::string> argument_types(ifcopenshell::type_declaration* self) {
    std::vector<std::string> result;
    auto argument_type = ifcopenshell::Argument_UNKNOWN;
    auto* declared_type = self->declared_type();
    if (declared_type != nullptr) {
        argument_type = ifcopenshell::from_parameter_type(declared_type);
    }
    result.push_back(ifcopenshell::argument_type_to_string(argument_type));
    return result;
}

inline std::vector<std::string> argument_types(ifcopenshell::enumeration_type* self) {
    (void)self;
    return std::vector<std::string>{ifcopenshell::argument_type_to_string(ifcopenshell::Argument_STRING)};
}

inline IFCAPI_STATIC const char* kind(ifcopenshell::parameter_type* self) {
    if (self->as_named_type()) {
        return "NAMED";
    }
    if (self->as_simple_type()) {
        return "SIMPLE";
    }
    if (self->as_aggregation_type()) {
        return "AGGREGATION";
    }
    throw std::runtime_error("Unknown parameter type.");
}

inline IFCAPI_STATIC const char* kind(ifcopenshell::simple_type* self) {
    switch (self->declared_type()) {
    case ifcopenshell::simple_type::binary_type:
        return "BINARY";
    case ifcopenshell::simple_type::boolean_type:
        return "BOOLEAN";
    case ifcopenshell::simple_type::integer_type:
        return "INTEGER";
    case ifcopenshell::simple_type::logical_type:
        return "LOGICAL";
    case ifcopenshell::simple_type::number_type:
        return "NUMBER";
    case ifcopenshell::simple_type::real_type:
        return "REAL";
    case ifcopenshell::simple_type::string_type:
        return "STRING";
    case ifcopenshell::simple_type::datatype_COUNT:
        break;
    }
    throw std::runtime_error("Unknown simple type.");
}

inline int type_of_aggregation(ifcopenshell::aggregation_type* self) {
    return static_cast<int>(self->type_of_aggregation());
}

inline IFCAPI_STATIC const char* type_of_aggregation_string(
    ifcopenshell::aggregation_type* self
) {
    switch (self->type_of_aggregation()) {
    case ifcopenshell::aggregation_type::array_type:
        return "array";
    case ifcopenshell::aggregation_type::bag_type:
        return "bag";
    case ifcopenshell::aggregation_type::list_type:
        return "list";
    case ifcopenshell::aggregation_type::set_type:
        return "set";
    }
    throw std::runtime_error("Unknown aggregation type.");
}

inline int type_of_aggregation(ifcopenshell::inverse_attribute* self) {
    return static_cast<int>(self->type_of_aggregation());
}

inline IFCAPI_STATIC const char* type_of_aggregation_string(
    ifcopenshell::inverse_attribute* self
) {
    switch (self->type_of_aggregation()) {
    case ifcopenshell::inverse_attribute::bag_type:
        return "bag";
    case ifcopenshell::inverse_attribute::set_type:
        return "set";
    case ifcopenshell::inverse_attribute::unspecified_type:
        return "";
    }
    throw std::runtime_error("Unknown inverse aggregation type.");
}

inline std::vector<std::string> argument_types(ifcopenshell::entity* self) {
    std::vector<std::string> result;
    size_t index = 0;
    for (const auto* attr : self->all_attributes()) {
        auto argument_type = ifcopenshell::Argument_UNKNOWN;
        auto* parameter_type = attr->type_of_attribute();
        if (self->derived()[index++]) {
            argument_type = ifcopenshell::Argument_DERIVED;
        } else if (parameter_type != nullptr) {
            argument_type = ifcopenshell::from_parameter_type(parameter_type);
        }
        result.push_back(ifcopenshell::argument_type_to_string(argument_type));
    }
    return result;
}

inline IFCAPI_STATIC const char* kind(ifcopenshell::aggregation_type* self) {
    switch (self->type_of_aggregation()) {
    case ifcopenshell::aggregation_type::array_type:
        return "ARRAY";
    case ifcopenshell::aggregation_type::bag_type:
        return "BAG";
    case ifcopenshell::aggregation_type::list_type:
        return "LIST";
    case ifcopenshell::aggregation_type::set_type:
        return "SET";
    }
    throw std::runtime_error("Unknown aggregation type.");
}

inline std::size_t size(std::vector<express::base>& self) {
    return self.size();
}

inline std::optional<express::base> get(
    std::vector<express::base>& self,
    std::size_t index
) {
    if (index >= self.size()) {
        throw std::out_of_range("Instance list index out of range.");
    }
    return self[static_cast<int>(index)];
}

inline int operator_token_ptr(std::size_t start, const std::string& data) {
    const char value = data.empty() ? '$' : data.front();
    return static_cast<int>(ifcopenshell::token(start, value).type);
}

inline int general_token_ptr(std::size_t start, const std::string& token) {
    return static_cast<int>(ifcopenshell::token(start, ifcopenshell::token::Token_STRING, token).type);
}

} // namespace ifcparse::bindings

#endif // IFCWRAP_BINDING_GENERATOR_IFCPARSE_SPEC_HPP
