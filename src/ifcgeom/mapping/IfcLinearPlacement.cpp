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

#if defined SCHEMA_HAS_IfcLinearPlacement

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcLinearPlacement* inst) {

	 // IfcLinearPlacement was added in IFC 4.1 but it had an Orientation attribute of type IfcOrientationExpression, which when combined with other
    // attributes was similar to IfcAxis2PlacementLinear. IFC 4.1 and IFC 4.2 have been withdrawn so I'm not going to try to implement linear placement for them.
    // For this reason the preprocessor skips this code if SCHEMA_HAS_IfcAxis2PlacementLinear is not defined
#if defined SCHEMA_HAS_IfcAxis2PlacementLinear
    // the following is taken from IfcLocalPlacement and tweaked a little
    // assumes that PlacementRelTo is relative to another IfcLinearPlacement
    IfcSchema::IfcLinearPlacement* current = (IfcSchema::IfcLinearPlacement*)inst;
    auto m4 = taxonomy::make<taxonomy::matrix4>();


	for (;;) {
        IfcSchema::IfcAxis2PlacementLinear* relplacement = current->RelativePlacement();
        m4->components() = taxonomy::cast<taxonomy::matrix4>(map(relplacement))->ccomponents() * m4->ccomponents();

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
            } else if (parent->declaration().is(IfcSchema::IfcLinearPlacement::Class())) {
				// Keep processing parent placements
                current = current->PlacementRelTo()->as<IfcSchema::IfcLinearPlacement>();
			} else {
				// This is the root placement (typically Site).
				break;
			}
		} else {
			break;
		}
	}

	 // The IFC specification does not provided a description of the optional
    // CartesianPosition attribute. It is assumed to be a pre-computed IfcAxis2Placement3D
    // to be used by software that don't support IfcLinearPlacement. Check that the
	// provided cartesian position is the same as the one determined by linear placement
    if (inst->CartesianPosition()) {
        auto m_fallback = taxonomy::cast<taxonomy::matrix4>(map(inst->CartesianPosition()));
        if (m4 != m_fallback) {
            Logger::Warning("IfcLinearPlacement.CartesianPosition is different than the computed placement", inst);
        }
    }

	 // @todo: rb - not sure what this means... it came from IfcLocalPlacement
    // m4->components() = offset_and_rotation_ * m4->components();

    return m4;

#else
	// The IFC specification does not provided a description of the optional
    // CartesianPosition attribute. It is assumed to be a pre-computed IfcAxis2Placement3D
    // to be used by software that don't support IfcLinearPlacement. In this case,
    // we will simply use the intended CartesianPosition provided by the IFC model
    if (inst->CartesianPosition()) {
        return map(inst->CartesianPosition());
    } else {
        Logger::Error("Unsupported");
    }
#endif // SCHEMA_HAS_IfcAxis2PlacementLinear
}

#endif
