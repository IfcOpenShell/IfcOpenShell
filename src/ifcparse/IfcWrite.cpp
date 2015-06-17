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
#include <locale>

#include "../ifcparse/IfcParse.h" 
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcWritableEntity.h"
#include "../ifcparse/IfcCharacterDecoder.h"
#include "../ifcparse/IfcFile.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4-latebound.h"
#else
#include "../ifcparse/Ifc2x3-latebound.h"
#endif

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
	_id = new int(e->id());

	const unsigned int count = e->getArgumentCount();
	for ( unsigned int i = 0; i < count; ++ i ) {
		this->setArgument(i, e->getArgument(i));
	}
}

IfcEntityList::ptr IfcWritableEntity::getInverse(IfcSchema::Type::Enum type, int attribute_index) {
	if (file) {
		int id = _id ? *_id : setId();
		return file->getInverse(id, type, attribute_index);
	} else {
		throw IfcParse::IfcException("Instance not part of a file");
	}
}

std::string IfcWritableEntity::datatype() const { return IfcSchema::Type::ToString(_type); }
Argument* IfcWritableEntity::getArgument (unsigned int i) {
	if (args[i] == 0) {
		_setArgument(i, boost::none);
	}
	return args[i];
}
unsigned int IfcWritableEntity::getArgumentCount() const {return args.size(); }
IfcSchema::Type::Enum IfcWritableEntity::type() const { return _type; }
bool IfcWritableEntity::is(IfcSchema::Type::Enum v) const { return _type == v; }
std::string IfcWritableEntity::toString(bool upper) const {
	std::stringstream ss;
	ss.imbue(std::locale::classic());
	
	std::string dt = datatype();
	if (upper) {
		for (std::string::iterator p = dt.begin(); p != dt.end(); ++p ) *p = toupper(*p);
	}

	if (_id && !IfcSchema::Type::IsSimple(type())) {
		ss << "#" << *_id;
		ss << "=";
	}

	ss << dt << "(";
	for (std::map<int,Argument*>::const_iterator it = args.begin(); it != args.end(); ++ it) {
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
IfcWritableEntity* IfcWritableEntity::isWritable() { return this; }
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

void IfcWritableEntity::setArgument(int i, Argument* a) {
	IfcWrite::IfcWriteArgument* wa = new IfcWrite::IfcWriteArgument(this);
	IfcUtil::ArgumentType attr_type = a->type();
	switch(attr_type) {
	case IfcUtil::Argument_NULL:
		this->setArgument(i);
		break;
	case IfcUtil::Argument_DERIVED:
		this->setArgumentDerived(i);
		break;
	case IfcUtil::Argument_INT:
		this->setArgument(i, static_cast<int>(*a));
		break;
	case IfcUtil::Argument_BOOL:
		this->setArgument(i, static_cast<bool>(*a));
		break;
	case IfcUtil::Argument_DOUBLE:
		this->setArgument(i, static_cast<double>(*a));
		break;
	case IfcUtil::Argument_STRING:
		this->setArgument(i, static_cast<std::string>(*a));
		break;
	case IfcUtil::Argument_BINARY: {
		boost::dynamic_bitset<> attr_value = *a;
		this->setArgument(i, attr_value); }
		break;
	case IfcUtil::Argument_AGGREGATE_OF_INT: {
		std::vector<int> attr_value = *a;
		this->setArgument(i, attr_value); }
		break;
	case IfcUtil::Argument_AGGREGATE_OF_DOUBLE: {
		std::vector<double> attr_value = *a;
		this->setArgument(i, attr_value); }
		break;
	case IfcUtil::Argument_AGGREGATE_OF_STRING: {
		std::vector<std::string> attr_value = *a;
		this->setArgument(i, attr_value); }
		break;
	case IfcUtil::Argument_AGGREGATE_OF_BINARY: {
		std::vector< boost::dynamic_bitset<> > attr_value = *a;
		this->setArgument(i, attr_value); }
		break;
	case IfcUtil::Argument_ENUMERATION: {
		IfcSchema::Type::Enum ty = IfcSchema::Type::GetAttributeEntity(_type, i);
		std::string enum_literal = a->toString();
		// Remove leading and trailing '.'
		enum_literal = enum_literal.substr(1, enum_literal.size() - 2);
		std::pair<const char*, int> enum_ref = IfcSchema::Type::GetEnumerationIndex(ty, enum_literal);
		this->setArgument(i, enum_ref.second, enum_ref.first); }
		break;
	case IfcUtil::Argument_ENTITY_INSTANCE: {
		this->setArgument(i, static_cast<IfcUtil::IfcBaseClass*>(*a)); }
		break;
	case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
		IfcEntityList::ptr instances = *a;
		IfcEntityList::ptr mapped_instances(new IfcEntityList);
		for (IfcEntityList::it it = instances->begin(); it != instances->end(); ++it) {
			mapped_instances->push(*it);
		}
		this->setArgument(i, mapped_instances); }
		break;
	case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
		std::vector< std::vector<int> > attr_value = *a;
		this->setArgument(i, attr_value); }
		break;
	case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
		std::vector< std::vector<double> > attr_value = *a;
		this->setArgument(i, attr_value); }
		break;
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
		this->setArgument(i, mapped_instances); }
		break;
	default:
	case IfcUtil::Argument_UNKNOWN:
		throw IfcParse::IfcException("Unknown argument encountered");
		break;
	}
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
void IfcWritableEntity::setArgument(int i,const boost::dynamic_bitset<>& v){
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
void IfcWritableEntity::setArgument(int i,const std::vector< std::vector<double> >& v){
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,const std::vector<std::string>& v){
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,const std::vector<int>& v){
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,const std::vector< std::vector<int> >& v){
	_setArgument(i, v);
}
void IfcWritableEntity::setArgument(int i,const std::vector< boost::dynamic_bitset<> >& v){
	_setArgument(i, v);
}

class SizeVisitor : public boost::static_visitor<int> {
public:
	int operator()(const boost::none_t& i) const { return -1; }
	int operator()(const IfcWriteArgument::Derived& i) const { return -1; }
	int operator()(const int& i) const { return -1; }
	int operator()(const bool& i) const { return -1; }
	int operator()(const double& i) const { return -1; }
	int operator()(const std::string& i) const { return -1; }
	int operator()(const boost::dynamic_bitset<>& i) const { return -1; }
	int operator()(const std::vector<int>& i) const { return i.size(); }
	int operator()(const std::vector<double>& i) const { return i.size(); }
	int operator()(const std::vector< std::vector<int> >& i) const { return i.size(); }
	int operator()(const std::vector< std::vector<double> >& i) const { return i.size(); }
	int operator()(const std::vector<std::string>& i) const { return i.size(); }
	int operator()(const std::vector< boost::dynamic_bitset<> >& i) const { return i.size(); }
	int operator()(const IfcWriteArgument::EnumerationReference& i) const { return -1; }
	int operator()(const IfcUtil::IfcBaseClass* const& i) const { return -1; }
	int operator()(const IfcEntityList::ptr& i) const { return i->size(); }
	int operator()(const IfcEntityListList::ptr& i) const { return i->size(); }
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
		oss.imbue(std::locale::classic());
		oss << std::setprecision(15) << d;
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

	std::string format_binary(const boost::dynamic_bitset<>& b) {
		std::ostringstream oss;
		oss.imbue(std::locale::classic());
		oss.put('"');
		oss << std::hex << std::setw(1);
		unsigned c = b.size();
		unsigned n = (4 - (c % 4)) & 3;
		oss << n;
		for (unsigned i = 0; i < c + n;) {
			unsigned accum = 0;
			for (int j = 0; j < 4; ++j, ++i) {
				unsigned bit = i < n ? 0 : b.test(c - i + n - 1) ? 1 : 0;
				accum |= bit << (3-j);
			}
			oss << accum;
		}
		oss.put('"');
		return oss.str();
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
	void operator()(const boost::dynamic_bitset<>& i) { data << format_binary(i); }
	void operator()(const std::string& i) { 
		std::string s = i;
		if (upper) {
			data << static_cast<std::string>(IfcCharacterEncoder(s));
		} else {
			data << '\'' << s << '\'';
		}
	}
	void operator()(const std::vector<int>& i);
	void operator()(const std::vector<double>& i);
	void operator()(const std::vector<std::string>& i);
	void operator()(const std::vector< boost::dynamic_bitset<> >& i);
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
	void operator()(const std::vector< std::vector<int> >& i);
	void operator()(const std::vector< std::vector<double> >& i);
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

template <>
void StringBuilderVisitor::serialize(const std::vector<std::string>& i) {
	data << "(";
	for (std::vector<std::string>::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		if (upper) {
			std::string s = IfcCharacterEncoder(*it);
			data << s;
		} else {
			data << *it;
		}
	}
	data << ")";
}

template <>
void StringBuilderVisitor::serialize(const std::vector<double>& i) {
	data << "(";
	for (std::vector<double>::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		data << format_double(*it);
	}
	data << ")";
}

template <>
void StringBuilderVisitor::serialize(const std::vector< boost::dynamic_bitset<> >& i) {
	data << "(";
	for (std::vector< boost::dynamic_bitset<> >::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		data << format_binary(*it);
	}
	data << ")";
}

void StringBuilderVisitor::operator()(const std::vector<int>& i) { serialize(i); }
void StringBuilderVisitor::operator()(const std::vector<double>& i) { serialize(i); }
void StringBuilderVisitor::operator()(const std::vector<std::string>& i) { serialize(i); }
void StringBuilderVisitor::operator()(const std::vector< boost::dynamic_bitset<> >& i) { serialize(i); }
void StringBuilderVisitor::operator()(const std::vector< std::vector<int> >& i) {
	data << "(";
	for (std::vector< std::vector<int> >::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		serialize(*it);
	}
	data << ")";
}
void StringBuilderVisitor::operator()(const std::vector< std::vector<double> >& i) {
	data << "(";
	for (std::vector< std::vector<double> >::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		serialize(*it);
	}
	data << ")";
}

IfcWriteArgument::operator int() const { return as<int>(); }
IfcWriteArgument::operator bool() const { return as<bool>(); }
IfcWriteArgument::operator double() const { return as<double>(); }
IfcWriteArgument::operator std::string() const { 
	if (type() == IfcUtil::Argument_ENUMERATION) {
		return as<EnumerationReference>().enumeration_value;
	}
	return as<std::string>(); 
}
IfcWriteArgument::operator IfcUtil::IfcBaseClass*() const { return as<IfcUtil::IfcBaseClass*>(); }
IfcWriteArgument::operator boost::dynamic_bitset<>() const { return as< boost::dynamic_bitset<> >(); }
IfcWriteArgument::operator std::vector<double>() const { return as<std::vector<double> >(); }
IfcWriteArgument::operator std::vector<int>() const { return as<std::vector<int> >(); }
IfcWriteArgument::operator std::vector<std::string>() const { return as<std::vector<std::string > >(); }
IfcWriteArgument::operator std::vector< boost::dynamic_bitset<> >() const { return as< std::vector< boost::dynamic_bitset<> > >(); }
IfcWriteArgument::operator IfcEntityList::ptr() const { return as<IfcEntityList::ptr>(); }
IfcWriteArgument::operator std::vector< std::vector<int> >() const { return as<std::vector< std::vector<int> > >(); }
IfcWriteArgument::operator std::vector< std::vector<double> >() const { return as<std::vector< std::vector<double> > >(); }
IfcWriteArgument::operator IfcEntityListList::ptr() const { throw; }
bool IfcWriteArgument::isNull() const { return type() == IfcUtil::Argument_NULL; }
Argument* IfcWriteArgument::operator [] (unsigned int i) const { throw IfcParse::IfcException("Invalid cast"); }
std::string IfcWriteArgument::toString(bool upper) const {
	std::ostringstream str;
	str.imbue(std::locale::classic());
	StringBuilderVisitor v(str, upper);
	container.apply_visitor(v);
	return v;
}
unsigned int IfcWriteArgument::size() const {
	SizeVisitor v;
	const int size = container.apply_visitor(v);
	if (size == -1) {
		throw IfcParse::IfcException("Invalid cast");
	} else {
		return size;
	}
}

IfcUtil::ArgumentType IfcWriteArgument::type() const {
	return static_cast<IfcUtil::ArgumentType>(container.which());
}

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
