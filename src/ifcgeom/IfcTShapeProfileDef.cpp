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
#include "../ifcgeom_schema_agnostic/profile_helper.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTShapeProfileDef* l, TopoDS_Shape& face) {
	const bool doFlangeEdgeFillet = !!l->FlangeEdgeRadius();
	const bool doWebEdgeFillet = !!l->WebEdgeRadius();
	const bool doFillet = !!l->FilletRadius();
	const bool hasFlangeSlope = !!l->FlangeSlope();
	const bool hasWebSlope = !!l->WebSlope();

	const double y = l->Depth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double x = l->FlangeWidth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d1 = l->WebThickness() * getValue(GV_LENGTH_UNIT);
	const double d2 = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);
	const double flangeSlope = hasFlangeSlope ? (*l->FlangeSlope() * getValue(GV_PLANEANGLE_UNIT)) : 0.;
	const double webSlope = hasWebSlope ? (*l->WebSlope() * getValue(GV_PLANEANGLE_UNIT)) : 0.;

	if ( x < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || d2 < ALMOST_ZERO ) {
		Logger::Message(Logger::LOG_NOTICE,"Skipping zero sized profile:",l);
		return false;
	}
	
	double dy1 = 0.0f;
	double dy2 = 0.0f;
	double dx1 = 0.0f;
	double dx2 = 0.0f;
	double f1 = 0.0f;
	double f2 = 0.0f;
	double f3 = 0.0f;

	if (doFillet) {
		f1 = *l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}
	if (doWebEdgeFillet) {
		f2 = *l->WebEdgeRadius() * getValue(GV_LENGTH_UNIT);
	}
	if (doFlangeEdgeFillet) {
		f3 = *l->FlangeEdgeRadius() * getValue(GV_LENGTH_UNIT);
	}

	double xx, xy;
	if (hasFlangeSlope) {
		dy1 = (x / 2. - d1) * tan(flangeSlope);
		dy2 = x / 2. * tan(flangeSlope);
	}
	if (hasWebSlope) {
		dx1 = (y - d2) * tan(webSlope);
		dx2 = y * tan(webSlope);
	}
	if (hasWebSlope || hasFlangeSlope) {
		const double x1s = d1/2. - dx2; const double y1s = -y;
		const double x1e = d1/2. + dx1; const double y1e = y - d2;
		const double x2s = x; const double y2s = y - d2 + dy2;
		const double x2e = d1/2.; const double y2e = y - d2 - dy1;

		const double a1 = y1e - y1s;
		const double b1 = x1s - x1e;
		const double c1 = a1*x1s + b1*y1s;

		const double a2 = y2e - y2s;
		const double b2 = x2s - x2e;
		const double c2 = a2*x2s + b2*y2s;

		const double det = a1*b2 - a2*b1;

		if (ALMOST_THE_SAME(det, 0.)) {
			Logger::Message(Logger::LOG_NOTICE, "Web and flange do not intersect for:",l);
			return false;
		}

		xx = (b2*c1 - b1*c2) / det;
		xy = (a1*c2 - a2*c1) / det;
	} else {
		xx = d1 / 2;
		xy = y - d2;
	}

	gp_Trsf2d trsf2d;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf2d);
	}

	double coords[16] = {d1/2.-dx2,-y, xx,xy, x,y-d2+dy2, x,y, -x,y, -x,y-d2+dy2, -xx,xy, -d1/2.+dx2,-y};
	int fillets[6] = {0,1,2,5,6,7};
	double radii[6] = {f2,f1,f3,f3,f1,f2};
	return util::profile_helper(8, coords, (doFillet || doWebEdgeFillet || doFlangeEdgeFillet) ? 6 : 0, fillets, radii, trsf2d, face);
}
