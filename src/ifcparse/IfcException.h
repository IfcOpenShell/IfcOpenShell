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

#ifndef IFCEXCEPTION_H
#define IFCEXCEPTION_H

#include "ifc_parse_api.h"

#include <boost/lexical_cast.hpp>

#include <exception>
#include <string>

#ifdef _MSC_VER
// "C4275 can be ignored in Visual C++ if you are deriving from a type in the Standard C++ Library",
// https://msdn.microsoft.com/en-us/library/3tdb471s.aspx
#pragma warning(push)
#pragma warning(disable : 4275)
#endif

namespace IfcParse {
	class IFC_PARSE_API IfcException : public std::exception {
	private:
		std::string message;
	public:
		IfcException(const std::string& m)
			 : message(m) {}
		virtual ~IfcException () throw () {}
		virtual const char* what() const throw() {
			return message.c_str(); 
		}
	};

	class IFC_PARSE_API IfcAttributeOutOfRangeException : public IfcException {
	public:
		IfcAttributeOutOfRangeException(const std::string& e)
			: IfcException(e) {}
		~IfcAttributeOutOfRangeException () throw () {}
	};

	class IFC_PARSE_API IfcInvalidTokenException : public IfcException {
	public:
		IfcInvalidTokenException(
			int token_start,
			const std::string& token_string,
			const std::string& expected_type
		)
			: IfcException(
				std::string("Token ") + token_string + " at " + 
				boost::lexical_cast<std::string>(token_start) + 
				" invalid " + expected_type
			)
		{}
		IfcInvalidTokenException(
			int token_start,
			char c
		)
			: IfcException(
				std::string("Unexpected '") + std::string(1, c) + "' at " +
				boost::lexical_cast<std::string>(token_start)
			)
		{}
		~IfcInvalidTokenException() throw () {}
	};

}

#ifdef _MSC_VER
#pragma warning(pop)
#endif

#endif
