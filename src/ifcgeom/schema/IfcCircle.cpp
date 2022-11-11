#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCircle* inst) {
	auto c = new taxonomy::circle;
	c->matrix = as<taxonomy::matrix4>(map(inst->Position()));
	c->radius = inst->Radius() * length_unit_;
	return c;
}
