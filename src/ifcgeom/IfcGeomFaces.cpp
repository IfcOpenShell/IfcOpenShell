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

#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS_Iterator.hxx>

#include <BRepAlgoAPI_Cut.hxx>

#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>

#include <TopLoc_Location.hxx>
#include <BRepGProp_Face.hxx>

#include <Standard_Failure.hxx>

#include <BRep_Tool.hxx>
#include <BRepCheck_Face.hxx>
#include <BRepBuilderAPI_Transform.hxx>

#ifdef USE_IFC4
#include <Geom_BSplineSurface.hxx>
#include <TColgp_Array2OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#endif

#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::Kernel::convert(const IfcSchema::IfcFace* l, TopoDS_Shape& face) {
	IfcSchema::IfcFaceBound::list::ptr bounds = l->Bounds();

	Handle(Geom_Surface) face_surface;
	bool reversed_face_surface = false;
	const bool is_face_surface = l->is(IfcSchema::Type::IfcFaceSurface);

	if (is_face_surface) {
		IfcSchema::IfcFaceSurface* fs = (IfcSchema::IfcFaceSurface*) l;
		fs->FaceSurface();
		// FIXME: Surfaces are interpreted as a TopoDS_Shape
		TopoDS_Shape surface_shape;
		if (!convert_shape(fs->FaceSurface(), surface_shape)) return false;

		// FIXME: Assert this obtaines the only face
		TopExp_Explorer exp(surface_shape, TopAbs_FACE);
		if (!exp.More()) return false;

		TopoDS_Face surface = TopoDS::Face(exp.Current());
		face_surface = BRep_Tool::Surface(surface);
	}
	
	const int num_bounds = bounds->size();
	int num_outer_bounds = 0;

	for (IfcSchema::IfcFaceBound::list::it it = bounds->begin(); it != bounds->end(); ++it) {
		IfcSchema::IfcFaceBound* bound = *it;
		if (bound->is(IfcSchema::Type::IfcFaceOuterBound)) num_outer_bounds ++;
	}

	// The number of outer bounds should be one according to the schema. Also Open Cascade
	// expects this, but it is not strictly checked. Regardless, if the number is greater,
	// the face will still be processed as long as there are no holes. A compound of faces
	// is returned in that case.
	if (num_bounds > 1 && num_outer_bounds > 1 && num_bounds != num_outer_bounds) {
		Logger::Message(Logger::LOG_ERROR, "Invalid configuration of boundaries for:", l->entity);
		return false;
	}

	TopoDS_Compound compound;
	BRep_Builder builder;
	if (num_outer_bounds > 1) {
		builder.MakeCompound(compound);
	}
	
	// The builder is initialized on the heap because of the various different moments
	// of initialization depending on the configuration of surfaces and boundaries.
	BRepBuilderAPI_MakeFace* mf = 0;
	
	bool success = false;
	int processed = 0;

	for (int process_interior = 0; process_interior <= 1; ++process_interior) {
		for (IfcSchema::IfcFaceBound::list::it it = bounds->begin(); it != bounds->end(); ++it) {
			IfcSchema::IfcFaceBound* bound = *it;
			IfcSchema::IfcLoop* loop = bound->Bound();
		
			bool same_sense = bound->Orientation();
			const bool is_interior = 
				!bound->is(IfcSchema::Type::IfcFaceOuterBound) &&
				(num_bounds > 1) &&
				(num_outer_bounds < num_bounds);

			// The exterior face boundary is processed first
			if (is_interior == !process_interior) continue;
		
			TopoDS_Wire wire;
			if (!convert_wire(loop, wire)) break;

			/*
			The approach below does not result in a significant speed-up
			if (loop->is(IfcSchema::Type::IfcPolyLoop) && processed == 0 && face_surface.IsNull()) {
				IfcSchema::IfcPolyLoop* polyloop = (IfcSchema::IfcPolyLoop*) loop;
				IfcSchema::IfcCartesianPoint::list::ptr points = polyloop->Polygon();

				if (points->size() == 3) {
					// Help Open Cascade by finding the plane more efficiently
					IfcSchema::IfcCartesianPoint::list::it point_iterator = points->begin();
					gp_Pnt a, b, c;
					convert(*point_iterator++, a);
					convert(*point_iterator++, b);
					convert(*point_iterator++, c);
					const gp_XYZ ab = (b.XYZ() - a.XYZ());
					const gp_XYZ ac = (c.XYZ() - a.XYZ());
					const gp_Vec cross = ab.Crossed(ac);
					if (cross.SquareMagnitude() > ALMOST_ZERO) {
						const gp_Dir n = cross;
						face_surface = new Geom_Plane(a, n);
					}
				}
			}
			*/
		
			if (!same_sense) {
				wire.Reverse();
			}

			ShapeFix_ShapeTolerance FTol;
			FTol.SetTolerance(wire, getValue(GV_PRECISION), TopAbs_WIRE);

			if (!mf) {
				if (face_surface.IsNull()) {
					mf = new BRepBuilderAPI_MakeFace(wire);
				} else {
					mf = new BRepBuilderAPI_MakeFace(face_surface, wire); 
				}				

				/* BRepBuilderAPI_FaceError er = mf->Error();
				if (er == BRepBuilderAPI_NotPlanar) {
					ShapeFix_ShapeTolerance FTol;
					FTol.SetTolerance(wire, getValue(GV_PRECISION), TopAbs_WIRE);
					delete mf;
					mf = new BRepBuilderAPI_MakeFace(wire);
				} */

				if (mf->IsDone()) {
					TopoDS_Face outer_face_bound = mf->Face();

					if (BRepCheck_Face(outer_face_bound).OrientationOfWires() == BRepCheck_BadOrientationOfSubshape) {
						wire.Reverse();
						same_sense = !same_sense;
						delete mf;
						if (face_surface.IsNull()) {
							mf = new BRepBuilderAPI_MakeFace(wire);
						} else {
							mf = new BRepBuilderAPI_MakeFace(face_surface, wire); 
						}
						ShapeFix_Face fix(mf->Face());
						fix.FixOrientation();
						fix.Perform();
						outer_face_bound = fix.Face();
					}

					// If the wires are reversed the face needs to be reversed as well in order
					// to maintain the counter-clock-wise ordering of the bounding wire's vertices.
					bool all_reversed = true;
					TopoDS_Iterator it(outer_face_bound, false);
					for (; it.More(); it.Next()) {
						const TopoDS_Wire& w = TopoDS::Wire(it.Value());
						if ((w.Orientation() != TopAbs_REVERSED) == same_sense) {
							all_reversed = false;
						}
					}

					if (all_reversed) {
						outer_face_bound.Reverse();
					}

					if (num_outer_bounds > 1) {
						builder.Add(compound, outer_face_bound);
						delete mf; mf = 0;
					} else if (num_bounds > 1) {
						// Reinitialize the builder to the outer face 
						// bound in order to add holes more robustly.
						delete mf;
						mf = new BRepBuilderAPI_MakeFace(outer_face_bound);
					} else {
						face = outer_face_bound;
						success = true;
					}
				} else {
					break;
				}

			} else {
				mf->Add(wire);
			}
			processed ++;
		}
	}

	if (!success) {
		success = processed == num_bounds;
		if (success) {
			if (num_outer_bounds > 1) {
				face = compound;
			} else {
				success = success && mf->IsDone();
				if (success) {
					face = mf->Face();
				}
			}
		}
	}

	if (success) {
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(face, getValue(GV_PRECISION), TopAbs_FACE);
	}

	delete mf;
	return success;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcArbitraryClosedProfileDef* l, TopoDS_Shape& face) {
	TopoDS_Wire wire;
	if ( ! convert_wire(l->OuterCurve(),wire) ) return false;

	TopoDS_Face f;
	bool success = convert_wire_to_face(wire, f);
	if (success) face = f;
	return success;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcArbitraryProfileDefWithVoids* l, TopoDS_Shape& face) {
	TopoDS_Wire profile;
	if ( ! convert_wire(l->OuterCurve(),profile) ) return false;
	BRepBuilderAPI_MakeFace mf(profile);
	IfcSchema::IfcCurve::list::ptr voids = l->InnerCurves();
	for( IfcSchema::IfcCurve::list::it it = voids->begin(); it != voids->end(); ++ it ) {
		TopoDS_Wire hole;
		if ( convert_wire(*it,hole) ) {
			mf.Add(hole);
		}
	}
	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();
	face = TopoDS::Face(sfs.Shape());
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRectangleProfileDef* l, TopoDS_Shape& face) {
	const double x = l->XDim() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double y = l->YDim() / 2.0f * getValue(GV_LENGTH_UNIT);

	if ( x < ALMOST_ZERO || y < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::Kernel::convert(l->Position(),trsf2d);
	double coords[8] = {-x,-y,x,-y,x,y,-x,y};
	return profile_helper(4,coords,0,0,0,trsf2d,face);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRoundedRectangleProfileDef* l, TopoDS_Shape& face) {
	const double x = l->XDim() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double y = l->YDim() / 2.0f  * getValue(GV_LENGTH_UNIT);
	const double r = l->RoundingRadius() * getValue(GV_LENGTH_UNIT);

	if ( x < ALMOST_ZERO || y < ALMOST_ZERO || r < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::Kernel::convert(l->Position(),trsf2d);
	double coords[8] = {-x,-y, x,-y, x,y, -x,y};
	int fillets[4] = {0,1,2,3};
	double radii[4] = {r,r,r,r};
	return profile_helper(4,coords,4,fillets,radii,trsf2d,face);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRectangleHollowProfileDef* l, TopoDS_Shape& face) {
	const double x = l->XDim() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double y = l->YDim() / 2.0f  * getValue(GV_LENGTH_UNIT);
	const double d = l->WallThickness() * getValue(GV_LENGTH_UNIT);

	const bool fr1 = l->hasOuterFilletRadius();
	const bool fr2 = l->hasInnerFilletRadius();

	const double r1 = fr1 ? l->OuterFilletRadius() * getValue(GV_LENGTH_UNIT) : 0.;
	const double r2 = fr2 ? l->InnerFilletRadius() * getValue(GV_LENGTH_UNIT) : 0.;
	
	if ( x < ALMOST_ZERO || y < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	TopoDS_Face f1;
	TopoDS_Face f2;

	gp_Trsf2d trsf2d;
	IfcGeom::Kernel::convert(l->Position(),trsf2d);
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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTrapeziumProfileDef* l, TopoDS_Shape& face) {
	const double x1 = l->BottomXDim() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double w = l->TopXDim() * getValue(GV_LENGTH_UNIT);
	const double dx = l->TopXOffset() * getValue(GV_LENGTH_UNIT);
	const double y = l->YDim() / 2.0f  * getValue(GV_LENGTH_UNIT);

	if ( x1 < ALMOST_ZERO || w < ALMOST_ZERO || y < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::Kernel::convert(l->Position(),trsf2d);
	double coords[8] = {-x1,-y, x1,-y, dx+w-x1,y, dx-x1,y};
	return profile_helper(4,coords,0,0,0,trsf2d,face);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcIShapeProfileDef* l, TopoDS_Shape& face) {
	const double x1 = l->OverallWidth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double y = l->OverallDepth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d1 = l->WebThickness() / 2.0f  * getValue(GV_LENGTH_UNIT);
	const double dy1 = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);

	bool doFillet1 = l->hasFilletRadius();
	double f1 = 0.;
	if ( doFillet1 ) {
		f1 = l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}

	bool doFillet2 = doFillet1;
	double x2 = x1, dy2 = dy1, f2 = f1;

	if (l->is(IfcSchema::Type::IfcAsymmetricIShapeProfileDef)) {
		IfcSchema::IfcAsymmetricIShapeProfileDef* assym = (IfcSchema::IfcAsymmetricIShapeProfileDef*) l;
		x2 = assym->TopFlangeWidth() / 2. * getValue(GV_LENGTH_UNIT);
		doFillet2 = assym->hasTopFlangeFilletRadius();
		if (doFillet2) {
			f2 = assym->TopFlangeFilletRadius() * getValue(GV_LENGTH_UNIT);
		}
		if (assym->hasTopFlangeThickness()) {
			dy2 = assym->TopFlangeThickness() * getValue(GV_LENGTH_UNIT);
		}
	}	

	if ( x1 < ALMOST_ZERO || x2 < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || dy1 < ALMOST_ZERO || dy2 < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	convert(l->Position(),trsf2d);

	double coords[24] = {-x1,-y, x1,-y, x1,-y+dy1, d1,-y+dy1, d1,y-dy2, x2,y-dy2, x2,y, -x2,y, -x2,y-dy2, -d1,y-dy2, -d1,-y+dy1, -x1,-y+dy1};
	int fillets[4] = {3,4,9,10};
	double radii[4] = {f1,f1,f2,f2};
	return profile_helper(12,coords,(doFillet1||doFillet2) ? 4 : 0,fillets,radii,trsf2d,face);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcZShapeProfileDef* l, TopoDS_Shape& face) {
	const double x = l->FlangeWidth() * getValue(GV_LENGTH_UNIT);
	const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double dx = l->WebThickness() / 2.0f  * getValue(GV_LENGTH_UNIT);
	const double dy = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);

	bool doFillet = l->hasFilletRadius();
	bool doEdgeFillet = l->hasEdgeRadius();
	
	double f1 = 0.;
	double f2 = 0.;

	if ( doFillet ) {
		f1 = l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}
	if ( doEdgeFillet ) {
		f2 = l->EdgeRadius() * getValue(GV_LENGTH_UNIT);
	}

	if ( x == 0.0f || y == 0.0f || dx == 0.0f || dy == 0.0f ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::Kernel::convert(l->Position(),trsf2d);

	double coords[16] = {-dx,-y, x,-y, x,-y+dy, dx,-y+dy, dx,y, -x,y, -x,y-dy, -dx,y-dy};
	int fillets[4] = {2,3,6,7};
	double radii[4] = {f2,f1,f2,f1};
	return profile_helper(8,coords,(doFillet || doEdgeFillet) ? 4 : 0,fillets,radii,trsf2d,face);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCShapeProfileDef* l, TopoDS_Shape& face) {
	const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double x = l->Width() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d1 = l->WallThickness() * getValue(GV_LENGTH_UNIT);
	const double d2 = l->Girth() * getValue(GV_LENGTH_UNIT);
	bool doFillet = l->hasInternalFilletRadius();
	double f1 = 0;
	double f2 = 0;
	if ( doFillet ) {
		f1 = l->InternalFilletRadius() * getValue(GV_LENGTH_UNIT);
		f2 = f1 + d1;
	}

	if ( x < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || d2 < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	IfcGeom::Kernel::convert(l->Position(),trsf2d);

	double coords[24] = {-x,-y,x,-y,x,-y+d2,x-d1,-y+d2,x-d1,-y+d1,-x+d1,-y+d1,-x+d1,y-d1,x-d1,y-d1,x-d1,y-d2,x,y-d2,x,y,-x,y};
	int fillets[8] = {0,1,4,5,6,7,10,11};
	double radii[8] = {f2,f2,f1,f1,f1,f1,f2,f2};
	return profile_helper(12,coords,doFillet ? 8 : 0,fillets,radii,trsf2d,face);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcLShapeProfileDef* l, TopoDS_Shape& face) {
	const bool hasSlope = l->hasLegSlope();
	const bool doEdgeFillet = l->hasEdgeRadius();
	const bool doFillet = l->hasFilletRadius();

	const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double x = (l->hasWidth() ? l->Width() : l->Depth()) / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d = l->Thickness() * getValue(GV_LENGTH_UNIT);
	const double slope = hasSlope ? (l->LegSlope() * getValue(GV_PLANEANGLE_UNIT)) : 0.;
	
	double f1 = 0.0f;
	double f2 = 0.0f;
	if (doFillet) {
		f1 = l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}
	if ( doEdgeFillet) {
		f2 = l->EdgeRadius() * getValue(GV_LENGTH_UNIT);
	}

	if ( x < ALMOST_ZERO || y < ALMOST_ZERO || d < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	double xx = -x+d;
	double xy = -y+d;
	double dy1 = 0.;
	double dy2 = 0.;
	double dx1 = 0.;
	double dx2 = 0.;
	if (hasSlope) {
		dy1 = tan(slope) * x;
		dy2 = tan(slope) * (x - d);
		dx1 = tan(slope) * y;
		dx2 = tan(slope) * (y - d);

		const double x1s = x; const double y1s = -y + d - dy1;
		const double x1e = -x + d; const double y1e = -y + d + dy2;
		const double x2s = -x + d - dx1; const double y2s = y;
		const double x2e = -x + d + dx2; const double y2e = -y + d;

		const double a1 = y1e - y1s;
		const double b1 = x1s - x1e;
		const double c1 = a1*x1s + b1*y1s;

		const double a2 = y2e - y2s;
		const double b2 = x2s - x2e;
		const double c2 = a2*x2s + b2*y2s;

		const double det = a1*b2 - a2*b1;

		if (ALMOST_THE_SAME(det, 0.)) {
			Logger::Message(Logger::LOG_NOTICE, "Legs do not intersect for:",l->entity);
			return false;
		}

		xx = (b2*c1 - b1*c2) / det;
		xy = (a1*c2 - a2*c1) / det;
	}

	gp_Trsf2d trsf2d;
	convert(l->Position(),trsf2d);

	double coords[12] = {-x,-y, x,-y, x,-y+d-dy1, xx, xy, -x+d-dx1,y, -x,y};
	int fillets[3] = {2,3,4};
	double radii[3] = {f2,f1,f2};
	return profile_helper(6,coords,doFillet ? 3 : 0,fillets,radii,trsf2d,face);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcUShapeProfileDef* l, TopoDS_Shape& face) {
	const bool doEdgeFillet = l->hasEdgeRadius();
	const bool doFillet = l->hasFilletRadius();
	const bool hasSlope = l->hasFlangeSlope();

	const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double x = l->FlangeWidth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d1 = l->WebThickness() * getValue(GV_LENGTH_UNIT);
	const double d2 = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);
	const double slope = hasSlope ? (l->FlangeSlope() * getValue(GV_PLANEANGLE_UNIT)) : 0.;
	
	double dy1 = 0.0f;
	double dy2 = 0.0f;
	double f1 = 0.0f;
	double f2 = 0.0f;

	if (doFillet) {
		f1 = l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}
	if (doEdgeFillet) {
		f2 = l->EdgeRadius() * getValue(GV_LENGTH_UNIT);
	}

	if (hasSlope) {
		dy1 = (x - d1) * tan(slope);
		dy2 = x * tan(slope);
	}

	if ( x < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || d2 < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	gp_Trsf2d trsf2d;
	convert(l->Position(),trsf2d);

	double coords[16] = {-x,-y, x,-y, x,-y+d2-dy2, -x+d1,-y+d2+dy1, -x+d1,y-d2-dy1, x,y-d2+dy2, x,y, -x,y};
	int fillets[4] = {2,3,4,5};
	double radii[4] = {f2,f1,f1,f2};
	return profile_helper(8, coords, (doFillet || doEdgeFillet) ? 4 : 0, fillets, radii, trsf2d, face);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTShapeProfileDef* l, TopoDS_Shape& face) {
	const bool doFlangeEdgeFillet = l->hasFlangeEdgeRadius();
	const bool doWebEdgeFillet = l->hasWebEdgeRadius();
	const bool doFillet = l->hasFilletRadius();
	const bool hasFlangeSlope = l->hasFlangeSlope();
	const bool hasWebSlope = l->hasWebSlope();

	const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double x = l->FlangeWidth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d1 = l->WebThickness() * getValue(GV_LENGTH_UNIT);
	const double d2 = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);
	const double flangeSlope = hasFlangeSlope ? (l->FlangeSlope() * getValue(GV_PLANEANGLE_UNIT)) : 0.;
	const double webSlope = hasWebSlope ? (l->WebSlope() * getValue(GV_PLANEANGLE_UNIT)) : 0.;

	if ( x < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || d2 < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}
	
	double dy1 = 0.0f;
	double dy2 = 0.0f;
	double dx1 = 0.0f;
	double dx2 = 0.0f;
	double f1 = 0.0f;
	double f2 = 0.0f;
	double f3 = 0.0f;

	if (doFillet) {
		f1 = l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}
	if (doWebEdgeFillet) {
		f2 = l->WebEdgeRadius() * getValue(GV_LENGTH_UNIT);
	}
	if (doFlangeEdgeFillet) {
		f3 = l->FlangeEdgeRadius() * getValue(GV_LENGTH_UNIT);
	}

	double xx, xy;
	if (hasFlangeSlope) {
		dy1 = (x / 2. - d1) * tan(flangeSlope);
		dy2 = x / 2. * tan(flangeSlope);
	}
	if (hasWebSlope) {
		dx1 = (y - d2) * tan(webSlope);
		dx2 = y * tan(webSlope);
	}
	if (hasWebSlope || hasFlangeSlope) {
		const double x1s = d1/2. - dx2; const double y1s = -y;
		const double x1e = d1/2. + dx1; const double y1e = y - d2;
		const double x2s = x; const double y2s = y - d2 + dy2;
		const double x2e = d1/2.; const double y2e = y - d2 - dy1;

		const double a1 = y1e - y1s;
		const double b1 = x1s - x1e;
		const double c1 = a1*x1s + b1*y1s;

		const double a2 = y2e - y2s;
		const double b2 = x2s - x2e;
		const double c2 = a2*x2s + b2*y2s;

		const double det = a1*b2 - a2*b1;

		if (ALMOST_THE_SAME(det, 0.)) {
			Logger::Message(Logger::LOG_NOTICE, "Web and flange do not intersect for:",l->entity);
			return false;
		}

		xx = (b2*c1 - b1*c2) / det;
		xy = (a1*c2 - a2*c1) / det;
	} else {
		xx = d1 / 2;
		xy = y - d2;
	}

	gp_Trsf2d trsf2d;
	convert(l->Position(),trsf2d);

	double coords[16] = {d1/2.-dx2,-y, xx,xy, x,y-d2+dy2, x,y, -x,y, -x,y-d2+dy2, -xx,xy, -d1/2.+dx2,-y};
	int fillets[6] = {0,1,2,5,6,7};
	double radii[6] = {f2,f1,f3,f3,f1,f2};
	return profile_helper(8, coords, (doFillet || doWebEdgeFillet || doFlangeEdgeFillet) ? 6 : 0, fillets, radii, trsf2d, face);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCircleProfileDef* l, TopoDS_Shape& face) {
	const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
	if ( r == 0.0f ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}
	
	gp_Trsf2d trsf;	
	convert(l->Position(),trsf);

	BRepBuilderAPI_MakeWire w;
	gp_Ax2 ax = gp_Ax2().Transformed(trsf);
	Handle(Geom_Circle) circle = new Geom_Circle(ax, r);
	TopoDS_Edge edge = BRepBuilderAPI_MakeEdge(circle);
	w.Add(edge);

	TopoDS_Face f;
	bool success = convert_wire_to_face(w, f);
	if (success) face = f;
	return success;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCircleHollowProfileDef* l, TopoDS_Shape& face) {
	const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
	const double t = l->WallThickness() * getValue(GV_LENGTH_UNIT);
	
	if ( r == 0.0f || t == 0.0f ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}
	
	gp_Trsf2d trsf;	
	convert(l->Position(),trsf);
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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcEllipseProfileDef* l, TopoDS_Shape& face) {
	double rx = l->SemiAxis1() * getValue(GV_LENGTH_UNIT);
	double ry = l->SemiAxis2() * getValue(GV_LENGTH_UNIT);

	if ( rx < ALMOST_ZERO || ry < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l->entity);
		return false;
	}

	const bool rotated = ry > rx;
	gp_Trsf2d trsf;	
	convert(l->Position(),trsf);

	gp_Ax2 ax = gp_Ax2();
	if (rotated) {
		ax.Rotate(ax.Axis(), M_PI / 2.);
		std::swap(rx, ry);
	}
	ax.Transform(trsf);

	BRepBuilderAPI_MakeWire w;
	Handle(Geom_Ellipse) ellipse = new Geom_Ellipse(ax, rx, ry);
	TopoDS_Edge edge = BRepBuilderAPI_MakeEdge(ellipse);
	w.Add(edge);

	TopoDS_Face f;
	bool success = convert_wire_to_face(w, f);
	if (success) face = f;
	return success;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCenterLineProfileDef* l, TopoDS_Shape& face) {
	const double d = l->Thickness() * getValue(GV_LENGTH_UNIT) / 2.;

	TopoDS_Wire wire;
	if (!convert_wire(l->Curve(), wire)) return false;

	// BRepOffsetAPI_MakeOffset insists on creating circular arc
	// segments for joining the curves that constitute the center
	// line. This is probably not in accordance with the IFC spec.
	// Although it does not specify a method to join segments
	// explicitly, it does dictate 'a constant thickness along the
	// curve'. Therefore for simple singular wires a quick
	// alternative is provided that uses a straight join.

	TopExp_Explorer exp(wire, TopAbs_EDGE);
	TopoDS_Edge edge = TopoDS::Edge(exp.Current());
	exp.Next();

	if (!exp.More()) {
		double u1, u2;
		Handle(Geom_Curve) curve = BRep_Tool::Curve(edge, u1, u2);

		Handle(Geom_TrimmedCurve) trim = new Geom_TrimmedCurve(curve, u1, u2);

		Handle(Geom_OffsetCurve) c1 = new Geom_OffsetCurve(trim,  d, gp::DZ());
		Handle(Geom_OffsetCurve) c2 = new Geom_OffsetCurve(trim, -d, gp::DZ());

		gp_Pnt c1a, c1b, c2a, c2b;
		c1->D0(c1->FirstParameter(), c1a);
		c1->D0(c1->LastParameter(), c1b);
		c2->D0(c2->FirstParameter(), c2a);
		c2->D0(c2->LastParameter(), c2b);

		BRepBuilderAPI_MakeWire mw;
		mw.Add(BRepBuilderAPI_MakeEdge(c1));
		mw.Add(BRepBuilderAPI_MakeEdge(c1a, c2a));
		mw.Add(BRepBuilderAPI_MakeEdge(c2));
		mw.Add(BRepBuilderAPI_MakeEdge(c2b, c1b));
		
		face = BRepBuilderAPI_MakeFace(mw.Wire());
	} else {
		BRepOffsetAPI_MakeOffset offset(BRepBuilderAPI_MakeFace(gp_Pln(gp::Origin(), gp::DZ())));
		offset.AddWire(wire);
		offset.Perform(d);
		face = BRepBuilderAPI_MakeFace(TopoDS::Wire(offset));
	}
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCompositeProfileDef* l, TopoDS_Shape& face) {
	// BRepBuilderAPI_MakeFace mf;

	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	IfcSchema::IfcProfileDef::list::ptr profiles = l->Profiles();
	bool first = true;
	for (IfcSchema::IfcProfileDef::list::it it = profiles->begin(); it != profiles->end(); ++it) {
		TopoDS_Face f;
		if (convert_face(*it, f)) {
			builder.Add(compound, f);
			/* TopExp_Explorer exp(f, TopAbs_WIRE);
			for (; exp.More(); exp.Next()) {
				const TopoDS_Wire& wire = TopoDS::Wire(exp.Current());
				if (first) {
					mf.Init(BRepBuilderAPI_MakeFace(wire));
				} else {
					mf.Add(wire);
				}
				first = false;
			} */
		}
	}

	face = compound;
	return !face.IsNull();
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcDerivedProfileDef* l, TopoDS_Shape& face) {
	TopoDS_Face f;
	gp_Trsf2d trsf2d;
	if (convert_face(l->ParentProfile(), f) && IfcGeom::Kernel::convert(l->Operator(), trsf2d)) {
		gp_Trsf trsf = trsf2d;
		face = TopoDS::Face(BRepBuilderAPI_Transform(f, trsf));
		return true;
	} else {
		return false;
	}
}

#ifdef USE_IFC4

bool IfcGeom::Kernel::convert(const IfcSchema::IfcBSplineSurfaceWithKnots* l, TopoDS_Shape& face) {
	SHARED_PTR< IfcTemplatedEntityListList<IfcSchema::IfcCartesianPoint> > cps = l->ControlPointsList();
	std::vector<double> uknots = l->UKnots();
	std::vector<double> vknots = l->VKnots();
	std::vector<int> umults = l->UMultiplicities();
	std::vector<int> vmults = l->VMultiplicities();

	TColgp_Array2OfPnt Poles (0, cps->size() - 1, 0, (*cps->begin()).size() - 1);
	TColStd_Array1OfReal UKnots(0, uknots.size() - 1);
	TColStd_Array1OfReal VKnots(0, vknots.size() - 1);
	TColStd_Array1OfInteger UMults(0, umults.size() - 1);
	TColStd_Array1OfInteger VMults(0, vmults.size() - 1);
	Standard_Integer UDegree = l->UDegree();
	Standard_Integer VDegree = l->VDegree();

	int i = 0, j;
	for (IfcTemplatedEntityListList<IfcSchema::IfcCartesianPoint>::outer_it it = cps->begin(); it != cps->end(); ++it, ++i) {
		j = 0;
		for (IfcTemplatedEntityListList<IfcSchema::IfcCartesianPoint>::inner_it jt = (*it).begin(); jt != (*it).end(); ++jt, ++j) {
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

	face = BRepBuilderAPI_MakeFace(surf, getValue(GV_PRECISION));

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPlane* l, TopoDS_Shape& face) {
	gp_Pln pln;
	convert(l, pln);
	Handle_Geom_Surface surf = new Geom_Plane(pln);
	face = BRepBuilderAPI_MakeFace(surf, getValue(GV_PRECISION));
	return true;
}

#endif