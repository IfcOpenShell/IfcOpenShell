#include "abstract_mapping.h"

#include "../ifcparse/file.h"

#include <boost/preprocessor/stringize.hpp>
#include <boost/preprocessor/seq/for_each.hpp>
#include <mutex>

#ifndef SCHEMA_SEQ
static_assert(false, "A boost preprocessor sequence of schema identifiers is needed for this file to compile.");
#endif

// Declares the schema-based external kernel initialization routines:
// - extern void init_MappingImplementation_Ifc2x3(IfcGeom::impl::mapping_registry*);
// - ...
#define EXTERNAL_DEFS(r, data, elem) \
	extern void BOOST_PP_CAT(init_MappingImplementation_Ifc, elem)(ifcopenshell::geometry::impl::mapping_registry*);

// Declares the schema-based external iterator initialization routines:
// - init_MappingImplementation_Ifc2x3(this);
// - ...
#define CALL_DEFS(r, data, elem) \
	BOOST_PP_CAT(init_MappingImplementation_Ifc, elem)(&registry);

BOOST_PP_SEQ_FOR_EACH(EXTERNAL_DEFS, , SCHEMA_SEQ)

namespace {
	std::string mapping_key(const std::string& schema_name) {
		return boost::to_lower_copy(schema_name);
	}

	ifcopenshell::plugin::module builtin_mapping_module(const std::string& schema_name) {
		ifcopenshell::plugin::metadata metadata;
		metadata.kind_ = ifcopenshell::plugin::kind::mapping;
		metadata.id = "geometry.mapping." + boost::to_lower_copy(schema_name);
		metadata.schema = schema_name;
		return ifcopenshell::plugin::module::builtin(metadata);
	}

}

ifcopenshell::geometry::impl::mapping_registry& ifcopenshell::geometry::impl::mapping_registry_instance() {
	static mapping_registry registry;
	static std::once_flag once;
	std::call_once(once, []() {
		BOOST_PP_SEQ_FOR_EACH(CALL_DEFS, , SCHEMA_SEQ)
	});
	return registry;
}

void ifcopenshell::geometry::impl::mapping_registry::bind(const std::string& schema_name, ifcopenshell::geometry::impl::mapping_fn fn, const plugin::module& module) {
	auto& entry = entries_[mapping_key(schema_name)];
	entry.fn_ = fn;
	entry.module_ = module.meta().id.empty() ? builtin_mapping_module(schema_name) : module;
}

ifcopenshell::geometry::abstract_mapping* ifcopenshell::geometry::impl::mapping_registry::construct(ifcopenshell::file* file, Settings& s) {
	const std::string schema_name_lower = boost::to_lower_copy(file->schema()->name());
	const auto it = entries_.find(schema_name_lower);
	if (it == entries_.end()) {
		throw ifcopenshell::exception("No geometry mapping registered for " + schema_name_lower);
	}
	auto new_mapping = it->second.fn_(file, s);
	new_mapping->initialize_settings();
	return new_mapping;
}

ifcopenshell::geometry::impl::MappingFactoryImplementation& ifcopenshell::geometry::impl::mapping_implementations() {
	static MappingFactoryImplementation impl;
	return impl;
}

ifcopenshell::geometry::impl::MappingFactoryImplementation::MappingFactoryImplementation() {
	mapping_registry_instance();
}

void ifcopenshell::geometry::impl::MappingFactoryImplementation::bind(const std::string& schema_name, ifcopenshell::geometry::impl::mapping_fn fn) {
	mapping_registry_instance().bind(schema_name, fn, builtin_mapping_module(schema_name));
}

ifcopenshell::geometry::abstract_mapping* ifcopenshell::geometry::impl::MappingFactoryImplementation::construct(ifcopenshell::file* file, Settings& s) {
	return mapping_registry_instance().construct(file, s);
}
