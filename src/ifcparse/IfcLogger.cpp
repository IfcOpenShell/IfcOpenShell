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

#include "Argument.h"

#include <algorithm>
#include <boost/algorithm/string/replace.hpp>
#include <boost/optional.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/version.hpp>
#include <chrono>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <mutex>

namespace {

std::string get_time(bool with_milliseconds = false) {
    std::ostringstream oss;
    time_t now = time(nullptr);
    oss << std::put_time(localtime(&now), "%F %T");

    if (with_milliseconds) {
        auto now_chrono = std::chrono::system_clock::now();
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now_chrono.time_since_epoch()) % 1000;
        oss << '.' << std::setfill('0') << std::setw(3) << ms.count();
    }

    return oss.str();
}

template <typename T>
struct severity_strings {
    static const std::array<std::basic_string<T>, 5> value;
};

template <>
const std::array<std::basic_string<char>, 5> severity_strings<char>::value = {"Performance", "Debug", "Notice", "Warning", "Error"};

template <>
const std::array<std::basic_string<wchar_t>, 5> severity_strings<wchar_t>::value = {L"Performance", L"Debug", L"Notice", L"Warning", L"Error"};

template <typename T>
void plain_text_message(T& os, const boost::optional<IfcUtil::IfcBaseClass*>& current_product, Logger::Severity type, const std::string& message, const IfcUtil::IfcBaseInterface* instance) {
    os << "[" << severity_strings<typename T::char_type>::value[type] << "] ";
    os << "[" << get_time(type <= Logger::LOG_PERF).c_str() << "] ";
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
void json_message(T& os, const boost::optional<IfcUtil::IfcBaseClass*>& current_product, Logger::Severity type, const std::string& message, const IfcUtil::IfcBaseInterface* instance) {
    boost::property_tree::basic_ptree<std::basic_string<typename T::char_type>, std::basic_string<typename T::char_type>> pt;

    // @todo this is crazy
    static const typename T::char_type time_string[] = {'t', 'i', 'm', 'e', 0};
    static const typename T::char_type level_string[] = {'l', 'e', 'v', 'e', 'l', 0};
    static const typename T::char_type product_string[] = {'p', 'r', 'o', 'd', 'u', 'c', 't', 0};
    static const typename T::char_type message_string[] = {'m', 'e', 's', 's', 'a', 'g', 'e', 0};
    static const typename T::char_type instance_string[] = {'i', 'n', 's', 't', 'a', 'n', 'c', 'e', 0};

    pt.put(level_string, severity_strings<typename T::char_type>::value[type]);
    if (current_product) {
        pt.put(product_string, string_as<typename T::char_type>((**current_product).data().toString()));
    }
    pt.put(message_string, string_as<typename T::char_type>(message));
    if (instance) {
        pt.put(instance_string, string_as<typename T::char_type>(instance->data().toString()));
    }

    pt.put(time_string, string_as<typename T::char_type>(get_time()));

    boost::property_tree::write_json(os, pt, false);
}
} // namespace

void Logger::SetProduct(boost::optional<const IfcUtil::IfcBaseClass*> product) {
    if (verbosity_ <= LOG_DEBUG && product) {
        Message(LOG_DEBUG, "Begin processing", *product);
    }
    if (!product && print_perf_stats_on_element_) {
        PrintPerformanceStats();
        performance_statistics_.clear();
    }
    current_product_ = product;
}

void Logger::SetOutput(std::ostream* l1, std::ostream* l2) {
    wlog1_ = wlog2_ = 0;
    log1_ = l1;
    log2_ = l2;
    if (log2_ == nullptr) {
        log2_ = &log_stream_;
    }
}

void Logger::SetOutput(std::wostream* l1, std::wostream* l2) {
    log1_ = log2_ = 0;
    wlog1_ = l1;
    wlog2_ = l2;
    if (wlog2_ == nullptr) {
        log2_ = &log_stream_;
    }
}

void Logger::Message(Logger::Severity type, const std::string& message, const IfcUtil::IfcBaseInterface* instance) {
    static std::mutex m;
    std::lock_guard<std::mutex> lk(m);

    if (type == LOG_PERF) {
        if (!first_timepoint_) {
            first_timepoint_ = std::chrono::time_point_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now()).time_since_epoch().count();
        }
        double t0 = (std::chrono::time_point_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now()).time_since_epoch().count() - *first_timepoint_) / 1.e9;
        if (message.substr(0, 5) == "done ") {
            auto orig = message.substr(5);
            performance_statistics_[orig] += t0 - performance_signal_start_[orig];
        } else {
            performance_signal_start_[message] = t0;
        }
    }

    if (type > max_severity_) {
        max_severity_ = type;
    }
    if (((log2_ != nullptr) || (wlog2_ != nullptr)) && type >= verbosity_) {
        if (format_ == FMT_PLAIN) {
            if (log2_ != nullptr) {
                plain_text_message(*log2_, current_product_, type, message, instance);
            } else if (wlog2_ != nullptr) {
                plain_text_message(*wlog2_, current_product_, type, message, instance);
            }
        } else if (format_ == FMT_JSON) {
            if (log2_ != nullptr) {
                json_message(*log2_, current_product_, type, message, instance);
            } else if (wlog2_ != nullptr) {
                json_message(*wlog2_, current_product_, type, message, instance);
            }
        }
    }
}

void Logger::Message(Logger::Severity type, const std::exception& exception, const IfcUtil::IfcBaseInterface* instance) {
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
    if (log1_ != nullptr) {
        status(*log1_, message, new_line);
    } else if (wlog1_ != nullptr) {
        status(*wlog1_, message, new_line);
    }
}

void Logger::ProgressBar(int progress) {
    Status("\r[" + std::string(progress, '#') + std::string(50 - progress, ' ') + "]", false);
}

std::string Logger::GetLog() {
    return log_stream_.str();
}

void Logger::PrintPerformanceStats() {
    std::vector<std::pair<double, std::string>> items;
    for (auto& p : performance_statistics_) {
        items.push_back({p.second, p.first});
    }

    std::sort(items.begin(), items.end());
    std::reverse(items.begin(), items.end());

    size_t max_size = 0;
    for (auto& p : items) {
        if (p.second.size() > max_size) {
            max_size = p.second.size();
        }
    }

    for (auto& p : items) {
        auto s = p.second + std::string(max_size - p.second.size(), ' ') + ": " + std::to_string(p.first);
        Message(LOG_PERF, s);
    }
}

void Logger::Verbosity(Logger::Severity v) { verbosity_ = v; }
Logger::Severity Logger::Verbosity() { return verbosity_; }

Logger::Severity Logger::MaxSeverity() { return max_severity_; }

void Logger::OutputFormat(Format f) { format_ = f; }
Logger::Format Logger::OutputFormat() { return format_; }

std::ostream* Logger::log1_ = 0;
std::ostream* Logger::log2_ = 0;
std::wostream* Logger::wlog1_ = 0;
std::wostream* Logger::wlog2_ = 0;
std::stringstream Logger::log_stream_;
Logger::Severity Logger::verbosity_ = Logger::LOG_NOTICE;
Logger::Severity Logger::max_severity_ = Logger::LOG_NOTICE;
Logger::Format Logger::format_ = Logger::FMT_PLAIN;
boost::optional<IfcUtil::IfcBaseClass*> Logger::current_product_;
boost::optional<long long> Logger::first_timepoint_;
std::map<std::string, double> Logger::performance_statistics_;
std::map<std::string, double> Logger::performance_signal_start_;
bool Logger::print_perf_stats_on_element_ = false;
