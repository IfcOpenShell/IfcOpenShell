#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcAxis2Placement3D* inst) {
	Eigen::Vector3d o, axis(0, 0, 1), refDirection, X(1, 0, 0);
	{
		taxonomy::point3 v = as<taxonomy::point3>(map(inst->Location()));
		o = *v.components_;
	}
	const bool hasAxis = inst->hasAxis();
	const bool hasRef = inst->hasRefDirection();

	if (hasAxis != hasRef) {
		Logger::Warning("Axis and RefDirection should be specified together", inst);
	}

	if (hasAxis) {
		taxonomy::direction3 v = as<taxonomy::direction3>(map(inst->Axis()));
		axis = *v.components_;
	}

	if (hasRef) {
		taxonomy::direction3 v = as<taxonomy::direction3>(map(inst->RefDirection()));
		refDirection = *v.components_;
	} else {
		if (acos(axis.dot(X)) > 1.e-5) {
			refDirection = { 1., 0., 0. };
		} else {
			refDirection = { 0., 0., 1. };
		}
		auto Xvec = axis.dot(refDirection) * axis;
		auto Xaxis = refDirection - Xvec;
		refDirection = Xaxis;
	}
	return new taxonomy::matrix4(o, axis, refDirection);
}
