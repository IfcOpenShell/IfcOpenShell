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

        //static bool traverse_match(IfcSchema::IfcProduct* prod, filter_t pred)
        //{
        //    bool is_match = false;
        //    IfcSchema::IfcProduct* parent, *current = prod;
        //    while ((parent = static_cast<IfcSchema::IfcProduct*>(IfcGeom::Kernel::get_decomposing_entity(current))) != 0) {
        //        if (pred(parent)) {
        //            is_match = true;
        //            break;
        //        }
        //        current = parent;
        //    }
        //}
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

    /// @todo Maybe not use template class for this after all. Attribute name would be better
    /// than index, but IfcBaseClass doesn't have getArgument(name) (IfcLateBoundEntity would have though).
    template<class IfcType, unsigned short ArgIndex, typename ArgType>
    struct arg_filter : public wildcard_filter
    {
        arg_filter()
        {
#ifndef NDEBUG
            IfcType dummy(0);
            assert(ArgIndex < dummy.getArgumentCount());
#endif
        }
        arg_filter(bool include, bool traverse, const std::set<std::string>& patterns)
            : wildcard_filter(include, traverse, patterns)
        {
    #ifndef NDEBUG
            IfcType dummy(0);
            assert(ArgIndex < dummy.getArgumentCount());
    #endif
            populate(patterns);
        }

        ArgType value(IfcSchema::IfcProduct* prod) const
        {
            Argument *arg = prod->is(IfcType::Class()) ? prod->entity->getArgument(ArgIndex) : 0;
            return arg && !arg->isNull() ? *arg : ArgType();
        }

        bool operator()(IfcSchema::IfcProduct* prod) const
        {
            bool is_match = match(value(prod));
            if (is_match != include && traverse) {
                IfcSchema::IfcProduct* parent, *current = prod;
                while ((parent = static_cast<IfcSchema::IfcProduct*>(IfcGeom::Kernel::get_decomposing_entity(current))) != 0) {
                    if (match(value(parent))) {
                        is_match = true;
                        break;
                    }
                    current = parent;
                }
            }
            return is_match == include;
        }
    };

    struct layer_filter : public wildcard_filter
    {
        layer_filter() {}
        layer_filter(bool include, bool traverse, const std::set<std::string>& patterns)
            : wildcard_filter(include, traverse, patterns)
        {
        }

        bool operator()(IfcSchema::IfcProduct* prod) const
        {
            bool is_match = false;
            std::map<std::string, IfcSchema::IfcPresentationLayerAssignment*> layers = IfcGeom::Kernel::get_layers(prod);
            std::map<std::string, IfcSchema::IfcPresentationLayerAssignment*>::const_iterator lit;
            for (lit = layers.begin(); lit != layers.end(); ++lit) {
                if (match(lit->first)) {
                    is_match = true;
                    break;
                }
            }

            if (is_match != include && traverse) {
                for (lit = layers.begin(); lit != layers.end(); ++lit) {
                    IfcSchema::IfcProduct* parent, *current = prod;
                    while ((parent = static_cast<IfcSchema::IfcProduct*>(IfcGeom::Kernel::get_decomposing_entity(current))) != 0) {
                        if (match(lit->first)) {
                            is_match = true;
                            break;
                        }
                        current = parent;
                    }
                    if (is_match) {
                        break;
                    }
                }
            }

            return is_match == include;
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
                IfcSchema::IfcProduct* parent, *current = prod;
                while ((parent = static_cast<IfcSchema::IfcProduct*>(IfcGeom::Kernel::get_decomposing_entity(current))) != 0) {
                    if (match(parent)) {
                        is_match = true;
                        break;
                    }
                    current = parent;
                }
            }
            return is_match == include;
        }
    };
}

#endif
