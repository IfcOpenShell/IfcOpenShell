#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcHalfSpaceSolid* inst) {
	IfcSchema::IfcSurface* surface = inst->BaseSurface();
	if (!surface->declaration().is(IfcSchema::IfcPlane::Class())) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BaseSurface:", surface);
		return nullptr;
	}
	auto p = new taxonomy::plane;
	p->matrix = as<taxonomy::matrix4>(map(((IfcSchema::IfcPlane*)surface)->Position()));
	p->orientation.reset(!inst->AgreementFlag());
	auto f = new taxonomy::face;
	f->basis = p;
	return f;
}
