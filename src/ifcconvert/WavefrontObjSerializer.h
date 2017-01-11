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

#include "../ifcconvert/GeometrySerializer.h"

// http://people.sc.fsu.edu/~jburkardt/txt/obj_format.txt
class WaveFrontOBJSerializer : public GeometrySerializer {
private:
	const std::string mtl_filename;
	std::ofstream obj_stream;
	std::ofstream mtl_stream;
	unsigned int vcount_total;
	std::set<std::string> materials;
public:
	WaveFrontOBJSerializer(const std::string& obj_filename, const std::string& mtl_filename, const SerializerSettings& settings)
		: GeometrySerializer(settings)
		, mtl_filename(mtl_filename)
		, obj_stream(obj_filename.c_str())
		, mtl_stream(mtl_filename.c_str())
		, vcount_total(1)
    {
        obj_stream << std::setprecision(settings.precision);
        mtl_stream << std::setprecision(settings.precision);
    }

	virtual ~WaveFrontOBJSerializer() {}
	bool ready();
	void writeHeader();
	void writeMaterial(const IfcGeom::Material& style);
	void write(const IfcGeom::TriangulationElement<real_t>* o);
	void write(const IfcGeom::BRepElement<real_t>* /*o*/) {}
	void finalize() {}
	bool isTesselated() const { return true; }
	void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(IfcParse::IfcFile*) {}
};

#endif
