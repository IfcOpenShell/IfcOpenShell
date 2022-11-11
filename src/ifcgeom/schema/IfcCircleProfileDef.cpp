#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#include <boost/math/constants/constants.hpp>

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCircleProfileDef* inst) {
	std::vector<double> radii = { inst->Radius() * length_unit_ };
	
	if (inst->as<IfcSchema::IfcCircleHollowProfileDef>()) {
		double t = inst->as<IfcSchema::IfcCircleHollowProfileDef>()->WallThickness() * length_unit_;
		radii.push_back(radii.front() - t);
	}

	auto f = new taxonomy::face;

	for (auto it = radii.begin(); it != radii.end(); ++it) {
		const double r = *it;
		const bool exterior = it == radii.begin();

		auto c = new taxonomy::circle;
		c->radius = r;

		bool has_position = true;
#ifdef SCHEMA_IfcParameterizedProfileDef_Position_IS_OPTIONAL
		has_position = inst->hasPosition();
#endif
		if (has_position) {
			taxonomy::matrix4 m = as<taxonomy::matrix4>(map(inst->Position()));
			if (m.components_) {
				c->matrix = *m.components_;
			}
		}

		auto e = new taxonomy::edge;
		e->basis = c;
		e->start = 0.;
		e->end = 2 * boost::math::constants::pi<double>();

		auto l = new taxonomy::loop;
		l->children = { e };
		l->external = exterior;

		f->children.push_back(l);
	}

	return f;
}
