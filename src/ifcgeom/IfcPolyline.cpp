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

#include <gp_Pnt.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <TopoDS_Wire.hxx>
#include "../ifcgeom/IfcGeom.h"

#define _USE_MATH_DEFINES
#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPolyline* l, TopoDS_Wire& result) {
	IfcSchema::IfcCartesianPoint::list::ptr points = l->Points();

	// Parse and store the points in a sequence
	TColgp_SequenceOfPnt polygon;
	for(IfcSchema::IfcCartesianPoint::list::it it = points->begin(); it != points->end(); ++ it) {
		gp_Pnt pnt;
		IfcGeom::Kernel::convert(*it, pnt);
		polygon.Append(pnt);
	}

	// @todo the strict tolerance should also govern these arbitrary precision increases
	const double eps = getValue(GV_PRECISION) * 10;
	const bool closed_by_proximity = polygon.Length() >= 3 && polygon.First().Distance(polygon.Last()) < eps;
	if (closed_by_proximity) {
		// tfk: note 1-based
		polygon.Remove(polygon.Length());
	}

	// Remove points that are too close to one another
	remove_duplicate_points_from_loop(polygon, closed_by_proximity, eps);

	if (polygon.Length() < 2) {
		// We somehow need to signal we fail this curve on purpose not to trigger an error.
		BRep_Builder B;
		B.MakeWire(result);
		return false;
	}
	
	BRepBuilderAPI_MakePolygon w;
	for (int i = 1; i <= polygon.Length(); ++i) {
		w.Add(polygon.Value(i));
	}

	if (closed_by_proximity) {
		w.Close();
	}

	result = w.Wire();
	return true;
}
