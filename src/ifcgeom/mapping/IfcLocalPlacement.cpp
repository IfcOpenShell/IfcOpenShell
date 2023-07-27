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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcLocalPlacement* inst) {
	IfcSchema::IfcLocalPlacement* current = (IfcSchema::IfcLocalPlacement*)inst;
	auto m4 = taxonomy::make<taxonomy::matrix4>();
	for (;;) {
		IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
		// @todo this type check is wrong and unnecessary?
		if (relplacement->as<IfcSchema::IfcAxis2Placement3D>()) {
			// @todo check
			m4->components() = taxonomy::cast<taxonomy::matrix4>(map(relplacement))->ccomponents() * m4->ccomponents();
		}
		if (current->PlacementRelTo()) {
			IfcSchema::IfcObjectPlacement* parent = current->PlacementRelTo();

			bool parent_placement_ignored = false;
			if (placement_rel_to_type_ || placement_rel_to_instance_) {
				IfcSchema::IfcProduct::list::ptr parent_places = parent->PlacesObject();
				for (auto iter = parent_places->begin(); iter != parent_places->end(); ++iter) {
					if ((placement_rel_to_type_ && (*iter)->declaration().is(*placement_rel_to_type_)) ||
						(placement_rel_to_instance_ && (*iter)->as<IfcUtil::IfcBaseEntity>() == placement_rel_to_instance_)) {
						parent_placement_ignored = true;
					}
				}
			}

			if (parent_placement_ignored) {
				// The parent placement of the current is a placement for a type that is
				// being ignored (Site or Building) or it is the host element of an opening.
				break;
			} else if (parent->declaration().is(IfcSchema::IfcLocalPlacement::Class())) {
				// Keep processing parent placements
				current = current->PlacementRelTo()->as<IfcSchema::IfcLocalPlacement>();
			} else {
				// This is the root placement (typically Site).
				break;
			}
		} else {
			break;
		}
	}

	// @todo
	// m4->components() = offset_and_rotation_ * m4->components();

	return m4;
}
