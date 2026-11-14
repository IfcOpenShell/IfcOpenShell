// This file was generated with the assistance of an AI coding tool.
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

#include "../../ifcgeom/infra_sweep_helper.h"

#include <Eigen/Geometry>

#ifdef SCHEMA_HAS_IfcRevolvedAreaSolidTapered

namespace {
	// Edge count per loop, used to check both profiles interpolate vertex by vertex.
	std::vector<size_t> loop_edge_counts(const taxonomy::face::ptr& f) {
		std::vector<size_t> counts;
		for (const auto& loop : f->children) {
			counts.push_back(loop->children.size());
		}
		return counts;
	}

	double distance_to_axis(const Eigen::Vector3d& p, const Eigen::Vector3d& axis_loc, const Eigen::Vector3d& axis_dir) {
		const Eigen::Vector3d d = p - axis_loc;
		return (d - d.dot(axis_dir) * axis_dir).norm();
	}
}

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRevolvedAreaSolidTapered& inst) {
	const double ang = inst.Angle() * angle_unit_;
	if (ang < settings_.get<settings::Precision>().get()) {
		logger_.message(ifcopenshell::logger::LOG_ERROR, "GEO", 328, "Non-positive revolution angle encountered for:", inst);
		return nullptr;
	}

	auto start_face = taxonomy::cast<taxonomy::face>(map(inst.SweptArea()));
	auto end_face = taxonomy::cast<taxonomy::face>(map(inst.EndSweptArea()));
	if (!start_face || !end_face) {
		return nullptr;
	}

	if (loop_edge_counts(start_face) != loop_edge_counts(end_face)) {
		logger_.warning("GEO", 329, "SweptArea and EndSweptArea have mismatching vertex topology; cannot interpolate tapered revolve for:", inst);
		return nullptr;
	}

	const Eigen::Vector3d axis_loc = taxonomy::cast<taxonomy::point3>(map(inst.Axis().Location()))->ccomponents();
	Eigen::Vector3d axis_dir(0., 0., 1.);
	if (inst.Axis().Axis()) {
		axis_dir = taxonomy::cast<taxonomy::direction3>(map(inst.Axis().Axis()))->ccomponents();
	}
	if (axis_dir.norm() < 1.e-9) {
		logger_.warning("GEO", 330, "Degenerate revolution axis for:", inst);
		return nullptr;
	}
	axis_dir.normalize();

	// The largest vertex distance to the axis gives the arc length that the step setting subdivides.
	double radius = 0.;
	for (const auto& face : { start_face, end_face }) {
		Eigen::Matrix4d fm = Eigen::Matrix4d::Identity();
		if (face->matrix) {
			fm = face->matrix->ccomponents();
		}
		for (const auto& loop : face->children) {
			for (const auto& edge : loop->children) {
				const auto* sp = std::get_if<taxonomy::point3::ptr>(&edge->start);
				if (!sp || !*sp) {
					continue;
				}
				Eigen::Vector4d hp;
				hp << (*sp)->ccomponents(), 1.;
				const Eigen::Vector3d wp = (fm * hp).head<3>();
				radius = std::max(radius, distance_to_axis(wp, axis_loc, axis_dir));
			}
		}
	}
	if (radius < settings_.get<settings::Precision>().get()) {
		radius = 1.;
	}

	const double arc_length = ang * radius;

	// Directrix frame at arc length u: the profile rotated by u/radius about the axis.
	// Columns follow make_loft: tangent, lateral (profile X), up (profile Y), origin.
	const Eigen::Vector3d L = axis_loc;
	const Eigen::Vector3d A = axis_dir;
	const double total_angle = ang;
	auto fn = taxonomy::make<taxonomy::functor_item>(arc_length, [L, A, total_angle, arc_length](double u) -> Eigen::Matrix4d {
		const double theta = total_angle * (u / arc_length);
		const Eigen::Matrix3d R = Eigen::AngleAxisd(theta, A).toRotationMatrix();
		Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
		m.col(0).head<3>() = R.col(2);
		m.col(1).head<3>() = R.col(0);
		m.col(2).head<3>() = R.col(1);
		m.col(3).head<3>() = L - R * L;
		return m;
	});

	std::vector<cross_section> cross_sections;
	cross_sections.push_back({ 0., start_face, Eigen::Vector3d::Zero(), std::nullopt, std::nullopt });
	cross_sections.push_back({ arc_length, end_face, Eigen::Vector3d::Zero(), std::nullopt, std::nullopt });

	auto loft = make_loft(settings_, inst, fn, cross_sections, logger_);
	if (!loft) {
		return nullptr;
	}

	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = !!inst.Position();
#endif
	if (has_position) {
		loft->matrix = taxonomy::cast<taxonomy::matrix4>(map(inst.Position()));
	}

	return loft;
}

#endif
