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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcIShapeProfileDef* l, TopoDS_Shape& face) {
	const double x1 = l->OverallWidth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double y = l->OverallDepth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d1 = l->WebThickness() / 2.0f  * getValue(GV_LENGTH_UNIT);
	const double dy1 = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);

	bool doFillet1 = !!l->FilletRadius();
	double f1 = 0.;
	if ( doFillet1 ) {
		f1 = *l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}

	bool doFillet2 = doFillet1;
	double x2 = x1, dy2 = dy1, f2 = f1;

	// @todo in IFC4 a IfcAsymmetricIShapeProfileDef is not a subtype anymore of IfcIShapeProfileDef!
	if (l->declaration().is(IfcSchema::IfcAsymmetricIShapeProfileDef::Class())) {
		IfcSchema::IfcAsymmetricIShapeProfileDef* assym = (IfcSchema::IfcAsymmetricIShapeProfileDef*) l;
		x2 = assym->TopFlangeWidth() / 2. * getValue(GV_LENGTH_UNIT);
		doFillet2 = !!assym->TopFlangeFilletRadius();
		if (doFillet2) {
			f2 = *assym->TopFlangeFilletRadius() * getValue(GV_LENGTH_UNIT);
		}
		if (assym->TopFlangeThickness()) {
			dy2 = *assym->TopFlangeThickness() * getValue(GV_LENGTH_UNIT);
		}
	}	

	if ( x1 < ALMOST_ZERO || x2 < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || dy1 < ALMOST_ZERO || dy2 < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l);
		return false;
	}

	gp_Trsf2d trsf2d;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf2d);
	}

	double coords[24] = {-x1,-y, x1,-y, x1,-y+dy1, d1,-y+dy1, d1,y-dy2, x2,y-dy2, x2,y, -x2,y, -x2,y-dy2, -d1,y-dy2, -d1,-y+dy1, -x1,-y+dy1};
	int fillets[4] = {3,4,9,10};
	double radii[4] = {f1,f2,f2,f1};
	return profile_helper(12,coords,(doFillet1||doFillet2) ? 4 : 0,fillets,radii,trsf2d,face);
}
