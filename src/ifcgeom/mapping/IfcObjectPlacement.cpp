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

	const IfcSchema::IfcAxis2Placement3D* fallback = nullptr;

	if (inst->as<IfcSchema::IfcLocalPlacement>()) {
		transform = inst->as<IfcSchema::IfcLocalPlacement>()->RelativePlacement();
	}
#ifdef SCHEMA_HAS_IfcLinearPlacement
   else if (inst->as<IfcSchema::IfcLinearPlacement>()) {
#ifdef SCHEMA_IfcLinearPlacement_HAS_RelativePlacement
        transform = inst->as<IfcSchema::IfcLinearPlacement>()->RelativePlacement();
        fallback = inst->as<IfcSchema::IfcLinearPlacement>()->CartesianPosition();
#else
        // @todo Ifc4x1 and Ifc4x2 don't have RelativePlacement
        return nullptr;
#endif
    }
#endif
    else if (inst->as<IfcSchema::IfcGridPlacement>()) {
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

	taxonomy::ptr result;
	if (!parent_placement_ignored && relative_to) {
		// The parent placement of the current is a placement for a type that is
		// being ignored (Site or Building) or it is the host element of an opening.
        result = taxonomy::make<taxonomy::matrix4>(
			taxonomy::cast<taxonomy::matrix4>(map(relative_to))->ccomponents() *
			taxonomy::cast<taxonomy::matrix4>(map(transform))->ccomponents()
		);
	} else {
		result = map(transform);
	}

	if (fallback) {
        auto mapped_fallback = taxonomy::cast<taxonomy::matrix4>(map(fallback));
        if (mapped_fallback != result) {
            Logger::Warning("Computed placement differs from fallback", inst);
        }
    }

	return result;

	// @todo
	// m4->components() = offset_and_rotation_ * m4->components();
}
