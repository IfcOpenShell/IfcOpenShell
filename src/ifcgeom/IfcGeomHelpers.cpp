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
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Mat.hxx>
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


namespace IfcGeom {
	namespace Cache {
#include "IfcRegisterCreateCache.h"
	}
}
#define IN_CACHE(T,E,t,e) std::map<int,t>::const_iterator it = Cache::T.find(E->entity->id());\
	if ( it != Cache::T.end() ) { e = it->second; return true; }
#define CACHE(T,E,e) Cache::T[E->entity->id()] = e;

bool IfcGeom::convert(const Ifc2x3::IfcCartesianPoint::ptr l, gp_Pnt& point) {
	IN_CACHE(IfcCartesianPoint,l,gp_Pnt,point)
	std::vector<float> xyz = l->Coordinates();
	point = gp_Pnt(
		xyz.size()     ? (xyz[0]*Ifc::LengthUnit) : 0.0f,
		xyz.size() > 1 ? (xyz[1]*Ifc::LengthUnit) : 0.0f,
		xyz.size() > 2 ? (xyz[2]*Ifc::LengthUnit) : 0.0f
	);
	CACHE(IfcCartesianPoint,l,point)
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcDirection::ptr l, gp_Dir& dir) {
	IN_CACHE(IfcDirection,l,gp_Dir,dir)
	std::vector<float> xyz = l->DirectionRatios();
	dir = gp_Dir(
		xyz.size()     ? xyz[0] : 0.0f,
		xyz.size() > 1 ? xyz[1] : 0.0f,
		xyz.size() > 2 ? xyz[2] : 0.0f
	);
	CACHE(IfcDirection,l,dir)
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcVector::ptr l, gp_Vec& v) {
	IN_CACHE(IfcVector,l,gp_Vec,v)
	gp_Dir d;
	IfcGeom::convert(l->Orientation(),d);
	v = l->Magnitude() * Ifc::LengthUnit * d;
	CACHE(IfcVector,l,v)
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcAxis2Placement3D::ptr l, gp_Trsf& trsf) {
	IN_CACHE(IfcAxis2Placement3D,l,gp_Trsf,trsf)
	gp_Pnt o;gp_Dir axis = gp_Dir(0,0,1);gp_Dir refDirection;
	IfcGeom::convert(l->Location(),o);
	bool hasRef = l->hasRefDirection();
	if ( l->hasAxis() ) IfcGeom::convert(l->Axis(),axis);
	if ( hasRef ) IfcGeom::convert(l->RefDirection(),refDirection);
	gp_Ax3 ax3;
	if ( hasRef ) ax3 = gp_Ax3(o,axis,refDirection);
	else ax3 = gp_Ax3(o,axis);
	trsf.SetTransformation(ax3, gp_Ax3(gp_Pnt(),gp_Dir(0,0,1),gp_Dir(1,0,0)));
	CACHE(IfcAxis2Placement3D,l,trsf)
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcCartesianTransformationOperator3D::ptr l, gp_Trsf& trsf) {
	IN_CACHE(IfcCartesianTransformationOperator3D,l,gp_Trsf,trsf)
	gp_Pnt origin;
	IfcGeom::convert(l->LocalOrigin(),origin);
	gp_Dir axis1 (1.,0.,0.);
	gp_Dir axis2 (0.,1.,0.);
	gp_Dir axis3;
	if ( l->hasAxis1() ) IfcGeom::convert(l->Axis1(),axis1);
	if ( l->hasAxis2() ) IfcGeom::convert(l->Axis2(),axis2);
	if ( l->hasAxis3() ) IfcGeom::convert(l->Axis3(),axis3);
	else axis3 = axis1.Crossed(axis2);
	const gp_Ax3 ax3 (origin,axis3,axis1);
	trsf.SetTransformation(ax3);
	trsf.Invert();
	if ( l->hasScale() ) trsf.SetScaleFactor(l->Scale());
	CACHE(IfcCartesianTransformationOperator3D,l,trsf)
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcCartesianTransformationOperator2D::ptr l, gp_Trsf2d& trsf) {
	IN_CACHE(IfcCartesianTransformationOperator2D,l,gp_Trsf2d,trsf)
	gp_Pnt origin;
	IfcGeom::convert(l->LocalOrigin(),origin);
	gp_Dir axis1 (1.,0.,0.);
	if ( l->hasAxis1() ) IfcGeom::convert(l->Axis1(),axis1);
	const gp_Ax2d ax2d (gp_Pnt2d(origin.X(),origin.Y()),gp_Dir2d(axis1.X(),axis1.Y()));
	trsf.SetTransformation(ax2d);
	trsf.Invert();
	if ( l->hasScale() ) trsf.SetScaleFactor(l->Scale());
	CACHE(IfcCartesianTransformationOperator2D,l,trsf)
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcPlane::ptr pln, gp_Pln& plane) {
	IN_CACHE(IfcPlane,pln,gp_Pln,plane)
	Ifc2x3::IfcAxis2Placement3D::ptr l = pln->Position();
	gp_Pnt o;gp_Dir axis = gp_Dir(0,0,1);gp_Dir refDirection;
	IfcGeom::convert(l->Location(),o);
	bool hasRef = l->hasRefDirection();
	if ( l->hasAxis() ) IfcGeom::convert(l->Axis(),axis);
	if ( hasRef ) IfcGeom::convert(l->RefDirection(),refDirection);
	gp_Ax3 ax3;
	if ( hasRef ) ax3 = gp_Ax3(o,axis,refDirection);
	else ax3 = gp_Ax3(o,axis);
	plane = gp_Pln(ax3);
	CACHE(IfcPlane,pln,plane)
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcAxis2Placement2D::ptr l, gp_Trsf2d& trsf) {
	IN_CACHE(IfcAxis2Placement2D,l,gp_Trsf2d,trsf)
	gp_Pnt P; gp_Dir V (1,0,0);
	IfcGeom::convert(l->Location(),P);
	if ( l->hasRefDirection() )
		IfcGeom::convert(l->RefDirection(),V);

	gp_Ax2d axis(gp_Pnt2d(P.X(),P.Y()),gp_Dir2d(V.X(),V.Y()));
	trsf.SetTransformation(axis,gp_Ax2d());
	CACHE(IfcAxis2Placement2D,l,trsf)
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcObjectPlacement::ptr l, gp_Trsf& trsf) {
	IN_CACHE(IfcObjectPlacement,l,gp_Trsf,trsf)
	if ( ! l->is(Ifc2x3::Type::IfcLocalPlacement) ) return false;
	Ifc2x3::IfcLocalPlacement::ptr current = reinterpret_pointer_cast<Ifc2x3::IfcObjectPlacement,Ifc2x3::IfcLocalPlacement>(l);
	while (1) {
		gp_Trsf trsf2;
		Ifc2x3::IfcAxis2Placement relplacement = current->RelativePlacement();
		if ( relplacement->is(Ifc2x3::Type::IfcAxis2Placement3D) ) {
			IfcGeom::convert((Ifc2x3::IfcAxis2Placement3D*)relplacement,trsf2);
			trsf.PreMultiply(trsf2);
		}
		if ( current->hasPlacementRelTo() ) {
			Ifc2x3::IfcObjectPlacement::ptr relto = current->PlacementRelTo();
			if ( relto->is(Ifc2x3::Type::IfcLocalPlacement) )
				current = reinterpret_pointer_cast<Ifc2x3::IfcObjectPlacement,Ifc2x3::IfcLocalPlacement>(current->PlacementRelTo());
			else break;			
		} else break;
	}
	CACHE(IfcObjectPlacement,l,trsf)
	return true;
}
void IfcGeom::Cache::Purge() {
#include "IfcRegisterPurgeCache.h"
	IfcGeom::Cache::PurgeShapeCache();
}