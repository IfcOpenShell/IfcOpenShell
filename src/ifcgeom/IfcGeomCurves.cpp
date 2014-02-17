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

bool IfcGeom::convert(const IfcSchema::IfcCircle::ptr l, Handle(Geom_Curve)& curve) {
	const double r = l->Radius() * IfcGeom::GetValue(GV_LENGTH_UNIT);
	if ( r <= 0.0f ) { return false; }
	gp_Trsf trsf;
	IfcSchema::IfcAxis2Placement placement = l->Position();
	if (placement->is(IfcSchema::Type::IfcAxis2Placement3D)) {
		IfcGeom::convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
	} else {
		gp_Trsf2d trsf2d;
		IfcGeom::convert((IfcAxis2Placement2D*)placement,trsf2d);
		trsf = trsf2d;
	}
	gp_Ax2 ax = gp_Ax2().Transformed(trsf);
	curve = new Geom_Circle(ax, r);
	return true;
}
bool IfcGeom::convert(const IfcSchema::IfcEllipse::ptr l, Handle(Geom_Curve)& curve) {
	double x = l->SemiAxis1() * IfcGeom::GetValue(GV_LENGTH_UNIT);
	double y = l->SemiAxis2() * IfcGeom::GetValue(GV_LENGTH_UNIT);
	if ( x == 0.0f || y == 0.0f || y > x ) { return false; }
	gp_Trsf trsf;
	IfcSchema::IfcAxis2Placement placement = l->Position();
	if (placement->is(IfcSchema::Type::IfcAxis2Placement3D)) {
		IfcGeom::convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
	} else {
		gp_Trsf2d trsf2d;
		IfcGeom::convert((IfcSchema::IfcAxis2Placement2D*)placement,trsf2d);
		trsf = trsf2d;
	}
	gp_Ax2 ax = gp_Ax2().Transformed(trsf);
	curve = new Geom_Ellipse(ax, x, y);
	return true;
}
bool IfcGeom::convert(const IfcSchema::IfcLine::ptr l, Handle(Geom_Curve)& curve) {
	gp_Pnt pnt;gp_Vec vec;
	IfcGeom::convert(l->Pnt(),pnt);
	IfcGeom::convert(l->Dir(),vec);	
	// See note at IfcGeomWires.cpp:237
	curve = new Geom_Line(pnt,vec);
	return true;
}