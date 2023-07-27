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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcArbitraryClosedProfileDef* inst) {
	auto loop = taxonomy::cast<taxonomy::loop>(map(inst->OuterCurve()));
	if (loop) {
		auto face = taxonomy::make<taxonomy::face>();
		loop->external = true;
		face->children = { loop };

		if (inst->as<IfcSchema::IfcArbitraryProfileDefWithVoids>()) {
			auto with_voids = inst->as<IfcSchema::IfcArbitraryProfileDefWithVoids>();
			auto voids = with_voids->InnerCurves();
			for (auto& v : *voids) {
				auto inner_loop = taxonomy::cast<taxonomy::loop>(map(v));
				if (inner_loop) {
					inner_loop->external = false;
					face->children.push_back(inner_loop);
				}
			}
		}
		
		return face;
	} else {
		return nullptr;
	}
}
