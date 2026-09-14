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

/// What a pass over the tokens has to produce. The parser needs every
/// value; the lazy index only needs to know where the tokens are and which
/// of them are instance names, so it ends strings without decoding them and
/// passes over numbers, enumerations and binaries. The choice is a template
/// parameter of spf_lexer::next(), so each pass compiles to its own loop.
struct full_tokens {
    static constexpr bool decode_strings = true;
    static constexpr bool decode_values = true;
    static constexpr bool keep_keywords = true;
};
struct index_tokens {
    static constexpr bool decode_strings = false;
    static constexpr bool decode_values = false;
    static constexpr bool keep_keywords = true;
};
/// Inside an attribute list the index only looks at operators and names, so
/// a keyword (an inline typed value such as IFCLABEL), an enumeration or a
/// binary comes back as Token_LITERAL without its text being copied.
struct attribute_tokens {
    static constexpr bool decode_strings = false;
    static constexpr bool decode_values = false;
    static constexpr bool keep_keywords = false;
};

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
    // The next token. With index_tokens a string, number, enumeration or
    // binary comes back as Token_LITERAL (Token_STRING for a string) with
    // only its position; names, keywords and operators are always read.
    template <typename Policy = full_tokens>
    token next();
    ~spf_lexer();
    // void TokenString(size_t offset, std::string& result);
};

IFC_PARSE_API std::vector<express::base> traverse(const express::base& instance, int max_depth = -1);

IFC_PARSE_API std::vector<express::base> traverse_breadth_first(const express::base& instance, int max_depth = -1);
} // namespace ifcopenshell

IFC_PARSE_API std::ostream& operator<<(std::ostream& stream, const ifcopenshell::file& file);

#endif
