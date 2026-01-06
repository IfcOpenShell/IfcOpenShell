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

#include "IfcParse.h"

#include "express.h"
#include "IfcCharacterDecoder.h"
#include "IfcException.h"
#include "IfcFile.h"
#include "IfcLogger.h"
#include "IfcSchema.h"
#include "IfcSIPrefix.h"
#include "FileReader.h"
#include "utils.h"

#include <algorithm>
#include <boost/algorithm/string.hpp>
#include <boost/variant.hpp>
#include <boost/math/special_functions/fpclassify.hpp>
#include <ctime>
#include <set>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <iomanip>

#ifdef USE_MMAP
#include <boost/filesystem/path.hpp>
#endif

#define PERMISSIVE_FLOAT

using namespace IfcParse;

// A static locale for the real number parser. strtod() is locale-dependent, causing issues
// in locales that have ',' as a decimal separator. Therefore the non standard _strtod_l() /
// strtod_l() is used and a reference to the "C" locale is obtained here. The alternative is
// to use std::istringstream::imbue(std::locale::classic()), but there are subtleties in
// parsing in MSVC2010 and it appears to be much slower.
#if defined(_MSC_VER)

static _locale_t locale = (_locale_t)0;
void init_locale() {
    if (locale == (_locale_t)0) {
        locale = _create_locale(LC_NUMERIC, "C");
    }
}

#else

#if defined(__MINGW64__) || defined(__MINGW32__)
#include <locale>
#include <sstream>

typedef void* locale_t;
static locale_t locale = (locale_t)0;

void init_locale() {}

double strtod_l(const char* start, char** end, locale_t loc) {
    double d;
    std::stringstream ss;
    ss.imbue(std::locale::classic());
    ss << start;
    ss >> d;
    size_t nread = ss.tellg();
    *end = const_cast<char*>(start) + nread;
    return d;
}

#else

#ifdef __APPLE__
#include <xlocale.h>
#endif
#include <locale.h>

static locale_t locale = (locale_t)0;
void init_locale() {
    if (locale == (locale_t)0) {
        locale = newlocale(LC_NUMERIC_MASK, "C", (locale_t)0);
    }
}

#endif

#endif

IfcSpfLexer::IfcSpfLexer(IfcParse::FileReader* stream_) {
    stream = stream_;
    decoder_ = new IfcCharacterDecoder(stream_);
}

IfcSpfLexer::~IfcSpfLexer() {
    delete decoder_;
}

size_t IfcSpfLexer::skipWhitespace() const {
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

size_t IfcSpfLexer::skipComment() const {
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

//
// Returns the offset of the current Token and moves cursor to next
//
Token IfcSpfLexer::Next() {

    if (stream->eof()) {
        return Token{};
    }

    while ((skipWhitespace() != 0U) || (skipComment() != 0U)) {
    }

    if (stream->eof()) {
        return Token{};
    }

    auto& str = GetTempString();
    auto pos = stream->tell();
    char character = stream->read();

    // If the cursor is at [()=,;$*] we know token consists of single char
    if (character == '(' ||
        character == ')' ||
        character == '=' ||
        character == ',' ||
        character == ';' ||
        character == '$' ||
        character == '*')
    {
        return OperatorTokenPtr(this, pos, character);
    }

    if (character == '\'') {
        // If a string is encountered defer processing to the IfcCharacterDecoder
        str = *decoder_;
    } else {
        str.assign(&character, 1);

        while (!stream->eof()) {
            // Read character and increment pointer if not starting a new token
            character = stream->peek();
            if (character == '(' ||
                character == ')' ||
                character == '=' ||
                character == ',' ||
                character == ';' ||
                character == '/') {
                break;
            }
            if (!(character == ' ' || character == '\r' || character == '\n' || character == '\t')) {
                str.push_back(character);
            }
            stream->increment();
        }
    }
    return GeneralTokenPtr(this, pos, str);
}

//
// Reads a std::string from the file at specified offset
// Omits whitespace and comments
//
void IfcSpfLexer::TokenString(size_t offset, std::string& buffer) {
    buffer.clear();
	auto local_stream = *this->stream;
	local_stream.seek(offset);
    while (!local_stream.eof()) {
        char character = local_stream.peek();
        if (!buffer.empty() && (character == '(' ||
                                character == ')' ||
                                character == '=' ||
                                character == ',' ||
                                character == ';' ||
                                character == '/')) {
            break;
        }
        local_stream.increment();
        if (character == ' ' ||
            character == '\r' ||
            character == '\n' ||
            character == '\t') {
            continue;
        }
        if (character == '\'') {
            // todo, make decoder use local offset ptr
            auto local_offset = local_stream.tell();
            buffer = decoder_->get(local_offset);
            break;
        }
        buffer.push_back(character);
    }
}

//Note: according to STEP standard, there may be newlines in tokens
/*
inline void RemoveTokenSeparators(FileReader* stream, size_t start, size_t end, std::string& oDestination) {
    oDestination.clear();
    for (unsigned i = start; i < end; i++) {
        char character = stream->get(i);
        if (character == ' ' ||
            character == '\r' ||
            character == '\n' ||
            character == '\t') {
            continue;
        }
        oDestination += character;
    }
}
*/

bool ParseInt(const char* pStart, int& val) {
    char* pEnd;
    long result = strtol(pStart, &pEnd, 10);
    if (*pEnd != 0) {
        return false;
    }
    val = (int)result;
    return true;
}

bool ParseFloat(const char* pStart, double& val) {
    char* pEnd;
#ifdef _MSC_VER
    double result = _strtod_l(pStart, &pEnd, locale);
#else
    double result = strtod_l(pStart, &pEnd, locale);
#endif
    if (*pEnd != 0) {
        return false;
    }
    val = result;
    return true;
}

bool ParseBool(const char* pStart, int& val) {
    if (strlen(pStart) != 3 || pStart[0] != '.' || pStart[2] != '.') {
        return false;
    }
    char mid = pStart[1];

    if (mid == 'T') {
        val = 1;
    } else if (mid == 'F') {
        val = 0;
    } else if (mid == 'U') {
        val = 2;
    } else {
        return false;
    }

    return true;
}

Token IfcParse::OperatorTokenPtr(IfcSpfLexer* lexer, size_t start, char data) {
    Token token(lexer, start, Token_OPERATOR);
    token.value_char = data;
    return token;
}

Token IfcParse::GeneralTokenPtr(IfcSpfLexer* lexer, size_t start, const std::string& tokenStr) {
    Token token(lexer, start, Token_NONE);

    //determine type of the token
    const char& first = tokenStr.front();
    if (first == '#') {
        token.type = Token_IDENTIFIER;
        if (!ParseInt(tokenStr.c_str() + 1, token.value_int)) {
            Logger::Message(Logger::LOG_ERROR, "Token '" + tokenStr + "' at offset " + std::to_string(token.startPos) + " is not valid");
            token.type = Token_OPERATOR;
            token.value_char = '$';
        }
    } else if (first == '\'') {
        token.type = Token_STRING;
    } else if (first == '.') {
        token.type = Token_ENUMERATION;
        if (ParseBool(tokenStr.c_str(), token.value_int)) { //bool is also enumeration
            token.type = Token_BOOL;
        }
    } else if (first == '"') {
        token.type = Token_BINARY;
    } else if (ParseInt(tokenStr.c_str(), token.value_int)) {
        token.type = Token_INT;
    } else if (ParseFloat(tokenStr.c_str(), token.value_double)) {
        token.type = Token_FLOAT;
    } else {
        token.type = Token_KEYWORD;
    }

    return token;
}

bool TokenFunc::isOperator(const Token& token) {
    return token.type == Token_OPERATOR;
}

bool TokenFunc::isOperator(const Token& token, char character) {
    return token.type == Token_OPERATOR && token.value_char == character;
}

bool TokenFunc::isIdentifier(const Token& token) {
    return token.type == Token_IDENTIFIER;
}

bool TokenFunc::isString(const Token& token) {
    return token.type == Token_STRING;
}

bool TokenFunc::isEnumeration(const Token& token) {
    return token.type == Token_ENUMERATION || token.type == Token_BOOL;
}

bool TokenFunc::isBinary(const Token& token) {
    return token.type == Token_BINARY;
}

bool TokenFunc::isKeyword(const Token& token) {
    return token.type == Token_KEYWORD;
}

bool TokenFunc::isInt(const Token& token) {
    return token.type == Token_INT;
}

bool TokenFunc::isBool(const Token& token) {
    // Bool and logical share the same storage type, just logical unknown is stored as 2.
    return token.type == Token_BOOL && token.value_int != 2;
}

bool TokenFunc::isLogical(const Token& token) {
    return token.type == Token_BOOL;
}

bool TokenFunc::isFloat(const Token& token) {
#ifdef PERMISSIVE_FLOAT
    /// NB: We are being more permissive here then allowed by the standard
    return token.type == Token_FLOAT || token.type == Token_INT;
#else
    return token.type == Token_FLOAT;
#endif
}

int TokenFunc::asInt(const Token& token) {
    if (token.type != Token_INT) {
        throw IfcInvalidTokenException(token.startPos, toString(token), "integer");
    }
    return token.value_int;
}

int TokenFunc::asIdentifier(const Token& token) {
    if (token.type != Token_IDENTIFIER) {
        throw IfcInvalidTokenException(token.startPos, toString(token), "instance name");
    }
    return token.value_int;
}

bool TokenFunc::asBool(const Token& token) {
    if (token.type != Token_BOOL) {
        throw IfcInvalidTokenException(token.startPos, toString(token), "boolean");
    }
    return token.value_int == 1;
}

boost::logic::tribool TokenFunc::asLogical(const Token& token) {
    if (token.type != Token_BOOL) {
        throw IfcInvalidTokenException(token.startPos, toString(token), "boolean");
    }
    if (token.value_int == 0) {
        return false;
    }
    if (token.value_int == 1) {
        return true;
    }
    return boost::logic::indeterminate;
}

double TokenFunc::asFloat(const Token& token) {
#ifdef PERMISSIVE_FLOAT
    if (token.type == Token_INT) {
        /// NB: We are being more permissive here then allowed by the standard
        return token.value_int;
    } // ----> continues beyond preprocessor directive
#endif
    if (token.type == Token_FLOAT) {
        return token.value_double;
    }
    throw IfcInvalidTokenException(token.startPos, toString(token), "real");
}

const std::string& TokenFunc::asStringRef(const Token& token) {
    if (token.type == Token_NONE) {
        throw IfcParse::IfcException("Null token encountered, premature end of file?");
    }
    std::string& str = token.lexer->GetTempString();
    token.lexer->TokenString(token.startPos, str);
    if ((isString(token) || isEnumeration(token) || isBinary(token)) && !str.empty()) {
        //remove start+end characters in-place
        str.erase(str.end() - 1);
        str.erase(str.begin());
    }
    return str;
}

std::string TokenFunc::asString(const Token& token) {
    if (isString(token) || isEnumeration(token) || isBinary(token)) {
        return asStringRef(token);
    }
    throw IfcInvalidTokenException(token.startPos, toString(token), "string");
}

boost::dynamic_bitset<> TokenFunc::asBinary(const Token& token) {
    const std::string& str = asStringRef(token);
    if (str.empty()) {
        throw IfcException("Token is not a valid binary sequence");
    }

    std::string::const_iterator it = str.begin();
    int n = *it - '0';
    if ((n < 0 || n > 3) || (str.size() == 1 && n != 0)) {
        throw IfcException("Token is not a valid binary sequence");
    }

    ++it;
    unsigned i = ((unsigned)str.size() - 1) * 4 - n;
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

std::string TokenFunc::toString(const Token& token) {
    std::string result;
    if (token.type == Token_OPERATOR) {
		result.push_back(token.value_char);
    } else if (token.type == Token_INT) {
        result = std::to_string(token.value_int);
    } else if (token.type == Token_BOOL) {
        if (token.value_int == 1) {
            result = ".T.";
        } else if (token.value_int == 0) {
            result = ".F.";
        } else {
            result = ".U.";
        }
    } else if (token.type == Token_FLOAT) {
        std::ostringstream oss;
        oss << std::setprecision(15) << token.value_double;
        result = oss.str();
	} else {
        token.lexer->TokenString(token.startPos, result);
    }
    return result;
}

//
// Reads the arguments from a list of token
// Aditionally, registers the ids (i.e. #[\d]+) in the inverse map
//
void IfcParse::impl::in_memory_file_storage::load(std::optional<size_t> entity_instance_name, const IfcParse::entity* entity, parse_context& context, int attribute_index) {
    Token next = tokens->Next();

    /*
    if (TokenFunc::isOperator(next, '(')) {
        next = tokens->Next();
    }
    */

    size_t attribute_index_within_data = 0;
    size_t return_value = 0;

    while ((next.startPos != 0U) || (next.lexer != nullptr)) {
        if (TokenFunc::isOperator(next, ',')) {
            if (attribute_index == -1) {
                attribute_index_within_data += 1;
            }
        } else if (TokenFunc::isOperator(next, ')')) {
            break;
        } else if (TokenFunc::isOperator(next, '(')) {
            return_value++;
            load(entity_instance_name, entity, context.push(), attribute_index == -1 ? (int) attribute_index_within_data : attribute_index);
        } else {
            return_value++;
            if (TokenFunc::isIdentifier(next) && entity && entity_instance_name) {
                register_inverse(*entity_instance_name, entity, next.value_int, attribute_index == -1 ? (int) attribute_index_within_data : attribute_index);
            }

            if (TokenFunc::isKeyword(next)) {
                try {
                    const auto* decl = (schema ? schema : file->schema())->declaration_by_name(TokenFunc::asStringRef(next));
                    parse_context ps;
                    tokens->Next();
                    // The only case we know where a defined type contains entity
                    // instance references is IfcPropertySetDefinitionSet. For
                    // that purpose we propagate the entity_instance_name to
                    // register inverses to the host entity (and not the defined
                    // type) and to be able to actually register the references in
                    // the 2nd pass.
                    load(entity_instance_name, entity, ps, attribute_index == -1 ? (int)attribute_index_within_data : attribute_index);
                    express::Base simple_type_instance(read_simple_type_instances.emplace_back(
                        ps.construct(file, entity_instance_name, *references_to_resolve, decl, std::nullopt, attribute_index == -1 ? (int)attribute_index_within_data : attribute_index))
                    );
                    // @todo do we need express::Base here? Or should we just push InstanceData?
                    context.push(simple_type_instance);
                } catch (IfcException& e) {
                    Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + " at offset " + std::to_string(next.startPos));
                    // #4070 We didn't actually capture an aggregate entry, undo length increment.
                    return_value--;
                }
            } else {
                context.push(next);
            }
        }
        next = tokens->Next();
    }
}

//
// Reads an Entity from the list of Tokens at the specified offset in the file
//
std::shared_ptr<InstanceData> IfcParse::impl::in_memory_file_storage::read(unsigned int i) {
    Token datatype = tokens->Next();
    if (!TokenFunc::isKeyword(datatype)) {
        throw IfcException("Unexpected token while parsing entity");
    }
    const IfcParse::declaration* ty = file->schema()->declaration_by_name(TokenFunc::asStringRef(datatype));
    parse_context pc;
    tokens->Next();
    load(i, ty->as_entity(), pc, -1);
    return pc.construct(file, i, *references_to_resolve, ty, std::nullopt, -1);
}

void IfcParse::impl::in_memory_file_storage::try_read_semicolon() const {
    auto old_offset = tokens->stream->tell();
    Token semilocon = tokens->Next();
    if (!TokenFunc::isOperator(semilocon, ';')) {
        tokens->stream->seek(old_offset);
    }
}

void IfcParse::impl::in_memory_file_storage::register_inverse(unsigned id_from, const IfcParse::entity* from_entity, int inst_id, int attribute_index) {
    // Assume a check on token type has already been performed
    byref_excl_[{inst_id, from_entity->index_in_schema(), attribute_index}].push_back(id_from);
}

void IfcParse::impl::in_memory_file_storage::unregister_inverse(unsigned id_from, const IfcParse::entity* from_entity, const express::Base& inst, int attribute_index) {
    auto& ids = byref_excl_[{inst.id(), from_entity->index_in_schema(), attribute_index}];
    auto iter = std::find(ids.begin(), ids.end(), id_from);
    if (iter == ids.end()) {
        // @todo inverses also need to be populated when multiple instances are added to a new file.
        // throw IfcParse::IfcException("Instance not found among inverses");
    } else {
        ids.erase(iter);
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

void IfcParse::impl::rocks_db_file_storage::register_inverse(unsigned id_from, const IfcParse::entity* from_entity, int inst_id, int attribute_index) {
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

void IfcParse::impl::rocks_db_file_storage::unregister_inverse(unsigned id_from, const IfcParse::entity* from_entity, const express::Base& inst, int attribute_index) {
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
            Logger::Error("Unregistering non-existant inverse #" + std::to_string(id_from) + " on instance #" + std::to_string(inst_id) + " at attribute " + std::to_string(attribute_index));
        }
        s.resize(vals.size() * sizeof(uint32_t));
        memcpy(s.data(), vals.data(), s.size());
        db->Put(wopts, key, s);
    }
#endif
}

void IfcParse::impl::rocks_db_file_storage::add_type_ref(const express::Base& new_entity)
{
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

void IfcParse::impl::rocks_db_file_storage::remove_type_ref(const express::Base& new_entity)
{
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
    class StringBuilderVisitor : public boost::static_visitor<void> {
    private:
        StringBuilderVisitor(const StringBuilderVisitor&);            //N/A
        StringBuilderVisitor& operator=(const StringBuilderVisitor&); //N/A

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
        // The REAL token definition from the IFC SPF standard does not necessarily match
        // the output of the C++ ostream formatting operation.
        // REAL = [ SIGN ] DIGIT { DIGIT } "." { DIGIT } [ "E" [ SIGN ] DIGIT { DIGIT } ] .
        static std::string format_double(const double& d) {
            std::ostringstream oss;
            oss.imbue(std::locale::classic());
            oss << std::setprecision(std::numeric_limits<double>::digits10) << d;
            const std::string str = oss.str();
            oss.str("");
            std::string::size_type e = str.find('e');
            if (e == std::string::npos) {
                e = str.find('E');
            }
            const std::string mantissa = str.substr(0, e);
            oss << mantissa;
            if (mantissa.find('.') == std::string::npos) {
                oss << ".";
            }
            if (e != std::string::npos) {
                oss << "E";
                oss << str.substr(e + 1);
            }
            return oss.str();
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
        StringBuilderVisitor(std::ostream& stream, bool upper = false)
            : data_(stream),
            upper_(upper) {}
        void operator()(const Blank& /*i*/) { data_ << "$"; }
        void operator()(const Derived& /*i*/) { data_ << "*"; }
        void operator()(const int& i) { data_ << i; }
        void operator()(const bool& i) { data_ << (i ? ".T." : ".F."); }
        void operator()(const boost::logic::tribool& i) { data_ << (i ? ".T." : (boost::logic::indeterminate(i) ? ".U." : ".F.")); }
        void operator()(const double& i) { data_ << format_double(i); }
        void operator()(const boost::dynamic_bitset<>& i) { data_ << format_binary(i); }
        void operator()(const std::string& i) {
            std::string s = i;
            if (upper_) {
                data_ << static_cast<std::string>(IfcCharacterEncoder(s));
            } else {
                data_ << '\'' << s << '\'';
            }
        }
        void operator()(const std::vector<int>& i);
        void operator()(const std::vector<double>& i);
        void operator()(const std::vector<std::string>& i);
        void operator()(const std::vector<boost::dynamic_bitset<>>& i);
        void operator()(const EnumerationReference& i) {
            data_ << "." << i.value() << ".";
        }
        void operator()(const express::Base& i) {
            if (i.declaration().as_entity() == nullptr || i.declaration().schema() == &Header_section_schema::get_schema()) {
                i.toString(data_, upper_);
            } else {
                data_ << "#" << i.id();
            }
        }
        void operator()(const std::vector<express::Base>& i) {
            data_ << "(";
            for (auto it = i.begin(); it != i.end(); ++it) {
                if (it != i.begin()) {
                    data_ << ",";
                }
                (*this)(*it);
            }
            data_ << ")";
        }
        void operator()(const std::vector<std::vector<int>>& i);
        void operator()(const std::vector<std::vector<double>>& i);
        void operator()(const std::vector<std::vector<express::Base>>& i) {
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
        void operator()(const empty_aggregate_t& /*unused*/) const { data_ << "()"; }
        void operator()(const empty_aggregate_of_aggregate_t& /*unused*/) const { data_ << "()"; }
    };

    template <>
    void StringBuilderVisitor::serialize(const std::vector<std::string>& i) {
        data_ << "(";
        for (std::vector<std::string>::const_iterator it = i.begin(); it != i.end(); ++it) {
            if (it != i.begin()) {
                data_ << ",";
            }
            std::string encoder = IfcCharacterEncoder(*it);
            data_ << encoder;
        }
        data_ << ")";
    }

    template <>
    void StringBuilderVisitor::serialize(const std::vector<double>& i) {
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
    void StringBuilderVisitor::serialize(const std::vector<boost::dynamic_bitset<>>& i) {
        data_ << "(";
        for (std::vector<boost::dynamic_bitset<>>::const_iterator it = i.begin(); it != i.end(); ++it) {
            if (it != i.begin()) {
                data_ << ",";
            }
            data_ << format_binary(*it);
        }
        data_ << ")";
    }

    void StringBuilderVisitor::operator()(const std::vector<int>& i) { serialize(i); }
    void StringBuilderVisitor::operator()(const std::vector<double>& i) { serialize(i); }
    void StringBuilderVisitor::operator()(const std::vector<std::string>& i) { serialize(i); }
    void StringBuilderVisitor::operator()(const std::vector<boost::dynamic_bitset<>>& i) { serialize(i); }
    void StringBuilderVisitor::operator()(const std::vector<std::vector<int>>& i) {
        data_ << "(";
        for (std::vector<std::vector<int>>::const_iterator it = i.begin(); it != i.end(); ++it) {
            if (it != i.begin()) {
                data_ << ",";
            }
            serialize(*it);
        }
        data_ << ")";
    }
    void StringBuilderVisitor::operator()(const std::vector<std::vector<double>>& i) {
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
void InstanceData::toString(std::ostream& ss, bool upper) const {
    ss.imbue(std::locale::classic());

    ss << "(";

    StringBuilderVisitor vis(ss, upper);

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
        if (has_attribute_value<Blank>(i)) {
            if (declaration_ != nullptr && declaration_->as_entity() && declaration_->as_entity()->derived()[i]) {
               ss << "*";
            } else {
               ss << "$";
	        }
        } else {
            apply_visitor(vis, i);
        }
    }
    ss << ")";
}

/*
unsigned IfcUtil::IfcBaseEntity::set_id(const std::optional<unsigned>& i) {
    if (i) {
        return id_ = *i;
    }
    return id_ = file_->FreshId();
}
*/

namespace {
// @todo remove redundancy with python wrapper code (which is not identical due to
// different handling of enumerations)
IfcUtil::ArgumentType get_argument_type(const IfcParse::declaration* decl, size_t i) {
    const IfcParse::parameter_type* pt = 0;
    if (decl->as_entity() != nullptr) {
        pt = decl->as_entity()->attribute_by_index(i)->type_of_attribute();
        if (decl->as_entity()->derived()[i]) {
            return IfcUtil::Argument_DERIVED;
        }
    } else if ((decl->as_type_declaration() != nullptr) && i == 0) {
        pt = decl->as_type_declaration()->declared_type();
    } else if ((decl->as_enumeration_type() != nullptr) && i == 0) {
        return IfcUtil::Argument_ENUMERATION;
    }

    if (pt == 0) {
        return IfcUtil::Argument_UNKNOWN;
    }
    return IfcUtil::from_parameter_type(pt);
}
} // namespace

class unregister_inverse_visitor {
  private:
    IfcFile& file_;
    const express::Base data_;

  public:
    unregister_inverse_visitor(IfcFile& file, const express::Base& data)
        : file_(file),
          data_(data) {}

    void operator()(const express::Base& inst, int index) {
        file_.unregister_inverse(data_.id(), data_.declaration().as_entity(), inst, index);
    }
};

class register_inverse_visitor {
  private:
    IfcFile& file_;
    const express::Base data_;

  public:
    register_inverse_visitor(IfcFile& file, const express::Base& data)
        : file_(file),
          data_(data) {}

    void operator()(const express::Base& inst, int index) {
        file_.register_inverse(data_.id(), data_.declaration().as_entity(), inst.id(), index);
    }
};

class add_to_instance_list_visitor {
  private:
    std::vector<express::Base>* list_;

  public:
    add_to_instance_list_visitor(std::vector<express::Base>* list)
        : list_(list) {}

    void operator()(const express::Base& inst) {
        list_->push_back(inst);
    }
};

class apply_individual_instance_visitor {
  private:
    std::optional<AttributeValue> attribute_;
    int attribute_index_;

    const express::Base inst_;


    template <typename T>
    void apply_attribute_(T& t, const AttributeValue& attr, int index) const {
        switch (attr.type()) {
        case IfcUtil::Argument_ENTITY_INSTANCE: {
            express::Base inst = attr;
            t(inst, index);
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
            std::vector<express::Base> entity_list_attribute = attr;
            for (auto& inst : entity_list_attribute) {
                t(inst, index);
            }
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
            std::vector<std::vector<express::Base>> nested_list_attr = attr;
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
    apply_individual_instance_visitor(const AttributeValue& attribute, int idx)
        : attribute_(attribute)
        , attribute_index_(idx)
    {}

    apply_individual_instance_visitor(const express::Base& data)
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
    (!std::is_base_of_v<express::Base, T> || std::is_same_v<express::Base, T>),
    void>::type
express::Base::set_attribute_value(size_t i, const T& t) {
    if constexpr (std::is_same_v<std::decay_t<T>, double>) {
        if (!std::isfinite(t)) {
            throw IfcParse::IfcException("Only finite values are allowed");
        }
    }
    if constexpr (std::is_same_v<std::decay_t<T>, std::vector<double>>) {
        if (std::any_of(t.begin(), t.end(), [](double d) { return !std::isfinite(d); })) {
            throw IfcParse::IfcException("Only finite values are allowed");
        }
    }
    if constexpr (std::is_same_v<std::decay_t<T>, std::vector<std::vector<double>>>) {
        for (auto& tt : t) {
            if (std::any_of(tt.begin(), tt.end(), [](double d) { return !std::isfinite(d); })) {
                throw IfcParse::IfcException("Only finite values are allowed");
            }
        }
    }
    auto current_attribute = get_attribute_value(i);

    // Deregister old attribute guid in file guid map.
    if (i == 0 && (data()->file()->ifcroot_type() != nullptr) && this->declaration().is(*data()->file()->ifcroot_type())) {
        try {
            auto guid = (std::string) current_attribute;
            auto it = data()->file()->internal_guid_map().find(guid);
            if (it != data()->file()->internal_guid_map().end()) {
                const std::pair<const std::string, express::Base>& p = *it;
                if (p.second == *this) {
                    data()->file()->internal_guid_map().erase(it);
                }
            }
        } catch (IfcParse::IfcException& e) {
            Logger::Error(e);
        }
    }

    if constexpr (std::is_same_v<T, express::Base> || std::is_same_v<T, std::vector<express::Base>> || std::is_same_v<T, std::vector<std::vector<express::Base>>> || std::is_same_v<T, Blank>) {
        // Deregister inverse indices in file
        unregister_inverse_visitor visitor(*data()->file(), *this);
        apply_individual_instance_visitor(current_attribute, (int)i).apply(visitor);
    }

    {
        void* const storage = std::visit([](const auto& m) { return (void*)&m; }, data()->file()->storage_);
        data()->set_attribute_value(i, t);
    }
    auto new_attribute = get_attribute_value(i);

    // Register inverse indices in file
    if constexpr (std::is_same_v<T, express::Base> || std::is_same_v<T, std::vector<express::Base>> || std::is_same_v<T, std::vector<std::vector<express::Base>>>) {
        register_inverse_visitor visitor(*data()->file(), *this);
        apply_individual_instance_visitor(new_attribute, (int)i).apply(visitor);
    }
    
    // Register new attribute guid in guid map
    if (i == 0 && (data()->file()->ifcroot_type() != nullptr) && this->declaration().is(*data()->file()->ifcroot_type())) {
        try {
            auto guid = (std::string) new_attribute;
            auto it = data()->file()->internal_guid_map().find(guid);
            if (it != data()->file()->internal_guid_map().end()) {
                Logger::Warning("Duplicate guid " + guid);
            }
            data()->file()->internal_guid_map().insert({guid, *this});
        } catch (IfcParse::IfcException& e) {
            Logger::Error(e);
        }
    }
}

template <typename T>
typename std::enable_if<
    (!std::is_base_of_v<express::Base, T> || std::is_same_v<express::Base, T>),
    void>::type
express::Base::set_attribute_value(const std::string& s, const T& t)
{
    set_attribute_value(declaration().as_entity()->attribute_index(s), t);
}

//
// Parses the IFC file in fn
// Creates the maps
//
#ifdef USE_MMAP
IfcFile::IfcFile(const std::string& fn, bool mmap) {
    initialize(fn, mmap);
}

bool IfcParse::IfcFile::initialize(const std::string& fn, bool mmap) {
    std::unique_ptr<FileReader> s;
    if (mmap) {
        s = std::make_unique<FileReader>(fn, FileReader::mmap_tag{});
    } else {
        s = std::make_unique<FileReader>(fn);
    }

    storage_.emplace<1>(this);
    std::get<impl::in_memory_file_storage>(storage_).read_from_stream(&*s, schema_, max_id_, types_to_bypass_loading_);

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

IfcFile::IfcFile(const uninitialized_tag&)
    : schema_(nullptr), max_id_(0), header_(new IfcParse::IfcSpfHeader(this)), good_(file_open_status::UNKNOWN), ifcroot_type_(nullptr) {}

bool IfcParse::IfcFile::initialize(const std::string& path, filetype ty, bool readonly) {
    if (ty == FT_AUTODETECT) {
        ty = guess_file_type(path);
    }
    if (ty == FT_IFCSPF) {
        FileReader s(path);
        storage_.emplace<1>(this);
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
    return good_ == file_open_status::SUCCESS;
}

void IfcParse::IfcFile::bypass_type(const std::string& type_name) {
    types_to_bypass_loading_.insert(type_name);
}

IfcFile::IfcFile(const std::string& path, filetype ty, bool readonly)
    : schema_(nullptr)
    , max_id_(0)
    , header_(new IfcSpfHeader(this))
{
    initialize(path, ty, readonly);
}

IfcFile::IfcFile(std::istream& stream, int length)
    : schema_(nullptr)
    , max_id_(0)
{
    FileReader s(FileReader::caller_fed_tag{});

    std::string string_data;
	string_data.resize(length);
	stream.read(string_data.data(), length);
    s.pushNextPage(string_data);

    storage_.emplace<1>(this);
    std::get<impl::in_memory_file_storage>(storage_).read_from_stream(&s, schema_, max_id_, types_to_bypass_loading_);
    good_ = std::get<impl::in_memory_file_storage>(storage_).good_;
    ifcroot_type_ = schema_ ? schema_->declaration_by_name("IfcRoot") : nullptr;

    byid_ = decltype(byid_)(&std::get<impl::in_memory_file_storage>(storage_).byid_read_);
    byref_excl_ = decltype(byref_excl_)(&std::get<impl::in_memory_file_storage>(storage_).byref_excl_);
    byguid_ = decltype(byguid_)(&std::get<impl::in_memory_file_storage>(storage_).byguid_);
}

IfcFile::IfcFile(void* data, int length)
    : schema_(nullptr)
    , max_id_(0)
{
	FileReader s(std::string((char*)data, length), FileReader::caller_fed_tag{});
    
    storage_.emplace<1>(this);
    std::get<impl::in_memory_file_storage>(storage_).read_from_stream(&s, schema_, max_id_, types_to_bypass_loading_);
    good_ = std::get<impl::in_memory_file_storage>(storage_).good_;
    ifcroot_type_ = schema_ ? schema_->declaration_by_name("IfcRoot") : nullptr;

    byid_ = decltype(byid_)(&std::get<impl::in_memory_file_storage>(storage_).byid_read_);
    byref_excl_ = decltype(byref_excl_)(&std::get<impl::in_memory_file_storage>(storage_).byref_excl_);
    byguid_ = decltype(byguid_)(&std::get<impl::in_memory_file_storage>(storage_).byguid_);
}

IfcFile::IfcFile(IfcParse::FileReader* s)
    : schema_(nullptr)
    , max_id_(0)
{
    storage_.emplace<1>(this);
    std::get<impl::in_memory_file_storage>(storage_).read_from_stream(s, schema_, max_id_, types_to_bypass_loading_);
    good_ = std::get<impl::in_memory_file_storage>(storage_).good_;
    ifcroot_type_ = schema_ ? schema_->declaration_by_name("IfcRoot") : nullptr;

    byid_ = decltype(byid_)(&std::get<impl::in_memory_file_storage>(storage_).byid_read_);
    byref_excl_ = decltype(byref_excl_)(&std::get<impl::in_memory_file_storage>(storage_).byref_excl_);
    byguid_ = decltype(byguid_)(&std::get<impl::in_memory_file_storage>(storage_).byguid_);
}

IfcFile::IfcFile(const IfcParse::schema_definition* schema, filetype ty, const std::string& path)
    : schema_(schema)
    , ifcroot_type_(schema_->declaration_by_name("IfcRoot"))
    , max_id_(0)
{
    if (ty == FT_AUTODETECT) {
        ty = guess_file_type(path);
    }
    if (ty == FT_IFCSPF) {
        storage_.emplace<1>(this);

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
    header_.reset(new IfcSpfHeader(this));
    setDefaultHeaderValues();
}

bool IfcParse::InstanceStreamer::hasSemicolon() const {
    auto local_stream = stream_->clone();
	auto local_lexer = IfcSpfLexer(&local_stream);
    Token t;
    try {
        t = local_lexer.Next();
    } catch (const std::out_of_range&) {
        return false;
    }
    while (t.type != Token_NONE) {
        if (TokenFunc::isOperator(t, ';')) {
            return true;
		}
        try {
            t = local_lexer.Next();
        } catch (const std::out_of_range&) {
            // This most likely happens when a page boundary is contained within a string
            break;
        }
    }
	return false;
}

size_t IfcParse::InstanceStreamer::semicolonCount() const {
    auto local_stream = stream_->clone();
    auto local_lexer = IfcSpfLexer(&local_stream);
    Token t;
    size_t count = 0;
    try {
        t = local_lexer.Next();
    } catch (const std::out_of_range&) {
        return false;
    }
    while (t.type != Token_NONE) {
        if (TokenFunc::isOperator(t, ';')) {
            count++;
        }
        try {
            t = local_lexer.Next();
        } catch (const std::out_of_range&) {
            // This most likely happens when a page boundary is contained within a string
            break;
        }
    }
    return count;
}

void IfcParse::InstanceStreamer::pushPage(const std::string& page)
{
    stream_->pushNextPage(page);
    if (good_ == file_open_status::NO_HEADER) {
        header_ = new IfcParse::IfcSpfHeader(lexer_);
        if (header_->tryRead() && header_->file_schema().schema_identifiers().size() == 1) {
            try {
                schema_ = IfcParse::schema_by_name(header_->file_schema().schema_identifiers().front());
                good_ = file_open_status::SUCCESS;
            } catch (const IfcParse::IfcException&) {
            }
        }
        storage_.file = nullptr;
        storage_.schema = schema_;
        storage_.tokens = lexer_;
        storage_.references_to_resolve = &references_to_resolve_;
    }
}

IfcParse::InstanceStreamer::InstanceStreamer()
    : stream_(new FileReader(FileReader::caller_fed_tag{}))
    , lexer_(new IfcSpfLexer(stream_))
    , token_stream_(3, Token{})
    , schema_(nullptr)
    , progress_(0)
{
    init_locale();
    good_ = file_open_status::NO_HEADER;
}

IfcParse::InstanceStreamer::InstanceStreamer(const std::string& fn, bool mmap)
    : stream_(mmap ? new FileReader(fn, FileReader::mmap_tag{}) : new FileReader(fn))
    , lexer_(new IfcSpfLexer(stream_))
    , token_stream_(3, Token{})
    , schema_(nullptr)
    , progress_(0)
{
    init_locale();

    good_ = file_open_status::NO_HEADER;
    if (stream_->size() && !stream_->eof()) {
        header_ = new IfcParse::IfcSpfHeader(lexer_);
        if (header_->tryRead() && header_->file_schema().schema_identifiers().size() == 1) {
            try {
                schema_ = IfcParse::schema_by_name(header_->file_schema().schema_identifiers().front());
                good_ = file_open_status::SUCCESS;
            } catch (const IfcParse::IfcException&) {
            }
        }
        storage_.file = nullptr;
        storage_.schema = schema_;
        storage_.tokens = lexer_;
        storage_.references_to_resolve = &references_to_resolve_;
    }
}

IfcParse::InstanceStreamer::InstanceStreamer(void* data, int length)
    : stream_(new FileReader(std::string((char*) data, length), FileReader::caller_fed_tag{}))
    , lexer_(new IfcSpfLexer(stream_))
    , token_stream_(3, Token{})
    , schema_(nullptr)
    , progress_(0)
{
    init_locale();

    good_ = file_open_status::NO_HEADER;
    if (stream_->size() && !stream_->eof()) {
        header_ = new IfcParse::IfcSpfHeader(lexer_);
        if (header_->tryRead() && header_->file_schema().schema_identifiers().size() == 1) {
            try {
                schema_ = IfcParse::schema_by_name(header_->file_schema().schema_identifiers().front());
                good_ = file_open_status::SUCCESS;
            } catch (const IfcParse::IfcException&) {
            }
        }
        storage_.file = nullptr;
        storage_.schema = schema_;
        storage_.tokens = lexer_;
        storage_.references_to_resolve = &references_to_resolve_;
    }
}

IfcParse::InstanceStreamer::InstanceStreamer(const IfcParse::schema_definition* schema, IfcParse::IfcSpfLexer* lexer)
    : stream_(nullptr)
    , lexer_(lexer)
    , header_(nullptr)
    , token_stream_(3, Token{})
    , schema_(schema)
    , progress_(0)
{
    init_locale();

    storage_.file = nullptr;
    storage_.schema = schema_;
    storage_.tokens = lexer_;
    storage_.references_to_resolve = &references_to_resolve_;
}

void IfcParse::impl::in_memory_file_storage::read_from_stream(IfcParse::FileReader* s, const IfcParse::schema_definition*& schema, unsigned int& max_id, const std::set<std::string>& typed_to_bypass) {
    // Initialize a "C" locale for locale-independent
    // number parsing. See comment above on line 41.
    init_locale();

    tokens = nullptr;

    if (!s->size() || s->eof()) {
        // @todo set good on parent file
        good_ = file_open_status::READ_ERROR;
        return;
    }

    tokens = new IfcSpfLexer(s);

    std::vector<std::string> schemas;

    file->header().file(file);

    if (file->header().tryRead()) {
        try {
            schemas = file->header().file_schema().schema_identifiers();
        } catch (...) {
            // Purposely empty catch block
        }
    } else {
        good_ = file_open_status::NO_HEADER;
    }

    if (schemas.size() == 1) {
        try {
            schema = IfcParse::schema_by_name(schemas.front());
        } catch (const IfcParse::IfcException& e) {
            good_ = file_open_status::UNSUPPORTED_SCHEMA;
            Logger::Error(e);
        }
    }

    if (schema == nullptr) {
        Logger::Message(Logger::LOG_ERROR, "No support for file schema encountered (" + boost::algorithm::join(schemas, ", ") + ")");
        return;
    }

    auto ifcroot_type_ = schema->declaration_by_name("IfcRoot");

	InstanceStreamer streamer(schema, tokens);
    streamer.owner = file;
    streamer.bypassTypes(typed_to_bypass);

    Logger::Status("Scanning file...");

    while (streamer) {

        auto inst = streamer.readInstance();

        if (!inst) {
            // No more instances to read
            break;
		}

        auto current_id = std::get<0>(*inst);

        express::Base instance(std::get<2>(*inst));

        if (instance.declaration().is(*ifcroot_type_)) {
            try {
                const std::string guid = instance.get_attribute_value(0);
                if (byguid_.find(guid) != byguid_.end()) {
                    std::stringstream ss;
                    ss << "Instance encountered with non-unique GlobalId " << guid;
                    Logger::Message(Logger::LOG_WARNING, ss.str());
                }
                byguid_[guid] = instance;
            } catch (const IfcException& ex) {
                Logger::Message(Logger::LOG_ERROR, ex.what());
            }
        }

        const IfcParse::declaration* ty = &instance.declaration();

        {
            bytype_excl_[ty].push_back(instance);
        }

        if (byid_.find(current_id) != byid_.end()) {
            std::stringstream ss;
            ss << "Overwriting instance with name #" << current_id;
            Logger::Message(Logger::LOG_WARNING, ss.str());
        }

        byid_.insert({(uint32_t)current_id, std::get<2>(*inst)});
        max_id = (std::max)(max_id, (unsigned int) current_id);
    }

	good_ = streamer.status();
	byref_excl_ = streamer.inverses();
    
	// Move the storage of simple type instances so that they are retained during the lifetime of the file
    read_simple_type_instances = streamer.stealInstances();

    // Set file ownership on simple type instances, so that when adding them to other files, proper copies are created
    /*
    // @todo double check whether file ownership is property set earlier on
    for (auto& inst : read_simple_type_instances) {
        inst->file_ = file;
    }
    */

    Logger::Status("\rDone scanning file   ");

    delete tokens;

    if (good_ != file_open_status::SUCCESS) {
        return;
    }

    const auto& bypassed = streamer.bypassed_instances();

    for (const auto& p : streamer.references()) {
        const auto& ref = p.first.name_;
        const auto& refattr = p.first.index_;
        if (auto* v = std::get_if<reference_or_simple_type>(&p.second)) {
            if (auto* name = std::get_if<InstanceReference>(v)) {
                if (std::binary_search(bypassed.begin(), bypassed.end(), *name)) {
                    continue;
                }
                auto it = byid_.find(*name);
                if (it == byid_.end()) {
                    Logger::Error("Instance reference #" + std::to_string(*name) + " used by instance #" + std::to_string(ref) + " at attribute index " + std::to_string(refattr) + " not found at offset " + std::to_string(name->file_offset));
                } else {
                    auto& storage = byid_[p.first.name_];
                    auto attr_index = p.first.index_;
                    
                    if (storage->has_attribute_value<express::Base>(attr_index)) {
                        express::Base inst = storage->get_attribute_value(attr_index);
                        if (!inst.declaration().as_entity()) {
                            // Probably a case of IfcPropertySetDefinitionSet, divert storage of reference to the simply type instance
                            storage = inst.data_weak().lock();
                            attr_index = 0;
                        }
                    }

                    if (storage->has_attribute_value<Blank>(attr_index)) {
                        storage->set_attribute_value(attr_index, express::Base(it->second));
                    } else {
                        Logger::Error("Duplicate definition for instance reference");
                    }
                }
            } else if (auto inst = std::get_if<express::Base>(v)) {
                byid_[p.first.name_]->set_attribute_value(p.first.index_, *inst);
            }
        } else if (auto* vv = std::get_if<std::vector<reference_or_simple_type>>(&p.second)) {
            std::vector<express::Base> instances;
            instances.reserve(vv->size());
            for (const auto& vi : *vv) {
                if (auto* name = std::get_if<InstanceReference>(&vi)) {
                    if (std::binary_search(bypassed.begin(), bypassed.end(), *name)) {
                        continue;
                    }
                    auto it = byid_.find(*name);
                    if (it == byid_.end()) {
                        Logger::Error("Instance reference #" + std::to_string(*name) + " used by instance #" + std::to_string(ref) + " at attribute index " + std::to_string(refattr) + " not found at offset " + std::to_string(name->file_offset));
                    } else {
                        instances.push_back(express::Base(it->second));
                    }
                } else if (auto* inst = std::get_if<express::Base>(&vi)) {
                    instances.push_back(*inst);
                }
            }

            auto& storage = byid_[p.first.name_];
            auto attr_index = p.first.index_;
            
            if (storage->has_attribute_value<express::Base>(attr_index)) {
                express::Base inst = storage->get_attribute_value(attr_index);
                if (!inst.declaration().as_entity()) {
                    // Probably a case of IfcPropertySetDefinitionSet, divert storage of reference to the simply type instance
                    storage = inst.data_weak().lock();
                    attr_index = 0;
                }
            }

            if (storage->has_attribute_value<Blank>(attr_index)) {
                storage->set_attribute_value(attr_index, instances);
            } else {
                Logger::Error("Duplicate definition for instance reference");
            }
        } else if (auto* vvv = std::get_if<std::vector<std::vector<reference_or_simple_type>>>(&p.second)) {
            std::vector<std::vector<express::Base>> instances;
            for (const auto& vi : *vvv) {
                auto& inner = instances.emplace_back();
                for (const auto& vii : vi) {
                    if (auto* name = std::get_if<InstanceReference>(&vii)) {
                        if (std::binary_search(bypassed.begin(), bypassed.end(), *name)) {
                            continue;
                        }
                        auto it = byid_.find(*name);
                        if (it == byid_.end()) {
                            Logger::Error("Instance reference #" + std::to_string(*name) + " used by instance #" + std::to_string(ref) + " at attribute index " + std::to_string(refattr) + " not found at offset " + std::to_string(name->file_offset));
                        } else {
                            inner.push_back(express::Base(it->second));
                        }
                    } else if (auto* inst = std::get_if<express::Base>(&vii)) {
                        inner.push_back(*inst);
                    }
                }
            }

            auto& storage = byid_[p.first.name_];
            auto attr_index = p.first.index_;
            
            if (storage->has_attribute_value<express::Base>(attr_index)) {
                express::Base inst = storage->get_attribute_value(attr_index);
                if (!inst.declaration().as_entity()) {
                    // Probably a case of IfcPropertySetDefinitionSet, divert storage of reference to the simply type instance
                    storage = inst.data_weak().lock();
                    attr_index = 0;
                }
            }

            if (storage->has_attribute_value<Blank>(attr_index)) {
                storage->set_attribute_value(attr_index, instances);
            } else {
                Logger::Error("Duplicate definition for instance reference");
            }
        }
    }

    Logger::Status("Done resolving references");
}

void IfcFile::recalculate_id_counter() {
    /*
    // @todo
    entity_by_id_t::key_type k = 0;
    for (auto& p : byid_) {
        if (p.first > k) {
            k = p.first;
        }
    }
    max_id_ = (unsigned int)k;
    */
}

class traversal_recorder {
    std::vector<express::Base> list_;
    std::map<int, std::vector<express::Base>> instances_by_level_;
    int mode_;

  public:
    traversal_recorder(int mode) : mode_(mode) {
    };

    void push_back(int level, const express::Base& instance) {
        if (mode_ == 0) {
            list_.push_back(instance);
        } else {
            auto& l = instances_by_level_[level];
            l.push_back(instance);
        }
    }

    std::vector<express::Base> get_list() const {
        if (mode_ == 0) {
            return list_;
        }
        std::vector<express::Base> l;
        for (const auto& p : instances_by_level_) {
            l.insert(l.end(), p.second.begin(), p.second.end());
        }
        return l;
    }
};

class traversal_visitor {
  private:
    std::set<express::Base>& visited_;
    traversal_recorder& list_;
    int level_;
    int max_level_;

  public:
    traversal_visitor(std::set<express::Base>& visited, traversal_recorder& list, int level, int max_level)
        : visited_(visited),
          list_(list),
          level_(level),
          max_level_(max_level) {}

    void operator()(const express::Base& inst, int index);
};

void traverse_(const express::Base& instance, std::set<express::Base>& visited, traversal_recorder& list, int level, int max_level) {
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

void traversal_visitor::operator()(const express::Base& inst, int /* index */) {
    traverse_(inst, visited_, list_, level_, max_level_);
}

std::vector<express::Base> IfcParse::traverse(const express::Base& instance, int max_level) {
    std::set<express::Base> visited;
    traversal_recorder recorder(0);
    traverse_(instance, visited, recorder, 0, max_level);
    return recorder.get_list();
}

// I'm cheating this isn't breadth-first, but rather we record visited instances
// keeping track of their rank and return a list ordered by rank. Is this equivalent?
std::vector<express::Base> IfcParse::traverse_breadth_first(const express::Base& instance, int max_level) {
    std::set<express::Base> visited;
    traversal_recorder recorder(1);
    traverse_(instance, visited, recorder, 0, max_level);
    return recorder.get_list();
}

/// @note: for backwards compatibility
std::vector<express::Base> IfcFile::traverse(const express::Base& instance, int max_level) {
    return IfcParse::traverse(instance, max_level);
}

/// @note: for backwards compatibility
std::vector<express::Base> IfcFile::traverse_breadth_first(const express::Base& instance, int max_level) {
    return IfcParse::traverse_breadth_first(instance, max_level);
}

express::Base IfcFile::addEntity(const express::Base& entity) {
    if (entity.data()->file() == this) {
        return entity;
    }

    if (entity.declaration().schema() != schema()) {
        throw IfcParse::IfcException("Unabled to add instance from " + entity.declaration().schema()->name() + " schema to file with " + schema()->name() + " schema");
    }

    // If this instance has been inserted before, return
    // a reference to the copy that was created from it.
    entity_entity_map_t::iterator mit = entity_file_map_.find(entity.identity());
    if (mit != entity_file_map_.end()) {
        return mit->second;
    }

    express::Base new_entity;

    // Obtain all forward references by a depth-first
    // traversal and add them to the file.
    try {
        auto entity_attributes = traverse(entity, 1);
        for (auto it = entity_attributes.begin() + 1; it != entity_attributes.end(); ++it) {
            if (*it != entity) {
                entity_entity_map_t::iterator mit2 = entity_file_map_.find(it->identity());
                if (mit2 == entity_file_map_.end()) {
                    entity_file_map_.insert(entity_entity_map_t::value_type(it->identity(), addEntity(*it)));
                }
            }
        }
    } catch (...) {
        Logger::Message(Logger::LOG_ERROR, "Failed to visit forward references of", entity);
    }

    // An instance is being added from another file. A copy of the
    // container and entity is created. The attribute references
    // need to be updated to point to instances in this file.
    IfcFile* other_file = entity.data()->file();
    create(&entity.declaration());
    auto* decl = &entity.declaration();

    auto num_attributes = (decl->as_entity() ? decl->as_entity()->attribute_count() : 1);
    for (size_t i = 0; i < num_attributes; ++i) {
        entity.data()->apply_visitor([this, i, decl, &new_entity](const auto& v) {
            using U = std::decay_t<decltype(v)>;
            // only need to copy non-instance attribute values, others are assigned below after mapping
            if constexpr (std::is_same_v<U, express::Base>) {
            } else if constexpr (std::is_same_v<U, std::vector<express::Base>>) {
            } else if constexpr (std::is_same_v<U, std::vector<std::vector<express::Base>>>) {
            } else {
                new_entity.set_attribute_value(i, v);
            }
        }, i);
    }
        
    // In case an entity is added that contains geometry, the unit
    // information needs to be accounted for for IfcLengthMeasures.
    double conversion_factor = calculate_unit_factors ? std::numeric_limits<double>::quiet_NaN() : 1.0;

    for (size_t i = 0; i < num_attributes; ++i) {
        // old attribute value
        auto attr = entity.get_attribute_value(i);
        IfcUtil::ArgumentType attr_type = attr.type();

        IfcParse::declaration* potentially_length_measure_decl = 0;
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

        if (attr_type == IfcUtil::Argument_ENTITY_INSTANCE) {
            entity_entity_map_t::const_iterator eit = entity_file_map_.find(((express::Base)(attr)).identity());
            if (eit == entity_file_map_.end()) {
                throw IfcParse::IfcException("Unable to map instance to file");
            }
            // @todo previously, we directly use storage::set() not to trigger inverse recalculation which happens at the end
            new_entity.set_attribute_value(i, eit->second);
        } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
            std::vector<express::Base> instances = attr;
            std::vector<express::Base> new_instances;
            for (auto& i : instances) {
                entity_entity_map_t::const_iterator eit = entity_file_map_.find(i.identity());
                if (eit == entity_file_map_.end()) {
                    throw IfcParse::IfcException("Unable to map instance to file");
                }
                new_instances.push_back(eit->second);
            }
            new_entity.set_attribute_value(i, new_instances);
        } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
            std::vector<std::vector<express::Base>> instances = attr;
            std::vector<std::vector<express::Base>> new_instances;

            for (auto& v : instances) {
                new_instances.emplace_back();
                for (auto& i : v) {
                    entity_entity_map_t::const_iterator eit = entity_file_map_.find(i.identity());
                    if (eit == entity_file_map_.end()) {
                        throw IfcParse::IfcException("Unable to map instance to file");
                    }
                    new_instances.back().push_back(eit->second);
                }
            }
                
            new_entity.set_attribute_value(i, new_instances);
        } else if ((potentially_length_measure_decl != nullptr) && potentially_length_measure_decl->is(*schema()->declaration_by_name("IfcLengthMeasure"))) {
            if (boost::math::isnan(conversion_factor)) {
                std::pair<express::Base, double> this_file_unit = {express::Base{}, 1.0};
                std::pair<express::Base, double> other_file_unit = {express::Base{}, 1.0};
                try {
                    this_file_unit = getUnit("LENGTHUNIT");
                    other_file_unit = other_file->getUnit("LENGTHUNIT");
                } catch (IfcParse::IfcException&) {
                }
                if (this_file_unit.first && other_file_unit.first) {
                    conversion_factor = other_file_unit.second / this_file_unit.second;
                } else {
                    conversion_factor = 1.;
                }
            }
            if (attr_type == IfcUtil::Argument_DOUBLE) {
                double v = attr;
                v *= conversion_factor;
                new_entity.set_attribute_value(i, v);
            } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
                std::vector<double> v = attr;
                for (std::vector<double>::iterator it = v.begin(); it != v.end(); ++it) {
                    (*it) *= conversion_factor;
                }
                new_entity.set_attribute_value(i, v);
            } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
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

    entity_file_map_.insert(entity_entity_map_t::value_type(entity.identity(), new_entity));

    // For subtypes of IfcRoot, the GUID mapping needs to be updated.
    if (decl->is(*ifcroot_type_)) {
        try {
            const std::string guid = new_entity.get_attribute_value(0);
            if (byguid_.find(guid) != byguid_.end()) {
                std::stringstream ss;
                ss << "Overwriting entity with guid " << guid;
                Logger::Message(Logger::LOG_WARNING, ss.str());
            }
            byguid_.insert({ guid, new_entity });
        } catch (const std::exception& ex) {
            Logger::Message(Logger::LOG_ERROR, ex.what());
        }
    }

    add_type_ref(new_entity);

    return new_entity;
}

void IfcFile::removeEntity(const express::Base& entity) {
    auto id = entity.id();

    auto file_entity = instance_by_id(id);

    // Attention when running removeEntity inside a loop over a list of entities to be removed.
    // This invalidates the iterator. A workaround is to reverse the loop:
    // boost::shared_ptr<aggregate_of_instance> entities = ...;
    // for (auto it = entities->end() - 1; it >= entities->begin(); --it) {
    //    express::Base *const inst = *it;
    //    model->removeEntity(inst);
    // }

    // TODO: Create a set of weak relations. Inverse relations that do not dictate an
    // instance to be retained. For example: when deleting an IfcRepresentation, the
    // individual IfcRepresentationItems can not be deleted if an IfcStyledItem is
    // related. Hence, the IfcRepresentationItem::StyledByItem relation could be
    // characterized as weak.
    // std::set<IfcSchema::Type::Enum> weak_roots;

    if (entity != file_entity) {
        throw IfcParse::IfcException("Instance not part of this file");
    }

    if (batch_mode_) {
        batch_deletion_ids_.push_back(id);
    } else {
        process_deletion_(entity);
    }
}

void IfcFile::process_deletion_(const express::Base& entity) {

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

                IfcUtil::ArgumentType attr_type = attr.type();
                switch (attr_type) {
                case IfcUtil::Argument_ENTITY_INSTANCE: {
                    express::Base instance_attribute = attr;
                    if (instance_attribute == entity) {
                        related_instance.set_attribute_value(i, Blank{});
                    }
                } break;
                case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
                    std::vector<express::Base> instance_list = attr;
                    auto it = std::remove(instance_list.begin(), instance_list.end(), entity);
                    if (it != instance_list.end()) {
                        instance_list.erase(it, instance_list.end());
                        if (instance_list.empty() && related_instance.declaration().as_entity()->attribute_by_index(i)->optional()) {
                            // @todo we can also check the lower bound of the attribute type before setting to null.
                            related_instance.set_attribute_value(i, Blank{});
                        } else {
                            related_instance.set_attribute_value(i, instance_list);
                        }
                    }
                } break;
                case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
                    std::vector<std::vector<express::Base>> instance_list_list = attr;
                    bool updated = false;
                    for (auto& li : instance_list_list) {
                        auto it = std::remove(li.begin(), li.end(), entity);
                        if (it != li.end()) {
                            li.erase(it, li.end());
                            updated = true;
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
            Logger::Warning("GlobalId on rooted instance not encountered in map");
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

    // This now frees the shared_ptr
    byid_.erase(entity.id());
}

void IfcParse::impl::in_memory_file_storage::process_deletion_inverse(const express::Base& entity) {
    auto id = entity.id();

    // Delete inverses into entity
    byref_excl_.erase(
        byref_excl_.lower_bound({ id, -1, -1 }),
        byref_excl_.upper_bound({ id, std::numeric_limits<short>::max(), std::numeric_limits<short>::max() }));

    // This is based on traversal which needs instances to still be contained in the map.
    // another option would be to keep byid intact for the remainder of this loop
    auto entity_attributes = traverse(entity, 1);
    for (auto it = entity_attributes.begin(); it != entity_attributes.end(); ++it) {
        auto entity_attribute = *it;
        if (entity_attribute == entity) {
            continue;
        }
        const unsigned int name = entity_attribute.id();
        // Do not update inverses for simple types (which have id()==0 in IfcOpenShell).
        if (name != 0) {
            // Find instances entity -> other
            // and update inverses from entity into other
            auto lower = byref_excl_.lower_bound({ name, -1, -1 });
            auto upper = byref_excl_.upper_bound({ name, std::numeric_limits<short>::max(), std::numeric_limits<short>::max() });

            for (auto byref_it = lower; byref_it != upper; ++byref_it) {
                auto& ids = byref_it->second;
                ids.erase(std::remove(ids.begin(), ids.end(), id), ids.end());
            }
        }
    }
}

namespace {
    template <typename Fn>
    void visit_subtypes(const IfcParse::entity* ent, Fn fn) {
        fn(ent);
        for (const auto& st : ent->subtypes()) {
            visit_subtypes(st, fn);
        }
    }

    template <typename Fn>
    void visit_supertypes(const IfcParse::entity* ent, Fn fn) {
        fn(ent);
        if (ent->supertype()) {
            visit_supertypes(ent->supertype(), fn);
        }
    }
}

std::vector<express::Base> IfcFile::instances_by_type(const IfcParse::declaration* t) {
    std::vector<express::Base> insts;
    if (t->as_entity() != nullptr) {
        visit_subtypes(t->as_entity(), [this, &insts](const IfcParse::entity* ent) {
            auto subtype_insts = instances_by_type_excl_subtypes(ent);
            insts.insert(insts.end(), subtype_insts.begin(), subtype_insts.end());
        });
    }
    return insts;
}

std::vector<express::Base> IfcFile::instances_by_type_excl_subtypes(const IfcParse::declaration* t) {
    return std::visit([t](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            auto it = x.bytype_excl_.find(t);
            return (it == x.bytype_excl_.end()) ? std::vector<express::Base>{} : it->second;
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            std::vector<express::Base> ret;
            auto it = x.bytype_.find(t->index_in_schema());
            if (it != x.bytype_.end()) {
                const auto& s = it->second;
                // @todo generalize this, bytype_ should be a map_adapter
                std::vector<size_t> vals(s.size() / sizeof(size_t));
                memcpy(vals.data(), s.data(), s.size());
                for (auto& v : vals) {
                    ret.push_back(x.assert_existance(v, IfcParse::impl::rocks_db_file_storage::entityinstance_ref));
                }
            }
            return ret;
        } else {
            throw std::runtime_error("Storage not initialized");
            std::vector<express::Base> ret;
            return ret;
        }
    }, storage_);
}

std::vector<express::Base> IfcFile::instances_by_type(const std::string& t) {
    return instances_by_type(schema()->declaration_by_name(t));
}

std::vector<express::Base> IfcFile::instances_by_type_excl_subtypes(const std::string& t) {
    return instances_by_type_excl_subtypes(schema()->declaration_by_name(t));
}

std::vector<express::Base> IfcFile::instances_by_reference(int t) {
    std::vector<express::Base> ret;
    std::visit([this, t, &ret](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            auto lower = x.byref_excl_.lower_bound({ t, -1, -1 });
            auto upper = x.byref_excl_.upper_bound({ t, std::numeric_limits<short>::max(), std::numeric_limits<short>::max() });
            for (auto it = lower; it != upper; ++it) {
                for (auto& i : it->second) {
                    ret.push_back(instance_by_id(i));
                }
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

express::Base IfcFile::instance_by_id(int id) {
    return std::visit([id](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
            return express::Base{};
        } else {
            return x.instance_by_id(id);
        }
    }, storage_);
}

void IfcParse::IfcFile::add_type_ref(const express::Base& new_entity)
{
    std::visit([new_entity](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.add_type_ref(new_entity);
        }
    }, storage_);
}


void IfcParse::IfcFile::remove_type_ref(const express::Base& new_entity) {
    std::visit([new_entity](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.remove_type_ref(new_entity);
        }
    }, storage_);
}

void IfcParse::IfcFile::process_deletion_inverse(const express::Base& inst) {
    std::visit([inst](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.process_deletion_inverse(inst);
        }
    }, storage_);
}

express::Base IfcFile::instance_by_guid(const std::string& guid) {
    auto it = byguid_.find(guid);
    if (it == byguid_.end()) {
        throw IfcException("Instance with GlobalId '" + guid + "' not found");
    }
    return it->second;
}

IfcFile::type_iterator IfcFile::types_begin() const {
    return std::visit([](const auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            return IfcFile::type_iterator{ impl::rocks_db_file_storage::rocksdb_types_iterator{} };
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            return IfcFile::type_iterator{ x.bytype_excl_.begin() };
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            return IfcFile::type_iterator{ impl::rocks_db_file_storage::rocksdb_types_iterator(&x) };
        }
    }, storage_);
}

IfcFile::type_iterator IfcFile::types_end() const {
    return std::visit([](const auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            return IfcFile::type_iterator{ impl::rocks_db_file_storage::rocksdb_types_iterator{} };
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            return IfcFile::type_iterator{ x.bytype_excl_.end() };
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            return IfcFile::type_iterator{ impl::rocks_db_file_storage::rocksdb_types_iterator{} };
        }
    }, storage_);
}

std::ostream& operator<<(std::ostream& out, const IfcParse::IfcFile& file) {
    file.header().write(out);

    typedef std::vector<express::Base> vector_t;
    vector_t sorted;
    std::transform(file.begin(), file.end(), std::back_inserter(sorted), [&file](const auto& x) { return x.second; });
    std::sort(sorted.begin(), sorted.end(), [](const auto& a, const auto& b) { return a.id() < b.id(); });

    for (auto& e : sorted) {
        // @todo this check should no longer be necessary?
        if (e.declaration().as_entity() != nullptr) {
            e.toString(out, true);
            out << ";" << std::endl;
        }
    }

    out << "ENDSEC;" << std::endl;
    out << "END-ISO-10303-21;" << std::endl;

    return out;
}

std::string IfcFile::createTimestamp() {
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

const IfcParse::schema_definition* IfcFile::schema() const {
    if (schema_ == nullptr) {
        throw IfcException("No schema loaded");
	}
    return schema_;
}

std::vector<int> IfcFile::get_inverse_indices(int instance_id) {
    std::vector<int> return_value;

    // Mapping of instance id to attribute offset.
    std::map<int, std::vector<int>> mapping;

    std::visit([&mapping, instance_id](const auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            auto lower = x.byref_excl_.lower_bound({ instance_id, -1, -1 });
            auto upper = x.byref_excl_.upper_bound({ instance_id, std::numeric_limits<short>::max(), std::numeric_limits<short>::max() });
            for (auto it = lower; it != upper; ++it) {
                for (auto& i : it->second) {
                    mapping[i].push_back(std::get<2>(it->first));
                }
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

    auto refs = instances_by_reference(instance_id);

    for (const auto& ref : refs) {
        auto it = mapping.find(ref.id());
        if (it == mapping.end() || it->second.empty()) {
            throw IfcException("Internal error");
        }
        return_value.push_back(it->second.front());
        it->second.erase(it->second.begin());
        if (it->second.empty()) {
            mapping.erase(it);
        }
    }

    // Test whether all mappings where indeed used.
    if (!mapping.empty()) {
        throw IfcException("Internal error");
    }

    return return_value;
}

std::vector<express::Entity> IfcFile::getInverse(int instance_id, const IfcParse::declaration* type, int attribute_index) {
    std::vector<express::Entity> return_value;
    
    if (type == nullptr && attribute_index == -1) {
        // @todo this is silly.
        auto r = instances_by_reference(instance_id);
        for (auto& i : r) {
            return_value.push_back(i.as<express::Entity>());
        }
        return return_value;
    }
    
    visit_subtypes(type->as_entity(), [this, attribute_index, instance_id, &return_value](const IfcParse::declaration* ent) {

        std::visit([&return_value, this, attribute_index, instance_id, ent](const auto& x) {
            if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
                if (attribute_index == -1) {
                    auto lower = x.byref_excl_.lower_bound({ instance_id, ent->index_in_schema(), -1 });
                    auto upper = x.byref_excl_.upper_bound({ instance_id, ent->index_in_schema(), std::numeric_limits<short>::max() });

                    for (auto it = lower; it != upper; ++it) {
                        for (auto& i : it->second) {
                            return_value.push_back(instance_by_id(i).template as<express::Entity>());
                        }
                    }
                } else {
                    auto it = x.byref_excl_.find({ instance_id, ent->index_in_schema(), attribute_index });
                    if (it != x.byref_excl_.end()) {
                        for (auto& i : it->second) {
                            return_value.push_back(instance_by_id(i).template as<express::Entity>());
                        }
                    }
                }
            }
#ifdef IFOPSH_WITH_ROCKSDB            
            else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
                if (attribute_index == -1) {
                    // @todo no lower/upper_bounds() implemented yet
                    auto prefix = "v|" + std::to_string(instance_id) + "|" + std::to_string(ent->index_in_schema()) + "|";
                    auto it = std::unique_ptr<rocksdb::Iterator>(x.db->NewIterator(rocksdb::ReadOptions()));
                    it->Seek(prefix);
                    while (it->Valid() && it->key().starts_with(prefix)) {
                        std::vector<uint32_t> vals(it->value().size() / sizeof(uint32_t));
                        memcpy(vals.data(), it->value().data(), it->value().size());
                        for (auto& v : vals) {
                            return_value.push_back(instance_by_id(v).as<express::Entity>());
                        }
                        it->Next();
                    }
                } else {
                    auto it = x.byref_excl_.find({ instance_id, ent->index_in_schema(), attribute_index });
                    if (it != x.byref_excl_.end()) {
                        for (auto& i : it->second) {
                            return_value.push_back(instance_by_id(i).as<express::Entity>());
                        }
                    }
                }
            }
#endif
        }, storage_);
    });

    return return_value;
}

size_t IfcFile::getTotalInverses(int instance_id) {
    size_t n = 0;

    std::visit([&n, instance_id](const auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
            auto lower = x.byref_excl_.lower_bound({ instance_id, -1, -1 });
            auto upper = x.byref_excl_.upper_bound({ instance_id, std::numeric_limits<short>::max(), std::numeric_limits<short>::max() });
            for (auto it = lower; it != upper; ++it) {
                n += it->second.size();
            }
        } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            // @todo
        }
    }, storage_);

    return n;
}

void IfcFile::setDefaultHeaderValues() {
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
    header().file_name().settime_stamp(createTimestamp());
    header().file_name().setauthor(string_vector);
    header().file_name().setorganization(string_vector);
    header().file_name().setpreprocessor_version("IfcOpenShell " + std::string(IFCOPENSHELL_VERSION));
    header().file_name().setoriginating_system("IfcOpenShell " + std::string(IFCOPENSHELL_VERSION));
    header().file_name().setauthorization(empty_string);

    header().file_schema().setschema_identifiers(schema_identifiers);
}

std::pair<express::Base, double> IfcFile::getUnit(const std::string& unit_type) {
    std::pair<express::Base, double> return_value(express::Base{}, 1.);

    auto projects = instances_by_type(schema()->declaration_by_name("IfcProject"));
    if (projects.empty()) {
        try {
            projects = instances_by_type(schema()->declaration_by_name("IfcContext"));
        } catch (IfcException&) {
        }
    }

    if (!projects.empty()) {
        auto project = *projects.begin();

        express::Base unit_assignment = project.as<express::Entity>().get("UnitsInContext");

        std::vector<express::Base> units = unit_assignment.as<express::Entity>().get("Units");

        for (auto& unit : units) {
            if (unit.declaration().is("IfcNamedUnit")) {
                const std::string file_unit_type = unit.as<express::Entity>().get("UnitType");

                if (file_unit_type != unit_type) {
                    continue;
                }

                express::Base siunit;
                if (unit.declaration().is("IfcConversionBasedUnit")) {
                    express::Base mu = unit.as<express::Entity>().get("ConversionFactor");
                    express::Base vlc = mu.as<express::Entity>().get("ValueComponent");
                    express::Base unc = mu.as<express::Entity>().get("UnitComponent");
                    return_value.second *= static_cast<double>(vlc.get_attribute_value(0));
                    return_value.first = unit;

                    if (unc.declaration().is("IfcSIUnit")) {
                        siunit = unc;
                    }

                } else if (unit.declaration().is("IfcSIUnit")) {
                    return_value.first = siunit = unit;
                }

                if (siunit) {
                    AttributeValue prefix = siunit.as<express::Entity>().get("Prefix");
                    if (!prefix.isNull()) {
                        return_value.second *= IfcSIPrefixToValue(prefix);
                    }
                }
            }
        }
    }

    return return_value;
}

void IfcParse::IfcFile::build_inverses_(const express::Base& inst) {
    std::function<void(const express::Base&, int)> fn = [this, inst](const express::Base& attr, int idx) {
        if (attr.declaration().as_entity() != nullptr) {
            unsigned entity_attribute_id = attr.id();
            const auto* decl = inst.declaration().as_entity();

            std::visit([entity_attribute_id, decl, idx, inst](auto& x) {
                if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
                } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::in_memory_file_storage>) {
                    x.byref_excl_[{entity_attribute_id, decl->index_in_schema(), idx}].push_back(inst.id());
                } else if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
                    // @todo
                }
            }, storage_);
        }
    };

    apply_individual_instance_visitor(inst).apply(fn);
}

void IfcParse::IfcFile::unbatch() {
    for (auto& id : batch_deletion_ids_) {
        process_deletion_(instance_by_id(id));
    }
    batch_mode_ = false;
    batch_deletion_ids_.clear();
}

void IfcParse::IfcFile::reset_identity_cache() {
    std::visit([](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, impl::rocks_db_file_storage>) {
            x.instance_cache_.clear();
            x.type_instance_cache_.clear();
        }
	}, storage_);
}

void IfcParse::IfcFile::build_inverses() {
    for (const auto& pair : *this) {
        build_inverses_(express::Base(pair.second));
    }
}

void IfcParse::IfcFile::register_inverse(unsigned id_from, const IfcParse::entity* from_entity, int inst_id, int attribute_index)
{
    std::visit([id_from, from_entity, inst_id, attribute_index](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.register_inverse(id_from, from_entity, inst_id, attribute_index);
        }
    }, storage_);
}

void IfcParse::IfcFile::unregister_inverse(unsigned id_from, const IfcParse::entity* from_entity, const express::Base& inst, int attribute_index)
{
    std::visit([id_from, from_entity, inst, attribute_index](auto& x) {
        if constexpr (std::is_same_v<std::decay_t<decltype(x)>, std::monostate>) {
            throw std::runtime_error("Storage not initialized");
        } else {
            return x.unregister_inverse(id_from, from_entity, inst, attribute_index);
        }
    }, storage_);
}

std::atomic_uint32_t InstanceData::counter_(0);

// bool IfcParse::IfcFile::guid_map_ = true;

void express::Base::unset_attribute_value(size_t index) {
    data()->set_attribute_value(index, Blank{});
}

AttributeValue express::Base::get_attribute_value(size_t index) const {
    return data()->get_attribute_value(index);
}

void express::Base::toString(std::ostream& out, bool upper) const
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
    data()->toString(out, upper);
}

/*
InstanceData::InstanceData(const InstanceData& data)
    : storage_(data.size())
{
    
}
*/

AttributeValue InstanceData::get_attribute_value(size_t index) const
{
    if (storage_) {
        return AttributeValue(storage_, (uint8_t)index);
    } else {
        auto* const storage = std::visit([](auto& m) -> IfcParse::impl::rocks_db_file_storage* {
            using U = std::decay_t<decltype(m)>;
            if constexpr (std::is_same_v<U, IfcParse::impl::rocks_db_file_storage>) {
                return &m;
            } else {
                return nullptr;
            }
        }, file_->storage_);
        return AttributeValue(storage, identity_, declaration_, (uint8_t) index);
    }
}

bool IfcParse::impl::rocks_db_file_storage::read_schema(const IfcParse::schema_definition*& schema) {
#ifdef IFOPSH_WITH_ROCKSDB
    std::string value;
    auto key = "h|file_schema|0";
    db->Get(rocksdb::ReadOptions{}, key, &value);
    std::vector<std::string> strings;
    if (::impl::deserialize(this, value, strings) && strings.size() == 1) {
        try {
            schema = schema_by_name(strings[0]);
        } catch (IfcException&) {
            return false;
		}
        return true;
    }
#endif
    return false;    
}

    /*
express::Base::IfcBaseClass(InstanceData&& data)
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

void express::Base::set_attribute_value(size_t i, const express::Base& p) {
    set_attribute_value<express::Base>(i, p);
}
void express::Base::set_attribute_value(const std::string& name, const express::Base& p) {
    set_attribute_value<express::Base>(name, p);
}

template void IFC_PARSE_API express::Base::set_attribute_value<Blank>(size_t index, const Blank& value);
template void IFC_PARSE_API express::Base::set_attribute_value<Derived>(size_t index, const Derived& value);
template void IFC_PARSE_API express::Base::set_attribute_value<int>(size_t index, const int& value);
template void IFC_PARSE_API express::Base::set_attribute_value<bool>(size_t index, const bool& value);
template void IFC_PARSE_API express::Base::set_attribute_value<boost::logic::tribool>(size_t index, const boost::logic::tribool& value);
template void IFC_PARSE_API express::Base::set_attribute_value<double>(size_t index, const double& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::string>(size_t index, const std::string& value);
template void IFC_PARSE_API express::Base::set_attribute_value<boost::dynamic_bitset<>>(size_t index, const boost::dynamic_bitset<>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<EnumerationReference>(size_t index, const EnumerationReference& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<int>>(size_t index, const std::vector<int>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<double>>(size_t index, const std::vector<double>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<std::string>>(size_t index, const std::vector<std::string>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<boost::dynamic_bitset<>>>(size_t index, const std::vector<boost::dynamic_bitset<>>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<express::Base>>(size_t index, const std::vector<express::Base>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<std::vector<int>>>(size_t index, const std::vector<std::vector<int>>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<std::vector<double>>>(size_t index, const std::vector<std::vector<double>>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<std::vector<express::Base>>>(size_t index, const std::vector<std::vector<express::Base>>& value);

template void IFC_PARSE_API express::Base::set_attribute_value<Blank>(const std::string& name, const Blank& value);
template void IFC_PARSE_API express::Base::set_attribute_value<Derived>(const std::string& name, const Derived& value);
template void IFC_PARSE_API express::Base::set_attribute_value<int>(const std::string& name, const int& value);
template void IFC_PARSE_API express::Base::set_attribute_value<bool>(const std::string& name, const bool& value);
template void IFC_PARSE_API express::Base::set_attribute_value<boost::logic::tribool>(const std::string& name, const boost::logic::tribool& value);
template void IFC_PARSE_API express::Base::set_attribute_value<double>(const std::string& name, const double& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::string>(const std::string& name, const std::string& value);
template void IFC_PARSE_API express::Base::set_attribute_value<boost::dynamic_bitset<>>(const std::string& name, const boost::dynamic_bitset<>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<EnumerationReference>(const std::string& name, const EnumerationReference& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<int>>(const std::string& name, const std::vector<int>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<double>>(const std::string& name, const std::vector<double>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<std::string>>(const std::string& name, const std::vector<std::string>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<boost::dynamic_bitset<>>>(const std::string& name, const std::vector<boost::dynamic_bitset<>>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<express::Base>>(const std::string& name, const std::vector<express::Base>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<std::vector<int>>>(const std::string& name, const std::vector<std::vector<int>>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<std::vector<double>>>(const std::string& name, const std::vector<std::vector<double>>& value);
template void IFC_PARSE_API express::Base::set_attribute_value<std::vector<std::vector<express::Base>>>(const std::string& name, const std::vector<std::vector<express::Base>>& value);

namespace express {
template <typename T>
T Entity::get_value(const std::string& name) const {
    auto attr = get(name);
    T v = attr;
    return v;
}

template <typename T>
T Entity::get_value(const std::string& name, const T& default_value) const {
    auto attr = get(name);
    if (attr.isNull()) {
        return default_value;
    }
    T v = attr;
    return v;
}
} // namespace express

template int IFC_PARSE_API express::Entity::get_value<int>(const std::string&) const;
template bool IFC_PARSE_API express::Entity::get_value<bool>(const std::string&) const;
template boost::logic::tribool IFC_PARSE_API express::Entity::get_value<boost::logic::tribool>(const std::string&) const;
template double IFC_PARSE_API express::Entity::get_value<double>(const std::string&) const;
template std::string IFC_PARSE_API express::Entity::get_value<std::string>(const std::string&) const;
template express::Base IFC_PARSE_API express::Entity::get_value<express::Base>(const std::string&) const;
template boost::dynamic_bitset<> IFC_PARSE_API express::Entity::get_value<boost::dynamic_bitset<>>(const std::string&) const;
template EnumerationReference IFC_PARSE_API express::Entity::get_value<EnumerationReference>(const std::string&) const;
template std::vector<int> IFC_PARSE_API express::Entity::get_value<std::vector<int>>(const std::string&) const;
template std::vector<double> IFC_PARSE_API express::Entity::get_value<std::vector<double>>(const std::string&) const;
template std::vector<std::string> IFC_PARSE_API express::Entity::get_value<std::vector<std::string>>(const std::string&) const;
template std::vector<boost::dynamic_bitset<>> IFC_PARSE_API express::Entity::get_value<std::vector<boost::dynamic_bitset<>>>(const std::string&) const;
template std::vector<express::Base> IFC_PARSE_API express::Entity::get_value<std::vector<express::Base>>(const std::string&) const;
template std::vector<std::vector<int>> IFC_PARSE_API express::Entity::get_value<std::vector<std::vector<int>>>(const std::string&) const;
template std::vector<std::vector<double>> IFC_PARSE_API express::Entity::get_value<std::vector<std::vector<double>>>(const std::string&) const;
template std::vector<std::vector<express::Base>> IFC_PARSE_API express::Entity::get_value<std::vector<std::vector<express::Base>>>(const std::string&) const;

template int IFC_PARSE_API express::Entity::get_value<int>(const std::string&, const int&) const;
template bool IFC_PARSE_API express::Entity::get_value<bool>(const std::string&, const bool&) const;
template boost::logic::tribool IFC_PARSE_API express::Entity::get_value<boost::logic::tribool>(const std::string&, const boost::logic::tribool&) const;
template double IFC_PARSE_API express::Entity::get_value<double>(const std::string&, const double&) const;
template std::string IFC_PARSE_API express::Entity::get_value<std::string>(const std::string&, const std::string&) const;
template express::Base IFC_PARSE_API express::Entity::get_value<express::Base>(const std::string&, const express::Base&) const;
template boost::dynamic_bitset<> IFC_PARSE_API express::Entity::get_value<boost::dynamic_bitset<>>(const std::string&, const boost::dynamic_bitset<>&) const;
template EnumerationReference IFC_PARSE_API express::Entity::get_value<EnumerationReference>(const std::string&, const EnumerationReference&) const;
template std::vector<int> IFC_PARSE_API express::Entity::get_value<std::vector<int>>(const std::string&, const std::vector<int>&) const;
template std::vector<double> IFC_PARSE_API express::Entity::get_value<std::vector<double>>(const std::string&, const std::vector<double>&) const;
template std::vector<std::string> IFC_PARSE_API express::Entity::get_value<std::vector<std::string>>(const std::string&, const std::vector<std::string>&) const;
template std::vector<boost::dynamic_bitset<>> IFC_PARSE_API express::Entity::get_value<std::vector<boost::dynamic_bitset<>>>(const std::string&, const std::vector<boost::dynamic_bitset<>>&) const;
template std::vector<express::Base> IFC_PARSE_API express::Entity::get_value<std::vector<express::Base>>(const std::string&, const std::vector<express::Base>&) const;
template std::vector<std::vector<int>> IFC_PARSE_API express::Entity::get_value<std::vector<std::vector<int>>>(const std::string&, const std::vector<std::vector<int>>&) const;
template std::vector<std::vector<double>> IFC_PARSE_API express::Entity::get_value<std::vector<std::vector<double>>>(const std::string&, const std::vector<std::vector<double>>&) const;
template std::vector<std::vector<express::Base>> IFC_PARSE_API express::Entity::get_value<std::vector<std::vector<express::Base>>>(const std::string&, const std::vector<std::vector<express::Base>>&) const;
