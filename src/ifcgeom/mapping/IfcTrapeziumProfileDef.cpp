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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcTrapeziumProfileDef* inst) {
	const double x1 = inst->BottomXDim() / 2. * length_unit_;
	const double w = inst->TopXDim() * length_unit_;
	const double dx = inst->TopXOffset() * length_unit_;
	const double y = inst->YDim() / 2.  * length_unit_;

	// See: https://forums.buildingsmart.org/t/how-are-the-sides-of-ifctrapeziumprofiledefs-bounding-box-calculated-in-most-implementations/2945/8
	// The trapezium x center should not be midway of BottomXDim but rather at the center of the overall bounding box.
	const double x_offset = ((std::min(dx, 0.) + std::max(w + dx, x1 * 2.)) / 2.) - x1;

	const double tol = settings_.get<settings::Precision>().get();

	if (x1 < tol || w < tol || y < tol) {
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
		{{-x1 - x_offset, -y}},
		{{+x1 - x_offset, -y}},
		{{-x1 + dx + w - x_offset, y}},
		{{-x1 + dx - x_offset, y}}
	});
}
