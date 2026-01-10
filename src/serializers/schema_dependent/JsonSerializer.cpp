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
		JsonSerializer* operator()(IfcParse::IfcFile* file, const std::string& json_filename, JsonSerializer::Dialect dialect) const {
            POSTFIX_SCHEMA(JsonSerializer)* s = new POSTFIX_SCHEMA(JsonSerializer)(file, json_filename, dialect);
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
        if constexpr (std::is_same_v<std::decay_t<T>, Derived> || std::is_same_v<std::decay_t<T>, boost::dynamic_bitset<>> || std::is_same_v<std::decay_t<T>, express::Base> || std::is_same_v<std::decay_t<T>, std::vector<int>> || std::is_same_v<std::decay_t<T>, std::vector<double>> || std::is_same_v<std::decay_t<T>, std::vector<std::string>> || std::is_same_v<std::decay_t<T>, std::vector<boost::dynamic_bitset<>>> || std::is_same_v<std::decay_t<T>, std::vector<express::Base>> || std::is_same_v<std::decay_t<T>, std::vector<std::vector<express::Base>>> || std::is_same_v<std::decay_t<T>, std::vector<std::vector<int>>> || std::is_same_v<std::decay_t<T>, std::vector<std::vector<double>>> || std::is_same_v<std::decay_t<T>, empty_aggregate_t> || std::is_same_v<std::decay_t<T>, empty_aggregate_of_aggregate_t> || std::is_same_v<std::decay_t<T>, Blank>) {
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
auto get_related(T t, F f, G g) {
    auto li = (t.*f)();
    std::vector<V> acc;
    for (auto& u : li) {
        try {
            auto vs = (u.template as<U>().*g)();
            if constexpr (std::is_base_of_v<express::Base, decltype(vs)>) {
                if (auto vv = vs.template as<V>()) {
                    acc.push_back(vv);
                }
            } else if constexpr (std::is_base_of_v<express::Select, decltype(vs)>) {
                if (auto vv = vs.concrete().template as<V>()) {
                    acc.push_back(vv);
                }
            } else {
                for (auto& v : vs) {
                    if (auto vv = v.template as<V>()) {
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

void format_entity_instance(express::Base instance, json& tree, express::Base parent = express::Base()) {
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
            val = instance.as<express::Entity>().get(keyIfc);
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
    child["type"] = instance.declaration().name();
    if (parent) {
        if (auto rt = parent.as<IfcSchema::IfcRoot>()) {
            child["parent"] = rt.GlobalId();
        }
    }
    // @todo groups
    write_to_json("ObjectType", "ObjectType");
    write_to_json("tag", "Tag");
    if (auto storey = instance.as<IfcSchema::IfcBuildingStorey>()) {
        auto elevation = storey.Elevation();
        if (elevation) {
            child["attributes"] = json::object({{"elevation", *elevation}});
        }
    }

    if (auto obj = instance.as<IfcSchema::IfcObject>()) {
        auto property_sets = get_related<IfcSchema::IfcObject, IfcSchema::IfcRelDefinesByProperties, IfcSchema::IfcPropertySetDefinition>(obj, &IfcSchema::IfcObject::IsDefinedBy, &IfcSchema::IfcRelDefinesByProperties::RelatingPropertyDefinition);
        if (!property_sets.empty()) {
            child["propertySetIds"] = json::array();
            for (auto& pset : property_sets) {
                child["propertySetIds"].push_back(pset.GlobalId());
            }
        }
    }

    tree.push_back(child);
}


// A function to be called recursively. Template specialization is used
// to descend into decomposition, containment and property relationships.
template <typename A>
void descend(A instance, json& tree, express::Base parent = express::Base()) {
    if (instance.declaration().is(IfcSchema::IfcObjectDefinition::Class())) {
        descend(instance.template as<IfcSchema::IfcObjectDefinition>(), tree, parent);
    } else {
        format_entity_instance(instance, tree);
    }
}

// @todo would be nice to generalize this with the XML version
//
// Descends into the tree by recursing into IfcRelContainedInSpatialStructure,
// IfcRelDecomposes, IfcRelDefinesByType, IfcRelDefinesByProperties relations.
template <>
void descend(IfcSchema::IfcObjectDefinition product, json& tree, express::Base parent) {
    if (product.declaration().is(IfcSchema::IfcElement::Class())) {
        auto voids = product.as<IfcSchema::IfcElement>().FillsVoids();
        if (voids.size() == 1 && voids.front().RelatingOpeningElement() != parent) {
            // Fills are placed under their corresponding opening, return early to avoid duplication.
            return;
        }
    }

    format_entity_instance(product, tree, parent);

    if (auto opening = product.as<IfcSchema::IfcOpeningElement>()) {
        auto fills = get_related<IfcSchema::IfcOpeningElement, IfcSchema::IfcRelFillsElement, IfcSchema::IfcElement>(
            opening, &IfcSchema::IfcOpeningElement::HasFillings, &IfcSchema::IfcRelFillsElement::RelatedBuildingElement);

        for (auto& f : fills) {
            descend(f, tree, product);
        }
    }

    if (auto structure = product.as<IfcSchema::IfcSpatialStructureElement>()) {
        auto elements = get_related<IfcSchema::IfcSpatialStructureElement, IfcSchema::IfcRelContainedInSpatialStructure, IfcSchema::IfcObjectDefinition>(structure, &IfcSchema::IfcSpatialStructureElement::ContainsElements, &IfcSchema::IfcRelContainedInSpatialStructure::RelatedElements);

        for (auto& el : elements) {
            descend(el, tree, product);
        }
    }

    if (auto element = product.as<IfcSchema::IfcElement>()) {
        auto openings = get_related<IfcSchema::IfcElement, IfcSchema::IfcRelVoidsElement, IfcSchema::IfcOpeningElement>(
            element, &IfcSchema::IfcElement::HasOpenings, &IfcSchema::IfcRelVoidsElement::RelatedOpeningElement);

        for (auto& op : openings) {
            descend(op, tree, product);
        }
    }

#ifdef SCHEMA_IfcRelDecomposes_HAS_RelatedObjects
    auto structures = get_related<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelDecomposes, IfcSchema::IfcObjectDefinition>(product, &IfcSchema::IfcObjectDefinition::IsDecomposedBy, &IfcSchema::IfcRelDecomposes::RelatedObjects);
#else
    auto structures = get_related<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelAggregates, IfcSchema::IfcObjectDefinition>(product, &IfcSchema::IfcObjectDefinition::IsDecomposedBy, &IfcSchema::IfcRelAggregates::RelatedObjects);

    auto nested = get_related<IfcSchema::IfcObjectDefinition, IfcSchema::IfcRelNests, IfcSchema::IfcObjectDefinition>(product, &IfcSchema::IfcObjectDefinition::IsNestedBy, &IfcSchema::IfcRelNests::RelatedObjects);

    structures.insert(structures.end(), nested.begin(), nested.end());
#endif

    for (auto& ob : structures) {
        descend(ob, tree, product);
    }

    // psets are handled as part of format_entity_instance()
    // all other relationships are not needed in JSON output
}

IfcSchema::IfcValue get_value_from_prop(IfcSchema::IfcProperty& prop) {
    if (auto psv = prop.as<IfcSchema::IfcPropertySingleValue>()) {
        if (auto nv = psv.NominalValue()) {
            return nv;
        }
    }
    // @todo other unit types
    return IfcSchema::IfcValue{};
}

IfcSchema::IfcUnit get_unit_from_prop(IfcSchema::IfcProperty& prop) {
    if (auto psv = prop.as<IfcSchema::IfcPropertySingleValue>()) {
        if (auto un = psv.Unit()) {
            return un;
        }
    }
    // @todo other unit types
    return IfcSchema::IfcUnit{};
}

} // namespace

void POSTFIX_SCHEMA(JsonSerializer)::finalize() {
    json output;

    auto projects = file->instances_by_type<IfcSchema::IfcProject>();
    if (projects.size() != 1) {
        Logger::Message(Logger::LOG_ERROR, "Expected a single IfcProject");
        return;
    }
    IfcSchema::IfcProject project = projects.front();

    auto catch_exceptions = [this](const auto& fn) {
        try {
            return fn();
        } catch (const std::exception& e) {
            Logger::Error(e);
            static std::invoke_result_t<decltype(fn)> v;
            return v;
        }
    };

    output["id"] = catch_exceptions([&]() { return file->header().file_name().name(); });
    output["projectId"] = catch_exceptions([&]() { return project.GlobalId(); });
    output["author"] = catch_exceptions([&]() { return file->header().file_name().author().empty() ? "unknown" : file->header().file_name().author().front(); });
    output["createdAt"] = catch_exceptions([&]() { return file->header().file_name().time_stamp(); });
    output["schema"] = catch_exceptions([&]() { return file->header().file_schema().schema_identifiers().front(); }); // without schema we would not be here
    output["creatingApplication"] = catch_exceptions([&]() { return file->header().file_name().originating_system(); });
    output["properties"] = json::array();
    output["propertySets"] = json::array();
    output["units"] = json::array();
    output["projectUnits"] = json::object();
    output["metaObjects"] = json::array();
    output["groups"] = json::array();

    // Maps for deduplication of properties and quantities
    std::map<express::Entity, size_t> property_to_index;
    std::unordered_map<json, std::size_t> json_to_index;

    // Obtain sequence of units because properties, quantities reference them by index.
    // IfcUnit is a select of IfcDerivedUnit, IfcMonetaryUnit and IfcNamedUnit.
    // Unfortunately, instances_by_type() does not support select types directly (even though there isn't a real reason for that).
    std::vector<IfcSchema::IfcUnit> units;
    {
        auto vs = file->instances_by_type<IfcSchema::IfcDerivedUnit>();
        for (auto& v : vs) {
            units.push_back(v);
        }
    }
    {
        auto vs = file->instances_by_type<IfcSchema::IfcMonetaryUnit>();
        for (auto& v : vs) {
            units.push_back(v);
        }
    }
    {
        auto vs = file->instances_by_type<IfcSchema::IfcNamedUnit>();
        for (auto& v : vs) {
            units.push_back(v);
        }
    }

    auto format_property = [&](const express::Entity& prop_) {
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
        if (auto prop = prop_.as<IfcSchema::IfcProperty>()) {
            jprop["name"] = prop.Name();
            jprop["ifcPropertyType"] = prop.declaration().name();
            if (auto val = get_value_from_prop(prop)) {
                jprop["ifcValueType"] = val.concrete().declaration().name();
                jprop["value"] = val.concrete().get_attribute_value(0).apply_visitor(format_value_visitor{});
                jprop["valueType"] = val.concrete().get_attribute_value(0).apply_visitor(get_type_visitor{});
            }
            if (auto unit = get_unit_from_prop(prop)) {
                jprop["unit"] = std::distance(units.begin(), std::find(units.begin(), units.end(), unit));
            }
        }
        
        return jprop;
    };

    auto format_quantity = [&](const express::Entity& qto_) {
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
        if (auto qto = qto_.as<IfcSchema::IfcPhysicalQuantity>()) {
            jprop["name"] = qto.Name();
            jprop["ifcPropertyType"] = qto.declaration().name();
            if (auto prop = qto.as<IfcSchema::IfcPhysicalSimpleQuantity>()) {
                jprop["ifcValueType"] = prop.declaration().as_entity()->attributes()[0]->name();
                jprop["value"] = prop.get_attribute_value(3).apply_visitor(format_value_visitor{});
                jprop["valueType"] = "number";
                if (auto unit = prop.Unit()) {
                    jprop["unit"] = std::distance(units.begin(), std::find(units.begin(), units.end(), unit));
                }
            }
        }
        return jprop;
    };

    auto deduplicate = [&](auto base_formatter) {
        return [&, base_formatter](const express::Entity& prop) mutable -> std::size_t {
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
    for (auto& inst : pset_predef_or_qsets) {
        std::vector<size_t> property_indices;
        if (auto pset = inst.as<IfcSchema::IfcPropertySet>()) {
            auto props = pset.HasProperties();
            for (auto& prop : props) {
                std::size_t index = property_index_for(prop);
                property_indices.push_back(index);
            }
        } else if (auto qset = inst.as<IfcSchema::IfcElementQuantity>()) {
            auto qtos = qset.Quantities();
            for (auto& qto : qtos) {
                std::size_t index = quantity_index_for(qto);
                property_indices.push_back(index);
            }
#ifdef SCHEMA_HAS_IfcPreDefinedPropertySet
        // ifc2x3 does not have this type yet, just inherits from IfcPropertySetDefinition
        } else if (auto pset = inst.as<IfcSchema::IfcPreDefinedPropertySet>()) {
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
        output["propertySets"].push_back(json::object({{"id", inst.GlobalId()},
                                                       {"name", *inst.Name()}, // @todo optional
                                                       {"type", inst.declaration().name()},
                                                       {"properties", property_indices}}));
    }

    for (auto& unit : units) {
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
        junit["className"] = unit.concrete().declaration().name();
        if (auto siunit = unit.concrete().as<IfcSchema::IfcSIUnit>()) {
            // @todo figure out how to encode name for si units
            std::string unit_name = "";
            junit["unitEnum"] = IfcSchema::IfcUnitEnum::ToString(siunit.UnitType());
            if (siunit.Prefix()) {
                junit["prefix"] = IfcSchema::IfcSIPrefix::ToString(*siunit.Prefix());
                unit_name.push_back(IfcSchema::IfcSIPrefix::ToString(*siunit.Prefix())[0]);
            }
            unit_name.push_back(IfcSchema::IfcSIUnitName::ToString(siunit.Name())[0]);
            boost::to_lower(unit_name);
            junit["name"] = unit_name;
        } else if (auto convunit = unit.concrete().as<IfcSchema::IfcConversionBasedUnit>()) {
            junit["name"] = convunit.Name();
            junit["unitEnum"] = IfcSchema::IfcUnitEnum::ToString(convunit.UnitType());
            if (convunit.ConversionFactor()) {
                json jconv;
                auto val = convunit.ConversionFactor().ValueComponent();
                jconv["valueComponent"] = {
                    {"value", val.concrete().get_attribute_value(0).apply_visitor(format_value_visitor{})},
                    {"valueType", val.concrete().get_attribute_value(0).apply_visitor(get_type_visitor{})}
                };
                jconv["unitComponent"] = std::distance(units.begin(), std::find(units.begin(), units.end(), convunit.ConversionFactor().UnitComponent()));
                junit["conversionFactor"] = jconv;
            }
        } else if (auto derunit = unit.concrete().as<IfcSchema::IfcDerivedUnit>()) {
#ifdef SCHEMA_IfcDerivedUnit_HAS_Name
            // 4.3 onwards
            if (derunit.Name()) {
                junit["name"] = *derunit.Name();
            }
#endif
            json jelements = json::array();
            auto elements = derunit.Elements();
            for (auto& elem : elements) {
                jelements.push_back({
                    {"unit", std::distance(units.begin(), std::find(units.begin(), units.end(), elem.Unit()))},
                    {"exponent", elem.Exponent()}
                });
            }
            junit["elements"] = jelements;
        }
        if (auto namedunit = unit.concrete().as<IfcSchema::IfcNamedUnit>()) {
            // support for derived attributes is only available in python
            if (!namedunit.as<IfcSchema::IfcSIUnit>()) {
                if (auto dimexp = namedunit.Dimensions()) {
                    junit["dimensions"] = {
                        {"LengthExponent", dimexp.LengthExponent()},
                        {"MassExponent", dimexp.MassExponent()},
                        {"TimeExponent", dimexp.TimeExponent()},
                        {"ElectricCurrentExponent", dimexp.ElectricCurrentExponent()},
                        {"ThermodynamicTemperatureExponent", dimexp.ThermodynamicTemperatureExponent()},
                        {"AmountOfSubstanceExponent", dimexp.AmountOfSubstanceExponent()},
                        {"LuminousIntensityExponent", dimexp.LuminousIntensityExponent()}};
                }
            }
        }
        output["units"].push_back(junit);
    }

    auto project_units = project.UnitsInContext().Units();
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
    for (auto pu : project_units) {
        auto it = std::find(units.begin(), units.end(), pu);
        if (auto nu = pu.as<IfcSchema::IfcNamedUnit>()) {
            if (it != units.end()) {
                output["projectUnits"][IfcSchema::IfcUnitEnum::ToString(nu.UnitType())] = std::distance(units.begin(), it);
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

    descend(project, output["metaObjects"]);

    std::ofstream f(IfcUtil::path::from_utf8(json_filename).c_str());
    f << output.dump(4);
}

#endif