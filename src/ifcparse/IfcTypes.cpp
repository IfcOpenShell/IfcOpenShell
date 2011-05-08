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

#include "StdFail_NotDone.hxx"

#include "../ifcparse/IfcTypes.h"
#include "../ifcparse/IfcEnum.h"

using namespace IfcSchema;

#define IFC_PARSE_SOURCE
#include "../ifcparse/IfcSchema.h"
#undef IFC_PARSE_SOURCE

bool IfcGeom::convert_shape(const IfcEntity L, TopoDS_Shape &result) {
	if ( ! L ) return false;
#define IFC_SHAPE_SRC
#include "../ifcparse/IfcSchema.h"
#undef IFC_SHAPE_SRC
	std::cout << "[Error] Failed to interpret:" << std::endl << L->toString() << std::endl;
	return false;
}

bool IfcGeom::convert_wire(const IfcEntity L, TopoDS_Wire &result) {
	if ( ! L ) return false;
#define IFC_WIRE_SRC
#include "../ifcparse/IfcSchema.h"
#undef IFC_WIRE_SRC
	std::cout << "[Error] Failed to interpret:" << std::endl << L->toString() << std::endl;
	return false;
}

bool IfcGeom::convert_face(const IfcEntity L, TopoDS_Face &result) {
	if ( ! L ) return false;
	TopoDS_Wire wire;
#define IFC_FACE_SRC
#include "../ifcparse/IfcSchema.h"
#undef IFC_FACE_SRC
	std::cout << "[Error] Failed to interpret:" << std::endl << L->toString() << std::endl;
	return false;
}
