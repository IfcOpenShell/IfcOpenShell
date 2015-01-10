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

#include <sstream>

#include "../ifcparse/IfcWritableEntity.h"

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcWrite.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4-latebound.h"
#else
#include "../ifcparse/Ifc2x3-latebound.h"
#endif

#include "IfcLateBoundEntity.h"

using namespace IfcUtil;

IfcWrite::IfcWritableEntity* IfcParse::IfcLateBoundEntity::writable_entity() {
	IfcWrite::IfcWritableEntity* e;
	if (entity->isWritable()) {
		e = (IfcWrite::IfcWritableEntity*) entity;
	} else {
		entity = e = new IfcWrite::IfcWritableEntity(entity);
	}
	return e;
}
IfcParse::IfcLateBoundEntity::IfcLateBoundEntity(const std::string& s) {
	std::string S = s;
	for (std::string::iterator i = S.begin(); i != S.end(); ++i ) *i = toupper(*i);
	_type = IfcSchema::Type::FromString(S);
	entity = new IfcWrite::IfcWritableEntity(_type);
	IfcSchema::Type::PopulateDerivedFields(writable_entity());
}
IfcParse::IfcLateBoundEntity::IfcLateBoundEntity(IfcAbstractEntity* e) {
	entity = e;
	_type = e->type();
}
unsigned int IfcParse::IfcLateBoundEntity::id() const {
	if (entity->file) {
		return static_cast<unsigned int>(entity->id());
	} else {
		throw IfcException("Entity not bound to a file");
	}
}
bool IfcParse::IfcLateBoundEntity::is(IfcSchema::Type::Enum v) const {
	IfcSchema::Type::Enum _ty = _type;
	if (v == _ty) return true;
	while (_ty != -1) {
		_ty = IfcSchema::Type::Parent(_ty);
		if (v == _ty) return true;
	}
	return false;	
}
std::string IfcParse::IfcLateBoundEntity::is_a() const {
	return IfcSchema::Type::ToString(_type);
}
bool IfcParse::IfcLateBoundEntity::is_a(const std::string& s) const {
	std::string S = s;
	for (std::string::iterator i = S.begin(); i != S.end(); ++i ) *i = toupper(*i);
	return is(IfcSchema::Type::FromString(S));
}
IfcSchema::Type::Enum IfcParse::IfcLateBoundEntity::type() const {
	return _type;
}
unsigned int IfcParse::IfcLateBoundEntity::getArgumentCount() const {
	return IfcSchema::Type::GetAttributeCount(_type);
}
IfcUtil::ArgumentType IfcParse::IfcLateBoundEntity::getArgumentType(unsigned int i) const {
	return IfcSchema::Type::GetAttributeDerived(_type, i)
		? IfcUtil::Argument_DERIVED
		: IfcSchema::Type::GetAttributeType(_type,i);
}
Argument* IfcParse::IfcLateBoundEntity::getArgument(unsigned int i) const {
	return entity->getArgument(i);
}
const char* IfcParse::IfcLateBoundEntity::getArgumentName(unsigned int i) const {
	return IfcSchema::Type::GetAttributeName(_type,i).c_str();
}
void IfcParse::IfcLateBoundEntity::invalid_argument(unsigned int i, const std::string& t) {
	const std::string arg_name = IfcSchema::Type::GetAttributeName(_type,i);
	throw IfcException(t + " is not a valid type for '" + arg_name + "'");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i) {
	bool is_optional = IfcSchema::Type::GetAttributeOptional(_type, i);
	if (is_optional) {
		writable_entity()->setArgument(i);
	} else invalid_argument(i,"NULL");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i, int v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_INT) {
		writable_entity()->setArgument(i,v);	
	} else if ( (arg_type == Argument_BOOL) && ( (v == 0) || (v == 1) ) ) {
		writable_entity()->setArgument(i, v == 1);
	} else invalid_argument(i,"INT");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i, bool v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_BOOL) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"BOOL");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i, double v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_DOUBLE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"DOUBLE");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i, const std::string& a) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_STRING) {
		writable_entity()->setArgument(i,a);	
	} else if (arg_type == Argument_ENUMERATION) {
		std::pair<const char*, int> enum_data = IfcSchema::Type::GetEnumerationIndex(IfcSchema::Type::GetAttributeEnumerationClass(_type, i), a);
		writable_entity()->setArgument(i, enum_data.second, enum_data.first);
	} else invalid_argument(i,"STRING");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i, const std::vector<int>& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_VECTOR_INT) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of INT");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i, const std::vector<double>& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_VECTOR_DOUBLE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of DOUBLE");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i, const std::vector<std::string>& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_VECTOR_STRING) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of STRING");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i, IfcParse::IfcLateBoundEntity* v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_ENTITY) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"ENTITY");
}
void IfcParse::IfcLateBoundEntity::setArgument(unsigned int i, IfcEntityList::ptr v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_ENTITY_LIST) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of ENTITY");
}
std::pair<IfcUtil::ArgumentType,Argument*> IfcParse::IfcLateBoundEntity::get_argument(unsigned i) {
	return std::pair<IfcUtil::ArgumentType,Argument*>(getArgumentType(i),getArgument(i));
}
std::pair<IfcUtil::ArgumentType,Argument*> IfcParse::IfcLateBoundEntity::get_argument(const std::string& a) {
	return get_argument(IfcSchema::Type::GetAttributeIndex(_type,a));
}
unsigned IfcParse::IfcLateBoundEntity::getArgumentIndex(const std::string& a) const {
	return IfcSchema::Type::GetAttributeIndex(_type,a);
}
std::string IfcParse::IfcLateBoundEntity::toString() {
	return entity->toString(false);
}
IfcEntityList::ptr IfcParse::IfcLateBoundEntity::get_inverse(const std::string& a) {
	std::pair<IfcSchema::Type::Enum, unsigned> inv = IfcSchema::Type::GetInverseAttribute(_type, a);
	return entity->getInverse(inv.first, inv.second);
}		
bool IfcParse::IfcLateBoundEntity::is_valid() {
	const unsigned arg_count = getArgumentCount();
	bool valid = true;
	std::ostringstream oss;
	oss << "Argument ";
	for (unsigned i = 0; i < arg_count; ++i) {
		bool is_null = true;
		try {
			const Argument& arg = *getArgument(i);
			is_null = arg.isNull();
		} catch(IfcException) {}
		if (!IfcSchema::Type::GetAttributeOptional(_type,i) && is_null) {
			if (!valid) {
				oss << ", ";
			}
			oss << "\"" << getArgumentName(i) << "\"";
			valid = false;
		}
	}
	oss << " not optional";
	if (!valid) {
		throw IfcException(oss.str());
	}
	return valid;
}
