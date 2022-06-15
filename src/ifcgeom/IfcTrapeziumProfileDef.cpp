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

#include <gp_Trsf2d.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTrapeziumProfileDef* l, TopoDS_Shape& face) {
	const double x1 = l->BottomXDim() / 2. * getValue(GV_LENGTH_UNIT);
	const double w = l->TopXDim() * getValue(GV_LENGTH_UNIT);
	const double dx = l->TopXOffset() * getValue(GV_LENGTH_UNIT);
	const double y = l->YDim() / 2.  * getValue(GV_LENGTH_UNIT);

	// See: https://forums.buildingsmart.org/t/how-are-the-sides-of-ifctrapeziumprofiledefs-bounding-box-calculated-in-most-implementations/2945/8
	// The trapezium x center should not be midway of BottomXDim but rather at the center of the overall bounding box.
	const double x_offset = ((std::min(dx, 0.) + std::max(w + dx, x1 * 2.)) / 2.) - x1;

	if ( x1 < ALMOST_ZERO || w < ALMOST_ZERO || y < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l);
		return false;
	}

	gp_Trsf2d trsf2d;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf2d);
	}

	double coords[8] = {
		-x1 - x_offset, -y,
		+x1 - x_offset, -y,
		-x1 + dx + w - x_offset, y,
		-x1 + dx - x_offset,y
	};
	return profile_helper(4,coords,0,0,0,trsf2d,face);
}
