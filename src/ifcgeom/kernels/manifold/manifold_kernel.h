#ifndef MANIFOLD_KERNEL_H
#define MANIFOLD_KERNEL_H

#include <manifold/manifold.h>

#include "../../../ifcgeom/abstract_kernel.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"
#include "../../../ifcgeom/kernels/manifold/manifold_conversion_result.h"

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

	virtual bool convert_impl(const taxonomy::extrusion::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::shell::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::solid::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::boolean_result::ptr, std::vector<ifcopenshell::geom::conversion_result>&);

	double dilation_hack = 0.;

	virtual bool convert_openings(const express::base& entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geom::taxonomy::matrix4>>& openings,
		const std::vector<ifcopenshell::geom::conversion_result>& entity_shapes, const ifcopenshell::geom::taxonomy::matrix4& entity_trsf, std::vector<ifcopenshell::geom::conversion_result>& cut_shapes);
};

}
}
}

#endif
