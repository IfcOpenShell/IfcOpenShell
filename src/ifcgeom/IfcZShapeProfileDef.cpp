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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcZShapeProfileDef* l, TopoDS_Shape& face) {
	const double x = l->FlangeWidth() * getValue(GV_LENGTH_UNIT);
	const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double dx = l->WebThickness() / 2.0f  * getValue(GV_LENGTH_UNIT);
	const double dy = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);

	bool doFillet = !!l->FilletRadius();
	bool doEdgeFillet = !!l->EdgeRadius();
	
	double f1 = 0.;
	double f2 = 0.;

	if ( doFillet ) {
		f1 = *l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}
	if ( doEdgeFillet ) {
		f2 = *l->EdgeRadius() * getValue(GV_LENGTH_UNIT);
	}

	if ( x == 0.0f || y == 0.0f || dx == 0.0f || dy == 0.0f ) {
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

	double coords[16] = {-dx,-y, x,-y, x,-y+dy, dx,-y+dy, dx,y, -x,y, -x,y-dy, -dx,y-dy};
	int fillets[4] = {2,3,6,7};
	double radii[4] = {f2,f1,f2,f1};
	return profile_helper(8,coords,(doFillet || doEdgeFillet) ? 4 : 0,fillets,radii,trsf2d,face);
}
