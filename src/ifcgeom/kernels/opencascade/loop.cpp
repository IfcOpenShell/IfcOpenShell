#include "OpenCascadeKernel.h"
#include "wire_builder.h"

#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <BRepAdaptor_CompCurve.hxx>
#include <Approx_Curve3d.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <gp_Pnt.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <Geom_BSplineCurve.hxx>

#include <TopExp.hxx>
#include <BRep_Tool.hxx>
#include <TopTools_ListOfShape.hxx>
#include <BRepTools_WireExplorer.hxx>

#include <Standard_Version.hxx>
#if OCC_VERSION_HEX < 0x70600
#include <BRepAdaptor_HCompCurve.hxx>
#endif

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;

namespace {
	struct curve_creation_visitor {
		OpenCascadeKernel* kernel;
		OpenCascadeKernel::curve_creation_visitor_result_type result;

		OpenCascadeKernel::curve_creation_visitor_result_type operator()(const taxonomy::bspline_curve::ptr& bc) {

			const bool is_rational = !!bc->weights;

			TColgp_Array1OfPnt      Poles(0, bc->control_points.size() - 1);
			TColStd_Array1OfReal    Weights(0, bc->control_points.size() - 1);
			TColStd_Array1OfReal    Knots(0, (int)bc->knots.size() - 1);
			TColStd_Array1OfInteger Mults(0, (int)bc->knots.size() - 1);
			Standard_Integer        Degree = bc->degree;
			Standard_Boolean        Periodic = false;
			// @tfk: it appears to be wrong to expect a period curve when the curve is closed, see #586
			// Standard_Boolean     Periodic = l->ClosedCurve();

			int i;

			if (is_rational) {
				i = 0;
				for (auto it = bc->weights->begin(); it != bc->weights->end(); ++it, ++i) {
					Weights(i) = *it;
				}
			}

			i = 0;
			for (auto it = bc->control_points.begin(); it != bc->control_points.end(); ++it, ++i) {
				Poles(i) = OpenCascadeKernel::convert_xyz<gp_Pnt>(**it);
			}

			i = 0;
			for (auto it = bc->multiplicities.begin(); it != bc->multiplicities.end(); ++it, ++i) {
				Mults(i) = *it;
			}

			i = 0;
			for (auto it = bc->knots.begin(); it != bc->knots.end(); ++it, ++i) {
				Knots(i) = *it;
			}

			if (is_rational) {
				return result = Handle(Geom_Curve)(new Geom_BSplineCurve(Poles, Weights, Knots, Mults, Degree, Periodic));
			} else {
				return result = Handle(Geom_Curve)(new Geom_BSplineCurve(Poles, Knots, Mults, Degree, Periodic));
			}
		}

		OpenCascadeKernel::curve_creation_visitor_result_type operator()(const taxonomy::line::ptr& l) {
			const auto& m = l->matrix->ccomponents();
			return result = Handle(Geom_Curve)(new Geom_Line(OpenCascadeKernel::convert_xyz2<gp_Pnt>(m.col(3)), OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(2))));
		}

		OpenCascadeKernel::curve_creation_visitor_result_type operator()(const taxonomy::circle::ptr& c) {
			const auto& m = c->matrix->ccomponents();
			return result = Handle(Geom_Curve)(new Geom_Circle(gp_Ax2(OpenCascadeKernel::convert_xyz2<gp_Pnt>(m.col(3)), OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(2)), OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(0))), c->radius));
		}

		OpenCascadeKernel::curve_creation_visitor_result_type operator()(const taxonomy::ellipse::ptr& e) {
			const auto& m = e->matrix->ccomponents();
			return result = Handle(Geom_Curve)(new Geom_Ellipse(gp_Ax2(OpenCascadeKernel::convert_xyz2<gp_Pnt>(m.col(3)), OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(2)), OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(0))), e->radius, e->radius2));
		}

		OpenCascadeKernel::curve_creation_visitor_result_type operator()(const taxonomy::loop::ptr& l) {
			TopoDS_Wire wire;
			kernel->convert(l, wire);
			return result = wire;
		}

		OpenCascadeKernel::curve_creation_visitor_result_type operator()(const taxonomy::edge::ptr& e) {
			// @todo for polyloops/-lines we should probably construct edges based on correct oriented TopoDS_Vertex instead.

			if (e->start.which() != e->end.which()) {
				throw std::runtime_error("Different trim types not supported");
			}

			TopoDS_Edge E;
			auto e_basis = e->basis;
			if (e_basis) {
				while (e_basis->kind() == taxonomy::EDGE && e_basis->instance && e_basis->instance->declaration().name() == "IfcTrimmedCurve") {
					// @todo we still might have something to wrt orientation on periodic curves
					// to make sure we select the correct arc later on.
					e_basis = taxonomy::cast<taxonomy::edge>(e_basis)->basis;
				}
				auto crv_or_wire = kernel->convert_curve(e_basis);
				Handle(Geom_Curve) curve;
				if (crv_or_wire.which() == 0) {
					curve = boost::get<Handle(Geom_Curve)>(crv_or_wire);
				} else {
					// @todo
					const double precision_ = 1.e-5;
					Logger::Warning("Approximating BasisCurve due to possible discontinuities", e->instance);
					const auto& w = boost::get<TopoDS_Wire>(crv_or_wire);
#if OCC_VERSION_HEX < 0x70600
					BRepAdaptor_CompCurve cc(w, true);
					Handle(Adaptor3d_HCurve) hcc = Handle(Adaptor3d_HCurve)(new BRepAdaptor_HCompCurve(cc));
#else
					auto hcc = new BRepAdaptor_CompCurve(w, true);
#endif
					// @todo, arbitrary numbers here, note they cannot be too high as contiguous memory is allocated based on them.
					Approx_Curve3d approx(hcc, precision_, GeomAbs_C0, 10, 10);
					curve = approx.Curve();
				}

				const bool reversed = !e->orientation.get_value_or(true);
				const bool is_conic = e_basis->kind() == taxonomy::ELLIPSE || e_basis->kind() == taxonomy::CIRCLE;

				auto e_start = e->start;
				auto e_end = e->end;

				if (!e->curve_sense.get_value_or(true)) {
					std::swap(e_start, e_end);
				}

				// @todo, copy over logic from previous IfcTrimmedCurve handling
				if (e_start.which() == 0) {
					E = BRepBuilderAPI_MakeEdge(curve).Edge();
				} else if (e_start.which() == 1) {
					auto p1 = OpenCascadeKernel::convert_xyz<gp_Pnt>(*boost::get<taxonomy::point3::ptr>(e_start));
					auto p2 = OpenCascadeKernel::convert_xyz<gp_Pnt>(*boost::get<taxonomy::point3::ptr>(e_end));

					if (curve->IsClosed() && p1.Distance(p2) <= kernel->settings().get<settings::Precision>().get()) {
						E = BRepBuilderAPI_MakeEdge(curve).Edge();
					} else {
						E = BRepBuilderAPI_MakeEdge(curve, p1, p2).Edge();
					}
				} else if (e_start.which() == 2) {
					auto v1 = boost::get<double>(e_start);
					auto v2 = boost::get<double>(e_end);

					if (is_conic && ALMOST_THE_SAME(fmod(v2 - v1, M_PI * 2.), 0.)) {
						E = BRepBuilderAPI_MakeEdge(curve).Edge();
					} else {
						E = BRepBuilderAPI_MakeEdge(curve, v1, v2).Edge();
					}
				}

				// When SenseAgreement == .F. the vertices above have been reversed to
				// comply with the direction of conical curves. The ordering of the
				// vertices then still needs to be reversed in order to have begin and
				// end vertex consistent with IFC.
				if (!e->curve_sense.get_value_or(true)) {
					E.Reverse();
				}

				if (reversed) {
					E.Reverse();
				}
			} else {
				if (e->start.which() != 1) {
					throw std::runtime_error("Non-cartesian trim on edge without curve");
				}
				auto p1 = OpenCascadeKernel::convert_xyz<gp_Pnt>(*boost::get<taxonomy::point3::ptr>(e->start));
				auto p2 = OpenCascadeKernel::convert_xyz<gp_Pnt>(*boost::get<taxonomy::point3::ptr>(e->end));

				E = BRepBuilderAPI_MakeEdge(p1, p2).Edge();
			}

#ifdef IFOPSH_DEBUG
			std::ostringstream oss;
			e->print(oss);
			TopoDS_Vertex v0, v1;
			TopExp::Vertices(E, v0, v1, true);
			BRep_Tool::Pnt(v0).DumpJson(oss);
			BRep_Tool::Pnt(v1).DumpJson(oss);
			auto osss = oss.str();
			std::wcout << osss.c_str() << std::endl;
#endif 

			BRep_Builder B;
			TopoDS_Wire W;
			B.MakeWire(W);
			B.Add(W, E);
			return result = W;
		}

		OpenCascadeKernel::curve_creation_visitor_result_type operator()(const taxonomy::offset_curve::ptr&) {
			// @todo
			throw std::runtime_error("Offset curves not supported as part of loop");
		}
	};

}

OpenCascadeKernel::curve_creation_visitor_result_type OpenCascadeKernel::convert_curve(const taxonomy::ptr curve) {
	curve_creation_visitor v{ this };
	if (dispatch_curve_creation<curve_creation_visitor, 0>::dispatch(curve, v)) {
		return v.result;
	} else {
		throw std::runtime_error("No curve created");
	}
}

bool OpenCascadeKernel::convert(const taxonomy::loop::ptr loop, TopoDS_Wire& wire) {
	TopTools_ListOfShape converted_segments;

	for (auto& segment : loop->children) {
		TopoDS_Wire segment_wire;
		try {
			segment_wire = boost::get<TopoDS_Wire>(convert_curve(segment));
		} catch (...) {
			// @todo we should do some better logging here and catch specific exceptions
			// but most notably we just want to continue processing when there are
			// duplicate vertices in our loop (or remove them earlier in the mapping?).
			continue;
		}

#ifdef IFOPSH_DEBUG
		std::ostringstream o;
		segment->print(o);
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(segment_wire, v0, v1);
		gp_Pnt p0 = BRep_Tool::Pnt(v0);
		gp_Pnt p1 = BRep_Tool::Pnt(v1);
		o << "p0 " << p0.X() << " " << p0.Y() << " " << p0.Z() << std::endl;
		o << "p1 " << p1.X() << " " << p1.Y() << " " << p1.Z() << std::endl;
		auto o_str = o.str();
		std::wcout << o_str.c_str() << std::endl;
#endif

		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(segment_wire, precision_, TopAbs_WIRE);

		converted_segments.Append(segment_wire);
	}

	if (converted_segments.Extent() == 0) {
		Logger::Message(Logger::LOG_ERROR, "No segment successfully converted:", loop->instance);
		return false;
	}

	BRepBuilderAPI_MakeWire w;
	TopoDS_Vertex wire_first_vertex, wire_last_vertex, edge_first_vertex, edge_last_vertex;

	TopTools_ListIteratorOfListOfShape it(converted_segments);

	/*
	@todo
	IfcEntityList::ptr profile = l->data().getInverse(&IfcSchema::IfcProfileDef::Class(), -1);
	const bool force_close = profile && profile->size() > 0;
	*/
	const bool force_close = false;

	wire_builder bld(precision_, loop->instance ? loop->instance->as<IfcUtil::IfcBaseEntity>() : nullptr);
	shape_pair_enumerate(it, bld, force_close);
	wire = bld.wire();

	TopTools_IndexedDataMapOfShapeListOfShape map;
	TopExp::MapShapesAndAncestors(wire, TopAbs_VERTEX, TopAbs_EDGE, map);

	TopTools_IndexedMapOfShape edges_to_tesselate;

	for (int i = 1; i <= map.Extent(); ++i) {
		auto& edges = map.FindFromIndex(i);
		auto& vertex = TopoDS::Vertex(map.FindKey(i));

		if (edges.Extent() == 2) {
			double u0, v0, u1, v1;

			auto crv1 = BRep_Tool::Curve(TopoDS::Edge(edges.First()), u0, v0);
			auto crv2 = BRep_Tool::Curve(TopoDS::Edge(edges.Last()), u1, v1);

			auto has_circle = crv1->DynamicType() == STANDARD_TYPE(Geom_Circle) || crv2->DynamicType() == STANDARD_TYPE(Geom_Circle);
			auto has_line = crv1->DynamicType() == STANDARD_TYPE(Geom_Line) || crv2->DynamicType() == STANDARD_TYPE(Geom_Line);

			if (has_circle && has_line) {
				auto param1 = BRep_Tool::Parameter(vertex, TopoDS::Edge(edges.First()));
				auto param2 = BRep_Tool::Parameter(vertex, TopoDS::Edge(edges.Last()));

				gp_Pnt P1, P2;
				gp_Vec V1, V2;

				crv1->D1(param1, P1, V1);
				crv2->D1(param2, P2, V2);

				V1.Normalize();
				V2.Normalize();

				V2.Reverse();

				if (edges.First().Orientation() == TopAbs_REVERSED) {
					V1.Reverse();
				}
				if (edges.Last().Orientation() == TopAbs_REVERSED) {
					V2.Reverse();
				}

				auto ang = std::acos(V1.Dot(V2));

				if (ang < 0.0314) {
					edges_to_tesselate.Add(crv1->DynamicType() == STANDARD_TYPE(Geom_Circle) ? edges.First() : edges.Last());
					Logger::Notice("Sharp circular corner detecting, substituting with linear approximation");
				}
			}
		}
	}

	if (edges_to_tesselate.Extent()) {
		BRepBuilderAPI_MakeWire mw;

		BRepTools_WireExplorer exp(wire);
		for (; exp.More(); exp.Next()) {
			if (edges_to_tesselate.Contains(exp.Current())) {
				BRepAdaptor_Curve crv(TopoDS::Edge(exp.Current()));
				GCPnts_QuasiUniformDeflection tessellater(crv, 0.01);
				int n = tessellater.NbPoints();
				if (exp.Current().Orientation() == TopAbs_REVERSED) {
					for (int i = n-1; i >= 1; --i) {
						mw.Add(BRepBuilderAPI_MakeEdge(tessellater.Value(i + 1), tessellater.Value(i)).Edge());
					}
				} else {
					for (int i = 2; i <= n; ++i) {
						mw.Add(BRepBuilderAPI_MakeEdge(tessellater.Value(i - 1), tessellater.Value(i)).Edge());
					}
				}
			} else {
				mw.Add(exp.Current());
			}
		}

		wire = mw.Wire();
	}

	return true;
}

bool OpenCascadeKernel::convert_impl(const taxonomy::loop::ptr loop, IfcGeom::ConversionResults& results) {
	TopoDS_Wire shape;
	if (!convert(loop, shape)) {
		return false;
	}

	results.emplace_back(ConversionResult(
		loop->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		new OpenCascadeShape(shape),
		loop->surface_style
	));
	return true;
}

bool OpenCascadeKernel::convert_impl(const taxonomy::edge::ptr edge, IfcGeom::ConversionResults& results) {
	TopoDS_Wire shape = boost::get<TopoDS_Wire>(convert_curve(edge));

	results.emplace_back(ConversionResult(
		edge->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		new OpenCascadeShape(shape),
		edge->surface_style
	));
	return true;
}
