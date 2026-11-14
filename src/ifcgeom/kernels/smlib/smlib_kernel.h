/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCGEOM_SMLIB_KERNEL_H
#define IFCGEOM_SMLIB_KERNEL_H

#include "../../../ifcgeom/abstract_kernel.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"
#include "../../../ifcgeom/kernels/smlib/smlib_conversion_result.h"

namespace ifcopenshell {
namespace geom {
namespace kernels {

/// Geometry kernel backed by NVIDIA's SMLib boundary representation modeler,
/// part of the usd-brep project.
///
/// SMLib is a NURBS based solid modeler: profiles are swept into exact
/// boundary representations, boolean operations are evaluated on those, and
/// triangles are produced on demand by tessellating them.
///
/// @note SMLib runs single threaded in this configuration; concurrent
///       conversions in one process are not supported by the library.
class IFC_GEOMLIBRARY_API smlib_kernel : public abstract_kernel {
public:
	smlib_kernel(const ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root())
		: abstract_kernel("smlib", settings, logger) {}

	virtual abstract_kernel* clone(ifcopenshell::logger& logger) const {
		return new smlib_kernel(settings(), logger);
	}

	virtual bool supports_boolean_operations() const { return true; }

	virtual bool convert_impl(const taxonomy::extrusion::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::revolve::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::face::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::shell::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::solid::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
	virtual bool convert_impl(const taxonomy::boolean_result::ptr, std::vector<ifcopenshell::geom::conversion_result>&);

	virtual bool convert_openings(const express::base& entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geom::taxonomy::matrix4>>& openings,
		const std::vector<ifcopenshell::geom::conversion_result>& entity_shapes, const ifcopenshell::geom::taxonomy::matrix4& entity_trsf, std::vector<ifcopenshell::geom::conversion_result>& cut_shapes);
};

} // namespace kernels
} // namespace geom
} // namespace ifcopenshell

#endif
