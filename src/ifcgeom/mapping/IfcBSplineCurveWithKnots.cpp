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


#include "mapping.h"

#define mapping POSTFIX_SCHEMA(mapping)

using namespace ifcopenshell::geometry;

#ifdef SCHEMA_HAS_IfcBSplineCurveWithKnots
taxonomy::ptr mapping::map_impl(const IfcSchema::IfcBSplineCurveWithKnots* inst) {
	auto bc = taxonomy::make<taxonomy::bspline_curve>();
	
	const IfcSchema::IfcCartesianPoint::list::ptr cps = inst->ControlPointsList();
	std::vector<taxonomy::point3::ptr> points;
	std::transform(cps->begin(), cps->end(), std::back_inserter(points), [this](IfcSchema::IfcCartesianPoint* cp) { return taxonomy::cast<taxonomy::point3>(map(cp)); });
	bc->control_points = points;
		
	bc->multiplicities = inst->KnotMultiplicities();
	bc->knots = inst->Knots();
	if (inst->as<IfcSchema::IfcRationalBSplineCurveWithKnots>()) {
		bc->weights = inst->as<IfcSchema::IfcRationalBSplineCurveWithKnots>()->WeightsData();
	}
	bc->degree = inst->Degree();

	return bc;
}
#endif