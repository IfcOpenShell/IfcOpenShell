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

using namespace ifcopenshell::geom;

#ifdef SCHEMA_HAS_IfcBSplineSurfaceWithKnots

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcBSplineSurfaceWithKnots& inst) {
	auto bs = taxonomy::make<taxonomy::bspline_surface>();

	auto cps = inst.ControlPointsList();
	std::transform(cps.begin(), cps.end(), std::back_inserter(bs->control_points), [this](const std::vector<IfcSchema::IfcCartesianPoint>& inner) {
		std::vector<taxonomy::point3::ptr> ps;
		std::transform(inner.begin(), inner.end(), std::back_inserter(ps), [this](const IfcSchema::IfcCartesianPoint& cp) { return taxonomy::cast<taxonomy::point3>(map(cp)); });
		return ps;
	});

	auto to_int_vector = [](const std::vector<int64_t>& v) {
		return std::vector<int>(v.begin(), v.end());
	};
	bs->multiplicities = { to_int_vector(inst.UMultiplicities()), to_int_vector(inst.VMultiplicities()) };
	bs->knots = { inst.UKnots(), inst.VKnots() };
	if (inst.as<IfcSchema::IfcRationalBSplineSurfaceWithKnots>()) {
		bs->weights = inst.as<IfcSchema::IfcRationalBSplineSurfaceWithKnots>().WeightsData();
	}
	bs->degree = { (int) inst.UDegree(), (int) inst.VDegree() };

	return bs;
}

#endif
