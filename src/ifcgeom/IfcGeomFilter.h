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
#ifndef NDEBUG
#include "../ifcparse/IfcWritableEntity.h"
#endif

#include <boost/function.hpp>
#include <boost/regex.hpp>
#include <boost/algorithm/string/replace.hpp>
#include <boost/algorithm/string/case_conv.hpp>

namespace IfcGeom
{
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

        static bool traverse_match(IfcSchema::IfcProduct* prod, const filter_t& pred)
        {
            IfcSchema::IfcProduct* parent, *current = prod;
            while ((parent = static_cast<IfcSchema::IfcProduct*>(IfcGeom::Kernel::get_decomposing_entity(current))) != 0) {
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

        bool match(const std::string &str) const
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
            std::string special_chars = "\\^.$|()[]+/";
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
                IfcWrite::IfcWritableEntity dummy(it->first);
                IfcUtil::IfcBaseClass* base = IfcSchema::SchemaEntity(&dummy);
                assert(it->second < base->getArgumentCount() && "Invalid argument index");
                delete base;
            }
#endif
        }

        std::string value(IfcSchema::IfcProduct* prod) const
        {
            for (arg_map_t::const_iterator it = args.begin(); it != args.end(); ++it) {
                if (prod->is(it->first)) {
                    Argument *arg = (it->second < prod->entity->getArgumentCount() ? prod->entity->getArgument(it->second) : 0);
                    if (arg && !arg->isNull()) {
                        return *arg;
                    }
                }
            }
            return "";
        }

        bool operator()(IfcSchema::IfcProduct* prod) const
        {
            bool is_match = match(value(prod));
            if (is_match != include && traverse) {
                is_match = traverse_match(prod, boost::ref(*this));
            }
            return is_match == include;
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
            bool is_match = match(prod);
            if (is_match != include && traverse) {
                is_match = traverse_match(prod, boost::ref(*this));
            }
            return is_match == include;
        }

        struct wildcards_match
        {
            wildcards_match(const std::set<boost::regex>& patterns) : patterns(patterns) {}
            bool operator()(const layer_map_t::value_type& layer_map_value) const
            {
                foreach(const boost::regex& r, patterns) {
                    if (boost::regex_match(layer_map_value.first, r)) {
                        return true;
                    }
                }
                return false;
            }

            std::set<boost::regex> patterns;
        };
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
                // TODO: Add child classes so that containment in set can be in O(log n)
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
            bool is_match = match(prod);
            if (is_match != include && traverse) {
                is_match = traverse_match(prod, boost::ref(*this));
            }
            return is_match == include;
        }
    };
}

#endif
