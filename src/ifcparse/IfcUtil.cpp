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

void Logger::SetOutput(std::ostream* l1, std::ostream* l2) { 
	log1 = l1; 
	log2 = l2; 
	if ( ! log2 ) {
		log2 = &log_stream;
	}
}
void Logger::Message(Logger::Severity type, const std::string& message, IfcAbstractEntity* entity) {
	if ( log2 && type >= verbosity ) {
		(*log2) << "[" << severity_strings[type] << "] " << message << std::endl;
		if ( entity ) (*log2) << entity->toString() << std::endl;
	}
}
void Logger::Status(const std::string& message, bool new_line) {
	if ( log1 ) {
		(*log1) << message;
		if ( new_line ) (*log1) << std::endl;
		else (*log1) << std::flush;
	}
}
void Logger::ProgressBar(int progress) {
	if ( log1 ) {
		Status("\r[" + std::string(progress,'#') + std::string(50 - progress,' ') + "]", false);
	}
}
std::string Logger::GetLog() {
	return log_stream.str();
}
void Logger::Verbosity(Logger::Severity v) { verbosity = v; }
Logger::Severity Logger::Verbosity() { return verbosity; }

std::ostream* Logger::log1 = 0;
std::ostream* Logger::log2 = 0;
std::stringstream Logger::log_stream;
Logger::Severity Logger::verbosity = Logger::LOG_NOTICE;
const char* Logger::severity_strings[] = { "Notice","Warning","Error" };

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
