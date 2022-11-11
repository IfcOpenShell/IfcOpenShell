#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#include "../profile_helper.h"

taxonomy::item* mapping::map_impl(const IfcSchema::IfcRectangleProfileDef* inst) {
	const double x = inst->XDim() / 2.0f * length_unit_;
	const double y = inst->YDim() / 2.0f * length_unit_;
	boost::optional<double> radius;
	if (inst->as<IfcSchema::IfcRoundedRectangleProfileDef>()) {
		radius = inst->as<IfcSchema::IfcRoundedRectangleProfileDef>()->RoundingRadius() * length_unit_;
	}
	
	// @todo
	const double precision_ = 1.e-5;

	if (x < precision_ || y < precision_) {
		Logger::Message(Logger::LOG_NOTICE, "Skipping zero sized profile:", inst);
		return nullptr;
	}

	Eigen::Matrix4d m4;
	bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
	has_position = inst->hasPosition();
#endif
	if (has_position) {
		taxonomy::matrix4 m = as<taxonomy::matrix4>(map(inst->Position()));
		m4 = m.ccomponents();
	}

	return profile_helper(m4, {
		{{-x, -y}, radius},
		{{+x, -y}, radius},
		{{+x, +y}, radius},
		{{-x, +y}, radius},
	});
}
