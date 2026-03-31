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

#include "logger.h"

#include "argument.h"
#include "instance_data.h"

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

static thread_local express::Base current_product_;

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
const std::array<std::basic_string<char>, 5> severity_strings<char>::value = {"Performance", "Debug", "notice", "warning", "error"};

template <>
const std::array<std::basic_string<wchar_t>, 5> severity_strings<wchar_t>::value = {L"Performance", L"Debug", L"notice", L"warning", L"error"};

template <typename T>
void plain_text_message(T& out, const express::Base& current_product, logger::Severity type, const std::string& message, const express::Base& instance) {
    out << "[" << severity_strings<typename T::char_type>::value[type] << "] ";
    out << "[" << get_time(type <= logger::LOG_PERF).c_str() << "] ";
    if (current_product) {
        std::string global_id = current_product.as<express::Entity>().get("GlobalId");
        out << "{" << global_id.c_str() << "} ";
    }
    out << message.c_str() << std::endl;
    if (instance) {
        std::ostringstream oss;
        instance.to_string(oss);
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
void json_message(T& out, const express::Base& current_product, logger::Severity type, const std::string& message, const express::Base& instance) {
    boost::property_tree::basic_ptree<std::basic_string<typename T::char_type>, std::basic_string<typename T::char_type>> property_tree;

    // @todo this is crazy
    static const typename T::char_type time_string[] = {'t', 'i', 'm', 'e', 0};
    static const typename T::char_type level_string[] = {'l', 'e', 'v', 'e', 'l', 0};
    static const typename T::char_type product_string[] = {'p', 'r', 'o', 'd', 'u', 'c', 't', 0};
    static const typename T::char_type message_string[] = {'m', 'e', 's', 's', 'a', 'g', 'e', 0};
    static const typename T::char_type instance_string[] = {'i', 'n', 's', 't', 'a', 'n', 'c', 'e', 0};

    property_tree.put(level_string, severity_strings<typename T::char_type>::value[type]);
    if (current_product) {
        std::ostringstream oss;
        current_product.to_string(oss);
        property_tree.put(product_string, string_as<typename T::char_type>(oss.str()));
    }
    property_tree.put(message_string, string_as<typename T::char_type>(message));
    if (instance) {
        std::ostringstream oss;
        instance.to_string(oss);
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

void logger::set_product(std::optional<const express::Base> product) {
    if (verbosity_ <= LOG_DEBUG && product) {
        message(LOG_DEBUG, "Begin processing", *product);
    }
    if (!product && print_perf_stats_on_element_) {
        print_performance_stats();
        performance_statistics_.clear();
    }
    current_product_ = product.value_or(express::Base{});
}

void logger::set_output(std::ostream* stream1, std::ostream* stream2) {
    wlog1_ = wlog2_ = 0;
    log1_ = stream1;
    log2_ = stream2;
    if (log2_ == nullptr) {
        log2_ = &log_stream_;
    }
}

void logger::set_output(std::wostream* stream1, std::wostream* stream2) {
    log1_ = log2_ = 0;
    wlog1_ = stream1;
    wlog2_ = stream2;
    if (wlog2_ == nullptr) {
        log2_ = &log_stream_;
    }
}

void logger::message(logger::Severity type, const std::string& text, const express::Base& instance) {
    if (type < verbosity_) {
        return;
    }

    static std::mutex mtx;
    std::lock_guard<std::mutex> lock(mtx);

    if (type == LOG_PERF) {
        if (!first_timepoint_) {
            first_timepoint_ = std::chrono::time_point_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now()).time_since_epoch().count();
        }
        double t0 = (std::chrono::time_point_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now()).time_since_epoch().count() - *first_timepoint_) / 1.e9;
        if (text.substr(0, 5) == "done ") {
            auto orig = text.substr(5);
            performance_statistics_[orig] += t0 - performance_signal_start_[orig];
        } else {
            performance_signal_start_[text] = t0;
        }
    }

    if (type > max_severity_) {
        max_severity_ = type;
    }
    if (((log2_ != nullptr) || (wlog2_ != nullptr))) {
        if (format_ == FMT_PLAIN) {
            if (log2_ != nullptr) {
                plain_text_message(*log2_, current_product_, type, text, instance);
            } else if (wlog2_ != nullptr) {
                plain_text_message(*wlog2_, current_product_, type, text, instance);
            }
        } else if (format_ == FMT_JSON) {
            if (log2_ != nullptr) {
                json_message(*log2_, current_product_, type, text, instance);
            } else if (wlog2_ != nullptr) {
                json_message(*wlog2_, current_product_, type, text, instance);
            }
        }
    }
}

void logger::message(logger::Severity type, const std::exception& exception, const express::Base& instance) {
    message(type, std::string(exception.what()), instance);
}

template <typename T>
void write_status(T& log1, const std::string& text, bool new_line) {
    log1 << text.c_str();
    if (new_line) {
        log1 << std::endl;
    } else {
        log1 << std::flush;
    }
}

void logger::status(const std::string& message, bool new_line) {
    if (log1_ != nullptr) {
        write_status(*log1_, message, new_line);
    } else if (wlog1_ != nullptr) {
        write_status(*wlog1_, message, new_line);
    }
}

void logger::progress_bar(int progress) {
    status("\r[" + std::string(progress, '#') + std::string(50 - progress, ' ') + "]", false);
}

std::string logger::get_log() {
    return log_stream_.str();
}

void logger::print_performance_stats() {
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
        auto text = item.second + std::string(max_size - item.second.size(), ' ') + ": " + std::to_string(item.first);
        logger::message(LOG_PERF, text);
    }
}

void logger::verbosity(logger::Severity severity) { verbosity_ = severity; }
logger::Severity logger::verbosity() { return verbosity_; }

logger::Severity logger::max_severity() { return max_severity_; }

void logger::output_format(Format format) { format_ = format; }
logger::Format logger::output_format() { return format_; }

std::ostream* logger::log1_ = 0;
std::ostream* logger::log2_ = 0;
std::wostream* logger::wlog1_ = 0;
std::wostream* logger::wlog2_ = 0;
std::stringstream logger::log_stream_;
logger::Severity logger::verbosity_ = logger::LOG_NOTICE;
logger::Severity logger::max_severity_ = logger::LOG_NOTICE;
logger::Format logger::format_ = logger::FMT_PLAIN;
std::optional<long long> logger::first_timepoint_;
std::map<std::string, double> logger::performance_statistics_;
std::map<std::string, double> logger::performance_signal_start_;
bool logger::print_perf_stats_on_element_ = false;
