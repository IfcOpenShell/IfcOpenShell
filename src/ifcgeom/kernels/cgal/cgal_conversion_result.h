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

#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

#include "../../../ifcgeom/element.h"

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

#include <variant>

#ifdef IFOPSH_SIMPLE_KERNEL

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

#define kernel_ Simplekernel_
#define cgal_shape SimpleCgalShape
#define cgal_placement cgal_simple_placement
#define cgal_point cgal_simple_point
#define cgal_direction cgal_simple_direction
#define cgal_vector cgal_simple_vector
#define cgal_plane cgal_simple_plane
#define cgal_curve cgal_simple_curve
#define cgal_wire cgal_simple_wire
#define cgal_face cgal_simple_face
#define cgal_polyhedron cgal_simple_polyhedron
#define cgal_vertex_descriptor cgal_simple_vertex_descriptor
#define cgal_face_descriptor cgal_simple_face_descriptor

typedef CGAL::Exact_predicates_inexact_constructions_kernel kernel_;

#else

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Nef_polyhedron_3.h>
typedef CGAL::Exact_predicates_exact_constructions_kernel kernel_;

#endif

typedef kernel_::Aff_transformation_3 cgal_placement;
typedef kernel_::Point_3 cgal_point;
typedef kernel_::Vector_3 cgal_direction;
typedef kernel_::Vector_3 cgal_vector;
typedef kernel_::Plane_3 cgal_plane;
typedef std::vector<kernel_::Point_3> cgal_curve;
typedef std::vector<kernel_::Point_3> cgal_wire;

namespace {
	struct cgal_face {
		cgal_wire outer;
		std::vector<cgal_wire> inner;
	};
}

typedef CGAL::Polyhedron_3<kernel_> cgal_polyhedron;
typedef boost::graph_traits<CGAL::Polyhedron_3<kernel_>>::vertex_descriptor cgal_vertex_descriptor;
typedef boost::graph_traits<CGAL::Polyhedron_3<kernel_>>::face_descriptor cgal_face_descriptor;

#include "../../../ifcgeom/conversion_result.h"

namespace ifcopenshell { namespace geom {

	using ifcopenshell::geom::opaque_coordinate;
	using ifcopenshell::geom::opaque_number;

#ifndef IFOPSH_SIMPLE_KERNEL
	class IFC_GEOMLIBRARY_API number_epeck : public opaque_number {
	private:
		struct model : opaque_number::number_concept {
			CGAL::Epeck::FT value;

			model(const CGAL::Epeck::FT& v)
				: value(v) {}

			static const model& as_same(const number_concept& other) {
				auto same = dynamic_cast<const model*>(&other);
				if (same == nullptr) {
					throw std::runtime_error("Incompatible opaque number types");
				}
				return *same;
			}

			virtual double to_double() const {
				return CGAL::to_double(value);
			}

			virtual std::string to_string() const {
				std::stringstream ss;
				ss << value.exact();
				return ss.str();
			}

			virtual std::shared_ptr<const number_concept> add(const number_concept& other) const {
				return std::make_shared<model>(value + as_same(other).value);
			}

			virtual std::shared_ptr<const number_concept> subtract(const number_concept& other) const {
				return std::make_shared<model>(value - as_same(other).value);
			}

			virtual std::shared_ptr<const number_concept> multiply(const number_concept& other) const {
				return std::make_shared<model>(value * as_same(other).value);
			}

			virtual std::shared_ptr<const number_concept> divide(const number_concept& other) const {
				return std::make_shared<model>(value / as_same(other).value);
			}

			virtual std::shared_ptr<const number_concept> negate() const {
				return std::make_shared<model>(-value);
			}

			virtual std::shared_ptr<const number_concept> from_double(double v) const {
				return std::make_shared<model>(CGAL::Epeck::FT(v));
			}

			virtual std::shared_ptr<const number_concept> from_int(int v) const {
                return std::make_shared<model>(CGAL::Epeck::FT(v));
            }

			virtual bool equals(const number_concept& other) const {
				return value == as_same(other).value;
			}

			virtual bool less_than(const number_concept& other) const {
				return value < as_same(other).value;
			}

			virtual const std::type_info& type() const {
				return typeid(CGAL::Epeck::FT);
			}

			virtual const void* value_ptr() const {
				return &value;
			}
		};

	public:
		number_epeck(const CGAL::Epeck::FT& v)
			: opaque_number(std::make_shared<model>(v)) {}

		const CGAL::Epeck::FT& value() const {
			return value_as<CGAL::Epeck::FT>();
		}
	};
#endif

	class IFC_GEOMLIBRARY_API cgal_shape : public ifcopenshell::geom::conversion_result_shape {
	private:
		typedef std::variant<cgal_polyhedron, cgal_point, cgal_wire> cgal_shape_storage;

		bool convex_tag_ = false;
		mutable std::optional<cgal_shape_storage> shape_;
#ifndef IFOPSH_SIMPLE_KERNEL
		mutable std::optional<CGAL::Nef_polyhedron_3<kernel_>> nef_;
#endif
      public:

		cgal_shape(const cgal_polyhedron& shape, bool convex = false, ifcopenshell::logger& logger = ifcopenshell::logger::root());
		cgal_shape(const cgal_point& point, bool convex = false);
		cgal_shape(const cgal_wire& wire, bool convex = false);

#ifndef IFOPSH_SIMPLE_KERNEL
		cgal_shape(const CGAL::Nef_polyhedron_3<kernel_>& shape, bool convex = false) {
			nef_ = shape;
			convex_tag_ = convex;
		}
#endif

#ifndef IFOPSH_SIMPLE_KERNEL
		void to_poly() const;

		void to_nef() const;

		operator const CGAL::Nef_polyhedron_3<kernel_>& () const { to_nef(); return *nef_; }
		const CGAL::Nef_polyhedron_3<kernel_>& nef() const { to_nef(); return *nef_; }
#else
		// noop on simple kernel
		void to_poly() const {}
#endif

		virtual std::string_view backend_id() const {
#ifdef IFOPSH_SIMPLE_KERNEL
			return "cgal-simple";
#else
			return "cgal";
#endif
		}
		operator const cgal_polyhedron& () const { return poly(); }
		const cgal_polyhedron& poly() const;
		bool is_poly() const { return shape_ && std::holds_alternative<cgal_polyhedron>(*shape_); }
		bool is_point() const { return shape_ && std::holds_alternative<cgal_point>(*shape_); }
		bool is_wire() const { return shape_ && std::holds_alternative<cgal_wire>(*shape_); }
		const cgal_point& point() const { return std::get<cgal_point>(*shape_); }
		const cgal_wire& wire() const { return std::get<cgal_wire>(*shape_); }

		virtual void triangulate(ifcopenshell::geom::settings settings, const ifcopenshell::geom::taxonomy::matrix4& place, ifcopenshell::geom::triangulation* t, int item_id, int surface_style_id, ifcopenshell::logger& logger = ifcopenshell::logger::root()) const;
		virtual void serialize(const ifcopenshell::geom::taxonomy::matrix4& place, std::string&) const;

		virtual ifcopenshell::geom::conversion_result_shape* clone() const {
			if (shape_) {
				return std::visit([this](const auto& value) -> ifcopenshell::geom::conversion_result_shape* {
					return new cgal_shape(value, convex_tag_);
				}, *shape_);
			}
#ifndef IFOPSH_SIMPLE_KERNEL
			if (nef_) {
				return new cgal_shape(*nef_, convex_tag_);
			}
#endif
			return nullptr;
		}

		virtual bool is_manifold() const;

		virtual double bounding_box(void*&) const;

		virtual int num_vertices() const;

		virtual void set_box(void*);

		virtual int surface_genus() const;

		virtual int num_edges() const;
		virtual int num_faces() const;

		// @todo this must be something with a virtual dtor so that we can delete it.
		virtual std::pair<opaque_coordinate<3>, opaque_coordinate<3>> bounding_box() const;

		virtual opaque_number length();
		virtual opaque_number area();
		virtual opaque_number volume();

		virtual opaque_coordinate<3> position();
		virtual opaque_coordinate<3> axis();
		virtual opaque_coordinate<4> plane_equation();

		virtual std::vector<conversion_result_shape*> convex_decomposition();
		virtual conversion_result_shape* halfspaces();
		virtual conversion_result_shape* solid();
		virtual conversion_result_shape* box();
		virtual conversion_result_shape* wrap_in_compound();

		virtual std::vector<conversion_result_shape*> vertices();
		virtual std::vector<conversion_result_shape*> edges();
		virtual std::vector<conversion_result_shape*> facets();

		virtual conversion_result_shape* add(conversion_result_shape*);
		virtual conversion_result_shape* subtract(conversion_result_shape*);
		virtual conversion_result_shape* intersect(conversion_result_shape*);
		virtual conversion_result_shape* concat(conversion_result_shape*);

		virtual std::size_t map(opaque_coordinate<4>& from, opaque_coordinate<4>& to);
		virtual std::size_t map(const std::vector<opaque_coordinate<4>>& from, const std::vector<opaque_coordinate<4>>& to);
		virtual conversion_result_shape* moved(ifcopenshell::geom::taxonomy::matrix4::ptr) const;

		virtual bool surface_area_along_direction(double tol, const ifcopenshell::geom::taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const;

		bool convex_tag() const { return convex_tag_; }
		bool& convex_tag() { return convex_tag_; }
	};

#ifndef IFOPSH_SIMPLE_KERNEL
	class IFC_GEOMLIBRARY_API cgal_shape_half_space_decomposition : public ifcopenshell::geom::conversion_result_shape {
	private:
		std::unique_ptr<halfspace_tree<kernel_>> shape_;
		std::list<CGAL::Plane_3<kernel_>> planes_;

	public:
		cgal_shape_half_space_decomposition(const CGAL::Nef_polyhedron_3<kernel_>& shape, bool is_convex) {
			if (is_convex) {
				shape_ = std::move(build_halfspace_tree_is_decomposed(shape, planes_));
			} else {
				shape_ = std::move(build_halfspace_tree_decomposed(shape, planes_));
			}
		}

		cgal_shape_half_space_decomposition(const CGAL::Plane_3<kernel_>& shape) {
			shape_.reset(new halfspace_tree_plane<kernel_>(shape));
			planes_.push_back(shape);
		}
		virtual std::string_view backend_id() const {
#ifdef IFOPSH_SIMPLE_KERNEL
			return "cgal-simple";
#else
			return "cgal";
#endif
		}

		virtual void triangulate(ifcopenshell::geom::settings settings, const ifcopenshell::geom::taxonomy::matrix4& place, ifcopenshell::geom::triangulation* t, int item_id, int surface_style_id, ifcopenshell::logger& logger = ifcopenshell::logger::root()) const;
		virtual void serialize(const ifcopenshell::geom::taxonomy::matrix4& place, std::string&) const;

		virtual int surface_genus() const;
		virtual bool is_manifold() const;

		virtual int num_vertices() const;
		virtual int num_edges() const;
		virtual int num_faces() const;

		virtual double bounding_box(void*&) const;

		// @todo this must be something with a virtual dtor so that we can delete it.
		virtual std::pair<opaque_coordinate<3>, opaque_coordinate<3>> bounding_box() const;
		virtual void set_box(void* b);

		virtual opaque_number length();
		virtual opaque_number area();
		virtual opaque_number volume();

		virtual opaque_coordinate<3> position();
		virtual opaque_coordinate<3> axis();
		virtual opaque_coordinate<4> plane_equation();

		virtual std::vector<conversion_result_shape*> convex_decomposition();
		virtual conversion_result_shape* halfspaces();
		virtual conversion_result_shape* solid();
		virtual conversion_result_shape* box();
		virtual conversion_result_shape* wrap_in_compound();

		virtual std::vector<conversion_result_shape*> vertices();
		virtual std::vector<conversion_result_shape*> edges();
		virtual std::vector<conversion_result_shape*> facets();

		virtual conversion_result_shape* add(conversion_result_shape*);
		virtual conversion_result_shape* subtract(conversion_result_shape*);
		virtual conversion_result_shape* intersect(conversion_result_shape*);
		virtual conversion_result_shape* concat(conversion_result_shape*) {
			return nullptr;
		}

		virtual std::size_t map(opaque_coordinate<4>& from, opaque_coordinate<4>& to);
		virtual std::size_t map(const std::vector<opaque_coordinate<4>>& from, const std::vector<opaque_coordinate<4>>& to);
		virtual conversion_result_shape* moved(ifcopenshell::geom::taxonomy::matrix4::ptr) const;

		virtual bool surface_area_along_direction(double tol, const ifcopenshell::geom::taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const {
			return false;
		}
	};
#endif
}}

#ifdef IFOPSH_SIMPLE_KERNEL
#undef cgal_shape
#endif

#endif
