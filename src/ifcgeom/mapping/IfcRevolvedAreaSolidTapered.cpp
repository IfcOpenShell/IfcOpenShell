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

#include "../../ifcgeom/infra_sweep_helper.h"

#include <Eigen/Geometry>

#ifdef SCHEMA_HAS_IfcRevolvedAreaSolidTapered

namespace {
	// Number of edges (and therefore vertices) in a mapped profile face, per loop.
	// Used to verify the two profiles share a compatible topology before lofting,
	// as linear profile interpolation only works when the loops match one to one.
	std::vector<size_t> loop_edge_counts(const taxonomy::face::ptr& f) {
		std::vector<size_t> counts;
		for (const auto& loop : f->children) {
			counts.push_back(loop->children.size());
		}
		return counts;
	}

	// Shortest distance from a point to the (infinite) revolution axis line.
	double distance_to_axis(const Eigen::Vector3d& p, const Eigen::Vector3d& axis_loc, const Eigen::Vector3d& axis_dir) {
		const Eigen::Vector3d d = p - axis_loc;
		return (d - d.dot(axis_dir) * axis_dir).norm();
	}
}

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRevolvedAreaSolidTapered* inst) {
	const double ang = inst->Angle() * angle_unit_;
	if (ang < settings_.get<settings::Precision>().get()) {
		logger_.Message(Logger::LOG_ERROR, "GEO", 328, "Non-positive revolution angle encountered for:", inst);
		return nullptr;
	}

	auto start_face = taxonomy::cast<taxonomy::face>(map(inst->SweptArea()));
	auto end_face = taxonomy::cast<taxonomy::face>(map(inst->EndSweptArea()));
	if (!start_face || !end_face) {
		return nullptr;
	}

	// The tapered profile is linearly interpolated between SweptArea and EndSweptArea
	// while it revolves. Vertex-by-vertex interpolation only makes sense when both
	// profiles have the same loop count and the same number of vertices per loop.
	const auto counts_a = loop_edge_counts(start_face);
	const auto counts_b = loop_edge_counts(end_face);
	if (counts_a != counts_b) {
		logger_.Warning("GEO", 329, "SweptArea and EndSweptArea have mismatching vertex topology; cannot interpolate tapered revolve for:", inst);
		return nullptr;
	}

	// Revolution axis (IfcAxis1Placement): a point and a direction. The direction
	// defaults to (0, 0, 1) when omitted.
	const Eigen::Vector3d axis_loc = taxonomy::cast<taxonomy::point3>(map(inst->Axis()->Location()))->ccomponents();
	Eigen::Vector3d axis_dir;
	if (inst->Axis()->Axis()) {
		axis_dir = taxonomy::cast<taxonomy::direction3>(map(inst->Axis()->Axis()))->ccomponents();
	} else {
		axis_dir = Eigen::Vector3d(0., 0., 1.);
	}
	if (axis_dir.norm() < 1.e-9) {
		logger_.Warning("GEO", 330, "Degenerate revolution axis for:", inst);
		return nullptr;
	}
	axis_dir.normalize();

	// Representative radius: the largest distance from the axis to any profile vertex.
	// It sets a real arc length for the sweep so the tessellation of the arc (governed
	// by the FunctionStepParam setting) resolves the outermost, most curved edge well.
	double radius = 0.;
	for (const auto& face : { start_face, end_face }) {
		Eigen::Matrix4d fm = Eigen::Matrix4d::Identity();
		if (face->matrix) {
			fm = face->matrix->ccomponents();
		}
		for (const auto& loop : face->children) {
			for (const auto& edge : loop->children) {
				const auto* sp = boost::get<taxonomy::point3::ptr>(&edge->start);
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
		// Profile sits on the axis; fall back to a unit so the sweep domain is non-empty.
		radius = 1.;
	}

	const double arc_length = ang * radius;

	// Directrix functor: the placement frame at arc-length parameter u along the
	// circular path of the profile origin around the revolution axis. Column 0 is the
	// circumferential tangent, columns 1 and 2 span the rotated profile plane, and
	// column 3 is the rotated origin. make_loft remaps these columns so that the
	// profile's local Z aligns with the tangent (as a normal IfcRevolvedAreaSolid
	// section does) and the profile is genuinely rotated about the axis at each step.
	// Because the frame follows the arc, the lateral faces curve through the
	// cylindrical revolve space instead of forming a single straight ruled chord
	// between the two end profiles.
	const Eigen::Vector3d L = axis_loc;
	const Eigen::Vector3d A = axis_dir;
	const double total_angle = ang;
	auto fn = taxonomy::make<taxonomy::functor_item>(arc_length, [L, A, total_angle, arc_length](double u) -> Eigen::Matrix4d {
		const double theta = arc_length > 1.e-12 ? total_angle * (u / arc_length) : 0.;
		const Eigen::Matrix3d R = Eigen::AngleAxisd(theta, A).toRotationMatrix();
		Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
		m.col(0).head<3>() = R.col(2); // tangent -> profile normal (local Z)
		m.col(1).head<3>() = R.col(0); // rotated profile local X
		m.col(2).head<3>() = R.col(1); // rotated profile local Y
		m.col(3).head<3>() = L - R * L; // rotation of the origin about the axis through L
		return m;
	});

	const Eigen::Vector3d no_offset = Eigen::Vector3d::Zero();
	const boost::optional<Eigen::Matrix3d> no_rotation = boost::none;
	std::vector<cross_section> cross_sections;
	cross_sections.push_back({ 0., start_face, no_offset, no_rotation });
	cross_sections.push_back({ arc_length, end_face, no_offset, no_rotation });

	// make_loft tessellates the directrix into intermediate stations, linearly
	// interpolates the profile between the two cross sections at each station, and
	// orients every station by the frame above. It also independently guards against
	// mismatching loop and edge counts, returning nullptr in that case.
	auto loft = make_loft(settings_, inst, fn, cross_sections, logger_);
	if (!loft) {
		return nullptr;
	}

	taxonomy::matrix4::ptr matrix;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = inst->Position() != nullptr;
#endif
	if (has_position) {
		matrix = taxonomy::cast<taxonomy::matrix4>(map(inst->Position()));
	}
	if (matrix) {
		loft->matrix = matrix;
	}

	return loft;
}

#endif
