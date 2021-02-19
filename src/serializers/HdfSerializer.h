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

#ifndef HdfSERIALIZER_H
#define HdfSERIALIZER_H

#include <set>
#include <string>
#include <fstream>

#include "H5Cpp.h"

#include "../serializers/GeometrySerializer.h"

// http://people.sc.fsu.edu/~jburkardt/txt/obj_format.txt
class HdfSerializer : public GeometrySerializer {
private:
	const std::string hdf_filename;
	unsigned int vcount_total;
	H5::H5File file;
	std::set<std::string> guids;
	std::vector<double> double_data_container;
	std::vector<int> int_data_container;
	const H5std_string  DATASET_NAME_POSITIONS;
	const H5std_string  DATASET_NAME_NORMALS;
	const H5std_string  DATASET_NAME_INDICES;
	const H5std_string  DATASET_NAME_OCCT;
	H5::CompType mtype1;
	H5::CompType mtype2;
	H5::CompType mtype3;

	
public:
	HdfSerializer(const std::string& hdf_filename, const SerializerSettings& settings);
	virtual ~HdfSerializer() {}
	bool ready();
	void writeHeader();
	void write(const IfcGeom::BRepElement<real_t>* o);
	void write(const IfcGeom::TriangulationElement<real_t>* /*o*/) {}
	void finalize() {}
	bool isTesselated() const { return false; }
	void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(IfcParse::IfcFile*) {}
};

#endif
