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

#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

#ifdef SCHEMA_HAS_IfcCraneRailAShapeProfileDef
bool IfcGeom::Kernel::convert(const IfcSchema::IfcCraneRailAShapeProfileDef* l, TopoDS_Shape& face) {
	double oh = l->OverallHeight() * getValue(GV_LENGTH_UNIT);
	double bw2 = l->BaseWidth2() * getValue(GV_LENGTH_UNIT);
	double hw = l->HeadWidth() * getValue(GV_LENGTH_UNIT);
	double hd2 = l->HeadDepth2() * getValue(GV_LENGTH_UNIT);
	double hd3 = l->HeadDepth3() * getValue(GV_LENGTH_UNIT);
	double wt = l->WebThickness() * getValue(GV_LENGTH_UNIT);
	double bw4 = l->BaseWidth4() * getValue(GV_LENGTH_UNIT);
	double bd1 = l->BaseDepth1() * getValue(GV_LENGTH_UNIT);
	double bd2 = l->BaseDepth2() * getValue(GV_LENGTH_UNIT);
	double bd3 = l->BaseDepth3() * getValue(GV_LENGTH_UNIT);

	gp_Trsf2d trsf2d;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf2d);
	}

	double coords[28] = {
		-hw / 2., +oh / 2.,
		-hw / 2., +oh / 2. - hd3,
		-wt / 2., +oh / 2. - hd2,
		-wt / 2., -oh / 2. + bd2,
		-bw4 / 2., -oh / 2. + bd3,
		-bw2 / 2., -oh / 2. + bd1,
		-bw2 / 2., -oh / 2.,
		+bw2 / 2., -oh / 2.,
		+bw2 / 2., -oh / 2. + bd1,
		+bw4 / 2., -oh / 2. + bd3,
		+wt / 2., -oh / 2. + bd2,
		+wt / 2., +oh / 2. - hd2,
		+hw / 2., +oh / 2. - hd3,
		+hw / 2., +oh / 2.
	};

	return profile_helper(14, coords, 0, 0, 0, trsf2d, face);
}
#endif
