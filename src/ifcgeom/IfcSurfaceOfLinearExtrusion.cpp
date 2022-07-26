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

#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Trsf.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSurfaceOfLinearExtrusion* l, TopoDS_Shape& shape) {
	TopoDS_Wire wire;
	if ( !convert_wire(l->SweptCurve(), wire) ) {
		TopoDS_Face face;
		if ( !convert_face(l->SweptCurve(),face) ) return false;
		TopExp_Explorer exp(face, TopAbs_WIRE);
		wire = TopoDS::Wire(exp.Current());
	}
	const double height = l->Depth() * getValue(GV_LENGTH_UNIT);
	
	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptSurface_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}

	gp_Dir dir;
	convert(l->ExtrudedDirection(),dir);

	shape = BRepPrimAPI_MakePrism(wire, height*dir);
	
	if (has_position) {
		// IfcSweptSurface.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}
	
	return !shape.IsNull();
}
