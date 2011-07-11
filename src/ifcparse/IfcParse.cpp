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

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcEnum.h"
#include "../ifcparse/IfcTypes.h"

using namespace IfcParse;

// 
// Opens the file, gets the filesize and reads a chunk in memory
//
File::File(const std::string& fn) {
	eof = false;
	stream.open(fn.c_str(),std::ios_base::binary);
	stream.seekg(0,std::ios_base::end);
	size = stream.tellg();
	stream.seekg(0,std::ios_base::beg);
	buffer = new char[size < BUF_SIZE ? size : BUF_SIZE];
	ptr = 0;
	len = 0;
	offset = 0;
	ReadBuffer(false);
}

void File::Close() {
	stream.close();
	delete[] buffer;
}

//
// Reads a chunk of BUF_SIZE in memory and increments cursor if requested
//
void File::ReadBuffer(bool inc) {
	if ( inc ) {
		offset += len;
		stream.seekg(offset,std::ios_base::beg);
	}
	eof = stream.eof();
	if ( eof ) return;
	stream.read(buffer,size < BUF_SIZE ? size : BUF_SIZE);
	len = stream.gcount();
	eof = len == 0;
	ptr = 0;
}

//
// Seeks an arbitrary position in the file
//
void File::Seek(unsigned int o) {
	if ( o >= offset && (o < (offset+len)) ) {
		ptr = o - offset;
	} else {
		offset = o;
		stream.clear();
		stream.seekg(o,std::ios_base::beg);
		ReadBuffer(false);
	}
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
	if ( o >= offset && (o < (offset+len)) ) {
		return buffer[o-offset];
	} else {
		stream.clear();
		stream.seekg(o,std::ios_base::beg);
		return stream.peek();
	}
}

//
// Returns the cursor position
//
unsigned int File::Tell() {
	return offset + ptr;
}

//
// Increments cursor and reads new chunk if necessary
//
void File::Inc() {
	if ( ++ptr == len ) { ReadBuffer(); }
}

Tokens::Tokens(IfcParse::File *f) {
	file = f;
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
		else if ( !inComment && c == '\'' ) inString = ! inString;

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
		else if ( !inComment && c == '\'' ) inString = ! inString;
		p = c;
	}
	file->Seek(old_offset);
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
	if ( ! isIdentifier(t) ) throw IfcException("Token is not an identifier");
	const std::string str = asString(t);
	return atoi(str.c_str()+1);
}
bool TokenFunc::asBool(Token t) {
	const std::string str = asString(t);
	return str == "T";
}
float TokenFunc::asFloat(Token t) {
	const std::string str = asString(t);
	return (float) atof(str.c_str());
}
std::string TokenFunc::asString(Token t) {
	if ( isOperator(t,'$') ) return "";
	else if ( isOperator(t) ) throw IfcException("Token is not a string");
	std::string str = Ifc::tokens->TokenString(t - 128);
	return isString(t) || isEnumeration(t) ? str.substr(1,str.size()-2) : str;
}
std::string TokenFunc::toString(Token t) {
	if ( isOperator(t) ) return std::string ( (char*) &t, 1 );
	else return asString(t);
}


TokenArgument::TokenArgument(Token t) {
	token = t;
}

EntityArgument::EntityArgument(EntityPtr e) {
	entity = e;
}

// 
// Reads the arguments from a list of token
// Aditionally, stores the ids (i.e. #[\d]+) in a vector
//
ArgumentList::ArgumentList(Tokens* t, std::vector<unsigned int>& ids) {
	while( Token next = t->Next() ) {
		if ( TokenFunc::isOperator(next,',') ) continue;
		if ( TokenFunc::isOperator(next,')') ) break;
		if ( TokenFunc::isOperator(next,'(') ) Push( ArgumentPtr(new ArgumentList(t,ids)) );
		else {
			if ( TokenFunc::isIdentifier(next) ) ids.push_back(TokenFunc::asInt(next));
			if ( TokenFunc::isDatatype(next) ) {
				Ifc::file->Seek(TokenFunc::Offset(next));
				EntityPtr entity = EntityPtr(new Entity(0,t,ids,true));
				Push ( ArgumentPtr(new EntityArgument(entity)) );
			} else {
				Push ( ArgumentPtr(new TokenArgument(next)) );
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
ArgumentList::operator float() const { throw IfcException("Argument is not a number"); }
ArgumentList::operator std::string() const { throw IfcException("Argument is not a string"); }
ArgumentList::operator EntityPtr() const { throw IfcException("Argument is not an IFC type"); }
ArgumentList::operator EntitiesPtr() const {
	EntitiesPtr l (new Entities());
	std::vector<ArgumentPtr>::const_iterator it;
	for ( it = list.begin(); it != list.end(); ++ it ) {
		// FIXME: account for $
		const EntityPtr entity = **it;
		l->push(entity);
	}
	return l;
}
unsigned int ArgumentList::Size() const { return list.size(); }
ArgumentPtr ArgumentList::operator [] (unsigned int i) const {
	if ( i >= list.size() ) 
		throw IfcException("Argument index out of range");
	return list[i];
}
std::string ArgumentList::toString() const {
	std::stringstream ss;
	ss << "(";
	for( std::vector<ArgumentPtr>::const_iterator it = list.begin(); it != list.end(); it ++ ) {
		if ( it != list.begin() ) ss << ",";
		ss << (*it)->toString();
	}
	ss << ")";
	return ss.str();
}

//
// Functions for casting the TokenArgument to other types
//
TokenArgument::operator int() const { return TokenFunc::asInt(token); }
TokenArgument::operator bool() const { return TokenFunc::asBool(token); }
TokenArgument::operator float() const { return TokenFunc::asFloat(token); }
TokenArgument::operator std::string() const { return TokenFunc::asString(token); }
TokenArgument::operator EntityPtr() const { return Ifc::EntityById(TokenFunc::asInt(token)); }
TokenArgument::operator EntitiesPtr() const { throw IfcException("Argument is not a list of entities"); }
unsigned int TokenArgument::Size() const { return 1; }
ArgumentPtr TokenArgument::operator [] (unsigned int i) const { throw IfcException("Argument is not a list of arguments"); }
std::string TokenArgument::toString() const { return TokenFunc::asString(token); }

//
// Functions for casting the EntityArgument to other types
//
EntityArgument::operator int() const { throw IfcException("Argument is not an integer"); }
EntityArgument::operator bool() const { throw IfcException("Argument is not a boolean"); }
EntityArgument::operator float() const { throw IfcException("Argument is not a number"); }
EntityArgument::operator std::string() const { throw IfcException("Argument is not a string"); }
EntityArgument::operator EntityPtr() const { return entity; }
EntityArgument::operator EntitiesPtr() const { throw IfcException("Argument is not a list of entities"); }
unsigned int  EntityArgument::Size() const { return 1; }
ArgumentPtr EntityArgument::operator [] (unsigned int i) const { throw IfcException("Argument is not a list of arguments"); }
std::string EntityArgument::toString() const { return entity->toString(); }

//
// Reads an Entity from the list of Tokens
// If the type of the Entity is not known, the ArgumentList is not loaded
//
Entity::Entity(unsigned int i, Tokens* t, std::vector<unsigned int>& ids, bool parse) {
	Token datatype = t->Next();
	if ( ! TokenFunc::isDatatype(datatype)) throw IfcException("Unexpected token while parsing entity");
	type = IfcSchema::Enum::FromString(TokenFunc::asString(datatype));
	id = i;
	args = ArgumentPtr();
	offset = TokenFunc::Offset(datatype);
	if ( (type != IfcSchema::Enum::IfcDontCare && type != IfcSchema::Enum::IfcUnknown) || parse ) 
		Load(ids, false);
}

//
// Reads an Entity from the list of Tokens at the specified offset in the file
//
Entity::Entity(unsigned int i, Tokens* t, unsigned int o) {
	std::vector<unsigned int> ids;
	id = i;
	offset = o;
	Load(ids, true);
}

//
// Access the Nth argument from the ArgumentList
//
ArgumentPtr Entity::operator [] (unsigned int i) {
	if ( ! args ) {
		std::vector<unsigned int> ids;
		Load(ids, true);
	}
	return (*args)[i];
}

//
// Load the ArgumentList
//
void Entity::Load(std::vector<unsigned int>& ids, bool seek) {
	if ( seek ) {
		Ifc::file->Seek(offset);
		Token datatype = Ifc::tokens->Next();
		if ( ! TokenFunc::isDatatype(datatype) ) throw IfcException("Unexpected token while parsing entity");
		type = IfcSchema::Enum::FromString(TokenFunc::asString(datatype));
	}
	Token open = Ifc::tokens->Next();
	args = ArgumentPtr(new ArgumentList(Ifc::tokens, ids));
	unsigned int old_offset = Ifc::file->Tell();
	Token semilocon = Ifc::tokens->Next();
	if ( ! TokenFunc::isOperator(semilocon,';') ) Ifc::file->Seek(old_offset);
}

//
// Returns a CamelCase string representation of the datatype as it is defined in IfcSchema.h
//
std::string Entity::Datatype() const {
	return IfcSchema::Enum::ToString(type);
}

//
// Returns a string representation of the entity
// Note that this initializes the entity if it is not initialized
//
std::string Entity::toString() {
	if ( ! args ) {
		std::vector<unsigned int> ids;
		Load(ids, true);
	}
	std::stringstream ss;
	ss << "#" << id << "=" << Datatype() << args->toString();
	return ss.str();
}

//
// Returns the entities of type c that have this entity in their ArgumentList
//
EntitiesPtr Entity::parents(IfcSchema::Enum::IfcTypes c) {
	EntitiesPtr l = EntitiesPtr(new Entities());
	EntitiesPtr all = Ifc::EntitiesByReference(id);
	if ( ! all ) return l;
	for( Entities::it it = all->begin(); it != all->end();++  it  ) {
		if ( c == IfcSchema::Enum::ALL || (*it)->type == c ) {
			l->push(*it);
		}
	}
	return l;
}
EntitiesPtr Entity::parents(IfcSchema::Enum::IfcTypes c, int i, const std::string& a) {
	EntitiesPtr l = EntitiesPtr(new Entities());
	EntitiesPtr all = parents(c);
	for( Entities::it it = all->begin(); it != all->end();++ it  ) {
		const std::string s = *((**it)[i]);
		if ( s == a ) {
			l->push(*it);
		}
	}
	return l;
}
void Entities::push(EntityPtr l) {
	if ( l ) ls.push_back(l);
}
void Entities::push(EntitiesPtr l) {
	for( it i = l->begin(); i != l->end(); ++i  ) {
		if ( *i ) ls.push_back(*i);
	}
}
int Entities::Size() const { return ls.size(); }
Entities::it Entities::begin() { return ls.begin(); }
Entities::it Entities::end() { return ls.end(); }

//
// Returns the entities of type c that have one of these entities in their ArgumentList
//
EntitiesPtr Entities::parents(IfcSchema::Enum::IfcTypes c) {
	EntitiesPtr l = EntitiesPtr(new Entities());
	for( it i = begin(); i != end(); ++i  ) {
		l->push((*i)->parents(c));
	}
	return l;
}
EntitiesPtr Entities::parents(IfcSchema::Enum::IfcTypes c, int ar, const std::string& a) {
	EntitiesPtr l = EntitiesPtr(new Entities());
	for( it i = begin(); i != end(); ++i  ) {
		l->push((*i)->parents(c,ar,a));
	}
	return l;
}
EntityPtr Entities::operator[] (int i) {
	return ls[i];
}

//
// Parses the IFC file in fn
// Creates the maps
// Gets the unit definitins from the file
//
bool Ifc::Init(const std::string& fn) {
	file = new File (fn);
	tokens = new Tokens (file);
	Token token = 0;
	Token previous = 0;
	unsigned int currentId = 0;
	lastId = 0;
	int x = 0;
	EntityPtr entity;
	std::cout << "Scanning file..." << std::endl;
	while ( true ) {
		if ( currentId ) {
			std::vector<unsigned int> ids;
			entity = EntityPtr(new Entity(currentId,tokens,ids));
			if ( !((++x)%1000) ) std::cout << "\r#" << currentId << "         ";
			if ( entity->type != IfcSchema::Enum::IfcDontCare && entity->type != IfcSchema::Enum::IfcUnknown) {
				byid[currentId] = entity;
				EntitiesPtr L = EntitiesByType(entity->type);
				if ( L == 0 ) {
					L = EntitiesPtr(new Entities());
					bytype[entity->type] = L;
				}
				L->push(entity);
				for( std::vector<unsigned int>::const_iterator it = ids.begin(); it != ids.end(); ++it ) {
					const int arg_id = *it;
					EntitiesPtr L = EntitiesByReference(arg_id);
					if ( L == 0 ) {
						L = EntitiesPtr(new Entities());
						byref[arg_id] = L;
					}
					L->push(entity);
				}
			} else {
				offsets[currentId] = entity->offset;
			}
			currentId = 0;
		} else token = tokens->Next();
		if ( ! token ) break;
		if ( previous && TokenFunc::isIdentifier(previous) ) {
			int id = TokenFunc::asInt(previous);
			if ( TokenFunc::isOperator(token,'=') ) {
				currentId = id;
			} else {				
				EntitiesPtr L = EntitiesByReference(id);
				if ( L == 0 ) {
					L = EntitiesPtr(new Entities());
					byref[id] = L;
				}
				L->push(entity);
			}
		}
		previous = token;
	}

	std::cout << "\rDone!                     " << std::endl;

	IfcEntity IfcUnitAssigment = *EntitiesByType(IfcSchema::Enum::IfcUnitAssignment)->begin();
	IfcEntities units = ((IfcSchema::UnitAssignment*)IfcUnitAssigment.get())->Units();
	Ifc::LengthUnit = 1.0f;
	if ( units )
		for ( IfcParse::Entities::it it = units->begin(); it != units->end(); it ++ ) {
			IfcEntity unit = *it;
			float value = 1.0f;
			std::string UnitType = "";
			if ( unit->type == IfcSchema::Enum::IfcConversionBasedUnit ) {
				IfcSchema::ConversionBasedUnit* IfcConversionBasedUnit = (IfcSchema::ConversionBasedUnit*)(*it).get();
				IfcSchema::MeasureWithUnit* IfcMeasureWithUnit = (IfcSchema::MeasureWithUnit*)IfcConversionBasedUnit->ConversionFactor().get();
				try {
					unit = IfcMeasureWithUnit->Unit();
					value = *((*IfcMeasureWithUnit->Value())[0]);
				} catch (...) {}
			}
			if ( unit->type == IfcSchema::Enum::IfcSIUnit ) {
				IfcSchema::SIUnit* IfcSIUnit = (IfcSchema::SIUnit*)(*it).get();
				value *= UnitPrefixToValue(IfcSIUnit->UnitPrefix());
				UnitType = IfcSIUnit->UnitType();
			}
			if ( UnitType == "LENGTHUNIT" ) {
				Ifc::LengthUnit = value;
			} else if ( UnitType == "PLANEANGLEUNIT" ) {
				Ifc::PlaneAngleUnit = value;
			}
		}
		return true;
}

EntitiesPtr Ifc::EntitiesByType(IfcSchema::Enum::IfcTypes t) {
	MapEntitiesByType::const_iterator it = bytype.find(t);
	return (it == bytype.end()) ? EntitiesPtr() : it->second;
}
EntitiesPtr Ifc::EntitiesByReference(int t) {
	MapEntitiesByRef::const_iterator it = byref.find(t);
	return (it == byref.end()) ? EntitiesPtr() : it->second;
}
EntityPtr Ifc::EntityById(int id) {
	MapEntityById::const_iterator it = byid.find(id);
	if ( it == byid.end() ) {
		MapOffsetById::const_iterator it2 = offsets.find(id);
		if ( it2 == offsets.end() ) throw IfcException("Entity not found");
		const unsigned int offset = (*it2).second;
		EntityPtr entity = EntityPtr(new Entity(id,Ifc::tokens,offset));
		byid[id] = entity;
		return entity;
	}
	return it->second;
}
IfcException::IfcException(std::string e) { error = e; }
const char* IfcException::what() const { return error.c_str(); }
void Ifc::Dispose() {
	file->Close();
	delete file;
	delete tokens;
	offsets.clear();
	bytype.clear();
	byid.clear();
	byref.clear();
	IfcGeom::Cache::Purge();
}

float UnitPrefixToValue( const std::string& s ) {
	     if ( s == "EXA"   ) return (float) 1e18;
	else if ( s == "PETA"  ) return (float) 1e15;
	else if ( s == "TERA"  ) return (float) 1e12;
	else if ( s == "GIGA"  ) return (float) 1e9;
	else if ( s == "MEGA"  ) return (float) 1e6;
	else if ( s == "KILO"  ) return (float) 1e3;
	else if ( s == "HECTO" ) return (float) 1e2;
	else if ( s == "DECA"  ) return (float) 1;
	else if ( s == "DECI"  ) return (float) 1e-1;
	else if ( s == "CENTI" ) return (float) 1e-2;
	else if ( s == "MILLI" ) return (float) 1e-3;
	else if ( s == "MICRO" ) return (float) 1e-6;
	else if ( s == "NANO"  ) return (float) 1e-9;
	else if ( s == "PICO"  ) return (float) 1e-12;
	else if ( s == "FEMTO" ) return (float) 1e-15;
	else if ( s == "ATTO"  ) return (float) 1e-18;
	else return 1.0f;
}

File* Ifc::file = 0;
unsigned int Ifc::lastId = 0;
Tokens* Ifc::tokens = 0;
float Ifc::LengthUnit = 1.0f;
float Ifc::PlaneAngleUnit = 1.0f;
int Ifc::CircleSegments = 32;
MapEntitiesByType Ifc::bytype;
MapEntityById Ifc::byid;
MapEntitiesByRef Ifc::byref;
MapOffsetById Ifc::offsets;
