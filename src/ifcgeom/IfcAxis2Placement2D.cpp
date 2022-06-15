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

#include <gp_Pnt.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Dir2d.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Ax2d.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcAxis2Placement2D* l, gp_Trsf2d& trsf) {
	IN_CACHE(IfcAxis2Placement2D,l,gp_Trsf2d,trsf)
	gp_Pnt P; gp_Dir V (1,0,0);

	if (!l->Location()->declaration().is("IfcCartesianPoint")) {
		// only applicable to 4x3 rc2
		Logger::Error("Not implemented", l->Location());
		return false;
	}

	IfcGeom::Kernel::convert((const IfcSchema::IfcCartesianPoint*) l->Location(),P);
	if (l->RefDirection()) {
		IfcGeom::Kernel::convert(l->RefDirection(), V);
	}

	gp_Ax2d axis(gp_Pnt2d(P.X(),P.Y()), gp_Dir2d(V.X(),V.Y()));
	
	if (!axis_equal(axis, gp_Ax2d(), getValue(GV_PRECISION))) {
		trsf.SetTransformation(axis, gp_Ax2d());
	}

	CACHE(IfcAxis2Placement2D,l,trsf)
	return true;
}
