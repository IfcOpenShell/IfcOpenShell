#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcArbitraryClosedProfileDef* inst) {
	auto loop = map(inst->OuterCurve());
	if (loop) {
		auto face = new taxonomy::face;
		((taxonomy::loop*)loop)->external = true;
		face->children = { loop };
		if (inst->as<IfcSchema::IfcArbitraryProfileDefWithVoids>()) {
			auto with_voids = inst->as<IfcSchema::IfcArbitraryProfileDefWithVoids>();
			auto voids = with_voids->InnerCurves();
			for (auto& v : *voids) {
				auto inner_loop = map(v);
				if (inner_loop) {
					((taxonomy::loop*)inner_loop)->external = false;
					face->children.push_back(inner_loop);
				}
			}
		}
		return face;
	} else {
		return nullptr;
	}
}
