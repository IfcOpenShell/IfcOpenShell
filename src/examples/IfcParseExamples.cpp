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

// TODO: Multiple schemas
#define IfcSchema Ifc2x3

#include "../ifcparse/IfcFile.h"
#include "../ifcparse/IfcLogger.h"
#include "../ifcparse/Ifc2x3.h"

#include <boost/preprocessor/stringize.hpp>
#include <boost/preprocessor/seq/for_each.hpp>
#include <boost/preprocessor/seq/size.hpp>
#include <boost/preprocessor/seq/pop_back.hpp>
#include <boost/preprocessor/comparison/greater.hpp> 
#include <boost/preprocessor/selection/min.hpp>

#ifdef _MSC_VER 
#define strcasecmp _stricmp
#endif

#ifndef SCHEMA_SEQ
static_assert(false, "A boost preprocessor sequence of schema identifiers is needed for this file to compile.");
#endif

// @todo duplicated with Kernel.h

// @tfk A macro cannot define an include (I think), so here we can't
// loop over the sequence of schema identifiers, but rather we have
// unroll the loop with at least the amount of schemas we'd like support
// for and then overflow into an existing empty include file.

#define INCLUDE_SCHEMA(n) \
	BOOST_PP_IIF(BOOST_PP_GREATER(BOOST_PP_SEQ_SIZE(SCHEMA_SEQ), n), BOOST_PP_STRINGIZE(../ifcparse/BOOST_PP_CAT(Ifc,BOOST_PP_SEQ_ELEM(BOOST_PP_MIN(n, BOOST_PP_SEQ_SIZE(BOOST_PP_SEQ_POP_BACK(SCHEMA_SEQ))),SCHEMA_SEQ)).h), "../ifcgeom/empty.h")

#include INCLUDE_SCHEMA(0)
#include INCLUDE_SCHEMA(1)
#include INCLUDE_SCHEMA(2)
#include INCLUDE_SCHEMA(3)
#include INCLUDE_SCHEMA(4)
#include INCLUDE_SCHEMA(5)
#include INCLUDE_SCHEMA(6)
#include INCLUDE_SCHEMA(7)
#include INCLUDE_SCHEMA(8)
#include INCLUDE_SCHEMA(9)
#include INCLUDE_SCHEMA(10)
#include INCLUDE_SCHEMA(11)
#include INCLUDE_SCHEMA(12)
#include INCLUDE_SCHEMA(13)
#include INCLUDE_SCHEMA(14)
#include INCLUDE_SCHEMA(15)

#include <iomanip>

#if USE_VLD
#include <vld.h>
#endif

template<class T, class = void>
struct is_ifc4_or_higher : std::false_type {};

template<class T>
struct is_ifc4_or_higher<T, std::void_t<decltype(T::IfcMaterialDefinition)>> : std::true_type { };

typedef std::map<std::string, std::map<std::string, std::string>> element_properties;

std::string format_string(const AttributeValue& argument) {
	// Argument is a runtime tagged variant for the various data types in a IFC model,
	// in this particular case we only care about flattening it to a string.
	// @todo mostly duplicated from XmlSerializer.cpp
	if (argument.isNull()) {
		return "-";
	}
	auto argument_type = argument.type();
	switch (argument_type) {
	case IfcUtil::Argument_BOOL: {
		const bool b = argument;
		return b ? "true" : "false";
	}
	case IfcUtil::Argument_DOUBLE: {
		const double d = argument;
		std::stringstream stream;
		stream << std::setprecision(std::numeric_limits< double >::max_digits10) << d;
		return stream.str();
		break; }
	case IfcUtil::Argument_STRING:
	case IfcUtil::Argument_ENUMERATION: {
		return static_cast<std::string>(argument);
		break; }
	case IfcUtil::Argument_INT: {
		const int v = argument;
		std::stringstream stream;
		stream << v;
		return stream.str();
		break; }
	}
	return "?";
}

template <typename Schema, typename T>
void process_pset(element_properties& props, const T* inst) {
	// Process an individual Property or Quantity set.
	if (auto pset = inst->template as<typename Schema::IfcPropertySet>()) {
		if (!pset->Name()) {
			return;
		}
		auto ps = pset->HasProperties();
		for (auto it = ps->begin(); it != ps->end(); ++it) {
			auto& p = *it;
			if (auto singleval = p->template as<typename Schema::IfcPropertySingleValue>()) {
				std::string propname, propvalue;
				if constexpr (is_ifc4_or_higher<Schema>::value) {
					if (!singleval->Name()) {
						continue;
					}
					propname = *singleval->Name();
				}
				if constexpr (!is_ifc4_or_higher<Schema>::value) {
					propname = singleval->Name();
				}
				if (!singleval->NominalValue()) {
					propvalue = "-";
				} else {
					props[*pset->Name()][propname] = format_string(singleval->NominalValue()->template as<IfcUtil::IfcBaseClass>()->data().get_attribute_value(0));
				}
			}
		}
	}
	if (auto qset = inst->template as<typename Schema::IfcElementQuantity>()) {
		if (!qset->Name()) {
			return;
		}
		auto qs = qset->Quantities();
		for (auto it = qs->begin(); it != qs->end(); ++it) {
			auto& q = *it;
			if (q->template as<typename Schema::IfcPhysicalSimpleQuantity>() && q->data().get_attribute_value(3).type() == IfcUtil::Argument_DOUBLE) {
				double v = q->data().get_attribute_value(3);
				props[*qset->Name()][q->Name()] = std::to_string(v);
			}
		}
	}
	if constexpr (is_ifc4_or_higher<Schema>::value) {
		if (auto extprops = inst->template as<typename Schema::IfcExtendedProperties>()) {
			// @todo
		}
	}
}

template <typename Schema>
void get_psets_s(element_properties& props, const typename Schema::IfcObjectDefinition* inst) {
	// Extracts the property definitions for an IFC instance. 
	if (auto tyob = inst->template as<typename Schema::IfcTypeObject>()) {
		if (tyob->HasPropertySets()) {
			auto defs = *tyob->HasPropertySets();
			for (auto it = defs->begin(); it != defs->end(); ++it) {
				auto& def = *it;
				process_pset<Schema>(props, def);
			}
		}
	}
	if constexpr (is_ifc4_or_higher<Schema>::value) {
		if (auto mdef = inst->template as<typename Schema::IfcMaterialDefinition>()) {
			auto defs = mdef->HasProperties();
			for (auto it = defs->begin(); it != defs->end(); ++it) {
				auto& def = *it;
				process_pset<Schema>(props, def);
			}
		}
		if (auto pdef = inst->template as<typename Schema::IfcProfileDef>()) {
			auto defs = pdef->HasProperties();
			for (auto it = defs->begin(); it != defs->end(); ++it) {
				auto& def = *it;
				process_pset<Schema>(props, def);
			}
		}
	}
	if (auto ob = inst->template as<typename Schema::IfcObject>()) {
		if constexpr (is_ifc4_or_higher<Schema>::value) {
			auto rels = ob->IsTypedBy();
			for (auto it = rels->begin(); it != rels->end(); ++it) {
				auto& rel = *it;
				get_psets_s<Schema>(props, rel->RelatingType());
			}
		}
		{
			auto rels = ob->IsDefinedBy();
			for (auto it = rels->begin(); it != rels->end(); ++it) {
				auto& rel = *it;
				if (auto bytype = rel->template as<typename Schema::IfcRelDefinesByType>()) {
					get_psets_s<Schema>(props, bytype->RelatingType());
				} else if (auto byprops = rel->template as<typename Schema::IfcRelDefinesByProperties>()) {
					process_pset<Schema>(props, byprops->RelatingPropertyDefinition());
				}
			}
		}
	}
}

// What follows is machinery to create a preprocessor-based dispatch mechanism to dispatch to the
// correct get_psets_s<Schema>() based on inst->declaration().schema()->name().

#define EXPAND_AND_CONCATENATE(elem) Ifc##elem

#define GENERATE_LITERAL_STRING(elem) "Ifc" # elem

#define TEST_AND_DISPATCH(r, data, elem) \
	if (strcasecmp(schema_name, GENERATE_LITERAL_STRING(elem)) == 0) { get_psets_s<EXPAND_AND_CONCATENATE(elem)>(props, inst->as<EXPAND_AND_CONCATENATE(elem)::IfcObjectDefinition>()); }

void get_psets(element_properties& props, const IfcUtil::IfcBaseClass* inst) {
	auto schema_name = inst->declaration().schema()->name().c_str();
	BOOST_PP_SEQ_FOR_EACH(TEST_AND_DISPATCH, , SCHEMA_SEQ)
}

int main(int argc, char** argv) {
	if (argc != 2) {
        std::cout << "usage: IfcParseExamples <filename.ifc>" << std::endl;
        return 1;
    }
    
    // Redirect the output (both progress and log) to stdout
    Logger::SetOutput(&std::cout, &std::cout);

    // Parse the IFC file provided in argv[1]
    IfcParse::IfcFile file(argv[1]);
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
	IfcSchema::IfcBuildingElement::list::ptr elements = file.instances_by_type<IfcSchema::IfcBuildingElement>();

    std::cout << "Found " << elements->size() << " elements in " << argv[1] << ":" << std::endl;

    for (auto it = elements->begin(); it != elements->end(); ++it) {
        const auto* element = *it;
		element->toString(std::cout);
		std::cout << std::endl;

        const IfcSchema::IfcWindow* window;
        if ((window = element->as<IfcSchema::IfcWindow>()) != 0) {
            if (window->OverallWidth() && window->OverallHeight()) {
                const double area = *window->OverallWidth() * *window->OverallHeight();
                std::cout << "The area of this window is " << area << std::endl;
            }
        }

		element_properties props;
		get_psets(props, element);

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
