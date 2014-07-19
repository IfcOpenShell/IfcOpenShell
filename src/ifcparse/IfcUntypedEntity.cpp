#include <sstream>

#include "../ifcparse/IfcWritableEntity.h"

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/Ifc2x3-rt.h"

#include "IfcUntypedEntity.h"

using namespace IfcUtil;

IfcWrite::IfcWritableEntity* IfcParse::IfcUntypedEntity::writable_entity() {
	IfcWrite::IfcWritableEntity* e;
	if (entity->isWritable()) {
		e = (IfcWrite::IfcWritableEntity*) entity;
	} else {
		entity = e = new IfcWrite::IfcWritableEntity(entity);
	}
	return e;
}
IfcParse::IfcUntypedEntity::IfcUntypedEntity(const std::string& s) {
	std::string S = s;
	for (std::string::iterator i = S.begin(); i != S.end(); ++i ) *i = toupper(*i);
	_type = IfcSchema::Type::FromString(S);
	entity = new IfcWrite::IfcWritableEntity(_type);
	IfcSchema::Type::PopulateDerivedFields(writable_entity());
}
IfcParse::IfcUntypedEntity::IfcUntypedEntity(IfcAbstractEntity* e) {
	entity = e;
	_type = e->type();
}
unsigned int IfcParse::IfcUntypedEntity::id() const {
	if (entity->file) {
		return static_cast<unsigned int>(entity->id());
	} else {
		throw IfcException("Entity not bound to a file");
	}
}
bool IfcParse::IfcUntypedEntity::is(IfcSchema::Type::Enum v) const {
	IfcSchema::Type::Enum _ty = _type;
	if (v == _ty) return true;
	while (_ty != -1) {
		_ty = IfcSchema::Type::Parent(_ty);
		if (v == _ty) return true;
	}
	return false;	
}
std::string IfcParse::IfcUntypedEntity::is_a() const {
	return IfcSchema::Type::ToString(_type);
}
bool IfcParse::IfcUntypedEntity::is_a(const std::string& s) const {
	std::string S = s;
	for (std::string::iterator i = S.begin(); i != S.end(); ++i ) *i = toupper(*i);
	return is(IfcSchema::Type::FromString(S));
}
IfcSchema::Type::Enum IfcParse::IfcUntypedEntity::type() const {
	return _type;
}
unsigned int IfcParse::IfcUntypedEntity::getArgumentCount() const {
	return IfcSchema::Type::GetAttributeCount(_type);
}
IfcUtil::ArgumentType IfcParse::IfcUntypedEntity::getArgumentType(unsigned int i) const {
	return IfcSchema::Type::GetAttributeDerived(_type, i)
		? IfcUtil::Argument_DERIVED
		: IfcSchema::Type::GetAttributeType(_type,i);
}
ArgumentPtr IfcParse::IfcUntypedEntity::getArgument(unsigned int i) const {
	return entity->getArgument(i);
}
const char* IfcParse::IfcUntypedEntity::getArgumentName(unsigned int i) const {
	return IfcSchema::Type::GetAttributeName(_type,i).c_str();
}
void IfcParse::IfcUntypedEntity::invalid_argument(unsigned int i, const std::string& t) {
	const std::string arg_name = IfcSchema::Type::GetAttributeName(_type,i);
	throw IfcException(t + " is not a valid type for '" + arg_name + "'");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i) {
	bool is_optional = IfcSchema::Type::GetAttributeOptional(_type, i);
	if (is_optional) {
		writable_entity()->setArgument(i);
	} else invalid_argument(i,"NULL");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i, int v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_INT) {
		writable_entity()->setArgument(i,v);	
	} else if ( (arg_type == Argument_BOOL) && ( (v == 0) || (v == 1) ) ) {
		writable_entity()->setArgument(i, v == 1);
	} else invalid_argument(i,"INT");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i, bool v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_BOOL) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"BOOL");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i, double v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_DOUBLE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"DOUBLE");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i, const std::string& a) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_STRING) {
		writable_entity()->setArgument(i,a);	
	} else if (arg_type == Argument_ENUMERATION) {
		std::pair<const char*, int> enum_data = IfcSchema::Type::GetEnumerationIndex(IfcSchema::Type::GetAttributeEnumerationClass(_type, i), a);
		writable_entity()->setArgument(i, enum_data.second, enum_data.first);
	} else invalid_argument(i,"STRING");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i, const std::vector<int>& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_VECTOR_INT) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of INT");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i, const std::vector<double>& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_VECTOR_DOUBLE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of DOUBLE");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i, const std::vector<std::string>& v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_VECTOR_STRING) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of STRING");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i, IfcParse::IfcUntypedEntity* v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_ENTITY) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"ENTITY");
}
void IfcParse::IfcUntypedEntity::setArgument(unsigned int i, IfcEntities v) {
	IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_ENTITY_LIST) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of ENTITY");
}
std::pair<IfcUtil::ArgumentType,ArgumentPtr> IfcParse::IfcUntypedEntity::get_argument(unsigned i) {
	return std::pair<IfcUtil::ArgumentType,ArgumentPtr>(getArgumentType(i),getArgument(i));
}
std::pair<IfcUtil::ArgumentType,ArgumentPtr> IfcParse::IfcUntypedEntity::get_argument(const std::string& a) {
	return get_argument(IfcSchema::Type::GetAttributeIndex(_type,a));
}
unsigned IfcParse::IfcUntypedEntity::getArgumentIndex(const std::string& a) const {
	return IfcSchema::Type::GetAttributeIndex(_type,a);
}
std::string IfcParse::IfcUntypedEntity::toString() {
	return entity->toString(false);
}
IfcEntities IfcParse::IfcUntypedEntity::get_inverse(const std::string& a) {
	std::pair<IfcSchema::Type::Enum, unsigned> inv = IfcSchema::Type::GetInverseAttribute(_type, a);
	IfcEntities invs = entity->getInverse(inv.first);
	IfcEntities filtered(new IfcEntityList());
	for (IfcEntityList::it it = invs->begin(); it != invs->end(); ++it) {
		try {
			const int id = *(*it)->entity->getArgument(inv.second);
			if (id == this->entity->id()) { filtered->push(*it); }
		} catch (...) {}
	}
	return filtered;
}		
bool IfcParse::IfcUntypedEntity::is_valid() {
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
