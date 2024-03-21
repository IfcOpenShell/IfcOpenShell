#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

using namespace IfcGeom;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcProduct* inst) {
	// @todo decide on this, what happens in the product mapping?
	// currently things like openings, layers and materials are processed in the converter
	auto c = taxonomy::make<taxonomy::collection>();
	if (inst->ObjectPlacement()) {
		c->matrix = taxonomy::cast<taxonomy::matrix4>(map(inst->ObjectPlacement()));
	} else {
		// @todo Otherwise we get crashes in the serializer, but maybe fix them there..?
		c->matrix = taxonomy::make<taxonomy::matrix4>();
	}
	return c;

	/*
	const bool use_body = !this->settings_.get(IteratorSettings::INCLUDE_CURVES);

	auto openings = find_openings(inst);
	// @todo const cast
	auto reps = inst->data().file->traverse((IfcSchema::IfcProduct*) inst, 2)->as<IfcSchema::IfcRepresentation>();
	IfcSchema::IfcRepresentation* body = nullptr;
	for (auto& rep : *reps) {
		if (rep->RepresentationIdentifier()) {
			if ((*rep->RepresentationIdentifier() == "Body") == use_body) {
				body = rep;
			}
		}
	}
	if (!body) {
		return nullptr;
	}

	auto c = new taxonomy::collection;
	c->matrix = taxonomy::cast<taxonomy::matrix4>(map(inst->ObjectPlacement()));

	const auto single_material = get_single_material_association(inst);
	if (single_material) {
		auto material_style = map(single_material);
		if (material_style) {
			c->surface_style = (taxonomy::style*) material_style;
		}
	}

	if (openings->size() && !settings_.get(IteratorSettings::DISABLE_OPENING_SUBTRACTIONS) && use_body) {
		
		Eigen::Matrix4d ci;
		if (c->matrix.components_) {
			ci = c->matrix.components_->inverse();
		} else {
			ci.setIdentity();
		}

		aggregate_of_instance::ptr operands(new aggregate_of_instance);
		operands->push(body);
		operands->push(openings);
		auto n = map_to_collection<taxonomy::boolean_result>(this, operands);
		std::for_each(n->children.begin() + 1, n->children.end(), [&ci](taxonomy::ptr i) {
			((taxonomy::geom_ptr)i)->matrix.components() = ci * ((taxonomy::geom_ptr)i)->matrix.ccomponents();
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
	*/
}
