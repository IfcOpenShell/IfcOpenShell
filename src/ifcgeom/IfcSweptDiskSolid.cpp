﻿/********************************************************************************
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

#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopExp.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <ShapeFix_Shape.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <Geom_Line.hxx>
#include <Geom_Plane.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepFilletAPI_MakeFillet2d.hxx>

#include "../ifcgeom/IfcGeom.h"

#include "../ifcgeom_schema_agnostic/sweep_utils.h"
#include "../ifcgeom_schema_agnostic/wire_utils.h"
#include "../ifcgeom_schema_agnostic/face_definition.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

namespace {
	std::string format_edge(const TopoDS_Edge& e) {
		std::ostringstream oss;
		double _, __;
		TopoDS_Vertex v0, v1;

		auto crv = BRep_Tool::Curve(e, _, __);
		auto nm = crv->DynamicType()->Name();
		TopExp::Vertices(e, v0, v1, true);

		auto p0 = BRep_Tool::Pnt(v0);
		auto p1 = BRep_Tool::Pnt(v1);

		oss << "Edge" << std::endl << std::setprecision(2)
			<< " (" << p0.X() << " " << p0.Y() << " " << p0.Z() << ")" << std::endl
			<< " (" << p1.X() << " " << p1.Y() << " " << p1.Z() << ")" << std::endl
			<< nm << std::endl;

		return oss.str();
	}
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSweptDiskSolid* l, TopoDS_Shape& shape) {
	TopoDS_Wire wire, section1, section2;

	bool hasInnerRadius = !!l->InnerRadius();

	if (!convert_wire(l->Directrix(), wire)) {
		return false;
	}
	
	// Start- EndParam became optional in IFC4
#ifdef SCHEMA_IfcSweptDiskSolid_StartParam_IS_OPTIONAL
	auto sp = l->StartParam();
	auto ep = l->EndParam();
#else
	boost::optional<double> sp, ep;
	sp = l->StartParam();
	ep = l->EndParam();
#endif

	if (count(wire, TopAbs_EDGE) == 1 && sp && ep) {
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(wire, v0, v1);
		if (v0.IsSame(v1)) {
			TopExp_Explorer exp(wire, TopAbs_EDGE);
			auto& e = TopoDS::Edge(exp.Current());
			double a, b;
			auto crv = BRep_Tool::Curve(e, a, b);
			if ((crv->DynamicType() == STANDARD_TYPE(Geom_Circle)) ||
				(crv->DynamicType() == STANDARD_TYPE(Geom_Ellipse))) 
			{
				BRepBuilderAPI_MakeEdge me(crv, *sp, *ep);
				if (me.IsDone()) {
					auto e2 = me.Edge();
					BRep_Builder B;
					wire.Nullify();
					B.MakeWire(wire);
					B.Add(wire, e2);
				}
			}
		}
	}

	double fillet = 0.;

#ifdef SCHEMA_HAS_IfcSweptDiskSolidPolygonal
	if (l->as<IfcSchema::IfcSweptDiskSolidPolygonal>()) {
		auto fr = l->as<IfcSchema::IfcSweptDiskSolidPolygonal>()->FilletRadius();
		if (fr) {
			fillet = *fr;
		}
	}
#endif

	if (fillet > getValue(GV_PRECISION)) {

		if (util::is_polyhedron(wire)) {
			BRep_Builder BB;
			TopoDS_Vertex V;
			std::vector<TopoDS_Edge> sorted_edges;
			util::sort_edges(wire, sorted_edges);

			if (sorted_edges.size() >= 2) {
				size_t i = 0, j = 1;

				// If the wire is closed we need to cycle from end back to begin
				while (j < (sorted_edges.size() + (wire.Closed() ? 1 : 0))) {
					const TopoDS_Edge& a = sorted_edges[i];
					const TopoDS_Edge& b = sorted_edges[j % sorted_edges.size()];

					/*
					std::wcout << "INPUT:" << std::endl;
					std::wcout << "a " << format_edge(a).c_str() << std::endl;
					std::wcout << "b " << format_edge(b).c_str() << std::endl;
					*/

					// @todo this code is duplicated with code from IfcFace, refactor
					// Help Open Cascade by finding the plane more efficiently
					// We have already asserted the wire is a polyhedron and edges are linear
					double _, __;
					Handle(Geom_Line) c1 = Handle(Geom_Line)::DownCast(BRep_Tool::Curve(a, _, __));
					Handle(Geom_Line) c2 = Handle(Geom_Line)::DownCast(BRep_Tool::Curve(b, _, __));

					const gp_Vec ab = c1->Position().Direction();
					const gp_Vec ac = c2->Position().Direction();
					const gp_Vec cross = ab.Crossed(ac);

					if (cross.SquareMagnitude() > ALMOST_ZERO) {
						const gp_Dir n = cross;
						gp_Pln plane(c1->Position().Location(), n);
						auto face = BRepBuilderAPI_MakeFace(plane).Face();

						TopoDS_Wire wire;
						BB.MakeWire(wire);
						BB.Add(wire, a);
						BB.Add(wire, b);
						BB.Add(face, wire);
						TopExp::CommonVertex(a, b, V);

						BRepFilletAPI_MakeFillet2d mf2d(face);
						mf2d.AddFillet(V, fillet);
						mf2d.Build();

						if (mf2d.IsDone()) {

							auto new_wire = TopoDS::Wire(TopoDS_Iterator(mf2d.Shape()).Value());
							std::vector<TopoDS_Edge> new_sorted_edges;
							util::sort_edges(new_wire, new_sorted_edges);

							//  B               C      B2            C
							// 	o───────────────o      o─────────────o
							// 	│                     /
							// 	│                 B1 o
							// 	│                    │
							// 	│                    │
							// 	o                    o
							// 	A                    A

							if (new_sorted_edges.size() == 3) {
								// Delete AB
								sorted_edges.erase(sorted_edges.begin() + i);
								// Delete BC
								sorted_edges.erase(sorted_edges.begin() + i);

								/*
								std::wcout << "OUTPUT:" << std::endl;
								for (auto& e : new_sorted_edges) {
									std::wcout << " " << format_edge(e).c_str() << std::endl;
								}
								*/

								// Insert AB1 B1B2 B2C
								sorted_edges.insert(sorted_edges.begin() + i, new_sorted_edges.begin(), new_sorted_edges.end());

								// Number of edges increased, so an additional increment
								i += 1;
								j += 1;
							} else {
								Logger::Error("Unexpected amount of fillet edges generated");
							}					
						} else {
							Logger::Error("Unable to build fillet, probably edge too short");
						}
					} else {
						Logger::Error("Colinear edges, not applying fillet");
					}
					i++;
					j++;
				}
			} else {
				Logger::Error("Not enough edges for applying fillet");
			}

			TopoDS_Wire new_wire;
			BB.MakeWire(new_wire);

			for (size_t i = 0; i < sorted_edges.size(); ++i) {
				const auto& e = sorted_edges[i];
				BB.Add(new_wire, e);
			}

			wire = new_wire;
		} else {
			Logger::Error("Directrix is not polyhedral, ignoring FilletRadius");
		}
	}

	// NB: Note that StartParam and EndParam param are ignored and the assumption is
	// made that the parametric range over which to be swept matches the IfcCurve in
	// its entirety.
	
	util::process_sweep(wire, l->Radius() * getValue(GV_LENGTH_UNIT), shape);

	if (shape.IsNull()) {
		return false;
	}

	double r2 = 0.;

	if (hasInnerRadius) {
		// Subtraction of pipes with small radii is unstable.
		r2 = *l->InnerRadius() * getValue(GV_LENGTH_UNIT);
	}

	if (r2 > getValue(GV_PRECISION) * 10.) {
		TopoDS_Shape inner;
		util::process_sweep(wire, r2, inner);

		bool is_valid = false;

		// Boolean op on the compound of separately processed sweeps
		// is not attempted.
		// @todo iterate over compound subshapes and process boolean
		// separately.
		// @todo don't process as boolean op at all, since we know
		// only the start and end faces intersect and we know they
		// are co-planar and we know they are circles.
		if (shape.ShapeType() != TopAbs_COMPOUND) {
			BRepAlgoAPI_Cut brep_cut(shape, inner);
			if (brep_cut.IsDone()) {
				TopoDS_Shape result = brep_cut;

				ShapeFix_Shape fix(result);
				fix.Perform();
				result = fix.Shape();

				is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
				if (is_valid) {
					shape = result;
				}
			}
		}

		if (!is_valid) {
			Logger::Message(Logger::LOG_WARNING, "Failed to subtract inner radius void for:", l);
		}
	}

	return true;
}
