#include "../../ifcgeom/schema_agnostic/IfcGeomRenderStyles.h"

#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>

#include <map>

namespace pt = boost::property_tree;

static std::map<std::string, ifcopenshell::geometry::taxonomy::style> default_materials;
static ifcopenshell::geometry::taxonomy::style default_material;
static bool default_materials_initialized = false;

void InitDefaultMaterials() {
	default_materials.insert(std::make_pair("IfcSite", ifcopenshell::geometry::taxonomy::style("IfcSite")));
	default_materials["IfcSite"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.75, 0.8, 0.65));

	default_materials.insert(std::make_pair("IfcSlab", ifcopenshell::geometry::taxonomy::style("IfcSlab")));
	default_materials["IfcSlab"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.4, 0.4, 0.4));

	default_materials.insert(std::make_pair("IfcWallStandardCase", ifcopenshell::geometry::taxonomy::style("IfcWallStandardCase")));
	default_materials["IfcWallStandardCase"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.9, 0.9, 0.9));

	default_materials.insert(std::make_pair("IfcWall", ifcopenshell::geometry::taxonomy::style("IfcWall")));
	default_materials["IfcWall"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.9, 0.9, 0.9));

	default_materials.insert(std::make_pair("IfcWindow", ifcopenshell::geometry::taxonomy::style("IfcWindow")));
	default_materials["IfcWindow"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.75, 0.8, 0.75));
	default_materials["IfcWindow"].transparency.reset(0.3);

	default_materials.insert(std::make_pair("IfcDoor", ifcopenshell::geometry::taxonomy::style("IfcDoor")));
	default_materials["IfcDoor"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.55, 0.3, 0.15));

	default_materials.insert(std::make_pair("IfcBeam", ifcopenshell::geometry::taxonomy::style("IfcBeam")));
	default_materials["IfcBeam"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.75, 0.7, 0.7));

	default_materials.insert(std::make_pair("IfcRailing", ifcopenshell::geometry::taxonomy::style("IfcRailing")));
	default_materials["IfcRailing"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.65, 0.6, 0.6));

	default_materials.insert(std::make_pair("IfcMember", ifcopenshell::geometry::taxonomy::style("IfcMember")));
	default_materials["IfcMember"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.65, 0.6, 0.6));

	default_materials.insert(std::make_pair("IfcPlate", ifcopenshell::geometry::taxonomy::style("IfcPlate")));
	default_materials["IfcPlate"].diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.8, 0.8, 0.8));

	default_material = ifcopenshell::geometry::taxonomy::style("DefaultMaterial");
	default_material.diffuse.reset(ifcopenshell::geometry::taxonomy::colour(0.7, 0.7, 0.7));

	default_materials_initialized = true;
}

boost::optional<ifcopenshell::geometry::taxonomy::colour> read_colour_component(const boost::optional<pt::ptree&> list) {
	if (!list) {
		return boost::none;
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
		default_materials.insert(std::make_pair(name, ifcopenshell::geometry::taxonomy::style(name)));

		pt::ptree material = material_pair.second;
		boost::optional<pt::ptree&> diffuse = material.get_child_optional("diffuse");
		default_materials[name].diffuse = read_colour_component(diffuse);

		boost::optional<pt::ptree&> specular = material.get_child_optional("specular");
		default_materials[name].specular = read_colour_component(specular);

		if (material.get_child_optional("specular-roughness")) {
			default_materials[name].specularity.reset(1.0 / material.get<double>("specular-roughness"));
		}
		if (material.get_child_optional("transparency")) {
			default_materials[name].transparency = material.get<double>("transparency");
		}
	}

	// Is "*" present? If yes, remove it and make it the default style.
	std::map<std::string, ifcopenshell::geometry::taxonomy::style>::const_iterator it = default_materials.find("*");
	if (it != default_materials.end()) {
		ifcopenshell::geometry::taxonomy::style star = it->second;
		default_material.diffuse = star.diffuse;
		default_material.specular = star.specular;
		default_material.specularity = star.specularity;
		default_material.transparency = star.transparency;
		default_materials.erase(it);
	}
}

const ifcopenshell::geometry::taxonomy::style& IfcGeom::get_default_style(const std::string& s) {
	if (!default_materials_initialized) InitDefaultMaterials();
	std::map<std::string, ifcopenshell::geometry::taxonomy::style>::const_iterator it = default_materials.find(s);
	if (it == default_materials.end()) {
		default_materials.insert(std::make_pair(s, ifcopenshell::geometry::taxonomy::style(s)));
		default_materials[s].diffuse = default_material.diffuse;
		default_materials[s].specular = default_material.specular;
		default_materials[s].specularity = default_material.specularity;
		default_materials[s].transparency = default_material.transparency;
		it = default_materials.find(s);
	}
	return it->second;
}
