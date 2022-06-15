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

#include <gp_Pnt.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include "../ifcgeom/IfcGeom.h"
#include <Geom_BSplineCurve.hxx>

#define Kernel MAKE_TYPE_NAME(Kernel)

#ifdef SCHEMA_HAS_IfcBSplineCurveWithKnots
bool IfcGeom::Kernel::convert(const IfcSchema::IfcBSplineCurveWithKnots* l, Handle(Geom_Curve)& curve) {

	const bool is_rational = l->declaration().is(IfcSchema::IfcRationalBSplineCurveWithKnots::Class());

	const IfcSchema::IfcCartesianPoint::list::ptr cps = l->ControlPointsList();
	const std::vector<int> mults = l->KnotMultiplicities();
	const std::vector<double> knots = l->Knots();

	TColgp_Array1OfPnt      Poles(0,  cps->size() - 1);
	TColStd_Array1OfReal    Weights(0, cps->size() - 1);
	TColStd_Array1OfReal    Knots(0, (int)knots.size() - 1);
	TColStd_Array1OfInteger Mults(0, (int)mults.size() - 1);
	Standard_Integer        Degree = l->Degree();
	Standard_Boolean        Periodic = false; 
	// @tfk: it appears to be wrong to expect a period curve when the curve is closed, see #586
	// Standard_Boolean     Periodic = l->ClosedCurve();
	
	int i;

	if (is_rational) {
		IfcSchema::IfcRationalBSplineCurveWithKnots* rl = (IfcSchema::IfcRationalBSplineCurveWithKnots*)l;
		std::vector<double> weights = rl->WeightsData();

		i = 0;
		for (std::vector<double>::const_iterator it = weights.begin(); it != weights.end(); ++it, ++i) {
			Weights(i) = *it;
		}
	}

	i = 0;
	for (IfcSchema::IfcCartesianPoint::list::it it = cps->begin(); it != cps->end(); ++it, ++i) {
		gp_Pnt pnt;
		if (!convert(*it, pnt)) return false;
		Poles(i) = pnt;
	}
	
	i = 0;
	for (std::vector<int>::const_iterator it = mults.begin(); it != mults.end(); ++it, ++i) {
		Mults(i) = *it;
	}

	i = 0;
	for (std::vector<double>::const_iterator it = knots.begin(); it != knots.end(); ++it, ++i) {
		Knots(i) = *it;
	}
	
	if (is_rational) {
		curve = new Geom_BSplineCurve(Poles, Weights, Knots, Mults, Degree, Periodic);
	} else {
		curve = new Geom_BSplineCurve(Poles, Knots, Mults, Degree, Periodic);
	}
	return true;
}
#endif