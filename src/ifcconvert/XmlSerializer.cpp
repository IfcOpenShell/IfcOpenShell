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
#include <boost/version.hpp>

#include "XmlSerializer.h"

#include <algorithm>

#include "../ifcparse/IfcSIPrefix.h"
#include "../ifcgeom/IfcGeom.h"

using boost::property_tree::ptree;
using namespace IfcSchema;

namespace {

std::map<std::string, std::string> argument_name_map;

// Format an IFC attribute and maybe returns as string. Only literal scalar 
// values are converted. Things like entity instances and lists are omitted.
boost::optional<std::string> format_attribute(const Argument* argument, IfcUtil::ArgumentType argument_type, const std::string& argument_name) {
	boost::optional<std::string> value;
	
	// Hard-code lat-lon as it represents an array
	// of integers best emitted as a single decimal
	if (argument_name == "IfcSite.RefLatitude" ||
		argument_name == "IfcSite.RefLongitude")
	{
		std::vector<int> angle = *argument;
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
				value = format_attribute(f->getArgument(0), f->getArgumentType(0), argument_name);
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

				value = unit_name;
			} else if (e->is(IfcSchema::Type::IfcLocalPlacement)) {
				IfcSchema::IfcLocalPlacement* placement = e->as<IfcSchema::IfcLocalPlacement>();
				gp_Trsf trsf;
				IfcGeom::Kernel kernel;
				
				if (kernel.convert(placement, trsf)) {
					std::stringstream stream;
					for (int i = 1; i < 5; ++i) {
						for (int j = 1; j < 4; ++j) {
							const double trsf_value = trsf.Value(j, i);
							stream << trsf_value << " ";
						}
						stream << ((i == 4) ? "1" : "0 ");
					}
					value = stream.str();
				}				
			}
			break; }
        default:
            break;
	}
	return value;
}

// Appends to a node with possibly existing attributes
ptree& format_entity_instance(IfcUtil::IfcBaseEntity* instance, ptree& child, ptree& tree, bool as_link = false) {
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

		const std::string qualified_name = IfcSchema::Type::ToString(instance->type()) + "." + argument_name;
		boost::optional<std::string> value;
		try {
			value = format_attribute(argument, argument_type, qualified_name);
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
	return tree.add_child(Type::ToString(instance->type()), child);
}

// Formats an entity instances as a ptree node, and insert into the DOM. Recurses
// over the entity attributes and writes them as xml attributes of the node.
ptree& format_entity_instance(IfcUtil::IfcBaseEntity* instance, ptree& tree, bool as_link = false) {
    ptree child;
    return format_entity_instance(instance, child, tree, as_link);
}

std::string qualify_unrooted_instance(IfcUtil::IfcBaseClass* inst) {
	return IfcSchema::Type::ToString(inst->type()) + "_" + boost::lexical_cast<std::string>(inst->entity->id());
}

// A function to be called recursively. Template specialization is used 
// to descend into decomposition, containment and property relationships.
template <typename A>
ptree& descend(A* instance, ptree& tree) {
	if (instance->is(IfcSchema::Type::IfcObjectDefinition)) {
		return descend(instance->template as<IfcSchema::IfcObjectDefinition>(), tree);
	} else {
		return format_entity_instance(instance, tree);
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
		acc->push((*u.*g)()->template as<V>());
	}
	return acc;
}

// Descends into the tree by recursing into IfcRelContainedInSpatialStructure,
// IfcRelDecomposes, IfcRelDefinesByType, IfcRelDefinesByProperties relations.
template <>
ptree& descend(IfcObjectDefinition* product, ptree& tree) {
	ptree& child = format_entity_instance(product, tree);
	
	if (product->is(Type::IfcSpatialStructureElement)) {
		IfcSpatialStructureElement* structure = (IfcSpatialStructureElement*) product;

		IfcObjectDefinition::list::ptr elements = get_related
			<IfcSpatialStructureElement, IfcRelContainedInSpatialStructure, IfcObjectDefinition>
			(structure, &IfcSpatialStructureElement::ContainsElements, &IfcRelContainedInSpatialStructure::RelatedElements);
	
		for (IfcObjectDefinition::list::it it = elements->begin(); it != elements->end(); ++it) {
			descend(*it, child);
		}
	}

    if (product->is(Type::IfcElement)) {
        IfcElement* element = static_cast<IfcElement*>(product);
        IfcOpeningElement::list::ptr openings = get_related<IfcElement, IfcRelVoidsElement, IfcOpeningElement>(
            element, &IfcElement::HasOpenings, &IfcRelVoidsElement::RelatedOpeningElement);

        for (IfcOpeningElement::list::it it = openings->begin(); it != openings->end(); ++it) {
            descend(*it, child);
        }
    }

#ifndef USE_IFC4
	IfcObjectDefinition::list::ptr structures = get_related
		<IfcObjectDefinition, IfcRelDecomposes, IfcObjectDefinition>
		(product, &IfcObjectDefinition::IsDecomposedBy, &IfcRelDecomposes::RelatedObjects);
#else
	IfcObjectDefinition::list::ptr structures = get_related
		<IfcObjectDefinition, IfcRelAggregates, IfcObjectDefinition>
		(product, &IfcProduct::IsDecomposedBy, &IfcRelAggregates::RelatedObjects);
#endif

	for (IfcObjectDefinition::list::it it = structures->begin(); it != structures->end(); ++it) {
		IfcObjectDefinition* ob = *it;
		descend(ob, child);
	}

	if (product->is(IfcSchema::Type::IfcObject)) {
		IfcSchema::IfcObject* object = product->as<IfcSchema::IfcObject>();

		IfcPropertySetDefinition::list::ptr property_sets = get_related
			<IfcObject, IfcRelDefinesByProperties, IfcPropertySetDefinition>
			(object, &IfcObject::IsDefinedBy, &IfcRelDefinesByProperties::RelatingPropertyDefinition);

		for (IfcPropertySetDefinition::list::it it = property_sets->begin(); it != property_sets->end(); ++it) {
			IfcPropertySetDefinition* pset = *it;
			if (pset->is(Type::IfcPropertySet)) {
				format_entity_instance(pset, child, true);
			}
		}

#ifdef USE_IFC4
		IfcTypeObject::list::ptr types = get_related
			<IfcObject, IfcRelDefinesByType, IfcTypeObject>
			(object, &IfcObject::IsTypedBy, &IfcRelDefinesByType::RelatingType);
#else
		IfcTypeObject::list::ptr types = get_related
			<IfcObject, IfcRelDefinesByType, IfcTypeObject>
			(object, &IfcObject::IsDefinedBy, &IfcRelDefinesByType::RelatingType);
#endif

		for (IfcTypeObject::list::it it = types->begin(); it != types->end(); ++it) {
			IfcTypeObject* type = *it;
			format_entity_instance(type, child, true);
		}
	}

    if (product->is(Type::IfcProduct)) {
        std::map<std::string, IfcPresentationLayerAssignment*> layers = IfcGeom::Kernel::get_layers(product->as<IfcProduct>());
        for (std::map<std::string, IfcPresentationLayerAssignment*>::const_iterator it = layers.begin(); it != layers.end(); ++it) {
            // IfcPresentationLayerAssignments don't have GUIDs (only optional Identifier) so use name as the ID.
            // Note that the IfcPresentationLayerAssignment passed here doesn't really matter as as_link is true
            // for the format_entity_instance() call.
            ptree node;
            node.put("<xmlattr>.xlink:href", "#" + it->first);
            format_entity_instance(it->second, node, child, true);
        }
		
		IfcRelAssociates::list::ptr associations = product->HasAssociations();
		for (IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
			if ((*it)->as<IfcRelAssociatesMaterial>()) {
				IfcMaterialSelect* mat = (*it)->as<IfcRelAssociatesMaterial>()->RelatingMaterial();
				ptree node;
				node.put("<xmlattr>.xlink:href", "#" + qualify_unrooted_instance(mat));
				format_entity_instance((IfcUtil::IfcBaseEntity*) mat, node, child, true);
			}
		}
    }

	return child;
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

} // ~unnamed namespace

void XmlSerializer::finalize() {
	argument_name_map.insert(std::make_pair("GlobalId", "id"));

	IfcProject::list::ptr projects = file->entitiesByType<IfcProject>();
	if (projects->size() != 1) {
		Logger::Message(Logger::LOG_ERROR, "Expected a single IfcProject");
		return;
	}
	IfcProject* project = *projects->begin();

	ptree root, header, units, decomposition, properties, types, layers, materials;
	
	// Write the SPF header as XML nodes.
	foreach(const std::string& s, file->header().file_description().description()) {
		header.add_child("file_description.description", ptree(s));
	}
	foreach(const std::string& s, file->header().file_name().author()) {
		header.add_child("file_name.author", ptree(s));
	}
	foreach(const std::string& s, file->header().file_name().organization()) {
		header.add_child("file_name.organization", ptree(s));
	}
	foreach(const std::string& s, file->header().file_schema().schema_identifiers()) {
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

	// Write all type objects as XML nodes.
	IfcTypeObject::list::ptr type_objects = file->entitiesByType<IfcTypeObject>();
	for (IfcTypeObject::list::it it = type_objects->begin(); it != type_objects->end(); ++it) {
		IfcTypeObject* type_object = *it;
		ptree& node = descend(type_object, types);
		// ptree& node = format_entity_instance(type_object, types);	
		
		if (type_object->hasHasPropertySets()) {
			IfcPropertySetDefinition::list::ptr property_sets = type_object->HasPropertySets();
			for (IfcPropertySetDefinition::list::it jt = property_sets->begin(); jt != property_sets->end(); ++jt) {
				IfcPropertySetDefinition* pset = *jt;
				if (pset->is(Type::IfcPropertySet)) {
					format_entity_instance(pset, node, true);
				}
			}
		}
	}

	// Write all assigned units as XML nodes.
	IfcEntityList::ptr unit_assignments = project->UnitsInContext()->Units();
	for (IfcEntityList::it it = unit_assignments->begin(); it != unit_assignments->end(); ++it) {
		if ((*it)->is(IfcSchema::Type::IfcNamedUnit)) {
			IfcSchema::IfcNamedUnit* named_unit = (*it)->as<IfcSchema::IfcNamedUnit>();
			ptree& node = format_entity_instance(named_unit, units);
			node.put("<xmlattr>.SI_equivalent", IfcParse::get_SI_equivalent(named_unit));
		} else if ((*it)->is(IfcSchema::Type::IfcMonetaryUnit)) {
			format_entity_instance((*it)->as<IfcSchema::IfcMonetaryUnit>(), units);
		}
	}

    // Layer assignments. IfcPresentationLayerAssignments don't have GUIDs (only optional Identifier)
    // so use names as the IDs and only insert those with unique names. In case of possible duplicate names/IDs
    // the first IfcPresentationLayerAssignment occurence takes precedence.
    std::set<std::string> layer_names;
    IfcPresentationLayerAssignment::list::ptr layer_assignments = file->entitiesByType<IfcPresentationLayerAssignment>();
    for (IfcPresentationLayerAssignment::list::it it = layer_assignments->begin(); it != layer_assignments->end(); ++it) {
        const std::string& name = (*it)->Name();
        if (layer_names.find(name) == layer_names.end()) {
            layer_names.insert(name);
            ptree node;
            node.put("<xmlattr>.id", name);
            format_entity_instance(*it, node, layers);
        }
    }

	IfcRelAssociatesMaterial::list::ptr materal_associations = file->entitiesByType<IfcRelAssociatesMaterial>();
	std::set<IfcMaterialSelect*> emitted_materials;
	for (IfcRelAssociatesMaterial::list::it it = materal_associations->begin(); it != materal_associations->end(); ++it) {
		IfcMaterialSelect* mat = (**it).RelatingMaterial();
		if (emitted_materials.find(mat) == emitted_materials.end()) {
			emitted_materials.insert(mat);
			ptree node;
			node.put("<xmlattr>.id", qualify_unrooted_instance(mat));
			if (mat->as<IfcMaterialLayerSetUsage>()) {
				IfcMaterialLayerSet* layerset = mat->as<IfcMaterialLayerSetUsage>()->ForLayerSet();
				if (layerset->hasLayerSetName()) {
					node.put("<xmlattr>.LayerSetName", layerset->LayerSetName());
				}
				IfcMaterialLayer::list::ptr ls = layerset->MaterialLayers();
				for (IfcMaterialLayer::list::it jt = ls->begin(); jt != ls->end(); ++jt) {
					ptree subnode;
					if ((*jt)->hasMaterial()) {
						subnode.put("<xmlattr>.Name", (*jt)->Material()->Name());
					}
					format_entity_instance(*jt, subnode, node);
				}
			} else if (mat->as<IfcMaterialList>()) {
				IfcMaterial::list::ptr mats = mat->as<IfcMaterialList>()->Materials();
				for (IfcMaterial::list::it jt = mats->begin(); jt != mats->end(); ++jt) {
					ptree subnode;
					format_entity_instance(*jt, subnode, node);
				}
			}
			format_entity_instance((IfcUtil::IfcBaseEntity*) mat, node, materials);
		}
	}

	root.add_child("ifc.header",        header);
	root.add_child("ifc.units",         units);
	root.add_child("ifc.properties",    properties);
	root.add_child("ifc.types",         types);
    root.add_child("ifc.layers",        layers);
	root.add_child("ifc.materials",     materials);
	root.add_child("ifc.decomposition", decomposition);

	root.put("ifc.<xmlattr>.xmlns:xlink", "http://www.w3.org/1999/xlink");

#if BOOST_VERSION >= 105600
	boost::property_tree::xml_writer_settings<ptree::key_type> settings = boost::property_tree::xml_writer_make_settings<ptree::key_type>('\t', 1);
#else
	boost::property_tree::xml_writer_settings<char> settings('\t', 1);
#endif
	boost::property_tree::write_xml(xml_filename, root, std::locale(), settings);
}
