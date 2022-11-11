#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcMappedItem* inst) {
	IfcSchema::IfcCartesianTransformationOperator* transform = inst->MappingTarget();
	taxonomy::matrix4 gtrsf = as<taxonomy::matrix4>(map(transform));
	IfcSchema::IfcRepresentationMap* rmap = inst->MappingSource();
	IfcSchema::IfcAxis2Placement* placement = rmap->MappingOrigin();
	taxonomy::matrix4 trsf2 = as<taxonomy::matrix4>(map(placement));
	// Cannot be nullptr here
	*gtrsf.components_ = *gtrsf.components_ * *trsf2.components_;
	
	// @todo immutable for caching?
	// @todo allow for multiple levels of matrix?
	auto shapes = map(rmap->MappedRepresentation());
	if (shapes == nullptr) {
		return shapes;
	}

	auto collection = new taxonomy::collection;
	collection->children.push_back(shapes);
	collection->matrix = *gtrsf.components_;

	if (shapes != nullptr) {
		for (auto& c : ((taxonomy::collection*)shapes)->children) {
			// @todo previously style was also copied.
		}
	}

	return collection;
}
