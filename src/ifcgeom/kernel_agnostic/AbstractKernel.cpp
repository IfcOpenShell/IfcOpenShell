#include "AbstractKernel.h"

#include "../../ifcgeom/schema_agnostic/IfcGeomElement.h"
#include "../../ifcgeom/kernels/opencascade/OpenCascadeKernel.h"

#undef Handle

#include "../../ifcgeom/kernels/cgal/CgalKernel.h"

bool ifcopenshell::geometry::kernels::AbstractKernel::convert(const taxonomy::item* item, ifcopenshell::geometry::ConversionResults& results) {
	try {
		return dispatch_conversion<0>::dispatch(this, item, results);
	} catch (std::exception& e) {
		Logger::Error(e, item->instance);
		return false;
	}
}

ifcopenshell::geometry::kernels::AbstractKernel* ifcopenshell::geometry::kernels::construct(const std::string& geometry_library, IfcParse::IfcFile* file) {
	const std::string geometry_library_lower = boost::to_lower_copy(geometry_library);
	if (geometry_library_lower == "opencascade") {
		return new OpenCascadeKernel(settings);
	} else if (geometry_library_lower == "cgal") {
		return new CgalKernel(settings);
	} else {
		throw IfcParse::IfcException("No geometry kernel registered for " + geometry_library);
	}
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::collection* collection, ifcopenshell::geometry::ConversionResults& r) { 
	auto s = r.size();
	for (auto& c : collection->children) {
		convert(c, r);
	}
	for (auto i = s; i < r.size(); ++i) {
		r[i].prepend(collection->matrix);
		if (!r[i].hasStyle()) {
			r[i].setStyle(collection->surface_style);
		}
	}
	return r.size() > s;
}
