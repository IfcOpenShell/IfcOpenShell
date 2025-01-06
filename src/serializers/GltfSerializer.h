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

#ifndef GLTFSERIALIZER_H
#define GLTFSERIALIZER_H

#ifdef WITH_GLTF

#include "../serializers/serializers_api.h"
#include "../ifcgeom/GeometrySerializer.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

#include <map>

class SERIALIZERS_API GltfSerializer : public WriteOnlyGeometrySerializer {
private:
	std::string filename_, tmp_filename1_, tmp_filename2_;
	std::ofstream fstream_, tmp_fstream1_, tmp_fstream2_;
	std::map<std::string, int> materials_, meshes_;
	json json_, node_array_;
	boost::optional<json> ecef_transform_, north_rotation_;
	int bufferViewId;

	int writeMaterial(const ifcopenshell::geometry::taxonomy::style::ptr style);
public:
	GltfSerializer(const std::string& filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings);
	virtual ~GltfSerializer();
	bool ready();
	void writeHeader();
	void write(const IfcGeom::TriangulationElement* o);
	void write(const IfcGeom::BRepElement* /*o*/) {}
	void finalize();
	bool isTesselated() const { return true; }
	void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(IfcParse::IfcFile*);
};

#endif

#endif
