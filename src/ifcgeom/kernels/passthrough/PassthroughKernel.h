#ifndef PASSTHROUGH_KERNEL_H
#define PASSTHROUGH_KERNEL_H

#include "../../../ifcgeom/AbstractKernel.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"
#include "../../../ifcgeom/kernels/passthrough/PassthroughConversionResult.h"

namespace ifcopenshell {
namespace geometry {
namespace kernels {

class IFC_GEOMLIBRARY_API PassthroughKernel : public AbstractKernel {
public:
	PassthroughKernel(const Settings& settings)
		: AbstractKernel("passthrough", settings) {}

	virtual AbstractKernel* clone() const {
		return new PassthroughKernel(settings());
	}

	virtual bool supports_boolean_operations() const { return false; }

	virtual bool convert_impl(const taxonomy::shell::ptr, IfcGeom::ConversionResults&);
	virtual bool convert_impl(const taxonomy::solid::ptr, IfcGeom::ConversionResults&);
	virtual bool convert_impl(const taxonomy::extrusion::ptr, IfcGeom::ConversionResults&);

	virtual bool convert_openings(const express::Base&, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geometry::taxonomy::matrix4>>&,
		const IfcGeom::ConversionResults&, const ifcopenshell::geometry::taxonomy::matrix4&, IfcGeom::ConversionResults&);
};

}
}
}

#endif
