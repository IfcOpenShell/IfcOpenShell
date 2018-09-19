﻿/********************************************************************************
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

#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/Argument.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcEntityList.h"

#include <boost/algorithm/string/replace.hpp>
#include <boost/optional.hpp>

#include <iostream>
#include <algorithm>


void IfcEntityList::push(IfcUtil::IfcBaseClass* l) {
	if (l) {
		ls.push_back(l);
	}
}
void IfcEntityList::push(const IfcEntityList::ptr& l) {
	if (l) {
		for( it i = l->begin(); i != l->end(); ++i  ) {
			if ( *i ) ls.push_back(*i);
		}
	}
}
unsigned int IfcEntityList::size() const { return (unsigned int) ls.size(); }
IfcEntityList::it IfcEntityList::begin() { return ls.begin(); }
IfcEntityList::it IfcEntityList::end() { return ls.end(); }
IfcUtil::IfcBaseClass* IfcEntityList::operator[] (int i) {
	return ls[i];
}
bool IfcEntityList::contains(IfcUtil::IfcBaseClass* instance) const {
	return std::find(ls.begin(), ls.end(), instance) != ls.end();
}
void IfcEntityList::remove(IfcUtil::IfcBaseClass* instance) {
	std::vector<IfcUtil::IfcBaseClass*>::iterator it;
	while ((it = std::find(ls.begin(), ls.end(), instance)) != ls.end()) {
		ls.erase(it);
	}
}

IfcEntityList::ptr IfcEntityList::filtered(const std::set<const IfcParse::declaration*>& entities) {
	IfcEntityList::ptr return_value(new IfcEntityList);
	for (it it = begin(); it != end(); ++it) {
		bool contained = false;
		for (std::set<const IfcParse::declaration*>::const_iterator jt = entities.begin(); jt != entities.end(); ++jt) {
			if ((*it)->declaration().is(**jt)) {
				contained = true;
				break;
			}
		}
		if (!contained) {
			return_value->push(*it);
		}
	}	
	return return_value;
}

IfcEntityList::ptr IfcEntityList::unique() {
	std::set<IfcUtil::IfcBaseClass*> encountered;
	IfcEntityList::ptr return_value(new IfcEntityList);
	for (it it = begin(); it != end(); ++it) {
		if (encountered.find(*it) == encountered.end()) {
			return_value->push(*it);
			encountered.insert(*it);
		}
	}
	return return_value;
}

//Note: some of these methods are overloaded in derived classes
Argument::operator int() const { throw IfcParse::IfcException("Argument is not an integer"); }
Argument::operator bool() const { throw IfcParse::IfcException("Argument is not a boolean"); }
Argument::operator double() const { throw IfcParse::IfcException("Argument is not a number"); }
Argument::operator std::string() const { throw IfcParse::IfcException("Argument is not a string"); }
Argument::operator boost::dynamic_bitset<>() const { throw IfcParse::IfcException("Argument is not a binary"); }
Argument::operator IfcUtil::IfcBaseClass*() const { throw IfcParse::IfcException("Argument is not an entity instance"); }
Argument::operator std::vector<double>() const { throw IfcParse::IfcException("Argument is not a list of floats"); }
Argument::operator std::vector<int>() const { throw IfcParse::IfcException("Argument is not a list of ints"); }
Argument::operator std::vector<std::string>() const { throw IfcParse::IfcException("Argument is not a list of strings"); }
Argument::operator std::vector<boost::dynamic_bitset<> >() const { throw IfcParse::IfcException("Argument is not a list of binaries"); }
Argument::operator IfcEntityList::ptr() const { throw IfcParse::IfcException("Argument is not a list of entity instances"); }
Argument::operator std::vector< std::vector<int> >() const { throw IfcParse::IfcException("Argument is not a list of list of ints"); }
Argument::operator std::vector< std::vector<double> >() const { throw IfcParse::IfcException("Argument is not a list of list of floats"); }
Argument::operator IfcEntityListList::ptr() const { throw IfcParse::IfcException("Argument is not a list of list of entity instances"); }


static const char* const argument_type_string[] = {
	"NULL",
	"DERIVED",
	"INT",
	"BOOL",
	"DOUBLE",
	"STRING",
	"BINARY",
	"ENUMERATION",
	"ENTITY INSTANCE",

	"EMPTY AGGREGATE",
	"AGGREGATE OF INT",
	"AGGREGATE OF DOUBLE",
	"AGGREGATE OF STRING",
	"AGGREGATE OF BINARY",
	"AGGREGATE OF ENTITY INSTANCE",

	"AGGREGATE OF EMPTY AGGREGATE",
	"AGGREGATE OF AGGREGATE OF INT",
	"AGGREGATE OF AGGREGATE OF DOUBLE",
	"AGGREGATE OF AGGREGATE OF ENTITY INSTANCE", 

	"UNKNOWN"
};

const char* IfcUtil::ArgumentTypeToString(ArgumentType argument_type) {
	return argument_type_string[static_cast<int>(argument_type)];
}

bool IfcUtil::valid_binary_string(const std::string& s) {
	for (std::string::const_iterator it = s.begin(); it != s.end(); ++it) {
		if (*it != '0' && *it != '1') return false;
	}
	return true;
}

void IfcUtil::sanitate_material_name(std::string &str)
{
    // Spaces in material names have been observed to cause problems with obj and dae importers.
    // Handle other potential problematic characters here too if observing problems.
    boost::replace_all(str, " ", "_");
}

void IfcUtil::escape_xml(std::string &str)
{
	boost::replace_all(str, "&", "&amp;");
    boost::replace_all(str, "\"", "&quot;");
    boost::replace_all(str, "'", "&apos;");
    boost::replace_all(str, "<", "&lt;");
    boost::replace_all(str, ">", "&gt;");
}

void IfcUtil::unescape_xml(std::string &str)
{
	boost::replace_all(str, "&amp;", "&");
    boost::replace_all(str, "&quot;", "\"");
    boost::replace_all(str, "&apos;", "'");
    boost::replace_all(str, "&lt;", "<");
    boost::replace_all(str, "&gt;", ">");
}

Argument* IfcUtil::IfcBaseEntity::get(const std::string& name) const {
	return data().getArgument(declaration().attribute_index(name));
}

void IfcUtil::IfcBaseClass::data(IfcEntityInstanceData* d) {
	delete data_;
	data_ = d; 
}

IfcUtil::ArgumentType IfcUtil::make_aggregate(IfcUtil::ArgumentType elem_type) {
	if (elem_type == IfcUtil::Argument_INT) {
		return IfcUtil::Argument_AGGREGATE_OF_INT;
	} else if (elem_type == IfcUtil::Argument_DOUBLE) {
		return IfcUtil::Argument_AGGREGATE_OF_DOUBLE;
	} else if (elem_type == IfcUtil::Argument_STRING) {
		return IfcUtil::Argument_AGGREGATE_OF_STRING;
	} else if (elem_type == IfcUtil::Argument_BINARY) {
		return IfcUtil::Argument_AGGREGATE_OF_BINARY;
	} else if (elem_type == IfcUtil::Argument_ENTITY_INSTANCE) {
		return IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE;
	} else if (elem_type == IfcUtil::Argument_AGGREGATE_OF_INT) {
		return IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT;
	} else if (elem_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
		return IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE;
	} else if (elem_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
		return IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE;
	} else if (elem_type == IfcUtil::Argument_EMPTY_AGGREGATE) {
		return IfcUtil::Argument_AGGREGATE_OF_EMPTY_AGGREGATE;
	} else {
		return IfcUtil::Argument_UNKNOWN;
	}
}

IfcUtil::ArgumentType IfcUtil::from_parameter_type(const IfcParse::parameter_type* pt) {
	// TODO: How to detect derived types here without a reference to the refering entity?

	const IfcParse::aggregation_type* at = pt->as_aggregation_type();
	const IfcParse::named_type* nt = pt->as_named_type();
	const IfcParse::simple_type* st = pt->as_simple_type();
	
	if (at) {
		return make_aggregate(from_parameter_type(at->type_of_element()));
	} else if (nt) {
		if (nt->declared_type()->as_entity()) {
			return IfcUtil::Argument_ENTITY_INSTANCE;
		} else if (nt->declared_type()->as_enumeration_type()) {
			return IfcUtil::Argument_ENUMERATION;
		} else if (nt->declared_type()->as_select_type()) {
			return IfcUtil::Argument_ENTITY_INSTANCE;
		} else if (nt->declared_type()->as_type_declaration()) {
			return from_parameter_type(nt->declared_type()->as_type_declaration()->declared_type());
		}
	} else if (st) {
		switch (st->declared_type()) {
		case IfcParse::simple_type::binary_type:
			return IfcUtil::Argument_BINARY;
		case IfcParse::simple_type::boolean_type:
			return IfcUtil::Argument_BOOL;
		case IfcParse::simple_type::integer_type:
			return IfcUtil::Argument_INT;
		case IfcParse::simple_type::logical_type:
			return IfcUtil::Argument_BOOL;
		case IfcParse::simple_type::number_type:
			return IfcUtil::Argument_DOUBLE;
		case IfcParse::simple_type::real_type:
			return IfcUtil::Argument_DOUBLE;
		case IfcParse::simple_type::string_type:
			return IfcUtil::Argument_STRING;
		case IfcParse::simple_type::datatype_COUNT:
			throw IfcParse::IfcException("Invalid simple type encountered");
		}
	}

	return IfcUtil::Argument_UNKNOWN;
}