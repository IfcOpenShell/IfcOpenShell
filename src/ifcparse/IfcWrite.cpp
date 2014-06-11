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

#include <iomanip> 

#include "../ifcparse/IfcParse.h" 
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcWritableEntity.h"
#include "../ifcparse/IfcCharacterDecoder.h"

using namespace IfcWrite;

IfcWritableEntity::IfcWritableEntity(IfcSchema::Type::Enum t) {
	_type = t;
	_id = 0;
	file = 0;
}
IfcWritableEntity::~IfcWritableEntity() {
	delete _id;
}
int IfcWritableEntity::setId(int i) {
	if (i > 0) {
		delete _id;
		return *(_id = new int(i));
	} else {
		if (_id) { return *_id; }
		else { 
			delete _id; 
			return *(_id = new int(file->FreshId())); 
		}
	}
}
IfcWritableEntity::IfcWritableEntity(IfcAbstractEntity* e) 
{
	file = e->file;
	_type = e->type();
	delete _id;
	_id = new int(e->id());

	const unsigned int count = e->getArgumentCount();
	for ( unsigned int i = 0; i < count; ++ i ) {
		args[i] = e->getArgument(i);
		writemask[i] = false;
	}
}
// TODO: Reove redundancy with IfcParse::Entity
IfcEntityList::ptr IfcWritableEntity::getInverse(IfcSchema::Type::Enum c) {
	IfcEntityList::ptr l = IfcEntityList::ptr(new IfcEntityList);
	int id = _id ? *_id : setId();
	IfcEntityList::ptr all = file->EntitiesByReference(id);
	if ( ! all ) return l;
	for( IfcEntityList::it it = all->begin(); it != all->end();++  it  ) {
		if ( c == IfcSchema::Type::ALL || (*it)->is(c) ) {
			l->push(*it);
		}
	}
	return l;
}
IfcEntityList::ptr IfcWritableEntity::getInverse(IfcSchema::Type::Enum c, int i, const std::string& a) {
	IfcEntityList::ptr l = IfcEntityList::ptr(new IfcEntityList);
	IfcEntityList::ptr all = getInverse(c);
	for( IfcEntityList::it it = all->begin(); it != all->end();++ it  ) {
		const std::string s = *(*it)->entity->getArgument(i);
		if ( s == a ) {
			l->push(*it);
		}
	}
	return l;
}

std::string IfcWritableEntity::datatype() const { return IfcSchema::Type::ToString(_type); }
Argument* IfcWritableEntity::getArgument (unsigned int i) { if ( i >= getArgumentCount() ) throw IfcParse::IfcException("Argument not set"); return args[i]; }unsigned int IfcWritableEntity::getArgumentCount() const {return args.size(); }
IfcSchema::Type::Enum IfcWritableEntity::type() const { return _type; }
bool IfcWritableEntity::is(IfcSchema::Type::Enum v) const { return _type == v; }
std::string IfcWritableEntity::toString(bool upper) const {
	std::stringstream ss;
	std::string dt = datatype();
	if ( upper ) {
		for (std::string::iterator p = dt.begin(); p != dt.end(); ++p ) *p = toupper(*p);
	}
	if ( _id ) ss << "#" << *_id;
	ss << "=" << dt << "(";
	for ( std::map<int,Argument*>::const_iterator it = args.begin(); it != args.end(); ++ it ) {
		if ( it != args.begin() ) ss << ",";
		const Argument* a = it->second;
		ss << it->second->toString(upper);
	}
	ss << ")";
	return ss.str();
}
unsigned int IfcWritableEntity::id() { 
	if ( !_id ) {
		_id = new int(file->FreshId()); 
	}
	return *_id; 
}
bool IfcWritableEntity::isWritable() { return true; }
bool IfcWritableEntity::arg_writable(int i) {
	std::map<int,bool>::const_iterator it = writemask.find(i);
	if ( it == writemask.end() ) return false;
	else return it->second;
}
void IfcWritableEntity::arg_writable(int i, bool b) {
	writemask[i] = b;
}

template <typename T> void IfcWritableEntity::_setArgument(int i, const T& t) {
	if ( arg_writable(i) ) delete args[i];
	IfcWriteArgument* arg = new IfcWriteArgument(this);
	args[i] = arg;
	arg->set(t);
	arg_writable(i,true);
}

void IfcWritableEntity::setArgument(int i) {
	_setArgument(i, boost::none);
}
void IfcWritableEntity::setArgumentDerived(int i) {
	_setArgument(i, IfcWriteArgument::Derived());
}
void IfcWritableEntity::setArgument(int i,int v) {
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,bool v) {
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,int v, const char* c){
	_setArgument(i, IfcWriteArgument::EnumerationReference(v, c));
}
void IfcWritableEntity::setArgument(int i,const std::string& v){
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,double v){
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,IfcUtil::IfcBaseClass* v){
	if ( v ) {
		_setArgument(i, v);
	} else {
		_setArgument(i, boost::none);
	}
}
void IfcWritableEntity::setArgument(int i,IfcEntityList::ptr v){
	if ( v.get() ) {
		_setArgument(i, v);
	} else {
		_setArgument(i, boost::none);
	}
}
void IfcWritableEntity::setArgument(int i,IfcEntityListList::ptr v){
	if ( v.get() ) {
		_setArgument(i, v);
	} else {
		_setArgument(i, boost::none);
	}
}
void IfcWritableEntity::setArgument(int i,const std::vector<double>& v){
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,const std::vector<std::string>& v){
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,const std::vector<int>& v){
	_setArgument(i, v);
}

class SizeVisitor : public boost::static_visitor<int> {
public:
	int operator()(const boost::none_t& i) const { return -1; }
	int operator()(const IfcWriteArgument::Derived& i) const { return -1; }
	int operator()(const int& i) const { return -1; }
	int operator()(const bool& i) const { return -1; }
	int operator()(const double& i) const { return -1; }
	int operator()(const std::string& i) const { return i.size(); }
	int operator()(const std::vector<int>& i) const { return i.size(); }
	int operator()(const std::vector<double>& i) const { return i.size(); }
	int operator()(const std::vector<std::string>& i) const { return i.size(); }
	int operator()(const IfcWriteArgument::EnumerationReference& i) const { return -1; }
	int operator()(const IfcUtil::IfcBaseClass* const& i) const { return -1; }
	int operator()(const IfcEntityList::ptr& i) const { return i->Size(); }
	int operator()(const IfcEntityListList::ptr& i) const { return i->Size(); }
};

class StringBuilderVisitor : public boost::static_visitor<void> {
private:
	std::ostringstream& data;
	template <typename T> void serialize(const std::vector<T>& i) {
		data << "(";
		for (typename std::vector<T>::const_iterator it = i.begin(); it != i.end(); ++it) {
			if (it != i.begin()) data << ",";
			data << *it;
		}
		data << ")";
	}
	// The REAL token definition from the IFC SPF standard does not necessarily match
	// the output of the C++ ostream formatting operation.
	// REAL = [ SIGN ] DIGIT { DIGIT } "." { DIGIT } [ "E" [ SIGN ] DIGIT { DIGIT } ] .
	std::string format_double(const double& d) {
		std::ostringstream oss;
		oss << std::setprecision(16) << d;
		const std::string str = oss.str();
		oss.str("");
		std::string::size_type e = str.find('e');
		if (e == std::string::npos) {
			e = str.find('E');
		}
		const std::string mantissa = str.substr(0,e);
		oss << mantissa;
		if (mantissa.find('.') == std::string::npos) {
			oss << ".";
		}
		if (e != std::string::npos) {
			oss << "E";
			oss << str.substr(e+1);
		}
		return oss.str();
	}
	void serialize_double(const std::vector<double>& i) {
		data << "(";
		for (std::vector<double>::const_iterator it = i.begin(); it != i.end(); ++it) {
			if (it != i.begin()) data << ",";
			data << format_double(*it);
		}
		data << ")";
	}
	bool upper;
public:
	StringBuilderVisitor(std::ostringstream& stream, bool upper = false) 
		: data(stream), upper(upper) {}
	void operator()(const boost::none_t& i) { data << "$"; }
	void operator()(const IfcWriteArgument::Derived& i) { data << "*"; }
	void operator()(const int& i) { data << i; }
	void operator()(const bool& i) { data << (i ? ".T." : ".F."); }
	void operator()(const double& i) { data << format_double(i); }
	void operator()(const std::string& i) { 
		std::string s = i;
		if (upper) s = IfcCharacterEncoder(s);
		data << s; 
	}
	void operator()(const std::vector<int>& i) { serialize(i); }
	void operator()(const std::vector<double>& i) { serialize_double(i); }
	void operator()(const std::vector<std::string>& i) { serialize(i); }
	void operator()(const IfcWriteArgument::EnumerationReference& i) {
		data << "." << i.enumeration_value << ".";
	}
	void operator()(const IfcUtil::IfcBaseClass* const& i) { 
		IfcAbstractEntity* e = i->entity;
		if ( IfcSchema::Type::IsSimple(e->type()) ) {
			data << e->toString(upper);
		} else {
			data << "#" << e->id();
		}
	}
	void operator()(const IfcEntityList::ptr& i) { 
		data << "(";
		for (IfcEntityList::it it = i->begin(); it != i->end(); ++it) {
			if (it != i->begin()) data << ",";
			(*this)(*it);
		}
		data << ")";
	}
	void operator()(const IfcEntityListList::ptr& i) { 
		data << "(";
		for (IfcEntityListList::outer_it outer_it = i->begin(); outer_it != i->end(); ++outer_it) {
			data << "(";
			if (outer_it != i->begin()) data << ",";
			for (IfcEntityListList::inner_it inner_it = outer_it->begin(); inner_it != outer_it->end(); ++inner_it) {
				if (inner_it != outer_it->begin()) data << ",";
				(*this)(*inner_it);
			}
			data << ")";
		}
		data << ")";
	}
	operator std::string() { return data.str(); }
};

IfcWriteArgument::operator int() const { return as<int>(); }
IfcWriteArgument::operator bool() const { return as<bool>(); }
IfcWriteArgument::operator double() const { return as<double>(); }
IfcWriteArgument::operator std::string() const { return as<std::string>(); }
IfcWriteArgument::operator std::vector<double>() const { return as<std::vector<double> >(); }
IfcWriteArgument::operator std::vector<int>() const { return as<std::vector<int> >(); }
IfcWriteArgument::operator std::vector<std::string>() const { return as<std::vector<std::string > >(); }
IfcWriteArgument::operator IfcUtil::IfcBaseClass*() const { return as<IfcUtil::IfcBaseClass*>(); }
IfcWriteArgument::operator IfcEntityList::ptr() const { return as<IfcEntityList::ptr>(); }
IfcWriteArgument::operator IfcEntityListList::ptr() const { throw; }
bool IfcWriteArgument::isNull() const { return argumentType() == argument_type_null; }
Argument* IfcWriteArgument::operator [] (unsigned int i) const { throw IfcParse::IfcException("Invalid cast"); }
std::string IfcWriteArgument::toString(bool upper) const {
	std::ostringstream str;
	StringBuilderVisitor v(str, upper);
	container.apply_visitor(v);
	return v;
}
unsigned int IfcWriteArgument::Size() const {
	SizeVisitor v;
	const int size = container.apply_visitor(v);
	if (size == -1) {
		throw IfcParse::IfcException("Invalid cast");
	} else {
		return size;
	}
}
IfcWriteArgument::argument_type IfcWriteArgument::argumentType() const {
	return static_cast<argument_type>(container.which());
}

IfcEntityList::ptr IfcSelectHelperEntity::getInverse(IfcSchema::Type::Enum,int,const std::string &) {throw IfcParse::IfcException("Invalid cast");}
IfcEntityList::ptr IfcSelectHelperEntity::getInverse(IfcSchema::Type::Enum) {throw IfcParse::IfcException("Invalid cast");}
std::string IfcSelectHelperEntity::datatype() const { return IfcSchema::Type::ToString(_type); }
Argument* IfcSelectHelperEntity::getArgument(unsigned int i) {
	if ( i != 0 ) throw IfcParse::IfcException("Invalid cast");
	return arg;
}
unsigned int IfcSelectHelperEntity::getArgumentCount() const { return 1; }
IfcSchema::Type::Enum IfcSelectHelperEntity::type() const { return _type; }
bool IfcSelectHelperEntity::is(IfcSchema::Type::Enum t) const { return _type == t; }
std::string IfcSelectHelperEntity::toString(bool upper) const {
	std::stringstream ss;
	std::string dt = datatype();
	if ( upper ) {
		for (std::string::iterator p = dt.begin(); p != dt.end(); ++p ) *p = toupper(*p);
	}
	ss << dt << "(" << arg->toString(upper) << ")";
	return ss.str();
}
unsigned int IfcSelectHelperEntity::id() { throw IfcParse::IfcException("Invalid cast"); }
bool IfcSelectHelperEntity::isWritable() { throw IfcParse::IfcException("Invalid cast"); }

IfcSelectHelper::IfcSelectHelper(const std::string& v, IfcSchema::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteArgument(0);
	a->set(v);
	this->entity = new IfcSelectHelperEntity(t,a);
}
IfcSelectHelper::IfcSelectHelper(const char* const v, IfcSchema::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteArgument(0);
	a->set<std::string>(v);
	this->entity = new IfcSelectHelperEntity(t,a);
}
IfcSelectHelper::IfcSelectHelper(int v, IfcSchema::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteArgument(0);
	a->set(v);
	this->entity = new IfcSelectHelperEntity(t,a);
}
IfcSelectHelper::IfcSelectHelper(double v, IfcSchema::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteArgument(0);
	a->set(v);
	this->entity = new IfcSelectHelperEntity(t,a);
}
IfcSelectHelper::IfcSelectHelper(bool v, IfcSchema::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteArgument(0);
	a->set(v);
	this->entity = new IfcSelectHelperEntity(t,a);
}
bool IfcSelectHelper::is(IfcSchema::Type::Enum t) const { return entity->is(t); }
IfcSchema::Type::Enum IfcSelectHelper::type() const { return entity->type(); } 

EntityBuffer* EntityBuffer::i = 0;
EntityBuffer* EntityBuffer::instance() {
	if ( ! i ) {
		i = new EntityBuffer();
		i->buffer = IfcEntityList::ptr(new IfcEntityList);
	}
	return i;
}
IfcEntityList::ptr EntityBuffer::Get() {
	return instance()->buffer;
}
void EntityBuffer::Clear() {
	instance()->buffer = IfcEntityList::ptr(new IfcEntityList);
}
void EntityBuffer::Add(IfcUtil::IfcBaseClass* e) {
	instance()->buffer->push(e);
}
