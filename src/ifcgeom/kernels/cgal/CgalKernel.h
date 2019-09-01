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

#ifndef CGAL_KERNEL_H
#define CGAL_KERNEL_H

/*
#ifdef NO_CACHE

#define IN_CACHE(T,E,t,e)
#define CACHE(T,E,e)

#else

#define IN_CACHE(T,E,t,e) std::map<int,t>::const_iterator it = cache.T.find(E->entity->id());\
if ( it != cache.T.end() ) { e = it->second; return true; }
#define CACHE(T,E,e) cache.T[E->entity->id()] = e;

#endif
*/

#include <cmath>

#define ALMOST_ZERO 1.e-9

template <typename T>
inline static bool ALMOST_THE_SAME(const T& a, const T& b, double tolerance=ALMOST_ZERO) {
        return fabs(a-b) < tolerance;
}

#include "../../../ifcparse/macros.h"

#include "../../../ifcgeom/kernel_agnostic/AbstractKernel.h"

#include "../../../ifcgeom/schema_agnostic/IfcGeomElement.h"
#include "../../../ifcgeom/kernels/cgal/CgalConversionResult.h"

// @todo create separate shapetype enum?
#include "../../../ifcgeom/kernels/opencascade/IfcGeomShapeType.h"

struct PolyhedronBuilder : public CGAL::Modifier_base<CGAL::Polyhedron_3<Kernel_>::HalfedgeDS> {
private:
  std::list<cgal_face_t> *face_list;
public:
  PolyhedronBuilder(std::list<cgal_face_t> *face_list) {
    this->face_list = face_list;
  }
  
  void operator()(CGAL::Polyhedron_3<Kernel_>::HalfedgeDS &hds) {
    std::list<Kernel_::Point_3> points;
    std::list<std::list<std::size_t>> facet_vertices;
    CGAL::Polyhedron_incremental_builder_3<CGAL::Polyhedron_3<Kernel_>::HalfedgeDS> builder(hds, true);
    
    for (auto &face: *face_list) {
      facet_vertices.push_back(std::list<std::size_t>());
      for (auto &point: face.outer) {
        facet_vertices.back().push_back(points.size());
        points.push_back(point);
      }
    }
    
    builder.begin_surface(points.size(), facet_vertices.size());
    
    for (auto &point: points) {
//      std::cout << "Adding point " << point << std::endl;
      builder.add_vertex(point);
    }
    
    for (auto &facet: facet_vertices) {
      builder.begin_facet();
//      std::cout << "Adding facet ";
      for (auto &vertex: facet) {
//        std::cout << vertex << " ";
        builder.add_vertex_to_facet(vertex);
      }
//      std::cout << std::endl;
      builder.end_facet();
    }
    
    builder.end_surface();
  }
};

namespace ifcopenshell {
namespace geometry {
namespace kernels {

	class IFC_GEOM_API CgalKernel : public AbstractKernel {
	public:

		CgalKernel()
			: AbstractKernel("cgal") {}

		void remove_duplicate_points_from_loop(cgal_wire_t& polygon);

		CGAL::Polyhedron_3<Kernel_> create_polyhedron(std::list<cgal_face_t> &face_list);
		CGAL::Polyhedron_3<Kernel_> create_polyhedron(CGAL::Nef_polyhedron_3<Kernel_> &nef_polyhedron);
		CGAL::Nef_polyhedron_3<Kernel_> create_nef_polyhedron(std::list<cgal_face_t> &face_list);
		CGAL::Nef_polyhedron_3<Kernel_> create_nef_polyhedron(CGAL::Polyhedron_3<Kernel_> &polyhedron);

		bool convert(const taxonomy::face*, cgal_face_t&);
		bool convert(const taxonomy::loop*, cgal_wire_t&);
		bool convert(const taxonomy::shell* l, cgal_shape_t& shape);

		virtual bool convert_impl(const taxonomy::shell*, ifcopenshell::geometry::ConversionResults&);
		virtual bool convert_impl(const taxonomy::extrusion*, ifcopenshell::geometry::ConversionResults&);
	};

}
}
}
#endif