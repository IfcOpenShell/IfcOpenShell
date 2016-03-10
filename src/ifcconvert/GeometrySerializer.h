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

#ifndef GEOMETRYSERIALIZER_H
#define GEOMETRYSERIALIZER_H

#ifdef IFCCONVERT_DOUBLE_PRECISION
typedef double real_t;
#else
typedef float real_t;
#endif

#include "../ifcconvert/Serializer.h"
#include "../ifcgeom/IfcGeomIterator.h"

class GeometrySerializer : public Serializer {
public:
    GeometrySerializer(const IfcGeom::IteratorSettings &settings) : settings_(settings) {}
	virtual ~GeometrySerializer() {} 

	virtual bool isTesselated() const = 0;
	virtual void write(const IfcGeom::TriangulationElement<real_t>* o) = 0;
	virtual void write(const IfcGeom::BRepElement<real_t>* o) = 0;
	virtual void setUnitNameAndMagnitude(const std::string& name, float magnitude) = 0;

    const IfcGeom::IteratorSettings& settings() const { return settings_; }
    IfcGeom::IteratorSettings& settings() { return settings_; }

protected:
    IfcGeom::IteratorSettings settings_;
};

#endif
