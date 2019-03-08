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
#include "../ifcparse/Argument.h"

#include <boost/algorithm/string/replace.hpp>
#include <boost/optional.hpp>

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/version.hpp>

#include <iostream>
#include <algorithm>

namespace {
	
	template <typename T>
	struct severity_strings {
		static const std::array<std::basic_string<T>, 3> value;
	};

	template <>
	const std::array<std::basic_string<char>, 3> severity_strings<char>::value = { "Notice", "Warning", "Error" };

	template <>
	const std::array<std::basic_string<wchar_t>, 3> severity_strings<wchar_t>::value = { L"Notice", L"Warning", L"Error" };
	
	template <typename T>
	void plain_text_message(T& os, const boost::optional<IfcUtil::IfcBaseClass*>& current_product, Logger::Severity type, const std::string& message, const IfcUtil::IfcBaseClass* instance) {
		os << "[" << severity_strings<typename T::char_type>::value[type] << "] ";
		if (current_product) {
            std::string global_id = *((IfcUtil::IfcBaseEntity*)*current_product)->get("GlobalId");
			os << "{" << global_id.c_str() << "} ";
		}
		os << message.c_str() << std::endl;
		if (instance) {
			std::string instance_string = instance->data().toString();
			if (instance_string.size() > 259) {
				instance_string = instance_string.substr(0, 256) + "...";
			}
			os << instance_string.c_str() << std::endl;
		}
	}

	template <typename T>
	std::basic_string<T> string_as(const std::string& s) {
		std::basic_string<T> v;
		v.assign(s.begin(), s.end());
		return v;
	}

	template <typename T>
	void json_message(T& os, const boost::optional<IfcUtil::IfcBaseClass*>& current_product, Logger::Severity type, const std::string& message, const IfcUtil::IfcBaseClass* instance) {
		boost::property_tree::basic_ptree<std::basic_string<typename T::char_type>, std::basic_string<typename T::char_type> > pt;
		
		// @todo this is crazy
		static const typename T::char_type level_string[] = { 'l', 'e', 'v', 'e', 'l', 0 };
		static const typename T::char_type product_string[] = { 'p', 'r', 'o', 'd', 'u', 'c', 't', 0 };
		static const typename T::char_type message_string[] = { 'm', 'e', 's', 's', 'a', 'g', 'e', 0 };
		static const typename T::char_type instance_string[] = { 'i', 'n', 's', 't', 'a', 'n', 'c', 'e', 0 };
		
		pt.put(level_string, severity_strings<typename T::char_type>::value[type]);
		if (current_product) {
			pt.put(product_string, string_as<typename T::char_type>((**current_product).data().toString()));
		}
		pt.put(message_string, string_as<typename T::char_type>(message));
		if (instance) {
			pt.put(instance_string, string_as<typename T::char_type>(instance->data().toString()));
		}
		boost::property_tree::write_json(os, pt, false);
	}
}

void Logger::SetProduct(boost::optional<IfcUtil::IfcBaseClass*> product) {
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

void Logger::Message(Logger::Severity type, const std::string& message, const IfcUtil::IfcBaseClass* instance) {
	if ((log2 || wlog2) && type >= verbosity) {
		if (format == FMT_PLAIN) {
            if (log2) {
                plain_text_message(*log2, current_product, type, message, instance);
            } else if (wlog2) {
                plain_text_message(*wlog2, current_product, type, message, instance);
            }
		} else if (format == FMT_JSON) {
            if (log2) {
                json_message(*log2, current_product, type, message, instance);
            } else if (wlog2) {
                json_message(*wlog2, current_product, type, message, instance);
            }
		}
	}
}

void Logger::Message(Logger::Severity type, const std::exception& exception, const IfcUtil::IfcBaseClass* instance) {
	Message(type, std::string(exception.what()), instance);
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

Logger::Severity Logger::MaxSeverity() { return max_severity; }

void Logger::OutputFormat(Format f) { format = f; }
Logger::Format Logger::OutputFormat() { return format; }

std::ostream* Logger::log1 = 0;
std::ostream* Logger::log2 = 0;
std::wostream* Logger::wlog1 = 0;
std::wostream* Logger::wlog2 = 0;
std::stringstream Logger::log_stream;
Logger::Severity Logger::verbosity = Logger::LOG_NOTICE;
Logger::Severity Logger::max_severity = Logger::LOG_NOTICE;
Logger::Format Logger::format = Logger::FMT_PLAIN;
boost::optional<IfcUtil::IfcBaseClass*> Logger::current_product;
