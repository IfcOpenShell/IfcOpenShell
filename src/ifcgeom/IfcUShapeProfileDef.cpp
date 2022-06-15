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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcUShapeProfileDef* l, TopoDS_Shape& face) {
	const bool doEdgeFillet = !!l->EdgeRadius();
	const bool doFillet = !!l->FilletRadius();
	const bool hasSlope = !!l->FlangeSlope();

	const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double x = l->FlangeWidth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d1 = l->WebThickness() * getValue(GV_LENGTH_UNIT);
	const double d2 = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);
	const double slope = l->FlangeSlope().get_value_or(0.) * getValue(GV_PLANEANGLE_UNIT);
	
	double dy1 = 0.0f;
	double dy2 = 0.0f;
	double f1 = 0.0f;
	double f2 = 0.0f;

	if (doFillet) {
		f1 = *l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}
	if (doEdgeFillet) {
		f2 = *l->EdgeRadius() * getValue(GV_LENGTH_UNIT);
	}

	if (hasSlope) {
		dy1 = (x - d1) * tan(slope);
		dy2 = x * tan(slope);
	}

	if ( x < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || d2 < ALMOST_ZERO ) {
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

	double coords[16] = {-x,-y, x,-y, x,-y+d2-dy2, -x+d1,-y+d2+dy1, -x+d1,y-d2-dy1, x,y-d2+dy2, x,y, -x,y};
	int fillets[4] = {2,3,4,5};
	double radii[4] = {f2,f1,f1,f2};
	return profile_helper(8, coords, (doFillet || doEdgeFillet) ? 4 : 0, fillets, radii, trsf2d, face);
}
