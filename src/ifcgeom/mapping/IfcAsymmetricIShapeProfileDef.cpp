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
using namespace ifcopenshell::geometry;

#include "../profile_helper.h"

// In IFC2X3 IfcAsymmetricIShapeProfileDef is a subtype of IfcIShapeProfileDef and is
// therefore dispatched (and handled) by the IfcIShapeProfileDef mapping. From IFC4
// onwards it is a standalone subtype of IfcParameterizedProfileDef with its own
// Bottom*/Top* attributes, so nothing mapped it and the extrusion came out empty.
// The presence of the standalone BottomFlangeWidth attribute is the discriminator:
// it is only defined in the schemas where the type is standalone (IFC4 / IFC4X3).
#ifdef SCHEMA_IfcAsymmetricIShapeProfileDef_HAS_BottomFlangeWidth

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcAsymmetricIShapeProfileDef* inst) {
	// Bottom flange (half width), overall depth (half), web (half thickness).
	const double xb = inst->BottomFlangeWidth() / 2.0 * length_unit_;
	const double xt = inst->TopFlangeWidth() / 2.0 * length_unit_;
	const double y = inst->OverallDepth() / 2.0 * length_unit_;
	const double d1 = inst->WebThickness() / 2.0 * length_unit_;

	// Bottom flange thickness; top flange thickness defaults to the bottom one.
	const double ftb = inst->BottomFlangeThickness() * length_unit_;
	const double ftt = inst->TopFlangeThickness().get_value_or(inst->BottomFlangeThickness()) * length_unit_;

	// Optional fillet radii (web/flange transition) and flange edge radii.
	const double fb = inst->BottomFlangeFilletRadius().get_value_or(0.) * length_unit_;
	const double ft_top = inst->TopFlangeFilletRadius().get_value_or(0.) * length_unit_;
	const double feb = inst->BottomFlangeEdgeRadius().get_value_or(0.) * length_unit_;
	const double fet = inst->TopFlangeEdgeRadius().get_value_or(0.) * length_unit_;

	// Optional flange slopes: the inner edge of the flange rises towards the web.
	const double bottomSlope = inst->BottomFlangeSlope().get_value_or(0.) * angle_unit_;
	const double topSlope = inst->TopFlangeSlope().get_value_or(0.) * angle_unit_;
	const double dyb = (xb - d1) * tan(bottomSlope);
	const double dyt = (xt - d1) * tan(topSlope);

	const double tol = settings_.get<settings::Precision>().get();

	if (xb < tol || xt < tol || y < tol || d1 < tol || ftb < tol || ftt < tol) {
		logger_.Message(Logger::LOG_NOTICE, "GEO", 264, "Skipping zero sized profile:", inst);
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

	// Twelve corner points, running counter-clockwise from the bottom-left, with the
	// bottom flange (xb) possibly wider than the top flange (xt). Fillet/edge radii are
	// attached to the corner they round, matching the symmetric IfcIShapeProfileDef.
	return profile_helper(m4, {
		{{-xb,-y}},
		{{xb,-y}},
		{{xb,-y + ftb}, {feb}},
		{{d1,-y + ftb + dyb},{fb} },
		{{d1,y - ftt - dyt},{ft_top} },
		{{xt,y - ftt}, {fet}},
		{{xt,y}},
		{{-xt,y}},
		{{-xt,y - ftt}, {fet}},
		{{-d1,y - ftt - dyt},{ft_top} },
		{{-d1,-y + ftb + dyb},{fb} },
		{{-xb,-y + ftb}, {feb}}
	});
}

#endif
