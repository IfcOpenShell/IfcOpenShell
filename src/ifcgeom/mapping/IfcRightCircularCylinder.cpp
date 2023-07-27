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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRightCircularCylinder* inst) {
	// @todo
	return nullptr;
	/*

	const double r = inst->Radius() * length_unit_;
	const double h = inst->Height() * length_unit_;

	BRepPrimAPI_MakeCylinder builder(r, h);
	gp_Trsf trsf;
	IfcGeom::Kernel::convert(inst->Position(),trsf);
	
	// IfcCsgPrimitive3D.Position has unit scale factor
	shape = builder.Solid().Moved(trsf);

	return true;
	*/
}
