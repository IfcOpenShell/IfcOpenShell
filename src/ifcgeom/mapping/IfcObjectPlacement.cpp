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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcObjectPlacement* inst) {
	const IfcSchema::IfcObjectPlacement* relative_to = nullptr;
	const IfcUtil::IfcBaseInterface* transform;

#ifdef SCHEMA_HAS_IfcLinearPlacement
	if (inst->as<IfcSchema::IfcLinearPlacement>()) {
		transform = inst->as<IfcSchema::IfcLinearPlacement>()->RelativePlacement();
	}
#endif
	if (inst->as<IfcSchema::IfcLocalPlacement>()) {
		transform = inst->as<IfcSchema::IfcLocalPlacement>()->RelativePlacement();
	}
	if (inst->as<IfcSchema::IfcGridPlacement>()) {
		// @todo a bit harder to map without kernel
		return nullptr;
	}

#ifdef SCHEMA_IfcObjectPlacement_HAS_PlacementRelTo
	relative_to = inst->PlacementRelTo();
#else
	if (inst->as<IfcSchema::IfcLocalPlacement>()) {
		relative_to = inst->as<IfcSchema::IfcLocalPlacement>()->PlacementRelTo();
	}
#endif

	bool parent_placement_ignored = false;
	if (relative_to && (placement_rel_to_type_ || placement_rel_to_instance_)) {
		IfcSchema::IfcProduct::list::ptr parent_places = relative_to->PlacesObject();
		for (auto iter = parent_places->begin(); iter != parent_places->end(); ++iter) {
			if ((placement_rel_to_type_ && (*iter)->declaration().is(*placement_rel_to_type_)) ||
				(placement_rel_to_instance_ && (*iter)->as<IfcUtil::IfcBaseEntity>() == placement_rel_to_instance_)) {
				parent_placement_ignored = true;
			}
		}
	}

	if (!parent_placement_ignored && relative_to) {
		// The parent placement of the current is a placement for a type that is
		// being ignored (Site or Building) or it is the host element of an opening.
		return taxonomy::make<taxonomy::matrix4>(
			taxonomy::cast<taxonomy::matrix4>(map(relative_to))->ccomponents() *
			taxonomy::cast<taxonomy::matrix4>(map(transform))->ccomponents()
		);
	} else {
		return map(transform);
	}

	// @todo
	// m4->components() = offset_and_rotation_ * m4->components();
}
