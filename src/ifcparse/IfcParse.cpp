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
#include "../ifcparse/IfcFile.h"
#include "../ifcparse/IfcWritableEntity.h"

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

Tokens::Tokens(IfcParse::IfcSpfStream *s, IfcParse::IfcFile* f) {
	file = f;
	stream = s;
	decoder = new IfcCharacterDecoder(s);
}

Tokens::~Tokens() {
	delete decoder;
}

unsigned int Tokens::skipWhitespace() {
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

unsigned int Tokens::skipComment() {
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
Token Tokens::Next() {

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
std::string Tokens::TokenString(unsigned int offset) {
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
Token IfcParse::TokenPtr(Tokens* tokens, unsigned int offset) { return Token(tokens,offset); }
Token IfcParse::TokenPtr(char c) { return Token((Tokens*)0,(unsigned) c); }
Token IfcParse::TokenPtr() { return Token((Tokens*)0,0); }

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
bool TokenFunc::isDatatype(const Token& t) {
	return ! isOperator(t) && startsWith(t, 'I');
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

EntityArgument::EntityArgument(Ifc2x3::Type::Enum ty, const Token& t) {
	entity = new IfcUtil::IfcArgumentSelect(ty,new TokenArgument(t));
}

// 
// Reads the arguments from a list of token
// Aditionally, stores the ids (i.e. #[\d]+) in a vector
//
ArgumentList::ArgumentList(Tokens* t, std::vector<unsigned int>& ids) {
	Token next = t->Next();
	while( next.second || next.first ) {
		if ( TokenFunc::isOperator(next,',') ) {}
		else if ( TokenFunc::isOperator(next,')') ) break;
		else if ( TokenFunc::isOperator(next,'(') ) Push( new ArgumentList(t,ids) );
		else {
			if ( TokenFunc::isIdentifier(next) ) ids.push_back(TokenFunc::asInt(next));
			if ( TokenFunc::isDatatype(next) ) {
				t->Next();
				try {
					Push ( new EntityArgument(Ifc2x3::Type::FromString(TokenFunc::asString(next)),t->Next()) );
				} catch ( IfcException& e ) {
					Logger::Message(Logger::LOG_ERROR,e.what());
				}
				t->Next();
			} else {
				Push ( new TokenArgument(next) );
			}
		}
		next = t->Next();
	}
}

void ArgumentList::Push(ArgumentPtr l) {
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
	std::vector<ArgumentPtr>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		r.push_back(**it);
	}
	return r;
}
ArgumentList::operator std::vector<int>() const {
	std::vector<int> r;
	std::vector<ArgumentPtr>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		r.push_back(**it);
	}
	return r;
}
ArgumentList::operator std::vector<std::string>() const {
	std::vector<std::string> r;
	std::vector<ArgumentPtr>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		r.push_back(**it);
	}
	return r;
}
ArgumentList::operator IfcUtil::IfcSchemaEntity() const { throw IfcException("Argument is not an IFC type"); }
//ArgumentList::operator IfcUtil::IfcAbstractSelect::ptr() const { throw IfcException("Argument is not an IFC type"); }
ArgumentList::operator IfcEntities() const {
	IfcEntities l ( new IfcEntityList() );
	std::vector<ArgumentPtr>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		// FIXME: account for $
		const IfcUtil::IfcSchemaEntity entity = **it;
		l->push(entity);
	}
	return l;
}
unsigned int ArgumentList::Size() const { return (unsigned int) list.size(); }
ArgumentPtr ArgumentList::operator [] (unsigned int i) const {
	if ( i >= list.size() ) 
		throw IfcException("Argument index out of range");
	return list[i];
}
std::string ArgumentList::toString(bool upper) const {
	std::stringstream ss;
	ss << "(";
	for( std::vector<ArgumentPtr>::const_iterator it = list.begin(); it != list.end(); it ++ ) {
		if ( it != list.begin() ) ss << ",";
		ss << (*it)->toString(upper);
	}
	ss << ")";
	return ss.str();
}
bool ArgumentList::isNull() const { return false; }
ArgumentList::~ArgumentList() {
	for( std::vector<ArgumentPtr>::iterator it = list.begin(); it != list.end(); it ++ ) {
		delete (*it);
	}
	list.clear();
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
TokenArgument::operator IfcUtil::IfcSchemaEntity() const { return token.first->file->EntityById(TokenFunc::asInt(token)); }
TokenArgument::operator IfcEntities() const { throw IfcException("Argument is not a list of entities"); }
unsigned int TokenArgument::Size() const { return 1; }
ArgumentPtr TokenArgument::operator [] (unsigned int i) const { throw IfcException("Argument is not a list of arguments"); }
std::string TokenArgument::toString(bool upper) const { 
	if ( upper && TokenFunc::isString(token) ) {
		return IfcWrite::IfcCharacterEncoder(TokenFunc::asString(token)); 
	} else {
		return TokenFunc::toString(token); 
	}
}
bool TokenArgument::isNull() const { return TokenFunc::isOperator(token,'$'); }
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
EntityArgument::operator IfcUtil::IfcSchemaEntity() const {	return entity; }
//EntityArgument::operator IfcUtil::IfcAbstractSelect::ptr() const { return entity; }
EntityArgument::operator IfcEntities() const { throw IfcException("Argument is not a list of entities"); }
unsigned int EntityArgument::Size() const { return 1; }
ArgumentPtr EntityArgument::operator [] (unsigned int i) const { throw IfcException("Argument is not a list of arguments"); }
std::string EntityArgument::toString(bool upper) const { 
	ArgumentPtr arg = entity->wrappedValue();
	IfcParse::TokenArgument* token_arg = dynamic_cast<IfcParse::TokenArgument*>(arg);
	const bool is_string = TokenFunc::isString(token_arg->token);
	std::string token_string = token_arg ? (is_string 
		? TokenFunc::asString(token_arg->token) 
		: TokenFunc::toString(token_arg->token))
		: std::string();
	std::string dt = Ifc2x3::Type::ToString(entity->type());
	if ( upper ) {
		for (std::string::iterator p = dt.begin(); p != dt.end(); ++p ) *p = toupper(*p);
		if (is_string) token_string = IfcWrite::IfcCharacterEncoder(token_string);
	} else {
		token_string.insert(token_string.begin(),'\'');
		token_string.push_back('\'');
	}
	return dt + "(" + token_string + ")";
}
//return entity->entity->toString(); }
bool EntityArgument::isNull() const { return false; }
EntityArgument::~EntityArgument() { delete entity; }

//
// Reads an Entity from the list of Tokens
//
Entity::Entity(unsigned int i, IfcFile* f) { //: file(f) {
	file = f;
	Token datatype = f->tokens->Next();
	if ( ! TokenFunc::isDatatype(datatype)) throw IfcException("Unexpected token while parsing entity");
	_type = Ifc2x3::Type::FromString(TokenFunc::asString(datatype));
	_id = i;
	args = ArgumentPtr();
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
ArgumentPtr Entity::getArgument(unsigned int i) {
	if ( ! args ) {
		std::vector<unsigned int> ids;
		Load(ids, true);
	}
	return (*args)[i];
}

unsigned int Entity::getArgumentCount() {
	if ( ! args ) {
		std::vector<unsigned int> ids;
		Load(ids, true);
	}
	return args->Size();
}

//
// Load the ArgumentList
//
void Entity::Load(std::vector<unsigned int>& ids, bool seek) {
	if ( seek ) {
		file->tokens->stream->Seek(offset);
		Token datatype = file->tokens->Next();
		if ( ! TokenFunc::isDatatype(datatype)) throw IfcException("Unexpected token while parsing entity");
		_type = Ifc2x3::Type::FromString(TokenFunc::asString(datatype));
	}
	Token open = file->tokens->Next();
	args = new ArgumentList(file->tokens, ids);
	unsigned int old_offset = file->tokens->stream->Tell();
	Token semilocon = file->tokens->Next();
	if ( ! TokenFunc::isOperator(semilocon,';') ) file->tokens->stream->Seek(old_offset);
}

Ifc2x3::Type::Enum Entity::type() const {
	return _type;
}

//
// Returns the CamelCase string representation of the datatype as it is defined in the schema
//
std::string Entity::datatype() {
	return Ifc2x3::Type::ToString(_type);
}

//
// Returns a string representation of the entity
// Note that this initializes the entity if it is not initialized
//
std::string Entity::toString(bool upper) {
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
IfcEntities Entity::getInverse(Ifc2x3::Type::Enum c) {
	IfcEntities l = IfcEntities(new IfcEntityList());
	IfcEntities all = file->EntitiesByReference(_id);
	if ( ! all ) return l;
	for( IfcEntityList::it it = all->begin(); it != all->end();++  it  ) {
		if ( c == Ifc2x3::Type::ALL || (*it)->is(c) ) {
			l->push(*it);
		}
	}
	return l;
}
IfcEntities Entity::getInverse(Ifc2x3::Type::Enum c, int i, const std::string& a) {
	IfcEntities l = IfcEntities(new IfcEntityList());
	IfcEntities all = getInverse(c);
	for( IfcEntityList::it it = all->begin(); it != all->end();++ it  ) {
		const std::string s = *(*it)->entity->getArgument(i);
		if ( s == a ) {
			l->push(*it);
		}
	}
	return l;
}
bool Entity::is(Ifc2x3::Type::Enum v) const {	return _type == v; }
unsigned int Entity::id() { return _id; }

bool Entity::isWritable() {
	return false;
}

IfcFile::IfcFile() {
	file = 0;
	lastId = 0;
	tokens = 0;
	MaxId = 0;
	initTimestamp();
}

//
// Parses the IFC file in fn
// Creates the maps
// Gets the unit definitins from the file
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
bool IfcFile::Init(IfcParse::IfcSpfStream* f) {
	Ifc2x3::InitStringMap();
	file = f;
	if ( ! file->valid ) return false;
	tokens = new Tokens (file,this);
	Token token = TokenPtr();
	Token previous = TokenPtr();
	unsigned int currentId = 0;
	lastId = 0;
	int x = 0;
	EntityPtr e;
	IfcUtil::IfcSchemaEntity entity = 0; 
	Logger::Status("Scanning file...");
	while ( ! file->eof ) {
		if ( currentId ) {
			try {
				e = new Entity(currentId,this);
				entity = Ifc2x3::SchemaEntity(e);
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
			if ( entity->is(Ifc2x3::Type::IfcRoot) ) {
				Ifc2x3::IfcRoot::ptr ifc_root = (Ifc2x3::IfcRoot::ptr) entity;
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

			Ifc2x3::Type::Enum ty = entity->type();
			do {
				IfcEntities instances_by_type = EntitiesByType(ty);
				if (!instances_by_type) {
					instances_by_type = IfcEntities(new IfcEntityList());
					bytype[ty] = instances_by_type;
				}
				instances_by_type->push(entity);
				ty = Ifc2x3::Type::Parent(ty);
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
				IfcEntities instances_by_ref = EntitiesByReference(id);
				if (!instances_by_ref) {
					instances_by_ref = IfcEntities(new IfcEntityList());
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
void IfcFile::AddEntities(IfcEntities es) {
	for( IfcEntityList::it i = es->begin(); i != es->end(); ++ i ) {
		AddEntity(*i);
	}
}
void IfcFile::AddEntity(IfcUtil::IfcSchemaEntity entity) {
	if ( entity->is(Ifc2x3::Type::IfcRoot) ) {
		Ifc2x3::IfcRoot::ptr ifc_root = (Ifc2x3::IfcRoot::ptr) entity;
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

	Ifc2x3::Type::Enum ty = entity->type();
	do {
		IfcEntities instances_by_type = EntitiesByType(ty);
		if (!instances_by_type) {
			instances_by_type = IfcEntities(new IfcEntityList());
			bytype[ty] = instances_by_type;
		}
		instances_by_type->push(entity);
		ty = Ifc2x3::Type::Parent(ty);
	} while ( ty > -1 );

	int new_id = -1;
	// For newly created entities ensure a valid ENTITY_INSTANCE_NAME is set
	if ( entity->entity->isWritable() ) {
		if ( ! entity->entity->file ) entity->entity->file = this;
		new_id = ((IfcWrite::IfcWritableEntity*)(entity->entity))->setId();
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

}
IfcEntities IfcFile::EntitiesByType(Ifc2x3::Type::Enum t) {
	MapEntitiesByType::const_iterator it = bytype.find(t);
	return (it == bytype.end()) ? IfcEntities() : it->second;
}
IfcEntities IfcFile::EntitiesByType(const std::string& t) {
	std::string ty = t;
	for (std::string::iterator p = ty.begin(); p != ty.end(); ++p ) *p = toupper(*p);
	return EntitiesByType(Ifc2x3::Type::FromString(ty));
}
IfcEntities IfcFile::EntitiesByReference(int t) {
	MapEntitiesByRef::const_iterator it = byref.find(t);
	return (it == byref.end()) ? IfcEntities() : it->second;
}
IfcUtil::IfcSchemaEntity IfcFile::EntityById(int id) {
	MapEntityById::const_iterator it = byid.find(id);
	if ( it == byid.end() ) {
		MapOffsetById::const_iterator it2 = offsets.find(id);
		if ( it2 == offsets.end() ) throw IfcException("Entity not found");
		const unsigned int offset = (*it2).second;
		EntityPtr e = EntityPtr(new Entity(id,this,offset));
		IfcUtil::IfcSchemaEntity entity = Ifc2x3::SchemaEntity(e);
		byid[id] = entity;
		return entity;
	}
	return it->second;
}
Ifc2x3::IfcRoot::ptr IfcFile::EntityByGuid(const std::string& guid) {
	MapEntityByGuid::const_iterator it = byguid.find(guid);
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
	for( MapEntityById::const_iterator it = byid.begin(); it != byid.end(); ++ it ) {
		delete it->second->entity;
		delete it->second;
	}
	delete file;
	delete tokens;
}

MapEntityById::const_iterator IfcFile::begin() const {
	return byid.begin();
}
MapEntityById::const_iterator IfcFile::end() const {
	return byid.end();
}

std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f) {
	os << "ISO-10303-21;" << std::endl;
	os << "HEADER;" << std::endl;
	os << "FILE_DESCRIPTION(('ViewDefinition []'),'2;1');" << std::endl;
	os << "FILE_NAME(" 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.filename())) << "," 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.timestamp())) << ",(" 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.authorOrganisation())) << "),(" 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.authorName())) << "," 
		<< static_cast<std::string>(IfcWrite::IfcCharacterEncoder(f.authorEmail())) 
		<< "),'IfcOpenShell " << IFCOPENSHELL_VERSION 
		<< "','IfcOpenShell " << IFCOPENSHELL_VERSION 
		<< "','');" << std::endl;
	os << "FILE_SCHEMA(('IFC2X3'));" << std::endl;
	os << "ENDSEC;" << std::endl;
	os << "DATA;" << std::endl;

	for ( MapEntityById::const_iterator it = f.begin(); it != f.end(); ++ it ) {
		const IfcEntity e = it->second;
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