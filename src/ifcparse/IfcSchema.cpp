#include "IfcSchema.h"

#include <map>

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

static std::map<std::string, const IfcParse::schema_definition*> schemas;

IfcParse::schema_definition::schema_definition(const std::string& name, const std::vector<const declaration*>& declarations, const bool built_in = false)
	: name_(name)
	, declarations_(declarations)
	, built_in_(built_in)
{
	std::sort(declarations_.begin(), declarations_.end(), declaration_by_enum_sort());
	for (std::vector<const declaration*>::const_iterator it = declarations_.begin(); it != declarations_.end(); ++it) {
		if ((**it).as_type_declaration()) type_declarations_.push_back((**it).as_type_declaration());
		if ((**it).as_select_type()) select_types_.push_back((**it).as_select_type());
		if ((**it).as_enumeration_type()) enumeration_types_.push_back((**it).as_enumeration_type());
		if ((**it).as_entity()) entities_.push_back((**it).as_entity());
	}
	schemas[name_] = this;
}

IfcParse::schema_definition::~schema_definition() {
	schemas.erase(name_);
	for (std::vector<const declaration*>::const_iterator it = declarations_.begin(); it != declarations_.end(); ++it) {
		delete *it;
	}
}

const IfcParse::schema_definition* schema_by_name(const std::string& name) {
	std::map<std::string, IfcParse::schema_definition*>::const_iterator it = schemas.find(name);
	if (it == schemas.end()) {
		throw IfcParse::IfcException("No schema named " + name);
	}
	return it->second;
}