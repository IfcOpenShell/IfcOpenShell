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

#include "parse.h"

#include "express.h"
#include "character_decoder.h"
#include "exception.h"
#include "file.h"
#include "logger.h"
#include "schema.h"
#include "si_prefix.h"
#include "file_reader.h"
#include "utils.h"

#include <algorithm>
#include <boost/algorithm/string.hpp>
#include <boost/variant.hpp>
#include <boost/math/special_functions/fpclassify.hpp>
#include <ctime>
#include <set>
#include <stdio.h>
#include <stdlib.h>
#include <cstring>
#include <string>
#include <iomanip>
#include <charconv>
#include <type_traits>

// Apple clang's libc++ has no floating-point std::from_chars overload (it's
// =deleted), so on macOS doubles are parsed via strtod_l with a cached "C"
// locale — locale-independent, unlike strtod. Other platforms (libstdc++,
// MSVC STL) have working float from_chars and are left unchanged.
#if defined(__APPLE__)
#include <xlocale.h>
#include <locale.h>
#endif

#ifdef USE_MMAP
#include <boost/filesystem/path.hpp>
#endif

#define PERMISSIVE_FLOAT

using namespace ifcopenshell;

template <typename Reader>
spf_lexer<Reader>::spf_lexer(Reader* stream_, ifcopenshell::logger& log)
    : decoder_(nullptr)
    , logger_(log) {
    stream = stream_;
    decoder_ = new character_decoder<Reader>(stream_, logger_);
}

template <typename Reader>
spf_lexer<Reader>::~spf_lexer() {
    delete decoder_;
}

template <typename Reader>
size_t spf_lexer<Reader>::skip_whitespace() const {
    size_t index = 0;
    while (!stream->eof()) {
        char character = stream->peek();
        if ((character == ' ' || character == '\r' || character == '\n' || character == '\t')) {
            stream->increment();
            ++index;
        } else {
            break;
        }
    }
    return index;
}

template <typename Reader>
size_t spf_lexer<Reader>::skip_comment() const {
    if (stream->eof()) {
        return 0;
    }
    char character = stream->peek();
    if (character != '/') {
        return 0;
    }
    stream->increment();
    character = stream->peek();
    if (character != '*') {
        stream->seek(stream->tell() - 1);
        return 0;
    }
    size_t index = 2;
    char intermediate = 0;
    while (!stream->eof()) {
        character = stream->peek();
        stream->increment();
        ++index;
        if (character == '/' && intermediate == '*') {
            break;
        }
        intermediate = character;
    }
    return index;
}

template <typename Reader>
std::string& spf_lexer<Reader>::get_temp_string() const {
    const size_t idx = pool_index++;
    const size_t slice = idx >> 4;
    const size_t offset = idx & 0xF;

    while (stringpool_.size() <= slice) {
        stringpool_.push_back(std::make_unique<std::array<std::string, 16>>());
    }

    // std::wcout << "Num contexts: " << idx << std::endl;

    return (*stringpool_[slice])[offset];
}

namespace {

#if defined(__APPLE__) || defined(__EMSCRIPTEN__)
double parse_double_c(const char* start, char** end) {
    static const locale_t loc = newlocale(LC_NUMERIC_MASK, "C", (locale_t)0);
    return strtod_l(start, end, loc);
}
#endif

template <typename T>
bool parse_num_(const char* pStart, size_t size, T& val) {
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

} // namespace

namespace SWAR {
constexpr uint32_t ONES32 = 0x01010101u;
constexpr uint32_t HIGHS32 = 0x80808080u;
constexpr uint64_t ONES = 0x0101010101010101ull;
constexpr uint64_t HIGHS = 0x8080808080808080ull;

constexpr uint64_t splat(unsigned char c) {
    return ONES * c;
}

inline uint32_t has_zero_byte(uint32_t x) {
    return (x - ONES32) & ~x & HIGHS32;
}

inline uint64_t has_zero_byte(uint64_t x) {
    return (x - ONES) & ~x & HIGHS;
}

inline uint32_t eq_mask(uint32_t x, uint32_t c) {
    return has_zero_byte(x ^ c);
}

inline uint64_t eq_mask(uint64_t x, uint64_t c) {
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
inline uint64_t has_special_char(uint64_t x) {
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
inline uint32_t has_special_char(uint32_t x) {
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

//
// Returns the offset of the current token and moves cursor to next
//
template <typename Reader>
token spf_lexer<Reader>::next() {

    if (stream->eof()) {
        return token{};
    }

    auto pos = stream->tell();
    char character = stream->read();

    if (character == '/' || character == ' ' || character == '\r' || character == '\n' || character == '\t') {
        while ((skip_whitespace() != 0U) || (skip_comment() != 0U)) {
        }
        if (stream->eof()) {
            return token{};
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
        return token(pos, character);
    }

    auto& str = get_temp_string();

    if (character == '\'') {
        // If a string is encountered defer processing to the character_decoder
        str = *decoder_;
        return token(pos, token::Token_STRING, str);
    } else {
        auto ttype = token::Token_NONE;
        if (character == '"' || character == '.') {
            if (character == '"') {
                ttype = token::Token_BINARY;
            } else {
                ttype = token::Token_ENUMERATION;
            }
            str.clear();
        } else if (character == '#') {
            ttype = token::Token_IDENTIFIER;
            str.clear();
        } else {
            str.assign(&character, 1);
        }

        auto remaining = stream->remaining();
        while (remaining) {
            if (remaining >= 8) {
                uint64_t x = stream->peek_u64();
                if ((ttype == token::Token_NONE ? SWAR::has_special_char<false>(x) : SWAR::has_special_char<true>(x)) == 0) {
                    str.append(reinterpret_cast<const char*>(&x), 8);
                    stream->increment(8);
                    remaining -= 8;
                    continue;
                }
            }
            if (remaining >= 4) {
                uint32_t x = stream->peek_u32();
                if ((ttype == token::Token_NONE ? SWAR::has_special_char<false>(x) : SWAR::has_special_char<true>(x)) == 0) {
                    str.append(reinterpret_cast<const char*>(&x), 4);
                    stream->increment(4);
                    remaining -= 4;
                    continue;
                }
            }

            // Read character and increment pointer if not starting a new token
            char character = stream->peek();
            if (character == '(' ||
                character == ')' ||
                character == '=' ||
                character == ',' ||
                character == ';' ||
                character == '/') {
                break;
            }
            if (!(character == ' ' || character == '\r' || character == '\n' || character == '\t')) {
                if ((ttype == token::Token_BINARY && character == '"') ||
                    (ttype == token::Token_ENUMERATION && character == '.')) {
                    // Skip
                } else {
                    str.push_back(character);
                }
            }
            stream->increment();
            remaining -= 1;
        }

        if (ttype == token::Token_ENUMERATION && str.size() == 1 && (str[0] == 'T' || str[0] == 'F' || str[0] == 'U')) {
            pop_pool_entry();
            return token(pos, token::Token_BOOL, str[0]);
        } else if (ttype == token::Token_IDENTIFIER) {
            int int_val;
            if (!parse_num_(str.c_str(), str.size(), int_val)) {
                throw invalid_token_exception(pos, str, "instance name");
            }
            pop_pool_entry();
            return token(pos, ttype, (int64_t)int_val);
        } else if (ttype == token::Token_NONE && !str.empty()) {
            int64_t int_val;
            double float_val;
            auto& first = str.front();
            if ((first >= 'A' && first <= 'Z') || (first >= 'a' && first <= 'z')) {
                ttype = token::Token_KEYWORD;
                return token(pos, ttype, str);
            } else if (parse_num_(str.c_str(), str.size(), int_val)) {
                ttype = token::Token_INT;
                pop_pool_entry();
                return token(pos, ttype, int_val);
            } else if (parse_num_(str.c_str(), str.size(), float_val)) {
                ttype = token::Token_FLOAT;
                pop_pool_entry();
                return token(pos, float_val);
            }
        } else if (ttype == token::Token_BINARY || ttype == token::Token_ENUMERATION) {
            return token(pos, ttype, str);
        }

        throw invalid_token_exception(pos, str, "valid token");
    }
}

template class IFC_PARSE_API ifcopenshell::spf_lexer<file_reader<full_buffer_impl>>;
template class IFC_PARSE_API ifcopenshell::spf_lexer<file_reader<paged_file_impl>>;
template class IFC_PARSE_API ifcopenshell::spf_lexer<file_reader<pushed_sequential_impl>>;
#ifdef USE_MMAP
template class IFC_PARSE_API ifcopenshell::spf_lexer<file_reader<mmap_impl>>;
#endif

bool token::is_operator() {
    return type == Token_OPERATOR;
}

bool token::is_operator(char character) {
    return type == Token_OPERATOR && value_char == character;
}

bool token::is_identifier() {
    return type == Token_IDENTIFIER;
}

bool token::is_string() {
    return type == Token_STRING;
}

bool token::is_enumeration() {
    // @nb this is a bit confusing?
    return type == Token_ENUMERATION || type == Token_BOOL;
}

bool token::is_binary() {
    return type == Token_BINARY;
}

bool token::is_keyword() {
    return type == Token_KEYWORD;
}

bool token::is_int() {
    return type == Token_INT;
}

bool token::is_bool() {
    // Bool and logical share the same storage type, just logical unknown is stored as 'U'.
    return type == Token_BOOL && value_char != 'U';
}

bool token::is_logical() {
    return type == Token_BOOL;
}

bool token::is_float() {
#ifdef PERMISSIVE_FLOAT
    /// NB: We are being more permissive here then allowed by the standard
    return type == Token_FLOAT || type == Token_INT;
#else
    return type == Token_FLOAT;
#endif
}

int64_t token::as_int() {
    if (type != Token_INT) {
        throw invalid_token_exception(start_pos, to_string(), "integer");
    }
    return value_int;
}

unsigned token::as_identifier() {
    if (type != Token_IDENTIFIER) {
        throw invalid_token_exception(start_pos, to_string(), "instance name");
    }
    return (unsigned) value_int;
}

bool token::as_bool() {
    if (type != Token_BOOL) {
        throw invalid_token_exception(start_pos, to_string(), "boolean");
    }
    return value_char == 'T';
}

boost::logic::tribool token::as_logical() {
    if (type != Token_BOOL) {
        throw invalid_token_exception(start_pos, to_string(), "logical");
    }
    if (value_int == 'F') {
        return false;
    }
    if (value_int == 'T') {
        return true;
    }
    return boost::logic::indeterminate;
}

double token::as_float() {
#ifdef PERMISSIVE_FLOAT
    if (type == Token_INT) {
        /// NB: We are being more permissive here then allowed by the standard
        return value_int;
    } // ----> continues beyond preprocessor directive
#endif
    if (type == Token_FLOAT) {
        return value_double;
    }
    throw invalid_token_exception(start_pos, to_string(), "real");
}

const std::string& token::as_string() {
    if (is_string() || is_enumeration() || is_binary() || is_keyword()) {
        // @todo quotes
        return *value_string;
    }
    throw invalid_token_exception(start_pos, to_string(), "string");
}

boost::dynamic_bitset<> token::as_binary() {
    const std::string& str = as_string();
    if (str.empty()) {
        throw exception("token is not a valid binary sequence");
    }

    std::string::const_iterator it = str.begin();
    int n = *it - '0';
    if ((n < 0 || n > 3) || (str.size() == 1 && n != 0)) {
        throw exception("token is not a valid binary sequence");
    }

    ++it;
    unsigned i = (str.size() - 1) * 4 - n;
    boost::dynamic_bitset<> bitset(i);

    for (; it != str.end(); ++it) {
        const std::string::value_type& c = *it;
        int value = (c < 'A') ? (c - '0') : (c - 'A' + 10);
        for (unsigned j = 0; j < 4; ++j) {
            if (i-- == 0) {
                break;
            }
            if ((value & (1 << (3 - j))) != 0) {
                bitset.set(i);
            }
        }
    }

    return bitset;
}

std::string token::to_string() {
    std::string result;
    if (type == Token_OPERATOR || type == Token_BOOL) {
		result.push_back(value_char);
    } else if (type == Token_INT) {
        result = std::to_string(value_int);
    } else if (type == Token_FLOAT) {
        std::ostringstream oss;
        oss << std::setprecision(15) << value_double;
        result = oss.str();
	} else {
        return as_string();
    }
    return result;
}

std::string ifcopenshell::encode_spf_string(const std::string& value) {
    return character_encoder(value);
}

std::string ifcopenshell::decode_spf_string(const std::string& value) {
    std::string wrapped;
    auto value_p = &value;
    if (!value.empty() && value.front() != '\'') {
        wrapped = "'" + value + "'";
        value_p = &wrapped;
    }
    file_reader<full_buffer_impl> reader(*value_p, caller_fed_tag{});
    spf_lexer<file_reader<full_buffer_impl>> lexer(&reader);
    token decoded = lexer.next();
    if (!decoded.is_string()) {
        throw exception("Expected an SPF string");
    }
    return decoded.as_string();
}

namespace {

template<typename Variant, typename T>
struct is_type_in_variant;

template<typename T, typename First, typename... Rest>
struct is_type_in_variant<std::variant<First, Rest...>, T>
{
    static constexpr bool value = std::is_same<T, First>::value || is_type_in_variant<std::variant<Rest...>, T>::value;
};

template<typename T, typename Last>
struct is_type_in_variant<std::variant<Last>, T>
{
    static constexpr bool value = std::is_same<T, Last>::value;
};

template<typename Variant, typename T>
constexpr bool is_type_in_variant_v = is_type_in_variant<Variant, T>::value;

class parameter_type_view {
    const ifcopenshell::declaration* declaration_;
    const std::vector<const ifcopenshell::attribute*>* attributes_;
    std::unique_ptr<ifcopenshell::named_type> transient_named_type_;

public:
    parameter_type_view(const ifcopenshell::declaration* declaration)
        : declaration_(declaration)
        , attributes_(nullptr)
    {
        if (declaration_ && declaration_->as_entity()) {
            attributes_ = &declaration_->as_entity()->all_attributes();
        } else if (declaration_ && declaration_->as_enumeration_type()) {
            transient_named_type_.reset(new ifcopenshell::named_type(const_cast<ifcopenshell::declaration*>(declaration_)));
        }
    }

    size_t size() const {
        if (attributes_) {
            return attributes_->size();
        }
        return declaration_ ? 1 : 0;
    }

    const ifcopenshell::parameter_type* operator[](size_t index) const {
        if (attributes_) {
            return index < attributes_->size() ? (*attributes_)[index]->type_of_attribute() : nullptr;
        }
        if (index != 0 || !declaration_) {
            return nullptr;
        }
        if (auto* type_declaration = declaration_->as_type_declaration()) {
            return type_declaration->declared_type();
        }
        if (declaration_->as_enumeration_type()) {
            return transient_named_type_.get();
        }
        return nullptr;
    }
};

const ifcopenshell::parameter_type* unwrap_type_declarations(const ifcopenshell::parameter_type* parameter_type) {
    while (parameter_type && parameter_type->as_named_type() &&
        parameter_type->as_named_type()->declared_type()->as_type_declaration()) {
        parameter_type = parameter_type->as_named_type()->declared_type()->as_type_declaration()->declared_type();
    }
    return parameter_type;
}

ifcopenshell::declaration* declared_type(const ifcopenshell::parameter_type* parameter_type) {
    parameter_type = unwrap_type_declarations(parameter_type);
    return parameter_type && parameter_type->as_named_type() ? parameter_type->as_named_type()->declared_type() : nullptr;
}

const ifcopenshell::aggregation_type* aggregate_parameter_type(const ifcopenshell::parameter_type* parameter_type) {
    parameter_type = unwrap_type_declarations(parameter_type);
    return parameter_type ? parameter_type->as_aggregation_type() : nullptr;
}

const ifcopenshell::aggregation_type* nested_aggregation_type(const ifcopenshell::aggregation_type* aggregate_type) {
    return aggregate_type ? aggregate_parameter_type(aggregate_type->type_of_element()) : nullptr;
}

void warn_attribute_count(
    const ifcopenshell::declaration* declaration,
    std::optional<size_t> instance_name,
    size_t expected_size,
    size_t actual_size,
    ifcopenshell::logger& logger
) {
    if (!declaration || expected_size == actual_size) {
        return;
    }
    if (declaration->schema() == &Header_section_schema::get_schema()) {
        logger.warning("VAL", 15, "Expected " + std::to_string(expected_size) + " attribute values, found " + std::to_string(actual_size) + " for header entity " + declaration->name());
    } else {
        logger.warning("VAL", 16, "Expected " + std::to_string(expected_size) + " attribute values, found " + std::to_string(actual_size) + (instance_name ? std::string(" for instance #" + std::to_string(*instance_name)) : std::string("")));
    }
}

template <typename Fn>
void dispatch_token_direct(ifcopenshell::token token, ifcopenshell::declaration* declaration, int attribute_index, logger& logger, Fn&& fn) {
    if (token.is_binary()) {
        fn(token.as_binary());
    } else if (token.is_bool()) {
        fn(token.as_bool());
    } else if (token.is_logical()) {
        fn(token.as_logical());
    } else if (token.is_enumeration()) {
        const auto& value = token.as_string();
        if (declaration && declaration->as_enumeration_type()) {
            try {
                fn(enumeration_reference(declaration->as_enumeration_type(), declaration->as_enumeration_type()->lookup_enum_offset(value)));
            } catch (ifcopenshell::exception&) {
                logger.error("VAL", 12, "An enumeration literal '" + value + "' is not valid for type '" + declaration->name() + "' at offset " + std::to_string(token.start_pos));
            }
        } else {
            logger.error("VAL", 13, "An enumeration literal '" + value + "' is not expected at attribute index '" + std::to_string(attribute_index) + "' at offset " + std::to_string(token.start_pos));
        }
    } else if (token.is_int()) {
        fn(token.as_int());
    } else if (token.is_float()) {
        fn(token.as_float());
    } else if (token.is_identifier()) {
        fn(ifcopenshell::reference_or_simple_type{ifcopenshell::instance_reference{(int) token.as_identifier(), token.start_pos}});
    } else if (token.is_string()) {
        fn(token.as_string());
    } else if (token.is_operator('*')) {
        fn(derived{});
    }
}

typedef std::variant<
    blank,

    std::vector<int64_t>,
    std::vector<double>,
    std::vector<std::string>,
    std::vector<boost::dynamic_bitset<>>,
    std::vector<ifcopenshell::reference_or_simple_type>,

    std::vector<std::vector<int64_t>>,
    std::vector<std::vector<double>>,
    std::vector<std::vector<ifcopenshell::reference_or_simple_type>>
> direct_aggregate_storage;

struct direct_aggregate {
    direct_aggregate_storage storage;
    size_t pending_empty_aggregates = 0;
    size_t values = 0;
    ifcopenshell::logger& logger_;

    explicit direct_aggregate(ifcopenshell::logger& logger)
        : logger_(logger) {}

    template <typename T>
    void append(const T& value) {
        ++values;
        if constexpr (is_type_in_variant_v<direct_aggregate_storage, std::vector<std::decay_t<T>>>) {
            if constexpr (
                std::is_same_v<std::decay_t<T>, std::vector<int64_t>> ||
                std::is_same_v<std::decay_t<T>, std::vector<double>> ||
                std::is_same_v<std::decay_t<T>, std::vector<ifcopenshell::reference_or_simple_type>>
            ) {
                if (storage.index() == 0 && pending_empty_aggregates) {
                    append_promoted(value);
                    return;
                }
            }
            if (pending_empty_aggregates) {
                logger_.error("VAL", 14, "Inconsistent aggregate valuation while attempting to append " + std::string(typeid(T).name()) + " after an empty nested aggregate");
                pending_empty_aggregates = 0;
            }
            if (storage.index() == 0) {
                storage = std::vector<std::decay_t<T>>{value};
            } else if (auto* vector = std::get_if<std::vector<std::decay_t<T>>>(&storage)) {
                vector->push_back(value);
            } else {
                append_promoted(value);
            }
        } else {
            logger_.error("UNS", 31, std::string("Aggregates of ") + typeid(T).name() + " are not supported in the IfcOpenShell parser");
        }
    }

    void append_empty_nested() {
        ++values;
        if (auto* int_vector = std::get_if<std::vector<std::vector<int64_t>>>(&storage)) {
            int_vector->emplace_back();
        } else if (auto* double_vector = std::get_if<std::vector<std::vector<double>>>(&storage)) {
            double_vector->emplace_back();
        } else if (auto* reference_vector = std::get_if<std::vector<std::vector<ifcopenshell::reference_or_simple_type>>>(&storage)) {
            reference_vector->emplace_back();
        } else if (storage.index() == 0) {
            ++pending_empty_aggregates;
        } else {
            logger_.error("Inconsistent aggregate valuation while attempting to append an empty nested aggregate");
        }
    }

private:
    template <typename T>
    void append_promoted(const T& value) {
        if constexpr (std::is_same_v<std::decay_t<T>, int64_t>) {
            if (auto* vector = std::get_if<std::vector<double>>(&storage)) {
                vector->push_back((double) value);
                return;
            }
        }
        if constexpr (std::is_same_v<std::decay_t<T>, double>) {
            if (auto* vector = std::get_if<std::vector<int64_t>>(&storage)) {
                std::vector<double> promoted(vector->begin(), vector->end());
                promoted.push_back(value);
                storage = std::move(promoted);
                return;
            }
        }
        if constexpr (std::is_same_v<std::decay_t<T>, std::vector<int64_t>>) {
            if (storage.index() == 0) {
                std::vector<std::vector<int64_t>> promoted(pending_empty_aggregates);
                pending_empty_aggregates = 0;
                promoted.push_back(value);
                storage = std::move(promoted);
                return;
            }
            if (auto* vector = std::get_if<std::vector<std::vector<int64_t>>>(&storage)) {
                vector->push_back(value);
                return;
            }
            if (auto* vector = std::get_if<std::vector<std::vector<double>>>(&storage)) {
                std::vector<double> promoted(value.begin(), value.end());
                vector->push_back(std::move(promoted));
                return;
            }
        }
        if constexpr (std::is_same_v<std::decay_t<T>, std::vector<double>>) {
            if (storage.index() == 0) {
                std::vector<std::vector<double>> promoted(pending_empty_aggregates);
                pending_empty_aggregates = 0;
                promoted.push_back(value);
                storage = std::move(promoted);
                return;
            }
            if (auto* vector = std::get_if<std::vector<std::vector<double>>>(&storage)) {
                vector->push_back(value);
                return;
            }
            if (auto* vector = std::get_if<std::vector<std::vector<int64_t>>>(&storage)) {
                std::vector<std::vector<double>> promoted;
                promoted.reserve(vector->size() + 1);
                for (const auto& nested : *vector) {
                    promoted.emplace_back(nested.begin(), nested.end());
                }
                promoted.push_back(value);
                storage = std::move(promoted);
                return;
            }
        }
        if constexpr (std::is_same_v<std::decay_t<T>, std::vector<ifcopenshell::reference_or_simple_type>>) {
            if (storage.index() == 0) {
                std::vector<std::vector<ifcopenshell::reference_or_simple_type>> promoted(pending_empty_aggregates);
                pending_empty_aggregates = 0;
                promoted.push_back(value);
                storage = std::move(promoted);
                return;
            }
            if (auto* vector = std::get_if<std::vector<std::vector<ifcopenshell::reference_or_simple_type>>>(&storage)) {
                vector->push_back(value);
                return;
            }
        }

        auto current = std::visit([](auto v) {
            if constexpr (!std::is_same_v<decltype(v), blank>) {
                return std::string(typeid(typename decltype(v)::value_type).name());
            } else {
                return std::string{};
            }
        }, storage);
        logger_.error("Inconsistent aggregate valuation while attempting to append " + std::string(typeid(T).name()) + " to an aggregate of " + current);
    }
};

void append_empty_direct_aggregate(const ifcopenshell::aggregation_type* aggregate_type, direct_aggregate& target) {
    if (!aggregate_type) {
        target.append_empty_nested();
        return;
    }

    auto argument_type = ifcopenshell::make_aggregate(ifcopenshell::from_parameter_type(aggregate_type->type_of_element()));
    if (argument_type == ifcopenshell::Argument_AGGREGATE_OF_INT) {
        target.storage = std::vector<int64_t>{};
    } else if (argument_type == ifcopenshell::Argument_AGGREGATE_OF_DOUBLE) {
        target.storage = std::vector<double>{};
    } else if (argument_type == ifcopenshell::Argument_AGGREGATE_OF_STRING) {
        target.storage = std::vector<std::string>{};
    } else if (argument_type == ifcopenshell::Argument_AGGREGATE_OF_BINARY) {
        target.storage = std::vector<boost::dynamic_bitset<>>{};
    } else if (argument_type == ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
        target.storage = std::vector<ifcopenshell::reference_or_simple_type>{};
    } else if (argument_type == ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_INT) {
        target.storage = std::vector<std::vector<int64_t>>{};
    } else if (argument_type == ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
        target.storage = std::vector<std::vector<double>>{};
    } else if (argument_type == ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
        target.storage = std::vector<std::vector<ifcopenshell::reference_or_simple_type>>{};
    } else {
        target.append_empty_nested();
    }
}

template <typename T>
void set_direct_attribute(
    in_memory_attribute_storage& storage,
    std::optional<size_t> instance_name,
    ifcopenshell::unresolved_references* references_to_resolve,
    size_t attribute_index,
    int resolve_reference_index,
    const T& value
) {
    if constexpr (std::is_same_v<std::decay_t<T>, ifcopenshell::reference_or_simple_type>) {
        if (instance_name && references_to_resolve) {
            references_to_resolve->push_back(std::make_pair(
                ifcopenshell::mutable_attribute_value{(uint32_t) *instance_name, resolve_reference_index == -1 ? (uint8_t) attribute_index : (uint8_t) resolve_reference_index},
                value
            ));
        }
    } else if constexpr (std::is_same_v<std::decay_t<T>, std::vector<ifcopenshell::reference_or_simple_type>>) {
        if (instance_name && references_to_resolve) {
            references_to_resolve->push_back({{(uint32_t) *instance_name, resolve_reference_index == -1 ? (uint8_t) attribute_index : (uint8_t) resolve_reference_index}, value});
        }
    } else if constexpr (std::is_same_v<std::decay_t<T>, std::vector<std::vector<ifcopenshell::reference_or_simple_type>>>) {
        if (instance_name && references_to_resolve) {
            references_to_resolve->push_back({{(uint32_t) *instance_name, resolve_reference_index == -1 ? (uint8_t) attribute_index : (uint8_t) resolve_reference_index}, value});
        }
    } else {
        storage.set(attribute_index, value);
    }
}

template <typename Reader>
void skip_aggregate(ifcopenshell::spf_lexer<Reader>* tokens) {
    size_t depth = 1;
    while (depth) {
        token next = tokens->next();
        if (!next) {
            break;
        }
        if (next.is_operator('(')) {
            ++depth;
        } else if (next.is_operator(')')) {
            --depth;
        }
    }
}

template <typename Reader>
direct_aggregate read_direct_aggregate(
    ifcopenshell::impl::in_memory_file_storage& storage,
    ifcopenshell::spf_lexer<Reader>* tokens,
    std::optional<size_t> entity_instance_name,
    const ifcopenshell::entity* entity,
    int attribute_index,
    const ifcopenshell::aggregation_type* aggregate_type,
    ifcopenshell::logger& logger
) {
    direct_aggregate aggregate(logger);
    token next = tokens->next();

    while (next) {
        if (next.is_operator(',')) {
        } else if (next.is_operator(')')) {
            break;
        } else if (next.is_operator('(')) {
            auto nested = read_direct_aggregate(storage, tokens, entity_instance_name, entity, attribute_index, nested_aggregation_type(aggregate_type), logger);
            if (nested.values == 0 && nested.storage.index() == 0) {
                aggregate.append_empty_nested();
            } else {
                std::visit([&aggregate](const auto& value) {
                    if constexpr (!std::is_same_v<std::decay_t<decltype(value)>, blank>) {
                        aggregate.append(value);
                    }
                }, nested.storage);
            }
        } else if (next.is_keyword()) {
            try {
                const auto* declaration = (storage.schema ? storage.schema : storage.file->schema())->declaration_by_name(next.as_string());
                tokens->next();
                auto data = storage.load(tokens, entity_instance_name, declaration, entity, attribute_index);
                storage.read_simple_type_instances.push_back(data);
                aggregate.append(ifcopenshell::reference_or_simple_type{express::base(data)});
            } catch (exception& e) {
                logger.error("SYN", 123, std::string(e.what()) + " at offset " + std::to_string(next.start_pos));
            }
        } else {
            if (next.is_identifier() && entity && entity_instance_name) {
                storage.register_inverse((unsigned)*entity_instance_name, entity, next.value_int, attribute_index);
            }
            dispatch_token_direct(next, aggregate_type && aggregate_type->type_of_element()->as_named_type() ? aggregate_type->type_of_element()->as_named_type()->declared_type() : nullptr, attribute_index, logger, [&aggregate](const auto& value) {
                aggregate.append(value);
            });
        }
        next = tokens->next();
    }

    if (aggregate.values == 0) {
        append_empty_direct_aggregate(aggregate_type, aggregate);
    }

    return aggregate;
}

} // namespace

//
// Reads the arguments from a list of tokens directly into instance_data storage.
// Additionally, registers the ids (i.e. #[\d]+) in the inverse map.
//
template <typename Reader>
shared_pointer_type ifcopenshell::impl::in_memory_file_storage::load(
    ifcopenshell::spf_lexer<Reader>* tokens,
    std::optional<size_t> entity_instance_name,
    const ifcopenshell::declaration* declaration,
    const ifcopenshell::entity* entity,
    int attribute_index,
    bool coerce_attribute_count
) {
    static_cast<void>(coerce_attribute_count);

    parameter_type_view parameter_types(declaration);
    const size_t expected_size = parameter_types.size();
    in_memory_attribute_storage storage(expected_size);

    token next = tokens->next();
    size_t attribute_index_within_data = 0;
    size_t values_read = 0;

    while (next) {
        if (next.is_operator(',')) {
            ++attribute_index_within_data;
        } else if (next.is_operator(')')) {
            break;
        } else {
            ++values_read;
            const bool retain_value = attribute_index_within_data < expected_size;
            const ifcopenshell::parameter_type* parameter_type = retain_value ? parameter_types[attribute_index_within_data] : nullptr;
            const int reference_attribute_index = attribute_index == -1 ? (int) attribute_index_within_data : attribute_index;

            if (next.is_operator('(')) {
                if (retain_value) {
                    auto aggregate = read_direct_aggregate(*this, tokens, entity_instance_name, entity, reference_attribute_index, aggregate_parameter_type(parameter_type), logger_.get());
                    std::visit([&](const auto& value) {
                        if constexpr (!std::is_same_v<std::decay_t<decltype(value)>, blank>) {
                            set_direct_attribute(storage, entity_instance_name, references_to_resolve, attribute_index_within_data, attribute_index, value);
                        }
                    }, aggregate.storage);
                } else {
                    skip_aggregate(tokens);
                }
            } else if (next.is_keyword()) {
                try {
                    const auto* simple_declaration = (schema ? schema : file->schema())->declaration_by_name(next.as_string());
                    tokens->next();
                    if (retain_value) {
                        auto data = load(tokens, entity_instance_name, simple_declaration, entity, reference_attribute_index);
                        read_simple_type_instances.push_back(data);
                        storage.set(attribute_index_within_data, express::base(data));
                    } else {
                        skip_aggregate(tokens);
                    }
                } catch (exception& e) {
                    logger_.get().message(ifcopenshell::logger::LOG_ERROR, std::string(e.what()) + " at offset " + std::to_string(next.start_pos));
                    --values_read;
                }
            } else {
                if (next.is_identifier() && entity && entity_instance_name) {
                    register_inverse((unsigned)*entity_instance_name, entity, next.value_int, reference_attribute_index);
                }
                if (retain_value) {
                    dispatch_token_direct(next, declared_type(parameter_type), (int) attribute_index_within_data, logger_.get(), [&](const auto& value) {
                        set_direct_attribute(storage, entity_instance_name, references_to_resolve, attribute_index_within_data, attribute_index, value);
                    });
                }
            }
        }
        next = tokens->next();
    }

    warn_attribute_count(declaration, entity_instance_name, expected_size, values_read, logger_.get());
    return ifcopenshell::make_pointer_type<instance_data>(file, declaration, (declaration && declaration->as_entity()) ? (uint32_t)entity_instance_name.value_or(0) : 0, std::move(storage));
}

template <typename Reader>
void ifcopenshell::impl::in_memory_file_storage::try_read_semicolon(ifcopenshell::spf_lexer<Reader>* tokens) const {
    auto old_offset = tokens->stream->tell();
    token semilocon = tokens->next();
    if (!semilocon.is_operator(';')) {
        tokens->stream->seek(old_offset);
    }
}

void ifcopenshell::impl::in_memory_file_storage::register_inverse(unsigned id_from, const ifcopenshell::entity* from_entity, int inst_id, int attribute_index) {
    // Assume a check on token type has already been performed
    byref_excl_.add((uint32_t)inst_id, (uint32_t)id_from, (uint16_t)from_entity->index_in_schema(), attribute_index);
}

void ifcopenshell::impl::in_memory_file_storage::unregister_inverse(unsigned id_from, const ifcopenshell::entity* from_entity, const express::base& inst, int attribute_index) {
    if (!byref_excl_.remove((uint32_t)inst.id(), (uint32_t)id_from, (uint16_t)from_entity->index_in_schema(), attribute_index)) {
        // @todo inverses also need to be populated when multiple instances are added to a new file.
        // throw ifcopenshell::exception("Instance not found among inverses");
    }
}

namespace {
    template <typename T>
    std::string to_string_fixed_width(const T& t, size_t) {
        // @todo currently inactive
        std::ostringstream oss;
        oss << /*std::setfill('0') << std::setw(w) <<*/ t;
        return oss.str();
    }
}

void ifcopenshell::impl::rocks_db_file_storage::register_inverse(unsigned id_from, const ifcopenshell::entity* from_entity, int inst_id, int attribute_index) {
#ifndef IFOPSH_WITH_ROCKSDB
    (void)id_from;
    (void)from_entity;
    (void)inst_id;
    (void)attribute_index;
#endif
#ifdef IFOPSH_WITH_ROCKSDB
    static std::string s;
    uint32_t v = id_from;
    s.resize(sizeof(uint32_t));
    memcpy(s.data(), &v, sizeof(uint32_t));

    auto key = "v|" + to_string_fixed_width(inst_id, 10) + "|" + to_string_fixed_width(from_entity->index_in_schema(), 4) + "|" + to_string_fixed_width(attribute_index, 2);

    db->Merge(wopts, key, s);
    /*
    // Python client does not support merges
    // @todo turn this into a setting
    {
        std::string current;
        db->Get(rocksdb::ReadOptions{}, key, &current);
        auto new_val = current + s;
        db->Put(wopts, key, new_val);
    }*/
#endif
}

void ifcopenshell::impl::rocks_db_file_storage::unregister_inverse(unsigned id_from, const ifcopenshell::entity* from_entity, const express::base& inst, int attribute_index) {
#ifndef IFOPSH_WITH_ROCKSDB
    (void)id_from;
    (void)from_entity;
    (void)inst;
    (void)attribute_index;
#endif
#ifdef IFOPSH_WITH_ROCKSDB
    static std::string s;
    auto inst_id = inst.id();
    auto key = "v|" + to_string_fixed_width(inst_id, 10) + "|" + to_string_fixed_width(from_entity->index_in_schema(), 4) + "|" + to_string_fixed_width(attribute_index, 2);
    if (db->Get(rocksdb::ReadOptions{}, key, &s).ok()) {
        std::vector<uint32_t> vals(s.size() / sizeof(uint32_t));
        memcpy(vals.data(), s.data(), s.size());
        auto it = std::find(vals.begin(), vals.end(), (uint32_t)id_from);
        if (it != vals.end()) {
            vals.erase(it);
        } else {
            file->logger().error("Unregistering non-existant inverse #" + std::to_string(id_from) + " on instance #" + std::to_string(inst_id) + " at attribute " + std::to_string(attribute_index));
        }
        s.resize(vals.size() * sizeof(uint32_t));
        memcpy(s.data(), vals.data(), s.size());
        db->Put(wopts, key, s);
    }
#endif
}

void ifcopenshell::impl::rocks_db_file_storage::add_type_ref(const express::base& new_entity)
{
#ifndef IFOPSH_WITH_ROCKSDB
    (void)new_entity;
#endif
#ifdef IFOPSH_WITH_ROCKSDB
    size_t v;
    std::string s(sizeof(size_t), ' ');

    if (new_entity.declaration().as_entity()) {
        v = new_entity.id();
        memcpy(s.data(), &v, sizeof(size_t));

        // no merges yet, because the python client doesn't support them
        db->Merge(wopts, "t|" + std::to_string(new_entity.declaration().index_in_schema()), s);

        /*{
            std::string current;
            // @todo this uses the same key-namespace as typedecl instances, not a direct conflict, but also not very clear
            auto key = "t|" + std::to_string(new_entity.declaration().index_in_schema());
            db->Get(rocksdb::ReadOptions{}, key, &current);
            auto new_val = current + s;
            db->Put(wopts, key, new_val);
        }*/
    }

    // not only mapping also register type
    v = new_entity.declaration().index_in_schema();
    memcpy(s.data(), &v, sizeof(size_t));
    db->Put(wopts, (new_entity.declaration().as_entity() ? "i|" : "t|") + std::to_string(new_entity.id() ? new_entity.id() : new_entity.identity()) + "|_", s);
#endif
}

void ifcopenshell::impl::rocks_db_file_storage::remove_type_ref(const express::base& new_entity)
{
#ifndef IFOPSH_WITH_ROCKSDB
    (void)new_entity;
#endif
#ifdef IFOPSH_WITH_ROCKSDB
    if (new_entity.declaration().as_entity()) {
        std::string s;
        auto key = "t|" + std::to_string(new_entity.declaration().index_in_schema());
        if (db->Get(rocksdb::ReadOptions{}, key, &s).ok()) {
            std::vector<size_t> vals(s.size() / sizeof(size_t));
            memcpy(vals.data(), s.data(), s.size());
            vals.erase(std::find(vals.begin(), vals.end(), (size_t)new_entity.id()));
            s.resize(vals.size() * sizeof(size_t));
            memcpy(s.data(), vals.data(), s.size());
            db->Put(wopts, key, s);
        }
    }

    db->Delete(wopts, (new_entity.declaration().as_entity() ? "i|" : "t|") + std::to_string(new_entity.id() ? new_entity.id() : new_entity.identity()) + "|_");
#endif
}

namespace {
    class string_builder_visitor : public boost::static_visitor<void> {
    private:
        string_builder_visitor(const string_builder_visitor&);            //N/A
        string_builder_visitor& operator=(const string_builder_visitor&); //N/A

        std::ostream& data_;
        template <typename T>
        void serialize(const std::vector<T>& i) {
            data_ << "(";
            for (typename std::vector<T>::const_iterator it = i.begin(); it != i.end(); ++it) {
                if (it != i.begin()) {
                    data_ << ",";
                }
                data_ << *it;
            }
            data_ << ")";
        }
        // Shortest decimal representation of 'd' that round-trips back to the
        // exact same double (like std::to_chars, or Python's repr).
        // Using actual `std::to_chars` requires macOS 13.3+, so we implement this manually,
        // until we drop support for older targets.
        //
        // Mirrors libstdc++'s notation-choice bounds (floating_to_chars.cc,
        // __floating_to_chars_shortest) to pick whichever of fixed/scientific is
        // shorter for a given digit count and exponent.
        static inline void format_double_shortest(char (&buf)[64], double d) {
            char sci[64];
            int mantissa_length = 17;
            for (int prec = 1; prec <= 17; ++prec) {
                snprintf(sci, sizeof(sci), "%.*e", prec - 1, d);
                if (strtod(sci, nullptr) == d) {
                    mantissa_length = prec;
                    break;
                }
            }
            const char* exp_str = strchr(sci, 'e');
            const int scientific_exponent = exp_str ? atoi(exp_str + 1) : 0;
            const int fd_exponent = scientific_exponent - (mantissa_length - 1);
            int lower_bound = -(mantissa_length + 3);
            int upper_bound = 5;
            if (mantissa_length == 1) {
                ++lower_bound;
                --upper_bound;
            }
            if (fd_exponent >= lower_bound && fd_exponent <= upper_bound) {
                const int fixed_precision = fd_exponent < 0 ? -fd_exponent : 0;
                snprintf(buf, 64, "%.*f", fixed_precision, d);
            } else {
                snprintf(buf, 64, "%.*e", mantissa_length - 1, d);
            }
        }
        // The REAL token definition from the IFC SPF standard does not necessarily match
        // the output of the C++ ostream formatting operation.
        // REAL = [ SIGN ] DIGIT { DIGIT } "." { DIGIT } [ "E" [ SIGN ] DIGIT { DIGIT } ] .
        static std::string format_double(const double& d) {
            // Use the shortest representation that round-trips exactly (like
            // Python's repr) instead of max_digits10. max_digits10 padded clean
            // values with noise digits (0.0174532925199433 -> 0.017453292519943299),
            // which rewrote every REAL and produced huge diffs when a file was
            // re-saved. See #7696.
            char buf[64];
            format_double_shortest(buf, d);
            const std::string str(buf);
            std::string::size_type e = str.find('e');
            if (e == std::string::npos) {
                e = str.find('E');
            }
            std::string result = str.substr(0, e);
            if (result.find('.') == std::string::npos) {
                result += '.';
            }
            if (e != std::string::npos) {
                result += 'E';
                result += str.substr(e + 1);
            }
            return result;
        }

        static std::string format_binary(const boost::dynamic_bitset<>& b) {
            std::ostringstream oss;
            oss.imbue(std::locale::classic());
            oss.put('"');
            oss << std::uppercase << std::hex << std::setw(1);
            unsigned c = (unsigned)b.size();
            unsigned n = (4 - (c % 4)) & 3;
            oss << n;
            for (unsigned i = 0; i < c + n;) {
                unsigned accum = 0;
                for (int j = 0; j < 4; ++j, ++i) {
                    unsigned bit = i < n ? 0 : b.test(c - i + n - 1) ? 1
                        : 0;
                    accum |= bit << (3 - j);
                }
                oss << accum;
            }
            oss.put('"');
            return oss.str();
        }

        bool upper_;

    public:
        string_builder_visitor(std::ostream& stream, bool upper = false)
            : data_(stream),
            upper_(upper) {}
        void operator()(const blank& /*i*/) { data_ << "$"; }
        void operator()(const derived& /*i*/) { data_ << "*"; }
        void operator()(const int64_t& i) { data_ << i; }
        void operator()(const bool& i) { data_ << (i ? ".T." : ".F."); }
        void operator()(const boost::logic::tribool& i) { data_ << (i ? ".T." : (boost::logic::indeterminate(i) ? ".U." : ".F.")); }
        void operator()(const double& i) { data_ << format_double(i); }
        void operator()(const boost::dynamic_bitset<>& i) { data_ << format_binary(i); }
        void operator()(const std::string& i) {
            std::string s = i;
            if (upper_) {
                data_ << static_cast<std::string>(character_encoder(s));
            } else {
                data_ << '\'' << s << '\'';
            }
        }
        void operator()(const std::vector<int64_t>& i);
        void operator()(const std::vector<double>& i);
        void operator()(const std::vector<std::string>& i);
        void operator()(const std::vector<boost::dynamic_bitset<>>& i);
        void operator()(const enumeration_reference& i) {
            data_ << "." << i.value() << ".";
        }
        void operator()(const express::base& i) {
            if (i.declaration().as_entity() == nullptr || i.declaration().schema() == &Header_section_schema::get_schema()) {
                i.to_string(data_, upper_);
            } else {
                data_ << "#" << i.id();
            }
        }
        void operator()(const std::vector<express::base>& i) {
            data_ << "(";
            for (auto it = i.begin(); it != i.end(); ++it) {
                if (it != i.begin()) {
                    data_ << ",";
                }
                (*this)(*it);
            }
            data_ << ")";
        }
        void operator()(const std::vector<std::vector<int64_t>>& i);
        void operator()(const std::vector<std::vector<double>>& i);
        void operator()(const std::vector<std::vector<express::base>>& i) {
            data_ << "(";
            for (auto outer_it = i.begin(); outer_it != i.end(); ++outer_it) {
                if (outer_it != i.begin()) {
                    data_ << ",";
                }
                data_ << "(";
                for (auto inner_it = outer_it->begin(); inner_it != outer_it->end(); ++inner_it) {
                    if (inner_it != outer_it->begin()) {
                        data_ << ",";
                    }
                    (*this)(*inner_it);
                }
                data_ << ")";
            }
            data_ << ")";
        }
        void operator()(const empty_aggregate& /*unused*/) const { data_ << "()"; }
        void operator()(const empty_aggregate_of_aggregate& /*unused*/) const { data_ << "()"; }
    };

    template <>
    void string_builder_visitor::serialize(const std::vector<std::string>& i) {
        data_ << "(";
        for (std::vector<std::string>::const_iterator it = i.begin(); it != i.end(); ++it) {
            if (it != i.begin()) {
                data_ << ",";
            }
            std::string encoder = character_encoder(*it);
            data_ << encoder;
        }
        data_ << ")";
    }

    template <>
    void string_builder_visitor::serialize(const std::vector<double>& i) {
        data_ << "(";
        for (std::vector<double>::const_iterator it = i.begin(); it != i.end(); ++it) {
            if (it != i.begin()) {
                data_ << ",";
            }
            data_ << format_double(*it);
        }
        data_ << ")";
    }

    template <>
    void string_builder_visitor::serialize(const std::vector<boost::dynamic_bitset<>>& i) {
        data_ << "(";
        for (std::vector<boost::dynamic_bitset<>>::const_iterator it = i.begin(); it != i.end(); ++it) {
            if (it != i.begin()) {
                data_ << ",";
            }
            data_ << format_binary(*it);
        }
        data_ << ")";
    }

    void string_builder_visitor::operator()(const std::vector<int64_t>& i) { serialize(i); }
    void string_builder_visitor::operator()(const std::vector<double>& i) { serialize(i); }
    void string_builder_visitor::operator()(const std::vector<std::string>& i) { serialize(i); }
    void string_builder_visitor::operator()(const std::vector<boost::dynamic_bitset<>>& i) { serialize(i); }
    void string_builder_visitor::operator()(const std::vector<std::vector<int64_t>>& i) {
        data_ << "(";
        for (std::vector<std::vector<int64_t>>::const_iterator it = i.begin(); it != i.end(); ++it) {
            if (it != i.begin()) {
                data_ << ",";
            }
            serialize(*it);
        }
        data_ << ")";
    }
    void string_builder_visitor::operator()(const std::vector<std::vector<double>>& i) {
        data_ << "(";
        for (std::vector<std::vector<double>>::const_iterator it = i.begin(); it != i.end(); ++it) {
            if (it != i.begin()) {
                data_ << ",";
            }
            serialize(*it);
        }
        data_ << ")";
    }
}

//
// Returns a string representation of the entity
// Note that this initializes the entity if it is not initialized
//
void instance_data::to_string(std::ostream& ss, bool upper) const {
    ss.imbue(std::locale::classic());

    ss << "(";

    string_builder_visitor vis(ss, upper);

    // In almost all cases, storage is initialized with the size of the schema declaration,
    // apparently except in case of header entities and invalid in-line type declarations.
    auto size = (declaration_ && declaration_->as_entity() ? declaration_->as_entity()->attribute_count() : 1);
    if (storage_) {
        size = (std::min)(size, storage_->size());
    }

    for (size_t i = 0; i < size; ++i) {
        if (i != 0) {
            ss << ",";
        }
        if (has_attribute_value<blank>(i)) {
            if (declaration_ != nullptr && declaration_->as_entity() && declaration_->as_entity()->derived()[i]) {
               ss << "*";
            } else {
               ss << "$";
	        }
        } else {
            get_attribute_value(i).apply_visitor(vis);
        }
    }
    ss << ")";
}

/*
unsigned ifcopenshell::IfcBaseEntity::set_id(const std::optional<unsigned>& i) {
    if (i) {
        return id_ = *i;
    }
    return id_ = file_->fresh_id();
}
*/

namespace {
// @todo remove redundancy with python wrapper code (which is not identical due to
// different handling of enumerations)
[[maybe_unused]] ifcopenshell::argument_type get_argument_type(const ifcopenshell::declaration* decl, size_t i) {
    const ifcopenshell::parameter_type* pt = 0;
    if (decl->as_entity() != nullptr) {
        pt = decl->as_entity()->attribute_by_index(i)->type_of_attribute();
        if (decl->as_entity()->derived()[i]) {
            return ifcopenshell::Argument_DERIVED;
        }
    } else if ((decl->as_type_declaration() != nullptr) && i == 0) {
        pt = decl->as_type_declaration()->declared_type();
    } else if ((decl->as_enumeration_type() != nullptr) && i == 0) {
        return ifcopenshell::Argument_ENUMERATION;
    }

    if (pt == 0) {
        return ifcopenshell::Argument_UNKNOWN;
    }
    return ifcopenshell::from_parameter_type(pt);
}
} // namespace

class unregister_inverse_visitor {
  private:
    file& file_;
    const express::base data_;

  public:
    unregister_inverse_visitor(file& file, const express::base& data)
        : file_(file),
          data_(data) {}

    void operator()(const express::base& inst, int index) {
        file_.unregister_inverse(data_.id(), data_.declaration().as_entity(), inst, index);
    }
};

class register_inverse_visitor {
  private:
    file& file_;
    const express::base data_;

  public:
    register_inverse_visitor(file& file, const express::base& data)
        : file_(file),
          data_(data) {}

    void operator()(const express::base& inst, int index) {
        file_.register_inverse(data_.id(), data_.declaration().as_entity(), inst.id(), index);
    }
};

class add_to_instance_list_visitor {
  private:
    std::vector<express::base>* list_;

  public:
    add_to_instance_list_visitor(std::vector<express::base>* list)
        : list_(list) {}

    void operator()(const express::base& inst) {
        list_->push_back(inst);
    }
};

class apply_individual_instance_visitor {
  private:
    std::optional<attribute_value> attribute_;
    int attribute_index_;

    const express::base inst_;


    template <typename T>
    void apply_attribute_(T& t, const attribute_value& attr, int index) const {
        switch (attr.type()) {
        case ifcopenshell::Argument_ENTITY_INSTANCE: {
            express::base inst = attr;
            t(inst, index);
            break;
        }
        case ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
            std::vector<express::base> entity_list_attribute = attr;
            for (auto& inst : entity_list_attribute) {
                t(inst, index);
            }
            break;
        }
        case ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
            std::vector<std::vector<express::base>> nested_list_attr = attr;
            for (auto& vec : nested_list_attr) {
                for (auto& inst : vec) {
                    t(inst, index);
                }
            }
            break;
        }
        default:
            break;
        }
    }
  public:
    apply_individual_instance_visitor(const attribute_value& attribute, int idx)
        : attribute_(attribute)
        , attribute_index_(idx)
    {}

    apply_individual_instance_visitor(const express::base& data)
        : inst_(data)
    {}

    template <typename T>
    void apply(T& t) const {
        if (attribute_) {
            apply_attribute_(t, *attribute_, attribute_index_);
        } else {
            const auto& decl = inst_.declaration();
            for (size_t i = 0; i < (decl.as_entity() ? decl.as_entity()->attribute_count() : 1); ++i) {
                auto attr = inst_.get_attribute_value(i);
                apply_attribute_(t, attr, (int) i);
            }
        }
    };
};

template <typename T>
typename std::enable_if<
    (!std::is_base_of_v<express::base, T> || std::is_same_v<express::base, T>),
    void>::type
express::base::set_attribute_value(size_t i, const T& t) {
    if constexpr (std::is_same_v<std::decay_t<T>, double>) {
        if (!std::isfinite(t)) {
            throw ifcopenshell::exception("Only finite values are allowed");
        }
    }
    if constexpr (std::is_same_v<std::decay_t<T>, std::vector<double>>) {
        if (std::any_of(t.begin(), t.end(), [](double d) { return !std::isfinite(d); })) {
            throw ifcopenshell::exception("Only finite values are allowed");
        }
    }
    if constexpr (std::is_same_v<std::decay_t<T>, std::vector<std::vector<double>>>) {
        for (auto& tt : t) {
            if (std::any_of(tt.begin(), tt.end(), [](double d) { return !std::isfinite(d); })) {
                throw ifcopenshell::exception("Only finite values are allowed");
            }
        }
    }
    auto current_attribute = get_attribute_value(i);

    // Deregister old attribute guid in file guid map.
    if (i == 0 && (file()->ifcroot_type() != nullptr) && this->declaration().is(*file()->ifcroot_type())) {
        try {
            auto guid = (std::string) current_attribute;
            auto it = file()->internal_guid_map().find(guid);
            if (it != file()->internal_guid_map().end()) {
                const std::pair<const std::string, express::base>& p = *it;
                if (p.second == *this) {
                    file()->internal_guid_map().erase(it);
                }
            }
        } catch (ifcopenshell::exception& e) {
            file()->logger().error(e);
        }
    }

    if constexpr (std::is_same_v<T, express::base> || std::is_same_v<T, std::vector<express::base>> || std::is_same_v<T, std::vector<std::vector<express::base>>> || std::is_same_v<T, blank>) {
        // Deregister inverse indices in file
        unregister_inverse_visitor visitor(*file(), *this);
        apply_individual_instance_visitor(current_attribute, (int)i).apply(visitor);
    }

    data()->set_attribute_value(i, t);
    auto new_attribute = get_attribute_value(i);

    // Register inverse indices in file
    if constexpr (std::is_same_v<T, express::base> || std::is_same_v<T, std::vector<express::base>> || std::is_same_v<T, std::vector<std::vector<express::base>>>) {
        register_inverse_visitor visitor(*file(), *this);
        apply_individual_instance_visitor(new_attribute, (int)i).apply(visitor);
    }

    // Register new attribute guid in guid map
    if (i == 0 && (file()->ifcroot_type() != nullptr) && this->declaration().is(*file()->ifcroot_type())) {
        try {
            auto guid = (std::string) new_attribute;
            auto it = file()->internal_guid_map().find(guid);
            if (it != file()->internal_guid_map().end()) {
                file()->logger().warning("Duplicate guid " + guid);
            }
            file()->internal_guid_map().insert({guid, *this});
        } catch (ifcopenshell::exception& e) {
            file()->logger().error(e);
        }
    }
}

template <typename T>
typename std::enable_if<
    (!std::is_base_of_v<express::base, T> || std::is_same_v<express::base, T>),
    void>::type
express::base::set_attribute_value(const std::string& s, const T& t)
{
    set_attribute_value(declaration().as_entity()->attribute_index(s), t);
}

//
// Parses the IFC file in fn
// Creates the maps
//
#ifdef USE_MMAP
file::file(const std::string& fn, bool mmap, ifcopenshell::logger& log)
    : logger_(log)
    , schema_(nullptr)
    , ifcroot_type_(nullptr)
    , max_id_(0) {
    initialize(fn, mmap);
}

bool ifcopenshell::file::initialize(const std::string& fn, bool mmap) {
    if (mmap) {
        file_reader<mmap_impl> s(fn);
        storage_.emplace<1>(this, logger_.get());
        header_.reset(new spf_header(this, &logger_.get()));
        std::get<impl::in_memory_file_storage>(storage_).read_from_stream(&s, schema_, max_id_, types_to_bypass_loading_);
    } else {
        file_reader<full_buffer_impl> s(fn);
        storage_.emplace<1>(this, logger_.get());
        header_.reset(new spf_header(this, &logger_.get()));
        std::get<impl::in_memory_file_storage>(storage_).read_from_stream(&s, schema_, max_id_, types_to_bypass_loading_);
    }

    if ((good_ = std::get<impl::in_memory_file_storage>(storage_).good_)) {
        // @todo unify these names, it's already confusing enough as it stands
        byid_ = decltype(byid_)(&std::get<impl::in_memory_file_storage>(storage_).byid_read_);
        byref_excl_ = decltype(byref_excl_)(&std::get<impl::in_memory_file_storage>(storage_).byref_excl_);
        byguid_ = decltype(byguid_)(&std::get<impl::in_memory_file_storage>(storage_).byguid_);
    }

    ifcroot_type_ = schema_ ? schema_->declaration_by_name("IfcRoot") : nullptr;
    return good_ == file_open_status::SUCCESS;
}
#endif

file::file(const uninitialized_tag&, ifcopenshell::logger& log)
    : good_(file_open_status::UNKNOWN), logger_(log), schema_(nullptr), ifcroot_type_(nullptr), max_id_(0), header_(nullptr) {}

bool ifcopenshell::file::initialize(const std::string& path, filetype ty, bool readonly) {
    if (ty == FT_AUTODETECT) {
        ty = guess_file_type(path);
    }
    if (ty == FT_IFCSPF) {
        file_reader<full_buffer_impl> s(path);
        storage_.emplace<1>(this, logger_.get());
        header_.reset(new spf_header(this, &logger_.get()));
        std::get<impl::in_memory_file_storage>(storage_).read_from_stream(&s, schema_, max_id_, types_to_bypass_loading_);

        if ((good_ = std::get<impl::in_memory_file_storage>(storage_).good_)) {
            // @todo unify these names, it's already confusing enough as it stands
            byid_ = decltype(byid_)(&std::get<impl::in_memory_file_storage>(storage_).byid_read_);
            byref_excl_ = decltype(byref_excl_)(&std::get<impl::in_memory_file_storage>(storage_).byref_excl_);
            byguid_ = decltype(byguid_)(&std::get<impl::in_memory_file_storage>(storage_).byguid_);
        }
        // byidentity_ = decltype(byidentity_)(&std::get<impl::in_memory_file_storage>(storage_).byidentity_);
    } else if (ty == FT_ROCKSDB) {
        // This would make some difference, but in the greater light of things, not really significant
        // LateBoundEntity is also still large per instance
        // instantiate_typed_instances = false;

        // @todo this can only be used for databases that already exist, because otherwise there is no way to specify the schema
        storage_.emplace<2>(path, this, readonly);
        if (std::get<impl::rocks_db_file_storage>(storage_).db == nullptr) {
            storage_.emplace<0>();
            good_ = file_open_status::READ_ERROR;
        } else {
            if (std::get<impl::rocks_db_file_storage>(storage_).read_schema(schema_)) {
                byid_ = decltype(byid_)(&std::get<impl::rocks_db_file_storage>(storage_).instance_by_name_);
                byref_excl_ = decltype(byref_excl_)(&std::get<impl::rocks_db_file_storage>(storage_).byref_excl_);
                byguid_ = decltype(byguid_)(&std::get<impl::rocks_db_file_storage>(storage_).byguid_);
                good_ = file_open_status::SUCCESS;
            } else {
                good_ = file_open_status::UNSUPPORTED_SCHEMA;
            }
        }
        // byidentity_ = decltype(byidentity_)(&std::get<impl::rocks_db_file_storage>(storage_).instance_cache_);
    } else {
        storage_.emplace<0>();
        good_ = file_open_status::READ_ERROR;
        // throw std::runtime_error("Unsupported file format");
    }
    ifcroot_type_ = schema_ ? schema_->declaration_by_name("IfcRoot") : nullptr;
    if (!header_) {
        header_.reset(new spf_header(this, &logger_.get()));
    }
    return good_ == file_open_status::SUCCESS;
}

void ifcopenshell::file::bypass_type(const std::string& type_name) {
    types_to_bypass_loading_.insert(type_name);
}

file::file(const std::string& path, filetype ty, bool readonly, ifcopenshell::logger& log)
    : logger_(log)
    , schema_(nullptr)
    , ifcroot_type_(nullptr)
    , max_id_(0)
{
    initialize(path, ty, readonly);
}

file::file(std::istream& stream, int length, ifcopenshell::logger& log)
    : logger_(log)
    , schema_(nullptr)
    , ifcroot_type_(nullptr)
    , max_id_(0)
{
    file_reader<pushed_sequential_impl> s(caller_fed_tag{});

    std::string string_data;
	string_data.resize(length);
	stream.read(string_data.data(), length);
    s.push_next_page(string_data);

    storage_.emplace<1>(this, logger_.get());
    header_.reset(new spf_header(this, &logger_.get()));
    std::get<impl::in_memory_file_storage>(storage_).read_from_stream(&s, schema_, max_id_, types_to_bypass_loading_);
    good_ = std::get<impl::in_memory_file_storage>(storage_).good_;
    ifcroot_type_ = schema_ ? schema_->declaration_by_name("IfcRoot") : nullptr;

    byid_ = decltype(byid_)(&std::get<impl::in_memory_file_storage>(storage_).byid_read_);
    byref_excl_ = decltype(byref_excl_)(&std::get<impl::in_memory_file_storage>(storage_).byref_excl_);
    byguid_ = decltype(byguid_)(&std::get<impl::in_memory_file_storage>(storage_).byguid_);

}

file::file(void* data, int length, ifcopenshell::logger& log)
    : logger_(log)
    , schema_(nullptr)
    , ifcroot_type_(nullptr)
    , max_id_(0)
{
	file_reader<pushed_sequential_impl> s(std::string((char*)data, length), caller_fed_tag{});

    storage_.emplace<1>(this, logger_.get());
    header_.reset(new spf_header(this, &logger_.get()));
    std::get<impl::in_memory_file_storage>(storage_).read_from_stream(&s, schema_, max_id_, types_to_bypass_loading_);
    good_ = std::get<impl::in_memory_file_storage>(storage_).good_;
    ifcroot_type_ = schema_ ? schema_->declaration_by_name("IfcRoot") : nullptr;

    byid_ = decltype(byid_)(&std::get<impl::in_memory_file_storage>(storage_).byid_read_);
    byref_excl_ = decltype(byref_excl_)(&std::get<impl::in_memory_file_storage>(storage_).byref_excl_);
    byguid_ = decltype(byguid_)(&std::get<impl::in_memory_file_storage>(storage_).byguid_);

}

file::file(const ifcopenshell::schema_definition* schema, filetype ty, const std::string& path, ifcopenshell::logger& log)
    : logger_(log)
    , schema_(schema)
    , ifcroot_type_(schema_->declaration_by_name("IfcRoot"))
    , max_id_(0)
{
    if (ty == FT_AUTODETECT) {
        ty = guess_file_type(path);
    }
    if (ty == FT_IFCSPF) {
        storage_.emplace<1>(this, logger_.get());

        byid_ = decltype(byid_)(&std::get<impl::in_memory_file_storage>(storage_).byid_read_);
        byref_excl_ = decltype(byref_excl_)(&std::get<impl::in_memory_file_storage>(storage_).byref_excl_);
        byguid_ = decltype(byguid_)(&std::get<impl::in_memory_file_storage>(storage_).byguid_);

        // byidentity_ = decltype(byidentity_)(&std::get<impl::in_memory_file_storage>(storage_).byidentity_);
    } else if (ty == FT_ROCKSDB) {
        storage_.emplace<2>(path, this);

        byid_ = decltype(byid_)(&std::get<impl::rocks_db_file_storage>(storage_).instance_by_name_);
        byref_excl_ = decltype(byref_excl_)(&std::get<impl::rocks_db_file_storage>(storage_).byref_excl_);
        byguid_ = decltype(byguid_)(&std::get<impl::rocks_db_file_storage>(storage_).byguid_);

        // byidentity_ = decltype(byidentity_)(&std::get<impl::rocks_db_file_storage>(storage_).instance_cache_);
    } else {
        throw std::runtime_error("Unsupported file format");
    }
    header_.reset(new spf_header(this, &logger_.get()));
    set_default_header_values();
}

namespace {

template <typename Reader>
void read_terminal(spf_lexer<Reader>& lexer, const std::string& term, bool trailing_semicolon) {
    if (lexer.next().as_string() != term) {
        throw exception(std::string("Expected " + term));
    }
    if (trailing_semicolon) {
        if (!lexer.next().is_operator(';')) {
            throw exception("Expected ;");
        }
    }
}

template <typename Reader>
shared_pointer_type read_header_entity(
    ifcopenshell::file* file,
    ifcopenshell::impl::in_memory_file_storage& storage,
    spf_lexer<Reader>& lexer,
    ifcopenshell::unresolved_references& references_to_resolve,
    const ifcopenshell::entity& decl) {
    lexer.next();
    storage.file = file;
    storage.references_to_resolve = &references_to_resolve;
    return storage.load(&lexer, std::nullopt, &decl, nullptr, -1);
}

template <typename Reader>
void parse_header(
    ifcopenshell::spf_header& header,
    ifcopenshell::impl::in_memory_file_storage& storage,
    spf_lexer<Reader>& lexer,
    ifcopenshell::unresolved_references& references_to_resolve) {
    static const char* const ISO_10303_21 = "ISO-10303-21";
    static const char* const HEADER = "HEADER";

    read_terminal(lexer, ISO_10303_21, true);
    read_terminal(lexer, HEADER, true);

    read_terminal(lexer, Header_section_schema::file_description::Class().name_uc(), false);
    header.set_file_description(read_header_entity(header.owner_file(), storage, lexer, references_to_resolve, Header_section_schema::file_description::Class()));
    if (!lexer.next().is_operator(';')) {
        throw exception("Expected ;");
    }

    read_terminal(lexer, Header_section_schema::file_name::Class().name_uc(), false);
    header.set_file_name(read_header_entity(header.owner_file(), storage, lexer, references_to_resolve, Header_section_schema::file_name::Class()));
    if (!lexer.next().is_operator(';')) {
        throw exception("Expected ;");
    }

    read_terminal(lexer, Header_section_schema::file_schema::Class().name_uc(), false);
    header.set_file_schema(read_header_entity(header.owner_file(), storage, lexer, references_to_resolve, Header_section_schema::file_schema::Class()));
    if (!lexer.next().is_operator(';')) {
        throw exception("Expected ;");
    }
}

template <typename Reader>
bool try_parse_header(
    ifcopenshell::spf_header& header,
    ifcopenshell::impl::in_memory_file_storage& storage,
    spf_lexer<Reader>& lexer,
    ifcopenshell::unresolved_references& references_to_resolve) {
    try {
        parse_header(header, storage, lexer, references_to_resolve);
        return true;
    } catch (const std::exception& e) {
        storage.logger_.get().error(e);
        return false;
    }
}

} // namespace

template <typename Reader>
const spf_header* ifcopenshell::instance_streamer<Reader>::header() const {
    return owner_ ? &owner_->header() : owned_header_.get();
}

template <typename Reader>
spf_header& ifcopenshell::instance_streamer<Reader>::ensure_header() {
    if (owner_ != nullptr) {
        return owner_->header();
    }

    if (!owned_header_) {
        owned_header_ = std::make_unique<spf_header>(owner_, &logger_.get());
    }

    return *owned_header_;
}

template <typename Reader>
void ifcopenshell::instance_streamer<Reader>::materialize_bypass_types() {
    if (!schema_) {
        return;
    }

    types_to_bypass_materialized_.assign(schema_->declarations().size(), false);
    for (auto& bp : types_to_bypass_) {
        std::function<void(const ifcopenshell::entity*)> mark;
        mark = [&](const ifcopenshell::entity* e) {
            types_to_bypass_materialized_[e->index_in_schema()] = true;
            for (auto& subtype : e->subtypes()) {
                mark(subtype);
            }
        };
        if (auto* e = bp->as_entity()) {
            mark(e);
        }
    }
}

template <typename Reader>
void ifcopenshell::instance_streamer<Reader>::initialize_header() {
    storage_.file = owner_;
    storage_.schema = schema_;
    storage_.references_to_resolve = &references_to_resolve_;

    if (!lexer_ || !stream_ || !stream_->size() || stream_->eof()) {
        return;
    }

    auto& header = ensure_header();
    if (try_parse_header(header, storage_, *lexer_, references_to_resolve_) && header.file_schema().schema_identifiers().size() == 1) {
        try {
            schema_ = ifcopenshell::schema_by_name(header.file_schema().schema_identifiers().front());
            good_ = file_open_status::SUCCESS;
        } catch (const ifcopenshell::exception&) {
        }
    }

    storage_.schema = schema_;

    materialize_bypass_types();
}

template <typename Reader>
bool ifcopenshell::instance_streamer<Reader>::has_semicolon() const {
    auto local_stream = stream_->clone();
    auto local_lexer = spf_lexer<Reader>(&local_stream, logger_.get());
    token t;
    try {
        t = local_lexer.next();
    } catch (const std::out_of_range&) {
        return false;
    }
    while (t.type != token::Token_NONE) {
        if (t.is_operator(';')) {
            return true;
        }
        try {
            t = local_lexer.next();
        } catch (const std::out_of_range&) {
            break;
        }
    }
    return false;
}

template <typename Reader>
size_t ifcopenshell::instance_streamer<Reader>::semicolon_count() const {
    auto local_stream = stream_->clone();
    auto local_lexer = spf_lexer<Reader>(&local_stream, logger_.get());
    token t;
    size_t count = 0;
    try {
        t = local_lexer.next();
    } catch (const std::out_of_range&) {
        return false;
    }
    while (t.type != token::Token_NONE) {
        if (t.is_operator(';')) {
            count++;
        }
        try {
            t = local_lexer.next();
        } catch (const std::out_of_range&) {
            break;
        }
    }
    return count;
}

template <typename Reader>
void ifcopenshell::instance_streamer<Reader>::push_page(const std::string& page) {
    stream_->push_next_page(page);
    if (good_ == file_open_status::NO_HEADER) {
        initialize_header();
    }
}

template <typename Reader>
ifcopenshell::instance_streamer<Reader>::instance_streamer(ifcopenshell::file* f, ifcopenshell::logger& log)
    : stream_(nullptr)
    , owner_(f)
    , token_stream_(3, token{})
    , schema_(nullptr)
    , storage_(nullptr, log)
    , logger_(log)
    , progress_(0)
{
    if constexpr (std::is_same_v<Reader, file_reader<full_buffer_impl>>) {
        owned_stream_ = std::make_unique<Reader>(caller_fed_tag{});
    } else if constexpr (std::is_same_v<Reader, file_reader<pushed_sequential_impl>>) {
        owned_stream_ = std::make_unique<Reader>(caller_fed_tag{});
    } else {
        static_assert(file_reader_dependent_false_v<Reader>, "Default instance_streamer requires a pushed sequential reader");
    }

    stream_ = owned_stream_.get();
    lexer_ = std::make_unique<spf_lexer<Reader>>(stream_, logger_.get());
    good_ = file_open_status::NO_HEADER;
    storage_.file = f;
    storage_.references_to_resolve = &references_to_resolve_;
}

template <typename Reader>
ifcopenshell::instance_streamer<Reader>::instance_streamer(const std::string& fn, bool mmap, ifcopenshell::file* f, ifcopenshell::logger& log)
    : stream_(nullptr)
    , owner_(f)
    , token_stream_(3, token{})
    , schema_(nullptr)
    , storage_(nullptr, log)
    , logger_(log)
    , progress_(0)
{
   if constexpr (std::is_same_v<Reader, file_reader<full_buffer_impl>>) {
        (void)mmap;
        owned_stream_ = std::make_unique<Reader>(fn);
#ifdef USE_MMAP
    } else if constexpr (std::is_same_v<Reader, file_reader<mmap_impl>>) {
        (void)mmap;
        owned_stream_ = std::make_unique<Reader>(fn);
#endif
    } else {
        static_assert(file_reader_dependent_false_v<Reader>, "Path-based instance_streamer requires a file-backed reader");
    }

    stream_ = owned_stream_.get();
    lexer_ = std::make_unique<spf_lexer<Reader>>(stream_, logger_.get());
    good_ = file_open_status::NO_HEADER;
    initialize_header();
}

template <typename Reader>
ifcopenshell::instance_streamer<Reader>::instance_streamer(void* data, int length, ifcopenshell::file* f, ifcopenshell::logger& log)
    : stream_(nullptr)
    , owner_(f)
    , token_stream_(3, token{})
    , schema_(nullptr)
    , storage_(nullptr, log)
    , logger_(log)
    , progress_(0)
{
    if constexpr (std::is_same_v<Reader, file_reader<full_buffer_impl>>) {
        owned_stream_ = std::make_unique<Reader>(std::string((char*)data, length), caller_fed_tag{});
    } else if constexpr (std::is_same_v<Reader, file_reader<pushed_sequential_impl>>) {
        owned_stream_ = std::make_unique<Reader>(std::string((char*)data, length), caller_fed_tag{});
    } else {
        static_assert(file_reader_dependent_false_v<Reader>, "Buffer-based instance_streamer requires a pushed sequential reader");
    }

    stream_ = owned_stream_.get();
    lexer_ = std::make_unique<spf_lexer<Reader>>(stream_, logger_.get());
    good_ = file_open_status::NO_HEADER;
    initialize_header();
}

template <typename Reader>
ifcopenshell::instance_streamer<Reader>::instance_streamer(Reader* stream, ifcopenshell::file* f, ifcopenshell::logger& log)
    : stream_(stream)
    , owner_(f)
    , token_stream_(3, token{})
    , schema_(nullptr)
    , storage_(nullptr, log)
    , logger_(log)
    , progress_(0)
{
    lexer_ = std::make_unique<spf_lexer<Reader>>(stream_, logger_.get());
    good_ = file_open_status::NO_HEADER;
    initialize_header();
}

template <typename Reader>
void ifcopenshell::instance_streamer<Reader>::bypass_types(const std::set<std::string>& type_names) {
    for (auto& name : type_names) {
        try {
            types_to_bypass_.push_back(schema_->declaration_by_name(name));
        } catch (const exception&) {
            continue;
        }
    }
    materialize_bypass_types();
}

template <typename Reader>
std::optional<std::tuple<size_t, const ifcopenshell::declaration*, shared_pointer_type>> ifcopenshell::instance_streamer<Reader>::read_instance() {
    std::optional<std::tuple<size_t, const ifcopenshell::declaration*, shared_pointer_type>> return_value;

    const auto* header = this->header();
    if (yield_header_instances_ && header && yielded_header_instances_ < 3) {
        if (yielded_header_instances_ == 0) {
            return_value.emplace(
                0,
                &header->file_description().declaration(),
#ifdef IFOPSH_SAFE_INSTANCE
                header->file_description().data_weak().lock());
#else
                header->file_description().data_weak());
#endif
        } else if (yielded_header_instances_ == 1) {
            return_value.emplace(
                0,
                &header->file_name().declaration(),
#ifdef IFOPSH_SAFE_INSTANCE
                header->file_name().data_weak().lock());
#else
                header->file_name().data_weak());
#endif
        } else if (yielded_header_instances_ == 2) {
            return_value.emplace(
                0,
                &header->file_schema().declaration(),
#ifdef IFOPSH_SAFE_INSTANCE
                header->file_schema().data_weak().lock());
#else
                header->file_schema().data_weak());
#endif
        }
        yielded_header_instances_ += 1;
        return return_value;
    }

    unsigned current_id = 0;
    while (good_ && !lexer_->stream->eof() && !current_id) {
        if (token_stream_[0].type == ifcopenshell::token::Token_IDENTIFIER &&
            token_stream_[1].type == ifcopenshell::token::Token_OPERATOR &&
            token_stream_[1].value_char == '=' &&
            token_stream_[2].type == ifcopenshell::token::Token_KEYWORD) {
            current_id = token_stream_[0].as_identifier();
            const ifcopenshell::declaration* entity_type;
            try {
                entity_type = schema_->declaration_by_name(token_stream_[2].as_string());
            } catch (const exception& ex) {
                logger_.get().message(ifcopenshell::logger::LOG_ERROR, std::string(ex.what()) + " at offset " + std::to_string(token_stream_[2].start_pos));
                current_id = 0;
                goto advance;
            }

            if (entity_type->as_entity() == nullptr) {
                logger_.get().message(ifcopenshell::logger::LOG_ERROR, "Non-entity type " + entity_type->name() + " at offset " + std::to_string(token_stream_[2].start_pos));
                current_id = 0;
                goto advance;
            }

            if (types_to_bypass_materialized_[entity_type->index_in_schema()]) {
                bypassed_instances_.push_back(current_id);
                current_id = 0;
                goto advance;
            }

            lexer_->next();
            try {
                auto data = storage_.load(lexer_.get(), current_id, entity_type, entity_type->as_entity(), -1, coerce_attribute_count);

                if (((++progress_) % 1000) == 0) {
                    std::stringstream ss;
                    ss << "\r#" << current_id;
                    logger_.get().status(ss.str(), false);
                }

                return_value.emplace(
                    (size_t)current_id,
                    entity_type,
                    data);
            } catch (const invalid_token_exception& e) {
                good_ = file_open_status::INVALID_SYNTAX;
                logger_.get().error(e);
                break;
            }
        }
    advance:
        token next_token;
        try {
            next_token = lexer_->next();
        } catch (const exception& e) {
            logger_.get().message(ifcopenshell::logger::LOG_ERROR, std::string(e.what()) + ". Parsing terminated");
        } catch (...) {
            logger_.get().message(ifcopenshell::logger::LOG_ERROR, "Parsing terminated");
        }

        if (!lexer_->stream->eof() && !next_token) {
            good_ = file_open_status::INVALID_SYNTAX;
            break;
        }

        token_stream_.push_back(next_token);
    }

    stream_->drop_pages();
    lexer_->reset_pool();

    return return_value;
}

template class IFC_PARSE_API ifcopenshell::instance_streamer<file_reader<full_buffer_impl>>;

template <typename Reader>
void ifcopenshell::impl::in_memory_file_storage::read_from_stream(Reader* s, const ifcopenshell::schema_definition*& schema, unsigned int& max_id, const std::set<std::string>& typed_to_bypass) {
    schema = nullptr;

    if (!s->size() || s->eof()) {
        good_ = file_open_status::READ_ERROR;
        return;
    }

    std::vector<std::string> schemas;

    instance_streamer<Reader> streamer(s, file, logger_.get());
    streamer.yield_header_instances(false);

    if (const auto* header = streamer.header()) {
        try {
            schemas = header->file_schema().schema_identifiers();
        } catch (...) {
        }
    }

    schema = streamer.schema();
    if (schema == nullptr && schemas.size() == 1) {
        try {
            schema = ifcopenshell::schema_by_name(schemas.front());
        } catch (const ifcopenshell::exception& e) {
            good_ = file_open_status::UNSUPPORTED_SCHEMA;
            logger_.get().error(e);
        }
    }

    if (schema == nullptr) {
        if (schemas.empty()) {
            good_ = streamer.status();
        } else {
            good_ = file_open_status::UNSUPPORTED_SCHEMA;
        }
        logger_.get().message(ifcopenshell::logger::LOG_ERROR, "No support for file schema encountered (" + boost::algorithm::join(schemas, ", ") + ")");
        return;
    }

    auto ifcroot_type_ = schema->declaration_by_name("IfcRoot");
    streamer.bypass_types(typed_to_bypass);

    logger_.get().status("Scanning file...");

    while (streamer) {
        auto inst = streamer.read_instance();

        if (!inst) {
            break;
        }

        auto current_id = std::get<0>(*inst);
        express::base instance(std::get<2>(*inst));

        if (instance.declaration().is(*ifcroot_type_)) {
            try {
                const std::string guid = instance.get_attribute_value(0);
                if (byguid_.find(guid) != byguid_.end()) {
                    std::stringstream ss;
                    ss << "Instance encountered with non-unique GlobalId " << guid;
                    logger_.get().message(ifcopenshell::logger::LOG_WARNING, ss.str());
                }
                byguid_[guid] = instance;
            } catch (const exception& ex) {
                logger_.get().message(ifcopenshell::logger::LOG_ERROR, ex.what());
            }
        }

        const ifcopenshell::declaration* ty = &instance.declaration();
        bytype_excl_[ty].push_back(instance);

        if (byid_.find(current_id) != byid_.end()) {
            std::stringstream ss;
            ss << "Overwriting instance with name #" << current_id;
            logger_.get().message(ifcopenshell::logger::LOG_WARNING, ss.str());
        }

        byid_.insert({(uint32_t)current_id, std::get<2>(*inst)});
        max_id = (std::max)(max_id, (unsigned int)current_id);
    }

    good_ = streamer.status();
    byref_excl_ = std::move(streamer.inverses());
    byref_excl_.sort();
    read_simple_type_instances = streamer.steal_instances();

    logger_.get().status("\rDone scanning file   ");

    if (good_ != file_open_status::SUCCESS) {
        return;
    }

    const auto& bypassed = streamer.bypassed_instances();

    for (const auto& p : streamer.references()) {
        const auto& ref = p.first.name_;
        const auto& refattr = p.first.index_;

        auto owner_it = byid_.find(ref);
        if (owner_it == byid_.end()) {
            logger_.get().error("Instance #" + std::to_string(ref) + " referenced at attribute index " + std::to_string(refattr) + " not found");
            continue;
        }
        auto& owner = owner_it->second;

        if (auto* v = std::get_if<reference_or_simple_type>(&p.second)) {
            if (auto* name = std::get_if<instance_reference>(v)) {
                if (std::binary_search(bypassed.begin(), bypassed.end(), *name)) {
                    continue;
                }
                auto it = byid_.find(*name);
                if (it == byid_.end()) {
                    logger_.get().error("Instance reference #" + std::to_string(*name) + " used by instance #" + std::to_string(ref) + " at attribute index " + std::to_string(refattr) + " not found at offset " + std::to_string(name->file_offset));
                } else {
                    auto storage = owner;
                    auto attr_index = p.first.index_;

                    if (storage->template has_attribute_value<express::base>(attr_index)) {
                        express::base inst = storage->get_attribute_value(attr_index);
                        if (inst && !inst.declaration().as_entity()) {
                            // Probably a case of IfcPropertySetDefinitionSet, divert storage of reference to the simply type instance
#ifdef IFOPSH_SAFE_INSTANCE
                            storage = inst.data_weak().lock();
#else
                            storage = inst.data_weak();
#endif
                            attr_index = 0;
                        }
                    }

                    if (storage->template has_attribute_value<blank>(attr_index)) {
                        storage->set_attribute_value(attr_index, express::base(it->second));
                    } else {
                        logger_.get().error("Duplicate definition for instance reference");
                    }
                }
            } else if (auto inst = std::get_if<express::base>(v)) {
                owner->set_attribute_value(p.first.index_, *inst);
            }
        } else if (auto* vv = std::get_if<std::vector<reference_or_simple_type>>(&p.second)) {
            std::vector<express::base> instances;
            instances.reserve(vv->size());
            for (const auto& vi : *vv) {
                if (auto* name = std::get_if<instance_reference>(&vi)) {
                    if (std::binary_search(bypassed.begin(), bypassed.end(), *name)) {
                        continue;
                    }
                    auto it = byid_.find(*name);
                    if (it == byid_.end()) {
                        logger_.get().error("Instance reference #" + std::to_string(*name) + " used by instance #" + std::to_string(ref) + " at attribute index " + std::to_string(refattr) + " not found at offset " + std::to_string(name->file_offset));
                    } else {
                        instances.push_back(express::base(it->second));
                    }
                } else if (auto* inst = std::get_if<express::base>(&vi)) {
                    instances.push_back(*inst);
                }
            }

            auto storage = owner;
            auto attr_index = p.first.index_;

            if (storage->template has_attribute_value<express::base>(attr_index)) {
                express::base inst = storage->get_attribute_value(attr_index);
                if (inst && !inst.declaration().as_entity()) {
                    // Probably a case of IfcPropertySetDefinitionSet, divert storage of reference to the simply type instance
#ifdef IFOPSH_SAFE_INSTANCE
                    storage = inst.data_weak().lock();
#else
                    storage = inst.data_weak();
#endif
                    attr_index = 0;
                }
            }

            if (storage->template has_attribute_value<blank>(attr_index)) {
                storage->set_attribute_value(attr_index, instances);
            } else {
                logger_.get().error("Duplicate definition for instance reference");
            }
        } else if (auto* vvv = std::get_if<std::vector<std::vector<reference_or_simple_type>>>(&p.second)) {
            std::vector<std::vector<express::base>> instances;
            for (const auto& vi : *vvv) {
                auto& inner = instances.emplace_back();
                for (const auto& vii : vi) {
                    if (auto* name = std::get_if<instance_reference>(&vii)) {
                        if (std::binary_search(bypassed.begin(), bypassed.end(), *name)) {
                            continue;
                        }
                        auto it = byid_.find(*name);
                        if (it == byid_.end()) {
                            logger_.get().error("Instance reference #" + std::to_string(*name) + " used by instance #" + std::to_string(ref) + " at attribute index " + std::to_string(refattr) + " not found at offset " + std::to_string(name->file_offset));
                        } else {
                            inner.push_back(express::base(it->second));
                        }
                    } else if (auto* inst = std::get_if<express::base>(&vii)) {
                        inner.push_back(*inst);
                    }
                }
            }

            auto storage = owner;
            auto attr_index = p.first.index_;

            if (storage->template has_attribute_value<express::base>(attr_index)) {
                express::base inst = storage->get_attribute_value(attr_index);
                if (inst && !inst.declaration().as_entity()) {
                    // Probably a case of IfcPropertySetDefinitionSet, divert storage of reference to the simply type instance
#ifdef IFOPSH_SAFE_INSTANCE
                    storage = inst.data_weak().lock();
#else
                    storage = inst.data_weak();
#endif
                    attr_index = 0;
                }
            }

            if (storage->template has_attribute_value<blank>(attr_index)) {
                storage->set_attribute_value(attr_index, instances);
            } else {
                logger_.get().error("Duplicate definition for instance reference");
            }
        }
    }

    logger_.get().status("Done resolving references");
}

template void ifcopenshell::impl::in_memory_file_storage::read_from_stream(file_reader<full_buffer_impl>* s, const ifcopenshell::schema_definition*& schema, unsigned int& max_id, const std::set<std::string>& typed_to_bypass);
template void ifcopenshell::impl::in_memory_file_storage::read_from_stream(file_reader<pushed_sequential_impl>* s, const ifcopenshell::schema_definition*& schema, unsigned int& max_id, const std::set<std::string>& typed_to_bypass);
#ifdef USE_MMAP
template void ifcopenshell::impl::in_memory_file_storage::read_from_stream(file_reader<mmap_impl>* s, const ifcopenshell::schema_definition*& schema, unsigned int& max_id, const std::set<std::string>& typed_to_bypass);
#endif

void file::recalculate_id_counter() {
    /*
    // @todo
    entity_by_id::key_type k = 0;
    for (auto& p : byid_) {
        if (p.first > k) {
            k = p.first;
        }
    }
    max_id_ = (unsigned int)k;
    */
}

class traversal_recorder {
    std::vector<express::base> list_;
    std::map<int, std::vector<express::base>> instances_by_level_;
    int mode_;

  public:
    traversal_recorder(int mode) : mode_(mode) {
    };

    void push_back(int level, const express::base& instance) {
        if (mode_ == 0) {
            list_.push_back(instance);
        } else {
            auto& l = instances_by_level_[level];
            l.push_back(instance);
        }
    }

    std::vector<express::base> get_list() const {
        if (mode_ == 0) {
            return list_;
        }
        std::vector<express::base> l;
        for (const auto& p : instances_by_level_) {
            l.insert(l.end(), p.second.begin(), p.second.end());
        }
        return l;
    }
};

class traversal_visitor {
  private:
    std::set<express::base>& visited_;
    traversal_recorder& list_;
    int level_;
    int max_level_;

  public:
    traversal_visitor(std::set<express::base>& visited, traversal_recorder& list, int level, int max_level)
        : visited_(visited),
          list_(list),
          level_(level),
          max_level_(max_level) {}

    void operator()(const express::base& inst, int index);
};

void traverse_(const express::base& instance, std::set<express::base>& visited, traversal_recorder& list, int level, int max_level) {
    if (visited.find(instance) != visited.end()) {
        return;
    }
    visited.insert(instance);
    list.push_back(level, instance);

    if (level >= max_level && max_level > 0) {
        return;
    }

    traversal_visitor visit(visited, list, level + 1, max_level);
    apply_individual_instance_visitor(instance).apply(visit);
}

void traversal_visitor::operator()(const express::base& inst, int /* index */) {
    traverse_(inst, visited_, list_, level_, max_level_);
}

std::vector<express::base> ifcopenshell::traverse(const express::base& instance, int max_level) {
    std::set<express::base> visited;
    traversal_recorder recorder(0);
    traverse_(instance, visited, recorder, 0, max_level);
    return recorder.get_list();
}

// I'm cheating this isn't breadth-first, but rather we record visited instances
// keeping track of their rank and return a list ordered by rank. Is this equivalent?
std::vector<express::base> ifcopenshell::traverse_breadth_first(const express::base& instance, int max_level) {
    std::set<express::base> visited;
    traversal_recorder recorder(1);
    traverse_(instance, visited, recorder, 0, max_level);
    return recorder.get_list();
}

/// @note: for backwards compatibility
std::vector<express::base> file::traverse(const express::base& instance, int max_level) {
    return ifcopenshell::traverse(instance, max_level);
}

/// @note: for backwards compatibility
std::vector<express::base> file::traverse_breadth_first(const express::base& instance, int max_level) {
    return ifcopenshell::traverse_breadth_first(instance, max_level);
}

express::base file::add_entity(const express::base& entity, int id) {
    if (entity.file() == this) {
        return entity;
    }

    if (entity.declaration().schema() != schema()) {
        throw ifcopenshell::exception("Unabled to add instance from " + entity.declaration().schema()->name() + " schema to file with " + schema()->name() + " schema");
    }

    // If this instance has been inserted before, return
    // a reference to the copy that was created from it.
    entity_entity_map::iterator mit = entity_file_map_.find(entity.identity());
    if (mit != entity_file_map_.end()) {
        return mit->second;
    }

    // Obtain all forward references by a depth-first
    // traversal and add them to the file.
    try {
        auto entity_attributes = traverse(entity, 1);
        for (auto it = entity_attributes.begin() + 1; it != entity_attributes.end(); ++it) {
            if (*it != entity) {
                entity_entity_map::iterator mit2 = entity_file_map_.find(it->identity());
                if (mit2 == entity_file_map_.end()) {
                    entity_file_map_.insert(entity_entity_map::value_type(it->identity(), add_entity(*it)));
                }
            }
        }
    } catch (...) {
        logger_.get().message(ifcopenshell::logger::LOG_ERROR, "Failed to visit forward references of", entity);
    }

    // An instance is being added from another file. A copy of the
    // container and entity is created. The attribute references
    // need to be updated to point to instances in this file.
    file* other_file = entity.file();
    auto new_entity = create(&entity.declaration(), id);
    auto* decl = &entity.declaration();

    auto num_attributes = (decl->as_entity() ? decl->as_entity()->attribute_count() : 1);
    for (size_t i = 0; i < num_attributes; ++i) {
        entity.get_attribute_value(i).apply_visitor([this, i, decl, &new_entity](const auto& v) {
            using u = std::decay_t<decltype(v)>;
            // only need to copy non-instance attribute values, others are assigned below after mapping
            if constexpr (std::is_same_v<u, express::base>) {
            } else if constexpr (std::is_same_v<u, std::vector<express::base>>) {
            } else if constexpr (std::is_same_v<u, std::vector<std::vector<express::base>>>) {
            } else if constexpr (std::is_same_v<u, empty_aggregate>) {
            } else if constexpr (std::is_same_v<u, empty_aggregate_of_aggregate>) {
            } else {
                new_entity.set_attribute_value(i, v);
            }
        });
    }

    // In case an entity is added that contains geometry, the unit
    // information needs to be accounted for for IfcLengthMeasures.
    double conversion_factor = calculate_unit_factors ? std::numeric_limits<double>::quiet_NaN() : 1.0;

    for (size_t i = 0; i < num_attributes; ++i) {
        // old attribute value
        auto attr = entity.get_attribute_value(i);
        ifcopenshell::argument_type attr_type = attr.type();

        ifcopenshell::declaration* potentially_length_measure_decl = 0;
        if (decl->as_entity() != nullptr) {
            potentially_length_measure_decl = 0;
            const parameter_type* pt = decl->as_entity()->attribute_by_index(i)->type_of_attribute();
            while (pt->as_aggregation_type() != nullptr) {
                pt = pt->as_aggregation_type()->type_of_element();
            }
            if (pt->as_named_type() != nullptr) {
                potentially_length_measure_decl = pt->as_named_type()->declared_type();
            }
        }

        if (attr_type == ifcopenshell::Argument_ENTITY_INSTANCE) {
            entity_entity_map::const_iterator eit = entity_file_map_.find(((express::base)(attr)).identity());
            if (eit == entity_file_map_.end()) {
                throw ifcopenshell::exception("Unable to map instance to file");
            }
            // @todo previously, we directly use storage::set() not to trigger inverse recalculation which happens at the end
            new_entity.set_attribute_value(i, eit->second);
        } else if (attr_type == ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
            std::vector<express::base> instances = attr;
            std::vector<express::base> new_instances;
            for (auto& i : instances) {
                entity_entity_map::const_iterator eit = entity_file_map_.find(i.identity());
                if (eit == entity_file_map_.end()) {
                    throw ifcopenshell::exception("Unable to map instance to file");
                }
                new_instances.push_back(eit->second);
            }
            new_entity.set_attribute_value(i, new_instances);
        } else if (attr_type == ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
            std::vector<std::vector<express::base>> instances = attr;
            std::vector<std::vector<express::base>> new_instances;

            for (auto& v : instances) {
                new_instances.emplace_back();
                for (auto& i : v) {
                    entity_entity_map::const_iterator eit = entity_file_map_.find(i.identity());
                    if (eit == entity_file_map_.end()) {
                        throw ifcopenshell::exception("Unable to map instance to file");
                    }
                    new_instances.back().push_back(eit->second);
                }
            }

            new_entity.set_attribute_value(i, new_instances);
        } else if ((potentially_length_measure_decl != nullptr) && potentially_length_measure_decl->is(*schema()->declaration_by_name("IfcLengthMeasure"))) {
            if (boost::math::isnan(conversion_factor)) {
                std::pair<express::base, double> this_file_unit = {express::base{}, 1.0};
                std::pair<express::base, double> other_file_unit = {express::base{}, 1.0};
                try {
                    this_file_unit = get_unit("LENGTHUNIT");
                    other_file_unit = other_file->get_unit("LENGTHUNIT");
                } catch (ifcopenshell::exception&) {
                }
                if (this_file_unit.first && other_file_unit.first) {
                    conversion_factor = other_file_unit.second / this_file_unit.second;
                } else {
                    conversion_factor = 1.;
                }
            }
            if (attr_type == ifcopenshell::Argument_DOUBLE) {
                double v = attr;
                v *= conversion_factor;
                new_entity.set_attribute_value(i, v);
            } else if (attr_type == ifcopenshell::Argument_AGGREGATE_OF_DOUBLE) {
                std::vector<double> v = attr;
                for (std::vector<double>::iterator it = v.begin(); it != v.end(); ++it) {
                    (*it) *= conversion_factor;
                }
                new_entity.set_attribute_value(i, v);
            } else if (attr_type == ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
                std::vector<std::vector<double>> v = attr;
                for (std::vector<std::vector<double>>::iterator it = v.begin(); it != v.end(); ++it) {
                    std::vector<double>& v2 = (*it);
                    for (std::vector<double>::iterator jt = v2.begin(); jt != v2.end(); ++jt) {
                        (*jt) *= conversion_factor;
                    }
                }
                new_entity.set_attribute_value(i, v);
            }
        }
    }

    entity_file_map_.insert(entity_entity_map::value_type(entity.identity(), new_entity));

    // For subtypes of IfcRoot, the GUID mapping needs to be updated.
    /*
    if (decl->is(*ifcroot_type_)) {
        try {
            const std::string guid = new_entity.get_attribute_value(0);
            if (byguid_.find(guid) != byguid_.end()) {
                std::stringstream ss;
                ss << "Overwriting entity with guid " << guid;
                logger_.get().message(ifcopenshell::logger::LOG_WARNING, ss.str());
            }
            byguid_.insert({ guid, new_entity });
        } catch (const std::exception& ex) {
            logger_.get().message(ifcopenshell::logger::LOG_ERROR, ex.what());
        }
    }
    */

    // add_type_ref(new_entity);

    return new_entity;
}

void file::remove_entity(const express::base& entity) {
    auto id = entity.id();

    auto file_entity = instance_by_id(id);

    // Attention when running remove_entity inside a loop over a list of entities to be removed.
    // This invalidates the iterator. A workaround is to reverse the loop:
    // std::shared_ptr<aggregate_of_instance> entities = ...;
    // for (auto it = entities->end() - 1; it >= entities->begin(); --it) {
    //    express::base *const inst = *it;
    //    model->remove_entity(inst);
    // }

    // TODO: Create a set of weak relations. Inverse relations that do not dictate an
    // instance to be retained. For example: when deleting an IfcRepresentation, the
    // individual IfcRepresentationItems can not be deleted if an IfcStyledItem is
    // related. Hence, the IfcRepresentationItem::StyledByItem relation could be
    // characterized as weak.
    // std::set<IfcSchema::Type::Enum> weak_roots;

    if (entity != file_entity) {
        throw ifcopenshell::exception("Instance not part of this file");
    }

    if (batch_mode_) {
        batch_deletion_ids_.push_back(id);
    } else {
        process_deletion_(entity);
        byid_.erase(entity.id());
    }
}

void file::process_deletion_(const express::base& entity) {

    auto references = instances_by_reference(entity.id());

    // Alter entity instances with INVERSE relations to the entity being
    // deleted. This is necessary to maintain a valid IFC file, because
    // dangling references to it's entities name should be removed. At this
    // moment, inversely related instances affected by the removal of the
    // entity being deleted are not deleted themselves.
    if (!references.empty()) {
        for (auto& related_instance : references) {
            if (std::find(batch_deletion_ids_.begin(), batch_deletion_ids_.end(), related_instance.id()) != batch_deletion_ids_.end()) {
                continue;
            }

            const auto& decl = related_instance.declaration();
            for (size_t i = 0; i < (decl.as_entity() ? decl.as_entity()->attribute_count() : 1); ++i) {
                auto attr = related_instance.get_attribute_value(i);
                if (attr.isNull()) {
                    continue;
                }

                ifcopenshell::argument_type attr_type = attr.type();
                switch (attr_type) {
                case ifcopenshell::Argument_ENTITY_INSTANCE: {
                    express::base instance_attribute = attr;
                    if (instance_attribute == entity) {
                        related_instance.set_attribute_value(i, blank{});
                    }
                } break;
                case ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
                    std::vector<express::base> instance_list = attr;
                    auto it = std::remove(instance_list.begin(), instance_list.end(), entity);
                    if (it != instance_list.end()) {
                        instance_list.erase(it, instance_list.end());
                        if (instance_list.empty() && related_instance.declaration().as_entity()->attribute_by_index(i)->optional()) {
                            // @todo we can also check the lower bound of the attribute type before setting to null.
                            related_instance.set_attribute_value(i, blank{});
                        } else {
                            related_instance.set_attribute_value(i, instance_list);
                        }
                    }
                } break;
                case ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
                    std::vector<std::vector<express::base>> instance_list_list = attr;
                    for (auto& li : instance_list_list) {
                        auto it = std::remove(li.begin(), li.end(), entity);
                        if (it != li.end()) {
                            li.erase(it, li.end());
                        }
                    }
                    related_instance.set_attribute_value(i, instance_list_list);
                } break;
                default:
                    break;
                }
            }
        }
    }

    if (entity.declaration().is(*ifcroot_type_) && !entity.get_attribute_value(0).isNull()) {
        const std::string global_id = entity.get_attribute_value(0);
        auto it = byguid_.find(global_id);
        if (it != byguid_.end()) {
            byguid_.erase(it);
        } else {
            logger_.get().warning("GlobalId on rooted instance not encountered in map");
        }
    }

    process_deletion_inverse(entity);

    remove_type_ref(entity);

    // entity_file_map is in place to prevent duplicate definitions with usage of add().
    // Upon deletion the pairs need to be erased.
    // @todo this is not strictly necessary anymore and can be amortized to e.g 1/100 times
    // to delete the expired weak_ptrs.
    for (auto it = entity_file_map_.begin(); it != entity_file_map_.end();) {
        if (it->second == entity) {
            it = entity_file_map_.erase(it);
        } else {
            ++it;
        }
    }
}

void ifcopenshell::impl::in_memory_file_storage::process_deletion_inverse(const express::base& entity) {
    auto id = entity.id();

    // Delete inverses into entity
    byref_excl_.erase(id);
    byref_excl_.remove_source(id);
}

namespace {
    template <typename Fn>
    void visit_subtypes(const ifcopenshell::entity* ent, Fn fn) {
        fn(ent);
        for (const auto& st : ent->subtypes()) {
            visit_subtypes(st, fn);
        }
    }

    template <typename Fn>
    void visit_supertypes(const ifcopenshell::entity* ent, Fn fn) {
        fn(ent);
        if (ent->supertype()) {
            visit_supertypes(ent->supertype(), fn);
        }
    }
}

std::vector<express::base> file::instances_by_type(const ifcopenshell::declaration* t) {
    std::vector<express::base> insts;
    if (t->as_entity() != nullptr) {
        visit_subtypes(t->as_entity(), [this, &insts](const ifcopenshell::entity* ent) {
            auto subtype_insts = instances_by_type_excl_subtypes(ent);
            insts.insert(insts.end(), subtype_insts.begin(), subtype_insts.end());
        });
    }
    return insts;
}

std::vector<express::base> file::instances_by_type_excl_subtypes(const ifcopenshell::declaration* t) {
    return std::visit([t](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            auto it = x.bytype_excl_.find(t);
            return (it == x.bytype_excl_.end()) ? std::vector<express::base>{} : it->second;
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            std::vector<express::base> ret;
            auto it = x.bytype_.find(t->index_in_schema());
            if (it != x.bytype_.end()) {
                const auto& s = it->second;
                // @todo generalize this, bytype_ should be a map_adapter
                std::vector<size_t> vals(s.size() / sizeof(size_t));
                memcpy(vals.data(), s.data(), s.size());
                for (auto& v : vals) {
                    ret.push_back(x.assert_existance(v, ifcopenshell::impl::rocks_db_file_storage::entityinstance_ref));
                }
            }
            return ret;
        } else {
            throw std::runtime_error("Storage not initialized");
            std::vector<express::base> ret;
            return ret;
        }
    }, storage_);
}

std::vector<express::base> file::instances_by_type(const std::string& t) {
    return instances_by_type(schema()->declaration_by_name(t));
}

std::vector<express::base> file::instances_by_type_excl_subtypes(const std::string& t) {
    return instances_by_type_excl_subtypes(schema()->declaration_by_name(t));
}

std::vector<express::base> file::instances_by_reference(int t) {
    std::vector<express::base> ret;
    std::visit([this, t, &ret](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            auto range = x.byref_excl_.equal_range((uint32_t)t);
            ret.reserve(ret.size() + (size_t)std::distance(range.first, range.second));
            for (auto it = range.first; it != range.second; ++it) {
                ret.push_back(instance_by_id(it->source_id));
            }
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            // @todo no lower/upper_bounds() implemented yet
            auto prefix = "v|" + std::to_string(t) + "|";
            auto it = std::unique_ptr<rocksdb::Iterator>(x.db->NewIterator(rocksdb::ReadOptions()));
            it->Seek(prefix);
            while (it->Valid() && it->key().starts_with(prefix)) {
                std::vector<uint32_t> vals(it->value().size() / sizeof(uint32_t));
                memcpy(vals.data(), it->value().data(), it->value().size());
                for (auto& v : vals) {
                    ret.push_back(instance_by_id(v));
                }
                it->Next();
            }
        }
#endif
        else {
            throw std::runtime_error("Storage not initialized");
        }
    }, storage_);
    return ret;
}

express::base file::instance_by_id(int id) {
    return std::visit([id](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
            return express::base{};
        } else {
            return x.instance_by_id(id);
        }
    }, storage_);
}

void ifcopenshell::file::add_type_ref(const express::base& new_entity)
{
    std::visit([new_entity](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.add_type_ref(new_entity);
        }
    }, storage_);
}


void ifcopenshell::file::remove_type_ref(const express::base& new_entity) {
    std::visit([new_entity](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.remove_type_ref(new_entity);
        }
    }, storage_);
}

void ifcopenshell::file::process_deletion_inverse(const express::base& inst) {
    std::visit([inst](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.process_deletion_inverse(inst);
        }
    }, storage_);
}

express::base file::instance_by_guid(const std::string& guid) {
    auto it = byguid_.find(guid);
    if (it == byguid_.end()) {
        throw exception("Instance with GlobalId '" + guid + "' not found");
    }
    return it->second;
}

file::type_iterator file::types_begin() const {
    return std::visit([](const auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            return file::type_iterator{ impl::rocks_db_file_storage::rocksdb_types_iterator{} };
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            return file::type_iterator{ x.bytype_excl_.begin() };
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            return file::type_iterator{ impl::rocks_db_file_storage::rocksdb_types_iterator(&x) };
        }
    }, storage_);
}

file::type_iterator file::types_end() const {
    return std::visit([](const auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            return file::type_iterator{ impl::rocks_db_file_storage::rocksdb_types_iterator{} };
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            return file::type_iterator{ x.bytype_excl_.end() };
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            return file::type_iterator{ impl::rocks_db_file_storage::rocksdb_types_iterator{} };
        }
    }, storage_);
}

std::ostream& operator<<(std::ostream& out, const ifcopenshell::file& file) {
    file.header().write(out);

    typedef std::vector<express::base> vector_t;
    vector_t sorted;
    std::transform(file.begin(), file.end(), std::back_inserter(sorted), [&file](const auto& x) { return x.second; });
    std::sort(sorted.begin(), sorted.end(), [](const auto& a, const auto& b) { return a.id() < b.id(); });

    for (auto& e : sorted) {
        // @todo this check should no longer be necessary?
        if (e.declaration().as_entity() != nullptr) {
            e.to_string(out, true);
            out << ";" << std::endl;
        }
    }

    out << "ENDSEC;" << std::endl;
    out << "END-ISO-10303-21;" << std::endl;

    return out;
}

std::string file::create_timestamp() {
    char buf[255];

    time_t t;
    time(&t);

    struct tm* ti = localtime(&t);

    std::string result;
    if (strftime(buf, 255, "%Y-%m-%dT%H:%M:%S", ti) != 0U) {
        result = std::string(buf);
    }

    return result;
}

const ifcopenshell::schema_definition* file::schema() const {
    if (schema_ == nullptr) {
        throw exception("No schema loaded");
	}
    return schema_;
}

std::vector<int> file::get_inverse_indices_by_id(int instance_id) {
    std::vector<int> return_value;

    // Mapping of instance id to attribute offset.
    std::map<int, std::vector<int>> mapping;
    bool handled = false;

    std::visit([&mapping, &return_value, &handled, instance_id](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            handled = true;
            auto range = x.byref_excl_.equal_range((uint32_t)instance_id);
            return_value.reserve((size_t)std::distance(range.first, range.second));
            for (auto it = range.first; it != range.second; ++it) {
                return_value.push_back(it->attribute_index);
            }
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
#ifdef IFOPSH_WITH_ROCKSDB
            // @todo no lower/upper_bounds() implemented yet
            auto prefix = "v|" + std::to_string(instance_id) + "|";
            auto it = std::unique_ptr<rocksdb::Iterator>(x.db->NewIterator(rocksdb::ReadOptions()));
            it->Seek(prefix);
            while (it->Valid() && it->key().starts_with(prefix)) {
                std::vector<uint32_t> vals(it->value().size() / sizeof(uint32_t));
                memcpy(vals.data(), it->value().data(), it->value().size());
                auto tuple = key_from_string<std::tuple<int, int, int>>(it->key().ToString().substr(2));
                for (auto& i : vals) {
                    mapping[i].push_back(std::get<2>(tuple));
                }
                it->Next();
            }
#endif
        }
    }, storage_);

    if (handled) {
        return return_value;
    }

    auto refs = instances_by_reference(instance_id);

    for (const auto& ref : refs) {
        auto it = mapping.find(ref.id());
        if (it == mapping.end() || it->second.empty()) {
            throw exception("Internal error");
        }
        return_value.push_back(it->second.front());
        it->second.erase(it->second.begin());
        if (it->second.empty()) {
            mapping.erase(it);
        }
    }

    // Test whether all mappings where indeed used.
    if (!mapping.empty()) {
        throw exception("Internal error");
    }

    return return_value;
}

std::vector<express::entity> file::get_inverse(int instance_id, const ifcopenshell::declaration* type, int attribute_index) {
    std::vector<express::entity> return_value;

    if (type == nullptr && attribute_index == -1) {
        // @todo this is silly.
        auto r = instances_by_reference(instance_id);
        for (auto& i : r) {
            return_value.push_back(i.as<express::entity>());
        }
        return return_value;
    }

    std::visit([&return_value, this, attribute_index, instance_id, type](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            std::vector<uint8_t> source_types(schema()->declarations().size(), 0);
            visit_subtypes(type->as_entity(), [&source_types](const ifcopenshell::declaration* ent) {
                source_types[ent->index_in_schema()] = 1;
            });
            auto range = x.byref_excl_.equal_range((uint32_t)instance_id);
            for (auto it = range.first; it != range.second; ++it) {
                if (it->source_entity < source_types.size() && source_types[it->source_entity] &&
                    (attribute_index == -1 || it->attribute_index == attribute_index)) {
                    return_value.push_back(instance_by_id(it->source_id).template as<express::entity>());
                }
            }
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            visit_subtypes(type->as_entity(), [this, attribute_index, instance_id, &return_value, &x](const ifcopenshell::declaration* ent) {
                if (attribute_index == -1) {
                    // @todo no lower/upper_bounds() implemented yet
                    auto prefix = "v|" + std::to_string(instance_id) + "|" + std::to_string(ent->index_in_schema()) + "|";
                    auto it = std::unique_ptr<rocksdb::Iterator>(x.db->NewIterator(rocksdb::ReadOptions()));
                    it->Seek(prefix);
                    while (it->Valid() && it->key().starts_with(prefix)) {
                        std::vector<uint32_t> vals(it->value().size() / sizeof(uint32_t));
                        memcpy(vals.data(), it->value().data(), it->value().size());
                        for (auto& v : vals) {
                            return_value.push_back(instance_by_id(v).template as<express::entity>());
                        }
                        it->Next();
                    }
                } else {
                    auto it = x.byref_excl_.find({instance_id, ent->index_in_schema(), attribute_index});
                    if (it != x.byref_excl_.end()) {
                        for (auto& i : it->second) {
                            return_value.push_back(instance_by_id(i).template as<express::entity>());
                        }
                    }
                }
            });
        }
#endif
    }, storage_);

    return return_value;
}

size_t file::get_total_inverses(int instance_id) {
    std::set<uint32_t> counted_ids;

    std::visit([&counted_ids, instance_id](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            auto range = x.byref_excl_.equal_range((uint32_t)instance_id);
            for (auto it = range.first; it != range.second; ++it) {
                counted_ids.insert(it->source_id);
            }
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            // @todo
        }
    }, storage_);

    return counted_ids.size();
}

void file::set_default_header_values() {
    const std::string empty_string;
    std::vector<std::string> file_description;
    std::vector<std::string> schema_identifiers;
    std::vector<std::string> string_vector = {""};

    file_description.push_back("ViewDefinition [CoordinationView]");
    if (schema() != nullptr) {
        schema_identifiers.push_back(schema()->name());
    }

    header().file_description().setdescription(file_description);
    header().file_description().setimplementation_level("2;1");

    header().file_name().setname(empty_string);
    header().file_name().settime_stamp(create_timestamp());
    header().file_name().setauthor(string_vector);
    header().file_name().setorganization(string_vector);
    header().file_name().setpreprocessor_version("IfcOpenShell " + std::string(IFCOPENSHELL_VERSION));
    header().file_name().setoriginating_system("IfcOpenShell " + std::string(IFCOPENSHELL_VERSION));
    header().file_name().setauthorization(empty_string);

    header().file_schema().setschema_identifiers(schema_identifiers);
}

std::pair<express::base, double> file::get_unit(const std::string& unit_type) {
    std::pair<express::base, double> return_value(express::base{}, 1.);

    auto projects = instances_by_type(schema()->declaration_by_name("IfcProject"));
    if (projects.empty()) {
        try {
            projects = instances_by_type(schema()->declaration_by_name("IfcContext"));
        } catch (exception&) {
        }
    }

    if (!projects.empty()) {
        auto project = *projects.begin();

        express::base unit_assignment = project.as<express::entity>().get("UnitsInContext");

        std::vector<express::base> units = unit_assignment.as<express::entity>().get("Units");

        for (auto& unit : units) {
            if (unit.declaration().is("IfcNamedUnit")) {
                const std::string file_unit_type = unit.as<express::entity>().get("UnitType");

                if (file_unit_type != unit_type) {
                    continue;
                }

                express::base siunit;
                if (unit.declaration().is("IfcConversionBasedUnit")) {
                    express::base mu = unit.as<express::entity>().get("ConversionFactor");
                    express::base vlc = mu.as<express::entity>().get("ValueComponent");
                    express::base unc = mu.as<express::entity>().get("UnitComponent");
                    return_value.second *= static_cast<double>(vlc.get_attribute_value(0));
                    return_value.first = unit;

                    if (unc.declaration().is("IfcSIUnit")) {
                        siunit = unc;
                    }

                } else if (unit.declaration().is("IfcSIUnit")) {
                    return_value.first = siunit = unit;
                }

                if (siunit) {
                    attribute_value prefix = siunit.as<express::entity>().get("Prefix");
                    if (!prefix.isNull()) {
                        return_value.second *= si_prefix_to_value(prefix);
                    }
                }
            }
        }
    }

    return return_value;
}

void ifcopenshell::file::build_inverses_(const express::base& inst) {
    std::function<void(const express::base&, int)> fn = [this, inst](const express::base& attr, int idx) {
        if (attr.declaration().as_entity() != nullptr) {
            unsigned entity_attribute_id = attr.id();
            const auto* decl = inst.declaration().as_entity();

            std::visit([entity_attribute_id, decl, idx, inst](auto& x) {
                if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
                } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
                    x.byref_excl_.add(entity_attribute_id, inst.id(), (uint16_t)decl->index_in_schema(), idx);
                } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
                    // @todo
                }
            }, storage_);
        }
    };

    apply_individual_instance_visitor(inst).apply(fn);
}

void ifcopenshell::file::unbatch() {
    for (auto& id : batch_deletion_ids_) {
        process_deletion_(instance_by_id(id));
    }
    // keep in memory until all deletions are processed
    for (auto& id : batch_deletion_ids_) {
        byid_.erase(id);
    }
    batch_mode_ = false;
    batch_deletion_ids_.clear();
}

void ifcopenshell::file::reset_identity_cache() {
    std::visit([](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            std::lock_guard<std::mutex> lock(x.instance_cache_mutex_);
            x.instance_cache_.clear();
            x.type_instance_cache_.clear();
        }
	}, storage_);
}

void ifcopenshell::file::build_inverses() {
    for (const auto& pair : *this) {
        build_inverses_(express::base(pair.second));
    }
}

void ifcopenshell::file::register_inverse(unsigned id_from, const ifcopenshell::entity* from_entity, int inst_id, int attribute_index)
{
    std::visit([id_from, from_entity, inst_id, attribute_index](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.register_inverse(id_from, from_entity, inst_id, attribute_index);
        }
    }, storage_);
}

void ifcopenshell::file::unregister_inverse(unsigned id_from, const ifcopenshell::entity* from_entity, const express::base& inst, int attribute_index)
{
    std::visit([id_from, from_entity, inst, attribute_index](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.unregister_inverse(id_from, from_entity, inst, attribute_index);
        }
    }, storage_);
}

std::atomic_uint32_t instance_data::counter_(0);

// bool ifcopenshell::file::guid_map_ = true;

void express::base::unset_attribute_value(size_t index) {
    data()->set_attribute_value(index, blank{});
}

attribute_value express::base::get_attribute_value(size_t index) const {
    return data()->get_attribute_value(index);
}

void express::base::to_string(std::ostream& out, bool upper) const
{
    const auto *ent = declaration().as_entity();
    if (ent != nullptr && declaration().schema() != &Header_section_schema::get_schema()) {
        out << "#" << id() << "=";
    }
    if (upper) {
        out << declaration().name_uc();
    } else {
        out << declaration().name();
    }
    data()->to_string(out, upper);
}

ifcopenshell::file* express::base::file() const {
    return data()->file();
}

/*
instance_data::instance_data(const instance_data& data)
    : storage_(data.size())
{

}
*/

attribute_value instance_data::get_attribute_value(size_t index) const
{
    if (storage_) {
        return attribute_value(storage_, (uint8_t)index);
    } else {
        auto* const storage = std::visit([](auto& m) -> ifcopenshell::impl::rocks_db_file_storage* {
            using U = std::decay_t<decltype(m)>;
            if constexpr (std::is_same_v<U, ifcopenshell::impl::rocks_db_file_storage>) {
                return &m;
            } else {
                return nullptr;
            }
        }, file_->storage_);
        return attribute_value(storage, id_ ? id_ : identity_, declaration_, (uint8_t)index);
    }
}

bool ifcopenshell::impl::rocks_db_file_storage::read_schema(const ifcopenshell::schema_definition*& schema) {
#ifndef IFOPSH_WITH_ROCKSDB
    (void)schema;
#endif
#ifdef IFOPSH_WITH_ROCKSDB
    std::string value;
    auto key = "h|file_schema|0";
    db->Get(rocksdb::ReadOptions{}, key, &value);
    std::vector<std::string> strings;
    if (::impl::deserialize(this, value, strings) && strings.size() == 1) {
        try {
            schema = schema_by_name(strings[0]);
        } catch (exception&) {
            return false;
		}
        return true;
    }
#endif
    return false;
}

    /*
express::base::IfcBaseClass(instance_data&& data)
    : identity_(counter_++)
    , id_(0)
    , file_(nullptr)
    , data_(std::move(data))
{
    * @todo this is not allowed cannot call virtual func in constructor
    if (!declaration().as_entity()) {
        // @nb from v0.9 type decl instances have their own id, which may collide with instance names in the file
        // but is otherwise unique
        id_ = identity_;
    }
}
    */

void express::base::set_attribute_value(size_t i, const express::base& p) {
    set_attribute_value<express::base>(i, p);
}
void express::base::set_attribute_value(const std::string& name, const express::base& p) {
    set_attribute_value<express::base>(name, p);
}

template void IFC_PARSE_API express::base::set_attribute_value<blank>(size_t index, const blank& value);
template void IFC_PARSE_API express::base::set_attribute_value<derived>(size_t index, const derived& value);
template void IFC_PARSE_API express::base::set_attribute_value<int64_t>(size_t index, const int64_t& value);
template void IFC_PARSE_API express::base::set_attribute_value<bool>(size_t index, const bool& value);
template void IFC_PARSE_API express::base::set_attribute_value<boost::logic::tribool>(size_t index, const boost::logic::tribool& value);
template void IFC_PARSE_API express::base::set_attribute_value<double>(size_t index, const double& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::string>(size_t index, const std::string& value);
template void IFC_PARSE_API express::base::set_attribute_value<boost::dynamic_bitset<>>(size_t index, const boost::dynamic_bitset<>& value);
template void IFC_PARSE_API express::base::set_attribute_value<enumeration_reference>(size_t index, const enumeration_reference& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<int64_t>>(size_t index, const std::vector<int64_t>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<double>>(size_t index, const std::vector<double>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<std::string>>(size_t index, const std::vector<std::string>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<boost::dynamic_bitset<>>>(size_t index, const std::vector<boost::dynamic_bitset<>>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<express::base>>(size_t index, const std::vector<express::base>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<std::vector<int64_t>>>(size_t index, const std::vector<std::vector<int64_t>>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<std::vector<double>>>(size_t index, const std::vector<std::vector<double>>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<std::vector<express::base>>>(size_t index, const std::vector<std::vector<express::base>>& value);

template void IFC_PARSE_API express::base::set_attribute_value<blank>(const std::string& name, const blank& value);
template void IFC_PARSE_API express::base::set_attribute_value<derived>(const std::string& name, const derived& value);
template void IFC_PARSE_API express::base::set_attribute_value<int64_t>(const std::string& name, const int64_t& value);
template void IFC_PARSE_API express::base::set_attribute_value<bool>(const std::string& name, const bool& value);
template void IFC_PARSE_API express::base::set_attribute_value<boost::logic::tribool>(const std::string& name, const boost::logic::tribool& value);
template void IFC_PARSE_API express::base::set_attribute_value<double>(const std::string& name, const double& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::string>(const std::string& name, const std::string& value);
template void IFC_PARSE_API express::base::set_attribute_value<boost::dynamic_bitset<>>(const std::string& name, const boost::dynamic_bitset<>& value);
template void IFC_PARSE_API express::base::set_attribute_value<enumeration_reference>(const std::string& name, const enumeration_reference& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<int64_t>>(const std::string& name, const std::vector<int64_t>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<double>>(const std::string& name, const std::vector<double>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<std::string>>(const std::string& name, const std::vector<std::string>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<boost::dynamic_bitset<>>>(const std::string& name, const std::vector<boost::dynamic_bitset<>>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<express::base>>(const std::string& name, const std::vector<express::base>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<std::vector<int64_t>>>(const std::string& name, const std::vector<std::vector<int64_t>>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<std::vector<double>>>(const std::string& name, const std::vector<std::vector<double>>& value);
template void IFC_PARSE_API express::base::set_attribute_value<std::vector<std::vector<express::base>>>(const std::string& name, const std::vector<std::vector<express::base>>& value);

namespace express {
template <typename T>
T entity::get_value(const std::string& name) const {
    auto attr = get(name);
    T v = attr;
    return v;
}

template <typename T>
T entity::get_value(const std::string& name, const T& default_value) const {
    auto attr = get(name);
    if (attr.isNull()) {
        return default_value;
    }
    T v = attr;
    return v;
}
} // namespace express

template int64_t IFC_PARSE_API express::entity::get_value<int64_t>(const std::string&) const;
template bool IFC_PARSE_API express::entity::get_value<bool>(const std::string&) const;
template boost::logic::tribool IFC_PARSE_API express::entity::get_value<boost::logic::tribool>(const std::string&) const;
template double IFC_PARSE_API express::entity::get_value<double>(const std::string&) const;
template std::string IFC_PARSE_API express::entity::get_value<std::string>(const std::string&) const;
template express::base IFC_PARSE_API express::entity::get_value<express::base>(const std::string&) const;
template boost::dynamic_bitset<> IFC_PARSE_API express::entity::get_value<boost::dynamic_bitset<>>(const std::string&) const;
template enumeration_reference IFC_PARSE_API express::entity::get_value<enumeration_reference>(const std::string&) const;
template std::vector<int64_t> IFC_PARSE_API express::entity::get_value<std::vector<int64_t>>(const std::string&) const;
template std::vector<double> IFC_PARSE_API express::entity::get_value<std::vector<double>>(const std::string&) const;
template std::vector<std::string> IFC_PARSE_API express::entity::get_value<std::vector<std::string>>(const std::string&) const;
template std::vector<boost::dynamic_bitset<>> IFC_PARSE_API express::entity::get_value<std::vector<boost::dynamic_bitset<>>>(const std::string&) const;
template std::vector<express::base> IFC_PARSE_API express::entity::get_value<std::vector<express::base>>(const std::string&) const;
template std::vector<std::vector<int64_t>> IFC_PARSE_API express::entity::get_value<std::vector<std::vector<int64_t>>>(const std::string&) const;
template std::vector<std::vector<double>> IFC_PARSE_API express::entity::get_value<std::vector<std::vector<double>>>(const std::string&) const;
template std::vector<std::vector<express::base>> IFC_PARSE_API express::entity::get_value<std::vector<std::vector<express::base>>>(const std::string&) const;

template int64_t IFC_PARSE_API express::entity::get_value<int64_t>(const std::string&, const int64_t&) const;
template bool IFC_PARSE_API express::entity::get_value<bool>(const std::string&, const bool&) const;
template boost::logic::tribool IFC_PARSE_API express::entity::get_value<boost::logic::tribool>(const std::string&, const boost::logic::tribool&) const;
template double IFC_PARSE_API express::entity::get_value<double>(const std::string&, const double&) const;
template std::string IFC_PARSE_API express::entity::get_value<std::string>(const std::string&, const std::string&) const;
template express::base IFC_PARSE_API express::entity::get_value<express::base>(const std::string&, const express::base&) const;
template boost::dynamic_bitset<> IFC_PARSE_API express::entity::get_value<boost::dynamic_bitset<>>(const std::string&, const boost::dynamic_bitset<>&) const;
template enumeration_reference IFC_PARSE_API express::entity::get_value<enumeration_reference>(const std::string&, const enumeration_reference&) const;
template std::vector<int64_t> IFC_PARSE_API express::entity::get_value<std::vector<int64_t>>(const std::string&, const std::vector<int64_t>&) const;
template std::vector<double> IFC_PARSE_API express::entity::get_value<std::vector<double>>(const std::string&, const std::vector<double>&) const;
template std::vector<std::string> IFC_PARSE_API express::entity::get_value<std::vector<std::string>>(const std::string&, const std::vector<std::string>&) const;
template std::vector<boost::dynamic_bitset<>> IFC_PARSE_API express::entity::get_value<std::vector<boost::dynamic_bitset<>>>(const std::string&, const std::vector<boost::dynamic_bitset<>>&) const;
template std::vector<express::base> IFC_PARSE_API express::entity::get_value<std::vector<express::base>>(const std::string&, const std::vector<express::base>&) const;
template std::vector<std::vector<int64_t>> IFC_PARSE_API express::entity::get_value<std::vector<std::vector<int64_t>>>(const std::string&, const std::vector<std::vector<int64_t>>&) const;
template std::vector<std::vector<double>> IFC_PARSE_API express::entity::get_value<std::vector<std::vector<double>>>(const std::string&, const std::vector<std::vector<double>>&) const;
template std::vector<std::vector<express::base>> IFC_PARSE_API express::entity::get_value<std::vector<std::vector<express::base>>>(const std::string&, const std::vector<std::vector<express::base>>&) const;
