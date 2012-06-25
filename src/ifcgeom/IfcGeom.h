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

namespace IfcGeom {

	// Tolerances and settings for various geometrical operations:
	enum GeomValue {
		// Specifies the deflection of the mesher
		GV_DEFLECTION_TOLERANCE, 
		// Specifies the tolerance of the wire builder, most notably for trimmed curves
		GV_WIRE_CREATION_TOLERANCE,
		// Specifies the minimal area of a face to be included in an IfcConnectedFaceset
		GV_MINIMAL_FACE_AREA,
		// Specifies the treshold distance under which cartesian points are deemed equal
		GV_POINT_EQUALITY_TOLERANCE,
		// Specifies maximum number of faces for a shell to be sewed. Sewing shells
		// that consist of many faces is really detrimental for the performance.
		GV_MAX_FACES_TO_SEW
	};

	bool convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face);
	bool convert_shapes(const IfcUtil::IfcBaseClass* L, ShapeList& result);
	bool is_shape_collection(const IfcUtil::IfcBaseClass* L);
	const TopoDS_Shape* convert_shape(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
	bool convert_wire(const IfcUtil::IfcBaseClass* L, TopoDS_Wire& result);
	bool convert_curve(const IfcUtil::IfcBaseClass* L, Handle(Geom_Curve)& result);
	bool convert_face(const IfcUtil::IfcBaseClass* L, TopoDS_Face& result);
	bool convert_openings(const Ifc2x3::IfcProduct::ptr entity, const Ifc2x3::IfcRelVoidsElement::list& openings, const ShapeList& entity_shapes, const gp_Trsf& entity_trsf, ShapeList& cut_shapes);
	bool convert_openings_fast(const Ifc2x3::IfcProduct::ptr entity, const Ifc2x3::IfcRelVoidsElement::list& openings, const ShapeList& entity_shapes, const gp_Trsf& entity_trsf, ShapeList& cut_shapes);
	bool create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& solid);
	bool is_compound(const TopoDS_Shape& shape);
	bool is_convex(const TopoDS_Wire& wire);
	TopoDS_Shape halfspace_from_plane(const gp_Pln& pln,const gp_Pnt& cent);
	gp_Pln plane_from_face(const TopoDS_Face& face);
	gp_Pnt point_above_plane(const gp_Pln& pln, bool agree=true);
	const TopoDS_Shape& ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid);
	bool profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Face& face); 
	double shape_volume(const TopoDS_Shape& s);
	double face_area(const TopoDS_Face& f);
	void SetValue(GeomValue var, double value);
	double GetValue(GeomValue var);

	namespace Cache {
		void Purge();
		void PurgeShapeCache();
	}
#include "IfcRegisterGeomHeader.h"
}
#endif
