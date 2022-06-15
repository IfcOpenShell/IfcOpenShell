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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcLShapeProfileDef* l, TopoDS_Shape& face) {
	const bool hasSlope = !!l->LegSlope();
	const bool doEdgeFillet = !!l->EdgeRadius();
	const bool doFillet = !!l->FilletRadius();

	const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double x = l->Width().get_value_or(l->Depth()) / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d = l->Thickness() * getValue(GV_LENGTH_UNIT);
	const double slope = l->LegSlope().get_value_or(0.) * getValue(GV_PLANEANGLE_UNIT);
	
	double f1 = 0.0f;
	double f2 = 0.0f;
	if (doFillet) {
		f1 = *l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}
	if ( doEdgeFillet) {
		f2 = *l->EdgeRadius() * getValue(GV_LENGTH_UNIT);
	}

	if ( x < ALMOST_ZERO || y < ALMOST_ZERO || d < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l);
		return false;
	}

	double xx = -x+d;
	double xy = -y+d;
	double dy1 = 0.;
	double dy2 = 0.;
	double dx1 = 0.;
	double dx2 = 0.;
	if (hasSlope) {
		dy1 = tan(slope) * x;
		dy2 = tan(slope) * (x - d);
		dx1 = tan(slope) * y;
		dx2 = tan(slope) * (y - d);

		const double x1s = x; const double y1s = -y + d - dy1;
		const double x1e = -x + d; const double y1e = -y + d + dy2;
		const double x2s = -x + d - dx1; const double y2s = y;
		const double x2e = -x + d + dx2; const double y2e = -y + d;

		const double a1 = y1e - y1s;
		const double b1 = x1s - x1e;
		const double c1 = a1*x1s + b1*y1s;

		const double a2 = y2e - y2s;
		const double b2 = x2s - x2e;
		const double c2 = a2*x2s + b2*y2s;

		const double det = a1*b2 - a2*b1;

		if (ALMOST_THE_SAME(det, 0.)) {
			Logger::Message(Logger::LOG_NOTICE, "Legs do not intersect for:",l);
			return false;
		}

		xx = (b2*c1 - b1*c2) / det;
		xy = (a1*c2 - a2*c1) / det;
	}

	gp_Trsf2d trsf2d;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf2d);
	}

	double coords[12] = {-x,-y, x,-y, x,-y+d-dy1, xx, xy, -x+d-dx1,y, -x,y};
	int fillets[3] = {2,3,4};
	double radii[3] = {f2,f1,f2};
	return profile_helper(6,coords,doFillet ? 3 : 0,fillets,radii,trsf2d,face);
}
