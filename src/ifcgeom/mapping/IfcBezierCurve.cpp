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

#ifdef SCHEMA_HAS_IfcBezierCurve
// IfcBezierCurve is an IfcBSplineCurve where the knots are evenly spaced
// with high multiplicities. This is an IFC2X3-only entity.
// For a Bezier curve of degree n with n+1 control points:
// - Knot vector: {0, ..., 0, 1, ..., 1} with multiplicity (n+1) at each end
// - This ensures the curve passes through the first and last control points
taxonomy::ptr mapping::map_impl(const IfcSchema::IfcBezierCurve* inst) {
	auto bc = taxonomy::make<taxonomy::bspline_curve>();

	const IfcSchema::IfcCartesianPoint::list::ptr cps = inst->ControlPointsList();
	std::vector<taxonomy::point3::ptr> points;
	std::transform(cps->begin(), cps->end(), std::back_inserter(points),
		[this](IfcSchema::IfcCartesianPoint* cp) {
			return taxonomy::cast<taxonomy::point3>(map(cp));
		});
	bc->control_points = points;

	int degree = inst->Degree();
	bc->degree = degree;

	// Generate Bezier knot vector: [0, ..., 0, 1, ..., 1]
	// with multiplicity (degree + 1) at each end
	int mult = degree + 1;

	// For Bezier curves: two knots (0 and 1), each with multiplicity (degree + 1)
	bc->multiplicities = {mult, mult};
	bc->knots = {0.0, 1.0};

	// Handle rational Bezier curves (IfcRationalBezierCurve)
	if (inst->as<IfcSchema::IfcRationalBezierCurve>()) {
		bc->weights = inst->as<IfcSchema::IfcRationalBezierCurve>()->Weights();
	}

	return bc;
}
#endif
