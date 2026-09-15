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

// The tokenizer's body, spf_lexer::scan(), and what it needs. It lives in a
// header so a consumer's callbacks inline into the loop; next() is the
// consumer that stops after one token.

#ifndef IFCPARSE_SPF_SCAN_H
#define IFCPARSE_SPF_SCAN_H

#include "parse.h"

#include <charconv>
#include <cstring>
#include <string>

namespace ifcopenshell {

#if defined(__APPLE__) || defined(__EMSCRIPTEN__)
IFC_PARSE_API double parse_double_c(const char* start, char** end);
#endif

template <typename T>
inline bool parse_num_(const char* pStart, size_t size, T& val) {
    if (size == 0) {
        return false;
    }
    if (*pStart == '+') {
        ++pStart;
        --size;
        if (size == 0) {
            return false;
        }
    }
    if constexpr (std::is_floating_point_v<T>) {
#if defined(__APPLE__) || defined(__EMSCRIPTEN__)
        // pStart is NUL-terminated at pStart + size (callers pass c_str()), so
        // strtod_l stops exactly at the end of a well-formed number. from_chars
        // is not instantiated for double here — its float overload is =deleted
        // in libc++ (Apple's and Emscripten's).
        char* pEnd = nullptr;
        const double result = parse_double_c(pStart, &pEnd);
        if (pEnd != pStart + size) {
            return false;
        }
        val = static_cast<T>(result);
        return true;
#else
        auto re = std::from_chars(pStart, pStart + size, val);
        return re.ec == std::errc() && re.ptr == pStart + size;
#endif
    } else {
        auto re = std::from_chars(pStart, pStart + size, val);
        return re.ec == std::errc() && re.ptr == pStart + size;
    }
}


// These helpers sit on the tokenizer's innermost loop; left to the
// compiler's heuristics they end up as calls, one per eight bytes.
#if defined(_MSC_VER)
#define IFC_SWAR_INLINE __forceinline
#else
#define IFC_SWAR_INLINE inline __attribute__((always_inline))
#endif

namespace SWAR {
constexpr uint32_t ONES32 = 0x01010101u;
constexpr uint32_t HIGHS32 = 0x80808080u;
constexpr uint64_t ONES = 0x0101010101010101ull;
constexpr uint64_t HIGHS = 0x8080808080808080ull;

constexpr uint64_t splat(unsigned char c) {
    return ONES * c;
}

IFC_SWAR_INLINE uint32_t has_zero_byte(uint32_t x) {
    return (x - ONES32) & ~x & HIGHS32;
}

IFC_SWAR_INLINE uint64_t has_zero_byte(uint64_t x) {
    return (x - ONES) & ~x & HIGHS;
}

IFC_SWAR_INLINE uint32_t eq_mask(uint32_t x, uint32_t c) {
    return has_zero_byte(x ^ c);
}

IFC_SWAR_INLINE uint64_t eq_mask(uint64_t x, uint64_t c) {
    return has_zero_byte(x ^ c);
}

namespace chars {
constexpr uint64_t lpar = splat('(');
constexpr uint64_t rpar = splat(')');
constexpr uint64_t eq = splat('=');
constexpr uint64_t comma = splat(',');
constexpr uint64_t semi = splat(';');
constexpr uint64_t slash = splat('/');

constexpr uint64_t space = splat(' ');
constexpr uint64_t cr = splat('\r');
constexpr uint64_t lf = splat('\n');
constexpr uint64_t tab = splat('\t');

constexpr uint64_t quote = splat('"');
constexpr uint64_t dot = splat('.');
} // namespace chars

template <bool IncludeDot = true>
IFC_SWAR_INLINE uint64_t has_special_char(uint64_t x) {
    return eq_mask(x, chars::lpar) |
           eq_mask(x, chars::rpar) |
           eq_mask(x, chars::eq) |
           eq_mask(x, chars::comma) |
           eq_mask(x, chars::semi) |
           eq_mask(x, chars::slash) |
           eq_mask(x, chars::space) |
           eq_mask(x, chars::cr) |
           eq_mask(x, chars::lf) |
           eq_mask(x, chars::tab) |
           eq_mask(x, chars::quote) |
           (IncludeDot ? eq_mask(x, chars::dot) : uint64_t{0});
}

template <bool IncludeDot = true>
IFC_SWAR_INLINE uint32_t has_special_char(uint32_t x) {
    return eq_mask(x, static_cast<uint32_t>(chars::lpar)) |
           eq_mask(x, static_cast<uint32_t>(chars::rpar)) |
           eq_mask(x, static_cast<uint32_t>(chars::eq)) |
           eq_mask(x, static_cast<uint32_t>(chars::comma)) |
           eq_mask(x, static_cast<uint32_t>(chars::semi)) |
           eq_mask(x, static_cast<uint32_t>(chars::slash)) |
           eq_mask(x, static_cast<uint32_t>(chars::space)) |
           eq_mask(x, static_cast<uint32_t>(chars::cr)) |
           eq_mask(x, static_cast<uint32_t>(chars::lf)) |
           eq_mask(x, static_cast<uint32_t>(chars::tab)) |
           eq_mask(x, static_cast<uint32_t>(chars::quote)) |
           (IncludeDot ? eq_mask(x, static_cast<uint32_t>(chars::dot)) : uint32_t{0});
}

}


inline bool is_token_delimiter(char c) {
    return c == '(' || c == ')' || c == '=' || c == ',' || c == ';' || c == '/';
}

// One pass over the tokens from the cursor, handing each to the consumer
// without building a token; each callback returns whether to go on. The
// consumer's constexpr flags decide what is decoded: decode_strings (else a
// string is ended, not decoded, and reported by its bounds), decode_values
// (else numbers, enumerations and binaries are reported as literals by
// position only) and keep_keywords (else a keyword is a literal too, so
// nothing is copied but a name's digits). Returns at the end of the input.
template <typename Reader>
template <typename Consumer>
void spf_lexer<Reader>::scan(Consumer& consumer) {
    while (true) {
        if (stream->eof()) {
            return;
        }

        auto pos = stream->tell();
        char character = stream->read();

        if (character == '/' || character == ' ' || character == '\r' || character == '\n' || character == '\t') {
            if (character == '/') {
                // skip_comment() wants to see the slash itself, so a comment
                // that follows the previous token without whitespace is skipped.
                stream->seek(pos);
            }
            while ((skip_whitespace() != 0U) || (skip_comment() != 0U)) {
            }
            if (stream->eof()) {
                return;
            }
            pos = stream->tell();
            character = stream->read();
        }

        // If the cursor is at [()=,;$*] we know token consists of single char
        if (character == '(' ||
            character == ')' ||
            character == '=' ||
            character == ',' ||
            character == ';' ||
            character == '$' ||
            character == '*')
        {
            if (!consumer.operator_(pos, character)) {
                return;
            }
            continue;
        }

        if (character == '\'') {
            // If a string is encountered defer processing to the character_decoder
            if constexpr (Consumer::decode_strings) {
                auto& str = get_temp_string();
                str = *decoder_;
                if (!consumer.string(pos, str)) {
                    return;
                }
            } else {
                decoder_->skip();
                if (!consumer.string(pos, stream->tell())) {
                    return;
                }
            }
            continue;
        }

        // Parse names directly when the complete spelling is in this span.
        // Whitespace, page splits and invalid names use the normal token loop.
        if (character == '#') {
            const auto span = stream->span();
            if (span.second) {
                const char* begin = span.first;
                const char* end = begin + span.second;
                const char* digits = begin + (*begin == '+');
                int value;
                const auto parsed = std::from_chars(digits, end, value);
                if (parsed.ec == std::errc() && parsed.ptr != end && is_token_delimiter(*parsed.ptr)) {
                    stream->increment(static_cast<size_t>(parsed.ptr - begin));
                    if (!consumer.identifier(pos, static_cast<uint32_t>(value))) {
                        return;
                    }
                    continue;
                }
            }
        }

        auto ttype = token::Token_NONE;
        if (character == '"') {
            ttype = token::Token_BINARY;
        } else if (character == '.') {
            ttype = token::Token_ENUMERATION;
        } else if (character == '#') {
            ttype = token::Token_IDENTIFIER;
        }
        std::string* text = nullptr;
        if (Consumer::keep_keywords || ttype == token::Token_IDENTIFIER) {
            text = &get_temp_string();
            if (ttype == token::Token_NONE) {
                text->assign(&character, 1);
            } else {
                text->clear();
            }
        }

        auto remaining = stream->remaining();
        while (remaining) {
            // Most index tokens are shorter than a word. Testing both word
            // widths at every byte costs more than the scalar delimiter check.
            if constexpr (Consumer::keep_keywords) {
                if (remaining >= 8) {
                    uint64_t x = stream->peek_u64();
                    if ((ttype == token::Token_NONE ? SWAR::has_special_char<false>(x) : SWAR::has_special_char<true>(x)) == 0) {
                        if (Consumer::keep_keywords || ttype == token::Token_IDENTIFIER) {
                            text->append(reinterpret_cast<const char*>(&x), 8);
                        }
                        stream->increment(8);
                        remaining -= 8;
                        continue;
                    }
                }
                if (remaining >= 4) {
                    uint32_t x = stream->peek_u32();
                    if ((ttype == token::Token_NONE ? SWAR::has_special_char<false>(x) : SWAR::has_special_char<true>(x)) == 0) {
                        if (Consumer::keep_keywords || ttype == token::Token_IDENTIFIER) {
                            text->append(reinterpret_cast<const char*>(&x), 4);
                        }
                        stream->increment(4);
                        remaining -= 4;
                        continue;
                    }
                }
            }

            // Read character and increment pointer if not starting a new token
            char c = stream->peek();
            if (is_token_delimiter(c)) {
                break;
            }
            if (!(c == ' ' || c == '\r' || c == '\n' || c == '\t')) {
                if ((ttype == token::Token_BINARY && c == '"') ||
                    (ttype == token::Token_ENUMERATION && c == '.')) {
                    // Skip
                } else if (Consumer::keep_keywords || ttype == token::Token_IDENTIFIER) {
                    text->push_back(c);
                }
            }
            stream->increment();
            remaining -= 1;
        }

        if (ttype == token::Token_IDENTIFIER) {
            auto& str = *text;
            int int_val;
            if (!parse_num_(str.c_str(), str.size(), int_val)) {
                throw invalid_token_exception(pos, str, "instance name");
            }
            pop_pool_entry();
            if (!consumer.identifier(pos, (uint32_t)int_val)) {
                return;
            }
            continue;
        }

        if constexpr (!Consumer::decode_values) {
            // Only names and keywords are read; everything else is a literal
            // whose position is all the consumer wants.
            if constexpr (Consumer::keep_keywords) {
                auto& str = *text;
                if (ttype == token::Token_NONE && !str.empty()) {
                    const char first = str.front();
                    if ((first >= 'A' && first <= 'Z') || (first >= 'a' && first <= 'z')) {
                        if (!consumer.keyword(pos, str)) {
                            return;
                        }
                        continue;
                    }
                }
            }
            if constexpr (Consumer::keep_keywords) {
                pop_pool_entry();
            }
            if (!consumer.literal(pos)) {
                return;
            }
            continue;
        } else {
            auto& str = *text;
            if (ttype == token::Token_ENUMERATION && str.size() == 1 && (str[0] == 'T' || str[0] == 'F' || str[0] == 'U')) {
                pop_pool_entry();
                if (!consumer.boolean(pos, str[0])) {
                    return;
                }
                continue;
            } else if (ttype == token::Token_NONE && !str.empty()) {
                int64_t int_val;
                double float_val;
                auto& first = str.front();
                if ((first >= 'A' && first <= 'Z') || (first >= 'a' && first <= 'z')) {
                    if (!consumer.keyword(pos, str)) {
                        return;
                    }
                    continue;
                } else if (parse_num_(str.c_str(), str.size(), int_val)) {
                    pop_pool_entry();
                    if (!consumer.integer(pos, int_val)) {
                        return;
                    }
                    continue;
                } else if (parse_num_(str.c_str(), str.size(), float_val)) {
                    pop_pool_entry();
                    if (!consumer.real(pos, float_val)) {
                        return;
                    }
                    continue;
                }
            } else if (ttype == token::Token_BINARY) {
                if (!consumer.binary(pos, str)) {
                    return;
                }
                continue;
            } else if (ttype == token::Token_ENUMERATION) {
                if (!consumer.enumeration(pos, str)) {
                    return;
                }
                continue;
            }

            throw invalid_token_exception(pos, str, "valid token");
        }
    }
}

// The consumer behind next(): builds one token and stops.
template <typename Policy>
struct token_consumer {
    static constexpr bool decode_strings = Policy::decode_strings;
    static constexpr bool decode_values = Policy::decode_values;
    static constexpr bool keep_keywords = Policy::keep_keywords;
    token result;
    bool operator_(size_t pos, char c) { result = token(pos, c); return false; }
    bool identifier(size_t pos, uint32_t name) { result = token(pos, token::Token_IDENTIFIER, (int64_t)name); return false; }
    bool string(size_t pos, const std::string& text) { result = token(pos, token::Token_STRING, text); return false; }
    bool string(size_t pos, size_t /*end*/) { result = token(pos, token::Token_STRING); return false; }
    bool keyword(size_t pos, const std::string& text) { result = token(pos, token::Token_KEYWORD, text); return false; }
    bool enumeration(size_t pos, const std::string& text) { result = token(pos, token::Token_ENUMERATION, text); return false; }
    bool binary(size_t pos, const std::string& text) { result = token(pos, token::Token_BINARY, text); return false; }
    bool boolean(size_t pos, char c) { result = token(pos, token::Token_BOOL, c); return false; }
    bool integer(size_t pos, int64_t value) { result = token(pos, token::Token_INT, value); return false; }
    bool real(size_t pos, double value) { result = token(pos, value); return false; }
    bool literal(size_t pos) { result = token(pos, token::Token_LITERAL); return false; }
};

template <typename Reader>
template <typename Policy>
token spf_lexer<Reader>::next() {
    token_consumer<Policy> consumer;
    scan(consumer);
    return consumer.result;
}

} // namespace ifcopenshell

#endif
