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
#include <BRepPrimAPI_MakeCylinder.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRightCircularCylinder* l, TopoDS_Shape& shape) {
	const double r = l->Radius() * getValue(GV_LENGTH_UNIT);
	const double h = l->Height() * getValue(GV_LENGTH_UNIT);

	BRepPrimAPI_MakeCylinder builder(r, h);
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(l->Position(),trsf);
	
	// IfcCsgPrimitive3D.Position has unit scale factor
	shape = builder.Solid().Moved(trsf);

	return true;
}
