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

#include "../ifcparse/IfcCharacterDecoder.h"
#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcSpfStream.h"
#include "../ifcparse/IfcFile.h"
#include "../ifcparse/IfcSIPrefix.h"
#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/utils.h"

#ifdef USE_MMAP
#include <boost/filesystem/path.hpp>
#endif

#include <set>
#include <ctime>
#include <mutex>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <algorithm>

#include <boost/circular_buffer.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/math/special_functions/fpclassify.hpp>

#define PERMISSIVE_FLOAT

using namespace IfcParse;

// A static locale for the real number parser. strtod() is locale-dependent, causing issues 
// in locales that have ',' as a decimal separator. Therefore the non standard _strtod_l() / 
// strtod_l() is used and a reference to the "C" locale is obtained here. The alternative is 
// to use std::istringstream::imbue(std::locale::classic()), but there are subtleties in 
// parsing in MSVC2010 and it appears to be much slower. 
#if defined(_MSC_VER)

static _locale_t locale = (_locale_t) 0;
void init_locale() {
	if (locale == (_locale_t) 0) {
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
IfcSpfStream::IfcSpfStream(const std::string& fn, bool mmap)
#else
IfcSpfStream::IfcSpfStream(const std::string& fn)
#endif
	: stream(0)
	, buffer(0)
	, valid(false)
	, eof(false)
{
#ifdef _MSC_VER
	std::wstring fn_ws = IfcUtil::path::from_utf8(fn);
	const wchar_t* fn_wide = fn_ws.c_str();

#ifdef USE_MMAP
	if (mmap) {
		mfs = boost::iostreams::mapped_file_source(boost::filesystem::wpath(fn_wide));
	} else {
#endif
		stream = _wfopen(fn_wide, L"rb");
#ifdef USE_MMAP	
	}
#endif

#else

#ifdef USE_MMAP
	if (mmap) {
		mfs = boost::iostreams::mapped_file_source(fn);
	} else {
#endif
		stream = fopen(fn.c_str(), "rb");
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
		buffer = mfs.data();
		ptr = 0;
		len = mfs.size();
	} else {
#endif
		if (stream == NULL) {
			return;
		}

		valid = true;
		fseek(stream, 0, SEEK_END);
		size = (unsigned int)ftell(stream);
		rewind(stream);
		char* buffer_rw = new char[size];
		len = (unsigned int)fread(buffer_rw, 1, size, stream);
		buffer = buffer_rw;
		eof = len == 0;
		ptr = 0;
		fclose(stream);
#ifdef USE_MMAP	
	}
#endif
}

IfcSpfStream::IfcSpfStream(std::istream& f, int l)
	: stream(0)
	, buffer(0)
{
	eof = false;
	size = l;
	char* buffer_rw = new char[size];
	f.read(buffer_rw,size);
	buffer = buffer_rw;
	valid = f.gcount() == size;
	ptr = 0;
	len = l;	
}

IfcSpfStream::IfcSpfStream(void* data, int l)
	: stream(0)
	, buffer(0)
{
	eof = false;
	size = l;
	buffer = (char*) data;
	valid = true;
	ptr = 0;
	len = l;
}

IfcSpfStream::~IfcSpfStream()
{
	Close();
}

void IfcSpfStream::Close() {
#ifdef USE_MMAP
	if (mfs.is_open()) {
		mfs.close();
		return;
	}
#endif
	delete[] buffer;
}

//
// Seeks an arbitrary position in the file
//
void IfcSpfStream::Seek(unsigned int o) {
	ptr = o;
	if (ptr >= len) throw IfcException("Reading outside of file limits");
	eof = false;
}

//
// Returns the character at the cursor
//
char IfcSpfStream::Peek() {
	return buffer[ptr];
}

//
// Returns the character at specified offset
//
char IfcSpfStream::Read(unsigned int o) {
	return buffer[o];
}

//
// Returns the cursor position
//
unsigned int IfcSpfStream::Tell() {
	return ptr;
}

//
// Increments cursor and reads new chunk if necessary
//
void IfcSpfStream::Inc() {
	if ( ++ptr == len ) { 
		eof = true;
		return;
	}
	const char current = IfcSpfStream::Peek();
	if (current == '\n' || current == '\r') {
		// NB this is recursive. It might as well be a loop.
		IfcSpfStream::Inc();
	}
}

IfcSpfLexer::IfcSpfLexer(IfcParse::IfcSpfStream *s, IfcParse::IfcFile* f) {
	file = f;
	stream = s;
	decoder = new IfcCharacterDecoder(s);
}

IfcSpfLexer::~IfcSpfLexer() {
	delete decoder;
}

unsigned int IfcSpfLexer::skipWhitespace() {
	unsigned int n = 0;
	while ( !stream->eof ) {
		char c = stream->Peek();
		if ( (c == ' ' || c == '\r' || c == '\n' || c == '\t' ) ) {
			stream->Inc();
			++n;
		}
		else break;
	}
	return n;
}

unsigned int IfcSpfLexer::skipComment() {
	char c = stream->Peek();
	if (c != '/') return 0;
	stream->Inc();
	c = stream->Peek();
	if (c != '*') {
		stream->Seek(stream->Tell() - 1);
		return 0;
	}
	unsigned int n = 2;
	char p = 0;
	while ( !stream->eof ) {
		c = stream->Peek();
		stream->Inc();
		++ n;
		if (c == '/' && p == '*') break;
		p = c;
	}
	return n;
}

//
// Returns the offset of the current Token and moves cursor to next
//
Token IfcSpfLexer::Next() {

	if ( stream->eof ) return NoneTokenPtr();

	while (skipWhitespace() || skipComment()) {}
	
	if ( stream->eof ) return NoneTokenPtr();
	unsigned int pos = stream->Tell();

	char c = stream->Peek();
	
	// If the cursor is at [()=,;$*] we know token consists of single char
	if (c == '(' || c == ')' || c == '=' || c == ',' || c == ';' || c == '$' || c == '*') {
		stream->Inc();
		return OperatorTokenPtr(this, pos, pos+1);
	}

	int len = 0;

	while ( ! stream->eof ) {

		// Read character and increment pointer if not starting a new token
		c = stream->Peek();
		if ( len && (c == '(' || c == ')' || c == '=' || c == ',' || c == ';' || c == '/') ) break;
		stream->Inc();
		len ++;

		// If a string is encountered defer processing to the IfcCharacterDecoder
		if ( c == '\'' ) decoder->skip();
	}
	if ( len ) return GeneralTokenPtr(this, pos, stream->Tell());
	else return NoneTokenPtr();
}

bool IfcSpfStream::is_eof_at(unsigned int local_ptr) {
	return local_ptr >= len;
}

void IfcSpfStream::increment_at(unsigned int& local_ptr) {
	if (++local_ptr == len) {
		return;
	}
	const char current = IfcSpfStream::peek_at(local_ptr);
	if (current == '\n' || current == '\r') IfcSpfStream::increment_at(local_ptr);
}

char IfcSpfStream::peek_at(unsigned int local_ptr) {
	return buffer[local_ptr];
}

//
// Reads a std::string from the file at specified offset
// Omits whitespace and comments
//
void IfcSpfLexer::TokenString(unsigned int offset, std::string &buffer) {
	buffer.clear();
	while (!stream->is_eof_at(offset)) {
		char c = stream->peek_at(offset);
		if ( buffer.size() && (c == '(' || c == ')' || c == '=' || c == ',' || c == ';' || c == '/') ) break;
		stream->increment_at(offset);
		if ( c == ' ' || c == '\r' || c == '\n' || c == '\t' ) continue;
		else if ( c == '\'' ) {
			// todo, make decoder use local offset ptr
			buffer = decoder->get(offset);
			break;
		}
		else buffer.push_back(c);
	}
}

//Note: according to STEP standard, there may be newlines in tokens
inline void RemoveTokenSeparators(IfcSpfStream* stream, unsigned start, unsigned end, std::string &oDestination) {
	oDestination.clear();
	for (unsigned i = start; i < end; i++) {
		char c = stream->Read(i);
		if (c == ' ' || c == '\r' || c == '\n' || c == '\t')
			continue;
		oDestination += c;
	}
}

bool ParseInt(const char *pStart, int &val) {
	char* pEnd;
	long result = strtol(pStart, &pEnd, 10);
	if (*pEnd != 0)
		return false;
	val = (int)result;
	return true;
}

bool ParseFloat(const char *pStart, double &val) {
	char* pEnd;
#ifdef _MSC_VER
	double result = _strtod_l(pStart, &pEnd, locale);
#else
	double result = strtod_l(pStart, &pEnd, locale);
#endif
	if (*pEnd != 0)
		return false;
	val = result;
	return true;
}

bool ParseBool(const char *pStart, bool &val) {
	if (strlen(pStart) != 3 || pStart[0] != '.' || pStart[2] != '.')
		return false;
	char mid = pStart[1];
	/// @todo https://github.com/IfcOpenShell/IfcOpenShell/issues/95
	if (!(mid == 'T' || mid == 'F' || mid == 'U'))
		return false;
	val = (mid == 'T');
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
	std::string &tokenStr = lexer->GetTempString();
	RemoveTokenSeparators(lexer->stream, start, end, tokenStr);
	
	//determine type of the token
	char first = lexer->stream->Read(start);
	if (first == '#') {
		token.type = Token_IDENTIFIER;
		if (!ParseInt(tokenStr.c_str() + 1, token.value_int))
			throw IfcException("Identifier token as not integer");
	}
	else if (first == '\'')
		token.type = Token_STRING;
	else if (first == '.') {
		token.type = Token_ENUMERATION;
		if (ParseBool(tokenStr.c_str(), token.value_bool)) //bool is also enumeration
			token.type = Token_BOOL;
	}
	else if (first == '"')
		token.type = Token_BINARY;
	else if (ParseInt(tokenStr.c_str(), token.value_int))
		token.type = Token_INT;
	else if (ParseFloat(tokenStr.c_str(), token.value_double))
		token.type = Token_FLOAT;
	else
		token.type = Token_KEYWORD;

	return token;
}
Token IfcParse::NoneTokenPtr() { return Token(); }


bool TokenFunc::isOperator(const Token& t) {
	return t.type == Token_OPERATOR;
}

bool TokenFunc::isOperator(const Token& t, char op) {
	return t.type == Token_OPERATOR && t.value_char == op;
}

bool TokenFunc::isIdentifier(const Token& t) {
	return t.type == Token_IDENTIFIER;
}

bool TokenFunc::isString(const Token& t) {
	return t.type == Token_STRING;
}

bool TokenFunc::isEnumeration(const Token& t) {
	return t.type == Token_ENUMERATION || t.type == Token_BOOL;
}

bool TokenFunc::isBinary(const Token& t) {
	return t.type == Token_BINARY;
}

bool TokenFunc::isKeyword(const Token& t) {
	return t.type == Token_KEYWORD;
}

bool TokenFunc::isInt(const Token& t) {
	return t.type == Token_INT;
}

bool TokenFunc::isBool(const Token& t) {
	return t.type == Token_BOOL;
}

bool TokenFunc::isFloat(const Token& t) {
#ifdef PERMISSIVE_FLOAT
	/// NB: We are being more permissive here then allowed by the standard
	return t.type == Token_FLOAT || t.type == Token_INT;
#else
	return t.type == Token_FLOAT;
#endif
}

int TokenFunc::asInt(const Token& t) {
	if (t.type != Token_INT) {
		throw IfcInvalidTokenException(t.startPos, toString(t), "integer");
	}
	return t.value_int;
}

int TokenFunc::asIdentifier(const Token& t) {
	if (t.type != Token_IDENTIFIER) {
		throw IfcInvalidTokenException(t.startPos, toString(t), "instance name");
	}
	return t.value_int;
}

bool TokenFunc::asBool(const Token& t) {
	if (t.type != Token_BOOL) {
		throw IfcInvalidTokenException(t.startPos, toString(t), "boolean");
	}
	return t.value_bool;
}

double TokenFunc::asFloat(const Token& t) {
#ifdef PERMISSIVE_FLOAT
	if (t.type == Token_INT) {
		/// NB: We are being more permissive here then allowed by the standard
		return t.value_int;
	} else // ----> continues beyond preprocessor directive
#endif
	if (t.type == Token_FLOAT) {
		return t.value_double;
	} else {
		throw IfcInvalidTokenException(t.startPos, toString(t), "real");
	}
}

const std::string &TokenFunc::asStringRef(const Token& t) {
    if (t.type == Token_NONE) {
        throw IfcParse::IfcException("Null token encountered, premature end of file?");
    }
	std::string &str = t.lexer->GetTempString();
	t.lexer->TokenString(t.startPos, str);
	if ((isString(t) || isEnumeration(t) || isBinary(t)) && !str.empty()) {
		//remove start+end characters in-place
		str.erase(str.end()-1);
		str.erase(str.begin());
	}
	return str;
}

std::string TokenFunc::asString(const Token& t) {
	if (isString(t) || isEnumeration(t) || isBinary(t)) {
		return asStringRef(t);
	} else {
		throw IfcInvalidTokenException(t.startPos, toString(t), "string");
	}
}

boost::dynamic_bitset<> TokenFunc::asBinary(const Token& t) {
	const std::string &str = asStringRef(t);
	if (str.size() < 1) {
		throw IfcException("Token is not a valid binary sequence");
	}
	
	std::string::const_iterator it = str.begin();
	int n = *it - '0';
	if ((n < 0 || n > 3) || (str.size() == 1 && n != 0)) {
		throw IfcException("Token is not a valid binary sequence");
	}

	++it;
	unsigned i = ((unsigned)str.size()-1) * 4 - n;
	boost::dynamic_bitset<> bitset(i);	

	for(; it != str.end(); ++it) {
		const std::string::value_type& c = *it;
		int value = (c < 'A') ? (c - '0') : (c - 'A' + 10);
		for (unsigned j = 0; j < 4; ++j) {
			if (i-- == 0) break;
			if (value & (1 << (3-j))) {
				bitset.set(i);
			}			
		}
	}

	return bitset;
}

std::string TokenFunc::toString(const Token& t) {
	std::string result;
	t.lexer->TokenString(t.startPos, result);
	return result;
}


TokenArgument::TokenArgument(const Token& t) {
	token = t;
}

EntityArgument::EntityArgument(const Token& t) {
	IfcParse::IfcFile* file = t.lexer->file;
	IfcEntityInstanceData* data = read(0, file, t.startPos);
	// Data needs to be loaded, for the tokens
	// to be consumed and parsing to continue.
	data->load();
	entity = file->schema()->instantiate(data);
}

namespace {
	template <typename T>
	class vector_or_array {
		std::vector<T>* vector_;
		T* array_;
		size_t size_, index_;

	public:
		vector_or_array(std::vector<T>* vector)
			: vector_(vector)
			, array_(0)
			, size_(0)
			, index_(0)
		{}

		vector_or_array(Argument** arr, size_t size)
			: vector_(0)
			, array_(arr)
			, size_(size)
			, index_(0)
		{}

		void push_back(const T& t) {
			if (array_ && index_ < size_) {
				array_[index_++] = t;
			} else if (vector_) {
				vector_->push_back(t);
			}
		}
	};
}

// 
// Reads the arguments from a list of token
// Aditionally, registers the ids (i.e. #[\d]+) in the inverse map
//
size_t IfcParse::IfcFile::load(unsigned entity_instance_name, Argument**& attributes, size_t num_attributes) {
	Token next = tokens->Next();

	std::vector<Argument*>* vector = 0;
	vector_or_array<Argument*> filler(attributes, num_attributes);
	if (attributes == 0) {
		vector = new std::vector<Argument*>();
		filler = vector_or_array<Argument*>(vector);
	}

	size_t return_value = 0;

	while( next.startPos || next.lexer ) {
		if ( TokenFunc::isOperator(next,',') ) {
			// do nothing
		} else if ( TokenFunc::isOperator(next,')') ) {
			break;
		} else if ( TokenFunc::isOperator(next,'(') ) {
			return_value++;
			ArgumentList* alist = new ArgumentList();
			alist->size() = load(entity_instance_name, alist->arguments(), 0);
			filler.push_back(alist);
		} else {
			return_value++;
			if ( TokenFunc::isIdentifier(next) ) {
				if (!parsing_complete_) {
					register_inverse(entity_instance_name, next);
				}
			} if ( TokenFunc::isKeyword(next) ) {
				try {
					filler.push_back(new EntityArgument(next));
				} catch ( IfcException& e ) {
					Logger::Message(Logger::LOG_ERROR, e.what());
				}
			} else {
				filler.push_back(new TokenArgument(next));
			}
		}
		next = tokens->Next();
	}

	if (vector) {
		attributes = new Argument*[vector->size()];
		return_value = vector->size();
		for (size_t i = 0; i < vector->size(); ++i) {
			attributes[i] = vector->at(i);
		}
	}

	delete vector;

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
template<typename T>
std::vector<T> read_aggregate_as_vector(Argument** list, size_t size) {
	std::vector<T> return_value;
	return_value.reserve(size);
	for (size_t i = 0; i < size; ++i) {
		return_value.push_back(*list[i]);
	}
	return return_value;
}
template<typename T>
std::vector< std::vector<T> > read_aggregate_of_aggregate_as_vector2(Argument** list, size_t size) {
	std::vector< std::vector<T> > return_value;
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

ArgumentList::operator std::vector<boost::dynamic_bitset<> >() const {
	return read_aggregate_as_vector<boost::dynamic_bitset<> >(list_, size_);
}

ArgumentList::operator IfcEntityList::ptr() const {
	IfcEntityList::ptr l ( new IfcEntityList() );
	for (size_t i = 0; i < size_; ++i) {
		// FIXME: account for $
		IfcUtil::IfcBaseClass* entity = *list_[i];
		l->push(entity);
	}
	return l;
}

ArgumentList::operator std::vector< std::vector<int> >() const {
	return read_aggregate_of_aggregate_as_vector2<int>(list_, size_);
}

ArgumentList::operator std::vector< std::vector<double> >() const {
	return read_aggregate_of_aggregate_as_vector2<double>(list_, size_);
}

ArgumentList::operator IfcEntityListList::ptr() const {
	IfcEntityListList::ptr l ( new IfcEntityListList() );
	for (size_t i = 0; i < size_; ++i) {
		const Argument* arg = list_[i];
		const ArgumentList* arg_list;
		if ((arg_list = dynamic_cast<const ArgumentList*>(arg)) != 0) {
			IfcEntityList::ptr e = *arg_list;
			l->push(e);
		} else {
			auto token = dynamic_cast<const TokenArgument*>(arg);
			int startpos = token ? token->token.startPos : 0;
			std::string string_rep = this->toString();
			throw IfcInvalidTokenException(startpos, string_rep, "nested aggregate");
		}
	}
	return l;
}

unsigned int ArgumentList::size() const { return (unsigned int)size_; }

Argument* ArgumentList::operator [] (unsigned int i) const {
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
	} else if (TokenFunc::isBool(token)) {
		return IfcUtil::Argument_BOOL;
	} else if (TokenFunc::isFloat(token)) {
		return IfcUtil::Argument_DOUBLE;
	} else if (TokenFunc::isString(token)) {
		return IfcUtil::Argument_STRING;
	} else if (TokenFunc::isEnumeration(token)) {
		return IfcUtil::Argument_ENUMERATION;
	} else if (TokenFunc::isIdentifier(token)) {
		return IfcUtil::Argument_ENTITY_INSTANCE;
	} else if (TokenFunc::isBinary(token)) {
		return IfcUtil::Argument_BINARY;
	} else if (TokenFunc::isOperator(token, '$')) {
		return IfcUtil::Argument_NULL;
	} else if (TokenFunc::isOperator(token, '*')) {
		return IfcUtil::Argument_DERIVED;
	} else {
		return IfcUtil::Argument_UNKNOWN;
	}
}

//
// Functions for casting the TokenArgument to other types
//
TokenArgument::operator int() const { return TokenFunc::asInt(token); }
TokenArgument::operator bool() const { return TokenFunc::asBool(token); }
TokenArgument::operator double() const { return TokenFunc::asFloat(token); }
TokenArgument::operator std::string() const { return TokenFunc::asString(token); }
TokenArgument::operator boost::dynamic_bitset<>() const { return TokenFunc::asBinary(token); }
TokenArgument::operator IfcUtil::IfcBaseClass*() const { return token.lexer->file->instance_by_id(TokenFunc::asIdentifier(token)); }
unsigned int TokenArgument::size() const { return 1; }
Argument* TokenArgument::operator [] (unsigned int /*i*/) const { throw IfcException("Argument is not a list of attributes"); }
std::string TokenArgument::toString(bool upper) const { 
	if ( upper && TokenFunc::isString(token) ) {
		return IfcWrite::IfcCharacterEncoder(TokenFunc::asString(token)); 
	} else {
		return TokenFunc::toString(token); 
	}
}
bool TokenArgument::isNull() const { return TokenFunc::isOperator(token,'$'); }

IfcUtil::ArgumentType EntityArgument::type() const {
	return IfcUtil::Argument_ENTITY_INSTANCE;
}

//
// Functions for casting the EntityArgument to other types
//
EntityArgument::operator IfcUtil::IfcBaseClass*() const { return entity; }
unsigned int EntityArgument::size() const { return 1; }
Argument* EntityArgument::operator [] (unsigned int /*i*/) const { throw IfcException("Argument is not a list of arguments"); }
std::string EntityArgument::toString(bool upper) const { 
	return entity->data().toString(upper);
}
//return entity->entity->toString(); }
bool EntityArgument::isNull() const { return false; }
EntityArgument::~EntityArgument() { delete entity;}

//
// Reads an Entity from the list of Tokens at the specified offset in the file
//
IfcEntityInstanceData* IfcParse::read(unsigned int i, IfcFile* f, boost::optional<unsigned> offset) {
	if (offset) {
		f->tokens->stream->Seek(*offset);
	}
	Token datatype = f->tokens->Next();
	if (!TokenFunc::isKeyword(datatype)) throw IfcException("Unexpected token while parsing entity");
	const IfcParse::declaration* ty = f->schema()->declaration_by_name(TokenFunc::asStringRef(datatype));
	IfcEntityInstanceData* e = new IfcEntityInstanceData(ty, f, i, offset.get_value_or(0));
	return e;
}

void IfcParse::IfcFile::seek_to(const IfcEntityInstanceData& data) {
	if (tokens->stream->Tell() != data.offset_in_file()) {
		tokens->stream->Seek(data.offset_in_file());
		Token datatype = tokens->Next();
		if (!TokenFunc::isKeyword(datatype)) throw IfcException("Unexpected token while parsing entity instance");
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

void IfcParse::IfcFile::register_inverse(unsigned id_from, Token t) {
	// Assume a check on token type has already been performed
	byref[t.value_int].push_back(id_from);
}

void IfcParse::IfcFile::register_inverse(unsigned id_from, IfcUtil::IfcBaseClass* inst) {
	byref[inst->data().id()].push_back(id_from);
}

void IfcParse::IfcFile::unregister_inverse(unsigned id_from, IfcUtil::IfcBaseClass* inst) {
	std::vector<unsigned int>& ids = byref[inst->data().id()];
	std::vector<unsigned int>::iterator it = std::find(ids.begin(), ids.end(), id_from);
	if (it == ids.end()) {
		// @todo inverses also need to be populated when multiple instances are added to a new file.
		// throw IfcParse::IfcException("Instance not found among inverses");
	} else {
		ids.erase(it);
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
	if (type_) {
		dt = type()->name();
		if (upper) {
			boost::to_upper(dt);
		}

		if (type()->as_entity() || id_ != 0) {
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

IfcEntityInstanceData::~IfcEntityInstanceData() {
	if (attributes_ != NULL) {
		for (size_t i = 0; i < getArgumentCount(); ++i) {
			delete attributes_[i];
		}
		delete[] attributes_;
	}
}

unsigned IfcEntityInstanceData::set_id(boost::optional<unsigned> i) {
	if (i) {
		return id_ = *i;
	} else {
		return id_ = file->FreshId();
	}
}

//
// Returns the entities of Entity type that have this entity in their ArgumentList
//
IfcEntityList::ptr IfcEntityInstanceData::getInverse(const IfcParse::declaration* type, int attribute_index) const {
	static std::mutex m;
	std::lock_guard<std::mutex> lk(m);

	return file->getInverse(id_, type, attribute_index);
}

void IfcEntityInstanceData::load() const {
	static std::recursive_mutex m;
	std::lock_guard<std::recursive_mutex> lk(m);

	// type_ is 0 for header entities which have their size predetermined in code
	Argument** tmp_data = nullptr;
	if (type_ != 0) {
		tmp_data = new Argument*[getArgumentCount()]{};
	}
	file->seek_to(*this);
	size_t n = file->load(id(), tmp_data, getArgumentCount());
	if (n != getArgumentCount()) {
		Logger::Error("Wrong number of attributes on instance with id #" + boost::lexical_cast<std::string>(id_));
	}
	file->try_read_semicolon();
	// @todo does this need to be atomic somehow?
	attributes_ = tmp_data;
}

IfcEntityInstanceData::IfcEntityInstanceData(const IfcEntityInstanceData& e) {
	file = 0;
	type_ = e.type_;
	id_ = 0;

	const unsigned int count = e.getArgumentCount();

	// In order not to have the instance read from file
	attributes_ = new Argument*[count];

	for (unsigned int i = 0; i < count; ++i) {
		attributes_[i] = 0;
		this->setArgument(i, e.getArgument(i));
	}
}

static IfcParse::NullArgument static_null_attribute;

Argument* IfcEntityInstanceData::getArgument(unsigned int i) const {
	if (attributes_ == 0) {
		load();
	}
	if (i < getArgumentCount()) {
		if (attributes_[i] == nullptr) {
			return &static_null_attribute;
		} else {
			return attributes_[i];
		}
	} else {
		throw IfcParse::IfcException("Attribute index out of range");
	}
}

class unregister_inverse_visitor {
private:
	IfcFile& file_;
	const IfcEntityInstanceData& data_;

public:
	unregister_inverse_visitor(IfcFile& file, const IfcEntityInstanceData& data)
		: file_(file), data_(data)
	{}

	void operator()(IfcUtil::IfcBaseClass* inst) {
		file_.unregister_inverse(data_.id(), inst);
	}
};

class register_inverse_visitor {
private:
	IfcFile& file_;
	const IfcEntityInstanceData& data_;

public:
	register_inverse_visitor(IfcFile& file, const IfcEntityInstanceData& data)
		: file_(file), data_(data)
	{}

	void operator()(IfcUtil::IfcBaseClass* inst) {
		file_.register_inverse(data_.id(), inst);
	}
};

class add_to_instance_list_visitor {
private:
	IfcEntityList::ptr& list_;

public:
	add_to_instance_list_visitor(IfcEntityList::ptr& list)
		: list_(list)
	{}

	void operator()(IfcUtil::IfcBaseClass* inst) {
		list_->push(inst);
	}
};

class apply_individual_instance_visitor {
private:
	Argument* attribute_;
	IfcEntityInstanceData* data_;

	template <typename T>
	void apply_attribute_(T& t, Argument* attr) const {
		if (!attr) {
			return;
		}

		if (attr->type() == IfcUtil::Argument_ENTITY_INSTANCE) {
			IfcUtil::IfcBaseClass* inst = *attr;
			t(inst);
		} else if (attr->type() == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcEntityList::ptr entity_list_attribute = *attr;
			for (IfcEntityList::it it = entity_list_attribute->begin(); it != entity_list_attribute->end(); ++it) {
				t(*it);
			}
		} else if (attr->type() == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcEntityListList::ptr entity_list_attribute = *attr;
			for (IfcEntityListList::outer_it it = entity_list_attribute->begin(); it != entity_list_attribute->end(); ++it) {
				for (IfcEntityListList::inner_it jt = it->begin(); jt != it->end(); ++jt) {
					t(*jt);
				}
			}
		}
	};
public:
	apply_individual_instance_visitor(Argument* attribute)
		: attribute_(attribute), data_(0)
	{}

	apply_individual_instance_visitor(IfcEntityInstanceData* data)
		: attribute_(0), data_(data)
	{}

	template <typename T>
	void apply(T& t) const {
		if (attribute_) {
			apply_attribute_(t, attribute_);
		} else {
			for (unsigned i = 0; i < data_->getArgumentCount(); ++i) {
				Argument* attr = data_->getArgument(i);
				apply_attribute_(t, attr);
			}
		}
	};

};

void IfcEntityInstanceData::setArgument(unsigned int i, Argument* a, IfcUtil::ArgumentType attr_type) {
	if (attributes_ == 0) {
		load();
	}

	if (attr_type == IfcUtil::Argument_UNKNOWN) {
		attr_type = a->type();
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
	case IfcUtil::Argument_DOUBLE:
		copy->set(static_cast<double>(*a));
		break;
	case IfcUtil::Argument_STRING:
		copy->set(static_cast<std::string>(*a));
		break;
	case IfcUtil::Argument_BINARY: {
		boost::dynamic_bitset<> attr_value = *a;
		copy->set(attr_value);
		break; }
	case IfcUtil::Argument_AGGREGATE_OF_INT: {
		std::vector<int> attr_value = *a;
		copy->set(attr_value);
		break;  }
	case IfcUtil::Argument_AGGREGATE_OF_DOUBLE: {
		std::vector<double> attr_value = *a;
		copy->set(attr_value);
		break; }
	case IfcUtil::Argument_AGGREGATE_OF_STRING: {
		std::vector<std::string> attr_value = *a;
		copy->set(attr_value);
		break; }
	case IfcUtil::Argument_AGGREGATE_OF_BINARY: {
		std::vector< boost::dynamic_bitset<> > attr_value = *a;
		copy->set(attr_value);
		break; }
	case IfcUtil::Argument_ENUMERATION: {
		std::string enum_literal = a->toString();
		// Remove leading and trailing '.'
		enum_literal = enum_literal.substr(1, enum_literal.size() - 2);
		
		const IfcParse::enumeration_type* enum_type = type()->as_entity()->
			attribute_by_index(i)->type_of_attribute()->as_named_type()->declared_type()->as_enumeration_type();
		
		std::vector<std::string>::const_iterator it = std::find(
			enum_type->enumeration_items().begin(), 
			enum_type->enumeration_items().end(), 
			enum_literal);
		
		if (it == enum_type->enumeration_items().end()) {
			throw IfcParse::IfcException(enum_literal + " does not name a valid item for " + enum_type->name());
		}

		copy->set(IfcWrite::IfcWriteArgument::EnumerationReference(it - enum_type->enumeration_items().begin(), it->c_str()));
		break; }
	case IfcUtil::Argument_ENTITY_INSTANCE: {
		copy->set(static_cast<IfcUtil::IfcBaseClass*>(*a));
		break; }
	case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
		IfcEntityList::ptr instances = *a;
		IfcEntityList::ptr mapped_instances(new IfcEntityList);
		// @todo mapped_instances are not actually mapped to the file using add().
		for (IfcEntityList::it it = instances->begin(); it != instances->end(); ++it) {
			mapped_instances->push(*it);
		}
		copy->set(mapped_instances);
		break; }
	case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
		std::vector< std::vector<int> > attr_value = *a;
		copy->set(attr_value);
		break; }
	case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
		std::vector< std::vector<double> > attr_value = *a;
		copy->set(attr_value);
		break; }
	case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
		IfcEntityListList::ptr instances = *a;
		IfcEntityListList::ptr mapped_instances(new IfcEntityListList);
		for (IfcEntityListList::outer_it it = instances->begin(); it != instances->end(); ++it) {
			std::vector<IfcUtil::IfcBaseClass*> inner;
			for (IfcEntityListList::inner_it jt = it->begin(); jt != it->end(); ++jt) {
				inner.push_back(*jt);
			}
			mapped_instances->push(inner);
		}
		copy->set(mapped_instances);
		break; }
	case IfcUtil::Argument_EMPTY_AGGREGATE:
	case IfcUtil::Argument_AGGREGATE_OF_EMPTY_AGGREGATE: {
		IfcUtil::ArgumentType t2 = IfcUtil::from_parameter_type(type()->as_entity()->attribute_by_index(i)->type_of_attribute());
		delete copy;
		copy = 0;
		setArgument(i, a, t2);
		break; }
	default:
	case IfcUtil::Argument_UNKNOWN:
		throw IfcParse::IfcException(std::string("Unknown attribute encountered: '") + a->toString() + "' at index '" + boost::lexical_cast<std::string>(i) + "'");
		break;
	}

	if (!copy) {
		return;
	}

	if (attributes_[i] != 0) {
		Argument* current_attribute = attributes_[i];
		if (this->file) {
			unregister_inverse_visitor visitor(*this->file, *this);
			apply_individual_instance_visitor(current_attribute).apply(visitor);
		}
		delete attributes_[i];
	}

	if (this->file) {
		register_inverse_visitor visitor(*this->file, *this);
		apply_individual_instance_visitor(copy).apply(visitor);

		this->file->mark_entity_as_modified(id_);
	}

	attributes_[i] = copy;
}

//
// Parses the IFC file in fn
// Creates the maps
//
#ifdef USE_MMAP
IfcFile::IfcFile(const std::string& fn, bool mmap) {
	return IfcFile::Init(new IfcSpfStream(fn, mmap));
}
#else
IfcFile::IfcFile(const std::string& fn) {
	initialize_(new IfcSpfStream(fn));
}
#endif

IfcFile::IfcFile(std::istream& f, int len) {
	initialize_(new IfcSpfStream(f, len));
}

IfcFile::IfcFile(void* data, int len) {
	initialize_(new IfcSpfStream(data, len));
}

IfcFile::IfcFile(IfcParse::IfcSpfStream* s) {
	initialize_(s);
}

IfcFile::IfcFile(const IfcParse::schema_definition* schema)
	: parsing_complete_(true)
	, good_(true)
	, schema_(schema)
	, ifcroot_type_(schema_->declaration_by_name("IfcRoot"))
	, MaxId(0)
	, tokens(0)
	, stream(0)
{
	setDefaultHeaderValues();
}

void IfcFile::initialize_(IfcParse::IfcSpfStream* s) {
	// Initialize a "C" locale for locale-independent
	// number parsing. See comment above on line 41.
	init_locale();

	good_ = false;

	parsing_complete_ = false;
	MaxId = 0;
	tokens = 0;
	stream = 0;
	schema_ = 0;

	setDefaultHeaderValues();
	
	stream = s;
	if (!stream->valid) {
		return;
	}

	tokens = new IfcSpfLexer(stream, this);
	_header.file(this);
	_header.tryRead();

	std::vector<std::string> schemas;
	try {
		schemas = _header.file_schema().schema_identifiers();
	} catch (...) {
		// Purposely empty catch block
	}

	if (schemas.size() == 1) {
		try {
			schema_ = IfcParse::schema_by_name(schemas.front());
		} catch (const IfcParse::IfcException& e) {
			Logger::Error(e);
		}
	}

	if (schema_ == 0) {
		Logger::Message(Logger::LOG_ERROR, "No support for file schema encountered ("
			+ boost::algorithm::join(schemas, ", ") + ")");
		return;
	}

	good_ = true;

	ifcroot_type_ = schema_->declaration_by_name("IfcRoot");

	boost::circular_buffer<Token> token_stream(3, Token());

	IfcEntityInstanceData* data;
	IfcUtil::IfcBaseClass* instance = 0;

	unsigned current_id = 0;
	int progress = 0;
	Logger::Status("Scanning file...");
	
	while (!stream->eof) {
		if (token_stream[0].type == IfcParse::Token_IDENTIFIER &&
			token_stream[1].type == IfcParse::Token_OPERATOR &&
			token_stream[1].value_char == '=' &&
			token_stream[2].type == IfcParse::Token_KEYWORD)
		{
			current_id = (unsigned) TokenFunc::asIdentifier(token_stream[0]);
			const IfcParse::declaration* entity_type;
			try {
				entity_type = schema_->declaration_by_name(TokenFunc::asStringRef(token_stream[2]));
			} catch (const IfcException& ex) {
				Logger::Message(Logger::LOG_ERROR, ex.what());
				goto advance;
			}
				
			data = new IfcEntityInstanceData(entity_type, this, current_id, token_stream[2].startPos);
			instance = schema()->instantiate(data);

            /// @todo Printing to stdout in a library class feels weird. Maybe move the progress prints to the client code?
			// Update the status after every 1000 instances parsed
			if (!((++progress) % 1000)) {
				std::stringstream ss; ss << "\r#" << current_id;
				Logger::Status(ss.str(), false);
			}

			if (instance->declaration().is(*ifcroot_type_)) {
				try {
					const std::string guid = *instance->data().getArgument(0);
					if ( byguid.find(guid) != byguid.end() ) {
						std::stringstream ss;
						ss << "Instance encountered with non-unique GlobalId " << guid;
						Logger::Message(Logger::LOG_WARNING,ss.str());
					}
					byguid[guid] = instance;
				} catch (const IfcException& ex) {
					Logger::Message(Logger::LOG_ERROR,ex.what());
				}
			}

			const IfcParse::declaration* ty = &instance->declaration();

			{
				IfcEntityList::ptr insts = instances_by_type_excl_subtypes(ty);
				if (!insts) {
					insts = IfcEntityList::ptr(new IfcEntityList());
					bytype_excl[ty] = insts;
				}
				insts->push(instance);
			}

			for (;;) {
				IfcEntityList::ptr insts = instances_by_type(ty);
				if (!insts) {
					insts = IfcEntityList::ptr(new IfcEntityList());
					bytype[ty] = insts;
				}
				insts->push(instance);
				const IfcParse::declaration* pt = ty->as_entity()->supertype();
				if (pt) {
					ty = pt;
				} else {
					break;
				}
			}

			if (byid.find(current_id) != byid.end()) {
				std::stringstream ss;
				ss << "Overwriting instance with name #" << current_id;
				Logger::Message(Logger::LOG_WARNING,ss.str());
			}
			byid[current_id] = instance;
			
			MaxId = (std::max)(MaxId, current_id);
		} else if (token_stream[0].type == IfcParse::Token_IDENTIFIER && instance) {
			register_inverse(current_id, token_stream[0]);
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

		if (next_token.type == Token_NONE) break;

		token_stream.push_back(next_token);
	}

	Logger::Status("\rDone scanning file   ");

	parsing_complete_ = true;

	return;
}

class traversal_visitor {
private:
	std::set<IfcUtil::IfcBaseClass*>& visited_;
	IfcEntityList::ptr& list_;
	int level_;
	int max_level_;

public:
	traversal_visitor(std::set<IfcUtil::IfcBaseClass*>& visited, IfcEntityList::ptr& list, int level, int max_level)
		: visited_(visited)
		, list_(list)
		, level_(level)
		, max_level_(max_level)
	{}

	void operator()(IfcUtil::IfcBaseClass* inst);
};

void traverse_(IfcUtil::IfcBaseClass* instance, std::set<IfcUtil::IfcBaseClass*>& visited, IfcEntityList::ptr list, int level, int max_level) {
	if (visited.find(instance) != visited.end()) {
		return;
	}
	visited.insert(instance);
	list->push(instance);

	if (level >= max_level && max_level > 0) return;

	traversal_visitor visit(visited, list, level + 1, max_level);
	apply_individual_instance_visitor(&instance->data()).apply(visit);
}

void traversal_visitor::operator()(IfcUtil::IfcBaseClass* inst) {
	traverse_(inst, visited_, list_, level_, max_level_);
}

IfcEntityList::ptr IfcParse::traverse(IfcUtil::IfcBaseClass* instance, int max_level) {
	std::set<IfcUtil::IfcBaseClass*> visited;
	IfcEntityList::ptr return_value(new IfcEntityList);
	traverse_(instance, visited, return_value, 0, max_level);
	return return_value;
}

/// @note: for backwards compatibility
IfcEntityList::ptr IfcFile::traverse(IfcUtil::IfcBaseClass* instance, int max_level) {
	return IfcParse::traverse(instance, max_level);
}

void IfcFile::mark_entity_as_modified(int /*id*/)
{
	by_ref_cached_.clear();
}

void IfcFile::addEntities(IfcEntityList::ptr es) {
	for( IfcEntityList::it i = es->begin(); i != es->end(); ++ i ) {
		addEntity(*i);
	}
}

IfcUtil::IfcBaseClass* IfcFile::addEntity(IfcUtil::IfcBaseClass* entity) {
	if (entity->declaration().schema() != schema()) {
		throw IfcParse::IfcException("Unabled to add instance from " + entity->declaration().schema()->name() + " schema to file with " + schema()->name() + " schema");
	}

	// If this instance has been inserted before, return
	// a reference to the copy that was created from it.
	entity_entity_map_t::iterator mit = entity_file_map.find(entity);
	if (mit != entity_file_map.end()) {
		return mit->second;
	}

	IfcUtil::IfcBaseClass* new_entity = entity;

	// Obtain all forward references by a depth-first 
	// traversal and add them to the file.
	if (parsing_complete_) {
		try {
			IfcEntityList::ptr entity_attributes = traverse(entity, 1);
			for (IfcEntityList::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
				if (*it != entity) {
					entity_entity_map_t::iterator mit2 = entity_file_map.find(*it);
					if (mit2 == entity_file_map.end()) {
						entity_file_map.insert(entity_entity_map_t::value_type(*it, addEntity(*it)));
					}
				}
			}
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Failed to visit forward references of", entity);
		}
	}

	// See whether the instance is already part of a file
	if (entity->data().file != 0) {
		if (entity->data().file == this) {
			// If it is part of this file
			// nothing needs to be done.
			return entity;
		}

		// An instance is being added from another file. A copy of the
		// container and entity is created. The attribute references 
		// need to be updated to point to instances in this file.
		IfcFile* other_file = entity->data().file;
		IfcEntityInstanceData* we = new IfcEntityInstanceData(entity->data());
		new_entity = schema()->instantiate(we);
		
		// In case an entity is added that contains geometry, the unit
		// information needs to be accounted for for IfcLengthMeasures.
        double conversion_factor = std::numeric_limits<double>::quiet_NaN();

		for (unsigned i = 0; i < we->getArgumentCount(); ++i) {
			Argument* attr = we->getArgument(i);
			IfcUtil::ArgumentType attr_type = attr->type();

			IfcParse::declaration* decl = 0;
			if (entity->declaration().as_entity()) {
				decl = 0;
				const parameter_type* pt = entity->declaration().as_entity()->attribute_by_index(i)->type_of_attribute();
				while (pt->as_aggregation_type()) {
					pt = pt->as_aggregation_type()->type_of_element();
				}
				if (pt->as_named_type()) {
					decl = pt->as_named_type()->declared_type();
				}
			}
			
			if (attr_type == IfcUtil::Argument_ENTITY_INSTANCE) {
				entity_entity_map_t::const_iterator eit = entity_file_map.find(*attr);
				if (eit == entity_file_map.end()) throw IfcParse::IfcException("Unable to map instance to file");
				
				IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
				copy->set(eit->second);
				we->setArgument(i, copy);
			} else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
				IfcEntityList::ptr instances = *attr;
				IfcEntityList::ptr new_instances(new IfcEntityList);
				for (IfcEntityList::it it = instances->begin(); it != instances->end(); ++it) {
					entity_entity_map_t::const_iterator eit = entity_file_map.find(*it);
					if (eit == entity_file_map.end()) throw IfcParse::IfcException("Unable to map instance to file");
					new_instances->push(eit->second);
				}
				
				IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
				copy->set(new_instances);
				we->setArgument(i, copy);
			} else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
				IfcEntityListList::ptr instances = *attr;
				IfcEntityListList::ptr new_instances(new IfcEntityListList);
				for (IfcEntityListList::outer_it it = instances->begin(); it != instances->end(); ++it) {
					std::vector<IfcUtil::IfcBaseClass*> list;
					for (IfcEntityListList::inner_it jt = it->begin(); jt != it->end(); ++jt) {
						entity_entity_map_t::const_iterator eit = entity_file_map.find(*jt);
						if (eit == entity_file_map.end()) throw IfcParse::IfcException("Unable to map instance to file");
						list.push_back(eit->second);
					}
					new_instances->push(list);
				}

				IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
				copy->set(new_instances);
				we->setArgument(i, copy);
			} else if (decl && decl->is(*schema()->declaration_by_name("IfcLengthMeasure"))) {
				if (boost::math::isnan(conversion_factor)) {
					const std::pair<IfcUtil::IfcBaseClass*, double> this_file_unit = getUnit("LENGTHUNIT");
					const std::pair<IfcUtil::IfcBaseClass*, double> other_file_unit = other_file->getUnit("LENGTHUNIT");
					if (this_file_unit.first && other_file_unit.first) {
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
				}
			}
		}

		// A new entity instance name is generated and
		// the instance is pointed to this file.
		we->file = this;
		if (we->type()->as_entity()) {
			we->set_id(FreshId());
		}

		// @todo entity_file_map: use weak_ptr
		entity_file_map.insert(entity_entity_map_t::value_type(entity, new_entity));
	}

	// For subtypes of IfcRoot, the GUID mapping needs to be updated.
	if (new_entity->declaration().is(*ifcroot_type_)) {
		try {
			const std::string guid = *new_entity->data().getArgument(0);
			if ( byguid.find(guid) != byguid.end() ) {
				std::stringstream ss;
				ss << "Overwriting entity with guid " << guid;
				Logger::Message(Logger::LOG_WARNING,ss.str());
			}
			byguid[guid] = new_entity;
		} catch (const IfcException& ex) {
			Logger::Message(Logger::LOG_ERROR,ex.what());
		}
	}

	// The mapping by entity type is updated.
	const IfcParse::declaration* ty = &new_entity->declaration();

	if (ty->as_entity()) {
		IfcEntityList::ptr insts = instances_by_type_excl_subtypes(ty);
		if (!insts) {
			insts = IfcEntityList::ptr(new IfcEntityList());
			bytype_excl[ty] = insts;
		}
		insts->push(new_entity);
	}

	for (; ty->as_entity();) {
		IfcEntityList::ptr insts = instances_by_type(ty);
		if (!insts) {
			insts = IfcEntityList::ptr(new IfcEntityList());
			bytype[ty] = insts;
		}
		insts->push(new_entity);

		const IfcParse::declaration* pt = ty->as_entity()->supertype();
		if (pt) {
			ty = pt;
		} else {
			break;
		}
	}

	if (ty->as_entity()) {
		int new_id = -1;
		if (!new_entity->data().file) {
			// For newly created entities ensure a valid ENTITY_INSTANCE_NAME is set
			new_entity->data().file = this;
			new_id = new_entity->data().set_id();
		} else {
			new_id = new_entity->data().id();
		}

		if (byid.find(new_id) != byid.end()) {
			// This should not happen
			std::stringstream ss;
			ss << "Overwriting entity with id " << new_id;
			Logger::Message(Logger::LOG_WARNING, ss.str());
		}

		// The mapping by entity instance name is updated.
		byid[new_id] = new_entity;
	}

	if (parsing_complete_ && ty->as_entity()) {
		build_inverses_(new_entity);
	}

	return new_entity;
}

void IfcFile::removeEntity(IfcUtil::IfcBaseClass* entity) {
	const unsigned id = entity->data().id();
	IfcUtil::IfcBaseClass* file_entity = instance_by_id(id);
	
	// Attention when running removeEntity inside a loop over a list of entities to be removed. 
	// This invalidates the iterator. A workaround is to reverse the loop:
	// boost::shared_ptr<IfcEntityList> entities = ...;
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

	IfcEntityList::ptr references = instances_by_reference(id);

	// Alter entity instances with INVERSE relations to the entity being 
	// deleted. This is necessary to maintain a valid IFC file, because 
	// dangling references to it's entities name should be removed. At this
	// moment, inversely related instances affected by the removal of the
	// entity being deleted are not deleted themselves.
	if (references) {
		for (IfcEntityList::it iit = references->begin(); iit != references->end(); ++iit) {
			IfcUtil::IfcBaseEntity* related_instance = (IfcUtil::IfcBaseEntity*) *iit;


			for (unsigned i = 0; i < related_instance->data().getArgumentCount(); ++i) {
				Argument* attr = related_instance->data().getArgument(i);
				if (attr->isNull()) continue;

				IfcUtil::ArgumentType attr_type = attr->type();
				switch(attr_type) {
				case IfcUtil::Argument_ENTITY_INSTANCE: {
					IfcUtil::IfcBaseClass* instance_attribute = *attr;
					if (instance_attribute == entity) {
						IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
						copy->set(boost::blank());
						related_instance->data().setArgument(i, copy);
					} }
					break;
				case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
					IfcEntityList::ptr instance_list = *attr;
					if (instance_list->contains(entity)) {
						instance_list->remove(entity);

						IfcWrite::IfcWriteArgument* copy = new IfcWrite::IfcWriteArgument();
						copy->set(instance_list);
						related_instance->data().setArgument(i, copy);
					} }
					break;
				case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
					IfcEntityListList::ptr instance_list_list = *attr;
					if (instance_list_list->contains(entity)) {
						IfcEntityListList::ptr new_list(new IfcEntityListList);
						for (IfcEntityListList::outer_it it = instance_list_list->begin(); it != instance_list_list->end(); ++it) {
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
					} }
					break;
				default: break;
				}
			}
		}
		byref.erase(byref.find(id));
	}

	IfcEntityList::ptr entity_attributes = traverse(entity, 1);
	for (IfcEntityList::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
		IfcUtil::IfcBaseClass* entity_attribute = *it;
		if (entity_attribute == entity) continue;
		const unsigned int name = entity_attribute->data().id();
		// Do not update inverses for simple types (which have id()==0 in IfcOpenShell).
		if (name != 0) {
			entities_by_ref_t::iterator byref_it = byref.find(name);
			if (byref_it != byref.end()) {
				std::vector<unsigned>& ids = byref_it->second;
				ids.erase(std::remove(ids.begin(), ids.end(), id), ids.end());
			}
		}
	}

	if (entity->declaration().is(*ifcroot_type_)) {
		const std::string global_id = *entity->data().getArgument(0);
		byguid.erase(byguid.find(global_id));
	}
	
	byid.erase(byid.find(id));

	const IfcParse::declaration* ty = &entity->declaration();

	{
		IfcEntityList::ptr instances_of_same_type = instances_by_type_excl_subtypes(ty);
		instances_of_same_type->remove(entity);
		if (instances_of_same_type->size() == 0) {
			bytype_excl.erase(ty);
		}
	}

	for (;;) {
		IfcEntityList::ptr instances_of_same_type = instances_by_type(ty);
		if (instances_of_same_type) {
			instances_of_same_type->remove(entity);
		}
		if (instances_of_same_type->size() == 0) {
			bytype.erase(ty);
		}

		const IfcParse::declaration* pt = ty->as_entity()->supertype();
		if (pt) {
			ty = pt;
		} else {
			break;
		}
	}
	
	delete entity;
}

IfcEntityList::ptr IfcFile::instances_by_type(const IfcParse::declaration* t) {
	entities_by_type_t::const_iterator it = bytype.find(t);
	return (it == bytype.end()) ? IfcEntityList::ptr() : it->second;
}

IfcEntityList::ptr IfcFile::instances_by_type_excl_subtypes(const IfcParse::declaration* t) {
	entities_by_type_t::const_iterator it = bytype_excl.find(t);
	return (it == bytype_excl.end()) ? IfcEntityList::ptr() : it->second;
}

IfcEntityList::ptr IfcFile::instances_by_type(const std::string& t) {
	return instances_by_type(schema()->declaration_by_name(t));
}

IfcEntityList::ptr IfcFile::instances_by_type_excl_subtypes(const std::string& t) {
	return instances_by_type_excl_subtypes(schema()->declaration_by_name(t));
}

IfcEntityList::ptr IfcFile::instances_by_reference(int t) {
	entities_by_ref_t::const_iterator it = byref.find(t);
	IfcEntityList::ptr ret;
	if (it != byref.end()) {
        ref_map_t::const_iterator cached_it = by_ref_cached_.find(t);
        if (cached_it != by_ref_cached_.end()) {
            ret = cached_it->second;
        }
        else {
            if (it->second.size()) {
                ret.reset(new IfcEntityList);            
                ret->reserve((unsigned)it->second.size());
                const std::vector<unsigned>& ids = it->second;
                for (std::vector<unsigned>::const_iterator jt = ids.begin(); jt != ids.end(); ++jt) {
                    ret->push(instance_by_id(*jt));
                }
            }
            by_ref_cached_[t] = ret;
        }
	}
	return ret;
}

IfcUtil::IfcBaseClass* IfcFile::instance_by_id(int id) {
	entity_by_id_t::const_iterator it = byid.find(id);
	if (it == byid.end()) {
		throw IfcException("Instance #" + boost::lexical_cast<std::string>(id) + " not found");
	}
	return it->second;
}

IfcUtil::IfcBaseClass* IfcFile::instance_by_guid(const std::string& guid) {
	entity_by_guid_t::const_iterator it = byguid.find(guid);
	if ( it == byguid.end() ) {
		throw IfcException("Instance with GlobalId '" + guid + "' not found");
	} else {
		return it->second;
	}
}

// FIXME: Test destructor to delete entity and arg allocations
IfcFile::~IfcFile() {
	for( entity_by_id_t::const_iterator it = byid.begin(); it != byid.end(); ++ it ) {
		delete it->second;
	}
	delete stream;
	delete tokens;
}

IfcFile::entity_by_id_t::const_iterator IfcFile::begin() const {
	return byid.begin();
}

IfcFile::entity_by_id_t::const_iterator IfcFile::end() const {
	return byid.end();
}

IfcFile::type_iterator IfcFile::types_begin() const {
	return bytype_excl.begin();
}

IfcFile::type_iterator IfcFile::types_end() const {
	return bytype_excl.end();
}

IfcFile::type_iterator IfcFile::types_incl_super_begin() const {
	return bytype.begin();
}

IfcFile::type_iterator IfcFile::types_incl_super_end() const {
	return bytype.end();
}

namespace {
	struct id_instance_pair_sorter {
		bool operator()(const IfcParse::IfcFile::entity_by_id_t::value_type& a, const IfcParse::IfcFile::entity_by_id_t::value_type& b) const {
			return a.first < b.first;
		}
	};
}

std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f) {
	f.header().write(os);

	typedef std::vector<std::pair<unsigned int, IfcUtil::IfcBaseClass*> > vector_t;
	vector_t sorted(f.begin(), f.end());
	std::sort(sorted.begin(), sorted.end(), id_instance_pair_sorter());

	for (vector_t::const_iterator it = sorted.begin(); it != sorted.end(); ++ it) {
		const IfcUtil::IfcBaseClass* e = it->second;
		if (e->declaration().as_entity()) {
			os << e->data().toString(true) << ";" << std::endl;
		}
	}

	os << "ENDSEC;" << std::endl;
	os << "END-ISO-10303-21;" << std::endl;

	return os;
}

std::string IfcFile::createTimestamp() const {
	char buf[255];
	
	time_t t;
	time(&t);
	
	struct tm* ti = localtime (&t);

	std::string result = "";
	if (strftime(buf,255,"%Y-%m-%dT%H:%M:%S",ti)) {
		result = std::string(buf);
	}

	return result;
}

IfcEntityList::ptr IfcFile::getInverse(int instance_id, const IfcParse::declaration* type, int attribute_index) {
	IfcUtil::IfcBaseClass* instance = instance_by_id(instance_id);

	IfcEntityList::ptr l = IfcEntityList::ptr(new IfcEntityList);
	IfcEntityList::ptr all = instances_by_reference(instance_id);
	if (!all) return l;

	for(IfcEntityList::it it = all->begin(); it != all->end(); ++it) {
		bool valid = type == 0 || (*it)->declaration().is(*type);
		if (valid && attribute_index >= 0) {
            try {
                Argument* arg = (*it)->data().getArgument(attribute_index);
                if (arg->type() == IfcUtil::Argument_ENTITY_INSTANCE) {
                    valid = instance == *arg;
                } else if (arg->type() == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
                    IfcEntityList::ptr li = *arg;
                    valid = li->contains(instance);
                } else if (arg->type() == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
                    IfcEntityListList::ptr li = *arg;
                    valid = li->contains(instance);
                }
            } catch (const IfcException& e) {
				valid = false;
				Logger::Error(e);
			}
		}
		if (valid) {
			l->push(*it);
		}
	}

	return l;
}

void IfcFile::setDefaultHeaderValues() {
	const std::string empty_string = "";
	std::vector<std::string> file_description, schema_identifiers, empty_vector;

	file_description.push_back("ViewDefinition [CoordinationView]");
	if (schema()) {
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
	IfcEntityList::ptr projects = instances_by_type(schema()->declaration_by_name("IfcProject"));

	if (projects && projects->size() == 1) {
		IfcUtil::IfcBaseClass* project = *projects->begin();
		
		IfcUtil::IfcBaseClass* unit_assignment = *project->data().getArgument(
			project->declaration().as_entity()->attribute_index("UnitsInContext")
		);
		
		IfcEntityList::ptr units = *unit_assignment->data().getArgument(
			unit_assignment->declaration().as_entity()->attribute_index("Units")
		);

		for (IfcEntityList::it it = units->begin(); it != units->end(); ++it) {
			IfcUtil::IfcBaseClass* unit = *it;
			if (unit->declaration().is("IfcNamedUnit")) {
				const std::string file_unit_type = *unit->data().getArgument(
					unit->declaration().as_entity()->attribute_index("UnitType")
				);

				if (file_unit_type != unit_type) {
					continue;
				}

				IfcUtil::IfcBaseClass* siunit = 0;
				if (unit->declaration().is("IfcConversionBasedUnit")) {
					IfcUtil::IfcBaseClass* mu = *unit->data().getArgument(
						unit->declaration().as_entity()->attribute_index("ConversionFactor")
					);

					IfcUtil::IfcBaseClass* vlc = *mu->data().getArgument(
						mu->declaration().as_entity()->attribute_index("ValueComponent")
					);

					IfcUtil::IfcBaseClass* unc = *mu->data().getArgument(
						mu->declaration().as_entity()->attribute_index("ValueComponent")
					);

					return_value.second *= static_cast<double>(*vlc->data().getArgument(0));
					return_value.first = unit;

					if (unc->declaration().is("IfcSIUnit")) {
						siunit = unc;
					}

				} else if (unit->declaration().is("IfcSIUnit")) {
					return_value.first = siunit = unit;
				}

				if (siunit) {
					Argument* prefix = siunit->data().getArgument(
						siunit->declaration().as_entity()->attribute_index("Prefix")
					);

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
	IfcEntityList::ptr entity_attributes(new IfcEntityList);
	try {
		entity_attributes = traverse(inst, 1);
	} catch (const std::exception& e) {
		Logger::Error(e);
	}

	for (IfcEntityList::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
		IfcUtil::IfcBaseClass* entity_attribute = *it;
		if (*it == inst) continue;
		try {
			if (entity_attribute->declaration().as_entity()) {
				unsigned entity_attribute_id = entity_attribute->data().id();
				byref[entity_attribute_id].push_back(inst->data().id());
			}
		} catch (const std::exception& e) {
			Logger::Error(e);
		}
	}
}

void IfcParse::IfcFile::build_inverses() {
	for (auto& pair : *this) {
		build_inverses_(pair.second);	
	}
}
