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

/********************************************************************************
 *                                                                              *
 * Implementations of the various conversion functions defined in mapping.i *
 *                                                                              *
 ********************************************************************************/

#define _USE_MATH_DEFINES
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
#include <BRepAdaptor_HCompCurve.hxx>
#include <Approx_Curve3d.hxx>

#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

namespace {
	// Returns the first edge of a wire
	TopoDS_Edge first_edge(const TopoDS_Wire& w) {
		TopoDS_Vertex v1, v2;
		TopExp::Vertices(w, v1, v2);
		TopTools_IndexedDataMapOfShapeListOfShape wm;
		TopExp::MapShapesAndAncestors(w, TopAbs_VERTEX, TopAbs_EDGE, wm);
		return TopoDS::Edge(wm.FindFromKey(v1).First());
	}

	// Returns new wire with the edge replaced by a linear edge with the vertex v moved to p
	TopoDS_Wire adjust(const TopoDS_Wire& w, const TopoDS_Vertex& v, const gp_Pnt& p) {
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

	// A wrapper around BRepBuilderAPI_MakeWire that makes sure segments are connected either by moving end points or by adding intermediate segments
	class wire_builder {
	private:
		BRepBuilderAPI_MakeWire mw_;
		double p_;
		bool override_next_;
		gp_Pnt next_override_;
		const IfcUtil::IfcBaseClass* inst_;

	public:
		wire_builder(double p, const IfcUtil::IfcBaseClass* inst = 0) : p_(p), override_next_(false), inst_(inst) {}

		void operator()(const TopoDS_Shape& a) {
			const TopoDS_Wire& w = TopoDS::Wire(a);
			if (override_next_) {
				override_next_ = false;
				TopoDS_Edge e = first_edge(w);
				mw_.Add(adjust(w, TopExp::FirstVertex(e, true), next_override_));
			} else {
				mw_.Add(w);
			}			
		}

		void operator()(const TopoDS_Shape& a, const TopoDS_Shape& b, bool last) {
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

		const TopoDS_Wire& wire() { return mw_.Wire(); }
	};

	template <typename Fn>
	void shape_pair_enumerate(TopTools_ListIteratorOfListOfShape& it, Fn& fn, bool closed) {
		bool is_first = true;
		TopoDS_Shape first, previous, current;
		for (; it.More(); it.Next(), is_first = false) {
			current = it.Value();
			if (is_first) {
				first = current;
			} else {
				fn(previous, current, false);
			}
			previous = current;
		}
		if (closed) {
			fn(current, first, true);
		} else {
			fn(current);
		}
	}
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCompositeCurve* l, TopoDS_Wire& wire) {
	if ( getValue(GV_PLANEANGLE_UNIT)<0 ) {
		Logger::Message(Logger::LOG_WARNING,"Creating a composite curve without unit information:",l);

		// Temporarily pretend we do have unit information
		setValue(GV_PLANEANGLE_UNIT,1.0);
		
		bool succes_radians = false;
        bool succes_degrees = false;
        bool use_radians = false;
        bool use_degrees = false;

		// First try radians
		TopoDS_Wire wire_radians, wire_degrees;
        try {
		    succes_radians = IfcGeom::Kernel::convert(l,wire_radians);
        } catch (const std::exception& e) {
			Logger::Notice(e);
		} catch (const Standard_Failure& e) {
			if (e.GetMessageString() && strlen(e.GetMessageString())) {
				Logger::Notice(e.GetMessageString());
			} else {
				Logger::Notice("Unknown error using radians");
			}
		} catch (...) {
			Logger::Notice("Unknown error using radians");
		}

		// Now try degrees
		setValue(GV_PLANEANGLE_UNIT,0.0174532925199433);
        try {
		    succes_degrees = IfcGeom::Kernel::convert(l,wire_degrees);
        } catch (const std::exception& e) {
			Logger::Notice(e);
		} catch (const Standard_Failure& e) {
			if (e.GetMessageString() && strlen(e.GetMessageString())) {
				Logger::Notice(e.GetMessageString());
			} else {
				Logger::Notice("Unknown error using degrees");
			}
		} catch (...) {
			Logger::Notice("Unknown error using degrees");
		}

		// Restore to unknown unit state
		setValue(GV_PLANEANGLE_UNIT,-1.0);

		if ( succes_degrees && ! succes_radians ) {
			use_degrees = true;
		} else if ( succes_radians && ! succes_degrees ) {
			use_radians = true;
		} else if ( succes_radians && succes_degrees ) {
			if ( wire_degrees.Closed() && ! wire_radians.Closed() ) {
				use_degrees = true;
			} else if ( wire_radians.Closed() && ! wire_degrees.Closed() ) {
				use_radians = true;
			} else {
				// No heuristic left to prefer the one over the other,
				// apparently both variants are equally successful.
				// The curve might be composed of only straight segments.
				// Let's go with the wire created using radians as that
				// at least is a SI unit.
				use_radians = true;
			}
		}

		if ( use_radians ) {
			Logger::Message(Logger::LOG_NOTICE,"Used radians to create composite curve");
            wire = wire_radians;
		} else if ( use_degrees ) {
			Logger::Message(Logger::LOG_NOTICE,"Used degrees to create composite curve");
            wire = wire_degrees;
		}

		return use_radians || use_degrees;
	}

#ifdef SCHEMA_HAS_IfcSegment
	// 4x3
	IfcSchema::IfcSegment::list::ptr segments = l->Segments();
#else
	IfcSchema::IfcCompositeCurveSegment::list::ptr segments = l->Segments();
#endif

	TopTools_ListOfShape converted_segments;
	
	for (auto it = segments->begin(); it != segments->end(); ++it) {

		if (!(*it)->declaration().is(IfcSchema::IfcCompositeCurveSegment::Class())) {
			Logger::Error("Not implemented", *it);
			return false;
		}

		IfcSchema::IfcCurve* curve = ((IfcSchema::IfcCompositeCurveSegment*)(*it))->ParentCurve();

		// The type of ParentCurve is IfcCurve, but the documentation says:
		// ParentCurve: The *bounded curve* which defines the geometry of the segment. 
		// At least let's exclude IfcLine as an infinite linear segment
		// definitely does not make any sense.
		TopoDS_Wire segment;

		if (curve->as<IfcSchema::IfcLine>()) {
			Logger::Notice("Infinite IfcLine used as ParentCurve of segment, treating as a segment", *it);
			Handle_Geom_Curve handle;
			convert_curve(curve, handle);
			double u0 = 0.0;
			double u1 = curve->as<IfcSchema::IfcLine>()->Dir()->Magnitude() * getValue(GV_LENGTH_UNIT);
			if (u1 < getValue(GV_PRECISION)) {
				Logger::Warning("Segment length below tolerance", *it);
			}
			BRepBuilderAPI_MakeEdge me(handle, u0, u1);
			if (me.IsDone()) {
				BRep_Builder B;
				B.MakeWire(segment);
				B.Add(segment, me.Edge());
			}
		} else if (!convert_wire(curve, segment)) {
			const bool failed_on_purpose = curve->as<IfcSchema::IfcPolyline>() && !segment.IsNull();
			Logger::Message(failed_on_purpose ? Logger::LOG_WARNING : Logger::LOG_ERROR, "Failed to convert curve:", curve);
			continue;
		}

		if (!((IfcSchema::IfcCompositeCurveSegment*)(*it))->SameSense()) {
			segment.Reverse();
		}

		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(segment, getValue(GV_PRECISION), TopAbs_WIRE);

		converted_segments.Append(segment);

	}

	if (converted_segments.Extent() == 0) {
		Logger::Message(Logger::LOG_ERROR, "No segment succesfully converted:", l);
		return false;
	}

	BRepBuilderAPI_MakeWire w;
	TopoDS_Vertex wire_first_vertex, wire_last_vertex, edge_first_vertex, edge_last_vertex;

	TopTools_ListIteratorOfListOfShape it(converted_segments);

	aggregate_of_instance::ptr profile = l->data().getInverse(&IfcSchema::IfcProfileDef::Class(), -1);
	const bool force_close = profile && profile->size() > 0;

	wire_builder bld(getValue(GV_PRECISION), l);
	shape_pair_enumerate(it, bld, force_close);
	wire = bld.wire();

	return true;
}

namespace {

	/*
	Below is code to deduce the formula below in SageMath

	| R, b = var('R b')
	| 
	| Bxy = R * cos(b), R * sin(b)
	| Cxy = R * cos(b/2), R * sin(b/2)
	| 
	| def dot(v, w):
	|     return v[0] * w[0] + v[1] * w[1]
	| 
	| def norm(v):
	|     l = sqrt(v[0]^2 + v[1]^2)
	|     return v[0] / l, v[1] / l
	| 
	| (R - R*dot(norm(Cxy), norm(Bxy))).full_simplify()
	*/

	double deflection_for_approximating_circle(double radius, double param) {
		return -radius * std::cos(1. / 2. * param) * std::cos(param) - radius * std::sin(1. / 2. * param) * std::sin(param) + radius;
	}
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTrimmedCurve* l, TopoDS_Wire& wire) {
	IfcSchema::IfcCurve* basis_curve = l->BasisCurve();
	bool isConic = basis_curve->declaration().is(IfcSchema::IfcConic::Class());
	double parameterFactor = isConic ? getValue(GV_PLANEANGLE_UNIT) : getValue(GV_LENGTH_UNIT);
	
	Handle(Geom_Curve) curve;
	if (shape_type(basis_curve) == ST_CURVE) {
		if (!convert_curve(basis_curve, curve)) return false;
	} else if (shape_type(basis_curve) == ST_WIRE) {
		Logger::Warning("Approximating BasisCurve due to possible discontinuities", l);
		TopoDS_Wire w;
		if (!convert_wire(basis_curve, w)) return false;
		BRepAdaptor_CompCurve cc(w, true);
		Handle(Adaptor3d_HCurve) hcc = Handle(Adaptor3d_HCurve)(new BRepAdaptor_HCompCurve(cc));
		// @todo, arbitrary numbers here, note they cannot be too high as contiguous memory is allocated based on them.
		Approx_Curve3d approx(hcc, getValue(GV_PRECISION), GeomAbs_C0, 10, 10);
		curve = approx.Curve();
	} else {
		Logger::Error("Unknown BasisCurve", l);
		return false;
	}
	
	bool trim_cartesian = l->MasterRepresentation() != IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER;
	aggregate_of_instance::ptr trims1 = l->Trim1();
	aggregate_of_instance::ptr trims2 = l->Trim2();
	
	unsigned sense_agreement = l->SenseAgreement() ? 0 : 1;
	double flts[2];
	gp_Pnt pnts[2];
	bool has_flts[2] = {false,false};
	bool has_pnts[2] = {false,false};
	
	TopoDS_Edge e;

	for ( aggregate_of_instance::it it = trims1->begin(); it != trims1->end(); it ++ ) {
		IfcUtil::IfcBaseClass* i = *it;
		if ( i->declaration().is(IfcSchema::IfcCartesianPoint::Class()) ) {
			IfcGeom::Kernel::convert((IfcSchema::IfcCartesianPoint*)i, pnts[sense_agreement] );
			has_pnts[sense_agreement] = true;
		} else if ( i->declaration().is(IfcSchema::IfcParameterValue::Class()) ) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[sense_agreement] = value * parameterFactor;
			has_flts[sense_agreement] = true;
		}
	}

	for ( aggregate_of_instance::it it = trims2->begin(); it != trims2->end(); it ++ ) {
		IfcUtil::IfcBaseClass* i = *it;
		if ( i->declaration().is(IfcSchema::IfcCartesianPoint::Class()) ) {
			IfcGeom::Kernel::convert((IfcSchema::IfcCartesianPoint*)i, pnts[1-sense_agreement] );
			has_pnts[1-sense_agreement] = true;
		} else if ( i->declaration().is(IfcSchema::IfcParameterValue::Class()) ) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[1-sense_agreement] = value * parameterFactor;
			has_flts[1-sense_agreement] = true;
		}
	}

	trim_cartesian &= has_pnts[0] && has_pnts[1];
	bool trim_cartesian_failed = !trim_cartesian;
	if ( trim_cartesian ) {
		if ( pnts[0].Distance(pnts[1]) < 2 * getValue(GV_PRECISION) ) {
			Logger::Message(Logger::LOG_WARNING,"Skipping segment with length below tolerance level:",l);
			return false;
		}
		ShapeFix_ShapeTolerance FTol;
		TopoDS_Vertex v1 = BRepBuilderAPI_MakeVertex(pnts[0]);
		TopoDS_Vertex v2 = BRepBuilderAPI_MakeVertex(pnts[1]);
		FTol.SetTolerance(v1, getValue(GV_PRECISION), TopAbs_VERTEX);
		FTol.SetTolerance(v2, getValue(GV_PRECISION), TopAbs_VERTEX);
		BRepBuilderAPI_MakeEdge me (curve,v1,v2);
		if (!me.IsDone()) {
			BRepBuilderAPI_EdgeError err = me.Error();
			if ( err == BRepBuilderAPI_PointProjectionFailed ) {
				Logger::Message(Logger::LOG_WARNING,"Point projection failed for:",l);
				trim_cartesian_failed = true;
			}
		} else {
			e = me.Edge();
			// BRepBuilderAPI_MakeEdge swaps v1 and v2 if the parameter value of v2 is 
			// smaller than that of v1. In that case the edge has to be reversed so that
			// the vertex order is consistent with Trim1 and Trim2. Otherwise the
			// IfcOpenShell wire builder will create intermediate edges automatically.
			// The alternative would be to reverse the underlying curve instead.
			if (!TopExp::FirstVertex(e, true).IsSame(v1)) {
				e.Reverse();
			}
		}
	}

	if ( (!trim_cartesian || trim_cartesian_failed) && (has_flts[0] && has_flts[1]) ) {
		// The Geom_Line is constructed from a gp_Pnt and gp_Dir, whereas the IfcLine
		// is defined by an IfcCartesianPoint and an IfcVector with Magnitude. Because
		// the vector is normalised when passed to Geom_Line constructor the magnitude
		// needs to be factored in with the IfcParameterValue here.
		if ( basis_curve->declaration().is(IfcSchema::IfcLine::Class()) ) {
			IfcSchema::IfcLine* line = static_cast<IfcSchema::IfcLine*>(basis_curve);
			const double magnitude = line->Dir()->Magnitude();
			flts[0] *= magnitude; flts[1] *= magnitude;
		}
		if ( basis_curve->declaration().is(IfcSchema::IfcEllipse::Class()) ) {
			IfcSchema::IfcEllipse* ellipse = static_cast<IfcSchema::IfcEllipse*>(basis_curve);
			double x = ellipse->SemiAxis1() * getValue(GV_LENGTH_UNIT);
			double y = ellipse->SemiAxis2() * getValue(GV_LENGTH_UNIT);
			const bool rotated = y > x;
			if (rotated) {
				flts[0] -= M_PI / 2.;
				flts[1] -= M_PI / 2.;
			}
		}

		double radius = 1.0;
		if (curve->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
			auto circle_curve = Handle_Geom_Circle::DownCast(curve);
			radius = circle_curve->Radius();
		} else if (curve->DynamicType() == STANDARD_TYPE(Geom_Ellipse)) {
			auto circle_curve = Handle_Geom_Ellipse::DownCast(curve);
			radius = (circle_curve->MajorRadius() + circle_curve->MinorRadius()) / 2.;
		}

		// Fix from @sanderboer to compare using model tolerance, see #744
		// Made dependent on radius, see #928

		// A good critereon for determining whether to take full curve
		// or trimmed segment would be whether there are other curve segments or this
		// is the only one.
		boost::optional<size_t> num_segments;
		auto segment = l->data().getInverse(&IfcSchema::IfcCompositeCurveSegment::Class(), -1);
		if (segment->size() == 1) {
			auto comp = (*segment->begin())->data().getInverse(&IfcSchema::IfcCompositeCurve::Class(), -1);
			if (comp->size() == 1) {
				num_segments = (*comp->begin())->as<IfcSchema::IfcCompositeCurve>()->Segments()->size();
			}
		}

		if (isConic && ALMOST_THE_SAME(fmod(flts[1]-flts[0],M_PI*2.), 0., 100 * getValue(GV_PRECISION) / (2 * M_PI * radius))) {
			e = BRepBuilderAPI_MakeEdge(curve).Edge();
		} else {
			BRepBuilderAPI_MakeEdge me (curve,flts[0],flts[1]);
			e = me.Edge();
		}

		if (num_segments && *num_segments > 1) {
			TopoDS_Vertex v0, v1;
			TopExp::Vertices(e, v0, v1);
			if (v0.IsSame(v1)) {
				Logger::Warning("Skipping degenerate segment", l);
				return false;
			}
		}

	} else if ( trim_cartesian_failed && (has_pnts[0] && has_pnts[1]) ) {
		e = BRepBuilderAPI_MakeEdge(pnts[0], pnts[1]).Edge();
	}

	if (e.IsNull()) {
		return false;
	}

	if (isConic) {
		// Tiny circle segnments can cause issues later on, for example
		// when the comp curve is used as the sweeping directrix.
		double a, b;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(e, a, b);
		double radius = -1.;
		if (crv->DynamicType() == STANDARD_TYPE(Geom_Circle)) {
			radius = Handle(Geom_Circle)::DownCast(crv)->Radius();
		} else if (crv->DynamicType() == STANDARD_TYPE(Geom_Ellipse)) {
			// The formula in deflection_for_approximating_circle() is for circles, but probably good enough
			radius = Handle(Geom_Ellipse)::DownCast(crv)->MajorRadius();
		}
		if (radius > 0. && deflection_for_approximating_circle(radius, b - a) < 100 * getValue(GV_PRECISION) && std::abs(b-a) < M_PI/4.) {
			TopoDS_Vertex v0, v1;
			TopExp::Vertices(e, v0, v1);
			e = TopoDS::Edge(BRepBuilderAPI_MakeEdge(v0, v1).Edge().Oriented(e.Orientation()));
			Logger::Warning("Subsituted edge with linear approximation", l);
		}
	}

	BRepBuilderAPI_MakeWire w;
	w.Add(e);

	if (w.IsDone()) {
		wire = w.Wire();

		// When SenseAgreement == .F. the vertices above have been reversed to
		// comply with the direction of conical curves. The ordering of the
		// vertices then still needs to be reversed in order to have begin and
		// end vertex consistent with IFC.
		if (sense_agreement != 0) { // .F.
			wire.Reverse();
		}

		return true;
	} else {
		return false;
	}
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPolyline* l, TopoDS_Wire& result) {
	IfcSchema::IfcCartesianPoint::list::ptr points = l->Points();

	// Parse and store the points in a sequence
	TColgp_SequenceOfPnt polygon;
	for(IfcSchema::IfcCartesianPoint::list::it it = points->begin(); it != points->end(); ++ it) {
		gp_Pnt pnt;
		IfcGeom::Kernel::convert(*it, pnt);
		polygon.Append(pnt);
	}

	// @todo the strict tolerance should also govern these arbitrary precision increases
	const double eps = getValue(GV_PRECISION) * 10;
	const bool closed_by_proximity = polygon.Length() >= 3 && polygon.First().Distance(polygon.Last()) < eps;
	if (closed_by_proximity) {
		// tfk: note 1-based
		polygon.Remove(polygon.Length());
	}

	// Remove points that are too close to one another
	remove_duplicate_points_from_loop(polygon, closed_by_proximity, eps);

	if (polygon.Length() < 2) {
		// We somehow need to signal we fail this curve on purpose not to trigger an error.
		BRep_Builder B;
		B.MakeWire(result);
		return false;
	}
	
	BRepBuilderAPI_MakePolygon w;
	for (int i = 1; i <= polygon.Length(); ++i) {
		w.Add(polygon.Value(i));
	}

	if (closed_by_proximity) {
		w.Close();
	}

	result = w.Wire();
	return true;
}

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
	if (wire_intersections(result, results)) {
		Logger::Error("Self-intersections with " + boost::lexical_cast<std::string>(results.Extent()) + " cycles detected", l);
		select_largest(results, result);
	}

	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcArbitraryOpenProfileDef* l, TopoDS_Wire& result) {
	return convert_wire(l->Curve(), result);
}

#include <Extrema_ExtPC.hxx>

namespace {
	bool create_edge_over_curve_with_log_messages(const Handle_Geom_Curve& crv, const double eps, const gp_Pnt& p1, const gp_Pnt& p2, TopoDS_Edge& result) {
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
}

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
		if (create_edge_over_curve_with_log_messages(crv, getValue(GV_PRECISION), p1, p2, e)) {
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
			if (create_edge_over_curve_with_log_messages(ecrv, getValue(GV_PRECISION), a, b, e)) {
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

bool IfcGeom::Kernel::convert(const IfcSchema::IfcEdgeLoop* l, TopoDS_Wire& result) {
	IfcSchema::IfcOrientedEdge::list::ptr li = l->EdgeList();
	BRepBuilderAPI_MakeWire mw;
	for (IfcSchema::IfcOrientedEdge::list::it it = li->begin(); it != li->end(); ++it) {
		TopoDS_Wire w;
		if (convert_wire(*it, w)) {
			mw.Add(TopoDS::Edge(TopoDS_Iterator(w).Value()));
		}
	}
	if (!mw.IsDone()) {
		return false;
	}
	result = mw.Wire();
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcEdge* l, TopoDS_Wire& result) {
	if (!l->EdgeStart()->declaration().is(IfcSchema::IfcVertexPoint::Class()) || !l->EdgeEnd()->declaration().is(IfcSchema::IfcVertexPoint::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Only IfcVertexPoints are supported for EdgeStart and -End", l);
		return false;
	}

	IfcSchema::IfcPoint* pnt1 = ((IfcSchema::IfcVertexPoint*) l->EdgeStart())->VertexGeometry();
	IfcSchema::IfcPoint* pnt2 = ((IfcSchema::IfcVertexPoint*) l->EdgeEnd())->VertexGeometry();
	if (!pnt1->declaration().is(IfcSchema::IfcCartesianPoint::Class()) || !pnt2->declaration().is(IfcSchema::IfcCartesianPoint::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Only IfcCartesianPoints are supported for VertexGeometry", l);
		return false;
	}
	
	gp_Pnt p1, p2;
	if (!convert(((IfcSchema::IfcCartesianPoint*)pnt1), p1) ||
		!convert(((IfcSchema::IfcCartesianPoint*)pnt2), p2))
	{
		return false;
	}

	BRepBuilderAPI_MakeWire mw;
	mw.Add(BRepBuilderAPI_MakeEdge(p1, p2));

	result = mw.Wire();
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcOrientedEdge* l, TopoDS_Wire& result) {
	if (convert_wire(l->EdgeElement(), result)) {
		if (!l->Orientation()) {
			result.Reverse();
		}
		return true;
	} else {
		return false;
	}
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSubedge* l, TopoDS_Wire& result) {
	TopoDS_Wire temp;
	if (convert_wire(l->ParentEdge(), result) && convert((IfcSchema::IfcEdge*) l, temp)) {
		TopExp_Explorer exp(result, TopAbs_EDGE);
		TopoDS_Edge edge = TopoDS::Edge(exp.Current());
		Standard_Real u1, u2;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u1, u2);
		TopoDS_Vertex v1, v2;
		TopExp::Vertices(temp, v1, v2);
		BRepBuilderAPI_MakeWire mw;
		mw.Add(BRepBuilderAPI_MakeEdge(crv, v1, v2));
		result = mw.Wire();
		return true;
	} else {
		return false;
	}
}

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
