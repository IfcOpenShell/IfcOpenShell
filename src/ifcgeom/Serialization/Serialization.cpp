#include "Serialization.h"
#include "opencascade_geometry_ifc_writer_plugin.h"

#include "../../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"
#include "../../ifcparse/file.h"

#include <boost/algorithm/string/case_conv.hpp>

namespace {
	std::string writer_schema_key(const std::string& schema_name) {
		return boost::to_upper_copy(schema_name);
	}
}

ifcopenshell::geom::opencascade_geometry_ifc_writer_registry& ifcopenshell::geom::opencascade_geometry_ifc_writer_registry_instance() {
	static opencascade_geometry_ifc_writer_registry registry;
	return registry;
}

void ifcopenshell::geom::opencascade_geometry_ifc_writer_registry::bind(const std::string& schema_name, serialise_fn serialise, tesselate_fn tesselate, const ifcopenshell::plugin::module& module) {
	entry entry;
	entry.serialise_ = serialise;
	entry.tesselate_ = tesselate;
	entry.module_ = module.meta().id.empty() ? ifcopenshell::plugin::module(opencascade_geometry_ifc_writer_plugin_metadata(schema_name)) : module;
	entries_[writer_schema_key(schema_name)] = entry;
}

express::base ifcopenshell::geom::opencascade_geometry_ifc_writer_registry::tesselate(ifcopenshell::file& f, const conversion_result_shape& shape, double deflection) const {
	auto iter = entries_.find(writer_schema_key(f.schema()->name()));
	if (iter == entries_.end()) {
		load_opencascade_geometry_ifc_writer_plugin(const_cast<opencascade_geometry_ifc_writer_registry&>(*this), f.schema()->name());
		iter = entries_.find(writer_schema_key(f.schema()->name()));
	}
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No geometry serialization available for " + f.schema()->name());
	}
	return iter->second.tesselate_(f, shape, deflection);
}

express::base ifcopenshell::geom::opencascade_geometry_ifc_writer_registry::serialise(ifcopenshell::file& f, const conversion_result_shape& shape, bool advanced) const {
	auto iter = entries_.find(writer_schema_key(f.schema()->name()));
	if (iter == entries_.end()) {
		load_opencascade_geometry_ifc_writer_plugin(const_cast<opencascade_geometry_ifc_writer_registry&>(*this), f.schema()->name());
		iter = entries_.find(writer_schema_key(f.schema()->name()));
	}
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No geometry serialization available for " + f.schema()->name());
	}
	return iter->second.serialise_(f, shape, advanced);
}

express::base ifcopenshell::geom::tesselate(ifcopenshell::file& f, const conversion_result_shape& shape, double deflection) {
	return opencascade_geometry_ifc_writer_registry_instance().tesselate(f, shape, deflection);
}

express::base ifcopenshell::geom::serialise(ifcopenshell::file& f, const conversion_result_shape& shape, bool advanced) {
	return opencascade_geometry_ifc_writer_registry_instance().serialise(f, shape, advanced);
}

express::base ifcopenshell::geom::tesselate(ifcopenshell::file& f, const TopoDS_Shape& shape, double deflection) {
	ifcopenshell::geom::open_cascade_shape converted(shape);
	return tesselate(f, converted, deflection);
}

express::base ifcopenshell::geom::serialise(ifcopenshell::file& f, const TopoDS_Shape& shape, bool advanced) {
	ifcopenshell::geom::open_cascade_shape converted(shape);
	return serialise(f, converted, advanced);
}
