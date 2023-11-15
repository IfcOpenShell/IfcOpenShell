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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcIShapeProfileDef* inst) {
	const bool doFillet1 = !!inst->FilletRadius();
#ifdef SCHEMA_IfcIShapeProfileDef_HAS_FlangeEdgeRadius
	const bool doFlangeEdgeRadius = !!inst->FlangeEdgeRadius();
	const bool hasSlope = !!inst->FlangeSlope();
#else
	const bool doFlangeEdgeRadius = false;
#endif

	const double x1 = inst->OverallWidth() / 2.0f * length_unit_;
	const double y = inst->OverallDepth() / 2.0f * length_unit_;
	const double d1 = inst->WebThickness() / 2.0f  * length_unit_;
	const double ft1 = inst->FlangeThickness() * length_unit_;
#ifdef SCHEMA_IfcIShapeProfileDef_HAS_FlangeEdgeRadius
	const double slope = inst->FlangeSlope().get_value_or(0.) * angle_unit_;
#endif

	double dy = 0.;
	double f1 = 0.;
	double f2 = 0.;
	double fe1 = 0.;
	double fe2 = 0.;
	double x2 = x1;
	double ft2 = ft1;

	if (doFillet1) {
		f1 = *inst->FilletRadius() * length_unit_;
	}
#ifdef SCHEMA_IfcIShapeProfileDef_HAS_FlangeEdgeRadius
	if (doFlangeEdgeRadius) {
		fe1 = *inst->FlangeEdgeRadius() * length_unit_;
	}
	if (hasSlope) {
		dy = (x1 - d1) * tan(slope);
	}
#endif

	bool doFillet2 = doFillet1;

	// @todo in IFC4 a IfcAsymmetricIShapeProfileDef is not a subtype anymore of IfcIShapeProfileDef!
	if (inst->declaration().is(IfcSchema::IfcAsymmetricIShapeProfileDef::Class())) {
		IfcSchema::IfcAsymmetricIShapeProfileDef* assym = (IfcSchema::IfcAsymmetricIShapeProfileDef*) inst;
		x2 = assym->TopFlangeWidth() / 2. * length_unit_;
		doFillet2 = !!assym->TopFlangeFilletRadius();
		if (doFillet2) {
			f2 = *assym->TopFlangeFilletRadius() * length_unit_;
		}
		if (assym->TopFlangeThickness()) {
			ft2 = *assym->TopFlangeThickness() * length_unit_;
		}
	} else {
		f2 = f1;
		fe2 = fe1;
	}

	const double tol = settings_.get<settings::Precision>().get();

	if (x1 < tol || x2 < tol || y < tol || d1 < tol || ft1 < tol || ft2 < tol) {
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
		{{-x1,-y}},
		{{x1,-y}},
		{{x1,-y + ft1}, {fe1}},
		{{d1,-y + ft1 + dy},{ f1} },
		{{d1,y - ft2 - dy},{f2} },
		{{x2,y - ft2}, {fe2}},
		{{x2,y}},
		{{-x2,y}},
		{{-x2,y - ft2}, {fe2}},
		{{-d1,y - ft2 - dy},{f2} },
		{{-d1,-y + ft1 + dy},{f1} },
		{{-x1,-y + ft1}, {fe1}}
	});
}
