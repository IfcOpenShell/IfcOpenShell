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
	for (unsigned i = 0; i < getArgumentCount(); ++i) {
		// Side effect of this is that a NULL attribute is created.
		entity->getArgument(i);
	}
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
IfcSchema::Type::Enum IfcParse::IfcLateBoundEntity::getArgumentEntity(unsigned int i) const {
	return IfcSchema::Type::GetAttributeEntity(_type, i);
}
Argument* IfcParse::IfcLateBoundEntity::getArgument(unsigned int i) const {
	return entity->getArgument(i);
}
const char* IfcParse::IfcLateBoundEntity::getArgumentName(unsigned int i) const {
	return IfcSchema::Type::GetAttributeName(_type,i).c_str();
}
bool IfcParse::IfcLateBoundEntity::getArgumentOptionality(unsigned int i) const {
	return IfcSchema::Type::GetAttributeOptional(_type, i);
}

void IfcParse::IfcLateBoundEntity::invalid_argument(unsigned int i, const std::string& t) {
	const std::string arg_name = IfcSchema::Type::GetAttributeName(_type,i);
	throw IfcException(t + " is not a valid type for '" + arg_name + "'");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsNull(unsigned int i) {
	bool is_optional = IfcSchema::Type::GetAttributeOptional(_type, i);
	if (is_optional) {
		writable_entity()->setArgument(i);
	} else invalid_argument(i,"NULL");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsInt(unsigned int i, int v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_INT) {
		writable_entity()->setArgument(i,v);	
	} else if ( (arg_type == Argument_BOOL) && ( (v == 0) || (v == 1) ) ) {
		writable_entity()->setArgument(i, v == 1);
	} else invalid_argument(i,"INTEGER");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsBool(unsigned int i, bool v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_BOOL) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"BOOLEAN");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsDouble(unsigned int i, double v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_DOUBLE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"REAL");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsString(unsigned int i, const std::string& a) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_STRING) {
		writable_entity()->setArgument(i,a);
	} else if (arg_type == Argument_ENUMERATION) {
		std::pair<const char*, int> enum_data = IfcSchema::Type::GetEnumerationIndex(IfcSchema::Type::GetAttributeEntity(_type, i), a);
		writable_entity()->setArgument(i, enum_data.second, enum_data.first);
	} else if (arg_type == Argument_BINARY) {
		if (valid_binary_string(a)) {
			boost::dynamic_bitset<> bits(a);
			writable_entity()->setArgument(i, bits);
		} else {
			throw IfcException("String not a valid binary representation");
		}
	} else invalid_argument(i,"STRING");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsAggregateOfInt(unsigned int i, const std::vector<int>& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_AGGREGATE_OF_INT) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"AGGREGATE OF INT");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsAggregateOfDouble(unsigned int i, const std::vector<double>& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_AGGREGATE_OF_DOUBLE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"AGGREGATE OF DOUBLE");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsAggregateOfString(unsigned int i, const std::vector<std::string>& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_AGGREGATE_OF_STRING) {
		writable_entity()->setArgument(i,v);	
	} else if (arg_type == Argument_AGGREGATE_OF_BINARY) {
		std::vector< boost::dynamic_bitset<> > bits;
		bits.reserve(v.size());
		for (std::vector<std::string>::const_iterator it = v.begin(); it != v.end(); ++it) {
			if (valid_binary_string(*it)) {
				bits.push_back(boost::dynamic_bitset<>(*it));
			} else {
				throw IfcException("String not a valid binary representation");
			}			
		}
		writable_entity()->setArgument(i, bits);
	} else invalid_argument(i,"AGGREGATE OF STRING");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsEntityInstance(unsigned int i, IfcParse::IfcLateBoundEntity* v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_ENTITY_INSTANCE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"ENTITY INSTANCE");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsAggregateOfEntityInstance(unsigned int i, IfcEntityList::ptr v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"AGGREGATE OF ENTITY INSTANCE");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsAggregateOfAggregateOfInt(unsigned int i, const std::vector< std::vector<int> >& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_AGGREGATE_OF_AGGREGATE_OF_INT) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"AGGREGATE OF AGGREGATE OF INT");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsAggregateOfAggregateOfDouble(unsigned int i, const std::vector< std::vector<double> >& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"AGGREGATE OF AGGREGATE OF DOUBLE");
}
void IfcParse::IfcLateBoundEntity::setArgumentAsAggregateOfAggregateOfEntityInstance(unsigned int i, IfcEntityListList::ptr v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"AGGREGATE OF AGGREGATE OF ENTITY INSTANCE");
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

std::vector<std::string> IfcParse::IfcLateBoundEntity::getAttributeNames() const {
	std::vector<std::string> return_value;
	return_value.reserve(getArgumentCount());
	for (unsigned i = 0; i < getArgumentCount(); ++i) {
		return_value.push_back(getArgumentName(i));
	}
	return return_value;
}

std::vector<std::string> IfcParse::IfcLateBoundEntity::getInverseAttributeNames() const {
	std::vector<std::string> return_value;
	std::set<std::string> values = IfcSchema::Type::GetInverseAttributeNames(_type);
	std::copy(values.begin(), values.end(), std::back_inserter(return_value));
	return return_value;
}
