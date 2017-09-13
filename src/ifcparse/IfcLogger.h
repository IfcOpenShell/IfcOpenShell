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

#ifndef IFCLOGGER_H
#define IFCLOGGER_H

#include <set>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <exception>

#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

#include <boost/optional.hpp>

#include "ifc_parse_api.h"

class IFC_PARSE_API Logger {
public:
	typedef enum { LOG_NOTICE, LOG_WARNING, LOG_ERROR } Severity;
private:
	static std::ostream* log1;
	static std::ostream* log2;
	static std::stringstream log_stream;
	static Severity verbosity;
	static const char* severity_strings[];
	static boost::optional<IfcSchema::IfcProduct*> current_product;
public:
	static void SetProduct(boost::optional<IfcSchema::IfcProduct*> product);
	/// Determines to what stream respectively progress and errors are logged
	static void SetOutput(std::ostream* l1, std::ostream* l2);
	/// Determines the types of log messages to get logged
	static void Verbosity(Severity v);
	static Severity Verbosity();
	
	/// Log a message to the output stream
	static void Message(Severity type, const std::string& message, IfcEntityInstanceData* entity=0);
	static void Message(Severity type, const std::exception& message, IfcEntityInstanceData* entity = 0);
	
	static void Notice(const std::string& message, IfcEntityInstanceData* entity = 0) { Message(LOG_NOTICE, message, entity); }
    static void Warning(const std::string& message, IfcEntityInstanceData* entity=0) { Message(LOG_WARNING, message, entity); }
    static void Error(const std::string& message, IfcEntityInstanceData* entity=0) { Message(LOG_ERROR, message, entity); }
	
	static void Notice(const std::exception& exception, IfcEntityInstanceData* entity = 0) { Message(LOG_NOTICE, exception, entity); }
	static void Warning(const std::exception& exception, IfcEntityInstanceData* entity = 0) { Message(LOG_WARNING, exception, entity); }
	static void Error(const std::exception& exception, IfcEntityInstanceData* entity = 0) { Message(LOG_ERROR, exception, entity); }

	static void Status(const std::string& message, bool new_line=true);

	static void ProgressBar(int progress);
	static std::string GetLog();
};

#endif
