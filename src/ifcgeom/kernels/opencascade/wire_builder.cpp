#include "wire_builder.h"

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/ConversionSettings.h"

#include <TopExp.hxx>
#include <TopoDS.hxx>
#include <BRep_Tool.hxx>
#include <BRep_Builder.hxx>
#include <ShapeBuild_ReShape.hxx>
#include <GC_MakeCircle.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <GeomAdaptor_Curve.hxx>

// Returns the first edge of a wire
TopoDS_Edge IfcGeom::util::first_edge(const TopoDS_Wire & w) {
	TopoDS_Vertex v1, v2;
	TopExp::Vertices(w, v1, v2);
	TopTools_IndexedDataMapOfShapeListOfShape wm;
	TopExp::MapShapesAndAncestors(w, TopAbs_VERTEX, TopAbs_EDGE, wm);
	return TopoDS::Edge(wm.FindFromKey(v1).First());
}

// Returns new wire with the edge replaced by a linear edge with the vertex v moved to p
TopoDS_Wire IfcGeom::util::adjust(const TopoDS_Wire & w, const TopoDS_Vertex & v, const gp_Pnt & p) {
	TopTools_IndexedDataMapOfShapeListOfShape map;
	TopExp::MapShapesAndAncestors(w, TopAbs_VERTEX, TopAbs_EDGE, map);

	bool all_linear = true, single_circle = false, first = true;

	const TopTools_ListOfShape& edges = map.FindFromKey(v);
	TopTools_ListIteratorOfListOfShape it(edges);
	for (; it.More(); it.Next()) {
		const TopoDS_Edge& e = TopoDS::Edge(it.Value());
		double _, __;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(e, _, __);
		const bool is_line = crv->DynamicType() == STANDARD_TYPE(Geom_Line);
		const bool is_circle = crv->DynamicType() == STANDARD_TYPE(Geom_Circle);
		all_linear = all_linear && is_line;
		single_circle = first && is_circle;
	}

	if (all_linear) {
		BRep_Builder b;
		TopoDS_Vertex v2;
		b.MakeVertex(v2, p, BRep_Tool::Tolerance(v));

		ShapeBuild_ReShape reshape;
		reshape.Replace(v.Oriented(TopAbs_FORWARD), v2);

		return TopoDS::Wire(reshape.Apply(w));
	} else if (single_circle) {
		TopoDS_Vertex v1, v2;
		TopExp::Vertices(w, v1, v2);

		gp_Pnt p1, p2, p3;
		p1 = v.IsEqual(v1) ? p : BRep_Tool::Pnt(v1);
		p3 = v.IsEqual(v2) ? p : BRep_Tool::Pnt(v2);

		double a, b;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(TopoDS::Edge(edges.First()), a, b);
		crv->D0((a + b) / 2., p2);

		GC_MakeCircle mc(p1, p2, p3);
		if (!mc.IsDone()) {
			throw IfcGeom::geometry_exception("Failed to adjust circle");
		}

		TopoDS_Edge edge = BRepBuilderAPI_MakeEdge(mc.Value(), p1, p3).Edge();
		BRepBuilderAPI_MakeWire builder;
		builder.Add(edge);
		return builder.Wire();
	} else {
		throw IfcGeom::geometry_exception("Unexpected wire to adjust");
	}
}

double IfcGeom::util::deflection_for_approximating_circle(double radius, double param) {
	return -radius * std::cos(1. / 2. * param) * std::cos(param) - radius * std::sin(1. / 2. * param) * std::sin(param) + radius;
}

bool IfcGeom::util::create_edge_over_curve_with_log_messages(const Handle_Geom_Curve & crv, const double eps, const gp_Pnt & p1, const gp_Pnt & p2, TopoDS_Edge & result) {
	if (crv->IsClosed() && p1.Distance(p2) <= eps) {
		BRepBuilderAPI_MakeEdge me(crv);
		if (me.IsDone()) {
			result = me.Edge();
			return true;
		} else {
			return false;
		}
	}

	BRep_Builder builder;
	TopoDS_Vertex v1, v2;
	/// @todo project first and emit warnings accordingly
	builder.MakeVertex(v1, p1, eps);
	builder.MakeVertex(v2, p2, eps);

	BRepBuilderAPI_MakeEdge me(crv, v1, v2);
	if (!me.IsDone()) {
		const double eps2 = eps * eps;
		if (me.Error() == BRepBuilderAPI_PointProjectionFailed) {
			GeomAdaptor_Curve GAC(crv);
			const gp_Pnt* ps[2] = { &p1, &p2 };
			for (int i = 0; i < 2; ++i) {
				Extrema_ExtPC extrema(*ps[i], GAC);
				if (extrema.IsDone()) {
					int n = extrema.NbExt();
					double dmin = std::numeric_limits<double>::infinity();
					for (int j = 1; j <= n; j++) {
						const double d = extrema.SquareDistance(j);
						if (d < dmin) {
							dmin = d;
						}
					}
					if (dmin == std::numeric_limits<double>::infinity()) {
						Logger::Error("No extrema for point");
					} else if (dmin > eps2) {
						Logger::Error("Distance of " + boost::lexical_cast<std::string>(std::sqrt(dmin)) + " exceeds tolerance");
					}
				} else {
					Logger::Error("Failed to calculate extrema for point");
				}
			}
		}
		return false;
	}
	result = me.Edge();
	return true;
}

void IfcGeom::util::wire_builder::operator()(const TopoDS_Shape& a) {
	const TopoDS_Wire& w = TopoDS::Wire(a);
	if (override_next_) {
		override_next_ = false;
		TopoDS_Edge e = first_edge(w);
		mw_.Add(adjust(w, TopExp::FirstVertex(e, true), next_override_));
	} else {
		mw_.Add(w);
	}
}

void IfcGeom::util::wire_builder::operator()(const TopoDS_Shape& a, const TopoDS_Shape& b, bool last) {
	TopoDS_Wire w1 = TopoDS::Wire(a);
	const TopoDS_Wire& w2 = TopoDS::Wire(b);

	if (override_next_) {
		override_next_ = false;
		TopoDS_Edge e = first_edge(w1);
		w1 = adjust(w1, TopExp::FirstVertex(e, true), next_override_);
	}

	TopoDS_Vertex w11, w12, w21, w22;
	TopExp::Vertices(w1, w11, w12);
	TopExp::Vertices(w2, w21, w22);

	gp_Pnt p1 = BRep_Tool::Pnt(w12);
	gp_Pnt p2 = BRep_Tool::Pnt(w21);

	double dist = p1.Distance(p2);

	// Distance is within tolerance, this is fine
	if (dist < p_) {
		mw_.Add(w1);
		goto check;
	}

	// Distance is too large for attempting to move end points, add intermediate edge
	if (dist > 1000. * p_) {
		mw_.Add(w1);
		mw_.Add(BRepBuilderAPI_MakeEdge(p1, p2));
		Logger::Warning("Added additional segment to close gap with length " + boost::lexical_cast<std::string>(dist) + " to:", inst_);
		goto check;
	}

	{
		TopTools_IndexedDataMapOfShapeListOfShape wmap1, wmap2;

		// Find edges connected to end- and begin vertex
		TopExp::MapShapesAndAncestors(w1, TopAbs_VERTEX, TopAbs_EDGE, wmap1);
		TopExp::MapShapesAndAncestors(w2, TopAbs_VERTEX, TopAbs_EDGE, wmap2);

		const TopTools_ListOfShape& last_edges = wmap1.FindFromKey(w12);
		const TopTools_ListOfShape& first_edges = wmap2.FindFromKey(w21);

		double _, __;
		if (last_edges.Extent() == 1 && first_edges.Extent() == 1) {
			Handle(Geom_Curve) c1 = BRep_Tool::Curve(TopoDS::Edge(last_edges.First()), _, __);
			Handle(Geom_Curve) c2 = BRep_Tool::Curve(TopoDS::Edge(first_edges.First()), _, __);

			const bool is_line1 = c1->DynamicType() == STANDARD_TYPE(Geom_Line);
			const bool is_line2 = c2->DynamicType() == STANDARD_TYPE(Geom_Line);

			const bool is_circle1 = c1->DynamicType() == STANDARD_TYPE(Geom_Circle);
			const bool is_circle2 = c2->DynamicType() == STANDARD_TYPE(Geom_Circle);

			// Preferably adjust the segment that is linear
			if (is_line1 || (is_circle1 && !is_line2)) {
				mw_.Add(adjust(w1, w12, p2));
				Logger::Notice("Adjusted edge end-point with distance " + boost::lexical_cast<std::string>(dist) + " on:", inst_);
			} else if ((is_line2 || is_circle2) && !last) {
				mw_.Add(w1);
				override_next_ = true;
				next_override_ = p1;
				Logger::Notice("Adjusted edge end-point with distance " + boost::lexical_cast<std::string>(dist) + " on:", inst_);
			} else {
				// In all other cases an edge is added
				mw_.Add(w1);
				mw_.Add(BRepBuilderAPI_MakeEdge(p1, p2));
				Logger::Warning("Added additional segment to close gap with length " + boost::lexical_cast<std::string>(dist) + " to:", inst_);
			}
		} else {
			Logger::Error("Internal error, inconsistent wire segments", inst_);
			mw_.Add(w1);
		}
	}

check:
	if (mw_.Error() == BRepBuilderAPI_NonManifoldWire) {
		Logger::Error("Non-manifold curve segments:", inst_);
	} else if (mw_.Error() == BRepBuilderAPI_DisconnectedWire) {
		Logger::Error("Failed to join curve segments:", inst_);
	}
}