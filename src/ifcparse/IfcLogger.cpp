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

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/version.hpp>

#include <iostream>
#include <algorithm>

using boost::property_tree::ptree;

namespace {
	static const char* severity_strings[] = {"Notice", "Warning", "Error"};

	void plain_text_message(std::ostream& os, const boost::optional<IfcSchema::IfcProduct*>& current_product, Logger::Severity type, const std::string& message, IfcEntityInstanceData* entity) {
		os << "[" << severity_strings[type] << "] ";
		if (current_product) {
			os << "{" << (*current_product)->GlobalId() << "} ";
		}
		os << message << std::endl;
		if (entity) {
			os << entity->toString() << std::endl;
		}
	}

	void json_message(std::ostream& os, const boost::optional<IfcSchema::IfcProduct*>& current_product, Logger::Severity type, const std::string& message, IfcEntityInstanceData* entity) {
		ptree pt;
		pt.put("level", severity_strings[type]);
		if (current_product) {
			pt.put("product", (**current_product).entity->toString());
		}
		pt.put("message", message);
		if (entity) {
			pt.put("instance", entity);
		}
		boost::property_tree::write_json(os, pt, false);
	}
}

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
	if (log2 && type >= verbosity) {
		if (format == FMT_PLAIN) {
			plain_text_message(*log2, current_product, type, message, entity);
		} else if (format == FMT_JSON) {
			json_message(*log2, current_product, type, message, entity);
		}
	}
}

void Logger::Message(Logger::Severity type, const std::exception& exception, IfcEntityInstanceData* entity) {
	Message(type, exception.what(), entity);
}

void Logger::Status(const std::string& message, bool new_line) {
	if (log1) {
		(*log1) << message;
		if ( new_line ) (*log1) << std::endl;
		else (*log1) << std::flush;
	}
}

void Logger::ProgressBar(int progress) {
	if (log1) {
		Status("\r[" + std::string(progress,'#') + std::string(50 - progress,' ') + "]", false);
	}
}

std::string Logger::GetLog() {
	return log_stream.str();
}

void Logger::Verbosity(Logger::Severity v) { verbosity = v; }
Logger::Severity Logger::Verbosity() { return verbosity; }

void Logger::OutputFormat(Format f) { format = f; }
Logger::Format Logger::OutputFormat() { return format; }

std::ostream* Logger::log1 = 0;
std::ostream* Logger::log2 = 0;
std::stringstream Logger::log_stream;
Logger::Severity Logger::verbosity = Logger::LOG_NOTICE;
Logger::Format Logger::format = Logger::FMT_PLAIN;
boost::optional<IfcSchema::IfcProduct*> Logger::current_product;