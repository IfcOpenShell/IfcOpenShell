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

#include "../ifcgeom/IfcGeom.h"
#include "../ifcgeom_schema_agnostic/wire_utils.h"

#include <gp_Pnt.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <TopoDS_Wire.hxx>
#include <TopTools_ListOfShape.hxx>

#define _USE_MATH_DEFINES
#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPolyLoop* l, TopoDS_Wire& result) {
	IfcSchema::IfcCartesianPoint::list::ptr points = l->Polygon();

	// Parse and store the points in a sequence
	TColgp_SequenceOfPnt polygon;
	for(IfcSchema::IfcCartesianPoint::list::it it = points->begin(); it != points->end(); ++ it) {
		gp_Pnt pnt;
		IfcGeom::Kernel::convert(*it, pnt);
		polygon.Append(pnt);
	}

	// A loop should consist of at least three vertices
	int original_count = polygon.Length();
	if (original_count < 3) {
		Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", l);
		return false;
	}

	// Remove points that are too close to one another
	const double eps = getValue(GV_PRECISION) * 10;
	remove_duplicate_points_from_loop(polygon, true, eps);

	int count = polygon.Length();
	if (original_count - count != 0) {
		std::stringstream ss; ss << (original_count - count) << " edges removed for:"; 
		Logger::Message(Logger::LOG_WARNING, ss.str(), l);
	}

	if (count < 3) {
		Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", l);
		return false;
	}

	BRepBuilderAPI_MakePolygon w;
	for (int i = 1; i <= polygon.Length(); ++i) {
		w.Add(polygon.Value(i));
	}
	w.Close();

	result = w.Wire();

	TopTools_ListOfShape results;
	if (getValue(GV_NO_WIRE_INTERSECTION_CHECK) < 0. && util::wire_intersections(result, results, get_wire_intersection_tolerance(result), getValue(GV_PRECISION))) {
		Logger::Error("Self-intersections with " + boost::lexical_cast<std::string>(results.Extent()) + " cycles detected", l);
		util::select_largest(results, result);
	}

	return true;
}
