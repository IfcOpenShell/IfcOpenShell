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
	auto items_to_include = this->settings_.get<settings::OutputDimensionality>().get();

	auto items = map_to_collection(this, inst->Items());
	if (!items) {
		auto its = inst->Items();
		bool empty_on_purpose = true;
		for (auto& itm : *its) {
			if (failed_on_purpose_.find(itm) == failed_on_purpose_.end()) {
				empty_on_purpose = false;
			}
		}
		if (empty_on_purpose) {
			failed_on_purpose_.insert(inst);
		}
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

	auto filtered = filter_in_place(items, [&items_to_include](taxonomy::ptr i) {
		auto is_curve = (i->kind() == taxonomy::EDGE || i->kind() == taxonomy::LOOP || i->kind() == taxonomy::PIECEWISE_FUNCTION);
		if (is_curve && items_to_include == settings::SURFACES_AND_SOLIDS) {
			return false;
		} else if (!is_curve && items_to_include == settings::CURVES) {
			return false;
		} else {
			return true;
		}
	});

	if (filtered->children.empty()) {
		failed_on_purpose_.insert(inst);
		return nullptr;
	}

	return filtered;
}
