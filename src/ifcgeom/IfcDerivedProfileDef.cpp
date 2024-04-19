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
#include <TopoDS_Face.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcDerivedProfileDef* l, TopoDS_Shape& face) {
	TopoDS_Face f;
	gp_Trsf2d trsf2d;
	bool is_mirror = false;
#ifdef SCHEMA_HAS_IfcMirroredProfileDef
	if (l->as<IfcSchema::IfcMirroredProfileDef>()) {
		trsf2d.SetMirror(gp::Origin2d());
		is_mirror = true;
	}
#endif
	if (!is_mirror) {
		if (!IfcGeom::Kernel::convert(l->Operator(), trsf2d)) {
			return false;
		}
	}
	if (convert_face(l->ParentProfile(), f)) {
		gp_Trsf trsf = trsf2d;
		face = BRepBuilderAPI_Transform(f, trsf).Shape();
		return true;
	} else {
		return false;
	}
}
