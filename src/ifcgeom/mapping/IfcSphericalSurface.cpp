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

#ifdef SCHEMA_HAS_IfcSphericalSurface

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcSphericalSurface* inst) {
	return nullptr;

	/*
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(inst->Position(), trsf);

	// IfcElementarySurface.Position has unit scale factor
	face = BRepBuilderAPI_MakeFace(new Geom_SphericalSurface(gp::XOY(), inst->Radius() * length_unit_), getValue(GV_PRECISION)).Face().Moved(trsf);
	return true;
	*/
}

#endif
