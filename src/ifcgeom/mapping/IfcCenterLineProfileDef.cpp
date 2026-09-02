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

#include "../profile_helper.h"

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCenterLineProfileDef* inst) {
	const double d = inst->Thickness() * length_unit_ / 2.;
	const double eps = settings_.get<settings::Precision>().get();

	if (d < eps) {
		logger_.Warning("GEO", 403, "Thickness below precision for:", inst);
		return nullptr;
	}

	auto mapped = map(inst->Curve());
	if (!mapped) {
		return nullptr;
	}
	auto crv = taxonomy::dcast<taxonomy::loop>(mapped);
	if (!crv || crv->children.empty()) {
		logger_.Warning("GEO", 404, "Unsupported centerline curve for:", inst);
		return nullptr;
	}
	if (!crv->is_polyhedron()) {
		logger_.Warning("GEO", 404, "Unsupported curved centerline segments for:", inst);
		return nullptr;
	}

	std::vector<Eigen::Vector2d> pts;
	pts.reserve(crv->children.size() + 1);
	for (auto& e : crv->children) {
		if (e->start.which() != 1 || e->end.which() != 1) {
			logger_.Warning("GEO", 404, "Unsupported parametric trims on centerline for:", inst);
			return nullptr;
		}
		Eigen::Vector2d p = boost::get<taxonomy::point3::ptr>(e->start)->ccomponents().head<2>();
		Eigen::Vector2d q = boost::get<taxonomy::point3::ptr>(e->end)->ccomponents().head<2>();
		if (pts.empty()) {
			pts.push_back(p);
		} else if ((pts.back() - p).norm() > eps) {
			logger_.Warning("GEO", 405, "Unsupported discontinuous centerline for:", inst);
			return nullptr;
		}
		pts.push_back(q);
	}

	if (pts.size() < 2 || (pts.front() - pts.back()).norm() < eps) {
		logger_.Warning("GEO", 405, "Unsupported closed or degenerate centerline for:", inst);
		return nullptr;
	}

	const size_t n = pts.size();
	std::vector<Eigen::Vector2d> normals(n - 1);
	for (size_t i = 0; i < n - 1; ++i) {
		Eigen::Vector2d t = pts[i + 1] - pts[i];
		const double l = t.norm();
		if (l < eps) {
			logger_.Warning("GEO", 405, "Degenerate centerline segment for:", inst);
			return nullptr;
		}
		t /= l;
		normals[i] = Eigen::Vector2d(-t.y(), t.x());
	}

	// Straight miter joins at the vertices, because the profile prescribes a
	// constant thickness along the curve, which the arc joins of a generic
	// offset algorithm would violate.
	std::vector<Eigen::Vector2d> miters(n);
	miters.front() = normals.front();
	miters.back() = normals.back();
	for (size_t i = 1; i < n - 1; ++i) {
		const double denom = 1. + normals[i - 1].dot(normals[i]);
		if (denom < 1.e-9) {
			logger_.Warning("GEO", 405, "Centerline reverses onto itself for:", inst);
			return nullptr;
		}
		miters[i] = (normals[i - 1] + normals[i]) / denom;
	}

	std::vector<Eigen::Vector2d> polygon;
	polygon.reserve(2 * n);
	for (size_t i = 0; i < n; ++i) {
		polygon.push_back(pts[i] - d * miters[i]);
	}
	for (size_t i = n; i-- > 0;) {
		polygon.push_back(pts[i] + d * miters[i]);
	}

	double twice_area = 0.;
	for (size_t i = 0; i < polygon.size(); ++i) {
		const auto& a = polygon[i];
		const auto& b = polygon[(i + 1) % polygon.size()];
		twice_area += a.x() * b.y() - b.x() * a.y();
	}
	if (twice_area < 0.) {
		std::reverse(polygon.begin(), polygon.end());
	}

	std::vector<taxonomy::point3::ptr> ps;
	ps.reserve(polygon.size() + 1);
	for (auto& p : polygon) {
		ps.push_back(taxonomy::make<taxonomy::point3>(p.x(), p.y(), 0.));
	}
	ps.push_back(ps.front());

	auto loop = polygon_from_points(ps);
	auto face = taxonomy::make<taxonomy::face>();
	face->children = { loop };
	return face;
}
