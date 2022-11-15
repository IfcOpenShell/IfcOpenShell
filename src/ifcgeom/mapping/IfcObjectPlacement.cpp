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

#include <gp_Trsf.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcObjectPlacement* l, gp_Trsf& trsf) {
	IN_CACHE(IfcObjectPlacement,l,gp_Trsf,trsf)
	if ( ! l->declaration().is(IfcSchema::IfcLocalPlacement::Class()) ) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported IfcObjectPlacement:", l);
		return false; 		
	}
	IfcSchema::IfcLocalPlacement* current = (IfcSchema::IfcLocalPlacement*)l;
	for (;;) {

		gp_Trsf trsf2;
		IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
		if (relplacement->as<IfcSchema::IfcAxis2Placement3D>()) {
			IfcGeom::Kernel::convert(relplacement->as<IfcSchema::IfcAxis2Placement3D>(),trsf2);
			trsf.PreMultiply(trsf2);
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

	trsf.PreMultiply(offset_and_rotation);
	
	CACHE(IfcObjectPlacement,l,trsf)
	return true;
}
