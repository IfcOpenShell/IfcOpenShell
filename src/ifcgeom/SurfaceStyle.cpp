#include "../ifcgeom/IfcGeomRenderStyles.h"

#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>

#include <map>
#include <mutex>

namespace pt = boost::property_tree;

static std::map<std::string, ifcopenshell::geometry::taxonomy::style::ptr> default_materials;
static ifcopenshell::geometry::taxonomy::style::ptr default_material;
static bool default_materials_initialized = false;

void InitDefaultMaterials() {
	default_materials.insert(std::make_pair("IfcSite", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcSite")));
	default_materials["IfcSite"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.75, 0.8, 0.65);

	default_materials.insert(std::make_pair("IfcSlab", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcSlab")));
	default_materials["IfcSlab"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.4, 0.4, 0.4);

	default_materials.insert(std::make_pair("IfcWallStandardCase", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcWallStandardCase")));
	default_materials["IfcWallStandardCase"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.9, 0.9, 0.9);

	default_materials.insert(std::make_pair("IfcWall", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcWall")));
	default_materials["IfcWall"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.9, 0.9, 0.9);

	default_materials.insert(std::make_pair("IfcWindow", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcWindow")));
	default_materials["IfcWindow"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.75, 0.8, 0.75);
	default_materials["IfcWindow"]->transparency = 0.3;

	default_materials.insert(std::make_pair("IfcDoor", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcDoor")));
	default_materials["IfcDoor"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.55, 0.3, 0.15);

	default_materials.insert(std::make_pair("IfcBeam", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcBeam")));
	default_materials["IfcBeam"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.75, 0.7, 0.7);

	default_materials.insert(std::make_pair("IfcRailing", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcRailing")));
	default_materials["IfcRailing"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.65, 0.6, 0.6);

	default_materials.insert(std::make_pair("IfcMember", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcMember")));
	default_materials["IfcMember"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.65, 0.6, 0.6);

	default_materials.insert(std::make_pair("IfcPlate", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcPlate")));
	default_materials["IfcPlate"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.8, 0.8, 0.8);

	default_materials.insert(std::make_pair("IfcSpace", std::make_shared<ifcopenshell::geometry::taxonomy::style>("IfcSpace")));
	default_materials["IfcSpace"]->diffuse = ifcopenshell::geometry::taxonomy::colour(0.65, 0.75, 0.8);
	default_materials["IfcSpace"]->transparency = 0.8;

	default_material = std::make_shared<ifcopenshell::geometry::taxonomy::style>("DefaultMaterial");
	default_material->diffuse = ifcopenshell::geometry::taxonomy::colour(0.7, 0.7, 0.7);

	default_materials_initialized = true;
}

ifcopenshell::geometry::taxonomy::colour read_colour_component(const boost::optional<pt::ptree&> list) {
	if (!list) {
		return ifcopenshell::geometry::taxonomy::colour();
	}
	double rgb[3];
	int i = 0;
	for (pt::ptree::value_type &colour : list.get()) {
		if (3 <= i) {
			throw std::runtime_error("rgb array over 3 elements large");
		}
		rgb[i] = colour.second.get_value<double>();
		i++;
	}
	if (i != 3) {
		throw std::runtime_error("rgb array less than 3 elements large (was " + std::to_string(i) + ")");
	}
	return ifcopenshell::geometry::taxonomy::colour(rgb[0], rgb[1], rgb[2]);
}

void IfcGeom::set_default_style_file(const std::string& json_file) {
	if (!default_materials_initialized) InitDefaultMaterials();
	default_materials.clear();

	// @todo this will probably need to be updated for UTF-8 paths on Windows
	pt::ptree root;
	pt::read_json(json_file, root);

	for (pt::ptree::value_type &material_pair : root) {
		std::string name = material_pair.first;
		default_materials.insert(std::make_pair(name, std::make_shared<ifcopenshell::geometry::taxonomy::style>(name)));

		pt::ptree material = material_pair.second;
		boost::optional<pt::ptree&> diffuse = material.get_child_optional("diffuse");
		default_materials[name]->diffuse = read_colour_component(diffuse);

		boost::optional<pt::ptree&> specular = material.get_child_optional("specular");
		default_materials[name]->specular = read_colour_component(specular);

		if (material.get_child_optional("specular-roughness")) {
			default_materials[name]->specularity = 1.0 / material.get<double>("specular-roughness");
		}
		if (material.get_child_optional("transparency")) {
			default_materials[name]->transparency = material.get<double>("transparency");
		}
	}

	// Is "*" present? If yes, remove it and make it the default style.
	auto it = default_materials.find("*");
	if (it != default_materials.end()) {
		default_material = it->second;
		default_materials.erase(it);
	}
}

const ifcopenshell::geometry::taxonomy::style::ptr& IfcGeom::get_default_style(const std::string& s) {
	static std::mutex m;
	std::lock_guard<std::mutex> lk(m);

	if (!default_materials_initialized) InitDefaultMaterials();
	auto it = default_materials.find(s);
	if (it == default_materials.end()) {
		default_materials.insert(std::make_pair(s, default_material));
		it = default_materials.find(s);
	}
	return it->second;
}

ifcopenshell::geometry::taxonomy::style::ptr& IfcGeom::update_default_style(const std::string& s) {
	if (!default_materials_initialized) InitDefaultMaterials();
	auto it = default_materials.find(s);
	if (it == default_materials.end()) {
		throw std::runtime_error("No style registered for " + s);
	}
	return it->second;
}
