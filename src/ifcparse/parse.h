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
 * This file provides functions for loading an IFC file into memory and access  *
 * its entities either by ID, by an IfcSchema::Type or by reference             *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCPARSE_H
#define IFCPARSE_H

#include "argument.h"
#include "ifc_parse_api.h"
#include "express.h"
#include "character_decoder.h"
#include "file_reader.h"
#include "macros.h"
#include "storage.h"

#include <boost/dynamic_bitset.hpp>
#include <memory>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>


extern IFC_PARSE_API const char *IFCOPENSHELL_VERSION;

namespace ifcopenshell {

IFC_PARSE_API std::string encode_spf_string(const std::string& value);

IFC_PARSE_API std::string decode_spf_string(const std::string& value);

/// A stream of tokens to be read from a file_reader.
template <typename Reader>
class IFC_PARSE_API spf_lexer {
  private:
    character_decoder<Reader>* decoder_;
    ifcopenshell::logger& logger_;

    size_t skip_whitespace() const;
    size_t skip_comment() const;

    mutable std::vector<std::unique_ptr<std::array<std::string, 16>>> stringpool_;
    mutable size_t pool_index = 0;

  public:

    spf_lexer(const spf_lexer&) = delete;
    spf_lexer& operator=(const spf_lexer&) = delete;

    std::string& get_temp_string() const;
    void reset_pool() const {
        pool_index = 0;
    }
    void pop_pool_entry() {
        if (pool_index > 0) {
            --pool_index;
        }
    }

    Reader* stream;
    // file* file;
    spf_lexer(Reader* stream, ifcopenshell::logger& logger = ifcopenshell::logger::root());
    token next();
    ~spf_lexer();
    // void TokenString(size_t offset, std::string& result);
};

IFC_PARSE_API std::vector<express::base> traverse(const express::base& instance, int max_depth = -1);

IFC_PARSE_API std::vector<express::base> traverse_breadth_first(const express::base& instance, int max_depth = -1);
} // namespace ifcopenshell

IFC_PARSE_API std::ostream& operator<<(std::ostream& stream, const ifcopenshell::file& file);

#endif
