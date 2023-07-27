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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcSurfaceOfLinearExtrusion* inst) {
	return nullptr;

	/*
	TopoDS_Wire wire;
	if ( !convert_wire(inst->SweptCurve(), wire) ) {
		TopoDS_Face face;
		if ( !convert_face(inst->SweptCurve(),face) ) return false;
		TopExp_Explorer exp(face, TopAbs_WIRE);
		wire = TopoDS::Wire(exp.Current());
	}
	const double height = inst->Depth() * length_unit_;
	
	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptSurface_Position_IS_OPTIONAL
	has_position = inst->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(inst->Position(), trsf);
	}

	gp_Dir dir;
	convert(inst->ExtrudedDirection(),dir);

	shape = BRepPrimAPI_MakePrism(wire, height*dir);
	
	if (has_position) {
		// IfcSweptSurface.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}
	
	return !shape.IsNull();
	*/
}
