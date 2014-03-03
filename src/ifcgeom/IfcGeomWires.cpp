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

#define _USE_MATH_DEFINES
#include <cmath>

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

bool IfcGeom::convert(const IfcSchema::IfcCompositeCurve::ptr l, TopoDS_Wire& wire) {
	if ( IfcGeom::GetValue(GV_PLANEANGLE_UNIT)<0 ) {
		Logger::Message(Logger::LOG_WARNING,"Creating a composite curve without unit information:",l->entity);

		// Temporarily pretend we do have unit information
		IfcGeom::SetValue(GV_PLANEANGLE_UNIT,1.0);
		
		bool succes_radians = false;
        bool succes_degrees = false;
        bool use_radians = false;
        bool use_degrees = false;

		// First try radians
		TopoDS_Wire wire_radians, wire_degrees;
        try {
		    succes_radians = IfcGeom::convert(l,wire_radians);
        } catch (...) {}

		// Now try degrees
		IfcGeom::SetValue(GV_PLANEANGLE_UNIT,0.0174532925199433);
        try {
		    succes_degrees = IfcGeom::convert(l,wire_degrees);
        } catch (...) {}

		// Restore to unknown unit state
		IfcGeom::SetValue(GV_PLANEANGLE_UNIT,-1.0);

		if ( succes_degrees && ! succes_radians ) {
			use_degrees = true;
		} else if ( succes_radians && ! succes_degrees ) {
			use_radians = true;
		} else if ( succes_radians && succes_degrees ) {
			if ( wire_degrees.Closed() && ! wire_radians.Closed() ) {
				use_degrees = true;
			} else if ( wire_radians.Closed() && ! wire_degrees.Closed() ) {
				use_radians = true;
			} else {
				// No heuristic left to prefer the one over the other,
				// apparently both variants are equally succesful.
				// The curve might be composed of only straight segments.
				// Let's go with the wire created using radians as that
				// at least is a SI unit.
				use_radians = true;
			}
		}

		if ( use_radians ) {
			Logger::Message(Logger::LOG_NOTICE,"Used radians to create composite curve");
            wire = wire_radians;
		} else if ( use_degrees ) {
			Logger::Message(Logger::LOG_NOTICE,"Used degrees to create composite curve");
            wire = wire_degrees;
		}

		return use_radians || use_degrees;
	}
	IfcSchema::IfcCompositeCurveSegment::list segments = l->Segments();
	BRepBuilderAPI_MakeWire w;
	//TopoDS_Vertex last_vertex;
	for( IfcSchema::IfcCompositeCurveSegment::it it = segments->begin(); it != segments->end(); ++ it ) {
		const IfcSchema::IfcCurve::ptr curve = (*it)->ParentCurve();
		TopoDS_Wire wire2;
		if ( ! IfcGeom::convert_wire(curve,wire2) ) {
			Logger::Message(Logger::LOG_ERROR,"Failed to convert curve:",curve->entity);
			continue;
		}
		if ( ! (*it)->SameSense() ) wire2.Reverse();
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire2, GetValue(GV_WIRE_CREATION_TOLERANCE), TopAbs_WIRE);
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
			Logger::Message(Logger::LOG_ERROR,"Failed to join curve segments:",l->entity);
			return false;
		}
	}
	wire = w.Wire();
	return true;
}
bool IfcGeom::convert(const IfcSchema::IfcTrimmedCurve::ptr l, TopoDS_Wire& wire) {
	IfcSchema::IfcCurve::ptr basis_curve = l->BasisCurve();
	bool isConic = basis_curve->is(IfcSchema::Type::IfcConic);
	double parameterFactor = isConic ? IfcGeom::GetValue(GV_PLANEANGLE_UNIT) : IfcGeom::GetValue(GV_LENGTH_UNIT);
	Handle(Geom_Curve) curve;
	if ( ! IfcGeom::convert_curve(basis_curve,curve) ) return false;
	bool trim_cartesian = l->MasterRepresentation() == IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN;
	IfcUtil::IfcAbstractSelect::list trims1 = l->Trim1();
	IfcUtil::IfcAbstractSelect::list trims2 = l->Trim2();
	bool trimmed1 = false;
	bool trimmed2 = false;
	unsigned sense_agreement = l->SenseAgreement() ? 0 : 1;
	double flts[2];
	gp_Pnt pnts[2];
	bool has_flts[2] = {false,false};
	bool has_pnts[2] = {false,false};
	BRepBuilderAPI_MakeWire w;
	for ( IfcUtil::IfcAbstractSelect::it it = trims1->begin(); it != trims1->end(); it ++ ) {
		const IfcUtil::IfcAbstractSelect::ptr i = *it;
		if ( i->is(IfcSchema::Type::IfcCartesianPoint) ) {
			IfcGeom::convert(reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,IfcSchema::IfcCartesianPoint>(i), pnts[sense_agreement] );
			has_pnts[sense_agreement] = true;
		} else if ( i->is(IfcSchema::Type::IfcParameterValue) ) {
			const double value = *reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,IfcUtil::IfcArgumentSelect>(i)->wrappedValue();
			flts[sense_agreement] = value * parameterFactor;
			has_flts[sense_agreement] = true;
		}
	}
	for ( IfcUtil::IfcAbstractSelect::it it = trims2->begin(); it != trims2->end(); it ++ ) {
		const IfcUtil::IfcAbstractSelect::ptr i = *it;
		if ( i->is(IfcSchema::Type::IfcCartesianPoint) ) {
			IfcGeom::convert(reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,IfcSchema::IfcCartesianPoint>(i), pnts[1-sense_agreement] );
			has_pnts[1-sense_agreement] = true;
		} else if ( i->is(IfcSchema::Type::IfcParameterValue) ) {
			const double value = *reinterpret_pointer_cast<IfcUtil::IfcAbstractSelect,IfcUtil::IfcArgumentSelect>(i)->wrappedValue();
			flts[1-sense_agreement] = value * parameterFactor;
			has_flts[1-sense_agreement] = true;
		}
	}
	trim_cartesian &= has_pnts[0] && has_pnts[1];
	bool trim_cartesian_failed = !trim_cartesian;
	if ( trim_cartesian ) {
		if ( pnts[0].Distance(pnts[1]) < GetValue(GV_WIRE_CREATION_TOLERANCE) ) {
			Logger::Message(Logger::LOG_WARNING,"Skipping segment with length below tolerance level:",l->entity);
			return false;
		}
		ShapeFix_ShapeTolerance FTol;
		TopoDS_Vertex v1 = BRepBuilderAPI_MakeVertex(pnts[0]);
		TopoDS_Vertex v2 = BRepBuilderAPI_MakeVertex(pnts[1]);
		FTol.SetTolerance(v1, GetValue(GV_WIRE_CREATION_TOLERANCE), TopAbs_VERTEX);
		FTol.SetTolerance(v2, GetValue(GV_WIRE_CREATION_TOLERANCE), TopAbs_VERTEX);
		BRepBuilderAPI_MakeEdge e (curve,v1,v2);
		if ( ! e.IsDone() ) {
			BRepBuilderAPI_EdgeError err = e.Error();
			if ( err == BRepBuilderAPI_PointProjectionFailed ) {
				Logger::Message(Logger::LOG_WARNING,"Point projection failed for:",l->entity);
				trim_cartesian_failed = true;
			}
		} else {
			w.Add(e.Edge());
		}
	}
	if ( (!trim_cartesian || trim_cartesian_failed) && (has_flts[0] && has_flts[1]) ) {
		// The Geom_Line is constructed from a gp_Pnt and gp_Dir, whereas the IfcLine
		// is defined by an IfcCartesianPoint and an IfcVector with Magnitude. Because
		// the vector is normalised when passed to Geom_Line constructor the magnitude
		// needs to be factored in with the IfcParameterValue here.
		if ( basis_curve->is(IfcSchema::Type::IfcLine) ) {
			IfcSchema::IfcLine* line = static_cast<IfcSchema::IfcLine*>(basis_curve);
			const double magnitude = line->Dir()->Magnitude();
			flts[0] *= magnitude; flts[1] *= magnitude;
		}
		if ( basis_curve->is(IfcSchema::Type::IfcEllipse) ) {
			IfcSchema::IfcEllipse* ellipse = static_cast<IfcSchema::IfcEllipse*>(basis_curve);
			double x = ellipse->SemiAxis1() * IfcGeom::GetValue(GV_LENGTH_UNIT);
			double y = ellipse->SemiAxis2() * IfcGeom::GetValue(GV_LENGTH_UNIT);
			const bool rotated = y > x;
			if (rotated) {
				flts[0] -= M_PI / 2.;
				flts[1] -= M_PI / 2.;
			}
		}
		if ( isConic && ALMOST_THE_SAME(fmod(flts[1]-flts[0],(double)(M_PI*2.0)),0.0f) ) {
			w.Add(BRepBuilderAPI_MakeEdge(curve));
		} else {
			BRepBuilderAPI_MakeEdge e (curve,flts[0],flts[1]);
			w.Add(e.Edge());
		}			
	} else if ( trim_cartesian_failed && (has_pnts[0] && has_pnts[1]) ) {
		w.Add(BRepBuilderAPI_MakeEdge(pnts[0],pnts[1]));
	}
	if ( w.IsDone() ) {
		wire = w.Wire();
		return true;
	} else {
		return false;
	}
}
bool IfcGeom::convert(const IfcSchema::IfcPolyline::ptr l, TopoDS_Wire& result) {
	IfcSchema::IfcCartesianPoint::list points = l->Points();

	BRepBuilderAPI_MakeWire w;
	gp_Pnt P1;gp_Pnt P2;
	for( IfcSchema::IfcCartesianPoint::it it = points->begin(); it != points->end(); ++ it ) {
		IfcGeom::convert(*it,P2);
		if ( it != points->begin() && ( !P1.IsEqual(P2,GetValue(GV_POINT_EQUALITY_TOLERANCE)) ) )
			w.Add(BRepBuilderAPI_MakeEdge(P1,P2));
		P1 = P2;
	}

	result = w.Wire();
	return true;
}
bool IfcGeom::convert(const IfcSchema::IfcPolyLoop::ptr l, TopoDS_Wire& result) {
	IfcSchema::IfcCartesianPoint::list points = l->Polygon();

	BRepBuilderAPI_MakeWire w;
	gp_Pnt P1;gp_Pnt P2;gp_Pnt F;
	int count = 0;
	for( IfcSchema::IfcCartesianPoint::it it = points->begin(); it != points->end(); ++ it ) {
		IfcGeom::convert(*it,P2);
		if ( it != points->begin() && ( !P1.IsEqual(P2,GetValue(GV_POINT_EQUALITY_TOLERANCE)) ) ) {
			w.Add(BRepBuilderAPI_MakeEdge(P1,P2));
			count ++;
		} else if ( ! count ) F = P2;		
		P1 = P2;
	}
	if ( !P1.IsEqual(F,GetValue(GV_POINT_EQUALITY_TOLERANCE)) ) {
		w.Add(BRepBuilderAPI_MakeEdge(P1,F));
		count ++;
	}
	if ( count < 3 ) return false;

	result = w.Wire();
	return true;
}