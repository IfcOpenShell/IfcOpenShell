#include <map>

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>
#include <boost/foreach.hpp>
#include <boost/version.hpp>

#include "XmlSerializer.h"

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
			if (Type::IsSimple(e->type())) {
				IfcUtil::IfcBaseType* f = (IfcUtil::IfcBaseType*) e;
				value = format_attribute(f->getArgument(0), f->getArgumentType(0));
			} else if (e->is(IfcSchema::Type::IfcSIUnit) || e->is(IfcSchema::Type::IfcConversionBasedUnit)) {
				// Some string concatenation to have a unit name as a XML attribute.

				std::string unit_name;

				if (e->is(IfcSchema::Type::IfcSIUnit)) {
					IfcSchema::IfcSIUnit* unit = (IfcSchema::IfcSIUnit*) e;
					unit_name = IfcSchema::IfcSIUnitName::ToString(unit->Name());
					if (unit->hasPrefix()) {
						unit_name = IfcSchema::IfcSIPrefix::ToString(unit->Prefix()) + unit_name;
					}
				} else {
					IfcSchema::IfcConversionBasedUnit* unit = (IfcSchema::IfcConversionBasedUnit*) e;
					unit_name = unit->Name();
				}

				for (std::string::iterator c = unit_name.begin(); c != unit_name.end(); ++c) *c = tolower(*c);

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
	const unsigned n = instance->getArgumentCount();
	for (unsigned i = 0; i < n; ++i) {
		const Argument* argument = instance->getArgument(i);
		if (argument->isNull()) continue;

		std::string argument_name = instance->getArgumentName(i);
		std::map<std::string, std::string>::const_iterator argument_name_it;
		argument_name_it = argument_name_map.find(argument_name);
		if (argument_name_it != argument_name_map.end()) {
			argument_name = argument_name_it->second;
		}
		const IfcUtil::ArgumentType argument_type = instance->getArgumentType(i);

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
	return tree.add_child(Type::ToString(instance->type()), child);
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
		acc->push((*u.*g)());
	}
	return acc;
}

// Descends into the tree by recursing into IfcRelContainedInSpatialStructure,
// IfcRelDecomposes and IfcRelDefinesByProperties relations.
template <>
void descend(IfcProduct* product, ptree& tree) {
	ptree& child = format_entity_instance(product, tree);
	
	if (product->is(Type::IfcSpatialStructureElement)) {
		IfcSpatialStructureElement* structure = (IfcSpatialStructureElement*) product;

		IfcProduct::list::ptr elements = get_related
			<IfcSpatialStructureElement, IfcRelContainedInSpatialStructure, IfcProduct>
			(structure, &IfcSpatialStructureElement::ContainsElements, &IfcRelContainedInSpatialStructure::RelatedElements);
	
		for (IfcProduct::list::it it = elements->begin(); it != elements->end(); ++it) {
			descend(*it, child);
		}
	}

	IfcObjectDefinition::list::ptr structures = get_related
		<IfcProduct, IfcRelDecomposes, IfcObjectDefinition>
		(product, &IfcProduct::IsDecomposedBy, &IfcRelDecomposes::RelatedObjects);

	for (IfcObjectDefinition::list::it it = structures->begin(); it != structures->end(); ++it) {
		IfcObjectDefinition* ob = *it;
		if (ob->is(Type::IfcSpatialStructureElement)) {
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
		if (pset->is(Type::IfcPropertySet)) {
			format_entity_instance(pset, child, true);
		}
	}
}

// Descends into the tree by recursing into IfcRelDecomposes relations.
template <>
void descend(IfcProject* project, ptree& tree) {
	ptree& child = format_entity_instance(project, tree);
	
	IfcObjectDefinition::list::ptr structures = get_related
		<IfcProject, IfcRelDecomposes, IfcObjectDefinition>
		(project, &IfcProject::IsDecomposedBy, &IfcRelDecomposes::RelatedObjects);
	
	for (IfcObjectDefinition::list::it it = structures->begin(); it != structures->end(); ++it) {
		IfcObjectDefinition* ob = *it;
		if (ob->is(Type::IfcSpatialStructureElement)) {
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
		if (p->is(Type::IfcComplexProperty)) {
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