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

#include "../../../ifcparse/macros.h"

#include "../../../ifcgeom/kernel_agnostic/AbstractKernel.h"

#include "../../../ifcgeom/schema_agnostic/Kernel.h"
#include "../../../ifcgeom/schema_agnostic/IfcGeomElement.h"
#include "../../../ifcgeom/schema_agnostic/cgal/CgalConversionResult.h"

// @todo create separate shapetype enum?
#include "../../../ifcgeom/kernels/opencascade/IfcGeomShapeType.h"

#define INCLUDE_SCHEMA(x) STRINGIFY(../../../ifcparse/x.h)
#include INCLUDE_SCHEMA(IfcSchema)
#undef INCLUDE_SCHEMA

namespace IfcGeom {

	class IFC_GEOM_API CgalCache {
	public:
#include "CgalEntityMappingCreateCache.h"
		std::map<int, cgal_shape_t> Shape;
	};

	class IFC_GEOM_API MAKE_TYPE_NAME(CgalKernel) : public MAKE_TYPE_NAME(AbstractKernel) {
	public:

		MAKE_TYPE_NAME(CgalKernel)()
			: MAKE_TYPE_NAME(AbstractKernel)("cgal") {}

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

		virtual bool is_identity_transform(const IfcUtil::IfcBaseClass*);
		virtual bool apply_layerset(const IfcSchema::IfcProduct* product, IfcGeom::ConversionResults& shapes);
		virtual bool validate_quantities(const IfcSchema::IfcProduct* product, const IfcGeom::Representation::BRep& brep);
		virtual bool convert_openings(const IfcSchema::IfcProduct* product, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const IfcGeom::ConversionResults& shapes, const ConversionResultPlacement* trsf, IfcGeom::ConversionResults& opened_shapes);

#include "CgalEntityMappingDeclaration.h"

	private:
		double deflection_tolerance;
		double dimensionality;
	};

}

#endif