#include "sweep_utils.h"

#include <gp_Ax2.hxx>
#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>

#include <TopExp.hxx>
#include <TopExp_Explorer.hxx>

#include <TopoDS.hxx>
#include <TopoDS_Vertex.hxx>
#include <TopoDS_Compound.hxx>

#include <BRep_Tool.hxx>
#include <BRep_Builder.hxx>

#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepPrimAPI_MakeRevol.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepOffsetAPI_MakePipeShell.hxx>

#include "../../../ifcparse/IfcLogger.h"
#include "base_utils.h"

bool IfcGeom::util::wire_is_c1_continuous(const TopoDS_Wire & w, double tol) {
	// NB Note that c0 continuity is NOT checked!

	TopTools_IndexedDataMapOfShapeListOfShape map;
	TopExp::MapShapesAndAncestors(w, TopAbs_VERTEX, TopAbs_EDGE, map);
	for (int i = 1; i <= map.Extent(); ++i) {
		const auto& li = map.FindFromIndex(i);
		if (li.Extent() == 2) {
			const TopoDS_Vertex& v = TopoDS::Vertex(map.FindKey(i));

			const TopoDS_Edge& e0 = TopoDS::Edge(li.First());
			const TopoDS_Edge& e1 = TopoDS::Edge(li.Last());

			double u0 = BRep_Tool::Parameter(v, e0);
			double u1 = BRep_Tool::Parameter(v, e1);

			double _, __;
			Handle(Geom_Curve) c0 = BRep_Tool::Curve(e0, _, __);
			Handle(Geom_Curve) c1 = BRep_Tool::Curve(e1, _, __);

			gp_Pnt p;
			gp_Vec v0, v1;
			c0->D1(u0, p, v0);
			c1->D1(u1, p, v1);

			if (1. - std::abs(v0.Normalized().Dot(v1.Normalized())) > tol) {
				return false;
			}
		}
	}
	return true;
}

bool IfcGeom::util::wire_to_ax(const TopoDS_Wire & wire, gp_Ax2 & directrix) {
	gp_Pnt directrix_origin;
	gp_Vec directrix_tangent;

	TopoDS_Edge edge;

	// Find first edge
	TopoDS_Vertex v0, v1;
	TopExp::Vertices(wire, v0, v1);
	TopTools_IndexedDataMapOfShapeListOfShape map;
	TopExp::MapShapesAndAncestors(wire, TopAbs_VERTEX, TopAbs_EDGE, map);
	if (v0.IsSame(v1) && map.Contains(v0) && map.FindFromKey(v0).Extent() == 2) {
		// Closed wire, with more than 1 edges
		auto es = map.FindFromKey(v0);
		auto e1 = TopoDS::Edge(es.First());
		auto e2 = TopoDS::Edge(es.Last());

		double u0, u1;

		gp_Vec accum;

		Handle(Geom_Curve) crv = BRep_Tool::Curve(e1, u0, u1);
		crv->D1(TopExp::FirstVertex(e1).IsSame(v0) ? u0 : u1, directrix_origin, directrix_tangent);

		accum += directrix_tangent;

		crv = BRep_Tool::Curve(e2, u0, u1);
		crv->D1(TopExp::FirstVertex(e2).IsSame(v0) ? u0 : u1, directrix_origin, directrix_tangent);

		accum += directrix_tangent;

		directrix_tangent = accum;

	} else if (map.Contains(v0) && map.FindFromKey(v0).Extent() == 1) {
		edge = TopoDS::Edge(map.FindFromKey(v0).First());

		double u0, u1;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u0, u1);
		crv->D1(u0, directrix_origin, directrix_tangent);
	} else {
		Logger::Error("Unable to locate first edge");
		return false;
	}

	directrix = gp_Ax2(directrix_origin, directrix_tangent);

	return true;
}

bool IfcGeom::util::is_single_linear_edge(const TopoDS_Wire & wire) {
	TopExp_Explorer exp(wire, TopAbs_EDGE);
	if (!exp.More()) {
		return false;
	}
	TopoDS_Edge e = TopoDS::Edge(exp.Current());
	exp.Next();
	if (exp.More()) {
		return false;
	}
	double u, v;
	Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
	return crv->DynamicType() == STANDARD_TYPE(Geom_Line);
}

bool IfcGeom::util::is_single_circular_edge(const TopoDS_Wire & wire) {
	TopExp_Explorer exp(wire, TopAbs_EDGE);
	if (!exp.More()) {
		return false;
	}
	TopoDS_Edge e = TopoDS::Edge(exp.Current());
	exp.Next();
	if (exp.More()) {
		return false;
	}
	double u, v;
	Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
	return crv->DynamicType() == STANDARD_TYPE(Geom_Circle);
}

void IfcGeom::util::process_sweep_as_extrusion(const TopoDS_Wire & wire, const TopoDS_Wire & section, TopoDS_Shape & result) {
	TopExp_Explorer exp(wire, TopAbs_EDGE);
	TopoDS_Edge e = TopoDS::Edge(exp.Current());
	double u, v;
	Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
	const auto& dir = Handle(Geom_Line)::DownCast(crv)->Position().Direction();
	// OCCT line is normalized so diff in parametric coords equals length
	const double depth = std::abs(u - v);
	// @todo we could be extruding the wire only when we know this is an intermediate edge.
	TopoDS_Face face = BRepBuilderAPI_MakeFace(section).Face();
	result = BRepPrimAPI_MakePrism(face, depth*dir).Shape();
}

void IfcGeom::util::process_sweep_as_revolution(const TopoDS_Wire & wire, const TopoDS_Wire & section, TopoDS_Shape & result) {
	TopExp_Explorer exp(wire, TopAbs_EDGE);
	TopoDS_Edge e = TopoDS::Edge(exp.Current());
	double u, v;
	Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
	auto circ = Handle(Geom_Circle)::DownCast(crv);
	// @todo we could be extruding the wire only when we know this is an intermediate edge.
	const double depth = std::abs(u - v);
	TopoDS_Face face = BRepBuilderAPI_MakeFace(section).Face();
	result = BRepPrimAPI_MakeRevol(face, circ->Axis(), depth).Shape();
}

void IfcGeom::util::process_sweep_as_pipe(const TopoDS_Wire & wire, const TopoDS_Wire & section, TopoDS_Shape & result, bool force_transformed) {
	// This tolerance is fairly high due to the linear edge substitution for small (or large radii) conical curves.
	const bool is_continuous = wire_is_c1_continuous(wire, 1.e-2);
	BRepOffsetAPI_MakePipeShell builder(wire);
	builder.Add(section);
	builder.SetTransitionMode(is_continuous || force_transformed ? BRepBuilderAPI_Transformed : BRepBuilderAPI_RightCorner);
	try {
		builder.Build();
	} catch (Standard_Failure& e) {
		// We fallback to BRepBuilderAPI_Transformed, but likely with visual artefacts.
		if (!(is_continuous || force_transformed)) {
			return process_sweep_as_pipe(wire, section, result, true);
		} else {
			throw e;
		}
	}
	builder.MakeSolid();
	result = builder.Shape();
}

void IfcGeom::util::sort_edges(const TopoDS_Wire & wire, std::vector<TopoDS_Edge>& sorted_edges) {
	TopTools_IndexedDataMapOfShapeListOfShape map;
	TopExp::MapShapesAndAncestors(wire, TopAbs_VERTEX, TopAbs_EDGE, map);

	for (int i = 1; i <= map.Extent(); ++i) {
		if (map.FindFromIndex(i).Extent() > 2) {
			Logger::Warning("Self-intersecting Directrix");
		}
	}

	std::set<TopoDS_TShape*> seen;

	auto num_edges = count(wire, TopAbs_EDGE);

	TopoDS_Vertex v0, v1;
	// @todo this creates the ancestor map twice
	TopExp::Vertices(wire, v0, v1);

	bool ignore_first_equality_because_closed = v0.IsSame(v1);

	// @todo this probably still does not work on a closed wire consisting of one (circular) edge.

	while ((int)sorted_edges.size() < num_edges &&
		(!v0.IsSame(v1) || ignore_first_equality_because_closed)) {
		ignore_first_equality_because_closed = false;
		if (!map.Contains(v0)) {
			throw std::runtime_error("Disconnected vertex");
		}
		const TopTools_ListOfShape& es = map.FindFromKey(v0);
		TopoDS_Vertex ve0, ve1;
		TopTools_ListIteratorOfListOfShape it(es);
		bool added = false;
		for (; it.More(); it.Next()) {
			const TopoDS_Edge& e = TopoDS::Edge(it.Value());
			TopExp::Vertices(e, ve0, ve1, true);
			if (ve0.IsSame(v0) && seen.find(&*e.TShape()) == seen.end()) {
				sorted_edges.push_back(e);
				v0 = ve1;
				added = true;
				seen.insert(&*e.TShape());
				break;
			}
		}
		if (!added) {
			throw std::runtime_error("Disconnected edge");
		}
	}
}

// #939: a closed loop causes failed triangulation in 7.3 and artefacts
// in 7.4 so we break up a closed wire into two equal parts.
void IfcGeom::util::break_closed(const TopoDS_Wire & wire, std::vector<TopoDS_Wire>& wires) {
	std::vector<TopoDS_Edge> sorted_edges;
	sort_edges(wire, sorted_edges);

	if (sorted_edges.size() == 1) {
		wires.push_back(wire);
		return;
	}

	BRep_Builder B;

	wires.emplace_back();
	B.MakeWire(wires.back());

	for (size_t i = 0; i < sorted_edges.size(); ++i) {
		if (i == sorted_edges.size() / 2) {
			wires.emplace_back();
			B.MakeWire(wires.back());
		}

		const auto& e = sorted_edges[i];
		B.Add(wires.back(), e);
	}
}

void IfcGeom::util::segment_adjacent_non_linear(const TopoDS_Wire & wire, std::vector<TopoDS_Wire>& wires) {
	std::vector<TopoDS_Edge> sorted_edges;
	sort_edges(wire, sorted_edges);

	BRep_Builder B;
	double u, v;

	wires.emplace_back();
	B.MakeWire(wires.back());

	for (int i = 0; i < (int)sorted_edges.size() - 1; ++i) {
		const auto& e = sorted_edges[i];
		Handle_Geom_Curve crv = BRep_Tool::Curve(e, u, v);
		const bool is_linear = crv->DynamicType() == STANDARD_TYPE(Geom_Line);

		const auto& f = sorted_edges[i + 1];
		crv = BRep_Tool::Curve(f, u, v);
		const bool next_is_linear = crv->DynamicType() == STANDARD_TYPE(Geom_Line);

		B.Add(wires.back(), e);

		if (!is_linear && !next_is_linear) {
			wires.emplace_back();
			B.MakeWire(wires.back());
		}
	}

	if (!sorted_edges.empty()) {
		B.Add(wires.back(), sorted_edges.back());
	}
}

// @todo make this generic for other sweeps not just swept disk
void IfcGeom::util::process_sweep(const TopoDS_Wire & wire, double radius, TopoDS_Shape & result) {
	std::vector<TopoDS_Wire> wires, wires_tmp;
	segment_adjacent_non_linear(wire, wires_tmp);
	for (auto& w : wires_tmp) {
		break_closed(w, wires);
	}

	TopoDS_Compound C;
	BRep_Builder B;
	if (wires.size() > 1) {
		B.MakeCompound(C);
	}

	for (auto& w : wires) {
		TopoDS_Shape part;

		gp_Ax2 directrix;
		if (!wire_to_ax(w, directrix)) {
			continue;
		}
		Handle(Geom_Circle) circle = new Geom_Circle(directrix, radius);
		TopoDS_Wire section = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circle));

		if (is_single_circular_edge(w)) {
			process_sweep_as_revolution(w, section, part);
		} else if (is_single_linear_edge(w)) {
			process_sweep_as_extrusion(w, section, part);
		} else {
			process_sweep_as_pipe(w, section, part);
		}
		if (wires.size() > 1) {
			B.Add(C, part);
		} else {
			result = part;
		}
	}

	if (wires.size() > 1) {
		result = C;
	}

	/*
	// Eliminate Swept Surfaces?
	result = ShapeCustom::SweptToElementary(result);

	// Eliminate Trimmed Surfaces?
	ShapeBuild_ReShape sbrs;
	BRep_Builder b;
	TopExp_Explorer exp(result, TopAbs_FACE);
	for (; exp.More(); exp.Next()) {
	const TopoDS_Face& f = TopoDS::Face(exp.Current());
	auto S = BRep_Tool::Surface(f);
	if (S->IsKind(STANDARD_TYPE(Geom_RectangularTrimmedSurface))) {
	auto RTS = Handle(Geom_RectangularTrimmedSurface)::DownCast(S);
	auto B = RTS->BasisSurface();
	TopoDS_Shape newf = f.EmptyCopied();
	// @todo Is it ok to assume no location?
	b.MakeFace(TopoDS::Face(newf), B, BRep_Tool::Tolerance(f));
	sbrs.Replace(f, newf);
	}
	}
	result = sbrs.Apply(result);
	*/
}
