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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcArbitraryProfileDefWithVoids* l, TopoDS_Shape& face) {
	TopoDS_Wire profile;
	if (!convert_wire(l->OuterCurve(), profile)) {
		return false;
	}

	util::assert_closed_wire(profile, getValue(GV_PRECISION));

	// @todo this is a discrepancy with IfcArbitraryClosedProfileDef without voids.
	// wire intersection code is not triggered this way.
	BRepBuilderAPI_MakeFace mf(profile);

	IfcSchema::IfcCurve::list::ptr voids = l->InnerCurves();

	for(IfcSchema::IfcCurve::list::it it = voids->begin(); it != voids->end(); ++it) {
		TopoDS_Wire hole;
		if (convert_wire(*it, hole)) {
			util::assert_closed_wire(hole, getValue(GV_PRECISION));
			mf.Add(hole);
		}
	}

	ShapeFix_Shape sfs(mf.Face());
	sfs.Perform();
	face = sfs.Shape();

	return true;
}
