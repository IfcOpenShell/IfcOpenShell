#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcRepresentation* inst) {
	const bool use_body = !this->settings_.get(ifcopenshell::geometry::settings::INCLUDE_CURVES);

	auto items = map_to_collection(this, inst->Items());
	if (items == nullptr) {
		return nullptr;
	}

	/*
	// Don't blindly flatten, as we're culling away IfcMappedItem transformations

	auto flat = flatten(items);
	if (flat == nullptr) {
		return nullptr;
	}
	*/

	return filter_in_place(items, [&use_body](taxonomy::item* i) {
		// @todo just filter loops for now.
		return (i->kind() != taxonomy::LOOP) == use_body;
	});
}
