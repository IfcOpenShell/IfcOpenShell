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

#ifdef _MSC_VER
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef NOMSG
#define NOMSG NOMSG
#endif
#ifndef NODRAWTEXT
#define NODRAWTEXT NODRAWTEXT
#endif
#ifndef NOGDI
#define NOGDI NOGDI
#endif
#ifndef NOSERVICE
#define NOSERVICE NOSERVICE
#endif
#ifndef NOKERNEL
#define NOKERNEL NOKERNEL
#endif
#ifndef NOUSER
#define NOUSER NOUSER
#endif
#ifndef NOMCX
#define NOMCX NOMCX
#endif
#ifndef NOIME
#define NOIME NOIME
#endif
#include <Windows.h>
#endif

#include "argument.h"
#include "express.h"
#include "exception.h"
#include "utils.h"
#include "file.h"

#include <algorithm>
#include <boost/algorithm/string/replace.hpp>
#include <boost/optional.hpp>

static const char* const argument_type_string[] = {
    "NULL",
    "DERIVED",
    "INT",
    "BOOL",
    "LOGICAL",
    "DOUBLE",
    "STRING",
    "BINARY",
    "ENUMERATION",
    "ENTITY INSTANCE",

    "EMPTY AGGREGATE",
    "AGGREGATE OF INT",
    "AGGREGATE OF DOUBLE",
    "AGGREGATE OF STRING",
    "AGGREGATE OF BINARY",
    "AGGREGATE OF ENTITY INSTANCE",

    "AGGREGATE OF EMPTY AGGREGATE",
    "AGGREGATE OF AGGREGATE OF INT",
    "AGGREGATE OF AGGREGATE OF DOUBLE",
    "AGGREGATE OF AGGREGATE OF ENTITY INSTANCE",

    "UNKNOWN"};

const char* ifcopenshell::argument_type_to_string(argument_type argument_type) {
    return argument_type_string[static_cast<int>(argument_type)];
}

bool ifcopenshell::valid_binary_string(const std::string& str) {
    for (std::string::const_iterator it = str.begin(); it != str.end(); ++it) {
        if (*it != '0' && *it != '1') {
            return false;
        }
    }
    return true;
}

void ifcopenshell::sanitate_material_name(std::string& str) {
    // Spaces in material names have been observed to cause problems with obj and dae importers.
    // Handle other potential problematic characters here too if observing problems.
    boost::replace_all(str, " ", "_");
}

void ifcopenshell::escape_xml(std::string& str) {
    boost::replace_all(str, "&", "&amp;");
    boost::replace_all(str, "\"", "&quot;");
    boost::replace_all(str, "'", "&apos;");
    boost::replace_all(str, "<", "&lt;");
    boost::replace_all(str, ">", "&gt;");
}

void ifcopenshell::unescape_xml(std::string& str) {
    boost::replace_all(str, "&amp;", "&");
    boost::replace_all(str, "&quot;", "\"");
    boost::replace_all(str, "&apos;", "'");
    boost::replace_all(str, "&lt;", "<");
    boost::replace_all(str, "&gt;", ">");
}

void instance_data::populate_derived_() {
    if (auto* ent = declaration_->as_entity()) {
        for (auto it = ent->derived().begin(); it != ent->derived().end(); ++it) {
            if (*it) {
                set_attribute_value(
                    std::distance(ent->derived().begin(), it),
                    derived{});
            }
        }
    }
}

attribute_value express::Entity::get(const std::string& name) const {
    auto attrs = declaration().as_entity()->all_attributes();
    auto iter = attrs.begin();
    size_t idx = 0;
    for (; iter != attrs.end(); ++iter, ++idx) {
        if ((*iter)->name() == name) {
            return get_attribute_value(idx);
        }
    }
    throw ifcopenshell::exception(name + " not found on " + declaration().name());
}

std::vector<express::Entity> express::Entity::get_inverse(const std::string& name) const {
    const std::vector<const ifcopenshell::inverse_attribute*> attrs = declaration().as_entity()->all_inverse_attributes();
    std::vector<const ifcopenshell::inverse_attribute*>::const_iterator iter = attrs.begin();
    for (; iter != attrs.end(); ++iter) {
        if ((*iter)->name() == name) {
            return file()->get_inverse(
                id(),
                (*iter)->entity_reference(),
                (int)(*iter)->entity_reference()->attribute_index((*iter)->attribute_reference()));
        }
    }
    throw ifcopenshell::exception(name + " not found on " + declaration().name());
}

/*
void ifcopenshell::IfcBaseClass::data(instance_data* data) {
    delete data_;
    data_ = data;
}
*/

ifcopenshell::argument_type ifcopenshell::make_aggregate(ifcopenshell::argument_type elem_type) {
    switch (elem_type) {
    case ifcopenshell::Argument_INT:
        return ifcopenshell::Argument_AGGREGATE_OF_INT;
    case ifcopenshell::Argument_DOUBLE:
        return ifcopenshell::Argument_AGGREGATE_OF_DOUBLE;
    case ifcopenshell::Argument_STRING:
        return ifcopenshell::Argument_AGGREGATE_OF_STRING;
    case ifcopenshell::Argument_BINARY:
        return ifcopenshell::Argument_AGGREGATE_OF_BINARY;
    case ifcopenshell::Argument_ENTITY_INSTANCE:
        return ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE;
    case ifcopenshell::Argument_AGGREGATE_OF_INT:
        return ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_INT;
    case ifcopenshell::Argument_AGGREGATE_OF_DOUBLE:
        return ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE;
    case ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE:
        return ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE;
    case ifcopenshell::Argument_EMPTY_AGGREGATE:
        return ifcopenshell::Argument_AGGREGATE_OF_EMPTY_AGGREGATE;
    default:
        return ifcopenshell::Argument_UNKNOWN;
    }
}

ifcopenshell::argument_type ifcopenshell::from_parameter_type(const ifcopenshell::parameter_type* pt) {
    // TODO: How to detect derived types here without a reference to the refering entity?

    const ifcopenshell::aggregation_type* at = pt->as_aggregation_type();
    const ifcopenshell::named_type* nt = pt->as_named_type();
    const ifcopenshell::simple_type* st = pt->as_simple_type();

    if (at != nullptr) {
        return make_aggregate(from_parameter_type(at->type_of_element()));
    }
    if (nt != nullptr) {
        if (nt->declared_type()->as_entity() != nullptr) {
            return ifcopenshell::Argument_ENTITY_INSTANCE;
        }
        if (nt->declared_type()->as_enumeration_type() != nullptr) {
            return ifcopenshell::Argument_ENUMERATION;
        }
        if (nt->declared_type()->as_select_type() != nullptr) {
            return ifcopenshell::Argument_ENTITY_INSTANCE;
        }
        if (nt->declared_type()->as_type_declaration() != nullptr) {
            return from_parameter_type(nt->declared_type()->as_type_declaration()->declared_type());
        }
    } else if (st != nullptr) {
        switch (st->declared_type()) {
        case ifcopenshell::simple_type::binary_type:
            return ifcopenshell::Argument_BINARY;
        case ifcopenshell::simple_type::boolean_type:
            return ifcopenshell::Argument_BOOL;
        case ifcopenshell::simple_type::integer_type:
            return ifcopenshell::Argument_INT;
        case ifcopenshell::simple_type::logical_type:
            return ifcopenshell::Argument_LOGICAL;
        case ifcopenshell::simple_type::number_type:
            return ifcopenshell::Argument_DOUBLE;
        case ifcopenshell::simple_type::real_type:
            return ifcopenshell::Argument_DOUBLE;
        case ifcopenshell::simple_type::string_type:
            return ifcopenshell::Argument_STRING;
        case ifcopenshell::simple_type::datatype_COUNT:
            throw ifcopenshell::exception("Invalid simple type encountered");
        }
    }

    return ifcopenshell::Argument_UNKNOWN;
}

#ifdef _MSC_VER
std::string ifcopenshell::path::to_utf8(const std::wstring& str) {
    int buffer_size = WideCharToMultiByte(CP_UTF8, 0, str.c_str(), -1, 0, 0, 0, 0);
    char* buffer = new char[buffer_size];
    WideCharToMultiByte(CP_UTF8, 0, str.c_str(), -1, buffer, buffer_size, 0, 0);
    std::string str_utf8(buffer);
    delete[] buffer;
    return str_utf8;
}

std::wstring ifcopenshell::path::from_utf8(const std::string& str) {
    int buffer_size = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), -1, 0, 0);
    wchar_t* buffer = new wchar_t[buffer_size];
    MultiByteToWideChar(CP_UTF8, 0, str.c_str(), -1, buffer, buffer_size);
    std::wstring str_wide(buffer);
    delete[] buffer;
    return str_wide;
}

IFC_PARSE_API bool ifcopenshell::path::rename_file(const std::string& old_filename, const std::string& new_filename) {
    std::wstring old_filename_w = from_utf8(old_filename);
    std::wstring new_filename_w = from_utf8(new_filename);
    delete_file(new_filename);
    const bool success = !!MoveFileW(old_filename_w.c_str(), new_filename_w.c_str());
    return success;
}

IFC_PARSE_API bool ifcopenshell::path::delete_file(const std::string& filename) {
    std::wstring filename_w = from_utf8(filename);
    const bool success = !!DeleteFileW(filename_w.c_str());
    return success;
}

#else

IFC_PARSE_API bool ifcopenshell::path::rename_file(const std::string& old_filename, const std::string& new_filename) {
    // Whether or not rename() replaces an existing file is implementation-specific,
    // so remove() possible existing file always.
    delete_file(new_filename);
    return std::rename(old_filename.c_str(), new_filename.c_str()) == 0;
}

IFC_PARSE_API bool ifcopenshell::path::delete_file(const std::string& filename) {
    return std::remove(filename.c_str()) != 0;
}

#endif
