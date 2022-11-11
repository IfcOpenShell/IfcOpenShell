#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcProduct* inst) {
	const bool use_body = !this->settings_.get(ifcopenshell::geometry::settings::INCLUDE_CURVES);

	auto openings = find_openings(inst);
	// @todo const cast
	auto reps = inst->data().file->traverse((IfcSchema::IfcProduct*) inst, 2)->as<IfcSchema::IfcRepresentation>();
	IfcSchema::IfcRepresentation* body = nullptr;
	for (auto& rep : *reps) {
		if ((rep->RepresentationIdentifier() == "Body") == use_body) {
			body = rep;
		}
	}
	if (!body) {
		return nullptr;
	}

	auto c = new taxonomy::collection;
	c->matrix = as<taxonomy::matrix4>(map(inst->ObjectPlacement()));

	const IfcSchema::IfcMaterial* single_material = get_single_material_association(inst);
	if (single_material) {
		auto material_style = map(single_material);
		if (material_style) {
			c->surface_style = (taxonomy::style*) material_style;
		}
	}

	if (openings->size() && !settings_.get(settings::DISABLE_OPENING_SUBTRACTIONS) && use_body) {
		
		Eigen::Matrix4d ci;
		if (c->matrix.components_) {
			ci = c->matrix.components_->inverse();
		} else {
			ci.setIdentity();
		}

		IfcEntityList::ptr operands(new IfcEntityList);
		operands->push(body);
		operands->push(openings);
		auto n = map_to_collection<taxonomy::boolean_result>(this, operands);
		std::for_each(n->children.begin() + 1, n->children.end(), [&ci](taxonomy::item* i) {
			((taxonomy::geom_item*)i)->matrix.components() = ci * ((taxonomy::geom_item*)i)->matrix.ccomponents();
		});
		n->operation = taxonomy::boolean_result::SUBTRACTION;
		// @todo one indirection too many
		n->instance = inst;
		c->children = { n };
	} else {
		auto child = map(body);
		if (child) {
			c->children = { child };
		} else {
			delete c;
			return nullptr;			
		}
	}

	return c;
}
