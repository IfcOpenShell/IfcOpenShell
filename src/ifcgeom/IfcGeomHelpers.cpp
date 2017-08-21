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

// Helper functions (re)set gp_(G)Trsf(2d) forms explicitly to 'Identity'
// so that it can be easily identified in the IfcMappedItem processing

// For axis placements detect equality early in order for the
// relatively computionaly expensive gp_Trsf calculation to be skipped
template <typename T>
bool axis_equal(const T& a, const T& b, double tolerance);
template <>
bool axis_equal(const gp_Ax3& a, const gp_Ax3& b, double tolerance) {
	if (!a.Location().IsEqual(b.Location(), tolerance)) return false;
	// Note that the tolerance below is angular, above is linear. Since architectural
	// objects are about 1m'ish in scale, it should be somewhat equivalent. Besides,
	// this is mostly a filter for NULL or default values in the placements.
	if (!a.Direction().IsEqual(b.Direction(), tolerance)) return false;
	if (!a.XDirection().IsEqual(b.XDirection(), tolerance)) return false;
	if (!a.YDirection().IsEqual(b.YDirection(), tolerance)) return false;
	return true;
}

bool axis_equal(const gp_Ax2d& a, const gp_Ax2d& b, double tolerance) {
	if (!a.Location().IsEqual(b.Location(), tolerance)) return false;
	if (!a.Direction().IsEqual(b.Direction(), tolerance)) return false;
	return true;
}

template <typename T> struct dimension_count {};
template <>           struct dimension_count <gp_Trsf2d > { static const int n = 2; };
template <>           struct dimension_count <gp_GTrsf2d> { static const int n = 2; };
template <>           struct dimension_count < gp_Trsf  > { static const int n = 3; };
template <>           struct dimension_count < gp_GTrsf > { static const int n = 3; };

template <typename T>
bool is_identity(const T& t, double tolerance) {
	// Note the {1, n+1} range due to Open Cascade's 1-based indexing
	// Note the {1, n+2} range due to the translation part of the matrix
	for (int i = 1; i < dimension_count<T>::n + 2; ++i) {
		for (int j = 1; j < dimension_count<T>::n + 1; ++j) {
			const double iden_value = i == j ? 1. : 0.;
			const double trsf_value = t.Value(j, i);
			if (fabs(trsf_value - iden_value) > tolerance) {
				return false;
			}
		}
	}
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCartesianPoint* l, gp_Pnt& point) {
	IN_CACHE(IfcCartesianPoint,l,gp_Pnt,point)
	std::vector<double> xyz = l->Coordinates();
	point = gp_Pnt(
		xyz.size()     ? (xyz[0]*getValue(GV_LENGTH_UNIT)) : 0.0f,
		xyz.size() > 1 ? (xyz[1]*getValue(GV_LENGTH_UNIT)) : 0.0f,
		xyz.size() > 2 ? (xyz[2]*getValue(GV_LENGTH_UNIT)) : 0.0f
	);
	CACHE(IfcCartesianPoint,l,point)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcDirection* l, gp_Dir& dir) {
	IN_CACHE(IfcDirection,l,gp_Dir,dir)
	std::vector<double> xyz = l->DirectionRatios();
	dir = gp_Dir(
		xyz.size()     ? xyz[0] : 0.0f,
		xyz.size() > 1 ? xyz[1] : 0.0f,
		xyz.size() > 2 ? xyz[2] : 0.0f
	);
	CACHE(IfcDirection,l,dir)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcVector* l, gp_Vec& v) {
	IN_CACHE(IfcVector,l,gp_Vec,v)
	gp_Dir d;
	IfcGeom::Kernel::convert(l->Orientation(),d);
	v = l->Magnitude() * getValue(GV_LENGTH_UNIT) * d;
	CACHE(IfcVector,l,v)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcAxis2Placement3D* l, gp_Trsf& trsf) {
	IN_CACHE(IfcAxis2Placement3D,l,gp_Trsf,trsf)
	gp_Pnt o;gp_Dir axis = gp_Dir(0,0,1);gp_Dir refDirection;
	IfcGeom::Kernel::convert(l->Location(),o);
	bool hasRef = l->hasRefDirection();
	if ( l->hasAxis() ) IfcGeom::Kernel::convert(l->Axis(),axis);
	if ( hasRef ) IfcGeom::Kernel::convert(l->RefDirection(),refDirection);
	gp_Ax3 ax3;
	if ( hasRef ) ax3 = gp_Ax3(o,axis,refDirection);
	else ax3 = gp_Ax3(o,axis);

	if (!axis_equal(ax3, (gp_Ax3) gp::XOY(), getValue(GV_PRECISION))) {
		trsf.SetTransformation(ax3, gp::XOY());
	}
	
	CACHE(IfcAxis2Placement3D,l,trsf)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcAxis1Placement* l, gp_Ax1& ax) {
	IN_CACHE(IfcAxis1Placement,l,gp_Ax1,ax)
	gp_Pnt o;gp_Dir axis = gp_Dir(0,0,1);
	IfcGeom::Kernel::convert(l->Location(),o);
	if ( l->hasAxis() ) IfcGeom::Kernel::convert(l->Axis(), axis);
	ax = gp_Ax1(o, axis);
	CACHE(IfcAxis1Placement,l,ax)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCartesianTransformationOperator3D* l, gp_Trsf& trsf) {
	IN_CACHE(IfcCartesianTransformationOperator3D,l,gp_Trsf,trsf)
	gp_Pnt origin;
	IfcGeom::Kernel::convert(l->LocalOrigin(),origin);
	gp_Dir axis1 (1.,0.,0.);
	gp_Dir axis2 (0.,1.,0.);
	gp_Dir axis3 (0.,0.,1.);
	if ( l->hasAxis1() ) IfcGeom::Kernel::convert(l->Axis1(),axis1);
	if ( l->hasAxis2() ) IfcGeom::Kernel::convert(l->Axis2(),axis2);
	if ( l->hasAxis3() ) IfcGeom::Kernel::convert(l->Axis3(),axis3);
	gp_Ax3 ax3 (origin,axis3,axis1);
	if ( axis2.Dot(ax3.YDirection()) < 0 ) ax3.YReverse();
	
	if (!axis_equal(ax3, (gp_Ax3) gp::XOY(), getValue(GV_PRECISION))) {
		trsf.SetTransformation(ax3);
		trsf.Invert();
	}
	
	if (l->hasScale() && !ALMOST_THE_SAME(l->Scale(), 1.)) {
		trsf.SetScaleFactor(l->Scale());
	}

	CACHE(IfcCartesianTransformationOperator3D,l,trsf)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCartesianTransformationOperator2D* l, gp_Trsf2d& trsf) {
	IN_CACHE(IfcCartesianTransformationOperator2D,l,gp_Trsf2d,trsf)

	gp_Pnt origin;
	gp_Dir axis1 (1.,0.,0.);
	gp_Dir axis2 (0.,1.,0.);
	
	IfcGeom::Kernel::convert(l->LocalOrigin(),origin);
	if ( l->hasAxis1() ) IfcGeom::Kernel::convert(l->Axis1(),axis1);
	if ( l->hasAxis2() ) IfcGeom::Kernel::convert(l->Axis2(),axis2);
	
	const gp_Pnt2d origin2d(origin.X(), origin.Y());
	const gp_Dir2d axis12d(axis1.X(), axis1.Y());
	const gp_Dir2d axis22d(axis2.X(), axis2.Y());

	// A better match to represent the IfcCartesianTransformationOperator2D would
	// be the gp_Ax22d, but to my knowledge no easy way exists to convert it into
	// a gp_Trsf2d. Easiest would probably be to simply update the underlying
	// gp_Mat2d directly.
	
	const gp_Ax2d ax2d (origin2d, axis12d);
	trsf.SetTransformation(ax2d);
	
	if ( ax2d.Direction().Rotated(M_PI / 2.).Dot(axis22d) < 0. ) {
		gp_Trsf2d mirror; mirror.SetMirror(ax2d);
		trsf.Multiply(mirror);
	}

	trsf.Invert();
	if ( l->hasScale() && !ALMOST_THE_SAME(l->Scale(), 1.) ) trsf.SetScaleFactor(l->Scale());

	if (is_identity(trsf, getValue(GV_PRECISION))) {
		trsf = gp_Trsf2d();
	}

	CACHE(IfcCartesianTransformationOperator2D,l,trsf)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCartesianTransformationOperator3DnonUniform* l, gp_GTrsf& gtrsf) {
	IN_CACHE(IfcCartesianTransformationOperator3DnonUniform,l,gp_GTrsf,gtrsf)
	gp_Trsf trsf;
	gp_Pnt origin;
	IfcGeom::Kernel::convert(l->LocalOrigin(),origin);
	gp_Dir axis1 (1.,0.,0.);
	gp_Dir axis2 (0.,1.,0.);
	gp_Dir axis3 (0.,0.,1.);
	if ( l->hasAxis1() ) IfcGeom::Kernel::convert(l->Axis1(),axis1);
	if ( l->hasAxis2() ) IfcGeom::Kernel::convert(l->Axis2(),axis2);
	if ( l->hasAxis3() ) IfcGeom::Kernel::convert(l->Axis3(),axis3);
	gp_Ax3 ax3 (origin,axis3,axis1);
	if ( axis2.Dot(ax3.YDirection()) < 0 ) ax3.YReverse();
	trsf.SetTransformation(ax3);
	trsf.Invert();
	const double scale1 = l->hasScale() ? l->Scale() : 1.0f;
	const double scale2 = l->hasScale2() ? l->Scale2() : scale1;
	const double scale3 = l->hasScale3() ? l->Scale3() : scale1;
	gtrsf = gp_GTrsf();
	gtrsf.SetValue(1,1,scale1);
	gtrsf.SetValue(2,2,scale2);
	gtrsf.SetValue(3,3,scale3);
	gtrsf.PreMultiply(trsf);

	if (is_identity(gtrsf, getValue(GV_PRECISION))) {
		gtrsf = gp_GTrsf();
	}

	CACHE(IfcCartesianTransformationOperator3DnonUniform,l,gtrsf)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCartesianTransformationOperator2DnonUniform* l, gp_GTrsf2d& gtrsf) {
	IN_CACHE(IfcCartesianTransformationOperator2DnonUniform,l,gp_GTrsf2d,gtrsf)

	gp_Trsf2d trsf;
	gp_Pnt origin;
	gp_Dir axis1 (1.,0.,0.);
	gp_Dir axis2 (0.,1.,0.);
	
	IfcGeom::Kernel::convert(l->LocalOrigin(),origin);
	if ( l->hasAxis1() ) IfcGeom::Kernel::convert(l->Axis1(),axis1);
	if ( l->hasAxis2() ) IfcGeom::Kernel::convert(l->Axis2(),axis2);

	const gp_Pnt2d origin2d(origin.X(), origin.Y());
	const gp_Dir2d axis12d(axis1.X(), axis1.Y());
	const gp_Dir2d axis22d(axis2.X(), axis2.Y());
	
	const gp_Ax2d ax2d (origin2d, axis12d);
	trsf.SetTransformation(ax2d);
	
	if ( ax2d.Direction().Rotated(M_PI / 2.).Dot(axis22d) < 0. ) {
		gp_Trsf2d mirror; mirror.SetMirror(ax2d);
		trsf.Multiply(mirror);
	}

	trsf.Invert();
	
	const double scale1 = l->hasScale() ? l->Scale() : 1.0f;
	const double scale2 = l->hasScale2() ? l->Scale2() : scale1;
	gtrsf = gp_GTrsf2d();
	gtrsf.SetValue(1,1,scale1);
	gtrsf.SetValue(2,2,scale2);
	gtrsf.Multiply(trsf);

	if (is_identity(gtrsf, getValue(GV_PRECISION))) {
		gtrsf = gp_GTrsf2d();
	}

	CACHE(IfcCartesianTransformationOperator2DnonUniform,l,gtrsf)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPlane* pln, gp_Pln& plane) {
	IN_CACHE(IfcPlane,pln,gp_Pln,plane)
	IfcSchema::IfcAxis2Placement3D* l = pln->Position();
	gp_Pnt o;gp_Dir axis = gp_Dir(0,0,1);gp_Dir refDirection;
	IfcGeom::Kernel::convert(l->Location(),o);
	bool hasRef = l->hasRefDirection();
	if ( l->hasAxis() ) IfcGeom::Kernel::convert(l->Axis(),axis);
	if ( hasRef ) IfcGeom::Kernel::convert(l->RefDirection(),refDirection);
	gp_Ax3 ax3;
	if ( hasRef ) ax3 = gp_Ax3(o,axis,refDirection);
	else ax3 = gp_Ax3(o,axis);
	plane = gp_Pln(ax3);
	CACHE(IfcPlane,pln,plane)
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcAxis2Placement2D* l, gp_Trsf2d& trsf) {
	IN_CACHE(IfcAxis2Placement2D,l,gp_Trsf2d,trsf)
	gp_Pnt P; gp_Dir V (1,0,0);
	IfcGeom::Kernel::convert(l->Location(),P);
	if ( l->hasRefDirection() )
		IfcGeom::Kernel::convert(l->RefDirection(),V);

	gp_Ax2d axis(gp_Pnt2d(P.X(),P.Y()), gp_Dir2d(V.X(),V.Y()));
	
	if (!axis_equal(axis, gp_Ax2d(), getValue(GV_PRECISION))) {
		trsf.SetTransformation(axis, gp_Ax2d());
	}

	CACHE(IfcAxis2Placement2D,l,trsf)
	return true;
}

void IfcGeom::Kernel::set_conversion_placement_rel_to(IfcSchema::Type::Enum type) {
	placement_rel_to = type;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcObjectPlacement* l, gp_Trsf& trsf) {
	IN_CACHE(IfcObjectPlacement,l,gp_Trsf,trsf)
	if ( ! l->is(IfcSchema::Type::IfcLocalPlacement) ) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported IfcObjectPlacement:", l->entity);
		return false; 		
	}
	IfcSchema::IfcLocalPlacement* current = (IfcSchema::IfcLocalPlacement*)l;
	for (;;) {
		gp_Trsf trsf2;
		IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
		if ( relplacement->is(IfcSchema::Type::IfcAxis2Placement3D) ) {
			IfcGeom::Kernel::convert((IfcSchema::IfcAxis2Placement3D*)relplacement,trsf2);
			trsf.PreMultiply(trsf2);
		}
		if ( current->hasPlacementRelTo() ) {
			IfcSchema::IfcObjectPlacement* parent = current->PlacementRelTo();
			IfcSchema::IfcProduct::list::ptr parentPlaces = parent->PlacesObject();
			bool parentPlacesType = false;
			for ( IfcSchema::IfcProduct::list::it iter = parentPlaces->begin();
				  iter != parentPlaces->end(); ++iter) {
				if ( (*iter)->is(placement_rel_to) ) parentPlacesType = true;
			}

			if ( parentPlacesType ) break;
			else if ( parent->is(IfcSchema::Type::IfcLocalPlacement) )
				current = (IfcSchema::IfcLocalPlacement*)current->PlacementRelTo();
			else break;
		} else break;
	}
	CACHE(IfcObjectPlacement,l,trsf)
	return true;
}
