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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcLShapeProfileDef* inst) {
	const bool hasSlope = !!inst->LegSlope();
	const bool doEdgeFillet = !!inst->EdgeRadius();
	const bool doFillet = !!inst->FilletRadius();

	const double y = inst->Depth() / 2.0f * length_unit_;
	const double x = inst->Width().get_value_or(inst->Depth()) / 2.0f * length_unit_;
	const double d = inst->Thickness() * length_unit_;
	const double slope = inst->LegSlope().get_value_or(0.) * angle_unit_;
	
	double f1 = 0.0f;
	double f2 = 0.0f;
	if (doFillet) {
		f1 = *inst->FilletRadius() * length_unit_;
	}
	if ( doEdgeFillet) {
		f2 = *inst->EdgeRadius() * length_unit_;
	}

	const double tol = settings_.get<settings::Precision>().get();

	if ( x < tol || y < tol || d < tol) {
		Logger::Message(Logger::LOG_NOTICE, "Skipping zero sized profile:", inst);
		return nullptr;
	}

	double xx = -x+d;
	double xy = -y+d;
	double dy1 = 0.;
	double dy2 = 0.;
	double dx1 = 0.;
	double dx2 = 0.;
	if (hasSlope) {
		dy1 = tan(slope) * x;
		dy2 = tan(slope) * (x - d);
		dx1 = tan(slope) * y;
		dx2 = tan(slope) * (y - d);

		const double x1s = x; const double y1s = -y + d - dy1;
		const double x1e = -x + d; const double y1e = -y + d + dy2;
		const double x2s = -x + d - dx1; const double y2s = y;
		const double x2e = -x + d + dx2; const double y2e = -y + d;

		const double a1 = y1e - y1s;
		const double b1 = x1s - x1e;
		const double c1 = a1*x1s + b1*y1s;

		const double a2 = y2e - y2s;
		const double b2 = x2s - x2e;
		const double c2 = a2*x2s + b2*y2s;

		const double det = a1*b2 - a2*b1;

		if (std::fabs(det) < 1.e-5) {
			Logger::Message(Logger::LOG_NOTICE, "Legs do not intersect for:", inst);
			return nullptr;
		}

		xx = (b2*c1 - b1*c2) / det;
		xy = (a1*c2 - a2*c1) / det;
	}

	taxonomy::matrix4::ptr m4;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = !!inst->Position();
#endif
	if (has_position) {
		m4 = taxonomy::cast<taxonomy::matrix4>(map(inst->Position()));
	}

	return profile_helper(m4, {
		{{-x,-y}},
		{{x,-y}},
		{{x,-y + d - dy1},{f2} },
		{{xx, xy},{f1} },
		{{-x + d - dx1,y},{f2} },
		{{-x,y}}
	});
}
