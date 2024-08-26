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

#if defined(WITH_HDF5) && defined(IFOPSH_WITH_OPENCASCADE)

#include "HdfSerializer.h"

#include "../ifcgeom/IfcGeomRenderStyles.h"
#include "../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

#include "../ifcparse/utils.h"

#include <BRepTools_ShapeSet.hxx>
#include <BinTools_ShapeSet.hxx>
#include <boost/lexical_cast.hpp>

#include <iomanip>
#include <numeric>
#include <functional>

#ifdef USE_BINARY
#define write_shape write_binary
#define read_shape read_binary
#else
#define write_shape write_text
#define read_shape read_text
#endif

herr_t print_stack(hid_t /*estack*/, void*) {
	// For debugging: when using IfcConvert on Windows with wcout,
	// it's difficult to get console output of HDF5 stack traces.
	/*
	auto f = fopen("temp.txt", "w");
	H5Eprint(estack, f);
	fclose(f);
	*/
	return 0;
}

HdfSerializer::HdfSerializer(const std::string& hdf_filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings, bool read_only)
	: GeometrySerializer(geometry_settings, settings)
	, hdf_filename(hdf_filename)
	, settings_(settings)
{
	H5E_auto2_t fn = &print_stack;
	H5::Exception::setAutoPrint(fn, nullptr);
	
	try {
		file = H5::H5File(hdf_filename, read_only
			? H5F_ACC_RDONLY
			: (H5F_ACC_RDWR | H5F_ACC_CREAT));
	} catch (H5::Exception& e) {
		throw IfcParse::IfcException(e.getDetailMsg());
	}
	
	str_type = H5::StrType(H5::PredType::C_S1, H5T_VARIABLE);

#ifdef USE_BINARY
	auto uint_type = H5::PredType::NATIVE_UINT8;
	shape_type = H5::VarLenType(&uint_type);
#else
	shape_type = str_type;
#endif

	hsize_t     dims_3[1]{ 3 };
	double3 = H5::ArrayType(H5::PredType::NATIVE_DOUBLE, 1, dims_3);

	style_compound = H5::CompType(sizeof(surface_style_serialization));
	style_compound.insertMember("name", HOFFSET(surface_style_serialization, name), str_type);
	style_compound.insertMember("original_name", HOFFSET(surface_style_serialization, original_name), str_type);
	style_compound.insertMember("id", HOFFSET(surface_style_serialization, id), H5::PredType::NATIVE_INT);
	style_compound.insertMember("diffuse", HOFFSET(surface_style_serialization, diffuse), double3);
	style_compound.insertMember("specular", HOFFSET(surface_style_serialization, specular), double3);
	style_compound.insertMember("transparency", HOFFSET(surface_style_serialization, transparency), H5::PredType::NATIVE_DOUBLE);
	style_compound.insertMember("specularity", HOFFSET(surface_style_serialization, specularity), H5::PredType::NATIVE_DOUBLE);

	hsize_t     dims_4x4[2]{ 4, 4 };
	double4x4 = H5::ArrayType(H5::PredType::NATIVE_DOUBLE, 2, dims_4x4);

	compound = H5::CompType(sizeof(brep_element));
	compound.insertMember("id", HOFFSET(brep_element, id), H5::PredType::NATIVE_INT);
	compound.insertMember("matrix", HOFFSET(brep_element, matrix), double4x4);
	compound.insertMember("shape_serialization", HOFFSET(brep_element, shape_serialization), shape_type);
	compound.insertMember("surface_style_id", HOFFSET(brep_element, surface_style), style_compound);
}

bool HdfSerializer::ready() {
	return true;
}

void HdfSerializer::writeHeader() {
}

namespace {
	template <typename T>
	H5::DataType h5_datatype_for_cpp();

	template <>
	H5::DataType h5_datatype_for_cpp<int>() {
		return H5::PredType::NATIVE_INT;
	}

	template <>
	H5::DataType h5_datatype_for_cpp<uint64_t>() {
		return H5::PredType::NATIVE_UINT64;
	}

	template <>
	H5::DataType h5_datatype_for_cpp<double>() {
		return H5::PredType::NATIVE_DOUBLE;
	}

	template <>
	H5::DataType h5_datatype_for_cpp<std::string>() {
		return H5::StrType(H5::PredType::C_S1, H5T_VARIABLE);
	}

	template <typename T>
	void do_read(H5::Attribute& attr, T& val) {
		attr.read(h5_datatype_for_cpp<T>(), &val);
	}

	template <>
	void do_read(H5::Attribute& attr, std::string& val) {
		attr.read(h5_datatype_for_cpp<std::string>(), val);
	}

	template <typename T>
	T read_scalar_attribute(H5::H5Object& l, const std::string& name) {
		auto attr = l.openAttribute(name);
		auto space = attr.getSpace();
		int rank = space.getSimpleExtentNdims();
		// A scalar dataspace, H5S_SCALAR, has a single element, though that
		// element may be of a complex datatype, such as a compound or array
		// datatype. By convention, the rank of a scalar dataspace is always
		// 0 (zero); 
		if (rank != 0) {
			throw std::runtime_error("Invalid");
		}
		T val;
		do_read<T>(attr, val);
		return val;
	}
}

#include <BinTools.hxx>

namespace {
	// https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/Part/App/TopoShape.cpp
	TopoDS_Shape read_binary(const hvl_t& vlen) {
		std::string s((char*)vlen.p, (size_t)vlen.len);
		std::istringstream str(s);
		BinTools_ShapeSet theShapeSet;
		theShapeSet.Read(str);
		Standard_Integer shapeId = 0, locId = 0, orient = 0;
		BinTools::GetInteger(str, shapeId);
		if (shapeId <= 0 || shapeId > theShapeSet.NbShapes()) {
			throw std::runtime_error("");
		}

		BinTools::GetInteger(str, locId);
		BinTools::GetInteger(str, orient);
		TopAbs_Orientation anOrient = static_cast<TopAbs_Orientation>(orient);

		TopoDS_Shape shp = theShapeSet.Shape(shapeId);
		shp.Location(theShapeSet.Locations().Location(locId));
		shp.Orientation(anOrient);

		return shp;
	}

	// https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/Part/App/TopoShape.cpp
	void write_binary(TopoDS_Shape shp, std::string& s) {
		std::ostringstream out;

		BinTools_ShapeSet theShapeSet;
		
		Standard_Integer shapeId = theShapeSet.Add(shp);
		Standard_Integer locId = theShapeSet.Locations().Index(shp.Location());
		Standard_Integer orient = static_cast<int>(shp.Orientation());

		theShapeSet.Write(out);
		BinTools::PutInteger(out, shapeId);
		BinTools::PutInteger(out, locId);
		BinTools::PutInteger(out, orient);

		s = out.str();
	}

	TopoDS_Shape read_text(const std::string& s) {
		std::stringstream stream(s);
		BRep_Builder B;
		TopoDS_Shape shp;
		BRepTools::Read(shp, stream, B);
		return shp;
	}

	void write_text(TopoDS_Shape shp, std::string& out) {
		std::stringstream sstream;
		BRepTools::Write(shp, sstream);
		out = sstream.str();
	}
}

namespace {
	template <typename T>
	std::vector<T> read_dataset(const H5::Group& group, const std::string& name) {
		auto ds = group.openDataSet(name);
		auto space = ds.getSpace();
		int rank = space.getSimpleExtentNdims();
		std::vector<hsize_t> dims(rank);
		space.getSimpleExtentDims(dims.data(), NULL);
		const hsize_t total = std::accumulate(dims.begin(), dims.end(), 1U, std::multiplies<hsize_t>());
		std::vector<T> result(total);
		ds.read(result.data(), h5_datatype_for_cpp<T>());
		return result;
	}
}

void HdfSerializer::read_surface_style(surface_style_serialization& s, const ifcopenshell::geometry::taxonomy::style::ptr& gss_) {
	auto& gss = *gss_;
	if (strlen(s.name) || s.id) {
		if (s.diffuse[0] == s.diffuse[0]) {
			gss.diffuse = ifcopenshell::geometry::taxonomy::colour(s.diffuse[0], s.diffuse[1], s.diffuse[2]);
		}
		if (s.specular[0] == s.specular[0]) {
			gss.specular = ifcopenshell::geometry::taxonomy::colour(s.specular[0], s.specular[1], s.specular[2]);
		}
		if (s.transparency == s.transparency) {
			gss.transparency = s.transparency;
		}
		if (s.specularity == s.specularity) {
			gss.specularity = s.specularity;
		}
	}

}

void HdfSerializer::remove(const std::string& guid) {
	if (H5Lexists(file.getId(), guid.c_str(), H5P_DEFAULT)) {
		file.unlink(guid);
	}
}

IfcGeom::Element* HdfSerializer::read(IfcParse::IfcFile& f, const std::string& guid, const std::string& representation_id_str, read_type rt) {
	if (!H5Lexists(file.getId(), guid.c_str(), H5P_DEFAULT)) {
		return nullptr;
	}

	auto element_group = file.openGroup(guid);
	if (!H5Lexists(element_group.getId(), representation_id_str.c_str(), H5P_DEFAULT)) {
		return nullptr;
	}
  
	int id = read_scalar_attribute<int>(element_group, "id");
	int parent_id = read_scalar_attribute<int>(element_group, "parent_id");
	std::string type = read_scalar_attribute<std::string>(element_group, "type");
	std::string name = read_scalar_attribute<std::string>(element_group, "name");
	std::string context = read_scalar_attribute<std::string>(element_group, "context");
	std::string unique_id = read_scalar_attribute<std::string>(element_group, "unique_id");

	auto trsf = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>();
	auto placeds = element_group.openDataSet(DATASET_NAME_PLACEMENT);
	double m44[4][4];
	placeds.read(m44, H5::PredType::NATIVE_DOUBLE);
	// @todo check
	trsf->components() << Eigen::Map<Eigen::Matrix4d>(&m44[0][0]);

	auto representation_group = element_group.openGroup(representation_id_str);
	std::string geom_id = read_scalar_attribute<std::string>(representation_group, "geom_id");

	auto inst = f.instance_by_id(id)->as<IfcUtil::IfcBaseEntity>();

	boost::shared_ptr<IfcGeom::Representation::BRep> brep_geometry;
	boost::shared_ptr<IfcGeom::Representation::Triangulation> triangulation_geometry;

	if (rt == READ_BREP) {
		auto it = brep_cache_.find(representation_id_str);
		if (it != brep_cache_.end()) {
			brep_geometry = it->second;
		}
	} else {
		auto it = triangulation_cache_.find(representation_id_str);
		if (it != triangulation_cache_.end()) {
			triangulation_geometry = it->second;
		}
	}

	if (rt == READ_BREP && !brep_geometry) {
		auto brepDataset = representation_group.openDataSet(DATASET_NAME_OCCT);
		
		/*
		// @todo

		static const auto ignored_settings =
			// Settings that do not affect storage of brep data
			IfcGeom::IteratorSettings::DISABLE_TRIANGULATION | IfcGeom::IteratorSettings::USE_BREP_DATA |
			// Settings that affect which representation is considered, but cache does not need to be complete
			IfcGeom::IteratorSettings::INCLUDE_CURVES | IfcGeom::IteratorSettings::EXCLUDE_SOLIDS_AND_SURFACES |
			// Only affects triangulation
			IfcGeom::IteratorSettings::WELD_VERTICES | IfcGeom::IteratorSettings::NO_NORMALS |
			IfcGeom::IteratorSettings::GENERATE_UVS | IfcGeom::IteratorSettings::EDGE_ARROWS |
			// Is applied in the serializer
			IfcGeom::IteratorSettings::ELEMENT_HIERARCHY;
		
		auto stored_settings = read_scalar_attribute<uint64_t>(brepDataset, "settings");
		auto requested_settings = settings_.get_raw();
		stored_settings &= ~ignored_settings;
		requested_settings &= ~ignored_settings;

		// World coordinates can be applied post hoc
		if (stored_settings != requested_settings && (stored_settings | IfcGeom::IteratorSettings::USE_WORLD_COORDS) != requested_settings) {
			throw std::runtime_error("Settings mismatch");
		}
		*/

		std::vector<brep_element> parts;
		{
			auto space = brepDataset.getSpace();
			int rank = space.getSimpleExtentNdims();

			if (rank != 1) {
				return nullptr;
			}

			std::vector<hsize_t> dims(rank);
			space.getSimpleExtentDims(dims.data(), NULL);

			parts.resize(dims[0]);
			brepDataset.read(parts.data(), compound);
		}

		IfcGeom::ConversionResults shapes;
		
		for (auto& part : parts) {
			TopoDS_Shape shp = read_shape(part.shape_serialization);

			// @todo check
			auto matrix = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>();
			matrix->components() << Eigen::Map<Eigen::Matrix4d>(&part.matrix[0][0]);

			auto style_ptr = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::style>();
			read_surface_style(part.surface_style, style_ptr);
			
			shapes.push_back(IfcGeom::ConversionResult(part.id, matrix, new ifcopenshell::geometry::OpenCascadeShape(shp), style_ptr));
		}

		/*
		// @todo

		// World coordinates can be applied post-hoc
		if (settings_.get(IfcGeom::IteratorSettings::USE_WORLD_COORDS) && !(stored_settings & IfcGeom::IteratorSettings::USE_WORLD_COORDS)) {
			for (IfcGeom::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
				it->prepend(trsf);
			}
			trsf = ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>();
		}
		*/

		brep_geometry = boost::shared_ptr<IfcGeom::Representation::BRep>(new IfcGeom::Representation::BRep(geometry_settings(), type, geom_id, shapes));

		/*
		// @todo
		if (!settings_.get(IfcGeom::IteratorSettings::USE_WORLD_COORDS)) {
			brep_cache_.insert({ representation_id_str, brep_geometry });
		}
		*/
	}
	
	if (rt == READ_TRIANGULATION && !triangulation_geometry) {
		H5::Group meshGroup;
		try {
			meshGroup = representation_group.openGroup(GROUP_NAME_MESH);
		} catch (H5::Exception&) {
			return nullptr;
		}

		auto verts = read_dataset<double>(meshGroup, DATASET_NAME_POSITIONS);
		auto faces = read_dataset<int>(meshGroup, DATASET_NAME_INDICES);
		auto edges = read_dataset<int>(meshGroup, DATASET_NAME_EDGES);
		auto normals = read_dataset<double>(meshGroup, DATASET_NAME_NORMALS);
		auto uvcoords = read_dataset<double>(meshGroup, DATASET_NAME_UVCOORDS);
		auto material_ids = read_dataset<int>(meshGroup, DATASET_NAME_MATERIAL_IDS);
		auto item_ids = read_dataset<int>(meshGroup, DATASET_NAME_ITEM_IDS);

		std::vector<surface_style_serialization> surface_styles;

		{
			auto ds = meshGroup.openDataSet(DATASET_NAME_MATERIALS);
			auto space = ds.getSpace();
			int rank = space.getSimpleExtentNdims();

			if (rank != 1) {
				return nullptr;
			}

			std::vector<hsize_t> dims(rank);
			space.getSimpleExtentDims(dims.data(), NULL);

			surface_styles.resize(dims[0]);
			ds.read(surface_styles.data(), style_compound);
		}

		std::vector<ifcopenshell::geometry::taxonomy::style::ptr> surface_style_ptrs(surface_styles.size());

		for (size_t i = 0; i < surface_styles.size(); ++i) {
			read_surface_style(surface_styles[i], surface_style_ptrs[i]);
		}

		triangulation_geometry = boost::shared_ptr<IfcGeom::Representation::Triangulation>(new IfcGeom::Representation::Triangulation(
			geometry_settings_,
			type,
			geom_id,
			verts,
			faces,
			edges,
			normals,
			uvcoords,
			material_ids,
			surface_style_ptrs,
			item_ids
		));

		triangulation_cache_.insert({ representation_id_str, triangulation_geometry });
	}

	if (rt == READ_BREP) {
		return new IfcGeom::BRepElement(id, parent_id, name, type, guid, context, trsf, brep_geometry, inst);
	} else {
		return new IfcGeom::TriangulationElement(
			IfcGeom::Element(
				geometry_settings_,
				id,
				parent_id,
				name,
				type,
				guid,
				context,
				trsf,
				inst
			),
			triangulation_geometry
		);
	}
}

H5::Group HdfSerializer::write(const IfcGeom::Element* o) {
	try {
		return file.openGroup(o->guid());
	} catch (H5::Exception&) {}

	H5::Group element_group = file.createGroup(o->guid());

	typedef std::string const & (IfcGeom::Element::*string_member_fun)(void) const;
	typedef int (IfcGeom::Element::*int_member_fun)(void) const;

	static const std::vector<std::pair<const char* const, string_member_fun>> data_pairs_string = {
		{"type", &IfcGeom::Element::type},
		{"name", &IfcGeom::Element::name },
		{"guid", &IfcGeom::Element::guid },
		{"context", &IfcGeom::Element::context },
		{"unique_id", &IfcGeom::Element::unique_id }
	};

	static const std::vector<std::pair<const char* const, int_member_fun>> data_pairs_int = {
		{"id", &IfcGeom::Element::id},
		{"parent_id", &IfcGeom::Element::parent_id },
	};

	H5::DataSpace attrdspace(H5S_SCALAR);

	for (auto& p : data_pairs_string) {
		H5::Attribute att = element_group.createAttribute(p.first, str_type, attrdspace);
		att.write(str_type, ((*o).*(p.second))());
	}

	for (auto& p : data_pairs_int) {
		H5::Attribute att = element_group.createAttribute(p.first, H5::PredType::NATIVE_INT, attrdspace);
		int value = ((*o).*(p.second))();
		att.write(H5::PredType::NATIVE_INT, &value);
	}

	hsize_t     dims_4x4[2]{ 4, 4 };
	H5::DataSpace dataspace_4x4(2, dims_4x4);

	auto placement_dataset = element_group.createDataSet(DATASET_NAME_PLACEMENT, H5::PredType::NATIVE_DOUBLE, dataspace_4x4);
	const auto& m = o->transformation().data()->ccomponents();
	// @todo check, is this needed, can we use the storage of Eigen?
	double m44[4][4] = {
		{ m(0,0), m(1,0), m(2,0), m(3,0) },
		{ m(0,1), m(1,1), m(2,1), m(3,1) },
		{ m(0,2), m(1,2), m(2,2), m(3,2) },
		{ m(0,3), m(1,3), m(2,3), m(3,3) }
	};
	placement_dataset.write(m44, H5::PredType::NATIVE_DOUBLE);

	return element_group;
}

H5::Group HdfSerializer::createRepresentationGroup(const H5::Group& element_group, const std::string& gid) {
	// the part before the hyphen is the representation id
	auto gid2 = gid;
	auto hyphen = gid2.find("-");
	if (hyphen != std::string::npos) {
		gid2 = gid2.substr(0, hyphen);
	}

	H5::Group representation_group;
	try {
		representation_group = element_group.openGroup(gid2);
	} catch (H5::Exception&) {
		representation_group = element_group.createGroup(gid2);

		H5::DataSpace attrdspace(H5S_SCALAR);
		{
			H5::Attribute att = representation_group.createAttribute("geom_id", str_type, attrdspace);
			std::string value = gid;
			att.write(str_type, value);
		}
	}
	return representation_group;
}

void HdfSerializer::write_style(surface_style_serialization& data, const ifcopenshell::geometry::taxonomy::style::ptr& sptr) {
	auto& s = *sptr;
	data.name = s.name.c_str();
	// @todo
	data.original_name = s.name.c_str();
	data.id = s.instance->as<IfcUtil::IfcBaseClass>()->id();
	if (s.diffuse) {
		data.diffuse[0] = s.diffuse.ccomponents()(0);
		data.diffuse[1] = s.diffuse.ccomponents()(1);
		data.diffuse[2] = s.diffuse.ccomponents()(2);
	}
	if (s.specular) {
		data.specular[0] = s.specular.ccomponents()(0);
		data.specular[1] = s.specular.ccomponents()(1);
		data.specular[2] = s.specular.ccomponents()(2);
	}
	if (s.transparency == s.transparency) {
		data.transparency = s.transparency;
	}
	if (s.specularity == s.specularity) {
		data.specularity = s.specularity;
	}
}


void HdfSerializer::write(const IfcGeom::BRepElement* o) {
	static auto nan = std::numeric_limits<double>::quiet_NaN();

	auto element_group = write((const IfcGeom::Element*)o);

	/*
	// For now we disable softlinks, as it can't be safely used with delete()
	// @todo we can still cache the serialization or read it from the file probably for a comparible speedup.

	auto it = group_cache_.find(o->geometry().id());
	if (it != group_cache_.end()) {
		H5Lcreate_soft(it->second.c_str(), element_group.getLocId(), o->geometry().id().c_str(), H5P_DEFAULT, H5P_DEFAULT);
		return;
	}
	*/

	H5::Group representation_group = createRepresentationGroup(element_group, o->geometry().id());

	/*
	const size_t len = H5Iget_name(representation_group.getId(), NULL, 0);
	char* name_buffer = new char[len];
	H5Iget_name(representation_group.getId(), name_buffer, len + 1);
	group_cache_.insert(it, { o->geometry().id(), name_buffer });		
	delete[] name_buffer;
	*/

	std::list<std::string> brep_strings;
	size_t num_parts = std::distance(o->geometry().begin(), o->geometry().end());
	brep_element* parts = new brep_element[num_parts];
	size_t i = 0;
	for (auto it = o->geometry().begin(); it != o->geometry().end(); ++it, ++i) {
		parts[i].id = it->ItemId();
		const auto& m = o->transformation().data()->ccomponents();
		// @todo check, is this needed, can we use the storage of Eigen?
		std::array<std::array<double, 4>, 4> arr = { {
			{ { m(0,0), m(1,0), m(2,0), m(3,0) } },
			{ { m(0,1), m(1,1), m(2,1), m(3,1) } },
			{ { m(0,2), m(1,2), m(2,2), m(3,2) } },
			{ { m(0,3), m(1,3), m(2,3), m(3,3) } }
		} };
		for (int j = 0; j < 4; ++j) {
			std::copy(arr[j].begin(), arr[j].end(), parts[i].matrix[j]);
		}

		brep_strings.emplace_back();
		write_shape(std::static_pointer_cast<ifcopenshell::geometry::OpenCascadeShape>(it->Shape())->shape(), brep_strings.back());
		
		parts[i].surface_style = { "", "", 0, {nan,nan,nan}, {nan,nan,nan}, nan, nan };
		if (it->hasStyle()) {
			auto s = it->StylePtr();
			write_style(parts[i].surface_style, s);
		}

#ifdef USE_BINARY
		const auto& s = brep_strings.back();
		parts[i].shape_serialization.p = new char[s.size()];
		memcpy(parts[i].shape_serialization.p, s.c_str(), s.size());
		parts[i].shape_serialization.len = s.size();
#else
		parts[i].shape_serialization = brep_strings.back().c_str();
#endif
	}

	hsize_t     dimsp[1]{ num_parts };
	H5::DataSpace dataspace_parts(1, dimsp);

	auto brepDataset = representation_group.createDataSet(DATASET_NAME_OCCT, compound, dataspace_parts);
	brepDataset.write(parts, compound);

	H5::DataSpace attrdspace(H5S_SCALAR);
	H5::Attribute att = brepDataset.createAttribute("settings", H5::PredType::NATIVE_UINT64, attrdspace);
	/*
	// @todo
	uint64_t value = o->geometry().settings().get_raw();
	*/
	uint64_t value = 0;
	att.write(H5::PredType::NATIVE_UINT64, &value);
}

namespace {

	template <typename T>
	void write_dataset(const H5::Group& group, const std::string& name, const std::vector<T>& ts, size_t stride) {
		hsize_t d[2]{ ts.size() / stride, stride };
		H5::DataSpace dataspace(stride == 1 ? 1 : 2, d);
		auto dt = h5_datatype_for_cpp<T>();

		auto ds = group.createDataSet(name, dt, dataspace);
		ds.write(ts.data(), dt);
	}

}

void HdfSerializer::write(const IfcGeom::TriangulationElement* o) {
	auto element_group = write((const IfcGeom::Element*)o);

	const auto& mesh = o->geometry();
	H5::Group representation_group = createRepresentationGroup(element_group, o->geometry().id());
	H5::Group meshGroup = representation_group.createGroup(GROUP_NAME_MESH);

	write_dataset(meshGroup, DATASET_NAME_POSITIONS, mesh.verts(), 3);
	write_dataset(meshGroup, DATASET_NAME_INDICES, mesh.faces(), 3);
	write_dataset(meshGroup, DATASET_NAME_EDGES, mesh.edges(), 2);
	write_dataset(meshGroup, DATASET_NAME_NORMALS, mesh.normals(), 2);
	write_dataset(meshGroup, DATASET_NAME_UVCOORDS, mesh.uvs(), 2);
	write_dataset(meshGroup, DATASET_NAME_MATERIAL_IDS, mesh.material_ids(), 1);
	write_dataset(meshGroup, DATASET_NAME_ITEM_IDS, mesh.item_ids(), 1);

	{
		auto& ts = mesh.materials();
		hsize_t d[2] { ts.size() };
		H5::DataSpace dataspace(1, d);
		const auto& dt = style_compound;

		std::vector<surface_style_serialization> data;
		data.reserve(ts.size());
		for (auto& m : ts) {
			data.emplace_back();
			write_style(data.back(), m);
		}

		auto ds = meshGroup.createDataSet(DATASET_NAME_MATERIALS, dt, dataspace);
		ds.write(data.data(), dt);
	}
}


const H5std_string HdfSerializer::DATASET_NAME_POSITIONS = "positions";
const H5std_string HdfSerializer::DATASET_NAME_UVCOORDS = "uvcoords";
const H5std_string HdfSerializer::DATASET_NAME_NORMALS = "normals";
const H5std_string HdfSerializer::DATASET_NAME_INDICES = "indices";
const H5std_string HdfSerializer::DATASET_NAME_EDGES = "edges";
const H5std_string HdfSerializer::DATASET_NAME_MATERIAL_IDS = "material_ids";
const H5std_string HdfSerializer::DATASET_NAME_ITEM_IDS = "item_ids";
const H5std_string HdfSerializer::DATASET_NAME_MATERIALS = "materials";
const H5std_string HdfSerializer::DATASET_NAME_OCCT = "brep";
const H5std_string HdfSerializer::DATASET_NAME_PLACEMENT = "placement";

const H5std_string HdfSerializer::GROUP_NAME_MESH = "mesh";


#endif