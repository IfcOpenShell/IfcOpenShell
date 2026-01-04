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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcFace& inst) {
	auto face = taxonomy::make<taxonomy::face>();
	auto bounds = inst.Bounds();
	for (auto& bound : bounds) {
		if (auto r = taxonomy::cast<taxonomy::loop>(map(bound.Bound()))) {
			if (!bound.Orientation()) {
				r->reverse();
			}
			// @todo check why loop sets external to true initially
			r->external = bound.declaration().is(IfcSchema::IfcFaceOuterBound::Class());
			/*
			// Make a copy in case we need immutability later for e.g. caching
			auto s = r->clone();
			((taxonomy::loop*)s)->external = true;
			delete r;
			r = s;
			*/
			face->children.push_back(r);
		}
	}

	auto face_surface = inst.as<IfcSchema::IfcFaceSurface>();

	if (face_surface) {
		face->basis = map(face_surface.FaceSurface());
	}

	if (face->children.empty()) {
#ifdef TAXONOMY_USE_NAKED_PTR
		delete face;
#endif
		return nullptr;
	}
	return face;
}
