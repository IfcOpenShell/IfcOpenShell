#ifndef BASE_UTILS_H
#define BASE_UTILS_H

#include <TopoDS_Shape.hxx>
#include <gp_Ax3.hxx>

namespace IfcGeom {
	namespace util {

		int count(const TopoDS_Shape&, TopAbs_ShapeEnum, bool unique = false);
		int surface_genus(const TopoDS_Shape&);

		bool is_manifold(const TopoDS_Shape& a);

		// For axis placements detect equality early in order for the
		// relatively computionaly expensive gp_Trsf calculation to be skipped
		bool axis_equal(const gp_Ax3& a, const gp_Ax3& b, double tolerance);

		bool axis_equal(const gp_Ax2d& a, const gp_Ax2d& b, double tolerance);

		bool is_identity(const gp_Trsf2d& t, double tolerance);
		bool is_identity(const gp_GTrsf2d& t, double tolerance);
		bool is_identity(const gp_Trsf& t, double tolerance);
		bool is_identity(const gp_GTrsf& t, double tolerance);

		gp_Trsf combine_offset_and_rotation(const gp_Vec &offset, const gp_Quaternion& rotation);

		bool is_nested_compound_of_solid(const TopoDS_Shape& s, int depth = 0);
	}
}

#endif