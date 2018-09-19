#include "Kernel.h"

IfcGeom::Kernel::Kernel(IfcParse::IfcFile* file) {
	if (file != 0) {
		if (file->schema() == 0) {
			throw IfcParse::IfcException("No schema associated with file");
		}

		const std::string& schema_name = file->schema()->name();
		implementation_ = impl::kernel_implementations().construct(schema_name, file);
	}
}

int IfcGeom::Kernel::count(const TopoDS_Shape& s, TopAbs_ShapeEnum t) {
	int i = 0;
	TopExp_Explorer exp(s, t);
	for (; exp.More(); exp.Next()) {
		++i;
	}
	return i;
}

IfcGeom::impl::KernelFactoryImplementation& IfcGeom::impl::kernel_implementations() {
	static KernelFactoryImplementation impl;
	return impl;
}

extern void init_KernelImplementation_Ifc2x3(IfcGeom::impl::KernelFactoryImplementation*);
extern void init_KernelImplementation_Ifc4(IfcGeom::impl::KernelFactoryImplementation*);

IfcGeom::impl::KernelFactoryImplementation::KernelFactoryImplementation() {
	init_KernelImplementation_Ifc2x3(this);
	init_KernelImplementation_Ifc4(this);
}

void IfcGeom::impl::KernelFactoryImplementation::bind(const std::string& schema_name, IfcGeom::impl::kernel_fn fn) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, fn));
}

IfcGeom::Kernel* IfcGeom::impl::KernelFactoryImplementation::construct(const std::string& schema_name, IfcParse::IfcFile* file) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	std::map<std::string, IfcGeom::impl::kernel_fn>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == end()) {
		throw IfcParse::IfcException("No geometry kernel registered for " + schema_name);
	}
	return it->second(file);
}

#define CREATE_GET_DECOMPOSING_ENTITY(IfcSchema)                                                                 \
                                                                                                                 \
IfcSchema::IfcObjectDefinition* get_decomposing_entity_impl(IfcSchema::IfcProduct* product) {                    \
	IfcSchema::IfcObjectDefinition* parent = 0;                                                                  \
                                                                                                                 \
	/* In case of an opening element, parent to the RelatingBuildingElement */                                   \
	if (product->declaration().is(IfcSchema::IfcOpeningElement::Class())) {                                      \
		IfcSchema::IfcOpeningElement* opening = (IfcSchema::IfcOpeningElement*)product;                          \
		IfcSchema::IfcRelVoidsElement::list::ptr voids = opening->VoidsElements();                               \
		if (voids->size()) {                                                                                     \
			IfcSchema::IfcRelVoidsElement* ifc_void = *voids->begin();                                           \
			parent = ifc_void->RelatingBuildingElement();                                                        \
		}                                                                                                        \
	} else if (product->declaration().is(IfcSchema::IfcElement::Class())) {                                      \
		IfcSchema::IfcElement* element = (IfcSchema::IfcElement*)product;                                        \
		IfcSchema::IfcRelFillsElement::list::ptr fills = element->FillsVoids();                                  \
		/* In case of a RelatedBuildingElement parent to the opening element */                                  \
		if (fills->size()) {                                                                                     \
			for (IfcSchema::IfcRelFillsElement::list::it it = fills->begin(); it != fills->end(); ++it) {        \
				IfcSchema::IfcRelFillsElement* fill = *it;                                                       \
				IfcSchema::IfcObjectDefinition* ifc_objectdef = fill->RelatingOpeningElement();                  \
				if (product == ifc_objectdef) continue;                                                          \
				parent = ifc_objectdef;                                                                          \
			}                                                                                                    \
		}                                                                                                        \
		/* Else simply parent to the containing structure */                                                     \
		if (!parent) {                                                                                           \
			IfcSchema::IfcRelContainedInSpatialStructure::list::ptr parents = element->ContainedInStructure();   \
			if (parents->size()) {                                                                               \
				IfcSchema::IfcRelContainedInSpatialStructure* container = *parents->begin();                     \
				parent = container->RelatingStructure();                                                         \
			}                                                                                                    \
		}                                                                                                        \
	}                                                                                                            \
                                                                                                                 \
	/* Parent decompositions to the RelatingObject */                                                            \
	if (!parent) {                                                                                               \
		IfcEntityList::ptr parents = product->data().getInverse((&IfcSchema::IfcRelAggregates::Class()), -1);    \
		parents->push(product->data().getInverse((&IfcSchema::IfcRelNests::Class()), -1));                       \
		for (IfcEntityList::it it = parents->begin(); it != parents->end(); ++it) {                              \
			IfcSchema::IfcRelDecomposes* decompose = (IfcSchema::IfcRelDecomposes*)*it;                          \
			IfcUtil::IfcBaseEntity* ifc_objectdef;                                                               \
                 																								 \
			ifc_objectdef = get_RelatingObject(decompose);                                                       \
                                                                                                                 \
			if (product == ifc_objectdef) continue;                                                              \
			parent = ifc_objectdef->as<IfcSchema::IfcObjectDefinition>();                                        \
		}                                                                                                        \
	}                                                                                                            \
	return parent;                                                                                               \
}

namespace {
	IfcUtil::IfcBaseEntity* get_RelatingObject(Ifc4::IfcRelDecomposes* decompose) {
		Ifc4::IfcRelAggregates* aggr = decompose->as<Ifc4::IfcRelAggregates>();
		if (aggr != nullptr) {
			return aggr->RelatingObject();
		}
		return nullptr;
	}

	IfcUtil::IfcBaseEntity* get_RelatingObject(Ifc2x3::IfcRelDecomposes* decompose) {
		return decompose->RelatingObject();
	}

	CREATE_GET_DECOMPOSING_ENTITY(Ifc2x3);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4);
}

IfcUtil::IfcBaseEntity* IfcGeom::Kernel::get_decomposing_entity(IfcUtil::IfcBaseEntity* inst) {
	if (inst->as<Ifc2x3::IfcProduct>()) {
		return get_decomposing_entity_impl(inst->as<Ifc2x3::IfcProduct>());
	} else if (inst->as<Ifc4::IfcProduct>()) {
		return get_decomposing_entity_impl(inst->as<Ifc4::IfcProduct>());
	} else {
		throw IfcParse::IfcException("Unexpected entity " + inst->declaration().name());
	}
}

namespace {
	template <typename Schema>
	static std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers_impl(typename Schema::IfcProduct* prod) {
		std::map<std::string, IfcUtil::IfcBaseEntity*> layers;
		if (prod->hasRepresentation()) {
			IfcEntityList::ptr r = IfcParse::traverse(prod->Representation());
			typename Schema::IfcRepresentation::list::ptr representations = r->as<typename Schema::IfcRepresentation>();
			for (typename Schema::IfcRepresentation::list::it it = representations->begin(); it != representations->end(); ++it) {
				typename Schema::IfcPresentationLayerAssignment::list::ptr a = (*it)->LayerAssignments();
				for (typename Schema::IfcPresentationLayerAssignment::list::it jt = a->begin(); jt != a->end(); ++jt) {
					layers[(*jt)->Name()] = *jt;
				}
			}

			typename Schema::IfcRepresentationItem::list::ptr items = r->as<typename Schema::IfcRepresentationItem>();
			for (typename Schema::IfcRepresentationItem::list::it it = items->begin(); it != items->end(); ++it) {
				typename Schema::IfcPresentationLayerAssignment::list::ptr a = getLayerAssignments(*it)->template as<typename Schema::IfcPresentationLayerAssignment>();
				for (typename Schema::IfcPresentationLayerAssignment::list::it jt = a->begin(); jt != a->end(); ++jt) {
					layers[(*jt)->Name()] = *jt;
				}
			}
		}
		return layers;
	}
}

std::map<std::string, IfcUtil::IfcBaseEntity*> IfcGeom::Kernel::get_layers(IfcUtil::IfcBaseEntity* inst) {
	if (inst->as<Ifc2x3::IfcProduct>()) {
		return get_layers_impl<Ifc2x3>(inst->as<Ifc2x3::IfcProduct>());
	} else if (inst->as<Ifc4::IfcProduct>()) {
		return get_layers_impl<Ifc4>(inst->as<Ifc4::IfcProduct>());
	} else {
		throw IfcParse::IfcException("Unexpected entity " + inst->declaration().name());
	}
}

