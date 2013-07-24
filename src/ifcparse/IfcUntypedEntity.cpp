#include <sstream>

#include "IfcWritableEntity.h"

#include "IfcUtil.h"
#include "IfcWrite.h"
#include "Ifc2x3-rt.h"

IfcWrite::IfcWritableEntity* Ifc::IfcUntypedEntity::writable_entity() {
	IfcWrite::IfcWritableEntity* e;
	if (entity->isWritable()) {
		e = (IfcWrite::IfcWritableEntity*) entity;
	} else {
		entity = e = new IfcWrite::IfcWritableEntity(entity);
	}
	return e;
}
Ifc::IfcUntypedEntity::IfcUntypedEntity(const std::string& s) {
	std::string S = s;
	for (std::string::iterator i = S.begin(); i != S.end(); ++i ) *i = toupper(*i);
	_type = Ifc2x3::Type::FromString(S);
	entity = new IfcWrite::IfcWritableEntity(_type);
}
Ifc::IfcUntypedEntity::IfcUntypedEntity(IfcAbstractEntity* e) {
	entity = e;
	_type = e->type();
}
bool Ifc::IfcUntypedEntity::is(Ifc2x3::Type::Enum v) const {
	Ifc2x3::Type::Enum _ty = _type;
	if (v == _ty) return true;
	while (_ty != -1) {
		_ty = Ifc2x3::Type::Parent(_ty);
		if (v == _ty) return true;
	}
	return false;	
}
std::string Ifc::IfcUntypedEntity::is_a() const {
	return Ifc2x3::Type::ToString(_type);
}
bool Ifc::IfcUntypedEntity::is_a(const std::string& s) const {
	std::string S = s;
	for (std::string::iterator i = S.begin(); i != S.end(); ++i ) *i = toupper(*i);
	return is(Ifc2x3::Type::FromString(S));
}
Ifc2x3::Type::Enum Ifc::IfcUntypedEntity::type() const {
	return _type;
}
unsigned int Ifc::IfcUntypedEntity::getArgumentCount() const {
	return Ifc2x3::Type::GetAttributeCount(_type);
}
IfcUtil::ArgumentType Ifc::IfcUntypedEntity::getArgumentType(unsigned int i) const {
	return Ifc2x3::Type::GetAttributeType(_type,i);
}
ArgumentPtr Ifc::IfcUntypedEntity::getArgument(unsigned int i) const {
	return entity->getArgument(i);
}
const char* Ifc::IfcUntypedEntity::getArgumentName(unsigned int i) const {
	return Ifc2x3::Type::GetAttributeName(_type,i).c_str();
}
void Ifc::IfcUntypedEntity::invalid_argument(unsigned int i, const std::string& t) {
	const std::string arg_name = Ifc2x3::Type::GetAttributeName(_type,i);
	throw IfcException(t + " is not a valid type for '" + arg_name + "'");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i) {
	bool is_optional = Ifc2x3::Type::GetAttributeOptional(_type, i);
	if (is_optional) {
		writable_entity()->setArgument(i);
	} else invalid_argument(i,"NONE");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i, int v) {
	IfcUtil::ArgumentType arg_type = Ifc2x3::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_INT) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"INT");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i, bool v) {
	IfcUtil::ArgumentType arg_type = Ifc2x3::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_BOOL) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"BOOL");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i, double v) {
	IfcUtil::ArgumentType arg_type = Ifc2x3::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_DOUBLE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"DOUBLE");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i, const std::string& a) {
	IfcUtil::ArgumentType arg_type = Ifc2x3::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_STRING) {
		writable_entity()->setArgument(i,a);	
	} else if (arg_type == Argument_ENUMERATION) {
		std::pair<const char*, int> enum_data = Ifc2x3::Type::GetEnumerationIndex(Ifc2x3::Type::GetAttributeEnumerationClass(_type, i), a);
		writable_entity()->setArgument(i, enum_data.second, enum_data.first);
	} else invalid_argument(i,"STRING");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i, const std::vector<int>& v) {
	IfcUtil::ArgumentType arg_type = Ifc2x3::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_VECTOR_INT) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of INT");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i, const std::vector<double>& v) {
	IfcUtil::ArgumentType arg_type = Ifc2x3::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_VECTOR_DOUBLE) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of DOUBLE");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i, const std::vector<std::string>& v) {
	IfcUtil::ArgumentType arg_type = Ifc2x3::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_VECTOR_STRING) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of STRING");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i, Ifc::IfcUntypedEntity* v) {
	IfcUtil::ArgumentType arg_type = Ifc2x3::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_ENTITY) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"ENTITY");
}
void Ifc::IfcUntypedEntity::setArgument(unsigned int i, IfcEntities v) {
	IfcUtil::ArgumentType arg_type = Ifc2x3::Type::GetAttributeType(_type,i);
	if (arg_type == Argument_ENTITY_LIST) {
		writable_entity()->setArgument(i,v);	
	} else invalid_argument(i,"LIST of ENTITY");
}
std::pair<IfcUtil::ArgumentType,ArgumentPtr> Ifc::IfcUntypedEntity::get_argument(unsigned i) {
	return std::pair<IfcUtil::ArgumentType,ArgumentPtr>(getArgumentType(i),getArgument(i));
}
std::pair<IfcUtil::ArgumentType,ArgumentPtr> Ifc::IfcUntypedEntity::get_argument(const std::string& a) {
	return get_argument(Ifc2x3::Type::GetAttributeIndex(_type,a));
}
unsigned Ifc::IfcUntypedEntity::getArgumentIndex(const std::string& a) const {
	return Ifc2x3::Type::GetAttributeIndex(_type,a);
}
std::string Ifc::IfcUntypedEntity::toString() {
	return entity->toString(false);
}
bool Ifc::IfcUntypedEntity::is_valid() {
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
		if (!Ifc2x3::Type::GetAttributeOptional(_type,i) && is_null) {
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
