#include "abstract_mapping.h"

#include "../ifcparse/file.h"
#include "../ifcgeom/mapping_plugin.h"

#include <boost/algorithm/string/case_conv.hpp>

namespace {
	std::string mapping_key(const std::string& schema_name) {
		return boost::to_lower_copy(schema_name);
	}

}

ifcopenshell::geometry::impl::mapping_registry& ifcopenshell::geometry::impl::mapping_registry_instance() {
	static mapping_registry registry;
	return registry;
}

void ifcopenshell::geometry::impl::mapping_registry::bind(const std::string& schema_name, ifcopenshell::geometry::impl::mapping_fn fn, const plugin::module& module) {
	auto& entry = entries_[mapping_key(schema_name)];
	entry.fn_ = fn;
	entry.module_ = module.meta().id.empty() ? plugin::module(mapping_plugin_metadata(schema_name)) : module;
}

ifcopenshell::geometry::abstract_mapping* ifcopenshell::geometry::impl::mapping_registry::construct(ifcopenshell::file* file, Settings& s, ::logger& log) {
	const std::string schema_name_lower = boost::to_lower_copy(file->schema()->name());
	auto it = entries_.find(schema_name_lower);
	if (it == entries_.end()) {
		load_mapping_plugin(*this, file->schema()->name());
		it = entries_.find(schema_name_lower);
	}
	if (it == entries_.end()) {
		throw ifcopenshell::exception("No geometry mapping registered for " + schema_name_lower);
	}
	auto new_mapping = it->second.fn_(file, s, log);
	try {
		new_mapping->initialize_settings();
	} catch (const std::exception& e) {
		log.error("GEO", 400, e);
		log.error("GEO", 401, "Unable to initialize conversion settings");
	}
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
	mapping_registry_instance().bind(schema_name, fn, plugin::module(mapping_plugin_metadata(schema_name)));
}

ifcopenshell::geometry::abstract_mapping* ifcopenshell::geometry::impl::MappingFactoryImplementation::construct(ifcopenshell::file* file, Settings& s, ::logger& log) {
	return mapping_registry_instance().construct(file, s, log);
}
