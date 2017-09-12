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
	wlog1 = wlog2 = 0;
	log1 = l1; 
	log2 = l2; 
	if (!log2) {
		log2 = &log_stream;
	}
}

void Logger::SetOutput(std::wostream* l1, std::wostream* l2) {
	log1 = log2 = 0;
	wlog1 = l1;
	wlog2 = l2;
	if (!wlog2) {
		log2 = &log_stream;
	}
}

template <typename T>
void Logger::log(T& log2, Logger::Severity type, const std::string& message, IfcEntityInstanceData* entity) {
	log2 << "[" << severity_strings[type] << "] ";
	if (current_product) {
		log2 << "{" << (*current_product)->GlobalId().c_str() << "} ";
	}
	log2 << message.c_str() << std::endl;
	if (entity) {
		log2 << entity->toString().c_str() << std::endl;
	}
}

void Logger::Message(Logger::Severity type, const std::string& message, IfcEntityInstanceData* entity) {
	if (type >= verbosity) {
		if (log2) {
			log(*log2, type, message, entity);
		} else if (wlog2) {
			log(*wlog2, type, message, entity);
		}
	}
}

void Logger::Message(Logger::Severity type, const std::exception& exception, IfcEntityInstanceData* entity) {
	Message(type, exception.what(), entity);
}

template <typename T>
void status(T& log1, const std::string& message, bool new_line) {
	log1 << message.c_str();
	if (new_line) {
		log1 << std::endl;
	} else {
		log1 << std::flush;
	}
}

void Logger::Status(const std::string& message, bool new_line) {
	if (log1) {
		status(*log1, message, new_line);
	} else if (wlog1) {
		status(*wlog1, message, new_line);
	}
}

void Logger::ProgressBar(int progress) {
	Status("\r[" + std::string(progress,'#') + std::string(50 - progress,' ') + "]", false);
}

std::string Logger::GetLog() {
	return log_stream.str();
}

void Logger::Verbosity(Logger::Severity v) { verbosity = v; }
Logger::Severity Logger::Verbosity() { return verbosity; }

std::ostream* Logger::log1 = 0;
std::ostream* Logger::log2 = 0;
std::wostream* Logger::wlog1 = 0;
std::wostream* Logger::wlog2 = 0;
std::stringstream Logger::log_stream;
Logger::Severity Logger::verbosity = Logger::LOG_NOTICE;
const char* Logger::severity_strings[] = { "Notice","Warning","Error" };
boost::optional<IfcSchema::IfcProduct*> Logger::current_product;
