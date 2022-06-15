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
#include <gp_Trsf.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <TopoDS_Wire.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPolygonalBoundedHalfSpace* l, TopoDS_Shape& shape) {
	TopoDS_Shape halfspace;
	if ( ! IfcGeom::Kernel::convert((IfcSchema::IfcHalfSpaceSolid*)l,halfspace) ) return false;	
	
	TopoDS_Wire wire;
	if ( ! convert_wire(l->PolygonalBoundary(),wire) || ! wire.Closed() ) return false;
	
	gp_Trsf trsf;
	if ( ! convert(l->Position(),trsf) ) return false;

	TColgp_SequenceOfPnt points;
	if (wire_to_sequence_of_point(wire, points)) {
		// Boolean subtractions not very robust for narrow operands, 
		// increase minimal point spacing to eliminate such shapes.
		const double t = getValue(GV_PRECISION) * 10.;
		remove_duplicate_points_from_loop(points, wire.Closed() != 0, t); // Note: wire always closed, as per if statement above
		remove_collinear_points_from_loop(points, wire.Closed() != 0, t);
		if (points.Length() < 3) {
			Logger::Message(Logger::LOG_ERROR, "Not enough points retained from:", l->PolygonalBoundary());
			return false;
		}
		sequence_of_point_to_wire(points, wire, wire.Closed() != 0);
	}

	TopoDS_Shape prism = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire),gp_Vec(0,0,200));
	gp_Trsf down; down.SetTranslation(gp_Vec(0,0,-100.0));
	
	// `trsf` and `down` both have a unit scale factor
	prism.Move(trsf*down);	
	
	shape = BRepAlgoAPI_Common(halfspace,prism);
	return true;
}
