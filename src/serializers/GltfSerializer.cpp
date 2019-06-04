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

#ifdef WITH_GLTF

#include "GltfSerializer.h"

#include "../ifcparse/utils.h"

#include <iterator>

static const uint32_t GLTF = 0x46546C67U;
static const uint32_t JSON = 0x4E4F534A;
static const uint32_t BIN = 0x004E4942;

static const uint32_t CT_BYTE = 5120;
static const uint32_t CT_UNSIGNED_BYTE = 5121;
static const uint32_t CT_SHORT = 5122;
static const uint32_t CT_UNSIGNED_SHORT = 5123;
static const uint32_t CT_UNSIGNED_INT = 5125;
static const uint32_t CT_FLOAT = 5126;

static const uint32_t PRIM_POINTS = 0;
static const uint32_t PRIM_LINES = 1;
static const uint32_t PRIM_LINE_LOOP = 2;
static const uint32_t PRIM_LINE_STRIP = 3;
static const uint32_t PRIM_TRIANGLES = 4;
static const uint32_t PRIM_TRIANGLE_STRIP = 5;
static const uint32_t PRIM_TRIANGLE_FAN = 6;

GltfSerializer::GltfSerializer(const std::string& filename, const SerializerSettings& settings)
	: GeometrySerializer(settings)
	, filename_(filename)
	, tmp_filename1_(filename + ".indices.tmp")
	, tmp_filename2_(filename + ".vertices.tmp")
	, fstream_(IfcUtil::path::from_utf8(filename).c_str(), std::ios_base::binary)
	, tmp_fstream1_(IfcUtil::path::from_utf8(tmp_filename1_).c_str(), std::ios_base::binary)
	, tmp_fstream2_(IfcUtil::path::from_utf8(tmp_filename2_).c_str(), std::ios_base::binary)
	{}

GltfSerializer::~GltfSerializer() {
	tmp_fstream1_.close();
	tmp_fstream2_.close();
	IfcUtil::path::delete_file(tmp_filename1_);
	IfcUtil::path::delete_file(tmp_filename2_);
}

bool GltfSerializer::ready() {
	return fstream_.is_open() && tmp_fstream1_.is_open() && tmp_fstream2_.is_open();
}

void GltfSerializer::writeHeader() {
	json_["asset"]["generator"] = "IfcOpenShell IfcConvert " IFCOPENSHELL_VERSION;
	json_["asset"]["version"] = "2.0";
	json_["scene"] = 0;

	node_array_ = json::array();
	json_["accessors"] = json::array();
	json_["scenes"] = json::array();
	json_["nodes"] = json::array();
	json_["meshes"] = json::array();
	json_["materials"] = json::array();
}

int GltfSerializer::writeMaterial(const IfcGeom::Material& style) {
	auto it = materials_.find(style.name());
	if (it != materials_.end()) {
		return it->second;
	}
	
	int idx = json_["materials"].size();
	materials_[style.name()] = idx;

	std::array<double, 4> base;
	base.fill(1.0);
	if (style.hasDiffuse()) {
		for (int i = 0; i < 3; ++i) {
			base[i] = style.diffuse()[i];
		}
	}
	if (style.hasTransparency()) {
		base[3] = 1. - style.transparency();
	}

	json_["materials"].push_back({ {"pbrMetallicRoughness", {{"baseColorFactor", base}, {"metallicFactor", 0}}} });
	
	if (style.hasTransparency() && style.transparency() > 1.e-9) {
		json_["materials"].back()["alphaMode"] = "BLEND";
	}

	return idx;
}

template <size_t N>
struct stride_name { static const char* const value; };
template <>
const char* const stride_name<1U>::value = "SCALAR";
template <>
const char* const stride_name<3U>::value = "VEC3";

template <typename T>
struct component_type { static const uint32_t value; };
template <>
const uint32_t component_type<int>::value = CT_UNSIGNED_INT;
template <>
const uint32_t component_type<float>::value = CT_FLOAT;

template <size_t N, typename It>
size_t write_accessor(json& j, std::ofstream& ofs, It begin, It end) {
	auto num = std::distance(begin, end) / N;

	json accessor = json::object();

	accessor["bufferView"] = N == 1 ? 0 : 1;
	accessor["byteOffset"] = (size_t)ofs.tellp();
	accessor["componentType"] = component_type<typename It::value_type>::value;
	accessor["count"] = num;

	std::array<typename It::value_type, N> min, max;
	min.fill(std::numeric_limits<typename It::value_type>::max());
	max.fill(std::numeric_limits<typename It::value_type>::lowest());
	for (auto it = begin; it != end; it += N) {
		for (size_t i = 0; i < N; ++i) {
			const float& v = *(it + i);
			if (v < min[i]) {
				min[i] = v;
			}
			if (v > max[i]) {
				max[i] = v;
			}
		}
	}
	accessor["min"] = min;
	accessor["max"] = max;
	accessor["type"] = stride_name<N>::value;

	ofs.write((const char*)&*begin, sizeof(typename It::value_type) * num * N);

	j["accessors"].push_back(accessor);

	return j["accessors"].size() - 1;
}

void GltfSerializer::write(const IfcGeom::TriangulationElement<real_t>* o) {
	if (o->geometry().material_ids().empty()) {
		return;
	}

	node_array_.push_back(json_["nodes"].size());

	const std::vector<double>& m = o->transformation().matrix().data();
	// nb: note that this contains the Y-UP transform as well.
	const std::array<double, 16> matrix_flat = {
		m[0], m[ 2], -m[ 1], 0,
		m[3], m[ 5], -m[ 4], 0,
		m[6], m[ 8], -m[ 7], 0,
		m[9], m[11], -m[10], 1
	};
	static const std::array<double, 16> identity_matrix = {1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};
	
	json node;
	if (matrix_flat != identity_matrix) {
		// glTF validator complains about identity matrices
		node["matrix"] = matrix_flat;
	}
	
	int current_mesh_index;

	// See if this mesh has already been processed
	auto it = meshes_.find(o->geometry().id());
	if (it == meshes_.end()) {

		auto mid1 = o->geometry().material_ids().begin();
		auto mid0 = mid1;
		auto fid0 = o->geometry().faces().begin();
		
		json mesh;
		mesh["name"] = o->geometry().id();
		
		while (true) {
			// In glTF we need to decompose a mesh into several primitives
			// with a constant material. In the triangulations coming from
			// IfcOpenShell the materials are encoded in an additional set
			// of indices. Therefore we loop over the material indices to
			// find equal ranges of materials. Triangle indices then need
			// to be updated to reference the vertices only for the current
			// material.
			mid1++;

			if ((mid1 == o->geometry().material_ids().end()) || (*mid1 != *mid0)) {
				auto n = std::distance(mid0, mid1);
				auto fid1 = fid0 + n * 3;

				auto idx_range = std::minmax_element(fid0, fid1);
				const auto& idx_begin = *idx_range.first;
				const auto& idx_end = *idx_range.second + 1;

				std::vector<int> idx_transformed;
				idx_transformed.reserve((n * 3));
				std::transform(fid0, fid1, std::back_inserter(idx_transformed), [idx_begin](int i) {
					return i - idx_begin;
				});

				json primitive = json::object();
				
				primitive["indices"] = write_accessor<1U>(json_, tmp_fstream1_, idx_transformed.begin(), idx_transformed.end());

				auto vbegin = o->geometry().verts().begin();
				std::vector<float> vf(vbegin + idx_begin * 3, vbegin + idx_end * 3);
				primitive["attributes"]["POSITION"] = write_accessor<3U>(json_, tmp_fstream2_, vf.begin(), vf.end());

				auto nbegin = o->geometry().normals().begin();
				std::vector<float> nf(nbegin + idx_begin * 3, nbegin + idx_end * 3);
				primitive["attributes"]["NORMAL"] = write_accessor<3U>(json_, tmp_fstream2_, nf.begin(), nf.end());
				
				primitive["material"] = writeMaterial(o->geometry().materials()[*mid0]);
				primitive["mode"] = PRIM_TRIANGLES;
				
				mesh["primitives"].push_back(primitive);

				if (mid1 == o->geometry().material_ids().end()) {
					break;
				}

				mid0 = mid1;
				fid0 = fid1;
			}
		}

		json_["meshes"].push_back(mesh);

		meshes_[o->geometry().id()] = current_mesh_index = json_["meshes"].size() - 1;
	} else {
		current_mesh_index = it->second;
	}

	node["mesh"] = current_mesh_index;
	json_["nodes"].push_back(node);
}

template <uint32_t>
struct padding_char { static const char value; };
template <>
const char padding_char<JSON>::value = ' ';
template <>
const char padding_char<BIN>::value = '\x00';

uint32_t padding_for(uint32_t length) {
	return ((4 - (length % 4)) % 4);
}

template <uint32_t iden>
void write_padding(std::ostream& fs, uint32_t N) {
	uint32_t padding = padding_for(N);
	for (uint32_t i = 0; i < padding; ++i) {
		fs.put(padding_char<iden>::value);
	}
}

template <uint32_t iden>
void write_header(std::ostream& fs, uint32_t N) {
	uint32_t padding = padding_for(N);
	uint32_t header[] = { N + padding, iden };
	fs.write((const char*)header, sizeof(header));
}

template <uint32_t iden, typename It>
void write_block(std::ostream& fs, It begin, It end) {
	uint32_t N = std::distance(begin, end);
	write_header<iden>(fs, N);
	fs.write((const char*)&*begin, N);
	write_padding<iden>(fs, N);
}

void GltfSerializer::finalize() {
	tmp_fstream1_.close();
	tmp_fstream2_.close();

	std::vector<char> binary_contents;
	// nb: uint32_t is the max buffer size in glTF
	uint32_t indices_length, binary_length;
	{
		std::ifstream ifs(IfcUtil::path::from_utf8(tmp_filename1_).c_str(), std::ios::binary);
		ifs.ignore(std::numeric_limits<std::streamsize>::max());
		indices_length = ifs.gcount();
	}
	{
		std::ifstream ifs(IfcUtil::path::from_utf8(tmp_filename2_).c_str(), std::ios::binary);
		ifs.ignore(std::numeric_limits<std::streamsize>::max());
		binary_length = indices_length + ifs.gcount();
	}

	json scene_0;
	scene_0["nodes"] = node_array_;
	json_["scenes"].push_back(scene_0);
	json_["bufferViews"].push_back({ {"buffer", 0}, { "byteLength", indices_length } });
	json_["bufferViews"].push_back({ {"buffer", 0}, {"byteStride", 12}, { "byteOffset", indices_length },  { "byteLength", binary_length - indices_length } });
	json_["buffers"].push_back({ {"byteLength", binary_length} });

	std::string json_contents = json_.dump();
	uint32_t json_length = (uint32_t) json_contents.size();

	uint32_t header[] = { GLTF, 2U, 12 + 8 + json_length + padding_for(json_length) + 8 + binary_length + padding_for(binary_length) };
	fstream_.write((const char*)header, sizeof(header));

	write_block<JSON>(fstream_, json_contents.begin(), json_contents.end());
	write_header<BIN>(fstream_, binary_length);
	{
		std::ifstream ifs(IfcUtil::path::from_utf8(tmp_filename1_).c_str(), std::ios::binary);
		fstream_ << ifs.rdbuf();
	}
	{
		std::ifstream ifs(IfcUtil::path::from_utf8(tmp_filename2_).c_str(), std::ios::binary);
		fstream_ << ifs.rdbuf();
	}
	write_padding<BIN>(fstream_, binary_length);
}

#endif
