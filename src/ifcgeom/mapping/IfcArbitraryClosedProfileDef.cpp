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

#include <TopoDS_Wire.hxx>
#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom_schema_agnostic/wire_utils.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcArbitraryClosedProfileDef* l, TopoDS_Shape& face) {
	TopoDS_Wire wire;
	if (!convert_wire(l->OuterCurve(), wire)) {
		return false;
	}

	util::assert_closed_wire(wire, getValue(GV_PRECISION));

	TopoDS_Compound f;
	bool success = util::convert_wire_to_faces(wire, f, {getValue(GV_NO_WIRE_INTERSECTION_CHECK) < 0., getValue(GV_NO_WIRE_INTERSECTION_TOLERANCE) < 0., 0., getValue(GV_PRECISION)});
	if (success) {
		face = f;
	}
	return success;
}
