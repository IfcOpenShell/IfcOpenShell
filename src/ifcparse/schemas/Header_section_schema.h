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

#ifndef HEADER_SECTION_SCHEMA_H
#define HEADER_SECTION_SCHEMA_H

#include <string>
#include <vector>
#include <optional>

#include "../../ifcparse/ifc_parse_api.h"

#include "../../ifcparse/express.h"
#include "../../ifcparse/schema.h"
#include "../../ifcparse/exception.h"
#include "../../ifcparse/argument.h"

namespace ifcopenshell {
class file;
class spf_header;
} // namespace ifcopenshell

struct Header_section_schema {

IFC_SCHEMA_API static const ifcopenshell::schema_definition& get_schema();

IFC_SCHEMA_API static void clear_schema();

static const char* const Identifier;

// Forward definitions
class file_description; class file_name; class file_schema; class schema_name; class time_stamp_text; 


class IFC_SCHEMA_API schema_name : public express::declared_type {
public:
    using express::declared_type::declared_type;

    static const ifcopenshell::type_declaration& Class();
    schema_name initialize(std::string v);
    operator std::string() const;
};

class IFC_SCHEMA_API time_stamp_text : public express::declared_type {
public:
    using express::declared_type::declared_type;

    static const ifcopenshell::type_declaration& Class();
    time_stamp_text initialize(std::string v);
    operator std::string() const;
};



class IFC_SCHEMA_API file_description : public express::entity {
public:
    using express::entity::entity;

    std::vector< std::string > /*[1:?]*/ description() const;
    void setdescription(const std::vector< std::string > /*[1:?]*/& v);
    std::string implementation_level() const;
    void setimplementation_level(const std::string& v);
    
    static const ifcopenshell::entity& Class();
    file_description initialize(std::vector< std::string > /*[1:?]*/ v1_description, std::string v2_implementation_level);
};

class IFC_SCHEMA_API file_name : public express::entity {
public:
    using express::entity::entity;

    std::string name() const;
    void setname(const std::string& v);
    std::string time_stamp() const;
    void settime_stamp(const std::string& v);
    std::vector< std::string > /*[1:?]*/ author() const;
    void setauthor(const std::vector< std::string > /*[1:?]*/& v);
    std::vector< std::string > /*[1:?]*/ organization() const;
    void setorganization(const std::vector< std::string > /*[1:?]*/& v);
    std::string preprocessor_version() const;
    void setpreprocessor_version(const std::string& v);
    std::string originating_system() const;
    void setoriginating_system(const std::string& v);
    std::string authorization() const;
    void setauthorization(const std::string& v);
    
    static const ifcopenshell::entity& Class();
    file_name initialize(std::string v1_name, std::string v2_time_stamp, std::vector< std::string > /*[1:?]*/ v3_author, std::vector< std::string > /*[1:?]*/ v4_organization, std::string v5_preprocessor_version, std::string v6_originating_system, std::string v7_authorization);
};

class IFC_SCHEMA_API file_schema : public express::entity {
public:
    using express::entity::entity;

    std::vector< std::string > /*[1:?]*/ schema_identifiers() const;
    void setschema_identifiers(const std::vector< std::string > /*[1:?]*/& v);
    
    static const ifcopenshell::entity& Class();
    file_schema initialize(std::vector< std::string > /*[1:?]*/ v1_schema_identifiers);
};

};

#endif
