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

#include <CGAL/Simple_cartesian.h>

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

typedef CGAL::Simple_cartesian<double> Kernel_; 

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

	class CgalShape : public IfcGeom::ConversionResultShape {
    public:
		CgalShape(const cgal_shape_t& shape)
			: shape_(shape) {}

		const cgal_shape_t& shape() const { return shape_; }
		operator const cgal_shape_t& () { return shape_; }

		virtual void Triangulate(const IfcGeom::IteratorSettings& settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int surface_style_id) const;
		
		virtual void Serialize(std::string&) const;

		virtual IfcGeom::ConversionResultShape* clone() const {
			return new CgalShape(shape_);
		}

		virtual bool is_manifold() const {
			throw std::runtime_error("Not implemented");
		}

		virtual double bounding_box(void*&) const;

		virtual int num_vertices() const;

		virtual void set_box(void*);

		virtual int surface_genus() const;

    private:
        cgal_shape_t shape_;
	};
    
}}

#endif
