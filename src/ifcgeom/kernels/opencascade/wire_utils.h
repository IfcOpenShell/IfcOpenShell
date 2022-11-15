#ifndef WIRE_UTILS_H
#define WIRE_UTILS_H

#include <gp_Pln.hxx>

#include <Geom_Curve.hxx>

#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Shape.hxx>
#include <TopoDS_Compound.hxx>

#include <TColgp_SequenceOfPnt.hxx>
#include <TopTools_ListOfShape.hxx>

#include <vector>

namespace IfcGeom {
	namespace util {
		bool approximate_plane_through_wire(const TopoDS_Wire& wire, gp_Pln& plane, double eps);

		bool flatten_wire(TopoDS_Wire& wire, double eps);

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
		triangulate_wire_result triangulate_wire(const std::vector<TopoDS_Wire>& wires, TopTools_ListOfShape& faces);

		bool wire_intersections(const TopoDS_Wire& wire, TopTools_ListOfShape& wires, const wire_tolerance_settings& settings);

		void select_largest(const TopTools_ListOfShape& shapes, TopoDS_Shape& largest);

		bool convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face, const IfcGeom::util::wire_tolerance_settings& settings);

		bool convert_wire_to_faces(const TopoDS_Wire& wire, TopoDS_Compound& face, const IfcGeom::util::wire_tolerance_settings& settings);

		void assert_closed_wire(TopoDS_Wire& wire, double tol);

		bool fill_nonmanifold_wires_with_planar_faces(TopoDS_Shape& shape, double tol);
		void remove_duplicate_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol);
		void remove_collinear_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol);
		bool wire_to_sequence_of_point(const TopoDS_Wire&, TColgp_SequenceOfPnt&);
		void sequence_of_point_to_wire(const TColgp_SequenceOfPnt&, TopoDS_Wire&, bool closed);

		bool convert_curve_to_wire(const Handle(Geom_Curve)& curve, TopoDS_Wire& wire);
	}
}

#endif
