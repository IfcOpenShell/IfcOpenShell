#include "Serialization.h"

#include "../../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"
#include "../../ifcparse/file.h"

#include <boost/algorithm/string/case_conv.hpp>
#include <boost/preprocessor/stringize.hpp>
#include <boost/preprocessor/seq/for_each.hpp>

#include <mutex>

namespace {
	std::string writer_schema_key(const std::string& schema_name) {
		return boost::to_upper_copy(schema_name);
	}

	ifcopenshell::plugin::module builtin_writer_module(const std::string& schema_name) {
		ifcopenshell::plugin::metadata metadata;
		metadata.kind_ = ifcopenshell::plugin::kind::opencascade_geometry_ifc_writer;
		metadata.id = "geometry.ifc_writer." + boost::to_lower_copy(schema_name);
		metadata.schema = schema_name;
		return ifcopenshell::plugin::module::builtin(metadata);
	}

	const ifcopenshell::geometry::OpenCascadeShape& require_opencascade_shape(const IfcGeom::ConversionResultShape& shape) {
		const auto* oc_shape = dynamic_cast<const ifcopenshell::geometry::OpenCascadeShape*>(&shape);
		if (!oc_shape) {
			throw ifcopenshell::exception("OpenCascade geometry IFC writer requires an opencascade conversion result shape");
		}
		return *oc_shape;
	}

	template <express::Base(*Fn)(ifcopenshell::file&, const TopoDS_Shape&, bool)>
	express::Base serialise_adapter(ifcopenshell::file& f, const IfcGeom::ConversionResultShape& shape, bool advanced) {
		return Fn(f, require_opencascade_shape(shape).shape(), advanced);
	}

	template <express::Base(*Fn)(ifcopenshell::file&, const TopoDS_Shape&, double)>
	express::Base tesselate_adapter(ifcopenshell::file& f, const IfcGeom::ConversionResultShape& shape, double deflection) {
		return Fn(f, require_opencascade_shape(shape).shape(), deflection);
	}
}

#define EXTERNAL_TESSELATE(r, data, elem) \
	express::Base BOOST_PP_CAT(tesselate_Ifc, elem)(ifcopenshell::file&, const TopoDS_Shape& shape, double deflection);

#define EXTERNAL_SERIALISE(r, data, elem) \
	express::Base BOOST_PP_CAT(serialise_Ifc, elem)(ifcopenshell::file&, const TopoDS_Shape& shape, bool advanced);

#define BIND_WRITER(r, data, elem) \
	registry.bind(BOOST_PP_STRINGIZE(BOOST_PP_CAT(Ifc, elem)), \
		&serialise_adapter<BOOST_PP_CAT(serialise_Ifc, elem)>, \
		&tesselate_adapter<BOOST_PP_CAT(tesselate_Ifc, elem)>, \
		builtin_writer_module(BOOST_PP_STRINGIZE(BOOST_PP_CAT(Ifc, elem))));

BOOST_PP_SEQ_FOR_EACH(EXTERNAL_TESSELATE, , SCHEMA_SEQ)
BOOST_PP_SEQ_FOR_EACH(EXTERNAL_SERIALISE, , SCHEMA_SEQ)

IfcGeom::opencascade_geometry_ifc_writer_registry& IfcGeom::opencascade_geometry_ifc_writer_registry_instance() {
	static opencascade_geometry_ifc_writer_registry registry;
	static std::once_flag once;
	std::call_once(once, []() {
		BOOST_PP_SEQ_FOR_EACH(BIND_WRITER, , SCHEMA_SEQ)
	});
	return registry;
}

void IfcGeom::opencascade_geometry_ifc_writer_registry::bind(const std::string& schema_name, serialise_fn serialise, tesselate_fn tesselate, const ifcopenshell::plugin::module& module) {
	entry entry;
	entry.serialise_ = serialise;
	entry.tesselate_ = tesselate;
	entry.module_ = module;
	entries_[writer_schema_key(schema_name)] = entry;
}

express::Base IfcGeom::opencascade_geometry_ifc_writer_registry::tesselate(ifcopenshell::file& f, const ConversionResultShape& shape, double deflection) const {
	const auto iter = entries_.find(writer_schema_key(f.schema()->name()));
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No geometry serialization available for " + f.schema()->name());
	}
	return iter->second.tesselate_(f, shape, deflection);
}

express::Base IfcGeom::opencascade_geometry_ifc_writer_registry::serialise(ifcopenshell::file& f, const ConversionResultShape& shape, bool advanced) const {
	const auto iter = entries_.find(writer_schema_key(f.schema()->name()));
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
