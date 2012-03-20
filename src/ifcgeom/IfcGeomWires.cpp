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

#include <BRep_Tool.hxx>

#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::convert(const Ifc2x3::IfcCompositeCurve::ptr l, TopoDS_Wire& wire) {
	if ( ! Ifc::hasPlaneAngleUnit ) {
		Ifc::LogMessage("Warning","Creating a composite curve without unit information:",l->entity);
		Ifc::hasPlaneAngleUnit = true;
		// First try radians
		Ifc::PlaneAngleUnit = 1.0f;
		bool succes_radians = IfcGeom::convert(l,wire);
		bool succes_degrees;
		if ( succes_radians ) {
			Ifc::LogMessage("Notice","Used radians to create composite curve");
		} else {
			// Now try degrees
			Ifc::PlaneAngleUnit = 0.0174532925199433f;
			succes_degrees = IfcGeom::convert(l,wire);
			if ( succes_degrees ) {
				Ifc::LogMessage("Notice","Used degrees to create composite curve");
			}
			// Restore to radians
			Ifc::PlaneAngleUnit = 1.0f;
		}
		Ifc::hasPlaneAngleUnit = false;
		return succes_radians || succes_degrees;
	}
	Ifc2x3::IfcCompositeCurveSegment::list segments = l->Segments();
	BRepBuilderAPI_MakeWire w;
	//TopoDS_Vertex last_vertex;
	for( Ifc2x3::IfcCompositeCurveSegment::it it = segments->begin(); it != segments->end(); ++ it ) {
		const Ifc2x3::IfcCurve::ptr curve = (*it)->ParentCurve();
		TopoDS_Wire wire2;
		if ( ! IfcGeom::convert_wire(curve,wire2) ) {
			Ifc::LogMessage("Error","Failed to convert curve:",curve->entity);
			continue;
		}
		if ( ! (*it)->SameSense() ) wire2.Reverse();
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire2, WIRE_CREATION_TOLERANCE, TopAbs_WIRE);
		/*if ( it != segments->begin() ) {
			TopExp_Explorer exp (wire2,TopAbs_VERTEX);
			const TopoDS_Vertex& first_vertex = TopoDS::Vertex(exp.Current());
			gp_Pnt first = BRep_Tool::Pnt(first_vertex);
			gp_Pnt last = BRep_Tool::Pnt(last_vertex);
			Standard_Real distance = first.Distance(last);
			if ( distance > ALMOST_ZERO ) {
				w.Add( BRepBuilderAPI_MakeEdge( last_vertex, first_vertex ) );
			}
		}*/
		w.Add(wire2);
		//last_vertex = w.Vertex();
		if ( w.Error() != BRepBuilderAPI_WireDone ) {
			Ifc::LogMessage("Error","Failed to join curve segments:",l->entity);
			return false;
		}
	}
	wire = w.Wire();
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcTrimmedCurve::ptr l, TopoDS_Wire& wire) {
	Ifc2x3::IfcCurve::ptr basis_curve = l->BasisCurve();
	bool isConic = basis_curve->is(Ifc2x3::Type::IfcConic);
	double parameterFactor = isConic ? Ifc::PlaneAngleUnit : Ifc::LengthUnit;
	Handle(Geom_Curve) curve;
	if ( ! IfcGeom::convert_curve(basis_curve,curve) ) return false;
	bool trim_cartesian = l->MasterRepresentation() == Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN;
	IfcUtil::IfcAbstractSelect::list trims1 = l->Trim1();
	IfcUtil::IfcAbstractSelect::list trims2 = l->Trim2();
	bool trimmed1 = false;
	bool trimmed2 = false;
	bool sense_agreement = l->SenseAgreement();
	double flt1;
	gp_Pnt pnt1;
	BRepBuilderAPI_MakeWire w;
	for ( IfcUtil::IfcAbstractSelect::it it = trims1->begin(); it != trims1->end(); it ++ ) {
		const IfcUtil::IfcAbstractSelect::ptr i = *it;
		if ( i->is(Ifc2x3::Type::IfcCartesianPoint) && trim_cartesian ) {
			IfcGeom::convert(reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,Ifc2x3::IfcCartesianPoint>(i), pnt1 );
			trimmed1 = true;
		} else if ( i->is(Ifc2x3::Type::IfcParameterValue) && !trim_cartesian ) {
			const double value = *reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,IfcUtil::IfcArgumentSelect>(i)->wrappedValue();
			flt1 = value * parameterFactor;
			trimmed1 = true;
		}
	}
	for ( IfcUtil::IfcAbstractSelect::it it = trims2->begin(); it != trims2->end(); it ++ ) {
		const IfcUtil::IfcAbstractSelect::ptr i = *it;
		if ( i->is(Ifc2x3::Type::IfcCartesianPoint) && trim_cartesian && trimmed1 ) {
			gp_Pnt pnt2;
			IfcGeom::convert(reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,Ifc2x3::IfcCartesianPoint>(i), pnt2 );
			BRepBuilderAPI_MakeEdge e (curve,sense_agreement ? pnt1 : pnt2,sense_agreement ? pnt2 : pnt1);
			if ( ! e.IsDone() ) {
				BRepBuilderAPI_EdgeError err = e.Error();
				if ( err == BRepBuilderAPI_PointProjectionFailed ) {
					w.Add(BRepBuilderAPI_MakeEdge(sense_agreement ? pnt1 : pnt2,sense_agreement ? pnt2 : pnt1));
					Ifc::LogMessage("Warning","Point projection failed for:",l->entity);
				}
			} else {
				w.Add(e.Edge());
			}
			trimmed2 = true;
			break;
		} else if ( i->is(Ifc2x3::Type::IfcParameterValue) && !trim_cartesian && trimmed1 ) {
			const double value = *reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,IfcUtil::IfcArgumentSelect>(i)->wrappedValue();
			double flt2 = value * parameterFactor;
			if ( isConic && ALMOST_THE_SAME(fmod(flt2-flt1,(double)(PI*2.0)),0.0f) ) {
				w.Add(BRepBuilderAPI_MakeEdge(curve));
			} else {
				BRepBuilderAPI_MakeEdge e (curve,sense_agreement ? flt1 : flt2,sense_agreement ? flt2 : flt1);
				w.Add(e.Edge());
			}
			trimmed2 = true;
			break;
		}
	}
	if ( trimmed2 ) wire = w.Wire();
	return trimmed2;
}
bool IfcGeom::convert(const Ifc2x3::IfcPolyline::ptr l, TopoDS_Wire& result) {
	Ifc2x3::IfcCartesianPoint::list points = l->Points();

	BRepBuilderAPI_MakeWire w;
	gp_Pnt P1;gp_Pnt P2;
	for( Ifc2x3::IfcCartesianPoint::it it = points->begin(); it != points->end(); ++ it ) {
		IfcGeom::convert(*it,P2);
		if ( it != points->begin() && ( !P1.IsEqual(P2,POINT_EQUALITY_TOLERANCE) ) )
			w.Add(BRepBuilderAPI_MakeEdge(P1,P2));
		P1 = P2;
	}

	result = w.Wire();
	return true;
}
bool IfcGeom::convert(const Ifc2x3::IfcPolyLoop::ptr l, TopoDS_Wire& result) {
	Ifc2x3::IfcCartesianPoint::list points = l->Polygon();

	BRepBuilderAPI_MakeWire w;
	gp_Pnt P1;gp_Pnt P2;gp_Pnt F;
	int count = 0;
	for( Ifc2x3::IfcCartesianPoint::it it = points->begin(); it != points->end(); ++ it ) {
		IfcGeom::convert(*it,P2);
		if ( it != points->begin() && ( !P1.IsEqual(P2,POINT_EQUALITY_TOLERANCE) ) ) {
			w.Add(BRepBuilderAPI_MakeEdge(P1,P2));
			count ++;
		} else if ( ! count ) F = P2;		
		P1 = P2;
	}
	if ( !P1.IsEqual(F,POINT_EQUALITY_TOLERANCE) ) {
		w.Add(BRepBuilderAPI_MakeEdge(P1,F));
		count ++;
	}
	if ( count < 3 ) return false;

	result = w.Wire();
	return true;
}