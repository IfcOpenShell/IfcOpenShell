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

#include <TopoDS_Wire.hxx>
#include "../ifcgeom/IfcGeom.h"
#include <memory>

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcGeometricSet* l, IfcRepresentationShapeItems& shapes) {
	// @nb the selection is partly duplicated from convert_curves() but it's needed as a
	// geometric set by it's static class definition does not inform us of the type of elements.
	// @todo handle this better so that this doesn't log an error.
	const bool include_curves = getValue(GV_DIMENSIONALITY) != +1;
	const bool include_solids_and_surfaces = getValue(GV_DIMENSIONALITY) != -1;

	aggregate_of_instance::ptr elements = l->Elements();
	if ( !elements->size() ) return false;
	bool part_succes = false;
	auto parent_style = get_style(l);
	for (aggregate_of_instance::it it = elements->begin(); it != elements->end(); ++it) {
		auto element = *it;
		TopoDS_Shape s;
		if (shape_type(element) == ST_SHAPELIST) {
			IfcRepresentationShapeItems items;
			if (!(convert_shapes(element, items) && flatten_shape_list(items, s, false))) {
				continue;
			}
		} else if (shape_type(element) == ST_SHAPE && include_solids_and_surfaces) {
			if (!convert_shape(element, s)) {
				continue;
			}
		} else if ((shape_type(element) == ST_WIRE || shape_type(element) == ST_CURVE) && include_curves) {
			TopoDS_Wire w;
			if (!convert_wire(element, w)) {
				continue;
			}
			s = w;
		} else {
			continue;
		}

		part_succes = true;
		decltype(parent_style) style = 0;
		if (element->declaration().is(IfcSchema::IfcPoint::Class())) {
			style = get_style((IfcSchema::IfcPoint*) element);
		}
		else if (element->declaration().is(IfcSchema::IfcCurve::Class())) {
			style = get_style((IfcSchema::IfcCurve*) element);
		}
		else if (element->declaration().is(IfcSchema::IfcSurface::Class())) {
			style = get_style((IfcSchema::IfcSurface*) element);
		}
		shapes.push_back(IfcRepresentationShapeItem(l->data().id(), s, style ? style : parent_style));
	}
	return part_succes;
}
