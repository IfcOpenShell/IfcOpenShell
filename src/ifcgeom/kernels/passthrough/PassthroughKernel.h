#ifndef PASSTHROUGH_KERNEL_H
#define PASSTHROUGH_KERNEL_H

#include "../../../ifcgeom/AbstractKernel.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"
#include "../../../ifcgeom/kernels/passthrough/PassthroughConversionResult.h"

namespace ifcopenshell {
namespace geom {
namespace kernels {

class IFC_GEOMLIBRARY_API passthrough_kernel : public abstract_kernel {
public:
	passthrough_kernel(const ifcopenshell::geom::settings& settings, ::logger& logger = ::logger::root())
		: abstract_kernel("passthrough", settings, logger) {}

	virtual abstract_kernel* clone(::logger& logger) const {
		return new passthrough_kernel(settings(), logger);
	}

	virtual bool supports_boolean_operations() const { return false; }

	virtual bool convert_impl(const taxonomy::shell::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const taxonomy::solid::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const taxonomy::extrusion::ptr, ifcopenshell::geom::conversion_results&);

	virtual bool convert_openings(const express::base&, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geom::taxonomy::matrix4>>&,
		const ifcopenshell::geom::conversion_results&, const ifcopenshell::geom::taxonomy::matrix4&, ifcopenshell::geom::conversion_results&);
};

}
}
}

#endif
