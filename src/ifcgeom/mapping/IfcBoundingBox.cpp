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
#include <BRepPrimAPI_MakeBox.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcBoundingBox* l, TopoDS_Shape& shape) {
	const double dx = l->XDim() * getValue(GV_LENGTH_UNIT);
	const double dy = l->YDim() * getValue(GV_LENGTH_UNIT);
	const double dz = l->ZDim() * getValue(GV_LENGTH_UNIT);

	gp_Pnt corner;
	IfcGeom::Kernel::convert(l->Corner(), corner);
	BRepPrimAPI_MakeBox builder(corner, dx, dy, dz);

	shape = builder.Solid();

	return true;
}
