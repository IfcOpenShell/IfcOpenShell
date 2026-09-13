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
#include "swar.h"

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
    const char* skip_string_(std::string* raw) const;

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

    // The consumer-driven counterpart of next() for the lazy index: scans one
    // instance's attribute list, from just past its opening parenthesis to
    // just past the terminating semicolon, decoding nothing. Strings are
    // skipped (doubled quotes included), comments and whitespace go through
    // the same helpers next() uses, and only references are read:
    // sink.reference(name, attribute) is called for each one with the index
    // of the top-level attribute it sits in, and sink.first_string(raw) once
    // if the first attribute is a string, with its undecoded text. Returns
    // nullptr on success or the reason the instance is malformed, in which
    // case the caller falls back to the full parser.
    template <typename Sink>
    const char* scan_attributes(Sink& sink);
    // void TokenString(size_t offset, std::string& result);
};

template <typename Reader>
template <typename Sink>
const char* spf_lexer<Reader>::scan_attributes(Sink& sink) {
    int depth = 1;
    int attribute = 0;
    while ((skip_whitespace() != 0U) || (skip_comment() != 0U)) {
    }
    if (!stream->eof() && stream->peek() == '\'') {
        stream->increment();
        std::string& raw = get_temp_string();
        raw.clear();
        const char* failure = skip_string_(&raw);
        pop_pool_entry();
        if (failure != nullptr) {
            return failure;
        }
        sink.first_string(raw);
    }
    // Span by span: the plain bytes are walked with a pointer, eight at a
    // time while none of them matters; whatever cannot be finished inside
    // the span (a string, a reference, a comment) continues through the
    // cursor, which crosses page boundaries by itself.
    while (true) {
        const auto span = stream->span();
        const char* data = span.first;
        const size_t length = span.second;
        if (length == 0) {
            return "file ends inside an instance";
        }
        size_t i = 0;
        bool consumed = false;  // the cursor was moved past what this span handled
        while (i < length && !consumed) {
            while (i + 8 <= length) {
                uint64_t x;
                std::memcpy(&x, data + i, sizeof(x));
                if (SWAR::has_scan_char(x) != 0) {
                    break;
                }
                i += 8;
            }
            if (i == length) {
                break;
            }
            switch (data[i]) {
            case '\'': {
                stream->increment(i + 1);
                const char* failure = skip_string_(nullptr);
                if (failure != nullptr) {
                    return failure;
                }
                consumed = true;
                break;
            }
            case '(':
                ++depth;
                ++i;
                break;
            case ')':
                if (--depth == 0) {
                    stream->increment(i + 1);
                    while ((skip_whitespace() != 0U) || (skip_comment() != 0U)) {
                    }
                    if (stream->eof() || stream->peek() != ';') {
                        return "expected ; after )";
                    }
                    stream->increment();
                    return nullptr;
                }
                ++i;
                break;
            case ',':
                if (depth == 1) {
                    ++attribute;
                }
                ++i;
                break;
            case '#': {
                uint32_t name = 0;
                size_t j = i + 1;
                while (j < length && data[j] >= '0' && data[j] <= '9') {
                    name = name * 10 + (uint32_t)(data[j] - '0');
                    ++j;
                }
                size_t digits = j - i - 1;
                if (j == length) {
                    // The digits may continue on the next page.
                    stream->increment(j);
                    while (!stream->eof()) {
                        const char digit = stream->peek();
                        if (digit < '0' || digit > '9') {
                            break;
                        }
                        name = name * 10 + (uint32_t)(digit - '0');
                        stream->increment();
                        ++digits;
                    }
                    consumed = true;
                } else {
                    i = j;
                }
                if (digits == 0 || digits > 9) {
                    return "bad instance name in a reference";
                }
                sink.reference(name, attribute);
                break;
            }
            case '/':
                stream->increment(i);
                if (skip_comment() == 0) {
                    return "unexpected /";
                }
                consumed = true;
                break;
            case ';':
                return "; inside an instance";
            default:
                ++i;
                break;
            }
        }
        if (!consumed) {
            stream->increment(i);
        }
    }
}

IFC_PARSE_API std::vector<express::base> traverse(const express::base& instance, int max_depth = -1);

IFC_PARSE_API std::vector<express::base> traverse_breadth_first(const express::base& instance, int max_depth = -1);
} // namespace ifcopenshell

IFC_PARSE_API std::ostream& operator<<(std::ostream& stream, const ifcopenshell::file& file);

#endif
