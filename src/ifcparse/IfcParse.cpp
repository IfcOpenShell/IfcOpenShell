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

using namespace IfcParse;

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
bool TokenFunc::isKeyword(const Token& t) {
	// bool is a subtype of enumeration, no need to test for that
	return !isOperator(t) && !isIdentifier(t) && !isString(t) && !isEnumeration(t) && !isInt(t) && !isFloat(t);
}
bool TokenFunc::isInt(const Token& t) {
	if (isOperator(t)) return false;
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
	if (isOperator(t)) return false;
	const std::string str = asString(t);
	const char* start = str.c_str();
	char* end;
	double result = strtod(start,&end);
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
	double result = strtod(start,&end);
	if ( start == end ) throw IfcException("Token is not a real");
	return result;
}
std::string TokenFunc::asString(const Token& t) {
	if ( isOperator(t,'$') ) return "";
	else if ( isOperator(t) ) throw IfcException("Token is not a string");
	std::string str = t.first->TokenString(t.second);
	return isString(t) || isEnumeration(t) ? str.substr(1,str.size()-2) : str;
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
ArgumentList::ArgumentList(IfcSpfLexer* t, std::vector<unsigned int>& ids) {
	IfcParse::IfcFile* file = t->file;
	
	Token next = t->Next();
	while( next.second || next.first ) {
		if ( TokenFunc::isOperator(next,',') ) {}
		else if ( TokenFunc::isOperator(next,')') ) break;
		else if ( TokenFunc::isOperator(next,'(') ) Push( new ArgumentList(t,ids) );
		else {
			if ( TokenFunc::isIdentifier(next) ) ids.push_back(TokenFunc::asInt(next));
			if ( TokenFunc::isKeyword(next) ) {
				t->Next();
				try {
					Push ( new EntityArgument(next) );
				} catch ( IfcException& e ) {
					Logger::Message(Logger::LOG_ERROR,e.what());
				}
			} else {
				Push ( new TokenArgument(next) );
			}
		}
		next = t->Next();
	}
}

IfcUtil::ArgumentType ArgumentList::type() const {
	if (list.empty()) return IfcUtil::Argument_UNKNOWN;
	const IfcUtil::ArgumentType elem_type = list[0]->type();
	if (elem_type == IfcUtil::Argument_INT) {
		return IfcUtil::Argument_VECTOR_INT;
	} else if (elem_type == IfcUtil::Argument_DOUBLE) {
		return IfcUtil::Argument_VECTOR_DOUBLE;
	} else if (elem_type == IfcUtil::Argument_STRING) {
		return IfcUtil::Argument_VECTOR_STRING;
	} else if (elem_type == IfcUtil::Argument_ENTITY) {
		return IfcUtil::Argument_ENTITY_LIST;
	} else {
		return IfcUtil::Argument_UNKNOWN;
	}
}

void ArgumentList::Push(Argument* l) {
	list.push_back(l);
}

//
// Functions for casting the ArgumentList to other types
//
ArgumentList::operator int() const { throw IfcException("Argument is not an integer"); }
ArgumentList::operator bool() const { throw IfcException("Argument is not a boolean"); }
ArgumentList::operator double() const { throw IfcException("Argument is not a number"); }
ArgumentList::operator std::string() const { throw IfcException("Argument is not a string"); }
ArgumentList::operator std::vector<double>() const {
	std::vector<double> r;
	std::vector<Argument*>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		r.push_back(**it);
	}
	return r;
}
ArgumentList::operator std::vector<int>() const {
	std::vector<int> r;
	std::vector<Argument*>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		r.push_back(**it);
	}
	return r;
}
ArgumentList::operator std::vector<std::string>() const {
	std::vector<std::string> r;
	std::vector<Argument*>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		r.push_back(**it);
	}
	return r;
}
ArgumentList::operator IfcUtil::IfcBaseClass*() const { throw IfcException("Argument is not an IFC type"); }
//ArgumentList::operator IfcUtil::IfcAbstractSelect::ptr() const { throw IfcException("Argument is not an IFC type"); }
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
unsigned int ArgumentList::Size() const { return (unsigned int) list.size(); }
Argument* ArgumentList::operator [] (unsigned int i) const {
	if ( i >= list.size() ) 
		throw IfcException("Argument index out of range");
	return list[i];
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
		return IfcUtil::Argument_ENTITY;
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
TokenArgument::operator std::vector<double>() const { throw IfcException("Argument is not a list of floats"); }
TokenArgument::operator std::vector<int>() const { throw IfcException("Argument is not a list of ints"); }
TokenArgument::operator std::vector<std::string>() const { throw IfcException("Argument is not a list of strings"); }
TokenArgument::operator IfcUtil::IfcBaseClass*() const { return token.first->file->EntityById(TokenFunc::asInt(token)); }
TokenArgument::operator IfcEntityList::ptr() const { throw IfcException("Argument is not a list of entities"); }
TokenArgument::operator IfcEntityListList::ptr() const { throw IfcException("Argument is not a list of entity lists"); }
unsigned int TokenArgument::Size() const { return 1; }
Argument* TokenArgument::operator [] (unsigned int i) const { throw IfcException("Argument is not a list of arguments"); }
std::string TokenArgument::toString(bool upper) const { 
	if ( upper && TokenFunc::isString(token) ) {
		return IfcWrite::IfcCharacterEncoder(TokenFunc::asString(token)); 
	} else {
		return TokenFunc::toString(token); 
	}
}
bool TokenArgument::isNull() const { return TokenFunc::isOperator(token,'$'); }

IfcUtil::ArgumentType EntityArgument::type() const {
	return IfcUtil::Argument_ENTITY;
}

//
// Functions for casting the EntityArgument to other types
//
EntityArgument::operator int() const { throw IfcException("Argument is not an integer"); }
EntityArgument::operator bool() const { throw IfcException("Argument is not a boolean"); }
EntityArgument::operator double() const { throw IfcException("Argument is not a number"); }
EntityArgument::operator std::string() const { throw IfcException("Argument is not a string"); }
EntityArgument::operator std::vector<double>() const { throw IfcException("Argument is not a list of floats"); }
EntityArgument::operator std::vector<int>() const { throw IfcException("Argument is not a list of ints"); }
EntityArgument::operator std::vector<std::string>() const { throw IfcException("Argument is not a list of strings"); }
EntityArgument::operator IfcUtil::IfcBaseClass*() const { return entity; }
//EntityArgument::operator IfcUtil::IfcAbstractSelect::ptr() const { return entity; }
EntityArgument::operator IfcEntityList::ptr() const { throw IfcException("Argument is not a list of entities"); }
EntityArgument::operator IfcEntityListList::ptr() const { throw IfcException("Argument is not a list of entity lists"); }
unsigned int EntityArgument::Size() const { return 1; }
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
	return args->Size();
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
	args = new ArgumentList(file->tokens, ids);
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
	if ( ! args ) {
		std::vector<unsigned int> ids;
		Load(ids, true);
	}
	std::stringstream ss;
	std::string dt = datatype();
	if ( upper ) {
		for (std::string::iterator p = dt.begin(); p != dt.end(); ++p ) *p = toupper(*p);
	}
	ss << "#" << _id << "=" << dt << args->toString(upper);
	return ss.str();
}

Entity::~Entity() {
	delete args;
}

//
// Returns the entities of type c that have this entity in their ArgumentList
//
IfcEntityList::ptr Entity::getInverse(IfcSchema::Type::Enum c) {
	IfcEntityList::ptr l = IfcEntityList::ptr(new IfcEntityList());
	IfcEntityList::ptr all = file->EntitiesByReference(_id);
	if ( ! all ) return l;
	for( IfcEntityList::it it = all->begin(); it != all->end();++  it  ) {
		if ( c == IfcSchema::Type::ALL || (*it)->is(c) ) {
			l->push(*it);
		}
	}
	return l;
}
IfcEntityList::ptr Entity::getInverse(IfcSchema::Type::Enum c, int i, const std::string& a) {
	IfcEntityList::ptr l = IfcEntityList::ptr(new IfcEntityList());
	IfcEntityList::ptr all = getInverse(c);
	for( IfcEntityList::it it = all->begin(); it != all->end();++ it  ) {
		const std::string s = *(*it)->entity->getArgument(i);
		if ( s == a ) {
			l->push(*it);
		}
	}
	return l;
}
bool Entity::is(IfcSchema::Type::Enum v) const { return _type == v; }
unsigned int Entity::id() { return _id; }

IfcWrite::IfcWritableEntity* Entity::isWritable() {
	return 0;
}

IfcFile::IfcFile(bool create_latebound_entities)
	: _create_latebound_entities(create_latebound_entities)
{
	stream = 0;
	lastId = 0;
	tokens = 0;
	MaxId = 0;
	initTimestamp();
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
		Logger::Message(Logger::LOG_WARNING, std::string("File schema encountered that is different from expected value of '") + IfcSchema::Identifier + "'");
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
			} catch (IfcException ex) {
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
				} catch (IfcException ex) {
					Logger::Message(Logger::LOG_ERROR,ex.what());
				}
			}

			IfcSchema::Type::Enum ty = entity->type();
			do {
				IfcEntityList::ptr instances_by_type = EntitiesByType(ty);
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
				IfcEntityList::ptr instances_by_ref = EntitiesByReference(id);
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
void IfcFile::AddEntities(IfcEntityList::ptr es) {
	for( IfcEntityList::it i = es->begin(); i != es->end(); ++ i ) {
		AddEntity(*i);
	}
}
void IfcFile::AddEntity(IfcUtil::IfcBaseClass* entity) {
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
		} catch (IfcException ex) {
			Logger::Message(Logger::LOG_ERROR,ex.what());
		}
	}

	IfcSchema::Type::Enum ty = entity->type();
	do {
		IfcEntityList::ptr instances_by_type = EntitiesByType(ty);
		if (!instances_by_type) {
			instances_by_type = IfcEntityList::ptr(new IfcEntityList());
			bytype[ty] = instances_by_type;
		}
		instances_by_type->push(entity);
		ty = IfcSchema::Type::Parent(ty);
	} while ( ty > -1 );
	
	int new_id = -1;
	// For newly created entities ensure a valid ENTITY_INSTANCE_NAME is set
	if ( entity->entity->isWritable() ) {
		if ( ! entity->entity->file ) entity->entity->file = this;
		new_id = entity->entity->isWritable()->setId();
	} else {
		// TODO: Detect and fix ENTITY_INSTANCE_NAME collisions
		new_id = entity->entity->id();
	}
	if ( byid.find(new_id) != byid.end() ) {
		std::stringstream ss;
		ss << "Overwriting entity with id " << new_id;
		Logger::Message(Logger::LOG_WARNING,ss.str());
	}
	byid[new_id] = entity;

	unsigned arg_count = entity->entity->getArgumentCount();
	for (unsigned i = 0; i < arg_count; ++i) {
		Argument* arg = entity->entity->getArgument(i);

		// Create a flat list of entity instances referenced by the instance that is being added
		IfcEntityList::ptr entity_attributes(new IfcEntityList);
		if (arg->type() == IfcUtil::Argument_ENTITY) {
			IfcUtil::IfcBaseClass* entity_attribute = *arg;
			entity_attributes->push(entity_attribute);
		} else if (arg->type() == IfcUtil::Argument_ENTITY_LIST) {
			IfcEntityList::ptr entity_list_attribute = *arg;
			entity_attributes->push(entity_list_attribute);
		} else if (arg->type() == IfcUtil::Argument_ENTITY_LIST_LIST) {
			IfcEntityListList::ptr entity_list_attribute = *arg;
			for (IfcEntityListList::outer_it it = entity_list_attribute->begin(); it != entity_list_attribute->end(); ++it) {
				for (IfcEntityListList::inner_it jt = it->begin(); jt != it->end(); ++jt) {
					entity_attributes->push(*jt);
				}
			}
		}

		for (IfcEntityList::it it = entity_attributes->begin(); it != entity_attributes->end(); ++it) {
			IfcUtil::IfcBaseClass* entity_attribute = *it;
			try {
				if (!IfcSchema::Type::IsSimple(entity_attribute->type())) {
					// At this point simple types are IfcSelectHelper instances
					// which are not writable and do not have an instance name.
					if (entity_attribute->entity->isWritable()) {
						if ( ! entity_attribute->entity->file ) {
							entity_attribute->entity->file = this;
						}
						entity_attribute->entity->isWritable()->setId();
					}
					unsigned entity_attribute_id = entity_attribute->entity->id();
					IfcEntityList::ptr refs = EntitiesByReference(entity_attribute_id);
					if (!refs) {
						refs = IfcEntityList::ptr(new IfcEntityList);
						byref[entity_attribute_id] = refs;
					}
					refs->push(entity);
				}
			} catch (IfcParse::IfcException&) {}
		}
	}
}
IfcEntityList::ptr IfcFile::EntitiesByType(IfcSchema::Type::Enum t) {
	entities_by_type_t::const_iterator it = bytype.find(t);
	return (it == bytype.end()) ? IfcEntityList::ptr() : it->second;
}
IfcEntityList::ptr IfcFile::EntitiesByType(const std::string& t) {
	std::string ty = t;
	for (std::string::iterator p = ty.begin(); p != ty.end(); ++p ) *p = toupper(*p);
	return EntitiesByType(IfcSchema::Type::FromString(ty));
}
IfcEntityList::ptr IfcFile::EntitiesByReference(int t) {
	entities_by_ref_t::const_iterator it = byref.find(t);
	return (it == byref.end()) ? IfcEntityList::ptr() : it->second;
}
IfcUtil::IfcBaseClass* IfcFile::EntityById(int id) {
	entity_by_id_t::const_iterator it = byid.find(id);
	if ( it == byid.end() ) {
		offset_by_id_t::const_iterator it2 = offsets.find(id);
		if ( it2 == offsets.end() ) throw IfcException("Entity not found");
		const unsigned int offset = (*it2).second;
		Entity* e = new Entity(id,this,offset);
		IfcUtil::IfcBaseClass* entity = IfcSchema::SchemaEntity(e);
		byid[id] = entity;
		return entity;
	}
	return it->second;
}
IfcSchema::IfcRoot* IfcFile::EntityByGuid(const std::string& guid) {
	entity_by_guid_t::const_iterator it = byguid.find(guid);
	if ( it == byguid.end() ) {
		throw IfcException("Entity not found");
	} else {
		return it->second;
	}
}

IfcException::IfcException(std::string e) { error = e; }
IfcException::~IfcException() throw () {}
const char* IfcException::what() const throw() { return error.c_str(); }

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
	os << "ISO-10303-21;" << std::endl;
	os << "HEADER;" << std::endl;
	os << "FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');" << std::endl;
	os << "FILE_NAME(" 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.filename())) << "," 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.timestamp())) << ",(" 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.authorOrganisation())) << "),(" 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.authorName())) << "," 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.authorEmail())) 
		<< "),'IfcOpenShell " << IFCOPENSHELL_VERSION 
		<< "','IfcOpenShell " << IFCOPENSHELL_VERSION 
		<< "','');" << std::endl;
#ifdef USE_IFC4
	os << "FILE_SCHEMA(('IFC4'));" << std::endl;
#else
	os << "FILE_SCHEMA(('IFC2X3'));" << std::endl;
#endif
	os << "ENDSEC;" << std::endl;
	os << "DATA;" << std::endl;

	for ( IfcFile::entity_by_id_t::const_iterator it = f.begin(); it != f.end(); ++ it ) {
		const IfcUtil::IfcBaseClass* e = it->second;
		os << e->entity->toString(true) << ";" << std::endl;
	}

	os << "ENDSEC;" << std::endl;
	os << "END-ISO-10303-21;" << std::endl;

	return os;
}

void IfcFile::filename(const std::string& s) { _filename = s; }
std::string IfcFile::filename() const { return _filename; }
void IfcFile::timestamp(const std::string& s) { _timestamp = s; }
std::string IfcFile::timestamp() const { return _timestamp; }
void IfcFile::author(const std::string& name, const std::string& email, const std::string& organisation) {
	_author = name;
	_author_email = email;
	_author_organisation = organisation;
}
std::string IfcFile::authorName() const { return _author; }
std::string IfcFile::authorEmail() const { return _author_email; }
std::string IfcFile::authorOrganisation() const { return _author_organisation; }
void IfcFile::initTimestamp() {
	char buf[255];
	time_t t;
	time(&t);
	struct tm * ti = localtime (&t);
	if (strftime(buf,255,"%Y-%m-%dT%H:%M:%S",ti)) {
		_timestamp = std::string(buf);
	}
}