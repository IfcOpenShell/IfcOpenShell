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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcMappedItem* inst) {
	IfcSchema::IfcCartesianTransformationOperator* transform = inst->MappingTarget();
	taxonomy::matrix4::ptr gtrsf = taxonomy::cast<taxonomy::matrix4>(map(transform));
	IfcSchema::IfcRepresentationMap* rmap = inst->MappingSource();
	IfcSchema::IfcAxis2Placement* placement = rmap->MappingOrigin();
	taxonomy::matrix4::ptr trsf2 = taxonomy::cast<taxonomy::matrix4>(map(placement));
	Eigen::Matrix4d res = gtrsf->ccomponents() * trsf2->ccomponents();

	// @todo immutable for caching?
	// @todo allow for multiple levels of matrix?
	auto shapes = taxonomy::dcast<taxonomy::collection>(map(rmap->MappedRepresentation()));
	if (shapes == nullptr) {
		if (failed_on_purpose_.find(rmap->MappedRepresentation()) != failed_on_purpose_.end()) {
			// propagate
			failed_on_purpose_.insert(inst);
		}
		return shapes;
	}

	auto collection = taxonomy::make<taxonomy::collection>();
	collection->children.push_back(shapes);
	collection->matrix = taxonomy::make<taxonomy::matrix4>(res);

	if (shapes != nullptr) {
		for (auto& c : taxonomy::cast<taxonomy::collection>(shapes)->children) {
			// @todo previously style was also copied.
		}
	}

	return collection;
}
