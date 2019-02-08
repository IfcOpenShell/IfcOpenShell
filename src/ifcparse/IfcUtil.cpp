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

#ifdef _MSC_VER
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef NOMSG
#define NOMSG NOMSG
#endif
#ifndef NODRAWTEXT
#define NODRAWTEXT NODRAWTEXT
#endif
#ifndef NOGDI
#define NOGDI NOGDI
#endif
#ifndef NOSERVICE
#define NOSERVICE NOSERVICE   
#endif
#ifndef NOKERNEL
#define NOKERNEL NOKERNEL
#endif
#ifndef NOUSER
#define NOUSER NOUSER
#endif
#ifndef NOMCX
#define NOMCX NOMCX
#endif
#ifndef NOIME
#define NOIME NOIME
#endif
#include <Windows.h>
#endif

#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/Argument.h"
#include "../ifcparse/utils.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcEntityList.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4-latebound.h"
#else
#include "../ifcparse/Ifc2x3-latebound.h"
#endif

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
void IfcEntityList::reserve(unsigned capacity) { ls.reserve((size_t)capacity); }
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

std::vector<std::string> IfcUtil::IfcBaseEntity::getAttributeNames() const {
	std::vector<std::string> return_value;
	return_value.reserve(getArgumentCount());
	for (unsigned i = 0; i < getArgumentCount(); ++i) {
		return_value.push_back(getArgumentName(i));
	}
	return return_value;
}

std::vector<std::string> IfcUtil::IfcBaseEntity::getInverseAttributeNames() const {
	std::vector<std::string> return_value;
	std::set<std::string> values = IfcSchema::Type::GetInverseAttributeNames(entity->type());
	std::copy(values.begin(), values.end(), std::back_inserter(return_value));
	return return_value;
}

Argument* IfcUtil::IfcBaseEntity::getArgumentByName(const std::string& name) const {
	unsigned int i = IfcSchema::Type::GetAttributeIndex(type(), name);
	return getArgument(i);
}

#ifdef _MSC_VER
std::string IfcUtil::path::to_utf8(const std::wstring& str) {
	int buffer_size = WideCharToMultiByte(CP_UTF8, 0, str.c_str(), -1, 0, 0, 0, 0);
	char* buffer = new char[buffer_size];
	WideCharToMultiByte(CP_UTF8, 0, str.c_str(), -1, buffer, buffer_size, 0, 0);
	std::string str_utf8(buffer);
	delete[] buffer;
	return str_utf8;
}

std::wstring IfcUtil::path::from_utf8(const std::string& str) {
	int buffer_size = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), -1, 0, 0);
	wchar_t* buffer = new wchar_t[buffer_size];
	MultiByteToWideChar(CP_UTF8, 0, str.c_str(), -1, buffer, buffer_size);
	std::wstring str_wide(buffer);
	delete[] buffer;
	return str_wide;
}

IFC_PARSE_API bool IfcUtil::path::rename_file(const std::string& old_filename, const std::string& new_filename) {
	std::wstring old_filename_w = from_utf8(old_filename);
	std::wstring new_filename_w = from_utf8(new_filename);
	delete_file(new_filename);
	const bool success = !!MoveFileW(old_filename_w.c_str(), new_filename_w.c_str());
	return success;
}

IFC_PARSE_API bool IfcUtil::path::delete_file(const std::string& filename) {
	std::wstring filename_w = from_utf8(filename);
	const bool success = !!DeleteFileW(filename_w.c_str());
	return success;
}

#else

IFC_PARSE_API bool IfcUtil::path::rename_file(const std::string& old_filename, const std::string& new_filename) {
	// Whether or not rename() replaces an existing file is implementation-specific,
	// so remove() possible existing file always.
	delete_file(new_filename);
	return std::rename(old_filename.c_str(), new_filename.c_str()) == 0;
}

IFC_PARSE_API bool IfcUtil::path::delete_file(const std::string& filename) {
	return std::remove(filename.c_str());
}

#endif

