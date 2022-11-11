#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCartesianPoint* inst) {
	auto coords = inst->Coordinates();
	return new taxonomy::point3(
		coords.size() >= 1 ? coords[0] * length_unit_ : 0.,
		coords.size() >= 2 ? coords[1] * length_unit_ : 0.,
		coords.size() >= 3 ? coords[2] * length_unit_ : 0.
	);
}
