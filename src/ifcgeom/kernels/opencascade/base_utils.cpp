#include "base_utils.h"

#include "../../../ifcparse/IfcLogger.h"
#include "OpenCascadeConversionResult.h"
#include "boolean_utils.h"

#include <TopExp.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Vertex.hxx>

#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>

#include <Geom_Plane.hxx>
#include <Geom_OffsetSurface.hxx>

#include <ShapeAnalysis_Curve.hxx>
#include <ShapeAnalysis_Surface.hxx>

#include <BRep_Tool.hxx>
#include <BRepBndLib.hxx>

#include <BRepBuilderAPI_Transform.hxx>
#include <BRepBuilderAPI_GTransform.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepOffsetAPI_Sewing.hxx>

#include <GeomAPI_IntSS.hxx>
#include <GeomAPI_IntCS.hxx>

#include <BRepGProp.hxx>
#include <BRepGProp_Face.hxx>
#include <GProp_GProps.hxx>

#include <ShapeFix_Shell.hxx>
#include <ShapeFix_Solid.hxx>
#include <ShapeFix_Shape.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepClass3d_SolidClassifier.hxx>
#include <BRepCheck.hxx>
#include <BRepTools.hxx>

#include <BRepAlgoAPI_Fuse.hxx>

#include <TopTools_IndexedMapOfShape.hxx>

// For axis placements detect equality early in order for the
// relatively computionaly expensive gp_Trsf calculation to be skipped
bool IfcGeom::util::axis_equal(const gp_Ax3 & a, const gp_Ax3 & b, double tolerance) {
	if (!a.Location().IsEqual(b.Location(), tolerance)) return false;
	// Note that the tolerance below is angular, above is linear. Since architectural
	// objects are about 1m'ish in scale, it should be somewhat equivalent. Besides,
	// this is mostly a filter for NULL or default values in the placements.
	if (!a.Direction().IsEqual(b.Direction(), tolerance)) return false;
	if (!a.XDirection().IsEqual(b.XDirection(), tolerance)) return false;
	if (!a.YDirection().IsEqual(b.YDirection(), tolerance)) return false;
	return true;
}

bool IfcGeom::util::axis_equal(const gp_Ax2d & a, const gp_Ax2d & b, double tolerance) {
	if (!a.Location().IsEqual(b.Location(), tolerance)) return false;
	if (!a.Direction().IsEqual(b.Direction(), tolerance)) return false;
	return true;
}

int IfcGeom::util::count(const TopoDS_Shape& s, TopAbs_ShapeEnum t, bool unique) {
	if (unique) {
		TopTools_IndexedMapOfShape map;
		TopExp::MapShapes(s, t, map);
		return map.Extent();
	} else {
		int i = 0;
		TopExp_Explorer exp(s, t);
		for (; exp.More(); exp.Next()) {
			++i;
		}
		return i;
	}
}


int IfcGeom::util::surface_genus(const TopoDS_Shape& s) {
	int nv = count(s, TopAbs_VERTEX, true);
	int ne = count(s, TopAbs_EDGE, true);
	int nf = count(s, TopAbs_FACE, true);

	const int euler = nv - ne + nf;
	const int genus = (2 - euler) / 2;

	return genus;
}

bool IfcGeom::util::is_manifold(const TopoDS_Shape& a) {
	if (a.ShapeType() == TopAbs_COMPOUND || a.ShapeType() == TopAbs_SOLID) {
		TopoDS_Iterator it(a);
		for (; it.More(); it.Next()) {
			if (!is_manifold(it.Value())) {
				return false;
			}
		}
		return true;
	} else {
		TopTools_IndexedDataMapOfShapeListOfShape map;
		TopExp::MapShapesAndAncestors(a, TopAbs_EDGE, TopAbs_FACE, map);

		for (int i = 1; i <= map.Extent(); ++i) {
			const TopoDS_Edge& e = TopoDS::Edge(map.FindKey(i));

			TopoDS_Vertex v0, v1;
			TopExp::Vertices(e, v0, v1);
			const bool degenerate = !v0.IsNull() && !v1.IsNull() && v0.IsSame(v1);

			if (degenerate) {
				continue;
			}

			if (map.FindFromIndex(i).Extent() != 2) {
				return false;
			}
		}

		return true;
	}
}


bool IfcGeom::util::is_nested_compound_of_solid(const TopoDS_Shape& s, int depth) {
	if (s.ShapeType() == TopAbs_COMPOUND) {
		TopoDS_Iterator it(s);
		for (; it.More(); it.Next()) {
			if (!is_nested_compound_of_solid(it.Value(), depth + 1)) {
				return false;
			}
		}
		return true;
	} else if (s.ShapeType() == TopAbs_SOLID) {
		return depth > 0;
	} else {
		return false;
	}
}

namespace {
	template <typename T> struct dimension_count {};
	template <>           struct dimension_count <gp_Trsf2d > { static const int n = 2; };
	template <>           struct dimension_count <gp_GTrsf2d> { static const int n = 2; };
	template <>           struct dimension_count < gp_Trsf  > { static const int n = 3; };
	template <>           struct dimension_count < gp_GTrsf > { static const int n = 3; };

	template <typename T>
	bool is_identity_helper(const T& t, double tolerance) {
		// Note the {1, n+1} range due to Open Cascade's 1-based indexing
		// Note the {1, n+2} range due to the translation part of the matrix
		for (int i = 1; i < dimension_count<T>::n + 2; ++i) {
			for (int j = 1; j < dimension_count<T>::n + 1; ++j) {
				const double iden_value = i == j ? 1. : 0.;
				const double trsf_value = t.Value(j, i);
				if (fabs(trsf_value - iden_value) > tolerance) {
					return false;
				}
			}
		}
		return true;
	}
}

bool IfcGeom::util::is_identity(const gp_Trsf2d& t, double tolerance) {
	return is_identity_helper(t, tolerance);
}

bool IfcGeom::util::is_identity(const gp_GTrsf2d& t, double tolerance) {
	return is_identity_helper(t, tolerance);
}

bool IfcGeom::util::is_identity(const gp_Trsf& t, double tolerance) {
	return is_identity_helper(t, tolerance);
}

bool IfcGeom::util::is_identity(const gp_GTrsf& t, double tolerance) {
	return is_identity_helper(t, tolerance);
}

gp_Trsf IfcGeom::util::combine_offset_and_rotation(const gp_Vec & offset, const gp_Quaternion & rotation) {
	auto offset_transform = gp_Trsf{};
	offset_transform.SetTranslation(offset);

	auto rotation_transform = gp_Trsf{};
	rotation_transform.SetRotation(rotation);

	return rotation_transform * offset_transform;
}


bool IfcGeom::util::project(const Handle_Geom_Surface& srf, const TopoDS_Shape& shp, double& u1, double& v1, double& u2, double& v2, double widen) {
	// @todo std::unique_ptr for C++11
	ShapeAnalysis_Surface* sas = 0;
	Handle(Geom_Plane) pln;

	if (srf->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
		// Optimize projection for specific cases
		pln = Handle(Geom_Plane)::DownCast(srf);
	} else if (srf->DynamicType() == STANDARD_TYPE(Geom_OffsetSurface) && Handle(Geom_OffsetSurface)::DownCast(srf)->BasisSurface()->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
		// For an offset planar surface the projected UV coords are the same as the basis surface
		pln = Handle(Geom_Plane)::DownCast(Handle(Geom_OffsetSurface)::DownCast(srf)->BasisSurface());
	} else {
		sas = new ShapeAnalysis_Surface(srf);
	}

	u1 = v1 = +std::numeric_limits<double>::infinity();
	u2 = v2 = -std::numeric_limits<double>::infinity();

	gp_Pnt median;
	int vertex_count = 0;
	for (TopExp_Explorer exp(shp, TopAbs_VERTEX); exp.More(); exp.Next(), ++vertex_count) {
		gp_Pnt p = BRep_Tool::Pnt(TopoDS::Vertex(exp.Current()));
		median.ChangeCoord() += p.XYZ();

		gp_Pnt2d uv;
		if (sas) {
			uv = sas->ValueOfUV(p, 1e-3);
		} else {
			gp_Vec d = p.XYZ() - pln->Position().Location().XYZ();
			uv.SetX(d.Dot(pln->Position().XDirection()));
			uv.SetY(d.Dot(pln->Position().YDirection()));
		}

		if (uv.X() < u1) u1 = uv.X();
		if (uv.Y() < v1) v1 = uv.Y();
		if (uv.X() > u2) u2 = uv.X();
		if (uv.Y() > v2) v2 = uv.Y();
	}

	if (vertex_count > 0) {

		// Add a little bit of resolution so that the median is shifted towards the mass
		// of the curve. This helps to find the parameter ordering for conic surfaces.
		for (TopExp_Explorer exp(shp, TopAbs_EDGE); exp.More(); exp.Next(), ++vertex_count) {
			const TopoDS_Edge& e = TopoDS::Edge(exp.Current());

			double a, b;
			Handle_Geom_Curve crv = BRep_Tool::Curve(e, a, b);
			gp_Pnt p;
			crv->D0((a + b) / 2., p);

			median.ChangeCoord() += p.XYZ();
		}

		median.ChangeCoord().Divide(vertex_count);
		gp_Pnt2d uv;
		if (sas) {
			uv = sas->ValueOfUV(median, 1e-3);
		} else {
			gp_Vec d = median.XYZ() - pln->Position().Location().XYZ();
			uv.SetX(d.Dot(pln->Position().XDirection()));
			uv.SetY(d.Dot(pln->Position().YDirection()));
		}

		if (uv.X() < u1 || uv.X() > u2) {
			std::swap(u1, u2);
		}

		u1 -= widen;
		u2 += widen;
		v1 -= widen;
		v2 += widen;

	}

	delete sas;
	return vertex_count > 0;
}


TopoDS_Shape IfcGeom::util::apply_transformation(const TopoDS_Shape& s, const gp_Trsf& t) {
	if (t.Form() == gp_Identity) {
		return s;
	} else {
		/// @todo set to 1. and exactly 1. or use epsilon?
		if (t.ScaleFactor() != 1.) {
			return BRepBuilderAPI_Transform(s, t, true);
		} else {
			return s.Moved(t);
		}
	}
}


TopoDS_Shape IfcGeom::util::apply_transformation(const TopoDS_Shape& s, const gp_GTrsf& t) {
	if (t.Form() == gp_Other) {
		return BRepBuilderAPI_GTransform(s, t, true);
	} else {
		return apply_transformation(s, t.Trsf());
	}
}

TopoDS_Shape IfcGeom::util::apply_transformation(const TopoDS_Shape& s, const ifcopenshell::geometry::taxonomy::matrix4& t) {
	// @todo this probably discards non-uniform scale?
	gp_GTrsf trsf;
	if (t.components_) {
		gp_Trsf tr;
		const auto& m = t.ccomponents();
		tr.SetValues(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3)
		);
		trsf = tr;
	}
	return apply_transformation(s, trsf);
}

bool IfcGeom::util::fit_halfspace(const TopoDS_Shape& a, const TopoDS_Shape& b, TopoDS_Shape& box, double& height, double tol) {
	TopExp_Explorer exp(b, TopAbs_FACE);
	if (!exp.More()) {
		return false;
	}

	TopoDS_Face face = TopoDS::Face(exp.Current());
	exp.Next();

	if (exp.More()) {
		return false;
	}

	Handle(Geom_Surface) surf = BRep_Tool::Surface(face);

	// const gp_XYZ xyz = a.Location().Transformation().TranslationPart();
	// std::cout << "dz " << xyz.Z() << std::endl;

	if (surf->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
		return false;
	}

	Bnd_Box bb;
	BRepBndLib::Add(a, bb);

	if (bb.IsVoid()) {
		return false;
	}

	double xs[2], ys[2], zs[2];
	bb.Get(xs[0], ys[0], zs[0], xs[1], ys[1], zs[1]);

	gp_Pln pln = Handle(Geom_Plane)::DownCast(surf)->Pln();

	gp_Pnt P = pln.Position().Location();
	gp_Vec z = pln.Position().Direction();
	gp_Vec x = pln.Position().XDirection();
	gp_Vec y = pln.Position().YDirection();

	if (face.Orientation() != TopAbs_REVERSED) {
		z.Reverse();
	}

	double D, Umin, Umax, Vmin, Vmax;
	D = 0.;
	Umin = Vmin = +std::numeric_limits<double>::infinity();
	Umax = Vmax = -std::numeric_limits<double>::infinity();

	for (int i = 0; i < 2; ++i) {
		for (int j = 0; j < 2; ++j) {
			for (int k = 0; k < 2; ++k) {
				gp_Pnt p(xs[i], ys[j], zs[k]);

				gp_Vec d = p.XYZ() - P.XYZ();
				const double u = d.Dot(x);
				const double v = d.Dot(y);
				const double w = d.Dot(z);

				if (w > D) {
					D = w;
				}
				if (u < Umin) {
					Umin = u;
				}
				if (u > Umax) {
					Umax = u;
				}
				if (v < Vmin) {
					Vmin = v;
				}
				if (v > Vmax) {
					Vmax = v;
				}
			}
		}
	}

	const double eps = tol * 1000.;

	BRepBuilderAPI_MakePolygon poly;
	poly.Add(P.XYZ() + x.XYZ() * (Umin - eps) + y.XYZ() * (Vmin - eps));
	poly.Add(P.XYZ() + x.XYZ() * (Umax + eps) + y.XYZ() * (Vmin - eps));
	poly.Add(P.XYZ() + x.XYZ() * (Umax + eps) + y.XYZ() * (Vmax + eps));
	poly.Add(P.XYZ() + x.XYZ() * (Umin - eps) + y.XYZ() * (Vmax + eps));
	poly.Close();

	BRepBuilderAPI_MakeFace mf(surf, poly.Wire(), true);

	gp_Vec vec = gp_Vec(z.XYZ() * (D + eps));

	BRepPrimAPI_MakePrism mp(mf.Face(), vec);
	box = mp.Shape();

	height = D;
	return true;
}


const Handle_Geom_Curve IfcGeom::util::intersect(const Handle_Geom_Surface& a, const Handle_Geom_Surface& b) {
	GeomAPI_IntSS x(a, b, 1.e-7);
	if (x.IsDone() && x.NbLines() == 1) {
		return x.Line(1);
	} else {
		return Handle_Geom_Curve();
	}
}

const Handle_Geom_Curve IfcGeom::util::intersect(const Handle_Geom_Surface& a, const TopoDS_Face& b) {
	return intersect(a, BRep_Tool::Surface(b));
}

const Handle_Geom_Curve IfcGeom::util::intersect(const TopoDS_Face& a, const Handle_Geom_Surface& b) {
	return intersect(BRep_Tool::Surface(a), b);
}

bool IfcGeom::util::intersect(const Handle_Geom_Curve& a, const Handle_Geom_Surface& b, gp_Pnt& p) {
	GeomAPI_IntCS x(a, b);
	if (x.IsDone() && x.NbPoints() == 1) {
		p = x.Point(1);
		return true;
	} else {
		return false;
	}
}

bool IfcGeom::util::intersect(const Handle_Geom_Curve& a, const TopoDS_Face& b, gp_Pnt &c) {
	return intersect(a, BRep_Tool::Surface(b), c);
}

bool IfcGeom::util::intersect(const Handle_Geom_Curve& a, const TopoDS_Shape& b, std::vector<gp_Pnt>& out) {
	TopExp_Explorer exp(b, TopAbs_FACE);
	gp_Pnt p;
	for (; exp.More(); exp.Next()) {
		if (intersect(a, TopoDS::Face(exp.Current()), p)) {
			out.push_back(p);
		}
	}
	return !out.empty();
}

bool IfcGeom::util::intersect(const Handle_Geom_Surface& a, const TopoDS_Shape& b, std::vector< std::pair<Handle_Geom_Surface, Handle_Geom_Curve> >& out) {
	TopExp_Explorer exp(b, TopAbs_FACE);
	for (; exp.More(); exp.Next()) {
		const TopoDS_Face& f = TopoDS::Face(exp.Current());
		const Handle_Geom_Surface& s = BRep_Tool::Surface(f);
		Handle_Geom_Curve crv = intersect(a, s);
		if (!crv.IsNull()) {
			out.push_back(std::make_pair(s, crv));
		}
	}
	return !out.empty();
}

bool IfcGeom::util::closest(const gp_Pnt& a, const std::vector<gp_Pnt>& b, gp_Pnt& c) {
	double minimal_distance = std::numeric_limits<double>::infinity();
	for (std::vector<gp_Pnt>::const_iterator it = b.begin(); it != b.end(); ++it) {
		const double d = a.Distance(*it);
		if (d < minimal_distance) {
			minimal_distance = d;
			c = *it;
		}
	}
	return minimal_distance != std::numeric_limits<double>::infinity();
}

bool IfcGeom::util::project(const Handle_Geom_Curve& crv, const gp_Pnt& pt, gp_Pnt& p, double& u, double& d) {
	ShapeAnalysis_Curve sac;
	sac.Project(crv, pt, 1e-3, p, u, false);
	d = pt.Distance(p);
	return true;
}

double IfcGeom::util::shape_volume(const TopoDS_Shape& s) {
	GProp_GProps prop;
	BRepGProp::VolumeProperties(s, prop);
	return prop.Mass();
}

double IfcGeom::util::face_area(const TopoDS_Face& f) {
	GProp_GProps prop;
	BRepGProp::SurfaceProperties(f, prop);
	return prop.Mass();
}

bool IfcGeom::util::is_convex(const TopoDS_Wire& wire, double tol) {
	for (TopExp_Explorer exp1(wire, TopAbs_VERTEX); exp1.More(); exp1.Next()) {
		TopoDS_Vertex V1 = TopoDS::Vertex(exp1.Current());
		gp_Pnt P1 = BRep_Tool::Pnt(V1);
		// Store the neighboring points
		std::vector<gp_Pnt> neighbors;
		for (TopExp_Explorer exp3(wire, TopAbs_EDGE); exp3.More(); exp3.Next()) {
			TopoDS_Edge edge = TopoDS::Edge(exp3.Current());
			std::vector<gp_Pnt> edge_points;
			for (TopExp_Explorer exp2(edge, TopAbs_VERTEX); exp2.More(); exp2.Next()) {
				TopoDS_Vertex V2 = TopoDS::Vertex(exp2.Current());
				gp_Pnt P2 = BRep_Tool::Pnt(V2);
				edge_points.push_back(P2);
			}
			if (edge_points.size() != 2) continue;
			if (edge_points[0].IsEqual(P1, tol)) neighbors.push_back(edge_points[1]);
			else if (edge_points[1].IsEqual(P1, tol)) neighbors.push_back(edge_points[0]);
		}
		// There should be two of these
		if (neighbors.size() != 2) return false;
		// Now find the non neighboring points
		std::vector<gp_Pnt> non_neighbors;
		for (TopExp_Explorer exp2(wire, TopAbs_VERTEX); exp2.More(); exp2.Next()) {
			TopoDS_Vertex V2 = TopoDS::Vertex(exp2.Current());
			gp_Pnt P2 = BRep_Tool::Pnt(V2);
			if (P1.IsEqual(P2, tol)) continue;
			bool found = false;
			for (std::vector<gp_Pnt>::const_iterator it = neighbors.begin(); it != neighbors.end(); ++it) {
				if ((*it).IsEqual(P2, tol)) { found = true; break; }
			}
			if (!found) non_neighbors.push_back(P2);
		}
		// Calculate the angle between the two edges of the vertex
		gp_Dir dir1(neighbors[0].XYZ() - P1.XYZ());
		gp_Dir dir2(neighbors[1].XYZ() - P1.XYZ());
		const double angle = acos(dir1.Dot(dir2)) + 0.0001;
		// Now for the non-neighbors see whether a greater angle can be found with one of the edges
		for (std::vector<gp_Pnt>::const_iterator it = non_neighbors.begin(); it != non_neighbors.end(); ++it) {
			gp_Dir dir3((*it).XYZ() - P1.XYZ());
			const double angle2 = acos(dir3.Dot(dir1));
			const double angle3 = acos(dir3.Dot(dir2));
			if (angle2 > angle || angle3 > angle) return false;
		}
	}
	return true;
}

TopoDS_Shape IfcGeom::util::halfspace_from_plane(const gp_Pln& pln, const gp_Pnt& cent) {
	TopoDS_Face face = BRepBuilderAPI_MakeFace(pln).Face();
	return BRepPrimAPI_MakeHalfSpace(face, cent).Solid();
}

gp_Pln IfcGeom::util::plane_from_face(const TopoDS_Face& face) {
	BRepGProp_Face prop(face);
	Standard_Real u1, u2, v1, v2;
	prop.Bounds(u1, u2, v1, v2);
	Standard_Real u = (u1 + u2) / 2.0;
	Standard_Real v = (v1 + v2) / 2.0;
	gp_Pnt p;
	gp_Vec n;
	prop.Normal(u, v, p, n);
	return gp_Pln(p, n);
}

gp_Pnt IfcGeom::util::point_above_plane(const gp_Pln& pln, bool agree) {
	if (agree) {
		return pln.Location().Translated(pln.Axis().Direction());
	} else {
		return pln.Location().Translated(-pln.Axis().Direction());
	}
}

bool IfcGeom::util::is_compound(const TopoDS_Shape& shape) {
	bool has_solids = TopExp_Explorer(shape, TopAbs_SOLID).More() != 0;
	bool has_shells = TopExp_Explorer(shape, TopAbs_SHELL).More() != 0;
	bool has_compounds = TopExp_Explorer(shape, TopAbs_COMPOUND).More() != 0;
	bool has_faces = TopExp_Explorer(shape, TopAbs_FACE).More() != 0;
	return has_compounds && has_faces && !has_solids && !has_shells;
}

bool IfcGeom::util::shape_to_face_list(const TopoDS_Shape& s, TopTools_ListOfShape& li) {
	TopExp_Explorer exp(s, TopAbs_FACE);
	for (; exp.More(); exp.Next()) {
		TopoDS_Face face = TopoDS::Face(exp.Current());
		li.Append(face);
	}
	return true;
}

bool IfcGeom::util::create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& shape, double tol) {
	TopTools_ListOfShape face_list;
	shape_to_face_list(compound, face_list);
	if (face_list.Extent() == 0) {
		return false;
	}
	return create_solid_from_faces(face_list, shape, tol);
}

bool IfcGeom::util::create_solid_from_faces(const TopTools_ListOfShape& face_list, TopoDS_Shape& shape, double tol, bool force_sewing) {
	bool valid_shell = false;

	if (face_list.Extent() == 1) {
		shape = face_list.First();
		// A bit dubious what to return here.
		return true;
	} else if (face_list.Extent() == 0) {
		return false;
	}

	TopTools_ListIteratorOfListOfShape face_iterator;

	bool has_shared_edges = false;
	TopTools_MapOfShape edge_set;

	// In case there are wire intersections or failures in non-planar wire triangulations
	// the idea is to let occt do an exhaustive search of edge partners. But we have not
	// found a case where this actually improves boolean ops later on.
	// if (!faceset_helper_ || !faceset_helper_->non_manifold()) {

	for (face_iterator.Initialize(face_list); !force_sewing && face_iterator.More(); face_iterator.Next()) {
		// As soon as is detected one of the edges is shared, the assumption is made no
		// additional sewing is necessary.
		if (!has_shared_edges) {
			TopExp_Explorer exp(face_iterator.Value(), TopAbs_EDGE);
			for (; exp.More(); exp.Next()) {
				if (edge_set.Contains(exp.Current())) {
					has_shared_edges = true;
					break;
				}
				edge_set.Add(exp.Current());
			}
		}
	}

	BRepOffsetAPI_Sewing sewing_builder;
	sewing_builder.SetTolerance(tol);
	sewing_builder.SetMaxTolerance(tol);
	sewing_builder.SetMinTolerance(tol);

	BRep_Builder builder;
	TopoDS_Shell shell;
	builder.MakeShell(shell);

	for (face_iterator.Initialize(face_list); face_iterator.More(); face_iterator.Next()) {
		if (has_shared_edges) {
			builder.Add(shell, face_iterator.Value());
		} else {
			sewing_builder.Add(face_iterator.Value());
		}
	}

	try {
		if (has_shared_edges) {
			ShapeFix_Shell fix;
			fix.FixFaceOrientation(shell);
			shape = fix.Shape();
		} else {
			sewing_builder.Perform();
			shape = sewing_builder.SewedShape();
		}

		BRepCheck_Analyzer ana(shape);
		valid_shell = ana.IsValid();

		if (!valid_shell) {
			ShapeFix_Shape sfs(shape);
			sfs.Perform();
			shape = sfs.Shape();

			BRepCheck_Analyzer reana(shape);
			valid_shell = reana.IsValid();
		}

		valid_shell &= util::count(shape, TopAbs_SHELL) > 0;
	} catch (const Standard_Failure& e) {
		if (e.GetMessageString() && strlen(e.GetMessageString())) {
			Logger::Error(e.GetMessageString());
		} else {
			Logger::Error("Unknown error sewing shell");
		}
	} catch (...) {
		Logger::Error("Unknown error sewing shell");
	}

	if (valid_shell) {

		TopoDS_Shape complete_shape;
		TopExp_Explorer exp(shape, TopAbs_SHELL);

		for (; exp.More(); exp.Next()) {
			TopoDS_Shape result_shape = exp.Current();

			try {
				ShapeFix_Solid solid;
				solid.SetMaxTolerance(tol);
				TopoDS_Solid solid_shape = solid.SolidFromShell(TopoDS::Shell(exp.Current()));
				// @todo: BRepClass3d_SolidClassifier::PerformInfinitePoint() is done by SolidFromShell
				//        and this is done again, to be able to catch errors during this process.
				//        This is double work that should be avoided.
				if (!solid_shape.IsNull()) {
					try {
						BRepClass3d_SolidClassifier classifier(solid_shape);
						result_shape = solid_shape;
						classifier.PerformInfinitePoint(tol);
						if (classifier.State() == TopAbs_IN) {
							shape.Reverse();
						}
					} catch (const Standard_Failure& e) {
						if (e.GetMessageString() && strlen(e.GetMessageString())) {
							Logger::Error(e.GetMessageString());
						} else {
							Logger::Error("Unknown error classifying solid");
						}
					} catch (...) {
						Logger::Error("Unknown error classifying solid");
					}
				}
			} catch (const Standard_Failure& e) {
				if (e.GetMessageString() && strlen(e.GetMessageString())) {
					Logger::Error(e.GetMessageString());
				} else {
					Logger::Error("Unknown error creating solid");
				}
			} catch (...) {
				Logger::Error("Unknown error creating solid");
			}

			if (complete_shape.IsNull()) {
				complete_shape = result_shape;
			} else {
				BRep_Builder B;
				if (complete_shape.ShapeType() != TopAbs_COMPOUND) {
					TopoDS_Compound C;
					B.MakeCompound(C);
					B.Add(C, complete_shape);
					complete_shape = C;
					Logger::Warning("Multiple components in IfcConnectedFaceSet");
				}
				B.Add(complete_shape, result_shape);
			}
		}

		TopExp_Explorer loose_faces(shape, TopAbs_FACE, TopAbs_SHELL);

		for (; loose_faces.More(); loose_faces.Next()) {
			BRep_Builder B;
			if (complete_shape.ShapeType() != TopAbs_COMPOUND) {
				TopoDS_Compound C;
				B.MakeCompound(C);
				B.Add(C, complete_shape);
				complete_shape = C;
				Logger::Warning("Loose faces in IfcConnectedFaceSet");
			}
			B.Add(complete_shape, loose_faces.Current());
		}

		shape = complete_shape;

	} else {
		Logger::Error("Failed to sew faceset");
	}

	return valid_shell;
}

bool IfcGeom::util::flatten_shape_list(const IfcGeom::ConversionResults& shapes, TopoDS_Shape& result, bool fuse, bool create_shell, double tol) {
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	result = TopoDS_Shape();

	for (IfcGeom::ConversionResults::const_iterator it = shapes.begin(); it != shapes.end(); ++it) {
		TopoDS_Shape merged;
		const TopoDS_Shape& s = std::static_pointer_cast<ifcopenshell::geometry::OpenCascadeShape>(it->Shape())->shape();
		if (fuse || create_shell) {
			merged = util::ensure_fit_for_subtraction(s, tol);
		} else {
			merged = s;
		}

		// @todo refactor, also should be GTrsf
		const auto& m = it->Placement()->ccomponents();
		gp_Trsf trsf;
		trsf.SetValues(
			m(0, 0), m(0, 1), m(0, 2), m(0, 3),
			m(1, 0), m(1, 1), m(1, 2), m(1, 3),
			m(2, 0), m(2, 1), m(2, 2), m(2, 3)
		);

		const TopoDS_Shape moved_shape = util::apply_transformation(merged, trsf);

		if (shapes.size() == 1) {
			result = moved_shape;
			return true;
		}

		if (fuse) {
			if (result.IsNull()) {
				result = moved_shape;
			} else {
				BRepAlgoAPI_Fuse brep_fuse(result, moved_shape);
				if (brep_fuse.IsDone()) {
					TopoDS_Shape fused = brep_fuse;

					ShapeFix_Shape fix(result);
					fix.Perform();
					result = fix.Shape();

					bool is_valid = BRepCheck_Analyzer(result).IsValid() != 0;
					if (is_valid) {
						result = fused;
					}
				}
			}
		} else {
			builder.Add(compound, moved_shape);
		}
	}

	if (!fuse) {
		result = compound;
	}

	const bool success = !result.IsNull();
	return success;
}

bool IfcGeom::util::validate_shape(const TopoDS_Shape& s) {
	BRepCheck_Analyzer ana(s);
	if (ana.IsValid()) {
		return true;
	}

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
					BRepTools::Dump(s, str);
					any_emitted = true;
				}
			}
		}
		for (TopoDS_Iterator it(s); it.More(); it.Next()) {
			dump(it.Value());
		}
	};

	dump(s);

	Logger::Warning(str.str());

	return false;
}
