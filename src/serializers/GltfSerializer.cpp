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

#ifdef WITH_PROJ
#include <proj.h>
#endif

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

static const uint32_t ELEMENT_ARRAY_BUFFER = 34963;
static const uint32_t ARRAY_BUFFER = 34962;

GltfSerializer::GltfSerializer(const std::string& filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings)
	: WriteOnlyGeometrySerializer(geometry_settings, settings)
	, filename_(filename)
	, tmp_filename1_(filename + ".indices.tmp")
	, tmp_filename2_(filename + ".vertices.tmp")
	, fstream_(IfcUtil::path::from_utf8(filename).c_str(), std::ios_base::binary)
	, tmp_fstream1_(IfcUtil::path::from_utf8(tmp_filename1_).c_str(), std::ios_base::binary)
	, tmp_fstream2_(IfcUtil::path::from_utf8(tmp_filename2_).c_str(), std::ios_base::binary)
	, bufferViewId(0)
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

int GltfSerializer::writeMaterial(const ifcopenshell::geometry::taxonomy::style::ptr style) {
	auto it = materials_.find(style->name);
	if (it != materials_.end()) {
		return it->second;
	}
	
	int idx = json_["materials"].size();
	materials_[style->name] = idx;

	std::array<double, 4> base;
	base.fill(1.0);
	if (style->diffuse) {
		for (int i = 0; i < 3; ++i) {
			base[i] = style->diffuse.ccomponents()(i);
		}
	}
	if (style->transparency == style->transparency) {
		base[3] = 1. - style->transparency;
	}

	json_["materials"].push_back({ {"doubleSided", true}, {"pbrMetallicRoughness", {{"baseColorFactor", base}, {"metallicFactor", 0}}} });
	
	if (style->transparency == style->transparency && style->transparency > 1.e-9) {
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
size_t write_accessor(json& j, std::ofstream& ofs, It begin, It end, int bufferViewId) {
	auto num = std::distance(begin, end) / N;

	json accessor = json::object();

	accessor["bufferView"] = bufferViewId;
	accessor["byteOffset"] = 0;
	accessor["componentType"] = component_type<typename It::value_type>::value;
	accessor["count"] = num;

	if (N == 1) {
		j["bufferViews"].push_back({ {"buffer", 0}, {"byteOffset", (size_t)ofs.tellp()}, { "byteLength", num *  4}, {"target", ELEMENT_ARRAY_BUFFER} });
	} else {
		j["bufferViews"].push_back({ {"buffer", 0}, {"byteStride", 12}, { "byteOffset", (size_t)ofs.tellp()}, { "byteLength", num * 12}, {"target", ARRAY_BUFFER}});
	}


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

void GltfSerializer::write(const IfcGeom::TriangulationElement* o) {
	if (o->geometry().material_ids().empty()) {
		return;
	}

	node_array_.push_back(json_["nodes"].size());

	const auto& m = o->transformation().data()->ccomponents();
	
	// @todo check
	std::array<double, 16> matrix_flat;
	if (settings_.get<ifcopenshell::geometry::settings::WriteGltfEcef>().get()) {
		matrix_flat = {
			m(0,0), m(1,0), m(2,0), m(3,0),
			m(0,1), m(1,1), m(2,1), m(3,1),
			m(0,2), m(1,2), m(2,2), m(3,2),
			m(0,3), m(1,3), m(2,3), m(3,3)
		};
	} else {
		// nb: note that this contains the Y-UP transform as well.
		matrix_flat = {
			m(0,0), m(2,0), -m(1,0), m(3,0),
			m(0,1), m(2,1), -m(1,1), m(3,1),
			m(0,2), m(2,2), -m(1,2), m(3,2),
			m(0,3), m(2,3), -m(1,3), m(3,3)
		};
	}
	
	static const std::array<double, 16> identity_matrix = {1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};
	
	json node;
	if (matrix_flat != identity_matrix) {
		// glTF validator complains about identity matrices
		node["matrix"] = matrix_flat;
	}
	node["name"] = object_id(o);
	
	int current_mesh_index;

	// See if this mesh has already been processed
	auto it = meshes_.find(o->geometry().id());
	if (it == meshes_.end()) {

		auto mid1 = o->geometry().material_ids().begin();
		auto mid0 = mid1;

		std::vector<int>::const_iterator fid0;
		int stride;
		int primitive_type;

		if (!o->geometry().faces().empty()) {
			stride = 3;
			fid0 = o->geometry().faces().begin();
			primitive_type = PRIM_TRIANGLES;
		} else {
			stride = 2;
			fid0 = o->geometry().edges().begin();
			primitive_type = PRIM_LINES;
		}

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
				auto fid1 = fid0 + n * stride;

				auto idx_range = std::minmax_element(fid0, fid1);
				const auto& idx_begin = *idx_range.first;
				const auto& idx_end = *idx_range.second + 1;

				std::vector<int> idx_transformed;
				idx_transformed.reserve((n * stride));
				std::transform(fid0, fid1, std::back_inserter(idx_transformed), [idx_begin](int i) {
					return i - idx_begin;
				});

				json primitive = json::object();
				
				primitive["indices"] = write_accessor<1U>(json_, tmp_fstream1_, idx_transformed.begin(), idx_transformed.end(), bufferViewId++);

				auto vbegin = o->geometry().verts().begin();
				std::vector<float> vf(vbegin + idx_begin * 3, vbegin + idx_end * 3);
				primitive["attributes"]["POSITION"] = write_accessor<3U>(json_, tmp_fstream2_, vf.begin(), vf.end(), bufferViewId++);

				if (o->geometry().normals().size()) {
					auto nbegin = o->geometry().normals().begin();
					std::vector<float> nf(nbegin + idx_begin * 3, nbegin + idx_end * 3);
					primitive["attributes"]["NORMAL"] = write_accessor<3U>(json_, tmp_fstream2_, nf.begin(), nf.end(), bufferViewId++);
				}
				
				if (*mid0 >= 0) {
					primitive["material"] = writeMaterial(o->geometry().materials()[*mid0]);
				}
				primitive["mode"] = primitive_type;
				
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
	if (north_rotation_) {
		(*north_rotation_)["children"] = json::array();
		for (int i = 0; i < json_["nodes"].size(); ++i) {
			(*north_rotation_)["children"].push_back(i);
		}
		json_["nodes"].push_back(*north_rotation_);
	}

	if (ecef_transform_) {
		(*ecef_transform_)["children"] = json::array();
		for (int i = 0; i < json_["nodes"].size(); ++i) {
			(*ecef_transform_)["children"].push_back(i);
		}
		json_["nodes"].push_back(*ecef_transform_);
	}

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
	if (north_rotation_ || ecef_transform_) {
		scene_0["nodes"] = std::array<size_t, 1>{json_["nodes"].size() - 1};
	} else {
		scene_0["nodes"] = node_array_;
	}
	json_["scenes"].push_back(scene_0);

	//The generated glb file will contain the indices buffer followed by the vertices buffer.
	//Therefore once we know the size of the indices buffer, we update our vertices buffer 
	//to have an offset equal to the size of the indices buffer.
	for (auto &n : json_["bufferViews"]) {
		if (n.contains("byteStride")) {
			n["byteOffset"] = (int)n["byteOffset"] + indices_length;
		}
	}

	json_["buffers"].push_back({ {"byteLength", binary_length} });

	std::string json_contents = json_.dump();
	uint32_t json_length = (uint32_t) json_contents.size();

	const int GLB_FILE_HEADER = 12;
	const int GLB_JSON_HEADER = 8;
	const int GLB_BINARY_CHUNK_HEADER = 8;

	uint32_t header[] = { GLTF, 2U, GLB_FILE_HEADER + GLB_JSON_HEADER + json_length + padding_for(json_length) + 
						  GLB_BINARY_CHUNK_HEADER + binary_length + padding_for(binary_length) };
	fstream_.write((const char*)header, sizeof(header));

	write_block<JSON>(fstream_, json_contents.begin(), json_contents.end());
	write_header<BIN>(fstream_, binary_length);
	{
		//First, write the indices buffer into our glb file
		std::ifstream ifs(IfcUtil::path::from_utf8(tmp_filename1_).c_str(), std::ios::binary);
		fstream_ << ifs.rdbuf();
	}
	{
		//Next, write the vertices buffer into our glb file
		std::ifstream ifs(IfcUtil::path::from_utf8(tmp_filename2_).c_str(), std::ios::binary);
		fstream_ << ifs.rdbuf();
	}
	write_padding<BIN>(fstream_, binary_length);
}

namespace {
	void normalize(std::array<double, 3>& v) {
		auto l = std::sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);

		v[0] /= l;
		v[1] /= l;
		v[2] /= l;
	}

	void cross(const std::array<double, 3>& v1, const std::array<double, 3>& v2, std::array<double, 3>& result) {
		result[0] = v1[1] * v2[2] - v1[2] * v2[1];
		result[1] = v1[2] * v2[0] - v1[0] * v2[2];
		result[2] = v1[0] * v2[1] - v1[1] * v2[0];
	}

	void proj_log(void *, int, const char* c) {
		Logger::Error("PROJ: " + std::string(c));
	}
}

void GltfSerializer::setFile(IfcParse::IfcFile* f) {
	if (!settings_.get<ifcopenshell::geometry::settings::WriteGltfEcef>().get()) {
		return;
	}

	boost::optional<std::string> crs_epsg;
	boost::optional<std::array<double, 3>> crs_x_axis;
	boost::optional<std::array<double, 3>> eastings_northings_elevation;

	aggregate_of_instance::ptr coordops;
	try {
		coordops = f->instances_by_type("IfcCoordinateOperation");
	} catch (IfcParse::IfcException&) {
		// Ignored. Schema likely doesn't support IfcCoordinateOperation.
	}
	if (coordops) {
		for (auto& coordop : *coordops) {
			IfcUtil::IfcBaseClass* source_crs = coordop->as<IfcUtil::IfcBaseEntity>()->get("SourceCRS");
			if (source_crs->declaration().is("IfcGeometricRepresentationContext")) {
				IfcUtil::IfcBaseClass* target_crs = coordop->as<IfcUtil::IfcBaseEntity>()->get("TargetCRS");
				auto name_attr = target_crs->as<IfcUtil::IfcBaseEntity>()->get("Name");
				if (coordop->declaration().is("IfcMapConversion")) {
					
					if (!name_attr.isNull()) {
						std::string epsg_code = name_attr;
						crs_epsg = epsg_code;

						// @todo in which unit are these?
						double eastings = coordop->as<IfcUtil::IfcBaseEntity>()->get("Eastings");
						double northings = coordop->as<IfcUtil::IfcBaseEntity>()->get("Northings");
						double height = coordop->as<IfcUtil::IfcBaseEntity>()->get("OrthogonalHeight");
						height = 0.;

						eastings_northings_elevation = { { eastings, northings, height} };

						auto xaxis_attr = coordop->as<IfcUtil::IfcBaseEntity>()->get("XAxisAbscissa");
						auto yaxis_attr = coordop->as<IfcUtil::IfcBaseEntity>()->get("XAxisOrdinate");
						if (!xaxis_attr.isNull() && !yaxis_attr.isNull()) {
							double xaxis = xaxis_attr;
							double yaxis = yaxis_attr;

							crs_x_axis = { { xaxis, yaxis, 0. } };
						}
					}
				}
			}
		}
	}

	if (!crs_epsg) {
		auto sites = f->instances_by_type("IfcSite");

		if (sites && sites->size() == 1) {
			auto lat_attr = (*sites->begin())->as<IfcUtil::IfcBaseEntity>()->get("RefLatitude");
			auto lon_attr = (*sites->begin())->as<IfcUtil::IfcBaseEntity>()->get("RefLongitude");

			if (!lat_attr.isNull() && !lon_attr.isNull()) {
				std::vector<int> lat_dms = lat_attr;
				std::vector<int> lon_dms = lon_attr;

				auto to_decimal = [](const std::vector<int>& dms) {
					double val = dms[0] + dms[1] / 60. + dms[2] / 3600.;
					if (dms.size() == 4) {
						val += dms[3] / 3600.e6;
					}
					return val;
				};

				auto lat = to_decimal(lat_dms);
				auto lon = to_decimal(lon_dms);
				double elev = 0.;

				/*
				auto elev_attr = (*sites->begin())->as<IfcUtil::IfcBaseEntity>()->get("RefElevation");
				if (!elev_attr->isNull()) {
					elev = *elev_attr;
				}
				*/

				crs_epsg.reset("EPSG:4326");
				eastings_northings_elevation = { { lat, lon, elev } };
			}
		}
	}

	auto contexts = f->instances_by_type_excl_subtypes("IfcGeometricRepresentationContext");

	if (contexts && contexts->size() > 0) {
		auto context = (*contexts->begin())->as<IfcUtil::IfcBaseEntity>();
		auto north_attr = context->get("TrueNorth");
		if (!north_attr.isNull()) {
			IfcUtil::IfcBaseClass* north = north_attr;
			if (north->declaration().is("IfcDirection")) {
				std::vector<double> ratios = north->as<IfcUtil::IfcBaseEntity>()->get("DirectionRatios");
				crs_x_axis = { { ratios[1], -ratios[0], 0. } };
			}
		}
	}

#ifdef WITH_PROJ

	if (crs_epsg) {
		PJ_COORD wgs84_point;

		auto C = proj_context_create();
		proj_log_func(C, nullptr, proj_log);

		// @todo a bit ugly we assume a proj.db in current working directory.
		// a very simplistic but at least portable solution.
		proj_context_set_database_path(C, "proj.db", nullptr, nullptr);

		if (*crs_epsg == "EPSG:4326") {
			wgs84_point = proj_coord(
				(*eastings_northings_elevation)[0],
				(*eastings_northings_elevation)[1],
				(*eastings_northings_elevation)[2],
				0);
		} else {
			// @todo a bit ugly we assume a proj.db in current working directory.
			// a very simplistic but at least portable solution.
			proj_context_set_database_path(C, "proj.db", nullptr, nullptr);

			auto P = proj_create_crs_to_crs(
				C, crs_epsg->c_str(), "EPSG:4326",
				NULL);

			if (!P) {
				Logger::Error("Failed to create PROJ transformation object");
				return;
			}

			auto a = proj_coord(
				(*eastings_northings_elevation)[0],
				(*eastings_northings_elevation)[1],
				(*eastings_northings_elevation)[2],
				0);

			wgs84_point = proj_trans(P, PJ_FWD, a);

			Logger::Notice("Calculated latitude: " + std::to_string(wgs84_point.lp.lam) + " longitude: " + std::to_string(wgs84_point.lp.phi));
		}

		std::swap(wgs84_point.lp.phi, wgs84_point.lp.lam);

		const char *input_crs = "+proj=latlong +datum=WGS84";
		const char *output_crs = "+proj=geocent +datum=WGS84 +units=m";

		// Create a transformation object
		PJ *transform = proj_create_crs_to_crs(C, input_crs, output_crs, NULL);

		// Perform the transformation
		PJ_COORD output_point = proj_trans(transform, PJ_FWD, wgs84_point);

		// Extract the ECEF coordinates
		double x = output_point.xyz.x;
		double y = output_point.xyz.y;
		double z = output_point.xyz.z;

		const char *ellipsoid_def = "WGS84";

		// Create a CRS object representing the ellipsoid
		PJ *ellipsoid_crs = proj_create(C, ellipsoid_def);

		if (!ellipsoid_crs) {
			Logger::Error("Failed to create ellipsoid CRS");
			return;
		}

		auto ellipse = proj_get_ellipsoid(C, ellipsoid_crs);


		int _;
		double semi_major, semi_minor, __;
		proj_ellipsoid_get_parameters(C, ellipse, &semi_major, &semi_minor, &_, &__);

		std::array<double, 3> dxyz = { {
			x * (1. / (semi_major * semi_major)),
			y * (1. / (semi_major * semi_major)),
			z * (1. / (semi_minor * semi_minor))
		} };
		normalize(dxyz);

		// Oblate spheroid, so X and Y axis are equal, so rotation around Z yields east axis.
		std::array<double, 3> east_xyz = { {
			-y,
			x,
			0.
		} };
		normalize(east_xyz);

		std::array<double, 3> north;
		cross(dxyz, east_xyz, north);

		std::array<double, 16> matrix = {
			east_xyz[0], east_xyz[1], east_xyz[2], 0,
			north[0], north[1], north[2], 0.,
			dxyz[0], dxyz[1], dxyz[2], 0,
			0,0,0,1
		};

		ecef_transform_ = json::object({
			{"matrix", matrix }
		});

		json_["extensions"]["CESIUM_RTC"]["center"] = std::array<double, 3>{ {x, y, z} };
		json_["extensionsUsed"].push_back("CESIUM_RTC");

		// Clean up
		proj_destroy(ellipsoid_crs);
		proj_destroy(transform);
		proj_context_destroy(C);
	}

	if (crs_x_axis) {
		normalize(*crs_x_axis);

		auto phi = std::atan2((*crs_x_axis)[1], (*crs_x_axis)[0]);

		north_rotation_ = json::object({
			{"matrix", std::array<double, 16>{
				+std::cos(-phi), -std::sin(-phi), 0., 0.,
				+std::sin(-phi), +std::cos(-phi), 0., 0.,
				0., 0., 1., 0.,
				0., 0., 0., 1.
				}}
		});
	}
#endif
}


#endif
