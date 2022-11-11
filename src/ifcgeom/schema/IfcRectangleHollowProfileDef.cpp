#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#include "../profile_helper.h"

taxonomy::item* mapping::map_impl(const IfcSchema::IfcRectangleHollowProfileDef* inst) {
	const double x = inst->XDim() / 2.0f * length_unit_;
	const double y = inst->YDim() / 2.0f * length_unit_;
	const double d = inst->WallThickness() * length_unit_;

	boost::optional<double> radius1, radius2;
	if (inst->hasOuterFilletRadius()) {
		radius1 = inst->OuterFilletRadius() * length_unit_;
	}
	if (inst->hasInnerFilletRadius()) {
		radius2 = inst->InnerFilletRadius() * length_unit_;
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

	auto outer_loop = profile_helper(m4, {
		{{-x, -y}, radius1},
		{{+x, -y}, radius1},
		{{+x, +y}, radius1},
		{{-x, +y}, radius1},
	});
	outer_loop->external = true;

	auto inner_loop = profile_helper(m4, {
		{{-x + d, -y + d}, radius2},
		{{+x - d, -y + d}, radius2},
		{{+x - d, +y - d}, radius2},
		{{-x + d, +y - d}, radius2},
	});
	inner_loop->reverse();
	inner_loop->external = false;

	auto face = new taxonomy::face;
	face->children = { outer_loop, inner_loop };

	// @todo is this necessary;
	std::swap(outer_loop->matrix, face->matrix);
	inner_loop->matrix = outer_loop->matrix;
	
	return face;
}