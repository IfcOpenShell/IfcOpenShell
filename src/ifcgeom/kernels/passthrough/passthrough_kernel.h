#ifndef PASSTHROUGH_KERNEL_H
#define PASSTHROUGH_KERNEL_H

#include "../../../ifcgeom/abstract_kernel.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"
#include "../../../ifcgeom/kernels/passthrough/passthrough_conversion_result.h"

namespace ifcopenshell {
namespace geom {
namespace kernels {

class IFC_GEOMLIBRARY_API passthrough_kernel : public abstract_kernel {
public:
	passthrough_kernel(const ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root())
		: abstract_kernel("passthrough", settings, logger) {}

	virtual abstract_kernel* clone(ifcopenshell::logger& logger) const {
		return new passthrough_kernel(settings(), logger);
	}

	virtual bool supports_boolean_operations() const { return false; }

	virtual bool convert_impl(const taxonomy::shell::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::solid::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::extrusion::ptr, std::vector<ifcopenshell::geom::conversion_result>&);

	virtual bool convert_openings(const express::base&, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geom::taxonomy::matrix4>>&,
		const std::vector<ifcopenshell::geom::conversion_result>&, const ifcopenshell::geom::taxonomy::matrix4&, std::vector<ifcopenshell::geom::conversion_result>&);
};

}
}
}

#endif
