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

/********************************************************************************
 *                                                                              *
 * This file has been generated from header_schema.exp. Do not make modifications*
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/

#include "../../ifcparse/schemas/Header_section_schema.h"
#include "../../ifcparse/schema.h"
#include "../../ifcparse/exception.h"
#include "../../ifcparse/file.h"

#include <map>

const char* const Header_section_schema::Identifier = "HEADER_SECTION_SCHEMA";

using namespace ifcopenshell;

// External definitions
extern declaration* HEADER_SECTION_SCHEMA_types[5];



// Function implementations for schema_name
const ifcopenshell::type_declaration& Header_section_schema::schema_name::Class() { return *((ifcopenshell::type_declaration*)HEADER_SECTION_SCHEMA_types[3]); }
Header_section_schema::schema_name Header_section_schema::schema_name::initialize(std::string v) { set_attribute_value(0, (v));; return *this; }
Header_section_schema::schema_name::operator std::string() const { return get_attribute_value(0); }

// Function implementations for time_stamp_text
const ifcopenshell::type_declaration& Header_section_schema::time_stamp_text::Class() { return *((ifcopenshell::type_declaration*)HEADER_SECTION_SCHEMA_types[4]); }
Header_section_schema::time_stamp_text Header_section_schema::time_stamp_text::initialize(std::string v) { set_attribute_value(0, (v));; return *this; }
Header_section_schema::time_stamp_text::operator std::string() const { return get_attribute_value(0); }


// Function implementations for file_description
std::vector< std::string > /*[1:?]*/ Header_section_schema::file_description::description() const {  std::vector< std::string > /*[1:?]*/ v = get_attribute_value(0); return v; }
void Header_section_schema::file_description::setdescription(const std::vector< std::string > /*[1:?]*/& v) { set_attribute_value(0, v);if constexpr (false)unset_attribute_value(0); }
std::string Header_section_schema::file_description::implementation_level() const {  std::string v = get_attribute_value(1); return v; }
void Header_section_schema::file_description::setimplementation_level(const std::string& v) { set_attribute_value(1, v);if constexpr (false)unset_attribute_value(1); }


const ifcopenshell::entity& Header_section_schema::file_description::Class() { return *((ifcopenshell::entity*)HEADER_SECTION_SCHEMA_types[0]); }
Header_section_schema::file_description Header_section_schema::file_description::initialize(std::vector< std::string > /*[1:?]*/ v1_description, std::string v2_implementation_level) { set_attribute_value(0, (v1_description));set_attribute_value(1, (v2_implementation_level));; return *this; }

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


const ifcopenshell::entity& Header_section_schema::file_name::Class() { return *((ifcopenshell::entity*)HEADER_SECTION_SCHEMA_types[1]); }
Header_section_schema::file_name Header_section_schema::file_name::initialize(std::string v1_name, std::string v2_time_stamp, std::vector< std::string > /*[1:?]*/ v3_author, std::vector< std::string > /*[1:?]*/ v4_organization, std::string v5_preprocessor_version, std::string v6_originating_system, std::string v7_authorization) { set_attribute_value(0, (v1_name));set_attribute_value(1, (v2_time_stamp));set_attribute_value(2, (v3_author));set_attribute_value(3, (v4_organization));set_attribute_value(4, (v5_preprocessor_version));set_attribute_value(5, (v6_originating_system));set_attribute_value(6, (v7_authorization));; return *this; }

// Function implementations for file_schema
std::vector< std::string > /*[1:?]*/ Header_section_schema::file_schema::schema_identifiers() const {  std::vector< std::string > /*[1:?]*/ v = get_attribute_value(0); return v; }
void Header_section_schema::file_schema::setschema_identifiers(const std::vector< std::string > /*[1:?]*/& v) { set_attribute_value(0, v);if constexpr (false)unset_attribute_value(0); }


const ifcopenshell::entity& Header_section_schema::file_schema::Class() { return *((ifcopenshell::entity*)HEADER_SECTION_SCHEMA_types[2]); }
Header_section_schema::file_schema Header_section_schema::file_schema::initialize(std::vector< std::string > /*[1:?]*/ v1_schema_identifiers) { set_attribute_value(0, (v1_schema_identifiers));; return *this; }

