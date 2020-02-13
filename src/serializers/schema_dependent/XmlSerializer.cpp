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
#include "../../ifcgeom/IfcGeom.h"
#include "../../ifcparse/utils.h"

using boost::property_tree::ptree;

#include "XmlSerializer.h"

namespace {
	struct MAKE_TYPE_NAME(factory_t) {
		XmlSerializer* operator()(IfcParse::IfcFile* file, const std::string& xml_filename) const {
			MAKE_TYPE_NAME(XmlSerializer)* s = new MAKE_TYPE_NAME(XmlSerializer)(file, xml_filename);
			s->setFile(file);
			return s;
		}
	};
}

void MAKE_INIT_FN(XmlSerializer)(XmlSerializerFactory::Factory* mapping) {
	static const std::string schema_name = STRINGIFY(IfcSchema);
	MAKE_TYPE_NAME(factory_t) factory;
	mapping->bind(schema_name, factory);
}

namespace {

// TODO: Make this a member of XmlSerializer?
std::map<std::string, std::string> MAKE_TYPE_NAME(argument_name_map);

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
			if (!e->declaration().as_entity()) {
				IfcUtil::IfcBaseType* f = (IfcUtil::IfcBaseType*) e;
				value = format_attribute(f->data().getArgument(0), f->data().getArgument(0)->type(), argument_name);
			} else if (e->declaration().is(IfcSchema::IfcSIUnit::Class()) || e->declaration().is(IfcSchema::IfcConversionBasedUnit::Class())) {
				// Some string concatenation to have a unit name as a XML attribute.

				std::string unit_name;

				if (e->declaration().is(IfcSchema::IfcSIUnit::Class())) {
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
			} else if (e->declaration().is(IfcSchema::IfcLocalPlacement::Class())) {
				IfcSchema::IfcLocalPlacement* placement = e->as<IfcSchema::IfcLocalPlacement>();
				gp_Trsf trsf;
				IfcGeom::MAKE_TYPE_NAME(Kernel) kernel;
				
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
	const unsigned n = instance->declaration().attribute_count();
	for (unsigned i = 0; i < n; ++i) {
		try {
		    instance->data().getArgument(i);
		} catch (const std::exception&) {
		    Logger::Error("Expected " + boost::lexical_cast<std::string>(n) + " attributes for:", instance);
		    break;
		}		
		const Argument* argument = instance->data().getArgument(i);
		if (argument->isNull()) continue;

		std::string argument_name = instance->declaration().attribute_by_index(i)->name();
		std::map<std::string, std::string>::const_iterator argument_name_it;
		argument_name_it = MAKE_TYPE_NAME(argument_name_map).find(argument_name);
		if (argument_name_it != MAKE_TYPE_NAME(argument_name_map).end()) {
			argument_name = argument_name_it->second;
		}
		const IfcUtil::ArgumentType argument_type = instance->data().getArgument(i)->type();

		const std::string qualified_name = instance->declaration().name() + "." + argument_name;
		boost::optional<std::string> value;
		try {
			value = format_attribute(argument, argument_type, qualified_name);
		} catch (const std::exception& e) {
			Logger::Error(e);
		} catch (const Standard_ConstructionError& e) {
			Logger::Error(e.GetMessageString(), instance);
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
	return tree.add_child(instance->declaration().name(), child);
}

// Formats an entity instances as a ptree node, and insert into the DOM. Recurses
// over the entity attributes and writes them as xml attributes of the node.
ptree& format_entity_instance(IfcUtil::IfcBaseEntity* instance, ptree& tree, bool as_link = false) {
    ptree child;
    return format_entity_instance(instance, child, tree, as_link);
}

std::string qualify_unrooted_instance(IfcUtil::IfcBaseClass* inst) {
	return inst->declaration().name() + "_" + boost::lexical_cast<std::string>(inst->data().id());
}

// A function to be called recursively. Template specialization is used 
// to descend into decomposition, containment and property relationships.
template <typename A>
ptree& descend(A* instance, ptree& tree) {
	if (instance->declaration().is(IfcSchema::IfcObjectDefinition::Class())) {
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
ptree& descend(IfcSchema::IfcObjectDefinition* product, ptree& tree) {
	ptree& child = format_entity_instance(product, tree);
	
	if (product->declaration().is(IfcSchema::IfcSpatialStructureElement::Class())) {
		IfcSchema::IfcSpatialStructureElement* structure = (IfcSchema::IfcSpatialStructureElement*) product;

		IfcSchema::IfcObjectDefinition::list::ptr elements = get_related
			<IfcSchema::IfcSpatialStructureElement, IfcSchema::IfcRelContainedInSpatialStructure, IfcSchema::IfcObjectDefinition>
			(structure, &IfcSchema::IfcSpatialStructureElement::ContainsElements, &IfcSchema::IfcRelContainedInSpatialStructure::RelatedElements);
	
		for (IfcSchema::IfcObjectDefinition::list::it it = elements->begin(); it != elements->end(); ++it) {
			descend(*it, child);
		}
	}

    if (product->declaration().is(IfcSchema::IfcElement::Class())) {
		IfcSchema::IfcElement* element = static_cast<IfcSchema::IfcElement*>(product);
		IfcSchema::IfcOpeningElement::list::ptr openings = get_related<IfcSchema::IfcElement, IfcSchema::IfcRelVoidsElement, IfcSchema::IfcOpeningElement>(
            element, &IfcSchema::IfcElement::HasOpenings, &IfcSchema::IfcRelVoidsElement::RelatedOpeningElement);

        for (IfcSchema::IfcOpeningElement::list::it it = openings->begin(); it != openings->end(); ++it) {
            descend(*it, child);
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
		descend(ob, child);
	}

	if (product->declaration().is(IfcSchema::IfcObject::Class())) {
		IfcSchema::IfcObject* object = product->as<IfcSchema::IfcObject>();

		IfcSchema::IfcPropertySetDefinition::list::ptr property_sets = get_related
			<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByProperties, IfcSchema::IfcPropertySetDefinition>
			(object, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByProperties::RelatingPropertyDefinition);

		for (IfcSchema::IfcPropertySetDefinition::list::it it = property_sets->begin(); it != property_sets->end(); ++it) {
			IfcSchema::IfcPropertySetDefinition* pset = *it;
			if (pset->declaration().is(IfcSchema::IfcPropertySet::Class())) {
				format_entity_instance(pset, child, true);
			}
			if (pset->declaration().is(IfcSchema::IfcElementQuantity::Class())) {
				format_entity_instance(pset, child, true);
			}
			if (pset->declaration().is(IfcSchema::IfcElementQuantity::Class())) {
				format_entity_instance(pset, child, true);
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
			format_entity_instance(type, child, true);
		}
	}

    if (product->declaration().is(IfcSchema::IfcProduct::Class())) {
        std::map<std::string, IfcUtil::IfcBaseEntity*> layers = IfcGeom::Kernel::get_layers(product);
        for (std::map<std::string, IfcUtil::IfcBaseEntity*>::const_iterator it = layers.begin(); it != layers.end(); ++it) {
            // IfcPresentationLayerAssignments don't have GUIDs (only optional Identifier) so use name as the ID.
            // Note that the IfcPresentationLayerAssignment passed here doesn't really matter as as_link is true
            // for the format_entity_instance() call.
            ptree node;
            node.put("<xmlattr>.xlink:href", "#" + it->first);
            format_entity_instance(it->second, node, child, true);
        }
		
		IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
		for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
			if ((*it)->as<IfcSchema::IfcRelAssociatesMaterial>()) {
				IfcSchema::IfcMaterialSelect* mat = (*it)->as<IfcSchema::IfcRelAssociatesMaterial>()->RelatingMaterial();
				ptree node;
				node.put("<xmlattr>.xlink:href", "#" + qualify_unrooted_instance(mat));
				format_entity_instance((IfcUtil::IfcBaseEntity*) mat, node, child, true);
			}
		}
    }

	return child;
}

// Format IfcProperty instances and insert into the DOM. IfcComplexProperties are flattened out.
void format_properties(IfcSchema::IfcProperty::list::ptr properties, ptree& node) {
	for (IfcSchema::IfcProperty::list::it it = properties->begin(); it != properties->end(); ++it) {
		IfcSchema::IfcProperty* p = *it;
		if (p->declaration().is(IfcSchema::IfcComplexProperty::Class())) {
			IfcSchema::IfcComplexProperty* complex = (IfcSchema::IfcComplexProperty*) p;
			format_properties(complex->HasProperties(), node);
		} else {
			format_entity_instance(p, node);
		}
	}
}

// Format IfcElementQuantity instances and insert into the DOM.
void format_quantities(IfcSchema::IfcPhysicalQuantity::list::ptr quantities, ptree& node) {
	for (IfcSchema::IfcPhysicalQuantity::list::it it = quantities->begin(); it != quantities->end(); ++it) {
		IfcSchema::IfcPhysicalQuantity* p = *it;
		ptree& node2 = format_entity_instance(p, node);
		if (p->declaration().is(IfcSchema::IfcPhysicalComplexQuantity::Class())) {
			IfcSchema::IfcPhysicalComplexQuantity* complex = (IfcSchema::IfcPhysicalComplexQuantity*)p;
			format_quantities(complex->HasQuantities(), node2);
		}
	}
}

} // ~unnamed namespace

void MAKE_TYPE_NAME(XmlSerializer)::finalize() {
	MAKE_TYPE_NAME(argument_name_map).insert(std::make_pair("GlobalId", "id"));

	IfcSchema::IfcProject::list::ptr projects = file->instances_by_type<IfcSchema::IfcProject>();
	if (projects->size() != 1) {
		Logger::Message(Logger::LOG_ERROR, "Expected a single IfcProject");
		return;
	}
	IfcSchema::IfcProject* project = *projects->begin();

	ptree root, header, units, decomposition, properties, quantities, types, layers, materials;
	
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
	descend(project, decomposition);

	// Write all property sets and values as XML nodes.
	IfcSchema::IfcPropertySet::list::ptr psets = file->instances_by_type<IfcSchema::IfcPropertySet>();
	for (IfcSchema::IfcPropertySet::list::it it = psets->begin(); it != psets->end(); ++it) {
		IfcSchema::IfcPropertySet* pset = *it;
		ptree& node = format_entity_instance(pset, properties);
		format_properties(pset->HasProperties(), node);
	}
	
	// Write all quantities and values as XML nodes.
	IfcSchema::IfcElementQuantity::list::ptr qtosets = file->instances_by_type<IfcSchema::IfcElementQuantity>();
	for (IfcSchema::IfcElementQuantity::list::it it = qtosets->begin(); it != qtosets->end(); ++it) {
		IfcSchema::IfcElementQuantity* qto = *it;
		ptree& node = format_entity_instance(qto, quantities);
		format_quantities(qto->Quantities(), node);
	}


	// Write all type objects as XML nodes.
	IfcSchema::IfcTypeObject::list::ptr type_objects = file->instances_by_type<IfcSchema::IfcTypeObject>();
	for (IfcSchema::IfcTypeObject::list::it it = type_objects->begin(); it != type_objects->end(); ++it) {
		IfcSchema::IfcTypeObject* type_object = *it;
		ptree& node = descend(type_object, types);
		// ptree& node = format_entity_instance(type_object, types);	
		
		if (type_object->hasHasPropertySets()) {
			IfcSchema::IfcPropertySetDefinition::list::ptr property_sets = type_object->HasPropertySets();
			for (IfcSchema::IfcPropertySetDefinition::list::it jt = property_sets->begin(); jt != property_sets->end(); ++jt) {
				IfcSchema::IfcPropertySetDefinition* pset = *jt;
				if (pset->declaration().is(IfcSchema::IfcPropertySet::Class())) {
					format_entity_instance(pset, node, true);
				}
			}
		}
	}

	// Write all assigned units as XML nodes.
	IfcEntityList::ptr unit_assignments = project->UnitsInContext()->Units();
	for (IfcEntityList::it it = unit_assignments->begin(); it != unit_assignments->end(); ++it) {
		if ((*it)->declaration().is(IfcSchema::IfcNamedUnit::Class())) {
			IfcSchema::IfcNamedUnit* named_unit = (*it)->as<IfcSchema::IfcNamedUnit>();
			ptree& node = format_entity_instance(named_unit, units);
			node.put("<xmlattr>.SI_equivalent", IfcParse::get_SI_equivalent<IfcSchema>(named_unit));
		} else if ((*it)->declaration().is(IfcSchema::IfcMonetaryUnit::Class())) {
			format_entity_instance((*it)->as<IfcSchema::IfcMonetaryUnit>(), units);
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
            format_entity_instance(*it, node, layers);
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
				if (layerset->hasLayerSetName()) {
					node.put("<xmlattr>.LayerSetName", layerset->LayerSetName());
				}
				IfcSchema::IfcMaterialLayer::list::ptr ls = layerset->MaterialLayers();
				for (IfcSchema::IfcMaterialLayer::list::it jt = ls->begin(); jt != ls->end(); ++jt) {
					ptree subnode;
					if ((*jt)->hasMaterial()) {
						subnode.put("<xmlattr>.Name", (*jt)->Material()->Name());
					}
					format_entity_instance(*jt, subnode, node);
				}
			} else if (mat->as<IfcSchema::IfcMaterialList>()) {
				IfcSchema::IfcMaterial::list::ptr mats = mat->as<IfcSchema::IfcMaterialList>()->Materials();
				for (IfcSchema::IfcMaterial::list::it jt = mats->begin(); jt != mats->end(); ++jt) {
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
	root.add_child("ifc.quantities",    quantities);
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
	
	std::ofstream f(IfcUtil::path::from_utf8(xml_filename).c_str());
	boost::property_tree::write_xml(f, root, settings);
}
