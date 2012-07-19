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
#include "IfcWrite.h"
#include "IfcWritableEntity.h"

using namespace IfcWrite;

IfcWritableEntity::IfcWritableEntity(Ifc2x3::Type::Enum t) {
	_type = t;
	_id = 0;
}
int IfcWritableEntity::setId(int i) {
	return *(_id = new int(i > 0 ? i : Ifc::FreshId()));
}
IfcWritableEntity::IfcWritableEntity(IfcAbstractEntity* e) 
{
	_type = e->type();
	_id = new int(e->id());

	const unsigned int count = e->getArgumentCount();
	for ( unsigned int i = 0; i < count; ++ i ) {
		args[i] = e->getArgument(i);
		writemask[i] = false;
	}
}
// TODO: Reove redundancy with IfcParse::Entity
IfcEntities IfcWritableEntity::getInverse(Ifc2x3::Type::Enum c) {
	IfcEntities l = IfcEntities(new IfcEntityList());
	int id = _id ? *_id : setId();
	IfcEntities all = Ifc::EntitiesByReference(id);
	if ( ! all ) return l;
	for( IfcEntityList::it it = all->begin(); it != all->end();++  it  ) {
		if ( c == Ifc2x3::Type::ALL || (*it)->is(c) ) {
			l->push(*it);
		}
	}
	return l;
}
IfcEntities IfcWritableEntity::getInverse(Ifc2x3::Type::Enum c, int i, const std::string& a) {
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

std::string IfcWritableEntity::datatype() { return Ifc2x3::Type::ToString(_type); }
ArgumentPtr IfcWritableEntity::getArgument (unsigned int i) { if ( i >= getArgumentCount() ) throw; return args[i]; }
unsigned int IfcWritableEntity::getArgumentCount() {return args.size(); }
Ifc2x3::Type::Enum IfcWritableEntity::type() const { return _type; }
bool IfcWritableEntity::is(Ifc2x3::Type::Enum v) const { return _type == v; }
std::string IfcWritableEntity::toString(bool upper) {
	std::stringstream ss;
	std::string dt = datatype();
	if ( upper ) {
		for (std::string::iterator p = dt.begin(); p != dt.end(); ++p ) *p = toupper(*p);
	}
	if ( _id ) ss << "#" << *_id;
	ss << "=" << dt << "(";
	for ( std::map<int,ArgumentPtr>::const_iterator it = args.begin(); it != args.end(); ++ it ) {
		if ( it != args.begin() ) ss << ",";
		const ArgumentPtr a = it->second;
		ss << it->second->toString(upper);
	}
	ss << ")";
	return ss.str();
}
unsigned int IfcWritableEntity::id() { if ( !_id ) _id = new int(Ifc::FreshId()); return *_id; }
bool IfcWritableEntity::isWritable() { return true; }
bool IfcWritableEntity::arg_writable(int i) {
	std::map<int,bool>::const_iterator it = writemask.find(i);
	if ( it == writemask.end() ) return false;
	else return it->second;
}
void IfcWritableEntity::arg_writable(int i, bool b) {
	writemask[i] = b;
}
void IfcWritableEntity::setArgument(int i,int v) {
	if ( arg_writable(i) ) delete args[i];
	args[i] = new IfcWriteIntegralArgument(v);
	arg_writable(i,true);
}
void IfcWritableEntity::setArgument(int i,int v, const char* c){
	if ( arg_writable(i) ) delete args[i];
	args[i] = new IfcWriteEnumerationArgument(v,c);
	arg_writable(i,true);
}
void IfcWritableEntity::setArgument(int i,const std::string& v){
	if ( arg_writable(i) ) delete args[i];
	args[i] = new IfcWriteIntegralArgument(v);
	arg_writable(i,true);
}
void IfcWritableEntity::setArgument(int i,const Nullable<std::string>& v){
	if ( arg_writable(i) ) delete args[i];
	if ( v.IsNull() ) new IfcWriteNullArgument();
	else args[i] = new IfcWriteIntegralArgument(v);
	arg_writable(i,true);
}
void IfcWritableEntity::setArgument(int i,double v){
	if ( arg_writable(i) ) delete args[i];
	args[i] = new IfcWriteIntegralArgument(v);
	arg_writable(i,true);
}
void IfcWritableEntity::setArgument(int i,IfcUtil::IfcSchemaEntity v){
	if ( arg_writable(i) ) delete args[i];
	if ( v ) args[i] = new IfcWriteIntegralArgument(v);
	else args[i] = new IfcWriteNullArgument();
	arg_writable(i,true);
}
void IfcWritableEntity::setArgument(int i,IfcEntities v){
	if ( arg_writable(i) ) delete args[i];
	if ( v.get() ) args[i] = new IfcWriteEntityListArgument(v);
	else args[i] = new IfcWriteNullArgument();
	arg_writable(i,true);
}
void IfcWritableEntity::setArgument(int i,const std::vector<double>& v){
	if ( arg_writable(i) ) delete args[i];
	args[i] = new IfcWriteIntegralArgument(v);
	arg_writable(i,true);
}
void IfcWritableEntity::setArgument(int i,const std::vector<std::string>& v){
	if ( arg_writable(i) ) delete args[i];
	args[i] = new IfcWriteIntegralArgument(v);
	arg_writable(i,true);
}
void IfcWritableEntity::setArgument(int i,const std::vector<int>& v){
	if ( arg_writable(i) ) delete args[i];
	args[i] = new IfcWriteIntegralArgument(v);
	arg_writable(i,true);
}

IfcWriteNullArgument::operator int() const { throw; }
IfcWriteNullArgument::operator bool() const { throw; }
IfcWriteNullArgument::operator double() const { throw; }
IfcWriteNullArgument::operator std::string() const { throw; }
IfcWriteNullArgument::operator std::vector<double>() const { throw; }
IfcWriteNullArgument::operator std::vector<int>() const { throw; }
IfcWriteNullArgument::operator std::vector<std::string>() const { throw; }
IfcWriteNullArgument::operator IfcUtil::IfcSchemaEntity() const { throw; }
IfcWriteNullArgument::operator IfcEntities() const { throw; }
bool IfcWriteNullArgument::isNull() const { return true; }
ArgumentPtr IfcWriteNullArgument::operator [] (unsigned int i) const { throw; }
std::string IfcWriteNullArgument::toString(bool upper) const { return "$"; }
unsigned int IfcWriteNullArgument::Size() const { throw; }

IfcWriteEntityListArgument::IfcWriteEntityListArgument(const IfcEntities& v) { value = v; }
IfcWriteEntityListArgument::operator int() const { throw; }
IfcWriteEntityListArgument::operator bool() const { throw; }
IfcWriteEntityListArgument::operator double() const { throw; }
IfcWriteEntityListArgument::operator std::string() const { throw; }
IfcWriteEntityListArgument::operator std::vector<double>() const { throw; }
IfcWriteEntityListArgument::operator std::vector<int>() const { throw; }
IfcWriteEntityListArgument::operator std::vector<std::string>() const { throw; }
IfcWriteEntityListArgument::operator IfcUtil::IfcSchemaEntity() const { throw; }
IfcWriteEntityListArgument::operator IfcEntities() const { return value; }
bool IfcWriteEntityListArgument::isNull() const { return false; }
unsigned int IfcWriteEntityListArgument::Size() const { return value->Size(); }
ArgumentPtr IfcWriteEntityListArgument::operator [] (unsigned int i) const { throw; }
std::string IfcWriteEntityListArgument::toString(bool upper)  const {
	std::ostringstream ss;
	ss << "(";
	for ( IfcEntityList::it it = value->begin(); it != value->end(); ++ it ) {
		if ( it != value->begin() ) ss << ",";
		IfcAbstractEntity* e = (*it)->entity;
		if ( Ifc2x3::Type::IsSimple(e->type()) ) {
			ss << e->toString(upper);
		} else {
			ss << "#" << e->id();
		}
	}
	ss << ")";
	return ss.str();
}

IfcWriteEnumerationArgument::IfcWriteEnumerationArgument(int v, const char* c) {data=v; enumeration_value = c;}
IfcWriteEnumerationArgument::operator int() const { throw; }
IfcWriteEnumerationArgument::operator bool() const { throw; }
IfcWriteEnumerationArgument::operator double() const { throw; }
IfcWriteEnumerationArgument::operator std::string() const { return std::string(enumeration_value); }
IfcWriteEnumerationArgument::operator std::vector<double>() const { throw; }
IfcWriteEnumerationArgument::operator std::vector<int>() const { throw; }
IfcWriteEnumerationArgument::operator std::vector<std::string>() const { throw; }
IfcWriteEnumerationArgument::operator IfcUtil::IfcSchemaEntity() const { throw; }
IfcWriteEnumerationArgument::operator IfcEntities() const { throw; }
bool IfcWriteEnumerationArgument::isNull() const { return false; }
ArgumentPtr IfcWriteEnumerationArgument::operator [] (unsigned int i) const { throw; }
std::string IfcWriteEnumerationArgument::toString(bool upper) const { return std::string(".") + enumeration_value + '.';}
unsigned int IfcWriteEnumerationArgument::Size() const { throw; }

IfcWriteIntegralArgument::IfcWriteIntegralArgument(int v) {data=new int(v); type = Argument_INT;}
IfcWriteIntegralArgument::IfcWriteIntegralArgument(bool v) {data=new bool(v); type = Argument_BOOL;}
IfcWriteIntegralArgument::IfcWriteIntegralArgument(double v) {data=new double(v); type = Argument_DOUBLE;}
IfcWriteIntegralArgument::IfcWriteIntegralArgument(const std::string& v) {data=new std::string(v); type = Argument_STRING;}
IfcWriteIntegralArgument::IfcWriteIntegralArgument(const std::vector<int> v) {data=new std::vector<int>(v); type = Argument_VECTOR_INT;}
IfcWriteIntegralArgument::IfcWriteIntegralArgument(const std::vector<double> v) {data=new std::vector<double>(v); type = Argument_VECTOR_DOUBLE;}
IfcWriteIntegralArgument::IfcWriteIntegralArgument(const std::vector<std::string> v) {data=new std::vector<std::string>(v); type = Argument_VECTOR_STRING;}
IfcWriteIntegralArgument::IfcWriteIntegralArgument(IfcUtil::IfcSchemaEntity v) {data=v; type = Argument_ENTITY;}
IfcWriteIntegralArgument::~IfcWriteIntegralArgument() {
	switch ( type ) {
	case Argument_INT:
		delete (int*) data;
		break;
	case Argument_BOOL:
		delete (bool*) data;
		break;
	case Argument_DOUBLE:
		delete (double*) data;
		break;
	case Argument_STRING:
		delete (std::string*) data;
		break;
	case Argument_VECTOR_INT:
		delete (std::vector<int>*) data;
		break;
	case Argument_VECTOR_DOUBLE:
		delete (std::vector<double>*) data;
		break;
	case Argument_VECTOR_STRING:
		delete (std::vector<std::string>*) data;
		break;
	case Argument_ENTITY:
		break;
	}
}
IfcWriteIntegralArgument::operator int() const { if ( type != Argument_INT ) throw; return *(int*)data; }
IfcWriteIntegralArgument::operator bool() const { if ( type != Argument_BOOL ) throw; return *(bool*)data; }
IfcWriteIntegralArgument::operator double() const { if ( type != Argument_DOUBLE ) throw; return *(double*)data; }
IfcWriteIntegralArgument::operator std::string() const { if ( type != Argument_STRING ) throw; return *(std::string*)data; }
IfcWriteIntegralArgument::operator std::vector<double>() const { if ( type != Argument_VECTOR_DOUBLE ) throw; return *(std::vector<double>*)data; }
IfcWriteIntegralArgument::operator std::vector<int>() const { if ( type != Argument_VECTOR_INT ) throw; return *(std::vector<int>*)data; }
IfcWriteIntegralArgument::operator std::vector<std::string>() const { if ( type != Argument_VECTOR_STRING ) throw; return *(std::vector<std::string>*)data; }
IfcWriteIntegralArgument::operator IfcUtil::IfcSchemaEntity() const { if ( type != Argument_ENTITY ) throw; return (IfcUtil::IfcSchemaEntity)data; }
IfcWriteIntegralArgument::operator IfcEntities() const { throw; }
bool IfcWriteIntegralArgument::isNull() const { return false; }
unsigned int IfcWriteIntegralArgument::Size() const { 
	switch ( type ) {
	case Argument_VECTOR_INT:
		return ((std::vector<int>*) data)->size();
		break;
	case Argument_VECTOR_DOUBLE:
		return ((std::vector<double>*) data)->size();
		break;
	case Argument_VECTOR_STRING:
		return ((std::vector<std::string>*) data)->size();
		break;
	default:
		throw;
		break;
	}
}
ArgumentPtr IfcWriteIntegralArgument::operator [] (unsigned int i) const { throw; }
std::string IfcWriteIntegralArgument::toString(bool upper) const {
	std::ostringstream ss;
	switch ( type ) {
	case Argument_INT:
		ss << *(int*)data;
		break;
	case Argument_BOOL:
		ss << ((*(bool*) data) ? ".T." : ".F.");
		break;
	case Argument_DOUBLE:
		ss << *(double*) data;
		break;
	case Argument_STRING:
		ss << '\'' << *(std::string*) data << '\'';
		break;
	case Argument_VECTOR_INT:
		ss << "(";
		{const std::vector<int>& v = *(std::vector<int>*) data;
		for ( std::vector<int>::const_iterator it = v.begin(); it != v.end(); ++ it ) {
			if ( it != v.begin() ) ss << ",";
			ss << *it;
		}}
		ss << ")";
		break;
	case Argument_VECTOR_DOUBLE:
		ss << "(";
		{const std::vector<double>& v = *(std::vector<double>*) data;
		for ( std::vector<double>::const_iterator it = v.begin(); it != v.end(); ++ it ) {
			if ( it != v.begin() ) ss << ",";
			ss << *it;
		}}
		ss << ")";
		break;
	case Argument_VECTOR_STRING:
		ss << "(";
		{const std::vector<std::string>& v = *(std::vector<std::string>*) data;
		for ( std::vector<std::string>::const_iterator it = v.begin(); it != v.end(); ++ it ) {
			if ( it != v.begin() ) ss << ",";
			ss << '\'' << *it << '\'';
		}}
		ss << ")";
		break;
	case Argument_ENTITY:
		{IfcAbstractEntity* e = ((IfcUtil::IfcSchemaEntity)data)->entity;
		if ( Ifc2x3::Type::IsSimple(e->type()) ) {
			ss << e->toString(upper);
		} else {
			ss << "#" << e->id();
		}}
		break;
	default: throw;
	}
	return ss.str();
}

IfcEntities IfcSelectHelperEntity::getInverse(Ifc2x3::Type::Enum,int,const std::string &) {throw;}
IfcEntities IfcSelectHelperEntity::getInverse(Ifc2x3::Type::Enum) {throw;}
std::string IfcSelectHelperEntity::datatype() { return Ifc2x3::Type::ToString(_type); }
ArgumentPtr IfcSelectHelperEntity::getArgument(unsigned int i) {
	if ( i != 0 ) throw;
	return arg;
}
unsigned int IfcSelectHelperEntity::getArgumentCount() { return 1; }
Ifc2x3::Type::Enum IfcSelectHelperEntity::type() const { return _type; }
bool IfcSelectHelperEntity::is(Ifc2x3::Type::Enum t) const { return _type == t; }
std::string IfcSelectHelperEntity::toString(bool upper) {
	std::stringstream ss;
	std::string dt = datatype();
	if ( upper ) {
		for (std::string::iterator p = dt.begin(); p != dt.end(); ++p ) *p = toupper(*p);
	}
	ss << dt << "(" << arg->toString(upper) << ")";
	return ss.str();
}
unsigned int IfcSelectHelperEntity::id() { throw; }
bool IfcSelectHelperEntity::isWritable() { throw; }

IfcSelectHelper::IfcSelectHelper(const std::string& v, Ifc2x3::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteIntegralArgument(v);
	this->entity = new IfcSelectHelperEntity(t,a);
}
IfcSelectHelper::IfcSelectHelper(const char* const v, Ifc2x3::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteIntegralArgument(std::string(v));
	this->entity = new IfcSelectHelperEntity(t,a);
}
IfcSelectHelper::IfcSelectHelper(int v, Ifc2x3::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteIntegralArgument(v);
	this->entity = new IfcSelectHelperEntity(t,a);
}
IfcSelectHelper::IfcSelectHelper(float v, Ifc2x3::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteIntegralArgument(v);
	this->entity = new IfcSelectHelperEntity(t,a);
}
IfcSelectHelper::IfcSelectHelper(bool v, Ifc2x3::Type::Enum t) {
	IfcWriteArgument* a = new IfcWriteIntegralArgument(v);
	this->entity = new IfcSelectHelperEntity(t,a);
}
bool IfcSelectHelper::is(Ifc2x3::Type::Enum t) const { return entity->is(t); }
Ifc2x3::Type::Enum IfcSelectHelper::type() const { return entity->type(); } 