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

/** @file   IfcGeomFilter.h
    @brief  A set of predefined product filters for IfcGeom::Iterator */

#ifndef IFCGEOMFILTER_H
#define IFCGEOMFILTER_H

#include "IfcGeom.h"

#include <boost/function.hpp>
#include <boost/regex.hpp>
#include <boost/algorithm/string/replace.hpp>
#include <boost/algorithm/string/case_conv.hpp>

#include <functional>

namespace IfcGeom
{
    /// The filter function (free or member function) or function object (use boost::ref() to reference to it)
    /// should return true if the geometry for the product is wanted to be included in the output.
    /// http://www.boost.org/doc/libs/1_62_0/doc/html/function/tutorial.html
    typedef boost::function<bool(IfcSchema::IfcProduct*)> filter_t;

    struct filter
    {
        filter() : include(false), traverse(false) {}
        filter(bool incl, bool trav) : include(incl), traverse(trav) {}
        /// Should the product be included (true) or excluded (false).
        bool include;
        /// If traversal requested, traverse to the parents to see if they satisfy the criteria. E.g. we might be looking for
        /// children of a storey named "Level 20", or children of entities that have no representation, e.g. IfcCurtainWall.
        bool traverse;
        /// Optional description for the filtering criteria of this filter.
        std::string description;

        bool match(IfcSchema::IfcProduct* prod, const filter_t& pred) const
        {
            bool is_match = pred(prod);
            if (!is_match && traverse) {
                is_match = traverse_match(prod, pred);
            }
            return is_match == include;
        }

        static bool traverse_match(IfcSchema::IfcProduct* prod, const filter_t& pred)
        {
            IfcSchema::IfcProduct* parent, *current = prod;
            while ((parent = dynamic_cast<IfcSchema::IfcProduct*>(IfcGeom::Kernel::get_decomposing_entity(current))) != 0) {
                if (pred(parent)) {
                    return true;
                }
                current = parent;
            }
            return false;
        }
    };

    struct wildcard_filter : public filter
    {
        wildcard_filter() : filter(false, false) {}
        wildcard_filter(bool include, bool traverse, const std::set<std::string>& patterns)
            : filter(include, traverse)
        {
            populate(patterns);
        }

        std::set<boost::regex> values;

        void populate(const std::set<std::string>& patterns)
        {
            values.clear();
            foreach(const std::string &pattern, patterns) {
                values.insert(wildcard_string_to_regex(pattern));
            }
        }

        bool match(const std::string &str) const { return match_values(values, str); }

        static bool match_values(const std::set<boost::regex>& values, const std::string &str)
        {
            foreach(const boost::regex& r, values) {
                if (boost::regex_match(str, r)) {
                    return true;
                }
            }
            return false;
        }

        static boost::regex wildcard_string_to_regex(std::string str)
        {
            // Escape all non-"*?" regex special chars
            static const std::string special_chars = "\\^.$|()[]+/";
            foreach(char c, special_chars) {
                std::string char_str(1, c);
                boost::replace_all(str, char_str, "\\" + char_str);
            }
            // Convert "*?" to their regex equivalents
            boost::replace_all(str, "?", ".");
            boost::replace_all(str, "*", ".*");
            return boost::regex(str);
        }
    };

    /// @note supports only string arguments for now
    struct string_arg_filter : public wildcard_filter
    {
        // Using this for now in order to overcome the fact that different classes have the argument at different indices.
        typedef std::map<IfcSchema::Type::Enum, unsigned short> arg_map_t;
        arg_map_t args;

        /// @todo Take only attribute name when IfcBaseClass and IfcLateBoundEntity are merged.
        string_arg_filter(arg_map_t args) : args(args) { assert_arguments(); }
        string_arg_filter(IfcSchema::Type::Enum type, unsigned short index) { args[type] = index;  assert_arguments(); }
        string_arg_filter(
            IfcSchema::Type::Enum type1, unsigned short index1,
            IfcSchema::Type::Enum type2, unsigned short index2)
        {
            args[type1] = index1;
            args[type2] = index2;
            assert_arguments();
        }

        /// @todo this won't be needed when we have the generic argument name access
        void assert_arguments()
        {
#ifndef NDEBUG
            for (arg_map_t::const_iterator it = args.begin(); it != args.end(); ++it) {
                IfcEntityInstanceData dummy(it->first);
                IfcUtil::IfcBaseClass* base = IfcSchema::SchemaEntity(&dummy);
                assert(it->second < base->getArgumentCount() && "Argument index out of bounds");
                assert(base->getArgumentType(it->second) == IfcUtil::Argument_STRING && "Argument type not string");
                delete base;
            }
#endif
        }

        std::string value(IfcSchema::IfcProduct* prod) const
        {
            for (arg_map_t::const_iterator it = args.begin(); it != args.end(); ++it) {
                if (prod->is(it->first) && it->second < prod->entity->getArgumentCount() &&
                    prod->getArgumentType(it->second) == IfcUtil::Argument_STRING) {
                    Argument *arg = prod->entity->getArgument(it->second);
                    if (!arg->isNull()) {
                        return *arg;
                    }
                }
            }
            return "";
        }

        bool match(IfcSchema::IfcProduct* prod) const { return wildcard_filter::match(value(prod)); }

        bool operator()(IfcSchema::IfcProduct* prod) const
        {
            // @note bind1st() and mem_fun() deprecated in C++11, use bind() and mem_fn() when migrating to C++11.
            return filter::match(prod, std::bind1st(std::mem_fun(&string_arg_filter::match), this));
        }

        void update_description()
        {
            std::stringstream ss;

            ss << (traverse ? "traverse " : "") << (include ? "include" : "exclude");
            std::vector<std::string> patterns;
            foreach(const boost::regex& r, values) {
                patterns.push_back("\"" + r.str() + "\"");
            }

            for (arg_map_t::const_iterator it = args.begin(); it != args.end(); ++it) {
                IfcEntityInstanceData dummy(it->first);
                IfcUtil::IfcBaseClass* base = IfcSchema::SchemaEntity(&dummy);
                try {
                    ss << " " << IfcSchema::Type::ToString(it->first) << "." << base->getArgumentName(it->second);
                } catch (const std::exception& e) {
					Logger::Error(e);
				}
                delete base;
            }

            ss << " values " << boost::algorithm::join(patterns, " ");
            description = ss.str();
        }
    };

    struct layer_filter : public wildcard_filter
    {
        typedef std::map<std::string, IfcSchema::IfcPresentationLayerAssignment*> layer_map_t;

        layer_filter() {}
        layer_filter(bool include, bool traverse, const std::set<std::string>& patterns)
            : wildcard_filter(include, traverse, patterns)
        {
        }

        bool match(IfcSchema::IfcProduct* prod) const
        {
            layer_map_t layers = IfcGeom::Kernel::get_layers(prod);
            return std::find_if(layers.begin(), layers.end(), wildcards_match(values)) != layers.end();
        }

        bool operator()(IfcSchema::IfcProduct* prod) const
        {
            return filter::match(prod, std::bind1st(std::mem_fun(&layer_filter::match), this));
        }

        struct wildcards_match
        {
            wildcards_match(const std::set<boost::regex>& patterns) : patterns(patterns) {}
            bool operator()(const layer_map_t::value_type& layer_map_value) const
            {
                return wildcard_filter::match_values(patterns, layer_map_value.first);
            }

            std::set<boost::regex> patterns;
        };

        void update_description()
        {
            std::stringstream ss;
            ss << (traverse ? "traverse " : "") << (include ? "include" : "exclude") << " layers";
            std::vector<std::string> str_values;
            foreach(const boost::regex& r, values) {
                str_values.push_back(" \"" + r.str() + "\"");
            }
            ss << boost::algorithm::join(str_values, " ");
            description = ss.str();
        }
    };

    struct entity_filter : public filter
    {
        entity_filter() {}
        entity_filter(bool include, bool traverse/*, const std::set<std::string>& types*/)
            : filter(include, traverse)
        {
            //populate(types);
        }

        std::set<IfcSchema::Type::Enum> values;

        void populate(const std::set<std::string>& types)
        {
            values.clear();
            foreach(const std::string& type, types) {
                IfcSchema::Type::Enum ty;
                try {
                    ty = IfcSchema::Type::FromString(boost::to_upper_copy(type));
                } catch (const IfcParse::IfcException&) {
                    throw IfcParse::IfcException("'" +  type + "' does not name a valid IFC entity");
                }
                values.insert(ty);
                /// @todo Add child classes so that containment in set can be in O(log n)
            }
        }

        bool match(IfcSchema::IfcProduct* prod) const
        {
            // The set is iterated over to able to filter on subtypes.
            foreach(IfcSchema::Type::Enum type, values) {
                if (prod->is(type)) {
                    return true;
                }
            }
            return false;
        }

        bool operator()(IfcSchema::IfcProduct* prod) const
        {
            return filter::match(prod, std::bind1st(std::mem_fun(&entity_filter::match), this));
        }

        void update_description()
        {
            std::stringstream ss;
            ss << (traverse ? "traverse " : "") << (include ? "include" : "exclude") << " entities";
            foreach(IfcSchema::Type::Enum type, values) {
                ss << " " << IfcSchema::Type::ToString(type);
            }
            description = ss.str();
        }
    };
}

#endif
