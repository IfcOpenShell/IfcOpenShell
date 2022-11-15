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
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopExp_Explorer.hxx>
#include <BRep_Tool.hxx>
#include "../ifcgeom/IfcGeom.h"

#include "../ifcgeom_schema_agnostic/wire_builder.h"

#define _USE_MATH_DEFINES
#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcEdgeCurve* l, TopoDS_Wire& result) {
	IfcSchema::IfcPoint* pnt1 = ((IfcSchema::IfcVertexPoint*) l->EdgeStart())->VertexGeometry();
	IfcSchema::IfcPoint* pnt2 = ((IfcSchema::IfcVertexPoint*) l->EdgeEnd())->VertexGeometry();
	if (!pnt1->declaration().is(IfcSchema::IfcCartesianPoint::Class()) || !pnt2->declaration().is(IfcSchema::IfcCartesianPoint::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Only IfcCartesianPoints are supported for VertexGeometry", l);
		return false;
	}
	
	gp_Pnt p1, p2;
	if (!IfcGeom::Kernel::convert(((IfcSchema::IfcCartesianPoint*)pnt1), p1) ||
		!IfcGeom::Kernel::convert(((IfcSchema::IfcCartesianPoint*)pnt2), p2))
	{
		return false;
	}
	
	BRepBuilderAPI_MakeWire mw;
	Handle_Geom_Curve crv;

	// The lack of a clear separation between topological and geometrical entities
	// is starting to get problematic. If the underlying curve is bounded it is
	// assumed that a topological wire can be crafted from it. After which an
	// attempt is made to reconstruct it from the individual curves and the vertices
	// of the IfcEdgeCurve.
	const bool is_bounded = l->EdgeGeometry()->declaration().is(IfcSchema::IfcBoundedCurve::Class());

	if (!is_bounded && convert_curve(l->EdgeGeometry(), crv)) {
		TopoDS_Edge e;
		if (util::create_edge_over_curve_with_log_messages(crv, getValue(GV_PRECISION), p1, p2, e)) {
			mw.Add(e);
			result = mw;
			return true;
		} else {
			return false;
		}
	} else if (is_bounded && convert_wire(l->EdgeGeometry(), result)) {
		if (!l->SameSense()) {
			result.Reverse();
		}
		
		bool first = true;
		TopExp_Explorer exp(result, TopAbs_EDGE);
		
		while (exp.More()) {
			const TopoDS_Edge& ed = TopoDS::Edge(exp.Current());
			Standard_Real u1, u2;
			Handle(Geom_Curve) ecrv = BRep_Tool::Curve(ed, u1, u2);
			exp.Next();
			const bool last = !exp.More();

			gp_Pnt a, b;

			if (first && last) {
				a = p1;
				b = p2;				
			} else if (first) {
				a = p1;
				ecrv->D0(u2, b);
			} else if (last) {
				ecrv->D0(u1, a);
				b = p2;
			} else {
				BRepBuilderAPI_MakeEdge me(ecrv, u1, u2);
				if (!me.IsDone()) {
					return false;
				}
				mw.Add(me.Edge());
				first = false;
				continue;
			}

			TopoDS_Edge e;
			if (util::create_edge_over_curve_with_log_messages(ecrv, getValue(GV_PRECISION), a, b, e)) {
				mw.Add(e);
			} else {
				return false;
			}

			first = false;
		}
		result = mw;
		return true;
	} else {
		return false;
	}
}
