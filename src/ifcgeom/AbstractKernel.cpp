#include "AbstractKernel.h"

#include "../ifcgeom/IfcGeomElement.h"
#include "../ifcgeom/ConversionSettings.h"

#ifdef IFOPSH_WITH_OPENCASCADE
#include "../ifcgeom/kernels/opencascade/OpenCascadeKernel.h"
#undef Handle
#endif

#ifdef IFOPSH_WITH_CGAL
#include "../ifcgeom/kernels/cgal/CgalKernel.h"
#undef CGAL_KERNEL_H
#undef CGALCONVERSIONRESULT_H
#define IFOPSH_SIMPLE_KERNEL
#include "../ifcgeom/kernels/cgal/CgalKernel.h"
#endif

using namespace ifcopenshell::geometry;

bool ifcopenshell::geometry::kernels::AbstractKernel::convert(const taxonomy::item* item, IfcGeom::ConversionResults& results) {
	// std::stringstream ss;
	// item->print(ss);
	// auto sss = ss.str();
	// std::wcout << sss.c_str() << std::endl;

	try {
		return dispatch_conversion<0>::dispatch(this, item, results);
	} catch (std::exception& e) {
		Logger::Error(e, item->instance);
		return false;
	}
}

const ConversionSettings & ifcopenshell::geometry::kernels::AbstractKernel::settings() const
{
	return conv_settings_;
}

ifcopenshell::geometry::kernels::AbstractKernel* ifcopenshell::geometry::kernels::construct(const std::string& geometry_library, const ConversionSettings& conv_settings) {
	const std::string geometry_library_lower = boost::to_lower_copy(geometry_library);

#ifdef IFOPSH_WITH_OPENCASCADE
	if (geometry_library_lower == "opencascade") {
		return new IfcGeom::OpenCascadeKernel(conv_settings);
	}
#endif

#ifdef IFOPSH_WITH_CGAL
	if (geometry_library_lower == "cgal") {
		return new CgalKernel(conv_settings);
	}

	if (geometry_library_lower == "cgal-simple") {
		return new SimpleCgalKernel(conv_settings);
	}
#endif
	
	throw IfcParse::IfcException("No geometry kernel registered for " + geometry_library);
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::collection* collection, IfcGeom::ConversionResults& r) {
	auto s = r.size();
	for (auto& c : collection->children) {
		convert(c, r);
	}
	for (auto i = s; i < r.size(); ++i) {
		r[i].prepend(collection->matrix);
		if (!r[i].hasStyle() && collection->surface_style) {
			r[i].setStyle(*collection->surface_style);
		}
	}
	return r.size() > s;
}
