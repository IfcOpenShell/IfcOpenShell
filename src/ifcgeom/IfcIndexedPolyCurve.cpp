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
#include <GC_MakeCircle.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <TopoDS_Wire.hxx>
#include <BRep_Tool.hxx>
#include "../ifcgeom/IfcGeom.h"

#define _USE_MATH_DEFINES
#define Kernel MAKE_TYPE_NAME(Kernel)

#ifdef SCHEMA_HAS_IfcIndexedPolyCurve

bool IfcGeom::Kernel::convert(const IfcSchema::IfcIndexedPolyCurve* l, TopoDS_Wire& result) {
	
	IfcSchema::IfcCartesianPointList* point_list = l->Points();
	std::vector< std::vector<double> > coordinates;
	if (point_list->as<IfcSchema::IfcCartesianPointList2D>()) {
		coordinates = point_list->as<IfcSchema::IfcCartesianPointList2D>()->CoordList();
	} else if (point_list->as<IfcSchema::IfcCartesianPointList3D>()) {
		coordinates = point_list->as<IfcSchema::IfcCartesianPointList3D>()->CoordList();
	}

	std::vector<gp_Pnt> points;
	points.reserve(coordinates.size());
	for (std::vector< std::vector<double> >::const_iterator it = coordinates.begin(); it != coordinates.end(); ++it) {
		const std::vector<double>& coords = *it;
		points.push_back(gp_Pnt(
			coords.size() < 1 ? 0. : coords[0] * getValue(GV_LENGTH_UNIT),
			coords.size() < 2 ? 0. : coords[1] * getValue(GV_LENGTH_UNIT),
			coords.size() < 3 ? 0. : coords[2] * getValue(GV_LENGTH_UNIT)));
	}

	int max_index = points.size();

	BRepBuilderAPI_MakeWire w;

	// ignored, just for capturing the curve parameters on the null check
	double u, v;

	if(l->Segments()) {
		aggregate_of_instance::ptr segments = *l->Segments();
		for (aggregate_of_instance::it it = segments->begin(); it != segments->end(); ++it) {
			IfcUtil::IfcBaseClass* segment = *it;
			if (segment->declaration().is(IfcSchema::IfcLineIndex::Class())) {
				IfcSchema::IfcLineIndex* line = (IfcSchema::IfcLineIndex*) segment;
				std::vector<int> indices = *line;
				gp_Pnt previous;
				for (std::vector<int>::const_iterator jt = indices.begin(); jt != indices.end(); ++jt) {
					if (*jt < 1 || *jt > max_index) {
						throw IfcParse::IfcException("IfcIndexedPolyCurve index out of bounds for index " + boost::lexical_cast<std::string>(*jt));
					}
					const gp_Pnt& current = points[*jt - 1];
					if (jt != indices.begin()) {
						BRepBuilderAPI_MakeEdge me(previous, current);
						if (me.IsDone() && !BRep_Tool::Curve(me.Edge(), u, v).IsNull()) {
							w.Add(me.Edge());
						} else {
							Logger::Warning("Ignoring segment on", l);
						}
					}
					previous = current;
				}
			} else if (segment->declaration().is(IfcSchema::IfcArcIndex::Class())) {
				IfcSchema::IfcArcIndex* arc = (IfcSchema::IfcArcIndex*) segment;
				std::vector<int> indices = *arc;
				if (indices.size() != 3) {
					throw IfcParse::IfcException("Invalid IfcArcIndex encountered");
				}
				for (int i = 0; i < 3; ++i) {
					const int& idx = indices[i];
					if (idx < 1 || idx > max_index) {
						throw IfcParse::IfcException("IfcIndexedPolyCurve index out of bounds for index " + boost::lexical_cast<std::string>(idx));
					}
				}
				const gp_Pnt& a = points[indices[0] - 1];
				const gp_Pnt& b = points[indices[1] - 1];
				const gp_Pnt& c = points[indices[2] - 1];
				Handle(Geom_Circle) circ = GC_MakeCircle(a, b, c).Value();
				BRepBuilderAPI_MakeEdge me(circ, a, c);
				if (me.IsDone() && !BRep_Tool::Curve(me.Edge(), u, v).IsNull()) {
					w.Add(me.Edge());
				} else {
					Logger::Warning("Ignoring segment on", l);
				}
			} else {
				throw IfcParse::IfcException("Unexpected IfcIndexedPolyCurve segment of type " + segment->declaration().name());
			}
		}
	} else if (points.begin() < points.end()) {
        std::vector<gp_Pnt>::const_iterator previous = points.begin();
        for (std::vector<gp_Pnt>::const_iterator current = previous+1; current < points.end(); ++current){
			BRepBuilderAPI_MakeEdge me(*previous, *current);
			if (me.IsDone() && !BRep_Tool::Curve(me.Edge(), u, v).IsNull()) {
				w.Add(me.Edge());
				previous = current;
			}
        }
    }

	result = w.Wire();
	return true;
}

#endif
