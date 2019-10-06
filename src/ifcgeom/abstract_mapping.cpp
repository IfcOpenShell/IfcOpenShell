#include "abstract_mapping.h"

#include "../ifcparse/IfcFile.h"

ifcopenshell::geometry::impl::MappingFactoryImplementation& ifcopenshell::geometry::impl::mapping_implementations() {
	static MappingFactoryImplementation impl;
	return impl;
}

extern void init_MappingImplementation_Ifc2x3(ifcopenshell::geometry::impl::MappingFactoryImplementation*);
extern void init_MappingImplementation_Ifc4(ifcopenshell::geometry::impl::MappingFactoryImplementation*);
extern void init_MappingImplementation_Ifc4x1(ifcopenshell::geometry::impl::MappingFactoryImplementation*);
extern void init_MappingImplementation_Ifc4x2(ifcopenshell::geometry::impl::MappingFactoryImplementation*);

ifcopenshell::geometry::impl::MappingFactoryImplementation::MappingFactoryImplementation() {
	init_MappingImplementation_Ifc2x3(this);
	init_MappingImplementation_Ifc4(this);
	init_MappingImplementation_Ifc4x1(this);
	init_MappingImplementation_Ifc4x2(this);
}

void ifcopenshell::geometry::impl::MappingFactoryImplementation::bind(const std::string& schema_name, ifcopenshell::geometry::impl::mapping_fn fn) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, fn));
}

ifcopenshell::geometry::abstract_mapping* ifcopenshell::geometry::impl::MappingFactoryImplementation::construct(IfcParse::IfcFile* file, settings& s) {
	const std::string schema_name_lower = boost::to_lower_copy(file->schema()->name());
	std::map<std::string, ifcopenshell::geometry::impl::mapping_fn>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == end()) {
		throw IfcParse::IfcException("No geometry mapping registered for " + schema_name_lower);
	}
	return it->second(file, s);
}
