#include "conversion_result.h"
#include "representation.h"

ifcopenshell::geom::triangulation* ifcopenshell::geom::conversion_result_shape::Triangulate(const ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger) const
{
	auto t = ifcopenshell::geom::triangulation::empty(settings);
	static ifcopenshell::geom::taxonomy::matrix4 iden;
	Triangulate(settings, iden, t, -1, -1, logger);
	return t;
}

using namespace ifcopenshell::geom::taxonomy;

void ifcopenshell::geom::conversion_result::append(ifcopenshell::geom::taxonomy::matrix4::ptr trsf) {
	placement_ = make<matrix4>(placement_->ccomponents() * trsf->ccomponents());
}

void ifcopenshell::geom::conversion_result::prepend(ifcopenshell::geom::taxonomy::matrix4::ptr trsf) {
	placement_ = make<matrix4>(trsf->ccomponents() * placement_->ccomponents());
}

template struct IFC_GEOM_API ifcopenshell::geom::opaque_coordinate<3>;
template struct IFC_GEOM_API ifcopenshell::geom::opaque_coordinate<4>;
