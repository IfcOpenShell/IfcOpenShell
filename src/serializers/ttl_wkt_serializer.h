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
#include "../ifcgeom/geometry_serializer.h"

class SERIALIZERS_API ttl_wkt_serializer : public ifcopenshell::geom::write_only_geometry_serializer {
private:
	stream_or_filename filename_;
public:
	ttl_wkt_serializer(const stream_or_filename& filename, const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr);
	virtual ~ttl_wkt_serializer() {}
	bool ready();
	void writeHeader();
	void write(const ifcopenshell::geom::triangulation_element* o);
	void write(const ifcopenshell::geom::brep_element* /*o*/);
	void finalize() {}
	bool isTesselated() const;
	void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(ifcopenshell::file&) {}
	std::string ttl_object_id(const ifcopenshell::geom::element* o, const char* const postfix = nullptr);
};

#endif
