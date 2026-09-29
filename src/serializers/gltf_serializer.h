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
#include "../ifcgeom/geometry_serializer.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

#include <map>

class SERIALIZERS_API gltf_serializer : public ifcopenshell::geom::write_only_geometry_serializer {
private:
	std::string filename_, tmp_filename1_, tmp_filename2_;
	std::ofstream fstream_, tmp_fstream1_, tmp_fstream2_;
	std::map<std::string, int> materials_, meshes_;
	json json_, node_array_;
	std::optional<json> ecef_transform_, north_rotation_, z_up_transform_;
	int bufferViewId;
    std::map<express::base, size_t> node_indices_;
    std::vector<size_t> roots_;

	int writeMaterial(const ifcopenshell::geom::taxonomy::style::ptr style);
	void setup_georeferencing(
		const std::optional<std::string>& crs_epsg,
		const std::optional<std::array<double, 3>>& eastings_northings_elevation,
		std::optional<std::array<double, 3>> crs_x_axis);
public:
	gltf_serializer(const std::string& filename, const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr);
	virtual ~gltf_serializer();
	bool ready();
	void writeHeader();
	void write(const ifcopenshell::geom::triangulation_element* o);
	void write(const ifcopenshell::geom::native_element* /*o*/) {}
	void finalize();
	bool isTesselated() const { return true; }
	void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(ifcopenshell::file&);
};

#endif

#endif
