/********************************************************************************
*                                                                              *
* This file is part of IfcOpenShell.                                           *
*                                                                              *
* IfcOpenShell is free software: you can redistribute it and/or modify         *
* it under the terms of the Lesser GNU General Public License as published by  *
* the Free Software Foundation, either version 3.0 of the License, or          *
* (at your option) any later version.                                          *
*                                                                              *
* IfcOpenShell is distributed in the hope that it will be useful,              *
* but WITHOUT ANY WARRANTY; without even the implied warranty of               *
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
* Lesser GNU General Public License for more details.                          *
*                                                                              *
* You should have received a copy of the Lesser GNU General Public License     *
* along with this program. If not, see <http://www.gnu.org/licenses/>.         *
*                                                                              *
********************************************************************************/

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>
#include <boost/version.hpp>
#include <boost/foreach.hpp>

#include "XmlSerializer.h"

#include <algorithm>

#include "../../ifcparse/IfcSIPrefix.h"
#include "../../ifcparse/utils.h"
#include "../../ifcparse/IfcLogger.h"

using boost::property_tree::ptree;

#include "XmlSerializer.h"

namespace {
	struct POSTFIX_SCHEMA(factory_t) {
		XmlSerializer* operator()(IfcParse::IfcFile* file, const std::string& xml_filename) const {
			POSTFIX_SCHEMA(XmlSerializer)* s = new POSTFIX_SCHEMA(XmlSerializer)(file, xml_filename);
			s->setFile(file);
			return s;
		}
	};
}

void MAKE_INIT_FN(XmlSerializer)(XmlSerializerFactory::Factory* mapping) {
	static const std::string schema_name = STRINGIFY(IfcSchema);
	POSTFIX_SCHEMA(factory_t) factory;
	mapping->bind(schema_name, factory);
}

namespace {

// TODO: Make this a member of XmlSerializer?
std::map<std::string, std::string> POSTFIX_SCHEMA(argument_name_map);

// Format an IFC attribute and maybe returns as string. Only literal scalar 
// values are converted. Things like entity instances and lists are omitted.
boost::optional<std::string> format_attribute(ifcopenshell::geometry::abstract_mapping* mapping, AttributeValue argument, IfcUtil::ArgumentType argument_type, const std::string& argument_name) {
	boost::optional<std::string> value;
	
	// Hard-code lat-lon as it represents an array
	// of integers best emitted as a single decimal
	if (argument_name == "IfcSite.RefLatitude" ||
		argument_name == "IfcSite.RefLongitude")
	{
		std::vector<int> angle = argument;
		double deg;
		if (angle.size() >= 3) {
			deg = angle[0] + angle[1] / 60. + angle[2] / 3600.;
			int prec = 8;
			if (angle.size() == 4) {
				deg += angle[3] / (1000000. * 3600.);
				prec = 14;
			}
			std::stringstream stream;
			stream << std::setprecision(prec) << deg;
			value = stream.str();
		}
		return value;
	}

	switch(argument_type) {
		case IfcUtil::Argument_BOOL: {
			const bool b = argument;
			value = b ? "true" : "false";
			break; }
		case IfcUtil::Argument_DOUBLE: {
			const double d = argument;
			std::stringstream stream;
			stream << std::setprecision (std::numeric_limits< double >::max_digits10) << d;
			value = stream.str();
			break; }
		case IfcUtil::Argument_STRING:
		case IfcUtil::Argument_ENUMERATION: {
			value = static_cast<std::string>(argument);
			break; }
		case IfcUtil::Argument_INT: {
			const int v = argument;
			std::stringstream stream;
			stream << v;
			value = stream.str();
			break; }
		case IfcUtil::Argument_ENTITY_INSTANCE: {
			IfcUtil::IfcBaseClass* e = argument;
			if (!e->declaration().as_entity()) {
				IfcUtil::IfcBaseType* f = e->as<IfcUtil::IfcBaseType>();
				value = format_attribute(mapping, f->data().get_attribute_value(0), f->data().get_attribute_value(0).type(), argument_name);
			} else if (e->declaration().is(IfcSchema::IfcSIUnit::Class()) || e->declaration().is(IfcSchema::IfcConversionBasedUnit::Class())) {
				// Some string concatenation to have a unit name as a XML attribute.

				std::string unit_name;

				if (e->declaration().is(IfcSchema::IfcSIUnit::Class())) {
					IfcSchema::IfcSIUnit* unit = e->as<IfcSchema::IfcSIUnit>();
					unit_name = IfcSchema::IfcSIUnitName::ToString(unit->Name());
					if (unit->Prefix()) {
						unit_name = IfcSchema::IfcSIPrefix::ToString(*unit->Prefix()) + unit_name;
					}
				} else {
					IfcSchema::IfcConversionBasedUnit* unit = e->as<IfcSchema::IfcConversionBasedUnit>();
					unit_name = unit->Name();
				}

				value = unit_name;
			} else if (e->declaration().is(IfcSchema::IfcLocalPlacement::Class())) {
				IfcSchema::IfcLocalPlacement* placement = e->as<IfcSchema::IfcLocalPlacement>();
				auto item = mapping->map(e);
				auto matrix = ifcopenshell::geometry::taxonomy::cast< ifcopenshell::geometry::taxonomy::matrix4>(item);
				
				std::stringstream stream;
				for (int i = 1; i < 5; ++i) {
					for (int j = 1; j < 4; ++j) {
						const double trsf_value = matrix->ccomponents()(j, i);
						stream << std::setprecision (std::numeric_limits< double >::max_digits10) << trsf_value << " ";
					}
					stream << ((i == 4) ? "1" : "0 ");
				}
				value = stream.str();

#ifdef TAXONOMY_USE_NAKED_PTR
				delete item;
#endif
			}
			break; }
        default:
            break;
	}
	return value;
}

// Appends to a node with possibly existing attributes
ptree* format_entity_instance(ifcopenshell::geometry::abstract_mapping* mapping, IfcUtil::IfcBaseEntity* instance, ptree& child, ptree& tree, bool as_link = false) {
	const unsigned n = instance->declaration().attribute_count();
	for (unsigned i = 0; i < n; ++i) {
		try {
		    instance->data().get_attribute_value(i);
		} catch (const std::exception&) {
		    Logger::Error("Expected " + boost::lexical_cast<std::string>(n) + " attributes for:", instance);
		    break;
		}		
		auto argument = instance->data().get_attribute_value(i);
		if (argument.isNull()) continue;

		std::string argument_name = instance->declaration().attribute_by_index(i)->name();
		std::map<std::string, std::string>::const_iterator argument_name_it;
		argument_name_it = POSTFIX_SCHEMA(argument_name_map).find(argument_name);
		if (argument_name_it != POSTFIX_SCHEMA(argument_name_map).end()) {
			argument_name = argument_name_it->second;
		}
		const IfcUtil::ArgumentType argument_type = instance->data().get_attribute_value(i).type();

		const std::string qualified_name = instance->declaration().name() + "." + argument_name;
		boost::optional<std::string> value;
		try {
			value = format_attribute(mapping, argument, argument_type, qualified_name);
		} catch (const std::exception& e) {
			Logger::Error(e);
		}

		if (value) {
			if (as_link) {
				if (argument_name == "id") {
					child.put("<xmlattr>.xlink:href", std::string("#") + *value);
				}
			} else {
				std::stringstream stream;
				stream << "<xmlattr>." << argument_name;
				child.put(stream.str(), *value);
			}
		}
	}
	return &tree.add_child(instance->declaration().name(), child);
}

// Formats an entity instances as a ptree node, and insert into the DOM. Recurses
// over the entity attributes and writes them as xml attributes of the node.
ptree* format_entity_instance(ifcopenshell::geometry::abstract_mapping* mapping, IfcUtil::IfcBaseEntity* instance, ptree& tree, bool as_link = false) {
    ptree child;
    return format_entity_instance(mapping, instance, child, tree, as_link);
}

std::string qualify_unrooted_instance(IfcUtil::IfcBaseInterface* inst) {
	return inst->declaration().name() + "_" + boost::lexical_cast<std::string>(inst->as<IfcUtil::IfcBaseEntity>()->id());
}

// A function to be called recursively. Template specialization is used 
// to descend into decomposition, containment and property relationships.
template <typename A>
ptree* descend(ifcopenshell::geometry::abstract_mapping* mapping, A* instance, ptree& tree, IfcUtil::IfcBaseClass* parent=nullptr) {
	if (instance->declaration().is(IfcSchema::IfcObjectDefinition::Class())) {
		return descend(mapping, instance->template as<IfcSchema::IfcObjectDefinition>(), tree, parent);
	} else {
		return format_entity_instance(mapping, instance, tree);
	}
}

// Returns related entity instances using IFC's objectified relationship
// model. The second and third argument require a member function pointer.
template <typename T, typename U, typename V, typename F, typename G>
typename V::list::ptr get_related(T* t, F f, G g) {
	typename U::list::ptr li = (*t.*f)()->template as<U>();
	typename V::list::ptr acc(new typename V::list);
	for (typename U::list::it it = li->begin(); it != li->end(); ++it) {
		U* u = *it;
		try {
			acc->push((*u.*g)()->template as<V>());
		} catch (IfcParse::IfcException& e) {
			Logger::Error(e);
		}
	}
	return acc;
}

// Descends into the tree by recursing into IfcRelContainedInSpatialStructure,
// IfcRelDecomposes, IfcRelDefinesByType, IfcRelDefinesByProperties relations.
template <>
ptree* descend(ifcopenshell::geometry::abstract_mapping* mapping, IfcSchema::IfcObjectDefinition* product, ptree& tree, IfcUtil::IfcBaseClass* parent) {
	if (product->declaration().is(IfcSchema::IfcElement::Class())) {
		auto voids = product->as<IfcSchema::IfcElement>()->FillsVoids();
		if (voids && voids->size() == 1 && (*voids->begin())->RelatingOpeningElement() != parent) {
			// Fills are placed under their corresponding opening, return early to avoid duplication.
			return nullptr;
		}
	}

	ptree& child = *format_entity_instance(mapping, product, tree);

	if (product->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
		IfcSchema::IfcOpeningElement* opening = product->as<IfcSchema::IfcOpeningElement>();
		IfcSchema::IfcElement::list::ptr fills = get_related<IfcSchema::IfcOpeningElement, IfcSchema::IfcRelFillsElement, IfcSchema::IfcElement>(
			opening, &IfcSchema::IfcOpeningElement::HasFillings, &IfcSchema::IfcRelFillsElement::RelatedBuildingElement);

		for (IfcSchema::IfcElement::list::it it = fills->begin(); it != fills->end(); ++it) {
			descend(mapping, *it, child, product);
		}
	}
	
	if (product->declaration().is(IfcSchema::IfcSpatialStructureElement::Class())) {
		IfcSchema::IfcSpatialStructureElement* structure = product->as<IfcSchema::IfcSpatialStructureElement>();

		IfcSchema::IfcObjectDefinition::list::ptr elements = get_related
			<IfcSchema::IfcSpatialStructureElement, IfcSchema::IfcRelContainedInSpatialStructure, IfcSchema::IfcObjectDefinition>
			(structure, &IfcSchema::IfcSpatialStructureElement::ContainsElements, &IfcSchema::IfcRelContainedInSpatialStructure::RelatedElements);
	
		for (IfcSchema::IfcObjectDefinition::list::it it = elements->begin(); it != elements->end(); ++it) {
			descend(mapping, *it, child, product);
		}
	}

    if (product->declaration().is(IfcSchema::IfcElement::Class())) {
		IfcSchema::IfcElement* element = static_cast<IfcSchema::IfcElement*>(product);
		IfcSchema::IfcOpeningElement::list::ptr openings = get_related<IfcSchema::IfcElement, IfcSchema::IfcRelVoidsElement, IfcSchema::IfcOpeningElement>(
            element, &IfcSchema::IfcElement::HasOpenings, &IfcSchema::IfcRelVoidsElement::RelatedOpeningElement);

        for (IfcSchema::IfcOpeningElement::list::it it = openings->begin(); it != openings->end(); ++it) {
            descend(mapping, *it, child, product);
        }
    }

#ifdef SCHEMA_IfcRelDecomposes_HAS_RelatedObjects
	IfcSchema::IfcObjectDefinition::list::ptr structures = get_related
		<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelDecomposes, IfcSchema::IfcObjectDefinition>
		(product, &IfcSchema::IfcObjectDefinition::IsDecomposedBy, &IfcSchema::IfcRelDecomposes::RelatedObjects);
#else
	IfcSchema::IfcObjectDefinition::list::ptr structures = get_related
		<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelAggregates, IfcSchema::IfcObjectDefinition>
		(product, &IfcSchema::IfcObjectDefinition::IsDecomposedBy, &IfcSchema::IfcRelAggregates::RelatedObjects);

	structures->push(get_related
		<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelNests, IfcSchema::IfcObjectDefinition>
		(product, &IfcSchema::IfcObjectDefinition::IsNestedBy, &IfcSchema::IfcRelNests::RelatedObjects));
#endif

	for (IfcSchema::IfcObjectDefinition::list::it it = structures->begin(); it != structures->end(); ++it) {
		IfcSchema::IfcObjectDefinition* ob = *it;
		descend(mapping, ob, child, product);
	}

	if (product->declaration().is(IfcSchema::IfcObject::Class())) {
		IfcSchema::IfcObject* object = product->as<IfcSchema::IfcObject>();

		IfcSchema::IfcPropertySetDefinition::list::ptr property_sets = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByProperties, IfcSchema::IfcPropertySetDefinition>
			(object, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByProperties::RelatingPropertyDefinition);

		for (IfcSchema::IfcPropertySetDefinition::list::it it = property_sets->begin(); it != property_sets->end(); ++it) {
			IfcSchema::IfcPropertySetDefinition* pset = *it;
			if (pset->declaration().is(IfcSchema::IfcPropertySet::Class())) {
				format_entity_instance(mapping, pset, child, true);
			} else if (pset->declaration().is(IfcSchema::IfcElementQuantity::Class())) {
				format_entity_instance(mapping, pset, child, true);
			}
		}

#ifdef SCHEMA_IfcObject_HAS_IsTypedBy
		IfcSchema::IfcTypeObject::list::ptr types = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByType, IfcSchema::IfcTypeObject>
			(object, &IfcSchema::IfcObject::IsTypedBy, &IfcSchema::IfcRelDefinesByType::RelatingType);
#else
		IfcSchema::IfcTypeObject::list::ptr types = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByType, IfcSchema::IfcTypeObject>
			(object, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByType::RelatingType);
#endif

		for (IfcSchema::IfcTypeObject::list::it it = types->begin(); it != types->end(); ++it) {
			IfcSchema::IfcTypeObject* type = *it;
			format_entity_instance(mapping, type, child, true);
		}
	}

    if (product->declaration().is(IfcSchema::IfcProduct::Class())) {
        std::map<std::string, IfcUtil::IfcBaseEntity*> layers = mapping->get_layers(product);
        for (std::map<std::string, IfcUtil::IfcBaseEntity*>::const_iterator it = layers.begin(); it != layers.end(); ++it) {
            // IfcPresentationLayerAssignments don't have GUIDs (only optional Identifier) so use name as the ID.
            // Note that the IfcPresentationLayerAssignment passed here doesn't really matter as as_link is true
            // for the format_entity_instance() call.
            ptree node;
            node.put("<xmlattr>.xlink:href", "#" + it->first);
            format_entity_instance(mapping, it->second, node, child, true);
        }
		
		IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
		for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
			if ((*it)->as<IfcSchema::IfcRelAssociatesMaterial>()) {
				IfcSchema::IfcMaterialSelect* mat = (*it)->as<IfcSchema::IfcRelAssociatesMaterial>()->RelatingMaterial();
				ptree node;
				node.put("<xmlattr>.xlink:href", "#" + qualify_unrooted_instance(mat));
				format_entity_instance(mapping, mat->as<IfcUtil::IfcBaseEntity>(), node, child, true);
			}
		}
    }

	return &child;
}

// Format IfcProperty instances and insert into the DOM. IfcComplexProperties are flattened out.
void format_properties(ifcopenshell::geometry::abstract_mapping* mapping, IfcSchema::IfcProperty::list::ptr properties, ptree& node) {
	for (IfcSchema::IfcProperty::list::it it = properties->begin(); it != properties->end(); ++it) {
		IfcSchema::IfcProperty* p = *it;
		if (p->declaration().is(IfcSchema::IfcComplexProperty::Class())) {
			IfcSchema::IfcComplexProperty* complex = p->as<IfcSchema::IfcComplexProperty>();
			format_properties(mapping, complex->HasProperties(), node);
		} else {
			format_entity_instance(mapping, p, node);
		}
	}
}

void writeGroupToNode(ifcopenshell::geometry::abstract_mapping* mapping, IfcSchema::IfcGroup* group, ptree& node, std::set<std::string>notRootGroups) {
	// @todo tfk: instead of a set<string> shouldn't we just have a set<IfcGroup>, the current approach
	// might not work with non-unique or NIL group names.

	// @todo tfk: should the set be a passed as a reference?
	if (!group->Name()) {
		return;
	}

    if (notRootGroups.find(*group->Name()) != notRootGroups.end()) {
        return;
    }
    // Write one group to root
    ptree* node2 = descend(mapping, group, node);
    auto father = group->IsGroupedBy();
    for (auto iter = father->begin(); iter != father->end(); iter++)
    {
        IfcSchema::IfcRelAssigns* ii = *iter;
        auto objs = ii->RelatedObjects();
        for (auto objit = objs->begin(); objit != objs->end(); objit++) {
            auto entity = *objit;
            if (entity->declaration().is(IfcSchema::IfcGroup::Class()) && entity->Name()) {
                writeGroupToNode(mapping, entity->as<IfcSchema::IfcGroup>(), *node2, notRootGroups);
                notRootGroups.emplace(*entity->Name());
            }
            else {
                // Write child to father group
                descend(mapping, entity, *node2);
            }
        }
    }
}

// Format IfcElementQuantity instances and insert into the DOM.
void format_quantities(ifcopenshell::geometry::abstract_mapping* mapping, IfcSchema::IfcPhysicalQuantity::list::ptr quantities, ptree& node) {
	for (IfcSchema::IfcPhysicalQuantity::list::it it = quantities->begin(); it != quantities->end(); ++it) {
		IfcSchema::IfcPhysicalQuantity* p = *it;
		ptree* node2 = format_entity_instance(mapping, p, node);
		if (node2 && p->declaration().is(IfcSchema::IfcPhysicalComplexQuantity::Class())) {
			IfcSchema::IfcPhysicalComplexQuantity* complex = p->as<IfcSchema::IfcPhysicalComplexQuantity>();
			format_quantities(mapping, complex->HasQuantities(), *node2);
		}
	}
}

// Format IfcTask instances and insert into the DOM.
void format_tasks(ifcopenshell::geometry::abstract_mapping* mapping, IfcSchema::IfcTask* task, ptree& node) {
	ptree* ntask = format_entity_instance(mapping, task, node);

	if (ntask) {
#ifdef SCHEMA_IfcTask_HAS_TaskTime
		IfcSchema::IfcTaskTime* task_time = task->TaskTime();
		if (task_time)
		{
			format_entity_instance(mapping, task_time, *ntask);
		}
#endif

#ifdef SCHEMA_IfcProcess_HAS_IsSuccessorFrom
		IfcSchema::IfcRelSequence::list::ptr successor_from = task->IsSuccessorFrom();
		for (IfcSchema::IfcRelSequence::list::it it = successor_from->begin(); it != successor_from->end(); ++it)
		{
			IfcSchema::IfcProcess* relating_process = (*it)->RelatingProcess();
			ptree nobject;
			nobject.put("<xmlattr>.id", relating_process->GlobalId());
			ntask->add_child("IsSuccessorFrom", nobject);
		}
#endif

#ifdef SCHEMA_IfcProcess_HAS_IsPredecessorTo
		IfcSchema::IfcRelSequence::list::ptr predecessor_to = task->IsPredecessorTo();
		for (IfcSchema::IfcRelSequence::list::it it = predecessor_to->begin(); it != predecessor_to->end(); ++it)
		{
			IfcSchema::IfcProcess* relating_process = (*it)->RelatedProcess();
			ptree nobject;
			nobject.put("<xmlattr>.id", relating_process->GlobalId());
			ntask->add_child("IsPredecessorTo", nobject);
		}
#endif

		IfcSchema::IfcPropertySetDefinition::list::ptr property_sets = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByProperties, IfcSchema::IfcPropertySetDefinition>
			(task, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByProperties::RelatingPropertyDefinition);

		for (IfcSchema::IfcPropertySetDefinition::list::it it = property_sets->begin(); it != property_sets->end(); ++it) {
			IfcSchema::IfcPropertySetDefinition* pset = *it;
			if (pset->declaration().is(IfcSchema::IfcPropertySet::Class())) {
				format_entity_instance(mapping, pset, *ntask, true);
			}
			else if (pset->declaration().is(IfcSchema::IfcElementQuantity::Class())) {
				format_entity_instance(mapping, pset, *ntask, true);
			}
		}

#ifdef SCHEMA_IfcProcess_HAS_OperatesOn
		IfcSchema::IfcRelAssignsToProcess::list::ptr operates = task->OperatesOn();
		if (operates->size() > 0)
		{
			for (IfcSchema::IfcRelAssignsToProcess::list::it i = operates->begin(); i != operates->end(); ++i)
			{
				IfcSchema::IfcRelAssignsToProcess* operation = (*i);
				IfcSchema::IfcObjectDefinition::list::ptr objects = operation->RelatedObjects();
				for (IfcSchema::IfcObjectDefinition::list::it it2 = objects->begin(); it2 != objects->end(); ++it2)
				{
					IfcSchema::IfcObjectDefinition* object = *it2;
					ptree nobject;
					nobject.put("<xmlattr>.id", object->GlobalId());
					if (object->declaration().is(IfcSchema::IfcProduct::Class()))
					{
						ntask->add_child("Input", nobject);
					}
					else if (object->declaration().is(IfcSchema::IfcResource::Class()))
					{
						ntask->add_child("Resource", nobject);
					}
					else if (object->declaration().is(IfcSchema::IfcControl::Class()))
					{
						ntask->add_child("Control", nobject);
					}
					else
					{
						nobject.put("<xmlattr>.Type", object->declaration().name());
						ntask->add_child("OperatesOn", nobject);
					}
				}
			}
		}
#endif

		IfcSchema::IfcRelAssigns::list::ptr assignments = task->HasAssignments();
		for (IfcSchema::IfcRelAssigns::list::it i = assignments->begin(); i != assignments->end(); ++i)
		{
			IfcSchema::IfcRelAssigns* assignment = *i;
			if (assignment->declaration().is(IfcSchema::IfcRelAssignsToProduct::Class())) {
				IfcSchema::IfcRelAssignsToProduct* assign_to_product = assignment->as<IfcSchema::IfcRelAssignsToProduct>();
				IfcSchema::IfcProduct* product = assign_to_product->RelatingProduct()->as<IfcSchema::IfcProduct>();
				ptree nobject;
				nobject.put("<xmlattr>.id", product->GlobalId());
				ntask->add_child("Output", nobject);
			}
		}

#ifdef SCHEMA_IfcObjectDefinition_HAS_IsNestedBy
		IfcSchema::IfcRelNests::list::ptr nested_by = task->IsNestedBy();
		for (IfcSchema::IfcRelNests::list::it it = nested_by->begin(); it != nested_by->end(); ++it)
		{
			IfcSchema::IfcObjectDefinition::list::ptr related_objects = (*it)->RelatedObjects();
			for (IfcSchema::IfcObjectDefinition::list::it it2 = related_objects->begin(); it2 != related_objects->end(); ++it2)
			{
				if (!(*it2)->declaration().is(IfcSchema::IfcTask::Class())) {
					continue;
				}
				IfcSchema::IfcTask* task2 = (*it2)->as<IfcSchema::IfcTask>();
				format_tasks(mapping, task2, *ntask);
			}
		}
#endif
	}
}

} // ~unnamed namespace

void POSTFIX_SCHEMA(XmlSerializer)::finalize() {
	POSTFIX_SCHEMA(argument_name_map).insert(std::make_pair("GlobalId", "id"));

	IfcSchema::IfcProject::list::ptr projects = file->instances_by_type<IfcSchema::IfcProject>();
	if (projects->size() != 1) {
		Logger::Message(Logger::LOG_ERROR, "Expected a single IfcProject");
		return;
	}
	IfcSchema::IfcProject* project = *projects->begin();

	ptree root, header, units, decomposition, properties, quantities, types, layers, materials, work, calendars, connections, groups;

	// Write the SPF header as XML nodes.
	BOOST_FOREACH(const std::string& s, file->header().file_description().description()) {
		header.add_child("file_description.description", ptree(s));
	}
	BOOST_FOREACH(const std::string& s, file->header().file_name().author()) {
		header.add_child("file_name.author", ptree(s));
	}
	BOOST_FOREACH(const std::string& s, file->header().file_name().organization()) {
		header.add_child("file_name.organization", ptree(s));
	}
	BOOST_FOREACH(const std::string& s, file->header().file_schema().schema_identifiers()) {
		header.add_child("file_schema.schema_identifiers", ptree(s));
	}
	try {
		header.put("file_description.implementation_level", file->header().file_description().implementation_level());
	}
	catch (const IfcParse::IfcException& ex) {
		std::stringstream ss;
		ss << "Failed to get ifc file header file_description implementation_level, error: '" << ex.what() << "'";
		Logger::Message(Logger::LOG_ERROR, ss.str());
	}
	try {
		header.put("file_name.name", file->header().file_name().name());
	}
	catch (const IfcParse::IfcException& ex) {
		std::stringstream ss;
		ss << "Failed to get ifc file header file_name name, error: '" << ex.what() << "'";
		Logger::Message(Logger::LOG_ERROR, ss.str());
	}
    try {
        header.put("file_name.time_stamp", file->header().file_name().time_stamp());
    }
    catch (const IfcParse::IfcException& ex) {
        std::stringstream ss;
        ss << "Failed to get ifc file header file_name time_stamp, error: '" << ex.what() << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }
    try {
        header.put("file_name.preprocessor_version", file->header().file_name().preprocessor_version());
    }
    catch (const IfcParse::IfcException& ex) {
        std::stringstream ss;
        ss << "Failed to get ifc file header file_name preprocessor_version, error: '" << ex.what() << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }
    try {
        header.put("file_name.originating_system", file->header().file_name().originating_system());
    }
    catch (const IfcParse::IfcException& ex) {
        std::stringstream ss;
        ss << "Failed to get ifc file header file_name originating_system, error: '" << ex.what() << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }
    try {
        header.put("file_name.authorization", file->header().file_name().authorization());
    }
    catch (const IfcParse::IfcException& ex) {
        std::stringstream ss;
        ss << "Failed to get ifc file header file_name authorization, error: '" << ex.what() << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }

	// Descend into the decomposition structure of the IFC file.
	descend(mapping_, project, decomposition);

	// Write all property sets and values as XML nodes.
	IfcSchema::IfcPropertySet::list::ptr psets = file->instances_by_type<IfcSchema::IfcPropertySet>();
	for (IfcSchema::IfcPropertySet::list::it it = psets->begin(); it != psets->end(); ++it) {
		IfcSchema::IfcPropertySet* pset = *it;
		ptree* node = format_entity_instance(mapping_, pset, properties);
		if (node) {
			format_properties(mapping_, pset->HasProperties(), *node);
		}
	}

	// Write all group sets and values as XML nodes.
	IfcSchema::IfcGroup::list::ptr gsets = file->instances_by_type<IfcSchema::IfcGroup>();
	std::set<std::string> notRootGroups; //selfname, fathername
	for (IfcSchema::IfcGroup::list::it it = gsets->begin(); it != gsets->end(); ++it) {
		writeGroupToNode(mapping_, *it, groups, notRootGroups);
	}
	for (auto it = groups.begin(); it != groups.end();) {
		if (notRootGroups.find(it->second.get<std::string>("<xmlattr>.Name")) != notRootGroups.end()) {
			it = groups.erase(it);
		} else {
			it++;
		}
	}

	// Write all quantities and values as XML nodes.
	IfcSchema::IfcElementQuantity::list::ptr qtosets = file->instances_by_type<IfcSchema::IfcElementQuantity>();
	for (IfcSchema::IfcElementQuantity::list::it it = qtosets->begin(); it != qtosets->end(); ++it) {
		IfcSchema::IfcElementQuantity* qto = *it;
		ptree* node = format_entity_instance(mapping_, qto, quantities);
		if (node) {
			format_quantities(mapping_, qto->Quantities(), *node);
		}
	}

	// Write all work schedules and values as XML nodes.
	ptree pwork_schedules;
	IfcSchema::IfcWorkSchedule::list::ptr pschedules = file->instances_by_type<IfcSchema::IfcWorkSchedule>();
	for (IfcSchema::IfcWorkSchedule::list::it it = pschedules->begin(); it != pschedules->end(); ++it) {
		IfcSchema::IfcWorkSchedule* schedule = *it;
		ptree* nschedule = format_entity_instance(mapping_, schedule, pwork_schedules);
		
		if(nschedule) {
			IfcSchema::IfcRelAssignsToControl::list::ptr controls = schedule->Controls();
			for(IfcSchema::IfcRelAssignsToControl::list::it it2 = controls->begin(); it2 != controls->end(); ++it2) {
				IfcSchema::IfcRelAssignsToControl* control = *it2;
				
				IfcSchema::IfcObjectDefinition::list::ptr objects = control->RelatedObjects();
				for(IfcSchema::IfcObjectDefinition::list::it it3 = objects->begin(); it3 != objects->end(); ++it3) {
					IfcSchema::IfcObjectDefinition* object = *it3;
					
					if (object && object->declaration().is(IfcSchema::IfcTask::Class())) {
						IfcSchema::IfcTask* task = object->as<IfcSchema::IfcTask>();
						format_tasks(mapping_, task, *nschedule);
					}
				}
			}
		}
	}
	work.add_child("schedules", pwork_schedules);

	// Write all work plans and values as XML nodes.
	ptree pwork_plans;
	IfcSchema::IfcWorkPlan::list::ptr pplans = file->instances_by_type<IfcSchema::IfcWorkPlan>();
	for (IfcSchema::IfcWorkPlan::list::it it = pplans->begin(); it != pplans->end(); ++it) {
		IfcSchema::IfcWorkPlan* plan = *it;
		ptree* nschedule = format_entity_instance(mapping_, plan, pwork_plans);

		if (nschedule) {
#ifdef SCHEMA_IfcObjectDefinition_HAS_IsDecomposedBy
			auto decomposed_by = plan->IsDecomposedBy();
			for (auto it2 = decomposed_by->begin(); it2 != decomposed_by->end(); ++it2)
			{
				IfcSchema::IfcObjectDefinition::list::ptr related_objects = (*it2)->RelatedObjects();
				for (IfcSchema::IfcObjectDefinition::list::it it3 = related_objects->begin(); it3 != related_objects->end(); ++it3)
				{
					IfcSchema::IfcObjectDefinition* work_schedule = *it3;
					ptree pwork_schedule;
					pwork_schedule.put("<xmlattr>.id", work_schedule->GlobalId());
					nschedule->add_child("IfcWorkSchedule", pwork_schedule);
				}
			}
#endif
		}
	}
	work.add_child("plans", pwork_plans);
	
	// Write all work calendars and values as XML nodes.
#ifdef SCHEMA_HAS_IfcWorkCalendar
	IfcSchema::IfcWorkCalendar::list::ptr pcalendars = file->instances_by_type<IfcSchema::IfcWorkCalendar>();
	for (IfcSchema::IfcWorkCalendar::list::it it = pcalendars->begin(); it != pcalendars->end(); ++it) {
		IfcSchema::IfcWorkCalendar* calendar = *it;
		ptree* ncalendar = format_entity_instance(mapping_, calendar, calendars);
		
		if (ncalendar) {
			IfcSchema::IfcWorkTime::list::ptr working_times = calendar->WorkingTimes().value_or(nullptr);
			if (working_times != nullptr) {
				for (IfcSchema::IfcWorkTime::list::it it2 = working_times->begin(); it2 != working_times->end(); ++it2)
				{
					IfcSchema::IfcWorkTime* working_time = *it2;
					format_entity_instance(mapping_, working_time, *ncalendar);
				}
			}
		}
	}
#endif
	
	IfcSchema::IfcRelConnectsElements::list::ptr pconnections = file->instances_by_type<IfcSchema::IfcRelConnectsElements>();
	for (IfcSchema::IfcRelConnectsElements::list::it it = pconnections->begin(); it != pconnections->end(); ++it) {
		IfcSchema::IfcRelConnectsElements* connection = *it;

		ptree* nconnection = format_entity_instance(mapping_, connection, connections);

		ptree nrelatedElement;
		ptree nrelatingElement;

		format_entity_instance(mapping_,connection->RelatedElement(), nrelatedElement, true);
		format_entity_instance(mapping_,connection->RelatingElement(), nrelatingElement, true);
		
		nconnection->add_child("RelatedElement",  nrelatedElement);
		nconnection->add_child("RelatingElement", nrelatingElement);
	}

	// Write all type objects as XML nodes.
	IfcSchema::IfcTypeObject::list::ptr type_objects = file->instances_by_type<IfcSchema::IfcTypeObject>();
	for (IfcSchema::IfcTypeObject::list::it it = type_objects->begin(); it != type_objects->end(); ++it) {
		IfcSchema::IfcTypeObject* type_object = *it;
		ptree* node = descend(mapping_, type_object, types);
		
		if (node && type_object->HasPropertySets()) {
			IfcSchema::IfcPropertySetDefinition::list::ptr property_sets = *type_object->HasPropertySets();
			for (IfcSchema::IfcPropertySetDefinition::list::it jt = property_sets->begin(); jt != property_sets->end(); ++jt) {
				IfcSchema::IfcPropertySetDefinition* pset = *jt;
				if (pset->declaration().is(IfcSchema::IfcPropertySet::Class())) {
					format_entity_instance(mapping_, pset, *node, true);
				}
			}
		}
	}

	// Write all assigned units as XML nodes.
	auto unit_assignments = project->UnitsInContext()->Units();
	for (auto it = unit_assignments->begin(); it != unit_assignments->end(); ++it) {
		if ((*it)->declaration().is(IfcSchema::IfcNamedUnit::Class())) {
			IfcSchema::IfcNamedUnit* named_unit = (*it)->as<IfcSchema::IfcNamedUnit>();
			ptree* node = format_entity_instance(mapping_, named_unit, units);
			if (node) {
				node->put("<xmlattr>.SI_equivalent", IfcParse::get_SI_equivalent<IfcSchema>(named_unit));
			}
		} else if ((*it)->declaration().is(IfcSchema::IfcMonetaryUnit::Class())) {
			format_entity_instance(mapping_, (*it)->as<IfcSchema::IfcMonetaryUnit>(), units);
		}
	}

    // Layer assignments. IfcPresentationLayerAssignments don't have GUIDs (only optional Identifier)
    // so use names as the IDs and only insert those with unique names. In case of possible duplicate names/IDs
    // the first IfcPresentationLayerAssignment occurrence takes precedence.
    std::set<std::string> layer_names;
	IfcSchema::IfcPresentationLayerAssignment::list::ptr layer_assignments = file->instances_by_type<IfcSchema::IfcPresentationLayerAssignment>();
    for (IfcSchema::IfcPresentationLayerAssignment::list::it it = layer_assignments->begin(); it != layer_assignments->end(); ++it) {
        const std::string& name = (*it)->Name();
        if (layer_names.find(name) == layer_names.end()) {
            layer_names.insert(name);
            ptree node;
            node.put("<xmlattr>.id", name);
            format_entity_instance(mapping_, *it, node, layers);
        }
    }

	IfcSchema::IfcRelAssociatesMaterial::list::ptr materal_associations = file->instances_by_type<IfcSchema::IfcRelAssociatesMaterial>();
	std::set<IfcSchema::IfcMaterialSelect*> emitted_materials;
	for (IfcSchema::IfcRelAssociatesMaterial::list::it it = materal_associations->begin(); it != materal_associations->end(); ++it) {
		IfcSchema::IfcMaterialSelect* mat = (**it).RelatingMaterial();
		if (emitted_materials.find(mat) == emitted_materials.end()) {
			emitted_materials.insert(mat);
			ptree node;
			node.put("<xmlattr>.id", qualify_unrooted_instance(mat));
			if (mat->as<IfcSchema::IfcMaterialLayerSetUsage>() || mat->as<IfcSchema::IfcMaterialLayerSet>()) {				
				IfcSchema::IfcMaterialLayerSet* layerset = mat->as<IfcSchema::IfcMaterialLayerSet>();
				if (!layerset) {
					layerset = mat->as<IfcSchema::IfcMaterialLayerSetUsage>()->ForLayerSet();
				}				
				if (layerset->LayerSetName()) {
					node.put("<xmlattr>.LayerSetName", *layerset->LayerSetName());
				}
				IfcSchema::IfcMaterialLayer::list::ptr ls = layerset->MaterialLayers();
				for (IfcSchema::IfcMaterialLayer::list::it jt = ls->begin(); jt != ls->end(); ++jt) {
					ptree subnode;
					if ((*jt)->Material()) {
						subnode.put("<xmlattr>.Name", (*jt)->Material()->Name());
					}
					format_entity_instance(mapping_, *jt, subnode, node);
				}
			} else if (mat->as<IfcSchema::IfcMaterialList>()) {
				IfcSchema::IfcMaterial::list::ptr mats = mat->as<IfcSchema::IfcMaterialList>()->Materials();
				for (IfcSchema::IfcMaterial::list::it jt = mats->begin(); jt != mats->end(); ++jt) {
					ptree subnode;
					format_entity_instance(mapping_, *jt, subnode, node);
				}
			}
			format_entity_instance(mapping_, mat->as<IfcUtil::IfcBaseEntity>(), node, materials);
		}
	}

	root.add_child("ifc.header",        header);
	root.add_child("ifc.units",         units);
	root.add_child("ifc.connections",   connections);
	root.add_child("ifc.properties",    properties);
	root.add_child("ifc.quantities",    quantities);
	root.add_child("ifc.work",			work);
	root.add_child("ifc.calendars",		calendars);
	root.add_child("ifc.types",         types);
	root.add_child("ifc.layers",        layers);
    root.add_child("ifc.groups",        groups);
	root.add_child("ifc.materials",     materials);
	root.add_child("ifc.decomposition", decomposition);

	root.put("ifc.<xmlattr>.xmlns:xlink", "http://www.w3.org/1999/xlink");

#if BOOST_VERSION >= 105600
	boost::property_tree::xml_writer_settings<ptree::key_type> settings = boost::property_tree::xml_writer_make_settings<ptree::key_type>('\t', 1);
#else
	boost::property_tree::xml_writer_settings<char> settings('\t', 1);
#endif
	
	std::ofstream f(IfcUtil::path::from_utf8(xml_filename).c_str());
	boost::property_tree::write_xml(f, root, settings);
}
