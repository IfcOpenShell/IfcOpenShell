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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcIShapeProfileDef* l, TopoDS_Shape& face) {

	const bool doFillet1 = !!l->FilletRadius();
#ifdef SCHEMA_IfcIShapeProfileDef_HAS_FlangeEdgeRadius
	const bool doFlangeEdgeRadius = !!l->FlangeEdgeRadius();
	const bool hasSlope = !!l->FlangeSlope();
#else
	const bool doFlangeEdgeRadius = false;
#endif

	const double x1 = l->OverallWidth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double y = l->OverallDepth() / 2.0f * getValue(GV_LENGTH_UNIT);
	const double d1 = l->WebThickness() / 2.0f	* getValue(GV_LENGTH_UNIT);
	const double ft1 = l->FlangeThickness() * getValue(GV_LENGTH_UNIT);
#ifdef SCHEMA_IfcIShapeProfileDef_HAS_FlangeEdgeRadius
	const double slope = l->FlangeSlope().get_value_or(0.) * getValue(GV_PLANEANGLE_UNIT);
#endif

	double dy = 0.0f;
	double f1 = 0.0f;
	double f2 = 0.0f;
	double fe1 = 0.0f;
	double fe2 = 0.0f;
	double x2 = x1;
	double ft2 = ft1;

	if ( doFillet1 ) {
		f1 = *l->FilletRadius() * getValue(GV_LENGTH_UNIT);
	}
#ifdef SCHEMA_IfcIShapeProfileDef_HAS_FlangeEdgeRadius
	if (doFlangeEdgeRadius) {
		fe1 = *l->FlangeEdgeRadius() * getValue(GV_LENGTH_UNIT);
	}
	if (hasSlope) {
		dy = (x1 - d1) * tan(slope);
	}
#endif

	bool doFillet2 = doFillet1;

	// @todo in IFC4 a IfcAsymmetricIShapeProfileDef is not a subtype anymore of IfcIShapeProfileDef!
	if (l->declaration().is(IfcSchema::IfcAsymmetricIShapeProfileDef::Class())) {
		IfcSchema::IfcAsymmetricIShapeProfileDef* assym = (IfcSchema::IfcAsymmetricIShapeProfileDef*) l;
		x2 = assym->TopFlangeWidth() / 2. * getValue(GV_LENGTH_UNIT);
		doFillet2 = !!assym->TopFlangeFilletRadius();
		if (doFillet2) {
			f2 = *assym->TopFlangeFilletRadius() * getValue(GV_LENGTH_UNIT);
		}
		if (assym->TopFlangeThickness()) {
			ft2 = *assym->TopFlangeThickness() * getValue(GV_LENGTH_UNIT);
		}
	} else {
		f2 = f1;
		fe2 = fe1;
	}

	if ( x1 < ALMOST_ZERO || x2 < ALMOST_ZERO || y < ALMOST_ZERO || d1 < ALMOST_ZERO || ft1 < ALMOST_ZERO || ft2 < ALMOST_ZERO ) {
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

	double coords[24] = {
		-x1,-y,
		x1,-y,
		x1,-y+ft1,
		d1,-y+ft1+dy,
		d1,y-ft2-dy,
		x2,y-ft2,
		x2,y,
		-x2,y,
		-x2,y-ft2,
		-d1,y-ft2-dy,
		-d1,-y+ft1+dy,
		-x1,-y+ft1
	};
	int fillets[8] = {2,3,4,5,8,9,10,11};
	double radii[8] = {fe1,f1,f2,fe2,fe2,f2,f1,fe1};
	return util::profile_helper(12,coords,(doFillet1 || doFillet2 || doFlangeEdgeRadius) ? 8 : 0,fillets,radii,trsf2d,face);
}
