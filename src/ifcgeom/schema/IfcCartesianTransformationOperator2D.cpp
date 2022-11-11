#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCartesianTransformationOperator2D* inst) {
	auto m = new taxonomy::matrix4;
	
	Eigen::Vector4d origin, axis1(1.0, 0.0, 0.0, 0.0), axis2(0.0, 1.0, 0.0, 0.0), axis3(0.0, 0.0, 1.0, 0.0);
	
	taxonomy::point3 O = as<taxonomy::point3>(map(inst->LocalOrigin()));
	origin << *O.components_, 1.0;
	
	if (inst->hasAxis1()) {
		taxonomy::direction3 ax1 = as<taxonomy::direction3>(map(inst->Axis1()));
		axis1 << *ax1.components_, 0.0;
	}	
	if (inst->hasAxis2()) {
		taxonomy::direction3 ax2 = as<taxonomy::direction3>(map(inst->Axis1()));
		axis2 << *ax2.components_, 0.0;
	}

	double scale1, scale2;
	scale1 = scale2 = 1.0;

	if (inst->hasScale()) {
		scale1 = inst->Scale();
	}
	if (inst->as<IfcSchema::IfcCartesianTransformationOperator2DnonUniform>()) {
		auto nu = inst->as<IfcSchema::IfcCartesianTransformationOperator2DnonUniform>();
		scale2 = nu->hasScale2() ? nu->Scale2() : scale1;
	}

	m->components() << 
		axis1 * scale1, 
		axis2 * scale2, 
		axis3, 
		origin;

	m->components().transposeInPlace();

	return m;
}
