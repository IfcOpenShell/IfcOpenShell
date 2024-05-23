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
#include <boost/math/special_functions/fpclassify.hpp>
#include <ctime>
#include <mutex>
#include <set>
#include <stdio.h>
#include <stdlib.h>
#include <string>

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
unsigned int IfcSpfStream::Tell() {
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

unsigned int IfcSpfLexer::skipWhitespace() {
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

unsigned int IfcSpfLexer::skipComment() {
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
    if (len != 0) {
        return GeneralTokenPtr(this, pos, stream->Tell());
    }
    return NoneTokenPtr();
}

bool IfcSpfStream::is_eof_at(unsigned int local_ptr) {
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
    if (str.size() < 1) {
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

TokenArgument::TokenArgument(const Token& tok) {
    token = tok;
}

EntityArgument::EntityArgument(const Token& token) {
    IfcParse::IfcFile* file = token.lexer->file;
    IfcEntityInstanceData* data = read(0, file, token.startPos);
    // Data needs to be loaded, for the tokens
    // to be consumed and parsing to continue.
    data->load();
    entity_ = file->schema()->instantiate(data);
}

namespace {
template <typename T>
class vector_or_array {
    std::vector<T>* vector_;
    T* array_;
    size_t size_, index_;

  public:
    vector_or_array(std::vector<T>* vector)
        : vector_(vector),
          array_(0),
          size_(0),
          index_(0) {}

    vector_or_array(Argument** arr, size_t size)
        : vector_(0),
          array_(arr),
          size_(size),
          index_(0) {}

    void push_back(const T& type) {
        // @todo this should log a warning when the size is exceeded
        if (array_ && index_ < size_) {
            array_[index_++] = type;
        } else if (vector_) {
            vector_->push_back(type);
        }
    }

    size_t index() const {
        if (vector_) {
            return vector_->size();
        }
        return index_;
    }
};
} // namespace

//
// Reads the arguments from a list of token
// Aditionally, registers the ids (i.e. #[\d]+) in the inverse map
//
size_t IfcParse::IfcFile::load(unsigned entity_instance_name, const IfcParse::entity* entity, Argument**& attributes, size_t num_attributes, int attribute_index) {
    Token next = tokens->Next();

    std::vector<Argument*>* vector = 0;
    vector_or_array<Argument*> filler(attributes, num_attributes);
    if (attributes == 0) {
        if (num_attributes != 0) {
            // If num_attributes is zero we know this is a top-level entity instance (or header entity) being parsed.
            // There can only be parsed one of these at a time, so we can reuse the vector we have defined at the file
            // scope.
            if (entity != nullptr) {
                vector = &internal_attribute_vector_;
            } else {
                vector = &internal_attribute_vector_simple_type_;
            }
            vector->clear();
        } else {
            vector = new std::vector<Argument*>;
        }
        filler = vector_or_array<Argument*>(vector);
    }

    size_t return_value = 0;

    while ((next.startPos != 0U) || (next.lexer != nullptr)) {
        if (TokenFunc::isOperator(next, ',')) {
            // do nothing
        } else if (TokenFunc::isOperator(next, ')')) {
            break;
        } else if (TokenFunc::isOperator(next, '(')) {
            return_value++;
            ArgumentList* alist = new ArgumentList();
            // entity is passed along here, after all the it is the type of the instance
            // that owns the list that is significant for inverse attributes
            alist->size() = load(entity_instance_name, entity, alist->arguments(), 0, attribute_index == -1 ? (int)filler.index() : attribute_index);
            filler.push_back(alist);
        } else {
            return_value++;
            if (TokenFunc::isIdentifier(next)) {
                if (!parsing_complete_) {
                    register_inverse(entity_instance_name, entity, next, attribute_index == -1 ? (int)filler.index() : attribute_index);
                }
            }

            if (TokenFunc::isKeyword(next)) {
                try {
                    auto* entity = new EntityArgument(next);
                    addEntity(((IfcUtil::IfcBaseClass*)*entity));
                    filler.push_back(entity);
                } catch (IfcException& e) {
                    Logger::Message(Logger::LOG_ERROR, e.what());
                    // #4070 We didn't actually capture an aggregate entry, undo length increment.
                    return_value--;
                }
            } else {
                filler.push_back(new TokenArgument(next));
            }
        }
        next = tokens->Next();
    }

    if (vector != nullptr) {
        // Obviously don't try and create a 0-length array.
        if ((num_attributes != 0U) || !vector->empty()) {
            // @todo figure out whether all this logic is still necessary, since we know the
            // expected amount of attributes and shouldn't be able to access more than allowed
            // by the schema.
            attributes = new Argument* [(std::max)(num_attributes, vector->size())] { nullptr };

            // @todo this appears unnecessary, we increment this in the loop already,
            // which is more accurate as the filler can't go above it's size in case
            // it uses the pre-allocated c-array.
            // -> return_value = vector->size();

            for (size_t i = 0; i < vector->size(); ++i) {
                attributes[i] = vector->at(i);
            }
        }

        if ((vector != &internal_attribute_vector_) && (vector != &internal_attribute_vector_simple_type_)) {
            delete vector;
        }
    }

    return return_value;
}

IfcUtil::ArgumentType ArgumentList::type() const {
    if (size_ == 0) {
        return IfcUtil::Argument_EMPTY_AGGREGATE;
    }

    const IfcUtil::ArgumentType elem_type = list_[0]->type();
    return IfcUtil::make_aggregate(elem_type);
}

// templated helper function for reading arguments into a list
template <typename T>
std::vector<T> read_aggregate_as_vector(Argument** list, size_t size) {
    std::vector<T> return_value;
    return_value.reserve(size);
    for (size_t i = 0; i < size; ++i) {
        return_value.push_back(*list[i]);
    }
    return return_value;
}
template <typename T>
std::vector<std::vector<T>> read_aggregate_of_aggregate_as_vector2(Argument** list, size_t size) {
    std::vector<std::vector<T>> return_value;
    return_value.reserve(size);
    for (size_t i = 0; i < size; ++i) {
        return_value.push_back(*list[i]);
    }
    return return_value;
}

//
// Functions for casting the ArgumentList to other types
//
ArgumentList::operator std::vector<double>() const {
    return read_aggregate_as_vector<double>(list_, size_);
}

ArgumentList::operator std::vector<int>() const {
    return read_aggregate_as_vector<int>(list_, size_);
}

ArgumentList::operator std::vector<std::string>() const {
    return read_aggregate_as_vector<std::string>(list_, size_);
}

ArgumentList::operator std::vector<boost::dynamic_bitset<>>() const {
    return read_aggregate_as_vector<boost::dynamic_bitset<>>(list_, size_);
}

ArgumentList::operator aggregate_of_instance::ptr() const {
    aggregate_of_instance::ptr l(new aggregate_of_instance());
    for (size_t i = 0; i < size_; ++i) {
        // FIXME: account for $
        try {
            IfcUtil::IfcBaseClass* entity = *list_[i];
            l->push(entity);
        } catch (IfcException e) {
            Logger::Error(e);
        }
    }
    return l;
}

ArgumentList::operator std::vector<std::vector<int>>() const {
    return read_aggregate_of_aggregate_as_vector2<int>(list_, size_);
}

ArgumentList::operator std::vector<std::vector<double>>() const {
    return read_aggregate_of_aggregate_as_vector2<double>(list_, size_);
}

ArgumentList::operator aggregate_of_aggregate_of_instance::ptr() const {
    aggregate_of_aggregate_of_instance::ptr l(new aggregate_of_aggregate_of_instance());
    for (size_t i = 0; i < size_; ++i) {
        const Argument* arg = list_[i];
        const ArgumentList* arg_list;
        if ((arg_list = dynamic_cast<const ArgumentList*>(arg)) != 0) {
            aggregate_of_instance::ptr e = *arg_list;
            l->push(e);
        } else {
            const auto* token = dynamic_cast<const TokenArgument*>(arg);
            int startpos = token != nullptr ? token->token.startPos : 0;
            std::string string_rep = this->toString();
            throw IfcInvalidTokenException(startpos, string_rep, "nested aggregate");
        }
    }
    return l;
}

unsigned int ArgumentList::size() const { return (unsigned int)size_; }

Argument* ArgumentList::operator[](unsigned int i) const {
    if (i >= size_) {
        throw IfcAttributeOutOfRangeException("Argument index out of range");
    }
    return list_[i];
}

/*
void ArgumentList::set(unsigned int i, Argument* argument) {
	while (size() < i) {
		push(new NullArgument());
	}
	if (i < size()) {
		delete list[i];
		list[i] = argument;
	} else {
		list.push_back(argument);
	}	
}
*/

std::string ArgumentList::toString(bool upper) const {
    std::stringstream ss;
    ss << "(";
    for (size_t i = 0; i < size_; ++i) {
        if (i != 0) {
            ss << ",";
        }
        ss << list_[i]->toString(upper);
    }
    ss << ")";
    return ss.str();
}

bool ArgumentList::isNull() const { return false; }

ArgumentList::~ArgumentList() {
    for (size_t i = 0; i < size_; ++i) {
        delete list_[i];
    }
    delete[] list_;
}

IfcUtil::ArgumentType TokenArgument::type() const {
    if (TokenFunc::isInt(token)) {
        return IfcUtil::Argument_INT;
    }
    if (TokenFunc::isBool(token)) {
        return IfcUtil::Argument_BOOL;
    }
    if (TokenFunc::isLogical(token)) {
        return IfcUtil::Argument_LOGICAL;
    }
    if (TokenFunc::isFloat(token)) {
        return IfcUtil::Argument_DOUBLE;
    }
    if (TokenFunc::isString(token)) {
        return IfcUtil::Argument_STRING;
    }
    if (TokenFunc::isEnumeration(token)) {
        return IfcUtil::Argument_ENUMERATION;
    }
    if (TokenFunc::isIdentifier(token)) {
        return IfcUtil::Argument_ENTITY_INSTANCE;
    }
    if (TokenFunc::isBinary(token)) {
        return IfcUtil::Argument_BINARY;
    }
    if (TokenFunc::isOperator(token, '$')) {
        return IfcUtil::Argument_NULL;
    }
    if (TokenFunc::isOperator(token, '*')) {
        return IfcUtil::Argument_DERIVED;
    }
    return IfcUtil::Argument_UNKNOWN;
}

//
// Functions for casting the TokenArgument to other types
//
TokenArgument::operator int() const { return TokenFunc::asInt(token); }
TokenArgument::operator bool() const { return TokenFunc::asBool(token); }
TokenArgument::operator boost::logic::tribool() const { return TokenFunc::asLogical(token); }
TokenArgument::operator double() const { return TokenFunc::asFloat(token); }
TokenArgument::operator std::string() const { return TokenFunc::asString(token); }
TokenArgument::operator boost::dynamic_bitset<>() const { return TokenFunc::asBinary(token); }
TokenArgument::operator IfcUtil::IfcBaseClass*() const { return token.lexer->file->instance_by_id(TokenFunc::asIdentifier(token)); }
unsigned int TokenArgument::size() const { return 1; }
Argument* TokenArgument::operator[](unsigned int /*i*/) const { throw IfcException("Argument is not a list of attributes"); }
std::string TokenArgument::toString(bool upper) const {
    if (upper && TokenFunc::isString(token)) {
        return IfcWrite::IfcCharacterEncoder(TokenFunc::asString(token));
    }
    return TokenFunc::toString(token);
}
bool TokenArgument::isNull() const { return TokenFunc::isOperator(token, '$'); }

IfcUtil::ArgumentType EntityArgument::type() const {
    return IfcUtil::Argument_ENTITY_INSTANCE;
}

//
// Functions for casting the EntityArgument to other types
//
EntityArgument::operator IfcUtil::IfcBaseClass*() const {
    return entity_;
}

unsigned int EntityArgument::size() const {
    return 1;
}

Argument* EntityArgument::operator[](unsigned int /*i*/) const {
    throw IfcException("Argument is not a list of arguments");
}

std::string EntityArgument::toString(bool upper) const {
    return entity_->data().toString(upper);
}

bool EntityArgument::isNull() const { return false; }
EntityArgument::~EntityArgument() {
    // We don't delete it here, rather it will be freed as part of the entity_file_map.
    // For that purpose when parsed, the simple type instance is explicitly added to the
    // file. The reason is we want parsed simply types to behave the same as constructed
    // simple types.

    // delete entity;
}

//
// Reads an Entity from the list of Tokens at the specified offset in the file
//
IfcEntityInstanceData* IfcParse::read(unsigned int i, IfcFile* f, boost::optional<unsigned> offset) {
    if (offset) {
        f->tokens->stream->Seek(*offset);
    }
    Token datatype = f->tokens->Next();
    if (!TokenFunc::isKeyword(datatype)) {
        throw IfcException("Unexpected token while parsing entity");
    }
    const IfcParse::declaration* ty = f->schema()->declaration_by_name(TokenFunc::asStringRef(datatype));
    IfcEntityInstanceData* e = new IfcEntityInstanceData(ty, f, i, offset.get_value_or(0));
    return e;
}

void IfcParse::IfcFile::seek_to(const IfcEntityInstanceData& data) {
    if (tokens->stream->Tell() != data.offset_in_file()) {
        tokens->stream->Seek(data.offset_in_file());
        Token datatype = tokens->Next();
        if (!TokenFunc::isKeyword(datatype)) {
            throw IfcException("Unexpected token while parsing entity instance");
        }
    }
    tokens->Next();
}

void IfcParse::IfcFile::try_read_semicolon() {
    unsigned int old_offset = tokens->stream->Tell();
    Token semilocon = tokens->Next();
    if (!TokenFunc::isOperator(semilocon, ';')) {
        tokens->stream->Seek(old_offset);
    }
}

void IfcParse::IfcFile::register_inverse(unsigned id_from, const IfcParse::entity* from_entity, Token t, int attribute_index) {
    // Assume a check on token type has already been performed
    const auto* e = from_entity;
    byref_excl_[t.value_int].push_back(id_from);
    while (e != nullptr) {
        byref_[{t.value_int, e->index_in_schema(), attribute_index}].push_back(id_from);
        e = e->supertype();
    }
}

void IfcParse::IfcFile::register_inverse(unsigned id_from, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass* inst, int attribute_index) {
    const auto* e = from_entity;
    byref_excl_[inst->data().id()].push_back(id_from);
    while (e != nullptr) {
        byref_[{inst->data().id(), e->index_in_schema(), attribute_index}].push_back(id_from);
        e = e->supertype();
    }
}

void IfcParse::IfcFile::unregister_inverse(unsigned id_from, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass* inst, int attribute_index) {
    const auto* entity = from_entity;
    while (entity != nullptr) {
        std::vector<int>& ids = byref_[{inst->data().id(), entity->index_in_schema(), attribute_index}];
        std::vector<int>::iterator iter = std::find(ids.begin(), ids.end(), id_from);
        if (iter == ids.end()) {
            // @todo inverses also need to be populated when multiple instances are added to a new file.
            // throw IfcParse::IfcException("Instance not found among inverses");
        } else {
            ids.erase(iter);
        }
        entity = entity->supertype();
    }

    std::vector<int>& ids = byref_excl_[inst->data().id()];
    std::vector<int>::iterator iter = std::find(ids.begin(), ids.end(), id_from);
    if (iter == ids.end()) {
        // @todo inverses also need to be populated when multiple instances are added to a new file.
        // throw IfcParse::IfcException("Instance not found among inverses");
    } else {
        ids.erase(iter);
    }
}

//
// Returns a string representation of the entity
// Note that this initializes the entity if it is not initialized
//
std::string IfcEntityInstanceData::toString(bool upper) const {
    if (attributes_ == 0) {
        load();
    }

    std::stringstream ss;
    ss.imbue(std::locale::classic());

    std::string dt;
    if (type_ != nullptr) {
        dt = type()->name();
        if (upper) {
            boost::to_upper(dt);
        }

        if ((type()->as_entity() != nullptr) || id_ != 0) {
            ss << "#" << id_ << "=";
        }
    }

    ss << dt << "(";

    for (size_t i = 0; i < getArgumentCount(); ++i) {
        if (i != 0) {
            ss << ",";
        }
        if (attributes_[i] == 0) {
            ss << "$";
        } else {
            ss << attributes_[i]->toString(upper);
        }
    }
    ss << ")";

    return ss.str();
}

void IfcEntityInstanceData::clearArguments() {
    if (attributes_ != NULL) {
        for (size_t i = 0; i < getArgumentCount(); ++i) {
            delete attributes_[i];
        }
        delete[] attributes_;
        attributes_ = NULL;
    }
}

IfcEntityInstanceData::~IfcEntityInstanceData() {
    clearArguments();
}

unsigned IfcEntityInstanceData::set_id(boost::optional<unsigned> i) {
    if (i) {
        return id_ = *i;
    }
    return id_ = file->FreshId();
}

//
// Returns the entities of Entity type that have this entity in their ArgumentList
//
aggregate_of_instance::ptr IfcEntityInstanceData::getInverse(const IfcParse::declaration* type, int attribute_index) const {
    static std::mutex mtx;
    std::lock_guard<std::mutex> lock(mtx);

    return file->getInverse(id_, type, attribute_index);
}

void IfcEntityInstanceData::load() const {
    static std::recursive_mutex mtx;
    std::lock_guard<std::recursive_mutex> lockk(mtx);

    Argument** tmp_data = nullptr;

    if (file->parsing_complete()) {
        // only when parsing is fully complete we need to seek to the instance, otherwise
        // we know the token cursor is currently at the keyword token
        file->seek_to(*this);
    } else {
        // Apparently the load() function assumes one token later after the opening parenthesis
        file->tokens->Next();
    }

    // type_ is 0 for header entities which have their size predetermined in code
    // in that we have attributes_ pre-constructed to the correct size in the constructor
    // in the other case load() will use a vector internally to grow to the size found in the file
    size_t n = file->load(id(), type_ != nullptr ? type_->as_entity() : nullptr, type_ != nullptr ? tmp_data : attributes_, getArgumentCount());
    if (n != getArgumentCount()) {
        Logger::Error("Wrong number of attributes on instance with id #" + std::to_string(id_) +
                      " at offset " + std::to_string(this->offset_in_file()) +
                      " expected " + std::to_string(getArgumentCount()) +
                      " got " + std::to_string(n));
    }

    file->try_read_semicolon();

    // @todo does this need to be atomic somehow?
    if (tmp_data != nullptr) {
        attributes_ = tmp_data;
    }
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

IfcEntityInstanceData::IfcEntityInstanceData(const IfcEntityInstanceData& data) {
    file = 0;
    type_ = data.type_;
    id_ = 0;

    const size_t count = data.getArgumentCount();

    // In order not to have the instance read from file
    attributes_ = new Argument*[count];

    for (unsigned int i = 0; i < count; ++i) {
        attributes_[i] = 0;
        this->setArgument(i, data.getArgument(i), get_argument_type(data.type(), i), true);
    }
}

static IfcParse::NullArgument static_null_attribute;

Argument* IfcEntityInstanceData::getArgument(size_t i) const {
    if (attributes_ == 0) {
        load();
    }
    if (i < getArgumentCount()) {
        if (attributes_[i] == nullptr) {
            return &static_null_attribute;
        }
        return attributes_[i];
    }
    throw IfcParse::IfcException("Attribute index out of range");
}

class unregister_inverse_visitor {
  private:
    IfcFile& file_;
    const IfcEntityInstanceData& data_;

  public:
    unregister_inverse_visitor(IfcFile& file, const IfcEntityInstanceData& data)
        : file_(file),
          data_(data) {}

    void operator()(IfcUtil::IfcBaseClass* inst, int index) {
        file_.unregister_inverse(data_.id(), data_.type()->as_entity(), inst, index);
    }
};

class register_inverse_visitor {
  private:
    IfcFile& file_;
    const IfcEntityInstanceData& data_;

  public:
    register_inverse_visitor(IfcFile& file, const IfcEntityInstanceData& data)
        : file_(file),
          data_(data) {}

    void operator()(IfcUtil::IfcBaseClass* inst, int index) {
        file_.register_inverse(data_.id(), data_.type()->as_entity(), inst, index);
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
    Argument* attribute_;
    IfcEntityInstanceData* data_;
    int attribute_index_;

    template <typename T>
    void apply_attribute_(T& t, Argument* attr, int index) const {
        if (!attr) {
            return;
        }

        if (attr->type() == IfcUtil::Argument_ENTITY_INSTANCE) {
            IfcUtil::IfcBaseClass* inst = *attr;
            t(inst, index);
        } else if (attr->type() == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
            aggregate_of_instance::ptr entity_list_attribute = *attr;
            for (aggregate_of_instance::it it = entity_list_attribute->begin(); it != entity_list_attribute->end(); ++it) {
                t(*it, index);
            }
        } else if (attr->type() == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
            aggregate_of_aggregate_of_instance::ptr entity_list_attribute = *attr;
            for (aggregate_of_aggregate_of_instance::outer_it it = entity_list_attribute->begin(); it != entity_list_attribute->end(); ++it) {
                for (aggregate_of_aggregate_of_instance::inner_it jt = it->begin(); jt != it->end(); ++jt) {
                    t(*jt, index);
                }
            }
        }
    };

  public:
    apply_individual_instance_visitor(Argument* attribute, int idx)
        : attribute_(attribute),
          data_(0),
          attribute_index_(idx) {}

    apply_individual_instance_visitor(IfcEntityInstanceData* data)
        : attribute_(0),
          data_(data) {}

    template <typename T>
    void apply(T& t) const {
        if (attribute_) {
            apply_attribute_(t, attribute_, attribute_index_);
        } else {
            for (size_t i = 0; i < data_->getArgumentCount(); ++i) {
                Argument* attr = data_->getArgument(i);
                apply_attribute_(t, attr, i);
            }
        }
    };
};

void IfcEntityInstanceData::setArgument(size_t i, Argument* a, IfcUtil::ArgumentType attr_type, bool make_copy) {
    if (attributes_ == 0) {
        load();
    }
    Argument* new_attribute = a;
    if (make_copy) {
        if (attr_type == IfcUtil::Argument_UNKNOWN) {
            attr_type = a->type();
        } else if (a->isNull()) {
            attr_type = IfcUtil::Argument_NULL;
        }

        IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();

        switch (attr_type) {
        case IfcUtil::Argument_NULL:
            copy->set(boost::blank());
            break;
        case IfcUtil::Argument_DERIVED:
            copy->set(IfcWrite::IfcWriteArgument::Derived());
            break;
        case IfcUtil::Argument_INT:
            copy->set(static_cast<int>(*a));
            break;
        case IfcUtil::Argument_BOOL:
            copy->set(static_cast<bool>(*a));
            break;
        case IfcUtil::Argument_LOGICAL: {
            boost::logic::tribool tb = *a;
            copy->set(tb);
            break;
        }
        case IfcUtil::Argument_DOUBLE:
            copy->set(static_cast<double>(*a));
            break;
        case IfcUtil::Argument_STRING:
            copy->set(static_cast<std::string>(*a));
            break;
        case IfcUtil::Argument_BINARY: {
            boost::dynamic_bitset<> attr_value = *a;
            copy->set(attr_value);
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_INT: {
            std::vector<int> attr_value = *a;
            copy->set(attr_value);
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_DOUBLE: {
            std::vector<double> attr_value = *a;
            copy->set(attr_value);
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_STRING: {
            std::vector<std::string> attr_value = *a;
            copy->set(attr_value);
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_BINARY: {
            std::vector<boost::dynamic_bitset<>> attr_value = *a;
            copy->set(attr_value);
            break;
        }
        case IfcUtil::Argument_ENUMERATION: {
            std::string enum_literal = a->toString();
            // Remove leading and trailing '.'
            enum_literal = enum_literal.substr(1, enum_literal.size() - 2);

            const IfcParse::enumeration_type* enum_type = type()->as_enumeration_type() != nullptr
                                                              ? type()->as_enumeration_type()
                                                              : type()->as_entity()->attribute_by_index(i)->type_of_attribute()->as_named_type()->declared_type()->as_enumeration_type();

            std::vector<std::string>::const_iterator it = std::find(
                enum_type->enumeration_items().begin(),
                enum_type->enumeration_items().end(),
                enum_literal);

            if (it == enum_type->enumeration_items().end()) {
                throw IfcParse::IfcException(enum_literal + " does not name a valid item for " + enum_type->name());
            }

            copy->set(IfcWrite::IfcWriteArgument::EnumerationReference(it - enum_type->enumeration_items().begin(), it->c_str()));
            break;
        }
        case IfcUtil::Argument_ENTITY_INSTANCE: {
            copy->set(static_cast<IfcUtil::IfcBaseClass*>(*a));
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
            aggregate_of_instance::ptr instances = *a;
            aggregate_of_instance::ptr mapped_instances(new aggregate_of_instance);
            // @todo mapped_instances are not actually mapped to the file using add().
            for (aggregate_of_instance::it it = instances->begin(); it != instances->end(); ++it) {
                mapped_instances->push(*it);
            }
            copy->set(mapped_instances);
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
            std::vector<std::vector<int>> attr_value = *a;
            copy->set(attr_value);
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
            std::vector<std::vector<double>> attr_value = *a;
            copy->set(attr_value);
            break;
        }
        case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
            aggregate_of_aggregate_of_instance::ptr instances = *a;
            aggregate_of_aggregate_of_instance::ptr mapped_instances(new aggregate_of_aggregate_of_instance);
            for (aggregate_of_aggregate_of_instance::outer_it it = instances->begin(); it != instances->end(); ++it) {
                std::vector<IfcUtil::IfcBaseClass*> inner;
                for (aggregate_of_aggregate_of_instance::inner_it jt = it->begin(); jt != it->end(); ++jt) {
                    inner.push_back(*jt);
                }
                mapped_instances->push(inner);
            }
            copy->set(mapped_instances);
            break;
        }
        case IfcUtil::Argument_EMPTY_AGGREGATE:
        case IfcUtil::Argument_AGGREGATE_OF_EMPTY_AGGREGATE: {
            IfcUtil::ArgumentType t2 = IfcUtil::from_parameter_type(type()->as_entity()->attribute_by_index(i)->type_of_attribute());
            delete copy;
            copy = 0;
            setArgument(i, a, t2, make_copy);
            break;
        }
        default:
        case IfcUtil::Argument_UNKNOWN:
            throw IfcParse::IfcException(std::string("Unknown attribute encountered: '") + a->toString() + "' at index '" + boost::lexical_cast<std::string>(i) + "'");
            break;
        }

        if (copy == nullptr) {
            return;
        }

        new_attribute = copy;
    }

    if (attributes_[i] != 0) {
        Argument* current_attribute = attributes_[i];
        if (this->file != nullptr) {

            // Deregister old attribute guid in file guid map.
            if (i == 0 && (this->type() != nullptr) && (this->file->ifcroot_type() != nullptr) && this->type()->is(*this->file->ifcroot_type())) {
                try {
                    auto guid = (std::string)*current_attribute;
                    auto it = this->file->internal_guid_map().find(guid);
                    if (it != this->file->internal_guid_map().end() && &it->second->data() == this) {
                        this->file->internal_guid_map().erase(it);
                    }
                } catch (IfcParse::IfcException& e) {
                    Logger::Error(e);
                }
            }

            // Deregister inverse indices in file
            unregister_inverse_visitor visitor(*this->file, *this);
            apply_individual_instance_visitor(current_attribute, i).apply(visitor);
        }
        delete attributes_[i];
    }

    if (this->file != nullptr) {
        // Register inverse indices in file
        register_inverse_visitor visitor(*this->file, *this);
        apply_individual_instance_visitor(new_attribute, i).apply(visitor);
    }

    attributes_[i] = new_attribute;

    // Register new attribute guid in guid map
    if (this->file != nullptr) {
        if (i == 0 && (this->type() != nullptr) && (this->file->ifcroot_type() != nullptr) && this->type()->is(*this->file->ifcroot_type())) {
            try {
                auto guid = (std::string)*new_attribute;
                auto it = this->file->internal_guid_map().find(guid);
                if (it != this->file->internal_guid_map().end()) {
                    Logger::Warning("Duplicate guid " + guid);
                }
                this->file->internal_guid_map()[guid] = this->file->instance_by_id_2(this->id());
            } catch (IfcParse::IfcException& e) {
                Logger::Error(e);
            }
        }
    }
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
    initialize_(new IfcSpfStream(path));
}
#endif

IfcFile::IfcFile(std::istream& stream, int length) {
    initialize_(new IfcSpfStream(stream, length));
}

IfcFile::IfcFile(void* data, int length) {
    initialize_(new IfcSpfStream(data, length));
}

IfcFile::IfcFile(IfcParse::IfcSpfStream* s) {
    initialize_(s);
}

IfcFile::IfcFile(const IfcParse::schema_definition* schema)
    : parsing_complete_(true),
      schema_(schema),
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

    // prevent heap allocations during parse
    internal_attribute_vector_.reserve(64);
    internal_attribute_vector_simple_type_.reserve(16);

    parsing_complete_ = false;
    MaxId = 0;
    tokens = 0;
    stream = 0;
    schema_ = 0;

    setDefaultHeaderValues();

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

    IfcEntityInstanceData* data;
    instance_storage_type instance = 0;

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

            data = new IfcEntityInstanceData(entity_type, this, current_id, token_stream[2].startPos);
            instance = instance_storage_type(schema()->instantiate(data));

            /// @todo Printing to stdout in a library class feels weird. Maybe move the progress prints to the client code?
            // Update the status after every 1000 instances parsed
            if (((++progress) % 1000) == 0) {
                std::stringstream ss;
                ss << "\r#" << current_id;
                Logger::Status(ss.str(), false);
            }

            if (!lazy_load_) {
                data->load();
            }

            if (instance->declaration().is(*ifcroot_type_)) {
                try {
                    const std::string guid = *instance->data().getArgument(0);
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

                bytype_excl_.insert({ ty, instance });

            for (;;) {
                bytype_.insert({ ty, instance });
                const IfcParse::declaration* pt = ty->as_entity()->supertype();
                if (pt != nullptr) {
                    ty = pt;
                } else {
                    break;
                }
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

    parsing_complete_ = true;

    return;
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

IfcFile::instance_storage_type IfcFile::addEntity(IfcUtil::IfcBaseClass* entity, int id) {
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

    // Obtain all forward references by a depth-first
    // traversal and add them to the file.
    if (parsing_complete_) {
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
    }

    instance_storage_type new_entity;

    // See whether the instance is already part of a file
    if (entity->data().file == 0) {
        // We can simply wrap it into a new smart pointer
        new_entity = instance_storage_type(entity);
    } else {
        if (entity->data().file == this) {
            if (entity->declaration().as_entity() == nullptr) {
                // While not a mapping that can be queried, we do need to free the instance later on
                byidentity_[entity->identity()] = instance_storage_type(entity);
            }

            // If it is part of this file
            // nothing else needs to be done.
            if constexpr (std::is_same_v<IfcFile::instance_storage_type, IfcUtil::IfcBaseClass*>) {
                return entity;
            } else {
                for (auto& x : byid_) {
                    if (&*x.second == entity) {
                        return x.second;
                    }
                }
                throw std::runtime_error("Internal error");
            }
        }

        // An instance is being added from another file. A copy of the
        // container and entity is created. The attribute references
        // need to be updated to point to instances in this file.
        IfcFile* other_file = entity->data().file;
        IfcEntityInstanceData* we = new IfcEntityInstanceData(entity->data());
        new_entity = instance_storage_type(schema()->instantiate(we));

        // In case an entity is added that contains geometry, the unit
        // information needs to be accounted for for IfcLengthMeasures.
        double conversion_factor = std::numeric_limits<double>::quiet_NaN();

        for (size_t i = 0; i < we->getArgumentCount(); ++i) {
            Argument* attr = we->getArgument(i);
            IfcUtil::ArgumentType attr_type = attr->type();

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
                entity_entity_map_t::const_iterator eit = entity_file_map_.find(((IfcUtil::IfcBaseClass*)(*attr))->identity());
                if (eit == entity_file_map_.end()) {
                    throw IfcParse::IfcException("Unable to map instance to file");
                }

                IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
                copy->set(&*eit->second);
                we->setArgument(i, copy);
            } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
                aggregate_of_instance::ptr instances = *attr;
                aggregate_of_instance::ptr new_instances(new aggregate_of_instance);
                for (aggregate_of_instance::it it = instances->begin(); it != instances->end(); ++it) {
                    entity_entity_map_t::const_iterator eit = entity_file_map_.find((*it)->identity());
                    if (eit == entity_file_map_.end()) {
                        throw IfcParse::IfcException("Unable to map instance to file");
                    }
                    new_instances->push(&*eit->second);
                }

                IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
                copy->set(new_instances);
                we->setArgument(i, copy);
            } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
                aggregate_of_aggregate_of_instance::ptr instances = *attr;
                aggregate_of_aggregate_of_instance::ptr new_instances(new aggregate_of_aggregate_of_instance);
                for (aggregate_of_aggregate_of_instance::outer_it it = instances->begin(); it != instances->end(); ++it) {
                    std::vector<IfcUtil::IfcBaseClass*> list;
                    for (aggregate_of_aggregate_of_instance::inner_it jt = it->begin(); jt != it->end(); ++jt) {
                        entity_entity_map_t::const_iterator eit = entity_file_map_.find((*jt)->identity());
                        if (eit == entity_file_map_.end()) {
                            throw IfcParse::IfcException("Unable to map instance to file");
                        }
                        list.push_back(&*eit->second);
                    }
                    new_instances->push(list);
                }

                IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
                copy->set(new_instances);
                we->setArgument(i, copy);
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
                    double v = *attr;
                    v *= conversion_factor;

                    IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
                    copy->set(v);
                    we->setArgument(i, copy);
                } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
                    std::vector<double> v = *attr;
                    for (std::vector<double>::iterator it = v.begin(); it != v.end(); ++it) {
                        (*it) *= conversion_factor;
                    }

                    IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
                    copy->set(v);
                    we->setArgument(i, copy);
                } else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
                    std::vector<std::vector<double>> v = *attr;
                    for (std::vector<std::vector<double>>::iterator it = v.begin(); it != v.end(); ++it) {
                        std::vector<double>& v2 = (*it);
                        for (std::vector<double>::iterator jt = v2.begin(); jt != v2.end(); ++jt) {
                            (*jt) *= conversion_factor;
                        }
                    }

                    IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
                    copy->set(v);
                    we->setArgument(i, copy);
                }
            }
        }

        // A new entity instance name is generated and
        // the instance is pointed to this file.
        we->file = this;
        if (we->type()->as_entity() != nullptr) {
            if (id == -1) {
                we->set_id(FreshId());
            } else {
                we->set_id((unsigned int)id);
                if ((unsigned)id > MaxId) {
                    MaxId = (unsigned)id;
                }
            }
        }

        entity_file_map_.insert(entity_entity_map_t::value_type(entity->identity(), &*new_entity));
    }

    // For subtypes of IfcRoot, the GUID mapping needs to be updated.
    if (new_entity->declaration().is(*ifcroot_type_)) {
        try {
            const std::string guid = *new_entity->data().getArgument(0);
            if (byguid_.find(guid) != byguid_.end()) {
                std::stringstream ss;
                ss << "Overwriting entity with guid " << guid;
                Logger::Message(Logger::LOG_WARNING, ss.str());
            }
            byguid_[guid] = new_entity;
        } catch (const IfcException& ex) {
            Logger::Message(Logger::LOG_ERROR, ex.what());
        }
    }

    // The mapping by entity type is updated.
    const IfcParse::declaration* ty = &new_entity->declaration();

    if (ty->as_entity() != nullptr) {
        bytype_excl_.insert({ ty, new_entity });
    }

    for (; ty->as_entity() != nullptr;) {
        bytype_.insert({ ty, new_entity });

        const IfcParse::declaration* pt = ty->as_entity()->supertype();
        if (pt != nullptr) {
            ty = pt;
        } else {
            break;
        }
    }

    if (ty->as_entity() != nullptr) {
        int new_id = -1;
        if (new_entity->data().file == nullptr) {
            // For newly created entities ensure a valid ENTITY_INSTANCE_NAME is set
            new_entity->data().file = this;
            boost::optional<unsigned> id_value;
            if (id != -1) {
                id_value = (unsigned)id;
                if ((unsigned)id > MaxId) {
                    MaxId = (unsigned)id;
                }
            }
            new_id = new_entity->data().set_id(id_value);
        } else {
            new_id = new_entity->data().id();
        }

        if (byid_.find(new_id) != byid_.end()) {
            // This should not happen
            std::stringstream ss;
            ss << "Overwriting entity with id " << new_id;
            Logger::Message(Logger::LOG_WARNING, ss.str());
        }
        // The mapping by entity instance name is updated.
        byid_[new_id] = new_entity;
    } else if (new_entity->data().file == nullptr) {
        // For non-entity instances, no mappings are updated, but the file
        // pointer has to be set, so that actual copies are created in subsequent
        // times.
        new_entity->data().file = this;

        // While not a mapping that can be queried, we do need to free the instance
        byidentity_[new_entity->identity()] = new_entity;
    }

    if (parsing_complete_ && (ty->as_entity() != nullptr)) {
        build_inverses_(&*new_entity);
    }

    return new_entity;
}

void IfcFile::removeEntity(IfcUtil::IfcBaseClass* entity) {
    const unsigned id = entity->data().id();

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

                if (std::find(batch_deletion_ids_.begin(), batch_deletion_ids_.end(), related_instance->data().id()) != batch_deletion_ids_.end()) {
                    continue;
                }

                for (size_t i = 0; i < related_instance->data().getArgumentCount(); ++i) {
                    Argument* attr = related_instance->data().getArgument(i);
                    if (attr->isNull()) {
                        continue;
                    }

                    IfcUtil::ArgumentType attr_type = attr->type();
                    switch (attr_type) {
                    case IfcUtil::Argument_ENTITY_INSTANCE: {
                        IfcUtil::IfcBaseClass* instance_attribute = *attr;
                        if (instance_attribute == entity) {
                            IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
                            copy->set(boost::blank());
                            related_instance->data().setArgument(i, copy);
                        }
                    } break;
                    case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
                        aggregate_of_instance::ptr instance_list = *attr;
                        if (instance_list->contains(entity)) {
                            IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
                            instance_list->remove(entity);
                            if ((instance_list->size() == 0U) && related_instance->declaration().as_entity()->attribute_by_index(i)->optional()) {
                                // @todo we can also check the lower bound of the attribute type before setting to null.
                                copy->set(boost::blank());
                            } else {
                                copy->set(instance_list);
                            }
                            related_instance->data().setArgument(i, copy);
                        }
                    } break;
                    case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
                        aggregate_of_aggregate_of_instance::ptr instance_list_list = *attr;
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

                            IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
                            copy->set(new_list);
                            related_instance->data().setArgument(i, copy);
                        }
                    } break;
                    default:
                        break;
                    }
                }
            }
        }

        if (!batch_mode_) {
            byref_.erase(
                byref_.lower_bound({id, -1, -1}),
                byref_.upper_bound({id, std::numeric_limits<int>::max(), std::numeric_limits<int>::max()}));

            byref_excl_.erase(id);

            // This is based on traversal which needs instances to still be contained in the map.
            // another option would be to keep byid intact for the remainder of this loop
            aggregate_of_instance::ptr entity_attributes = traverse(entity, 1);
            for (aggregate_of_instance::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
                IfcUtil::IfcBaseClass* entity_attribute = *it;
                if (entity_attribute == entity) {
                    continue;
                }
                const unsigned int name = entity_attribute->data().id();
                // Do not update inverses for simple types (which have id()==0 in IfcOpenShell).
                if (name != 0) {
                    {
                        auto lower = byref_.lower_bound({name, -1, -1});
                        auto upper = byref_.upper_bound({name, std::numeric_limits<int>::max(), std::numeric_limits<int>::max()});

                        for (auto byref_it = lower; byref_it != upper; ++byref_it) {
                            auto& ids = byref_it->second;
                            ids.erase(std::remove(ids.begin(), ids.end(), id), ids.end());
                        }
                    }
                    {
                        auto byref_it = byref_excl_.find(name);
                        if (byref_it != byref_excl_.end()) {
                            auto& ids = byref_it->second;
                            ids.erase(std::remove(ids.begin(), ids.end(), id), ids.end());
                        }
                    }
                }
            }
        }

        if (entity->declaration().is(*ifcroot_type_) && !entity->data().getArgument(0)->isNull()) {
            const std::string global_id = *entity->data().getArgument(0);
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
            auto instances_of_same_type = bytype_excl_.equal_range(ty);
            for (auto it = instances_of_same_type.first; it != instances_of_same_type.second;) {
                if (&*it->second == entity) {
                    it = bytype_excl_.erase(it);
                } else {
                    ++it;
                }
            }
        }

        for (;;) {
            auto instances_of_same_type = bytype_.equal_range(ty);
            for (auto it = instances_of_same_type.first; it != instances_of_same_type.second;) {
                if (&*it->second == entity) {
                    it = bytype_.erase(it);
                } else {
                    ++it;
                }
            }

            const IfcParse::declaration* pt = ty->as_entity()->supertype();
            if (pt != nullptr) {
                ty = pt;
            } else {
                break;
            }
        }

        // entity_file_map is in place to prevent duplicate definitions with usage of add().
        // Upon deletion the pairs need to be erased.
        for (auto it = entity_file_map_.begin(); it != entity_file_map_.end();) {
            if (&*it->second == entity) {
                it = entity_file_map_.erase(it);
            } else {
                ++it;
            }
        }

        if constexpr (std::is_same_v<IfcFile::instance_storage_type, IfcUtil::IfcBaseClass*>) {
            delete entity;
        }
    }

    if (batch_mode_) {
        for (auto it = byref_.begin(); it != byref_.end();) {
            bool do_delete = batch_deletion_ids_.get<1>().find(std::get<INSTANCE_ID>(it->first)) != batch_deletion_ids_.get<1>().end();
            if (!do_delete) {
                it->second.erase(std::remove_if(it->second.begin(), it->second.end(), [this](int x) {
                                     return batch_deletion_ids_.get<1>().find(x) != batch_deletion_ids_.get<1>().end();
                                 }),
                                 it->second.end());
                do_delete = it->second.empty();
            }
            if (do_delete) {
                it = byref_.erase(it);
            } else {
                ++it;
            }
        }

        for (auto it = byref_excl_.begin(); it != byref_excl_.end();) {
            bool do_delete = batch_deletion_ids_.get<1>().find(it->first) != batch_deletion_ids_.get<1>().end();
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

IfcFile::type_iterator_range_t IfcFile::instances_by_type_range(const IfcParse::declaration* t) {
    return bytype_.equal_range(t);
}

IfcFile::type_iterator_range_t IfcFile::instances_by_type_excl_subtypes_range(const IfcParse::declaration* t) {
    return bytype_.equal_range(t);
}

IfcFile::type_iterator_range_t IfcFile::instances_by_type_range(const std::string& t) {
    return instances_by_type_range(schema()->declaration_by_name(t));
}

IfcFile::type_iterator_range_t IfcFile::instances_by_type_excl_subtypes_range(const std::string& t) {
    return instances_by_type_excl_subtypes_range(schema()->declaration_by_name(t));
}

aggregate_of_instance::ptr IfcFile::instances_by_reference(int t) {
    aggregate_of_instance::ptr ret(new aggregate_of_instance);
    for (auto& i : byref_excl_[t]) {
        ret->push(instance_by_id(i));
    }
    return ret;
}

IfcUtil::IfcBaseClass* IfcFile::instance_by_id(int id) {
    entity_by_id_t::const_iterator it = byid_.find(id);
    if (it == byid_.end()) {
        throw IfcException("Instance #" + boost::lexical_cast<std::string>(id) + " not found");
    }
    return &*it->second;
}

IfcFile::instance_storage_type IfcFile::instance_by_id_2(int id) {
    entity_by_id_t::const_iterator it = byid_.find(id);
    if (it == byid_.end()) {
        throw IfcException("Instance #" + boost::lexical_cast<std::string>(id) + " not found");
    }
    return it->second;
}

IfcFile::instance_storage_type IfcFile::instance_by_guid(const std::string& guid) {
    entity_by_guid_t::const_iterator it = byguid_.find(guid);
    if (it == byguid_.end()) {
        throw IfcException("Instance with GlobalId '" + guid + "' not found");
    }
    return it->second;
}

// FIXME: Test destructor to delete entity and arg allocations
IfcFile::~IfcFile() {
    if constexpr (std::is_same_v<IfcFile::instance_storage_type, IfcUtil::IfcBaseClass*>) {
        std::set<IfcFile::instance_storage_type> entities_to_delete;
        for (const auto& pair : byid_) {
            entities_to_delete.insert(pair.second);
        }
        for (const auto& pair : byidentity_) {
            entities_to_delete.insert(pair.second);
        }
        for (auto entity : entities_to_delete) {
            delete &*entity;
        }
    }
    delete stream;
    delete tokens;
}

IfcFile::entity_by_id_t::const_iterator IfcFile::begin() const {
    return byid_.begin();
}

IfcFile::entity_by_id_t::const_iterator IfcFile::end() const {
    return byid_.end();
}

IfcFile::type_iterator<IfcFile::entities_by_type_t::key_type> IfcFile::types_begin() const {
    return bytype_excl_.begin();
}

IfcFile::type_iterator<IfcFile::entities_by_type_t::key_type> IfcFile::types_end() const {
    return bytype_excl_.end();
}

IfcFile::type_iterator<IfcFile::entities_by_type_t::key_type> IfcFile::types_incl_super_begin() const {
    return bytype_.begin();
}

IfcFile::type_iterator<IfcFile::entities_by_type_t::key_type> IfcFile::types_incl_super_end() const {
    return bytype_.end();
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

    typedef std::vector<std::pair<unsigned int, IfcParse::IfcFile::instance_storage_type>> vector_t;
    vector_t sorted(file.begin(), file.end());
    std::sort(sorted.begin(), sorted.end(), id_instance_pair_sorter());

    for (vector_t::const_iterator it = sorted.begin(); it != sorted.end(); ++it) {
        auto& e = it->second;
        if (e->declaration().as_entity() != nullptr) {
            out << e->data().toString(true) << ";" << std::endl;
        }
    }

    out << "ENDSEC;" << std::endl;
    out << "END-ISO-10303-21;" << std::endl;

    return out;
}

std::string IfcFile::createTimestamp() const {
    char buf[255];

    time_t t;
    time(&t);

    struct tm* ti = localtime(&t);

    std::string result = "";
    if (strftime(buf, 255, "%Y-%m-%dT%H:%M:%S", ti) != 0U) {
        result = std::string(buf);
    }

    return result;
}

std::vector<int> IfcFile::get_inverse_indices(int instance_id) {
    std::vector<int> return_value;

    auto lower = byref_.lower_bound({instance_id, -1, -1});
    auto upper = byref_.upper_bound({instance_id, std::numeric_limits<int>::max(), std::numeric_limits<int>::max()});

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
        auto it = mapping.find(ref->data().id());
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

    if (attribute_index == -1) {
        auto lower = byref_.lower_bound({instance_id, type->index_in_schema(), -1});
        auto upper = byref_.upper_bound({instance_id, type->index_in_schema(), std::numeric_limits<int>::max()});

        for (auto it = lower; it != upper; ++it) {
            for (auto& i : it->second) {
                return_value->push(instance_by_id(i));
            }
        }
    } else {
        auto it = byref_.find({instance_id, type->index_in_schema(), attribute_index});
        if (it != byref_.end()) {
            for (auto& i : it->second) {
                return_value->push(instance_by_id(i));
            }
        }
    }

    return return_value;
}

int IfcFile::getTotalInverses(int instance_id) {
    return byref_excl_[instance_id].size();
}

void IfcFile::setDefaultHeaderValues() {
    const std::string empty_string = "";
    std::vector<std::string> file_description, schema_identifiers, empty_vector;

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

    auto projects = instances_by_type_range(schema()->declaration_by_name("IfcProject"));
    if (std::distance(projects.first, projects.second) == 0) {
        try {
            projects = instances_by_type_range(schema()->declaration_by_name("IfcContext"));
        } catch (IfcException& e) {
        }
    }

    if (std::distance(projects.first, projects.second) == 1) {
        auto project = *projects.first;

        IfcUtil::IfcBaseClass* unit_assignment = *project->data().getArgument(
            project->declaration().as_entity()->attribute_index("UnitsInContext"));

        aggregate_of_instance::ptr units = *unit_assignment->data().getArgument(
            unit_assignment->declaration().as_entity()->attribute_index("Units"));

        for (aggregate_of_instance::it it = units->begin(); it != units->end(); ++it) {
            IfcUtil::IfcBaseClass* unit = *it;
            if (unit->declaration().is("IfcNamedUnit")) {
                const std::string file_unit_type = *unit->data().getArgument(
                    unit->declaration().as_entity()->attribute_index("UnitType"));

                if (file_unit_type != unit_type) {
                    continue;
                }

                IfcUtil::IfcBaseClass* siunit = 0;
                if (unit->declaration().is("IfcConversionBasedUnit")) {
                    IfcUtil::IfcBaseClass* mu = *unit->data().getArgument(
                        unit->declaration().as_entity()->attribute_index("ConversionFactor"));

                    IfcUtil::IfcBaseClass* vlc = *mu->data().getArgument(
                        mu->declaration().as_entity()->attribute_index("ValueComponent"));

                    IfcUtil::IfcBaseClass* unc = *mu->data().getArgument(
                        mu->declaration().as_entity()->attribute_index("UnitComponent"));

                    return_value.second *= static_cast<double>(*vlc->data().getArgument(0));
                    return_value.first = unit;

                    if (unc->declaration().is("IfcSIUnit")) {
                        siunit = unc;
                    }

                } else if (unit->declaration().is("IfcSIUnit")) {
                    return_value.first = siunit = unit;
                }

                if (siunit != nullptr) {
                    Argument* prefix = siunit->data().getArgument(
                        siunit->declaration().as_entity()->attribute_index("Prefix"));

                    if (!prefix->isNull()) {
                        return_value.second *= IfcSIPrefixToValue(*prefix);
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
            unsigned entity_attribute_id = attr->data().id();
            const auto* decl = inst->declaration().as_entity();
            byref_excl_[entity_attribute_id].push_back(inst->data().id());
            while (decl != nullptr) {
                byref_[{entity_attribute_id, decl->index_in_schema(), idx}].push_back(inst->data().id());
                decl = decl->supertype();
            }
        }
    };

    apply_individual_instance_visitor(&inst->data()).apply(fn);
}

void IfcParse::IfcFile::build_inverses() {
    for (const auto& pair : *this) {
        build_inverses_(&*pair.second);
    }
}

/// Compatibility functions that take the ranges from above and turn into an aggregate
aggregate_of_instance::ptr IfcParse::IfcFile::instances_by_type(const IfcParse::declaration* decl) {
    aggregate_of_instance::ptr aggr(new aggregate_of_instance);
    for (auto& inst : boost::make_iterator_range(instances_by_type_range(decl))) {
        aggr->push(&*inst);
    }
    return aggr;
}
aggregate_of_instance::ptr IfcParse::IfcFile::instances_by_type_excl_subtypes(const IfcParse::declaration* decl) {
    aggregate_of_instance::ptr aggr(new aggregate_of_instance);
    for (auto& inst : boost::make_iterator_range(instances_by_type_excl_subtypes_range(decl))) {
        aggr->push(&*inst);
    }
    return aggr;
}
aggregate_of_instance::ptr IfcParse::IfcFile::instances_by_type(const std::string& type) {
    return instances_by_type(schema()->declaration_by_name(type));
}
aggregate_of_instance::ptr IfcParse::IfcFile::instances_by_type_excl_subtypes(const std::string& type) {
    return instances_by_type_excl_subtypes(schema()->declaration_by_name(type));
}


std::atomic_uint32_t IfcUtil::IfcBaseClass::counter_(0);

bool IfcParse::IfcFile::lazy_load_ = true;
bool IfcParse::IfcFile::guid_map_ = true;

template <typename T>
void IfcUtil::IfcBaseClass::set_value(int index, const T& value) {
    IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();
    attr->set(value);
    data_->setArgument(index, attr);
}

void IfcUtil::IfcBaseClass::unset_value(int index) {
    IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();
    data_->setArgument(index, attr);
}

template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<int>(int index, const int& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<bool>(int index, const bool& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<boost::logic::tribool>(int index, const boost::logic::tribool& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<double>(int index, const double& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<std::string>(int index, const std::string& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<boost::dynamic_bitset<>>(int index, const boost::dynamic_bitset<>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<IfcWrite::IfcWriteArgument::EnumerationReference>(int index, const IfcWrite::IfcWriteArgument::EnumerationReference& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<IfcUtil::IfcBaseClass*>(int index, IfcUtil::IfcBaseClass* const& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<std::vector<int>>(int index, const std::vector<int>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<std::vector<double>>(int index, const std::vector<double>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<std::vector<std::string>>(int index, const std::vector<std::string>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<std::vector<boost::dynamic_bitset<>>>(int index, const std::vector<boost::dynamic_bitset<>>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<aggregate_of_instance::ptr>(int index, const aggregate_of_instance::ptr& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<std::vector<std::vector<int>>>(int index, const std::vector<std::vector<int>>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<std::vector<std::vector<double>>>(int index, const std::vector<std::vector<double>>& value);
template void IFC_PARSE_API IfcUtil::IfcBaseClass::set_value<aggregate_of_aggregate_of_instance::ptr>(int index, const aggregate_of_aggregate_of_instance::ptr& value);
