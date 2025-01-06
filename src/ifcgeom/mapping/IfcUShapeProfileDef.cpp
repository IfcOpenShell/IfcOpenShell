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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcUShapeProfileDef* inst) {
	const bool doEdgeFillet = !!inst->EdgeRadius();
	const bool doFillet = !!inst->FilletRadius();
	const bool hasSlope = !!inst->FlangeSlope();

	const double y = inst->Depth() / 2.0f * length_unit_;
	const double x = inst->FlangeWidth() / 2.0f * length_unit_;
	const double d1 = inst->WebThickness() * length_unit_;
	const double d2 = inst->FlangeThickness() * length_unit_;
	const double slope = inst->FlangeSlope().get_value_or(0.) * angle_unit_;
	
	double dy1 = 0.0f;
	double dy2 = 0.0f;
	double f1 = 0.0f;
	double f2 = 0.0f;

	if (doFillet) {
		f1 = *inst->FilletRadius() * length_unit_;
	}
	if (doEdgeFillet) {
		f2 = *inst->EdgeRadius() * length_unit_;
	}

	if (hasSlope) {
		dy1 = (x - d1) * tan(slope);
		dy2 = x * tan(slope);
	}

	const double tol = settings_.get<settings::Precision>().get();

	if (x < tol || y < tol || d1 < tol || d2 < tol) {
		Logger::Message(Logger::LOG_NOTICE, "Skipping zero sized profile:", inst);
		return nullptr;
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
		{{x,-y + d2 - dy2},{f2} },
		{{-x + d1,-y + d2 + dy1},{ f1}},
		{{-x + d1,y - d2 - dy1},{ f1}},
		{{x,y - d2 + dy2},{ f2}},
		{{x,y}},
		{{-x,y}}
	});
}
