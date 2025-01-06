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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcZShapeProfileDef* inst) {
	const double x = inst->FlangeWidth() * length_unit_;
	const double y = inst->Depth() / 2.0f * length_unit_;
	const double dx = inst->WebThickness() / 2.0f  * length_unit_;
	const double dy = inst->FlangeThickness() * length_unit_;

	bool doFillet = !!inst->FilletRadius();
	bool doEdgeFillet = !!inst->EdgeRadius();
	
	double f1 = 0.;
	double f2 = 0.;

	if ( doFillet ) {
		f1 = *inst->FilletRadius() * length_unit_;
	}
	if ( doEdgeFillet ) {
		f2 = *inst->EdgeRadius() * length_unit_;
	}

	const double tol = settings_.get<settings::Precision>().get();

	if (x < tol || y < tol || dx < tol || dy < tol) {
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
		{{-dx,-y}},
		{{x,-y}},
		{{x,-y + dy},{ f2}},
		{{dx,-y + dy},{ f1}},
		{{dx,y}},
		{{-x,y}},
		{{-x,y - dy},{ f2}},
		{{-dx,y - dy},{ f1}}
	});
}
