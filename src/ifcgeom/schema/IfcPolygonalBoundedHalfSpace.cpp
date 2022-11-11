#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcPolygonalBoundedHalfSpace* inst) {
	auto f = map_impl((IfcSchema::IfcHalfSpaceSolid*) inst);
	((taxonomy::face*)f)->children = { map(inst->PolygonalBoundary()) };
	((taxonomy::face*)f)->matrix = as<taxonomy::matrix4>(map(inst->Position()));
	return f;
}
