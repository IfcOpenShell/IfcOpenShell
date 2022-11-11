#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#include "../profile_helper.h"

taxonomy::item* mapping::map_impl(const IfcSchema::IfcIShapeProfileDef* inst) {
	const double x1 = inst->OverallWidth() / 2.0f * length_unit_;
	const double y = inst->OverallDepth() / 2.0f * length_unit_;
	const double d1 = inst->WebThickness() / 2.0f  * length_unit_;
	const double dy1 = inst->FlangeThickness() * length_unit_;

	bool doFillet1 = inst->hasFilletRadius();
	double f1 = 0.;
	if (doFillet1) {
		f1 = inst->FilletRadius() * length_unit_;
	}

	bool doFillet2 = doFillet1;
	double x2 = x1, dy2 = dy1, f2 = f1;

	if (inst->declaration().is(IfcSchema::IfcAsymmetricIShapeProfileDef::Class())) {
		IfcSchema::IfcAsymmetricIShapeProfileDef* assym = (IfcSchema::IfcAsymmetricIShapeProfileDef*) inst;
		x2 = assym->TopFlangeWidth() / 2. * length_unit_;
		doFillet2 = assym->hasTopFlangeFilletRadius();
		if (doFillet2) {
			f2 = assym->TopFlangeFilletRadius() * length_unit_;
		}
		if (assym->hasTopFlangeThickness()) {
			dy2 = assym->TopFlangeThickness() * length_unit_;
		}
	}

	// @todo
	const double precision_ = 1.e-5;

	if (x1 < precision_ || x2 < precision_ || y < precision_ || d1 < precision_ || dy1 < precision_ || dy2 < precision_) {
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
		{{-x1,-y}},
		{{x1,-y}},
		{{x1,-y + dy1}},
		{{d1,-y + dy1}, f1},
		{{d1,y - dy2}, f2},
		{{x2,y - dy2}},
		{{x2,y}},
		{{-x2,y}},
		{{-x2,y - dy2}},
		{{-d1,y - dy2}, f2},
		{{-d1,-y + dy1}, f1},
		{{-x1,-y + dy1}}
	});
}
