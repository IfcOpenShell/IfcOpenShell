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
#include <BRepFilletAPI_MakeFillet2d.hxx>

#define Kernel MAKE_TYPE_NAME(Kernel)
#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPlane* l, TopoDS_Shape& face) {
	gp_Pln pln;
	convert(l, pln);
	Handle_Geom_Surface surf = new Geom_Plane(pln);
#if OCC_VERSION_HEX < 0x60502
	face = BRepBuilderAPI_MakeFace(surf);
#else
	face = BRepBuilderAPI_MakeFace(surf, getValue(GV_PRECISION));
#endif
	return true;
}
bool IfcGeom::Kernel::convert(const IfcSchema::IfcPlane* pln, gp_Pln& plane) {
	IN_CACHE(IfcPlane,pln,gp_Pln,plane)
	IfcSchema::IfcAxis2Placement3D* l = pln->Position();
	gp_Pnt o;gp_Dir axis = gp_Dir(0,0,1);gp_Dir refDirection;

	if (!l->Location()->declaration().is("IfcCartesianPoint")) {
		// only applicable to 4x3 rc2
		Logger::Error("Not implemented", l->Location());
		return false;
	}

	IfcGeom::Kernel::convert((const IfcSchema::IfcCartesianPoint*) l->Location(),o);
	bool hasRef = !!l->RefDirection();
	if ( l->Axis() ) IfcGeom::Kernel::convert(l->Axis(),axis);
	if ( hasRef ) IfcGeom::Kernel::convert(l->RefDirection(),refDirection);
	gp_Ax3 ax3;
	if ( hasRef ) ax3 = gp_Ax3(o,axis,refDirection);
	else ax3 = gp_Ax3(o,axis);
	plane = gp_Pln(ax3);
	CACHE(IfcPlane,pln,plane)
	return true;
}
