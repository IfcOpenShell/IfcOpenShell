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

#ifdef SCHEMA_HAS_IfcBSplineSurfaceWithKnots

bool IfcGeom::Kernel::convert(const IfcSchema::IfcBSplineSurfaceWithKnots* l, TopoDS_Shape& face) {
	boost::shared_ptr< aggregate_of_aggregate_of<IfcSchema::IfcCartesianPoint> > cps = l->ControlPointsList();
	std::vector<double> uknots = l->UKnots();
	std::vector<double> vknots = l->VKnots();
	std::vector<int> umults = l->UMultiplicities();
	std::vector<int> vmults = l->VMultiplicities();

	TColgp_Array2OfPnt Poles (0, (int)cps->size() - 1, 0, (int)(*cps->begin()).size() - 1);
	TColStd_Array1OfReal UKnots(0, (int)uknots.size() - 1);
	TColStd_Array1OfReal VKnots(0, (int)vknots.size() - 1);
	TColStd_Array1OfInteger UMults(0, (int)umults.size() - 1);
	TColStd_Array1OfInteger VMults(0, (int)vmults.size() - 1);
	Standard_Integer UDegree = l->UDegree();
	Standard_Integer VDegree = l->VDegree();

	int i = 0, j;
	for (aggregate_of_aggregate_of<IfcSchema::IfcCartesianPoint>::outer_it it = cps->begin(); it != cps->end(); ++it, ++i) {
		j = 0;
		for (aggregate_of_aggregate_of<IfcSchema::IfcCartesianPoint>::inner_it jt = (*it).begin(); jt != (*it).end(); ++jt, ++j) {
			IfcSchema::IfcCartesianPoint* p = *jt;
			gp_Pnt pnt;
			if (!convert(p, pnt)) return false;
			Poles(i, j) = pnt;
		}
	}
	i = 0;
	for (std::vector<double>::const_iterator it = uknots.begin(); it != uknots.end(); ++it, ++i) {
		UKnots(i) = *it;
	}
	i = 0;
	for (std::vector<double>::const_iterator it = vknots.begin(); it != vknots.end(); ++it, ++i) {
		VKnots(i) = *it;
	}
	i = 0;
	for (std::vector<int>::const_iterator it = umults.begin(); it != umults.end(); ++it, ++i) {
		UMults(i) = *it;
	}
	i = 0;
	for (std::vector<int>::const_iterator it = vmults.begin(); it != vmults.end(); ++it, ++i) {
		VMults(i) = *it;
	}
	Handle_Geom_Surface surf = new Geom_BSplineSurface(Poles, UKnots, VKnots, UMults, VMults, UDegree, VDegree);

#if OCC_VERSION_HEX < 0x60502
	face = BRepBuilderAPI_MakeFace(surf);
#else
	face = BRepBuilderAPI_MakeFace(surf, getValue(GV_PRECISION));
#endif

	return true;
}

#endif
