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

namespace IfcGeom {
	namespace Cache {
#define IFC_GEOM_CACHE
#include "../ifcparse/IfcSchema.h"
#undef IFC_GEOM_CACHE
	}
}
#define IN_CACHE(T,E,t,e) std::map<int,t *>::const_iterator it = Cache::T.find(E->id);\
	if ( it != Cache::T.end() ) { e = *(it->second); return true; }
#define CACHE(T,E,e) Cache::T[E->id] = e;

bool IfcGeom::convert(IfcSchema::ExtrudedAreaSolid* IfcExtrudedAreaSolid, TopoDS_Shape& shape) {
	TopoDS_Face face;
	if ( ! IfcGeom::convert_face(IfcExtrudedAreaSolid->Profile(),face) ) return false;
	const float height = IfcExtrudedAreaSolid->Height() * Ifc::LengthUnit;
	gp_Trsf trsf;
	convert((IfcSchema::Axis2Placement3D*) IfcExtrudedAreaSolid->Placement().get(),trsf);

	gp_Dir dir;
	convert((IfcSchema::Direction*) IfcExtrudedAreaSolid->Dir().get(),dir);
	
	shape = BRepPrimAPI_MakePrism(face,height*dir);
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
	if ( surf->type != IfcSchema::Enum::IfcPlane ) return false;
	IfcSchema::Plane* IfcPlane = (IfcSchema::Plane*)surf.get();
	gp_Pln pln;
	IfcGeom::convert(IfcPlane,pln);
	gp_Pnt pnt = pln.Location();
	bool reverse = IfcHalfSpaceSolid->Flag();
	if ( IfcHalfSpaceSolid->type == IfcSchema::Enum::IfcPolygonalBoundedHalfSpace ) reverse = !reverse;
	if ( reverse ) pnt.Translate(-pln.Axis().Direction());
	else pnt.Translate(pln.Axis().Direction());
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
	extrusion.Move(trsf);
	extrusion.Move(down);	
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
		//std::cout << "[Notice] Trying to fix non-planar face:" << std::endl << IfcFace->toString() << std::endl;
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire, 0.01, TopAbs_WIRE);
		mf = BRepBuilderAPI_MakeFace(wire, false);
		er = mf.Error();
	}
	if ( er != BRepBuilderAPI_FaceDone ) return false;

	if ( bounds->Size() == 1 ) {
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
bool IfcGeom::convert(IfcSchema::CartesianPoint* IfcCartesianPoint, gp_Pnt& point) {
	IN_CACHE(CartesianPoint,IfcCartesianPoint,gp_Pnt,point)
	gp_Pnt* p = new gp_Pnt(
		IfcCartesianPoint->X() * Ifc::LengthUnit,
		IfcCartesianPoint->Y() * Ifc::LengthUnit,
		((*IfcCartesianPoint)[0]->Size() == 3) ? (IfcCartesianPoint->Z() * Ifc::LengthUnit) : 0.0f
	);
	CACHE(CartesianPoint,IfcCartesianPoint,p)
	point = *p;
	return true;
}
bool IfcGeom::convert(IfcSchema::Direction* IfcDirection, gp_Dir& dir) {
	IN_CACHE(Direction,IfcDirection,gp_Dir,dir);
	gp_Dir* d = new gp_Dir(
		IfcDirection->X(),
		IfcDirection->Y(),
		((*IfcDirection)[0]->Size() == 3) ? IfcDirection->Z() : 0.0f
	);
	CACHE(Direction,IfcDirection,d);
	dir = *d;
	return true;
}
bool IfcGeom::convert(IfcSchema::Vector* IfcVector, gp_Vec& v) {
	gp_Dir d;
	IfcGeom::convert((IfcSchema::Direction*)IfcVector->Orientation().get(),d);
	v = IfcVector->Magnitude() * Ifc::LengthUnit * d;
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
bool IfcGeom::convert(IfcSchema::RectangleProfileDef* IfcRectangleProfileDef,class TopoDS_Face& face) {
	const float x = IfcRectangleProfileDef->Width() / 2.0f * Ifc::LengthUnit;
	const float y = IfcRectangleProfileDef->Height() / 2.0f  * Ifc::LengthUnit;

	if ( x == 0.0f || y == 0.0f ) {
		std::cout << "[Notice] Skipping zero sized profile:" << std::endl << IfcRectangleProfileDef->toString() << std::endl;
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::convert((IfcSchema::Axis2Placement2D*)IfcRectangleProfileDef->Placement().get(),trsf2d);
	float coords[8] = {-x,-y,x,-y,x,y,-x,y};
	return IfcGeom::profile_helper(4,coords,0,0,0,trsf2d,face);
}
bool IfcGeom::convert(IfcSchema::IShapeProfileDef* IfcIShapeProfileDef,class TopoDS_Face& face) {
	const float x = IfcIShapeProfileDef->Width() / 2.0f * Ifc::LengthUnit;
	const float y = IfcIShapeProfileDef->Depth() / 2.0f * Ifc::LengthUnit;
	const float d1 = IfcIShapeProfileDef->WebThickness() / 2.0f  * Ifc::LengthUnit;
	const float d2 = IfcIShapeProfileDef->FlangeThickness() * Ifc::LengthUnit;
	bool doFillet = false;
	float f;
	try {
		f = IfcIShapeProfileDef->FilletRadius() * Ifc::LengthUnit;
		doFillet = true;
	} catch ( IfcParse::IfcException& ) {}		

	if ( x == 0.0f || y == 0.0f || d1 == 0.0f || d2 == 0.0f ) {
		std::cout << "[Notice] Skipping zero sized profile:" << std::endl << IfcIShapeProfileDef->toString() << std::endl;
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::convert((IfcSchema::Axis2Placement2D*)IfcIShapeProfileDef->Placement().get(),trsf2d);

	float coords[24] = {-x,-y,x,-y,x,-y+d2,d1,-y+d2,d1,y-d2,x,y-d2,x,y,-x,y,-x,y-d2,-d1,y-d2,-d1,-y+d2,-x,-y+d2};
	int fillets[4] = {3,4,9,10};
	float radii[4] = {f,f,f,f};
	return IfcGeom::profile_helper(12,coords,doFillet ? 4 : 0,fillets,radii,trsf2d,face);
}
bool IfcGeom::convert(IfcSchema::CShapeProfileDef* IfcCShapeProfileDef,class TopoDS_Face& face) {
	const float x = IfcCShapeProfileDef->Depth() / 2.0f * Ifc::LengthUnit;
	const float y = IfcCShapeProfileDef->Width() / 2.0f * Ifc::LengthUnit;
	const float d1 = IfcCShapeProfileDef->WallThickness() * Ifc::LengthUnit;
	const float d2 = IfcCShapeProfileDef->Girth() * Ifc::LengthUnit;
	bool doFillet = false;
	float f1,f2;
	try {
		f1 = IfcCShapeProfileDef->InternalFilletRadius() * Ifc::LengthUnit;
		f2 = f1 + d1;
		doFillet = true;
	} catch ( IfcParse::IfcException& ) {}		

	if ( x == 0.0f || y == 0.0f || d1 == 0.0f || d2 == 0.0f ) {
		std::cout << "[Notice] Skipping zero sized profile:" << std::endl << IfcCShapeProfileDef->toString() << std::endl;
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::convert((IfcSchema::Axis2Placement2D*)IfcCShapeProfileDef->Placement().get(),trsf2d);

	float coords[24] = {-x,-y,x,-y,x,-y+d2,x-d1,-y+d2,x-d1,-y+d1,-x+d1,-y+d1,-x+d1,y-d1,x-d1,y-d1,x-d1,y-d2,x,y-d2,x,y,-x,y};
	int fillets[8] = {0,1,4,5,6,7,10,11};
	float radii[8] = {f2,f2,f1,f1,f1,f1,f2,f2};
	return IfcGeom::profile_helper(12,coords,doFillet ? 8 : 0,fillets,radii,trsf2d,face);
}
bool IfcGeom::convert(IfcSchema::LShapeProfileDef* IfcLShapeProfileDef,class TopoDS_Face& face) {
	const float y = IfcLShapeProfileDef->Depth() / 2.0f * Ifc::LengthUnit;
	const float x = IfcLShapeProfileDef->Width() / 2.0f * Ifc::LengthUnit;
	const float d = IfcLShapeProfileDef->Thickness() * Ifc::LengthUnit;
	bool doFillet = false;
	float f1 = 0.0f;
	float f2 = 0.0f;
	try {
		f1 = IfcLShapeProfileDef->FilletRadius() * Ifc::LengthUnit;
		doFillet = true;
	} catch ( IfcParse::IfcException& ) {}		
	try {
		f2 = IfcLShapeProfileDef->EdgeRadius() * Ifc::LengthUnit;
		doFillet = true;
	} catch ( IfcParse::IfcException& ) {}

	if ( x == 0.0f || y == 0.0f || d == 0.0f ) {
		std::cout << "[Notice] Skipping zero sized profile:" << std::endl << IfcLShapeProfileDef->toString() << std::endl;
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::convert((IfcSchema::Axis2Placement2D*)IfcLShapeProfileDef->Placement().get(),trsf2d);

	float coords[12] = {-x,-y,x,-y,x,-y+d,-x+d,-y+d,-x+d,y,-x,y};
	int fillets[3] = {2,3,4};
	float radii[3] = {f2,f1,f2};
	return IfcGeom::profile_helper(6,coords,doFillet ? 3 : 0,fillets,radii,trsf2d,face);
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
		if ( ! IfcGeom::convert_wire(segment->ParentCurve(),wire2) ) {
			std::cout << "[Warning] Failed to convert:" << std::endl << segment->ParentCurve()->toString() << std::endl;
			continue;	
		}
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
	bool isConic = basis->type == IfcSchema::Enum::IfcCircle || basis->type == IfcSchema::Enum::IfcEllipse;
	float parameterFactor = isConic ? Ifc::PlaneAngleUnit : Ifc::LengthUnit;
	Handle(Geom_Curve) curve;
	if ( ! IfcGeom::convert_curve(basis,curve) ) return false;
	bool cartesian = IfcTrimmedCurve->MasterRepresentation() == "CARTESIAN";
	IfcEntities trims1 = IfcTrimmedCurve->Trim1();
	IfcEntities trims2 = IfcTrimmedCurve->Trim2();
	bool trimmed1 = false;
	bool trimmed2 = false;
	float flt1;
	gp_Pnt pnt1;
	BRepBuilderAPI_MakeWire w;
	for ( IfcParse::Entities::it it = trims1->begin(); it != trims1->end(); it ++ ) {
		const IfcEntity i = *it;
		if ( i->type == IfcSchema::Enum::IfcCartesianPoint && cartesian ) {
			IfcGeom::convert( (IfcSchema::CartesianPoint*) i.get(), pnt1 );
			trimmed1 = true;
		} else if ( i->type == IfcSchema::Enum::IfcParameterValue ) {
			flt1 = ((IfcSchema::ParameterValue*)i.get())->Value() * parameterFactor;
			trimmed1 = true;
		}
	}
	for ( IfcParse::Entities::it it = trims2->begin(); it != trims2->end(); it ++ ) {
		const IfcEntity i = *it;
		if ( i->type == IfcSchema::Enum::IfcCartesianPoint && cartesian && trimmed1 ) {
			gp_Pnt pnt2;
			IfcGeom::convert( (IfcSchema::CartesianPoint*) i.get(), pnt2 );
			BRepBuilderAPI_MakeEdge e (curve,pnt1,pnt2);
			w.Add(e.Edge());			
			trimmed2 = true;
		} else if ( i->type == IfcSchema::Enum::IfcParameterValue && trimmed1 ) {
			float flt2 = ((IfcSchema::ParameterValue*)i.get())->Value() * parameterFactor;
			BRepBuilderAPI_MakeEdge e (curve,flt1,flt2);
			w.Add(e.Edge());
			trimmed2 = true;
		}
	}
	if ( trimmed2 ) wire = w.Wire();
	return trimmed2;
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
bool IfcGeom::convert(IfcSchema::Line* IfcLine, Handle(Geom_Curve)& curve) {
	gp_Pnt pnt;gp_Vec vec;
	IfcGeom::convert((IfcSchema::CartesianPoint*)IfcLine->Pnt().get(),pnt);
	IfcGeom::convert((IfcSchema::Vector*)IfcLine->Dir().get(),vec);	
	curve = new Geom_Line(pnt,vec);
	return true;
}
bool IfcGeom::convert(IfcSchema::Polyline* IfcPolyline, TopoDS_Wire& result) {
	IfcEntities points = IfcPolyline->Points();

	BRepBuilderAPI_MakeWire w;
	int count = 0;
	for( IfcParse::Entities::it it = points->begin(); it != points->end(); ++ it ) {
		gp_Pnt P1;gp_Pnt P2;
		IfcGeom::convert((IfcSchema::CartesianPoint*)(*it).get(),P1);
		IfcParse::Entities::it next = it + 1;
		if ( next == points->end() ) {
			if ( IfcPolyline->type == IfcSchema::Enum::IfcPolyloop ) next = points->begin();
			else break;
		}
		IfcGeom::convert((IfcSchema::CartesianPoint*)(*next).get(),P2);
		if ( P1.X() == P2.X() && P1.Y() == P2.Y() && P1.Z() == P2.Z() ) continue;
		//std::cout << P1.X() << "," << P1.Y() << "," << P1.Z() << " -> " << P2.X() << "," <<P2.Y() << "," << P2.Z() << std::endl;
		TopoDS_Edge e = BRepBuilderAPI_MakeEdge(P1,P2);
		w.Add(e);
		count ++;
	}

	//std::cout << std::endl;
	if ( (count < 3) && IfcPolyline->type == IfcSchema::Enum::IfcPolyloop ) {
		std::cout << "[Notice] Skipping loop with " << count << " edges:" << std::endl << IfcPolyline->toString() << std::endl;
		return false;
	}

	result = w.Wire();
	return true;
}
bool IfcGeom::convert(IfcSchema::Polyloop* IfcPolyloop, TopoDS_Wire& result) {
	return IfcGeom::convert((IfcSchema::Polyline*)IfcPolyloop,result);
}
bool IfcGeom::convert(IfcSchema::Axis2Placement3D* IfcAxis2Placement3D, gp_Trsf& trsf) {
	IN_CACHE(Axis2Placement3D,IfcAxis2Placement3D,gp_Trsf,trsf);

	gp_Trsf* t = new gp_Trsf();
	gp_Pnt o;gp_Dir axis = gp_Dir(0,0,1);gp_Dir refDirection; bool hasRef = false;
	IfcGeom::convert((IfcSchema::CartesianPoint*) IfcAxis2Placement3D->Origin().get(),o);
	try {
		IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement3D->Axis().get(),axis);
		IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement3D->RefDirection().get(),refDirection);
		hasRef = true;
	} catch( IfcParse::IfcException& ) {}
	gp_Ax3 ax3;
	if ( hasRef ) ax3 = gp_Ax3(o,axis,refDirection);
	else ax3 = gp_Ax3(o,axis);
	t->SetTransformation(ax3, gp_Ax3(gp_Pnt(),gp_Dir(0,0,1),gp_Dir(1,0,0)));

	CACHE(Axis2Placement3D,IfcAxis2Placement3D,t);
	trsf = *t;
	return true;
}
bool IfcGeom::convert(IfcSchema::Plane* IfcPlane, gp_Pln& plane) {
	IN_CACHE(Plane,IfcPlane,gp_Pln,plane)
	IfcSchema::Axis2Placement3D* IfcAxis2Placement3D = (IfcSchema::Axis2Placement3D*) IfcPlane->Placement().get();
	gp_Pnt o;gp_Dir axis = gp_Dir(0,0,1);gp_Dir refDirection; bool hasRef = false;

	IfcGeom::convert((IfcSchema::CartesianPoint*) IfcAxis2Placement3D->Origin().get(),o);
	try {
		IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement3D->Axis().get(),axis);
		IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement3D->RefDirection().get(),refDirection);
		hasRef = true;
	} catch( IfcParse::IfcException& ) {}

	gp_Ax3 ax3;
	if ( hasRef ) ax3 = gp_Ax3(o,axis,refDirection);
	else ax3 = gp_Ax3(o,axis);

	gp_Pln* ppln = new gp_Pln(ax3);
	CACHE(Plane,IfcPlane,ppln);
	plane = *ppln;
	return true;
}
bool IfcGeom::convert(IfcSchema::Axis2Placement2D* IfcAxis2Placement2D, gp_Trsf2d& trsf) {
	IN_CACHE(Axis2Placement2D,IfcAxis2Placement2D,gp_Trsf2d,trsf)
	gp_Pnt P; gp_Dir V (1,0,0);

	gp_Trsf2d* ptrsf = new gp_Trsf2d();
	IfcGeom::convert((IfcSchema::CartesianPoint*) IfcAxis2Placement2D->Origin().get(),P);
	try {
		IfcGeom::convert((IfcSchema::Direction*) IfcAxis2Placement2D->Axis().get(),V);
	} catch( IfcParse::IfcException& ) {}

	gp_Ax2d axis(gp_Pnt2d(P.X(),P.Y()),gp_Dir2d(V.X(),V.Y()));
	ptrsf->SetTransformation(axis,gp_Ax2d());

	CACHE(Axis2Placement2D,IfcAxis2Placement2D,ptrsf);
	trsf = *ptrsf;
	return true;
}
bool IfcGeom::convert(IfcSchema::LocalPlacement* IfcLocalPlacement, gp_Trsf& trsf) {
	IN_CACHE(LocalPlacement,IfcLocalPlacement,gp_Trsf,trsf)
	gp_Trsf* ptrsf = new gp_Trsf();
	while (1) {
		gp_Trsf trsf2;
		IfcGeom::convert((IfcSchema::Axis2Placement3D*) IfcLocalPlacement->Placement().get(),trsf2);
		ptrsf->PreMultiply(trsf2);
		try {
			IfcLocalPlacement = (IfcSchema::LocalPlacement*) IfcLocalPlacement->Parent().get();
		} catch ( IfcParse::IfcException ) { break; }
	}
	CACHE(LocalPlacement,IfcLocalPlacement,ptrsf);
	trsf = *ptrsf;
	return true;
}
bool IfcGeom::convert_openings(const IfcSchema::BuildingElement* IfcBuildingElement, 
							   const IfcEntities openings, TopoDS_Shape& result, const gp_Trsf& trsf2) {
	for ( IfcParse::Entities::it it = openings->begin(); it != openings->end(); ++ it ) {
		IfcSchema::RelVoidsElement* IfcRelVoidsElement = (IfcSchema::RelVoidsElement*)(*it).get();
		IfcSchema::BuildingElement* IfcOpeningElement = (IfcSchema::BuildingElement*) IfcRelVoidsElement->Opening().get();
		gp_Trsf trsf;
		IfcGeom::convert((IfcSchema::LocalPlacement*) IfcOpeningElement->Placement().get(),trsf);
		trsf.PreMultiply(trsf2.Inverted());
		IfcSchema::ProductDefinitionShape* IfcProductDefinitionShape = (IfcSchema::ProductDefinitionShape*) IfcOpeningElement->Shape().get();
		IfcEntities IfcShapeReps = IfcProductDefinitionShape->ShapeReps();
		for ( IfcParse::Entities::it shaperep = IfcShapeReps->begin(); shaperep != IfcShapeReps->end(); ++shaperep ) {
			IfcSchema::ShapeRepresentation* IfcShapeRepresentation = (IfcSchema::ShapeRepresentation*) (*shaperep).get();
			IfcEntities IfcShapes = IfcShapeRepresentation->Shapes();
			for ( IfcParse::Entities::it shape = IfcShapes->begin(); shape != IfcShapes->end(); ++shape ) {
				TopoDS_Shape s;
				if ( ! IfcGeom::convert_shape(*shape,s)) continue;
				s.Move(trsf);
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
		//std::cout << "[Notice] Trying to fix non-planar face" << std::endl;
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire, 0.01, TopAbs_WIRE);
		mf = BRepBuilderAPI_MakeFace(wire, false);
		er = mf.Error();
	}
	if ( er != BRepBuilderAPI_FaceDone ) return false;
	face = mf.Face();
	return true;
}
bool IfcGeom::profile_helper(int numVerts, float* verts, int numFillets, int* filletIndices, float* filletRadii, gp_Trsf2d trsf, TopoDS_Face& face) {
	TopoDS_Vertex* vertices = new TopoDS_Vertex[numVerts];
	
	for ( int i = 0; i < numVerts; i ++ ) {
		gp_XY xy (verts[2*i],verts[2*i+1]);
		trsf.Transforms(xy);
		vertices[i] = BRepBuilderAPI_MakeVertex(gp_Pnt(xy.X(),xy.Y(),0.0f));
	}

	BRepBuilderAPI_MakeWire w;
	for ( int i = 0; i < numVerts; i ++ )
		w.Add(BRepBuilderAPI_MakeEdge(vertices[i],vertices[(i+1)%numVerts]));

	IfcGeom::convert_wire_to_face(w.Wire(),face);

	if ( numFillets ) {
		BRepFilletAPI_MakeFillet2d fillet (face);
		for ( int i = 0; i < numFillets; i ++ ) {
			const float radius = filletRadii[i];
			if ( radius < 1e-7 ) continue;
			fillet.AddFillet(vertices[filletIndices[i]],radius);
		}
		fillet.Build();
		face = TopoDS::Face(fillet.Shape());
	}

	delete[] vertices;
	return true;
}
void IfcGeom::Cache::Purge() {
#define IFC_GEOM_CACHE_PURGE
#include "../ifcparse/IfcSchema.h"
#undef IFC_GEOM_CACHE_PURGE
	PurgeShapeCache();
}