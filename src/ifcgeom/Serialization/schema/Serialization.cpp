#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <Geom_BSplineCurve.hxx>

#include <Geom_Plane.hxx>
#include <Geom_BSplineSurface.hxx>
#include <Geom_CylindricalSurface.hxx>

#include <BRepTools_WireExplorer.hxx>

#include <TColgp_Array2OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array2OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <Geom_BezierCurve.hxx>
#include <Geom_TrimmedCurve.hxx>
#include <BRep_Tool.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <BRepMesh_IncrementalMesh.hxx>
#include <BRepTools.hxx>

#include "../../../ifcparse/macros.h"
#include "../../../ifcparse/IfcParse.h"
#include "../../../ifcparse/IfcFile.h"

#define INCLUDE_PARENT_PARENT_DIR(x) STRINGIFY(../../../ifcparse/x.h)
#include INCLUDE_PARENT_PARENT_DIR(IfcSchema)
#undef INCLUDE_PARENT_PARENT_DIR
#define INCLUDE_PARENT_PARENT_DIR(x) STRINGIFY(../../../ifcparse/x-definitions.h)
#include INCLUDE_PARENT_PARENT_DIR(IfcSchema)

#include <numeric>

template <typename T, typename U>
int convert_to_ifc(IfcParse::IfcFile& f, const T& t, U& u, bool /*advanced*/) {
	u = f.create<U>();
    u.set_attribute_value(0, std::vector<double>{t.X(), t.Y(), t.Z()});
	return 1;
}

template <>
int convert_to_ifc(IfcParse::IfcFile& f, const TopoDS_Vertex& v, IfcSchema::IfcCartesianPoint& p, bool advanced) {
	gp_Pnt pnt = BRep_Tool::Pnt(v);
	return convert_to_ifc(f, pnt, p, advanced);
}

template <>
int convert_to_ifc(IfcParse::IfcFile& f, const TopoDS_Vertex& v, IfcSchema::IfcVertexPoint& vertex, bool advanced) {
	IfcSchema::IfcCartesianPoint p;
	if (convert_to_ifc(f, v, p, advanced)) {
        vertex = f.create<IfcSchema::IfcVertexPoint>();
        vertex.setVertexGeometry(p);
		return 1;
	} else {
		return 0;
	}
}

template <>
int convert_to_ifc(IfcParse::IfcFile& f, const gp_Ax2& a, IfcSchema::IfcAxis2Placement3D& ax, bool advanced) {
	IfcSchema::IfcCartesianPoint p;
	IfcSchema::IfcDirection x, z;
	if (!(convert_to_ifc(f, a.Location(), p, advanced) && convert_to_ifc(f, a.Direction(), z, advanced) && convert_to_ifc(f, a.XDirection(), x, advanced))) {
        ax = IfcSchema::IfcAxis2Placement3D{};
		return 0;
	}
    ax = f.create<IfcSchema::IfcAxis2Placement3D>();
    ax.setLocation(p);
    ax.setAxis(z);
    ax.setRefDirection(x);
	return 1;
}

template <typename T, typename U>
void opencascade_array_to_vector(T& t, std::vector<U>& u) {
	u.reserve(t.Length());
	for (int i = t.Lower(); i <= t.Upper(); ++i) {
		u.push_back(t.Value(i));
	}
}

template <typename T, typename U>
void opencascade_array_to_vector2(T& t, std::vector< std::vector<U> >& u) {
	u.reserve(t.RowLength());
	for (int j = t.LowerRow(); j <= t.UpperRow(); ++j) {
		std::vector<U> v;
		v.reserve(t.ColLength());
		for (int i = t.LowerCol(); i <= t.UpperCol(); ++i) {
			v.push_back(t.Value(j, i));
		}
		u.push_back(v);
	}
}

#ifdef SCHEMA_HAS_IfcRationalBSplineSurfaceWithKnots
namespace {
	IfcSchema::IfcKnotType::Value opencascade_knotspec_to_ifc(GeomAbs_BSplKnotDistribution bspline_knot_spec) {
		IfcSchema::IfcKnotType::Value knot_spec = IfcSchema::IfcKnotType::IfcKnotType_UNSPECIFIED;
		if (bspline_knot_spec == GeomAbs_Uniform) {
			knot_spec = IfcSchema::IfcKnotType::IfcKnotType_UNIFORM_KNOTS;
		} else if (bspline_knot_spec == GeomAbs_QuasiUniform) {
			knot_spec = IfcSchema::IfcKnotType::IfcKnotType_QUASI_UNIFORM_KNOTS;
		} else if (bspline_knot_spec == GeomAbs_PiecewiseBezier) {
			knot_spec = IfcSchema::IfcKnotType::IfcKnotType_PIECEWISE_BEZIER_KNOTS;
		}
		return knot_spec;
	}
}
#endif

template <>
int convert_to_ifc(IfcParse::IfcFile& f, const Handle_Geom_Curve& c, IfcSchema::IfcCurve& curve, bool advanced) {
	if (c->DynamicType() == STANDARD_TYPE(Geom_TrimmedCurve)) {
		Handle_Geom_TrimmedCurve trim = Handle_Geom_TrimmedCurve::DownCast(c);
		const Handle_Geom_Curve basis = trim->BasisCurve();
		return convert_to_ifc(f, basis, curve, advanced);
	} else if (c->DynamicType() == STANDARD_TYPE(Geom_Line)) {
		IfcSchema::IfcDirection d;
		IfcSchema::IfcCartesianPoint p;

		Handle_Geom_Line line = Handle_Geom_Line::DownCast(c);

		if (!convert_to_ifc(f, line->Position().Location(), p, advanced)) {
			return 0;
		}
		if (!convert_to_ifc(f, line->Position().Direction(), d, advanced)) {
			return 0;
		}

		IfcSchema::IfcVector v = f.create<IfcSchema::IfcVector>();
        v.setOrientation(d);
        v.setMagnitude(1.);
        IfcSchema::IfcLine l = f.create<IfcSchema::IfcLine>();
        l.setPnt(p);
        l.setDir(v);
        curve = l;

		return 1;
	} else if (c->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
		IfcSchema::IfcAxis2Placement3D ax;

		Handle_Geom_Circle circle = Handle_Geom_Circle::DownCast(c);

		convert_to_ifc(f, circle->Position(), ax, advanced);
        auto circ = f.create<IfcSchema::IfcCircle>();
        circ.setPosition(ax);
        circ.setRadius(circle->Radius());
        curve = circ;

		return 1;
	} else if (c->DynamicType() == STANDARD_TYPE(Geom_Ellipse)) {
		IfcSchema::IfcAxis2Placement3D ax;

		Handle_Geom_Ellipse ellipse = Handle_Geom_Ellipse::DownCast(c);

		auto el = f.create<IfcSchema::IfcEllipse>();
        el.setPosition(ax);
        el.setSemiAxis1(ellipse->MajorRadius());
        el.setSemiAxis2(ellipse->MinorRadius());
        curve = el;

		return 1;
	}
#ifdef SCHEMA_HAS_IfcRationalBSplineSurfaceWithKnots
	else if (c->DynamicType() == STANDARD_TYPE(Geom_BezierCurve)) {
		Handle_Geom_BezierCurve bezier = Handle_Geom_BezierCurve::DownCast(c);

		std::vector<int> mults;
		std::vector<double> knots;
		std::vector<double> weights;

		IfcSchema::IfcKnotType::Value knot_spec = IfcSchema::IfcKnotType::IfcKnotType_QUASI_UNIFORM_KNOTS;

		std::vector<IfcSchema::IfcCartesianPoint> points;
		TColgp_Array1OfPnt poles(1, bezier->NbPoles());
		bezier->Poles(poles);
		for (int i = 1; i <= bezier->NbPoles(); ++i) {
			IfcSchema::IfcCartesianPoint p;
			if (!convert_to_ifc(f, poles.Value(i), p, advanced)) {
				return 0;
			}
			points.push_back(p);

			if (i == 1 || i == bezier->NbPoles()) {
				mults.push_back(bezier->Degree() + 1);
			} else {
				mults.push_back(bezier->Degree());
			}

			knots.push_back((double) i - 1);
		}

		TColStd_Array1OfReal bspline_weights(1, bezier->NbPoles());
		bezier->Weights(bspline_weights);
		opencascade_array_to_vector(bspline_weights, weights);

		auto bspl = f.create<IfcSchema::IfcRationalBSplineCurveWithKnots>();
        bspl.setDegree(bezier->Degree());
        bspl.setControlPointsList(points);
        bspl.setCurveForm(IfcSchema::IfcBSplineCurveForm::IfcBSplineCurveForm_UNSPECIFIED);
        bspl.setClosedCurve(bezier->IsClosed() != 0);
        bspl.setSelfIntersect(false);
        bspl.setKnotMultiplicities(mults);
        bspl.setKnots(knots);
        bspl.setKnotSpec(knot_spec);
        bspl.setWeightsData(weights);

		return 1;
	}
	else if (c->DynamicType() == STANDARD_TYPE(Geom_BSplineCurve)) {
		Handle_Geom_BSplineCurve bspline = Handle_Geom_BSplineCurve::DownCast(c);

		std::vector<IfcSchema::IfcCartesianPoint> points;
		TColgp_Array1OfPnt poles(1, bspline->NbPoles());
		bspline->Poles(poles);
		for (int i = 1; i <= bspline->NbPoles(); ++i) {
			IfcSchema::IfcCartesianPoint p;
			if (!convert_to_ifc(f, poles.Value(i), p, advanced)) {
				return 0;
			}
			points.push_back(p);
		}
		IfcSchema::IfcKnotType::Value knot_spec = opencascade_knotspec_to_ifc(bspline->KnotDistribution());

		std::vector<int> mults;
		std::vector<double> knots;
		std::vector<double> weights;

		TColStd_Array1OfInteger bspline_mults(1, bspline->NbKnots());
		TColStd_Array1OfReal bspline_knots(1, bspline->NbKnots());
		TColStd_Array1OfReal bspline_weights(1, bspline->NbPoles());

		bspline->Multiplicities(bspline_mults);
		bspline->Knots(bspline_knots);
		bspline->Weights(bspline_weights);

		opencascade_array_to_vector(bspline_mults, mults);
		opencascade_array_to_vector(bspline_knots, knots);
		opencascade_array_to_vector(bspline_weights, weights);

		bool rational = false;
		for (std::vector<double>::const_iterator it = weights.begin(); it != weights.end(); ++it) {
			if ((*it) != 1.) {
				rational = true;
				break;
			}
		}

		if (bspline->IsPeriodic() && points.size()) {
			points.push_back(points.front());
			weights.push_back(weights[0]);
			auto sum = std::accumulate(mults.begin(), mults.end(), 0);
			auto d = sum - (bspline->Degree() + (int) points.size() + 1);
			(*mults.begin()) -= d / 2;
			(*mults.rbegin()) -= d / 2;
		}

		IfcSchema::IfcBSplineCurveWithKnots bspl;

		if (rational) {
            auto rbspl = f.create<IfcSchema::IfcRationalBSplineCurveWithKnots>();
            rbspl.setWeightsData(weights);
            bspl = rbspl;
        } else {
            bspl = f.create<IfcSchema::IfcBSplineCurveWithKnots>();
        }

		bspl.setDegree(bspline->Degree());
        bspl.setControlPointsList(points);
        bspl.setCurveForm(IfcSchema::IfcBSplineCurveForm::IfcBSplineCurveForm_UNSPECIFIED);
        bspl.setClosedCurve(bspline->IsClosed() != 0);
        bspl.setSelfIntersect(false);
        bspl.setKnotMultiplicities(mults);
        bspl.setKnots(knots);
        bspl.setKnotSpec(knot_spec);

		return 1;
	}
#endif
	return 0;
}

template <>
int convert_to_ifc(IfcParse::IfcFile& f, const Handle_Geom_Surface& s, IfcSchema::IfcSurface& surface, bool advanced) {
	if (s->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
		Handle_Geom_Plane plane = Handle_Geom_Plane::DownCast(s);
		IfcSchema::IfcAxis2Placement3D place;
		/// @todo: Note that the Ax3 is converted to an Ax2 here
		if (!convert_to_ifc(f, plane->Position().Ax2(), place, advanced)) {
			return 0;
		}
        auto pln = f.create<IfcSchema::IfcPlane>();
        pln.setPosition(place);
        surface = pln;
		return 1;
	}
#ifdef SCHEMA_HAS_IfcRationalBSplineSurfaceWithKnots
	else if (s->DynamicType() == STANDARD_TYPE(Geom_CylindricalSurface)) {
		Handle_Geom_CylindricalSurface cyl = Handle_Geom_CylindricalSurface::DownCast(s);
		IfcSchema::IfcAxis2Placement3D place;
		/// @todo: Note that the Ax3 is converted to an Ax2 here
		if (!convert_to_ifc(f, cyl->Position().Ax2(), place, advanced)) {
			return 0;
		}

		auto surf = f.create<IfcSchema::IfcCylindricalSurface>();
        surf.setPosition(place);
        surf.setRadius(cyl->Radius());
		surface = surf;

		return 1;
	} else if (s->DynamicType() == STANDARD_TYPE(Geom_BSplineSurface)) {
        std::vector<std::vector<IfcSchema::IfcCartesianPoint>> points;
		Handle_Geom_BSplineSurface bspline = Handle_Geom_BSplineSurface::DownCast(s);

		TColgp_Array2OfPnt poles(1, bspline->NbUPoles(), 1, bspline->NbVPoles());
		bspline->Poles(poles);
		for (int i = 1; i <= bspline->NbUPoles(); ++i) {
            auto& ps = points.emplace_back();
			ps.reserve(bspline->NbVPoles());
			for (int j = 1; j <= bspline->NbVPoles(); ++j) {
				IfcSchema::IfcCartesianPoint p;
				if (!convert_to_ifc(f, poles.Value(i, j), p, advanced)) {
					return 0;
				}
				ps.push_back(p);
			}
		}

		IfcSchema::IfcKnotType::Value knot_spec_u = opencascade_knotspec_to_ifc(bspline->UKnotDistribution());
		IfcSchema::IfcKnotType::Value knot_spec_v = opencascade_knotspec_to_ifc(bspline->VKnotDistribution());

		if (knot_spec_u != knot_spec_v) {
			knot_spec_u = IfcSchema::IfcKnotType::IfcKnotType_UNSPECIFIED;
		}

		std::vector<int> umults;
		std::vector<int> vmults;
		std::vector<double> uknots;
		std::vector<double> vknots;
		std::vector< std::vector<double> > weights;

		TColStd_Array1OfInteger bspline_umults(1, bspline->NbUKnots());
		TColStd_Array1OfInteger bspline_vmults(1, bspline->NbVKnots());
		TColStd_Array1OfReal bspline_uknots(1, bspline->NbUKnots());
		TColStd_Array1OfReal bspline_vknots(1, bspline->NbVKnots());
		TColStd_Array2OfReal bspline_weights(1, bspline->NbUPoles(), 1, bspline->NbVPoles());

		bspline->UMultiplicities(bspline_umults);
		bspline->VMultiplicities(bspline_vmults);
		bspline->UKnots(bspline_uknots);
		bspline->VKnots(bspline_vknots);
		bspline->Weights(bspline_weights);

		opencascade_array_to_vector(bspline_umults, umults);
		opencascade_array_to_vector(bspline_vmults, vmults);
		opencascade_array_to_vector(bspline_uknots, uknots);
		opencascade_array_to_vector(bspline_vknots, vknots);
		opencascade_array_to_vector2(bspline_weights, weights);

		bool rational = false;
		for (std::vector< std::vector<double> >::const_iterator it = weights.begin(); it != weights.end(); ++it) {
			for (std::vector<double>::const_iterator jt = it->begin(); jt != it->end(); ++jt) {
				if ((*jt) != 1.) {
					rational = true;
					break;
				}
			}
		}

		IfcSchema::IfcBSplineSurfaceWithKnots bspl;

		if (rational) {
			auto rbspl = f.create<IfcSchema::IfcRationalBSplineSurfaceWithKnots>();
			rbspl.setWeightsData(weights);
			bspl = rbspl;
		} else {
			bspl = f.create<IfcSchema::IfcBSplineSurfaceWithKnots>();
        }

		bspl.setUDegree(bspline->UDegree());
		bspl.setVDegree(bspline->VDegree());
		bspl.setControlPointsList(points);
		bspl.setSurfaceForm(IfcSchema::IfcBSplineSurfaceForm::IfcBSplineSurfaceForm_UNSPECIFIED);
		bspl.setUClosed(bspline->IsUClosed() != 0);
		bspl.setVClosed(bspline->IsVClosed() != 0);
		bspl.setSelfIntersect(false);
		bspl.setUMultiplicities(umults);
        bspl.setVMultiplicities(vmults);
		bspl.setUKnots(uknots);
		bspl.setVKnots(vknots);
        bspl.setKnotSpec(knot_spec_u);

		surface = bspl;

		return 1;
	}
#endif
	return 0;
}

template <>
int convert_to_ifc(IfcParse::IfcFile& f, const TopoDS_Edge& e, IfcSchema::IfcCurve& c, bool advanced) {
	double a, b;
	IfcSchema::IfcCurve base;

	Handle_Geom_Curve crv = BRep_Tool::Curve(e, a, b);
	if (!convert_to_ifc(f, crv, base, advanced)) {
		return 0;
	}

	auto ta = f.create<IfcSchema::IfcParameterValue>();
    ta.set_attribute_value(0, a);
    auto tb = f.create<IfcSchema::IfcParameterValue>();
    tb.set_attribute_value(0, b);

	std::vector<IfcSchema::IfcTrimmingSelect> trim1{ta};
    std::vector<IfcSchema::IfcTrimmingSelect> trim2{tb};

	auto tc = f.create<IfcSchema::IfcTrimmedCurve>();
    tc.setBasisCurve(base);
    tc.setTrim1(trim1);
	tc.setTrim2(trim2);
    tc.setSenseAgreement(true);
    tc.setMasterRepresentation(IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER);

	c = tc;

	return 1;
}

template <>
int convert_to_ifc(IfcParse::IfcFile& f, const TopoDS_Edge& e, IfcSchema::IfcEdge& edge, bool advanced) {
	double a, b;

	TopExp_Explorer exp(e, TopAbs_VERTEX);
	if (!exp.More()) return 0;
	TopoDS_Vertex v1 = TopoDS::Vertex(exp.Current());
	exp.Next();
	if (!exp.More()) return 0;
	TopoDS_Vertex v2 = TopoDS::Vertex(exp.Current());

	IfcSchema::IfcVertexPoint vertex1, vertex2;
	if (!(convert_to_ifc(f, v1, vertex1, advanced) && convert_to_ifc(f, v2, vertex2, advanced))) {
		return 0;
	}

	Handle_Geom_Curve crv = BRep_Tool::Curve(e, a, b);

	if (crv.IsNull()) {
		return 0;
	}

	if (crv->DynamicType() == STANDARD_TYPE(Geom_Line) && !advanced) {
        IfcSchema::IfcEdge edge2 = f.create<IfcSchema::IfcEdge>();
        edge2.setEdgeStart(vertex1);
        edge2.setEdgeEnd(vertex2);
		
		auto ori = f.create<IfcSchema::IfcOrientedEdge>();
		ori.setEdgeElement(edge2);
        ori.setOrientation(true);
		
		edge = ori;
		return 1;
	} else {
		IfcSchema::IfcCurve curve;
		if (!convert_to_ifc(f, crv, curve, advanced)) {
			return 0;
		}

		/// @todo probably not correct
		const bool sense = e.Orientation() == TopAbs_FORWARD;

		auto ec = f.create<IfcSchema::IfcEdgeCurve>();
		ec.setEdgeStart(vertex1);
		ec.setEdgeEnd(vertex2);
		ec.setEdgeGeometry(curve);
        ec.setSameSense(true);

		auto ori = f.create<IfcSchema::IfcOrientedEdge>();
		ori.setEdgeElement(ec);
        ori.setOrientation(sense);

		edge = ori;
		return 1;
	}
}

namespace {
	bool is_polygonal(const Handle_Geom_Curve& crv) {
		if (crv->DynamicType() == STANDARD_TYPE(Geom_Line)) {
			return true;
		} else if (crv->DynamicType() == STANDARD_TYPE(Geom_TrimmedCurve)) {
			return is_polygonal(Handle_Geom_TrimmedCurve::DownCast(crv)->BasisCurve());
		} else if (crv->DynamicType() == STANDARD_TYPE(Geom_BSplineCurve)) {
			auto bspl = Handle_Geom_BSplineCurve::DownCast(crv);
			return bspl->NbPoles() == 2 && bspl->Degree() == 1;
		} else {
			return false;
		}
	}
}

template <>
int convert_to_ifc(IfcParse::IfcFile& f, const TopoDS_Wire& wire, IfcSchema::IfcLoop& loop, bool advanced) {
	bool polygonal = true;
	for (TopExp_Explorer exp(wire, TopAbs_EDGE); exp.More(); exp.Next()) {
		double a, b;
		Handle_Geom_Curve crv = BRep_Tool::Curve(TopoDS::Edge(exp.Current()), a, b);
		if (crv.IsNull()) {
			continue;
		}
		if (!is_polygonal(crv)) {
			polygonal = false;
			break;
		}
	}
	if (!polygonal && !advanced) {
		return 0;
	} else if (polygonal && !advanced) {
		std::vector<IfcSchema::IfcCartesianPoint> points;
		BRepTools_WireExplorer exp(wire);
		IfcSchema::IfcCartesianPoint p;
		for (; exp.More(); exp.Next()) {
			if (convert_to_ifc(f, exp.CurrentVertex(), p, advanced)) {
				points.push_back(p);
			} else {
				return 0;
			}
		}
		auto pl = f.create<IfcSchema::IfcPolyLoop>();
        pl.setPolygon(points);
        loop = pl;
		return 1;
	} else {
		std::vector<IfcSchema::IfcOrientedEdge> edges;
		BRepTools_WireExplorer exp(wire);
		for (; exp.More(); exp.Next()) {
            IfcSchema::IfcEdge edge;
			// With advanced set to true convert_to_ifc(IfcParse::IfcFile& f, TopoDS_Edge&) will always create an IfcOrientedEdge
			if (!convert_to_ifc(f, exp.Current(), edge, true)) {
				double a, b;
				if (BRep_Tool::Curve(TopoDS::Edge(exp.Current()), a, b).IsNull()) {
					continue;
				} else {
					return 0;
				}
			}
			edges.push_back(edge.as<IfcSchema::IfcOrientedEdge>());
		}
		auto el = f.create<IfcSchema::IfcEdgeLoop>();
        el.setEdgeList(edges);
        loop = el;
		return 1;
	}
}

template <>
int convert_to_ifc(IfcParse::IfcFile& f, const TopoDS_Face& fa, IfcSchema::IfcFace& face, bool advanced) {
	Handle_Geom_Surface surf = BRep_Tool::Surface(fa);
	TopExp_Explorer exp(fa, TopAbs_WIRE);
	std::vector<IfcSchema::IfcFaceBound> bounds;
	int index = 0;
	auto outer = BRepTools::OuterWire(fa);
	for (; exp.More(); exp.Next(), ++index) {
		IfcSchema::IfcLoop loop;
		if (!convert_to_ifc(f, TopoDS::Wire(exp.Current()), loop, advanced)) {
			return 0;
		}
		IfcSchema::IfcFaceBound bnd;
		if (outer == exp.Current()) {
            bnd = f.create<IfcSchema::IfcFaceOuterBound>();
		} else {
            bnd = f.create<IfcSchema::IfcFaceBound>();
		}
        bnd.setBound(loop);
        bnd.setOrientation(true);

		bounds.push_back(bnd);
	}

	const bool is_planar = surf->DynamicType() == STANDARD_TYPE(Geom_Plane);

	if (!is_planar && !advanced) {
		return 0;
	}
	if (is_planar && !advanced) {
        face = f.create<IfcSchema::IfcFace>();
        face.setBounds(bounds);
		return 1;
	} else {
#ifdef SCHEMA_HAS_IfcAdvancedFace
		IfcSchema::IfcSurface surface;
		if (!convert_to_ifc(f, surf, surface, advanced)) {
			return 0;
		}
		auto adv = f.create<IfcSchema::IfcAdvancedFace>();
		adv.setBounds(bounds);
		adv.setFaceSurface(surface);
        adv.setSameSense(fa.Orientation() == TopAbs_FORWARD);
        face = adv;
		return 1;
#else
		// No IfcAdvancedFace in Ifc2x3
		return 0;
#endif
	}
}

template <typename U>
int convert_to_ifc(IfcParse::IfcFile& f, const TopoDS_Shape& s, U& item, bool advanced) {
	std::vector<IfcSchema::IfcFace> faces;
	IfcSchema::IfcFace fa;

	for (TopExp_Explorer exp(s, TopAbs_FACE); exp.More(); exp.Next()) {
		if (convert_to_ifc(f, TopoDS::Face(exp.Current()), fa, advanced)) {
			faces.push_back(fa);
		} else {
			std::set<express::Base> created;
            for (auto& face : faces) {
                auto resources = f.traverse(face);
                created.insert(resources.begin(), resources.end());
			}
            for (auto& c : created) {
                f.removeEntity(c);
            }
			return 0;
		}
	}

	item = f.create<U>();
    item.setCfsFaces(faces);

	return faces.size();
}

express::Base POSTFIX_SCHEMA(serialise)(IfcParse::IfcFile& f, const TopoDS_Shape& shape, bool advanced) {

#ifndef SCHEMA_HAS_IfcAdvancedBrep
	advanced = false;
#endif

	for (TopExp_Explorer exp(shape, TopAbs_COMPSOLID); exp.More();) {
		/// @todo CompSolids are not supported
        return express::Base{};
	}

	IfcSchema::IfcRepresentation rep;
	std::vector<IfcSchema::IfcRepresentationItem> items;

	// First check if there is a solid with one or more shells
	for (TopExp_Explorer exp(shape, TopAbs_SOLID); exp.More(); exp.Next()) {
		IfcSchema::IfcClosedShell outer;
		std::vector<IfcSchema::IfcClosedShell> inner;
		for (TopExp_Explorer exp2(exp.Current(), TopAbs_SHELL); exp2.More(); exp2.Next()) {
			IfcSchema::IfcClosedShell shell;
			if (!convert_to_ifc(f, exp2.Current(), shell, advanced)) {
                return express::Base{};
			}
			/// @todo Are shells always in this order or does Orientation() needs to be checked?
			/// > #4216, no, consider using BRepClass3d::OuterShell()
			if (outer) {
				inner.push_back(shell);
			} else {
				outer = shell;
			}
		}

#ifdef SCHEMA_HAS_IfcAdvancedBrep
		if (advanced) {
			if (inner.size()) {
				auto inst = f.create<IfcSchema::IfcAdvancedBrepWithVoids>();
				inst.setOuter(outer);
                inst.setVoids(inner);
				items.push_back(inst);
			} else {
                auto inst = f.create<IfcSchema::IfcAdvancedBrep>();
                inst.setOuter(outer);
                items.push_back(inst);
			}
		} else
#endif

			/// @todo this is not necessarily correct as the shell is not necessarily facetted.
			if (inner.size()) {
                auto inst = f.create<IfcSchema::IfcFacetedBrepWithVoids>();
                inst.setOuter(outer);
                inst.setVoids(inner);
                items.push_back(inst);
			} else {
				auto inst = f.create<IfcSchema::IfcFacetedBrep>();
                inst.setOuter(outer);
				items.push_back(inst);
			}

	}

	if (items.size() > 0) {
		auto srep = f.create<IfcSchema::IfcShapeRepresentation>();
		srep.setRepresentationIdentifier("Body");
		srep.setRepresentationType(advanced ? "AdvancedBrep" : "Brep");
		srep.setItems(items);
        rep = srep;
	} else {

		// If not, see if there is a shell
		std::vector<IfcSchema::IfcShell> shells;
		for (TopExp_Explorer exp(shape, TopAbs_SHELL); exp.More(); exp.Next()) {
			IfcSchema::IfcOpenShell shell;
			if (!convert_to_ifc(f, exp.Current(), shell, advanced)) {
                return express::Base{};
			}
			shells.push_back(shell);
		}

		if (shells.size() > 0) {
            auto inst = f.create<IfcSchema::IfcShellBasedSurfaceModel>();
            inst.setSbsmBoundary(shells);
			items.push_back(inst);

			auto srep = f.create<IfcSchema::IfcShapeRepresentation>();
			srep.setRepresentationIdentifier("Body");
			srep.setRepresentationType(advanced ? "AdvancedBrep" : "Brep");
            srep.setItems(items);

			rep = srep;
		} else {

			// If not, see if there is are one of more faces. Note that they will be grouped into a shell.
			IfcSchema::IfcOpenShell shell;
			int face_count = convert_to_ifc(f, shape, shell, advanced);

			if (face_count > 0) {
				items.push_back(shell);
                auto srep = f.create<IfcSchema::IfcShapeRepresentation>();
                srep.setRepresentationIdentifier("Body");
                srep.setRepresentationType(advanced ? "AdvancedBrep" : "Brep");
                srep.setItems(items);

				rep = srep;
			} else {

				// If not, see if there are any edges. Note that wires are skipped as
				// they are not commonly top-level geometrical descriptions in IFC.
				// Also note that edges are written as trimmed curves rather than edges.

				std::vector<express::Entity> edges;

				for (TopExp_Explorer exp(shape, TopAbs_EDGE); exp.More(); exp.Next()) {
					IfcSchema::IfcCurve c;
					if (!convert_to_ifc(f, TopoDS::Edge(exp.Current()), c, advanced)) {
                        return express::Base{};
					}
					edges.push_back(c);
				}

				if (edges.size() == 0) {
                    return express::Base{};
				} else if (edges.size() == 1) {
                    auto srep = f.create<IfcSchema::IfcShapeRepresentation>();
                    srep.setRepresentationIdentifier("Axis");
                    srep.setRepresentationType("Curve2D");
                    srep.setItems(cast_vector<IfcSchema::IfcRepresentationItem>(edges));
                    rep = srep;
				} else {
					// A geometric set is created as that probably (?) makes more sense in IFC
					auto curves = f.create<IfcSchema::IfcGeometricCurveSet>();
                    curves.setElements(cast_vector<IfcSchema::IfcGeometricSetSelect>(edges));
                    items.push_back(curves);

                    auto srep = f.create<IfcSchema::IfcShapeRepresentation>();
                    srep.setRepresentationIdentifier("Axis");
                    srep.setRepresentationType("GeometricCurveSet");
                    srep.setItems(items);
                    rep = srep;
				}

			}
		}
	}

	auto pds = f.create<IfcSchema::IfcProductDefinitionShape>();
    pds.setRepresentations({rep});

	return pds;
}

express::Base POSTFIX_SCHEMA(tesselate)(IfcParse::IfcFile& f, const TopoDS_Shape& shape, double deflection) {
	// @todo use triangulated face set in ifc4+ schema

	BRepMesh_IncrementalMesh(shape, deflection);

	std::vector<IfcSchema::IfcFace> faces;

	for (TopExp_Explorer exp(shape, TopAbs_FACE); exp.More(); exp.Next()) {
		const TopoDS_Face& face = TopoDS::Face(exp.Current());
		TopLoc_Location loc;
		Handle(Poly_Triangulation) tri = BRep_Tool::Triangulation(face, loc);

		if (!tri.IsNull()) {
			std::vector<IfcSchema::IfcCartesianPoint> vertices;
			for (int i = 1; i <= tri->NbNodes(); ++i) {
				gp_Pnt pnt = tri->Node(i).Transformed(loc);
				std::vector<double> xyz; xyz.push_back(pnt.X()); xyz.push_back(pnt.Y()); xyz.push_back(pnt.Z());
                IfcSchema::IfcCartesianPoint cpnt = f.create<IfcSchema::IfcCartesianPoint>();
                cpnt.setCoordinates(xyz);
				vertices.push_back(cpnt);
			}
			const Poly_Array1OfTriangle& triangles = tri->Triangles();
			for (int i = 1; i <= triangles.Length(); ++i) {
				int n1, n2, n3;
				triangles(i).Get(n1, n2, n3);
                std::vector<IfcSchema::IfcCartesianPoint> points {
                    vertices[n1 - 1], vertices[n2 - 1], vertices[n3 - 1]
                };
                IfcSchema::IfcPolyLoop loop = f.create<IfcSchema::IfcPolyLoop>();
                loop.setPolygon(points);
                IfcSchema::IfcFaceOuterBound bound = f.create<IfcSchema::IfcFaceOuterBound>();
                bound.setBound(loop);
                bound.setOrientation(face.Orientation() != TopAbs_REVERSED);
                IfcSchema::IfcFace face2 = f.create<IfcSchema::IfcFace>();
                face2.setBounds({bound});
				faces.push_back(face2);
			}
		}
	}
    auto shell = f.create<IfcSchema::IfcOpenShell>();
    shell.setCfsFaces(faces);

    auto surface_model = f.create<IfcSchema::IfcFaceBasedSurfaceModel>();
    surface_model.setFbsmFaces({shell});

	auto rep = f.create<IfcSchema::IfcShapeRepresentation>();
    rep.setRepresentationIdentifier("Tessellation");
    rep.setRepresentationType("SurfaceModel");
    rep.setItems({surface_model});

	auto shapedef = f.create<IfcSchema::IfcProductDefinitionShape>();
    shapedef.setRepresentations({rep});

	return shapedef;
}
