#include "abstract_mapping.h"

#include "../ifcparse/file.h"
#include "../ifcgeom/mapping_plugin.h"

#include <boost/algorithm/string/case_conv.hpp>

namespace {
	std::string mapping_key(const std::string& schema_name) {
		return boost::to_lower_copy(schema_name);
	}

}

ifcopenshell::geom::impl::mapping_registry& ifcopenshell::geom::impl::mapping_registry_instance() {
	static mapping_registry registry;
	return registry;
}

void ifcopenshell::geom::impl::mapping_registry::bind(const std::string& schema_name, ifcopenshell::geom::impl::mapping_fn fn, const plugin::module& module) {
	auto& entry = entries_[mapping_key(schema_name)];
	entry.fn_ = fn;
	entry.module_ = module.meta().id.empty() ? plugin::module(mapping_plugin_metadata(schema_name)) : module;
}

bool ifcopenshell::geom::impl::mapping_registry::has(const std::string& schema_name) const {
	return entries_.find(mapping_key(schema_name)) != entries_.end();
}

ifcopenshell::geom::abstract_mapping* ifcopenshell::geom::impl::mapping_registry::construct(ifcopenshell::file* file, ifcopenshell::geom::settings& settings, ifcopenshell::logger& log) {
	const std::string schema_name_lower = boost::to_lower_copy(file->schema()->name());
	auto it = entries_.find(schema_name_lower);
	if (it == entries_.end()) {
		load_mapping_plugin(*this, file->schema()->name());
		it = entries_.find(schema_name_lower);
	}
	if (it == entries_.end()) {
		throw ifcopenshell::exception("No geometry mapping registered for " + schema_name_lower);
	}
	auto new_mapping = it->second.fn_(file, settings, log);
	try {
		new_mapping->initialize_settings();
	} catch (const std::exception& e) {
		log.error("GEO", 400, e);
		log.error("GEO", 401, "Unable to initialize conversion settings");
	}
	return new_mapping;
}

ifcopenshell::geom::impl::mapping_factory_implementation& ifcopenshell::geom::impl::mapping_implementations() {
	static mapping_factory_implementation impl;
	return impl;
}

ifcopenshell::geom::impl::mapping_factory_implementation::mapping_factory_implementation() {
	mapping_registry_instance();
}

void ifcopenshell::geom::impl::mapping_factory_implementation::bind(const std::string& schema_name, ifcopenshell::geom::impl::mapping_fn fn) {
	mapping_registry_instance().bind(schema_name, fn, plugin::module(mapping_plugin_metadata(schema_name)));
}

ifcopenshell::geom::abstract_mapping* ifcopenshell::geom::impl::mapping_factory_implementation::construct(ifcopenshell::file* file, ifcopenshell::geom::settings& settings, ifcopenshell::logger& log) {
	return mapping_registry_instance().construct(file, settings, log);
}
