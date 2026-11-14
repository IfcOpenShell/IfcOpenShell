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
#include "../profile_helper.h"

#include <array>

#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geom;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCenterLineProfileDef& inst) {
	const double d = inst.Thickness() * length_unit_ / 2.;
	const double eps = settings_.get<settings::Precision>().get();

	if (d < eps) {
		logger_.warning("GEO", 331, "Thickness below precision for:", inst);
		return nullptr;
	}

	auto crv = taxonomy::cast<taxonomy::loop>(map(inst.Curve()));
	if (!crv || crv->children.empty() || !crv->is_polyhedron()) {
		logger_.warning("GEO", 332, "Only polyline centerlines are supported:", inst);
		return nullptr;
	}

	std::vector<Eigen::Vector2d> pts;
	pts.reserve(crv->children.size() + 1);
	for (auto& e : crv->children) {
		auto p = std::get_if<taxonomy::point3::ptr>(&e->start);
		auto q = std::get_if<taxonomy::point3::ptr>(&e->end);
		if (!p || !q || !*p || !*q) {
			logger_.warning("GEO", 332, "Only polyline centerlines are supported:", inst);
			return nullptr;
		}
		Eigen::Vector2d a = (*p)->ccomponents().head<2>();
		Eigen::Vector2d b = (*q)->ccomponents().head<2>();
		if (pts.empty()) {
			pts.push_back(a);
		} else if ((pts.back() - a).norm() > eps) {
			logger_.warning("GEO", 333, "Discontinuous centerline for:", inst);
			return nullptr;
		}
		pts.push_back(b);
	}

	if ((pts.front() - pts.back()).norm() < eps) {
		logger_.warning("GEO", 333, "Closed centerline for:", inst);
		return nullptr;
	}

	const size_t n = pts.size();
	std::vector<Eigen::Vector2d> normals(n - 1);
	std::vector<double> lengths(n - 1);
	for (size_t i = 0; i < n - 1; ++i) {
		Eigen::Vector2d t = pts[i + 1] - pts[i];
		lengths[i] = t.norm();
		if (lengths[i] < eps) {
			logger_.warning("GEO", 333, "Degenerate centerline segment for:", inst);
			return nullptr;
		}
		t /= lengths[i];
		normals[i] = Eigen::Vector2d(-t.y(), t.x());
	}

	// Straight miter joins keep the thickness constant along the curve
	std::vector<Eigen::Vector2d> miters(n);
	miters.front() = normals.front();
	miters.back() = normals.back();
	// What the inner corners take from each segment, per side
	std::vector<std::array<double, 2>> retreat(n - 1, { 0., 0. });
	for (size_t i = 1; i < n - 1; ++i) {
		const double denom = 1. + normals[i - 1].dot(normals[i]);
		const double cross = normals[i - 1].x() * normals[i].y() - normals[i - 1].y() * normals[i].x();
		if (denom < 1.e-9) {
			logger_.warning("GEO", 333, "Centerline reverses onto itself for:", inst);
			return nullptr;
		}
		miters[i] = (normals[i - 1] + normals[i]) / denom;
		const size_t side = cross > 0. ? 0 : 1;
		retreat[i - 1][side] += d * std::abs(cross) / denom;
		retreat[i][side] += d * std::abs(cross) / denom;
	}
	for (size_t i = 0; i < n - 1; ++i) {
		if ((std::max)(retreat[i][0], retreat[i][1]) > lengths[i] - eps) {
			logger_.warning("GEO", 333, "Centerline turn too sharp for its thickness:", inst);
			return nullptr;
		}
	}

	std::vector<taxonomy::point3::ptr> ps;
	ps.reserve(2 * n + 1);
	for (size_t i = 0; i < n; ++i) {
		const Eigen::Vector2d p = pts[i] - d * miters[i];
		ps.push_back(taxonomy::make<taxonomy::point3>(p.x(), p.y(), 0.));
	}
	for (size_t i = n; i-- > 0;) {
		const Eigen::Vector2d p = pts[i] + d * miters[i];
		ps.push_back(taxonomy::make<taxonomy::point3>(p.x(), p.y(), 0.));
	}
	ps.push_back(ps.front());

	auto face = taxonomy::make<taxonomy::face>();
	face->children = { polygon_from_points(ps) };
	return face;
}
