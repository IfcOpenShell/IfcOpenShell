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

#include <boost/optional/optional.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>

#include <map>

#include "IfcGeom.h"

namespace pt = boost::property_tree;

bool process_colour(IfcSchema::IfcColourRgb* colour, double* rgb) {
	if (colour != 0) {
		rgb[0] = colour->Red();
		rgb[1] = colour->Green();
		rgb[2] = colour->Blue();
	}
	return colour != 0;
}

bool process_colour(IfcSchema::IfcNormalisedRatioMeasure* factor, double* rgb) {
	if (factor != 0) {
		const double f = *factor;
		rgb[0] = rgb[1] = rgb[2] = f;
	}
	return factor != 0;
}

bool process_colour(IfcSchema::IfcColourOrFactor* colour_or_factor, double* rgb) {
	if (colour_or_factor == 0) {
		return false;
	} else if (colour_or_factor->is(IfcSchema::Type::IfcColourRgb)) {
		return process_colour(static_cast<IfcSchema::IfcColourRgb*>(colour_or_factor), rgb);
	} else if (colour_or_factor->is(IfcSchema::Type::IfcNormalisedRatioMeasure)) {
		return process_colour(static_cast<IfcSchema::IfcNormalisedRatioMeasure*>(colour_or_factor), rgb);
	} else {
		return false;
	}
}

const IfcGeom::SurfaceStyle* IfcGeom::Kernel::internalize_surface_style(const std::pair<IfcSchema::IfcSurfaceStyle*, IfcSchema::IfcSurfaceStyleShading*>& shading_styles) {
	if (shading_styles.second == 0) {
		return 0;
	}
	int surface_style_id = shading_styles.first->entity->id();
	std::map<int,SurfaceStyle>::const_iterator it = style_cache.find(surface_style_id);
	if (it != style_cache.end()) {
		return &(it->second);
	}
	SurfaceStyle surface_style;
	if (shading_styles.first->hasName()) {
		surface_style = SurfaceStyle(surface_style_id, shading_styles.first->Name());
	} else {
		surface_style = SurfaceStyle(surface_style_id);
	}
	double rgb[3];
	if (process_colour(shading_styles.second->SurfaceColour(), rgb)) {
		surface_style.Diffuse().reset(SurfaceStyle::ColorComponent(rgb[0], rgb[1], rgb[2]));
	}
	if (shading_styles.second->is(IfcSchema::Type::IfcSurfaceStyleRendering)) {
		IfcSchema::IfcSurfaceStyleRendering* rendering_style = static_cast<IfcSchema::IfcSurfaceStyleRendering*>(shading_styles.second);
		if (rendering_style->hasDiffuseColour() && process_colour(rendering_style->DiffuseColour(), rgb)) {
			SurfaceStyle::ColorComponent diffuse = surface_style.Diffuse().get_value_or(SurfaceStyle::ColorComponent(1,1,1));
			surface_style.Diffuse().reset(SurfaceStyle::ColorComponent(diffuse.R() * rgb[0], diffuse.G() * rgb[1], diffuse.B() * rgb[2]));
		}
		if (rendering_style->hasDiffuseTransmissionColour()) {
			// Not supported
		}
		if (rendering_style->hasReflectionColour()) {
			// Not supported
		}
		if (rendering_style->hasSpecularColour() && process_colour(rendering_style->SpecularColour(), rgb)) {
			surface_style.Specular().reset(SurfaceStyle::ColorComponent(rgb[0], rgb[1], rgb[2]));
		}
		if (rendering_style->hasSpecularHighlight()) {
			IfcSchema::IfcSpecularHighlightSelect* highlight = rendering_style->SpecularHighlight();
			if (highlight->is(IfcSchema::Type::IfcSpecularRoughness)) {
				double roughness = *((IfcSchema::IfcSpecularRoughness*)highlight);
				if (roughness >= 1e-9) {
					surface_style.Specularity().reset(1.0 / roughness);
				}
			} else if (highlight->is(IfcSchema::Type::IfcSpecularExponent)) {
				surface_style.Specularity().reset(*((IfcSchema::IfcSpecularExponent*)highlight));
			}
		}
		if (rendering_style->hasTransmissionColour()) {
			// Not supported
		}
		if (rendering_style->hasTransparency()) {
			const double d = rendering_style->Transparency();
			surface_style.Transparency().reset(d);
		}
	}
	return &(style_cache[surface_style_id] = surface_style);
}

const IfcGeom::SurfaceStyle* IfcGeom::Kernel::get_style(const IfcSchema::IfcRepresentationItem* item) {
	return internalize_surface_style(get_surface_style<IfcSchema::IfcSurfaceStyleShading>(item));	
}

const IfcGeom::SurfaceStyle* IfcGeom::Kernel::get_style(const IfcSchema::IfcMaterial* material) {
	IfcSchema::IfcMaterialDefinitionRepresentation::list::ptr defs = material->HasRepresentation();
	for (IfcSchema::IfcMaterialDefinitionRepresentation::list::it jt = defs->begin(); jt != defs->end(); ++jt) {
		IfcSchema::IfcRepresentation::list::ptr reps = (*jt)->Representations();
		IfcSchema::IfcStyledItem::list::ptr styles(new IfcSchema::IfcStyledItem::list);
		for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
			styles->push((**it).Items()->as<IfcSchema::IfcStyledItem>());
		}
		for (IfcSchema::IfcStyledItem::list::it it = styles->begin(); it != styles->end(); ++it) {
			const std::pair<IfcSchema::IfcSurfaceStyle*, IfcSchema::IfcSurfaceStyleShading*> ss = get_surface_style<IfcSchema::IfcSurfaceStyleShading>(*it);
			if (ss.second) {
				return internalize_surface_style(ss);
			}
		}
	}
	IfcGeom::SurfaceStyle material_style = IfcGeom::SurfaceStyle(material->id(), material->Name());
	return &(style_cache[material->id()] = material_style);
}

static std::map<std::string, IfcGeom::SurfaceStyle> default_materials;
static IfcGeom::SurfaceStyle default_material;
static bool default_materials_initialized = false;

void InitDefaultMaterials() {
	default_materials.insert(std::make_pair("IfcSite", IfcGeom::SurfaceStyle("IfcSite")));
	default_materials["IfcSite"            ].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.75, 0.8, 0.65));

	default_materials.insert(std::make_pair("IfcSlab", IfcGeom::SurfaceStyle("IfcSlab")));
	default_materials["IfcSlab"            ].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.4 , 0.4, 0.4 ));
	
	default_materials.insert(std::make_pair("IfcWallStandardCase", IfcGeom::SurfaceStyle("IfcWallStandardCase")));
	default_materials["IfcWallStandardCase"].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.9 , 0.9, 0.9 ));
	
	default_materials.insert(std::make_pair("IfcWall", IfcGeom::SurfaceStyle("IfcWall")));
	default_materials["IfcWall"            ].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.9 , 0.9, 0.9 ));
	
	default_materials.insert(std::make_pair("IfcWindow", IfcGeom::SurfaceStyle("IfcWindow")));
	default_materials["IfcWindow"          ].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.75, 0.8, 0.75));
	default_materials["IfcWindow"          ].Transparency().reset(0.3);
	
	default_materials.insert(std::make_pair("IfcDoor", IfcGeom::SurfaceStyle("IfcDoor")));
	default_materials["IfcDoor"            ].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.55, 0.3, 0.15));
	
	default_materials.insert(std::make_pair("IfcBeam", IfcGeom::SurfaceStyle("IfcBeam")));
	default_materials["IfcBeam"            ].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.75, 0.7, 0.7 ));
	
	default_materials.insert(std::make_pair("IfcRailing", IfcGeom::SurfaceStyle("IfcRailing")));
	default_materials["IfcRailing"         ].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.65, 0.6, 0.6 ));
	
	default_materials.insert(std::make_pair("IfcMember", IfcGeom::SurfaceStyle("IfcMember")));
	default_materials["IfcMember"          ].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.65, 0.6, 0.6 ));
	
	default_materials.insert(std::make_pair("IfcPlate", IfcGeom::SurfaceStyle("IfcPlate")));
	default_materials["IfcPlate"           ].Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.8 , 0.8, 0.8 ));

	default_material = IfcGeom::SurfaceStyle("DefaultMaterial");
	default_material.Diffuse().reset(IfcGeom::SurfaceStyle::ColorComponent(0.7, 0.7, 0.7));

	default_materials_initialized = true;
}

boost::optional<IfcGeom::SurfaceStyle::ColorComponent> read_colour_component(const boost::optional<pt::ptree&> list) {
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
	return IfcGeom::SurfaceStyle::ColorComponent(rgb[0], rgb[1], rgb[2]);
}

void IfcGeom::set_default_style_file(const std::string& json_file) {
  if (!default_materials_initialized) InitDefaultMaterials();
  default_materials.clear();

  // @todo this will probably need to be updated for UTF-8 paths on Windows
  pt::ptree root;
  pt::read_json(json_file, root);

  for (pt::ptree::value_type &material_pair : root) {
    std::string name = material_pair.first;
    default_materials.insert(std::make_pair(name, IfcGeom::SurfaceStyle(name)));

    pt::ptree material = material_pair.second;
    boost::optional<pt::ptree&> diffuse = material.get_child_optional("diffuse");
    default_materials[name].Diffuse() = read_colour_component(diffuse);

    boost::optional<pt::ptree&> specular = material.get_child_optional("specular");
    default_materials[name].Specular() = read_colour_component(specular);

    if (material.get_child_optional("specular-roughness")) {
      default_materials[name].Specularity().reset(1.0 / material.get<double>("specular-roughness"));
    }
    if (material.get_child_optional("transparency")) {
      default_materials[name].Transparency() = material.get<double>("transparency");
    }
  }

	// Is "*" present? If yes, remove it and make it the default style.
	std::map<std::string, IfcGeom::SurfaceStyle>::const_iterator it = default_materials.find("*");
	if (it != default_materials.end()) {
		IfcGeom::SurfaceStyle star = it->second;
		default_material.Diffuse() = star.Diffuse();
		default_material.Specular() = star.Specular();
		default_material.Specularity() = star.Specularity();
		default_material.Transparency() = star.Transparency();
		default_materials.erase(it);
	}
}

const IfcGeom::SurfaceStyle* IfcGeom::get_default_style(const std::string& s) {
	if (!default_materials_initialized) InitDefaultMaterials();
	std::map<std::string, IfcGeom::SurfaceStyle>::const_iterator it = default_materials.find(s);
	if (it == default_materials.end()) {
		default_materials.insert(std::make_pair(s, IfcGeom::SurfaceStyle(s)));
		default_materials[s].Diffuse() = default_material.Diffuse();
		default_materials[s].Specular() = default_material.Specular();
		default_materials[s].Specularity() = default_material.Specularity();
		default_materials[s].Transparency() = default_material.Transparency();
		it = default_materials.find(s);
	}
	const IfcGeom::SurfaceStyle& surface_style = it->second;
	return &surface_style;
}
