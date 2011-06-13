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
 * Implementations of the various conversion functions required by IfcSchema.h. *
 * The functions are prototyped in IfcTypes.h. Functions that convert a         *
 * TopoDS_Shape or TopoDS_Wire are called from IfcGeom::convert_shape and       *
 * IfcGeom::convert_wire respectively                                           *
 *                                                                              *
 ********************************************************************************/

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcTypes.h"

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Vec2d.hxx>
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

#include <TopLoc_Location.hxx>

bool IfcGeom::convert(IfcSchema::ExtrudedAreaSolid* IfcExtrudedAreaSolid, TopoDS_Shape& shape) {
	TopoDS_Face face;
	if ( ! IfcGeom::convert_face(IfcExtrudedAreaSolid->Profile(),face) ) return false;
	const float height = IfcExtrudedAreaSolid->Height() * Ifc::LengthUnit;
	gp_Trsf trsf;
	convert((IfcSchema::Axis2Placement3D*) IfcExtrudedAreaSolid->Placement().get(),trsf);

	gp_Vec dir3;
	convert((IfcSchema::Direction*) IfcExtrudedAreaSolid->Dir().get(),dir3);

	gp_Vec extrude = dir3.Scaled(height);
	
	shape = BRepPrimAPI_MakePrism(face,extrude);
	shape.Move(trsf);
	return ! shape.IsNull();
}
bool IfcGeom::convert(IfcSchema::FacetedBrep* IfcFacetedBrep, TopoDS_Shape& shape) {
	return IfcGeom::convert_shape(IfcFacetedBrep->Shell(),shape);
}
bool IfcGeom::convert(IfcSchema::FaceBasedSurfaceModel* IfcFaceBasedSurfaceModel, TopoDS_Shape& shape) {
	return IfcGeom::convert((IfcSchema::ShellBasedSurfaceModel*) IfcFaceBasedSurfaceModel,shape);
}
bool IfcGeom::convert(IfcSchema::HalfSpaceSolid* IfcHalfSpaceSolid, TopoDS_Shape& shape) {
	IfcEntity surf = IfcHalfSpaceSolid->Surface();
	if ( surf->dt != IfcSchema::Enum::IfcPlane ) return false;
	IfcSchema::Plane* IfcPlane = (IfcSchema::Plane*)surf.get();
	gp_Pln pln;
	IfcGeom::convert(IfcPlane,pln);
	gp_Pnt pnt = pln.Location();
	if ( !IfcHalfSpaceSolid->Flag() != (IfcHalfSpaceSolid->dt == IfcSchema::Enum::IfcPolygonalBoundedHalfSpace) ) pnt.Translate(pln.Axis().Direction());
	else pnt.Translate(-pln.Axis().Direction());
	shape = BRepPrimAPI_MakeHalfSpace(BRepBuilderAPI_MakeFace(pln),pnt).Solid();
	return true;
}
bool IfcGeom::convert(IfcSchema::PolygonalBoundedHalfSpace* IfcPolygonalBoundedHalfSpace, TopoDS_Shape& shape) {
	TopoDS_Shape halfspace;
	if ( ! IfcGeom::convert((IfcSchema::HalfSpaceSolid*)IfcPolygonalBoundedHalfSpace,halfspace) ) return false;	
	TopoDS_Wire wire;
	if ( ! IfcGeom::convert_wire(IfcPolygonalBoundedHalfSpace->Boundary(),wire) ) return false;	
	gp_Trsf trsf;
	convert((IfcSchema::Axis2Placement3D*) IfcPolygonalBoundedHalfSpace->Placement().get(),trsf);
	TopoDS_Shape extrusion = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire),gp_Vec(0,0,20000.0));
	gp_Trsf down; down.SetTranslation(gp_Vec(0,0,-10000.0));
	extrusion.Move(down);
	extrusion.Move(trsf);
	shape = BRepAlgoAPI_Cut(extrusion,halfspace);
	return true;
}
bool IfcGeom::convert(IfcSchema::ShellBasedSurfaceModel* IfcShellBasedSurfaceModel, TopoDS_Shape& shape) {
	IfcEntities shells = IfcShellBasedSurfaceModel->Shells();
	BRep_Builder builder;
	TopoDS_Compound c;
	builder.MakeCompound(c);
	for( IfcParse::Entities::it it = shells->begin(); it != shells->end(); ++ it ) {
		TopoDS_Shape s;
		if ( IfcGeom::convert_shape(*it,s) ) {
			builder.Add(c,s);
		}
	}
	shape = c;
	return true;
}
bool IfcGeom::convert(IfcSchema::BooleanClippingResult* IfcBooleanClippingResult, TopoDS_Shape& shape) {
	TopoDS_Shape s1, s2;
	bool res1 = IfcGeom::convert_shape(IfcBooleanClippingResult->First(),s1);
	if ( ! res1 ) return false;
	bool res2 = IfcGeom::convert_shape(IfcBooleanClippingResult->Second(),s2);
	if ( res2 )
		shape = BRepAlgoAPI_Cut(s1,s2);
	return true;
}
bool IfcGeom::convert(IfcSchema::ClosedShell* IfcClosedShell, TopoDS_Shape& shape) {
	if ( ! IfcGeom::convert((IfcSchema::OpenShell*) IfcClosedShell,shape) ) return false;
	try {
		ShapeFix_Solid solid;
		solid.LimitTolerance(0.01);
		shape = solid.SolidFromShell(TopoDS::Shell(shape));
	} catch(...) {}
	return true;
}
bool IfcGeom::convert(IfcSchema::ConnectedFaceSet* IfcConnectedFaceSet, TopoDS_Shape& shape) {
	return IfcGeom::convert((IfcSchema::ClosedShell*) IfcConnectedFaceSet,shape);
}
bool IfcGeom::convert(IfcSchema::OpenShell* IfcOpenShell, TopoDS_Shape& shape) {
	BRepOffsetAPI_Sewing builder;
	builder.SetTolerance(0.01);
	IfcEntities faces = IfcOpenShell->Faces();
	bool facesAdded = false;
	for( IfcParse::Entities::it it = faces->begin(); it != faces->end(); ++ it ) {
		TopoDS_Face face;
		if ( IfcGeom::convert((IfcSchema::Face*) (*it).get(),face) ) {
			builder.Add(face);
			facesAdded = true;
		} else {
			std::cout << "[Warning] Invalid face:" << std::endl << (*it).get()->toString() << std::endl;
		}
	}
	if ( ! facesAdded ) return false;
	builder.Perform();
	shape = builder.SewedShape();
	return true;
}
bool IfcGeom::convert(IfcSchema::Face* IfcFace, TopoDS_Face& face) {
	IfcEntities bounds = IfcFace->Bounds();
	IfcParse::Entities::it it = bounds->begin();
	IfcSchema::FaceBound* bound = (IfcSchema::FaceBound*)(*it).get();

	IfcEntity loop = bound->Loop();
	TopoDS_Wire wire;
	if ( ! IfcGeom::convert_wire(loop,wire) ) return false;
	BRepBuilderAPI_MakeFace mf(wire, false);
	BRepBuilderAPI_FaceError er = mf.Error();
	if ( er == BRepBuilderAPI_NotPlanar ) {
		std::cout << "[Notice] Trying to fix non-planar face:" << std::endl << IfcFace->toString() << std::endl;
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire, 0.01, TopAbs_WIRE);
		mf = BRepBuilderAPI_MakeFace(wire, false);
		er = mf.Error();
	}
	if ( er != BRepBuilderAPI_FaceDone ) return false;

	if ( bounds->size == 1 ) {
		face = mf.Face();
		return true;
	}

	for( ++ it; it != bounds->end(); ++ it ) {
		IfcSchema::FaceBound* bound = (IfcSchema::FaceBound*)(*it).get();
		IfcEntity loop = bound->Loop();
		TopoDS_Wire hole;
		IfcGeom::convert_wire(loop,hole);
		mf.Add(hole);
	}

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();
	face = TopoDS::Face(sfs.Shape());
	return true;		
}
bool IfcGeom::convert(IfcSchema::CircleHollowProfileDef* IfcCircleHollowProfileDef, TopoDS_Face& face) {
	const float r = IfcCircleHollowProfileDef->Radius() * Ifc::LengthUnit;
	const float t = IfcCircleHollowProfileDef->WallThickness() * Ifc::LengthUnit;
	
	if ( r == 0.0f || t == 0.0f ) {
		std::cout << "[Notice] Skipping zero sized profile:" << std::endl << IfcCircleHollowProfileDef->toString() << std::endl;
		return false;
	}
	
	gp_Trsf2d trsf;	
	IfcGeom::convert((IfcSchema::Axis2Placement2D*)IfcCircleHollowProfileDef->Placement().get(),trsf);
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
bool IfcGeom::convert(IfcSchema::CartesianPoint* IfcCartesianPoint, gp_Pnt& p) {
	if ( IfcCartesianPoint->arg(0)->count() == 3 )
		p = gp_Pnt(IfcCartesianPoint->X() * Ifc::LengthUnit,IfcCartesianPoint->Y() * Ifc::LengthUnit,IfcCartesianPoint->Z() * Ifc::LengthUnit);
	else
		p = gp_Pnt(IfcCartesianPoint->X() * Ifc::LengthUnit,IfcCartesianPoint->Y() * Ifc::LengthUnit,0.0f);
	return true;
}
bool IfcGeom::convert(IfcSchema::Direction* IfcDirection, gp_Vec& v) {
	if ( IfcDirection->arg(0)->count() == 3 )
		v = gp_Vec(IfcDirection->X(),IfcDirection->Y(),IfcDirection->Z());
	else
		v = gp_Vec(IfcDirection->X(),IfcDirection->Y(),0.0f);
	return true;
}
bool IfcGeom::convert(IfcSchema::ArbitraryClosedProfileDef* IfcArbitraryClosedProfileDef, TopoDS_Wire& wire) {
	return IfcGeom::convert_wire(IfcArbitraryClosedProfileDef->Polyline(),wire);
}
bool IfcGeom::convert(IfcSchema::ArbitraryProfileDefWithVoids* IfcArbitraryProfileDefWithVoids, TopoDS_Face& face) {
	TopoDS_Wire profile;
	if ( ! IfcGeom::convert_wire(IfcArbitraryProfileDefWithVoids->Polyline(),profile) ) return false;
	BRepBuilderAPI_MakeFace mf(profile, false);
	IfcEntities voids = IfcArbitraryProfileDefWithVoids->Voids();
	for( IfcParse::Entities::it it = voids->begin(); it != voids->end(); ++ it ) {
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
bool IfcGeom::convert(IfcSchema::RectangleProfileDef* IfcRectangleProfileDef,class TopoDS_Wire& wire) {
	const float x = IfcRectangleProfileDef->Width() / 2.0f * Ifc::LengthUnit;
	const float y = IfcRectangleProfileDef->Height() / 2.0f  * Ifc::LengthUnit;

	if ( x == 0.0f || y == 0.0f ) {
		std::cout << "[Notice] Skipping zero sized profile:" << std::endl << IfcRectangleProfileDef->toString() << std::endl;
		return false;
	}

	gp_Trsf2d trsf;
	IfcGeom::convert((IfcSchema::Axis2Placement2D*)IfcRectangleProfileDef->Placement().get(),trsf);
	
	gp_XY p1 (-x,-y);trsf.Transforms(p1);gp_Pnt P1(p1.X(),p1.Y(),0.0f);
	gp_XY p2 ( x,-y);trsf.Transforms(p2);gp_Pnt P2(p2.X(),p2.Y(),0.0f);
	gp_XY p3 ( x, y);trsf.Transforms(p3);gp_Pnt P3(p3.X(),p3.Y(),0.0f);
	gp_XY p4 (-x, y);trsf.Transforms(p4);gp_Pnt P4(p4.X(),p4.Y(),0.0f);
	
	BRepBuilderAPI_MakeWire w;
	w.Add(BRepBuilderAPI_MakeEdge(P1,P2));
	w.Add(BRepBuilderAPI_MakeEdge(P2,P3));
	w.Add(BRepBuilderAPI_MakeEdge(P3,P4));
	w.Add(BRepBuilderAPI_MakeEdge(P4,P1));
	wire = w.Wire();
	return true;
}
bool IfcGeom::convert(IfcSchema::CircleProfileDef* IfcCircleProfileDef,class TopoDS_Wire& wire) {
	const float r = IfcCircleProfileDef->Radius() * Ifc::LengthUnit;
	
	if ( r == 0.0f ) {
		std::cout << "[Notice] Skipping zero sized profile:" << std::endl << IfcCircleProfileDef->toString() << std::endl;
		return false;
	}
	
	gp_Trsf2d trsf;	
	IfcGeom::convert((IfcSchema::Axis2Placement2D*)IfcCircleProfileDef->Placement().get(),trsf);

	BRepBuilderAPI_MakeWire w;

#ifdef SEGMENTED_CIRCLE
	TopoDS_Vertex previous,current,first;
	for ( int i = 0; i <= Ifc::CircleSegments; i ++ ) {
		const float theta = (float) PI * i / Ifc::CircleSegments * 2;
		current = i == Ifc::CircleSegments ? first : 
			BRepBuilderAPI_MakeVertex (  gp_Pnt(r * sin(theta), r * cos(theta), 0.0f)  ).Vertex();
		if ( i ) {
			w.Add(BRepBuilderAPI_MakeEdge(previous,current));
		} else {
			first = current;
		}
		previous = current;
	}
#else
	gp_Ax2 ax = gp_Ax2().Transformed(trsf);
	Handle(Geom_Circle) circle = new Geom_Circle(ax, r);
	TopoDS_Edge edge = BRepBuilderAPI_MakeEdge(circle);
	w.Add(edge);
#endif

	wire = w.Wire();
	return true;
}
bool IfcGeom::convert(IfcSchema::CompositeCurve* IfcCompositeCurve, class TopoDS_Wire& wire) {
	IfcEntities segments = IfcCompositeCurve->Segments();
	BRepBuilderAPI_MakeWire w;
	for( IfcParse::Entities::it it = segments->begin(); it != segments->end(); ++ it ) {
		IfcSchema::CompositeCurveSegment* segment = (IfcSchema::CompositeCurveSegment*)(*it).get();
		TopoDS_Wire wire2;
		if ( ! IfcGeom::convert_wire(segment->ParentCurve(),wire2) ) continue;
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire2, 0.01, TopAbs_WIRE);
		w.Add(wire2);
		if ( w.Error() != BRepBuilderAPI_WireDone ) {
			std::cout << "[Error] Failed to join curve segments:" << std::endl << IfcCompositeCurve->toString() << std::endl;
			return false;
		}
	}
	wire = w.Wire();
	return true;
}
bool IfcGeom::convert(IfcSchema::TrimmedCurve* IfcTrimmedCurve, class TopoDS_Wire& wire) {
	IfcEntity basis = IfcTrimmedCurve->BasisCurve();
	IfcEntity trim1 = *IfcTrimmedCurve->Trim1()->begin();
	IfcEntity trim2 = *IfcTrimmedCurve->Trim2()->begin();
	Handle(Geom_Curve) curve;
	if ( ! IfcGeom::convert_curve(basis,curve) ) return false;
	if ( trim1->dt != trim2->dt ) return false;
	BRepBuilderAPI_MakeWire w;
	if ( trim1->dt == IfcSchema::Enum::IfcParameterValue ) {
		const float p1 = ((IfcSchema::ParameterValue*)trim1.get())->Value() * Ifc::PlaneAngleUnit;
		const float p2 = ((IfcSchema::ParameterValue*)trim2.get())->Value() * Ifc::PlaneAngleUnit;
		BRepBuilderAPI_MakeEdge e (curve,p1,p2);
		w.Add(e.Edge());
	} else if ( trim1->dt == IfcSchema::Enum::IfcCartesianPoint ) {
		gp_Pnt v1,v2;
		IfcGeom::convert((IfcSchema::CartesianPoint*)trim1.get(),v1);
		IfcGeom::convert((IfcSchema::CartesianPoint*)trim2.get(),v2);
		BRepBuilderAPI_MakeEdge e (curve,v1,v2);
		w.Add(e.Edge());
	}
	wire = w.Wire();
	return true;
}
bool IfcGeom::convert(IfcSchema::Circle* IfcCircle, Handle(Geom_Curve)& curve) {
	const float r = IfcCircle->Radius() * Ifc::LengthUnit;
	if ( r == 0.0f ) { return false; }
	IfcSchema::Axis2Placement2D* placement = (IfcSchema::Axis2Placement2D*) IfcCircle->Placement().get();
	gp_Trsf2d trsf;
	IfcGeom::convert(placement, trsf);
	gp_Ax2 ax = gp_Ax2().Transformed(trsf);
	curve = new Geom_Circle(ax, r);
	return true;
}
bool IfcGeom::convert(IfcSchema::Ellipse* IfcEllipse, Handle(Geom_Curve)& curve) {
	float x = IfcEllipse->Axis1() * Ifc::LengthUnit;
	float y = IfcEllipse->Axis2() * Ifc::LengthUnit;
	if ( x == 0.0f || y == 0.0f || y > x ) { return false; }
	IfcSchema::Axis2Placement2D* placement = (IfcSchema::Axis2Placement2D*) IfcEllipse->Placement().get();
	gp_Trsf2d trsf;
	IfcGeom::convert(placement, trsf);
	gp_Ax2 ax;
	ax = gp_Ax2().Transformed(trsf);
	curve = new Geom_Ellipse(ax, x, y);
	return true;
}
bool IfcGeom::convert(IfcSchema::Polyline* IfcPolyline, TopoDS_Wire& result) {
	IfcEntities points = IfcPolyline->Points();

	BRepBuilderAPI_MakeWire w;
	for( IfcParse::Entities::it it = points->begin(); it != points->end(); ++ it ) {
		gp_Pnt P1;gp_Pnt P2;
		IfcGeom::convert((IfcSchema::CartesianPoint*)(*it).get(),P1);
		IfcParse::Entities::it next = it + 1;
		if ( next == points->end() ) {
			if ( IfcPolyline->dt == IfcSchema::Enum::IfcPolyloop ) next = points->begin();
			else break;
		}
		IfcGeom::convert((IfcSchema::CartesianPoint*)(*next).get(),P2);
		if ( P1.X() == P2.X() && P1.Y() == P2.Y() && P1.Z() == P2.Z() ) continue;
		TopoDS_Edge e = BRepBuilderAPI_MakeEdge(P1,P2);
		w.Add(e);
	}

	result = w.Wire();
	return true;
}
bool IfcGeom::convert(IfcSchema::Polyloop* IfcPolyloop, TopoDS_Wire& result) {
	return IfcGeom::convert((IfcSchema::Polyline*)IfcPolyloop,result);
}
bool IfcGeom::convert(IfcSchema::Axis2Placement3D* IfcAxis2Placement3D, gp_Trsf& trsf) {
	gp_Pnt o;gp_Vec x = gp_Vec(1,0,0);gp_Vec z = gp_Vec(0,0,1);

	IfcGeom::convert((IfcSchema::CartesianPoint*) IfcAxis2Placement3D->Origin().get(),o);
	try {
		IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement3D->Dir1().get(),z);
		IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement3D->Dir2().get(),x);
	} catch( IfcParse::IfcException& ) {}

	gp_Ax3 axis(o,z,x);
	gp_Ax3 def(gp_Pnt(),gp_Dir(0,0,1),gp_Dir(1,0,0));
	trsf.SetTransformation(axis,def);
	return true;
}
bool IfcGeom::convert(IfcSchema::Plane* IfcPlane, gp_Pln& plane) {
	IfcSchema::Axis2Placement3D* IfcAxis2Placement3D = (IfcSchema::Axis2Placement3D*) IfcPlane->Placement().get();
	gp_Pnt o;gp_Vec x;gp_Vec z;

	IfcGeom::convert((IfcSchema::CartesianPoint*) IfcAxis2Placement3D->Origin().get(),o);
	IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement3D->Dir1().get(),z);
	IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement3D->Dir2().get(),x);

	gp_Ax3 axis(o,z,x);
	plane = gp_Pln(axis);
	return true;
}
bool IfcGeom::convert(IfcSchema::Axis2Placement2D* IfcAxis2Placement2D, gp_Trsf2d& trsf) {
	gp_Pnt P; gp_Vec V;

	IfcGeom::convert((IfcSchema::CartesianPoint*) IfcAxis2Placement2D->Origin().get(),P);
	IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement2D->Dir1().get(),V);

	gp_Ax2d axis(gp_Pnt2d(P.X(),P.Y()),gp_Vec2d(V.X(),V.Y()));
	trsf.SetTransformation(axis,gp_Ax2d());
	return true;
}
bool IfcGeom::convert(IfcSchema::LocalPlacement* IfcLocalPlacement, gp_Trsf& trsf) {
	while (1) {
		gp_Trsf trsf2;
		IfcGeom::convert((IfcSchema::Axis2Placement3D*) IfcLocalPlacement->Placement().get(),trsf2);
		trsf.PreMultiply(trsf2);
		try {
			IfcLocalPlacement = (IfcSchema::LocalPlacement*) IfcLocalPlacement->Parent().get();
		} catch ( IfcParse::IfcException ) { break; }
	}
	return true;
}
bool IfcGeom::convert_openings(const IfcSchema::BuildingElement* IfcBuildingElement, 
							   const IfcEntities openings, TopoDS_Shape& result, const gp_Trsf& trsf2) {
	for ( IfcParse::Entities::it it = openings->begin(); it != openings->end(); ++ it ) {
		IfcSchema::RelVoidsElement* IfcRelVoidsElement = (IfcSchema::RelVoidsElement*)(*it).get();
		IfcSchema::BuildingElement* IfcOpeningElement = (IfcSchema::BuildingElement*) IfcRelVoidsElement->Opening().get();
		gp_Trsf trsf;
		IfcGeom::convert((IfcSchema::LocalPlacement*) IfcOpeningElement->Placement().get(),trsf);
		gp_Trsf trsf3 = trsf2.Inverted();
		IfcSchema::ProductDefinitionShape* IfcProductDefinitionShape = (IfcSchema::ProductDefinitionShape*) IfcOpeningElement->Shape().get();
		IfcEntities IfcShapeReps = IfcProductDefinitionShape->ShapeReps();
		for ( IfcParse::Entities::it shaperep = IfcShapeReps->begin(); shaperep != IfcShapeReps->end(); ++shaperep ) {
			IfcSchema::ShapeRepresentation* IfcShapeRepresentation = (IfcSchema::ShapeRepresentation*) (*shaperep).get();
			IfcEntities IfcShapes = IfcShapeRepresentation->Shapes();
			for ( IfcParse::Entities::it shape = IfcShapes->begin(); shape != IfcShapes->end(); ++shape ) {
				TopoDS_Shape s;
				if ( ! IfcGeom::convert_shape(*shape,s)) continue;
				s.Move(trsf);
				s.Move(trsf3);
				result = BRepAlgoAPI_Cut(result,s);
			}
		}
	}
	return true;
}
bool IfcGeom::convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face) {
	BRepBuilderAPI_MakeFace mf(wire, false);
	BRepBuilderAPI_FaceError er = mf.Error();
	if ( er == BRepBuilderAPI_NotPlanar ) {
		std::cout << "[Notice] Trying to fix non-planar face" << std::endl;
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire, 0.01, TopAbs_WIRE);
		mf = BRepBuilderAPI_MakeFace(wire, false);
		er = mf.Error();
	}
	if ( er != BRepBuilderAPI_FaceDone ) return false;
	face = mf.Face();
	return true;
}