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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcIShapeProfileDef* l, TopoDS_Shape& face) {
	const double x1 = l->OverallWidth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double y = l->OverallDepth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d1 = l->WebThickness() / 2.0f  * getValue(GV_LENGTH_UNIT);
	const double dy1 = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);

	bool doFillet1 = !!l->FilletRadius();
	double f1 = 0.;
	if ( doFillet1 ) {
		f1 = *l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}

	bool doFillet2 = doFillet1;
	double x2 = x1, dy2 = dy1, f2 = f1;

	// @todo in IFC4 a IfcAsymmetricIShapeProfileDef is not a subtype anymore of IfcIShapeProfileDef!
	if (l->declaration().is(IfcSchema::IfcAsymmetricIShapeProfileDef::Class())) {
		IfcSchema::IfcAsymmetricIShapeProfileDef* assym = (IfcSchema::IfcAsymmetricIShapeProfileDef*) l;
		x2 = assym->TopFlangeWidth() / 2. * getValue(GV_LENGTH_UNIT);
		doFillet2 = !!assym->TopFlangeFilletRadius();
		if (doFillet2) {
			f2 = *assym->TopFlangeFilletRadius() * getValue(GV_LENGTH_UNIT);
		}
		if (assym->TopFlangeThickness()) {
			dy2 = *assym->TopFlangeThickness() * getValue(GV_LENGTH_UNIT);
		}
	}	

	if ( x1 < ALMOST_ZERO || x2 < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || dy1 < ALMOST_ZERO || dy2 < ALMOST_ZERO ) {
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

	double coords[24] = {-x1,-y, x1,-y, x1,-y+dy1, d1,-y+dy1, d1,y-dy2, x2,y-dy2, x2,y, -x2,y, -x2,y-dy2, -d1,y-dy2, -d1,-y+dy1, -x1,-y+dy1};
	int fillets[4] = {3,4,9,10};
	double radii[4] = {f1,f2,f2,f1};
	return profile_helper(12,coords,(doFillet1||doFillet2) ? 4 : 0,fillets,radii,trsf2d,face);
}
