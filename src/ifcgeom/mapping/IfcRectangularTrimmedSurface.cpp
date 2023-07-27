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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRectangularTrimmedSurface* inst) {
	// @todo we'll need to add support for p-curves at some point, but not now.
	return nullptr;

	/*
	if (!inst->BasisSurface()->declaration().is(IfcSchema::IfcPlane::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BasisSurface:", inst->BasisSurface());
		return false;
	}
	gp_Pln pln;
	IfcGeom::Kernel::convert((IfcSchema::IfcPlane*) inst->BasisSurface(), pln);

	BRepBuilderAPI_MakeFace mf(pln, inst->U1(), inst->U2(), inst->V1(), inst->V2());

	face = mf.Face();

	return true;
	*/
}
