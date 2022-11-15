#include "Kernel.h"

#include <TopExp.hxx>
#include <TopTools_ListOfShape.hxx>
#include <TopTools_IndexedMapOfShape.hxx>
#include <TopTools_IndexedDataMapOfShapeListOfShape.hxx>

#include <TopoDS.hxx>
#include <TopoDS_Vertex.hxx>
#include <TopoDS_Edge.hxx>

#include <boost/preprocessor/stringize.hpp>
#include <boost/preprocessor/seq/for_each.hpp>

IfcGeom::Kernel::Kernel(IfcParse::IfcFile* file) {
	if (file != 0) {
		if (file->schema() == 0) {
			throw IfcParse::IfcException("No schema associated with file");
		}

		const std::string& schema_name = file->schema()->name();
		implementation_ = impl::kernel_implementations().construct(schema_name, file);
	}
}

IfcGeom::impl::KernelFactoryImplementation& IfcGeom::impl::kernel_implementations() {
	static KernelFactoryImplementation impl;
	return impl;
}

// Declares the schema-based external kernel initialization routines:
// - extern void init_KernelImplementation_Ifc2x3(IfcGeom::impl::KernelFactoryImplementation*);
// - ...
#define EXTERNAL_DEFS(r, data, elem) \
	extern void BOOST_PP_CAT(init_KernelImplementation_Ifc, elem)(IfcGeom::impl::KernelFactoryImplementation*);

// Declares the schema-based external iterator initialization routines:
// - init_IteratorImplementation_Ifc2x3(this);
// - ...
#define CALL_DEFS(r, data, elem) \
	BOOST_PP_CAT(init_KernelImplementation_Ifc, elem)(this);

BOOST_PP_SEQ_FOR_EACH(EXTERNAL_DEFS, , SCHEMA_SEQ)

IfcGeom::impl::KernelFactoryImplementation::KernelFactoryImplementation() {
	BOOST_PP_SEQ_FOR_EACH(CALL_DEFS, , SCHEMA_SEQ)
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
		aggregate_of_instance::ptr parents = product->data().getInverse((&IfcSchema::IfcRelAggregates::Class()), -1);    \
		parents->push(product->data().getInverse((&IfcSchema::IfcRelNests::Class()), -1));                       \
		for (aggregate_of_instance::it it = parents->begin(); it != parents->end(); ++it) {                      \
			IfcSchema::IfcRelDecomposes* decompose = (*it)->as<IfcSchema::IfcRelDecomposes>();                   \
			IfcUtil::IfcBaseEntity* ifc_objectdef;                                                               \
                 																								 \
			ifc_objectdef = get_RelatingObject(decompose);                                                       \
                                                                                                                 \
			if (!ifc_objectdef || product == ifc_objectdef) continue;                                            \
			parent = ifc_objectdef->as<IfcSchema::IfcObjectDefinition>();                                        \
		}                                                                                                        \
	}                                                                                                            \
	return parent;                                                                                               \
}

#define GET_RELATINGOBJECT_IFC4_VARIANT(IfcSchema)                                    \
                                                                                      \
IfcUtil::IfcBaseEntity* get_RelatingObject(IfcSchema::IfcRelDecomposes* decompose) {  \
    IfcSchema::IfcRelAggregates* aggr = decompose->as<IfcSchema::IfcRelAggregates>(); \
    if (aggr != nullptr) {                                                            \
        return aggr->RelatingObject();                                                \
    }                                                                                 \
    IfcSchema::IfcRelNests* nest = decompose->as<IfcSchema::IfcRelNests>();           \
    if (nest != nullptr) {                                                            \
        return nest->RelatingObject();                                                \
    }                                                                                 \
    return nullptr;                                                                   \
}

namespace {

#ifdef HAS_SCHEMA_2x3
	IfcUtil::IfcBaseEntity* get_RelatingObject(Ifc2x3::IfcRelDecomposes* decompose) {
		return decompose->RelatingObject();
	}
	CREATE_GET_DECOMPOSING_ENTITY(Ifc2x3);
#endif

#ifdef HAS_SCHEMA_4
	GET_RELATINGOBJECT_IFC4_VARIANT(Ifc4);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4);
#endif

#ifdef HAS_SCHEMA_4x1
	GET_RELATINGOBJECT_IFC4_VARIANT(Ifc4x1);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x1);
#endif

#ifdef HAS_SCHEMA_4x2
	GET_RELATINGOBJECT_IFC4_VARIANT(Ifc4x2);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x2);
#endif

#ifdef HAS_SCHEMA_4x3_rc1
	GET_RELATINGOBJECT_IFC4_VARIANT(Ifc4x3_rc1);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x3_rc1);
#endif

#ifdef HAS_SCHEMA_4x3_rc2
	GET_RELATINGOBJECT_IFC4_VARIANT(Ifc4x3_rc2);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x3_rc2);
#endif
	
#ifdef HAS_SCHEMA_4x3_rc3
	GET_RELATINGOBJECT_IFC4_VARIANT(Ifc4x3_rc3);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x3_rc3);
#endif

#ifdef HAS_SCHEMA_4x3_rc4
	GET_RELATINGOBJECT_IFC4_VARIANT(Ifc4x3_rc4);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x3_rc4);
#endif

#ifdef HAS_SCHEMA_4x3
	GET_RELATINGOBJECT_IFC4_VARIANT(Ifc4x3);
	CREATE_GET_DECOMPOSING_ENTITY(Ifc4x3);
#endif
}

// Declares the schema-based IfcProduct check:
// - if (inst->as<Ifc2x3::IfcProduct>()) { ... }
// - ...
#define IFCPROCUCT_CHECK(r, data, elem) \
	if (inst->as<BOOST_PP_CAT(Ifc, elem)::IfcProduct>()) { return get_decomposing_entity_impl(inst->as<BOOST_PP_CAT(Ifc, elem)::IfcProduct>(), include_openings); }

#define GET_LAYERS(r, data, elem) \
	if (inst->as<BOOST_PP_CAT(Ifc, elem)::IfcProduct>()) { return get_layers_impl<BOOST_PP_CAT(Ifc, elem)>(inst->as<BOOST_PP_CAT(Ifc, elem)::IfcProduct>()); }


IfcUtil::IfcBaseEntity* IfcGeom::Kernel::get_decomposing_entity(IfcUtil::IfcBaseEntity* inst, bool include_openings) {
	BOOST_PP_SEQ_FOR_EACH(IFCPROCUCT_CHECK, , SCHEMA_SEQ)

	if (inst->declaration().name() == "IfcProject") {
		return nullptr;
	}

	throw IfcParse::IfcException("Unexpected entity " + inst->declaration().name());
}

namespace {
	template <typename Schema>
	static std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers_impl(typename Schema::IfcProduct* prod) {
		std::map<std::string, IfcUtil::IfcBaseEntity*> layers;
		if (prod->Representation()) {
			aggregate_of_instance::ptr r = IfcParse::traverse(prod->Representation());
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
	BOOST_PP_SEQ_FOR_EACH(GET_LAYERS, , SCHEMA_SEQ)

	throw IfcParse::IfcException("Unexpected entity " + inst->declaration().name());
}
