#include "../ifcgeom_schema_agnostic/IfcGeomRenderStyles.h"

#include <map>

static std::map<std::string, IfcGeom::SurfaceStyle> default_materials;
static IfcGeom::SurfaceStyle default_material;
static bool default_materials_initialized = false;

void InitDefaultMaterials() {
	default_materials.insert(std::make_pair("IfcSite", IfcGeom::SurfaceStyle("IfcSite")));
	default_materials["IfcSite"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.75, 0.8, 0.65));

	default_materials.insert(std::make_pair("IfcSlab", IfcGeom::SurfaceStyle("IfcSlab")));
	default_materials["IfcSlab"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.4, 0.4, 0.4));

	default_materials.insert(std::make_pair("IfcWallStandardCase", IfcGeom::SurfaceStyle("IfcWallStandardCase")));
	default_materials["IfcWallStandardCase"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.9, 0.9, 0.9));

	default_materials.insert(std::make_pair("IfcWall", IfcGeom::SurfaceStyle("IfcWall")));
	default_materials["IfcWall"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.9, 0.9, 0.9));

	default_materials.insert(std::make_pair("IfcWindow", IfcGeom::SurfaceStyle("IfcWindow")));
	default_materials["IfcWindow"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.75, 0.8, 0.75));
	default_materials["IfcWindow"].Transparency().reset(0.3);

	default_materials.insert(std::make_pair("IfcDoor", IfcGeom::SurfaceStyle("IfcDoor")));
	default_materials["IfcDoor"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.55, 0.3, 0.15));

	default_materials.insert(std::make_pair("IfcBeam", IfcGeom::SurfaceStyle("IfcBeam")));
	default_materials["IfcBeam"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.75, 0.7, 0.7));

	default_materials.insert(std::make_pair("IfcRailing", IfcGeom::SurfaceStyle("IfcRailing")));
	default_materials["IfcRailing"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.65, 0.6, 0.6));

	default_materials.insert(std::make_pair("IfcMember", IfcGeom::SurfaceStyle("IfcMember")));
	default_materials["IfcMember"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.65, 0.6, 0.6));

	default_materials.insert(std::make_pair("IfcPlate", IfcGeom::SurfaceStyle("IfcPlate")));
	default_materials["IfcPlate"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.8, 0.8, 0.8));

	default_material = IfcGeom::SurfaceStyle("DefaultMaterial");
	default_material.Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.7, 0.7, 0.7));

	default_materials_initialized = true;
}

const IfcGeom::SurfaceStyle* IfcGeom::get_default_style(const std::string& s) {
	if (!default_materials_initialized) InitDefaultMaterials();
	std::map<std::string, IfcGeom::SurfaceStyle>::const_iterator it = default_materials.find(s);
	if (it == default_materials.end()) {
		default_materials.insert(std::make_pair(s, IfcGeom::SurfaceStyle(s)));
		default_materials[s].Diffuse().reset(*default_material.Diffuse());
		it = default_materials.find(s);
	}
	const IfcGeom::SurfaceStyle& surface_style = it->second;
	return &surface_style;
}
