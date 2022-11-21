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

#include "../serializers/serializers_api.h"
#include "../ifcgeom_schema_agnostic/IfcGeomIterator.h"

#include "../ifcgeom_schema_agnostic/GeometrySerializer.h"

class SERIALIZERS_API OpenCascadeBasedSerializer : public WriteOnlyGeometrySerializer {
	OpenCascadeBasedSerializer(const OpenCascadeBasedSerializer&); //N/A
	OpenCascadeBasedSerializer& operator =(const OpenCascadeBasedSerializer&); //N/A
protected:
	const std::string out_filename;
	const char* getSymbolForUnitMagnitude(float mag);
public:
	explicit OpenCascadeBasedSerializer(const std::string& out_filename, const SerializerSettings& settings)
		: WriteOnlyGeometrySerializer(settings)
		, out_filename(out_filename)
	{}
	virtual ~OpenCascadeBasedSerializer() {}
	void writeHeader() {}
	bool ready();
	virtual void writeShape(const std::string& name, const TopoDS_Shape& shape) = 0;
	void write(const IfcGeom::TriangulationElement* /*o*/) {}
	void write(const IfcGeom::BRepElement* o);
	bool isTesselated() const { return false; }
	void setFile(IfcParse::IfcFile*) {}
};

#endif
