#ifndef LAYERSET_H
#define LAYERSET_H

#include "IfcRepresentationShapeItem.h"

#include <Geom_Surface.hxx>

#include <list>
#include <vector>

namespace IfcGeom {
	namespace util {
		bool apply_layerset(const IfcRepresentationShapeItems&, const std::vector<Handle_Geom_Surface>&, const std::vector<std::shared_ptr<const SurfaceStyle>>&, IfcRepresentationShapeItems&, double tol);

		bool apply_folded_layerset(const IfcRepresentationShapeItems&, const std::vector< std::vector<Handle_Geom_Surface> >&, const std::vector<std::shared_ptr<const SurfaceStyle>>&, IfcRepresentationShapeItems&, double tol);

		bool split_solid_by_surface(const TopoDS_Shape&, const Handle_Geom_Surface&, TopoDS_Shape&, TopoDS_Shape&, double tol);

		bool split_solid_by_shell(const TopoDS_Shape&, const TopoDS_Shape& s, TopoDS_Shape&, TopoDS_Shape&, double tol);
	}
}

#endif