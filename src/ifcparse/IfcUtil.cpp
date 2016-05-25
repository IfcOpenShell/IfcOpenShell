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

#include "IfcUtil.h"
#include "../ifcparse/IfcException.h"

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
IfcEntityList::ptr IfcEntityList::filtered(const std::set<IfcSchema::Type::Enum>& entities) {
	IfcEntityList::ptr return_value(new IfcEntityList);
	for (it it = begin(); it != end(); ++it) {
		bool contained = false;
		for (std::set<IfcSchema::Type::Enum>::const_iterator jt = entities.begin(); jt != entities.end(); ++jt) {
			if ((*it)->is(*jt)) {
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


unsigned int IfcUtil::IfcBaseType::getArgumentCount() const { return 1; }
Argument* IfcUtil::IfcBaseType::getArgument(unsigned int i) const { return entity->getArgument(i); }
const char* IfcUtil::IfcBaseType::getArgumentName(unsigned int i) const { if (i == 0) { return "wrappedValue"; } else { throw IfcParse::IfcAttributeOutOfRangeException("Argument index out of range"); } }


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

	"AGGREGATE OF INT",
	"AGGREGATE OF DOUBLE",
	"AGGREGATE OF STRING",
	"AGGREGATE OF BINARY",
	"AGGREGATE OF ENTITY INSTANCE",

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

#ifndef IFCPARSE_NO_REGEX
boost::regex IfcUtil::wildcard_string_to_regex(std::string str)
{
    // Escape all non-"*?" regex special chars
    std::string special_chars = "\\^.$|()[]+/";
    foreach(char c, special_chars) {
        std::string char_str(1, c);
        boost::replace_all(str, char_str, "\\"+ char_str);
    }
    // Convert "*?" to their regex equivalents
    boost::replace_all(str, "?", ".");
    boost::replace_all(str, "*", ".*");
    return boost::regex(str);
}
#endif

void IfcUtil::sanitate_material_name(std::string &str)
{
    // Spaces in material names have been observed to cause problems with obj and dae importers.
    // Handle other potential problematic characters here too if observing problems.
    boost::replace_all(str, " ", "_");
}

void IfcUtil::escape_xml(std::string &str)
{
    boost::replace_all(str, "\"", "&quot;");
    boost::replace_all(str, "'", "&apos;");
    boost::replace_all(str, "<", "&lt;");
    boost::replace_all(str, ">", "&gt;");
    boost::replace_all(str, "&", "&amp;");
}

void IfcUtil::unescape_xml(std::string &str)
{
    boost::replace_all(str, "&quot;", "\"");
    boost::replace_all(str, "&apos;", "'");
    boost::replace_all(str, "&lt;", "<");
    boost::replace_all(str, "&gt;", ">");
    boost::replace_all(str, "&amp;", "&");
}
