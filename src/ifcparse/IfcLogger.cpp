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

#include "IfcLogger.h"
#include "../ifcparse/IfcException.h"

#include <boost/algorithm/string/replace.hpp>
#include <boost/optional.hpp>

#include <iostream>
#include <algorithm>


void Logger::SetProduct(boost::optional<IfcSchema::IfcProduct*> product) {
	current_product = product;
}
void Logger::SetOutput(std::ostream* l1, std::ostream* l2) { 
	log1 = l1; 
	log2 = l2; 
	if ( ! log2 ) {
		log2 = &log_stream;
	}
}

void Logger::Message(Logger::Severity type, const std::string& message, IfcEntityInstanceData* entity) {
	if ( log2 && type >= verbosity ) {
		(*log2) << "[" << severity_strings[type] << "] ";
		if ( current_product ) {
		    (*log2) << "{" << (*current_product)->GlobalId() << "} ";
		}
		(*log2) << message << std::endl;
		if ( entity ) (*log2) << entity->toString() << std::endl;
	}
}

void Logger::Message(Logger::Severity type, const std::exception& exception, IfcEntityInstanceData* entity) {
	Message(type, exception.what(), entity);
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
boost::optional<IfcSchema::IfcProduct*> Logger::current_product;