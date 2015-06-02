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

/********************************************************************************
 *                                                                              *
 * Implementations of the various conversion functions defined in IfcRegister.h *
 *                                                                              *
 ********************************************************************************/

#include <algorithm>

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

#ifdef USE_IFC4
#include <Geom_BSplineCurve.hxx>
#endif

#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCircle* l, Handle(Geom_Curve)& curve) {
	const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
	if ( r < ALMOST_ZERO ) { 
		Logger::Message(Logger::LOG_ERROR, "Radius not greater than zero for:", l->entity);
		return false;
	}
	gp_Trsf trsf;
	IfcSchema::IfcAxis2Placement* placement = l->Position();
	if (placement->is(IfcSchema::Type::IfcAxis2Placement3D)) {
		IfcGeom::Kernel::convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
	} else {
		gp_Trsf2d trsf2d;
		IfcGeom::Kernel::convert((IfcSchema::IfcAxis2Placement2D*)placement,trsf2d);
		trsf = trsf2d;
	}
	gp_Ax2 ax = gp_Ax2().Transformed(trsf);
	curve = new Geom_Circle(ax, r);
	return true;
}
bool IfcGeom::Kernel::convert(const IfcSchema::IfcEllipse* l, Handle(Geom_Curve)& curve) {
	double x = l->SemiAxis1() * getValue(GV_LENGTH_UNIT);
	double y = l->SemiAxis2() * getValue(GV_LENGTH_UNIT);
	if (x < ALMOST_ZERO || y < ALMOST_ZERO) { 
		Logger::Message(Logger::LOG_ERROR, "Radius not greater than zero for:", l->entity);
		return false;
	}
	// Open Cascade does not allow ellipses of which the minor radius
	// is greater than the major radius. Hence, in this case, the
	// ellipse is rotated. Note that special care needs to be taken
	// when creating a trimmed curve off of an ellipse like this.
	const bool rotated = y > x;
	gp_Trsf trsf;
	IfcSchema::IfcAxis2Placement* placement = l->Position();
	if (placement->is(IfcSchema::Type::IfcAxis2Placement3D)) {
		convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
	} else {
		gp_Trsf2d trsf2d;
		convert((IfcSchema::IfcAxis2Placement2D*)placement,trsf2d);
		trsf = trsf2d;
	}
	gp_Ax2 ax = gp_Ax2();
	if (rotated) {
		ax.Rotate(ax.Axis(), M_PI / 2.);
		std::swap(x, y);
	}
	ax.Transform(trsf);
	curve = new Geom_Ellipse(ax, x, y);
	return true;
}
bool IfcGeom::Kernel::convert(const IfcSchema::IfcLine* l, Handle(Geom_Curve)& curve) {
	gp_Pnt pnt;gp_Vec vec;
	convert(l->Pnt(),pnt);
	convert(l->Dir(),vec);	
	// See note at IfcGeomWires.cpp:237
	curve = new Geom_Line(pnt,vec);
	return true;
}

#ifdef USE_IFC4
bool IfcGeom::Kernel::convert(const IfcSchema::IfcBSplineCurveWithKnots* l, Handle(Geom_Curve)& curve) {

	const IfcSchema::IfcCartesianPoint::list::ptr cps = l->ControlPointsList();
	const std::vector<int> mults = l->KnotMultiplicities();
	const std::vector<double> knots = l->Knots();

	TColgp_Array1OfPnt      Poles(0,  cps->size() - 1);
	TColStd_Array1OfReal    Knots(0, knots.size() - 1);
	TColStd_Array1OfInteger Mults(0, mults.size() - 1);
	Standard_Integer        Degree = l->Degree();
	Standard_Boolean        Periodic = l->ClosedCurve();

	int i = 0;
	for (IfcSchema::IfcCartesianPoint::list::it it = cps->begin(); it != cps->end(); ++it, ++i) {
		gp_Pnt pnt;
		if (!convert(*it, pnt)) return false;
		Poles(i) = pnt;
	}
	
	i = 0;
	for (std::vector<int>::const_iterator it = mults.begin(); it != mults.end(); ++it, ++i) {
		Mults(i) = *it;
	}

	i = 0;
	for (std::vector<double>::const_iterator it = knots.begin(); it != knots.end(); ++it, ++i) {
		Knots(i) = *it;
	}
	
	curve = new Geom_BSplineCurve(Poles, Knots, Mults, Degree, Periodic);
	return true;
}
#endif