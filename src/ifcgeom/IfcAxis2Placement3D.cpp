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

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Vec2d.hxx>
#include <gp_Dir2d.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Ax3.hxx>
#include <gp_Ax2d.hxx>
#include <gp_Pln.hxx>
#include <gp_Circ.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <Geom_TrimmedCurve.hxx>
#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>
#include <BRepFilletAPI_MakeFillet2d.hxx>
#include <TopLoc_Location.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcAxis2Placement3D* l, gp_Trsf& trsf) {
	IN_CACHE(IfcAxis2Placement3D, l, gp_Trsf, trsf)

	gp_Pnt o;
	gp_Dir axis(0, 0, 1);
	gp_Dir refDirection;

	if (!l->Location()->declaration().is("IfcCartesianPoint")) {
		// only applicable to 4x3 rc2
		Logger::Error("Not implemented", l->Location());
		return false;
	}

	IfcGeom::Kernel::convert((const IfcSchema::IfcCartesianPoint*) l->Location(), o);
	const bool hasAxis = !!l->Axis();
	const bool hasRef = !!l->RefDirection();

	if (hasAxis != hasRef) {
		Logger::Warning("Axis and RefDirection should be specified together", l);
	}

	if (hasAxis) {
		IfcGeom::Kernel::convert(l->Axis(), axis);
	}

	if (hasRef) {
		IfcGeom::Kernel::convert(l->RefDirection(), refDirection);
	} else {
		if (!axis.IsParallel(gp::DX(), 1.e-5)) {
			refDirection = gp::DX();
		} else {
			refDirection = gp::DZ();
		}
		gp_Vec Xvec = axis.Dot(refDirection) * axis;
		gp_Vec Xaxis = refDirection.XYZ() - Xvec.XYZ();
		refDirection = Xaxis;
	}

	gp_Ax3 ax3(o, axis, refDirection);

	if (!axis_equal(ax3, (gp_Ax3) gp::XOY(), getValue(GV_PRECISION))) {
		trsf.SetTransformation(ax3, gp::XOY());
	}
	
	CACHE(IfcAxis2Placement3D,l,trsf)
	return true;
}
