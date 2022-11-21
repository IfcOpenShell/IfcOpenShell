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

#include <gp_Pln.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <TopoDS_Face.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRectangularTrimmedSurface* l, TopoDS_Shape& face) {
	if (!l->BasisSurface()->declaration().is(IfcSchema::IfcPlane::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BasisSurface:", l->BasisSurface());
		return false;
	}
	gp_Pln pln;
	IfcGeom::Kernel::convert((IfcSchema::IfcPlane*) l->BasisSurface(), pln);

	BRepBuilderAPI_MakeFace mf(pln, l->U1(), l->U2(), l->V1(), l->V2());

	face = mf.Face();

	return true;
}
