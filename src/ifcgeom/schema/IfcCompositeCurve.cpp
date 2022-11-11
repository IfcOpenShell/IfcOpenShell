#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcCompositeCurve* inst) {
	auto loop = new taxonomy::loop;
	auto segments = inst->Segments();
	for (auto& segment : *segments) {
		auto crv = map(segment->ParentCurve());
		if (crv) {
			if (crv->kind() == taxonomy::EDGE) {
				((taxonomy::edge*)crv)->orientation_2.reset(segment->SameSense());
				loop->children.push_back(crv);
			} else if (crv->kind() == taxonomy::LOOP) {
				if (!segment->SameSense()) {
					crv->reverse();
				}
				auto curve_segments = ((taxonomy::loop*)crv)->children_as<taxonomy::edge>();
				for (auto& s : curve_segments) {
					loop->children.push_back(s);
				}
				// @todo delete crv without children
			}
		}
	}
	IfcEntityList::ptr profile = inst->data().getInverse(&IfcSchema::IfcProfileDef::Class(), -1);
	const bool force_close = profile && profile->size() > 0;
	loop->closed = force_close;
	return loop;
}