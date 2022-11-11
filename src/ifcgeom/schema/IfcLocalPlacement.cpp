#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcLocalPlacement* inst) {
	IfcSchema::IfcLocalPlacement* current = (IfcSchema::IfcLocalPlacement*)inst;
	auto m4 = new taxonomy::matrix4;
	for (;;) {
		IfcSchema::IfcAxis2Placement* relplacement = current->RelativePlacement();
		if (relplacement->declaration().is(IfcSchema::IfcAxis2Placement3D::Class())) {
			taxonomy::matrix4 trsf2 = as<taxonomy::matrix4>(map(relplacement));
			// @todo check
			m4->components() = trsf2.ccomponents() * m4->ccomponents();
		}
		if (current->hasPlacementRelTo()) {
			IfcSchema::IfcObjectPlacement* parent = current->PlacementRelTo();
			IfcSchema::IfcProduct::list::ptr parentPlaces = parent->PlacesObject();
			bool parentPlacesType = false;
			for (IfcSchema::IfcProduct::list::it iter = parentPlaces->begin();
				iter != parentPlaces->end(); ++iter) {
				if ((*iter)->declaration().is(*placement_rel_to_)) {
					parentPlacesType = true;
				}
			}
			if (parentPlacesType) {
				break;
			} else if (parent->declaration().is(IfcSchema::IfcLocalPlacement::Class())) {
				current = (IfcSchema::IfcLocalPlacement*)current->PlacementRelTo();
			} else {
				break;
			}
		} else {
			break;
		}
	}
	return m4;
}
