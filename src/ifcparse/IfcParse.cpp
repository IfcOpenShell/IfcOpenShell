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

#include "IfcBaseClass.h"
#include "IfcCharacterDecoder.h"
#include "IfcException.h"
#include "IfcFile.h"
#include "IfcLogger.h"
#include "IfcSchema.h"
#include "IfcSIPrefix.h"
#include "IfcSpfStream.h"
#include "utils.h"

#include <algorithm>
#include <boost/algorithm/string.hpp>
#include <boost/circular_buffer.hpp>
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

//
// Opens the file and gets the filesize
//
#ifdef USE_MMAP
IfcSpfStream::IfcSpfStream(const std::string& path, bool mmap)
#else
IfcSpfStream::IfcSpfStream(const std::string& path)
#endif
    : stream_(0),
      buffer_(0),
      valid(false),
      eof(false) {
#ifdef _MSC_VER
    std::wstring fn_ws = IfcUtil::path::from_utf8(path);
    const wchar_t* fn_wide = fn_ws.c_str();

#ifdef USE_MMAP
    if (mmap) {
        mfs = boost::iostreams::mapped_file_source(boost::filesystem::wpath(fn_wide));
    } else {
#endif
        stream_ = _wfopen(fn_wide, L"rb");
#ifdef USE_MMAP
    }
#endif

#else

#ifdef USE_MMAP
    if (mmap) {
        mfs = boost::iostreams::mapped_file_source(path);
    } else {
#endif
        stream_ = fopen(path.c_str(), "rb");
#ifdef USE_MMAP
    }
#endif

#endif

#ifdef USE_MMAP
    if (mmap) {
        if (!mfs.is_open()) {
            return;
        }

        valid = true;
        buffer_ = mfs.data();
        ptr_ = 0;
        len_ = mfs.size();
    } else {
#endif
        if (stream_ == NULL) {
            return;
        }

        valid = true;
        fseek(stream_, 0, SEEK_END);
        size = (unsigned int)ftell(stream_);
        rewind(stream_);
        char* buffer_rw = new char[size];
        len_ = (unsigned int)fread(buffer_rw, 1, size, stream_);
        buffer_ = buffer_rw;
        eof = len_ == 0;
        ptr_ = 0;
        fclose(stream_);
        stream_ = nullptr;
#ifdef USE_MMAP
    }
#endif
}

IfcSpfStream::IfcSpfStream(std::istream& stream, int length)
    : stream_(0),
      buffer_(0) {
    eof = false;
    size = length;
    char* buffer_rw = new char[size];
    stream.read(buffer_rw, size);
    buffer_ = buffer_rw;
    valid = stream.gcount() == size;
    ptr_ = 0;
    len_ = length;
}

IfcSpfStream::IfcSpfStream(void* data, int length)
    : stream_(0),
      buffer_(0) {
    eof = false;
    size = length;
    buffer_ = (char*)data;
    valid = true;
    ptr_ = 0;
    len_ = length;
}

IfcSpfStream::~IfcSpfStream() {
    Close();
}

void IfcSpfStream::Close() {
#ifdef USE_MMAP
    if (mfs.is_open()) {
        mfs.close();
        return;
    }
#endif
    delete[] buffer_;
    if (stream_ != nullptr) {
        fclose(stream_);
    }
}

//
// Seeks an arbitrary position in the file
//
void IfcSpfStream::Seek(unsigned int offset) {
    ptr_ = offset;
    if (ptr_ >= len_) {
        throw IfcException("Reading outside of file limits");
    }
    eof = false;
}

//
// Returns the character at the cursor
//
char IfcSpfStream::Peek() {
    return buffer_[ptr_];
}

//
// Returns the character at specified offset
//
char IfcSpfStream::Read(unsigned int offset) {
    return buffer_[offset];
}

//
// Returns the cursor position
//
unsigned int IfcSpfStream::Tell() const {
    return ptr_;
}

//
// Increments cursor and reads new chunk if necessary
//
void IfcSpfStream::Inc() {
    if (++ptr_ == len_) {
        eof = true;
        return;
    }
    const char current = IfcSpfStream::Peek();
    if (current == '\n' || current == '\r') {
        // NB this is recursive. It might as well be a loop.
        IfcSpfStream::Inc();
    }
}

IfcSpfLexer::IfcSpfLexer(IfcParse::IfcSpfStream* stream_, IfcParse::IfcFile* file_) {
    file = file_;
    stream = stream_;
    decoder_ = new IfcCharacterDecoder(stream_);
}

IfcSpfLexer::~IfcSpfLexer() {
    delete decoder_;
}

unsigned int IfcSpfLexer::skipWhitespace() const {
    unsigned int index = 0;
    while (!stream->eof) {
        char character = stream->Peek();
        if ((character == ' ' || character == '\r' || character == '\n' || character == '\t')) {
            stream->Inc();
            ++index;
        } else {
            break;
        }
    }
    return index;
}

unsigned int IfcSpfLexer::skipComment() const {
    char character = stream->Peek();
    if (character != '/') {
        return 0;
    }
    stream->Inc();
    character = stream->Peek();
    if (character != '*') {
        stream->Seek(stream->Tell() - 1);
        return 0;
    }
    unsigned int index = 2;
    char intermediate = 0;
    while (!stream->eof) {
        character = stream->Peek();
        stream->Inc();
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

    if (stream->eof) {
        return NoneTokenPtr();
    }

    while ((skipWhitespace() != 0U) || (skipComment() != 0U)) {
    }

    if (stream->eof) {
        return NoneTokenPtr();
    }
    unsigned int pos = stream->Tell();

    char character = stream->Peek();

    // If the cursor is at [()=,;$*] we know token consists of single char
    if (character == '(' ||
        character == ')' ||
        character == '=' ||
        character == ',' ||
        character == ';' ||
        character == '$' ||
        character == '*') {
        stream->Inc();
        return OperatorTokenPtr(this, pos, pos + 1);
    }

    int len = 0;

    while (!stream->eof) {

        // Read character and increment pointer if not starting a new token
        character = stream->Peek();
        if ((len != 0) && (character == '(' ||
                           character == ')' ||
                           character == '=' ||
                           character == ',' ||
                           character == ';' ||
                           character == '/')) {
            break;
        }
        stream->Inc();
        len++;

        // If a string is encountered defer processing to the IfcCharacterDecoder
        if (character == '\'') {
            decoder_->skip();
        }
    }
    Token t;
    if (len != 0) {
        t = GeneralTokenPtr(this, pos, stream->Tell());
    } else {
        t = NoneTokenPtr();
    }
    // std::wcout << "token: " << pos << " " << TokenFunc::asStringRef(t).c_str() << std::endl;
    return t;
}

bool IfcSpfStream::is_eof_at(unsigned int local_ptr) const {
    return local_ptr >= len_;
}

void IfcSpfStream::increment_at(unsigned int& local_ptr) {
    if (++local_ptr == len_) {
        return;
    }
    const char current = IfcSpfStream::peek_at(local_ptr);
    if (current == '\n' || current == '\r') {
        IfcSpfStream::increment_at(local_ptr);
    }
}

char IfcSpfStream::peek_at(unsigned int local_ptr) {
    return buffer_[local_ptr];
}

//
// Reads a std::string from the file at specified offset
// Omits whitespace and comments
//
void IfcSpfLexer::TokenString(unsigned int offset, std::string& buffer) {
    buffer.clear();
    while (!stream->is_eof_at(offset)) {
        char character = stream->peek_at(offset);
        if (!buffer.empty() && (character == '(' ||
                                character == ')' ||
                                character == '=' ||
                                character == ',' ||
                                character == ';' ||
                                character == '/')) {
            break;
        }
        stream->increment_at(offset);
        if (character == ' ' ||
            character == '\r' ||
            character == '\n' ||
            character == '\t') {
            continue;
        }
        if (character == '\'') {
            // todo, make decoder use local offset ptr
            buffer = decoder_->get(offset);
            break;
        }
        buffer.push_back(character);
    }
}

//Note: according to STEP standard, there may be newlines in tokens
inline void RemoveTokenSeparators(IfcSpfStream* stream, unsigned start, unsigned end, std::string& oDestination) {
    oDestination.clear();
    for (unsigned i = start; i < end; i++) {
        char character = stream->Read(i);
        if (character == ' ' ||
            character == '\r' ||
            character == '\n' ||
            character == '\t') {
            continue;
        }
        oDestination += character;
    }
}

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

Token IfcParse::OperatorTokenPtr(IfcSpfLexer* lexer, unsigned start, unsigned end) {
    char first = lexer->stream->Read(start);
    Token token(lexer, start, end, Token_OPERATOR);
    token.value_char = first;
    return token;
}

Token IfcParse::GeneralTokenPtr(IfcSpfLexer* lexer, unsigned start, unsigned end) {
    Token token(lexer, start, end, Token_NONE);

    //extract token into temp buffer (remove eol-s, no encoding changes)
    std::string& tokenStr = lexer->GetTempString();
    RemoveTokenSeparators(lexer->stream, start, end, tokenStr);

    //determine type of the token
    char first = lexer->stream->Read(start);
    if (first == '#') {
        token.type = Token_IDENTIFIER;
        if (!ParseInt(tokenStr.c_str() + 1, token.value_int)) {
            throw IfcException("Identifier token as not integer");
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
Token IfcParse::NoneTokenPtr() { return Token(); }

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
    token.lexer->TokenString(token.startPos, result);
    return result;
}

//
// Reads the arguments from a list of token
// Aditionally, registers the ids (i.e. #[\d]+) in the inverse map
//
void IfcParse::IfcFile::load(unsigned entity_instance_name, const IfcParse::entity* entity, parse_context& context, int attribute_index) {
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
            if (TokenFunc::isIdentifier(next)) {
                register_inverse(entity_instance_name, entity, next, attribute_index == -1 ? attribute_index_within_data : attribute_index);
            }

            if (TokenFunc::isKeyword(next)) {
                try {
                    parse_context ps;
                    tokens->Next();
                    load(0, nullptr, ps, -1);
                    const auto *decl = schema_->declaration_by_name(TokenFunc::asStringRef(next));
                    auto* simple_type_instance = schema_->instantiate(decl, ps.construct(-1, references_to_resolve, decl, boost::none));
                    //@todo decide addEntity(((IfcUtil::IfcBaseClass*)*entity));
                    context.push(simple_type_instance);
                    simple_type_instance->file_ = this;
                } catch (IfcException& e) {
                    Logger::Message(Logger::LOG_ERROR, e.what());
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
IfcEntityInstanceData IfcParse::read(unsigned int i, IfcFile* f) {
    Token datatype = f->tokens->Next();
    if (!TokenFunc::isKeyword(datatype)) {
        throw IfcException("Unexpected token while parsing entity");
    }
    const IfcParse::declaration* ty = f->schema()->declaration_by_name(TokenFunc::asStringRef(datatype));
    parse_context pc;
    f->tokens->Next();
    f->load(i, ty->as_entity(), pc, -1);
    return IfcEntityInstanceData(pc.construct(i, f->references_to_resolve, ty, boost::none));
}

void IfcParse::IfcFile::try_read_semicolon() const {
    unsigned int old_offset = tokens->stream->Tell();
    Token semilocon = tokens->Next();
    if (!TokenFunc::isOperator(semilocon, ';')) {
        tokens->stream->Seek(old_offset);
    }
}

void IfcParse::IfcFile::register_inverse(unsigned id_from, const IfcParse::entity* from_entity, Token t, int attribute_index) {
    // Assume a check on token type has already been performed
    const auto* e = from_entity;
    byref_excl_[{t.value_int, e->index_in_schema(), attribute_index}].push_back(id_from);
}

void IfcParse::IfcFile::register_inverse(unsigned id_from, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass* inst, int attribute_index) {
    const auto* e = from_entity;
    byref_excl_[{inst->id(), e->index_in_schema(), attribute_index}].push_back(id_from);
}

void IfcParse::IfcFile::unregister_inverse(unsigned id_from, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass* inst, int attribute_index) {
    std::vector<int>& ids = byref_excl_[{inst->id(), from_entity->index_in_schema(), attribute_index}];
    std::vector<int>::iterator iter = std::find(ids.begin(), ids.end(), id_from);
    if (iter == ids.end()) {
        // @todo inverses also need to be populated when multiple instances are added to a new file.
        // throw IfcParse::IfcException("Instance not found among inverses");
    } else {
        ids.erase(iter);
    }
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
        void operator()(const IfcUtil::IfcBaseClass* const& i) {
            if (i->declaration().as_entity() == nullptr) {
                i->toString(data_, upper_);
            } else {
                data_ << "#" << i->id();
            }
        }
        void operator()(const aggregate_of_instance::ptr& i) {
            data_ << "(";
            for (aggregate_of_instance::it it = i->begin(); it != i->end(); ++it) {
                if (it != i->begin()) {
                    data_ << ",";
                }
                (*this)(*it);
            }
            data_ << ")";
        }
        void operator()(const std::vector<std::vector<int>>& i);
        void operator()(const std::vector<std::vector<double>>& i);
        void operator()(const aggregate_of_aggregate_of_instance::ptr& i) {
            data_ << "(";
            for (aggregate_of_aggregate_of_instance::outer_it outer_it = i->begin(); outer_it != i->end(); ++outer_it) {
                if (outer_it != i->begin()) {
                    data_ << ",";
                }
                data_ << "(";
                for (aggregate_of_aggregate_of_instance::inner_it inner_it = outer_it->begin(); inner_it != outer_it->end(); ++inner_it) {
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
void IfcEntityInstanceData::toString(std::ostream& ss, bool upper, const entity* decl) const {
    ss.imbue(std::locale::classic());

    ss << "(";

    StringBuilderVisitor vis(ss, upper);

    for (size_t i = 0; i < size(); ++i) {
        if (i != 0) {
            ss << ",";
        }
        if (storage_.has<Blank>(i)) {
            if (decl != nullptr && decl->derived()[i]) {
               ss << "*";
            } else {
               ss << "$";
	        }
        } else {
            storage_.apply_visitor(vis, i);
        }
    }
    ss << ")";
}

unsigned IfcUtil::IfcBaseEntity::set_id(const boost::optional<unsigned>& i) {
    if (i) {
        return id_ = *i;
    }
    return id_ = file_->FreshId();
}

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
    const IfcUtil::IfcBaseClass* data_;

  public:
    unregister_inverse_visitor(IfcFile& file, const IfcUtil::IfcBaseClass* data)
        : file_(file),
          data_(data) {}

    void operator()(IfcUtil::IfcBaseClass* inst, int index) {
        file_.unregister_inverse(data_->id(), data_->declaration().as_entity(), inst, index);
    }
};

class register_inverse_visitor {
  private:
    IfcFile& file_;
    const IfcUtil::IfcBaseClass* data_;

  public:
    register_inverse_visitor(IfcFile& file, const IfcUtil::IfcBaseClass* data)
        : file_(file),
          data_(data) {}

    void operator()(IfcUtil::IfcBaseClass* inst, int index) {
        file_.register_inverse(data_->id(), data_->declaration().as_entity(), inst, index);
    }
};

class add_to_instance_list_visitor {
  private:
    aggregate_of_instance::ptr& list_;

  public:
    add_to_instance_list_visitor(aggregate_of_instance::ptr& list)
        : list_(list) {}

    void operator()(IfcUtil::IfcBaseClass* inst) {
        list_->push(inst);
    }
};

class apply_individual_instance_visitor {
  private:
    boost::optional<AttributeValue> attribute_;
    IfcEntityInstanceData* data_;
    int attribute_index_;

    template <typename T>
    void apply_attribute_(T& t, const AttributeValue& attr, int index) const {
        if (attr.type() == IfcUtil::Argument_ENTITY_INSTANCE) {
            IfcUtil::IfcBaseClass* inst = attr;
            t(inst, index);
        } else if (attr.type() == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
            aggregate_of_instance::ptr entity_list_attribute = attr;
            for (aggregate_of_instance::it it = entity_list_attribute->begin(); it != entity_list_attribute->end(); ++it) {
                t(*it, index);
            }
        } else if (attr.type() == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
            aggregate_of_aggregate_of_instance::ptr entity_list_attribute = attr;
            for (aggregate_of_aggregate_of_instance::outer_it it = entity_list_attribute->begin(); it != entity_list_attribute->end(); ++it) {
                for (aggregate_of_aggregate_of_instance::inner_it jt = it->begin(); jt != it->end(); ++jt) {
                    t(*jt, index);
                }
            }
        }
    };

  public:
    apply_individual_instance_visitor(const AttributeValue& attribute, int idx)
        : attribute_(attribute)
        , attribute_index_(idx)
    {}

    apply_individual_instance_visitor(IfcEntityInstanceData* data)
        : data_(data) 
    {}

    template <typename T>
    void apply(T& t) const {
        if (attribute_) {
            apply_attribute_(t, *attribute_, attribute_index_);
        } else {
            for (size_t i = 0; i < data_->size(); ++i) {
                auto attr = data_->get_attribute_value(i);
                apply_attribute_(t, attr, (int) i);
            }
        }
    };
};

template <typename T>
void IfcUtil::IfcBaseClass::set_attribute_value(size_t i, const T& t) {
    auto current_attribute = data_.get_attribute_value(i);
    if (file_ != nullptr) {

        // Deregister old attribute guid in file guid map.
        if (i == 0 && (file_->ifcroot_type() != nullptr) && this->declaration().is(*file_->ifcroot_type())) {
            try {
                auto guid = (std::string) current_attribute;
                auto it = file_->internal_guid_map().find(guid);
                if (it != file_->internal_guid_map().end() && it->second == this) {
                    file_->internal_guid_map().erase(it);
                }
            } catch (IfcParse::IfcException& e) {
                Logger::Error(e);
            }
        }

        // Deregister inverse indices in file
        unregister_inverse_visitor visitor(*file_, this);
        apply_individual_instance_visitor(current_attribute, (int) i).apply(visitor);
    }

    data_.storage_.set(i, t);
    auto new_attribute = data_.get_attribute_value(i);

    if (file_ != nullptr) {
        // Register inverse indices in file
        register_inverse_visitor visitor(*file_, this);
        apply_individual_instance_visitor(new_attribute, (int) i).apply(visitor);
    
        // Register new attribute guid in guid map
        if (i == 0 && (file_->ifcroot_type() != nullptr) && this->declaration().is(*file_->ifcroot_type())) {
            try {
                auto guid = (std::string) new_attribute;
                auto it = file_->internal_guid_map().find(guid);
                if (it != file_->internal_guid_map().end()) {
                    Logger::Warning("Duplicate guid " + guid);
                }
                file_->internal_guid_map()[guid] = file_->instance_by_id(this->id());
            } catch (IfcParse::IfcException& e) {
                Logger::Error(e);
            }
        }
    }
}

template <typename T>
void IfcUtil::IfcBaseClass::set_attribute_value(const std::string& s, const T& t) {
    set_attribute_value(declaration().as_entity()->attribute_index(s), t);
}

//
// Parses the IFC file in fn
// Creates the maps
//
#ifdef USE_MMAP
IfcFile::IfcFile(const std::string& fn, bool mmap) {
    initialize_(new IfcSpfStream(fn, mmap));
}
#else
IfcFile::IfcFile(const std::string& path) {
    IfcSpfStream s(path);
    initialize_(&s);
}
#endif

IfcFile::IfcFile(std::istream& stream, int length) {
    IfcSpfStream s(stream, length);
    initialize_(&s);
}

IfcFile::IfcFile(void* data, int length) {
    IfcSpfStream s(data, length);
    initialize_(&s);
}

IfcFile::IfcFile(IfcParse::IfcSpfStream* s) {
    initialize_(s);
}

IfcFile::IfcFile(const IfcParse::schema_definition* schema)
    : schema_(schema),
      ifcroot_type_(schema_->declaration_by_name("IfcRoot")),
      MaxId(0),
      tokens(0),
      stream(0) {
    setDefaultHeaderValues();
}

void IfcFile::initialize_(IfcParse::IfcSpfStream* s) {
    // Initialize a "C" locale for locale-independent
    // number parsing. See comment above on line 41.
    init_locale();

    MaxId = 0;
    tokens = 0;
    stream = 0;
    schema_ = 0;

    // setDefaultHeaderValues();

    stream = s;
    if (!stream->valid) {
        good_ = file_open_status::READ_ERROR;
        return;
    }

    tokens = new IfcSpfLexer(stream, this);

    std::vector<std::string> schemas;

    _header.file(this);
    if (_header.tryRead()) {
        try {
            schemas = _header.file_schema().schema_identifiers();
        } catch (...) {
            // Purposely empty catch block
        }
    } else {
        good_ = file_open_status::NO_HEADER;
    }

    if (schemas.size() == 1) {
        try {
            schema_ = IfcParse::schema_by_name(schemas.front());
        } catch (const IfcParse::IfcException& e) {
            good_ = file_open_status::UNSUPPORTED_SCHEMA;
            Logger::Error(e);
        }
    }

    if (schema_ == 0) {
        Logger::Message(Logger::LOG_ERROR, "No support for file schema encountered (" + boost::algorithm::join(schemas, ", ") + ")");
        return;
    }

    ifcroot_type_ = schema_->declaration_by_name("IfcRoot");

    boost::circular_buffer<Token> token_stream(3, Token());

    IfcUtil::IfcBaseClass* instance = nullptr;

    unsigned current_id = 0;
    int progress = 0;
    Logger::Status("Scanning file...");

    int paren_stack_depth = 0;
    int attribute_index = -1;

    while (!stream->eof) {
        if (token_stream[0].type == IfcParse::Token_IDENTIFIER &&
            token_stream[1].type == IfcParse::Token_OPERATOR &&
            token_stream[1].value_char == '=' &&
            token_stream[2].type == IfcParse::Token_KEYWORD) {
            attribute_index = 0;

            current_id = (unsigned)TokenFunc::asIdentifier(token_stream[0]);
            const IfcParse::declaration* entity_type;
            try {
                entity_type = schema_->declaration_by_name(TokenFunc::asStringRef(token_stream[2]));
            } catch (const IfcException& ex) {
                Logger::Message(Logger::LOG_ERROR, std::string(ex.what()) + " at offset " + std::to_string(token_stream[2].startPos));
                goto advance;
            }

            if (entity_type->as_entity() == nullptr) {
                Logger::Message(Logger::LOG_ERROR, "Non entity type " + entity_type->name() + " at offset " + std::to_string(token_stream[2].startPos));
                goto advance;
            }

            parse_context ps;
            tokens->Next();
            load(current_id, entity_type->as_entity(), ps, -1);
            instance = schema_->instantiate(entity_type, ps.construct(current_id, references_to_resolve, entity_type, boost::none));
            instance->file_ = this;
            instance->id_ = current_id;

            /// @todo Printing to stdout in a library class feels weird. Maybe move the progress prints to the client code?
            // Update the status after every 1000 instances parsed
            if (((++progress) % 1000) == 0) {
                std::stringstream ss;
                ss << "\r#" << current_id;
                Logger::Status(ss.str(), false);
            }

            if (instance->declaration().is(*ifcroot_type_)) {
                try {
                    const std::string guid = instance->data().get_attribute_value(0);
                    if (byguid_.find(guid) != byguid_.end()) {
                        std::stringstream ss;
                        ss << "Instance encountered with non-unique GlobalId " << guid;
                        Logger::Message(Logger::LOG_WARNING, ss.str());
                    }
                    byguid_[guid] = instance;
                } catch (const IfcException& ex) {
                    Logger::Message(Logger::LOG_ERROR, ex.what());
                }
                // this has consumed the instance tokens, set stack depth to 0
                paren_stack_depth = 0;
                attribute_index = -1;
            }

            const IfcParse::declaration* ty = &instance->declaration();

            {
                if (bytype_excl_.find(ty) == bytype_excl_.end()) {
                    bytype_excl_[ty].reset(new aggregate_of_instance());
                }
                bytype_excl_[ty]->push(instance);
            }

            if (byid_.find(current_id) != byid_.end()) {
                std::stringstream ss;
                ss << "Overwriting instance with name #" << current_id;
                Logger::Message(Logger::LOG_WARNING, ss.str());
            }
            byid_[current_id] = instance;

            MaxId = (std::max)(MaxId, current_id);
        } else if (token_stream[0].type == IfcParse::Token_IDENTIFIER && (instance != nullptr)) {
            register_inverse(current_id, instance->declaration().as_entity(), token_stream[0], attribute_index);
        } else if (token_stream[0].type == IfcParse::Token_OPERATOR && token_stream[0].value_char == '(') {
            paren_stack_depth++;
        } else if (token_stream[0].type == IfcParse::Token_OPERATOR && token_stream[0].value_char == ')') {
            paren_stack_depth--;
            if (paren_stack_depth == 0) {
                attribute_index = -1;
            }
        } else if (paren_stack_depth == 1 && token_stream[0].type == IfcParse::Token_OPERATOR && token_stream[0].value_char == ',') {
            attribute_index++;
        }

    advance:
        Token next_token;
        try {
            next_token = tokens->Next();
        } catch (const IfcException& e) {
            Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + ". Parsing terminated");
        } catch (...) {
            Logger::Message(Logger::LOG_ERROR, "Parsing terminated");
        }

        if (next_token.type == Token_NONE) {
            break;
        }

        token_stream.push_back(next_token);
    }

    Logger::Status("\rDone scanning file   ");

    delete tokens;

    auto resolve_instance = [this](auto inst, int ref, int refattr) {
        IfcUtil::IfcBaseClass* ptr;
        if constexpr (std::is_same_v<decltype(inst), int>) {
            entity_by_id_t::const_iterator it = byid_.find(inst);
            if (it == byid_.end()) {
                Logger::Error("Instance reference #" + std::to_string(inst) + " used by instance #" + std::to_string(ref) + " at attribute index " + std::to_string(refattr) + " not found");
                ptr = nullptr;
            } else {
                ptr = it->second;
            }
        } else {
            ptr = inst;
        }
        return ptr;
    };

    for (auto& p : references_to_resolve) {
        boost::apply_visitor([this, &resolve_instance, &p](auto& v) {
            if constexpr (std::is_same_v<std::decay_t<decltype(v)>, reference_or_simple_type>) {
                auto inst = boost::apply_visitor([p, &resolve_instance](auto x) { return resolve_instance(x, p.first.name_, p.first.index_); }, v);
                if (inst) {
                    byid_[p.first.name_]->data().storage_.set(p.first.index_, inst);
                }
            } else if constexpr (std::is_same_v<std::decay_t<decltype(v)>, std::vector<reference_or_simple_type>>) {
                aggregate_of_instance::ptr instances(new aggregate_of_instance);
                instances->reserve(v.size());
                for (auto& vi : v) {
                    auto inst = boost::apply_visitor([p, &resolve_instance](auto x) { return resolve_instance(x, p.first.name_, p.first.index_); }, vi);
                    if (inst) {
                        instances->push(inst);
                    }
                }
                byid_[p.first.name_]->data().storage_.set(p.first.index_, instances);
            } else if constexpr (std::is_same_v<std::decay_t<decltype(v)>, std::vector<std::vector<reference_or_simple_type>>>) {
                aggregate_of_aggregate_of_instance::ptr instances(new aggregate_of_aggregate_of_instance);
                for (auto& vi : v) {
                    std::vector<IfcUtil::IfcBaseClass*> inner;
                    for (auto& vii : vi) {
                        auto inst = boost::apply_visitor([p, &resolve_instance](auto x) { return resolve_instance(x, p.first.name_, p.first.index_); }, vii);
                        if (inst) {
                            inner.push_back(inst);
                        }
                    }
                    instances->push(inner);
                }
                byid_[p.first.name_]->data().storage_.set(p.first.index_, instances);
            } else {
                // static_assert(false, "Inconsistent type");
            }
        }, p.second);
    }

    references_to_resolve.clear();
}

void IfcFile::recalculate_id_counter() {
    entity_by_id_t::key_type k = 0;
    for (auto& p : byid_) {
        if (p.first > k) {
            k = p.first;
        }
    }
    MaxId = (unsigned int)k;
}

class traversal_recorder {
    aggregate_of_instance::ptr list_;
    std::map<int, aggregate_of_instance::ptr> instances_by_level_;
    int mode_;

  public:
    traversal_recorder(int mode) : mode_(mode) {
        if (mode == 0) {
            list_.reset(new aggregate_of_instance);
        }
    };

    void push_back(int level, IfcUtil::IfcBaseClass* instance) {
        if (mode_ == 0) {
            list_->push(instance);
        } else {
            auto& l = instances_by_level_[level];
            if (!l) {
                l.reset(new aggregate_of_instance);
            }
            l->push(instance);
        }
    }

    aggregate_of_instance::ptr get_list() const {
        if (mode_ == 0) {
            return list_;
        }
        aggregate_of_instance::ptr l(new aggregate_of_instance);
        for (const auto& p : instances_by_level_) {
            l->push(p.second);
        }
        return l;
    }
};

class traversal_visitor {
  private:
    std::set<IfcUtil::IfcBaseClass*>& visited_;
    traversal_recorder& list_;
    int level_;
    int max_level_;

  public:
    traversal_visitor(std::set<IfcUtil::IfcBaseClass*>& visited, traversal_recorder& list, int level, int max_level)
        : visited_(visited),
          list_(list),
          level_(level),
          max_level_(max_level) {}

    void operator()(IfcUtil::IfcBaseClass* inst, int index);
};

void traverse_(IfcUtil::IfcBaseClass* instance, std::set<IfcUtil::IfcBaseClass*>& visited, traversal_recorder& list, int level, int max_level) {
    if (visited.find(instance) != visited.end()) {
        return;
    }
    visited.insert(instance);
    list.push_back(level, instance);

    if (level >= max_level && max_level > 0) {
        return;
    }

    traversal_visitor visit(visited, list, level + 1, max_level);
    apply_individual_instance_visitor(&instance->data()).apply(visit);
}

void traversal_visitor::operator()(IfcUtil::IfcBaseClass* inst, int /* index */) {
    traverse_(inst, visited_, list_, level_, max_level_);
}

aggregate_of_instance::ptr IfcParse::traverse(IfcUtil::IfcBaseClass* instance, int max_level) {
    std::set<IfcUtil::IfcBaseClass*> visited;
    traversal_recorder recorder(0);
    traverse_(instance, visited, recorder, 0, max_level);
    return recorder.get_list();
}

// I'm cheating this isn't breadth-first, but rather we record visited instances
// keeping track of their rank and return a list ordered by rank. Is this equivalent?
aggregate_of_instance::ptr IfcParse::traverse_breadth_first(IfcUtil::IfcBaseClass* instance, int max_level) {
    std::set<IfcUtil::IfcBaseClass*> visited;
    traversal_recorder recorder(1);
    traverse_(instance, visited, recorder, 0, max_level);
    return recorder.get_list();
}

/// @note: for backwards compatibility
aggregate_of_instance::ptr IfcFile::traverse(IfcUtil::IfcBaseClass* instance, int max_level) {
    return IfcParse::traverse(instance, max_level);
}

/// @note: for backwards compatibility
aggregate_of_instance::ptr IfcFile::traverse_breadth_first(IfcUtil::IfcBaseClass* instance, int max_level) {
    return IfcParse::traverse_breadth_first(instance, max_level);
}

void IfcFile::addEntities(aggregate_of_instance::ptr entities) {
    for (aggregate_of_instance::it i = entities->begin(); i != entities->end(); ++i) {
        addEntity(*i);
    }
}

IfcUtil::IfcBaseClass* IfcFile::addEntity(IfcUtil::IfcBaseClass* entity, int id) {
    if (id != -1 && byid_.find((unsigned)id) != byid_.end()) {
        throw IfcParse::IfcException("An instance with id " + boost::lexical_cast<std::string>(id) + " is already part of this file");
    }

    if (entity->declaration().schema() != schema()) {
        throw IfcParse::IfcException("Unabled to add instance from " + entity->declaration().schema()->name() + " schema to file with " + schema()->name() + " schema");
    }

    // If this instance has been inserted before, return
    // a reference to the copy that was created from it.
    entity_entity_map_t::iterator mit = entity_file_map_.find(entity->identity());
    if (mit != entity_file_map_.end()) {
        return mit->second;
    }

    IfcUtil::IfcBaseClass* new_entity = entity;

    // Obtain all forward references by a depth-first
    // traversal and add them to the file.
    try {
        aggregate_of_instance::ptr entity_attributes = traverse(entity, 1);
        for (aggregate_of_instance::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
            if (*it != entity) {
                entity_entity_map_t::iterator mit2 = entity_file_map_.find((*it)->identity());
                if (mit2 == entity_file_map_.end()) {
                    entity_file_map_.insert(entity_entity_map_t::value_type((*it)->identity(), addEntity(*it)));
                }
            }
        }
    } catch (...) {
        Logger::Message(Logger::LOG_ERROR, "Failed to visit forward references of", entity);
    }

    // See whether the instance is already part of a file
    if (entity->file_ != nullptr) {
        if (entity->file_ == this) {
            if (entity->declaration().as_entity() == nullptr) {
                // While not a mapping that can be queried, we do need to free the instance later on
                byidentity_[new_entity->identity()] = new_entity;
            }

            // If it is part of this file
            // nothing else needs to be done.
            return entity;
        }

        // An instance is being added from another file. A copy of the
        // container and entity is created. The attribute references
        // need to be updated to point to instances in this file.
        IfcFile* other_file = entity->file_;

        IfcEntityInstanceData we(entity->data());
        new_entity = schema()->instantiate(&entity->declaration(), std::move(we));

        // In case an entity is added that contains geometry, the unit
        // information needs to be accounted for for IfcLengthMeasures.
        double conversion_factor = std::numeric_limits<double>::quiet_NaN();

        for (size_t i = 0; i < new_entity->data().size(); ++i) {
            auto attr = new_entity->data().get_attribute_value(i);
            IfcUtil::ArgumentType attr_type = attr.type();

            IfcParse::declaration* decl = 0;
            if (entity->declaration().as_entity() != nullptr) {
                decl = 0;
                const parameter_type* pt = entity->declaration().as_entity()->attribute_by_index(i)->type_of_attribute();
                while (pt->as_aggregation_type() != nullptr) {
                    pt = pt->as_aggregation_type()->type_of_element();
                }
                if (pt->as_named_type() != nullptr) {
                    decl = pt->as_named_type()->declared_type();
                }
            }

            if (attr_type == IfcUtil::Argument_ENTITY_INSTANCE) {
                entity_entity_map_t::const_iterator eit = entity_file_map_.find(((IfcUtil::IfcBaseClass*)(attr))->identity());
                if (eit == entity_file_map_.end()) {
                    throw IfcParse::IfcException("Unable to map instance to file");
                }
                // We directly use storage set not to trigger inverse recalculation which happens at the end
                new_entity->data().storage_.set(i, eit->second);
            } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
                aggregate_of_instance::ptr instances = attr;
                aggregate_of_instance::ptr new_instances(new aggregate_of_instance);
                for (aggregate_of_instance::it it = instances->begin(); it != instances->end(); ++it) {
                    entity_entity_map_t::const_iterator eit = entity_file_map_.find((*it)->identity());
                    if (eit == entity_file_map_.end()) {
                        throw IfcParse::IfcException("Unable to map instance to file");
                    }
                    new_instances->push(eit->second);
                }

                new_entity->data().storage_.set(i, new_instances);
            } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
                aggregate_of_aggregate_of_instance::ptr instances = attr;
                aggregate_of_aggregate_of_instance::ptr new_instances(new aggregate_of_aggregate_of_instance);
                for (aggregate_of_aggregate_of_instance::outer_it it = instances->begin(); it != instances->end(); ++it) {
                    std::vector<IfcUtil::IfcBaseClass*> list;
                    for (aggregate_of_aggregate_of_instance::inner_it jt = it->begin(); jt != it->end(); ++jt) {
                        entity_entity_map_t::const_iterator eit = entity_file_map_.find((*jt)->identity());
                        if (eit == entity_file_map_.end()) {
                            throw IfcParse::IfcException("Unable to map instance to file");
                        }
                        list.push_back(eit->second);
                    }
                    new_instances->push(list);
                }
                
                new_entity->data().storage_.set(i, new_instances);
            } else if ((decl != nullptr) && decl->is(*schema()->declaration_by_name("IfcLengthMeasure"))) {
                if (boost::math::isnan(conversion_factor)) {
                    std::pair<IfcUtil::IfcBaseClass*, double> this_file_unit = {nullptr, 1.0};
                    std::pair<IfcUtil::IfcBaseClass*, double> other_file_unit = {nullptr, 1.0};
                    try {
                        this_file_unit = getUnit("LENGTHUNIT");
                        other_file_unit = other_file->getUnit("LENGTHUNIT");
                    } catch (IfcParse::IfcException&) {
                    }
                    if ((this_file_unit.first != nullptr) && (other_file_unit.first != nullptr)) {
                        conversion_factor = other_file_unit.second / this_file_unit.second;
                    } else {
                        conversion_factor = 1.;
                    }
                }
                if (attr_type == IfcUtil::Argument_DOUBLE) {
                    double v = attr;
                    v *= conversion_factor;
                    new_entity->data().storage_.set(i, v);
                } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
                    std::vector<double> v = attr;
                    for (std::vector<double>::iterator it = v.begin(); it != v.end(); ++it) {
                        (*it) *= conversion_factor;
                    }
                    new_entity->data().storage_.set(i, v);
                } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
                    std::vector<std::vector<double>> v = attr;
                    for (std::vector<std::vector<double>>::iterator it = v.begin(); it != v.end(); ++it) {
                        std::vector<double>& v2 = (*it);
                        for (std::vector<double>::iterator jt = v2.begin(); jt != v2.end(); ++jt) {
                            (*jt) *= conversion_factor;
                        }
                    }
                    new_entity->data().storage_.set(i, v);
                }
            }
        }

        // A new entity instance name is generated and
        // the instance is pointed to this file.
        new_entity->file_ = this;
        if (new_entity->declaration().as_entity() != nullptr) {
            if (id == -1) {
                new_entity->as<IfcUtil::IfcBaseEntity>()->set_id(FreshId());
            } else {
                new_entity->as<IfcUtil::IfcBaseEntity>()->set_id((unsigned int)id);
                if ((unsigned)id > MaxId) {
                    MaxId = (unsigned)id;
                }
            }
        }

        entity_file_map_.insert(entity_entity_map_t::value_type(entity->identity(), new_entity));
    }

    // For subtypes of IfcRoot, the GUID mapping needs to be updated.
    if (new_entity->declaration().is(*ifcroot_type_)) {
        try {
            const std::string guid = new_entity->data().get_attribute_value(0);
            if (byguid_.find(guid) != byguid_.end()) {
                std::stringstream ss;
                ss << "Overwriting entity with guid " << guid;
                Logger::Message(Logger::LOG_WARNING, ss.str());
            }
            byguid_[guid] = new_entity;
        } catch (const std::exception& ex) {
            Logger::Message(Logger::LOG_ERROR, ex.what());
        }
    }

    // The mapping by entity type is updated.
    const IfcParse::declaration* ty = &new_entity->declaration();

    if (ty->as_entity() != nullptr) {
        if (bytype_excl_.find(ty) == bytype_excl_.end()) {
            bytype_excl_[ty].reset(new aggregate_of_instance());
        }
        bytype_excl_[ty]->push(new_entity);
    }

    if (ty->as_entity() != nullptr) {
        int new_id = -1;
        if (new_entity->file_ == nullptr) {
            // For newly created entities ensure a valid ENTITY_INSTANCE_NAME is set
            new_entity->file_ = this;
            boost::optional<unsigned> id_value;
            if (id != -1) {
                id_value = (unsigned)id;
                if ((unsigned)id > MaxId) {
                    MaxId = (unsigned)id;
                }
            }
            new_id = new_entity->as<IfcUtil::IfcBaseEntity>()->set_id(id_value);
        } else {
            new_id = new_entity->id();
        }

        if (byid_.find(new_id) != byid_.end()) {
            // This should not happen
            std::stringstream ss;
            ss << "Overwriting entity with id " << new_id;
            Logger::Message(Logger::LOG_WARNING, ss.str());
        }
        // The mapping by entity instance name is updated.
        byid_[new_id] = new_entity;
    } else if (new_entity->file_ == nullptr) {
        // For non-entity instances, no mappings are updated, but the file
        // pointer has to be set, so that actual copies are created in subsequent
        // times.
        new_entity->file_ = this;

        // While not a mapping that can be queried, we do need to free the instance
        byidentity_[new_entity->identity()] = new_entity;
    }

    if ((ty->as_entity() != nullptr)) {
        build_inverses_(new_entity);
    }

    return new_entity;
}

void IfcFile::removeEntity(IfcUtil::IfcBaseClass* entity) {
    const unsigned id = entity->id();

    IfcUtil::IfcBaseClass* file_entity = instance_by_id(id);

    // Attention when running removeEntity inside a loop over a list of entities to be removed.
    // This invalidates the iterator. A workaround is to reverse the loop:
    // boost::shared_ptr<aggregate_of_instance> entities = ...;
    // for (auto it = entities->end() - 1; it >= entities->begin(); --it) {
    //    IfcUtil::IfcBaseClass *const inst = *it;
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

    batch_deletion_ids_.push_back(id);

    if (!batch_mode_) {
        process_deletion_();
    }
}

void IfcFile::process_deletion_() {

    for (const auto& id : batch_deletion_ids_.get<0>()) {
        auto* entity = instance_by_id(id);

        aggregate_of_instance::ptr references = instances_by_reference(id);

        // Alter entity instances with INVERSE relations to the entity being
        // deleted. This is necessary to maintain a valid IFC file, because
        // dangling references to it's entities name should be removed. At this
        // moment, inversely related instances affected by the removal of the
        // entity being deleted are not deleted themselves.
        if (references) {
            for (aggregate_of_instance::it iit = references->begin(); iit != references->end(); ++iit) {
                IfcUtil::IfcBaseEntity* related_instance = (IfcUtil::IfcBaseEntity*)*iit;

                if (std::find(batch_deletion_ids_.begin(), batch_deletion_ids_.end(), related_instance->id()) != batch_deletion_ids_.end()) {
                    continue;
                }

                for (size_t i = 0; i < related_instance->data().size(); ++i) {
                    auto attr = related_instance->data().get_attribute_value(i);
                    if (attr.isNull()) {
                        continue;
                    }

                    IfcUtil::ArgumentType attr_type = attr.type();
                    switch (attr_type) {
                    case IfcUtil::Argument_ENTITY_INSTANCE: {
                        IfcUtil::IfcBaseClass* instance_attribute = attr;
                        if (instance_attribute == entity) {
                            related_instance->set_attribute_value(i, Blank{});
                        }
                    } break;
                    case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
                        aggregate_of_instance::ptr instance_list = attr;
                        if (instance_list->contains(entity)) {
                            instance_list->remove(entity);
                            if ((instance_list->size() == 0U) && related_instance->declaration().as_entity()->attribute_by_index(i)->optional()) {
                                // @todo we can also check the lower bound of the attribute type before setting to null.
                                related_instance->set_attribute_value(i, Blank{});
                            } else {
                                related_instance->set_attribute_value(i, instance_list);
                            }
                        }
                    } break;
                    case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
                        aggregate_of_aggregate_of_instance::ptr instance_list_list = attr;
                        if (instance_list_list->contains(entity)) {
                            aggregate_of_aggregate_of_instance::ptr new_list(new aggregate_of_aggregate_of_instance);
                            for (aggregate_of_aggregate_of_instance::outer_it it = instance_list_list->begin(); it != instance_list_list->end(); ++it) {
                                std::vector<IfcUtil::IfcBaseClass*> instances = *it;
                                std::vector<IfcUtil::IfcBaseClass*>::iterator jt;
                                while ((jt = std::find(instances.begin(), instances.end(), entity)) != instances.end()) {
                                    instances.erase(jt);
                                }
                                new_list->push(instances);
                            }
                            related_instance->set_attribute_value(i, new_list);
                        }
                    } break;
                    default:
                        break;
                    }
                }
            }
        }

        if (!batch_mode_) {
            byref_excl_.erase(
                byref_excl_.lower_bound({id, -1, -1}),
                byref_excl_.upper_bound({id, std::numeric_limits<short>::max(), std::numeric_limits<short>::max()}));

            // byref_excl_.erase(id);

            // This is based on traversal which needs instances to still be contained in the map.
            // another option would be to keep byid intact for the remainder of this loop
            aggregate_of_instance::ptr entity_attributes = traverse(entity, 1);
            for (aggregate_of_instance::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
                IfcUtil::IfcBaseClass* entity_attribute = *it;
                if (entity_attribute == entity) {
                    continue;
                }
                const unsigned int name = entity_attribute->id();
                // Do not update inverses for simple types (which have id()==0 in IfcOpenShell).
                if (name != 0) {
                    {
                        auto lower = byref_excl_.lower_bound({name, -1, -1});
                        auto upper = byref_excl_.upper_bound({name, std::numeric_limits<short>::max(), std::numeric_limits<short>::max()});

                        for (auto byref_it = lower; byref_it != upper; ++byref_it) {
                            auto& ids = byref_it->second;
                            ids.erase(std::remove(ids.begin(), ids.end(), id), ids.end());
                        }
                    }
                }
            }
        }

        if (entity->declaration().is(*ifcroot_type_) && !entity->data().get_attribute_value(0).isNull()) {
            const std::string global_id = entity->data().get_attribute_value(0);
            auto it = byguid_.find(global_id);
            if (it != byguid_.end()) {
                byguid_.erase(it);
            } else {
                Logger::Warning("GlobalId on rooted instance not encountered in map");
            }
        }

        byid_.erase(byid_.find(id));

        const IfcParse::declaration* ty = &entity->declaration();

        {
            auto it = bytype_excl_.find(ty);
            if (it != bytype_excl_.end()) {
                it->second->remove(entity);
                if (it->second->size() == 0) {
                    bytype_excl_.erase(ty);
                }
            }
        }

        // entity_file_map is in place to prevent duplicate definitions with usage of add().
        // Upon deletion the pairs need to be erased.
        for (auto it = entity_file_map_.begin(); it != entity_file_map_.end();) {
            if (it->second == entity) {
                it = entity_file_map_.erase(it);
            } else {
                ++it;
            }
        }

        delete entity;
    }

    if (batch_mode_) {
        for (auto it = byref_excl_.begin(); it != byref_excl_.end();) {
            bool do_delete = batch_deletion_ids_.get<1>().find(std::get<INSTANCE_ID>(it->first)) != batch_deletion_ids_.get<1>().end();
            if (!do_delete) {
                it->second.erase(std::remove_if(it->second.begin(), it->second.end(), [this](int x) {
                                     return batch_deletion_ids_.get<1>().find(x) != batch_deletion_ids_.get<1>().end();
                                 }),
                                 it->second.end());
                do_delete = it->second.empty();
            }
            if (do_delete) {
                it = byref_excl_.erase(it);
            } else {
                ++it;
            }
        }
    }

    batch_deletion_ids_.clear();
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

aggregate_of_instance::ptr IfcFile::instances_by_type(const IfcParse::declaration* t) {
    aggregate_of_instance::ptr insts(new aggregate_of_instance);
    if (t->as_entity() != nullptr) {
        visit_subtypes(t->as_entity(), [this, &insts](const IfcParse::entity* ent) {
            auto it = bytype_excl_.find(ent);
            if (it != bytype_excl_.end()) {
                insts->push(it->second);
            }
        });
    }
    return insts;
}

aggregate_of_instance::ptr IfcFile::instances_by_type_excl_subtypes(const IfcParse::declaration* t) {
    entities_by_type_t::const_iterator it = bytype_excl_.find(t);
    return (it == bytype_excl_.end()) ? aggregate_of_instance::ptr(new aggregate_of_instance) : it->second;
}

aggregate_of_instance::ptr IfcFile::instances_by_type(const std::string& t) {
    return instances_by_type(schema()->declaration_by_name(t));
}

aggregate_of_instance::ptr IfcFile::instances_by_type_excl_subtypes(const std::string& t) {
    return instances_by_type_excl_subtypes(schema()->declaration_by_name(t));
}

aggregate_of_instance::ptr IfcFile::instances_by_reference(int t) {
    auto lower = byref_excl_.lower_bound({ t, -1, -1 });
    auto upper = byref_excl_.upper_bound({ t, std::numeric_limits<short>::max(), std::numeric_limits<short>::max() });
    aggregate_of_instance::ptr ret(new aggregate_of_instance);
    for (auto it = lower; it != upper; ++it) {
        for (auto& i : it->second) {
            ret->push(instance_by_id(i));
        }
    }
    return ret;
}

IfcUtil::IfcBaseClass* IfcFile::instance_by_id(int id) {
    entity_by_id_t::const_iterator it = byid_.find(id);
    if (it == byid_.end()) {
        throw IfcException("Instance #" + boost::lexical_cast<std::string>(id) + " not found");
    }
    return it->second;
}

IfcUtil::IfcBaseClass* IfcFile::instance_by_guid(const std::string& guid) {
    entity_by_guid_t::const_iterator it = byguid_.find(guid);
    if (it == byguid_.end()) {
        throw IfcException("Instance with GlobalId '" + guid + "' not found");
    }
    return it->second;
}

// FIXME: Test destructor to delete entity and arg allocations
IfcFile::~IfcFile() {
    std::set<IfcUtil::IfcBaseClass*> entities_to_delete;
    for (const auto& pair : byid_) {
        entities_to_delete.insert(pair.second);
    }
    for (const auto& pair : byidentity_) {
        entities_to_delete.insert(pair.second);
    }
    for (auto* entity : entities_to_delete) {
        delete entity;
    }
}

IfcFile::entity_by_id_t::const_iterator IfcFile::begin() const {
    return byid_.begin();
}

IfcFile::entity_by_id_t::const_iterator IfcFile::end() const {
    return byid_.end();
}

IfcFile::type_iterator IfcFile::types_begin() const {
    return bytype_excl_.begin();
}

IfcFile::type_iterator IfcFile::types_end() const {
    return bytype_excl_.end();
}

namespace {
struct id_instance_pair_sorter {
    bool operator()(const IfcParse::IfcFile::entity_by_id_t::value_type& a, const IfcParse::IfcFile::entity_by_id_t::value_type& b) const {
        return a.first < b.first;
    }
};
} // namespace

std::ostream& operator<<(std::ostream& out, const IfcParse::IfcFile& file) {
    file.header().write(out);

    typedef std::vector<std::pair<unsigned int, IfcUtil::IfcBaseClass*>> vector_t;
    vector_t sorted(file.begin(), file.end());
    std::sort(sorted.begin(), sorted.end(), id_instance_pair_sorter());

    for (vector_t::const_iterator it = sorted.begin(); it != sorted.end(); ++it) {
        const IfcUtil::IfcBaseClass* e = it->second;
        if (e->declaration().as_entity() != nullptr) {
            e->toString(out, true);
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

std::vector<int> IfcFile::get_inverse_indices(int instance_id) {
    std::vector<int> return_value;

    auto lower = byref_excl_.lower_bound({instance_id, -1, -1});
    auto upper = byref_excl_.upper_bound({instance_id, std::numeric_limits<short>::max(), std::numeric_limits<short>::max()});

    // Mapping of instance id to attribute offset.
    std::map<int, std::vector<int>> mapping;

    for (auto it = lower; it != upper; ++it) {
        for (auto& i : it->second) {
            // We only take the tuple for the type that id=i actually is, in order not
            // to count double. Because byref contains mappings for every supertype of id=i.
            if (instance_by_id(i)->declaration().index_in_schema() == std::get<1>(it->first)) {
                mapping[i].push_back(std::get<2>(it->first));
            }
        }
    }

    auto refs = instances_by_reference(instance_id);

    for (const auto& ref : *refs) {
        auto it = mapping.find(ref->id());
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

aggregate_of_instance::ptr IfcFile::getInverse(int instance_id, const IfcParse::declaration* type, int attribute_index) {
    if (type == nullptr && attribute_index == -1) {
        return instances_by_reference(instance_id);
    }

    aggregate_of_instance::ptr return_value(new aggregate_of_instance);

    visit_subtypes(type->as_entity(), [this, attribute_index, instance_id, &return_value](const IfcParse::declaration* ent) {
        if (attribute_index == -1) {
            auto lower = byref_excl_.lower_bound({ instance_id, ent->index_in_schema(), -1 });
            auto upper = byref_excl_.upper_bound({ instance_id, ent->index_in_schema(), std::numeric_limits<short>::max() });

            for (auto it = lower; it != upper; ++it) {
                for (auto& i : it->second) {
                    return_value->push(instance_by_id(i));
                }
            }
        } else {
            auto it = byref_excl_.find({ instance_id, ent->index_in_schema(), attribute_index });
            if (it != byref_excl_.end()) {
                for (auto& i : it->second) {
                    return_value->push(instance_by_id(i));
                }
            }
        }
    });

    return return_value;
}

size_t IfcFile::getTotalInverses(int instance_id) {
    size_t n = 0;
    auto lower = byref_excl_.lower_bound({ instance_id, -1, -1 });
    auto upper = byref_excl_.upper_bound({ instance_id, std::numeric_limits<short>::max(), std::numeric_limits<short>::max() });
    for (auto it = lower; it != upper; ++it) {
        n += it->second.size();
    }
    return n;
}

void IfcFile::setDefaultHeaderValues() {
    const std::string empty_string;
    std::vector<std::string> file_description;
    std::vector<std::string> schema_identifiers;
    std::vector<std::string> empty_vector;

    file_description.push_back("ViewDefinition [CoordinationView]");
    if (schema() != nullptr) {
        schema_identifiers.push_back(schema()->name());
    }

    header().file_description().description(file_description);
    header().file_description().implementation_level("2;1");

    header().file_name().name(empty_string);
    header().file_name().time_stamp(createTimestamp());
    header().file_name().author(empty_vector);
    header().file_name().organization(empty_vector);
    header().file_name().preprocessor_version("IfcOpenShell " IFCOPENSHELL_VERSION);
    header().file_name().originating_system("IfcOpenShell " IFCOPENSHELL_VERSION);
    header().file_name().authorization(empty_string);

    header().file_schema().schema_identifiers(schema_identifiers);
}

std::pair<IfcUtil::IfcBaseClass*, double> IfcFile::getUnit(const std::string& unit_type) {
    std::pair<IfcUtil::IfcBaseClass*, double> return_value(0, 1.);

    aggregate_of_instance::ptr projects = instances_by_type(schema()->declaration_by_name("IfcProject"));
    if (!projects || projects->size() == 0) {
        try {
            projects = instances_by_type(schema()->declaration_by_name("IfcContext"));
        } catch (IfcException&) {
        }
    }

    if (projects && projects->size() == 1) {
        IfcUtil::IfcBaseClass* project = *projects->begin();

        IfcUtil::IfcBaseClass* unit_assignment = project->data().get_attribute_value(
            project->declaration().as_entity()->attribute_index("UnitsInContext"));

        aggregate_of_instance::ptr units = unit_assignment->data().get_attribute_value(
            unit_assignment->declaration().as_entity()->attribute_index("Units"));

        for (aggregate_of_instance::it it = units->begin(); it != units->end(); ++it) {
            IfcUtil::IfcBaseClass* unit = *it;
            if (unit->declaration().is("IfcNamedUnit")) {
                const std::string file_unit_type = unit->data().get_attribute_value(
                    unit->declaration().as_entity()->attribute_index("UnitType"));

                if (file_unit_type != unit_type) {
                    continue;
                }

                IfcUtil::IfcBaseClass* siunit = 0;
                if (unit->declaration().is("IfcConversionBasedUnit")) {
                    IfcUtil::IfcBaseClass* mu = unit->data().get_attribute_value(
                        unit->declaration().as_entity()->attribute_index("ConversionFactor"));

                    IfcUtil::IfcBaseClass* vlc = mu->data().get_attribute_value(
                        mu->declaration().as_entity()->attribute_index("ValueComponent"));

                    IfcUtil::IfcBaseClass* unc = mu->data().get_attribute_value(
                        mu->declaration().as_entity()->attribute_index("UnitComponent"));

                    return_value.second *= static_cast<double>(vlc->data().get_attribute_value(0));
                    return_value.first = unit;

                    if (unc->declaration().is("IfcSIUnit")) {
                        siunit = unc;
                    }

                } else if (unit->declaration().is("IfcSIUnit")) {
                    return_value.first = siunit = unit;
                }

                if (siunit != nullptr) {
                    AttributeValue prefix = siunit->data().get_attribute_value(
                        siunit->declaration().as_entity()->attribute_index("Prefix"));

                    if (!prefix.isNull()) {
                        return_value.second *= IfcSIPrefixToValue(prefix);
                    }
                }
            }
        }
    }

    return return_value;
}

void IfcParse::IfcFile::build_inverses_(IfcUtil::IfcBaseClass* inst) {
    std::function<void(IfcUtil::IfcBaseClass*, int)> fn = [this, inst](IfcUtil::IfcBaseClass* attr, int idx) {
        if (attr->declaration().as_entity() != nullptr) {
            unsigned entity_attribute_id = attr->id();
            const auto* decl = inst->declaration().as_entity();
            byref_excl_[{entity_attribute_id, decl->index_in_schema(), idx}].push_back(inst->id());
        }
    };

    apply_individual_instance_visitor(&inst->data()).apply(fn);
}

void IfcParse::IfcFile::build_inverses() {
    for (const auto& pair : *this) {
        build_inverses_(pair.second);
    }
}

std::atomic_uint32_t IfcUtil::IfcBaseClass::counter_(0);

bool IfcParse::IfcFile::guid_map_ = true;

void IfcUtil::IfcBaseClass::unset_attribute_value(size_t index) {
    data_.storage_.set(index, Blank{});
}

void IfcUtil::IfcBaseClass::toString(std::ostream& out, bool upper) const
{
    const auto *ent = declaration().as_entity();
    if (ent != nullptr) {
        out << "#" << as<IfcUtil::IfcBaseEntity>()->id() << "=";
    }
    if (upper) {
        out << declaration().name_uc();
    } else {
        out << declaration().name();
    }
    data().toString(out, upper, ent);
}

IfcEntityInstanceData::IfcEntityInstanceData(const IfcEntityInstanceData& data)
    : storage_(data.storage_.size() )
{
    for (size_t i = 0; i < data.storage_.size(); ++i) {
        data.storage_.apply_visitor([this, i](const auto& v) {
            using U = std::decay_t<decltype(v)>;
            if constexpr (std::is_same_v<U, aggregate_of_instance::ptr>) {
                // @todo why did we ever choose shared_ptrs for these
                // aggregates? Now we need to explicit copies.
                aggregate_of_instance::ptr v2(new aggregate_of_instance);
                if (v) {
                    v2->reserve(v->size());
                    for (auto& i : *v) {
                        v2->push(i);
                    }
                }
                storage_.set(i, v2);
            } else if constexpr (std::is_same_v<U, aggregate_of_aggregate_of_instance::ptr>) {
                aggregate_of_aggregate_of_instance::ptr v2(new aggregate_of_aggregate_of_instance);
                if (v) {
                    for (auto& i : *v) {
                        v2->push(i);
                    }
                }
                storage_.set(i, v2);
            } else {
                storage_.set(i, v);
            }
        }, i);
    }
}

AttributeValue IfcEntityInstanceData::get_attribute_value(size_t index) const
{
    return { &storage_, (uint8_t) index };
}


template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<Blank>(size_t index, const Blank& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<int>(size_t index, const int& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<bool>(size_t index, const bool& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<boost::logic::tribool>(size_t index, const boost::logic::tribool& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<double>(size_t index, const double& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::string>(size_t index, const std::string& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<boost::dynamic_bitset<>>(size_t index, const boost::dynamic_bitset<>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<EnumerationReference>(size_t index, const EnumerationReference& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<IfcUtil::IfcBaseClass*>(size_t index, IfcUtil::IfcBaseClass* const& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<int>>(size_t index, const std::vector<int>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<double>>(size_t index, const std::vector<double>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<std::string>>(size_t index, const std::vector<std::string>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<boost::dynamic_bitset<>>>(size_t index, const std::vector<boost::dynamic_bitset<>>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<aggregate_of_instance::ptr>(size_t index, const aggregate_of_instance::ptr& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<std::vector<int>>>(size_t index, const std::vector<std::vector<int>>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<std::vector<double>>>(size_t index, const std::vector<std::vector<double>>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<aggregate_of_aggregate_of_instance::ptr>(size_t index, const aggregate_of_aggregate_of_instance::ptr& value);

template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<Blank>(const std::string& name, const Blank& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<int>(const std::string& name, const int& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<bool>(const std::string& name, const bool& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<boost::logic::tribool>(const std::string& name, const boost::logic::tribool& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<double>(const std::string& name, const double& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::string>(const std::string& name, const std::string& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<boost::dynamic_bitset<>>(const std::string& name, const boost::dynamic_bitset<>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<EnumerationReference>(const std::string& name, const EnumerationReference& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<IfcUtil::IfcBaseClass*>(const std::string& name, IfcUtil::IfcBaseClass* const& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<int>>(const std::string& name, const std::vector<int>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<double>>(const std::string& name, const std::vector<double>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<std::string>>(const std::string& name, const std::vector<std::string>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<boost::dynamic_bitset<>>>(const std::string& name, const std::vector<boost::dynamic_bitset<>>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<aggregate_of_instance::ptr>(const std::string& name, const aggregate_of_instance::ptr& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<std::vector<int>>>(const std::string& name, const std::vector<std::vector<int>>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<std::vector<std::vector<double>>>(const std::string& name, const std::vector<std::vector<double>>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_attribute_value<aggregate_of_aggregate_of_instance::ptr>(const std::string& name, const aggregate_of_aggregate_of_instance::ptr& value);
