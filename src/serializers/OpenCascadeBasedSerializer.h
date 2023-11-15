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

#ifdef IFOPSH_WITH_OPENCASCADE

#ifndef OPENCASCADEBASEDSERIALIZER_H
#define OPENCASCADEBASEDSERIALIZER_H

#include "../serializers/serializers_api.h"
#include "../ifcgeom/Iterator.h"

#include "../ifcgeom/GeometrySerializer.h"

#include <TopoDS_Shape.hxx>

class SERIALIZERS_API OpenCascadeBasedSerializer : public WriteOnlyGeometrySerializer {
	OpenCascadeBasedSerializer(const OpenCascadeBasedSerializer&); //N/A
	OpenCascadeBasedSerializer& operator =(const OpenCascadeBasedSerializer&); //N/A
protected:
	const std::string out_filename;
	const char* getSymbolForUnitMagnitude(float mag);
public:
	explicit OpenCascadeBasedSerializer(const std::string& out_filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings)
		: WriteOnlyGeometrySerializer(geometry_settings, settings)
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
#endif
