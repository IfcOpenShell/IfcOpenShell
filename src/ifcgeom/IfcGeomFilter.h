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

#include <boost/version.hpp>
#if BOOST_VERSION >= 107800 && defined(_MSC_VER)
#define BOOST_REGEX_NO_W32
#endif

#include "../ifcgeom/AbstractKernel.h"
#include "../ifcparse/IfcFile.h"
#include "../ifcgeom/abstract_mapping.h"

#include <boost/foreach.hpp>
#include <boost/function.hpp>
#include <boost/regex.hpp>
#include <boost/algorithm/string/replace.hpp>
#include <boost/algorithm/string/case_conv.hpp>

#include <functional>

namespace IfcGeom {
    /// The filter function (free or member function) or function object (use boost::ref() to reference to it)
    /// should return true if the geometry for the product is wanted to be included in the output.
    /// http://www.boost.org/doc/libs/1_62_0/doc/html/function/tutorial.html
	typedef boost::function<bool(IfcUtil::IfcBaseEntity*)> filter_t;

    struct filter
    {
        filter() : include(false), traverse(false), traverse_openings(false) {}
        filter(bool incl, bool trav, bool trav_openings = false) : include(incl), traverse(trav), traverse_openings(trav_openings) {}
        /// Should the product be included (true) or excluded (false).
        bool include;
        /// If traversal requested, traverse to the parents to see if they satisfy the criteria. E.g. we might be looking for
        /// children of a storey named "Level 20", or children of entities that have no representation, e.g. IfcCurtainWall.
        bool traverse;
		/// Include opening relationships as part of traversal.
		bool traverse_openings;
        /// Optional description for the filtering criteria of this filter.
        std::string description;

		bool match(IfcUtil::IfcBaseEntity* prod, const filter_t& pred) const {
            bool is_match = pred(prod);
            if (!is_match && traverse) {
                is_match = traverse_match(prod, pred);
            }
            return is_match == include;
        }

        bool traverse_match(IfcUtil::IfcBaseEntity* prod, const filter_t& pred) const
        {
            IfcUtil::IfcBaseEntity* parent, *current = prod;
			// @todo examine if this can indeed be static. For now usage is only
			// in IfcConvert so invocation is bound to a single file with a single
			// schema.
			// @todo pass settings
			ifcopenshell::geometry::Settings s;
			static auto mapping = ifcopenshell::geometry::impl::mapping_implementations().construct(prod->file_, s);
            while ((parent = mapping->get_decomposing_entity(current, traverse_openings)) != nullptr) {
                if (pred(parent)) {
                    return true;
                }
                current = parent;
            }
            return false;
        }
    };

	struct wildcard_filter : public filter {
        wildcard_filter() : filter(false, false) {}
        wildcard_filter(bool include, bool traverse, const std::set<std::string>& patterns)
			: filter(include, traverse) {
            populate(patterns);
        }

        std::set<boost::regex> values;

		void populate(const std::set<std::string>& patterns) {
            values.clear();
			for(auto& pattern: patterns) {
                values.insert(wildcard_string_to_regex(pattern));
            }
        }

        bool match(const std::string &str) const { return match_values(values, str); }

		static bool match_values(const std::set<boost::regex>& values, const std::string &str) {
			for(auto& r: values) {
                if (boost::regex_match(str, r)) {
                    return true;
                }
            }
            return false;
        }

		static boost::regex wildcard_string_to_regex(std::string str) {
            // Escape all non-"*?" regex special chars
            static const std::string special_chars = "\\^.$|()[]+/";
			for(auto c: special_chars) {
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
	struct attribute_filter : public wildcard_filter {
		std::string attribute_name;

		attribute_filter() {}
		attribute_filter(const std::string& attribute_name)
			: attribute_name(attribute_name) {}

		std::string value(IfcUtil::IfcBaseEntity* prod) const {
			try {
				return (std::string) prod->get(attribute_name);
			} catch (...) {
				// Either
				// (a) not an attribute name for this entity instance
				// (b) not a string attribute
				// (c) null for this entity instance
				// @todo: validate the filters with a reference to the schema
				//        probably in IfcGeomIteratorImplementation
				return "<invalid>";
            }
        }

		bool match(IfcUtil::IfcBaseEntity* prod) const {
			return wildcard_filter::match(value(prod));
		}

		bool operator()(IfcUtil::IfcBaseEntity* prod) const {
			return filter::match(prod, std::bind(&attribute_filter::match, this, std::placeholders::_1));
        }

		void update_description() {
            std::stringstream ss;

            ss << (traverse ? "traverse " : "") << (include ? "include" : "exclude");
            std::vector<std::string> patterns;
			for (auto& r : values) {
                patterns.push_back("\"" + r.str() + "\"");
            }

			ss << " " << attribute_name;
            ss << " values " << boost::algorithm::join(patterns, " ");

            description = ss.str();
        }
    };

	struct layer_filter : public wildcard_filter {
		typedef std::map<std::string, IfcUtil::IfcBaseEntity*> layer_map_t;

        layer_filter() {}
        layer_filter(bool include, bool traverse, const std::set<std::string>& patterns)
			: wildcard_filter(include, traverse, patterns) {}

		bool match(IfcUtil::IfcBaseEntity* prod) const {
			// @todo
			ifcopenshell::geometry::Settings s;
			static auto mapping = ifcopenshell::geometry::impl::mapping_implementations().construct(prod->file_, s);
			layer_map_t layers = mapping->get_layers(prod);
            return std::find_if(layers.begin(), layers.end(), wildcards_match(values)) != layers.end();
        }

		bool operator()(IfcUtil::IfcBaseEntity* prod) const {
            return filter::match(prod, std::bind(&layer_filter::match, this, std::placeholders::_1));
        }

		struct wildcards_match {
            wildcards_match(const std::set<boost::regex>& patterns) : patterns(patterns) {}
			bool operator()(const layer_map_t::value_type& layer_map_value) const {
                return wildcard_filter::match_values(patterns, layer_map_value.first);
            }

            std::set<boost::regex> patterns;
        };

		void update_description() {
            std::stringstream ss;
            ss << (traverse ? "traverse " : "") << (include ? "include" : "exclude") << " layers";
            std::vector<std::string> str_values;
            BOOST_FOREACH(const boost::regex& r, values) {
                str_values.push_back(" \"" + r.str() + "\"");
            }
            ss << boost::algorithm::join(str_values, " ");
            description = ss.str();
        }
    };

	struct entity_filter : public filter {
		std::set<std::string> entity_names;

        entity_filter() {}
		entity_filter(bool include, bool traverse, const std::set<std::string>& entity_names)
            : filter(include, traverse)
			, entity_names(entity_names) {}

		bool match(IfcUtil::IfcBaseEntity* prod) const {
            // The set is iterated over to able to filter on subtypes.
			for (auto& name : entity_names) {
				if (prod->declaration().is(name)) {
                    return true;
                }
            }
            return false;
        }

		bool operator()(IfcUtil::IfcBaseEntity* prod) const {
            return filter::match(prod, std::bind(&entity_filter::match, this, std::placeholders::_1));
        }

		void update_description() {
            std::stringstream ss;
            ss << (traverse ? "traverse " : "") << (include ? "include" : "exclude") << " entities";
			for (auto& name : entity_names) {
				ss << " " << name;
            }
            description = ss.str();
        }
    };

	struct instance_id_filter : public filter {
		std::set<int> instance_ids_;

		instance_id_filter() {}
		instance_id_filter(bool include, bool traverse, const std::set<int>& instance_ids)
			: filter(include, traverse)
			, instance_ids_(instance_ids) {}

		bool match(IfcUtil::IfcBaseEntity* prod) const {
			return instance_ids_.find(prod->id()) != instance_ids_.end();
		}

		bool operator()(IfcUtil::IfcBaseEntity* prod) const {
			return filter::match(prod, std::bind(&instance_id_filter::match, this, std::placeholders::_1));
		}

		void update_description() {
			std::stringstream ss;
			ss << (traverse ? "traverse " : "") << (include ? "include" : "exclude") << " ids";
			for (auto& id : instance_ids_) {
				ss << " " << id;
			}
			description = ss.str();
		}
	};
}

#endif
