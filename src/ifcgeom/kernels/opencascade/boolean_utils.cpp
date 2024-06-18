#include "boolean_utils.h"

#include "IfcGeomTree.h"
#include "base_utils.h"

#include <BRepBuilderAPI_Copy.hxx>
#include <TopExp_Explorer.hxx>
#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>
#include <TopExp.hxx>
#include <TopoDS.hxx>
#include <Bnd_Box.hxx>
#include <Extrema_ExtPC.hxx>
#include <Geom_Plane.hxx>
#include <Geom_BSplineCurve.hxx>
#include <ShapeUpgrade_UnifySameDomain.hxx>
#include <GeomAPI_ExtremaCurveCurve.hxx>
#include <ShapeAnalysis_Surface.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <Standard_Version.hxx>
#include <BRepAlgoAPI_Fuse.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BOPAlgo_PaveFiller.hxx>
#include <BOPAlgo_Alerts.hxx>
#include <ShapeFix_Shape.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepCheck_ListIteratorOfListOfStatus.hxx>
#include <BRepCheck.hxx>
#include <ShapeAnalysis_Edge.hxx>
#include <Bnd_OBB.hxx>

#include <vector>
#include <thread>

void IfcGeom::util::copy_operand(const TopTools_ListOfShape & l, TopTools_ListOfShape & r) {
#if OCC_VERSION_HEX < 0x70000
	r.Clear();
	TopTools_ListIteratorOfListOfShape it(l);
	for (; it.More(); it.Next()) {
		r.Append(BRepBuilderAPI_Copy(it.Value()));
	}
#else
	// On OCCT 7.0 and higher BRepAlgoAPI_BuilderAlgo::SetNonDestructive(true) is
	// called. Not entirely sure on the behaviour before 7.0, so overcautiously
	// create copies.
	r.Assign(l);
#endif
}

TopoDS_Shape IfcGeom::util::copy_operand(const TopoDS_Shape & s) {
#if OCC_VERSION_HEX < 0x70000
	return BRepBuilderAPI_Copy(s);
#else
	return s;
#endif
}

double IfcGeom::util::min_edge_length(const TopoDS_Shape & a) {
	double min_edge_len = std::numeric_limits<double>::infinity();
	TopExp_Explorer exp(a, TopAbs_EDGE);
	for (; exp.More(); exp.Next()) {
		const TopoDS_Edge& e = TopoDS::Edge(exp.Current());
		
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(e, v0, v1);
		if (!v0.IsNull() && !v1.IsNull() && v0.IsSame(v1)) {
			// Don't consider a 3d-degenerate edge (for example cone apex)
			// in calculating overall shape min edge length.
			continue;
		}

		GProp_GProps prop;
		BRepGProp::LinearProperties(e, prop);
		double l = prop.Mass();
		if (l < min_edge_len) {
			min_edge_len = l;
		}
	}
	return min_edge_len;
}

double IfcGeom::util::min_vertex_edge_distance(const TopoDS_Shape & a, double min_search, double max_search) {
	double M = std::numeric_limits<double>::infinity();

	TopTools_IndexedMapOfShape vertices, edges;

	TopExp::MapShapes(a, TopAbs_VERTEX, vertices);
	TopExp::MapShapes(a, TopAbs_EDGE, edges);

	IfcGeom::impl::tree<int> tree;

	// Add edges to tree
	for (int i = 1; i <= edges.Extent(); ++i) {
		tree.add(i, edges(i));
	}

	for (int j = 1; j <= vertices.Extent(); ++j) {
		const TopoDS_Vertex& v = TopoDS::Vertex(vertices(j));
		gp_Pnt p = BRep_Tool::Pnt(v);

		Bnd_Box b;
		b.Add(p);
		b.Enlarge(max_search);

		std::vector<int> edge_idxs = tree.select_box(b, false);
		std::vector<int>::const_iterator it = edge_idxs.begin();
		for (; it != edge_idxs.end(); ++it) {
			const TopoDS_Edge& e = TopoDS::Edge(edges(*it));
			TopoDS_Vertex v1, v2;
			TopExp::Vertices(e, v1, v2);

			if (v.IsSame(v1) || v.IsSame(v2)) {
				continue;
			}

			BRepAdaptor_Curve crv(e);
			Extrema_ExtPC ext(p, crv);
			if (!ext.IsDone()) {
				continue;
			}

			for (int i = 1; i <= ext.NbExt(); ++i) {
				const double m = sqrt(ext.SquareDistance(i));
				if (m < M && m > min_search) {
					M = m;
				}
			}
		}
	}

	return M;
}

bool IfcGeom::util::faces_overlap(const TopoDS_Face & f, const TopoDS_Face & g) {
	points_on_planar_face_generator pgen(f);

	BRep_Builder B;
	gp_Pnt test;
	double eps = BRep_Tool::Tolerance(f) + BRep_Tool::Tolerance(g);

	BRepExtrema_DistShapeShape x;
	x.LoadS1(g);

	while (pgen(test)) {
		TopoDS_Vertex V;
		B.MakeVertex(V, test, Precision::Confusion());
		x.LoadS2(V);
		x.Perform();
		if (x.IsDone() && x.NbSolution() == 1) {
			if (x.Value() > eps) {
				return false;
			}
		}
	}

	return true;
}

double IfcGeom::util::min_face_face_distance(const TopoDS_Shape & a, double max_search) {
	/*
	NB: This is currently only implemented for planar surfaces.
	*/
	double M = std::numeric_limits<double>::infinity();

	TopTools_IndexedMapOfShape faces;

	TopExp::MapShapes(a, TopAbs_FACE, faces);

	IfcGeom::impl::tree<int> tree;

	// Add faces to tree
	for (int i = 1; i <= faces.Extent(); ++i) {
		if (BRep_Tool::Surface(TopoDS::Face(faces(i)))->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
			tree.add(i, faces(i));
		}
	}

	for (int j = 1; j <= faces.Extent(); ++j) {
		const TopoDS_Face& f = TopoDS::Face(faces(j));
		const Handle(Geom_Surface)& fs = BRep_Tool::Surface(f);

		if (fs->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
			continue;
		}

		points_on_planar_face_generator pgen(f);

		Bnd_Box b;
		BRepBndLib::AddClose(f, b);
		b.Enlarge(max_search);

		std::vector<int> face_idxs = tree.select_box(b, false);
		std::vector<int>::const_iterator it = face_idxs.begin();
		for (; it != face_idxs.end(); ++it) {
			if (*it == j) {
				continue;
			}

			const TopoDS_Face& g = TopoDS::Face(faces(*it));
			const Handle(Geom_Surface)& gs = BRep_Tool::Surface(g);

			auto p0 = Handle(Geom_Plane)::DownCast(fs);
			auto p1 = Handle(Geom_Plane)::DownCast(gs);

			if (p0->Position().IsCoplanar(p1->Position(), max_search, asin(max_search))) {
				pgen.reset();

				BRepTopAdaptor_FClass2d cls(g, BRep_Tool::Tolerance(g));

				gp_Pnt test;
				while (pgen(test)) {
					gp_Vec d = test.XYZ() - p1->Position().Location().XYZ();
					double u = d.Dot(p1->Position().XDirection());
					double v = d.Dot(p1->Position().YDirection());

					// nb: TopAbs_ON is explicitly not considered to prevent matching adjacent faces
					// with similar orientations.
					if (cls.Perform(gp_Pnt2d(u, v)) == TopAbs_IN) {
						gp_Pnt test2;
						p1->D0(u, v, test2);
						double w = std::abs(gp_Vec(p1->Position().Direction().XYZ()).Dot(test2.XYZ() - test.XYZ()));
						if (w < M) {
							M = w;
						}
					}
				}
			}
		}
	}

	return M;
}

int IfcGeom::util::bounding_box_overlap(double p, const TopoDS_Shape & a, const TopTools_ListOfShape & b, TopTools_ListOfShape & c) {
	int N = 0;

	Bnd_Box A;
	BRepBndLib::Add(a, A);

	if (A.IsVoid()) {
		return 0;
	}

	TopTools_ListIteratorOfListOfShape it(b);
	for (; it.More(); it.Next()) {
		Bnd_Box B;
		BRepBndLib::Add(it.Value(), B);

		if (B.IsVoid()) {
			continue;
		}

		if (A.Distance(B) < p) {
			c.Append(it.Value());
		} else {
			++N;
		}
	}

	return N;
}

bool IfcGeom::util::get_edge_axis(const TopoDS_Edge & e, gp_Ax1 & ax) {
	double _, __;

	auto crv = BRep_Tool::Curve(e, _, __);
	auto line = Handle_Geom_Line::DownCast(crv);
	auto bsple = Handle_Geom_BSplineCurve::DownCast(crv);

	if (line) {
		ax = line->Position();
		return true;
	} else if (bsple) {
		if (bsple->NbPoles() == 2 && bsple->Degree() == 1) {
			gp_Dir V(bsple->Poles().Last().XYZ() - bsple->Poles().First().XYZ());
			ax = gp_Ax1(bsple->Poles().First(), V);
			return true;
		}
	}

	return false;
}

bool IfcGeom::util::is_subset(const TopTools_IndexedMapOfShape & lhs, const TopTools_IndexedMapOfShape & rhs) {
	if (rhs.Extent() < lhs.Extent()) {
		return false;
	}
	for (int i = 1; i < lhs.Extent(); ++i) {
		auto& s = lhs.FindKey(i);
		if (!rhs.Contains(s)) {
			return false;
		}
	}
	return true;
}

bool IfcGeom::util::is_extrusion(const gp_Vec & v, const TopoDS_Shape & s, TopoDS_Face & base, std::pair<double, double>& interval) {
	// This assumes UnifySameDomain has been processed on s, so that
	// the extrusion top and bottom are a single face.

	TopTools_IndexedDataMapOfShapeListOfShape mapping;
	TopExp::MapShapesAndAncestors(s, TopAbs_EDGE, TopAbs_FACE, mapping);
	TopExp::MapShapesAndAncestors(s, TopAbs_VERTEX, TopAbs_FACE, mapping);

	TopTools_ListOfShape parallel;
	TopTools_IndexedMapOfShape curved_orthogonal;
	gp_Ax1 ax;
	gp_Ax1 V(gp::Origin(), v);

	// Segment edges in parallel to extrusion direction, and orthogonal or curved,
	// where the latter two categories have to make the edges part of the base or
	// top face. When neither of these categories the shape is not a extrusion
	// or the extrusion direction is not orthogonal to its basis.
	for (int i = 1; i < mapping.Extent(); ++i) {
		auto& s = mapping.FindKey(i);
		if (s.ShapeType() != TopAbs_EDGE) {
			continue;
		}

		// @todo use a linear tolernace and the face extrimities, see #2218
		const TopoDS_Edge& e = TopoDS::Edge(s);
		if (!get_edge_axis(e, ax)) {
			// curved
			curved_orthogonal.Add(e);
		} else if (ax.IsParallel(V, 1.e-7)) {
			parallel.Append(e);
		} else if (ax.IsNormal(V, 1.e-7)) {
			// ortho
			curved_orthogonal.Add(e);
		} else {
			return false;
		}
	}

	// Select the two faces for which their edges are subsets
	// of the ortho/curved edges
	TopTools_IndexedMapOfShape ortho_faces;
	for (TopExp_Explorer exp(s, TopAbs_FACE); exp.More(); exp.Next()) {
		TopTools_IndexedMapOfShape face_edges;
		TopExp::MapShapes(exp.Current(), TopAbs_EDGE, face_edges);
		if (is_subset(face_edges, curved_orthogonal)) {
			ortho_faces.Add(exp.Current());
		}
	}

	// There should be a basis and top face
	if (ortho_faces.Extent() != 2) {
		return false;
	}

	// For the parallel edges assert that its two vertices are part
	// of both the basis and the top face.
	for (TopTools_ListIteratorOfListOfShape it(parallel);
		it.More(); it.Next()) {
		TopoDS_Vertex v01[2];
		TopExp::Vertices(TopoDS::Edge(it.Value()), v01[0], v01[1]);

		TopTools_IndexedMapOfShape v_ortho_faces;
		int nb_ortho_faces[2] = { 0,0 };

		for (int i = 0; i < 2; ++i) {
			auto& faces = mapping.FindFromKey(v01[i]);

			for (TopTools_ListIteratorOfListOfShape jt(faces);
				jt.More(); jt.Next()) {
				if (ortho_faces.Contains(jt.Value())) {
					nb_ortho_faces[i] ++;
					v_ortho_faces.Add(jt.Value());
				}
			}
		}

		bool sets_equal = v_ortho_faces.Size() == ortho_faces.Size() && is_subset(v_ortho_faces, ortho_faces);
		if (!sets_equal) {
			return false;
		}
	}

	// Assert the base/top faces are planar and get the interval
	// (dot products along axis) for which the extrusion is defined
	// If necessary swap the two faces so that the basis face has
	// the smallest dot product along the axis.
	auto f0 = TopoDS::Face(ortho_faces.FindKey(1));
	auto f1 = TopoDS::Face(ortho_faces.FindKey(2));

	const Handle(Geom_Surface)& f0_s = BRep_Tool::Surface(f0);
	const Handle(Geom_Surface)& f1_s = BRep_Tool::Surface(f1);

	auto p0 = Handle(Geom_Plane)::DownCast(f0_s);
	auto p1 = Handle(Geom_Plane)::DownCast(f1_s);

	if (p0.IsNull() || p1.IsNull()) {
		return false;
	}

	auto dot0 = p0->Location().XYZ().Dot(v.XYZ());
	auto dot1 = p1->Location().XYZ().Dot(v.XYZ());

	if (dot0 > dot1) {
		std::swap(dot0, dot1);
		std::swap(f0, f1);
	}

	base = f0;
	interval = { dot0, dot1 };

	return true;
}

int IfcGeom::util::eliminate_narrow_operands(double prec, const TopTools_ListOfShape& bs, TopTools_ListOfShape & c) {
	int N = 0;
	TopTools_ListIteratorOfListOfShape it(bs);
	for (; it.More(); it.Next()) {

		Bnd_OBB box;
		BRepBndLib::AddOBB(it.Value(), box, false, false, false);

		auto min_dimension = box.XHSize() < box.YHSize() ? box.XHSize() : box.YHSize();
		min_dimension = min_dimension < box.ZHSize() ? min_dimension : box.ZHSize();

		bool is_narrow = min_dimension < prec;

		Logger::Notice("Min OBB dimension of operand = " + std::to_string(min_dimension));

		if (!is_narrow) {
			c.Append(it.Value());
		} else {
			++N;
		}
	}
	return N;
}

int IfcGeom::util::eliminate_touching_operands(double prec, const TopoDS_Shape & a, const TopTools_ListOfShape & bs, TopTools_ListOfShape & c) {
	TopTools_IndexedMapOfShape a_faces;
	TopExp::MapShapes(a, TopAbs_FACE, a_faces);

	// Check if any of the faces in a are non-planar, which is
	// not supported by this quick check.
	for (int i = 1; i <= a_faces.Extent(); ++i) {
		auto surf = BRep_Tool::Surface(TopoDS::Face(a_faces(i)));
		if (surf->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
			return 0;
		}
	}

	TopTools_IndexedMapOfShape a_vertices;
	TopExp::MapShapes(a, TopAbs_VERTEX, a_vertices);

	IfcGeom::impl::tree<int> tree;

	// Add faces to tree
	for (int i = 1; i <= a_faces.Extent(); ++i) {
		tree.add(i, a_faces(i));
	}

	int N = 0;

	TopTools_ListIteratorOfListOfShape it(bs);
	for (; it.More(); it.Next()) {
		bool is_touching = false;

		auto& b = it.Value();

		TopTools_IndexedMapOfShape b_faces;
		TopExp::MapShapes(b, TopAbs_FACE, b_faces);

		// Check if any of the faces in b are non-planar, which is
		// not supported by this quick check.
		bool non_planar = false;
		for (int i = 1; i <= b_faces.Extent(); ++i) {
			auto surf = BRep_Tool::Surface(TopoDS::Face(b_faces(i)));
			if (surf->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
				non_planar = true;
				break;
			}
		}

		if (non_planar) {
			continue;
		}

		TopTools_IndexedMapOfShape b_vertices;
		TopExp::MapShapes(b, TopAbs_VERTEX, b_vertices);

		for (int k = 1; k <= b_faces.Extent(); ++k) {
			const TopoDS_Face& f_b = TopoDS::Face(b_faces(k));
			Bnd_Box B;
			BRepBndLib::Add(f_b, B);

			// Query tree using b_face bounding box
			for (auto& i : tree.select_box(B, false)) {
				const TopoDS_Face& f_a = TopoDS::Face(a_faces(i));

				TopTools_IndexedMapOfShape f_a_vertices;
				TopExp::MapShapes(f_a, TopAbs_VERTEX, f_a_vertices);

				BRepGProp_Face prop_a(f_a);
				BRepGProp_Face prop_b(f_b);

				gp_Pnt p_a, p_b;
				gp_Vec v_a, v_b;

				double u0, u1, v0, v1;
				prop_a.Bounds(u0, u1, v0, v1);
				prop_a.Normal((u0 + u1) / 2., (u0 + u1) / 2., p_a, v_a);

				prop_b.Bounds(u0, u1, v0, v1);
				prop_b.Normal((u0 + u1) / 2., (u0 + u1) / 2., p_b, v_b);

				bool all_vertices_behind_f_a = true;

				// Check if all 'other' vertices in a are pointing
				// away from the face in a, so that there is no geometry
				// from a in front of the face that could participate
				// in the boolean subtraction.
				for (int j = 1; j <= a_vertices.Extent(); ++j) {
					if (!f_a_vertices.Contains(a_vertices(j))) {
						auto p = BRep_Tool::Pnt(TopoDS::Vertex(a_vertices(j)));
						if ((p.XYZ() - p_a.XYZ()).Dot(v_a.XYZ()) > prec) {
							all_vertices_behind_f_a = false;
							break;
						}
					}
				}

				if (!all_vertices_behind_f_a) {
					continue;
				}

				// Check if surface normals are opposite
				if (v_a.IsOpposite(v_b, 1.e-5)) {
					// Check if faces are co-planar
					if ((p_b.XYZ() - p_a.XYZ()).Dot(v_a.XYZ()) <= prec) {

						TopTools_IndexedMapOfShape f_b_vertices;
						TopExp::MapShapes(f_b, TopAbs_VERTEX, f_b_vertices);

						bool all_vertices_behind_f_b = true;

						// Check if all 'other' vertices in b are pointing
						// away from the face in a. So that a boolean subtraction
						// would not alter a.
						for (int j = 1; j <= b_vertices.Extent(); ++j) {
							if (!f_b_vertices.Contains(b_vertices(j))) {
								auto p = BRep_Tool::Pnt(TopoDS::Vertex(b_vertices(j)));
								if ((p.XYZ() - p_a.XYZ()).Dot(v_a.XYZ()) < prec * 10.) {
									all_vertices_behind_f_b = false;
									break;
								}
							}
						}

						if (all_vertices_behind_f_b) {
							is_touching = true;
							break;
						}

					}
				}
			}

			if (is_touching) {
				break;
			}
		}

		if (!is_touching) {
			c.Append(it.Value());
		} else {
			++N;
		}
	}

	return N;
}

TopoDS_Shape IfcGeom::util::unify(const TopoDS_Shape & s, double tolerance) {
	tolerance = (std::min)(min_edge_length(s) / 2., tolerance);
	ShapeUpgrade_UnifySameDomain usd(s);
#if OCC_VERSION_HEX >= 0x70200
	usd.SetSafeInputMode(true);
#endif
#if OCC_VERSION_HEX >= 0x70100
	usd.SetLinearTolerance(tolerance);
	usd.SetAngularTolerance(1.e-3);
#endif
	usd.Build();
	return usd.Shape();
}

bool IfcGeom::util::boolean_subtraction_2d_using_builder(const TopoDS_Shape & a_input, const TopTools_ListOfShape & b_input, TopoDS_Shape & result, double eps) {
	IfcGeom::impl::tree<int> edge_tree;

	TopTools_ListOfShape ab_input = b_input;
	ab_input.Prepend(a_input);

	TopTools_ListIteratorOfListOfShape it(ab_input);
	int shape_index = 0;
	int edge_index = 0;
	std::map<int, int> edge_index_to_shape_index;

	std::vector<TopoDS_Shape> shapes;
	std::vector<std::pair<size_t, TopoDS_Edge>> edges;
	// First is the outer wire
	std::vector<TopoDS_Wire> wires;

	for (; it.More(); it.Next(), ++shape_index) {
		if (it.Value().ShapeType() != TopAbs_FACE) {
			return false;
		}

		const TopoDS_Face& f = TopoDS::Face(it.Value());
		TopoDS_Wire outer_wire;

		if (shape_index == 0) {
			outer_wire = BRepTools::OuterWire(f);
			wires.push_back(outer_wire);
		}

		size_t num_wires = 0;
		TopoDS_Iterator it2(it.Value());
		for (; it2.More(); it2.Next()) {
			++num_wires;

			if (outer_wire.IsNull() || !it2.Value().IsSame(outer_wire)) {
				wires.push_back(TopoDS::Wire(it2.Value()));

				if (shape_index == 0 && num_wires > 0) {
					// An inner wire on the first operand face: reverse, because
					// MakeFace expects inner boundaries to be added as bounded
					// areas.
					wires.back().Reverse();
				}
			}
		}

		if (num_wires > 1 && shape_index != 0) {
			// The first operand can have inner wires, but the others
			// can't because a inner wire would result in an additional
			// outer wire for the result.
			return false;
		}

		shapes.push_back(it.Value());
		TopExp_Explorer exp(it.Value(), TopAbs_EDGE);
		for (; exp.More(); exp.Next(), ++edge_index) {
			edge_tree.add(edge_index, exp.Current());
			edge_index_to_shape_index[edge_index] = shape_index;
			edges.push_back({ shape_index, TopoDS::Edge(exp.Current()) });
		}
	}

	shape_index = 0;
	edge_index = 0;

	it.Initialize(ab_input);
	for (; it.More(); it.Next(), ++shape_index) {
		TopExp_Explorer exp(it.Value(), TopAbs_EDGE);
		for (; exp.More(); exp.Next(), ++edge_index) {
			Bnd_Box b;
			BRepBndLib::Add(exp.Current(), b);
			b.Enlarge(eps);

			for (auto& i : edge_tree.select_box(b)) {
				if (i == edge_index) {
					// Skip self-selection
					continue;
				}

				if (edges[i].first == shape_index) {
					// Skip edges of the same operand
					continue;
				}

				const TopoDS_Edge& e0 = TopoDS::Edge(exp.Current());
				const TopoDS_Edge& e1 = edges[i].second;

				double u11, u12, u21, u22, U1, U2;

				GeomAPI_ExtremaCurveCurve ecc(
					BRep_Tool::Curve(e0, u11, u12),
					BRep_Tool::Curve(e1, u21, u22)
				);

				if (!ecc.Extrema().IsParallel() && ecc.NbExtrema() == 1) {
					// @todo: extend this to work in case of multiple extrema and curved segments.
					gp_Pnt p1, p2;
					ecc.Points(1, p1, p2);

					// #3616 Only take into account orthogonal distance between closest points on curve
					// to see whether inside tolerance. Current DY is hardcoded. The sensible default
					// for walls.
					gp_Vec vec(p1, p2);
					Standard_Real d = vec.Dot(gp::DY());
					gp_Vec projected = d * gp::DY();
					gp_Vec ortho_remainder = vec - projected;
					Standard_Real ortho_distance = ortho_remainder.Magnitude();

					const bool unbounded_intersects = ortho_distance < eps;
					if (unbounded_intersects) {
						ecc.Parameters(1, U1, U2);

						if (u11 > u12) {
							std::swap(u11, u12);
						}
						if (u21 > u22) {
							std::swap(u21, u22);
						}

						/// @todo: tfk: probably need different thresholds on non-linear curves
						u11 -= eps;
						u12 += eps;
						u21 -= eps;
						u22 += eps;

						if (u11 < U1 && U1 < u12 && u21 < U2 && U2 < u22) {
							// Edge curves belonging to different operands intersect, don't process
							// using builder.
							Logger::Notice("Intersecting boundaries");
							return false;
						}
					}
				}
			}
		}
	}

	// Only inner wires are considered that are directly contained in the outer wire
	// Redundant subtractions are eliminated.

	std::vector<bool> redundant(wires.size(), false);

	std::vector<TopoDS_Face> wire_faces;
	wire_faces.reserve(wires.size());

	std::vector<BRepTopAdaptor_FClass2d> wire_clss;
	wire_clss.reserve(wires.size());

	std::vector<std::unique_ptr<ShapeAnalysis_Surface>> sass;
	sass.reserve(wires.size());

	for (auto& w : wires) {
		wire_faces.push_back(BRepBuilderAPI_MakeFace(w).Face());
		wire_clss.emplace_back(wire_faces.back(), eps);
		sass.push_back(std::make_unique<ShapeAnalysis_Surface>(BRep_Tool::Surface(wire_faces.back())));
	}

	// First check for containment in outer wire
	for (auto it = ++wires.begin(); it != wires.end(); ++it) {
		// Considering a single vertex is sufficient because we have already
		// guaranteed that the edges of different operands do not cross.
		TopoDS_Iterator it_ed(*it);
		auto& ed = it_ed.Value();

		TopoDS_Iterator it_v(ed);
		auto& v = TopoDS::Vertex(it_v.Value());

		auto pnt = BRep_Tool::Pnt(v);
		auto p2d = sass[0]->ValueOfUV(pnt, eps);
		if (wire_clss[0].Perform(p2d) != TopAbs_IN) {
			// A wire is not contained in the outer wire, it's a subtraction without
			// any effect and marked as redundant. Feeding it to the builder algo
			// will likely cause problems.
			redundant[std::distance(wires.begin(), it)] = true;
			Logger::Notice("Subtraction operand outside of outer bound");
		}
	}

	// Now build a tree to find inner wires contained in other inner wires
	// NB first wire is *not* in this tree
	IfcGeom::impl::tree<int> wire_tree;
	for (size_t wire_index = 1; wire_index < wires.size(); ++wire_index) {
		wire_tree.add(wire_index, wires[wire_index]);
	}

	for (size_t wire_index = 1; wire_index < wires.size(); ++wire_index) {
		Bnd_Box b;
		BRepBndLib::Add(wires[wire_index], b);
		b.Enlarge(eps);

		// We're only selecting operands completely within b because we
		// have already guaranteed they do not intersect. So they are
		// either fully in or out. Selecting with complete_within=true
		// will filter out some unnecessary cases. It also means we need
		// that due this asymmetry we need to process all pairs of wire
		// indices and not just the pairs where the first element is less
		// than the second element.
		for (auto& other_index : wire_tree.select_box(b, true)) {
			// other_index is fully contained in wire_index
			if (wire_index == other_index) {
				continue;
			}

			TopoDS_Iterator it_ed(wires[other_index]);
			auto& ed = it_ed.Value();

			TopoDS_Iterator it_v(ed);
			auto& v = TopoDS::Vertex(it_v.Value());

			auto pnt = BRep_Tool::Pnt(v);
			auto p2d = sass[wire_index]->ValueOfUV(pnt, eps);
			if (wire_clss[wire_index].Perform(p2d) == TopAbs_IN) {
				// A wire is contained within another operand
				redundant[other_index] = true;
				Logger::Notice("Subtraction operand contained in other");
			}
		}
	}

	BRepBuilderAPI_MakeFace mf(wire_faces[0]);
	for (size_t wire_index = 1; wire_index < wires.size(); ++wire_index) {
		if (!redundant[wire_index]) {
			mf.Add(TopoDS::Wire(wires[wire_index].Reversed()));
		}
	}
	result = mf.Face();

	return true;
}

void IfcGeom::util::points_on_planar_face_generator::reset() {
	i = j = (int)inset_;
}

bool IfcGeom::util::points_on_planar_face_generator::operator()(gp_Pnt& p) {
	while (j < N) {
		double u = u0 + (u1 - u0) * i / N;
		double v = v0 + (v1 - v0) * j / N;

		i++;
		if (i == N) {
			i = 0;
			j++;
		}

		// Specifically does not consider ON
		if (cls_.Perform(gp_Pnt2d(u, v)) == TopAbs_IN) {
			plane_->D0(u, v, p);
			return true;
		}
	}

	return false;
}


bool IfcGeom::util::boolean_operation(const boolean_settings& settings, const TopoDS_Shape& a_input, const TopTools_ListOfShape& b_input, BOPAlgo_Operation op, TopoDS_Shape& result, double fuzziness) {
	using namespace std::string_literals;

	const bool do_unify = true;
	const bool do_subtraction_eliminate_disjoint_bbox = true;
	const bool do_subtraction_eliminate_touching = true;
	const bool do_eliminate_narrow_obb = true;
	const bool do_attempt_2d_boolean = settings.attempt_2d;
	const bool debug = settings.debug;

	std::string debug_identifier;
	if (debug) {
		static my_thread_local size_t operation_counter_ = 0;
		std::stringstream ss;
		ss << "bool-" << std::this_thread::get_id() << "-" << (operation_counter_++);
		debug_identifier = ss.str();
		Logger::Notice("Boolean debug identifier: " + debug_identifier);
	}

	if (fuzziness < 0.) {
		fuzziness = settings.precision / 100.;
	}

	/*
	{
		TopoDS_Compound C;
		BRep_Builder BB;
		BB.MakeCompound(C);

		BB.Add(C, a_input);

		TopTools_ListIteratorOfListOfShape it(b_input);
		for (; it.More(); it.Next()) {
			BB.Add(C, it.Value());
		}

		result = C;
	}

	return true;
	*/

	// @todo, it does seem a bit odd, we first triangulate non-planar faces
	// to later unify them again. Can we make this a bit more intelligent?
	TopoDS_Shape a;
	TopTools_ListOfShape b;

	if (do_unify) {
		PERF("boolean operation: unifying operands");

		a = unify(a_input, fuzziness * 1000.);

		Logger::Message(
			Logger::LOG_DEBUG,
			"Simplified operand A from "s +
			std::to_string(count(a_input, TopAbs_FACE)) +
			" to "s +
			std::to_string(count(a, TopAbs_FACE))
		);

		{
			TopTools_ListIteratorOfListOfShape it(b_input);
			for (; it.More(); it.Next()) {
				b.Append(unify(it.Value(), fuzziness));
				Logger::Message(
					Logger::LOG_DEBUG,
					"Simplified operand B from "s +
					std::to_string(count(it.Value(), TopAbs_FACE)) +
					" to "s +
					std::to_string(count(b.Last(), TopAbs_FACE))
				);
			}
		}
	} else {
		a = a_input;
		b = b_input;
	}

	bool is_2d = count(a, TopAbs_FACE) > 0 && count(a, TopAbs_SHELL) == 0;

	bool success = false;
	BRepAlgoAPI_BooleanOperation* builder;
	TopTools_ListOfShape b_tmp;

	if (op == BOPAlgo_CUT) {
		builder = new BRepAlgoAPI_Cut();

		if (do_subtraction_eliminate_disjoint_bbox) {
			PERF("boolean subtraction: eliminate disjoint bbox");

			auto N = bounding_box_overlap(fuzziness, a, b, b_tmp);
			if (N) {
				Logger::Notice("Eliminated " + std::to_string(N) + " disjoint operands");
				std::swap(b, b_tmp);
			}
		}

		if (!is_2d && do_subtraction_eliminate_touching) {
			PERF("boolean subtraction: eliminate touching");

			b_tmp.Clear();
			auto N = eliminate_touching_operands(fuzziness, a, b, b_tmp);
			if (N) {
				Logger::Notice("Eliminated " + std::to_string(N) + " touching operands");
				std::swap(b, b_tmp);
			}
		}

		if (!is_2d && do_eliminate_narrow_obb) {
			PERF("boolean subtraction: eliminate narrow");

			b_tmp.Clear();
			auto N = eliminate_narrow_operands(fuzziness, b, b_tmp);
			if (N) {
				Logger::Notice("Eliminated " + std::to_string(N) + " narrow operands");
				std::swap(b, b_tmp);
			}
		}

	} else if (op == BOPAlgo_COMMON) {
		builder = new BRepAlgoAPI_Common();
	} else if (op == BOPAlgo_FUSE) {
		builder = new BRepAlgoAPI_Fuse();
	} else {
		return false;
	}

	if (b.Extent() == 0) {
		Logger::Warning("No other operands remaining, using first operand");
		result = a;
		return true;
	}

	if (Logger::LOG_NOTICE >= Logger::Verbosity()) {
		PERF("preliminary manifoldness check");

		if (!a.IsNull()) {
			Logger::Notice("Operand A is " + (is_manifold(a) ? ""s : "non-"s) + "manifold");
		}

		TopTools_ListIteratorOfListOfShape it(b);
		for (int i = 0; it.More(); it.Next(), ++i) {
			Logger::Notice("Operand B " + std::to_string(i) + " is " + (is_manifold(it.Value()) ? ""s : "non-"s) + "manifold");
		}
	}

	// Find a sensible value for the fuzziness, based on precision
	// and limited by edge lengths and vertex-edge distances.
	double min_length_orig;

	{
		PERF("boolean operation: min edge length");

		min_length_orig = min_edge_length(a);
		TopTools_ListIteratorOfListOfShape it(b);
		for (; it.More(); it.Next()) {
			double d = min_edge_length(it.Value());
			if (d < min_length_orig) {
				min_length_orig = d;
			}
		}
	}

	{
		PERF("boolean operation: min vertex-edge dist");

		double d = min_vertex_edge_distance(a, settings.precision, min_length_orig);
		if (d < min_length_orig) {
			min_length_orig = d;
		}

		TopTools_ListIteratorOfListOfShape it(b);
		for (; it.More(); it.Next()) {
			d = min_vertex_edge_distance(it.Value(), settings.precision, min_length_orig);
			if (d < min_length_orig) {
				min_length_orig = d;
			}
		}
	}

	const double fuzz = (std::min)(min_length_orig / 3., fuzziness);

	Logger::Notice("Used fuzziness: " + std::to_string(fuzz));

	TopTools_ListOfShape s1s;
	s1s.Append(copy_operand(a));

	if (debug) {
		TopTools_ListOfShape* lists[2] = { &s1s, &b };
		static std::string operand_names[2] = { "a", "b" };
		for (int i = 0; i < 2; ++i) {
			TopTools_ListIteratorOfListOfShape it(*lists[i]);
			for (int j = 0; it.More(); it.Next(), ++j) {
				std::string fn = debug_identifier + "-" + operand_names[i] + "-" + std::to_string(j) + ".brep";
				BRepTools::Write(it.Value(), fn.c_str());
			}
		}
	}

	if (op == BOPAlgo_CUT) {
		TopoDS_Face a_face;
		std::pair<double, double> a_interval;

		TopTools_ListOfShape b_faces, b_remainder_3d;

		bool is_extrusion_a = false;
		if (do_attempt_2d_boolean) {
			PERF("boolean subtraction: extrusion check");

			is_extrusion_a = is_extrusion(gp::DY(), a, a_face, a_interval);
		}

		if (is_extrusion_a) {
			Logger::Notice("Operand A 1/1 is an extrusion");

			TopTools_ListIteratorOfListOfShape it(b);
			for (int nb = 1; it.More(); it.Next(), ++nb) {
				bool process_2d = false;
				TopoDS_Face b_face;
				std::pair<double, double> b_interval;

				bool is_extrusion_b;
				{
					PERF("boolean subtraction: extrusion check");

					is_extrusion_b = is_extrusion(gp::DY(), it.Value(), b_face, b_interval);
				}

				if (is_extrusion_b) {
					Logger::Notice("Operand B " + std::to_string(nb) + "/" + std::to_string(b.Extent()) + " is an extrusion");

					if (b_interval.first < a_interval.first + fuzz && b_interval.second > a_interval.second - fuzz) {
						Logger::Notice("Operand B creates a through hole");

						// Align b with a operand
						gp_Trsf trsf;
						trsf.SetTranslation(gp_Vec(gp::DY()) * (a_interval.first - b_interval.first));

						b_faces.Append(b_face.Moved(trsf));
						process_2d = true;
					}
				}

				if (!process_2d) {
					b_remainder_3d.Append(it.Value());
				}
			}

			if (b_faces.Extent()) {
				TopoDS_Shape face_result;

				bool boolean_op_2d_success;
				{
					PERF("boolean operation: 2d builder");
					// First try using face builder

					boolean_op_2d_success = boolean_subtraction_2d_using_builder(a_face, b_faces, face_result, fuzziness);
				}

				if (!boolean_op_2d_success) {
					PERF("boolean operation: 2d");
					// Retry using generic 2d using boolean algo on faces

					boolean_op_2d_success = boolean_operation(settings, a_face, b_faces, op, face_result, fuzziness);
				}

				if (boolean_op_2d_success) {
					PERF("boolean operation: 2d to 3d");

					BRepPrimAPI_MakePrism mp(face_result, gp_Vec(gp::DY()) * (a_interval.second - a_interval.first));
					if (mp.IsDone()) {
						if (b_remainder_3d.Extent()) {
							Logger::Notice(std::to_string(b_remainder_3d.Extent()) + " operands remaining to process in 3D");
							b = b_remainder_3d;
							s1s.Clear();
							s1s.Append(mp.Shape());
						} else {
							Logger::Notice("Processed fully in 2D");
							result = mp.Shape();
							return true;
						}
					} else {
						Logger::Notice("Failed to extrude 2D boolean result. Retrying in 3D.");
					}
				} else {
					Logger::Notice("Failed to perform 2D boolean operation. Retrying in 3D.");
				}
			} else {
				Logger::Notice("No second operands can be processed as 2D inner bounds. Retrying in 3D.");
			}
		}
	}

#if OCC_VERSION_HEX >= 0x70000
	builder->SetNonDestructive(true);
#endif
	builder->SetFuzzyValue(fuzz);
	builder->SetArguments(s1s);
	copy_operand(b, b_tmp);
	std::swap(b, b_tmp);
	builder->SetTools(b);
	{
		PERF("boolean operation: build");

		builder->Build();
	}
	if (builder->IsDone()) {
		if (builder->DSFiller()->HasWarning(STANDARD_TYPE(BOPAlgo_AlertAcquiredSelfIntersection))) {
			Logger::Notice("Builder reports self-intersection in output");
			success = false;
		} else if(builder->DSFiller()->HasWarning(STANDARD_TYPE(BOPAlgo_AlertBadPositioning)) && !TopoDS_Iterator(*builder).More()) {
			Logger::Notice("Builder reports bad positioning and result is empty");
			success = false;
		} else {
			TopoDS_Shape r = *builder;

			{
				PERF("boolean operation: shape healing");

				ShapeFix_Shape fix(r);
				try {
					fix.SetMaxTolerance(fuzz);
					fix.Perform();
					r = fix.Shape();
				} catch (...) {
					Logger::Error("Shape healing failed on boolean result");
				}
			}

			{
				PERF("boolean operation: shape analysis");

				BRepCheck_Analyzer ana(r);
				success = ana.IsValid() != 0;

				if (!success) {
					Logger::Notice("Boolean operation yields invalid result");

					std::stringstream str;
					bool any_emitted = false;

					std::function<void(const TopoDS_Shape&)> dump;
					dump = [&ana, &str, &dump, &any_emitted](const TopoDS_Shape& s) {
						if (!ana.Result(s).IsNull()) {
							BRepCheck_ListIteratorOfListOfStatus itl;
							itl.Initialize(ana.Result(s)->Status());
							for (; itl.More(); itl.Next()) {
								if (itl.Value() != BRepCheck_NoError) {
									if (any_emitted) {
										str << ", ";
									}
									BRepCheck::Print(itl.Value(), str);
									str.seekp(str.tellp() - (std::streamoff)1);
									str << " on ";
									TopAbs::Print(s.ShapeType(), str);
									any_emitted = true;
								}
							}
						}
						for (TopoDS_Iterator it(s); it.More(); it.Next()) {
							dump(it.Value());
						}
					};

					dump(r);

					Logger::Notice(str.str());
				}
			}

			if (success) {

				{
					PERF("boolean operation: manifoldness check");

					success = !is_manifold(a) || is_manifold(r);
				}

				if (!success) {
					PERF("boolean operation: manifoldness check exemption");

					// An exemption for the requirement to be manifold: When the cut operands have overlapping edge belonging to faces that do not overlap.
					bool operands_nonmanifold = false;
					if (op == BOPAlgo_CUT) {
						TopTools_IndexedMapOfShape edges;
						TopTools_IndexedDataMapOfShapeListOfShape map;
						for (TopTools_ListIteratorOfListOfShape it2(b); it2.More(); it2.Next()) {
							auto& bb = it2.Value();
							TopExp::MapShapes(bb, TopAbs_EDGE, edges);
							TopExp::MapShapesAndAncestors(bb, TopAbs_EDGE, TopAbs_FACE, map);
						}
						IfcGeom::impl::tree<int> tree;
						for (int i = 1; i <= edges.Extent(); ++i) {
							tree.add(i, edges.FindKey(i));
						}
						for (int i = 1; i <= edges.Extent(); ++i) {
							const TopoDS_Edge& ei = TopoDS::Edge(edges.FindKey(i));
							Bnd_Box bb;
							BRepBndLib::Add(ei, bb);
							bb.Enlarge(fuzziness);
							auto ii = tree.select_box(bb, false);
							for (int j : ii) {
								if (j != i) {
									const TopoDS_Edge& ej = TopoDS::Edge(edges.FindKey(j));
									ShapeAnalysis_Edge sae;
									double f = fuzziness;
									bool edges_overlapping = sae.CheckOverlapping(ei, ej, f, 0.) ||
										sae.CheckOverlapping(ej, ei, f, 0.);

									if (edges_overlapping) {
										auto faces_i = map.FindFromKey(edges.FindKey(i));
										auto faces_j = map.FindFromKey(edges.FindKey(j));
										bool overlap = false;
										for (TopTools_ListIteratorOfListOfShape it4(faces_i); it4.More(); it4.Next()) {
											auto& fi = it4.Value();
											for (TopTools_ListIteratorOfListOfShape it2(faces_j); it2.More(); it2.Next()) {
												auto& fj = it2.Value();
												if (faces_overlap(TopoDS::Face(fi), TopoDS::Face(fj))) {
													overlap = true;
												}
											}
											if (overlap) {
												break;
											}
										}
										operands_nonmanifold = !overlap;
										break;
									}
								}
							}
							if (operands_nonmanifold) {
								break;
							}
						}
					}
					success = operands_nonmanifold;
				}

				if (success) {

					bool all_faces_included_in_result = true;
					bool has_open_shells = false;

					if (op == BOPAlgo_CUT) {
						PERF("boolean operation: open shell face addition check");

						for (TopExp_Explorer exp(a, TopAbs_SHELL); exp.More(); exp.Next()) {
							if (!exp.Current().Closed()) {
								// This 'face addition check' is only done when the first operand
								// contains open shells (which was initially the aim of this check
								// see #1472).
								// Later in #1914 we found that the logic to apply openings in groups
								// of similar edge lengths can create a situation of inner voids, which
								// trigger a false positive in this check. This could have also been
								// solved below by checking whether the opening(s) are included as a
								// unmodified (interior) shell within a solid of multiple shells.
								// Checking for open shells in first operand was quicker and more
								// straightforward. The question still is whether in cases like #1472
								// we need to first try the boolean union as solid/solid interference
								// to trigger this case or whether we can immediately proceed to a face/
								// solid operation.
								has_open_shells = true;
								break;
							}
						}

						if (has_open_shells) {
							TopTools_IndexedMapOfShape faces;
							TopExp::MapShapes(r, TopAbs_FACE, faces);
							for (TopExp_Explorer exp(a, TopAbs_FACE); exp.More(); exp.Next()) {
								auto& f = TopoDS::Face(exp.Current());
								if (!faces.Contains(f)) {
									all_faces_included_in_result = false;
									break;
								}
							}
						} else {
							all_faces_included_in_result = false;
						}
					}

					int result_n_faces = count(r, TopAbs_FACE);
					int first_op_n_faces = count(a, TopAbs_FACE);

					if (op == BOPAlgo_CUT && has_open_shells && all_faces_included_in_result && result_n_faces > first_op_n_faces) {
						success = false;
						Logger::Notice("Boolean result discarded because subtractions results in only the addition of faces");
					} else {
						// when there are edges or vertex-edge distances close to the used fuzziness, the
						// output is not trusted and the operation is attempted with a higher fuzziness.
						int reason = 0;
						double v;

						{
							PERF("boolean operation: result min edge length check");

							if ((v = min_edge_length(r)) < fuzziness * 3.) {
								reason = 0;
								success = false;

								goto skip_further_checks;
							}
						}

						{
							PERF("boolean operation: result min vertex-edge dist check");

							if ((v = min_vertex_edge_distance(r, settings.precision, fuzziness * 3.)) < fuzziness * 3.) {
								reason = 1;
								success = false;

								goto skip_further_checks;
							}
						}

						{
							PERF("boolean operation: result min face-face dist check");

							if ((v = min_face_face_distance(r, 1.e-4)) < 1.e-4) {
								// #2095 Check if this distance wasn't already realized in the input first operand.
								if (v < min_face_face_distance(a, 1.e-4)) {
									reason = 2;
									success = false;
								}
							}
						}

					skip_further_checks:
						if (!success) {
							static const char* const reason_strings[] = { "edge length", "vertex-edge", "face-face" };
							std::stringstream str;
							str << "Boolean operation result failing " << reason_strings[reason] << " interference check, with fuzziness " << fuzziness << " with length " << v;
							Logger::Notice(str.str());
						}
					}

					if (success) {
						result = r;
					}

				} else {
					Logger::Notice("Boolean operation yields non-manifold result");
				}
			}
		}
	} else {
		std::stringstream str;

#if OCC_VERSION_HEX >= 0x70200

		if (builder->HasError(STANDARD_TYPE(BOPAlgo_AlertBOPNotAllowed))) {
			Logger::Error("Invalid operands. Using first operand");
			result = a;
			success = true;
		}
#endif

#if OCC_VERSION_HEX >= 0x70000
		builder->DumpErrors(str);
#else
		str << "Error code: " << builder->ErrorStatus();
#endif
		std::string str_str = str.str();
		if (str_str.size()) {
			Logger::Notice(str_str);
		}
	}
	delete builder;
	if (!success) {
		const double new_fuzziness = fuzziness * 10.;
		if (new_fuzziness - 1e-15 <= settings.precision * 10000. && new_fuzziness < min_length_orig) {
			return boolean_operation(settings, a, b, op, result, new_fuzziness);
		} else {
			Logger::Notice("No longer attempting boolean operation with higher fuzziness");
		}
	}
	return success && !result.IsNull();
}

bool IfcGeom::util::boolean_operation(const boolean_settings& settings, const TopoDS_Shape& a, const TopoDS_Shape& b, BOPAlgo_Operation op, TopoDS_Shape& result, double fuzziness) {
	TopTools_ListOfShape bs;
	bs.Append(b);
	return boolean_operation(settings, a, bs, op, result, fuzziness);
}

TopoDS_Shape IfcGeom::util::ensure_fit_for_subtraction(const TopoDS_Shape& shape, double tol) {
	const bool is_comp = is_compound(shape);
	if (!is_comp) {
		return shape;
	}

	TopoDS_Solid solid;
	if (!create_solid_from_compound(shape, solid, tol)) {
		return shape;
	}

	return solid;
}
