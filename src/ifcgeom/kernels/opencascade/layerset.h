#ifndef LAYERSET_H
#define LAYERSET_H

#include "../../ConversionResult.h"

#include <Geom_Surface.hxx>
#include <TopoDS_Shape.hxx>

#include <list>
#include <vector>

namespace IfcGeom {
	namespace util {
		bool apply_layerset(const ConversionResults&, const std::vector<Handle_Geom_Surface>&, const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>&, ConversionResults&, double tol);

		bool apply_folded_layerset(const ConversionResults&, const std::vector< std::vector<Handle_Geom_Surface> >&, const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>&, ConversionResults&, double tol);

		bool split_solid_by_surface(const TopoDS_Shape&, const Handle_Geom_Surface&, TopoDS_Shape&, TopoDS_Shape&, double tol);

		bool split_solid_by_shell(const TopoDS_Shape&, const TopoDS_Shape& s, TopoDS_Shape&, TopoDS_Shape&, double tol);
	}
}

#endif