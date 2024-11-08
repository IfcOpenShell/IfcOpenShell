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

#ifndef CGALCONVERSIONRESULT_H
#define CGALCONVERSIONRESULT_H

#include "../../../ifcgeom/IfcGeomElement.h"

#undef Handle

#include "../../../ifcgeom/kernels/cgal/nef_to_halfspace_tree.h"

#define CGAL_NO_DEPRECATED_CODE

#include <boost/property_map/property_map.hpp>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/boost/graph/graph_traits_Polyhedron_3.h>
#include <CGAL/Polygon_mesh_processing/stitch_borders.h>
#include <CGAL/Polygon_mesh_processing/orientation.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/compute_normal.h>
#include <CGAL/Polygon_mesh_processing/self_intersections.h>

#ifdef IFOPSH_SIMPLE_KERNEL

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

#define Kernel_ SimpleKernel_
#define CgalShape SimpleCgalShape
#define cgal_placement_t cgal_simple_placement_t
#define cgal_point_t cgal_simple_point_t
#define cgal_direction_t cgal_simple_direction_t
#define cgal_vector_t cgal_simple_vector_t
#define cgal_plane_t cgal_simple_plane_t
#define cgal_curve_t cgal_simple_curve_t
#define cgal_wire_t cgal_simple_wire_t
#define cgal_face_t cgal_simple_face_t
#define cgal_shape_t cgal_simple_shape_t
#define cgal_vertex_descriptor_t cgal_simple_vertex_descriptor_t
#define cgal_face_descriptor_t cgal_simple_face_descriptor_t

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_;

#else

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Nef_polyhedron_3.h>
typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_;

#endif

typedef Kernel_::Aff_transformation_3 cgal_placement_t;
typedef Kernel_::Point_3 cgal_point_t;
typedef Kernel_::Vector_3 cgal_direction_t;
typedef Kernel_::Vector_3 cgal_vector_t;
typedef Kernel_::Plane_3 cgal_plane_t;
typedef std::vector<Kernel_::Point_3> cgal_curve_t;
typedef std::vector<Kernel_::Point_3> cgal_wire_t;

namespace {
	struct cgal_face_t {
		cgal_wire_t outer;
		std::vector<cgal_wire_t> inner;
	};
}

typedef CGAL::Polyhedron_3<Kernel_> cgal_shape_t;
typedef boost::graph_traits<CGAL::Polyhedron_3<Kernel_>>::vertex_descriptor cgal_vertex_descriptor_t;
typedef boost::graph_traits<CGAL::Polyhedron_3<Kernel_>>::face_descriptor cgal_face_descriptor_t;

#include "../../../ifcgeom/ConversionResult.h"

namespace ifcopenshell { namespace geometry {

	using IfcGeom::OpaqueCoordinate;
	using IfcGeom::OpaqueNumber;

	using IfcGeom::add_;
	using IfcGeom::subtract_;
	using IfcGeom::multiply_;
	using IfcGeom::divide_;
	using IfcGeom::equals_;
	using IfcGeom::less_than_;
	using IfcGeom::negate_;

#ifndef IFOPSH_SIMPLE_KERNEL
	class IFC_GEOM_API NumberEpeck : public OpaqueNumber {
	private:
		CGAL::Epeck::FT value_;

		template <CGAL::Epeck::FT(*Fn)(CGAL::Epeck::FT, CGAL::Epeck::FT)>
		OpaqueNumber* binary_op(OpaqueNumber* other) const {
			auto nnd = dynamic_cast<NumberEpeck*>(other);
			if (nnd) {
				return new NumberEpeck(Fn(value_, nnd->value_));
			} else {
				return nullptr;
			}
		}

		template <bool(*Fn)(CGAL::Epeck::FT, CGAL::Epeck::FT)>
		bool binary_op_bool(OpaqueNumber* other) const {
			auto nnd = dynamic_cast<NumberEpeck*>(other);
			if (nnd) {
				return Fn(value_, nnd->value_);
			} else {
				return false;
			}
		}

		template <CGAL::Epeck::FT(*Fn)(CGAL::Epeck::FT)>
		OpaqueNumber* unary_op() const {
			return new NumberEpeck(Fn(value_));
		}
	public:
		NumberEpeck(const CGAL::Epeck::FT& v)
			: value_(v) {}

		virtual ~NumberEpeck() { }

		virtual double to_double() const {
			return CGAL::to_double(value_);
		}

		virtual std::string to_string() const {
			std::stringstream ss;
			ss << value_.exact();
			return ss.str();
		}

		const CGAL::Epeck::FT& value() const {
			return value_;
		}

		virtual OpaqueNumber* operator+(OpaqueNumber* other) const {
			return binary_op<add_<CGAL::Epeck::FT>>(other);
		}
		virtual OpaqueNumber* operator-(OpaqueNumber* other) const {
			return binary_op<subtract_<CGAL::Epeck::FT>>(other);
		}
		virtual OpaqueNumber* operator*(OpaqueNumber* other) const {
			return binary_op<multiply_<CGAL::Epeck::FT>>(other);
		}
		virtual OpaqueNumber* operator/(OpaqueNumber* other) const {
			return binary_op<divide_<CGAL::Epeck::FT>>(other);
		}
		virtual bool operator==(OpaqueNumber* other) const {
			return binary_op_bool<equals_<CGAL::Epeck::FT>>(other);
		}
		virtual bool operator<(OpaqueNumber* other) const {
			return binary_op_bool<less_than_<CGAL::Epeck::FT>>(other);
		}
		virtual OpaqueNumber* operator-() const {
			return unary_op<negate_<CGAL::Epeck::FT>>();
		}
		virtual OpaqueNumber* clone() const {
			return new NumberEpeck(value_);
		}
	};
#endif

	class CgalShape : public IfcGeom::ConversionResultShape {
	private:
		bool convex_tag_ = false;
		mutable boost::optional<cgal_shape_t> shape_;
#ifndef IFOPSH_SIMPLE_KERNEL
		mutable boost::optional<CGAL::Nef_polyhedron_3<Kernel_>> nef_;
#endif
    public:
		CgalShape(const cgal_shape_t& shape, bool convex = false);

#ifndef IFOPSH_SIMPLE_KERNEL
		CgalShape(const CGAL::Nef_polyhedron_3<Kernel_>& shape, bool convex = false) {
			nef_ = shape;
			convex_tag_ = convex;
		}
#endif

#ifndef IFOPSH_SIMPLE_KERNEL
		void to_poly() const;

		void to_nef() const;

		operator const CGAL::Nef_polyhedron_3<Kernel_>& () const { to_nef(); return *nef_; }
		const CGAL::Nef_polyhedron_3<Kernel_>& nef() const { to_nef(); return *nef_; }
#else
		// noop on simple kernel
		void to_poly() const {}
#endif

		operator const cgal_shape_t& () const { to_poly();  return *shape_; }
		const cgal_shape_t& poly() const { to_poly(); return *shape_; }

		virtual void Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id) const;
		virtual void Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string&) const;

		virtual IfcGeom::ConversionResultShape* clone() const {
			return new CgalShape(*shape_);
		}

		virtual bool is_manifold() const;

		virtual double bounding_box(void*&) const;

		virtual int num_vertices() const;

		virtual void set_box(void*);

		virtual int surface_genus() const;

		virtual int num_edges() const;
		virtual int num_faces() const;

		// @todo this must be something with a virtual dtor so that we can delete it.
		virtual std::pair<OpaqueCoordinate<3>, OpaqueCoordinate<3>> bounding_box() const;

		virtual OpaqueNumber* length();
		virtual OpaqueNumber* area();
		virtual OpaqueNumber* volume();

		virtual OpaqueCoordinate<3> position();
		virtual OpaqueCoordinate<3> axis();
		virtual OpaqueCoordinate<4> plane_equation();

		virtual std::vector<ConversionResultShape*> convex_decomposition();
		virtual ConversionResultShape* halfspaces();
		virtual ConversionResultShape* solid();
		virtual ConversionResultShape* box();

		virtual std::vector<ConversionResultShape*> vertices();
		virtual std::vector<ConversionResultShape*> edges();
		virtual std::vector<ConversionResultShape*> facets();

		virtual ConversionResultShape* add(ConversionResultShape*);
		virtual ConversionResultShape* subtract(ConversionResultShape*);
		virtual ConversionResultShape* intersect(ConversionResultShape*);

		virtual void map(OpaqueCoordinate<4>& from, OpaqueCoordinate<4>& to);
		virtual void map(const std::vector<OpaqueCoordinate<4>>& from, const std::vector<OpaqueCoordinate<4>>& to);
		virtual ConversionResultShape* moved(ifcopenshell::geometry::taxonomy::matrix4::ptr) const;

		bool convex_tag() const { return convex_tag_; }
		bool& convex_tag() { return convex_tag_; }
	};

#ifndef IFOPSH_SIMPLE_KERNEL
	class CgalShapeHalfSpaceDecomposition : public IfcGeom::ConversionResultShape {
	private:
		std::unique_ptr<halfspace_tree<Kernel_>> shape_;
		std::list<CGAL::Plane_3<Kernel_>> planes_;

	public:
		CgalShapeHalfSpaceDecomposition(const CGAL::Nef_polyhedron_3<Kernel_>& shape, bool is_convex) {
			if (is_convex) {
				shape_ = std::move(build_halfspace_tree_is_decomposed(shape, planes_));
			} else {
				shape_ = std::move(build_halfspace_tree_decomposed(shape, planes_));
			}
		}

		CgalShapeHalfSpaceDecomposition(const CGAL::Plane_3<Kernel_>& shape) {
			shape_.reset(new halfspace_tree_plane<Kernel_>(shape));
			planes_.push_back(shape);
		}

		virtual void Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id) const;
		virtual void Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string&) const;

		virtual int surface_genus() const;
		virtual bool is_manifold() const;

		virtual int num_vertices() const;
		virtual int num_edges() const;
		virtual int num_faces() const;

		virtual double bounding_box(void*&) const;

		// @todo this must be something with a virtual dtor so that we can delete it.
		virtual std::pair<OpaqueCoordinate<3>, OpaqueCoordinate<3>> bounding_box() const;
		virtual void set_box(void* b);

		virtual OpaqueNumber* length();
		virtual OpaqueNumber* area();
		virtual OpaqueNumber* volume();

		virtual OpaqueCoordinate<3> position();
		virtual OpaqueCoordinate<3> axis();
		virtual OpaqueCoordinate<4> plane_equation();

		virtual std::vector<ConversionResultShape*> convex_decomposition();
		virtual ConversionResultShape* halfspaces();
		virtual ConversionResultShape* solid();
		virtual ConversionResultShape* box();

		virtual std::vector<ConversionResultShape*> vertices();
		virtual std::vector<ConversionResultShape*> edges();
		virtual std::vector<ConversionResultShape*> facets();

		virtual ConversionResultShape* add(ConversionResultShape*);
		virtual ConversionResultShape* subtract(ConversionResultShape*);
		virtual ConversionResultShape* intersect(ConversionResultShape*);

		virtual void map(OpaqueCoordinate<4>& from, OpaqueCoordinate<4>& to);
		virtual void map(const std::vector<OpaqueCoordinate<4>>& from, const std::vector<OpaqueCoordinate<4>>& to);
		virtual ConversionResultShape* moved(ifcopenshell::geometry::taxonomy::matrix4::ptr) const;
	};
#endif
}}

#endif
