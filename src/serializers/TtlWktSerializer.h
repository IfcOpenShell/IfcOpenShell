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

#ifndef TTLWKTSERIALIZER_H
#define TTLWKTSERIALIZER_H

#include <set>
#include <string>
#include <fstream>

#include "../serializers/serializers_api.h"
#include "../ifcgeom/GeometrySerializer.h"

 // http://people.sc.fsu.edu/~jburkardt/txt/obj_format.txt
class SERIALIZERS_API TtlWktSerializer : public WriteOnlyGeometrySerializer {
private:
	stream_or_filename filename_;
public:
	TtlWktSerializer(const stream_or_filename& filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings);
	virtual ~TtlWktSerializer() {}
	bool ready();
	void writeHeader();
	void write(const IfcGeom::TriangulationElement* o);
	void write(const IfcGeom::BRepElement* /*o*/);
	void finalize() {}
	bool isTesselated() const;
	void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(IfcParse::IfcFile*) {}
	std::string ttl_object_id(const IfcGeom::Element* o, const char* const postfix = nullptr);
};

#endif
