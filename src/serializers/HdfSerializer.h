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

#ifndef HDFSERIALIZER_H
#define HDFSERIALIZER_H

#if defined(WITH_HDF5) && defined(IFOPSH_WITH_OPENCASCADE)

#include <set>
#include <string>
#include <fstream>

#include "H5Cpp.h"

#include "../serializers/serializers_api.h"
#include "../ifcgeom/GeometrySerializer.h"

#define USE_BINARY

class SERIALIZERS_API HdfSerializer : public GeometrySerializer {
private:
	const std::string hdf_filename;
	unsigned int vcount_total;
	H5::H5File file;
	ifcopenshell::geometry::SerializerSettings settings_;

	static const H5std_string DATASET_NAME_POSITIONS;
	static const H5std_string DATASET_NAME_UVCOORDS;
	static const H5std_string DATASET_NAME_NORMALS;
	static const H5std_string DATASET_NAME_INDICES;
	static const H5std_string DATASET_NAME_EDGES;
	static const H5std_string DATASET_NAME_MATERIAL_IDS;
	static const H5std_string DATASET_NAME_ITEM_IDS;
	static const H5std_string DATASET_NAME_MATERIALS;
	static const H5std_string DATASET_NAME_OCCT;
	static const H5std_string DATASET_NAME_PLACEMENT;	

	static const H5std_string GROUP_NAME_MESH;

	struct surface_style_serialization {
		const char* name;
		const char* original_name;
		// 0 if unset
		unsigned int id;
		// nan if unset
		double diffuse[3];
		double specular[3];
		double transparency;
		double specularity;
	};

	struct brep_element {
		int id;
		double matrix[4][4];
#ifdef USE_BINARY
		hvl_t shape_serialization;
#else
		const char* shape_serialization;
#endif
		surface_style_serialization surface_style;
	};

	H5::CompType compound;
	H5::CompType style_compound;
	H5::StrType str_type;
	H5::ArrayType double4x4, double3;
	H5::DataType shape_type;

private:

	std::map<std::string, boost::shared_ptr<IfcGeom::Representation::BRep>> brep_cache_;
	std::map<std::string, boost::shared_ptr<IfcGeom::Representation::Triangulation>> triangulation_cache_;
	std::map<std::string, std::string> group_cache_;

	H5::Group createRepresentationGroup(const H5::Group& element_group, const std::string& gid);
	void read_surface_style(surface_style_serialization& sss, const ifcopenshell::geometry::taxonomy::style::ptr& style_ptr);
	void write_style(surface_style_serialization& data, const ifcopenshell::geometry::taxonomy::style::ptr& s);

public:
	HdfSerializer(const std::string& hdf_filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings, bool read_only=false);
	virtual ~HdfSerializer() {}
	bool ready();
	void writeHeader();

	H5::Group write(const IfcGeom::Element* o);
	void write(const IfcGeom::BRepElement* o);
	void write(const IfcGeom::TriangulationElement* o);
	void remove(const std::string& guid);

	IfcGeom::Element* read(IfcParse::IfcFile& f, const std::string& guid, const std::string&, read_type rt = READ_BREP);
	
	void finalize() {}
	bool isTesselated() const { return false; }
	void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(IfcParse::IfcFile*) {}
};

#endif

#endif
