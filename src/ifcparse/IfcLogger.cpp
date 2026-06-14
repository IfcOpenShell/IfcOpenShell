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
#include <cstdio>
#include <ctime>
#include <iomanip>
#include <iostream>

namespace {

std::string get_time(bool with_milliseconds = false) {
    std::ostringstream oss;
    time_t now = time(nullptr);
    oss << std::put_time(localtime(&now), "%F %T");

    if (with_milliseconds) {
        auto now_chrono = std::chrono::system_clock::now();
        auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(now_chrono.time_since_epoch()) % 1000;
        oss << '.' << std::setfill('0') << std::setw(3) << milliseconds.count();
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

std::string format_code(const char (&code_prefix)[4], uint16_t code_number) {
    std::ostringstream oss;
    oss << code_prefix[0] << code_prefix[1] << code_prefix[2] << std::setfill('0') << std::setw(3) << code_number;
    return oss.str();
}

template <typename T>
void plain_text_message(T& out, const IfcUtil::IfcBaseClass* current_product, Logger::Severity type, const std::string& code, const std::string& message, const IfcUtil::IfcBaseInterface* instance) {
    out << "[" << severity_strings<typename T::char_type>::value[type] << "] ";
    out << "[" << code.c_str() << "] ";
    out << "[" << get_time(type <= Logger::LOG_PERF).c_str() << "] ";
    if (current_product) {
        std::string global_id = current_product->as<IfcUtil::IfcBaseEntity>()->get("GlobalId");
        out << "{" << global_id.c_str() << "} ";
    }
    out << message.c_str() << std::endl;
    if (instance) {
        std::ostringstream oss;
        instance->as<IfcUtil::IfcBaseClass>()->toString(oss);
        auto instance_string = oss.str();
        if (instance_string.size() > 259) {
            instance_string = instance_string.substr(0, 256) + "...";
        }
        out << instance_string.c_str() << std::endl;
    }
}

template <typename T>
std::basic_string<T> string_as(const std::string& string) {
    std::basic_string<T> result;
    result.assign(string.begin(), string.end());
    return result;
}

template <typename T>
void json_message(T& out, const IfcUtil::IfcBaseClass* current_product, Logger::Severity type, const std::string& code, const std::string& message, const IfcUtil::IfcBaseInterface* instance) {
    boost::property_tree::basic_ptree<std::basic_string<typename T::char_type>, std::basic_string<typename T::char_type>> property_tree;

    // @todo this is crazy
    static const typename T::char_type time_string[] = {'t', 'i', 'm', 'e', 0};
    static const typename T::char_type level_string[] = {'l', 'e', 'v', 'e', 'l', 0};
    static const typename T::char_type code_string[] = {'c', 'o', 'd', 'e', 0};
    static const typename T::char_type product_string[] = {'p', 'r', 'o', 'd', 'u', 'c', 't', 0};
    static const typename T::char_type message_string[] = {'m', 'e', 's', 's', 'a', 'g', 'e', 0};
    static const typename T::char_type instance_string[] = {'i', 'n', 's', 't', 'a', 'n', 'c', 'e', 0};

    property_tree.put(level_string, severity_strings<typename T::char_type>::value[type]);
    property_tree.put(code_string, string_as<typename T::char_type>(code));
    if (current_product) {
        std::ostringstream oss;
        current_product->toString(oss);
        property_tree.put(product_string, string_as<typename T::char_type>(oss.str()));
    }
    property_tree.put(message_string, string_as<typename T::char_type>(message));
    if (instance) {
        std::ostringstream oss;
        instance->as<IfcUtil::IfcBaseClass>()->toString(oss);
        property_tree.put(instance_string, string_as<typename T::char_type>(oss.str()));
    }

    property_tree.put(time_string, string_as<typename T::char_type>(get_time()));

    boost::property_tree::write_json(out, property_tree, false);

    // Append a newline after the JSON object if the Boost version is 1.86 or higher
#if BOOST_VERSION >= 108600
    out << '\n';
#endif

}
} // namespace

log_message::log_message(
    int severity,
    const char (&code_prefix)[4],
    uint16_t code_number,
    const std::string& timestamp,
    const std::string& message,
    const IfcUtil::IfcBaseInterface* inst,
    const IfcUtil::IfcBaseClass* current_product)
    : severity(severity)
    , timestamp(timestamp)
    , message(message)
{
    snprintf(code, 7, "%s%03u", code_prefix, code_number);
    if (inst) {
        std::ostringstream oss;
        inst->as<IfcUtil::IfcBaseClass>()->toString(oss);
        instance = oss.str();
    }
    if (current_product) {
        std::ostringstream oss;
        current_product->toString(oss);
        product = oss.str();
    }
}

Logger& Logger::Root() {
    static Logger logger;
    return logger;
}

const IfcUtil::IfcBaseClass* Logger::current_product() const {
    return current_product_;
}

void Logger::current_product(const IfcUtil::IfcBaseClass* product) {
    current_product_ = product;
}

void Logger::SetProduct(boost::optional<const IfcUtil::IfcBaseClass*> product) {
    if (verbosity_ <= LOG_DEBUG && product) {
        Message(LOG_DEBUG, "SYS", 3, "Begin processing", *product);
    }
    if (!product && print_perf_stats_on_element_) {
        PrintPerformanceStats();
        performance_statistics_.clear();
    }
    current_product(product.get_value_or(nullptr));
}

void Logger::SetOutput(std::ostream* stream1, std::ostream* stream2) {
    wlog1_ = wlog2_ = 0;
    log1_ = stream1;
    log2_ = stream2;
    if (log2_ == nullptr) {
        log2_ = &log_stream_;
    }
}

void Logger::SetOutput(std::wostream* stream1, std::wostream* stream2) {
    log1_ = log2_ = 0;
    wlog1_ = stream1;
    wlog2_ = stream2;
    if (wlog2_ == nullptr) {
        log2_ = &log_stream_;
    }
}

void Logger::Message(Logger::Severity type, const char (&code_prefix)[4], uint16_t code_number, const std::string& message, const IfcUtil::IfcBaseInterface* instance) {
    if (type < verbosity_) {
        return;
    }

    std::lock_guard<std::mutex> lock(mutex_);
    const std::string code = format_code(code_prefix, code_number);

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

    if (format_ == FMT_INMEMORY) {
        log_messages_.emplace_back(type, code_prefix, code_number, get_time(), message, instance, current_product());
    } else if (((log2_ != nullptr) || (wlog2_ != nullptr))) {
        if (format_ == FMT_PLAIN) {
            if (log2_ != nullptr) {
                plain_text_message(*log2_, current_product(), type, code, message, instance);
            } else if (wlog2_ != nullptr) {
                plain_text_message(*wlog2_, current_product(), type, code, message, instance);
            }
        } else if (format_ == FMT_JSON) {
            if (log2_ != nullptr) {
                json_message(*log2_, current_product(), type, code, message, instance);
            } else if (wlog2_ != nullptr) {
                json_message(*wlog2_, current_product(), type, code, message, instance);
            }
        }
    }
}

void Logger::Message(Logger::Severity type, const char (&code_prefix)[4], uint16_t code_number, const std::exception& exception, const IfcUtil::IfcBaseInterface* instance) {
    Message(type, code_prefix, code_number, std::string(exception.what()), instance);
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
    std::lock_guard<std::mutex> lock(mutex_);
    return log_stream_.str();
}

void Logger::ClearLog() {
    std::lock_guard<std::mutex> lock(mutex_);
    log_stream_.str(std::string());
    log_stream_.clear();
    log_messages_.clear();
}

void Logger::Append(Logger& logger) {
    if (&logger == this) {
        return;
    }

    std::scoped_lock lock(mutex_, logger.mutex_);

    if (logger.max_severity_ > max_severity_) {
        max_severity_ = logger.max_severity_;
    }

    if (format_ == FMT_INMEMORY) {
        log_messages_.insert(log_messages_.end(), logger.log_messages_.begin(), logger.log_messages_.end());
    } else {
        const std::string log = logger.log_stream_.str();
        if (!log.empty()) {
            if (log2_ != nullptr) {
                *log2_ << log;
            } else if (wlog2_ != nullptr) {
                *wlog2_ << string_as<wchar_t>(log);
            } else {
                log_stream_ << log;
            }
        }
    }

    logger.log_stream_.str(std::string());
    logger.log_stream_.clear();
    logger.log_messages_.clear();
}

void Logger::PrintPerformanceStats() {
    std::vector<std::pair<double, std::string>> items;
    for (auto& stat : performance_statistics_) {
        items.push_back({stat.second, stat.first});
    }

    std::sort(items.begin(), items.end());
    std::reverse(items.begin(), items.end());

    size_t max_size = 0;
    for (auto& item : items) {
        if (item.second.size() > max_size) {
            max_size = item.second.size();
        }
    }

    for (auto& item : items) {
        auto message = item.second + std::string(max_size - item.second.size(), ' ') + ": " + std::to_string(item.first);
        Message(LOG_PERF, "SYS", 4, message);
    }
}

void Logger::Verbosity(Logger::Severity severity) { verbosity_ = severity; }
Logger::Severity Logger::Verbosity() const { return verbosity_; }

Logger::Severity Logger::MaxSeverity() const { return max_severity_; }

void Logger::OutputFormat(Format format) { format_ = format; }
Logger::Format Logger::OutputFormat() const { return format_; }
