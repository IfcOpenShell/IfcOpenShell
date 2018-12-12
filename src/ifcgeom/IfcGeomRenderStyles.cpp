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

#include <map>

#include "IfcGeom.h"

namespace {

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
		} else if (colour_or_factor->declaration().is(IfcSchema::IfcColourRgb::Class())) {
			return process_colour(static_cast<IfcSchema::IfcColourRgb*>(colour_or_factor), rgb);
		} else if (colour_or_factor->declaration().is(IfcSchema::IfcNormalisedRatioMeasure::Class())) {
			return process_colour(static_cast<IfcSchema::IfcNormalisedRatioMeasure*>(colour_or_factor), rgb);
		} else {
			return false;
		}
	}

}

#define Kernel MAKE_TYPE_NAME(Kernel)

const IfcGeom::SurfaceStyle* IfcGeom::Kernel::internalize_surface_style(const std::pair<IfcUtil::IfcBaseClass*, IfcUtil::IfcBaseClass*>& shading_styles) {
	if (shading_styles.second == 0) {
		return 0;
	}
	int surface_style_id = shading_styles.first->data().id();
	std::map<int,SurfaceStyle>::const_iterator it = style_cache.find(surface_style_id);
	if (it != style_cache.end()) {
		return &(it->second);
	}
	SurfaceStyle surface_style;

	IfcSchema::IfcSurfaceStyle* style = shading_styles.first->as<IfcSchema::IfcSurfaceStyle>();
	IfcSchema::IfcSurfaceStyleShading* shading = shading_styles.second->as<IfcSchema::IfcSurfaceStyleShading>();

	if (style->hasName()) {
		surface_style = SurfaceStyle(surface_style_id, style->Name());
	} else {
		surface_style = SurfaceStyle(surface_style_id);
	}
	double rgb[3];
	if (process_colour(shading->SurfaceColour(), rgb)) {
		surface_style.Diffuse().reset(SurfaceStyle::ColorComponent(rgb[0], rgb[1], rgb[2]));
	}
	if (shading_styles.second->declaration().is(IfcSchema::IfcSurfaceStyleRendering::Class())) {
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
			if (highlight->declaration().is(IfcSchema::IfcSpecularRoughness::Class())) {
				double roughness = *((IfcSchema::IfcSpecularRoughness*)highlight);
				if (roughness >= 1e-9) {
					surface_style.Specularity().reset(1.0 / roughness);
				}
			} else if (highlight->declaration().is(IfcSchema::IfcSpecularExponent::Class())) {
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
