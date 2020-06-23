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

#include "JsonSerializer.h"

#include "../../ifcparse/IfcSIPrefix.h"
#include "../../ifcgeom/IfcGeom.h"
#include "../../ifcparse/utils.h"

#include <map>
#include <algorithm>
#include <utility>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

// The ifc json version written to the exported json file
#define IFC_JSON_VERSION "1.0"

// Utils
namespace {
    std::vector<std::string> filter_empty_strings(const std::vector<std::string>& source) {
        std::vector<std::string> filtered_items;

        for (const std::string& item : source) {
            if (item.length() > 0) {
                filtered_items.push_back(item);
            }
        }

        return filtered_items;
    }
}

namespace {
    struct MAKE_TYPE_NAME(factory_t) {
        JsonSerializer *operator()(IfcParse::IfcFile *file, const std::string &json_filename) const {
            MAKE_TYPE_NAME(JsonSerializer) *s = new MAKE_TYPE_NAME(JsonSerializer)(file, json_filename);
            s->setFile(file);
            return s;
        }
    };
}

void MAKE_INIT_FN(JsonSerializer)(JsonSerializerFactory::Factory *mapping) {
    static const std::string schema_name = STRINGIFY(IfcSchema);
    MAKE_TYPE_NAME(factory_t) factory;
    mapping->bind(schema_name, factory);
}

namespace {
    // TODO: Make this a member of JsonSerializer?
    std::map<std::string, std::string> MAKE_TYPE_NAME(argument_name_map);

    // Format an IFC attribute and maybe returns as string. Only literal scalar values are converted.
    // Things like entity instances and lists are omitted.
    boost::optional<std::string> format_attribute(const Argument* argument, IfcUtil::ArgumentType argument_type, const std::string& argument_name) {
        boost::optional<std::string> value;

        // Hard-code lat-lon as it represents an array of integers best emitted as a single decimal
        if (argument_name == "IfcSite.RefLatitude" || argument_name == "IfcSite.RefLongitude") {
            std::vector<int> angle = *argument;
            double deg;

            if (angle.size() >= 3) {
                deg = angle[0] + angle[1] / 60. + angle[2] / 3600.;
                int precision = 8;

                if (angle.size() == 4) {
                    deg += angle[3] / (1000000. * 3600.);
                    precision = 14;
                }

                std::stringstream stream;
                stream << std::setprecision(precision) << deg;
                value = stream.str();
            }

            return value;
        }

        switch(argument_type) {
            case IfcUtil::Argument_BOOL: {
                const bool b = *argument;
                value = b ? "true" : "false";
                break;
            }
            case IfcUtil::Argument_DOUBLE: {
                const double d = *argument;
                std::stringstream stream;
                stream << d;
                value = stream.str();
                break;
            }
            case IfcUtil::Argument_STRING:
            case IfcUtil::Argument_ENUMERATION: {
                value = static_cast<std::string>(*argument);
                break;
            }
            case IfcUtil::Argument_INT: {
                const int v = *argument;
                std::stringstream stream;
                stream << v;
                value = stream.str();
                break;
            }
            case IfcUtil::Argument_ENTITY_INSTANCE: {
                IfcUtil::IfcBaseClass* e = *argument;

                if (!e->declaration().as_entity()) {
                    IfcUtil::IfcBaseType* f = (IfcUtil::IfcBaseType*) e;
                    value = format_attribute(f->data().getArgument(0), f->data().getArgument(0)->type(), argument_name);
                }
                else if (e->declaration().is(IfcSchema::IfcSIUnit::Class()) || e->declaration().is(IfcSchema::IfcConversionBasedUnit::Class())) {
                    // Some string concatenation to have a unit name as a XML attribute.
                    std::string unit_name;

                    if (e->declaration().is(IfcSchema::IfcSIUnit::Class())) {
                        IfcSchema::IfcSIUnit* unit = (IfcSchema::IfcSIUnit*) e;
                        unit_name = IfcSchema::IfcSIUnitName::ToString(unit->Name());

                        if (unit->hasPrefix()) {
                            unit_name = IfcSchema::IfcSIPrefix::ToString(unit->Prefix()) + unit_name;
                        }
                    }
                    else {
                        IfcSchema::IfcConversionBasedUnit* unit = (IfcSchema::IfcConversionBasedUnit*) e;
                        unit_name = unit->Name();
                    }

                    value = unit_name;
                }
                else if (e->declaration().is(IfcSchema::IfcLocalPlacement::Class())) {
                    IfcSchema::IfcLocalPlacement* placement = e->as<IfcSchema::IfcLocalPlacement>();
                    gp_Trsf transform;
                    IfcGeom::MAKE_TYPE_NAME(Kernel) kernel;

                    if (kernel.convert(placement, transform)) {
                        std::stringstream stream;

                        for (int i = 1; i < 5; ++i) {
                            for (int j = 1; j < 4; ++j) {
                                const double transform_value = transform.Value(j, i);
                                stream << transform_value << " ";
                            }

                            stream << ((i == 4) ? "1" : "0 ");
                        }
                        value = stream.str();
                    }
                }
                break;
            }
            default:
                break;
        }

        return value;
    }

    // Formats IFC entity instance, adds properties to the referenced jsonObject
    void format_entity_instance(IfcUtil::IfcBaseEntity* instance, json::reference jsonObject, bool as_link = false) {
        if (!jsonObject.is_object()) {
            Logger::Error("Json reference must be an object!", instance);
            return;
        }

        const unsigned n = instance->declaration().attribute_count();

        for (unsigned i = 0; i < n; ++i) {
            try {
                instance->data().getArgument(i);
            }
            catch (const std::exception&) {
                Logger::Error("Expected " + std::to_string(n) + " attributes for:", instance);
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
            }
            catch (const std::exception& e) {
                Logger::Error(e);
            }
            catch (const Standard_ConstructionError& e) {
                Logger::Error(e.GetMessageString(), instance);
            }

            if (value) {
                if (as_link) {
                    if (argument_name == "id") {
                        jsonObject["@{http://www.w3.org/1999/xlink}href"] = std::string("#") + *value;
                    }
                }
                else {
                    std::stringstream stream;
                    stream << "@" << argument_name;
                    jsonObject[stream.str()] = *value;
                }
            }
        }
    }

    std::string qualify_unrooted_instance(IfcUtil::IfcBaseClass* inst) {
        return inst->declaration().name() + "_" + std::to_string(inst->data().id());
    }

    // Initializes an array in a jsonObject with jsonKey, creates an empty object to that array and returns the reference
    json::reference getEmptyObjectReferenceInArray(const std::string& jsonKey, json::reference jsonObject) {
        // Get a json reference to the target jsonKey
        json::reference arrayReference = jsonObject[jsonKey];

        // Initialize the array if not done previously
        if (arrayReference.is_null()) {
            arrayReference = json::array();
        }

        // Add empty object to array and return its reference
        arrayReference += json::object();
        return arrayReference.back();
    }

    // A function to be called recursively. Template specialization is used 
    // to descend into decomposition, containment and property relationships.
    template <typename A>
    void descend(A* instance, json::reference jsonObject, IfcUtil::IfcBaseClass* parent = nullptr) {
        if (!jsonObject.is_object() && !jsonObject.is_null()) {
            Logger::Error("Json reference must be an object or null!", instance);
            return;
        }

        // If the instance is an IfcObjectDefinition -> can have children -> descend deeper
        if (instance->declaration().is(IfcSchema::IfcObjectDefinition::Class())) {
            // Use the created empty json object as the reference
            descend(instance->template as<IfcSchema::IfcObjectDefinition>(), jsonObject, parent);
        }
        // Otherwise just format the instance
        else {
            // Initialize a container array for the IFC type if not created yet
            // add an empty object to that array and get the reference
            json::reference targetObject = instance->declaration().is(IfcSchema::IfcProject::Class()) ?
                jsonObject["IfcProject"] = json::object() :
                getEmptyObjectReferenceInArray(instance->declaration().name(), jsonObject);

            // Add entity instance properties to the created empty json object
            format_entity_instance(instance, targetObject);
        }
    }

    // Returns related entity instances using IFC's objectified relationship model.
    // The second and third argument require a member function pointer.
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

    // Descends into the tree by recursion into IfcRelContainedInSpatialStructure,
    // IfcRelDecomposes, IfcRelDefinesByType, IfcRelDefinesByProperties relations.
    template <>
    void descend(IfcSchema::IfcObjectDefinition* product, json::reference jsonObject, IfcUtil::IfcBaseClass* parent) {
        if (!jsonObject.is_object() && !jsonObject.is_null()) {
            Logger::Error("Json reference must be an object or null!", product);
            return;
        }

        // TODO: This is commented out to replicate old output where FillsVoids elements (IfcWindow, IfcDoor...)
        //  were listed under IfcBuildingStorey etc.
        /*
        if (product->declaration().is(IfcSchema::IfcElement::Class())) {
            auto voids = product->as<IfcSchema::IfcElement>()->FillsVoids();

            if (voids && voids->size() == 1 && (*voids->begin())->RelatingOpeningElement() != parent) {
                // Fills are placed under their corresponding opening, return early to avoid duplication.
                return;
            }
        }
        */

        // Initialize a container array for the IFC type if not created yet
        // add an empty object to that array and get the reference
        // There can be only one IfcProject so do not create an array of it
        json::reference targetObject = product->declaration().is(IfcSchema::IfcProject::Class()) ?
            jsonObject["IfcProject"] = json::object() :
            getEmptyObjectReferenceInArray(product->declaration().name(), jsonObject);

        // Add entity instance properties to json object
        format_entity_instance(product, targetObject);

        // Descend into related objects under IfcSpatialStructureElement
        if (product->declaration().is(IfcSchema::IfcSpatialStructureElement::Class())) {
            IfcSchema::IfcSpatialStructureElement* structure = (IfcSchema::IfcSpatialStructureElement*) product;

            IfcSchema::IfcObjectDefinition::list::ptr elements = get_related
                    <IfcSchema::IfcSpatialStructureElement, IfcSchema::IfcRelContainedInSpatialStructure, IfcSchema::IfcObjectDefinition>
                    (structure, &IfcSchema::IfcSpatialStructureElement::ContainsElements, &IfcSchema::IfcRelContainedInSpatialStructure::RelatedElements);

            for (IfcSchema::IfcObjectDefinition::list::it it = elements->begin(); it != elements->end(); ++it) {
                descend(*it, targetObject);
            }
        }

        // Descend into openings under IfcElement
        if (product->declaration().is(IfcSchema::IfcElement::Class())) {
            IfcSchema::IfcElement *element = static_cast<IfcSchema::IfcElement*>(product);
            IfcSchema::IfcOpeningElement::list::ptr openings = get_related
                    <IfcSchema::IfcElement, IfcSchema::IfcRelVoidsElement, IfcSchema::IfcOpeningElement>
                    (element, &IfcSchema::IfcElement::HasOpenings, &IfcSchema::IfcRelVoidsElement::RelatedOpeningElement);

            for (IfcSchema::IfcOpeningElement::list::it it = openings->begin(); it != openings->end(); ++it) {
                descend(*it, targetObject);
            }
        }

        // TODO: This is commented out to replicate old output where FillsVoids elements (IfcWindow, IfcDoor...)
        //  were listed under IfcBuildingStorey etc. If this was enabled, the fills would be duplicated under openings
        // Descend into fills under IfcOpeningElement
        /*
        if (product->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
            IfcSchema::IfcOpeningElement* opening = static_cast<IfcSchema::IfcOpeningElement*>(product);
            IfcSchema::IfcElement::list::ptr fills = get_related
                    <IfcSchema::IfcOpeningElement, IfcSchema::IfcRelFillsElement, IfcSchema::IfcElement>
                    (opening, &IfcSchema::IfcOpeningElement::HasFillings, &IfcSchema::IfcRelFillsElement::RelatedBuildingElement);

            for (IfcSchema::IfcElement::list::it it = fills->begin(); it != fills->end(); ++it) {
                descend(*it, targetObject);
            }
        }
        */

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
                (product, &IfcSchema::IfcObjectDefinition::IsNestedBy, &IfcSchema::IfcRelNests::RelatedObjects)
        );
#endif

        // Descend into IfcObjectDefinitions under this element
        for (IfcSchema::IfcObjectDefinition::list::it it = structures->begin(); it != structures->end(); ++it) {
            IfcSchema::IfcObjectDefinition* ob = *it;
            descend(ob, targetObject);
        }

        // Format property sets, quantities and the object type under this IfcObject
        if (product->declaration().is(IfcSchema::IfcObject::Class())) {
            IfcSchema::IfcObject* object = product->as<IfcSchema::IfcObject>();

            IfcSchema::IfcPropertySetDefinition::list::ptr property_sets = get_related
                    <IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByProperties, IfcSchema::IfcPropertySetDefinition>
                    (object, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByProperties::RelatingPropertyDefinition);

            // Format property sets & quantities
            for (IfcSchema::IfcPropertySetDefinition::list::it it = property_sets->begin(); it != property_sets->end(); ++it) {
                IfcSchema::IfcPropertySetDefinition* pset = *it;

                json::reference to = getEmptyObjectReferenceInArray(pset->declaration().name(), targetObject);

                if (pset->declaration().is(IfcSchema::IfcPropertySet::Class())) {
                    format_entity_instance(pset, to, true);
                }
                else if (pset->declaration().is(IfcSchema::IfcElementQuantity::Class())) {
                    format_entity_instance(pset, to, true);
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

            // Format type, an IfcObject can have 0-1 types
            for (IfcSchema::IfcTypeObject::list::it it = types->begin(); it != types->end(); ++it) {
                IfcSchema::IfcTypeObject* type = *it;

                json::reference to = targetObject[type->declaration().name()] = json::object();
                format_entity_instance(type, to, true);
            }
        }

        // Format links to layers and materials under IfcProduct
        if (product->declaration().is(IfcSchema::IfcProduct::Class())) {
            std::map<std::string, IfcUtil::IfcBaseEntity*> layers = IfcGeom::Kernel::get_layers(product);

            // Format layer name links
            for (std::map<std::string, IfcUtil::IfcBaseEntity*>::const_iterator it = layers.begin(); it != layers.end(); ++it) {
                // IfcPresentationLayerAssignments don't have GUIDs (only optional Identifier) so use name as the ID.
                // Note that the IfcPresentationLayerAssignment passed here doesn't really matter as as_link is true for the format_entity_instance() call.
                json::reference to = getEmptyObjectReferenceInArray(it->second->declaration().name(), targetObject);

                to["@{http://www.w3.org/1999/xlink}href"] = "#" + it->first;
                format_entity_instance(it->second, to, true);
            }

            IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();

            // Format material GUID links
            for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
                if ((*it)->as<IfcSchema::IfcRelAssociatesMaterial>()) {
                    IfcSchema::IfcMaterialSelect* mat = (*it)->as<IfcSchema::IfcRelAssociatesMaterial>()->RelatingMaterial();

                    json::reference to = getEmptyObjectReferenceInArray(((IfcUtil::IfcBaseEntity*) mat)->declaration().name(), targetObject);

                    to["@{http://www.w3.org/1999/xlink}href"] = "#" + qualify_unrooted_instance(mat);
                    format_entity_instance((IfcUtil::IfcBaseEntity*) mat, to, true);
                }
            }
        }
    }

    // Format IfcProperty instances and insert into the DOM. IfcComplexProperties are flattened out.
    void format_properties(const IfcSchema::IfcProperty::list::ptr& properties, json::reference jsonObject) {
        for (IfcSchema::IfcProperty::list::it it = properties->begin(); it != properties->end(); ++it) {
            IfcSchema::IfcProperty* p = *it;

            if (p->declaration().is(IfcSchema::IfcComplexProperty::Class())) {
                IfcSchema::IfcComplexProperty* complex = (IfcSchema::IfcComplexProperty*) p;
                format_properties(complex->HasProperties(), jsonObject);
            }
            else {
                json::reference targetObject = getEmptyObjectReferenceInArray(p->declaration().name(), jsonObject);
                format_entity_instance(p, targetObject);
            }
        }
    }

    // Format IfcElementQuantity instances and insert into the DOM.
    void format_quantities(const IfcSchema::IfcPhysicalQuantity::list::ptr& quantities, json::reference jsonObject) {
        for (IfcSchema::IfcPhysicalQuantity::list::it it = quantities->begin(); it != quantities->end(); ++it) {
            IfcSchema::IfcPhysicalQuantity* p = *it;

            json::reference targetObject = getEmptyObjectReferenceInArray(p->declaration().name(), jsonObject);

            format_entity_instance(p, targetObject);

            if (p->declaration().is(IfcSchema::IfcPhysicalComplexQuantity::Class())) {
                IfcSchema::IfcPhysicalComplexQuantity* complex = (IfcSchema::IfcPhysicalComplexQuantity*)p;
                format_quantities(complex->HasQuantities(), targetObject);
            }
        }
    }

    // Writes string value to json reference, if string is empty it writes nullptr
    void add_string(json::reference ref, std::string stringToAdd) {
        if (stringToAdd.length() == 0)
            ref = nullptr;
        else
            ref = stringToAdd;
    }

    // Writes string vector to json reference, filters empty string values
    void add_string_vector(json::reference ref, const std::vector<std::string>& vectorToAdd) {
        ref = filter_empty_strings(vectorToAdd);
    }
    
    void log_error(const char *error) {
        std::stringstream ss;
        ss << "Failed to get ifc file header data, error: '" << error << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }
} // ~unnamed namespace

void MAKE_TYPE_NAME(JsonSerializer)::writeIfcHeader(json::reference ifc) {
    json::reference header = ifc["header"];
    json::reference fileDescription = header["file_description"];
    json::reference fileName = header["file_name"];
    json::reference fileSchema = header["file_schema"];
    json::reference ifcJsonVersion = header["ifc_json_version"];

    add_string_vector(fileDescription["description"], file->header().file_description().description());
    add_string_vector(fileName["author"], file->header().file_name().author());
    add_string_vector(fileName["organization"], file->header().file_name().organization());
    add_string_vector(fileSchema["schema_identifiers"], file->header().file_schema().schema_identifiers());

    // TODO: Refactor to reduce repeated code
    try {
        add_string(fileDescription["implementation_level"], file->header().file_description().implementation_level());
    }
    catch (const IfcParse::IfcException& ex) {
        log_error(ex.what());
    }

    try {
        add_string(fileName["name"], file->header().file_name().name());
    }
    catch (const IfcParse::IfcException& ex) {
        log_error(ex.what());
    }

    try {
        add_string(fileName["time_stamp"], file->header().file_name().time_stamp());
    }
    catch (const IfcParse::IfcException& ex) {
        log_error(ex.what());
    }

    try {
        add_string(fileName["preprocessor_version"], file->header().file_name().preprocessor_version());
    }
    catch (const IfcParse::IfcException& ex) {
        log_error(ex.what());
    }

    try {
        add_string(fileName["originating_system"], file->header().file_name().originating_system());
    }
    catch (const IfcParse::IfcException& ex) {
        log_error(ex.what());
    }

    try {
        add_string(fileName["authorization"], file->header().file_name().authorization());
    }
    catch (const IfcParse::IfcException& ex) {
        log_error(ex.what());
    }

    add_string(ifcJsonVersion, IFC_JSON_VERSION);
}

void MAKE_TYPE_NAME(JsonSerializer)::finalize() {
    MAKE_TYPE_NAME(argument_name_map).insert(std::make_pair("GlobalId", "id"));

    IfcSchema::IfcProject::list::ptr projects = file->instances_by_type<IfcSchema::IfcProject>();
    if (projects->size() != 1) {
        Logger::Message(Logger::LOG_ERROR, "Expected a single IfcProject");
        return;
    }
    IfcSchema::IfcProject* project = *projects->begin();

    json jsonRoot;
    json::reference ifc = jsonRoot["ifc"];

    // Write the SPF header
    writeIfcHeader(ifc);

    // Write the decomposition
    descend(project, ifc["decomposition"]);

    // Write all property sets and values
    IfcSchema::IfcPropertySet::list::ptr psets = file->instances_by_type<IfcSchema::IfcPropertySet>();
    json::reference properties = ifc["properties"];

    for (IfcSchema::IfcPropertySet::list::it it = psets->begin(); it != psets->end(); ++it) {
        IfcSchema::IfcPropertySet* pset = *it;

        json::reference propertyObject = getEmptyObjectReferenceInArray(pset->declaration().name(), properties);

        format_entity_instance(pset, propertyObject);
        format_properties(pset->HasProperties(), propertyObject);
    }

    // Write all quantities and values
    IfcSchema::IfcElementQuantity::list::ptr quantitySets = file->instances_by_type<IfcSchema::IfcElementQuantity>();
    json::reference quantities = ifc["quantities"];

    for (IfcSchema::IfcElementQuantity::list::it it = quantitySets->begin(); it != quantitySets->end(); ++it) {
        IfcSchema::IfcElementQuantity* qto = *it;

        json::reference quantityObject = getEmptyObjectReferenceInArray(qto->declaration().name(), quantities);

        format_entity_instance(qto, quantityObject);
        format_quantities(qto->Quantities(), quantityObject);
    }

    // Write all type objects
    IfcSchema::IfcTypeObject::list::ptr type_objects = file->instances_by_type<IfcSchema::IfcTypeObject>();
    json::reference types = ifc["types"];

    for (IfcSchema::IfcTypeObject::list::it it = type_objects->begin(); it != type_objects->end(); ++it) {
        IfcSchema::IfcTypeObject* type_object = *it;

        descend(type_object, types);

        if (type_object->hasHasPropertySets()) {
            IfcSchema::IfcPropertySetDefinition::list::ptr property_sets = type_object->HasPropertySets();

            for (IfcSchema::IfcPropertySetDefinition::list::it jt = property_sets->begin(); jt != property_sets->end(); ++jt) {
                IfcSchema::IfcPropertySetDefinition *pset = *jt;

                if (pset->declaration().is(IfcSchema::IfcPropertySet::Class())) {
                    json::reference propertyObject = getEmptyObjectReferenceInArray(pset->declaration().name(), properties);
                    format_entity_instance(pset, propertyObject, true);
                }
            }
        }
    }

    // Write all assigned units
    IfcEntityList::ptr unit_assignments = project->UnitsInContext()->Units();
    json::reference units = ifc["units"];

    for (IfcEntityList::it it = unit_assignments->begin(); it != unit_assignments->end(); ++it) {
        json::reference unitObject = getEmptyObjectReferenceInArray((*it)->declaration().name(), units);

        if ((*it)->declaration().is(IfcSchema::IfcNamedUnit::Class())) {
            IfcSchema::IfcNamedUnit* named_unit = (*it)->as<IfcSchema::IfcNamedUnit>();

            format_entity_instance(named_unit, unitObject);
            unitObject["@SI_equivalent"] = IfcParse::get_SI_equivalent<IfcSchema>(named_unit);
        }
        else if ((*it)->declaration().is(IfcSchema::IfcMonetaryUnit::Class())) {
            format_entity_instance((*it)->as<IfcSchema::IfcMonetaryUnit>(), unitObject);
        }
    }

    // Write presentation layers 
    // IfcPresentationLayerAssignments don't have GUIDs (only optional Identifier)
    // so use names as the IDs and only insert those with unique names. In case of possible duplicate names/IDs
    // the first IfcPresentationLayerAssignment occurrence takes precedence.
    std::set<std::string> layer_names;
    IfcSchema::IfcPresentationLayerAssignment::list::ptr layer_assignments = file->instances_by_type<IfcSchema::IfcPresentationLayerAssignment>();
    json::reference layers = ifc["layers"];

    for (IfcSchema::IfcPresentationLayerAssignment::list::it it = layer_assignments->begin(); it != layer_assignments->end(); ++it) {
        const std::string& name = (*it)->Name();

        if (layer_names.find(name) == layer_names.end()) {
            layer_names.insert(name);

            json::reference layerObject = getEmptyObjectReferenceInArray((*it)->declaration().name(), layers);
            layerObject["@id"] = name;
            format_entity_instance(*it, layerObject);
        }
    }

    // Write materials
    IfcSchema::IfcRelAssociatesMaterial::list::ptr materal_associations = file->instances_by_type<IfcSchema::IfcRelAssociatesMaterial>();
    std::set<IfcSchema::IfcMaterialSelect *> emitted_materials;
    json::reference materials = ifc["materials"];

    for (IfcSchema::IfcRelAssociatesMaterial::list::it it = materal_associations->begin(); it != materal_associations->end(); ++it) {
        IfcSchema::IfcMaterialSelect* mat = (**it).RelatingMaterial();
        if (emitted_materials.find(mat) == emitted_materials.end()) {
            emitted_materials.insert(mat);

            // Write IfcMaterialLayerSetUsage / IfcMaterialLayerSet
            if (mat->as<IfcSchema::IfcMaterialLayerSetUsage>() || mat->as<IfcSchema::IfcMaterialLayerSet>()) {
                IfcSchema::IfcMaterialLayerSet* layerset = mat->as<IfcSchema::IfcMaterialLayerSet>();
                std::string materialJsonKey = "IfcMaterialLayerSet";

                if (!layerset) {
                    materialJsonKey = "IfcMaterialLayerSetUsage";
                    layerset = mat->as<IfcSchema::IfcMaterialLayerSetUsage>()->ForLayerSet();
                }

                json::reference materialObject = getEmptyObjectReferenceInArray(materialJsonKey, materials);
                materialObject["@id"] = qualify_unrooted_instance(mat);

                if (layerset->hasLayerSetName()) {
                    materialObject["@LayerSetName"] = layerset->LayerSetName();
                }

                IfcSchema::IfcMaterialLayer::list::ptr ls = layerset->MaterialLayers();

                for (IfcSchema::IfcMaterialLayer::list::it jt = ls->begin(); jt != ls->end(); ++jt) {
                    json::reference subMaterialObject = getEmptyObjectReferenceInArray((*jt)->declaration().name(), materialObject);

                    if ((*jt)->hasMaterial()) {
                        subMaterialObject["@Name"] = (*jt)->Material()->Name();
                    }
                    
                    format_entity_instance(*jt, subMaterialObject);
                }

                format_entity_instance((IfcUtil::IfcBaseEntity*) mat, materialObject);
            }
            // write IfcMaterialList
            else if (mat->as<IfcSchema::IfcMaterialList>()) {
                IfcSchema::IfcMaterial::list::ptr mats = mat->as<IfcSchema::IfcMaterialList>()->Materials();

                json::reference materialObject = getEmptyObjectReferenceInArray("IfcMaterialList", materials);
                materialObject["@id"] = qualify_unrooted_instance(mat);

                for (IfcSchema::IfcMaterial::list::it jt = mats->begin(); jt != mats->end(); ++jt) {
                    json::reference subMaterialObject = getEmptyObjectReferenceInArray((*jt)->declaration().name(), materialObject);

                    format_entity_instance(*jt, subMaterialObject);
                }

                format_entity_instance((IfcUtil::IfcBaseEntity *) mat, materialObject);
            }
            // write IfcMaterial
            else if (mat->as<IfcSchema::IfcMaterial>()) {
                json::reference materialObject = getEmptyObjectReferenceInArray("IfcMaterial", materials);
                materialObject["@id"] = qualify_unrooted_instance(mat);

                format_entity_instance((IfcUtil::IfcBaseEntity*) mat, materialObject);
            }
        }
    }

    std::ofstream f(IfcUtil::path::from_utf8(json_filename).c_str());

    // Write json to stream
    f << jsonRoot << std::endl;
}
