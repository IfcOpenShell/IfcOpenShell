#ifndef MANIFOLD_KERNEL_H
#define MANIFOLD_KERNEL_H

#include <manifold/manifold.h>

#include "../../../ifcgeom/AbstractKernel.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"
#include "../../../ifcgeom/kernels/manifold/ManifoldConversionResult.h"

namespace ifcopenshell {
namespace geometry {
namespace kernels {

class IFC_GEOMLIBRARY_API ManifoldKernel : public AbstractKernel {
public:
	ManifoldKernel(const Settings& settings)
		: AbstractKernel("manifold", settings) {}

	virtual AbstractKernel* clone() const {
		return new ManifoldKernel(settings());
	}

	virtual bool supports_boolean_operations() const { return true; }

	virtual bool convert_impl(const taxonomy::extrusion::ptr, IfcGeom::ConversionResults&);
	virtual bool convert_impl(const taxonomy::shell::ptr, IfcGeom::ConversionResults&);
	virtual bool convert_impl(const taxonomy::solid::ptr, IfcGeom::ConversionResults&);
	virtual bool convert_impl(const taxonomy::boolean_result::ptr, IfcGeom::ConversionResults&);

	virtual bool convert_openings(const express::Base& entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geometry::taxonomy::matrix4>>& openings,
		const IfcGeom::ConversionResults& entity_shapes, const ifcopenshell::geometry::taxonomy::matrix4& entity_trsf, IfcGeom::ConversionResults& cut_shapes);
};

}
}
}

#endif
