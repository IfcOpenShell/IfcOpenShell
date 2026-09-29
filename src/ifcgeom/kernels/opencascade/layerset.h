#ifndef LAYERSET_H
#define LAYERSET_H

#include "../../conversion_result.h"

#include <Geom_Surface.hxx>
#include <TopoDS_Shape.hxx>

#include <list>
#include <vector>

namespace ifcopenshell::geom {
	namespace util {
		bool apply_layerset(const std::vector<conversion_result>&, const std::vector<opencascade::handle<Geom_Surface>>&, const std::vector<ifcopenshell::geom::taxonomy::style::ptr>&, std::vector<conversion_result>&, double tol);

		bool apply_folded_layerset(const std::vector<conversion_result>&, const std::vector<std::vector<opencascade::handle<Geom_Surface>>>&, const std::vector<ifcopenshell::geom::taxonomy::style::ptr>&, std::vector<conversion_result>&, double tol);

		bool split_solid_by_surface(const TopoDS_Shape&, const opencascade::handle<Geom_Surface>&, TopoDS_Shape&, TopoDS_Shape&, double tol);

		bool split_solid_by_shell(const TopoDS_Shape&, const TopoDS_Shape& s, TopoDS_Shape&, TopoDS_Shape&, double tol);
	}
}

#endif
