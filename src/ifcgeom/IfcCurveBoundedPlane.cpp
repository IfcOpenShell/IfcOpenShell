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
#include <gp_Ax3.hxx>
#include <gp_Pln.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <ShapeFix_Shape.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCurveBoundedPlane* l, TopoDS_Shape& face) {
	gp_Pln pln;
	if (!IfcGeom::Kernel::convert(l->BasisSurface(), pln)) {
		return false;
	}

	gp_Trsf trsf;
	trsf.SetTransformation(pln.Position(), gp::XOY());
	
	TopoDS_Wire outer;
	if (!convert_wire(l->OuterBoundary(), outer)) {
		return false;
	}
	
	BRepBuilderAPI_MakeFace mf(outer);

	if (!mf.IsDone() || mf.Shape().IsNull()) {
		Logger::Error("Invalid outer boundary:", l->OuterBoundary());
		return false;
	}
	
	IfcSchema::IfcCurve::list::ptr boundaries = l->InnerBoundaries();

	for (IfcSchema::IfcCurve::list::it it = boundaries->begin(); it != boundaries->end(); ++it) {
		TopoDS_Wire inner;
		if (convert_wire(*it, inner)) {
			mf.Add(inner);
		}
	}

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();

	// `trsf` consitutes the placement of the plane and therefore has unit scale factor
	face = TopoDS::Face(sfs.Shape()).Moved(trsf);
	
	return true;
}
