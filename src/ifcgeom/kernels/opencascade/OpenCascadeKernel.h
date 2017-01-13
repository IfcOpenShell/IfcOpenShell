/********************************************************************************
*                                                                              *
* This file is part of IfcOpenShell.                                           *
*                                                                              *
* IfcOpenShell is free software: you can redistribute it and/or modify         *
* it under the terms of the Lesser GNU General Public License as published by  *
* the Free Software Foundation, either version 3.0 of the License, or          *
* (at your option) any later version.                                          *
*                                                                              *
* IfcOpenShell is distributed in the hope that it will be useful,              *
* but WITHOUT ANY WARRANTY; without even the implied warranty of               *
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
* Lesser GNU General Public License for more details.                          *
*                                                                              *
* You should have received a copy of the Lesser GNU General Public License     *
* along with this program. If not, see <http://www.gnu.org/licenses/>.         *
*                                                                              *
********************************************************************************/

#ifndef OPENCASADE_KERNEL_H
#define OPENCASADE_KERNEL_H

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <Geom_Curve.hxx>
#include <gp_Pln.hxx>
#include <TColgp_SequenceOfPnt.hxx>
#include <TopTools_ListOfShape.hxx>
#include <Geom_Surface.hxx>

// Define this in case you want to conserve memory usage at all cost. This has been
// benchmarked extensively: https://github.com/IfcOpenShell/IfcOpenShell/pull/47
// #define NO_CACHE

#ifdef NO_CACHE

#define IN_CACHE(T,E,t,e)
#define CACHE(T,E,e)

#else

#define IN_CACHE(T,E,t,e) std::map<int,t>::const_iterator it = cache.T.find(E->entity->id());\
if ( it != cache.T.end() ) { e = it->second; return true; }
#define CACHE(T,E,e) cache.T[E->entity->id()] = e;

#endif

namespace IfcGeom {

	class IFC_GEOM_API Cache {
	public:
#include "EntityMappingCreateCache.h"
		std::map<int, TopoDS_Shape> Shape;
	};

	class IFC_GEOM_API OpenCascadeKernel : public AbstractKernel {
	public:

#ifndef NO_CACHE
		Cache cache;
#endif

		IfcGeom::ShapeType shape_type(const IfcUtil::IfcBaseClass* L);

		bool convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face);
		bool convert_curve_to_wire(const Handle(Geom_Curve)& curve, TopoDS_Wire& wire);
		bool convert_shapes(const IfcUtil::IfcBaseClass* L, ConversionResults& result);
		bool convert_shape(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
		bool flatten_shape_list(const IfcGeom::ConversionResults& shapes, TopoDS_Shape& result, bool fuse);
		bool convert_wire(const IfcUtil::IfcBaseClass* L, TopoDS_Wire& result);
		bool convert_curve(const IfcUtil::IfcBaseClass* L, Handle(Geom_Curve)& result);
		bool convert_face(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);


		bool convert_layerset(const IfcSchema::IfcProduct*, std::vector<Handle_Geom_Surface>&, std::vector<const SurfaceStyle*>&, std::vector<double>&);
		bool apply_layerset(const ConversionResults&, const std::vector<Handle_Geom_Surface>&, const std::vector<const SurfaceStyle*>&, ConversionResults&);
		bool apply_folded_layerset(const ConversionResults&, const std::vector< std::vector<Handle_Geom_Surface> >&, const std::vector<const SurfaceStyle*>&, ConversionResults&);
		bool fold_layers(const IfcSchema::IfcWall*, const ConversionResults&, const std::vector<Handle_Geom_Surface>&, const std::vector<double>&, std::vector< std::vector<Handle_Geom_Surface> >&);

		bool split_solid_by_surface(const TopoDS_Shape&, const Handle_Geom_Surface&, TopoDS_Shape&, TopoDS_Shape&);
		bool split_solid_by_shell(const TopoDS_Shape&, const TopoDS_Shape& s, TopoDS_Shape&, TopoDS_Shape&);

		const Handle_Geom_Curve intersect(const Handle_Geom_Surface&, const Handle_Geom_Surface&);
		const Handle_Geom_Curve intersect(const Handle_Geom_Surface&, const TopoDS_Face&);
		const Handle_Geom_Curve intersect(const TopoDS_Face&, const Handle_Geom_Surface&);
		bool intersect(const Handle_Geom_Curve&, const Handle_Geom_Surface&, gp_Pnt&);
		bool intersect(const Handle_Geom_Curve&, const TopoDS_Face&, gp_Pnt&);
		bool intersect(const Handle_Geom_Curve&, const TopoDS_Shape&, std::vector<gp_Pnt>&);
		bool intersect(const Handle_Geom_Surface&, const TopoDS_Shape&, std::vector< std::pair<Handle_Geom_Surface, Handle_Geom_Curve> >&);
		bool closest(const gp_Pnt&, const std::vector<gp_Pnt>&, gp_Pnt&);
		bool project(const Handle_Geom_Curve&, const gp_Pnt&, gp_Pnt& p, double& u, double& d);
		bool project(const Handle_Geom_Surface&, const TopoDS_Shape&, double& u1, double& v1, double& u2, double& v2, double widen = 0.1);
		int count(const TopoDS_Shape&, TopAbs_ShapeEnum);


		bool find_wall_end_points(const IfcSchema::IfcWall*, gp_Pnt& start, gp_Pnt& end);

		bool create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& solid);
		bool create_solid_from_faces(const TopTools_ListOfShape& face_list, TopoDS_Shape& solid);
		bool is_compound(const TopoDS_Shape& shape);
		bool is_convex(const TopoDS_Wire& wire);
		TopoDS_Shape halfspace_from_plane(const gp_Pln& pln, const gp_Pnt& cent);
		gp_Pln plane_from_face(const TopoDS_Face& face);
		gp_Pnt point_above_plane(const gp_Pln& pln, bool agree = true);
		const TopoDS_Shape& ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid);
		bool profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Shape& face);
		double shape_volume(const TopoDS_Shape& s);
		double face_area(const TopoDS_Face& f);
		void apply_tolerance(TopoDS_Shape& s, double t);

		bool fill_nonmanifold_wires_with_planar_faces(TopoDS_Shape& shape);
		void remove_duplicate_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol = -1.);
		void remove_collinear_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol = -1.);
		bool wire_to_sequence_of_point(const TopoDS_Wire&, TColgp_SequenceOfPnt&);
		void sequence_of_point_to_wire(const TColgp_SequenceOfPnt&, TopoDS_Wire&, bool closed);
		bool approximate_plane_through_wire(const TopoDS_Wire&, gp_Pln&);
		bool flatten_wire(TopoDS_Wire&);

		static TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_Trsf&);
		static TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_GTrsf&);

		bool convert_openings(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const ConversionResults& entity_shapes, const gp_Trsf& entity_trsf, ConversionResults& cut_shapes);
		bool convert_openings_fast(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const ConversionResults& entity_shapes, const gp_Trsf& entity_trsf, ConversionResults& cut_shapes);

		void purge_cache() {
			// Rather hack-ish, but a stopgap solution to keep memory under control
			// for large files. SurfaceStyles need to be kept at all costs, as they
			// are read later on when serializing Collada files.
#ifndef NO_CACHE
			cache = Cache();
#endif
		}

		virtual bool is_identity_transform(IfcUtil::IfcBaseClass*);
		virtual IfcGeom::NativeElement<double>* create_brep_for_representation_and_product(
			const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*);
		virtual IfcGeom::NativeElement<double>* create_brep_for_processed_representation(
			const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*, IfcGeom::NativeElement<double>*);

#include "EntityMappingDeclaration.h"

	};

}

#endif