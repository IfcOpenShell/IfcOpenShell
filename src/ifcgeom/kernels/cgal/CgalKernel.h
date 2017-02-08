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

#include "../../../ifcgeom/IfcGeom.h"

#undef Handle

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Polyhedron_3.h>

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel;

typedef Kernel::Aff_transformation_3 cgal_placement_t;
typedef Kernel::Point_3 cgal_point_t;
typedef Kernel::Vector_3 cgal_direction_t;
typedef std::vector<Kernel::Point_3> cgal_curve_t;
typedef std::vector<Kernel::Point_3> cgal_wire_t;

struct cgal_face_t {
  cgal_wire_t outer;
  std::vector<cgal_wire_t> inner;
};

typedef CGAL::Polyhedron_3<Kernel> cgal_shape_t;

struct PolyhedronBuilder : public CGAL::Modifier_base<CGAL::Polyhedron_3<Kernel>::HalfedgeDS> {
private:
  std::list<cgal_face_t> *face_list;
public:
  PolyhedronBuilder(std::list<cgal_face_t> *face_list) {
    this->face_list = face_list;
  }
  
  void operator()(CGAL::Polyhedron_3<Kernel>::HalfedgeDS &hds) {
    std::map<Kernel::Point_3, std::size_t> points_map;
    std::list<std::list<std::size_t>> facet_vertices;
    CGAL::Polyhedron_incremental_builder_3<CGAL::Polyhedron_3<Kernel>::HalfedgeDS> builder(hds, true);
    
    for (auto const &face: *face_list) {
      facet_vertices.push_back(std::list<std::size_t>());
      for (auto const &point: face.outer) {
        if (points_map.count(point) == 0) {
          facet_vertices.back().push_back(points_map.size());
          points_map[point] = points_map.size();
        } else {
          facet_vertices.back().push_back(points_map[point]);
        }
      }
    }
    
    builder.begin_surface(points_map.size(), facet_vertices.size());
    
    for (auto const &point: points_map) {
//      std::cout << "Adding point " << point.first << std::endl;
      builder.add_vertex(point.first);
    }
    
    for (auto const &facet: facet_vertices) {
      builder.begin_facet();
//      std::cout << "Adding facet ";
      for (auto const &vertex: facet) {
//        std::cout << vertex << " ";
        builder.add_vertex_to_facet(vertex);
      }
//      std::cout << std::endl;
      builder.end_facet();
    }
    
    builder.end_surface();
  }
};

namespace IfcGeom {

	class IFC_GEOM_API CgalCache {
	public:
#include "CgalEntityMappingCreateCache.h"
		std::map<int, cgal_shape_t> Shape;
	};

	class IFC_GEOM_API CgalKernel : public AbstractKernel {
	public:

#ifndef NO_CACHE
		CgalCache cache;
#endif

		IfcGeom::ShapeType shape_type(const IfcUtil::IfcBaseClass* L);

		bool convert_shapes(const IfcUtil::IfcBaseClass* L, ConversionResults& result);
		bool convert_shape(const IfcUtil::IfcBaseClass* L, cgal_shape_t& result);
		bool convert_wire(const IfcUtil::IfcBaseClass* L, cgal_wire_t& result);
		bool convert_curve(const IfcUtil::IfcBaseClass* L, cgal_curve_t& result);
		bool convert_face(const IfcUtil::IfcBaseClass* L, cgal_face_t& result);

		// bool convert_openings(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const ConversionResults& entity_shapes, const gp_Trsf& entity_trsf, ConversionResults& cut_shapes);

		void purge_cache() {
			// Rather hack-ish, but a stopgap solution to keep memory under control
			// for large files. SurfaceStyles need to be kept at all costs, as they
			// are read later on when serializing Collada files.
#ifndef NO_CACHE
			cache = CgalCache();
#endif
		}

		virtual bool is_identity_transform(IfcUtil::IfcBaseClass*);
		virtual IfcGeom::NativeElement<double>* create_brep_for_representation_and_product(
			const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*);
		virtual IfcGeom::NativeElement<double>* create_brep_for_processed_representation(
			const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*, IfcGeom::NativeElement<double>*);

#include "CgalEntityMappingDeclaration.h"

	};

}

#endif
