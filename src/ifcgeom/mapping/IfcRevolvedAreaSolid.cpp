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

#include <boost/math/constants/constants.hpp>

#include <algorithm>
#include <limits>

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRevolvedAreaSolid& inst) {
	const double ang = inst.Angle() * angle_unit_;

	auto face = taxonomy::cast<taxonomy::face>(map(inst.SweptArea()));
	auto axis_origin = taxonomy::cast<taxonomy::point3>(map(inst.Axis().Location()));
	auto axis_direction = taxonomy::cast<taxonomy::direction3>(map(inst.Axis().Axis()));

	std::optional<double> angle;

	taxonomy::matrix4::ptr matrix;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
    has_position = !!inst.Position();
#endif
	if (has_position) {
		matrix = taxonomy::cast<taxonomy::matrix4>(map(inst.Position()));
	}

	if (ang < boost::math::constants::pi<double>() * 2. - 1.e-5) {
		angle = ang;
	}

	{
		// https://github.com/IfcOpenShell/IfcOpenShell/issues/1030
		// The axis shall not intersect the interior of the swept area. The swept
		// area lies in the XY plane of Position, so the sign of the distance to
		// the axis, measured along the in-plane normal of the axis, tells on
		// which side of the axis a point lies.
		const Eigen::Vector3d origin = axis_origin->ccomponents();
		const Eigen::Vector3d normal = Eigen::Vector3d::UnitZ().cross(axis_direction->ccomponents()).normalized();
		double min_distance = +std::numeric_limits<double>::infinity();
		double max_distance = -std::numeric_limits<double>::infinity();
		for (const auto& loop : face->children) {
			for (const auto& p : loop->to_polygon(settings_)) {
				Eigen::Vector3d q = p.ccomponents();
				if (face->matrix) {
					q = (face->matrix->ccomponents() * q.homogeneous()).head<3>();
				}
				const double d = normal.dot(q - origin);
				min_distance = std::min(min_distance, d);
				max_distance = std::max(max_distance, d);
			}
		}
		const double tolerance = settings_.get<settings::Precision>().get();
		if (min_distance < -tolerance && max_distance > tolerance) {
			logger_.warning("GEO", 329, "Axis intersects SweptArea of:", inst);
		}
	}

	return taxonomy::make<taxonomy::revolve>(
		matrix,
		face,
		axis_origin,
		axis_direction,
		angle
	);
}
