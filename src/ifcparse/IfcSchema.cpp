#include "IfcSchema.h"

#include <map>

bool IfcParse::declaration::is(const std::string& name) const {
	if (name_ == name) return true;

	if (this->as_entity()) {
		return this->as_entity()->is(name);
	} else if (this->as_type_declaration()) {
		const IfcParse::named_type* nt = this->as_type_declaration()->declared_type()->as_named_type();
		if (nt) return nt->is(name);
	}

	return false;
}

bool IfcParse::declaration::is(const IfcParse::declaration& decl) const {
	if (this == &decl) return true;

	if (this->as_entity()) {
		return this->as_entity()->is(decl);
	} else if (this->as_type_declaration()) {
		const IfcParse::named_type* nt = this->as_type_declaration()->declared_type()->as_named_type();
		if (nt) return nt->is(decl);
	}

	return false;
}

bool IfcParse::named_type::is(const std::string& name) const {
	return declared_type()->is(name);
}

bool IfcParse::named_type::is(const IfcParse::declaration& decl) const {
	return declared_type()->is(decl);
}

static std::map<std::string, const IfcParse::schema_definition*> schemas;

IfcParse::schema_definition::schema_definition(const std::string& name, const std::vector<const declaration*>& declarations, instance_factory* factory)
	: name_(name)
	, declarations_(declarations)
	, factory_(factory)
{
	std::sort(declarations_.begin(), declarations_.end(), declaration_by_index_sort());
	for (std::vector<const declaration*>::iterator it = declarations_.begin(); it != declarations_.end(); ++it) {
		(**it).schema_ = this;

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

#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/Ifc4.h"

const IfcParse::schema_definition* IfcParse::schema_by_name(const std::string& name) {
	// TODO: initialize automatically somehow
	Ifc2x3::get_schema();
	Ifc4::get_schema();

	std::map<std::string, const IfcParse::schema_definition*>::const_iterator it = schemas.find(name);
	if (it == schemas.end()) {
		throw IfcParse::IfcException("No schema named " + name);
	}
	return it->second;
}