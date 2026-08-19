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

#include "ifcparse/macros.h"

#ifndef IfcSchema
#define IfcSchema Ifc2x3
#endif

#include "ifcparse/file.h"
#include "ifcparse/logger.h"
#include "plugin/plugin.h"

#include INCLUDE_SCHEMA(ifcparse/schemas, IfcSchema)
#include INCLUDE_SCHEMA_DEFINITIONS(ifcparse/schemas, IfcSchema)

#ifdef _MSC_VER
#define strcasecmp _stricmp
#endif

#include <iomanip>

#if USE_VLD
#include <vld.h>
#endif

template<class T, class = void>
struct is_ifc4_or_higher : std::false_type {};

template<class T>
struct is_ifc4_or_higher<T, std::void_t<decltype(T::IfcMaterialDefinition)>> : std::true_type { };

typedef std::map<std::string, std::map<std::string, std::string>> element_properties;

std::string string_value(const std::string& value) {
	return value;
}

std::string string_value(const std::optional<std::string>& value) {
	return value.value_or("");
}

bool has_string(const std::string& value) {
	return !value.empty();
}

bool has_string(const std::optional<std::string>& value) {
	return value.has_value();
}

#ifdef SCHEMA_HAS_IfcBuildingElement
typedef IfcSchema::IfcBuildingElement element_t;
#else
typedef IfcSchema::IfcBuiltElement element_t;
#endif

std::string format_string(const ifcopenshell::attribute_value& argument) {
	// Argument is a runtime tagged variant for the various data types in a IFC model,
	// in this particular case we only care about flattening it to a string.
	// @todo mostly duplicated from xml_serializer.cpp
	if (argument.isNull()) {
		return "-";
	}
	auto argument_type = argument.type();
	switch (argument_type) {
	case ifcopenshell::Argument_BOOL: {
		const bool b = argument;
		return b ? "true" : "false";
	}
	case ifcopenshell::Argument_DOUBLE: {
		const double d = argument;
		std::stringstream stream;
		stream << std::setprecision(std::numeric_limits< double >::max_digits10) << d;
		return stream.str();
		break; }
	case ifcopenshell::Argument_STRING:
	case ifcopenshell::Argument_ENUMERATION: {
		return static_cast<std::string>(argument);
		break; }
	case ifcopenshell::Argument_INT: {
		const int v = argument;
		std::stringstream stream;
		stream << v;
		return stream.str();
		break; }
	}
	return "?";
}

template <typename Schema, typename T>
void process_pset(element_properties& props, const T& inst) {
	// Process an individual Property or Quantity set.
	if (auto pset = inst.template as<typename Schema::IfcPropertySet>()) {
		auto pset_name = pset.Name();
		if (!has_string(pset_name)) {
			return;
		}
		auto ps = pset.HasProperties();
		for (const auto& p : ps) {
			if (auto singleval = p.template as<typename Schema::IfcPropertySingleValue>()) {
				std::string propname, propvalue;
				auto property_name = singleval.Name();
				if (!has_string(property_name)) {
					continue;
				}
				propname = string_value(property_name);
				auto nominal_value = singleval.NominalValue();
				if (!nominal_value) {
					propvalue = "-";
				} else {
					props[string_value(pset_name)][propname] = format_string(nominal_value.get_attribute_value(0));
				}
			}
		}
	}
	if (auto qset = inst.template as<typename Schema::IfcElementQuantity>()) {
		auto qset_name = qset.Name();
		if (!has_string(qset_name)) {
			return;
		}
		auto qs = qset.Quantities();
		for (const auto& q : qs) {
			if (q.template as<typename Schema::IfcPhysicalSimpleQuantity>() && q.get_attribute_value(3).type() == ifcopenshell::Argument_DOUBLE) {
				double v = q.get_attribute_value(3);
				props[string_value(qset_name)][string_value(q.Name())] = std::to_string(v);
			}
		}
	}
	if constexpr (is_ifc4_or_higher<Schema>::value) {
		if (auto extprops = inst.template as<typename Schema::IfcExtendedProperties>()) {
			// @todo
		}
	}
}

template <typename Schema>
void get_psets_s(element_properties& props, const typename Schema::IfcObjectDefinition& inst) {
	// Extracts the property definitions for an IFC instance.
	if (auto tyob = inst.template as<typename Schema::IfcTypeObject>()) {
		if (tyob.HasPropertySets()) {
			auto defs = *tyob.HasPropertySets();
			for (const auto& def : defs) {
				process_pset<Schema>(props, def);
			}
		}
	}
	if constexpr (is_ifc4_or_higher<Schema>::value) {
		if (auto mdef = inst.template as<typename Schema::IfcMaterialDefinition>()) {
			auto defs = mdef.HasProperties();
			for (const auto& def : defs) {
				process_pset<Schema>(props, def);
			}
		}
		if (auto pdef = inst.template as<typename Schema::IfcProfileDef>()) {
			auto defs = pdef.HasProperties();
			for (const auto& def : defs) {
				process_pset<Schema>(props, def);
			}
		}
	}
	if (auto ob = inst.template as<typename Schema::IfcObject>()) {
		if constexpr (is_ifc4_or_higher<Schema>::value) {
			auto rels = ob.IsTypedBy();
			for (const auto& rel : rels) {
				get_psets_s<Schema>(props, rel.RelatingType());
			}
		}
		{
			auto rels = ob.IsDefinedBy();
			for (const auto& rel : rels) {
				if (auto bytype = rel.template as<typename Schema::IfcRelDefinesByType>()) {
					get_psets_s<Schema>(props, bytype.RelatingType());
				} else if (auto byprops = rel.template as<typename Schema::IfcRelDefinesByProperties>()) {
					process_pset<Schema>(props, byprops.RelatingPropertyDefinition());
				}
			}
		}
	}
}

element_properties get_psets(const express::base& inst) {
	element_properties props;
	if (auto object_definition = inst.as<IfcSchema::IfcObjectDefinition>()) {
		get_psets_s<IfcSchema>(props, object_definition);
	}
	return props;
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cout << "usage: IfcParseExamples <filename.ifc>" << std::endl;
        return 1;
    }

#ifdef IFCOPENSHELL_EXAMPLE_PLUGIN_PATH
	ifcopenshell::plugin::set_search_paths({IFCOPENSHELL_EXAMPLE_PLUGIN_PATH});
#endif

    // Redirect the output (both progress and log) to stdout
    ifcopenshell::logger::root().set_output(&std::cout, &std::cout);

    // Parse the IFC file provided in argv[1]
    ifcopenshell::file file(argv[1]);
    if (!file.good()) {
        std::cout << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // Lets get a list of IfcBuildingElements, this is the parent
    // type of things like walls, windows and doors.
    // entitiesByType is a templated function and returns a
    // templated class that behaves like a std::vector.
    // Note that the return types are all typedef'ed as members of
    // the generated classes, ::list for the templated vector class,
    // ::ptr for a shared pointer and ::it for an iterator.
    // We will simply iterate over the vector and print a string
    // representation of the entity to stdout.
    //
    // Secondly, lets find out which of them are IfcWindows.
    // In order to access the additional properties that windows
    // have on top af the properties of building elements,
    // we need to cast them to IfcWindows. Since these properties
    // are optional we need to make sure the properties are
    // defined for the window in question before accessing them.
    auto elements = file.instances_by_type<element_t>();

    std::cout << "Found " << elements.size() << " elements in " << argv[1] << ":" << std::endl;

    for (auto& element : elements) {
        element.to_string(std::cout);
        std::cout << std::endl;

        if (auto window = element.as<IfcSchema::IfcWindow>()) {
            if (window.OverallWidth() && window.OverallHeight()) {
                const double area = *window.OverallWidth() * *window.OverallHeight();
                std::cout << "The area of this window is " << area << std::endl;
            }
        }

        element_properties props = get_psets(element);

        for (auto& ps : props) {
            std::cout << ps.first << std::endl;
            std::cout << std::string(ps.first.size(), '=') << std::endl;
            size_t max_key_len = 0;
            for (auto& p : ps.second) {
                if (p.first.size() > max_key_len) {
                    max_key_len = p.first.size();
                }
            }
            for (auto& p : ps.second) {
                std::cout << p.first << std::string(max_key_len - p.first.size(), ' ') << ":" << p.second << std::endl;
            }
            std::cout << std::endl;
        }
    }
}
