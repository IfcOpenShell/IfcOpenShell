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

#include <set>
#include <algorithm>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <ctime>

#ifdef _MSC_VER
#include <Windows.h>
#endif

#include "../ifcparse/IfcCharacterDecoder.h"
#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcSpfStream.h"
#include "../ifcparse/IfcWritableEntity.h"
#include "../ifcparse/IfcLateBoundEntity.h"
#include "../ifcparse/IfcFile.h"
#include "../ifcparse/IfcSIPrefix.h"

using namespace IfcParse;

// A static locale for the real number parser. strtod() is locale-dependent, causing issues 
// in locales that have ',' as a decimal separator. Therefore the non standard _strtod_l() / 
// strtod_l() is used and a reference to the "C" locale is obtained here. The alternative is 
// to use std::istringstream::imbue(std::locale::classic()), but there are subtleties in 
// parsing in MSVC2010 and it appears to be much slower. 
#ifdef _MSC_VER
static _locale_t locale = (_locale_t) 0;
void init_locale() {
	if (locale == (_locale_t) 0) {
		locale = _create_locale(LC_NUMERIC, "C");
	}
}
#else
#ifdef __APPLE__
#include <xlocale.h>
#endif
static locale_t locale = (locale_t) 0;
void init_locale() {
	if (locale == (locale_t) 0) {
		locale = newlocale(LC_NUMERIC_MASK, "C", (locale_t) 0);
	}
}
#endif

// 
// Opens the file, gets the filesize and reads a chunk in memory
//
IfcSpfStream::IfcSpfStream(const std::string& fn) {
	eof = false;
#ifdef _MSC_VER
	int fn_buffer_size = MultiByteToWideChar(CP_UTF8, 0, fn.c_str(), -1, 0, 0);
	wchar_t* fn_wide = new wchar_t[fn_buffer_size];
	MultiByteToWideChar(CP_UTF8, 0, fn.c_str(), -1, fn_wide, fn_buffer_size);
	stream = _wfopen(fn_wide, L"rb");
	delete[] fn_wide;
#else
	stream = fopen(fn.c_str(), "rb");
#endif
	if (stream == NULL) {
		valid = false;
		return;
	}
	valid = true;
	fseek(stream, 0, SEEK_END);
	size = (unsigned int) ftell(stream);;
	rewind(stream);
#ifdef BUF_SIZE
	offset = 0;
	paging = size > BUF_SIZE;
	buffer = new char[size < BUF_SIZE ? size : BUF_SIZE];
#else
	buffer = new char[size];
#endif
	ptr = 0;
	len = 0;	
	ReadBuffer(false);
}

IfcSpfStream::IfcSpfStream(std::istream& f, int l) {
	eof = false;
	size = l;
#ifdef BUF_SIZE
	paging = false;
	offset = 0;
#endif
	buffer = new char[size];
	f.read(buffer,size);
	valid = f.gcount() == size;
	ptr = 0;
	len = l;	
}

IfcSpfStream::IfcSpfStream(void* data, int l) {
	eof = false;
	size = l;
#ifdef BUF_SIZE
	paging = false;
	offset = 0;
#endif
	buffer = (char*) data;
	valid = true;
	ptr = 0;
	len = l;	
}

void IfcSpfStream::Close() {
#ifdef BUF_SIZE
	if ( paging ) fclose(stream);
#endif
	delete[] buffer;
}

//
// Reads a chunk of BUF_SIZE in memory and increments cursor if requested
//
void IfcSpfStream::ReadBuffer(bool inc) {
#ifdef BUF_SIZE
	if ( inc ) {
		offset += len;
		fseek(stream, offset, SEEK_SET);
	}
#endif
	eof = feof(stream) != 0;
	if ( eof ) return;
#ifdef BUF_SIZE
	len = (unsigned int) fread(buffer, 1, size < BUF_SIZE ? size : BUF_SIZE, stream);
#else
	len = (unsigned int) fread(buffer, 1, size, stream);
#endif
	eof = len == 0;
	ptr = 0;
#ifdef BUF_SIZE
	if (!paging) fclose(stream);
#else
	fclose(stream);
#endif
}

//
// Seeks an arbitrary position in the file
//
void IfcSpfStream::Seek(unsigned int o) {
#ifdef BUF_SIZE
	if ( !paging ) {
#endif
		ptr = o;
		if (ptr >= len) throw IfcException("Reading outside of file limits");
		eof = false;
#ifdef BUF_SIZE
	} else if ( o >= offset && (o < (offset+len)) ) {
		ptr = o - offset;
	} else {
		offset = o;
		clearerr(stream);
		fseek(stream, o, SEEK_SET);
		ReadBuffer(false);
	}
#endif
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
#ifdef BUF_SIZE
	if ( ! paging ) {
#endif
		return buffer[o];
#ifdef BUF_SIZE
	} else if ( o >= offset && (o < (offset+len)) ) {
		return buffer[o-offset];
	} else {
		clearerr(stream);
		fseek(stream, o, SEEK_SET);
		return ungetc(getc(stream), stream);
	}
#endif
}

//
// Returns the cursor position
//
unsigned int IfcSpfStream::Tell() {
#ifdef BUF_SIZE
	return offset + ptr;
#else
	return ptr;
#endif
}

//
// Increments cursor and reads new chunk if necessary
//
void IfcSpfStream::Inc() {
	if ( ++ptr == len ) { 
#ifdef BUF_SIZE
		if ( paging ) ReadBuffer();
		else {
#endif
			eof = true;
			return;
#ifdef BUF_SIZE
		}
#endif
	}
	const char current = IfcSpfStream::Peek();
	if ( current == '\n' || current == '\r' ) IfcSpfStream::Inc();
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

	if ( stream->eof ) return TokenPtr();

	while (skipWhitespace() || skipComment()) {}
	
	if ( stream->eof ) return TokenPtr();
	unsigned int pos = stream->Tell();

	char c = stream->Peek();
	
	// If the cursor is at [()=,;$*] we know token consists of single char
	if (c == '(' || c == ')' || c == '=' || c == ',' || c == ';' || c == '$' || c == '*') {
		stream->Inc();
		return TokenPtr(c);
	}

	int len = 0;

	char p = 0;
	while ( ! stream->eof ) {

		// Read character and increment pointer if not starting a new token
		char c = stream->Peek();
		if ( len && (c == '(' || c == ')' || c == '=' || c == ',' || c == ';' || c == '/') ) break;
		stream->Inc();
		len ++;

		// If a string is encountered defer processing to the IfcCharacterDecoder
		if ( c == '\'' ) decoder->dryRun();

		p = c;
	}
	if ( len ) return TokenPtr(this,pos);
	else return TokenPtr();
}

//
// Reads a std::string from the file at specified offset
// Omits whitespace and comments
//
std::string IfcSpfLexer::TokenString(unsigned int offset) {
	const bool was_eof = stream->eof;
	unsigned int old_offset = stream->Tell();
	stream->Seek(offset);
	std::string buffer;
	buffer.reserve(128);
	char p = 0;
	while ( ! stream->eof ) {
		char c = stream->Peek();
		if ( buffer.size() && (c == '(' || c == ')' || c == '=' || c == ',' || c == ';' || c == '/') ) break;
		stream->Inc();
		if ( c == ' ' || c == '\r' || c == '\n' || c == '\t' ) continue;
		else if ( c == '\'' ) return *decoder;
		else buffer.push_back(c);
		p = c;
	}
	if ( was_eof ) stream->eof = true;
	else stream->Seek(old_offset);
	return buffer;
}

//
// Functions for creating Tokens from an arbitary file offset.
// The first 4 bits are reserved for Tokens of type ()=,;$*
//
Token IfcParse::TokenPtr(IfcSpfLexer* tokens, unsigned int offset) { return Token(tokens,offset); }
Token IfcParse::TokenPtr(char c) { return Token((IfcSpfLexer*)0,(unsigned) c); }
Token IfcParse::TokenPtr() { return Token((IfcSpfLexer*)0,0); }

//
// Functions to convert Tokens to binary data
//
bool TokenFunc::startsWith(const Token& t, char c) {
	return t.first->stream->Read(t.second) == c;
}

bool TokenFunc::isOperator(const Token& t, char op) {
	return (!t.first) && (!op || op == t.second);
}

bool TokenFunc::isIdentifier(const Token& t) {
	return ! isOperator(t) && startsWith(t, '#');
}

bool TokenFunc::isString(const Token& t) {
	return ! isOperator(t) && startsWith(t, '\'');
}

bool TokenFunc::isEnumeration(const Token& t) {
	return ! isOperator(t) && startsWith(t, '.');
}

bool TokenFunc::isBinary(const Token& t) {
	return ! isOperator(t) && startsWith(t, '"');
}

bool TokenFunc::isKeyword(const Token& t) {
	// bool is a subtype of enumeration, no need to test for that
	return !isOperator(t) && !isIdentifier(t) && !isString(t) && !isEnumeration(t) && !isInt(t) && !isFloat(t) && !isBinary(t);
}

bool TokenFunc::isInt(const Token& t) {
	if (isOperator(t) || isString(t) || isEnumeration(t)) {
		return false;
	}
	const std::string str = asString(t);
	const char* start = str.c_str();
	char* end;
	long result = strtol(start,&end,10);
	return ((end - start) == str.length());
}

bool TokenFunc::isBool(const Token& t) {
	if (!isEnumeration(t)) return false;
	const std::string str = asString(t);
	return str == "T" || str == "F";
}

bool TokenFunc::isFloat(const Token& t) {
	if (isOperator(t) || isString(t) || isEnumeration(t)) {
		return false;
	}
	const std::string str = asString(t);
	const char* start = str.c_str();
	char* end;
#ifdef _MSC_VER
	double result = _strtod_l(start,&end,locale);
#else
	double result = strtod_l(start,&end,locale);
#endif
	return ((end - start) == str.length());
}

int TokenFunc::asInt(const Token& t) {
	const std::string str = asString(t);
	// In case of an ENTITY_INSTANCE_NAME skip the leading #
	const char* start = str.c_str() + (isIdentifier(t) ? 1 : 0);
	char* end;
	long result = strtol(start,&end,10);
	if ( start == end ) throw IfcException("Token is not an integer or identifier");
	return (int) result;
}

bool TokenFunc::asBool(const Token& t) {
	const std::string str = asString(t);
	return str == "T";
}

double TokenFunc::asFloat(const Token& t) {
	const std::string str = asString(t);
	const char* start = str.c_str();
	char* end;
#ifdef _MSC_VER
	double result = _strtod_l(start,&end,locale);
#else
	double result = strtod_l(start,&end,locale);
#endif
	if ( start == end ) throw IfcException("Token is not a real");
	return result;
}

std::string TokenFunc::asString(const Token& t) {
	if ( isOperator(t,'$') ) return "";
	else if ( isOperator(t) ) throw IfcException("Token is not a string");
	std::string str = t.first->TokenString(t.second);
	return isString(t) || isEnumeration(t) || isBinary(t) ? str.substr(1,str.size()-2) : str;
}

boost::dynamic_bitset<> TokenFunc::asBinary(const Token& t) {
	const std::string str = asString(t);
	if (str.size() < 1) {
		throw IfcException("Token is not a valid binary sequence");
	}
	
	std::string::const_iterator it = str.begin();
	int n = *it - '0';
	if ((n < 0 || n > 3) || (str.size() == 1 && n != 0)) {
		throw IfcException("Token is not a valid binary sequence");
	}

	++it;
	unsigned i = (str.size()-1) * 4 - n;
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
	if ( isOperator(t) ) return std::string ( (char*) &t.second	, 1 );
	else return t.first->TokenString(t.second);
}


TokenArgument::TokenArgument(const Token& t) {
	token = t;
}

EntityArgument::EntityArgument(const Token& t) {
	IfcParse::IfcFile* file = t.first->file;
	if (file->create_latebound_entities()) {
		entity = new IfcLateBoundEntity(new Entity(0, file, t.second));
	} else {
		entity = IfcSchema::SchemaEntity(new Entity(0, file, t.second));
	}
}

// 
// Reads the arguments from a list of token
// Aditionally, stores the ids (i.e. #[\d]+) in a vector
//
void ArgumentList::read(IfcSpfLexer* t, std::vector<unsigned int>& ids) {
	IfcParse::IfcFile* file = t->file;
	
	Token next = t->Next();
	while( next.second || next.first ) {
		if ( TokenFunc::isOperator(next,',') ) {
			// do nothing
		} else if ( TokenFunc::isOperator(next,')') ) {
			break;
		} else if ( TokenFunc::isOperator(next,'(') ) {
			ArgumentList* list = new ArgumentList();
			list->read(t, ids);
			push(list);
		} else {
			if ( TokenFunc::isIdentifier(next) ) {
				ids.push_back(TokenFunc::asInt(next));
			} if ( TokenFunc::isKeyword(next) ) {
				t->Next();
				try {
					push ( new EntityArgument(next) );
				} catch ( IfcException& e ) {
					Logger::Message(Logger::LOG_ERROR,e.what());
				}
			} else {
				push ( new TokenArgument(next) );
			}
		}
		next = t->Next();
	}
}

IfcUtil::ArgumentType ArgumentList::type() const {
	if (list.empty()) return IfcUtil::Argument_UNKNOWN;
	const IfcUtil::ArgumentType elem_type = list[0]->type();
	if (elem_type == IfcUtil::Argument_INT) {
		return IfcUtil::Argument_AGGREGATE_OF_INT;
	} else if (elem_type == IfcUtil::Argument_DOUBLE) {
		return IfcUtil::Argument_AGGREGATE_OF_DOUBLE;
	} else if (elem_type == IfcUtil::Argument_STRING) {
		return IfcUtil::Argument_AGGREGATE_OF_STRING;
	} else if (elem_type == IfcUtil::Argument_BINARY) {
		return IfcUtil::Argument_AGGREGATE_OF_BINARY;
	} else if (elem_type == IfcUtil::Argument_ENTITY_INSTANCE) {
		return IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE;
	} else if (elem_type == IfcUtil::Argument_AGGREGATE_OF_INT) {
		return IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT;
	} else if (elem_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
		return IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE;
	} else if (elem_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
		return IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE;
	} else {
		return IfcUtil::Argument_UNKNOWN;
	}
}

void ArgumentList::push(Argument* l) {
	list.push_back(l);
}

// templated helper function for reading arguments into a list
template<typename T>
std::vector<T> read_aggregate_as_vector(const std::vector<Argument*>& list) {
	std::vector<T> return_value;
	return_value.reserve(list.size());
	std::vector<Argument*>::const_iterator it = list.begin();
	for (; it != list.end(); ++it) {
		return_value.push_back(**it);
	}
	return return_value;
}
template<typename T>
std::vector< std::vector<T> > read_aggregate_of_aggregate_as_vector2(const std::vector<Argument*>& list) {
	std::vector< std::vector<T> > return_value;
	return_value.reserve(list.size());
	std::vector<Argument*>::const_iterator it = list.begin();
	for (; it != list.end(); ++it) {
		return_value.push_back(**it);
	}
	return return_value;
}

//
// Functions for casting the ArgumentList to other types
//
ArgumentList::operator int() const { throw IfcException("Argument is not an integer"); }
ArgumentList::operator bool() const { throw IfcException("Argument is not a boolean"); }
ArgumentList::operator double() const { throw IfcException("Argument is not a number"); }
ArgumentList::operator std::string() const { throw IfcException("Argument is not a string"); }
ArgumentList::operator boost::dynamic_bitset<>() const { throw IfcException("Argument is not a binary"); }

ArgumentList::operator std::vector<double>() const {
	return read_aggregate_as_vector<double>(list);
}

ArgumentList::operator std::vector<int>() const {
	return read_aggregate_as_vector<int>(list);
}

ArgumentList::operator std::vector<std::string>() const {
	return read_aggregate_as_vector<std::string>(list);
}

ArgumentList::operator std::vector<boost::dynamic_bitset<> >() const {
	return read_aggregate_as_vector<boost::dynamic_bitset<> >(list);
}

ArgumentList::operator IfcUtil::IfcBaseClass*() const { throw IfcException("Argument is not an entity instance"); }

ArgumentList::operator IfcEntityList::ptr() const {
	IfcEntityList::ptr l ( new IfcEntityList() );
	std::vector<Argument*>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		// FIXME: account for $
		IfcUtil::IfcBaseClass* entity = **it;
		l->push(entity);
	}
	return l;
}

ArgumentList::operator std::vector< std::vector<int> >() const {
	return read_aggregate_of_aggregate_as_vector2<int>(list);
}

ArgumentList::operator std::vector< std::vector<double> >() const {
	return read_aggregate_of_aggregate_as_vector2<double>(list);
}

ArgumentList::operator IfcEntityListList::ptr() const {
	IfcEntityListList::ptr l ( new IfcEntityListList() );
	std::vector<Argument*>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		const Argument* arg = *it;
		const ArgumentList* arg_list;
		if ((arg_list = dynamic_cast<const ArgumentList*>(arg))) {
			IfcEntityList::ptr e = *arg_list;
			l->push(e);
		}
	}
	return l;
}

unsigned int ArgumentList::size() const { return (unsigned int) list.size(); }

Argument* ArgumentList::operator [] (unsigned int i) const {
	if ( i >= list.size() ) {
		throw IfcAttributeOutOfRangeException("Argument index out of range");
	}
	return list[i];
}

void ArgumentList::set(unsigned int i, Argument* argument) {
	while (size() < i) {
		push(new TokenArgument(Token(static_cast<IfcSpfLexer*>(0), '$')));
	}
	if (i < size()) {
		delete list[i];
		list[i] = argument;
	} else {
		list.push_back(argument);
	}	
}

std::string ArgumentList::toString(bool upper) const {
	std::stringstream ss;
	ss << "(";
	for( std::vector<Argument*>::const_iterator it = list.begin(); it != list.end(); it ++ ) {
		if ( it != list.begin() ) ss << ",";
		ss << (*it)->toString(upper);
	}
	ss << ")";
	return ss.str();
}

bool ArgumentList::isNull() const { return false; }

ArgumentList::~ArgumentList() {
	for( std::vector<Argument*>::iterator it = list.begin(); it != list.end(); it ++ ) {
		delete (*it);
	}
	list.clear();
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
TokenArgument::operator std::vector<double>() const { throw IfcException("Argument is not a list of floats"); }
TokenArgument::operator std::vector<int>() const { throw IfcException("Argument is not a list of ints"); }
TokenArgument::operator std::vector<std::string>() const { throw IfcException("Argument is not a list of strings"); }
TokenArgument::operator std::vector<boost::dynamic_bitset<> >() const { throw IfcException("Argument is not a list of binaries"); }
TokenArgument::operator IfcUtil::IfcBaseClass*() const { return token.first->file->entityById(TokenFunc::asInt(token)); }
TokenArgument::operator IfcEntityList::ptr() const { throw IfcException("Argument is not a list of entity instances"); }
TokenArgument::operator std::vector< std::vector<int> >() const { throw IfcException("Argument is not a list of list of ints"); }
TokenArgument::operator std::vector< std::vector<double> >() const { throw IfcException("Argument is not a list of list of floats"); }
TokenArgument::operator IfcEntityListList::ptr() const { throw IfcException("Argument is not a list of list of entity instances"); }
unsigned int TokenArgument::size() const { return 1; }
Argument* TokenArgument::operator [] (unsigned int i) const { throw IfcException("Argument is not a list of attributes"); }
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
EntityArgument::operator int() const { throw IfcException("Argument is not an integer"); }
EntityArgument::operator bool() const { throw IfcException("Argument is not a boolean"); }
EntityArgument::operator double() const { throw IfcException("Argument is not a number"); }
EntityArgument::operator boost::dynamic_bitset<>() const { throw IfcException("Argument is not a binary"); }
EntityArgument::operator std::string() const { throw IfcException("Argument is not a string"); }
EntityArgument::operator std::vector<double>() const { throw IfcException("Argument is not a list of floats"); }
EntityArgument::operator std::vector<int>() const { throw IfcException("Argument is not a list of ints"); }
EntityArgument::operator std::vector<std::string>() const { throw IfcException("Argument is not a list of strings"); }
EntityArgument::operator std::vector<boost::dynamic_bitset<> >() const { throw IfcException("Argument is not a list of binaries"); }
EntityArgument::operator IfcUtil::IfcBaseClass*() const { return entity; }
EntityArgument::operator IfcEntityList::ptr() const { throw IfcException("Argument is not a list of entity instances"); }
EntityArgument::operator std::vector< std::vector<int> >() const { throw IfcException("Argument is not a list of list of ints"); }
EntityArgument::operator std::vector< std::vector<double> >() const { throw IfcException("Argument is not a list of list of floats"); }
EntityArgument::operator IfcEntityListList::ptr() const { throw IfcException("Argument is not a list of list of entity instances"); }
unsigned int EntityArgument::size() const { return 1; }
Argument* EntityArgument::operator [] (unsigned int i) const { throw IfcException("Argument is not a list of arguments"); }
std::string EntityArgument::toString(bool upper) const { 
	return entity->entity->toString(upper);
}
//return entity->entity->toString(); }
bool EntityArgument::isNull() const { return false; }
EntityArgument::~EntityArgument() { delete entity; }

//
// Reads an Entity from the list of Tokens
//
Entity::Entity(unsigned int i, IfcFile* f) : _id(i), args(0) {
	file = f;
	Token datatype = f->tokens->Next();
	if ( ! TokenFunc::isKeyword(datatype)) throw IfcException("Unexpected token while parsing entity");
	_type = IfcSchema::Type::FromString(TokenFunc::asString(datatype));
	offset = datatype.second;
}

//
// Reads an Entity from the list of Tokens at the specified offset in the file
//
Entity::Entity(unsigned int i, IfcFile* f, unsigned int o) { // : file(f) {
	file = f;
	std::vector<unsigned int> ids;
	_id = i;
	offset = o;
	Load(ids, true);
}

//
// Access the Nth argument from the ArgumentList
//
Argument* Entity::getArgument(unsigned int i) {
	if ( ! args ) {
		std::vector<unsigned int> ids;
		Load(ids, true);
	}
	return (*args)[i];
}

unsigned int Entity::getArgumentCount() const {
	if ( ! args ) {
		std::vector<unsigned int> ids;
		Load(ids, true);
	}
	return args->size();
}

//
// Load the ArgumentList
//
void Entity::Load(std::vector<unsigned int>& ids, bool seek) const {
	if ( seek ) {
		file->tokens->stream->Seek(offset);
		Token datatype = file->tokens->Next();
		if ( ! TokenFunc::isKeyword(datatype)) throw IfcException("Unexpected token while parsing entity");
		_type = IfcSchema::Type::FromString(TokenFunc::asString(datatype));
	}
	Token open = file->tokens->Next();
	args = new ArgumentList();
	args->read(file->tokens, ids);
	unsigned int old_offset = file->tokens->stream->Tell();
	Token semilocon = file->tokens->Next();
	if ( ! TokenFunc::isOperator(semilocon,';') ) file->tokens->stream->Seek(old_offset);
}

IfcSchema::Type::Enum Entity::type() const {
	return _type;
}

//
// Returns the CamelCase string representation of the datatype as it is defined in the schema
//
std::string Entity::datatype() const {
	return IfcSchema::Type::ToString(_type);
}

//
// Returns a string representation of the entity
// Note that this initializes the entity if it is not initialized
//
std::string Entity::toString(bool upper) const {
	if (!args) {
		std::vector<unsigned int> ids;
		Load(ids, true);
	}

	std::stringstream ss;
	ss.imbue(std::locale::classic());
	
	std::string dt = datatype();
	if (upper) {
		for (std::string::iterator p = dt.begin(); p != dt.end(); ++p ) *p = toupper(*p);
	}

	if (!IfcSchema::Type::IsSimple(type()) || _id != 0) {
		ss << "#" << _id << "=";
	}

	ss << dt << args->toString(upper);

	return ss.str();
}

Entity::~Entity() {
	delete args;
}

//
// Returns the entities of Entity type that have this entity in their ArgumentList
//
IfcEntityList::ptr Entity::getInverse(IfcSchema::Type::Enum type, int attribute_index) {
	return file->getInverse(_id, type, attribute_index);
}

bool Entity::is(IfcSchema::Type::Enum v) const { return _type == v; }
unsigned int Entity::id() { return _id; }

IfcWrite::IfcWritableEntity* Entity::isWritable() {
	return 0;
}

IfcFile::IfcFile(bool create_latebound_entities)
	: _create_latebound_entities(create_latebound_entities)
	, stream(0)
	, lastId(0)
	, tokens(0)
	, MaxId(0)
{
	setDefaultHeaderValues();
}

//
// Parses the IFC file in fn
// Creates the maps
//
bool IfcFile::Init(const std::string& fn) {
	return IfcFile::Init(new IfcSpfStream(fn));
}

bool IfcFile::Init(std::istream& f, int len) {
	return IfcFile::Init(new IfcSpfStream(f,len));
}

bool IfcFile::Init(void* data, int len) {
	return IfcFile::Init(new IfcSpfStream(data,len));
}

bool IfcFile::Init(IfcParse::IfcSpfStream* s) {
	// Initialize a "C" locale for locale-independent
	// number parsing. See comment above on line 41.
	init_locale();

	stream = s;
	if (!stream->valid) {
		return false;
	}

	tokens = new IfcSpfLexer(stream, this);
	_header.lexer(tokens);
	_header.tryRead();

	std::vector<std::string> schemas;
	try {
		schemas = _header.file_schema().schema_identifiers();
	} catch (...) {}
	if (schemas.size() != 1 || schemas[0] != IfcSchema::Identifier) {
		Logger::Message(Logger::LOG_ERROR, std::string("File schema encountered different from expected '") + IfcSchema::Identifier + "'");
	}

	Token token = TokenPtr();
	Token previous = TokenPtr();

	unsigned int currentId = 0;
	lastId = 0;
	int x = 0;
	Entity* e;
	IfcUtil::IfcBaseClass* entity = 0; 
	Logger::Status("Scanning file...");
	while ( ! stream->eof ) {
		if ( currentId ) {
			try {
				e = new Entity(currentId,this);
				if (this->create_latebound_entities()) {
					entity = new IfcLateBoundEntity(e);
				} else {
					entity = IfcSchema::SchemaEntity(e);
				}
			} catch (const IfcException& ex) {
				currentId = 0;
				Logger::Message(Logger::LOG_ERROR,ex.what());
				continue;
			}
			// Update the status after every 1000 instances parsed
			if ( !((++x)%1000) ) {
				std::stringstream ss; ss << "\r#" << currentId;
				Logger::Status(ss.str(), false);
			}
			if ( entity->is(IfcSchema::Type::IfcRoot) ) {
				IfcSchema::IfcRoot* ifc_root = (IfcSchema::IfcRoot*) entity;
				try {
					const std::string guid = ifc_root->GlobalId();
					if ( byguid.find(guid) != byguid.end() ) {
						std::stringstream ss;
						ss << "Overwriting entity with guid " << guid;
						Logger::Message(Logger::LOG_WARNING,ss.str());
					}
					byguid[guid] = ifc_root;
				} catch (const IfcException& ex) {
					Logger::Message(Logger::LOG_ERROR,ex.what());
				}
			}

			IfcSchema::Type::Enum ty = entity->type();
			do {
				IfcEntityList::ptr instances_by_type = entitiesByType(ty);
				if (!instances_by_type) {
					instances_by_type = IfcEntityList::ptr(new IfcEntityList());
					bytype[ty] = instances_by_type;
				}
				instances_by_type->push(entity);
				ty = IfcSchema::Type::Parent(ty);
			} while ( ty > -1 );
			
			if ( byid.find(currentId) != byid.end() ) {
				std::stringstream ss;
				ss << "Overwriting entity with id " << currentId;
				Logger::Message(Logger::LOG_WARNING,ss.str());
			}
			byid[currentId] = entity;
			
			MaxId = (std::max)(MaxId,currentId);
			currentId = 0;
		} else {
			try { token = tokens->Next(); }
			catch (... ) { token = TokenPtr(); }
		}

		if ( ! (token.second || token.first) ) break;
		
		if ( (previous.second || previous.first) && TokenFunc::isIdentifier(previous) ) {
			int id = TokenFunc::asInt(previous);
			if ( TokenFunc::isOperator(token,'=') ) {
				currentId = id;
			} else if (entity) {
				IfcEntityList::ptr instances_by_ref = entitiesByReference(id);
				if (!instances_by_ref) {
					instances_by_ref = IfcEntityList::ptr(new IfcEntityList());
					byref[id] = instances_by_ref;
				}
				instances_by_ref->push(entity);
			}
		}
		previous = token;
	}
	Logger::Status("\rDone scanning file   ");
	return true;
}

void IfcFile::traverse(IfcUtil::IfcBaseClass* instance, std::set<IfcUtil::IfcBaseClass*>& visited, IfcEntityList::ptr list, int level, int max_level) {
	if (visited.find(instance) != visited.end()) {
		return;
	}
	visited.insert(instance);
	list->push(instance);

	if (level >= max_level && max_level > 0) return;

	for (unsigned i = 0; i < instance->getArgumentCount(); ++i) {
		Argument* arg = instance->getArgument(i);

		if (arg->type() == IfcUtil::Argument_ENTITY_INSTANCE) {
			traverse(*arg, visited, list, level + 1, max_level);
		} else if (arg->type() == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcEntityList::ptr entity_list_attribute = *arg;
			for (IfcEntityList::it it = entity_list_attribute->begin(); it != entity_list_attribute->end(); ++it) {
				traverse(*it, visited, list, level + 1, max_level);
			}
		} else if (arg->type() == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcEntityListList::ptr entity_list_attribute = *arg;
			for (IfcEntityListList::outer_it it = entity_list_attribute->begin(); it != entity_list_attribute->end(); ++it) {
				for (IfcEntityListList::inner_it jt = it->begin(); jt != it->end(); ++jt) {
					traverse(*jt, visited, list, level + 1, max_level);
				}
			}
		}
	}
}

IfcEntityList::ptr IfcFile::traverse(IfcUtil::IfcBaseClass* instance, int max_level) {
	std::set<IfcUtil::IfcBaseClass*> visited;
	IfcEntityList::ptr return_value(new IfcEntityList);
	traverse(instance, visited, return_value, 0, max_level);
	return return_value;
}

void IfcFile::addEntities(IfcEntityList::ptr es) {
	for( IfcEntityList::it i = es->begin(); i != es->end(); ++ i ) {
		addEntity(*i);
	}
}

IfcUtil::IfcBaseClass* IfcFile::addEntity(IfcUtil::IfcBaseClass* entity) {
	// If this instance has been inserted before, return
	// a reference to the copy that was created from it.
	entity_entity_map_t::iterator it = entity_file_map.find(entity);
	if (it != entity_file_map.end()) {
		return it->second;
	}

	// Obtain all forward references by a depth-first 
	// traversal and add them to the file.
	try {
		IfcEntityList::ptr entity_attributes = traverse(entity, 1);
		for (IfcEntityList::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
			if (*it != entity) {
				entity_file_map.insert(entity_entity_map_t::value_type(*it, addEntity(*it)));
			}
		}
	} catch (...) {
		Logger::Message(Logger::LOG_ERROR, "Failed to visit forward references of", entity->entity);
	}

	// See whether the instance is already part of a file
	if (entity->entity->file != 0) {
		if (entity->entity->file == this) {
			// If it is part of this file
			// nothing needs to be done.
			return entity;
		}

		// An instance is being added from another file. A copy of the
		// container and entity is created. The attribute references 
		// need to be updated to point to instances in this file.
		IfcFile* other_file = entity->entity->file;
		IfcWrite::IfcWritableEntity* we = new IfcWrite::IfcWritableEntity(entity->entity);
		if (this->create_latebound_entities()) {
			entity = new IfcLateBoundEntity(we);
		} else {
			entity = IfcSchema::SchemaEntity(we);
		}
		
		// In case an entity is added that contains geometry, the unit
		// information needs to be accounted for for IfcLengthMeasures.
		boost::optional<double> conversion_factor;

		for (unsigned i = 0; i < we->getArgumentCount(); ++i) {
			Argument* attr = we->getArgument(i);
			IfcUtil::ArgumentType attr_type = attr->type();
			if (attr_type == IfcUtil::Argument_ENTITY_INSTANCE) {
				entity_entity_map_t::const_iterator eit = entity_file_map.find(*attr);
				if (eit == entity_file_map.end()) throw IfcParse::IfcException("Unable to map instance to file");
				we->setArgument(i, eit->second);
			} else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
				IfcEntityList::ptr instances = *attr;
				IfcEntityList::ptr new_instances(new IfcEntityList);
				for (IfcEntityList::it it = instances->begin(); it != instances->end(); ++it) {
					entity_entity_map_t::const_iterator eit = entity_file_map.find(*it);
					if (eit == entity_file_map.end()) throw IfcParse::IfcException("Unable to map instance to file");
					new_instances->push(eit->second);
				}
				we->setArgument(i, new_instances);
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
				we->setArgument(i, new_instances);
			} else if (entity->getArgumentEntity(i) == IfcSchema::Type::IfcLengthMeasure ||
				entity->getArgumentEntity(i) == IfcSchema::Type::IfcPositiveLengthMeasure) 
			{
				if (!conversion_factor) {
					conversion_factor = other_file->getUnit(IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT).second / 
						getUnit(IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT).second;
				}
				if (attr_type == IfcUtil::Argument_DOUBLE) {
					double v = *attr;
					v *= *conversion_factor;
					we->setArgument(i, v);
				} else if (attr_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
					std::vector<double> v = *attr;
					for (std::vector<double>::iterator it = v.begin(); it != v.end(); ++it) {
						(*it) *= *conversion_factor;
					}
					we->setArgument(i, v);
				}
			}
		}

		// A new entity instance name is generated and
		// the instance is pointed to this file.
		we->file = this;
		we->setId(FreshId());
	}

	// For subtypes of IfcRoot, the GUID mapping needs to be updated.
	if (entity->is(IfcSchema::Type::IfcRoot)) {
		IfcSchema::IfcRoot* ifc_root = (IfcSchema::IfcRoot*) entity;
		try {
			const std::string guid = ifc_root->GlobalId();
			if ( byguid.find(guid) != byguid.end() ) {
				std::stringstream ss;
				ss << "Overwriting entity with guid " << guid;
				Logger::Message(Logger::LOG_WARNING,ss.str());
			}
			byguid[guid] = ifc_root;
		} catch (const IfcException& ex) {
			Logger::Message(Logger::LOG_ERROR,ex.what());
		}
	}

	// The mapping by entity type is updated.
	IfcSchema::Type::Enum ty = entity->type();
	do {
		IfcEntityList::ptr instances_by_type = entitiesByType(ty);
		if (!instances_by_type) {
			instances_by_type = IfcEntityList::ptr(new IfcEntityList());
			bytype[ty] = instances_by_type;
		}
		instances_by_type->push(entity);
		ty = IfcSchema::Type::Parent(ty);
	} while ( ty > -1 );
	
	int new_id = -1;
	if (entity->entity->isWritable() && !entity->entity->file) {
		// For newly created entities ensure a valid ENTITY_INSTANCE_NAME is set
		entity->entity->file = this;
		new_id = entity->entity->isWritable()->setId();
	} else {
		new_id = entity->entity->id();
	}

	if (byid.find(new_id) != byid.end()) {
		// This should not happen
		std::stringstream ss;
		ss << "Overwriting entity with id " << new_id;
		Logger::Message(Logger::LOG_WARNING, ss.str());
	}

	// The mapping by entity instance name is updated.
	byid[new_id] = entity;

	// The mapping by reference is updated.
	IfcEntityList::ptr entity_attributes(new IfcEntityList);
	try {
		entity_attributes = traverse(entity, 1);
	} catch (...) {}
	for (IfcEntityList::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
		IfcUtil::IfcBaseClass* entity_attribute = *it;
		if (*it == entity) continue;
		try {
			if (!IfcSchema::Type::IsSimple(entity_attribute->type())) {
				unsigned entity_attribute_id = entity_attribute->entity->id();
				IfcEntityList::ptr refs = entitiesByReference(entity_attribute_id);
				if (!refs) {
					refs = IfcEntityList::ptr(new IfcEntityList);
					byref[entity_attribute_id] = refs;
				}
				refs->push(entity);
			}
		} catch (const IfcParse::IfcException&) {}
	}

	return entity;
}

IfcWrite::IfcWritableEntity* make_writable(IfcUtil::IfcBaseClass* instance) {
	if (instance->entity->isWritable()) {
		return instance->entity->isWritable();
	}

	IfcWrite::IfcWritableEntity* return_value;
	instance->entity = return_value = new IfcWrite::IfcWritableEntity(instance->entity);
	return return_value;
}

void IfcFile::removeEntity(IfcUtil::IfcBaseClass* entity) {
	const unsigned id = entity->entity->id();
	IfcUtil::IfcBaseClass* file_entity = entityById(id);

	// TODO: Create a set of weak relations. Inverse relations that do not dictate an 
	// instance to be retained. For example: when deleting an IfcRepresentation, the 
	// individual IfcRepresentationItems can not be deleted if an IfcStyledItem is 
	// related. Hence, the IfcRepresentationItem::StyledByItem relation could be 
	// characterized as weak. 
	std::set<IfcSchema::Type::Enum> weak_roots;

	if (entity != file_entity) {
		throw IfcParse::IfcException("Instance not part of this file");
	}

	std::set<IfcUtil::IfcBaseClass*> deletion_queue;
	IfcEntityList::ptr references = entitiesByReference(id);

	// Alter entity instances with INVERSE relations to the entity being 
	// deleted. This is necessary to maintain a valid IFC file, because 
	// dangling references to it's entities name should be removed. At this
	// moment, inversely related instances affected by the removal of the
	// entity being deleted are not deleted themselves.
	if (references) {
		for (IfcEntityList::it it = references->begin(); it != references->end(); ++it) {
			IfcUtil::IfcBaseEntity* related_instance = (IfcUtil::IfcBaseEntity*) *it;
			for (unsigned i = 0; i < related_instance->getArgumentCount(); ++i) {
				Argument* attr = related_instance->getArgument(i);
				if (attr->isNull()) continue;

				IfcUtil::ArgumentType attr_type = related_instance->getArgumentType(i);
				switch(attr_type) {
				case IfcUtil::Argument_ENTITY_INSTANCE: {
					IfcUtil::IfcBaseClass* instance_attribute = *attr;
					if (instance_attribute == entity) {
						make_writable(related_instance)->setArgument(i);
						// deletion_queue.insert(related_instance);
					} }
					break;
				case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
					IfcEntityList::ptr instance_list = *attr;
					if (instance_list->contains(entity)) {
						instance_list->remove(entity);
						make_writable(related_instance)->setArgument(i, instance_list);
						/* if (instance_list->size() == 0) {
							deletion_queue.insert(related_instance);
						} */
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
						make_writable(related_instance)->setArgument(i, new_list);
						/* if (new_list->totalSize() == 0) {
							deletion_queue.insert(related_instance);
						} */
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
		entitiesByReference(entity_attribute->entity->id())->remove(entity);
		if (entitiesByReference(entity_attribute->entity->id())->filtered(weak_roots)->size() == 0) {
			deletion_queue.insert(entity_attribute);
		}
	}

	if (entity->is(IfcSchema::Type::IfcRoot)) {
		const std::string global_id = ((IfcSchema::IfcRoot*) entity)->GlobalId();
		byguid.erase(byguid.find(global_id));
	}
	
	byid.erase(byid.find(id));
	
	IfcEntityList::ptr instances_of_same_type = entitiesByType(entity->type());
	instances_of_same_type->remove(entity);

	while (!deletion_queue.empty()) {
		removeEntity(*deletion_queue.begin());
		deletion_queue.erase(deletion_queue.begin());
	}

	delete entity->entity;
	delete entity;
}

IfcEntityList::ptr IfcFile::entitiesByType(IfcSchema::Type::Enum t) {
	entities_by_type_t::const_iterator it = bytype.find(t);
	return (it == bytype.end()) ? IfcEntityList::ptr() : it->second;
}

IfcEntityList::ptr IfcFile::entitiesByType(const std::string& t) {
	std::string ty = t;
	for (std::string::iterator p = ty.begin(); p != ty.end(); ++p ) *p = toupper(*p);
	return entitiesByType(IfcSchema::Type::FromString(ty));
}

IfcEntityList::ptr IfcFile::entitiesByReference(int t) {
	entities_by_ref_t::const_iterator it = byref.find(t);
	return (it == byref.end()) ? IfcEntityList::ptr() : it->second;
}

IfcUtil::IfcBaseClass* IfcFile::entityById(int id) {
	entity_by_id_t::const_iterator it = byid.find(id);
	if (it == byid.end()) {
		throw IfcException("Entity not found");
	}
	return it->second;
}

IfcSchema::IfcRoot* IfcFile::entityByGuid(const std::string& guid) {
	entity_by_guid_t::const_iterator it = byguid.find(guid);
	if ( it == byguid.end() ) {
		throw IfcException("Entity not found");
	} else {
		return it->second;
	}
}

// FIXME: Test destructor to delete entity and arg allocations
IfcFile::~IfcFile() {
	for( entity_by_id_t::const_iterator it = byid.begin(); it != byid.end(); ++ it ) {
		delete it->second->entity;
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

std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f) {
	f.header().write(os);

	for ( IfcFile::entity_by_id_t::const_iterator it = f.begin(); it != f.end(); ++ it ) {
		const IfcUtil::IfcBaseClass* e = it->second;
		if (!IfcSchema::Type::IsSimple(e->type())) {
			os << e->entity->toString(true) << ";" << std::endl;
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

IfcEntityList::ptr IfcFile::getInverse(int instance_id, IfcSchema::Type::Enum type, int attribute_index) {
	IfcUtil::IfcBaseClass* instance = entityById(instance_id);

	IfcEntityList::ptr l = IfcEntityList::ptr(new IfcEntityList);
	IfcEntityList::ptr all = entitiesByReference(instance_id);
	if (!all) return l;

	for(IfcEntityList::it it = all->begin(); it != all->end(); ++it) {
		bool valid = type == IfcSchema::Type::UNDEFINED || (*it)->is(type);
		if (valid && attribute_index >= 0) {
			Argument* arg = (*it)->entity->getArgument(attribute_index);
			if (arg->type() == IfcUtil::Argument_ENTITY_INSTANCE) {
				valid = instance == *arg;
			} else if (arg->type() == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
				IfcEntityList::ptr li = *arg;
				valid = li->contains(instance);
			} else if (arg->type() == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
				IfcEntityListList::ptr li = *arg;
				valid = li->contains(instance);
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
	schema_identifiers.push_back(IfcSchema::Identifier);

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

std::pair<IfcSchema::IfcNamedUnit*, double> IfcFile::getUnit(IfcSchema::IfcUnitEnum::IfcUnitEnum type) {
	std::pair<IfcSchema::IfcNamedUnit*, double> return_value((IfcSchema::IfcNamedUnit*)0, 1.);
	IfcSchema::IfcProject::list::ptr projects = entitiesByType<IfcSchema::IfcProject>();
	if (projects->size() == 1) {
		IfcSchema::IfcProject* project = *projects->begin();
		IfcEntityList::ptr units = project->UnitsInContext()->Units();
		for (IfcEntityList::it it = units->begin(); it != units->end(); ++it) {
			IfcSchema::IfcUnit* unit = *it;
			if (unit->is(IfcSchema::Type::IfcNamedUnit)) {
				IfcSchema::IfcNamedUnit* named_unit = (IfcSchema::IfcNamedUnit*) unit;
				if (named_unit->UnitType() != type) {
					continue;
				}
				IfcSchema::IfcSIUnit* unit = 0;
				if (named_unit->is(IfcSchema::Type::IfcConversionBasedUnit)) {
					IfcSchema::IfcConversionBasedUnit* u = (IfcSchema::IfcConversionBasedUnit*)named_unit;
					IfcSchema::IfcMeasureWithUnit* mu = u->ConversionFactor();
					return_value.second *= static_cast<double>(*mu->ValueComponent()->entity->getArgument(0));
					return_value.first = named_unit;
					if (mu->UnitComponent()->is(IfcSchema::Type::IfcSIUnit)) {
						unit = (IfcSchema::IfcSIUnit*) mu->UnitComponent();
					}
				} else if (named_unit->is(IfcSchema::Type::IfcSIUnit)) {
					return_value.first = unit = (IfcSchema::IfcSIUnit*) named_unit;
				}
				if (unit) {
					if (unit->hasPrefix()) {
						return_value.second *= IfcSIPrefixToValue(unit->Prefix());
					}
				}
			}
		}
	}
	return return_value;
}