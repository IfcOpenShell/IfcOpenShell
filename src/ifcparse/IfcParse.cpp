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
File::File(const std::string& fn) {
	eof = false;
	stream.open(fn.c_str(),std::ios_base::binary);
	if ( ! stream.good() ) {
		valid = false;
		return;
	}
	valid = true;
	stream.seekg(0,std::ios_base::end);
	size = (unsigned int) stream.tellg();
	stream.seekg(0,std::ios_base::beg);
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

File::File(std::istream& f, int l) {
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

File::File(void* data, int l) {
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

void File::Close() {
	stream.close();
	delete[] buffer;
}

//
// Reads a chunk of BUF_SIZE in memory and increments cursor if requested
//
void File::ReadBuffer(bool inc) {
#ifdef BUF_SIZE
	if ( inc ) {
		offset += len;
		stream.seekg(offset,std::ios_base::beg);
	}
#endif
	eof = stream.eof();
	if ( eof ) return;
#ifdef BUF_SIZE
	stream.read(buffer,size < BUF_SIZE ? size : BUF_SIZE);
#else
	stream.read(buffer,size);
#endif
	len = (unsigned int) stream.gcount();
	eof = len == 0;
	ptr = 0;
}

//
// Seeks an arbitrary position in the file
//
void File::Seek(unsigned int o) {
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
		stream.clear();
		stream.seekg(o,std::ios_base::beg);
		ReadBuffer(false);
	}
#endif
}

//
// Returns the character at the cursor
//
char File::Peek() {
	return buffer[ptr];
}

//
// Returns the character at specified offset
//
char File::Read(unsigned int o) {
#ifdef BUF_SIZE
	if ( ! paging ) {
#endif
		return buffer[o];
#ifdef BUF_SIZE
	} else if ( o >= offset && (o < (offset+len)) ) {
		return buffer[o-offset];
	} else {
		stream.clear();
		stream.seekg(o,std::ios_base::beg);
		return stream.peek();
	}
#endif
}

//
// Returns the cursor position
//
unsigned int File::Tell() {
#ifdef BUF_SIZE
	return offset + ptr;
#else
	return ptr;
#endif
}

//
// Increments cursor and reads new chunk if necessary
//
void File::Inc() {
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
	const char current = File::Peek();
	if ( current == '\n' || current == '\r' ) File::Inc();
}

Tokens::Tokens(IfcParse::File *f) {
	file = f;
	decoder = new IfcCharacterDecoder(f);
}

Tokens::~Tokens() {
	delete decoder;
}

//
// Returns the offset of the current Token and moves cursor to next
//
Token Tokens::Next() {

	if ( file->eof ) return TokenPtr();

	char c;

	// Trim whitespace
	while ( !file->eof ) {
		c = file->Peek();
		if ( (c == ' ' || c == '\r' || c == '\n' || c == '\t' ) ) file->Inc();
		else break;
	}

	if ( file->eof ) return TokenPtr();
	unsigned int pos = file->Tell();

	bool inString = false;
	bool inComment = false;

	// If the cursor is at [()=,;$*] we know token consists of single char
	if ( c == '(' || c == ')' || c == '=' || c == ',' || c == ';' || c == '$' || c == '*' ) {
		file->Inc();
		return TokenPtr(c);
	}

	int len = 0;

	char p = 0;
	while ( ! file->eof ) {

		// Read character and increment pointer if not starting a new token
		char c = file->Peek();
		if ( len && (!inString || inComment) && (c == '(' || c == ')' || c == '=' || c == ',' || c == ';' ) ) break;
		file->Inc();

		// Skip whitespace if not in comment or string
		if ( !inComment && !inString && (c == ' ' || c == '\r' || c == '\n' || c == '\t' ) ) continue;

		len ++;

		// Keep track of whether cursor is inside a string or comment		
		if ( inComment && p == '*' && c == '/' ) inComment = false;
		else if ( !inString && !inComment && p == '/' && c == '*' ) inComment = true;
		else if ( !inComment && c == '\'' ) decoder->dryRun();

		p = c;
	}
	if ( len ) return TokenPtr(pos);
	else return TokenPtr();
}

//
// Reads a std::string from the file at specified offset
// Omits whitespace and comments
//
std::string Tokens::TokenString(unsigned int offset) {
	const bool was_eof = file->eof;
	unsigned int old_offset = file->Tell();
	file->Seek(offset);
	bool inString = false;
	bool inComment = false;
	std::string buffer;
	buffer.reserve(128);
	char p = 0;
	while ( ! file->eof ) {
		char c = file->Peek();
		if ( buffer.size() && (!inString || inComment) && (c == '(' || c == ')' || c == '=' || c == ',' || c == ';' ) ) break;
		file->Inc();
		if ( !inComment && !inString && (c == ' ' || c == '\r' || c == '\n' || c == '\t' ) ) continue;
		if ( !inComment ) buffer.push_back(c);
		if ( inComment && p == '*' && c == '/' ) inComment = false;
		else if ( !inString && !inComment && p == '/' && c == '*' ) inComment = true;
		else if ( !inComment && c == '\'' ) return *decoder;
		p = c;
	}
	if ( was_eof ) file->eof = true;
	else file->Seek(old_offset);
	return buffer;
}

//
// Functions for creating Tokens from an arbitary file offset.
// The first 4 bits are reserved for Tokens of type ()=,;$*
//
Token IfcParse::TokenPtr(unsigned int offset) { return offset + 128; }
Token IfcParse::TokenPtr(char c) { return c; }
Token IfcParse::TokenPtr() { return 0; }

//
// Functions to convert Tokens to binary data
//
unsigned int TokenFunc::Offset(Token t) { return t - 128; }
bool TokenFunc::startsWith(Token t, char c) {
	return Ifc::file->Read(Offset(t)) == c;
}
bool TokenFunc::isOperator(Token t, char op) {
	return (t < 128) && (!op || op == t);
}
bool TokenFunc::isIdentifier(Token t) {
	return ! isOperator(t) && startsWith(t, '#');
}
bool TokenFunc::isString(Token t) {
	return ! isOperator(t) && startsWith(t, '\'');
}
bool TokenFunc::isEnumeration(Token t) {
	return ! isOperator(t) && startsWith(t, '.');
}
bool TokenFunc::isDatatype(Token t) {
	return ! isOperator(t) && startsWith(t, 'I');
}
int TokenFunc::asInt(Token t) {
	const std::string str = asString(t);
	// In case of an ENTITY_INSTANCE_NAME skip the leading #
	const char* start = str.c_str() + (isIdentifier(t) ? 1 : 0);
	char* end;
	long result = strtol(start,&end,10);
	if ( start == end ) throw IfcException("Token is not an integer or identifier");
	return (int) result;
}
bool TokenFunc::asBool(Token t) {
	const std::string str = asString(t);
	return str == "T";
}
double TokenFunc::asFloat(Token t) {
	const std::string str = asString(t);
	return (double) atof(str.c_str());
}
std::string TokenFunc::asString(Token t) {
	if ( isOperator(t,'$') ) return "";
	else if ( isOperator(t) ) throw IfcException("Token is not a string");
	std::string str = Ifc::tokens->TokenString(t - 128);
	return isString(t) || isEnumeration(t) ? str.substr(1,str.size()-2) : str;
}
std::string TokenFunc::toString(Token t) {
	if ( isOperator(t) ) return std::string ( (char*) &t, 1 );
	else return Ifc::tokens->TokenString(t - 128);
}


TokenArgument::TokenArgument(Token t) {
	token = t;
}

EntityArgument::EntityArgument(Ifc2x3::Type::Enum ty, Token t) {
	entity = new IfcUtil::IfcArgumentSelect(ty,new TokenArgument(t));
}

// 
// Reads the arguments from a list of token
// Aditionally, stores the ids (i.e. #[\d]+) in a vector
//
ArgumentList::ArgumentList(Tokens* t, std::vector<unsigned int>& ids) {
	while( Token next = t->Next() ) {
		if ( TokenFunc::isOperator(next,',') ) continue;
		if ( TokenFunc::isOperator(next,')') ) break;
		if ( TokenFunc::isOperator(next,'(') ) Push( new ArgumentList(t,ids) );
		else {
			if ( TokenFunc::isIdentifier(next) ) ids.push_back(TokenFunc::asInt(next));
			if ( TokenFunc::isDatatype(next) ) {
				t->Next();
				try {
					Push ( new EntityArgument(Ifc2x3::Type::FromString(TokenFunc::asString(next)),t->Next()) );
				} catch ( IfcException& e ) {
					Ifc::LogMessage("Error",e.what());
				}
				t->Next();
			} else {
				Push ( new TokenArgument(next) );
			}
		}
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
TokenArgument::operator IfcUtil::IfcSchemaEntity() const { return Ifc::EntityById(TokenFunc::asInt(token)); }
/*TokenArgument::operator IfcUtil::IfcAbstractSelect::ptr() const {
//TODO Fix memory leak
return new IfcUtil::IfcEntitySelect(*this); 
}*/
TokenArgument::operator IfcEntities() const { throw IfcException("Argument is not a list of entities"); }
unsigned int TokenArgument::Size() const { return 1; }
ArgumentPtr TokenArgument::operator [] (unsigned int i) const { throw IfcException("Argument is not a list of arguments"); }
std::string TokenArgument::toString(bool upper) const { return TokenFunc::toString(token); }
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
	std::string token_string = ( token_arg ) ? TokenFunc::toString(token_arg->token) : "";
	std::string dt = Ifc2x3::Type::ToString(entity->type());
	if ( upper ) {
		for (std::string::iterator p = dt.begin(); p != dt.end(); ++p ) *p = toupper(*p);
	}
	return dt + "(" + token_string + ")";
}
//return entity->entity->toString(); }
bool EntityArgument::isNull() const { return false; }
EntityArgument::~EntityArgument() { delete entity; }

//
// Reads an Entity from the list of Tokens
//
Entity::Entity(unsigned int i, Tokens* t) {
	Token datatype = t->Next();
	if ( ! TokenFunc::isDatatype(datatype)) throw IfcException("Unexpected token while parsing entity");
	_type = Ifc2x3::Type::FromString(TokenFunc::asString(datatype));
	_id = i;
	args = ArgumentPtr();
	offset = TokenFunc::Offset(datatype);
}

//
// Reads an Entity from the list of Tokens at the specified offset in the file
//
Entity::Entity(unsigned int i, Tokens* t, unsigned int o) {
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
		Ifc::file->Seek(offset);
		Token datatype = Ifc::tokens->Next();
		if ( ! TokenFunc::isDatatype(datatype)) throw IfcException("Unexpected token while parsing entity");
		_type = Ifc2x3::Type::FromString(TokenFunc::asString(datatype));
	}
	Token open = Ifc::tokens->Next();
	args = new ArgumentList(Ifc::tokens, ids);
	unsigned int old_offset = Ifc::file->Tell();
	Token semilocon = Ifc::tokens->Next();
	if ( ! TokenFunc::isOperator(semilocon,';') ) Ifc::file->Seek(old_offset);
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
	IfcEntities all = Ifc::EntitiesByReference(_id);
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

//
// Parses the IFC file in fn
// Creates the maps
// Gets the unit definitins from the file
//
bool Ifc::Init(const std::string& fn) {
	return Ifc::Init(new File(fn));
}
bool Ifc::Init(std::istream& f, int len) {
	return Ifc::Init(new File(f,len));
}
bool Ifc::Init(void* data, int len) {
	return Ifc::Init(new File(data,len));
}
bool Ifc::Init(IfcParse::File* f) {
	Ifc2x3::InitStringMap();
	file = f;
	if ( ! file->valid ) return false;
	tokens = new Tokens (file);
	Token token = 0;
	Token previous = 0;
	unsigned int currentId = 0;
	lastId = 0;
	int x = 0;
	EntityPtr e;
	IfcUtil::IfcSchemaEntity entity = 0; 
	if ( log1 ) std::cout << "Scanning file..." << std::endl;
	while ( ! file->eof ) {
		if ( currentId ) {
			try {
				e = new Entity(currentId,tokens);
				entity = Ifc2x3::SchemaEntity(e);
			} catch (IfcException ex) {
				currentId = 0;
				Ifc::LogMessage("Error",ex.what());
				continue;
			}
			if ( log1 && !((++x)%1000) ) std::cout << "\r#" << currentId << "         " << std::flush;
			if ( entity->is(Ifc2x3::Type::IfcRoot) ) {
				Ifc2x3::IfcRoot::ptr ifc_root = (Ifc2x3::IfcRoot::ptr) entity;
				try {
					const std::string guid = ifc_root->GlobalId();
					if ( byguid.find(guid) != byguid.end() ) {
						std::stringstream ss;
						ss << "Overwriting entity with guid " << guid;
						Ifc::LogMessage("Warning",ss.str());
					}
					byguid[guid] = ifc_root;
				} catch (IfcException ex) {
					Ifc::LogMessage("Error",ex.what());
				}
			}
			Ifc2x3::Type::Enum ty = entity->type();
			do {
				IfcEntities L = EntitiesByType(ty);
				if ( L == 0 ) {
					L = IfcEntities(new IfcEntityList());
					bytype[ty] = L;
				}
				L->push(entity);
				ty = Ifc2x3::Type::Parent(ty);
			} while ( ty > -1 );
			if ( byid.find(currentId) != byid.end() ) {
				std::stringstream ss;
				ss << "Overwriting entity with id " << currentId;
				Ifc::LogMessage("Warning",ss.str());
			}
			byid[currentId] = entity;
			MaxId = std::max(MaxId,currentId);
			currentId = 0;
		} else {
			try { token = tokens->Next(); }
			catch (... ) { token = 0; }
		}
		if ( ! token ) break;
		if ( previous && TokenFunc::isIdentifier(previous) ) {
			int id = TokenFunc::asInt(previous);
			if ( TokenFunc::isOperator(token,'=') ) {
				currentId = id;
			} else if (entity) {
				IfcEntities L = EntitiesByReference(id);
				if ( L == 0 ) {
					L = IfcEntities(new IfcEntityList());
					byref[id] = L;
				}
				L->push(entity);
			}
		}
		previous = token;
	}

	if ( log1 ) std::cout << "\rDone scanning file   " << std::endl;

	Ifc2x3::IfcUnitAssignment::list unit_assignments = EntitiesByType<Ifc2x3::IfcUnitAssignment>();
	IfcUtil::IfcAbstractSelect::list units = IfcUtil::IfcAbstractSelect::list();
	if ( unit_assignments->Size() ) {
		Ifc2x3::IfcUnitAssignment::ptr unit_assignment = *unit_assignments->begin();
		units = unit_assignment->Units();
	}
	if ( ! units ) {
		// No units eh... Since tolerances and deflection are specified internally in meters
		// we will try to find another indication of the model size.
		Ifc2x3::IfcExtrudedAreaSolid::list extrusions = EntitiesByType<Ifc2x3::IfcExtrudedAreaSolid>();
		if ( ! extrusions->Size() ) return true;
		double max_height = -1.0f;
		for ( Ifc2x3::IfcExtrudedAreaSolid::it it = extrusions->begin(); it != extrusions->end(); ++ it ) {
			const double depth = (*it)->Depth();
			if ( depth > max_height ) max_height = depth;
		}
		if ( max_height > 100.0f ) Ifc::LengthUnit = 0.001f;
		return true;
	}
	try {
		for ( IfcUtil::IfcAbstractSelect::it it = units->begin(); it != units->end(); ++ it ) {
			const IfcUtil::IfcAbstractSelect::ptr base = *it;
			Ifc2x3::IfcSIUnit::ptr unit = Ifc2x3::IfcSIUnit::ptr();
			double value = 1.0f;
			if ( base->is(Ifc2x3::Type::IfcConversionBasedUnit) ) {
				const Ifc2x3::IfcConversionBasedUnit::ptr u = reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,Ifc2x3::IfcConversionBasedUnit>(base);
				const Ifc2x3::IfcMeasureWithUnit::ptr u2 = u->ConversionFactor();
				Ifc2x3::IfcUnit u3 = u2->UnitComponent();
				if ( u3->is(Ifc2x3::Type::IfcSIUnit) ) {
					unit = (Ifc2x3::IfcSIUnit*) u3;
				}
				Ifc2x3::IfcValue v = u2->ValueComponent();
				IfcUtil::IfcArgumentSelect* v2 = (IfcUtil::IfcArgumentSelect*) v;
				const double f = *v2->wrappedValue();
				value *= f;
			} else if ( base->is(Ifc2x3::Type::IfcSIUnit) ) {
				unit = reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,Ifc2x3::IfcSIUnit>(base);
			}
			if ( unit ) {
				if ( unit->hasPrefix() ) {
					value *= UnitPrefixToValue(unit->Prefix());
				}
				Ifc2x3::IfcUnitEnum::IfcUnitEnum type = unit->UnitType();
				if ( type == Ifc2x3::IfcUnitEnum::IfcUnit_LENGTHUNIT ) {
					Ifc::LengthUnit = value;
				} else if ( type == Ifc2x3::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT ) {
					Ifc::PlaneAngleUnit = value;
					Ifc::hasPlaneAngleUnit = true;
				}
			}
		}
	} catch ( IfcException ex ) {
		Ifc::LogMessage("Error",ex.what());
	}
	return true;
}
void Ifc::AddEntity(IfcUtil::IfcSchemaEntity entity) {
	if ( entity->is(Ifc2x3::Type::IfcRoot) ) {
		Ifc2x3::IfcRoot::ptr ifc_root = (Ifc2x3::IfcRoot::ptr) entity;
		try {
			const std::string guid = ifc_root->GlobalId();
			if ( byguid.find(guid) != byguid.end() ) {
				std::stringstream ss;
				ss << "Overwriting entity with guid " << guid;
				Ifc::LogMessage("Warning",ss.str());
			}
			byguid[guid] = ifc_root;
		} catch (IfcException ex) {
			Ifc::LogMessage("Error",ex.what());
		}
	}
	Ifc2x3::Type::Enum ty = entity->type();
	do {
		IfcEntities L = EntitiesByType(ty);
		if ( L == 0 ) {
			L = IfcEntities(new IfcEntityList());
			bytype[ty] = L;
		}
		L->push(entity);
		ty = Ifc2x3::Type::Parent(ty);
	} while ( ty > -1 );
	int new_id = -1;
	// For newly created entities ensure a valid ENTITY_INSTANCE_NAME is set
	if ( entity->entity->isWritable() ) {
		new_id = ((IfcWrite::IfcWritableEntity*)(entity->entity))->setId();
	} else {
		// TODO: Detect and fix ENTITY_INSTANCE_NAME collisions
		new_id = entity->entity->id();
	}
	if ( byid.find(new_id) != byid.end() ) {
		std::stringstream ss;
		ss << "Overwriting entity with id " << new_id;
		Ifc::LogMessage("Warning",ss.str());
	}
	byid[new_id] = entity;

}

IfcEntities Ifc::EntitiesByType(Ifc2x3::Type::Enum t) {
	MapEntitiesByType::const_iterator it = bytype.find(t);
	return (it == bytype.end()) ? IfcEntities() : it->second;
}
IfcEntities Ifc::EntitiesByType(const std::string& t) {
	std::string ty = t;
	for (std::string::iterator p = ty.begin(); p != ty.end(); ++p ) *p = toupper(*p);
	return EntitiesByType(Ifc2x3::Type::FromString(ty));
}
IfcEntities Ifc::EntitiesByReference(int t) {
	MapEntitiesByRef::const_iterator it = byref.find(t);
	return (it == byref.end()) ? IfcEntities() : it->second;
}
IfcUtil::IfcSchemaEntity Ifc::EntityById(int id) {
	MapEntityById::const_iterator it = byid.find(id);
	if ( it == byid.end() ) {
		MapOffsetById::const_iterator it2 = offsets.find(id);
		if ( it2 == offsets.end() ) throw IfcException("Entity not found");
		const unsigned int offset = (*it2).second;
		EntityPtr e = EntityPtr(new Entity(id,Ifc::tokens,offset));
		IfcUtil::IfcSchemaEntity entity = Ifc2x3::SchemaEntity(e);
		byid[id] = entity;
		return entity;
	}
	return it->second;
}
Ifc2x3::IfcRoot::ptr Ifc::EntityByGuid(const std::string& guid) {
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

void Ifc::Dispose() {
	for( MapEntityById::const_iterator it = byid.begin(); it != byid.end(); ++ it ) {
		delete it->second->entity;
		delete it->second;
	}
	bytype.clear();
	byid.clear();
	byref.clear();
	file->Close();
	delete file;
	delete tokens;
	offsets.clear();
	log_stream.str("");
}

double UnitPrefixToValue( Ifc2x3::IfcSIPrefix::IfcSIPrefix v ) {
	if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_EXA   ) return (double) 1e18;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_PETA  ) return (double) 1e15;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_TERA  ) return (double) 1e12;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_GIGA  ) return (double) 1e9;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_MEGA  ) return (double) 1e6;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_KILO  ) return (double) 1e3;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_HECTO ) return (double) 1e2;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_DECA  ) return (double) 1;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_DECI  ) return (double) 1e-1;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_CENTI ) return (double) 1e-2;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_MILLI ) return (double) 1e-3;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_MICRO ) return (double) 1e-6;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_NANO  ) return (double) 1e-9;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_PICO  ) return (double) 1e-12;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_FEMTO ) return (double) 1e-15;
	else if ( v == Ifc2x3::IfcSIPrefix::IfcSIPrefix_ATTO  ) return (double) 1e-18;
	else return 1.0f;
}
void Ifc::SetOutput(std::ostream* l1, std::ostream* l2) { 
	log1 = l1; 
	log2 = l2; 
	if ( ! log2 ) {
		log2 = &log_stream;
	}
}
void Ifc::LogMessage(const std::string& type, const std::string& message, const IfcAbstractEntityPtr entity) {
	if ( log2 ) {
		(*log2) << "[" << type << "] " << message << std::endl;
		if ( entity ) (*log2) << entity->toString() << std::endl;
	}
}
std::string Ifc::GetLog() {
	return log_stream.str();
}
MapEntityById::const_iterator Ifc::First() {
	return byid.begin();
}
MapEntityById::const_iterator Ifc::Last() {
	return byid.end();
}
void Ifc::Serialize(std::ostream& os) {
	os << "ISO-10303-21;" << std::endl;
	os << "HEADER;" << std::endl;
	os << "FILE_DESCRIPTION(('ViewDefinition []'),'2;1');" << std::endl;
	os << "FILE_NAME('','',(''),('',''),'IfcOpenShell','IfcOpenShell','');" << std::endl;
	os << "FILE_SCHEMA(('IFC2X3'));" << std::endl;
	os << "ENDSEC;" << std::endl;
	os << "DATA;" << std::endl;

	for ( MapEntityById::const_iterator it = First(); it != Last(); ++ it ) {
		const IfcEntity e = it->second;
		os << e->entity->toString(true) << ";" << std::endl;
	}

	os << "ENDSEC;" << std::endl;
	os << "END-ISO-10303-21;" << std::endl;	
}

File* Ifc::file = 0;
std::ostream* Ifc::log1 = 0;
std::ostream* Ifc::log2 = 0;
unsigned int Ifc::lastId = 0;
Tokens* Ifc::tokens = 0;
double Ifc::LengthUnit = 1.0f;
double Ifc::PlaneAngleUnit = 1.0f;
bool Ifc::hasPlaneAngleUnit = false;
bool Ifc::SewShells = false;
int Ifc::CircleSegments = 32;
MapEntitiesByType Ifc::bytype;
MapEntityById Ifc::byid;
MapEntityByGuid Ifc::byguid;
MapEntitiesByRef Ifc::byref;
MapOffsetById Ifc::offsets;
std::stringstream Ifc::log_stream;
int Ifc::Verbosity = 2;
unsigned int Ifc::MaxId = 0;
