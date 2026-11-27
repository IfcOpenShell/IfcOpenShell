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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCenterLineProfileDef& inst) {
	const double d = inst.Thickness() * length_unit_ / 2.;
	const double eps = settings_.get<settings::Precision>().get();

	if (d < eps) {
		logger_.warning("GEO", 331, "Thickness below precision for:", inst);
		return nullptr;
	}

	auto mapped = taxonomy::cast<taxonomy::loop>(map(inst.Curve()));
	if (!mapped || mapped->children.empty()) {
		logger_.warning("GEO", 332, "No curve for:", inst);
		return nullptr;
	}
	// The centerline is open, however it is referenced by a profile.
	auto crv = taxonomy::loop::ptr(mapped->clone_());
	crv->closed = false;
	const double end = static_cast<double>(crv->children.size());

	// The area is bounded by the offsets of the centerline on either side and
	// straight connections at its ends. The kernels construct the offsets.
	auto reference = taxonomy::make<taxonomy::direction3>(0, 0, 1);
	auto left = taxonomy::make<taxonomy::offset_curve>();
	left->basis = crv;
	left->offset = d;
	left->reference = reference;
	auto right = taxonomy::make<taxonomy::offset_curve>();
	right->basis = crv;
	right->offset = -d;
	right->reference = reference;

	auto point_at = [](const taxonomy::offset_curve::ptr& c, double u) {
		Eigen::Vector3d p = c->evaluate(0, u);
		return taxonomy::make<taxonomy::point3>(p.x(), p.y(), p.z());
	};
	auto left_start = point_at(left, 0.);
	auto left_end = point_at(left, end);
	auto right_start = point_at(right, 0.);
	auto right_end = point_at(right, end);
	if ((left_start->ccomponents() - left_end->ccomponents()).norm() < eps) {
		logger_.warning("GEO", 333, "Closed centerline for:", inst);
		return nullptr;
	}

	auto along_right = taxonomy::make<taxonomy::edge>();
	along_right->basis = right;
	along_right->start = 0.;
	along_right->end = end;
	auto back_along_left = taxonomy::make<taxonomy::edge>();
	back_along_left->basis = left;
	back_along_left->start = end;
	back_along_left->end = 0.;

	auto loop = taxonomy::make<taxonomy::loop>();
	loop->children = {
		along_right,
		taxonomy::make<taxonomy::edge>(right_end, left_end),
		back_along_left,
		taxonomy::make<taxonomy::edge>(left_start, right_start),
	};
	loop->closed = true;
	loop->external = true;

	auto face = taxonomy::make<taxonomy::face>();
	face->children = { loop };
	return face;
}
