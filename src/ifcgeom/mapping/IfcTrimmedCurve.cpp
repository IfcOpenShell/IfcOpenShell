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

#include <cmath>
#include <gp_Pnt.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopExp.hxx>
#include <BRep_Tool.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <BRepAdaptor_CompCurve.hxx>
#include <Standard_Version.hxx>

#if OCC_VERSION_HEX < 0x70600
#include <BRepAdaptor_HCompCurve.hxx>
#endif

#include <Approx_Curve3d.hxx>
#include "../ifcgeom/IfcGeom.h"

#include "../ifcgeom_schema_agnostic/wire_builder.h"

#define _USE_MATH_DEFINES

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTrimmedCurve* l, TopoDS_Wire& wire) {
	IfcSchema::IfcCurve* basis_curve = l->BasisCurve();
	bool isConic = basis_curve->declaration().is(IfcSchema::IfcConic::Class());
	double parameterFactor = isConic ? getValue(GV_PLANEANGLE_UNIT) : getValue(GV_LENGTH_UNIT);
	
	Handle(Geom_Curve) curve;
	if (shape_type(basis_curve) == ST_CURVE) {
		if (!convert_curve(basis_curve, curve)) return false;
	} else if (shape_type(basis_curve) == ST_WIRE) {
		Logger::Warning("Approximating BasisCurve due to possible discontinuities", l);
		TopoDS_Wire w;
		if (!convert_wire(basis_curve, w)) return false;
#if OCC_VERSION_HEX < 0x70600
		BRepAdaptor_CompCurve cc(w, true);
		Handle(Adaptor3d_HCurve) hcc = Handle(Adaptor3d_HCurve)(new BRepAdaptor_HCompCurve(cc));
#else
		auto hcc = new BRepAdaptor_CompCurve(w, true);
#endif
		// @todo, arbitrary numbers here, note they cannot be too high as contiguous memory is allocated based on them.
		Approx_Curve3d approx(hcc, getValue(GV_PRECISION), GeomAbs_C0, 10, 10);
		curve = approx.Curve();
	} else {
		Logger::Error("Unknown BasisCurve", l);
		return false;
	}
	
	bool trim_cartesian = l->MasterRepresentation() != IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER;
	aggregate_of_instance::ptr trims1 = l->Trim1();
	aggregate_of_instance::ptr trims2 = l->Trim2();
	
	unsigned sense_agreement = l->SenseAgreement() ? 0 : 1;
	double flts[2];
	gp_Pnt pnts[2];
	bool has_flts[2] = {false,false};
	bool has_pnts[2] = {false,false};
	
	TopoDS_Edge e;

	for ( aggregate_of_instance::it it = trims1->begin(); it != trims1->end(); it ++ ) {
		IfcUtil::IfcBaseClass* i = *it;
		if ( i->declaration().is(IfcSchema::IfcCartesianPoint::Class()) ) {
			IfcGeom::Kernel::convert((IfcSchema::IfcCartesianPoint*)i, pnts[sense_agreement] );
			has_pnts[sense_agreement] = true;
		} else if ( i->declaration().is(IfcSchema::IfcParameterValue::Class()) ) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[sense_agreement] = value * parameterFactor;
			has_flts[sense_agreement] = true;
		}
	}

	for ( aggregate_of_instance::it it = trims2->begin(); it != trims2->end(); it ++ ) {
		IfcUtil::IfcBaseClass* i = *it;
		if ( i->declaration().is(IfcSchema::IfcCartesianPoint::Class()) ) {
			IfcGeom::Kernel::convert((IfcSchema::IfcCartesianPoint*)i, pnts[1-sense_agreement] );
			has_pnts[1-sense_agreement] = true;
		} else if ( i->declaration().is(IfcSchema::IfcParameterValue::Class()) ) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[1-sense_agreement] = value * parameterFactor;
			has_flts[1-sense_agreement] = true;
		}
	}

	trim_cartesian &= has_pnts[0] && has_pnts[1];
	bool trim_cartesian_failed = !trim_cartesian;
	if ( trim_cartesian ) {
		if ( pnts[0].Distance(pnts[1]) < 2 * getValue(GV_PRECISION) ) {
			Logger::Message(Logger::LOG_WARNING,"Skipping segment with length below tolerance level:",l);
			return false;
		}
		ShapeFix_ShapeTolerance FTol;
		TopoDS_Vertex v1 = BRepBuilderAPI_MakeVertex(pnts[0]);
		TopoDS_Vertex v2 = BRepBuilderAPI_MakeVertex(pnts[1]);
		FTol.SetTolerance(v1, getValue(GV_PRECISION), TopAbs_VERTEX);
		FTol.SetTolerance(v2, getValue(GV_PRECISION), TopAbs_VERTEX);
		BRepBuilderAPI_MakeEdge me (curve,v1,v2);
		if (!me.IsDone()) {
			BRepBuilderAPI_EdgeError err = me.Error();
			if ( err == BRepBuilderAPI_PointProjectionFailed ) {
				Logger::Message(Logger::LOG_WARNING,"Point projection failed for:",l);
				trim_cartesian_failed = true;
			}
		} else {
			e = me.Edge();
			// BRepBuilderAPI_MakeEdge swaps v1 and v2 if the parameter value of v2 is 
			// smaller than that of v1. In that case the edge has to be reversed so that
			// the vertex order is consistent with Trim1 and Trim2. Otherwise the
			// IfcOpenShell wire builder will create intermediate edges automatically.
			// The alternative would be to reverse the underlying curve instead.
			if (!TopExp::FirstVertex(e, true).IsSame(v1)) {
				e.Reverse();
			}
		}
	}

	if ( (!trim_cartesian || trim_cartesian_failed) && (has_flts[0] && has_flts[1]) ) {
		// The Geom_Line is constructed from a gp_Pnt and gp_Dir, whereas the IfcLine
		// is defined by an IfcCartesianPoint and an IfcVector with Magnitude. Because
		// the vector is normalised when passed to Geom_Line constructor the magnitude
		// needs to be factored in with the IfcParameterValue here.
		if ( basis_curve->declaration().is(IfcSchema::IfcLine::Class()) ) {
			IfcSchema::IfcLine* line = static_cast<IfcSchema::IfcLine*>(basis_curve);
			const double magnitude = line->Dir()->Magnitude();
			flts[0] *= magnitude; flts[1] *= magnitude;
		}
		if ( basis_curve->declaration().is(IfcSchema::IfcEllipse::Class()) ) {
			IfcSchema::IfcEllipse* ellipse = static_cast<IfcSchema::IfcEllipse*>(basis_curve);
			double x = ellipse->SemiAxis1() * getValue(GV_LENGTH_UNIT);
			double y = ellipse->SemiAxis2() * getValue(GV_LENGTH_UNIT);
			const bool rotated = y > x;
			if (rotated) {
				flts[0] -= M_PI / 2.;
				flts[1] -= M_PI / 2.;
			}
		}

		double radius = 1.0;
		if (curve->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
			auto circle_curve = Handle_Geom_Circle::DownCast(curve);
			radius = circle_curve->Radius();
		} else if (curve->DynamicType() == STANDARD_TYPE(Geom_Ellipse)) {
			auto circle_curve = Handle_Geom_Ellipse::DownCast(curve);
			radius = (circle_curve->MajorRadius() + circle_curve->MinorRadius()) / 2.;
		}

		// Fix from @sanderboer to compare using model tolerance, see #744
		// Made dependent on radius, see #928

		// A good critereon for determining whether to take full curve
		// or trimmed segment would be whether there are other curve segments or this
		// is the only one.
		boost::optional<size_t> num_segments;
		auto segment = l->data().getInverse(&IfcSchema::IfcCompositeCurveSegment::Class(), -1);
		if (segment->size() == 1) {
			auto comp = (*segment->begin())->data().getInverse(&IfcSchema::IfcCompositeCurve::Class(), -1);
			if (comp->size() == 1) {
				num_segments = (*comp->begin())->as<IfcSchema::IfcCompositeCurve>()->Segments()->size();
			}
		}

		// @todo is 100. not too much? Check with the original issue.
		const double precision_markup = getValue(IfcGeom::Kernel::GV_PRECISION_FACTOR) == 1. ? 1. : 100.;

		if (isConic && ALMOST_THE_SAME(fmod(flts[1]-flts[0],M_PI*2.), 0., precision_markup * getValue(GV_PRECISION) / (2 * M_PI * radius))) {
			e = BRepBuilderAPI_MakeEdge(curve).Edge();
		} else {
			BRepBuilderAPI_MakeEdge me (curve,flts[0],flts[1]);
			e = me.Edge();
		}

		if (num_segments && *num_segments > 1) {
			TopoDS_Vertex v0, v1;
			TopExp::Vertices(e, v0, v1);
			if (v0.IsSame(v1)) {
				Logger::Warning("Skipping degenerate segment", l);
				return false;
			}
		}

	} else if ( trim_cartesian_failed && (has_pnts[0] && has_pnts[1]) ) {
		e = BRepBuilderAPI_MakeEdge(pnts[0], pnts[1]).Edge();
	}

	if (e.IsNull()) {
		return false;
	}

	if (isConic) {
		// Tiny circle segnments can cause issues later on, for example
		// when the comp curve is used as the sweeping directrix.
		double a, b;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(e, a, b);
		double radius = -1.;
		if (crv->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
			radius = Handle(Geom_Circle)::DownCast(crv)->Radius();
		} else if (crv->DynamicType() == STANDARD_TYPE(Geom_Ellipse)) {
			// The formula in deflection_for_approximating_circle() is for circles, but probably good enough
			radius = Handle(Geom_Ellipse)::DownCast(crv)->MajorRadius();
		}
		if (radius > 0. && util::deflection_for_approximating_circle(radius, b - a) < 100 * getValue(GV_PRECISION) && std::abs(b-a) < M_PI/4.) {
			TopoDS_Vertex v0, v1;
			TopExp::Vertices(e, v0, v1);
			e = TopoDS::Edge(BRepBuilderAPI_MakeEdge(v0, v1).Edge().Oriented(e.Orientation()));
			Logger::Warning("Subsituted edge with linear approximation", l);
		}
	}

	BRepBuilderAPI_MakeWire w;
	w.Add(e);

	if (w.IsDone()) {
		wire = w.Wire();

		// When SenseAgreement == .F. the vertices above have been reversed to
		// comply with the direction of conical curves. The ordering of the
		// vertices then still needs to be reversed in order to have begin and
		// end vertex consistent with IFC.
		if (sense_agreement != 0) { // .F.
			wire.Reverse();
		}

		return true;
	} else {
		return false;
	}
}
