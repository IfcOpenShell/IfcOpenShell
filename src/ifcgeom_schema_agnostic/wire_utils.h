#include <gp_Pln.hxx>
#include <TopoDS_Wire.hxx>
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

		/// Triangulate the set of wires. The firstmost wire is assumed to be the outer wire.
		triangulate_wire_result triangulate_wire(const std::vector<TopoDS_Wire>& wires, TopTools_ListOfShape& faces);

		// eps: tolerance added to wire intersection checks, can be zero
		// eps_real: tolerance used to construct new edge geometry around intersection points, cannot be zero
		bool wire_intersections(const TopoDS_Wire& wire, TopTools_ListOfShape& wires, double eps, double eps_real);

		void select_largest(const TopTools_ListOfShape& shapes, TopoDS_Shape& largest);
	}
}
