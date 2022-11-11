#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcConnectedFaceSet* inst) {
	auto shell = map_to_collection<taxonomy::shell>(this, inst->CfsFaces());
	if (shell == nullptr) {
		return nullptr;
	}
	shell->closed = inst->declaration().is(IfcSchema::IfcClosedShell::Class());
	return shell;
}
