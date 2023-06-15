#include "abstract_mapping.h"

#include "../ifcparse/IfcFile.h"

#include <boost/preprocessor/stringize.hpp>
#include <boost/preprocessor/seq/for_each.hpp>

#ifndef SCHEMA_SEQ
static_assert(false, "A boost preprocessor sequence of schema identifiers is needed for this file to compile.");
#endif

ifcopenshell::geometry::impl::MappingFactoryImplementation& ifcopenshell::geometry::impl::mapping_implementations() {
	static MappingFactoryImplementation impl;
	return impl;
}

// Declares the schema-based external kernel initialization routines:
// - extern void init_MappingImplementation_Ifc2x3(IfcGeom::impl::MappingFactoryImplementation*);
// - ...
#define EXTERNAL_DEFS(r, data, elem) \
	extern void BOOST_PP_CAT(init_MappingImplementation_Ifc, elem)(ifcopenshell::geometry::impl::MappingFactoryImplementation*);

// Declares the schema-based external iterator initialization routines:
// - init_MappingImplementation_Ifc2x3(this);
// - ...
#define CALL_DEFS(r, data, elem) \
	BOOST_PP_CAT(init_MappingImplementation_Ifc, elem)(this);

BOOST_PP_SEQ_FOR_EACH(EXTERNAL_DEFS, , SCHEMA_SEQ)

ifcopenshell::geometry::impl::MappingFactoryImplementation::MappingFactoryImplementation() {
	BOOST_PP_SEQ_FOR_EACH(CALL_DEFS, , SCHEMA_SEQ)
}

void ifcopenshell::geometry::impl::MappingFactoryImplementation::bind(const std::string& schema_name, ifcopenshell::geometry::impl::mapping_fn fn) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, fn));
}

ifcopenshell::geometry::abstract_mapping* ifcopenshell::geometry::impl::MappingFactoryImplementation::construct(IfcParse::IfcFile* file, Settings& s) {
	const std::string schema_name_lower = boost::to_lower_copy(file->schema()->name());
	std::map<std::string, ifcopenshell::geometry::impl::mapping_fn>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == end()) {
		throw IfcParse::IfcException("No geometry mapping registered for " + schema_name_lower);
	}
	auto new_mapping = it->second(file, s);
	new_mapping->initialize_settings();
	return new_mapping;
}
