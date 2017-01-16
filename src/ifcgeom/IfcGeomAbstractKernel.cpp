#include "../ifcparse/IfcSIPrefix.h"

#include "IfcGeom.h"
#include "kernels/opencascade/OpenCascadeKernel.h"
#include "kernels/cgal/CgalKernel.h"

void IfcGeom::AbstractKernel::setValue(GeomValue var, double value) {
	switch (var) {
	case GV_DEFLECTION_TOLERANCE:
		deflection_tolerance = value;
		break;
	case GV_WIRE_CREATION_TOLERANCE:
		wire_creation_tolerance = value;
		break;
	case GV_POINT_EQUALITY_TOLERANCE:
		point_equality_tolerance = value;
		break;
	case GV_MAX_FACES_TO_SEW:
		max_faces_to_sew = value;
		break;
	case GV_LENGTH_UNIT:
		ifc_length_unit = value;
		break;
	case GV_PLANEANGLE_UNIT:
		ifc_planeangle_unit = value;
		break;
	case GV_PRECISION:
		modelling_precision = value;
		break;
	case GV_DIMENSIONALITY:
		dimensionality = value;
		break;
	default:
		assert(!"never reach here");
	}
}

double IfcGeom::AbstractKernel::getValue(GeomValue var) const {
	switch (var) {
	case GV_DEFLECTION_TOLERANCE:
		return deflection_tolerance;
	case GV_WIRE_CREATION_TOLERANCE:
		return wire_creation_tolerance;
	case GV_MINIMAL_FACE_AREA:
		// Considering a right-angled triangle, this about the smallest
		// area you can obtain without the vertices being confused.
		return modelling_precision * modelling_precision / 2.;
	case GV_POINT_EQUALITY_TOLERANCE:
		return point_equality_tolerance;
	case GV_MAX_FACES_TO_SEW:
		return max_faces_to_sew;
	case GV_LENGTH_UNIT:
		return ifc_length_unit;
		break;
	case GV_PLANEANGLE_UNIT:
		return ifc_planeangle_unit;
		break;
	case GV_PRECISION:
		return modelling_precision;
		break;
	case GV_DIMENSIONALITY:
		return dimensionality;
		break;
	}
	assert(!"never reach here");
	return 0;
}

IfcSchema::IfcRelVoidsElement::list::ptr IfcGeom::AbstractKernel::find_openings(IfcSchema::IfcProduct* product) {

	IfcSchema::IfcRelVoidsElement::list::ptr openings(new IfcSchema::IfcRelVoidsElement::list);
	if (product->is(IfcSchema::Type::IfcElement) && !product->is(IfcSchema::Type::IfcOpeningElement)) {
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
		openings = element->HasOpenings();
	}

	// Is the IfcElement a decomposition of an IfcElement with any IfcOpeningElements?
	IfcSchema::IfcObjectDefinition* obdef = product->as<IfcSchema::IfcObjectDefinition>();
	for (;;) {
#ifdef USE_IFC4
		IfcSchema::IfcRelAggregates::list::ptr decomposes = obdef->Decomposes();
#else
		IfcSchema::IfcRelDecomposes::list::ptr decomposes = obdef->Decomposes();
#endif
		if (decomposes->size() != 1) break;
		IfcSchema::IfcObjectDefinition* rel_obdef = (*decomposes->begin())->RelatingObject();
		if (rel_obdef->is(IfcSchema::Type::IfcElement) && !rel_obdef->is(IfcSchema::Type::IfcOpeningElement)) {
			IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)rel_obdef;
			openings->push(element->HasOpenings());
		}

		obdef = rel_obdef;
	}

	return openings;
}

IfcSchema::IfcObjectDefinition* IfcGeom::AbstractKernel::get_decomposing_entity(IfcSchema::IfcProduct* product) {
	IfcSchema::IfcObjectDefinition* parent = 0;

	// In case of an opening element, parent to the RelatingBuildingElement
	if (product->is(IfcSchema::Type::IfcOpeningElement)) {
		IfcSchema::IfcOpeningElement* opening = (IfcSchema::IfcOpeningElement*)product;
		IfcSchema::IfcRelVoidsElement::list::ptr voids = opening->VoidsElements();
		if (voids->size()) {
			IfcSchema::IfcRelVoidsElement* ifc_void = *voids->begin();
			parent = ifc_void->RelatingBuildingElement();
		}
	} else if (product->is(IfcSchema::Type::IfcElement)) {
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;
		IfcSchema::IfcRelFillsElement::list::ptr fills = element->FillsVoids();
		// Incase of a RelatedBuildingElement parent to the opening element
		if (fills->size()) {
			for (IfcSchema::IfcRelFillsElement::list::it it = fills->begin(); it != fills->end(); ++it) {
				IfcSchema::IfcRelFillsElement* fill = *it;
				IfcSchema::IfcObjectDefinition* ifc_objectdef = fill->RelatingOpeningElement();
				if (product == ifc_objectdef) continue;
				parent = ifc_objectdef;
			}
		}
		// Else simply parent to the containing structure
		if (!parent) {
			IfcSchema::IfcRelContainedInSpatialStructure::list::ptr parents = element->ContainedInStructure();
			if (parents->size()) {
				IfcSchema::IfcRelContainedInSpatialStructure* container = *parents->begin();
				parent = container->RelatingStructure();
			}
		}
	}
	// Parent decompositions to the RelatingObject
	if (!parent) {
		IfcEntityList::ptr parents = product->entity->getInverse(IfcSchema::Type::IfcRelAggregates, -1);
		parents->push(product->entity->getInverse(IfcSchema::Type::IfcRelNests, -1));
		for (IfcEntityList::it it = parents->begin(); it != parents->end(); ++it) {
			IfcSchema::IfcRelDecomposes* decompose = (IfcSchema::IfcRelDecomposes*)*it;
			IfcSchema::IfcObjectDefinition* ifc_objectdef;
#ifdef USE_IFC4
			if (decompose->is(IfcSchema::Type::IfcRelAggregates)) {
				ifc_objectdef = ((IfcSchema::IfcRelAggregates*)decompose)->RelatingObject();
			} else {
				continue;
			}
#else
			ifc_objectdef = decompose->RelatingObject();
#endif
			if (product == ifc_objectdef) continue;
			parent = ifc_objectdef;
		}
	}
	return parent;
}

std::pair<std::string, double> IfcGeom::AbstractKernel::initializeUnits(IfcSchema::IfcUnitAssignment* unit_assignment) {
	// Set default units, set length to meters, angles to undefined
	setValue(IfcGeom::AbstractKernel::GV_LENGTH_UNIT, 1.0);
	setValue(IfcGeom::AbstractKernel::GV_PLANEANGLE_UNIT, -1.0);

	std::string unit_name = "METER";
	double unit_magnitude = 1.;

	try {
		IfcEntityList::ptr units = unit_assignment->Units();
		if (!units || !units->size()) {
			Logger::Message(Logger::LOG_ERROR, "No unit information found");
		} else {
			for (IfcEntityList::it it = units->begin(); it != units->end(); ++it) {
				IfcUtil::IfcBaseClass* base = *it;
				if (base->is(IfcSchema::Type::IfcNamedUnit)) {
					IfcSchema::IfcNamedUnit* named_unit = base->as<IfcSchema::IfcNamedUnit>();
					if (named_unit->UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT ||
						named_unit->UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT)
					{
						std::string current_unit_name;
						const double current_unit_magnitude = IfcParse::get_SI_equivalent(named_unit);
						if (current_unit_magnitude != 0.) {
							if (named_unit->is(IfcSchema::Type::IfcConversionBasedUnit)) {
								IfcSchema::IfcConversionBasedUnit* u = (IfcSchema::IfcConversionBasedUnit*)base;
								current_unit_name = u->Name();
							} else if (named_unit->is(IfcSchema::Type::IfcSIUnit)) {
								IfcSchema::IfcSIUnit* si_unit = named_unit->as<IfcSchema::IfcSIUnit>();
								if (si_unit->hasPrefix()) {
									current_unit_name = IfcSchema::IfcSIPrefix::ToString(si_unit->Prefix()) + unit_name;
								}
								current_unit_name += IfcSchema::IfcSIUnitName::ToString(si_unit->Name());
							}
							if (named_unit->UnitType() == IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT) {
								unit_name = current_unit_name;
								unit_magnitude = current_unit_magnitude;
								setValue(IfcGeom::AbstractKernel::GV_LENGTH_UNIT, current_unit_magnitude);
							} else {
								setValue(IfcGeom::AbstractKernel::GV_PLANEANGLE_UNIT, current_unit_magnitude);
							}
						}
					}
				}
			}
		}
	} catch (const IfcParse::IfcException& ex) {
		std::stringstream ss;
		ss << "Failed to determine unit information '" << ex.what() << "'";
		Logger::Message(Logger::LOG_ERROR, ss.str());
	}

	return std::pair<std::string, double>(unit_name, unit_magnitude);
}

IfcSchema::IfcRepresentation* IfcGeom::AbstractKernel::find_representation(const IfcSchema::IfcProduct* product, const std::string& identifier) {
	if (!product->hasRepresentation()) return 0;
	IfcSchema::IfcProductRepresentation* prod_rep = product->Representation();
	IfcSchema::IfcRepresentation::list::ptr reps = prod_rep->Representations();
	for (IfcSchema::IfcRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
		if ((**it).hasRepresentationIdentifier() && (**it).RepresentationIdentifier() == identifier) {
			return *it;
		}
	}
	return 0;
}

const IfcSchema::IfcRepresentationItem* IfcGeom::AbstractKernel::find_item_carrying_style(const IfcSchema::IfcRepresentationItem* item) {
	if (item->StyledByItem()->size()) {
		return item;
	}

	while (item->is(IfcSchema::Type::IfcBooleanClippingResult)) {
		// All instantiations of IfcBooleanOperand (type of FirstOperand) are subtypes of
		// IfcGeometricRepresentationItem
		item = (IfcSchema::IfcGeometricRepresentationItem*) ((IfcSchema::IfcBooleanClippingResult*) item)->FirstOperand();
		if (item->StyledByItem()->size()) {
			return item;
		}
	}

	// TODO: Ideally this would be done for other entities (such as IfcCsgSolid) as well.
	// But neither are these very prevalent, nor does the current IfcOpenShell style
	// mechanism enable to conveniently style subshapes, which would be necessary for
	// distinctly styled union operands.

	return item;
}

IfcGeom::AbstractKernel* IfcGeom::AbstractKernel::kernel_by_name(const std::string& name) {
	if (name == "opencascade") {
		return new OpenCascadeKernel();
	} else if (name == "cgal") {
		return new CgalKernel();
	} else {
		throw std::runtime_error("No kernel named " + name);
	}
}