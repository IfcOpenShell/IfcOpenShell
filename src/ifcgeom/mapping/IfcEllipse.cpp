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
#include <Geom_Ellipse.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcEllipse* l, Handle(Geom_Curve)& curve) {
	double x = l->SemiAxis1() * getValue(GV_LENGTH_UNIT);
	double y = l->SemiAxis2() * getValue(GV_LENGTH_UNIT);
	if (x < ALMOST_ZERO || y < ALMOST_ZERO) { 
		Logger::Message(Logger::LOG_ERROR, "Radius not greater than zero for:", l);
		return false;
	}
	// Open Cascade does not allow ellipses of which the minor radius
	// is greater than the major radius. Hence, in this case, the
	// ellipse is rotated. Note that special care needs to be taken
	// when creating a trimmed curve off of an ellipse like this.
	const bool rotated = y > x;
	gp_Trsf trsf;
	
	IfcSchema::IfcAxis2Placement* placement = l->Position();
	if (placement->as<IfcSchema::IfcAxis2Placement3D>()) {
		IfcGeom::Kernel::convert(placement->as<IfcSchema::IfcAxis2Placement3D>(), trsf);
	} else {
		gp_Trsf2d trsf2d;
		IfcGeom::Kernel::convert(placement->as<IfcSchema::IfcAxis2Placement2D>(), trsf2d);
		trsf = trsf2d;
	}

	gp_Ax2 ax = gp_Ax2();
	if (rotated) {
		ax.Rotate(ax.Axis(), M_PI / 2.);
		std::swap(x, y);
	}
	ax.Transform(trsf);
	curve = new Geom_Ellipse(ax, x, y);
	return true;
}
