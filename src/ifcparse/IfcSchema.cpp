#include "IfcSchema.h"

bool IfcParse::declaration::is(const std::string& name) const {
	return is(IfcSchema::Type::FromString(name));
}

bool IfcParse::declaration::is(IfcSchema::Type::Enum name) const {
	if (this->as_entity()) {
		return this->as_entity()->is(name);
	} else {
		return this->name() == IfcSchema::Type::ToString(name);
	}
}

bool IfcParse::named_type::is(const std::string& name) const {
	return declared_type()->is(name);
}

bool IfcParse::named_type::is(IfcSchema::Type::Enum name) const {
	return declared_type()->is(name);
}