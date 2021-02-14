#include "Kernel.h"

#include <TopExp.hxx>
#include <TopTools_ListOfShape.hxx>
#include <TopTools_IndexedMapOfShape.hxx>
#include <TopTools_IndexedDataMapOfShapeListOfShape.hxx>

IfcGeom::Kernel::Kernel(IfcParse::IfcFile* file) {
	if (file != 0) {
		if (file->schema() == 0) {
			throw IfcParse::IfcException("No schema associated with file");
		}

		const std::string& schema_name = file->schema()->name();
		implementation_ = impl::kernel_implementations().construct(schema_name, file);
	}
}

int IfcGeom::Kernel::count(const TopoDS_Shape& s, TopAbs_ShapeEnum t, bool unique) {
	if (unique) {
		TopTools_IndexedMapOfShape map;
		TopExp::MapShapes(s, t, map);
		return map.Extent();
	} else {
		int i = 0;
		TopExp_Explorer exp(s, t);
		for (; exp.More(); exp.Next()) {
			++i;
		}
		return i;
	}
}


int IfcGeom::Kernel::surface_genus(const TopoDS_Shape& s) {
	int nv = count(s, TopAbs_VERTEX, true);
	int ne = count(s, TopAbs_EDGE, true);
	int nf = count(s, TopAbs_FACE, true);

	const int euler = nv - ne + nf;
	const int genus = (2 - euler) / 2;

	return genus;
}

IfcGeom::impl::KernelFactoryImplementation& IfcGeom::impl::kernel_implementations() {
	static KernelFactoryImplementation impl;
	return impl;
}

extern void init_KernelImplementation_Ifc2x3(IfcGeom::impl::KernelFactoryImplementation*);
extern void init_KernelImplementation_Ifc4(IfcGeom::impl::KernelFactoryImplementation*);
extern void init_KernelImplementation_Ifc4x1(IfcGeom::impl::KernelFactoryImplementation*);
extern void init_KernelImplementation_Ifc4x2(IfcGeom::impl::KernelFactoryImplementation*);
extern void init_KernelImplementation_Ifc4x3_rc1(IfcGeom::impl::KernelFactoryImplementation*);
extern void init_KernelImplementation_Ifc4x3_rc2(IfcGeom::impl::KernelFactoryImplementation*);

IfcGeom::impl::KernelFactoryImplementation::KernelFactoryImplementation() {
	init_KernelImplementation_Ifc2x3(this);
	init_KernelImplementation_Ifc4(this);
	init_KernelImplementation_Ifc4x1(this);
	init_KernelImplementation_Ifc4x2(this);
	init_KernelImplementation_Ifc4x3_rc1(this);
	init_KernelImplementation_Ifc4x3_rc2(this);
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
IfcSchema::IfcObjectDefinition* get_decomposing_entity_impl(IfcSchema::IfcProduct* product, bool include_openings) {\
	IfcSchema::IfcObjectDefinition* parent = 0;                                                                  \
                                                                                                                 \
	/* In case of an opening element, parent to the RelatingBuildingElement */                                   \
	if (include_openings && product->declaration().is(IfcSchema::IfcOpeningElement::Class())) {                  \
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
		if (fills->size() && include_openings) {                                                                 \
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
    
    IfcUtil::IfcBaseEntity* get_RelatingObject(Ifc4x1::IfcRelDecomposes* decompose) {
		Ifc4x1::IfcRelAggregates* aggr = decompose->as<Ifc4x1::IfcRelAggregates>();
		if (aggr != nullptr) {
			return aggr->RelatingObject();
		}
		return nullptr;
	}
    
    IfcUtil::IfcBaseEntity* get_RelatingObject(Ifc4x2::IfcRelDecomposes* decompose) {
		Ifc4x2::IfcRelAggregates* aggr = decompose->as<Ifc4x2::IfcRelAggregates>();
		if (aggr != nullptr) {
			return aggr->RelatingObject();
		}
		return nullptr;
	}
    
    IfcUtil::IfcBaseEntity* get_RelatingObject(Ifc4x3_rc1::IfcRelDecomposes* decompose) {
		Ifc4x3_rc1::IfcRelAggregates* aggr = decompose->as<Ifc4x3_rc1::IfcRelAggregates>();
		if (aggr != nullptr) {
			return aggr->RelatingObject();
		}
		return nullptr;
	}

	IfcUtil::IfcBaseEntity* get_RelatingObject(Ifc4x3_rc2::IfcRelDecomposes* decompose) {
		Ifc4x3_rc2::IfcRelAggregates* aggr = decompose->as<Ifc4x3_rc2::IfcRelAggregates>();
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
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x1);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x2);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x3_rc1);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x3_rc2);
}

IfcUtil::IfcBaseEntity* IfcGeom::Kernel::get_decomposing_entity(IfcUtil::IfcBaseEntity* inst, bool include_openings) {
	if (inst->as<Ifc2x3::IfcProduct>()) {
		return get_decomposing_entity_impl(inst->as<Ifc2x3::IfcProduct>(), include_openings);
	} else if (inst->as<Ifc4::IfcProduct>()) {
		return get_decomposing_entity_impl(inst->as<Ifc4::IfcProduct>(), include_openings);
	} else if (inst->as<Ifc4x1::IfcProduct>()) {
		return get_decomposing_entity_impl(inst->as<Ifc4x1::IfcProduct>(), include_openings);
	} else if (inst->as<Ifc4x2::IfcProduct>()) {
		return get_decomposing_entity_impl(inst->as<Ifc4x2::IfcProduct>(), include_openings);
	} else if (inst->as<Ifc4x3_rc1::IfcProduct>()) {
		return get_decomposing_entity_impl(inst->as<Ifc4x3_rc1::IfcProduct>(), include_openings);
	} else if (inst->as<Ifc4x3_rc2::IfcProduct>()) {
		return get_decomposing_entity_impl(inst->as<Ifc4x3_rc2::IfcProduct>(), include_openings);
	} else if (inst->declaration().name() == "IfcProject") {
		return nullptr;
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
		}
		return layers;
	}
}

std::map<std::string, IfcUtil::IfcBaseEntity*> IfcGeom::Kernel::get_layers(IfcUtil::IfcBaseEntity* inst) {
	if (inst->as<Ifc2x3::IfcProduct>()) {
		return get_layers_impl<Ifc2x3>(inst->as<Ifc2x3::IfcProduct>());
	} else if (inst->as<Ifc4::IfcProduct>()) {
		return get_layers_impl<Ifc4>(inst->as<Ifc4::IfcProduct>());
	} else if (inst->as<Ifc4x1::IfcProduct>()) {
		return get_layers_impl<Ifc4x1>(inst->as<Ifc4x1::IfcProduct>());
	} else if (inst->as<Ifc4x2::IfcProduct>()) {
		return get_layers_impl<Ifc4x2>(inst->as<Ifc4x2::IfcProduct>());
	} else if (inst->as<Ifc4x3_rc1::IfcProduct>()) {
		return get_layers_impl<Ifc4x3_rc1>(inst->as<Ifc4x3_rc1::IfcProduct>());
	} else if (inst->as<Ifc4x3_rc2::IfcProduct>()) {
		return get_layers_impl<Ifc4x3_rc2>(inst->as<Ifc4x3_rc2::IfcProduct>());
	} else {
		throw IfcParse::IfcException("Unexpected entity " + inst->declaration().name());
	}
}

bool IfcGeom::Kernel::is_manifold(const TopoDS_Shape& a) {
	if (a.ShapeType() == TopAbs_COMPOUND || a.ShapeType() == TopAbs_SOLID) {
		TopoDS_Iterator it(a);
		for (; it.More(); it.Next()) {
			if (!is_manifold(it.Value())) {
				return false;
			}
		}
		return true;
	} else {
		TopTools_IndexedDataMapOfShapeListOfShape map;
		TopExp::MapShapesAndAncestors(a, TopAbs_EDGE, TopAbs_FACE, map);

		for (int i = 1; i <= map.Extent(); ++i) {
			if (map.FindFromIndex(i).Extent() != 2) {
				return false;
			}
		}

		return true;
	}
}