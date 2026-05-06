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

IfcGeom::opencascade_geometry_ifc_writer_registry& IfcGeom::opencascade_geometry_ifc_writer_registry_instance() {
	static opencascade_geometry_ifc_writer_registry registry;
	return registry;
}

void IfcGeom::opencascade_geometry_ifc_writer_registry::bind(const std::string& schema_name, serialise_fn serialise, tesselate_fn tesselate, const ifcopenshell::plugin::module& module) {
	entry entry;
	entry.serialise_ = serialise;
	entry.tesselate_ = tesselate;
	entry.module_ = module.meta().id.empty() ? ifcopenshell::plugin::module(opencascade_geometry_ifc_writer_plugin_metadata(schema_name)) : module;
	entries_[writer_schema_key(schema_name)] = entry;
}

express::Base IfcGeom::opencascade_geometry_ifc_writer_registry::tesselate(ifcopenshell::file& f, const ConversionResultShape& shape, double deflection) const {
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

express::Base IfcGeom::opencascade_geometry_ifc_writer_registry::serialise(ifcopenshell::file& f, const ConversionResultShape& shape, bool advanced) const {
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

express::Base IfcGeom::tesselate(ifcopenshell::file& f, const ConversionResultShape& shape, double deflection) {
	return opencascade_geometry_ifc_writer_registry_instance().tesselate(f, shape, deflection);
}

express::Base IfcGeom::serialise(ifcopenshell::file& f, const ConversionResultShape& shape, bool advanced) {
	return opencascade_geometry_ifc_writer_registry_instance().serialise(f, shape, advanced);
}

express::Base IfcGeom::tesselate(ifcopenshell::file& f, const TopoDS_Shape& shape, double deflection) {
	ifcopenshell::geometry::OpenCascadeShape converted(shape);
	return tesselate(f, converted, deflection);
}

express::Base IfcGeom::serialise(ifcopenshell::file& f, const TopoDS_Shape& shape, bool advanced) {
	ifcopenshell::geometry::OpenCascadeShape converted(shape);
	return serialise(f, converted, advanced);
}
