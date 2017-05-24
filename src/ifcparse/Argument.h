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

#ifndef ARGUMENT_H
#define ARGUMENT_H

#include <set>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>

#include "ifc_parse_api.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4enum.h"
#else
#include "../ifcparse/Ifc2x3enum.h"
#endif

#include "../ifcparse/IfcEntityList.h"

#include <boost/shared_ptr.hpp>
#include <boost/dynamic_bitset.hpp>
#include <boost/foreach.hpp>

#define foreach BOOST_FOREACH
#define rforeach BOOST_REVERSE_FOREACH

class Argument;
class IfcEntityList;
class IfcEntityListList;
class IfcEntityInstanceData;
namespace IfcParse {
	class IfcFile;
}
namespace IfcUtil {
	class IfcBaseClass;

    IFC_PARSE_API const char* ArgumentTypeToString(ArgumentType argument_type);

	IFC_PARSE_API bool valid_binary_string(const std::string& s);
    /// Replaces spaces and potentially other problem causing characters with underscores.
    IFC_PARSE_API void sanitate_material_name(std::string &str);
    IFC_PARSE_API void escape_xml(std::string &str);
    IFC_PARSE_API void unescape_xml(std::string &str);
}

class IFC_PARSE_API Argument {
public:
	virtual operator int() const;
	virtual operator bool() const;
	virtual operator double() const;
	virtual operator std::string() const;
	virtual operator boost::dynamic_bitset<>() const;
	virtual operator IfcUtil::IfcBaseClass*() const;

	virtual operator std::vector<int>() const;
	virtual operator std::vector<double>() const;
	virtual operator std::vector<std::string>() const;
	virtual operator std::vector<boost::dynamic_bitset<> >() const;
	virtual operator IfcEntityList::ptr() const;

	virtual operator std::vector< std::vector<int> >() const;
	virtual operator std::vector< std::vector<double> >() const;
	virtual operator IfcEntityListList::ptr() const;

	virtual bool isNull() const = 0;
	virtual unsigned int size() const = 0;

	virtual IfcUtil::ArgumentType type() const = 0;
	virtual Argument* operator [] (unsigned int i) const = 0;
	virtual std::string toString(bool upper=false) const = 0;
	
	virtual ~Argument() {};
};

#endif
