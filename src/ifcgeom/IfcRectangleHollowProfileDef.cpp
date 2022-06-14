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

#include <new>
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
#include <Geom_Plane.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <Geom_TrimmedCurve.hxx>
#include <Geom_OffsetCurve.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepOffsetAPI_MakeOffset.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <TopExp.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS_Iterator.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <ShapeFix_Edge.hxx>
#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>
#include <TopLoc_Location.hxx>
#include <BRepGProp_Face.hxx>
#include <Standard_Failure.hxx>
#include <BRep_Tool.hxx>
#include <BRepCheck_Face.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include <Standard_Version.hxx>
#include <TopTools_DataMapOfShapeInteger.hxx>
#include <TopTools_ListIteratorOfListOfShape.hxx>
#include <BRepLib_FindSurface.hxx>
#include <ShapeFix_Shape.hxx>
#include <ShapeExtend_DataMapIteratorOfDataMapOfShapeListOfMsg.hxx>
#include <Message_ListIteratorOfListOfMsg.hxx>
#include <ShapeExtend_MsgRegistrator.hxx>
#include <Message_Msg.hxx>
#include "../ifcgeom/IfcGeom.h"
#include <Geom_BSplineSurface.hxx>
#include <TColgp_Array2OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRectangleHollowProfileDef* l, TopoDS_Shape& face) {
	const double x = l->XDim() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double y = l->YDim() / 2.0f  * getValue(GV_LENGTH_UNIT);
	const double d = l->WallThickness() * getValue(GV_LENGTH_UNIT);

	const bool fr1 = !!l->OuterFilletRadius();
	const bool fr2 = !!l->InnerFilletRadius();

	const double r1 = fr1 ? (*l->OuterFilletRadius()) * getValue(GV_LENGTH_UNIT) : 0.;
	const double r2 = fr2 ? (*l->InnerFilletRadius()) * getValue(GV_LENGTH_UNIT) : 0.;
	
	if ( x < ALMOST_ZERO || y < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l);
		return false;
	}

	TopoDS_Face f1;
	TopoDS_Face f2;

	gp_Trsf2d trsf2d;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf2d);
	}

	double coords1[8] = {-x  ,-y,   x  ,-y,   x,  y,   -x,  y  };
	double coords2[8] = {-x+d,-y+d, x-d,-y+d, x-d,y-d, -x+d,y-d};
	double radii1[4] = {r1,r1,r1,r1};
	double radii2[4] = {r2,r2,r2,r2};
	int fillets[4] = {0,1,2,3};

	bool s1 = profile_helper(4,coords1,fr1 ? 4 : 0,fillets,radii1,trsf2d,f1);
	bool s2 = profile_helper(4,coords2,fr2 ? 4 : 0,fillets,radii2,trsf2d,f2);

	if (!s1 || !s2) return false;

	TopExp_Explorer exp1(f1, TopAbs_WIRE);
	TopExp_Explorer exp2(f2, TopAbs_WIRE);

	TopoDS_Wire w1 = TopoDS::Wire(exp1.Current());	
	TopoDS_Wire w2 = TopoDS::Wire(exp2.Current());

	BRepBuilderAPI_MakeFace mf(w1, false);
	mf.Add(w2);

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();
	face = TopoDS::Face(sfs.Shape());	
	return true;
}
