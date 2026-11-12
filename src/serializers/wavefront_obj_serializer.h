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

#ifndef WAVEFRONTOBJSERIALIZER_H
#define WAVEFRONTOBJSERIALIZER_H

#include <set>
#include <string>
#include <fstream>

#include "../serializers/serializers_api.h"
#include "../ifcgeom/geometry_serializer.h"

// http://people.sc.fsu.edu/~jburkardt/txt/obj_format.txt
class SERIALIZERS_API wavefront_obj_serializer : public ifcopenshell::geom::write_only_geometry_serializer {
private:
	stream_or_filename obj_stream;
	stream_or_filename mtl_stream;
	size_t vcount_total, ncount_total;
	std::set<std::string> materials;
public:
	wavefront_obj_serializer(const stream_or_filename& obj_filename, const stream_or_filename& mtl_filename, const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr);
	virtual ~wavefront_obj_serializer() {}
	bool ready();
	void writeHeader();
	void writeMaterial(const ifcopenshell::geom::taxonomy::style::ptr style);
	void write(const ifcopenshell::geom::triangulation_element* o);
	void write(const ifcopenshell::geom::native_element* /*o*/) {}
	void finalize() {}
	bool isTesselated() const { return true; }
	void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(ifcopenshell::file&) {}
};

#endif
