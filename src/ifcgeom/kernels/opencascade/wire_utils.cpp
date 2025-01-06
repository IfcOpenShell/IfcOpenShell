#include "wire_utils.h"

#include "../../../ifcparse/IfcLogger.h"
#include "../../../ifcgeom/ConversionSettings.h"

#include "base_utils.h"
#include "boolean_utils.h"
#include "IfcGeomTree.h"

#include <TopExp.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Iterator.hxx>
#include <ShapeFix_Wire.hxx>
#include <BRep_Tool.hxx>
#include <BRepTools_WireExplorer.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepAlgo_NormalProjection.hxx>
#include <BRepMesh_IncrementalMesh.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <TopTools_ListOfShape.hxx>
#include <ShapeExtend_WireData.hxx>
#include <Standard_Version.hxx>
#include <GeomAPI_ExtremaCurveCurve.hxx>
#include <BRepOffsetAPI_Sewing.hxx>
#include <ShapeFix_Solid.hxx>
#include <ShapeFix_ShapeTolerance.hxx>

#include <boost/range/irange.hpp>
#include <boost/range/algorithm_ext/push_back.hpp>

#include <map>

bool IfcGeom::util::approximate_plane_through_wire(const TopoDS_Wire& wire, gp_Pln& plane, double eps_) {
	// Newell's Method is used for the normal calculation
	// as a simple edge cross product can give opposite results
	// for a concave face boundary.
	// Reference: Graphics Gems III p. 231

	const double eps2 = eps_ * eps_;

	double x = 0, y = 0, z = 0;
	gp_Pnt current, previous, first;
	gp_XYZ center;
	int n = 0;

	BRepTools_WireExplorer exp(wire);

	for (;; exp.Next()) {
		const bool has_more = exp.More() != 0;
		if (has_more) {
			const TopoDS_Vertex& v = exp.CurrentVertex();
			current = BRep_Tool::Pnt(v);
			center += current.XYZ();
		} else {
			current = first;
		}
		if (n) {
			const double& xn = previous.X();
			const double& yn = previous.Y();
			const double& zn = previous.Z();
			const double& xn1 = current.X();
			const double& yn1 = current.Y();
			const double& zn1 = current.Z();
			x += (yn - yn1)*(zn + zn1);
			y += (xn + xn1)*(zn - zn1);
			z += (xn - xn1)*(yn + yn1);
		} else {
			first = current;
		}
		if (!has_more) {
			break;
		}
		previous = current;
		++n;
	}

	if (n < 3) {
		return false;
	}

	gp_Vec v(x, y, z);
	// @todo the epsilon passed to us here is the maximum allowed deviation of
	// the given points to the constructed plane. When doing triangulation and
	// obtaining a 2d points for the Delaunay, infinity is passed here, so this
	// can't for assessing degenerativeness.
	if (v.Magnitude() < 1.e-7) {
		Logger::Warning("Degenerate face boundary in normal estimation");
		return false;
	}

	plane = gp_Pln(center / n, v);

	exp.Init(wire);
	for (; exp.More(); exp.Next()) {
		const TopoDS_Vertex& vrt = exp.CurrentVertex();
		current = BRep_Tool::Pnt(vrt);
		if (plane.SquareDistance(current) > eps2) {
			return false;
		}
	}

	return true;
}

bool IfcGeom::util::flatten_wire(TopoDS_Wire& wire, double eps) {
	gp_Pln pln;
	if (!approximate_plane_through_wire(wire, pln, eps)) {
		return false;
	}
	TopoDS_Face face = BRepBuilderAPI_MakeFace(pln).Face();
	BRepAlgo_NormalProjection proj(face);
	proj.Add(wire);
	proj.Build();
	if (!proj.IsDone()) {
		return false;
	}
	TopTools_ListOfShape list;
	proj.BuildWire(list);
	if (list.Extent() != 1) {
		return false;
	}
	wire = TopoDS::Wire(list.First());
	return true;
}

IfcGeom::util::triangulate_wire_result IfcGeom::util::triangulate_wire(const std::vector<TopoDS_Wire>& wires, TopTools_ListOfShape& faces) {
	// This is a bit of a precarious approach, but seems to work for the
	// versions of OCCT tested for. OCCT has a Delaunay triangulation function
	// BRepMesh_Delaun, but it is notoriously hard to interpret the results
	// (due to the Bowyer-Watson super triangle perhaps?). Therefore
	// alternatively we use the regular OCCT incremental mesher on a new face
	// created from the UV coordinates of the original wire. Pray to our gods
	// that the vertex coordinates are unaffected by the meshing algorithm and
	// map them back to 3d coordinates when iterating over the mesh triangles.

	// In addition, to maintain a manifold shell, we need to make sure that
	// every edge from the input wire is used exactly once in the list of
	// resulting faces. And that other internal edges are used twice.

	typedef std::pair<double, double> uv_node;

	gp_Pln pln;
	if (!approximate_plane_through_wire(wires.front(), pln, std::numeric_limits<double>::infinity())) {
		return TRIANGULATE_WIRE_FAIL;
	}

	const gp_XYZ& udir = pln.Position().XDirection().XYZ();
	const gp_XYZ& vdir = pln.Position().YDirection().XYZ();
	const gp_XYZ& pnt = pln.Position().Location().XYZ();

	std::map<uv_node, TopoDS_Vertex> mapping;
	std::map<std::pair<uv_node, uv_node>, TopoDS_Edge> existing_edges, new_edges;

	std::unique_ptr<BRepBuilderAPI_MakeFace> mf;

	for (auto it = wires.begin(); it != wires.end(); ++it) {
		const TopoDS_Wire& wire = *it;
		BRepTools_WireExplorer exp(wire);
		BRepBuilderAPI_MakePolygon mp;

		// Add UV coordinates to a newly created polygon
		for (; exp.More(); exp.Next()) {
			// Project onto plane
			const TopoDS_Vertex& V = exp.CurrentVertex();
			gp_Pnt p = BRep_Tool::Pnt(V);
			double u = (p.XYZ() - pnt).Dot(udir);
			double v = (p.XYZ() - pnt).Dot(vdir);
			mp.Add(gp_Pnt(u, v, 0.));

			mapping.insert(std::make_pair(std::make_pair(u, v), V));

			// Store existing edges in a map so that triangles can
			// actually reference the preexisting edges.
			const TopoDS_Edge& e = exp.Current();
			TopoDS_Vertex V0, V1;
			TopExp::Vertices(e, V0, V1, true);
			gp_Pnt p0 = BRep_Tool::Pnt(V0);
			gp_Pnt p1 = BRep_Tool::Pnt(V1);
			double u0 = (p0.XYZ() - pnt).Dot(udir);
			double v0 = (p0.XYZ() - pnt).Dot(vdir);
			double u1 = (p1.XYZ() - pnt).Dot(udir);
			double v1 = (p1.XYZ() - pnt).Dot(vdir);
			uv_node uv0 = std::make_pair(u0, v0);
			uv_node uv1 = std::make_pair(u1, v1);
			existing_edges.insert(std::make_pair(std::make_pair(uv0, uv1), e));
			existing_edges.insert(std::make_pair(std::make_pair(uv1, uv0), TopoDS::Edge(e.Reversed())));
		}

		// Not closed by default
		mp.Close();

		if (mf) {
			if (it - 1 == wires.begin()) {
				// @todo is this necessary?
				TopoDS_Face f = mf->Face();
				mf->Init(f);
			}
			mf->Add(mp.Wire());
		} else {
			mf.reset(new BRepBuilderAPI_MakeFace(mp.Wire()));
		}
	}

	const TopoDS_Face& face = mf->Face();

	// Create a triangular mesh from the face
	BRepMesh_IncrementalMesh(face, Precision::Confusion());

	int n123[3];
	TopLoc_Location loc;
	Handle_Poly_Triangulation tri = BRep_Tool::Triangulation(face, loc);

	if (!tri.IsNull()) {

		const Poly_Array1OfTriangle& triangles = tri->Triangles();
		for (int i = 1; i <= triangles.Length(); ++i) {
			if (face.Orientation() == TopAbs_REVERSED)
				triangles(i).Get(n123[2], n123[1], n123[0]);
			else triangles(i).Get(n123[0], n123[1], n123[2]);

			// Create polygons from the mesh vertices
			BRepBuilderAPI_MakeWire mp2;
			for (int j = 0; j < 3; ++j) {

				uv_node uvnodes[2];
				TopoDS_Vertex vs[2];

				for (int k = 0; k < 2; ++k) {
					const gp_Pnt& uv = tri->Node(n123[(j + k) % 3]);
					uvnodes[k] = std::make_pair(uv.X(), uv.Y());

					auto it = mapping.find(uvnodes[k]);
					if (it == mapping.end()) {
						Logger::Error("Internal error: unable to unproject uv-mesh");
						return TRIANGULATE_WIRE_FAIL;
					}

					vs[k] = it->second;
				}

				auto it = existing_edges.find(std::make_pair(uvnodes[0], uvnodes[1]));
				if (it != existing_edges.end()) {
					// This is a boundary edge, reuse existing edge from wire
					mp2.Add(it->second);
				} else {
					auto jt = new_edges.find(std::make_pair(uvnodes[0], uvnodes[1]));
					if (jt != new_edges.end()) {
						// We have already added the reverse as part of another
						// triangle, reuse this edge.
						mp2.Add(TopoDS::Edge(jt->second));
					} else {
						// This is a new internal edge. Register the reverse
						// for reuse later. We need to be sure to reuse vertices
						// for the edge construction because otherwise the wire
						// builder will use geometrical proximity for vertex
						// connections in which case the edge will be copied
						// and no longer partner with other edges from the shell.
						TopoDS_Edge ne = BRepBuilderAPI_MakeEdge(vs[0], vs[1]);
						mp2.Add(ne);
						// Store the reverse to be picked up later.
						new_edges.insert(std::make_pair(std::make_pair(uvnodes[1], uvnodes[0]), TopoDS::Edge(ne.Reversed())));
					}
				}
			}

			BRepBuilderAPI_MakeFace mft(mp2.Wire());
			if (mft.IsDone()) {
				TopoDS_Face triangle_face = mft.Face();
				TopoDS_Iterator jt(triangle_face, false);
				for (; jt.More(); jt.Next()) {
					const TopoDS_Wire& w = TopoDS::Wire(jt.Value());
					if (w.Orientation() != wires.front().Orientation()) {
						triangle_face.Reverse();
					}
				}
				faces.Append(triangle_face);
			} else {
				Logger::Error("Internal error: missing face");
				return TRIANGULATE_WIRE_FAIL;
			}
		}
	}

	TopTools_IndexedDataMapOfShapeListOfShape mape, mapn;
	for (auto& wire : wires) {
		TopExp::MapShapesAndAncestors(wire, TopAbs_EDGE, TopAbs_WIRE, mape);
	}
	TopTools_ListIteratorOfListOfShape it(faces);
	for (; it.More(); it.Next()) {
		TopExp::MapShapesAndAncestors(it.Value(), TopAbs_EDGE, TopAbs_WIRE, mapn);
	}

	// Validation
	bool non_manifold = false;

	for (int i = 1; i <= mape.Extent(); ++i) {
#if OCC_VERSION_HEX >= 0x70000
		TopTools_ListOfShape val;
		if (!mapn.FindFromKey(mape.FindKey(i), val)) {
#else
		bool contains = false;
		try {
			TopTools_ListOfShape val = mapn.FindFromKey(mape.FindKey(i));
			contains = true;
		} catch (Standard_NoSuchObject&) {}
		if (!contains) {
#endif
			// All existing edges need to exist in the new faces
			Logger::Error("Internal error, missing edge from triangulation");
			non_manifold = true;
		}
		}

	for (int i = 1; i <= mapn.Extent(); ++i) {
		const TopoDS_Shape& v = mapn.FindKey(i);
		int n = mapn.FindFromIndex(i).Extent();
		// Existing edges are boundaries with use 1
		// New edges are internal with use 2
		if (n != (mape.Contains(v) ? 1 : 2)) {
			Logger::Error("Internal error, non-manifold result from triangulation");
			non_manifold = true;
		}
	}

	return non_manifold ? TRIANGULATE_WIRE_NON_MANIFOLD : TRIANGULATE_WIRE_OK;
}

namespace {

	/*
	 * A small helper utility to wrap around a numeric range
	*/
	class bounded_int {
	private:
		int i;
		size_t n;
	public:
		bounded_int(int i, size_t n) : i(i), n(n) {}

		bounded_int& operator--() {
			--i;
			if (i == -1) {
				i = (int)n - 1;
			}
			return *this;
		}

		bounded_int& operator++() {
			++i;
			if (i == (int)n) {
				i = 0;
			}
			return *this;
		}

		operator int() { return i; }
	};
}

namespace {
	double get_wire_intersection_tolerance(const IfcGeom::util::wire_tolerance_settings& settings, const TopoDS_Wire& wire) {
		if (settings.use_wire_intersection_tolerance) {
			// This corresponds to faceset_helper::epsilon
			if (settings.vertex_clustering_epsilon > 0.) {
				return settings.vertex_clustering_epsilon / 3.;
			} else {
				return (std::min)(IfcGeom::util::min_edge_length(wire) / 2., settings.precision * 10.);
			}
		} else {
			return 0.;
		}
	}
}

bool IfcGeom::util::wire_intersections(const TopoDS_Wire& wire, TopTools_ListOfShape& wires, const wire_tolerance_settings& settings) {
	double eps = get_wire_intersection_tolerance(settings, wire);
	double eps_real = settings.precision;
	
	if (!wire.Closed()) {
		wires.Append(wire);
		return false;
	}

	int n = util::count(wire, TopAbs_EDGE);
	if (n < 3) {
		wires.Append(wire);
		return false;
	}

	// Note: initialize empty
	Handle(ShapeExtend_WireData) wd = new ShapeExtend_WireData();

	// ... to be sure to get consecutive edges
	BRepTools_WireExplorer exp(wire);
	IfcGeom::impl::tree<int> tree;

	int edge_idx = 0;
	for (; exp.More(); exp.Next()) {
		wd->Add(exp.Current());
		if (n > 64) {
			// tfk: indices in tree are 0-based vd 1-based in wiredata
			tree.add(edge_idx++, exp.Current());
		}
	}

	if (wd->NbEdges() != n) {
		// If the number of edges differs, BRepTools_WireExplorer did not
		// reach every edge, probably due to loops exactly at vertex locations.
		// This is not supported by this algorithm which only elimates loops
		// due to edge crossings.

		throw geometry_exception("Invalid loop");
	}

	bool intersected = false;

	// tfk: Extrema on infinite curves proved to be more robust.
	// TopoDS_Face face = BRepBuilderAPI_MakeFace(wire, true).Face();
	// ShapeAnalysis_Wire saw(wd, face, getValue(GV_PRECISION));

	// @todo: should this start from 0 in case of n > 64?
	for (int i = 2; i < n; ++i) {

		std::vector<int> js;
		if (n > 64) {
			Bnd_Box b;
			BRepBndLib::Add(wd->Edge(i + 1), b);
			b.Enlarge(eps);
			js = tree.select_box(b, false);
		} else {
			boost::push_back(js, boost::irange(0, i - 1));
		}

		for (std::vector<int>::const_iterator it = js.begin(); it != js.end(); ++it) {
			int j = *it;

			if (n > 64) {
				if (j > i) {
					continue;
				}
				if ((std::max)(i, j) - (std::min)(i, j) <= 1) {
					continue;
				}
			}

			// Only check non-consecutive edges
			if (i == n - 1 && j == 0) continue;

			double u11, u12, u21, u22, U1, U2;
			GeomAPI_ExtremaCurveCurve ecc(
				BRep_Tool::Curve(wd->Edge(i + 1), u11, u12),
				BRep_Tool::Curve(wd->Edge(j + 1), u21, u22)
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

				// tfk: code below is for ShapeAnalysis_Wire::CheckIntersectingEdges()
				// IntRes2d_SequenceOfIntersectionPoint points2d;
				// TColgp_SequenceOfPnt points3d;
				// TColStd_SequenceOfReal errors;
				// if (saw.CheckIntersectingEdges(i + 1, j + 1, points2d, points3d, errors)) {

				if (u11 < U1 && U1 < u12 && u21 < U2 && U2 < u22) {

					intersected = true;

					// Explore a forward and backward cycle from the intersection point
					for (int fb = 0; fb <= 1; ++fb) {
						const bool forward = fb == 0;

						BRepBuilderAPI_MakeWire mw;
						bool first = true;

						for (bounded_int k(j, n);;) {
							bool intersecting = k == j || k == i;
							if (intersecting) {
								TopoDS_Edge e = wd->Edge(k + 1);

								TopoDS_Vertex v1, v2;
								TopExp::Vertices(e, v1, v2, true);
								const TopoDS_Vertex* v = first == forward ? &v2 : &v1;

								// gp_Pnt p2 = points3d.Value(1);

								gp_Pnt p1 = BRep_Tool::Pnt(*v);
								gp_Pnt pp1, pp2;
								ecc.Points(1, pp1, pp2);
								const gp_Pnt& p2 = k == i ? pp1 : pp2;

								// Substitute with a new edge from/to the intersection point
								if (p1.Distance(p2) > eps_real * 2) {
									double _, __;
									Handle_Geom_Curve crv = BRep_Tool::Curve(e, _, __);
									BRepBuilderAPI_MakeEdge me(crv, p1, p2);
									TopoDS_Edge ed = me.Edge();
									mw.Add(ed);
								}

								first = false;
							} else {
								// Re-use original edge
								mw.Add(wd->Edge(k + 1));
							}

							if (k == i) {
								break;
							}

							if (forward) {
								++k;
							} else {
								--k;
							}
						}

						ShapeFix_Wire sfw;
						sfw.Load(mw.Wire());
						sfw.Perform();

						// Recursively process both cuts

						// @todo this is a change in behaviour with eps precomputed from the kernel
						// instead of adaptively calculated for the successive iterations.
						wire_intersections(sfw.Wire(), wires, settings);
					}

					return true;
				}

			}
		}
	}

	// No intersections found, append original wire
	if (!intersected) {
		wires.Append(wire);
	}

	return intersected;
}

void IfcGeom::util::select_largest(const TopTools_ListOfShape& shapes, TopoDS_Shape& largest) {
	double mass = 0.;
	TopTools_ListIteratorOfListOfShape it(shapes);
	for (; it.More(); it.Next()) {
		/*
		// tfk: bounding box is more efficient probably
		const TopoDS_Wire& w = TopoDS::Wire(it.Value());
		TopoDS_Face face = BRepBuilderAPI_MakeFace(w).Face();
		const double m = face_area(face);
		*/

		Bnd_Box bb;
		BRepBndLib::AddClose(it.Value(), bb);
		double xyz_min[3], xyz_max[3];
		bb.Get(xyz_min[0], xyz_min[1], xyz_min[2], xyz_max[0], xyz_max[1], xyz_max[2]);
		
		// @todo hard coded precision.
		// @todo this is a really strange measure for wire size. Why not use newell's
		// method to project to plane and then calculate size of the 2d bbox?
		const double eps = 1.e-5;

		double m = 1.;
		for (int i = 0; i < 3; ++i) {
			if (Precision::IsNegativeInfinite(xyz_min[i])) {
				xyz_min[i] = 0.;
			}
			if (Precision::IsInfinite(xyz_max[i])) {
				xyz_max[i] = 0.;
			}
			m *= (xyz_max[i] + eps) - (xyz_min[i] - eps);
		}

		if (m > mass) {
			mass = m;
			largest = it.Value();
		}
	}
}


bool IfcGeom::util::wire_to_sequence_of_point(const TopoDS_Wire& w, TColgp_SequenceOfPnt& p) {
	TopExp_Explorer exp(w, TopAbs_EDGE);
	for (; exp.More(); exp.Next()) {
		double a, b;
		Handle_Geom_Curve crv = BRep_Tool::Curve(TopoDS::Edge(exp.Current()), a, b);
		if (crv->DynamicType() != STANDARD_TYPE(Geom_Line)) {
			return false;
		}
	}

	exp.ReInit();

	int i = 0;
	for (; exp.More(); exp.Next(), ++i) {
		TopoDS_Vertex v1, v2;
		TopExp::Vertices(TopoDS::Edge(exp.Current()), v1, v2, true);
		if (exp.More()) {
			if (i == 0) {
				p.Append(BRep_Tool::Pnt(v1));
			}
			p.Append(BRep_Tool::Pnt(v2));
		}
	}

	return true;
}

void IfcGeom::util::sequence_of_point_to_wire(const TColgp_SequenceOfPnt& p, TopoDS_Wire& w, bool close) {
	BRepBuilderAPI_MakePolygon builder;
	for (int i = 1; i <= p.Length(); ++i) {
		builder.Add(p.Value(i));
	}
	if (close) {
		builder.Close();
	}
	w = builder.Wire();
}

void IfcGeom::util::remove_collinear_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol) {
	const int start = closed ? 1 : 2;
	const int end = polygon.Length() - (closed ? 0 : 1);
	std::vector<bool> to_remove(polygon.Length(), false);
	for (int i = start; i <= end; ++i) {
		const gp_Pnt& a = polygon.Value(((i - 2 + polygon.Length()) % polygon.Length()) + 1);
		const gp_Pnt& b = polygon.Value(i);
		const gp_Pnt& c = polygon.Value((i % polygon.Length()) + 1);
		const gp_Vec d1 = c.XYZ() - a.XYZ();
		const gp_Vec d2 = b.XYZ() - a.XYZ();
		const double dt = d2.Dot(d1) / d1.Dot(d1);
		const gp_Vec d3 = d1.Scaled(dt);
		const gp_Pnt b2 = a.XYZ() + d3.XYZ();
		if (b.Distance(b2) < tol) {
			to_remove[i - 1] = true;
		}
	}
	for (int i = (int)to_remove.size() - 1; i >= 0; --i) {
		if (to_remove[i]) {
			polygon.Remove(i + 1);
		}
	}
}

void IfcGeom::util::remove_duplicate_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol) {
	tol *= tol;

	for (;;) {
		bool removed = false;
		int n = polygon.Length() - (closed ? 0 : 1);
		for (int i = 1; i <= n; ++i) {
			// wrap around to the first point in case of a closed loop
			int j = (i % polygon.Length()) + 1;
			double dist = polygon.Value(i).SquareDistance(polygon.Value(j));
			if (dist < tol) {
				// do not remove the first or last point to
				// maintain connectivity with other wires
				if ((closed && j == 1) || (!closed && j == n)) polygon.Remove(i);
				else polygon.Remove(j);
				removed = true;
				break;
			}
		}
		if (!removed) break;
	}
}


namespace {

	// Returns the vertex part of an TopoDS_Edge edge that is not TopoDS_Vertex vertex
	TopoDS_Vertex find_other(const TopoDS_Edge& edge, const TopoDS_Vertex& vertex) {
		TopExp_Explorer exp(edge, TopAbs_VERTEX);
		while (exp.More()) {
			if (!exp.Current().IsSame(vertex)) {
				return TopoDS::Vertex(exp.Current());
			}
			exp.Next();
		}
		return TopoDS_Vertex();
	}

	TopoDS_Edge find_next(const TopTools_IndexedMapOfShape& edge_set, const TopTools_IndexedDataMapOfShapeListOfShape& vertex_to_edges, const TopoDS_Vertex& current, const TopoDS_Edge& previous_edge) {
		const TopTools_ListOfShape& edges = vertex_to_edges.FindFromKey(current);
		TopTools_ListIteratorOfListOfShape eit;
		for (eit.Initialize(edges); eit.More(); eit.Next()) {
			const TopoDS_Edge& edge = TopoDS::Edge(eit.Value());
			if (edge.IsSame(previous_edge)) continue;
			if (edge_set.Contains(edge)) {
				return edge;
			}
		}
		return TopoDS_Edge();
	}

}

bool IfcGeom::util::fill_nonmanifold_wires_with_planar_faces(TopoDS_Shape& shape, double tol) {
	BRepOffsetAPI_Sewing sew;
	sew.Add(shape);

	TopTools_IndexedDataMapOfShapeListOfShape edge_to_faces;
	TopTools_IndexedDataMapOfShapeListOfShape vertex_to_edges;
	std::set<int> visited;
	TopTools_IndexedMapOfShape edge_set;

	TopExp::MapShapesAndAncestors(shape, TopAbs_EDGE, TopAbs_FACE, edge_to_faces);

	const int num_edges = edge_to_faces.Extent();
	for (int i = 1; i <= num_edges; ++i) {
		const TopTools_ListOfShape& faces = edge_to_faces.FindFromIndex(i);
		const int count = faces.Extent();
		// Find only the non-manifold edges: Edges that are only part of a
		// single face and therefore part of the wire(s) we want to fill.
		if (count == 1) {
			const TopoDS_Shape& edge = edge_to_faces.FindKey(i);
			TopExp::MapShapesAndAncestors(edge, TopAbs_VERTEX, TopAbs_EDGE, vertex_to_edges);
			edge_set.Add(edge);
		}
	}

	const int num_verts = vertex_to_edges.Extent();
	TopoDS_Vertex first, current;
	TopoDS_Edge previous_edge;

	// Now loop over all the vertices that are part of the wire(s) to be filled
	for (int i = 1; i <= num_verts; ++i) {
		first = current = TopoDS::Vertex(vertex_to_edges.FindKey(i));
		// We keep track of the vertices we already used
		if (visited.find(vertex_to_edges.FindIndex(current)) != visited.end()) {
			continue;
		}
		// Given these vertices, try to find closed loops and create new
		// wires out of them.
		BRepBuilderAPI_MakeWire w;
		for (;;) {
			visited.insert(vertex_to_edges.FindIndex(current));
			// Find the edge that the current vertex is part of and points
			// away from the previous vertex (null for the first vertex).
			TopoDS_Edge edge = find_next(edge_set, vertex_to_edges, current, previous_edge);
			if (edge.IsNull()) {
				return false;
			}
			TopoDS_Vertex other = find_other(edge, current);
			if (other.IsNull()) {
				// Dealing with a conical edge probably, for some reason
				// this works better than adding the edge directly.
				double u1, u2;
				Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u1, u2);
				w.Add(BRepBuilderAPI_MakeEdge(crv, u1, u2));
				break;
			} else {
				w.Add(edge);
			}
			// See if the starting point of this loop has been reached. Note that
			// additional wires after this one potentially will be created.
			if (other.IsSame(first)) {
				break;
			}
			previous_edge = edge;
			current = other;
		}
		sew.Add(BRepBuilderAPI_MakeFace(w));
		previous_edge.Nullify();
	}

	sew.Perform();
	shape = sew.SewedShape();

	try {
		ShapeFix_Solid solid;
		solid.LimitTolerance(tol);
		shape = solid.SolidFromShell(TopoDS::Shell(shape));
	} catch (const Standard_Failure& e) {
		if (e.GetMessageString() && strlen(e.GetMessageString())) {
			Logger::Error(e.GetMessageString());
		} else {
			Logger::Error("Unknown error creating solid");
		}
	} catch (...) {
		Logger::Error("Unknown error creating solid");
	}

	return true;
}


bool IfcGeom::util::convert_curve_to_wire(const Handle(Geom_Curve)& curve, TopoDS_Wire& wire) {
	try {
		wire = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(curve));
		return true;
	} catch (const Standard_Failure& e) {
		if (e.GetMessageString() && strlen(e.GetMessageString())) {
			Logger::Error(e.GetMessageString());
		} else {
			Logger::Error("Unknown error converting curve to wire");
		}
	} catch (...) {
		Logger::Error("Unknown error converting curve to wire");
	}
	return false;
}


void IfcGeom::util::assert_closed_wire(TopoDS_Wire& wire, double tol) {
	if (wire.Closed() == 0) {
		TopoDS_Vertex v0, v1;
		TopExp::Vertices(wire, v0, v1);

		gp_Pnt p1 = BRep_Tool::Pnt(v0);
		gp_Pnt p2 = BRep_Tool::Pnt(v1);

		if (p1.Distance(p2) > tol) {
			BRepBuilderAPI_MakeWire mw;
			mw.Add(wire);
			mw.Add(BRepBuilderAPI_MakeEdge(v0, v1).Edge());
			wire = mw.Wire();
		}

		Logger::Warning("Wire not closed");
	}
}

bool IfcGeom::util::convert_wire_to_face(const TopoDS_Wire& w, TopoDS_Face& face, const IfcGeom::util::wire_tolerance_settings& settings) {
	TopoDS_Wire wire = w;

	TopTools_ListOfShape results;

	if (settings.use_wire_intersection_check && util::wire_intersections(wire, results, settings)) {
		Logger::Warning("Self-intersections with " + boost::lexical_cast<std::string>(results.Extent()) + " cycles detected");
		util::select_largest(results, wire);
	}

	bool is_2d = true;
	TopExp_Explorer exp(wire, TopAbs_EDGE);
	for (; exp.More(); exp.Next()) {
		double a, b;
		// @todo this does not handle fillets
		Handle(Geom_Curve) crv = BRep_Tool::Curve(TopoDS::Edge(exp.Current()), a, b);
		if (crv->DynamicType() != STANDARD_TYPE(Geom_Line)) {
			is_2d = false;
			break;
		}
		Handle(Geom_Line) line = Handle(Geom_Line)::DownCast(crv);
		if (line->Lin().Direction().Z() > ALMOST_ZERO) {
			is_2d = false;
			break;
		}
	}

	if (!is_2d) {
		// For 2d wires (e.g. profiles) a higher tolerance for plane fitting is never required.
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire, settings.precision, TopAbs_WIRE);
	}

	BRepBuilderAPI_MakeFace mf(wire, false);
	BRepBuilderAPI_FaceError er = mf.Error();

	if (er != BRepBuilderAPI_FaceDone) {
		Logger::Error("Failed to create face.");
		return false;
	}
	face = mf.Face();

	return true;
}

bool IfcGeom::util::convert_wire_to_faces(const TopoDS_Wire& w, TopoDS_Compound& faces, const IfcGeom::util::wire_tolerance_settings& settings) {
	bool is_2d = true;
	TopExp_Explorer exp(w, TopAbs_EDGE);
	for (; exp.More(); exp.Next()) {
		double a, b;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(TopoDS::Edge(exp.Current()), a, b);
		if (crv->DynamicType() != STANDARD_TYPE(Geom_Line)) {
			is_2d = false;
			break;
		}
		Handle(Geom_Line) line = Handle(Geom_Line)::DownCast(crv);
		if (line->Lin().Direction().Z() > ALMOST_ZERO) {
			is_2d = false;
			break;
		}
	}

	TopTools_ListOfShape results;
	if (settings.use_wire_intersection_check && util::wire_intersections(w, results, settings)) {
		Logger::Warning("Self-intersections with " + boost::lexical_cast<std::string>(results.Extent()) + " cycles detected");
	} else {
		results.Clear();
		results.Append(w);
	}

	TopoDS_Compound C;
	BRep_Builder B;
	B.MakeCompound(faces);

	std::list<std::pair<double, TopoDS_Face>> face_list;
	double max_area = 0.;

	TopTools_ListIteratorOfListOfShape it(results);
	for (; it.More(); it.Next()) {
		const TopoDS_Wire& wire = TopoDS::Wire(it.Value());
		if (!is_2d) {
			// For 2d wires (e.g. profiles) a higher tolerance for plane fitting is never required.
			ShapeFix_ShapeTolerance FTol;
			FTol.SetTolerance(wire, settings.precision, TopAbs_WIRE);
		}

		BRepBuilderAPI_MakeFace mf(wire, false);
		BRepBuilderAPI_FaceError er = mf.Error();

		if (er != BRepBuilderAPI_FaceDone) {
			Logger::Error("Failed to create face.");
			continue;
		}

		TopoDS_Face face = mf.Face();
		const double m = face_area(face);

		face_list.push_back({ m, face });
		if (m > max_area) {
			max_area = m;
		}
	}

	for (auto& p : face_list) {
		if (p.first >= max_area / 10.) {
			B.Add(faces, p.second);
		} else {
			Logger::Warning("Ignoring self-intersection loop with area " + boost::lexical_cast<std::string>(p.first));
		}
	}

	return true;
}