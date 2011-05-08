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

Argument::Argument(const std::string& s) {
	const char first = s[0];
	const int strlen = s.size();
	const char last = s[strlen-1];		
	if ( first == '#' ) {
		type = IDENTIFIER;
		std::istringstream iss(s.substr(1));
		iss >> _data;
	} else if ( first == '(' || first == ')' || first == '=' || first == '$' || first == '*' || first == ';' || first == ',' ) {
		type = OPERATOR;
		_data = first;
	} else if ( first == '\'' && last == '\'' ) {
		type = STRING;
		_data = -1;
		std::string t = s.substr(1,s.size()-2);
		for ( int i = 0; i < (int)argstrings.size(); ++ i ) if ( argstrings[i] == t ) { _data = i; break; }
		if ( _data == -1 ) { _data = argstrings.size(); argstrings.push_back(t); }
	} else if ( first == '.' && last == '.' ) {
		type = ENUMERATION;
		_data = -1;
		std::string t = s.substr(1,s.size()-2);
		for ( int i = 0; i < (int)enumstrings.size(); ++ i ) if ( enumstrings[i] == t ) { _data = i; break; }
		if ( _data == -1 ) { _data = enumstrings.size(); enumstrings.push_back(t); }
	} else if ( ( first >= 48 && first <= 57 ) || first == '-' || first == '.' ) {
		type = NUMBER;
		std::istringstream iss(s);
		iss >> _number;
	} else {
		type = DATATYPE;
		_data = -1;
		for ( int i = 0; i < (int)datatypes.size(); ++ i ) if ( datatypes[i] == s ) { _data = i; break; }
		if ( _data == -1 ) { _data = datatypes.size(); datatypes.push_back(s); }
	}
}
std::string Argument::s() const {
	if ( type == OPERATOR ) { std::string r; r.push_back((char)_data); return r; }
	if ( type == DATATYPE ) return datatypes[_data];
	if ( type == STRING ) return argstrings[_data];
	if ( type == ENUMERATION ) return enumstrings[_data];
	throw IfcException();
}
float Argument::f() const {
	if ( type != NUMBER ) throw IfcException();
	return _number;
}
int Argument::i() const {
	if ( type != IDENTIFIER ) throw IfcException();
	return _data;
}
bool Argument::b() const {
	if ( type != ENUMERATION ) throw IfcException();
	return s() == "T";
}
bool Argument::isOp(char op) const {
	return type == OPERATOR && ( op == 0 || op == ((char)_data) );
}
std::string Argument::toString() const {
	if ( type == DATATYPE ) return s();
	else if ( type == OPERATOR ) return s();
	std::stringstream ss;
	if ( type == NUMBER ) ss << f();
	else if ( type == STRING ) ss << "'" << s() << "'";
	else if ( type == ENUMERATION ) ss << "." << s() << ".";
	else if ( type == IDENTIFIER ) ss << "#" << i();
	return ss.str();
}
std::vector<std::string> Argument::datatypes;
std::vector<std::string> Argument::argstrings;
std::vector<std::string> Argument::enumstrings;

ArgumentList::ArgumentList() {
	_levels.push_back(this);
	_current = this;
	_arg = 0;
}
void ArgumentList::_push() {
	ArgumentList* a = new ArgumentList();
	_levels.push_back(a);
	_args.push_back(a);
	_current = a;
}
void ArgumentList::_pop() {
	if ( _levels.empty() ) return;
	_current = _levels.back();
	_levels.pop_back();
}
void ArgumentList::_append(const Argument* v) {
	ArgumentList* a = new ArgumentList();
	a->_arg = v;
	_current->_args.push_back(a);
}

std::string ArgumentList::toString() const {
	if ( _arg ) return _arg->toString();
	std::stringstream ss; ss << "(";
	std::vector<ArgumentList*>::const_iterator it;
	for ( it = _args.begin() ; it != _args.end(); ++ it ) {
		if ( it != _args.begin() ) ss << ",";
		ss << (*it)->toString();
	}
	ss << ")";
	return ss.str();
}

float ArgumentList::f() const { return _arg->f(); }
bool ArgumentList::b() const { return _arg->b(); }
int ArgumentList::i() const { return _arg->i(); }
std::string ArgumentList::s() const { return _arg->s(); }
int ArgumentList::count() const { return _arg ? 1 : _args.size(); }
ArgumentList* ArgumentList::arg(int i) const { return _args[i]; }

EntityPtr ArgumentList::ref() const {
	if ( _arg->isOp('$') ) throw IfcException();
	return Ifc::EntityById(_arg->i());
}
EntitiesPtr ArgumentList::refs() const {
	EntitiesPtr l (new Entities());
	std::vector<ArgumentList*>::const_iterator it;
	for ( it = _args.begin(); it != _args.end(); ++ it ) {
		ArgumentList* a = *it;
		if ( a->_arg && a->_arg->type == Argument::IDENTIFIER ) {
			l->push(Ifc::EntityById(a->_arg->i()));
		}
	}
	return l;
}
ArgumentList::~ArgumentList() {
	if ( _arg ) delete _arg;
	else {
		while( ! _args.empty() ) {
			delete _args.back(); _args.pop_back();
		}
	}
}
inline bool Entity::term(char last) {
	return last == '(' || last == ')' || last == '=' || last == ',' || last == ';';
}
Entity::Entity(std::istream* ss, std::vector<int>& refs) {
	std::string curvar;
	curvar.reserve(64);
	bool inStr = false;
	char c[1] = "";
	int state = -1;
	args = 0;
	_dt = 0;
	id = -1;
	do {
		ss->read(c,1);
		if ( !inStr && ((*c) == ' ' || (*c) == '\r' || (*c) == '\n' || (*c) == '\t') ) continue;
		if ( curvar.size() && !inStr && ( term(*c) || term(*curvar.rbegin())) ) {
			Argument* v = new Argument(curvar);
			curvar.clear();
			curvar.push_back(*c);
			if ( state < 10 ) state ++;
			if ( state == 0 ) {
				if ( v->type == Argument::IDENTIFIER ) {
					id = v->i(); 
				} else {
					state = -1;
				}
			} else if ( state == 1 ) {
				if ( ! v->isOp('=') ) state = -1;
			} else if ( state == 2 ) {
				if ( v->type == Argument::DATATYPE ) {
					dt = IfcSchema::Enum::FromString(v->s());
					_dt = v;
					continue;
				}
			} else if ( args ) {
				if ( v->isOp('(') ) args->_push();
				else if ( v->isOp(')') ) args->_pop();
				else if ( ! v->isOp(',') && !v->isOp(';') ) {
					args->_append(v);
					if ( v->type == Argument::IDENTIFIER ) refs.push_back(v->i());
					continue;
				}
			} else if ( v->isOp('(') ) {
				args = new ArgumentList();
			}
			delete v;
		} else curvar.push_back(*c);
		if ( *c == '\'' ) inStr = !inStr;
	} while ( !ss->eof() && (*c != ';' || inStr) );
}
Entity::~Entity() {
	delete args;
	delete _dt;
}
bool Entity::isAssignment() const {
	return args > 0;
}
std::string Entity::datatype() const {
	if ( _dt ) return _dt->s();
	else return IfcSchema::Enum::ToString(dt);
}
ArgumentList* Entity::arg(int i) const {
	return this->args->arg(i);
}
std::string Entity::toString() const {
	std::stringstream ss;
	if ( isAssignment() ) {
		ss << "#" << id << "=" << datatype() << args->toString();
	}
	return ss.str();
}
EntitiesPtr Entity::parents(IfcSchema::Enum::IfcTypes c) {
	EntitiesPtr l = EntitiesPtr(new Entities());
	EntitiesPtr all = Ifc::EntitiesByReference(id);
	if ( ! all ) return l;
	for( Entities::it it = all->begin(); it != all->end();++  it  ) {
		if ( c == IfcSchema::Enum::ALL || (*it)->dt == c ) {
			l->push(*it);
		}
	}
	return l;
}
EntitiesPtr Entity::parents(IfcSchema::Enum::IfcTypes c, int i, const std::string& a) {
	EntitiesPtr l = EntitiesPtr(new Entities());
	EntitiesPtr all = parents(c);
	for( Entities::it it = all->begin(); it != all->end();++ it  ) {
		if ( (*it)->arg(i)->s() == a ) {
			l->push(*it);
		}
	}
	return l;
}

void Entities::push(EntityPtr l) {
	if ( l ) {
		ls.push_back(l);
		size = ls.size();
	}
}
void Entities::pushs(EntitiesPtr l) {
	for( it i = l->begin(); i != l->end(); ++i  ) {
		if ( *i ) ls.push_back(*i);
	}
	size = ls.size();
}
Entities::it Entities::begin() { return ls.begin(); }
Entities::it Entities::end() { return ls.end(); }
EntitiesPtr Entities::parents(IfcSchema::Enum::IfcTypes c) {
	EntitiesPtr l = EntitiesPtr(new Entities());
	for( it i = begin(); i != end(); ++i  ) {
		l->pushs((*i)->parents(c));
	}
	return l;
}
EntitiesPtr Entities::parents(IfcSchema::Enum::IfcTypes c, int ar, const std::string& a) {
	EntitiesPtr l = EntitiesPtr(new Entities());
	for( it i = begin(); i != end(); ++i  ) {
		l->pushs((*i)->parents(c,ar,a));
	}
	return l;
}
EntityPtr Entities::operator[] (int i) {
	return ls[i];
}
Entities::Entities() {
	size = 0;
}

File::File(std::string fn, bool debug) {
	valid = false;
	std::ifstream f(fn.c_str());
	if ( ! f.is_open() ) return;
	valid = true;
	std::istream *pf = (std::istream*) &f;
	while( !pf->eof() ) {
		std::vector<int> refs;
		EntityPtr il (new Entity(pf,refs));
		if ( il->isAssignment() ) {
			if ( debug )
				std::cout << il->toString();
			if ( il->dt == IfcSchema::Enum::IfcDontCare ) {
				continue;
			}
			EntitiesPtr l = EntitiesByType(il->dt);
			if ( l == 0 ) {
				l = EntitiesPtr(new Entities());
				bytype[il->dt] = l;
			}
			l->push(il);
			byid[il->id] = il;
			
			std::vector<int>::const_iterator it;
			for( it = refs.begin(); it != refs.end();++ it  ) {
				const int _id = *it;
				EntitiesPtr L = EntitiesByReference(_id);
				if ( L == 0 ) {
					L = EntitiesPtr(new Entities());
					byref[_id] = L;
				}
				L->push(il);
			}
		}
	}
	f.close();
}
EntitiesPtr File::EntitiesByType(IfcSchema::Enum::IfcTypes t) {
	std::map<IfcSchema::Enum::IfcTypes,EntitiesPtr>::const_iterator it;
	it = bytype.find(t);
	return (it == bytype.end()) ? EntitiesPtr() : (*it).second;
}
EntitiesPtr File::EntitiesByReference(int t) {
	std::map<int,EntitiesPtr>::const_iterator it;
	it = byref.find(t);
	return (it == byref.end()) ? EntitiesPtr() : (*it).second;
}
EntityPtr File::EntityById(int id) {
	std::map<int,EntityPtr>::const_iterator it;
	it = byid.find(id);
	if ( it == byid.end() ) throw IfcException(id);
	return (*it).second;
}
IfcException::IfcException(int id) {
	std::stringstream ss;
	ss << "Unable to find IFC Entity #" << id;
	w = ss.str();
}

IfcException::IfcException() {
	w = "Unexpected argument supplied";
}

const char* IfcException::what() const throw(){ return w.c_str(); }
IfcException::~IfcException() throw(){ }

EntitiesPtr Ifc::EntitiesByType(IfcSchema::Enum::IfcTypes t) {
	return f->EntitiesByType(t);
}
EntitiesPtr Ifc::EntitiesByReference(int t) {
	return f->EntitiesByReference(t);
}
EntityPtr Ifc::EntityById(int id) {
	return f->EntityById(id);
}
bool Ifc::Init(std::string fn) {
	f = new File(fn, false);
	IfcEntities units = EntitiesByType(IfcSchema::Enum::IfcSIUnit);
	Ifc::Scale = 1.0f;
	if ( units )
	for ( IfcParse::Entities::it it = units->begin(); it != units->end(); it ++ ) {
		IfcSchema::SIUnit* unit = (IfcSchema::SIUnit*)(*it).get();
		if ( unit->Type() == "LENGTHUNIT" ) {
			if      ( unit->Prefix() == "EXA"   ) Ifc::Scale = (float) 1e18;
			else if ( unit->Prefix() == "PETA"  ) Ifc::Scale = (float) 1e15;
			else if ( unit->Prefix() == "TERA"  ) Ifc::Scale = (float) 1e12;
			else if ( unit->Prefix() == "GIGA"  ) Ifc::Scale = (float) 1e9;
			else if ( unit->Prefix() == "MEGA"  ) Ifc::Scale = (float) 1e6;
			else if ( unit->Prefix() == "KILO"  ) Ifc::Scale = (float) 1e3;
			else if ( unit->Prefix() == "HECTO" ) Ifc::Scale = (float) 1e2;
			else if ( unit->Prefix() == "DECA"  ) Ifc::Scale = (float) 1;
			else if ( unit->Prefix() == "DECI"  ) Ifc::Scale = (float) 1e-1;
			else if ( unit->Prefix() == "CENTI" ) Ifc::Scale = (float) 1e-2;
			else if ( unit->Prefix() == "MILLI" ) Ifc::Scale = (float) 1e-3;
			else if ( unit->Prefix() == "MICRO" ) Ifc::Scale = (float) 1e-6;
			else if ( unit->Prefix() == "NANO"  ) Ifc::Scale = (float) 1e-9;
			else if ( unit->Prefix() == "PICO"  ) Ifc::Scale = (float) 1e-12;
			else if ( unit->Prefix() == "FEMTO" ) Ifc::Scale = (float) 1e-15;
			else if ( unit->Prefix() == "ATTO"  ) Ifc::Scale = (float) 1e-18;
		}
	}
	return f->valid;
}
void Ifc::Dispose() {
	delete f;
	Argument::datatypes.clear();
	Argument::argstrings.clear();
	Argument::enumstrings.clear();
}
File* Ifc::f = 0;
float Ifc::Scale = 1.0f;
