// This file was generated with the assistance of an AI coding tool.

#include "boolean_cgal_fallback.h"
#include "base_utils.h"

#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Shell.hxx>
#include <TopoDS_Compound.hxx>
#include <BRep_Tool.hxx>
#include <BRep_Builder.hxx>
#include <BRepTools.hxx>
#include <BRepTools_WireExplorer.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_Sewing.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <ShapeFix_Shape.hxx>
#include <Geom_Plane.hxx>
#include <gp_Pnt.hxx>

#ifdef IFOPSH_WITH_CGAL

// The rest of this file only deals with plain CGAL types, so the OCCT
// Handle(...) macro is no longer needed and would clash with CGAL/boost.
#undef Handle

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/Polygon_mesh_processing/repair_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/orient_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/polygon_soup_to_polygon_mesh.h>
#include <CGAL/Polygon_mesh_processing/orientation.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/number_utils.h>

namespace {

	typedef CGAL::Exact_predicates_exact_constructions_kernel fallback_kernel_t;
	typedef fallback_kernel_t::Point_3 fallback_point_t;
	typedef CGAL::Polyhedron_3<fallback_kernel_t> fallback_polyhedron_t;
	typedef CGAL::Nef_polyhedron_3<fallback_kernel_t> fallback_nef_t;

	bool shape_has_only_planar_faces(const TopoDS_Shape& s) {
		for (TopExp_Explorer exp(s, TopAbs_FACE); exp.More(); exp.Next()) {
			auto surf = BRep_Tool::Surface(TopoDS::Face(exp.Current()));
			if (surf.IsNull() || surf->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
				return false;
			}
		}
		return true;
	}

	// Builds a polygon soup from the outer wire of every face. Faces with
	// inner wires (holes) are not supported and cause this to fail, leaving
	// the caller to fall back to the pre-existing behaviour.
	bool shape_to_polyhedron(const TopoDS_Shape& s, fallback_polyhedron_t& poly) {
		std::vector<fallback_point_t> points;
		std::vector<std::vector<std::size_t>> polygons;

		for (TopExp_Explorer fexp(s, TopAbs_FACE); fexp.More(); fexp.Next()) {
			const TopoDS_Face& f = TopoDS::Face(fexp.Current());

			int num_wires = 0;
			for (TopExp_Explorer wexp(f, TopAbs_WIRE); wexp.More(); wexp.Next()) {
				++num_wires;
			}
			if (num_wires != 1) {
				return false;
			}

			TopoDS_Wire w = BRepTools::OuterWire(f);

			std::vector<std::size_t> face_indices;
			for (BRepTools_WireExplorer we(w, f); we.More(); we.Next()) {
				gp_Pnt p = BRep_Tool::Pnt(we.CurrentVertex());
				points.emplace_back(p.X(), p.Y(), p.Z());
				face_indices.push_back(points.size() - 1);
			}

			if (face_indices.size() < 3) {
				return false;
			}

			polygons.push_back(std::move(face_indices));
		}

		if (polygons.empty()) {
			return false;
		}

		CGAL::Polygon_mesh_processing::repair_polygon_soup(points, polygons);

		if (!CGAL::Polygon_mesh_processing::is_polygon_soup_a_polygon_mesh(polygons)) {
			CGAL::Polygon_mesh_processing::orient_polygon_soup(points, polygons);
		}

		poly.clear();
		CGAL::Polygon_mesh_processing::polygon_soup_to_polygon_mesh(points, polygons, poly);

		return poly.size_of_facets() > 0;
	}

	bool shape_to_nef(const TopoDS_Shape& s, fallback_nef_t& nef) {
		fallback_polyhedron_t poly;
		if (!shape_to_polyhedron(s, poly)) {
			return false;
		}

		if (!poly.is_closed()) {
			return false;
		}

		try {
			if (!CGAL::Polygon_mesh_processing::is_outward_oriented(poly)) {
				CGAL::Polygon_mesh_processing::reverse_face_orientations(poly);
			}
			CGAL::Polygon_mesh_processing::triangulate_faces(poly);
			nef = fallback_nef_t(poly);
		} catch (...) {
			return false;
		}

		return !nef.is_empty();
	}

	bool polyhedron_to_shape(fallback_polyhedron_t& poly, TopoDS_Shape& result, double tol) {
		if (poly.size_of_facets() == 0) {
			return false;
		}

		BRep_Builder builder;
		TopoDS_Compound comp;
		builder.MakeCompound(comp);

		for (auto fit = poly.facets_begin(); fit != poly.facets_end(); ++fit) {
			BRepBuilderAPI_MakePolygon mp;
			auto h = fit->facet_begin();
			auto h0 = h;
			do {
				const auto& p = h->vertex()->point();
				mp.Add(gp_Pnt(CGAL::to_double(p.x()), CGAL::to_double(p.y()), CGAL::to_double(p.z())));
				++h;
			} while (h != h0);

			if (!mp.IsDone()) {
				return false;
			}
			mp.Close();

			BRepBuilderAPI_MakeFace mf(mp.Wire());
			if (!mf.IsDone()) {
				return false;
			}

			builder.Add(comp, mf.Face());
		}

		BRepBuilderAPI_Sewing sewing(tol);
		sewing.Add(comp);
		sewing.Perform();

		TopoDS_Shape sewn = sewing.SewedShape();

		TopoDS_Shape solid_or_shell = sewn;
		if (sewn.ShapeType() == TopAbs_SHELL) {
			BRepBuilderAPI_MakeSolid ms(TopoDS::Shell(sewn));
			if (ms.IsDone()) {
				solid_or_shell = ms.Solid();
			}
		}

		ShapeFix_Shape fix(solid_or_shell);
		fix.SetMaxTolerance(tol);
		fix.Perform();

		result = fix.Shape();
		return true;
	}

}

bool IfcGeom::util::boolean_operation_cgal_fallback(const TopoDS_Shape& a, const NCollection_List<TopoDS_Shape>& b, BOPAlgo_Operation op, TopoDS_Shape& result, double tol) {
	if (op != BOPAlgo_CUT && op != BOPAlgo_FUSE && op != BOPAlgo_COMMON) {
		return false;
	}

	if (!shape_has_only_planar_faces(a)) {
		return false;
	}

	fallback_nef_t nef_a;
	if (!shape_to_nef(a, nef_a)) {
		return false;
	}

	NCollection_List<TopoDS_Shape>::Iterator it(b);
	for (; it.More(); it.Next()) {
		if (!shape_has_only_planar_faces(it.Value())) {
			return false;
		}

		fallback_nef_t nef_b;
		if (!shape_to_nef(it.Value(), nef_b)) {
			return false;
		}

		if (op == BOPAlgo_CUT) {
			nef_a -= nef_b;
		} else if (op == BOPAlgo_FUSE) {
			nef_a += nef_b;
		} else {
			nef_a *= nef_b;
		}
	}

	if (!nef_a.is_simple()) {
		return false;
	}

	fallback_polyhedron_t poly;
	try {
		nef_a.convert_to_polyhedron(poly);
	} catch (...) {
		return false;
	}

	TopoDS_Shape shape;
	if (!polyhedron_to_shape(poly, shape, tol)) {
		return false;
	}

	BRepCheck_Analyzer ana(shape);
	if (!ana.IsValid()) {
		return false;
	}

	if (!is_manifold(shape) || has_coincident_edges(shape, tol)) {
		return false;
	}

	result = shape;
	return true;
}

#else

bool IfcGeom::util::boolean_operation_cgal_fallback(const TopoDS_Shape&, const NCollection_List<TopoDS_Shape>&, BOPAlgo_Operation, TopoDS_Shape&, double) {
	return false;
}

#endif
