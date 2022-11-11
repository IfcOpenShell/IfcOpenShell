#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcFace* inst) {
	taxonomy::face* face = new taxonomy::face;
	auto bounds = inst->Bounds();
	for (auto& bound : *bounds) {
		if (auto r = map(bound->Bound())) {
			if (!bound->Orientation()) {
				r->reverse();
			}
			if (bound->declaration().is(IfcSchema::IfcFaceOuterBound::Class())) {
				((taxonomy::loop*)r)->external = true;
				/*
				// Make a copy in case we need immutability later for e.g. caching
				auto s = r->clone();
				((taxonomy::loop*)s)->external = true;
				delete r;
				r = s;
				*/
			}
			face->children.push_back(r);
		}		
	}
	if (face->children.empty()) {
		delete face;
		return nullptr;
	}
	return face;
}
