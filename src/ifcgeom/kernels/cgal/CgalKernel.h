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

typedef void* cgal_shape_t;
typedef void* cgal_face_t;
typedef void* cgal_wire_t;
typedef void* cgal_curve_t;
typedef void* cgal_placement_t;
typedef void* cgal_point_t;

namespace IfcGeom {

	class IFC_GEOM_API CgalCache {
	public:
#include "CgalEntityMappingCreateCache.h"
		std::map<int, cgal_shape_t> Shape;
	};

	class IFC_GEOM_API MAKE_TYPE_NAME(CgalKernel) : public Kernel {
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