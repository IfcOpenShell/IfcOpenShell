#include "boolean_utils.h"

#include "../ifcgeom_schema_agnostic/IfcGeomTree.h"

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

#include <vector>

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
		for (int i = 1; i <= b_faces.Extent(); ++i) {
			auto surf = BRep_Tool::Surface(TopoDS::Face(b_faces(i)));
			if (surf->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
				continue;
			}
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

				// @todo: extend this to work in case of multiple extrema and curved segments.
				const bool unbounded_intersects = (!ecc.Extrema().IsParallel() && ecc.NbExtrema() == 1 && ecc.Distance(1) < eps);
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