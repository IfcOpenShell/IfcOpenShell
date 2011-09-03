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

#include <new>

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

bool IfcGeom::convert(const Ifc2x3::IfcFace::ptr l, TopoDS_Face& face) {
	Ifc2x3::IfcFaceBound::list bounds = l->Bounds();
	Ifc2x3::IfcFaceBound::it it = bounds->begin();
	Ifc2x3::IfcLoop::ptr loop = (*it)->Bound();
	TopoDS_Wire wire;
	if ( ! IfcGeom::convert_wire(loop,wire) ) return false;
	BRepBuilderAPI_MakeFace mf (wire);
	BRepBuilderAPI_FaceError er = mf.Error();
	if ( er == BRepBuilderAPI_NotPlanar ) {
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire, 0.01, TopAbs_WIRE);
		mf.~BRepBuilderAPI_MakeFace();
		new (&mf) BRepBuilderAPI_MakeFace(wire);
		er = mf.Error();
	}
	if ( er != BRepBuilderAPI_FaceDone ) return false;
	if ( bounds->Size() == 1 ) {
		face = mf.Face();
		return true;
	}
	for( ++it; it != bounds->end(); ++ it) {
		Ifc2x3::IfcLoop::ptr loop = (*it)->Bound();
		TopoDS_Wire wire;
		if ( ! IfcGeom::convert_wire(loop,wire) ) return false;
		mf.Add(wire);
	}
	if ( mf.IsDone() ) {
		ShapeFix_Shape sfs(mf.Face());
		sfs.Perform();
		face = TopoDS::Face(sfs.Shape());
		return true;
	} else {
		return false;
	}
}
bool IfcGeom::convert(const Ifc2x3::IfcArbitraryClosedProfileDef::ptr l, TopoDS_Face& face) {
	TopoDS_Wire wire;
	if ( ! IfcGeom::convert_wire(l->OuterCurve(),wire) ) return false;
	return IfcGeom::convert_wire_to_face(wire,face);
}
bool IfcGeom::convert(const Ifc2x3::IfcArbitraryProfileDefWithVoids::ptr l, TopoDS_Face& face) {
	TopoDS_Wire profile;
	if ( ! IfcGeom::convert_wire(l->OuterCurve(),profile) ) return false;
	BRepBuilderAPI_MakeFace mf(profile);
	Ifc2x3::IfcCurve::list voids = l->InnerCurves();
	for( Ifc2x3::IfcCurve::it it = voids->begin(); it != voids->end(); ++ it ) {
		TopoDS_Wire hole;
		if ( IfcGeom::convert_wire(*it,hole) ) {
			mf.Add(hole);
		}
	}
	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();
	face = TopoDS::Face(sfs.Shape());
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcRectangleProfileDef::ptr l, TopoDS_Face& face) {
	const float x = l->XDim() / 2.0f * Ifc::LengthUnit;
	const float y = l->YDim() / 2.0f  * Ifc::LengthUnit;

	if ( x == 0.0f || y == 0.0f ) {
		Ifc::LogMessage("Notice","Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::convert(l->Position(),trsf2d);
	float coords[8] = {-x,-y,x,-y,x,y,-x,y};
	return IfcGeom::profile_helper(4,coords,0,0,0,trsf2d,face);
}
bool IfcGeom::convert(const Ifc2x3::IfcIShapeProfileDef::ptr l, TopoDS_Face& face) {
	const float x = l->OverallWidth() / 2.0f * Ifc::LengthUnit;
	const float y = l->OverallDepth() / 2.0f * Ifc::LengthUnit;
	const float d1 = l->WebThickness() / 2.0f  * Ifc::LengthUnit;
	const float d2 = l->FlangeThickness() * Ifc::LengthUnit;
	bool doFillet = l->hasFilletRadius();
	float f;
	if ( doFillet ) {
		f = l->FilletRadius() * Ifc::LengthUnit;
	}

	if ( x == 0.0f || y == 0.0f || d1 == 0.0f || d2 == 0.0f ) {
		Ifc::LogMessage("Notice","Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::convert(l->Position(),trsf2d);

	float coords[24] = {-x,-y,x,-y,x,-y+d2,d1,-y+d2,d1,y-d2,x,y-d2,x,y,-x,y,-x,y-d2,-d1,y-d2,-d1,-y+d2,-x,-y+d2};
	int fillets[4] = {3,4,9,10};
	float radii[4] = {f,f,f,f};
	return IfcGeom::profile_helper(12,coords,doFillet ? 4 : 0,fillets,radii,trsf2d,face);
}
bool IfcGeom::convert(const Ifc2x3::IfcCShapeProfileDef::ptr l, TopoDS_Face& face) {
	const float x = l->Depth() / 2.0f * Ifc::LengthUnit;
	const float y = l->Width() / 2.0f * Ifc::LengthUnit;
	const float d1 = l->WallThickness() * Ifc::LengthUnit;
	const float d2 = l->Girth() * Ifc::LengthUnit;
	bool doFillet = l->hasInternalFilletRadius();
	float f1,f2;
	if ( doFillet ) {
		f1 = l->InternalFilletRadius() * Ifc::LengthUnit;
		f2 = f1 + d1;
	}

	if ( x == 0.0f || y == 0.0f || d1 == 0.0f || d2 == 0.0f ) {
		Ifc::LogMessage("Notice","Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::convert(l->Position(),trsf2d);

	float coords[24] = {-x,-y,x,-y,x,-y+d2,x-d1,-y+d2,x-d1,-y+d1,-x+d1,-y+d1,-x+d1,y-d1,x-d1,y-d1,x-d1,y-d2,x,y-d2,x,y,-x,y};
	int fillets[8] = {0,1,4,5,6,7,10,11};
	float radii[8] = {f2,f2,f1,f1,f1,f1,f2,f2};
	return IfcGeom::profile_helper(12,coords,doFillet ? 8 : 0,fillets,radii,trsf2d,face);
}
bool IfcGeom::convert(const Ifc2x3::IfcLShapeProfileDef::ptr l, TopoDS_Face& face) {
	const float y = l->Depth() / 2.0f * Ifc::LengthUnit;
	const float x = l->Width() / 2.0f * Ifc::LengthUnit;
	const float d = l->Thickness() * Ifc::LengthUnit;
	bool doEdgeFillet = l->hasEdgeRadius();
	bool doFillet = l->hasFilletRadius();
	float f1 = 0.0f;
	float f2 = 0.0f;
	if (doFillet) {
		f1 = l->FilletRadius() * Ifc::LengthUnit;
	}
	if ( doEdgeFillet) {
		f2 = l->EdgeRadius() * Ifc::LengthUnit;
	}
	if ( x == 0.0f || y == 0.0f || d == 0.0f ) {
		Ifc::LogMessage("Notice","Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::convert(l->Position(),trsf2d);

	float coords[12] = {-x,-y,x,-y,x,-y+d,-x+d,-y+d,-x+d,y,-x,y};
	int fillets[3] = {2,3,4};
	float radii[3] = {f2,f1,f2};
	return IfcGeom::profile_helper(6,coords,doFillet ? 3 : 0,fillets,radii,trsf2d,face);
}
bool IfcGeom::convert(const Ifc2x3::IfcCircleProfileDef::ptr l, TopoDS_Face& face) {
	const float r = l->Radius() * Ifc::LengthUnit;
	if ( r == 0.0f ) {
		Ifc::LogMessage("Notice","Skipping zero sized profile:",l->entity);
		return false;
	}
	
	gp_Trsf2d trsf;	
	IfcGeom::convert(l->Position(),trsf);

	BRepBuilderAPI_MakeWire w;
	gp_Ax2 ax = gp_Ax2().Transformed(trsf);
	Handle(Geom_Circle) circle = new Geom_Circle(ax, r);
	TopoDS_Edge edge = BRepBuilderAPI_MakeEdge(circle);
	w.Add(edge);
	return IfcGeom::convert_wire_to_face(w,face);
}
bool IfcGeom::convert(const Ifc2x3::IfcCircleHollowProfileDef::ptr l, TopoDS_Face& face) {
	const float r = l->Radius() * Ifc::LengthUnit;
	const float t = l->WallThickness() * Ifc::LengthUnit;
	
	if ( r == 0.0f || t == 0.0f ) {
		Ifc::LogMessage("Notice","Skipping zero sized profile:",l->entity);
		return false;
	}
	
	gp_Trsf2d trsf;	
	IfcGeom::convert(l->Position(),trsf);
	gp_Ax2 ax = gp_Ax2().Transformed(trsf);

	BRepBuilderAPI_MakeWire outer;	
	Handle(Geom_Circle) outerCircle = new Geom_Circle(ax, r);
	outer.Add(BRepBuilderAPI_MakeEdge(outerCircle));
	BRepBuilderAPI_MakeFace mf(outer.Wire(), false);

	BRepBuilderAPI_MakeWire inner;	
	Handle(Geom_Circle) innerCirlce = new Geom_Circle(ax, r-t);
	inner.Add(BRepBuilderAPI_MakeEdge(innerCirlce));
	mf.Add(inner);

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();
	face = TopoDS::Face(sfs.Shape());	
	return true;		
}