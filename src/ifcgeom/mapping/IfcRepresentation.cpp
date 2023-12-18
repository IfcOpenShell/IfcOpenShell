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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRepresentation* inst) {
	// @todo
	const bool use_body = !this->settings_.get<settings::IncludeCurves>().get();

	auto items = map_to_collection(this, inst->Items());
	if (!items) {
		return nullptr;
	}

	/*
	// Don't blindly flatten, as we're culling away IfcMappedItem transformations

	auto flat = flatten(items);
	if (flat == nullptr) {
		return nullptr;
	}
	*/

	// @todo
	// if (s.ShapeType() == TopAbs_COMPOUND && TopoDS_Iterator(s).More() && TopoDS_Iterator(s).Value().ShapeType() == TopAbs_SOLID) {

	auto filtered = filter_in_place(items, [&use_body](taxonomy::ptr i) {
		// @todo just filter loops for now.
		return (i->kind() != taxonomy::LOOP && i->kind() != taxonomy::PIECEWISE_FUNCTION) == use_body;
	});

	if (filtered->children.empty()) {
		return nullptr;
	}

	return filtered;
}

/*
taxonomy::ptr mapping::map_impl(const IfcSchema::IfcRepresentation* l, ConversionResults& shapes) {
	IfcSchema::IfcRepresentationItem::list::ptr items = inst->Items();
	bool part_succes = false;
	if ( items->size() ) {
		for ( IfcSchema::IfcRepresentationItem::list::it it = items->begin(); it != items->end(); ++ it ) {
			IfcSchema::IfcRepresentationptr representation_item = *it;
			if ( shape_type(representation_item) == ST_SHAPELIST ) {
				part_succes |= convert_shapes(*it, shapes);
			} else {
				TopoDS_Shape s;
				if (convert_shape(representation_item, s)) {
					if (s.ShapeType() == TopAbs_COMPOUND && TopoDS_Iterator(s).More() && TopoDS_Iterator(s).Value().ShapeType() == TopAbs_SOLID) {
						TopoDS_Iterator topo_it(s);
						for (; topo_it.More(); topo_it.Next()) {
							shapes.push_back(ConversionResult(representation_item->data().id(), topo_it.Value(), get_style(representation_item)));
						}
					} else {
						shapes.push_back(ConversionResult(representation_item->data().id(), s, get_style(representation_item)));
					}
					part_succes |= true;
				}
			}
		}
	}
	return part_succes;
}
*/