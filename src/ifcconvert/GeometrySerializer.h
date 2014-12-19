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

#include "../ifcgeom/IfcGeomIterator.h"

class GeometrySerializer {
public:
	virtual bool ready() = 0;
	virtual void writeHeader() = 0;
	virtual void finalize() = 0;
	virtual bool isTesselated() const = 0;
	virtual ~GeometrySerializer() {} 
	virtual void write(const IfcGeom::TriangulationElement<double>* o) = 0;
	virtual void write(const IfcGeom::ShapeModelElement<double>* o) = 0;
	virtual void setUnitNameAndMagnitude(const std::string& name, float magnitude) = 0;
};

#endif