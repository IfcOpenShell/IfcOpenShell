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

class WaveFrontOBJSerializer : public GeometrySerializer {
private:
	const std::string mtl_filename;
	std::ofstream obj_stream;
	std::ofstream mtl_stream;
	unsigned int vcount_total;
	std::set<std::string> materials;
public:
	WaveFrontOBJSerializer(const std::string& obj_filename, const std::string& mtl_filename, const IfcGeom::IteratorSettings &settings)
		: GeometrySerializer(settings)
		, obj_stream(obj_filename.c_str())
		, mtl_filename(mtl_filename)
		, mtl_stream(mtl_filename.c_str())		
		, vcount_total(1)
	{}
	virtual ~WaveFrontOBJSerializer() {}
	bool ready();
	void writeHeader();
	void writeMaterial(const IfcGeom::Material& style);
	void write(const IfcGeom::TriangulationElement<double>* o);
	void write(const IfcGeom::BRepElement<double>* /*o*/) {}
	void finalize() {}
	bool isTesselated() const { return true; }
	void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(IfcParse::IfcFile*) {}
};

#endif
