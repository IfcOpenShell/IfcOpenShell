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
std::optional<std::string> format_attribute(ifcopenshell::geometry::abstract_mapping* mapping, AttributeValue argument, IfcUtil::ArgumentType argument_type, const std::string& argument_name) {
	std::optional<std::string> value;
	
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
		case IfcUtil::Argument_BOOL:
		case IfcUtil::Argument_LOGICAL:{
			const boost::logic::tribool b = argument;
			value = b.value == boost::logic::tribool::indeterminate_value ? "unknown" : b ? "true" : "false";
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
			express::Base e = argument;
			if (e.declaration().as_entity() == nullptr) {
				auto f = e.as<express::DeclaredType>();
				value = format_attribute(mapping, f.get_attribute_value(0), f.get_attribute_value(0).type(), argument_name);
			} else if (e.declaration().is(IfcSchema::IfcSIUnit::Class()) || e.declaration().is(IfcSchema::IfcConversionBasedUnit::Class())) {
				// Some string concatenation to have a unit name as a XML attribute.

				std::string unit_name;

				if (auto unit = e.as<IfcSchema::IfcSIUnit>()) {
					unit_name = IfcSchema::IfcSIUnitName::ToString(unit.Name());
					if (unit.Prefix()) {
						unit_name = IfcSchema::IfcSIPrefix::ToString(*unit.Prefix()) + unit_name;
					}
				} else {
					auto cunit = e.as<IfcSchema::IfcConversionBasedUnit>();
                    unit_name = cunit.Name();
				}

				value = unit_name;
            } else if (auto placement = e.as<IfcSchema::IfcLocalPlacement>()) {
				auto item = mapping->map(e);
				auto matrix = ifcopenshell::geometry::taxonomy::cast< ifcopenshell::geometry::taxonomy::matrix4>(item);
				
				std::stringstream stream;
				for (int i = 0; i < 4; ++i) {
					for (int j = 0; j < 4; ++j) {
						const double trsf_value = matrix->ccomponents()(j, i);
						stream << std::setprecision (std::numeric_limits< double >::max_digits10) << trsf_value << " ";
					}
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
ptree* format_entity_instance(ifcopenshell::geometry::abstract_mapping* mapping, const express::Base& instance, ptree& child, ptree& tree, bool as_link = false) {
	const unsigned n = instance.declaration().as_entity()->attribute_count();
	for (unsigned i = 0; i < n; ++i) {
		try {
		    instance.get_attribute_value(i);
		} catch (const std::exception&) {
		    Logger::Error("Expected " + boost::lexical_cast<std::string>(n) + " attributes for:", instance);
		    break;
		}		
		auto argument = instance.get_attribute_value(i);
		if (argument.isNull()) continue;

		std::string argument_name = instance.declaration().as_entity()->attribute_by_index(i)->name();
		std::map<std::string, std::string>::const_iterator argument_name_it;
		argument_name_it = POSTFIX_SCHEMA(argument_name_map).find(argument_name);
		if (argument_name_it != POSTFIX_SCHEMA(argument_name_map).end()) {
			argument_name = argument_name_it->second;
		}
        const IfcUtil::ArgumentType argument_type = instance.get_attribute_value(i).type();

		const std::string qualified_name = instance.declaration().name() + "." + argument_name;
		std::optional<std::string> value;
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
    return &tree.add_child(instance.declaration().name(), child);
}

// Formats an entity instances as a ptree node, and insert into the DOM. Recurses
// over the entity attributes and writes them as xml attributes of the node.
ptree* format_entity_instance(ifcopenshell::geometry::abstract_mapping* mapping, const express::Base& instance, ptree& tree, bool as_link = false) {
    ptree child;
    return format_entity_instance(mapping, instance, child, tree, as_link);
}

std::string qualify_unrooted_instance(const express::Base& inst) {
    return inst.declaration().name() + "_" + std::to_string(inst.id());
}

// A function to be called recursively. Template specialization is used 
// to descend into decomposition, containment and property relationships.
template <typename A>
ptree* descend(ifcopenshell::geometry::abstract_mapping* mapping, A instance, ptree& tree, express::Base parent = express::Base()) {
	if (instance.declaration().is(IfcSchema::IfcObjectDefinition::Class())) {
		return descend(mapping, instance.template as<IfcSchema::IfcObjectDefinition>(), tree, parent);
	} else {
		return format_entity_instance(mapping, instance, tree);
	}
}

// Returns related entity instances using IFC's objectified relationship
// model. The second and third argument require a member function pointer.
template <typename T, typename U, typename V, typename F, typename G>
auto get_related(T t, F f, G g) {
	auto li = (t.*f)();
    std::vector<V> acc;
    for (auto& u : li) {
		try {
            auto vs = (u.as<U>().*g)();
            if constexpr (std::is_base_of_v<express::Base, decltype(vs)>) {
                if (auto vv = vs.as<V>()) {
					acc.push_back(vv);
                }
            } else if constexpr (std::is_base_of_v<express::Select, decltype(vs)>) {
                if (auto vv = vs.concrete().as<V>()) {
                    acc.push_back(vv);
                }                
            } else {
                for (auto& v : vs) {
                    if (auto vv = v.as<V>()) {
						acc.push_back(vv);
                    }
                }
            }            
		} catch (IfcParse::IfcException& e) {
			Logger::Error(e);
		}
	}
	return acc;
}

// Descends into the tree by recursing into IfcRelContainedInSpatialStructure,
// IfcRelDecomposes, IfcRelDefinesByType, IfcRelDefinesByProperties relations.
template <>
ptree* descend(ifcopenshell::geometry::abstract_mapping* mapping, const IfcSchema::IfcObjectDefinition& product, ptree& tree, express::Base parent) {
	if (product.declaration().is(IfcSchema::IfcElement::Class())) {
		auto voids = product.as<IfcSchema::IfcElement>().FillsVoids();
		if (voids.size() == 1 && voids.front().RelatingOpeningElement() != parent) {
			// Fills are placed under their corresponding opening, return early to avoid duplication.
			return nullptr;
		}
	}

	ptree& child = *format_entity_instance(mapping, product, tree);

	if (auto opening = product.as<IfcSchema::IfcOpeningElement>()) {
		auto fills = get_related<IfcSchema::IfcOpeningElement, IfcSchema::IfcRelFillsElement, IfcSchema::IfcElement>(
			opening, &IfcSchema::IfcOpeningElement::HasFillings, &IfcSchema::IfcRelFillsElement::RelatedBuildingElement);

		for (auto& f : fills) {
			descend(mapping, f, child, product);
		}
	}
	
	if (auto structure = product.as<IfcSchema::IfcSpatialStructureElement>()) {
		auto elements = get_related
			<IfcSchema::IfcSpatialStructureElement, IfcSchema::IfcRelContainedInSpatialStructure, IfcSchema::IfcObjectDefinition>
			(structure, &IfcSchema::IfcSpatialStructureElement::ContainsElements, &IfcSchema::IfcRelContainedInSpatialStructure::RelatedElements);
	
		for (auto& el : elements) {
			descend(mapping, el, child, product);
		}
	}

    if (auto element = product.as<IfcSchema::IfcElement>()) {
		auto openings = get_related<IfcSchema::IfcElement, IfcSchema::IfcRelVoidsElement, IfcSchema::IfcOpeningElement>(
            element, &IfcSchema::IfcElement::HasOpenings, &IfcSchema::IfcRelVoidsElement::RelatedOpeningElement);

        for (auto& op : openings) {
            descend(mapping, op, child, product);
        }
    }

#ifdef SCHEMA_IfcRelDecomposes_HAS_RelatedObjects
	auto structures = get_related
		<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelDecomposes, IfcSchema::IfcObjectDefinition>
		(product, &IfcSchema::IfcObjectDefinition::IsDecomposedBy, &IfcSchema::IfcRelDecomposes::RelatedObjects);
#else
	auto structures = get_related
		<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelAggregates, IfcSchema::IfcObjectDefinition>
		(product, &IfcSchema::IfcObjectDefinition::IsDecomposedBy, &IfcSchema::IfcRelAggregates::RelatedObjects);

	auto nested = get_related
		<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelNests, IfcSchema::IfcObjectDefinition>
		(product, &IfcSchema::IfcObjectDefinition::IsNestedBy, &IfcSchema::IfcRelNests::RelatedObjects);

    structures.insert(structures.end(), nested.begin(), nested.end());
#endif

	for (auto& ob : structures) {
		descend(mapping, ob, child, product);
	}

	if (auto object = product.as<IfcSchema::IfcObject>()) {
		auto property_sets = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByProperties, IfcSchema::IfcPropertySetDefinition>
			(object, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByProperties::RelatingPropertyDefinition);

#ifdef SCHEMAS_HAS_IfcPropertySetDefinitionSet
		auto property_set_sets = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByProperties, IfcSchema::IfcPropertySetDefinitionSet>
			(object, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByProperties::RelatingPropertyDefinition);

		for (auto& s : property_set_sets) {
            auto set_sets_value = (decltype(property_sets))s;
            property_sets.insert(property_sets.end(), set_sets_value.begin(), set_sets_value.end());
		}
#endif

		for (auto& pset : property_sets) {
			if (pset.declaration().is(IfcSchema::IfcPropertySet::Class())) {
				format_entity_instance(mapping, pset, child, true);
			} else if (pset.declaration().is(IfcSchema::IfcElementQuantity::Class())) {
				format_entity_instance(mapping, pset, child, true);
			}
		}

#ifdef SCHEMA_IfcObject_HAS_IsTypedBy
		auto types = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByType, IfcSchema::IfcTypeObject>
			(object, &IfcSchema::IfcObject::IsTypedBy, &IfcSchema::IfcRelDefinesByType::RelatingType);
#else
        auto types = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByType, IfcSchema::IfcTypeObject>
			(object, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByType::RelatingType);
#endif

		for (auto& type : types) {
			format_entity_instance(mapping, type, child, true);
		}
	}

    if (product.declaration().is(IfcSchema::IfcProduct::Class())) {
        auto layers = mapping->get_layers(product);
        for (auto& p : layers) {
            // IfcPresentationLayerAssignments don't have GUIDs (only optional Identifier) so use name as the ID.
            // Note that the IfcPresentationLayerAssignment passed here doesn't really matter as as_link is true
            // for the format_entity_instance() call.
            ptree node;
            node.put("<xmlattr>.xlink:href", "#" + p.first);
            format_entity_instance(mapping, p.second, node, child, true);
        }
		
		auto associations = product.HasAssociations();
		for (auto& rel : associations) {
            if (auto relmat = rel.as<IfcSchema::IfcRelAssociatesMaterial>()) {
                IfcSchema::IfcMaterialSelect mat = relmat.RelatingMaterial();
				ptree node;
				node.put("<xmlattr>.xlink:href", "#" + qualify_unrooted_instance(mat));
                format_entity_instance(mapping, mat.concrete(), node, child, true);
			}
		}
    }

#if defined(SCHEMA_HAS_IfcAlignmentSegment) && defined(SCHEMA_IfcAlignmentSegment_HAS_DesignParameters)
	if (auto als = product.as<IfcSchema::IfcAlignmentSegment>()) {
		ptree node;
		format_entity_instance(mapping, als.DesignParameters(), node, child, false);
	}
#endif

	return &child;
}

// Format IfcProperty instances and insert into the DOM. IfcComplexProperties are flattened out.
void format_properties(ifcopenshell::geometry::abstract_mapping* mapping, const std::vector<IfcSchema::IfcProperty>& properties, ptree& node) {
    for (auto& p : properties) {
        if (auto complex = p.as<IfcSchema::IfcComplexProperty>()) {
			format_properties(mapping, complex.HasProperties(), node);
		} else {
			format_entity_instance(mapping, p, node);
		}
	}
}

void writeGroupToNode(ifcopenshell::geometry::abstract_mapping* mapping, IfcSchema::IfcGroup group, ptree& node, std::set<std::string> notRootGroups) {
	// @todo tfk: instead of a set<string> shouldn't we just have a set<IfcGroup>, the current approach
	// might not work with non-unique or NIL group names.

	// @todo tfk: should the set be a passed as a reference?
	if (!group.Name()) {
		return;
	}

    if (notRootGroups.find(*group.Name()) != notRootGroups.end()) {
        return;
    }
    // Write one group to root
    ptree* node2 = descend(mapping, group, node);
    auto father = group.IsGroupedBy();
    for (auto& ii : father)
    {
        auto objs = ii.RelatedObjects();
        for (auto entity : objs) {
            if (entity.as<IfcSchema::IfcGroup>() && entity.Name()) {
                writeGroupToNode(mapping, entity.as<IfcSchema::IfcGroup>(), *node2, notRootGroups);
                notRootGroups.emplace(*entity.Name());
            }
            else {
                // Write child to father group
                descend(mapping, entity, *node2);
            }
        }
    }
}

// Format IfcElementQuantity instances and insert into the DOM.
void format_quantities(ifcopenshell::geometry::abstract_mapping* mapping, const std::vector<IfcSchema::IfcPhysicalQuantity>& quantities, ptree& node) {
	for (auto& p : quantities) {
		ptree* node2 = format_entity_instance(mapping, p, node);
		if (node2 && p.declaration().is(IfcSchema::IfcPhysicalComplexQuantity::Class())) {
            format_quantities(mapping, p.as<IfcSchema::IfcPhysicalComplexQuantity>().HasQuantities(), *node2);
		}
	}
}

// Format IfcTask instances and insert into the DOM.
void format_tasks(ifcopenshell::geometry::abstract_mapping* mapping, IfcSchema::IfcTask task, ptree& node) {
	ptree* ntask = format_entity_instance(mapping, task, node);

	if (ntask) {
#ifdef SCHEMA_IfcTask_HAS_TaskTime
		IfcSchema::IfcTaskTime task_time = task.TaskTime();
		if (task_time)
		{
			format_entity_instance(mapping, task_time, *ntask);
		}
#endif

#ifdef SCHEMA_IfcProcess_HAS_IsSuccessorFrom
		auto successor_from = task.IsSuccessorFrom();
		for (auto& rel : successor_from)
		{
			IfcSchema::IfcProcess relating_process = rel.RelatingProcess();
			ptree nobject;
			nobject.put("<xmlattr>.id", relating_process.GlobalId());
			ntask->add_child("IsSuccessorFrom", nobject);
		}
#endif

#ifdef SCHEMA_IfcProcess_HAS_IsPredecessorTo
		auto predecessor_to = task.IsPredecessorTo();
        for (auto& rel : predecessor_to)
		{
            IfcSchema::IfcProcess relating_process = rel.RelatedProcess();
			ptree nobject;
			nobject.put("<xmlattr>.id", relating_process.GlobalId());
			ntask->add_child("IsPredecessorTo", nobject);
		}
#endif

		auto property_sets = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByProperties, IfcSchema::IfcPropertySetDefinition>
			(task, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByProperties::RelatingPropertyDefinition);

		for (auto& pset : property_sets) {
			if (pset.declaration().is(IfcSchema::IfcPropertySet::Class())) {
				format_entity_instance(mapping, pset, *ntask, true);
			}
			else if (pset.declaration().is(IfcSchema::IfcElementQuantity::Class())) {
				format_entity_instance(mapping, pset, *ntask, true);
			}
		}

#ifdef SCHEMA_IfcProcess_HAS_OperatesOn
		auto operates = task.OperatesOn();
        for (auto& operation : operates)
		{
			auto objects = operation.RelatedObjects();
            for (auto& object : objects)
			{
				ptree nobject;
				nobject.put("<xmlattr>.id", object.GlobalId());
				if (object.declaration().is(IfcSchema::IfcProduct::Class()))
				{
					ntask->add_child("Input", nobject);
				}
				else if (object.declaration().is(IfcSchema::IfcResource::Class()))
				{
					ntask->add_child("Resource", nobject);
				}
				else if (object.declaration().is(IfcSchema::IfcControl::Class()))
				{
					ntask->add_child("Control", nobject);
				}
				else
				{
					nobject.put("<xmlattr>.Type", object.declaration().name());
					ntask->add_child("OperatesOn", nobject);
				}
			}
		}
#endif

		auto assignments = task.HasAssignments();
        for (auto& assignment : assignments)
		{
            if (auto assign_to_product = assignment.as<IfcSchema::IfcRelAssignsToProduct>()) {
                IfcSchema::IfcRoot product = assign_to_product.RelatingProduct().as<IfcSchema::IfcProduct>();
                if (!product) {
                    product = assign_to_product.RelatingProduct().as<IfcSchema::IfcTypeProduct>();
                }
				ptree nobject;
				nobject.put("<xmlattr>.id", product.GlobalId());
				ntask->add_child("Output", nobject);
			}
		}

#ifdef SCHEMA_IfcObjectDefinition_HAS_IsNestedBy
		auto nested_by = task.IsNestedBy();
        for (auto& rel : nested_by)
		{
			auto related_objects = rel.RelatedObjects();
			for (auto& object : related_objects)
			{
                if (auto task2 = object.as<IfcSchema::IfcTask>()) {
                    format_tasks(mapping, task2, *ntask);
                }
			}
		}
#endif
	}
}

} // ~unnamed namespace

void POSTFIX_SCHEMA(XmlSerializer)::finalize() {
	POSTFIX_SCHEMA(argument_name_map).insert(std::make_pair("GlobalId", "id"));

	auto projects = file->instances_by_type<IfcSchema::IfcProject>();
	if (projects.size() != 1) {
		Logger::Message(Logger::LOG_ERROR, "Expected a single IfcProject");
		return;
	}
    IfcSchema::IfcProject& project = projects.front();

	ptree root, header, units, decomposition, properties, quantities, types, layers, materials, work, calendars, connections, groups;

	auto catch_exceptions = [this](const auto& fn) {
		try {
			return fn();
		} catch(const std::exception& e) {
			Logger::Error(e);
			static std::invoke_result_t<decltype(fn)> v;
			return v;
		}
	};

	// Write the SPF header as XML nodes.
	BOOST_FOREACH(const std::string & s, catch_exceptions([this]() { return file->header().file_description().description(); })) {
		header.add_child("file_description.description", ptree(s));
	}
	BOOST_FOREACH(const std::string& s, catch_exceptions([this]() { return file->header().file_name().author(); })) {
		header.add_child("file_name.author", ptree(s));
	}
	BOOST_FOREACH(const std::string& s, catch_exceptions([this]() { return file->header().file_name().organization(); })) {
		header.add_child("file_name.organization", ptree(s));
	}
	BOOST_FOREACH(const std::string& s, catch_exceptions([this]() { return file->header().file_schema().schema_identifiers(); })) {
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
		// @nb inconsistent spelling
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
	auto psets = file->instances_by_type<IfcSchema::IfcPropertySet>();
	for (auto& pset : psets) {
		ptree* node = format_entity_instance(mapping_, pset, properties);
		if (node) {
			format_properties(mapping_, pset.HasProperties(), *node);
		}
	}

	// Write all group sets and values as XML nodes.
	auto gsets = file->instances_by_type<IfcSchema::IfcGroup>();
	std::set<std::string> notRootGroups; //selfname, fathername
	for (auto& g : gsets) {
		writeGroupToNode(mapping_, g, groups, notRootGroups);
	}
	for (auto it = groups.begin(); it != groups.end();) {
		if (notRootGroups.find(it->second.get<std::string>("<xmlattr>.Name")) != notRootGroups.end()) {
			it = groups.erase(it);
		} else {
			it++;
		}
	}

	// Write all quantities and values as XML nodes.
	auto qtosets = file->instances_by_type<IfcSchema::IfcElementQuantity>();
	for (auto& qto : qtosets) {
		ptree* node = format_entity_instance(mapping_, qto, quantities);
		if (node) {
			format_quantities(mapping_, qto.Quantities(), *node);
		}
	}

	// Write all work schedules and values as XML nodes.
	ptree pwork_schedules;
	auto pschedules = file->instances_by_type<IfcSchema::IfcWorkSchedule>();
    for (auto& schedule : pschedules) {
		ptree* nschedule = format_entity_instance(mapping_, schedule, pwork_schedules);
		
		if(nschedule) {
			auto controls = schedule.Controls();
			for(auto& control : controls) {
				auto objects = control.RelatedObjects();
				for(auto& object : objects) {
					if (object && object.declaration().is(IfcSchema::IfcTask::Class())) {
						IfcSchema::IfcTask task = object.as<IfcSchema::IfcTask>();
						format_tasks(mapping_, task, *nschedule);
					}
				}
			}
		}
	}
	work.add_child("schedules", pwork_schedules);

	// Write all work plans and values as XML nodes.
	ptree pwork_plans;
	auto pplans = file->instances_by_type<IfcSchema::IfcWorkPlan>();
	for (auto& plan : pplans) {
		ptree* nschedule = format_entity_instance(mapping_, plan, pwork_plans);

		if (nschedule) {
#ifdef SCHEMA_IfcObjectDefinition_HAS_IsDecomposedBy
			auto decomposed_by = plan.IsDecomposedBy();
			for (auto& rel : decomposed_by)
			{
				auto related_objects = rel.RelatedObjects();
                for (auto& work_schedule : related_objects)
				{
					ptree pwork_schedule;
					pwork_schedule.put("<xmlattr>.id", work_schedule.GlobalId());
					nschedule->add_child("IfcWorkSchedule", pwork_schedule);
				}
			}
#endif
		}
	}
	work.add_child("plans", pwork_plans);
	
	// Write all work calendars and values as XML nodes.
#ifdef SCHEMA_HAS_IfcWorkCalendar
	auto pcalendars = file->instances_by_type<IfcSchema::IfcWorkCalendar>();
    for (auto& calendar : pcalendars) {
		ptree* ncalendar = format_entity_instance(mapping_, calendar, calendars);
		
		if (ncalendar) {
            auto working_times = calendar.WorkingTimes().value_or(std::vector<IfcSchema::IfcWorkTime>{});
            for (auto& working_time : working_times)
			{
				format_entity_instance(mapping_, working_time, *ncalendar);
			}
		}
	}
#endif
	
	auto pconnections = file->instances_by_type<IfcSchema::IfcRelConnectsElements>();
    for (auto& connection : pconnections) {
		ptree* nconnection = format_entity_instance(mapping_, connection, connections);

		ptree nrelatedElement;
		ptree nrelatingElement;

		format_entity_instance(mapping_,connection.RelatedElement(), nrelatedElement, true);
		format_entity_instance(mapping_,connection.RelatingElement(), nrelatingElement, true);
		
		nconnection->add_child("RelatedElement",  nrelatedElement);
		nconnection->add_child("RelatingElement", nrelatingElement);
	}

	// Write all type objects as XML nodes.
	auto type_objects = file->instances_by_type<IfcSchema::IfcTypeObject>();
    for (auto& type_object : type_objects) {
		ptree* node = descend(mapping_, type_object, types);
		
		if (node && type_object.HasPropertySets()) {
			auto property_sets = *type_object.HasPropertySets();
			for (auto& pset : property_sets) {
				if (pset.declaration().is(IfcSchema::IfcPropertySet::Class())) {
					format_entity_instance(mapping_, pset, *node, true);
				}
			}
		}
	}

	// Write all assigned units as XML nodes.
	auto unit_assignments = project.UnitsInContext().Units();
	for (auto& unit : unit_assignments) {
        if (auto named_unit = unit.as<IfcSchema::IfcNamedUnit>()) {
			ptree* node = format_entity_instance(mapping_, named_unit, units);
			if (node) {
				node->put("<xmlattr>.SI_equivalent", IfcParse::get_SI_equivalent<IfcSchema>(named_unit));
			}
        } else if (auto mon_unit = unit.as<IfcSchema::IfcMonetaryUnit>()) {
            format_entity_instance(mapping_, mon_unit, units);
		}
	}

    // Layer assignments. IfcPresentationLayerAssignments don't have GUIDs (only optional Identifier)
    // so use names as the IDs and only insert those with unique names. In case of possible duplicate names/IDs
    // the first IfcPresentationLayerAssignment occurrence takes precedence.
    std::set<std::string> layer_names;
	auto layer_assignments = file->instances_by_type<IfcSchema::IfcPresentationLayerAssignment>();
    for (auto& assignment : layer_assignments) {
        const std::string& name = assignment.Name();
        if (layer_names.find(name) == layer_names.end()) {
            layer_names.insert(name);
            ptree node;
            node.put("<xmlattr>.id", name);
            format_entity_instance(mapping_, assignment, node, layers);
        }
    }

	auto materal_associations = file->instances_by_type<IfcSchema::IfcRelAssociatesMaterial>();
	std::set<express::Base> emitted_materials;
	for (auto& rel : materal_associations) {
        IfcSchema::IfcMaterialSelect mat = rel.RelatingMaterial();
		if (emitted_materials.find(mat) == emitted_materials.end()) {
			emitted_materials.insert(mat);
			ptree node;
			node.put("<xmlattr>.id", qualify_unrooted_instance(mat));
            // @todo this does not handle IfcMaterialProfileSetUsage and IfcMaterialConstituentSet
            if (mat.concrete().as<IfcSchema::IfcMaterialLayerSetUsage>() || mat.concrete().as<IfcSchema::IfcMaterialLayerSet>()) {				
				IfcSchema::IfcMaterialLayerSet layerset = mat.concrete().as<IfcSchema::IfcMaterialLayerSet>();
				if (!layerset) {
					layerset = mat.concrete().as<IfcSchema::IfcMaterialLayerSetUsage>().ForLayerSet();
				}				
				if (layerset.LayerSetName()) {
					node.put("<xmlattr>.LayerSetName", *layerset.LayerSetName());
				}
				auto ls = layerset.MaterialLayers();
				for (auto& layer : ls) {
					ptree subnode;
					if (layer.Material()) {
                        subnode.put("<xmlattr>.Name", layer.Material());
					}
                    format_entity_instance(mapping_, layer, subnode, node);
				}
			} else if (auto matlist = mat.concrete().as<IfcSchema::IfcMaterialList>()) {
                auto mats = matlist.Materials();
				for (auto& mat : mats) {
					ptree subnode;
                    format_entity_instance(mapping_, mat, subnode, node);
				}
			}
            format_entity_instance(mapping_, mat.concrete(), node, materials);
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
