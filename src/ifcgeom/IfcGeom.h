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

#ifndef IFCGEOM_H
#define IFCGEOM_H

#define ALMOST_ZERO (1e-9)
#define ALMOST_THE_SAME(a,b) (fabs(a-b) < ALMOST_ZERO)

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <Geom_Curve.hxx>
#include <gp_Pln.hxx>

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcUtil.h"

#include "../ifcgeom/IfcShapeList.h"

#define FACESET_AS_COMPOUND 1

namespace IfcGeom {
	bool convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face);
	bool convert_shapes(const IfcUtil::IfcBaseClass* L, ShapeList& result);
	bool is_shape_collection(const IfcUtil::IfcBaseClass* L);
	const TopoDS_Shape* convert_shape(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
	bool convert_wire(const IfcUtil::IfcBaseClass* L, TopoDS_Wire& result);
	bool convert_curve(const IfcUtil::IfcBaseClass* L, Handle(Geom_Curve)& result);
	bool convert_face(const IfcUtil::IfcBaseClass* L, TopoDS_Face& result);
	bool convert_openings(const Ifc2x3::IfcProduct::ptr entity, const Ifc2x3::IfcRelVoidsElement::list& openings, const ShapeList& entity_shapes, const gp_Trsf& entity_trsf, ShapeList& cut_shapes);
	bool create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& solid);
	bool is_compound(const TopoDS_Shape& shape);
	const TopoDS_Shape& ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid);
	bool profile_helper(int numVerts, float* verts, int numFillets, int* filletIndices, float* filletRadii, gp_Trsf2d trsf, TopoDS_Face& face); 
	float shape_volume(const TopoDS_Shape& s);
	namespace Cache {
		void Purge();
		void PurgeShapeCache();
	}
#include "IfcRegisterGeomHeader.h"
}
#endif
