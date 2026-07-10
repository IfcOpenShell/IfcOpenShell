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

#include <boost/math/constants/constants.hpp>

#include <Eigen/Geometry>

#ifdef SCHEMA_HAS_IfcRevolvedAreaSolidTapered

// IfcRevolvedAreaSolidTapered revolves a start profile (SweptArea) into an end
// profile (EndSweptArea) about a revolution axis. Unlike a plain
// IfcRevolvedAreaSolid the cross section morphs along the sweep, so it cannot be
// expressed as a single taxonomy::revolve. It is instead built as a loft: the
// revolution axis is turned into a rigid-rotation directrix (a functor_item),
// and make_loft() interpolates the two profiles while placing them around the
// arc, mirroring how IfcSectionedSolidHorizontal and IfcExtrudedAreaSolidTapered
// are handled.
taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRevolvedAreaSolidTapered* inst) {
	const double ang = inst->Angle() * angle_unit_;
	if (ang < 1.e-7) {
		logger_.Message(Logger::LOG_ERROR, "GEO", 89, "Non-positive revolution angle encountered for:", inst);
		return nullptr;
	}

	auto start_face = taxonomy::cast<taxonomy::face>(map(inst->SweptArea()));
	auto end_face = taxonomy::cast<taxonomy::face>(map(inst->EndSweptArea()));
	if (!start_face || !end_face) {
		return nullptr;
	}

	// Revolution axis, expressed in the profile (Position) coordinate system.
	taxonomy::direction3::ptr axis_dir;
	if (inst->Axis()->Axis()) {
		axis_dir = taxonomy::cast<taxonomy::direction3>(map(inst->Axis()->Axis()));
	} else {
		// IfcAxis1Placement.Axis is optional and defaults to (0, 0, 1).
		axis_dir = taxonomy::make<taxonomy::direction3>(0, 0, 1);
	}
	auto axis_loc = taxonomy::cast<taxonomy::point3>(map(inst->Axis()->Location()));

	const Eigen::Vector3d d = axis_dir->ccomponents().normalized();
	const Eigen::Vector3d P = axis_loc->ccomponents();

	// Directrix: a rigid rotation about the revolution axis, parameterised by the
	// swept angle. make_loft() re-maps the profile local axes onto the frame
	// columns as local-X <- col(1), local-Y <- col(2), local-Z (normal) <- col(0),
	// so the rotation columns are permuted to compensate. The remaining Position
	// placement is applied as loft->matrix below.
	auto directrix = taxonomy::make<taxonomy::functor_item>(ang, [d, P](double u) -> Eigen::Matrix4d {
		const Eigen::Matrix3d R(Eigen::AngleAxisd(u, d));
		Eigen::Matrix4d A = Eigen::Matrix4d::Identity();
		A.block<3, 3>(0, 0) = R;
		A.block<3, 1>(0, 3) = P - R * P;

		Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
		m.col(0) = A.col(2);
		m.col(1) = A.col(0);
		m.col(2) = A.col(1);
		m.col(3) = A.col(3);
		return m;
	});

	std::vector<cross_section> cross_sections;
	cross_sections.push_back({ 0.0, start_face, Eigen::Vector3d::Zero(), boost::none });
	cross_sections.push_back({ ang, end_face, Eigen::Vector3d::Zero(), boost::none });

	auto loft = make_loft(settings_, inst, directrix, cross_sections, logger_);
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
	loft->matrix = matrix;

	return loft;
}
#endif
