#ifndef MANIFOLD_KERNEL_H
#define MANIFOLD_KERNEL_H

#include <manifold/manifold.h>

#include "../../../ifcgeom/AbstractKernel.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"
#include "../../../ifcgeom/kernels/manifold/ManifoldConversionResult.h"

namespace ifcopenshell {
namespace geom {
namespace kernels {

class IFC_GEOMLIBRARY_API manifold_kernel : public abstract_kernel {
public:
	manifold_kernel(const ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root())
		: abstract_kernel("manifold", settings, logger) {}

	virtual abstract_kernel* clone(ifcopenshell::logger& logger) const {
		return new manifold_kernel(settings(), logger);
	}

	virtual bool supports_openings() const { return true; }
	virtual bool supports_boolean_operations() const { return true; }

	virtual bool convert_impl(const taxonomy::extrusion::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const taxonomy::shell::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const taxonomy::solid::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const taxonomy::boolean_result::ptr, ifcopenshell::geom::conversion_results&);

	double dilation_hack = 0.;

	virtual bool convert_openings(const express::base& entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geom::taxonomy::matrix4>>& openings,
		const ifcopenshell::geom::conversion_results& entity_shapes, const ifcopenshell::geom::taxonomy::matrix4& entity_trsf, ifcopenshell::geom::conversion_results& cut_shapes);
};

}
}
}

#endif
