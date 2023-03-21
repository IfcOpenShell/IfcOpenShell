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

taxonomy::item* mapping::map_impl(const IfcSchema::IfcMappedItem* inst) {
	IfcSchema::IfcCartesianTransformationOperator* transform = inst->MappingTarget();
	auto qqq = (taxonomy::matrix4*)map(transform);
	taxonomy::matrix4 gtrsf = *qqq;
	IfcSchema::IfcRepresentationMap* rmap = inst->MappingSource();
	IfcSchema::IfcAxis2Placement* placement = rmap->MappingOrigin();
	taxonomy::matrix4 trsf2 = *(taxonomy::matrix4*)(map(placement));
	Eigen::Matrix4d res = gtrsf.ccomponents() * trsf2.ccomponents();

	// @todo immutable for caching?
	// @todo allow for multiple levels of matrix?
	auto shapes = map(rmap->MappedRepresentation());
	if (shapes == nullptr) {
		return shapes;
	}

	auto collection = new taxonomy::collection;
	collection->children.push_back(shapes);
	collection->matrix = res;

	if (shapes != nullptr) {
		for (auto& c : ((taxonomy::collection*)shapes)->children) {
			// @todo previously style was also copied.
		}
	}

	return collection;
}
