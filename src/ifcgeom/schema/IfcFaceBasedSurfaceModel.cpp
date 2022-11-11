#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcFaceBasedSurfaceModel* inst) {
	return map_to_collection(this, inst->FbsmFaces());
}