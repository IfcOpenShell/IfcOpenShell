#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcExtrudedAreaSolid* inst) {
	return new taxonomy::extrusion(
		as<taxonomy::matrix4>(map(inst->Position())),
		as<taxonomy::face>(map(inst->SweptArea())),
		as<taxonomy::direction3>(map(inst->ExtrudedDirection())),
		inst->Depth() * length_unit_
	);
}
