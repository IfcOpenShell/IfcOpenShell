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

#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <Geom_Circle.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCircle* l, Handle(Geom_Curve)& curve) {
	const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
	if ( r < ALMOST_ZERO ) { 
		Logger::Message(Logger::LOG_ERROR, "Radius not greater than zero for:", l);
		return false;
	}
	gp_Trsf trsf;
	IfcSchema::IfcAxis2Placement* placement = l->Position();
	if (placement->as<IfcSchema::IfcAxis2Placement3D>()) {
		IfcGeom::Kernel::convert(placement->as<IfcSchema::IfcAxis2Placement3D>(),trsf);
	} else {
		gp_Trsf2d trsf2d;
		IfcGeom::Kernel::convert(placement->as<IfcSchema::IfcAxis2Placement2D>(),trsf2d);
		trsf = trsf2d;
	}
	gp_Ax2 ax = gp_Ax2().Transformed(trsf);
	curve = new Geom_Circle(ax, r);
	return true;
}
