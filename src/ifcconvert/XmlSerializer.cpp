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

#include <map>

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>
#include <boost/foreach.hpp>
#include <boost/version.hpp>

#include "XmlSerializer.h"

#include <algorithm>

using boost::property_tree::ptree;
using namespace IfcSchema;

static std::map<std::string, std::string> argument_name_map;

// Format an IFC attribute and maybe returns as string. Only literal scalar 
// values are converted. Things like entity instances and lists are omitted.
boost::optional<std::string> format_attribute(const Argument* argument, IfcUtil::ArgumentType argument_type) {
	boost::optional<std::string> value;
	switch(argument_type) {
		case IfcUtil::Argument_BOOL: {
			const bool b = *argument;
			value = b ? "true" : "false";
			break; }
		case IfcUtil::Argument_DOUBLE: {
			const double d = *argument;
			std::stringstream stream;
			stream << d;
			value = stream.str();
			break; }
		case IfcUtil::Argument_STRING:
		case IfcUtil::Argument_ENUMERATION: {
			value = static_cast<std::string>(*argument);
			break; }
		case IfcUtil::Argument_INT: {
			const int v = *argument;
			std::stringstream stream;
			stream << v;
			value = stream.str();
			break; }
		case IfcUtil::Argument_ENTITY_INSTANCE: {
			IfcUtil::IfcBaseClass* e = *argument;
			if (Type::IsSimple(e->declaration().type())) {
				IfcUtil::IfcBaseType* f = (IfcUtil::IfcBaseType*) e;
				value = format_attribute(f->data().getArgument(0), f->data().getArgument(0)->type());
			} else if (e->declaration().is(IfcSchema::Type::IfcSIUnit) || e->declaration().is(IfcSchema::Type::IfcConversionBasedUnit)) {
				// Some string concatenation to have a unit name as a XML attribute.

				std::string unit_name;

				if (e->declaration().is(IfcSchema::Type::IfcSIUnit)) {
					IfcSchema::IfcSIUnit* unit = (IfcSchema::IfcSIUnit*) e;
					unit_name = IfcSchema::IfcSIUnitName::ToString(unit->Name());
					if (unit->hasPrefix()) {
						unit_name = IfcSchema::IfcSIPrefix::ToString(unit->Prefix()) + unit_name;
					}
				} else {
					IfcSchema::IfcConversionBasedUnit* unit = (IfcSchema::IfcConversionBasedUnit*) e;
					unit_name = unit->Name();
				}

				// TODO add toLower() and toUpper() string helper functions for the project
				std::transform(unit_name.begin(), unit_name.end(), unit_name.begin(), ::tolower);

				value = unit_name;
			}
			break; }
	}
	return value;
}

// Formats an entity instances as a ptree node, and insert into the DOM. Recurses
// over the entity attributes and writes them as xml attributes of the node.
ptree& format_entity_instance(IfcUtil::IfcBaseEntity* instance, ptree& tree, bool as_link = false) {
	ptree child;
	const unsigned n = instance->data().getArgumentCount();
	std::vector<const IfcParse::entity::attribute*> attributes = instance->declaration().all_attributes();

	for (unsigned i = 0; i < n; ++i) {
		const Argument* argument = instance->data().getArgument(i);
		if (argument->isNull()) continue;

		std::string argument_name = attributes[i]->name();
		std::map<std::string, std::string>::const_iterator argument_name_it;
		argument_name_it = argument_name_map.find(argument_name);
		if (argument_name_it != argument_name_map.end()) {
			argument_name = argument_name_it->second;
		}
		const IfcUtil::ArgumentType argument_type = instance->data().getArgument(i)->type();

		boost::optional<std::string> value;
		try {
			value = format_attribute(argument, argument_type);
		} catch (...) {}

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
	return tree.add_child(Type::ToString(instance->declaration().type()), child);
}

// A function to be called recursively. Template specialization is used 
// to descend into decomposition, containment and property relationships.
template <typename A>
void descend(A* instance, ptree& tree) {
	format_entity_instance(instance, tree);
}

// Returns related entity instances using IFC's objectified relationship
// model. The second and third argument require a member function pointer.
template <typename T, typename U, typename V, typename F, typename G>
typename V::list::ptr get_related(T* t, F f, G g) {
	typename U::list::ptr li = (*t.*f)()->template as<U>();
	typename V::list::ptr acc(new typename V::list);
	for (typename U::list::it it = li->begin(); it != li->end(); ++it) {
		U* u = *it;
		acc->push((*u.*g)()->template as<V>());
	}
	return acc;
}

// Descends into the tree by recursing into IfcRelContainedInSpatialStructure,
// IfcRelDecomposes and IfcRelDefinesByProperties relations.
template <>
void descend(IfcProduct* product, ptree& tree) {
	ptree& child = format_entity_instance(product, tree);
	
	if (product->declaration().is(Type::IfcSpatialStructureElement)) {
		IfcSpatialStructureElement* structure = (IfcSpatialStructureElement*) product;

		IfcProduct::list::ptr elements = get_related
			<IfcSpatialStructureElement, IfcRelContainedInSpatialStructure, IfcProduct>
			(structure, &IfcSpatialStructureElement::ContainsElements, &IfcRelContainedInSpatialStructure::RelatedElements);
	
		for (IfcProduct::list::it it = elements->begin(); it != elements->end(); ++it) {
			descend(*it, child);
		}
	}

#ifdef USE_IFC2x3
	IfcObjectDefinition::list::ptr structures = get_related
		<IfcProduct, IfcRelDecomposes, IfcObjectDefinition>
		(product, &IfcProduct::IsDecomposedBy, &IfcRelDecomposes::RelatedObjects);
#else
	IfcObjectDefinition::list::ptr structures = get_related
		<IfcProduct, IfcRelAggregates, IfcObjectDefinition>
		(product, &IfcProduct::IsDecomposedBy, &IfcRelAggregates::RelatedObjects);
#endif

	for (IfcObjectDefinition::list::it it = structures->begin(); it != structures->end(); ++it) {
		IfcObjectDefinition* ob = *it;
		if (ob->declaration().is(Type::IfcSpatialStructureElement)) {
			descend((IfcProduct*)ob, child);
		} else {
			descend(ob, child);
		}
	}

	IfcPropertySetDefinition::list::ptr property_sets = get_related
		<IfcProduct, IfcRelDefinesByProperties, IfcPropertySetDefinition>
		(product, &IfcProduct::IsDefinedBy, &IfcRelDefinesByProperties::RelatingPropertyDefinition);

	for (IfcPropertySetDefinition::list::it it = property_sets->begin(); it != property_sets->end(); ++it) {
		IfcPropertySetDefinition* pset = *it;
		if (pset->declaration().is(Type::IfcPropertySet)) {
			format_entity_instance(pset, child, true);
		}
	}
}

// Descends into the tree by recursing into IfcRelDecomposes relations.
template <>
void descend(IfcProject* project, ptree& tree) {
	ptree& child = format_entity_instance(project, tree);
	
#ifdef USE_IFC2x3
	IfcObjectDefinition::list::ptr structures = get_related
		<IfcProject, IfcRelDecomposes, IfcObjectDefinition>
		(project, &IfcProject::IsDecomposedBy, &IfcRelDecomposes::RelatedObjects);
#else
	IfcObjectDefinition::list::ptr structures = get_related
		<IfcProject, IfcRelAggregates, IfcObjectDefinition>
		(project, &IfcProduct::IsDecomposedBy, &IfcRelAggregates::RelatedObjects);
#endif
	
	for (IfcObjectDefinition::list::it it = structures->begin(); it != structures->end(); ++it) {
		IfcObjectDefinition* ob = *it;
		if (ob->declaration().is(Type::IfcSpatialStructureElement)) {
			descend((IfcProduct*)ob, child);
		} else {
			descend(ob, child);
		}
	}
}

// Format IfcProperty instances and insert into the DOM. IfcComplexProperties are flattened out.
void format_properties(IfcProperty::list::ptr properties, ptree& node) {
	for (IfcProperty::list::it it = properties->begin(); it != properties->end(); ++it) {
		IfcProperty* p = *it;
		if (p->declaration().is(Type::IfcComplexProperty)) {
			IfcComplexProperty* complex = (IfcComplexProperty*) p;
			format_properties(complex->HasProperties(), node);
		} else {
			format_entity_instance(p, node);
		}
	}
}

void XmlSerializer::finalize() {
	argument_name_map.insert(std::make_pair("GlobalId", "id"));

	IfcProject::list::ptr projects = file->entitiesByType<IfcProject>();
	if (projects->size() != 1) {
		Logger::Message(Logger::LOG_ERROR, "Expected a single IfcProject");
		return;
	}
	IfcProject* project = *projects->begin();

	ptree root, header, decomposition, properties;
	
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
	header.put("file_description.implementation_level", file->header().file_description().implementation_level());
	header.put("file_name.name",                        file->header().file_name().name());
	header.put("file_name.time_stamp",                  file->header().file_name().time_stamp());
	header.put("file_name.preprocessor_version",        file->header().file_name().preprocessor_version());
	header.put("file_name.originating_system",          file->header().file_name().originating_system());
	header.put("file_name.authorization",               file->header().file_name().authorization());
	
	// Descend into the decomposition structure of the IFC file.
	descend(project, decomposition);

	// Write all property sets and values as XML nodes.
	IfcPropertySet::list::ptr psets = file->entitiesByType<IfcPropertySet>();
	for (IfcPropertySet::list::it it = psets->begin(); it != psets->end(); ++it) {
		IfcPropertySet* pset = *it;
		ptree& node = format_entity_instance(pset, properties);
		format_properties(pset->HasProperties(), node);
	}

	root.add_child("ifc.header",        header);
	root.add_child("ifc.properties",    properties);
	root.add_child("ifc.decomposition", decomposition);

	root.put("ifc.<xmlattr>.xmlns:xlink", "http://www.w3.org/1999/xlink");

#if BOOST_VERSION >= 105600
	boost::property_tree::xml_writer_settings<ptree::key_type> settings = boost::property_tree::xml_writer_make_settings<ptree::key_type>('\t', 1);
#else
	boost::property_tree::xml_writer_settings<char> settings('\t', 1);
#endif
	boost::property_tree::write_xml(xml_filename, root, std::locale(), settings);
}