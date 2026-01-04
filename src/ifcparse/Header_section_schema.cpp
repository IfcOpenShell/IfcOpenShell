
#include "../ifcparse/Header_section_schema.h"
#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcFile.h"

#include <map>

const char* const Header_section_schema::Identifier = "HEADER_SECTION_SCHEMA";

using namespace IfcParse;

namespace {
    template <typename T, typename U>
    std::vector<T> cast_vector(const std::vector<U>& vs) {
        std::vector<T> result;
        for (const auto& v : vs) {
            if constexpr (std::is_base_of_v<T, U> || std::is_same_v<T, U>) {
                // For a base or identity transform we can just rely on static cast
                result.push_back(v);
            } else if constexpr (std::is_base_of_v<express::Select, U> && std::is_same_v<T, express::Base>) {
                // From a select to concrete we simply call the appropriate method
                result.push_back(v.concrete());
            } else {
                if (auto u = v.as<T>()) {
                    result.push_back(u);
                }
            }
        }
        return result;
    }

    template <typename T, typename U>
    std::vector<std::vector<T>> cast_vector_vector(const std::vector<std::vector<U>>& vs) {
        std::vector<std::vector<T>> result;
        for (const auto& v : vs) {
            result.push_back(cast_vector<T>(v));
        }
        return result;
    }
}

// External definitions
extern declaration* HEADER_SECTION_SCHEMA_types[5];



// Function implementations for schema_name
const IfcParse::type_declaration& Header_section_schema::schema_name::Class() { return *((IfcParse::type_declaration*)HEADER_SECTION_SCHEMA_types[3]); }
Header_section_schema::schema_name::operator std::string() const { return get_attribute_value(0); }

// Function implementations for time_stamp_text
const IfcParse::type_declaration& Header_section_schema::time_stamp_text::Class() { return *((IfcParse::type_declaration*)HEADER_SECTION_SCHEMA_types[4]); }
Header_section_schema::time_stamp_text::operator std::string() const { return get_attribute_value(0); }


// Function implementations for file_description
std::vector< std::string > /*[1:?]*/ Header_section_schema::file_description::description() const {  std::vector< std::string > /*[1:?]*/ v = get_attribute_value(0); return v; }
void Header_section_schema::file_description::setdescription(const std::vector< std::string > /*[1:?]*/& v) { set_attribute_value(0, v);if constexpr (false)unset_attribute_value(0); }
std::string Header_section_schema::file_description::implementation_level() const {  std::string v = get_attribute_value(1); return v; }
void Header_section_schema::file_description::setimplementation_level(const std::string& v) { set_attribute_value(1, v);if constexpr (false)unset_attribute_value(1); }


// const IfcParse::entity& Header_section_schema::file_description::declaration() const { return *((IfcParse::entity*)HEADER_SECTION_SCHEMA_types[0]); }
const IfcParse::entity& Header_section_schema::file_description::Class() { return *((IfcParse::entity*)HEADER_SECTION_SCHEMA_types[0]); }
// Header_section_schema::file_description::file_description(const std::weak_ptr<InstanceData>& e) : express::Entity(e) { }
// Header_section_schema::file_description::file_description(std::vector< std::string > /*[1:?]*/ v1_description, std::string v2_implementation_level) : express::Entity(const std::weak_ptr<InstanceData>&(in_memory_attribute_storage(2))) { set_attribute_value(0, (v1_description));set_attribute_value(1, (v2_implementation_level));; populate_derived(); }

// Function implementations for file_name
std::string Header_section_schema::file_name::name() const {  std::string v = get_attribute_value(0); return v; }
void Header_section_schema::file_name::setname(const std::string& v) { set_attribute_value(0, v);if constexpr (false)unset_attribute_value(0); }
std::string Header_section_schema::file_name::time_stamp() const {  std::string v = get_attribute_value(1); return v; }
void Header_section_schema::file_name::settime_stamp(const std::string& v) { set_attribute_value(1, v);if constexpr (false)unset_attribute_value(1); }
std::vector< std::string > /*[1:?]*/ Header_section_schema::file_name::author() const {  std::vector< std::string > /*[1:?]*/ v = get_attribute_value(2); return v; }
void Header_section_schema::file_name::setauthor(const std::vector< std::string > /*[1:?]*/& v) { set_attribute_value(2, v);if constexpr (false)unset_attribute_value(2); }
std::vector< std::string > /*[1:?]*/ Header_section_schema::file_name::organization() const {  std::vector< std::string > /*[1:?]*/ v = get_attribute_value(3); return v; }
void Header_section_schema::file_name::setorganization(const std::vector< std::string > /*[1:?]*/& v) { set_attribute_value(3, v);if constexpr (false)unset_attribute_value(3); }
std::string Header_section_schema::file_name::preprocessor_version() const {  std::string v = get_attribute_value(4); return v; }
void Header_section_schema::file_name::setpreprocessor_version(const std::string& v) { set_attribute_value(4, v);if constexpr (false)unset_attribute_value(4); }
std::string Header_section_schema::file_name::originating_system() const {  std::string v = get_attribute_value(5); return v; }
void Header_section_schema::file_name::setoriginating_system(const std::string& v) { set_attribute_value(5, v);if constexpr (false)unset_attribute_value(5); }
std::string Header_section_schema::file_name::authorization() const {  std::string v = get_attribute_value(6); return v; }
void Header_section_schema::file_name::setauthorization(const std::string& v) { set_attribute_value(6, v);if constexpr (false)unset_attribute_value(6); }


// const IfcParse::entity& Header_section_schema::file_name::declaration() const { return *((IfcParse::entity*)HEADER_SECTION_SCHEMA_types[1]); }
const IfcParse::entity& Header_section_schema::file_name::Class() { return *((IfcParse::entity*)HEADER_SECTION_SCHEMA_types[1]); }
// Header_section_schema::file_name::file_name(const std::weak_ptr<InstanceData>& e) : express::Entity(e) { }
// Header_section_schema::file_name::file_name(std::string v1_name, std::string v2_time_stamp, std::vector< std::string > /*[1:?]*/ v3_author, std::vector< std::string > /*[1:?]*/ v4_organization, std::string v5_preprocessor_version, std::string v6_originating_system, std::string v7_authorization) : express::Entity(const std::weak_ptr<InstanceData>&(in_memory_attribute_storage(7))) { set_attribute_value(0, (v1_name));set_attribute_value(1, (v2_time_stamp));set_attribute_value(2, (v3_author));set_attribute_value(3, (v4_organization));set_attribute_value(4, (v5_preprocessor_version));set_attribute_value(5, (v6_originating_system));set_attribute_value(6, (v7_authorization));; populate_derived(); }

// Function implementations for file_schema
std::vector< std::string > /*[1:?]*/ Header_section_schema::file_schema::schema_identifiers() const {  std::vector< std::string > /*[1:?]*/ v = get_attribute_value(0); return v; }
void Header_section_schema::file_schema::setschema_identifiers(const std::vector< std::string > /*[1:?]*/& v) { set_attribute_value(0, v);if constexpr (false)unset_attribute_value(0); }


// const IfcParse::entity& Header_section_schema::file_schema::declaration() const { return *((IfcParse::entity*)HEADER_SECTION_SCHEMA_types[2]); }
const IfcParse::entity& Header_section_schema::file_schema::Class() { return *((IfcParse::entity*)HEADER_SECTION_SCHEMA_types[2]); }
// Header_section_schema::file_schema::file_schema(const std::weak_ptr<InstanceData>& e) : express::Entity(e) { }
// Header_section_schema::file_schema::file_schema(std::vector< std::string > /*[1:?]*/ v1_schema_identifiers) : express::Entity(const std::weak_ptr<InstanceData>&(in_memory_attribute_storage(1))) { set_attribute_value(0, (v1_schema_identifiers));; populate_derived(); }

