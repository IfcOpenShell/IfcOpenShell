#ifndef BASE_UTILS_H
#define BASE_UTILS_H

#include "../../../ifcgeom/ConversionResult.h"
#include "../ifc_geomlibrary_api.h"

#include <gp_Pln.hxx>
#include <gp_Pnt.hxx>
#include <gp_Ax3.hxx>
#include <gp_Ax2d.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_GTrsf.hxx>

#include <TopTools_ListOfShape.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Shape.hxx>

#include <Geom_Curve.hxx>
#include <Geom_Surface.hxx>

#include <vector>

namespace IfcGeom {
	namespace util {

		IFC_GEOMLIBRARY_API int count(const TopoDS_Shape&, TopAbs_ShapeEnum, bool unique = false);
		IFC_GEOMLIBRARY_API int surface_genus(const TopoDS_Shape&);

		IFC_GEOMLIBRARY_API bool is_manifold(const TopoDS_Shape& a);

		// For axis placements detect equality early in order for the
		// relatively computionaly expensive gp_Trsf calculation to be skipped
		IFC_GEOMLIBRARY_API bool axis_equal(const gp_Ax3& a, const gp_Ax3& b, double tolerance);

		IFC_GEOMLIBRARY_API bool axis_equal(const gp_Ax2d& a, const gp_Ax2d& b, double tolerance);

		IFC_GEOMLIBRARY_API bool is_identity(const gp_Trsf2d& t, double tolerance);
		IFC_GEOMLIBRARY_API bool is_identity(const gp_GTrsf2d& t, double tolerance);
		IFC_GEOMLIBRARY_API bool is_identity(const gp_Trsf& t, double tolerance);
		IFC_GEOMLIBRARY_API bool is_identity(const gp_GTrsf& t, double tolerance);

		IFC_GEOMLIBRARY_API gp_Trsf combine_offset_and_rotation(const gp_Vec &offset, const gp_Quaternion& rotation);

		IFC_GEOMLIBRARY_API bool is_nested_compound_of_solid(const TopoDS_Shape& s, int depth = 0);

		// Creates a solid from a compound of faces. When there are multiple connected components,
		// a compound of solids is returned.
		IFC_GEOMLIBRARY_API bool create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& solid, double tol);
		IFC_GEOMLIBRARY_API bool shape_to_face_list(const TopoDS_Shape& s, TopTools_ListOfShape& li);
		IFC_GEOMLIBRARY_API bool create_solid_from_faces(const TopTools_ListOfShape& face_list, TopoDS_Shape& solid, double tol, bool force_sewing = false);
		IFC_GEOMLIBRARY_API bool is_compound_of_faces(const TopoDS_Shape& shape);
		IFC_GEOMLIBRARY_API bool is_convex(const TopoDS_Wire& wire, double tol);
		IFC_GEOMLIBRARY_API TopoDS_Shape halfspace_from_plane(const gp_Pln& pln, const gp_Pnt& cent);
		IFC_GEOMLIBRARY_API gp_Pln plane_from_face(const TopoDS_Face& face);
		IFC_GEOMLIBRARY_API gp_Pnt point_above_plane(const gp_Pln& pln, bool agree = true);

		IFC_GEOMLIBRARY_API bool fit_halfspace(const TopoDS_Shape& a, const TopoDS_Shape& b, TopoDS_Shape& box, double& height, double tol);
		IFC_GEOMLIBRARY_API const Handle_Geom_Curve intersect(const Handle_Geom_Surface&, const Handle_Geom_Surface&);
		IFC_GEOMLIBRARY_API const Handle_Geom_Curve intersect(const Handle_Geom_Surface&, const TopoDS_Face&);
		IFC_GEOMLIBRARY_API const Handle_Geom_Curve intersect(const TopoDS_Face&, const Handle_Geom_Surface&);
		IFC_GEOMLIBRARY_API bool intersect(const Handle_Geom_Curve&, const Handle_Geom_Surface&, gp_Pnt&);
		IFC_GEOMLIBRARY_API bool intersect(const Handle_Geom_Curve&, const TopoDS_Face&, gp_Pnt&);
		IFC_GEOMLIBRARY_API bool intersect(const Handle_Geom_Curve&, const TopoDS_Shape&, std::vector<gp_Pnt>&);
		IFC_GEOMLIBRARY_API bool intersect(const Handle_Geom_Surface&, const TopoDS_Shape&, std::vector< std::pair<Handle_Geom_Surface, Handle_Geom_Curve> >&);
		IFC_GEOMLIBRARY_API bool closest(const gp_Pnt&, const std::vector<gp_Pnt>&, gp_Pnt&);
		IFC_GEOMLIBRARY_API bool project(const Handle_Geom_Curve&, const gp_Pnt&, gp_Pnt& p, double& u, double& d);
		IFC_GEOMLIBRARY_API bool project(const Handle_Geom_Surface&, const TopoDS_Shape&, double& u1, double& v1, double& u2, double& v2, double widen = 0.1);

		IFC_GEOMLIBRARY_API double shape_volume(const TopoDS_Shape& s);
		IFC_GEOMLIBRARY_API double face_area(const TopoDS_Face& f);

		IFC_GEOMLIBRARY_API TopoDS_Shape apply_transformation(const TopoDS_Shape&, const ifcopenshell::geometry::taxonomy::matrix4& t);
		IFC_GEOMLIBRARY_API TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_Trsf&);
		IFC_GEOMLIBRARY_API TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_GTrsf&);

		IFC_GEOMLIBRARY_API bool flatten_shape_list(const IfcGeom::ConversionResults& shapes, TopoDS_Shape& result, bool fuse, bool create_shell, double tol);
		IFC_GEOMLIBRARY_API bool validate_shape(const TopoDS_Shape&);

		IFC_GEOMLIBRARY_API TopoDS_Shape unify(const TopoDS_Shape& s, double tolerance);
	}
}

#endif
