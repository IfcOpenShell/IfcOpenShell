#ifndef WIRE_UTILS_H
#define WIRE_UTILS_H

#include "../ifc_geomlibrary_api.h"

#include <gp_Pln.hxx>

#include <Geom_Curve.hxx>

#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Shape.hxx>
#include <TopoDS_Compound.hxx>

#include <gp_Pnt.hxx>
#include <NCollection_List.hxx>
#include <NCollection_Sequence.hxx>

#include <vector>

namespace IfcGeom {
	namespace util {
		IFC_GEOMLIBRARY_API bool approximate_plane_through_wire(const TopoDS_Wire& wire, gp_Pln& plane, double eps);

		IFC_GEOMLIBRARY_API bool flatten_wire(TopoDS_Wire& wire, double eps);

		enum triangulate_wire_result {
			TRIANGULATE_WIRE_FAIL,
			TRIANGULATE_WIRE_OK,
			TRIANGULATE_WIRE_NON_MANIFOLD,
		};

		struct wire_tolerance_settings {
			bool use_wire_intersection_check;
			bool use_wire_intersection_tolerance;
			double vertex_clustering_epsilon;
			double precision;
		};

		/// Triangulate the set of wires. The firstmost wire is assumed to be the outer wire.
        IFC_GEOMLIBRARY_API triangulate_wire_result triangulate_wire(const std::vector<TopoDS_Wire>& wires, NCollection_List<TopoDS_Shape>& faces);

		IFC_GEOMLIBRARY_API bool wire_intersections(const TopoDS_Wire& wire, NCollection_List<TopoDS_Shape>& wires, const wire_tolerance_settings& settings);

		IFC_GEOMLIBRARY_API void select_largest(const NCollection_List<TopoDS_Shape>& shapes, TopoDS_Shape& largest);

		IFC_GEOMLIBRARY_API bool convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face, const IfcGeom::util::wire_tolerance_settings& settings);

		IFC_GEOMLIBRARY_API bool convert_wire_to_faces(const TopoDS_Wire& wire, TopoDS_Compound& face, const IfcGeom::util::wire_tolerance_settings& settings);

		IFC_GEOMLIBRARY_API void assert_closed_wire(TopoDS_Wire& wire, double tol);

		IFC_GEOMLIBRARY_API bool fill_nonmanifold_wires_with_planar_faces(TopoDS_Shape& shape, double tol);
        IFC_GEOMLIBRARY_API void remove_duplicate_points_from_loop(NCollection_Sequence<gp_Pnt>& polygon, bool closed, double tol);
        IFC_GEOMLIBRARY_API void remove_collinear_points_from_loop(NCollection_Sequence<gp_Pnt>& polygon, bool closed, double tol);
        IFC_GEOMLIBRARY_API bool wire_to_sequence_of_point(const TopoDS_Wire&, NCollection_Sequence<gp_Pnt>&);
        IFC_GEOMLIBRARY_API void sequence_of_point_to_wire(const NCollection_Sequence<gp_Pnt>&, TopoDS_Wire&, bool closed);

		IFC_GEOMLIBRARY_API bool convert_curve_to_wire(const opencascade::handle<Geom_Curve>& curve, TopoDS_Wire& wire);
	}
}

#endif
