#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcAxis2Placement2D* inst) {
	Eigen::Vector3d P, axis(0, 0, 1), V(1, 0, 0);
	{
		taxonomy::point3 v = as<taxonomy::point3>(map(inst->Location()));
		P = *v.components_;
	}
	const bool hasRef = inst->hasRefDirection();
	if (hasRef) {
		taxonomy::direction3 v = as<taxonomy::direction3>(map(inst->RefDirection()));
		V = *v.components_;
	}
	return new taxonomy::matrix4(P, axis, V);
}
