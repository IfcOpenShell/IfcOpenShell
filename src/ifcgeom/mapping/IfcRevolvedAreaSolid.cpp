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

#include <boost/math/constants/constants.hpp>

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRevolvedAreaSolid* inst) {
	const double ang = inst->Angle() * angle_unit_;

	taxonomy::cast<taxonomy::face>(map(inst->SweptArea()));
	
	boost::optional<double> angle;

	taxonomy::matrix4::ptr matrix;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = inst->Position() != nullptr;
#endif
	if (has_position) {
		matrix = taxonomy::cast<taxonomy::matrix4>(map(inst->Position()));
	}

	if (ang < boost::math::constants::pi<double>() * 2. - 1.e-5) {
		angle = ang;
	}

	return taxonomy::make<taxonomy::revolve>(
		matrix,
		taxonomy::cast<taxonomy::face>(map(inst->SweptArea())),
		taxonomy::cast<taxonomy::point3>(map(inst->Axis()->Location())),
		taxonomy::cast<taxonomy::direction3>(map(inst->Axis()->Axis())),
		angle
	);

	/*
	{
		// https://github.com/IfcOpenShell/IfcOpenShell/issues/1030
		// Check whether Axis does not intersect SweptArea

		double min_dot = +std::numeric_limits<double>::infinity();
		double max_dot = -std::numeric_limits<double>::infinity();

		gp_Ax2 ax(ax1.Location(), gp::DZ(), ax1.Direction());

		TopExp_Explorer exp(face, TopAbs_EDGE);
		for (; exp.More(); exp.Next()) {
			BRepAdaptor_Curve crv(TopoDS::Edge(exp.Current()));
			GCPnts_QuasiUniformDeflection tessellater(crv, getValue(GV_PRECISION));

			int n = tessellater.NbPoints();
			for (int i = 1; i <= n; ++i) {
				double d = ax.YDirection().XYZ().Dot(tessellater.Value(i).XYZ());
				if (d < min_dot) {
					min_dot = d;
				}
				if (d > max_dot) {
					max_dot = d;
				}
			}
		}

		bool intersecting;
		if (std::abs(min_dot) > std::abs(max_dot)) {
			intersecting = max_dot > + getValue(GV_PRECISION);
		} else {
			intersecting = min_dot < - getValue(GV_PRECISION);
		}

		if (intersecting) {
			Logger::Warning("Warning Axis and SweptArea intersecting", l);
		}
	}
	*/
}
