#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#include <boost/math/constants/constants.hpp>

taxonomy::item* mapping::map_impl(const IfcSchema::IfcTrimmedCurve* inst) {
	IfcSchema::IfcCurve* basis_curve = inst->BasisCurve();
	bool isConic = basis_curve->declaration().is(IfcSchema::IfcConic::Class());
	double parameterFactor = isConic ? angle_unit_ : length_unit_;

	auto tc = new taxonomy::edge;
	tc->basis = map(inst->BasisCurve());

	bool trim_cartesian = inst->MasterRepresentation() != IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER;
	IfcEntityList::ptr trims1 = inst->Trim1();
	IfcEntityList::ptr trims2 = inst->Trim2();

	// reversed orientation handling happens in geometry kernel
	unsigned sense_agreement = 0; // inst->SenseAgreement() ? 0 : 1;
	double flts[2];
	taxonomy::point3 pnts[2];
	bool has_flts[2] = { false,false };
	bool has_pnts[2] = { false,false };

	tc->orientation = inst->SenseAgreement();

	for (IfcEntityList::it it = trims1->begin(); it != trims1->end(); it++) {
		IfcUtil::IfcBaseClass* i = *it;
		if (i->declaration().is(IfcSchema::IfcCartesianPoint::Class())) {
			pnts[sense_agreement] = as<taxonomy::point3>(map(i));
			has_pnts[sense_agreement] = true;
		} else if (i->declaration().is(IfcSchema::IfcParameterValue::Class())) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[sense_agreement] = value * parameterFactor;
			has_flts[sense_agreement] = true;
		}
	}

	for (IfcEntityList::it it = trims2->begin(); it != trims2->end(); it++) {
		IfcUtil::IfcBaseClass* i = *it;
		if (i->declaration().is(IfcSchema::IfcCartesianPoint::Class())) {
			pnts[1 - sense_agreement] = as<taxonomy::point3>(map(i));
			has_pnts[1 - sense_agreement] = true;
		} else if (i->declaration().is(IfcSchema::IfcParameterValue::Class())) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[1 - sense_agreement] = value * parameterFactor;
			has_flts[1 - sense_agreement] = true;
		}
	}

	// @todo
	const double precision_ = 1.e-5;

	trim_cartesian &= has_pnts[0] && has_pnts[1];
	if (trim_cartesian) {
		if ((*pnts[0].components_ - *pnts[1].components_).norm() < (2 * precision_)) {
			Logger::Message(Logger::LOG_WARNING, "Skipping segment with length below tolerance level:", inst);
			return nullptr;
		}
		tc->start = pnts[0];
		tc->end = pnts[1];
	} else if (has_flts[0] && has_flts[1]) {
		// The Geom_Line is constructed from a gp_Pnt and gp_Dir, whereas the IfcLine
		// is defined by an IfcCartesianPoint and an IfcVector with Magnitude. Because
		// the vector is normalised when passed to Geom_Line constructor the magnitude
		// needs to be factored in with the IfcParameterValue here.
		if (basis_curve->declaration().is(IfcSchema::IfcLine::Class())) {
			IfcSchema::IfcLine* line = static_cast<IfcSchema::IfcLine*>(basis_curve);
			const double magnitude = line->Dir()->Magnitude();
			flts[0] *= magnitude; flts[1] *= magnitude;
		}
		if (basis_curve->declaration().is(IfcSchema::IfcEllipse::Class())) {
			IfcSchema::IfcEllipse* ellipse = static_cast<IfcSchema::IfcEllipse*>(basis_curve);
			double x = ellipse->SemiAxis1() * length_unit_;
			double y = ellipse->SemiAxis2() * length_unit_;
			// @todo the need for this rotation is OCCT-specific
			const bool rotated = y > x;
			if (rotated) {
				flts[0] -= boost::math::constants::pi<double>() / 2.;
				flts[1] -= boost::math::constants::pi<double>() / 2.;
			}
		}
		tc->start = flts[0];
		tc->end = flts[1];
	}

	/*
	// @todo
	if (isConic) {
		// Tiny circle segnments can cause issues later on, for example
		// when the comp curve is used as the sweeping directrix.
		double a, b;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(e, a, b);
		double radius = -1.;
		if (crv->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
			radius = Handle(Geom_Circle)::DownCast(crv)->Radius();
		} else if (crv->DynamicType() == STANDARD_TYPE(Geom_Ellipse)) {
			// The formula above is for circles, but probably good enough
			radius = Handle(Geom_Ellipse)::DownCast(crv)->MajorRadius();
		}
		if (radius > 0. && deflection_for_approximating_circle(radius, b - a) < getValue(GV_PRECISION)) {
			TopoDS_Vertex v0, v1;
			TopExp::Vertices(e, v0, v1);
			e = TopoDS::Edge(BRepBuilderAPI_MakeEdge(v0, v1).Edge().Oriented(e.Orientation()));
			Logger::Warning("Subsituted edge with linear approximation", l);
		}
	}
	*/
		
	return tc;
}
