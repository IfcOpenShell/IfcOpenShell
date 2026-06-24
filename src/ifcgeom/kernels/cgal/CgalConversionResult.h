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

#include <variant>

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

#ifndef IFOPSH_SIMPLE_KERNEL
	class IFC_GEOMLIBRARY_API NumberEpeck : public OpaqueNumber {
	private:
		struct Model : OpaqueNumber::NumberConcept {
			CGAL::Epeck::FT value;

			Model(const CGAL::Epeck::FT& v)
				: value(v) {}

			static const Model& as_same(const NumberConcept& other) {
				auto same = dynamic_cast<const Model*>(&other);
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

			virtual std::shared_ptr<const NumberConcept> add(const NumberConcept& other) const {
				return std::make_shared<Model>(value + as_same(other).value);
			}

			virtual std::shared_ptr<const NumberConcept> subtract(const NumberConcept& other) const {
				return std::make_shared<Model>(value - as_same(other).value);
			}

			virtual std::shared_ptr<const NumberConcept> multiply(const NumberConcept& other) const {
				return std::make_shared<Model>(value * as_same(other).value);
			}

			virtual std::shared_ptr<const NumberConcept> divide(const NumberConcept& other) const {
				return std::make_shared<Model>(value / as_same(other).value);
			}

			virtual std::shared_ptr<const NumberConcept> negate() const {
				return std::make_shared<Model>(-value);
			}

			virtual std::shared_ptr<const NumberConcept> from_double(double v) const {
				return std::make_shared<Model>(CGAL::Epeck::FT(v));
			}

			virtual std::shared_ptr<const NumberConcept> from_int(int v) const {
                return std::make_shared<Model>(CGAL::Epeck::FT(v));
            }

			virtual bool equals(const NumberConcept& other) const {
				return value == as_same(other).value;
			}

			virtual bool less_than(const NumberConcept& other) const {
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
		NumberEpeck(const CGAL::Epeck::FT& v)
			: OpaqueNumber(std::make_shared<Model>(v)) {}

		const CGAL::Epeck::FT& value() const {
			return value_as<CGAL::Epeck::FT>();
		}
	};
#endif

	class IFC_GEOMLIBRARY_API CgalShape : public IfcGeom::ConversionResultShape {
	private:
		typedef std::variant<cgal_shape_t, cgal_point_t, cgal_wire_t> cgal_shape_storage_t;

		bool convex_tag_ = false;
		mutable boost::optional<cgal_shape_storage_t> shape_;
#ifndef IFOPSH_SIMPLE_KERNEL
		mutable boost::optional<CGAL::Nef_polyhedron_3<Kernel_>> nef_;
#endif
      public:
#ifdef IFOPSH_SIMPLE_KERNEL
        std::string type() const override { return "CgalSimpleShape"; }
#else
        std::string type() const override { return "CgalShape"; }
#endif

		CgalShape(const cgal_shape_t& shape, bool convex = false, Logger& logger = Logger::Root());
		CgalShape(const cgal_point_t& point, bool convex = false);
		CgalShape(const cgal_wire_t& wire, bool convex = false);

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

		operator const cgal_shape_t& () const { return poly(); }
		const cgal_shape_t& poly() const;
		bool is_poly() const { return shape_ && std::holds_alternative<cgal_shape_t>(*shape_); }
		bool is_point() const { return shape_ && std::holds_alternative<cgal_point_t>(*shape_); }
		bool is_wire() const { return shape_ && std::holds_alternative<cgal_wire_t>(*shape_); }
		const cgal_point_t& point() const { return std::get<cgal_point_t>(*shape_); }
		const cgal_wire_t& wire() const { return std::get<cgal_wire_t>(*shape_); }

		virtual void Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id, Logger& logger = Logger::Root()) const;
		virtual void Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string&) const;

		virtual IfcGeom::ConversionResultShape* clone() const {
			if (shape_) {
				return std::visit([this](const auto& value) -> IfcGeom::ConversionResultShape* {
					return new CgalShape(value, convex_tag_);
				}, *shape_);
			}
#ifndef IFOPSH_SIMPLE_KERNEL
			if (nef_) {
				return new CgalShape(*nef_, convex_tag_);
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
		virtual std::pair<OpaqueCoordinate<3>, OpaqueCoordinate<3>> bounding_box() const;

		virtual OpaqueNumber length();
		virtual OpaqueNumber area();
		virtual OpaqueNumber volume();

		virtual OpaqueCoordinate<3> position();
		virtual OpaqueCoordinate<3> axis();
		virtual OpaqueCoordinate<4> plane_equation();

		virtual std::vector<ConversionResultShape*> convex_decomposition();
		virtual ConversionResultShape* halfspaces();
		virtual ConversionResultShape* solid();
		virtual ConversionResultShape* box();
		virtual ConversionResultShape* wrap_in_compound();

		virtual std::vector<ConversionResultShape*> vertices();
		virtual std::vector<ConversionResultShape*> edges();
		virtual std::vector<ConversionResultShape*> facets();

		virtual ConversionResultShape* add(ConversionResultShape*);
		virtual ConversionResultShape* subtract(ConversionResultShape*);
		virtual ConversionResultShape* intersect(ConversionResultShape*);
		virtual ConversionResultShape* concat(ConversionResultShape*);

		virtual std::size_t map(OpaqueCoordinate<4>& from, OpaqueCoordinate<4>& to);
		virtual std::size_t map(const std::vector<OpaqueCoordinate<4>>& from, const std::vector<OpaqueCoordinate<4>>& to);
		virtual ConversionResultShape* moved(ifcopenshell::geometry::taxonomy::matrix4::ptr) const;

		virtual bool surface_area_along_direction(double tol, const ifcopenshell::geometry::taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const;

		bool convex_tag() const { return convex_tag_; }
		bool& convex_tag() { return convex_tag_; }
	};

#ifndef IFOPSH_SIMPLE_KERNEL
	class IFC_GEOMLIBRARY_API CgalShapeHalfSpaceDecomposition : public IfcGeom::ConversionResultShape {
	private:
		std::unique_ptr<halfspace_tree<Kernel_>> shape_;
		std::list<CGAL::Plane_3<Kernel_>> planes_;

	public:
        std::string type() const override { return "CgalShapeHalfSpaceDecomposition"; }

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

		virtual void Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id, Logger& logger = Logger::Root()) const;
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

		virtual OpaqueNumber length();
		virtual OpaqueNumber area();
		virtual OpaqueNumber volume();

		virtual OpaqueCoordinate<3> position();
		virtual OpaqueCoordinate<3> axis();
		virtual OpaqueCoordinate<4> plane_equation();

		virtual std::vector<ConversionResultShape*> convex_decomposition();
		virtual ConversionResultShape* halfspaces();
		virtual ConversionResultShape* solid();
		virtual ConversionResultShape* box();
		virtual ConversionResultShape* wrap_in_compound();

		virtual std::vector<ConversionResultShape*> vertices();
		virtual std::vector<ConversionResultShape*> edges();
		virtual std::vector<ConversionResultShape*> facets();

		virtual ConversionResultShape* add(ConversionResultShape*);
		virtual ConversionResultShape* subtract(ConversionResultShape*);
		virtual ConversionResultShape* intersect(ConversionResultShape*);
		virtual ConversionResultShape* concat(ConversionResultShape*) {
			return nullptr;
		}

		virtual std::size_t map(OpaqueCoordinate<4>& from, OpaqueCoordinate<4>& to);
		virtual std::size_t map(const std::vector<OpaqueCoordinate<4>>& from, const std::vector<OpaqueCoordinate<4>>& to);
		virtual ConversionResultShape* moved(ifcopenshell::geometry::taxonomy::matrix4::ptr) const;

		virtual bool surface_area_along_direction(double tol, const ifcopenshell::geometry::taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const {
			return false;
		}
	};
#endif
}}

#ifdef IFOPSH_SIMPLE_KERNEL
#undef CgalShape
#endif

#endif
