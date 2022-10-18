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

#ifndef ITERATOR_IMPLEMENTATION_H
#define ITERATOR_IMPLEMENTATION_H

#include "../ifcparse/IfcFile.h"

#include "../ifcgeom_schema_agnostic/IfcGeomFilter.h"
#include "../ifcgeom_schema_agnostic/GeometrySerializer.h"
#include "../ifcgeom_schema_agnostic/IfcGeomIteratorSettings.h"

#include <gp_XYZ.hxx>

#include <boost/function.hpp>

#include <map>
#include <string>

namespace IfcGeom {
	class IteratorImplementation;

	class Element;

	class BRepElement;
}

typedef boost::function4<IfcGeom::IteratorImplementation*, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*, const std::vector<IfcGeom::filter_t>&, int> iterator_fn;

class IFC_GEOM_API IteratorFactoryImplementation : public std::map<std::string, iterator_fn> {
public:
	IteratorFactoryImplementation();
	void bind(const std::string& schema_name, iterator_fn fn);
	IfcGeom::IteratorImplementation* construct(const std::string& schema_name, const IfcGeom::IteratorSettings&, IfcParse::IfcFile*, const std::vector<IfcGeom::filter_t>&, int);
};

IFC_GEOM_API IteratorFactoryImplementation& iterator_implementations();

namespace IfcGeom {

	class IteratorImplementation {
	protected:
		GeometrySerializer* cache_ = nullptr;
	public:
		void set_cache(GeometrySerializer* cache) { cache_ = cache; }

		virtual bool initialize() = 0;
		virtual void compute_bounds(bool with_geometry) = 0;
		virtual const gp_XYZ& bounds_min() const = 0;
		virtual const gp_XYZ& bounds_max() const = 0;
		virtual int progress() const = 0;
		virtual const std::string& getUnitName() const = 0;
		virtual double getUnitMagnitude() const = 0;
		virtual IfcParse::IfcFile* file() const = 0;
		virtual IfcUtil::IfcBaseClass* next() = 0;
		virtual Element* get() = 0;
		virtual BRepElement* get_native() = 0;
		virtual const Element* get_object(int id) = 0;
		virtual IfcUtil::IfcBaseClass* create() = 0;
	};

}

#endif
