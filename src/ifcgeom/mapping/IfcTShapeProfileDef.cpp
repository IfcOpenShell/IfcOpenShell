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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcTShapeProfileDef* inst) {
	const bool doFlangeEdgeFillet = !!inst->FlangeEdgeRadius();
	const bool doWebEdgeFillet = !!inst->WebEdgeRadius();
	const bool doFillet = !!inst->FilletRadius();
	const bool hasFlangeSlope = !!inst->FlangeSlope();
	const bool hasWebSlope = !!inst->WebSlope();

	const double y = inst->Depth() / 2.0f * length_unit_;
	const double x = inst->FlangeWidth() / 2.0f * length_unit_;
	const double d1 = inst->WebThickness() * length_unit_;
	const double d2 = inst->FlangeThickness() * length_unit_;
	const double flangeSlope = hasFlangeSlope ? (*inst->FlangeSlope() * angle_unit_) : 0.;
	const double webSlope = hasWebSlope ? (*inst->WebSlope() * angle_unit_) : 0.;

	const double tol = settings_.get<settings::Precision>().get();

	if (x < tol || y < tol || d1 < tol || d2 < tol) {
		Logger::Message(Logger::LOG_NOTICE, "Skipping zero sized profile:", inst);
		return nullptr;
	}
	
	double dy1 = 0.0f;
	double dy2 = 0.0f;
	double dx1 = 0.0f;
	double dx2 = 0.0f;
	double f1 = 0.0f;
	double f2 = 0.0f;
	double f3 = 0.0f;

	if (doFillet) {
		f1 = *inst->FilletRadius() * length_unit_;
	}
	if (doWebEdgeFillet) {
		f2 = *inst->WebEdgeRadius() * length_unit_;
	}
	if (doFlangeEdgeFillet) {
		f3 = *inst->FlangeEdgeRadius() * length_unit_;
	}

	double xx, xy;
	if (hasFlangeSlope) {
		dy1 = (x / 2. - d1) * tan(flangeSlope);
		dy2 = x / 2. * tan(flangeSlope);
	}
	if (hasWebSlope) {
		dx1 = (y - d2) * tan(webSlope);
		dx2 = y * tan(webSlope);
	}
	if (hasWebSlope || hasFlangeSlope) {
		const double x1s = d1/2. - dx2; const double y1s = -y;
		const double x1e = d1/2. + dx1; const double y1e = y - d2;
		const double x2s = x; const double y2s = y - d2 + dy2;
		const double x2e = d1/2.; const double y2e = y - d2 - dy1;

		const double a1 = y1e - y1s;
		const double b1 = x1s - x1e;
		const double c1 = a1*x1s + b1*y1s;

		const double a2 = y2e - y2s;
		const double b2 = x2s - x2e;
		const double c2 = a2*x2s + b2*y2s;

		const double det = a1*b2 - a2*b1;

		if (std::fabs(det) < 1.e-5) {
			Logger::Message(Logger::LOG_NOTICE, "Web and flange do not intersect for:", inst);
			return nullptr;
		}

		xx = (b2*c1 - b1*c2) / det;
		xy = (a1*c2 - a2*c1) / det;
	} else {
		xx = d1 / 2;
		xy = y - d2;
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
		{{d1 / 2. - dx2,-y},{ f2} },
		{{xx,xy},{ f1}},
		{{x,y - d2 + dy2},{ f3}},
		{{x,y}},
		{{-x,y}},
		{{-x,y - d2 + dy2},{f3}},
		{{-xx,xy},{f1}},
		{{-d1 / 2. + dx2,-y},{f2}}
	});
}
