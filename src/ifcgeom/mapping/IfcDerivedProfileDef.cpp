/********************************************************************************
 *																			  *
 * This file is part of IfcOpenShell.										   *
 *																			  *
 * IfcOpenShell is free software: you can redistribute it and/or modify		 *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or		  *
 * (at your option) any later version.										  *
 *																			  *
 * IfcOpenShell is distributed in the hope that it will be useful,			  *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of			   *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the				 *
 * Lesser GNU General Public License for more details.						  *
 *																			  *
 * You should have received a copy of the Lesser GNU General Public License	 *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.		 *
 *																			  *
 ********************************************************************************/

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcDerivedProfileDef* inst) {
	auto it = map(inst->ParentProfile());
	if (it == nullptr) {
		return nullptr;
	}
	// @todo we mutate it so we need to clone otherwise we alter the cached item.
	it = taxonomy::item::ptr(it->clone_());

	taxonomy::matrix4::ptr m;
	bool is_mirror = false;
#ifdef SCHEMA_HAS_IfcMirroredProfileDef
	if (inst->as<IfcSchema::IfcMirroredProfileDef>()) {
		m = taxonomy::make<taxonomy::matrix4>();
		// @todo test
		m->components().col(0) *= -1.;
		is_mirror = true;
	}
#endif
	if (!is_mirror) {
		m = taxonomy::cast<taxonomy::matrix4>(map(inst->Operator()));
		if (!m) {
			return nullptr;
		}
	}
	if (!taxonomy::cast<taxonomy::geom_item>(it)->matrix) {
		// @todo should this not be initialized by default? matrix4 already has a 'lazy identity' mechanism.
		taxonomy::cast<taxonomy::geom_item>(it)->matrix = taxonomy::make<taxonomy::matrix4>();
	}
	taxonomy::cast<taxonomy::geom_item>(it)->matrix->components() *= m->ccomponents();
	return it;
}
