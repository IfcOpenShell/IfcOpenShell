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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcManifoldSolidBrep* inst) {
	IfcSchema::IfcClosedShell::list::ptr voids(new IfcSchema::IfcClosedShell::list);
	if (inst->declaration().is(IfcSchema::IfcFacetedBrepWithVoids::Class())) {
		voids = inst->as<IfcSchema::IfcFacetedBrepWithVoids>()->Voids();
	}
#ifdef SCHEMA_HAS_IfcAdvancedBrepWithVoids
	if (inst->declaration().is(IfcSchema::IfcAdvancedBrepWithVoids::Class())) {
		voids = inst->as<IfcSchema::IfcAdvancedBrepWithVoids>()->Voids();
	}
#endif

	taxonomy::solid::ptr solid;
	if (voids->size()) {
		solid = map_to_collection<taxonomy::solid>(this, voids);
	} else {
		solid = taxonomy::make<taxonomy::solid>();
	}
	solid->children.insert(solid->children.begin(), taxonomy::cast<taxonomy::shell>(map(inst->Outer())));

	return solid;
}
