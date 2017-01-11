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

#ifndef OPENCASCADEBASEDSERIALIZER_H
#define OPENCASCADEBASEDSERIALIZER_H

#include "../ifcgeom/IfcGeomIterator.h"

#include "../ifcconvert/GeometrySerializer.h"

class OpenCascadeBasedSerializer : public GeometrySerializer {
	OpenCascadeBasedSerializer(const OpenCascadeBasedSerializer&); //N/A
	OpenCascadeBasedSerializer& operator =(const OpenCascadeBasedSerializer&); //N/A
protected:
	const std::string out_filename;
	const char* getSymbolForUnitMagnitude(float mag);
public:
	explicit OpenCascadeBasedSerializer(const std::string& out_filename, const SerializerSettings& settings)
		: GeometrySerializer(settings)
		, out_filename(out_filename)
	{}
	virtual ~OpenCascadeBasedSerializer() {}
	void writeHeader() {}
	bool ready();
	virtual void writeShape(const TopoDS_Shape& shape) = 0;
	void write(const IfcGeom::TriangulationElement<real_t>* /*o*/) {}
	void write(const IfcGeom::BRepElement<real_t>* o);
	bool isTesselated() const { return false; }
	void setFile(IfcParse::IfcFile*) {}
};

#endif
