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

#ifdef WITH_GLTF

#include "JsonSerializer.h"

#include <algorithm>
#include <fstream>

#include <nlohmann/json.hpp>

#include "../../ifcparse/IfcSIPrefix.h"
#include "../../ifcparse/utils.h"
#include "../../ifcparse/IfcLogger.h"

using json = nlohmann::json;

namespace {
	struct POSTFIX_SCHEMA(factory_t) {
		JsonSerializer* operator()(IfcParse::IfcFile* file, const std::string& json_filename, JsonSerializer::Dialect dialect, Logger& logger) const {
            POSTFIX_SCHEMA(JsonSerializer)* s = new POSTFIX_SCHEMA(JsonSerializer)(file, json_filename, dialect, logger);
			s->setFile(file);
			return s;
		}
	};
}

void MAKE_INIT_FN(JsonSerializer)(JsonSerializerFactory::Factory* mapping) {
	static const std::string schema_name = STRINGIFY(IfcSchema);
	POSTFIX_SCHEMA(factory_t) factory;
	mapping->bind(schema_name, factory);
}

namespace {

class format_value_visitor : public boost::static_visitor<std::string> {
  public:

    format_value_visitor() = default;

    template <typename T>
    json operator()(const T& t) const {
        if constexpr (std::is_same_v<std::decay_t<T>, Derived> || std::is_same_v<std::decay_t<T>, boost::dynamic_bitset<>> || std::is_same_v<std::decay_t<T>, IfcUtil::IfcBaseClass*> || std::is_same_v<std::decay_t<T>, std::vector<int>> || std::is_same_v<std::decay_t<T>, std::vector<double>> || std::is_same_v<std::decay_t<T>, std::vector<std::string>> || std::is_same_v<std::decay_t<T>, std::vector<boost::dynamic_bitset<>>> || std::is_same_v<std::decay_t<T>, aggregate_of_instance::ptr> || std::is_same_v<std::decay_t<T>, aggregate_of_aggregate_of_instance::ptr> || std::is_same_v<std::decay_t<T>, std::vector<std::vector<int>>> || std::is_same_v<std::decay_t<T>, std::vector<std::vector<double>>> || std::is_same_v<std::decay_t<T>, empty_aggregate_t> || std::is_same_v<std::decay_t<T>, empty_aggregate_of_aggregate_t> || std::is_same_v<std::decay_t<T>, Blank>) {
            return "";
        } else if constexpr (std::is_same_v<std::decay_t<T>, boost::logic::tribool>) {
            // @todo handle indeterminate
            return "";
        } else if constexpr (std::is_same_v<std::decay_t<T>, std::string>) {
            return t;
        } else if constexpr (std::is_same_v<std::decay_t<T>, EnumerationReference>) {
            return t.value();
        } else {
            return t;
        }
    }
};

class get_type_visitor : public boost::static_visitor<std::string> {
  public:
    get_type_visitor() = default;

    template <typename T>
    std::string operator()(const T& t) const {
        // @todo more types
        return "number";
    }
};

// Returns related entity instances using IFC's objectified relationship
// model. The second and third argument require a member function pointer.
template <typename T, typename U, typename V, typename F, typename G>
auto get_related(Logger& logger, T* t, F f, G g) {
    typename U::list::ptr li = (*t.*f)()->template as<U>();
    typename aggregate_of<V>::ptr acc(new aggregate_of<V>);
    for (typename U::list::it it = li->begin(); it != li->end(); ++it) {
        U* u = *it;
        try {
            acc->push((*u.*g)()->template as<V>());
        } catch (IfcParse::IfcException& e) {
            logger.Error("SER", 6, e);
        }
    }
    return acc;
}

void format_entity_instance(IfcUtil::IfcBaseEntity* instance, json& tree, Logger& logger, IfcUtil::IfcBaseEntity* parent = nullptr) {
    /*
    {
        "id" : string,            // Element GUID (IFC GloballyUniqueId)
        "name" : string,          // Element name
        "longName" ?: string,     // Long name (for spatial elements)
        "type" : string,          // IFC entity type
        "parent" : string | null, // Parent element GUID (null for root)
        "groups" ?: string[],     // Array of group GUIDs
        "ObjectType" ?: string,   // ObjectType attribute (for IfcObject)
        "tag" ?: string,          // Tag attribute (for IfcElement)
        "attributes" ?: {
            // Special attributes
            "elevation" ?: number // Elevation for IfcBuildingStorey
        },
        "propertySetIds" ?: string[] // Array of property set GUIDs
    }
    */

    json child;

    auto write_to_json = [&](const std::string& keyJson, const std::string& keyIfc) {
        AttributeValue val;
        try {
            val = instance->get(keyIfc);
        } catch (const IfcParse::IfcException&) {
            // simply laziness like no attribute Tag on IfcProject
            return;
        }
        if (!val.isNull()) {
            child[keyJson] = val.apply_visitor(format_value_visitor{});
        }
    };

    write_to_json("id", "GlobalId");
    write_to_json("name", "Name");
    write_to_json("longName", "LongName");
    child["type"] = instance->declaration().name();
    if (parent) {
        if (auto* rt = parent->as<IfcSchema::IfcRoot>()) {
            child["parent"] = rt->GlobalId();
        }
    }
    // @todo groups
    write_to_json("ObjectType", "ObjectType");
    write_to_json("tag", "Tag");
    if (auto* storey = instance->as<IfcSchema::IfcBuildingStorey>()) {
        auto elevation = storey->Elevation();
        if (elevation) {
            child["attributes"] = json::object({{"elevation", *elevation}});
        }
    }

    if (auto* obj = instance->as<IfcSchema::IfcObject>()) {
        IfcSchema::IfcPropertySetDefinition::list::ptr property_sets = get_related<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByProperties, IfcSchema::IfcPropertySetDefinition>(logger, obj, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByProperties::RelatingPropertyDefinition);
        if (!property_sets && property_sets->size()) {
            child["propertySetIds"] = json::array();
            for (IfcSchema::IfcPropertySetDefinition::list::it it = property_sets->begin(); it != property_sets->end(); ++it) {
                IfcSchema::IfcPropertySetDefinition* pset = *it;
                child["propertySetIds"].push_back(pset->GlobalId());
            }
        }
    }

    tree.push_back(child);
}


// A function to be called recursively. Template specialization is used
// to descend into decomposition, containment and property relationships.
template <typename A>
void descend(A* instance, json& tree, Logger& logger, IfcUtil::IfcBaseEntity* parent = nullptr) {
    if (instance->declaration().is(IfcSchema::IfcObjectDefinition::Class())) {
        descend(instance->template as<IfcSchema::IfcObjectDefinition>(), tree, logger, parent);
    } else {
        format_entity_instance(instance, tree, logger);
    }
}

// @todo would be nice to generalize this with the XML version
//
// Descends into the tree by recursing into IfcRelContainedInSpatialStructure,
// IfcRelDecomposes, IfcRelDefinesByType, IfcRelDefinesByProperties relations.
template <>
void descend(IfcSchema::IfcObjectDefinition* product, json& tree, Logger& logger, IfcUtil::IfcBaseEntity* parent) {
    if (product->declaration().is(IfcSchema::IfcElement::Class())) {
        auto voids = product->as<IfcSchema::IfcElement>()->FillsVoids();
        if (voids && voids->size() == 1 && (*voids->begin())->RelatingOpeningElement() != parent) {
            // Fills are placed under their corresponding opening, return early to avoid duplication.
            return;
        }
    }

    format_entity_instance(product, tree, logger, parent);

    if (product->declaration().is(IfcSchema::IfcOpeningElement::Class())) {
        IfcSchema::IfcOpeningElement* opening = product->as<IfcSchema::IfcOpeningElement>();
        IfcSchema::IfcElement::list::ptr fills = get_related<IfcSchema::IfcOpeningElement, IfcSchema::IfcRelFillsElement, IfcSchema::IfcElement>(
            logger, opening, &IfcSchema::IfcOpeningElement::HasFillings, &IfcSchema::IfcRelFillsElement::RelatedBuildingElement);

        for (IfcSchema::IfcElement::list::it it = fills->begin(); it != fills->end(); ++it) {
            descend(*it, tree, logger, product);
        }
    }

    if (product->declaration().is(IfcSchema::IfcSpatialStructureElement::Class())) {
        IfcSchema::IfcSpatialStructureElement* structure = product->as<IfcSchema::IfcSpatialStructureElement>();

        IfcSchema::IfcObjectDefinition::list::ptr elements = get_related<IfcSchema::IfcSpatialStructureElement, IfcSchema::IfcRelContainedInSpatialStructure, IfcSchema::IfcObjectDefinition>(logger, structure, &IfcSchema::IfcSpatialStructureElement::ContainsElements, &IfcSchema::IfcRelContainedInSpatialStructure::RelatedElements);

        for (IfcSchema::IfcObjectDefinition::list::it it = elements->begin(); it != elements->end(); ++it) {
            descend(*it, tree, logger, product);
        }
    }

    if (product->declaration().is(IfcSchema::IfcElement::Class())) {
        IfcSchema::IfcElement* element = static_cast<IfcSchema::IfcElement*>(product);
        IfcSchema::IfcOpeningElement::list::ptr openings = get_related<IfcSchema::IfcElement, IfcSchema::IfcRelVoidsElement, IfcSchema::IfcOpeningElement>(
            logger, element, &IfcSchema::IfcElement::HasOpenings, &IfcSchema::IfcRelVoidsElement::RelatedOpeningElement);

        for (IfcSchema::IfcOpeningElement::list::it it = openings->begin(); it != openings->end(); ++it) {
            descend(*it, tree, logger, product);
        }
    }

#ifdef SCHEMA_IfcRelDecomposes_HAS_RelatedObjects
    IfcSchema::IfcObjectDefinition::list::ptr structures = get_related<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelDecomposes, IfcSchema::IfcObjectDefinition>(logger, product, &IfcSchema::IfcObjectDefinition::IsDecomposedBy, &IfcSchema::IfcRelDecomposes::RelatedObjects);
#else
    IfcSchema::IfcObjectDefinition::list::ptr structures = get_related<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelAggregates, IfcSchema::IfcObjectDefinition>(logger, product, &IfcSchema::IfcObjectDefinition::IsDecomposedBy, &IfcSchema::IfcRelAggregates::RelatedObjects);

    structures->push(get_related<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelNests, IfcSchema::IfcObjectDefinition>(logger, product, &IfcSchema::IfcObjectDefinition::IsNestedBy, &IfcSchema::IfcRelNests::RelatedObjects));
#endif

    for (IfcSchema::IfcObjectDefinition::list::it it = structures->begin(); it != structures->end(); ++it) {
        IfcSchema::IfcObjectDefinition* ob = *it;
        descend(ob, tree, logger, product);
    }

    // psets are handled as part of format_entity_instance()
    // all other relationships are not needed in JSON output
}

IfcSchema::IfcValue* get_value_from_prop(const IfcSchema::IfcProperty* prop) {
    if (auto* psv = prop->as<IfcSchema::IfcPropertySingleValue>()) {
        if (auto* nv = psv->NominalValue()) {
            return nv;
        }
    }
    // @todo other unit typs
    return nullptr;
}

IfcSchema::IfcUnit* get_unit_from_prop(const IfcSchema::IfcProperty* prop) {
    if (auto* psv = prop->as<IfcSchema::IfcPropertySingleValue>()) {
        if (auto* un = psv->Unit()) {
            return un;
        }
    }
    // @todo other unit typs
    return nullptr;
}

} // namespace

void POSTFIX_SCHEMA(JsonSerializer)::finalize() {
    json output;

    IfcSchema::IfcProject::list::ptr projects = file->instances_by_type<IfcSchema::IfcProject>();
    if (projects->size() != 1) {
        logger_.Message(Logger::LOG_ERROR, "SER", 7, "Expected a single IfcProject");
        return;
    }
    IfcSchema::IfcProject* project = *projects->begin();

    auto catch_exceptions = [this](const auto& fn) {
        try {
            return fn();
        } catch (const std::exception& e) {
            logger_.Error("SER", 8, e);
            static std::invoke_result_t<decltype(fn)> v;
            return v;
        }
    };

    output["id"] = catch_exceptions([&]() { return file->header().file_name()->name(); });
    output["projectId"] = catch_exceptions([&]() { return project->GlobalId(); });
    output["author"] = catch_exceptions([&]() { return file->header().file_name()->author().empty() ? "unknown" : file->header().file_name()->author().front(); });
    output["createdAt"] = catch_exceptions([&]() { return file->header().file_name()->time_stamp(); });
    output["schema"] = catch_exceptions([&]() { return file->header().file_schema()->schema_identifiers().front(); }); // without schema we would not be here
    output["creatingApplication"] = catch_exceptions([&]() { return file->header().file_name()->originating_system(); });
    output["properties"] = json::array();
    output["propertySets"] = json::array();
    output["units"] = json::array();
    output["projectUnits"] = json::object();
    output["metaObjects"] = json::array();
    output["groups"] = json::array();

    // Maps for deduplication of properties and quantities
    std::map<const IfcUtil::IfcBaseEntity*, size_t> property_to_index;
    std::unordered_map<json, std::size_t> json_to_index;

    // Obtain sequence of units because properties, quantities reference them by index.
    // IfcUnit is a select of IfcDerivedUnit, IfcMonetaryUnit and IfcNamedUnit.
    // Unfortunately, instances_by_type() does not support select types directly (even though there isn't a real reason for that).
    IfcSchema::IfcUnit::list::ptr units(new IfcSchema::IfcUnit::list);
    units->push(file->instances_by_type<IfcSchema::IfcDerivedUnit>()->as<IfcSchema::IfcUnit>());
    units->push(file->instances_by_type<IfcSchema::IfcMonetaryUnit>()->as<IfcSchema::IfcUnit>());
    units->push(file->instances_by_type<IfcSchema::IfcNamedUnit>()->as<IfcSchema::IfcUnit>());

    auto format_property = [&](const IfcUtil::IfcBaseEntity* prop_) {
        json jprop;
        /*
        {
            "name": "LoadBearing",
            "ifcPropertyType": "IfcPropertySingleValue",
            "ifcValueType": "IfcBoolean",
            "value": "True",
            "valueType": "boolean"
        },
        */
        if (auto* prop = prop_->as<IfcSchema::IfcProperty>()) {
            jprop["name"] = prop->Name();
            jprop["ifcPropertyType"] = prop->declaration().name();
            if (auto* val = get_value_from_prop(prop)) {
                jprop["ifcValueType"] = val->declaration().name();
                jprop["value"] = val->data().get_attribute_value(nullptr, nullptr, 0, 0).apply_visitor(format_value_visitor{});
                jprop["valueType"] = val->data().get_attribute_value(nullptr, nullptr, 0, 0).apply_visitor(get_type_visitor{});
            }
            if (auto* unit = get_unit_from_prop(prop)) {
                jprop["unit"] = std::distance(units->begin(), std::find(units->begin(), units->end(), unit));
            }
        }
        
        return jprop;
    };

    auto format_quantity = [&](const IfcUtil::IfcBaseEntity* qto_) {
        json jprop;
        /*
          {
            "name": "GrossVolume",
            "ifcPropertyType": "IfcQuantityVolume",
            "value": 12.5,
            "valueType": "ElementQuantity",
            "unit": 3
          }       
          */
        if (auto* qto = qto_->as<IfcSchema::IfcPhysicalQuantity>()) {
            jprop["name"] = qto->Name();
            jprop["ifcPropertyType"] = qto->declaration().name();
            if (auto* prop = qto->as<IfcSchema::IfcPhysicalSimpleQuantity>()) {
                jprop["ifcValueType"] = prop->declaration().attributes()[0]->name();
                jprop["value"] = prop->data().get_attribute_value(nullptr, nullptr, 0, 3).apply_visitor(format_value_visitor{});
                jprop["valueType"] = "number";
                if (auto* unit = prop->Unit()) {
                    jprop["unit"] = std::distance(units->begin(), std::find(units->begin(), units->end(), unit));
                }
            }
        }
        return jprop;
    };

    auto deduplicate = [&](auto base_formatter) {
        return [&, base_formatter](const IfcUtil::IfcBaseEntity* prop) mutable -> std::size_t {
            if (auto it = property_to_index.find(prop); it != property_to_index.end()) {
                return it->second;
            }

            // Build JSON for this property
            json j = base_formatter(prop);

            // Check if an identical JSON object is already in the global list
            auto [it2, inserted] = json_to_index.try_emplace(j, output["properties"].size());
            if (inserted) {
                // First time we've seen this JSON -> append to output
                output["properties"].push_back(j);
            }

            std::size_t idx = it2->second;
            property_to_index.emplace(prop, idx); // remember for this pointer too
            return idx;
        };
    };
    auto property_index_for = deduplicate(format_property);
    auto quantity_index_for = deduplicate(format_quantity);

    auto pset_predef_or_qsets = file->instances_by_type<IfcSchema::IfcPropertySetDefinition>();
    for (auto& inst : *pset_predef_or_qsets) {
        std::vector<size_t> property_indices;
        if (auto* pset = inst->as<IfcSchema::IfcPropertySet>()) {
            auto props = pset->HasProperties();
            for (auto& prop : *props) {
                std::size_t index = property_index_for(prop);
                property_indices.push_back(index);
            }
        } else if (auto* qset = inst->as<IfcSchema::IfcElementQuantity>()) {
            auto qtos = qset->Quantities();
            for (auto& qto : *qtos) {
                std::size_t index = quantity_index_for(qto);
                property_indices.push_back(index);
            }
#ifdef SCHEMA_HAS_IfcPreDefinedPropertySet
        // ifc2x3 does not have this type yet, just inherits from IfcPropertySetDefinition
        } else if (auto* pset = inst->as<IfcSchema::IfcPreDefinedPropertySet>()) {
#else
        } else {
#endif
            /*
            // not all_attributes() only the attributes defined on this particular concrete type
            // @todo actually I don't know how to map PreDefinedPropertySet yet
            auto attributes = inst->declaration().attributes();
            for (auto* a : attributes) {
                auto val = inst->get(a->name());
                if (val.isNull()) {
                    continue;
                }
                val.apply_visitor(format_value_visitor{});
            }
            */
        }

        /*
        {
            "id" : "3fG7k$Hj2_9Pxd8vD_xg7",
            "name" : "Pset_WallCommon",
            "type" : "IfcPropertySet",
            "properties" : [ 0, 1, 2 ]
        },
        */
        output["propertySets"].push_back(json::object({{"id", inst->GlobalId()},
                                                       {"name", *inst->Name()}, // @todo optional
                                                       {"type", inst->declaration().name()},
                                                       {"properties", property_indices}}));
    }

    for (auto& unit : *units) {
        /*
        {
          "name": string,                  // Unit symbol/name
          "className": string,             // IFC unit class
          "unitEnum"?: string,             // Unit type enum
          "unitType"?: string,             // Unit type (alternative)
          "prefix"?: string,               // SI prefix (for IfcSIUnit)
          "userDefinedType"?: string,      // User-defined type
          "conversionFactor"?: {           // Conversion factor (for IfcConversionBasedUnit)
            "valueComponent": {
              "value": number,
              "valueType": string,
              "ifcValueType": string
            },
            "unitComponent": number        // Reference to base unit index
          },
          "elements"?: [                   // For IfcDerivedUnit
            {
              "unit": number,              // Reference to unit index
              "exponent": number           // Exponent value
            }
          ],
          "dimensions"?: {                 // IfcDimensionalExponents
            "LengthExponent": number,
            "MassExponent": number,
            "TimeExponent": number,
            "ElectricCurrentExponent": number,
            "ThermodynamicTemperatureExponent": number,
            "AmountOfSubstanceExponent": number,
            "LuminousIntensityExponent": number
          }
        }
        */
        json junit;
        junit["className"] = unit->declaration().name();
        if (auto* siunit = unit->as<IfcSchema::IfcSIUnit>()) {
            // @todo figure out how to encode name for si units
            std::string unit_name = "";
            junit["unitEnum"] = IfcSchema::IfcUnitEnum::ToString(siunit->UnitType());
            if (siunit->Prefix()) {
                junit["prefix"] = IfcSchema::IfcSIPrefix::ToString(*siunit->Prefix());
                unit_name.push_back(IfcSchema::IfcSIPrefix::ToString(*siunit->Prefix())[0]);
            }
            unit_name.push_back(IfcSchema::IfcSIUnitName::ToString(siunit->Name())[0]);
            boost::to_lower(unit_name);
            junit["name"] = unit_name;
        } else if (auto* convunit = unit->as<IfcSchema::IfcConversionBasedUnit>()) {
            junit["name"] = convunit->Name();
            junit["unitEnum"] = IfcSchema::IfcUnitEnum::ToString(convunit->UnitType());
            if (convunit->ConversionFactor()) {
                json jconv;
                auto val = convunit->ConversionFactor()->ValueComponent();
                jconv["valueComponent"] = {
                    {"value", val->data().get_attribute_value(nullptr, nullptr, 0, 0).apply_visitor(format_value_visitor{})},
                    {"valueType", val->data().get_attribute_value(nullptr, nullptr, 0, 0).apply_visitor(get_type_visitor{})}
                };
                jconv["unitComponent"] = std::distance(units->begin(), std::find(units->begin(), units->end(), convunit->ConversionFactor()->UnitComponent()));
                junit["conversionFactor"] = jconv;
            }
        } else if (auto* derunit = unit->as<IfcSchema::IfcDerivedUnit>()) {
#ifdef SCHEMA_IfcDerivedUnit_HAS_Name
            // 4.3 onwards
            if (derunit->Name()) {
                junit["name"] = *derunit->Name();
            }
#endif
            json jelements = json::array();
            auto elements = derunit->Elements();
            for (auto& elem : *elements) {
                jelements.push_back({
                    {"unit", std::distance(units->begin(), std::find(units->begin(), units->end(), elem->Unit()))},
                    {"exponent", elem->Exponent()}
                });
            }
            junit["elements"] = jelements;
        }
        if (auto* namedunit = unit->as<IfcSchema::IfcNamedUnit>()) {
            // support for derived attributes is only available in python
            if (namedunit->as<IfcSchema::IfcSIUnit>() == nullptr) {
                if (auto* dimexp = namedunit->Dimensions()) {
                    junit["dimensions"] = {
                        {"LengthExponent", dimexp->LengthExponent()},
                        {"MassExponent", dimexp->MassExponent()},
                        {"TimeExponent", dimexp->TimeExponent()},
                        {"ElectricCurrentExponent", dimexp->ElectricCurrentExponent()},
                        {"ThermodynamicTemperatureExponent", dimexp->ThermodynamicTemperatureExponent()},
                        {"AmountOfSubstanceExponent", dimexp->AmountOfSubstanceExponent()},
                        {"LuminousIntensityExponent", dimexp->LuminousIntensityExponent()}};
                }
            }
        }
        output["units"].push_back(junit);
    }

    auto project_units = project->UnitsInContext()->Units();
    /*
    {
      "LENGTHUNIT": number,
      "AREAUNIT": number,
      "VOLUMEUNIT": number,
      "PLANEANGLEUNIT": number,
      "MASSUNIT": number,
      "TIMEUNIT": number,
      // ... other unit types
    }*/
    for (auto* pu : *project_units) {
        auto it = std::find(units->begin(), units->end(), pu);
        if (auto* nu = pu->as<IfcSchema::IfcNamedUnit>()) {
            if (it != units->end()) {
                output["projectUnits"][IfcSchema::IfcUnitEnum::ToString(nu->UnitType())] = std::distance(units->begin(), it);
            }
        }
    }

    /*
    // meta objects
    {
      "id": string,                    // Element GUID (IFC GloballyUniqueId)
      "name": string,                  // Element name
      "longName"?: string,             // Long name (for spatial elements)
      "type": string,                  // IFC entity type
      "parent": string | null,         // Parent element GUID (null for root)
      "groups"?: string[],             // Array of group GUIDs
      "ObjectType"?: string,           // ObjectType attribute (for IfcObject)
      "tag"?: string,                  // Tag attribute (for IfcElement)
      "attributes"?: {                 // Special attributes
        "elevation"?: number           // Elevation for IfcBuildingStorey
      },
      "propertySetIds"?: string[]      // Array of property set GUIDs
    }
    */

    descend(project, output["metaObjects"], logger_);

    std::ofstream f(IfcUtil::path::from_utf8(json_filename).c_str());
    f << output.dump(4);
}

    /*

    ptree root, header, units, decomposition, properties, quantities, types, layers, materials, work, calendars, connections, groups;


    // Write the SPF header as XML nodes.
    BOOST_FOREACH (const std::string& s, catch_exceptions([this]() { return file->header().file_description()->description(); })) {
        header.add_child("file_description.description", ptree(s));
    }
    BOOST_FOREACH (const std::string& s, catch_exceptions([this]() { return file->header().file_name()->author(); })) {
        header.add_child("file_name.author", ptree(s));
    }
    BOOST_FOREACH (const std::string& s, catch_exceptions([this]() { return file->header().file_name()->organization(); })) {
        header.add_child("file_name.organization", ptree(s));
    }
    BOOST_FOREACH (const std::string& s, catch_exceptions([this]() { return file->header().file_schema()->schema_identifiers(); })) {
        header.add_child("file_schema.schema_identifiers", ptree(s));
    }
    try {
        header.put("file_description.implementation_level", file->header().file_description()->implementation_level());
    } catch (const IfcParse::IfcException& ex) {
        std::stringstream ss;
        ss << "Failed to get ifc file header file_description implementation_level, error: '" << ex.what() << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }
    try {
        header.put("file_name.name", file->header().file_name()->name());
    } catch (const IfcParse::IfcException& ex) {
        std::stringstream ss;
        ss << "Failed to get ifc file header file_name name, error: '" << ex.what() << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }
    try {
        header.put("file_name.time_stamp", file->header().file_name()->time_stamp());
    } catch (const IfcParse::IfcException& ex) {
        std::stringstream ss;
        ss << "Failed to get ifc file header file_name time_stamp, error: '" << ex.what() << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }
    try {
        header.put("file_name.preprocessor_version", file->header().file_name()->preprocessor_version());
    } catch (const IfcParse::IfcException& ex) {
        std::stringstream ss;
        ss << "Failed to get ifc file header file_name preprocessor_version, error: '" << ex.what() << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }
    try {
        header.put("file_name.originating_system", file->header().file_name()->originating_system());
    } catch (const IfcParse::IfcException& ex) {
        std::stringstream ss;
        ss << "Failed to get ifc file header file_name originating_system, error: '" << ex.what() << "'";
        Logger::Message(Logger::LOG_ERROR, ss.str());
    }
    try {
        // @nb inconsistent spelling
        header.put("file_name.authorization", file->header().file_name()->authorization());
    } catch (const IfcParse::IfcException& ex) {
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

        if (nschedule) {
            IfcSchema::IfcRelAssignsToControl::list::ptr controls = schedule->Controls();
            for (IfcSchema::IfcRelAssignsToControl::list::it it2 = controls->begin(); it2 != controls->end(); ++it2) {
                IfcSchema::IfcRelAssignsToControl* control = *it2;

                IfcSchema::IfcObjectDefinition::list::ptr objects = control->RelatedObjects();
                for (IfcSchema::IfcObjectDefinition::list::it it3 = objects->begin(); it3 != objects->end(); ++it3) {
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
            for (auto it2 = decomposed_by->begin(); it2 != decomposed_by->end(); ++it2) {
                IfcSchema::IfcObjectDefinition::list::ptr related_objects = (*it2)->RelatedObjects();
                for (IfcSchema::IfcObjectDefinition::list::it it3 = related_objects->begin(); it3 != related_objects->end(); ++it3) {
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
                for (IfcSchema::IfcWorkTime::list::it it2 = working_times->begin(); it2 != working_times->end(); ++it2) {
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

        format_entity_instance(mapping_, connection->RelatedElement(), nrelatedElement, true);
        format_entity_instance(mapping_, connection->RelatingElement(), nrelatingElement, true);

        nconnection->add_child("RelatedElement", nrelatedElement);
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

    root.add_child("ifc.header", header);
    root.add_child("ifc.units", units);
    root.add_child("ifc.connections", connections);
    root.add_child("ifc.properties", properties);
    root.add_child("ifc.quantities", quantities);
    root.add_child("ifc.work", work);
    root.add_child("ifc.calendars", calendars);
    root.add_child("ifc.types", types);
    root.add_child("ifc.layers", layers);
    root.add_child("ifc.groups", groups);
    root.add_child("ifc.materials", materials);
    root.add_child("ifc.decomposition", decomposition);

    root.put("ifc.<xmlattr>.xmlns:xlink", "http://www.w3.org/1999/xlink");

#if BOOST_VERSION >= 105600
    boost::property_tree::xml_writer_settings<ptree::key_type> settings = boost::property_tree::xml_writer_make_settings<ptree::key_type>('\t', 1);
#else
    boost::property_tree::xml_writer_settings<char> settings('\t', 1);
#endif

    std::ofstream f(IfcUtil::path::from_utf8(xml_filename).c_str());
    boost::property_tree::write_xml(f, root, settings);
    */

#endif
