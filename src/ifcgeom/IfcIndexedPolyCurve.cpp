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

#include <cmath>
#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Vec2d.hxx>
#include <gp_Dir2d.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Ax3.hxx>
#include <gp_Ax2d.hxx>
#include <gp_Pln.hxx>
#include <gp_Circ.hxx>
#include <GC_MakeCircle.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <Geom_TrimmedCurve.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp.hxx>
#include <TopExp_Explorer.hxx>
#include <TopLoc_Location.hxx>
#include <TopTools_ListOfShape.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepFilletAPI_MakeFillet2d.hxx>
#include <BRep_Tool.hxx>
#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>
#include <Geom_BSplineCurve.hxx>
#include <BRepTools_WireExplorer.hxx>
#include <ShapeBuild_ReShape.hxx>
#include <TopTools_ListOfShape.hxx>
#include <TopTools_ListIteratorOfListOfShape.hxx>
#include <BRepAdaptor_CompCurve.hxx>
#include <Standard_Version.hxx>
#include <BRepAdaptor_HCompCurve.hxx>
#include <Approx_Curve3d.hxx>
#include "../ifcgeom/IfcGeom.h"
#include <Extrema_ExtPC.hxx>

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
