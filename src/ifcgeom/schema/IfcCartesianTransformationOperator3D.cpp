#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCartesianTransformationOperator3D* inst) {
	auto m = new taxonomy::matrix4;

	Eigen::Vector4d origin;
	Eigen::Vector4d axis1(1., 0., 0., 0.);
	Eigen::Vector4d axis2(0., 1., 0., 0.);
	Eigen::Vector4d axis3(0., 0., 1., 0.);

	taxonomy::point3 O = as<taxonomy::point3>(map(inst->LocalOrigin()));
	origin << *O.components_, 1.0;

	if (inst->hasAxis1()) {
		taxonomy::direction3 ax1 = as<taxonomy::direction3>(map(inst->Axis1()));
		axis1 << *ax1.components_, 0.0;
	}
	if (inst->hasAxis2()) {
		taxonomy::direction3 ax2 = as<taxonomy::direction3>(map(inst->Axis2()));
		axis2 << *ax2.components_, 0.0;
	}
	if (inst->hasAxis3()) {
		taxonomy::direction3 ax3 = as<taxonomy::direction3>(map(inst->Axis3()));
		axis3 << *ax3.components_, 0.0;
	}

	double scale1, scale2, scale3;
	scale1 = scale2 = scale3 = 1.;

	if (inst->hasScale()) {
		scale1 = inst->Scale();
	}
	if (inst->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>()) {
		auto nu = inst->as<IfcSchema::IfcCartesianTransformationOperator3DnonUniform>();
		scale2 = nu->hasScale2() ? nu->Scale2() : scale1;
		scale3 = nu->hasScale3() ? nu->Scale3() : scale1;
	}

	Eigen::Matrix4d tmp;
	tmp <<
		axis1 * scale1,
		axis2 * scale2,
		axis3 * scale3,
		origin;

	m->components() = tmp.inverse();
	m->components().transposeInPlace();

	// @todo tag identity?

	return m;
}
