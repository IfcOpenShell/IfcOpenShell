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

#include <BRepBuilderAPI_MakeFace.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <ShapeFix_Shape.hxx>
#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom_schema_agnostic/wire_utils.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcAnnotationFillArea* l, TopoDS_Shape& face) {
	TopoDS_Wire outer_boundary;
	if (!convert_wire(l->OuterBoundary(), outer_boundary)) {
		return false;
	}

	util::assert_closed_wire(outer_boundary, getValue(GV_PRECISION));

	BRepBuilderAPI_MakeFace mf(outer_boundary);

	if (l->InnerBoundaries()) {
		IfcSchema::IfcCurve::list::ptr inner_boundaries = *l->InnerBoundaries();

		for(IfcSchema::IfcCurve::list::it it = inner_boundaries->begin(); it != inner_boundaries->end(); ++it) {
			TopoDS_Wire hole;
			if (convert_wire(*it, hole)) {
				util::assert_closed_wire(hole, getValue(GV_PRECISION));
				mf.Add(hole);
			}
		}
	}

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();
	face = sfs.Shape();

	return true;
}
